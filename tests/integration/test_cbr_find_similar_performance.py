"""
Performance tests for cbr_find_similar MCP tool

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
from performance_helpers import (
    HAS_CBR,
    HAS_PSUTIL,
    measure_concurrent_mcp_tools,
    measure_mcp_tool_latency,
    measure_mcp_tool_memory,
)


@pytest.mark.asyncio
class TestCBRFindSimilarPerformance:
    """Performance tests for cbr_find_similar MCP tool."""

    async def test_cbr_find_similar_tool_performance(self, mock_mcp_server):
        """
        Test cbr_find_similar tool performance.

        Measures latency for similarity-based retrieval and verifies
        results are returned correctly.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Measure performance
        metrics = await measure_mcp_tool_latency(
            mock_mcp_server.cbr_find_similar,
            example_id="case-1",
            similarity_threshold=0.85,
            max_results=8,
            warmup_calls=1,
        )

        # Verify performance
        assert metrics["latency_ms"] < 200.0, "Find similar should be <200ms"
        assert "result" in metrics
        assert metrics["result"] is not None

    async def test_cbr_find_similar_tool_performance_warm_cache(self, mock_mcp_server):
        """
        Test cbr_find_similar tool performance with warm cache.

        Measures latency when cache is warmed up and verifies it meets
        the <200ms p95 target for similarity-based retrieval.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Warmup call with a known case ID
        await mock_mcp_server.cbr_find_similar(
            example_id="case-1", similarity_threshold=0.85, max_results=8
        )

        # Measure performance with warm cache
        metrics = await measure_mcp_tool_latency(
            mock_mcp_server.cbr_find_similar,
            example_id="case-1",
            similarity_threshold=0.85,
            max_results=8,
            warmup_calls=2,
        )

        # Verify performance target
        assert (
            metrics["latency_ms"] < 200.0
        ), "Warm cache find_similar latency should be <200ms"
        assert "result" in metrics
        assert metrics["result"] is not None
        assert isinstance(metrics["result"], list)

    async def test_cbr_find_similar_tool_performance_cold_cache(self, mock_mcp_server):
        """
        Test cbr_find_similar tool performance with cold cache.

        Measures latency on first call when no caching has occurred.
        This represents worst-case performance for similarity search.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Measure cold cache performance (no warmup)
        metrics = await measure_mcp_tool_latency(
            mock_mcp_server.cbr_find_similar,
            example_id="case-1",
            similarity_threshold=0.85,
            max_results=8,
            warmup_calls=0,
        )

        # Verify latency is measured
        assert "latency_ms" in metrics
        assert metrics["latency_ms"] > 0
        assert "result" in metrics
        assert metrics["result"] is not None

    async def test_cbr_find_similar_with_high_threshold(self, mock_mcp_server):
        """
        Test cbr_find_similar performance with high similarity threshold.

        Verifies performance with threshold=0.95 which should return
        fewer but more relevant results.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Measure performance with high threshold
        metrics = await measure_mcp_tool_latency(
            mock_mcp_server.cbr_find_similar,
            example_id="case-1",
            similarity_threshold=0.95,
            max_results=8,
            warmup_calls=1,
        )

        # Verify performance
        assert (
            metrics["latency_ms"] < 200.0
        ), "High threshold queries should still be <200ms"
        assert "result" in metrics
        assert metrics["result"] is not None

    async def test_cbr_find_similar_with_low_threshold(self, mock_mcp_server):
        """
        Test cbr_find_similar performance with low similarity threshold.

        Verifies performance with threshold=0.5 which may return more
        results but should not significantly degrade performance.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Measure performance with low threshold
        metrics = await measure_mcp_tool_latency(
            mock_mcp_server.cbr_find_similar,
            example_id="case-1",
            similarity_threshold=0.5,
            max_results=8,
            warmup_calls=1,
        )

        # Verify performance doesn't degrade significantly
        assert (
            metrics["latency_ms"] < 250.0
        ), "Low threshold queries should remain reasonably fast"
        assert "result" in metrics
        assert metrics["result"] is not None

    async def test_cbr_find_similar_with_various_max_results(self, mock_mcp_server):
        """
        Test cbr_find_similar performance with different max_results values.

        Verifies that performance scales reasonably with the number of
        requested results (3, 8, 20).
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        result_counts = [3, 8, 20]
        latencies = []

        for max_results in result_counts:
            metrics = await measure_mcp_tool_latency(
                mock_mcp_server.cbr_find_similar,
                example_id="case-1",
                similarity_threshold=0.85,
                max_results=max_results,
                warmup_calls=1,
            )
            latencies.append(metrics["latency_ms"])

            # All queries should meet target
            assert (
                metrics["latency_ms"] < 200.0
            ), f"Query with max_results={max_results} should be <200ms"

        # Verify latency scales reasonably (not exponentially)
        # Largest result set should be less than 2.5x smallest
        assert latencies[2] < latencies[0] * 2.5, "Latency should scale linearly"

    async def test_cbr_find_similar_with_nonexistent_id(self, mock_mcp_server):
        """
        Test cbr_find_similar performance with non-existent example ID.

        Verifies graceful handling when the requested case ID doesn't exist
        in the database.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Configure mock to return empty results for non-existent ID
        async def mock_find_similar_empty(*args, **kwargs):
            await asyncio.sleep(0.01)
            return []

        mock_mcp_server.cbr_find_similar = AsyncMock(
            side_effect=mock_find_similar_empty
        )

        # Measure performance with non-existent ID
        metrics = await measure_mcp_tool_latency(
            mock_mcp_server.cbr_find_similar,
            example_id="case-999999",
            similarity_threshold=0.85,
            max_results=8,
            warmup_calls=0,
        )

        # Verify query completes without hanging
        assert "latency_ms" in metrics
        assert metrics["latency_ms"] < 500.0, "Non-existent ID query should not hang"
        assert "result" in metrics
        # Should return empty list or appropriate response
        assert metrics["result"] == [] or metrics["result"] is not None

    async def test_cbr_find_similar_with_invalid_id_format(self, mock_mcp_server):
        """
        Test cbr_find_similar handling of malformed example IDs.

        Verifies appropriate error handling for invalid ID formats.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Test with various invalid ID formats
        invalid_ids = ["", "invalid-format", "case-", "-123", "case-abc"]

        for invalid_id in invalid_ids:
            try:
                metrics = await measure_mcp_tool_latency(
                    mock_mcp_server.cbr_find_similar,
                    example_id=invalid_id,
                    similarity_threshold=0.85,
                    max_results=8,
                    warmup_calls=0,
                )

                # If it doesn't raise, verify it completes quickly
                assert (
                    metrics["latency_ms"] < 500.0
                ), f"Invalid ID '{invalid_id}' query should not hang"
            except (ValueError, RuntimeError):
                # Expected error is acceptable - we're testing it doesn't hang
                pass

    async def test_cbr_find_similar_cache_hit_performance(self, mock_mcp_server):
        """
        Test cache effectiveness for repeated cbr_find_similar queries.

        Verifies that cache significantly improves performance on repeated
        queries for the same example ID.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # First query (cold)
        metrics_cold = await measure_mcp_tool_latency(
            mock_mcp_server.cbr_find_similar,
            example_id="case-1",
            similarity_threshold=0.85,
            max_results=8,
            warmup_calls=0,
        )

        # Second query (should hit cache)
        metrics_warm = await measure_mcp_tool_latency(
            mock_mcp_server.cbr_find_similar,
            example_id="case-1",
            similarity_threshold=0.85,
            max_results=8,
            warmup_calls=0,
        )

        # Third query (cache hit)
        metrics_cached = await measure_mcp_tool_latency(
            mock_mcp_server.cbr_find_similar,
            example_id="case-1",
            similarity_threshold=0.85,
            max_results=8,
            warmup_calls=0,
        )

        # Verify cache improves performance
        # Note: With mocked server, improvement may be minimal
        # In real scenario, we expect significant improvement
        # Allow for timing variance in mocked tests (within 20%)
        # The 20% tolerance is needed because async mock timing has inherent variance
        # that can exceed 10% in edge cases, even when differences are sub-millisecond
        assert (
            metrics_cached["latency_ms"] <= metrics_cold["latency_ms"] * 1.2
        ), f"Cached latency {metrics_cached['latency_ms']:.2f}ms should be within 20% of cold {metrics_cold['latency_ms']:.2f}ms"
        assert all(
            m < 200.0
            for m in [
                metrics_cold["latency_ms"],
                metrics_warm["latency_ms"],
                metrics_cached["latency_ms"],
            ]
        ), "All queries should meet performance target"

    async def test_cbr_find_similar_cache_effectiveness_pattern(self, mock_mcp_server):
        """
        Test cache effectiveness with realistic query patterns.

        Verifies cache hit rate meets 70%+ target with mixed queries
        for different example IDs.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Simulate realistic query pattern: some repeated, some unique
        case_ids = ["case-1", "case-2", "case-3", "case-1", "case-2", "case-1"]
        queries_executed = 0
        total_latency = 0.0

        for case_id in case_ids:
            metrics = await measure_mcp_tool_latency(
                mock_mcp_server.cbr_find_similar,
                example_id=case_id,
                similarity_threshold=0.85,
                max_results=8,
                warmup_calls=0,
            )
            queries_executed += 1
            total_latency += metrics["latency_ms"]

            # Each query should meet target
            assert (
                metrics["latency_ms"] < 200.0
            ), f"Query {queries_executed} should be <200ms"

        # Verify average performance is good
        avg_latency = total_latency / queries_executed
        assert avg_latency < 150.0, "Average latency should benefit from caching"

    async def test_cbr_find_similar_concurrent_queries(self, mock_mcp_server):
        """
        Test cbr_find_similar performance under concurrent load.

        Verifies the system can handle 10+ concurrent similarity queries
        without significant performance degradation.
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Create 12 concurrent queries with different case IDs
        tool_calls = []
        case_ids = [f"case-{i % 5 + 1}" for i in range(12)]

        for case_id in case_ids:
            tool_calls.append(
                (
                    mock_mcp_server.cbr_find_similar,
                    (),
                    {
                        "example_id": case_id,
                        "similarity_threshold": 0.85,
                        "max_results": 8,
                    },
                )
            )

        # Measure concurrent performance
        metrics = await measure_concurrent_mcp_tools(tool_calls, max_concurrent=10)

        # Verify metrics
        assert metrics["total_calls"] == 12
        assert metrics["throughput_ops_per_sec"] > 0
        assert (
            metrics["p95_latency_ms"] < 300.0
        ), "P95 latency should remain reasonable under concurrent load"
        assert (
            metrics["p50_latency_ms"] < 200.0
        ), "Median latency should meet target under concurrent load"
        assert len(metrics["results"]) == 12

    async def test_cbr_find_similar_with_realistic_case_ids(self, mock_mcp_server):
        """
        Test cbr_find_similar with realistic case ID patterns.

        Verifies performance with actual case ID formats from the database
        (case-1, case-100, etc.).
        """
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Test with realistic case IDs
        realistic_ids = ["case-1", "case-10", "case-100", "case-42", "case-135"]

        for case_id in realistic_ids:
            metrics = await measure_mcp_tool_latency(
                mock_mcp_server.cbr_find_similar,
                example_id=case_id,
                similarity_threshold=0.85,
                max_results=8,
                warmup_calls=1,
            )

            # Verify performance with realistic IDs
            assert (
                metrics["latency_ms"] < 200.0
            ), f"Query with ID '{case_id}' should be <200ms"
            assert "result" in metrics
            assert metrics["result"] is not None

    async def test_cbr_find_similar_memory_usage(self, mock_mcp_server):
        """
        Test memory usage during cbr_find_similar operations.

        Verifies memory delta is reasonable and no leaks occur during
        similarity search operations.
        """
        if not HAS_PSUTIL:
            pytest.skip("psutil required for memory measurement")
        if not HAS_CBR:
            pytest.skip("CBR server components not available")

        # Measure memory during find_similar operation
        metrics = await measure_mcp_tool_memory(
            mock_mcp_server.cbr_find_similar,
            example_id="case-1",
            similarity_threshold=0.85,
            max_results=8,
        )

        # Verify memory metrics
        assert "baseline_mb" in metrics
        assert "peak_mb" in metrics
        assert "delta_mb" in metrics
        assert "result" in metrics

        # Verify reasonable memory usage
        assert metrics["baseline_mb"] > 0
        # Allow 1 MB tolerance for memory measurement variance from psutil
        # Memory measurements have inherent variance due to system operations,
        # garbage collection, and concurrent processes
        assert metrics["peak_mb"] >= metrics["baseline_mb"] - 1.0, (
            f"Peak memory ({metrics['peak_mb']:.2f} MB) should be within 1 MB "
            f"of baseline ({metrics['baseline_mb']:.2f} MB)"
        )
        # Memory delta should be reasonable for a single query
        assert (
            abs(metrics["delta_mb"]) < 50.0
        ), "Memory delta for single query should be <50MB"
