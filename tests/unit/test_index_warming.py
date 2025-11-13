"""
Unit tests for index warming functionality.

Tests cover:
- Index warming strategy (startup, specific collections)
- Warm-up query generation and execution
- Warm-up completion tracking and timing
- Performance improvement verification
- Error handling scenarios
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import numpy as np
import pytest

# These imports will fail initially since the modules don't exist yet
from cbr_mcp_server.performance.index_warming import (
    IndexWarmer,
    WarmupConfig,
    WarmupStatus,
    execute_warmup_query,
    generate_warmup_queries,
)


class TestIndexWarmingStrategy:
    """Tests for index warming strategy on startup and specific collections."""

    @pytest.mark.asyncio
    async def test_startup_warming_all_collections(self):
        """Verify that index warming is triggered on server startup for all collections."""
        # Arrange
        mock_client = Mock()
        mock_collection1 = Mock(name="collection1")
        mock_collection2 = Mock(name="collection2")
        mock_client.list_collections.return_value = [mock_collection1, mock_collection2]

        config = WarmupConfig(collections=["collection1", "collection2"], num_queries=3)
        warmer = IndexWarmer(mock_client, config)

        # Act
        await warmer.warm_on_startup()

        # Assert
        assert warmer.is_warmed()
        assert warmer.get_warmup_time() > 0
        assert len(warmer.get_warmed_collections()) == 2

    @pytest.mark.asyncio
    async def test_specific_collection_warming(self):
        """Verify that specific collections can be warmed independently."""
        # Arrange
        mock_client = Mock()
        mock_collection = Mock(name="specific_collection")
        mock_client.get_collection.return_value = mock_collection

        config = WarmupConfig()
        warmer = IndexWarmer(mock_client, config)

        # Act
        await warmer.warm_collection("specific_collection")

        # Assert
        assert "specific_collection" in warmer.get_warmed_collections()
        mock_client.get_collection.assert_called_once_with(name="specific_collection")

    @pytest.mark.asyncio
    async def test_collection_existence_check_before_warming(self):
        """Verify that collection existence is checked before warming attempt."""
        # Arrange
        mock_client = Mock()
        mock_client.get_collection.side_effect = ValueError("Collection not found")

        config = WarmupConfig()
        warmer = IndexWarmer(mock_client, config)

        # Act & Assert
        with pytest.raises(ValueError, match="Collection not found"):
            await warmer.warm_collection("nonexistent_collection")


class TestWarmupQueryGeneration:
    """Tests for warm-up query generation."""

    def test_generate_warmup_queries_returns_valid_queries(self):
        """Verify that appropriate warm-up queries are generated for ChromaDB."""
        # Arrange
        embedding_dim = 768
        num_queries = 5

        # Act
        queries = generate_warmup_queries(embedding_dim, num_queries)

        # Assert
        assert len(queries) == num_queries
        for query in queries:
            assert "query_embeddings" in query
            assert len(query["query_embeddings"]) == embedding_dim
            assert "n_results" in query
            assert query["n_results"] > 0

    def test_warmup_queries_have_diverse_patterns(self):
        """Verify that multiple query variations are generated."""
        # Arrange
        embedding_dim = 768
        num_queries = 10

        # Act
        queries = generate_warmup_queries(embedding_dim, num_queries)

        # Assert
        embeddings = [q["query_embeddings"] for q in queries]
        # Verify queries are different from each other
        for i in range(len(embeddings) - 1):
            assert not np.array_equal(embeddings[i], embeddings[i + 1])

    def test_warmup_query_parameters_are_valid(self):
        """Verify that query parameters are correct for ChromaDB."""
        # Arrange
        embedding_dim = 768

        # Act
        queries = generate_warmup_queries(embedding_dim, num_queries=3)

        # Assert
        for query in queries:
            assert isinstance(query["query_embeddings"], (list, np.ndarray))
            assert query["n_results"] in range(1, 11)  # Reasonable range


class TestWarmupQueryExecution:
    """Tests for warm-up query execution."""

    @pytest.mark.asyncio
    async def test_execute_warmup_query_calls_chromadb(self):
        """Verify that warm-up queries are executed against ChromaDB."""
        # Arrange
        mock_collection = Mock()
        mock_collection.query = AsyncMock(return_value={"ids": [["1", "2"]]})
        query = {
            "query_embeddings": [0.1] * 768,
            "n_results": 5,
        }

        # Act
        await execute_warmup_query(mock_collection, query)

        # Assert
        mock_collection.query.assert_called_once()
        call_kwargs = mock_collection.query.call_args[1]
        assert "query_embeddings" in call_kwargs
        assert call_kwargs["n_results"] == 5

    @pytest.mark.asyncio
    async def test_multiple_warmup_queries_executed(self):
        """Verify that multiple queries are executed per collection."""
        # Arrange
        mock_collection = Mock()
        mock_collection.query = AsyncMock(return_value={"ids": [["1"]]})
        queries = [
            {"query_embeddings": [0.1] * 768, "n_results": 5},
            {"query_embeddings": [0.2] * 768, "n_results": 3},
            {"query_embeddings": [0.3] * 768, "n_results": 7},
        ]

        # Act
        for query in queries:
            await execute_warmup_query(mock_collection, query)

        # Assert
        assert mock_collection.query.call_count == 3

    @pytest.mark.asyncio
    async def test_warmup_query_error_handling(self):
        """Verify that errors during warm-up are handled gracefully."""
        # Arrange
        mock_collection = Mock()
        mock_collection.query = AsyncMock(side_effect=RuntimeError("ChromaDB error"))
        query = {"query_embeddings": [0.1] * 768, "n_results": 5}

        # Act & Assert
        # Should not raise, but should log the error
        try:
            await execute_warmup_query(mock_collection, query)
        except RuntimeError:
            pytest.fail("Error should be handled gracefully")


class TestWarmupCompletionTracking:
    """Tests for warm-up completion tracking."""

    @pytest.mark.asyncio
    async def test_completion_flag_set_after_warming(self):
        """Verify that completion flag is set after warming."""
        # Arrange
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.list_collections.return_value = [mock_collection]

        config = WarmupConfig(collections=["test_collection"])
        warmer = IndexWarmer(mock_client, config)

        # Act
        await warmer.warm_on_startup()

        # Assert
        assert warmer.is_warmed() is True

    @pytest.mark.asyncio
    async def test_completion_timestamp_recorded(self):
        """Verify that completion timestamp is recorded."""
        # Arrange
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.list_collections.return_value = [mock_collection]

        config = WarmupConfig(collections=["test_collection"])
        warmer = IndexWarmer(mock_client, config)

        before_time = time.time()

        # Act
        await warmer.warm_on_startup()

        after_time = time.time()

        # Assert
        completion_time = warmer.get_completion_timestamp()
        assert before_time <= completion_time <= after_time

    def test_status_can_be_queried(self):
        """Verify that warmup status can be queried."""
        # Arrange
        mock_client = Mock()
        config = WarmupConfig()
        warmer = IndexWarmer(mock_client, config)

        # Act
        status = warmer.get_status()

        # Assert
        assert isinstance(status, WarmupStatus)
        assert hasattr(status, "is_warmed")
        assert hasattr(status, "warmed_collections")
        assert hasattr(status, "warmup_duration")


class TestWarmupTimingMetrics:
    """Tests for warm-up timing metrics."""

    @pytest.mark.asyncio
    async def test_start_time_recorded(self):
        """Verify that start time is recorded."""
        # Arrange
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.list_collections.return_value = [mock_collection]

        config = WarmupConfig()
        warmer = IndexWarmer(mock_client, config)

        # Act
        with patch("time.time") as mock_time:
            mock_time.return_value = 1000.0
            await warmer.warm_on_startup()

            # Assert
            assert warmer._start_time == 1000.0

    @pytest.mark.asyncio
    async def test_duration_calculated_correctly(self):
        """Verify that duration is calculated correctly."""
        # Arrange
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.list_collections.return_value = [mock_collection]

        config = WarmupConfig()
        warmer = IndexWarmer(mock_client, config)

        # Act
        with patch("time.time") as mock_time:
            mock_time.side_effect = [1000.0, 1005.5]  # 5.5 seconds
            await warmer.warm_on_startup()

            # Assert
            duration = warmer.get_warmup_time()
            assert duration == pytest.approx(5.5, rel=0.1)

    @pytest.mark.asyncio
    async def test_per_collection_timing_tracked(self):
        """Verify that per-collection timing is tracked."""
        # Arrange
        mock_client = Mock()
        mock_coll1 = Mock(name="coll1")
        mock_coll2 = Mock(name="coll2")
        mock_client.list_collections.return_value = [mock_coll1, mock_coll2]

        config = WarmupConfig(collections=["coll1", "coll2"])
        warmer = IndexWarmer(mock_client, config)

        # Act
        await warmer.warm_on_startup()

        # Assert
        timings = warmer.get_collection_timings()
        assert "coll1" in timings
        assert "coll2" in timings
        assert all(t > 0 for t in timings.values())


class TestFirstQueryPerformanceImprovement:
    """Tests for verifying that warming improves first-query performance."""

    @pytest.mark.asyncio
    async def test_first_query_faster_after_warming(self):
        """Verify that first query after warming is faster than cold start."""
        # Arrange
        mock_client = Mock()
        mock_collection = Mock()

        # Simulate cold start delay
        query_times = [0.5, 0.1, 0.1]  # First query slow, then fast

        async def delayed_query(**kwargs):
            delay = query_times.pop(0) if query_times else 0.1
            await asyncio.sleep(delay)
            return {"ids": [["1"]]}

        mock_collection.query = AsyncMock(side_effect=delayed_query)
        mock_client.get_collection.return_value = mock_collection

        config = WarmupConfig(collections=["test_coll"], num_queries=2)
        warmer = IndexWarmer(mock_client, config)

        # Act - warm the index
        await warmer.warm_on_startup()

        # Measure query time after warming
        start = time.time()
        await mock_collection.query(query_embeddings=[[0.1] * 768], n_results=5)
        query_time = time.time() - start

        # Assert - query should be fast because index is warm
        assert query_time < 0.2  # Should be much faster than cold start

    @pytest.mark.asyncio
    async def test_subsequent_queries_maintain_performance(self):
        """Verify that subsequent queries maintain performance."""
        # Arrange
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.query = AsyncMock(return_value={"ids": [["1"]]})
        mock_client.get_collection.return_value = mock_collection

        config = WarmupConfig()
        warmer = IndexWarmer(mock_client, config)
        await warmer.warm_on_startup()

        # Act - execute multiple queries
        times = []
        for _ in range(5):
            start = time.time()
            await mock_collection.query(query_embeddings=[[0.1] * 768], n_results=5)
            times.append(time.time() - start)

        # Assert - all queries should be consistently fast
        assert all(t < 0.1 for t in times)


class TestWarmupErrorHandling:
    """Tests for error handling during warm-up."""

    @pytest.mark.asyncio
    async def test_collection_not_found_handled_gracefully(self):
        """Verify graceful handling when collection doesn't exist."""
        # Arrange
        mock_client = Mock()
        mock_client.get_collection.side_effect = ValueError("Collection not found")

        config = WarmupConfig()
        warmer = IndexWarmer(mock_client, config)

        # Act & Assert - should not raise
        with patch("logging.warning") as mock_log:
            await warmer.warm_collection("nonexistent")
            mock_log.assert_called()

    @pytest.mark.asyncio
    async def test_other_collections_warmed_after_error(self):
        """Verify that other collections are still warmed after one fails."""
        # Arrange
        mock_client = Mock()
        mock_coll1 = Mock(name="coll1")
        mock_coll2 = Mock(name="coll2")

        def get_collection_side_effect(name):
            if name == "coll1":
                raise ValueError("Collection not found")
            return mock_coll2

        mock_client.get_collection.side_effect = get_collection_side_effect

        config = WarmupConfig(collections=["coll1", "coll2"])
        warmer = IndexWarmer(mock_client, config)

        # Act
        await warmer.warm_on_startup()

        # Assert - coll2 should still be warmed
        assert "coll2" in warmer.get_warmed_collections()

    @pytest.mark.asyncio
    async def test_chromadb_connection_failure_handled(self):
        """Verify graceful handling when ChromaDB is unavailable."""
        # Arrange
        mock_client = Mock()
        mock_client.list_collections.side_effect = ConnectionError(
            "ChromaDB unavailable"
        )

        config = WarmupConfig()
        warmer = IndexWarmer(mock_client, config)

        # Act & Assert - server should continue in degraded mode
        with patch("logging.error") as mock_log:
            await warmer.warm_on_startup()
            mock_log.assert_called()
            assert warmer.is_warmed() is False


class TestWarmupMultipleCollections:
    """Tests for warming multiple collections."""

    @pytest.mark.asyncio
    async def test_all_collections_warmed(self):
        """Verify all collections are warmed."""
        # Arrange
        mock_client = Mock()
        collections = [Mock(name=f"coll{i}") for i in range(3)]
        mock_client.list_collections.return_value = collections

        config = WarmupConfig(collections=["coll0", "coll1", "coll2"])
        warmer = IndexWarmer(mock_client, config)

        # Act
        await warmer.warm_on_startup()

        # Assert
        warmed = warmer.get_warmed_collections()
        assert len(warmed) == 3
        assert all(f"coll{i}" in warmed for i in range(3))

    @pytest.mark.asyncio
    async def test_collections_warmed_in_order(self):
        """Verify collections are warmed in correct order."""
        # Arrange
        mock_client = Mock()
        warm_order = []

        def track_warming(name):
            warm_order.append(name)
            return Mock()

        mock_client.get_collection.side_effect = track_warming

        config = WarmupConfig(collections=["first", "second", "third"])
        warmer = IndexWarmer(mock_client, config)

        # Act
        await warmer.warm_on_startup()

        # Assert
        assert warm_order == ["first", "second", "third"]

    @pytest.mark.asyncio
    async def test_total_timing_includes_all_collections(self):
        """Verify total timing includes all collections."""
        # Arrange
        mock_client = Mock()
        collections = [Mock(name=f"coll{i}") for i in range(3)]
        mock_client.list_collections.return_value = collections

        config = WarmupConfig(collections=["coll0", "coll1", "coll2"])
        warmer = IndexWarmer(mock_client, config)

        # Act
        await warmer.warm_on_startup()

        # Assert
        total_time = warmer.get_warmup_time()
        collection_times = warmer.get_collection_timings()
        sum_collection_times = sum(collection_times.values())

        assert total_time >= sum_collection_times


class TestWarmupIdempotency:
    """Tests for warm-up idempotency."""

    @pytest.mark.asyncio
    async def test_multiple_warmup_calls_safe(self):
        """Verify that warming can be called multiple times safely."""
        # Arrange
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.list_collections.return_value = [mock_collection]

        config = WarmupConfig()
        warmer = IndexWarmer(mock_client, config)

        # Act
        await warmer.warm_on_startup()
        await warmer.warm_on_startup()
        await warmer.warm_on_startup()

        # Assert - should not error
        assert warmer.is_warmed() is True

    @pytest.mark.asyncio
    async def test_subsequent_warmups_faster(self):
        """Verify that subsequent warm-ups are faster (cached)."""
        # Arrange
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.list_collections.return_value = [mock_collection]

        config = WarmupConfig()
        warmer = IndexWarmer(mock_client, config)

        # Act
        async def measure_warmup_time():
            start = time.time()
            await warmer.warm_on_startup()
            return time.time() - start

        first_warmup_time = await measure_warmup_time()
        second_warmup_time = await measure_warmup_time()

        # Assert
        assert second_warmup_time <= first_warmup_time

    @pytest.mark.asyncio
    async def test_state_remains_consistent(self):
        """Verify that state remains consistent after multiple warm-ups."""
        # Arrange
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.list_collections.return_value = [mock_collection]

        config = WarmupConfig(collections=["test_coll"])
        warmer = IndexWarmer(mock_client, config)

        # Act
        await warmer.warm_on_startup()
        status1 = warmer.get_status()

        await warmer.warm_on_startup()
        status2 = warmer.get_status()

        # Assert
        assert status1.is_warmed == status2.is_warmed
        assert status1.warmed_collections == status2.warmed_collections


class TestWarmupConfiguration:
    """Tests for warm-up configuration."""

    def test_num_queries_configurable(self):
        """Verify that number of warm-up queries is configurable."""
        # Arrange & Act
        config1 = WarmupConfig(num_queries=5)
        config2 = WarmupConfig(num_queries=10)

        # Assert
        assert config1.num_queries == 5
        assert config2.num_queries == 10

    def test_collections_to_warm_configurable(self):
        """Verify that collections to warm are configurable."""
        # Arrange & Act
        config = WarmupConfig(collections=["coll1", "coll2", "coll3"])

        # Assert
        assert config.collections == ["coll1", "coll2", "coll3"]

    def test_warmup_can_be_disabled(self):
        """Verify that warm-up can be disabled."""
        # Arrange & Act
        config = WarmupConfig(enabled=False)

        # Assert
        assert config.enabled is False

    @pytest.mark.asyncio
    async def test_disabled_warmup_skips_warming(self):
        """Verify that disabled warm-up skips warming process."""
        # Arrange
        mock_client = Mock()
        config = WarmupConfig(enabled=False)
        warmer = IndexWarmer(mock_client, config)

        # Act
        await warmer.warm_on_startup()

        # Assert
        mock_client.list_collections.assert_not_called()
        assert warmer.is_warmed() is False


class TestWarmupEdgeCases:
    """Tests for edge cases in warm-up functionality."""

    @pytest.mark.asyncio
    async def test_empty_collections_list(self):
        """Verify that warming with empty collections list is handled correctly."""
        # Arrange
        mock_client = Mock()
        config = WarmupConfig(collections=[])
        warmer = IndexWarmer(mock_client, config)

        # Act
        await warmer.warm_on_startup()

        # Assert
        assert warmer.is_warmed() is True  # Should complete without error
        assert len(warmer.get_warmed_collections()) == 0

    def test_invalid_query_parameters_rejected(self):
        """Verify that invalid query parameters are rejected."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="num_queries must be positive"):
            generate_warmup_queries(embedding_dim=768, num_queries=0)

        with pytest.raises(ValueError, match="num_queries must be positive"):
            generate_warmup_queries(embedding_dim=768, num_queries=-5)

        with pytest.raises(ValueError, match="embedding_dim must be positive"):
            generate_warmup_queries(embedding_dim=0, num_queries=5)

    @pytest.mark.asyncio
    async def test_warmup_with_none_collection_name(self):
        """Verify that None collection name is handled appropriately."""
        # Arrange
        mock_client = Mock()
        config = WarmupConfig()
        warmer = IndexWarmer(mock_client, config)

        # Act & Assert
        with pytest.raises(ValueError, match="Collection name cannot be None"):
            await warmer.warm_collection(None)
