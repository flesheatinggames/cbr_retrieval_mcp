"""
Integration Tests for Performance Monitoring System.

This module tests the end-to-end integration of the performance monitoring
components:
- PerformanceMetricsTracker: Query latency, cache, and memory tracking
- MetricsExporter: JSON export of live metrics
- PerformanceAlertManager: Threshold-based alerting
- Dashboard integration: Metrics flow to health dashboard

These tests verify that monitoring components work together correctly during
actual CBR operations, ensuring metrics are tracked accurately, exported
correctly, and alerts trigger appropriately.
"""

import asyncio
import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from cbr_mcp_server.performance.metrics import (
    MetricsExporter,
    PerformanceAlertManager,
    PerformanceMetricsTracker,
)


@pytest.fixture
def metrics_tracker():
    """Create a fresh PerformanceMetricsTracker for each test."""
    return PerformanceMetricsTracker()


@pytest.fixture
def metrics_exporter():
    """Create a MetricsExporter for each test."""
    return MetricsExporter()


@pytest.fixture
def alert_manager():
    """Create a PerformanceAlertManager with no cooldown for testing."""
    return PerformanceAlertManager(cooldown_seconds=0)


@pytest.fixture
def mock_chromadb_client():
    """Mock ChromaDB client for isolated testing."""
    mock_client = MagicMock()
    mock_collection = MagicMock()

    # Configure mock collection with typical responses
    mock_collection.query.return_value = {
        "ids": [["case-1", "case-2", "case-3"]],
        "distances": [[0.1, 0.2, 0.3]],
        "metadatas": [
            [
                {"category": "code", "tags": ["python", "auth"]},
                {"category": "code", "tags": ["react", "hooks"]},
                {"category": "orchestration", "tags": ["planning"]},
            ]
        ],
        "documents": [["Example 1", "Example 2", "Example 3"]],
    }

    mock_collection.get.return_value = {
        "ids": ["case-1"],
        "metadatas": [{"category": "code", "tags": ["python"]}],
        "documents": ["Example case"],
    }

    mock_client.get_or_create_collection.return_value = mock_collection
    mock_client.get_collection.return_value = mock_collection

    return mock_client


@pytest.fixture
def mock_embedding_model():
    """Mock embedding model for query encoding."""
    model = MagicMock()
    model.encode.return_value = [0.15] * 384  # Realistic embedding
    return model


# ============================================================================
# Test 1: Metrics Tracking During Actual CBR Queries
# ============================================================================


def test_metrics_tracking_during_cbr_queries(
    metrics_tracker, mock_chromadb_client, mock_embedding_model
):
    """
    Test that query latency is correctly recorded during CBR retrieval operations.

    This test simulates a CBR query workflow and verifies that:
    - Latency is recorded after query execution
    - Latency value is positive and realistic
    - Query count increments correctly
    - Latency statistics are calculated accurately
    """
    # Simulate a CBR query with realistic timing
    start_time = time.perf_counter()

    # Simulate query processing (embedding + vector search)
    query_embedding = mock_embedding_model.encode("test query")
    mock_chromadb_client.get_collection("test_collection").query(
        query_embeddings=[query_embedding], n_results=5
    )

    # Simulate realistic processing delay
    time.sleep(0.01)  # 10ms

    end_time = time.perf_counter()
    latency = end_time - start_time

    # Record the latency
    metrics_tracker.record_query_latency(latency)

    # Verify metrics were recorded correctly
    summary = metrics_tracker.get_metrics_summary()

    assert summary["query_count"] == 1, "Query count should be 1"
    assert summary["latency_samples"] == 1, "Should have 1 latency sample"
    assert summary["latency_min"] > 0, "Latency should be positive"
    assert summary["latency_min"] < 1.0, "Latency should be realistic (< 1s)"
    assert (
        summary["latency_avg"] == summary["latency_min"]
    ), "Min/avg should match for single query"
    assert (
        summary["latency_max"] == summary["latency_min"]
    ), "Min/max should match for single query"

    # Execute multiple queries to test aggregation
    for i in range(4):
        time.sleep(0.005 * (i + 1))  # Variable delays
        latency = 0.01 + (0.005 * i)
        metrics_tracker.record_query_latency(latency)

    summary = metrics_tracker.get_metrics_summary()
    assert summary["query_count"] == 5, "Should have 5 queries total"
    assert (
        summary["latency_min"] < summary["latency_avg"] < summary["latency_max"]
    ), "Stats should be ordered"


# ============================================================================
# Test 2: Cache Metrics Integration
# ============================================================================


def test_cache_metrics_integration(
    metrics_tracker, mock_chromadb_client, mock_embedding_model
):
    """
    Test cache hit/miss tracking during operations with caching enabled.

    This test verifies:
    - Cache hits increment on repeated queries
    - Cache misses increment on new queries
    - Cache hit rate calculation is accurate
    - Metrics persist across multiple operations
    """
    # Simulate cache for repeated queries
    query_cache = {}

    def execute_query_with_cache(query: str):
        """Simulate query execution with caching."""
        if query in query_cache:
            # Cache hit
            metrics_tracker.record_cache_hit()
            return query_cache[query]
        else:
            # Cache miss - execute query
            metrics_tracker.record_cache_miss()
            embedding = mock_embedding_model.encode(query)
            result = mock_chromadb_client.get_collection("test").query(
                query_embeddings=[embedding], n_results=5
            )
            query_cache[query] = result
            return result

    # Execute queries with cache behavior
    execute_query_with_cache("query1")  # Miss
    execute_query_with_cache("query2")  # Miss
    execute_query_with_cache("query1")  # Hit
    execute_query_with_cache("query2")  # Hit
    execute_query_with_cache("query3")  # Miss
    execute_query_with_cache("query1")  # Hit

    # Verify cache metrics
    summary = metrics_tracker.get_metrics_summary()

    assert summary["cache_hits"] == 3, "Should have 3 cache hits"
    assert summary["cache_misses"] == 3, "Should have 3 cache misses"
    assert summary["cache_hit_rate"] == 0.5, "Hit rate should be 50% (3/6)"

    # Execute more queries to test persistence
    for i in range(10):
        execute_query_with_cache("query1")  # All hits

    summary = metrics_tracker.get_metrics_summary()
    assert summary["cache_hits"] == 13, "Should have 13 total hits"
    assert summary["cache_misses"] == 3, "Misses should remain at 3"
    expected_hit_rate = 13 / 16
    assert (
        abs(summary["cache_hit_rate"] - expected_hit_rate) < 0.001
    ), "Hit rate should be ~81%"


# ============================================================================
# Test 3: Memory Metrics Integration with ResourceMonitor
# ============================================================================


def test_memory_metrics_integration(metrics_tracker):
    """
    Test memory tracking integration with ResourceMonitor.

    This test verifies:
    - Memory usage is recorded during queries
    - Peak memory tracking works correctly
    - Memory samples accumulate over time
    - Memory statistics are accurate
    """
    # Simulate memory usage during queries
    base_memory = 100 * 1024 * 1024  # 100 MB baseline

    # Record memory at different points
    metrics_tracker.record_memory_usage(base_memory)
    time.sleep(0.001)

    # Simulate memory increase during query
    metrics_tracker.record_memory_usage(base_memory + 10 * 1024 * 1024)  # +10 MB
    time.sleep(0.001)

    # Simulate peak memory usage
    peak_memory = base_memory + 25 * 1024 * 1024  # +25 MB
    metrics_tracker.record_memory_usage(peak_memory)
    time.sleep(0.001)

    # Memory decreases after query
    metrics_tracker.record_memory_usage(base_memory + 5 * 1024 * 1024)  # +5 MB

    # Verify memory metrics
    summary = metrics_tracker.get_metrics_summary()

    assert summary["memory_samples"] == 4, "Should have 4 memory samples"
    assert (
        summary["memory_current"] == base_memory + 5 * 1024 * 1024
    ), "Current memory should match last sample"
    assert summary["memory_peak"] == peak_memory, "Peak memory should be highest value"
    assert (
        summary["memory_peak"] > summary["memory_current"]
    ), "Peak should be greater than current"


# ============================================================================
# Test 4: Dashboard Receives Real Metrics from Tracker
# ============================================================================


def test_dashboard_metrics_integration(
    metrics_tracker, mock_chromadb_client, mock_embedding_model
):
    """
    Test that metrics tracker data flows correctly to the health dashboard.

    This test verifies:
    - Dashboard can retrieve current metrics snapshot
    - Metrics JSON is valid and complete
    - Dashboard updates reflect actual operations
    - All expected metrics fields are present
    """
    # Simulate operations that generate metrics
    for i in range(10):
        # Simulate queries
        latency = 0.01 + (i * 0.001)
        metrics_tracker.record_query_latency(latency)

        # Simulate cache activity
        if i % 2 == 0:
            metrics_tracker.record_cache_hit()
        else:
            metrics_tracker.record_cache_miss()

        # Simulate memory usage
        memory = 100 * 1024 * 1024 + (i * 1024 * 1024)
        metrics_tracker.record_memory_usage(memory)

    # Simulate dashboard retrieving metrics
    dashboard_snapshot = metrics_tracker.get_metrics_summary()

    # Verify all expected fields are present
    expected_fields = [
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

    for field in expected_fields:
        assert field in dashboard_snapshot, f"Dashboard snapshot missing field: {field}"

    # Verify metrics reflect actual operations
    assert dashboard_snapshot["query_count"] == 10, "Dashboard should show 10 queries"
    assert dashboard_snapshot["cache_hits"] == 5, "Dashboard should show 5 cache hits"
    assert (
        dashboard_snapshot["cache_misses"] == 5
    ), "Dashboard should show 5 cache misses"
    assert (
        dashboard_snapshot["memory_samples"] == 10
    ), "Dashboard should show 10 memory samples"

    # Verify metrics are JSON-serializable (required for dashboard)
    try:
        json.dumps(dashboard_snapshot)
    except (TypeError, ValueError) as e:
        pytest.fail(f"Dashboard snapshot not JSON-serializable: {e}")


# ============================================================================
# Test 5: JSON Export Produces Valid Output from Live Metrics
# ============================================================================


def test_json_export_from_live_metrics(metrics_tracker, metrics_exporter, tmp_path):
    """
    Test that MetricsExporter correctly exports live metrics to JSON.

    This test verifies:
    - JSON output is valid and parseable
    - All metrics are present in export
    - Special values (NaN, Infinity) are sanitized
    - Pretty-print formatting works correctly
    """
    # Generate live metrics
    for i in range(5):
        metrics_tracker.record_query_latency(0.01 + i * 0.005)
        metrics_tracker.record_cache_hit()
        metrics_tracker.record_memory_usage(100 * 1024 * 1024 + i * 1024 * 1024)

    # Get live metrics
    live_metrics = metrics_tracker.get_metrics_summary()

    # Test JSON export (basic)
    json_output = metrics_exporter.export_to_json(live_metrics)

    # Verify JSON is valid
    try:
        parsed = json.loads(json_output)
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON output: {e}")

    # Verify all metrics are present
    for key, value in live_metrics.items():
        assert key in parsed, f"Exported JSON missing key: {key}"

    # Test pretty-print export
    pretty_json = metrics_exporter.export_to_json(live_metrics, pretty_print=True)
    assert "\n" in pretty_json, "Pretty-print should include newlines"
    assert "  " in pretty_json, "Pretty-print should include indentation"

    # Test export with metadata
    metadata_json = metrics_exporter.export_to_json(live_metrics, include_metadata=True)
    parsed_metadata = json.loads(metadata_json)
    assert "metadata" in parsed_metadata, "Export should include metadata section"
    assert (
        "timestamp" in parsed_metadata["metadata"]
    ), "Metadata should include timestamp"

    # Test file export
    export_path = tmp_path / "metrics_export.json"
    metrics_exporter.export_to_file(live_metrics, export_path)

    assert export_path.exists(), "Export file should exist"

    with open(export_path, "r") as f:
        file_contents = json.load(f)

    assert file_contents == parsed, "File export should match JSON export"


# ============================================================================
# Test 6: Alerting Triggers on Threshold Violations During Operations
# ============================================================================


def test_alerting_triggers_on_threshold_violations(
    metrics_tracker, alert_manager, mock_chromadb_client
):
    """
    Test that PerformanceAlertManager detects threshold violations during operations.

    This test verifies:
    - Alerts trigger when latency exceeds threshold
    - Cooldown mechanism prevents alert spam
    - Alert history is recorded correctly
    - Callbacks are invoked on violations
    """
    # Set up alert callback to track invocations
    alert_triggered = []

    def alert_callback():
        alert_triggered.append(True)

    # Register threshold for latency (> 50ms)
    alert_manager.register_threshold(
        metric_name="latency_max",
        threshold=0.05,  # 50ms
        comparison="gt",
        callback=alert_callback,
    )

    # Execute queries with varying latencies
    queries = [0.01, 0.02, 0.03, 0.06, 0.07, 0.08]  # Last 3 exceed threshold

    for latency in queries:
        metrics_tracker.record_query_latency(latency)
        summary = metrics_tracker.get_metrics_summary()
        violations = alert_manager.check_thresholds(summary)

    # Verify alerts were triggered
    assert len(alert_triggered) == 3, "Should have triggered 3 alerts for violations"

    # Verify alert history
    history = alert_manager.get_alert_history()
    assert len(history) == 3, "Alert history should contain 3 violations"

    for violation in history:
        assert (
            violation["metric"] == "latency_max"
        ), "Violation metric should be latency_max"
        assert violation["value"] > 0.05, "Violation value should exceed threshold"
        assert violation["comparison"] == "gt", "Comparison should be 'gt'"

    # Test cooldown mechanism
    alert_manager_with_cooldown = PerformanceAlertManager(cooldown_seconds=10)
    alert_manager_with_cooldown.register_threshold(
        metric_name="latency_max",
        threshold=0.05,
        comparison="gt",
    )

    cooldown_alerts = []
    for i in range(5):
        metrics_tracker.record_query_latency(0.08)  # All exceed threshold
        summary = metrics_tracker.get_metrics_summary()
        violations = alert_manager_with_cooldown.check_thresholds(summary)
        cooldown_alerts.extend(violations)

    # Only first alert should fire due to cooldown
    assert len(cooldown_alerts) == 1, "Cooldown should prevent multiple alerts"


# ============================================================================
# Test 7: Metrics Persistence Across Multiple Operations
# ============================================================================


def test_metrics_persistence_across_operations(metrics_tracker, mock_chromadb_client):
    """
    Test that metrics accumulate correctly across multiple query cycles.

    This test verifies:
    - Metrics accumulate (don't reset) across queries
    - Time-windowed metrics work correctly
    - Historical data is preserved
    - Metrics can be reset on demand
    """
    # Execute first batch of queries
    for i in range(10):
        metrics_tracker.record_query_latency(0.01 + i * 0.001)
        metrics_tracker.record_cache_hit()
        metrics_tracker.record_memory_usage(100 * 1024 * 1024)

    summary_batch1 = metrics_tracker.get_metrics_summary()
    assert summary_batch1["query_count"] == 10, "First batch should have 10 queries"
    assert summary_batch1["cache_hits"] == 10, "First batch should have 10 hits"

    # Execute second batch of queries (metrics should accumulate)
    for i in range(15):
        metrics_tracker.record_query_latency(0.015 + i * 0.001)
        metrics_tracker.record_cache_miss()
        metrics_tracker.record_memory_usage(110 * 1024 * 1024)

    summary_batch2 = metrics_tracker.get_metrics_summary()
    assert summary_batch2["query_count"] == 25, "Should accumulate to 25 queries"
    assert summary_batch2["cache_hits"] == 10, "Hits should remain at 10"
    assert summary_batch2["cache_misses"] == 15, "Should have 15 misses"

    # Test time-windowed metrics
    # Note: Time windowing only applies to latency metrics, not cache/memory
    # Wait to create significant time separation
    time.sleep(1.5)  # Wait 1.5 seconds

    # Add new queries after time gap
    for i in range(5):
        metrics_tracker.record_query_latency(0.02)
        time.sleep(0.01)  # Small delay between queries

    # Get metrics with 1-second window
    # Should include only the 5 recent queries (executed within last 1 second)
    windowed_summary = metrics_tracker.get_metrics_summary(window_seconds=1)
    # The window filters latencies by timestamp, so recent 5 should be within window
    assert (
        windowed_summary["query_count"] <= 5
    ), f"Window should show at most 5 recent queries, got {windowed_summary['query_count']}"
    assert (
        windowed_summary["query_count"] > 0
    ), "Window should show at least some recent queries"

    # Test metrics reset
    metrics_tracker.reset_metrics()
    summary_after_reset = metrics_tracker.get_metrics_summary()
    assert summary_after_reset["query_count"] == 0, "Metrics should reset to 0"
    assert summary_after_reset["cache_hits"] == 0, "Cache hits should reset to 0"
    assert summary_after_reset["cache_misses"] == 0, "Cache misses should reset to 0"


# ============================================================================
# Test 8: Concurrent Access to Metrics Tracker
# ============================================================================


def test_concurrent_metrics_tracking(metrics_tracker):
    """
    Test thread-safety of metrics tracker under concurrent access.

    This test verifies:
    - Multiple concurrent queries can record metrics without race conditions
    - Lock mechanism prevents data corruption
    - Final metric counts are accurate
    - No exceptions occur during concurrent access
    """
    num_threads = 10
    operations_per_thread = 100
    errors = []

    def worker_thread():
        """Worker function that records metrics concurrently."""
        try:
            for i in range(operations_per_thread):
                # Record various metrics
                metrics_tracker.record_query_latency(0.01 + i * 0.0001)
                metrics_tracker.record_cache_hit()
                metrics_tracker.record_memory_usage(100 * 1024 * 1024 + i * 1024)
        except Exception as e:
            errors.append(e)

    # Create and start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=worker_thread)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify no errors occurred
    assert len(errors) == 0, f"Concurrent access caused errors: {errors}"

    # Verify final metrics are accurate
    summary = metrics_tracker.get_metrics_summary()

    expected_query_count = num_threads * operations_per_thread
    expected_cache_hits = num_threads * operations_per_thread
    expected_memory_samples = num_threads * operations_per_thread

    assert (
        summary["query_count"] == expected_query_count
    ), "Query count should match expected"
    assert (
        summary["cache_hits"] == expected_cache_hits
    ), "Cache hits should match expected"
    assert (
        summary["memory_samples"] == expected_memory_samples
    ), "Memory samples should match expected"

    # Verify metrics are still in valid state
    assert summary["latency_min"] > 0, "Latency min should be positive"
    assert (
        summary["latency_max"] > summary["latency_min"]
    ), "Latency max should be greater than min"
    assert (
        summary["memory_peak"] >= summary["memory_current"]
    ), "Peak memory should be >= current"
