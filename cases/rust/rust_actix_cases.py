RUST_ACTIX_CASES = [
    {
        "problem": """
An Actix-web application with middleware, state management, WebSockets, and SSE support.
""",
        "solution": """
use actix_web::{
    get, post, web, App, Error, HttpRequest, HttpResponse, HttpServer, Responder,
    middleware::{Logger, NormalizePath},
};
use actix_web_actors::ws;
use actix::{Actor, StreamHandler, AsyncContext, ActorContext};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

// Application state
#[derive(Clone)]
pub struct AppState {
    pub db: sqlx::PgPool,
    pub connections: Arc<Mutex<Vec<String>>>,
}

// Request/Response DTOs
#[derive(Debug, Deserialize)]
pub struct CreateItemRequest {
    pub name: String,
    pub description: String,
    pub price: f64,
}

#[derive(Debug, Serialize, sqlx::FromRow)]
pub struct Item {
    pub id: i32,
    pub name: String,
    pub description: String,
    pub price: f64,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Serialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<String>,
}

impl<T: Serialize> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
        }
    }

    pub fn error(message: impl Into<String>) -> ApiResponse<()> {
        ApiResponse {
            success: false,
            data: None,
            error: Some(message.into()),
        }
    }
}

// WebSocket actor
pub struct WsConnection {
    id: String,
    hb: Instant,
}

impl WsConnection {
    pub fn new(id: String) -> Self {
        Self {
            id,
            hb: Instant::now(),
        }
    }

    fn hb(&self, ctx: &mut ws::WebsocketContext<Self>) {
        ctx.run_interval(Duration::from_secs(5), |act, ctx| {
            if Instant::now().duration_since(act.hb) > Duration::from_secs(10) {
                tracing::warn!("WebSocket heartbeat failed, disconnecting");
                ctx.stop();
                return;
            }
            ctx.ping(b"");
        });
    }
}

impl Actor for WsConnection {
    type Context = ws::WebsocketContext<Self>;

    fn started(&mut self, ctx: &mut Self::Context) {
        tracing::info!(connection_id = %self.id, "WebSocket connection started");
        self.hb(ctx);
    }

    fn stopped(&mut self, _ctx: &mut Self::Context) {
        tracing::info!(connection_id = %self.id, "WebSocket connection stopped");
    }
}

impl StreamHandler<Result<ws::Message, ws::ProtocolError>> for WsConnection {
    fn handle(&mut self, msg: Result<ws::Message, ws::ProtocolError>, ctx: &mut Self::Context) {
        match msg {
            Ok(ws::Message::Ping(msg)) => {
                self.hb = Instant::now();
                ctx.pong(&msg);
            }
            Ok(ws::Message::Pong(_)) => {
                self.hb = Instant::now();
            }
            Ok(ws::Message::Text(text)) => {
                tracing::debug!(message = %text, "Received text message");
                ctx.text(format!("Echo: {}", text));
            }
            Ok(ws::Message::Binary(bin)) => ctx.binary(bin),
            Ok(ws::Message::Close(reason)) => {
                tracing::info!(?reason, "WebSocket close requested");
                ctx.close(reason);
                ctx.stop();
            }
            _ => (),
        }
    }
}

// Route handlers
#[get("/health")]
async fn health_check() -> impl Responder {
    HttpResponse::Ok().json(serde_json::json!({
        "status": "healthy",
        "timestamp": chrono::Utc::now().to_rfc3339()
    }))
}

#[get("/items")]
async fn get_items(
    state: web::Data<AppState>,
    query: web::Query<PaginationQuery>,
) -> Result<HttpResponse, Error> {
    let items = sqlx::query_as!(
        Item,
        "SELECT id, name, description, price, created_at 
         FROM items 
         ORDER BY created_at DESC 
         LIMIT $1 OFFSET $2",
        query.limit.unwrap_or(10) as i64,
        query.offset.unwrap_or(0) as i64
    )
    .fetch_all(&state.db)
    .await
    .map_err(|e| {
        tracing::error!(error = %e, "Failed to fetch items");
        actix_web::error::ErrorInternalServerError("Database error")
    })?;

    Ok(HttpResponse::Ok().json(ApiResponse::success(items)))
}

#[get("/items/{id}")]
async fn get_item(
    state: web::Data<AppState>,
    path: web::Path<i32>,
) -> Result<HttpResponse, Error> {
    let id = path.into_inner();

    let item = sqlx::query_as!(
        Item,
        "SELECT id, name, description, price, created_at FROM items WHERE id = $1",
        id
    )
    .fetch_optional(&state.db)
    .await
    .map_err(|e| {
        tracing::error!(error = %e, item_id = id, "Failed to fetch item");
        actix_web::error::ErrorInternalServerError("Database error")
    })?;

    match item {
        Some(item) => Ok(HttpResponse::Ok().json(ApiResponse::success(item))),
        None => Ok(HttpResponse::NotFound().json(ApiResponse::<()>::error("Item not found"))),
    }
}

#[post("/items")]
async fn create_item(
    state: web::Data<AppState>,
    body: web::Json<CreateItemRequest>,
) -> Result<HttpResponse, Error> {
    let item = sqlx::query_as!(
        Item,
        "INSERT INTO items (name, description, price) VALUES ($1, $2, $3) 
         RETURNING id, name, description, price, created_at",
        body.name,
        body.description,
        body.price
    )
    .fetch_one(&state.db)
    .await
    .map_err(|e| {
        tracing::error!(error = %e, "Failed to create item");
        actix_web::error::ErrorInternalServerError("Database error")
    })?;

    Ok(HttpResponse::Created().json(ApiResponse::success(item)))
}

#[derive(Deserialize)]
struct PaginationQuery {
    limit: Option<i32>,
    offset: Option<i32>,
}

// WebSocket endpoint
#[get("/ws")]
async fn websocket(
    req: HttpRequest,
    stream: web::Payload,
    state: web::Data<AppState>,
) -> Result<HttpResponse, Error> {
    let conn_id = uuid::Uuid::new_v4().to_string();
    
    state.connections.lock().unwrap().push(conn_id.clone());

    let ws = WsConnection::new(conn_id);
    ws::start(ws, &req, stream)
}

// Server-Sent Events endpoint
#[get("/events")]
async fn events() -> impl Responder {
    use actix_web::body::BodyStream;
    use futures::stream;
    use std::pin::Pin;

    let stream = stream::unfold(0, |state| async move {
        tokio::time::sleep(Duration::from_secs(1)).await;
        let message = format!("data: {{"count": {}, "timestamp": "{}"}}

", 
            state, 
            chrono::Utc::now().to_rfc3339()
        );
        Some((Ok::<_, actix_web::Error>(web::Bytes::from(message)), state + 1))
    });

    HttpResponse::Ok()
        .content_type("text/event-stream")
        .append_header(("Cache-Control", "no-cache"))
        .append_header(("X-Accel-Buffering", "no"))
        .streaming(BodyStream::new(stream))
}

// Custom middleware for request timing
pub struct RequestTimer;

impl<S, B> actix_web::dev::Transform<S, actix_web::dev::ServiceRequest> for RequestTimer
where
    S: actix_web::dev::Service<
        actix_web::dev::ServiceRequest,
        Response = actix_web::dev::ServiceResponse<B>,
        Error = Error,
    >,
    S::Future: 'static,
    B: 'static,
{
    type Response = actix_web::dev::ServiceResponse<B>;
    type Error = Error;
    type Transform = RequestTimerMiddleware<S>;
    type InitError = ();
    type Future = std::future::Ready<Result<Self::Transform, Self::InitError>>;

    fn new_transform(&self, service: S) -> Self::Future {
        std::future::ready(Ok(RequestTimerMiddleware { service }))
    }
}

pub struct RequestTimerMiddleware<S> {
    service: S,
}

impl<S, B> actix_web::dev::Service<actix_web::dev::ServiceRequest> for RequestTimerMiddleware<S>
where
    S: actix_web::dev::Service<
        actix_web::dev::ServiceRequest,
        Response = actix_web::dev::ServiceResponse<B>,
        Error = Error,
    >,
    S::Future: 'static,
    B: 'static,
{
    type Response = actix_web::dev::ServiceResponse<B>;
    type Error = Error;
    type Future = Pin<Box<dyn std::future::Future<Output = Result<Self::Response, Self::Error>>>>;

    actix_web::dev::forward_ready!(service);

    fn call(&self, req: actix_web::dev::ServiceRequest) -> Self::Future {
        let start = Instant::now();
        let path = req.path().to_owned();
        let method = req.method().to_string();
        
        let fut = self.service.call(req);

        Box::pin(async move {
            let res = fut.await?;
            let duration = start.elapsed();
            
            tracing::info!(
                method = %method,
                path = %path,
                status = %res.status(),
                duration_ms = duration.as_millis(),
                "Request completed"
            );
            
            Ok(res)
        })
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    tracing_subscriber::fmt::init();

    let database_url = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "postgres://localhost/mydb".to_string());

    let pool = sqlx::postgres::PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await
        .expect("Failed to create pool");

    let state = AppState {
        db: pool,
        connections: Arc::new(Mutex::new(Vec::new())),
    };

    tracing::info!("Starting server on 127.0.0.1:8080");

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(state.clone()))
            .wrap(Logger::default())
            .wrap(NormalizePath::trim())
            .wrap(RequestTimer)
            .service(health_check)
            .service(get_items)
            .service(get_item)
            .service(create_item)
            .service(websocket)
            .service(events)
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}
""",
        "category": "rust",
        "subcategory": "actix",
        "tags": ["actix", "api", "async", "database", "event", "form", "handler"],
    }
]
