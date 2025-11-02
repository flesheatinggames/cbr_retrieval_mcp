
RUST_SERDE_CASES = [
    {
        "problem": """
Custom serde serialization and deserialization with complex nested structures and validation.
""",
        "solution": """
use serde::{Deserialize, Deserializer, Serialize, Serializer, de};
use std::collections::HashMap;
use chrono::{DateTime, Utc, NaiveDate};
use std::str::FromStr;

// Custom date format serialization
fn serialize_date<S>(date: &NaiveDate, serializer: S) -> Result<S::Ok, S::Error>
where
    S: Serializer,
{
    serializer.serialize_str(&date.format("%Y-%m-%d").to_string())
}

fn deserialize_date<'de, D>(deserializer: D) -> Result<NaiveDate, D::Error>
where
    D: Deserializer<'de>,
{
    let s = String::deserialize(deserializer)?;
    NaiveDate::parse_from_str(&s, "%Y-%m-%d")
        .map_err(de::Error::custom)
}

// Custom enum with string representation
#[derive(Debug, Clone, PartialEq)]
pub enum UserRole {
    Admin,
    User,
    Guest,
    Custom(String),
}

impl Serialize for UserRole {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let role_str = match self {
            UserRole::Admin => "admin",
            UserRole::User => "user",
            UserRole::Guest => "guest",
            UserRole::Custom(s) => s.as_str(),
        };
        serializer.serialize_str(role_str)
    }
}

impl<'de> Deserialize<'de> for UserRole {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let s = String::deserialize(deserializer)?;
        Ok(match s.as_str() {
            "admin" => UserRole::Admin,
            "user" => UserRole::User,
            "guest" => UserRole::Guest,
            _ => UserRole::Custom(s),
        })
    }
}

// Money amount with custom serialization
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Money {
    amount_cents: i64,
}

impl Money {
    pub fn from_dollars(dollars: f64) -> Self {
        Self {
            amount_cents: (dollars * 100.0).round() as i64,
        }
    }

    pub fn to_dollars(&self) -> f64 {
        self.amount_cents as f64 / 100.0
    }
}

impl Serialize for Money {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_f64(self.to_dollars())
    }
}

impl<'de> Deserialize<'de> for Money {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let dollars = f64::deserialize(deserializer)?;
        Ok(Money::from_dollars(dollars))
    }
}

// Complex nested structure
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct User {
    pub id: String,
    pub email: String,
    
    #[serde(skip_serializing_if = "Option::is_none")]
    pub full_name: Option<String>,
    
    pub role: UserRole,
    
    #[serde(with = "chrono::serde::ts_seconds")]
    pub created_at: DateTime<Utc>,
    
    #[serde(
        serialize_with = "serialize_date",
        deserialize_with = "deserialize_date"
    )]
    pub birth_date: NaiveDate,
    
    #[serde(default)]
    pub preferences: UserPreferences,
    
    #[serde(skip_serializing_if = "Vec::is_empty", default)]
    pub tags: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
pub struct UserPreferences {
    #[serde(default = "default_theme")]
    pub theme: String,
    
    #[serde(default = "default_true")]
    pub notifications_enabled: bool,
    
    #[serde(default)]
    pub custom_settings: HashMap<String, serde_json::Value>,
}

fn default_theme() -> String {
    "light".to_string()
}

fn default_true() -> bool {
    true
}

// Transaction with polymorphic payment method
#[derive(Debug, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum PaymentMethod {
    CreditCard {
        card_number: String,
        expiry: String,
        cvv: String,
    },
    PayPal {
        email: String,
    },
    BankTransfer {
        account_number: String,
        routing_number: String,
    },
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Transaction {
    pub id: String,
    pub amount: Money,
    pub currency: String,
    
    #[serde(flatten)]
    pub payment_method: PaymentMethod,
    
    pub status: TransactionStatus,
    
    #[serde(with = "chrono::serde::ts_milliseconds")]
    pub timestamp: DateTime<Utc>,
    
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<HashMap<String, String>>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum TransactionStatus {
    Pending,
    Completed,
    Failed,
    Refunded,
}

// API Response wrapper with generics
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ApiResponse<T> {
    pub success: bool,
    
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<T>,
    
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<ApiError>,
    
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ApiError {
    pub code: String,
    pub message: String,
    
    #[serde(skip_serializing_if = "Option::is_none")]
    pub details: Option<serde_json::Value>,
}

impl<T> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
            timestamp: Utc::now(),
        }
    }

    pub fn error(code: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(ApiError {
                code: code.into(),
                message: message.into(),
                details: None,
            }),
            timestamp: Utc::now(),
        }
    }
}

// Example usage and tests
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_user_serialization() {
        let user = User {
            id: "123".to_string(),
            email: "user@example.com".to_string(),
            full_name: Some("John Doe".to_string()),
            role: UserRole::Admin,
            created_at: Utc::now(),
            birth_date: NaiveDate::from_ymd_opt(1990, 1, 1).unwrap(),
            preferences: UserPreferences {
                theme: "dark".to_string(),
                notifications_enabled: true,
                custom_settings: HashMap::new(),
            },
            tags: vec!["vip".to_string(), "verified".to_string()],
        };

        let json = serde_json::to_string_pretty(&user).unwrap();
        println!("Serialized user:
{}", json);

        let deserialized: User = serde_json::from_str(&json).unwrap();
        assert_eq!(user.id, deserialized.id);
        assert_eq!(user.role, deserialized.role);
    }

    #[test]
    fn test_transaction_with_payment_methods() {
        let transaction = Transaction {
            id: "txn_123".to_string(),
            amount: Money::from_dollars(99.99),
            currency: "USD".to_string(),
            payment_method: PaymentMethod::CreditCard {
                card_number: "****1234".to_string(),
                expiry: "12/25".to_string(),
                cvv: "***".to_string(),
            },
            status: TransactionStatus::Completed,
            timestamp: Utc::now(),
            metadata: None,
        };

        let json = serde_json::to_string_pretty(&transaction).unwrap();
        println!("Serialized transaction:
{}", json);

        let deserialized: Transaction = serde_json::from_str(&json).unwrap();
        assert_eq!(transaction.id, deserialized.id);
        assert_eq!(transaction.status, deserialized.status);
    }

    #[test]
    fn test_api_response() {
        let response = ApiResponse::success(vec!["item1", "item2"]);
        let json = serde_json::to_string_pretty(&response).unwrap();
        println!("Success response:
{}", json);

        let error_response: ApiResponse<()> = ApiResponse::error("NOT_FOUND", "Resource not found");
        let error_json = serde_json::to_string_pretty(&error_response).unwrap();
        println!("Error response:
{}", error_json);
    }
}
""",
        "category": 'rust',
        "subcategory": 'serde',
        "tags": ['api', 'deserialization', 'form', 'json', 'orm', 'response', 'routing']
    }
]
