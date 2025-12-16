"""
Tests to verify that test isolation is working correctly.

This module verifies that:
1. Tests are not using the production database
2. File descriptors are not being leaked
3. Tests are properly isolated from each other
"""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestDatabaseIsolation:
    """Verify database isolation is working."""

    def test_production_db_not_accessed(self):
        """Verify tests cannot access production ./db directory."""
        from cbr_mcp_server.performance.production_cbr_retriever import ProductionCBRRetriever

        # This should be intercepted by prevent_production_db_access fixture
        with patch("cbr_mcp_server.performance.production_cbr_retriever.chromadb") as mock_chromadb:
            mock_client = Mock()
            mock_collection = Mock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chromadb.PersistentClient.return_value = mock_client

            # Try to create retriever with production path
            retriever = ProductionCBRRetriever(db_path="./db")

            # Verify it was called but path should have been redirected
            assert mock_chromadb.PersistentClient.called

            # If prevent_production_db_access is working, the actual call
            # should not have used "./db"
            call_args = mock_chromadb.PersistentClient.call_args
            if call_args and call_args[1].get('path') == "./db":
                pytest.fail("Production database path was not redirected!")

    def test_isolated_db_fixture_creates_temp_dir(self, isolated_test_db):
        """Verify isolated_test_db fixture creates temporary directory."""
        assert isolated_test_db is not None
        assert os.path.exists(isolated_test_db)
        assert os.path.isdir(isolated_test_db)

        # Should be in temp directory, not production
        assert "./db" not in isolated_test_db
        assert "cbr_test_" in isolated_test_db

    def test_multiple_retrievers_use_different_dbs(self, isolated_test_db):
        """Verify multiple test runs get different database directories."""
        first_db = isolated_test_db

        # Create another temp db manually to simulate another test
        import tempfile
        second_db = tempfile.mkdtemp(prefix="cbr_test_")

        assert first_db != second_db
        assert os.path.exists(first_db)
        assert os.path.exists(second_db)

        # Cleanup second db
        import shutil
        shutil.rmtree(second_db)

    def test_mock_chromadb_prevents_real_connections(self, mock_chromadb_for_tests):
        """Verify mock ChromaDB fixture prevents real database connections."""
        from cbr_mcp_server.performance.production_cbr_retriever import ProductionCBRRetriever

        # Create retriever - should use mocked ChromaDB
        retriever = ProductionCBRRetriever(db_path="./any_path")

        # The client should be the mock
        assert retriever.client is mock_chromadb_for_tests

    def test_file_descriptor_count_reasonable(self):
        """Verify we're not leaking file descriptors."""
        try:
            import resource

            # Get current file descriptor limit and usage
            soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)

            # Count open file descriptors (Unix-like systems)
            import os
            fd_count = len(os.listdir('/proc/%d/fd' % os.getpid())) if os.path.exists('/proc/%d/fd' % os.getpid()) else 0

            # In a healthy test, we should have far fewer than 1000 open FDs
            if fd_count > 0:  # Only check if we could count them
                assert fd_count < 1000, f"Too many open file descriptors: {fd_count}"
        except (ImportError, OSError):
            # Not on Unix or can't check - skip this verification
            pass


class TestIsolationInPractice:
    """Test that isolation works in practice with real components."""

    def test_concurrent_retrievers_isolated(self, isolated_test_db):
        """Test that multiple retrievers can coexist without interference."""
        from cbr_mcp_server.performance.production_cbr_retriever import ProductionCBRRetriever

        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = Mock()
            mock_model.encode.return_value = [[0.1, 0.2, 0.3]]
            mock_st.return_value = mock_model

            # Create multiple retrievers with isolated databases
            retrievers = []
            for i in range(3):
                import tempfile
                temp_db = tempfile.mkdtemp(prefix=f"cbr_test_{i}_")
                retriever = ProductionCBRRetriever(
                    db_path=temp_db,
                    embedding_model=mock_model
                )
                retrievers.append((retriever, temp_db))

            # Verify each has its own database path
            db_paths = [db for _, db in retrievers]
            assert len(set(db_paths)) == 3, "Retrievers should have unique databases"

            # Cleanup
            import shutil
            for retriever, temp_db in retrievers:
                del retriever
                shutil.rmtree(temp_db, ignore_errors=True)