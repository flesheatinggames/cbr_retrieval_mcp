
RUST_TOWER_CASES = [
    {
        "problem": """
Building composable middleware layers using Tower for service abstraction.
""",
        "solution": """
use tower::{Service, ServiceBuilder, ServiceExt, Layer};
use tower::limit::RateLimitLayer;
use tower::timeout::TimeoutLayer;
use tower::buffer::BufferLayer;
use std::time::Duration;
use std::task::{Context, Poll};
use std::pin::Pin;
use futures::Future;

// Custom middleware for request logging
#[derive(Clone)]
pub struct LoggingLayer;

impl<S> Layer<S> for LoggingLayer {
    type Service = LoggingService<S>;

    fn layer(&self, service: S) -> Self::Service {
        LoggingService { inner: service }
    }
}

#[derive(Clone)]
pub struct LoggingService<S> {
    inner: S,
}

impl<S, Request> Service<Request> for LoggingService<S>
where
    S: Service<Request>,
    Request: std::fmt::Debug,
{
    type Response = S::Response;
    type Error = S::Error;
    type Future = Pin<Box<dyn Future<Output = Result<Self::Response, Self::Error>> + Send>>;

    fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        self.inner.poll_ready(cx)
    }

    fn call(&mut self, request: Request) -> Self::Future {
        println!("Processing request: {:?}", request);
        let start = std::time::Instant::now();
        let future = self.inner.call(request);

        Box::pin(async move {
            let result = future.await;
            let elapsed = start.elapsed();
            println!("Request completed in {:?}", elapsed);
            result
        })
    }
}

// Custom middleware for authentication
#[derive(Clone)]
pub struct AuthLayer {
    valid_tokens: Vec<String>,
}

impl AuthLayer {
    pub fn new(valid_tokens: Vec<String>) -> Self {
        Self { valid_tokens }
    }
}

impl<S> Layer<S> for AuthLayer {
    type Service = AuthService<S>;

    fn layer(&self, service: S) -> Self::Service {
        AuthService {
            inner: service,
            valid_tokens: self.valid_tokens.clone(),
        }
    }
}

#[derive(Clone)]
pub struct AuthService<S> {
    inner: S,
    valid_tokens: Vec<String>,
}

#[derive(Debug)]
pub struct AuthenticatedRequest<T> {
    pub user_id: String,
    pub inner: T,
}

impl<S, Request> Service<Request> for AuthService<S>
where
    S: Service<AuthenticatedRequest<Request>>,
    Request: HasToken,
{
    type Response = S::Response;
    type Error = S::Error;
    type Future = S::Future;

    fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        self.inner.poll_ready(cx)
    }

    fn call(&mut self, request: Request) -> Self::Future {
        let token = request.token();
        
        // Validate token
        let user_id = if self.valid_tokens.contains(&token.to_string()) {
            format!("user_{}", token)
        } else {
            "anonymous".to_string()
        };

        let authenticated = AuthenticatedRequest {
            user_id,
            inner: request,
        };

        self.inner.call(authenticated)
    }
}

pub trait HasToken {
    fn token(&self) -> &str;
}

// Example request type
#[derive(Debug, Clone)]
pub struct HttpRequest {
    pub path: String,
    pub token: String,
}

impl HasToken for HttpRequest {
    fn token(&self) -> &str {
        &self.token
    }
}

// Simple echo service
#[derive(Clone)]
pub struct EchoService;

impl<T: std::fmt::Debug> Service<T> for EchoService {
    type Response = String;
    type Error = Box<dyn std::error::Error + Send + Sync>;
    type Future = Pin<Box<dyn Future<Output = Result<Self::Response, Self::Error>> + Send>>;

    fn poll_ready(&mut self, _cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        Poll::Ready(Ok(()))
    }

    fn call(&mut self, request: T) -> Self::Future {
        let response = format!("Echo: {:?}", request);
        Box::pin(async move { Ok(response) })
    }
}

// Building a service with multiple middleware layers
pub async fn build_service() {
    let service = ServiceBuilder::new()
        // Add timeout layer
        .layer(TimeoutLayer::new(Duration::from_secs(30)))
        // Add rate limiting
        .layer(RateLimitLayer::new(5, Duration::from_secs(1)))
        // Add buffering
        .layer(BufferLayer::new(100))
        // Add custom logging
        .layer(LoggingLayer)
        // Add custom auth
        .layer(AuthLayer::new(vec!["valid_token".to_string()]))
        // Build the service
        .service(EchoService);

    // Use the service
    let mut service = service;
    
    let request = HttpRequest {
        path: "/api/users".to_string(),
        token: "valid_token".to_string(),
    };

    match service.ready().await {
        Ok(svc) => {
            match svc.call(request).await {
                Ok(response) => println!("Response: {}", response),
                Err(e) => println!("Error: {}", e),
            }
        }
        Err(e) => println!("Service not ready: {}", e),
    }
}

// Retry middleware
#[derive(Clone)]
pub struct RetryLayer {
    max_retries: usize,
}

impl RetryLayer {
    pub fn new(max_retries: usize) -> Self {
        Self { max_retries }
    }
}

impl<S> Layer<S> for RetryLayer {
    type Service = RetryService<S>;

    fn layer(&self, service: S) -> Self::Service {
        RetryService {
            inner: service,
            max_retries: self.max_retries,
        }
    }
}

#[derive(Clone)]
pub struct RetryService<S> {
    inner: S,
    max_retries: usize,
}

impl<S, Request> Service<Request> for RetryService<S>
where
    S: Service<Request> + Clone,
    Request: Clone,
{
    type Response = S::Response;
    type Error = S::Error;
    type Future = Pin<Box<dyn Future<Output = Result<Self::Response, Self::Error>> + Send>>;

    fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        self.inner.poll_ready(cx)
    }

    fn call(&mut self, request: Request) -> Self::Future {
        let mut service = self.inner.clone();
        let max_retries = self.max_retries;

        Box::pin(async move {
            let mut attempts = 0;
            loop {
                let req = request.clone();
                match service.call(req).await {
                    Ok(response) => return Ok(response),
                    Err(e) => {
                        attempts += 1;
                        if attempts >= max_retries {
                            return Err(e);
                        }
                        println!("Retry attempt {}/{}", attempts, max_retries);
                        tokio::time::sleep(Duration::from_millis(100 * attempts as u64)).await;
                    }
                }
            }
        })
    }
}

#[tokio::main]
async fn main() {
    build_service().await;
}
""",
        "category": 'rust',
        "subcategory": 'tower',
        "tags": ['api', 'async', 'auth', 'authentication', 'form', 'http', 'logging']
    }
]
