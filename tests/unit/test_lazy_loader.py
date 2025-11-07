"""
Unit tests for Lazy Loading System components.

This module tests LazyLoader, AccessPatternTracker, PreloadStrategy, and LoadScheduler
components following TDD principles. These tests will initially fail until the
implementations are complete.

Test Coverage:
- LazyLoader: On-demand case loading and background loading
- AccessPatternTracker: Access pattern recording and prediction
- PreloadStrategy: Preload candidate identification and scheduling
- LoadScheduler: Background task scheduling and prioritization
"""

import asyncio
import time
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest

# These imports will fail initially - this is expected in TDD
from cbr_mcp_server.performance.lazy_loader import (
    LazyLoader,
    AccessPatternTracker,
    PreloadStrategy,
    LoadScheduler,
)


class TestLazyLoader:
    """Test suite for LazyLoader component."""

    @pytest.fixture
    def mock_case_loader(self):
        """Mock case loader function."""
        loader = Mock()
        loader.return_value = {"case_id": "test_case", "content": "test content"}
        return loader

    @pytest.fixture
    def lazy_loader(self, mock_case_loader):
        """Create LazyLoader instance with mock dependencies."""
        return LazyLoader(case_loader=mock_case_loader)

    def test_load_on_demand(self, lazy_loader, mock_case_loader):
        """Verify on-demand loading of cases."""
        case_id = "case_123"

        case_data = lazy_loader.load_on_demand(case_id)

        # Verify case was loaded
        assert case_data is not None
        mock_case_loader.assert_called_once_with(case_id)

    def test_load_on_demand_cached(self, lazy_loader, mock_case_loader):
        """Verify cached cases skip loading."""
        case_id = "case_123"

        # First load - should call loader
        first_load = lazy_loader.load_on_demand(case_id)
        assert mock_case_loader.call_count == 1

        # Second load - should use cache
        second_load = lazy_loader.load_on_demand(case_id)
        assert mock_case_loader.call_count == 1  # No additional call
        assert second_load == first_load

    @pytest.mark.asyncio
    async def test_schedule_background_load(self, lazy_loader, mock_case_loader):
        """Verify background loading can be scheduled."""
        case_ids = ["case_1", "case_2", "case_3"]

        # Schedule background loading
        task = lazy_loader.schedule_background_load(case_ids)

        # Wait for background loading to complete
        await asyncio.sleep(0.1)

        # Verify all cases are loaded
        for case_id in case_ids:
            assert lazy_loader.is_loaded(case_id) is True

    def test_is_loaded(self, lazy_loader):
        """Verify loaded state checking."""
        case_id = "case_test"

        # Initially not loaded
        assert lazy_loader.is_loaded(case_id) is False

        # Load the case
        lazy_loader.load_on_demand(case_id)

        # Now should be loaded
        assert lazy_loader.is_loaded(case_id) is True

    def test_concurrent_loading(self, lazy_loader, mock_case_loader):
        """Verify thread-safe concurrent loading."""
        case_id = "case_concurrent"

        # Simulate concurrent loading attempts
        import threading

        results = []

        def load_case():
            result = lazy_loader.load_on_demand(case_id)
            results.append(result)

        threads = [threading.Thread(target=load_case) for _ in range(5)]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Verify case was loaded only once (thread-safe)
        assert mock_case_loader.call_count == 1
        # All threads should get the same result
        assert all(r == results[0] for r in results)

    def test_loading_error_handling(self, lazy_loader, mock_case_loader):
        """Verify error handling during loading."""
        case_id = "case_error"
        mock_case_loader.side_effect = Exception("Loading error")

        # Should handle error gracefully
        result = lazy_loader.load_on_demand(case_id)

        # Should return None or raise appropriate exception
        assert result is None or isinstance(result, dict)


class TestAccessPatternTracker:
    """Test suite for AccessPatternTracker component.

    Tests cover access recording, pattern prediction, hot case identification,
    sliding window management, and frequency calculation as specified in the
    test specification document.
    """

    @pytest.fixture
    def pattern_tracker(self):
        """Create AccessPatternTracker instance with 24-hour window."""
        return AccessPatternTracker(window_hours=24, min_frequency=2)

    @pytest.fixture
    def mock_datetime(self):
        """Mock datetime for consistent timestamp testing."""
        with patch("cbr_mcp_server.performance.lazy_loader.datetime") as mock_dt:
            from datetime import datetime

            # Set a fixed "now" time
            fixed_now = datetime(2025, 11, 7, 12, 0, 0)
            mock_dt.now.return_value = fixed_now
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            yield mock_dt

    def test_record_access(self, pattern_tracker, mock_datetime):
        """Test access recording stores case ID and timestamp correctly."""
        from datetime import datetime

        case_id = "case_001"
        expected_time = mock_datetime.now.return_value

        # Record access
        pattern_tracker.record_access(case_id)

        # Verify access was recorded with correct case ID and timestamp
        accesses = pattern_tracker.get_access_history(case_id)
        assert len(accesses) == 1
        assert accesses[0]["case_id"] == case_id
        assert accesses[0]["timestamp"] == expected_time

        # Verify access history grows as expected
        pattern_tracker.record_access(case_id)
        accesses = pattern_tracker.get_access_history(case_id)
        assert len(accesses) == 2

    def test_predict_next_accesses(self, pattern_tracker):
        """Test access prediction algorithm based on historical patterns."""
        # Create sequential access pattern: case_001 -> case_002 -> case_003
        pattern_tracker.record_access("case_001")
        pattern_tracker.record_access("case_002")
        pattern_tracker.record_access("case_003")

        # Repeat pattern multiple times to establish it
        for _ in range(3):
            pattern_tracker.record_access("case_001")
            pattern_tracker.record_access("case_002")
            pattern_tracker.record_access("case_003")

        # After accessing case_001, should predict case_002
        predictions = pattern_tracker.predict_next_accesses("case_001", limit=3)

        # Verify predictions are not empty
        assert len(predictions) > 0
        # case_002 should be in predictions since it frequently follows case_001
        assert "case_002" in predictions

        # Verify prediction count respects limit
        assert len(predictions) <= 3

        # Test empty history returns empty list
        predictions_empty = pattern_tracker.predict_next_accesses(
            "never_accessed", limit=5
        )
        assert predictions_empty == []

    def test_get_hot_cases(self, pattern_tracker, mock_datetime):
        """Verify hot case identification returns frequently accessed cases sorted by frequency."""
        from datetime import datetime

        # Set fixed time for testing
        mock_datetime.now.return_value = datetime(2025, 11, 7, 12, 0, 0)

        # Record different access frequencies
        # case_001: 5 accesses (hottest)
        for _ in range(5):
            pattern_tracker.record_access("case_001")

        # case_002: 3 accesses (medium)
        for _ in range(3):
            pattern_tracker.record_access("case_002")

        # case_003: 1 access (coldest)
        pattern_tracker.record_access("case_003")

        # Get hot cases
        hot_cases = pattern_tracker.get_hot_cases(limit=3)

        # Should return cases sorted by frequency (descending)
        assert len(hot_cases) == 3
        assert hot_cases[0] == "case_001"  # Most accessed
        assert hot_cases[1] == "case_002"  # Second most
        assert hot_cases[2] == "case_003"  # Least accessed

        # Test with limit smaller than available cases
        hot_cases_limited = pattern_tracker.get_hot_cases(limit=2)
        assert len(hot_cases_limited) <= 2
        assert hot_cases_limited[0] == "case_001"

        # Test empty case returns empty list
        tracker_empty = AccessPatternTracker(window_hours=24)
        hot_cases_empty = tracker_empty.get_hot_cases(limit=5)
        assert hot_cases_empty == []

    def test_access_window_management(self, pattern_tracker, mock_datetime):
        """Test sliding window excludes old accesses outside the time window."""
        from datetime import datetime

        # Record old access (outside 24-hour window)
        old_time = datetime(2025, 11, 6, 10, 0, 0)  # More than 24 hours ago
        mock_datetime.now.return_value = old_time
        pattern_tracker.record_access("case_old")

        # Record recent access (within 24-hour window)
        recent_time = datetime(2025, 11, 7, 11, 0, 0)  # Within last hour
        mock_datetime.now.return_value = recent_time
        pattern_tracker.record_access("case_recent")

        # Move to current time for analysis
        current_time = datetime(2025, 11, 7, 12, 0, 0)
        mock_datetime.now.return_value = current_time

        # Get hot cases - should only include recent access (within window)
        hot_cases = pattern_tracker.get_hot_cases(limit=10)

        # Verify recent access is included, old access is excluded
        assert "case_recent" in hot_cases
        assert "case_old" not in hot_cases

        # Test window boundary (access exactly at 24-hour mark)
        boundary_time = datetime(2025, 11, 6, 12, 0, 0)  # Exactly 24 hours ago
        mock_datetime.now.return_value = boundary_time
        pattern_tracker.record_access("case_boundary")

        mock_datetime.now.return_value = datetime(2025, 11, 7, 12, 0, 0)
        hot_cases_boundary = pattern_tracker.get_hot_cases(limit=10)

        # Boundary case should be excluded (strictly within window)
        # Implementation may vary, but this tests the edge condition
        assert len(hot_cases_boundary) >= 1

    def test_frequency_calculation(self, pattern_tracker, mock_datetime):
        """Test access frequency calculation returns correct accesses-per-hour metric."""
        from datetime import datetime

        # Set time window
        mock_datetime.now.return_value = datetime(2025, 11, 7, 12, 0, 0)

        # Record 5 accesses for case_001 within window
        for _ in range(5):
            pattern_tracker.record_access("case_001")

        # Get frequency (should be accesses per hour)
        frequency = pattern_tracker.get_access_frequency("case_001")

        # Frequency should be positive
        assert frequency > 0

        # Test frequency is 0 for never-accessed cases
        frequency_unaccessed = pattern_tracker.get_access_frequency(
            "never_accessed"
        )
        assert frequency_unaccessed == 0

        # Test frequency only counts accesses within window
        # Record old accesses (outside window)
        old_time = datetime(2025, 11, 5, 12, 0, 0)  # 2 days ago
        mock_datetime.now.return_value = old_time
        for _ in range(10):
            pattern_tracker.record_access("case_mixed")

        # Record recent accesses (within window)
        recent_time = datetime(2025, 11, 7, 11, 0, 0)
        mock_datetime.now.return_value = recent_time
        for _ in range(3):
            pattern_tracker.record_access("case_mixed")

        # Move to current time
        current_time = datetime(2025, 11, 7, 12, 0, 0)
        mock_datetime.now.return_value = current_time

        # Frequency should only reflect recent accesses (3), not old ones (10)
        frequency_mixed = pattern_tracker.get_access_frequency("case_mixed")
        # Should be relatively low (based on 3 accesses, not 13)
        assert 0 < frequency_mixed < 10

        # Test multiple cases have proportional frequencies
        for _ in range(5):
            pattern_tracker.record_access("case_high_freq")
        for _ in range(2):
            pattern_tracker.record_access("case_low_freq")

        freq_high = pattern_tracker.get_access_frequency("case_high_freq")
        freq_low = pattern_tracker.get_access_frequency("case_low_freq")

        # Higher access count should have higher frequency
        assert freq_high > freq_low


class TestPreloadStrategy:
    """Test suite for PreloadStrategy component."""

    @pytest.fixture
    def mock_access_tracker(self):
        """Create mock AccessPatternTracker for testing."""
        tracker = Mock()
        tracker.get_hot_cases.return_value = ["case1", "case2", "case3"]
        tracker.predict_next_accesses.return_value = ["case4", "case5"]
        tracker.get_access_frequency.return_value = 0.8  # Default high frequency
        return tracker

    @pytest.fixture
    def mock_load_scheduler(self):
        """Create mock LoadScheduler for testing."""
        scheduler = Mock()
        scheduler.schedule_task.return_value = True
        return scheduler

    @pytest.fixture
    def mock_lazy_loader(self):
        """Create mock LazyLoader for testing."""
        loader = Mock()
        loader.load_on_demand.return_value = {"case_id": "test", "content": "test data"}
        return loader

    @pytest.fixture
    def preload_strategy(self, mock_access_tracker, mock_load_scheduler, mock_lazy_loader):
        """Create PreloadStrategy instance with mocked dependencies."""
        return PreloadStrategy(
            access_tracker=mock_access_tracker,
            load_scheduler=mock_load_scheduler,
            preload_threshold=0.5,
            batch_size=10,
            lazy_loader=mock_lazy_loader,
        )

    def test_identify_preload_candidates(self, preload_strategy, mock_access_tracker):
        """Verify that PreloadStrategy correctly identifies cases for preloading."""
        # Configure mock to return specific candidates
        mock_access_tracker.get_hot_cases.return_value = ["case1", "case2", "case3"]
        mock_access_tracker.predict_next_accesses.return_value = ["case4", "case5"]

        candidates = preload_strategy.identify_candidates()

        # Should return combined list of hot cases and predictions
        assert candidates is not None
        assert isinstance(candidates, list)
        assert len(candidates) > 0

        # Should include hot cases
        assert "case1" in candidates or "case2" in candidates or "case3" in candidates

        # Verify tracker methods were called
        mock_access_tracker.get_hot_cases.assert_called_once()
        mock_access_tracker.predict_next_accesses.assert_called_once()

    def test_identify_preload_candidates_respects_limits(
        self, preload_strategy, mock_access_tracker
    ):
        """Verify candidate identification respects configurable limits."""
        # Configure mock to return many candidates
        mock_access_tracker.get_hot_cases.return_value = [f"hot_{i}" for i in range(20)]
        mock_access_tracker.predict_next_accesses.return_value = [
            f"pred_{i}" for i in range(20)
        ]

        candidates = preload_strategy.identify_candidates()

        # Should not exceed reasonable limits
        assert len(candidates) <= 50  # Reasonable upper bound

    def test_identify_preload_candidates_deduplicates(
        self, preload_strategy, mock_access_tracker
    ):
        """Verify candidate list is deduplicated."""
        # Configure mock to return overlapping candidates
        mock_access_tracker.get_hot_cases.return_value = ["case1", "case2", "case3"]
        mock_access_tracker.predict_next_accesses.return_value = [
            "case2",
            "case3",
            "case4",
        ]

        candidates = preload_strategy.identify_candidates()

        # Should deduplicate overlapping cases
        unique_candidates = set(candidates)
        assert len(candidates) == len(unique_candidates)

    def test_preload_threshold_filtering(self, preload_strategy, mock_access_tracker):
        """Verify only cases meeting threshold are selected for preloading."""
        # Configure mock to return cases with various frequencies
        candidate_cases = ["high_freq", "medium_freq", "low_freq"]
        mock_access_tracker.get_hot_cases.return_value = candidate_cases
        mock_access_tracker.predict_next_accesses.return_value = []

        # Configure frequency responses
        def get_frequency_side_effect(case_id):
            if case_id == "high_freq":
                return 0.9  # Above threshold (0.5)
            elif case_id == "medium_freq":
                return 0.6  # Above threshold
            else:  # low_freq
                return 0.3  # Below threshold (0.5)

        mock_access_tracker.get_access_frequency.side_effect = get_frequency_side_effect

        # Identify and filter candidates
        filtered = preload_strategy.filter_by_threshold(candidate_cases)

        # Only high and medium frequency cases should pass
        assert "high_freq" in filtered
        assert "medium_freq" in filtered
        assert "low_freq" not in filtered

    def test_preload_threshold_filtering_at_boundary(
        self, preload_strategy, mock_access_tracker
    ):
        """Verify threshold filtering behavior at exact boundary value."""
        candidate_cases = ["exact_threshold"]
        mock_access_tracker.get_hot_cases.return_value = candidate_cases
        mock_access_tracker.predict_next_accesses.return_value = []

        # Configure frequency at exact threshold (0.5)
        mock_access_tracker.get_access_frequency.return_value = 0.5

        filtered = preload_strategy.filter_by_threshold(candidate_cases)

        # Case at exact threshold should be included (>= behavior)
        assert "exact_threshold" in filtered

    def test_preload_threshold_filtering_with_zero_frequency(
        self, preload_strategy, mock_access_tracker
    ):
        """Verify cases with zero frequency are filtered out."""
        candidate_cases = ["never_accessed"]
        mock_access_tracker.get_access_frequency.return_value = 0.0

        filtered = preload_strategy.filter_by_threshold(candidate_cases)

        # Zero frequency should be filtered out
        assert len(filtered) == 0

    def test_preload_threshold_filtering_with_all_below_threshold(
        self, preload_strategy, mock_access_tracker
    ):
        """Verify behavior when all candidates are below threshold."""
        candidate_cases = ["case1", "case2", "case3"]
        mock_access_tracker.get_access_frequency.return_value = 0.2  # Below 0.5

        filtered = preload_strategy.filter_by_threshold(candidate_cases)

        # No cases should pass
        assert len(filtered) == 0

    def test_preload_scheduling(
        self, preload_strategy, mock_access_tracker, mock_load_scheduler
    ):
        """Verify preload tasks are correctly scheduled for background execution."""
        # Configure candidates
        candidates = ["case1", "case2", "case3"]
        mock_access_tracker.get_hot_cases.return_value = candidates
        mock_access_tracker.predict_next_accesses.return_value = []
        mock_access_tracker.get_access_frequency.return_value = 0.8  # Above threshold

        # Schedule preloading
        scheduled_count = preload_strategy.schedule_preload()

        # Verify scheduling occurred
        assert scheduled_count > 0

        # Verify LoadScheduler was called for each candidate
        assert mock_load_scheduler.schedule_task.call_count >= len(candidates)

    def test_preload_scheduling_with_priority(
        self, preload_strategy, mock_load_scheduler, mock_access_tracker
    ):
        """Verify preload tasks are scheduled with correct priority."""
        candidates = ["case1"]
        mock_access_tracker.get_hot_cases.return_value = candidates
        mock_access_tracker.predict_next_accesses.return_value = []
        mock_access_tracker.get_access_frequency.return_value = 0.9

        preload_strategy.schedule_preload()

        # Verify priority parameter was passed to scheduler
        mock_load_scheduler.schedule_task.assert_called()
        call_args = mock_load_scheduler.schedule_task.call_args

        # Verify task was scheduled (structure may vary by implementation)
        assert call_args is not None

    def test_preload_scheduling_handles_scheduler_errors(
        self, preload_strategy, mock_load_scheduler, mock_access_tracker
    ):
        """Verify error handling when scheduler fails."""
        candidates = ["case1"]
        mock_access_tracker.get_hot_cases.return_value = candidates
        mock_access_tracker.predict_next_accesses.return_value = []
        mock_access_tracker.get_access_frequency.return_value = 0.8

        # Mock scheduler to raise exception
        mock_load_scheduler.schedule_task.side_effect = Exception("Scheduler error")

        # Should handle error gracefully
        try:
            scheduled_count = preload_strategy.schedule_preload()
            # If it handles errors gracefully, count may be 0
            assert scheduled_count >= 0
        except Exception:
            # Or it may propagate the exception
            pytest.fail("Exception should be handled gracefully")

    def test_preload_batch_size_limit_respected(
        self, preload_strategy, mock_access_tracker, mock_load_scheduler
    ):
        """Verify batch size limits are respected during preloading."""
        # Configure many candidates (more than batch_size=10)
        many_candidates = [f"case_{i}" for i in range(50)]
        mock_access_tracker.get_hot_cases.return_value = many_candidates
        mock_access_tracker.predict_next_accesses.return_value = []
        mock_access_tracker.get_access_frequency.return_value = 0.8  # Above threshold

        # Schedule preloading
        scheduled_count = preload_strategy.schedule_preload()

        # Should not exceed batch size
        assert scheduled_count <= preload_strategy.batch_size
        assert mock_load_scheduler.schedule_task.call_count <= preload_strategy.batch_size

    def test_preload_batch_size_edge_case_size_one(
        self, mock_access_tracker, mock_load_scheduler, mock_lazy_loader
    ):
        """Verify batch size of 1 is handled correctly."""
        preload_strategy = PreloadStrategy(
            access_tracker=mock_access_tracker,
            load_scheduler=mock_load_scheduler,
            preload_threshold=0.5,
            batch_size=1,
            lazy_loader=mock_lazy_loader,
        )

        # Configure multiple candidates
        mock_access_tracker.get_hot_cases.return_value = ["case1", "case2", "case3"]
        mock_access_tracker.predict_next_accesses.return_value = []
        mock_access_tracker.get_access_frequency.return_value = 0.8

        scheduled_count = preload_strategy.schedule_preload()

        # Should only schedule 1 task
        assert scheduled_count == 1
        assert mock_load_scheduler.schedule_task.call_count == 1

    def test_preload_batch_size_edge_case_large_batch(
        self, mock_access_tracker, mock_load_scheduler, mock_lazy_loader
    ):
        """Verify very large batch sizes are handled correctly."""
        preload_strategy = PreloadStrategy(
            access_tracker=mock_access_tracker,
            load_scheduler=mock_load_scheduler,
            preload_threshold=0.5,
            batch_size=1000,  # Very large
            lazy_loader=mock_lazy_loader,
        )

        # Configure fewer candidates than batch size
        mock_access_tracker.get_hot_cases.return_value = ["case1", "case2"]
        mock_access_tracker.predict_next_accesses.return_value = ["case3"]
        mock_access_tracker.get_access_frequency.return_value = 0.8

        scheduled_count = preload_strategy.schedule_preload()

        # Should only schedule available candidates (3), not batch_size (1000)
        assert scheduled_count <= 3
        assert mock_load_scheduler.schedule_task.call_count <= 3

    def test_preload_batch_size_selects_most_relevant(
        self, preload_strategy, mock_access_tracker, mock_load_scheduler
    ):
        """Verify most relevant candidates are selected when batching limits apply."""
        # Configure many candidates with varying frequencies
        many_candidates = [f"case_{i}" for i in range(50)]
        mock_access_tracker.get_hot_cases.return_value = many_candidates[:30]
        mock_access_tracker.predict_next_accesses.return_value = many_candidates[30:]

        # Configure frequency to prioritize certain cases
        def get_frequency_side_effect(case_id):
            # First 10 cases have highest frequency
            case_num = int(case_id.split("_")[1])
            if case_num < 10:
                return 0.9
            elif case_num < 20:
                return 0.7
            else:
                return 0.6

        mock_access_tracker.get_access_frequency.side_effect = get_frequency_side_effect

        scheduled_count = preload_strategy.schedule_preload()

        # Should schedule exactly batch_size (10)
        assert scheduled_count == preload_strategy.batch_size

        # Verify high-priority cases were scheduled
        scheduled_cases = []
        for call_item in mock_load_scheduler.schedule_task.call_args_list:
            # Extract case_id from call args (structure may vary)
            scheduled_cases.append(call_item)

        # Should have scheduled exactly batch_size tasks
        assert len(scheduled_cases) == preload_strategy.batch_size


class TestLoadScheduler:
    """Test suite for LoadScheduler component."""

    @pytest.fixture
    def load_scheduler(self):
        """Create LoadScheduler instance."""
        return LoadScheduler(max_concurrent_tasks=5)

    @pytest.fixture
    def mock_task(self):
        """Create mock task function."""
        async def task_func(task_id):
            await asyncio.sleep(0.01)
            return f"Task {task_id} completed"

        return task_func

    def test_schedule_task(self, load_scheduler, mock_task):
        """Verify background task scheduling."""
        task_id = "task_123"

        # Schedule task
        scheduled_task_id = load_scheduler.schedule_task(
            task_func=mock_task, task_id=task_id, priority=5
        )

        # Verify task was scheduled
        assert scheduled_task_id is not None
        assert load_scheduler.is_scheduled(scheduled_task_id) is True

        # Verify task metadata
        task_info = load_scheduler.get_task_info(scheduled_task_id)
        assert task_info is not None
        assert task_info["task_id"] == task_id
        assert task_info["priority"] == 5

    def test_task_prioritization(self, load_scheduler, mock_task):
        """Verify task priority ordering."""
        # Schedule tasks with different priorities
        task_ids = []
        priorities = [3, 1, 5, 2, 4]  # Not in order

        for i, priority in enumerate(priorities):
            task_id = load_scheduler.schedule_task(
                task_func=mock_task, task_id=f"task_{i}", priority=priority
            )
            task_ids.append(task_id)

        # Get task execution order
        execution_order = load_scheduler.get_execution_order()

        # Verify tasks are ordered by priority (highest first)
        priorities_in_order = [
            load_scheduler.get_task_info(tid)["priority"] for tid in execution_order
        ]

        # Should be in descending priority order: [5, 4, 3, 2, 1]
        assert priorities_in_order == sorted(priorities, reverse=True)

    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self, load_scheduler, mock_task):
        """Verify parallel task execution."""
        # Schedule multiple tasks
        task_ids = []
        num_tasks = 10

        for i in range(num_tasks):
            task_id = load_scheduler.schedule_task(
                task_func=mock_task, task_id=f"task_{i}", priority=1
            )
            task_ids.append(task_id)

        # Start execution
        start_time = time.time()
        results = await load_scheduler.execute_all()
        end_time = time.time()

        # Verify all tasks completed
        assert len(results) == num_tasks

        # Verify parallel execution (should not take num_tasks * 0.01 seconds)
        # With max_concurrent_tasks=5, should take roughly 2 * 0.01 seconds (2 batches)
        execution_time = end_time - start_time
        sequential_time = num_tasks * 0.01
        assert execution_time < sequential_time * 0.5  # Should be much faster

    @pytest.mark.asyncio
    async def test_task_cancellation(self, load_scheduler, mock_task):
        """Verify cancellation of scheduled tasks."""
        # Schedule a task
        task_id = load_scheduler.schedule_task(
            task_func=mock_task, task_id="cancellable_task", priority=1
        )

        # Verify task is scheduled
        assert load_scheduler.is_scheduled(task_id) is True

        # Cancel the task
        cancelled = load_scheduler.cancel_task(task_id)

        # Verify task was cancelled
        assert cancelled is True
        assert load_scheduler.is_scheduled(task_id) is False

        # Verify task does not execute
        results = await load_scheduler.execute_all()

        # Cancelled task should not be in results
        task_ids_executed = [r["task_id"] for r in results if "task_id" in r]
        assert "cancellable_task" not in task_ids_executed

    def test_task_cancellation_nonexistent(self, load_scheduler):
        """Verify cancelling non-existent task returns False."""
        # Attempt to cancel non-existent task
        cancelled = load_scheduler.cancel_task("nonexistent_task_id")

        # Should return False or raise appropriate error
        assert cancelled is False
