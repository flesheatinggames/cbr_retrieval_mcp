"""
Comprehensive tests for Error Recovery System components.

This test suite covers the missing error recovery components:
- RetryManager: Configurable retry policies with exponential backoff
- ErrorClassifier: Error categorization and severity determination
- FallbackHandler: Graceful degradation strategies
- ChromaDB reconnection integration
- Embedding model reinitialization

These tests are designed to fail initially since the implementations don't exist yet.
This follows TDD Red phase - write failing tests first, then implement to make them pass.
"""

import asyncio
import threading
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import chromadb
import pytest
from sentence_transformers import SentenceTransformer

# Import CBRMCPServer for integration tests
try:
    from cbr_mcp_server import CBRMCPServer
except ImportError:
    # Fallback mock for test environment
    CBRMCPServer = Mock


class ErrorType(Enum):
    """Error type classifications for testing."""

    CONNECTION_ERROR = "connection"
    TIMEOUT_ERROR = "timeout"
    AUTH_ERROR = "authentication"
    RESOURCE_ERROR = "resource"
    UNKNOWN_ERROR = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels for testing."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RetryPolicy:
    """Mock retry policy for testing."""

    def __init__(
        self,
        max_attempts: int,
        base_delay: float,
        max_delay: float,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


# Import the implemented classes from cbr_mcp_server
try:
    from cbr_mcp_server import (
        ErrorClassifier,
    )
    from cbr_mcp_server import ErrorSeverity as CBRErrorSeverity
    from cbr_mcp_server import ErrorType as CBRErrorType
    from cbr_mcp_server import (
        FallbackHandler,
        RetryManager,
    )

    # Use CBR implementations for the enums to avoid conflicts
    ErrorType = CBRErrorType
    ErrorSeverity = CBRErrorSeverity
except ImportError:
    # Fallback to local definitions if import fails
    class RetryManager:
        """Fallback implementation - tests will fail."""

        pass

    class ErrorClassifier:
        """Fallback implementation - tests will fail."""

        pass

    class FallbackHandler:
        """Fallback implementation - tests will fail."""

        pass


class TestRetryManager:
    """Test suite for RetryManager component."""

    def test_retry_policy_configuration(self):
        """Test that retry policies are configured with correct parameters."""
        # This will fail - RetryManager doesn't exist yet
        retry_manager = RetryManager()

        policy = RetryPolicy(
            max_attempts=5,
            base_delay=1.0,
            max_delay=60.0,
            exponential_base=2.0,
            jitter=True,
        )

        retry_manager.configure_policy(policy)

        assert retry_manager.policy.max_attempts == 5
        assert retry_manager.policy.base_delay == 1.0
        assert retry_manager.policy.max_delay == 60.0
        assert retry_manager.policy.exponential_base == 2.0
        assert retry_manager.policy.jitter is True

    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation with jitter."""
        retry_manager = RetryManager()
        policy = RetryPolicy(
            max_attempts=5, base_delay=1.0, max_delay=60.0, jitter=True
        )
        retry_manager.configure_policy(policy)

        # First attempt should be base delay
        delay1 = retry_manager.calculate_delay(1)
        assert 1.0 <= delay1 <= 2.0  # With jitter

        # Second attempt should be ~2x base delay
        delay2 = retry_manager.calculate_delay(2)
        assert 2.0 <= delay2 <= 4.0

        # Third attempt should be ~4x base delay
        delay3 = retry_manager.calculate_delay(3)
        assert 4.0 <= delay3 <= 8.0

        # Should not exceed max_delay
        delay_high = retry_manager.calculate_delay(10)
        assert delay_high <= 60.0

    def test_max_attempts_enforcement(self):
        """Test that retry stops after configured max attempts."""
        retry_manager = RetryManager()
        policy = RetryPolicy(max_attempts=3, base_delay=0.1, max_delay=1.0)
        retry_manager.configure_policy(policy)

        mock_operation = Mock(side_effect=Exception("Always fails"))

        with pytest.raises(Exception) as exc_info:
            retry_manager.execute_with_retry(mock_operation)

        # Should have attempted exactly 3 times
        assert mock_operation.call_count == 3
        assert "Max retry attempts exceeded" in str(exc_info.value)

    def test_successful_retry_scenario(self):
        """Test operation that fails then succeeds on retry."""
        retry_manager = RetryManager()
        policy = RetryPolicy(max_attempts=3, base_delay=0.1, max_delay=1.0)
        retry_manager.configure_policy(policy)

        # Fail twice, succeed on third attempt
        mock_operation = Mock(
            side_effect=[Exception("Fail 1"), Exception("Fail 2"), "Success"]
        )

        result = retry_manager.execute_with_retry(mock_operation)

        assert result == "Success"
        assert mock_operation.call_count == 3

    def test_retry_exhaustion_scenario(self):
        """Test behavior when all retry attempts are exhausted."""
        retry_manager = RetryManager()
        policy = RetryPolicy(max_attempts=2, base_delay=0.1, max_delay=1.0)
        retry_manager.configure_policy(policy)

        mock_operation = Mock(side_effect=ConnectionError("Connection failed"))

        with pytest.raises(ConnectionError):
            retry_manager.execute_with_retry(mock_operation)

        assert mock_operation.call_count == 2

    def test_different_error_types_handling(self):
        """Test that some errors are retryable while others are not."""
        retry_manager = RetryManager()
        policy = RetryPolicy(max_attempts=3, base_delay=0.1, max_delay=1.0)
        retry_manager.configure_policy(policy)

        # Connection errors should be retryable
        mock_retryable = Mock(side_effect=ConnectionError("Retryable"))
        with pytest.raises(ConnectionError):
            retry_manager.execute_with_retry(mock_retryable)
        assert mock_retryable.call_count == 3

        # Authentication errors should not be retryable
        mock_non_retryable = Mock(side_effect=PermissionError("Auth failed"))
        with pytest.raises(PermissionError):
            retry_manager.execute_with_retry(mock_non_retryable)
        assert mock_non_retryable.call_count == 1  # No retries for auth errors

    @pytest.mark.asyncio
    async def test_async_operation_retries(self):
        """Test retry behavior with async operations."""
        retry_manager = RetryManager()
        policy = RetryPolicy(max_attempts=3, base_delay=0.1, max_delay=1.0)
        retry_manager.configure_policy(policy)

        # Async operation that fails twice then succeeds
        async def mock_async_op():
            mock_async_op.call_count += 1
            if mock_async_op.call_count <= 2:
                raise ConnectionError("Async fail")
            return "Async success"

        mock_async_op.call_count = 0

        result = await retry_manager.execute_with_retry_async(mock_async_op)

        assert result == "Async success"
        assert mock_async_op.call_count == 3


class TestErrorClassifier:
    """Test suite for ErrorClassifier component."""

    def test_connection_error_classification(self):
        """Test classification of connection-related errors."""
        # This will fail - ErrorClassifier doesn't exist yet
        classifier = ErrorClassifier()

        connection_errors = [
            ConnectionError("Connection refused"),
            ConnectionRefusedError("Port not open"),
            ConnectionAbortedError("Connection aborted"),
            OSError("Network unreachable"),
        ]

        for error in connection_errors:
            error_type = classifier.classify_error(error)
            assert error_type == ErrorType.CONNECTION_ERROR

    def test_timeout_error_classification(self):
        """Test classification of timeout-related errors."""
        classifier = ErrorClassifier()

        timeout_errors = [
            TimeoutError("Operation timed out"),
            asyncio.TimeoutError("Async timeout"),
            Exception("timeout"),  # String-based detection
        ]

        for error in timeout_errors:
            error_type = classifier.classify_error(error)
            assert error_type == ErrorType.TIMEOUT_ERROR

    def test_authentication_error_classification(self):
        """Test classification of authentication-related errors."""
        classifier = ErrorClassifier()

        auth_errors = [
            PermissionError("Access denied"),
            Exception("Unauthorized"),
            Exception("Authentication failed"),
            Exception("Invalid credentials"),
        ]

        for error in auth_errors:
            error_type = classifier.classify_error(error)
            assert error_type == ErrorType.AUTH_ERROR

    def test_memory_error_classification(self):
        """Test classification of resource/memory-related errors."""
        classifier = ErrorClassifier()

        resource_errors = [
            MemoryError("Out of memory"),
            OSError("No space left on device"),
            Exception("CUDA out of memory"),
            Exception("Resource exhausted"),
        ]

        for error in resource_errors:
            error_type = classifier.classify_error(error)
            assert error_type == ErrorType.RESOURCE_ERROR

    def test_unknown_error_classification(self):
        """Test classification of unknown/generic errors."""
        classifier = ErrorClassifier()

        unknown_errors = [
            ValueError("Invalid value"),
            TypeError("Wrong type"),
            Exception("Some random error"),
        ]

        for error in unknown_errors:
            error_type = classifier.classify_error(error)
            assert error_type == ErrorType.UNKNOWN_ERROR

    def test_error_severity_determination(self):
        """Test determination of error severity levels."""
        classifier = ErrorClassifier()

        # Critical errors
        critical_errors = [MemoryError("OOM"), SystemError("System failure")]
        for error in critical_errors:
            severity = classifier.determine_severity(error)
            assert severity == ErrorSeverity.CRITICAL

        # High severity errors
        high_errors = [ConnectionError("Database down"), PermissionError("Auth failed")]
        for error in high_errors:
            severity = classifier.determine_severity(error)
            assert severity == ErrorSeverity.HIGH

        # Medium severity errors
        medium_errors = [TimeoutError("Request timeout"), OSError("Resource busy")]
        for error in medium_errors:
            severity = classifier.determine_severity(error)
            assert severity == ErrorSeverity.MEDIUM

        # Low severity errors
        low_errors = [ValueError("Bad input"), TypeError("Type mismatch")]
        for error in low_errors:
            severity = classifier.determine_severity(error)
            assert severity == ErrorSeverity.LOW

    def test_retryable_error_determination(self):
        """Test determination of which errors should be retried."""
        classifier = ErrorClassifier()

        # Retryable errors
        retryable_errors = [
            ConnectionError("Network issue"),
            TimeoutError("Timeout"),
            OSError("Resource temporarily unavailable"),
        ]
        for error in retryable_errors:
            assert classifier.is_retryable(error) is True

        # Non-retryable errors
        non_retryable_errors = [
            PermissionError("Access denied"),
            ValueError("Invalid input"),
            TypeError("Wrong type"),
        ]
        for error in non_retryable_errors:
            assert classifier.is_retryable(error) is False

    def test_error_metadata_extraction(self):
        """Test extraction of metadata from errors."""
        classifier = ErrorClassifier()

        error = ConnectionError("Connection to localhost:8080 failed after 30s")
        metadata = classifier.extract_metadata(error)

        assert metadata["error_type"] == ErrorType.CONNECTION_ERROR
        assert metadata["severity"] == ErrorSeverity.HIGH
        assert metadata["retryable"] is True
        assert "localhost:8080" in metadata["details"]
        assert "30s" in metadata["details"]


class TestFallbackHandler:
    """Test suite for FallbackHandler component."""

    def test_fallback_strategy_registration(self):
        """Test registration of fallback strategies by error type."""
        # This will fail - FallbackHandler doesn't exist yet
        fallback_handler = FallbackHandler()

        mock_strategy = Mock()
        fallback_handler.register_strategy(ErrorType.CONNECTION_ERROR, mock_strategy)

        registered_strategy = fallback_handler.get_strategy(ErrorType.CONNECTION_ERROR)
        assert registered_strategy == mock_strategy

    def test_fallback_execution(self):
        """Test execution of fallback when primary operation fails."""
        fallback_handler = FallbackHandler()

        # Primary operation that fails
        mock_primary = Mock(side_effect=ConnectionError("Primary failed"))

        # Fallback strategy that succeeds
        mock_fallback = Mock(return_value="Fallback result")
        fallback_handler.register_strategy(ErrorType.CONNECTION_ERROR, mock_fallback)

        result = fallback_handler.execute_with_fallback(mock_primary)

        assert result == "Fallback result"
        assert mock_primary.call_count == 1
        assert mock_fallback.call_count == 1

    def test_fallback_chaining(self):
        """Test multiple levels of fallback strategies."""
        fallback_handler = FallbackHandler()

        # Chain of fallbacks: primary -> fallback1 -> fallback2 -> success
        mock_primary = Mock(side_effect=ConnectionError("Primary failed"))
        mock_fallback1 = Mock(side_effect=TimeoutError("Fallback1 failed"))
        mock_fallback2 = Mock(return_value="Fallback2 success")

        fallback_handler.register_strategy_chain(
            ErrorType.CONNECTION_ERROR, [mock_fallback1, mock_fallback2]
        )

        result = fallback_handler.execute_with_fallback(mock_primary)

        assert result == "Fallback2 success"
        assert mock_primary.call_count == 1
        assert mock_fallback1.call_count == 1
        assert mock_fallback2.call_count == 1

    def test_graceful_degradation(self):
        """Test graceful degradation when service is unavailable."""
        fallback_handler = FallbackHandler()

        # Service unavailable
        mock_service = Mock(side_effect=ConnectionError("Service down"))

        # Degraded response strategy
        def degraded_response(*args, **kwargs):
            return {
                "status": "degraded",
                "message": "Service temporarily unavailable",
                "limited_results": [],
            }

        fallback_handler.register_strategy(
            ErrorType.CONNECTION_ERROR, degraded_response
        )

        result = fallback_handler.execute_with_fallback(mock_service)

        assert result["status"] == "degraded"
        assert "unavailable" in result["message"]
        assert "limited_results" in result

    def test_fallback_failure_handling(self):
        """Test behavior when all fallbacks fail."""
        fallback_handler = FallbackHandler()

        # All operations fail
        mock_primary = Mock(side_effect=ConnectionError("Primary failed"))
        mock_fallback1 = Mock(side_effect=TimeoutError("Fallback1 failed"))
        mock_fallback2 = Mock(side_effect=OSError("Fallback2 failed"))

        fallback_handler.register_strategy_chain(
            ErrorType.CONNECTION_ERROR, [mock_fallback1, mock_fallback2]
        )

        with pytest.raises(Exception) as exc_info:
            fallback_handler.execute_with_fallback(mock_primary)

        assert "All fallback strategies failed" in str(exc_info.value)

    @patch("builtins.open")
    @patch("json.load")
    def test_cached_response_fallback(self, mock_json_load, mock_open):
        """Test fallback to cached responses when service fails."""
        fallback_handler = FallbackHandler()

        # Service fails
        mock_service = Mock(side_effect=ConnectionError("Service down"))

        # Cached data available
        cached_data = {"results": ["cached_item1", "cached_item2"]}
        mock_json_load.return_value = cached_data

        def cache_fallback_strategy(*args, **kwargs):
            return fallback_handler.get_cached_response("cache_key")

        fallback_handler.register_strategy(
            ErrorType.CONNECTION_ERROR, cache_fallback_strategy
        )

        result = fallback_handler.execute_with_fallback(mock_service)

        assert result == cached_data
        assert mock_open.called

    def test_default_response_fallback(self):
        """Test fallback to default response when no cached data exists."""
        fallback_handler = FallbackHandler()

        # Service fails
        mock_service = Mock(side_effect=ConnectionError("Service down"))

        # No cached data, return defaults
        def default_response_strategy(*args, **kwargs):
            return {
                "results": [],
                "message": "No results available",
                "fallback_mode": True,
            }

        fallback_handler.register_strategy(
            ErrorType.CONNECTION_ERROR, default_response_strategy
        )

        result = fallback_handler.execute_with_fallback(mock_service)

        assert result["results"] == []
        assert result["fallback_mode"] is True
        assert "No results available" in result["message"]

    @pytest.mark.asyncio
    async def test_async_fallback_execution(self):
        """Test fallback execution with async operations."""
        fallback_handler = FallbackHandler()

        # Async primary operation that fails
        async def mock_async_primary():
            raise ConnectionError("Async primary failed")

        # Async fallback that succeeds
        async def mock_async_fallback():
            return "Async fallback success"

        fallback_handler.register_async_strategy(
            ErrorType.CONNECTION_ERROR, mock_async_fallback
        )

        result = await fallback_handler.execute_with_fallback_async(mock_async_primary)

        assert result == "Async fallback success"


class TestChromaDBReconnectionIntegration:
    """Test suite for ChromaDB reconnection integration."""

    @patch("chromadb.PersistentClient")
    def test_automatic_reconnection_on_connection_loss(self, mock_chroma_client):
        """Test automatic reconnection when ChromaDB connection is lost."""
        # This will fail - reconnection logic doesn't exist yet
        from cbr_mcp_server import CBRMCPServer, CBRServerConfig

        # Mock ChromaDB client that fails then succeeds on reconnection
        mock_client = Mock()
        mock_collection = Mock()

        # First call fails (connection lost)
        mock_collection.query.side_effect = [
            ConnectionError("Connection lost"),
            {
                "documents": [["result1"]],
                "metadatas": [[{}]],
            },  # Success after reconnect
        ]

        mock_client.get_collection.return_value = mock_collection
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client

        # Create config with real database enabled
        config = CBRServerConfig(use_real_db=True)
        server = CBRMCPServer(config=config)

        # This should trigger reconnection logic
        result = server.query_with_reconnection("test query")

        # Should have attempted reconnection
        assert mock_client.get_collection.call_count >= 2
        assert "result1" in str(result)

    @patch("chromadb.PersistentClient")
    def test_connection_pool_recovery(self, mock_chroma_client):
        """Test recovery when connection pool is exhausted."""
        from cbr_mcp_server import CBRMCPServer, CBRServerConfig

        # Mock connection pool exhaustion
        mock_client = Mock()
        mock_client.get_collection.side_effect = [
            OSError("Connection pool exhausted"),
            Mock(),  # New connection succeeds
        ]
        mock_client.get_or_create_collection.return_value = Mock()
        mock_chroma_client.return_value = mock_client

        # Create config with real database enabled
        config = CBRServerConfig(use_real_db=True)
        server = CBRMCPServer(config=config)

        # Should create new connection when pool exhausted
        result = server.ensure_connection_available()

        assert result is True
        assert mock_client.get_collection.call_count == 2

    @patch("chromadb.PersistentClient")
    @pytest.mark.asyncio
    async def test_query_retry_after_reconnection(self, mock_chroma_client):
        """Test that queries gracefully handle reconnection failures and provide fallback results."""
        from cbr_mcp_server import CBRMCPServer, CBRServerConfig

        mock_client = Mock()
        mock_collection = Mock()

        # Simulate connection failure - system should fall back gracefully
        mock_collection.query.side_effect = ConnectionError("Connection failed")
        mock_client.get_collection.return_value = mock_collection
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client

        # Create config with real database enabled
        config = CBRServerConfig(use_real_db=True)
        server = CBRMCPServer(config=config)

        # Should handle connection failure gracefully with fallback data
        result = await server.cbr_retrieve("test", max_results=1)

        # Validate that system provided fallback results despite connection failure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert len(result) > 0, "Result should not be empty"
        # System should provide mock data when connection fails
        assert "examples" in result, "Should return examples structure"

    @patch("chromadb.PersistentClient")
    @patch("threading.Timer")
    def test_persistent_connection_monitoring(self, mock_timer, mock_chroma_client):
        """Test persistent monitoring of connection health."""
        from cbr_mcp_server import CBRMCPServer, CBRServerConfig

        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = Mock()
        mock_chroma_client.return_value = mock_client

        # Create config with real database enabled
        config = CBRServerConfig(use_real_db=True)
        server = CBRMCPServer(config=config)
        server.start_connection_monitoring()

        # Should have started monitoring timer
        assert mock_timer.called
        monitor_call = mock_timer.call_args
        assert monitor_call[0][0] > 0  # Positive interval
        assert callable(monitor_call[0][1])  # Monitor function

    @patch("chromadb.PersistentClient")
    def test_connection_failure_escalation(self, mock_chroma_client):
        """Test escalation to circuit breaker on repeated connection failures."""
        from cbr_mcp_server import CBRMCPServer, CBRServerConfig

        # Mock repeated failures
        mock_client = Mock()
        mock_client.get_collection.side_effect = ConnectionError("Persistent failure")
        mock_client.get_or_create_collection.return_value = Mock()
        mock_chroma_client.return_value = mock_client

        # Create config with real database enabled
        config = CBRServerConfig(use_real_db=True)
        server = CBRMCPServer(config=config)

        # After multiple failures, should trigger circuit breaker
        with pytest.raises(Exception) as exc_info:
            for _ in range(10):  # Exceed failure threshold
                try:
                    server.query_with_reconnection("test")
                except:
                    pass
            server.query_with_reconnection("test")  # Should trigger circuit breaker

        assert "circuit breaker" in str(exc_info.value).lower()

    @patch("chromadb.PersistentClient")
    def test_concurrent_reconnection_handling(self, mock_chroma_client):
        """Test thread-safe reconnection when multiple threads lose connection."""
        import threading

        from cbr_mcp_server import CBRMCPServer, CBRServerConfig

        mock_client = Mock()
        mock_collection = Mock()

        # Simulate concurrent connection loss
        connection_attempts = []

        def track_connection_attempt(*args, **kwargs):
            connection_attempts.append(threading.current_thread().ident)
            if len(connection_attempts) == 1:
                # First thread succeeds
                return mock_collection
            else:
                # Subsequent threads reuse connection
                return mock_collection

        mock_client.get_collection.side_effect = track_connection_attempt
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client

        # Create config with real database enabled
        config = CBRServerConfig(use_real_db=True)
        server = CBRMCPServer(config=config)

        # Simulate concurrent access
        results = []
        threads = []

        def concurrent_query():
            try:
                result = server.query_with_reconnection("test")
                results.append(result)
            except Exception as e:
                results.append(e)

        for _ in range(5):
            thread = threading.Thread(target=concurrent_query)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should have handled concurrent reconnection safely
        assert len(results) == 5
        # Only one actual reconnection attempt should have been made
        unique_attempts = set(connection_attempts)
        assert len(unique_attempts) <= 2  # Allow for some race conditions


class TestEmbeddingModelReinitialization:
    """Test suite for embedding model reinitialization."""

    @patch("cbr_mcp_server.startup_configuration_validator")
    @patch("sentence_transformers.SentenceTransformer")
    def test_model_reload_on_memory_error(
        self, mock_sentence_transformer, mock_startup_validator
    ):
        """Test model reload when memory error occurs during embedding."""
        from cbr_mcp_server import CBRMCPServer

        # Bypass startup validation
        mock_startup_validator.return_value = True

        # Mock model that fails with OOM then succeeds after reload
        mock_model = Mock()
        embed_results = [
            MemoryError("CUDA out of memory"),
            [[0.1, 0.2, 0.3]],  # Success after reload
        ]
        mock_model.encode.side_effect = embed_results
        mock_sentence_transformer.return_value = mock_model

        server = CBRMCPServer()

        # Should reload model and retry embedding
        result = server.embed_with_retry("test text")

        assert result == [0.1, 0.2, 0.3]
        # Should have called model loading twice (initial + reload)
        assert mock_sentence_transformer.call_count == 2

    @patch("cbr_mcp_server.startup_configuration_validator")
    @patch("sentence_transformers.SentenceTransformer")
    def test_model_reload_on_loading_failure(
        self, mock_sentence_transformer, mock_startup_validator
    ):
        """Test fallback model loading when primary model fails to load."""
        from cbr_mcp_server import CBRMCPServer

        # Bypass startup validation
        mock_startup_validator.return_value = True

        # First attempt fails, second succeeds with fallback model
        loading_results = [
            OSError("Model loading failed"),
            Mock(),  # Fallback model succeeds
        ]
        mock_sentence_transformer.side_effect = loading_results

        server = CBRMCPServer()

        # Should attempt fallback model loading
        server.initialize_embedding_model_with_fallback()

        # Should have tried loading twice
        assert mock_sentence_transformer.call_count == 2
        # Second call should use fallback model
        fallback_call = mock_sentence_transformer.call_args_list[1]
        assert (
            fallback_call[0][0] != "nomic-ai/nomic-embed-text-v1.5"
        )  # Different model

    @patch("cbr_mcp_server.startup_configuration_validator")
    @patch("sentence_transformers.SentenceTransformer")
    def test_embedding_retry_after_model_reload(
        self, mock_sentence_transformer, mock_startup_validator
    ):
        """Test embedding retry after model reload."""
        from cbr_mcp_server import CBRMCPServer

        # Bypass startup validation
        mock_startup_validator.return_value = True

        # Mock model instances
        failed_model = Mock()
        failed_model.encode.side_effect = MemoryError("OOM")

        success_model = Mock()
        success_model.encode.return_value = [[0.5, 0.6, 0.7]]

        mock_sentence_transformer.side_effect = [failed_model, success_model]

        server = CBRMCPServer()

        # Should reload model and retry
        result = server.embed_with_model_recovery("test text")

        assert result == [0.5, 0.6, 0.7]
        assert failed_model.encode.call_count == 1
        assert success_model.encode.call_count == 1

    @patch("sentence_transformers.SentenceTransformer")
    @patch("psutil.virtual_memory")
    def test_model_health_monitoring(
        self, mock_psutil_memory, mock_sentence_transformer
    ):
        """Test monitoring model performance and health."""
        from cbr_mcp_server import CBRMCPServer

        # Mock memory usage monitoring
        mock_memory = Mock()
        mock_memory.percent = 85  # High memory usage
        mock_psutil_memory.return_value = mock_memory

        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model

        server = CBRMCPServer()

        # Should detect performance degradation
        health_status = server.check_model_health()

        assert health_status["memory_pressure"] is True
        assert health_status["requires_reload"] is True

    @patch("sentence_transformers.SentenceTransformer")
    def test_concurrent_model_access_during_reload(self, mock_sentence_transformer):
        """Test thread safety during model reload."""
        import threading
        import time

        from cbr_mcp_server import CBRMCPServer

        # Mock models
        old_model = Mock()
        new_model = Mock()
        new_model.encode.return_value = [[0.8, 0.9, 1.0]]

        mock_sentence_transformer.side_effect = [old_model, new_model]

        server = CBRMCPServer()

        # Simulate concurrent access during reload
        results = []
        errors = []

        def concurrent_embed():
            try:
                # Simulate some delay
                time.sleep(0.01)
                result = server.embed_thread_safe("test text")
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Start model reload in background
        reload_thread = threading.Thread(target=server.reload_embedding_model)
        reload_thread.start()

        # Start concurrent embedding requests
        embed_threads = []
        for _ in range(10):
            thread = threading.Thread(target=concurrent_embed)
            embed_threads.append(thread)
            thread.start()

        # Wait for all threads
        reload_thread.join()
        for thread in embed_threads:
            thread.join()

        # Should handle concurrent access safely
        assert len(errors) == 0  # No thread safety errors
        assert len(results) <= 10  # Some requests may be blocked during reload

    @patch("cbr_mcp_server.startup_configuration_validator")
    @patch("sentence_transformers.SentenceTransformer")
    def test_model_fallback_strategies(
        self, mock_sentence_transformer, mock_startup_validator
    ):
        """Test fallback to simpler models when primary model fails."""
        from cbr_mcp_server import CBRMCPServer

        # Bypass startup validation
        mock_startup_validator.return_value = True

        # Primary model fails, fallbacks succeed
        fallback_sequence = [
            OSError("Primary model failed"),  # nomic-ai model
            OSError("First fallback failed"),  # all-MiniLM-L6-v2
            Mock(),  # simple TF-IDF fallback succeeds
        ]

        mock_sentence_transformer.side_effect = fallback_sequence

        server = CBRMCPServer()

        # Should try multiple fallback strategies
        final_model = server.initialize_with_fallback_cascade()

        assert final_model is not None
        # Should have tried all fallback options
        assert mock_sentence_transformer.call_count == 3

    @patch("sentence_transformers.SentenceTransformer")
    def test_model_performance_monitoring(self, mock_sentence_transformer):
        """Test monitoring of model embedding performance."""
        from cbr_mcp_server import CBRMCPServer

        mock_model = Mock()

        # Simulate slow embeddings
        def slow_encode(*args, **kwargs):
            time.sleep(0.1)  # Simulate slow embedding
            return [[0.1, 0.2]]

        mock_model.encode.side_effect = slow_encode
        mock_sentence_transformer.return_value = mock_model

        server = CBRMCPServer()

        # Monitor embedding performance
        start_time = time.time()
        server.embed_with_monitoring("test text")
        end_time = time.time()

        performance_stats = server.get_embedding_performance_stats()

        assert (
            performance_stats["avg_embedding_time"] > 0.05
        )  # Should detect slow embedding
        assert performance_stats["total_embeddings"] == 1
        assert performance_stats["requires_optimization"] is True
