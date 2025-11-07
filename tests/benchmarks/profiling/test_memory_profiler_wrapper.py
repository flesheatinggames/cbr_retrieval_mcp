"""
Test suite for memory_profiler integration wrapper module.

This module provides comprehensive tests for the MemoryProfilerWrapper class
and associated decorators for memory profiling during CBR operations.
"""

import asyncio
from typing import Dict
from unittest.mock import MagicMock, patch

import pytest

try:
    from cbr_mcp_server.performance.profiling.memory_profiler_wrapper import (
        MemoryProfilerWrapper,
        profile_memory,
        profile_memory_async,
    )

    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MemoryProfilerWrapper = None
    profile_memory = None
    profile_memory_async = None
    MEMORY_PROFILER_AVAILABLE = False


# ============================================================================
# MemoryProfilerWrapper Class Tests
# ============================================================================


class TestMemoryProfilerWrapperClass:
    """Tests for MemoryProfilerWrapper class initialization and lifecycle."""

    def test_memory_profiler_initialization(self):
        """Test MemoryProfilerWrapper initializes with correct parameters."""
        # Test default initialization
        profiler = MemoryProfilerWrapper()
        assert profiler.interval == 0.01
        assert profiler.max_usage is False

        # Test custom initialization
        profiler_custom = MemoryProfilerWrapper(interval=0.05, max_usage=True)
        assert profiler_custom.interval == 0.05
        assert profiler_custom.max_usage is True

    def test_start_stop_memory_tracking_lifecycle(self):
        """Test start() and stop() methods work correctly."""
        profiler = MemoryProfilerWrapper()

        # Start tracking
        profiler.start()
        assert profiler._tracking is True
        assert profiler._start_time is not None

        # Perform some memory-intensive operation
        test_data = [i for i in range(10000)]

        # Stop tracking
        stats = profiler.stop()
        assert profiler._tracking is False
        assert isinstance(stats, dict)
        assert "baseline_mb" in stats
        assert "peak_mb" in stats
        assert "delta_mb" in stats
        assert stats["peak_mb"] >= stats["baseline_mb"]

    def test_context_manager_usage(self):
        """Test MemoryProfilerWrapper works as context manager."""
        # Use context manager
        with MemoryProfilerWrapper() as profiler:
            # Perform memory-intensive operation
            test_data = [i for i in range(10000)]
            assert profiler._tracking is True

        # After context, tracking should be stopped
        assert profiler._tracking is False
        assert hasattr(profiler, "_final_stats")
        assert isinstance(profiler._final_stats, dict)

    def test_decorator_usage_for_profiling_functions(self):
        """Test @profile_memory decorator works on sync functions."""

        @profile_memory(interval=0.01)
        def test_function():
            # Allocate some memory
            data = [i for i in range(10000)]
            return len(data)

        result = test_function()
        assert result == 10000

        # Decorator should have attached memory stats
        assert hasattr(test_function, "_memory_stats")
        assert isinstance(test_function._memory_stats, dict)
        assert "baseline_mb" in test_function._memory_stats

    @pytest.mark.asyncio
    async def test_async_function_memory_tracking(self):
        """Test @profile_memory_async decorator works on async functions."""

        @profile_memory_async(interval=0.01)
        async def async_test_function():
            # Allocate some memory asynchronously
            await asyncio.sleep(0.01)
            data = [i for i in range(10000)]
            return len(data)

        result = await async_test_function()
        assert result == 10000

        # Decorator should have attached memory stats
        assert hasattr(async_test_function, "_memory_stats")
        assert isinstance(async_test_function._memory_stats, dict)

    def test_interval_configuration_for_sampling(self):
        """Test custom interval configuration affects sampling rate."""
        profiler_fast = MemoryProfilerWrapper(interval=0.001)
        profiler_slow = MemoryProfilerWrapper(interval=0.1)

        assert profiler_fast.interval == 0.001
        assert profiler_slow.interval == 0.1
        assert profiler_fast.interval < profiler_slow.interval

    def test_max_usage_tracking_mode(self):
        """Test max_usage mode tracks peak memory correctly."""
        profiler = MemoryProfilerWrapper(max_usage=True)

        profiler.start()

        # Create memory spikes
        spike1 = [i for i in range(5000)]
        del spike1
        spike2 = [i for i in range(10000)]
        del spike2

        stats = profiler.stop()

        # With max_usage=True, peak should capture highest point
        assert stats["peak_mb"] >= stats["baseline_mb"]
        assert stats["delta_mb"] >= 0


# ============================================================================
# Memory Measurement Tests
# ============================================================================


class TestMemoryMeasurement:
    """Tests for memory measurement functionality."""

    def test_baseline_memory_measurement(self):
        """Test baseline memory is captured at start."""
        profiler = MemoryProfilerWrapper()
        profiler.start()

        baseline = profiler.get_baseline_memory_mb()
        assert isinstance(baseline, float)
        assert baseline > 0
        assert baseline < 10000  # Reasonable upper bound for baseline

        profiler.stop()

    def test_peak_memory_measurement(self):
        """Test peak memory is tracked during operations."""
        profiler = MemoryProfilerWrapper()
        profiler.start()

        baseline = profiler.get_baseline_memory_mb()

        # Allocate memory
        large_data = [i for i in range(100000)]

        peak = profiler.get_peak_memory_mb()
        assert isinstance(peak, float)
        assert peak >= baseline

        profiler.stop()

    def test_memory_delta_calculation(self):
        """Test memory delta calculated correctly."""
        profiler = MemoryProfilerWrapper()
        profiler.start()

        baseline = profiler.get_baseline_memory_mb()

        # Allocate memory
        large_data = [i for i in range(100000)]

        delta = profiler.get_memory_delta_mb()
        peak = profiler.get_peak_memory_mb()

        assert isinstance(delta, float)
        assert delta >= 0
        assert abs(delta - (peak - baseline)) < 0.1  # Allow small float error

        profiler.stop()

    def test_memory_usage_over_time_tracking(self):
        """Test memory measurements captured at multiple points."""
        profiler = MemoryProfilerWrapper()
        profiler.start()

        measurements = []

        # Take measurements at different points
        measurements.append(profiler.get_current_memory_mb())

        data1 = [i for i in range(10000)]
        measurements.append(profiler.get_current_memory_mb())

        data2 = [i for i in range(20000)]
        measurements.append(profiler.get_current_memory_mb())

        assert len(measurements) == 3
        assert all(isinstance(m, float) for m in measurements)
        # Memory should generally increase (or stay same)
        assert measurements[-1] >= measurements[0]

        profiler.stop()

    def test_multiple_measurement_points(self):
        """Test repeated measurements work correctly."""
        profiler = MemoryProfilerWrapper()
        profiler.start()

        # Take multiple measurements
        m1 = profiler.get_current_memory_mb()
        m2 = profiler.get_current_memory_mb()
        m3 = profiler.get_current_memory_mb()

        assert isinstance(m1, float)
        assert isinstance(m2, float)
        assert isinstance(m3, float)

        # Measurements should be independent and consistent
        assert abs(m1 - m2) < 10  # Should be very close
        assert abs(m2 - m3) < 10

        profiler.stop()


# ============================================================================
# Memory Statistics Tests
# ============================================================================


class TestMemoryStatistics:
    """Tests for memory statistics reporting."""

    def test_getting_current_memory_usage(self):
        """Test get_current_memory_mb() returns current memory."""
        profiler = MemoryProfilerWrapper()
        profiler.start()

        current = profiler.get_current_memory_mb()
        assert isinstance(current, float)
        assert current > 0
        assert current < 10000  # Reasonable upper bound

        profiler.stop()

    def test_getting_peak_memory_usage(self):
        """Test get_peak_memory_mb() returns peak memory."""
        profiler = MemoryProfilerWrapper()
        profiler.start()

        baseline = profiler.get_baseline_memory_mb()

        # Create memory spike
        spike = [i for i in range(100000)]

        peak = profiler.get_peak_memory_mb()
        assert isinstance(peak, float)
        assert peak >= baseline

        # Delete spike
        del spike

        # Peak should still be the highest point
        peak_after = profiler.get_peak_memory_mb()
        assert peak_after == peak

        profiler.stop()

    def test_getting_memory_growth_statistics(self):
        """Test get_memory_delta_mb() returns growth stats."""
        profiler = MemoryProfilerWrapper()
        profiler.start()

        # Initial delta should be 0 or very small
        initial_delta = profiler.get_memory_delta_mb()
        assert initial_delta >= 0
        assert initial_delta < 1  # Should be minimal at start

        # Allocate memory
        data = [i for i in range(100000)]

        # Delta should increase
        final_delta = profiler.get_memory_delta_mb()
        assert final_delta > initial_delta

        profiler.stop()

    def test_memory_usage_summary_reports(self):
        """Test get_memory_stats() returns comprehensive summary."""
        profiler = MemoryProfilerWrapper()
        profiler.start()

        # Allocate some memory
        data = [i for i in range(50000)]

        stats = profiler.get_memory_stats()

        # Verify comprehensive stats
        assert isinstance(stats, dict)
        assert "baseline_mb" in stats
        assert "peak_mb" in stats
        assert "current_mb" in stats
        assert "delta_mb" in stats

        # Verify stats are valid
        assert stats["baseline_mb"] > 0
        assert stats["peak_mb"] >= stats["baseline_mb"]
        assert stats["current_mb"] > 0
        assert stats["delta_mb"] >= 0

        profiler.stop()


# ============================================================================
# Integration with CBR Operations Tests
# ============================================================================


class TestCBROperationsIntegration:
    """Tests for memory profiling integration with CBR operations."""

    def test_memory_profiling_of_query_operations(self):
        """Test memory profiling works during CBR query operations."""

        @profile_memory(interval=0.01)
        def mock_cbr_query(query_text: str, top_k: int = 5):
            """Mock CBR query operation."""
            # Simulate query processing
            embeddings = [0.1] * 768  # Mock embedding vector
            results = [{"id": i, "score": 0.9} for i in range(top_k)]
            return results

        results = mock_cbr_query("test query", top_k=10)
        assert len(results) == 10

        # Verify memory stats captured
        assert hasattr(mock_cbr_query, "_memory_stats")
        stats = mock_cbr_query._memory_stats
        assert "baseline_mb" in stats
        assert "peak_mb" in stats

    @pytest.mark.asyncio
    async def test_memory_profiling_of_embedding_operations(self):
        """Test memory profiling works during embedding generation."""

        @profile_memory_async(interval=0.01)
        async def mock_embedding_generation(texts: list[str]):
            """Mock embedding generation operation."""
            await asyncio.sleep(0.01)
            # Simulate embedding generation - memory intensive
            embeddings = [[0.1] * 768 for _ in texts]
            return embeddings

        texts = [f"text_{i}" for i in range(100)]
        embeddings = await mock_embedding_generation(texts)
        assert len(embeddings) == 100

        # Verify memory stats captured
        assert hasattr(mock_embedding_generation, "_memory_stats")
        stats = mock_embedding_generation._memory_stats
        assert stats["peak_mb"] >= stats["baseline_mb"]

    def test_memory_profiling_of_database_operations(self):
        """Test memory profiling works during database operations."""

        @profile_memory(interval=0.01)
        def mock_database_operation():
            """Mock database operation."""
            # Simulate loading data from database
            records = [{"id": i, "data": f"record_{i}"} for i in range(1000)]
            return records

        records = mock_database_operation()
        assert len(records) == 1000

        # Verify memory tracking
        assert hasattr(mock_database_operation, "_memory_stats")
        stats = mock_database_operation._memory_stats
        assert stats["delta_mb"] >= 0

    def test_memory_profiling_of_cache_operations(self):
        """Test memory profiling works during cache operations."""
        profiler = MemoryProfilerWrapper()

        with profiler:
            # Simulate cache operations
            cache = {}
            for i in range(1000):
                cache[f"key_{i}"] = {"data": [j for j in range(100)]}

            assert len(cache) == 1000

        # Verify memory stats
        stats = profiler._final_stats
        assert "baseline_mb" in stats
        assert "peak_mb" in stats
        assert "delta_mb" in stats
        assert stats["delta_mb"] > 0  # Cache should use memory


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def memory_profiler_wrapper() -> MemoryProfilerWrapper:
    """
    Fixture providing a fresh MemoryProfilerWrapper instance.

    Returns:
        MemoryProfilerWrapper: Fresh profiler instance with default config
    """
    return MemoryProfilerWrapper()


@pytest.fixture
def memory_profiler_with_custom_config() -> MemoryProfilerWrapper:
    """
    Fixture providing a MemoryProfilerWrapper with custom configuration.

    Returns:
        MemoryProfilerWrapper: Profiler instance with custom interval and max_usage
    """
    return MemoryProfilerWrapper(interval=0.05, max_usage=True)
