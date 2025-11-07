"""
Performance optimization module for CBR MCP Server.

This module contains components for performance optimization including:
- Memory management
- Caching mechanisms
- Query optimization
- Resource monitoring
"""

from cbr_mcp_server.performance.data_models import (
    CachePolicy,
    MemoryAllocation,
    MemoryConfig,
    MemoryMetrics,
    QueryOptimizationConfig,
)
from cbr_mcp_server.performance.memory_manager import (
    EmbeddingCacheManager,
    MemoryManager,
    MemoryPressureDetector,
)

__all__ = [
    # Data models
    "CachePolicy",
    "MemoryAllocation",
    "MemoryConfig",
    "MemoryMetrics",
    "QueryOptimizationConfig",
    # Memory management components
    "EmbeddingCacheManager",
    "MemoryManager",
    "MemoryPressureDetector",
]
