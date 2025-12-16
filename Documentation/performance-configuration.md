# CBR MCP Server - Performance Configuration Guide

> Last Updated: 2025-12-11
> Version: 2.0.0
> Related Spec: 2025-11-05-local-performance-optimization

## Overview

This guide documents all performance configuration options available in the CBR MCP Server following the Phase 2 local performance optimization. The server implements memory management, query caching, lazy loading, and startup optimizations to achieve sub-200ms query latency and <500MB memory usage.

## Configuration Structure

Performance settings are organized into five main sections:

```yaml
performance:
  memory: {...}           # Memory management settings
  cache: {...}            # Result caching configuration
  lazy_loading: {...}     # Lazy loading options
  cache_warming: {...}    # Cache pre-warming settings
  index_warming: {...}    # Index pre-warming settings
```

## Memory Management Configuration

Controls memory usage limits and monitoring for local resource constraints.

### Configuration Options

```yaml
performance:
  memory:
    # Maximum memory allocation (MB)
    # Target: <500MB for local development
    # Range: 256-1024
    # Default: 512
    max_memory_mb: 512

    # Memory pressure warning threshold (0.0-1.0)
    # Triggers warning when usage exceeds this percentage
    # Default: 0.8 (80%)
    warning_threshold: 0.8

    # Enable automatic memory pressure detection
    # Default: true
    auto_detect_pressure: true

    # Memory check interval (seconds)
    # How often to check memory usage
    # Default: 30.0
    check_interval: 30.0
```

### Memory Manager Features

The `MemoryManager` component provides:

- **Real-time Memory Tracking**: Monitors RSS (Resident Set Size) memory usage
- **Pressure Detection**: Warns when approaching configured limits
- **Integration with ResourceMonitor**: Works with existing monitoring infrastructure
- **Thread-safe Operations**: Safe for concurrent access

### Environment Variable Overrides

```bash
# Override memory limits
export CBR_MAX_MEMORY_MB=512
export CBR_MEMORY_WARNING_THRESHOLD=0.8

# Enable debug logging for memory tracking
export CBR_MEMORY_DEBUG=1
```

### Example Configurations

**Low Memory (256MB limit)**:
```yaml
performance:
  memory:
    max_memory_mb: 256
    warning_threshold: 0.75
```

**Standard Development (512MB limit)**:
```yaml
performance:
  memory:
    max_memory_mb: 512
    warning_threshold: 0.8
```

**High Performance (1GB limit)**:
```yaml
performance:
  memory:
    max_memory_mb: 1024
    warning_threshold: 0.85
```

## Cache Configuration

Controls the result caching system that provides 70%+ cache hit rates.

### Configuration Options

```yaml
performance:
  cache:
    # Maximum number of cached results
    # Default: 1000
    max_size: 1000

    # Cache entry time-to-live (seconds)
    # How long results stay in cache
    # Default: 3600 (1 hour)
    ttl_seconds: 3600

    # Eviction policy
    # Options: "LRU" (Least Recently Used)
    # Default: "LRU"
    eviction_policy: "LRU"

    # Enable cache metrics tracking
    # Default: true
    enable_metrics: true

    # Cache cleanup interval (seconds)
    # How often to run eviction checks
    # Default: 300 (5 minutes)
    cleanup_interval: 300
```

### Cache System Features

The `ResultCache` component provides:

- **LRU Eviction**: Automatically removes least recently used entries
- **TTL Support**: Entries expire after configured time-to-live
- **Hit/Miss Tracking**: Comprehensive metrics for cache effectiveness
- **Thread-safe**: Safe for concurrent query access
- **Memory-aware**: Respects overall memory limits

### Cache Metrics

The cache tracks these metrics:

- **Hit Rate**: Percentage of queries served from cache
- **Miss Rate**: Percentage of queries requiring database access
- **Entry Count**: Current number of cached results
- **Eviction Count**: Total cache evictions performed

### Environment Variable Overrides

```bash
# Override cache settings
export CBR_CACHE_MAX_SIZE=1000
export CBR_CACHE_TTL_SECONDS=3600

# Disable caching (for testing)
export CBR_CACHE_ENABLED=false
```

### Example Configurations

**High Cache Hit Rate (Large Cache)**:
```yaml
performance:
  cache:
    max_size: 5000
    ttl_seconds: 7200  # 2 hours
    eviction_policy: "LRU"
```

**Memory Constrained (Small Cache)**:
```yaml
performance:
  cache:
    max_size: 500
    ttl_seconds: 1800  # 30 minutes
    eviction_policy: "LRU"
```

**Development (Fast Expiration)**:
```yaml
performance:
  cache:
    max_size: 1000
    ttl_seconds: 600  # 10 minutes
    eviction_policy: "LRU"
```

## Lazy Loading Configuration

Controls on-demand loading of embeddings and case data to reduce startup time and memory footprint.

### Configuration Options

```yaml
performance:
  lazy_loading:
    # Enable lazy loading system
    # Default: true
    enabled: true

    # Preload frequently accessed cases
    # Default: true
    preload_hot_cases: true

    # Number of hot cases to preload
    # Default: 50
    hot_case_count: 50

    # Enable background loading
    # Default: true
    background_loading_enabled: true

    # Access pattern window (hours)
    # How far back to analyze access patterns
    # Default: 24
    access_window_hours: 24

    # Minimum access frequency (0.0-1.0)
    # Threshold for considering a case "hot"
    # Default: 0.5
    min_access_frequency: 0.5

    # Batch size for loading operations
    # Default: 20
    batch_size: 20

    # Maximum concurrent load operations
    # Default: 5
    max_concurrent_loads: 5

    # Maximum lazy loader cache size
    # Default: 200
    max_cache_size: 200
```

### Lazy Loader Features

The `LazyLoader` component provides:

- **On-demand Loading**: Load cases only when accessed
- **Access Pattern Learning**: Identifies frequently accessed cases
- **Predictive Preloading**: Loads hot cases in background
- **Background Scheduling**: Non-blocking load operations
- **Memory Efficiency**: Reduces initial memory footprint

### Environment Variable Overrides

```bash
# Override lazy loading settings
export CBR_LAZY_LOADING_ENABLED=true
export CBR_HOT_CASE_COUNT=50
export CBR_LAZY_LOADING_BATCH_SIZE=20

# Disable lazy loading (load all at startup)
export CBR_LAZY_LOADING_ENABLED=false
```

### Example Configurations

**Aggressive Lazy Loading (Minimal Startup)**:
```yaml
performance:
  lazy_loading:
    enabled: true
    preload_hot_cases: false
    background_loading_enabled: true
    batch_size: 10
```

**Balanced (Recommended)**:
```yaml
performance:
  lazy_loading:
    enabled: true
    preload_hot_cases: true
    hot_case_count: 50
    background_loading_enabled: true
    batch_size: 20
```

**Eager Loading (Fast First Query)**:
```yaml
performance:
  lazy_loading:
    enabled: true
    preload_hot_cases: true
    hot_case_count: 100
    background_loading_enabled: true
    batch_size: 50
```

## Cache Warming Configuration

Pre-populates the result cache with frequently accessed queries during startup.

### Configuration Options

```yaml
performance:
  cache_warming:
    # Enable cache warming on startup
    # Default: false
    enabled: false

    # List of queries to pre-execute
    # Default: []
    queries:
      - "authentication code example"
      - "database connection"
      - "error handling pattern"
      - "logging configuration"
      - "caching strategy"
```

### Cache Warming Features

- **Startup Pre-loading**: Executes queries before first user request
- **Non-blocking**: Runs in background if configured
- **Failure Tolerant**: Continues even if individual queries fail

### Environment Variable Overrides

```bash
# Enable cache warming
export CBR_CACHE_WARMING_ENABLED=true

# Provide warming queries (comma-separated)
export CBR_CACHE_WARMING_QUERIES="auth example,database connection,error handling"
```

### Example Configurations

**Disabled (Default)**:
```yaml
performance:
  cache_warming:
    enabled: false
```

**Common Queries**:
```yaml
performance:
  cache_warming:
    enabled: true
    queries:
      - "user authentication"
      - "database query"
      - "API endpoint"
      - "error handling"
      - "logging setup"
```

**Project-Specific**:
```yaml
performance:
  cache_warming:
    enabled: true
    queries:
      - "React component example"
      - "Firebase authentication"
      - "TypeScript interface"
      - "Next.js API route"
```

## Index Warming Configuration

Pre-warms ChromaDB HNSW index structures to reduce first query latency.

### Configuration Options

```yaml
performance:
  index_warming:
    # Enable index warming on startup
    # Default: false
    enabled: false

    # Categories to warm indexes for
    # Default: ["code", "orchestration", "best-practice"]
    categories:
      - "code"
      - "orchestration"
      - "best-practice"
      - "anti-pattern"

    # Number of warming queries per category
    # Default: 3
    warmup_query_count: 3
```

### Index Warming Features

- **HNSW Index Pre-loading**: Populates internal index caches
- **Background Execution**: Non-blocking startup operation
- **Category-based**: Warms indexes for specific case categories
- **Latency Reduction**: Reduces first query time by 30-50%

### Environment Variable Overrides

```bash
# Enable index warming
export CBR_INDEX_WARMING_ENABLED=true
export CBR_INDEX_WARMING_CATEGORIES="code,orchestration,best-practice"
export CBR_INDEX_WARMUP_QUERY_COUNT=3
```

### Example Configurations

**Disabled (Fastest Startup)**:
```yaml
performance:
  index_warming:
    enabled: false
```

**Basic Warming**:
```yaml
performance:
  index_warming:
    enabled: true
    categories:
      - "code"
      - "orchestration"
    warmup_query_count: 2
```

**Comprehensive Warming**:
```yaml
performance:
  index_warming:
    enabled: true
    categories:
      - "code"
      - "orchestration"
      - "best-practice"
      - "anti-pattern"
    warmup_query_count: 5
```

## Complete Configuration Examples

### Minimal (Fastest Startup)

```yaml
performance:
  memory:
    max_memory_mb: 256
    warning_threshold: 0.75
  cache:
    max_size: 500
    ttl_seconds: 1800
    eviction_policy: "LRU"
  lazy_loading:
    enabled: true
    preload_hot_cases: false
    batch_size: 10
  cache_warming:
    enabled: false
  index_warming:
    enabled: false
```

### Balanced (Recommended)

```yaml
performance:
  memory:
    max_memory_mb: 512
    warning_threshold: 0.8
  cache:
    max_size: 1000
    ttl_seconds: 3600
    eviction_policy: "LRU"
  lazy_loading:
    enabled: true
    preload_hot_cases: true
    hot_case_count: 50
    background_loading_enabled: true
    batch_size: 20
  cache_warming:
    enabled: false
  index_warming:
    enabled: true
    categories:
      - "code"
      - "orchestration"
    warmup_query_count: 3
```

### Maximum Performance (Best Latency)

```yaml
performance:
  memory:
    max_memory_mb: 1024
    warning_threshold: 0.85
  cache:
    max_size: 5000
    ttl_seconds: 7200
    eviction_policy: "LRU"
  lazy_loading:
    enabled: true
    preload_hot_cases: true
    hot_case_count: 100
    background_loading_enabled: true
    batch_size: 50
  cache_warming:
    enabled: true
    queries:
      - "authentication"
      - "database"
      - "error handling"
      - "logging"
      - "caching"
  index_warming:
    enabled: true
    categories:
      - "code"
      - "orchestration"
      - "best-practice"
      - "anti-pattern"
    warmup_query_count: 5
```

## Performance Targets

With proper configuration, the CBR MCP Server achieves:

- **Query Latency**: <200ms (p95) for typical queries
- **Memory Usage**: <500MB peak with standard case base (135 cases)
- **Cache Hit Rate**: >70% for repeated queries
- **Startup Time**: <5 seconds (without warming, <8 seconds with full warming)
- **Concurrent Throughput**: 10+ concurrent queries without degradation

## Configuration Best Practices

1. **Start with Balanced Configuration**: Use the recommended balanced config as baseline
2. **Profile Your Workload**: Measure actual query patterns before optimizing
3. **Adjust Memory Limits**: Set `max_memory_mb` based on available system resources
4. **Enable Caching**: Always enable caching for production workloads
5. **Use Lazy Loading**: Keep enabled unless you need instant first-query performance
6. **Selective Index Warming**: Only warm indexes for categories you frequently query
7. **Monitor Cache Hit Rate**: Aim for >70% hit rate, adjust `max_size` and `ttl_seconds` accordingly
8. **Test Configuration Changes**: Always benchmark after configuration changes

## Troubleshooting

### High Memory Usage

If memory usage exceeds limits:

1. Reduce `memory.max_memory_mb`
2. Decrease `cache.max_size`
3. Lower `lazy_loading.max_cache_size`
4. Disable cache warming and index warming

### Low Cache Hit Rate

If cache hit rate is below 70%:

1. Increase `cache.max_size`
2. Increase `cache.ttl_seconds`
3. Enable `cache_warming` with common queries
4. Check query variations (slight wording differences cause misses)

### Slow Startup

If startup time exceeds 5 seconds:

1. Disable `cache_warming`
2. Disable `index_warming`
3. Reduce `lazy_loading.hot_case_count`
4. Set `lazy_loading.preload_hot_cases: false`

### Slow First Query

If first query is slow despite optimizations:

1. Enable `index_warming`
2. Increase `index_warming.warmup_query_count`
3. Enable `cache_warming` with similar query
4. Set `lazy_loading.preload_hot_cases: true`

## See Also

- [Performance Tuning Guide](./performance-tuning-guide.md) - Advanced optimization strategies
- [Benchmark Results](./benchmark-results.md) - Measured performance metrics
- [Performance Troubleshooting](./performance-troubleshooting.md) - Detailed problem resolution
- [Monitoring Setup Guide](./monitoring-setup-guide.md) - Performance monitoring configuration
