"""
Data models for performance optimization.

This module contains Pydantic models for:
- Memory configuration (MemoryConfig)
- Memory usage metrics (MemoryMetrics)
- Memory allocation breakdown (MemoryAllocation)
- Cache configuration (CachePolicy)
- Query optimization configuration (QueryOptimizationConfig)
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


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
