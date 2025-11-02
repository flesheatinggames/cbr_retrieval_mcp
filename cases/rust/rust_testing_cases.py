
RUST_TESTING_CASES = [
    {
        "problem": """
Comprehensive testing patterns including unit tests, integration tests, mocking, and property-based testing.
""",
        "solution": """
#[cfg(test)]
mod tests {
    use super::*;
    use mockall::{predicate::*, mock};
    use proptest::prelude::*;

    // ============================================
    // Basic Unit Tests
    // ============================================

    #[test]
    fn test_addition() {
        assert_eq!(2 + 2, 4);
    }

    #[test]
    fn test_string_concatenation() {
        let result = format!("{} {}", "Hello", "World");
        assert_eq!(result, "Hello World");
    }

    #[test]
    #[should_panic(expected = "divide by zero")]
    fn test_divide_by_zero() {
        let _result = 10 / 0;
    }

    // ============================================
    // Testing with Setup and Teardown
    // ============================================

    struct TestContext {
        temp_file: std::path::PathBuf,
    }

    impl TestContext {
        fn new() -> Self {
            let temp_file = std::env::temp_dir().join(format!("test_{}.txt", uuid::Uuid::new_v4()));
            Self { temp_file }
        }
    }

    impl Drop for TestContext {
        fn drop(&mut self) {
            let _ = std::fs::remove_file(&self.temp_file);
        }
    }

    #[test]
    fn test_with_context() {
        let ctx = TestContext::new();
        std::fs::write(&ctx.temp_file, "test data").unwrap();
        
        let content = std::fs::read_to_string(&ctx.temp_file).unwrap();
        assert_eq!(content, "test data");
        // File will be cleaned up when ctx is dropped
    }

    // ============================================
    // Mocking with Mockall
    // ============================================

    pub trait UserRepository {
        fn find_user(&self, id: u32) -> Option<User>;
        fn create_user(&mut self, name: String) -> Result<User, String>;
    }

    mock! {
        pub UserRepo {}
        impl UserRepository for UserRepo {
            fn find_user(&self, id: u32) -> Option<User>;
            fn create_user(&mut self, name: String) -> Result<User, String>;
        }
    }

    #[derive(Debug, Clone, PartialEq)]
    pub struct User {
        pub id: u32,
        pub name: String,
    }

    pub struct UserService<R: UserRepository> {
        repo: R,
    }

    impl<R: UserRepository> UserService<R> {
        pub fn new(repo: R) -> Self {
            Self { repo }
        }

        pub fn get_user(&self, id: u32) -> Result<User, String> {
            self.repo.find_user(id).ok_or_else(|| "User not found".to_string())
        }
    }

    #[test]
    fn test_user_service_with_mock() {
        let mut mock_repo = MockUserRepo::new();
        
        mock_repo
            .expect_find_user()
            .with(eq(1))
            .times(1)
            .returning(|_| Some(User {
                id: 1,
                name: "John Doe".to_string(),
            }));

        let service = UserService::new(mock_repo);
        let user = service.get_user(1).unwrap();
        
        assert_eq!(user.id, 1);
        assert_eq!(user.name, "John Doe");
    }

    #[test]
    fn test_user_not_found() {
        let mut mock_repo = MockUserRepo::new();
        
        mock_repo
            .expect_find_user()
            .with(eq(999))
            .returning(|_| None);

        let service = UserService::new(mock_repo);
        let result = service.get_user(999);
        
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), "User not found");
    }

    // ============================================
    // Async Tests
    // ============================================

    async fn async_operation() -> Result<String, String> {
        tokio::time::sleep(tokio::time::Duration::from_millis(10)).await;
        Ok("Success".to_string())
    }

    #[tokio::test]
    async fn test_async_operation() {
        let result = async_operation().await;
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), "Success");
    }

    #[tokio::test]
    async fn test_timeout() {
        let result = tokio::time::timeout(
            tokio::time::Duration::from_millis(5),
            tokio::time::sleep(tokio::time::Duration::from_secs(1)),
        ).await;
        
        assert!(result.is_err());
    }

    // ============================================
    // Property-Based Testing
    // ============================================

    proptest! {
        #[test]
        fn test_addition_commutative(a in 0..1000i32, b in 0..1000i32) {
            prop_assert_eq!(a + b, b + a);
        }

        #[test]
        fn test_string_reverse_twice(s in ".*") {
            let reversed_once: String = s.chars().rev().collect();
            let reversed_twice: String = reversed_once.chars().rev().collect();
            prop_assert_eq!(s, reversed_twice);
        }

        #[test]
        fn test_vec_length_after_push(v in prop::collection::vec(any::<i32>(), 0..100)) {
            let original_len = v.len();
            let mut v_mut = v.clone();
            v_mut.push(42);
            prop_assert_eq!(v_mut.len(), original_len + 1);
        }
    }

    // ============================================
    // Parameterized Tests
    // ============================================

    #[test]
    fn test_multiple_inputs() {
        let test_cases = vec![
            ("input1", "output1"),
            ("input2", "output2"),
            ("input3", "output3"),
        ];

        for (input, expected) in test_cases {
            let result = process_string(input);
            assert_eq!(result, expected, "Failed for input: {}", input);
        }
    }

    fn process_string(input: &str) -> String {
        format!("out{}", &input[2..])
    }

    // ============================================
    // Integration Tests Helper
    // ============================================

    pub struct TestDatabase {
        pub pool: sqlx::PgPool,
    }

    impl TestDatabase {
        pub async fn new() -> Self {
            let database_url = std::env::var("TEST_DATABASE_URL")
                .unwrap_or_else(|_| "postgres://localhost/test_db".to_string());
            
            let pool = sqlx::postgres::PgPoolOptions::new()
                .max_connections(5)
                .connect(&database_url)
                .await
                .expect("Failed to create test database pool");

            // Run migrations
            sqlx::migrate!("./migrations")
                .run(&pool)
                .await
                .expect("Failed to run migrations");

            Self { pool }
        }

        pub async fn cleanup(&self) {
            sqlx::query("TRUNCATE TABLE users CASCADE")
                .execute(&self.pool)
                .await
                .expect("Failed to cleanup database");
        }
    }

    // ============================================
    // Benchmark Tests (with criterion)
    // ============================================

    // Note: Benchmarks are typically in benches/ directory
    // This is示例 structure:
    /*
    use criterion::{black_box, criterion_group, criterion_main, Criterion};

    fn fibonacci(n: u64) -> u64 {
        match n {
            0 => 0,
            1 => 1,
            n => fibonacci(n - 1) + fibonacci(n - 2),
        }
    }

    fn criterion_benchmark(c: &mut Criterion) {
        c.bench_function("fib 20", |b| b.iter(|| fibonacci(black_box(20))));
    }

    criterion_group!(benches, criterion_benchmark);
    criterion_main!(benches);
    */

    // ============================================
    // Snapshot Testing Pattern
    // ============================================

    #[test]
    fn test_json_output() {
        let data = User {
            id: 1,
            name: "John Doe".to_string(),
        };

        let json = serde_json::to_string_pretty(&data).unwrap();
        
        // In real snapshot testing, you'd use insta crate:
        // insta::assert_snapshot!(json);
        
        assert!(json.contains(""id": 1"));
        assert!(json.contains(""name": "John Doe""));
    }

    // ============================================
    // Error Case Testing
    // ============================================

    fn divide(a: i32, b: i32) -> Result<i32, String> {
        if b == 0 {
            Err("Division by zero".to_string())
        } else {
            Ok(a / b)
        }
    }

    #[test]
    fn test_division_success() {
        let result = divide(10, 2);
        assert_eq!(result.unwrap(), 5);
    }

    #[test]
    fn test_division_by_zero() {
        let result = divide(10, 0);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), "Division by zero");
    }

    // ============================================
    // Custom Test Assertions
    // ============================================

    fn assert_approximately_equal(a: f64, b: f64, epsilon: f64) {
        assert!(
            (a - b).abs() < epsilon,
            "Values not approximately equal: {} vs {}",
            a,
            b
        );
    }

    #[test]
    fn test_floating_point_comparison() {
        let result = 0.1 + 0.2;
        assert_approximately_equal(result, 0.3, 0.0001);
    }
}

// Example of test module organization
#[cfg(test)]
mod unit_tests {
    // Unit tests here
}

#[cfg(test)]
mod integration_tests {
    // Integration tests here
}
""",
        "category": 'rust',
        "subcategory": 'testing',
        "tags": ['async', 'database', 'form', 'json', 'migration', 'orm', 'query']
    }
]
