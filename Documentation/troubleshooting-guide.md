# CBR MCP Server - Troubleshooting Guide

> Last Updated: 2025-09-09
> Version: 1.0.0

## Overview

This comprehensive troubleshooting guide provides step-by-step solutions for common issues, error diagnosis techniques, and advanced debugging strategies for the CBR MCP Server. The guide covers production stability features, enhanced logging analysis, error recovery troubleshooting, and real-world problem scenarios.

## General Troubleshooting Approach

### Step-by-Step Diagnostic Process

1. **Identify the Problem**
   - Check server status and health dashboard
   - Review recent error logs and metrics
   - Determine if issue is system-wide or specific to certain queries
   - Note timing and frequency of the issue

2. **Gather Information**
   - Enable debug logging if not already active
   - Check system resource usage (CPU, memory, disk)
   - Review configuration settings
   - Examine database and embedding model status

3. **Isolate the Issue**
   - Test individual components (database, embeddings, caching)
   - Try different query types and sizes
   - Check network connectivity and permissions
   - Verify recent changes or deployments

4. **Apply Solution**
   - Use appropriate fix from this guide
   - Monitor results and system stability
   - Document the resolution for future reference
   - Consider preventive measures

## Common Issues and Solutions

### Server Startup Problems

#### Issue: Server Won't Start - Database Path Error

**Symptoms:**
```
Configuration Error: database_path '/path/to/db' is not writable
Failed to initialize ChromaDB client
```

**Root Cause:** Database directory doesn't exist or lacks proper permissions.

**Solution:**
```bash
# Check if directory exists
ls -la /path/to/db

# Create directory if missing
mkdir -p /path/to/db

# Fix permissions
chmod 755 /path/to/db
chown $(whoami):$(whoami) /path/to/db

# Verify ChromaDB can access the path
python -c "import chromadb; client = chromadb.PersistentClient(path='/path/to/db'); print('ChromaDB OK')"
```

**Prevention:**
- Always use absolute paths in production
- Set up proper directory creation in deployment scripts
- Include database path verification in startup validation

#### Issue: Embedding Model Loading Failure

**Symptoms:**
```
ERROR: Failed to load embedding model 'nomic-ai/nomic-embed-text-v1.5'
OSError: [Errno 28] No space left on device
ConnectionError: HTTPSConnectionPool failed to establish a new connection
```

**Root Causes:**
- Insufficient disk space for model download
- Network connectivity issues
- Hugging Face Hub access problems

**Solution:**
```bash
# Check disk space
df -h

# Clear space if needed
sudo apt-get clean
docker system prune -f

# Test network connectivity
curl -I https://huggingface.co

# Test model loading manually
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)
print('Model loaded successfully')
"

# Check Hugging Face cache location
python -c "
import transformers
print('Cache directory:', transformers.file_utils.default_cache_path)
"
```

**Prevention:**
- Monitor disk space regularly
- Pre-download models in deployment process
- Set up offline model serving for production

#### Issue: Port Already in Use

**Symptoms:**
```
ERROR: [Errno 48] Address already in use: ('localhost', 8080)
Failed to start health dashboard on port 8080
```

**Solution:**
```bash
# Find process using the port
lsof -i :8080
netstat -tulnp | grep :8080

# Kill conflicting process
kill -9 <PID>

# Or use alternative port
export CBR_DASHBOARD_PORT=8081
export CBR_MONITORING_PORT=8081

# Check available ports
netstat -tulnp | grep LISTEN
```

### Connection and Communication Issues

#### Issue: MCP Communication Failures

**Symptoms:**
```
ERROR: Failed to process MCP request
JSONRPCException: Invalid request format
Timeout waiting for MCP response
```

**Root Causes:**
- Malformed JSON-RPC requests
- Network timeouts
- Buffer overflow in stdio transport
- Client compatibility issues

**Solution:**
```bash
# Enable debug logging to see raw MCP messages
export CBR_LOG_LEVEL=DEBUG
export CBR_LOG_FORMAT=colored
cbr-mcp-server

# Test MCP communication manually
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}}, "id": 1}' | cbr-mcp-server

# Check stdio buffer limits
ulimit -a

# Increase buffer sizes if needed
ulimit -n 4096
```

**Debug Analysis:**
- Look for `MCP Request:` and `MCP Response:` in debug logs
- Check for incomplete JSON messages
- Monitor request/response correlation IDs
- Verify protocol version compatibility

#### Issue: Database Connection Lost

**Symptoms:**
```
WARNING: ChromaDB connection lost, attempting recovery
ERROR: Circuit breaker OPEN for database operations
Database integrity check failed
```

**Root Causes:**
- Database corruption or lock contention
- Network issues (if using remote ChromaDB)
- Resource exhaustion
- Concurrent access conflicts

**Solution:**
```bash
# Check database integrity
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collections = client.list_collections()
print(f'Collections: {[c.name for c in collections]}')
"

# Run database integrity validation
export CBR_LOG_LEVEL=DEBUG
python -c "
from cbr_mcp_server import DatabaseIntegrityValidator, CBRServerConfig
config = CBRServerConfig.from_environment()
validator = DatabaseIntegrityValidator(config)
result = validator.run_full_integrity_check()
print(f'Integrity check: {result.overall_status}')
for finding in result.corruption_findings:
    print(f'Issue: {finding.description}')
"

# Repair database if needed
python -c "
from cbr_mcp_server import DatabaseRepairer, CBRServerConfig
config = CBRServerConfig.from_environment()
repairer = DatabaseRepairer(config)
success = repairer.repair_database()
print(f'Repair successful: {success}')
"
```

**Recovery Steps:**
1. Stop the server gracefully
2. Run integrity validation
3. Apply repairs if corruption detected
4. Restart with monitoring enabled
5. Check circuit breaker status in health dashboard

### Performance Problems

#### Issue: High Memory Usage

**Symptoms:**
```
WARNING: Memory usage 89.2% exceeds threshold (85.0%)
CRITICAL: Memory usage 94.1% exceeds critical threshold (90.0%)
Out of memory error during embedding generation
```

**Root Causes:**
- Large result sets cached in memory
- Memory leaks in embedding processing
- Insufficient garbage collection
- Too many concurrent requests

**Solution:**
```bash
# Check current memory usage
curl http://localhost:8080/api/metrics/system | jq '.memory'

# Monitor memory patterns
top -p $(pgrep -f cbr-mcp-server)
htop -p $(pgrep -f cbr-mcp-server)

# Reduce memory usage temporarily
export CBR_CACHE_ENABLED=false
export CBR_MAX_RESULTS_DEFAULT=5

# Force garbage collection (for testing)
python -c "
import gc
gc.collect()
print(f'Collected: {gc.collect()} objects')
"

# Check for memory leaks
export CBR_LOG_LEVEL=DEBUG
# Look for increasing memory usage patterns in logs
```

**Memory Optimization:**
```yaml
# Add to configuration
production:
  cache_ttl: 1800          # Shorter cache TTL
  max_query_length: 5000   # Limit query size
  
query:
  max_results_default: 5   # Smaller result sets

monitoring:
  retention_hours: 24      # Shorter metric retention
```

#### Issue: Slow Query Performance

**Symptoms:**
```
WARNING: Query latency 2.34s exceeds threshold (1.0s)
High p95 response time: 3.2s
Cache hit rate below 50%
```

**Root Causes:**
- Inefficient similarity search parameters
- Database index issues
- Large collection size without optimization
- Cold embedding model start

**Solution:**
```bash
# Check query performance metrics
curl http://localhost:8080/api/stats/queries | jq '.performance'

# Analyze slow queries in logs
grep "Query latency" /var/log/cbr/server.log | sort -k4 -nr | head -10

# Test query performance
python -c "
import time
from cbr_mcp_server import ProductionCBRRetriever, CBRServerConfig
config = CBRServerConfig.from_environment()
retriever = ProductionCBRRetriever(config)

start = time.time()
results = retriever.retrieve_cases('test query', max_results=5)
duration = time.time() - start
print(f'Query took {duration:.2f}s, returned {len(results)} results')
"
```

**Performance Tuning:**
```yaml
query:
  similarity_threshold_default: 0.8  # Higher threshold = fewer results
  max_results_default: 10            # Reasonable limit
  
production:
  cache_enabled: true
  cache_ttl: 3600                   # Cache results longer
```

#### Issue: High CPU Usage

**Symptoms:**
```
WARNING: CPU usage 78.3% exceeds threshold (70.0%)
CRITICAL: CPU usage 91.2% exceeds critical threshold (85.0%)
Embedding generation taking too long
```

**Solution:**
```bash
# Check CPU usage patterns
curl http://localhost:8080/api/metrics/system | jq '.cpu'

# Profile CPU usage
perf top -p $(pgrep -f cbr-mcp-server)

# Check for CPU-intensive operations
grep "Performance:" /var/log/cbr/server.log | tail -20

# Reduce CPU load temporarily
export CBR_PERFORMANCE_MONITORING=false
export CBR_METRICS_INTERVAL=60  # Less frequent monitoring
```

### Database and Embedding Problems

#### Issue: Embedding Generation Failures

**Symptoms:**
```
ERROR: Failed to generate embeddings for query
RuntimeError: CUDA out of memory
Model loading failed with timeout
```

**Root Causes:**
- GPU memory exhaustion (if using CUDA)
- Model compatibility issues
- Corrupt model cache
- Resource constraints

**Solution:**
```bash
# Check embedding model status
python -c "
from sentence_transformers import SentenceTransformer
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA devices: {torch.cuda.device_count()}')
    for i in range(torch.cuda.device_count()):
        print(f'Device {i}: {torch.cuda.get_device_name(i)}')
"

# Test embedding generation
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)
embeddings = model.encode(['test query'])
print(f'Embedding shape: {embeddings.shape}')
print('Embedding generation successful')
"

# Clear model cache if corrupted
rm -rf ~/.cache/torch/sentence_transformers/

# Force CPU usage if GPU issues
export CUDA_VISIBLE_DEVICES=""
```

#### Issue: Database Corruption

**Symptoms:**
```
ERROR: Collection 'code_solutions_case_base' not found
Database integrity check failed: 3 corrupted entries found
Inconsistent embedding dimensions detected
```

**Solution:**
```bash
# Run comprehensive integrity check
python -c "
from cbr_mcp_server import DatabaseIntegrityValidator, CBRServerConfig
config = CBRServerConfig.from_environment()
validator = DatabaseIntegrityValidator(config)
result = validator.run_full_integrity_check()
print(f'Overall status: {result.overall_status}')
print(f'Collections checked: {result.collections_checked}')
print(f'Documents validated: {result.documents_validated}')
print(f'Corruption findings: {len(result.corruption_findings)}')
for finding in result.corruption_findings:
    print(f'- {finding.description} (Severity: {finding.severity})')
"

# Create backup before repair
cp -r ./db ./db_backup_$(date +%Y%m%d_%H%M%S)

# Attempt automatic repair
python -c "
from cbr_mcp_server import DatabaseRepairer, CBRServerConfig
config = CBRServerConfig.from_environment()
repairer = DatabaseRepairer(config)
success = repairer.repair_database()
print(f'Repair successful: {success}')
if success:
    print('Database repair completed successfully')
else:
    print('Manual intervention may be required')
"

# If automatic repair fails, manual steps:
# 1. Stop the server
# 2. Remove corrupted collection
# 3. Re-initialize from backup or re-populate
```

### Configuration Issues

#### Issue: Invalid Configuration Values

**Symptoms:**
```
Configuration Error: similarity_threshold_default must be between 0.0 and 1.0
Configuration Error: monitoring_port conflicts with dashboard_port
YAML parsing error: invalid syntax
```

**Solution:**
```bash
# Validate configuration syntax
cbr-mcp-server --config your-config.yaml --validate-only

# Test configuration loading
python -c "
from cbr_mcp_server import CBRServerConfig, load_configuration_from_file
try:
    if 'your-config.yaml':
        config = load_configuration_from_file('your-config.yaml')
    else:
        config = CBRServerConfig.from_environment()
    print('Configuration loaded successfully')
    print(f'Database path: {config.database_path}')
    print(f'Log level: {config.log_level}')
except Exception as e:
    print(f'Configuration error: {e}')
"

# Check for common configuration conflicts
python -c "
import yaml
with open('your-config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    
dashboard_port = config.get('dashboard', {}).get('port', 8080)
monitoring_port = config.get('monitoring', {}).get('port', dashboard_port)

if dashboard_port == monitoring_port:
    print('WARNING: Dashboard and monitoring ports conflict')
    
similarity = config.get('query', {}).get('similarity_threshold_default', 0.7)
if not 0.0 <= similarity <= 1.0:
    print(f'ERROR: Invalid similarity threshold: {similarity}')
"
```

#### Issue: Environment Variable Override Not Working

**Symptoms:**
- Configuration changes not taking effect
- Default values used instead of environment variables
- Inconsistent behavior across restarts

**Solution:**
```bash
# Check environment variables are set
env | grep CBR_

# Test specific variable loading
python -c "
import os
print('Environment variables:')
for key, value in os.environ.items():
    if key.startswith('CBR_'):
        print(f'  {key}={value}')
"

# Check configuration precedence
export CBR_LOG_LEVEL=DEBUG
python -c "
from cbr_mcp_server import CBRServerConfig
config = CBRServerConfig.from_environment()
print(f'Final log level: {config.log_level}')
print(f'Database path: {config.database_path}')
"

# Clear conflicting variables
unset $(env | grep CBR_ | cut -d= -f1)
# Then set only desired variables
export CBR_LOG_LEVEL=INFO
export CBR_DATABASE_PATH=./db
```

## Error Messages Reference

### Critical Errors

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| `Circuit breaker OPEN for database operations` | Database operations failing repeatedly | Check database health, wait for circuit breaker reset, or restart server |
| `CRITICAL: Memory usage X% exceeds critical threshold` | System running out of memory | Reduce cache size, lower result limits, restart server |
| `EMERGENCY: CPU usage X% exceeds emergency threshold` | System overloaded | Stop non-essential processes, check for runaway queries |
| `Database integrity check failed` | Database corruption detected | Run integrity validation and repair procedures |
| `Failed to load embedding model` | Model loading error | Check disk space, network connectivity, model compatibility |

### Warning Messages

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| `WARNING: High error rate detected` | Many requests failing | Check logs for specific error patterns, investigate root cause |
| `WARNING: Cache hit rate below threshold` | Cache inefficiency | Review cache configuration, check query patterns |
| `WARNING: Disk usage exceeds threshold` | Low disk space | Clean up logs, old data, or increase disk capacity |
| `ChromaDB connection lost, attempting recovery` | Temporary database issue | Monitor recovery attempts, check database health |
| `Rate limiting threshold exceeded` | Too many requests | Review rate limits, check for request spikes |

### Info Messages

| Error Message | Meaning | Action |
|---------------|---------|--------|
| `Server starting with configuration` | Normal startup | Monitor for completion |
| `Health check passed` | System healthy | No action needed |
| `Circuit breaker reset to CLOSED` | Recovery from previous failures | Continue monitoring |
| `Database integrity check completed` | Validation finished | Review results if issues found |
| `Performance monitoring enabled` | Monitoring active | Use dashboard for metrics |

## Debug Mode Configuration and Usage

### Enabling Debug Mode

```bash
# Enable comprehensive debugging
export CBR_LOG_LEVEL=DEBUG
export CBR_LOG_FORMAT=colored
export CBR_LOG_CONSOLE=true
export CBR_LOG_PERFORMANCE=true
export CBR_LOG_CORRELATION=true

# Start server with debug options
cbr-mcp-server
```

### Debug Configuration File

```yaml
# debug.yaml - Debug configuration
logging:
  level: "DEBUG"
  format: "colored"
  console_output: true
  console_format: "colored"
  enable_colors: true
  performance_logging: true
  request_correlation: true
  
monitoring:
  interval: 5.0          # Frequent monitoring
  
dashboard:
  debug: true            # Enable debug features
  websocket_enabled: true
  metrics_update_interval: 1  # Real-time updates

production:
  input_validation: "permissive"  # Allow debug queries
  cache_enabled: false           # Disable cache for testing
```

### Debug Information Available

**Request Tracing:**
```
DEBUG: MCP Request [req-123]: cbr_retrieve
DEBUG: Query preprocessing [req-123]: "user authentication code"
DEBUG: Embedding generation [req-123]: 384 dimensions, 0.023s
DEBUG: ChromaDB query [req-123]: 156 candidates, similarity > 0.7
DEBUG: Result filtering [req-123]: 12 results, 0.089s total
DEBUG: MCP Response [req-123]: 12 results, 0.112s end-to-end
```

**Performance Metrics:**
```
DEBUG: Performance [database_query]: 0.034s
DEBUG: Performance [embedding_generation]: 0.023s  
DEBUG: Performance [result_processing]: 0.012s
DEBUG: Memory usage: 67.2% (5.4GB/8.0GB)
DEBUG: Cache status: 234 entries, 78.5% hit rate
```

**Error Context:**
```
DEBUG: Circuit breaker [database]: State=HALF_OPEN, Failures=2/5
ERROR: Database query failed [req-456]: Connection timeout after 30s
DEBUG: Retry attempt 1/3 [req-456]: Exponential backoff 2.0s
DEBUG: Circuit breaker [database]: State=OPEN (too many failures)
```

## Log Analysis Techniques

### Log File Locations

```bash
# Default locations
./cbr_server.log                    # Current log
./cbr_server.log.1                  # First backup
./cbr_server.log.2                  # Second backup
/var/log/cbr/server.log            # Production location
```

### Analyzing Performance Issues

```bash
# Find slowest queries
grep "Query latency" cbr_server.log | \
  awk '{print $NF, $0}' | \
  sort -nr | \
  head -20

# Analyze memory usage trends
grep "Memory usage" cbr_server.log | \
  awk '{print $1, $2, $4}' | \
  tail -100

# Check error patterns
grep "ERROR" cbr_server.log | \
  awk '{print $4, $5}' | \
  sort | uniq -c | sort -nr

# Find request correlation issues
grep "req-[0-9]" cbr_server.log | \
  grep -E "(ERROR|timeout|failed)" | \
  awk '{print $3}' | sort | uniq -c
```

### JSON Log Analysis

```bash
# For JSON formatted logs
# Extract error messages
jq -r 'select(.level=="ERROR") | .message' cbr_server.log

# Performance analysis
jq -r 'select(.performance) | "\(.timestamp) \(.performance.operation) \(.performance.duration)"' cbr_server.log

# Memory usage over time  
jq -r 'select(.memory_percent) | "\(.timestamp) \(.memory_percent)"' cbr_server.log

# Request success rates
jq -r 'select(.request_id) | "\(.level) \(.request_id)"' cbr_server.log | \
  sort | uniq -c
```

### Log Monitoring Scripts

```bash
#!/bin/bash
# monitor_logs.sh - Real-time log monitoring

LOG_FILE="${1:-./cbr_server.log}"

echo "Monitoring CBR server logs: $LOG_FILE"
echo "Press Ctrl+C to stop"
echo

tail -f "$LOG_FILE" | while read line; do
    # Highlight errors and warnings
    if echo "$line" | grep -q "ERROR"; then
        echo -e "\033[31m$line\033[0m"  # Red
    elif echo "$line" | grep -q "WARNING"; then
        echo -e "\033[33m$line\033[0m"  # Yellow
    elif echo "$line" | grep -q "CRITICAL"; then
        echo -e "\033[35m$line\033[0m"  # Magenta
    elif echo "$line" | grep -q "Performance"; then
        echo -e "\033[36m$line\033[0m"  # Cyan
    else
        echo "$line"
    fi
done
```

## Using Health Dashboard for Troubleshooting

### Dashboard Sections for Troubleshooting

**System Status Overview:**
- Server health indicator (green/yellow/red)
- Database connection status
- Embedding model status
- Circuit breaker states

**Resource Monitoring:**
- CPU usage trends and spikes
- Memory consumption patterns
- Disk usage and I/O metrics
- Network activity

**Application Metrics:**
- Request success/failure rates
- Query performance statistics
- Cache hit rates and efficiency
- Error categorization

### Troubleshooting Workflows Using Dashboard

**Performance Issues:**
1. Check system resource graphs for spikes
2. Review query latency distribution
3. Examine cache hit rates
4. Look for error correlations with resource usage

**Connectivity Issues:**
1. Check database connection indicator
2. Review network metrics
3. Look for request timeout patterns
4. Check circuit breaker status

**Stability Issues:**
1. Monitor error rate trends
2. Check recovery attempt statistics
3. Review resource threshold breaches
4. Examine uptime and restart patterns

### Dashboard API for Automated Troubleshooting

```bash
# Health check automation
check_health() {
    local status=$(curl -s http://localhost:8080/health | jq -r '.status')
    case "$status" in
        "healthy") echo "✅ System healthy" ;;
        "warning") echo "⚠️ System warnings detected" ;;
        "unhealthy") echo "❌ System unhealthy - investigation needed" ;;
    esac
}

# Resource monitoring
check_resources() {
    local metrics=$(curl -s http://localhost:8080/api/metrics/system)
    local cpu=$(echo "$metrics" | jq -r '.cpu.percent')
    local memory=$(echo "$metrics" | jq -r '.memory.percent')
    local disk=$(echo "$metrics" | jq -r '.disk.percent')
    
    echo "Resources: CPU ${cpu}%, Memory ${memory}%, Disk ${disk}%"
    
    # Alert thresholds
    (( $(echo "$cpu > 85" | bc -l) )) && echo "⚠️ High CPU usage"
    (( $(echo "$memory > 90" | bc -l) )) && echo "⚠️ High memory usage"
    (( $(echo "$disk > 90" | bc -l) )) && echo "⚠️ High disk usage"
}

# Error analysis
check_errors() {
    local app_metrics=$(curl -s http://localhost:8080/api/metrics/application)
    local error_rate=$(echo "$app_metrics" | jq -r '.requests.error')
    local success_rate=$(echo "$app_metrics" | jq -r '.requests.success')
    local total=$(echo "$app_metrics" | jq -r '.requests.total')
    
    echo "Requests: Total $total, Success $success_rate, Errors $error_rate"
    
    if (( error_rate > 10 )); then
        echo "⚠️ High error rate detected"
        # Could trigger additional diagnostics here
    fi
}
```

## Advanced Debugging Scenarios

### Intermittent Connection Issues

**Problem:** Random connection failures that are hard to reproduce.

**Debug Approach:**
1. Enable continuous monitoring
2. Correlate failures with system metrics
3. Check for resource exhaustion patterns
4. Review network timeout configurations

```bash
# Continuous monitoring script
while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Test connection
    if curl -s http://localhost:8080/health > /dev/null; then
        status="OK"
    else
        status="FAILED"
    fi
    
    # Get system metrics
    cpu=$(curl -s http://localhost:8080/api/metrics/system | jq -r '.cpu.percent')
    memory=$(curl -s http://localhost:8080/api/metrics/system | jq -r '.memory.percent')
    
    echo "$timestamp,$status,$cpu,$memory" >> connection_monitoring.csv
    
    sleep 5
done
```

### Memory Leak Investigation

**Problem:** Memory usage gradually increases over time.

**Debug Steps:**
1. Monitor memory patterns over extended periods
2. Correlate memory growth with specific operations
3. Check for cache overflow or retention issues
4. Profile memory allocation patterns

```python
# Memory profiling script
import psutil
import time
import requests
import json

def monitor_memory_usage(duration_hours=24):
    """Monitor memory usage patterns for leak detection."""
    process = psutil.Process()  # Current process
    start_time = time.time()
    end_time = start_time + (duration_hours * 3600)
    
    measurements = []
    
    while time.time() < end_time:
        # Get memory info
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        # Get application metrics
        try:
            response = requests.get('http://localhost:8080/api/metrics/application')
            app_metrics = response.json()
            cache_size = app_metrics.get('cache', {}).get('size', 0)
        except:
            cache_size = -1
        
        measurement = {
            'timestamp': time.time(),
            'memory_rss': memory_info.rss,
            'memory_vms': memory_info.vms,
            'memory_percent': memory_percent,
            'cache_size': cache_size
        }
        
        measurements.append(measurement)
        print(f"Memory: {memory_percent:.1f}% ({memory_info.rss/1024/1024:.1f}MB), Cache: {cache_size}")
        
        time.sleep(60)  # Check every minute
    
    # Save results
    with open('memory_profile.json', 'w') as f:
        json.dump(measurements, f, indent=2)
    
    print(f"Memory profiling complete. Results saved to memory_profile.json")

if __name__ == "__main__":
    monitor_memory_usage(duration_hours=2)  # 2-hour monitoring
```

### Query Performance Regression

**Problem:** Query performance suddenly degrades without obvious cause.

**Investigation Process:**
1. Compare current metrics with historical baselines
2. Check for database index issues
3. Analyze query complexity patterns
4. Review recent configuration changes

```bash
# Performance regression analysis
analyze_performance_regression() {
    echo "=== Query Performance Analysis ==="
    
    # Current performance
    echo "Current metrics:"
    curl -s http://localhost:8080/api/stats/queries | jq '.performance'
    
    # Historical comparison (if available)
    echo -e "\nHistorical performance (last 7 days):"
    grep "avg_response_time" cbr_server.log.* | \
        awk '{print $1, $2, $NF}' | \
        sort | \
        tail -20
    
    # Check for slow queries
    echo -e "\nSlowest recent queries:"
    grep "Query latency" cbr_server.log | \
        sort -k4 -nr | \
        head -10
    
    # Database performance
    echo -e "\nDatabase performance:"
    python -c "
import time
from cbr_mcp_server import ProductionCBRRetriever, CBRServerConfig
config = CBRServerConfig.from_environment()
retriever = ProductionCBRRetriever(config)

# Test query performance
queries = ['authentication', 'database connection', 'error handling']
for query in queries:
    start = time.time()
    results = retriever.retrieve_cases(query, max_results=5)
    duration = time.time() - start
    print(f'Query \"{query}\": {duration:.3f}s, {len(results)} results')
"
}
```

This comprehensive troubleshooting guide provides practical solutions for the most common issues encountered with the CBR MCP Server, along with advanced debugging techniques for complex scenarios.