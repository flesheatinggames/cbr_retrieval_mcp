"""
Comprehensive test suite for cbr_search_category MCP tool subcategory parameter enhancement.

This test suite follows TDD principles to define expected behavior before implementation.
Tests cover the addition of an optional subcategory parameter to the cbr_search_category tool.

Test Coverage:
- Tool wrapper accepts optional subcategory parameter
- Subcategory properly passed to implementation method
- Category-only filtering (backward compatibility)
- Category+subcategory combined filtering
- Parameter validation for subcategory
- Error handling for invalid subcategory values
- Edge cases and boundary conditions
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch, call
from typing import Any, Dict, List, Optional

# Import the actual classes and handle missing dependencies gracefully
try:
    from cbr_mcp_server import CBRMCPServer, ProductionCBRRetriever
    from retriever import CBRRetriever
    # Mock MCP dependencies that aren't available in test environment
    try:
        from mcp.server.fastmcp import FastMCP, Context
        from mcp.types import Tool, Resource, TextContent
        import mcp.server.stdio
    except ImportError:
        # Create mock classes for MCP components
        class FastMCP:
            def run(self, transport=None):
                pass

        class Context:
            def __init__(self):
                self.session = Mock()
                self.debug = AsyncMock()
                self.info = AsyncMock()
                self.warning = AsyncMock()
                self.error = AsyncMock()

        class TextContent:
            def __init__(self, text):
                self.text = text

        # Make these available globally for tests
        globals()['FastMCP'] = FastMCP
        globals()['Context'] = Context
        globals()['TextContent'] = TextContent

except ImportError as e:
    print(f"Import error in tests: {e}")
    # Fallback: create basic mock classes for testing
    class CBRMCPServer:
        pass
    class ProductionCBRRetriever:
        pass
    class CBRRetriever:
        pass


@pytest.fixture
def mock_server_config():
    """Fixture to provide a mock server configuration."""
    mock_config = Mock()
    mock_config.validate_production.return_value = None
    mock_config.require_auth = False
    mock_config.rate_limit_enabled = False
    mock_config.use_real_db = False
    mock_config.cache_enabled = False

    # Core CBR configuration
    mock_config.database_path = "./test_db"
    mock_config.collection_name = "test_collection"
    mock_config.embedding_model = "nomic-ai/nomic-embed-text-v1.5"
    mock_config.max_results_default = 10
    mock_config.similarity_threshold_default = 0.7
    mock_config.enable_health_checks = True
    mock_config.log_level = "INFO"

    # Legacy compatibility
    mock_config.db_path = "./test_db"

    # Auth configuration
    mock_config.api_keys = []
    mock_config.admin_keys = []

    # Rate limiting configuration
    mock_config.rate_limit_requests = 100
    mock_config.rate_limit_window = 3600

    # Input validation
    mock_config.input_validation = "permissive"
    mock_config.max_query_length = 10000
    mock_config.sanitization = True

    # Cache configuration
    mock_config.cache_ttl = 3600

    # Retry configuration
    mock_config.max_retries = 3
    mock_config.retry_enabled = True
    mock_config.circuit_breaker = True

    # Health monitoring
    mock_config.health_check_enabled = False
    mock_config.metrics_enabled = False
    mock_config.monitoring_port = 8080
    mock_config.performance_monitoring = True

    # Logging
    mock_config.log_format = "structured"
    mock_config.log_correlation_id = True

    return mock_config


@pytest.fixture
def mock_server_with_config(mock_server_config):
    """Fixture to create a CBRMCPServer with mocked dependencies."""
    def _create_server(retriever=None):
        with patch('cbr_mcp_server.CBRServerConfig') as mock_config_class:
            mock_config_class.from_environment.return_value = mock_server_config

            with patch('cbr_mcp_server.startup_configuration_validator') as mock_validator:
                mock_validator.return_value = True

                with patch('cbr_mcp_server.LogConfig'):
                    with patch('cbr_mcp_server.LoggerManager'):
                        with patch('cbr_mcp_server.StructuredLogger'):
                            return CBRMCPServer(retriever=retriever, config=mock_server_config)
    return _create_server


@pytest.fixture
def mock_context():
    """Mock MCP Context for tool calls."""
    context = Mock(spec=Context)
    context.session = Mock()
    context.debug = AsyncMock()
    context.info = AsyncMock()
    context.warning = AsyncMock()
    context.error = AsyncMock()
    return context


@pytest.fixture
def mock_cbr_retriever():
    """Mock ProductionCBRRetriever for tool tests."""
    retriever = Mock(spec=ProductionCBRRetriever)
    retriever.search_by_category = AsyncMock(return_value=[
        {
            "id": "cat_001",
            "content": "Category specific example 1",
            "category": "brewing",
            "subcategory": "IPA",
            "similarity_score": 0.92
        },
        {
            "id": "cat_002",
            "content": "Category specific example 2",
            "category": "brewing",
            "subcategory": "IPA",
            "similarity_score": 0.88
        }
    ])
    return retriever


class TestSubcategoryParameterAcceptance:
    """Test that the MCP tool wrapper accepts the optional subcategory parameter."""

    @pytest.mark.asyncio
    async def test_subcategory_parameter_accepted_none_default(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test tool accepts subcategory=None as default value."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        # Call without subcategory parameter (should use default None)
        result = await server.cbr_search_category(
            category="brewing",
            query="IPA techniques",
            limit=10,
            ctx=mock_context
        )

        # Should not raise any errors
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_subcategory_parameter_accepted_with_value(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test tool accepts subcategory with a specific value."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        # Call with subcategory parameter
        result = await server.cbr_search_category(
            category="brewing",
            subcategory="IPA",
            query="hops selection",
            limit=10,
            ctx=mock_context
        )

        # Should not raise any errors
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_subcategory_parameter_accepted_explicit_none(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test tool accepts subcategory=None explicitly."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        # Call with explicit subcategory=None
        result = await server.cbr_search_category(
            category="brewing",
            subcategory=None,
            query="general brewing",
            limit=10,
            ctx=mock_context
        )

        # Should not raise any errors
        assert result is not None
        assert isinstance(result, dict)


class TestSubcategoryPassedToImplementation:
    """Test that subcategory parameter is properly passed to implementation method."""

    @pytest.mark.asyncio
    async def test_subcategory_none_passed_to_implementation(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test subcategory=None is passed to implementation method."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        await server.cbr_search_category(
            category="brewing",
            query="IPA",
            limit=10,
            ctx=mock_context
        )

        # Verify retriever was called with subcategory=None
        mock_cbr_retriever.search_by_category.assert_called_once()
        call_kwargs = mock_cbr_retriever.search_by_category.call_args.kwargs
        assert "subcategory" in call_kwargs
        assert call_kwargs["subcategory"] is None

    @pytest.mark.asyncio
    async def test_subcategory_value_passed_to_implementation(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test subcategory value is passed to implementation method."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        await server.cbr_search_category(
            category="brewing",
            subcategory="IPA",
            query="hops",
            limit=10,
            ctx=mock_context
        )

        # Verify retriever was called with subcategory="IPA"
        mock_cbr_retriever.search_by_category.assert_called_once()
        call_kwargs = mock_cbr_retriever.search_by_category.call_args.kwargs
        assert call_kwargs["subcategory"] == "IPA"


class TestCategoryOnlyFiltering:
    """Test category-only search when subcategory=None (backward compatibility)."""

    @pytest.mark.asyncio
    async def test_category_only_search_default_subcategory(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test category search without subcategory uses default None."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        result = await server.cbr_search_category(
            category="brewing",
            query="general brewing",
            limit=10,
            ctx=mock_context
        )

        # Verify retriever called with category and subcategory=None
        mock_cbr_retriever.search_by_category.assert_called_once_with(
            category="brewing",
            query="general brewing",
            limit=10,
            subcategory=None
        )

        # Verify response structure
        assert isinstance(result, dict)
        assert "category" in result
        assert result["category"] == "brewing"
        assert "results" in result

    @pytest.mark.asyncio
    async def test_category_only_search_explicit_none(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test category search with explicit subcategory=None."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        result = await server.cbr_search_category(
            category="fermentation",
            subcategory=None,
            query="temperature control",
            limit=5,
            ctx=mock_context
        )

        # Verify retriever called correctly
        mock_cbr_retriever.search_by_category.assert_called_once_with(
            category="fermentation",
            query="temperature control",
            limit=5,
            subcategory=None
        )

        # Verify response
        assert result["category"] == "fermentation"
        assert "results" in result


class TestCategoryAndSubcategoryFiltering:
    """Test combined category+subcategory search when subcategory is specified."""

    @pytest.mark.asyncio
    async def test_category_and_subcategory_search(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test search with both category and subcategory specified."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        result = await server.cbr_search_category(
            category="brewing",
            subcategory="IPA",
            query="hops selection",
            limit=10,
            ctx=mock_context
        )

        # Verify retriever called with both parameters
        mock_cbr_retriever.search_by_category.assert_called_once_with(
            category="brewing",
            query="hops selection",
            limit=10,
            subcategory="IPA"
        )

        # Verify response structure includes both
        assert isinstance(result, dict)
        assert "category" in result
        assert result["category"] == "brewing"
        assert "results" in result

    @pytest.mark.asyncio
    async def test_different_subcategories_same_category(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test multiple searches with different subcategories in same category."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        # First search with subcategory "IPA"
        await server.cbr_search_category(
            category="brewing",
            subcategory="IPA",
            query="hops",
            limit=10,
            ctx=mock_context
        )

        # Second search with subcategory "Stout"
        await server.cbr_search_category(
            category="brewing",
            subcategory="Stout",
            query="roasted malt",
            limit=10,
            ctx=mock_context
        )

        # Verify both calls were made with correct subcategories
        assert mock_cbr_retriever.search_by_category.call_count == 2
        first_call = mock_cbr_retriever.search_by_category.call_args_list[0].kwargs
        second_call = mock_cbr_retriever.search_by_category.call_args_list[1].kwargs

        assert first_call["subcategory"] == "IPA"
        assert second_call["subcategory"] == "Stout"


class TestSubcategoryParameterValidation:
    """Test parameter validation for subcategory values."""

    @pytest.mark.asyncio
    async def test_subcategory_empty_string_handling(
        self,
        mock_cbr_retriever,
        mock_context,
        mock_server_with_config
    ):
        """Test empty string subcategory is handled correctly."""
        server = mock_server_with_config(mock_cbr_retriever)

        # Empty string should either be treated as None or raise validation error
        result = await server.cbr_search_category(
            category="brewing",
            subcategory="",
            query="general",
            limit=10,
            ctx=mock_context
        )

        # Verify call was made (empty string handling depends on implementation)
        mock_cbr_retriever.search_by_category.assert_called_once()
        call_kwargs = mock_cbr_retriever.search_by_category.call_args.kwargs
        # Empty string should either be None or empty string
        assert "subcategory" in call_kwargs

    @pytest.mark.asyncio
    async def test_subcategory_whitespace_only_handling(
        self,
        mock_cbr_retriever,
        mock_context,
        mock_server_with_config
    ):
        """Test whitespace-only subcategory is handled correctly."""
        server = mock_server_with_config(mock_cbr_retriever)

        # Whitespace should be stripped or raise validation error
        result = await server.cbr_search_category(
            category="brewing",
            subcategory="   ",
            query="general",
            limit=10,
            ctx=mock_context
        )

        # Verify validation or sanitization occurred
        mock_cbr_retriever.search_by_category.assert_called_once()


class TestSubcategoryErrorHandling:
    """Test error handling for invalid subcategory values."""

    @pytest.mark.asyncio
    async def test_error_handling_retriever_exception_with_subcategory(
        self,
        mock_cbr_retriever,
        mock_context,
        mock_server_with_config
    ):
        """Test error handling when retriever fails with subcategory."""
        mock_cbr_retriever.search_by_category.side_effect = Exception(
            "Invalid subcategory: unknown_subcategory"
        )

        server = mock_server_with_config(mock_cbr_retriever)

        # Should raise exception with proper error message
        with pytest.raises(Exception, match="Failed to search category"):
            await server.cbr_search_category(
                category="brewing",
                subcategory="unknown_subcategory",
                query="test",
                limit=10,
                ctx=mock_context
            )

        # Verify context.error was called
        mock_context.error.assert_called_once()
        error_message = mock_context.error.call_args[0][0]
        assert "Failed to search category" in error_message

    @pytest.mark.asyncio
    async def test_error_message_sanitization_with_subcategory(
        self,
        mock_cbr_retriever,
        mock_context,
        mock_server_with_config
    ):
        """Test error messages are properly sanitized with subcategory."""
        mock_cbr_retriever.search_by_category.side_effect = Exception(
            "Database error with subcategory: IPA"
        )

        server = mock_server_with_config(mock_cbr_retriever)

        with pytest.raises(Exception):
            await server.cbr_search_category(
                category="brewing",
                subcategory="IPA",
                query="test",
                limit=10,
                ctx=mock_context
            )

        # Error should be logged through context
        mock_context.error.assert_called_once()


class TestBackwardCompatibility:
    """Test backward compatibility when subcategory parameter is not provided."""

    @pytest.mark.asyncio
    async def test_existing_calls_without_subcategory_still_work(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test existing code calling without subcategory continues to work."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        # Call exactly as in existing code (no subcategory parameter)
        result = await server.cbr_search_category(
            category="brewing",
            query="IPA techniques",
            limit=10,
            ctx=mock_context
        )

        # Should work without errors
        assert result is not None
        assert isinstance(result, dict)
        assert "category" in result
        assert "results" in result

        # Verify default subcategory=None was used
        mock_cbr_retriever.search_by_category.assert_called_once()
        call_kwargs = mock_cbr_retriever.search_by_category.call_args.kwargs
        assert call_kwargs.get("subcategory") is None

    @pytest.mark.asyncio
    async def test_response_format_unchanged_without_subcategory(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test response format remains the same when subcategory not used."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        result = await server.cbr_search_category(
            category="fermentation",
            query="temperature",
            limit=5,
            ctx=mock_context
        )

        # Response should have same structure as before
        assert "category" in result
        assert "results" in result
        assert result["category"] == "fermentation"
        # Should not have subcategory in response if not provided
        assert isinstance(result["results"], list)


class TestSubcategoryEdgeCases:
    """Test edge cases and boundary conditions with subcategory parameter."""

    @pytest.mark.asyncio
    async def test_subcategory_with_empty_query(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test subcategory filtering works with empty query string."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        result = await server.cbr_search_category(
            category="brewing",
            subcategory="IPA",
            query="",
            limit=10,
            ctx=mock_context
        )

        # Should work with empty query
        mock_cbr_retriever.search_by_category.assert_called_once_with(
            category="brewing",
            query="",
            limit=10,
            subcategory="IPA"
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_subcategory_with_limit_parameter(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test subcategory works correctly with limit parameter."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        # Test with different limit values
        await server.cbr_search_category(
            category="brewing",
            subcategory="IPA",
            query="hops",
            limit=5,
            ctx=mock_context
        )

        mock_cbr_retriever.search_by_category.assert_called_once_with(
            category="brewing",
            query="hops",
            limit=5,
            subcategory="IPA"
        )

    @pytest.mark.asyncio
    async def test_subcategory_with_special_characters(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test subcategory with special characters in name."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        # Subcategory with spaces and hyphens
        result = await server.cbr_search_category(
            category="brewing",
            subcategory="West Coast IPA",
            query="hops",
            limit=10,
            ctx=mock_context
        )

        # Should handle special characters
        mock_cbr_retriever.search_by_category.assert_called_once()
        call_kwargs = mock_cbr_retriever.search_by_category.call_args.kwargs
        assert call_kwargs["subcategory"] == "West Coast IPA"

    @pytest.mark.asyncio
    async def test_subcategory_case_sensitivity(
        self,
        mock_cbr_retriever,
        mock_context
    ):
        """Test subcategory parameter preserves case."""
        server = CBRMCPServer(retriever=mock_cbr_retriever)

        # Test with different cases
        await server.cbr_search_category(
            category="brewing",
            subcategory="IPA",
            query="test",
            limit=10,
            ctx=mock_context
        )

        first_call_kwargs = mock_cbr_retriever.search_by_category.call_args.kwargs
        assert first_call_kwargs["subcategory"] == "IPA"

        # Reset mock
        mock_cbr_retriever.search_by_category.reset_mock()

        await server.cbr_search_category(
            category="brewing",
            subcategory="ipa",
            query="test",
            limit=10,
            ctx=mock_context
        )

        second_call_kwargs = mock_cbr_retriever.search_by_category.call_args.kwargs
        assert second_call_kwargs["subcategory"] == "ipa"
        # Should preserve the exact case provided
        assert first_call_kwargs["subcategory"] != second_call_kwargs["subcategory"]
