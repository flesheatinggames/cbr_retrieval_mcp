
RUST_CLAP_CASES = [
    {
        "problem": """
A CLI application using clap with subcommands, arguments, environment variables, and configuration file support.
""",
        "solution": """
use clap::{Parser, Subcommand, Args, ValueEnum};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use anyhow::{Context, Result};

#[derive(Debug, Clone, ValueEnum)]
pub enum OutputFormat {
    Json,
    Yaml,
    Table,
    Csv,
}

#[derive(Debug, Clone, ValueEnum)]
pub enum LogLevel {
    Error,
    Warn,
    Info,
    Debug,
    Trace,
}

#[derive(Parser, Debug)]
#[command(name = "myapp")]
#[command(author = "Your Name <your@email.com>")]
#[command(version = "1.0")]
#[command(about = "A comprehensive CLI application", long_about = None)]
#[command(propagate_version = true)]
pub struct Cli {
    /// Configuration file path
    #[arg(short, long, value_name = "FILE", env = "MYAPP_CONFIG")]
    pub config: Option<PathBuf>,

    /// Output format
    #[arg(short, long, value_enum, default_value = "table")]
    pub output: OutputFormat,

    /// Log level
    #[arg(short, long, value_enum, default_value = "info", env = "MYAPP_LOG_LEVEL")]
    pub log_level: LogLevel,

    /// Enable verbose mode
    #[arg(short, long)]
    pub verbose: bool,

    /// Disable colored output
    #[arg(long)]
    pub no_color: bool,

    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand, Debug)]
pub enum Commands {
    /// User management commands
    User(UserCommand),
    
    /// Database operations
    Database(DatabaseCommand),
    
    /// Configuration management
    Config(ConfigCommand),
    
    /// Server operations
    Server(ServerCommand),
}

#[derive(Args, Debug)]
pub struct UserCommand {
    #[command(subcommand)]
    pub action: UserAction,
}

#[derive(Subcommand, Debug)]
pub enum UserAction {
    /// List all users
    List {
        /// Number of users to display
        #[arg(short, long, default_value = "10")]
        limit: usize,
        
        /// Page number
        #[arg(short, long, default_value = "1")]
        page: usize,
        
        /// Filter by status
        #[arg(short, long)]
        status: Option<String>,
        
        /// Search query
        #[arg(short = 'q', long)]
        search: Option<String>,
    },
    
    /// Get user details
    Get {
        /// User ID or email
        #[arg(value_name = "IDENTIFIER")]
        id: String,
        
        /// Include related data
        #[arg(short, long)]
        include: Vec<String>,
    },
    
    /// Create a new user
    Create {
        /// User name
        #[arg(short, long)]
        name: String,
        
        /// User email
        #[arg(short, long)]
        email: String,
        
        /// User role
        #[arg(short, long, default_value = "user")]
        role: String,
        
        /// Skip email verification
        #[arg(long)]
        no_verify: bool,
    },
    
    /// Update user information
    Update {
        /// User ID
        id: String,
        
        /// New name
        #[arg(short, long)]
        name: Option<String>,
        
        /// New email
        #[arg(short, long)]
        email: Option<String>,
        
        /// New role
        #[arg(short, long)]
        role: Option<String>,
    },
    
    /// Delete a user
    Delete {
        /// User ID
        id: String,
        
        /// Force deletion without confirmation
        #[arg(short, long)]
        force: bool,
    },
}

#[derive(Args, Debug)]
pub struct DatabaseCommand {
    #[command(subcommand)]
    pub action: DatabaseAction,
}

#[derive(Subcommand, Debug)]
pub enum DatabaseAction {
    /// Run database migrations
    Migrate {
        /// Migration version (or 'latest')
        #[arg(default_value = "latest")]
        version: String,
        
        /// Dry run (don't execute)
        #[arg(short, long)]
        dry_run: bool,
    },
    
    /// Rollback migrations
    Rollback {
        /// Number of migrations to rollback
        #[arg(short, long, default_value = "1")]
        steps: usize,
    },
    
    /// Backup database
    Backup {
        /// Output file path
        #[arg(short, long)]
        output: PathBuf,
        
        /// Compress backup
        #[arg(short, long)]
        compress: bool,
    },
    
    /// Restore database from backup
    Restore {
        /// Backup file path
        input: PathBuf,
        
        /// Force restore without confirmation
        #[arg(short, long)]
        force: bool,
    },
    
    /// Seed database with sample data
    Seed {
        /// Seed file or preset name
        #[arg(default_value = "default")]
        preset: String,
        
        /// Clear existing data first
        #[arg(short, long)]
        clean: bool,
    },
}

#[derive(Args, Debug)]
pub struct ConfigCommand {
    #[command(subcommand)]
    pub action: ConfigAction,
}

#[derive(Subcommand, Debug)]
pub enum ConfigAction {
    /// Show current configuration
    Show {
        /// Show only specific key
        key: Option<String>,
    },
    
    /// Set configuration value
    Set {
        /// Configuration key
        key: String,
        
        /// Configuration value
        value: String,
    },
    
    /// Initialize configuration file
    Init {
        /// Force overwrite existing config
        #[arg(short, long)]
        force: bool,
    },
    
    /// Validate configuration
    Validate,
}

#[derive(Args, Debug)]
pub struct ServerCommand {
    #[command(subcommand)]
    pub action: ServerAction,
}

#[derive(Subcommand, Debug)]
pub enum ServerAction {
    /// Start the server
    Start {
        /// Server host
        #[arg(short = 'H', long, default_value = "0.0.0.0")]
        host: String,
        
        /// Server port
        #[arg(short, long, default_value = "3000", env = "MYAPP_PORT")]
        port: u16,
        
        /// Number of worker threads
        #[arg(short, long)]
        workers: Option<usize>,
        
        /// Run in background
        #[arg(short, long)]
        daemon: bool,
    },
    
    /// Stop the server
    Stop {
        /// Force stop
        #[arg(short, long)]
        force: bool,
    },
    
    /// Restart the server
    Restart {
        /// Graceful restart
        #[arg(short, long)]
        graceful: bool,
    },
    
    /// Show server status
    Status,
}

// Configuration file structure
#[derive(Debug, Serialize, Deserialize)]
pub struct Config {
    pub database_url: String,
    pub api_key: Option<String>,
    pub timeout: Option<u64>,
    pub retry_attempts: Option<u32>,
    pub features: ConfigFeatures,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ConfigFeatures {
    pub authentication: bool,
    pub caching: bool,
    pub logging: bool,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            database_url: "postgres://localhost/myapp".to_string(),
            api_key: None,
            timeout: Some(30),
            retry_attempts: Some(3),
            features: ConfigFeatures {
                authentication: true,
                caching: true,
                logging: true,
            },
        }
    }
}

impl Config {
    pub fn load_from_file(path: &PathBuf) -> Result<Self> {
        let content = std::fs::read_to_string(path)
            .with_context(|| format!("Failed to read config file: {:?}", path))?;
        
        let config: Config = toml::from_str(&content)
            .with_context(|| "Failed to parse config file")?;
        
        Ok(config)
    }

    pub fn save_to_file(&self, path: &PathBuf) -> Result<()> {
        let content = toml::to_string_pretty(self)
            .context("Failed to serialize config")?;
        
        std::fs::write(path, content)
            .with_context(|| format!("Failed to write config file: {:?}", path))?;
        
        Ok(())
    }
}

// Main application logic
pub struct App {
    cli: Cli,
    config: Config,
}

impl App {
    pub fn new(cli: Cli) -> Result<Self> {
        let config = if let Some(config_path) = &cli.config {
            Config::load_from_file(config_path)?
        } else {
            Config::default()
        };

        Ok(Self { cli, config })
    }

    pub async fn run(&self) -> Result<()> {
        // Initialize logger based on cli options
        self.setup_logger();

        match &self.cli.command {
            Commands::User(cmd) => self.handle_user_command(cmd).await,
            Commands::Database(cmd) => self.handle_database_command(cmd).await,
            Commands::Config(cmd) => self.handle_config_command(cmd),
            Commands::Server(cmd) => self.handle_server_command(cmd).await,
        }
    }

    fn setup_logger(&self) {
        let level = match self.cli.log_level {
            LogLevel::Error => tracing::Level::ERROR,
            LogLevel::Warn => tracing::Level::WARN,
            LogLevel::Info => tracing::Level::INFO,
            LogLevel::Debug => tracing::Level::DEBUG,
            LogLevel::Trace => tracing::Level::TRACE,
        };

        tracing_subscriber::fmt()
            .with_max_level(level)
            .with_ansi(!self.cli.no_color)
            .init();
    }

    async fn handle_user_command(&self, cmd: &UserCommand) -> Result<()> {
        match &cmd.action {
            UserAction::List { limit, page, status, search } => {
                println!("Listing users (limit: {}, page: {})", limit, page);
                if let Some(s) = status {
                    println!("Filtering by status: {}", s);
                }
                if let Some(q) = search {
                    println!("Searching for: {}", q);
                }
                Ok(())
            }
            UserAction::Get { id, include } => {
                println!("Getting user: {}", id);
                if !include.is_empty() {
                    println!("Including: {:?}", include);
                }
                Ok(())
            }
            UserAction::Create { name, email, role, no_verify } => {
                println!("Creating user: {} <{}> (role: {})", name, email, role);
                if *no_verify {
                    println!("Skipping email verification");
                }
                Ok(())
            }
            UserAction::Update { id, name, email, role } => {
                println!("Updating user: {}", id);
                Ok(())
            }
            UserAction::Delete { id, force } => {
                println!("Deleting user: {}", id);
                if *force {
                    println!("Force deletion enabled");
                }
                Ok(())
            }
        }
    }

    async fn handle_database_command(&self, cmd: &DatabaseCommand) -> Result<()> {
        match &cmd.action {
            DatabaseAction::Migrate { version, dry_run } => {
                println!("Running migrations to version: {}", version);
                Ok(())
            }
            DatabaseAction::Rollback { steps } => {
                println!("Rolling back {} migration(s)", steps);
                Ok(())
            }
            DatabaseAction::Backup { output, compress } => {
                println!("Backing up to: {:?}", output);
                Ok(())
            }
            DatabaseAction::Restore { input, force } => {
                println!("Restoring from: {:?}", input);
                Ok(())
            }
            DatabaseAction::Seed { preset, clean } => {
                println!("Seeding database with preset: {}", preset);
                Ok(())
            }
        }
    }

    fn handle_config_command(&self, cmd: &ConfigCommand) -> Result<()> {
        match &cmd.action {
            ConfigAction::Show { key } => {
                if let Some(k) = key {
                    println!("Showing config key: {}", k);
                } else {
                    println!("Current configuration:");
                    println!("{}", toml::to_string_pretty(&self.config)?);
                }
                Ok(())
            }
            ConfigAction::Set { key, value } => {
                println!("Setting {} = {}", key, value);
                Ok(())
            }
            ConfigAction::Init { force } => {
                println!("Initializing configuration");
                Ok(())
            }
            ConfigAction::Validate => {
                println!("Configuration is valid!");
                Ok(())
            }
        }
    }

    async fn handle_server_command(&self, cmd: &ServerCommand) -> Result<()> {
        match &cmd.action {
            ServerAction::Start { host, port, workers, daemon } => {
                println!("Starting server on {}:{}", host, port);
                Ok(())
            }
            ServerAction::Stop { force } => {
                println!("Stopping server");
                Ok(())
            }
            ServerAction::Restart { graceful } => {
                println!("Restarting server");
                Ok(())
            }
            ServerAction::Status => {
                println!("Server status: Running");
                Ok(())
            }
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    let app = App::new(cli)?;
    app.run().await
}
""",
        "category": 'rust',
        "subcategory": 'clap',
        "tags": ['api', 'async', 'auth', 'authentication', 'caching', 'clap', 'csv']
    }
]
