"""
Data models for performance optimization.

This module contains Pydantic models for:
- Memory configuration (MemoryConfig)
- Memory usage metrics (MemoryMetrics)
- Memory allocation breakdown (MemoryAllocation)
- Cache configuration (CachePolicy)
- Query optimization configuration (QueryOptimizationConfig)
- Lazy loading configuration (LazyLoadingConfig)
- Index optimization configuration (IndexOptimizationConfig)
"""

import logging
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)


class MemoryConfig(BaseModel):
    """Configuration for memory management."""

    max_memory_mb: int = Field(
        default=500, ge=100, le=2000, description="Maximum memory usage in MB"
    )

    embedding_cache_size: int = Field(
        default=1000,
        ge=100,
        le=5000,
        description="Maximum number of embeddings to cache",
    )

    memory_check_interval_sec: float = Field(
        default=10.0,
        ge=1.0,
        le=60.0,
        description="Interval for memory usage checks in seconds",
    )

    pressure_threshold_pct: float = Field(
        default=0.85,
        ge=0.5,
        le=0.95,
        description="Memory pressure threshold as percentage of max",
    )

    emergency_eviction_pct: float = Field(
        default=0.30,
        ge=0.10,
        le=0.50,
        description="Percentage of cache to evict under pressure",
    )


class MemoryMetrics(BaseModel):
    """Memory usage metrics."""

    current_mb: float = Field(description="Current memory usage in MB")
    peak_mb: float = Field(description="Peak memory usage in MB")
    limit_mb: int = Field(description="Configured memory limit in MB")
    available_mb: float = Field(description="Available memory in MB")

    @property
    def usage_percentage(self) -> float:
        """Calculate percentage of limit used."""
        return (self.current_mb / self.limit_mb) * 100

    @property
    def is_under_pressure(self) -> bool:
        """Check if memory is under pressure."""
        return self.usage_percentage > 85.0


class MemoryAllocation(BaseModel):
    """Breakdown of memory allocation."""

    embedding_cache_mb: float = Field(default=0.0)
    query_cache_mb: float = Field(default=0.0)
    model_mb: float = Field(default=0.0)
    database_mb: float = Field(default=0.0)
    overhead_mb: float = Field(default=0.0)

    @property
    def total_mb(self) -> float:
        """Calculate total allocated memory."""
        return (
            self.embedding_cache_mb
            + self.query_cache_mb
            + self.model_mb
            + self.database_mb
            + self.overhead_mb
        )


class CachePolicy(BaseModel):
    """
    Configuration for cache behavior and limits.

    Attributes:
        max_size: Maximum number of entries in cache (None = unlimited)
        default_ttl: Default time-to-live in seconds (None = never expire)
        eviction_policy: Eviction strategy ("LRU" or "FIFO")
    """

    max_size: Optional[int] = Field(
        default=1000,
        description="Maximum cache entries (None for unlimited)",
    )

    default_ttl: Optional[int] = Field(
        default=3600,
        description="Default TTL in seconds (None for no expiration)",
    )

    eviction_policy: Literal["LRU", "FIFO"] = Field(
        default="LRU",
        description="Eviction strategy",
    )

    @field_validator("max_size")
    @classmethod
    def validate_max_size(cls, v: Optional[int]) -> Optional[int]:
        """Validate max_size is positive or None."""
        if v is not None and v <= 0:
            raise ValueError("max_size must be positive or None")
        return v

    @field_validator("default_ttl")
    @classmethod
    def validate_default_ttl(cls, v: Optional[int]) -> Optional[int]:
        """Validate default_ttl is positive or None."""
        if v is not None and v <= 0:
            raise ValueError("default_ttl must be positive or None")
        return v

    def should_evict(self, current_size: int) -> bool:
        """
        Check if eviction is needed based on current cache size.

        Args:
            current_size: Current number of entries in cache

        Returns:
            True if cache is at or over max_size limit, False otherwise
        """
        if self.max_size is None:
            # Unlimited size - never evict
            return False
        return current_size >= self.max_size


class QueryOptimizationConfig(BaseModel):
    """
    Configuration for query optimization and performance tuning.

    This configuration controls connection pooling, query batching,
    caching behavior, and timeout settings for ChromaDB queries.

    Attributes:
        connection_pool_size: Number of ChromaDB connections to maintain in pool
        batch_query_threshold: Minimum queries to trigger batch processing
        batch_max_wait_ms: Maximum wait time for batch accumulation in milliseconds
        query_timeout_ms: Individual query timeout in milliseconds
        enable_query_cache: Whether to use query result caching
        cache_ttl_seconds: Query cache time-to-live in seconds
        enable_connection_pooling: Whether to use connection pooling
    """

    connection_pool_size: int = Field(
        default=5,
        description="Number of ChromaDB connections in pool",
    )

    batch_query_threshold: int = Field(
        default=3,
        description="Minimum queries to trigger batch processing",
    )

    batch_max_wait_ms: int = Field(
        default=50,
        description="Maximum wait time for batch in milliseconds",
    )

    query_timeout_ms: int = Field(
        default=5000,
        description="Individual query timeout in milliseconds",
    )

    enable_query_cache: bool = Field(
        default=True,
        description="Enable query result caching",
    )

    cache_ttl_seconds: int = Field(
        default=300,
        description="Query cache TTL in seconds",
    )

    enable_connection_pooling: bool = Field(
        default=True,
        description="Enable connection pooling",
    )

    @field_validator("connection_pool_size")
    @classmethod
    def validate_connection_pool_size(cls, v: int) -> int:
        """Validate connection_pool_size is positive."""
        if v < 1:
            raise ValueError("connection_pool_size must be at least 1")
        return v

    @field_validator("batch_query_threshold")
    @classmethod
    def validate_batch_query_threshold(cls, v: int) -> int:
        """Validate batch_query_threshold is positive."""
        if v < 1:
            raise ValueError("batch_query_threshold must be at least 1")
        return v

    @field_validator("batch_max_wait_ms")
    @classmethod
    def validate_batch_max_wait_ms(cls, v: int) -> int:
        """Validate batch_max_wait_ms is positive."""
        if v < 1:
            raise ValueError("batch_max_wait_ms must be at least 1")
        return v

    @field_validator("query_timeout_ms")
    @classmethod
    def validate_query_timeout_ms(cls, v: int) -> int:
        """Validate query_timeout_ms meets minimum threshold."""
        if v < 100:
            raise ValueError("query_timeout_ms must be at least 100")
        return v

    @field_validator("cache_ttl_seconds")
    @classmethod
    def validate_cache_ttl_seconds(cls, v: int) -> int:
        """Validate cache_ttl_seconds is non-negative."""
        if v < 0:
            raise ValueError("cache_ttl_seconds must be non-negative")
        return v


class LazyLoadingConfig(BaseModel):
    """
    Configuration for lazy loading system with predictive preloading.

    This configuration controls the behavior of the lazy loading system,
    which loads case embeddings and data on-demand rather than at startup.
    It includes support for predictive preloading based on access patterns
    to maintain performance while minimizing memory usage.

    Attributes:
        lazy_load_enabled: Enable/disable lazy loading system (default: True)
        preload_hot_cases: Enable predictive preloading of frequently accessed cases (default: True)
        hot_case_count: Number of hot cases to pre-load based on access frequency (default: 50)
        background_loading_enabled: Enable background loading tasks for non-critical cases (default: True)
        access_window_hours: Time window in hours for tracking access patterns (default: 24)
        min_access_frequency: Minimum access frequency (accesses per hour) for preload candidates (default: 0.5)
        preload_batch_size: Maximum number of cases to preload in a single batch operation (default: 20)
        max_concurrent_loads: Maximum number of concurrent loading tasks to prevent resource exhaustion (default: 5)
    """

    lazy_load_enabled: bool = Field(
        default=True,
        description="Enable/disable lazy loading",
    )

    preload_hot_cases: bool = Field(
        default=True,
        description="Enable predictive preloading of hot cases",
    )

    hot_case_count: int = Field(
        default=50,
        description="Number of hot cases to pre-load",
    )

    background_loading_enabled: bool = Field(
        default=True,
        description="Enable background loading",
    )

    access_window_hours: int = Field(
        default=24,
        description="Hours for access pattern tracking window",
    )

    min_access_frequency: float = Field(
        default=0.5,
        description="Minimum frequency for preload candidates",
    )

    preload_batch_size: int = Field(
        default=20,
        description="Maximum cases to preload in one batch",
    )

    max_concurrent_loads: int = Field(
        default=5,
        description="Maximum concurrent loading tasks",
    )

    max_cache_size: int = Field(
        default=200,
        description="Maximum number of cases to keep in memory cache (LRU eviction)",
        gt=0,
    )

    @field_validator("hot_case_count")
    @classmethod
    def validate_hot_case_count(cls, v: int) -> int:
        """Validate hot_case_count is positive."""
        if v < 1:
            raise ValueError("hot_case_count must be at least 1")
        return v

    @field_validator("access_window_hours")
    @classmethod
    def validate_access_window_hours(cls, v: int) -> int:
        """Validate access_window_hours is positive."""
        if v < 1:
            raise ValueError("access_window_hours must be at least 1")
        return v

    @field_validator("min_access_frequency")
    @classmethod
    def validate_min_access_frequency(cls, v: float) -> float:
        """Validate min_access_frequency is between 0 and 1."""
        if v < 0.0 or v > 1.0:
            raise ValueError("min_access_frequency must be between 0.0 and 1.0")

        # Warn about extreme values
        if v == 0.0:
            logger.warning("min_access_frequency=0.0 will preload all cases")
        if v >= 1.0:
            logger.warning("min_access_frequency>=1.0 may prevent most preloading")

        return v

    @field_validator("preload_batch_size")
    @classmethod
    def validate_preload_batch_size(cls, v: int) -> int:
        """Validate preload_batch_size is positive."""
        if v < 1:
            raise ValueError("preload_batch_size must be at least 1")
        return v

    @field_validator("max_concurrent_loads")
    @classmethod
    def validate_max_concurrent_loads(cls, v: int) -> int:
        """Validate max_concurrent_loads is positive."""
        if v < 1:
            raise ValueError("max_concurrent_loads must be at least 1")
        return v

    @field_validator("max_cache_size")
    @classmethod
    def validate_max_cache_size(cls, v: int) -> int:
        """Validate max_cache_size is positive."""
        if v < 1:
            raise ValueError("max_cache_size must be at least 1")
        return v


class IndexOptimizationConfig(BaseModel):
    """
    Configuration for ChromaDB HNSW index optimization.

    This configuration controls the HNSW (Hierarchical Navigable Small World)
    index parameters used by ChromaDB for approximate nearest neighbor search.

    Attributes:
        space: Distance metric for similarity search ("l2", "ip", or "cosine")
        ef_construction: Build-time search parameter (4-1000, default: 100)
        ef_search: Query-time search parameter (1+, default: 10, must be <= ef_construction)
        M: Number of bi-directional links per node (4-64, default: 16)
    """

    space: Literal["l2", "ip", "cosine"] = Field(
        default="l2",
        description="Distance metric (l2=Euclidean, ip=Inner Product, cosine=Cosine Similarity)",
    )

    ef_construction: int = Field(
        default=100,
        description="Build-time search parameter (higher = better accuracy, slower build)",
    )

    ef_search: int = Field(
        default=10,
        description="Query-time search parameter (higher = better accuracy, slower queries)",
    )

    M: int = Field(
        default=16,
        description="Number of bi-directional links per node (higher = more memory, better accuracy)",
    )

    @field_validator("ef_construction", mode="before")
    @classmethod
    def validate_ef_construction(cls, v: int) -> int:
        """Validate ef_construction is in valid range [4, 1000] and is an integer."""
        # Ensure type is int, not string
        if not isinstance(v, int):
            raise ValueError("ef_construction must be an integer")
        if v < 4 or v > 1000:
            raise ValueError("ef_construction must be between 4 and 1000")
        return v

    @field_validator("ef_search", mode="before")
    @classmethod
    def validate_ef_search(cls, v: int) -> int:
        """Validate ef_search is positive and is an integer."""
        # Ensure type is int, not string
        if not isinstance(v, int):
            raise ValueError("ef_search must be an integer")
        if v < 1:
            raise ValueError("ef_search must be at least 1")
        return v

    @field_validator("M", mode="before")
    @classmethod
    def validate_m(cls, v: int) -> int:
        """Validate M is in valid range [4, 64] and is an integer."""
        # Ensure type is int, not string
        if not isinstance(v, int):
            raise ValueError("M must be an integer")
        if v < 4 or v > 64:
            raise ValueError("M must be between 4 and 64")
        return v

    @model_validator(mode="after")
    def validate_ef_search_vs_ef_construction(self) -> "IndexOptimizationConfig":
        """
        Validate business rule: ef_search must be <= ef_construction.

        When only one parameter is set, auto-adjust the other to maintain the constraint.
        When both are explicitly set, enforce the constraint strictly.
        """
        # Get fields that were explicitly set during initialization
        fields_set = (
            self.model_fields_set if hasattr(self, "model_fields_set") else set()
        )

        # If both ef_search and ef_construction were explicitly provided, enforce strictly
        if "ef_search" in fields_set and "ef_construction" in fields_set:
            if self.ef_search > self.ef_construction:
                raise ValueError(
                    f"ef_search ({self.ef_search}) must be <= ef_construction ({self.ef_construction})"
                )
        # If only ef_construction was set and it's less than default ef_search
        elif "ef_construction" in fields_set and "ef_search" not in fields_set:
            if self.ef_search > self.ef_construction:
                self.ef_search = self.ef_construction
        # If only ef_search was set and it's greater than default ef_construction
        elif "ef_search" in fields_set and "ef_construction" not in fields_set:
            if self.ef_search > self.ef_construction:
                self.ef_construction = self.ef_search

        return self

    def to_chroma_metadata(self) -> dict[str, Any]:
        """
        Convert configuration to ChromaDB-compatible HNSW metadata format.

        Returns:
            dict: Metadata dictionary with ChromaDB HNSW parameter keys
                - hnsw:space: Distance metric
                - hnsw:construction_ef: Build-time search parameter
                - hnsw:search_ef: Query-time search parameter
                - hnsw:M: Bi-directional links per node
        """
        return {
            "hnsw:space": self.space,
            "hnsw:construction_ef": self.ef_construction,
            "hnsw:search_ef": self.ef_search,
            "hnsw:M": self.M,
        }
