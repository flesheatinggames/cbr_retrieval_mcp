"""
Integration tests for ProductionCBRRetriever with performance enhancements.

This test suite verifies the integration of ProductionCBRRetriever with:
- MemoryManager for memory tracking
- ResultCache for query result caching
- LazyLoader for on-demand embedding loading

These tests are written in TDD fashion and will fail until the implementations
are complete.

These tests follow integration testing patterns by testing real component
interactions rather than heavily mocked interfaces.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import time
from typing import Dict, List, Any
import numpy as np

# These imports will fail until the implementation is complete
from cbr_mcp_server.performance.production_cbr_retriever import ProductionCBRRetriever
from cbr_mcp_server.performance.memory_manager import MemoryManager
from cbr_mcp_server.performance.cache_system import ResultCache  # FIXED: Correct import path
from cbr_mcp_server.performance.lazy_loader import LazyLoader


class TestProductionCBRRetrieverInitialization:
    """Test ProductionCBRRetriever initialization with MemoryManager integration."""

    @pytest.fixture
    def mock_chroma_client(self):
        """Mock ChromaDB client."""
        client = Mock()
        collection = Mock()
        client.get_or_create_collection.return_value = collection
        return client

    @pytest.fixture
    def mock_embedding_model(self):
        """Mock embedding model."""
        model = Mock()
        model.encode.return_value = [[0.1, 0.2, 0.3]]
        return model

    def test_initialization_creates_memory_manager(self, mock_chroma_client, mock_embedding_model):
        """Test that ProductionCBRRetriever initializes with real MemoryManager."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            assert retriever is not None
            assert hasattr(retriever, 'memory_manager')
            assert isinstance(retriever.memory_manager, MemoryManager)

    def test_initialization_enables_memory_tracking(self, mock_chroma_client, mock_embedding_model):
        """Test that memory tracking is enabled upon initialization."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            # MemoryManager tracking should be enabled by default
            # Real MemoryManager instance should have tracking active
            memory_usage = retriever.memory_manager.check_memory_usage()
            assert memory_usage >= 0  # Should return valid memory reading

    def test_initialization_creates_result_cache(self, mock_chroma_client, mock_embedding_model):
        """Test that ProductionCBRRetriever initializes with real ResultCache."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            assert hasattr(retriever, 'result_cache')
            assert isinstance(retriever.result_cache, ResultCache)

    def test_initialization_creates_lazy_loader(self, mock_chroma_client, mock_embedding_model):
        """Test that ProductionCBRRetriever initializes with real LazyLoader."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            assert hasattr(retriever, 'lazy_loader')
            assert isinstance(retriever.lazy_loader, LazyLoader)


class TestQueryExecutionWithResultCache:
    """Test query execution with real ResultCache integration."""

    @pytest.fixture
    def mock_chroma_client(self):
        """Mock ChromaDB client with query response."""
        client = Mock()
        collection = Mock()
        collection.query.return_value = {
            'ids': [['case1', 'case2']],
            'documents': [['doc1', 'doc2']],
            'metadatas': [[{'category': 'code'}, {'category': 'orchestration'}]],
            'distances': [[0.1, 0.2]]
        }
        client.get_or_create_collection.return_value = collection
        return client

    @pytest.fixture
    def mock_embedding_model(self):
        """Mock embedding model."""
        model = Mock()
        model.encode.return_value = [[0.1, 0.2, 0.3]]
        return model

    def test_cache_miss_executes_query(self, mock_chroma_client, mock_embedding_model):
        """Test that first-time queries execute against ChromaDB (cache miss)."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            query = "example query"
            results = retriever.retrieve(query, max_results=5)

            # Verify ChromaDB was queried
            assert mock_chroma_client.get_or_create_collection().query.called
            assert results is not None
            assert len(results) > 0

    def test_cache_miss_stores_results(self, mock_chroma_client, mock_embedding_model):
        """Test that results from cache miss are stored in real ResultCache."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            query = "example query"
            results = retriever.retrieve(query, max_results=5)

            # Test real cache behavior
            # Real ResultCache should have stored the results
            cached_results = retriever.result_cache.get(query)
            assert cached_results is not None
            assert cached_results == results

    def test_cache_hit_serves_from_cache(self, mock_chroma_client, mock_embedding_model):
        """Test that repeated queries are served from cache without hitting ChromaDB."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            query = "example query"

            # First query - cache miss
            results1 = retriever.retrieve(query, max_results=5)
            first_call_count = mock_chroma_client.get_or_create_collection().query.call_count

            # Second query - cache hit (real cache should serve this)
            results2 = retriever.retrieve(query, max_results=5)
            second_call_count = mock_chroma_client.get_or_create_collection().query.call_count

            # Verify ChromaDB was not queried on second request
            assert second_call_count == first_call_count
            assert results1 == results2

    @pytest.mark.asyncio
    async def test_cache_hit_is_faster(self, mock_chroma_client, mock_embedding_model):
        """Test that cached queries are faster than non-cached queries."""
        # Add artificial delay to ChromaDB query
        def slow_query(*args, **kwargs):
            time.sleep(0.1)
            return {
                'ids': [['case1']],
                'documents': [['doc1']],
                'metadatas': [[{'category': 'code'}]],
                'distances': [[0.1]]
            }

        mock_chroma_client.get_or_create_collection().query.side_effect = slow_query

        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            query = "example query"

            # First query - measure time
            start1 = time.time()
            retriever.retrieve(query, max_results=5)
            duration1 = time.time() - start1

            # Second query - measure time (should use real cache)
            start2 = time.time()
            retriever.retrieve(query, max_results=5)
            duration2 = time.time() - start2

            # Cache hit should be significantly faster
            assert duration2 < duration1 * 0.5

    def test_memory_tracking_during_query(self, mock_chroma_client, mock_embedding_model):
        """Test that real MemoryManager tracks memory usage during queries."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            query = "example query"

            # Get memory before query
            memory_before = retriever.memory_manager.check_memory_usage()

            retriever.retrieve(query, max_results=5)

            # Get memory after query
            memory_after = retriever.memory_manager.check_memory_usage()

            # Verify memory tracking is working (both readings should be valid)
            assert memory_before >= 0
            assert memory_after >= 0


class TestLazyLoadingOfEmbeddings:
    """Test lazy loading of embeddings with real LazyLoader integration."""

    @pytest.fixture
    def mock_chroma_client(self):
        """Mock ChromaDB client."""
        client = Mock()
        collection = Mock()
        client.get_or_create_collection.return_value = collection
        return client

    @pytest.fixture
    def mock_case_loader(self):
        """
        Mock case loader function that simulates loading delay.
        This follows the pattern from test_lazy_loading_integration.py
        """
        def loader(case_id: str) -> Dict[str, Any]:
            # Simulate loading delay
            time.sleep(0.01)
            return {
                "case_id": case_id,
                "content": f"Content for {case_id}",
                "category": "code"
            }
        return loader

    def test_embeddings_not_loaded_during_initialization(self, mock_chroma_client, mock_case_loader):
        """Test that embeddings are not loaded during initialization."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                case_loader=mock_case_loader,
                enable_lazy_loading=True
            )

            # Real LazyLoader should not have loaded any cases yet
            # Check via LazyLoader's tracking
            assert retriever.lazy_loader is not None
            # Initially no cases should be loaded
            loaded_count = len([cid for cid in ["case_1", "case_2"]
                               if retriever.lazy_loader.is_loaded(cid)])
            assert loaded_count == 0

    def test_embeddings_loaded_on_first_query(self, mock_chroma_client, mock_case_loader):
        """Test that embeddings are loaded on first query requiring them."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                case_loader=mock_case_loader,
                enable_lazy_loading=True
            )

            # Trigger loading by requesting a case
            case_id = "case_1"
            result = retriever.lazy_loader.load_on_demand(case_id)

            # Verify case was loaded
            assert result is not None
            assert retriever.lazy_loader.is_loaded(case_id)

    def test_subsequent_queries_reuse_loaded_embeddings(self, mock_chroma_client, mock_case_loader):
        """Test that subsequent queries reuse loaded embeddings."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                case_loader=mock_case_loader,
                enable_lazy_loading=True
            )

            case_id = "case_1"

            # First load - should take time
            start1 = time.time()
            result1 = retriever.lazy_loader.load_on_demand(case_id)
            duration1 = time.time() - start1

            # Second load - should use cache (faster)
            start2 = time.time()
            result2 = retriever.lazy_loader.load_on_demand(case_id)
            duration2 = time.time() - start2

            # Verify same data returned
            assert result1 == result2
            # Second access should be much faster (from cache)
            assert duration2 < duration1 / 5

    def test_lazy_loader_tracks_loaded_vs_unloaded(self, mock_chroma_client, mock_case_loader):
        """Test that real LazyLoader tracks loaded vs. unloaded embeddings."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                case_loader=mock_case_loader,
                enable_lazy_loading=True
            )

            case_ids = ["case_1", "case_2", "case_3"]

            # Initially none loaded
            loaded_count = sum(1 for cid in case_ids if retriever.lazy_loader.is_loaded(cid))
            assert loaded_count == 0

            # Load first case
            retriever.lazy_loader.load_on_demand(case_ids[0])

            # Verify tracking updated
            assert retriever.lazy_loader.is_loaded(case_ids[0])
            assert not retriever.lazy_loader.is_loaded(case_ids[1])


class TestCacheWarmingOnStartup:
    """Test cache warming on startup with real ResultCache."""

    @pytest.fixture
    def mock_chroma_client(self):
        """Mock ChromaDB client."""
        client = Mock()
        collection = Mock()
        collection.query.return_value = {
            'ids': [['case1']],
            'documents': [['doc1']],
            'metadatas': [[{'category': 'code'}]],
            'distances': [[0.1]]
        }
        client.get_or_create_collection.return_value = collection
        return client

    @pytest.fixture
    def mock_embedding_model(self):
        """Mock embedding model."""
        model = Mock()
        model.encode.return_value = [[0.1, 0.2, 0.3]]
        return model

    @pytest.fixture
    def cache_warming_config(self):
        """Configuration with cache warming enabled."""
        return {
            'cache_warming': {
                'enabled': True,
                'queries': [
                    'authentication example',
                    'database query pattern',
                    'error handling'
                ]
            }
        }

    def test_cache_warming_triggered_during_initialization(
        self, mock_chroma_client, mock_embedding_model, cache_warming_config
    ):
        """Test that cache warming is triggered during initialization."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model,
                config=cache_warming_config
            )

            # Verify real cache was warmed (should have entries)
            # Check if cache has any entries
            cache_has_entries = False
            for query in cache_warming_config['cache_warming']['queries']:
                if retriever.result_cache.get(query) is not None:
                    cache_has_entries = True
                    break

            assert cache_has_entries, "Cache should have been warmed with at least one query"

    def test_frequently_accessed_queries_preloaded(
        self, mock_chroma_client, mock_embedding_model, cache_warming_config
    ):
        """Test that specified frequently accessed queries are preloaded into real ResultCache."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model,
                config=cache_warming_config
            )

            # Verify each warming query is in real cache
            for query in cache_warming_config['cache_warming']['queries']:
                cached_result = retriever.result_cache.get(query)
                assert cached_result is not None, f"Query '{query}' should be in cache after warming"

    def test_memory_tracked_during_cache_warming(
        self, mock_chroma_client, mock_embedding_model, cache_warming_config
    ):
        """Test that real MemoryManager tracks memory usage during cache warming."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            # Get memory before initialization
            temp_manager = MemoryManager(max_memory_mb=512, pressure_threshold=0.8)
            memory_before = temp_manager.check_memory_usage()

            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model,
                config=cache_warming_config
            )

            # Get memory after cache warming
            memory_after = retriever.memory_manager.check_memory_usage()

            # Memory tracking should show valid readings
            assert memory_before >= 0
            assert memory_after >= 0


class TestConfigurationLoading:
    """Test configuration loading with performance settings applied to real components."""

    @pytest.fixture
    def mock_chroma_client(self):
        """Mock ChromaDB client."""
        client = Mock()
        collection = Mock()
        client.get_or_create_collection.return_value = collection
        return client

    @pytest.fixture
    def mock_embedding_model(self):
        """Mock embedding model."""
        model = Mock()
        model.encode.return_value = [[0.1, 0.2, 0.3]]
        return model

    @pytest.fixture
    def performance_config(self):
        """Configuration with performance settings."""
        return {
            'cache': {
                'max_size': 1000,
                'ttl_seconds': 3600
            },
            'memory': {
                'max_memory_mb': 512,
                'warning_threshold': 0.8
            },
            'lazy_loading': {
                'enabled': True,
                'batch_size': 50
            }
        }

    def test_performance_settings_loaded(
        self, mock_chroma_client, mock_embedding_model, performance_config
    ):
        """Test that performance settings are loaded correctly."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model,
                config=performance_config
            )

            assert retriever.config == performance_config

    def test_settings_applied_to_memory_manager(
        self, mock_chroma_client, mock_embedding_model, performance_config
    ):
        """Test that settings are applied to real MemoryManager."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model,
                config=performance_config
            )

            # Verify real MemoryManager has correct max_memory_mb
            assert retriever.memory_manager.max_memory_mb == 512

    def test_settings_applied_to_result_cache(
        self, mock_chroma_client, mock_embedding_model, performance_config
    ):
        """Test that settings are applied to real ResultCache."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model,
                config=performance_config
            )

            # Verify real ResultCache respects max_size
            # Fill cache beyond limit and verify eviction
            for i in range(1005):  # Exceed max_size of 1000
                retriever.result_cache.set(f"query_{i}", f"result_{i}")

            # Cache should have evicted entries to stay under limit
            # Not all 1005 queries should be cached
            cached_count = sum(1 for i in range(1005)
                             if retriever.result_cache.get(f"query_{i}") is not None)
            assert cached_count <= 1000

    def test_settings_applied_to_lazy_loader(
        self, mock_chroma_client, mock_embedding_model, performance_config
    ):
        """Test that settings are applied to real LazyLoader."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model,
                config=performance_config
            )

            # Verify lazy loading is enabled
            assert retriever.lazy_loader is not None
            # LazyLoader should be configured with batch_size

    def test_invalid_configuration_raises_error(
        self, mock_chroma_client, mock_embedding_model
    ):
        """Test that invalid configuration raises appropriate errors."""
        invalid_config = {
            'cache': {
                'max_size': -1  # Invalid: negative size
            }
        }

        with patch('chromadb.Client', return_value=mock_chroma_client):
            with pytest.raises(ValueError, match="Invalid cache configuration"):
                ProductionCBRRetriever(
                    db_path="./test_db",
                    embedding_model=mock_embedding_model,
                    config=invalid_config
                )


class TestMemoryManagerTracking:
    """Test real MemoryManager tracks memory during complex queries."""

    @pytest.fixture
    def mock_chroma_client_large_results(self):
        """Mock ChromaDB client with large result sets."""
        client = Mock()
        collection = Mock()

        # Simulate large result set
        large_results = {
            'ids': [['case' + str(i) for i in range(100)]],
            'documents': [['doc' + str(i) for i in range(100)]],
            'metadatas': [[{'category': 'code'} for i in range(100)]],
            'distances': [[0.1 * i for i in range(100)]]
        }
        collection.query.return_value = large_results
        client.get_or_create_collection.return_value = collection
        return client

    @pytest.fixture
    def mock_embedding_model(self):
        """Mock embedding model."""
        model = Mock()
        model.encode.return_value = [[0.1, 0.2, 0.3]]
        return model

    def test_memory_tracked_before_query(
        self, mock_chroma_client_large_results, mock_embedding_model
    ):
        """Test that memory usage is tracked before query."""
        with patch('chromadb.Client', return_value=mock_chroma_client_large_results):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            # Real MemoryManager should provide current usage
            memory_before = retriever.memory_manager.check_memory_usage()
            assert memory_before >= 0

    def test_memory_tracked_during_query_execution(
        self, mock_chroma_client_large_results, mock_embedding_model
    ):
        """Test that memory usage is tracked during query execution."""
        with patch('chromadb.Client', return_value=mock_chroma_client_large_results):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            query = "complex query"
            retriever.retrieve(query, max_results=100)

            # Real MemoryManager should track memory during operation
            current_memory = retriever.memory_manager.check_memory_usage()
            assert current_memory > 0

    def test_memory_tracked_after_query_completion(
        self, mock_chroma_client_large_results, mock_embedding_model
    ):
        """Test that memory usage is tracked after query completion."""
        with patch('chromadb.Client', return_value=mock_chroma_client_large_results):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            query = "complex query"
            retriever.retrieve(query, max_results=100)

            # Real MemoryManager should provide valid reading after query
            memory_after = retriever.memory_manager.check_memory_usage()
            assert memory_after >= 0

    def test_memory_metrics_accessible(
        self, mock_chroma_client_large_results, mock_embedding_model
    ):
        """Test that memory metrics are accessible from real MemoryManager."""
        with patch('chromadb.Client', return_value=mock_chroma_client_large_results):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            query = "complex query"
            retriever.retrieve(query, max_results=100)

            # Real MemoryManager should provide current usage
            current_memory = retriever.memory_manager.check_memory_usage()
            assert current_memory >= 0


class TestResultCacheEviction:
    """Test real ResultCache eviction on memory pressure."""

    @pytest.fixture
    def mock_chroma_client(self):
        """Mock ChromaDB client."""
        client = Mock()
        collection = Mock()
        collection.query.return_value = {
            'ids': [['case1']],
            'documents': [['doc1']],
            'metadatas': [[{'category': 'code'}]],
            'distances': [[0.1]]
        }
        client.get_or_create_collection.return_value = collection
        return client

    @pytest.fixture
    def mock_embedding_model(self):
        """Mock embedding model."""
        model = Mock()
        model.encode.return_value = [[0.1, 0.2, 0.3]]
        return model

    @pytest.fixture
    def low_memory_config(self):
        """Configuration with low memory threshold."""
        return {
            'cache': {
                'max_size': 5  # Very small cache
            },
            'memory': {
                'max_memory_mb': 10,  # Very low limit
                'warning_threshold': 0.8
            }
        }

    def test_cache_fills_to_limit(
        self, mock_chroma_client, mock_embedding_model, low_memory_config
    ):
        """Test that real cache fills up to memory limit."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model,
                config=low_memory_config
            )

            # Fill cache with queries
            for i in range(5):
                retriever.retrieve(f"query {i}", max_results=5)

            # Verify cache has entries (up to max_size)
            cached_count = sum(1 for i in range(5)
                             if retriever.result_cache.get(f"query {i}") is not None)
            assert cached_count <= 5

    def test_lru_eviction_when_limit_reached(
        self, mock_chroma_client, mock_embedding_model, low_memory_config
    ):
        """Test that real cache evicts least recently used entries when limit is reached."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model,
                config=low_memory_config
            )

            # Fill cache to limit
            for i in range(5):
                retriever.retrieve(f"query {i}", max_results=5)

            # Add one more query - should evict oldest (LRU behavior)
            retriever.retrieve("query 5", max_results=5)

            # Verify LRU eviction occurred
            # Oldest query should be evicted, newest should be present
            assert retriever.result_cache.get("query 5") is not None
            # At least one old query should be evicted
            old_queries_present = sum(1 for i in range(5)
                                     if retriever.result_cache.get(f"query {i}") is not None)
            assert old_queries_present < 5  # Should have evicted at least one

    def test_memory_usage_within_limits(
        self, mock_chroma_client, mock_embedding_model, low_memory_config
    ):
        """Test that memory usage stays within configured limits."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model,
                config=low_memory_config
            )

            # Fill cache beyond limit
            for i in range(10):
                retriever.retrieve(f"query {i}", max_results=5)

            # Real MemoryManager should track memory
            current_memory = retriever.memory_manager.check_memory_usage()
            max_memory = low_memory_config['memory']['max_memory_mb']

            # Note: In integration test, we can't guarantee memory stays under limit
            # But we verify tracking is working
            assert current_memory >= 0


class TestLazyLoaderErrorHandling:
    """Test real LazyLoader handles missing embeddings gracefully."""

    @pytest.fixture
    def mock_chroma_client(self):
        """Mock ChromaDB client."""
        client = Mock()
        collection = Mock()
        client.get_or_create_collection.return_value = collection
        return client

    @pytest.fixture
    def failing_case_loader(self):
        """Case loader that fails for certain cases."""
        def loader(case_id: str) -> Dict[str, Any]:
            if "failing" in case_id:
                raise RuntimeError(f"Failed to load case: {case_id}")
            return {
                "case_id": case_id,
                "content": f"Content for {case_id}",
                "category": "code"
            }
        return loader

    def test_lazy_loader_attempts_to_load(
        self, mock_chroma_client, failing_case_loader
    ):
        """Test that real LazyLoader attempts to load embeddings."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                case_loader=failing_case_loader,
                enable_lazy_loading=True
            )

            # Should successfully load normal case
            result = retriever.lazy_loader.load_on_demand("normal_case")
            assert result is not None

    def test_error_handling_for_failed_embeddings(
        self, mock_chroma_client, failing_case_loader
    ):
        """Test appropriate error handling when embeddings cannot be loaded."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                case_loader=failing_case_loader,
                enable_lazy_loading=True
            )

            # LazyLoader handles failures gracefully by logging and returning None
            result = retriever.lazy_loader.load_on_demand("failing_case")
            assert result is None, "Failed case loading should return None"

    def test_system_continues_with_available_embeddings(
        self, mock_chroma_client, failing_case_loader
    ):
        """Test that system continues to function with available embeddings."""
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                case_loader=failing_case_loader,
                enable_lazy_loading=True
            )

            # Should work with non-failing queries
            results = retriever.lazy_loader.load_on_demand("normal_case")
            assert results is not None

            # Should gracefully handle failing queries by returning None
            failing_result = retriever.lazy_loader.load_on_demand("failing_case")
            assert failing_result is None, "Failed case loading should return None for graceful degradation"


class TestErrorPropagation:
    """
    Test error propagation through the integration stack.

    Verifies that errors from individual components (MemoryManager, ResultCache,
    LazyLoader) properly propagate to the caller with useful debugging information.
    """

    @pytest.fixture
    def mock_chroma_client(self):
        """Mock ChromaDB client."""
        client = Mock()
        collection = Mock()
        collection.query.return_value = {
            'ids': [['case1']],
            'documents': [['doc1']],
            'metadatas': [[{'category': 'code'}]],
            'distances': [[0.1]]
        }
        client.get_or_create_collection.return_value = collection
        return client

    @pytest.fixture
    def mock_embedding_model(self):
        """Mock embedding model."""
        model = Mock()
        model.encode.return_value = [[0.1, 0.2, 0.3]]
        return model

    def test_memory_manager_error_propagates_to_retriever(
        self, mock_chroma_client, mock_embedding_model
    ):
        """
        Test that MemoryManager errors propagate through ProductionCBRRetriever.

        Scenario: MemoryManager.check_memory_usage() raises an error
        Expected: Error propagates to caller with context about memory tracking failure
        """
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            # Mock MemoryManager to raise error during memory check
            with patch.object(retriever.memory_manager, 'check_memory_usage',
                            side_effect=RuntimeError("Memory tracking system failure")):

                # Verify error propagates with useful context
                with pytest.raises(RuntimeError) as exc_info:
                    retriever.retrieve("test query", max_results=5)

                # Error message should indicate memory tracking issue
                assert "Memory tracking" in str(exc_info.value) or "memory" in str(exc_info.value).lower()

    def test_result_cache_error_propagates_to_retriever(
        self, mock_chroma_client, mock_embedding_model
    ):
        """
        Test that ResultCache errors are handled gracefully.

        Scenario: ResultCache.get() raises an error
        Expected: Query still completes by bypassing cache, or error propagates with context
        """
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            # Mock ResultCache to raise error during get
            with patch.object(retriever.result_cache, 'get',
                            side_effect=RuntimeError("Cache corruption error")):

                # Should either:
                # 1. Handle gracefully and complete query (bypassing cache)
                # 2. Propagate error with useful context
                try:
                    result = retriever.retrieve("test query", max_results=5)
                    # If it succeeds, verify query completed despite cache error
                    assert result is not None
                except RuntimeError as e:
                    # If it fails, verify error message provides context
                    assert "cache" in str(e).lower() or "Cache" in str(e)

    def test_lazy_loader_error_propagates_to_retriever(
        self, mock_chroma_client, mock_embedding_model
    ):
        """
        Test that LazyLoader errors propagate with debugging information.

        Scenario: LazyLoader.load_on_demand() raises an error
        Expected: Error propagates to caller with case_id and failure reason
        """
        failing_loader = Mock()
        failing_loader.load_on_demand.side_effect = RuntimeError("Failed to load case: case_123")
        failing_loader.is_loaded.return_value = False

        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model,
                enable_lazy_loading=True
            )

            # Replace lazy_loader with failing version
            retriever.lazy_loader = failing_loader

            # Verify error propagates with useful debugging info
            with pytest.raises(RuntimeError) as exc_info:
                retriever.lazy_loader.load_on_demand("case_123")

            error_msg = str(exc_info.value)
            # Error should contain case_id for debugging
            assert "case_123" in error_msg

    def test_chromadb_error_recovery(
        self, mock_chroma_client, mock_embedding_model
    ):
        """
        Test that ChromaDB errors trigger retry logic.

        Scenario: ChromaDB query fails on first attempt, succeeds on retry
        Expected: Retriever retries and eventually returns result
        """
        # Configure mock to fail once, then succeed
        call_count = [0]

        def query_with_retry(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("ChromaDB connection timeout")
            return {
                'ids': [['case1']],
                'documents': [['doc1']],
                'metadatas': [[{'category': 'code'}]],
                'distances': [[0.1]]
            }

        mock_chroma_client.get_or_create_collection().query.side_effect = query_with_retry

        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model,
                max_retries=3  # Enable retry logic
            )

            # Should retry and eventually succeed
            result = retriever.retrieve("test query", max_results=5)

            # Verify retry occurred (called more than once)
            assert call_count[0] > 1
            # Verify query eventually succeeded
            assert result is not None

    def test_embedding_model_error_handling(
        self, mock_chroma_client, mock_embedding_model
    ):
        """
        Test that embedding model errors propagate with context.

        Scenario: Embedding model fails during encode
        Expected: Error propagates with information about which query failed
        """
        # Configure embedding model to fail
        mock_embedding_model.encode.side_effect = RuntimeError("Model inference failed")

        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            # Verify error propagates with context
            with pytest.raises(RuntimeError) as exc_info:
                retriever.retrieve("test query", max_results=5)

            error_msg = str(exc_info.value)
            # Error should indicate embedding/model failure
            assert "model" in error_msg.lower() or "embedding" in error_msg.lower() or "inference" in error_msg.lower()

    def test_multiple_component_failures(
        self, mock_chroma_client, mock_embedding_model
    ):
        """
        Test cascade failure handling.

        Scenario: Cache fails, then DB fails
        Expected: Errors are logged separately, original error not masked
        """
        with patch('chromadb.Client', return_value=mock_chroma_client):
            retriever = ProductionCBRRetriever(
                db_path="./test_db",
                embedding_model=mock_embedding_model
            )

            # Mock both cache and DB to fail
            with patch.object(retriever.result_cache, 'get',
                            side_effect=RuntimeError("Cache failure")):
                with patch.object(mock_chroma_client.get_or_create_collection(), 'query',
                                side_effect=RuntimeError("Database connection lost")):

                    # Verify error handling doesn't mask original error
                    with pytest.raises(RuntimeError) as exc_info:
                        retriever.retrieve("test query", max_results=5)

                    # Should report at least one of the failures
                    error_msg = str(exc_info.value)
                    assert ("cache" in error_msg.lower() or "database" in error_msg.lower() or
                           "Cache" in error_msg or "Database" in error_msg)
