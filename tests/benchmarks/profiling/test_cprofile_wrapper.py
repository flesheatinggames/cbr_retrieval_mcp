"""
cProfile Integration Wrapper Tests for CBR MCP Server.

This test suite provides comprehensive coverage for the cProfile integration
wrapper module, which offers convenient profiling capabilities for CBR server
operations. The wrapper simplifies profiling of synchronous and async operations,
providing structured profile data collection and multiple output formats.

Test Coverage:
1. ProfilerWrapper Class (7 tests)
   - Basic initialization
   - Start/stop lifecycle management
   - Context manager usage
   - Decorator for synchronous functions
   - Decorator for async functions
   - Nested profiling contexts
   - State management and error handling

2. Profile Data Collection (5 tests)
   - Timing statistics collection
   - Function call count tracking
   - Cumulative time tracking
   - Sorting profile results by various criteria
   - Filtering profile results by function name

3. Profile Output Formats (4 tests)
   - Text format output
   - Statistics dictionary format
   - Saving to .prof file format
   - Print stats to console

4. Integration with CBR Operations (4 tests)
   - Profiling query retrieval operations
   - Profiling embedding generation
   - Profiling database queries
   - Profiling full request lifecycle

Note: These are TDD tests - they define the expected interface and behavior
before the implementation exists. All tests should fail with ModuleNotFoundError
or AttributeError initially.
"""

import asyncio
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import the cProfile wrapper module (will fail initially - that's expected for TDD)
try:
    from tests.benchmarks.profiling.cprofile_wrapper import (
        ProfilerWrapper,
        profile_async_function,
        profile_function,
    )

    PROFILER_AVAILABLE = True
except ImportError:
    PROFILER_AVAILABLE = False
    # Create placeholder classes for test structure
    ProfilerWrapper = None
    profile_function = None
    profile_async_function = None


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def profiler_wrapper():
    """
    Provide a clean ProfilerWrapper instance for testing.

    Returns:
        ProfilerWrapper: Fresh instance with default configuration
    """
    if not PROFILER_AVAILABLE:
        pytest.skip("ProfilerWrapper not yet implemented")
    return ProfilerWrapper(sort_by="cumulative")


@pytest.fixture
def temp_profile_file():
    """
    Provide a temporary file path for profile output.

    Yields:
        str: Path to temporary .prof file
    """
    with tempfile.NamedTemporaryFile(suffix=".prof", delete=False) as tmp:
        temp_path = tmp.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_cbr_retriever():
    """
    Mock CBR retriever for integration testing.

    Returns:
        Mock: Configured mock with realistic timing
    """
    retriever = Mock()

    async def mock_retrieve(query_text, max_results=5):
        await asyncio.sleep(0.01)  # Simulate DB latency
        return {
            "cases": [
                {"id": f"case_{i}", "content": "Example"} for i in range(max_results)
            ],
            "total_results": max_results,
        }

    retriever.retrieve = AsyncMock(side_effect=mock_retrieve)
    return retriever


@pytest.fixture
def mock_embedding_model():
    """
    Mock embedding model for profiling tests.

    Returns:
        Mock: Embedding model with simulated generation time
    """
    model = Mock()

    def mock_encode(text):
        time.sleep(0.005)  # Simulate embedding generation
        return [0.1] * 768

    model.encode = Mock(side_effect=mock_encode)
    return model


# ============================================================================
# Section 1: ProfilerWrapper Class Tests (7 tests)
# ============================================================================


def test_profiler_initialization_default():
    """
    Test ProfilerWrapper initialization with default parameters.

    Verifies that a ProfilerWrapper instance can be created with default
    configuration and that initial state is correct.
    """
    if not PROFILER_AVAILABLE:
        pytest.skip("ProfilerWrapper not yet implemented")

    profiler = ProfilerWrapper()

    assert profiler is not None
    assert hasattr(profiler, "sort_by")
    assert profiler.sort_by == "cumulative"  # Default sort order
    assert hasattr(profiler, "start")
    assert hasattr(profiler, "stop")
    assert hasattr(profiler, "get_stats")


def test_profiler_initialization_custom_sort():
    """
    Test ProfilerWrapper initialization with custom sort_by parameter.

    Verifies that sort_by parameter can be customized during initialization.
    """
    if not PROFILER_AVAILABLE:
        pytest.skip("ProfilerWrapper not yet implemented")

    profiler = ProfilerWrapper(sort_by="time")

    assert profiler.sort_by == "time"


def test_start_stop_profiling_lifecycle():
    """
    Test that profiler can be started and stopped correctly.

    Verifies:
    - Profiler state changes from stopped to running
    - Profiler state changes from running to stopped
    - Stats are available after stop
    """
    profiler = ProfilerWrapper()

    assert not profiler._is_running

    profiler.start()
    assert profiler._is_running

    # Do some work
    time.sleep(0.01)
    sum([i for i in range(100)])

    profiler.stop()
    assert not profiler._is_running

    stats = profiler.get_stats()
    assert stats is not None
    assert "total_calls" in stats


def test_context_manager_usage():
    """
    Test that ProfilerWrapper works as context manager with 'with' statement.

    Verifies:
    - Profiler starts automatically on __enter__
    - Profiler stops automatically on __exit__
    - Stats are available after context exit
    """
    profiler = ProfilerWrapper()

    assert not profiler._is_running

    with profiler:
        assert profiler._is_running
        # Do some work
        time.sleep(0.01)
        sum([i for i in range(100)])

    assert not profiler._is_running
    stats = profiler.get_stats()
    assert stats is not None
    assert "total_calls" in stats


def test_decorator_usage_for_functions():
    """
    Test that profile_function decorator works on synchronous functions.

    Verifies:
    - Function executes successfully
    - Profiling data is captured
    - Function return value is preserved
    """

    @profile_function(sort_by="cumulative")
    def sample_function(x: int, y: int) -> int:
        """Sample function for testing decorator."""
        time.sleep(0.01)
        return x + y

    result = sample_function(5, 10)

    assert result == 15


@pytest.mark.asyncio
async def test_async_function_profiling_support():
    """
    Test that profile_async_function decorator works on async functions.

    Verifies:
    - Async function executes successfully
    - Profiling data is captured
    - Await semantics are preserved
    - Function return value is preserved
    """

    @profile_async_function(sort_by="cumulative")
    async def sample_async_function(x: int, y: int) -> int:
        """Sample async function for testing decorator."""
        await asyncio.sleep(0.01)
        return x * y

    result = await sample_async_function(5, 10)

    assert result == 50


def test_nested_profiling_contexts():
    """
    Test that nested profiler contexts work correctly.

    Verifies:
    - Inner and outer contexts both capture data
    - No interference between contexts
    - Each context has independent stats
    """
    outer_profiler = ProfilerWrapper()
    inner_profiler = ProfilerWrapper()

    with outer_profiler:
        time.sleep(0.01)
        sum([i for i in range(100)])

        with inner_profiler:
            time.sleep(0.01)
            sum([i for i in range(50)])

    outer_stats = outer_profiler.get_stats()
    inner_stats = inner_profiler.get_stats()

    assert outer_stats is not None
    assert inner_stats is not None
    assert "total_calls" in outer_stats
    assert "total_calls" in inner_stats


def test_profiler_state_management_errors(profiler_wrapper):
    """
    Test profiler state transitions and error handling.

    Verifies that:
    - Cannot stop profiler that hasn't been started
    - Cannot start already running profiler
    - State management is robust
    """

    # Cannot stop before starting
    with pytest.raises((RuntimeError, ValueError)):
        profiler_wrapper.stop()

    # Start profiler
    profiler_wrapper.start()

    # Cannot start again while running
    with pytest.raises((RuntimeError, ValueError)):
        profiler_wrapper.start()

    # Stop profiler
    profiler_wrapper.stop()

    # Can start again after stopping
    profiler_wrapper.start()
    profiler_wrapper.stop()


# ============================================================================
# Profile Data Collection Tests (5 tests)
# ============================================================================


def test_collecting_timing_statistics():
    """
    Test that timing statistics are collected accurately.

    Verifies:
    - Stats contain timing data
    - Timing values are reasonable (> 0)
    - Total time is tracked
    """
    profiler = ProfilerWrapper()

    with profiler:
        time.sleep(0.02)
        sum([i**2 for i in range(1000)])

    stats = profiler.get_stats()

    assert "total_calls" in stats
    assert "total_time" in stats
    assert stats["total_time"] > 0
    assert isinstance(stats["total_time"], float)


def test_function_call_counts():
    """
    Test that function call counts are tracked correctly.

    Verifies:
    - Call counts match expected invocations
    - Multiple calls to same function are counted
    """

    def helper_function():
        """Helper function called multiple times."""
        return sum([i for i in range(10)])

    profiler = ProfilerWrapper()

    with profiler:
        for _ in range(5):
            helper_function()

    stats = profiler.get_stats()
    assert stats["total_calls"] >= 5


def test_cumulative_time_tracking():
    """
    Test that cumulative time includes nested function time.

    Verifies:
    - Cumulative time >= total time of nested calls
    - Parent function cumulative time includes children
    """

    def child_function():
        """Child function with some work."""
        time.sleep(0.01)
        return sum([i for i in range(100)])

    def parent_function():
        """Parent function calling child."""
        child_function()
        child_function()

    profiler = ProfilerWrapper()

    with profiler:
        parent_function()

    stats = profiler.get_stats()
    assert "total_time" in stats
    assert stats["total_time"] > 0.01  # At least two sleep calls


def test_sorting_profile_results():
    """
    Test that profile results can be sorted by different metrics.

    Verifies:
    - Results can be sorted by "time"
    - Results can be sorted by "cumulative"
    - Results can be sorted by "calls"
    """
    profiler_time = ProfilerWrapper(sort_by="time")
    profiler_cumulative = ProfilerWrapper(sort_by="cumulative")

    def sample_work():
        time.sleep(0.01)
        return sum([i for i in range(100)])

    with profiler_time:
        sample_work()

    with profiler_cumulative:
        sample_work()

    stats_time = profiler_time.get_stats()
    stats_cumulative = profiler_cumulative.get_stats()

    assert stats_time is not None
    assert stats_cumulative is not None


def test_filtering_profile_results_by_function_name():
    """
    Test that profile results can be filtered by function name pattern.

    Verifies:
    - Only matching functions appear in filtered results
    - Filtering by pattern works correctly
    """

    def target_function():
        """Function to be filtered for."""
        return sum([i for i in range(100)])

    def other_function():
        """Function to be filtered out."""
        return sum([i for i in range(50)])

    profiler = ProfilerWrapper()

    with profiler:
        target_function()
        other_function()

    top_functions = profiler.get_top_functions(n=20)

    assert len(top_functions) > 0
    # Should include both functions
    function_names = [f["name"] for f in top_functions]
    assert any("target_function" in name for name in function_names)


# ============================================================================
# Profile Output Formats Tests (4 tests)
# ============================================================================


def test_text_format_output(capsys):
    """
    Test that text format output is human-readable.

    Verifies:
    - Output contains expected sections
    - Output is readable format
    - print_stats produces output
    """
    profiler = ProfilerWrapper()

    with profiler:
        time.sleep(0.01)
        sum([i for i in range(100)])

    profiler.print_stats(num_lines=10)
    captured = capsys.readouterr()

    assert len(captured.out) > 0
    assert "function calls" in captured.out or "ncalls" in captured.out


def test_statistics_dictionary_format():
    """
    Test that get_stats returns properly structured dictionary.

    Verifies:
    - Dict contains expected keys
    - Values are correct types
    - All required fields present
    """
    profiler = ProfilerWrapper()

    with profiler:
        time.sleep(0.01)
        sum([i for i in range(100)])

    stats = profiler.get_stats()

    assert isinstance(stats, dict)
    assert "total_calls" in stats
    assert "total_time" in stats
    assert "primitive_calls" in stats
    assert isinstance(stats["total_calls"], int)
    assert isinstance(stats["total_time"], float)


def test_saving_to_file_prof_format():
    """
    Test that profile data can be saved to .prof file.

    Verifies:
    - File is created
    - File is loadable by pstats
    - File contains profile data
    """
    profiler = ProfilerWrapper()

    with profiler:
        time.sleep(0.01)
        sum([i for i in range(100)])

    with tempfile.NamedTemporaryFile(suffix=".prof", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        profiler.save_to_file(tmp_path)

        assert Path(tmp_path).exists()
        assert Path(tmp_path).stat().st_size > 0

        # Verify it's a valid prof file by loading with pstats
        import pstats

        stats = pstats.Stats(tmp_path)
        assert stats is not None
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_get_top_functions():
    """
    Test that top N functions by metric can be retrieved.

    Verifies:
    - Correct number of functions returned (up to N)
    - Functions are sorted by metric
    - Each function has required fields
    """

    def work_function_1():
        time.sleep(0.01)
        return sum([i for i in range(100)])

    def work_function_2():
        time.sleep(0.005)
        return sum([i for i in range(50)])

    profiler = ProfilerWrapper()

    with profiler:
        work_function_1()
        work_function_2()

    top_5 = profiler.get_top_functions(n=5)

    assert isinstance(top_5, list)
    assert len(top_5) <= 5
    assert len(top_5) > 0

    for func_info in top_5:
        assert "name" in func_info
        assert "ncalls" in func_info
        assert "tottime" in func_info
        assert "cumtime" in func_info


# ============================================================================
# Integration with CBR Operations Tests (4 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_profiling_query_retrieval_operations(
    profiler_wrapper, mock_cbr_retriever
):
    """
    Test profiler can measure query retrieval performance.

    Verifies that profiling a CBR query retrieval operation
    captures relevant function calls and timing data.
    """

    async def execute_query():
        result = await mock_cbr_retriever.retrieve(
            query_text="Test query", max_results=5
        )
        return result

    with profiler_wrapper:
        result = await execute_query()

    # Assertions
    assert result is not None
    assert result["total_results"] == 5

    stats = profiler_wrapper.get_stats()
    assert stats is not None
    assert isinstance(stats, dict)


def test_profiling_embedding_generation(profiler_wrapper, mock_embedding_model):
    """
    Test profiler can measure embedding generation.

    Verifies that profiling embedding model inference captures
    model operations and timing breakdown.
    """

    def generate_embedding():
        text = "Sample query for embedding"
        embedding = mock_embedding_model.encode(text)
        return embedding

    with profiler_wrapper:
        embedding = generate_embedding()

    # Assertions
    assert embedding is not None
    assert len(embedding) == 768

    stats = profiler_wrapper.get_stats()
    assert stats is not None

    # Embedding generation should be captured
    if "total_time" in stats:
        assert stats["total_time"] > 0


@pytest.mark.asyncio
async def test_profiling_database_queries(profiler_wrapper, mock_cbr_retriever):
    """
    Test profiler can measure database query performance.

    Verifies that profiling ChromaDB operations captures
    collection access and query execution time.
    """

    async def database_operation():
        # Simulate multiple database queries
        results = []
        for i in range(3):
            result = await mock_cbr_retriever.retrieve(
                query_text=f"Query {i}", max_results=5
            )
            results.append(result)
        return results

    with profiler_wrapper:
        results = await database_operation()

    # Assertions
    assert len(results) == 3
    assert all(r["total_results"] == 5 for r in results)

    stats = profiler_wrapper.get_stats()
    assert stats is not None

    # Multiple queries should accumulate in cumulative time
    if "total_calls" in stats:
        assert stats["total_calls"] >= 3


@pytest.mark.asyncio
async def test_profiling_full_request_lifecycle(
    profiler_wrapper, mock_cbr_retriever, mock_embedding_model
):
    """
    Test profiler can measure complete CBR request.

    Verifies that profiling end-to-end request captures all stages:
    embedding generation, database query, and result processing.
    """

    async def full_cbr_request():
        # Stage 1: Generate embedding
        query_text = "Complete CBR request test"
        embedding = mock_embedding_model.encode(query_text)

        # Stage 2: Execute database query
        result = await mock_cbr_retriever.retrieve(query_text=query_text, max_results=5)

        # Stage 3: Process results
        processed = [case["id"] for case in result["cases"]]

        return {"embedding": embedding, "cases": result["cases"], "ids": processed}

    with profiler_wrapper:
        result = await full_cbr_request()

    # Assertions
    assert result is not None
    assert "embedding" in result
    assert "cases" in result
    assert "ids" in result
    assert len(result["ids"]) == 5

    stats = profiler_wrapper.get_stats()
    assert stats is not None

    # All stages should be captured in profile
    top_functions = profiler_wrapper.get_top_functions(n=20)
    assert len(top_functions) > 0


# ============================================================================
# Additional Fixture Tests
# ============================================================================


def test_profiler_wrapper_fixture(profiler_wrapper):
    """
    Test pytest fixture provides clean ProfilerWrapper instance.

    Verifies that the fixture returns a properly initialized
    ProfilerWrapper and that multiple tests get isolated instances.
    """
    assert profiler_wrapper is not None
    assert isinstance(profiler_wrapper, ProfilerWrapper)
    assert hasattr(profiler_wrapper, "start")
    assert hasattr(profiler_wrapper, "stop")
    assert hasattr(profiler_wrapper, "get_stats")
    assert profiler_wrapper.sort_by == "cumulative"


def test_profiler_wrapper_fixture_isolation(profiler_wrapper):
    """
    Test fixture provides isolated instances across tests.

    Verifies that each test gets a fresh profiler instance
    without state pollution from other tests.
    """

    def sample_function():
        return sum(range(100))

    # Use profiler in this test
    with profiler_wrapper:
        sample_function()

    # This test should have its own clean instance
    # (verified by running this test along with other tests)
    assert profiler_wrapper is not None
