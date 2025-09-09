# CBR MCP Server - Health Dashboard Guide

> Last Updated: 2025-09-09
> Version: 1.0.0

## Overview

The CBR MCP Server includes a comprehensive health dashboard that provides real-time monitoring, performance metrics, and system diagnostics. The dashboard combines a web-based interface with programmatic API access, enabling both human operators and automated monitoring systems to track server health, performance, and case-based reasoning statistics.

### Key Features and Benefits

- **Real-time System Monitoring**: Live CPU, memory, disk, and network usage metrics
- **CBR Query Analytics**: Performance statistics, similarity scores, and usage patterns  
- **Request Tracing**: Detailed logging and visualization of CBR queries and responses
- **Database Health**: ChromaDB connection status, integrity checks, and performance metrics
- **Error Tracking**: Failure rates, recovery statistics, and alert management
- **WebSocket Integration**: Real-time updates without page refresh
- **API Access**: Programmatic access to all metrics for external monitoring tools

### When to Use the Dashboard

The health dashboard is particularly useful during:
- **Development**: Monitoring query performance and debugging CBR behavior
- **Production Monitoring**: Tracking system health and identifying performance bottlenecks
- **Troubleshooting**: Diagnosing issues with database connections, embedding performance, or resource constraints
- **Performance Optimization**: Analyzing query patterns and system resource usage
- **Capacity Planning**: Understanding usage trends and resource requirements

## Getting Started

### Prerequisites and Requirements

- CBR MCP Server version 1.0.0 or higher
- Modern web browser with WebSocket support (Chrome 16+, Firefox 11+, Safari 7+, Edge 12+)
- Network access to the configured dashboard port (default: 8080)
- Optional: FastAPI dependencies for full dashboard functionality

### Starting the Dashboard

The health dashboard is automatically available when the CBR MCP Server starts with dashboard configuration enabled.

#### Default Access

```bash
# Dashboard runs on localhost:8080 by default
http://localhost:8080
```

#### Custom Port Configuration

**Using Environment Variables:**
```bash
export CBR_DASHBOARD_HOST="localhost"
export CBR_DASHBOARD_PORT="9090"
cbr-mcp-server
```

**Using YAML Configuration:**
```yaml
dashboard:
  host: "localhost"
  port: 9090
  debug: false
```

**Using Command Line:**
```bash
# Set environment variables inline
CBR_DASHBOARD_PORT=9090 cbr-mcp-server
```

### Browser Compatibility

The dashboard is compatible with:
- **Chrome/Chromium**: Version 16+ (WebSocket support)
- **Firefox**: Version 11+ (WebSocket support)
- **Safari**: Version 7+ (WebSocket support)
- **Microsoft Edge**: Version 12+ (WebSocket support)
- **Mobile Browsers**: Most modern mobile browsers with WebSocket support

## Dashboard Features

### Real-time System Metrics

The dashboard provides comprehensive system monitoring including:

**CPU Monitoring:**
- Current CPU usage percentage
- CPU core count and load averages
- Historical CPU trends and patterns
- Alert thresholds for warning/critical/emergency levels

**Memory Monitoring:**
- Memory usage percentage and absolute values (used/total/available)
- Memory allocation patterns
- Garbage collection metrics (if available)
- Memory leak detection and trending

**Disk Monitoring:**
- Disk usage percentage and space metrics (used/free/total)
- Database storage usage
- Log file storage consumption
- I/O performance metrics

**Network Monitoring:**
- Network bytes sent/received
- Connection counts and statuses
- Request/response throughput
- Network latency measurements

### CBR Query Statistics and Performance

**Query Performance Metrics:**
- Average response time for CBR queries
- 95th and 99th percentile response times
- Query success and failure rates
- Similarity score distributions

**Query Analytics:**
- Most frequent query patterns
- Top-performing categories and use cases
- Query complexity and result set size analysis
- Temporal usage patterns and trends

**Recent Query History:**
- Last 10-50 queries with details
- Query text, similarity scores, and response times
- Success/failure status and error details
- Result count and relevance metrics

### Request Logging and Tracing

**Request Visualization:**
- Real-time request flow and processing status
- Request correlation IDs for tracing
- Processing pipeline visualization
- Error tracking and recovery attempts

**Performance Tracing:**
- Detailed timing breakdowns for each request phase
- Database query performance
- Embedding generation and similarity search times
- Cache hit/miss rates and performance impact

### Database Health and Integrity

**ChromaDB Status:**
- Connection health and availability
- Collection status and document counts
- Index health and performance metrics
- Backup and replication status (if configured)

**Integrity Monitoring:**
- Data consistency checks
- Corruption detection and reporting
- Schema validation and compatibility
- Performance degradation alerts

**Embedding Model Status:**
- Model loading status and performance
- Embedding cache hit rates
- Model memory usage and optimization
- Version compatibility and updates

### Error Rates and Recovery Statistics

**Error Tracking:**
- Request failure rates and categorization
- Database connection failures and recovery
- Authentication and authorization errors
- Rate limiting and capacity issues

**Recovery Metrics:**
- Automatic retry success rates
- Circuit breaker status and triggers
- Failover and fallback mechanism performance
- Mean time to recovery (MTTR) statistics

## Web Interface Guide

### Dashboard Navigation

The web interface is organized into several key sections:

**Header Section:**
- Dashboard title and current status indicator
- Last update timestamp and refresh controls
- Alert summary and notification badges
- Connection status for WebSocket updates

**Main Dashboard Grid:**
- System metrics cards (CPU, Memory, Disk, Network)
- Application metrics cards (Requests, Cache, Database)
- Query statistics and performance charts
- Recent activity and error logs

**Real-time Charts:**
- Time-series graphs for system and application metrics
- Interactive charts with zoom and time range selection
- Alert threshold indicators and breach notifications
- Trend analysis and prediction visualizations

### Understanding Metrics and Visualizations

#### System Metrics Cards

**CPU Usage Card:**
- Current usage percentage with color coding (green < 70%, yellow 70-85%, red > 85%)
- Core count and load average indicators
- Trend arrow showing increase/decrease direction
- Click to expand detailed CPU breakdown

**Memory Usage Card:**
- Used vs. available memory with progress bar
- Percentage usage with color-coded alerts
- Memory type breakdown (if available)
- Cache and buffer usage statistics

**Disk Usage Card:**
- Database storage consumption
- Log file space usage
- Free space remaining with alerts
- I/O throughput indicators

#### Application Metrics

**Request Statistics:**
- Total requests processed with success/failure breakdown
- Current request rate (requests per minute/hour)
- Average response time with percentile indicators
- Error rate percentage with alert thresholds

**Cache Performance:**
- Hit rate percentage with performance indicators
- Cache size and memory usage
- Most frequently cached queries
- Cache invalidation and refresh statistics

**Database Metrics:**
- Active connections and connection pool status
- Query latency and throughput
- Index performance and optimization status
- Data integrity and consistency indicators

### Interpreting Performance Data

#### Performance Indicators

**Green Status (Healthy):**
- CPU usage < 70%
- Memory usage < 75%
- Error rate < 5%
- Response time < 200ms average

**Yellow Status (Warning):**
- CPU usage 70-85%
- Memory usage 75-90%
- Error rate 5-10%
- Response time 200-500ms average

**Red Status (Critical):**
- CPU usage > 85%
- Memory usage > 90%
- Error rate > 10%
- Response time > 500ms average

#### Trend Analysis

**Performance Trends:**
- Upward trends in resource usage may indicate capacity issues
- Spikes in error rates often correlate with system resource constraints
- Gradual increases in response time suggest performance degradation
- Cache hit rate decreases may indicate cache inefficiency or capacity issues

### Troubleshooting from Dashboard Data

#### Common Performance Issues

**High CPU Usage:**
1. Check query complexity and frequency
2. Review embedding model performance
3. Analyze database query efficiency
4. Consider scaling or optimization

**Memory Issues:**
1. Monitor cache size and efficiency
2. Check for memory leaks in query processing
3. Evaluate embedding model memory usage
4. Consider memory limit adjustments

**Database Performance:**
1. Monitor connection counts and query latency
2. Check for index optimization opportunities
3. Analyze query patterns for efficiency
4. Review database storage and I/O performance

**Error Analysis:**
1. Review error categories and patterns
2. Check authentication and authorization issues
3. Monitor rate limiting and capacity constraints
4. Analyze retry and recovery success rates

## API Reference

The health dashboard provides comprehensive REST API endpoints for programmatic access to all monitoring data.

### Health Check Endpoint

**GET /health**

Basic health check endpoint returning overall server status.

```http
GET /health HTTP/1.1
Host: localhost:8080
```

**Response Format:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-09T10:00:00Z",
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "last_check": "2025-09-09T09:59:00Z"
    },
    "cache": {
      "status": "healthy",
      "hit_rate": 0.85
    },
    "rate_limiting": {
      "status": "enabled"
    }
  }
}
```

**Status Values:**
- `healthy`: All systems operating normally
- `warning`: Some non-critical issues detected
- `unhealthy`: Critical issues requiring attention

### System Performance Metrics

**GET /api/metrics/system**

Returns detailed system resource metrics.

```http
GET /api/metrics/system HTTP/1.1
Host: localhost:8080
```

**Response Format:**
```json
{
  "timestamp": "2025-09-09T10:00:00Z",
  "cpu": {
    "percent": 25.0,
    "cores": 8,
    "load_avg": [1.2, 1.1, 0.9]
  },
  "memory": {
    "percent": 60.0,
    "used": 8192,
    "total": 16384,
    "available": 8192
  },
  "disk": {
    "percent": 45.0,
    "used": 450,
    "total": 1000,
    "free": 550
  },
  "network": {
    "bytes_sent": 1024000,
    "bytes_recv": 2048000
  }
}
```

### Application-Specific Metrics

**GET /api/metrics/application**

Returns CBR-specific application metrics.

```http
GET /api/metrics/application HTTP/1.1
Host: localhost:8080
```

**Response Format:**
```json
{
  "timestamp": "2025-09-09T10:00:00Z",
  "requests": {
    "total": 1500,
    "success": 1425,
    "error": 75,
    "rate": 25.0
  },
  "cache": {
    "hit_rate": 0.85,
    "hits": 1275,
    "misses": 225,
    "size": 150
  },
  "database": {
    "connections": 5,
    "queries": 2000,
    "avg_latency": 0.025
  },
  "embeddings": {
    "model_loaded": true,
    "cache_size": 1000,
    "cache_hit_rate": 0.9
  }
}
```

### Query Statistics and Analytics

**GET /api/stats/queries**

Returns detailed query performance and usage statistics.

```http
GET /api/stats/queries HTTP/1.1
Host: localhost:8080
```

**Response Format:**
```json
{
  "timestamp": "2025-09-09T10:00:00Z",
  "recent_queries": [
    {
      "query": "authentication code",
      "similarity": 0.92,
      "response_time": 0.045
    },
    {
      "query": "database connection",
      "similarity": 0.88,
      "response_time": 0.032
    }
  ],
  "performance": {
    "avg_response_time": 0.038,
    "p95_response_time": 0.075,
    "p99_response_time": 0.120
  },
  "patterns": {
    "top_categories": [
      {"name": "authentication", "count": 45},
      {"name": "database", "count": 32}
    ],
    "success_rate": 0.95,
    "error_rate": 0.05
  }
}
```

### WebSocket Endpoints for Real-time Updates

**WebSocket /ws/metrics**

Establishes WebSocket connection for real-time metrics streaming.

```javascript
// JavaScript WebSocket connection
const websocket = new WebSocket('ws://localhost:8080/ws/metrics');

websocket.onopen = function(event) {
    console.log('Connected to metrics stream');
};

websocket.onmessage = function(event) {
    const metrics = JSON.parse(event.data);
    updateDashboard(metrics);
};
```

**Message Format:**
```json
{
  "timestamp": "2025-09-09T10:00:00Z",
  "system": {
    "cpu": 25.0,
    "memory": 60.0,
    "disk": 45.0
  },
  "application": {
    "requests": 100,
    "cache_hit_rate": 0.85,
    "error_rate": 0.05
  },
  "queries": {
    "total": 50,
    "average_latency": 120.0
  }
}
```

### Error Responses

All API endpoints return consistent error responses:

```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "Failed to retrieve metrics",
    "timestamp": "2025-09-09T10:00:00Z"
  }
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `500`: Internal server error
- `503`: Service unavailable (during startup/shutdown)
- `429`: Rate limit exceeded (if rate limiting enabled)

## Configuration Options

### Basic Dashboard Configuration

The dashboard can be configured through YAML configuration files or environment variables.

**YAML Configuration:**
```yaml
dashboard:
  host: "localhost"              # Dashboard host binding
  port: 8080                    # Dashboard port
  debug: false                  # Enable debug features
  websocket_enabled: true       # Enable real-time updates
  metrics_update_interval: 5    # Update interval in seconds
  security_headers: true        # Enable security headers
```

### Environment Variable Configuration

**Dashboard Host and Port:**
```bash
# Set dashboard host and port
export CBR_DASHBOARD_HOST="0.0.0.0"    # Bind to all interfaces
export CBR_DASHBOARD_PORT="9090"       # Use custom port

# Enable debug mode for development
export CBR_DASHBOARD_DEBUG="true"
```

### Feature Configuration Options

**WebSocket Settings:**
```bash
# WebSocket configuration
export CBR_WEBSOCKET_ENABLED="true"           # Enable WebSocket updates
export CBR_METRICS_INTERVAL="2"               # Update every 2 seconds
export CBR_MAX_WEBSOCKET_CONNECTIONS="50"     # Limit WebSocket connections
```

**Security Configuration:**
```bash
# Security settings
export CBR_SECURITY_HEADERS="true"            # Enable security headers
export CBR_CORS_ORIGINS="http://localhost:3000,https://monitor.example.com"
```

**Performance Tuning:**
```bash
# Performance settings
export CBR_MAX_PAYLOAD_SIZE="2097152"         # 2MB max payload size
export CBR_DASHBOARD_CACHE_TTL="300"          # 5-minute cache TTL
```

### Security Considerations

**Network Security:**
- Use `localhost` for local-only access
- Use `0.0.0.0` only when external access is required
- Configure firewall rules to restrict access to dashboard port
- Consider using reverse proxy with SSL/TLS termination

**CORS Configuration:**
```yaml
dashboard:
  cors_origins:
    - "https://monitoring.example.com"         # Trusted monitoring domain
    - "http://localhost:3000"                  # Local development
```

**Security Headers:**
The dashboard automatically includes security headers when enabled:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

### Performance Impact Considerations

**Resource Usage:**
- Dashboard adds minimal CPU overhead (<1% typical usage)
- Memory usage increases by ~10-20MB for web interface
- WebSocket connections use ~1-2KB per connection
- Metrics collection intervals affect system resource usage

**Optimization Settings:**
```yaml
dashboard:
  metrics_update_interval: 10    # Reduce update frequency
  max_websocket_connections: 10  # Limit concurrent connections
  debug: false                   # Disable debug features in production
```

## Integration Examples

### Programmatic API Usage

#### Python Integration Example

```python
import asyncio
import aiohttp
import json

class CBRHealthMonitor:
    def __init__(self, dashboard_host="localhost", dashboard_port=8080):
        self.base_url = f"http://{dashboard_host}:{dashboard_port}"
    
    async def get_health_status(self):
        """Get overall health status."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as response:
                return await response.json()
    
    async def get_system_metrics(self):
        """Get system performance metrics."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/metrics/system") as response:
                return await response.json()
    
    async def get_application_metrics(self):
        """Get CBR application metrics."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/metrics/application") as response:
                return await response.json()
    
    async def monitor_continuous(self, callback):
        """Monitor continuously with callback."""
        while True:
            try:
                health = await self.get_health_status()
                system = await self.get_system_metrics()
                app = await self.get_application_metrics()
                
                await callback({
                    "health": health,
                    "system": system,
                    "application": app
                })
                
            except Exception as e:
                print(f"Monitoring error: {e}")
            
            await asyncio.sleep(30)  # Check every 30 seconds

# Usage example
async def alert_callback(metrics):
    """Example callback for handling metrics."""
    if metrics["system"]["cpu"]["percent"] > 80:
        print(f"HIGH CPU ALERT: {metrics['system']['cpu']['percent']}%")
    
    if metrics["application"]["requests"]["error"] > 10:
        print(f"HIGH ERROR RATE: {metrics['application']['requests']['error']}%")

# Start monitoring
monitor = CBRHealthMonitor()
asyncio.run(monitor.monitor_continuous(alert_callback))
```

#### JavaScript/Node.js Integration

```javascript
const axios = require('axios');
const WebSocket = require('ws');

class CBRDashboardClient {
    constructor(host = 'localhost', port = 8080) {
        this.baseURL = `http://${host}:${port}`;
        this.wsURL = `ws://${host}:${port}/ws/metrics`;
    }
    
    async getHealthStatus() {
        try {
            const response = await axios.get(`${this.baseURL}/health`);
            return response.data;
        } catch (error) {
            throw new Error(`Health check failed: ${error.message}`);
        }
    }
    
    async getMetrics() {
        const [system, application, queries] = await Promise.all([
            axios.get(`${this.baseURL}/api/metrics/system`),
            axios.get(`${this.baseURL}/api/metrics/application`),
            axios.get(`${this.baseURL}/api/stats/queries`)
        ]);
        
        return {
            system: system.data,
            application: application.data,
            queries: queries.data
        };
    }
    
    connectRealTime(onMetrics, onError) {
        const ws = new WebSocket(this.wsURL);
        
        ws.on('open', () => {
            console.log('Connected to metrics stream');
        });
        
        ws.on('message', (data) => {
            const metrics = JSON.parse(data);
            onMetrics(metrics);
        });
        
        ws.on('error', onError);
        
        return ws;
    }
}

// Usage example
const client = new CBRDashboardClient();

// Get current health status
client.getHealthStatus()
    .then(health => console.log('Health:', health))
    .catch(error => console.error('Error:', error));

// Real-time metrics monitoring
const ws = client.connectRealTime(
    (metrics) => {
        console.log('Received metrics:', metrics.timestamp);
        if (metrics.system.cpu > 85) {
            console.log('CPU ALERT: High usage detected');
        }
    },
    (error) => {
        console.error('WebSocket error:', error);
    }
);
```

### Monitoring Automation Scripts

#### System Health Check Script

```bash
#!/bin/bash
# CBR Health Monitor Script

DASHBOARD_HOST="localhost"
DASHBOARD_PORT="8080"
BASE_URL="http://${DASHBOARD_HOST}:${DASHBOARD_PORT}"

# Function to check health status
check_health() {
    local health_response=$(curl -s "${BASE_URL}/health")
    local status=$(echo "$health_response" | jq -r '.status')
    
    if [ "$status" = "healthy" ]; then
        echo "✅ CBR Server Health: HEALTHY"
        return 0
    else
        echo "❌ CBR Server Health: $status"
        echo "$health_response" | jq '.'
        return 1
    fi
}

# Function to check system metrics
check_system_metrics() {
    local metrics=$(curl -s "${BASE_URL}/api/metrics/system")
    local cpu=$(echo "$metrics" | jq -r '.cpu.percent')
    local memory=$(echo "$metrics" | jq -r '.memory.percent')
    local disk=$(echo "$metrics" | jq -r '.disk.percent')
    
    echo "📊 System Metrics:"
    echo "   CPU: ${cpu}%"
    echo "   Memory: ${memory}%"
    echo "   Disk: ${disk}%"
    
    # Check thresholds
    if (( $(echo "$cpu > 85" | bc -l) )); then
        echo "⚠️  WARNING: High CPU usage (${cpu}%)"
    fi
    
    if (( $(echo "$memory > 90" | bc -l) )); then
        echo "⚠️  WARNING: High memory usage (${memory}%)"
    fi
    
    if (( $(echo "$disk > 90" | bc -l) )); then
        echo "⚠️  WARNING: High disk usage (${disk}%)"
    fi
}

# Function to check application metrics
check_application_metrics() {
    local metrics=$(curl -s "${BASE_URL}/api/metrics/application")
    local error_rate=$(echo "$metrics" | jq -r '.requests.error')
    local cache_hit_rate=$(echo "$metrics" | jq -r '.cache.hit_rate')
    local avg_latency=$(echo "$metrics" | jq -r '.database.avg_latency')
    
    echo "🔧 Application Metrics:"
    echo "   Error Rate: ${error_rate}%"
    echo "   Cache Hit Rate: $(echo "$cache_hit_rate * 100" | bc)%"
    echo "   Avg DB Latency: ${avg_latency}ms"
    
    if (( $(echo "$error_rate > 10" | bc -l) )); then
        echo "⚠️  WARNING: High error rate (${error_rate}%)"
    fi
    
    if (( $(echo "$cache_hit_rate < 0.7" | bc -l) )); then
        echo "⚠️  WARNING: Low cache hit rate ($(echo "$cache_hit_rate * 100" | bc)%)"
    fi
}

# Main execution
echo "🔍 Checking CBR MCP Server Health..."
echo "Dashboard: ${BASE_URL}"
echo "Timestamp: $(date)"
echo

if check_health; then
    check_system_metrics
    echo
    check_application_metrics
    echo
    echo "✅ Health check completed successfully"
    exit 0
else
    echo "❌ Health check failed"
    exit 1
fi
```

### External Monitoring Tool Integration

#### Prometheus Integration Example

```python
# CBR Prometheus Exporter
from prometheus_client import start_http_server, Gauge, Counter
import asyncio
import aiohttp
import time

# Define Prometheus metrics
cpu_usage = Gauge('cbr_cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('cbr_memory_usage_percent', 'Memory usage percentage')
disk_usage = Gauge('cbr_disk_usage_percent', 'Disk usage percentage')

request_total = Counter('cbr_requests_total', 'Total requests processed')
request_errors = Counter('cbr_request_errors_total', 'Total request errors')
cache_hits = Counter('cbr_cache_hits_total', 'Total cache hits')
cache_misses = Counter('cbr_cache_misses_total', 'Total cache misses')

query_latency = Gauge('cbr_query_latency_seconds', 'Average query latency')

class CBRPrometheusExporter:
    def __init__(self, cbr_dashboard_url="http://localhost:8080"):
        self.dashboard_url = cbr_dashboard_url
    
    async def collect_metrics(self):
        """Collect metrics from CBR dashboard and export to Prometheus."""
        async with aiohttp.ClientSession() as session:
            # Get system metrics
            async with session.get(f"{self.dashboard_url}/api/metrics/system") as response:
                system_data = await response.json()
                cpu_usage.set(system_data['cpu']['percent'])
                memory_usage.set(system_data['memory']['percent'])
                disk_usage.set(system_data['disk']['percent'])
            
            # Get application metrics
            async with session.get(f"{self.dashboard_url}/api/metrics/application") as response:
                app_data = await response.json()
                request_total._value._value = app_data['requests']['total']
                request_errors._value._value = app_data['requests']['error']
                cache_hits._value._value = app_data['cache']['hits']
                cache_misses._value._value = app_data['cache']['misses']
                query_latency.set(app_data['database']['avg_latency'])

async def main():
    # Start Prometheus metrics server
    start_http_server(8000)  # Prometheus metrics on port 8000
    
    exporter = CBRPrometheusExporter()
    
    while True:
        try:
            await exporter.collect_metrics()
            print(f"Metrics updated at {time.ctime()}")
        except Exception as e:
            print(f"Error collecting metrics: {e}")
        
        await asyncio.sleep(30)  # Update every 30 seconds

if __name__ == "__main__":
    print("Starting CBR Prometheus Exporter...")
    asyncio.run(main())
```

#### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "CBR MCP Server Monitoring",
    "panels": [
      {
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "cbr_cpu_usage_percent",
            "legendFormat": "CPU Usage %"
          },
          {
            "expr": "cbr_memory_usage_percent", 
            "legendFormat": "Memory Usage %"
          },
          {
            "expr": "cbr_disk_usage_percent",
            "legendFormat": "Disk Usage %"
          }
        ]
      },
      {
        "title": "Request Statistics",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(cbr_requests_total[5m])",
            "legendFormat": "Request Rate"
          },
          {
            "expr": "rate(cbr_request_errors_total[5m])",
            "legendFormat": "Error Rate"
          }
        ]
      },
      {
        "title": "Query Performance",
        "type": "singlestat",
        "targets": [
          {
            "expr": "cbr_query_latency_seconds",
            "legendFormat": "Avg Query Latency"
          }
        ]
      }
    ]
  }
}
```

This comprehensive health dashboard guide provides everything needed to effectively monitor, troubleshoot, and optimize the CBR MCP Server using both the web interface and programmatic access methods.