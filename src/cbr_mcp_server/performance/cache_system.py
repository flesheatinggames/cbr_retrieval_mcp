"""
Cache system for performance optimization.

This module provides:
- CacheEntry: Individual cache entries with TTL and access tracking
- CacheMetrics: Cache performance metrics
- ResultCache: LRU cache with TTL expiration
- CachePolicy: Configuration for cache behavior (re-exported from data_models)

**Thread Safety Warning:**
ResultCache is NOT thread-safe. If using in concurrent environments,
external synchronization is required (e.g., asyncio.Lock or threading.Lock).
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple, Type

from cachetools import LRUCache

from cbr_mcp_server.performance.data_models import CachePolicy

# Re-export CachePolicy for convenience
__all__ = ["CacheEntry", "CacheMetrics", "ResultCache", "CachePolicy"]


class CacheEntry:
    """
    Individual cache entry with metadata and expiration.

    Attributes:
        value: The cached value
        ttl: Time-to-live in seconds (None = never expires)
        created_at: Timestamp of creation
        last_accessed: Timestamp of last access
        access_count: Number of times accessed
    """

    def __init__(self, value: Any, ttl: Optional[int] = None):
        """
        Initialize cache entry.

        Args:
            value: The value to cache
            ttl: Time-to-live in seconds (None = never expires)
        """
        self.value: Any = value
        self.ttl: Optional[int] = ttl
        self.created_at: datetime = datetime.now()
        self.last_accessed: datetime = datetime.now()
        self.access_count: int = 0

    def is_expired(self) -> bool:
        """
        Check if entry has expired based on TTL.

        Returns:
            True if expired, False otherwise
        """
        if self.ttl is None:
            return False

        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl

    def mark_accessed(self) -> None:
        """Update last access time and increment access count."""
        self.last_accessed = datetime.now()
        self.access_count += 1


class CacheMetrics:
    """
    Cache performance tracking and reporting.

    Attributes:
        hits: Number of cache hits
        misses: Number of cache misses
        size: Current cache size
    """

    def __init__(self, hits: int = 0, misses: int = 0, size: int = 0):
        """
        Initialize cache metrics.

        Args:
            hits: Number of cache hits
            misses: Number of cache misses
            size: Current cache size
        """
        self.hits = hits
        self.misses = misses
        self.size = size

    @property
    def hit_rate(self) -> float:
        """
        Calculate cache hit rate as percentage.

        Returns:
            Hit rate percentage (0.0-100.0)
        """
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize metrics to dictionary.

        Returns:
            Dictionary with hits, misses, size, and hit_rate
        """
        return {
            "hits": self.hits,
            "misses": self.misses,
            "size": self.size,
            "hit_rate": round(self.hit_rate, 2),
        }


class ResultCache:
    """
    High-performance LRU cache with TTL expiration.

    Uses cachetools.LRUCache for efficient LRU eviction policy.
    Supports configurable cache size, TTL, and metrics tracking.

    **Thread Safety:** This class is NOT thread-safe. External synchronization
    required for concurrent access (e.g., asyncio.Lock or threading.Lock).

    **Resource Cleanup:** Call close() when done or use as a context manager
    to ensure proper cleanup of cache resources.
    """

    def __init__(self, policy: CachePolicy):
        """
        Initialize result cache with policy.

        Args:
            policy: Cache policy configuration
        """
        self._policy = policy

        # Use LRUCache from cachetools for efficient LRU eviction
        max_size = policy.max_size if policy.max_size is not None else 1000
        self._cache: LRUCache = LRUCache(maxsize=max_size)

        # Track metrics
        self._hits = 0
        self._misses = 0

    @property
    def max_size(self) -> Optional[int]:
        """Get maximum cache size from policy."""
        max_size: Optional[int] = self._policy.max_size
        return max_size

    @property
    def default_ttl(self) -> Optional[int]:
        """Get default TTL from policy."""
        default_ttl: Optional[int] = self._policy.default_ttl
        return default_ttl

    @property
    def eviction_policy(self) -> str:
        """Get eviction policy from policy."""
        eviction_policy: str = self._policy.eviction_policy
        return eviction_policy

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve cached value by key.

        Returns None if key not found or entry expired.
        Updates hit/miss counters and LRU position.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if key not in self._cache:
            self._misses += 1
            return None

        entry: CacheEntry = self._cache[key]

        # Check if expired
        if entry.is_expired():
            # Remove expired entry
            del self._cache[key]
            self._misses += 1
            return None

        # Update access tracking
        entry.mark_accessed()
        self._hits += 1

        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store value in cache with key.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None or 0 uses default TTL)
        """
        # Use default TTL if ttl is None or 0
        effective_ttl = ttl if ttl and ttl > 0 else self.default_ttl

        # Create cache entry
        entry = CacheEntry(value=value, ttl=effective_ttl)

        # Store in LRU cache (will automatically evict LRU item if full)
        self._cache[key] = entry

    def evict_expired(self) -> int:
        """
        Remove all expired entries from cache.

        **Performance:** This operation has O(n) complexity where n is the
        current cache size, as it must iterate through all entries to check
        expiration status.

        **Usage Guidance:**
        - Call periodically in background tasks to prevent expired entry buildup
        - Avoid calling on hot paths or during high-traffic periods
        - Consider calling during idle periods or at scheduled intervals
        - For caches with 1000+ entries, expect 10-50ms execution time

        **Warning:** For large caches (10,000+ entries), this operation may
        take 100ms+ and should be scheduled carefully to avoid blocking.

        Returns:
            Number of entries evicted
        """
        expired_keys = []

        # Find all expired keys
        for key, entry in list(self._cache.items()):
            if entry.is_expired():
                expired_keys.append(key)

        # Remove expired entries
        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def get_metrics(self) -> CacheMetrics:
        """
        Get current cache metrics.

        Returns:
            CacheMetrics with hits, misses, and size
        """
        return CacheMetrics(hits=self._hits, misses=self._misses, size=len(self._cache))

    def clear(self) -> None:
        """Clear all cache entries and reset metrics."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def close(self) -> None:
        """
        Clean up cache resources.

        Clears all cached entries and resets metrics. This method should be
        called when the cache is no longer needed to free resources.

        Safe to call multiple times - subsequent calls are no-ops.
        """
        self.clear()

    def __enter__(self) -> "ResultCache":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Context manager exit - ensures cleanup."""
        self.close()
