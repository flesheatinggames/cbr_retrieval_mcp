"""Pytest configuration and global fixtures."""

import os
import warnings
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
@pytest.fixture(scope="session", autouse=True)
def mock_sentence_transformer():
    """Mock SentenceTransformer to prevent model downloads during tests."""
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
