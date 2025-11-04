"""
},
{
    "problem": "An Axum REST API with CRUD operations, pagination, and input validation using validator crate.",
    "solution":"""

RUST_AXUM_CASES = [
    {
        "problem": """
An Axum web server with authentication middleware, error handling, and database connection pooling.
""",
        "solution": """
use axum::{
    async_trait,
    extract::{FromRef, FromRequestParts, State},
    http::{request::Parts, StatusCode},
    middleware::{self, Next},
    response::{IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use sqlx::{PgPool, postgres::PgPoolOptions};
use std::sync::Arc;
use tokio::net::TcpListener;
use tower::ServiceBuilder;
use tower_http::{
    cors::{Any, CorsLayer},
    trace::TraceLayer,
};
use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, Validation};

// Application state
#[derive(Clone)]
pub struct AppState {
    pub db: PgPool,
    pub jwt_secret: Arc<String>,
}

impl FromRef<AppState> for PgPool {
    fn from_ref(state: &AppState) -> Self {
        state.db.clone()
    }
}

// JWT Claims
#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,  // user id
    pub exp: usize,   // expiration time
    pub iat: usize,   // issued at
}

// Auth extractor
pub struct AuthUser {
    pub user_id: String,
}

#[async_trait]
impl<S> FromRequestParts<S> for AuthUser
where
    AppState: FromRef<S>,
    S: Send + Sync,
{
    type Rejection = AuthError;

    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
        let state = AppState::from_ref(state);
        
        // Extract token from Authorization header
        let auth_header = parts
            .headers
            .get("Authorization")
            .and_then(|h| h.to_str().ok())
            .ok_or(AuthError::MissingToken)?;

        let token = auth_header
            .strip_prefix("Bearer ")
            .ok_or(AuthError::InvalidToken)?;

        // Decode and validate JWT
        let token_data = decode::<Claims>(
            token,
            &DecodingKey::from_secret(state.jwt_secret.as_bytes()),
            &Validation::default(),
        )
        .map_err(|_| AuthError::InvalidToken)?;

        Ok(AuthUser {
            user_id: token_data.claims.sub,
        })
    }
}

// Error types
#[derive(Debug)]
pub enum AuthError {
    MissingToken,
    InvalidToken,
}

impl IntoResponse for AuthError {
    fn into_response(self) -> Response {
        let (status, message) = match self {
            AuthError::MissingToken => (StatusCode::UNAUTHORIZED, "Missing authentication token"),
            AuthError::InvalidToken => (StatusCode::UNAUTHORIZED, "Invalid authentication token"),
        };
        (status, Json(serde_json::json!({ "error": message }))).into_response()
    }
}

#[derive(Debug)]
pub enum AppError {
    Database(sqlx::Error),
    NotFound,
    Unauthorized,
    BadRequest(String),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, message) = match self {
            AppError::Database(e) => {
                tracing::error!("Database error: {:?}", e);
                (StatusCode::INTERNAL_SERVER_ERROR, "Database error".to_string())
            }
            AppError::NotFound => (StatusCode::NOT_FOUND, "Resource not found".to_string()),
            AppError::Unauthorized => (StatusCode::UNAUTHORIZED, "Unauthorized".to_string()),
            AppError::BadRequest(msg) => (StatusCode::BAD_REQUEST, msg),
        };
        (status, Json(serde_json::json!({ "error": message }))).into_response()
    }
}

impl From<sqlx::Error> for AppError {
    fn from(err: sqlx::Error) -> Self {
        AppError::Database(err)
    }
}

// DTOs
#[derive(Debug, Deserialize)]
pub struct LoginRequest {
    pub email: String,
    pub password: String,
}

#[derive(Debug, Serialize)]
pub struct LoginResponse {
    pub token: String,
    pub user_id: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct User {
    pub id: String,
    pub email: String,
    pub name: String,
}

// Handlers
pub async fn login_handler(
    State(state): State<AppState>,
    Json(payload): Json<LoginRequest>,
) -> Result<Json<LoginResponse>, AppError> {
    // Validate credentials (simplified for example)
    let user = sqlx::query_as!(
        User,
        r#"
        SELECT id, email, name
        FROM users
        WHERE email = $1
        LIMIT 1
        "#,
        payload.email
    )
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::Unauthorized)?;

    // In production, verify password hash here
    // For example: verify_password(&payload.password, &user.password_hash)?;

    // Generate JWT
    let now = chrono::Utc::now();
    let claims = Claims {
        sub: user.id.clone(),
        exp: (now + chrono::Duration::hours(24)).timestamp() as usize,
        iat: now.timestamp() as usize,
    };

    let token = encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(state.jwt_secret.as_bytes()),
    )
    .map_err(|_| AppError::BadRequest("Failed to generate token".to_string()))?;

    Ok(Json(LoginResponse {
        token,
        user_id: user.id,
    }))
}

pub async fn get_profile_handler(
    auth_user: AuthUser,
    State(state): State<AppState>,
) -> Result<Json<User>, AppError> {
    let user = sqlx::query_as!(
        User,
        r#"
        SELECT id, email, name
        FROM users
        WHERE id = $1
        "#,
        auth_user.user_id
    )
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::NotFound)?;

    Ok(Json(user))
}

pub async fn health_check() -> impl IntoResponse {
    Json(serde_json::json!({
        "status": "healthy",
        "timestamp": chrono::Utc::now().to_rfc3339()
    }))
}

// Logging middleware
pub async fn logging_middleware(
    req: axum::extract::Request,
    next: Next,
) -> Response {
    let method = req.method().clone();
    let uri = req.uri().clone();
    let start = std::time::Instant::now();
    
    let response = next.run(req).await;
    
    let duration = start.elapsed();
    tracing::info!(
        "{} {} - {} ({:?})",
        method,
        uri,
        response.status(),
        duration
    );
    
    response
}

// Main application
pub async fn create_app(db_url: &str, jwt_secret: String) -> anyhow::Result<Router> {
    // Create database connection pool
    let db = PgPoolOptions::new()
        .max_connections(5)
        .connect(db_url)
        .await?;

    // Run migrations
    sqlx::migrate!("./migrations")
        .run(&db)
        .await?;

    let state = AppState {
        db,
        jwt_secret: Arc::new(jwt_secret),
    };

    // Configure CORS
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    // Build router
    let app = Router::new()
        .route("/health", get(health_check))
        .route("/api/login", post(login_handler))
        .route("/api/profile", get(get_profile_handler))
        .layer(
            ServiceBuilder::new()
                .layer(TraceLayer::new_for_http())
                .layer(middleware::from_fn(logging_middleware))
                .layer(cors)
        )
        .with_state(state);

    Ok(app)
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_target(false)
        .compact()
        .init();

    let database_url = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "postgres://localhost/myapp".to_string());
    let jwt_secret = std::env::var("JWT_SECRET")
        .unwrap_or_else(|_| "your-secret-key".to_string());

    let app = create_app(&database_url, jwt_secret).await?;

    let listener = TcpListener::bind("0.0.0.0:3000").await?;
    tracing::info!("Server starting on {}", listener.local_addr()?);

    axum::serve(listener, app).await?;

    Ok(())
}
""",
        "category": "rust",
        "subcategory": "axum",
        "tags": [
            "api",
            "async",
            "auth",
            "authentication",
            "authorization",
            "axum",
            "database",
        ],
    },
    {
        "problem": """
An Axum REST API with CRUD operations, pagination, and input validation using validator crate.
""",
        "solution": """
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{delete, get, post, put},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use sqlx::{FromRow, PgPool};
use validator::Validate;

// Models
#[derive(Debug, Serialize, FromRow)]
pub struct Article {
    pub id: i32,
    pub title: String,
    pub content: String,
    pub author_id: String,
    pub published: bool,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Deserialize, Validate)]
pub struct CreateArticleRequest {
    #[validate(length(min = 3, max = 200, message = "Title must be between 3 and 200 characters"))]
    pub title: String,
    
    #[validate(length(min = 10, message = "Content must be at least 10 characters"))]
    pub content: String,
    
    pub published: Option<bool>,
}

#[derive(Debug, Deserialize, Validate)]
pub struct UpdateArticleRequest {
    #[validate(length(min = 3, max = 200, message = "Title must be between 3 and 200 characters"))]
    pub title: Option<String>,
    
    #[validate(length(min = 10, message = "Content must be at least 10 characters"))]
    pub content: Option<String>,
    
    pub published: Option<bool>,
}

#[derive(Debug, Deserialize)]
pub struct PaginationParams {
    #[serde(default = "default_page")]
    pub page: i64,
    
    #[serde(default = "default_page_size")]
    pub page_size: i64,
    
    pub search: Option<String>,
}

fn default_page() -> i64 { 1 }
fn default_page_size() -> i64 { 10 }

#[derive(Debug, Serialize)]
pub struct PaginatedResponse<T> {
    pub items: Vec<T>,
    pub total: i64,
    pub page: i64,
    pub page_size: i64,
    pub total_pages: i64,
}

// Error handling
#[derive(Debug)]
pub enum ApiError {
    Database(sqlx::Error),
    NotFound,
    ValidationError(String),
}

impl IntoResponse for ApiError {
    fn into_response(self) -> axum::response::Response {
        let (status, message) = match self {
            ApiError::Database(e) => {
                tracing::error!("Database error: {:?}", e);
                (StatusCode::INTERNAL_SERVER_ERROR, "Database error occurred".to_string())
            }
            ApiError::NotFound => (StatusCode::NOT_FOUND, "Resource not found".to_string()),
            ApiError::ValidationError(msg) => (StatusCode::BAD_REQUEST, msg),
        };
        
        (status, Json(serde_json::json!({ "error": message }))).into_response()
    }
}

impl From<sqlx::Error> for ApiError {
    fn from(err: sqlx::Error) -> Self {
        ApiError::Database(err)
    }
}

// Handlers
pub async fn create_article(
    State(pool): State<PgPool>,
    auth_user: crate::AuthUser,
    Json(payload): Json<CreateArticleRequest>,
) -> Result<(StatusCode, Json<Article>), ApiError> {
    // Validate input
    payload.validate()
        .map_err(|e| ApiError::ValidationError(e.to_string()))?;

    let article = sqlx::query_as!(
        Article,
        r#"
        INSERT INTO articles (title, content, author_id, published)
        VALUES ($1, $2, $3, $4)
        RETURNING id, title, content, author_id, published, created_at, updated_at
        "#,
        payload.title,
        payload.content,
        auth_user.user_id,
        payload.published.unwrap_or(false)
    )
    .fetch_one(&pool)
    .await?;

    Ok((StatusCode::CREATED, Json(article)))
}

pub async fn get_articles(
    State(pool): State<PgPool>,
    Query(params): Query<PaginationParams>,
) -> Result<Json<PaginatedResponse<Article>>, ApiError> {
    let offset = (params.page - 1) * params.page_size;
    
    // Build dynamic query based on search parameter
    let (items, total) = if let Some(search_term) = params.search {
        let search_pattern = format!("%{}%", search_term);
        
        let items = sqlx::query_as!(
            Article,
            r#"
            SELECT id, title, content, author_id, published, created_at, updated_at
            FROM articles
            WHERE title ILIKE $1 OR content ILIKE $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            "#,
            search_pattern,
            params.page_size,
            offset
        )
        .fetch_all(&pool)
        .await?;

        let count_result = sqlx::query!(
            "SELECT COUNT(*) as count FROM articles WHERE title ILIKE $1 OR content ILIKE $1",
            search_pattern
        )
        .fetch_one(&pool)
        .await?;

        (items, count_result.count.unwrap_or(0))
    } else {
        let items = sqlx::query_as!(
            Article,
            r#"
            SELECT id, title, content, author_id, published, created_at, updated_at
            FROM articles
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
            "#,
            params.page_size,
            offset
        )
        .fetch_all(&pool)
        .await?;

        let count_result = sqlx::query!("SELECT COUNT(*) as count FROM articles")
            .fetch_one(&pool)
            .await?;

        (items, count_result.count.unwrap_or(0))
    };

    let total_pages = (total as f64 / params.page_size as f64).ceil() as i64;

    Ok(Json(PaginatedResponse {
        items,
        total,
        page: params.page,
        page_size: params.page_size,
        total_pages,
    }))
}

pub async fn get_article(
    State(pool): State<PgPool>,
    Path(id): Path<i32>,
) -> Result<Json<Article>, ApiError> {
    let article = sqlx::query_as!(
        Article,
        r#"
        SELECT id, title, content, author_id, published, created_at, updated_at
        FROM articles
        WHERE id = $1
        "#,
        id
    )
    .fetch_optional(&pool)
    .await?
    .ok_or(ApiError::NotFound)?;

    Ok(Json(article))
}

pub async fn update_article(
    State(pool): State<PgPool>,
    auth_user: crate::AuthUser,
    Path(id): Path<i32>,
    Json(payload): Json<UpdateArticleRequest>,
) -> Result<Json<Article>, ApiError> {
    // Validate input
    payload.validate()
        .map_err(|e| ApiError::ValidationError(e.to_string()))?;

    // Check if article exists and user owns it
    let existing = sqlx::query!("SELECT author_id FROM articles WHERE id = $1", id)
        .fetch_optional(&pool)
        .await?
        .ok_or(ApiError::NotFound)?;

    if existing.author_id != auth_user.user_id {
        return Err(ApiError::ValidationError("Unauthorized to update this article".to_string()));
    }

    // Build update query dynamically
    let article = sqlx::query_as!(
        Article,
        r#"
        UPDATE articles
        SET 
            title = COALESCE($1, title),
            content = COALESCE($2, content),
            published = COALESCE($3, published),
            updated_at = NOW()
        WHERE id = $4
        RETURNING id, title, content, author_id, published, created_at, updated_at
        "#,
        payload.title,
        payload.content,
        payload.published,
        id
    )
    .fetch_one(&pool)
    .await?;

    Ok(Json(article))
}

pub async fn delete_article(
    State(pool): State<PgPool>,
    auth_user: crate::AuthUser,
    Path(id): Path<i32>,
) -> Result<StatusCode, ApiError> {
    // Check if article exists and user owns it
    let existing = sqlx::query!("SELECT author_id FROM articles WHERE id = $1", id)
        .fetch_optional(&pool)
        .await?
        .ok_or(ApiError::NotFound)?;

    if existing.author_id != auth_user.user_id {
        return Err(ApiError::ValidationError("Unauthorized to delete this article".to_string()));
    }

    sqlx::query!("DELETE FROM articles WHERE id = $1", id)
        .execute(&pool)
        .await?;

    Ok(StatusCode::NO_CONTENT)
}

// Router configuration
pub fn articles_router() -> Router<PgPool> {
    Router::new()
        .route("/articles", post(create_article).get(get_articles))
        .route("/articles/:id", get(get_article).put(update_article).delete(delete_article))
}
""",
        "category": "rust",
        "subcategory": "axum",
        "tags": ["api", "async", "auth", "axum", "crud", "database", "error-handling"],
    },
]
