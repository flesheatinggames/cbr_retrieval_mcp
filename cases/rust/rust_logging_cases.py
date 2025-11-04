RUST_LOGGING_CASES = [
    {
        "problem": """
A structured logging system using tracing with multiple layers, filtering, and custom formatting.
""",
        "solution": """
use tracing::{debug, error, info, instrument, span, trace, warn, Level};
use tracing_subscriber::{
    fmt::{self, format::FmtSpan},
    layer::SubscriberExt,
    util::SubscriberInitExt,
    EnvFilter, Layer,
};
use std::time::Duration;

pub struct TracingConfig {
    pub log_level: String,
    pub json_format: bool,
    pub pretty_print: bool,
    pub log_file: Option<String>,
}

impl Default for TracingConfig {
    fn default() -> Self {
        Self {
            log_level: "info".to_string(),
            json_format: false,
            pretty_print: true,
            log_file: None,
        }
    }
}

pub fn init_tracing(config: TracingConfig) -> anyhow::Result<()> {
    let env_filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new(&config.log_level));

    let fmt_layer = if config.json_format {
        fmt::layer()
            .json()
            .with_current_span(true)
            .with_span_list(true)
            .with_target(true)
            .with_file(true)
            .with_line_number(true)
            .boxed()
    } else if config.pretty_print {
        fmt::layer()
            .pretty()
            .with_target(true)
            .with_file(true)
            .with_line_number(true)
            .with_thread_names(true)
            .with_span_events(FmtSpan::NEW | FmtSpan::CLOSE)
            .boxed()
    } else {
        fmt::layer()
            .compact()
            .with_target(true)
            .boxed()
    };

    let registry = tracing_subscriber::registry()
        .with(env_filter)
        .with(fmt_layer);

    if let Some(log_file) = config.log_file {
        let file = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(log_file)?;
        
        let file_layer = fmt::layer()
            .json()
            .with_writer(std::sync::Arc::new(file))
            .with_ansi(false);
        
        registry.with(file_layer).init();
    } else {
        registry.init();
    }

    Ok(())
}

#[derive(Debug)]
pub struct Request {
    pub id: String,
    pub method: String,
    pub path: String,
    pub user_id: Option<String>,
}

#[instrument(
    name = "handle_request",
    skip(req),
    fields(
        request_id = %req.id,
        method = %req.method,
        path = %req.path,
        user_id = ?req.user_id,
    )
)]
pub async fn handle_request(req: Request) -> Result<String, String> {
    info!("Processing request");
    
    // Create a span for authentication
    let auth_span = span!(Level::DEBUG, "authenticate");
    let _auth_guard = auth_span.enter();
    
    if let Some(user_id) = &req.user_id {
        debug!(%user_id, "User authenticated");
    } else {
        warn!("Anonymous request");
    }
    
    drop(_auth_guard);
    
    // Database query span
    let query_result = {
        let _span = span!(Level::DEBUG, "database_query", query = "SELECT * FROM items").entered();
        tokio::time::sleep(Duration::from_millis(100)).await;
        debug!("Query executed successfully");
        "data"
    };
    
    // Business logic span
    let result = {
        let _span = span!(Level::DEBUG, "business_logic").entered();
        trace!("Starting business logic");
        process_data(query_result).await?;
        "success"
    };
    
    info!(result = %result, "Request completed successfully");
    Ok(result.to_string())
}

#[instrument(skip(data))]
async fn process_data(data: &str) -> Result<(), String> {
    debug!(data_len = data.len(), "Processing data");
    tokio::time::sleep(Duration::from_millis(50)).await;
    Ok(())
}

// Custom log fields using structured fields
pub struct MetricsCollector {
    request_count: std::sync::Arc<std::sync::atomic::AtomicU64>,
    error_count: std::sync::Arc<std::sync::atomic::AtomicU64>,
}

impl MetricsCollector {
    pub fn new() -> Self {
        Self {
            request_count: std::sync::Arc::new(std::sync::atomic::AtomicU64::new(0)),
            error_count: std::sync::Arc::new(std::sync::atomic::AtomicU64::new(0)),
        }
    }

    #[instrument(skip(self))]
    pub fn record_request(&self, duration_ms: u64, status: u16) {
        self.request_count.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        
        if status >= 400 {
            self.error_count.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
            warn!(
                status = status,
                duration_ms = duration_ms,
                "Request failed"
            );
        } else {
            info!(
                status = status,
                duration_ms = duration_ms,
                "Request successful"
            );
        }
    }

    pub fn get_stats(&self) -> (u64, u64) {
        (
            self.request_count.load(std::sync::atomic::Ordering::Relaxed),
            self.error_count.load(std::sync::atomic::Ordering::Relaxed),
        )
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    init_tracing(TracingConfig {
        log_level: "debug".to_string(),
        json_format: false,
        pretty_print: true,
        log_file: Some("app.log".to_string()),
    })?;

    info!("Application started");

    let metrics = MetricsCollector::new();

    // Simulate requests
    for i in 0..5 {
        let req = Request {
            id: format!("req-{}", i),
            method: "GET".to_string(),
            path: "/api/items".to_string(),
            user_id: Some(format!("user-{}", i)),
        };

        let start = std::time::Instant::now();
        match handle_request(req).await {
            Ok(_) => {
                let duration = start.elapsed().as_millis() as u64;
                metrics.record_request(duration, 200);
            }
            Err(e) => {
                error!(error = %e, "Request failed");
                let duration = start.elapsed().as_millis() as u64;
                metrics.record_request(duration, 500);
            }
        }
    }

    let (total, errors) = metrics.get_stats();
    info!(
        total_requests = total,
        total_errors = errors,
        success_rate = format!("{:.2}%", ((total - errors) as f64 / total as f64) * 100.0),
        "Final statistics"
    );

    Ok(())
}
""",
        "category": "rust",
        "subcategory": "logging",
        "tags": [
            "api",
            "async",
            "auth",
            "authentication",
            "database",
            "event",
            "filter",
        ],
    }
]
