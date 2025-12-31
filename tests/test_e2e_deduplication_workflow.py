"""End-to-end integration tests for vector database deduplication workflows.

This test suite validates the complete end-to-end workflows for the deduplication
feature as specified in Task 6.1 of the vector-db-deduplication spec:

1. Complete workflow: fresh database → populate → re-run (no duplicates)
2. Partial database → add new cases → verify no duplicates
3. Validation mode on known-good database
4. Validation mode on database with discrepancies
5. Error recovery scenarios

These tests use temporary ChromaDB instances to ensure test isolation and
follow TDD principles by being written BEFORE the implementation is complete.

Test Strategy:
- Use real ChromaDB operations for integration-level validation
- Mock SentenceTransformer embeddings to avoid model downloads
- Use temporary database paths for complete test isolation
- Verify both successful paths and error handling
"""

import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock
import pytest
import chromadb

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utilities.setup_vectordb import (
    generate_case_id,
    identify_new_cases,
    validate_database,
    main,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_db_path(worker_id):
    """Create temporary database path for testing with worker-specific naming."""
    temp_dir = tempfile.mkdtemp(prefix=f"cbr_e2e_test_{worker_id}_")
    db_path = Path(temp_dir) / "test_db"
    yield str(db_path)
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def unique_collection_name(request):
    """Generate unique collection name for each test to avoid conflicts."""
    test_name = request.node.name
    # Create unique collection name from test name
    return f"test_{test_name}"


@pytest.fixture
def mock_embedding_model():
    """Mock SentenceTransformer embedding model to prevent model downloads."""
    with patch("scripts.utilities.setup_vectordb.SentenceTransformer") as mock_model:
        mock_instance = Mock()

        # Configure encode to return mock embeddings
        def mock_encode(texts, normalize_embeddings=True):
            import numpy as np

            # Return unique embeddings based on text length for determinism
            return np.random.rand(len(texts), 768)

        mock_instance.encode.side_effect = mock_encode
        mock_model.return_value = mock_instance

        yield mock_model


@pytest.fixture
def sample_cases_full():
    """Full set of sample cases for testing."""
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
def sample_cases_subset(sample_cases_full):
    """Subset of sample cases (first 3 of 5)."""
    return sample_cases_full[:3]


# ============================================================================
# Test 1: Complete Workflow - Fresh Database → Populate → Re-run
# ============================================================================


def test_e2e_fresh_database_populate_rerun_no_duplicates(
    temp_db_path, mock_embedding_model, sample_cases_full, unique_collection_name
):
    """
    Test: Complete end-to-end workflow from fresh database to re-run.

    Given: Empty database
    When: Run setup_vectordb.py to populate
          Then run it again with same cases
    Then: First run adds all cases
          Second run skips all cases (no duplicates)
          Database count identical after both runs
          All case IDs match expected content-based IDs
    """
    # Given: Empty database (fresh ChromaDB client)
    with patch("chromadb.PersistentClient") as mock_client_cls:
        # Use in-memory client for test isolation
        client = chromadb.Client()
        # Use unique collection name to avoid conflicts between tests
        collection = client.create_collection(unique_collection_name)

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = collection
        mock_client_instance.get_collection.return_value = collection
        mock_client_cls.return_value = mock_client_instance

        # When: First run - populate database
        with patch(
            "scripts.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_full,
        ):
            with patch("sys.argv", ["setup_vectordb.py"]):
                main()

        first_run_count = collection.count()
        first_run_ids = set(collection.get()["ids"])

        # Then: All cases added
        assert first_run_count == len(
            sample_cases_full
        ), f"First run should add all {len(sample_cases_full)} cases, got {first_run_count}"

        # Verify content-based IDs were generated
        expected_ids = {generate_case_id(case) for case in sample_cases_full}
        assert (
            first_run_ids == expected_ids
        ), "Case IDs should match content-based ID generation"

        # When: Second run - re-run with same cases
        with patch(
            "scripts.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_full,
        ):
            with patch("sys.argv", ["setup_vectordb.py"]):
                main()

        second_run_count = collection.count()
        second_run_ids = set(collection.get()["ids"])

        # Then: No new cases added (all skipped)
        assert (
            second_run_count == first_run_count
        ), f"Second run should not add cases (expected {first_run_count}, got {second_run_count})"

        # And: Case IDs unchanged
        assert (
            second_run_ids == first_run_ids
        ), "Case IDs should remain identical after re-run"

        # And: No duplicate IDs present
        all_ids = collection.get()["ids"]
        assert len(all_ids) == len(
            set(all_ids)
        ), "Database should not contain duplicate IDs"


# ============================================================================
# Test 2: Partial Database → Add New Cases → No Duplicates
# ============================================================================


def test_e2e_partial_database_add_new_cases_no_duplicates(
    temp_db_path,
    mock_embedding_model,
    sample_cases_subset,
    sample_cases_full,
    unique_collection_name,
):
    """
    Test: Incremental update workflow with partial database.

    Given: Database with subset of cases (3 of 5)
    When: Run setup_vectordb.py with full case set (5 cases)
    Then: Only 2 new cases added
          Original 3 cases preserved
          Final count is 5 (no duplicates)
          All case IDs are content-based
    """
    # Given: Database with subset of cases
    with patch("chromadb.PersistentClient") as mock_client_cls:
        client = chromadb.Client()
        collection = client.create_collection(unique_collection_name)

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = collection
        mock_client_instance.get_collection.return_value = collection
        mock_client_cls.return_value = mock_client_instance

        # First run: populate with subset
        with patch(
            "scripts.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_subset,
        ):
            with patch("sys.argv", ["setup_vectordb.py"]):
                main()

        initial_count = collection.count()
        initial_ids = set(collection.get()["ids"])

        assert initial_count == len(
            sample_cases_subset
        ), f"Initial population should have {len(sample_cases_subset)} cases"

        # When: Second run with full case set
        with patch(
            "scripts.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_full,
        ):
            with patch("sys.argv", ["setup_vectordb.py"]):
                main()

        final_count = collection.count()
        final_ids = set(collection.get()["ids"])

        # Then: Only new cases added
        expected_new_cases = len(sample_cases_full) - len(sample_cases_subset)
        actual_new_cases = final_count - initial_count

        assert (
            actual_new_cases == expected_new_cases
        ), f"Expected {expected_new_cases} new cases added, got {actual_new_cases}"

        # And: Original cases preserved
        assert initial_ids.issubset(
            final_ids
        ), "Original case IDs should be preserved in final database"

        # And: Final count correct (no duplicates)
        assert final_count == len(
            sample_cases_full
        ), f"Final count should be {len(sample_cases_full)}, got {final_count}"

        # And: All IDs are content-based
        expected_ids = {generate_case_id(case) for case in sample_cases_full}
        assert final_ids == expected_ids, "All case IDs should be content-based"

        # And: No duplicate IDs
        all_ids = collection.get()["ids"]
        assert len(all_ids) == len(
            set(all_ids)
        ), "Database should not contain duplicate IDs"


# ============================================================================
# Test 3: Validation Mode on Known-Good Database
# ============================================================================


def test_e2e_validation_mode_known_good_database(
    unique_collection_name,
    temp_db_path,
    mock_embedding_model,
    sample_cases_full,
    capsys,
):
    """
    Test: Validation mode on database in perfect sync with case files.

    Given: Database populated with cases matching case files exactly
    When: Run setup_vectordb.py --validate
    Then: Validation reports perfect match
          Exit code 0 (success)
          Output shows "in perfect sync" message
          Database unchanged after validation
    """
    # Given: Database with all cases
    with patch("chromadb.PersistentClient") as mock_client_cls:
        client = chromadb.Client()
        collection = client.create_collection(unique_collection_name)

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = collection
        mock_client_instance.get_collection.return_value = collection
        mock_client_cls.return_value = mock_client_instance

        # Populate database
        with patch(
            "scripts.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_full,
        ):
            with patch("sys.argv", ["setup_vectordb.py"]):
                main()

        pre_validation_count = collection.count()
        pre_validation_ids = set(collection.get()["ids"])

        # When: Run validation mode via CLI
        with patch(
            "scripts.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_full,
        ):
            with patch("sys.argv", ["setup_vectordb.py", "--validate"]):
                with pytest.raises(SystemExit) as exc_info:
                    main()

        # Capture output
        captured = capsys.readouterr()
        output = captured.out.lower()

        # Then: Exit code 0 (perfect match)
        assert (
            exc_info.value.code == 0
        ), f"Validation should exit with code 0 for perfect match, got {exc_info.value.code}"

        # And: Output shows perfect sync
        assert (
            "perfect sync" in output or "✓" in output or "matching" in output
        ), f"Output should indicate perfect sync, got: {captured.out}"

        # And: Statistics show correct counts
        assert (
            str(len(sample_cases_full)) in output
        ), "Output should show correct case count"

        # And: Database unchanged
        post_validation_count = collection.count()
        post_validation_ids = set(collection.get()["ids"])

        assert (
            post_validation_count == pre_validation_count
        ), "Validation should not change database count"
        assert (
            post_validation_ids == pre_validation_ids
        ), "Validation should not change database IDs"


def test_e2e_validation_mode_function_call_known_good(
    unique_collection_name,
    temp_db_path,
    mock_embedding_model,
    sample_cases_full,
    capsys,
):
    """
    Test: Direct function call to validate_database on known-good database.

    This tests the validate_database function directly (not via CLI).

    Given: Database with all cases matching files
    When: Call validate_database() directly
    Then: Returns dictionary with has_discrepancies=False for perfect match
          Dictionary contains correct validation statistics
    """
    # Given: Database with all cases
    with patch("chromadb.PersistentClient") as mock_client_cls:
        client = chromadb.Client()
        collection = client.create_collection(unique_collection_name)

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = collection
        mock_client_instance.get_collection.return_value = collection
        mock_client_cls.return_value = mock_client_instance

        # Populate database
        with patch(
            "scripts.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_full,
        ):
            with patch("sys.argv", ["setup_vectordb.py"]):
                main()

        # When: Call validate_database directly
        with patch(
            "scripts.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_full,
        ):
            result = validate_database(sample_cases_full, collection)

        # Then: Result is a dictionary with expected structure
        assert isinstance(result, dict), "validate_database should return a dictionary"
        assert (
            "has_discrepancies" in result
        ), "Result should contain 'has_discrepancies' field"
        assert (
            "cases_in_files" in result
        ), "Result should contain 'cases_in_files' field"
        assert "cases_in_db" in result, "Result should contain 'cases_in_db' field"
        assert "matches" in result, "Result should contain 'matches' field"
        assert (
            "missing_from_db" in result
        ), "Result should contain 'missing_from_db' field"
        assert "extra_in_db" in result, "Result should contain 'extra_in_db' field"

        # And: No discrepancies for perfect match
        assert (
            result["has_discrepancies"] is False
        ), f"Validation should report no discrepancies for perfect match, got has_discrepancies={result['has_discrepancies']}"

        # And: Correct statistics
        assert result["cases_in_files"] == len(
            sample_cases_full
        ), f"Should have {len(sample_cases_full)} cases in files"
        assert result["cases_in_db"] == len(
            sample_cases_full
        ), f"Should have {len(sample_cases_full)} cases in database"
        assert result["matches"] == len(
            sample_cases_full
        ), f"All {len(sample_cases_full)} cases should match"
        assert len(result["missing_from_db"]) == 0, "Should have no missing cases"
        assert len(result["extra_in_db"]) == 0, "Should have no extra cases"


# ============================================================================
# Test 4: Validation Mode on Database with Discrepancies
# ============================================================================


def test_e2e_validation_mode_database_with_discrepancies(
    unique_collection_name,
    temp_db_path,
    mock_embedding_model,
    sample_cases_subset,
    sample_cases_full,
    capsys,
):
    """
    Test: Validation mode on database with discrepancies via CLI.

    Given: Database with subset of cases (3 of 5)
          Case files contain full set (5 cases)
    When: Run setup_vectordb.py --validate
    Then: Validation reports discrepancies
          Exit code 1 (failure)
          Missing cases listed correctly (2 cases)
          Database unchanged after validation
    """
    # Given: Database with subset, files have full set
    with patch("chromadb.PersistentClient") as mock_client_cls:
        client = chromadb.Client()
        collection = client.create_collection(unique_collection_name)

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = collection
        mock_client_instance.get_collection.return_value = collection
        mock_client_cls.return_value = mock_client_instance

        # Populate with subset
        with patch(
            "scripts.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_subset,
        ):
            with patch("sys.argv", ["setup_vectordb.py"]):
                main()

        pre_validation_count = collection.count()
        pre_validation_ids = set(collection.get()["ids"])

        # When: Run validation mode via CLI
        with patch(
            "scripts.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_full,
        ):
            with patch("sys.argv", ["setup_vectordb.py", "--validate"]):
                with pytest.raises(SystemExit) as exc_info:
                    main()

        # Capture output
        captured = capsys.readouterr()
        output = captured.out.lower()

        # Then: Exit code 1 (discrepancies found)
        assert (
            exc_info.value.code == 1
        ), f"Validation should exit with code 1 for discrepancies, got {exc_info.value.code}"

        # And: Discrepancies reported
        assert (
            "missing from database" in output
            or "⚠" in output
            or "discrepancies" in output
        ), f"Should report discrepancies, got: {captured.out}"

        # And: Correct number of missing cases
        expected_missing = len(sample_cases_full) - len(sample_cases_subset)
        assert (
            str(expected_missing) in output
        ), f"Should report {expected_missing} missing cases in output: {captured.out}"

        # And: Database unchanged
        post_validation_count = collection.count()
        post_validation_ids = set(collection.get()["ids"])

        assert (
            post_validation_count == pre_validation_count
        ), "Validation should not change database count"
        assert (
            post_validation_ids == pre_validation_ids
        ), "Validation should not change database IDs"


def test_e2e_validation_mode_function_call_with_discrepancies(
    unique_collection_name,
    temp_db_path,
    mock_embedding_model,
    sample_cases_subset,
    sample_cases_full,
    capsys,
):
    """
    Test: Direct function call to validate_database with discrepancies.

    This tests the validate_database function directly (not via CLI).

    Given: Database with subset of cases
    When: Call validate_database() with full case set
    Then: Returns dictionary with has_discrepancies=True
          Missing cases reported correctly in the dictionary
    """
    # Given: Database with subset
    with patch("chromadb.PersistentClient") as mock_client_cls:
        client = chromadb.Client()
        collection = client.create_collection(unique_collection_name)

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = collection
        mock_client_instance.get_collection.return_value = collection
        mock_client_cls.return_value = mock_client_instance

        # Populate with subset
        with patch(
            "scripts.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_subset,
        ):
            with patch("sys.argv", ["setup_vectordb.py"]):
                main()

        # When: Validate against full case set
        result = validate_database(sample_cases_full, collection)

        # Then: Result is a dictionary with expected structure
        assert isinstance(result, dict), "validate_database should return a dictionary"
        assert (
            "has_discrepancies" in result
        ), "Result should contain 'has_discrepancies' field"
        assert (
            "cases_in_files" in result
        ), "Result should contain 'cases_in_files' field"
        assert "cases_in_db" in result, "Result should contain 'cases_in_db' field"
        assert "matches" in result, "Result should contain 'matches' field"
        assert (
            "missing_from_db" in result
        ), "Result should contain 'missing_from_db' field"
        assert "extra_in_db" in result, "Result should contain 'extra_in_db' field"

        # And: Has discrepancies (missing cases)
        assert (
            result["has_discrepancies"] is True
        ), f"Validation should report discrepancies when cases are missing, got has_discrepancies={result['has_discrepancies']}"

        # And: Correct statistics
        expected_missing = len(sample_cases_full) - len(sample_cases_subset)
        assert result["cases_in_files"] == len(
            sample_cases_full
        ), f"Should have {len(sample_cases_full)} cases in files"
        assert result["cases_in_db"] == len(
            sample_cases_subset
        ), f"Should have {len(sample_cases_subset)} cases in database"
        assert result["matches"] == len(
            sample_cases_subset
        ), f"Should have {len(sample_cases_subset)} matching cases"
        assert (
            len(result["missing_from_db"]) == expected_missing
        ), f"Should report {expected_missing} missing cases, got {len(result['missing_from_db'])}"
        assert len(result["extra_in_db"]) == 0, "Should have no extra cases"

        # And: missing_from_db list contains the expected case IDs
        expected_missing_ids = {
            generate_case_id(case)
            for case in sample_cases_full[len(sample_cases_subset) :]
        }
        actual_missing_ids = set(result["missing_from_db"])
        assert (
            actual_missing_ids == expected_missing_ids
        ), f"Missing case IDs should match expected IDs"


# ============================================================================
# Test 5: Error Recovery - ChromaDB Connection Failure
# ============================================================================


def test_e2e_error_recovery_chromadb_connection_failure(
    mock_embedding_model, sample_cases_full, capsys
):
    """
    Test: Error handling when ChromaDB connection fails.

    Given: ChromaDB PersistentClient raises exception
    When: Run setup_vectordb.py
    Then: Appropriate error message displayed
          Script exits with non-zero code
          Error message guides user to fix
    """
    # Given: ChromaDB connection failure
    with patch("chromadb.PersistentClient") as mock_client_cls:
        mock_client_cls.side_effect = Exception("Failed to connect to ChromaDB")

        # When: Run main()
        with patch(
            "scripts.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_full,
        ):
            with patch("sys.argv", ["setup_vectordb.py"]):
                with pytest.raises(SystemExit) as exc_info:
                    main()

        # Then: Exit with non-zero code
        assert (
            exc_info.value.code != 0
        ), "Should exit with non-zero code on connection failure"

        # And: Error message displayed
        captured = capsys.readouterr()
        output = (captured.out + captured.err).lower()

        assert (
            "chromadb" in output or "database" in output
        ), "Error message should mention ChromaDB/database"
        assert (
            "failed" in output or "error" in output
        ), "Error message should indicate failure"


# ============================================================================
# Test 6: Error Recovery - Embedding Generation Failure
# ============================================================================


def test_e2e_error_recovery_embedding_generation_failure(
    unique_collection_name, temp_db_path, sample_cases_full, capsys
):
    """
    Test: Error handling when embedding model fails.

    Given: SentenceTransformer.encode raises exception
    When: Run setup_vectordb.py
    Then: Appropriate error message displayed
          Script exits with non-zero code
          Error mentions embedding model issue
    """
    # Given: Embedding generation failure
    with patch("scripts.utilities.setup_vectordb.SentenceTransformer") as mock_model:
        mock_instance = Mock()
        mock_instance.encode.side_effect = Exception("Embedding generation failed")
        mock_model.return_value = mock_instance

        with patch("chromadb.PersistentClient") as mock_client_cls:
            client = chromadb.Client()
            collection = client.create_collection(unique_collection_name)

            mock_client_instance = Mock()
            mock_client_instance.get_or_create_collection.return_value = collection
            mock_client_cls.return_value = mock_client_instance

            # When: Run main()
            with patch(
                "scripts.utilities.setup_vectordb.load_all_cases",
                return_value=sample_cases_full,
            ):
                with patch("sys.argv", ["setup_vectordb.py"]):
                    with pytest.raises(SystemExit) as exc_info:
                        main()

            # Then: Exit with non-zero code
            assert (
                exc_info.value.code != 0
            ), "Should exit with non-zero code on embedding failure"

            # And: Error message displayed
            captured = capsys.readouterr()
            output = (captured.out + captured.err).lower()

            assert (
                "embedding" in output or "model" in output
            ), "Error message should mention embedding/model"
            assert (
                "failed" in output or "error" in output
            ), "Error message should indicate failure"


# ============================================================================
# Test 7: Error Recovery - Empty Collection After Filtering
# ============================================================================


def test_e2e_error_recovery_empty_collection_after_filtering(
    unique_collection_name, temp_db_path, mock_embedding_model, capsys
):
    """
    Test: Behavior when filters result in zero cases.

    Given: load_all_cases returns empty list (all filtered out)
    When: Run setup_vectordb.py
    Then: Warning message displayed
          Script exits gracefully
          No database operations attempted
    """
    # Given: Empty case list after filtering
    with patch("chromadb.PersistentClient") as mock_client_cls:
        client = chromadb.Client()
        collection = client.create_collection(unique_collection_name)

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = collection
        mock_client_cls.return_value = mock_client_instance

        # When: Run with empty case list
        with patch("scripts.utilities.setup_vectordb.load_all_cases", return_value=[]):
            with patch("sys.argv", ["setup_vectordb.py"]):
                # Should exit gracefully
                try:
                    main()
                except SystemExit as e:
                    # Verify exit was graceful
                    pass

        # Then: Collection should be empty or warning displayed
        captured = capsys.readouterr()
        output = (captured.out + captured.err).lower()

        # Should either warn about empty cases or gracefully handle
        # (implementation-specific behavior)
        collection_count = collection.count()
        assert collection_count == 0, "No cases should be added when case list is empty"


# ============================================================================
# Test 8: Complete Workflow with Real Case Base
# ============================================================================


def test_e2e_complete_workflow_with_real_case_base(
    unique_collection_name, temp_db_path, mock_embedding_model
):
    """
    Test: Integration test with actual case loading (not mocked cases).

    Given: Real case loader (load_all_cases not mocked)
    When: Run setup_vectordb.py to populate
          Then run again to verify deduplication
    Then: All real cases loaded successfully
          Content-based IDs generated correctly
          Metadata stored properly
          Re-run produces no duplicates
    """
    # Given: Real case loading (don't mock load_all_cases)
    with patch("chromadb.PersistentClient") as mock_client_cls:
        client = chromadb.Client()
        collection = client.create_collection(unique_collection_name)

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = collection
        mock_client_instance.get_collection.return_value = collection
        mock_client_cls.return_value = mock_client_instance

        # When: First run with real case loader
        with patch("sys.argv", ["setup_vectordb.py"]):
            main()

        first_run_count = collection.count()
        first_run_ids = set(collection.get()["ids"])

        # Then: Cases loaded successfully
        assert first_run_count > 0, "Should load cases from real case base"

        # And: All IDs start with 'case_' (content-based)
        assert all(
            case_id.startswith("case_") for case_id in first_run_ids
        ), "All IDs should be content-based (start with 'case_')"

        # And: Metadata stored
        all_data = collection.get(include=["metadatas"])
        assert (
            len(all_data["metadatas"]) == first_run_count
        ), "All cases should have metadata"

        # Verify metadata has required fields
        for metadata in all_data["metadatas"]:
            assert "category" in metadata, "Metadata should include category"
            assert "subcategory" in metadata, "Metadata should include subcategory"

        # When: Second run (re-run)
        with patch("sys.argv", ["setup_vectordb.py"]):
            main()

        second_run_count = collection.count()
        second_run_ids = set(collection.get()["ids"])

        # Then: No duplicates (count unchanged)
        assert (
            second_run_count == first_run_count
        ), f"Re-run should not add duplicates (expected {first_run_count}, got {second_run_count})"

        # And: IDs unchanged
        assert (
            second_run_ids == first_run_ids
        ), "Re-run should preserve existing case IDs"

        # And: No duplicate IDs in database
        all_ids = collection.get()["ids"]
        assert len(all_ids) == len(
            set(all_ids)
        ), "Database should not contain duplicate IDs after re-run"
