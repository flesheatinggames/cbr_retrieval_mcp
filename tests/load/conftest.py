"""
Pytest configuration for load and stress tests.

This conftest provides session-scoped fixtures for load testing to prevent
memory regression from multiple model/retriever instances.

Load tests use mock fixtures (like benchmarks) to test infrastructure performance
without the memory overhead of real embedding models (~630MB) and ChromaDB (~690MB).
"""

import gc
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import numpy as np
import pytest


# ============================================================================
# Mock Fixtures for Load Testing (Same as Benchmarks)
# ============================================================================
# Load tests use mocks to avoid the ~1.3GB memory overhead of real models,
# allowing us to test the infrastructure's memory efficiency (<500MB target)


@pytest.fixture(scope="function")
def mock_chromadb() -> Any:
    """
    Mock ChromaDB for load testing.

    Prevents loading real ChromaDB (~690MB when initialized) so we can test
    the memory efficiency of the load testing infrastructure itself.

    IMPORTANT: This fixture is function-scoped to prevent contaminating other
    tests when running with pytest-xdist. Session-scoped patches can leak
    across tests on the same worker, causing intermittent failures.
    """
    with patch("chromadb.PersistentClient") as mock_client:
        mock_collection = Mock()
        mock_collection.get.return_value = {
            "ids": ["case_1", "case_2"],
            "metadatas": [{"category": "test"}, {"category": "test"}],
            "documents": ["doc1", "doc2"],
            "embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        }
        mock_collection.query.return_value = {
            "ids": [["case_1", "case_2"]],
            "distances": [[0.1, 0.2]],
            "metadatas": [[{"category": "test"}, {"category": "test"}]],
            "documents": [["doc1", "doc2"]],
        }
        mock_collection.count.return_value = 2
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        yield mock_client


@pytest.fixture(scope="function")
def mock_sentence_transformer() -> Any:
    """
    Mock SentenceTransformer for load testing.

    Prevents loading real embedding model (~630MB) so we can test
    the memory efficiency of the load testing infrastructure itself.

    IMPORTANT: This fixture is function-scoped to prevent contaminating other
    tests when running with pytest-xdist. Session-scoped patches can leak
    across tests on the same worker, causing intermittent failures.
    """
    with patch("sentence_transformers.SentenceTransformer") as mock_st:
        mock_instance = Mock()
        # Return standard 768-dimension embeddings
        mock_instance.encode.return_value = np.array([[0.1] * 768], dtype=np.float32)
        mock_st.return_value = mock_instance
        yield mock_st


# ============================================================================
# Real Component Fixtures (DEPRECATED - Use Mocks Instead)
# ============================================================================
# These fixtures load real components (~1.3GB) and should NOT be used for
# load tests. They're kept for backward compatibility but should be removed.


@pytest.fixture(scope="session")
def shared_embedding_model_REAL(request):
    """
    Session-scoped shared embedding model - ONE instance for entire test session.

    This fixture ensures only ONE embedding model exists in memory across all
    test modules, preventing memory regression from multiple model instances.

    Memory optimization: Reduces peak memory by ~700MB by sharing a single
    embedding model instance instead of creating one per test module.
    """
    try:
        from cbr_mcp_server.performance.production_cbr_retriever import (
            LazyEmbeddingModel,
        )
    except ImportError:
        pytest.skip("CBR server components not available")

    # Create ONE embedding model for entire session
    embedding_model = LazyEmbeddingModel(
        model_name="nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True
    )

    yield embedding_model

    # Cleanup: explicitly delete embedding model and force garbage collection
    del embedding_model
    gc.collect()


@pytest.fixture(scope="session")
def shared_cbr_retriever_REAL(request, shared_embedding_model_REAL):
    """
    DEPRECATED: Real CBR retriever with real embedding model (~1.3GB memory).

    DO NOT USE for load tests. This fixture loads real components and will
    cause load tests to fail the 500MB memory target. Use mocked retriever instead.

    Session-scoped shared CBR retriever - ONE instance for entire test session.

    This fixture uses the shared_embedding_model to ensure only ONE retriever
    with ONE embedding model exists in memory across all test modules.

    Memory optimization: Prevents duplicate retriever/model instances across
    test modules, reducing memory footprint by ~700MB.
    """
    try:
        from cbr_mcp_server.performance.production_cbr_retriever import (
            ProductionCBRRetriever,
        )
    except ImportError:
        pytest.skip("CBR server components not available")

    # Initialize retriever with shared embedding model and ISOLATED test database
    import tempfile
    import shutil
    test_db_path = tempfile.mkdtemp(prefix="load_test_db_")

    try:
        retriever = ProductionCBRRetriever(
            db_path=test_db_path, embedding_model=shared_embedding_model_REAL
        )

        # Trigger lazy initialization with a test query
        try:
            retriever.retrieve(query="test", max_results=1)
        except Exception as e:
            pytest.skip(f"Failed to initialize shared CBR retriever: {e}")

        yield retriever

    finally:
        # Cleanup: close retriever to release file descriptors
        try:
            retriever.close()
        except Exception:
            pass  # Best effort cleanup

        # explicitly delete retriever and force garbage collection
        del retriever
        gc.collect()

        # Cleanup temp database directory
        try:
            shutil.rmtree(test_db_path)
        except Exception:
            pass  # Best effort cleanup


@pytest.fixture(scope="function")
def shared_cbr_retriever(request, mock_chromadb, mock_sentence_transformer):
    """
    Function-scoped MOCKED CBR retriever for load testing.

    Uses mocks instead of real components to test infrastructure memory efficiency
    without the ~1.3GB overhead of real embedding models and ChromaDB.

    This allows load tests to verify that the infrastructure itself (LoadTestRunner,
    async operations, memory monitoring) stays under the 500MB target.

    CRITICAL: Does NOT create CBRMCPServer to avoid loading real ProductionCBRRetriever.
    Instead returns a lightweight mock that matches the retriever interface.

    IMPORTANT: This fixture is function-scoped to prevent contaminating other
    tests when running with pytest-xdist. Session-scoped mocks can leak
    across tests on the same worker, causing intermittent failures.
    """
    # DON'T import CBRMCPServer - it creates real ProductionCBRRetriever!
    # Just create a simple mock retriever directly

    class MockRetriever:
        """Lightweight mock retriever compatible with load test expectations."""

        def __init__(self):
            import time
            import random
            self.cache = Mock()
            # Start with no cache metrics
            self._cache_hits = 0
            self._cache_misses = 0
            self._query_cache = {}  # Simple in-memory cache for hit/miss simulation
            self._cache_max_size = 50  # Simulate cache size limit
            self._time = time
            self._random = random

            # Update cache.get_metrics to return current values
            self.cache.get_metrics = lambda: Mock(
                hits=self._cache_hits,
                misses=self._cache_misses
            )

            def clear_cache():
                self._query_cache.clear()
                self._cache_hits = 0
                self._cache_misses = 0

            self.cache.clear = clear_cache

        def retrieve(self, query: str, max_results: int = 5):
            """Mock retrieve method with cache hit/miss tracking and realistic latency."""
            # Simulate realistic query latency
            if query in self._query_cache:
                # Cache hit: faster latency (5-15ms)
                self._time.sleep(0.005 + self._random.random() * 0.01)
                self._cache_hits += 1
                return self._query_cache[query]
            else:
                # Cache miss: slower latency (40-120ms to simulate embedding + DB)
                self._time.sleep(0.04 + self._random.random() * 0.08)
                self._cache_misses += 1

            # Generate mock results
            results = []
            for i in range(max_results):
                results.append({
                    "id": f"case_{i}_{hash(query) % 1000}",
                    "content": f"Mock result {i} for query: {query}",
                    "metadata": {"category": "test", "score": 0.95 - (i * 0.05)},
                })

            # Simulate LRU cache eviction when cache is full
            if len(self._query_cache) >= self._cache_max_size:
                # Remove oldest entry (first item)
                oldest_key = next(iter(self._query_cache))
                del self._query_cache[oldest_key]

            # Cache the results
            self._query_cache[query] = results
            return results

    retriever = MockRetriever()

    yield retriever

    # Cleanup
    del retriever
    gc.collect()


@pytest.fixture
def cbr_retriever(shared_cbr_retriever):
    """
    Provides clean CBR retriever state for each test.

    Uses session-scoped shared_cbr_retriever for memory efficiency,
    but resets cache state before each test to ensure test isolation.

    This prevents test pollution where later tests inherit cache state
    from earlier tests, which causes incorrect cache hit rates and
    distorted performance metrics.
    """
    # Clear cache state before each test
    shared_cbr_retriever._query_cache.clear()
    shared_cbr_retriever._cache_hits = 0
    shared_cbr_retriever._cache_misses = 0

    # Reset memory tracking if present
    if hasattr(shared_cbr_retriever, "_memory_samples"):
        shared_cbr_retriever._memory_samples.clear()

    return shared_cbr_retriever
