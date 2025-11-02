
RUST_DASHMAP_CASES = [
    {
        "problem": """
High-performance concurrent HashMap using DashMap for lock-free operations.
""",
        "solution": """
use dashmap::{DashMap, DashSet};
use std::sync::Arc;
use std::thread;
use std::time::Duration;
use serde::{Deserialize, Serialize};

// Cache with automatic expiration
#[derive(Clone, Serialize, Deserialize)]
pub struct CacheEntry<T> {
    pub value: T,
    pub expires_at: std::time::Instant,
}

pub struct ExpiringCache<K, V> {
    map: Arc<DashMap<K, CacheEntry<V>>>,
}

impl<K, V> ExpiringCache<K, V>
where
    K: Eq + std::hash::Hash + Clone,
    V: Clone,
{
    pub fn new() -> Self {
        Self {
            map: Arc::new(DashMap::new()),
        }
    }

    pub fn insert(&self, key: K, value: V, ttl: Duration) {
        let entry = CacheEntry {
            value,
            expires_at: std::time::Instant::now() + ttl,
        };
        self.map.insert(key, entry);
    }

    pub fn get(&self, key: &K) -> Option<V> {
        self.map.get(key).and_then(|entry| {
            if entry.expires_at > std::time::Instant::now() {
                Some(entry.value.clone())
            } else {
                drop(entry);
                self.map.remove(key);
                None
            }
        })
    }

    pub fn remove(&self, key: &K) -> Option<V> {
        self.map.remove(key).map(|(_, entry)| entry.value)
    }

    pub fn cleanup_expired(&self) {
        let now = std::time::Instant::now();
        self.map.retain(|_, entry| entry.expires_at > now);
    }

    pub fn len(&self) -> usize {
        self.map.len()
    }
}

// Concurrent session store
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Session {
    pub user_id: String,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub last_accessed: chrono::DateTime<chrono::Utc>,
    pub data: serde_json::Value,
}

pub struct SessionStore {
    sessions: Arc<DashMap<String, Session>>,
}

impl SessionStore {
    pub fn new() -> Self {
        Self {
            sessions: Arc::new(DashMap::new()),
        }
    }

    pub fn create_session(&self, user_id: String) -> String {
        let session_id = uuid::Uuid::new_v4().to_string();
        let session = Session {
            user_id,
            created_at: chrono::Utc::now(),
            last_accessed: chrono::Utc::now(),
            data: serde_json::json!({}),
        };
        self.sessions.insert(session_id.clone(), session);
        session_id
    }

    pub fn get_session(&self, session_id: &str) -> Option<Session> {
        self.sessions.get_mut(session_id).map(|mut entry| {
            entry.last_accessed = chrono::Utc::now();
            entry.clone()
        })
    }

    pub fn update_session_data(&self, session_id: &str, data: serde_json::Value) -> bool {
        self.sessions.get_mut(session_id).map(|mut session| {
            session.data = data;
            session.last_accessed = chrono::Utc::now();
        }).is_some()
    }

    pub fn delete_session(&self, session_id: &str) -> bool {
        self.sessions.remove(session_id).is_some()
    }

    pub fn cleanup_inactive(&self, max_age: Duration) {
        let cutoff = chrono::Utc::now() - chrono::Duration::from_std(max_age).unwrap();
        self.sessions.retain(|_, session| session.last_accessed > cutoff);
    }

    pub fn active_sessions(&self) -> usize {
        self.sessions.len()
    }
}

// Concurrent metrics collector
pub struct MetricsCollector {
    counters: Arc<DashMap<String, u64>>,
    gauges: Arc<DashMap<String, f64>>,
}

impl MetricsCollector {
    pub fn new() -> Self {
        Self {
            counters: Arc::new(DashMap::new()),
            gauges: Arc::new(DashMap::new()),
        }
    }

    pub fn increment_counter(&self, name: &str, value: u64) {
        self.counters
            .entry(name.to_string())
            .and_modify(|v| *v += value)
            .or_insert(value);
    }

    pub fn set_gauge(&self, name: &str, value: f64) {
        self.gauges.insert(name.to_string(), value);
    }

    pub fn get_counter(&self, name: &str) -> Option<u64> {
        self.counters.get(name).map(|v| *v)
    }

    pub fn get_gauge(&self, name: &str) -> Option<f64> {
        self.gauges.get(name).map(|v| *v)
    }

    pub fn snapshot(&self) -> (Vec<(String, u64)>, Vec<(String, f64)>) {
        let counters: Vec<_> = self.counters
            .iter()
            .map(|entry| (entry.key().clone(), *entry.value()))
            .collect();

        let gauges: Vec<_> = self.gauges
            .iter()
            .map(|entry| (entry.key().clone(), *entry.value()))
            .collect();

        (counters, gauges)
    }

    pub fn reset(&self) {
        self.counters.clear();
        self.gauges.clear();
    }
}

// Distributed rate limiter
pub struct RateLimiter {
    requests: Arc<DashMap<String, Vec<std::time::Instant>>>,
    max_requests: usize,
    window: Duration,
}

impl RateLimiter {
    pub fn new(max_requests: usize, window: Duration) -> Self {
        Self {
            requests: Arc::new(DashMap::new()),
            max_requests,
            window,
        }
    }

    pub fn check_rate_limit(&self, key: &str) -> bool {
        let now = std::time::Instant::now();
        let cutoff = now - self.window;

        let mut entry = self.requests.entry(key.to_string()).or_insert_with(Vec::new);
        
        // Remove old requests
        entry.retain(|&timestamp| timestamp > cutoff);

        if entry.len() < self.max_requests {
            entry.push(now);
            true
        } else {
            false
        }
    }

    pub fn cleanup(&self) {
        let cutoff = std::time::Instant::now() - self.window;
        self.requests.retain(|_, timestamps| {
            !timestamps.is_empty() && timestamps.last().map_or(false, |&t| t > cutoff)
        });
    }
}

// Concurrent set operations
pub struct UniqueVisitors {
    visitors: Arc<DashSet<String>>,
}

impl UniqueVisitors {
    pub fn new() -> Self {
        Self {
            visitors: Arc::new(DashSet::new()),
        }
    }

    pub fn visit(&self, visitor_id: String) -> bool {
        self.visitors.insert(visitor_id)
    }

    pub fn has_visited(&self, visitor_id: &str) -> bool {
        self.visitors.contains(visitor_id)
    }

    pub fn count(&self) -> usize {
        self.visitors.len()
    }

    pub fn clear(&self) {
        self.visitors.clear();
    }
}

// Example usage
fn main() {
    // Expiring cache
    let cache = Arc::new(ExpiringCache::new());
    cache.insert("key1", "value1", Duration::from_secs(2));
    
    println!("Value: {:?}", cache.get(&"key1"));
    thread::sleep(Duration::from_secs(3));
    println!("Value after expiry: {:?}", cache.get(&"key1"));

    // Session store
    let store = Arc::new(SessionStore::new());
    let session_id = store.create_session("user123".to_string());
    println!("Created session: {}", session_id);

    if let Some(session) = store.get_session(&session_id) {
        println!("Session user: {}", session.user_id);
    }

    // Metrics collector
    let metrics = Arc::new(MetricsCollector::new());
    
    let handles: Vec<_> = (0..10)
        .map(|i| {
            let metrics = metrics.clone();
            thread::spawn(move || {
                for _ in 0..100 {
                    metrics.increment_counter("requests", 1);
                    metrics.set_gauge(&format!("worker_{}", i), i as f64 * 1.5);
                }
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    let (counters, gauges) = metrics.snapshot();
    println!("Total requests: {:?}", counters);
    println!("Number of gauges: {}", gauges.len());

    // Rate limiter
    let limiter = Arc::new(RateLimiter::new(5, Duration::from_secs(1)));
    
    for i in 0..10 {
        let allowed = limiter.check_rate_limit("user123");
        println!("Request {}: {}", i, if allowed { "allowed" } else { "blocked" });
    }

    // Unique visitors
    let visitors = Arc::new(UniqueVisitors::new());
    
    visitors.visit("visitor1".to_string());
    visitors.visit("visitor2".to_string());
    visitors.visit("visitor1".to_string()); // Duplicate
    
    println!("Unique visitors: {}", visitors.count());
}
""",
        "category": 'rust',
        "subcategory": 'dashmap',
        "tags": ['dashmap', 'form', 'json', 'orm', 'performance', 'request', 'rust']
    }
]
