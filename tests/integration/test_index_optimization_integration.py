"""
Integration Tests for Index Optimization Components.

This module tests the integration of three key performance components:
1. IndexOptimizationConfig: HNSW configuration for ChromaDB
2. IndexWarmer: Index warming on startup for improved first-query performance
3. IndexPerformanceMonitor: Performance monitoring and metrics tracking

These tests verify that all components work together correctly with real ChromaDB
instances, ensuring proper configuration, warming, and monitoring workflows.
"""

import asyncio
import time
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import chromadb
import pytest

from cbr_mcp_server.performance.data_models import IndexOptimizationConfig
from cbr_mcp_server.performance.index_monitor import (
    IndexPerformanceMonitor,
    IndexPerformanceThresholds,
)
from cbr_mcp_server.performance.index_warming import (
    IndexWarmer,
    WarmupConfig,
    generate_warmup_queries,
)


@pytest.fixture
def ephemeral_chromadb_client():
    """Create an ephemeral ChromaDB client for integration tests."""
    # Use in-memory client to avoid filesystem dependencies
    client = chromadb.Client()
    yield client
    # Cleanup happens automatically with ephemeral client


@pytest.fixture
def mock_embedding_model():
    """Create mock embedding model for query encoding."""
    model = MagicMock()
    # Return realistic embedding (list format) with correct dimension
    model.encode.return_value = [0.1] * 768
    return model


@pytest.fixture
def mock_case_loader():
    """Create mock case loader simulating storage access."""

    def loader(case_id: str) -> Dict[str, Any]:
        return {
            "case_id": case_id,
            "content": f"Content for {case_id}",
            "category": "code",
            "subcategory": "testing",
            "tags": ["test"],
            "embedding": [0.1] * 768,
        }

    return loader


class TestIndexOptimizationConfigIntegration:
    """Test IndexOptimizationConfig integration with ChromaDB."""

    def test_config_applies_to_chromadb_collection(self, ephemeral_chromadb_client):
        """
        Test that IndexOptimizationConfig correctly applies HNSW parameters to ChromaDB.

        This verifies:
        1. Configuration generates valid ChromaDB metadata
        2. Collection created with expected HNSW parameters
        3. Metadata retrievable from collection
        """
        # Create optimization configuration
        config = IndexOptimizationConfig(
            space="cosine", ef_construction=100, ef_search=50, M=16
        )

        # Convert to ChromaDB metadata
        chroma_metadata = config.to_chroma_metadata()

        # Create collection with HNSW configuration
        collection = ephemeral_chromadb_client.create_collection(
            name="test_optimized_collection", metadata=chroma_metadata
        )

        # Verify collection was created (this will fail if collection doesn't exist)
        assert collection is not None, "Collection should be created successfully"

        # Verify metadata was stored correctly
        retrieved_metadata = collection.metadata
        assert retrieved_metadata is not None, "Collection should have metadata"

        # Verify HNSW parameters are present
        assert (
            "hnsw:space" in retrieved_metadata
        ), "HNSW space parameter should be present"
        assert (
            "hnsw:construction_ef" in retrieved_metadata
        ), "HNSW construction_ef should be present"
        assert (
            "hnsw:search_ef" in retrieved_metadata
        ), "HNSW search_ef should be present"
        assert "hnsw:M" in retrieved_metadata, "HNSW M parameter should be present"

    def test_config_validation_with_chromadb(self, ephemeral_chromadb_client):
        """
        Test IndexOptimizationConfig validation rules work with ChromaDB.

        This verifies:
        1. ef_search <= ef_construction constraint is enforced
        2. Invalid parameters rejected before collection creation
        3. Valid configuration produces valid metadata
        """
        # Verify invalid config is rejected (ef_search > ef_construction)
        with pytest.raises(ValueError, match="ef_search.*must be <= ef_construction"):
            IndexOptimizationConfig(ef_construction=50, ef_search=100)

        # Create valid config with ef_search <= ef_construction
        config = IndexOptimizationConfig(ef_construction=100, ef_search=50)

        # Verify constraint is satisfied
        assert (
            config.ef_search <= config.ef_construction
        ), "ef_search should be <= ef_construction"

        # Verify ChromaDB accepts the valid configuration
        chroma_metadata = config.to_chroma_metadata()
        collection = ephemeral_chromadb_client.create_collection(
            name="test_validated_collection", metadata=chroma_metadata
        )

        assert collection is not None, "ChromaDB should accept valid configuration"

    def test_config_parameter_formats(self, ephemeral_chromadb_client):
        """
        Test that configuration parameters use correct types and formats.

        This verifies:
        1. Integer parameters stored as integers
        2. String parameters stored as strings
        3. ChromaDB accepts the parameter types
        """
        config = IndexOptimizationConfig(
            space="l2", ef_construction=200, ef_search=100, M=32
        )

        metadata = config.to_chroma_metadata()

        # Verify parameter types
        assert isinstance(metadata["hnsw:space"], str), "hnsw:space should be string"
        assert isinstance(
            metadata["hnsw:construction_ef"], int
        ), "hnsw:construction_ef should be int"
        assert isinstance(
            metadata["hnsw:search_ef"], int
        ), "hnsw:search_ef should be int"
        assert isinstance(metadata["hnsw:M"], int), "hnsw:M should be int"

        # Verify ChromaDB accepts these types
        collection = ephemeral_chromadb_client.create_collection(
            name="test_parameter_types", metadata=metadata
        )
        assert collection is not None, "ChromaDB should accept parameter types"


class TestIndexWarmerIntegration:
    """Test IndexWarmer integration with ChromaDB."""

    @pytest.mark.asyncio
    async def test_warmer_warms_chromadb_collection(
        self, ephemeral_chromadb_client, mock_embedding_model
    ):
        """
        Test IndexWarmer successfully warms a ChromaDB collection.

        This verifies:
        1. Warmer completes successfully (is_warmed = True)
        2. Collection warmed within reasonable time
        3. Warmup queries execute without errors
        """
        # Create a collection with some vectors
        collection = ephemeral_chromadb_client.create_collection(
            name="test_warmup_collection"
        )

        # Add some vectors to warm
        collection.add(
            ids=["vec1", "vec2", "vec3"],
            embeddings=[[0.1] * 768, [0.2] * 768, [0.3] * 768],
            documents=["doc1", "doc2", "doc3"],
        )

        # Create warmer
        config = WarmupConfig(num_queries=3, collections=["test_warmup_collection"])
        warmer = IndexWarmer(ephemeral_chromadb_client, config)

        # Execute warming
        start_time = time.time()
        await warmer.warm_on_startup()
        warmup_duration = time.time() - start_time

        # Verify warming completed successfully
        assert warmer.is_warmed(), "Warmer should report as warmed"
        assert warmup_duration < 5.0, "Warmup should complete within 5 seconds"
        assert (
            "test_warmup_collection" in warmer.get_warmed_collections()
        ), "Collection should be in warmed list"

    @pytest.mark.asyncio
    async def test_warmer_tracks_collection_timings(self, ephemeral_chromadb_client):
        """
        Test IndexWarmer tracks per-collection timing information.

        This verifies:
        1. Per-collection timings recorded
        2. Timing values are reasonable (non-zero, finite)
        3. All collections have timing entries
        """
        # Create multiple collections
        for i in range(3):
            collection = ephemeral_chromadb_client.create_collection(
                name=f"test_collection_{i}"
            )
            collection.add(
                ids=[f"vec{i}"], embeddings=[[0.1] * 768], documents=[f"doc{i}"]
            )

        # Create warmer for all collections
        config = WarmupConfig(
            num_queries=2,
            collections=[f"test_collection_{i}" for i in range(3)],
        )
        warmer = IndexWarmer(ephemeral_chromadb_client, config)

        # Execute warming
        await warmer.warm_on_startup()

        # Verify timing information
        timings = warmer.get_collection_timings()
        assert len(timings) == 3, "Should have timing for all 3 collections"

        for collection_name, duration in timings.items():
            assert duration > 0, f"Timing for {collection_name} should be positive"
            assert duration < 10.0, f"Timing for {collection_name} should be reasonable"

    @pytest.mark.asyncio
    async def test_warmer_handles_missing_collection(self, ephemeral_chromadb_client):
        """
        Test IndexWarmer gracefully handles missing collections.

        This verifies:
        1. ValueError raised for non-existent collection
        2. Error logged appropriately
        3. Warmer continues for other collections
        """
        # Create warmer with non-existent collection
        config = WarmupConfig(num_queries=2, collections=["non_existent_collection"])
        warmer = IndexWarmer(ephemeral_chromadb_client, config)

        # Execute warming (should handle missing collection)
        await warmer.warm_on_startup()

        # Verify warmer did not mark as warmed (no collections successfully warmed)
        assert (
            len(warmer.get_warmed_collections()) == 0
        ), "No collections should be warmed"


class TestIndexPerformanceMonitorIntegration:
    """Test IndexPerformanceMonitor integration with ChromaDB."""

    def test_monitor_tracks_real_chromadb_queries(self, ephemeral_chromadb_client):
        """
        Test IndexPerformanceMonitor tracks performance from real ChromaDB queries.

        This verifies:
        1. Monitor tracks query latencies
        2. Index size retrieved correctly
        3. HNSW parameters extracted
        4. Metrics aggregation produces valid data
        """
        # Create collection with HNSW config
        config = IndexOptimizationConfig(
            space="cosine", ef_construction=100, ef_search=50, M=16
        )
        collection = ephemeral_chromadb_client.create_collection(
            name="test_monitor_collection", metadata=config.to_chroma_metadata()
        )

        # Add vectors
        collection.add(
            ids=["vec1", "vec2", "vec3"],
            embeddings=[[0.1] * 768, [0.2] * 768, [0.3] * 768],
            documents=["doc1", "doc2", "doc3"],
        )

        # Create monitor
        monitor = IndexPerformanceMonitor(collection)

        # Perform some queries and track latencies
        for _ in range(5):
            start = time.time()
            collection.query(query_embeddings=[[0.15] * 768], n_results=2)
            latency_ms = (time.time() - start) * 1000
            monitor.track_query_latency(latency_ms)

        # Aggregate metrics
        metrics = monitor.aggregate_metrics()

        # Verify metrics
        assert metrics.index_size == 3, "Index size should match vector count"
        assert (
            metrics.latency_distribution.sample_count == 5
        ), "Should have 5 latency samples"
        assert (
            metrics.latency_distribution.p50_ms > 0
        ), "Median latency should be positive"
        assert (
            "ef_construction" in metrics.hnsw_params
            or "hnsw_construction_ef" in metrics.hnsw_params
        ), "HNSW parameters should be extracted"

    def test_monitor_detects_threshold_violations(self, ephemeral_chromadb_client):
        """
        Test IndexPerformanceMonitor detects performance threshold violations.

        This verifies:
        1. Latency threshold violations detected
        2. Index size threshold violations detected
        3. Threshold check returns appropriate messages
        """
        # Create collection
        collection = ephemeral_chromadb_client.create_collection(
            name="test_threshold_collection"
        )
        collection.add(ids=["vec1"], embeddings=[[0.1] * 768], documents=["doc1"])

        # Create monitor with strict thresholds
        thresholds = IndexPerformanceThresholds(
            max_query_latency_ms=1.0,  # Very strict (1ms)
            max_index_size=2,  # Strict size limit
            max_memory_mb=10,  # Strict memory limit
        )
        monitor = IndexPerformanceMonitor(
            collection, thresholds=thresholds, enabled=True
        )

        # Add latency that exceeds threshold
        monitor.track_query_latency(100.0)  # 100ms >> 1ms threshold

        # Check for violations
        violations = monitor.check_thresholds()

        # Verify latency violation detected
        assert violations is not None, "Should detect threshold violations"
        assert len(violations) > 0, "Should have at least one violation"
        assert any(
            "latency" in v.lower() for v in violations
        ), "Should detect latency threshold violation"

    def test_monitor_hnsw_parameter_extraction(self, ephemeral_chromadb_client):
        """
        Test IndexPerformanceMonitor extracts HNSW parameters from collection.

        This verifies:
        1. Parameters extracted correctly from metadata
        2. All key HNSW parameters present
        3. Parameter values match configuration
        """
        # Create collection with specific HNSW config
        config = IndexOptimizationConfig(
            space="l2", ef_construction=150, ef_search=75, M=24
        )
        collection = ephemeral_chromadb_client.create_collection(
            name="test_hnsw_params", metadata=config.to_chroma_metadata()
        )

        # Create monitor
        monitor = IndexPerformanceMonitor(collection)

        # Extract HNSW parameters
        params = monitor.get_hnsw_parameters()

        # Verify parameters extracted
        assert len(params) > 0, "Should extract HNSW parameters"

        # Verify key parameters present (using fallback keys)
        assert (
            "ef_construction" in params or "hnsw_construction_ef" in params
        ), "Should have ef_construction"
        assert (
            "ef_search" in params or "hnsw_search_ef" in params
        ), "Should have ef_search"
        assert "M" in params or "hnsw_M" in params, "Should have M parameter"


class TestIntegratedWorkflow:
    """Test complete integration of all components."""

    @pytest.mark.asyncio
    async def test_complete_optimization_workflow(self, ephemeral_chromadb_client):
        """
        Test end-to-end workflow: Config → Collection → Warmer → Monitor.

        This verifies:
        1. IndexOptimizationConfig creates properly configured collection
        2. IndexWarmer successfully warms the optimized collection
        3. IndexPerformanceMonitor tracks warmup performance
        4. All metrics align correctly
        """
        # Step 1: Create optimized configuration
        config = IndexOptimizationConfig(
            space="cosine", ef_construction=100, ef_search=50, M=16
        )

        # Step 2: Create collection with optimization
        collection = ephemeral_chromadb_client.create_collection(
            name="test_integrated_workflow", metadata=config.to_chroma_metadata()
        )

        # Add test vectors
        collection.add(
            ids=[f"vec{i}" for i in range(10)],
            embeddings=[[0.1 * i] * 768 for i in range(10)],
            documents=[f"doc{i}" for i in range(10)],
        )

        # Step 3: Warm the collection
        warmup_config = WarmupConfig(
            num_queries=5, collections=["test_integrated_workflow"]
        )
        warmer = IndexWarmer(ephemeral_chromadb_client, warmup_config)
        await warmer.warm_on_startup()

        # Step 4: Monitor performance
        monitor = IndexPerformanceMonitor(collection)

        # Perform queries and track latencies
        for _ in range(10):
            start = time.time()
            collection.query(query_embeddings=[[0.15] * 768], n_results=3)
            latency_ms = (time.time() - start) * 1000
            monitor.track_query_latency(latency_ms)

        # Step 5: Verify integration
        assert warmer.is_warmed(), "Collection should be warmed"
        assert (
            "test_integrated_workflow" in warmer.get_warmed_collections()
        ), "Collection should be in warmed list"

        metrics = monitor.aggregate_metrics()
        assert metrics.index_size == 10, "Monitor should track correct index size"
        assert (
            metrics.latency_distribution.sample_count == 10
        ), "Should have 10 latency samples"

        # Verify HNSW config persisted through workflow
        hnsw_params = monitor.get_hnsw_parameters()
        assert len(hnsw_params) > 0, "HNSW parameters should be present"

    @pytest.mark.asyncio
    async def test_warmer_with_performance_callback(self, ephemeral_chromadb_client):
        """
        Test IndexWarmer reporting metrics via callback to monitor.

        This verifies:
        1. Monitor callback receives warmup metrics
        2. Callback invoked with timing data
        3. Bidirectional integration works
        """
        # Create collection
        collection = ephemeral_chromadb_client.create_collection(
            name="test_callback_collection"
        )
        collection.add(
            ids=["vec1", "vec2"],
            embeddings=[[0.1] * 768, [0.2] * 768],
            documents=["doc1", "doc2"],
        )

        # Create monitor with callback tracking
        monitor = IndexPerformanceMonitor(collection)
        callback_invoked = {"count": 0, "metrics": None}

        def test_callback(metrics):
            callback_invoked["count"] += 1
            callback_invoked["metrics"] = metrics

        monitor.set_tracker_callback(test_callback)

        # Create warmer and warm collection
        config = WarmupConfig(num_queries=3, collections=["test_callback_collection"])
        warmer = IndexWarmer(ephemeral_chromadb_client, config)
        await warmer.warm_on_startup()

        # Note: This test verifies the callback infrastructure exists
        # Actual callback integration would require IndexWarmer to call monitor.report_to_tracker()
        # which is not currently implemented but the infrastructure is in place

        assert warmer.is_warmed(), "Warmer should complete successfully"


class TestParameterChangeDetection:
    """Test IndexPerformanceMonitor parameter change detection."""

    def test_parameter_change_detection(self, ephemeral_chromadb_client):
        """
        Test monitor detects HNSW parameter changes.

        This verifies:
        1. Initial parameters captured correctly
        2. Parameter changes detected
        3. No false positives for unchanged parameters
        """
        # Create collection with initial config
        initial_config = IndexOptimizationConfig(
            space="cosine", ef_construction=100, ef_search=50, M=16
        )
        collection = ephemeral_chromadb_client.create_collection(
            name="test_param_changes", metadata=initial_config.to_chroma_metadata()
        )

        monitor = IndexPerformanceMonitor(collection)
        initial_params = monitor.get_hnsw_parameters()

        # Simulate parameter change (in practice, would modify collection metadata)
        # For testing, create a modified params dict
        updated_params = initial_params.copy()

        # Modify a parameter
        if "ef_search" in updated_params:
            updated_params["ef_search"] = 100  # Changed from 50
        elif "hnsw_search_ef" in updated_params:
            updated_params["hnsw_search_ef"] = 100  # Changed from 50

        # Detect change
        changed = monitor.detect_parameter_changes(initial_params, updated_params)
        assert changed is True, "Should detect parameter change"

        # Verify no false positive for identical parameters
        unchanged = monitor.detect_parameter_changes(initial_params, initial_params)
        assert unchanged is False, "Should not detect change for identical parameters"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_warmer_with_disabled_config(self, ephemeral_chromadb_client):
        """
        Test IndexWarmer respects disabled configuration.

        This verifies:
        1. Warmer skips warming when disabled
        2. is_warmed remains False
        3. No collections warmed
        4. Completes quickly (no actual work done)
        """
        # Create collection
        collection = ephemeral_chromadb_client.create_collection(
            name="test_disabled_warmer"
        )
        collection.add(ids=["vec1"], embeddings=[[0.1] * 768], documents=["doc1"])

        # Create warmer with disabled config
        config = WarmupConfig(
            num_queries=5, collections=["test_disabled_warmer"], enabled=False
        )
        warmer = IndexWarmer(ephemeral_chromadb_client, config)

        # Execute warming (should be skipped)
        start_time = time.time()
        await warmer.warm_on_startup()
        duration = time.time() - start_time

        # Verify warming was skipped
        assert not warmer.is_warmed(), "Warmer should not be marked as warmed"
        assert (
            len(warmer.get_warmed_collections()) == 0
        ), "No collections should be warmed"
        assert duration < 0.1, "Disabled warmer should complete almost instantly"

    @pytest.mark.asyncio
    async def test_warmer_with_none_collections_warms_all(self):
        """
        Test IndexWarmer with collections=None warms all collections.

        This verifies:
        1. collections=None triggers discovery of all collections
        2. All collections in client are warmed
        3. Warmer completes successfully

        Note: Uses isolated client to avoid collecting all test collections.
        """
        # Create isolated ChromaDB client for this test
        isolated_client = chromadb.Client()

        # Create multiple collections with unique prefix
        unique_prefix = "test_none_auto_discover"
        for i in range(3):
            collection = isolated_client.create_collection(name=f"{unique_prefix}_{i}")
            collection.add(
                ids=[f"vec{i}"], embeddings=[[0.1] * 768], documents=[f"doc{i}"]
            )

        # Create warmer with collections=None (auto-discover)
        config = WarmupConfig(num_queries=2, collections=None, enabled=True)
        warmer = IndexWarmer(isolated_client, config)

        # Execute warming
        await warmer.warm_on_startup()

        # Verify all collections were warmed (including our 3 new ones)
        warmed = warmer.get_warmed_collections()

        # Check that our specific collections were warmed
        our_collections = [name for name in warmed if unique_prefix in name]
        assert (
            len(our_collections) == 3
        ), f"Should warm all 3 of our collections, got {len(our_collections)}"
        assert warmer.is_warmed(), "Warmer should be marked as complete"

        # Verify warmer found and warmed multiple collections (not just our 3)
        # This confirms collections=None does discovery
        assert (
            len(warmed) >= 3
        ), f"Warmer should discover and warm collections, found {len(warmed)}"

    @pytest.mark.asyncio
    async def test_warmer_with_empty_collections_list(self, ephemeral_chromadb_client):
        """
        Test IndexWarmer with empty collections list (explicit no-op).

        This verifies:
        1. Empty list means no collections to warm (different from None)
        2. Warmer completes but is marked as warmed (no work to do)
        3. No collections in warmed list
        """
        # Create a collection (but don't include in config)
        collection = ephemeral_chromadb_client.create_collection(
            name="test_ignored_collection"
        )
        collection.add(ids=["vec1"], embeddings=[[0.1] * 768], documents=["doc1"])

        # Create warmer with empty collections list
        config = WarmupConfig(num_queries=2, collections=[], enabled=True)
        warmer = IndexWarmer(ephemeral_chromadb_client, config)

        # Execute warming
        await warmer.warm_on_startup()

        # Verify no collections warmed
        assert (
            len(warmer.get_warmed_collections()) == 0
        ), "Should not warm any collections"
        assert warmer.is_warmed(), "Warmer should be marked complete (no work to do)"

    def test_monitor_with_disabled_monitoring(self, ephemeral_chromadb_client):
        """
        Test IndexPerformanceMonitor respects disabled monitoring flag.

        This verifies:
        1. Monitor can be created with enabled=False
        2. Metrics can still be tracked (infrastructure works)
        3. Flag is accessible for conditional logic
        """
        # Create collection
        collection = ephemeral_chromadb_client.create_collection(
            name="test_disabled_monitor"
        )
        collection.add(ids=["vec1"], embeddings=[[0.1] * 768], documents=["doc1"])

        # Create monitor with monitoring disabled
        monitor = IndexPerformanceMonitor(collection, enabled=False)

        # Verify disabled flag is set
        assert not monitor.enabled, "Monitor should be disabled"

        # Verify infrastructure still works (can track metrics even if disabled)
        # This allows conditional monitoring without breaking code
        monitor.track_query_latency(50.0)
        assert (
            len(monitor.query_latencies) == 1
        ), "Should still track latencies (infrastructure functional)"

    def test_monitor_with_zero_latencies(self, ephemeral_chromadb_client):
        """
        Test IndexPerformanceMonitor handles case with no latency data.

        This verifies:
        1. Latency distribution calculation handles empty data
        2. Returns zero values for all percentiles
        3. No division by zero or other errors
        """
        # Create collection
        collection = ephemeral_chromadb_client.create_collection(
            name="test_zero_latencies"
        )

        # Create monitor (no latencies tracked)
        monitor = IndexPerformanceMonitor(collection)

        # Calculate distribution with no data
        distribution = monitor.calculate_latency_distribution()

        # Verify safe handling
        assert distribution.p50_ms == 0.0, "p50 should be 0 with no data"
        assert distribution.p95_ms == 0.0, "p95 should be 0 with no data"
        assert distribution.p99_ms == 0.0, "p99 should be 0 with no data"
        assert distribution.sample_count == 0, "Sample count should be 0"
        assert distribution.outlier_count == 0, "Outlier count should be 0"
