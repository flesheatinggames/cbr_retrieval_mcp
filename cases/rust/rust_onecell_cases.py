
RUST_ONECELL_CASES = [
    {
        "problem": """
Lazy static initialization and one-time initialization using once_cell.
""",
        "solution": """
use once_cell::sync::{Lazy, OnceCell};
use std::sync::Mutex;
use std::collections::HashMap;

// Lazy static configuration
static CONFIG: Lazy<AppConfig> = Lazy::new(|| {
    println!("Initializing configuration...");
    AppConfig {
        api_key: std::env::var("API_KEY").unwrap_or_else(|_| "default_key".to_string()),
        max_connections: 100,
        timeout_ms: 30000,
    }
});

#[derive(Debug)]
struct AppConfig {
    api_key: String,
    max_connections: usize,
    timeout_ms: u64,
}

// Lazy database pool
static DB_POOL: Lazy<Mutex<DatabasePool>> = Lazy::new(|| {
    println!("Creating database pool...");
    Mutex::new(DatabasePool::new(10))
});

struct DatabasePool {
    size: usize,
    connections: Vec<String>,
}

impl DatabasePool {
    fn new(size: usize) -> Self {
        Self {
            size,
            connections: (0..size).map(|i| format!("conn_{}", i)).collect(),
        }
    }

    fn get_connection(&mut self) -> Option<String> {
        self.connections.pop()
    }

    fn release_connection(&mut self, conn: String) {
        if self.connections.len() < self.size {
            self.connections.push(conn);
        }
    }
}

// One-time initialization with OnceCell
static REGISTRY: OnceCell<Mutex<HashMap<String, String>>> = OnceCell::new();

fn get_registry() -> &'static Mutex<HashMap<String, String>> {
    REGISTRY.get_or_init(|| {
        println!("Initializing registry...");
        Mutex::new(HashMap::new())
    })
}

// Lazy per-thread data
use std::cell::RefCell;
thread_local! {
    static THREAD_ID: RefCell<Option<String>> = RefCell::new(None);
    
    static THREAD_CACHE: RefCell<HashMap<String, String>> = RefCell::new({
        println!("Initializing thread-local cache");
        HashMap::new()
    });
}

fn get_thread_id() -> String {
    THREAD_ID.with(|id| {
        let mut id = id.borrow_mut();
        if id.is_none() {
            *id = Some(format!("thread-{}", std::thread::current().id().as_u64()));
        }
        id.clone().unwrap()
    })
}

// Lazy-initialized logger
static LOGGER: Lazy<Mutex<Logger>> = Lazy::new(|| {
    Mutex::new(Logger::new("app.log"))
});

struct Logger {
    file_path: String,
    entries: Vec<String>,
}

impl Logger {
    fn new(file_path: impl Into<String>) -> Self {
        Self {
            file_path: file_path.into(),
            entries: Vec::new(),
        }
    }

    fn log(&mut self, message: impl Into<String>) {
        let entry = format!("[{}] {}", chrono::Utc::now().to_rfc3339(), message.into());
        self.entries.push(entry);
    }

    fn flush(&self) -> std::io::Result<()> {
        std::fs::write(&self.file_path, self.entries.join("
"))
    }
}

// Lazy compiled regex patterns
use regex::Regex;

static EMAIL_PATTERN: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$").unwrap()
});

static URL_PATTERN: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"https?://[^\s]+").unwrap()
});

fn validate_email(email: &str) -> bool {
    EMAIL_PATTERN.is_match(email)
}

fn extract_urls(text: &str) -> Vec<String> {
    URL_PATTERN
        .find_iter(text)
        .map(|m| m.as_str().to_string())
        .collect()
}

// Example usage
fn main() {
    // Access lazy config
    println!("API Key: {}", CONFIG.api_key);
    println!("Max connections: {}", CONFIG.max_connections);

    // Use database pool
    {
        let mut pool = DB_POOL.lock().unwrap();
        if let Some(conn) = pool.get_connection() {
            println!("Got connection: {}", conn);
            pool.release_connection(conn);
        }
    }

    // Use registry
    {
        let registry = get_registry();
        let mut reg = registry.lock().unwrap();
        reg.insert("key1".to_string(), "value1".to_string());
        println!("Registry size: {}", reg.len());
    }

    // Thread-local data
    let handles: Vec<_> = (0..3)
        .map(|_| {
            std::thread::spawn(|| {
                let thread_id = get_thread_id();
                println!("Thread ID: {}", thread_id);
                
                THREAD_CACHE.with(|cache| {
                    let mut cache = cache.borrow_mut();
                    cache.insert("local_key".to_string(), thread_id.clone());
                    println!("Cache size: {}", cache.len());
                });
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    // Logger
    {
        let mut logger = LOGGER.lock().unwrap();
        logger.log("Application started");
        logger.log("Processing request");
        logger.flush().unwrap();
    }

    // Regex validation
    println!("Email valid: {}", validate_email("test@example.com"));
    let urls = extract_urls("Visit https://example.com and https://rust-lang.org");
    println!("Found URLs: {:?}", urls);
}
""",
        "category": 'rust',
        "subcategory": 'onecell',
        "tags": ['api', 'database', 'form', 'http', 'onecell', 'orm', 'request']
    }
]
