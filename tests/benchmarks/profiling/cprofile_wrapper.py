"""
cProfile Integration Wrapper for CBR MCP Server.

This module provides a convenient wrapper around Python's cProfile module
for profiling CBR server operations. It simplifies the process of profiling
synchronous and async functions, collecting structured profile data, and
outputting results in multiple formats.

Key Features:
- ProfilerWrapper class for flexible profiling workflows
- Context manager support for profiling code blocks
- Decorators for profiling functions (sync and async)
- Multiple output formats (text, dict, .prof file)
- Top N functions by various metrics
- State management with error handling

Usage Examples:
    # Context manager
    with ProfilerWrapper() as profiler:
        # code to profile
        pass
    stats = profiler.get_stats()

    # Decorator
    @profile_function(sort_by="time")
    def my_function():
        pass

    # Manual control
    profiler = ProfilerWrapper()
    profiler.start()
    # code to profile
    profiler.stop()
    profiler.print_stats()
"""

import asyncio
import cProfile
import functools
import io
import pstats
from typing import Any, Callable, Dict, List, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class ProfilerWrapper:
    """
    Wrapper around cProfile for convenient profiling of CBR operations.

    This class provides a high-level interface to cProfile with support for
    context managers, manual start/stop control, and multiple output formats.

    Supports nested profiling by temporarily pausing outer profilers when
    inner profilers start.

    Attributes:
        sort_by: Sorting criteria for profile output ('cumulative', 'time', 'calls')
        _profiler: Internal cProfile.Profile instance
        _is_running: State flag indicating if profiler is active
        _stats: Cached pstats.Stats object after profiling
        _was_paused: Flag indicating if profiler was paused for nested profiling
    """

    # Class-level stack to track active profilers for nested support
    _active_profilers: List['ProfilerWrapper'] = []

    def __init__(self, sort_by: str = "cumulative"):
        """
        Initialize ProfilerWrapper with specified sort order.

        Args:
            sort_by: Sort criterion ('cumulative', 'time', 'calls', etc.)
        """
        self.sort_by = sort_by
        self._profiler = cProfile.Profile()
        self._is_running = False
        self._stats: Optional[pstats.Stats] = None
        self._was_paused = False

    def start(self):
        """
        Start profiling.

        If another profiler is active, it will be paused to allow nested profiling.

        Raises:
            RuntimeError: If profiler is already running
        """
        if self._is_running:
            raise RuntimeError("Profiler is already running")

        # Pause any currently active profiler to support nesting
        if ProfilerWrapper._active_profilers:
            current = ProfilerWrapper._active_profilers[-1]
            if current._is_running and not current._was_paused:
                try:
                    current._profiler.disable()
                    current._was_paused = True
                except Exception:
                    # If disable fails, continue anyway
                    pass

        try:
            self._profiler.enable()
            self._is_running = True
            ProfilerWrapper._active_profilers.append(self)
        except ValueError as e:
            # Handle case where another profiler is still active
            # Create a new profiler instance
            self._profiler = cProfile.Profile()
            self._profiler.enable()
            self._is_running = True
            ProfilerWrapper._active_profilers.append(self)

    def stop(self):
        """
        Stop profiling and prepare statistics.

        If a profiler was paused for this one, it will be resumed.

        Raises:
            RuntimeError: If profiler is not running
        """
        if not self._is_running:
            raise RuntimeError("Profiler is not running")

        self._profiler.disable()
        self._is_running = False

        # Remove from active stack
        if self in ProfilerWrapper._active_profilers:
            ProfilerWrapper._active_profilers.remove(self)

        # Resume the previously paused profiler if any
        if ProfilerWrapper._active_profilers:
            previous = ProfilerWrapper._active_profilers[-1]
            if previous._was_paused:
                try:
                    previous._profiler.enable()
                    previous._was_paused = False
                except Exception:
                    # If re-enable fails, continue anyway
                    pass

        # Create Stats object for analysis
        self._stats = pstats.Stats(self._profiler)
        self._stats.sort_stats(self.sort_by)

    def __enter__(self):
        """
        Enter context manager - start profiling.

        Returns:
            Self for context manager protocol
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager - stop profiling.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised

        Returns:
            False to propagate exceptions
        """
        self.stop()
        return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get profiling statistics as structured dictionary.

        Returns:
            Dict containing:
                - total_calls: Total number of function calls
                - primitive_calls: Calls that were not induced by recursion
                - total_time: Total time spent in profiled code

        Raises:
            RuntimeError: If profiler hasn't been stopped yet
        """
        if self._stats is None:
            raise RuntimeError("No stats available - call stop() first")

        # Extract statistics from pstats.Stats
        return {
            "total_calls": self._stats.total_calls,
            "primitive_calls": self._stats.prim_calls,
            "total_time": self._stats.total_tt,
        }

    def get_top_functions(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top N functions by the configured sort metric.

        Args:
            n: Number of top functions to return

        Returns:
            List of dicts, each containing:
                - name: Function name with file/line info
                - ncalls: Number of calls
                - tottime: Total time in function (excluding subcalls)
                - cumtime: Cumulative time (including subcalls)
                - percall_tot: tottime / ncalls
                - percall_cum: cumtime / ncalls

        Raises:
            RuntimeError: If profiler hasn't been stopped yet
        """
        if self._stats is None:
            raise RuntimeError("No stats available - call stop() first")

        # Get function stats from pstats
        func_list = []

        for func, (cc, nc, tt, ct, callers) in self._stats.stats.items():
            # Format function name
            filename, line, func_name = func
            name = f"{filename}:{line}({func_name})"

            func_list.append({
                "name": name,
                "ncalls": nc,
                "tottime": tt,
                "cumtime": ct,
                "percall_tot": tt / nc if nc > 0 else 0,
                "percall_cum": ct / nc if nc > 0 else 0,
            })

        # Sort by the configured metric
        if self.sort_by == "cumulative":
            func_list.sort(key=lambda x: x["cumtime"], reverse=True)
        elif self.sort_by == "time":
            func_list.sort(key=lambda x: x["tottime"], reverse=True)
        elif self.sort_by == "calls":
            func_list.sort(key=lambda x: x["ncalls"], reverse=True)

        return func_list[:n]

    def print_stats(self, num_lines: Optional[int] = None):
        """
        Print profiling statistics to stdout.

        Args:
            num_lines: Number of lines to print (None for all)

        Raises:
            RuntimeError: If profiler hasn't been stopped yet
        """
        if self._stats is None:
            raise RuntimeError("No stats available - call stop() first")

        if num_lines is None:
            self._stats.print_stats()
        else:
            self._stats.print_stats(num_lines)

    def save_to_file(self, filepath: str):
        """
        Save profiling data to .prof file for later analysis.

        The saved file can be loaded with pstats.Stats(filepath) or
        analyzed with tools like snakeviz.

        Args:
            filepath: Path where to save the .prof file

        Raises:
            RuntimeError: If profiler hasn't been stopped yet
        """
        if self._stats is None:
            raise RuntimeError("No stats available - call stop() first")

        self._stats.dump_stats(filepath)


def profile_function(sort_by: str = "cumulative") -> Callable[[F], F]:
    """
    Decorator for profiling synchronous functions.

    The function will be profiled each time it's called, with stats
    available but not automatically printed.

    Args:
        sort_by: Sort criterion for profile results

    Returns:
        Decorator function

    Example:
        @profile_function(sort_by="time")
        def my_function(x, y):
            return x + y
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler = ProfilerWrapper(sort_by=sort_by)

            with profiler:
                result = func(*args, **kwargs)

            # Stats are collected but not printed
            # Could add option to print/save in future
            return result

        return wrapper

    return decorator


def profile_async_function(sort_by: str = "cumulative") -> Callable[[F], F]:
    """
    Decorator for profiling async functions.

    The async function will be profiled each time it's awaited, with stats
    available but not automatically printed.

    Args:
        sort_by: Sort criterion for profile results

    Returns:
        Decorator function

    Example:
        @profile_async_function(sort_by="time")
        async def my_async_function(x, y):
            await asyncio.sleep(0.1)
            return x * y
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            profiler = ProfilerWrapper(sort_by=sort_by)

            with profiler:
                result = await func(*args, **kwargs)

            # Stats are collected but not printed
            # Could add option to print/save in future
            return result

        return wrapper

    return decorator
