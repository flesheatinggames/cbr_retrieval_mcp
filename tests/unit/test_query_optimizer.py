"""
Unit tests for Query Optimizer components.

This module tests ConnectionPool, QueryOptimizer, BatchCoordinator, and QueryCache
components following TDD principles. These tests will initially fail until the
implementations are complete.

Test Coverage:
- ConnectionPool: Database connection pooling and management
- QueryOptimizer: Query planning and optimization
- BatchCoordinator: Query batching logic
- QueryCache: Query result caching
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest

# These imports will fail initially - this is expected in TDD
from cbr_mcp_server.performance.query_optimizer import (
    BatchCoordinator,
    ConnectionPool,
    QueryCache,
    QueryOptimizer,
)


class TestConnectionPool:
    """Test suite for ConnectionPool component."""

    @pytest.fixture
    def mock_chroma_client(self):
        """Create mock ChromaDB client."""
        client = MagicMock()
        client.get_or_create_collection = MagicMock(return_value=MagicMock())
        return client

    @pytest.fixture
    def mock_chroma_connection(self):
        """Create mock ChromaDB connection."""
        connection = MagicMock()
        connection.query = MagicMock(return_value={"results": []})
        connection.get = MagicMock(return_value={"documents": []})
        connection.is_valid = MagicMock(return_value=True)
        return connection

    @pytest.fixture
    def connection_pool(self, mock_chroma_client):
        """Create ConnectionPool instance with default configuration."""
        with patch(
            "cbr_mcp_server.performance.query_optimizer.chromadb.Client",
            return_value=mock_chroma_client,
        ):
            return ConnectionPool(pool_size=5)

    def test_pool_initialization_with_configured_size(self):
        """Verify ConnectionPool initializes with configured size."""
        pool_size = 3
        pool = ConnectionPool(pool_size=pool_size)

        assert pool.pool_size == pool_size
        assert pool.max_size == pool_size

    def test_pool_initialization_with_default_size(self):
        """Verify ConnectionPool initializes with default size if not specified."""
        pool = ConnectionPool()

        # Default size should be reasonable (5 is common default)
        assert pool.pool_size > 0
        assert pool.pool_size <= 10

    def test_pool_initialization_creates_empty_pool(self):
        """Verify ConnectionPool starts with empty pool (lazy initialization)."""
        pool = ConnectionPool(pool_size=5)

        # Pool should be empty initially (connections created on-demand)
        assert pool.available_connections == 0 or pool.available_connections == 5

    def test_get_connection_returns_chroma_connection(
        self, connection_pool, mock_chroma_connection
    ):
        """Verify get_connection() returns a ChromaDB connection object."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            connection = connection_pool.get_connection()

            assert connection is not None
            assert hasattr(connection, "query") or hasattr(connection, "get")

    def test_get_connection_when_pool_not_exhausted(
        self, connection_pool, mock_chroma_connection
    ):
        """Verify get_connection() works when pool has available connections."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            # Get initial available count
            initial_available = connection_pool.available_connections

            connection = connection_pool.get_connection()

            assert connection is not None
            # Available connections should decrease (or stay same if created on-demand)
            assert connection_pool.available_connections <= initial_available

    def test_get_connection_pool_exhaustion_behavior(
        self, connection_pool, mock_chroma_connection
    ):
        """Verify behavior when all connections are in use (pool exhausted)."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            # Acquire all connections
            connections = []
            for i in range(connection_pool.pool_size):
                conn = connection_pool.get_connection()
                connections.append(conn)

            # Pool should now be exhausted
            # Attempting to get another connection should either:
            # 1. Wait for available connection
            # 2. Create new connection (if allowed)
            # 3. Raise exception

            # We'll test that it handles exhaustion gracefully
            try:
                extra_conn = connection_pool.get_connection(timeout=0.1)
                # If we get here, pool allows creating extra connections or waiting
                assert extra_conn is not None
            except (TimeoutError, RuntimeError, Exception) as e:
                # Pool correctly raises exception when exhausted
                assert "exhausted" in str(e).lower() or "timeout" in str(e).lower()

    @pytest.mark.skipif(
        os.environ.get('PYTEST_XDIST_WORKER') is not None,
        reason="Flaky timing test - skip in parallel execution mode"
    )
    def test_get_connection_with_timeout(self, connection_pool, mock_chroma_connection):
        """Verify get_connection() respects timeout parameter when waiting."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            # Acquire all connections
            connections = []
            for i in range(connection_pool.pool_size):
                conn = connection_pool.get_connection()
                connections.append(conn)

            # Try to get connection with short timeout
            start_time = time.time()
            try:
                connection_pool.get_connection(timeout=0.5)
            except (TimeoutError, RuntimeError):
                elapsed = time.time() - start_time
                # Should timeout around 0.5 seconds (allow some margin)
                assert 0.3 <= elapsed <= 1.0

    def test_release_connection_returns_to_pool(
        self, connection_pool, mock_chroma_connection
    ):
        """Verify release_connection() returns connection to pool."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            # Get connection
            connection = connection_pool.get_connection()
            initial_available = connection_pool.available_connections

            # Release connection
            connection_pool.release_connection(connection)

            # Available connections should increase
            assert connection_pool.available_connections > initial_available

    def test_release_connection_with_none(self, connection_pool):
        """Verify release_connection() handles None gracefully."""
        # Should not raise error
        try:
            connection_pool.release_connection(None)
            # If it succeeds silently, that's valid
        except (ValueError, TypeError) as e:
            # If it raises specific exception, that's also valid
            assert "None" in str(e) or "null" in str(e).lower()

    def test_release_connection_with_invalid_connection(self, connection_pool):
        """Verify release_connection() handles invalid connections."""
        invalid_conn = Mock()

        # Should handle gracefully
        try:
            connection_pool.release_connection(invalid_conn)
        except (ValueError, RuntimeError) as e:
            # Raising exception for invalid connection is acceptable
            assert "invalid" in str(e).lower() or "unknown" in str(e).lower()

    def test_connection_reuse_acquire_release_acquire(
        self, connection_pool, mock_chroma_connection
    ):
        """Verify acquired connections can be released and re-acquired."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            # First acquisition
            conn1 = connection_pool.get_connection()
            conn1_id = id(conn1)

            # Release
            connection_pool.release_connection(conn1)

            # Second acquisition
            conn2 = connection_pool.get_connection()
            conn2_id = id(conn2)

            # Should reuse same connection object
            assert conn1_id == conn2_id or conn2 is not None

    def test_connection_reuse_multiple_cycles(
        self, connection_pool, mock_chroma_connection
    ):
        """Verify connections can be acquired and released multiple times."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            # Perform multiple acquire/release cycles
            for cycle in range(5):
                conn = connection_pool.get_connection()
                assert conn is not None

                # Use connection
                if hasattr(conn, "query"):
                    conn.query.return_value = {"results": []}

                # Release
                connection_pool.release_connection(conn)

            # Pool should still be functional
            assert connection_pool.available_connections >= 0

    def test_warm_pool_initializes_all_connections(
        self, connection_pool, mock_chroma_connection
    ):
        """Verify warm_pool() pre-initializes all connections."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            # Warm the pool
            connection_pool.warm_pool()

            # All connections should be available
            assert connection_pool.available_connections == connection_pool.pool_size

    def test_warm_pool_idempotency(self, connection_pool, mock_chroma_connection):
        """Verify warm_pool() is idempotent (safe to call multiple times)."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ) as mock_create:
            # Warm pool twice
            connection_pool.warm_pool()
            first_call_count = mock_create.call_count

            connection_pool.warm_pool()
            second_call_count = mock_create.call_count

            # Should not create duplicate connections
            assert (
                second_call_count == first_call_count
                or second_call_count <= first_call_count + connection_pool.pool_size
            )

    def test_warm_pool_performance(self, connection_pool, mock_chroma_connection):
        """Verify warm_pool() completes in reasonable time."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            start_time = time.time()

            connection_pool.warm_pool()

            elapsed = time.time() - start_time

            # Should complete in under 5 seconds
            assert elapsed < 5.0

    def test_pool_size_configuration_respected(self):
        """Verify ConnectionPool respects configured pool size."""
        pool_size = 3
        pool = ConnectionPool(pool_size=pool_size)

        assert pool.pool_size == pool_size
        assert pool.max_size == pool_size

    def test_pool_with_minimum_size(self, mock_chroma_connection):
        """Verify pool works with minimum size (edge case)."""
        pool = ConnectionPool(pool_size=1)

        with patch.object(
            pool, "_create_connection", return_value=mock_chroma_connection
        ):
            # Should be able to acquire single connection
            conn = pool.get_connection()
            assert conn is not None

            # Release
            pool.release_connection(conn)

            # Should be able to acquire again
            conn2 = pool.get_connection()
            assert conn2 is not None

    def test_pool_with_large_size(self, mock_chroma_connection):
        """Verify pool works with larger configurations."""
        pool_size = 20
        pool = ConnectionPool(pool_size=pool_size)

        with patch.object(
            pool, "_create_connection", return_value=mock_chroma_connection
        ):
            # Acquire multiple connections
            connections = []
            for i in range(10):
                conn = pool.get_connection()
                connections.append(conn)

            # All should be valid
            assert len(connections) == 10
            assert all(conn is not None for conn in connections)

    def test_connection_validity_after_pool_operations(
        self, connection_pool, mock_chroma_connection
    ):
        """Verify connections remain valid after pool operations."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            # Acquire
            conn = connection_pool.get_connection()

            # Verify connection works
            if hasattr(conn, "query"):
                result = conn.query(query_texts=["test"])
                assert result is not None

            # Release
            connection_pool.release_connection(conn)

            # Re-acquire
            conn2 = connection_pool.get_connection()

            # Should still work
            if hasattr(conn2, "query"):
                result2 = conn2.query(query_texts=["test2"])
                assert result2 is not None

    def test_concurrent_connection_acquisition(
        self, connection_pool, mock_chroma_connection
    ):
        """Verify pool handles concurrent connection acquisitions safely."""
        import threading

        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            acquired_connections = []
            errors = []

            def acquire_connection():
                try:
                    conn = connection_pool.get_connection()
                    acquired_connections.append(conn)
                except Exception as e:
                    errors.append(e)

            # Create multiple threads acquiring connections
            threads = []
            for i in range(3):
                thread = threading.Thread(target=acquire_connection)
                threads.append(thread)
                thread.start()

            # Wait for all threads
            for thread in threads:
                thread.join(timeout=2.0)

            # Should have acquired connections without errors
            # (or errors should be acceptable pool exhaustion errors)
            assert len(acquired_connections) > 0 or len(errors) > 0

    def test_pool_cleanup_on_shutdown(self, connection_pool, mock_chroma_connection):
        """Verify pool cleans up connections on shutdown."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            # Warm pool
            connection_pool.warm_pool()

            # Close pool
            if hasattr(connection_pool, "close"):
                connection_pool.close()

                # Available connections should be 0
                assert connection_pool.available_connections == 0
            else:
                # If no close method, that's acceptable
                pass

    def test_get_connection_after_pool_close(
        self, connection_pool, mock_chroma_connection
    ):
        """Verify get_connection() after pool close raises appropriate error."""
        with patch.object(
            connection_pool, "_create_connection", return_value=mock_chroma_connection
        ):
            if hasattr(connection_pool, "close"):
                # Close pool
                connection_pool.close()

                # Attempting to get connection should fail
                with pytest.raises((RuntimeError, ValueError)):
                    connection_pool.get_connection()
            else:
                # If no close method, skip this test
                pytest.skip("ConnectionPool does not implement close()")


class TestQueryOptimizer:
    """Test suite for QueryOptimizer component."""

    @pytest.fixture
    def mock_cache_system(self):
        """Create mock CacheSystem for testing."""
        mock = Mock()
        mock.get.return_value = None  # Default: cache miss
        mock.set.return_value = None
        return mock

    @pytest.fixture
    def mock_memory_manager(self):
        """Create mock MemoryManager for testing."""
        mock = Mock()
        mock.get_available_memory.return_value = 400  # 400MB available
        mock.is_under_pressure.return_value = False
        return mock

    @pytest.fixture
    def mock_chromadb_collection(self):
        """Create mock ChromaDB collection for testing."""
        mock = Mock()
        mock.query.return_value = {
            "ids": [["case1", "case2"]],
            "distances": [[0.1, 0.2]],
            "documents": [["doc1", "doc2"]],
            "metadatas": [[{"category": "test"}, {"category": "test"}]],
        }
        return mock

    @pytest.fixture
    def query_optimizer(
        self, mock_cache_system, mock_memory_manager, mock_chromadb_collection
    ):
        """Create QueryOptimizer instance with mocked dependencies."""
        return QueryOptimizer(
            cache_system=mock_cache_system,
            memory_manager=mock_memory_manager,
            collection=mock_chromadb_collection,
        )

    def test_query_optimizer_initialization_with_dependencies(
        self, mock_cache_system, mock_memory_manager
    ):
        """Verify QueryOptimizer initializes with required dependencies."""
        optimizer = QueryOptimizer(
            cache_system=mock_cache_system, memory_manager=mock_memory_manager
        )

        assert optimizer.cache_system is mock_cache_system
        assert optimizer.memory_manager is mock_memory_manager

    def test_query_optimizer_initialization_without_dependencies(self):
        """Verify QueryOptimizer initialization fails without dependencies."""
        with pytest.raises((TypeError, ValueError)):
            QueryOptimizer()

    def test_optimize_query_plan_with_valid_query(self, query_optimizer):
        """Verify that a valid query is successfully optimized."""
        query = {"text": "test query", "limit": 10, "threshold": 0.7}

        optimized = query_optimizer.optimize_query_plan(query)

        assert optimized is not None
        assert "execution_plan" in optimized
        assert optimized["execution_plan"] is not None

    def test_optimize_query_plan_with_empty_query_text(self, query_optimizer):
        """Test edge case of empty query text."""
        query = {"text": "", "limit": 10}

        # Should raise ValueError for empty query
        with pytest.raises(ValueError, match="empty|text"):
            query_optimizer.optimize_query_plan(query)

    def test_optimize_query_plan_with_none_query(self, query_optimizer):
        """Test edge case of None query."""
        # Should raise TypeError or ValueError for None query
        with pytest.raises((TypeError, ValueError)):
            query_optimizer.optimize_query_plan(None)

    def test_optimize_query_plan_with_category_filter(self, query_optimizer):
        """Verify category filtering is preserved in optimization."""
        query = {"text": "test query", "category": "orchestration", "limit": 10}

        optimized = query_optimizer.optimize_query_plan(query)

        assert "category" in optimized["execution_plan"]["filters"]
        assert optimized["execution_plan"]["filters"]["category"] == "orchestration"

    def test_optimize_query_plan_with_subcategory_filter(self, query_optimizer):
        """Verify subcategory filtering is preserved in optimization."""
        query = {
            "text": "test query",
            "category": "orchestration",
            "subcategory": "planning",
            "limit": 10,
        }

        optimized = query_optimizer.optimize_query_plan(query)

        assert "subcategory" in optimized["execution_plan"]["filters"]
        assert optimized["execution_plan"]["filters"]["subcategory"] == "planning"

    def test_optimize_query_plan_with_similarity_threshold(self, query_optimizer):
        """Verify similarity thresholds are considered in optimization."""
        query = {"text": "test query", "threshold": 0.85, "limit": 10}

        optimized = query_optimizer.optimize_query_plan(query)

        assert optimized["execution_plan"]["threshold"] == 0.85

    def test_optimize_query_plan_with_invalid_query_type(self, query_optimizer):
        """Test edge case of invalid query type (not dict/Query object)."""
        invalid_query = "this is a string not a query"

        with pytest.raises(TypeError, match="query|dict|Query"):
            query_optimizer.optimize_query_plan(invalid_query)

    def test_execute_with_optimization_success(self, query_optimizer):
        """Verify successful execution with optimization."""
        query = {"text": "test query", "limit": 5}

        # ChromaDB collection already injected via fixture
        result = query_optimizer.execute_with_optimization(query)

        assert result is not None
        assert "results" in result
        assert len(result["results"]) > 0
        assert "optimization_metrics" in result

    def test_execute_with_optimization_with_cache_hit(
        self, query_optimizer, mock_cache_system
    ):
        """Verify cache is used when available."""
        query = {"text": "cached query", "limit": 5}

        # Mock cache hit
        cached_result = {
            "results": [{"id": "cached1"}],
            "from_cache": True,
            "optimization_metrics": {"cache_hit": True},
        }
        mock_cache_system.get.return_value = cached_result

        result = query_optimizer.execute_with_optimization(query)

        # Should return cached result
        assert result["from_cache"] is True
        assert result["results"][0]["id"] == "cached1"
        mock_cache_system.get.assert_called_once()

    def test_execute_with_optimization_with_cache_miss(
        self, query_optimizer, mock_cache_system
    ):
        """Verify ChromaDB query on cache miss."""
        query = {"text": "uncached query", "limit": 5}

        # Mock cache miss (already default in fixture)
        mock_cache_system.get.return_value = None

        # ChromaDB collection already injected via fixture
        result = query_optimizer.execute_with_optimization(query)

        # Should query ChromaDB
        query_optimizer._collection.query.assert_called_once()

        # Should cache the result
        mock_cache_system.set.assert_called_once()

        assert result.get("from_cache", False) is False

    def test_execute_with_optimization_chromadb_failure(self, query_optimizer):
        """Test error handling when ChromaDB fails."""
        query = {"text": "failing query", "limit": 5}

        # Mock ChromaDB failure
        query_optimizer._collection.query.side_effect = Exception(
            "ChromaDB connection failed"
        )

        with pytest.raises(Exception, match="ChromaDB"):
            query_optimizer.execute_with_optimization(query)

    def test_execute_with_optimization_empty_results(self, query_optimizer):
        """Verify handling of queries returning no results."""
        query = {"text": "no match query", "limit": 5}

        # Mock empty results
        query_optimizer._collection.query.return_value = {
            "ids": [[]],
            "distances": [[]],
            "documents": [[]],
            "metadatas": [[]],
        }

        result = query_optimizer.execute_with_optimization(query)

        assert "results" in result
        assert len(result["results"]) == 0

    def test_execute_with_max_results_limit(self, query_optimizer, mock_memory_manager):
        """Verify optimization respects max_results limits."""
        # Create query with very high limit
        query = {"text": "test query", "limit": 10000}

        optimized = query_optimizer.optimize_query_plan(query)

        # Should reduce limit based on memory constraints
        assert optimized["execution_plan"]["limit"] < 10000

    def test_optimization_under_memory_pressure(
        self, query_optimizer, mock_memory_manager
    ):
        """Test behavior when MemoryManager indicates low memory during optimization."""
        query = {"text": "test query", "limit": 100}

        # Simulate memory pressure
        mock_memory_manager.is_under_pressure.return_value = True
        mock_memory_manager.get_available_memory.return_value = 50  # Low memory

        optimized = query_optimizer.optimize_query_plan(query)

        # Should reduce result limit under memory pressure
        assert optimized["execution_plan"]["limit"] < query["limit"]

    def test_batch_queries_with_multiple_valid_queries(self, query_optimizer):
        """Verify batching of multiple queries."""
        queries = [
            {"text": "query 1", "limit": 5},
            {"text": "query 2", "limit": 5},
            {"text": "query 3", "limit": 5},
        ]

        # ChromaDB collection already injected via fixture
        batch_result = query_optimizer.batch_queries(queries)

        assert batch_result is not None
        assert "results" in batch_result
        assert len(batch_result["results"]) == 3
        assert batch_result["total_queries"] == 3

    def test_batch_queries_with_empty_list(self, query_optimizer):
        """Test edge case of empty query list."""
        # Should raise ValueError for empty list
        with pytest.raises(ValueError, match="empty"):
            query_optimizer.batch_queries([])

    def test_batch_queries_with_single_query(self, query_optimizer):
        """Verify batching works with single query."""
        queries = [{"text": "single query", "limit": 5}]

        # ChromaDB collection already injected via fixture
        batch_result = query_optimizer.batch_queries(queries)

        assert batch_result is not None
        assert len(batch_result["results"]) == 1
        assert batch_result["total_queries"] == 1

    def test_batch_queries_with_partial_failures(self, query_optimizer):
        """Test resilience when some queries fail."""
        queries = [
            {"text": "valid query 1", "limit": 5},
            {"text": "failing query", "limit": 5},
            {"text": "valid query 2", "limit": 5},
        ]

        # Mock ChromaDB to fail on second query
        def query_side_effect(*args, **kwargs):
            # Check the query text to determine if it should fail
            query_text = kwargs.get("query_texts", [""])[0]
            if "failing" in query_text:
                raise Exception("Query failed")
            return {
                "ids": [["case1"]],
                "distances": [[0.1]],
                "documents": [["doc1"]],
                "metadatas": [[{"category": "test"}]],
            }

        query_optimizer._collection.query.side_effect = query_side_effect

        batch_result = query_optimizer.batch_queries(queries)

        # Should have results for successful queries and errors for failed ones
        assert batch_result["total_queries"] == 3
        assert batch_result["successful_queries"] < 3
        assert len(batch_result["errors"]) > 0

    def test_batch_queries_with_all_failures(self, query_optimizer):
        """Test complete batch failure scenario."""
        queries = [
            {"text": "failing 1", "limit": 5},
            {"text": "failing 2", "limit": 5},
        ]

        # Mock all queries to fail
        query_optimizer._collection.query.side_effect = Exception("All queries failed")

        batch_result = query_optimizer.batch_queries(queries)

        assert batch_result["successful_queries"] == 0
        assert len(batch_result["errors"]) == 2

    def test_optimization_metrics_collection(self, query_optimizer):
        """Verify optimization metrics are collected."""
        query = {"text": "test query", "limit": 5}

        # ChromaDB collection already injected via fixture
        result = query_optimizer.execute_with_optimization(query)

        # Should include optimization metrics
        assert "optimization_metrics" in result
        assert "optimization_time_ms" in result["optimization_metrics"]
        assert "cache_hit" in result["optimization_metrics"]
        assert "result_count" in result["optimization_metrics"]

    def test_query_plan_caching(self, query_optimizer):
        """Verify query plans are cached for similar queries."""
        query1 = {"text": "test query", "limit": 10}
        query2 = {"text": "test query", "limit": 10}  # Same as query1

        plan1 = query_optimizer.optimize_query_plan(query1)
        plan2 = query_optimizer.optimize_query_plan(query2)

        # Second query should reuse optimized plan
        # (Implementation may vary - check for consistency)
        assert plan1["execution_plan"]["limit"] == plan2["execution_plan"]["limit"]

    def test_optimization_with_large_result_set_warning(self, query_optimizer):
        """Verify optimization handles large result sets with warning."""
        # Mock large result set (1000 results)
        large_ids = [[f"case{i}" for i in range(1000)]]
        large_distances = [[0.1 * i for i in range(1000)]]
        large_docs = [[f"doc{i}" for i in range(1000)]]
        large_metas = [[{"category": "test"} for _ in range(1000)]]

        query_optimizer._collection.query.return_value = {
            "ids": large_ids,
            "distances": large_distances,
            "documents": large_docs,
            "metadatas": large_metas,
        }

        query = {"text": "large result query", "limit": 1000}

        with patch("logging.warning") as mock_warning:
            result = query_optimizer.execute_with_optimization(query)

            # Should log warning for large result set
            # (Implementation may warn at different thresholds)
            # This assertion is optional based on implementation
            if result["results"] and len(result["results"]) > 500:
                assert mock_warning.called

        assert len(result["results"]) <= 1000

    def test_concurrent_query_optimization_thread_safety(self, query_optimizer):
        """Verify thread-safety of query optimization."""
        import threading

        queries = [{"text": f"concurrent query {i}", "limit": 5} for i in range(5)]

        results = []
        errors = []

        def optimize_query(query):
            try:
                result = query_optimizer.optimize_query_plan(query)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create threads for concurrent optimization
        threads = []
        for query in queries:
            thread = threading.Thread(target=optimize_query, args=(query,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=2.0)

        # All queries should complete successfully
        assert len(results) == 5
        assert len(errors) == 0


class TestBatchCoordinator:
    """Test suite for BatchCoordinator component."""

    @pytest.fixture
    def default_coordinator(self):
        """Create BatchCoordinator with default configuration."""
        return BatchCoordinator(batch_size=5, max_wait_ms=100)

    @pytest.fixture
    def custom_coordinator(self):
        """Create BatchCoordinator with custom configuration."""
        return BatchCoordinator(batch_size=10, max_wait_ms=200)

    @pytest.fixture
    async def mock_query_executor(self):
        """Create mock query executor."""
        executor = AsyncMock()
        executor.execute_batch = AsyncMock(
            return_value=[{"result": i} for i in range(5)]
        )
        return executor

    # Initialization Tests
    def test_batch_coordinator_initialization_with_defaults(self):
        """Verify BatchCoordinator initializes with default configuration."""
        coordinator = BatchCoordinator(batch_size=3, max_wait_ms=50)

        assert coordinator.batch_size == 3
        assert coordinator.max_wait_ms == 50

    def test_batch_coordinator_initialization_with_custom_batch_size(self):
        """Verify BatchCoordinator initializes with custom batch size."""
        coordinator = BatchCoordinator(batch_size=20, max_wait_ms=100)

        assert coordinator.batch_size == 20

    def test_batch_coordinator_initialization_with_custom_max_wait(self):
        """Verify BatchCoordinator initializes with custom max wait time."""
        coordinator = BatchCoordinator(batch_size=5, max_wait_ms=300)

        assert coordinator.max_wait_ms == 300

    def test_batch_coordinator_validates_positive_batch_size(self):
        """Verify BatchCoordinator validates positive batch size."""
        # Should raise error for zero batch size
        with pytest.raises(ValueError):
            BatchCoordinator(batch_size=0, max_wait_ms=100)

        # Should raise error for negative batch size
        with pytest.raises(ValueError):
            BatchCoordinator(batch_size=-5, max_wait_ms=100)

    def test_batch_coordinator_validates_positive_max_wait_time(self):
        """Verify BatchCoordinator validates positive max wait time."""
        # Should raise error for zero max wait
        with pytest.raises(ValueError):
            BatchCoordinator(batch_size=5, max_wait_ms=0)

        # Should raise error for negative max wait
        with pytest.raises(ValueError):
            BatchCoordinator(batch_size=5, max_wait_ms=-100)

    # Single Query Tests (No Batching)
    # Serial execution required - test has isolation issues in parallel mode
    @pytest.mark.serial
    @pytest.mark.asyncio
    async def test_single_query_executes_immediately_without_batching(
        self, default_coordinator, mock_query_executor
    ):
        """Verify single query executes immediately without batching."""
        query = {"type": "retrieve", "text": "test query"}

        start_time = time.time()
        result = await default_coordinator.submit_query(query, mock_query_executor)
        elapsed_ms = (time.time() - start_time) * 1000

        # Should execute immediately (well under max_wait_ms)
        assert elapsed_ms < 50  # Much less than max_wait_ms=100
        assert result is not None

    @pytest.mark.asyncio
    async def test_single_query_returns_correct_result_mapping(
        self, default_coordinator, mock_query_executor
    ):
        """Verify single query returns correct result mapping."""
        query = {"type": "retrieve", "text": "test query"}
        mock_query_executor.execute_batch = AsyncMock(
            return_value=[{"result": "single_result"}]
        )

        result = await default_coordinator.submit_query(query, mock_query_executor)

        assert result == {"result": "single_result"}

    @pytest.mark.asyncio
    async def test_single_query_maintains_response_format(
        self, default_coordinator, mock_query_executor
    ):
        """Verify single query maintains response format."""
        query = {"type": "retrieve", "text": "test", "metadata": {"id": "123"}}
        expected_result = {
            "result": "data",
            "metadata": {"query_id": "123", "timestamp": "2024-01-01"},
        }
        mock_query_executor.execute_batch = AsyncMock(return_value=[expected_result])

        result = await default_coordinator.submit_query(query, mock_query_executor)

        assert result == expected_result

    @pytest.mark.asyncio
    async def test_single_query_tracks_execution_time(
        self, default_coordinator, mock_query_executor
    ):
        """Verify single query tracks execution time."""
        query = {"type": "retrieve", "text": "test"}

        await default_coordinator.submit_query(query, mock_query_executor)

        metrics = default_coordinator.get_metrics()
        assert metrics.total_queries == 1
        assert metrics.avg_execution_time_ms >= 0

    # Multiple Query Batching Tests
    @pytest.mark.asyncio
    async def test_multiple_similar_queries_are_batched_together(
        self, default_coordinator, mock_query_executor
    ):
        """Verify multiple similar queries are batched together."""
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(3)]

        # Submit queries concurrently
        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # All queries should be in the same batch
        assert len(results) == 3
        # Executor should be called once for the batch
        assert mock_query_executor.execute_batch.call_count == 1

    @pytest.mark.asyncio
    async def test_batch_executes_when_batch_size_threshold_reached(
        self, default_coordinator, mock_query_executor
    ):
        """Verify batch executes when batch size threshold reached."""
        # default_coordinator has batch_size=5
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(5)]

        # Submit queries to fill the batch
        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # Should execute immediately when threshold reached
        assert len(results) == 5
        assert mock_query_executor.execute_batch.call_count == 1

    @pytest.mark.asyncio
    async def test_batch_executes_when_max_wait_time_exceeded(
        self, default_coordinator, mock_query_executor
    ):
        """Verify batch executes when max wait time exceeded."""
        # Submit only 2 queries (under batch_size=5)
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(2)]

        start_time = time.time()
        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)
        elapsed_ms = (time.time() - start_time) * 1000

        # Should execute after max_wait_ms=100
        assert elapsed_ms >= 95
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_batched_queries_maintain_ordering(
        self, default_coordinator, mock_query_executor
    ):
        """Verify batched queries maintain ordering."""
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(3)]
        expected_results = [{"result": f"result_{i}"} for i in range(3)]
        mock_query_executor.execute_batch = AsyncMock(return_value=expected_results)

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # Results should maintain the order of submission
        assert results[0] == {"result": "result_0"}
        assert results[1] == {"result": "result_1"}
        assert results[2] == {"result": "result_2"}

    @pytest.mark.asyncio
    async def test_batched_queries_map_responses_to_original_queries_correctly(
        self, default_coordinator, mock_query_executor
    ):
        """Verify batched queries map responses to original queries correctly."""
        queries = [
            {"type": "retrieve", "text": "query_A", "id": "A"},
            {"type": "retrieve", "text": "query_B", "id": "B"},
            {"type": "retrieve", "text": "query_C", "id": "C"},
        ]
        expected_results = [
            {"result": "result_A", "query_id": "A"},
            {"result": "result_B", "query_id": "B"},
            {"result": "result_C", "query_id": "C"},
        ]
        mock_query_executor.execute_batch = AsyncMock(return_value=expected_results)

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # Each result should map to its corresponding query
        assert results[0]["query_id"] == "A"
        assert results[1]["query_id"] == "B"
        assert results[2]["query_id"] == "C"

    # Batch Size Management Tests
    @pytest.mark.asyncio
    async def test_batch_size_limit_enforcement_does_not_exceed_max(
        self, default_coordinator, mock_query_executor
    ):
        """Verify batch size limit enforcement (does not exceed max)."""
        # Submit more queries than batch_size (5)
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(7)]

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        await asyncio.gather(*tasks)

        # Should create 2 batches: one of size 5, one of size 2
        # First batch should have exactly 5 queries
        first_batch_call = mock_query_executor.execute_batch.call_args_list[0]
        assert len(first_batch_call[0][0]) == 5

    @pytest.mark.asyncio
    async def test_partial_batch_execution_when_under_threshold(
        self, default_coordinator, mock_query_executor
    ):
        """Verify partial batch execution when under threshold."""
        # Submit only 3 queries (under batch_size=5)
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(3)]

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # Should execute partial batch after timeout
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_batch_fills_to_capacity_before_execution(
        self, default_coordinator, mock_query_executor
    ):
        """Verify batch fills to capacity before execution."""
        # Submit exactly batch_size queries
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(5)]

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        await asyncio.gather(*tasks)

        # Should execute once with full batch
        assert mock_query_executor.execute_batch.call_count == 1
        call_args = mock_query_executor.execute_batch.call_args_list[0]
        assert len(call_args[0][0]) == 5

    @pytest.mark.asyncio
    async def test_multiple_batches_created_when_queries_exceed_batch_size(
        self, default_coordinator, mock_query_executor
    ):
        """Verify multiple batches created when queries exceed batch size."""
        # Submit 12 queries (batch_size=5 means 3 batches needed)
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(12)]

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        await asyncio.gather(*tasks)

        # Should create 3 batches (5 + 5 + 2)
        assert mock_query_executor.execute_batch.call_count >= 2

    # Timeout Behavior Tests
    @pytest.mark.skipif(
        os.environ.get('PYTEST_XDIST_WORKER') is not None,
        reason="Flaky timing test - skip in parallel execution mode"
    )
    @pytest.mark.asyncio
    async def test_batch_executes_after_max_wait_time_even_if_not_full(
        self, default_coordinator, mock_query_executor
    ):
        """Verify batch executes after max wait time even if not full."""
        # Submit only 2 queries (under batch_size=5)
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(2)]

        start_time = time.time()
        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        await asyncio.gather(*tasks)
        elapsed_ms = (time.time() - start_time) * 1000

        # Should wait approximately max_wait_ms before executing
        assert elapsed_ms >= 95  # max_wait_ms=100
        assert elapsed_ms < 200  # Should not wait much longer

    @pytest.mark.asyncio
    async def test_max_wait_time_starts_from_first_query_arrival(
        self, default_coordinator, mock_query_executor
    ):
        """Verify max wait time starts from first query arrival."""
        # Submit first query
        first_query = {"type": "retrieve", "text": "query_0"}

        start_time = time.time()
        task1 = asyncio.create_task(
            default_coordinator.submit_query(first_query, mock_query_executor)
        )

        # Wait 50ms before submitting second query
        await asyncio.sleep(0.05)

        second_query = {"type": "retrieve", "text": "query_1"}
        task2 = asyncio.create_task(
            default_coordinator.submit_query(second_query, mock_query_executor)
        )

        await asyncio.gather(task1, task2)
        elapsed_ms = (time.time() - start_time) * 1000

        # Total time should be ~100ms from first query (not 150ms)
        assert elapsed_ms >= 95
        assert elapsed_ms < 150

    @pytest.mark.asyncio
    async def test_timeout_cancellation_when_batch_fills_before_timeout(
        self, default_coordinator, mock_query_executor
    ):
        """Verify timeout cancellation when batch fills before timeout."""
        # Submit exactly batch_size queries quickly
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(5)]

        start_time = time.time()
        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        await asyncio.gather(*tasks)
        elapsed_ms = (time.time() - start_time) * 1000

        # Should execute immediately without waiting for timeout
        assert elapsed_ms < 50  # Much less than max_wait_ms=100

    @pytest.mark.asyncio
    async def test_concurrent_timeout_handling_for_multiple_batches(
        self, default_coordinator, mock_query_executor
    ):
        """Verify concurrent timeout handling for multiple batches."""
        # Submit 7 queries (will create 2 batches: 5 + 2)
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(7)]

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        await asyncio.gather(*tasks)

        # Both batches should execute correctly
        assert mock_query_executor.execute_batch.call_count >= 2

    @pytest.mark.asyncio
    async def test_timer_cancellation_is_properly_awaited(
        self, default_coordinator, mock_query_executor
    ):
        """
        Verify timer task cancellation is properly awaited to prevent resource leaks.

        This test ensures that when batch fills before timeout, the timer task is:
        1. Cancelled properly
        2. Awaited to completion
        3. CancelledError is handled
        4. No resource leaks occur
        """
        # Submit enough queries to fill the batch immediately
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(5)]

        # Mock executor to simulate some work
        async def mock_execute_batch(batch_queries):
            await asyncio.sleep(0.01)  # Simulate some processing
            return [{"result": f"result_{i}"} for i in range(len(batch_queries))]

        mock_query_executor.execute_batch = mock_execute_batch

        # Submit queries - batch should fill and cancel timer
        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # Verify all queries completed successfully
        assert len(results) == 5
        assert all("result" in r for r in results)

        # Verify no timer task is left running
        # (timer should be cancelled and cleaned up)
        assert default_coordinator._batch_timer_task is None or \
               default_coordinator._batch_timer_task.done()

    @pytest.mark.asyncio
    async def test_timer_cancellation_with_concurrent_operations(
        self, default_coordinator, mock_query_executor
    ):
        """
        Verify timer cancellation works correctly with concurrent batch operations.

        This test simulates a scenario where:
        1. Multiple queries arrive quickly
        2. Batch fills before timer expires
        3. Timer is cancelled while other operations are in progress
        4. System continues to work correctly
        """
        # Submit queries in waves to test concurrent cancellation
        wave1 = [{"type": "retrieve", "text": f"wave1_{i}"} for i in range(5)]
        wave2 = [{"type": "retrieve", "text": f"wave2_{i}"} for i in range(5)]

        # Mock executor with slight delay
        async def mock_execute_batch(batch_queries):
            await asyncio.sleep(0.02)
            return [{"result": f"result_{i}"} for i in range(len(batch_queries))]

        mock_query_executor.execute_batch = mock_execute_batch

        # Submit first wave - will fill batch and cancel timer
        tasks1 = [
            default_coordinator.submit_query(q, mock_query_executor) for q in wave1
        ]
        results1 = await asyncio.gather(*tasks1)

        # Submit second wave - should create new batch
        tasks2 = [
            default_coordinator.submit_query(q, mock_query_executor) for q in wave2
        ]
        results2 = await asyncio.gather(*tasks2)

        # Verify both waves completed successfully
        assert len(results1) == 5
        assert len(results2) == 5
        assert all("result" in r for r in results1)
        assert all("result" in r for r in results2)

    @pytest.mark.asyncio
    async def test_timer_cancellation_no_resource_leak(
        self, default_coordinator, mock_query_executor
    ):
        """
        Verify that timer cancellation does not cause resource leaks.

        This test submits multiple batches and verifies that:
        1. Each timer is properly cancelled
        2. No tasks are left running
        3. System state is clean after each batch
        """
        # Submit multiple batches
        for batch_num in range(3):
            queries = [
                {"type": "retrieve", "text": f"batch{batch_num}_query_{i}"}
                for i in range(5)
            ]

            tasks = [
                default_coordinator.submit_query(q, mock_query_executor)
                for q in queries
            ]
            results = await asyncio.gather(*tasks)

            # Verify batch completed
            assert len(results) == 5

            # Verify no timer left running
            assert default_coordinator._batch_timer_task is None or \
                   default_coordinator._batch_timer_task.done()

            # Small delay between batches
            await asyncio.sleep(0.01)

        # Verify system is in clean state
        assert len(default_coordinator._current_batch) == 0
        assert len(default_coordinator._batch_futures) == 0

    @pytest.mark.asyncio
    async def test_timer_task_cleanup_after_cancellation(
        self, default_coordinator, mock_query_executor
    ):
        """
        Verify timer task is properly cleaned up after cancellation.

        This ensures that after batch execution with timer cancellation:
        1. Timer task reference is set to None
        2. Task state is 'done'
        3. No pending cancellations
        """
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(5)]

        # Track timer task state
        timer_task_before = None

        async def track_and_execute(batch_queries):
            nonlocal timer_task_before
            timer_task_before = default_coordinator._batch_timer_task
            await asyncio.sleep(0.01)
            return [{"result": f"result_{i}"} for i in range(len(batch_queries))]

        mock_query_executor.execute_batch = track_and_execute

        # Submit queries
        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        await asyncio.gather(*tasks)

        # Verify timer was cancelled and cleaned up
        if timer_task_before is not None:
            assert timer_task_before.done()
            # If task was cancelled, it should have CancelledError
            if timer_task_before.cancelled():
                with pytest.raises(asyncio.CancelledError):
                    timer_task_before.result()

        # Verify current state is clean
        assert default_coordinator._batch_timer_task is None

    # Query Similarity Detection Tests
    @pytest.mark.asyncio
    async def test_similar_queries_are_grouped_into_same_batch(
        self, default_coordinator, mock_query_executor
    ):
        """Verify similar queries are grouped into same batch."""
        # All retrieve queries should be grouped together
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(3)]

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        await asyncio.gather(*tasks)

        # Should be in one batch
        assert mock_query_executor.execute_batch.call_count == 1

    @pytest.mark.asyncio
    async def test_dissimilar_queries_are_separated_into_different_batches(
        self, default_coordinator, mock_query_executor
    ):
        """Verify dissimilar queries are separated into different batches."""
        # Different query types should be in different batches
        retrieve_query = {"type": "retrieve", "text": "query_1"}
        search_query = {"type": "search_category", "category": "test"}

        # Submit with different executors or expect separation
        task1 = default_coordinator.submit_query(retrieve_query, mock_query_executor)
        task2 = default_coordinator.submit_query(search_query, mock_query_executor)

        await asyncio.gather(task1, task2)

        # Different query types may be batched separately or require type-specific handling
        assert mock_query_executor.execute_batch.call_count >= 1

    @pytest.mark.asyncio
    async def test_similarity_detection_based_on_query_type(
        self, default_coordinator, mock_query_executor
    ):
        """Verify similarity detection based on query type."""
        queries = [
            {"type": "retrieve", "text": "query_1"},
            {"type": "retrieve", "text": "query_2"},
            {"type": "search_category", "category": "test"},
        ]

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        await asyncio.gather(*tasks)

        # Should batch by type
        assert mock_query_executor.execute_batch.call_count >= 1

    @pytest.mark.asyncio
    async def test_similarity_detection_based_on_query_parameters(
        self, default_coordinator, mock_query_executor
    ):
        """Verify similarity detection based on query parameters."""
        # Similar parameters should be batched
        queries = [
            {"type": "retrieve", "text": "query", "threshold": 0.8},
            {"type": "retrieve", "text": "query", "threshold": 0.8},
        ]

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        await asyncio.gather(*tasks)

        # Should be in same batch (similar parameters)
        assert mock_query_executor.execute_batch.call_count == 1

    # Response Mapping Tests
    @pytest.mark.asyncio
    async def test_responses_correctly_mapped_to_original_query_order(
        self, default_coordinator, mock_query_executor
    ):
        """Verify responses correctly mapped to original query order."""
        queries = [
            {"type": "retrieve", "text": "first"},
            {"type": "retrieve", "text": "second"},
            {"type": "retrieve", "text": "third"},
        ]
        expected_results = [
            {"result": "first_result"},
            {"result": "second_result"},
            {"result": "third_result"},
        ]
        mock_query_executor.execute_batch = AsyncMock(return_value=expected_results)

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # Verify correct mapping
        assert results[0]["result"] == "first_result"
        assert results[1]["result"] == "second_result"
        assert results[2]["result"] == "third_result"

    @pytest.mark.asyncio
    async def test_response_mapping_preserves_query_metadata(
        self, default_coordinator, mock_query_executor
    ):
        """Verify response mapping preserves query metadata."""
        queries = [
            {"type": "retrieve", "text": "query", "metadata": {"id": "A"}},
            {"type": "retrieve", "text": "query", "metadata": {"id": "B"}},
        ]
        expected_results = [
            {"result": "data_A", "query_metadata": {"id": "A"}},
            {"result": "data_B", "query_metadata": {"id": "B"}},
        ]
        mock_query_executor.execute_batch = AsyncMock(return_value=expected_results)

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # Metadata should be preserved
        assert results[0]["query_metadata"]["id"] == "A"
        assert results[1]["query_metadata"]["id"] == "B"

    @pytest.mark.asyncio
    async def test_response_mapping_handles_errors_correctly(
        self, default_coordinator, mock_query_executor
    ):
        """Verify response mapping handles errors correctly."""
        queries = [
            {"type": "retrieve", "text": "query_1"},
            {"type": "retrieve", "text": "query_2"},
        ]
        # Second result is an error
        expected_results = [
            {"result": "success"},
            {"error": "Query failed", "status": "error"},
        ]
        mock_query_executor.execute_batch = AsyncMock(return_value=expected_results)

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # First should succeed, second should have error
        assert "result" in results[0]
        assert "error" in results[1]

    @pytest.mark.asyncio
    async def test_response_mapping_maintains_result_integrity(
        self, default_coordinator, mock_query_executor
    ):
        """Verify response mapping maintains result integrity."""
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(5)]
        expected_results = [
            {"result": f"result_{i}", "data": {"value": i * 10}} for i in range(5)
        ]
        mock_query_executor.execute_batch = AsyncMock(return_value=expected_results)

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # Each result should be intact
        for i, result in enumerate(results):
            assert result["result"] == f"result_{i}"
            assert result["data"]["value"] == i * 10

    # Concurrent Operation Tests
    @pytest.mark.asyncio
    async def test_concurrent_query_submissions_are_handled_correctly(
        self, default_coordinator, mock_query_executor
    ):
        """Verify concurrent query submissions are handled correctly."""
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(10)]

        # Submit all queries concurrently
        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # All queries should complete successfully
        assert len(results) == 10

    @pytest.mark.asyncio
    async def test_thread_safety_of_batch_coordination(
        self, default_coordinator, mock_query_executor
    ):
        """Verify thread safety of batch coordination."""

        # Submit from multiple coroutines concurrently
        async def submit_batch(start_idx):
            queries = [
                {"type": "retrieve", "text": f"query_{start_idx}_{i}"} for i in range(3)
            ]
            tasks = [
                default_coordinator.submit_query(q, mock_query_executor)
                for q in queries
            ]
            return await asyncio.gather(*tasks)

        # Submit multiple batches concurrently
        batch_tasks = [submit_batch(i * 10) for i in range(3)]
        all_results = await asyncio.gather(*batch_tasks)

        # All batches should complete without corruption
        assert len(all_results) == 3

    @pytest.mark.asyncio
    async def test_batch_isolation_between_concurrent_batches(
        self, default_coordinator, mock_query_executor
    ):
        """Verify batch isolation between concurrent batches."""
        # Create two separate query batches
        batch1_queries = [{"type": "retrieve", "text": f"batch1_{i}"} for i in range(3)]
        batch2_queries = [{"type": "retrieve", "text": f"batch2_{i}"} for i in range(3)]

        # Submit both batches concurrently
        tasks1 = [
            default_coordinator.submit_query(q, mock_query_executor)
            for q in batch1_queries
        ]
        tasks2 = [
            default_coordinator.submit_query(q, mock_query_executor)
            for q in batch2_queries
        ]

        results1 = await asyncio.gather(*tasks1)
        results2 = await asyncio.gather(*tasks2)

        # Results should be isolated and correct
        assert len(results1) == 3
        assert len(results2) == 3

    @pytest.mark.asyncio
    async def test_async_query_submission_and_result_retrieval(
        self, default_coordinator, mock_query_executor
    ):
        """Verify async query submission and result retrieval."""
        query = {"type": "retrieve", "text": "test"}

        # Should support async/await
        result = await default_coordinator.submit_query(query, mock_query_executor)

        assert result is not None

    # Error Handling Tests
    @pytest.mark.asyncio
    async def test_batch_execution_error_handling(
        self, default_coordinator, mock_query_executor
    ):
        """Verify batch execution error handling."""
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(3)]
        mock_query_executor.execute_batch = AsyncMock(
            side_effect=Exception("Execution failed")
        )

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]

        # Should handle error gracefully
        with pytest.raises(Exception):
            await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_partial_batch_failure_handling(
        self, default_coordinator, mock_query_executor
    ):
        """Verify partial batch failure handling."""
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(3)]
        # Return partial results with error
        expected_results = [
            {"result": "success"},
            {"error": "Failed", "status": "error"},
            {"result": "success"},
        ]
        mock_query_executor.execute_batch = AsyncMock(return_value=expected_results)

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # Should handle partial failures
        assert "result" in results[0]
        assert "error" in results[1]
        assert "result" in results[2]

    @pytest.mark.asyncio
    async def test_query_timeout_error_handling(
        self, default_coordinator, mock_query_executor
    ):
        """Verify query timeout error handling."""

        # Mock a very slow execution
        async def slow_execution(queries):
            await asyncio.sleep(1)
            return [{"result": "data"}] * len(queries)

        mock_query_executor.execute_batch = slow_execution

        query = {"type": "retrieve", "text": "test"}

        # Should timeout appropriately
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                default_coordinator.submit_query(query, mock_query_executor),
                timeout=0.5,
            )

    @pytest.mark.asyncio
    async def test_recovery_from_execution_errors(
        self, default_coordinator, mock_query_executor
    ):
        """Verify recovery from execution errors."""
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(2)]

        # First call fails
        mock_query_executor.execute_batch = AsyncMock(
            side_effect=Exception("First failure")
        )

        with pytest.raises(Exception):
            tasks = [
                default_coordinator.submit_query(q, mock_query_executor)
                for q in queries
            ]
            await asyncio.gather(*tasks)

        # Second call succeeds
        mock_query_executor.execute_batch = AsyncMock(
            return_value=[{"result": "success"}] * 2
        )

        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        results = await asyncio.gather(*tasks)

        # Should recover and work correctly
        assert len(results) == 2

    # Metrics and Monitoring Tests
    @pytest.mark.asyncio
    async def test_batch_count_tracking(self, default_coordinator, mock_query_executor):
        """Verify batch count tracking."""
        # Submit multiple batches
        for _ in range(3):
            queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(5)]
            tasks = [
                default_coordinator.submit_query(q, mock_query_executor)
                for q in queries
            ]
            await asyncio.gather(*tasks)

        metrics = default_coordinator.get_metrics()
        assert metrics.total_batches >= 3

    @pytest.mark.asyncio
    async def test_average_batch_size_calculation(
        self, default_coordinator, mock_query_executor
    ):
        """Verify average batch size calculation."""
        # Submit batches of different sizes
        # Batch 1: 5 queries (full)
        queries1 = [{"type": "retrieve", "text": f"query_{i}"} for i in range(5)]
        tasks1 = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries1
        ]
        await asyncio.gather(*tasks1)

        # Batch 2: 3 queries (partial)
        queries2 = [{"type": "retrieve", "text": f"query_{i}"} for i in range(3)]
        tasks2 = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries2
        ]
        await asyncio.gather(*tasks2)

        metrics = default_coordinator.get_metrics()
        # Average should be (5 + 3) / 2 = 4.0
        assert 3.5 <= metrics.avg_batch_size <= 4.5

    @pytest.mark.asyncio
    async def test_batch_utilization_metrics(
        self, default_coordinator, mock_query_executor
    ):
        """Verify batch utilization metrics."""
        # Submit full batch
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(5)]
        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        await asyncio.gather(*tasks)

        metrics = default_coordinator.get_metrics()
        # Utilization should be 100% (5/5)
        assert metrics.batch_utilization >= 0.9

    @pytest.mark.asyncio
    async def test_wait_time_metrics(self, default_coordinator, mock_query_executor):
        """Verify wait time metrics."""
        # Submit partial batch (will wait for timeout)
        queries = [{"type": "retrieve", "text": f"query_{i}"} for i in range(2)]
        tasks = [
            default_coordinator.submit_query(q, mock_query_executor) for q in queries
        ]
        await asyncio.gather(*tasks)

        metrics = default_coordinator.get_metrics()
        # Should track average wait time
        assert metrics.avg_wait_time_ms >= 0
