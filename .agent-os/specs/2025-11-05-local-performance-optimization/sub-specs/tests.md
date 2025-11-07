# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-11-05-local-performance-optimization/spec.md

> Created: 2025-11-05
> Version: 1.0.0

## Test Coverage Strategy

All tests will follow TDD principles - tests written before implementation. Each component will have unit tests, integration tests, and performance benchmarks.

## Unit Tests

### Memory Manager Tests (tests/unit/test_memory_manager.py)

**MemoryManager Component Tests:**
- `test_memory_manager_initialization` - Verify MemoryManager initializes with correct config
- `test_check_memory_usage` - Test memory usage tracking returns accurate metrics
- `test_enforce_memory_limits_under_limit` - Verify no action when under memory limit
- `test_enforce_memory_limits_over_limit` - Verify cache eviction triggered when over limit
- `test_get_available_memory` - Test available memory calculation
- `test_trigger_cache_eviction` - Verify cache eviction reduces memory usage
- `test_memory_pressure_detection` - Test memory pressure threshold detection
- `test_emergency_eviction_percentage` - Verify emergency eviction removes correct percentage

**EmbeddingCacheManager Component Tests:**
- `test_cache_embedding` - Test caching of embedding vectors
- `test_get_cached_embedding_hit` - Verify cache hit returns correct embedding
- `test_get_cached_embedding_miss` - Verify cache miss returns None
- `test_evict_least_recently_used` - Test LRU eviction removes oldest entries
- `test_warm_cache` - Verify cache warming pre-loads specified embeddings
- `test_cache_size_limit` - Test cache respects size limit
- `test_cache_ttl_expiration` - Verify expired entries are not returned
- `test_embedding_size_calculation` - Test memory size calculation for embeddings

**MemoryPressureDetector Tests:**
- `test_detect_pressure_under_threshold` - Verify no pressure detected under threshold
- `test_detect_pressure_over_threshold` - Verify pressure detected over threshold
- `test_pressure_callback_triggered` - Test callback execution on pressure detection
- `test_continuous_monitoring` - Verify continuous pressure monitoring works

### Query Optimizer Tests (tests/unit/test_query_optimizer.py)

**QueryOptimizer Component Tests:**
- `test_optimize_query_plan` - Test query plan optimization logic
- `test_execute_with_optimization` - Verify optimized execution path
- `test_batch_queries_multiple` - Test batching of multiple similar queries
- `test_batch_queries_single` - Verify single query bypasses batching
- `test_query_cache_integration` - Test integration with query result cache
- `test_connection_reuse` - Verify connection pool reuse
- `test_parallel_query_execution` - Test parallel execution of independent queries

**ConnectionPool Component Tests:**
- `test_connection_pool_initialization` - Verify pool initializes with correct size
- `test_get_connection` - Test connection acquisition from pool
- `test_release_connection` - Test connection release back to pool
- `test_connection_pool_exhaustion` - Verify behavior when pool exhausted
- `test_warm_pool` - Test pool warming on startup
- `test_connection_health_check` - Verify unhealthy connections are replaced

**BatchCoordinator Component Tests:**
- `test_batch_accumulation` - Test query accumulation for batching
- `test_batch_timeout` - Verify batch executes after timeout
- `test_batch_size_threshold` - Test batch executes when size threshold reached
- `test_batch_result_mapping` - Verify results correctly mapped to original queries
- `test_batch_error_handling` - Test error handling in batch execution

### Cache System Tests (tests/unit/test_cache_system.py)

**ResultCache Component Tests:**
- `test_cache_set_and_get` - Test basic cache set/get operations
- `test_cache_miss` - Verify cache miss behavior
- `test_cache_ttl_expiration` - Test TTL-based expiration
- `test_lru_eviction` - Verify LRU eviction policy
- `test_cache_size_limit` - Test cache respects size limit
- `test_evict_expired` - Test manual expiration of old entries
- `test_get_metrics` - Verify cache metrics calculation
- `test_cache_clear` - Test cache clearing functionality

**CacheEntry Component Tests:**
- `test_cache_entry_creation` - Test CacheEntry initialization
- `test_is_expired_not_expired` - Verify not expired when within TTL
- `test_is_expired_expired` - Verify expired when TTL exceeded
- `test_update_access` - Test access metadata update
- `test_size_calculation` - Verify size calculation for entries

**CachePolicy Component Tests:**
- `test_policy_evaluation` - Test cache policy evaluation logic
- `test_policy_size_based` - Test size-based eviction policy
- `test_policy_ttl_based` - Test TTL-based eviction policy
- `test_policy_lru_based` - Test LRU eviction policy

### Lazy Loader Tests (tests/unit/test_lazy_loader.py)

**LazyLoader Component Tests:**
- `test_load_on_demand` - Test on-demand case loading
- `test_load_on_demand_cached` - Verify cached cases skip loading
- `test_schedule_background_load` - Test background loading scheduling
- `test_is_loaded` - Test loaded state checking
- `test_concurrent_loading` - Verify thread-safe concurrent loading
- `test_loading_error_handling` - Test error handling during loading

**AccessPatternTracker Component Tests:**
- `test_record_access` - Test access recording
- `test_predict_next_accesses` - Test access prediction algorithm
- `test_get_hot_cases` - Verify hot case identification
- `test_access_window_management` - Test sliding window for access tracking
- `test_frequency_calculation` - Test access frequency calculation

**PreloadStrategy Component Tests:**
- `test_identify_preload_candidates` - Test candidate identification
- `test_preload_threshold_filtering` - Test threshold-based filtering
- `test_preload_scheduling` - Test preload task scheduling
- `test_preload_batch_size` - Verify batch size limits respected

**LoadScheduler Component Tests:**
- `test_schedule_task` - Test background task scheduling
- `test_task_prioritization` - Verify task priority ordering
- `test_concurrent_task_execution` - Test parallel task execution
- `test_task_cancellation` - Test cancellation of scheduled tasks

## Integration Tests

### Performance Integration Tests (tests/integration/test_performance_integration.py)

**End-to-End Performance Tests:**
- `test_query_latency_under_target` - Verify queries complete under 200ms
- `test_memory_usage_under_limit` - Verify memory stays under 500MB limit
- `test_cache_hit_rate_target` - Verify cache achieves 70%+ hit rate
- `test_startup_time_under_target` - Verify startup completes under 5 seconds
- `test_concurrent_query_performance` - Test performance under concurrent load
- `test_cold_start_performance` - Test performance on cold start
- `test_warm_cache_performance` - Test performance with warm cache

**Memory Integration Tests:**
- `test_memory_manager_cache_integration` - Test MemoryManager with CacheSystem
- `test_memory_pressure_triggers_eviction` - Verify eviction on memory pressure
- `test_memory_tracking_accuracy` - Test memory tracking matches actual usage
- `test_memory_limits_enforced_end_to_end` - Verify limits enforced in real scenarios

**Query Optimization Integration Tests:**
- `test_query_optimizer_with_chromadb` - Test optimizer with real ChromaDB
- `test_batch_query_execution_performance` - Measure batching performance improvement
- `test_connection_pool_with_concurrent_queries` - Test pool under concurrent load
- `test_query_cache_integration` - Test query cache with real queries

**Lazy Loading Integration Tests:**
- `test_lazy_loading_reduces_startup_time` - Verify lazy loading improves startup
- `test_on_demand_loading_performance` - Test on-demand loading latency
- `test_background_preloading_effectiveness` - Verify preloading improves hit rates
- `test_access_pattern_learning` - Test pattern learning over time

### MCP Protocol Integration Tests (tests/integration/test_mcp_performance_integration.py)

**MCP Tool Performance Tests:**
- `test_cbr_retrieve_performance` - Test cbr_retrieve tool meets latency target
- `test_cbr_search_category_performance` - Test cbr_search_category latency
- `test_cbr_find_similar_performance` - Test cbr_find_similar latency
- `test_multiple_tool_calls_performance` - Test performance of sequential tool calls
- `test_concurrent_tool_calls_performance` - Test concurrent MCP tool calls

**MCP Resource Performance Tests:**
- `test_categories_resource_performance` - Test categories resource latency
- `test_examples_resource_performance` - Test examples by ID resource latency
- `test_stats_resource_performance` - Test stats resource latency

## Performance Benchmarks

### Latency Benchmarks (tests/benchmarks/test_latency_benchmarks.py)

**Query Latency Benchmarks:**
- `benchmark_cold_query_latency` - Measure cold query latency
- `benchmark_warm_query_latency` - Measure warm query latency
- `benchmark_cached_query_latency` - Measure fully cached query latency
- `benchmark_bulk_query_latency` - Measure latency under bulk load
- `benchmark_concurrent_query_latency` - Measure latency with concurrent queries

**Component Latency Benchmarks:**
- `benchmark_embedding_generation_latency` - Measure embedding generation time
- `benchmark_chromadb_query_latency` - Measure ChromaDB query time
- `benchmark_cache_lookup_latency` - Measure cache lookup time
- `benchmark_lazy_loading_latency` - Measure lazy loading overhead

### Memory Benchmarks (tests/benchmarks/test_memory_benchmarks.py)

**Memory Usage Benchmarks:**
- `benchmark_baseline_memory_usage` - Measure baseline memory consumption
- `benchmark_full_cache_memory_usage` - Measure memory with full cache
- `benchmark_memory_under_load` - Measure memory during sustained load
- `benchmark_peak_memory_usage` - Measure peak memory consumption
- `benchmark_memory_after_eviction` - Measure memory after cache eviction

**Memory Component Benchmarks:**
- `benchmark_embedding_cache_memory` - Measure embedding cache memory
- `benchmark_query_cache_memory` - Measure query cache memory
- `benchmark_lazy_loading_memory` - Measure memory with lazy loading

### Throughput Benchmarks (tests/benchmarks/test_throughput_benchmarks.py)

**Throughput Benchmarks:**
- `benchmark_queries_per_second` - Measure sustained queries per second
- `benchmark_concurrent_throughput` - Measure throughput with concurrent queries
- `benchmark_batch_query_throughput` - Measure batching throughput improvement
- `benchmark_cache_enabled_throughput` - Measure throughput with caching

### Startup Benchmarks (tests/benchmarks/test_startup_benchmarks.py)

**Startup Time Benchmarks:**
- `benchmark_cold_start_time` - Measure server cold start time
- `benchmark_warm_start_time` - Measure server warm start time
- `benchmark_lazy_loading_startup` - Measure startup with lazy loading
- `benchmark_eager_loading_startup` - Measure startup with eager loading
- `benchmark_startup_components` - Break down startup time by component

## Regression Tests

### Performance Regression Tests (tests/regression/test_performance_regression.py)

**Regression Prevention Tests:**
- `test_no_latency_regression` - Verify no query latency regression vs baseline
- `test_no_memory_regression` - Verify no memory usage regression vs baseline
- `test_no_cache_regression` - Verify no cache hit rate regression vs baseline
- `test_no_startup_regression` - Verify no startup time regression vs baseline
- `test_no_throughput_regression` - Verify no throughput regression vs baseline

**Functionality Regression Tests:**
- `test_existing_functionality_preserved` - Verify all existing features work
- `test_existing_tests_pass` - Verify entire existing test suite passes
- `test_mcp_protocol_compliance_preserved` - Verify MCP protocol still compliant
- `test_accuracy_not_degraded` - Verify retrieval accuracy not affected

## Load Tests

### Load Testing (tests/load/test_performance_load.py)

**Sustained Load Tests:**
- `test_sustained_load_100_queries` - Test sustained 100 queries
- `test_sustained_load_1000_queries` - Test sustained 1000 queries
- `test_sustained_load_with_memory_limit` - Test load with memory constraints
- `test_sustained_load_cache_behavior` - Test cache behavior under sustained load

**Stress Tests:**
- `test_stress_concurrent_queries` - Stress test with many concurrent queries
- `test_stress_memory_pressure` - Stress test memory management
- `test_stress_cache_churn` - Stress test cache with high turnover
- `test_stress_lazy_loading` - Stress test lazy loading system

**Spike Tests:**
- `test_spike_sudden_load` - Test behavior with sudden load spike
- `test_spike_recovery` - Test recovery after load spike
- `test_spike_cache_warming` - Test cache warming during spike

## Profiling Tests

### Profiling Test Helpers (tests/profiling/test_profiling_helpers.py)

**Profiling Infrastructure Tests:**
- `test_cpu_profiler_integration` - Test cProfile integration
- `test_memory_profiler_integration` - Test memory_profiler integration
- `test_performance_report_generation` - Test automated report generation
- `test_hotspot_identification` - Test automatic hotspot detection

## Test Configuration

### Test Fixtures

**Performance Test Fixtures:**
```python
@pytest.fixture
def performance_config():
    """Provide test-optimized performance configuration."""
    return CBRServerConfig(
        memory=MemoryConfig(max_memory_mb=250, embedding_cache_size=500),
        cache=CacheConfig(query_cache_size=250, query_cache_ttl_sec=60),
        query_optimization=QueryOptimizationConfig(connection_pool_size=3),
    )

@pytest.fixture
def performance_baseline():
    """Provide baseline performance metrics for comparison."""
    return {
        "query_latency_ms": 200.0,
        "memory_usage_mb": 500.0,
        "cache_hit_rate": 0.70,
        "startup_time_sec": 5.0,
    }

@pytest.fixture
def mock_chromadb_collection():
    """Provide mock ChromaDB collection for testing."""
    # Mock implementation
    pass

@pytest.fixture
def sample_query_workload():
    """Provide sample query workload for testing."""
    return [
        {"query": "authentication", "type": "retrieve"},
        {"query": "database", "type": "search_category"},
        # ... more sample queries
    ]
```

### Test Data

**Test Cases:**
- Use existing 135-case case base for realistic testing
- Create small synthetic case base (20 cases) for fast unit tests
- Create large synthetic case base (500 cases) for stress tests

### Performance Assertion Helpers

```python
def assert_latency_under_target(latency_ms: float, target_ms: float = 200.0):
    """Assert query latency meets target."""
    assert latency_ms < target_ms, f"Latency {latency_ms}ms exceeds target {target_ms}ms"

def assert_memory_under_limit(memory_mb: float, limit_mb: float = 500.0):
    """Assert memory usage under limit."""
    assert memory_mb < limit_mb, f"Memory {memory_mb}MB exceeds limit {limit_mb}MB"

def assert_cache_hit_rate_target(hit_rate: float, target: float = 0.70):
    """Assert cache hit rate meets target."""
    assert hit_rate >= target, f"Cache hit rate {hit_rate:.2%} below target {target:.2%}"
```

## Test Execution Strategy

### Test Phases

1. **Unit Tests First:** Validate individual components in isolation
2. **Integration Tests:** Validate component interactions
3. **Performance Benchmarks:** Establish performance baselines
4. **Regression Tests:** Ensure no degradation
5. **Load Tests:** Validate under realistic load

### Continuous Integration

- Run unit tests on every commit
- Run integration tests on every PR
- Run performance benchmarks nightly
- Run regression tests before releases
- Run load tests weekly

### Test Coverage Goals

- Unit test coverage: 90%+ for performance components
- Integration test coverage: 80%+ for performance paths
- Benchmark coverage: All performance targets measured
- Regression coverage: All existing functionality tested
