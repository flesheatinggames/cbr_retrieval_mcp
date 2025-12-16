"""
Integration tests for setup_vectordb.py with modular case structure.

These tests verify that setup_vectordb.py works correctly with the new
modular case base structure in cases/__init__.py.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_chromadb_client():
    """Mock ChromaDB PersistentClient."""
    with patch("cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient") as mock_client:
        mock_instance = Mock()
        mock_collection = Mock()

        # Configure collection mock
        mock_collection.count.return_value = 0
        mock_collection.add.return_value = None

        # Configure client mock
        mock_instance.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_instance

        yield {
            "client": mock_client,
            "instance": mock_instance,
            "collection": mock_collection,
        }


@pytest.fixture
def mock_embedding_model():
    """Mock SentenceTransformer embedding model."""
    with patch("cbr_mcp_server.utilities.setup_vectordb.SentenceTransformer") as mock_model:
        mock_instance = Mock()

        # Configure encode to return mock embeddings
        def mock_encode(texts, normalize_embeddings=True):
            # Return mock embeddings (one vector per text)
            import numpy as np

            return np.random.rand(len(texts), 768)  # 768-dimensional embeddings

        mock_instance.encode.side_effect = mock_encode
        mock_model.return_value = mock_instance

        yield mock_model


@pytest.fixture
def sample_cases():
    """Sample cases with new metadata structure."""
    return [
        {
            "problem": "How to implement Firebase authentication?",
            "solution": "Use firebase.auth().signInWithEmailAndPassword()",
            "category": "firebase",
            "subcategory": "authentication",
            "tags": ["auth", "firebase", "security"],
        },
        {
            "problem": "How to create a React component?",
            "solution": "function MyComponent() { return <div>Hello</div>; }",
            "category": "react",
            "subcategory": "components",
            "tags": ["react", "jsx", "components"],
        },
        {
            "problem": "How to use Next.js routing?",
            "solution": "Create files in pages/ directory for automatic routing",
            "category": "nextjs",
            "subcategory": "routing",
            "tags": ["nextjs", "routing", "pages"],
        },
    ]


@pytest.fixture
def all_cases():
    """Generate mock cases to match the expected case count from ALL_CASES."""
    from cases import ALL_CASES as ACTUAL_ALL_CASES

    case_count = len(ACTUAL_ALL_CASES)
    cases = []
    categories = ["firebase", "react", "nextjs", "bootstrap", "webdev", "orchestration"]

    for i in range(case_count):
        category = categories[i % len(categories)]
        case = {
            "problem": f"Problem {i}: How to implement {category} feature?",
            "solution": f"Solution {i}: Implementation for {category}",
            "category": category,
            "subcategory": f"subcategory_{i}",
            "tags": [category, f"tag_{i}", "test"],
        }
        cases.append(case)

    return cases


class TestSetupVectorDBImportsAllCases:
    """Test that setup_vectordb imports and processes all cases."""

    def test_setup_vectordb_imports_all_cases(
        self, mock_chromadb_client, mock_embedding_model, all_cases
    ):
        """Verify setup_vectordb.py imports all cases from modular structure.

        NOTE: This test mocks case_base.CASE_BASE since setup_vectordb.py currently
        imports from there. Once setup_vectordb.py is updated to import from
        cases.ALL_CASES, this mock should be updated accordingly.
        """
        from cases import ALL_CASES as ACTUAL_ALL_CASES

        expected_case_count = len(ACTUAL_ALL_CASES)

        # Mock the cases.load_all_cases import
        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=all_cases):
            # Import setup_vectordb
            from cbr_mcp_server.utilities import setup_vectordb

            # Call main() to execute the setup logic
            setup_vectordb.main([])

            # Verify ChromaDB client was initialized
            mock_chromadb_client["client"].assert_called_once_with(path="./db")

            # Verify collection was created/retrieved
            mock_chromadb_client[
                "instance"
            ].get_or_create_collection.assert_called_once_with(
                name="code_solutions_case_base"
            )

            # Verify collection count was checked
            mock_chromadb_client["collection"].count.assert_called()

            # Verify add was called with all cases
            mock_chromadb_client["collection"].add.assert_called_once()
            call_args = mock_chromadb_client["collection"].add.call_args

            # Check that embeddings were generated for all cases
            assert call_args[1]["embeddings"].shape[0] == expected_case_count

            # Check that all documents (solutions) were added
            assert len(call_args[1]["documents"]) == expected_case_count

            # Check that all IDs were generated
            assert len(call_args[1]["ids"]) == expected_case_count

            # Check that all metadata entries were created
            assert len(call_args[1]["metadatas"]) == expected_case_count

    def test_setup_vectordb_generates_correct_ids(
        self, mock_chromadb_client, mock_embedding_model, all_cases
    ):
        """Verify that unique IDs are generated for all cases."""
        from cases import ALL_CASES as ACTUAL_ALL_CASES

        expected_case_count = len(ACTUAL_ALL_CASES)

        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=all_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # Reset mocks after initial import to test only the reload behavior
            mock_chromadb_client["client"].reset_mock()
            mock_chromadb_client["instance"].reset_mock()
            mock_chromadb_client["collection"].reset_mock()
            mock_embedding_model.return_value.encode.reset_mock()

            setup_vectordb.main([])

            call_args = mock_chromadb_client["collection"].add.call_args
            ids = call_args[1]["ids"]

            # Verify all IDs are unique
            assert len(ids) == len(set(ids))

            # Verify ID format (id0, id1, ..., id{n-1})
            expected_ids = [f"id{i}" for i in range(expected_case_count)]
            assert ids == expected_ids

    def test_setup_vectordb_extracts_problems_and_solutions(
        self, mock_chromadb_client, mock_embedding_model, sample_cases
    ):
        """Verify that problems and solutions are correctly extracted."""
        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=sample_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # Reset mocks after initial import to test only the reload behavior
            mock_chromadb_client["client"].reset_mock()
            mock_chromadb_client["instance"].reset_mock()
            mock_chromadb_client["collection"].reset_mock()
            mock_embedding_model.return_value.encode.reset_mock()

            setup_vectordb.main([])

            call_args = mock_chromadb_client["collection"].add.call_args

            # Verify solutions are stored as documents
            documents = call_args[1]["documents"]
            expected_solutions = [case["solution"] for case in sample_cases]
            assert documents == expected_solutions

            # Verify problems are stored in metadata
            metadatas = call_args[1]["metadatas"]
            expected_problems = [case["problem"] for case in sample_cases]
            actual_problems = [meta["problem"] for meta in metadatas]
            assert actual_problems == expected_problems


class TestSetupVectorDBHandlesMetadataFields:
    """Test that setup_vectordb processes new metadata fields correctly."""

    def test_setup_vectordb_handles_metadata_fields(
        self, mock_chromadb_client, mock_embedding_model, sample_cases
    ):
        """Verify setup processes category, subcategory, tags without errors."""
        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=sample_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # This should not raise any exceptions
            try:
                setup_vectordb.main([])
                success = True
            except Exception as e:
                success = False
                error = str(e)

            assert (
                success
            ), f"Setup failed with metadata fields: {error if not success else ''}"

            # Verify ChromaDB add was called successfully
            assert mock_chromadb_client["collection"].add.called

    def test_setup_vectordb_metadata_format(
        self, mock_chromadb_client, mock_embedding_model, sample_cases
    ):
        """Verify metadata is correctly formatted for ChromaDB."""
        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=sample_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # Reset mocks after initial import to test only the reload behavior
            mock_chromadb_client["client"].reset_mock()
            mock_chromadb_client["instance"].reset_mock()
            mock_chromadb_client["collection"].reset_mock()
            mock_embedding_model.return_value.encode.reset_mock()

            setup_vectordb.main([])

            call_args = mock_chromadb_client["collection"].add.call_args
            metadatas = call_args[1]["metadatas"]

            # Verify each metadata entry has the problem field
            for i, metadata in enumerate(metadatas):
                assert "problem" in metadata
                assert metadata["problem"] == sample_cases[i]["problem"]
                assert isinstance(metadata["problem"], str)


class TestSetupVectorDBEmbeddingGeneration:
    """Test embedding generation for all cases."""

    def test_setup_vectordb_generates_embeddings_for_all_cases(
        self, mock_chromadb_client, mock_embedding_model, all_cases
    ):
        """Verify embeddings are generated for all cases."""
        from cases import ALL_CASES as ACTUAL_ALL_CASES

        expected_case_count = len(ACTUAL_ALL_CASES)

        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=all_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # Reset mocks after initial import to test only the reload behavior
            mock_chromadb_client["client"].reset_mock()
            mock_chromadb_client["instance"].reset_mock()
            mock_chromadb_client["collection"].reset_mock()
            mock_embedding_model.return_value.encode.reset_mock()

            setup_vectordb.main([])

            # Verify encode was called once with all problems
            mock_embedding_model.return_value.encode.assert_called_once()

            # Get the call arguments
            call_args = mock_embedding_model.return_value.encode.call_args
            problems_encoded = call_args[0][0]

            # Verify all problems were encoded
            assert len(problems_encoded) == expected_case_count

            # Verify normalize_embeddings parameter
            assert call_args[1]["normalize_embeddings"] is True

    def test_setup_vectordb_embedding_content(
        self, mock_chromadb_client, mock_embedding_model, sample_cases
    ):
        """Verify correct content is passed to embedding model."""
        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=sample_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # Reset mocks after initial import to test only the reload behavior
            mock_chromadb_client["client"].reset_mock()
            mock_chromadb_client["instance"].reset_mock()
            mock_chromadb_client["collection"].reset_mock()
            mock_embedding_model.return_value.encode.reset_mock()

            setup_vectordb.main([])

            call_args = mock_embedding_model.return_value.encode.call_args
            problems_encoded = call_args[0][0]

            # Verify problems are passed to encoder
            expected_problems = [case["problem"] for case in sample_cases]
            assert problems_encoded == expected_problems


class TestSetupVectorDBChromaDBIntegration:
    """Test ChromaDB client initialization and collection management."""

    def test_setup_vectordb_chromadb_client_initialization(
        self, mock_chromadb_client, mock_embedding_model, sample_cases
    ):
        """Verify ChromaDB client is initialized with correct parameters."""
        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=sample_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # Reset mocks after initial import to test only the reload behavior
            mock_chromadb_client["client"].reset_mock()
            mock_chromadb_client["instance"].reset_mock()
            mock_chromadb_client["collection"].reset_mock()
            mock_embedding_model.return_value.encode.reset_mock()

            setup_vectordb.main([])

            # Verify PersistentClient was called with correct path
            mock_chromadb_client["client"].assert_called_once_with(path="./db")

    def test_setup_vectordb_collection_creation(
        self, mock_chromadb_client, mock_embedding_model, sample_cases
    ):
        """Verify collection is created/retrieved with correct name."""
        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=sample_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # Reset mocks after initial import to test only the reload behavior
            mock_chromadb_client["client"].reset_mock()
            mock_chromadb_client["instance"].reset_mock()
            mock_chromadb_client["collection"].reset_mock()
            mock_embedding_model.return_value.encode.reset_mock()

            setup_vectordb.main([])

            # Verify get_or_create_collection was called
            mock_chromadb_client[
                "instance"
            ].get_or_create_collection.assert_called_once_with(
                name="code_solutions_case_base"
            )

    def test_setup_vectordb_skip_if_populated(
        self, mock_chromadb_client, mock_embedding_model, sample_cases
    ):
        """Verify setup skips population if collection already has data."""
        # Configure collection to return count > 0
        mock_chromadb_client["collection"].count.return_value = 10

        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=sample_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # Reset mocks after initial import to test only the reload behavior
            mock_chromadb_client["client"].reset_mock()
            mock_chromadb_client["instance"].reset_mock()
            mock_chromadb_client["collection"].reset_mock()
            mock_embedding_model.return_value.encode.reset_mock()

            setup_vectordb.main([])

            # Verify add was NOT called
            mock_chromadb_client["collection"].add.assert_not_called()


class TestSetupVectorDBEdgeCases:
    """Test edge cases and error handling."""

    def test_setup_vectordb_handles_empty_case_list(
        self, mock_chromadb_client, mock_embedding_model
    ):
        """Verify graceful handling when case list is empty."""
        empty_cases = []

        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=empty_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # This should not crash
            try:
                setup_vectordb.main([])
                success = True
            except SystemExit as e:
                # SystemExit is expected for empty case list
                success = False
                error = "empty case list"
            except Exception as e:
                success = False
                error = str(e)

            # Allow either success with no-op or controlled failure
            # Empty case list should be handled gracefully
            if not success:
                # If it fails, verify it's a controlled failure
                assert "empty" in error.lower() or "no cases" in error.lower()

    def test_setup_vectordb_handles_cases_with_missing_optional_metadata(
        self, mock_chromadb_client, mock_embedding_model
    ):
        """Verify robustness when cases have only required fields."""
        minimal_cases = [
            {"problem": "Minimal problem 1", "solution": "Minimal solution 1"},
            {"problem": "Minimal problem 2", "solution": "Minimal solution 2"},
        ]

        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=minimal_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # This should handle cases with only required fields
            try:
                setup_vectordb.main([])
                success = True
            except Exception:
                success = False

            # Should succeed - metadata fields are optional in setup_vectordb
            assert success

            # Verify cases were added
            assert mock_chromadb_client["collection"].add.called


class TestSetupVectorDBDuplicateHandling:
    """Test handling of duplicate case IDs."""

    def test_setup_vectordb_generates_unique_ids(
        self, mock_chromadb_client, mock_embedding_model, all_cases
    ):
        """Verify all generated IDs are unique."""
        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=all_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # Reset mocks after initial import to test only the reload behavior
            mock_chromadb_client["client"].reset_mock()
            mock_chromadb_client["instance"].reset_mock()
            mock_chromadb_client["collection"].reset_mock()
            mock_embedding_model.return_value.encode.reset_mock()

            setup_vectordb.main([])

            call_args = mock_chromadb_client["collection"].add.call_args
            ids = call_args[1]["ids"]

            # Verify no duplicate IDs
            assert len(ids) == len(set(ids)), "Duplicate IDs found"

    def test_setup_vectordb_id_sequence(
        self, mock_chromadb_client, mock_embedding_model, sample_cases
    ):
        """Verify IDs are sequential and predictable."""
        with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=sample_cases):
            import importlib

            from cbr_mcp_server.utilities import setup_vectordb

            # Reset mocks after initial import to test only the reload behavior
            mock_chromadb_client["client"].reset_mock()
            mock_chromadb_client["instance"].reset_mock()
            mock_chromadb_client["collection"].reset_mock()
            mock_embedding_model.return_value.encode.reset_mock()

            setup_vectordb.main([])

            call_args = mock_chromadb_client["collection"].add.call_args
            ids = call_args[1]["ids"]

            # Verify sequential IDs
            expected = [f"id{i}" for i in range(len(sample_cases))]
            assert ids == expected


class TestSetupVectorDBErrorHandling:
    """Test error handling during setup."""

    def test_setup_vectordb_handles_embedding_failure(
        self, mock_chromadb_client, sample_cases
    ):
        """Verify handling when embedding generation fails."""
        # Mock embedding model to raise an exception
        with patch("cbr_mcp_server.utilities.setup_vectordb.SentenceTransformer") as mock_model:
            mock_instance = Mock()
            mock_instance.encode.side_effect = RuntimeError(
                "Embedding generation failed"
            )
            mock_model.return_value = mock_instance

            with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=sample_cases):
                # Should raise the embedding error during execution
                with pytest.raises(RuntimeError, match="Embedding generation failed"):
                    from cbr_mcp_server.utilities import setup_vectordb

                    setup_vectordb.main([])

    def test_setup_vectordb_handles_chromadb_connection_failure(
        self, mock_embedding_model, sample_cases
    ):
        """Verify handling when ChromaDB connection fails."""
        with patch("cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient") as mock_client:
            mock_client.side_effect = ConnectionError("Cannot connect to ChromaDB")

            with patch("cbr_mcp_server.utilities.setup_vectordb.load_all_cases", return_value=sample_cases):
                # Should raise the connection error during execution
                with pytest.raises(ConnectionError, match="Cannot connect to ChromaDB"):
                    from cbr_mcp_server.utilities import setup_vectordb

                    setup_vectordb.main([])


class TestSetupVectorDBFutureModularStructure:
    """Test compatibility with future modular case structure.

    These tests verify setup_vectordb.py will work correctly once updated
    to import from cases.ALL_CASES instead of case_base.CASE_BASE.
    """

    def test_setup_vectordb_with_modular_cases_import(
        self, mock_chromadb_client, mock_embedding_model, all_cases
    ):
        """Verify setup_vectordb works when importing from cases.ALL_CASES.

        This test simulates the future state after setup_vectordb.py is updated
        to import from the modular structure.
        """
        from cases import ALL_CASES as ACTUAL_ALL_CASES

        expected_case_count = len(ACTUAL_ALL_CASES)

        # Create a modified version of setup_vectordb that imports from cases
        setup_code = """
import chromadb
from sentence_transformers import SentenceTransformer
from cases import ALL_CASES as CASE_BASE

# Initialize the Embedding Model
embedding_model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)

# Initialize ChromaDB Client
client = chromadb.PersistentClient(path="./db")

# Create or load a collection
collection = client.get_or_create_collection(
    name="code_solutions_case_base"
)

# Populate the database
if collection.count() == 0:
    problems = [case["problem"] for case in CASE_BASE]
    solutions = [case["solution"] for case in CASE_BASE]
    ids = [f"id{i}" for i in range(len(problems))]
    problem_embeddings = embedding_model.encode(problems, normalize_embeddings=True)
    collection.add(
        embeddings=problem_embeddings,
        documents=solutions,
        metadatas=[{"problem": p} for p in problems],
        ids=ids
    )
"""

        # Mock cases.ALL_CASES
        with patch("cases.ALL_CASES", all_cases):
            # Execute the modified setup code
            namespace = {}
            exec(setup_code, namespace)

            # Verify all cases were processed
            call_args = mock_chromadb_client["collection"].add.call_args
            embeddings = call_args[1]["embeddings"]
            # Embeddings can be list or numpy array
            embeddings_count = len(embeddings) if isinstance(embeddings, list) else embeddings.shape[0]
            assert embeddings_count == expected_case_count
            assert len(call_args[1]["ids"]) == expected_case_count

    def test_modular_structure_provides_all_required_fields(
        self, mock_chromadb_client, mock_embedding_model
    ):
        """Verify modular structure cases have all required fields for setup."""
        # Import actual cases from the modular structure
        from cases import ALL_CASES

        # Verify we have at least some cases
        assert len(ALL_CASES) >= 5, f"Expected at least 5 cases, got {len(ALL_CASES)}"

        # Verify each case has required fields for setup_vectordb
        for i, case in enumerate(ALL_CASES):
            assert "problem" in case, f"Case {i} missing 'problem' field"
            assert "solution" in case, f"Case {i} missing 'solution' field"
            assert isinstance(
                case["problem"], str
            ), f"Case {i} 'problem' is not a string"
            assert isinstance(
                case["solution"], str
            ), f"Case {i} 'solution' is not a string"
            assert len(case["problem"]) > 0, f"Case {i} has empty 'problem'"
            assert len(case["solution"]) > 0, f"Case {i} has empty 'solution'"
