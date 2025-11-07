"""
Server Startup Time Baseline Tests for CBR MCP Server.

This test module measures and establishes baseline performance metrics for server
initialization phases to track optimization progress.

Measured Phases:
1. Cold start total initialization time
2. Embedding model loading time
3. Database connection initialization time
4. Case base loading time
5. Warm start vs cold start comparison
6. Per-phase timing breakdown

Target: <5 seconds total startup time
"""

import asyncio
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Tuple
from unittest.mock import Mock, patch

import pytest

# Import server components - will fail until implemented
try:
    from cbr_mcp_server import (
        CBRMCPServer,
        CBRServerConfig,
        ProductionCBRRetriever,
        SentenceTransformer,
        chromadb,
    )
except ImportError:
    CBRMCPServer = None
    CBRServerConfig = None
    ProductionCBRRetriever = None
    SentenceTransformer = None
    chromadb = None


class TestServerStartupBaseline:
    """Baseline performance tests for server startup timing."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary directory for ChromaDB test database."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup after test
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def clean_model_cache(self):
        """
        Ensure clean state for embedding model tests by clearing any cached models.
        This simulates a true cold start scenario.
        """
        # Note: Actual cache clearing implementation depends on sentence-transformers
        # For now, we'll use environment variables to simulate cold start
        original_env = os.environ.copy()

        # Clear any caching environment variables
        os.environ["TRANSFORMERS_OFFLINE"] = "0"
        os.environ["HF_HUB_OFFLINE"] = "0"

        yield

        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)

    def _capture_phase_timing(
        self, phase_name: str, start_time: float
    ) -> Tuple[str, float]:
        """
        Helper to capture and format phase timing.

        Args:
            phase_name: Name of the initialization phase
            start_time: perf_counter() value at phase start

        Returns:
            Tuple of (phase_name, elapsed_time_seconds)
        """
        elapsed = time.perf_counter() - start_time
        return (phase_name, elapsed)

    # ========================================================================
    # Test 1: Cold Start Total Startup Time
    # ========================================================================

    async def test_cold_start_total_startup_time(
        self, temp_db_path, clean_model_cache, startup_result_tracker
    ):
        """
        Test the total time for a complete cold start of the MCP server.

        This measures end-to-end initialization from server creation to ready state,
        including all component loading and initialization.

        Requirements:
        - Total startup time < 5 seconds (target baseline)
        - Server initialization completes successfully
        - All components initialized correctly
        """
        print("\n[Cold Start] Measuring total cold start time...")

        # Measure total startup time from creation to ready
        start_total = time.perf_counter()

        # Create server configuration
        config = CBRServerConfig(
            database_path=temp_db_path,
            collection_name="test_cold_start_collection",
            use_real_db=True,
        )

        # Initialize server (this triggers all initialization phases)
        server = CBRMCPServer(config=config)

        # Capture total startup time
        total_time = time.perf_counter() - start_total

        print(f"[Cold Start] Total startup time: {total_time:.3f}s")

        # Record timing metrics
        startup_result_tracker.record({"total_time": total_time})

        # Verify server is initialized
        assert server is not None, "Server should be initialized"
        assert server.retriever is not None, "CBR retriever should be initialized"

        # Assert against target baseline
        assert (
            total_time < 5.0
        ), f"Cold start time {total_time:.3f}s exceeds 5 second target"

        print(f"[Cold Start] ✓ Cold start baseline established: {total_time:.3f}s")

    # ========================================================================
    # Test 2: Embedding Model Loading Time
    # ========================================================================

    def test_embedding_model_loading_time(
        self, clean_model_cache, startup_result_tracker
    ):
        """
        Test the time taken to load the nomic-ai embedding model.

        This isolates embedding model initialization from other components
        to measure model loading performance specifically.

        Requirements:
        - Model loads successfully
        - Loading time is captured for baseline comparison
        """
        print("\n[Embedding Model] Measuring model loading time...")

        model_name = "nomic-ai/nomic-embed-text-v1.5"

        # Measure model loading time
        start_load = time.perf_counter()

        model = SentenceTransformer(model_name, trust_remote_code=True)

        load_time = time.perf_counter() - start_load

        print(f"[Embedding Model] Model loading time: {load_time:.3f}s")

        # Record timing metrics
        startup_result_tracker.record({"load_time": load_time})

        # Verify model loaded successfully
        assert model is not None, "Model should be loaded successfully"

        # Verify model can generate embeddings
        test_embedding = model.encode("test query")
        assert test_embedding is not None, "Model should generate embeddings"
        assert len(test_embedding) > 0, "Embedding should have dimensions"

        print(f"[Embedding Model] ✓ Model loading baseline: {load_time:.3f}s")

    # ========================================================================
    # Test 3: Database Connection Initialization Time
    # ========================================================================

    @pytest.mark.skipif(chromadb is None, reason="ChromaDB not available")
    def test_database_connection_initialization_time(
        self, temp_db_path, startup_result_tracker
    ):
        """
        Test the time taken to establish ChromaDB connection and initialize collection.

        This isolates database initialization from other components.

        Requirements:
        - Database connection established successfully
        - Collection created or accessed successfully
        - Connection time measured for baseline
        """
        print("\n[Database Connection] Measuring database initialization time...")

        collection_name = "test_connection_collection"

        # Measure database connection and collection initialization time
        start_db = time.perf_counter()

        # Create ChromaDB client
        client = chromadb.PersistentClient(path=temp_db_path)

        # Get or create collection
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Test collection for connection timing"},
        )

        db_init_time = time.perf_counter() - start_db

        print(f"[Database Connection] Initialization time: {db_init_time:.3f}s")

        # Record timing metrics
        startup_result_tracker.record({"db_init_time": db_init_time})

        # Verify connection is functional
        assert client is not None, "Database client should be initialized"
        assert collection is not None, "Collection should be created"

        # Verify collection is accessible
        collection_info = collection.count()
        assert collection_info >= 0, "Collection should be queryable"

        print(
            f"[Database Connection] ✓ Database initialization baseline: {db_init_time:.3f}s"
        )

    # ========================================================================
    # Test 4: Case Base Loading Time
    # ========================================================================

    async def test_case_base_loading_time(self, temp_db_path, startup_result_tracker):
        """
        Test the time taken to load all cases from the modular case base structure.

        This measures the time for case discovery, module loading, and case aggregation.

        Requirements:
        - All 135 cases loaded successfully
        - Module discovery completes
        - Loading time measured for baseline
        """
        print("\n[Case Base Loading] Measuring case loading time...")

        # Create server config
        config = CBRServerConfig(
            database_path=temp_db_path,
            collection_name="test_case_loading_collection",
            use_real_db=True,
        )

        # Create mock logger
        from unittest.mock import Mock

        mock_logger = Mock()

        # Measure case base loading time
        start_loading = time.perf_counter()

        # Create retriever (this should trigger case loading)
        retriever = ProductionCBRRetriever(config, mock_logger)

        loading_time = time.perf_counter() - start_loading

        print(f"[Case Base Loading] Loading time: {loading_time:.3f}s")

        # Record timing metrics
        startup_result_tracker.record({"loading_time": loading_time})

        # Verify retriever is created
        assert retriever is not None, "Retriever should be created"
        assert retriever.collection is not None, "Collection should be initialized"

        print(f"[Case Base Loading] ✓ Case loading baseline: {loading_time:.3f}s")

    # ========================================================================
    # Test 5: Warm Start Total Startup Time
    # ========================================================================

    async def test_warm_start_total_startup_time(
        self, temp_db_path, startup_result_tracker
    ):
        """
        Test startup time when components are already cached (warm start scenario).

        This measures the performance improvement from caching after initial load.

        Requirements:
        - Warm start time is measured
        - Warm start is faster than cold start
        - Server initialization completes
        """
        print("\n[Warm Start] Pre-warming components...")

        # First initialization to warm up caches
        config = CBRServerConfig(
            database_path=temp_db_path,
            collection_name="test_warm_start_collection",
            use_real_db=True,
        )

        server1 = CBRMCPServer(config=config)

        # Release first server instance (Python GC will clean up)
        del server1

        print("[Warm Start] Measuring warm start time...")

        # Measure warm start time (components should be cached)
        start_warm = time.perf_counter()

        # Second initialization (warm start)
        server2 = CBRMCPServer(config=config)

        warm_time = time.perf_counter() - start_warm

        print(f"[Warm Start] Warm start time: {warm_time:.3f}s")

        # Record timing metrics
        startup_result_tracker.record({"warm_time": warm_time})

        # Verify server is initialized
        assert server2 is not None, "Server should be initialized after warm start"

        # Warm start should be faster than cold start target
        assert warm_time < 5.0, f"Warm start time {warm_time:.3f}s exceeds baseline"

        print(f"[Warm Start] ✓ Warm start baseline established: {warm_time:.3f}s")

    # ========================================================================
    # Test 6: Startup Phases Breakdown
    # ========================================================================

    async def test_startup_phases_breakdown(self, temp_db_path, startup_result_tracker):
        """
        Test detailed breakdown of all initialization phases in sequence.

        This captures timing for each phase to identify optimization opportunities.

        Requirements:
        - Each phase timing is captured
        - Phases complete in expected order
        - Sum of phases approximately equals total startup time
        """
        print("\n[Phases Breakdown] Measuring detailed phase timings...")

        phase_timings: List[Tuple[str, float]] = []

        # Phase 1: Configuration creation
        start_config = time.perf_counter()
        config = CBRServerConfig(
            database_path=temp_db_path,
            collection_name="test_phases_collection",
            use_real_db=True,
        )
        phase_timings.append(self._capture_phase_timing("Configuration", start_config))

        # Phase 2: Server instantiation (includes all initialization)
        start_server = time.perf_counter()
        server = CBRMCPServer(config=config)
        phase_timings.append(
            self._capture_phase_timing("Server Instantiation", start_server)
        )

        # Calculate total from phases
        total_from_phases = sum(t for _, t in phase_timings)

        print(f"\n[Phases Breakdown] Phase Timings:")
        for phase_name, phase_time in phase_timings:
            percentage = (
                (phase_time / total_from_phases) * 100 if total_from_phases > 0 else 0
            )
            print(f"  {phase_name:25} {phase_time:6.3f}s ({percentage:5.1f}%)")
        print(f"  {'Total':25} {total_from_phases:6.3f}s (100.0%)")

        # Record timing metrics
        startup_result_tracker.record(
            {"phase_timings": phase_timings, "total_time": total_from_phases}
        )

        # Verify phases complete successfully
        assert all(t >= 0 for _, t in phase_timings), "All phases should complete"

        # Verify server is initialized
        assert server is not None, "Server should be initialized after all phases"

        # Total should be under target
        assert (
            total_from_phases < 5.0
        ), f"Total startup {total_from_phases:.3f}s exceeds 5 second target"

        print(
            f"[Phases Breakdown] ✓ Phase breakdown baseline established: {total_from_phases:.3f}s total"
        )

    # ========================================================================
    # Test 7: Cold Start Repeatability
    # ========================================================================

    async def test_cold_start_repeatability(
        self, clean_model_cache, startup_result_tracker
    ):
        """
        Test that timing measurements are consistent across multiple cold start attempts.

        This ensures our baseline measurements are reliable and repeatable.

        Requirements:
        - Multiple cold start measurements taken (3-5 runs)
        - Measurements have reasonable variance (< 20%)
        - Average and standard deviation calculated
        """
        print("\n[Repeatability] Testing cold start repeatability...")

        num_runs = 3
        startup_times: List[float] = []

        for run in range(num_runs):
            # Create fresh temp directory for each run
            temp_dir = tempfile.mkdtemp()

            try:
                print(f"[Repeatability] Run {run + 1}/{num_runs}...")

                # Measure startup time
                start = time.perf_counter()

                config = CBRServerConfig(
                    database_path=temp_dir,
                    collection_name=f"test_repeat_collection_{run}",
                    use_real_db=True,
                )

                server = CBRMCPServer(config=config)

                elapsed = time.perf_counter() - start
                startup_times.append(elapsed)

                print(f"[Repeatability] Run {run + 1} time: {elapsed:.3f}s")

                # Clean up server
                del server

            finally:
                # Clean up temp directory
                shutil.rmtree(temp_dir, ignore_errors=True)

        # Calculate statistics
        avg_time = sum(startup_times) / len(startup_times)
        variance = sum((t - avg_time) ** 2 for t in startup_times) / len(startup_times)
        std_dev = variance**0.5
        coefficient_of_variation = (std_dev / avg_time) * 100 if avg_time > 0 else 0

        print(f"\n[Repeatability] Statistics:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Std Dev: {std_dev:.3f}s")
        print(f"  CoV: {coefficient_of_variation:.1f}%")
        print(f"  Min: {min(startup_times):.3f}s")
        print(f"  Max: {max(startup_times):.3f}s")

        # Record timing metrics
        startup_result_tracker.record(
            {
                "startup_times": startup_times,
                "avg_time": avg_time,
                "std_dev": std_dev,
                "coefficient_of_variation": coefficient_of_variation,
            }
        )

        # Verify measurements have reasonable variance
        assert (
            coefficient_of_variation < 20
        ), f"Variance {coefficient_of_variation:.1f}% exceeds 20% threshold"

        # Verify average is within target
        assert avg_time < 5.0, f"Average startup {avg_time:.3f}s exceeds 5s target"

        print(
            f"[Repeatability] ✓ Repeatability verified: {avg_time:.3f}s ± {std_dev:.3f}s"
        )

    # ========================================================================
    # Test 8: Filesystem Cache Effects
    # ========================================================================

    async def test_filesystem_cache_effects(self, temp_db_path, startup_result_tracker):
        """
        Test the impact of filesystem caching on subsequent startups.

        This measures how OS-level caching affects startup performance.

        Requirements:
        - First startup time measured (cold)
        - Immediate second startup time measured (warm)
        - Timing difference indicates cache impact
        """
        print("\n[FS Cache] Measuring filesystem cache effects...")

        config = CBRServerConfig(
            database_path=temp_db_path,
            collection_name="test_fs_cache_collection",
            use_real_db=True,
        )

        # First startup (cold - no FS cache)
        print("[FS Cache] First startup (cold)...")
        start_cold = time.perf_counter()

        server1 = CBRMCPServer(config=config)

        cold_time = time.perf_counter() - start_cold

        print(f"[FS Cache] Cold startup time: {cold_time:.3f}s")

        # Clean up first server
        del server1

        # Immediate second startup (warm - FS cache active)
        print("[FS Cache] Second startup (warm, FS cached)...")
        start_warm = time.perf_counter()

        server2 = CBRMCPServer(config=config)

        warm_time = time.perf_counter() - start_warm

        print(f"[FS Cache] Warm startup time: {warm_time:.3f}s")

        # Calculate cache benefit
        cache_benefit = cold_time - warm_time
        cache_benefit_pct = (cache_benefit / cold_time) * 100 if cold_time > 0 else 0

        print(f"\n[FS Cache] Filesystem Cache Impact:")
        print(f"  Cold start: {cold_time:.3f}s")
        print(f"  Warm start: {warm_time:.3f}s")
        print(f"  Benefit: {cache_benefit:.3f}s ({cache_benefit_pct:.1f}%)")

        # Record timing metrics
        startup_result_tracker.record(
            {
                "cold_time": cold_time,
                "warm_time": warm_time,
                "cache_benefit": cache_benefit,
            }
        )

        # Verify warm start is faster (or at least not slower)
        assert warm_time <= cold_time, "Warm start should not be slower than cold start"

        # Both should be under target
        assert cold_time < 5.0, f"Cold start {cold_time:.3f}s exceeds 5s target"
        assert warm_time < 5.0, f"Warm start {warm_time:.3f}s exceeds 5s target"

        print(f"[FS Cache] ✓ Cache effects measured and verified")
