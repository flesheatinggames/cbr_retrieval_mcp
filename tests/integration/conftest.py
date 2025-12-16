"""
Shared fixtures for integration tests.

This file makes fixtures from performance_helpers.py available to all
integration tests via pytest's fixture discovery mechanism.
"""

# Re-export all fixtures from performance_helpers
from performance_helpers import (
    mock_chromadb_client,
    mock_mcp_server,
    sample_workload_large,
    sample_workload_medium,
    sample_workload_small,
)

__all__ = [
    "sample_workload_small",
    "sample_workload_medium",
    "sample_workload_large",
    "mock_chromadb_client",
    "mock_mcp_server",
]
