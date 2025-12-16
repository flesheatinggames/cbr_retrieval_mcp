"""
Test suite for profiling configuration module.

This module provides comprehensive tests for profiling configuration management,
including cProfile settings, memory profiler settings, configuration presets,
and validation logic.

Tests follow TDD methodology - all tests should fail initially until the
profiling_config module is implemented.
"""

from pathlib import Path
from typing import Dict, Optional
import sys
import importlib.util

import pytest

# Ensure project root is in sys.path for imports
_project_root = Path(__file__).parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Import will fail initially - this is expected in TDD
CProfileConfig = None
MemoryProfileConfig = None
ProfilingConfig = None

_config_file = _project_root / "benchmarks" / "profiling" / "profiling_config.py"
if _config_file.exists():
    # Module exists, load it dynamically
    spec = importlib.util.spec_from_file_location(
        "benchmarks.profiling.profiling_config",
        _config_file
    )
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules["benchmarks.profiling.profiling_config"] = module
        spec.loader.exec_module(module)
        CProfileConfig = module.CProfileConfig
        MemoryProfileConfig = module.MemoryProfileConfig
        ProfilingConfig = module.ProfilingConfig


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def default_profiling_config() -> "ProfilingConfig":
    """Provide default ProfilingConfig instance for tests."""
    return ProfilingConfig(cprofile=CProfileConfig(), memory=MemoryProfileConfig())


@pytest.fixture
def quick_profiling_config() -> "ProfilingConfig":
    """Provide quick preset ProfilingConfig for tests."""
    return ProfilingConfig.quick_preset()


@pytest.fixture
def detailed_profiling_config() -> "ProfilingConfig":
    """Provide detailed preset ProfilingConfig for tests."""
    return ProfilingConfig.detailed_preset()


@pytest.fixture
def production_profiling_config() -> "ProfilingConfig":
    """Provide production preset ProfilingConfig for tests."""
    return ProfilingConfig.production_preset()


@pytest.fixture
def sample_config_dict() -> Dict:
    """Provide sample configuration dictionary for deserialization tests."""
    return {
        "cprofile": {
            "enabled": True,
            "sort_by": "cumulative",
            "output_format": "text",
            "top_functions": 20,
            "save_to_file": False,
            "output_path": None,
        },
        "memory": {
            "enabled": True,
            "interval": 0.01,
            "max_usage": False,
            "threshold_mb": None,
            "unit": "MB",
        },
    }


# ============================================================================
# ProfilingConfig Class Tests
# ============================================================================


@pytest.mark.unit
def test_default_profiling_config_initialization(default_profiling_config):
    """
    Test that default ProfilingConfig initializes with valid defaults.

    Verifies:
    - cprofile field exists and is CProfileConfig type
    - memory field exists and is MemoryProfileConfig type
    - Both sub-configs have sensible defaults
    """
    config = default_profiling_config

    # Verify sub-config types
    assert isinstance(
        config.cprofile, CProfileConfig
    ), "cprofile should be CProfileConfig instance"
    assert isinstance(
        config.memory, MemoryProfileConfig
    ), "memory should be MemoryProfileConfig instance"

    # Verify cprofile defaults
    assert config.cprofile.enabled is True, "cprofile should be enabled by default"
    assert config.cprofile.sort_by == "cumulative", "Default sort should be cumulative"
    assert (
        config.cprofile.output_format == "text"
    ), "Default output format should be text"
    assert config.cprofile.top_functions == 20, "Default top_functions should be 20"

    # Verify memory defaults
    assert config.memory.enabled is True, "memory profiler should be enabled by default"
    assert config.memory.interval == 0.01, "Default interval should be 0.01"
    assert config.memory.max_usage is False, "max_usage should be False by default"
    assert config.memory.unit == "MB", "Default unit should be MB"


@pytest.mark.unit
def test_custom_profiling_config_creation():
    """
    Test that custom ProfilingConfig preserves custom sub-config values.

    Verifies:
    - Custom CProfileConfig values are preserved
    - Custom MemoryProfileConfig values are preserved
    - No default override occurs
    """
    # Create custom sub-configs
    custom_cprofile = CProfileConfig(
        enabled=False,
        sort_by="time",
        output_format="stats",
        top_functions=50,
        save_to_file=True,
        output_path="/tmp/profile.stats",
    )

    custom_memory = MemoryProfileConfig(
        enabled=False,
        interval=0.1,
        max_usage=True,
        threshold_mb=500.0,
        unit="GB",
    )

    # Create ProfilingConfig with custom sub-configs
    config = ProfilingConfig(cprofile=custom_cprofile, memory=custom_memory)

    # Verify cprofile customization preserved
    assert config.cprofile.enabled is False
    assert config.cprofile.sort_by == "time"
    assert config.cprofile.output_format == "stats"
    assert config.cprofile.top_functions == 50
    assert config.cprofile.save_to_file is True
    assert config.cprofile.output_path == "/tmp/profile.stats"

    # Verify memory customization preserved
    assert config.memory.enabled is False
    assert config.memory.interval == 0.1
    assert config.memory.max_usage is True
    assert config.memory.threshold_mb == 500.0
    assert config.memory.unit == "GB"


@pytest.mark.unit
def test_profiling_config_from_dict(sample_config_dict):
    """
    Test that ProfilingConfig.from_dict() deserializes correctly.

    Verifies:
    - Nested dictionary structure properly parsed
    - CProfileConfig and MemoryProfileConfig created from dict data
    - Invalid dict raises appropriate error
    """
    # Test valid deserialization
    config = ProfilingConfig.from_dict(sample_config_dict)

    # Verify cprofile deserialization
    assert config.cprofile.enabled is True
    assert config.cprofile.sort_by == "cumulative"
    assert config.cprofile.output_format == "text"
    assert config.cprofile.top_functions == 20
    assert config.cprofile.save_to_file is False
    assert config.cprofile.output_path is None

    # Verify memory deserialization
    assert config.memory.enabled is True
    assert config.memory.interval == 0.01
    assert config.memory.max_usage is False
    assert config.memory.threshold_mb is None
    assert config.memory.unit == "MB"

    # Test invalid dict raises error
    invalid_dict = {"cprofile": "not_a_dict", "memory": {}}
    with pytest.raises((ValueError, TypeError, KeyError)):
        ProfilingConfig.from_dict(invalid_dict)


@pytest.mark.unit
def test_profiling_config_to_dict(default_profiling_config, sample_config_dict):
    """
    Test that ProfilingConfig.to_dict() serializes correctly.

    Verifies:
    - Returns proper nested dictionary structure
    - All config values present in output
    - Round-trip conversion (to_dict -> from_dict) preserves data
    """
    config = default_profiling_config

    # Serialize to dict
    config_dict = config.to_dict()

    # Verify structure
    assert isinstance(config_dict, dict), "to_dict() should return dictionary"
    assert "cprofile" in config_dict, "Should have cprofile key"
    assert "memory" in config_dict, "Should have memory key"

    # Verify cprofile values
    assert config_dict["cprofile"]["enabled"] is True
    assert config_dict["cprofile"]["sort_by"] == "cumulative"
    assert config_dict["cprofile"]["output_format"] == "text"
    assert config_dict["cprofile"]["top_functions"] == 20

    # Verify memory values
    assert config_dict["memory"]["enabled"] is True
    assert config_dict["memory"]["interval"] == 0.01
    assert config_dict["memory"]["max_usage"] is False
    assert config_dict["memory"]["unit"] == "MB"

    # Test round-trip conversion
    config_from_dict = ProfilingConfig.from_dict(config_dict)
    assert config_from_dict.cprofile.enabled == config.cprofile.enabled
    assert config_from_dict.cprofile.sort_by == config.cprofile.sort_by
    assert config_from_dict.memory.interval == config.memory.interval
    assert config_from_dict.memory.unit == config.memory.unit


@pytest.mark.unit
def test_profiling_config_validation():
    """
    Test that ProfilingConfig validates sub-config types.

    Verifies:
    - Rejects invalid cprofile type
    - Rejects invalid memory type
    - Raises appropriate validation errors
    """
    valid_cprofile = CProfileConfig()
    valid_memory = MemoryProfileConfig()

    # Test invalid cprofile type
    with pytest.raises((TypeError, ValueError, AttributeError)):
        ProfilingConfig(cprofile="not_a_cprofile_config", memory=valid_memory)

    # Test invalid memory type
    with pytest.raises((TypeError, ValueError, AttributeError)):
        ProfilingConfig(cprofile=valid_cprofile, memory="not_a_memory_config")

    # Test both invalid
    with pytest.raises((TypeError, ValueError, AttributeError)):
        ProfilingConfig(cprofile="invalid", memory=123)


# ============================================================================
# CProfile Configuration Tests
# ============================================================================


@pytest.mark.unit
def test_cprofile_sort_options():
    """
    Test that CProfileConfig accepts valid sort options.

    Verifies:
    - "cumulative", "time", "calls" are valid
    - Invalid sort option raises validation error
    - Default is "cumulative"
    """
    # Test valid sort options
    valid_sorts = ["cumulative", "time", "calls"]
    for sort_option in valid_sorts:
        config = CProfileConfig(sort_by=sort_option)
        assert (
            config.sort_by == sort_option
        ), f"{sort_option} should be valid sort option"

    # Test default
    default_config = CProfileConfig()
    assert default_config.sort_by == "cumulative", "Default sort should be cumulative"

    # Test invalid sort option
    with pytest.raises((ValueError, TypeError)):
        CProfileConfig(sort_by="invalid_sort_option")


@pytest.mark.unit
def test_cprofile_output_format_options():
    """
    Test that CProfileConfig validates output format options.

    Verifies:
    - "text", "stats", "file" are valid
    - Invalid format raises validation error
    - Default is "text"
    """
    # Test valid output formats
    valid_formats = ["text", "stats", "file"]
    for format_option in valid_formats:
        config = CProfileConfig(output_format=format_option)
        assert (
            config.output_format == format_option
        ), f"{format_option} should be valid output format"

    # Test default
    default_config = CProfileConfig()
    assert (
        default_config.output_format == "text"
    ), "Default output format should be text"

    # Test invalid format
    with pytest.raises((ValueError, TypeError)):
        CProfileConfig(output_format="invalid_format")


@pytest.mark.unit
def test_cprofile_top_function_count():
    """
    Test that top_functions count configuration validates correctly.

    Verifies:
    - Positive integers accepted
    - Zero or negative raises validation error
    - Default is 20
    """
    # Test positive integers
    valid_counts = [1, 10, 20, 50, 100]
    for count in valid_counts:
        config = CProfileConfig(top_functions=count)
        assert config.top_functions == count, f"top_functions={count} should be valid"

    # Test default
    default_config = CProfileConfig()
    assert default_config.top_functions == 20, "Default top_functions should be 20"

    # Test zero raises error
    with pytest.raises((ValueError, TypeError)):
        CProfileConfig(top_functions=0)

    # Test negative raises error
    with pytest.raises((ValueError, TypeError)):
        CProfileConfig(top_functions=-5)


@pytest.mark.unit
def test_cprofile_file_output_configuration():
    """
    Test file output settings validation.

    Verifies:
    - save_to_file=True requires output_path
    - output_path validation for valid paths
    - None output_path when save_to_file=False
    """
    # Test save_to_file=True with valid output_path
    config_with_file = CProfileConfig(
        save_to_file=True, output_path="/tmp/profile.stats"
    )
    assert config_with_file.save_to_file is True
    assert config_with_file.output_path == "/tmp/profile.stats"

    # Test save_to_file=False with None output_path
    config_no_file = CProfileConfig(save_to_file=False, output_path=None)
    assert config_no_file.save_to_file is False
    assert config_no_file.output_path is None

    # Test save_to_file=True without output_path raises error
    with pytest.raises((ValueError, TypeError, AttributeError)):
        CProfileConfig(save_to_file=True, output_path=None)

    # Test invalid output_path type
    with pytest.raises((ValueError, TypeError)):
        CProfileConfig(save_to_file=True, output_path=12345)


# ============================================================================
# Memory Profiler Configuration Tests
# ============================================================================


@pytest.mark.unit
def test_memory_profiler_sampling_interval():
    """
    Test memory sampling interval configuration.

    Verifies:
    - Positive float values accepted
    - Zero or negative raises validation error
    - Default is 0.01 seconds
    """
    # Test positive float values
    valid_intervals = [0.001, 0.01, 0.1, 1.0]
    for interval in valid_intervals:
        config = MemoryProfileConfig(interval=interval)
        assert config.interval == interval, f"interval={interval} should be valid"

    # Test default
    default_config = MemoryProfileConfig()
    assert default_config.interval == 0.01, "Default interval should be 0.01"

    # Test zero raises error
    with pytest.raises((ValueError, TypeError)):
        MemoryProfileConfig(interval=0.0)

    # Test negative raises error
    with pytest.raises((ValueError, TypeError)):
        MemoryProfileConfig(interval=-0.01)


@pytest.mark.unit
def test_memory_profiler_max_usage_mode():
    """
    Test max_usage mode toggle.

    Verifies:
    - Boolean values accepted
    - Default is False
    - Type validation for non-boolean
    """
    # Test True
    config_true = MemoryProfileConfig(max_usage=True)
    assert config_true.max_usage is True, "max_usage=True should be valid"

    # Test False
    config_false = MemoryProfileConfig(max_usage=False)
    assert config_false.max_usage is False, "max_usage=False should be valid"

    # Test default
    default_config = MemoryProfileConfig()
    assert default_config.max_usage is False, "Default max_usage should be False"

    # Test invalid type
    with pytest.raises((ValueError, TypeError)):
        MemoryProfileConfig(max_usage="not_a_boolean")


@pytest.mark.unit
def test_memory_profiler_threshold_alerts():
    """
    Test memory threshold configuration.

    Verifies:
    - Optional threshold_mb accepts None or positive float
    - Negative threshold raises validation error
    - Threshold triggers alert behavior (conceptual)
    """
    # Test None threshold
    config_no_threshold = MemoryProfileConfig(threshold_mb=None)
    assert config_no_threshold.threshold_mb is None, "threshold_mb=None should be valid"

    # Test positive float thresholds
    valid_thresholds = [100.0, 500.0, 1000.0, 5000.0]
    for threshold in valid_thresholds:
        config = MemoryProfileConfig(threshold_mb=threshold)
        assert (
            config.threshold_mb == threshold
        ), f"threshold_mb={threshold} should be valid"

    # Test negative threshold raises error
    with pytest.raises((ValueError, TypeError)):
        MemoryProfileConfig(threshold_mb=-100.0)

    # Test zero threshold raises error
    with pytest.raises((ValueError, TypeError)):
        MemoryProfileConfig(threshold_mb=0.0)


@pytest.mark.unit
def test_memory_profiler_unit_configuration():
    """
    Test memory measurement unit options.

    Verifies:
    - "MB" and "GB" are valid units
    - Invalid unit raises validation error
    - Default is "MB"
    """
    # Test valid units
    valid_units = ["MB", "GB"]
    for unit in valid_units:
        config = MemoryProfileConfig(unit=unit)
        assert config.unit == unit, f"unit={unit} should be valid"

    # Test default
    default_config = MemoryProfileConfig()
    assert default_config.unit == "MB", "Default unit should be MB"

    # Test invalid unit
    with pytest.raises((ValueError, TypeError)):
        MemoryProfileConfig(unit="KB")

    with pytest.raises((ValueError, TypeError)):
        MemoryProfileConfig(unit="invalid_unit")


# ============================================================================
# Profiling Presets Tests
# ============================================================================


@pytest.mark.unit
def test_quick_preset_configuration(quick_profiling_config):
    """
    Test that "quick" preset has minimal overhead settings.

    Verifies:
    - cprofile.top_functions is small (≤ 10)
    - memory.interval is larger (≥ 0.1) for less frequent sampling
    - Suitable for rapid profiling with low overhead
    """
    config = quick_profiling_config

    # Verify quick preset characteristics
    assert (
        config.cprofile.top_functions <= 10
    ), "Quick preset should have small top_functions (≤10)"
    assert (
        config.memory.interval >= 0.1
    ), "Quick preset should have large interval (≥0.1) for minimal overhead"

    # Verify both profilers are configured
    assert isinstance(config.cprofile, CProfileConfig)
    assert isinstance(config.memory, MemoryProfileConfig)


@pytest.mark.unit
def test_detailed_preset_configuration(detailed_profiling_config):
    """
    Test that "detailed" preset has comprehensive settings.

    Verifies:
    - cprofile.top_functions is large (≥ 50)
    - memory.interval is small (≤ 0.01) for frequent sampling
    - Both profilers enabled
    """
    config = detailed_profiling_config

    # Verify detailed preset characteristics
    assert (
        config.cprofile.top_functions >= 50
    ), "Detailed preset should have large top_functions (≥50)"
    assert (
        config.memory.interval <= 0.01
    ), "Detailed preset should have small interval (≤0.01) for detailed sampling"

    # Verify both profilers enabled
    assert config.cprofile.enabled is True, "Detailed preset should enable cprofile"
    assert (
        config.memory.enabled is True
    ), "Detailed preset should enable memory profiler"


@pytest.mark.unit
def test_production_preset_configuration(production_profiling_config):
    """
    Test that "production" preset has minimal overhead.

    Verifies:
    - Balanced settings for production use
    - Reasonable defaults for both profilers
    - Low performance impact configuration
    """
    config = production_profiling_config

    # Verify production preset characteristics
    assert (
        10 <= config.cprofile.top_functions <= 30
    ), "Production preset should have moderate top_functions (10-30)"
    assert (
        0.05 <= config.memory.interval <= 0.1
    ), "Production preset should have moderate interval (0.05-0.1)"

    # Verify both profilers are configured
    assert isinstance(config.cprofile, CProfileConfig)
    assert isinstance(config.memory, MemoryProfileConfig)

    # Production preset should be balanced, not necessarily enabling everything
    # but should have reasonable defaults that won't impact performance heavily
