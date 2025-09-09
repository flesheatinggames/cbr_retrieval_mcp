# CBR MCP Server Configuration Templates

This directory contains configuration templates for the CBR MCP Server. These files provide ready-to-use configurations for different deployment scenarios.

## Quick Start

1. **Copy the template you need**:
   ```bash
   # For development
   cp development.yaml ../cbr_config.yaml
   
   # For production
   cp production.yaml ../cbr_config.yaml
   
   # For Docker
   cp docker.yaml ../cbr_config.yaml
   
   # For environment variables
   cp .env.template ../.env
   ```

2. **Customize the configuration** by editing the copied file

3. **Start the server**:
   ```bash
   # With YAML configuration
   cbr-mcp-server --config cbr_config.yaml
   
   # With environment variables
   source .env && cbr-mcp-server
   ```

## Available Templates

### Configuration Files

- **`cbr_config.yaml.template`** - Complete template with all available options and documentation
- **`development.yaml`** - Development-friendly settings with debug logging and relaxed limits
- **`production.yaml`** - Production-optimized settings with security and performance tuning
- **`docker.yaml`** - Container deployment configuration with appropriate paths and settings

### Environment Variables

- **`.env.template`** - Complete environment variables template with all CBR_ prefixed variables

## Configuration Priority

The server loads configuration in this order (highest to lowest priority):

1. **Environment Variables** (CBR_ prefixed)
2. **YAML Configuration File** (specified with --config)
3. **Default Values** (built-in)

## Key Configuration Areas

### Core Server Settings
- Database path and collection name
- Embedding model selection
- Query defaults (max results, similarity thresholds)

### Enhanced Logging
- Log levels and formats
- File rotation and cleanup
- Performance and request correlation logging

### System Monitoring
- CPU, memory, and disk thresholds
- Monitoring intervals and retention
- Alert configuration

### Health Dashboard
- Port and host binding
- WebSocket settings
- Security headers

### Production Features
- Authentication and API keys
- Rate limiting
- Caching and performance optimization
- Error recovery and circuit breaker

## Customization Tips

### Development Setup
- Use `development.yaml` as starting point
- Enable debug logging for troubleshooting
- Disable authentication for easier testing
- Use relaxed resource thresholds

### Production Deployment
- Start with `production.yaml`
- Configure authentication with secure API keys
- Set appropriate resource monitoring thresholds
- Enable all production features (caching, rate limiting, etc.)

### Container Deployment
- Use `docker.yaml` for container environments
- Mount `/app/data` volume for persistence
- Use JSON logging for log aggregation
- Configure appropriate resource limits

## Environment Variables Reference

All environment variables use the `CBR_` prefix. Key variables include:

- `CBR_DATABASE_PATH` - ChromaDB database directory
- `CBR_LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `CBR_DASHBOARD_PORT` - Health dashboard port
- `CBR_REQUIRE_AUTH` - Enable authentication
- `CBR_API_KEYS` - Comma-separated API keys

See `.env.template` for complete list with descriptions.

## Configuration Validation

The server validates configuration at startup and provides helpful error messages for:
- Invalid file paths
- Out-of-range values
- Missing required settings
- Port conflicts

## Support

For detailed configuration documentation, see:
- `Documentation/CBR-MCP-Server-Configuration-Guide.md`
- Individual template files contain extensive comments
- Use `cbr-mcp-server --help` for command-line options

## Examples

### Loading Custom Configuration
```bash
# Load specific configuration file
cbr-mcp-server --config config/production.yaml

# Override with environment variables
CBR_LOG_LEVEL=DEBUG cbr-mcp-server --config config/production.yaml
```

### Configuration Testing
```bash
# Validate configuration without starting
cbr-mcp-server --config config/production.yaml --validate-only

# Test configuration with dry run
cbr-mcp-server --config config/production.yaml --dry-run
```