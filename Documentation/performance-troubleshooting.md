# CBR MCP Server - Performance Troubleshooting Guide

> Last Updated: 2025-12-11
> Version: 2.0.0
> Related Spec: 2025-11-05-local-performance-optimization

## Overview

This guide provides detailed troubleshooting procedures for performance-related issues in the CBR MCP Server following the Phase 2 local performance optimization. Use this guide to diagnose and resolve latency, memory, caching, and throughput problems.

## Table of Contents

1. [High Query Latency](#high-query-latency)
2. [Memory Issues](#memory-issues)
3. [Low Cache Hit Rate](#low-cache-hit-rate)
4. [Slow Startup](#slow-startup)
5. [Concurrent Performance Issues](#concurrent-performance-issues)
6. [Cache System Problems](#cache-system-problems)
7. [Lazy Loading Issues](#lazy-loading-issues)
8. [Monitoring and Diagnostics](#monitoring-and-diagnostics)

## High Query Latency

### Symptom

Query response times exceed 200ms (p95) or are inconsistent.

### Diagnostic Steps

#### 1. Check Current Latency Metrics

```python
# Get query performance metrics
from cbr_mcp_server.performance.metrics import get_performance_metrics

metrics = get_performance_metrics()
print(f"P50 Latency: {metrics['query_latency_p50']}ms")
print(f"P95 Latency: {metrics['query_latency_p95']}ms")
print(f"P99 Latency: {metrics['query_latency_p99']}ms")
```

#### 2. Profile Individual Query

```python
import time
from cbr_mcp_server.performance import ProductionCBRRetriever

retriever = ProductionCBRRetriever(db_path="./db")

start = time.time()
results = retriever.retrieve("your query here", max_results=10)
elapsed = (time.time() - start) * 1000

print(f"Query latency: {elapsed:.2f}ms")
print(f"Cache hit: {retriever.result_cache.get('your query here') is not None}")
```

#### 3. Check Cache Performance

```python
cache_metrics = retriever.result_cache.get_metrics()
print(f"Cache hit rate: {cache_metrics.hit_rate:.2%}")
print(f"Cache size: {cache_metrics.entries}")
print(f"Cache hits: {cache_metrics.hits}")
print(f"Cache misses: {cache_metrics.misses}")
```

### Common Causes and Solutions

#### **Cause 1: Low Cache Hit Rate**

**Diagnosis:**
- Cache hit rate < 70%
- Many cache misses logged

**Solution:**
```yaml
# Increase cache size and TTL
performance:
  cache:
    max_size: 2000  # Increase from default 1000
    ttl_seconds: 7200  # Increase from default 3600
```

**Validation:**
```bash
# Monitor cache hit rate improvement
grep "cache_hit_rate" logs/server.log | tail -20
```

#### **Cause 2: ChromaDB Index Not Warmed**

**Diagnosis:**
- First few queries slow (>250ms)
- Subsequent queries faster
- No index warming configured

**Solution:**
```yaml
performance:
  index_warming:
    enabled: true
    categories:
      - "code"
      - "orchestration"
      - "best-practice"
    warmup_query_count: 5  # Increase warming
```

**Validation:**
```bash
# Check startup logs for index warming
grep "Index warming" logs/server.log
```

#### **Cause 3: Embedding Model Slow**

**Diagnosis:**
- High CPU during queries
- Embedding generation taking >50ms

**Solution:**
```python
# Check embedding performance
import time
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5')

start = time.time()
embedding = model.encode("test query")
elapsed = (time.time() - start) * 1000

print(f"Embedding time: {elapsed:.2f}ms")
# Should be <50ms on modern hardware
```

If slow, consider:
- GPU acceleration (if available)
- Reducing batch size
- Model warm-up on startup

#### **Cause 4: Database Connection Issues**

**Diagnosis:**
- Intermittent slow queries
- Connection timeouts in logs

**Solution:**
```python
# Check ChromaDB client status
try:
    client = retriever.client
    collection = retriever.collection
    count = collection.count()
    print(f"Collection healthy: {count} cases")
except Exception as e:
    print(f"Database issue: {e}")
    # Reinitialize client
```

#### **Cause 5: Memory Pressure**

**Diagnosis:**
- Latency increases over time
- Memory warnings in logs
- System swap usage high

**Solution:**
```yaml
performance:
  memory:
    max_memory_mb: 384  # Reduce from 512
  cache:
    max_size: 500  # Reduce cache size
```

### Quick Fixes

```bash
# Clear all caches and restart
curl -X POST http://localhost:8080/api/cache/clear

# Force garbage collection
python -c "import gc; gc.collect()"

# Restart server with debug logging
CBR_LOG_LEVEL=DEBUG cbr-mcp-server
```

## Memory Issues

### Symptom

Memory usage exceeds 500MB target or grows continuously.

### Diagnostic Steps

#### 1. Check Current Memory Usage

```python
from cbr_mcp_server.performance.memory_manager import MemoryManager

manager = MemoryManager(max_memory_mb=512)
usage = manager.check_memory_usage()

print(f"Current memory: {usage['current_mb']:.2f} MB")
print(f"Peak memory: {usage['peak_mb']:.2f} MB")
print(f"Memory pressure: {usage['pressure_detected']}")
```

#### 2. Profile Memory by Component

```python
import sys
import psutil
import gc

process = psutil.Process()

# Check component sizes
print(f"Total RSS: {process.memory_info().rss / 1024**2:.2f} MB")

# Force garbage collection
collected = gc.collect()
print(f"Collected {collected} objects")

# Check after GC
print(f"After GC: {process.memory_info().rss / 1024**2:.2f} MB")
```

#### 3. Analyze Memory Growth

```python
import tracemalloc

tracemalloc.start()

# Perform operations
for i in range(100):
    retriever.retrieve(f"query {i}", max_results=10)

# Get memory snapshot
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("Top 10 memory allocations:")
for stat in top_stats[:10]:
    print(stat)
```

### Common Causes and Solutions

#### **Cause 1: Cache Too Large**

**Diagnosis:**
- Cache occupying >100MB
- Many cached entries (>2000)

**Solution:**
```yaml
performance:
  cache:
    max_size: 500  # Reduce from default 1000
    ttl_seconds: 1800  # Reduce TTL for faster eviction
```

**Validation:**
```python
cache_size = len(retriever.result_cache._cache)
print(f"Cache entries: {cache_size}")
# Should be < max_size setting
```

#### **Cause 2: Lazy Loader Cache Overflow**

**Diagnosis:**
- Lazy loader cache growing large
- Memory increases with unique queries

**Solution:**
```yaml
performance:
  lazy_loading:
    max_cache_size: 100  # Reduce from default 200
    batch_size: 10  # Smaller batches
```

#### **Cause 3: Embedding Cache Not Evicting**

**Diagnosis:**
- Many embeddings cached
- No eviction happening

**Solution:**
```python
# Manual cache cleanup
if hasattr(retriever.lazy_loader, '_loaded'):
    retriever.lazy_loader._loaded.clear()

if hasattr(retriever.result_cache, '_cache'):
    old_size = len(retriever.result_cache._cache)
    retriever.result_cache._cache.clear()
    print(f"Cleared {old_size} cache entries")
```

#### **Cause 4: Memory Leak**

**Diagnosis:**
- Memory grows continuously
- Garbage collection doesn't help
- Memory doesn't decrease after idle period

**Solution:**
```python
# Check for circular references
import objgraph

# Find objects with most references
objgraph.show_most_common_types(limit=20)

# Check for specific leaks
objgraph.show_growth(limit=10)

# Find reference chains
objgraph.show_backrefs([retriever], filename='backrefs.png')
```

### Emergency Memory Recovery

```python
# Emergency cleanup procedure
def emergency_memory_cleanup(retriever):
    """Force aggressive memory cleanup."""
    import gc

    # Clear all caches
    if hasattr(retriever.result_cache, '_cache'):
        retriever.result_cache._cache.clear()

    if hasattr(retriever.lazy_loader, '_loaded'):
        retriever.lazy_loader._loaded.clear()

    # Force garbage collection (multiple passes)
    for _ in range(3):
        collected = gc.collect()
        print(f"Collected {collected} objects")

    # Check final memory
    import psutil
    process = psutil.Process()
    final_mb = process.memory_info().rss / 1024**2
    print(f"Memory after cleanup: {final_mb:.2f} MB")

    return final_mb

final_memory = emergency_memory_cleanup(retriever)
```

## Low Cache Hit Rate

### Symptom

Cache hit rate below 70% for typical workloads.

### Diagnostic Steps

#### 1. Analyze Cache Metrics

```python
metrics = retriever.result_cache.get_metrics()

print(f"Hit rate: {metrics.hit_rate:.2%}")
print(f"Total requests: {metrics.hits + metrics.misses}")
print(f"Cache size: {metrics.entries}/{retriever.result_cache._policy.max_size}")
print(f"Evictions: {metrics.evictions}")
```

#### 2. Check Query Patterns

```python
# Log queries to analyze patterns
import logging

logging.basicConfig(level=logging.DEBUG)

# Monitor queries
for i in range(100):
    query = get_next_query()  # Your query source
    hit = retriever.result_cache.get(query) is not None
    print(f"Query: '{query[:50]}...' Hit: {hit}")
```

#### 3. Analyze TTL Expirations

```python
# Check if entries expiring too soon
metrics = retriever.result_cache.get_metrics()

expiration_rate = metrics.ttl_expirations / (metrics.hits + metrics.misses)
print(f"Expiration rate: {expiration_rate:.2%}")

# High expiration rate (>20%) indicates TTL too short
```

### Common Causes and Solutions

#### **Cause 1: Query Variations**

**Diagnosis:**
- Similar queries with slight differences
- Same question with different wording
- Whitespace or case differences

**Example:**
```python
# These are cache misses for identical intent:
retriever.retrieve("user authentication")  # miss
retriever.retrieve("user authentication ")  # miss (trailing space)
retriever.retrieve("User Authentication")  # miss (case difference)
```

**Solution:**
```python
# Normalize queries before caching
def normalize_query(query: str) -> str:
    """Normalize query for consistent caching."""
    return query.strip().lower()

# Use normalized key for cache
normalized = normalize_query(query)
cached = retriever.result_cache.get(normalized)
```

#### **Cause 2: Cache Too Small**

**Diagnosis:**
- High eviction rate
- Cache full (entries == max_size)
- Recent queries getting evicted

**Solution:**
```yaml
performance:
  cache:
    max_size: 2000  # Double the size
    eviction_policy: "LRU"  # Ensure LRU is set
```

#### **Cause 3: TTL Too Short**

**Diagnosis:**
- High TTL expiration rate
- Queries expiring before reuse

**Solution:**
```yaml
performance:
  cache:
    ttl_seconds: 7200  # Increase to 2 hours
```

#### **Cause 4: Diverse Query Workload**

**Diagnosis:**
- Each query unique
- No query repetition
- Hit rate naturally low

**Solution:**
- Enable cache warming with common queries
- Increase cache size
- Consider if caching provides value for this workload

```yaml
performance:
  cache_warming:
    enabled: true
    queries:
      - "authentication example"
      - "database connection"
      - "error handling"
      # Add your most common queries
```

### Cache Hit Rate Optimization

```python
# Analyze query frequency to optimize cache
from collections import Counter

query_counter = Counter()

# Log queries for analysis period
for query in your_query_stream():
    query_counter[normalize_query(query)] += 1

# Find most common queries
top_queries = query_counter.most_common(50)

print("Top 50 queries for cache warming:")
for query, count in top_queries:
    print(f"{count:4d}x: {query}")
```

## Slow Startup

### Symptom

Server startup time exceeds 5 seconds.

### Diagnostic Steps

#### 1. Profile Startup Time

```python
import time

startup_times = {}

start = time.time()
# Phase 1: Client init
client = chromadb.PersistentClient(path="./db")
startup_times['client_init'] = time.time() - start

start = time.time()
# Phase 2: Model loading
model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5')
startup_times['model_load'] = time.time() - start

start = time.time()
# Phase 3: Retriever init
retriever = ProductionCBRRetriever(db_path="./db", embedding_model=model)
startup_times['retriever_init'] = time.time() - start

# Print breakdown
for phase, duration in startup_times.items():
    print(f"{phase}: {duration:.3f}s")
print(f"Total: {sum(startup_times.values()):.3f}s")
```

#### 2. Check Configuration

```bash
# Review startup configuration
cat config/production.yaml | grep -A 10 "cache_warming\|index_warming"
```

### Common Causes and Solutions

#### **Cause 1: Cache Warming Enabled**

**Diagnosis:**
- Cache warming queries executing at startup
- Startup logs show cache warming activity

**Solution:**
```yaml
performance:
  cache_warming:
    enabled: false  # Disable for fastest startup
```

**Alternative:** Reduce warming queries
```yaml
performance:
  cache_warming:
    enabled: true
    queries:
      - "quick query 1"  # Only 2-3 essential queries
      - "quick query 2"
```

#### **Cause 2: Aggressive Index Warming**

**Diagnosis:**
- Index warming taking >1 second
- Many categories being warmed

**Solution:**
```yaml
performance:
  index_warming:
    enabled: true
    categories:
      - "code"  # Reduce to 1-2 categories
    warmup_query_count: 2  # Reduce query count
```

**Or disable completely:**
```yaml
performance:
  index_warming:
    enabled: false
```

#### **Cause 3: Eager Case Loading**

**Diagnosis:**
- All cases loading at startup
- Lazy loading disabled

**Solution:**
```yaml
performance:
  lazy_loading:
    enabled: true
    preload_hot_cases: false  # Don't preload anything
```

#### **Cause 4: Slow Embedding Model Load**

**Diagnosis:**
- Model loading taking >3 seconds
- Large model download happening

**Solution:**
```bash
# Pre-download model to cache
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('nomic-ai/nomic-embed-text-v1.5')"

# Verify model in cache
ls -lh ~/.cache/torch/sentence_transformers/
```

#### **Cause 5: Database Integrity Checks**

**Diagnosis:**
- ChromaDB performing integrity checks
- Large database taking time to open

**Solution:**
```python
# Check database size
import os
db_size = sum(
    os.path.getsize(os.path.join(dirpath, filename))
    for dirpath, dirnames, filenames in os.walk("./db")
    for filename in filenames
) / 1024**2

print(f"Database size: {db_size:.2f} MB")

# If very large (>500MB), consider optimization
```

### Startup Time Optimization

```python
# Minimal startup configuration
minimal_config = {
    "memory": {
        "max_memory_mb": 512
    },
    "cache": {
        "max_size": 1000,
        "ttl_seconds": 3600
    },
    "lazy_loading": {
        "enabled": True,
        "preload_hot_cases": False,
        "background_loading_enabled": True
    },
    "cache_warming": {
        "enabled": False
    },
    "index_warming": {
        "enabled": False
    }
}

# Expected startup: 2.5-3.5 seconds
```

## Concurrent Performance Issues

### Symptom

Performance degrades with concurrent queries or requests fail.

### Diagnostic Steps

#### 1. Load Test

```python
import concurrent.futures
import time

def query_worker(query_id):
    """Worker function for concurrent queries."""
    start = time.time()
    try:
        results = retriever.retrieve(f"query {query_id}", max_results=10)
        elapsed = time.time() - start
        return {
            'id': query_id,
            'success': True,
            'latency': elapsed * 1000,
            'results': len(results)
        }
    except Exception as e:
        return {
            'id': query_id,
            'success': False,
            'error': str(e)
        }

# Test with 10 concurrent queries
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(query_worker, i) for i in range(100)]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

# Analyze results
successes = [r for r in results if r['success']]
failures = [r for r in results if not r['success']]

print(f"Success rate: {len(successes)}/{len(results)} ({len(successes)/len(results):.1%})")
print(f"Avg latency: {sum(r['latency'] for r in successes)/len(successes):.1f}ms")
print(f"Failures: {len(failures)}")
```

#### 2. Check Resource Contention

```python
import psutil
import threading

def monitor_resources(duration=60):
    """Monitor CPU and memory during load."""
    process = psutil.Process()
    stats = []

    for _ in range(duration):
        stats.append({
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / 1024**2,
            'threads': len(process.threads())
        })
        time.sleep(1)

    return stats

# Start monitoring
monitor_thread = threading.Thread(target=lambda: monitor_resources(60))
monitor_thread.start()

# Run concurrent load
# ... your load test ...

monitor_thread.join()
```

### Common Causes and Solutions

#### **Cause 1: Cache Lock Contention**

**Diagnosis:**
- High latency with concurrent requests
- Thread count increases
- Cache access serialized

**Solution:**
```python
# Use thread-local caches for read-heavy workloads
import threading

thread_local = threading.local()

def get_thread_cache():
    if not hasattr(thread_local, 'cache'):
        thread_local.cache = {}
    return thread_local.cache
```

#### **Cause 2: Database Connection Limits**

**Diagnosis:**
- Connection errors under load
- ChromaDB timeouts

**Solution:**
```python
# Ensure proper connection pooling
# ProductionCBRRetriever uses single client with collection reuse
# Verify collection initialized properly
retriever._ensure_collection_initialized()
```

#### **Cause 3: Memory Pressure Under Load**

**Diagnosis:**
- Memory usage spikes with concurrent load
- System starts swapping

**Solution:**
```yaml
performance:
  memory:
    max_memory_mb: 768  # Increase for concurrent load
  cache:
    max_size: 1500  # Accommodate concurrent queries
```

#### **Cause 4: CPU Bottleneck**

**Diagnosis:**
- High CPU usage (>80%)
- Embedding generation slow

**Solution:**
- Reduce concurrent workers
- Use query batching
- Consider GPU acceleration

## Monitoring and Diagnostics

### Enable Debug Logging

```bash
# Start server with debug logging
export CBR_LOG_LEVEL=DEBUG
export CBR_LOG_FILE=logs/debug.log
cbr-mcp-server
```

### Health Dashboard

Access real-time metrics:

```bash
# Open health dashboard
open http://localhost:8080/health

# Or query metrics programmatically
curl http://localhost:8080/api/metrics
```

### Performance Profiling

```python
# Profile query execution
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Execute queries
for i in range(100):
    retriever.retrieve(f"query {i}", max_results=10)

profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Memory Profiling

```python
# Detailed memory profiling
from memory_profiler import profile

@profile
def profile_memory():
    retriever = ProductionCBRRetriever(db_path="./db")
    for i in range(100):
        results = retriever.retrieve(f"query {i}")
    return retriever

profile_memory()
```

## See Also

- [Performance Configuration Guide](./performance-configuration.md) - Configuration options
- [Performance Tuning Guide](./performance-tuning-guide.md) - Optimization strategies
- [Benchmark Results](./benchmark-results.md) - Expected performance metrics
- [Monitoring Setup Guide](./monitoring-setup-guide.md) - Monitoring configuration
