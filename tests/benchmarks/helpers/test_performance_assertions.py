"""
Unit tests for performance assertion helpers.

Tests the performance_assertions module which provides reusable assertion
utilities for validating performance metrics in benchmark tests.
"""

from typing import Any, Dict, List

import pytest


class TestLatencyAssertions:
    """Test suite for latency assertion functions."""

    def test_assert_latency_under_threshold_passes(self):
        """Test that assert_latency_under_threshold passes when latency is acceptable."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_latency_under_threshold,
        )

        # Should not raise - latency under threshold
        assert_latency_under_threshold(
            latency_ms=50.0, threshold_ms=100.0, metric_name="query_latency"
        )

        # Should not raise - latency equals threshold
        assert_latency_under_threshold(
            latency_ms=100.0, threshold_ms=100.0, metric_name="query_latency"
        )

    def test_assert_latency_under_threshold_fails(self):
        """Test that assert_latency_under_threshold fails when latency exceeds threshold."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_latency_under_threshold,
        )

        with pytest.raises(AssertionError) as exc_info:
            assert_latency_under_threshold(
                latency_ms=150.0, threshold_ms=100.0, metric_name="query_latency"
            )

        error_message = str(exc_info.value)
        assert "query_latency" in error_message
        assert "150.0" in error_message
        assert "100.0" in error_message

    def test_assert_percentile_latency_passes(self):
        """Test that assert_percentile_latency passes when percentile meets threshold."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_percentile_latency,
        )

        stats = {"p50": 25.0, "p95": 80.0, "p99": 120.0}

        # Should not raise - p95 under threshold
        assert_percentile_latency(stats, percentile="p95", threshold_ms=100.0)

        # Should not raise - p50 under threshold
        assert_percentile_latency(stats, percentile="p50", threshold_ms=50.0)

    def test_assert_percentile_latency_fails(self):
        """Test that assert_percentile_latency fails when percentile exceeds threshold."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_percentile_latency,
        )

        stats = {"p50": 25.0, "p95": 150.0, "p99": 200.0}

        with pytest.raises(AssertionError) as exc_info:
            assert_percentile_latency(stats, percentile="p95", threshold_ms=100.0)

        error_message = str(exc_info.value)
        assert "p95" in error_message
        assert "150.0" in error_message
        assert "100.0" in error_message

    def test_assert_percentile_latency_missing_percentile(self):
        """Test that assert_percentile_latency handles missing percentile."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_percentile_latency,
        )

        stats = {"p50": 25.0, "p95": 80.0}

        with pytest.raises(KeyError):
            assert_percentile_latency(stats, percentile="p99", threshold_ms=100.0)

    def test_assert_latency_distribution_passes(self):
        """Test that assert_latency_distribution passes when all percentiles meet thresholds."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_latency_distribution,
        )

        stats = {"p50": 25.0, "p95": 80.0, "p99": 120.0}

        # Should not raise - all percentiles under thresholds
        assert_latency_distribution(stats, p50_max=50.0, p95_max=100.0, p99_max=150.0)

    def test_assert_latency_distribution_fails_single_percentile(self):
        """Test that assert_latency_distribution fails when one percentile exceeds threshold."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_latency_distribution,
        )

        stats = {"p50": 25.0, "p95": 150.0, "p99": 120.0}

        with pytest.raises(AssertionError) as exc_info:
            assert_latency_distribution(
                stats, p50_max=50.0, p95_max=100.0, p99_max=150.0
            )

        error_message = str(exc_info.value)
        assert "p95" in error_message
        assert "150.0" in error_message

    def test_assert_latency_distribution_fails_multiple_percentiles(self):
        """Test that assert_latency_distribution fails when multiple percentiles exceed thresholds."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_latency_distribution,
        )

        stats = {"p50": 60.0, "p95": 150.0, "p99": 200.0}

        with pytest.raises(AssertionError) as exc_info:
            assert_latency_distribution(
                stats, p50_max=50.0, p95_max=100.0, p99_max=150.0
            )

        error_message = str(exc_info.value)
        # Should mention all failing percentiles
        assert (
            "p50" in error_message or "p95" in error_message or "p99" in error_message
        )


class TestMemoryAssertions:
    """Test suite for memory assertion functions."""

    def test_assert_memory_under_threshold_passes(self):
        """Test that assert_memory_under_threshold passes when memory is acceptable."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_memory_under_threshold,
        )

        # Should not raise - memory under threshold
        assert_memory_under_threshold(
            memory_mb=250.0, threshold_mb=500.0, metric_name="peak_memory"
        )

        # Should not raise - memory equals threshold
        assert_memory_under_threshold(
            memory_mb=500.0, threshold_mb=500.0, metric_name="peak_memory"
        )

    def test_assert_memory_under_threshold_fails(self):
        """Test that assert_memory_under_threshold fails when memory exceeds threshold."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_memory_under_threshold,
        )

        with pytest.raises(AssertionError) as exc_info:
            assert_memory_under_threshold(
                memory_mb=600.0, threshold_mb=500.0, metric_name="peak_memory"
            )

        error_message = str(exc_info.value)
        assert "peak_memory" in error_message
        assert "600.0" in error_message
        assert "500.0" in error_message

    def test_assert_memory_delta_passes(self):
        """Test that assert_memory_delta passes when delta is within limit."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_memory_delta,
        )

        # Should not raise - delta under max
        assert_memory_delta(baseline_mb=100.0, current_mb=120.0, max_delta_mb=50.0)

        # Should not raise - delta equals max
        assert_memory_delta(baseline_mb=100.0, current_mb=150.0, max_delta_mb=50.0)

    def test_assert_memory_delta_fails(self):
        """Test that assert_memory_delta fails when delta exceeds limit."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_memory_delta,
        )

        with pytest.raises(AssertionError) as exc_info:
            assert_memory_delta(baseline_mb=100.0, current_mb=200.0, max_delta_mb=50.0)

        error_message = str(exc_info.value)
        assert "100.0" in error_message  # baseline
        assert "200.0" in error_message  # current
        assert "100.0" in error_message or "50.0" in error_message  # delta or max

    def test_assert_no_memory_leak_passes(self):
        """Test that assert_no_memory_leak passes when memory growth is acceptable."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_no_memory_leak,
        )

        # Should not raise - stable memory
        measurements = [100.0, 102.0, 101.0, 103.0, 102.0]
        assert_no_memory_leak(measurements, max_growth_pct=10.0)

        # Should not raise - growth under limit
        measurements = [100.0, 105.0, 108.0, 109.0, 109.5]
        assert_no_memory_leak(measurements, max_growth_pct=10.0)

    def test_assert_no_memory_leak_fails(self):
        """Test that assert_no_memory_leak fails when memory leak detected."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_no_memory_leak,
        )

        # Clear upward trend indicating leak
        measurements = [100.0, 115.0, 130.0, 145.0, 160.0]

        with pytest.raises(AssertionError) as exc_info:
            assert_no_memory_leak(measurements, max_growth_pct=10.0)

        error_message = str(exc_info.value)
        assert "leak" in error_message.lower() or "growth" in error_message.lower()

    def test_assert_no_memory_leak_empty_measurements(self):
        """Test that assert_no_memory_leak handles empty measurements."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_no_memory_leak,
        )

        with pytest.raises(ValueError):
            assert_no_memory_leak([], max_growth_pct=10.0)


class TestPerformanceMetricsAssertions:
    """Test suite for performance metrics assertion functions."""

    def test_assert_cache_hit_rate_passes(self):
        """Test that assert_cache_hit_rate passes when hit rate meets minimum."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_cache_hit_rate,
        )

        # Should not raise - 80% hit rate meets 70% minimum
        assert_cache_hit_rate(hits=80, misses=20, min_hit_rate_pct=70.0)

        # Should not raise - 70% hit rate equals minimum
        assert_cache_hit_rate(hits=70, misses=30, min_hit_rate_pct=70.0)

    def test_assert_cache_hit_rate_fails(self):
        """Test that assert_cache_hit_rate fails when hit rate below minimum."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_cache_hit_rate,
        )

        with pytest.raises(AssertionError) as exc_info:
            # 50% hit rate below 70% minimum
            assert_cache_hit_rate(hits=50, misses=50, min_hit_rate_pct=70.0)

        error_message = str(exc_info.value)
        assert "50" in error_message or "70" in error_message

    def test_assert_cache_hit_rate_zero_requests(self):
        """Test that assert_cache_hit_rate handles zero requests."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_cache_hit_rate,
        )

        with pytest.raises(ValueError):
            assert_cache_hit_rate(hits=0, misses=0, min_hit_rate_pct=70.0)

    def test_assert_throughput_passes(self):
        """Test that assert_throughput passes when throughput meets minimum."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_throughput,
        )

        # Should not raise - 100 ops/sec meets 50 minimum
        assert_throughput(operations=1000, duration_sec=10.0, min_ops_per_sec=50.0)

        # Should not raise - 50 ops/sec equals minimum
        assert_throughput(operations=500, duration_sec=10.0, min_ops_per_sec=50.0)

    def test_assert_throughput_fails(self):
        """Test that assert_throughput fails when throughput below minimum."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_throughput,
        )

        with pytest.raises(AssertionError) as exc_info:
            # 20 ops/sec below 50 minimum
            assert_throughput(operations=200, duration_sec=10.0, min_ops_per_sec=50.0)

        error_message = str(exc_info.value)
        assert "20" in error_message or "50" in error_message

    def test_assert_throughput_zero_duration(self):
        """Test that assert_throughput handles zero duration."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_throughput,
        )

        with pytest.raises(ValueError):
            assert_throughput(operations=100, duration_sec=0.0, min_ops_per_sec=50.0)

    def test_assert_measurement_variance_passes(self):
        """Test that assert_measurement_variance passes when variance is acceptable."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_measurement_variance,
        )

        # Low variance measurements
        measurements = [100.0, 102.0, 98.0, 101.0, 99.0]
        assert_measurement_variance(measurements, max_cv_pct=10.0)

    def test_assert_measurement_variance_fails(self):
        """Test that assert_measurement_variance fails when variance too high."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_measurement_variance,
        )

        # High variance measurements
        measurements = [50.0, 100.0, 75.0, 150.0, 125.0]

        with pytest.raises(AssertionError) as exc_info:
            assert_measurement_variance(measurements, max_cv_pct=10.0)

        error_message = str(exc_info.value)
        assert "variance" in error_message.lower() or "cv" in error_message.lower()

    def test_assert_measurement_variance_empty_measurements(self):
        """Test that assert_measurement_variance handles empty measurements."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_measurement_variance,
        )

        with pytest.raises(ValueError):
            assert_measurement_variance([], max_cv_pct=10.0)


class TestHelperUtilities:
    """Test suite for helper utility functions."""

    def test_format_performance_message(self):
        """Test that format_performance_message creates descriptive messages."""
        from tests.benchmarks.helpers.performance_assertions import (
            format_performance_message,
        )

        message = format_performance_message(
            metric="query_latency", value=150.0, threshold=100.0, unit="ms"
        )

        assert "query_latency" in message
        assert "150.0" in message
        assert "100.0" in message
        assert "ms" in message

    def test_format_performance_message_without_unit(self):
        """Test that format_performance_message works without unit."""
        from tests.benchmarks.helpers.performance_assertions import (
            format_performance_message,
        )

        message = format_performance_message(
            metric="hit_rate", value=60.0, threshold=70.0, unit=""
        )

        assert "hit_rate" in message
        assert "60.0" in message
        assert "70.0" in message

    def test_calculate_percentile_valid(self):
        """Test that calculate_percentile correctly calculates percentiles."""
        from tests.benchmarks.helpers.performance_assertions import (
            calculate_percentile,
        )

        data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        # Test various percentiles
        p50 = calculate_percentile(data, 50)
        assert 45 <= p50 <= 55  # Around median

        p95 = calculate_percentile(data, 95)
        assert 90 <= p95 <= 100  # Near top

        p0 = calculate_percentile(data, 0)
        assert p0 == 10  # Minimum

        p100 = calculate_percentile(data, 100)
        assert p100 == 100  # Maximum

    def test_calculate_percentile_single_value(self):
        """Test that calculate_percentile handles single value."""
        from tests.benchmarks.helpers.performance_assertions import (
            calculate_percentile,
        )

        data = [42.0]
        assert calculate_percentile(data, 50) == 42.0
        assert calculate_percentile(data, 95) == 42.0

    def test_calculate_percentile_empty_data(self):
        """Test that calculate_percentile handles empty data."""
        from tests.benchmarks.helpers.performance_assertions import (
            calculate_percentile,
        )

        with pytest.raises(ValueError):
            calculate_percentile([], 50)

    def test_calculate_percentile_invalid_percentile(self):
        """Test that calculate_percentile rejects invalid percentiles."""
        from tests.benchmarks.helpers.performance_assertions import (
            calculate_percentile,
        )

        data = [10, 20, 30]

        with pytest.raises(ValueError):
            calculate_percentile(data, -1)

        with pytest.raises(ValueError):
            calculate_percentile(data, 101)

    def test_detect_outliers(self):
        """Test that detect_outliers correctly identifies outliers."""
        from tests.benchmarks.helpers.performance_assertions import detect_outliers

        # Normal distribution with outliers
        measurements = [100, 102, 98, 101, 99, 200, 95, 103]

        outliers = detect_outliers(measurements, threshold_std_dev=2.0)

        assert len(outliers) > 0
        assert 200 in outliers  # Clear outlier

    def test_detect_outliers_no_outliers(self):
        """Test that detect_outliers returns empty when no outliers."""
        from tests.benchmarks.helpers.performance_assertions import detect_outliers

        # Uniform data
        measurements = [100, 101, 99, 100, 102, 98, 101, 99]

        outliers = detect_outliers(measurements, threshold_std_dev=2.0)

        assert len(outliers) == 0

    def test_detect_outliers_empty_data(self):
        """Test that detect_outliers handles empty data."""
        from tests.benchmarks.helpers.performance_assertions import detect_outliers

        with pytest.raises(ValueError):
            detect_outliers([], threshold_std_dev=2.0)

    def test_detect_outliers_single_value(self):
        """Test that detect_outliers handles single value."""
        from tests.benchmarks.helpers.performance_assertions import detect_outliers

        outliers = detect_outliers([100.0], threshold_std_dev=2.0)
        assert len(outliers) == 0


class TestEdgeCases:
    """Test suite for edge cases and error handling."""

    def test_negative_latency_rejected(self):
        """Test that negative latency values are rejected."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_latency_under_threshold,
        )

        with pytest.raises(ValueError):
            assert_latency_under_threshold(
                latency_ms=-10.0, threshold_ms=100.0, metric_name="query_latency"
            )

    def test_negative_threshold_rejected(self):
        """Test that negative threshold values are rejected."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_latency_under_threshold,
        )

        with pytest.raises(ValueError):
            assert_latency_under_threshold(
                latency_ms=50.0, threshold_ms=-100.0, metric_name="query_latency"
            )

    def test_negative_memory_rejected(self):
        """Test that negative memory values are rejected."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_memory_under_threshold,
        )

        with pytest.raises(ValueError):
            assert_memory_under_threshold(
                memory_mb=-100.0, threshold_mb=500.0, metric_name="peak_memory"
            )

    def test_zero_threshold_values(self):
        """Test that zero thresholds are handled correctly."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_latency_under_threshold,
        )

        # Should work with zero threshold
        assert_latency_under_threshold(
            latency_ms=0.0, threshold_ms=0.0, metric_name="query_latency"
        )

        # Should fail if latency above zero threshold
        with pytest.raises(AssertionError):
            assert_latency_under_threshold(
                latency_ms=1.0, threshold_ms=0.0, metric_name="query_latency"
            )

    def test_empty_stats_dict(self):
        """Test that empty stats dict is handled."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_percentile_latency,
        )

        with pytest.raises(KeyError):
            assert_percentile_latency({}, percentile="p95", threshold_ms=100.0)

    def test_negative_operations_rejected(self):
        """Test that negative operations are rejected."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_throughput,
        )

        with pytest.raises(ValueError):
            assert_throughput(operations=-100, duration_sec=10.0, min_ops_per_sec=50.0)

    def test_negative_duration_rejected(self):
        """Test that negative duration is rejected."""
        from tests.benchmarks.helpers.performance_assertions import (
            assert_throughput,
        )

        with pytest.raises(ValueError):
            assert_throughput(operations=100, duration_sec=-10.0, min_ops_per_sec=50.0)
