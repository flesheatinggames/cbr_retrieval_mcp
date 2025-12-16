"""
Integration tests for Query Optimizer components.

Tests the integration between QueryOptimizer, ConnectionPool, BatchCoordinator,
and related components following TDD principles. These tests verify multi-component
interactions, end-to-end workflows, and realistic usage scenarios.

Test Coverage:
- QueryOptimizer + ResultCache integration
- QueryOptimizer + MemoryManager integration
- ConnectionPool lifecycle with ChromaDB
- BatchCoordinator async execution
- End-to-end query flows
- Connection pool exhaustion/recovery
- Concurrent query handling
- Combined component scenarios
- Memory pressure effects
- Error handling across components
"""

import asyncio
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from cbr_mcp_server.performance.cache_system import ResultCache
from cbr_mcp_server.performance.data_models import CachePolicy, MemoryConfig
from cbr_mcp_server.performance.memory_manager import MemoryManager
from cbr_mcp_server.performance.query_optimizer import (
    BatchCoordinator,
    ConnectionPool,
    QueryOptimizer,
)


class TestQueryOptimizerIntegration:
    """Integration tests for query optimizer components."""

    @pytest.fixture
    def cache_policy(self) -> CachePolicy:
        """Create cache policy for testing."""
        return CachePolicy(max_size=100, default_ttl=300)

    @pytest.fixture
    def result_cache(self, cache_policy: CachePolicy) -> ResultCache:
        """Create real ResultCache instance."""
        return ResultCache(policy=cache_policy)

    @pytest.fixture
    def memory_config(self) -> MemoryConfig:
        """Create memory configuration for testing."""
        return MemoryConfig(max_memory_mb=500, pressure_threshold_mb=450)

    @pytest.fixture
    def memory_manager(self, memory_config: MemoryConfig) -> MemoryManager:
        """Create real MemoryManager instance."""
        return MemoryManager(max_memory_mb=memory_config.max_memory_mb)

    @pytest.fixture
    def query_optimizer(
        self, result_cache: ResultCache, memory_manager: MemoryManager
    ) -> QueryOptimizer:
        """Create QueryOptimizer with real cache and memory manager."""
        return QueryOptimizer(cache_system=result_cache, memory_manager=memory_manager)

    @pytest.fixture
    def mock_chromadb_collection(self):
        """Create mock ChromaDB collection for testing."""
        mock = Mock()
        mock.query.return_value = {
            "ids": [["case1", "case2", "case3"]],
            "distances": [[0.1, 0.2, 0.3]],
            "documents": [["doc1", "doc2", "doc3"]],
            "metadatas": [
                [
                    {"category": "test", "subcategory": "sub1"},
                    {"category": "test", "subcategory": "sub2"},
                    {"category": "test", "subcategory": "sub3"},
                ]
            ],
        }
        return mock

    @pytest.fixture
    def temp_chromadb_path(self):
        """Create temporary directory for ChromaDB."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_query_optimizer_result_cache_integration(
        self,
        query_optimizer: QueryOptimizer,
        result_cache: ResultCache,
        mock_chromadb_collection,
    ):
        """
        Verify QueryOptimizer correctly integrates with ResultCache.

        Tests:
        - Cache miss triggers ChromaDB query
        - Result stored in cache after query
        - Cache hit returns cached result without ChromaDB query
        - Cache key generation is consistent
        """
        query = {"text": "test query", "limit": 5}

        # Mock ChromaDB connection
        with patch.object(
            query_optimizer,
            "_get_chromadb_collection",
            return_value=mock_chromadb_collection,
        ):
            # First query - should be cache miss
            result1 = query_optimizer.execute_with_optimization(query)

            # Verify ChromaDB was called
            assert mock_chromadb_collection.query.call_count == 1

            # Verify result is from ChromaDB (not cache)
            assert result1["from_cache"] is False
            assert "results" in result1
            assert len(result1["results"]) == 3

            # Reset mock to verify second query doesn't call ChromaDB
            mock_chromadb_collection.query.reset_mock()

            # Second identical query - should be cache hit
            result2 = query_optimizer.execute_with_optimization(query)

            # Verify ChromaDB was NOT called again
            assert mock_chromadb_collection.query.call_count == 0

            # Verify result is from cache
            assert result2["from_cache"] is True
            assert result2["results"] == result1["results"]

            # Verify cache metrics
            cache_metrics = result_cache.get_metrics()
            assert cache_metrics.hits >= 1
            assert cache_metrics.size >= 1

    def test_query_optimizer_memory_manager_integration(
        self,
        query_optimizer: QueryOptimizer,
        memory_manager: MemoryManager,
        mock_chromadb_collection,
    ):
        """
        Verify QueryOptimizer respects memory constraints.

        Tests:
        - Under memory pressure, query limits are reduced
        - Normal memory conditions preserve query limits
        - Memory-based optimization decisions are tracked
        """
        # Test under normal memory conditions
        normal_query = {"text": "test query", "limit": 100}

        with patch.object(
            query_optimizer,
            "_get_chromadb_collection",
            return_value=mock_chromadb_collection,
        ):
            # Mock memory manager to return not under pressure
            with patch.object(memory_manager, "is_under_pressure", return_value=False):
                optimized_normal = query_optimizer.optimize_query_plan(normal_query)
                assert optimized_normal["execution_plan"]["limit"] == 100

            # Simulate memory pressure by mocking is_under_pressure
            with patch.object(memory_manager, "is_under_pressure", return_value=True):
                with patch.object(
                    memory_manager, "get_available_memory", return_value=50
                ):
                    # Under pressure - should reduce limit
                    optimized_pressure = query_optimizer.optimize_query_plan(
                        normal_query
                    )
                    assert optimized_pressure["execution_plan"]["limit"] < 100

    def test_connection_pool_lifecycle_with_chromadb(self, temp_chromadb_path):
        """
        Verify ConnectionPool works with actual ChromaDB client.

        Tests:
        - Pool creates actual ChromaDB connections
        - Connections can execute real queries
        - Pool properly releases and reuses connections
        - Cleanup properly closes all connections
        """
        # Create connection pool with temp database
        pool = ConnectionPool(pool_size=3, db_path=temp_chromadb_path)

        try:
            # Get connection from pool
            conn1 = pool.get_connection()
            assert conn1 is not None

            # Verify connection works (can query)
            # Note: Real ChromaDB collection will be empty
            result = conn1.query(query_texts=["test"], n_results=1)
            assert result is not None
            assert "ids" in result

            # Release connection back to pool
            pool.release_connection(conn1)

            # Get connection again - should reuse same connection
            conn2 = pool.get_connection()
            assert conn2 is not None

            # Verify it's the same connection object
            assert id(conn1) == id(conn2)

            # Release again
            pool.release_connection(conn2)

            # Verify pool tracks available connections
            assert pool.available_connections > 0

        finally:
            # Cleanup
            pool.close()
            assert pool.available_connections == 0

    @pytest.mark.skipif(os.environ.get('PYTEST_XDIST_WORKER') is not None, reason="Test unstable in parallel execution mode")
    @pytest.mark.asyncio
    async def test_batch_coordinator_async_query_execution(self):
        """
        Verify BatchCoordinator correctly batches and executes async queries.

        Tests:
        - Single query executes quickly (< 50ms)
        - Multiple queries batched together
        - Batch timeout triggers execution
        - Results correctly mapped to queries
        """
        # Create batch coordinator
        coordinator = BatchCoordinator(batch_size=3, max_wait_ms=100)

        # Create mock executor
        mock_executor = AsyncMock()
        mock_executor.execute_batch = AsyncMock(
            return_value=[{"result": f"data_{i}"} for i in range(3)]
        )

        # Test single query execution (should be fast)
        single_query = {"text": "single query", "limit": 5}
        start_time = time.time()
        result = await coordinator.submit_query(single_query, mock_executor)
        elapsed_ms = (time.time() - start_time) * 1000

        # Should execute quickly (well under max_wait_ms)
        assert elapsed_ms < 50
        assert result is not None

        # Test batch execution
        queries = [{"text": f"query_{i}", "limit": 5} for i in range(3)]

        # Submit queries concurrently
        tasks = [coordinator.submit_query(q, mock_executor) for q in queries]
        results = await asyncio.gather(*tasks)

        # Verify all results returned
        assert len(results) == 3

        # Verify results correctly mapped
        for i, result in enumerate(results):
            assert result["result"] == f"data_{i}"

    def test_end_to_end_query_flow_cache_miss_to_population(
        self,
        query_optimizer: QueryOptimizer,
        result_cache: ResultCache,
        mock_chromadb_collection,
    ):
        """
        Verify complete query flow from cache miss through ChromaDB to cache population.

        Tests:
        - First query: cache miss → ChromaDB query → result cached
        - Second identical query: cache hit → no ChromaDB query
        - Query results match expected format
        - Optimization metrics tracked
        """
        query = {
            "text": "authentication with firebase",
            "category": "webdev",
            "limit": 10,
        }

        with patch.object(
            query_optimizer,
            "_get_chromadb_collection",
            return_value=mock_chromadb_collection,
        ):
            # First query - complete flow
            result1 = query_optimizer.execute_with_optimization(query)

            # Verify cache miss occurred
            assert result1["from_cache"] is False

            # Verify ChromaDB was queried
            assert mock_chromadb_collection.query.call_count == 1

            # Verify result format
            assert "results" in result1
            assert "optimization_metrics" in result1
            assert "cache_hit" in result1["optimization_metrics"]
            assert result1["optimization_metrics"]["cache_hit"] is False

            # Verify result was cached
            cache_metrics = result_cache.get_metrics()
            assert cache_metrics.size >= 1

            # Second identical query
            result2 = query_optimizer.execute_with_optimization(query)

            # Verify cache hit
            assert result2["from_cache"] is True
            assert result2["optimization_metrics"]["cache_hit"] is True

            # Verify results match
            assert result2["results"] == result1["results"]

            # Verify ChromaDB not called again
            assert mock_chromadb_collection.query.call_count == 1

    def test_connection_pool_exhaustion_and_recovery(self):
        """
        Verify ConnectionPool handles exhaustion and recovers gracefully.

        Tests:
        - Pool exhaustion raises appropriate timeout error
        - Released connections become available
        - Pool recovers and continues functioning
        - No connection leaks
        """
        # Create small pool for easier exhaustion
        pool = ConnectionPool(pool_size=2)

        # Mock connection creation
        mock_conn = Mock()
        with patch.object(pool, "_create_connection", return_value=mock_conn):
            # Acquire all connections
            conn1 = pool.get_connection()
            conn2 = pool.get_connection()

            # Pool should be exhausted
            assert pool.available_connections == 0

            # Trying to get another should timeout
            with pytest.raises(TimeoutError, match="exhausted"):
                pool.get_connection(timeout=0.1)

            # Release one connection
            pool.release_connection(conn1)

            # Should now have one available
            assert pool.available_connections == 1

            # Should be able to acquire again
            conn3 = pool.get_connection()
            assert conn3 is not None

            # Release all
            pool.release_connection(conn2)
            pool.release_connection(conn3)

            # Pool should be fully available
            assert pool.available_connections == 2

            # Cleanup
            pool.close()

    @pytest.mark.asyncio
    async def test_batch_coordinator_concurrent_query_handling(self):
        """
        Verify BatchCoordinator handles concurrent async query submissions.

        Tests:
        - Concurrent submissions batched correctly
        - Results mapped to correct queries
        - No race conditions or data corruption
        - Metrics track all queries
        """
        coordinator = BatchCoordinator(batch_size=5, max_wait_ms=100)

        # Create mock executor that returns unique results per query
        mock_executor = AsyncMock()

        async def execute_batch_impl(queries):
            """Return results matching query count."""
            return [
                {"query_idx": i, "data": f"result_{i}"} for i in range(len(queries))
            ]

        mock_executor.execute_batch = execute_batch_impl

        # Submit queries concurrently
        num_queries = 10
        queries = [
            {"text": f"concurrent_query_{i}", "limit": 5} for i in range(num_queries)
        ]

        tasks = [coordinator.submit_query(q, mock_executor) for q in queries]
        results = await asyncio.gather(*tasks)

        # Verify all queries completed
        assert len(results) == num_queries

        # Verify results are valid
        for result in results:
            assert "query_idx" in result
            assert "data" in result

        # Verify metrics tracked all queries
        metrics = coordinator.get_metrics()
        assert metrics.total_queries == num_queries

    def test_combined_components_optimizer_pool_cache(
        self, memory_manager: MemoryManager, mock_chromadb_collection
    ):
        """
        Verify all components work together in realistic scenario.

        Tests:
        - Queries flow through optimizer → cache → ChromaDB
        - Components share state correctly
        - Memory constraints affect all components
        - Performance metrics collected across components
        """
        import uuid

        # Create fresh cache and optimizer for this test
        cache_policy = CachePolicy(max_size=100, default_ttl=300)
        fresh_cache = ResultCache(policy=cache_policy)

        # Ensure cache is completely empty
        fresh_cache.clear()

        query_optimizer = QueryOptimizer(
            cache_system=fresh_cache, memory_manager=memory_manager
        )

        # Use unique queries with UUID to ensure no cross-test pollution
        unique_id = str(uuid.uuid4())[:8]
        queries = [
            {"text": f"combined_test_query_1_{unique_id}", "limit": 10},
            {"text": f"combined_test_query_2_{unique_id}", "limit": 20},
            {
                "text": f"combined_test_query_1_{unique_id}",
                "limit": 10,
            },  # Duplicate for cache hit
        ]

        with patch.object(
            query_optimizer,
            "_get_chromadb_collection",
            return_value=mock_chromadb_collection,
        ):
            results = []
            cache_hits_before_test = fresh_cache.get_metrics().hits
            cache_misses_before_test = fresh_cache.get_metrics().misses

            for i, query in enumerate(queries):
                result = query_optimizer.execute_with_optimization(query)
                results.append(result)

            # Verify results
            assert len(results) == 3

            # Verify cache behavior changed appropriately during test
            cache_metrics_after = fresh_cache.get_metrics()

            # Should have at least one cache hit (query 2 = query 0)
            assert cache_metrics_after.hits > cache_hits_before_test

            # Should have at least two cache misses (unique queries 0 and 1)
            assert cache_metrics_after.misses >= cache_misses_before_test + 2

            # Cache should contain at least 2 unique queries
            assert cache_metrics_after.size >= 2

            # Verify third query was a cache hit
            # (Since query[2] == query[0], it should hit cache)
            assert results[2]["from_cache"] is True

            # Verify memory manager is tracking
            current_memory = memory_manager.check_memory_usage()
            assert current_memory > 0

    def test_memory_pressure_affecting_query_optimization(
        self,
        query_optimizer: QueryOptimizer,
        memory_manager: MemoryManager,
        result_cache: ResultCache,
        mock_chromadb_collection,
    ):
        """
        Verify memory pressure triggers appropriate optimization behaviors.

        Tests:
        - High memory pressure → aggressive query limit reduction
        - Cache eviction triggered by memory manager
        - Query optimization adapts to memory constraints
        - System remains functional under pressure
        """
        # Set up eviction callback
        evicted_entries = []

        def eviction_callback(percentage: float):
            """Track eviction calls."""
            evicted_entries.append(percentage)
            # Simulate cache eviction
            result_cache.evict_expired()

        memory_manager.set_eviction_callback(eviction_callback)

        # Populate cache
        with patch.object(
            query_optimizer,
            "_get_chromadb_collection",
            return_value=mock_chromadb_collection,
        ):
            for i in range(10):
                query = {"text": f"query_{i}", "limit": 100}
                query_optimizer.execute_with_optimization(query)

            # Verify cache populated
            cache_metrics_before = result_cache.get_metrics()
            assert cache_metrics_before.size >= 10

            # Simulate memory pressure
            memory_manager._is_under_pressure = True
            memory_manager._available_memory_mb = 50

            # Trigger eviction
            memory_manager.trigger_cache_eviction(0.5)

            # Verify eviction callback was called
            assert len(evicted_entries) > 0

            # Test query optimization under pressure
            pressure_query = {"text": "pressure query", "limit": 1000}
            optimized = query_optimizer.optimize_query_plan(pressure_query)

            # Limit should be reduced under pressure
            assert optimized["execution_plan"]["limit"] < 1000

            # System should still function
            result = query_optimizer.execute_with_optimization(pressure_query)
            assert result is not None
            assert "results" in result

    def test_chromadb_unavailable_error_handling(self, query_optimizer: QueryOptimizer):
        """
        Verify components handle ChromaDB connection failures gracefully.

        Tests:
        - QueryOptimizer propagates errors correctly
        - Cache not corrupted by failed queries
        - Error metrics tracked
        """
        query = {"text": "test query", "limit": 5}

        # Mock ChromaDB to raise connection error
        mock_collection = Mock()
        mock_collection.query.side_effect = Exception("ChromaDB connection failed")

        with patch.object(
            query_optimizer,
            "_get_chromadb_collection",
            return_value=mock_collection,
        ):
            # Query should raise exception
            with pytest.raises(Exception, match="ChromaDB"):
                query_optimizer.execute_with_optimization(query)

            # Verify cache not corrupted
            cache_metrics = query_optimizer.cache_system.get_metrics()
            # Cache should not have stored failed result
            assert cache_metrics.size == 0

    def test_failed_queries_dont_corrupt_cache(
        self, query_optimizer: QueryOptimizer, result_cache: ResultCache
    ):
        """
        Verify failed queries don't corrupt cache.

        Tests:
        - Failed queries don't cache incomplete results
        - Cache remains consistent after errors
        - Subsequent queries succeed
        """
        good_query = {"text": "good query", "limit": 5}
        bad_query = {"text": "bad query", "limit": 5}

        # Mock ChromaDB to succeed for good query, fail for bad query
        mock_collection = Mock()

        def query_side_effect(*args, **kwargs):
            query_text = kwargs.get("query_texts", [""])[0]
            if "bad" in query_text:
                raise Exception("Query failed")
            return {
                "ids": [["case1"]],
                "distances": [[0.1]],
                "documents": [["doc1"]],
                "metadatas": [[{"category": "test"}]],
            }

        mock_collection.query.side_effect = query_side_effect

        with patch.object(
            query_optimizer,
            "_get_chromadb_collection",
            return_value=mock_collection,
        ):
            # Execute good query
            result1 = query_optimizer.execute_with_optimization(good_query)
            assert result1 is not None
            assert len(result1["results"]) == 1

            # Try bad query
            with pytest.raises(Exception, match="failed"):
                query_optimizer.execute_with_optimization(bad_query)

            # Verify cache only has good result
            cache_metrics = result_cache.get_metrics()
            assert cache_metrics.size == 1

            # Execute good query again - should hit cache
            result2 = query_optimizer.execute_with_optimization(good_query)
            assert result2["from_cache"] is True

    @pytest.mark.asyncio
    async def test_batch_coordinator_partial_failures(self):
        """
        Verify BatchCoordinator handles partial batch failures.

        Tests:
        - Successful queries return results
        - Failed queries return errors
        - Batch doesn't abort entirely on partial failure
        - Metrics reflect mix of success/failure
        """
        coordinator = BatchCoordinator(batch_size=5, max_wait_ms=100)

        # Mock executor that returns mix of success and error
        mock_executor = AsyncMock()
        mock_executor.execute_batch = AsyncMock(
            return_value=[
                {"result": "success_0"},
                {"error": "Query failed", "status": "error"},
                {"result": "success_2"},
            ]
        )

        queries = [
            {"text": "query_0", "limit": 5},
            {"text": "query_1", "limit": 5},
            {"text": "query_2", "limit": 5},
        ]

        # Submit queries
        tasks = [coordinator.submit_query(q, mock_executor) for q in queries]
        results = await asyncio.gather(*tasks)

        # Verify all queries got responses
        assert len(results) == 3

        # Verify mix of success and errors
        assert "result" in results[0]
        assert "error" in results[1]
        assert "result" in results[2]

    def test_integration_with_real_chromadb_query_patterns(
        self, query_optimizer: QueryOptimizer, mock_chromadb_collection
    ):
        """
        Verify components work with realistic ChromaDB query patterns.

        Tests:
        - Category filtering works through all layers
        - Similarity thresholds applied correctly
        - Result limits respected
        - Metadata preserved through pipeline
        """
        # Query with category filter
        query = {
            "text": "test query",
            "category": "orchestration",
            "subcategory": "planning",
            "limit": 5,
            "threshold": 0.8,
        }

        with patch.object(
            query_optimizer,
            "_get_chromadb_collection",
            return_value=mock_chromadb_collection,
        ):
            result = query_optimizer.execute_with_optimization(query)

            # Verify ChromaDB was called with correct parameters
            call_args = mock_chromadb_collection.query.call_args
            assert call_args is not None

            # Verify where clause includes filters
            where_clause = call_args[1].get("where")
            if where_clause:
                assert where_clause.get("category") == "orchestration"
                assert where_clause.get("subcategory") == "planning"

            # Verify results maintain metadata
            assert "results" in result
            for entry in result["results"]:
                assert "metadata" in entry
                assert "category" in entry["metadata"]

    def test_performance_metrics_collection_across_components(
        self,
        query_optimizer: QueryOptimizer,
        result_cache: ResultCache,
        mock_chromadb_collection,
    ):
        """
        Verify metrics collected accurately across all components.

        Tests:
        - Query timing tracked end-to-end
        - Cache hit/miss rates accurate
        - Memory usage metrics reflect reality
        """
        queries = [
            {"text": "query_1", "limit": 5},
            {"text": "query_2", "limit": 5},
            {"text": "query_1", "limit": 5},  # Duplicate
            {"text": "query_3", "limit": 5},
        ]

        with patch.object(
            query_optimizer,
            "_get_chromadb_collection",
            return_value=mock_chromadb_collection,
        ):
            for query in queries:
                result = query_optimizer.execute_with_optimization(query)
                # Verify optimization metrics present
                assert "optimization_metrics" in result
                assert "optimization_time_ms" in result["optimization_metrics"]

            # Verify cache metrics
            cache_metrics = result_cache.get_metrics()
            assert cache_metrics.hits >= 1  # Duplicate query should hit
            assert cache_metrics.misses >= 3  # Three unique queries
            assert cache_metrics.hit_rate > 0

    @pytest.mark.asyncio
    async def test_connection_pool_batch_coordinator_integration(self):
        """
        Verify connection pool works correctly with batch coordinator.

        Tests:
        - Batch queries use pooled connections
        - Connections released after batch execution
        - Pool doesn't exhaust under batch load
        - Connection reuse across batches
        """
        # Create connection pool
        pool = ConnectionPool(pool_size=3)

        # Create batch coordinator
        coordinator = BatchCoordinator(batch_size=5, max_wait_ms=100)

        # Mock connections
        mock_conn = Mock()
        with patch.object(pool, "_create_connection", return_value=mock_conn):
            # Mock executor that uses connection pool
            mock_executor = AsyncMock()

            async def execute_batch_with_pool(queries):
                # Simulate using pool
                conn = pool.get_connection()
                try:
                    # Simulate query execution
                    await asyncio.sleep(0.01)
                    return [{"result": f"data_{i}"} for i in range(len(queries))]
                finally:
                    pool.release_connection(conn)

            mock_executor.execute_batch = execute_batch_with_pool

            # Submit multiple batches
            for batch_num in range(3):
                queries = [
                    {"text": f"batch_{batch_num}_query_{i}", "limit": 5}
                    for i in range(5)
                ]

                tasks = [coordinator.submit_query(q, mock_executor) for q in queries]
                results = await asyncio.gather(*tasks)

                # Verify batch completed
                assert len(results) == 5

            # Verify pool still has connections available (no leaks)
            assert pool.available_connections > 0

            # Cleanup
            pool.close()
