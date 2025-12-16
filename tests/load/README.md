# Load Testing & Production Profiling

This directory contains load testing and production profiling tools for the CBR MCP Server.

## Files

- **`test_performance_load.py`**: Comprehensive load test suite with 20+ test scenarios
- **`production_profiling.py`**: Production-like workload profiling script
- **`test_memory_profile.py`**: Memory profiling utilities
- **`profile_memory_discrepancy.py`**: Memory discrepancy analysis

## Quick Start

### Run Production Profiling

Profile with production-like workload (5 minutes):

```bash
python tests/load/production_profiling.py
```

Profile with custom duration:

```bash
python tests/load/production_profiling.py --duration 300
```

### Run Load Tests

Run all load tests:

```bash
pytest tests/load/test_performance_load.py -m load -v
```

Run specific load test category:

```bash
# Sustained load tests
pytest tests/load/test_performance_load.py -k sustained -v

# Concurrent query tests
pytest tests/load/test_performance_load.py -k concurrent -v

# Memory pressure tests
pytest tests/load/test_performance_load.py -k memory_pressure -v
```

## Performance Targets

| Metric | Target |
|--------|--------|
| p95 Latency | < 200ms |
| p50 Latency | < 100ms |
| Peak Memory | < 500MB |
| Cache Hit Rate | > 70% |
| Throughput | > 10 QPS (10+ clients) |
| Error Rate | < 1% |

## Documentation

See [Production Profiling Guide](../../Documentation/production-profiling-guide.md) for complete documentation.

## Output

Production profiling generates:
- `profiling_results_<timestamp>.json` - Performance metrics and analysis
- `production_profile_<timestamp>.prof` - CPU profiling data for detailed analysis

Analyze CPU profile with:

```bash
# View in terminal
python -m pstats production_profile_*.prof

# Visualize with snakeviz (if installed)
snakeviz production_profile_*.prof
```
