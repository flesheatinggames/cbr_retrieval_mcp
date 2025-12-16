"""
Test isolation fixtures for CBR MCP Server tests.

This module provides fixtures to ensure proper test isolation,
preventing tests from using the production database and exhausting
file descriptors.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def isolated_test_db() -> Generator[str, None, None]:
    """
    Create an isolated test database directory for each test.

    This fixture:
    - Creates a unique temporary directory for ChromaDB
    - Ensures tests don't use the production ./db database
    - Automatically cleans up after the test

    Yields:
        str: Path to the temporary database directory
    """
    temp_dir = tempfile.mkdtemp(prefix="cbr_test_")
    yield temp_dir

    # Cleanup after test
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception:
        pass  # Best effort cleanup


@pytest.fixture
def mock_chromadb_for_tests():
    """
    Mock ChromaDB to prevent real database connections in unit tests.

    This fixture should be used for unit tests that don't need
    actual database functionality.
    """
    with patch("chromadb.PersistentClient") as mock_client_class:
        mock_client = Mock()
        mock_collection = Mock()

        # Setup standard mock responses
        mock_collection.query.return_value = {
            "ids": [["test-1", "test-2"]],
            "documents": [["doc1", "doc2"]],
            "metadatas": [[{"category": "test"}, {"category": "test"}]],
            "distances": [[0.1, 0.2]]
        }
        mock_collection.count.return_value = 2

        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client.get_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client

        yield mock_client


@pytest.fixture(autouse=True)
def prevent_production_db_access(monkeypatch):
    """
    Automatically prevent tests from accidentally using ./db production database.

    This fixture is autouse=True, so it applies to all tests automatically.
    It intercepts ChromaDB PersistentClient creation and redirects production
    database paths to a safe temporary location.
    """
    original_persistent_client = None

    try:
        import chromadb
        original_persistent_client = chromadb.PersistentClient
    except ImportError:
        return  # ChromaDB not installed, nothing to patch

    def safe_persistent_client(path=None, *args, **kwargs):
        """Intercept and redirect production database access."""
        if path and (path == "./db" or path == "db" or Path(path).name == "db"):
            # Redirect to a temporary directory
            temp_dir = tempfile.mkdtemp(prefix="cbr_intercepted_")
            import atexit
            atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
            path = temp_dir

        return original_persistent_client(path, *args, **kwargs)

    monkeypatch.setattr("chromadb.PersistentClient", safe_persistent_client)


@pytest.fixture
def production_cbr_retriever_isolated(isolated_test_db):
    """
    Create a ProductionCBRRetriever with an isolated test database.

    This fixture ensures the retriever uses a temporary database
    instead of the production ./db directory.
    """
    from cbr_mcp_server.performance.production_cbr_retriever import ProductionCBRRetriever

    # Create retriever with isolated database
    retriever = ProductionCBRRetriever(
        db_path=isolated_test_db,
        embedding_model=None  # Will use mock or minimal model
    )

    yield retriever

    # Cleanup: Close any connections
    if hasattr(retriever, 'client') and retriever.client:
        try:
            # ChromaDB doesn't have explicit close, but we can delete the reference
            retriever.client = None
            retriever.collection = None
        except Exception:
            pass