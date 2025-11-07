"""
Lazy loading system for CBR case data.

This module provides on-demand loading of case embeddings and data with
intelligent caching and predictive preloading capabilities.
"""

import asyncio
import heapq
import logging
import threading
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Dict, List, Optional

from cachetools import LRUCache

from cbr_mcp_server.performance.data_models import LazyLoadingConfig

logger = logging.getLogger(__name__)


class LazyLoader:
    """
    Lazy loader for CBR case data with LRU caching and background loading.

    This class provides on-demand loading of case data with intelligent LRU caching
    to minimize database queries while preventing unbounded memory growth. It supports
    both synchronous on-demand loading and asynchronous background loading for
    predictive preloading.

    The cache uses a Least Recently Used (LRU) eviction policy: when the cache reaches
    its maximum size, the least recently accessed cases are automatically evicted to
    make room for new entries. This prevents memory leaks as the case base grows.

    Thread-safe for concurrent access.

    Attributes:
        case_loader: Function to load case data by case_id
        config: Configuration for lazy loading behavior (optional, uses defaults if not provided)
        _cache: LRUCache storing loaded cases with automatic eviction
        _lock: Threading lock for thread-safe access
    """

    def __init__(
        self,
        case_loader: Callable[[str], Dict[str, Any]],
        config: Optional[LazyLoadingConfig] = None,
    ) -> None:
        """
        Initialize LazyLoader with case loading function and configuration.

        Args:
            case_loader: Function that takes case_id and returns case data dict
            config: Optional configuration (uses defaults if not provided)
        """
        self.case_loader = case_loader
        self.config = config or LazyLoadingConfig()
        self._cache: LRUCache = LRUCache(maxsize=self.config.max_cache_size)
        self._lock = threading.Lock()

    def load_on_demand(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Load case data on-demand with caching.

        This method first checks if the case is already cached. If not,
        it loads the case using the provided case_loader function and
        caches the result for future requests.

        Thread-safe implementation uses double-check locking pattern
        to minimize lock contention while ensuring only one load per case.

        Args:
            case_id: Unique identifier for the case to load

        Returns:
            Case data dictionary if successful, None if loading fails
        """
        # Fast path: check cache without lock
        if case_id in self._cache:
            return self._cache[case_id]

        # Slow path: load with lock protection
        with self._lock:
            # Double-check after acquiring lock (another thread may have loaded it)
            if case_id in self._cache:
                return self._cache[case_id]

            try:
                # Load case data
                case_data = self.case_loader(case_id)

                # Cache the result
                self._cache[case_id] = case_data

                return case_data

            except Exception as e:
                logger.error(
                    "Failed to load case on demand",
                    extra={
                        "case_id": case_id,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    },
                    exc_info=True,
                )
                return None

    def schedule_background_load(self, case_ids: List[str]) -> "asyncio.Task[None]":
        """
        Schedule background loading of multiple cases.

        This method creates an asynchronous task that loads all specified
        cases in the background without blocking the caller. Useful for
        predictive preloading of cases that are likely to be accessed soon.

        Args:
            case_ids: List of case IDs to load in background

        Returns:
            asyncio.Task object representing the background loading operation
        """

        async def load_cases_async() -> None:
            """Async function to load all cases."""
            for case_id in case_ids:
                # Load each case (will cache automatically)
                self.load_on_demand(case_id)
                # Small sleep to yield control
                await asyncio.sleep(0)

        # Create and return background task
        task: asyncio.Task[None] = asyncio.create_task(load_cases_async())
        return task

    def is_loaded(self, case_id: str) -> bool:
        """
        Check if a case is already loaded in cache.

        Args:
            case_id: Case identifier to check

        Returns:
            True if case is in cache, False otherwise
        """
        return case_id in self._cache


class AccessPatternTracker:
    """
    Track and analyze case access patterns for predictive loading.

    This class maintains a sliding window of case accesses, learns sequential
    access patterns, and provides predictions for future accesses based on
    historical behavior.

    Attributes:
        window_hours: Time window in hours for tracking accesses
        min_frequency: Minimum frequency threshold for hot case identification
        _access_history: Stores all access records with timestamps
        _sequential_patterns: Tracks which cases follow which (for prediction)
        _last_accessed: Tracks the last accessed case for pattern learning
    """

    def __init__(self, window_hours: int = 24, min_frequency: int = 2) -> None:
        """
        Initialize AccessPatternTracker.

        Args:
            window_hours: Sliding window size in hours (default: 24)
            min_frequency: Minimum frequency threshold (default: 2)
        """
        self.window_hours = window_hours
        self.min_frequency = min_frequency

        # Store access history: case_id -> list of {"case_id": str, "timestamp": datetime}
        self._access_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        # Track sequential patterns: case_id -> {next_case_id: count}
        self._sequential_patterns: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        # Track last accessed case for pattern learning
        self._last_accessed: Optional[str] = None

    def record_access(self, case_id: str) -> None:
        """
        Record a case access with current timestamp.

        This method stores the access in the history and updates sequential
        patterns based on the previously accessed case.

        Args:
            case_id: ID of the case being accessed
        """
        current_time = datetime.now()

        # Record access in history
        access_record = {"case_id": case_id, "timestamp": current_time}
        self._access_history[case_id].append(access_record)

        # Update sequential patterns (if there was a previous access)
        if self._last_accessed is not None and self._last_accessed != case_id:
            self._sequential_patterns[self._last_accessed][case_id] += 1

        # Update last accessed
        self._last_accessed = case_id

    def _filter_by_window(self, accesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter accesses to only include those within the time window.

        Args:
            accesses: List of access records with timestamps

        Returns:
            Filtered list of access records within the window
        """
        current_time = datetime.now()
        window_start = current_time - timedelta(hours=self.window_hours)

        # Filter accesses that are strictly after window_start
        return [access for access in accesses if access["timestamp"] > window_start]

    def get_access_history(self, case_id: str) -> List[Dict[str, Any]]:
        """
        Get access history for a specific case within the time window.

        Args:
            case_id: ID of the case

        Returns:
            List of access records with case_id and timestamp fields,
            filtered to the sliding time window
        """
        if case_id not in self._access_history:
            return []

        all_accesses = self._access_history[case_id]
        return self._filter_by_window(all_accesses)

    def predict_next_accesses(self, case_id: str, limit: int = 5) -> List[str]:
        """
        Predict next likely accesses based on sequential patterns.

        Uses learned sequential patterns to predict which cases are likely
        to be accessed after the given case_id.

        Args:
            case_id: ID of the current case
            limit: Maximum number of predictions to return

        Returns:
            List of predicted case IDs, sorted by likelihood (most likely first)
        """
        if case_id not in self._sequential_patterns:
            return []

        # Get patterns for this case
        patterns = self._sequential_patterns[case_id]

        if not patterns:
            return []

        # Sort by count (descending) and return top predictions
        sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)

        predictions = [case_id for case_id, _ in sorted_patterns[:limit]]
        return predictions

    def get_hot_cases(self, limit: int = 10) -> List[str]:
        """
        Get most frequently accessed cases within the time window.

        Args:
            limit: Maximum number of hot cases to return

        Returns:
            List of case IDs sorted by access frequency (descending)
        """
        # Calculate access counts within window for all cases
        case_frequencies: Dict[str, int] = {}

        for case_id, accesses in self._access_history.items():
            filtered_accesses = self._filter_by_window(accesses)
            if filtered_accesses:
                case_frequencies[case_id] = len(filtered_accesses)

        # Sort by frequency (descending) and return top cases
        sorted_cases = sorted(
            case_frequencies.items(), key=lambda x: x[1], reverse=True
        )

        return [case_id for case_id, _ in sorted_cases[:limit]]

    def get_access_frequency(self, case_id: str) -> float:
        """
        Calculate access frequency (accesses per hour) for a case.

        Args:
            case_id: ID of the case

        Returns:
            Access frequency as accesses per hour within the time window.
            Returns 0 if the case has never been accessed.
        """
        if case_id not in self._access_history:
            return 0.0

        # Get accesses within window
        filtered_accesses = self._filter_by_window(self._access_history[case_id])

        if not filtered_accesses:
            return 0.0

        # Calculate frequency as accesses per hour
        access_count = len(filtered_accesses)
        frequency = access_count / self.window_hours

        return frequency

    def get_stats(self) -> Dict[str, Any]:
        """
        Get tracker statistics.

        Returns:
            Dictionary containing tracker statistics including total cases
            tracked, total accesses, and window configuration.
        """
        total_cases = len(self._access_history)
        total_accesses = sum(
            len(self._filter_by_window(accesses))
            for accesses in self._access_history.values()
        )

        return {
            "window_hours": self.window_hours,
            "min_frequency": self.min_frequency,
            "total_cases_tracked": total_cases,
            "total_accesses_in_window": total_accesses,
            "patterns_learned": len(self._sequential_patterns),
        }


class PreloadStrategy:
    """
    Strategy for identifying and scheduling preload candidates.

    This class analyzes access patterns to identify cases that should be
    preloaded in the background. It combines hot cases (frequently accessed)
    with predicted cases (likely to be accessed next) and schedules them
    for background loading based on configurable thresholds and batch sizes.

    Attributes:
        access_tracker: Tracker for analyzing access patterns
        load_scheduler: Scheduler for background loading tasks
        preload_threshold: Minimum frequency threshold for preloading
        batch_size: Maximum number of cases to preload in one batch
        lazy_loader: Optional LazyLoader instance for actual preloading
    """

    def __init__(
        self,
        access_tracker: "AccessPatternTracker",
        load_scheduler: "LoadScheduler",
        preload_threshold: float = 0.5,
        batch_size: int = 10,
        lazy_loader: Optional["LazyLoader"] = None,
    ) -> None:
        """
        Initialize PreloadStrategy.

        Args:
            access_tracker: AccessPatternTracker instance for pattern analysis
            load_scheduler: LoadScheduler instance for task scheduling
            preload_threshold: Minimum frequency threshold (default: 0.5)
            batch_size: Maximum batch size for preloading (default: 10)
            lazy_loader: Optional LazyLoader instance for actual preloading
        """
        self.access_tracker = access_tracker
        self.load_scheduler = load_scheduler
        self.preload_threshold = preload_threshold
        self.batch_size = batch_size
        self.lazy_loader = lazy_loader

    def identify_candidates(self) -> List[str]:
        """
        Identify preload candidates by combining hot cases and predictions.

        This method retrieves hot cases from the access tracker and combines
        them with predicted next accesses. The combined list is deduplicated
        to ensure each case appears only once.

        Returns:
            List of unique case IDs identified as preload candidates
        """
        # Get hot cases from access tracker
        hot_cases = self.access_tracker.get_hot_cases(limit=self.batch_size)

        # Get predictions based on last accessed case
        # Since we don't have direct access to current case, we predict from hot cases
        predictions: List[str] = []
        if hot_cases:
            # Use the most accessed case as basis for prediction
            predictions = self.access_tracker.predict_next_accesses(
                hot_cases[0], limit=self.batch_size
            )

        # Combine and deduplicate
        combined = hot_cases + predictions
        unique_candidates = list(dict.fromkeys(combined))  # Preserves order

        return unique_candidates

    def identify_preload_candidates(
        self, max_batch_size: Optional[int] = None
    ) -> List[str]:
        """
        Identify preload candidates with optional batch size limit.

        Alternative method for candidate identification that allows
        specifying a maximum batch size different from the instance
        batch_size attribute.

        Args:
            max_batch_size: Optional maximum number of candidates to return

        Returns:
            List of case IDs limited by max_batch_size if provided
        """
        candidates = self.identify_candidates()

        if max_batch_size is not None:
            return candidates[:max_batch_size]

        return candidates

    def filter_by_threshold(self, candidates_with_scores: List[str]) -> List[str]:
        """
        Filter candidates by access frequency threshold.

        This method evaluates each candidate's access frequency and only
        includes those that meet or exceed the preload_threshold.

        Args:
            candidates_with_scores: List of case IDs to filter

        Returns:
            List of case IDs that meet the frequency threshold
        """
        filtered = []

        for case_id in candidates_with_scores:
            frequency = self.access_tracker.get_access_frequency(case_id)

            # Include if frequency meets or exceeds threshold (>= comparison)
            if frequency >= self.preload_threshold:
                filtered.append(case_id)

        return filtered

    def schedule_preload(self) -> int:
        """
        Schedule preload tasks for identified candidates.

        This method orchestrates the complete preload process:
        1. Identify preload candidates
        2. Filter by frequency threshold
        3. Sort by frequency (most relevant first)
        4. Limit to batch_size
        5. Schedule tasks via load_scheduler

        Returns:
            Number of tasks successfully scheduled
        """
        try:
            # Skip if no lazy_loader configured
            if self.lazy_loader is None:
                return 0

            # Identify candidates
            candidates = self.identify_candidates()

            # Filter by threshold and create scored list
            scored_candidates: List[tuple[str, float]] = []
            for case_id in candidates:
                frequency = self.access_tracker.get_access_frequency(case_id)
                if frequency >= self.preload_threshold:
                    scored_candidates.append((case_id, frequency))

            # Sort by frequency (descending) to prioritize most relevant
            scored_candidates.sort(key=lambda x: x[1], reverse=True)

            # Limit to batch_size
            candidates_to_schedule = scored_candidates[: self.batch_size]

            # Schedule tasks
            scheduled_count = 0
            for case_id, frequency in candidates_to_schedule:
                try:
                    # Create async wrapper for synchronous load_on_demand
                    async def load_case_async(cid: str) -> Any:
                        """Async wrapper for synchronous case loading."""
                        return self.lazy_loader.load_on_demand(cid)

                    # Schedule task with priority based on frequency
                    priority = int(frequency * 10)  # Scale frequency to priority
                    self.load_scheduler.schedule_task(
                        task_func=lambda cid=case_id: load_case_async(cid),
                        task_id=case_id,
                        priority=priority,
                    )
                    scheduled_count += 1
                except Exception as e:
                    logger.warning(
                        "Failed to schedule preload task",
                        extra={
                            "case_id": case_id,
                            "frequency": frequency,
                            "priority": int(frequency * 10),
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                        },
                    )
                    continue

            return scheduled_count

        except Exception as e:
            logger.error(
                "Failed to schedule preload batch",
                extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "preload_threshold": self.preload_threshold,
                    "batch_size": self.batch_size,
                },
                exc_info=True,
            )
            return 0

    def set_scheduler(self, scheduler: "LoadScheduler") -> None:
        """
        Set or update the load scheduler reference.

        Args:
            scheduler: New LoadScheduler instance to use
        """
        self.load_scheduler = scheduler


class LoadScheduler:
    """
    Background task scheduler for managing load priorities.

    Schedules and executes async tasks with priority ordering and
    concurrency limits. Higher priority tasks execute first.

    Attributes:
        max_concurrent_tasks: Maximum number of tasks to execute concurrently
        _tasks: Dictionary storing task metadata
        _priority_queue: Heap-based priority queue for task ordering
        _cancelled: Set of cancelled task IDs
        _lock: Threading lock for thread-safe access
    """

    def __init__(self, max_concurrent_tasks: int = 5) -> None:
        """
        Initialize LoadScheduler.

        Args:
            max_concurrent_tasks: Maximum number of tasks to execute concurrently
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._priority_queue: List[tuple[int, str]] = []  # heap: (-priority, task_id)
        self._cancelled: set[str] = set()
        self._lock = threading.Lock()

    def schedule_task(
        self,
        task_func: Callable[[str], Awaitable[Any]],
        task_id: str,
        priority: int = 1,
    ) -> str:
        """
        Schedule a task for background execution.

        Time Complexity: O(log n) where n is the number of scheduled tasks.
        Space Complexity: O(1) for task insertion.

        Args:
            task_func: Async function that takes task_id and returns Awaitable
            task_id: Unique identifier for the task
            priority: Task priority (higher = executed first)

        Returns:
            The task_id that was scheduled
        """
        with self._lock:
            task_info = {
                "task_id": task_id,
                "task_func": task_func,
                "priority": priority,
            }
            self._tasks[task_id] = task_info
            # Use negative priority for max-heap behavior
            heapq.heappush(self._priority_queue, (-priority, task_id))
        return task_id

    def is_scheduled(self, task_id: str) -> bool:
        """
        Check if a task is scheduled (not cancelled).

        Args:
            task_id: Task identifier to check

        Returns:
            True if task is scheduled and not cancelled, False otherwise
        """
        with self._lock:
            return task_id in self._tasks and task_id not in self._cancelled

    def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task metadata.

        Args:
            task_id: Task identifier

        Returns:
            Dictionary with task_id and priority, or None if not found
        """
        with self._lock:
            if task_id not in self._tasks:
                return None
            task = self._tasks[task_id]
            return {"task_id": task["task_id"], "priority": task["priority"]}

    def get_execution_order(self) -> List[str]:
        """
        Get task IDs in priority order (highest first).

        Time Complexity: O(n log n) where n is the number of tasks.
        Space Complexity: O(n) for sorted list.

        Returns:
            List of task_ids sorted by priority descending
        """
        with self._lock:
            # Sort by priority (descending)
            sorted_tasks = sorted(
                self._tasks.values(), key=lambda t: t["priority"], reverse=True
            )
            return [task["task_id"] for task in sorted_tasks]

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.

        Args:
            task_id: Task identifier to cancel

        Returns:
            True if task was found and cancelled, False if task doesn't exist
        """
        with self._lock:
            if task_id not in self._tasks:
                return False
            self._cancelled.add(task_id)
            return True

    async def execute_all(self) -> List[Any]:
        """
        Execute all non-cancelled tasks with concurrency limit.

        Time Complexity: O(n log n) where n is the number of tasks.
        Space Complexity: O(n) for storing task results.

        Returns:
            List of results from executed tasks
        """
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        results = []

        async def execute_task(task_info: Dict[str, Any]) -> Any:
            """Execute a single task with semaphore control."""
            async with semaphore:
                task_func = task_info["task_func"]
                task_id = task_info["task_id"]
                result = await task_func(task_id)
                return result

        # Collect tasks to execute (skip cancelled)
        tasks_to_execute = []
        with self._lock:
            for _, task_id in sorted(self._priority_queue):
                if task_id not in self._cancelled:
                    task_info = self._tasks[task_id]
                    tasks_to_execute.append(task_info)

        # Execute all tasks concurrently (respecting semaphore limit)
        if tasks_to_execute:
            results = await asyncio.gather(
                *[execute_task(task) for task in tasks_to_execute]
            )

        return results
