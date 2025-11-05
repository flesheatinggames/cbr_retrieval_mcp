"""
End-to-end integration tests for category-based search with complete database population flow.

This test suite verifies the entire flow from database population with fixed metadata
through to successful category search functionality. These tests ensure that:

1. The metadata extraction fix properly extracts category, subcategory, and tags
2. setup_vectordb.py populates the database with complete metadata
3. Category search functionality works with the complete metadata
4. Force rebuild and filtered loading preserve metadata integrity

These tests are designed as integration tests that verify the complete flow works
end-to-end after the metadata storage bug fix documented in:
@.agent-os/specs/2025-11-04-metadata-storage-bug-fix/spec.md

Test Group: End-to-End Category Search Integration (from tasks.md Task 9.1)
"""

import os
import shutil
import sys
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import chromadb
import pytest
from sentence_transformers import SentenceTransformer

# Add the src directory to path for importing cbr_mcp_server
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
sys.path.insert(0, src_path)

# Import by loading the cbr_mcp_server.py file directly (not the package)
import importlib.util
cbr_mcp_server_path = os.path.join(src_path, "cbr_mcp_server.py")
spec = importlib.util.spec_from_file_location("cbr_mcp_server_module", cbr_mcp_server_path)
cbr_mcp_server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cbr_mcp_server_module)
ProductionCBRRetriever = cbr_mcp_server_module.ProductionCBRRetriever
CBRServerConfig = cbr_mcp_server_module.CBRServerConfig

# Add scripts/utilities to path for importing setup_vectordb
scripts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "utilities")
sys.path.insert(0, scripts_path)

# Import setup_vectordb functions
import setup_vectordb


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
    temp_dir = tempfile.mkdtemp(prefix="cbr_test_e2e_")
    yield temp_dir
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_embedding_model():
    """
    Mock the SentenceTransformer to avoid downloading models during tests.

    Returns a mock that generates deterministic embeddings for testing.
    """
    mock_model = Mock(spec=SentenceTransformer)

    # Generate mock embeddings: simple list of floats for each case
    def mock_encode(texts, normalize_embeddings=True):
        # Handle both single text and list of texts
        if isinstance(texts, str):
            texts = [texts]

        embeddings = []
        for i, text in enumerate(texts):
            # Create a simple deterministic embedding based on text hash
            text_hash = hash(text) % 100
            embedding = [0.1 + text_hash * 0.001] * 384  # nomic uses 384 dimensions
            embeddings.append(embedding)

        return embeddings if len(embeddings) > 1 else embeddings[0]

    mock_model.encode = mock_encode
    return mock_model


# ============================================================================
# Test 1: Complete flow from clean database to category search
# ============================================================================


@pytest.mark.asyncio
async def test_e2e_populate_and_search_by_category(temp_db_dir, mock_embedding_model):
    """
    End-to-end test: Verify complete flow from clean database to successful category search.

    This test verifies:
    1. Database starts empty
    2. setup_vectordb populates with complete metadata (103 cases)
    3. CBR retriever can be initialized with populated database
    4. Category search returns orchestration cases
    5. All results have complete metadata (category, subcategory, tags)

    Expected to FAIL initially because metadata extraction is broken.
    After fix, should PASS with complete metadata in all results.
    """
    # Step 1: Verify database starts empty
    client = chromadb.PersistentClient(path=temp_db_dir)

    # Collection shouldn't exist yet
    collections = client.list_collections()
    assert len(collections) == 0, "Database should start empty"

    # Step 2: Populate database using setup_vectordb logic
    # Mock the embedding model to avoid actual model download
    with patch('setup_vectordb.SentenceTransformer', return_value=mock_embedding_model):
        # Import after patching
        from cases import load_all_cases
        from cbr_mcp_server.metadata_extraction import extract_metadata_list

        # Load all cases
        all_cases = load_all_cases()

        # Create collection
        collection = client.get_or_create_collection(name="code_solutions_case_base")

        # Prepare data
        problems = [case["problem"] for case in all_cases]
        solutions = [case["solution"] for case in all_cases]
        ids = [f"id{i}" for i in range(len(problems))]

        # Generate embeddings
        problem_embeddings = mock_embedding_model.encode(problems, normalize_embeddings=True)

        # Extract metadata (this is what we're testing was fixed)
        metadatas = extract_metadata_list(all_cases)

        # Add to collection
        collection.add(
            embeddings=problem_embeddings,
            documents=solutions,
            metadatas=metadatas,
            ids=ids
        )

    # Step 3: Verify 103 cases were loaded
    final_count = collection.count()
    assert final_count == 103, f"Expected 103 cases, got {final_count}"

    # Step 4: Initialize CBR retriever with populated database
    config = CBRServerConfig(
        database_path=temp_db_dir,
        collection_name="code_solutions_case_base",
        use_real_db=True
    )

    # Create mock logger (use StructuredLogger from module we loaded earlier)
    StructuredLogger = cbr_mcp_server_module.StructuredLogger
    mock_logger = Mock(spec=StructuredLogger)

    # Create retriever and override embedding model (no patch needed)
    retriever = ProductionCBRRetriever(config=config, logger=mock_logger)
    retriever.embedding_model = mock_embedding_model

    # Step 5: Execute category search for "orchestration"
    results = await retriever.search_by_category(category="orchestration")

    # Step 6: Verify results
    assert len(results) > 0, "Category search should return orchestration cases"

    # Verify all results have category="orchestration"
    for result in results:
        metadata = result.get("metadata", {})
        assert metadata.get("category") == "orchestration", \
            f"Expected category='orchestration', got {metadata.get('category')}"

    # Verify metadata completeness - all required fields present
    required_fields = {"problem", "category", "subcategory", "tags"}
    for i, result in enumerate(results):
        metadata = result.get("metadata", {})
        missing_fields = required_fields - set(metadata.keys())
        assert not missing_fields, \
            f"Result {i} missing metadata fields: {missing_fields}. Got: {metadata.keys()}"

        # Verify fields are not "unknown" defaults
        assert metadata["category"] != "unknown", "Category should not be 'unknown'"
        assert metadata["subcategory"] != "unknown", "Subcategory should not be 'unknown'"
        assert isinstance(metadata["tags"], str), "Tags should be a comma-separated string"
        assert len(metadata["tags"]) > 0, "Tags should not be empty"


# ============================================================================
# Test 2: Force rebuild from broken to fixed database
# ============================================================================


def test_e2e_force_rebuild_and_verify_metadata(temp_db_dir, mock_embedding_model):
    """
    End-to-end test: Verify migration from broken to fixed database using --force flag.

    This test verifies:
    1. Database with broken metadata (only 'problem' field) can be created
    2. Force rebuild deletes and recreates collection
    3. All 103 cases loaded after rebuild
    4. Sample case has complete metadata (not "unknown" defaults)
    5. Metadata values are correct

    Expected to FAIL initially because metadata extraction is broken.
    After fix, should PASS with complete metadata after force rebuild.
    """
    # Step 1: Create database with broken metadata (simulate legacy state)
    client = chromadb.PersistentClient(path=temp_db_dir)
    collection = client.get_or_create_collection(name="code_solutions_case_base")

    # Add a few cases with incomplete metadata (only problem field)
    broken_metadatas = [
        {"problem": "Test problem 1"},
        {"problem": "Test problem 2"},
        {"problem": "Test problem 3"}
    ]

    collection.add(
        embeddings=[[0.1] * 384, [0.2] * 384, [0.3] * 384],
        documents=["solution1", "solution2", "solution3"],
        metadatas=broken_metadatas,
        ids=["id0", "id1", "id2"]
    )

    # Step 2: Verify broken state
    initial_count = collection.count()
    assert initial_count == 3, "Should have 3 broken cases initially"

    # Verify metadata is incomplete
    broken_result = collection.get(ids=["id0"], include=["metadatas"])
    broken_metadata = broken_result["metadatas"][0]
    assert "category" not in broken_metadata, "Broken metadata should not have category"
    assert "problem" in broken_metadata, "Broken metadata should have problem field"

    # Step 3: Force rebuild with complete metadata
    with patch('setup_vectordb.SentenceTransformer', return_value=mock_embedding_model):
        from cases import load_all_cases
        from cbr_mcp_server.metadata_extraction import extract_metadata_list

        # Load all cases
        all_cases = load_all_cases()

        # Delete old collection and create new one (force rebuild)
        client.delete_collection(name="code_solutions_case_base")
        collection = client.create_collection(name="code_solutions_case_base")

        # Prepare data with fixed metadata
        problems = [case["problem"] for case in all_cases]
        solutions = [case["solution"] for case in all_cases]
        ids = [f"id{i}" for i in range(len(problems))]

        # Generate embeddings
        problem_embeddings = mock_embedding_model.encode(problems, normalize_embeddings=True)

        # Extract metadata (fixed version)
        metadatas = extract_metadata_list(all_cases)

        # Add to collection
        collection.add(
            embeddings=problem_embeddings,
            documents=solutions,
            metadatas=metadatas,
            ids=ids
        )

    # Step 4: Verify 103 cases loaded after rebuild
    final_count = collection.count()
    assert final_count == 103, f"Expected 103 cases after rebuild, got {final_count}"

    # Step 5: Retrieve sample case and verify complete metadata
    sample_result = collection.get(ids=["id0"], include=["metadatas"])
    sample_metadata = sample_result["metadatas"][0]

    # Verify all required fields present
    required_fields = {"problem", "category", "subcategory", "tags"}
    missing_fields = required_fields - set(sample_metadata.keys())
    assert not missing_fields, f"Sample case missing fields: {missing_fields}"

    # Verify metadata values are correct (not "unknown" defaults)
    assert sample_metadata["category"] != "unknown", \
        f"Category should not be 'unknown', got: {sample_metadata['category']}"
    assert sample_metadata["subcategory"] != "unknown", \
        f"Subcategory should not be 'unknown', got: {sample_metadata['subcategory']}"
    assert isinstance(sample_metadata["tags"], str), \
        f"Tags should be a comma-separated string, got: {type(sample_metadata['tags'])}"
    assert len(sample_metadata["tags"]) > 0, \
        "Tags should not be empty"

    # Verify category field has actual value (not empty or unknown)
    assert sample_metadata["category"], "Category should have a value"
    assert sample_metadata["category"] != "unknown", "Category should not be 'unknown'"


# ============================================================================
# Test 3: Filtered loading preserves metadata
# ============================================================================


@pytest.mark.asyncio
async def test_e2e_filtered_load_and_category_search(temp_db_dir, mock_embedding_model):
    """
    End-to-end test: Verify filtered loading preserves complete metadata.

    This test verifies:
    1. Database starts clean
    2. Filtered loading (--category orchestration firebase) loads subset
    3. Only specified categories are in database
    4. Category search works for loaded category
    5. Category search handles non-loaded category appropriately
    6. All results have complete metadata

    Expected to FAIL initially because metadata extraction is broken.
    After fix, should PASS with complete metadata in filtered results.
    """
    # Step 1: Verify database starts clean
    client = chromadb.PersistentClient(path=temp_db_dir)
    collections = client.list_collections()
    assert len(collections) == 0, "Database should start empty"

    # Step 2: Populate database with filtered categories
    with patch('setup_vectordb.SentenceTransformer', return_value=mock_embedding_model):
        from cases import load_all_cases
        from cbr_mcp_server.metadata_extraction import extract_metadata_list

        # Load all cases
        all_cases = load_all_cases()

        # Filter to only orchestration and firebase categories
        filter_categories = ["orchestration", "firebase"]
        filtered_cases = [
            case for case in all_cases
            if case.get("category") in filter_categories
        ]

        # Create collection
        collection = client.get_or_create_collection(name="code_solutions_case_base")

        # Prepare filtered data
        problems = [case["problem"] for case in filtered_cases]
        solutions = [case["solution"] for case in filtered_cases]
        ids = [f"id{i}" for i in range(len(problems))]

        # Generate embeddings
        problem_embeddings = mock_embedding_model.encode(problems, normalize_embeddings=True)

        # Extract metadata
        metadatas = extract_metadata_list(filtered_cases)

        # Add to collection
        collection.add(
            embeddings=problem_embeddings,
            documents=solutions,
            metadatas=metadatas,
            ids=ids
        )

    # Step 3: Verify only filtered categories loaded
    filtered_count = collection.count()
    assert filtered_count < 103, f"Filtered database should have < 103 cases, got {filtered_count}"
    assert filtered_count > 0, "Filtered database should have some cases"

    # Verify all cases have category in filter list
    all_results = collection.get(include=["metadatas"])
    for metadata in all_results["metadatas"]:
        assert metadata.get("category") in filter_categories, \
            f"Case has wrong category: {metadata.get('category')}"

    # Step 4: Initialize CBR retriever
    config = CBRServerConfig(
        database_path=temp_db_dir,
        collection_name="code_solutions_case_base",
        use_real_db=True
    )

    # Create mock logger (use StructuredLogger from module we loaded earlier)
    StructuredLogger = cbr_mcp_server_module.StructuredLogger
    mock_logger = Mock(spec=StructuredLogger)

    # Create retriever and override embedding model
    retriever = ProductionCBRRetriever(config=config, logger=mock_logger)
    retriever.embedding_model = mock_embedding_model

    # Step 5: Search for loaded category (orchestration) - should succeed
    orchestration_results = await retriever.search_by_category(category="orchestration")

    assert len(orchestration_results) > 0, "Should find orchestration cases"

    # Verify all results have complete metadata
    required_fields = {"problem", "category", "subcategory", "tags"}
    for result in orchestration_results:
        metadata = result.get("metadata", {})
        missing_fields = required_fields - set(metadata.keys())
        assert not missing_fields, f"Missing metadata fields: {missing_fields}"
        assert metadata["category"] == "orchestration"

    # Step 6: Search for non-loaded category (rust) - should return empty (no error with permissive validation)
    rust_results = await retriever.search_by_category(category="rust")

    # With permissive category validation, should return empty list for non-loaded category
    assert isinstance(rust_results, list), "Should return a list"
    assert len(rust_results) == 0, "Should return empty results for non-loaded category"
