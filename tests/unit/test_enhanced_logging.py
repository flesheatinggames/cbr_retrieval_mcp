"""
Comprehensive test suite for Enhanced Logging System Implementation.

This test suite defines the expected behavior for the production-ready logging
system with structlog integration, configurable formatting, performance tracking,
and robust file management.

Tests cover:
- LoggerManager class with structlog integration and configuration
- RequestInterceptor for MCP tool call logging and correlation
- PerformanceTracker for query latency and resource monitoring
- Configurable log formatting (JSON, text, colored)
- Log rotation and file management
- Environment variable configuration
- Error handling and recovery scenarios
"""

import asyncio
import pytest
import json
import os
import tempfile
import time
from unittest.mock import AsyncMock, Mock, patch, MagicMock, mock_open
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta

# These imports will fail initially since the enhanced logging implementation doesn't exist yet
try:
    from cbr_mcp_server import (
        LoggerManager,
        RequestInterceptor, 
        PerformanceTracker,
        EnhancedLogger,
        LogConfig
    )
    import structlog
    import logging
    from logging.handlers import RotatingFileHandler
except ImportError:
    # Expected to fail in TDD red phase - enhanced logging implementation doesn't exist yet
    pass


class TestLoggerManager:
    """Test LoggerManager class with structlog integration and configuration."""

    @pytest.fixture
    def mock_structlog(self):
        """Mock structlog configuration and processors."""
        with patch('structlog.configure') as mock_configure, \
             patch('structlog.processors.JSONRenderer') as mock_json_renderer, \
             patch('structlog.processors.TimeStamper') as mock_timestamper, \
             patch('structlog.stdlib.add_log_level') as mock_add_level, \
             patch('structlog.dev.ConsoleRenderer') as mock_console_renderer:
            
            mock_json_renderer.return_value = Mock()
            mock_timestamper.return_value = Mock()
            mock_add_level.return_value = Mock()
            mock_console_renderer.return_value = Mock()
            
            yield {
                'configure': mock_configure,
                'json_renderer': mock_json_renderer,
                'timestamper': mock_timestamper,
                'add_level': mock_add_level,
                'console_renderer': mock_console_renderer
            }

    @pytest.fixture
    def mock_logging(self):
        """Mock Python standard logging configuration."""
        with patch('logging.getLogger') as mock_get_logger, \
             patch('logging.StreamHandler') as mock_stream_handler, \
             patch('logging.handlers.RotatingFileHandler') as mock_rotating_handler:
            
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            mock_handler = Mock()
            mock_stream_handler.return_value = mock_handler
            mock_rotating_handler.return_value = mock_handler
            
            yield {
                'get_logger': mock_get_logger,
                'logger': mock_logger,
                'stream_handler': mock_stream_handler,
                'rotating_handler': mock_rotating_handler,
                'handler': mock_handler
            }

    def test_logger_manager_initialization_with_json_format(self, mock_structlog, mock_logging):
        """Test LoggerManager initializes with JSON log format configuration."""
        # Test will fail - LoggerManager class doesn't exist yet
        config = LogConfig(
            level="INFO",
            format="json",
            output_file="test.log",
            max_file_size=10*1024*1024,
            backup_count=5
        )
        
        manager = LoggerManager(config)
        
        # Should configure structlog with JSON renderer
        mock_structlog['configure'].assert_called_once()
        call_args = mock_structlog['configure'].call_args
        
        # Verify JSON renderer is in processors
        processors = call_args.kwargs['processors']
        assert any('JSONRenderer' in str(p) for p in processors)
        
        # Verify timestamper is configured
        mock_structlog['timestamper'].assert_called_once()
        
        # Verify log level processor is added
        mock_structlog['add_level'].assert_called_once()

    def test_logger_manager_initialization_with_text_format(self, mock_structlog, mock_logging):
        """Test LoggerManager initializes with plain text format configuration."""
        # Test will fail - LoggerManager class doesn't exist yet
        config = LogConfig(
            level="DEBUG",
            format="text", 
            output_file="debug.log",
            max_file_size=5*1024*1024,
            backup_count=3
        )
        
        manager = LoggerManager(config)
        
        # Should not use JSON renderer for text format
        mock_structlog['configure'].assert_called_once()
        call_args = mock_structlog['configure'].call_args
        processors = call_args.kwargs['processors']
        
        # JSON renderer should not be present for text format
        assert not any('JSONRenderer' in str(p) for p in processors)
        
        # Console renderer should be used for text format
        mock_structlog['console_renderer'].assert_called_once()

    def test_logger_manager_initialization_with_colored_format(self, mock_structlog, mock_logging):
        """Test LoggerManager initializes with colored format for terminal output."""
        # Test will fail - LoggerManager class doesn't exist yet
        config = LogConfig(
            level="WARNING",
            format="colored",
            output_file=None,  # Terminal output only
            enable_colors=True
        )
        
        manager = LoggerManager(config)
        
        # Should configure colored console renderer
        mock_structlog['console_renderer'].assert_called_once_with(colors=True)

    @patch.dict(os.environ, {
        'CBR_LOG_LEVEL': 'DEBUG',
        'CBR_LOG_FORMAT': 'json',
        'CBR_LOG_FILE': '/tmp/cbr_test.log',
        'CBR_LOG_MAX_SIZE': '20971520',
        'CBR_LOG_BACKUP_COUNT': '7',
        'CBR_LOG_ROTATION': 'true'
    })
    def test_logger_manager_environment_variable_configuration(self, mock_structlog, mock_logging):
        """Test LoggerManager loads configuration from environment variables."""
        # Test will fail - LoggerManager.from_environment() method doesn't exist yet
        manager = LoggerManager.from_environment()
        
        # Verify environment variables are read correctly
        assert manager.config.level == "DEBUG"
        assert manager.config.format == "json"
        assert manager.config.output_file == "/tmp/cbr_test.log"
        assert manager.config.max_file_size == 20971520  # 20MB
        assert manager.config.backup_count == 7
        assert manager.config.rotation_enabled == True

    @patch('os.path.getsize')
    @patch('logging.handlers.RotatingFileHandler.doRollover')
    def test_log_file_rotation_on_size_limit(self, mock_rollover, mock_getsize, mock_structlog, mock_logging):
        """Test log file rotation when maximum file size is reached."""
        # Test will fail - file rotation logic doesn't exist yet
        config = LogConfig(
            level="INFO",
            format="json",
            output_file="test.log",
            max_file_size=1024,  # Small size for testing
            backup_count=3
        )
        
        # Mock file size exceeding limit
        mock_getsize.return_value = 2048  # Exceeds 1024 byte limit
        
        manager = LoggerManager(config)
        
        # Simulate logging that should trigger rotation
        logger = manager.get_logger("test")
        logger.info("This is a test log message that should trigger rotation")
        
        # Verify rotation was triggered
        mock_rollover.assert_called_once()

    @patch('uuid.uuid4')
    def test_request_id_generation_and_propagation(self, mock_uuid, mock_structlog, mock_logging):
        """Test unique request ID generation and propagation through log context."""
        # Test will fail - request ID generation doesn't exist yet
        mock_uuid.return_value.hex = "test-request-id-12345"
        
        config = LogConfig(level="INFO", format="json")
        manager = LoggerManager(config)
        
        # Generate request ID
        request_id = manager.generate_request_id()
        assert request_id == "test-request-id-12345"
        
        # Set request context
        manager.set_request_context(request_id, {"user_agent": "test-agent"})
        
        # Verify context is maintained
        context = manager.get_request_context(request_id)
        assert context["request_id"] == request_id
        assert context["user_agent"] == "test-agent"

    def test_metadata_injection_in_log_entries(self, mock_structlog, mock_logging):
        """Test metadata injection and filtering in log entries."""
        # Test will fail - metadata injection doesn't exist yet
        config = LogConfig(level="INFO", format="json")
        manager = LoggerManager(config)
        
        # Set up request context with metadata
        request_id = "test-request-123"
        metadata = {
            "user_agent": "CBR-Client/1.0",
            "query_params": {"category": "brewing", "limit": 10},
            "response_size": 1024,
            "client_ip": "192.168.1.100"
        }
        
        manager.set_request_context(request_id, metadata)
        logger = manager.get_logger("cbr.test")
        
        # Log with context
        with manager.request_context(request_id):
            logger.info("Processing CBR query", operation="retrieve")
        
        # Verify metadata is injected (this will fail until implemented)
        # The actual verification would check the log output contains the metadata

    @patch('time.time')
    def test_performance_logging_accuracy(self, mock_time, mock_structlog, mock_logging):
        """Test performance logging tracks timing accurately."""
        # Test will fail - performance logging doesn't exist yet
        config = LogConfig(level="INFO", format="json", performance_logging=True)
        manager = LoggerManager(config)
        
        # Mock time progression
        start_time = 1000.0
        end_time = 1002.5  # 2.5 seconds later
        mock_time.side_effect = [start_time, end_time]
        
        logger = manager.get_logger("cbr.performance")
        
        # Start performance tracking
        perf_tracker = manager.start_performance_tracking("cbr_query")
        
        # Simulate operation
        time.sleep(0.1)  # This will be mocked
        
        # End performance tracking
        perf_tracker.finish("query completed", result_count=5)
        
        # Verify performance metrics are logged
        # Should log duration of 2.5 seconds
        assert perf_tracker.duration == 2.5


class TestRequestInterceptor:
    """Test RequestInterceptor for MCP tool call logging and correlation."""

    @pytest.fixture
    def mock_logger_manager(self):
        """Mock LoggerManager for request interceptor tests."""
        manager = Mock(spec=LoggerManager)
        manager.get_logger.return_value = Mock()
        manager.generate_request_id.return_value = "test-request-id"
        manager.set_request_context = Mock()
        manager.get_request_context.return_value = {"request_id": "test-request-id"}
        return manager

    @pytest.fixture
    def mock_mcp_context(self):
        """Mock MCP context for tool call interception."""
        context = Mock()
        context.session_id = "test-session-123"
        context.request_id = "mcp-request-456"
        return context

    def test_mcp_tool_call_logging_with_complete_metadata(self, mock_logger_manager, mock_mcp_context):
        """Test complete request/response logging for MCP tool calls with metadata."""
        # Test will fail - RequestInterceptor class doesn't exist yet
        interceptor = RequestInterceptor(mock_logger_manager)
        
        # Mock MCP tool request
        tool_request = {
            "tool": "cbr_retrieve",
            "arguments": {
                "query": "brewing temperature control",
                "category": "brewing", 
                "limit": 5,
                "similarity_threshold": 0.8
            }
        }
        
        # Mock MCP tool response
        tool_response = {
            "content": [{"type": "text", "text": "Found 3 relevant cases"}],
            "isError": False,
            "result_count": 3
        }
        
        # Intercept the call
        logged_request = interceptor.log_request(mock_mcp_context, tool_request)
        logged_response = interceptor.log_response(mock_mcp_context, tool_response)
        
        # Verify request logging
        assert logged_request["tool"] == "cbr_retrieve"
        assert logged_request["request_id"] is not None
        assert "arguments" in logged_request
        
        # Verify response logging  
        assert logged_response["result_count"] == 3
        assert logged_response["isError"] == False

    def test_request_correlation_across_intercepted_calls(self, mock_logger_manager, mock_mcp_context):
        """Test request IDs are maintained across intercepted calls."""
        # Test will fail - request correlation doesn't exist yet
        interceptor = RequestInterceptor(mock_logger_manager)
        
        # First request
        request1 = {"tool": "cbr_retrieve", "arguments": {"query": "test1"}}
        logged_request1 = interceptor.log_request(mock_mcp_context, request1)
        
        # Second related request  
        request2 = {"tool": "cbr_find_similar", "arguments": {"case_id": "case123"}}
        logged_request2 = interceptor.log_request(mock_mcp_context, request2)
        
        # Both should have the same session correlation
        assert logged_request1["session_id"] == logged_request2["session_id"]
        # But different request IDs
        assert logged_request1["request_id"] != logged_request2["request_id"]

    def test_parameter_sanitization_in_logs(self, mock_logger_manager, mock_mcp_context):
        """Test sensitive parameters are masked in logs."""
        # Test will fail - parameter sanitization doesn't exist yet
        interceptor = RequestInterceptor(mock_logger_manager)
        
        # Request with sensitive data
        request_with_sensitive_data = {
            "tool": "cbr_admin",
            "arguments": {
                "api_key": "super-secret-key-12345",
                "password": "admin-password", 
                "query": "legitimate query text",
                "auth_token": "bearer-token-abcdef"
            }
        }
        
        logged_request = interceptor.log_request(mock_mcp_context, request_with_sensitive_data)
        
        # Verify sensitive fields are masked
        assert logged_request["arguments"]["api_key"] == "***MASKED***"
        assert logged_request["arguments"]["password"] == "***MASKED***"
        assert logged_request["arguments"]["auth_token"] == "***MASKED***"
        # Non-sensitive fields should remain
        assert logged_request["arguments"]["query"] == "legitimate query text"

    def test_large_payload_truncation(self, mock_logger_manager, mock_mcp_context):
        """Test large requests/responses are truncated appropriately."""
        # Test will fail - payload truncation doesn't exist yet
        interceptor = RequestInterceptor(mock_logger_manager, max_payload_size=1024)
        
        # Create large payload
        large_query = "x" * 2048  # 2KB, exceeds 1KB limit
        large_request = {
            "tool": "cbr_retrieve",
            "arguments": {"query": large_query}
        }
        
        logged_request = interceptor.log_request(mock_mcp_context, large_request)
        
        # Verify payload is truncated
        assert len(logged_request["arguments"]["query"]) < 2048
        assert logged_request["arguments"]["query"].endswith("...[TRUNCATED]")
        assert logged_request.get("payload_truncated") == True
        assert logged_request.get("original_size") == 2048

    @patch('traceback.format_exc')
    def test_error_context_capture(self, mock_format_exc, mock_logger_manager, mock_mcp_context):
        """Test exceptions and stack traces are captured with context."""
        # Test will fail - error context capture doesn't exist yet
        mock_format_exc.return_value = "Traceback (most recent call last):\n  File test.py, line 1\n    raise ValueError('test error')\nValueError: test error"
        
        interceptor = RequestInterceptor(mock_logger_manager)
        
        # Simulate an error during tool execution
        error_context = {
            "tool": "cbr_retrieve", 
            "error_type": "ValueError",
            "error_message": "Invalid query parameter",
            "request_data": {"query": "malformed query"}
        }
        
        logged_error = interceptor.log_error(mock_mcp_context, error_context, capture_stack=True)
        
        # Verify error context is captured
        assert logged_error["error_type"] == "ValueError"
        assert logged_error["error_message"] == "Invalid query parameter"
        assert "stack_trace" in logged_error
        assert logged_error["stack_trace"].startswith("Traceback")


class TestPerformanceTracker:
    """Test PerformanceTracker for query latency and resource monitoring."""

    @pytest.fixture
    def mock_time(self):
        """Mock time.time() for performance measurements."""
        with patch('time.time') as mock_time:
            yield mock_time

    @pytest.fixture  
    def mock_psutil(self):
        """Mock psutil for system resource monitoring."""
        with patch('psutil.Process') as mock_process, \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.cpu_percent') as mock_cpu:
            
            # Mock process resource usage
            mock_proc_instance = Mock()
            mock_proc_instance.memory_info.return_value.rss = 104857600  # 100MB
            mock_proc_instance.cpu_percent.return_value = 15.5
            mock_process.return_value = mock_proc_instance
            
            # Mock system resource usage
            mock_mem_info = Mock()
            mock_mem_info.total = 8589934592  # 8GB
            mock_mem_info.used = 4294967296   # 4GB
            mock_mem_info.percent = 50.0
            mock_memory.return_value = mock_mem_info
            
            mock_cpu.return_value = 25.0
            
            yield {
                'process': mock_process,
                'memory': mock_memory, 
                'cpu': mock_cpu,
                'proc_instance': mock_proc_instance
            }

    def test_query_latency_measurement_accuracy(self, mock_time):
        """Test accurate latency calculation for queries."""
        # Test will fail - PerformanceTracker class doesn't exist yet
        mock_time.side_effect = [1000.0, 1002.5]  # 2.5 second duration
        
        tracker = PerformanceTracker()
        
        # Start tracking
        operation = tracker.start_operation("cbr_query")
        
        # Simulate work (mocked time advancement)
        # ... actual work would happen here ...
        
        # End tracking
        metrics = operation.finish({"result_count": 10, "category": "brewing"})
        
        # Verify accurate timing
        assert metrics["duration"] == 2.5
        assert metrics["operation"] == "cbr_query"
        assert metrics["result_count"] == 10

    def test_memory_usage_tracking_with_psutil(self, mock_psutil):
        """Test memory usage measurements are captured accurately."""
        # Test will fail - memory tracking doesn't exist yet
        tracker = PerformanceTracker()
        
        # Capture memory usage
        memory_metrics = tracker.capture_memory_metrics()
        
        # Verify memory measurements
        assert memory_metrics["process_memory_mb"] == 100  # 100MB from mock
        assert memory_metrics["system_memory_total_gb"] == 8  # 8GB from mock
        assert memory_metrics["system_memory_used_gb"] == 4   # 4GB from mock
        assert memory_metrics["system_memory_percent"] == 50.0

    def test_performance_metrics_aggregation(self, mock_time):
        """Test rolling averages and percentiles calculation."""
        # Test will fail - metrics aggregation doesn't exist yet
        tracker = PerformanceTracker(window_size=100)
        
        # Add multiple performance measurements
        latencies = [0.1, 0.2, 0.15, 0.3, 0.25, 0.18, 0.22, 0.16, 0.28, 0.19]
        for i, latency in enumerate(latencies):
            mock_time.side_effect = [i, i + latency]
            operation = tracker.start_operation("test_query")
            metrics = operation.finish({})
            tracker.add_measurement(metrics)
        
        # Get aggregated metrics
        aggregated = tracker.get_aggregated_metrics("test_query")
        
        # Verify statistical calculations
        assert aggregated["mean_latency"] == pytest.approx(0.203, rel=1e-2)
        assert aggregated["p50_latency"] == pytest.approx(0.19, rel=1e-2)
        assert aggregated["p95_latency"] == pytest.approx(0.28, rel=1e-2)
        assert aggregated["count"] == 10

    def test_performance_threshold_alerts(self, mock_time):
        """Test alerts when performance thresholds are exceeded."""
        # Test will fail - threshold alerting doesn't exist yet  
        alert_callback = Mock()
        
        tracker = PerformanceTracker(
            latency_threshold=1.0,  # 1 second threshold
            memory_threshold=500,   # 500MB threshold
            alert_callback=alert_callback
        )
        
        # Simulate slow query
        mock_time.side_effect = [1000.0, 1002.0]  # 2 second duration (exceeds threshold)
        
        operation = tracker.start_operation("slow_query")
        metrics = operation.finish({})
        
        # Verify alert was triggered
        alert_callback.assert_called_once()
        alert_args = alert_callback.call_args[0][0]
        assert alert_args["threshold_type"] == "latency"
        assert alert_args["threshold_value"] == 1.0
        assert alert_args["actual_value"] == 2.0
        assert alert_args["operation"] == "slow_query"

    @pytest.mark.asyncio
    async def test_concurrent_operation_tracking(self, mock_time):
        """Test performance tracking works correctly with concurrent requests."""
        # Test will fail - concurrent tracking doesn't exist yet
        tracker = PerformanceTracker()
        
        # Mock time for concurrent operations
        time_sequence = [1000.0, 1000.1, 1001.0, 1002.0, 1002.5, 1003.0]
        mock_time.side_effect = time_sequence
        
        # Start multiple concurrent operations
        op1 = tracker.start_operation("query_1")
        op2 = tracker.start_operation("query_2") 
        
        # Simulate concurrent execution
        await asyncio.sleep(0.001)  # Minimal delay
        
        # Finish operations in different order
        metrics2 = op2.finish({"result_count": 5})
        metrics1 = op1.finish({"result_count": 3})
        
        # Verify both operations tracked correctly
        assert metrics1["duration"] == 2.0  # 1000.0 to 1002.0 (actual consumption)
        assert metrics2["duration"] == pytest.approx(0.9, rel=1e-2)   # 1000.1 to 1001.0 (actual consumption) 
        assert metrics1["result_count"] == 3
        assert metrics2["result_count"] == 5


class TestLogConfiguration:
    """Test configurable log formatting (JSON, text, colored) and settings."""

    @pytest.fixture
    def temp_log_file(self):
        """Create temporary log file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass

    def test_json_log_formatting_output(self, temp_log_file):
        """Test structlog produces valid JSON output with all required fields."""
        # Test will fail - JSON formatting doesn't exist yet
        config = LogConfig(
            level="INFO",
            format="json",
            output_file=temp_log_file
        )
        
        manager = LoggerManager(config)
        logger = manager.get_logger("test.json")
        
        # Log test message with context
        logger.info("Test message", user_id=123, action="query", duration=0.5)
        
        # Read and verify JSON output
        with open(temp_log_file, 'r') as f:
            log_line = f.readline().strip()
        
        # Parse JSON
        log_entry = json.loads(log_line)
        
        # Verify required fields
        assert log_entry["event"] == "Test message"
        assert log_entry["level"] == "info"
        assert log_entry["user_id"] == 123
        assert log_entry["action"] == "query"
        assert log_entry["duration"] == 0.5
        assert "timestamp" in log_entry
        assert "logger" in log_entry

    def test_text_log_formatting_readability(self, temp_log_file):
        """Test plain text formatting with readable timestamps and levels."""
        # Test will fail - text formatting doesn't exist yet
        config = LogConfig(
            level="DEBUG", 
            format="text",
            output_file=temp_log_file
        )
        
        manager = LoggerManager(config)
        logger = manager.get_logger("test.text")
        
        # Log test messages at different levels
        logger.debug("Debug message", component="retriever")
        logger.info("Info message", operation="search")
        logger.warning("Warning message", issue="performance")
        logger.error("Error message", error_code=500)
        
        # Read and verify text output format
        with open(temp_log_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 4
        
        # Verify timestamp format and level indicators
        for line in lines:
            # Should contain readable timestamp
            assert any(char.isdigit() for char in line[:20])  # Date/time in first 20 chars
            # Should contain log level in brackets (may have padding)
            assert ('[debug' in line or '[info' in line or '[warning' in line or '[error' in line)

    @patch('sys.stderr.isatty')
    def test_colored_log_formatting_terminal_mode(self, mock_isatty, capsys, caplog):
        """Test ANSI color codes are applied in terminal mode."""
        # Test will fail - colored formatting doesn't exist yet
        mock_isatty.return_value = True  # Simulate terminal environment
        
        config = LogConfig(
            level="INFO",
            format="colored", 
            output_file=None,  # Console output
            enable_colors=True
        )
        
        manager = LoggerManager(config)
        logger = manager.get_logger("test.colored")
        
        # Log messages at different levels
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Capture console output - check both capsys and caplog
        captured = capsys.readouterr()
        
        # Check both captured output and the log records for ANSI codes
        # Since pytest may capture logging, check caplog.text and raw record messages
        all_output = captured.out + captured.err + caplog.text
        
        # Also check the raw log record messages for ANSI codes
        raw_messages = ""
        for record in caplog.records:
            raw_messages += record.getMessage()
        
        all_content = all_output + raw_messages
        
        # Verify ANSI color codes are present somewhere (console, logs, or raw messages)
        assert '\033[' in all_content or '\x1b[' in all_content  # ANSI escape codes
        
        # Different levels should have different colors
        color_codes = all_content.count('\033[') + all_content.count('\x1b[')
        assert color_codes >= 3  # At least one color code per log level

    def test_log_level_filtering_configuration(self, temp_log_file):
        """Test only logs above configured level are output."""
        # Test will fail - log level filtering doesn't exist yet
        config = LogConfig(
            level="WARNING",  # Only WARNING and ERROR should appear
            format="json",
            output_file=temp_log_file
        )
        
        manager = LoggerManager(config)
        logger = manager.get_logger("test.filter")
        
        # Log at various levels
        logger.debug("Debug message - should not appear")
        logger.info("Info message - should not appear")
        logger.warning("Warning message - should appear") 
        logger.error("Error message - should appear")
        
        # Read output file
        with open(temp_log_file, 'r') as f:
            lines = f.readlines()
        
        # Should only have 2 lines (WARNING and ERROR)
        assert len(lines) == 2
        
        # Verify content
        log1 = json.loads(lines[0].strip())
        log2 = json.loads(lines[1].strip())
        
        assert log1["level"] == "warning"
        assert log2["level"] == "error"

    def test_file_vs_console_output_different_formatters(self, temp_log_file, capsys, caplog):
        """Test different formatters for file and console streams."""
        # Test will fail - dual output formatting doesn't exist yet
        config = LogConfig(
            level="INFO",
            format="json",          # JSON to file
            console_format="text",  # Text to console
            output_file=temp_log_file,
            console_output=True
        )
        
        manager = LoggerManager(config)
        logger = manager.get_logger("test.dual")
        
        # Log test message
        logger.info("Test dual output", request_id="req-123")
        
        # Check file output (should be JSON)
        with open(temp_log_file, 'r') as f:
            file_content = f.readline().strip()
        
        file_log = json.loads(file_content)
        assert file_log["event"] == "Test dual output"
        assert file_log["request_id"] == "req-123"
        
        # Check console output (should be text) - also check caplog since pytest captures logging
        captured = capsys.readouterr()
        console_output = captured.out + captured.err
        
        # If console output is empty (due to pytest capture), check caplog
        if not console_output and hasattr(self, '_caplog'):
            console_output = caplog.text
        
        # Console should contain readable text format
        assert "Test dual output" in (console_output + caplog.text)
        assert "req-123" in (console_output + caplog.text)


class TestFileManagement:
    """Test log file rotation, cleanup, and management."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary directory for log file tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @patch('os.path.getsize')
    def test_log_file_rotation_at_size_threshold(self, mock_getsize, temp_log_dir):
        """Test log file rotation at configured size thresholds."""
        # Test will fail - file rotation doesn't exist yet
        log_file = os.path.join(temp_log_dir, "test.log")
        max_size = 1024  # 1KB limit for testing
        
        config = LogConfig(
            level="INFO",
            format="json",
            output_file=log_file,
            max_file_size=max_size,
            backup_count=3,
            rotation_enabled=True
        )
        
        manager = LoggerManager(config)
        logger = manager.get_logger("test.rotation")
        
        # Mock file size progression
        sizes = [500, 800, 1200]  # Last one exceeds limit
        mock_getsize.side_effect = sizes
        
        # Log messages to trigger rotation
        logger.info("Message 1")
        logger.info("Message 2") 
        logger.info("Message 3")  # This should trigger rotation
        
        # Verify rotation occurred
        # Should have main log file plus rotated backup
        log_files = [f for f in os.listdir(temp_log_dir) if f.startswith("test.log")]
        assert len(log_files) >= 2  # Original + at least 1 backup
        
        # Verify backup file naming
        assert any(f.endswith(".1") for f in log_files)

    def test_log_file_cleanup_retention_policy(self, temp_log_dir):
        """Test old log files are cleaned up according to retention policy."""
        # Test will fail - cleanup policy doesn't exist yet
        log_file = os.path.join(temp_log_dir, "cleanup.log")
        
        config = LogConfig(
            level="INFO",
            format="json",
            output_file=log_file,
            backup_count=2,  # Keep only 2 backup files
            cleanup_enabled=True
        )
        
        # Create mock old log files
        old_files = [
            "cleanup.log.1",   # Should keep
            "cleanup.log.2",   # Should keep  
            "cleanup.log.3",   # Should delete
            "cleanup.log.4",   # Should delete
            "cleanup.log.5"    # Should delete
        ]
        
        for old_file in old_files:
            Path(temp_log_dir, old_file).touch()
        
        manager = LoggerManager(config)
        
        # Trigger cleanup
        manager.cleanup_old_logs()
        
        # Verify cleanup
        remaining_files = [f for f in os.listdir(temp_log_dir) if f.startswith("cleanup.log")]
        
        # Should have main log + 2 backups = 3 total
        assert len(remaining_files) <= 3
        # Should keep most recent backups
        assert "cleanup.log.1" in remaining_files
        assert "cleanup.log.2" in remaining_files
        # Should remove older backups
        assert "cleanup.log.5" not in remaining_files

    @patch('cbr_mcp_server.threading.Lock')
    def test_concurrent_file_access_thread_safety(self, mock_lock, temp_log_dir):
        """Test thread-safe file writing during rotation."""
        # Test will fail - thread safety doesn't exist yet
        lock_instance = Mock()
        lock_instance.__enter__ = Mock(return_value=lock_instance)
        lock_instance.__exit__ = Mock(return_value=None)
        mock_lock.return_value = lock_instance
        
        log_file = os.path.join(temp_log_dir, "concurrent.log")
        config = LogConfig(
            level="INFO",
            format="json", 
            output_file=log_file,
            thread_safe=True
        )
        
        manager = LoggerManager(config)
        logger = manager.get_logger("test.concurrent")
        
        # Simulate concurrent logging
        import threading
        
        def log_worker(worker_id):
            for i in range(5):
                logger.info(f"Worker {worker_id} message {i}")
        
        # Start multiple threads
        threads = []
        for i in range(3):
            t = threading.Thread(target=log_worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify thread safety mechanisms were used
        mock_lock.assert_called()
        assert lock_instance.__enter__.call_count > 0
        assert lock_instance.__exit__.call_count > 0

    @patch('shutil.disk_usage')
    def test_disk_space_monitoring_cleanup_trigger(self, mock_disk_usage, temp_log_dir):
        """Test cleanup when disk space is low."""
        # Test will fail - disk space monitoring doesn't exist yet
        log_file = os.path.join(temp_log_dir, "space.log")
        
        # Mock low disk space
        mock_disk_usage.return_value = (
            100 * 1024 * 1024,  # Total: 100MB
            95 * 1024 * 1024,   # Used: 95MB  
            5 * 1024 * 1024     # Free: 5MB (only 5% free)
        )
        
        config = LogConfig(
            level="INFO",
            format="json",
            output_file=log_file,
            disk_space_monitoring=True,
            min_free_space_percent=10,  # Require 10% free space
            backup_count=2  # Only keep 2 backups to force cleanup
        )
        
        # Create some old log files to cleanup
        for i in range(5):
            Path(temp_log_dir, f"space.log.{i}").touch()
        
        manager = LoggerManager(config)
        logger = manager.get_logger("test.space")
        
        # Log message should trigger space check and cleanup
        logger.info("Test message")
        
        # Verify cleanup was triggered due to low space
        remaining_files = [f for f in os.listdir(temp_log_dir) if f.startswith("space.log")]
        assert len(remaining_files) < 6  # Some files should be cleaned up

    @patch('os.chmod')
    @patch('os.access')
    def test_file_permission_handling(self, mock_access, mock_chmod, temp_log_dir):
        """Test graceful handling of file permission errors."""
        # Test will fail - permission handling doesn't exist yet
        log_file = os.path.join(temp_log_dir, "permission.log")
        
        # Mock permission denied for file access
        mock_access.return_value = False  # No write permission
        
        config = LogConfig(
            level="INFO",
            format="json",
            output_file=log_file,
            handle_permissions=True
        )
        
        # Should handle permission error gracefully
        try:
            manager = LoggerManager(config)
            logger = manager.get_logger("test.permission")
            
            # This should not crash even with permission issues
            logger.info("Test message with permission issues")
            
        except PermissionError:
            pytest.fail("Should handle permission errors gracefully")
        
        # Verify attempt to fix permissions
        mock_chmod.assert_called()


# Integration tests to ensure all components work together
class TestEnhancedLoggingIntegration:
    """Integration tests for the complete enhanced logging system."""

    @pytest.fixture
    def full_logging_config(self, tmp_path):
        """Complete logging configuration for integration testing."""
        return LogConfig(
            level="DEBUG",
            format="json",
            output_file=str(tmp_path / "integration.log"),
            console_output=True,
            console_format="colored", 
            max_file_size=1024*1024,  # 1MB
            backup_count=3,
            rotation_enabled=True,
            performance_logging=True,
            request_correlation=True,
            thread_safe=True
        )

    @pytest.mark.asyncio
    async def test_end_to_end_logging_workflow(self, full_logging_config):
        """Test complete end-to-end logging workflow with all components."""
        # Test will fail - integration doesn't exist yet
        
        # Initialize complete system
        manager = LoggerManager(full_logging_config)
        interceptor = RequestInterceptor(manager)
        perf_tracker = PerformanceTracker()
        
        # Mock MCP context
        mock_context = Mock()
        mock_context.session_id = "integration-test-session"
        
        # Simulate complete request lifecycle
        request = {
            "tool": "cbr_retrieve",
            "arguments": {
                "query": "integration test query",
                "category": "testing",
                "limit": 5
            }
        }
        
        # Start request logging and performance tracking
        logged_request = interceptor.log_request(mock_context, request)
        perf_operation = perf_tracker.start_operation("cbr_retrieve")
        
        # Simulate processing time
        await asyncio.sleep(0.01)
        
        # Mock response
        response = {
            "content": [{"type": "text", "text": "Integration test results"}],
            "isError": False,
            "result_count": 3
        }
        
        # Finish logging and performance tracking
        logged_response = interceptor.log_response(mock_context, response)
        perf_metrics = perf_operation.finish({"result_count": 3})
        
        # Verify integration worked
        assert logged_request["tool"] == "cbr_retrieve"
        assert logged_response["result_count"] == 3
        assert perf_metrics["operation"] == "cbr_retrieve"
        assert perf_metrics["duration"] > 0
        
        # Verify log files were created
        assert full_logging_config.output_file and Path(full_logging_config.output_file).exists()

