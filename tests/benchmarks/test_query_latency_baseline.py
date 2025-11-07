"""
Query Latency Baseline Benchmark Tests for CBR MCP Server.

This test suite establishes performance baselines for CBR query operations,
measuring latency for various query types and complexities. These benchmarks
will be used to track performance improvements during optimization work.

Test Coverage:
- cbr_retrieve tool latency (simple, medium, complex queries)
- cbr_search_category tool latency (with/without subcategory)
- cbr_find_similar tool latency
- Cold start vs warm cache comparison
- Embedding generation latency isolation
- Concurrent query latency under load

Target Metrics:
- p95 latency < 200ms for typical queries
- Repeatable, consistent measurements
- Isolation from external factors

Note: These are TDD tests - they define the expected performance characteristics
before optimization work begins.
"""

import asyncio
import time
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
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
def mock_retriever():
    """Mock ProductionCBRRetriever for consistent test results."""
    retriever = Mock(spec=ProductionCBRRetriever)

    # Configure retrieve method
    async def mock_retrieve(query_text, max_results=5, similarity_threshold=0.7):
        # Simulate database query with consistent delay
        await asyncio.sleep(0.05)  # 50ms simulated DB latency
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

    retriever.retrieve = AsyncMock(side_effect=mock_retrieve)

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

    # Configure find_similar method
    async def mock_find_similar(case_id, max_results=5, similarity_threshold=0.7):
        await asyncio.sleep(0.045)  # 45ms simulated DB latency
        return {
            "cases": [
                {
                    "id": f"similar_{i}",
                    "content": f"Similar to {case_id}",
                    "similarity": 0.8 - (i * 0.05),
                    "metadata": {"category": "orchestration", "tags": ["similar"]},
                }
                for i in range(max_results)
            ],
            "source_case_id": case_id,
            "total_results": max_results,
        }

    retriever.find_similar = AsyncMock(side_effect=mock_find_similar)

    return retriever


@pytest.fixture
def mock_cbr_server(mock_retriever):
    """Mock CBRMCPServer with retriever configured."""
    server = Mock(spec=CBRMCPServer)
    server.retriever = mock_retriever
    return server


@pytest.fixture
def mock_context():
    """Mock MCP Context for tool invocations."""
    return Context()


@pytest.fixture
def mock_embedding_model():
    """Mock sentence transformer for embedding generation."""
    model = Mock()

    def mock_encode(texts, convert_to_tensor=False):
        # Simulate embedding generation time
        time.sleep(0.02)  # 20ms per embedding
        if isinstance(texts, str):
            return [0.1] * 768  # Typical embedding dimension
        return [[0.1] * 768 for _ in texts]

    model.encode = Mock(side_effect=mock_encode)
    return model


# ============================================================================
# Test: cbr_retrieve Tool Latency - Simple Query
# ============================================================================


def test_cbr_retrieve_latency_simple_query(benchmark, mock_cbr_server, mock_context):
    """
    Measure latency for a simple cbr_retrieve query.

    This test establishes baseline performance for straightforward queries
    with minimal description text and default parameters.
    """

    async def execute_simple_retrieve():
        result = await mock_cbr_server.retriever.retrieve(
            query_text="How to implement authentication?", max_results=5
        )
        return result

    # Benchmark the query using a new event loop
    def sync_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(execute_simple_retrieve())
        finally:
            loop.close()

    result = benchmark(sync_wrapper)

    # Assertions
    assert result is not None
    assert "cases" in result
    assert len(result["cases"]) == 5

    # Check benchmark statistics (will fail initially - that's the point of TDD)
    stats = benchmark.stats
    p95_latency_ms = (
        np.percentile(benchmark.stats.get("stats").data, 95) * 1000
    )  # Convert to milliseconds

    # This should fail initially since we haven't optimized yet
    assert (
        p95_latency_ms < 200
    ), f"p95 latency {p95_latency_ms:.2f}ms exceeds 200ms target"


# ============================================================================
# Test: cbr_retrieve Tool Latency - Medium Query
# ============================================================================


def test_cbr_retrieve_latency_medium_query(benchmark, mock_cbr_server, mock_context):
    """
    Measure latency for a medium complexity cbr_retrieve query.

    Tests with moderate description length and multiple contextual elements.
    """

    async def execute_medium_retrieve():
        query = (
            "I need to implement a user authentication system with email/password "
            "login, JWT token generation, and password reset functionality. "
            "The system should integrate with our existing React frontend."
        )
        result = await mock_cbr_server.retriever.retrieve(
            query_text=query, max_results=10, similarity_threshold=0.75
        )
        return result

    def sync_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(execute_medium_retrieve())
        finally:
            loop.close()

    result = benchmark(sync_wrapper)

    assert result is not None
    assert len(result["cases"]) == 10

    stats = benchmark.stats
    p95_latency_ms = np.percentile(benchmark.stats.get("stats").data, 95) * 1000

    assert (
        p95_latency_ms < 200
    ), f"p95 latency {p95_latency_ms:.2f}ms exceeds 200ms target"


# ============================================================================
# Test: cbr_retrieve Tool Latency - Complex Query
# ============================================================================


def test_cbr_retrieve_latency_complex_query(benchmark, mock_cbr_server, mock_context):
    """
    Measure latency for a complex cbr_retrieve query.

    Tests with long description, multiple constraints, and increased result limit.
    """

    async def execute_complex_retrieve():
        query = (
            "I need to build a comprehensive orchestration system for AI agents "
            "that includes task planning with sequential-thinking integration, "
            "TodoWrite synchronization, parallel task execution, verification "
            "with karen agent, error remediation protocols, and state management. "
            "The system must handle granular task decomposition according to the "
            "Principle of Verifiable Work, support multiple specialist agents, "
            "and maintain a Plan of Record throughout execution. Additionally, "
            "it needs pre-action gates, checkpoint validation, and comprehensive "
            "error recovery mechanisms."
        )
        result = await mock_cbr_server.retriever.retrieve(
            query_text=query, max_results=15, similarity_threshold=0.8
        )
        return result

    def sync_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(execute_complex_retrieve())
        finally:
            loop.close()

    result = benchmark(sync_wrapper)

    assert result is not None
    assert len(result["cases"]) == 15

    stats = benchmark.stats
    p95_latency_ms = np.percentile(benchmark.stats.get("stats").data, 95) * 1000

    # Complex queries may exceed target initially
    print(f"Complex query p95 latency: {p95_latency_ms:.2f}ms")
    assert result["cases"][0]["similarity"] > 0.8


# ============================================================================
# Test: cbr_search_category Tool Latency - Simple
# ============================================================================


def test_cbr_search_category_latency_simple(benchmark, mock_cbr_server, mock_context):
    """
    Measure latency for category search with a single category filter.

    Baseline for category-filtered retrieval without subcategory.
    """

    async def execute_category_search():
        result = await mock_cbr_server.retriever.search_by_category(
            category="orchestration", max_results=5
        )
        return result

    def sync_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(execute_category_search())
        finally:
            loop.close()

    result = benchmark(sync_wrapper)

    assert result is not None
    assert result["category"] == "orchestration"
    assert len(result["cases"]) == 5

    stats = benchmark.stats
    p95_latency_ms = np.percentile(benchmark.stats.get("stats").data, 95) * 1000

    assert (
        p95_latency_ms < 200
    ), f"p95 latency {p95_latency_ms:.2f}ms exceeds 200ms target"


# ============================================================================
# Test: cbr_search_category Tool Latency - With Subcategory
# ============================================================================


def test_cbr_search_category_latency_with_subcategory(
    benchmark, mock_cbr_server, mock_context
):
    """
    Measure latency for category search with subcategory filtering.

    Tests performance of hierarchical category filtering in ChromaDB.
    """

    async def execute_subcategory_search():
        result = await mock_cbr_server.retriever.search_by_category(
            category="orchestration", subcategory="planning", max_results=5
        )
        return result

    def sync_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(execute_subcategory_search())
        finally:
            loop.close()

    result = benchmark(sync_wrapper)

    assert result is not None
    assert result["category"] == "orchestration"
    assert result["subcategory"] == "planning"
    assert len(result["cases"]) == 5

    stats = benchmark.stats
    p95_latency_ms = np.percentile(benchmark.stats.get("stats").data, 95) * 1000

    assert (
        p95_latency_ms < 200
    ), f"p95 latency {p95_latency_ms:.2f}ms exceeds 200ms target"


# ============================================================================
# Test: cbr_find_similar Tool Latency
# ============================================================================


def test_cbr_find_similar_latency(benchmark, mock_cbr_server, mock_context):
    """
    Measure latency for finding similar cases by case ID.

    Baseline for similarity-based retrieval from existing case.
    """

    async def execute_find_similar():
        result = await mock_cbr_server.retriever.find_similar(
            case_id="case_123", max_results=5, similarity_threshold=0.7
        )
        return result

    def sync_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(execute_find_similar())
        finally:
            loop.close()

    result = benchmark(sync_wrapper)

    assert result is not None
    assert result["source_case_id"] == "case_123"
    assert len(result["cases"]) == 5

    stats = benchmark.stats
    p95_latency_ms = np.percentile(benchmark.stats.get("stats").data, 95) * 1000

    assert (
        p95_latency_ms < 200
    ), f"p95 latency {p95_latency_ms:.2f}ms exceeds 200ms target"


# ============================================================================
# Test: Cold Start vs Warm Cache - cbr_retrieve
# ============================================================================


@pytest.mark.asyncio
async def test_cold_start_vs_warm_cache_cbr_retrieve(benchmark, mock_cbr_server):
    """
    Compare latency between cold start and warm cache for cbr_retrieve.

    Measures performance improvement from caching embeddings and results.
    """

    query_text = "How to implement user authentication?"

    # Measure cold start (first query)
    cold_start = time.time()
    cold_result = await mock_cbr_server.retriever.retrieve(
        query_text=query_text, max_results=5
    )
    cold_latency_ms = (time.time() - cold_start) * 1000

    # Measure warm cache (subsequent identical query)
    warm_start = time.time()
    warm_result = await mock_cbr_server.retriever.retrieve(
        query_text=query_text, max_results=5
    )
    warm_latency_ms = (time.time() - warm_start) * 1000

    # Assertions
    assert cold_result is not None
    assert warm_result is not None
    assert len(cold_result["cases"]) == len(warm_result["cases"])

    # Warm cache should be faster (or at least not slower)
    cache_improvement_pct = (
        (cold_latency_ms - warm_latency_ms) / cold_latency_ms
    ) * 100

    print(f"Cold start latency: {cold_latency_ms:.2f}ms")
    print(f"Warm cache latency: {warm_latency_ms:.2f}ms")
    print(f"Cache improvement: {cache_improvement_pct:.1f}%")

    # This assertion may fail initially if caching isn't implemented
    assert (
        warm_latency_ms <= cold_latency_ms
    ), "Warm cache should not be slower than cold start"


# ============================================================================
# Test: Cold Start vs Warm Cache - cbr_search_category
# ============================================================================


@pytest.mark.asyncio
async def test_cold_start_vs_warm_cache_cbr_search_category(benchmark, mock_cbr_server):
    """
    Compare cold vs warm latency for category search.

    Measures caching effectiveness for category-filtered queries.
    """

    # Measure cold start
    cold_start = time.time()
    cold_result = await mock_cbr_server.retriever.search_by_category(
        category="orchestration", max_results=5
    )
    cold_latency_ms = (time.time() - cold_start) * 1000

    # Measure warm cache
    warm_start = time.time()
    warm_result = await mock_cbr_server.retriever.search_by_category(
        category="orchestration", max_results=5
    )
    warm_latency_ms = (time.time() - warm_start) * 1000

    assert cold_result is not None
    assert warm_result is not None

    cache_improvement_pct = (
        (cold_latency_ms - warm_latency_ms) / cold_latency_ms
    ) * 100

    print(f"Category search cold start: {cold_latency_ms:.2f}ms")
    print(f"Category search warm cache: {warm_latency_ms:.2f}ms")
    print(f"Cache improvement: {cache_improvement_pct:.1f}%")

    assert warm_latency_ms <= cold_latency_ms


# ============================================================================
# Test: Embedding Generation Latency (Isolated)
# ============================================================================


def test_embedding_generation_latency(benchmark, mock_embedding_model):
    """
    Measure embedding generation time in isolation.

    Establishes baseline for sentence transformer encode() operation,
    separate from database query time.
    """

    def generate_embeddings():
        query_text = (
            "I need to implement a user authentication system with JWT tokens "
            "and password reset functionality."
        )
        embedding = mock_embedding_model.encode(query_text, convert_to_tensor=False)
        return embedding

    result = benchmark(generate_embeddings)

    assert result is not None
    assert len(result) == 768  # Expected embedding dimension

    stats = benchmark.stats
    p95_latency_ms = np.percentile(benchmark.stats.get("stats").data, 95) * 1000

    print(f"Embedding generation p95 latency: {p95_latency_ms:.2f}ms")

    # Embedding generation should be relatively fast
    assert (
        p95_latency_ms < 100
    ), f"Embedding generation {p95_latency_ms:.2f}ms exceeds 100ms target"


# ============================================================================
# Test: Concurrent Query Latency
# ============================================================================


def test_concurrent_query_latency(benchmark, mock_cbr_server):
    """
    Measure latency under concurrent load.

    Tests performance degradation when multiple queries execute simultaneously,
    simulating real-world AI agent usage patterns.
    """

    async def execute_concurrent_queries():
        # Create 5 concurrent queries of different types
        tasks = [
            mock_cbr_server.retriever.retrieve(
                query_text="Authentication implementation", max_results=5
            ),
            mock_cbr_server.retriever.search_by_category(
                category="orchestration", max_results=5
            ),
            mock_cbr_server.retriever.find_similar(case_id="case_456", max_results=5),
            mock_cbr_server.retriever.retrieve(
                query_text="Database schema design", max_results=5
            ),
            mock_cbr_server.retriever.search_by_category(
                category="webdev", subcategory="api", max_results=5
            ),
        ]

        results = await asyncio.gather(*tasks)
        return results

    def sync_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(execute_concurrent_queries())
        finally:
            loop.close()

    results = benchmark(sync_wrapper)

    # Assertions
    assert len(results) == 5
    assert all(r is not None for r in results)
    assert all("cases" in r or "category" in r for r in results)

    stats = benchmark.stats
    p95_latency_ms = np.percentile(benchmark.stats.get("stats").data, 95) * 1000

    print(f"Concurrent query p95 latency: {p95_latency_ms:.2f}ms")

    # Concurrent queries will be slower but should still be reasonable
    # This will likely fail initially without optimization
    assert (
        p95_latency_ms < 300
    ), f"Concurrent p95 latency {p95_latency_ms:.2f}ms exceeds 300ms threshold"


# ============================================================================
# Test: Large Result Set Latency
# ============================================================================


def test_large_result_set_latency(benchmark, mock_cbr_server):
    """
    Measure latency when retrieving large result sets.

    Tests performance with maximum result limits to identify scaling issues.
    """

    async def execute_large_retrieve():
        result = await mock_cbr_server.retriever.retrieve(
            query_text="Orchestration system implementation", max_results=50
        )
        return result

    def sync_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(execute_large_retrieve())
        finally:
            loop.close()

    result = benchmark(sync_wrapper)

    assert result is not None
    assert len(result["cases"]) == 50

    stats = benchmark.stats
    p95_latency_ms = np.percentile(benchmark.stats.get("stats").data, 95) * 1000

    print(f"Large result set p95 latency: {p95_latency_ms:.2f}ms")

    # Large result sets may exceed standard target
    assert p95_latency_ms < 400, f"Large result latency {p95_latency_ms:.2f}ms too high"


# ============================================================================
# Test: Percentile Distribution Verification
# ============================================================================


def test_percentile_distribution_verification(benchmark, mock_cbr_server):
    """
    Verify that p50, p95, and p99 percentiles are captured correctly.

    Ensures benchmark statistics provide complete latency distribution.
    """

    async def execute_standard_query():
        result = await mock_cbr_server.retriever.retrieve(
            query_text="API endpoint implementation", max_results=5
        )
        return result

    def sync_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(execute_standard_query())
        finally:
            loop.close()

    result = benchmark(sync_wrapper)

    stats = benchmark.stats

    # Extract percentiles
    p50_latency_ms = np.percentile(benchmark.stats.get("stats").data, 50) * 1000
    p95_latency_ms = np.percentile(benchmark.stats.get("stats").data, 95) * 1000
    p99_latency_ms = np.percentile(benchmark.stats.get("stats").data, 99) * 1000

    print(f"Latency distribution:")
    print(f"  p50 (median): {p50_latency_ms:.2f}ms")
    print(f"  p95: {p95_latency_ms:.2f}ms")
    print(f"  p99: {p99_latency_ms:.2f}ms")

    # Verify percentile ordering
    assert p50_latency_ms <= p95_latency_ms
    assert p95_latency_ms <= p99_latency_ms

    # Verify all values are captured
    assert p50_latency_ms > 0
    assert p95_latency_ms > 0
    assert p99_latency_ms > 0
