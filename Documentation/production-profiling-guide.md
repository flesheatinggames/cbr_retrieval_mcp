# Production Profiling Guide

This guide explains how to use the production profiling tools to validate performance characteristics under realistic workload conditions.

## Overview

The production profiling script (`tests/load/production_profiling.py`) simulates a realistic production workload and collects comprehensive performance data using:

- **cProfile**: CPU profiling to identify performance bottlenecks
- **tracemalloc**: Memory profiling to track allocation patterns
- **psutil**: System resource monitoring
- **LoadTestRunner**: Concurrent request simulation with real-time metrics

## Performance Targets

The profiler validates against these production targets:

| Metric | Target | Description |
|--------|--------|-------------|
| p95 Latency | < 200ms | 95th percentile query response time |
| p50 Latency | < 100ms | Median query response time |
| Peak Memory | < 500MB | Maximum memory usage during sustained load |
| Cache Hit Rate | > 70% | After warmup period with typical query patterns |
| Throughput | > 10 QPS | With 10+ concurrent clients |
| Error Rate | < 1% | Failed queries under normal conditions |

## Usage

### Basic Usage

Run with default settings (5 minutes):

```bash
python tests/load/production_profiling.py
```

### Custom Duration

Run for a specific duration:

```bash
python tests/load/production_profiling.py --duration 600  # 10 minutes
```

### Custom Output Directory

Specify where to save results:

```bash
python tests/load/production_profiling.py --output-dir ./my_results
```

### Full Options

```bash
python tests/load/production_profiling.py \
  --duration 300 \
  --output-dir ./profiling_results
```

## What Gets Profiled

### Workload Simulation

The profiler generates a realistic production workload:

1. **Mixed Retrieve Queries** (50 unique, 70% repeat ratio)
   - Simulates realistic caching behavior
   - Includes simple, medium, and complex queries
   - Tests semantic similarity search

2. **Category Searches** (100 queries across 4 categories)
   - Tests hierarchical filtering
   - Validates ChromaDB where clause performance
   - Simulates browsing workflows

3. **Similar Case Lookups** (90 lookups)
   - Tests find_similar functionality
   - Validates vector similarity operations

### Concurrent Load

- **10 concurrent clients** executing queries simultaneously
- Tests async operation handling
- Validates no blocking between requests
- Simulates multiple AI agents querying in parallel

### Duration

- Default: **5 minutes** of sustained load
- Captures warmup behavior
- Detects memory leaks
- Measures latency stability over time

## Output Files

### 1. JSON Results File

`profiling_results_<timestamp>.json` contains:

```json
{
  "metadata": {
    "timestamp": "2025-12-15T10:30:00",
    "duration_seconds": 300,
    "elapsed_seconds": 302.5,
    "baseline_memory_mb": 145.2,
    "final_memory_mb": 187.3,
    "delta_memory_mb": 42.1
  },
  "load_metrics": {
    "total_queries": 3142,
    "successful_queries": 3140,
    "failed_queries": 2,
    "error_rate": 0.0006,
    "queries_per_second": 10.4,
    "latency": {
      "p50_ms": 87.3,
      "p95_ms": 156.2,
      "p99_ms": 203.7,
      "mean_ms": 92.1,
      "max_ms": 245.8
    },
    "memory": {
      "peak_mb": 187.5,
      "mean_mb": 175.2,
      "final_mb": 187.3,
      "samples_count": 300
    },
    "cache": {
      "hit_rate": 0.7234,
      "hits": 2271,
      "misses": 869
    }
  },
  "top_functions": [
    {
      "function": "retrieve.py:123(retrieve)",
      "ncalls": 3142,
      "tottime": 45.2,
      "cumtime": 278.5,
      "percall_tot": 0.014,
      "percall_cum": 0.089
    }
  ],
  "memory_top_consumers": [
    {
      "size_mb": 125.3,
      "count": 1,
      "location": "embedding_model.py:45"
    }
  ],
  "validation": {
    "p95_latency": true,
    "p50_latency": true,
    "peak_memory": true,
    "cache_hit_rate": true,
    "throughput": true,
    "error_rate": true,
    "overall": true
  }
}
```

### 2. cProfile Binary File

`production_profile_<timestamp>.prof` can be analyzed with:

```bash
# View in terminal
python -m pstats production_profile_<timestamp>.prof

# Visualize with snakeviz (if installed)
snakeviz production_profile_<timestamp>.prof

# Convert to call graph (requires gprof2dot and graphviz)
gprof2dot -f pstats production_profile_<timestamp>.prof | dot -Tpng -o profile.png
```

## Interpreting Results

### Console Output

The script prints real-time progress and a detailed summary:

```
======================================================================
CBR MCP Server - Production Profiling
======================================================================

Initializing CBR retriever...
Warming up retriever...
Initialization complete.

Generating production workload...
  - Generated 100 retrieve queries
  - Generated 100 category searches
  - Generated 90 similar lookups

Starting profiled workload (duration: 300s)...
======================================================================
Baseline memory: 145.2 MB

Starting CPU profiling...
Running concurrent load test (10 clients, 300s)...

======================================================================
Workload completed in 302.5s

Validating Performance Targets:
======================================================================
  p95 Latency: 156.23ms < 200ms ... ✓ PASS
  p50 Latency: 87.31ms < 100ms ... ✓ PASS
  Peak Memory: 187.5MB < 500MB ... ✓ PASS
  Cache Hit Rate: 72.3% > 70% ... ✓ PASS
  Throughput: 10.4 QPS > 10 QPS ... ✓ PASS
  Error Rate: 0.1% < 1% ... ✓ PASS
======================================================================
✓ ALL PERFORMANCE TARGETS MET
```

### Key Metrics to Watch

1. **Latency Distribution**
   - p50 should be well under 100ms for good user experience
   - p95 < 200ms ensures consistent performance
   - Large gap between p95 and max suggests occasional outliers

2. **Memory Behavior**
   - Peak < 500MB is hard requirement
   - Mean close to peak indicates stable usage
   - Large delta (final - baseline) may indicate leak

3. **Cache Performance**
   - Hit rate > 70% with typical workload indicates effective caching
   - Low hit rate suggests cache size too small or poor eviction
   - Check hit/miss counts for sufficient warmup

4. **Throughput**
   - > 10 QPS with 10 clients shows good concurrency
   - Low QPS may indicate blocking or contention
   - Compare with single-client throughput for scaling factor

### Red Flags

⚠️ **Memory Issues**
- Peak > 450MB: Too close to limit
- Delta > 100MB: Possible memory leak
- Continuous growth in samples: Definite leak

⚠️ **Performance Issues**
- p95 > 200ms: Misses latency target
- Cache hit rate < 60%: Cache not effective
- High error rate: Stability problems

⚠️ **Scalability Issues**
- Throughput < 8 QPS: Not scaling with concurrency
- p95 increases significantly over time: Degradation
- Memory spikes during concurrent load: Poor resource management

## Analyzing CPU Hotspots

Use the `top_functions` section to identify bottlenecks:

1. **High `cumtime` (cumulative time)**
   - Functions where most time is spent (including subcalls)
   - Prime candidates for optimization
   - Focus on functions with high cumtime AND high call count

2. **High `tottime` (self time)**
   - Functions spending time in their own code
   - May indicate inefficient algorithms
   - Look for tight loops or repeated operations

3. **High `percall`**
   - Individual calls are slow
   - May benefit from caching or memoization
   - Check for I/O or blocking operations

### Example Analysis

```json
{
  "function": "chromadb.py:234(query)",
  "ncalls": 869,  // Only on cache misses
  "cumtime": 156.2,  // 156 seconds total
  "percall_cum": 0.180  // 180ms per call
}
```

**Interpretation**: ChromaDB queries take 180ms each, consuming most of the latency budget. Since this only happens on cache misses (~30%), the cache is doing its job. Focus on optimizing query generation or ChromaDB indexing if latency needs improvement.

## Analyzing Memory Consumers

Check `memory_top_consumers` for allocation hotspots:

```json
{
  "size_mb": 125.3,
  "count": 1,
  "location": "embedding_model.py:45 - model = SentenceTransformer(...)"
}
```

**Interpretation**: Embedding model is largest memory consumer (expected). Single allocation suggests no leak. If count > 1 for model loading, that's a problem.

## Continuous Performance Tracking

### Baseline Establishment

Run profiling on known-good commit:

```bash
git checkout v1.0.0
python tests/load/production_profiling.py --output-dir ./baseline
```

### Regression Detection

Compare new results against baseline:

```bash
# After making changes
python tests/load/production_profiling.py --output-dir ./current

# Compare key metrics
python -c "
import json
baseline = json.load(open('baseline/profiling_results_*.json'))
current = json.load(open('current/profiling_results_*.json'))

print('Latency change:',
      current['load_metrics']['latency']['p95_ms'] -
      baseline['load_metrics']['latency']['p95_ms'], 'ms')
print('Memory change:',
      current['load_metrics']['memory']['peak_mb'] -
      baseline['load_metrics']['memory']['peak_mb'], 'MB')
"
```

### CI/CD Integration

Add to CI pipeline:

```yaml
# .github/workflows/performance.yml
- name: Run Production Profiling
  run: |
    python tests/load/production_profiling.py --duration 60

- name: Upload Profiling Results
  uses: actions/upload-artifact@v2
  with:
    name: profiling-results
    path: profiling_results/
```

## Troubleshooting

### Out of Memory

If profiling causes OOM:
- Reduce duration: `--duration 60`
- Check for memory leaks in recent changes
- Review memory_top_consumers for unexpected allocations

### Slow Profiling

If profiling is very slow:
- cProfile adds ~10-20% overhead (expected)
- Check if ChromaDB is actually running (not mock)
- Verify embedding model is loaded (not loading per query)

### Failed Validations

If targets not met:
1. Check which specific metric failed
2. Review corresponding section in this guide
3. Analyze top_functions or memory_consumers
4. Run with longer duration to rule out warmup issues

## Related Tools

- **Memory Baseline**: `pytest tests/benchmarks/test_memory_baseline.py`
- **Startup Baseline**: `pytest tests/benchmarks/test_startup_baseline.py`
- **Load Tests**: `pytest tests/load/test_performance_load.py -m load`
- **Benchmarks**: `pytest tests/benchmarks/`

## Best Practices

1. **Always profile with production configuration**
   - Use real ChromaDB (not mocks)
   - Use real embedding model
   - Use production database path

2. **Profile after significant changes**
   - Before/after optimization
   - After adding features
   - After dependency updates

3. **Keep historical results**
   - Track performance over time
   - Detect gradual degradation
   - Validate optimization impact

4. **Share results with team**
   - Document performance changes in PRs
   - Include profiling data in performance reviews
   - Update targets as system evolves

## Exit Codes

- **0**: All performance targets met
- **1**: One or more targets not met
- **1**: Error during profiling (exception)

Use exit code for CI/CD gating:

```bash
if python tests/load/production_profiling.py; then
  echo "Performance validated ✓"
else
  echo "Performance regression detected ✗"
  exit 1
fi
```
