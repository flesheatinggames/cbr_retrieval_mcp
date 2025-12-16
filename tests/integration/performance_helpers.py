"""
Shared helper functions and fixtures for MCP tool performance testing.

This module provides:
- Latency measurement helpers for async MCP tool calls
- Memory usage tracking during MCP operations
- Sample workload fixtures (small, medium, large)
- ChromaDB mock fixtures for isolated testing
- Concurrent MCP tool call performance testing helpers

These helpers support the performance testing infrastructure across all
MCP tool performance integration tests.
"""

import asyncio
import gc
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Try to import psutil for memory tracking
try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None

# Try to import CBR server components
try:
    from cbr_mcp_server import CBRMCPServer
    from cbr_mcp_server.performance.production_cbr_retriever import (
        ProductionCBRRetriever,
    )

    HAS_CBR = True
except ImportError:
    HAS_CBR = False
    CBRMCPServer = None
    ProductionCBRRetriever = None


# ============================================================================
# Helper Functions for MCP Tool Performance Measurement
# ============================================================================


async def measure_mcp_tool_latency(
    tool_func: callable,
    *args,
    warmup_calls: int = 0,
    **kwargs,
) -> Dict[str, float]:
    """
    Measure latency of an MCP tool call.

    This helper provides accurate timing for async MCP tool functions,
    supporting warmup calls for cache scenarios and statistical measurements.

    Args:
        tool_func: Async MCP tool function to measure
        *args: Positional arguments to pass to tool_func
        warmup_calls: Number of warmup calls before measurement
        **kwargs: Keyword arguments to pass to tool_func

    Returns:
        Dict containing:
            - latency_ms: Measured latency in milliseconds
            - result: The tool's return value

    Raises:
        ValueError: If tool_func is not callable
        RuntimeError: If tool call fails
    """
    if not callable(tool_func):
        raise ValueError("tool_func must be callable")

    # Warmup calls if requested
    for _ in range(warmup_calls):
        await tool_func(*args, **kwargs)

    # Measure actual call
    start_time = time.perf_counter()
    result = await tool_func(*args, **kwargs)
    end_time = time.perf_counter()

    latency_ms = (end_time - start_time) * 1000.0

    return {
        "latency_ms": latency_ms,
        "result": result,
    }


async def measure_mcp_tool_memory(
    tool_func: callable,
    *args,
    **kwargs,
) -> Dict[str, float]:
    """
    Measure memory usage during MCP tool execution.

    This helper tracks memory delta before, during, and after MCP tool
    execution to identify memory allocation patterns and potential leaks.

    Args:
        tool_func: Async MCP tool function to measure
        *args: Positional arguments to pass to tool_func
        **kwargs: Keyword arguments to pass to tool_func

    Returns:
        Dict containing:
            - baseline_mb: Memory usage before call (MB)
            - peak_mb: Peak memory during call (MB)
            - final_mb: Memory usage after call (MB)
            - delta_mb: Memory increase (final - baseline, MB)
            - result: The tool's return value

    Raises:
        RuntimeError: If psutil not available
        ValueError: If tool_func is not callable
    """
    if not HAS_PSUTIL:
        raise RuntimeError("psutil required for memory measurement")

    if not callable(tool_func):
        raise ValueError("tool_func must be callable")

    # Force garbage collection before measurement
    gc.collect()

    # Get baseline memory
    process = psutil.Process()
    baseline_mb = process.memory_info().rss / 1024 / 1024

    # Execute tool and track memory
    result = await tool_func(*args, **kwargs)

    # Get final memory
    gc.collect()
    final_mb = process.memory_info().rss / 1024 / 1024

    # Calculate delta
    delta_mb = final_mb - baseline_mb

    # Note: Peak tracking would require continuous sampling during execution
    # For this implementation, we use final as approximate peak
    peak_mb = final_mb

    return {
        "baseline_mb": baseline_mb,
        "peak_mb": peak_mb,
        "final_mb": final_mb,
        "delta_mb": delta_mb,
        "result": result,
    }


async def measure_concurrent_mcp_tools(
    tool_calls: List[tuple],
    max_concurrent: int = 10,
) -> Dict[str, Any]:
    """
    Measure performance of concurrent MCP tool calls.

    This helper executes multiple MCP tool calls concurrently and measures
    overall throughput and per-call latency to verify performance under load.

    Args:
        tool_calls: List of (tool_func, args, kwargs) tuples
        max_concurrent: Maximum number of concurrent calls

    Returns:
        Dict containing:
            - total_calls: Number of calls executed
            - total_duration_sec: Total time for all calls
            - throughput_ops_per_sec: Calls per second
            - latencies_ms: List of individual call latencies
            - p50_latency_ms: Median latency
            - p95_latency_ms: 95th percentile latency
            - p99_latency_ms: 99th percentile latency

    Raises:
        ValueError: If tool_calls is empty or invalid
    """
    if not tool_calls:
        raise ValueError("tool_calls must not be empty")

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)
    latencies = []
    results = []

    async def execute_with_semaphore(tool_func, args, kwargs):
        async with semaphore:
            start = time.perf_counter()
            result = await tool_func(*args, **kwargs)
            latency = (time.perf_counter() - start) * 1000.0
            return latency, result

    # Execute all calls concurrently
    start_time = time.perf_counter()
    tasks = [
        execute_with_semaphore(tool_func, args, kwargs)
        for tool_func, args, kwargs in tool_calls
    ]
    completed = await asyncio.gather(*tasks)
    end_time = time.perf_counter()

    # Extract latencies and results
    latencies = [lat for lat, _ in completed]
    results = [res for _, res in completed]

    # Calculate statistics
    latencies_sorted = sorted(latencies)
    total_duration = end_time - start_time
    throughput = len(tool_calls) / total_duration if total_duration > 0 else 0

    def percentile(data, pct):
        idx = int(len(data) * pct / 100.0)
        return data[min(idx, len(data) - 1)]

    return {
        "total_calls": len(tool_calls),
        "total_duration_sec": total_duration,
        "throughput_ops_per_sec": throughput,
        "latencies_ms": latencies,
        "p50_latency_ms": percentile(latencies_sorted, 50),
        "p95_latency_ms": percentile(latencies_sorted, 95),
        "p99_latency_ms": percentile(latencies_sorted, 99),
        "results": results,
    }


# ============================================================================
# Fixtures for MCP Performance Testing
# ============================================================================


@pytest.fixture
def sample_workload_small():
    """
    Small workload fixture with 5 representative queries.

    This fixture provides a small set of diverse queries for quick
    performance smoke tests and development iteration.

    Returns:
        List of 5 query dicts with:
            - query: Query string
            - category: Expected category (optional)
            - max_results: Number of results to request
    """
    return [
        {
            "query": "How to implement user authentication?",
            "category": "code",
            "max_results": 5,
        },
        {
            "query": "Best practices for error handling",
            "category": "best-practice",
            "max_results": 3,
        },
        {
            "query": "How to orchestrate multiple agents?",
            "category": "orchestration",
            "max_results": 5,
        },
        {
            "query": "React component lifecycle methods",
            "category": "code",
            "max_results": 5,
        },
        {
            "query": "Common async/await pitfalls",
            "category": "anti-pattern",
            "max_results": 3,
        },
    ]


@pytest.fixture
def sample_workload_medium():
    """
    Medium workload fixture with 20 realistic queries.

    This fixture provides a comprehensive set of queries covering all major
    categories with realistic patterns for thorough performance testing.

    Returns:
        List of 20 query dicts covering diverse categories and query types
    """
    return [
        # Code queries (5)
        {
            "query": "How to implement user authentication?",
            "category": "code",
            "max_results": 5,
        },
        {
            "query": "React component lifecycle methods",
            "category": "code",
            "max_results": 5,
        },
        {
            "query": "Firebase security rules examples",
            "category": "code",
            "max_results": 3,
        },
        {
            "query": "API rate limiting implementation",
            "category": "code",
            "max_results": 5,
        },
        {
            "query": "Database transaction patterns",
            "category": "code",
            "max_results": 5,
        },
        # Orchestration queries (5)
        {
            "query": "How to orchestrate multiple agents?",
            "category": "orchestration",
            "max_results": 5,
        },
        {
            "query": "Agent delegation patterns",
            "category": "orchestration",
            "max_results": 3,
        },
        {
            "query": "Planning phase best practices",
            "category": "orchestration",
            "max_results": 5,
        },
        {
            "query": "Remediation workflow patterns",
            "category": "orchestration",
            "max_results": 5,
        },
        {
            "query": "Verification protocol examples",
            "category": "orchestration",
            "max_results": 5,
        },
        # Best practice queries (5)
        {
            "query": "Best practices for error handling",
            "category": "best-practice",
            "max_results": 3,
        },
        {
            "query": "Code review checklist",
            "category": "best-practice",
            "max_results": 5,
        },
        {
            "query": "Testing strategy patterns",
            "category": "best-practice",
            "max_results": 5,
        },
        {
            "query": "Security audit guidelines",
            "category": "best-practice",
            "max_results": 3,
        },
        {
            "query": "Performance optimization tips",
            "category": "best-practice",
            "max_results": 5,
        },
        # Anti-pattern queries (5)
        {
            "query": "Common async/await pitfalls",
            "category": "anti-pattern",
            "max_results": 3,
        },
        {
            "query": "Completion bias examples",
            "category": "anti-pattern",
            "max_results": 3,
        },
        {
            "query": "Verification skip mistakes",
            "category": "anti-pattern",
            "max_results": 3,
        },
        {
            "query": "Protocol violation patterns",
            "category": "anti-pattern",
            "max_results": 3,
        },
        {
            "query": "Common testing mistakes",
            "category": "anti-pattern",
            "max_results": 5,
        },
    ]


@pytest.fixture
def sample_workload_large():
    """
    Large workload fixture with 50 diverse queries.

    This fixture provides an extensive set of queries for stress testing
    and comprehensive performance validation under load.

    Returns:
        List of 50 query dicts covering all categories with high diversity
    """
    # Start with medium workload as base
    workload = sample_workload_medium.__wrapped__()

    # Add 30 more queries to reach 50
    additional_queries = [
        # Additional code queries (10)
        {"query": "GraphQL schema design", "category": "code", "max_results": 5},
        {"query": "WebSocket implementation", "category": "code", "max_results": 5},
        {"query": "OAuth2 flow implementation", "category": "code", "max_results": 5},
        {"query": "Caching strategies", "category": "code", "max_results": 5},
        {"query": "Message queue patterns", "category": "code", "max_results": 5},
        {"query": "Microservices communication", "category": "code", "max_results": 5},
        {"query": "State management patterns", "category": "code", "max_results": 5},
        {"query": "File upload handling", "category": "code", "max_results": 5},
        {"query": "Search implementation", "category": "code", "max_results": 5},
        {"query": "Pagination strategies", "category": "code", "max_results": 5},
        # Additional orchestration queries (8)
        {
            "query": "Multi-agent coordination",
            "category": "orchestration",
            "max_results": 5,
        },
        {
            "query": "Task delegation strategies",
            "category": "orchestration",
            "max_results": 5,
        },
        {
            "query": "Workflow state management",
            "category": "orchestration",
            "max_results": 5,
        },
        {
            "query": "Agent communication patterns",
            "category": "orchestration",
            "max_results": 5,
        },
        {
            "query": "Completion detection patterns",
            "category": "orchestration",
            "max_results": 5,
        },
        {
            "query": "Error recovery workflows",
            "category": "orchestration",
            "max_results": 5,
        },
        {
            "query": "Parallel task execution",
            "category": "orchestration",
            "max_results": 5,
        },
        {
            "query": "Sequential task patterns",
            "category": "orchestration",
            "max_results": 5,
        },
        # Additional best practice queries (7)
        {
            "query": "API design principles",
            "category": "best-practice",
            "max_results": 5,
        },
        {
            "query": "Database schema design",
            "category": "best-practice",
            "max_results": 5,
        },
        {
            "query": "Documentation standards",
            "category": "best-practice",
            "max_results": 5,
        },
        {
            "query": "Code organization patterns",
            "category": "best-practice",
            "max_results": 5,
        },
        {
            "query": "Git workflow best practices",
            "category": "best-practice",
            "max_results": 5,
        },
        {
            "query": "Dependency management",
            "category": "best-practice",
            "max_results": 5,
        },
        {
            "query": "Configuration management",
            "category": "best-practice",
            "max_results": 5,
        },
        # Additional anti-pattern queries (5)
        {
            "query": "Common database mistakes",
            "category": "anti-pattern",
            "max_results": 3,
        },
        {"query": "API design pitfalls", "category": "anti-pattern", "max_results": 3},
        {
            "query": "Security vulnerabilities",
            "category": "anti-pattern",
            "max_results": 3,
        },
        {
            "query": "Performance bottlenecks",
            "category": "anti-pattern",
            "max_results": 3,
        },
        {"query": "Scalability mistakes", "category": "anti-pattern", "max_results": 3},
    ]

    return workload + additional_queries


@pytest.fixture
def mock_chromadb_client():
    """
    Mock ChromaDB client for isolated performance testing.

    This fixture provides a mocked ChromaDB client that simulates database
    operations without requiring an actual database connection, enabling
    fast and isolated performance tests.

    Returns:
        MagicMock configured with typical ChromaDB collection interface
    """
    mock_client = MagicMock()
    mock_collection = MagicMock()

    # Configure mock collection with typical responses
    mock_collection.query.return_value = {
        "ids": [["case-1", "case-2", "case-3"]],
        "distances": [[0.1, 0.2, 0.3]],
        "metadatas": [
            [
                {"category": "code", "tags": ["python", "auth"]},
                {"category": "code", "tags": ["react", "hooks"]},
                {"category": "orchestration", "tags": ["planning"]},
            ]
        ],
        "documents": [["Example 1", "Example 2", "Example 3"]],
    }

    mock_collection.get.return_value = {
        "ids": ["case-1"],
        "metadatas": [{"category": "code", "tags": ["python"]}],
        "documents": ["Example case"],
    }

    mock_client.get_or_create_collection.return_value = mock_collection
    mock_client.get_collection.return_value = mock_collection

    return mock_client


@pytest.fixture
def mock_mcp_server():
    """
    Mock MCP server for performance testing.

    This fixture provides a mocked MCP server with realistic tool behavior
    for performance testing without requiring actual server initialization.

    Returns:
        Mock server with cbr_retrieve, cbr_search_category, and
        cbr_find_similar tools configured
    """
    mock_server = MagicMock()

    # Mock cbr_retrieve tool
    async def mock_retrieve(
        query: str, max_results: int = 5, similarity_threshold: float = 0.8
    ):
        await asyncio.sleep(0.01)  # Simulate processing time
        return [
            {"id": f"case-{i}", "score": 0.9 - i * 0.1, "content": f"Result {i}"}
            for i in range(1, min(max_results + 1, 6))
        ]

    mock_server.cbr_retrieve = AsyncMock(side_effect=mock_retrieve)

    # Mock cbr_search_category tool
    async def mock_search_category(
        category: str,
        subcategory: Optional[str] = None,
        query: str = "",
        limit: int = 10,
    ):
        await asyncio.sleep(0.01)  # Simulate processing time
        return {
            "category": category,
            "results": [
                {"id": f"case-{i}", "content": f"Category result {i}"}
                for i in range(1, min(limit + 1, 6))
            ],
        }

    mock_server.cbr_search_category = AsyncMock(side_effect=mock_search_category)

    # Mock cbr_find_similar tool
    async def mock_find_similar(
        example_id: str,
        similarity_threshold: float = 0.85,
        max_results: int = 8,
    ):
        await asyncio.sleep(0.01)  # Simulate processing time
        return [
            {"id": f"case-{i}", "score": 0.95 - i * 0.05, "content": f"Similar {i}"}
            for i in range(1, min(max_results + 1, 6))
        ]

    mock_server.cbr_find_similar = AsyncMock(side_effect=mock_find_similar)

    return mock_server
