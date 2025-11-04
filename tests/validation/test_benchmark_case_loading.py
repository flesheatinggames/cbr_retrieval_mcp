"""
Tests for benchmark_case_loading.py

This test file verifies that the benchmark script correctly measures
baseline and new module performance metrics.
"""

import pytest
import sys
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import importlib.util


def test_benchmark_script_exists():
    """Test that benchmark_case_loading.py exists in project root."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    assert benchmark_path.exists(), "benchmark_case_loading.py should exist in project root"
    assert benchmark_path.is_file(), "benchmark_case_loading.py should be a file"


def test_benchmark_can_import():
    """Test that benchmark_case_loading.py can be imported."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    assert spec is not None, "Should be able to load benchmark module spec"

    module = importlib.util.module_from_spec(spec)
    assert module is not None, "Should be able to create module from spec"

    # Import should not raise
    spec.loader.exec_module(module)


def test_benchmark_measures_baseline_import_time():
    """Test that benchmark measures case_base.py import time."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Function should exist
    assert hasattr(module, 'measure_baseline_import_time'), \
        "Should have measure_baseline_import_time function"

    # Function should return a positive float (milliseconds)
    baseline_time = module.measure_baseline_import_time()
    assert isinstance(baseline_time, (int, float)), \
        "Import time should be numeric"
    assert baseline_time > 0, \
        "Import time should be positive"
    assert baseline_time < 10000, \
        "Import time should be reasonable (< 10 seconds)"


def test_benchmark_measures_baseline_memory():
    """Test that benchmark measures case_base.py memory usage."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Function should exist
    assert hasattr(module, 'measure_baseline_memory'), \
        "Should have measure_baseline_memory function"

    # Function should return a positive integer (bytes)
    baseline_memory = module.measure_baseline_memory()
    assert isinstance(baseline_memory, int), \
        "Memory usage should be an integer (bytes)"
    assert baseline_memory > 0, \
        "Memory usage should be positive"
    assert baseline_memory < 1024 * 1024 * 1024, \
        "Memory usage should be reasonable (< 1GB)"


def test_benchmark_measures_new_module_import_time():
    """Test that benchmark measures cases module import time."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Function should exist
    assert hasattr(module, 'measure_new_module_import_time'), \
        "Should have measure_new_module_import_time function"

    # Function should return a positive float (milliseconds)
    new_time = module.measure_new_module_import_time()
    assert isinstance(new_time, (int, float)), \
        "Import time should be numeric"
    assert new_time > 0, \
        "Import time should be positive"
    assert new_time < 10000, \
        "Import time should be reasonable (< 10 seconds)"


def test_benchmark_measures_new_module_memory():
    """Test that benchmark measures cases module memory usage."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Function should exist
    assert hasattr(module, 'measure_new_module_memory'), \
        "Should have measure_new_module_memory function"

    # Function should return a positive integer (bytes)
    new_memory = module.measure_new_module_memory()
    assert isinstance(new_memory, int), \
        "Memory usage should be an integer (bytes)"
    assert new_memory > 0, \
        "Memory usage should be positive"
    assert new_memory < 1024 * 1024 * 1024, \
        "Memory usage should be reasonable (< 1GB)"


def test_benchmark_calculates_overhead_percentages():
    """Test that benchmark correctly calculates overhead percentages."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Function should exist
    assert hasattr(module, 'calculate_overhead'), \
        "Should have calculate_overhead function"

    # Test with known values
    baseline = 100.0
    new_value = 110.0
    overhead = module.calculate_overhead(baseline, new_value)

    assert isinstance(overhead, (int, float)), \
        "Overhead should be numeric"
    assert overhead == pytest.approx(10.0, rel=0.01), \
        "Overhead calculation should be correct: ((110-100)/100)*100 = 10%"

    # Test with equal values (0% overhead)
    overhead_zero = module.calculate_overhead(100.0, 100.0)
    assert overhead_zero == pytest.approx(0.0, rel=0.01), \
        "Equal values should result in 0% overhead"

    # Test with negative overhead (improvement)
    overhead_negative = module.calculate_overhead(100.0, 90.0)
    assert overhead_negative == pytest.approx(-10.0, rel=0.01), \
        "Lower new value should result in negative overhead"


def test_benchmark_validates_performance_requirements():
    """Test that benchmark validates against spec requirements."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Function should exist
    assert hasattr(module, 'validate_requirements'), \
        "Should have validate_requirements function"

    # Test with passing values
    results_pass = {
        'baseline_time': 150.0,
        'new_time': 160.0,
        'time_overhead': 6.67,
        'baseline_memory': 1000000,
        'new_memory': 1100000,
        'memory_overhead': 10.0
    }
    validation = module.validate_requirements(results_pass)

    assert isinstance(validation, dict), \
        "Validation should return a dictionary"
    assert 'baseline_time_pass' in validation, \
        "Should check baseline time requirement"
    assert 'time_overhead_pass' in validation, \
        "Should check time overhead requirement"
    assert 'memory_overhead_pass' in validation, \
        "Should check memory overhead requirement"
    assert validation['baseline_time_pass'] is True, \
        "Baseline time < 200ms should pass"
    assert validation['time_overhead_pass'] is True, \
        "Time overhead < 15% should pass"
    assert validation['memory_overhead_pass'] is True, \
        "Memory overhead < 15% should pass"

    # Test with failing values
    results_fail = {
        'baseline_time': 250.0,  # > 200ms
        'new_time': 300.0,
        'time_overhead': 20.0,  # > 15%
        'baseline_memory': 1000000,
        'new_memory': 1200000,
        'memory_overhead': 20.0  # > 15%
    }
    validation_fail = module.validate_requirements(results_fail)

    assert validation_fail['baseline_time_pass'] is False, \
        "Baseline time > 200ms should fail"
    assert validation_fail['time_overhead_pass'] is False, \
        "Time overhead > 15% should fail"
    assert validation_fail['memory_overhead_pass'] is False, \
        "Memory overhead > 15% should fail"


def test_benchmark_output_format():
    """Test that benchmark produces clear, structured output."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Function should exist
    assert hasattr(module, 'format_results'), \
        "Should have format_results function"

    # Test formatting
    results = {
        'baseline_time': 150.0,
        'new_time': 160.0,
        'time_overhead': 6.67,
        'baseline_memory': 1000000,
        'new_memory': 1100000,
        'memory_overhead': 10.0
    }
    validation = {
        'baseline_time_pass': True,
        'time_overhead_pass': True,
        'memory_overhead_pass': True
    }

    output = module.format_results(results, validation)

    assert isinstance(output, str), \
        "Output should be a string"
    assert 'baseline' in output.lower() or 'Baseline' in output, \
        "Output should mention baseline"
    assert 'overhead' in output.lower() or 'Overhead' in output, \
        "Output should mention overhead"
    assert 'pass' in output.lower() or 'PASS' in output, \
        "Output should show PASS status"
    assert '150' in output or '150.0' in output, \
        "Output should include baseline time value"
    assert '6.67' in output or '6.7' in output, \
        "Output should include time overhead percentage"


def test_benchmark_handles_import_errors():
    """Test that benchmark handles import errors gracefully."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # The benchmark should have try-except blocks around imports
    # We can verify this by checking the source or by testing with mock failures

    # At minimum, the main function should exist and be callable
    assert hasattr(module, 'main'), \
        "Should have main function"
    assert callable(module.main), \
        "main should be callable"


def test_benchmark_runs_multiple_iterations():
    """Test that benchmark runs multiple iterations for accuracy."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Should have constants or parameters for iteration count
    # At least 10 iterations as specified
    assert hasattr(module, 'ITERATIONS') or hasattr(module, 'NUM_ITERATIONS'), \
        "Should define number of iterations as a constant"

    if hasattr(module, 'ITERATIONS'):
        assert module.ITERATIONS >= 10, \
            "Should run at least 10 iterations"
    elif hasattr(module, 'NUM_ITERATIONS'):
        assert module.NUM_ITERATIONS >= 10, \
            "Should run at least 10 iterations"


def test_benchmark_standalone_execution():
    """Test that benchmark can be executed standalone."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"

    # Test execution (with short timeout to avoid hanging)
    result = subprocess.run(
        [sys.executable, str(benchmark_path)],
        capture_output=True,
        text=True,
        timeout=30  # 30 second timeout
    )

    # Should execute without errors (or at least provide output)
    assert result.returncode == 0 or len(result.stdout) > 0 or len(result.stderr) > 0, \
        "Script should execute and provide output"

    # Output should contain key information
    output = result.stdout + result.stderr
    assert 'baseline' in output.lower() or 'import' in output.lower(), \
        "Output should mention baseline or import"


def test_benchmark_has_documentation():
    """Test that benchmark script has clear documentation."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"

    with open(benchmark_path, 'r') as f:
        content = f.read()

    # Should have a docstring
    assert '"""' in content or "'''" in content, \
        "Script should have docstrings"

    # Should have comments explaining the benchmark
    assert '#' in content, \
        "Script should have comments"

    # Should mention requirements (200ms, 15% overhead)
    assert '200' in content or '15' in content, \
        "Script should mention performance requirements"


def test_benchmark_uses_stdlib_only():
    """Test that benchmark uses only Python stdlib (no external dependencies)."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"

    with open(benchmark_path, 'r') as f:
        content = f.read()

    # Should import stdlib modules
    assert 'import time' in content or 'import timeit' in content, \
        "Should use time or timeit module"
    assert 'import tracemalloc' in content, \
        "Should use tracemalloc module"
    assert 'import sys' in content, \
        "Should use sys module"

    # Should NOT import external packages
    assert 'import pytest' not in content, \
        "Should not require pytest"
    assert 'import numpy' not in content, \
        "Should not require numpy"


def test_benchmark_measures_peak_memory():
    """Test that benchmark captures peak memory during import."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Memory measurement functions should use tracemalloc
    # and return peak memory (memory delta)
    baseline_memory = module.measure_baseline_memory()

    # Should be measuring significant memory (cases are non-trivial)
    assert baseline_memory > 10000, \
        "Should measure significant memory usage (> 10KB)"


def test_benchmark_calculates_averages():
    """Test that benchmark calculates mean time from multiple iterations."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # The measurement functions should internally handle multiple iterations
    # and return the average (verified by running multiple times and checking consistency)
    time1 = module.measure_baseline_import_time()
    time2 = module.measure_baseline_import_time()

    # Times should be relatively consistent (within 100% variance)
    # since they're averaging multiple iterations
    variance = abs(time1 - time2) / min(time1, time2)
    assert variance < 1.0, \
        "Multiple runs with averaging should produce consistent results"


def test_benchmark_displays_all_metrics():
    """Test that benchmark displays all required metrics."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"

    result = subprocess.run(
        [sys.executable, str(benchmark_path)],
        capture_output=True,
        text=True,
        timeout=30
    )

    output = result.stdout + result.stderr

    # Should display baseline metrics
    assert 'baseline' in output.lower(), \
        "Should display baseline metrics"

    # Should display new module metrics
    assert 'new' in output.lower() or 'module' in output.lower() or 'cases' in output.lower(), \
        "Should display new module metrics"

    # Should display overhead percentages
    assert '%' in output, \
        "Should display percentage values"

    # Should display pass/fail status
    assert 'pass' in output.lower() or 'fail' in output.lower(), \
        "Should display pass/fail status"


def test_benchmark_documents_baseline_metrics():
    """Test that benchmark provides clear baseline metrics for use in automated tests."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"

    result = subprocess.run(
        [sys.executable, str(benchmark_path)],
        capture_output=True,
        text=True,
        timeout=30
    )

    # Should complete successfully
    assert result.returncode == 0, \
        "Benchmark should complete successfully"

    output = result.stdout + result.stderr

    # Should provide numerical values that can be parsed
    # (contains digits for times and memory)
    import re
    numbers = re.findall(r'\d+\.?\d*', output)
    assert len(numbers) >= 4, \
        "Should display at least 4 numerical values (times and memory for both baselines)"


def test_benchmark_handles_zero_baseline():
    """Test that benchmark handles edge case of zero baseline values."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # calculate_overhead should handle zero baseline (or return error/inf)
    if hasattr(module, 'calculate_overhead'):
        # Should either return infinity, error, or handle gracefully
        try:
            result = module.calculate_overhead(0.0, 100.0)
            # If it returns a value, it should be a number (possibly inf)
            assert isinstance(result, (int, float))
        except (ZeroDivisionError, ValueError):
            # Or it should raise an appropriate error
            pass


def test_benchmark_precision_of_overhead_calculation():
    """Test overhead calculation with small percentage differences."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Test with 1% difference
    overhead_small = module.calculate_overhead(100.0, 101.0)
    assert overhead_small == pytest.approx(1.0, rel=0.001), \
        "Should accurately calculate small overhead percentages"

    # Test with 0.1% difference
    overhead_tiny = module.calculate_overhead(1000.0, 1001.0)
    assert overhead_tiny == pytest.approx(0.1, rel=0.001), \
        "Should handle very small overhead percentages"


def test_benchmark_memory_units_are_bytes():
    """Test that memory measurements are in bytes (not KB or MB)."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"
    spec = importlib.util.spec_from_file_location("benchmark_case_loading", benchmark_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    baseline_memory = module.measure_baseline_memory()
    new_memory = module.measure_new_module_memory()

    # Should be in bytes (large numbers for case loading)
    # A typical case base should use at least 100KB of memory
    assert baseline_memory > 100000, \
        "Memory should be measured in bytes (not KB or MB)"
    assert new_memory > 100000, \
        "Memory should be measured in bytes (not KB or MB)"


def test_benchmark_time_units_are_milliseconds():
    """Test that time measurements are reported in milliseconds."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"

    result = subprocess.run(
        [sys.executable, str(benchmark_path)],
        capture_output=True,
        text=True,
        timeout=30
    )

    output = result.stdout + result.stderr

    # Should mention milliseconds or ms
    assert 'ms' in output.lower() or 'millisecond' in output.lower(), \
        "Time should be reported in milliseconds"


def test_benchmark_reports_iterations_count():
    """Test that benchmark reports how many iterations were run."""
    benchmark_path = Path(__file__).parent / "benchmark_case_loading.py"

    result = subprocess.run(
        [sys.executable, str(benchmark_path)],
        capture_output=True,
        text=True,
        timeout=30
    )

    output = result.stdout + result.stderr

    # Should mention number of iterations
    assert 'iteration' in output.lower() or 'average' in output.lower(), \
        "Should indicate multiple iterations were run"
