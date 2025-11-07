# Performance Benchmark Tests

This directory contains performance baseline and benchmark tests for the CBR MCP Server.

## Setup

To run benchmark tests, you need to install `pytest-benchmark`:

```bash
pip install pytest-benchmark
```

Or add it to your development environment:

```bash
pip install -e ".[dev,benchmark]"
```

## Running Benchmarks

Run all benchmark tests:

```bash
pytest tests/benchmarks/ -v
```

Run specific benchmark test:

```bash
pytest tests/benchmarks/test_query_latency_baseline.py -v
pytest tests/benchmarks/test_startup_baseline.py -v
```

Generate benchmark comparison reports:

```bash
pytest tests/benchmarks/ --benchmark-compare
```

## Available Baselines

### Query Latency Baselines ✅

**File**: `test_query_latency_baseline.py`

Comprehensive query performance baselines using `pytest-benchmark`:
- `cbr_retrieve` latency (simple, medium, complex queries)
- `cbr_search_category` latency (with/without subcategory)
- `cbr_find_similar` latency
- Cold start vs warm cache comparison
- Embedding generation latency (isolated)
- Concurrent query performance
- Large result set latency
- Percentile distribution verification (p50, p95, p99)

**Output**: Benchmark statistics via pytest-benchmark framework

**Performance Targets**:
- **p95 latency**: < 200ms for typical queries
- **Concurrent queries**: < 300ms p95 under load
- **Large result sets**: < 400ms p95

### Startup Time Baselines ✅

**File**: `test_startup_baseline.py`

Comprehensive server startup performance measurements:
1. **Cold Start Total Time** - Complete initialization from scratch
2. **Embedding Model Loading** - Model download and initialization time
3. **Database Connection** - ChromaDB connection establishment
4. **Case Base Loading** - All 135 cases from modular structure
5. **Warm Start Time** - Performance with cached components
6. **Startup Phases Breakdown** - Detailed per-phase timing analysis
7. **Cold Start Repeatability** - Consistency across multiple runs (3 iterations)
8. **Filesystem Cache Effects** - Impact of OS-level caching

**Output**: `baseline_startup_time.json` (24KB) in project root

**Performance Target**: < 5 seconds total startup time

## Memory Profiling Limitations

### Why Memory Baselines Are Not Currently Collected

While comprehensive memory baseline tests exist in `test_memory_baseline.py`, they are **not practical for regular baseline collection** due to fundamental performance limitations of the `memory_profiler` library.

### Technical Background: How memory_profiler Works

The `memory_profiler` library measures memory usage by:
1. **Process Isolation**: Running the target function in a separate process
2. **Interval Sampling**: Polling memory usage at regular intervals (default: 0.01s)
3. **RSS Measurement**: Capturing Resident Set Size (physical memory) via psutil

This approach provides accurate memory measurements but creates significant overhead:
- Each function execution spawns a new process
- Continuous polling adds substantial latency
- Inter-process communication delays

### Performance Impact

**Original Test Configuration (Impractical)**:
- 100 queries per test
- 5 repeatability runs
- **Result**: 25+ minutes with no completion

**Reduced Test Configuration (Still Impractical)**:
- 10 queries per test
- 3 repeatability runs
- **Result**: 5+ minutes with no output

**Comparison to Working Baselines**:
- Query latency tests: Complete in seconds
- Startup time tests: Complete in ~30 seconds (8 tests)
- Memory tests: Minutes to hours with no practical results

### What Memory Tests Would Measure

The `test_memory_baseline.py` suite includes:
1. Server startup memory footprint (target: < 300MB)
2. Single query memory usage (target: < 50MB delta)
3. Concurrent query peak memory (target: < 500MB)
4. Memory growth over sequential queries (leak detection)
5. Embedding cache memory scaling
6. Case base size memory scaling
7. Memory measurement accuracy verification
8. Memory baseline repeatability

**Target**: < 500MB peak memory usage for production workloads

### Future Approaches

For practical memory baseline collection, consider:

**Option 1: Simpler psutil-Only Measurements**
- Direct RSS measurements without memory_profiler overhead
- Synchronous before/after measurements
- Trade accuracy for speed
- Example:
  ```python
  import psutil
  import os

  process = psutil.Process(os.getpid())
  baseline = process.memory_info().rss / 1024 / 1024  # MB
  # ... execute operation ...
  final = process.memory_info().rss / 1024 / 1024
  delta = final - baseline
  ```

**Option 2: Sampling-Based Monitoring**
- Background thread sampling at longer intervals (1-5 seconds)
- Track memory trends rather than precise deltas
- Suitable for integration tests

**Option 3: Production Monitoring Integration**
- Collect memory metrics during actual usage
- Aggregate statistics over time
- Real-world performance data

**Option 4: Profiling on Demand**
- Manual profiling sessions for specific investigations
- Not part of regular baseline collection
- Use `memory_profiler` decorators selectively

## Test Files

- **test_query_latency_baseline.py**: Query performance baselines (working)
- **test_startup_baseline.py**: Server startup timing baselines (working)
- **test_memory_baseline.py**: Memory usage baselines (impractical with current approach)

## Performance Summary

**Working Baselines** ✅:
- Query latency data collected via pytest-benchmark
- Startup timing data exported to JSON (24KB)
- 8 startup tests covering all initialization phases
- Comprehensive query performance coverage

**Future Work** 📋:
- Implement practical memory measurement approach
- Consider alternative profiling methods
- Integrate memory monitoring into production usage

## Note on TDD Approach

These tests define expected performance characteristics before optimization work.
Initial test runs may fail, indicating current performance needs improvement.
This is intentional (TDD Red phase). The goal is to:
1. Establish baseline measurements
2. Identify optimization opportunities
3. Track improvements over time
4. Prevent performance regressions
