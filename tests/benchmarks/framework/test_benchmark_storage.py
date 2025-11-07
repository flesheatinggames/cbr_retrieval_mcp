"""
Comprehensive tests for benchmark result storage module.

This test suite covers:
- BenchmarkStorage class initialization and basic operations
- Storage format serialization (JSON, CSV)
- Result querying capabilities (by name, date range, tags)
- Storage management (archival, rotation, concurrent writes)

All tests follow TDD principles and should FAIL initially.
"""

import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import pytest

# Import benchmark storage components
try:
    from cbr_mcp_server.performance.framework.benchmark_storage import (
        BenchmarkResult,
        BenchmarkStorage,
        ResultSerializer,
    )

    MODULE_AVAILABLE = True
except ImportError:
    # Module not yet implemented - TDD Red phase
    BenchmarkResult = None
    BenchmarkStorage = None
    ResultSerializer = None
    MODULE_AVAILABLE = False


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def benchmark_storage(tmp_path: Path) -> BenchmarkStorage:
    """Create BenchmarkStorage instance with temporary directory."""
    storage_path = tmp_path / "benchmark_results"
    return BenchmarkStorage(storage_path=str(storage_path))


@pytest.fixture
def sample_results() -> List[BenchmarkResult]:
    """Create sample BenchmarkResult objects for testing."""
    base_time = datetime(2025, 11, 5, 10, 0, 0)

    results = [
        BenchmarkResult(
            name="test_benchmark_1",
            timestamp=base_time,
            duration_ms=150.5,
            success=True,
            tags=["python", "unit"],
            metadata={"category": "performance"},
        ),
        BenchmarkResult(
            name="test_benchmark_2",
            timestamp=base_time + timedelta(hours=1),
            duration_ms=230.8,
            success=True,
            tags=["python", "integration"],
            metadata={"category": "reliability"},
        ),
        BenchmarkResult(
            name="test_benchmark_3",
            timestamp=base_time + timedelta(hours=2),
            duration_ms=95.2,
            success=False,
            tags=["javascript", "unit"],
            metadata={"category": "performance", "error": "timeout"},
        ),
    ]
    return results


# ============================================================================
# 1. BenchmarkStorage Class Tests
# ============================================================================


def test_storage_initialization_default_path():
    """
    Test BenchmarkStorage initializes with default path.

    Verifies:
    - Storage path is set to default "./benchmark_results"
    - Storage directory is created automatically
    """
    storage = BenchmarkStorage()

    assert storage.storage_path == "./benchmark_results"
    assert Path(storage.storage_path).exists()
    assert Path(storage.storage_path).is_dir()


def test_storage_initialization_custom_path(tmp_path: Path):
    """
    Test BenchmarkStorage initializes with custom path.

    Verifies:
    - Storage path is set to custom value
    - Custom directory is created automatically
    """
    custom_path = tmp_path / "custom_benchmarks"
    storage = BenchmarkStorage(storage_path=str(custom_path))

    assert storage.storage_path == str(custom_path)
    assert custom_path.exists()
    assert custom_path.is_dir()


def test_save_result_single(benchmark_storage: BenchmarkStorage):
    """
    Test saving a single BenchmarkResult.

    Verifies:
    - Result file is created
    - File contains correct JSON data
    - Filename follows naming convention (timestamp-name.json)
    """
    result = BenchmarkResult(
        name="test_save_single",
        timestamp=datetime(2025, 11, 5, 12, 0, 0),
        duration_ms=100.0,
        success=True,
        tags=["test"],
        metadata={},
    )

    benchmark_storage.save_result(result, format="json")

    storage_path = Path(benchmark_storage.storage_path)
    result_files = list(storage_path.glob("*.json"))

    assert len(result_files) == 1
    assert result.name in result_files[0].name

    with open(result_files[0], "r") as f:
        saved_data = json.load(f)
        assert saved_data["name"] == result.name
        assert saved_data["duration_ms"] == result.duration_ms


def test_save_results_multiple(
    benchmark_storage: BenchmarkStorage, sample_results: List[BenchmarkResult]
):
    """
    Test saving multiple BenchmarkResults in batch.

    Verifies:
    - Batch file is created
    - File contains JSON array with all results
    - All results are present in saved data
    """
    benchmark_storage.save_results(sample_results, format="json")

    storage_path = Path(benchmark_storage.storage_path)
    result_files = list(storage_path.glob("*.json"))

    assert len(result_files) == 1

    with open(result_files[0], "r") as f:
        saved_data = json.load(f)
        assert isinstance(saved_data, list)
        assert len(saved_data) == len(sample_results)
        assert all(
            item["name"] in [r.name for r in sample_results] for item in saved_data
        )


def test_load_results(
    benchmark_storage: BenchmarkStorage, sample_results: List[BenchmarkResult]
):
    """
    Test loading results from a specific file.

    Verifies:
    - Correct number of results loaded
    - Data integrity maintained (names, durations match)
    - Returns List[BenchmarkResult] objects
    """
    # First save the results
    benchmark_storage.save_results(sample_results, format="json")

    storage_path = Path(benchmark_storage.storage_path)
    result_file = list(storage_path.glob("*.json"))[0]

    # Load the results
    loaded_results = benchmark_storage.load_results(result_file.name)

    assert len(loaded_results) == len(sample_results)
    assert all(isinstance(r, BenchmarkResult) for r in loaded_results)
    assert {r.name for r in loaded_results} == {r.name for r in sample_results}


def test_load_latest_results(benchmark_storage: BenchmarkStorage):
    """
    Test loading the most recent N results.

    Verifies:
    - Correct count of results returned
    - Results ordered by timestamp descending (newest first)
    - Respects count parameter
    """
    # Create results with different timestamps
    results = [
        BenchmarkResult(
            name=f"benchmark_{i}",
            timestamp=datetime(2025, 11, 5, 10, 0, 0) + timedelta(hours=i),
            duration_ms=100.0 + i,
            success=True,
            tags=[],
            metadata={},
        )
        for i in range(5)
    ]

    # Save each result separately with slight time difference
    for result in results:
        benchmark_storage.save_result(result)

    # Load latest 3 results
    latest_results = benchmark_storage.load_latest_results(count=3)

    assert len(latest_results) == 3
    # Verify descending order by timestamp
    for i in range(len(latest_results) - 1):
        assert latest_results[i].timestamp >= latest_results[i + 1].timestamp


def test_storage_cleanup_archival(benchmark_storage: BenchmarkStorage):
    """
    Test archiving old benchmark results.

    Verifies:
    - Old files moved to archive subdirectory
    - Recent files remain in main storage directory
    - Archive directory structure created
    """
    old_time = datetime.now() - timedelta(days=60)
    recent_time = datetime.now() - timedelta(days=5)

    old_result = BenchmarkResult(
        name="old_benchmark",
        timestamp=old_time,
        duration_ms=100.0,
        success=True,
        tags=[],
        metadata={},
    )

    recent_result = BenchmarkResult(
        name="recent_benchmark",
        timestamp=recent_time,
        duration_ms=100.0,
        success=True,
        tags=[],
        metadata={},
    )

    benchmark_storage.save_result(old_result)
    benchmark_storage.save_result(recent_result)

    # Archive results older than 30 days
    benchmark_storage.archive_old_results(days=30)

    storage_path = Path(benchmark_storage.storage_path)
    archive_path = storage_path / "archive"

    # Recent result should remain in main directory
    main_files = list(storage_path.glob("*.json"))
    assert any("recent_benchmark" in f.name for f in main_files)

    # Old result should be in archive
    assert archive_path.exists()
    archived_files = list(archive_path.glob("*.json"))
    assert any("old_benchmark" in f.name for f in archived_files)


# ============================================================================
# 2. Storage Formats Tests
# ============================================================================


def test_json_format_serialization(sample_results: List[BenchmarkResult]):
    """
    Test BenchmarkResult serialization to JSON.

    Verifies:
    - Valid JSON string produced
    - Contains expected fields (name, timestamp, duration_ms, etc.)
    - Proper data types preserved
    """
    json_str = ResultSerializer.to_json(sample_results)

    # Verify it's valid JSON
    parsed = json.loads(json_str)

    assert isinstance(parsed, list)
    assert len(parsed) == len(sample_results)

    # Verify expected fields
    first_result = parsed[0]
    assert "name" in first_result
    assert "timestamp" in first_result
    assert "duration_ms" in first_result
    assert "success" in first_result
    assert "tags" in first_result
    assert "metadata" in first_result

    # Verify data types
    assert isinstance(first_result["name"], str)
    assert isinstance(first_result["duration_ms"], (int, float))
    assert isinstance(first_result["success"], bool)
    assert isinstance(first_result["tags"], list)


def test_json_format_deserialization(sample_results: List[BenchmarkResult]):
    """
    Test JSON deserialization to BenchmarkResult.

    Verifies:
    - Correct object type (BenchmarkResult)
    - All fields restored correctly
    - Data integrity maintained (round-trip serialization)
    """
    json_str = ResultSerializer.to_json(sample_results)
    deserialized_results = ResultSerializer.from_json(json_str)

    assert len(deserialized_results) == len(sample_results)
    assert all(isinstance(r, BenchmarkResult) for r in deserialized_results)

    # Verify data integrity
    for original, deserialized in zip(sample_results, deserialized_results):
        assert deserialized.name == original.name
        assert deserialized.duration_ms == original.duration_ms
        assert deserialized.success == original.success
        assert deserialized.tags == original.tags


def test_csv_format_export(sample_results: List[BenchmarkResult]):
    """
    Test results export to CSV format.

    Verifies:
    - Valid CSV format produced
    - Proper headers present
    - Correct number of rows (header + data rows)
    """
    csv_str = ResultSerializer.to_csv(sample_results)

    lines = csv_str.strip().split("\n")

    # Verify header row
    assert len(lines) > 0
    header = lines[0]
    assert "name" in header.lower()
    assert "timestamp" in header.lower()
    assert "duration_ms" in header.lower()

    # Verify data rows
    assert len(lines) == len(sample_results) + 1  # +1 for header


def test_format_validation(
    benchmark_storage: BenchmarkStorage, sample_results: List[BenchmarkResult]
):
    """
    Test validation of storage format parameter.

    Verifies:
    - Valid formats accepted (json, csv)
    - Invalid formats raise ValueError
    - Clear error message provided
    """
    result = sample_results[0]

    # Valid formats should work
    benchmark_storage.save_result(result, format="json")

    # Invalid format should raise ValueError
    with pytest.raises(ValueError, match="Unsupported format"):
        benchmark_storage.save_result(result, format="invalid_format")


def test_custom_format_plugins():
    """
    Test registration and use of custom format plugins.

    Verifies:
    - Custom format can be registered
    - Registered serializer is used
    - Custom format appears in supported formats
    """

    def custom_serializer(results: List[BenchmarkResult]) -> str:
        """Mock custom serializer."""
        return "CUSTOM_FORMAT:" + ",".join(r.name for r in results)

    # Register custom format
    ResultSerializer.register_format("custom", custom_serializer)

    # Verify it's registered
    assert "custom" in ResultSerializer.supported_formats()

    # Verify custom serializer is used
    sample_results = [
        BenchmarkResult(
            name="test1",
            timestamp=datetime.now(),
            duration_ms=100.0,
            success=True,
            tags=[],
            metadata={},
        )
    ]

    output = ResultSerializer.serialize(sample_results, format="custom")
    assert output.startswith("CUSTOM_FORMAT:")
    assert "test1" in output


# ============================================================================
# 3. Result Querying Tests
# ============================================================================


def test_query_by_name(
    benchmark_storage: BenchmarkStorage, sample_results: List[BenchmarkResult]
):
    """
    Test querying results by benchmark name.

    Verifies:
    - Returns only matching results
    - Returns empty list if no match
    - Partial name matching works
    """
    # Save sample results
    benchmark_storage.save_results(sample_results)

    # Query by exact name
    results = benchmark_storage.query_by_name("test_benchmark_1")
    assert len(results) == 1
    assert results[0].name == "test_benchmark_1"

    # Query by partial name
    results = benchmark_storage.query_by_name("test_benchmark")
    assert len(results) == 3

    # Query with no matches
    results = benchmark_storage.query_by_name("nonexistent")
    assert len(results) == 0


def test_query_by_date_range(
    benchmark_storage: BenchmarkStorage, sample_results: List[BenchmarkResult]
):
    """
    Test querying results by date range.

    Verifies:
    - Returns only results within range
    - Boundary dates are inclusive
    - Empty range returns empty list
    """
    benchmark_storage.save_results(sample_results)

    base_time = datetime(2025, 11, 5, 10, 0, 0)

    # Query for middle result
    start = base_time + timedelta(minutes=30)
    end = base_time + timedelta(hours=1, minutes=30)

    results = benchmark_storage.query_by_date_range(start, end)

    assert len(results) == 1
    assert results[0].name == "test_benchmark_2"

    # Query for all results
    start = base_time - timedelta(hours=1)
    end = base_time + timedelta(hours=3)

    results = benchmark_storage.query_by_date_range(start, end)
    assert len(results) == 3


def test_query_by_tags(
    benchmark_storage: BenchmarkStorage, sample_results: List[BenchmarkResult]
):
    """
    Test querying results by tags.

    Verifies:
    - Returns results matching all specified tags
    - Handles multiple tags (AND logic)
    - Returns empty list if no matches
    """
    benchmark_storage.save_results(sample_results)

    # Query by single tag
    results = benchmark_storage.query_by_tags(["python"])
    assert len(results) == 2
    assert all("python" in r.tags for r in results)

    # Query by multiple tags (AND logic)
    results = benchmark_storage.query_by_tags(["python", "unit"])
    assert len(results) == 1
    assert results[0].name == "test_benchmark_1"

    # Query with no matches
    results = benchmark_storage.query_by_tags(["nonexistent"])
    assert len(results) == 0


def test_sorting_results(
    benchmark_storage: BenchmarkStorage, sample_results: List[BenchmarkResult]
):
    """
    Test sorting results by various criteria.

    Verifies:
    - Can sort by date (ascending/descending)
    - Can sort by duration_ms
    - Proper sort order maintained
    """
    benchmark_storage.save_results(sample_results)

    # Sort by date ascending
    results = benchmark_storage.load_latest_results(count=10)
    sorted_by_date_asc = benchmark_storage.sort_results(
        results, by="timestamp", ascending=True
    )

    for i in range(len(sorted_by_date_asc) - 1):
        assert sorted_by_date_asc[i].timestamp <= sorted_by_date_asc[i + 1].timestamp

    # Sort by duration descending
    sorted_by_duration_desc = benchmark_storage.sort_results(
        results, by="duration_ms", ascending=False
    )

    for i in range(len(sorted_by_duration_desc) - 1):
        assert (
            sorted_by_duration_desc[i].duration_ms
            >= sorted_by_duration_desc[i + 1].duration_ms
        )


def test_result_pagination(benchmark_storage: BenchmarkStorage):
    """
    Test pagination of large result sets.

    Verifies:
    - Correct page size honored
    - Correct page number retrieved
    - Total count accurate
    """
    # Create large result set
    large_result_set = [
        BenchmarkResult(
            name=f"benchmark_{i}",
            timestamp=datetime.now() + timedelta(seconds=i),
            duration_ms=100.0 + i,
            success=True,
            tags=[],
            metadata={},
        )
        for i in range(50)
    ]

    benchmark_storage.save_results(large_result_set)

    # Get first page
    page_1 = benchmark_storage.paginate_results(page=1, page_size=10)
    assert len(page_1["results"]) == 10
    assert page_1["page"] == 1
    assert page_1["page_size"] == 10
    assert page_1["total_count"] == 50
    assert page_1["total_pages"] == 5

    # Get middle page
    page_3 = benchmark_storage.paginate_results(page=3, page_size=10)
    assert len(page_3["results"]) == 10
    assert page_3["page"] == 3


# ============================================================================
# 4. Storage Management Tests
# ============================================================================


def test_automatic_result_archival(benchmark_storage: BenchmarkStorage):
    """
    Test automatic archival of old results.

    Verifies:
    - Results older than threshold archived automatically
    - Recent results retained in main storage
    - Archive directory structure correct
    """
    # Create old and recent results
    old_results = [
        BenchmarkResult(
            name=f"old_{i}",
            timestamp=datetime.now() - timedelta(days=45 + i),
            duration_ms=100.0,
            success=True,
            tags=[],
            metadata={},
        )
        for i in range(3)
    ]

    recent_results = [
        BenchmarkResult(
            name=f"recent_{i}",
            timestamp=datetime.now() - timedelta(days=i),
            duration_ms=100.0,
            success=True,
            tags=[],
            metadata={},
        )
        for i in range(3)
    ]

    for result in old_results + recent_results:
        benchmark_storage.save_result(result)

    # Trigger automatic archival (30 day threshold)
    benchmark_storage.archive_old_results(days=30)

    storage_path = Path(benchmark_storage.storage_path)
    archive_path = storage_path / "archive"

    # Verify recent results in main storage
    main_files = list(storage_path.glob("*.json"))
    assert all("recent_" in f.name for f in main_files)

    # Verify old results in archive
    archived_files = list(archive_path.glob("*.json"))
    assert len(archived_files) == 3


def test_storage_size_limits_rotation(benchmark_storage: BenchmarkStorage):
    """
    Test storage rotation when size limit exceeded.

    Verifies:
    - Oldest results deleted when limit exceeded
    - Total storage size stays under limit
    - Most recent results retained
    """
    # Set a small size limit (e.g., 1 MB)
    benchmark_storage.set_size_limit_mb(1.0)

    # Create many large results to exceed limit
    large_results = [
        BenchmarkResult(
            name=f"large_benchmark_{i}",
            timestamp=datetime.now() + timedelta(seconds=i),
            duration_ms=100.0,
            success=True,
            tags=[],
            metadata={"large_data": "x" * 10000},  # ~10KB per result
        )
        for i in range(150)  # ~1.5MB total
    ]

    for result in large_results:
        benchmark_storage.save_result(result)

    # Trigger rotation
    benchmark_storage.rotate_if_needed()

    # Verify size is under limit
    current_size_mb = benchmark_storage.get_storage_size_mb()
    assert current_size_mb <= 1.0

    # Verify most recent results retained
    storage_path = Path(benchmark_storage.storage_path)
    remaining_files = list(storage_path.glob("*.json"))
    assert len(remaining_files) > 0


def test_result_file_naming_conventions(benchmark_storage: BenchmarkStorage):
    """
    Test result files follow consistent naming pattern.

    Verifies:
    - Filename includes timestamp
    - Filename includes benchmark name
    - Proper file extension (.json)
    """
    result = BenchmarkResult(
        name="test_naming_convention",
        timestamp=datetime(2025, 11, 5, 14, 30, 45),
        duration_ms=100.0,
        success=True,
        tags=[],
        metadata={},
    )

    benchmark_storage.save_result(result)

    storage_path = Path(benchmark_storage.storage_path)
    result_files = list(storage_path.glob("*.json"))

    assert len(result_files) == 1
    filename = result_files[0].name

    # Verify naming pattern: YYYYMMDD_HHMMSS_benchmark_name.json
    assert "20251105" in filename  # Date
    assert "143045" in filename  # Time
    assert "test_naming_convention" in filename
    assert filename.endswith(".json")


def test_concurrent_write_handling(benchmark_storage: BenchmarkStorage):
    """
    Test concurrent writes don't corrupt data.

    Verifies:
    - All results saved successfully
    - No data corruption from race conditions
    - Proper file locking mechanism
    """
    results_per_thread = 10
    num_threads = 5

    def write_results(thread_id: int):
        """Write results from a thread."""
        for i in range(results_per_thread):
            result = BenchmarkResult(
                name=f"thread_{thread_id}_result_{i}",
                timestamp=datetime.now(),
                duration_ms=100.0 + thread_id + i,
                success=True,
                tags=[f"thread_{thread_id}"],
                metadata={},
            )
            benchmark_storage.save_result(result)

    # Create and start threads
    threads = []
    for thread_id in range(num_threads):
        thread = threading.Thread(target=write_results, args=(thread_id,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all results saved
    storage_path = Path(benchmark_storage.storage_path)
    result_files = list(storage_path.glob("*.json"))

    total_expected = results_per_thread * num_threads
    assert len(result_files) == total_expected

    # Verify no corrupted files
    for result_file in result_files:
        with open(result_file, "r") as f:
            data = json.load(f)
            assert "name" in data
            assert "duration_ms" in data
