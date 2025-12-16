"""
Memory profiling script to identify the 717MB discrepancy between benchmarks and load tests.

This script uses memory_profiler and tracemalloc to identify where the extra memory
is being consumed during load tests vs benchmarks.
"""

import gc
import sys
import tracemalloc
from pathlib import Path

import psutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def get_memory_mb():
    """Get current process memory in MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def profile_benchmark_fixture():
    """Profile memory usage of benchmark fixture setup."""
    print("\n" + "=" * 80)
    print("PROFILING BENCHMARK FIXTURE (Expected: <505MB)")
    print("=" * 80)

    tracemalloc.start()
    gc.collect()
    baseline_memory = get_memory_mb()
    print(f"Baseline memory: {baseline_memory:.1f} MB")

    # Import and setup benchmark fixture
    from cbr_mcp_server.performance.production_cbr_retriever import (
        LazyEmbeddingModel,
        ProductionCBRRetriever,
    )

    # Create embedding model (session-scoped)
    print("\nCreating embedding model...")
    embedding_model = LazyEmbeddingModel(
        model_name="nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True
    )
    after_embedding_memory = get_memory_mb()
    print(
        f"After embedding model creation: {after_embedding_memory:.1f} MB "
        f"(+{after_embedding_memory - baseline_memory:.1f} MB)"
    )

    # Create retriever (session-scoped) with isolated test DB
    print("\nCreating retriever...")
    import tempfile
    test_db_path = Path(tempfile.mkdtemp(prefix="profile_test_db_"))
    retriever = ProductionCBRRetriever(
        db_path=str(test_db_path), embedding_model=embedding_model
    )
    after_retriever_memory = get_memory_mb()
    print(
        f"After retriever creation: {after_retriever_memory:.1f} MB "
        f"(+{after_retriever_memory - after_embedding_memory:.1f} MB)"
    )

    # Initialize with test query
    print("\nInitializing with test query...")
    retriever.retrieve(query="test", max_results=1)
    after_init_memory = get_memory_mb()
    print(
        f"After initialization: {after_init_memory:.1f} MB "
        f"(+{after_init_memory - after_retriever_memory:.1f} MB)"
    )

    # Get snapshot
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")

    print("\nTop 10 memory allocations (benchmark setup):")
    for stat in top_stats[:10]:
        print(f"{stat}")

    peak_memory = get_memory_mb()
    print(f"\n{'=' * 80}")
    print(f"BENCHMARK PEAK MEMORY: {peak_memory:.1f} MB")
    print(f"{'=' * 80}\n")

    tracemalloc.stop()

    return embedding_model, retriever, peak_memory, test_db_path


def profile_load_test_fixture():
    """Profile memory usage of load test fixture setup."""
    print("\n" + "=" * 80)
    print("PROFILING LOAD TEST FIXTURE (Current: 1222MB, Target: <505MB)")
    print("=" * 80)

    tracemalloc.start()
    gc.collect()
    baseline_memory = get_memory_mb()
    print(f"Baseline memory: {baseline_memory:.1f} MB")

    # Import load test conftest fixture
    sys.path.insert(0, str(Path(__file__).parent))
    from conftest import shared_cbr_retriever, shared_embedding_model

    # Create a mock request object
    class MockRequest:
        pass

    request = MockRequest()

    # Create embedding model using load test fixture
    print("\nCreating embedding model (load test fixture)...")
    embedding_model_gen = shared_embedding_model(request)
    embedding_model = next(embedding_model_gen)
    after_embedding_memory = get_memory_mb()
    print(
        f"After embedding model creation: {after_embedding_memory:.1f} MB "
        f"(+{after_embedding_memory - baseline_memory:.1f} MB)"
    )

    # Create retriever using load test fixture
    print("\nCreating retriever (load test fixture)...")
    retriever_gen = shared_cbr_retriever(request, embedding_model)
    retriever = next(retriever_gen)
    after_retriever_memory = get_memory_mb()
    print(
        f"After retriever creation: {after_retriever_memory:.1f} MB "
        f"(+{after_retriever_memory - after_embedding_memory:.1f} MB)"
    )

    # Get snapshot
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")

    print("\nTop 10 memory allocations (load test setup):")
    for stat in top_stats[:10]:
        print(f"{stat}")

    peak_memory = get_memory_mb()
    print(f"\n{'=' * 80}")
    print(f"LOAD TEST PEAK MEMORY: {peak_memory:.1f} MB")
    print(f"{'=' * 80}\n")

    tracemalloc.stop()

    return embedding_model, retriever, peak_memory


def compare_fixture_objects():
    """Compare object creation between benchmark and load test fixtures."""
    print("\n" + "=" * 80)
    print("COMPARING FIXTURE OBJECT CREATION")
    print("=" * 80)

    # Profile benchmark fixture
    bench_model, bench_retriever, bench_peak, bench_db_path = profile_benchmark_fixture()

    # Profile load test fixture
    load_model, load_retriever, load_peak = profile_load_test_fixture()

    # Compare
    print("\n" + "=" * 80)
    print("MEMORY DISCREPANCY ANALYSIS")
    print("=" * 80)
    discrepancy = load_peak - bench_peak
    print(f"Benchmark peak memory: {bench_peak:.1f} MB")
    print(f"Load test peak memory: {load_peak:.1f} MB")
    print(f"DISCREPANCY: {discrepancy:.1f} MB ({discrepancy / bench_peak * 100:.1f}% increase)")

    if discrepancy > 50:
        print("\n⚠️  CRITICAL: Load test fixture consumes significantly more memory!")
        print("This explains why load tests fail the 500MB target.")
    else:
        print("\n✓ Fixtures have similar memory footprint.")
        print("The issue may be in the test execution itself.")

    # Cleanup with proper resource management
    try:
        bench_retriever.close()
    except Exception:
        pass
    try:
        load_retriever.close()
    except Exception:
        pass

    del bench_model, bench_retriever, load_model, load_retriever
    gc.collect()

    # Clean up temp database
    import shutil
    try:
        shutil.rmtree(str(bench_db_path))
    except Exception:
        pass


def profile_test_runner():
    """Profile memory usage of LoadTestRunner during execution."""
    print("\n" + "=" * 80)
    print("PROFILING LOADTESTRUNNER EXECUTION")
    print("=" * 80)

    import asyncio

    from test_performance_load import LoadTestRunner, generate_query_workload

    # Create retriever
    from cbr_mcp_server.performance.production_cbr_retriever import (
        LazyEmbeddingModel,
        ProductionCBRRetriever,
    )

    embedding_model = LazyEmbeddingModel(
        model_name="nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True
    )
    import tempfile
    test_db_path = Path(tempfile.mkdtemp(prefix="profile_runner_test_db_"))
    retriever = ProductionCBRRetriever(
        db_path=str(test_db_path), embedding_model=embedding_model
    )
    retriever.retrieve(query="test", max_results=1)

    baseline_memory = get_memory_mb()
    print(f"Baseline memory (before test runner): {baseline_memory:.1f} MB")

    # Create test runner
    print("\nCreating LoadTestRunner...")
    queries = generate_query_workload(num_unique_queries=10, repeated_query_ratio=0.7)
    runner = LoadTestRunner(
        retriever=retriever,
        queries=queries,
        duration_seconds=5,  # Short test
        concurrent_clients=1,
        collect_memory=True,
        memory_sample_interval=0.5,
    )

    after_runner_memory = get_memory_mb()
    print(
        f"After LoadTestRunner creation: {after_runner_memory:.1f} MB "
        f"(+{after_runner_memory - baseline_memory:.1f} MB)"
    )

    # Run test
    print("\nRunning load test (5 seconds)...")
    tracemalloc.start()

    async def run_test():
        metrics = await runner.run_load_test()
        return metrics

    metrics = asyncio.run(run_test())

    after_test_memory = get_memory_mb()
    print(
        f"After load test execution: {after_test_memory:.1f} MB "
        f"(+{after_test_memory - after_runner_memory:.1f} MB)"
    )

    # Get snapshot
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")

    print("\nTop 10 memory allocations (during load test):")
    for stat in top_stats[:10]:
        print(f"{stat}")

    peak_memory = get_memory_mb()
    print(f"\n{'=' * 80}")
    print(f"LOAD TEST RUNNER PEAK MEMORY: {peak_memory:.1f} MB")
    print(f"Memory samples from test: {[round(m, 1) for m in metrics.memory_samples[:5]]}")
    print(f"Reported peak from test: {metrics.peak_memory_mb:.1f} MB")
    print(f"{'=' * 80}\n")

    tracemalloc.stop()

    # Cleanup
    try:
        retriever.close()
    except Exception:
        pass

    del retriever, embedding_model
    gc.collect()

    # Clean up temp database
    import shutil
    try:
        shutil.rmtree(str(test_db_path))
    except Exception:
        pass


if __name__ == "__main__":
    print("\nMemory Profiling: Load Test vs Benchmark Discrepancy")
    print("=" * 80)

    # Step 1: Compare fixture object creation
    compare_fixture_objects()

    # Step 2: Profile test runner execution
    print("\n")
    profile_test_runner()

    print("\n" + "=" * 80)
    print("PROFILING COMPLETE")
    print("=" * 80)
