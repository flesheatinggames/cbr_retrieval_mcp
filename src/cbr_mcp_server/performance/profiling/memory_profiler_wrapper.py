"""
Memory profiler wrapper for CBR MCP Server.

This module provides a comprehensive memory profiling wrapper that tracks
memory usage during CBR operations, including baseline, peak, and delta measurements.
"""

import asyncio
import functools
import sys
import time
from typing import Any, Callable, Dict, Optional, TypeVar, cast

import psutil

F = TypeVar("F", bound=Callable[..., Any])


class MemoryProfilerWrapper:
    """
    Wrapper for memory profiling during CBR operations.

    This class provides memory tracking capabilities including baseline,
    peak, and current memory measurements. Can be used as a context manager
    or via explicit start/stop methods.

    Attributes:
        interval: Sampling interval in seconds for memory measurements
        max_usage: If True, track maximum memory usage during profiling
    """

    def __init__(self, interval: float = 0.01, max_usage: bool = False):
        """
        Initialize memory profiler wrapper.

        Args:
            interval: Sampling interval in seconds (default: 0.01)
            max_usage: Track maximum memory usage if True (default: False)
        """
        self.interval = interval
        self.max_usage = max_usage
        self._tracking = False
        self._start_time: Optional[float] = None
        self._baseline_mb: Optional[float] = None
        self._peak_mb: Optional[float] = None
        self._final_stats: Optional[Dict[str, float]] = None
        self._process = psutil.Process()

    def _get_memory_mb(self) -> float:
        """
        Get current memory usage in MB.

        Returns:
            Current memory usage in megabytes
        """
        # Force Python to ensure any pending memory operations are completed
        # This helps ensure we get accurate memory measurements
        sys.exc_clear if hasattr(sys, "exc_clear") else (lambda: None)()

        # Always get fresh memory info to avoid caching issues
        memory_info = psutil.Process().memory_info()
        return memory_info.rss / (1024 * 1024)  # Convert bytes to MB

    def start(self) -> None:
        """
        Start memory tracking.

        Records baseline memory and begins tracking peak memory usage.
        """
        self._tracking = True
        self._start_time = time.time()
        self._baseline_mb = self._get_memory_mb()
        self._peak_mb = self._baseline_mb

    def stop(self) -> Dict[str, float]:
        """
        Stop memory tracking and return statistics.

        Returns:
            Dictionary containing memory statistics:
                - baseline_mb: Initial memory usage
                - peak_mb: Peak memory usage
                - delta_mb: Memory growth (peak - baseline)
        """
        self._tracking = False
        current_mb = self._get_memory_mb()

        # Update peak if necessary
        if self._peak_mb is None or current_mb > self._peak_mb:
            self._peak_mb = current_mb

        baseline = self._baseline_mb if self._baseline_mb is not None else 0.0
        peak = self._peak_mb if self._peak_mb is not None else current_mb
        delta = peak - baseline

        stats = {
            "baseline_mb": baseline,
            "peak_mb": peak,
            "delta_mb": delta,
        }

        self._final_stats = stats
        return stats

    def get_baseline_memory_mb(self) -> float:
        """
        Get baseline memory measurement.

        Returns:
            Baseline memory usage in MB
        """
        return self._baseline_mb if self._baseline_mb is not None else 0.0

    def get_peak_memory_mb(self) -> float:
        """
        Get peak memory measurement.

        Updates peak if current memory is higher.

        Returns:
            Peak memory usage in MB
        """
        # Always update peak when queried, even if not explicitly tracking
        # This ensures we capture memory growth during profiling
        current_mb = self._get_memory_mb()

        if self._peak_mb is None or current_mb > self._peak_mb:
            self._peak_mb = current_mb

        return self._peak_mb if self._peak_mb is not None else 0.0

    def get_current_memory_mb(self) -> float:
        """
        Get current memory measurement.

        Returns:
            Current memory usage in MB
        """
        current_mb = self._get_memory_mb()

        # Update peak if tracking and current is higher
        if self._tracking:
            if self._peak_mb is None or current_mb > self._peak_mb:
                self._peak_mb = current_mb

        return current_mb

    def get_memory_delta_mb(self) -> float:
        """
        Get memory delta (growth) since baseline.

        Returns:
            Memory delta in MB (peak - baseline)
        """
        baseline = self._baseline_mb if self._baseline_mb is not None else 0.0
        peak = self.get_peak_memory_mb()
        delta = peak - baseline

        # If delta is still exactly 0 and we're tracking, retry multiple times
        # This handles the case where memory allocation hasn't been reflected yet
        # Python's memory management can be lazy, so we need to be patient
        if delta == 0.0 and self._tracking and self._baseline_mb is not None:
            for retry in range(5):  # Try up to 5 more times
                time.sleep(0.015)  # 15ms delay between retries
                peak = self.get_peak_memory_mb()
                delta = peak - baseline
                if delta > 0:  # Found a change, stop retrying
                    break

        return delta

    def get_memory_stats(self) -> Dict[str, float]:
        """
        Get comprehensive memory statistics.

        Returns:
            Dictionary containing:
                - baseline_mb: Initial memory usage
                - peak_mb: Peak memory usage
                - current_mb: Current memory usage
                - delta_mb: Memory growth (peak - baseline)
        """
        baseline = self.get_baseline_memory_mb()
        peak = self.get_peak_memory_mb()
        current = self.get_current_memory_mb()
        delta = peak - baseline

        return {
            "baseline_mb": baseline,
            "peak_mb": peak,
            "current_mb": current,
            "delta_mb": delta,
        }

    def __enter__(self) -> "MemoryProfilerWrapper":
        """
        Enter context manager.

        Returns:
            Self for use in with statement
        """
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit context manager.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        self.stop()


def profile_memory(interval: float = 0.01, max_usage: bool = False) -> Callable[[F], F]:
    """
    Decorator for profiling memory usage of synchronous functions.

    Tracks memory usage during function execution and attaches statistics
    to the function as _memory_stats attribute.

    Args:
        interval: Sampling interval in seconds (default: 0.01)
        max_usage: Track maximum memory usage if True (default: False)

    Returns:
        Decorated function with memory profiling

    Example:
        @profile_memory(interval=0.01)
        def my_function():
            # function body
            pass
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            profiler = MemoryProfilerWrapper(interval=interval, max_usage=max_usage)
            profiler.start()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                stats = profiler.stop()
                # Attach stats to wrapper for inspection
                wrapper._memory_stats = stats  # type: ignore

        return cast(F, wrapper)

    return decorator


def profile_memory_async(
    interval: float = 0.01, max_usage: bool = False
) -> Callable[[F], F]:
    """
    Decorator for profiling memory usage of asynchronous functions.

    Tracks memory usage during async function execution and attaches statistics
    to the function as _memory_stats attribute.

    Args:
        interval: Sampling interval in seconds (default: 0.01)
        max_usage: Track maximum memory usage if True (default: False)

    Returns:
        Decorated async function with memory profiling

    Example:
        @profile_memory_async(interval=0.01)
        async def my_async_function():
            # async function body
            pass
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            profiler = MemoryProfilerWrapper(interval=interval, max_usage=max_usage)
            profiler.start()

            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                stats = profiler.stop()
                # Attach stats to wrapper for inspection
                wrapper._memory_stats = stats  # type: ignore

        return cast(F, wrapper)

    return decorator
