"""
CBR Case Loading Performance Benchmark

This script measures the performance impact of the modular case structure refactoring
by comparing import time and memory usage between the original case_base.py and the
new modular cases/ structure.

Performance Requirements (from spec):
- Baseline import time: < 200ms
- Time overhead: < 15% vs original
- Memory overhead: < 15% vs original

Usage:
    python benchmark_case_loading.py

The script will measure both modules and report whether requirements are met.
Uses only Python stdlib modules (timeit, tracemalloc, sys) for maximum portability.
"""

import sys
import timeit
import tracemalloc
from pathlib import Path

# Add project root to Python path for imports
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent  # Go up two levels from scripts/utilities/
sys.path.insert(0, str(project_root))


# Configuration: Number of iterations for averaging (10-20 as per spec)
NUM_ITERATIONS = 15

# Performance requirements
MAX_BASELINE_TIME_MS = 200.0
MAX_TIME_OVERHEAD_PERCENT = 15.0
MAX_MEMORY_OVERHEAD_PERCENT = 15.0


def measure_baseline_import_time():
    """
    Measure import time for original case_base.py module.

    Uses timeit.repeat() to run multiple iterations and returns the average
    import time in milliseconds.

    Returns:
        float: Average import time in milliseconds
    """
    # Setup: Clear module from cache before each iteration (including dependencies)
    # Note: We need to pass the project_root as a string literal since __file__ isn't available in timeit context
    setup_code = f"""
import sys
# Add project root to path (literal path from outer scope)
project_root = r'{project_root}'
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# Clear case_base and all cases submodules to ensure fresh import
modules_to_clear = [m for m in list(sys.modules.keys()) if m == 'case_base' or m.startswith('cases')]
for module in modules_to_clear:
    del sys.modules[module]
"""

    # Code to time: Import the module
    import_code = "import case_base"

    try:
        # Run multiple iterations and get times in seconds
        times = timeit.repeat(
            stmt=import_code,
            setup=setup_code,
            repeat=NUM_ITERATIONS,
            number=1
        )

        # Calculate average and convert to milliseconds
        avg_time_seconds = sum(times) / len(times)
        avg_time_ms = avg_time_seconds * 1000.0

        return avg_time_ms

    except ImportError as e:
        print(f"Error importing case_base: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Unexpected error measuring baseline import time: {e}", file=sys.stderr)
        raise


def measure_baseline_memory():
    """
    Measure memory usage for importing case_base.py module.

    Uses tracemalloc to capture peak memory usage during import.

    Returns:
        int: Peak memory usage in bytes
    """
    try:
        # Clear module from cache including any dependencies
        modules_to_clear = [m for m in sys.modules.keys() if m == 'case_base' or m.startswith('cases')]
        for module in modules_to_clear:
            del sys.modules[module]

        # Start memory tracking
        tracemalloc.start()

        # Import the module
        import case_base

        # Get peak memory usage
        current, peak = tracemalloc.get_traced_memory()

        # Stop tracking
        tracemalloc.stop()

        # Return peak memory usage
        return peak

    except ImportError as e:
        tracemalloc.stop()
        print(f"Error importing case_base: {e}", file=sys.stderr)
        raise
    except Exception as e:
        tracemalloc.stop()
        print(f"Unexpected error measuring baseline memory: {e}", file=sys.stderr)
        raise


def measure_new_module_import_time():
    """
    Measure import time for new modular cases/ structure.

    Uses timeit.repeat() to run multiple iterations and returns the average
    import time in milliseconds.

    Returns:
        float: Average import time in milliseconds
    """
    # Setup: Clear module from cache before each iteration
    # Note: We need to pass the project_root as a string literal since __file__ isn't available in timeit context
    setup_code = f"""
import sys
# Add project root to path (literal path from outer scope)
project_root = r'{project_root}'
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# Clear all cases submodules
modules_to_clear = [m for m in sys.modules.keys() if m.startswith('cases')]
for module in modules_to_clear:
    del sys.modules[module]
"""

    # Code to time: Import the module
    import_code = "from cases import ALL_CASES"

    try:
        # Run multiple iterations and get times in seconds
        times = timeit.repeat(
            stmt=import_code,
            setup=setup_code,
            repeat=NUM_ITERATIONS,
            number=1
        )

        # Calculate average and convert to milliseconds
        avg_time_seconds = sum(times) / len(times)
        avg_time_ms = avg_time_seconds * 1000.0

        return avg_time_ms

    except ImportError as e:
        print(f"Error importing cases module: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Unexpected error measuring new module import time: {e}", file=sys.stderr)
        raise


def measure_new_module_memory():
    """
    Measure memory usage for importing cases/ modular structure.

    Uses tracemalloc to capture peak memory usage during import.

    Returns:
        int: Peak memory usage in bytes
    """
    try:
        # Clear modules from cache
        modules_to_clear = [m for m in sys.modules.keys() if m.startswith('cases')]
        for module in modules_to_clear:
            del sys.modules[module]

        # Start memory tracking
        tracemalloc.start()

        # Import the module
        from cases import ALL_CASES

        # Get peak memory usage
        current, peak = tracemalloc.get_traced_memory()

        # Stop tracking
        tracemalloc.stop()

        # Return peak memory usage
        return peak

    except ImportError as e:
        tracemalloc.stop()
        print(f"Error importing cases module: {e}", file=sys.stderr)
        raise
    except Exception as e:
        tracemalloc.stop()
        print(f"Unexpected error measuring new module memory: {e}", file=sys.stderr)
        raise


def calculate_overhead(baseline, new_value):
    """
    Calculate percentage overhead between baseline and new value.

    Formula: ((new - baseline) / baseline) * 100

    Args:
        baseline: Baseline value
        new_value: New value to compare

    Returns:
        float: Overhead percentage (positive = increase, negative = decrease)

    Raises:
        ZeroDivisionError: If baseline is zero
    """
    if baseline == 0:
        raise ZeroDivisionError("Cannot calculate overhead with zero baseline")

    overhead = ((new_value - baseline) / baseline) * 100.0
    return overhead


def validate_requirements(results):
    """
    Validate measured results against performance requirements.

    Requirements:
    - Baseline time < 200ms
    - Time overhead < 15%
    - Memory overhead < 15%

    Args:
        results: Dictionary with keys:
            - baseline_time: float (ms)
            - new_time: float (ms)
            - time_overhead: float (%)
            - baseline_memory: int (bytes)
            - new_memory: int (bytes)
            - memory_overhead: float (%)

    Returns:
        dict: Validation results with keys:
            - baseline_time_pass: bool
            - time_overhead_pass: bool
            - memory_overhead_pass: bool
    """
    validation = {
        'baseline_time_pass': results['baseline_time'] < MAX_BASELINE_TIME_MS,
        'time_overhead_pass': results['time_overhead'] < MAX_TIME_OVERHEAD_PERCENT,
        'memory_overhead_pass': results['memory_overhead'] < MAX_MEMORY_OVERHEAD_PERCENT
    }

    return validation


def format_results(results, validation):
    """
    Format benchmark results as clear, structured output.

    Args:
        results: Dictionary with measurement results
        validation: Dictionary with pass/fail status

    Returns:
        str: Formatted output string
    """
    output = []
    output.append("=" * 60)
    output.append("CBR Case Loading Performance Benchmark")
    output.append("=" * 60)
    output.append("")
    output.append(f"Configuration: {NUM_ITERATIONS} iterations averaged")
    output.append("")

    # Baseline metrics
    baseline_status = "PASS" if validation['baseline_time_pass'] else "FAIL"
    output.append(f"Baseline (case_base.py): Import time: {results['baseline_time']:.1f} ms ({baseline_status}: < {MAX_BASELINE_TIME_MS}ms)")
    output.append(f"  Memory usage: {results['baseline_memory']:,} bytes")
    output.append("")

    # New module metrics
    output.append(f"New Module (cases/): Import time: {results['new_time']:.1f} ms")
    output.append(f"  Memory usage: {results['new_memory']:,} bytes")
    output.append("")

    # Overhead analysis
    time_status = "PASS" if validation['time_overhead_pass'] else "FAIL"
    output.append(f"Performance Overhead: Time overhead: {results['time_overhead']:.1f}% ({time_status}: < {MAX_TIME_OVERHEAD_PERCENT}%)")

    memory_status = "PASS" if validation['memory_overhead_pass'] else "FAIL"
    output.append(f"  Memory overhead: {results['memory_overhead']:.1f}% ({memory_status}: < {MAX_MEMORY_OVERHEAD_PERCENT}%)")
    output.append("")

    # Overall result
    output.append("=" * 60)
    all_pass = all(validation.values())
    if all_pass:
        output.append("ALL REQUIREMENTS MET")
    else:
        output.append("REQUIREMENTS NOT MET")
        output.append("")
        output.append("Failed checks:")
        if not validation['baseline_time_pass']:
            output.append(f"  - Baseline import time: {results['baseline_time']:.1f}ms > {MAX_BASELINE_TIME_MS}ms")
        if not validation['time_overhead_pass']:
            output.append(f"  - Time overhead: {results['time_overhead']:.1f}% > {MAX_TIME_OVERHEAD_PERCENT}%")
        if not validation['memory_overhead_pass']:
            output.append(f"  - Memory overhead: {results['memory_overhead']:.1f}% > {MAX_MEMORY_OVERHEAD_PERCENT}%")
    output.append("=" * 60)

    return "\n".join(output)


def main():
    """
    Main benchmark execution function.

    Orchestrates all measurements, validation, and reporting.

    Returns:
        int: Exit code (0 = success, 1 = failure)
    """
    try:
        print("Starting CBR case loading performance benchmark...")
        print(f"Running {NUM_ITERATIONS} iterations for each measurement...")
        print()

        # Measure baseline (case_base.py)
        print("Measuring baseline (case_base.py) import time...")
        baseline_time = measure_baseline_import_time()

        print("Measuring baseline (case_base.py) memory usage...")
        baseline_memory = measure_baseline_memory()

        # Measure new module (cases/)
        print("Measuring new module (cases/) import time...")
        new_time = measure_new_module_import_time()

        print("Measuring new module (cases/) memory usage...")
        new_memory = measure_new_module_memory()

        print()
        print("Calculating overhead...")

        # Calculate overhead percentages
        time_overhead = calculate_overhead(baseline_time, new_time)
        memory_overhead = calculate_overhead(baseline_memory, new_memory)

        # Package results
        results = {
            'baseline_time': baseline_time,
            'new_time': new_time,
            'time_overhead': time_overhead,
            'baseline_memory': baseline_memory,
            'new_memory': new_memory,
            'memory_overhead': memory_overhead
        }

        # Validate against requirements
        validation = validate_requirements(results)

        # Format and display results
        print()
        output = format_results(results, validation)
        print(output)

        # Return exit code based on validation
        all_pass = all(validation.values())
        return 0 if all_pass else 1

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n\nBenchmark failed with error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
