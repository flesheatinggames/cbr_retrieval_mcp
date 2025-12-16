"""Memory profiling test to identify what's using memory in load tests."""
import gc
import psutil
import pytest


@pytest.mark.asyncio
async def test_minimal_load_test_memory(shared_cbr_retriever):
    """Minimal load test to profile memory usage."""
    import tracemalloc

    # Start tracing
    tracemalloc.start()
    gc.collect()

    # Get baseline
    process = psutil.Process()
    baseline_mb = process.memory_info().rss / 1024 / 1024

    # Run a simple load pattern
    for i in range(50):
        results = shared_cbr_retriever.retrieve(f"query {i % 10}", max_results=5)
        assert len(results) == 5

    # Get memory snapshot
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")

    # Print top memory consumers
    print("\n=== Top 10 Memory Consumers ===")
    for stat in top_stats[:10]:
        print(f"{stat.size / 1024 / 1024:.1f} MB - {stat}")

    # Get final memory
    gc.collect()
    final_mb = process.memory_info().rss / 1024 / 1024
    delta_mb = final_mb - baseline_mb

    print(f"\n=== Memory Summary ===")
    print(f"Baseline: {baseline_mb:.1f}MB")
    print(f"Final: {final_mb:.1f}MB")
    print(f"Delta: {delta_mb:.1f}MB")

    tracemalloc.stop()

    # This should be very low with mocks
    assert delta_mb < 100, f"Memory delta {delta_mb:.1f}MB too high"
