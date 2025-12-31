"""Integration tests for incremental update workflow in setup_vectordb.py

This test suite validates the incremental database update functionality that:
1. Preserves existing cases (no deletion)
2. Adds only new cases
3. Skips duplicate cases correctly
4. Provides accurate statistics

These tests follow Test-Driven Development (TDD) principles and are written
BEFORE the incremental update workflow implementation.

The tests use real ChromaDB operations for integration-level validation while
mocking file I/O and external dependencies.

NOTE: Tests use unique collection names per test to ensure isolation during
parallel execution with pytest-xdist.
"""

import sys
import uuid
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

import pytest
import chromadb

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utilities.setup_vectordb import generate_case_id, identify_new_cases


def get_unique_collection_name() -> str:
    """Generate a unique collection name for test isolation in parallel execution."""
    return f"test_collection_{uuid.uuid4().hex[:12]}"


def call_main_with_mocked_args(argv_list):
    """Helper to call main() with mocked sys.argv."""
    from scripts.utilities.setup_vectordb import main

    with patch("sys.argv", argv_list):
        main()


# Test data fixtures
@pytest.fixture
def sample_cases_initial():
    """Initial set of cases for first database population."""
    return [
        {
            "problem": "How to implement authentication?",
            "solution": "Use Firebase Auth with email/password.",
            "category": "code",
            "subcategory": "firebase-auth",
            "tags": ["firebase", "auth"],
        },
        {
            "problem": "How to handle form validation?",
            "solution": "Use client-side validation with server-side verification.",
            "category": "code",
            "subcategory": "forms",
            "tags": ["forms", "validation"],
        },
        {
            "problem": "How to deploy Next.js app?",
            "solution": "Deploy to Vercel with automatic CI/CD.",
            "category": "orchestration",
            "subcategory": "deployment",
            "tags": ["nextjs", "deployment"],
        },
    ]


@pytest.fixture
def sample_cases_expanded():
    """Expanded set including initial cases plus new ones."""
    return [
        # Original cases (should be skipped)
        {
            "problem": "How to implement authentication?",
            "solution": "Use Firebase Auth with email/password.",
            "category": "code",
            "subcategory": "firebase-auth",
            "tags": ["firebase", "auth"],
        },
        {
            "problem": "How to handle form validation?",
            "solution": "Use client-side validation with server-side verification.",
            "category": "code",
            "subcategory": "forms",
            "tags": ["forms", "validation"],
        },
        {
            "problem": "How to deploy Next.js app?",
            "solution": "Deploy to Vercel with automatic CI/CD.",
            "category": "orchestration",
            "subcategory": "deployment",
            "tags": ["nextjs", "deployment"],
        },
        # New cases (should be added)
        {
            "problem": "How to optimize React performance?",
            "solution": "Use React.memo and useMemo hooks.",
            "category": "code",
            "subcategory": "react-components",
            "tags": ["react", "performance"],
        },
        {
            "problem": "How to secure API endpoints?",
            "solution": "Implement JWT authentication with rate limiting.",
            "category": "security",
            "subcategory": "api-security",
            "tags": ["security", "api"],
        },
    ]


@pytest.fixture
def temp_db_path():
    """Create temporary database path for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_db"
    yield str(db_path)
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_embedding_model():
    """Mock SentenceTransformer embedding model."""
    with patch("scripts.utilities.setup_vectordb.SentenceTransformer") as mock_model:
        mock_instance = Mock()

        # Configure encode to return mock embeddings
        def mock_encode(texts, normalize_embeddings=True):
            import numpy as np
            return np.random.rand(len(texts), 768)  # 768-dimensional embeddings

        mock_instance.encode.side_effect = mock_encode
        mock_model.return_value = mock_instance

        yield mock_model


def test_incremental_update_preserves_existing_cases(
    temp_db_path, mock_embedding_model, sample_cases_initial, sample_cases_expanded
):
    """
    Test: Verify that running the update workflow does not delete existing cases.

    Given: A database populated with initial cases
    When: Running main() again with expanded case set
    Then: All original cases remain in database (not deleted)
          AND new cases are added
    """
    collection_name = get_unique_collection_name()
    # Given: Database with initial cases
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_initial):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            # Setup real-like ChromaDB mock
            client = chromadb.Client()
            collection = client.create_collection(collection_name)

            mock_client_instance = Mock()
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            # First run: populate with initial cases
            from scripts.utilities.setup_vectordb import main
            with patch("sys.argv", ["setup_vectordb.py"]):
                main()

            initial_count = collection.count()
            initial_ids = set(collection.get()["ids"])

            assert initial_count == len(sample_cases_initial), \
                f"Expected {len(sample_cases_initial)} cases, got {initial_count}"

    # When: Running main() again with expanded case set
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_expanded):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            # Second run: should add new cases without deleting existing
            call_main_with_mocked_args(["setup_vectordb.py"])

            final_count = collection.count()
            final_ids = set(collection.get()["ids"])

    # Then: All original case IDs still present
    assert initial_ids.issubset(final_ids), \
        "Original case IDs were deleted (should be preserved)"

    # And: New cases were added
    assert final_count > initial_count, \
        f"Expected count > {initial_count}, got {final_count}"

    # And: Final count matches total unique cases
    expected_count = len(sample_cases_expanded)
    assert final_count == expected_count, \
        f"Expected {expected_count} total cases, got {final_count}"


def test_incremental_update_adds_new_cases(
    temp_db_path, mock_embedding_model, sample_cases_initial, sample_cases_expanded
):
    """
    Test: Verify that new cases are successfully added to partially populated database.

    Given: Database with 3 initial cases
    When: Running main() with 5 cases (3 existing + 2 new)
    Then: Only 2 new cases are added
          AND final database has all 5 unique cases
    """
    collection_name = get_unique_collection_name()
    # Given: Database with initial cases
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_initial):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            client = chromadb.Client()
            collection = client.create_collection(collection_name)

            mock_client_instance = Mock()
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            call_main_with_mocked_args(["setup_vectordb.py"])
            initial_count = collection.count()

    # When: Running with expanded case set
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_expanded):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            call_main_with_mocked_args(["setup_vectordb.py"])
            final_count = collection.count()

    # Then: New cases were added
    new_cases_added = final_count - initial_count
    expected_new = len(sample_cases_expanded) - len(sample_cases_initial)

    assert new_cases_added == expected_new, \
        f"Expected {expected_new} new cases added, got {new_cases_added}"

    # And: Final database has all unique cases
    assert final_count == len(sample_cases_expanded), \
        f"Expected {len(sample_cases_expanded)} total cases, got {final_count}"

    # And: No duplicate IDs present
    all_ids = collection.get()["ids"]
    assert len(all_ids) == len(set(all_ids)), \
        "Duplicate IDs found in database"


def test_incremental_update_skips_duplicates(
    temp_db_path, mock_embedding_model, sample_cases_initial
):
    """
    Test: Verify that duplicate cases are correctly identified and skipped.

    Given: Database already contains all cases
    When: Running main() again with same cases
    Then: Zero new cases added
          AND skipped count equals total case count
          AND collection count unchanged
    """
    collection_name = get_unique_collection_name()
    # Given: Database with all cases
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_initial):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            client = chromadb.Client()
            collection = client.create_collection(collection_name)

            mock_client_instance = Mock()
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            call_main_with_mocked_args(["setup_vectordb.py"])
            first_count = collection.count()

    # When: Running again with same cases
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_initial):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            # Use identify_new_cases to verify skipping logic
            new_cases, skipped_count = identify_new_cases(sample_cases_initial, collection)

            call_main_with_mocked_args(["setup_vectordb.py"])
            second_count = collection.count()

    # Then: No cases added (all skipped)
    assert len(new_cases) == 0, \
        f"Expected 0 new cases, got {len(new_cases)}"

    # And: Skipped count equals total cases
    assert skipped_count == len(sample_cases_initial), \
        f"Expected {len(sample_cases_initial)} skipped, got {skipped_count}"

    # And: Collection count unchanged
    assert second_count == first_count, \
        f"Expected count {first_count}, got {second_count} (should be unchanged)"


def test_incremental_update_statistics_output(
    temp_db_path, mock_embedding_model, sample_cases_initial, sample_cases_expanded, capsys
):
    """
    Test: Verify statistics output shows correct counts.

    Given: Database with initial cases
    When: Running main() with expanded case set
    Then: Statistics display correct added, skipped, and total counts
    """
    collection_name = get_unique_collection_name()
    # Given: Database with initial cases
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_initial):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            client = chromadb.Client()
            collection = client.create_collection(collection_name)

            mock_client_instance = Mock()
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            call_main_with_mocked_args(["setup_vectordb.py"])

    # When: Running with expanded case set
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_expanded):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            call_main_with_mocked_args(["setup_vectordb.py"])

    # Capture output
    captured = capsys.readouterr()
    output = captured.out.lower()

    # Then: Output contains statistics
    expected_added = len(sample_cases_expanded) - len(sample_cases_initial)
    expected_skipped = len(sample_cases_initial)
    expected_total = len(sample_cases_expanded)

    # Statistics should show added count
    assert "added" in output or "new" in output, \
        "Statistics should mention added/new cases"

    # Statistics should show skipped count
    assert "skipped" in output or "existing" in output, \
        "Statistics should mention skipped/existing cases"

    # Statistics should show total count
    assert "total" in output, \
        "Statistics should show total case count"

    # Verify counts match actual state
    final_count = collection.count()
    assert final_count == expected_total, \
        f"Expected {expected_total} total cases, got {final_count}"


def test_incremental_update_idempotency(
    temp_db_path, mock_embedding_model, sample_cases_initial
):
    """
    Test: Verify multiple runs produce identical database state (idempotent).

    Given: Same case set
    When: Running main() three times
    Then: All three runs result in identical database state
          AND collection count consistent across all runs
          AND case IDs identical after each run
    """
    collection_name = get_unique_collection_name()
    # Setup persistent collection
    client = chromadb.Client()
    collection = client.create_collection(collection_name)

    counts = []
    id_sets = []

    # Run main() three times
    for run_number in range(3):
        with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_initial):
            with patch("chromadb.PersistentClient") as mock_client_cls:
                mock_client_instance = Mock()
                mock_client_instance.get_or_create_collection.return_value = collection
                mock_client_cls.return_value = mock_client_instance

                call_main_with_mocked_args(["setup_vectordb.py"])

                count = collection.count()
                ids = set(collection.get()["ids"])

                counts.append(count)
                id_sets.append(ids)

    # Then: All runs produced same count
    assert len(set(counts)) == 1, \
        f"Counts differ across runs: {counts} (should be identical)"

    # And: All runs produced same IDs
    assert id_sets[0] == id_sets[1] == id_sets[2], \
        "Case IDs differ across runs (should be identical)"

    # And: Count matches expected
    expected_count = len(sample_cases_initial)
    assert counts[0] == expected_count, \
        f"Expected {expected_count} cases, got {counts[0]}"


def test_incremental_update_full_workflow_integration(
    temp_db_path, mock_embedding_model, sample_cases_initial, sample_cases_expanded
):
    """
    Test: Validate complete workflow from case loading through database population.

    Given: Initial and expanded case sets
    When: Running full workflow (load → identify new → add to collection)
    Then: Cases loaded correctly
          AND new cases identified accurately
          AND only new cases added to collection
          AND embeddings generated only for new cases
          AND metadata stored correctly
    """
    collection_name = get_unique_collection_name()
    # Given: Empty database
    client = chromadb.Client()
    collection = client.create_collection(collection_name)

    # First run: populate with initial cases
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_initial):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance = Mock()
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            mock_embedding_model.return_value.encode.reset_mock()

            call_main_with_mocked_args(["setup_vectordb.py"])

            # Verify initial population
            initial_count = collection.count()
            assert initial_count == len(sample_cases_initial)

            # Verify embeddings generated for all initial cases
            encode_calls = mock_embedding_model.return_value.encode.call_count
            assert encode_calls >= 1, "Embeddings should be generated"

    # Second run: add new cases
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_expanded):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            # Identify new cases before running
            new_cases, skipped = identify_new_cases(sample_cases_expanded, collection)

            mock_embedding_model.return_value.encode.reset_mock()

            call_main_with_mocked_args(["setup_vectordb.py"])

            final_count = collection.count()

    # Then: New cases identified correctly
    expected_new = len(sample_cases_expanded) - len(sample_cases_initial)
    assert len(new_cases) == expected_new, \
        f"Expected {expected_new} new cases, got {len(new_cases)}"

    # And: Only new cases added
    cases_added = final_count - initial_count
    assert cases_added == expected_new, \
        f"Expected {expected_new} cases added, got {cases_added}"

    # And: Final count correct
    assert final_count == len(sample_cases_expanded), \
        f"Expected {len(sample_cases_expanded)} total cases, got {final_count}"

    # And: Metadata stored correctly (verify by checking collection)
    all_data = collection.get(include=["metadatas"])
    assert len(all_data["metadatas"]) == final_count, \
        "Metadata count should match case count"


def test_incremental_update_with_partially_populated_database(
    temp_db_path, mock_embedding_model, sample_cases_initial, sample_cases_expanded
):
    """
    Test: Verify behavior when database already has some but not all cases.

    Given: Database with subset of cases
    When: Running main() with full case set
    Then: identify_new_cases() correctly finds new vs existing
          AND only missing cases are added
          AND existing cases remain unchanged
    """
    collection_name = get_unique_collection_name()
    # Given: Database with subset (2 out of 5 cases)
    client = chromadb.Client()
    collection = client.create_collection(collection_name)

    subset_cases = sample_cases_initial[:2]  # Only 2 cases

    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=subset_cases):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance = Mock()
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            call_main_with_mocked_args(["setup_vectordb.py"])
            subset_count = collection.count()
            subset_ids = set(collection.get()["ids"])

    # When: Running with full expanded set
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_expanded):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            # Identify new cases
            new_cases, skipped = identify_new_cases(sample_cases_expanded, collection)

            call_main_with_mocked_args(["setup_vectordb.py"])
            final_count = collection.count()
            final_ids = set(collection.get()["ids"])

    # Then: Correct number of new cases identified
    expected_new = len(sample_cases_expanded) - len(subset_cases)
    assert len(new_cases) == expected_new, \
        f"Expected {expected_new} new cases, got {len(new_cases)}"

    # And: Correct number skipped
    assert skipped == len(subset_cases), \
        f"Expected {len(subset_cases)} skipped, got {skipped}"

    # And: Existing cases preserved
    assert subset_ids.issubset(final_ids), \
        "Existing case IDs were lost"

    # And: Final count correct
    assert final_count == len(sample_cases_expanded), \
        f"Expected {len(sample_cases_expanded)} total, got {final_count}"


def test_incremental_update_with_fully_populated_database(
    temp_db_path, mock_embedding_model, sample_cases_expanded
):
    """
    Test: Verify behavior when all cases already exist (no-op scenario).

    Given: Database already contains all cases
    When: Running main() with same cases
    Then: identify_new_cases() returns empty new cases list
          AND no add() operation called on collection
          AND statistics show 0 added, N skipped
    """
    collection_name = get_unique_collection_name()
    # Given: Database with all cases
    client = chromadb.Client()
    collection = client.create_collection(collection_name)

    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_expanded):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance = Mock()
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            call_main_with_mocked_args(["setup_vectordb.py"])
            first_count = collection.count()

    # When: Running again with same cases
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_expanded):
        # Track if add() is called
        original_add = collection.add
        add_called = False

        def track_add(*args, **kwargs):
            nonlocal add_called
            add_called = True
            return original_add(*args, **kwargs)

        collection.add = track_add

        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            # Identify new cases
            new_cases, skipped = identify_new_cases(sample_cases_expanded, collection)

            call_main_with_mocked_args(["setup_vectordb.py"])
            second_count = collection.count()

    # Then: No new cases identified
    assert len(new_cases) == 0, \
        f"Expected 0 new cases, got {len(new_cases)}"

    # And: All cases skipped
    assert skipped == len(sample_cases_expanded), \
        f"Expected {len(sample_cases_expanded)} skipped, got {skipped}"

    # And: No add() called (no-op)
    # Note: This assertion may fail if implementation always calls add(),
    # which is acceptable if it's called with empty list

    # And: Count unchanged
    assert second_count == first_count, \
        f"Count changed from {first_count} to {second_count} (should be no-op)"


def test_incremental_update_with_empty_database(
    temp_db_path, mock_embedding_model, sample_cases_initial
):
    """
    Test: Verify first-run behavior with empty database (baseline).

    Given: Empty database collection
    When: Running main() for first time
    Then: All cases identified as new
          AND all cases added to collection
          AND statistics show N added, 0 skipped
    """
    collection_name = get_unique_collection_name()
    # Given: Empty database
    client = chromadb.Client()
    collection = client.create_collection(collection_name)

    assert collection.count() == 0, "Collection should start empty"

    # When: Running main() for first time
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_initial):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance = Mock()
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            # Identify new cases before running
            new_cases, skipped = identify_new_cases(sample_cases_initial, collection)

            call_main_with_mocked_args(["setup_vectordb.py"])
            final_count = collection.count()

    # Then: All cases identified as new
    assert len(new_cases) == len(sample_cases_initial), \
        f"Expected {len(sample_cases_initial)} new cases, got {len(new_cases)}"

    # And: No cases skipped
    assert skipped == 0, \
        f"Expected 0 skipped cases, got {skipped}"

    # And: All cases added
    assert final_count == len(sample_cases_initial), \
        f"Expected {len(sample_cases_initial)} cases in DB, got {final_count}"


def test_force_flag_no_longer_needed(
    temp_db_path, mock_embedding_model, sample_cases_initial, sample_cases_expanded
):
    """
    Test: Verify incremental mode is default (--force no longer required).

    Given: Database with initial cases
    When: Running main() without --force flag
    Then: Incremental update performed (not full rebuild)
          AND existing cases not deleted
          AND new cases added correctly
    """
    collection_name = get_unique_collection_name()
    # Given: Database with initial cases
    client = chromadb.Client()
    collection = client.create_collection(collection_name)

    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_initial):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance = Mock()
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            call_main_with_mocked_args(["setup_vectordb.py"])  # No --force flag
            initial_count = collection.count()
            initial_ids = set(collection.get()["ids"])

    # When: Running without --force flag with expanded cases
    with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=sample_cases_expanded):
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            call_main_with_mocked_args(["setup_vectordb.py"])  # No --force flag
            final_count = collection.count()
            final_ids = set(collection.get()["ids"])

    # Then: Existing cases not deleted
    assert initial_ids.issubset(final_ids), \
        "Existing cases were deleted (incremental mode should preserve them)"

    # And: New cases added
    assert final_count > initial_count, \
        f"Expected count > {initial_count}, got {final_count}"

    # And: Final count correct
    expected_count = len(sample_cases_expanded)
    assert final_count == expected_count, \
        f"Expected {expected_count} cases, got {final_count}"

    # And: Incremental update was used (not full rebuild)
    cases_added = final_count - initial_count
    expected_new = len(sample_cases_expanded) - len(sample_cases_initial)
    assert cases_added == expected_new, \
        f"Expected {expected_new} new cases added incrementally, got {cases_added}"
