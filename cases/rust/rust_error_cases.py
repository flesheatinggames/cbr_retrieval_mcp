

RUST_ERROR_CASES = [
    {
        "problem": """
Comprehensive error handling system using thiserror for library errors and anyhow for application errors with context.
""",
        "solution": """
use thiserror::Error;
use anyhow::{Context, Result as AnyhowResult, bail, ensure};
use std::path::PathBuf;
use std::fmt;

// ============================================
// Library-level errors (using thiserror)
// ============================================

#[derive(Debug, Error)]
pub enum ConfigError {
    #[error("Configuration file not found: {path}")]
    FileNotFound { path: PathBuf },
    
    #[error("Invalid configuration: {message}")]
    InvalidConfig { message: String },
    
    #[error("Failed to parse configuration")]
    ParseError(#[from] toml::de::Error),
    
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
}

#[derive(Debug, Error)]
pub enum DatabaseError {
    #[error("Connection failed: {details}")]
    ConnectionFailed { details: String },
    
    #[error("Query failed: {query}")]
    QueryFailed {
        query: String,
        #[source]
        source: sqlx::Error,
    },
    
    #[error("Entity not found: {entity_type} with id {id}")]
    NotFound {
        entity_type: String,
        id: String,
    },
    
    #[error("Constraint violation: {constraint}")]
    ConstraintViolation { constraint: String },
    
    #[error("Transaction error")]
    TransactionError(#[from] sqlx::Error),
    
    #[error("Migration failed at version {version}: {reason}")]
    MigrationFailed { version: String, reason: String },
}

#[derive(Debug, Error)]
pub enum AuthError {
    #[error("Authentication failed")]
    AuthenticationFailed,
    
    #[error("Invalid credentials")]
    InvalidCredentials,
    
    #[error("Token expired at {expired_at}")]
    TokenExpired { expired_at: String },
    
    #[error("Insufficient permissions: required {required}, have {actual}")]
    InsufficientPermissions { required: String, actual: String },
    
    #[error("Account locked until {unlock_time}")]
    AccountLocked { unlock_time: String },
}

#[derive(Debug, Error)]
pub enum ValidationError {
    #[error("Field '{field}' is required")]
    RequiredField { field: String },
    
    #[error("Field '{field}' must be between {min} and {max} characters")]
    LengthOutOfRange {
        field: String,
        min: usize,
        max: usize,
        actual: usize,
    },
    
    #[error("Invalid {field_type}: {value}")]
    InvalidFormat {
        field_type: String,
        value: String,
        #[source]
        source: Box<dyn std::error::Error + Send + Sync>,
    },
    
    #[error("Multiple validation errors")]
    Multiple {
        errors: Vec<ValidationError>,
    },
}

#[derive(Debug, Error)]
pub enum ApiError {
    #[error("HTTP {status}: {message}")]
    HttpError { status: u16, message: String },
    
    #[error("Network error")]
    NetworkError(#[from] reqwest::Error),
    
    #[error("Rate limit exceeded, retry after {seconds}s")]
    RateLimitExceeded { seconds: u64 },
    
    #[error("Serialization error")]
    SerializationError(#[from] serde_json::Error),
    
    #[error("API timeout after {seconds}s")]
    Timeout { seconds: u64 },
}

// ============================================
// Application-level error (top-level)
// ============================================

#[derive(Debug, Error)]
pub enum AppError {
    #[error("Configuration error")]
    Config(#[from] ConfigError),
    
    #[error("Database error")]
    Database(#[from] DatabaseError),
    
    #[error("Authentication error")]
    Auth(#[from] AuthError),
    
    #[error("Validation error")]
    Validation(#[from] ValidationError),
    
    #[error("External API error")]
    Api(#[from] ApiError),
    
    #[error("Internal server error")]
    Internal(String),
}

// ============================================
// Error conversion and context helpers
// ============================================

pub type AppResult<T> = Result<T, AppError>;

// Extension trait for adding context to results
pub trait ErrorContext<T> {
    fn with_context_info<F>(self, f: F) -> AnyhowResult<T>
    where
        F: FnOnce() -> String;
}

impl<T, E> ErrorContext<T> for Result<T, E>
where
    E: std::error::Error + Send + Sync + 'static,
{
    fn with_context_info<F>(self, f: F) -> AnyhowResult<T>
    where
        F: FnOnce() -> String,
    {
        self.with_context(|| f())
    }
}

// ============================================
// Example usage in application code
// ============================================

use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
pub struct Config {
    pub database_url: String,
    pub api_key: String,
    pub max_connections: usize,
}

pub struct ConfigLoader;

impl ConfigLoader {
    pub fn load(path: &PathBuf) -> Result<Config, ConfigError> {
        // Check if file exists
        if !path.exists() {
            return Err(ConfigError::FileNotFound { path: path.clone() });
        }

        // Read file
        let content = std::fs::read_to_string(path)?;

        // Parse TOML
        let config: Config = toml::from_str(&content)?;

        // Validate
        if config.database_url.is_empty() {
            return Err(ConfigError::InvalidConfig {
                message: "database_url cannot be empty".to_string(),
            });
        }

        if config.max_connections == 0 {
            return Err(ConfigError::InvalidConfig {
                message: "max_connections must be greater than 0".to_string(),
            });
        }

        Ok(config)
    }
}

#[derive(Debug, Serialize)]
pub struct User {
    pub id: i32,
    pub email: String,
    pub name: String,
}

pub struct UserRepository {
    pool: sqlx::PgPool,
}

impl UserRepository {
    pub async fn find_by_id(&self, id: i32) -> Result<User, DatabaseError> {
        sqlx::query_as!(
            User,
            "SELECT id, email, name FROM users WHERE id = $1",
            id
        )
        .fetch_optional(&self.pool)
        .await
        .map_err(|e| DatabaseError::QueryFailed {
            query: format!("SELECT user by id {}", id),
            source: e,
        })?
        .ok_or_else(|| DatabaseError::NotFound {
            entity_type: "User".to_string(),
            id: id.to_string(),
        })
    }

    pub async fn create(&self, email: &str, name: &str) -> Result<User, DatabaseError> {
        sqlx::query_as!(
            User,
            "INSERT INTO users (email, name) VALUES ($1, $2) RETURNING id, email, name",
            email,
            name
        )
        .fetch_one(&self.pool)
        .await
        .map_err(|e| {
            if e.to_string().contains("duplicate key") {
                DatabaseError::ConstraintViolation {
                    constraint: "unique_email".to_string(),
                }
            } else {
                DatabaseError::QueryFailed {
                    query: "INSERT user".to_string(),
                    source: e,
                }
            }
        })
    }
}

pub struct Validator;

impl Validator {
    pub fn validate_email(email: &str) -> Result<(), ValidationError> {
        if email.is_empty() {
            return Err(ValidationError::RequiredField {
                field: "email".to_string(),
            });
        }

        if !email.contains('@') {
            return Err(ValidationError::InvalidFormat {
                field_type: "email".to_string(),
                value: email.to_string(),
                source: "Missing @ symbol".into(),
            });
        }

        Ok(())
    }

    pub fn validate_name(name: &str) -> Result<(), ValidationError> {
        let len = name.len();
        if len < 2 || len > 100 {
            return Err(ValidationError::LengthOutOfRange {
                field: "name".to_string(),
                min: 2,
                max: 100,
                actual: len,
            });
        }

        Ok(())
    }

    pub fn validate_user_input(email: &str, name: &str) -> Result<(), ValidationError> {
        let mut errors = Vec::new();

        if let Err(e) = Self::validate_email(email) {
            errors.push(e);
        }

        if let Err(e) = Self::validate_name(name) {
            errors.push(e);
        }

        if !errors.is_empty() {
            return Err(ValidationError::Multiple { errors });
        }

        Ok(())
    }
}

// ============================================
// Application service layer (using anyhow)
// ============================================

pub struct UserService {
    repository: UserRepository,
}

impl UserService {
    pub async fn create_user(&self, email: String, name: String) -> AnyhowResult<User> {
        // Validate input
        Validator::validate_user_input(&email, &name)
            .context("Failed to validate user input")?;

        // Create user
        let user = self.repository
            .create(&email, &name)
            .await
            .with_context(|| format!("Failed to create user with email: {}", email))?;

        tracing::info!("User created successfully: {}", user.id);

        Ok(user)
    }

    pub async fn get_user(&self, id: i32) -> AnyhowResult<User> {
        ensure!(id > 0, "User ID must be positive, got: {}", id);

        self.repository
            .find_by_id(id)
            .await
            .with_context(|| format!("Failed to fetch user with id: {}", id))
    }

    pub async fn process_users(&self, ids: Vec<i32>) -> AnyhowResult<Vec<User>> {
        if ids.is_empty() {
            bail!("Cannot process empty list of user IDs");
        }

        let mut users = Vec::new();

        for id in ids {
            match self.get_user(id).await {
                Ok(user) => users.push(user),
                Err(e) => {
                    tracing::warn!("Failed to fetch user {}: {:#}", id, e);
                    // Continue processing other users
                }
            }
        }

        if users.is_empty() {
            bail!("No users could be processed successfully");
        }

        Ok(users)
    }
}

// ============================================
// HTTP API layer with error responses
// ============================================

use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
    details: Option<String>,
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, error_message, details) = match self {
            AppError::Config(e) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                "Configuration error".to_string(),
                Some(e.to_string()),
            ),
            AppError::Database(DatabaseError::NotFound { .. }) => (
                StatusCode::NOT_FOUND,
                "Resource not found".to_string(),
                Some(self.to_string()),
            ),
            AppError::Database(DatabaseError::ConstraintViolation { .. }) => (
                StatusCode::CONFLICT,
                "Constraint violation".to_string(),
                Some(self.to_string()),
            ),
            AppError::Database(_) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                "Database error".to_string(),
                None, // Don't expose internal database errors
            ),
            AppError::Auth(AuthError::InvalidCredentials) => (
                StatusCode::UNAUTHORIZED,
                "Invalid credentials".to_string(),
                None,
            ),
            AppError::Auth(AuthError::InsufficientPermissions { .. }) => (
                StatusCode::FORBIDDEN,
                "Insufficient permissions".to_string(),
                Some(self.to_string()),
            ),
            AppError::Auth(_) => (
                StatusCode::UNAUTHORIZED,
                "Authentication failed".to_string(),
                Some(self.to_string()),
            ),
            AppError::Validation(ValidationError::Multiple { ref errors }) => (
                StatusCode::BAD_REQUEST,
                "Validation failed".to_string(),
                Some(format!("{} errors found", errors.len())),
            ),
            AppError::Validation(_) => (
                StatusCode::BAD_REQUEST,
                "Validation failed".to_string(),
                Some(self.to_string()),
            ),
            AppError::Api(ApiError::RateLimitExceeded { .. }) => (
                StatusCode::TOO_MANY_REQUESTS,
                "Rate limit exceeded".to_string(),
                Some(self.to_string()),
            ),
            AppError::Api(_) => (
                StatusCode::BAD_GATEWAY,
                "External API error".to_string(),
                Some(self.to_string()),
            ),
            AppError::Internal(_) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                "Internal server error".to_string(),
                None,
            ),
        };

        let body = Json(ErrorResponse {
            error: error_message,
            details,
        });

        (status, body).into_response()
    }
}

// Example usage in HTTP handlers
pub async fn create_user_handler(
    service: UserService,
    Json(payload): Json<CreateUserRequest>,
) -> Result<Json<User>, AppError> {
    let user = service
        .create_user(payload.email, payload.name)
        .await
        .map_err(|e| {
            tracing::error!("Failed to create user: {:#}", e);
            AppError::Internal(e.to_string())
        })?;

    Ok(Json(user))
}

#[derive(Deserialize)]
struct CreateUserRequest {
    email: String,
    name: String,
}
""",
        "category": 'rust',
        "subcategory": 'error',
        "tags": ['api', 'async', 'auth', 'authentication', 'axum', 'database', 'error']
    }
]
