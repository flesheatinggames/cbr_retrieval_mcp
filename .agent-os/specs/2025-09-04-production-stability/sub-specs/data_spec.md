# Data Specification

This is the data specification for the spec detailed in @.agent-os/specs/2025-09-04-production-stability/spec.md

> Created: 2025-09-04
> Version: 1.0.0

## Data Models

### Configuration Models

```python
class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARN", "ERROR"] = "INFO"
    format: Literal["json", "text", "colored"] = "json"
    file_path: Optional[str] = "./cbr_server.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_request_logging: bool = True
    enable_performance_logging: bool = True

class MonitoringConfig(BaseModel):
    enable_resource_monitoring: bool = True
    polling_interval: int = 30  # seconds
    memory_threshold_mb: int = 512
    cpu_threshold_percent: float = 80.0
    disk_threshold_percent: float = 90.0
    metrics_retention_hours: int = 24

class ResilienceConfig(BaseModel):
    max_retry_attempts: int = 3
    initial_retry_delay: float = 1.0
    max_retry_delay: float = 30.0
    connection_timeout: float = 10.0
    health_check_interval: int = 60
    enable_circuit_breaker: bool = True
    circuit_breaker_failure_threshold: int = 5

class HealthDashboardConfig(BaseModel):
    enable_dashboard: bool = True
    port: int = 8080
    host: str = "localhost"
    auto_open_browser: bool = False
```

### Logging Models

```python
class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    message: str
    request_id: Optional[str] = None
    component: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RequestLogEntry(LogEntry):
    method: str
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    response_size_bytes: Optional[int] = None
    latency_ms: Optional[float] = None
    success: bool
    error_type: Optional[str] = None

class PerformanceLogEntry(LogEntry):
    memory_usage_mb: float
    cpu_percent: float
    disk_usage_percent: float
    active_connections: int
    query_queue_size: int
```

### Monitoring Models

```python
class SystemMetrics(BaseModel):
    timestamp: datetime
    memory_usage_mb: float
    memory_percent: float
    cpu_percent: float
    disk_usage_gb: float
    disk_percent: float
    load_average: List[float]
    uptime_seconds: int

class ApplicationMetrics(BaseModel):
    timestamp: datetime
    active_connections: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time_ms: float
    chromadb_status: Literal["connected", "disconnected", "error"]
    embedding_model_status: Literal["loaded", "loading", "error"]

class HealthStatus(BaseModel):
    overall_status: Literal["healthy", "degraded", "unhealthy"]
    components: Dict[str, Literal["healthy", "unhealthy"]]
    last_updated: datetime
    uptime_seconds: int
    system_metrics: SystemMetrics
    application_metrics: ApplicationMetrics
```

### Error Recovery Models

```python
class ErrorContext(BaseModel):
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    component: str
    timestamp: datetime
    request_id: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: Optional[bool] = None

class CircuitBreakerState(BaseModel):
    name: str
    state: Literal["closed", "open", "half_open"]
    failure_count: int
    last_failure_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None
    success_threshold: int = 3

class RetryAttempt(BaseModel):
    attempt_number: int
    timestamp: datetime
    delay_seconds: float
    error_message: str
    success: bool
```

## Database Schema Changes

### New Collections (ChromaDB)

No new ChromaDB collections are required. The existing `code_solutions_case_base` collection will remain unchanged.

### New File-Based Storage

```python
# metrics.db - SQLite database for metrics storage
CREATE TABLE system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    memory_usage_mb REAL NOT NULL,
    memory_percent REAL NOT NULL,
    cpu_percent REAL NOT NULL,
    disk_usage_gb REAL NOT NULL,
    disk_percent REAL NOT NULL,
    uptime_seconds INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE application_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    active_connections INTEGER NOT NULL,
    total_requests INTEGER NOT NULL,
    successful_requests INTEGER NOT NULL,
    failed_requests INTEGER NOT NULL,
    average_response_time_ms REAL NOT NULL,
    chromadb_status TEXT NOT NULL,
    embedding_model_status TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE error_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    error_type TEXT NOT NULL,
    error_message TEXT NOT NULL,
    component TEXT NOT NULL,
    request_id TEXT,
    recovery_attempted BOOLEAN DEFAULT FALSE,
    recovery_successful BOOLEAN,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

# Indexes for performance
CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX idx_application_metrics_timestamp ON application_metrics(timestamp);
CREATE INDEX idx_error_log_timestamp ON error_log(timestamp);
CREATE INDEX idx_error_log_component ON error_log(component);
```

### Configuration Files

```yaml
# cbr_config.yml - Main configuration file
logging:
  level: "INFO"
  format: "json"
  file_path: "./cbr_server.log"
  max_file_size: 10485760  # 10MB
  backup_count: 5
  enable_request_logging: true
  enable_performance_logging: true

monitoring:
  enable_resource_monitoring: true
  polling_interval: 30
  memory_threshold_mb: 512
  cpu_threshold_percent: 80.0
  disk_threshold_percent: 90.0
  metrics_retention_hours: 24

resilience:
  max_retry_attempts: 3
  initial_retry_delay: 1.0
  max_retry_delay: 30.0
  connection_timeout: 10.0
  health_check_interval: 60
  enable_circuit_breaker: true
  circuit_breaker_failure_threshold: 5

health_dashboard:
  enable_dashboard: true
  port: 8080
  host: "localhost"
  auto_open_browser: false
```

## API Endpoints

### Health Dashboard API

```python
# GET /health - Overall health status
{
  "status": "healthy",
  "timestamp": "2025-09-04T12:00:00Z",
  "uptime": 3600,
  "components": {
    "chromadb": "healthy",
    "embedding_model": "healthy",
    "file_system": "healthy"
  }
}

# GET /metrics/system - System resource metrics
{
  "timestamp": "2025-09-04T12:00:00Z",
  "memory": {
    "usage_mb": 256.5,
    "percent": 12.8
  },
  "cpu": {
    "percent": 15.2
  },
  "disk": {
    "usage_gb": 2.1,
    "percent": 25.3
  }
}

# GET /metrics/application - Application performance metrics
{
  "timestamp": "2025-09-04T12:00:00Z",
  "requests": {
    "total": 1500,
    "successful": 1485,
    "failed": 15,
    "success_rate": 99.0
  },
  "performance": {
    "average_response_time_ms": 85.2,
    "active_connections": 3
  },
  "components": {
    "chromadb_status": "connected",
    "embedding_model_status": "loaded"
  }
}

# GET /logs - Recent log entries with filtering
{
  "logs": [
    {
      "timestamp": "2025-09-04T12:00:00Z",
      "level": "INFO",
      "message": "CBR query completed successfully",
      "component": "cbr_tools",
      "request_id": "req_12345",
      "latency_ms": 95.2
    }
  ],
  "total_count": 1,
  "page": 1,
  "per_page": 50
}
```

### Internal Storage Formats

```python
# Log file format (JSON Lines)
{"timestamp": "2025-09-04T12:00:00.123Z", "level": "INFO", "component": "server", "message": "Server started", "metadata": {"port": 8080}}
{"timestamp": "2025-09-04T12:00:01.456Z", "level": "INFO", "component": "cbr_tools", "message": "Query processed", "request_id": "req_001", "latency_ms": 85.2}

# Metrics file format (CSV for lightweight storage)
# system_metrics.csv
timestamp,memory_mb,memory_percent,cpu_percent,disk_gb,disk_percent,uptime
2025-09-04T12:00:00Z,256.5,12.8,15.2,2.1,25.3,3600
2025-09-04T12:00:30Z,258.1,12.9,16.8,2.1,25.3,3630
```

This data specification ensures comprehensive storage and tracking of all production stability metrics while maintaining compatibility with the existing ChromaDB-based CBR functionality.