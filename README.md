# CBR MCP Server

A Model Context Protocol (MCP) server that provides access to Case-Based Reasoning (CBR) functionality.

## Overview

This server converts the existing FastAPI-based CBR system to the MCP protocol, providing tools and resources for case-based reasoning operations. It integrates with ChromaDB for vector storage and uses sentence-transformers for embedding generation.

## Features

### MCP Tools
- **`cbr_retrieve`** - Retrieve relevant examples from the case base
- **`cbr_search_category`** - Search for cases within a specific category
- **`cbr_find_similar`** - Find cases similar to a given example

### MCP Resources
- **`cbr://categories`** - Get available categories from the case base
- **`cbr://examples/{id}`** - Get a specific example by ID
- **`cbr://stats`** - Get system statistics

## Production Features

The CBR MCP Server includes comprehensive production-grade features for enterprise deployment:

### Enhanced Logging & Monitoring
- **Structured Logging** - JSON-formatted logs with configurable verbosity levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Request Tracing** - Detailed logging of MCP tool calls with request IDs and correlation tracking
- **Performance Monitoring** - Real-time tracking of query latency, memory usage, and system performance
- **Log Rotation** - Automatic log file rotation and cleanup with configurable size limits
- **Multiple Output Formats** - Support for JSON, plain text, and colored console output

### Process Resilience & Error Recovery
- **Connection Management** - Automatic retry logic with exponential backoff for ChromaDB connections
- **Graceful Shutdown** - Clean resource cleanup on process termination (SIGTERM, SIGINT)
- **Session State Management** - Maintains session state across connection interruptions
- **Circuit Breaker Pattern** - Prevents cascading failures for external dependencies
- **Automatic Recovery** - Self-healing capabilities for ChromaDB and embedding service failures

### System Resource Monitoring
- **Real-time Metrics** - CPU, memory, and disk usage monitoring with configurable thresholds
- **Alert System** - Threshold breach notifications and warnings
- **Metrics Storage** - Historical metrics data with rolling window aggregation
- **Background Monitoring** - Non-intrusive monitoring thread with configurable polling intervals

### Configuration & Validation
- **Startup Validation** - Comprehensive checks for database paths, embedding models, and dependencies
- **YAML Configuration** - Support for configuration files with environment variable overrides
- **Environment Variables** - Full configuration via environment variables (CBR_ prefix)
- **Database Integrity** - Automatic ChromaDB consistency validation and repair procedures
- **Multi-format Config** - Support for both file-based and environment-based configuration

### Health Dashboard
- **Web Interface** - Real-time health dashboard accessible at localhost:8080 (configurable)
- **System Metrics** - Live graphs of CPU, memory, and performance metrics
- **Query Statistics** - Request patterns, success rates, and performance analytics
- **Health Indicators** - Server status, uptime, and dependency health checks
- **Auto-refresh** - Real-time updates with WebSocket connections

## Installation

### Basic Installation

```bash
# Install the package with development dependencies
pip install -e ".[dev]"
```

### Production Installation

```bash
# Install with production dependencies
pip install -e ".[dev]"

# Install additional production dependencies
pip install structlog psutil pyyaml
```

### System Requirements

- Python 3.8+
- ChromaDB for vector storage
- At least 2GB RAM recommended for embedding model
- Write access for database directory (./db by default)
- Port 8080 available for health dashboard (configurable)

## Dependencies

- **mcp** - Model Context Protocol implementation
- **chromadb** - Vector database for storing case examples
- **sentence-transformers** - For generating embeddings
- **pydantic** - Data validation
- **einops** - Tensor operations

## Usage

### Running the Server

```python
from cbr_mcp_server import create_server

# Create and run the server
server = create_server()
server.mcp.run(transport="stdio")
```

### Command Line

```bash
# Basic startup (uses environment variables)
python cbr_mcp_server.py

# Or use the installed script
cbr-mcp-server

# With configuration file
CBR_CONFIG_FILE="./cbr_config.yaml" python cbr_mcp_server.py

# With custom log level and monitoring port
CBR_LOG_LEVEL="DEBUG" CBR_MONITORING_PORT="8081" cbr-mcp-server

# Production mode with all monitoring enabled
CBR_LOG_LEVEL="INFO" \
CBR_LOG_FORMAT="json" \
CBR_MONITORING_PORT="8080" \
CBR_PERFORMANCE_MONITORING="true" \
CBR_HEALTH_CHECK_ENABLED="true" \
cbr-mcp-server
```

### MCP Tools Usage

#### Retrieve Relevant Examples
```python
{
  "method": "tools/call",
  "params": {
    "name": "cbr_retrieve",
    "arguments": {
      "query": "How to brew an IPA?",
      "max_results": 5,
      "similarity_threshold": 0.8
    }
  }
}
```

#### Search by Category
```python
{
  "method": "tools/call", 
  "params": {
    "name": "cbr_search_category",
    "arguments": {
      "category": "brewing",
      "query": "IPA techniques",
      "limit": 10
    }
  }
}
```

#### Find Similar Cases
```python
{
  "method": "tools/call",
  "params": {
    "name": "cbr_find_similar",
    "arguments": {
      "example_id": "example_123",
      "similarity_threshold": 0.85,
      "max_results": 8
    }
  }
}
```

## Architecture

### CBRMCPServer
The main server class that:
- Initializes the FastMCP server
- Sets up MCP tools and resources
- Handles parameter validation and error handling
- Provides async wrappers around the synchronous CBR operations

### ExtendedCBRRetriever
Extends the original CBRRetriever class with:
- Async method wrappers
- Enhanced result formatting
- Category and similarity search capabilities
- System statistics reporting

## Configuration

The server supports multiple configuration methods with environment variable overrides.

### Environment Variables

All configuration options can be set via environment variables with the `CBR_` prefix:

```bash
# Core CBR Configuration
export CBR_DATABASE_PATH="./db"                          # Database directory path
export CBR_COLLECTION_NAME="code_solutions_case_base"     # ChromaDB collection name
export CBR_EMBEDDING_MODEL="nomic-ai/nomic-embed-text-v1.5"  # Embedding model
export CBR_MAX_RESULTS_DEFAULT=10                         # Default max results
export CBR_SIMILARITY_THRESHOLD_DEFAULT=0.7               # Default similarity threshold

# Logging Configuration
export CBR_LOG_LEVEL="INFO"                               # DEBUG, INFO, WARNING, ERROR, CRITICAL
export CBR_LOG_FORMAT="json"                              # json, text, colored
export CBR_LOG_FILE="./cbr_server.log"                   # Log file path (optional)
export CBR_LOG_CONSOLE="true"                             # Enable console output
export CBR_LOG_ROTATION="true"                            # Enable log rotation
export CBR_LOG_MAX_SIZE=10485760                          # Max log file size (10MB)
export CBR_LOG_BACKUP_COUNT=5                             # Number of backup files

# Monitoring Configuration
export CBR_MONITORING_PORT=8080                           # Health dashboard port
export CBR_METRICS_ENABLED="true"                         # Enable metrics collection
export CBR_PERFORMANCE_MONITORING="true"                  # Enable performance tracking

# Production Features
export CBR_HEALTH_CHECK_ENABLED="true"                    # Enable health checks
export CBR_RETRY_ENABLED="true"                           # Enable automatic retries
export CBR_MAX_RETRIES=3                                  # Maximum retry attempts
export CBR_CIRCUIT_BREAKER="true"                         # Enable circuit breaker
export CBR_CACHE_ENABLED="true"                           # Enable result caching
export CBR_CACHE_TTL=3600                                 # Cache TTL in seconds
```

### YAML Configuration File

You can also use a YAML configuration file with environment variable overrides:

```yaml
# cbr_config.yaml
# Core Configuration
database_path: "./db"
collection_name: "code_solutions_case_base"
embedding_model: "nomic-ai/nomic-embed-text-v1.5"
max_results_default: 10
similarity_threshold_default: 0.7

# Logging
log_level: "INFO"
log_format: "json"
log_file: "./cbr_server.log"
console_output: true
rotation_enabled: true
max_file_size: 10485760
backup_count: 5

# Monitoring & Health
monitoring_port: 8080
metrics_enabled: true
health_check_enabled: true
performance_monitoring: true

# Production Features
retry_enabled: true
max_retries: 3
circuit_breaker: true
cache_enabled: true
cache_ttl: 3600
input_validation: "strict"  # strict, normal, permissive
sanitization: true
max_query_length: 10000
```

### Loading Configuration

```python
from cbr_mcp_server import CBRServerConfig, load_configuration_from_file

# Load from environment variables only
config = CBRServerConfig.from_environment()

# Load from YAML file with env overrides
config = load_configuration_with_env_overrides("cbr_config.yaml")
```

## Health Dashboard

Access the real-time health dashboard in your web browser:

```
http://localhost:8080
```

The dashboard provides:
- **System Status** - Server uptime, health indicators, and dependency status
- **Performance Metrics** - Real-time CPU, memory, and disk usage graphs
- **Query Statistics** - Request patterns, success rates, latency distribution
- **Application Metrics** - CBR query performance, cache hit rates, error rates
- **Configuration View** - Current server configuration and feature status
- **Log Viewer** - Recent log entries with filtering and search capabilities

### Dashboard Configuration

```bash
# Custom dashboard port
export CBR_MONITORING_PORT=8081

# Disable dashboard (metrics still collected)
export CBR_METRICS_ENABLED=false
```

## Troubleshooting

### Log Files

By default, logs are written to:
- **Console Output**: Structured text format
- **Log File**: `./cbr_server.log` (if configured)
- **Rotation**: Automatic with 5 backup files (10MB each)

### Common Issues

#### Server Won't Start

```bash
# Check database directory permissions
ls -la ./db

# Verify configuration
python -c "from cbr_mcp_server import CBRServerConfig; print(CBRServerConfig.from_environment())"

# Check embedding model availability
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)"
```

#### Performance Issues

```bash
# Enable debug logging
export CBR_LOG_LEVEL=DEBUG

# Check resource usage in dashboard
curl http://localhost:8080/api/metrics

# Monitor system resources
top -p $(pgrep -f cbr-mcp-server)
```

#### Connection Problems

```bash
# Test ChromaDB connection
python -c "import chromadb; client = chromadb.PersistentClient(path='./db'); print('ChromaDB OK')"

# Check network connectivity
netstat -tulnp | grep :8080
```

#### Memory Usage

```bash
# Reduce embedding model memory usage
export CBR_CACHE_ENABLED=false  # Disable result caching
export CBR_MAX_RESULTS_DEFAULT=5  # Reduce default results

# Monitor memory in dashboard
curl http://localhost:8080/api/system/memory
```

### Debug Mode

```bash
# Enable verbose logging and debug features
export CBR_LOG_LEVEL=DEBUG
export CBR_LOG_FORMAT=colored
export CBR_LOG_CONSOLE=true
export CBR_PERFORMANCE_MONITORING=true

cbr-mcp-server
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest test_cbr_mcp_server.py -v

# Run specific test categories
pytest test_cbr_mcp_server.py::TestCBRMCPTools -v
pytest test_cbr_mcp_server.py::TestCBRMCPResources -v

# Run production stability tests
pytest test_production_stability_integration.py -v
pytest test_enhanced_logging.py -v
pytest test_process_resilience.py -v
pytest test_system_resource_monitoring.py -v
pytest test_error_recovery.py -v
pytest test_configuration_validation.py -v
pytest test_health_dashboard.py -v
```

### Test Coverage
- ✅ Server infrastructure and capabilities
- ✅ MCP tools (retrieve, search, find similar)
- ✅ MCP resources (categories, examples, stats)
- ✅ CBRRetriever integration
- ✅ Parameter validation and error handling
- ✅ Edge cases and concurrent operations
- ✅ Production stability features
- ✅ Enhanced logging and monitoring
- ✅ Process resilience and error recovery
- ✅ System resource monitoring
- ✅ Configuration validation
- ✅ Health dashboard functionality
- ✅ Database integrity checks

## Integration

### With Existing CBR System
The server maintains compatibility with the existing `retriever.py` and `case_base.py` components:
- Uses the original `CBRRetriever` class as a base
- Preserves existing ChromaDB and embedding functionality
- Adds MCP protocol layer without breaking existing code

### With MCP Clients
The server can be used with any MCP-compatible client:
- Claude Desktop
- Custom MCP clients
- Development tools that support MCP

## Error Handling

The server includes comprehensive error handling:
- Parameter validation for all tools
- Graceful handling of database connection issues
- Proper MCP error responses
- Logging and debugging support

## Performance

### Optimization Features
- **Concurrent Requests** - Async request handling with thread pool execution
- **Vector Search** - Efficient ChromaDB similarity search with configurable thresholds
- **Result Caching** - In-memory caching with configurable TTL (3600s default)
- **Connection Pooling** - Persistent ChromaDB connections with automatic retry
- **Large Result Warnings** - Automatic warnings for result sets >100 items
- **Memory Management** - Automatic garbage collection and resource cleanup
- **Performance Monitoring** - Real-time latency and throughput tracking

### Performance Configuration

```bash
# Optimize for speed
export CBR_CACHE_ENABLED=true
export CBR_CACHE_TTL=3600
export CBR_MAX_RESULTS_DEFAULT=10
export CBR_SIMILARITY_THRESHOLD_DEFAULT=0.8

# Optimize for memory
export CBR_CACHE_ENABLED=false
export CBR_MAX_RESULTS_DEFAULT=5
export CBR_PERFORMANCE_MONITORING=false
```

### Benchmarking

Monitor performance via the dashboard at `http://localhost:8080` or API endpoints:

```bash
# Get current performance metrics
curl http://localhost:8080/api/metrics

# Get query statistics
curl http://localhost:8080/api/queries/stats

# Get system resource usage
curl http://localhost:8080/api/system/resources
```

## Security

- Input validation for all parameters
- Secure resource URI parsing
- No direct database access exposure
- Proper error message sanitization