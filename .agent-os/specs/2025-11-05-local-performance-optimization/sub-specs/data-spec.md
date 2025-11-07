# Data Specification

This is the data specification for the spec detailed in @.agent-os/specs/2025-11-05-local-performance-optimization/spec.md

> Created: 2025-11-05
> Version: 1.0.0

## Data Models

### Performance Configuration Models

#### MemoryConfig

Configuration for memory management system.

```python
from pydantic import BaseModel, Field
from typing import Optional

class MemoryConfig(BaseModel):
    """Configuration for memory management."""

    max_memory_mb: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="Maximum memory usage in MB"
    )

    embedding_cache_size: int = Field(
        default=1000,
        ge=100,
        le=5000,
        description="Maximum number of embeddings to cache"
    )

    memory_check_interval_sec: float = Field(
        default=10.0,
        ge=1.0,
        le=60.0,
        description="Interval for memory usage checks in seconds"
    )

    pressure_threshold_pct: float = Field(
        default=0.85,
        ge=0.5,
        le=0.95,
        description="Memory pressure threshold as percentage of max"
    )

    emergency_eviction_pct: float = Field(
        default=0.30,
        ge=0.10,
        le=0.50,
        description="Percentage of cache to evict under pressure"
    )
```

#### CacheConfig

Configuration for caching system.

```python
class CacheConfig(BaseModel):
    """Configuration for result and embedding caching."""

    query_cache_size: int = Field(
        default=500,
        ge=50,
        le=2000,
        description="Maximum number of query results to cache"
    )

    query_cache_ttl_sec: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Query cache TTL in seconds"
    )

    embedding_cache_ttl_sec: int = Field(
        default=3600,
        ge=300,
        le=7200,
        description="Embedding cache TTL in seconds"
    )

    enable_cache_warming: bool = Field(
        default=True,
        description="Enable predictive cache warming"
    )

    warm_cache_on_startup: bool = Field(
        default=True,
        description="Pre-load hot cases on startup"
    )

    hot_case_count: int = Field(
        default=50,
        ge=10,
        le=200,
        description="Number of hot cases to pre-load"
    )
```

#### QueryOptimizationConfig

Configuration for query optimization.

```python
class QueryOptimizationConfig(BaseModel):
    """Configuration for query optimization."""

    connection_pool_size: int = Field(
        default=5,
        ge=1,
        le=20,
        description="ChromaDB connection pool size"
    )

    batch_query_threshold: int = Field(
        default=3,
        ge=2,
        le=10,
        description="Minimum queries to trigger batching"
    )

    batch_max_wait_ms: int = Field(
        default=50,
        ge=10,
        le=200,
        description="Maximum wait time for batch accumulation"
    )

    enable_query_batching: bool = Field(
        default=True,
        description="Enable automatic query batching"
    )

    parallel_query_execution: bool = Field(
        default=True,
        description="Execute independent queries in parallel"
    )
```

#### LazyLoadingConfig

Configuration for lazy loading system.

```python
class LazyLoadingConfig(BaseModel):
    """Configuration for lazy loading."""

    enabled: bool = Field(
        default=True,
        description="Enable lazy loading of embeddings"
    )

    background_loading: bool = Field(
        default=True,
        description="Enable background preloading"
    )

    preload_threshold: float = Field(
        default=0.7,
        ge=0.5,
        le=0.95,
        description="Access probability threshold for preloading"
    )

    access_pattern_window: int = Field(
        default=1000,
        ge=100,
        le=5000,
        description="Number of accesses to track for pattern analysis"
    )

    preload_batch_size: int = Field(
        default=10,
        ge=5,
        le=50,
        description="Number of cases to preload in batch"
    )
```

#### IndexOptimizationConfig

Configuration for ChromaDB index optimization.

```python
class IndexOptimizationConfig(BaseModel):
    """Configuration for ChromaDB HNSW index optimization."""

    hnsw_ef_construction: int = Field(
        default=100,
        ge=50,
        le=500,
        description="HNSW ef_construction parameter"
    )

    hnsw_ef_search: int = Field(
        default=50,
        ge=10,
        le=200,
        description="HNSW ef_search parameter"
    )

    hnsw_m: int = Field(
        default=16,
        ge=8,
        le=64,
        description="HNSW M parameter (number of connections)"
    )

    enable_index_warming: bool = Field(
        default=True,
        description="Warm index on startup"
    )
```

### Cache Data Models

#### CacheEntry

Represents a single cache entry with metadata.

```python
from datetime import datetime
from typing import Any, Optional

class CacheEntry(BaseModel):
    """Cache entry with value and metadata."""

    key: str = Field(description="Cache key")
    value: Any = Field(description="Cached value")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(default=0)
    ttl_seconds: Optional[int] = Field(default=None)
    size_bytes: int = Field(default=0, description="Approximate size")

    def is_expired(self) -> bool:
        """Check if entry has exceeded TTL."""
        if self.ttl_seconds is None:
            return False
        age = (datetime.utcnow() - self.created_at).total_seconds()
        return age > self.ttl_seconds

    def update_access(self) -> None:
        """Update access metadata."""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
```

#### CacheMetrics

Metrics for cache performance tracking.

```python
class CacheMetrics(BaseModel):
    """Cache performance metrics."""

    total_requests: int = Field(default=0)
    cache_hits: int = Field(default=0)
    cache_misses: int = Field(default=0)
    evictions: int = Field(default=0)
    current_size: int = Field(default=0)
    max_size: int = Field(default=0)
    memory_usage_mb: float = Field(default=0.0)

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests

    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate."""
        return 1.0 - self.hit_rate
```

### Memory Tracking Models

#### MemoryMetrics

System memory usage metrics.

```python
class MemoryMetrics(BaseModel):
    """Memory usage metrics."""

    current_mb: float = Field(description="Current memory usage in MB")
    peak_mb: float = Field(description="Peak memory usage in MB")
    limit_mb: int = Field(description="Configured memory limit in MB")
    available_mb: float = Field(description="Available memory in MB")

    @property
    def usage_percentage(self) -> float:
        """Calculate percentage of limit used."""
        return (self.current_mb / self.limit_mb) * 100

    @property
    def is_under_pressure(self) -> bool:
        """Check if memory is under pressure."""
        return self.usage_percentage > 85.0
```

#### MemoryAllocation

Detailed memory allocation breakdown.

```python
class MemoryAllocation(BaseModel):
    """Breakdown of memory allocation."""

    embedding_cache_mb: float = Field(default=0.0)
    query_cache_mb: float = Field(default=0.0)
    model_mb: float = Field(default=0.0)
    database_mb: float = Field(default=0.0)
    overhead_mb: float = Field(default=0.0)

    @property
    def total_mb(self) -> float:
        """Calculate total allocated memory."""
        return (
            self.embedding_cache_mb
            + self.query_cache_mb
            + self.model_mb
            + self.database_mb
            + self.overhead_mb
        )
```

### Performance Tracking Models

#### QueryPerformanceMetrics

Per-query performance metrics.

```python
class QueryPerformanceMetrics(BaseModel):
    """Performance metrics for a single query."""

    query_id: str = Field(description="Unique query identifier")
    query_type: str = Field(description="Type of query (retrieve, search, etc.)")

    total_time_ms: float = Field(description="Total query time in milliseconds")
    cache_lookup_ms: float = Field(default=0.0)
    embedding_generation_ms: float = Field(default=0.0)
    database_query_ms: float = Field(default=0.0)
    result_processing_ms: float = Field(default=0.0)

    cache_hit: bool = Field(default=False)
    result_count: int = Field(default=0)

    @property
    def meets_target(self) -> bool:
        """Check if query meets 200ms target."""
        return self.total_time_ms < 200.0
```

#### PerformanceSnapshot

Aggregate performance snapshot.

```python
from typing import List

class PerformanceSnapshot(BaseModel):
    """Aggregate performance snapshot."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Latency statistics
    query_count: int = Field(default=0)
    avg_latency_ms: float = Field(default=0.0)
    p50_latency_ms: float = Field(default=0.0)
    p95_latency_ms: float = Field(default=0.0)
    p99_latency_ms: float = Field(default=0.0)

    # Cache statistics
    cache_metrics: CacheMetrics

    # Memory statistics
    memory_metrics: MemoryMetrics

    # Query breakdown
    queries_under_200ms: int = Field(default=0)
    queries_over_200ms: int = Field(default=0)

    @property
    def target_compliance_rate(self) -> float:
        """Calculate percentage of queries meeting 200ms target."""
        if self.query_count == 0:
            return 0.0
        return (self.queries_under_200ms / self.query_count) * 100
```

### Access Pattern Models

#### AccessPattern

Case access pattern tracking.

```python
class AccessPattern(BaseModel):
    """Track access patterns for a case."""

    case_id: str = Field(description="Case identifier")
    total_accesses: int = Field(default=0)
    last_access: datetime = Field(default_factory=datetime.utcnow)
    access_frequency: float = Field(
        default=0.0,
        description="Accesses per hour"
    )

    def record_access(self) -> None:
        """Record a new access."""
        self.total_accesses += 1
        self.last_access = datetime.utcnow()

    def calculate_frequency(self, window_hours: float = 1.0) -> float:
        """Calculate access frequency."""
        # Implementation would track accesses in time window
        return self.access_frequency
```

## Configuration Storage

### Configuration File Format

Performance settings will be added to the existing configuration system. No new configuration files required - extend existing `CBRServerConfig` in server.py:

```python
class CBRServerConfig(BaseModel):
    """Extended CBR Server Configuration."""

    # Existing fields...

    # Performance optimization settings
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    query_optimization: QueryOptimizationConfig = Field(
        default_factory=QueryOptimizationConfig
    )
    lazy_loading: LazyLoadingConfig = Field(
        default_factory=LazyLoadingConfig
    )
    index_optimization: IndexOptimizationConfig = Field(
        default_factory=IndexOptimizationConfig
    )
```

### Environment Variable Overrides

Support environment variable overrides for configuration:

```bash
# Memory settings
CBR_MAX_MEMORY_MB=500
CBR_EMBEDDING_CACHE_SIZE=1000

# Cache settings
CBR_QUERY_CACHE_SIZE=500
CBR_QUERY_CACHE_TTL_SEC=300

# Query optimization
CBR_CONNECTION_POOL_SIZE=5
CBR_ENABLE_QUERY_BATCHING=true

# Lazy loading
CBR_LAZY_LOADING_ENABLED=true
CBR_BACKGROUND_LOADING=true
```

## Database Schema Changes

**No database schema changes required.** All optimizations work with existing ChromaDB schema and metadata structure.

## API Contracts

**No API contract changes required.** All MCP tool interfaces remain unchanged:

- `cbr_retrieve`: No changes
- `cbr_search_category`: No changes
- `cbr_find_similar`: No changes

MCP resources remain unchanged:
- `cbr://categories`
- `cbr://examples/{id}`
- `cbr://stats`

Internal performance improvements are transparent to API consumers.

## Performance Metrics Schema

### Metrics Export Format

Performance metrics will be exported in JSON format for external monitoring:

```json
{
  "timestamp": "2025-11-05T10:30:00Z",
  "snapshot": {
    "query_count": 1000,
    "avg_latency_ms": 145.3,
    "p50_latency_ms": 132.0,
    "p95_latency_ms": 187.5,
    "p99_latency_ms": 195.2,
    "target_compliance_rate": 98.5
  },
  "cache": {
    "hit_rate": 0.73,
    "total_requests": 1000,
    "cache_hits": 730,
    "cache_misses": 270,
    "current_size": 450,
    "memory_usage_mb": 45.3
  },
  "memory": {
    "current_mb": 387.5,
    "peak_mb": 412.8,
    "limit_mb": 500,
    "usage_percentage": 77.5
  }
}
```

## Data Migration

**No data migration required.** All optimizations are runtime enhancements that work with existing data.

## Backward Compatibility

All data models are additive:
- Existing configuration continues to work with defaults
- No breaking changes to data structures
- All existing tests continue to pass
