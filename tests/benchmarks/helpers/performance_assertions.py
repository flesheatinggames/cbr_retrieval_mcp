"""
Performance assertion helpers for benchmark tests.

Provides reusable assertion utilities for validating performance metrics
in benchmark tests. Includes latency, memory, throughput, and cache hit rate
assertions with comprehensive error messages.
"""

from typing import Any, Dict, List
import statistics


def format_performance_message(
    metric: str, value: float, threshold: float, unit: str = ""
) -> str:
    """
    Format a performance assertion error message.

    Args:
        metric: Name of the performance metric
        value: Actual measured value
        threshold: Expected threshold value
        unit: Unit of measurement (e.g., 'ms', 'MB')

    Returns:
        Formatted error message string
    """
    unit_str = f" {unit}" if unit else ""
    return f"{metric} exceeded threshold: {value}{unit_str} > {threshold}{unit_str}"


def calculate_percentile(data: List[float], percentile: float) -> float:
    """
    Calculate a percentile from a list of values.

    Args:
        data: List of numeric values
        percentile: Percentile to calculate (0-100)

    Returns:
        The calculated percentile value

    Raises:
        ValueError: If data is empty or percentile is invalid
    """
    if not data:
        raise ValueError("Cannot calculate percentile of empty data")

    if percentile < 0 or percentile > 100:
        raise ValueError(f"Percentile must be between 0 and 100, got {percentile}")

    sorted_data = sorted(data)
    if len(sorted_data) == 1:
        return sorted_data[0]

    # Use linear interpolation method
    index = (percentile / 100) * (len(sorted_data) - 1)
    lower_index = int(index)
    upper_index = min(lower_index + 1, len(sorted_data) - 1)
    weight = index - lower_index

    return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight


def detect_outliers(
    measurements: List[float], threshold_std_dev: float = 2.0
) -> List[float]:
    """
    Detect outliers in measurements using standard deviation threshold.

    Args:
        measurements: List of measurement values
        threshold_std_dev: Number of standard deviations to consider as outlier

    Returns:
        List of outlier values

    Raises:
        ValueError: If measurements is empty
    """
    if not measurements:
        raise ValueError("Cannot detect outliers in empty measurements")

    if len(measurements) == 1:
        return []

    mean = statistics.mean(measurements)
    std_dev = statistics.stdev(measurements)

    if std_dev == 0:
        return []

    outliers = []
    for value in measurements:
        z_score = abs((value - mean) / std_dev)
        if z_score > threshold_std_dev:
            outliers.append(value)

    return outliers


# Latency Assertions


def assert_latency_under_threshold(
    latency_ms: float, threshold_ms: float, metric_name: str
) -> None:
    """
    Assert that latency is under a threshold.

    Args:
        latency_ms: Measured latency in milliseconds
        threshold_ms: Maximum acceptable latency in milliseconds
        metric_name: Name of the latency metric for error messages

    Raises:
        ValueError: If latency or threshold is negative
        AssertionError: If latency exceeds threshold
    """
    if latency_ms < 0:
        raise ValueError(f"Latency cannot be negative: {latency_ms}")

    if threshold_ms < 0:
        raise ValueError(f"Threshold cannot be negative: {threshold_ms}")

    if latency_ms > threshold_ms:
        message = format_performance_message(
            metric_name, latency_ms, threshold_ms, "ms"
        )
        raise AssertionError(message)


def assert_percentile_latency(
    stats: Dict[str, float], percentile: str, threshold_ms: float
) -> None:
    """
    Assert that a percentile latency is under a threshold.

    Args:
        stats: Dictionary containing percentile statistics (e.g., {'p50': 25.0, 'p95': 80.0})
        percentile: Percentile key to check (e.g., 'p50', 'p95', 'p99')
        threshold_ms: Maximum acceptable latency for this percentile

    Raises:
        KeyError: If percentile not found in stats
        AssertionError: If percentile latency exceeds threshold
    """
    latency_value = stats[percentile]  # Let KeyError propagate

    if latency_value > threshold_ms:
        message = format_performance_message(
            percentile, latency_value, threshold_ms, "ms"
        )
        raise AssertionError(message)


def assert_latency_distribution(
    stats: Dict[str, float], p50_max: float, p95_max: float, p99_max: float
) -> None:
    """
    Assert that latency distribution meets all percentile thresholds.

    Args:
        stats: Dictionary containing percentile statistics
        p50_max: Maximum acceptable p50 latency
        p95_max: Maximum acceptable p95 latency
        p99_max: Maximum acceptable p99 latency

    Raises:
        AssertionError: If any percentile exceeds its threshold
    """
    failures = []

    if stats.get("p50", 0) > p50_max:
        failures.append(f"p50: {stats['p50']}ms > {p50_max}ms")

    if stats.get("p95", 0) > p95_max:
        failures.append(f"p95: {stats['p95']}ms > {p95_max}ms")

    if stats.get("p99", 0) > p99_max:
        failures.append(f"p99: {stats['p99']}ms > {p99_max}ms")

    if failures:
        raise AssertionError(
            f"Latency distribution failed: {', '.join(failures)}"
        )


# Memory Assertions


def assert_memory_under_threshold(
    memory_mb: float, threshold_mb: float, metric_name: str
) -> None:
    """
    Assert that memory usage is under a threshold.

    Args:
        memory_mb: Measured memory in megabytes
        threshold_mb: Maximum acceptable memory in megabytes
        metric_name: Name of the memory metric for error messages

    Raises:
        ValueError: If memory or threshold is negative
        AssertionError: If memory exceeds threshold
    """
    if memory_mb < 0:
        raise ValueError(f"Memory cannot be negative: {memory_mb}")

    if threshold_mb < 0:
        raise ValueError(f"Threshold cannot be negative: {threshold_mb}")

    if memory_mb > threshold_mb:
        message = format_performance_message(
            metric_name, memory_mb, threshold_mb, "MB"
        )
        raise AssertionError(message)


def assert_memory_delta(
    baseline_mb: float, current_mb: float, max_delta_mb: float
) -> None:
    """
    Assert that memory increase is within acceptable delta.

    Args:
        baseline_mb: Baseline memory usage in megabytes
        current_mb: Current memory usage in megabytes
        max_delta_mb: Maximum acceptable memory increase

    Raises:
        AssertionError: If memory delta exceeds maximum
    """
    delta = current_mb - baseline_mb

    if delta > max_delta_mb:
        raise AssertionError(
            f"Memory delta exceeded threshold: baseline={baseline_mb}MB, "
            f"current={current_mb}MB, delta={delta}MB > max={max_delta_mb}MB"
        )


def assert_no_memory_leak(
    measurements: List[float], max_growth_pct: float
) -> None:
    """
    Assert that no memory leak is detected in measurements.

    Uses linear regression to detect upward memory growth trend.

    Args:
        measurements: List of memory measurements over time
        max_growth_pct: Maximum acceptable memory growth percentage

    Raises:
        ValueError: If measurements is empty
        AssertionError: If memory leak detected
    """
    if not measurements:
        raise ValueError("Cannot detect memory leak with empty measurements")

    if len(measurements) < 2:
        return  # Not enough data to detect leak

    first_value = measurements[0]
    last_value = measurements[-1]

    growth_pct = ((last_value - first_value) / first_value) * 100

    if growth_pct > max_growth_pct:
        raise AssertionError(
            f"Memory leak detected: growth={growth_pct:.2f}% exceeds "
            f"max={max_growth_pct}% (from {first_value}MB to {last_value}MB)"
        )


# Performance Metrics Assertions


def assert_cache_hit_rate(
    hits: int, misses: int, min_hit_rate_pct: float
) -> None:
    """
    Assert that cache hit rate meets minimum threshold.

    Args:
        hits: Number of cache hits
        misses: Number of cache misses
        min_hit_rate_pct: Minimum acceptable hit rate percentage

    Raises:
        ValueError: If total requests is zero
        AssertionError: If hit rate below minimum
    """
    total = hits + misses

    if total == 0:
        raise ValueError("Cannot calculate hit rate with zero requests")

    hit_rate = (hits / total) * 100

    if hit_rate < min_hit_rate_pct:
        raise AssertionError(
            f"Cache hit rate below minimum: {hit_rate:.1f}% < {min_hit_rate_pct}%"
        )


def assert_throughput(
    operations: int, duration_sec: float, min_ops_per_sec: float
) -> None:
    """
    Assert that throughput meets minimum threshold.

    Args:
        operations: Number of operations completed
        duration_sec: Duration in seconds
        min_ops_per_sec: Minimum acceptable operations per second

    Raises:
        ValueError: If duration is zero or negative, or operations is negative
        AssertionError: If throughput below minimum
    """
    if operations < 0:
        raise ValueError(f"Operations cannot be negative: {operations}")

    if duration_sec <= 0:
        raise ValueError(f"Duration must be positive: {duration_sec}")

    ops_per_sec = operations / duration_sec

    if ops_per_sec < min_ops_per_sec:
        raise AssertionError(
            f"Throughput below minimum: {ops_per_sec:.1f} ops/sec < {min_ops_per_sec} ops/sec"
        )


def assert_measurement_variance(
    measurements: List[float], max_cv_pct: float
) -> None:
    """
    Assert that measurement variance is within acceptable range.

    Uses coefficient of variation (CV) to measure variance.

    Args:
        measurements: List of measurement values
        max_cv_pct: Maximum acceptable coefficient of variation percentage

    Raises:
        ValueError: If measurements is empty
        AssertionError: If variance exceeds maximum
    """
    if not measurements:
        raise ValueError("Cannot calculate variance with empty measurements")

    if len(measurements) < 2:
        return  # Not enough data to calculate variance

    mean = statistics.mean(measurements)
    std_dev = statistics.stdev(measurements)

    if mean == 0:
        return  # Avoid division by zero

    cv_pct = (std_dev / mean) * 100

    if cv_pct > max_cv_pct:
        raise AssertionError(
            f"Measurement variance too high: CV={cv_pct:.2f}% > max={max_cv_pct}%"
        )
