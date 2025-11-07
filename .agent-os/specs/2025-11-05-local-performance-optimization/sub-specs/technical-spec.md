# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-11-05-local-performance-optimization/spec.md

> Created: 2025-11-05
> Version: 1.0.0

## Technical Requirements

### Performance Targets

- **Query Response Latency:** <200ms for typical CBR queries (p95)
- **Memory Usage Efficiency:** <500MB peak usage for standard case bases (135 cases)
- **Cache Hit Rate:** 70%+ for frequently accessed cases
- **Startup Time:** <5 seconds for server initialization
- **Throughput:** Support 10+ concurrent queries without degradation

### Functional Requirements

1. **Memory Management**
   - Implement configurable embedding cache with size limits
   - Track and enforce memory consumption limits
   - Implement memory pressure detection and response
   - Support graceful degradation when approaching memory limits

2. **Query Performance**
   - Optimize ChromaDB query patterns for local single-user access
   - Implement connection pooling for database operations
   - Use batch operations for multiple similarity searches
   - Pre-compute and cache common query patterns

3. **Result Caching**
   - Implement LRU cache for query results
   - Cache frequently accessed case embeddings
   - Support configurable cache size and TTL
   - Implement cache warming for common queries

4. **Startup Optimization**
   - Lazy load embedding model (defer until first query)
   - Incremental database initialization
   - Pre-compile query patterns
   - Parallel initialization where possible

5. **Lazy Loading**
   - Load case embeddings on-demand
   - Implement background preloading for likely-needed cases
   - Cache loaded embeddings intelligently
   - Track access patterns for predictive loading

6. **Query Batching**
   - Detect and batch similar queries
   - Optimize batch size for throughput/latency tradeoff
   - Maintain query ordering and response mapping

7. **Index Optimization**
   - Configure ChromaDB HNSW parameters for local use
   - Optimize index refresh intervals
   - Implement index warming strategies
   - Monitor index size and fragmentation

## Technical Architecture

### Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Protocol Layer                    │
│              (Existing - No Changes)                     │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────▼────────────┐
         │  Performance Manager   │
         │  - Query Coordinator   │
         │  - Batch Processor     │
         │  - Cache Controller    │
         └───────────┬────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────┐   ┌──────▼──────┐   ┌────▼─────┐
│ Memory │   │    Query     │   │  Cache   │
│ Manager│   │  Optimizer   │   │  System  │
└───┬────┘   └──────┬───────┘   └────┬─────┘
    │               │                 │
    └───────────────┼─────────────────┘
                    │
         ┌──────────▼───────────┐
         │  CBR Retriever Core  │
         │  (Enhanced)          │
         └──────────┬───────────┘
                    │
         ┌──────────▼───────────┐
         │  ChromaDB + Model    │
         │  (Optimized Access)  │
         └──────────────────────┘
```

### Memory Manager Component

**Purpose:** Control and optimize memory usage for local execution constraints

**Key Classes:**
- `MemoryManager`: Central memory tracking and control
- `EmbeddingCacheManager`: Specialized cache for embedding vectors
- `MemoryPressureDetector`: Monitor and respond to memory limits
- `MemoryConfig`: Configuration for memory limits and policies

**Key Methods:**
```python
class MemoryManager:
    def check_memory_usage() -> MemoryMetrics
    def enforce_memory_limits() -> None
    def get_available_memory() -> int
    def trigger_cache_eviction() -> int

class EmbeddingCacheManager:
    def cache_embedding(case_id: str, embedding: np.ndarray) -> None
    def get_cached_embedding(case_id: str) -> Optional[np.ndarray]
    def evict_least_recently_used(count: int) -> int
    def warm_cache(case_ids: List[str]) -> None
```

### Query Optimizer Component

**Purpose:** Optimize query execution patterns for ChromaDB

**Key Classes:**
- `QueryOptimizer`: Query planning and optimization
- `ConnectionPool`: Database connection management
- `BatchCoordinator`: Query batching logic
- `QueryCache`: Query result caching

**Key Methods:**
```python
class QueryOptimizer:
    def optimize_query_plan(query: Query) -> OptimizedQuery
    def execute_with_optimization(query: Query) -> QueryResult
    def batch_queries(queries: List[Query]) -> BatchResult

class ConnectionPool:
    def get_connection() -> ChromaConnection
    def release_connection(conn: ChromaConnection) -> None
    def warm_pool() -> None
```

### Cache System Component

**Purpose:** High-performance result caching with LRU eviction

**Key Classes:**
- `ResultCache`: Main result caching system
- `CacheEntry`: Individual cache entry with metadata
- `CachePolicy`: Configurable cache behavior
- `CacheMetrics`: Cache performance tracking

**Key Methods:**
```python
class ResultCache:
    def get(key: str) -> Optional[CacheEntry]
    def set(key: str, value: Any, ttl: int) -> None
    def evict_expired() -> int
    def get_metrics() -> CacheMetrics
    def clear() -> None
```

### Lazy Loading Component

**Purpose:** On-demand loading of embeddings and case data

**Key Classes:**
- `LazyLoader`: Coordinated lazy loading
- `LoadScheduler`: Background loading scheduler
- `AccessPatternTracker`: Track usage patterns
- `PreloadStrategy`: Predictive preloading

**Key Methods:**
```python
class LazyLoader:
    def load_on_demand(case_id: str) -> CaseData
    def schedule_background_load(case_ids: List[str]) -> None
    def is_loaded(case_id: str) -> bool

class AccessPatternTracker:
    def record_access(case_id: str) -> None
    def predict_next_accesses() -> List[str]
    def get_hot_cases() -> List[str]
```

## Approach Options

### Option A: Aggressive Caching with Large Memory Footprint

**Description:** Maximize caching at the expense of memory usage, pre-loading all embeddings.

**Pros:**
- Fastest possible query performance
- Simplest implementation
- Predictable performance characteristics

**Cons:**
- May exceed 500MB memory target
- Wasteful for infrequently accessed cases
- Slow startup time due to pre-loading

**Decision:** Rejected - Violates memory efficiency requirement

### Option B: Minimal Caching with Pure Lazy Loading (Selected)

**Description:** Load everything on-demand with small in-memory cache using LRU eviction.

**Pros:**
- Meets memory constraints reliably
- Fast startup time
- Scales efficiently with case base size
- Adaptive to actual usage patterns

**Cons:**
- Cache misses result in database queries
- Requires sophisticated cache management
- More complex implementation

**Decision:** Selected - Best balance of performance and memory efficiency

**Rationale:** This approach provides optimal memory efficiency while maintaining good performance through intelligent caching. The LRU cache will naturally keep hot cases in memory while evicting rarely used data. Combined with predictive preloading, this achieves both performance and memory targets.

### Option C: Hybrid Approach with Fixed Hot Set

**Description:** Pre-load a fixed set of "hot" cases, lazy load the rest.

**Pros:**
- Guaranteed fast access to common cases
- Predictable memory usage
- Balanced approach

**Cons:**
- Requires manual hot set definition
- Less adaptive to changing patterns
- Risk of wrong hot set selection

**Decision:** Rejected - Less flexible than Option B

## External Dependencies

### New Libraries

- **cachetools** (Latest stable version)
  - **Purpose:** Production-grade LRU cache implementation
  - **Justification:** Provides efficient, thread-safe caching with multiple eviction policies
  - **Alternatives Considered:** functools.lru_cache (insufficient features), Redis (overkill for local)

- **memory_profiler** (Latest stable version)
  - **Purpose:** Memory usage profiling and tracking
  - **Justification:** Essential for validating memory optimization work
  - **Usage:** Development and testing only

- **psutil** (Latest stable version)
  - **Purpose:** System resource monitoring (memory, CPU)
  - **Justification:** Already used for ResourceMonitor, will extend usage for memory pressure detection
  - **Note:** May already be installed

### Configuration Changes

**pyproject.toml additions:**
```toml
[tool.cbr-mcp-server.performance]
# Memory limits in MB
max_memory_mb = 500
embedding_cache_size = 1000  # Max embeddings to cache
query_cache_size = 500       # Max query results to cache

# Cache TTL in seconds
embedding_cache_ttl = 3600
query_cache_ttl = 300

# Startup optimization
lazy_load_embeddings = true
parallel_init = true
preload_hot_cases = true
hot_case_count = 50

# Query optimization
connection_pool_size = 5
batch_query_threshold = 3
batch_max_wait_ms = 50

# Index optimization
hnsw_ef_construction = 100
hnsw_ef_search = 50
hnsw_m = 16
```

## Performance Testing Strategy

### Benchmark Scenarios

1. **Cold Start Query:** Measure first query after server start
2. **Warm Cache Query:** Measure query with cache hit
3. **Bulk Query:** Measure 10 concurrent queries
4. **Memory Stress:** Measure behavior at memory limit
5. **Cache Churn:** Measure performance with high cache turnover

### Performance Baselines

Establish baseline metrics before optimization:
- Current query latency (p50, p95, p99)
- Current memory usage patterns
- Current startup time
- Current cache hit rates (if any existing caching)

### Profiling Tools

- **cProfile:** Python code profiling for hotspot identification
- **memory_profiler:** Memory usage profiling per function
- **py-spy:** Sampling profiler for production-like profiling
- **Chrome DevTools:** If FastAPI endpoints used for testing

## Integration Points

### Existing Components to Modify

1. **ProductionCBRRetriever** (src/cbr_mcp_server/server.py)
   - Add cache layer integration
   - Implement lazy loading for embeddings
   - Add memory usage tracking

2. **CBRMCPServer** (src/cbr_mcp_server/server.py)
   - Add startup optimization hooks
   - Integrate query optimizer
   - Add performance monitoring

3. **PerformanceTracker** (src/cbr_mcp_server/server.py)
   - Extend to track query latency
   - Add cache hit/miss metrics
   - Add memory usage metrics

### New Components to Add

1. **performance/memory_manager.py:** Memory management system
2. **performance/query_optimizer.py:** Query optimization
3. **performance/cache_system.py:** Result and embedding caching
4. **performance/lazy_loader.py:** Lazy loading coordination
5. **performance/__init__.py:** Performance module exports

## Backward Compatibility

- All existing MCP tool interfaces remain unchanged
- Configuration changes are additive (new settings with defaults)
- Legacy FastAPI interface maintains current behavior
- Existing test suite must continue to pass
- No breaking changes to external API contracts

## Monitoring and Observability

### New Metrics to Track

- `query_latency_ms`: Query execution time histogram
- `cache_hit_rate`: Percentage of cache hits
- `memory_usage_mb`: Current memory consumption
- `embedding_cache_size`: Number of cached embeddings
- `query_cache_size`: Number of cached query results
- `startup_time_ms`: Server initialization time

### Performance Dashboards

Extend existing health dashboard to include:
- Real-time query latency graph
- Cache hit rate over time
- Memory usage graph with limit indicator
- Slow query log (queries >200ms)

## Risk Mitigation

### Technical Risks

1. **Risk:** Cache invalidation complexity
   - **Mitigation:** Use simple TTL-based expiration, no complex invalidation logic

2. **Risk:** Memory estimation inaccuracy
   - **Mitigation:** Conservative memory limits, active monitoring, graceful degradation

3. **Risk:** Query performance regression
   - **Mitigation:** Comprehensive benchmarking, A/B testing capability, rollback plan

4. **Risk:** ChromaDB version compatibility
   - **Mitigation:** Test with current ChromaDB version, document version requirements

### Performance Risks

1. **Risk:** Cache thrashing with poor hit rates
   - **Mitigation:** Adaptive cache sizing, access pattern analysis, cache warming

2. **Risk:** Lazy loading latency spikes
   - **Mitigation:** Predictive preloading, background loading, monitoring

3. **Risk:** Memory pressure affecting other processes
   - **Mitigation:** Configurable limits, memory pressure detection, automatic throttling
