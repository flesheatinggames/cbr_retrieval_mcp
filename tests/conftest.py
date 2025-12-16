"""Pytest configuration and global fixtures."""

import os
import warnings
import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, patch

import pytest

# Set environment variable to disable real model loading in tests
os.environ["TESTING"] = "true"
os.environ["CBR_USE_MOCK_MODEL"] = "true"

# Filter sqlite3 datetime adapter deprecation warnings
warnings.filterwarnings(
    "ignore", "The default datetime adapter is deprecated", DeprecationWarning
)


# Mock the SentenceTransformer at module level to prevent downloads
# NOTE: This mock is skipped for benchmark and load tests that need real embeddings
@pytest.fixture(scope="session", autouse=True)
def mock_sentence_transformer(request):
    """Mock SentenceTransformer to prevent model downloads during tests.

    Automatically skips mocking for test files containing 'benchmark' or 'load' in their path,
    as these are integration tests that need real embeddings.
    """
    # Skip mocking for benchmark and load integration tests
    # Check if any test items are from benchmark or load directory
    session = request.session
    test_paths = [str(item.path) for item in session.items]
    if any("benchmark" in path or "load" in path for path in test_paths):
        yield None
        return

    with patch("sentence_transformers.SentenceTransformer") as mock_st:
        # Create a mock instance that returns mock embeddings
        mock_instance = Mock()
        mock_instance.encode.return_value = [0.1, 0.2, 0.3]
        mock_st.return_value = mock_instance
        yield mock_st


@pytest.fixture(scope="session", autouse=True)
def disable_huggingface_hub():
    """Disable Hugging Face Hub downloads during tests."""
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    yield
    # Clean up after tests
    os.environ.pop("HF_HUB_OFFLINE", None)
    os.environ.pop("TRANSFORMERS_OFFLINE", None)


# ============================================================================
# Test Isolation Fixtures
# ============================================================================

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
def prevent_production_db_access(monkeypatch, request):
    """
    Automatically prevent tests from accidentally using ./db production database.

    This fixture is autouse=True, so it applies to all tests automatically.
    It intercepts ChromaDB PersistentClient creation and redirects production
    database paths to a safe temporary location.

    This works by wrapping the actual call site in ProductionCBRRetriever,
    ensuring path redirection happens even when tests patch chromadb.
    """
    # Skip for tests that explicitly opt out
    if "no_production_db_protection" in request.keywords:
        return

    try:
        from cbr_mcp_server.performance import production_cbr_retriever
    except ImportError:
        return  # Module not available

    # Store the original __init__ method
    original_init = production_cbr_retriever.ProductionCBRRetriever.__init__

    def safe_init(self, db_path: str, *args, **kwargs):
        """Intercept and redirect production database paths in __init__."""
        original_path = db_path
        if db_path and (db_path == "./db" or db_path == "db" or Path(db_path).name == "db"):
            # Redirect to a temporary directory
            temp_dir = tempfile.mkdtemp(prefix="cbr_intercepted_")
            import atexit
            atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
            db_path = temp_dir

        # Call original __init__ with potentially redirected path
        return original_init(self, db_path, *args, **kwargs)

    # Patch the __init__ method
    monkeypatch.setattr(
        production_cbr_retriever.ProductionCBRRetriever,
        "__init__",
        safe_init
    )


# ============================================================================
# Pytest-xdist Worker ID Fixture
# ============================================================================

@pytest.fixture
def worker_id(request):
    """
    Provide a unique worker ID for parallel test execution.

    When running with pytest-xdist (pytest -n auto), this returns the worker ID.
    When running normally, returns "master" to indicate single-process execution.

    This is useful for creating worker-specific resources (temp dirs, random seeds, etc.)
    to prevent race conditions during parallel test execution.

    Returns:
        str: Worker ID (e.g., "gw0", "gw1", ...) or "master" for non-parallel runs
    """
    if hasattr(request.config, 'workerinput'):
        # Running with pytest-xdist
        return request.config.workerinput['workerid']
    else:
        # Running without pytest-xdist (normal mode)
        return "master"
