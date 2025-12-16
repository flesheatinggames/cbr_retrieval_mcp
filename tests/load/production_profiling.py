"""
Production-Like Workload Profiling Script.

This script runs a comprehensive production-like workload simulation and collects
detailed performance data using cProfile and memory_profiler. It validates that
the system meets all performance targets under realistic usage conditions.

Performance Targets:
- Query latency: p95 < 200ms, p50 < 100ms
- Memory usage: Peak < 1500MB (accounts for real nomic-ai embedding model ~1135MB + query overhead)
- Cache hit rate: > 70% after warmup
- Throughput: > 10 queries/second with 10+ concurrent clients

Usage:
    python tests/load/production_profiling.py [--duration SECONDS] [--output-dir DIR]
"""

import argparse
import asyncio
import cProfile
import gc
import json
import pstats
import sys
import time
import tracemalloc
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import numpy as np
import psutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import CBR components
try:
    from cbr_mcp_server.performance.production_cbr_retriever import (
        ProductionCBRRetriever,
        LazyEmbeddingModel,
    )
    HAS_CBR = True
except ImportError:
    HAS_CBR = False
    ProductionCBRRetriever = None
    LazyEmbeddingModel = None

# Import workload generators
from tests.benchmarks.fixtures.workload_generators import (
    generate_mixed_workload,
    generate_hierarchical_searches,
)

# Import load test infrastructure
from tests.load.test_performance_load import (
    LoadTestRunner,
    LoadTestMetrics,
    generate_query_workload,
)


class ProductionProfiler:
    """Comprehensive production profiling with CPU and memory analysis."""

    def __init__(self, output_dir: Path, duration_seconds: int = 300):
        """
        Initialize production profiler.

        Args:
            output_dir: Directory to save profiling results
            duration_seconds: How long to run the profiling workload
        """
        self.output_dir = output_dir
        self.duration_seconds = duration_seconds
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize retriever
        if not HAS_CBR:
            raise ImportError("CBR components not available")

        print("Initializing CBR retriever...")
        self.embedding_model = LazyEmbeddingModel(
            model_name="nomic-ai/nomic-embed-text-v1.5",
            trust_remote_code=True
        )

        db_path = Path("./db")
        self.retriever = ProductionCBRRetriever(
            db_path=str(db_path),
            embedding_model=self.embedding_model
        )

        # Warm up with a test query
        print("Warming up retriever...")
        self.retriever.retrieve(query="test", max_results=1)
        print("Initialization complete.\n")

    def generate_production_workload(self) -> Dict[str, List[str]]:
        """
        Generate realistic production workload.

        Returns:
            Dictionary with different query types
        """
        print("Generating production workload...")

        workload = {
            # Mixed queries (50 unique, 70% repeat ratio for realistic caching)
            "retrieve_queries": generate_query_workload(
                num_unique_queries=50,
                repeated_query_ratio=0.7
            ),

            # Category searches
            "category_searches": [
                "orchestration",
                "web-development",
                "firebase",
                "security",
            ] * 25,  # Repeat for sustained load

            # Similar case lookups (simulate find_similar operations)
            "similar_lookups": ["case_0001", "case_0010", "case_0020"] * 30,
        }

        print(f"  - Generated {len(workload['retrieve_queries'])} retrieve queries")
        print(f"  - Generated {len(workload['category_searches'])} category searches")
        print(f"  - Generated {len(workload['similar_lookups'])} similar lookups")
        print()

        return workload

    async def run_profiled_workload(self) -> Dict[str, Any]:
        """
        Run production workload with CPU and memory profiling.

        Returns:
            Dictionary with profiling results and metrics
        """
        print(f"Starting profiled workload (duration: {self.duration_seconds}s)...")
        print("=" * 70)

        # Generate workload
        workload = self.generate_production_workload()

        # Start memory profiling
        tracemalloc.start()
        gc.collect()
        process = psutil.Process()
        baseline_mb = process.memory_info().rss / 1024 / 1024

        print(f"Baseline memory: {baseline_mb:.1f} MB\n")

        # Create cProfile profiler
        profiler = cProfile.Profile()

        # Start profiling
        print("Starting CPU profiling...")
        profiler.enable()
        start_time = time.perf_counter()

        # Run load test with mixed workload
        print(f"Running concurrent load test (10 clients, {self.duration_seconds}s)...\n")
        runner = LoadTestRunner(
            retriever=self.retriever,
            queries=workload["retrieve_queries"],
            duration_seconds=self.duration_seconds,
            concurrent_clients=10,  # 10+ concurrent as required
            collect_memory=True,
            memory_sample_interval=1.0,  # Sample every second
        )

        metrics = await runner.run_load_test()

        # Stop profiling
        profiler.disable()
        elapsed_time = time.perf_counter() - start_time

        print("\n" + "=" * 70)
        print(f"Workload completed in {elapsed_time:.1f}s\n")

        # Get memory snapshot
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics("lineno")

        # Get final memory
        gc.collect()
        final_mb = process.memory_info().rss / 1024 / 1024
        delta_mb = final_mb - baseline_mb

        # Stop memory profiling
        tracemalloc.stop()

        # Compile results
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": self.duration_seconds,
                "elapsed_seconds": elapsed_time,
                "baseline_memory_mb": round(baseline_mb, 2),
                "final_memory_mb": round(final_mb, 2),
                "delta_memory_mb": round(delta_mb, 2),
            },
            "load_metrics": {
                "total_queries": metrics.total_queries,
                "successful_queries": metrics.successful_queries,
                "failed_queries": metrics.failed_queries,
                "error_rate": round(metrics.error_rate, 4),
                "queries_per_second": round(metrics.queries_per_second, 2),
                "latency": {
                    "p50_ms": round(metrics.p50_latency * 1000, 2),
                    "p95_ms": round(metrics.p95_latency * 1000, 2),
                    "p99_ms": round(metrics.p99_latency * 1000, 2),
                    "mean_ms": round(metrics.mean_latency * 1000, 2),
                    "max_ms": round(metrics.max_latency * 1000, 2),
                },
                "memory": {
                    "peak_mb": round(metrics.peak_memory_mb, 2),
                    "mean_mb": round(metrics.mean_memory_mb, 2),
                    "final_mb": round(metrics.final_memory_mb, 2),
                    "samples_count": len(metrics.memory_samples),
                },
                "cache": {
                    "hit_rate": round(metrics.cache_hit_rate, 4),
                    "hits": metrics.cache_hits,
                    "misses": metrics.cache_misses,
                },
            },
            "memory_top_consumers": [
                {
                    "size_mb": round(stat.size / 1024 / 1024, 2),
                    "count": stat.count,
                    "location": f"{stat.traceback.format()[0] if stat.traceback else 'unknown'}"
                }
                for stat in top_stats[:10]
            ],
        }

        # Save cProfile data
        prof_file = self.output_dir / f"production_profile_{int(time.time())}.prof"
        profiler.dump_stats(str(prof_file))
        results["cprofile_file"] = str(prof_file)

        # Generate human-readable profile stats
        stats_io = pstats.Stats(profiler)
        stats_io.sort_stats("cumulative")

        # Get top functions by cumulative time
        stats_io.stream = None  # Disable immediate printing
        stats_dict = {}
        for func, (cc, nc, tt, ct, callers) in stats_io.stats.items():
            filename, line, func_name = func
            stats_dict[f"{filename}:{line}({func_name})"] = {
                "ncalls": nc,
                "tottime": round(tt, 3),
                "cumtime": round(ct, 3),
                "percall_tot": round(tt / nc if nc > 0 else 0, 6),
                "percall_cum": round(ct / nc if nc > 0 else 0, 6),
            }

        # Sort by cumulative time and take top 20
        sorted_funcs = sorted(
            stats_dict.items(),
            key=lambda x: x[1]["cumtime"],
            reverse=True
        )[:20]

        results["top_functions"] = [
            {"function": name, **data}
            for name, data in sorted_funcs
        ]

        return results

    def validate_performance_targets(self, results: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate that results meet performance targets.

        Args:
            results: Profiling results dictionary

        Returns:
            Dictionary of validation results
        """
        print("\nValidating Performance Targets:")
        print("=" * 70)

        metrics = results["load_metrics"]
        validations = {}

        # Latency targets
        p95_target = 200  # ms
        p50_target = 100  # ms
        p95_actual = metrics["latency"]["p95_ms"]
        p50_actual = metrics["latency"]["p50_ms"]

        validations["p95_latency"] = p95_actual < p95_target
        validations["p50_latency"] = p50_actual < p50_target

        status = "✓ PASS" if validations["p95_latency"] else "✗ FAIL"
        print(f"  p95 Latency: {p95_actual:.2f}ms < {p95_target}ms ... {status}")

        status = "✓ PASS" if validations["p50_latency"] else "✗ FAIL"
        print(f"  p50 Latency: {p50_actual:.2f}ms < {p50_target}ms ... {status}")

        # Memory target (updated to account for real nomic-ai/nomic-embed-text-v1.5 model)
        # The embedding model requires ~1135MB, plus query overhead and cache usage
        # This aligns with MAX_PEAK_MEMORY_MB thresholds set in memory benchmarks
        memory_target = 1500  # MB
        memory_actual = metrics["memory"]["peak_mb"]
        validations["peak_memory"] = memory_actual < memory_target

        status = "✓ PASS" if validations["peak_memory"] else "✗ FAIL"
        print(f"  Peak Memory: {memory_actual:.1f}MB < {memory_target}MB ... {status}")

        # Cache hit rate target
        cache_target = 0.70
        cache_actual = metrics["cache"]["hit_rate"]
        validations["cache_hit_rate"] = cache_actual > cache_target

        status = "✓ PASS" if validations["cache_hit_rate"] else "✗ FAIL"
        print(f"  Cache Hit Rate: {cache_actual:.1%} > {cache_target:.0%} ... {status}")

        # Throughput target
        throughput_target = 10  # queries/second with 10+ clients
        throughput_actual = metrics["queries_per_second"]
        validations["throughput"] = throughput_actual > throughput_target

        status = "✓ PASS" if validations["throughput"] else "✗ FAIL"
        print(f"  Throughput: {throughput_actual:.1f} QPS > {throughput_target} QPS ... {status}")

        # Error rate
        error_target = 0.01  # 1%
        error_actual = metrics["error_rate"]
        validations["error_rate"] = error_actual < error_target

        status = "✓ PASS" if validations["error_rate"] else "✗ FAIL"
        print(f"  Error Rate: {error_actual:.1%} < {error_target:.0%} ... {status}")

        print("=" * 70)

        # Overall pass/fail
        all_passed = all(validations.values())
        validations["overall"] = all_passed

        if all_passed:
            print("✓ ALL PERFORMANCE TARGETS MET")
        else:
            print("✗ SOME PERFORMANCE TARGETS NOT MET")
            failed = [k for k, v in validations.items() if not v and k != "overall"]
            print(f"  Failed checks: {', '.join(failed)}")

        print()
        return validations

    def save_results(self, results: Dict[str, Any], validations: Dict[str, bool]):
        """
        Save profiling results to JSON file.

        Args:
            results: Profiling results dictionary
            validations: Validation results dictionary
        """
        results["validation"] = validations

        output_file = self.output_dir / f"profiling_results_{int(time.time())}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"Results saved to: {output_file}")
        print(f"CPU profile saved to: {results['cprofile_file']}")
        print()

    def print_summary(self, results: Dict[str, Any]):
        """
        Print summary of profiling results.

        Args:
            results: Profiling results dictionary
        """
        print("\nProfiling Summary:")
        print("=" * 70)

        metadata = results["metadata"]
        metrics = results["load_metrics"]

        print(f"Duration: {metadata['elapsed_seconds']:.1f}s")
        print(f"Total Queries: {metrics['total_queries']}")
        print(f"Successful: {metrics['successful_queries']}")
        print(f"Failed: {metrics['failed_queries']}")
        print(f"Throughput: {metrics['queries_per_second']:.1f} QPS")
        print()

        print("Latency Distribution:")
        print(f"  p50: {metrics['latency']['p50_ms']:.2f}ms")
        print(f"  p95: {metrics['latency']['p95_ms']:.2f}ms")
        print(f"  p99: {metrics['latency']['p99_ms']:.2f}ms")
        print(f"  max: {metrics['latency']['max_ms']:.2f}ms")
        print()

        print("Memory Usage:")
        print(f"  Peak: {metrics['memory']['peak_mb']:.1f}MB")
        print(f"  Mean: {metrics['memory']['mean_mb']:.1f}MB")
        print(f"  Delta: {metadata['delta_memory_mb']:.1f}MB")
        print()

        print("Cache Performance:")
        print(f"  Hit Rate: {metrics['cache']['hit_rate']:.1%}")
        print(f"  Hits: {metrics['cache']['hits']}")
        print(f"  Misses: {metrics['cache']['misses']}")
        print()

        print("Top 5 Functions by Cumulative Time:")
        for i, func_data in enumerate(results["top_functions"][:5], 1):
            print(f"  {i}. {func_data['function']}")
            print(f"     cumtime: {func_data['cumtime']:.3f}s, "
                  f"calls: {func_data['ncalls']}, "
                  f"percall: {func_data['percall_cum']:.6f}s")
        print()

        print("Top 5 Memory Consumers:")
        for i, consumer in enumerate(results["memory_top_consumers"][:5], 1):
            print(f"  {i}. {consumer['size_mb']:.2f}MB - {consumer['location'][:60]}")
        print()


async def main():
    """Main entry point for production profiling."""
    parser = argparse.ArgumentParser(
        description="Profile CBR MCP Server with production-like workload"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Duration of profiling workload in seconds (default: 300)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./profiling_results",
        help="Directory to save profiling results (default: ./profiling_results)"
    )

    args = parser.parse_args()

    if not HAS_CBR:
        print("ERROR: CBR components not available")
        sys.exit(1)

    output_dir = Path(args.output_dir)

    print("=" * 70)
    print("CBR MCP Server - Production Profiling")
    print("=" * 70)
    print()

    # Initialize profiler
    profiler = ProductionProfiler(
        output_dir=output_dir,
        duration_seconds=args.duration
    )

    # Run profiled workload
    results = await profiler.run_profiled_workload()

    # Validate performance targets
    validations = profiler.validate_performance_targets(results)

    # Save results
    profiler.save_results(results, validations)

    # Print summary
    profiler.print_summary(results)

    # Exit with appropriate code
    if validations["overall"]:
        print("✓ SUCCESS: All performance targets met")
        sys.exit(0)
    else:
        print("✗ FAILURE: Some performance targets not met")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
