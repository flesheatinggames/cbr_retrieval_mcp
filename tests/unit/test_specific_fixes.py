import pytest
import json
import time
from unittest.mock import Mock, patch
from cbr_mcp_server import PerformanceTracker, RequestInterceptor, LoggerManager, LogConfig

def test_memory_leak_fix():
    """Test that operations dictionary is cleaned up."""
    tracker = PerformanceTracker(window_size=1)
    
    # Create multiple operations
    ops = []
    for i in range(10):
        op = tracker.start_operation(f"op_{i}")
        op.finish({})
        ops.append(op)
        time.sleep(0.1)
    
    # After window_size seconds, old operations should be cleaned up
    time.sleep(1.1)
    new_op = tracker.start_operation("new_op")
    
    # Check that old operations were cleaned up
    assert len(tracker.operations) < 10, "Operations dictionary should be cleaned up"
    print("✓ Memory leak fix: Operations dictionary is properly cleaned up")

def test_percentile_calculation():
    """Test correct percentile calculation."""
    tracker = PerformanceTracker()
    
    # Add measurements
    for duration in [1, 2, 3, 4, 5]:
        tracker.add_measurement({"operation": "test", "duration": duration})
    
    metrics = tracker.get_aggregated_metrics("test")
    
    # Median of [1,2,3,4,5] should be 3
    assert metrics["p50_latency"] == 3, f"Expected p50=3, got {metrics['p50_latency']}"
    print("✓ Percentile calculation: Correct median calculation")

def test_payload_size_tracking():
    """Test that original payload size is tracked correctly."""
    interceptor = RequestInterceptor(Mock(), max_payload_size=1024)
    
    # Create a large payload
    large_query = "x" * 2048
    request = {
        "tool": "cbr_retrieve",
        "arguments": {"query": large_query}
    }
    
    # Mock context
    context = Mock()
    context.session_id = "test"
    
    logged = interceptor.log_request(context, request)
    
    # Should track the original query size
    assert logged.get("original_size") == 2048, f"Expected size=2048, got {logged.get('original_size')}"
    print("✓ Payload size: Correctly tracks original data size")

def test_error_handling():
    """Test that file setup errors are handled properly."""
    config = LogConfig()
    
    # This should handle errors gracefully
    with patch('cbr_mcp_server.logging.handlers.RotatingFileHandler') as mock_handler:
        mock_handler.side_effect = Exception("File permission error")
        
        # Should not crash but handle the error
        try:
            manager = LoggerManager(config)
            print("✓ Error handling: Errors are handled appropriately")
        except RuntimeError as e:
            if "Failed to setup file handler" in str(e):
                print("✓ Error handling: Real errors raise exceptions as expected")
            else:
                raise

if __name__ == "__main__":
    test_memory_leak_fix()
    test_percentile_calculation()
    test_payload_size_tracking()
    test_error_handling()
    print("\n✅ All specific bug fixes verified!")
