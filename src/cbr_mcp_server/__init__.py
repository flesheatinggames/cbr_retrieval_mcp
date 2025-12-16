"""
CBR MCP Server - Case-Based Reasoning Model Context Protocol Server.

This package provides a production-ready MCP server for AI agent integration
with intelligent case-based reasoning capabilities.
"""

__version__ = "1.0.0"

import logging
import threading

# Try to import FastMCP (may not always be available)
# Use a temporary variable to avoid type assignment conflict
from typing import Any

# Import the module itself for test patching
from . import server as server_module
from .server import (
    VALID_CATEGORIES,
    VALID_SUBCATEGORIES,
    AlertSystem,
    CBRMCPServer,
    CBRServerConfig,
    ConfigurationValidator,
    DashboardConfig,
    DashboardServer,
    EnhancedLogger,
    ErrorClassifier,
    ErrorSeverity,
    ErrorType,
    FallbackHandler,
    HealthAPI,
    HealthMonitor,
    LogConfig,
    LoggerManager,
    MetricsBroadcaster,
    MetricsCollector,
    MonitoringConfig,
    PerformanceTracker,
    ProductionCBRRetriever,
    RequestInterceptor,
    ResourceMonitor,
    RetryManager,
    RetryPolicy,
    SentenceTransformer,
    SignalHandler,
    StructuredLogger,
    SystemMetrics,
    WebSocketManager,
    chromadb,
    load_configuration_from_file,
    load_configuration_with_env_overrides,
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
    "threading",
    # Logging infrastructure
    "StructuredLogger",
    "LogConfig",
    "LoggerManager",
    "EnhancedLogger",
    # Monitoring and performance
    "PerformanceTracker",
    "RequestInterceptor",
    "SystemMetrics",
    "MonitoringConfig",
    "ResourceMonitor",
    "MetricsCollector",
    "AlertSystem",
    # Error recovery system
    "RetryManager",
    "RetryPolicy",
    "ErrorClassifier",
    "FallbackHandler",
    "ErrorType",
    "ErrorSeverity",
    # Production infrastructure
    "HealthAPI",
    "HealthMonitor",
    "WebSocketManager",
    "SignalHandler",
    "DashboardConfig",
    "DashboardServer",
    "MetricsBroadcaster",
    # Validation constants
    "VALID_CATEGORIES",
    "VALID_SUBCATEGORIES",
    # Configuration validation
    "ConfigurationValidator",
    "load_configuration_from_file",
    "load_configuration_with_env_overrides",
    "startup_configuration_validator",
    # Main entry point
    "main",
    # Optional imports
    "FastMCP",
    # Version
    "__version__",
]
