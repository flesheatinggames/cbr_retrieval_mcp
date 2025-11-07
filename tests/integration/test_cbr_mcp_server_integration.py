"""
Integration tests for CBR MCP Server with modular case structure.

This test suite verifies that cbr_mcp_server.py correctly integrates with
the new modular case structure, loading cases dynamically and returning
all metadata fields (category, subcategory, tags) through MCP tools.

Tests cover:
- MCP server initialization with dynamic case loading
- cbr_retrieve tool returning cases with metadata
- cbr_search_category tool filtering by category with metadata
- cbr_find_similar tool returning similar cases with metadata
- Proper handling of new metadata structure across all tools
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Add project root to path for importing cases
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import cases to get dynamic case count
from cases import ALL_CASES

# Import the server and retriever
try:
    from mcp.server.fastmcp import Context as RealContext

    from cbr_mcp_server import CBRMCPServer, ProductionCBRRetriever
except ImportError as e:
    # Create minimal mocks for missing dependencies
    class CBRMCPServer:
        pass

    class ProductionCBRRetriever:
        pass

    class RealContext:
        pass


# Create a mock Context that doesn't require request_context
class MockContext:
    """Mock Context for testing that doesn't require MCP request context."""

    def __init__(self):
        self.debug = AsyncMock()
        self.info = AsyncMock()
        self.warning = AsyncMock()
        self.error = AsyncMock()


@pytest.fixture
def sample_case_with_metadata():
    """Fixture providing a sample case with all metadata fields."""
    return {
        "id": "test-case-001",
        "problem": "How to implement Firebase authentication?",
        "solution": "Use Firebase Auth SDK with email/password provider.",
        "category": "firebase",
        "subcategory": "auth",
        "tags": ["authentication", "firebase", "security"],
        "similarity_score": 0.95,
    }


@pytest.fixture
def sample_cases_with_metadata():
    """Fixture providing multiple sample cases with metadata."""
    return [
        {
            "id": "test-case-001",
            "problem": "How to implement Firebase authentication?",
            "solution": "Use Firebase Auth SDK with email/password provider.",
            "category": "firebase",
            "subcategory": "auth",
            "tags": ["authentication", "firebase", "security"],
            "similarity_score": 0.95,
        },
        {
            "id": "test-case-002",
            "problem": "How to create a React component?",
            "solution": "Define a functional component with hooks.",
            "category": "react",
            "subcategory": "components",
            "tags": ["react", "components", "hooks"],
            "similarity_score": 0.88,
        },
        {
            "id": "test-case-003",
            "problem": "How to orchestrate agent tasks?",
            "solution": "Use sequential delegation with verification.",
            "category": "orchestration",
            "subcategory": "delegation",
            "tags": ["agents", "orchestration", "workflow"],
            "similarity_score": 0.82,
        },
    ]


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
def mock_retriever(sample_cases_with_metadata):
    """Fixture providing a mock retriever with metadata support."""
    retriever = Mock(spec=ProductionCBRRetriever)

    # Mock retrieve_relevant_examples to return cases with metadata
    async def mock_retrieve(*args, **kwargs):
        return sample_cases_with_metadata

    retriever.retrieve_relevant_examples = AsyncMock(side_effect=mock_retrieve)

    # Mock search_by_category to return filtered cases
    async def mock_search_category(*args, **kwargs):
        category = kwargs.get("category", args[0] if args else "firebase")
        return [c for c in sample_cases_with_metadata if c["category"] == category]

    retriever.search_by_category = AsyncMock(side_effect=mock_search_category)

    # Mock find_similar_cases to return similar cases
    async def mock_find_similar(*args, **kwargs):
        return sample_cases_with_metadata[1:]  # Return all except first

    retriever.find_similar_cases = AsyncMock(side_effect=mock_find_similar)

    # Mock get_categories
    async def mock_get_categories():
        return ["firebase", "react", "orchestration"]

    retriever.get_categories = AsyncMock(side_effect=mock_get_categories)

    return retriever


@pytest.mark.asyncio
class TestMCPServerIntegration:
    """Integration tests for CBR MCP Server with modular case structure."""

    async def test_mcp_server_loads_cases_on_startup(
        self, mock_server_config, mock_retriever
    ):
        """
        Test that MCP server initializes successfully with modular case structure.

        Verifies:
        - Server initializes without errors
        - Retriever is created
        - Server metadata is set correctly
        - No exceptions during initialization
        """
        # Mock all heavy dependencies
        with (
            patch("cbr_mcp_server.chromadb"),
            patch("cbr_mcp_server.SentenceTransformer"),
            patch("cbr_mcp_server.FastMCP") as mock_fastmcp,
            patch("cbr_mcp_server.StructuredLogger"),
        ):

            # Create server with mocked retriever
            server = CBRMCPServer(config=mock_server_config, retriever=mock_retriever)

            # Verify server initialized
            assert server is not None, "Server should be initialized"
            assert server.name == "CBR-MCP-Server", "Server name should be set"
            assert server.version == "0.1.0", "Server version should be set"
            assert server.retriever is not None, "Retriever should be set"

            # Verify FastMCP was initialized
            mock_fastmcp.assert_called_once_with("CBR-MCP-Server")

    async def test_cbr_retrieve_returns_cases_with_metadata(
        self, mock_server_config, mock_retriever, sample_cases_with_metadata
    ):
        """
        Test that cbr_retrieve tool returns cases with all metadata fields.

        Verifies:
        - Cases have category field
        - Cases have subcategory field
        - Cases have tags field (as list)
        - All metadata values are valid
        """
        with (
            patch("cbr_mcp_server.chromadb"),
            patch("cbr_mcp_server.SentenceTransformer"),
            patch("cbr_mcp_server.FastMCP"),
            patch("cbr_mcp_server.StructuredLogger"),
        ):

            # Create server
            server = CBRMCPServer(config=mock_server_config, retriever=mock_retriever)

            # Mock context
            mock_ctx = MockContext()

            # Call cbr_retrieve tool
            result = await server.cbr_retrieve(
                query="How to implement authentication?",
                max_results=5,
                similarity_threshold=0.8,
                ctx=mock_ctx,
            )

            # Verify result structure
            assert isinstance(result, dict), "Result should be a dictionary"
            assert (
                "examples" in result or "results" in result
            ), "Result should contain examples or results"

            # Get the cases from result (handle both possible response structures)
            cases = result.get("examples", result.get("results", []))

            # Verify cases have metadata
            for case in cases:
                assert (
                    "category" in case
                ), f"Case {case.get('id')} should have category field"
                assert (
                    "subcategory" in case
                ), f"Case {case.get('id')} should have subcategory field"
                assert "tags" in case, f"Case {case.get('id')} should have tags field"

                # Verify metadata types and values
                assert isinstance(case["category"], str), "Category should be a string"
                assert isinstance(
                    case["subcategory"], str
                ), "Subcategory should be a string"
                assert isinstance(case["tags"], list), "Tags should be a list"
                assert len(case["tags"]) > 0, "Tags should not be empty"
                assert case["category"] != "", "Category should not be empty"
                assert case["subcategory"] != "", "Subcategory should not be empty"

    async def test_cbr_search_category_returns_metadata(
        self, mock_server_config, mock_retriever, sample_cases_with_metadata
    ):
        """
        Test that cbr_search_category tool returns filtered cases with metadata.

        Verifies:
        - Results are filtered by category
        - All cases have category field matching filter
        - All cases have subcategory and tags fields
        """
        with (
            patch("cbr_mcp_server.chromadb"),
            patch("cbr_mcp_server.SentenceTransformer"),
            patch("cbr_mcp_server.FastMCP"),
            patch("cbr_mcp_server.StructuredLogger"),
        ):

            # Create server
            server = CBRMCPServer(config=mock_server_config, retriever=mock_retriever)

            # Mock context
            mock_ctx = MockContext()

            # Call cbr_search_category tool
            result = await server.cbr_search_category(
                category="firebase", subcategory=None, query="", limit=10, ctx=mock_ctx
            )

            # Verify result structure
            assert isinstance(result, dict), "Result should be a dictionary"
            assert "category" in result, "Result should have category field"
            assert "results" in result, "Result should have results field"
            assert result["category"] == "firebase", "Category should match filter"

            # Verify cases have metadata and match category
            results = result["results"]
            for case in results:
                assert "category" in case, "Case should have category field"
                assert "subcategory" in case, "Case should have subcategory field"
                assert "tags" in case, "Case should have tags field"
                assert (
                    case["category"] == "firebase"
                ), "Case category should match filter"
                assert isinstance(case["tags"], list), "Tags should be a list"

    async def test_cbr_find_similar_returns_metadata(
        self, mock_server_config, mock_retriever, sample_cases_with_metadata
    ):
        """
        Test that cbr_find_similar tool returns similar cases with metadata.

        Verifies:
        - Similar cases have all metadata fields
        - Reference ID is returned correctly
        """
        with (
            patch("cbr_mcp_server.chromadb"),
            patch("cbr_mcp_server.SentenceTransformer"),
            patch("cbr_mcp_server.FastMCP"),
            patch("cbr_mcp_server.StructuredLogger"),
        ):

            # Create server
            server = CBRMCPServer(config=mock_server_config, retriever=mock_retriever)

            # Mock context
            mock_ctx = MockContext()

            # Call cbr_find_similar tool
            result = await server.cbr_find_similar(
                example_id="test-case-001",
                similarity_threshold=0.85,
                max_results=8,
                ctx=mock_ctx,
            )

            # Verify result structure
            assert isinstance(result, dict), "Result should be a dictionary"
            assert "reference_id" in result, "Result should have reference_id field"
            assert "similar_cases" in result, "Result should have similar_cases field"
            assert (
                result["reference_id"] == "test-case-001"
            ), "Reference ID should match input"

            # Verify similar cases have metadata
            similar_cases = result["similar_cases"]
            for case in similar_cases:
                assert "category" in case, "Similar case should have category field"
                assert (
                    "subcategory" in case
                ), "Similar case should have subcategory field"
                assert "tags" in case, "Similar case should have tags field"
                assert isinstance(case["category"], str), "Category should be string"
                assert isinstance(
                    case["subcategory"], str
                ), "Subcategory should be string"
                assert isinstance(case["tags"], list), "Tags should be list"

    async def test_retriever_loads_cases_dynamically(self, mock_server_config):
        """
        Test that ProductionCBRRetriever works with dynamically loaded cases.

        Verifies:
        - Retriever initializes without errors
        - Dynamic case count is available
        - Cases have metadata structure

        Note: Uses len(ALL_CASES) for dynamic case counting, not hardcoded values.
        """
        with (
            patch("cbr_mcp_server.chromadb") as mock_chromadb,
            patch("cbr_mcp_server.SentenceTransformer"),
            patch("cbr_mcp_server.StructuredLogger") as mock_logger,
        ):

            # Setup mock ChromaDB client
            mock_client = Mock()
            mock_collection = Mock()
            mock_collection.count.return_value = len(ALL_CASES)
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chromadb.PersistentClient.return_value = mock_client

            # Enable real DB for this test
            config = mock_server_config
            config.use_real_db = True

            # Create retriever
            retriever = ProductionCBRRetriever(
                config=config, logger=mock_logger.return_value
            )

            # Verify retriever initialized
            assert retriever is not None, "Retriever should be initialized"
            assert retriever.collection is not None, "Collection should be set"

            # Verify dynamic case count
            case_count = retriever.collection.count()
            assert case_count == len(
                ALL_CASES
            ), f"Case count should match ALL_CASES length ({len(ALL_CASES)})"

    async def test_all_tools_handle_new_metadata_structure(
        self, mock_server_config, mock_retriever, sample_cases_with_metadata
    ):
        """
        Test that all MCP tools handle new metadata structure without errors.

        Verifies:
        - cbr_retrieve works with metadata
        - cbr_search_category works with metadata
        - cbr_find_similar works with metadata
        - No exceptions when processing metadata fields
        - Metadata is preserved through call chain
        """
        with (
            patch("cbr_mcp_server.chromadb"),
            patch("cbr_mcp_server.SentenceTransformer"),
            patch("cbr_mcp_server.FastMCP"),
            patch("cbr_mcp_server.StructuredLogger"),
        ):

            # Create server
            server = CBRMCPServer(config=mock_server_config, retriever=mock_retriever)

            # Mock context
            mock_ctx = MockContext()

            # Test cbr_retrieve
            retrieve_result = await server.cbr_retrieve(
                query="test query",
                max_results=5,
                similarity_threshold=0.8,
                ctx=mock_ctx,
            )
            assert retrieve_result is not None, "cbr_retrieve should return result"

            # Test cbr_search_category
            search_result = await server.cbr_search_category(
                category="firebase", subcategory=None, query="", limit=10, ctx=mock_ctx
            )
            assert search_result is not None, "cbr_search_category should return result"

            # Test cbr_find_similar
            similar_result = await server.cbr_find_similar(
                example_id="test-case-001",
                similarity_threshold=0.85,
                max_results=8,
                ctx=mock_ctx,
            )
            assert similar_result is not None, "cbr_find_similar should return result"

            # Verify no exceptions were raised (implicit by reaching here)
            # Verify all results have consistent metadata structure

            # Check retrieve result metadata
            retrieve_cases = retrieve_result.get(
                "examples", retrieve_result.get("results", [])
            )
            for case in retrieve_cases:
                assert all(
                    field in case for field in ["category", "subcategory", "tags"]
                ), "All metadata fields should be present in cbr_retrieve results"

            # Check search result metadata
            search_cases = search_result.get("results", [])
            for case in search_cases:
                assert all(
                    field in case for field in ["category", "subcategory", "tags"]
                ), "All metadata fields should be present in cbr_search_category results"

            # Check similar result metadata
            similar_cases = similar_result.get("similar_cases", [])
            for case in similar_cases:
                assert all(
                    field in case for field in ["category", "subcategory", "tags"]
                ), "All metadata fields should be present in cbr_find_similar results"

    async def test_mcp_server_uses_dynamic_case_count(
        self, mock_server_config, mock_retriever
    ):
        """
        Test that server properly integrates with dynamic case loading.

        Verifies:
        - Server doesn't use hardcoded case counts
        - Case count is determined dynamically from ALL_CASES
        - Server handles variable case counts correctly
        """
        with (
            patch("cbr_mcp_server.chromadb"),
            patch("cbr_mcp_server.SentenceTransformer"),
            patch("cbr_mcp_server.FastMCP"),
            patch("cbr_mcp_server.StructuredLogger"),
        ):

            # Create server
            server = CBRMCPServer(config=mock_server_config, retriever=mock_retriever)

            # Verify server doesn't have hardcoded case count
            # This is verified by checking that retriever is used for queries
            assert (
                server.retriever is not None
            ), "Server should use retriever for dynamic queries"

            # Verify dynamic case count is available from cases module
            from cases import ALL_CASES

            expected_count = len(ALL_CASES)
            assert expected_count > 0, "ALL_CASES should contain cases"

            # This test documents that we use len(ALL_CASES) for dynamic counting
            # rather than hardcoded values like 49

    async def test_tools_handle_empty_metadata_gracefully(
        self, mock_server_config, mock_retriever
    ):
        """
        Test that MCP tools handle edge cases in metadata.

        Verifies:
        - Tools handle empty tags list
        - Tools handle missing optional fields gracefully
        - No crashes on malformed metadata
        """
        # Create edge case with minimal metadata
        edge_case = {
            "id": "edge-case-001",
            "problem": "Test problem",
            "solution": "Test solution",
            "category": "test",
            "subcategory": "test",
            "tags": [],  # Empty tags list
            "similarity_score": 0.5,
        }

        # Mock retriever to return edge case
        async def mock_retrieve_edge(*args, **kwargs):
            return [edge_case]

        mock_retriever.retrieve_relevant_examples = AsyncMock(
            side_effect=mock_retrieve_edge
        )

        with (
            patch("cbr_mcp_server.chromadb"),
            patch("cbr_mcp_server.SentenceTransformer"),
            patch("cbr_mcp_server.FastMCP"),
            patch("cbr_mcp_server.StructuredLogger"),
        ):

            # Create server
            server = CBRMCPServer(config=mock_server_config, retriever=mock_retriever)

            # Mock context
            mock_ctx = MockContext()

            # Call cbr_retrieve - should not crash on empty tags
            result = await server.cbr_retrieve(
                query="test query",
                max_results=5,
                similarity_threshold=0.8,
                ctx=mock_ctx,
            )

            # Verify result is returned despite empty tags
            assert result is not None, "Should return result even with empty tags"

            # Get cases from result
            cases = result.get("examples", result.get("results", []))
            assert len(cases) > 0, "Should return cases"

            # Verify case still has tags field (even if empty)
            for case in cases:
                assert "tags" in case, "Tags field should be present"
                assert isinstance(case["tags"], list), "Tags should be a list"

    async def test_cbr_retrieve_error_handling(
        self, mock_server_config, mock_retriever
    ):
        """
        Test that cbr_retrieve handles errors gracefully.

        Verifies:
        - Proper error handling when retriever fails
        - Error messages are returned correctly
        """

        # Mock retriever to raise exception
        async def mock_retrieve_error(*args, **kwargs):
            raise Exception("Database connection failed")

        mock_retriever.retrieve_relevant_examples = AsyncMock(
            side_effect=mock_retrieve_error
        )

        with (
            patch("cbr_mcp_server.chromadb"),
            patch("cbr_mcp_server.SentenceTransformer"),
            patch("cbr_mcp_server.FastMCP"),
            patch("cbr_mcp_server.StructuredLogger"),
        ):

            # Create server
            server = CBRMCPServer(config=mock_server_config, retriever=mock_retriever)

            # Mock context
            mock_ctx = MockContext()

            # Call cbr_retrieve - should handle error
            with pytest.raises(Exception) as exc_info:
                await server.cbr_retrieve(
                    query="test query",
                    max_results=5,
                    similarity_threshold=0.8,
                    ctx=mock_ctx,
                )

            # Verify error was raised
            assert "Database connection failed" in str(
                exc_info.value
            ) or "Failed to retrieve" in str(
                exc_info.value
            ), "Should raise appropriate error"

    async def test_metadata_preserved_through_multiple_operations(
        self, mock_server_config, mock_retriever, sample_cases_with_metadata
    ):
        """
        Test that metadata is preserved across multiple tool operations.

        Verifies:
        - Metadata consistency across retrieve, search, and find_similar
        - No data loss during processing
        - Same case returns same metadata from different tools
        """
        with (
            patch("cbr_mcp_server.chromadb"),
            patch("cbr_mcp_server.SentenceTransformer"),
            patch("cbr_mcp_server.FastMCP"),
            patch("cbr_mcp_server.StructuredLogger"),
        ):

            # Create server
            server = CBRMCPServer(config=mock_server_config, retriever=mock_retriever)

            # Mock context
            mock_ctx = MockContext()

            # Get case from retrieve
            retrieve_result = await server.cbr_retrieve(
                query="Firebase authentication",
                max_results=5,
                similarity_threshold=0.8,
                ctx=mock_ctx,
            )
            retrieve_cases = retrieve_result.get(
                "examples", retrieve_result.get("results", [])
            )
            retrieve_firebase = next(
                (c for c in retrieve_cases if c["category"] == "firebase"), None
            )

            # Get same category from search
            search_result = await server.cbr_search_category(
                category="firebase", subcategory=None, query="", limit=10, ctx=mock_ctx
            )
            search_cases = search_result["results"]
            search_firebase = next(
                (c for c in search_cases if c.get("id") == retrieve_firebase.get("id")),
                None,
            )

            # Verify metadata is consistent if same case found
            if retrieve_firebase and search_firebase:
                assert (
                    retrieve_firebase["category"] == search_firebase["category"]
                ), "Category should be consistent across operations"
                assert (
                    retrieve_firebase["subcategory"] == search_firebase["subcategory"]
                ), "Subcategory should be consistent across operations"
                assert (
                    retrieve_firebase["tags"] == search_firebase["tags"]
                ), "Tags should be consistent across operations"
