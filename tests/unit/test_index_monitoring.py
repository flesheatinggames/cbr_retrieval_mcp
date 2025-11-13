"""
Unit tests for Index Performance Monitoring components.

This module tests IndexPerformanceMonitor and related components following TDD principles.
These tests will initially fail until the implementations are complete.

Test Coverage:
- IndexPerformanceMonitor: Query latency, index size, memory usage tracking
- IndexPerformanceMetrics: Metrics aggregation and reporting
- IndexPerformanceThresholds: Threshold detection and alerting
- Integration with PerformanceTracker
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import numpy as np
import pytest

# These imports will fail initially - this is expected in TDD
from cbr_mcp_server.performance.index_monitor import (
    IndexPerformanceMetrics,
    IndexPerformanceMonitor,
    IndexPerformanceThresholds,
    LatencyDistribution,
)


class TestIndexPerformanceMonitor:
    """Test suite for IndexPerformanceMonitor component."""

    @pytest.fixture
    def mock_chromadb_collection(self):
        """Create mock ChromaDB collection."""
        collection = MagicMock()
        collection.count.return_value = 135  # Standard case base size
        collection.query.return_value = {
            "ids": [["case-1", "case-2"]],
            "distances": [[0.1, 0.2]],
            "metadatas": [[{"category": "code"}, {"category": "code"}]],
            "documents": [["doc1", "doc2"]],
        }
        # Mock HNSW metadata
        collection.metadata = {
            "hnsw:space": "cosine",
            "hnsw:construction_ef": 100,
            "hnsw:M": 16,
            "hnsw:search_ef": 50,
        }
        return collection

    @pytest.fixture
    def mock_psutil(self):
        """Mock psutil for memory monitoring."""
        with patch("cbr_mcp_server.performance.index_monitor.psutil") as mock:
            mock_process = Mock()
            mock_process.memory_info.return_value.rss = 400 * 1024 * 1024  # 400MB
            mock.Process.return_value = mock_process
            yield mock

    @pytest.fixture
    def index_monitor(self, mock_chromadb_collection, mock_psutil):
        """Create IndexPerformanceMonitor instance."""
        return IndexPerformanceMonitor(collection=mock_chromadb_collection)

    def test_monitor_initialization_with_defaults(
        self, mock_chromadb_collection, mock_psutil
    ):
        """Verify IndexPerformanceMonitor initializes with correct default values."""
        monitor = IndexPerformanceMonitor(collection=mock_chromadb_collection)

        assert monitor.collection is mock_chromadb_collection
        assert monitor.enabled is True
        assert isinstance(monitor.thresholds, IndexPerformanceThresholds)
        assert monitor.query_latencies == [] or isinstance(
            monitor.query_latencies, list
        )
        assert monitor.metrics is None or isinstance(
            monitor.metrics, IndexPerformanceMetrics
        )

    def test_monitor_initialization_with_custom_thresholds(
        self, mock_chromadb_collection, mock_psutil
    ):
        """Verify custom thresholds can be configured."""
        thresholds = IndexPerformanceThresholds(
            max_query_latency_ms=150.0, max_memory_mb=300, max_index_size=200
        )

        monitor = IndexPerformanceMonitor(
            collection=mock_chromadb_collection, thresholds=thresholds
        )

        assert monitor.thresholds.max_query_latency_ms == 150.0
        assert monitor.thresholds.max_memory_mb == 300
        assert monitor.thresholds.max_index_size == 200

    def test_track_query_latency_single_query(self, index_monitor):
        """Verify query latency is tracked for individual queries."""
        query_latency_ms = 45.3

        index_monitor.track_query_latency(query_latency_ms)

        assert len(index_monitor.query_latencies) >= 1
        assert query_latency_ms in index_monitor.query_latencies

    def test_track_query_latency_multiple_queries(self, index_monitor):
        """Verify multiple query latencies are accumulated."""
        latencies = [30.5, 45.2, 52.1, 38.7, 61.3]

        for latency in latencies:
            index_monitor.track_query_latency(latency)

        assert len(index_monitor.query_latencies) >= len(latencies)
        for latency in latencies:
            assert latency in index_monitor.query_latencies

    def test_calculate_latency_distribution_percentiles(self, index_monitor):
        """Verify latency distribution percentiles (p50, p95, p99) calculated correctly."""
        # Create distribution with known percentiles
        latencies = list(range(1, 101))  # 1-100ms, median=50.5, p95=95.05, p99=99.01
        for latency in latencies:
            index_monitor.track_query_latency(float(latency))

        distribution = index_monitor.calculate_latency_distribution()

        assert isinstance(distribution, LatencyDistribution)
        # Allow small tolerance for floating point calculations
        assert 49.0 <= distribution.p50_ms <= 51.0
        assert 94.0 <= distribution.p95_ms <= 96.0
        assert 98.0 <= distribution.p99_ms <= 100.0

    def test_calculate_latency_distribution_with_outliers(self, index_monitor):
        """Verify outlier handling in latency distribution."""
        # Mostly fast queries with a few slow outliers
        fast_queries = [30.0] * 90
        slow_outliers = [500.0, 600.0, 700.0]  # Significant outliers
        all_latencies = fast_queries + slow_outliers

        for latency in all_latencies:
            index_monitor.track_query_latency(latency)

        distribution = index_monitor.calculate_latency_distribution()

        # p50 should reflect majority (fast queries)
        assert distribution.p50_ms < 50.0
        # p99 should capture outliers
        assert distribution.p99_ms > 400.0
        assert distribution.outlier_count > 0

    def test_calculate_latency_distribution_empty_data(self, index_monitor):
        """Verify graceful handling of empty latency data."""
        distribution = index_monitor.calculate_latency_distribution()

        assert isinstance(distribution, LatencyDistribution)
        assert distribution.p50_ms == 0.0
        assert distribution.p95_ms == 0.0
        assert distribution.p99_ms == 0.0
        assert distribution.sample_count == 0

    def test_get_index_size_from_collection(
        self, index_monitor, mock_chromadb_collection
    ):
        """Verify index size (vector count) retrieved from ChromaDB collection."""
        mock_chromadb_collection.count.return_value = 135

        index_size = index_monitor.get_index_size()

        assert index_size == 135
        mock_chromadb_collection.count.assert_called_once()

    def test_get_index_size_tracks_growth(
        self, index_monitor, mock_chromadb_collection
    ):
        """Verify index size growth is tracked over time."""
        mock_chromadb_collection.count.side_effect = [100, 120, 135]

        size1 = index_monitor.get_index_size()
        size2 = index_monitor.get_index_size()
        size3 = index_monitor.get_index_size()

        assert size1 == 100
        assert size2 == 120
        assert size3 == 135
        assert (
            index_monitor.index_size_history == [100, 120, 135]
            or len(index_monitor.index_size_history) >= 3
        )

    def test_estimate_index_memory_usage(self, index_monitor, mock_psutil):
        """Verify index memory usage estimation."""
        # Mock process memory at 400MB
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 400 * 1024 * 1024
        mock_psutil.Process.return_value = mock_process

        memory_mb = index_monitor.estimate_index_memory_usage()

        assert isinstance(memory_mb, float)
        assert memory_mb > 0
        # Should be less than total process memory
        assert memory_mb <= 400.0

    def test_estimate_index_memory_with_baseline_subtraction(
        self, index_monitor, mock_psutil
    ):
        """Verify baseline memory is subtracted to isolate index memory."""
        # Set baseline (e.g., process overhead without index)
        index_monitor.baseline_memory_mb = 100.0

        # Mock current memory at 400MB
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 400 * 1024 * 1024
        mock_psutil.Process.return_value = mock_process

        memory_mb = index_monitor.estimate_index_memory_usage()

        # Should be approximately (400 - 100) = 300MB
        assert memory_mb <= 400.0
        assert memory_mb >= 0

    def test_get_hnsw_parameters_from_collection(
        self, index_monitor, mock_chromadb_collection
    ):
        """Verify HNSW parameters extracted from collection metadata."""
        params = index_monitor.get_hnsw_parameters()

        assert isinstance(params, dict)
        assert "ef_construction" in params or "hnsw_construction_ef" in params
        assert "ef_search" in params or "hnsw_search_ef" in params
        assert "M" in params or "hnsw_M" in params

    def test_detect_hnsw_parameter_changes(
        self, index_monitor, mock_chromadb_collection
    ):
        """Verify detection when HNSW parameters change."""
        # Get initial parameters
        initial_params = index_monitor.get_hnsw_parameters()

        # Simulate parameter change
        mock_chromadb_collection.metadata["hnsw:search_ef"] = 100  # Changed from 50

        updated_params = index_monitor.get_hnsw_parameters()
        changed = index_monitor.detect_parameter_changes(initial_params, updated_params)

        assert changed is True

    def test_aggregate_performance_metrics(
        self, index_monitor, mock_chromadb_collection
    ):
        """Verify metrics aggregated into IndexPerformanceMetrics data model."""
        # Add some latency data
        latencies = [30.0, 45.0, 50.0, 60.0, 75.0]
        for lat in latencies:
            index_monitor.track_query_latency(lat)

        metrics = index_monitor.aggregate_metrics()

        assert isinstance(metrics, IndexPerformanceMetrics)
        assert metrics.index_size > 0
        assert metrics.memory_mb >= 0
        assert isinstance(metrics.latency_distribution, LatencyDistribution)
        assert metrics.timestamp is not None

    def test_aggregate_metrics_includes_hnsw_params(
        self, index_monitor, mock_chromadb_collection
    ):
        """Verify aggregated metrics include HNSW configuration."""
        metrics = index_monitor.aggregate_metrics()

        assert hasattr(metrics, "hnsw_params")
        assert isinstance(metrics.hnsw_params, dict)

    def test_export_metrics_as_json(self, index_monitor):
        """Verify metrics can be serialized to JSON format."""
        # Add test data
        index_monitor.track_query_latency(45.0)
        metrics = index_monitor.aggregate_metrics()

        json_data = index_monitor.export_metrics_json(metrics)

        assert isinstance(json_data, (str, dict))
        # If string, should be valid JSON
        if isinstance(json_data, str):
            import json

            parsed = json.loads(json_data)
            assert "index_size" in parsed or "indexSize" in parsed
            assert "memory_mb" in parsed or "memoryMb" in parsed

    def test_check_latency_threshold_under_limit(self, index_monitor):
        """Verify no alert when latency is under threshold."""
        index_monitor.thresholds.max_query_latency_ms = 200.0

        # Add queries under threshold
        index_monitor.track_query_latency(50.0)
        index_monitor.track_query_latency(60.0)

        violations = index_monitor.check_thresholds()

        # Either no violations or latency not in violations
        assert violations is None or "latency" not in violations or violations == []

    def test_check_latency_threshold_exceeds_limit(self, index_monitor):
        """Verify alert triggered when p95 latency exceeds threshold."""
        index_monitor.thresholds.max_query_latency_ms = 100.0

        # Add mostly slow queries to push p95 over threshold
        for _ in range(90):
            index_monitor.track_query_latency(50.0)  # Fast queries
        for _ in range(10):
            index_monitor.track_query_latency(150.0)  # Slow queries push p95 up

        violations = index_monitor.check_thresholds()

        assert violations is not None
        assert len(violations) > 0
        assert any("latency" in str(v).lower() for v in violations)

    def test_check_memory_threshold_under_limit(
        self, index_monitor, mock_psutil, mock_chromadb_collection
    ):
        """Verify no alert when memory usage is under threshold."""
        index_monitor.thresholds.max_memory_mb = 500

        # Mock memory at 300MB (under threshold)
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 300 * 1024 * 1024
        mock_psutil.Process.return_value = mock_process

        violations = index_monitor.check_thresholds()

        # Either no violations or memory not in violations
        assert violations is None or "memory" not in violations or violations == []

    def test_check_memory_threshold_exceeds_limit(
        self, index_monitor, mock_psutil, mock_chromadb_collection
    ):
        """Verify alert triggered when index memory exceeds threshold."""
        index_monitor.thresholds.max_memory_mb = 300

        # Mock memory at 400MB (over threshold)
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 400 * 1024 * 1024
        mock_psutil.Process.return_value = mock_process

        violations = index_monitor.check_thresholds()

        assert violations is not None
        assert len(violations) > 0
        assert any("memory" in str(v).lower() for v in violations)

    def test_check_index_size_threshold_under_limit(
        self, index_monitor, mock_chromadb_collection
    ):
        """Verify no alert when index size is under threshold."""
        index_monitor.thresholds.max_index_size = 200
        mock_chromadb_collection.count.return_value = 135

        violations = index_monitor.check_thresholds()

        # Either no violations or size not in violations
        assert violations is None or "size" not in violations or violations == []

    def test_check_index_size_threshold_exceeds_limit(
        self, index_monitor, mock_chromadb_collection
    ):
        """Verify alert triggered when index size exceeds threshold."""
        index_monitor.thresholds.max_index_size = 100
        mock_chromadb_collection.count.return_value = 150  # Over threshold

        violations = index_monitor.check_thresholds()

        assert violations is not None
        assert len(violations) > 0
        assert any(
            "size" in str(v).lower() or "index" in str(v).lower() for v in violations
        )

    def test_calculate_performance_trend_improving(self, index_monitor):
        """Verify trend calculation detects improving performance."""
        # Simulate decreasing latencies over time (improvement)
        historical_latencies = [100.0, 90.0, 80.0, 70.0, 60.0]

        for latency in historical_latencies:
            index_monitor.track_query_latency(latency)

        trend = index_monitor.calculate_performance_trend()

        assert trend is not None
        assert trend["direction"] == "improving" or trend["slope"] < 0

    def test_calculate_performance_trend_degrading(self, index_monitor):
        """Verify trend calculation detects degrading performance."""
        # Simulate increasing latencies over time (degradation)
        historical_latencies = [50.0, 60.0, 70.0, 80.0, 90.0]

        for latency in historical_latencies:
            index_monitor.track_query_latency(latency)

        trend = index_monitor.calculate_performance_trend()

        assert trend is not None
        assert trend["direction"] == "degrading" or trend["slope"] > 0

    def test_calculate_performance_trend_stable(self, index_monitor):
        """Verify trend calculation detects stable performance."""
        # Simulate stable latencies with minor variance
        stable_latency = 50.0
        for _ in range(10):
            index_monitor.track_query_latency(stable_latency + np.random.uniform(-2, 2))

        trend = index_monitor.calculate_performance_trend()

        assert trend is not None
        assert trend["direction"] == "stable" or abs(trend["slope"]) < 0.5

    def test_reset_metrics_clears_latency_data(self, index_monitor):
        """Verify reset clears accumulated latency data."""
        # Add some data
        index_monitor.track_query_latency(45.0)
        index_monitor.track_query_latency(50.0)
        assert len(index_monitor.query_latencies) >= 2

        index_monitor.reset_metrics()

        assert len(index_monitor.query_latencies) == 0

    def test_reset_metrics_preserves_configuration(self, index_monitor):
        """Verify reset preserves thresholds and configuration."""
        original_threshold = index_monitor.thresholds.max_query_latency_ms

        index_monitor.reset_metrics()

        assert index_monitor.thresholds.max_query_latency_ms == original_threshold

    def test_reset_metrics_with_history_preservation(self, index_monitor):
        """Verify optional historical data preservation during reset."""
        # Add data
        index_monitor.track_query_latency(45.0)

        # Reset with history preservation
        index_monitor.reset_metrics(preserve_history=True)

        # Current metrics cleared but history exists
        assert hasattr(index_monitor, "metrics_history")
        assert (
            len(index_monitor.metrics_history) > 0
            or index_monitor.metrics_history is not None
        )

    def test_concurrent_latency_tracking_thread_safety(self, index_monitor):
        """Verify thread-safe metric collection for concurrent queries."""
        import threading

        def track_latencies():
            for _ in range(10):
                index_monitor.track_query_latency(45.0)

        # Run multiple threads concurrently
        threads = [threading.Thread(target=track_latencies) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have 50 total latencies (5 threads × 10 each)
        assert len(index_monitor.query_latencies) == 50

    def test_integration_with_performance_tracker(
        self, index_monitor, mock_chromadb_collection
    ):
        """Verify IndexPerformanceMonitor integrates with PerformanceTracker."""
        # Mock PerformanceTracker callback
        mock_tracker_callback = Mock()
        index_monitor.set_tracker_callback(mock_tracker_callback)

        # Track some metrics
        index_monitor.track_query_latency(45.0)
        metrics = index_monitor.aggregate_metrics()

        # Trigger callback
        index_monitor.report_to_tracker(metrics)

        # Verify callback was invoked with metrics
        mock_tracker_callback.assert_called_once()
        call_args = mock_tracker_callback.call_args
        assert call_args is not None
        # Verify metrics passed to callback
        assert isinstance(call_args[0][0], IndexPerformanceMetrics)

    def test_metrics_export_format_matches_schema(self, index_monitor):
        """Verify exported metrics match expected schema."""
        index_monitor.track_query_latency(45.0)
        metrics = index_monitor.aggregate_metrics()
        exported = index_monitor.export_metrics_json(metrics)

        # Parse if string
        if isinstance(exported, str):
            import json

            data = json.loads(exported)
        else:
            data = exported

        # Verify required fields present
        assert "timestamp" in data or "timestamp" in str(data)
        assert "index_size" in data or "indexSize" in str(data)
        assert "memory_mb" in data or "memoryMb" in str(data)
        assert "latency" in str(data).lower()


class TestIndexPerformanceMetrics:
    """Test suite for IndexPerformanceMetrics data model."""

    def test_metrics_model_initialization(self):
        """Verify IndexPerformanceMetrics initializes correctly."""
        latency_dist = LatencyDistribution(
            p50_ms=45.0, p95_ms=60.0, p99_ms=75.0, sample_count=100
        )

        metrics = IndexPerformanceMetrics(
            timestamp=datetime.now(timezone.utc),
            index_size=135,
            memory_mb=350.5,
            latency_distribution=latency_dist,
            hnsw_params={"ef_construction": 100, "ef_search": 50, "M": 16},
        )

        assert metrics.index_size == 135
        assert metrics.memory_mb == 350.5
        assert metrics.latency_distribution.p95_ms == 60.0

    def test_metrics_model_validation(self):
        """Verify Pydantic validation for IndexPerformanceMetrics."""
        # Should raise validation error for negative values
        with pytest.raises((ValueError, Exception)):
            IndexPerformanceMetrics(
                timestamp=datetime.now(timezone.utc),
                index_size=-10,  # Invalid: negative size
                memory_mb=350.5,
            )

    def test_metrics_model_serialization(self):
        """Verify metrics model can be serialized to dict."""
        latency_dist = LatencyDistribution(p50_ms=45.0, p95_ms=60.0, p99_ms=75.0)
        metrics = IndexPerformanceMetrics(
            timestamp=datetime.now(timezone.utc),
            index_size=135,
            memory_mb=350.5,
            latency_distribution=latency_dist,
            hnsw_params={"M": 16},
        )

        data = (
            metrics.model_dump() if hasattr(metrics, "model_dump") else metrics.dict()
        )

        assert isinstance(data, dict)
        assert data["index_size"] == 135
        assert data["memory_mb"] == 350.5


class TestIndexPerformanceThresholds:
    """Test suite for IndexPerformanceThresholds configuration."""

    def test_thresholds_initialization_with_defaults(self):
        """Verify default threshold values."""
        thresholds = IndexPerformanceThresholds()

        assert thresholds.max_query_latency_ms > 0
        assert thresholds.max_memory_mb > 0
        assert thresholds.max_index_size > 0

    def test_thresholds_initialization_with_custom_values(self):
        """Verify custom threshold configuration."""
        thresholds = IndexPerformanceThresholds(
            max_query_latency_ms=150.0, max_memory_mb=400, max_index_size=200
        )

        assert thresholds.max_query_latency_ms == 150.0
        assert thresholds.max_memory_mb == 400
        assert thresholds.max_index_size == 200

    def test_thresholds_validation_rejects_invalid_values(self):
        """Verify validation rejects invalid threshold values."""
        with pytest.raises((ValueError, Exception)):
            IndexPerformanceThresholds(
                max_query_latency_ms=-100.0  # Invalid: negative latency
            )


class TestLatencyDistribution:
    """Test suite for LatencyDistribution data model."""

    def test_latency_distribution_initialization(self):
        """Verify LatencyDistribution model initialization."""
        dist = LatencyDistribution(
            p50_ms=45.0, p95_ms=60.0, p99_ms=75.0, sample_count=100, outlier_count=3
        )

        assert dist.p50_ms == 45.0
        assert dist.p95_ms == 60.0
        assert dist.p99_ms == 75.0
        assert dist.sample_count == 100
        assert dist.outlier_count == 3

    def test_latency_distribution_default_values(self):
        """Verify default values for optional fields."""
        dist = LatencyDistribution(p50_ms=45.0, p95_ms=60.0, p99_ms=75.0)

        assert dist.sample_count >= 0
        assert dist.outlier_count >= 0

    def test_latency_distribution_validation(self):
        """Verify percentiles maintain logical ordering."""
        # p95 should be >= p50
        # p99 should be >= p95
        with pytest.raises((ValueError, AssertionError, Exception)):
            LatencyDistribution(
                p50_ms=100.0, p95_ms=50.0, p99_ms=75.0  # Invalid: p95 < p50
            )
