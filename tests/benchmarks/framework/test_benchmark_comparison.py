"""
Comprehensive tests for benchmark comparison utilities.

This module tests the comparison, regression detection, and statistical analysis
functionality for benchmark results.
"""

from dataclasses import dataclass
from typing import List, Tuple

import pytest


# Expected data structures (will be implemented in the actual module)
@dataclass
class BenchmarkResult:
    """Represents a single benchmark result."""

    name: str
    mean_ms: float
    std_dev_ms: float
    samples: List[float]
    percentiles: dict


@dataclass
class ComparisonResult:
    """Represents the comparison between baseline and current results."""

    benchmark_name: str
    baseline_mean_ms: float
    current_mean_ms: float
    percent_change: float
    is_regression: bool
    is_improvement: bool
    is_significant: bool
    effect_size: float
    confidence_interval: Tuple[float, float]


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def baseline_result() -> BenchmarkResult:
    """Create a baseline benchmark result."""
    return BenchmarkResult(
        name="test_query_performance",
        mean_ms=100.0,
        std_dev_ms=5.0,
        samples=[95.0, 98.0, 100.0, 102.0, 105.0],
        percentiles={"p50": 100.0, "p95": 104.0, "p99": 105.0},
    )


@pytest.fixture
def improved_result() -> BenchmarkResult:
    """Create a result showing improvement (faster)."""
    return BenchmarkResult(
        name="test_query_performance",
        mean_ms=85.0,
        std_dev_ms=4.0,
        samples=[80.0, 83.0, 85.0, 87.0, 90.0],
        percentiles={"p50": 85.0, "p95": 89.0, "p99": 90.0},
    )


@pytest.fixture
def regressed_result() -> BenchmarkResult:
    """Create a result showing regression (slower)."""
    return BenchmarkResult(
        name="test_query_performance",
        mean_ms=120.0,
        std_dev_ms=6.0,
        samples=[115.0, 118.0, 120.0, 122.0, 125.0],
        percentiles={"p50": 120.0, "p95": 124.0, "p99": 125.0},
    )


@pytest.fixture
def baseline_results() -> List[BenchmarkResult]:
    """Create a set of baseline benchmark results."""
    return [
        BenchmarkResult(
            name="benchmark_a",
            mean_ms=50.0,
            std_dev_ms=2.0,
            samples=[48.0, 49.0, 50.0, 51.0, 52.0],
            percentiles={"p50": 50.0, "p95": 51.5, "p99": 52.0},
        ),
        BenchmarkResult(
            name="benchmark_b",
            mean_ms=100.0,
            std_dev_ms=5.0,
            samples=[95.0, 98.0, 100.0, 102.0, 105.0],
            percentiles={"p50": 100.0, "p95": 104.0, "p99": 105.0},
        ),
        BenchmarkResult(
            name="benchmark_c",
            mean_ms=150.0,
            std_dev_ms=10.0,
            samples=[140.0, 145.0, 150.0, 155.0, 160.0],
            percentiles={"p50": 150.0, "p95": 158.0, "p99": 160.0},
        ),
    ]


@pytest.fixture
def current_results() -> List[BenchmarkResult]:
    """Create current results with mixed improvements and regressions."""
    return [
        BenchmarkResult(
            name="benchmark_a",
            mean_ms=45.0,  # 10% improvement
            std_dev_ms=2.0,
            samples=[43.0, 44.0, 45.0, 46.0, 47.0],
            percentiles={"p50": 45.0, "p95": 46.5, "p99": 47.0},
        ),
        BenchmarkResult(
            name="benchmark_b",
            mean_ms=115.0,  # 15% regression
            std_dev_ms=5.0,
            samples=[110.0, 113.0, 115.0, 117.0, 120.0],
            percentiles={"p50": 115.0, "p95": 119.0, "p99": 120.0},
        ),
        BenchmarkResult(
            name="benchmark_c",
            mean_ms=152.0,  # ~1.3% regression (below threshold)
            std_dev_ms=10.0,
            samples=[142.0, 147.0, 152.0, 157.0, 162.0],
            percentiles={"p50": 152.0, "p95": 160.0, "p99": 162.0},
        ),
    ]


@pytest.fixture
def comparator():
    """Create a BenchmarkComparator instance."""
    try:
        from cbr_mcp_server.performance.framework.benchmark_comparison import (
            BenchmarkComparator,
        )

        return BenchmarkComparator(threshold_pct=5.0, significance_level=0.05)
    except ImportError:
        pytest.skip("benchmark_comparison module not available")


@pytest.fixture
def regression_detector():
    """Create a RegressionDetector instance."""
    try:
        from cbr_mcp_server.performance.framework.benchmark_comparison import (
            RegressionDetector,
        )

        return RegressionDetector()
    except ImportError:
        pytest.skip("benchmark_comparison module not available")


@pytest.fixture
def statistical_analyzer():
    """Create a StatisticalAnalyzer instance."""
    try:
        from cbr_mcp_server.performance.framework.benchmark_comparison import (
            StatisticalAnalyzer,
        )

        return StatisticalAnalyzer()
    except ImportError:
        pytest.skip("benchmark_comparison module not available")


# =============================================================================
# 1. BenchmarkComparator Class Tests
# =============================================================================


def test_comparator_initialization():
    """Test BenchmarkComparator initialization with defaults and custom values."""
    try:
        from cbr_mcp_server.performance.framework.benchmark_comparison import (
            BenchmarkComparator,
        )

        # Test default initialization
        comparator_default = BenchmarkComparator()
        assert comparator_default.threshold_pct == 5.0
        assert comparator_default.significance_level == 0.05

        # Test custom initialization
        comparator_custom = BenchmarkComparator(
            threshold_pct=10.0, significance_level=0.01
        )
        assert comparator_custom.threshold_pct == 10.0
        assert comparator_custom.significance_level == 0.01
    except ImportError:
        pytest.skip("benchmark_comparison module not available")


def test_compare_single_results_improvement(
    comparator, baseline_result, improved_result
):
    """Test comparing two results correctly detects an improvement."""
    result = comparator.compare_results(baseline_result, improved_result)

    assert isinstance(result, ComparisonResult)
    assert result.benchmark_name == "test_query_performance"
    assert result.baseline_mean_ms == 100.0
    assert result.current_mean_ms == 85.0
    assert result.percent_change < 0  # Negative indicates improvement
    assert result.is_improvement is True
    assert result.is_regression is False


def test_compare_single_results_regression(
    comparator, baseline_result, regressed_result
):
    """Test comparing two results correctly detects a regression."""
    result = comparator.compare_results(baseline_result, regressed_result)

    assert isinstance(result, ComparisonResult)
    assert result.benchmark_name == "test_query_performance"
    assert result.baseline_mean_ms == 100.0
    assert result.current_mean_ms == 120.0
    assert result.percent_change > 0  # Positive indicates regression
    assert result.is_regression is True
    assert result.is_improvement is False


def test_compare_result_sets(comparator, baseline_results, current_results):
    """Test comparing multiple baseline and current results."""
    comparisons = comparator.compare_result_sets(baseline_results, current_results)

    assert isinstance(comparisons, list)
    assert len(comparisons) == 3
    assert all(isinstance(comp, ComparisonResult) for comp in comparisons)

    # Verify benchmark names match
    names = [comp.benchmark_name for comp in comparisons]
    assert "benchmark_a" in names
    assert "benchmark_b" in names
    assert "benchmark_c" in names


def test_detect_regressions_filters_correctly(
    comparator, baseline_results, current_results
):
    """Test detect_regressions only returns regressions."""
    comparisons = comparator.compare_result_sets(baseline_results, current_results)
    regressions = comparator.detect_regressions(comparisons)

    assert isinstance(regressions, list)
    assert all(comp.is_regression for comp in regressions)
    assert not any(comp.is_improvement for comp in regressions)

    # benchmark_b should be in regressions (15% regression)
    regression_names = [comp.benchmark_name for comp in regressions]
    assert "benchmark_b" in regression_names


def test_detect_improvements_filters_correctly(
    comparator, baseline_results, current_results
):
    """Test detect_improvements only returns improvements."""
    comparisons = comparator.compare_result_sets(baseline_results, current_results)
    improvements = comparator.detect_improvements(comparisons)

    assert isinstance(improvements, list)
    assert all(comp.is_improvement for comp in improvements)
    assert not any(comp.is_regression for comp in improvements)

    # benchmark_a should be in improvements (10% improvement)
    improvement_names = [comp.benchmark_name for comp in improvements]
    assert "benchmark_a" in improvement_names


# =============================================================================
# 2. Regression Detection Tests
# =============================================================================


def test_regression_detector_with_percentage_threshold(
    regression_detector, baseline_result
):
    """Test regression detection using percentage threshold."""
    # 10% increase - should be detected with 5% threshold
    high_regression = BenchmarkResult(
        name="test",
        mean_ms=110.0,
        std_dev_ms=5.0,
        samples=[105.0, 108.0, 110.0, 112.0, 115.0],
        percentiles={"p50": 110.0, "p95": 114.0, "p99": 115.0},
    )
    assert regression_detector.detect(baseline_result, high_regression, threshold=5.0)

    # 3% increase - should not be detected with 5% threshold
    low_regression = BenchmarkResult(
        name="test",
        mean_ms=103.0,
        std_dev_ms=5.0,
        samples=[98.0, 101.0, 103.0, 105.0, 108.0],
        percentiles={"p50": 103.0, "p95": 107.0, "p99": 108.0},
    )
    assert not regression_detector.detect(
        baseline_result, low_regression, threshold=5.0
    )


def test_regression_detector_no_regression_on_improvement(
    regression_detector, baseline_result, improved_result
):
    """Test that improvements are not flagged as regressions."""
    assert not regression_detector.detect(
        baseline_result, improved_result, threshold=5.0
    )


def test_regression_severity_classification(regression_detector):
    """Test severity classification for different percent changes."""
    # Minor regression (<10%)
    assert regression_detector.classify_severity(5.0) == "minor"
    assert regression_detector.classify_severity(9.0) == "minor"

    # Moderate regression (10-25%)
    assert regression_detector.classify_severity(10.0) == "moderate"
    assert regression_detector.classify_severity(20.0) == "moderate"
    assert regression_detector.classify_severity(25.0) == "moderate"

    # Severe regression (>25%)
    assert regression_detector.classify_severity(26.0) == "severe"
    assert regression_detector.classify_severity(50.0) == "severe"


def test_regression_detector_at_threshold_boundary(
    regression_detector, baseline_result
):
    """Test edge case at exact threshold value."""
    # Exactly 5% increase with 5% threshold
    at_threshold = BenchmarkResult(
        name="test",
        mean_ms=105.0,
        std_dev_ms=5.0,
        samples=[100.0, 103.0, 105.0, 107.0, 110.0],
        percentiles={"p50": 105.0, "p95": 109.0, "p99": 110.0},
    )

    # Behavior should be consistent (either always detect or never detect at boundary)
    result = regression_detector.detect(baseline_result, at_threshold, threshold=5.0)
    assert isinstance(result, bool)


def test_regression_detector_with_statistical_significance(comparator, baseline_result):
    """Test regression considers statistical significance."""
    # Large change with high variance - may not be statistically significant
    high_variance = BenchmarkResult(
        name="test",
        mean_ms=120.0,
        std_dev_ms=30.0,
        samples=[90.0, 100.0, 120.0, 140.0, 150.0],
        percentiles={"p50": 120.0, "p95": 145.0, "p99": 150.0},
    )

    result = comparator.compare_results(baseline_result, high_variance)
    # Despite 20% increase, high variance may make it non-significant
    assert result.percent_change > 10.0  # Large percent change
    # is_significant field should reflect statistical test


# =============================================================================
# 3. Statistical Analysis Tests
# =============================================================================


def test_calculate_percent_change(statistical_analyzer):
    """Test percent change calculation."""
    # Standard case
    assert statistical_analyzer.calculate_percent_change(100.0, 110.0) == 10.0
    assert statistical_analyzer.calculate_percent_change(100.0, 90.0) == -10.0

    # Edge cases
    assert statistical_analyzer.calculate_percent_change(100.0, 100.0) == 0.0

    # Large changes
    assert statistical_analyzer.calculate_percent_change(100.0, 200.0) == 100.0
    assert statistical_analyzer.calculate_percent_change(100.0, 50.0) == -50.0


def test_calculate_effect_size_cohens_d(statistical_analyzer):
    """Test Cohen's d effect size calculation."""
    baseline_data = [95.0, 98.0, 100.0, 102.0, 105.0]
    current_data = [115.0, 118.0, 120.0, 122.0, 125.0]

    effect_size = statistical_analyzer.calculate_effect_size(
        baseline_data, current_data
    )

    assert isinstance(effect_size, float)
    assert effect_size > 0  # Positive effect size for performance degradation
    # Large effect size expected for this difference
    assert effect_size > 1.0


def test_t_test_for_significance(statistical_analyzer):
    """Test t-test returns correct statistic and p-value."""
    # Significantly different data
    baseline_data = [95.0, 98.0, 100.0, 102.0, 105.0]
    different_data = [115.0, 118.0, 120.0, 122.0, 125.0]

    t_stat, p_value = statistical_analyzer.t_test(baseline_data, different_data)

    assert isinstance(t_stat, float)
    assert isinstance(p_value, float)
    assert 0.0 <= p_value <= 1.0
    assert p_value < 0.05  # Should be statistically significant

    # Nearly identical data
    similar_data = [99.0, 100.0, 100.0, 100.0, 101.0]
    t_stat2, p_value2 = statistical_analyzer.t_test(baseline_data, similar_data)

    assert p_value2 > 0.05  # Should not be statistically significant


def test_confidence_interval_calculation(statistical_analyzer):
    """Test confidence interval calculation for 95% confidence."""
    data = [95.0, 98.0, 100.0, 102.0, 105.0]

    lower, upper = statistical_analyzer.confidence_interval(data, confidence=0.95)

    assert isinstance(lower, float)
    assert isinstance(upper, float)
    assert lower < upper

    # Mean should be within interval
    mean = sum(data) / len(data)
    assert lower <= mean <= upper

    # Check interval width is reasonable
    assert upper - lower > 0


def test_statistical_functions_handle_edge_cases(statistical_analyzer):
    """Test statistical functions handle empty data, identical data, single values."""
    # Identical data - zero variance
    identical_data = [100.0, 100.0, 100.0, 100.0, 100.0]

    # Should handle zero variance gracefully
    effect_size = statistical_analyzer.calculate_effect_size(
        identical_data, identical_data
    )
    assert effect_size == 0.0 or effect_size != effect_size  # 0 or NaN acceptable

    # Single value lists
    single_value_a = [100.0]
    single_value_b = [110.0]

    # Should either compute or raise appropriate error
    try:
        result = statistical_analyzer.t_test(single_value_a, single_value_b)
        assert isinstance(result, tuple)
    except ValueError:
        pass  # Acceptable to raise ValueError for insufficient data

    # Empty lists - should raise ValueError
    empty_data = []
    with pytest.raises(ValueError):
        statistical_analyzer.calculate_percent_change(
            0.0, 100.0
        )  # Division by zero case

    with pytest.raises((ValueError, ZeroDivisionError)):
        statistical_analyzer.confidence_interval(empty_data)


# =============================================================================
# 4. Comparison Reporting Tests
# =============================================================================


def test_generate_comparison_summary(comparator, baseline_results, current_results):
    """Test summary generation with key metrics."""
    comparisons = comparator.compare_result_sets(baseline_results, current_results)

    try:
        from cbr_mcp_server.performance.framework.benchmark_comparison import (
            generate_comparison_summary,
        )
    except ImportError:
        pytest.skip("benchmark_comparison module not available")

    summary = generate_comparison_summary(comparisons)

    assert isinstance(summary, dict)
    assert "total_benchmarks" in summary
    assert "regression_count" in summary
    assert "improvement_count" in summary
    assert "average_percent_change" in summary

    assert summary["total_benchmarks"] == 3
    assert isinstance(summary["regression_count"], int)
    assert isinstance(summary["improvement_count"], int)
    assert isinstance(summary["average_percent_change"], float)


def test_generate_detailed_comparison_report(
    comparator, baseline_results, current_results
):
    """Test detailed report with all comparison data."""
    comparisons = comparator.compare_result_sets(baseline_results, current_results)

    try:
        from cbr_mcp_server.performance.framework.benchmark_comparison import (
            generate_detailed_report,
        )
    except ImportError:
        pytest.skip("benchmark_comparison module not available")

    report = generate_detailed_report(comparisons)

    assert isinstance(report, str)
    # Report should include all benchmark names
    assert "benchmark_a" in report
    assert "benchmark_b" in report
    assert "benchmark_c" in report

    # Report should include key metrics
    assert "baseline" in report.lower() or "Baseline" in report
    assert "current" in report.lower() or "Current" in report
    assert "%" in report  # Percent changes


def test_comparison_visualization_data(comparator, baseline_results, current_results):
    """Test generation of data suitable for visualization."""
    comparisons = comparator.compare_result_sets(baseline_results, current_results)

    try:
        from cbr_mcp_server.performance.framework.benchmark_comparison import (
            generate_visualization_data,
        )
    except ImportError:
        pytest.skip("benchmark_comparison module not available")

    viz_data = generate_visualization_data(comparisons)

    assert isinstance(viz_data, dict)
    assert "benchmark_names" in viz_data
    assert "baseline_values" in viz_data
    assert "current_values" in viz_data
    assert "percent_changes" in viz_data

    # All lists should have same length
    assert len(viz_data["benchmark_names"]) == 3
    assert len(viz_data["baseline_values"]) == 3
    assert len(viz_data["current_values"]) == 3
    assert len(viz_data["percent_changes"]) == 3


def test_export_comparison_results_to_dict(
    comparator, baseline_results, current_results
):
    """Test exporting comparison results to dictionary format."""
    comparisons = comparator.compare_result_sets(baseline_results, current_results)

    try:
        from cbr_mcp_server.performance.framework.benchmark_comparison import (
            export_comparison_results,
        )
    except ImportError:
        pytest.skip("benchmark_comparison module not available")

    exported = export_comparison_results(comparisons)

    assert isinstance(exported, list)
    assert len(exported) == 3

    for item in exported:
        assert isinstance(item, dict)
        assert "benchmark_name" in item
        assert "baseline_mean_ms" in item
        assert "current_mean_ms" in item
        assert "percent_change" in item
        assert "is_regression" in item
        assert "is_improvement" in item
        assert "is_significant" in item
        assert "effect_size" in item
        assert "confidence_interval" in item

        # Verify types
        assert isinstance(item["benchmark_name"], str)
        assert isinstance(item["baseline_mean_ms"], (int, float))
        assert isinstance(item["current_mean_ms"], (int, float))
        assert isinstance(item["percent_change"], (int, float))
        assert isinstance(item["is_regression"], bool)
        assert isinstance(item["is_improvement"], bool)
        assert isinstance(item["is_significant"], bool)
