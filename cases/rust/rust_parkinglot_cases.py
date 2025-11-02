
RUST_PARKINGLOT_CASES = [
    {
        "problem": """
High-performance synchronization primitives using parking_lot for better performance than std::sync.
""",
        "solution": """
use parking_lot::{Mutex, RwLock, Condvar, Once, OnceState};
use std::sync::Arc;
use std::thread;
use std::time::Duration;

// Shared counter with Mutex
#[derive(Default)]
pub struct Counter {
    value: Mutex<u64>,
}

impl Counter {
    pub fn new() -> Self {
        Self {
            value: Mutex::new(0),
        }
    }

    pub fn increment(&self) {
        let mut val = self.value.lock();
        *val += 1;
    }

    pub fn get(&self) -> u64 {
        *self.value.lock()
    }

    pub fn increment_by(&self, amount: u64) {
        let mut val = self.value.lock();
        *val += amount;
    }
}

// Read-write cache with RwLock
pub struct Cache<K, V> {
    data: RwLock<std::collections::HashMap<K, V>>,
}

impl<K: Eq + std::hash::Hash + Clone, V: Clone> Cache<K, V> {
    pub fn new() -> Self {
        Self {
            data: RwLock::new(std::collections::HashMap::new()),
        }
    }

    pub fn get(&self, key: &K) -> Option<V> {
        // Multiple readers can access simultaneously
        let data = self.data.read();
        data.get(key).cloned()
    }

    pub fn insert(&self, key: K, value: V) -> Option<V> {
        // Exclusive write access
        let mut data = self.data.write();
        data.insert(key, value)
    }

    pub fn remove(&self, key: &K) -> Option<V> {
        let mut data = self.data.write();
        data.remove(key)
    }

    pub fn contains_key(&self, key: &K) -> bool {
        let data = self.data.read();
        data.contains_key(key)
    }

    pub fn len(&self) -> usize {
        let data = self.data.read();
        data.len()
    }

    pub fn clear(&self) {
        let mut data = self.data.write();
        data.clear();
    }
}

// Producer-Consumer with Condvar
pub struct BoundedQueue<T> {
    queue: Mutex<std::collections::VecDeque<T>>,
    not_empty: Condvar,
    not_full: Condvar,
    capacity: usize,
}

impl<T> BoundedQueue<T> {
    pub fn new(capacity: usize) -> Self {
        Self {
            queue: Mutex::new(std::collections::VecDeque::with_capacity(capacity)),
            not_empty: Condvar::new(),
            not_full: Condvar::new(),
            capacity,
        }
    }

    pub fn push(&self, item: T) {
        let mut queue = self.queue.lock();
        
        // Wait until there's space
        while queue.len() >= self.capacity {
            self.not_full.wait(&mut queue);
        }
        
        queue.push_back(item);
        self.not_empty.notify_one();
    }

    pub fn pop(&self) -> T {
        let mut queue = self.queue.lock();
        
        // Wait until there's an item
        while queue.is_empty() {
            self.not_empty.wait(&mut queue);
        }
        
        let item = queue.pop_front().unwrap();
        self.not_full.notify_one();
        item
    }

    pub fn try_push(&self, item: T) -> Result<(), T> {
        let mut queue = self.queue.lock();
        
        if queue.len() >= self.capacity {
            return Err(item);
        }
        
        queue.push_back(item);
        self.not_empty.notify_one();
        Ok(())
    }

    pub fn try_pop(&self) -> Option<T> {
        let mut queue = self.queue.lock();
        
        if queue.is_empty() {
            return None;
        }
        
        let item = queue.pop_front();
        self.not_full.notify_one();
        item
    }

    pub fn len(&self) -> usize {
        self.queue.lock().len()
    }
}

// Lazy initialization with Once
pub struct LazyResource {
    once: Once,
    resource: RwLock<Option<String>>,
}

impl LazyResource {
    pub fn new() -> Self {
        Self {
            once: Once::new(),
            resource: RwLock::new(None),
        }
    }

    pub fn get(&self) -> String {
        self.once.call_once(|| {
            println!("Initializing resource...");
            thread::sleep(Duration::from_millis(100));
            *self.resource.write() = Some("Initialized Resource".to_string());
        });

        self.resource.read().as_ref().unwrap().clone()
    }

    pub fn is_initialized(&self) -> bool {
        self.once.state() == OnceState::Done
    }
}

// Thread-safe event log
pub struct EventLog {
    events: Mutex<Vec<(chrono::DateTime<chrono::Utc>, String)>>,
    max_events: usize,
}

impl EventLog {
    pub fn new(max_events: usize) -> Self {
        Self {
            events: Mutex::new(Vec::with_capacity(max_events)),
            max_events,
        }
    }

    pub fn log(&self, message: impl Into<String>) {
        let mut events = self.events.lock();
        
        if events.len() >= self.max_events {
            events.remove(0);
        }
        
        events.push((chrono::Utc::now(), message.into()));
    }

    pub fn get_recent(&self, count: usize) -> Vec<(chrono::DateTime<chrono::Utc>, String)> {
        let events = self.events.lock();
        let start = events.len().saturating_sub(count);
        events[start..].to_vec()
    }

    pub fn clear(&self) {
        let mut events = self.events.lock();
        events.clear();
    }
}

// Connection pool with RwLock
pub struct ConnectionPool {
    connections: RwLock<Vec<String>>,
    max_size: usize,
}

impl ConnectionPool {
    pub fn new(max_size: usize) -> Self {
        Self {
            connections: RwLock::new(Vec::new()),
            max_size,
        }
    }

    pub fn acquire(&self) -> Option<String> {
        let mut connections = self.connections.write();
        connections.pop()
    }

    pub fn release(&self, connection: String) -> Result<(), String> {
        let mut connections = self.connections.write();
        
        if connections.len() >= self.max_size {
            return Err("Pool is full".to_string());
        }
        
        connections.push(connection);
        Ok(())
    }

    pub fn size(&self) -> usize {
        self.connections.read().len()
    }
}

// Example usage
fn main() {
    // Counter example
    let counter = Arc::new(Counter::new());
    let handles: Vec<_> = (0..10)
        .map(|_| {
            let counter = counter.clone();
            thread::spawn(move || {
                for _ in 0..1000 {
                    counter.increment();
                }
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Final counter value: {}", counter.get());

    // Cache example
    let cache = Arc::new(Cache::<String, i32>::new());
    
    cache.insert("key1".to_string(), 42);
    cache.insert("key2".to_string(), 84);
    
    println!("Cache get key1: {:?}", cache.get(&"key1".to_string()));
    println!("Cache size: {}", cache.len());

    // Bounded queue example
    let queue = Arc::new(BoundedQueue::new(5));
    
    let producer_queue = queue.clone();
    let producer = thread::spawn(move || {
        for i in 0..10 {
            producer_queue.push(i);
            println!("Produced: {}", i);
            thread::sleep(Duration::from_millis(50));
        }
    });

    let consumer_queue = queue.clone();
    let consumer = thread::spawn(move || {
        for _ in 0..10 {
            let item = consumer_queue.pop();
            println!("Consumed: {}", item);
            thread::sleep(Duration::from_millis(100));
        }
    });

    producer.join().unwrap();
    consumer.join().unwrap();

    // Lazy resource example
    let resource = Arc::new(LazyResource::new());
    
    println!("Is initialized: {}", resource.is_initialized());
    
    let handles: Vec<_> = (0..3)
        .map(|i| {
            let resource = resource.clone();
            thread::spawn(move || {
                println!("Thread {}: {}", i, resource.get());
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    // Event log example
    let log = Arc::new(EventLog::new(100));
    
    log.log("Application started");
    log.log("Processing data");
    log.log("Operation completed");
    
    println!("\nRecent events:");
    for (timestamp, message) in log.get_recent(3) {
        println!("  [{}] {}", timestamp.format("%H:%M:%S"), message);
    }
}
""",
        "category": 'rust',
        "subcategory": 'parkinglot',
        "tags": ['event', 'form', 'orm', 'parkinglot', 'performance', 'rust', 'ui']
    }
]
