"""
Comprehensive tests for benchmark runner infrastructure module.

This test suite validates the benchmark runner framework for executing,
managing, and collecting results from performance benchmarks.

Tests cover:
- BenchmarkRunner initialization and execution
- Benchmark configuration validation
- Result collection and aggregation
- Benchmark suite management
"""

import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Import benchmark framework components
try:
    from cbr_mcp_server.performance.framework.benchmark_runner import (
        Benchmark,
        BenchmarkConfig,
        BenchmarkResult,
        BenchmarkRunner,
        BenchmarkSuite,
    )

    MODULE_AVAILABLE = True
except ImportError:
    # Module not yet implemented - TDD Red phase
    Benchmark = None
    BenchmarkConfig = None
    BenchmarkResult = None
    BenchmarkRunner = None
    BenchmarkSuite = None
    MODULE_AVAILABLE = False

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def default_config() -> BenchmarkConfig:
    """Provide default benchmark configuration for testing."""
    return BenchmarkConfig(
        iterations=100,
        warmup_iterations=10,
        timeout_seconds=60.0,
        collect_memory=True,
        collect_cpu=True,
    )


@pytest.fixture
def custom_config() -> BenchmarkConfig:
    """Provide custom benchmark configuration for testing."""
    return BenchmarkConfig(
        iterations=50,
        warmup_iterations=5,
        timeout_seconds=30.0,
        collect_memory=False,
        collect_cpu=False,
    )


@pytest.fixture
def benchmark_runner(default_config: BenchmarkConfig) -> BenchmarkRunner:
    """Provide BenchmarkRunner instance with default configuration."""
    return BenchmarkRunner(config=default_config)


@pytest.fixture
def benchmark_suite() -> BenchmarkSuite:
    """Provide empty BenchmarkSuite for testing."""
    return BenchmarkSuite(name="test_suite")


@pytest.fixture
def mock_benchmark_func() -> Mock:
    """Provide mock benchmark function that simulates work."""

    def benchmark_work():
        time.sleep(0.001)  # Simulate 1ms of work
        return "completed"

    return Mock(side_effect=benchmark_work)


@pytest.fixture
def mock_fast_benchmark() -> Callable:
    """Provide fast benchmark function for testing."""

    def fast_work():
        return sum(range(100))

    return fast_work


@pytest.fixture
def mock_slow_benchmark() -> Callable:
    """Provide slow benchmark function for timeout testing."""

    def slow_work():
        time.sleep(2.0)  # Exceeds typical timeout
        return "completed"

    return slow_work


# ============================================================================
# 1. BenchmarkRunner Class Tests (8 tests)
# ============================================================================


def test_benchmark_runner_initialization_default_config():
    """
    Test that BenchmarkRunner initializes with default configuration.

    Verifies:
    - Runner accepts None config and uses defaults
    - Default values are correctly set
    - Runner is ready to execute benchmarks
    """
    runner = BenchmarkRunner(config=None)

    assert runner is not None
    assert runner.config.iterations == 100
    assert runner.config.warmup_iterations == 10
    assert runner.config.timeout_seconds == 60.0
    assert runner.config.collect_memory is True
    assert runner.config.collect_cpu is True


def test_benchmark_runner_initialization_custom_config(custom_config: BenchmarkConfig):
    """
    Test that BenchmarkRunner accepts and uses custom configuration.

    Verifies:
    - Custom config is applied correctly
    - All custom values are respected
    - Runner is configured for custom execution
    """
    runner = BenchmarkRunner(config=custom_config)

    assert runner.config.iterations == 50
    assert runner.config.warmup_iterations == 5
    assert runner.config.timeout_seconds == 30.0
    assert runner.config.collect_memory is False
    assert runner.config.collect_cpu is False


def test_run_single_benchmark_success(
    benchmark_runner: BenchmarkRunner, mock_fast_benchmark: Callable
):
    """
    Test running a single benchmark function and collecting results.

    Verifies:
    - Benchmark executes successfully
    - BenchmarkResult is returned
    - Timing data is captured
    - Result contains expected metrics
    """
    result = benchmark_runner.run_single_benchmark(
        benchmark_func=mock_fast_benchmark, name="fast_test"
    )

    assert isinstance(result, BenchmarkResult)
    assert result.name == "fast_test"
    assert result.mean_ms > 0
    assert result.median_ms > 0
    assert result.p95_ms > 0
    assert result.p99_ms > 0
    assert isinstance(result.timestamp, datetime)


def test_run_benchmark_suite_multiple_benchmarks(
    benchmark_runner: BenchmarkRunner, benchmark_suite: BenchmarkSuite
):
    """
    Test running multiple benchmarks in a suite.

    Verifies:
    - Multiple benchmarks execute sequentially
    - Results returned for all benchmarks
    - Each result is properly formatted
    - Suite execution completes successfully
    """

    def bench1():
        return sum(range(100))

    def bench2():
        return sum(range(200))

    def bench3():
        return sum(range(300))

    benchmark_suite.add_benchmark(bench1, "benchmark_1")
    benchmark_suite.add_benchmark(bench2, "benchmark_2")
    benchmark_suite.add_benchmark(bench3, "benchmark_3")

    results = benchmark_runner.run_benchmark_suite(suite=benchmark_suite)

    assert len(results) == 3
    assert all(isinstance(r, BenchmarkResult) for r in results)
    assert results[0].name == "benchmark_1"
    assert results[1].name == "benchmark_2"
    assert results[2].name == "benchmark_3"


def test_benchmark_timeout_handling(
    benchmark_runner: BenchmarkRunner, mock_slow_benchmark: Callable
):
    """
    Test timeout enforcement for long-running benchmarks.

    Verifies:
    - Timeout is enforced
    - Timeout exception is raised or handled
    - Execution stops after timeout
    - Error is properly reported
    """
    # Configure short timeout
    benchmark_runner.config.timeout_seconds = 0.5

    with pytest.raises(TimeoutError):
        benchmark_runner.run_single_benchmark(
            benchmark_func=mock_slow_benchmark, name="slow_test"
        )


def test_benchmark_retry_logic_on_failure(benchmark_runner: BenchmarkRunner):
    """
    Test retry mechanism when benchmark fails.

    Verifies:
    - Failed benchmarks are retried
    - Retry count is tracked
    - Eventually succeeds after retries
    - Success result is returned
    """
    call_count = {"count": 0}

    def flaky_benchmark():
        call_count["count"] += 1
        if call_count["count"] < 3:
            raise RuntimeError("Transient failure")
        return "success"

    # Configure retry attempts
    benchmark_runner.config.max_retries = 3

    result = benchmark_runner.run_single_benchmark(
        benchmark_func=flaky_benchmark, name="flaky_test"
    )

    assert result is not None
    assert call_count["count"] == 3
    assert result.metadata.get("retry_count") == 2


def test_warmup_rounds_before_benchmark(
    benchmark_runner: BenchmarkRunner, mock_benchmark_func: Mock
):
    """
    Test warmup iterations run before actual benchmark.

    Verifies:
    - Warmup executes specified number of times
    - Warmup results not included in final metrics
    - Actual benchmark runs after warmup
    - Call count matches warmup + iterations
    """
    benchmark_runner.config.warmup_iterations = 5
    benchmark_runner.config.iterations = 10

    result = benchmark_runner.run_single_benchmark(
        benchmark_func=mock_benchmark_func, name="warmup_test"
    )

    # Warmup (5) + actual iterations (10) = 15 total calls
    assert mock_benchmark_func.call_count == 15
    assert result.metadata.get("warmup_iterations") == 5


def test_concurrent_benchmark_execution(benchmark_runner: BenchmarkRunner):
    """
    Test multiple benchmarks can run concurrently.

    Verifies:
    - Concurrent execution is supported
    - All benchmarks complete
    - Results collected for all
    - Execution time is reduced by concurrency
    """

    def bench_a():
        time.sleep(0.1)
        return "a"

    def bench_b():
        time.sleep(0.1)
        return "b"

    benchmark_runner.config.concurrent = True

    start_time = time.time()
    results = benchmark_runner.run_concurrent_benchmarks(
        benchmarks=[(bench_a, "bench_a"), (bench_b, "bench_b")]
    )
    elapsed = time.time() - start_time

    assert len(results) == 2
    # Concurrent execution should be faster than sequential
    assert elapsed < 0.25  # Less than 2 * 0.1 + overhead


# ============================================================================
# 2. Benchmark Configuration Tests (5 tests)
# ============================================================================


def test_benchmark_config_validation_valid():
    """
    Test valid configuration passes validation.

    Verifies:
    - Config object created successfully
    - All fields have valid values
    - No validation errors raised
    """
    config = BenchmarkConfig(
        iterations=100,
        warmup_iterations=10,
        timeout_seconds=60.0,
        collect_memory=True,
        collect_cpu=True,
    )

    assert config.iterations == 100
    assert config.warmup_iterations == 10
    assert config.timeout_seconds == 60.0


def test_benchmark_config_validation_invalid_iterations():
    """
    Test invalid iteration count is rejected.

    Verifies:
    - Negative iterations raise ValueError
    - Zero iterations raise ValueError
    - Validation message is clear
    """
    with pytest.raises(ValueError, match="iterations must be positive"):
        BenchmarkConfig(iterations=-1)

    with pytest.raises(ValueError, match="iterations must be positive"):
        BenchmarkConfig(iterations=0)


def test_configurable_timeout_values():
    """
    Test timeout can be configured.

    Verifies:
    - Timeout value is applied correctly
    - Different timeout values work
    - Timeout affects execution behavior
    """
    config_short = BenchmarkConfig(timeout_seconds=1.0)
    config_long = BenchmarkConfig(timeout_seconds=120.0)

    assert config_short.timeout_seconds == 1.0
    assert config_long.timeout_seconds == 120.0


def test_warmup_configuration():
    """
    Test warmup iteration count is configurable.

    Verifies:
    - Warmup config is applied
    - Zero warmup is allowed
    - Different warmup counts work
    """
    config_no_warmup = BenchmarkConfig(warmup_iterations=0)
    config_with_warmup = BenchmarkConfig(warmup_iterations=20)

    assert config_no_warmup.warmup_iterations == 0
    assert config_with_warmup.warmup_iterations == 20


def test_result_collection_settings():
    """
    Test result collection flags are configurable.

    Verifies:
    - Memory collection can be enabled/disabled
    - CPU collection can be enabled/disabled
    - Settings affect what metrics are collected
    """
    config_minimal = BenchmarkConfig(collect_memory=False, collect_cpu=False)
    config_full = BenchmarkConfig(collect_memory=True, collect_cpu=True)

    assert config_minimal.collect_memory is False
    assert config_minimal.collect_cpu is False
    assert config_full.collect_memory is True
    assert config_full.collect_cpu is True


# ============================================================================
# 3. Result Collection Tests (5 tests)
# ============================================================================


def test_collecting_benchmark_timing_results(
    benchmark_runner: BenchmarkRunner, mock_fast_benchmark: Callable
):
    """
    Test timing metrics are collected correctly.

    Verifies:
    - Mean, median, p95, p99 are calculated
    - Timing values are reasonable
    - All percentiles present
    """
    result = benchmark_runner.run_single_benchmark(
        benchmark_func=mock_fast_benchmark, name="timing_test"
    )

    assert result.mean_ms > 0
    assert result.median_ms > 0
    assert result.p95_ms > 0
    assert result.p99_ms > 0
    # P99 should be >= P95 >= median
    assert result.p99_ms >= result.p95_ms >= result.median_ms


@patch("benchmarks.framework.benchmark_runner.get_memory_usage")
def test_collecting_memory_usage_results(
    mock_memory: Mock, benchmark_runner: BenchmarkRunner, mock_fast_benchmark: Callable
):
    """
    Test memory usage is tracked during benchmarks.

    Verifies:
    - Memory metrics captured when enabled
    - Memory value is in MB
    - Memory profiler called correctly
    """
    mock_memory.return_value = 123.45  # MB

    benchmark_runner.config.collect_memory = True
    result = benchmark_runner.run_single_benchmark(
        benchmark_func=mock_fast_benchmark, name="memory_test"
    )

    assert result.memory_mb is not None
    assert result.memory_mb > 0
    mock_memory.assert_called()


@patch("benchmarks.framework.benchmark_runner.get_cpu_usage")
def test_collecting_system_resource_metrics(
    mock_cpu: Mock, benchmark_runner: BenchmarkRunner, mock_fast_benchmark: Callable
):
    """
    Test CPU and system metrics are collected.

    Verifies:
    - CPU metrics captured when enabled
    - Resource monitor called correctly
    - Metrics stored in metadata
    """
    mock_cpu.return_value = 45.2  # CPU percentage

    benchmark_runner.config.collect_cpu = True
    result = benchmark_runner.run_single_benchmark(
        benchmark_func=mock_fast_benchmark, name="cpu_test"
    )

    assert "cpu_usage" in result.metadata
    assert result.metadata["cpu_usage"] > 0
    mock_cpu.assert_called()


def test_result_aggregation_statistics(benchmark_runner: BenchmarkRunner):
    """
    Test statistical aggregation is correct.

    Verifies:
    - Mean calculated correctly
    - Median calculated correctly
    - Percentiles (p95, p99) accurate
    - Statistical formulas work
    """

    # Use predictable benchmark with known timing
    def predictable_benchmark():
        time.sleep(0.01)  # 10ms
        return "done"

    benchmark_runner.config.iterations = 100
    result = benchmark_runner.run_single_benchmark(
        benchmark_func=predictable_benchmark, name="stats_test"
    )

    # Verify statistical relationships
    assert result.mean_ms > 9  # Should be ~10ms
    assert result.mean_ms < 15
    assert result.p99_ms >= result.p95_ms
    assert result.p95_ms >= result.median_ms


def test_result_metadata_capture(
    benchmark_runner: BenchmarkRunner, mock_fast_benchmark: Callable
):
    """
    Test metadata (timestamp, environment) is captured.

    Verifies:
    - Timestamp is set
    - Environment info captured
    - Metadata dictionary populated
    - Custom metadata can be added
    """
    result = benchmark_runner.run_single_benchmark(
        benchmark_func=mock_fast_benchmark,
        name="metadata_test",
        metadata={"custom_tag": "test_value"},
    )

    assert isinstance(result.timestamp, datetime)
    assert result.metadata is not None
    assert "custom_tag" in result.metadata
    assert result.metadata["custom_tag"] == "test_value"
    assert "python_version" in result.metadata
    assert "platform" in result.metadata


# ============================================================================
# 4. Benchmark Suite Management Tests (5 tests)
# ============================================================================


def test_registering_benchmarks_to_suite(benchmark_suite: BenchmarkSuite):
    """
    Test benchmarks can be added to suite.

    Verifies:
    - Benchmarks registered successfully
    - Benchmarks retrievable by name
    - Tags are stored correctly
    """

    def bench1():
        return "a"

    def bench2():
        return "b"

    benchmark_suite.add_benchmark(bench1, "bench_1", tags=["fast", "unit"])
    benchmark_suite.add_benchmark(bench2, "bench_2", tags=["slow", "integration"])

    benchmarks = benchmark_suite.get_benchmarks()
    assert len(benchmarks) == 2
    assert benchmarks[0].name == "bench_1"
    assert benchmarks[1].name == "bench_2"


def test_running_full_benchmark_suite(
    benchmark_runner: BenchmarkRunner, benchmark_suite: BenchmarkSuite
):
    """
    Test entire suite can be executed.

    Verifies:
    - All benchmarks in suite execute
    - Results returned for each
    - Suite completion is reported
    """

    def bench_a():
        return sum(range(50))

    def bench_b():
        return sum(range(100))

    benchmark_suite.add_benchmark(bench_a, "suite_a")
    benchmark_suite.add_benchmark(bench_b, "suite_b")

    results = benchmark_suite.run_all(runner=benchmark_runner)

    assert len(results) == 2
    assert all(isinstance(r, BenchmarkResult) for r in results)


def test_selective_benchmark_execution_by_tag(
    benchmark_runner: BenchmarkRunner, benchmark_suite: BenchmarkSuite
):
    """
    Test filtering benchmarks by tags.

    Verifies:
    - Only tagged benchmarks execute
    - Tag filtering works correctly
    - Untagged benchmarks excluded
    """

    def fast_bench():
        return "fast"

    def slow_bench():
        time.sleep(0.1)
        return "slow"

    benchmark_suite.add_benchmark(fast_bench, "fast", tags=["quick"])
    benchmark_suite.add_benchmark(slow_bench, "slow", tags=["lengthy"])

    # Run only "quick" tagged benchmarks
    quick_benchmarks = benchmark_suite.get_benchmarks(tags=["quick"])
    assert len(quick_benchmarks) == 1
    assert quick_benchmarks[0].name == "fast"


@patch("benchmarks.framework.benchmark_runner.logger")
def test_benchmark_suite_progress_reporting(
    mock_logger: Mock,
    benchmark_runner: BenchmarkRunner,
    benchmark_suite: BenchmarkSuite,
):
    """
    Test progress is reported during suite execution.

    Verifies:
    - Progress updates logged
    - Completion percentage tracked
    - Progress callback invoked
    """

    def bench1():
        return "a"

    def bench2():
        return "b"

    benchmark_suite.add_benchmark(bench1, "progress_1")
    benchmark_suite.add_benchmark(bench2, "progress_2")

    benchmark_suite.run_all(runner=benchmark_runner)

    # Verify progress logging occurred
    assert mock_logger.info.called
    log_messages = [call[0][0] for call in mock_logger.info.call_args_list]
    assert any("Running benchmark" in msg for msg in log_messages)


def test_suite_execution_with_failure_handling(
    benchmark_runner: BenchmarkRunner, benchmark_suite: BenchmarkSuite
):
    """
    Test suite continues when individual benchmarks fail.

    Verifies:
    - Suite execution continues after failure
    - Failures are recorded
    - Successful benchmarks still run
    - Failure info captured in results
    """

    def working_bench():
        return "success"

    def failing_bench():
        raise RuntimeError("Intentional failure")

    benchmark_suite.add_benchmark(working_bench, "working")
    benchmark_suite.add_benchmark(failing_bench, "failing")
    benchmark_suite.add_benchmark(working_bench, "working2")

    results = benchmark_suite.run_all(runner=benchmark_runner, continue_on_error=True)

    # Should have 3 results (2 success, 1 failure)
    assert len(results) == 3
    success_results = [r for r in results if r.metadata.get("error") is None]
    failed_results = [r for r in results if r.metadata.get("error") is not None]

    assert len(success_results) == 2
    assert len(failed_results) == 1
    assert "Intentional failure" in failed_results[0].metadata["error"]


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


def test_empty_benchmark_suite_execution(
    benchmark_runner: BenchmarkRunner, benchmark_suite: BenchmarkSuite
):
    """
    Test running empty benchmark suite.

    Verifies:
    - Empty suite returns empty results
    - No errors raised
    - Graceful handling
    """
    results = benchmark_suite.run_all(runner=benchmark_runner)
    assert len(results) == 0


def test_benchmark_with_exception(benchmark_runner: BenchmarkRunner):
    """
    Test benchmark that raises exception.

    Verifies:
    - Exception is caught
    - Error recorded in result
    - Execution doesn't crash
    """

    def failing_benchmark():
        raise ValueError("Test exception")

    result = benchmark_runner.run_single_benchmark(
        benchmark_func=failing_benchmark, name="exception_test", continue_on_error=True
    )

    assert result.metadata.get("error") is not None
    assert "Test exception" in result.metadata["error"]


def test_zero_iteration_config():
    """
    Test configuration with zero iterations is rejected.

    Verifies:
    - ValueError raised for zero iterations
    - Clear error message
    """
    with pytest.raises(ValueError, match="iterations must be positive"):
        BenchmarkConfig(iterations=0)
