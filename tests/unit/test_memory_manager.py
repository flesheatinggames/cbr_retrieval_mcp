"""
Unit tests for Memory Management System components.

This module tests MemoryManager, EmbeddingCacheManager, and MemoryPressureDetector
components following TDD principles. These tests will initially fail until the
implementations are complete.

Test Coverage:
- MemoryManager: Memory limit enforcement and monitoring
- EmbeddingCacheManager: Embedding caching with LRU eviction
- MemoryPressureDetector: System memory pressure detection
"""

import time
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import MagicMock, Mock, call, patch

import numpy as np
import pytest

# These imports will fail initially - this is expected in TDD
from cbr_mcp_server.performance.memory_manager import (
    EmbeddingCacheManager,
    MemoryManager,
    MemoryPressureDetector,
)


class TestMemoryManager:
    """Test suite for MemoryManager component."""

    @pytest.fixture
    def mock_psutil(self):
        """Mock psutil for memory testing."""
        with patch("cbr_mcp_server.performance.memory_manager.psutil") as mock:
            yield mock

    @pytest.fixture
    def memory_manager(self, mock_psutil):
        """Create MemoryManager instance with mocked psutil."""
        mock_psutil.virtual_memory.return_value.total = 8 * 1024 * 1024 * 1024  # 8GB
        return MemoryManager(max_memory_mb=500)

    def test_memory_manager_initialization(self, memory_manager, mock_psutil):
        """Verify MemoryManager initializes with correct default values."""
        assert memory_manager.max_memory_mb == 500
        assert memory_manager.pressure_threshold == 0.8
        assert memory_manager.emergency_eviction_percentage >= 0.5
        mock_psutil.virtual_memory.assert_called()

    def test_check_memory_usage(self, memory_manager, mock_psutil):
        """Verify memory usage checking returns accurate current usage."""
        # Mock process memory info to return 200MB
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 200 * 1024 * 1024
        mock_psutil.Process.return_value = mock_process

        usage_mb = memory_manager.check_memory_usage()

        assert usage_mb == 200
        mock_psutil.Process.assert_called()
        mock_process.memory_info.assert_called()

    def test_enforce_memory_limits_under_limit(self, memory_manager, mock_psutil):
        """Verify no action taken when memory usage is under limit."""
        # Mock memory usage at 300MB (under 500MB limit)
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 300 * 1024 * 1024
        mock_psutil.Process.return_value = mock_process

        mock_eviction_callback = Mock()
        memory_manager.set_eviction_callback(mock_eviction_callback)

        result = memory_manager.enforce_memory_limits()

        assert result is True
        mock_eviction_callback.assert_not_called()

    def test_enforce_memory_limits_over_limit(self, memory_manager, mock_psutil):
        """Verify cache eviction triggered when memory exceeds limit."""
        # Mock memory usage at 600MB (over 500MB limit)
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 600 * 1024 * 1024
        mock_psutil.Process.return_value = mock_process

        mock_eviction_callback = Mock()
        memory_manager.set_eviction_callback(mock_eviction_callback)

        result = memory_manager.enforce_memory_limits()

        assert result is False
        mock_eviction_callback.assert_called_once()
        # Verify eviction percentage is reasonable (between 10% and 100%)
        call_args = mock_eviction_callback.call_args[0][0]
        assert 0.1 <= call_args <= 1.0

    def test_get_available_memory(self, memory_manager, mock_psutil):
        """Verify calculation of available memory remaining."""
        # Mock memory usage at 300MB
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 300 * 1024 * 1024
        mock_psutil.Process.return_value = mock_process

        available_mb = memory_manager.get_available_memory()

        # Available = 500MB max - 300MB used = 200MB
        assert available_mb == 200

    def test_trigger_cache_eviction(self, memory_manager):
        """Verify manual cache eviction trigger works."""
        mock_eviction_callback = Mock()
        memory_manager.set_eviction_callback(mock_eviction_callback)

        memory_manager.trigger_cache_eviction(percentage=0.3)

        mock_eviction_callback.assert_called_once_with(0.3)

    def test_memory_pressure_detection(self, memory_manager, mock_psutil):
        """Verify memory pressure correctly detected at threshold."""
        mock_process = Mock()
        mock_psutil.Process.return_value = mock_process

        # Test under pressure threshold (80% of 500MB = 400MB)
        mock_process.memory_info.return_value.rss = 300 * 1024 * 1024
        assert memory_manager.is_under_pressure() is False

        # Test over pressure threshold
        mock_process.memory_info.return_value.rss = 450 * 1024 * 1024
        assert memory_manager.is_under_pressure() is True

    def test_emergency_eviction_percentage(self, memory_manager, mock_psutil):
        """Verify emergency eviction uses aggressive percentage."""
        # Mock memory usage way over limit (900MB vs 500MB limit)
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 900 * 1024 * 1024
        mock_psutil.Process.return_value = mock_process

        mock_eviction_callback = Mock()
        memory_manager.set_eviction_callback(mock_eviction_callback)

        memory_manager.enforce_memory_limits()

        # Emergency eviction should use at least 50% eviction
        call_args = mock_eviction_callback.call_args[0][0]
        assert call_args >= 0.5


class TestEmbeddingCacheManager:
    """Test suite for EmbeddingCacheManager component."""

    @pytest.fixture
    def cache_manager(self):
        """Create EmbeddingCacheManager instance."""
        return EmbeddingCacheManager(max_entries=100, ttl_seconds=3600)

    @pytest.fixture
    def sample_embedding(self):
        """Create sample embedding vector."""
        return np.random.rand(768).astype(np.float32)

    def test_cache_embedding(self, cache_manager, sample_embedding):
        """Verify embedding can be cached with text key."""
        text_key = "sample text for embedding"

        cache_manager.cache_embedding(text_key, sample_embedding)

        # Verify embedding is stored and retrievable
        cached = cache_manager.get_cached_embedding(text_key)
        assert cached is not None
        np.testing.assert_array_equal(cached, sample_embedding)

    def test_get_cached_embedding_hit(self, cache_manager, sample_embedding):
        """Verify cache hit returns cached embedding."""
        text_key = "cached text"
        cache_manager.cache_embedding(text_key, sample_embedding)

        # Reset stats to test hit counting
        cache_manager.reset_stats()

        cached = cache_manager.get_cached_embedding(text_key)

        assert cached is not None
        np.testing.assert_array_equal(cached, sample_embedding)
        stats = cache_manager.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 0

    def test_get_cached_embedding_miss(self, cache_manager):
        """Verify cache miss returns None."""
        cache_manager.reset_stats()

        cached = cache_manager.get_cached_embedding("nonexistent key")

        assert cached is None
        stats = cache_manager.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 1

    def test_evict_least_recently_used(self, cache_manager, sample_embedding):
        """Verify LRU eviction removes oldest accessed entries."""
        # Fill cache with max_entries + 1 items
        embeddings = {}
        for i in range(101):
            key = f"text_{i}"
            emb = np.random.rand(768).astype(np.float32)
            embeddings[key] = emb
            cache_manager.cache_embedding(key, emb)

        # First item should be evicted (LRU)
        assert cache_manager.get_cached_embedding("text_0") is None

        # Last items should still be present
        cached_99 = cache_manager.get_cached_embedding("text_99")
        assert cached_99 is not None
        np.testing.assert_array_equal(cached_99, embeddings["text_99"])

    def test_warm_cache(self, cache_manager):
        """Verify cache warming pre-loads common embeddings."""
        # Mock ChromaDB collection
        mock_collection = Mock()
        mock_docs = ["doc1", "doc2", "doc3"]
        mock_embeddings = [
            np.random.rand(768).astype(np.float32).tolist() for _ in range(3)
        ]
        mock_collection.get.return_value = {
            "documents": mock_docs,
            "embeddings": mock_embeddings,
        }

        cache_manager.warm_cache(mock_collection, case_ids=["case1", "case2", "case3"])

        # Verify cache contains warmed entries
        for i, doc in enumerate(mock_docs):
            cached = cache_manager.get_cached_embedding(doc)
            assert cached is not None

    def test_cache_size_limit(self, cache_manager):
        """Verify cache size limited to max_entries."""
        # Add more than max_entries (100)
        for i in range(150):
            emb = np.random.rand(768).astype(np.float32)
            cache_manager.cache_embedding(f"text_{i}", emb)

        stats = cache_manager.get_stats()
        assert stats["size"] <= 100

    def test_cache_ttl_expiration(self, cache_manager, sample_embedding):
        """Verify cached entries expire after TTL."""
        # Use short TTL for testing
        short_ttl_cache = EmbeddingCacheManager(max_entries=100, ttl_seconds=1)

        text_key = "expiring text"
        short_ttl_cache.cache_embedding(text_key, sample_embedding)

        # Should be cached immediately
        assert short_ttl_cache.get_cached_embedding(text_key) is not None

        # Wait for TTL expiration
        time.sleep(1.5)

        # Should be expired now
        assert short_ttl_cache.get_cached_embedding(text_key) is None

    def test_embedding_size_calculation(self, cache_manager, sample_embedding):
        """Verify embedding memory size calculated correctly."""
        size_bytes = cache_manager.calculate_embedding_size(sample_embedding)

        # 768 floats * 4 bytes per float32 = 3072 bytes
        expected_size = 768 * 4
        assert size_bytes == expected_size

        stats = cache_manager.get_stats()
        assert "total_size_mb" in stats


class TestMemoryPressureDetector:
    """Test suite for MemoryPressureDetector component."""

    @pytest.fixture
    def mock_psutil(self):
        """Mock psutil for pressure detection testing."""
        with patch("cbr_mcp_server.performance.memory_manager.psutil") as mock:
            yield mock

    @pytest.fixture
    def pressure_detector(self, mock_psutil):
        """Create MemoryPressureDetector instance."""
        mock_psutil.virtual_memory.return_value.total = 8 * 1024 * 1024 * 1024  # 8GB
        return MemoryPressureDetector(threshold_percent=80.0)

    def test_detect_pressure_under_threshold(self, pressure_detector, mock_psutil):
        """Verify no pressure detected under threshold."""
        # Mock memory usage at 60% (under 80% threshold)
        mock_mem = Mock()
        mock_mem.percent = 60.0
        mock_psutil.virtual_memory.return_value = mock_mem

        is_under_pressure = pressure_detector.check_pressure()

        assert is_under_pressure is False

    def test_detect_pressure_over_threshold(self, pressure_detector, mock_psutil):
        """Verify pressure detected when exceeding threshold."""
        # Mock memory usage at 85% (over 80% threshold)
        mock_mem = Mock()
        mock_mem.percent = 85.0
        mock_psutil.virtual_memory.return_value = mock_mem

        is_under_pressure = pressure_detector.check_pressure()

        assert is_under_pressure is True

    def test_pressure_callback_triggered(self, pressure_detector, mock_psutil):
        """Verify callback executed when pressure detected."""
        mock_callback = Mock()
        pressure_detector.set_pressure_callback(mock_callback)

        # Mock high memory usage
        mock_mem = Mock()
        mock_mem.percent = 90.0
        mock_psutil.virtual_memory.return_value = mock_mem

        pressure_detector.check_pressure()

        # Callback should be called with pressure level
        mock_callback.assert_called_once()
        call_args = mock_callback.call_args[0][0]
        assert call_args == 90.0

    def test_continuous_monitoring(self, pressure_detector, mock_psutil):
        """Verify continuous monitoring thread works."""
        mock_callback = Mock()
        pressure_detector.set_pressure_callback(mock_callback)

        # Mock memory usage progression
        mock_mem = Mock()
        mock_mem.percent = 85.0  # Over threshold
        mock_psutil.virtual_memory.return_value = mock_mem

        # Start monitoring with short interval
        pressure_detector.start_monitoring(interval_seconds=0.1)

        # Wait for at least one monitoring cycle
        time.sleep(0.3)

        # Stop monitoring
        pressure_detector.stop_monitoring()

        # Callback should have been called at least once
        assert mock_callback.call_count >= 1
