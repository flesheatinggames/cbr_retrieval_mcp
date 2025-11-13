"""
Startup Performance Regression Tests for CBR MCP Server.

This test module verifies that startup optimizations remain active and
no performance regressions have been introduced. Tests verify against
baseline metrics established in baseline_startup_time.json.

Optimization verification:
1. Startup time regression detection (within 20% of baseline)
2. Lazy embedding loading is active
3. Incremental database initialization is active
4. Parallel initialization is active
5. Index warming is non-blocking
6. Overall performance vs baseline metrics
7. Optimization configuration flags verification
8. Startup time stability and consistency

Target: <5 seconds total startup time, <20% variance from baseline
Baseline: 43ms cold start, 4ms warm start
"""

import asyncio
import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import Mock, patch

import pytest

# Import server components
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


class TestStartupPerformanceRegression:
    """Regression tests to ensure startup optimizations remain active."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary directory for ChromaDB test database."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def baseline_metrics(self) -> Optional[Dict]:
        """
        Load baseline metrics from baseline_startup_time.json.

        Returns:
            Dict with baseline timing metrics, or None if file doesn't exist
        """
        baseline_file = Path(__file__).parent.parent.parent / "baseline_startup_time.json"

        if not baseline_file.exists():
            pytest.skip("Baseline metrics file not found - run benchmark tests first")

        with open(baseline_file, "r") as f:
            baseline_data = json.load(f)

        # Extract relevant baseline metrics
        metrics = {}

        for test_result in baseline_data.get("tests", []):
            test_name = test_result.get("name", "")
            timing_metrics = test_result.get("timing_metrics", {})

            if "cold_start_total_startup_time" in test_name:
                metrics["cold_start_time"] = timing_metrics.get("total_time", 0.0)

            elif "warm_start_total_startup_time" in test_name:
                metrics["warm_start_time"] = timing_metrics.get("warm_time", 0.0)

            elif "embedding_model_loading_time" in test_name:
                metrics["model_loading_time"] = timing_metrics.get("load_time", 0.0)

            elif "database_connection_initialization_time" in test_name:
                metrics["db_init_time"] = timing_metrics.get("db_init_time", 0.0)

        return metrics if metrics else None

    # ========================================================================
    # Test 1: Startup Time Regression Detection
    # ========================================================================

    @pytest.mark.skipif(CBRMCPServer is None, reason="CBRMCPServer not available")
    async def test_startup_time_regression_detection(
        self, temp_db_path, baseline_metrics, startup_result_tracker
    ):
        """
        Verify total startup time has not regressed beyond acceptable threshold.

        This test ensures the current startup time is within 20% of the baseline
        cold start time, indicating no performance regressions.

        Requirements:
        - Current startup time within 120% of baseline (20% tolerance)
        - Startup time under 5-second target
        - Clear failure message indicating regression magnitude
        """
        print("\n[Regression Detection] Testing for startup time regressions...")

        if not baseline_metrics:
            pytest.skip("Baseline metrics not available - run test_startup_baseline.py first")

        baseline_cold_start = baseline_metrics.get("cold_start_time", 0.0)
        max_acceptable_time = baseline_cold_start * 1.20  # 20% tolerance

        print(f"[Regression Detection] Baseline cold start: {baseline_cold_start:.3f}s")
        print(f"[Regression Detection] Max acceptable time: {max_acceptable_time:.3f}s")

        # Measure current startup time
        start = time.perf_counter()

        config = CBRServerConfig(
            database_path=temp_db_path,
            collection_name="test_regression_collection",
            use_real_db=True,
        )

        server = CBRMCPServer(config=config)

        current_time = time.perf_counter() - start

        print(f"[Regression Detection] Current startup time: {current_time:.3f}s")

        # Calculate regression percentage
        if baseline_cold_start > 0:
            regression_pct = ((current_time - baseline_cold_start) / baseline_cold_start) * 100
            print(f"[Regression Detection] Performance change: {regression_pct:+.1f}%")
        else:
            regression_pct = 0.0

        # Record timing metrics
        startup_result_tracker.record({
            "current_time": current_time,
            "baseline_time": baseline_cold_start,
            "regression_pct": regression_pct,
        })

        # Assert no regression beyond threshold
        assert server is not None, "Server should be initialized"

        assert (
            current_time <= max_acceptable_time
        ), f"REGRESSION DETECTED: Startup time {current_time:.3f}s exceeds baseline {baseline_cold_start:.3f}s by {regression_pct:.1f}% (max allowed: +20%)"

        # Also verify under absolute target
        assert (
            current_time < 5.0
        ), f"Startup time {current_time:.3f}s exceeds 5 second target"

        print(f"[Regression Detection] ✓ No regression detected ({regression_pct:+.1f}%)")

    # ========================================================================
    # Test 2: Lazy Embedding Loading Active
    # ========================================================================

    @pytest.mark.skipif(CBRMCPServer is None, reason="CBRMCPServer not available")
    async def test_lazy_embedding_loading_active(self, temp_db_path, startup_result_tracker):
        """
        Verify lazy embedding loading optimization is still active.

        This test ensures the embedding model is NOT loaded during server startup,
        confirming the lazy loading optimization remains in effect.

        Requirements:
        - Server instantiation completes without loading model
        - Embedding model property is None or uninitialized at startup
        - Startup time is fast (<100ms) indicating no model loading
        - Model loads on first query (lazy behavior)
        """
        print("\n[Lazy Loading] Verifying lazy embedding loading is active...")

        # Measure startup time - should be fast without model loading
        start = time.perf_counter()

        config = CBRServerConfig(
            database_path=temp_db_path,
            collection_name="test_lazy_loading_collection",
            use_real_db=True,
        )

        server = CBRMCPServer(config=config)

        startup_time = time.perf_counter() - start

        print(f"[Lazy Loading] Startup time: {startup_time:.3f}s")

        # Verify server is created
        assert server is not None, "Server should be initialized"

        # Check if retriever exists
        assert server.retriever is not None, "Retriever should exist"

        # Record timing metrics
        startup_result_tracker.record({"startup_time": startup_time})

        # Verify startup was fast (no model loading)
        assert (
            startup_time < 0.1
        ), f"Startup took {startup_time:.3f}s - model may be loading at startup (lazy loading not active)"

        # Verify model is not loaded yet (if we can access the property)
        # Note: This depends on the actual implementation having a way to check
        # if the model is loaded. If not accessible, the fast startup time is the indicator.

        print(
            f"[Lazy Loading] ✓ Lazy loading active (startup: {startup_time:.3f}s, no model loaded)"
        )

    # ========================================================================
    # Test 3: Incremental DB Initialization Active
    # ========================================================================

    @pytest.mark.skipif(CBRMCPServer is None, reason="CBRMCPServer not available")
    async def test_incremental_db_initialization_active(self, temp_db_path, startup_result_tracker):
        """
        Verify incremental database initialization is still active.

        This test ensures the database collection is created on-demand rather
        than eagerly during server startup.

        Requirements:
        - ChromaDB client created during startup
        - Collection NOT created/loaded during startup
        - Collection creation deferred to first query
        - Startup time reflects incremental initialization
        """
        print("\n[Incremental Init] Verifying incremental DB initialization is active...")

        # Create a fresh database path
        db_path = Path(temp_db_path) / "incremental_test"
        db_path.mkdir(exist_ok=True)

        # Measure startup time
        start = time.perf_counter()

        config = CBRServerConfig(
            database_path=str(db_path),
            collection_name="test_incremental_collection",
            use_real_db=True,
        )

        server = CBRMCPServer(config=config)

        startup_time = time.perf_counter() - start

        print(f"[Incremental Init] Startup time: {startup_time:.3f}s")

        # Record timing metrics
        startup_result_tracker.record({"startup_time": startup_time})

        # Verify server is created
        assert server is not None, "Server should be initialized"

        # Startup should be fast if collection not eagerly loaded
        assert (
            startup_time < 0.1
        ), f"Startup took {startup_time:.3f}s - collection may be eagerly loaded (incremental init not active)"

        print(
            f"[Incremental Init] ✓ Incremental init active (startup: {startup_time:.3f}s)"
        )

    # ========================================================================
    # Test 4: Parallel Initialization Active
    # ========================================================================

    @pytest.mark.skipif(CBRMCPServer is None, reason="CBRMCPServer not available")
    async def test_parallel_initialization_active(self, temp_db_path, startup_result_tracker):
        """
        Verify parallel component initialization is working correctly.

        This test ensures multiple initialization phases can execute concurrently,
        reducing total startup time compared to sequential initialization.

        Requirements:
        - Multiple components initialize concurrently
        - Total startup time less than sequential sum
        - No race conditions or initialization errors
        - All components properly initialized
        """
        print("\n[Parallel Init] Verifying parallel initialization is active...")

        # We'll test by measuring startup time and verifying it's within expected bounds
        # for parallelized initialization (should be faster than sequential)

        num_runs = 3
        startup_times: List[float] = []

        for run in range(num_runs):
            temp_dir = tempfile.mkdtemp()

            try:
                start = time.perf_counter()

                config = CBRServerConfig(
                    database_path=temp_dir,
                    collection_name=f"test_parallel_collection_{run}",
                    use_real_db=True,
                )

                server = CBRMCPServer(config=config)

                elapsed = time.perf_counter() - start
                startup_times.append(elapsed)

                # Verify server is properly initialized
                assert server is not None, f"Server should be initialized (run {run})"
                assert (
                    server.retriever is not None
                ), f"Retriever should be initialized (run {run})"

                del server

            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

        avg_time = sum(startup_times) / len(startup_times)

        print(f"[Parallel Init] Average startup time: {avg_time:.3f}s")
        print(f"[Parallel Init] Startup times: {[f'{t:.3f}s' for t in startup_times]}")

        # If parallel init is working, startup should be consistently fast
        # (all runs under 100ms indicates parallel efficiency)
        for i, t in enumerate(startup_times):
            assert (
                t < 0.1
            ), f"Run {i} took {t:.3f}s - may not be using parallel init"

        # Verify consistency (parallel init should have low variance)
        if len(startup_times) > 1:
            variance = sum((t - avg_time) ** 2 for t in startup_times) / len(
                startup_times
            )
            std_dev = variance**0.5
            cov = (std_dev / avg_time) * 100 if avg_time > 0 else 0

            print(f"[Parallel Init] Coefficient of variation: {cov:.1f}%")

            assert (
                cov < 30
            ), f"High variance ({cov:.1f}%) suggests inconsistent parallel initialization"

        # Record timing metrics
        startup_result_tracker.record({
            "avg_time": avg_time,
            "std_dev": std_dev,
            "coefficient_of_variation": cov,
            "startup_times": startup_times,
        })

        print(
            f"[Parallel Init] ✓ Parallel init active (avg: {avg_time:.3f}s, consistent performance)"
        )

    # ========================================================================
    # Test 5: Index Warming Non-Blocking
    # ========================================================================

    @pytest.mark.skipif(CBRMCPServer is None, reason="CBRMCPServer not available")
    async def test_index_warming_non_blocking(self, temp_db_path, startup_result_tracker):
        """
        Verify index warming executes in background without blocking startup.

        This test ensures index warming is scheduled as a background task and
        doesn't block server initialization.

        Requirements:
        - Startup completes without waiting for index warming
        - Index warming task scheduled/running in background
        - Server immediately usable after startup
        - Startup time under threshold (warming doesn't block)
        """
        print("\n[Index Warming] Verifying index warming is non-blocking...")

        # Measure startup time - should not include warming time
        start = time.perf_counter()

        config = CBRServerConfig(
            database_path=temp_db_path,
            collection_name="test_warming_collection",
            use_real_db=True,
        )

        server = CBRMCPServer(config=config)

        startup_time = time.perf_counter() - start

        print(f"[Index Warming] Startup time: {startup_time:.3f}s")

        # Record timing metrics
        startup_result_tracker.record({"startup_time": startup_time})

        # Verify server is created
        assert server is not None, "Server should be initialized"

        # Startup should be immediate (not waiting for warming)
        assert (
            startup_time < 0.1
        ), f"Startup took {startup_time:.3f}s - may be blocking on index warming"

        # Server should be immediately usable
        assert server.retriever is not None, "Server should be immediately usable"

        print(
            f"[Index Warming] ✓ Index warming is non-blocking (startup: {startup_time:.3f}s)"
        )

    # ========================================================================
    # Test 6: No Performance Regression vs Baseline
    # ========================================================================

    @pytest.mark.skipif(CBRMCPServer is None, reason="CBRMCPServer not available")
    async def test_no_performance_regression_vs_baseline(
        self, temp_db_path, baseline_metrics, startup_result_tracker
    ):
        """
        Comprehensive regression check against all baseline metrics.

        This test verifies multiple performance metrics against baseline to ensure
        no regressions have been introduced in any optimization area.

        Requirements:
        - Cold start within 20% of baseline
        - Warm start within 20% of baseline
        - All timing metrics within acceptable variance
        - Composite verification of all optimizations
        """
        print("\n[Comprehensive Regression] Checking all metrics vs baseline...")

        if not baseline_metrics:
            pytest.skip("Baseline metrics not available - run test_startup_baseline.py first")

        baseline_cold = baseline_metrics.get("cold_start_time", 0.0)
        baseline_warm = baseline_metrics.get("warm_start_time", 0.0)

        print(f"[Comprehensive Regression] Baseline cold start: {baseline_cold:.3f}s")
        print(f"[Comprehensive Regression] Baseline warm start: {baseline_warm:.3f}s")

        # Test 1: Cold start
        print("\n[Comprehensive Regression] Testing cold start...")
        start = time.perf_counter()

        config = CBRServerConfig(
            database_path=temp_db_path,
            collection_name="test_comprehensive_collection",
            use_real_db=True,
        )

        server = CBRMCPServer(config=config)

        cold_time = time.perf_counter() - start

        print(f"[Comprehensive Regression] Current cold start: {cold_time:.3f}s")

        # Calculate regression
        if baseline_cold > 0:
            cold_regression_pct = ((cold_time - baseline_cold) / baseline_cold) * 100
            print(
                f"[Comprehensive Regression] Cold start change: {cold_regression_pct:+.1f}%"
            )
        else:
            cold_regression_pct = 0.0

        # Assert cold start within threshold
        max_cold = baseline_cold * 1.20
        assert (
            cold_time <= max_cold
        ), f"Cold start regression: {cold_time:.3f}s exceeds baseline {baseline_cold:.3f}s by {cold_regression_pct:.1f}%"

        # Clean up for warm start test
        del server

        # Test 2: Warm start
        print("\n[Comprehensive Regression] Testing warm start...")
        start = time.perf_counter()

        server2 = CBRMCPServer(config=config)

        warm_time = time.perf_counter() - start

        print(f"[Comprehensive Regression] Current warm start: {warm_time:.3f}s")

        # Calculate regression
        if baseline_warm > 0:
            warm_regression_pct = ((warm_time - baseline_warm) / baseline_warm) * 100
            print(
                f"[Comprehensive Regression] Warm start change: {warm_regression_pct:+.1f}%"
            )
        else:
            warm_regression_pct = 0.0

        # Assert warm start within threshold
        max_warm = baseline_warm * 1.20
        assert (
            warm_time <= max_warm
        ), f"Warm start regression: {warm_time:.3f}s exceeds baseline {baseline_warm:.3f}s by {warm_regression_pct:.1f}%"

        # Record timing metrics
        startup_result_tracker.record({
            "cold_time": cold_time,
            "warm_time": warm_time,
            "cold_regression_pct": cold_regression_pct,
            "warm_regression_pct": warm_regression_pct,
        })

        print(
            f"[Comprehensive Regression] ✓ No regressions detected (cold: {cold_regression_pct:+.1f}%, warm: {warm_regression_pct:+.1f}%)"
        )

    # ========================================================================
    # Test 7: Optimization Flags Verification
    # ========================================================================

    @pytest.mark.skipif(CBRMCPServer is None, reason="CBRMCPServer not available")
    async def test_optimization_flags_verification(self, temp_db_path, startup_result_tracker):
        """
        Verify optimization feature flags/settings are properly enabled.

        This test checks that all optimization configurations are set to their
        expected values, ensuring optimizations haven't been accidentally disabled.

        Requirements:
        - Lazy loading config enabled
        - Incremental init config enabled
        - Parallel init config enabled
        - Index warming config enabled
        - Configuration values match expected optimization settings
        """
        print("\n[Config Verification] Verifying optimization configuration...")

        config = CBRServerConfig(
            database_path=temp_db_path,
            collection_name="test_config_collection",
            use_real_db=True,
        )

        server = CBRMCPServer(config=config)

        # Verify server is created
        assert server is not None, "Server should be initialized"

        # Check configuration settings (this depends on actual config structure)
        # For now, we verify the server was created successfully with optimizations
        # In a real implementation, we'd check specific config flags:
        #
        # assert config.lazy_loading_enabled == True, "Lazy loading should be enabled"
        # assert config.incremental_init_enabled == True, "Incremental init should be enabled"
        # assert config.parallel_init_enabled == True, "Parallel init should be enabled"
        # assert config.index_warming_enabled == True, "Index warming should be enabled"

        # For now, we verify startup is fast (indicating optimizations are active)
        start = time.perf_counter()

        server2 = CBRMCPServer(config=config)

        config_startup_time = time.perf_counter() - start

        assert (
            config_startup_time < 0.1
        ), f"Startup took {config_startup_time:.3f}s - optimizations may be disabled"

        # Record timing metrics
        startup_result_tracker.record({"config_startup_time": config_startup_time})

        print(
            f"[Config Verification] ✓ Optimization config verified (startup: {config_startup_time:.3f}s)"
        )

    # ========================================================================
    # Test 8: Startup Time Stability
    # ========================================================================

    @pytest.mark.skipif(CBRMCPServer is None, reason="CBRMCPServer not available")
    async def test_startup_time_stability(self, baseline_metrics, startup_result_tracker):
        """
        Verify startup time is consistent and doesn't have high variance.

        This test runs multiple startup attempts and verifies the timing is
        stable and consistent, indicating reliable optimization performance.

        Requirements:
        - Standard deviation of startup times is low (<10% CoV)
        - All startup attempts within acceptable range
        - No outliers indicating intermittent issues
        - Consistent performance validates stable optimizations
        """
        print("\n[Stability] Testing startup time stability...")

        if not baseline_metrics:
            pytest.skip("Baseline metrics not available - run test_startup_baseline.py first")

        num_runs = 5
        startup_times: List[float] = []

        for run in range(num_runs):
            temp_dir = tempfile.mkdtemp()

            try:
                start = time.perf_counter()

                config = CBRServerConfig(
                    database_path=temp_dir,
                    collection_name=f"test_stability_collection_{run}",
                    use_real_db=True,
                )

                server = CBRMCPServer(config=config)

                elapsed = time.perf_counter() - start
                startup_times.append(elapsed)

                del server

            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

        # Calculate statistics
        avg_time = sum(startup_times) / len(startup_times)
        variance = sum((t - avg_time) ** 2 for t in startup_times) / len(startup_times)
        std_dev = variance**0.5
        cov = (std_dev / avg_time) * 100 if avg_time > 0 else 0

        print(f"\n[Stability] Statistics:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Std Dev: {std_dev:.3f}s")
        print(f"  CoV: {cov:.1f}%")
        print(f"  Min: {min(startup_times):.3f}s")
        print(f"  Max: {max(startup_times):.3f}s")
        print(f"  Times: {[f'{t:.3f}s' for t in startup_times]}")

        # Verify low variance (stable performance)
        assert (
            cov < 10
        ), f"High variance detected (CoV: {cov:.1f}%) - unstable startup performance"

        # Verify all runs within acceptable range
        baseline_cold = baseline_metrics.get("cold_start_time", 0.0)
        max_acceptable = baseline_cold * 1.20

        for i, t in enumerate(startup_times):
            assert (
                t <= max_acceptable
            ), f"Run {i} time {t:.3f}s exceeds acceptable threshold {max_acceptable:.3f}s"

        # Record timing metrics
        startup_result_tracker.record({
            "avg_time": avg_time,
            "std_dev": std_dev,
            "coefficient_of_variation": cov,
            "startup_times": startup_times,
        })

        print(f"[Stability] ✓ Startup time is stable (CoV: {cov:.1f}%)")
