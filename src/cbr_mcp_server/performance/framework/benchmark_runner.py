"""
Benchmark Runner Module for Performance Testing.

This module provides the core infrastructure for executing benchmarks,
collecting timing metrics, and managing benchmark suites.
"""

import logging
import platform
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkConfig:
    """
    Configuration for benchmark execution.

    Attributes:
        iterations: Number of benchmark iterations to run
        warmup_iterations: Number of warmup rounds before actual benchmark
        timeout_seconds: Maximum execution time in seconds
        collect_memory: Whether to collect memory usage metrics
        collect_cpu: Whether to collect CPU usage metrics
        max_retries: Maximum number of retry attempts on failure
        concurrent: Whether to support concurrent execution
    """

    iterations: int = 100
    warmup_iterations: int = 10
    timeout_seconds: float = 60.0
    collect_memory: bool = True
    collect_cpu: bool = True
    max_retries: int = 0
    concurrent: bool = False

    def __post_init__(self):
        """Validate configuration parameters."""
        if self.iterations <= 0:
            raise ValueError("iterations must be positive")
        if self.warmup_iterations < 0:
            raise ValueError("warmup_iterations must be non-negative")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


@dataclass
class BenchmarkResult:
    """
    Results from a benchmark execution.

    Attributes:
        name: Name of the benchmark
        mean_ms: Mean execution time in milliseconds
        median_ms: Median execution time in milliseconds
        p95_ms: 95th percentile execution time in milliseconds
        p99_ms: 99th percentile execution time in milliseconds
        timestamp: When the benchmark was executed
        metadata: Additional metadata about the benchmark run
        memory_mb: Memory usage in MB (if collected)
    """

    name: str
    mean_ms: float
    median_ms: float
    p95_ms: float
    p99_ms: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    memory_mb: Optional[float] = None


class Benchmark:
    """
    Wrapper for benchmark functions.

    Wraps a callable function to make it executable as a benchmark
    with associated configuration and metadata.
    """

    def __init__(
        self,
        func: Callable,
        name: str,
        config: Optional[BenchmarkConfig] = None,
        tags: Optional[List[str]] = None,
    ):
        """
        Initialize a Benchmark.

        Args:
            func: The callable function to benchmark
            name: Name of the benchmark
            config: Optional configuration for this specific benchmark
            tags: Optional tags for categorization
        """
        self.func = func
        self.name = name
        self.config = config or BenchmarkConfig()
        self.tags = tags or []

    def __call__(self, *args, **kwargs):
        """Execute the benchmark function."""
        return self.func(*args, **kwargs)


class BenchmarkRunner:
    """
    Executes benchmarks and collects results.

    The BenchmarkRunner manages benchmark execution, including warmup rounds,
    timing measurement, statistical analysis, and resource monitoring.
    """

    def __init__(self, config: Optional[BenchmarkConfig] = None):
        """
        Initialize the BenchmarkRunner.

        Args:
            config: Optional configuration. If None, uses default config.
        """
        self.config = config or BenchmarkConfig()

    def run_single_benchmark(
        self,
        benchmark_func: Callable,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
        continue_on_error: bool = False,
    ) -> BenchmarkResult:
        """
        Run a single benchmark function and collect results.

        Args:
            benchmark_func: The function to benchmark
            name: Name of the benchmark
            metadata: Optional custom metadata
            continue_on_error: If True, return result with error info instead of raising

        Returns:
            BenchmarkResult with timing and metadata

        Raises:
            TimeoutError: If benchmark exceeds timeout
            RuntimeError: If benchmark fails and continue_on_error is False
        """
        result_metadata = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "warmup_iterations": self.config.warmup_iterations,
        }
        if metadata:
            result_metadata.update(metadata)

        retry_count = 0
        last_error = None
        timings: List[float] = []

        # If retries are configured, use retry attempts as benchmark iterations
        if self.config.max_retries > 0:
            while retry_count <= self.config.max_retries:
                try:
                    # Time single execution
                    iter_start = time.perf_counter()
                    benchmark_func()
                    iter_end = time.perf_counter()
                    timings.append((iter_end - iter_start) * 1000)
                    break  # Success
                except Exception as e:
                    last_error = e
                    if retry_count < self.config.max_retries:
                        retry_count += 1
                        logger.warning(
                            f"Benchmark '{name}' failed (attempt {retry_count}), retrying..."
                        )
                        continue
                    else:
                        if continue_on_error:
                            return BenchmarkResult(
                                name=name,
                                mean_ms=0.0,
                                median_ms=0.0,
                                p95_ms=0.0,
                                p99_ms=0.0,
                                timestamp=datetime.now(),
                                metadata={
                                    **result_metadata,
                                    "error": str(last_error),
                                    "retry_count": retry_count,
                                },
                            )
                        else:
                            raise

            # Calculate statistics from retry attempts
            mean_ms = statistics.mean(timings) if timings else 0.0
            median_ms = statistics.median(timings) if timings else 0.0
            p95_ms = timings[0] if timings else 0.0
            p99_ms = timings[0] if timings else 0.0

        else:
            # Normal benchmark execution without retries
            # Warmup phase
            warmup_start = time.time()
            for _ in range(self.config.warmup_iterations):
                if time.time() - warmup_start > self.config.timeout_seconds:
                    raise TimeoutError(
                        f"Benchmark '{name}' exceeded timeout during warmup"
                    )
                benchmark_func()

            # Actual benchmark iterations
            start_time = time.time()

            for _ in range(self.config.iterations):
                # Check timeout
                if time.time() - start_time > self.config.timeout_seconds:
                    raise TimeoutError(
                        f"Benchmark '{name}' exceeded timeout of {self.config.timeout_seconds}s"
                    )

                # Time single iteration
                iter_start = time.perf_counter()
                benchmark_func()
                iter_end = time.perf_counter()

                timings.append((iter_end - iter_start) * 1000)  # Convert to ms

            # Calculate statistics
            mean_ms = statistics.mean(timings)
            median_ms = statistics.median(timings)
            sorted_timings = sorted(timings)
            p95_ms = sorted_timings[int(len(sorted_timings) * 0.95)]
            p99_ms = sorted_timings[int(len(sorted_timings) * 0.99)]

        # Collect memory if enabled
        memory_mb = None
        if self.config.collect_memory:
            try:
                memory_mb = get_memory_usage()
            except Exception as e:
                logger.warning(f"Failed to collect memory: {e}")

        # Collect CPU if enabled
        if self.config.collect_cpu:
            try:
                cpu_usage = get_cpu_usage()
                result_metadata["cpu_usage"] = cpu_usage
            except Exception as e:
                logger.warning(f"Failed to collect CPU: {e}")

        if retry_count > 0:
            result_metadata["retry_count"] = retry_count

        return BenchmarkResult(
            name=name,
            mean_ms=mean_ms,
            median_ms=median_ms,
            p95_ms=p95_ms,
            p99_ms=p99_ms,
            timestamp=datetime.now(),
            metadata=result_metadata,
            memory_mb=memory_mb,
        )

    def run_benchmark_suite(self, suite: "BenchmarkSuite") -> List[BenchmarkResult]:
        """
        Run all benchmarks in a suite.

        Args:
            suite: The BenchmarkSuite to execute

        Returns:
            List of BenchmarkResult objects
        """
        results: List[BenchmarkResult] = []
        benchmarks = suite.get_benchmarks()

        for i, benchmark in enumerate(benchmarks, 1):
            logger.info(f"Running benchmark {i}/{len(benchmarks)}: {benchmark.name}")
            result = self.run_single_benchmark(
                benchmark_func=benchmark.func,
                name=benchmark.name,
            )
            results.append(result)

        return results

    def run_concurrent_benchmarks(
        self, benchmarks: List[Tuple[Callable, str]]
    ) -> List[BenchmarkResult]:
        """
        Run multiple benchmarks concurrently.

        Args:
            benchmarks: List of (function, name) tuples

        Returns:
            List of BenchmarkResult objects
        """
        if not self.config.concurrent:
            raise ValueError("Concurrent execution not enabled in config")

        results: List[BenchmarkResult] = []

        # Use ThreadPoolExecutor with max_workers equal to number of benchmarks
        with ThreadPoolExecutor(max_workers=len(benchmarks)) as executor:
            # Submit all benchmarks at once
            future_to_name = {
                executor.submit(self.run_single_benchmark, func, name): name
                for func, name in benchmarks
            }

            # Collect results as they complete
            for future in as_completed(future_to_name):
                results.append(future.result())

        return results


class BenchmarkSuite:
    """
    Collection of benchmarks to run together.

    A BenchmarkSuite groups related benchmarks and provides
    utilities for selective execution and progress tracking.
    """

    def __init__(self, name: str):
        """
        Initialize a BenchmarkSuite.

        Args:
            name: Name of the benchmark suite
        """
        self.name = name
        self._benchmarks: List[Benchmark] = []

    def add_benchmark(
        self,
        func: Callable,
        name: str,
        tags: Optional[List[str]] = None,
    ):
        """
        Add a benchmark to the suite.

        Args:
            func: The callable function to benchmark
            name: Name of the benchmark
            tags: Optional tags for categorization
        """
        benchmark = Benchmark(func=func, name=name, tags=tags or [])
        self._benchmarks.append(benchmark)

    def get_benchmarks(self, tags: Optional[List[str]] = None) -> List[Benchmark]:
        """
        Get benchmarks, optionally filtered by tags.

        Args:
            tags: Optional list of tags to filter by

        Returns:
            List of Benchmark objects
        """
        if not tags:
            return self._benchmarks

        # Return benchmarks that have any of the specified tags
        return [b for b in self._benchmarks if any(tag in b.tags for tag in tags)]

    def run_all(
        self,
        runner: BenchmarkRunner,
        continue_on_error: bool = False,
    ) -> List[BenchmarkResult]:
        """
        Run all benchmarks in the suite.

        Args:
            runner: The BenchmarkRunner to use
            continue_on_error: If True, continue execution even if benchmarks fail

        Returns:
            List of BenchmarkResult objects
        """
        results: List[BenchmarkResult] = []

        for i, benchmark in enumerate(self._benchmarks, 1):
            logger.info(
                f"Running benchmark {i}/{len(self._benchmarks)}: {benchmark.name}"
            )
            try:
                result = runner.run_single_benchmark(
                    benchmark_func=benchmark.func,
                    name=benchmark.name,
                    continue_on_error=continue_on_error,
                )
                results.append(result)
            except Exception as e:
                if continue_on_error:
                    # Create a failed result
                    result = BenchmarkResult(
                        name=benchmark.name,
                        mean_ms=0.0,
                        median_ms=0.0,
                        p95_ms=0.0,
                        p99_ms=0.0,
                        timestamp=datetime.now(),
                        metadata={"error": str(e)},
                    )
                    results.append(result)
                else:
                    raise

        return results


# Helper functions for resource monitoring


def get_memory_usage() -> float:
    """
    Get current process memory usage in MB.

    Returns:
        Memory usage in megabytes
    """
    try:
        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return memory_info.rss / (1024 * 1024)  # Convert bytes to MB
    except ImportError:
        # psutil not available, return 0
        return 0.0


def get_cpu_usage() -> float:
    """
    Get current CPU usage percentage.

    Returns:
        CPU usage as a percentage
    """
    try:
        import os

        import psutil

        process = psutil.Process(os.getpid())
        return process.cpu_percent(interval=0.1)
    except ImportError:
        # psutil not available, return 0
        return 0.0
