"""
Integration tests for database population with complete metadata.

This test suite verifies that setup_vectordb.py correctly stores complete metadata
(problem, category, subcategory, tags) in ChromaDB instead of only the problem field.

These tests are designed to FAIL initially as they test the bug fix implementation
for the metadata storage bug documented in:
@.agent-os/specs/2025-11-04-metadata-storage-bug-fix/spec.md

Test Group: Database Population with Metadata (from tests.md)

NOTE: Tests use unique collection names per test to ensure isolation during
parallel execution with pytest-xdist.
"""

import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

import chromadb
import pytest
from sentence_transformers import SentenceTransformer


def get_unique_collection_name() -> str:
    """Generate a unique collection name for test isolation in parallel execution."""
    return f"test_collection_{uuid.uuid4().hex[:12]}"

# Add the src directory to path for importing setup_vectordb
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
sys.path.insert(0, src_path)

# Import setup_vectordb functions after path is set
from cbr_mcp_server.utilities.setup_vectordb import (
    filter_cases,
    main,
    parse_arguments,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_db_dir():
    """
    Create a temporary directory for ChromaDB testing.

    Yields the path to the temporary directory and cleans it up after the test.
    This prevents tests from interfering with the actual ./db directory.
    """
    temp_dir = tempfile.mkdtemp(prefix="cbr_test_db_")
    yield temp_dir
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def unique_collection_name():
    """Generate a unique collection name for test isolation."""
    return get_unique_collection_name()


@pytest.fixture
def mock_embedding_model():
    """
    Mock the SentenceTransformer to avoid downloading models during tests.

    Returns a mock that generates deterministic embeddings for testing.
    """
    mock_model = Mock(spec=SentenceTransformer)

    # Generate mock embeddings: simple list of floats for each case
    # Each case gets a unique but deterministic embedding
    def mock_encode(texts, normalize_embeddings=True):
        embeddings = []
        for i, _ in enumerate(texts):
            # Create a simple deterministic embedding based on index
            embedding = [0.1 + i * 0.01, 0.2 + i * 0.01, 0.3 + i * 0.01]
            embeddings.append(embedding)
        return embeddings

    mock_model.encode = mock_encode
    return mock_model


@pytest.fixture
def sample_cases_with_complete_metadata():
    """
    Fixture providing sample cases with complete metadata for testing.

    Returns a small, realistic CASE_BASE with all required metadata fields.
    """
    return [
        {
            "problem": "How to implement Firebase authentication",
            "solution": "Use firebase.auth().signInWithEmailAndPassword(...)",
            "category": "firebase",
            "subcategory": "auth",
            "tags": ["authentication", "firebase", "login"],
        },
        {
            "problem": "How to orchestrate multi-step agent workflows",
            "solution": "Use sequential delegation with verification checkpoints",
            "category": "orchestration",
            "subcategory": "planning",
            "tags": ["orchestration", "planning", "delegation"],
        },
        {
            "problem": "How to validate user input in React forms",
            "solution": "Use controlled components with validation state",
            "category": "react",
            "subcategory": "forms",
            "tags": ["react", "forms", "validation"],
        },
    ]


@pytest.fixture
def broken_metadata_database(temp_db_dir, unique_collection_name):
    """
    Create a database with broken metadata (only problem field) for testing --force rebuild.

    This simulates the buggy state where only {"problem": "..."} is stored.
    Returns a tuple of (client, collection, collection_name) for use in tests.
    """
    client = chromadb.PersistentClient(path=temp_db_dir)
    collection = client.create_collection(name=unique_collection_name)

    # Add cases with BROKEN metadata (only problem field)
    collection.add(
        embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        documents=[
            "Solution code for case 1",
            "Solution code for case 2",
        ],
        metadatas=[
            {"problem": "Problem 1"},  # BROKEN: missing category, subcategory, tags
            {"problem": "Problem 2"},  # BROKEN: missing category, subcategory, tags
        ],
        ids=["id0", "id1"],
    )

    return client, collection, unique_collection_name


# ============================================================================
# Test 1: Populate Empty Database with Full Metadata
# ============================================================================


def test_populate_empty_database_with_full_metadata(
    temp_db_dir, mock_embedding_model, sample_cases_with_complete_metadata, monkeypatch
):
    """
    Test that populating an empty database stores complete metadata.

    Given: Empty ChromaDB collection
    When: Running setup_vectordb.py with fixed metadata code
    Then:
      - Collection count matches number of cases
      - First case has all 4 metadata fields (problem, category, subcategory, tags)
      - Metadata values are correct and match original case data
    """
    # Set up command line arguments for no filtering (load all cases)
    monkeypatch.setattr(sys, "argv", ["setup_vectordb.py"])

    # Create a wrapper that intercepts PersistentClient calls and uses temp directory
    original_persistent_client = chromadb.PersistentClient

    def persistent_client_with_temp_path(*args, **kwargs):
        # Replace any path argument with our temp directory
        kwargs["path"] = temp_db_dir
        return original_persistent_client(*args, **kwargs)

    # Patch at the module level where it's imported
    with (
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_with_complete_metadata,
        ),
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.SentenceTransformer",
            return_value=mock_embedding_model,
        ),
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient",
            side_effect=persistent_client_with_temp_path,
        ),
    ):
        # Run the main setup function
        main()

    # Verify the database was populated correctly
    client = chromadb.PersistentClient(path=temp_db_dir)
    collection = client.get_collection(name="code_solutions_case_base")

    # Assertion 1: Collection count matches number of cases
    assert collection.count() == len(
        sample_cases_with_complete_metadata
    ), "Collection count should match number of cases loaded"

    # Retrieve the first case to check metadata
    results = collection.get(ids=["id0"], include=["metadatas", "documents"])

    # Assertion 2: First case has all 4 required metadata fields
    first_metadata = results["metadatas"][0]
    required_fields = ["problem", "category", "subcategory", "tags"]
    for field in required_fields:
        assert (
            field in first_metadata
        ), f"Metadata should contain '{field}' field but it's missing"

    # Assertion 3: Metadata values are correct
    expected_first_case = sample_cases_with_complete_metadata[0]
    assert (
        first_metadata["problem"] == expected_first_case["problem"]
    ), "Problem field should match original case data"
    assert (
        first_metadata["category"] == expected_first_case["category"]
    ), "Category field should match original case data"
    assert (
        first_metadata["subcategory"] == expected_first_case["subcategory"]
    ), "Subcategory field should match original case data"

    # Tags should be stored as comma-separated string
    expected_tags_string = ",".join(expected_first_case["tags"])
    assert (
        first_metadata["tags"] == expected_tags_string
    ), "Tags should be stored as comma-separated string"


# ============================================================================
# Test 2: Force Rebuild Replaces Broken Metadata
# ============================================================================


def test_force_rebuild_replaces_broken_metadata(
    temp_db_dir,
    mock_embedding_model,
    sample_cases_with_complete_metadata,
    broken_metadata_database,
    monkeypatch,
):
    """
    Test that --force flag rebuilds database with correct metadata.

    Given: Existing database with broken metadata (only problem field)
    When: Running setup_vectordb.py --force with fixed code
    Then:
      - Old collection is deleted
      - New collection is created
      - Collection count matches expected number
      - All cases have complete metadata (4 fields)
    """
    # The broken_metadata_database fixture already created a broken database
    client, old_collection, collection_name = broken_metadata_database

    # Verify the broken state (only 2 cases, broken metadata)
    assert old_collection.count() == 2, "Broken database should have 2 cases initially"
    broken_results = old_collection.get(ids=["id0"], include=["metadatas"])
    assert (
        "category" not in broken_results["metadatas"][0]
    ), "Broken database should not have category field"

    # Set up command line arguments with --force flag
    monkeypatch.setattr(sys, "argv", ["setup_vectordb.py", "--force"])

    # Mock load_all_cases to return our sample cases
    with (
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_with_complete_metadata,
        ),
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.SentenceTransformer",
            return_value=mock_embedding_model,
        ),
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient",
            return_value=client,
        ),
    ):

        # Run the main setup function with --force
        main()

    # Verify the database was rebuilt correctly
    # Get the collection (should be newly created)
    collection = client.get_collection(name="code_solutions_case_base")

    # Assertion 1: Collection count matches new case set
    assert collection.count() == len(
        sample_cases_with_complete_metadata
    ), "Rebuilt database should have correct number of cases"

    # Assertion 2: All cases now have complete metadata
    all_results = collection.get(include=["metadatas"])
    for metadata in all_results["metadatas"]:
        required_fields = ["problem", "category", "subcategory", "tags"]
        for field in required_fields:
            assert (
                field in metadata
            ), f"All cases should have '{field}' after force rebuild"

    # Assertion 3: Verify first case has correct complete metadata
    first_result = collection.get(ids=["id0"], include=["metadatas"])
    first_metadata = first_result["metadatas"][0]
    assert (
        "category" in first_metadata
    ), "Rebuilt database should have category field (was missing before)"
    assert (
        "subcategory" in first_metadata
    ), "Rebuilt database should have subcategory field (was missing before)"
    assert (
        "tags" in first_metadata
    ), "Rebuilt database should have tags field (was missing before)"


# ============================================================================
# Test 3: Metadata Preserved During Filtered Load
# ============================================================================


def test_metadata_preserved_during_filtered_load(
    temp_db_dir, mock_embedding_model, monkeypatch
):
    """
    Test that category filtering preserves complete metadata.

    Given: Running setup_vectordb.py --category orchestration
    When: Loading only orchestration cases
    Then:
      - Filtered CASE_BASE contains only orchestration cases
      - All loaded cases have complete metadata
      - ChromaDB stores complete metadata for filtered subset
    """
    # Create a larger sample with multiple categories
    all_cases = [
        {
            "problem": "Orchestration problem 1",
            "solution": "Orchestration solution 1",
            "category": "orchestration",
            "subcategory": "planning",
            "tags": ["orchestration", "planning"],
        },
        {
            "problem": "Orchestration problem 2",
            "solution": "Orchestration solution 2",
            "category": "orchestration",
            "subcategory": "delegation",
            "tags": ["orchestration", "delegation"],
        },
        {
            "problem": "Firebase problem 1",
            "solution": "Firebase solution 1",
            "category": "firebase",
            "subcategory": "auth",
            "tags": ["firebase", "auth"],
        },
        {
            "problem": "React problem 1",
            "solution": "React solution 1",
            "category": "react",
            "subcategory": "hooks",
            "tags": ["react", "hooks"],
        },
    ]

    # Set up command line arguments with --category orchestration
    monkeypatch.setattr(
        sys, "argv", ["setup_vectordb.py", "--category", "orchestration"]
    )

    # Create a wrapper that intercepts PersistentClient calls and uses temp directory
    original_persistent_client = chromadb.PersistentClient

    def persistent_client_with_temp_path(*args, **kwargs):
        # Replace any path argument with our temp directory
        kwargs["path"] = temp_db_dir
        return original_persistent_client(*args, **kwargs)

    # Patch at the module level where it's imported
    with (
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.load_all_cases",
            return_value=all_cases,
        ),
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.SentenceTransformer",
            return_value=mock_embedding_model,
        ),
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient",
            side_effect=persistent_client_with_temp_path,
        ),
    ):
        # Run the main setup function
        main()

    # Verify the database was populated with filtered cases
    client = chromadb.PersistentClient(path=temp_db_dir)
    collection = client.get_collection(name="code_solutions_case_base")

    # Assertion 1: Only orchestration cases were loaded (2 out of 4)
    assert (
        collection.count() == 2
    ), "Should only load orchestration cases (2 out of 4 total)"

    # Assertion 2: All loaded cases have complete metadata
    all_results = collection.get(include=["metadatas"])
    for metadata in all_results["metadatas"]:
        required_fields = ["problem", "category", "subcategory", "tags"]
        for field in required_fields:
            assert (
                field in metadata
            ), f"Filtered cases should have complete metadata including '{field}'"

    # Assertion 3: All cases have category="orchestration"
    for metadata in all_results["metadatas"]:
        assert (
            metadata["category"] == "orchestration"
        ), "All loaded cases should have category='orchestration'"

    # Assertion 4: Verify specific subcategories are preserved
    subcategories = [m["subcategory"] for m in all_results["metadatas"]]
    assert "planning" in subcategories, "Planning subcategory should be preserved"
    assert "delegation" in subcategories, "Delegation subcategory should be preserved"


# ============================================================================
# Test 4: Problem Field Backward Compatibility
# ============================================================================


def test_problem_field_backward_compatibility(
    temp_db_dir, mock_embedding_model, sample_cases_with_complete_metadata, monkeypatch
):
    """
    Test that problem field still exists for backward compatibility.

    Given: Database populated with new metadata code
    When: Querying for problem field in metadata
    Then:
      - Problem field exists in metadata
      - Problem field contains expected problem description text
    """
    # Set up command line arguments for no filtering
    monkeypatch.setattr(sys, "argv", ["setup_vectordb.py"])

    # Create a wrapper that intercepts PersistentClient calls and uses temp directory
    original_persistent_client = chromadb.PersistentClient

    def persistent_client_with_temp_path(*args, **kwargs):
        # Replace any path argument with our temp directory
        kwargs["path"] = temp_db_dir
        return original_persistent_client(*args, **kwargs)

    # Patch at the module level where it's imported
    with (
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_with_complete_metadata,
        ),
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.SentenceTransformer",
            return_value=mock_embedding_model,
        ),
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient",
            side_effect=persistent_client_with_temp_path,
        ),
    ):
        # Run the main setup function
        main()

    # Verify the problem field is still accessible
    client = chromadb.PersistentClient(path=temp_db_dir)
    collection = client.get_collection(name="code_solutions_case_base")

    # Retrieve all cases to check problem field
    all_results = collection.get(include=["metadatas"])

    # Assertion 1: All cases have problem field
    for metadata in all_results["metadatas"]:
        assert (
            "problem" in metadata
        ), "Problem field should exist for backward compatibility"

    # Assertion 2: Problem field is a string
    for metadata in all_results["metadatas"]:
        assert isinstance(metadata["problem"], str), "Problem field should be a string"

    # Assertion 3: Problem field matches original case data
    for i, metadata in enumerate(all_results["metadatas"]):
        expected_problem = sample_cases_with_complete_metadata[i]["problem"]
        assert (
            metadata["problem"] == expected_problem
        ), f"Problem field should match original case data for case {i}"


# ============================================================================
# Test 5: Solution Stored as Document
# ============================================================================


def test_solution_stored_as_document(
    temp_db_dir, mock_embedding_model, sample_cases_with_complete_metadata, monkeypatch
):
    """
    Test that solution code is stored as document content (not metadata).

    Given: Database populated with new metadata code
    When: Retrieving documents and metadata from collection
    Then:
      - Documents contain solution code
      - Solution is NOT in metadata
      - Document content is retrievable and matches original
    """
    # Set up command line arguments for no filtering
    monkeypatch.setattr(sys, "argv", ["setup_vectordb.py"])

    # Create a wrapper that intercepts PersistentClient calls and uses temp directory
    original_persistent_client = chromadb.PersistentClient

    def persistent_client_with_temp_path(*args, **kwargs):
        # Replace any path argument with our temp directory
        kwargs["path"] = temp_db_dir
        return original_persistent_client(*args, **kwargs)

    # Patch at the module level where it's imported
    with (
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.load_all_cases",
            return_value=sample_cases_with_complete_metadata,
        ),
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.SentenceTransformer",
            return_value=mock_embedding_model,
        ),
        patch(
            "cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient",
            side_effect=persistent_client_with_temp_path,
        ),
    ):
        # Run the main setup function
        main()

    # Verify documents and metadata separation
    client = chromadb.PersistentClient(path=temp_db_dir)
    collection = client.get_collection(name="code_solutions_case_base")

    # Retrieve all cases with both documents and metadata
    all_results = collection.get(include=["documents", "metadatas"])

    # Assertion 1: Documents contain solution code
    for i, document in enumerate(all_results["documents"]):
        expected_solution = sample_cases_with_complete_metadata[i]["solution"]
        assert (
            document == expected_solution
        ), f"Document should contain solution code for case {i}"

    # Assertion 2: Solution is NOT in metadata
    for metadata in all_results["metadatas"]:
        assert (
            "solution" not in metadata
        ), "Solution should NOT be stored in metadata (should be in documents)"

    # Assertion 3: Document content is retrievable
    first_result = collection.get(ids=["id0"], include=["documents"])
    assert len(first_result["documents"]) == 1, "Should retrieve one document"
    assert (
        first_result["documents"][0]
        == sample_cases_with_complete_metadata[0]["solution"]
    ), "Retrieved document should match original solution"

    # Assertion 4: Verify all expected documents are present
    assert len(all_results["documents"]) == len(
        sample_cases_with_complete_metadata
    ), "All solutions should be stored as documents"
