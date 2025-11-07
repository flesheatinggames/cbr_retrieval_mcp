"""
CBR MCP Server - Case-Based Reasoning Model Context Protocol Server.

This package provides a production-ready MCP server for AI agent integration
with intelligent case-based reasoning capabilities.
"""

__version__ = "1.0.0"

import logging

# Import the module itself for test patching
from . import server as server_module

# Validation functions
# Validation constants
# Production infrastructure
# Monitoring and performance
# Logging infrastructure
# External dependencies
# Core server classes
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
    startup_configuration_validator,
)

# Try to import FastMCP (may not always be available)
try:
    from .server import FastMCP
except (ImportError, AttributeError):
    FastMCP = None

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
    # Optional imports
    "FastMCP",
    # Version
    "__version__",
]
