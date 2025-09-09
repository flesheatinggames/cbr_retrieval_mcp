# CBR MCP Server Configuration Guide

> Last Updated: 2025-09-09
> Version: 1.0.0

## Overview

The CBR MCP Server provides a comprehensive configuration system supporting both YAML configuration files and environment variables. This guide covers all configuration options, provides templates and examples for different deployment scenarios, and explains how to optimize settings for development, production, and container environments.

## Configuration System Architecture

The CBR MCP Server uses a hierarchical configuration system with the following priority order (highest to lowest):

1. **Environment Variables** (CBR_ prefixed)
2. **YAML Configuration Files** 
3. **Default Values**

### Configuration Classes

The server implements several specialized configuration classes:

- **LogConfig**: Enhanced logging system configuration
- **CBRServerConfig**: Core server and CBR functionality
- **MonitoringConfig**: System resource monitoring
- **DashboardConfig**: Health dashboard settings
- **ServerConfig**: Production server features

## Environment Variables Reference

All environment variables use the `CBR_` prefix for consistency and namespace isolation.

### Core Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CBR_DATABASE_PATH` | `./db` | Path to ChromaDB database directory |
| `CBR_COLLECTION_NAME` | `code_solutions_case_base` | ChromaDB collection name |
| `CBR_EMBEDDING_MODEL` | `nomic-ai/nomic-embed-text-v1.5` | Sentence transformer model |
| `CBR_MAX_RESULTS_DEFAULT` | `10` | Default maximum results for queries |
| `CBR_SIMILARITY_THRESHOLD_DEFAULT` | `0.7` | Default similarity threshold (0.0-1.0) |
| `CBR_ENABLE_HEALTH_CHECKS` | `true` | Enable health monitoring endpoints |

### Enhanced Logging Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CBR_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CBR_LOG_FORMAT` | `json` | Log format (json, text, colored) |
| `CBR_LOG_FILE` | `null` | Log file path (optional) |
| `CBR_LOG_CONSOLE` | `true` | Enable console output |
| `CBR_LOG_CONSOLE_FORMAT` | `text` | Console format (json, text, colored) |
| `CBR_LOG_MAX_SIZE` | `10485760` | Max log file size in bytes (10MB) |
| `CBR_LOG_BACKUP_COUNT` | `5` | Number of backup log files |
| `CBR_LOG_ROTATION` | `true` | Enable log file rotation |
| `CBR_LOG_CLEANUP` | `true` | Enable automatic log cleanup |
| `CBR_LOG_COLORS` | `false` | Enable colored console output |
| `CBR_LOG_PERFORMANCE` | `true` | Enable performance logging |
| `CBR_LOG_CORRELATION` | `true` | Enable request correlation IDs |
| `CBR_LOG_THREAD_SAFE` | `true` | Thread-safe logging |
| `CBR_LOG_DISK_MONITORING` | `false` | Monitor disk space for logs |
| `CBR_LOG_MIN_FREE_SPACE` | `10.0` | Minimum free disk space percentage |
| `CBR_LOG_HANDLE_PERMISSIONS` | `true` | Handle log file permissions |

### Production Server Features

| Variable | Default | Description |
|----------|---------|-------------|
| `CBR_REQUIRE_AUTH` | `false` | Enable authentication |
| `CBR_API_KEYS` | `[]` | Comma-separated API keys |
| `CBR_ADMIN_KEYS` | `[]` | Comma-separated admin keys |
| `CBR_RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `CBR_RATE_LIMIT_REQUESTS` | `100` | Requests per time window |
| `CBR_RATE_LIMIT_WINDOW` | `3600` | Rate limit window in seconds |
| `CBR_MONITORING_PORT` | `8080` | Health dashboard port |
| `CBR_CACHE_ENABLED` | `true` | Enable result caching |
| `CBR_CACHE_TTL` | `3600` | Cache TTL in seconds |
| `CBR_MAX_RETRIES` | `3` | Maximum retry attempts |
| `CBR_CIRCUIT_BREAKER` | `true` | Enable circuit breaker |

### Health Dashboard Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CBR_DASHBOARD_HOST` | `localhost` | Dashboard host binding |
| `CBR_DASHBOARD_PORT` | `8080` | Dashboard port |
| `CBR_DASHBOARD_DEBUG` | `false` | Enable dashboard debug mode |
| `CBR_WEBSOCKET_ENABLED` | `true` | Enable WebSocket updates |
| `CBR_METRICS_INTERVAL` | `5` | Metrics update interval (seconds) |
| `CBR_SECURITY_HEADERS` | `true` | Enable security headers |

## YAML Configuration Structure

The CBR MCP Server supports YAML configuration files with the following structure:

### Complete YAML Configuration Template

```yaml
# CBR MCP Server Configuration Template
# Copy this file and customize for your environment

# Core CBR Configuration
database:
  path: "./db"                                    # ChromaDB database path
  collection_name: "code_solutions_case_base"    # Collection name
  embedding_model: "nomic-ai/nomic-embed-text-v1.5"  # Embedding model

# Query Defaults
query:
  max_results_default: 10           # Default maximum results
  similarity_threshold_default: 0.7 # Default similarity threshold (0.0-1.0)

# Enhanced Logging System
logging:
  level: "INFO"                     # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "json"                    # json, text, colored
  output_file: null                 # Optional log file path
  console_output: true              # Enable console output
  console_format: "text"            # Console format
  max_file_size: 10485760          # 10MB in bytes
  backup_count: 5                   # Number of backup files
  rotation_enabled: true            # Enable log rotation
  cleanup_enabled: true             # Enable log cleanup
  enable_colors: false              # Colored console output
  performance_logging: true         # Log performance metrics
  request_correlation: true         # Enable correlation IDs
  thread_safe: true                 # Thread-safe logging
  disk_space_monitoring: false      # Monitor disk space
  min_free_space_percent: 10.0     # Minimum free space %
  handle_permissions: true          # Handle file permissions

# System Resource Monitoring
monitoring:
  enabled: true                     # Enable monitoring
  interval: 30.0                    # Monitoring interval (seconds)
  db_path: "./monitoring.db"        # Monitoring database path
  retention_hours: 168              # Data retention (7 days)
  alert_cooldown: 300               # Alert cooldown (5 minutes)
  max_alerts_per_hour: 100         # Max alerts per hour
  
  # Resource thresholds
  thresholds:
    cpu:
      warning: 70.0                 # CPU warning threshold %
      critical: 85.0                # CPU critical threshold %
      emergency: 95.0               # CPU emergency threshold %
    memory:
      warning: 75.0                 # Memory warning threshold %
      critical: 90.0                # Memory critical threshold %
      emergency: 98.0               # Memory emergency threshold %
    disk:
      warning: 80.0                 # Disk warning threshold %
      critical: 90.0                # Disk critical threshold %
      emergency: 95.0               # Disk emergency threshold %

# Health Dashboard
dashboard:
  host: "localhost"                 # Dashboard host
  port: 8080                       # Dashboard port
  debug: false                     # Debug mode
  cors_origins:                    # CORS origins
    - "http://localhost:3000"
  websocket_enabled: true          # Enable WebSocket updates
  metrics_update_interval: 5       # Update interval (seconds)
  security_headers: true           # Enable security headers
  max_websocket_connections: 100   # Max WebSocket connections
  max_payload_size: 1048576       # Max payload size (1MB)

# Production Features
production:
  # Authentication
  require_auth: false              # Enable authentication
  api_keys: []                     # List of API keys
  admin_keys: []                   # List of admin keys
  
  # Rate Limiting
  rate_limit_enabled: true         # Enable rate limiting
  rate_limit_requests: 100         # Requests per window
  rate_limit_window: 3600         # Window size (seconds)
  
  # Performance
  cache_enabled: true              # Enable caching
  cache_ttl: 3600                 # Cache TTL (seconds)
  performance_monitoring: true     # Performance monitoring
  
  # Reliability
  retry_enabled: true              # Enable retries
  max_retries: 3                  # Maximum retry attempts
  circuit_breaker: true           # Enable circuit breaker
  
  # Input Validation
  input_validation: "strict"       # strict, normal, permissive
  sanitization: true              # Enable input sanitization
  max_query_length: 10000         # Maximum query length

# Health Checks
health:
  enabled: true                    # Enable health checks
  timeout: 30                     # Health check timeout (seconds)
```

## Configuration Examples

### Development Configuration

Create `development.yaml` for local development:

```yaml
# Development Configuration
database:
  path: "./dev_db"
  collection_name: "dev_case_base"

query:
  max_results_default: 20          # More results for exploration

logging:
  level: "DEBUG"                   # Verbose logging
  format: "text"                   # Human-readable format
  console_format: "colored"        # Colored output
  enable_colors: true
  output_file: "dev.log"          # Development log file

monitoring:
  interval: 10.0                   # More frequent monitoring
  thresholds:
    cpu:
      warning: 80.0                # Higher thresholds for dev
      critical: 90.0
      emergency: 98.0
    memory:
      warning: 85.0
      critical: 95.0
      emergency: 99.0

dashboard:
  debug: true                      # Enable debug features
  websocket_enabled: true
  metrics_update_interval: 2       # Frequent updates

production:
  require_auth: false              # No auth for development
  rate_limit_enabled: false        # No rate limits
  cache_enabled: false             # Disable cache for testing
  input_validation: "permissive"   # Relaxed validation
```

### Production Configuration

Create `production.yaml` for production deployment:

```yaml
# Production Configuration
database:
  path: "/opt/cbr/data/db"
  collection_name: "production_case_base"

query:
  max_results_default: 10
  similarity_threshold_default: 0.75  # Higher threshold for quality

logging:
  level: "INFO"
  format: "json"                   # Structured logging
  output_file: "/var/log/cbr/server.log"
  console_output: false            # No console in production
  max_file_size: 52428800         # 50MB
  backup_count: 10
  disk_space_monitoring: true      # Monitor disk space
  min_free_space_percent: 15.0

monitoring:
  enabled: true
  interval: 60.0                   # Less frequent monitoring
  db_path: "/opt/cbr/data/monitoring.db"
  retention_hours: 720            # 30 days retention
  
  thresholds:
    cpu:
      warning: 60.0                # Lower thresholds for production
      critical: 75.0
      emergency: 90.0
    memory:
      warning: 70.0
      critical: 85.0
      emergency: 95.0

dashboard:
  host: "0.0.0.0"                 # Bind to all interfaces
  port: 8080
  debug: false
  security_headers: true
  websocket_enabled: true
  max_websocket_connections: 50

production:
  require_auth: true               # Enable authentication
  api_keys:
    - "prod-api-key-1"
    - "prod-api-key-2"
  admin_keys:
    - "admin-key-secure"
  
  rate_limit_enabled: true
  rate_limit_requests: 500         # Higher limits for production
  rate_limit_window: 3600
  
  cache_enabled: true
  cache_ttl: 1800                 # 30 minutes
  
  max_retries: 5                  # More retries in production
  circuit_breaker: true
  input_validation: "strict"       # Strict validation
  max_query_length: 5000          # Smaller queries in production

health:
  enabled: true
  timeout: 15                     # Faster timeout
```

### Docker Configuration

Create `docker.yaml` for container deployment:

```yaml
# Docker Container Configuration
database:
  path: "/app/data/db"            # Container volume mount
  collection_name: "container_case_base"

logging:
  level: "INFO"
  format: "json"                  # JSON for log aggregation
  console_output: true            # Docker logs to stdout
  console_format: "json"
  output_file: null               # No file logging in container
  
monitoring:
  enabled: true
  interval: 30.0
  db_path: "/app/data/monitoring.db"
  thresholds:
    # Container-optimized thresholds
    cpu:
      warning: 70.0
      critical: 85.0
      emergency: 95.0
    memory:
      warning: 80.0               # Higher memory threshold for containers
      critical: 90.0
      emergency: 95.0

dashboard:
  host: "0.0.0.0"                # Bind to all interfaces
  port: 8080
  debug: false

production:
  require_auth: true
  rate_limit_enabled: true
  cache_enabled: true
  circuit_breaker: true
  input_validation: "strict"

health:
  enabled: true
  timeout: 10                    # Quick health checks for orchestration
```

### Environment Variables Template

Create `.env.template` for environment-based configuration:

```bash
# CBR MCP Server Environment Variables Template
# Copy to .env and customize for your environment

# Core Configuration
CBR_DATABASE_PATH=./db
CBR_COLLECTION_NAME=code_solutions_case_base
CBR_EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1.5
CBR_MAX_RESULTS_DEFAULT=10
CBR_SIMILARITY_THRESHOLD_DEFAULT=0.7
CBR_ENABLE_HEALTH_CHECKS=true

# Enhanced Logging
CBR_LOG_LEVEL=INFO
CBR_LOG_FORMAT=json
# CBR_LOG_FILE=./cbr_server.log
CBR_LOG_CONSOLE=true
CBR_LOG_CONSOLE_FORMAT=text
CBR_LOG_MAX_SIZE=10485760
CBR_LOG_BACKUP_COUNT=5
CBR_LOG_ROTATION=true
CBR_LOG_CLEANUP=true
CBR_LOG_COLORS=false
CBR_LOG_PERFORMANCE=true
CBR_LOG_CORRELATION=true
CBR_LOG_THREAD_SAFE=true
CBR_LOG_DISK_MONITORING=false
CBR_LOG_MIN_FREE_SPACE=10.0
CBR_LOG_HANDLE_PERMISSIONS=true

# Production Features
CBR_REQUIRE_AUTH=false
# CBR_API_KEYS=key1,key2,key3
# CBR_ADMIN_KEYS=admin1,admin2
CBR_RATE_LIMIT_ENABLED=true
CBR_RATE_LIMIT_REQUESTS=100
CBR_RATE_LIMIT_WINDOW=3600
CBR_MONITORING_PORT=8080
CBR_CACHE_ENABLED=true
CBR_CACHE_TTL=3600
CBR_MAX_RETRIES=3
CBR_CIRCUIT_BREAKER=true

# Health Dashboard
CBR_DASHBOARD_HOST=localhost
CBR_DASHBOARD_PORT=8080
CBR_DASHBOARD_DEBUG=false
CBR_WEBSOCKET_ENABLED=true
CBR_METRICS_INTERVAL=5
CBR_SECURITY_HEADERS=true
```

## Configuration Loading

The CBR MCP Server loads configuration in the following order:

1. **Default Values**: Built-in sensible defaults
2. **YAML File**: If specified with `--config` parameter
3. **Environment Variables**: Override YAML and defaults

### Loading YAML Configuration

```bash
# Load specific configuration file
cbr-mcp-server --config production.yaml

# Load from standard locations (checked in order)
cbr-mcp-server
# Checks: ./cbr_config.yaml, ./config/cbr_config.yaml, /etc/cbr/config.yaml
```

### Environment Variable Override Examples

```bash
# Override log level
export CBR_LOG_LEVEL=DEBUG

# Override database path
export CBR_DATABASE_PATH=/custom/db/path

# Enable authentication with API keys
export CBR_REQUIRE_AUTH=true
export CBR_API_KEYS="key1,key2,key3"

# Start server (environment variables override YAML)
cbr-mcp-server --config production.yaml
```

## Configuration Validation

The server validates configuration at startup and provides detailed error messages:

### Validation Features

- **Type Checking**: Ensures correct data types
- **Range Validation**: Validates numeric ranges and limits
- **Path Validation**: Checks file/directory paths exist and are writable
- **Dependency Validation**: Validates configuration dependencies
- **Security Validation**: Checks for insecure configurations

### Common Validation Errors

```
Configuration Error: database_path cannot be empty
Configuration Error: similarity_threshold_default must be between 0.0 and 1.0
Configuration Error: log_file directory is not writable
Configuration Error: monitoring_port conflicts with dashboard_port
Configuration Error: api_keys required when require_auth is true
```

## Performance Tuning

### Memory Optimization

```yaml
# Memory-optimized configuration
query:
  max_results_default: 5           # Limit result sets
  
monitoring:
  retention_hours: 24              # Shorter retention
  
production:
  cache_ttl: 1800                 # Shorter cache TTL
  max_query_length: 2000          # Limit query size
```

### High-Performance Configuration

```yaml
# High-performance configuration
database:
  # Use SSD path for database
  path: "/fast/ssd/cbr/db"

logging:
  # Disable verbose logging
  level: "WARNING"
  performance_logging: false
  
monitoring:
  # Less frequent monitoring
  interval: 120.0
  
production:
  # Aggressive caching
  cache_enabled: true
  cache_ttl: 7200
  
  # Higher rate limits
  rate_limit_requests: 1000
```

## Security Configuration

### Authentication Setup

```yaml
production:
  require_auth: true
  api_keys:
    - "secure-api-key-1"
    - "secure-api-key-2" 
  admin_keys:
    - "admin-secure-key"
  
  # Security features
  input_validation: "strict"
  sanitization: true
  max_query_length: 5000
```

### Security Environment Variables

```bash
# Load API keys from secure source
export CBR_API_KEYS=$(cat /etc/secrets/cbr_api_keys)
export CBR_ADMIN_KEYS=$(cat /etc/secrets/cbr_admin_keys)

# Enable strict security
export CBR_REQUIRE_AUTH=true
export CBR_INPUT_VALIDATION=strict
export CBR_SANITIZATION=true
```

## Troubleshooting Configuration

### Debug Configuration Loading

```bash
# Enable debug logging for configuration
export CBR_LOG_LEVEL=DEBUG
cbr-mcp-server --config your-config.yaml

# Check configuration validation
cbr-mcp-server --config your-config.yaml --validate-only
```

### Common Issues

1. **Permission Errors**: Ensure database and log paths are writable
2. **Port Conflicts**: Check dashboard and monitoring ports don't conflict
3. **Missing Dependencies**: Install required packages (psutil, structlog, etc.)
4. **Path Issues**: Use absolute paths for production deployments
5. **Memory Issues**: Reduce cache TTL and result limits for low-memory systems

### Configuration Testing

```bash
# Test configuration without starting server
cbr-mcp-server --config test.yaml --dry-run

# Validate configuration syntax
cbr-mcp-server --config test.yaml --validate-only --verbose
```

This comprehensive configuration guide provides everything needed to set up the CBR MCP Server for any environment, from development to production deployment.