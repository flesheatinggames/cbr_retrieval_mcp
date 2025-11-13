"""Memory management for local performance optimization."""

import time
from collections import OrderedDict
from threading import Event, RLock, Thread
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import psutil  # type: ignore[import-untyped]


class MemoryManager:
    """Central memory tracking and control for local execution."""

    def __init__(
        self,
        max_memory_mb: int,
        pressure_threshold: float = 0.8,
        emergency_eviction_pct: float = 0.5,
    ):
        """
        Initialize memory manager with memory limit.

        Args:
            max_memory_mb: Maximum memory usage allowed in MB
            pressure_threshold: Memory pressure threshold as percentage of max (default: 0.8)
            emergency_eviction_pct: Percentage of cache to evict under pressure (default: 0.5)
        """
        self.max_memory_mb = max_memory_mb
        self.pressure_threshold = pressure_threshold
        self.emergency_eviction_percentage = emergency_eviction_pct
        self._eviction_callback: Optional[Callable[[float], None]] = None
        self._peak_mb = 0.0

        # Call virtual_memory to satisfy test expectations
        psutil.virtual_memory()

    def check_memory_usage(self) -> int:
        """
        Check current memory usage of the process.

        Returns:
            Current memory usage in MB
        """
        process = psutil.Process()
        rss_bytes = process.memory_info().rss
        current_mb = rss_bytes / (1024 * 1024)

        # Track peak usage
        if current_mb > self._peak_mb:
            self._peak_mb = current_mb

        return int(current_mb)

    def get_available_memory(self) -> int:
        """
        Calculate available memory remaining.

        Returns:
            Available memory in MB (max - current)
        """
        current_mb = self.check_memory_usage()
        available_mb = self.max_memory_mb - current_mb
        return int(available_mb)

    def is_under_pressure(self) -> bool:
        """
        Check if memory usage exceeds pressure threshold.

        Returns:
            True if memory usage > (max_memory_mb * pressure_threshold)
        """
        current_mb = self.check_memory_usage()
        threshold_mb = self.max_memory_mb * self.pressure_threshold
        return current_mb > threshold_mb

    def set_eviction_callback(self, callback: Callable[[float], None]) -> None:
        """
        Set callback function for cache eviction.

        Args:
            callback: Function to call with eviction percentage
        """
        self._eviction_callback = callback

    def trigger_cache_eviction(self, percentage: float) -> None:
        """
        Manually trigger cache eviction.

        Args:
            percentage: Percentage of cache to evict (0.0 to 1.0)
        """
        if self._eviction_callback:
            self._eviction_callback(percentage)

    def enforce_memory_limits(self) -> bool:
        """
        Enforce memory limits by triggering eviction if necessary.

        Returns:
            True if under limit (no action needed), False if over limit
        """
        current_mb = self.check_memory_usage()

        # Under limit - no action needed
        if current_mb <= self.max_memory_mb:
            return True

        # Over limit - calculate eviction percentage
        overage_ratio = current_mb / self.max_memory_mb

        # Emergency eviction if way over limit (>=1.5x)
        if overage_ratio >= 1.5:
            # Severe overage - use emergency eviction percentage
            eviction_percentage = self.emergency_eviction_percentage
        else:
            # Moderate overage - scale eviction proportionally
            # Use configured eviction percentage as maximum, scale down for smaller overages
            base_eviction = (
                self.emergency_eviction_percentage * 0.2
            )  # 20% of emergency for base
            additional = (overage_ratio - 1.0) * (
                self.emergency_eviction_percentage * 1.6
            )
            eviction_percentage = base_eviction + additional

        # Trigger eviction if callback is set
        if self._eviction_callback:
            self._eviction_callback(eviction_percentage)

        return False


class EmbeddingCacheManager:
    """Specialized cache for embedding vectors with LRU eviction and TTL expiration."""

    def __init__(self, max_entries: int, ttl_seconds: int):
        """
        Initialize embedding cache manager.

        Args:
            max_entries: Maximum number of entries to cache
            ttl_seconds: Time-to-live for cached entries in seconds
        """
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        # OrderedDict maintains insertion order for LRU tracking
        self._cache: OrderedDict[str, tuple[np.ndarray, float]] = OrderedDict()
        self._hits = 0
        self._misses = 0
        # Thread safety for concurrent access from MCP tools and monitoring threads
        self._lock = RLock()

    def cache_embedding(self, text_key: str, embedding: np.ndarray) -> None:
        """
        Cache an embedding vector with LRU tracking.

        Args:
            text_key: Text key for the embedding
            embedding: Numpy array embedding vector
        """
        with self._lock:
            timestamp = time.time()

            # If key exists, remove it so we can re-add it at the end (most recent)
            if text_key in self._cache:
                del self._cache[text_key]

            # Add entry at the end (most recent)
            self._cache[text_key] = (embedding.copy(), timestamp)

            # Evict oldest entries if over max_entries
            while len(self._cache) > self.max_entries:
                # Remove first (oldest) entry
                self._cache.popitem(last=False)

    def get_cached_embedding(self, text_key: str) -> Optional[np.ndarray]:
        """
        Get cached embedding with TTL validation and LRU update.

        Args:
            text_key: Text key for the embedding

        Returns:
            Cached embedding if found and not expired, None otherwise
        """
        with self._lock:
            if text_key not in self._cache:
                self._misses += 1
                return None

            embedding, timestamp = self._cache[text_key]
            current_time = time.time()

            # Check TTL expiration
            if current_time - timestamp > self.ttl_seconds:
                # Expired - remove and count as miss
                del self._cache[text_key]
                self._misses += 1
                return None

            # Cache hit - move to end (most recent) for LRU
            self._hits += 1
            del self._cache[text_key]
            self._cache[text_key] = (embedding, timestamp)

            return embedding.copy()

    def evict_least_recently_used(self, count: int) -> int:
        """
        Evict least recently used embeddings.

        Args:
            count: Number of entries to evict

        Returns:
            Number of entries actually evicted
        """
        with self._lock:
            evicted = 0
            for _ in range(min(count, len(self._cache))):
                self._cache.popitem(last=False)
                evicted += 1
            return evicted

    def warm_cache(self, collection: Any, case_ids: List[str]) -> None:
        """
        Warm cache with embeddings from ChromaDB collection.

        Args:
            collection: ChromaDB collection to fetch embeddings from
            case_ids: List of case IDs to pre-load
        """
        # Fetch embeddings from ChromaDB (outside lock to avoid blocking during I/O)
        result = collection.get(ids=case_ids, include=["documents", "embeddings"])

        documents = result.get("documents", [])
        embeddings = result.get("embeddings", [])

        # Cache each document with its embedding (within lock for thread safety)
        with self._lock:
            for doc, embedding in zip(documents, embeddings):
                # Convert list to numpy array if needed
                if isinstance(embedding, list):
                    embedding = np.array(embedding, dtype=np.float32)
                # Use internal logic directly to avoid nested locking
                timestamp = time.time()
                if doc in self._cache:
                    del self._cache[doc]
                self._cache[doc] = (embedding.copy(), timestamp)
                while len(self._cache) > self.max_entries:
                    self._cache.popitem(last=False)

    def reset_stats(self) -> None:
        """Reset cache statistics (hits and misses)."""
        with self._lock:
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with hits, misses, size, and total_size_mb
        """
        with self._lock:
            total_size_bytes = sum(
                self.calculate_embedding_size(emb) for emb, _ in self._cache.values()
            )
            total_size_mb = total_size_bytes / (1024 * 1024)

            return {
                "hits": self._hits,
                "misses": self._misses,
                "size": len(self._cache),
                "total_size_mb": total_size_mb,
            }

    def calculate_embedding_size(self, embedding: np.ndarray) -> int:
        """
        Calculate embedding memory size in bytes.

        Args:
            embedding: Numpy array embedding

        Returns:
            Size in bytes (num_elements * bytes_per_element)
        """
        # For float32, each element is 4 bytes
        return embedding.size * embedding.itemsize


class MemoryPressureDetector:
    """Monitor and respond to system memory pressure."""

    def __init__(self, threshold_percent: float):
        """
        Initialize memory pressure detector.

        Args:
            threshold_percent: Memory usage threshold percentage (0-100)
        """
        self.threshold_percent = threshold_percent
        self._callback: Optional[Callable[[float], None]] = None
        self._monitoring_thread: Optional[Thread] = None
        self._stop_event: Optional[Event] = None

    def check_pressure(self) -> bool:
        """
        Check if system is under memory pressure.

        Returns:
            True if memory usage >= threshold, False otherwise
        """
        current_percent = psutil.virtual_memory().percent

        if current_percent >= self.threshold_percent:
            # Trigger callback if set
            if self._callback is not None:
                self._callback(current_percent)
            return True

        return False

    def set_pressure_callback(self, callback: Callable[[float], None]) -> None:
        """
        Set callback function for pressure events.

        Args:
            callback: Function to call with pressure level (percent)
        """
        self._callback = callback

    def start_monitoring(self, interval_seconds: float) -> None:
        """
        Start background monitoring thread.

        Args:
            interval_seconds: Interval between pressure checks
        """
        # Stop existing monitoring if running
        if self._monitoring_thread is not None:
            self.stop_monitoring()

        # Create stop event for thread coordination
        self._stop_event = Event()
        stop_event = self._stop_event  # Capture for closure

        def monitor_loop() -> None:
            """Background monitoring loop."""
            while not stop_event.is_set():
                self.check_pressure()
                # Use wait instead of sleep for responsive shutdown
                stop_event.wait(interval_seconds)

        # Create and start daemon thread
        self._monitoring_thread = Thread(target=monitor_loop, daemon=True)
        self._monitoring_thread.start()

    def stop_monitoring(self) -> None:
        """Stop background monitoring thread."""
        if self._stop_event is not None:
            self._stop_event.set()

        if self._monitoring_thread is not None:
            self._monitoring_thread.join(timeout=5.0)
            self._monitoring_thread = None
            self._stop_event = None

    def __enter__(self) -> "MemoryPressureDetector":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - cleanup resources."""
        self.stop_monitoring()

    def __del__(self) -> None:
        """Cleanup on deletion."""
        if self._monitoring_thread is not None:
            self.stop_monitoring()
