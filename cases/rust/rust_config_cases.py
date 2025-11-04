RUST_CONFIG_CASES = [
    {
        "problem": """
Configuration management with multiple formats (TOML, YAML, JSON) and environment variable overrides.
""",
        "solution": """
use config::{Config, ConfigError, Environment, File, FileFormat};
use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct AppConfig {
    pub server: ServerConfig,
    pub database: DatabaseConfig,
    pub logging: LoggingConfig,
    pub features: FeaturesConfig,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
    pub workers: usize,
    pub timeout_seconds: u64,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct DatabaseConfig {
    pub url: String,
    pub max_connections: u32,
    pub min_connections: u32,
    pub connect_timeout_seconds: u64,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct LoggingConfig {
    pub level: String,
    pub format: String,
    pub output: String,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct FeaturesConfig {
    pub authentication: bool,
    pub caching: bool,
    pub rate_limiting: bool,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            server: ServerConfig {
                host: "127.0.0.1".to_string(),
                port: 8080,
                workers: 4,
                timeout_seconds: 30,
            },
            database: DatabaseConfig {
                url: "postgres://localhost/mydb".to_string(),
                max_connections: 10,
                min_connections: 2,
                connect_timeout_seconds: 5,
            },
            logging: LoggingConfig {
                level: "info".to_string(),
                format: "json".to_string(),
                output: "stdout".to_string(),
            },
            features: FeaturesConfig {
                authentication: true,
                caching: true,
                rate_limiting: true,
            },
        }
    }
}

pub struct ConfigLoader;

impl ConfigLoader {
    pub fn load() -> Result<AppConfig, ConfigError> {
        let mut builder = Config::builder()
            // Start with default values
            .add_source(Config::try_from(&AppConfig::default())?);

        // Load from config file if it exists
        if Path::new("config.toml").exists() {
            builder = builder.add_source(File::new("config", FileFormat::Toml));
        } else if Path::new("config.yaml").exists() {
            builder = builder.add_source(File::new("config", FileFormat::Yaml));
        } else if Path::new("config.json").exists() {
            builder = builder.add_source(File::new("config", FileFormat::Json));
        }

        // Override with environment variables
        // APP_SERVER__PORT=9000 will override server.port
        builder = builder.add_source(
            Environment::with_prefix("APP")
                .separator("__")
                .try_parsing(true)
        );

        let config = builder.build()?;
        config.try_deserialize()
    }

    pub fn load_from_file(path: impl AsRef<Path>) -> Result<AppConfig, ConfigError> {
        let path = path.as_ref();
        let format = Self::detect_format(path)?;

        Config::builder()
            .add_source(File::from(path).format(format))
            .build()?
            .try_deserialize()
    }

    pub fn load_with_overrides(
        base_path: impl AsRef<Path>,
        env: &str,
    ) -> Result<AppConfig, ConfigError> {
        let base_path = base_path.as_ref();
        let format = Self::detect_format(base_path)?;

        let mut builder = Config::builder()
            // Load base config
            .add_source(File::from(base_path).format(format.clone()));

        // Load environment-specific config
        let env_path = base_path.with_file_name(format!("config.{}.toml", env));
        if env_path.exists() {
            builder = builder.add_source(File::from(env_path).format(format));
        }

        // Override with environment variables
        builder = builder.add_source(
            Environment::with_prefix("APP")
                .separator("__")
                .try_parsing(true)
        );

        builder.build()?.try_deserialize()
    }

    fn detect_format(path: &Path) -> Result<FileFormat, ConfigError> {
        path.extension()
            .and_then(|ext| ext.to_str())
            .and_then(|ext| match ext {
                "toml" => Some(FileFormat::Toml),
                "yaml" | "yml" => Some(FileFormat::Yaml),
                "json" => Some(FileFormat::Json),
                _ => None,
            })
            .ok_or_else(|| ConfigError::Message("Unsupported file format".to_string()))
    }

    pub fn save(config: &AppConfig, path: impl AsRef<Path>) -> anyhow::Result<()> {
        let path = path.as_ref();
        let format = Self::detect_format(path)?;

        let content = match format {
            FileFormat::Toml => toml::to_string_pretty(config)?,
            FileFormat::Yaml => serde_yaml::to_string(config)?,
            FileFormat::Json => serde_json::to_string_pretty(config)?,
            _ => anyhow::bail!("Unsupported format"),
        };

        std::fs::write(path, content)?;
        Ok(())
    }
}

// Validation
impl AppConfig {
    pub fn validate(&self) -> Result<(), Vec<String>> {
        let mut errors = Vec::new();

        if self.server.port == 0 {
            errors.push("Server port cannot be 0".to_string());
        }

        if self.server.workers == 0 {
            errors.push("Server workers must be at least 1".to_string());
        }

        if self.database.max_connections < self.database.min_connections {
            errors.push("Max connections must be >= min connections".to_string());
        }

        if !["error", "warn", "info", "debug", "trace"].contains(&self.logging.level.as_str()) {
            errors.push(format!("Invalid log level: {}", self.logging.level));
        }

        if errors.is_empty() {
            Ok(())
        } else {
            Err(errors)
        }
    }
}

// Hot-reload support
use std::sync::{Arc, RwLock};
use notify::{Watcher, RecursiveMode, Event};

pub struct HotReloadConfig {
    config: Arc<RwLock<AppConfig>>,
    _watcher: notify::RecommendedWatcher,
}

impl HotReloadConfig {
    pub fn new(config_path: impl AsRef<Path>) -> anyhow::Result<Self> {
        let config_path = config_path.as_ref().to_path_buf();
        let initial_config = ConfigLoader::load_from_file(&config_path)?;
        let config = Arc::new(RwLock::new(initial_config));
        let config_clone = config.clone();

        let mut watcher = notify::recommended_watcher(move |res: Result<Event, notify::Error>| {
            match res {
                Ok(event) => {
                    if event.kind.is_modify() {
                        if let Ok(new_config) = ConfigLoader::load_from_file(&config_path) {
                            if let Ok(mut cfg) = config_clone.write() {
                                *cfg = new_config;
                                println!("Configuration reloaded");
                            }
                        }
                    }
                }
                Err(e) => println!("Watch error: {:?}", e),
            }
        })?;

        watcher.watch(config_path.as_ref(), RecursiveMode::NonRecursive)?;

        Ok(Self {
            config,
            _watcher: watcher,
        })
    }

    pub fn get(&self) -> AppConfig {
        self.config.read().unwrap().clone()
    }
}

// Example usage
fn main() -> anyhow::Result<()> {
    // Load configuration
    let config = ConfigLoader::load()?;
    println!("Configuration loaded:");
    println!("  Server: {}:{}", config.server.host, config.server.port);
    println!("  Database: {}", config.database.url);
    println!("  Log level: {}", config.logging.level);

    // Validate
    match config.validate() {
        Ok(_) => println!("Configuration is valid"),
        Err(errors) => {
            println!("Configuration errors:");
            for error in errors {
                println!("  - {}", error);
            }
        }
    }

    // Save to file
    ConfigLoader::save(&config, "config.example.toml")?;
    println!("Configuration saved to config.example.toml");

    // Load with environment overrides
    let config = ConfigLoader::load_with_overrides("config.toml", "production")?;
    println!("Production config loaded");

    Ok(())
}
""",
        "category": "rust",
        "subcategory": "config",
        "tags": [
            "auth",
            "authentication",
            "caching",
            "config",
            "database",
            "event",
            "form",
        ],
    }
]
