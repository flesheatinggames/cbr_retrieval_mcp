"""
Profiling configuration module.

This module provides configuration management for profiling operations,
including cProfile settings, memory profiler settings, and preset configurations.
"""

from pathlib import Path
from typing import Dict, Optional


class CProfileConfig:
    """Configuration for cProfile profiling operations."""

    VALID_SORT_OPTIONS = ["cumulative", "time", "calls"]
    VALID_OUTPUT_FORMATS = ["text", "stats", "file"]

    def __init__(
        self,
        enabled: bool = True,
        sort_by: str = "cumulative",
        output_format: str = "text",
        top_functions: int = 20,
        save_to_file: bool = False,
        output_path: Optional[str] = None,
    ):
        """
        Initialize cProfile configuration.

        Args:
            enabled: Whether cProfile profiling is enabled
            sort_by: Sort order for profiling results (cumulative, time, calls)
            output_format: Output format (text, stats, file)
            top_functions: Number of top functions to display
            save_to_file: Whether to save output to file
            output_path: Path to save output file (required if save_to_file=True)

        Raises:
            ValueError: If validation fails
            TypeError: If types are incorrect
        """
        # Validate sort_by
        if sort_by not in self.VALID_SORT_OPTIONS:
            raise ValueError(
                f"sort_by must be one of {self.VALID_SORT_OPTIONS}, got: {sort_by}"
            )

        # Validate output_format
        if output_format not in self.VALID_OUTPUT_FORMATS:
            raise ValueError(
                f"output_format must be one of {self.VALID_OUTPUT_FORMATS}, got: {output_format}"
            )

        # Validate top_functions
        if not isinstance(top_functions, int):
            raise TypeError(f"top_functions must be int, got: {type(top_functions)}")
        if top_functions <= 0:
            raise ValueError(f"top_functions must be positive, got: {top_functions}")

        # Validate save_to_file and output_path
        if save_to_file and output_path is None:
            raise ValueError("output_path is required when save_to_file=True")

        if output_path is not None and not isinstance(output_path, str):
            raise TypeError(f"output_path must be str or None, got: {type(output_path)}")

        self.enabled = enabled
        self.sort_by = sort_by
        self.output_format = output_format
        self.top_functions = top_functions
        self.save_to_file = save_to_file
        self.output_path = output_path

    def to_dict(self) -> Dict:
        """Serialize configuration to dictionary."""
        return {
            "enabled": self.enabled,
            "sort_by": self.sort_by,
            "output_format": self.output_format,
            "top_functions": self.top_functions,
            "save_to_file": self.save_to_file,
            "output_path": self.output_path,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CProfileConfig":
        """
        Deserialize configuration from dictionary.

        Args:
            data: Dictionary containing configuration data

        Returns:
            CProfileConfig instance

        Raises:
            KeyError: If required keys are missing
            ValueError: If validation fails
            TypeError: If types are incorrect
        """
        return cls(
            enabled=data["enabled"],
            sort_by=data["sort_by"],
            output_format=data["output_format"],
            top_functions=data["top_functions"],
            save_to_file=data["save_to_file"],
            output_path=data["output_path"],
        )


class MemoryProfileConfig:
    """Configuration for memory profiling operations."""

    VALID_UNITS = ["MB", "GB"]

    def __init__(
        self,
        enabled: bool = True,
        interval: float = 0.01,
        max_usage: bool = False,
        threshold_mb: Optional[float] = None,
        unit: str = "MB",
    ):
        """
        Initialize memory profiler configuration.

        Args:
            enabled: Whether memory profiling is enabled
            interval: Sampling interval in seconds
            max_usage: Whether to track max memory usage
            threshold_mb: Memory threshold in MB for alerts (None for no threshold)
            unit: Memory unit (MB or GB)

        Raises:
            ValueError: If validation fails
            TypeError: If types are incorrect
        """
        # Validate interval
        if not isinstance(interval, (int, float)):
            raise TypeError(f"interval must be numeric, got: {type(interval)}")
        if interval <= 0:
            raise ValueError(f"interval must be positive, got: {interval}")

        # Validate max_usage
        if not isinstance(max_usage, bool):
            raise TypeError(f"max_usage must be bool, got: {type(max_usage)}")

        # Validate threshold_mb
        if threshold_mb is not None:
            if not isinstance(threshold_mb, (int, float)):
                raise TypeError(
                    f"threshold_mb must be numeric or None, got: {type(threshold_mb)}"
                )
            if threshold_mb <= 0:
                raise ValueError(
                    f"threshold_mb must be positive when set, got: {threshold_mb}"
                )

        # Validate unit
        if unit not in self.VALID_UNITS:
            raise ValueError(
                f"unit must be one of {self.VALID_UNITS}, got: {unit}"
            )

        self.enabled = enabled
        self.interval = interval
        self.max_usage = max_usage
        self.threshold_mb = threshold_mb
        self.unit = unit

    def to_dict(self) -> Dict:
        """Serialize configuration to dictionary."""
        return {
            "enabled": self.enabled,
            "interval": self.interval,
            "max_usage": self.max_usage,
            "threshold_mb": self.threshold_mb,
            "unit": self.unit,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "MemoryProfileConfig":
        """
        Deserialize configuration from dictionary.

        Args:
            data: Dictionary containing configuration data

        Returns:
            MemoryProfileConfig instance

        Raises:
            KeyError: If required keys are missing
            ValueError: If validation fails
            TypeError: If types are incorrect
        """
        return cls(
            enabled=data["enabled"],
            interval=data["interval"],
            max_usage=data["max_usage"],
            threshold_mb=data["threshold_mb"],
            unit=data["unit"],
        )


class ProfilingConfig:
    """Main profiling configuration combining cProfile and memory profiling."""

    def __init__(
        self,
        cprofile: CProfileConfig,
        memory: MemoryProfileConfig,
    ):
        """
        Initialize profiling configuration.

        Args:
            cprofile: cProfile configuration
            memory: Memory profiler configuration

        Raises:
            TypeError: If sub-configs are not the correct types
            ValueError: If validation fails
            AttributeError: If required attributes are missing
        """
        # Validate cprofile type
        if not isinstance(cprofile, CProfileConfig):
            raise TypeError(
                f"cprofile must be CProfileConfig instance, got: {type(cprofile)}"
            )

        # Validate memory type
        if not isinstance(memory, MemoryProfileConfig):
            raise TypeError(
                f"memory must be MemoryProfileConfig instance, got: {type(memory)}"
            )

        self.cprofile = cprofile
        self.memory = memory

    def to_dict(self) -> Dict:
        """
        Serialize configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "cprofile": self.cprofile.to_dict(),
            "memory": self.memory.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ProfilingConfig":
        """
        Deserialize configuration from dictionary.

        Args:
            data: Dictionary containing configuration data

        Returns:
            ProfilingConfig instance

        Raises:
            KeyError: If required keys are missing
            ValueError: If validation fails
            TypeError: If types are incorrect
        """
        cprofile = CProfileConfig.from_dict(data["cprofile"])
        memory = MemoryProfileConfig.from_dict(data["memory"])
        return cls(cprofile=cprofile, memory=memory)

    @classmethod
    def quick_preset(cls) -> "ProfilingConfig":
        """
        Create a "quick" preset configuration with minimal overhead.

        Returns:
            ProfilingConfig configured for quick profiling

        Characteristics:
            - Small number of top functions (≤10)
            - Large sampling interval (≥0.1) for minimal overhead
            - Suitable for rapid profiling
        """
        cprofile = CProfileConfig(
            enabled=True,
            sort_by="cumulative",
            output_format="text",
            top_functions=10,
            save_to_file=False,
            output_path=None,
        )
        memory = MemoryProfileConfig(
            enabled=True,
            interval=0.1,
            max_usage=False,
            threshold_mb=None,
            unit="MB",
        )
        return cls(cprofile=cprofile, memory=memory)

    @classmethod
    def detailed_preset(cls) -> "ProfilingConfig":
        """
        Create a "detailed" preset configuration for comprehensive profiling.

        Returns:
            ProfilingConfig configured for detailed profiling

        Characteristics:
            - Large number of top functions (≥50)
            - Small sampling interval (≤0.01) for detailed sampling
            - Both profilers enabled
            - Suitable for in-depth performance analysis
        """
        cprofile = CProfileConfig(
            enabled=True,
            sort_by="cumulative",
            output_format="text",
            top_functions=50,
            save_to_file=False,
            output_path=None,
        )
        memory = MemoryProfileConfig(
            enabled=True,
            interval=0.01,
            max_usage=True,
            threshold_mb=None,
            unit="MB",
        )
        return cls(cprofile=cprofile, memory=memory)

    @classmethod
    def production_preset(cls) -> "ProfilingConfig":
        """
        Create a "production" preset configuration with balanced overhead.

        Returns:
            ProfilingConfig configured for production use

        Characteristics:
            - Moderate number of top functions (10-30)
            - Moderate sampling interval (0.05-0.1)
            - Balanced settings for production use
            - Low performance impact
        """
        cprofile = CProfileConfig(
            enabled=True,
            sort_by="cumulative",
            output_format="text",
            top_functions=20,
            save_to_file=False,
            output_path=None,
        )
        memory = MemoryProfileConfig(
            enabled=True,
            interval=0.05,
            max_usage=False,
            threshold_mb=None,
            unit="MB",
        )
        return cls(cprofile=cprofile, memory=memory)
