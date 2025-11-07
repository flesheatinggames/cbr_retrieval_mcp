"""
MCP Tool Integration Tests for cbr_search_category.

This test suite verifies that the cbr_search_category MCP tool correctly integrates
with the fixed metadata storage system, returning cases with complete metadata
(category, subcategory, tags) when filtering by category and subcategory.

These tests are part of Phase 3 (MCP Integration) of the metadata storage bug fix:
@.agent-os/specs/2025-11-04-metadata-storage-bug-fix/spec.md

Test Group: MCP Tool Integration (from tests.md lines 223-250)
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

import cbr_mcp_server as cbr_mcp_server_module

# Standard Python imports
from cbr_mcp_server import CBRMCPServer, ProductionCBRRetriever

# ============================================================================
# Mock Context for Testing
# ============================================================================


class MockContext:
    """Mock Context for testing that doesn't require MCP request context."""

    def __init__(self):
        self.debug = AsyncMock()
        self.info = AsyncMock()
        self.warning = AsyncMock()
        self.error = AsyncMock()


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_server_config():
    """Fixture providing a mock server configuration."""
    mock_config = Mock()
    mock_config.validate_production.return_value = None
    mock_config.require_auth = False
    mock_config.rate_limit_enabled = False
    mock_config.use_real_db = False
    mock_config.cache_enabled = False
    mock_config.database_path = "./test_db"
    mock_config.collection_name = "test_collection"
    mock_config.embedding_model = "nomic-ai/nomic-embed-text-v1.5"
    mock_config.max_results_default = 10
    mock_config.similarity_threshold_default = 0.7
    mock_config.enable_health_checks = True
    mock_config.log_level = "INFO"
    mock_config.db_path = "./test_db"
    mock_config.api_keys = []
    mock_config.admin_keys = []
    mock_config.rate_limit_requests = 100
    mock_config.rate_limit_window = 3600
    mock_config.input_validation = "permissive"
    mock_config.max_query_length = 10000
    mock_config.sanitization = True
    mock_config.health_check_interval = 60
    mock_config.circuit_breaker_failure_threshold = 5
    mock_config.circuit_breaker_timeout = 60
    mock_config.cache_ttl = 300
    mock_config.cache_max_size = 100
    mock_config.retry_enabled = False  # Disable retry/degraded mode for tests

    return mock_config


@pytest.fixture
def sample_orchestration_cases():
    """
    Fixture providing sample orchestration cases with complete metadata.

    These cases simulate what the database should return after the metadata fix.
    """
    return [
        {
            "id": "orch-001",
            "problem": "How to plan a multi-step agent workflow",
            "solution": "Use sequential delegation with verification checkpoints",
            "category": "orchestration",
            "subcategory": "planning",
            "tags": ["orchestration", "planning", "delegation"],
            "similarity_score": 0.95,
        },
        {
            "id": "orch-002",
            "problem": "How to create a detailed implementation plan",
            "solution": "Break down features into verifiable units of work",
            "category": "orchestration",
            "subcategory": "planning",
            "tags": ["orchestration", "planning", "decomposition"],
            "similarity_score": 0.92,
        },
        {
            "id": "orch-003",
            "problem": "How to delegate tasks to specialist agents",
            "solution": "Use delegation protocol with clear objectives",
            "category": "orchestration",
            "subcategory": "delegation",
            "tags": ["orchestration", "delegation", "agents"],
            "similarity_score": 0.88,
        },
    ]


@pytest.fixture
def mock_retriever_orchestration(sample_orchestration_cases):
    """
    Fixture providing a mock retriever that returns orchestration cases.

    This simulates the retriever behavior after the metadata fix is applied.
    """
    retriever = Mock(spec=ProductionCBRRetriever)

    # Mock search_by_category to return all orchestration cases
    async def mock_search_category(*args, **kwargs):
        category = kwargs.get("category", args[0] if args else None)
        subcategory = kwargs.get("subcategory", None)

        # Filter by category
        filtered = [c for c in sample_orchestration_cases if c["category"] == category]

        # Further filter by subcategory if provided
        if subcategory:
            filtered = [c for c in filtered if c["subcategory"] == subcategory]

        return filtered

    retriever.search_by_category = AsyncMock(side_effect=mock_search_category)

    return retriever


@pytest.fixture
def mock_retriever_error():
    """
    Fixture providing a mock retriever that raises errors for invalid categories.

    This tests error handling in the MCP tool integration.
    """
    retriever = Mock(spec=ProductionCBRRetriever)

    # Mock search_by_category to raise ValueError for invalid categories
    async def mock_search_category_error(*args, **kwargs):
        category = kwargs.get("category", args[0] if args else None)

        # Raise error for invalid categories
        if category not in ["orchestration", "firebase", "rust", "react"]:
            raise ValueError(
                f"Invalid category: '{category}'. Must be one of: orchestration, firebase, rust, react"
            )

        return []

    retriever.search_by_category = AsyncMock(side_effect=mock_search_category_error)

    return retriever


# ============================================================================
# Test 1: MCP Tool Call with Category="orchestration"
# ============================================================================


@pytest.mark.asyncio
async def test_mcp_cbr_search_category_tool_orchestration(
    mock_server_config, mock_retriever_orchestration
):
    """
    Test that MCP tool cbr_search_category returns orchestration cases with metadata.

    Given: MCP server with fixed database (complete metadata)
    When: Calling MCP tool cbr_search_category with category="orchestration"
    Then:
      - Tool call succeeds
      - Returns JSON response with category and results fields
      - Results contain orchestration cases
      - All returned cases have category="orchestration" in metadata
    """
    with (
        patch.object(cbr_mcp_server_module, "chromadb"),
        patch.object(cbr_mcp_server_module, "SentenceTransformer"),
        patch.object(cbr_mcp_server_module, "FastMCP"),
        patch.object(cbr_mcp_server_module, "StructuredLogger"),
    ):

        # Create server with mocked retriever
        server = CBRMCPServer(
            config=mock_server_config, retriever=mock_retriever_orchestration
        )

        # Mock context
        mock_ctx = MockContext()

        # Call cbr_search_category tool with category="orchestration"
        result = await server.cbr_search_category(
            category="orchestration", subcategory=None, query="", limit=10, ctx=mock_ctx
        )

        # Assertion 1: Tool call succeeds (no exception raised)
        assert result is not None, "Tool should return a result, not None"

        # Assertion 2: Returns JSON response with category and results fields
        assert isinstance(result, dict), "Result should be a dictionary (JSON response)"
        assert "category" in result, "Result should have 'category' field"
        assert "results" in result, "Result should have 'results' field"

        # Assertion 3: Results contain orchestration cases
        assert (
            result["category"] == "orchestration"
        ), "Category field should be 'orchestration'"
        assert isinstance(result["results"], list), "Results should be a list"
        assert (
            len(result["results"]) > 0
        ), "Should return at least one orchestration case"

        # Assertion 4: All returned cases have category="orchestration" in metadata
        for case in result["results"]:
            assert (
                "category" in case
            ), f"Case {case.get('id')} should have 'category' field"
            assert (
                case["category"] == "orchestration"
            ), f"Expected category='orchestration', got '{case.get('category')}'"

            # Verify other metadata fields are present
            assert (
                "subcategory" in case
            ), f"Case {case.get('id')} should have 'subcategory' field"
            assert "tags" in case, f"Case {case.get('id')} should have 'tags' field"


# ============================================================================
# Test 2: MCP Tool Call with Category and Subcategory
# ============================================================================


@pytest.mark.asyncio
async def test_mcp_cbr_search_category_tool_with_subcategory(
    mock_server_config, mock_retriever_orchestration
):
    """
    Test that MCP tool filters by both category and subcategory correctly.

    Given: MCP server with fixed database
    When: Calling MCP tool with category="orchestration", subcategory="planning"
    Then:
      - Tool call succeeds
      - Returns filtered results
      - All results match both category="orchestration" AND subcategory="planning"
    """
    with (
        patch.object(cbr_mcp_server_module, "chromadb"),
        patch.object(cbr_mcp_server_module, "SentenceTransformer"),
        patch.object(cbr_mcp_server_module, "FastMCP"),
        patch.object(cbr_mcp_server_module, "StructuredLogger"),
    ):

        # Create server with mocked retriever
        server = CBRMCPServer(
            config=mock_server_config, retriever=mock_retriever_orchestration
        )

        # Mock context
        mock_ctx = MockContext()

        # Call cbr_search_category tool with both category and subcategory
        result = await server.cbr_search_category(
            category="orchestration",
            subcategory="planning",
            query="",
            limit=10,
            ctx=mock_ctx,
        )

        # Assertion 1: Tool call succeeds
        assert result is not None, "Tool should return a result, not None"
        assert isinstance(result, dict), "Result should be a dictionary"

        # Assertion 2: Returns filtered results
        assert "results" in result, "Result should have 'results' field"
        assert isinstance(result["results"], list), "Results should be a list"
        assert len(result["results"]) > 0, "Should return at least one planning case"

        # Assertion 3: All results match BOTH category and subcategory
        for case in result["results"]:
            assert (
                "category" in case
            ), f"Case {case.get('id')} should have 'category' field"
            assert (
                "subcategory" in case
            ), f"Case {case.get('id')} should have 'subcategory' field"

            assert (
                case["category"] == "orchestration"
            ), f"Expected category='orchestration', got '{case.get('category')}'"
            assert (
                case["subcategory"] == "planning"
            ), f"Expected subcategory='planning', got '{case.get('subcategory')}'"


# ============================================================================
# Test 3: MCP Tool Error Handling
# ============================================================================


@pytest.mark.asyncio
async def test_mcp_cbr_search_category_tool_error_handling(
    mock_server_config, mock_retriever_error
):
    """
    Test that MCP tool handles invalid category gracefully.

    Given: MCP server with fixed database
    When: Calling MCP tool with invalid category
    Then:
      - Tool returns error response
      - Error message indicates invalid category
      - Server remains stable
    """
    with (
        patch.object(cbr_mcp_server_module, "chromadb"),
        patch.object(cbr_mcp_server_module, "SentenceTransformer"),
        patch.object(cbr_mcp_server_module, "FastMCP"),
        patch.object(cbr_mcp_server_module, "StructuredLogger"),
    ):

        # Create server with error-raising retriever
        server = CBRMCPServer(config=mock_server_config, retriever=mock_retriever_error)

        # Mock context
        mock_ctx = MockContext()

        # Attempt to call cbr_search_category tool with invalid category
        # The server wraps ValueError in Exception, so we expect Exception
        with pytest.raises(Exception) as exc_info:
            await server.cbr_search_category(
                category="invalid_category",
                subcategory=None,
                query="",
                limit=10,
                ctx=mock_ctx,
            )

        # Assertion 1: Error message indicates invalid category
        error_message = str(exc_info.value)
        assert (
            "Invalid category" in error_message or "invalid" in error_message.lower()
        ), f"Error message should mention invalid category, got: {error_message}"

        # Assertion 2: Error message mentions the invalid category name
        assert (
            "invalid_category" in error_message
        ), f"Error message should mention the invalid category name, got: {error_message}"

        # Assertion 3: Server remains stable (test passes without crashes)
        # If we got here, the server handled the error gracefully
        assert True, "Server should remain stable after error"
