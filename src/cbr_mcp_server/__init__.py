"""
CBR MCP Server - Case-Based Reasoning Model Context Protocol Server.

This package provides a production-ready MCP server for AI agent integration
with intelligent case-based reasoning capabilities.
"""

__version__ = "1.0.0"

import logging

# Try to import FastMCP (may not always be available)
# Use a temporary variable to avoid type assignment conflict
from typing import Any

# Import the module itself for test patching
from . import server as server_module
from .server import (
    VALID_CATEGORIES,
    VALID_SUBCATEGORIES,
    CBRMCPServer,
    CBRServerConfig,
    HealthAPI,
    LogConfig,
    LoggerManager,
    MonitoringConfig,
    PerformanceTracker,
    ProductionCBRRetriever,
    RequestInterceptor,
    SentenceTransformer,
    SignalHandler,
    StructuredLogger,
    SystemMetrics,
    WebSocketManager,
    chromadb,
    main,
    startup_configuration_validator,
)

FastMCP: Any = None
try:
    from .server import FastMCP as _FastMCP_temp

    FastMCP = _FastMCP_temp

except (ImportError, AttributeError):
    pass

# Re-export for public API
__all__ = [
    # Core server classes
    "CBRMCPServer",
    "ProductionCBRRetriever",
    "CBRServerConfig",
    # External dependencies
    "chromadb",
    "SentenceTransformer",
    "logging",
    # Logging infrastructure
    "StructuredLogger",
    "LogConfig",
    "LoggerManager",
    # Monitoring and performance
    "PerformanceTracker",
    "RequestInterceptor",
    "SystemMetrics",
    "MonitoringConfig",
    # Production infrastructure
    "HealthAPI",
    "WebSocketManager",
    "SignalHandler",
    # Validation constants
    "VALID_CATEGORIES",
    "VALID_SUBCATEGORIES",
    # Validation functions
    "startup_configuration_validator",
    # Main entry point
    "main",
    # Optional imports
    "FastMCP",
    # Version
    "__version__",
]
