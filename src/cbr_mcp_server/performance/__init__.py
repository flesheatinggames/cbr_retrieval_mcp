"""
Performance optimization module for CBR MCP Server.

This module contains components for performance optimization including:
- Memory management
- Caching mechanisms
- Query optimization
- Resource monitoring
- Lazy loading
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
from cbr_mcp_server.performance.production_cbr_retriever import (
    LazyEmbeddingModel,
    ProductionCBRRetriever,
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
    # Lazy loading components
    "LazyEmbeddingModel",
    "ProductionCBRRetriever",
]
