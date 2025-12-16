"""
Unit tests for performance metrics tracking component.

This module tests the PerformanceMetricsTracker, MetricsSnapshot,
MetricsExporter, and PerformanceAlertManager classes that will be
implemented to track query latency, cache hits, and memory usage.

Following TDD principles - these tests define the expected behavior
and will initially fail until the implementation is complete.
"""

import json
import time
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

# These imports will fail initially - that's expected for TDD
from cbr_mcp_server.performance.metrics import (
    MetricsExporter,
    MetricsSnapshot,
    PerformanceAlertManager,
    PerformanceMetricsTracker,
)


class TestPerformanceMetricsTracker:
    """Test suite for PerformanceMetricsTracker class."""

    def test_init_creates_empty_tracker(self):
        """Test that tracker initializes with empty metrics."""
        tracker = PerformanceMetricsTracker()

        metrics = tracker.get_metrics_summary()
        assert metrics["query_count"] == 0
        assert metrics["cache_hits"] == 0
        assert metrics["cache_misses"] == 0
        assert metrics["latency_samples"] == 0

    def test_record_query_latency_single(self):
        """Test recording a single query latency."""
        tracker = PerformanceMetricsTracker()

        tracker.record_query_latency(0.150)  # 150ms

        metrics = tracker.get_metrics_summary()
        assert metrics["query_count"] == 1
        assert metrics["latency_min"] == 0.150
        assert metrics["latency_max"] == 0.150
        assert metrics["latency_avg"] == 0.150
        assert metrics["latency_samples"] == 1

    def test_record_query_latency_multiple(self):
        """Test aggregation of multiple query latencies."""
        tracker = PerformanceMetricsTracker()

        latencies = [0.100, 0.150, 0.200, 0.250, 0.300]
        for latency in latencies:
            tracker.record_query_latency(latency)

        metrics = tracker.get_metrics_summary()
        assert metrics["query_count"] == 5
        assert metrics["latency_min"] == 0.100
        assert metrics["latency_max"] == 0.300
        assert metrics["latency_avg"] == pytest.approx(0.200, rel=1e-3)
        assert metrics["latency_p95"] >= 0.250
        assert metrics["latency_p99"] >= 0.250
        assert metrics["latency_samples"] == 5

    def test_record_cache_hit(self):
        """Test cache hit recording."""
        tracker = PerformanceMetricsTracker()

        tracker.record_cache_hit()
        tracker.record_cache_hit()

        metrics = tracker.get_metrics_summary()
        assert metrics["cache_hits"] == 2
        assert metrics["cache_misses"] == 0
        assert metrics["cache_hit_rate"] == 1.0

    def test_record_cache_miss(self):
        """Test cache miss recording."""
        tracker = PerformanceMetricsTracker()

        tracker.record_cache_miss()
        tracker.record_cache_miss()

        metrics = tracker.get_metrics_summary()
        assert metrics["cache_hits"] == 0
        assert metrics["cache_misses"] == 2
        assert metrics["cache_hit_rate"] == 0.0

    def test_cache_hit_rate_mixed(self):
        """Test cache hit rate calculation with mixed hits and misses."""
        tracker = PerformanceMetricsTracker()

        tracker.record_cache_hit()
        tracker.record_cache_hit()
        tracker.record_cache_hit()
        tracker.record_cache_miss()

        metrics = tracker.get_metrics_summary()
        assert metrics["cache_hits"] == 3
        assert metrics["cache_misses"] == 1
        assert metrics["cache_hit_rate"] == pytest.approx(0.75, rel=1e-3)

    def test_cache_hit_rate_with_no_accesses(self):
        """Test cache hit rate when no cache accesses have occurred."""
        tracker = PerformanceMetricsTracker()

        metrics = tracker.get_metrics_summary()
        # Should return 0.0 or None when no accesses
        assert metrics["cache_hit_rate"] in (0.0, None)

    def test_record_memory_usage(self):
        """Test memory usage tracking."""
        tracker = PerformanceMetricsTracker()

        tracker.record_memory_usage(1024 * 1024 * 100)  # 100 MB
        tracker.record_memory_usage(1024 * 1024 * 150)  # 150 MB

        metrics = tracker.get_metrics_summary()
        assert metrics["memory_samples"] == 2
        assert metrics["memory_current"] == 1024 * 1024 * 150
        assert metrics["memory_peak"] >= 1024 * 1024 * 150

    def test_get_metrics_summary(self):
        """Test complete metrics summary retrieval."""
        tracker = PerformanceMetricsTracker()

        # Record various metrics
        tracker.record_query_latency(0.100)
        tracker.record_query_latency(0.200)
        tracker.record_cache_hit()
        tracker.record_cache_miss()
        tracker.record_memory_usage(1024 * 1024 * 50)

        metrics = tracker.get_metrics_summary()

        # Verify all expected keys are present
        expected_keys = [
            "query_count",
            "latency_min",
            "latency_max",
            "latency_avg",
            "latency_p95",
            "latency_p99",
            "latency_samples",
            "cache_hits",
            "cache_misses",
            "cache_hit_rate",
            "memory_current",
            "memory_peak",
            "memory_samples",
        ]
        for key in expected_keys:
            assert key in metrics

    @patch("time.time")
    def test_time_window_filtering(self, mock_time):
        """Test metrics aggregation over time windows."""
        tracker = PerformanceMetricsTracker()

        # Record metrics at different times
        mock_time.return_value = 1000.0
        tracker.record_query_latency(0.100)

        mock_time.return_value = 1300.0  # 5 minutes later
        tracker.record_query_latency(0.200)

        mock_time.return_value = 1600.0  # 10 minutes from start
        tracker.record_query_latency(0.300)

        # Get metrics for last 5 minutes window
        mock_time.return_value = 1600.0
        metrics = tracker.get_metrics_summary(window_seconds=300)

        # Only the last two queries should be included
        assert metrics["query_count"] == 2
        assert metrics["latency_min"] == 0.200

    def test_reset_metrics(self):
        """Test metrics can be cleared."""
        tracker = PerformanceMetricsTracker()

        # Record some metrics
        tracker.record_query_latency(0.100)
        tracker.record_cache_hit()
        tracker.record_memory_usage(1024 * 1024)

        # Reset
        tracker.reset_metrics()

        # Verify all metrics are cleared
        metrics = tracker.get_metrics_summary()
        assert metrics["query_count"] == 0
        assert metrics["cache_hits"] == 0
        assert metrics["cache_misses"] == 0
        assert metrics["latency_samples"] == 0
        assert metrics["memory_samples"] == 0

    def test_percentile_calculation_with_single_value(self):
        """Test percentile calculation with only one data point."""
        tracker = PerformanceMetricsTracker()

        tracker.record_query_latency(0.150)

        metrics = tracker.get_metrics_summary()
        # With single value, all percentiles should equal that value
        assert metrics["latency_p95"] == 0.150
        assert metrics["latency_p99"] == 0.150

    def test_percentile_calculation_with_two_values(self):
        """Test percentile calculation with two data points."""
        tracker = PerformanceMetricsTracker()

        tracker.record_query_latency(0.100)
        tracker.record_query_latency(0.200)

        metrics = tracker.get_metrics_summary()
        # Verify percentiles are reasonable
        assert 0.100 <= metrics["latency_p95"] <= 0.200
        assert 0.100 <= metrics["latency_p99"] <= 0.200

    def test_percentile_calculation_with_many_values(self):
        """Test percentile calculation with large dataset."""
        tracker = PerformanceMetricsTracker()

        # Record 100 latencies from 0.001 to 0.100
        for i in range(1, 101):
            tracker.record_query_latency(i / 1000.0)

        metrics = tracker.get_metrics_summary()
        # P95 should be around 0.095, P99 around 0.099
        assert 0.090 <= metrics["latency_p95"] <= 0.100
        assert 0.095 <= metrics["latency_p99"] <= 0.100

    @pytest.mark.asyncio
    async def test_concurrent_access_safety(self):
        """Test thread-safe metric recording with concurrent access."""
        import asyncio

        tracker = PerformanceMetricsTracker()

        async def record_metrics(count: int):
            for i in range(count):
                tracker.record_query_latency(0.100 + i * 0.001)
                tracker.record_cache_hit()
                await asyncio.sleep(0.001)

        # Run multiple concurrent tasks
        await asyncio.gather(
            record_metrics(10), record_metrics(10), record_metrics(10)
        )

        metrics = tracker.get_metrics_summary()
        # All 30 queries should be recorded
        assert metrics["query_count"] == 30
        assert metrics["cache_hits"] == 30
        assert metrics["latency_samples"] == 30

    def test_negative_latency_rejected(self):
        """Test that negative latency values are rejected."""
        tracker = PerformanceMetricsTracker()

        with pytest.raises(ValueError, match="Latency.*negative"):
            tracker.record_query_latency(-0.050)

    def test_extremely_large_latency(self):
        """Test handling of extremely large latency values."""
        tracker = PerformanceMetricsTracker()

        # Record very large latency (e.g., 1 hour = 3600 seconds)
        tracker.record_query_latency(3600.0)

        metrics = tracker.get_metrics_summary()
        assert metrics["latency_max"] == 3600.0
        assert metrics["query_count"] == 1

    def test_zero_latency(self):
        """Test handling of zero latency (edge case)."""
        tracker = PerformanceMetricsTracker()

        tracker.record_query_latency(0.0)

        metrics = tracker.get_metrics_summary()
        assert metrics["latency_min"] == 0.0
        assert metrics["latency_avg"] == 0.0
        assert metrics["query_count"] == 1

    def test_very_large_dataset_performance(self):
        """Test percentile calculation with very large dataset."""
        tracker = PerformanceMetricsTracker()

        # Record 10,000 latencies
        for i in range(10000):
            tracker.record_query_latency(0.001 + i * 0.0001)

        metrics = tracker.get_metrics_summary()
        assert metrics["query_count"] == 10000
        assert metrics["latency_samples"] == 10000
        # Verify percentiles are calculated efficiently
        assert metrics["latency_p95"] > 0.0
        assert metrics["latency_p99"] > metrics["latency_p95"]

    def test_memory_usage_overflow_protection(self):
        """Test handling of extremely large memory values."""
        tracker = PerformanceMetricsTracker()

        # Test with very large memory value (e.g., 1 TB)
        large_memory = 1024 * 1024 * 1024 * 1024
        tracker.record_memory_usage(large_memory)

        metrics = tracker.get_metrics_summary()
        assert metrics["memory_current"] == large_memory
        assert metrics["memory_peak"] == large_memory


class TestMetricsSnapshot:
    """Test suite for MetricsSnapshot dataclass."""

    def test_snapshot_creation(self):
        """Test snapshot captures point-in-time metrics."""
        metrics_data = {
            "query_count": 10,
            "latency_avg": 0.150,
            "cache_hit_rate": 0.75,
            "memory_current": 1024 * 1024 * 100,
        }

        snapshot = MetricsSnapshot(
            timestamp=datetime.now(), metrics=metrics_data
        )

        assert snapshot.metrics["query_count"] == 10
        assert snapshot.metrics["latency_avg"] == 0.150
        assert isinstance(snapshot.timestamp, datetime)

    def test_snapshot_immutability(self):
        """Test snapshot is immutable (frozen dataclass)."""
        metrics_data = {"query_count": 10}
        snapshot = MetricsSnapshot(
            timestamp=datetime.now(), metrics=metrics_data
        )

        # Attempting to modify should raise FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            snapshot.timestamp = datetime.now()

    def test_snapshot_timestamp(self):
        """Test snapshot includes accurate timestamp."""
        with patch("cbr_mcp_server.performance.metrics.datetime") as mock_dt:
            mock_now = datetime(2025, 1, 1, 12, 0, 0)
            mock_dt.now.return_value = mock_now

            snapshot = MetricsSnapshot(
                timestamp=mock_dt.now(), metrics={"query_count": 5}
            )

            assert snapshot.timestamp == mock_now

    def test_snapshot_preserves_all_metrics(self):
        """Test snapshot preserves all metric fields."""
        complete_metrics = {
            "query_count": 100,
            "latency_min": 0.050,
            "latency_max": 0.300,
            "latency_avg": 0.150,
            "latency_p95": 0.250,
            "latency_p99": 0.280,
            "cache_hits": 75,
            "cache_misses": 25,
            "cache_hit_rate": 0.75,
            "memory_current": 1024 * 1024 * 100,
            "memory_peak": 1024 * 1024 * 150,
        }

        snapshot = MetricsSnapshot(
            timestamp=datetime.now(), metrics=complete_metrics
        )

        assert snapshot.metrics == complete_metrics


class TestMetricsExporter:
    """Test suite for MetricsExporter class."""

    def test_export_to_json(self):
        """Test metrics export to JSON format."""
        exporter = MetricsExporter()
        metrics = {
            "query_count": 10,
            "latency_avg": 0.150,
            "cache_hit_rate": 0.75,
        }

        json_output = exporter.export_to_json(metrics)

        # Verify valid JSON
        parsed = json.loads(json_output)
        assert parsed["query_count"] == 10
        assert parsed["latency_avg"] == 0.150
        assert parsed["cache_hit_rate"] == 0.75

    def test_export_empty_metrics(self):
        """Test export with no metrics."""
        exporter = MetricsExporter()
        empty_metrics = {}

        json_output = exporter.export_to_json(empty_metrics)

        # Should produce valid empty JSON
        parsed = json.loads(json_output)
        assert isinstance(parsed, dict)
        assert len(parsed) == 0

    def test_export_with_special_values(self):
        """Test handling of NaN and Infinity in metrics."""
        exporter = MetricsExporter()
        metrics = {
            "query_count": 10,
            "latency_avg": float("nan"),
            "cache_hit_rate": float("inf"),
        }

        json_output = exporter.export_to_json(metrics)

        # Should handle special values gracefully
        parsed = json.loads(json_output)
        assert parsed["query_count"] == 10
        # NaN and Infinity should be serialized to null or string
        assert parsed["latency_avg"] in (None, "NaN", "nan")
        assert parsed["cache_hit_rate"] in (None, "Infinity", "inf")

    @patch("cbr_mcp_server.performance.metrics.datetime")
    def test_export_includes_metadata(self, mock_dt):
        """Test export includes timestamp and version info."""
        mock_now = datetime(2025, 1, 1, 12, 0, 0)
        mock_dt.now.return_value = mock_now

        exporter = MetricsExporter()
        metrics = {"query_count": 10}

        json_output = exporter.export_to_json(
            metrics, include_metadata=True
        )

        parsed = json.loads(json_output)
        assert "metadata" in parsed
        assert "timestamp" in parsed["metadata"]
        assert "version" in parsed["metadata"]

    def test_export_to_file(self):
        """Test exporting metrics to a file."""
        exporter = MetricsExporter()
        metrics = {"query_count": 10, "cache_hit_rate": 0.75}

        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as f:
            filepath = f.name

        try:
            exporter.export_to_file(metrics, filepath)

            # Verify file was written correctly
            with open(filepath, "r") as f:
                parsed = json.load(f)
                assert parsed["query_count"] == 10
                assert parsed["cache_hit_rate"] == 0.75
        finally:
            import os

            os.unlink(filepath)

    def test_export_pretty_print(self):
        """Test export with pretty-printing enabled."""
        exporter = MetricsExporter()
        metrics = {"query_count": 10, "cache_hit_rate": 0.75}

        json_output = exporter.export_to_json(metrics, pretty_print=True)

        # Should contain newlines and indentation
        assert "\n" in json_output
        assert "  " in json_output or "\t" in json_output

    def test_export_to_file_permission_error(self):
        """Test export handles permission errors gracefully."""
        exporter = MetricsExporter()
        metrics = {"query_count": 10}

        # Try to write to a read-only location
        with pytest.raises((PermissionError, OSError)):
            exporter.export_to_file(metrics, "/root/restricted.json")

    def test_export_to_file_disk_full(self):
        """Test export handles disk full errors."""
        exporter = MetricsExporter()
        metrics = {"query_count": 10}

        # Mock open to simulate disk full
        with patch("builtins.open", side_effect=OSError("No space left on device")):
            with pytest.raises(OSError, match="No space left"):
                exporter.export_to_file(metrics, "/tmp/test.json")

    def test_export_invalid_path(self):
        """Test export handles invalid file paths."""
        exporter = MetricsExporter()
        metrics = {"query_count": 10}

        # Try to write to non-existent directory
        with pytest.raises((FileNotFoundError, OSError)):
            exporter.export_to_file(metrics, "/nonexistent/path/metrics.json")

    def test_export_large_metrics_dict(self):
        """Test export handles very large metrics dictionaries."""
        exporter = MetricsExporter()

        # Create large metrics dict with 1000 keys
        large_metrics = {f"metric_{i}": i * 0.001 for i in range(1000)}

        json_output = exporter.export_to_json(large_metrics)

        # Should successfully serialize
        parsed = json.loads(json_output)
        assert len(parsed) == 1000
        assert parsed["metric_999"] == 0.999


class TestPerformanceAlertManager:
    """Test suite for PerformanceAlertManager class."""

    def test_register_threshold(self):
        """Test threshold registration for alerts."""
        manager = PerformanceAlertManager()

        manager.register_threshold(
            metric_name="latency_avg", threshold=0.200, comparison="gt"
        )

        thresholds = manager.get_thresholds()
        assert "latency_avg" in thresholds
        assert thresholds["latency_avg"]["threshold"] == 0.200
        assert thresholds["latency_avg"]["comparison"] == "gt"

    def test_check_latency_threshold_exceeded(self):
        """Test alert triggered when latency exceeds threshold."""
        manager = PerformanceAlertManager()
        callback = Mock()

        manager.register_threshold(
            metric_name="latency_avg",
            threshold=0.200,
            comparison="gt",
            callback=callback,
        )

        metrics = {"latency_avg": 0.250}
        alerts = manager.check_thresholds(metrics)

        # Alert should be triggered
        assert len(alerts) == 1
        assert alerts[0]["metric"] == "latency_avg"
        assert alerts[0]["value"] == 0.250
        assert alerts[0]["threshold"] == 0.200
        callback.assert_called_once()

    def test_check_latency_threshold_not_exceeded(self):
        """Test no alert when threshold not exceeded."""
        manager = PerformanceAlertManager()
        callback = Mock()

        manager.register_threshold(
            metric_name="latency_avg",
            threshold=0.200,
            comparison="gt",
            callback=callback,
        )

        metrics = {"latency_avg": 0.150}
        alerts = manager.check_thresholds(metrics)

        # No alert should be triggered
        assert len(alerts) == 0
        callback.assert_not_called()

    def test_check_cache_hit_rate_threshold(self):
        """Test alert for low cache hit rate."""
        manager = PerformanceAlertManager()
        callback = Mock()

        manager.register_threshold(
            metric_name="cache_hit_rate",
            threshold=0.70,
            comparison="lt",
            callback=callback,
        )

        metrics = {"cache_hit_rate": 0.50}
        alerts = manager.check_thresholds(metrics)

        # Alert should be triggered
        assert len(alerts) == 1
        assert alerts[0]["metric"] == "cache_hit_rate"
        callback.assert_called_once()

    def test_check_memory_threshold(self):
        """Test alert for high memory usage."""
        manager = PerformanceAlertManager()
        callback = Mock()

        threshold_mb = 500 * 1024 * 1024  # 500 MB
        manager.register_threshold(
            metric_name="memory_current",
            threshold=threshold_mb,
            comparison="gt",
            callback=callback,
        )

        metrics = {"memory_current": 600 * 1024 * 1024}  # 600 MB
        alerts = manager.check_thresholds(metrics)

        assert len(alerts) == 1
        assert alerts[0]["metric"] == "memory_current"
        callback.assert_called_once()

    def test_multiple_threshold_violations(self):
        """Test handling of multiple simultaneous alerts."""
        manager = PerformanceAlertManager()
        callback1 = Mock()
        callback2 = Mock()

        manager.register_threshold(
            "latency_avg", threshold=0.200, comparison="gt", callback=callback1
        )
        manager.register_threshold(
            "cache_hit_rate",
            threshold=0.70,
            comparison="lt",
            callback=callback2,
        )

        metrics = {"latency_avg": 0.300, "cache_hit_rate": 0.50}
        alerts = manager.check_thresholds(metrics)

        # Both alerts should be triggered
        assert len(alerts) == 2
        callback1.assert_called_once()
        callback2.assert_called_once()

    @patch("time.time")
    def test_alert_cooldown_period(self, mock_time):
        """Test alerts respect cooldown to avoid spam."""
        manager = PerformanceAlertManager(cooldown_seconds=60)
        callback = Mock()

        manager.register_threshold(
            "latency_avg", threshold=0.200, comparison="gt", callback=callback
        )

        # First alert
        mock_time.return_value = 1000.0
        metrics = {"latency_avg": 0.300}
        alerts1 = manager.check_thresholds(metrics)
        assert len(alerts1) == 1
        assert callback.call_count == 1

        # Second alert within cooldown (30 seconds later)
        mock_time.return_value = 1030.0
        alerts2 = manager.check_thresholds(metrics)
        # Should be suppressed due to cooldown
        assert len(alerts2) == 0
        assert callback.call_count == 1  # Not called again

        # Third alert after cooldown (70 seconds from first)
        mock_time.return_value = 1070.0
        alerts3 = manager.check_thresholds(metrics)
        assert len(alerts3) == 1
        assert callback.call_count == 2  # Called again

    def test_clear_alerts(self):
        """Test alert history can be cleared."""
        manager = PerformanceAlertManager()

        manager.register_threshold(
            "latency_avg", threshold=0.200, comparison="gt"
        )

        metrics = {"latency_avg": 0.300}
        alerts = manager.check_thresholds(metrics)
        assert len(alerts) == 1

        # Clear alert history
        manager.clear_alert_history()

        # Verify history is cleared
        history = manager.get_alert_history()
        assert len(history) == 0

    def test_get_alert_history(self):
        """Test retrieving alert history."""
        manager = PerformanceAlertManager()

        manager.register_threshold(
            "latency_avg", threshold=0.200, comparison="gt"
        )

        metrics = {"latency_avg": 0.300}
        manager.check_thresholds(metrics)

        history = manager.get_alert_history()
        assert len(history) == 1
        assert history[0]["metric"] == "latency_avg"
        assert "timestamp" in history[0]

    def test_comparison_operators(self):
        """Test different comparison operators (gt, lt, gte, lte, eq)."""
        manager = PerformanceAlertManager()

        # Test gt (greater than)
        manager.register_threshold("metric1", threshold=10, comparison="gt")
        assert (
            len(manager.check_thresholds({"metric1": 11})) == 1
        )  # Should alert
        assert (
            len(manager.check_thresholds({"metric1": 10})) == 0
        )  # Should not

        # Test gte (greater than or equal)
        manager.register_threshold("metric2", threshold=10, comparison="gte")
        assert len(manager.check_thresholds({"metric2": 10})) == 1
        assert len(manager.check_thresholds({"metric2": 9})) == 0

        # Test lt (less than)
        manager.register_threshold("metric3", threshold=10, comparison="lt")
        assert len(manager.check_thresholds({"metric3": 9})) == 1
        assert len(manager.check_thresholds({"metric3": 10})) == 0

        # Test lte (less than or equal)
        manager.register_threshold("metric4", threshold=10, comparison="lte")
        assert len(manager.check_thresholds({"metric4": 10})) == 1
        assert len(manager.check_thresholds({"metric4": 11})) == 0

        # Test eq (equal)
        manager.register_threshold("metric5", threshold=10, comparison="eq")
        assert len(manager.check_thresholds({"metric5": 10})) == 1
        assert len(manager.check_thresholds({"metric5": 9})) == 0
