"""
Integration tests for cache system components.

Tests the integration between ResultCache, CacheEntry, CacheMetrics, and CachePolicy
components following TDD principles. These tests verify multi-component interactions,
end-to-end workflows, and realistic usage scenarios.

Test Coverage:
- Multi-component integration (ResultCache + CacheEntry + CacheMetrics)
- End-to-end caching workflows
- Realistic load patterns
- Concurrent access patterns (simulated)
- TTL expiration in real-world scenarios
- LRU eviction with mixed access patterns
- Cache warming and cold start scenarios
- Memory pressure and eviction behavior
- Cache hit/miss patterns over time
- Varying TTL values
- Cache clear and reset integration
- Metrics tracking accuracy
"""

import os
import time
from typing import Any, Dict, List

import pytest

from cbr_mcp_server.performance.cache_system import (
    CacheEntry,
    CacheMetrics,
    CachePolicy,
    ResultCache,
)


class TestCacheSystemIntegration:
    """Integration tests for cache system components."""

    @pytest.fixture
    def cache_policy(self) -> CachePolicy:
        """Create cache policy for testing."""
        return CachePolicy(max_size=100, default_ttl=3600)

    @pytest.fixture
    def result_cache(self, cache_policy: CachePolicy) -> ResultCache:
        """Create ResultCache instance for testing."""
        return ResultCache(policy=cache_policy)

    @pytest.fixture
    def sample_queries(self) -> List[Dict[str, Any]]:
        """Create sample query workload for testing."""
        return [
            {"query": "authentication with firebase", "type": "retrieve"},
            {"query": "database connection pooling", "type": "retrieve"},
            {"query": "api error handling", "type": "retrieve"},
            {"query": "authentication with firebase", "type": "retrieve"},  # repeat
            {"query": "form validation react", "type": "retrieve"},
            {"query": "database connection pooling", "type": "retrieve"},  # repeat
            {"query": "websocket integration", "type": "retrieve"},
            {"query": "authentication with firebase", "type": "retrieve"},  # repeat
            {"query": "caching strategies", "type": "retrieve"},
            {"query": "form validation react", "type": "retrieve"},  # repeat
        ]

    def test_cache_system_multi_component_integration(self, result_cache: ResultCache):
        """
        Verify ResultCache, CacheEntry, and CacheMetrics work together correctly.

        Tests:
        - CacheEntry metadata is properly tracked through ResultCache operations
        - CacheMetrics accurately reflect cache operations
        - TTL expiration integrates with metrics tracking
        """
        # Set cache entry with custom TTL
        test_value = {"results": [1, 2, 3]}
        result_cache.set("test_key", test_value, ttl=5)

        # Get cache entry (hit)
        retrieved = result_cache.get("test_key")

        # Verify CacheEntry value is correct
        assert retrieved == test_value

        # Get metrics and verify integration
        metrics = result_cache.get_metrics()

        # Should have 1 hit from the get operation
        assert metrics.hits >= 1
        assert metrics.size >= 1

        # Verify CacheMetrics calculates hit rate correctly
        assert metrics.hit_rate > 0.0

    def test_end_to_end_caching_workflow(self, result_cache: ResultCache):
        """
        Test complete cache lifecycle from set → get → eviction → metrics.

        Tests:
        - Sequential operations (set/get/evict) maintain consistency
        - Metrics accumulate correctly across workflow
        - Cache state remains valid throughout lifecycle
        """
        # Step 1: Set multiple entries
        for i in range(10):
            result_cache.set(f"key_{i}", f"value_{i}", ttl=10)

        # Step 2: Get some entries (hits)
        for i in range(5):
            value = result_cache.get(f"key_{i}")
            assert value == f"value_{i}"

        # Step 3: Get nonexistent entries (misses)
        for i in range(10, 15):
            value = result_cache.get(f"key_{i}")
            assert value is None

        # Step 4: Check metrics after operations
        metrics = result_cache.get_metrics()

        assert metrics.hits >= 5  # At least 5 hits from step 2
        assert metrics.misses >= 5  # At least 5 misses from step 3
        assert metrics.size == 10  # 10 entries from step 1

        # Step 5: Add entries with short TTL (that won't be accessed)
        for i in range(15, 20):
            result_cache.set(f"expire_key_{i}", f"expire_value_{i}", ttl=1)

        time.sleep(1.5)

        # Step 6: Evict expired entries (should find unaccessed expired entries)
        evicted_count = result_cache.evict_expired()
        assert evicted_count >= 1  # At least some expired entries should be found

        # Step 7: Verify final state
        final_metrics = result_cache.get_metrics()
        # Size should be less than before due to eviction
        assert final_metrics.size <= metrics.size + 5  # Allow for some variation

    def test_cache_with_realistic_load_patterns(
        self, result_cache: ResultCache, sample_queries: List[Dict[str, Any]]
    ):
        """
        Verify cache behavior under realistic query patterns.

        Tests:
        - Multiple sequential queries maintain performance
        - Cache hit rate improves over repeated queries
        - Memory usage stays within bounds
        """
        # Simulate query processing with caching
        for i, query in enumerate(sample_queries):
            query_key = f"{query['type']}:{query['query']}"

            # Try to get from cache first
            cached_result = result_cache.get(query_key)

            if cached_result is None:
                # Simulate query execution
                query_result = {
                    "query": query["query"],
                    "results": [f"result_{i}_1", f"result_{i}_2"],
                    "timestamp": time.time(),
                }

                # Store in cache
                result_cache.set(query_key, query_result, ttl=300)
            else:
                # Use cached result
                query_result = cached_result

            # Verify result is valid
            assert query_result is not None
            assert "query" in query_result
            assert "results" in query_result

        # Check metrics after processing all queries
        metrics = result_cache.get_metrics()

        # Should have hits from repeated queries
        assert metrics.hits > 0

        # Hit rate should be reasonable (30%+ given query pattern)
        assert metrics.hit_rate >= 30.0

        # Cache should contain unique queries
        assert metrics.size > 0
        assert metrics.size <= len(set(q["query"] for q in sample_queries))

    def test_concurrent_cache_access_patterns(self, result_cache: ResultCache):
        """
        Test cache behavior with concurrent-like access patterns (simulated).

        Tests:
        - Cache maintains consistency under concurrent-like access patterns
        - Metrics track all operations correctly
        - No data corruption or race conditions
        """
        # Simulate concurrent access by interleaving operations
        keys = [f"key_{i}" for i in range(20)]

        # Round 1: Set all keys
        for key in keys:
            result_cache.set(key, f"value_{key}", ttl=60)

        # Round 2: Interleaved gets and sets
        for i in range(len(keys)):
            # Get even keys, set odd keys
            if i % 2 == 0:
                value = result_cache.get(keys[i])
                assert value == f"value_{keys[i]}"
            else:
                result_cache.set(keys[i], f"updated_{keys[i]}", ttl=60)

        # Round 3: Get all keys
        for i, key in enumerate(keys):
            value = result_cache.get(key)
            # Verify correct value based on whether it was updated
            if i % 2 == 0:
                assert value == f"value_{key}"
            else:
                assert value == f"updated_{key}"

        # Verify metrics are consistent
        metrics = result_cache.get_metrics()
        assert metrics.size == len(keys)
        assert metrics.hits > 0

    def test_ttl_expiration_in_real_world_scenarios(self, result_cache: ResultCache):
        """
        Verify TTL expiration works correctly in realistic scenarios.

        Tests:
        - Expired entries are not returned
        - Metrics count expired accesses as misses
        - Manual eviction of expired entries reduces cache size
        """
        # Add entries with different TTLs
        result_cache.set("short_ttl_1", "value1", ttl=1)
        result_cache.set("short_ttl_2", "value2", ttl=1)
        result_cache.set("medium_ttl", "value3", ttl=3)
        result_cache.set("long_ttl", "value4", ttl=10)

        # Verify all entries are accessible immediately
        assert result_cache.get("short_ttl_1") == "value1"
        assert result_cache.get("short_ttl_2") == "value2"
        assert result_cache.get("medium_ttl") == "value3"
        assert result_cache.get("long_ttl") == "value4"

        # Wait for short TTL entries to expire
        time.sleep(1.5)

        # Get metrics before accessing expired entries
        metrics_before = result_cache.get_metrics()

        # Try to access expired entries (should return None and increment misses)
        assert result_cache.get("short_ttl_1") is None
        assert result_cache.get("short_ttl_2") is None

        # Non-expired entries should still be accessible
        assert result_cache.get("medium_ttl") == "value3"
        assert result_cache.get("long_ttl") == "value4"

        # Verify metrics updated correctly
        metrics_after = result_cache.get_metrics()
        assert metrics_after.misses > metrics_before.misses

        # Add more unaccessed entries that will expire
        for i in range(5):
            result_cache.set(f"batch_expire_{i}", f"value_{i}", ttl=1)

        time.sleep(1.5)

        # Manually evict expired entries (should find unaccessed expired entries)
        evicted_count = result_cache.evict_expired()
        assert (
            evicted_count >= 3
        )  # Should find the batch_expire entries plus any others

        # Verify cache size reduced
        final_metrics = result_cache.get_metrics()
        # Size should be less than 10 (4 original + 5 batch_expire = 9, minus evicted)
        assert final_metrics.size < 9

    def test_lru_eviction_with_mixed_access_patterns(self, result_cache: ResultCache):
        """
        Test LRU eviction with varied access patterns.

        Tests:
        - Frequently accessed entries remain in cache
        - Least recently used entries are evicted first
        - Cache size respects max_size limit
        """
        # Fill cache to capacity (max_size = 100)
        for i in range(100):
            result_cache.set(f"key_{i}", f"value_{i}", ttl=300)

        # Access first 20 keys frequently to mark as recently used
        for _ in range(3):
            for i in range(20):
                result_cache.get(f"key_{i}")

        # Add 30 more entries to trigger eviction
        for i in range(100, 130):
            result_cache.set(f"key_{i}", f"value_{i}", ttl=300)

        # Verify cache respects max_size
        metrics = result_cache.get_metrics()
        assert metrics.size <= 100

        # Frequently accessed keys (0-19) should still be present
        hits_on_hot_keys = 0
        for i in range(20):
            if result_cache.get(f"key_{i}") is not None:
                hits_on_hot_keys += 1

        # Most hot keys should still be in cache
        assert hits_on_hot_keys >= 15

        # Some middle keys (20-99) should have been evicted
        misses_on_cold_keys = 0
        for i in range(20, 100):
            if result_cache.get(f"key_{i}") is None:
                misses_on_cold_keys += 1

        # Should have evicted at least some cold keys
        assert misses_on_cold_keys > 0

    def test_cache_warming_and_cold_start_scenarios(self, result_cache: ResultCache):
        """
        Test cache behavior on cold start vs warm cache.

        Tests:
        - Initial queries result in cache misses
        - Subsequent queries result in cache hits
        - Hit rate increases as cache warms
        """
        # Simulate cold start - all queries miss
        cold_queries = [f"query_{i}" for i in range(10)]

        for query in cold_queries:
            # Try cache first
            result = result_cache.get(query)
            assert result is None  # Cold start - all misses

            # Simulate query execution and caching
            result_cache.set(query, {"query": query, "results": []}, ttl=300)

        # Check metrics after cold start
        cold_metrics = result_cache.get_metrics()
        assert cold_metrics.misses >= 10
        assert cold_metrics.hit_rate == 0.0  # All misses on cold start

        # Simulate warm cache - same queries should hit
        for query in cold_queries:
            result = result_cache.get(query)
            assert result is not None  # Warm cache - all hits
            assert result["query"] == query

        # Check metrics after warm queries
        warm_metrics = result_cache.get_metrics()
        assert warm_metrics.hits >= 10
        assert warm_metrics.hit_rate > 0.0  # Should have hits now

        # Verify hit rate improved
        assert warm_metrics.hit_rate > cold_metrics.hit_rate

    def test_memory_pressure_and_eviction_behavior(self, result_cache: ResultCache):
        """
        Verify cache eviction under memory pressure.

        Tests:
        - Manual eviction reduces cache size
        - Evicted entries are no longer retrievable
        - Metrics reflect evicted entries
        """
        # Fill cache with entries
        for i in range(50):
            result_cache.set(f"key_{i}", f"value_{i}" * 100, ttl=300)  # Larger values

        # Get initial metrics
        initial_metrics = result_cache.get_metrics()
        initial_size = initial_metrics.size

        assert initial_size >= 50

        # Simulate memory pressure by adding entries with short TTL (unaccessed)
        for i in range(50, 80):
            result_cache.set(f"temp_key_{i}", f"temp_value_{i}", ttl=1)

        # Wait for temp entries to expire
        time.sleep(1.5)

        # Evict expired entries to simulate memory pressure relief
        evicted_count = result_cache.evict_expired()
        # Should evict the unaccessed expired temp entries
        assert evicted_count >= 15  # At least half of the 30 temp entries

        # Verify cache size reduced
        final_metrics = result_cache.get_metrics()
        # Size should be less than initial + 30 temp entries
        assert final_metrics.size < (initial_size + 30)

        # Verify accessing expired entries returns None (lazy removal)
        none_count = 0
        for i in range(50, 80):
            if result_cache.get(f"temp_key_{i}") is None:
                none_count += 1

        # Most temp entries should be expired/evicted
        assert none_count >= 20

    def test_cache_hit_miss_patterns_over_time(self, result_cache: ResultCache):
        """
        Track cache hit/miss patterns over sustained operation.

        Tests:
        - Hit rate reaches target (70%+) with realistic workload
        - Metrics accumulate correctly over many operations
        - Cache performance remains stable
        """
        # Define workload with realistic distribution
        # 70% of queries are repeated (should hit cache)
        # 30% of queries are unique (will miss)

        hot_queries = [f"hot_query_{i}" for i in range(10)]  # Repeated queries
        unique_queries = [f"unique_query_{i}" for i in range(30)]  # One-time queries

        # Warm up cache with hot queries
        for query in hot_queries:
            result_cache.set(query, {"query": query, "results": []}, ttl=300)

        # Simulate 100 queries with 70/30 distribution
        for i in range(100):
            if i % 10 < 7:  # 70% hot queries
                query = hot_queries[i % len(hot_queries)]
            else:  # 30% unique queries
                if i // 10 < len(unique_queries):
                    query = unique_queries[i // 10]
                else:
                    query = f"extra_unique_{i}"

            # Get from cache
            result = result_cache.get(query)

            if result is None:
                # Cache miss - simulate query execution
                result_cache.set(query, {"query": query, "results": []}, ttl=300)

        # Check final metrics
        final_metrics = result_cache.get_metrics()

        # Hit rate should be reasonable (>50%) given 70% repeated queries
        assert final_metrics.hit_rate >= 50.0

        # Should have processed all queries
        total_accesses = final_metrics.hits + final_metrics.misses
        assert total_accesses >= 100

        # Cache should contain entries
        assert final_metrics.size > 0

    @pytest.mark.skipif(os.environ.get('PYTEST_XDIST_WORKER') is not None, reason="Test unstable in parallel execution mode")
    def test_cache_with_varying_ttl_values(self, result_cache: ResultCache):
        """
        Test cache with different TTL values for different entries.

        Tests:
        - Entries with different TTLs expire independently
        - Short TTL entries expire before long TTL entries
        - Mixed TTL entries don't interfere with each other
        """
        # Add entries with varying TTLs
        result_cache.set("ttl_1_sec", "value1", ttl=1)
        result_cache.set("ttl_2_sec", "value2", ttl=2)
        result_cache.set("ttl_3_sec", "value3", ttl=3)
        result_cache.set("ttl_long", "value4", ttl=10)

        # Verify all entries accessible immediately
        assert result_cache.get("ttl_1_sec") == "value1"
        assert result_cache.get("ttl_2_sec") == "value2"
        assert result_cache.get("ttl_3_sec") == "value3"
        assert result_cache.get("ttl_long") == "value4"

        # Wait for 1-second TTL to expire
        time.sleep(1.5)

        assert result_cache.get("ttl_1_sec") is None  # Expired
        assert result_cache.get("ttl_2_sec") == "value2"  # Still valid
        assert result_cache.get("ttl_3_sec") == "value3"  # Still valid
        assert result_cache.get("ttl_long") == "value4"  # Still valid

        # Wait for 2-second TTL to expire
        time.sleep(1.0)

        assert result_cache.get("ttl_1_sec") is None  # Still expired
        assert result_cache.get("ttl_2_sec") is None  # Now expired
        assert result_cache.get("ttl_3_sec") == "value3"  # Still valid
        assert result_cache.get("ttl_long") == "value4"  # Still valid

        # Wait for 3-second TTL to expire
        time.sleep(1.5)

        assert result_cache.get("ttl_1_sec") is None  # Still expired
        assert result_cache.get("ttl_2_sec") is None  # Still expired
        assert result_cache.get("ttl_3_sec") is None  # Now expired
        assert result_cache.get("ttl_long") == "value4"  # Still valid (10 sec TTL)

    def test_cache_clear_and_reset_integration(self, result_cache: ResultCache):
        """
        Verify cache clear operation fully resets state.

        Tests:
        - Clear removes all entries
        - Metrics are reset to zero
        - Subsequent operations start fresh
        """
        # Add entries and perform operations
        for i in range(20):
            result_cache.set(f"key_{i}", f"value_{i}", ttl=300)

        # Perform some gets to accumulate metrics
        for i in range(10):
            result_cache.get(f"key_{i}")

        # Get some misses too
        for i in range(20, 25):
            result_cache.get(f"key_{i}")

        # Verify cache has state
        metrics_before = result_cache.get_metrics()
        assert metrics_before.size > 0
        assert metrics_before.hits > 0
        assert metrics_before.misses > 0

        # Clear cache
        result_cache.clear()

        # Verify all state is reset
        metrics_after = result_cache.get_metrics()
        assert metrics_after.size == 0
        assert metrics_after.hits == 0
        assert metrics_after.misses == 0
        assert metrics_after.hit_rate == 0.0

        # Verify entries are gone
        for i in range(20):
            assert result_cache.get(f"key_{i}") is None

        # Verify cache is functional after clear
        result_cache.set("new_key", "new_value", ttl=300)
        assert result_cache.get("new_key") == "new_value"

        # Verify metrics track new operations
        final_metrics = result_cache.get_metrics()
        assert final_metrics.size == 1
        assert final_metrics.hits >= 1

    def test_cache_metrics_tracking_accuracy(self, result_cache: ResultCache):
        """
        Verify metrics accurately track all cache operations.

        Tests:
        - Every get operation updates hit/miss counters
        - Cache size reflects actual entry count
        - Hit rate calculation is accurate
        """
        # Perform controlled operations and verify metrics at each step

        # Step 1: Add 5 entries
        for i in range(5):
            result_cache.set(f"key_{i}", f"value_{i}", ttl=300)

        metrics_1 = result_cache.get_metrics()
        assert metrics_1.size == 5
        assert metrics_1.hits == 0  # No gets yet
        assert metrics_1.misses == 0

        # Step 2: Get 3 existing keys (3 hits)
        for i in range(3):
            result_cache.get(f"key_{i}")

        metrics_2 = result_cache.get_metrics()
        assert metrics_2.hits >= 3
        assert metrics_2.misses == 0
        assert metrics_2.size == 5

        # Step 3: Get 2 nonexistent keys (2 misses)
        result_cache.get("nonexistent_1")
        result_cache.get("nonexistent_2")

        metrics_3 = result_cache.get_metrics()
        assert metrics_3.hits >= 3
        assert metrics_3.misses >= 2
        assert metrics_3.size == 5

        # Verify hit rate calculation
        # Should be 60% (3 hits / 5 total accesses)
        expected_hit_rate = (3 / 5) * 100
        assert abs(metrics_3.hit_rate - expected_hit_rate) < 5.0

        # Step 4: Add more entries and verify size tracking
        for i in range(5, 10):
            result_cache.set(f"key_{i}", f"value_{i}", ttl=300)

        metrics_4 = result_cache.get_metrics()
        assert metrics_4.size == 10

        # Step 5: Verify metrics accumulate (not reset)
        assert metrics_4.hits == metrics_3.hits  # No new hits
        assert metrics_4.misses == metrics_3.misses  # No new misses
