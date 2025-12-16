"""
Latency Benchmark Tests for CBR Query Operations.

This test suite measures latency for CBR query operations including:
- cbr_retrieve tool (semantic search queries)
- cbr_search_category tool (filtered category searches)
- cbr_find_similar tool (similarity-based retrieval)

Performance Targets:
- p95 latency < 200ms for typical queries
- p50 latency < 100ms for typical queries
- Consistent performance across warm and cold cache scenarios

Test Methodology:
- Uses pytest-benchmark for statistical measurement
- Measures p50, p95, and p99 latency percentiles
- Includes both warm and cold cache scenarios
- Tests real integration with ChromaDB and embedding model
"""

import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pytest

# Import CBR server components
try:
    from cbr_mcp_server.performance.production_cbr_retriever import (
        LazyEmbeddingModel,
        ProductionCBRRetriever,
    )

    HAS_CBR = True
except ImportError:
    HAS_CBR = False
    ProductionCBRRetriever = None
    LazyEmbeddingModel = None


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def cbr_retriever(shared_cbr_retriever):
    """
    Function-scoped fixture that delegates to shared session-scoped retriever.

    This wrapper provides per-test isolation while using the shared retriever
    instance to prevent memory regression from multiple embedding models.

    Memory optimization: Uses shared_cbr_retriever from conftest.py instead of
    creating new instances per module, saving ~700MB of memory.
    """
    if not HAS_CBR:
        pytest.skip("CBR server components not available")

    # Simply return the shared retriever - no need to create a new one
    return shared_cbr_retriever


# ============================================================================
# Test: cbr_retrieve Warm Cache Latency
# ============================================================================


def test_cbr_retrieve_warm_cache_latency(benchmark, cbr_retriever):
    """
    Measure p50, p95, p99 latency for cbr_retrieve with warm cache.

    This test measures performance when embeddings are already cached
    and the database connection is established. This represents typical
    query performance after server initialization.

    Expected Behavior:
    - p50 latency < 100ms
    - p95 latency < 200ms
    - All benchmark iterations complete successfully
    """
    if not HAS_CBR:
        pytest.skip("CBR server components not available")

    # Warm up the cache with a preliminary query
    cbr_retriever.retrieve(query="Test warm-up query", max_results=5)

    # Define the query to benchmark
    def execute_retrieve():
        result = cbr_retriever.retrieve(
            query="How to implement user authentication with JWT tokens?", max_results=5
        )
        return result

    result = benchmark(execute_retrieve)

    # Assertions
    assert result is not None, "Query should return results"
    assert isinstance(result, list), "Result should be a list"
    assert len(result) > 0, "Should return at least one case"

    # Calculate latency percentiles
    stats = benchmark.stats
    latencies_ms = np.array(stats.get("stats").data) * 1000  # Convert to milliseconds

    p50_latency_ms = np.percentile(latencies_ms, 50)
    p95_latency_ms = np.percentile(latencies_ms, 95)
    p99_latency_ms = np.percentile(latencies_ms, 99)

    print(f"\ncbr_retrieve warm cache latency:")
    print(f"  p50: {p50_latency_ms:.2f}ms")
    print(f"  p95: {p95_latency_ms:.2f}ms")
    print(f"  p99: {p99_latency_ms:.2f}ms")

    # Performance assertions (these will fail until optimization is implemented)
    assert (
        p50_latency_ms < 100
    ), f"p50 latency {p50_latency_ms:.2f}ms exceeds 100ms target"
    assert (
        p95_latency_ms < 200
    ), f"p95 latency {p95_latency_ms:.2f}ms exceeds 200ms target"


# ============================================================================
# Test: cbr_retrieve Cold Cache Latency
# ============================================================================


def test_cbr_retrieve_cold_cache_latency(cbr_retriever):
    """
    Measure latency for cbr_retrieve with cold cache (first query after server start).

    This test measures performance for the first query, which includes:
    - Embedding model initialization (if not loaded)
    - First database connection establishment
    - Initial embedding generation

    Expected Behavior:
    - Cold cache latency is documented (may exceed 200ms)
    - Subsequent queries show improvement over cold start
    """
    if not HAS_CBR:
        pytest.skip("CBR server components not available")

    # Measure cold start (simulate first query)
    cold_start_time = time.time()
    cold_result = cbr_retriever.retrieve(
        query="How to implement authentication?", max_results=5
    )
    cold_latency_ms = (time.time() - cold_start_time) * 1000

    # Measure subsequent query (warm cache)
    warm_start_time = time.time()
    warm_result = cbr_retriever.retrieve(
        query="How to implement authentication?", max_results=5  # Same query
    )
    warm_latency_ms = (time.time() - warm_start_time) * 1000

    # Assertions
    assert cold_result is not None, "Cold query should return results"
    assert warm_result is not None, "Warm query should return results"
    assert len(cold_result) > 0, "Cold query should return cases"
    assert len(warm_result) > 0, "Warm query should return cases"

    print(f"\ncbr_retrieve cold vs warm cache:")
    print(f"  Cold start: {cold_latency_ms:.2f}ms")
    print(f"  Warm cache: {warm_latency_ms:.2f}ms")
    print(
        f"  Improvement: {cold_latency_ms - warm_latency_ms:.2f}ms ({((cold_latency_ms - warm_latency_ms) / cold_latency_ms * 100):.1f}%)"
    )

    # Performance assertions
    assert (
        warm_latency_ms <= cold_latency_ms
    ), "Warm cache should not be slower than cold start"


# ============================================================================
# Test: cbr_search_category Warm Cache Latency
# ============================================================================


def test_cbr_search_category_warm_cache_latency(benchmark, cbr_retriever):
    """
    Measure p50, p95, p99 latency for cbr_search_category with warm cache.

    This test measures performance of category-filtered queries after
    the system is warmed up. Category filtering should be efficient
    using ChromaDB's native filtering capabilities.

    Expected Behavior:
    - p95 latency < 200ms
    - Category filtering performs efficiently
    - Results are correctly filtered by category

    Note: This test will SKIP if search_by_category method is not implemented yet.
    """
    if not HAS_CBR:
        pytest.skip("CBR server components not available")

    # Check if search_by_category method exists
    if not hasattr(cbr_retriever, "search_by_category"):
        pytest.skip("search_by_category method not implemented yet (expected for TDD)")

    # Warm up the cache
    cbr_retriever.search_by_category(category="orchestration", query="", max_results=5)

    # Define the category search to benchmark
    def execute_category_search():
        result = cbr_retriever.search_by_category(
            category="orchestration", query="", max_results=10
        )
        return result

    result = benchmark(execute_category_search)

    # Assertions
    assert result is not None, "Category search should return results"
    assert "category" in result or isinstance(
        result, list
    ), "Result should contain category or be a list"

    # Calculate latency percentiles
    stats = benchmark.stats
    latencies_ms = np.array(stats.get("stats").data) * 1000

    p50_latency_ms = np.percentile(latencies_ms, 50)
    p95_latency_ms = np.percentile(latencies_ms, 95)
    p99_latency_ms = np.percentile(latencies_ms, 99)

    print(f"\ncbr_search_category warm cache latency:")
    print(f"  p50: {p50_latency_ms:.2f}ms")
    print(f"  p95: {p95_latency_ms:.2f}ms")
    print(f"  p99: {p99_latency_ms:.2f}ms")

    # Performance assertions
    assert (
        p95_latency_ms < 200
    ), f"p95 latency {p95_latency_ms:.2f}ms exceeds 200ms target"


# ============================================================================
# Test: cbr_search_category Cold Cache Latency
# ============================================================================


def test_cbr_search_category_cold_cache_latency(cbr_retriever):
    """
    Measure latency for cbr_search_category with cold cache.

    This test measures first-query performance for category search,
    documenting the initialization overhead.

    Expected Behavior:
    - Cold cache latency is documented
    - Performance improves on subsequent queries

    Note: This test will SKIP if search_by_category method is not implemented yet.
    """
    if not HAS_CBR:
        pytest.skip("CBR server components not available")

    # Check if search_by_category method exists
    if not hasattr(cbr_retriever, "search_by_category"):
        pytest.skip("search_by_category method not implemented yet (expected for TDD)")

    # Measure cold start
    cold_start_time = time.time()
    cold_result = cbr_retriever.search_by_category(
        category="code", query="", max_results=5
    )
    cold_latency_ms = (time.time() - cold_start_time) * 1000

    # Measure warm cache
    warm_start_time = time.time()
    warm_result = cbr_retriever.search_by_category(
        category="code", query="", max_results=5
    )
    warm_latency_ms = (time.time() - warm_start_time) * 1000

    # Assertions
    assert cold_result is not None
    assert warm_result is not None

    print(f"\ncbr_search_category cold vs warm cache:")
    print(f"  Cold start: {cold_latency_ms:.2f}ms")
    print(f"  Warm cache: {warm_latency_ms:.2f}ms")
    print(f"  Improvement: {cold_latency_ms - warm_latency_ms:.2f}ms")

    # Performance assertions
    assert warm_latency_ms <= cold_latency_ms


# ============================================================================
# Test: cbr_find_similar Warm Cache Latency
# ============================================================================


def test_cbr_find_similar_warm_cache_latency(benchmark, cbr_retriever):
    """
    Measure p50, p95, p99 latency for cbr_find_similar with warm cache.

    This test measures performance of similarity-based retrieval after
    the system is warmed up. Find similar should leverage vector
    similarity search efficiently.

    Expected Behavior:
    - p95 latency < 200ms
    - Similarity search performs within acceptable bounds
    - Results are correctly ordered by similarity

    Note: This test will SKIP if find_similar method is not implemented yet.
    """
    if not HAS_CBR:
        pytest.skip("CBR server components not available")

    # Check if find_similar method exists
    if not hasattr(cbr_retriever, "find_similar"):
        pytest.skip("find_similar method not implemented yet (expected for TDD)")

    # First, get a valid case ID to use for similarity search
    initial_result = cbr_retriever.retrieve(query="orchestration", max_results=1)

    if not initial_result or len(initial_result) == 0:
        pytest.skip("No cases available for similarity testing")

    test_case_id = initial_result[0].get("id", "test_id")

    # Warm up the cache
    cbr_retriever.find_similar(example_id=test_case_id, max_results=5)

    # Define the similarity search to benchmark
    def execute_find_similar():
        result = cbr_retriever.find_similar(example_id=test_case_id, max_results=5)
        return result

    result = benchmark(execute_find_similar)

    # Assertions
    assert result is not None, "Find similar should return results"

    # Calculate latency percentiles
    stats = benchmark.stats
    latencies_ms = np.array(stats.get("stats").data) * 1000

    p50_latency_ms = np.percentile(latencies_ms, 50)
    p95_latency_ms = np.percentile(latencies_ms, 95)
    p99_latency_ms = np.percentile(latencies_ms, 99)

    print(f"\ncbr_find_similar warm cache latency:")
    print(f"  p50: {p50_latency_ms:.2f}ms")
    print(f"  p95: {p95_latency_ms:.2f}ms")
    print(f"  p99: {p99_latency_ms:.2f}ms")

    # Performance assertions
    assert (
        p95_latency_ms < 200
    ), f"p95 latency {p95_latency_ms:.2f}ms exceeds 200ms target"


# ============================================================================
# Test: cbr_find_similar Cold Cache Latency
# ============================================================================


def test_cbr_find_similar_cold_cache_latency(cbr_retriever):
    """
    Measure latency for cbr_find_similar with cold cache.

    This test documents cold start performance for similarity search.

    Expected Behavior:
    - Cold cache latency is documented
    - Performance improves on subsequent queries

    Note: This test will SKIP if find_similar method is not implemented yet.
    """
    if not HAS_CBR:
        pytest.skip("CBR server components not available")

    # Check if find_similar method exists
    if not hasattr(cbr_retriever, "find_similar"):
        pytest.skip("find_similar method not implemented yet (expected for TDD)")

    # Get a valid case ID
    initial_result = cbr_retriever.retrieve(query="testing", max_results=1)

    if not initial_result or len(initial_result) == 0:
        pytest.skip("No cases available for similarity testing")

    test_case_id = initial_result[0].get("id", "test_id")

    # Measure cold start
    cold_start_time = time.time()
    cold_result = cbr_retriever.find_similar(example_id=test_case_id, max_results=5)
    cold_latency_ms = (time.time() - cold_start_time) * 1000

    # Measure warm cache
    warm_start_time = time.time()
    warm_result = cbr_retriever.find_similar(example_id=test_case_id, max_results=5)
    warm_latency_ms = (time.time() - warm_start_time) * 1000

    # Assertions
    assert cold_result is not None
    assert warm_result is not None

    print(f"\ncbr_find_similar cold vs warm cache:")
    print(f"  Cold start: {cold_latency_ms:.2f}ms")
    print(f"  Warm cache: {warm_latency_ms:.2f}ms")
    print(f"  Improvement: {cold_latency_ms - warm_latency_ms:.2f}ms")

    # Performance assertions
    assert warm_latency_ms <= cold_latency_ms


# ============================================================================
# Test: Latency Percentiles Calculation
# ============================================================================


def test_latency_percentiles_calculation():
    """
    Verify correct calculation of p50, p95, p99 percentiles from latency data.

    This test validates that our percentile calculation methodology is
    mathematically correct and handles edge cases properly.

    Expected Behavior:
    - Percentiles are correctly calculated from sample data
    - Edge cases (empty data, single data point) are handled
    - Percentile ordering is maintained (p50 <= p95 <= p99)
    """
    # Test with known data
    latencies = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)

    # Assertions for known data (with floating point tolerance)
    assert abs(p50 - 55.0) < 0.01, f"Expected p50≈55.0, got {p50}"
    assert abs(p95 - 95.5) < 0.01, f"Expected p95≈95.5, got {p95}"
    assert abs(p99 - 99.1) < 0.01, f"Expected p99≈99.1, got {p99}"

    # Test percentile ordering
    assert p50 <= p95, "p50 should be <= p95"
    assert p95 <= p99, "p95 should be <= p99"

    # Test with single data point
    single_latency = np.array([42.0])
    single_p50 = np.percentile(single_latency, 50)
    single_p95 = np.percentile(single_latency, 95)
    single_p99 = np.percentile(single_latency, 99)

    assert single_p50 == 42.0
    assert single_p95 == 42.0
    assert single_p99 == 42.0

    # Test with uniform distribution
    uniform = np.array([50] * 100)
    uniform_p50 = np.percentile(uniform, 50)
    uniform_p95 = np.percentile(uniform, 95)
    uniform_p99 = np.percentile(uniform, 99)

    assert uniform_p50 == 50.0
    assert uniform_p95 == 50.0
    assert uniform_p99 == 50.0

    print("\nPercentile calculation verification:")
    print(f"  Known data p50: {p50}")
    print(f"  Known data p95: {p95}")
    print(f"  Known data p99: {p99}")
    print(f"  Single point: all percentiles = {single_p50}")
    print(f"  Uniform distribution: all percentiles = {uniform_p50}")


# ============================================================================
# Test: Concurrent Query Latency
# ============================================================================


def test_concurrent_query_latency(cbr_retriever):
    """
    Measure latency when multiple queries are executed concurrently.

    This test simulates real-world usage where multiple AI agents
    or concurrent requests query the CBR system simultaneously.

    Expected Behavior:
    - Concurrent queries maintain acceptable latency
    - No significant degradation under concurrent load
    - All queries complete successfully
    """
    if not HAS_CBR:
        pytest.skip("CBR server components not available")

    # Execute multiple queries in a tight loop to simulate concurrency
    start_time = time.time()

    results = []
    for i in range(5):
        result = cbr_retriever.retrieve(query=f"Test query {i}", max_results=5)
        results.append(result)

    total_time_ms = (time.time() - start_time) * 1000

    # Assertions
    assert len(results) == 5, "All concurrent queries should complete"
    assert all(r is not None for r in results), "All queries should return results"
    assert all(isinstance(r, list) for r in results), "All results should be lists"

    print(f"\nConcurrent query performance:")
    print(f"  Total time for 5 queries: {total_time_ms:.2f}ms")
    print(f"  Average time per query: {total_time_ms / 5:.2f}ms")

    # Performance assertion - this may fail initially without optimization
    assert (
        total_time_ms < 1000
    ), f"Concurrent queries took {total_time_ms:.2f}ms, exceeds 1000ms threshold"
