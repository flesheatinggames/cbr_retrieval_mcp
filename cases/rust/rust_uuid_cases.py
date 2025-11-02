
RUST_UUID_CASES = [
    {
        "problem": """
UUID generation, parsing, and validation for distributed systems.
""",
        "solution": """
use uuid::{Uuid, uuid, Builder, Variant, Version};
use std::collections::HashMap;
use std::sync::Arc;
use std::sync::atomic::{AtomicU64, Ordering};
use serde::{Deserialize, Serialize};

// Constant UUID for well-known identifiers
pub const SYSTEM_USER_ID: Uuid = uuid!("00000000-0000-0000-0000-000000000001");
pub const ADMIN_ROLE_ID: Uuid = uuid!("00000000-0000-0000-0000-000000000002");

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Entity {
    pub id: Uuid,
    pub name: String,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

// UUID generator with different strategies
pub struct UuidGenerator;

impl UuidGenerator {
    // V4: Random UUID
    pub fn random() -> Uuid {
        Uuid::new_v4()
    }

    // V1: Time-based UUID
    pub fn time_based() -> Uuid {
        let context = uuid::ContextV1::new(0);
        Uuid::now_v1(&context)
    }

    // V5: Name-based UUID (SHA-1)
    pub fn namespaced(namespace: &Uuid, name: &str) -> Uuid {
        Uuid::new_v5(namespace, name.as_bytes())
    }

    // V7: Time-ordered UUID (monotonic)
    pub fn time_ordered() -> Uuid {
        Uuid::now_v7()
    }

    // Generate multiple UUIDs efficiently
    pub fn generate_batch(count: usize) -> Vec<Uuid> {
        (0..count).map(|_| Uuid::new_v4()).collect()
    }
}

// UUID validator
pub struct UuidValidator;

impl UuidValidator {
    pub fn is_valid(uuid_str: &str) -> bool {
        Uuid::parse_str(uuid_str).is_ok()
    }

    pub fn validate_version(uuid: &Uuid, version: Version) -> bool {
        uuid.get_version() == Some(version)
    }

    pub fn validate_variant(uuid: &Uuid, variant: Variant) -> bool {
        uuid.get_variant() == variant
    }

    pub fn is_nil(uuid: &Uuid) -> bool {
        uuid.is_nil()
    }
}

// UUID registry for tracking and lookup
pub struct UuidRegistry<T> {
    entries: Arc<std::sync::RwLock<HashMap<Uuid, T>>>,
    counter: Arc<AtomicU64>,
}

impl<T: Clone> UuidRegistry<T> {
    pub fn new() -> Self {
        Self {
            entries: Arc::new(std::sync::RwLock::new(HashMap::new())),
            counter: Arc::new(AtomicU64::new(0)),
        }
    }

    pub fn register(&self, value: T) -> Uuid {
        let id = Uuid::new_v4();
        self.entries.write().unwrap().insert(id, value);
        self.counter.fetch_add(1, Ordering::Relaxed);
        id
    }

    pub fn register_with_id(&self, id: Uuid, value: T) -> Result<(), String> {
        let mut entries = self.entries.write().unwrap();
        if entries.contains_key(&id) {
            return Err("UUID already exists".to_string());
        }
        entries.insert(id, value);
        self.counter.fetch_add(1, Ordering::Relaxed);
        Ok(())
    }

    pub fn get(&self, id: &Uuid) -> Option<T> {
        self.entries.read().unwrap().get(id).cloned()
    }

    pub fn remove(&self, id: &Uuid) -> Option<T> {
        let removed = self.entries.write().unwrap().remove(id);
        if removed.is_some() {
            self.counter.fetch_sub(1, Ordering::Relaxed);
        }
        removed
    }

    pub fn exists(&self, id: &Uuid) -> bool {
        self.entries.read().unwrap().contains_key(id)
    }

    pub fn count(&self) -> u64 {
        self.counter.load(Ordering::Relaxed)
    }

    pub fn list_ids(&self) -> Vec<Uuid> {
        self.entries.read().unwrap().keys().copied().collect()
    }
}

// UUID-based distributed ID generator
pub struct DistributedIdGenerator {
    node_id: u64,
    sequence: Arc<AtomicU64>,
}

impl DistributedIdGenerator {
    pub fn new(node_id: u64) -> Self {
        Self {
            node_id,
            sequence: Arc::new(AtomicU64::new(0)),
        }
    }

    pub fn generate(&self) -> Uuid {
        let timestamp = chrono::Utc::now().timestamp_millis() as u64;
        let seq = self.sequence.fetch_add(1, Ordering::Relaxed);

        // Custom UUID layout: timestamp + node_id + sequence
        let bytes = [
            ((timestamp >> 40) & 0xFF) as u8,
            ((timestamp >> 32) & 0xFF) as u8,
            ((timestamp >> 24) & 0xFF) as u8,
            ((timestamp >> 16) & 0xFF) as u8,
            ((timestamp >> 8) & 0xFF) as u8,
            (timestamp & 0xFF) as u8,
            ((self.node_id >> 8) & 0xFF) as u8,
            (self.node_id & 0xFF) as u8,
            ((seq >> 56) & 0xFF) as u8,
            ((seq >> 48) & 0xFF) as u8,
            ((seq >> 40) & 0xFF) as u8,
            ((seq >> 32) & 0xFF) as u8,
            ((seq >> 24) & 0xFF) as u8,
            ((seq >> 16) & 0xFF) as u8,
            ((seq >> 8) & 0xFF) as u8,
            (seq & 0xFF) as u8,
        ];

        Builder::from_bytes(bytes).into_uuid()
    }
}

// UUID utilities
pub mod uuid_utils {
    use super::*;

    pub fn parse_multiple(uuid_strs: &[&str]) -> Vec<Result<Uuid, uuid::Error>> {
        uuid_strs.iter().map(|s| Uuid::parse_str(s)).collect()
    }

    pub fn to_string_batch(uuids: &[Uuid]) -> Vec<String> {
        uuids.iter().map(|uuid| uuid.to_string()).collect()
    }

    pub fn to_hyphenated(uuid: &Uuid) -> String {
        uuid.hyphenated().to_string()
    }

    pub fn to_simple(uuid: &Uuid) -> String {
        uuid.simple().to_string()
    }

    pub fn to_urn(uuid: &Uuid) -> String {
        uuid.urn().to_string()
    }

    pub fn to_bytes_le(uuid: &Uuid) -> [u8; 16] {
        *uuid.as_bytes()
    }

    pub fn compare_uuids(a: &Uuid, b: &Uuid) -> std::cmp::Ordering {
        a.cmp(b)
    }
}

// Example usage
fn main() {
    // Generate different UUID versions
    println!("Random UUID (V4): {}", UuidGenerator::random());
    println!("Time-based UUID (V7): {}", UuidGenerator::time_ordered());

    // Namespaced UUIDs
    let namespace = Uuid::NAMESPACE_DNS;
    let uuid1 = UuidGenerator::namespaced(&namespace, "example.com");
    let uuid2 = UuidGenerator::namespaced(&namespace, "example.com");
    println!("Namespaced UUIDs are deterministic: {}", uuid1 == uuid2);

    // Validation
    let uuid_str = "550e8400-e29b-41d4-a716-446655440000";
    println!("Is valid UUID: {}", UuidValidator::is_valid(uuid_str));

    if let Ok(uuid) = Uuid::parse_str(uuid_str) {
        println!("Version: {:?}", uuid.get_version());
        println!("Variant: {:?}", uuid.get_variant());
    }

    // Registry usage
    let registry = UuidRegistry::<String>::new();
    
    let id1 = registry.register("Entity 1".to_string());
    let id2 = registry.register("Entity 2".to_string());
    
    println!("\nRegistry count: {}", registry.count());
    println!("Entity 1: {:?}", registry.get(&id1));
    
    // Distributed ID generation
    let generator = DistributedIdGenerator::new(42);
    let ids: Vec<_> = (0..5).map(|_| generator.generate()).collect();
    println!("\nGenerated distributed IDs:");
    for id in ids {
        println!("  {}", id);
    }

    // UUID utilities
    println!("\nUUID formats:");
    let uuid = Uuid::new_v4();
    println!("  Hyphenated: {}", uuid_utils::to_hyphenated(&uuid));
    println!("  Simple: {}", uuid_utils::to_simple(&uuid));
    println!("  URN: {}", uuid_utils::to_urn(&uuid));
}
""",
        "category": 'rust',
        "subcategory": 'uuid',
        "tags": ['form', 'node', 'orm', 'rust', 'serde', 'ui', 'uuid']
    }
]
