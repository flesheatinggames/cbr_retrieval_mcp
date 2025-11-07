"""
Comprehensive backward compatibility test suite for cbr_retrieve MCP tool.

This test suite verifies that the cbr_retrieve MCP tool remains completely unchanged
during the subcategory parameter enhancement work (Task 6.2). These tests ensure:

1. cbr_retrieve tool signature has NOT changed
2. cbr_retrieve does NOT accept any new parameters (no subcategory parameter)
3. cbr_retrieve continues to work exactly as before
4. All existing cbr_retrieve parameters still work correctly
5. cbr_retrieve response format is unchanged
6. cbr_retrieve error handling is unchanged

CRITICAL: These tests should FAIL if cbr_retrieve is modified in any way.
SUCCESS = All tests pass, confirming cbr_retrieve is untouched.
"""

import asyncio
import inspect
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest


# Create a custom mock Context class for testing
class MockContext:
    """Mock Context class for testing that doesn't require request context."""

    def __init__(self):
        self.session = Mock()
        # Create async mock methods that return awaitables
        self.debug = AsyncMock(return_value=None)
        self.info = AsyncMock(return_value=None)
        self.warning = AsyncMock(return_value=None)
        self.error = AsyncMock(return_value=None)
        self.request_context = Mock()  # Add request_context to avoid errors


# Import the actual classes
try:
    from cbr_mcp_server import CBRMCPServer, ProductionCBRRetriever
    from retriever import CBRRetriever

    # Always use our MockContext instead of the real one for tests
    Context = MockContext

except ImportError as e:
    print(f"Import error in backward compatibility tests: {e}")

    # Create minimal mocks for testing
    class CBRMCPServer:
        pass

    class ProductionCBRRetriever:
        pass

    Context = MockContext


@pytest.fixture
def mock_server_config():
    """Fixture providing minimal mock server configuration."""
    config = Mock()
    config.database_path = "./test_db"
    config.db_path = "./test_db"  # startup_configuration_validator uses db_path
    config.collection_name = "test_collection"
    config.embedding_model = "nomic-ai/nomic-embed-text-v1.5"
    config.max_results_default = 5
    config.similarity_threshold_default = 0.8
    config.cache_enabled = True
    config.retry_enabled = True
    config.rate_limit_enabled = False
    config.require_auth = False
    config.use_real_db = False
    config.log_level = "INFO"
    config.max_query_length = 10000
    config.input_validation = "permissive"
    config.sanitization = True
    config.api_keys = []
    config.admin_keys = []
    return config


@pytest.fixture
def mock_production_retriever():
    """Fixture providing a mock ProductionCBRRetriever."""
    retriever = Mock(spec=ProductionCBRRetriever)
    retriever.db_path = "./test_db"
    retriever.collection_name = "test_collection"
    retriever.embedding_model_name = "nomic-ai/nomic-embed-text-v1.5"

    # Mock the retrieve_relevant_examples method - return actual data, not a coroutine
    retriever.retrieve_relevant_examples = AsyncMock(
        return_value=[
            {
                "id": "example1",
                "problem": "Sample problem",
                "solution": "Sample solution",
                "metadata": {"source": "test"},
            }
        ]
    )

    return retriever


@pytest.fixture
async def mock_cbr_server(mock_server_config, mock_production_retriever):
    """Fixture providing a mock CBR MCP Server with minimal setup."""
    with patch("cbr_mcp_server.ProductionCBRRetriever") as MockRetriever:
        MockRetriever.return_value = mock_production_retriever

        with patch(
            "cbr_mcp_server.server.startup_configuration_validator"
        ) as mock_validator:
            mock_validator.return_value = True

            with patch("cbr_mcp_server.LogConfig"):
                with patch("cbr_mcp_server.LoggerManager"):
                    with patch("cbr_mcp_server.StructuredLogger"):
                        server = CBRMCPServer(config=mock_server_config)

                        # Mock middleware components
                        server.input_validator = Mock()
                        server.input_validator.validate_input_size = AsyncMock()
                        server.input_validator.detect_injection = AsyncMock()
                        server.input_validator.validate_parameters = AsyncMock(
                            side_effect=lambda params: params
                        )

                        server.cache_manager = Mock()
                        server.cache_manager.generate_cache_key = Mock(
                            return_value="test_cache_key"
                        )
                        server.cache_manager.get_cache = AsyncMock(return_value=None)
                        server.cache_manager.set_cache = AsyncMock()

                        server.health_monitor = Mock()
                        server.health_monitor.metrics = Mock()
                        server.health_monitor.metrics.cache_hits = 0
                        server.health_monitor.metrics.cache_misses = 0

                        server.error_recovery = Mock()

                        # Create a proper circuit breaker mock that actually calls the function
                        async def mock_circuit_breaker_call(func, **kwargs):
                            # Actually call the function with the kwargs
                            return await func(**kwargs)

                        circuit_breaker = Mock()
                        circuit_breaker.call = AsyncMock(
                            side_effect=mock_circuit_breaker_call
                        )
                        server.error_recovery.get_circuit_breaker = Mock(
                            return_value=circuit_breaker
                        )
                        server.error_recovery.cbr_retrieve_degraded = AsyncMock(
                            return_value={"examples": []}
                        )

                        server.retriever = mock_production_retriever
                        server.config = mock_server_config
                        server.logger = Mock()

                        yield server


# ============================================================================
# TEST 1: cbr_retrieve Tool Signature Unchanged
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_retrieve_tool_signature_unchanged(mock_cbr_server):
    """
    Verify that the cbr_retrieve tool wrapper function signature has not changed.

    Expected signature:
        async def cbr_retrieve(
            query: str,
            max_results: int = 5,
            similarity_threshold: float = 0.8,
            ctx: Context = None
        ) -> Dict[str, Any]

    This test should FAIL if:
    - New parameters are added (e.g., subcategory)
    - Parameter types change
    - Default values change
    - Parameter order changes
    """
    # Get the cbr_retrieve method from the server instance
    cbr_retrieve_method = getattr(mock_cbr_server, "cbr_retrieve", None)
    assert cbr_retrieve_method is not None, "cbr_retrieve method not found on server"

    # Inspect the signature
    sig = inspect.signature(cbr_retrieve_method)
    params = sig.parameters

    # Verify exact parameter count (4 parameters - no self since it's a nested function)
    assert len(params) == 4, f"Expected 4 parameters, got {len(params)}"

    # Verify parameter names in correct order
    param_names = list(params.keys())
    assert param_names == [
        "query",
        "max_results",
        "similarity_threshold",
        "ctx",
    ], f"Parameter names don't match expected. Got: {param_names}"

    # Verify query parameter (required)
    query_param = params["query"]
    assert (
        query_param.default == inspect.Parameter.empty
    ), "query should not have a default value"
    assert (
        query_param.annotation == str
    ), f"query should be type str, got {query_param.annotation}"

    # Verify max_results parameter (optional with default=5)
    max_results_param = params["max_results"]
    assert (
        max_results_param.default == 5
    ), f"max_results default should be 5, got {max_results_param.default}"
    assert (
        max_results_param.annotation == int
    ), f"max_results should be type int, got {max_results_param.annotation}"

    # Verify similarity_threshold parameter (optional with default=0.8)
    similarity_threshold_param = params["similarity_threshold"]
    assert (
        similarity_threshold_param.default == 0.8
    ), f"similarity_threshold default should be 0.8, got {similarity_threshold_param.default}"
    assert (
        similarity_threshold_param.annotation == float
    ), f"similarity_threshold should be type float, got {similarity_threshold_param.annotation}"

    # Verify ctx parameter (optional, no specific default required)
    ctx_param = params["ctx"]
    # ctx can be None or have a different default, but must exist
    assert "ctx" in params, "ctx parameter is missing"

    # Verify NO subcategory parameter exists
    assert (
        "subcategory" not in params
    ), "FAILURE: subcategory parameter found in cbr_retrieve! This violates backward compatibility."

    # Verify return type annotation
    return_annotation = sig.return_annotation
    # Return type should be Dict[str, Any] or similar
    assert (
        return_annotation != inspect.Signature.empty
    ), "cbr_retrieve should have return type annotation"


# ============================================================================
# TEST 2: cbr_retrieve Implementation Signature Unchanged
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_retrieve_implementation_signature_unchanged(mock_cbr_server):
    """
    Verify the cbr_retrieve implementation method signature remains unchanged.

    The implementation may have an internal 'limit' parameter for legacy compatibility,
    but should NOT have a subcategory parameter or other new public parameters.
    """
    cbr_retrieve_method = mock_cbr_server.cbr_retrieve
    sig = inspect.signature(cbr_retrieve_method)
    params = sig.parameters

    # Core parameters must exist
    assert "query" in params, "query parameter missing from implementation"
    assert "max_results" in params, "max_results parameter missing from implementation"
    assert (
        "similarity_threshold" in params
    ), "similarity_threshold parameter missing from implementation"
    assert "ctx" in params, "ctx parameter missing from implementation"

    # CRITICAL: subcategory should NOT exist
    assert (
        "subcategory" not in params
    ), "FAILURE: subcategory parameter found in cbr_retrieve implementation! Backward compatibility broken."

    # Note: 'limit' parameter may exist as an internal alias for max_results (legacy compatibility)
    # This is acceptable as long as it's not exposed through the tool interface


# ============================================================================
# TEST 3: cbr_retrieve Rejects Unknown Parameters
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_retrieve_rejects_unknown_parameters(mock_cbr_server):
    """
    Verify that cbr_retrieve does NOT accept new parameters like subcategory.

    This test ensures the tool maintains its original interface and rejects
    any attempts to add new functionality through parameters.
    """
    # Attempt to call with subcategory parameter should fail
    with pytest.raises(TypeError) as exc_info:
        await mock_cbr_server.cbr_retrieve(
            query="test query",
            max_results=5,
            similarity_threshold=0.8,
            subcategory="remediation",  # This should be rejected
        )

    assert (
        "subcategory" in str(exc_info.value)
        or "unexpected" in str(exc_info.value).lower()
    ), f"Error message should indicate unexpected parameter. Got: {exc_info.value}"

    # Attempt to call with other unknown parameter should also fail
    with pytest.raises(TypeError) as exc_info:
        await mock_cbr_server.cbr_retrieve(
            query="test query", category="orchestration"  # This should also be rejected
        )

    assert (
        "category" in str(exc_info.value) or "unexpected" in str(exc_info.value).lower()
    ), f"Error message should indicate unexpected parameter. Got: {exc_info.value}"


# ============================================================================
# TEST 4: cbr_retrieve Required Parameter Validation
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_retrieve_required_parameter_validation(mock_cbr_server):
    """
    Verify that the query parameter is still required and validated correctly.

    This ensures the original validation logic remains unchanged.
    """
    # Test calling without query parameter should fail
    with pytest.raises(TypeError) as exc_info:
        await mock_cbr_server.cbr_retrieve()

    assert (
        "query" in str(exc_info.value).lower()
    ), f"Error should indicate missing query parameter. Got: {exc_info.value}"

    # Test calling with query=None should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        await mock_cbr_server.cbr_retrieve(query=None)

    assert "query is required" in str(
        exc_info.value
    ), f"Error message should indicate query is required. Got: {exc_info.value}"


# ============================================================================
# TEST 5: cbr_retrieve Optional Parameters Work Correctly
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_retrieve_optional_parameters_work_correctly(mock_cbr_server):
    """
    Verify that all existing optional parameters still work as expected.

    Tests:
    - max_results defaults to 5
    - max_results accepts custom values
    - similarity_threshold defaults to 0.8
    - similarity_threshold accepts custom values
    - ctx parameter works when provided
    - ctx parameter works when omitted
    """
    # Test with defaults (should use max_results=5, similarity_threshold=0.8)
    result = await mock_cbr_server.cbr_retrieve(query="test query")

    assert result is not None, "cbr_retrieve should return a result"
    assert isinstance(result, dict), "Result should be a dictionary"

    # Verify the retriever was called with default values
    mock_cbr_server.retriever.retrieve_relevant_examples.assert_called()
    call_kwargs = mock_cbr_server.retriever.retrieve_relevant_examples.call_args.kwargs
    assert call_kwargs.get("max_results") == 5, "Default max_results should be 5"
    assert (
        call_kwargs.get("similarity_threshold") == 0.8
    ), "Default similarity_threshold should be 0.8"

    # Reset mock
    mock_cbr_server.retriever.retrieve_relevant_examples.reset_mock()

    # Test with custom max_results
    result = await mock_cbr_server.cbr_retrieve(query="test query", max_results=10)

    call_kwargs = mock_cbr_server.retriever.retrieve_relevant_examples.call_args.kwargs
    assert (
        call_kwargs.get("max_results") == 10
    ), "Custom max_results should be passed through"

    # Reset mock
    mock_cbr_server.retriever.retrieve_relevant_examples.reset_mock()

    # Test with custom similarity_threshold
    result = await mock_cbr_server.cbr_retrieve(
        query="test query", similarity_threshold=0.9
    )

    call_kwargs = mock_cbr_server.retriever.retrieve_relevant_examples.call_args.kwargs
    assert (
        call_kwargs.get("similarity_threshold") == 0.9
    ), "Custom similarity_threshold should be passed through"

    # Reset mock
    mock_cbr_server.retriever.retrieve_relevant_examples.reset_mock()

    # Test with ctx parameter
    mock_ctx = Context()
    result = await mock_cbr_server.cbr_retrieve(query="test query", ctx=mock_ctx)

    # Verify ctx was used (should have called ctx.info at some point)
    assert mock_ctx.info.called, "ctx.info should be called when ctx is provided"

    # Test without ctx parameter (should not raise error)
    result = await mock_cbr_server.cbr_retrieve(query="test query")
    assert result is not None, "cbr_retrieve should work without ctx parameter"


# ============================================================================
# TEST 6: cbr_retrieve Response Format Unchanged
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_retrieve_response_format_unchanged(mock_cbr_server):
    """
    Verify that the response structure from cbr_retrieve is exactly the same.

    Expected format:
    {
        "examples": [
            {
                "id": str,
                "problem": str,
                "solution": str,
                "metadata": dict
            }
        ]
    }

    This test should FAIL if:
    - Response structure changes
    - New fields are added to the response
    - "examples" key is renamed or removed
    """
    result = await mock_cbr_server.cbr_retrieve(query="test query")

    # Verify response is a dictionary
    assert isinstance(result, dict), "Response should be a dictionary"

    # Verify response has exactly one key: "examples"
    assert "examples" in result, "Response must contain 'examples' key"
    assert (
        len(result.keys()) == 1
    ), f"Response should have exactly 1 key ('examples'), got {len(result.keys())}: {list(result.keys())}"

    # Verify examples is a list
    assert isinstance(result["examples"], list), "examples should be a list"

    # Verify no new fields were added
    assert "category" not in result, "Response should not contain 'category' field"
    assert (
        "subcategory" not in result
    ), "Response should not contain 'subcategory' field"
    assert "categories" not in result, "Response should not contain 'categories' field"

    # If there are examples, verify their structure hasn't changed
    if len(result["examples"]) > 0:
        example = result["examples"][0]
        assert isinstance(example, dict), "Each example should be a dictionary"
        assert "id" in example, "Example should have 'id' field"
        assert "problem" in example, "Example should have 'problem' field"
        assert "solution" in example, "Example should have 'solution' field"


# ============================================================================
# TEST 7: cbr_retrieve Functionality Unchanged
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_retrieve_functionality_unchanged(mock_cbr_server):
    """
    Verify that cbr_retrieve still performs its original function correctly.

    This test ensures:
    - Query is passed to retriever correctly
    - max_results is passed correctly
    - similarity_threshold is passed correctly
    - Examples are returned in expected format
    - Caching behavior is unchanged
    - Middleware execution is unchanged
    """
    query_text = "test query for functionality"
    max_results_val = 7
    similarity_threshold_val = 0.85

    # Call cbr_retrieve
    result = await mock_cbr_server.cbr_retrieve(
        query=query_text,
        max_results=max_results_val,
        similarity_threshold=similarity_threshold_val,
    )

    # Verify input validation was called
    mock_cbr_server.input_validator.validate_input_size.assert_called_with(query_text)
    mock_cbr_server.input_validator.detect_injection.assert_called_with(query_text)

    # Verify parameter validation was called
    mock_cbr_server.input_validator.validate_parameters.assert_called_once()
    validate_params_call = (
        mock_cbr_server.input_validator.validate_parameters.call_args[0][0]
    )
    assert validate_params_call["query"] == query_text
    assert validate_params_call["max_results"] == max_results_val
    assert validate_params_call["similarity_threshold"] == similarity_threshold_val

    # Verify cache was checked
    mock_cbr_server.cache_manager.generate_cache_key.assert_called()
    mock_cbr_server.cache_manager.get_cache.assert_called()

    # Verify retriever was called with correct parameters
    mock_cbr_server.retriever.retrieve_relevant_examples.assert_called()
    call_kwargs = mock_cbr_server.retriever.retrieve_relevant_examples.call_args.kwargs
    assert call_kwargs["query"] == query_text
    assert call_kwargs["max_results"] == max_results_val
    assert call_kwargs["similarity_threshold"] == similarity_threshold_val

    # Verify result was cached
    mock_cbr_server.cache_manager.set_cache.assert_called()

    # Verify result structure
    assert "examples" in result
    assert isinstance(result["examples"], list)


# ============================================================================
# TEST 8: cbr_retrieve Error Handling Unchanged
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_retrieve_error_handling_unchanged(mock_cbr_server):
    """
    Verify that error handling in cbr_retrieve remains exactly the same.

    Tests:
    - Database errors are handled correctly
    - Degraded mode fallback works
    - Error messages have the same format
    - Circuit breaker behavior is unchanged
    """
    # Configure retriever to raise an exception
    mock_cbr_server.retriever.retrieve_relevant_examples = AsyncMock(
        side_effect=Exception("Database connection failed")
    )

    # Configure degraded mode response
    mock_cbr_server.error_recovery.cbr_retrieve_degraded = AsyncMock(
        return_value={"examples": []}
    )

    # Call cbr_retrieve (should trigger error handling)
    result = await mock_cbr_server.cbr_retrieve(query="test query")

    # Verify degraded mode was called
    mock_cbr_server.error_recovery.cbr_retrieve_degraded.assert_called_once()

    # Verify degraded mode response format
    assert (
        "examples" in result
    ), "Degraded mode response should still have 'examples' key"
    assert isinstance(
        result["examples"], list
    ), "Degraded mode examples should be a list"

    # Test with retry disabled (should raise exception)
    mock_cbr_server.config.retry_enabled = False
    mock_cbr_server.retriever.retrieve_relevant_examples = AsyncMock(
        side_effect=Exception("Database connection failed")
    )

    with pytest.raises(Exception) as exc_info:
        await mock_cbr_server.cbr_retrieve(query="test query")

    # Verify error message format is unchanged
    assert "Failed to retrieve examples" in str(
        exc_info.value
    ), f"Error message format should be unchanged. Got: {exc_info.value}"


# ============================================================================
# TEST 9: cbr_retrieve Does Not Call Category Methods
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_retrieve_does_not_call_category_methods(mock_cbr_server):
    """
    Verify that cbr_retrieve does not interact with new category-related functionality.

    This ensures complete isolation from the subcategory enhancement work.

    Tests that the following methods are NEVER called by cbr_retrieve:
    - search_by_category
    - get_categories

    Only retrieve_relevant_examples should be called (existing method).
    """
    # Add spy methods to track calls
    if hasattr(mock_cbr_server.retriever, "search_by_category"):
        mock_cbr_server.retriever.search_by_category = AsyncMock()

    if hasattr(mock_cbr_server.retriever, "get_categories"):
        mock_cbr_server.retriever.get_categories = AsyncMock()

    # Call cbr_retrieve
    result = await mock_cbr_server.cbr_retrieve(query="test query")

    # Verify retrieve_relevant_examples WAS called (original behavior)
    assert (
        mock_cbr_server.retriever.retrieve_relevant_examples.called
    ), "retrieve_relevant_examples should be called"

    # Verify search_by_category was NOT called
    if hasattr(mock_cbr_server.retriever, "search_by_category"):
        assert (
            not mock_cbr_server.retriever.search_by_category.called
        ), "FAILURE: search_by_category should NOT be called by cbr_retrieve"

    # Verify get_categories was NOT called
    if hasattr(mock_cbr_server.retriever, "get_categories"):
        assert (
            not mock_cbr_server.retriever.get_categories.called
        ), "FAILURE: get_categories should NOT be called by cbr_retrieve"


# ============================================================================
# TEST 10: cbr_retrieve Integration with Existing Tests
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_retrieve_integration_with_existing_tests(mock_cbr_server):
    """
    Verify that cbr_retrieve still passes all original test scenarios.

    This test runs a series of common scenarios that should continue to work:
    - Empty query handling
    - Very large max_results
    - Edge case similarity thresholds
    - Multiple sequential calls
    """
    # Scenario 1: Empty query (should still validate and process)
    with pytest.raises(ValueError) as exc_info:
        await mock_cbr_server.cbr_retrieve(query=None)
    assert "query is required" in str(exc_info.value)

    # Scenario 2: Very large max_results (should be accepted)
    result = await mock_cbr_server.cbr_retrieve(query="test", max_results=1000)
    assert "examples" in result

    # Scenario 3: Edge case similarity thresholds
    result = await mock_cbr_server.cbr_retrieve(
        query="test", similarity_threshold=0.0  # Minimum
    )
    assert "examples" in result

    result = await mock_cbr_server.cbr_retrieve(
        query="test", similarity_threshold=1.0  # Maximum
    )
    assert "examples" in result

    # Scenario 4: Multiple sequential calls (verify consistency)
    results = []
    for i in range(3):
        result = await mock_cbr_server.cbr_retrieve(query=f"test query {i}")
        results.append(result)
        assert "examples" in result
        assert isinstance(result["examples"], list)

    # All results should have the same structure
    for result in results:
        assert set(result.keys()) == {
            "examples"
        }, "All results should have identical structure"


# ============================================================================
# TEST 11: cbr_retrieve Tool Wrapper in MCP Setup
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_retrieve_tool_wrapper_unchanged():
    """
    Verify that the tool wrapper function registered with MCP has not changed.

    This test inspects the actual tool registration to ensure the wrapper
    function maintains backward compatibility.
    """
    # This test verifies the tool wrapper signature at the MCP registration level
    # Create a minimal server instance to inspect tool registration
    config = Mock()
    config.database_path = "./test_db"
    config.db_path = "./test_db"  # startup_configuration_validator uses db_path
    config.collection_name = "test_collection"
    config.use_real_db = False
    config.api_keys = []  # Must be iterable for AuthenticationManager
    config.admin_keys = []
    config.log_level = "INFO"
    config.cache_enabled = False
    config.retry_enabled = False

    with patch("cbr_mcp_server.ProductionCBRRetriever"):
        with patch(
            "cbr_mcp_server.server.startup_configuration_validator"
        ) as mock_validator:
            mock_validator.return_value = True

            with patch("cbr_mcp_server.LogConfig"):
                with patch("cbr_mcp_server.LoggerManager"):
                    with patch("cbr_mcp_server.StructuredLogger"):
                        server = CBRMCPServer(config=config)

                        # The tool wrapper should be defined in _setup_tools
                        # Verify it exists and has the correct signature
                        assert hasattr(
                            server, "cbr_retrieve"
                        ), "cbr_retrieve method must exist on server"

                        cbr_retrieve_method = server.cbr_retrieve
                        sig = inspect.signature(cbr_retrieve_method)
                        params = list(sig.parameters.keys())

                        # Verify the wrapper maintains original parameters (no self - it's a nested function)
                        expected_params = [
                            "query",
                            "max_results",
                            "similarity_threshold",
                            "ctx",
                        ]
                        assert (
                            params == expected_params
                        ), f"Tool wrapper parameters changed! Expected {expected_params}, got {params}"

                        # Verify NO subcategory parameter in wrapper
                        assert (
                            "subcategory" not in params
                        ), "CRITICAL FAILURE: subcategory parameter found in tool wrapper!"


# ============================================================================
# SUMMARY TEST: Complete Backward Compatibility Verification
# ============================================================================


@pytest.mark.asyncio
async def test_complete_backward_compatibility_summary(mock_cbr_server):
    """
    Comprehensive verification that cbr_retrieve maintains complete backward compatibility.

    This test performs a full end-to-end verification that cbr_retrieve:
    1. Has unchanged signature
    2. Rejects new parameters
    3. Works with all original parameters
    4. Returns unchanged response format
    5. Maintains original error handling
    6. Does not interact with new category functionality

    SUCCESS = cbr_retrieve is completely untouched by subcategory enhancement
    FAILURE = cbr_retrieve has been modified (violates Task 6.2 requirements)
    """
    # 1. Signature verification
    sig = inspect.signature(mock_cbr_server.cbr_retrieve)
    params = list(sig.parameters.keys())
    assert "subcategory" not in params, "Signature must not include subcategory"
    assert "category" not in params, "Signature must not include category"

    # 2. Reject new parameters
    with pytest.raises(TypeError):
        await mock_cbr_server.cbr_retrieve(query="test", subcategory="remediation")

    # 3. Original parameters work
    result = await mock_cbr_server.cbr_retrieve(
        query="test", max_results=10, similarity_threshold=0.9
    )
    assert result is not None

    # 4. Response format unchanged
    assert "examples" in result
    assert len(result.keys()) == 1, "Response should only have 'examples' key"
    assert "category" not in result, "Response must not include category"
    assert "subcategory" not in result, "Response must not include subcategory"

    # 5. Error handling unchanged
    mock_cbr_server.retriever.retrieve_relevant_examples = AsyncMock(
        side_effect=Exception("Test error")
    )

    # Should use degraded mode
    result = await mock_cbr_server.cbr_retrieve(query="test")
    assert "examples" in result, "Error handling should return same format"

    # 6. No interaction with category methods
    if hasattr(mock_cbr_server.retriever, "search_by_category"):
        mock_cbr_server.retriever.search_by_category = AsyncMock()
        result = await mock_cbr_server.cbr_retrieve(query="test")
        assert (
            not mock_cbr_server.retriever.search_by_category.called
        ), "cbr_retrieve must not call search_by_category"

    # If we reach here, complete backward compatibility is verified
    print("\n✅ COMPLETE BACKWARD COMPATIBILITY VERIFIED ✅")
    print("cbr_retrieve remains completely unchanged during subcategory enhancement.")
