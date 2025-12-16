"""
Performance metrics tracking module.

This module provides comprehensive performance monitoring capabilities including
query latency tracking, cache performance metrics, memory usage monitoring,
and threshold-based alerting.
"""

import json
import math
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass(frozen=True)
class MetricsSnapshot:
    """
    Immutable snapshot of metrics at a point in time.

    Attributes:
        timestamp: The time when the snapshot was taken
        metrics: Dictionary containing metric values
    """

    timestamp: datetime
    metrics: Dict[str, Any]


class PerformanceMetricsTracker:
    """
    Thread-safe tracker for performance metrics.

    Tracks query latency, cache hit/miss rates, and memory usage with
    support for time-windowed aggregation and percentile calculations.
    """

    def __init__(self):
        """Initialize an empty metrics tracker."""
        self._lock = threading.Lock()
        self._query_latencies: List[tuple[float, float]] = []  # (timestamp, latency)
        self._cache_hits = 0
        self._cache_misses = 0
        self._memory_samples: List[tuple[float, int]] = []  # (timestamp, bytes)
        self._memory_current = 0
        self._memory_peak = 0

    def record_query_latency(self, latency: float) -> None:
        """
        Record a query latency measurement.

        Args:
            latency: Query latency in seconds

        Raises:
            ValueError: If latency is negative
        """
        if latency < 0:
            raise ValueError("Latency cannot be negative")

        with self._lock:
            timestamp = time.time()
            self._query_latencies.append((timestamp, latency))

    def record_cache_hit(self) -> None:
        """Record a cache hit event."""
        with self._lock:
            self._cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record a cache miss event."""
        with self._lock:
            self._cache_misses += 1

    def record_memory_usage(self, bytes_used: int) -> None:
        """
        Record memory usage measurement.

        Args:
            bytes_used: Memory usage in bytes
        """
        with self._lock:
            timestamp = time.time()
            self._memory_current = bytes_used
            self._memory_peak = max(self._memory_peak, bytes_used)
            self._memory_samples.append((timestamp, bytes_used))

    def get_metrics_summary(
        self, window_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated metrics summary.

        Args:
            window_seconds: Optional time window in seconds. If provided,
                only metrics within this window are included.

        Returns:
            Dictionary containing all aggregated metrics
        """
        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - window_seconds if window_seconds else 0

            # Filter latencies by time window
            if window_seconds:
                latencies = [
                    lat for ts, lat in self._query_latencies if ts >= cutoff_time
                ]
            else:
                latencies = [lat for _, lat in self._query_latencies]

            # Calculate latency statistics
            latency_samples = len(latencies)
            if latencies:
                latency_min = min(latencies)
                latency_max = max(latencies)
                latency_avg = sum(latencies) / len(latencies)
                latency_p95 = self._calculate_percentile(latencies, 0.95)
                latency_p99 = self._calculate_percentile(latencies, 0.99)
            else:
                latency_min = latency_max = latency_avg = latency_p95 = latency_p99 = (
                    None
                )

            # Calculate cache statistics
            total_cache_accesses = self._cache_hits + self._cache_misses
            if total_cache_accesses > 0:
                cache_hit_rate = self._cache_hits / total_cache_accesses
            else:
                cache_hit_rate = 0.0

            # Memory statistics
            memory_samples = len(self._memory_samples)

            return {
                "query_count": latency_samples,
                "latency_min": latency_min,
                "latency_max": latency_max,
                "latency_avg": latency_avg,
                "latency_p95": latency_p95,
                "latency_p99": latency_p99,
                "latency_samples": latency_samples,
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "cache_hit_rate": cache_hit_rate,
                "memory_current": self._memory_current,
                "memory_peak": self._memory_peak,
                "memory_samples": memory_samples,
            }

    def reset_metrics(self) -> None:
        """Clear all tracked metrics."""
        with self._lock:
            self._query_latencies.clear()
            self._cache_hits = 0
            self._cache_misses = 0
            self._memory_samples.clear()
            self._memory_current = 0
            self._memory_peak = 0

    @staticmethod
    def _calculate_percentile(values: List[float], percentile: float) -> float:
        """
        Calculate percentile from a list of values.

        Args:
            values: List of numeric values
            percentile: Percentile to calculate (0.0 to 1.0)

        Returns:
            The percentile value
        """
        if not values:
            return None

        sorted_values = sorted(values)
        n = len(sorted_values)

        if n == 1:
            return sorted_values[0]

        # Use linear interpolation between closest ranks
        rank = percentile * (n - 1)
        lower_idx = int(math.floor(rank))
        upper_idx = int(math.ceil(rank))

        if lower_idx == upper_idx:
            return sorted_values[lower_idx]

        # Interpolate
        lower_value = sorted_values[lower_idx]
        upper_value = sorted_values[upper_idx]
        fraction = rank - lower_idx

        return lower_value + fraction * (upper_value - lower_value)


class MetricsExporter:
    """
    Exports performance metrics to various formats.

    Handles JSON serialization with special value handling and file export.
    """

    def export_to_json(
        self,
        metrics: Dict[str, Any],
        include_metadata: bool = False,
        pretty_print: bool = False,
    ) -> str:
        """
        Export metrics to JSON string.

        Args:
            metrics: Metrics dictionary to export
            include_metadata: Whether to include timestamp and version metadata
            pretty_print: Whether to format JSON with indentation

        Returns:
            JSON string representation of metrics
        """
        # Handle special values (NaN, Infinity)
        sanitized_metrics = self._sanitize_special_values(metrics)

        if include_metadata:
            export_data = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0.0",
                },
                **sanitized_metrics,
            }
        else:
            export_data = sanitized_metrics

        if pretty_print:
            return json.dumps(export_data, indent=2)
        else:
            return json.dumps(export_data)

    def export_to_file(self, metrics: Dict[str, Any], filepath: str | Path) -> None:
        """
        Export metrics to a JSON file.

        Args:
            filepath: Path where the file should be written

        Raises:
            PermissionError: If insufficient permissions to write file
            OSError: If other file system errors occur
        """
        filepath = Path(filepath) if isinstance(filepath, str) else filepath

        json_content = self.export_to_json(metrics, pretty_print=True)

        with open(filepath, "w") as f:
            f.write(json_content)

    @staticmethod
    def _sanitize_special_values(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert NaN and Infinity to JSON-serializable values.

        Args:
            data: Dictionary potentially containing special float values

        Returns:
            Dictionary with special values converted to None or strings
        """
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, float):
                if math.isnan(value):
                    sanitized[key] = None
                elif math.isinf(value):
                    sanitized[key] = None
                else:
                    sanitized[key] = value
            else:
                sanitized[key] = value
        return sanitized


class PerformanceAlertManager:
    """
    Manages performance threshold alerts.

    Allows registration of thresholds and triggers callbacks when
    metrics violate those thresholds. Includes cooldown mechanism
    to prevent alert spam.
    """

    def __init__(self, cooldown_seconds: int = 0):
        """
        Initialize alert manager.

        Args:
            cooldown_seconds: Minimum time between alerts for the same metric
        """
        self._thresholds: Dict[str, Dict[str, Any]] = {}
        self._alert_history: List[Dict[str, Any]] = []
        self._last_alert_time: Dict[str, float] = {}
        self._cooldown_seconds = cooldown_seconds
        self._lock = threading.Lock()

    def register_threshold(
        self,
        metric_name: str,
        threshold: float,
        comparison: str,
        callback: Optional[Callable] = None,
    ) -> None:
        """
        Register a threshold for a metric.

        Args:
            metric_name: Name of the metric to monitor
            threshold: Threshold value
            comparison: Comparison operator ('gt', 'lt', 'gte', 'lte', 'eq')
            callback: Optional function to call when threshold is violated
        """
        with self._lock:
            self._thresholds[metric_name] = {
                "threshold": threshold,
                "comparison": comparison,
                "callback": callback,
            }

    def check_thresholds(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check metrics against registered thresholds.

        Args:
            metrics: Dictionary of current metric values

        Returns:
            List of threshold violations
        """
        violations = []
        current_time = time.time()

        with self._lock:
            for metric_name, threshold_config in self._thresholds.items():
                if metric_name not in metrics:
                    continue

                value = metrics[metric_name]
                threshold = threshold_config["threshold"]
                comparison = threshold_config["comparison"]
                callback = threshold_config.get("callback")

                # Check if threshold is violated
                is_violated = self._compare(value, threshold, comparison)

                if is_violated:
                    # Check cooldown
                    last_alert_time = self._last_alert_time.get(metric_name, 0)
                    if current_time - last_alert_time < self._cooldown_seconds:
                        # Skip due to cooldown
                        continue

                    # Record violation
                    violation = {
                        "metric": metric_name,
                        "value": value,
                        "threshold": threshold,
                        "comparison": comparison,
                        "timestamp": datetime.now(),
                    }
                    violations.append(violation)
                    self._alert_history.append(violation)
                    self._last_alert_time[metric_name] = current_time

                    # Trigger callback
                    if callback:
                        callback()

        return violations

    def get_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered thresholds.

        Returns:
            Dictionary mapping metric names to threshold configurations
        """
        with self._lock:
            return dict(self._thresholds)

    def get_alert_history(self) -> List[Dict[str, Any]]:
        """
        Get history of all alerts.

        Returns:
            List of alert records
        """
        with self._lock:
            return list(self._alert_history)

    def clear_alert_history(self) -> None:
        """Clear the alert history."""
        with self._lock:
            self._alert_history.clear()

    @staticmethod
    def _compare(value: float, threshold: float, operator: str) -> bool:
        """
        Compare a value against a threshold using the specified operator.

        Args:
            value: The value to compare
            threshold: The threshold to compare against
            operator: Comparison operator ('gt', 'lt', 'gte', 'lte', 'eq')

        Returns:
            True if the comparison is satisfied, False otherwise
        """
        if operator == "gt":
            return value > threshold
        elif operator == "lt":
            return value < threshold
        elif operator == "gte":
            return value >= threshold
        elif operator == "lte":
            return value <= threshold
        elif operator == "eq":
            return value == threshold
        else:
            raise ValueError(f"Unknown comparison operator: {operator}")
