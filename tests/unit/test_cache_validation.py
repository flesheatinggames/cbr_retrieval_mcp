"""
Unit tests to validate cache system functionality.

This test suite verifies that the cache system works correctly in isolation,
ensuring that the 0% cache hit rate issue has been resolved.
"""

import pytest
from cbr_mcp_server.performance.cache_system import CachePolicy, ResultCache


class TestCacheBasicFunctionality:
    """Test basic cache operations."""

    def test_cache_set_and_get(self):
        """Verify basic cache set/get operations work."""
        policy = CachePolicy(max_size=100, default_ttl=3600, eviction_policy="LRU")
        cache = ResultCache(policy=policy)

        # Set a value
        cache.set("test_key", {"data": "test_value"})

        # Get the value
        result = cache.get("test_key")

        assert result == {"data": "test_value"}

    def test_cache_hit_rate_tracking(self):
        """Verify cache hit/miss tracking works correctly."""
        policy = CachePolicy(max_size=100, default_ttl=3600, eviction_policy="LRU")
        cache = ResultCache(policy=policy)

        # First access - miss
        result1 = cache.get("key1")
        assert result1 is None

        # Set value
        cache.set("key1", {"value": 1})

        # Second access - hit
        result2 = cache.get("key1")
        assert result2 == {"value": 1}

        # Check metrics
        metrics = cache.get_metrics()
        assert metrics.hits == 1
        assert metrics.misses == 1
        assert metrics.hit_rate == 50.0  # 1 hit out of 2 total accesses

    def test_repeated_queries_cache_effectiveness(self):
        """Verify cache provides high hit rate for repeated queries."""
        policy = CachePolicy(max_size=100, default_ttl=3600, eviction_policy="LRU")
        cache = ResultCache(policy=policy)

        query = "test query"
        value = {"results": [1, 2, 3]}

        # First access - miss
        cache.set(query, value)

        # Simulate 10 repeated accesses
        for _ in range(10):
            result = cache.get(query)
            assert result == value

        # Check hit rate
        metrics = cache.get_metrics()
        assert metrics.hits == 10
        assert metrics.misses == 0
        assert metrics.hit_rate == 100.0

    def test_cache_key_consistency(self):
        """Verify same query generates consistent cache key."""
        policy = CachePolicy(max_size=100, default_ttl=3600, eviction_policy="LRU")
        cache = ResultCache(policy=policy)

        # Store with one key
        cache.set("identical_query", {"data": "first"})

        # Retrieve with same key
        result = cache.get("identical_query")

        assert result == {"data": "first"}

        # Verify cache hit
        metrics = cache.get_metrics()
        assert metrics.hit_rate == 100.0


class TestCacheIntegration:
    """Test cache integration with query patterns."""

    def test_cache_with_multiple_queries(self):
        """Verify cache works with multiple different queries."""
        policy = CachePolicy(max_size=100, default_ttl=3600, eviction_policy="LRU")
        cache = ResultCache(policy=policy)

        # Store multiple queries
        queries = ["query1", "query2", "query3"]
        for i, query in enumerate(queries):
            cache.set(query, {"result": i})

        # Retrieve all queries (should all hit)
        for i, query in enumerate(queries):
            result = cache.get(query)
            assert result == {"result": i}

        # Verify hit rate
        metrics = cache.get_metrics()
        assert metrics.hits == 3
        assert metrics.hit_rate == 100.0

    def test_cache_warmup_pattern(self):
        """Verify cache warmup pattern achieves high hit rate."""
        policy = CachePolicy(max_size=100, default_ttl=3600, eviction_policy="LRU")
        cache = ResultCache(policy=policy)

        warmup_queries = ["query1", "query2", "query3", "query4", "query5"]

        # Warmup phase - populate cache
        for query in warmup_queries:
            cache.set(query, {"data": query})

        # Reset metrics to measure only post-warmup
        cache.clear()
        for query in warmup_queries:
            cache.set(query, {"data": query})

        # Clear hit/miss counters by creating new cache with same data
        # Simulates post-warmup steady state
        hits = 0
        for _ in range(15):  # 15 iterations
            for query in warmup_queries:
                result = cache.get(query)
                if result is not None:
                    hits += 1

        # After warmup, all queries should hit
        total = 15 * len(warmup_queries)
        hit_rate = (hits / total) * 100
        assert hit_rate == 100.0  # Should achieve 100% hit rate

    def test_cache_size_limits(self):
        """Verify cache respects size limits with LRU eviction."""
        policy = CachePolicy(max_size=3, default_ttl=3600, eviction_policy="LRU")
        cache = ResultCache(policy=policy)

        # Fill cache to capacity
        cache.set("key1", {"data": 1})
        cache.set("key2", {"data": 2})
        cache.set("key3", {"data": 3})

        # Add one more - should evict LRU (key1)
        cache.set("key4", {"data": 4})

        # key1 should be evicted
        result1 = cache.get("key1")
        assert result1 is None

        # Other keys should still be present
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None
        assert cache.get("key4") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
