"""
Pytest configuration for memory baseline tests.

This conftest.py captures memory test results and exports them to JSON
for continuous performance tracking and comparison.
"""

import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

# Try to import psutil for additional machine info
try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None


class MemoryResultCollector:
    """Collects memory test results for JSON export."""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.machine_info: Optional[Dict[str, Any]] = None

    def add_result(
        self,
        test_name: str,
        fullname: str,
        status: str,
        memory_metrics: Optional[Dict[str, float]] = None,
        error_message: Optional[str] = None,
    ):
        """
        Add a test result to the collection.

        Args:
            test_name: Short test name
            fullname: Full test path
            status: "passed", "failed", or "skipped"
            memory_metrics: Dict with baseline_mb, peak_mb, final_mb, delta_mb
            error_message: Error message if test failed
        """
        result = {
            "name": test_name,
            "fullname": fullname,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if memory_metrics:
            result["memory_metrics"] = {
                "baseline_mb": round(memory_metrics.get("baseline_mb", 0.0), 2),
                "peak_mb": round(memory_metrics.get("peak_mb", 0.0), 2),
                "final_mb": round(memory_metrics.get("final_mb", 0.0), 2),
                "delta_mb": round(memory_metrics.get("delta_mb", 0.0), 2),
            }

        if error_message:
            result["error"] = error_message

        self.results.append(result)

    def set_machine_info(self):
        """Collect machine information for the report."""
        self.machine_info = {
            "node": platform.node(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "python_compiler": platform.python_compiler(),
            "python_implementation": platform.python_implementation(),
            "python_implementation_version": platform.python_version(),
            "python_version": platform.python_version(),
            "python_build": list(platform.python_build()),
            "release": platform.release(),
            "system": platform.system(),
        }

        # Add CPU info if available
        if HAS_PSUTIL:
            try:
                self.machine_info["cpu"] = {
                    "count": psutil.cpu_count(logical=True),
                    "count_physical": psutil.cpu_count(logical=False),
                }
            except Exception:
                pass

    def export_to_json(self, filepath: Path):
        """
        Export collected memory results to JSON file.

        Args:
            filepath: Path to output JSON file
        """
        if not self.machine_info:
            self.set_machine_info()

        output = {
            "machine_info": self.machine_info,
            "tests": self.results,
            "datetime": datetime.now(timezone.utc).isoformat(),
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r["status"] == "passed"),
            "failed": sum(1 for r in self.results if r["status"] == "failed"),
            "skipped": sum(1 for r in self.results if r["status"] == "skipped"),
        }

        # Write to file
        with open(filepath, "w") as f:
            json.dump(output, f, indent=4)

        print(f"\n✓ Memory baseline results exported to {filepath}")


class StartupResultCollector:
    """Collects startup timing test results for JSON export."""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.machine_info: Optional[Dict[str, Any]] = None

    def add_result(
        self,
        test_name: str,
        fullname: str,
        status: str,
        timing_metrics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ):
        """
        Add a startup test result to the collection.

        Args:
            test_name: Short test name
            fullname: Full test path
            status: "passed", "failed", or "skipped"
            timing_metrics: Dict with timing data (total_time, phase_timings, etc.)
            error_message: Error message if test failed
        """
        result = {
            "name": test_name,
            "fullname": fullname,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if timing_metrics:
            result["timing_metrics"] = {}

            # Round single timing values
            for key in [
                "total_time",
                "load_time",
                "db_init_time",
                "loading_time",
                "warm_time",
                "cold_time",
                "cache_benefit",
                "avg_time",
                "std_dev",
            ]:
                if key in timing_metrics:
                    result["timing_metrics"][key] = round(timing_metrics[key], 3)

            # Handle phase_timings as list of dicts
            if "phase_timings" in timing_metrics:
                result["timing_metrics"]["phase_timings"] = [
                    {"phase": phase_name, "time": round(phase_time, 3)}
                    for phase_name, phase_time in timing_metrics["phase_timings"]
                ]

            # Handle coefficient_of_variation
            if "coefficient_of_variation" in timing_metrics:
                result["timing_metrics"]["coefficient_of_variation"] = round(
                    timing_metrics["coefficient_of_variation"], 2
                )

            # Handle startup_times list
            if "startup_times" in timing_metrics:
                result["timing_metrics"]["startup_times"] = [
                    round(t, 3) for t in timing_metrics["startup_times"]
                ]

        if error_message:
            result["error"] = error_message

        self.results.append(result)

    def set_machine_info(self):
        """Collect machine information for the report."""
        self.machine_info = {
            "node": platform.node(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "python_compiler": platform.python_compiler(),
            "python_implementation": platform.python_implementation(),
            "python_implementation_version": platform.python_version(),
            "python_version": platform.python_version(),
            "python_build": list(platform.python_build()),
            "release": platform.release(),
            "system": platform.system(),
        }

        # Add CPU info if available
        if HAS_PSUTIL:
            try:
                self.machine_info["cpu"] = {
                    "count": psutil.cpu_count(logical=True),
                    "count_physical": psutil.cpu_count(logical=False),
                }
            except Exception:
                pass

    def export_to_json(self, filepath: Path):
        """
        Export collected startup results to JSON file.

        Args:
            filepath: Path to output JSON file
        """
        if not self.machine_info:
            self.set_machine_info()

        output = {
            "machine_info": self.machine_info,
            "tests": self.results,
            "datetime": datetime.now(timezone.utc).isoformat(),
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r["status"] == "passed"),
            "failed": sum(1 for r in self.results if r["status"] == "failed"),
            "skipped": sum(1 for r in self.results if r["status"] == "skipped"),
        }

        # Write to file
        with open(filepath, "w") as f:
            json.dump(output, f, indent=4)

        print(f"\n✓ Startup baseline results exported to {filepath}")


@pytest.fixture(scope="session")
def memory_collector(request):
    """Session-scoped fixture providing the memory result collector."""
    collector = MemoryResultCollector()
    collector.set_machine_info()
    request.session.memory_collector = collector
    return collector


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results."""
    outcome = yield
    report = outcome.get_result()

    # Only process test call phase (not setup/teardown)
    if report.when == "call":
        test_name = item.name
        fullname = item.nodeid

        # Determine status
        if report.passed:
            status = "passed"
        elif report.failed:
            status = "failed"
        elif report.skipped:
            status = "skipped"
        else:
            status = "unknown"

        # Get error message for failed tests
        error_message = None
        if report.failed and hasattr(report, "longrepr"):
            error_message = str(report.longrepr)[:200]  # Truncate long errors

        # Handle memory tests
        if hasattr(item.session, "memory_collector"):
            collector = item.session.memory_collector

            # Check if this is a memory test by looking at the test module
            if "test_memory_baseline" in fullname:
                collector.add_result(
                    test_name=test_name,
                    fullname=fullname,
                    status=status,
                    memory_metrics=None,  # Will be updated by fixture
                    error_message=error_message,
                )

        # Handle startup tests
        if hasattr(item.session, "startup_collector"):
            collector = item.session.startup_collector

            # Check if this is a startup test by looking at the test module
            if "test_startup_baseline" in fullname or "test_startup_benchmarks" in fullname:
                collector.add_result(
                    test_name=test_name,
                    fullname=fullname,
                    status=status,
                    timing_metrics=None,  # Will be updated by fixture
                    error_message=error_message,
                )


@pytest.fixture(scope="session", autouse=True)
def export_memory_results(request, memory_collector):
    """
    Session-scoped fixture to export memory results at end of test session.

    This fixture runs automatically and exports results after all tests complete.
    """
    # Store collector in session for hook access
    request.session.memory_collector = memory_collector

    # Yield to run tests
    yield

    # After all tests complete, export results
    project_root = Path(__file__).parent.parent.parent
    output_file = project_root / "baseline_memory_usage.json"

    memory_collector.export_to_json(output_file)


@pytest.fixture
def memory_result_tracker(memory_collector, request):
    """
    Fixture that allows tests to report their memory metrics.

    Usage in tests:
        def test_example(memory_result_tracker):
            memory_metrics = measure_memory_delta(some_function)
            memory_result_tracker.record(memory_metrics)
    """

    class MemoryTracker:
        def __init__(self, collector, test_item):
            self.collector = collector
            self.test_item = test_item
            self.metrics = None

        def record(self, memory_metrics: Dict[str, float]):
            """Record memory metrics for this test."""
            self.metrics = memory_metrics

    tracker = MemoryTracker(memory_collector, request.node)

    yield tracker

    # After test completes, update the result with metrics if recorded
    if tracker.metrics:
        # Find and update the corresponding result
        test_fullname = request.node.nodeid
        for result in memory_collector.results:
            if result["fullname"] == test_fullname:
                result["memory_metrics"] = {
                    "baseline_mb": round(tracker.metrics.get("baseline_mb", 0.0), 2),
                    "peak_mb": round(tracker.metrics.get("peak_mb", 0.0), 2),
                    "final_mb": round(tracker.metrics.get("final_mb", 0.0), 2),
                    "delta_mb": round(tracker.metrics.get("delta_mb", 0.0), 2),
                }
                break


# ============================================================================
# Startup Timing Test Infrastructure
# ============================================================================


@pytest.fixture(scope="session")
def startup_collector(request):
    """Session-scoped fixture providing the startup result collector."""
    collector = StartupResultCollector()
    collector.set_machine_info()
    request.session.startup_collector = collector
    return collector


@pytest.fixture(scope="session", autouse=True)
def export_startup_results(request, startup_collector):
    """
    Session-scoped fixture to export startup results at end of test session.

    This fixture runs automatically and exports results after all tests complete.
    """
    # Store collector in session for hook access
    request.session.startup_collector = startup_collector

    # Yield to run tests
    yield

    # After all tests complete, export results
    project_root = Path(__file__).parent.parent.parent
    output_file = project_root / "baseline_startup_time.json"

    startup_collector.export_to_json(output_file)


@pytest.fixture
def startup_result_tracker(startup_collector, request):
    """
    Fixture that allows tests to report their timing metrics.

    Usage in tests:
        def test_example(startup_result_tracker):
            timing_metrics = {"total_time": 2.5, "phase_timings": [("init", 1.0)]}
            startup_result_tracker.record(timing_metrics)
    """

    class StartupTracker:
        def __init__(self, collector, test_item):
            self.collector = collector
            self.test_item = test_item
            self.metrics = None

        def record(self, timing_metrics: Dict[str, Any]):
            """Record timing metrics for this test."""
            self.metrics = timing_metrics

    tracker = StartupTracker(startup_collector, request.node)

    yield tracker

    # After test completes, update the result with metrics if recorded
    if tracker.metrics:
        # Find and update the corresponding result
        test_fullname = request.node.nodeid
        for result in startup_collector.results:
            if result["fullname"] == test_fullname:
                # Build the timing_metrics dict
                timing_data = {}

                # Add single timing values
                for key in [
                    "total_time",
                    "load_time",
                    "db_init_time",
                    "loading_time",
                    "warm_time",
                    "cold_time",
                    "cache_benefit",
                    "avg_time",
                    "std_dev",
                ]:
                    if key in tracker.metrics:
                        timing_data[key] = round(tracker.metrics[key], 3)

                # Handle phase_timings as list of dicts
                if "phase_timings" in tracker.metrics:
                    timing_data["phase_timings"] = [
                        {"phase": phase_name, "time": round(phase_time, 3)}
                        for phase_name, phase_time in tracker.metrics["phase_timings"]
                    ]

                # Handle coefficient_of_variation
                if "coefficient_of_variation" in tracker.metrics:
                    timing_data["coefficient_of_variation"] = round(
                        tracker.metrics["coefficient_of_variation"], 2
                    )

                # Handle startup_times list
                if "startup_times" in tracker.metrics:
                    timing_data["startup_times"] = [
                        round(t, 3) for t in tracker.metrics["startup_times"]
                    ]

                result["timing_metrics"] = timing_data
                break


# ============================================================================
# Shared Fixtures for Memory Optimization (Session-Scoped)
# ============================================================================


@pytest.fixture(scope="session")
def shared_embedding_model(request):
    """
    Session-scoped shared embedding model - ONE instance for entire test session.

    This fixture ensures only ONE embedding model exists in memory across all
    test modules, preventing memory regression from multiple model instances.

    Memory optimization: Reduces peak memory by ~700MB by sharing a single
    embedding model instance instead of creating one per test module.
    """
    import gc

    try:
        from cbr_mcp_server.performance.production_cbr_retriever import (
            LazyEmbeddingModel,
        )
    except ImportError:
        pytest.skip("CBR server components not available")

    # Create ONE embedding model for entire session
    embedding_model = LazyEmbeddingModel(
        model_name="nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True
    )

    yield embedding_model

    # Cleanup: explicitly delete embedding model and force garbage collection
    del embedding_model
    gc.collect()


@pytest.fixture(scope="session")
def shared_cbr_retriever(request, shared_embedding_model):
    """
    Session-scoped shared CBR retriever - ONE instance for entire test session.

    This fixture uses the shared_embedding_model to ensure only ONE retriever
    with ONE embedding model exists in memory across all test modules.

    Memory optimization: Prevents duplicate retriever/model instances across
    test modules, reducing memory footprint by ~700MB.
    """
    import gc

    try:
        from cbr_mcp_server.performance.production_cbr_retriever import (
            ProductionCBRRetriever,
        )
    except ImportError:
        pytest.skip("CBR server components not available")

    # Initialize retriever with shared embedding model
    test_db_path = Path("./db")
    retriever = ProductionCBRRetriever(
        db_path=str(test_db_path), embedding_model=shared_embedding_model
    )

    # Trigger lazy initialization with a test query
    try:
        retriever.retrieve(query="test", max_results=1)
    except Exception as e:
        pytest.skip(f"Failed to initialize shared CBR retriever: {e}")

    yield retriever

    # Cleanup: explicitly delete retriever and force garbage collection
    del retriever
    gc.collect()
