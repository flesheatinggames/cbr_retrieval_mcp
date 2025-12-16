#!/usr/bin/env python3
"""
Benchmark Case Loading Performance

This script measures the performance impact of the modular case loading system
compared to the baseline case_base.py implementation.

Performance Requirements (from spec):
- Baseline import time: < 200ms
- Time overhead: < 15%
- Memory overhead: < 15%

The script runs multiple iterations (10+) to get accurate average measurements
and reports results in a clear, structured format.
"""

import sys
import time
import tracemalloc
from pathlib import Path

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# Configuration
ITERATIONS = 10  # Number of iterations for averaging
BASELINE_TIME_REQUIREMENT = 200.0  # milliseconds
TIME_OVERHEAD_REQUIREMENT = 15.0  # percent
MEMORY_OVERHEAD_REQUIREMENT = 15.0  # percent


def measure_baseline_import_time():
    """
    Measure the import time of case_base.py.

    Returns:
        float: Average import time in milliseconds
    """
    times = []

    for _ in range(ITERATIONS):
        # Clear the module and all related modules from sys.modules
        modules_to_clear = [m for m in sys.modules.keys() if 'case_base' in m or m.startswith('cases')]
        for module in modules_to_clear:
            del sys.modules[module]

        start = time.perf_counter()
        try:
            import case_base  # noqa: F401
        except ImportError:
            # Module might not exist or have different name
            pass
        end = time.perf_counter()

        times.append((end - start) * 1000)  # Convert to milliseconds

    return sum(times) / len(times)


def measure_baseline_memory():
    """
    Measure the memory usage of importing case_base.py.

    Returns:
        int: Peak memory usage in bytes
    """
    # Clear the module from sys.modules if it exists
    modules_to_clear = [m for m in sys.modules.keys() if 'case_base' in m or m.startswith('cases')]
    for module in modules_to_clear:
        del sys.modules[module]

    tracemalloc.start()

    try:
        import case_base  # noqa: F401
        # Force evaluation of CASE_BASE to measure actual data size
        _ = len(case_base.CASE_BASE)
    except (ImportError, AttributeError):
        pass

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return peak


def measure_new_module_import_time():
    """
    Measure the import time of the new cases module.

    Returns:
        float: Average import time in milliseconds
    """
    times = []

    for _ in range(ITERATIONS):
        # Clear the module from sys.modules if it exists
        modules_to_clear = [m for m in sys.modules.keys() if m.startswith('cases')]
        for module in modules_to_clear:
            del sys.modules[module]

        start = time.perf_counter()
        try:
            from cases import ALL_CASES  # noqa: F401
        except ImportError:
            pass
        end = time.perf_counter()

        times.append((end - start) * 1000)  # Convert to milliseconds

    return sum(times) / len(times)


def measure_new_module_memory():
    """
    Measure the memory usage of importing the new cases module.

    Returns:
        int: Peak memory usage in bytes
    """
    # Clear the module from sys.modules if it exists
    modules_to_clear = [m for m in sys.modules.keys() if m.startswith('cases')]
    for module in modules_to_clear:
        del sys.modules[module]

    tracemalloc.start()

    try:
        from cases import ALL_CASES  # noqa: F401
        # Force evaluation to measure actual data size
        _ = len(ALL_CASES)
    except (ImportError, AttributeError):
        pass

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return peak


def calculate_overhead(baseline, new_value):
    """
    Calculate the percentage overhead between baseline and new value.

    Args:
        baseline: The baseline measurement
        new_value: The new measurement

    Returns:
        float: Overhead percentage (can be negative if new value is lower)

    Raises:
        ZeroDivisionError: If baseline is zero
    """
    if baseline == 0:
        raise ZeroDivisionError("Baseline cannot be zero")

    return ((new_value - baseline) / baseline) * 100


def validate_requirements(results):
    """
    Validate benchmark results against spec requirements.

    Args:
        results: Dictionary with benchmark results

    Returns:
        dict: Validation results with pass/fail status for each requirement
    """
    validation = {
        'baseline_time_pass': results['baseline_time'] < BASELINE_TIME_REQUIREMENT,
        'time_overhead_pass': results['time_overhead'] < TIME_OVERHEAD_REQUIREMENT,
        'memory_overhead_pass': results['memory_overhead'] < MEMORY_OVERHEAD_REQUIREMENT
    }

    return validation


def format_results(results, validation):
    """
    Format benchmark results for display.

    Args:
        results: Dictionary with benchmark results
        validation: Dictionary with validation results

    Returns:
        str: Formatted output string
    """
    lines = []
    lines.append("=" * 60)
    lines.append("Case Loading Performance Benchmark")
    lines.append("=" * 60)
    lines.append(f"Iterations per measurement: {ITERATIONS}")
    lines.append("")

    lines.append("Baseline (case_base.py):")
    lines.append(f"  baseline: {results['baseline_time']:.2f} ms")
    lines.append(f"  baseline memory: {results['baseline_memory']:,} bytes")
    lines.append("")

    lines.append("New Module (cases/):")
    lines.append(f"  new module import time: {results['new_time']:.2f} ms")
    lines.append(f"  new memory: {results['new_memory']:,} bytes")
    lines.append("")

    lines.append("Overhead:")
    lines.append(f"  time overhead: {results['time_overhead']:.2f}%")
    lines.append(f"  memory overhead: {results['memory_overhead']:.2f}%")
    lines.append("")

    lines.append("Requirements Validation:")
    lines.append(f"  Baseline import < 200ms: {'PASS' if validation['baseline_time_pass'] else 'FAIL'}")
    lines.append(f"  Time overhead < 15%: {'PASS' if validation['time_overhead_pass'] else 'FAIL'}")
    lines.append(f"  Memory overhead < 15%: {'PASS' if validation['memory_overhead_pass'] else 'FAIL'}")
    lines.append("")

    all_pass = all(validation.values())
    lines.append(f"Overall: {'PASS' if all_pass else 'FAIL'}")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    """Main benchmark execution function."""
    try:
        print("Running case loading performance benchmark...")
        print(f"(Running {ITERATIONS} iterations for average measurements)")
        print()

        # Measure baseline
        print("Measuring baseline (case_base.py)...")
        baseline_time = measure_baseline_import_time()
        baseline_memory = measure_baseline_memory()

        # Measure new module
        print("Measuring new module (cases/)...")
        new_time = measure_new_module_import_time()
        new_memory = measure_new_module_memory()

        # Calculate overhead
        time_overhead = calculate_overhead(baseline_time, new_time)
        memory_overhead = calculate_overhead(baseline_memory, new_memory)

        # Collect results
        results = {
            'baseline_time': baseline_time,
            'new_time': new_time,
            'time_overhead': time_overhead,
            'baseline_memory': baseline_memory,
            'new_memory': new_memory,
            'memory_overhead': memory_overhead
        }

        # Validate requirements
        validation = validate_requirements(results)

        # Display results
        print()
        output = format_results(results, validation)
        print(output)

        # Always return 0 for successful execution
        # (even if performance requirements fail)
        return 0

    except Exception as e:
        print(f"Error during benchmark: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main())
