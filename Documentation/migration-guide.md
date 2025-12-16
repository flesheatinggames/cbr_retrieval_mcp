# CBR MCP Server Performance Optimization Migration Guide

> **Version:** 2.0.0
> **Last Updated:** 2025-12-15
> **Target Release:** Local Performance Optimization Phase 2
> **Related Spec:** 2025-11-05-local-performance-optimization

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Breaking Changes](#breaking-changes)
4. [Configuration Changes](#configuration-changes)
5. [Step-by-Step Migration Process](#step-by-step-migration-process)
6. [Common Deployment Scenarios](#common-deployment-scenarios)
7. [Performance Tuning Guide](#performance-tuning-guide)
8. [Rollback Procedures](#rollback-procedures)
9. [Troubleshooting](#troubleshooting)
10. [Validation Steps](#validation-steps)

---

## Overview

### What This Migration Accomplishes

This migration upgrades your CBR MCP Server installation to the performance-optimized version (v2.0) with comprehensive local execution enhancements. The optimized version delivers:

**Performance Improvements:**
- **Query Latency**: Sub-200ms response times (p95) for typical CBR queries
- **Memory Efficiency**: Optimized memory management with ~1275MB baseline usage (real embedding model)
- **Startup Time**: Server initialization in under 5 seconds
- **Cache Hit Rate**: 70%+ for frequently accessed cases
- **Throughput**: Support for 10+ concurrent queries without degradation

**New Capabilities:**
- Intelligent memory management with automatic pressure detection
- High-performance LRU result caching with configurable TTL
- Lazy loading for on-demand embedding and case data loading
- Query optimization with connection pooling and batch coordination
- Optional cache and index pre-warming for reduced first-query latency

### When to Use This Guide

Use this guide when:
- Upgrading an existing CBR MCP Server deployment to v2.0
- Migrating from the pre-optimization version (v1.x)
- Configuring performance settings for your workload
- Troubleshooting performance issues after upgrade

### Migration Safety

**This migration is designed for zero-downtime upgrades:**
- ✅ **No database schema changes** - All existing ChromaDB data preserved
- ✅ **Backward compatible** - All MCP tool interfaces unchanged
- ✅ **Additive configuration** - New settings with sensible defaults
- ✅ **Idempotent** - Can be run multiple times safely
- ✅ **Rollback ready** - Simple rollback process documented
- ✅ **No re-embedding** - Preserves all existing vector embeddings

---

## Technical Changes Summary

### Memory Threshold Updates

The performance optimization phase updated memory thresholds to account for the real `nomic-ai/nomic-embed-text-v1.5` embedding model rather than mocked components:

**Before (v1.x - Mocked Components):**
- MAX_STARTUP_MEMORY_MB: 1050MB (estimated for mocked model)
- MAX_PEAK_MEMORY_MB: 1200MB (estimated for mocked operations)
- Baseline assumption: ~500MB for mocked embedding model

**After (v2.0 - Real Embedding Model):**
- MAX_STARTUP_MEMORY_MB: 1350MB (accounts for real model ~1135MB + pytest overhead ~200MB)
- MAX_PEAK_MEMORY_MB: 1500MB (accounts for real model + query operations)
- Measured baseline: ~1275MB (based on baseline_memory_usage.json metrics)

**Rationale:** The real `nomic-ai/nomic-embed-text-v1.5` model requires significantly more memory (~1135MB) compared to mocked components (~500MB). The updated thresholds reflect actual measured memory usage to ensure realistic performance validation and avoid false test failures.

### Thread-Safe Encoding Fix

**LazyEmbeddingModel Thread Safety Enhancement:**

The `LazyEmbeddingModel` class in `src/cbr_mcp_server/performance/production_cbr_retriever.py` was enhanced with thread-safe encoding to prevent concurrent tensor shape mismatch errors:

**Changes:**
- Added `_encode_lock` threading lock to the `__init__` method
- Protected `encode()` method with lock to serialize SentenceTransformer encoding calls
- Prevents "The size of tensor a (X) must match the size of tensor b (Y)" errors under concurrent access

**Impact:**
- Fixes race condition when multiple threads encode queries of different lengths simultaneously
- SentenceTransformer.encode() is not thread-safe due to internal batching
- Lock ensures only one encoding operation occurs at a time, preventing tensor shape conflicts

### Production Profiling Target Update

**Updated Memory Target in tests/load/production_profiling.py:**

**Before:** Peak memory target < 500MB (based on mocked components)

**After:** Peak memory target < 1500MB (accounts for real nomic-ai embedding model ~1135MB + query overhead)

**Comment Added:**
```python
# Memory usage: Peak < 1500MB (accounts for real nomic-ai embedding model ~1135MB + query overhead)
```

### Test Infrastructure Compatibility Fix

**Cache Attribute Name Compatibility (tests/load/test_performance_load.py):**

Enhanced cache attribute checking to support both naming conventions:
- Checks for both `cache` and `result_cache` attributes
- Ensures compatibility across different CBR retriever implementations
- Prevents AttributeError when accessing cache metrics

---

## Prerequisites

### System Requirements

**Python Environment:**
```bash
Python >= 3.10
chromadb (existing version)
sentence-transformers (existing dependency)
psutil (existing dependency)
cachetools >= 5.3.0 (NEW)
memory_profiler (development only - NEW)
```

**Database Requirements:**
- ChromaDB collection: Existing collection unchanged
- Database path: Your current `./db` path (or custom)
- No database migration required
- No re-embedding required

**Disk Space:**
- Minimal additional space (<10MB for new Python dependencies)
- Existing database size unchanged
- Optional: Additional space for backups if desired

### Compatibility Matrix

| Component | Pre-Optimization (v1.x) | Performance-Optimized (v2.0) | Compatible? |
|-----------|-------------------------|------------------------------|-------------|
| MCP Protocol | stdio | stdio | ✅ Yes |
| MCP Tools | cbr_retrieve, cbr_search_category, cbr_find_similar | Same | ✅ Yes |
| ChromaDB | Any version | Any version | ✅ Yes |
| Case Base Format | Modular structure | Same | ✅ Yes |
| Metadata Schema | category/subcategory/tags | Same | ✅ Yes |
| Python Version | >= 3.10 | >= 3.10 | ✅ Yes |

### Pre-Migration Checklist

Before upgrading, ensure:

- [ ] **Backup created** - Copy of entire project directory (optional but recommended)
- [ ] **Database backup** - Backup of `./db` directory (optional)
- [ ] **Dependency check** - Current dependencies documented
- [ ] **Python environment active** - Virtual environment with existing dependencies
- [ ] **Server stopped** - No active CBR MCP Server instances running
- [ ] **Performance baseline** - Current query latency and memory usage recorded (optional)

---

## Breaking Changes

### API Compatibility: Zero Breaking Changes

**Good news!** This migration introduces **zero API breaking changes**:

- ✅ All existing MCP tool interfaces remain identical
- ✅ All existing configuration continues to work
- ✅ All existing ChromaDB data fully compatible
- ✅ All existing code and integrations continue to function
- ✅ No client-side changes required

### Behavioral Changes

While not breaking API compatibility, these behaviors have changed:

1. **Startup Behavior**
   - **Before**: Loaded all embeddings immediately at startup
   - **After**: Lazy loads embeddings on-demand (configurable)
   - **Impact**: Faster startup time, lower initial memory usage
   - **Mitigation**: Set `lazy_loading.enabled: false` to restore old behavior

2. **Memory Usage Pattern**
   - **Before**: Static memory allocation (~500MB estimated with mocked components)
   - **After**: Dynamic memory management with real embedding model (~1275MB baseline)
   - **Impact**: Higher baseline memory usage due to real `nomic-ai/nomic-embed-text-v1.5` model (~1135MB vs ~500MB mocked), but more adaptive to workload
   - **Mitigation**: Allocate 1.3-1.5GB RAM for the CBR server process; configure `memory.max_memory_mb` to match your resources
   - **Important**: Users with strict memory constraints (<2GB total system RAM) may need to adjust their environment or allocate additional memory

3. **First Query Latency**
   - **Before**: Consistent latency (all embeddings pre-loaded)
   - **After**: First query may be slightly slower if using lazy loading
   - **Impact**: Trade startup time for potential first-query latency
   - **Mitigation**: Enable `index_warming` or disable `lazy_loading`

---

## Configuration Changes

### New Configuration Sections

The v2.0 release adds five new configuration sections (all optional with defaults):

```yaml
performance:
  memory: {...}           # Memory management settings
  cache: {...}            # Result caching configuration
  lazy_loading: {...}     # Lazy loading options
  cache_warming: {...}    # Cache pre-warming settings
  index_warming: {...}    # Index pre-warming settings
```

### Memory Threshold Configuration Updates

The memory thresholds in test files have been updated to reflect real embedding model requirements. If you have custom test configurations, update them as follows:

**Files Affected:**
- `tests/benchmarks/test_memory_baseline.py`
- `tests/benchmarks/test_memory_benchmarks.py`
- `tests/load/production_profiling.py`

**Before (v1.x):**
```python
MAX_STARTUP_MEMORY_MB = 1050  # Based on mocked components
MAX_PEAK_MEMORY_MB = 1200     # Based on mocked operations
# Expected baseline: ~500MB
```

**After (v2.0):**
```python
MAX_STARTUP_MEMORY_MB = 1350  # Accounts for real embedding model (~1135MB) + pytest overhead (~200MB)
MAX_PEAK_MEMORY_MB = 1500     # Accounts for model + query operations
# Measured baseline: ~1275MB (from baseline_memory_usage.json)
```

**Migration Path for Custom Configurations:**

If you have custom memory thresholds in your test suite or monitoring:

1. **Update test thresholds** to account for real model size (~1135MB)
2. **Add overhead buffer** of ~200MB for pytest and system overhead
3. **Validate with baseline** by running: `pytest tests/benchmarks/test_memory_baseline.py --json-report --json-report-file=your_baseline.json`
4. **Review measured values** in the generated JSON report and adjust thresholds if needed

### Default Configuration

If you don't specify any performance configuration, these defaults are used:

```yaml
performance:
  memory:
    max_memory_mb: 512
    warning_threshold: 0.8
    auto_detect_pressure: true
    check_interval: 30.0

  cache:
    max_size: 1000
    ttl_seconds: 3600
    eviction_policy: "LRU"
    enable_metrics: true
    cleanup_interval: 300

  lazy_loading:
    enabled: true
    preload_hot_cases: true
    hot_case_count: 50
    background_loading_enabled: true
    access_window_hours: 24
    min_access_frequency: 0.5
    batch_size: 20
    max_concurrent_loads: 5
    max_cache_size: 200

  cache_warming:
    enabled: false
    queries: []

  index_warming:
    enabled: false
    categories: ["code", "orchestration", "best-practice"]
    warmup_query_count: 3
```

### Environment Variable Overrides

All performance settings can be overridden via environment variables:

```bash
# Memory settings
export CBR_MAX_MEMORY_MB=512
export CBR_MEMORY_WARNING_THRESHOLD=0.8

# Cache settings
export CBR_CACHE_MAX_SIZE=1000
export CBR_CACHE_TTL_SECONDS=3600
export CBR_CACHE_ENABLED=true

# Lazy loading settings
export CBR_LAZY_LOADING_ENABLED=true
export CBR_HOT_CASE_COUNT=50

# Cache warming
export CBR_CACHE_WARMING_ENABLED=false

# Index warming
export CBR_INDEX_WARMING_ENABLED=false
```

### Configuration File Location

**Option 1: No Configuration File (Use Defaults)**
- The server uses built-in defaults
- Override via environment variables if needed

**Option 2: pyproject.toml (Recommended)**
- Add `[tool.cbr-mcp-server.performance]` section
- See [Common Deployment Scenarios](#common-deployment-scenarios) for examples

**Option 3: Environment Variables Only**
- Set environment variables in your shell or `.env` file
- Useful for containerized deployments

---

## Step-by-Step Migration Process

### Step 1: Pre-Migration Validation

**1.1 Record Current Performance Baseline (Optional)**

Before upgrading, optionally measure your current performance:

```bash
# Activate your virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run benchmark if you have it
python -m pytest tests/benchmarks/test_query_latency_baseline.py

# Or manually test a few queries and note the response times
```

**1.2 Create Backup (Optional)**

If you want extra safety, create a backup:

```bash
# Backup entire project directory
cp -r /path/to/cbr_retrieval_mcp /path/to/cbr_retrieval_mcp.backup

# Or just backup the database
cp -r ./db ./db.backup
```

**1.3 Stop Running Server**

Stop any running CBR MCP Server instances:

```bash
# Find running instances
ps aux | grep cbr-mcp-server

# Kill process if found
kill <PID>
```

### Step 2: Upgrade Dependencies

**2.1 Update Package Dependencies**

The only new dependency is `cachetools`:

```bash
# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install cachetools>=5.3.0

# Verify installation
pip list | grep cachetools
```

**2.2 Install Development Dependencies (Optional)**

If you want to run performance benchmarks:

```bash
pip install memory_profiler pytest-benchmark
```

### Step 3: Update Code

**3.1 Pull Latest Code**

```bash
# If using Git
git pull origin main  # or your branch name

# If using downloaded archive
# Extract new version over existing directory
```

**3.2 Verify File Structure**

Ensure these new files exist:

```bash
# Check for new performance modules
ls src/cbr_mcp_server/performance/

# Should see:
# - __init__.py
# - cache_system.py
# - memory_manager.py
# - query_optimizer.py
# - production_cbr_retriever.py (updated)
```

### Step 4: Configure Performance Settings (Optional)

**4.1 Choose Configuration Approach**

You have three options:

**Option A: Use Defaults (Recommended for Most Users)**
- No configuration needed
- Balanced settings for typical workloads
- Skip to Step 5

**Option B: Add Configuration to pyproject.toml**

Edit `pyproject.toml` and add:

```toml
[tool.cbr-mcp-server.performance]
# See "Common Deployment Scenarios" section for examples
```

**Option C: Use Environment Variables**

Create a `.env` file or set in your shell:

```bash
export CBR_MAX_MEMORY_MB=512
export CBR_CACHE_MAX_SIZE=1000
# etc.
```

**4.2 Validate Configuration (If Added)**

If you added custom configuration, validate it:

```bash
# Test server startup with new config
python -c "from cbr_mcp_server.performance import MemoryManager; print('Config OK')"
```

### Step 5: Restart Server

**5.1 Start Updated Server**

```bash
# Start in stdio mode (typical for MCP)
cbr-mcp-server

# Or start with custom database path
cbr-mcp-server --db-path /path/to/db
```

**5.2 Verify Startup Success**

The server should start in under 5 seconds. You should see log messages like:

```
[INFO] CBR MCP Server starting...
[INFO] Initializing MemoryManager (max: 512MB)
[INFO] Initializing ResultCache (size: 1000, TTL: 3600s)
[INFO] Lazy loading enabled (hot cases: 50)
[INFO] Server ready to accept connections
```

### Step 6: Validation

**6.1 Test Basic Functionality**

Run a test query to ensure the server works:

```bash
# If you have the test suite
pytest tests/integration/test_cbr_mcp_server_integration.py

# Or test via your MCP client (e.g., Claude Code)
# Send a cbr_retrieve query and verify it works
```

**6.2 Check Performance Metrics**

Verify performance improvements:

```bash
# Run performance benchmarks (if installed)
pytest tests/benchmarks/test_query_latency_baseline.py
```

**6.3 Monitor Memory Usage**

Check that memory usage is under limits:

```bash
# Linux/Mac: Monitor with top or htop
top -p $(pgrep -f cbr-mcp-server)

# Or check server logs for memory warnings
tail -f logs/cbr_server.log | grep MEMORY
```

### Step 7: Post-Migration Optimization (Optional)

**7.1 Tune Configuration for Your Workload**

Based on your usage patterns, adjust settings:

- If memory usage is consistently below 300MB: Increase cache sizes
- If seeing slow first queries: Enable index warming
- If startup time is critical: Disable cache/index warming

See [Performance Tuning Guide](#performance-tuning-guide) section.

---

## Common Deployment Scenarios

### Scenario 1: Local Development (Default)

**Use Case:** Developer running CBR MCP Server on local machine alongside other development tools.

**Configuration:** Use defaults (no configuration needed)

**Expected Performance:**
- Startup time: 3-5 seconds
- Query latency: 50-150ms (p95)
- Memory usage: 1.3-1.4GB baseline (real embedding model ~1135MB + overhead)
- Cache hit rate: 70%+

**System Requirements:**
- Minimum RAM: 4GB total system memory (2GB available for CBR server)
- Recommended RAM: 8GB total system memory

**Environment Variables (Optional):**

```bash
# No environment variables needed - defaults are optimal
```

### Scenario 2: Memory-Constrained Environment

**Use Case:** Running on a machine with limited RAM (e.g., 4GB total system memory).

**Important Note:** The real `nomic-ai/nomic-embed-text-v1.5` model requires ~1135MB baseline. This scenario is only viable on systems with at least 4GB total RAM where 1.5GB can be dedicated to the CBR server.

**Configuration (pyproject.toml):**

```toml
[tool.cbr-mcp-server.performance]

[tool.cbr-mcp-server.performance.memory]
max_memory_mb = 1500  # Minimum for real embedding model
warning_threshold = 0.75

[tool.cbr-mcp-server.performance.cache]
max_size = 500  # Reduced cache to minimize overhead
ttl_seconds = 1800
eviction_policy = "LRU"

[tool.cbr-mcp-server.performance.lazy_loading]
enabled = true
preload_hot_cases = false  # Minimize startup memory
batch_size = 10
max_cache_size = 100

[tool.cbr-mcp-server.performance.cache_warming]
enabled = false  # Skip warming to reduce memory

[tool.cbr-mcp-server.performance.index_warming]
enabled = false  # Skip warming to reduce startup memory
```

**Environment Variables:**

```bash
export CBR_MAX_MEMORY_MB=1500
export CBR_CACHE_MAX_SIZE=500
export CBR_LAZY_LOADING_ENABLED=true
export CBR_HOT_CASE_COUNT=0
```

**Expected Performance:**
- Startup time: 2-3 seconds
- Query latency: 100-200ms (p95)
- Memory usage: 1.3-1.5GB (embedding model ~1135MB + minimal overhead)
- Cache hit rate: 60-70%

**System Requirements:**
- Minimum RAM: 4GB total (with 2GB available for other processes)
- Warning: Not suitable for systems with <4GB total RAM

### Scenario 3: High-Performance Workstation

**Use Case:** Running on a powerful development machine with plenty of RAM (16GB+).

**Configuration (pyproject.toml):**

```toml
[tool.cbr-mcp-server.performance]

[tool.cbr-mcp-server.performance.memory]
max_memory_mb = 1024
warning_threshold = 0.85

[tool.cbr-mcp-server.performance.cache]
max_size = 5000
ttl_seconds = 7200
eviction_policy = "LRU"
enable_metrics = true

[tool.cbr-mcp-server.performance.lazy_loading]
enabled = true
preload_hot_cases = true
hot_case_count = 100
background_loading_enabled = true
batch_size = 50
max_cache_size = 500

[tool.cbr-mcp-server.performance.cache_warming]
enabled = true
queries = [
  "authentication code example",
  "database connection pattern",
  "error handling best practice",
  "API endpoint implementation",
  "state management example"
]

[tool.cbr-mcp-server.performance.index_warming]
enabled = true
categories = ["code", "orchestration", "best-practice", "anti-pattern"]
warmup_query_count = 5
```

**Environment Variables:**

```bash
export CBR_MAX_MEMORY_MB=1024
export CBR_CACHE_MAX_SIZE=5000
export CBR_CACHE_TTL_SECONDS=7200
export CBR_HOT_CASE_COUNT=100
export CBR_CACHE_WARMING_ENABLED=true
export CBR_INDEX_WARMING_ENABLED=true
```

**Expected Performance:**
- Startup time: 6-8 seconds (includes warming)
- Query latency: 20-80ms (p95)
- Memory usage: 1.4-1.7GB (embedding model ~1135MB + large cache ~200-500MB)
- Cache hit rate: 80%+

### Scenario 4: Large Case Base (500+ Cases)

**Use Case:** Deployment with significantly larger case base than standard (135 cases).

**Configuration (pyproject.toml):**

```toml
[tool.cbr-mcp-server.performance]

[tool.cbr-mcp-server.performance.memory]
max_memory_mb = 1024
warning_threshold = 0.80

[tool.cbr-mcp-server.performance.cache]
max_size = 2000
ttl_seconds = 3600
eviction_policy = "LRU"

[tool.cbr-mcp-server.performance.lazy_loading]
enabled = true
preload_hot_cases = true
hot_case_count = 100
background_loading_enabled = true
batch_size = 30
max_cache_size = 300

[tool.cbr-mcp-server.performance.cache_warming]
enabled = false

[tool.cbr-mcp-server.performance.index_warming]
enabled = true
categories = ["code", "orchestration", "best-practice"]
warmup_query_count = 3
```

**Expected Performance:**
- Startup time: 5-7 seconds
- Query latency: 80-180ms (p95)
- Memory usage: 1.5-2.0GB (embedding model ~1135MB + larger case base + cache overhead)
- Cache hit rate: 70%+

**System Requirements:**
- Recommended RAM: 16GB total system memory
- Minimum RAM: 8GB total system memory

---

## Performance Tuning Guide

### Understanding Your Workload

Before tuning, understand your usage patterns:

1. **Query Frequency**: How many queries per minute?
2. **Query Diversity**: Do queries repeat or vary widely?
3. **Case Base Size**: How many total cases?
4. **Available Memory**: How much RAM can you allocate?
5. **Startup Criticality**: Is fast startup more important than fast first query?

### Tuning Memory Settings

**Goal: Balance performance with resource constraints**

```yaml
performance:
  memory:
    max_memory_mb: <VALUE>
    warning_threshold: <0.75-0.85>
```

**Tuning Guidelines:**

| Available RAM | Recommended max_memory_mb | Notes |
|--------------|---------------------------|-------|
| 4GB total | 1500 | Minimum viable (embedding model ~1135MB + minimal overhead) |
| 8GB total | 1500-2000 | Balanced, good for most workloads with cache overhead |
| 16GB+ total | 2000-3000 | Aggressive, maximizes performance with large caches |

**Important:** The embedding model alone requires ~1135MB. Values below 1350MB are not viable for production use with the real model.

**Warning Threshold:**
- `0.75`: Conservative, triggers early warnings
- `0.80`: Balanced (default)
- `0.85`: Aggressive, allows higher utilization

### Tuning Cache Settings

**Goal: Maximize cache hit rate while respecting memory limits**

```yaml
performance:
  cache:
    max_size: <VALUE>
    ttl_seconds: <VALUE>
```

**Tuning Guidelines:**

1. **Monitor Cache Hit Rate**
   - Target: >70% for typical workloads
   - If below 60%: Increase `max_size` or `ttl_seconds`
   - If above 85%: Can reduce cache size to save memory

2. **Cache Size Calculation**
   - Each cached result: ~5-10KB
   - 1000 entries ≈ 5-10MB
   - 5000 entries ≈ 25-50MB

3. **TTL Selection**
   - Short TTL (600-1800s): Fast-changing workloads
   - Medium TTL (3600s): Balanced (default)
   - Long TTL (7200-14400s): Stable workloads

**Example Adjustments:**

```yaml
# Low cache hit rate? Increase capacity
cache:
  max_size: 2000      # was 1000
  ttl_seconds: 7200   # was 3600

# High memory usage? Reduce cache
cache:
  max_size: 500       # was 1000
  ttl_seconds: 1800   # was 3600
```

### Tuning Lazy Loading

**Goal: Optimize startup time vs. first-query latency tradeoff**

```yaml
performance:
  lazy_loading:
    enabled: <true|false>
    preload_hot_cases: <true|false>
    hot_case_count: <VALUE>
```

**Tuning Guidelines:**

| Priority | Configuration | Startup Time | First Query |
|----------|--------------|--------------|-------------|
| Fast Startup | enabled: true, preload: false | 2-3s | 150-250ms |
| Balanced | enabled: true, preload: true, hot: 50 | 3-5s | 50-150ms |
| Fast First Query | enabled: false | 6-10s | 20-80ms |

**Adjustments Based on Observations:**

```yaml
# First query consistently slow?
lazy_loading:
  preload_hot_cases: true
  hot_case_count: 100  # Increase from default 50

# Startup too slow?
lazy_loading:
  preload_hot_cases: false
  hot_case_count: 25   # Reduce from default 50

# Don't care about startup time?
lazy_loading:
  enabled: false       # Load everything at startup
```

### Tuning Index Warming

**Goal: Reduce first-query latency for ChromaDB HNSW index**

```yaml
performance:
  index_warming:
    enabled: <true|false>
    warmup_query_count: <1-10>
```

**Impact Analysis:**

- **Disabled**: Startup +0s, First query +50-100ms
- **Enabled (3 queries)**: Startup +1-2s, First query +0ms
- **Enabled (10 queries)**: Startup +3-5s, First query +0ms

**Recommendations:**

```yaml
# Minimize first-query latency
index_warming:
  enabled: true
  warmup_query_count: 5

# Balance startup and performance
index_warming:
  enabled: true
  warmup_query_count: 3  # Default

# Fastest startup
index_warming:
  enabled: false
```

### Iterative Tuning Process

1. **Start with Defaults**: Begin with default configuration
2. **Measure Baseline**: Record startup time, query latency, memory usage
3. **Identify Bottleneck**: What's most problematic?
   - Slow queries? → Increase cache size
   - High memory? → Reduce cache size or enable aggressive lazy loading
   - Slow startup? → Disable warming, reduce hot case count
   - Slow first query? → Enable index warming, increase hot cases
4. **Make One Change**: Adjust one setting at a time
5. **Re-Measure**: Record new performance metrics
6. **Iterate**: Repeat until performance targets met

---

## Rollback Procedures

### When to Rollback

Consider rollback if:

- Server fails to start after migration
- Performance is significantly worse than before
- Memory usage exceeds acceptable limits
- Critical functionality is broken

### Rollback Process

**Method 1: Git Revert (If Using Git)**

```bash
# Stop the upgraded server
kill $(pgrep -f cbr-mcp-server)

# Revert to previous version
git log --oneline  # Find commit before upgrade
git checkout <previous-commit-hash>

# Reinstall old dependencies
pip install -r requirements.txt  # If you have one

# Restart server
cbr-mcp-server
```

**Method 2: Manual Rollback (If Not Using Git)**

```bash
# Stop the upgraded server
kill $(pgrep -f cbr-mcp-server)

# Restore from backup
rm -rf /path/to/cbr_retrieval_mcp
cp -r /path/to/cbr_retrieval_mcp.backup /path/to/cbr_retrieval_mcp

# Restore database (if backed up separately)
rm -rf ./db
cp -r ./db.backup ./db

# Restart server
cd /path/to/cbr_retrieval_mcp
source venv/bin/activate
cbr-mcp-server
```

**Method 3: Disable Performance Features**

If you want to keep the new code but disable performance features:

```bash
# Set environment variables to disable optimization
export CBR_LAZY_LOADING_ENABLED=false
export CBR_CACHE_ENABLED=false
export CBR_INDEX_WARMING_ENABLED=false

# Restart server
cbr-mcp-server
```

### Data Preservation

**Important:** The ChromaDB database is unchanged by this migration.

- No data loss occurs during rollback
- All case embeddings preserved
- All metadata intact
- Simply restarting with old code version restores previous behavior

---

## Troubleshooting

### Startup Issues

**Problem: Server fails to start**

```
Error: ImportError: cannot import name 'ResultCache' from 'cbr_mcp_server.performance'
```

**Solution:**

1. Verify cachetools is installed:
   ```bash
   pip list | grep cachetools
   ```

2. If not installed:
   ```bash
   pip install cachetools>=5.3.0
   ```

3. Verify file structure:
   ```bash
   ls src/cbr_mcp_server/performance/
   # Should see cache_system.py
   ```

**Problem: Server startup exceeds 10 seconds**

**Solution:**

Disable warming features:

```bash
export CBR_CACHE_WARMING_ENABLED=false
export CBR_INDEX_WARMING_ENABLED=false
export CBR_HOT_CASE_COUNT=0
cbr-mcp-server
```

Or edit configuration:

```yaml
performance:
  lazy_loading:
    preload_hot_cases: false
  cache_warming:
    enabled: false
  index_warming:
    enabled: false
```

### Memory Issues

**Problem: Memory usage exceeds limits**

```
[WARNING] Memory usage (650MB) exceeds threshold (512MB)
```

**Solution:**

1. **Reduce cache sizes:**
   ```bash
   export CBR_CACHE_MAX_SIZE=500  # Reduce from 1000
   export CBR_MAX_MEMORY_MB=1024  # Increase limit
   ```

2. **Enable aggressive eviction:**
   ```yaml
   performance:
     cache:
       max_size: 500
       ttl_seconds: 1800  # Shorter TTL
   ```

3. **Reduce lazy loader cache:**
   ```yaml
   performance:
     lazy_loading:
       max_cache_size: 100  # Reduce from 200
   ```

**Problem: Out of memory errors**

```
MemoryError: Unable to allocate array
```

**Solution:**

This indicates system-level memory exhaustion, not just CBR server limits:

1. **Check system memory:**
   ```bash
   free -h  # Linux
   vm_stat  # Mac
   ```

2. **Reduce CBR memory limit:**
   ```bash
   export CBR_MAX_MEMORY_MB=256
   ```

3. **Disable caching entirely (emergency):**
   ```bash
   export CBR_CACHE_ENABLED=false
   export CBR_LAZY_LOADING_ENABLED=false
   ```

### Performance Issues

**Problem: Queries slower than before migration**

**Diagnostic Steps:**

1. **Check cache hit rate:**
   - Look for cache metrics in logs
   - If hit rate <50%, cache is too small or TTL too short

2. **Verify lazy loading isn't causing delays:**
   ```bash
   export CBR_LAZY_LOADING_ENABLED=false
   # Restart and test
   ```

3. **Compare with baseline:**
   - Run benchmark: `pytest tests/benchmarks/test_query_latency_baseline.py`
   - Compare with pre-migration measurements

**Solutions:**

```yaml
# Increase cache capacity
performance:
  cache:
    max_size: 2000
    ttl_seconds: 7200

# Preload more hot cases
performance:
  lazy_loading:
    hot_case_count: 100
    preload_hot_cases: true

# Enable index warming
performance:
  index_warming:
    enabled: true
    warmup_query_count: 5
```

**Problem: First query is very slow**

**Solution:**

Enable index warming:

```yaml
performance:
  index_warming:
    enabled: true
    warmup_query_count: 5
```

Or disable lazy loading:

```yaml
performance:
  lazy_loading:
    enabled: false
```

### Configuration Issues

**Problem: Configuration not taking effect**

**Diagnostic:**

1. **Check configuration precedence:**
   - Environment variables override pyproject.toml
   - Check for conflicting env vars: `printenv | grep CBR_`

2. **Verify configuration file location:**
   ```bash
   # pyproject.toml should be in project root
   ls pyproject.toml
   ```

3. **Check configuration syntax:**
   ```bash
   python -c "import tomli; tomli.load(open('pyproject.toml', 'rb'))"
   ```

**Solution:**

```bash
# Clear all environment variables
unset $(printenv | grep CBR_ | cut -d= -f1)

# Restart server to use pyproject.toml config
cbr-mcp-server
```

### Integration Issues

**Problem: MCP tools not working**

**Diagnostic:**

```bash
# Test server startup
cbr-mcp-server --help

# Test basic functionality
python -c "from cbr_mcp_server import main; print('Import OK')"
```

**Solution:**

The MCP interface is unchanged. If tools aren't working:

1. Check server logs for errors
2. Verify client MCP configuration unchanged
3. Test with previous version to isolate issue
4. If persistent, rollback per [Rollback Procedures](#rollback-procedures)

---

## Validation Steps

### Post-Migration Validation Checklist

After migration, verify these items:

#### 1. Functional Validation

- [ ] **Server starts successfully** (under 10 seconds)
- [ ] **MCP tools respond correctly**
  - Test `cbr_retrieve` with sample query
  - Test `cbr_search_category` with known category
  - Test `cbr_find_similar` with known case ID
- [ ] **Results match expectations**
  - Query returns relevant cases
  - Results format unchanged
  - Metadata fields present

#### 2. Performance Validation

- [ ] **Query latency acceptable** (<200ms p95 for typical queries)
- [ ] **Memory usage within limits** (~1275MB baseline, peak <1500MB for standard workloads)
- [ ] **Cache working** (hit rate >50% after warmup period)
- [ ] **Startup time acceptable** (<5s without warming, <10s with warming)

#### 3. Monitoring Validation

- [ ] **Logs show performance metrics**
- [ ] **No error messages in logs**
- [ ] **Memory warnings only if exceeding threshold**
- [ ] **Cache metrics being tracked**

### Validation Test Scripts

**Basic Functionality Test:**

```bash
# Run integration tests
pytest tests/integration/test_cbr_mcp_server_integration.py -v

# Expected: All tests pass
```

**Performance Benchmark:**

```bash
# Run performance benchmarks
pytest tests/benchmarks/ -v -m "not load"

# Check output for:
# - Query latency <200ms (p95)
# - Memory usage ~1275MB baseline, peak <1500MB
# - Cache hit rate >70%
```

**Manual Query Test:**

If using with Claude Code or another MCP client:

1. Send a test query: "authentication code example"
2. Verify response received in <200ms
3. Send same query again
4. Verify second query is faster (cache hit)
5. Check logs for cache hit confirmation

**Memory Monitoring:**

```bash
# Monitor memory for 5 minutes
watch -n 10 'ps aux | grep cbr-mcp-server | grep -v grep | awk "{print \$6/1024\" MB\"}"'

# Expected: Memory stable under configured limit
```

### Validation Success Criteria

Migration is successful when:

✅ Server starts in <10 seconds
✅ All MCP tools return correct results
✅ Query latency p95 <200ms
✅ Memory usage ~1275MB baseline, peak <1500MB for standard workloads
✅ Cache hit rate >50% after 10 minutes
✅ No errors in server logs
✅ Client integrations continue working

If all criteria met: **Migration successful!**

If any criteria failed: See [Troubleshooting](#troubleshooting) or [Rollback Procedures](#rollback-procedures).

---

## Additional Resources

- **[Performance Configuration Guide](./performance-configuration.md)** - Detailed configuration reference
- **[Performance Tuning Guide](./performance-tuning-guide.md)** - Advanced optimization strategies
- **[Performance Troubleshooting](./performance-troubleshooting.md)** - Detailed problem resolution
- **[Benchmark Results](./benchmark-results.md)** - Measured performance metrics
- **[Monitoring Setup Guide](./monitoring-setup-guide.md)** - Performance monitoring configuration

---

## Support and Feedback

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review server logs in `logs/cbr_server.log`
3. Compare configuration with [Common Deployment Scenarios](#common-deployment-scenarios)
4. Consider a [Rollback](#rollback-procedures) if issues persist

---

**Document Version History:**

- v2.0.0 (2025-12-15): Initial migration guide for performance optimization
- Related to spec: 2025-11-05-local-performance-optimization
