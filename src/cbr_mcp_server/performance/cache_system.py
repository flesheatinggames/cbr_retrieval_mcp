"""
Cache system for performance optimization.

This module provides:
- CacheEntry: Individual cache entries with TTL and access tracking
- CacheMetrics: Cache performance metrics
- ResultCache: LRU cache with TTL expiration
- CachePolicy: Configuration for cache behavior (re-exported from data_models)

**Thread Safety:**
ResultCache is thread-safe for concurrent access. All cache operations are
protected by an internal threading.RLock, ensuring safe concurrent reads and
writes from multiple threads.
"""

import threading
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple, Type

from cachetools import LRUCache

from cbr_mcp_server.performance.data_models import CachePolicy

# Re-export CachePolicy for convenience
__all__ = ["CacheEntry", "CacheMetrics", "ResultCache", "CachePolicy", "CacheConfig"]


class CacheConfig(CachePolicy):
    """
    Backward compatibility alias for CachePolicy with alternative parameter names.

    This class allows using 'ttl_seconds' instead of 'default_ttl' for test compatibility.

    Usage:
        config = CacheConfig(max_size=100, ttl_seconds=3600)
        # Equivalent to:
        # config = CachePolicy(max_size=100, default_ttl=3600)
    """

    def __init__(
        self,
        max_size: Optional[int] = 1000,
        ttl_seconds: Optional[int] = None,
        eviction_policy: str = "LRU",
        **kwargs
    ):
        """
        Initialize CacheConfig with backward-compatible parameter names.

        Args:
            max_size: Maximum cache entries (None for unlimited)
            ttl_seconds: TTL in seconds (alias for default_ttl)
            eviction_policy: Eviction strategy ("LRU" or "FIFO")
            **kwargs: Additional arguments passed to CachePolicy
        """
        # Map ttl_seconds to default_ttl
        default_ttl = ttl_seconds if ttl_seconds is not None else kwargs.get('default_ttl', 3600)

        # Remove default_ttl from kwargs if present (we're setting it explicitly)
        kwargs.pop('default_ttl', None)

        super().__init__(
            max_size=max_size,
            default_ttl=default_ttl,
            eviction_policy=eviction_policy,
            **kwargs
        )


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

    **Expiration Strategy:**
    This cache uses lazy expiration as the primary expiration mechanism.
    Expired entries are automatically removed when accessed via get(),
    providing O(1) expiration checks without periodic O(n) scans.

    The evict_expired() method is provided for background cleanup tasks
    only and should NEVER be called in request handling paths due to
    its O(n) complexity.

    **Thread Safety:** This class is thread-safe for concurrent access.
    All cache operations are protected by an internal threading.RLock,
    ensuring safe concurrent reads and writes from multiple threads.

    **Resource Cleanup:** Call close() when done or use as a context manager
    to ensure proper cleanup of cache resources.
    """

    def __init__(self, policy: Optional[CachePolicy] = None, config: Optional[CachePolicy] = None):
        """
        Initialize result cache with policy.

        Args:
            policy: Cache policy configuration (preferred parameter name)
            config: Cache policy configuration (backward compatibility alias for 'policy')

        Raises:
            ValueError: If neither policy nor config is provided
        """
        # Support both 'policy' and 'config' parameter names for backward compatibility
        if policy is None and config is None:
            raise ValueError("Either 'policy' or 'config' parameter must be provided")

        self._policy = policy if policy is not None else config

        # Use LRUCache from cachetools for efficient LRU eviction
        max_size = self._policy.max_size if self._policy.max_size is not None else 1000
        self._cache: LRUCache = LRUCache(maxsize=max_size)

        # Track metrics
        self._hits = 0
        self._misses = 0

        # Thread safety lock
        self._lock = threading.RLock()

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
        Retrieve cached value by key with lazy expiration.

        Returns None if key not found or entry expired.
        Updates hit/miss counters and LRU position.

        **Lazy Expiration:** This method automatically removes expired entries
        when accessed, providing O(1) expiration checks. This is the primary
        expiration mechanism and eliminates the need for periodic O(n) scans
        in most use cases.

        Thread-safe: Protected by internal RLock.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
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

        Thread-safe: Protected by internal RLock.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None or 0 uses default TTL)
        """
        with self._lock:
            # Use default TTL if ttl is None or 0
            effective_ttl = ttl if ttl and ttl > 0 else self.default_ttl

            # Create cache entry
            entry = CacheEntry(value=value, ttl=effective_ttl)

            # Store in LRU cache (will automatically evict LRU item if full)
            self._cache[key] = entry

    def evict_expired(self) -> int:
        """
        Remove all expired entries from cache.

        ⚠️  **CRITICAL WARNING: DO NOT CALL IN REQUEST PATH** ⚠️

        This method performs an O(n) scan of all cache entries and will cause
        latency spikes (100ms+ for 10,000+ entries). It MUST ONLY be called by
        background cleanup tasks, never during request handling.

        **Preferred Approach:**
        This cache uses LAZY EXPIRATION - expired entries are automatically
        removed when accessed via get() with O(1) complexity. This is the
        primary expiration mechanism and should handle most use cases.

        **When to Use This Method:**
        - Periodic background cleanup (e.g., every 5-10 minutes)
        - During system idle periods
        - When cache memory usage needs to be minimized
        - NEVER in response to user requests or API calls

        **Thread Safety:** Protected by internal RLock.

        **Performance Characteristics:**
        - O(n) complexity where n is current cache size
        - ~1ms per 100 entries (10ms for 1000, 100ms for 10,000)
        - Blocks all cache access during execution
        - May violate <200ms latency targets if called in hot path

        Returns:
            Number of entries evicted
        """
        with self._lock:
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

        Thread-safe: Protected by internal RLock.

        Returns:
            CacheMetrics object with hits, misses, size, and hit_rate
        """
        with self._lock:
            metrics = CacheMetrics(hits=self._hits, misses=self._misses, size=len(self._cache))
            return metrics

    def clear(self) -> None:
        """
        Clear all cache entries and reset metrics.

        Thread-safe: Protected by internal RLock.
        """
        with self._lock:
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
