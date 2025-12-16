"""
Benchmark result storage module.

This module provides comprehensive storage and retrieval capabilities for benchmark results,
including multiple storage formats, querying, archival, and concurrent access support.
"""

import csv
import io
import json
import os
import shutil
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class BenchmarkResult:
    """
    Represents a single benchmark result.

    Attributes:
        name: Benchmark name/identifier
        timestamp: When the benchmark was executed
        duration_ms: Execution duration in milliseconds
        success: Whether the benchmark succeeded
        tags: List of tags for categorization
        metadata: Additional metadata as key-value pairs
    """

    name: str
    timestamp: datetime
    duration_ms: float
    success: bool
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResultSerializer:
    """
    Handles serialization and deserialization of benchmark results.

    Supports multiple formats: JSON, CSV, and custom formats via plugin system.
    """

    _custom_formats: Dict[str, Callable[[List[BenchmarkResult]], str]] = {}

    @classmethod
    def to_json(cls, results: List[BenchmarkResult]) -> str:
        """
        Serialize results to JSON string.

        Args:
            results: List of BenchmarkResult objects

        Returns:
            JSON string representation
        """

        def serialize_result(result: BenchmarkResult) -> Dict[str, Any]:
            """Convert BenchmarkResult to JSON-serializable dict."""
            data = asdict(result)
            # Convert datetime to ISO format string
            data["timestamp"] = result.timestamp.isoformat()
            return data

        serialized = [serialize_result(r) for r in results]
        return json.dumps(serialized, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> List[BenchmarkResult]:
        """
        Deserialize results from JSON string.

        Args:
            json_str: JSON string to parse

        Returns:
            List of BenchmarkResult objects
        """
        data = json.loads(json_str)
        results = []

        for item in data:
            # Convert ISO format string back to datetime
            item["timestamp"] = datetime.fromisoformat(item["timestamp"])
            results.append(BenchmarkResult(**item))

        return results

    @classmethod
    def to_csv(cls, results: List[BenchmarkResult]) -> str:
        """
        Serialize results to CSV string.

        Args:
            results: List of BenchmarkResult objects

        Returns:
            CSV string with header row
        """
        if not results:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "name",
                "timestamp",
                "duration_ms",
                "success",
                "tags",
                "metadata",
            ],
        )

        writer.writeheader()
        for result in results:
            row = asdict(result)
            # Convert complex types to strings for CSV
            row["timestamp"] = result.timestamp.isoformat()
            row["tags"] = json.dumps(result.tags)
            row["metadata"] = json.dumps(result.metadata)
            writer.writerow(row)

        return output.getvalue()

    @classmethod
    def register_format(
        cls, name: str, serializer: Callable[[List[BenchmarkResult]], str]
    ) -> None:
        """
        Register a custom serialization format.

        Args:
            name: Format name
            serializer: Function that converts List[BenchmarkResult] to string
        """
        cls._custom_formats[name] = serializer

    @classmethod
    def supported_formats(cls) -> List[str]:
        """
        Get list of supported format names.

        Returns:
            List of format names (includes 'json', 'csv', and custom formats)
        """
        return ["json", "csv"] + list(cls._custom_formats.keys())

    @classmethod
    def serialize(cls, results: List[BenchmarkResult], format: str) -> str:
        """
        Serialize results using specified format.

        Args:
            results: List of BenchmarkResult objects
            format: Format name ('json', 'csv', or custom)

        Returns:
            Serialized string

        Raises:
            ValueError: If format is not supported
        """
        if format == "json":
            return cls.to_json(results)
        elif format == "csv":
            return cls.to_csv(results)
        elif format in cls._custom_formats:
            return cls._custom_formats[format](results)
        else:
            raise ValueError(f"Unsupported format: {format}")


class BenchmarkStorage:
    """
    Manages storage, retrieval, and querying of benchmark results.

    Features:
    - Multiple storage formats (JSON, CSV)
    - Querying by name, date range, tags
    - Automatic archival of old results
    - Storage size management with rotation
    - Concurrent write support with thread safety
    """

    def __init__(self, storage_path: str = "./benchmark_results"):
        """
        Initialize benchmark storage.

        Args:
            storage_path: Directory path for storing benchmark results
        """
        self.storage_path = storage_path
        self._write_lock = threading.Lock()
        self._size_limit_mb: Optional[float] = None

        # Create storage directory if it doesn't exist
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)

    def save_result(
        self, result: BenchmarkResult, format: str = "json"
    ) -> None:
        """
        Save a single benchmark result.

        Args:
            result: BenchmarkResult to save
            format: Storage format ('json' or 'csv')

        Raises:
            ValueError: If format is not supported
        """
        if format not in ["json", "csv"]:
            raise ValueError(f"Unsupported format: {format}")

        with self._write_lock:
            # Generate filename: YYYYMMDD_HHMMSS_benchmark_name.json
            timestamp_str = result.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp_str}_{result.name}.{format}"
            filepath = Path(self.storage_path) / filename

            # Serialize single result as a dict (not array)
            if format == "json":
                data = asdict(result)
                data["timestamp"] = result.timestamp.isoformat()
                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2)
            elif format == "csv":
                csv_str = ResultSerializer.to_csv([result])
                with open(filepath, "w") as f:
                    f.write(csv_str)

    def save_results(
        self, results: List[BenchmarkResult], format: str = "json"
    ) -> None:
        """
        Save multiple benchmark results in batch.

        Args:
            results: List of BenchmarkResult objects to save
            format: Storage format ('json' or 'csv')

        Raises:
            ValueError: If format is not supported
        """
        if format not in ["json", "csv"]:
            raise ValueError(f"Unsupported format: {format}")

        if not results:
            return

        with self._write_lock:
            # Generate filename based on first result's timestamp
            timestamp_str = results[0].timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp_str}_batch.{format}"
            filepath = Path(self.storage_path) / filename

            if format == "json":
                json_str = ResultSerializer.to_json(results)
                with open(filepath, "w") as f:
                    f.write(json_str)
            elif format == "csv":
                csv_str = ResultSerializer.to_csv(results)
                with open(filepath, "w") as f:
                    f.write(csv_str)

    def load_results(self, filename: str) -> List[BenchmarkResult]:
        """
        Load results from a specific file.

        Args:
            filename: Name of the file to load (not full path)

        Returns:
            List of BenchmarkResult objects

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        filepath = Path(self.storage_path) / filename

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filename}")

        with open(filepath, "r") as f:
            content = f.read()

        if filename.endswith(".json"):
            data = json.loads(content)
            # Handle both single result (dict) and batch results (list)
            if isinstance(data, dict):
                data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                return [BenchmarkResult(**data)]
            else:  # list
                return ResultSerializer.from_json(content)
        else:
            raise ValueError(f"Unsupported file format: {filename}")

    def load_latest_results(self, count: int = 10) -> List[BenchmarkResult]:
        """
        Load the most recent N results.

        Args:
            count: Number of results to load

        Returns:
            List of BenchmarkResult objects, sorted by timestamp descending
        """
        storage_path = Path(self.storage_path)
        json_files = sorted(
            storage_path.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        all_results = []
        for json_file in json_files:
            try:
                results = self.load_results(json_file.name)
                all_results.extend(results)
            except (json.JSONDecodeError, ValueError):
                # Skip corrupted files
                continue

        # Sort by timestamp descending and return top N
        all_results.sort(key=lambda r: r.timestamp, reverse=True)
        return all_results[:count]

    def archive_old_results(self, days: int = 30) -> None:
        """
        Archive results older than specified days.

        Moves old result files to 'archive' subdirectory.

        Args:
            days: Age threshold in days
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        storage_path = Path(self.storage_path)
        archive_path = storage_path / "archive"
        archive_path.mkdir(exist_ok=True)

        for json_file in storage_path.glob("*.json"):
            try:
                results = self.load_results(json_file.name)
                # Check if any result in the file is older than cutoff
                if any(r.timestamp < cutoff_date for r in results):
                    # Move to archive
                    shutil.move(str(json_file), str(archive_path / json_file.name))
            except (json.JSONDecodeError, ValueError, FileNotFoundError):
                # Skip corrupted or missing files
                continue

    def query_by_name(self, name: str) -> List[BenchmarkResult]:
        """
        Query results by benchmark name (partial match).

        Args:
            name: Benchmark name or partial name to search for

        Returns:
            List of matching BenchmarkResult objects
        """
        all_results = self._load_all_results()
        return [r for r in all_results if name in r.name]

    def query_by_date_range(
        self, start: datetime, end: datetime
    ) -> List[BenchmarkResult]:
        """
        Query results within a date range (inclusive).

        Args:
            start: Start datetime
            end: End datetime

        Returns:
            List of BenchmarkResult objects within range
        """
        all_results = self._load_all_results()
        return [r for r in all_results if start <= r.timestamp <= end]

    def query_by_tags(self, tags: List[str]) -> List[BenchmarkResult]:
        """
        Query results by tags (AND logic - must have all tags).

        Args:
            tags: List of tags to match

        Returns:
            List of BenchmarkResult objects with all specified tags
        """
        all_results = self._load_all_results()
        return [r for r in all_results if all(tag in r.tags for tag in tags)]

    def sort_results(
        self, results: List[BenchmarkResult], by: str, ascending: bool = True
    ) -> List[BenchmarkResult]:
        """
        Sort results by specified field.

        Args:
            results: List of results to sort
            by: Field name to sort by ('timestamp', 'duration_ms', 'name')
            ascending: Sort order (True for ascending, False for descending)

        Returns:
            Sorted list of BenchmarkResult objects
        """
        return sorted(results, key=lambda r: getattr(r, by), reverse=not ascending)

    def paginate_results(
        self, page: int = 1, page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Paginate results.

        Args:
            page: Page number (1-indexed)
            page_size: Number of results per page

        Returns:
            Dictionary with paginated results and metadata
        """
        all_results = self._load_all_results()
        all_results.sort(key=lambda r: r.timestamp, reverse=True)

        total_count = len(all_results)
        total_pages = (total_count + page_size - 1) // page_size

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        return {
            "results": all_results[start_idx:end_idx],
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
        }

    def set_size_limit_mb(self, limit: float) -> None:
        """
        Set storage size limit in megabytes.

        Args:
            limit: Size limit in MB
        """
        self._size_limit_mb = limit

    def rotate_if_needed(self) -> None:
        """
        Rotate (delete) oldest files if storage size exceeds limit.

        Only runs if size limit has been set via set_size_limit_mb().
        """
        if self._size_limit_mb is None:
            return

        while self.get_storage_size_mb() > self._size_limit_mb:
            # Find and delete oldest file
            storage_path = Path(self.storage_path)
            json_files = sorted(storage_path.glob("*.json"), key=lambda p: p.stat().st_mtime)

            if not json_files:
                break

            oldest_file = json_files[0]
            oldest_file.unlink()

    def get_storage_size_mb(self) -> float:
        """
        Get current storage size in megabytes.

        Returns:
            Total size of all result files in MB
        """
        storage_path = Path(self.storage_path)
        total_bytes = sum(
            f.stat().st_size for f in storage_path.glob("*.json") if f.is_file()
        )
        return total_bytes / (1024 * 1024)

    def _load_all_results(self) -> List[BenchmarkResult]:
        """
        Load all results from storage directory.

        Returns:
            List of all BenchmarkResult objects
        """
        storage_path = Path(self.storage_path)
        all_results = []

        for json_file in storage_path.glob("*.json"):
            try:
                results = self.load_results(json_file.name)
                all_results.extend(results)
            except (json.JSONDecodeError, ValueError, FileNotFoundError):
                # Skip corrupted or missing files
                continue

        return all_results
