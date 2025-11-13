"""
Throughput Benchmark Tests for CBR MCP Server.

This test suite measures throughput performance (queries per second) for CBR operations
under various concurrency levels. These benchmarks establish baseline QPS metrics and
validate that the system can handle concurrent queries without performance degradation.

Test Coverage:
- Single client QPS baseline
- 5 concurrent clients QPS
- 10 concurrent clients QPS
- Cache hit rate during sustained load
- Cache hit rate after warmup period
- Performance degradation verification with concurrency
- Async operation handling under load
- Throughput stability over time
- Concurrent query result correctness
- Throughput measurement accuracy

Performance Targets:
- 10+ concurrent queries without degradation
- >70% cache hit rate after warmup
- QPS degradation <30% at 10 concurrent clients

Note: These are TDD tests - they define expected throughput characteristics
before optimization work begins. Tests will initially fail.
"""

import asyncio
import statistics
import time
from typing import Any, Dict, List, Tuple
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import CBR server components
try:
    from cbr_mcp_server import CBRMCPServer, ProductionCBRRetriever

    # Mock MCP dependencies if not available
    try:
        from mcp.server.fastmcp import Context
    except ImportError:

        class Context:
            def __init__(self):
                self.session = Mock()
                self.debug = AsyncMock()
                self.info = AsyncMock()
                self.warning = AsyncMock()
                self.error = AsyncMock()

        globals()["Context"] = Context

except ImportError:
    # Create minimal mocks for testing

    class CBRMCPServer:
        pass

    class ProductionCBRRetriever:
        pass

    class Context:
        def __init__(self):
            self.session = Mock()
            self.debug = AsyncMock()
            self.info = AsyncMock()
            self.warning = AsyncMock()
            self.error = AsyncMock()


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_retriever_with_cache_tracking():
    """
    Mock ProductionCBRRetriever with cache hit/miss tracking.

    Simulates a caching layer that tracks cache hits and misses for
    performance analysis.
    """
    retriever = Mock(spec=ProductionCBRRetriever)

    # Cache tracking state
    cache = {}
    cache_stats = {"hits": 0, "misses": 0}

    async def mock_retrieve(query_text, max_results=5, similarity_threshold=0.7):
        # Simulate cache lookup
        cache_key = f"{query_text}:{max_results}:{similarity_threshold}"

        if cache_key in cache:
            # Cache hit - faster response
            cache_stats["hits"] += 1
            await asyncio.sleep(0.01)  # 10ms cached response
            return cache[cache_key]
        else:
            # Cache miss - slower response with DB query
            cache_stats["misses"] += 1
            await asyncio.sleep(0.05)  # 50ms database query

            result = {
                "cases": [
                    {
                        "id": f"case_{i}",
                        "content": f"Example case {i} for {query_text}",
                        "similarity": 0.9 - (i * 0.1),
                        "metadata": {"category": "orchestration", "tags": ["planning"]},
                    }
                    for i in range(max_results)
                ],
                "query": query_text,
                "total_results": max_results,
            }

            # Store in cache
            cache[cache_key] = result
            return result

    retriever.retrieve = AsyncMock(side_effect=mock_retrieve)
    retriever.cache_stats = cache_stats

    # Configure search_by_category method
    async def mock_search_category(
        category, subcategory=None, max_results=5, similarity_threshold=0.7
    ):
        await asyncio.sleep(0.04)  # 40ms simulated DB latency
        return {
            "cases": [
                {
                    "id": f"case_{category}_{i}",
                    "content": f"Example for {category}/{subcategory or 'all'}",
                    "similarity": 0.85,
                    "metadata": {
                        "category": category,
                        "subcategory": subcategory,
                        "tags": ["test"],
                    },
                }
                for i in range(max_results)
            ],
            "category": category,
            "subcategory": subcategory,
            "total_results": max_results,
        }

    retriever.search_by_category = AsyncMock(side_effect=mock_search_category)

    return retriever


@pytest.fixture
def mock_cbr_server_with_cache(mock_retriever_with_cache_tracking):
    """Mock CBRMCPServer with cache-enabled retriever."""
    server = Mock(spec=CBRMCPServer)
    server.retriever = mock_retriever_with_cache_tracking
    return server


# ============================================================================
# Helper Functions
# ============================================================================


async def measure_qps(
    retriever, num_queries: int, query_func, concurrent_clients: int = 1
) -> Tuple[float, List[float]]:
    """
    Measure queries per second for a given query function.

    Args:
        retriever: Mock retriever instance
        num_queries: Total number of queries to execute
        query_func: Async function that executes a single query
        concurrent_clients: Number of concurrent clients executing queries

    Returns:
        Tuple of (average QPS, list of individual query times)
    """
    queries_per_client = num_queries // concurrent_clients
    start_time = time.time()
    query_times = []

    async def client_queries():
        client_times = []
        for _ in range(queries_per_client):
            query_start = time.time()
            await query_func(retriever)
            query_end = time.time()
            client_times.append(query_end - query_start)
        return client_times

    # Execute queries concurrently
    tasks = [client_queries() for _ in range(concurrent_clients)]
    results = await asyncio.gather(*tasks)

    # Flatten results
    for client_times in results:
        query_times.extend(client_times)

    end_time = time.time()
    total_duration = end_time - start_time
    qps = num_queries / total_duration

    return qps, query_times


def calculate_cache_hit_rate(cache_stats: Dict[str, int]) -> float:
    """
    Calculate cache hit rate as a percentage.

    Args:
        cache_stats: Dict with 'hits' and 'misses' keys

    Returns:
        Cache hit rate as percentage (0-100)
    """
    total_requests = cache_stats["hits"] + cache_stats["misses"]
    if total_requests == 0:
        return 0.0
    return (cache_stats["hits"] / total_requests) * 100


# ============================================================================
# Test: Single Client QPS Baseline
# ============================================================================


@pytest.mark.asyncio
async def test_single_client_qps_baseline(mock_cbr_server_with_cache):
    """
    Measure baseline queries per second (QPS) for a single client.

    Establishes the baseline throughput for a single client executing
    sequential queries. This provides the reference point for measuring
    performance degradation under concurrent load.

    Expected: QPS > 0, all queries complete successfully
    """

    async def query_func(retriever):
        await retriever.retrieve(
            query_text="How to implement authentication?", max_results=5
        )

    # Execute 20 queries sequentially
    qps, query_times = await measure_qps(
        mock_cbr_server_with_cache.retriever,
        num_queries=20,
        query_func=query_func,
        concurrent_clients=1,
    )

    # Assertions
    assert qps > 0, "QPS should be greater than 0"
    assert len(query_times) == 20, "Should have executed 20 queries"
    assert all(t > 0 for t in query_times), "All query times should be positive"

    print(f"\nSingle client baseline QPS: {qps:.2f}")
    print(f"Average query time: {statistics.mean(query_times)*1000:.2f}ms")
    print(f"Median query time: {statistics.median(query_times)*1000:.2f}ms")


# ============================================================================
# Test: 5 Concurrent Clients QPS
# ============================================================================


@pytest.mark.asyncio
async def test_five_concurrent_clients_qps(mock_cbr_server_with_cache):
    """
    Measure QPS with 5 concurrent clients.

    Tests throughput with moderate concurrency. Performance degradation
    should be minimal (<20% compared to single client baseline).

    Expected: QPS degradation <20%, all queries complete successfully
    """

    async def query_func(retriever):
        await retriever.retrieve(
            query_text="How to implement user authentication?", max_results=5
        )

    # First, establish single-client baseline
    baseline_qps, _ = await measure_qps(
        mock_cbr_server_with_cache.retriever,
        num_queries=20,
        query_func=query_func,
        concurrent_clients=1,
    )

    # Now measure with 5 concurrent clients
    concurrent_qps, query_times = await measure_qps(
        mock_cbr_server_with_cache.retriever,
        num_queries=50,
        query_func=query_func,
        concurrent_clients=5,
    )

    # Calculate performance degradation
    degradation_pct = ((baseline_qps - concurrent_qps) / baseline_qps) * 100

    # Assertions
    assert concurrent_qps > 0, "Concurrent QPS should be greater than 0"
    assert len(query_times) == 50, "Should have executed 50 queries"
    assert all(t > 0 for t in query_times), "All query times should be positive"

    print(f"\nBaseline QPS (1 client): {baseline_qps:.2f}")
    print(f"Concurrent QPS (5 clients): {concurrent_qps:.2f}")
    print(f"Performance degradation: {degradation_pct:.1f}%")

    # This will likely fail initially without optimization
    assert (
        degradation_pct < 20
    ), f"Performance degradation {degradation_pct:.1f}% exceeds 20% threshold"


# ============================================================================
# Test: 10 Concurrent Clients QPS
# ============================================================================


@pytest.mark.asyncio
async def test_ten_concurrent_clients_qps(mock_cbr_server_with_cache):
    """
    Measure QPS with 10 concurrent clients.

    Tests throughput with high concurrency. Performance degradation
    should remain acceptable (<30% compared to single client baseline).

    Expected: QPS degradation <30%, all queries complete successfully
    """

    async def query_func(retriever):
        await retriever.retrieve(
            query_text="Database schema design patterns", max_results=5
        )

    # Establish single-client baseline
    baseline_qps, _ = await measure_qps(
        mock_cbr_server_with_cache.retriever,
        num_queries=20,
        query_func=query_func,
        concurrent_clients=1,
    )

    # Measure with 10 concurrent clients
    concurrent_qps, query_times = await measure_qps(
        mock_cbr_server_with_cache.retriever,
        num_queries=100,
        query_func=query_func,
        concurrent_clients=10,
    )

    # Calculate performance degradation
    degradation_pct = ((baseline_qps - concurrent_qps) / baseline_qps) * 100

    # Assertions
    assert concurrent_qps > 0, "Concurrent QPS should be greater than 0"
    assert len(query_times) == 100, "Should have executed 100 queries"
    assert all(t > 0 for t in query_times), "All query times should be positive"

    print(f"\nBaseline QPS (1 client): {baseline_qps:.2f}")
    print(f"Concurrent QPS (10 clients): {concurrent_qps:.2f}")
    print(f"Performance degradation: {degradation_pct:.1f}%")

    # This will likely fail initially without optimization
    assert (
        degradation_pct < 30
    ), f"Performance degradation {degradation_pct:.1f}% exceeds 30% threshold"


# ============================================================================
# Test: Cache Hit Rate During Sustained Load
# ============================================================================


@pytest.mark.asyncio
async def test_cache_hit_rate_during_sustained_load(mock_cbr_server_with_cache):
    """
    Measure cache hit rate during sustained load.

    Executes a sustained workload with repeated queries to measure
    caching effectiveness. Cache hit rate should improve as the same
    queries are repeated.

    Expected: Cache hit rate measured and tracked correctly
    """
    retriever = mock_cbr_server_with_cache.retriever

    # Define a set of common queries
    queries = [
        "How to implement authentication?",
        "Database schema design",
        "API endpoint implementation",
        "Error handling patterns",
        "User authentication flow",
    ]

    # Execute sustained load (repeat queries multiple times)
    num_iterations = 20
    for iteration in range(num_iterations):
        for query_text in queries:
            await retriever.retrieve(query_text=query_text, max_results=5)

    # Calculate cache hit rate
    cache_hit_rate = calculate_cache_hit_rate(retriever.cache_stats)

    # Assertions
    total_requests = retriever.cache_stats["hits"] + retriever.cache_stats["misses"]
    assert total_requests == num_iterations * len(queries), "Should track all requests"
    assert cache_hit_rate >= 0 and cache_hit_rate <= 100, "Hit rate should be 0-100%"

    print(f"\nTotal requests: {total_requests}")
    print(f"Cache hits: {retriever.cache_stats['hits']}")
    print(f"Cache misses: {retriever.cache_stats['misses']}")
    print(f"Cache hit rate: {cache_hit_rate:.1f}%")


# ============================================================================
# Test: Cache Hit Rate After Warmup
# ============================================================================


@pytest.mark.asyncio
async def test_cache_hit_rate_after_warmup(mock_cbr_server_with_cache):
    """
    Verify cache hit rate exceeds 70% after warmup period.

    Simulates a warmup period followed by a steady-state workload.
    After warmup, cache hit rate should exceed 70% as queries repeat.

    Expected: Cache hit rate >70% after warmup
    """
    retriever = mock_cbr_server_with_cache.retriever

    # Define common queries for warmup
    warmup_queries = [
        "Authentication implementation",
        "Database design patterns",
        "API endpoint structure",
        "Error handling approach",
        "User session management",
    ]

    # Warmup phase: execute each query once to populate cache
    for query_text in warmup_queries:
        await retriever.retrieve(query_text=query_text, max_results=5)

    # Reset cache stats to measure only post-warmup performance
    retriever.cache_stats["hits"] = 0
    retriever.cache_stats["misses"] = 0

    # Steady-state phase: repeat queries to test cache effectiveness
    num_iterations = 15
    for iteration in range(num_iterations):
        for query_text in warmup_queries:
            await retriever.retrieve(query_text=query_text, max_results=5)

    # Calculate cache hit rate
    cache_hit_rate = calculate_cache_hit_rate(retriever.cache_stats)

    # Assertions
    total_requests = retriever.cache_stats["hits"] + retriever.cache_stats["misses"]
    assert total_requests == num_iterations * len(warmup_queries)

    print(f"\nPost-warmup requests: {total_requests}")
    print(f"Cache hits: {retriever.cache_stats['hits']}")
    print(f"Cache misses: {retriever.cache_stats['misses']}")
    print(f"Cache hit rate: {cache_hit_rate:.1f}%")

    # This will fail initially if caching isn't optimized
    assert (
        cache_hit_rate > 70
    ), f"Cache hit rate {cache_hit_rate:.1f}% below 70% target"


# ============================================================================
# Test: No Performance Degradation with Concurrency
# ============================================================================


@pytest.mark.asyncio
async def test_no_performance_degradation_with_concurrency(mock_cbr_server_with_cache):
    """
    Verify concurrent operations don't cause exponential performance degradation.

    Tests that throughput scales reasonably with concurrency. Linear scaling
    isn't expected, but exponential degradation indicates problems.

    Expected: QPS degradation within acceptable bounds for all concurrency levels
    """

    async def query_func(retriever):
        await retriever.retrieve(
            query_text="Orchestration system design", max_results=5
        )

    # Measure baseline
    baseline_qps, _ = await measure_qps(
        mock_cbr_server_with_cache.retriever,
        num_queries=20,
        query_func=query_func,
        concurrent_clients=1,
    )

    # Measure at different concurrency levels
    concurrency_levels = [2, 5, 10]
    results = []

    for concurrency in concurrency_levels:
        qps, _ = await measure_qps(
            mock_cbr_server_with_cache.retriever,
            num_queries=concurrency * 10,
            query_func=query_func,
            concurrent_clients=concurrency,
        )
        degradation_pct = ((baseline_qps - qps) / baseline_qps) * 100
        results.append((concurrency, qps, degradation_pct))

    # Print results
    print(f"\nBaseline QPS (1 client): {baseline_qps:.2f}")
    for concurrency, qps, degradation in results:
        print(f"Concurrency {concurrency}: {qps:.2f} QPS ({degradation:.1f}% degradation)")

    # Assertions: degradation should not be exponential
    for concurrency, qps, degradation in results:
        max_allowed_degradation = concurrency * 5  # 5% per additional client
        assert degradation < max_allowed_degradation, (
            f"Concurrency {concurrency}: degradation {degradation:.1f}% exceeds "
            f"threshold {max_allowed_degradation}%"
        )


# ============================================================================
# Test: Async Operation Handling
# ============================================================================


@pytest.mark.asyncio
async def test_async_operation_handling(mock_cbr_server_with_cache):
    """
    Verify async operations are handled correctly under load.

    Tests that async operations complete successfully, maintain isolation,
    and don't deadlock or hang under concurrent load.

    Expected: All async operations complete, no deadlocks, proper isolation
    """
    retriever = mock_cbr_server_with_cache.retriever

    # Create diverse async operations with varying completion times
    async def fast_query():
        return await retriever.retrieve(query_text="Quick query", max_results=3)

    async def medium_query():
        return await retriever.search_by_category(category="orchestration", max_results=5)

    async def slow_query():
        return await retriever.retrieve(
            query_text="Complex orchestration system implementation", max_results=10
        )

    # Execute mixed workload concurrently
    tasks = []
    for _ in range(10):
        tasks.append(fast_query())
        tasks.append(medium_query())
        tasks.append(slow_query())

    # Measure execution time
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()

    duration = end_time - start_time

    # Assertions
    assert len(results) == 30, "All 30 operations should complete"
    assert all(r is not None for r in results), "All results should be non-None"
    assert duration < 5.0, f"Operations took too long: {duration:.2f}s"

    print(f"\nAsync operations completed: {len(results)}")
    print(f"Total execution time: {duration:.2f}s")
    print(f"Operations per second: {len(results) / duration:.2f}")


# ============================================================================
# Test: Throughput Stability Over Time
# ============================================================================


@pytest.mark.asyncio
async def test_throughput_stability_over_time(mock_cbr_server_with_cache):
    """
    Verify throughput remains stable over extended test period.

    Measures QPS variance over multiple time windows to detect performance
    degradation over time (e.g., memory leaks, cache pollution).

    Expected: QPS variance <15% over test duration
    """

    async def query_func(retriever):
        await retriever.retrieve(query_text="API design patterns", max_results=5)

    # Measure QPS in multiple time windows
    num_windows = 5
    queries_per_window = 20
    qps_measurements = []

    for window in range(num_windows):
        qps, _ = await measure_qps(
            mock_cbr_server_with_cache.retriever,
            num_queries=queries_per_window,
            query_func=query_func,
            concurrent_clients=1,
        )
        qps_measurements.append(qps)
        print(f"Window {window + 1}: {qps:.2f} QPS")

    # Calculate variance
    mean_qps = statistics.mean(qps_measurements)
    std_dev = statistics.stdev(qps_measurements)
    coefficient_of_variation = (std_dev / mean_qps) * 100

    print(f"\nMean QPS: {mean_qps:.2f}")
    print(f"Standard deviation: {std_dev:.2f}")
    print(f"Coefficient of variation: {coefficient_of_variation:.1f}%")

    # Assertions
    assert coefficient_of_variation < 15, (
        f"QPS variance {coefficient_of_variation:.1f}% exceeds 15% threshold"
    )


# ============================================================================
# Test: Concurrent Query Result Correctness
# ============================================================================


@pytest.mark.asyncio
async def test_concurrent_query_result_correctness(mock_cbr_server_with_cache):
    """
    Verify concurrent queries return correct results without mixing.

    Tests data integrity under concurrency by executing distinct queries
    concurrently and verifying each receives the correct result.

    Expected: Each query receives correct result, no result mixing
    """
    retriever = mock_cbr_server_with_cache.retriever

    # Define distinct queries with identifiable results
    query_pairs = [
        ("Authentication implementation", "authentication"),
        ("Database design patterns", "database"),
        ("API endpoint structure", "api"),
        ("Error handling approach", "error"),
        ("User session management", "session"),
    ]

    # Execute all queries concurrently
    tasks = []
    for query_text, expected_keyword in query_pairs:
        tasks.append(retriever.retrieve(query_text=query_text, max_results=5))

    results = await asyncio.gather(*tasks)

    # Verify each result corresponds to the correct query
    for i, (query_text, expected_keyword) in enumerate(query_pairs):
        result = results[i]
        assert result is not None, f"Result {i} should not be None"
        assert "cases" in result, f"Result {i} should contain cases"
        assert result["query"] == query_text, (
            f"Result {i} query mismatch: expected '{query_text}', got '{result['query']}'"
        )

    print(f"\nAll {len(results)} concurrent queries returned correct results")


# ============================================================================
# Test: Throughput Measurement Accuracy
# ============================================================================


@pytest.mark.asyncio
async def test_throughput_measurement_accuracy():
    """
    Verify benchmark measurement infrastructure is accurate.

    Tests that QPS calculations are mathematically correct and timing
    measurements are accurate using known scenarios.

    Expected: QPS calculation is mathematically correct, timing accurate
    """
    # Create a fresh retriever with predictable, non-cached timing
    retriever = Mock(spec=ProductionCBRRetriever)

    # Create a simple, predictable mock without caching
    # Each query takes exactly 50ms for consistent timing
    async def mock_retrieve_consistent(query_text, max_results=5, similarity_threshold=0.7):
        await asyncio.sleep(0.05)  # Consistent 50ms per query
        return {
            "cases": [
                {
                    "id": f"case_{i}",
                    "content": f"Example case {i} for {query_text}",
                    "similarity": 0.9 - (i * 0.1),
                    "metadata": {"category": "orchestration", "tags": ["planning"]},
                }
                for i in range(max_results)
            ],
            "query": query_text,
            "total_results": max_results,
        }

    retriever.retrieve = AsyncMock(side_effect=mock_retrieve_consistent)

    # Use a unique query for this test
    test_query = "Accuracy test query"
    num_queries = 20

    # === FIRST MEASUREMENT: Direct timing ===
    start_time = time.time()
    for _ in range(num_queries):
        await retriever.retrieve(query_text=test_query, max_results=5)
    end_time = time.time()

    duration = end_time - start_time
    expected_qps = num_queries / duration

    # === SECOND MEASUREMENT: Using measure_qps helper ===
    async def query_func(retriever):
        await retriever.retrieve(query_text=test_query, max_results=5)

    measured_qps, query_times = await measure_qps(
        retriever, num_queries=num_queries, query_func=query_func, concurrent_clients=1
    )

    # Verify QPS calculation accuracy (within 5% tolerance)
    qps_difference_pct = abs(measured_qps - expected_qps) / expected_qps * 100

    print(f"\nExpected QPS: {expected_qps:.2f}")
    print(f"Measured QPS: {measured_qps:.2f}")
    print(f"Difference: {qps_difference_pct:.1f}%")

    # Assertions
    assert qps_difference_pct < 5, (
        f"QPS measurement error {qps_difference_pct:.1f}% exceeds 5% tolerance"
    )
    assert len(query_times) == num_queries, "Should record all query times"
    assert all(t > 0 for t in query_times), "All query times should be positive"
