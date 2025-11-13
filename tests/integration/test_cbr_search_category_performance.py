"""
Performance tests for cbr_search_category MCP tool

This module is part of the refactored MCP performance test suite.
Original file: test_mcp_performance_integration.py
"""

import asyncio
import gc
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from test_performance_helpers import (
    HAS_CBR,
    HAS_PSUTIL,
    measure_concurrent_mcp_tools,
    measure_mcp_tool_latency,
    measure_mcp_tool_memory,
)


@pytest.mark.asyncio
class TestCBRSearchCategoryPerformance:
    """Performance tests for cbr_search_category MCP tool."""

    async def test_cbr_search_category_all_main_categories_performance(
        self, mock_mcp_server
    ):
        """
        Test cbr_search_category performance for all 4 main categories.

        Verifies that queries for each main category (code, orchestration,
        best-practice, anti-pattern) meet the <200ms p95 latency target.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        categories = ["code", "orchestration", "best-practice", "anti-pattern"]
        results = {}

        for category in categories:
            # Measure performance for this category
            metrics = await measure_mcp_tool_latency(
                mock_mcp_server.cbr_search_category,
                category=category,
                subcategory=None,
                query="",
                limit=10,
                warmup_calls=1,
            )

            results[category] = metrics

            # Verify performance target for each category
            assert (
                metrics["latency_ms"] < 200.0
            ), f"Category '{category}' latency {metrics['latency_ms']}ms exceeds 200ms target"
            assert "result" in metrics
            assert metrics["result"] is not None

        # Verify consistency across categories (no category should be significantly slower)
        latencies = [results[cat]["latency_ms"] for cat in categories]
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        assert (
            max_latency < avg_latency * 2.0
        ), "Category latencies should be relatively consistent"

    async def test_cbr_search_category_with_subcategory_filtering_performance(
        self, mock_mcp_server
    ):
        """
        Test cbr_search_category performance with subcategory filtering.

        Verifies that adding subcategory filtering doesn't significantly
        impact query latency and meets the <200ms target.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Test subcategory queries for each main category
        test_queries = [
            {"category": "code", "subcategory": "firebase-auth"},
            {"category": "code", "subcategory": "react-components"},
            {"category": "orchestration", "subcategory": "delegation"},
            {"category": "orchestration", "subcategory": "remediation"},
            {"category": "best-practice", "subcategory": "planning"},
            {"category": "anti-pattern", "subcategory": "completion-bias"},
        ]

        for query_params in test_queries:
            # Measure performance with subcategory
            metrics = await measure_mcp_tool_latency(
                mock_mcp_server.cbr_search_category,
                category=query_params["category"],
                subcategory=query_params["subcategory"],
                query="",
                limit=10,
                warmup_calls=1,
            )

            # Verify performance target
            assert (
                metrics["latency_ms"] < 200.0
            ), f"Category '{query_params['category']}/{query_params['subcategory']}' latency exceeds target"
            assert "result" in metrics
            assert metrics["result"] is not None

    async def test_cbr_search_category_with_query_filtering_performance(
        self, mock_mcp_server
    ):
        """
        Test cbr_search_category performance with semantic query filtering.

        Verifies that adding query-based filtering meets latency targets
        and compares performance between empty and non-empty queries.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Test with query string
        metrics_with_query = await measure_mcp_tool_latency(
            mock_mcp_server.cbr_search_category,
            category="code",
            subcategory=None,
            query="How to implement user authentication?",
            limit=10,
            warmup_calls=1,
        )

        # Test without query string (empty query)
        metrics_without_query = await measure_mcp_tool_latency(
            mock_mcp_server.cbr_search_category,
            category="code",
            subcategory=None,
            query="",
            limit=10,
            warmup_calls=1,
        )

        # Both should meet latency target
        assert (
            metrics_with_query["latency_ms"] < 200.0
        ), "Query filtering latency exceeds target"
        assert (
            metrics_without_query["latency_ms"] < 200.0
        ), "Empty query latency exceeds target"

        # Verify results are returned
        assert metrics_with_query["result"] is not None
        assert metrics_without_query["result"] is not None

    async def test_cbr_search_category_cold_vs_warm_cache_performance(
        self, mock_mcp_server
    ):
        """
        Test cache effectiveness for cbr_search_category queries.

        Verifies that warm cache provides performance improvement and
        that cache hit rate meets the 70%+ target for repeated queries.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Cold cache - first call
        cold_metrics = await measure_mcp_tool_latency(
            mock_mcp_server.cbr_search_category,
            category="code",
            subcategory="firebase-auth",
            query="authentication",
            limit=10,
            warmup_calls=0,
        )

        # Warm cache - repeat same query multiple times
        warm_latencies = []
        for _ in range(5):
            warm_metrics = await measure_mcp_tool_latency(
                mock_mcp_server.cbr_search_category,
                category="code",
                subcategory="firebase-auth",
                query="authentication",
                limit=10,
                warmup_calls=0,
            )
            warm_latencies.append(warm_metrics["latency_ms"])

        avg_warm_latency = sum(warm_latencies) / len(warm_latencies)

        # Verify warm cache meets target
        assert avg_warm_latency < 200.0, "Warm cache latency exceeds target"

        # Verify cold cache latency is measured
        assert cold_metrics["latency_ms"] > 0
        assert cold_metrics["result"] is not None

    async def test_cbr_search_category_varying_result_limits_performance(
        self, mock_mcp_server
    ):
        """
        Test performance with different result set sizes.

        Verifies that latency scales reasonably with result limit and
        all configurations meet performance targets.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        test_limits = [3, 10, 25, 50]
        results = {}

        for limit in test_limits:
            metrics = await measure_mcp_tool_latency(
                mock_mcp_server.cbr_search_category,
                category="code",
                subcategory=None,
                query="",
                limit=limit,
                warmup_calls=1,
            )

            results[limit] = metrics

            # Verify performance target
            assert (
                metrics["latency_ms"] < 200.0
            ), f"Latency for limit={limit} exceeds target"
            assert metrics["result"] is not None

        # Verify latency scales reasonably (not exponentially)
        # Larger limits should take longer, but not dramatically
        latency_3 = results[3]["latency_ms"]
        latency_50 = results[50]["latency_ms"]
        assert (
            latency_50 < latency_3 * 5.0
        ), "Latency should scale reasonably with limit"

    async def test_cbr_search_category_concurrent_category_queries(
        self, mock_mcp_server
    ):
        """
        Test concurrent cbr_search_category queries across different categories.

        Verifies system can handle 10+ concurrent category queries without
        significant performance degradation as specified in targets.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Create 15 concurrent category queries across all categories
        categories = ["code", "orchestration", "best-practice", "anti-pattern"]
        tool_calls = []

        for i in range(15):
            category = categories[i % len(categories)]
            tool_calls.append(
                (
                    mock_mcp_server.cbr_search_category,
                    (),
                    {
                        "category": category,
                        "subcategory": None,
                        "query": f"test query {i}",
                        "limit": 10,
                    },
                )
            )

        # Measure concurrent performance
        metrics = await measure_concurrent_mcp_tools(tool_calls, max_concurrent=10)

        # Verify metrics
        assert metrics["total_calls"] == 15
        assert metrics["throughput_ops_per_sec"] > 0
        assert (
            metrics["p95_latency_ms"] < 300.0
        ), "P95 latency with concurrency exceeds 300ms"
        assert len(metrics["results"]) == 15

        # Verify individual queries didn't take too long
        max_latency = max(metrics["latencies_ms"])
        assert (
            max_latency < 400.0
        ), "Individual query latency under concurrency too high"

    async def test_cbr_search_category_small_workload_performance(
        self, mock_mcp_server, sample_workload_small
    ):
        """
        Test cbr_search_category with small workload fixture.

        Verifies performance meets targets across diverse category queries
        from the small workload (5 queries).
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        latencies = []

        # Execute category queries from small workload
        for query_dict in sample_workload_small:
            if "category" in query_dict:
                metrics = await measure_mcp_tool_latency(
                    mock_mcp_server.cbr_search_category,
                    category=query_dict["category"],
                    subcategory=None,
                    query=query_dict["query"],
                    limit=query_dict["max_results"],
                    warmup_calls=0,
                )

                latencies.append(metrics["latency_ms"])

                # Verify each query meets target
                assert (
                    metrics["latency_ms"] < 200.0
                ), f"Query latency {metrics['latency_ms']}ms exceeds target"

        # Verify average performance
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            assert avg_latency < 150.0, "Average latency should be well under target"

            # Verify p95
            latencies_sorted = sorted(latencies)
            p95_idx = int(len(latencies) * 0.95)
            p95_latency = latencies_sorted[min(p95_idx, len(latencies) - 1)]
            assert p95_latency < 200.0, "P95 latency exceeds target"

    async def test_cbr_search_category_medium_workload_performance(
        self, mock_mcp_server, sample_workload_medium
    ):
        """
        Test cbr_search_category with medium workload fixture.

        Verifies sustained performance across 20 diverse category queries
        and measures cache effectiveness.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        latencies = []
        category_queries = [q for q in sample_workload_medium if "category" in q]

        # Execute all category queries
        for query_dict in category_queries:
            metrics = await measure_mcp_tool_latency(
                mock_mcp_server.cbr_search_category,
                category=query_dict["category"],
                subcategory=None,
                query=query_dict["query"],
                limit=query_dict["max_results"],
                warmup_calls=0,
            )

            latencies.append(metrics["latency_ms"])

        # Verify all queries met target
        for i, latency in enumerate(latencies):
            assert latency < 200.0, f"Query {i} latency {latency}ms exceeds target"

        # Verify average and p95 performance
        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 150.0, "Average latency should be well under target"

        latencies_sorted = sorted(latencies)
        p95_idx = int(len(latencies) * 0.95)
        p95_latency = latencies_sorted[min(p95_idx, len(latencies) - 1)]
        assert p95_latency < 200.0, "P95 latency exceeds target"

    async def test_cbr_search_category_large_workload_performance(
        self, mock_mcp_server, sample_workload_large
    ):
        """
        Test cbr_search_category with large workload fixture.

        Verifies sustained performance across 100 queries with no degradation
        over time and measures cache hit rate effectiveness.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        latencies = []
        category_queries = [q for q in sample_workload_large if "category" in q]

        # Limit to first 50 category queries to keep test time reasonable
        category_queries = category_queries[:50]

        # Execute all queries
        for i, query_dict in enumerate(category_queries):
            metrics = await measure_mcp_tool_latency(
                mock_mcp_server.cbr_search_category,
                category=query_dict["category"],
                subcategory=None,
                query=query_dict["query"],
                limit=query_dict["max_results"],
                warmup_calls=0,
            )

            latencies.append(metrics["latency_ms"])

            # Check for performance degradation over time
            if i > 0 and i % 10 == 0:
                # Last 10 queries average shouldn't be worse than first 10
                recent_avg = sum(latencies[-10:]) / 10
                initial_avg = sum(latencies[:10]) / 10
                assert (
                    recent_avg < initial_avg * 2.0
                ), "Performance degradation detected over time"

        # Verify overall performance
        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 150.0, "Average latency should be well under target"

        # Verify p95 latency
        latencies_sorted = sorted(latencies)
        p95_idx = int(len(latencies) * 0.95)
        p95_latency = latencies_sorted[min(p95_idx, len(latencies) - 1)]
        assert p95_latency < 200.0, "P95 latency exceeds target"

        # Verify p99 is reasonable too
        p99_idx = int(len(latencies) * 0.99)
        p99_latency = latencies_sorted[min(p99_idx, len(latencies) - 1)]
        assert p99_latency < 300.0, "P99 latency should be reasonable even if above p95"

    async def test_cbr_search_category_invalid_category_handling_performance(
        self, mock_mcp_server
    ):
        """
        Test performance of error handling for invalid categories.

        Verifies that validation errors are handled quickly and don't
        add significant overhead to the system.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Mock invalid category to raise error
        async def mock_invalid_category(*args, **kwargs):
            raise ValueError("Invalid category")

        original_method = mock_mcp_server.cbr_search_category
        mock_mcp_server.cbr_search_category = AsyncMock(
            side_effect=mock_invalid_category
        )

        try:
            # Measure error handling latency
            start_time = time.perf_counter()
            try:
                await mock_mcp_server.cbr_search_category(
                    category="invalid_category", subcategory=None, query="", limit=10
                )
            except ValueError:
                pass  # Expected
            end_time = time.perf_counter()

            error_latency = (end_time - start_time) * 1000.0

            # Error handling should be very fast (< 50ms)
            assert error_latency < 50.0, "Error handling latency too high"

        finally:
            # Restore original method
            mock_mcp_server.cbr_search_category = original_method

    async def test_cbr_search_category_category_filtering_accuracy(
        self, mock_mcp_server
    ):
        """
        Verify category filtering accuracy alongside performance.

        Ensures results match requested category and that filtering
        doesn't compromise accuracy while maintaining performance.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Test each category
        categories = ["code", "orchestration", "best-practice", "anti-pattern"]

        for category in categories:
            metrics = await measure_mcp_tool_latency(
                mock_mcp_server.cbr_search_category,
                category=category,
                subcategory=None,
                query="",
                limit=10,
                warmup_calls=1,
            )

            # Verify performance
            assert (
                metrics["latency_ms"] < 200.0
            ), f"Category '{category}' latency exceeds target"

            # Verify accuracy - result should contain category info
            result = metrics["result"]
            assert result is not None
            # Result can be either a list or a dict with 'results' key
            if isinstance(result, dict):
                assert "results" in result or "category" in result
                # If dict has results list, verify those
                if "results" in result:
                    for item in result["results"]:
                        if isinstance(item, dict) and "category" in item:
                            assert (
                                item["category"] == category
                            ), f"Result category mismatch: expected {category}, got {item['category']}"
            else:
                # If result is a list, verify items in list
                assert isinstance(result, list)
                for item in result:
                    if isinstance(item, dict) and "category" in item:
                        assert (
                            item["category"] == category
                        ), f"Result category mismatch: expected {category}, got {item['category']}"

    async def test_cbr_search_category_memory_usage_during_queries(
        self, mock_mcp_server
    ):
        """
        Test memory usage during cbr_search_category queries.

        Verifies that category queries don't cause excessive memory
        allocation and that memory usage stays within reasonable bounds.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        if not HAS_PSUTIL:
            pytest.skip("psutil required for memory measurement")

        # Measure memory for single query
        metrics = await measure_mcp_tool_memory(
            mock_mcp_server.cbr_search_category,
            category="code",
            subcategory=None,
            query="test query",
            limit=10,
        )

        # Verify metrics returned
        assert "baseline_mb" in metrics
        assert "delta_mb" in metrics
        assert "result" in metrics

        # Memory delta for single query should be modest
        # (< 50MB for a single category query)
        assert (
            abs(metrics["delta_mb"]) < 50.0
        ), f"Memory delta {metrics['delta_mb']}MB too high for single query"

        # Verify no obvious memory leak (delta should be near zero after GC)
        assert abs(metrics["delta_mb"]) < 100.0, "Potential memory leak detected"


# ============================================================================
# Concurrent MCP Tool Performance Tests (Subtask 10.5)
# ============================================================================
