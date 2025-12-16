"""
Load and stress testing package for CBR MCP Server.

This package contains comprehensive load and stress tests to validate
the performance characteristics of the CBR retrieval system under
various load conditions.

Test Categories:
- Sustained Load Tests: Continuous typical load over extended periods
- Concurrent Query Stress Tests: High concurrent query volumes
- Memory Pressure Stress Tests: Near-limit memory scenarios
- Cache Churn Stress Tests: High cache turnover scenarios
- Spike Load Tests: Sudden traffic spikes and recovery

All tests use shared session-scoped fixtures to prevent memory regression
from multiple model/retriever instances.
"""
