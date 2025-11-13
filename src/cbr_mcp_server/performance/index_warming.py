"""
Index warming functionality for ChromaDB to improve first-query performance.

This module provides:
- WarmupConfig: Configuration for index warming
- WarmupStatus: Status tracking for warm-up operations
- IndexWarmer: Main class for managing index warming
- generate_warmup_queries: Generate diverse warm-up queries
- execute_warmup_query: Execute warm-up queries against ChromaDB
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class WarmupConfig:
    """Configuration for index warming."""

    num_queries: int = 5
    collections: Optional[List[str]] = None
    enabled: bool = True


@dataclass
class WarmupStatus:
    """Status information for warm-up operations."""

    is_warmed: bool
    warmed_collections: List[str]
    warmup_duration: float


class IndexWarmer:
    """Manages index warming for ChromaDB collections."""

    def __init__(self, client: Any, config: WarmupConfig):
        """
        Initialize the IndexWarmer.

        Args:
            client: ChromaDB client instance
            config: Warm-up configuration
        """
        self._client = client
        self._config = config
        self._is_warmed = False
        self._warmed_collections: List[str] = []
        self._collection_timings: Dict[str, float] = {}
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None
        self._completion_timestamp: Optional[float] = None

    def is_warmed(self) -> bool:
        """Check if warming has been completed."""
        return self._is_warmed

    def get_warmup_time(self) -> float:
        """Get total warmup duration in seconds."""
        if self._start_time is None or self._end_time is None:
            return 0.0
        return self._end_time - self._start_time

    def get_warmed_collections(self) -> List[str]:
        """Get list of warmed collection names."""
        return self._warmed_collections.copy()

    def get_completion_timestamp(self) -> float:
        """Get timestamp when warming completed."""
        if self._completion_timestamp is None:
            return 0.0
        return self._completion_timestamp

    def get_status(self) -> WarmupStatus:
        """Get current warmup status."""
        return WarmupStatus(
            is_warmed=self._is_warmed,
            warmed_collections=self.get_warmed_collections(),
            warmup_duration=self.get_warmup_time(),
        )

    def get_collection_timings(self) -> Dict[str, float]:
        """Get per-collection timing information."""
        return self._collection_timings.copy()

    async def warm_on_startup(self) -> None:
        """
        Warm up ChromaDB indexes on server startup.

        This method warms all configured collections to improve first-query performance.
        """
        if not self._config.enabled:
            logger.info("Index warming is disabled")
            return

        logger.info("Starting index warming")
        self._start_time = time.time()

        try:
            # Determine which collections to warm
            if self._config.collections is None:
                # No specific collections configured, get all from client
                all_collections = self._client.list_collections()
                collections_to_warm = [coll.name for coll in all_collections]
            else:
                # Use explicitly configured collections (empty list means no collections)
                collections_to_warm = self._config.collections

            # Warm each collection
            for collection_name in collections_to_warm:
                # Use perf_counter for per-collection timing to avoid conflicts with time.time() mocks
                coll_start = time.perf_counter()
                try:
                    await self.warm_collection(collection_name, track_timing=True)
                    # Track per-collection timing on success
                    self._collection_timings[collection_name] = (
                        time.perf_counter() - coll_start
                    )
                except Exception as e:
                    logging.warning(
                        f"Failed to warm collection '{collection_name}': {e}"
                    )
                    continue

            self._is_warmed = True
            self._end_time = time.time()
            self._completion_timestamp = self._end_time

            logger.info(f"Index warming completed in {self.get_warmup_time():.2f}s")

        except ConnectionError as e:
            logging.error(f"ChromaDB connection failed during warming: {e}")
            self._is_warmed = False
            self._end_time = time.time()
        except Exception as e:
            logging.error(f"Unexpected error during index warming: {e}")
            self._is_warmed = False
            self._end_time = time.time()

    async def warm_collection(
        self, collection_name: Optional[str], track_timing: bool = False
    ) -> None:
        """
        Warm a specific collection.

        Args:
            collection_name: Name of the collection to warm
            track_timing: Whether to track per-collection timing (stored externally)

        Raises:
            ValueError: If collection name is None or collection not found
        """
        if collection_name is None:
            raise ValueError("Collection name cannot be None")

        logger.info(f"Warming collection: {collection_name}")

        try:
            # Get collection from client (may raise ValueError if not found)
            collection = self._client.get_collection(name=collection_name)

            # Generate and execute warm-up queries
            queries = generate_warmup_queries(
                embedding_dim=768, num_queries=self._config.num_queries
            )

            for query in queries:
                await execute_warmup_query(collection, query)

            # Track completion
            if collection_name not in self._warmed_collections:
                self._warmed_collections.append(collection_name)

            logger.info(f"Collection '{collection_name}' warmed successfully")

        except ValueError as e:
            # Collection not found - log warning and re-raise
            logging.warning(f"Collection '{collection_name}' not found: {e}")
            raise


def generate_warmup_queries(
    embedding_dim: int, num_queries: int
) -> List[Dict[str, Any]]:
    """
    Generate diverse warm-up queries for ChromaDB.

    Args:
        embedding_dim: Dimensionality of embeddings
        num_queries: Number of queries to generate

    Returns:
        List of query dictionaries with query_embeddings and n_results

    Raises:
        ValueError: If parameters are invalid
    """
    if num_queries <= 0:
        raise ValueError("num_queries must be positive")

    if embedding_dim <= 0:
        raise ValueError("embedding_dim must be positive")

    queries = []
    for i in range(num_queries):
        # Generate random embedding for diversity
        query_embedding = np.random.randn(embedding_dim).tolist()

        # Vary n_results for different query patterns
        n_results = (i % 10) + 1  # Range 1-10

        queries.append({"query_embeddings": query_embedding, "n_results": n_results})

    return queries


async def execute_warmup_query(collection: Any, query: Dict[str, Any]) -> None:
    """
    Execute a warm-up query against a ChromaDB collection.

    Args:
        collection: ChromaDB collection instance
        query: Query dictionary with query_embeddings and n_results

    Note:
        Errors are logged but not raised to allow warming to continue.
    """
    try:
        # Execute the query
        result = collection.query(
            query_embeddings=[query["query_embeddings"]],
            n_results=query["n_results"],
        )
        # Handle both sync and async collections (for testing)
        if hasattr(result, "__await__"):
            await result
    except RuntimeError as e:
        logging.warning(f"Warmup query failed: {e}")
    except Exception as e:
        logging.warning(f"Unexpected error during warmup query: {e}")
