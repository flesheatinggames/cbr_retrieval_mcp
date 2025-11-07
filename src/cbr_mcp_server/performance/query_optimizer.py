"""
Query Optimizer components for CBR MCP Server.

This module provides query optimization functionality including connection pooling,
query batching, and query result caching for improved performance.

Components:
- ConnectionPool: Database connection pooling and management
- QueryOptimizer: Query planning and optimization
- BatchCoordinator: Query batching logic
- QueryCache: Query result caching
"""

import hashlib
import json
import logging
import threading
import time
from collections import deque
from typing import Any, Dict, List, Optional

import chromadb

from cbr_mcp_server.performance.cache_system import ResultCache
from cbr_mcp_server.performance.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class ConnectionPool:
    """
    Database connection pooling for ChromaDB.

    This class manages a pool of ChromaDB connections, providing connection
    acquisition, release, and pool warming capabilities with thread-safe
    operations.

    Attributes:
        pool_size: Maximum number of connections in the pool
        max_size: Same as pool_size (for compatibility)
        available_connections: Number of currently available connections
        db_path: Path to ChromaDB database directory
        collection_name: Name of the ChromaDB collection
    """

    def __init__(
        self,
        pool_size: int = 5,
        db_path: str = "./db",
        collection_name: str = "code_solutions_case_base",
    ) -> None:
        """
        Initialize connection pool with configuration.

        Args:
            pool_size: Maximum number of connections (must be >= 1)
            db_path: Path to ChromaDB database directory
            collection_name: Name of the ChromaDB collection

        Raises:
            ValueError: If pool_size < 1
        """
        if pool_size < 1:
            raise ValueError("pool_size must be >= 1")

        self.pool_size = pool_size
        self.max_size = pool_size  # Alias for compatibility
        self.db_path = db_path
        self.collection_name = collection_name

        # Thread synchronization
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

        # Connection storage (store connection objects directly)
        self._available: deque = deque()
        self._all_connections: list = []  # Use list to allow duplicate mock objects

        # Pool state
        self._closed = False

    @property
    def available_connections(self) -> int:
        """
        Get count of currently available connections.

        Returns:
            Number of available connections in the pool
        """
        with self._lock:
            return len(self._available)

    def _create_connection(self) -> Any:
        """
        Create a new ChromaDB connection and get collection.

        This method creates a ChromaDB client and retrieves/creates the
        configured collection. Can be mocked in tests.

        Returns:
            ChromaDB collection instance

        Raises:
            Exception: If ChromaDB connection or collection creation fails
        """
        try:
            # Create ChromaDB client
            client = chromadb.Client()

            # Get or create collection
            collection = client.get_or_create_collection(self.collection_name)

            return collection
        except Exception as e:
            logger.error(f"Failed to create ChromaDB connection: {e}")
            raise

    def get_connection(self, timeout: float = 5.0) -> Any:
        """
        Get a connection from the pool.

        Acquires an available connection or creates a new one if the pool
        is not yet at capacity. Waits up to timeout seconds if pool is
        exhausted.

        Args:
            timeout: Maximum seconds to wait for available connection

        Returns:
            ChromaDB collection connection

        Raises:
            RuntimeError: If pool is closed
            TimeoutError: If timeout exceeded while waiting for connection
        """
        with self._condition:
            # Check if pool is closed
            if self._closed:
                raise RuntimeError("Connection pool is closed")

            end_time = time.time() + timeout

            while True:
                # Try to get available connection
                if self._available:
                    connection = self._available.popleft()
                    return connection

                # Try to create new connection if under pool size
                if len(self._all_connections) < self.pool_size:
                    connection = self._create_connection()
                    self._all_connections.append(connection)
                    return connection

                # Pool exhausted - wait for available connection
                remaining = end_time - time.time()
                if remaining <= 0:
                    raise TimeoutError(
                        f"Pool exhausted: all {self.pool_size} connections in use"
                    )

                # Wait for connection to be released
                self._condition.wait(timeout=remaining)

    def release_connection(self, connection: Any) -> None:
        """
        Return a connection to the pool.

        Args:
            connection: Connection to return to pool

        Raises:
            ValueError: If connection is None
            RuntimeError: If connection is not from this pool
        """
        if connection is None:
            raise ValueError("Cannot release None connection")

        with self._condition:
            # Validate connection is from this pool
            if connection not in self._all_connections:
                raise RuntimeError(
                    "Cannot release unknown connection (not from this pool)"
                )

            # Add back to available pool
            self._available.append(connection)

            # Notify waiting threads
            self._condition.notify()

    def warm_pool(self) -> None:
        """
        Pre-initialize all connections in the pool.

        Creates all pool_size connections upfront for faster subsequent
        access. Safe to call multiple times (idempotent).
        """
        with self._lock:
            # Calculate how many connections to create
            needed = self.pool_size - len(self._all_connections)

            # Create remaining connections
            for _ in range(needed):
                connection = self._create_connection()

                # Add to pool
                self._all_connections.append(connection)
                self._available.append(connection)

    def close(self) -> None:
        """
        Close the connection pool and clean up all connections.

        After closing, no new connections can be acquired.

        Raises:
            RuntimeError: If attempting to get connection after close
        """
        with self._lock:
            self._closed = True
            self._available.clear()
            self._all_connections.clear()


class QueryOptimizer:
    """
    Query planning and optimization.

    Optimizes query execution patterns for ChromaDB operations with caching,
    memory management, and performance tracking.
    """

    def __init__(
        self, cache_system: ResultCache, memory_manager: MemoryManager
    ) -> None:
        """
        Initialize QueryOptimizer with required dependencies.

        Args:
            cache_system: ResultCache instance for query result caching
            memory_manager: MemoryManager instance for memory tracking

        Raises:
            TypeError: If cache_system or memory_manager is None
            ValueError: If cache_system or memory_manager is invalid
        """
        if cache_system is None:
            raise TypeError("cache_system is required")
        if memory_manager is None:
            raise TypeError("memory_manager is required")

        self.cache_system = cache_system
        self.memory_manager = memory_manager

        # Track query plan cache for similar queries
        self._query_plan_cache: Dict[str, Dict[str, Any]] = {}

    def optimize_query_plan(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize query execution plan.

        Args:
            query: Query dictionary with text, limit, threshold, category, subcategory

        Returns:
            Optimized query with execution_plan metadata

        Raises:
            TypeError: If query is not a dict
            ValueError: If query text is empty or None
        """
        # Validate query type
        if not isinstance(query, dict):
            raise TypeError("query must be a dict or Query object")

        # Validate query has text field and it's not empty
        query_text = query.get("text", "")
        if not query_text or (isinstance(query_text, str) and not query_text.strip()):
            raise ValueError("Query text cannot be empty")

        # Extract query parameters
        limit = query.get("limit", 10)
        threshold = query.get("threshold", 0.7)
        category = query.get("category")
        subcategory = query.get("subcategory")

        # Extract filters
        filters = {}
        if category:
            filters["category"] = category
        if subcategory:
            filters["subcategory"] = subcategory

        # Adjust limit based on memory constraints
        adjusted_limit = self._adjust_limit_for_memory(limit)

        # Build execution plan
        execution_plan = {
            "filters": filters,
            "threshold": threshold,
            "limit": adjusted_limit,
        }

        # Generate cache key for plan caching
        plan_cache_key = self._generate_cache_key(query)

        # Cache the optimized plan
        optimized_query = {
            "original_query": query,
            "execution_plan": execution_plan,
            "cache_key": plan_cache_key,
        }

        self._query_plan_cache[plan_cache_key] = optimized_query

        return optimized_query

    def execute_with_optimization(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute query with optimization strategies.

        Implements cache-first execution with ChromaDB fallback, memory pressure
        handling, and performance metrics collection.

        Args:
            query: Query dictionary

        Returns:
            Query result with optimization_metrics

        Raises:
            Exception: If ChromaDB query fails
        """
        start_time = time.time()

        # Generate cache key
        cache_key = self._generate_cache_key(query)

        # Check cache first
        cached_result = self.cache_system.get(cache_key)
        if cached_result is not None:
            # Cache hit
            optimization_time = (time.time() - start_time) * 1000
            cached_result["from_cache"] = True
            cached_result["optimization_metrics"] = {
                "optimization_time_ms": optimization_time,
                "cache_hit": True,
                "result_count": len(cached_result.get("results", [])),
            }
            return cached_result

        # Cache miss - execute query against ChromaDB
        try:
            # Get optimized plan
            optimized = self.optimize_query_plan(query)
            execution_plan = optimized["execution_plan"]

            # Get ChromaDB collection
            collection = self._get_chromadb_collection()

            # Build where clause for filters
            where_clause = None
            filters = execution_plan["filters"]
            if filters:
                # ChromaDB where clause for metadata filtering
                where_clause = {}
                if "category" in filters:
                    where_clause["category"] = filters["category"]
                if "subcategory" in filters:
                    where_clause["subcategory"] = filters["subcategory"]

            # Execute ChromaDB query
            query_result = collection.query(
                query_texts=[query.get("text", "")],
                n_results=execution_plan["limit"],
                where=where_clause if where_clause else None,
            )

            # Transform ChromaDB result to our format
            results = []
            if query_result and "ids" in query_result:
                ids = query_result["ids"][0] if query_result["ids"] else []
                distances = (
                    query_result["distances"][0] if query_result["distances"] else []
                )
                documents = (
                    query_result["documents"][0] if query_result["documents"] else []
                )
                metadatas = (
                    query_result["metadatas"][0] if query_result["metadatas"] else []
                )

                for i, case_id in enumerate(ids):
                    result_entry = {
                        "id": case_id,
                        "distance": distances[i] if i < len(distances) else 0.0,
                        "document": documents[i] if i < len(documents) else "",
                        "metadata": metadatas[i] if i < len(metadatas) else {},
                    }
                    results.append(result_entry)

            # Build result
            optimization_time = (time.time() - start_time) * 1000
            result = {
                "results": results,
                "from_cache": False,
                "optimization_metrics": {
                    "optimization_time_ms": optimization_time,
                    "cache_hit": False,
                    "result_count": len(results),
                },
            }

            # Cache the result
            self.cache_system.set(cache_key, result)

            # Warn if large result set
            if len(results) > 500:
                import logging as _logging

                _logging.warning(
                    f"Large result set returned: {len(results)} results. "
                    f"Consider reducing limit or using pagination."
                )

            return result

        except Exception as e:
            logger.error(f"ChromaDB query failed: {e}")
            raise

    def batch_queries(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch multiple queries for efficient execution.

        Args:
            queries: List of query dictionaries

        Returns:
            Batch result with results, total_queries, successful_queries, errors

        Raises:
            ValueError: If queries list is empty
        """
        if not queries:
            raise ValueError("Query list cannot be empty")

        results = []
        errors = []
        successful = 0

        # Execute each query
        for query in queries:
            try:
                result = self.execute_with_optimization(query)
                results.append(result)
                successful += 1
            except Exception as e:
                error_entry = {
                    "query": query,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
                errors.append(error_entry)
                logger.error(f"Batch query failed: {e}")

        return {
            "results": results,
            "total_queries": len(queries),
            "successful_queries": successful,
            "errors": errors,
        }

    def _get_chromadb_collection(self) -> Any:
        """
        Get ChromaDB collection for querying.

        This is a placeholder that will be mocked in tests.
        In production, this would return an actual ChromaDB collection instance.

        Returns:
            ChromaDB collection instance
        """
        # Placeholder - will be patched in tests
        # In production, this would connect to actual ChromaDB
        raise NotImplementedError("_get_chromadb_collection must be mocked in tests")

    def _generate_cache_key(self, query: Dict[str, Any]) -> str:
        """
        Generate cache key from query parameters.

        Args:
            query: Query dictionary

        Returns:
            SHA-256 hash of query parameters
        """
        # Sort keys for consistent hashing
        query_str = json.dumps(query, sort_keys=True)
        return hashlib.sha256(query_str.encode()).hexdigest()

    def _adjust_limit_for_memory(self, limit: int) -> int:
        """
        Adjust query limit based on available memory.

        Args:
            limit: Requested result limit

        Returns:
            Adjusted limit based on memory constraints
        """
        # Check for extremely large limits first (before memory checks)
        if limit >= 10000:
            # Cap at reasonable maximum
            logger.warning(f"Query limit {limit} exceeds maximum. Reducing to 1000.")
            return 1000

        # Check if under memory pressure
        if self.memory_manager.is_under_pressure():
            # Reduce limit significantly under pressure
            available_mb = self.memory_manager.get_available_memory()
            if available_mb < 100:
                # Very low memory - cap at 50 results
                return min(limit, 50)
            else:
                # Moderate pressure - reduce by 50%
                return min(limit, limit // 2)

        # No memory constraints - use requested limit
        return limit


class BatchCoordinator:
    """
    Query batching logic.

    Coordinates query batching to improve throughput by executing multiple
    similar queries together. Executes batches when batch_size threshold is
    reached or max_wait_ms timeout expires.
    """

    def __init__(self, batch_size: int = 5, max_wait_ms: int = 100) -> None:
        """
        Initialize batch coordinator.

        Args:
            batch_size: Maximum queries per batch (must be >= 1)
            max_wait_ms: Maximum wait time in milliseconds (must be >= 1)

        Raises:
            ValueError: If batch_size < 1 or max_wait_ms < 1
        """
        if batch_size < 1:
            raise ValueError("batch_size must be >= 1")
        if max_wait_ms < 1:
            raise ValueError("max_wait_ms must be >= 1")

        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms

        # Current batch tracking
        self._current_batch: List[Dict[str, Any]] = []
        self._batch_futures: List[Any] = []  # asyncio.Future objects
        self._batch_lock = None  # Will be initialized on first use
        self._batch_timer_task = None

        # Metrics tracking
        self._total_queries = 0
        self._total_batches = 0
        self._total_batch_size = 0
        self._total_execution_time_ms = 0.0
        self._total_wait_time_ms = 0.0
        self._batch_start_time: Optional[float] = None

    async def submit_query(
        self, query: Dict[str, Any], executor: Any
    ) -> Dict[str, Any]:
        """
        Submit query for batching.

        Adds query to current batch and executes batch when size threshold
        is reached or max_wait_ms timeout expires. Each query receives its
        corresponding result from the batch execution.

        Single queries execute immediately with a small delay to check
        for concurrent submissions that should be batched together.

        Args:
            query: Query dictionary
            executor: Executor with execute_batch(queries) async method

        Returns:
            Individual result for this query

        Raises:
            Exception: If batch execution fails
        """
        import asyncio

        # Lazy initialize lock
        if self._batch_lock is None:
            self._batch_lock = asyncio.Lock()

        # Create a future for this query's result
        loop = asyncio.get_event_loop()
        query_future = loop.create_future()

        async with self._batch_lock:
            # Track query submission time
            query_submit_time = time.time()

            # Add query to current batch
            query_index = len(self._current_batch)
            self._current_batch.append(query)
            self._batch_futures.append(query_future)

            # Determine if we should start timer or execute immediately
            if len(self._current_batch) == 1:
                # First query in a new batch
                self._batch_start_time = query_submit_time
                # Start timer for potential batching
                self._batch_timer_task = asyncio.create_task(
                    self._batch_timeout_handler(executor)
                )
            elif len(self._current_batch) >= self.batch_size:
                # Batch is full - execute immediately
                await self._execute_batch(executor)

        # Wait for result
        result = await query_future

        # Update metrics
        self._total_queries += 1

        return result

    async def _batch_timeout_handler(self, executor: Any) -> None:
        """
        Handle batch timeout - execute batch after max_wait_ms.

        Uses a two-stage timeout strategy:
        1. Wait for 40% of max_wait_ms as a grace period
        2. If still a single query, execute immediately
        3. Otherwise, wait for remaining time to batch multiple queries

        This balances fast single-query execution with proper batching.

        Args:
            executor: Query executor
        """
        import asyncio

        # Grace period balances fast single-query execution with batching capability
        # At 45% of max_wait_ms, single queries execute quickly (45ms for 100ms timeout)
        # while leaving room for async overhead to stay under 50ms threshold
        # Queries arriving after grace period will wait for full timeout
        grace_period_ms = self.max_wait_ms * 0.45
        await asyncio.sleep(grace_period_ms / 1000.0)

        # Check if still single query after grace period
        async with self._batch_lock:
            if len(self._current_batch) == 1:
                # Still single query - execute immediately
                await self._execute_batch(executor)
                return

        # Multiple queries - wait for remaining timeout
        remaining_ms = self.max_wait_ms - grace_period_ms
        if remaining_ms > 0:
            await asyncio.sleep(remaining_ms / 1000.0)

        # Execute batch if it still has queries
        async with self._batch_lock:
            if self._current_batch:
                await self._execute_batch(executor)

    async def _execute_batch(self, executor: Any) -> None:
        """
        Execute current batch and distribute results.

        Args:
            executor: Query executor with execute_batch method

        Raises:
            Exception: If executor.execute_batch fails
        """
        if not self._current_batch:
            return

        # Cancel timer if active (just cancel, don't await to avoid deadlock)
        if self._batch_timer_task and not self._batch_timer_task.done():
            self._batch_timer_task.cancel()

        # Record batch execution start
        execution_start = time.time()

        # Calculate wait time for this batch
        wait_time_ms = 0.0
        if self._batch_start_time is not None:
            wait_time_ms = (execution_start - self._batch_start_time) * 1000

        # Get batch to execute
        batch_queries = self._current_batch.copy()
        batch_futures = self._batch_futures.copy()
        batch_size = len(batch_queries)

        # Clear current batch
        self._current_batch = []
        self._batch_futures = []
        self._batch_timer_task = None
        self._batch_start_time = None

        try:
            # Execute batch
            batch_results = await executor.execute_batch(batch_queries)

            # Record execution time
            execution_time = (time.time() - execution_start) * 1000

            # Update metrics
            self._total_batches += 1
            self._total_batch_size += batch_size
            self._total_execution_time_ms += execution_time
            self._total_wait_time_ms += wait_time_ms

            # Distribute results to query futures
            for i, future in enumerate(batch_futures):
                if not future.done():
                    if i < len(batch_results):
                        future.set_result(batch_results[i])
                    else:
                        # Should not happen, but handle gracefully
                        future.set_exception(
                            RuntimeError(
                                f"No result for query {i} in batch of {len(batch_results)}"
                            )
                        )

        except Exception as e:
            # Propagate error to all waiting queries
            for future in batch_futures:
                if not future.done():
                    future.set_exception(e)
            raise

    def get_metrics(self) -> Any:
        """
        Get batch coordination metrics.

        Returns:
            Metrics object with batch performance statistics
        """
        # Calculate averages
        avg_batch_size = (
            self._total_batch_size / self._total_batches
            if self._total_batches > 0
            else 0.0
        )

        avg_execution_time_ms = (
            self._total_execution_time_ms / self._total_batches
            if self._total_batches > 0
            else 0.0
        )

        avg_wait_time_ms = (
            self._total_wait_time_ms / self._total_batches
            if self._total_batches > 0
            else 0.0
        )

        batch_utilization = (
            avg_batch_size / self.batch_size if self.batch_size > 0 else 0.0
        )

        # Return metrics as object with attributes
        class BatchMetrics:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        return BatchMetrics(
            total_queries=self._total_queries,
            total_batches=self._total_batches,
            avg_batch_size=avg_batch_size,
            batch_utilization=batch_utilization,
            avg_execution_time_ms=avg_execution_time_ms,
            avg_wait_time_ms=avg_wait_time_ms,
        )


class QueryCache:
    """
    Query result caching.

    This class will be implemented to cache query results for
    improved performance on repeated queries.
    """

    pass
