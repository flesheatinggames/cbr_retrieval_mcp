"""
Index Performance Monitoring for CBR MCP Server.

This module provides comprehensive monitoring of ChromaDB index performance including:
- Query latency tracking with percentile calculations
- Index size growth monitoring
- Memory usage estimation
- HNSW parameter tracking and change detection
- Threshold violation detection
- Performance trend analysis

Thread-safe implementation supports concurrent metric collection from multiple queries.
"""

import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import psutil
from pydantic import BaseModel, Field, ValidationInfo, field_validator


class LatencyDistribution(BaseModel):
    """
    Distribution of query latencies with percentile metrics.

    Attributes:
        p50_ms: 50th percentile (median) latency in milliseconds
        p95_ms: 95th percentile latency in milliseconds
        p99_ms: 99th percentile latency in milliseconds
        sample_count: Number of samples in distribution
        outlier_count: Number of outliers detected (beyond 3x IQR)
    """

    p50_ms: float = Field(ge=0.0, description="Median query latency")
    p95_ms: float = Field(ge=0.0, description="95th percentile latency")
    p99_ms: float = Field(ge=0.0, description="99th percentile latency")
    sample_count: int = Field(default=0, ge=0, description="Number of samples")
    outlier_count: int = Field(default=0, ge=0, description="Number of outliers")

    @field_validator("p95_ms")
    @classmethod
    def validate_p95(cls, v: float, info: ValidationInfo) -> float:
        """Ensure p95 >= p50."""
        if "p50_ms" in info.data and v < info.data["p50_ms"]:
            raise ValueError("p95 must be >= p50")
        return v

    @field_validator("p99_ms")
    @classmethod
    def validate_p99(cls, v: float, info: ValidationInfo) -> float:
        """Ensure p99 >= p95."""
        if "p95_ms" in info.data and v < info.data["p95_ms"]:
            raise ValueError("p99 must be >= p95")
        return v


class IndexPerformanceThresholds(BaseModel):
    """
    Configuration thresholds for performance monitoring.

    Attributes:
        max_query_latency_ms: Maximum acceptable p95 query latency
        max_memory_mb: Maximum acceptable index memory usage in MB
        max_index_size: Maximum acceptable vector count
    """

    max_query_latency_ms: float = Field(
        default=200.0, gt=0.0, description="Maximum p95 query latency in ms"
    )
    max_memory_mb: int = Field(
        default=512, gt=0, description="Maximum index memory in MB"
    )
    max_index_size: int = Field(default=1000, gt=0, description="Maximum vector count")


class IndexPerformanceMetrics(BaseModel):
    """
    Aggregated index performance metrics.

    Attributes:
        timestamp: Metrics collection timestamp
        index_size: Current vector count in index
        memory_mb: Estimated index memory usage in MB
        latency_distribution: Query latency distribution
        hnsw_params: HNSW algorithm configuration parameters
    """

    timestamp: datetime = Field(description="Metrics timestamp")
    index_size: int = Field(ge=0, description="Vector count")
    memory_mb: float = Field(default=0.0, ge=0.0, description="Memory usage in MB")
    latency_distribution: LatencyDistribution = Field(
        description="Latency distribution"
    )
    hnsw_params: Dict[str, Any] = Field(
        default_factory=dict, description="HNSW configuration"
    )


class IndexPerformanceMonitor:
    """
    Monitor and analyze ChromaDB index performance.

    Provides comprehensive tracking of query latency, index size, memory usage,
    and HNSW configuration. Supports threshold violation detection and trend
    analysis for proactive performance management.

    Thread-safe for concurrent metric collection across multiple queries.
    """

    def __init__(
        self,
        collection: Any,
        thresholds: Optional[IndexPerformanceThresholds] = None,
        enabled: bool = True,
    ):
        """
        Initialize index performance monitor.

        Args:
            collection: ChromaDB collection to monitor
            thresholds: Performance thresholds (uses defaults if None)
            enabled: Whether monitoring is enabled
        """
        self.collection = collection
        self.enabled = enabled
        self.thresholds = thresholds or IndexPerformanceThresholds()

        # Metrics storage
        self.query_latencies: List[float] = []
        self.index_size_history: List[int] = []
        self.baseline_memory_mb: float = 0.0
        self.metrics: Optional[IndexPerformanceMetrics] = None
        self.metrics_history: List[IndexPerformanceMetrics] = []

        # Thread safety
        self._lock = threading.Lock()

        # PerformanceTracker integration
        self._tracker_callback: Optional[Callable[..., None]] = None

    def track_query_latency(self, latency_ms: float) -> None:
        """
        Track query latency measurement (thread-safe).

        Args:
            latency_ms: Query latency in milliseconds
        """
        with self._lock:
            self.query_latencies.append(latency_ms)

    def calculate_latency_distribution(self) -> LatencyDistribution:
        """
        Calculate latency distribution percentiles and detect outliers.

        Returns:
            LatencyDistribution with percentile metrics
        """
        with self._lock:
            if not self.query_latencies:
                return LatencyDistribution(
                    p50_ms=0.0,
                    p95_ms=0.0,
                    p99_ms=0.0,
                    sample_count=0,
                    outlier_count=0,
                )

            latencies = np.array(self.query_latencies)

            # Calculate percentiles
            p50 = float(np.percentile(latencies, 50))
            p95 = float(np.percentile(latencies, 95))
            p99 = float(np.percentile(latencies, 99))

            # Detect outliers (beyond 3x IQR)
            q1 = float(np.percentile(latencies, 25))
            q3 = float(np.percentile(latencies, 75))
            iqr = q3 - q1
            outlier_threshold = q3 + 3 * iqr
            outliers = latencies[latencies > outlier_threshold]

            return LatencyDistribution(
                p50_ms=p50,
                p95_ms=p95,
                p99_ms=p99,
                sample_count=len(latencies),
                outlier_count=len(outliers),
            )

    def get_index_size(self) -> int:
        """
        Get current index size (vector count) from collection.

        Returns:
            Number of vectors in index
        """
        size: int = self.collection.count()
        self.index_size_history.append(size)
        return size

    def estimate_index_memory_usage(self) -> float:
        """
        Estimate index memory usage with baseline subtraction.

        Returns:
            Estimated index memory in MB
        """
        process = psutil.Process(os.getpid())
        total_memory_mb: float = process.memory_info().rss / (1024 * 1024)

        # Subtract baseline to isolate index memory
        index_memory: float = max(0.0, total_memory_mb - self.baseline_memory_mb)

        return index_memory

    def get_hnsw_parameters(self) -> Dict[str, Any]:
        """
        Extract HNSW algorithm parameters from collection metadata.

        Returns:
            Dictionary of HNSW configuration parameters
        """
        metadata = self.collection.metadata or {}

        params = {}

        # Extract HNSW parameters with fallback keys
        if "hnsw:construction_ef" in metadata:
            params["ef_construction"] = metadata["hnsw:construction_ef"]
            params["hnsw_construction_ef"] = metadata["hnsw:construction_ef"]

        if "hnsw:search_ef" in metadata:
            params["ef_search"] = metadata["hnsw:search_ef"]
            params["hnsw_search_ef"] = metadata["hnsw:search_ef"]

        if "hnsw:M" in metadata:
            params["M"] = metadata["hnsw:M"]
            params["hnsw_M"] = metadata["hnsw:M"]

        if "hnsw:space" in metadata:
            params["space"] = metadata["hnsw:space"]

        return params

    def detect_parameter_changes(
        self, initial_params: Dict[str, Any], updated_params: Dict[str, Any]
    ) -> bool:
        """
        Detect if HNSW parameters have changed.

        Args:
            initial_params: Initial HNSW parameters
            updated_params: Updated HNSW parameters

        Returns:
            True if parameters changed, False otherwise
        """
        # Compare key HNSW parameters
        key_params = [
            "ef_construction",
            "ef_search",
            "M",
            "hnsw_search_ef",
            "hnsw_construction_ef",
            "hnsw_M",
        ]

        for param in key_params:
            initial_value = initial_params.get(param)
            updated_value = updated_params.get(param)

            if initial_value is not None and updated_value is not None:
                if initial_value != updated_value:
                    return True

        return False

    def aggregate_metrics(self) -> IndexPerformanceMetrics:
        """
        Aggregate current performance metrics.

        Returns:
            IndexPerformanceMetrics with current state
        """
        metrics = IndexPerformanceMetrics(
            timestamp=datetime.now(timezone.utc),
            index_size=self.get_index_size(),
            memory_mb=self.estimate_index_memory_usage(),
            latency_distribution=self.calculate_latency_distribution(),
            hnsw_params=self.get_hnsw_parameters(),
        )

        self.metrics = metrics
        return metrics

    def export_metrics_json(self, metrics: IndexPerformanceMetrics) -> str:
        """
        Export metrics to JSON format.

        Args:
            metrics: Metrics to export

        Returns:
            JSON string representation
        """
        data = metrics.model_dump()

        # Convert datetime to ISO format
        if isinstance(data.get("timestamp"), datetime):
            data["timestamp"] = data["timestamp"].isoformat()

        return json.dumps(data, indent=2)

    def check_thresholds(self) -> Optional[List[str]]:
        """
        Check for threshold violations.

        Returns:
            List of violation messages, or None/empty list if no violations
        """
        violations = []

        # Check latency threshold (p95)
        if self.query_latencies:
            distribution = self.calculate_latency_distribution()
            if distribution.p95_ms > self.thresholds.max_query_latency_ms:
                violations.append(
                    f"Latency threshold exceeded: {distribution.p95_ms:.2f}ms "
                    f"(threshold: {self.thresholds.max_query_latency_ms}ms)"
                )

        # Check memory threshold
        memory_mb = self.estimate_index_memory_usage()
        if memory_mb > self.thresholds.max_memory_mb:
            violations.append(
                f"Memory threshold exceeded: {memory_mb:.2f}MB "
                f"(threshold: {self.thresholds.max_memory_mb}MB)"
            )

        # Check index size threshold
        index_size = self.get_index_size()
        if index_size > self.thresholds.max_index_size:
            violations.append(
                f"Index size threshold exceeded: {index_size} vectors "
                f"(threshold: {self.thresholds.max_index_size})"
            )

        return violations if violations else None

    def calculate_performance_trend(self) -> Dict[str, Any]:
        """
        Calculate performance trend from historical latencies.

        Uses linear regression to determine if performance is improving,
        degrading, or stable.

        Returns:
            Dictionary with trend direction and slope
        """
        with self._lock:
            if len(self.query_latencies) < 2:
                return {"direction": "stable", "slope": 0.0}

            # Use recent latencies for trend
            latencies = np.array(self.query_latencies)
            x = np.arange(len(latencies))

            # Linear regression
            slope = np.polyfit(x, latencies, 1)[0]

            # Determine trend direction
            if slope < -0.5:
                direction = "improving"
            elif slope > 0.5:
                direction = "degrading"
            else:
                direction = "stable"

            return {"direction": direction, "slope": float(slope)}

    def reset_metrics(self, preserve_history: bool = False) -> None:
        """
        Reset accumulated metrics.

        Args:
            preserve_history: If True, save current metrics to history
        """
        with self._lock:
            if preserve_history and self.metrics:
                self.metrics_history.append(self.metrics)

            # Clear current metrics
            self.query_latencies.clear()
            self.metrics = None
            # Note: index_size_history and thresholds are preserved

    def set_tracker_callback(self, callback: Callable[..., None]) -> None:
        """
        Set callback for PerformanceTracker integration.

        Args:
            callback: Callable to receive metrics updates
        """
        self._tracker_callback = callback

    def report_to_tracker(self, metrics: IndexPerformanceMetrics) -> None:
        """
        Report metrics to PerformanceTracker via callback.

        Args:
            metrics: Metrics to report
        """
        if self._tracker_callback:
            self._tracker_callback(metrics)
