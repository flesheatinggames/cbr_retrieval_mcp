RUST_REGEX_CASES = [
    {
        "problem": """
Advanced regex pattern matching with validation, extraction, and text processing.
""",
        "solution": r"""
use regex::{Regex, RegexBuilder, Captures};
use lazy_static::lazy_static;
use std::collections::HashMap;

// Pre-compiled regexes using lazy_static
lazy_static! {
    static ref EMAIL_REGEX: Regex = Regex::new(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    ).unwrap();
    
    static ref PHONE_REGEX: Regex = Regex::new(
        r"^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$"
    ).unwrap();
    
    static ref URL_REGEX: Regex = Regex::new(
        r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)"
    ).unwrap();
    
    static ref IPV4_REGEX: Regex = Regex::new(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    ).unwrap();
    
    static ref CREDIT_CARD_REGEX: Regex = Regex::new(
        r"^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})$"
    ).unwrap();
}

// Validation functions
pub struct Validator;

impl Validator {
    pub fn is_valid_email(email: &str) -> bool {
        EMAIL_REGEX.is_match(email)
    }

    pub fn is_valid_phone(phone: &str) -> bool {
        PHONE_REGEX.is_match(phone)
    }

    pub fn is_valid_url(url: &str) -> bool {
        URL_REGEX.is_match(url)
    }

    pub fn is_valid_ipv4(ip: &str) -> bool {
        IPV4_REGEX.is_match(ip)
    }

    pub fn is_valid_credit_card(number: &str) -> bool {
        let cleaned = number.replace(|c: char| c.is_whitespace() || c == '-', "");
        CREDIT_CARD_REGEX.is_match(&cleaned)
    }

    pub fn validate_password(password: &str) -> Result<(), Vec<String>> {
        let mut errors = Vec::new();

        if password.len() < 8 {
            errors.push("Password must be at least 8 characters long".to_string());
        }

        if !Regex::new(r"[A-Z]").unwrap().is_match(password) {
            errors.push("Password must contain at least one uppercase letter".to_string());
        }

        if !Regex::new(r"[a-z]").unwrap().is_match(password) {
            errors.push("Password must contain at least one lowercase letter".to_string());
        }

        if !Regex::new(r"\d").unwrap().is_match(password) {
            errors.push("Password must contain at least one digit".to_string());
        }

        if !Regex::new(r"[!@#$%^&*(),.?":{}|<>]").unwrap().is_match(password) {
            errors.push("Password must contain at least one special character".to_string());
        }

        if errors.is_empty() {
            Ok(())
        } else {
            Err(errors)
        }
    }
}

// Text extraction
pub struct TextExtractor;

impl TextExtractor {
    pub fn extract_emails(text: &str) -> Vec<String> {
        EMAIL_REGEX
            .find_iter(text)
            .map(|m| m.as_str().to_string())
            .collect()
    }

    pub fn extract_urls(text: &str) -> Vec<String> {
        URL_REGEX
            .find_iter(text)
            .map(|m| m.as_str().to_string())
            .collect()
    }

    pub fn extract_phone_numbers(text: &str) -> Vec<String> {
        PHONE_REGEX
            .find_iter(text)
            .map(|m| m.as_str().to_string())
            .collect()
    }

    pub fn extract_hashtags(text: &str) -> Vec<String> {
        let hashtag_regex = Regex::new(r"#[\w]+").unwrap();
        hashtag_regex
            .find_iter(text)
            .map(|m| m.as_str().to_string())
            .collect()
    }

    pub fn extract_mentions(text: &str) -> Vec<String> {
        let mention_regex = Regex::new(r"@[\w]+").unwrap();
        mention_regex
            .find_iter(text)
            .map(|m| m.as_str().to_string())
            .collect()
    }
}

// Template replacement
pub struct TemplateEngine {
    variables: HashMap<String, String>,
}

impl TemplateEngine {
    pub fn new() -> Self {
        Self {
            variables: HashMap::new(),
        }
    }

    pub fn set_variable(&mut self, key: impl Into<String>, value: impl Into<String>) {
        self.variables.insert(key.into(), value.into());
    }

    pub fn render(&self, template: &str) -> String {
        let var_regex = Regex::new(r"\{\{(\w+)\}\}").unwrap();
        
        var_regex.replace_all(template, |caps: &Captures| {
            let var_name = &caps[1];
            self.variables
                .get(var_name)
                .cloned()
                .unwrap_or_else(|| format!("{{{{{}}} }}", var_name))
        }).to_string()
    }

    pub fn render_with_defaults(&self, template: &str, defaults: &HashMap<String, String>) -> String {
        let var_regex = Regex::new(r"\{\{(\w+)\}\}").unwrap();
        
        var_regex.replace_all(template, |caps: &Captures| {
            let var_name = &caps[1];
            self.variables
                .get(var_name)
                .or_else(|| defaults.get(var_name))
                .cloned()
                .unwrap_or_else(|| format!("{{{{{}}} }}", var_name))
        }).to_string()
    }
}

// Text sanitization
pub struct TextSanitizer;

impl TextSanitizer {
    pub fn remove_html_tags(text: &str) -> String {
        let html_regex = Regex::new(r"<[^>]*>").unwrap();
        html_regex.replace_all(text, "").to_string()
    }

    pub fn remove_extra_whitespace(text: &str) -> String {
        let whitespace_regex = Regex::new(r"\s+").unwrap();
        whitespace_regex.replace_all(text.trim(), " ").to_string()
    }

    pub fn mask_sensitive_data(text: &str) -> String {
        let mut result = text.to_string();

        // Mask credit card numbers
        let cc_regex = Regex::new(r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}").unwrap();
        result = cc_regex.replace_all(&result, "****-****-****-****").to_string();

        // Mask SSN
        let ssn_regex = Regex::new(r"\d{3}-\d{2}-\d{4}").unwrap();
        result = ssn_regex.replace_all(&result, "***-**-****").to_string();

        // Mask email addresses
        let email_regex = Regex::new(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}").unwrap();
        result = email_regex.replace_all(&result, |caps: &Captures| {
            let email = caps.get(0).unwrap().as_str();
            let at_pos = email.find('@').unwrap();
            let (local, domain) = email.split_at(at_pos);
            format!("{}***{}", &local[..local.len().min(2)], domain)
        }).to_string();

        result
    }

    pub fn normalize_phone_number(phone: &str) -> Option<String> {
        if let Some(caps) = PHONE_REGEX.captures(phone) {
            Some(format!(
                "({}) {}-{}",
                &caps[1], &caps[2], &caps[3]
            ))
        } else {
            None
        }
    }
}

// Log parsing
pub struct LogParser;

#[derive(Debug)]
pub struct LogEntry {
    pub timestamp: String,
    pub level: String,
    pub component: String,
    pub message: String,
}

impl LogParser {
    pub fn parse_structured_log(line: &str) -> Option<LogEntry> {
        let log_regex = Regex::new(
            r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+\[(\w+)\]\s+\[([^\]]+)\]\s+(.*)$"
        ).unwrap();

        log_regex.captures(line).map(|caps| LogEntry {
            timestamp: caps[1].to_string(),
            level: caps[2].to_string(),
            component: caps[3].to_string(),
            message: caps[4].to_string(),
        })
    }

    pub fn extract_error_codes(text: &str) -> Vec<String> {
        let error_regex = Regex::new(r"(?i)error\s+code:\s*(\w+)").unwrap();
        error_regex
            .captures_iter(text)
            .map(|caps| caps[1].to_string())
            .collect()
    }
}

// Case-insensitive search with highlighting
pub fn highlight_matches(text: &str, search_term: &str) -> String {
    let pattern = format!("(?i){}", regex::escape(search_term));
    let regex = RegexBuilder::new(&pattern)
        .case_insensitive(true)
        .build()
        .unwrap();

    regex.replace_all(text, |caps: &Captures| {
        format!("<mark>{}</mark>", &caps[0])
    }).to_string()
}

// Example usage
fn main() {
    // Validation
    println!("Email validation:");
    println!("  test@example.com: {}", Validator::is_valid_email("test@example.com"));
    println!("  invalid.email: {}", Validator::is_valid_email("invalid.email"));

    // Extraction
    let text = "Contact us at support@example.com or sales@example.com. 
                Visit https://example.com for more info. 
                Call us at (555) 123-4567 or +1-555-987-6543.
                Follow us on #rust and #programming. Mention @rustlang!";

    println!("\nExtracted emails: {:?}", TextExtractor::extract_emails(text));
    println!("Extracted URLs: {:?}", TextExtractor::extract_urls(text));
    println!("Extracted phones: {:?}", TextExtractor::extract_phone_numbers(text));
    println!("Extracted hashtags: {:?}", TextExtractor::extract_hashtags(text));
    println!("Extracted mentions: {:?}", TextExtractor::extract_mentions(text));

    // Template rendering
    let mut engine = TemplateEngine::new();
    engine.set_variable("name", "John");
    engine.set_variable("age", "30");
    let template = "Hello {{name}}, you are {{age}} years old!";
    println!("\nRendered template: {}", engine.render(template));

    // Sanitization
    let sensitive = "My credit card is 4532-1234-5678-9010 and SSN is 123-45-6789. 
                     Email: john.doe@example.com";
    println!("\nMasked data: {}", TextSanitizer::mask_sensitive_data(sensitive));

    // Phone normalization
    if let Some(normalized) = TextSanitizer::normalize_phone_number("555-123-4567") {
        println!("Normalized phone: {}", normalized);
    }

    // Highlighting
    let text_to_search = "The quick brown fox jumps over the lazy dog. The FOX is quick!";
    println!("\nHighlighted: {}", highlight_matches(text_to_search, "fox"));
}
""",
        "category": "rust",
        "subcategory": "regex",
        "tags": ["form", "html", "http", "orm", "parser", "regex", "rust"],
    }
]
