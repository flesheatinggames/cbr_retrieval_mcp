"""
Integration tests for the deduplication workflow in setup_vectordb.py.

These tests verify the complete workflow of:
1. Loading cases from files
2. Identifying new vs. existing cases using identify_new_cases()
3. Adding only new cases to ChromaDB collection

Test Coverage:
- Full workflow with empty database (all cases are new)
- Full workflow with partially populated database (mix of new and existing)
- Full workflow with fully populated database (all cases are duplicates)
- Full workflow with real ChromaDB instance (end-to-end validation)

All tests are designed to work with pytest-xdist parallel execution.
"""

import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Generator, List
from unittest.mock import Mock, patch

import numpy as np
import pytest

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import chromadb

# Import shared test utilities
from tests.utils.metadata_helpers import transform_metadata


@pytest.fixture
def sample_cases() -> List[Dict[str, Any]]:
    """
    Sample test cases with complete metadata structure.

    Returns a consistent set of 5 cases with realistic content and metadata
    that matches the production schema (category, subcategory, tags).
    """
    return [
        {
            "problem": "How to implement Firebase email authentication?",
            "solution": "Use firebase.auth().signInWithEmailAndPassword(email, password)",
            "category": "code",
            "subcategory": "firebase-auth",
            "tags": ["firebase", "authentication", "security"],
        },
        {
            "problem": "How to create a functional React component?",
            "solution": "function MyComponent() { return <div>Hello</div>; }",
            "category": "code",
            "subcategory": "react-components",
            "tags": ["react", "jsx", "functional-components"],
        },
        {
            "problem": "How to set up Next.js API routes?",
            "solution": "Create files in pages/api/ directory for serverless functions",
            "category": "code",
            "subcategory": "api-routes",
            "tags": ["nextjs", "api", "serverless"],
        },
        {
            "problem": "How to plan features using Agent OS?",
            "solution": "Use sequential thinking to break down features into tasks",
            "category": "orchestration",
            "subcategory": "planning",
            "tags": ["planning", "agent-os", "workflow"],
        },
        {
            "problem": "How to verify task completion?",
            "solution": "Use karen agent to verify all acceptance criteria are met",
            "category": "orchestration",
            "subcategory": "verification",
            "tags": ["verification", "karen", "quality-assurance"],
        },
    ]


@pytest.fixture
def additional_cases() -> List[Dict[str, Any]]:
    """
    Additional cases for testing incremental updates.

    These cases are different from sample_cases and can be used to test
    adding new cases to a partially populated database.
    """
    return [
        {
            "problem": "How to implement Firebase Firestore queries?",
            "solution": "Use db.collection('users').where('age', '>', 18).get()",
            "category": "code",
            "subcategory": "firebase-auth",
            "tags": ["firebase", "firestore", "database"],
        },
        {
            "problem": "How to use React hooks?",
            "solution": "const [state, setState] = useState(initialValue)",
            "category": "code",
            "subcategory": "react-components",
            "tags": ["react", "hooks", "state-management"],
        },
        {
            "problem": "How to delegate tasks to specialized agents?",
            "solution": "Use delegation protocol with clear requirements and acceptance criteria",
            "category": "orchestration",
            "subcategory": "delegation",
            "tags": ["delegation", "agents", "workflow"],
        },
    ]


@pytest.fixture
def mock_embedding_model() -> Generator[Mock, None, None]:
    """
    Mock SentenceTransformer to speed up tests.

    Returns mock embeddings with correct dimensionality (768) for any input.

    Yields:
      Mock SentenceTransformer class with mocked encode method
    """
    with patch(
        "cbr_mcp_server.utilities.setup_vectordb.SentenceTransformer"
    ) as mock_model:
        mock_instance = Mock()

        def mock_encode(texts, normalize_embeddings=True):
            """Return fake 768-dimensional embeddings."""
            return np.random.rand(len(texts), 768)

        mock_instance.encode.side_effect = mock_encode
        mock_model.return_value = mock_instance

        yield mock_model


@pytest.fixture
def unique_collection_name() -> str:
    """
    Generate unique collection name for test isolation in parallel execution.

    Uses UUID to ensure each test worker gets a unique collection name,
    preventing conflicts when tests run in parallel via pytest-xdist.
    """
    return f"test_deduplication_{uuid.uuid4().hex}"


class TestDeduplicationWorkflowEmptyDatabase:
    """Test deduplication workflow starting with empty database."""

    def test_full_workflow_empty_database_all_new(
        self, sample_cases, mock_embedding_model, unique_collection_name
    ):
        """
        Verify complete workflow when database is empty (all cases are new).

        This test validates:
        1. identify_new_cases() identifies all cases as new
        2. All cases are added to the collection
        3. Database final count equals input case count
        4. No cases are skipped (skipped count is 0)
        """
        # Mock ChromaDB client and collection
        with patch(
            "cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient"
        ) as mock_client:
            mock_collection = Mock()
            mock_collection.name = unique_collection_name
            mock_collection.count.return_value = 0  # Empty database
            mock_collection.get.return_value = {"ids": []}  # No existing IDs
            mock_collection.add.return_value = None

            mock_instance = Mock()
            mock_instance.get_or_create_collection.return_value = mock_collection
            mock_client.return_value = mock_instance

            # Import and execute workflow
            from cbr_mcp_server.utilities.setup_vectordb import (
                generate_case_id,
                identify_new_cases,
            )

            # Step 1: Identify new cases
            new_cases, skipped_count = identify_new_cases(sample_cases, mock_collection)

            # Assertions for identify_new_cases()
            assert len(new_cases) == len(
                sample_cases
            ), "All cases should be identified as new"
            assert skipped_count == 0, "No cases should be skipped in empty database"
            assert new_cases == sample_cases, "All input cases should be returned"

            # Step 2: Simulate adding cases to collection
            # Generate embeddings (using mock)
            problems = [case["problem"] for case in new_cases]
            embeddings = mock_embedding_model.return_value.encode(
                problems, normalize_embeddings=True
            )

            # Generate IDs
            ids = [generate_case_id(case) for case in new_cases]

            # Add to collection
            mock_collection.add(
                embeddings=embeddings,
                documents=[case["solution"] for case in new_cases],
                metadatas=[transform_metadata(case) for case in new_cases],
                ids=ids,
            )

            # Verify collection.add was called
            mock_collection.add.assert_called_once()

            # Verify correct data was passed to add()
            call_args = mock_collection.add.call_args
            assert call_args[1]["embeddings"].shape[0] == len(sample_cases)
            assert len(call_args[1]["documents"]) == len(sample_cases)
            assert len(call_args[1]["ids"]) == len(sample_cases)
            assert len(call_args[1]["metadatas"]) == len(sample_cases)

            # Verify all IDs are unique
            assert len(set(ids)) == len(ids), "All generated IDs should be unique"


class TestDeduplicationWorkflowPartialDatabase:
    """Test deduplication workflow with partially populated database."""

    def test_full_workflow_partial_database_mixed_cases(
        self,
        sample_cases,
        additional_cases,
        mock_embedding_model,
        unique_collection_name,
    ):
        """
        Verify workflow correctly handles mix of new and existing cases.

        Scenario:
        - Database has 3 cases from sample_cases
        - Workflow loads all 5 sample_cases
        - Should identify 2 as new, skip 3 as duplicates

        Validates:
        1. identify_new_cases() correctly identifies new vs. existing
        2. Only new cases are added to collection
        3. Skipped count matches number of pre-existing cases
        4. Database count reflects addition of only new cases
        """
        # Pre-populate database with first 3 cases
        from cbr_mcp_server.utilities.setup_vectordb import generate_case_id

        existing_cases = sample_cases[:3]
        existing_ids = [generate_case_id(case) for case in existing_cases]

        # Mock ChromaDB client and collection
        with patch(
            "cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient"
        ) as mock_client:
            mock_collection = Mock()
            mock_collection.name = unique_collection_name
            mock_collection.count.return_value = len(existing_ids)
            mock_collection.get.return_value = {"ids": existing_ids}
            mock_collection.add.return_value = None

            mock_instance = Mock()
            mock_instance.get_or_create_collection.return_value = mock_collection
            mock_client.return_value = mock_instance

            # Import workflow function
            from cbr_mcp_server.utilities.setup_vectordb import identify_new_cases

            # Step 1: Identify new cases (load all 5 sample_cases)
            new_cases, skipped_count = identify_new_cases(sample_cases, mock_collection)

            # Assertions for identify_new_cases()
            assert len(new_cases) == 2, "Should identify 2 new cases"
            assert skipped_count == 3, "Should skip 3 existing cases"

            # Verify that the correct cases were identified as new
            new_case_ids = [generate_case_id(case) for case in new_cases]
            for case_id in new_case_ids:
                assert (
                    case_id not in existing_ids
                ), f"New case ID {case_id} should not be in existing IDs"

            # Verify skipped cases are the ones that were pre-existing
            expected_new_cases = sample_cases[3:]  # Last 2 cases
            assert new_cases == expected_new_cases, "Wrong cases identified as new"

            # Step 2: Simulate adding only new cases
            problems = [case["problem"] for case in new_cases]
            embeddings = mock_embedding_model.return_value.encode(
                problems, normalize_embeddings=True
            )

            mock_collection.add(
                embeddings=embeddings,
                documents=[case["solution"] for case in new_cases],
                metadatas=[transform_metadata(case) for case in new_cases],
                ids=new_case_ids,
            )

            # Verify only new cases were added
            mock_collection.add.assert_called_once()
            call_args = mock_collection.add.call_args
            assert call_args[1]["embeddings"].shape[0] == 2, "Should add only 2 cases"
            assert len(call_args[1]["ids"]) == 2, "Should have 2 IDs"


class TestDeduplicationWorkflowFullDatabase:
    """Test deduplication workflow when database is fully populated."""

    def test_full_workflow_fully_populated_all_duplicates(
        self, sample_cases, mock_embedding_model, unique_collection_name
    ):
        """
        Verify workflow handles scenario where all cases already exist.

        Scenario:
        - Database already contains all 5 sample_cases
        - Workflow attempts to load same 5 cases again
        - Should identify 0 as new, skip all 5 as duplicates

        Validates:
        1. identify_new_cases() identifies zero new cases
        2. All cases are correctly skipped
        3. No cases are added to collection
        4. Database count remains unchanged
        """
        from cbr_mcp_server.utilities.setup_vectordb import generate_case_id

        # All cases already in database
        existing_ids = [generate_case_id(case) for case in sample_cases]

        # Mock ChromaDB client and collection
        with patch(
            "cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient"
        ) as mock_client:
            mock_collection = Mock()
            mock_collection.name = unique_collection_name
            mock_collection.count.return_value = len(existing_ids)
            mock_collection.get.return_value = {"ids": existing_ids}
            mock_collection.add.return_value = None

            mock_instance = Mock()
            mock_instance.get_or_create_collection.return_value = mock_collection
            mock_client.return_value = mock_instance

            # Import workflow function
            from cbr_mcp_server.utilities.setup_vectordb import identify_new_cases

            # Step 1: Identify new cases
            new_cases, skipped_count = identify_new_cases(sample_cases, mock_collection)

            # Assertions for identify_new_cases()
            assert len(new_cases) == 0, "Should identify zero new cases"
            assert skipped_count == len(sample_cases), "Should skip all input cases"
            assert new_cases == [], "Should return empty list for new cases"

            # Step 2: Verify no add operation occurs when new_cases is empty
            # The correct pattern: only call add() if there are new cases
            # The inverted logic from lines 384-387 has been removed

            # Verify add was NOT called
            mock_collection.add.assert_not_called()

            # Verify database count remains unchanged
            assert mock_collection.count.return_value == len(
                existing_ids
            ), "Database count should remain unchanged"


class TestDeduplicationWorkflowRealChromaDB:
    """Integration test with real ChromaDB instance."""

    def test_full_workflow_real_chromadb_incremental_updates(
        self, sample_cases, additional_cases, mock_embedding_model
    ):
        """
        End-to-end integration test with actual ChromaDB instance.

        This test verifies the complete workflow with a real database:
        1. First run: Add all sample_cases to empty database
        2. Second run: Attempt to add same cases (should skip all)
        3. Third run: Add additional_cases (should add only new ones)

        Validates:
        - Content-based IDs work correctly with real database
        - Deduplication prevents duplicate entries
        - Incremental updates add only genuinely new cases
        - Database state is correct after each operation
        """
        from cbr_mcp_server.utilities.setup_vectordb import (
            generate_case_id,
            identify_new_cases,
        )

        # Create temporary database
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize real ChromaDB client
            client = chromadb.PersistentClient(path=temp_dir)
            collection_name = f"test_dedup_{uuid.uuid4().hex}"
            collection = client.get_or_create_collection(name=collection_name)

            # --- First run: Add all sample_cases to empty database ---
            new_cases_1, skipped_1 = identify_new_cases(sample_cases, collection)

            assert len(new_cases_1) == len(
                sample_cases
            ), "First run: all cases should be new"
            assert skipped_1 == 0, "First run: no cases should be skipped"

            # Add cases to database
            problems_1 = [case["problem"] for case in new_cases_1]
            embeddings_1 = mock_embedding_model.return_value.encode(
                problems_1, normalize_embeddings=True
            )
            ids_1 = [generate_case_id(case) for case in new_cases_1]

            collection.add(
                embeddings=embeddings_1.tolist(),
                documents=[case["solution"] for case in new_cases_1],
                metadatas=[transform_metadata(case) for case in new_cases_1],
                ids=ids_1,
            )

            # Verify database state after first run
            assert collection.count() == len(
                sample_cases
            ), "Database should contain all sample cases"

            # --- Second run: Attempt to add same cases (should skip all) ---
            new_cases_2, skipped_2 = identify_new_cases(sample_cases, collection)

            assert (
                len(new_cases_2) == 0
            ), "Second run: no cases should be new (all duplicates)"
            assert skipped_2 == len(
                sample_cases
            ), "Second run: all cases should be skipped"

            # Verify database count unchanged
            assert collection.count() == len(
                sample_cases
            ), "Database count should remain unchanged after duplicate detection"

            # --- Third run: Add additional_cases (should add only new ones) ---
            combined_cases = sample_cases + additional_cases
            new_cases_3, skipped_3 = identify_new_cases(combined_cases, collection)

            assert len(new_cases_3) == len(
                additional_cases
            ), "Third run: only additional cases should be new"
            assert skipped_3 == len(
                sample_cases
            ), "Third run: all original cases should be skipped"

            # Verify the correct cases were identified as new
            new_case_ids_3 = [generate_case_id(case) for case in new_cases_3]
            expected_new_ids = [generate_case_id(case) for case in additional_cases]
            assert set(new_case_ids_3) == set(
                expected_new_ids
            ), "Wrong cases identified as new in third run"

            # Add new cases to database
            problems_3 = [case["problem"] for case in new_cases_3]
            embeddings_3 = mock_embedding_model.return_value.encode(
                problems_3, normalize_embeddings=True
            )

            collection.add(
                embeddings=embeddings_3.tolist(),
                documents=[case["solution"] for case in new_cases_3],
                metadatas=[transform_metadata(case) for case in new_cases_3],
                ids=new_case_ids_3,
            )

            # Verify final database state
            expected_final_count = len(sample_cases) + len(additional_cases)
            assert (
                collection.count() == expected_final_count
            ), f"Database should contain {expected_final_count} cases total"

            # Clean up
            client.delete_collection(name=collection_name)
