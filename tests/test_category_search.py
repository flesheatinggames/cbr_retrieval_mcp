"""
Integration tests for category-based search functionality.

This test suite verifies that the cbr_search_category function correctly filters
cases by category and subcategory using the complete metadata stored in ChromaDB.

These tests are designed to FAIL initially as they test the bug fix implementation
for the metadata storage bug documented in:
@.agent-os/specs/2025-11-04-metadata-storage-bug-fix/spec.md

The current database has broken metadata (only stores "problem" field, missing
category/subcategory/tags), so category-based queries will fail. After the metadata
bug is fixed in setup_vectordb.py, these tests should pass.

Test Group: Category-Based Search Functionality (from tests.md)

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
    return f"test_collection_{uuid.uuid4().hex}"


# Add the src directory to path for importing cbr_mcp_server
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
sys.path.insert(0, src_path)

# Import from the cbr_mcp_server package
from cbr_mcp_server import CBRServerConfig, ProductionCBRRetriever, StructuredLogger

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
    temp_dir = tempfile.mkdtemp(prefix="cbr_test_category_search_")
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
        # Handle both single text and list of texts
        if isinstance(texts, str):
            texts = [texts]

        embeddings = []
        for i, text in enumerate(texts):
            # Create a simple deterministic embedding based on text hash
            text_hash = hash(text) % 100
            embedding = [
                0.1 + text_hash * 0.001,
                0.2 + text_hash * 0.001,
                0.3 + text_hash * 0.001,
            ]
            embeddings.append(embedding)

        # Return single list if input was single string, else list of lists
        return (
            embeddings
            if len(embeddings) > 1 or not isinstance(texts, list)
            else embeddings[0]
        )

    mock_model.encode = mock_encode
    return mock_model


@pytest.fixture
def sample_cases_for_category_search():
    """
    Fixture providing a diverse set of cases for category search testing.

    Returns cases spanning multiple categories and subcategories:
    - orchestration (planning, delegation)
    - firebase (auth)
    - rust (database, api)
    """
    return [
        # Orchestration - planning cases
        {
            "problem": "How to plan a multi-step agent workflow",
            "solution": "Use sequential delegation with verification checkpoints",
            "category": "orchestration",
            "subcategory": "planning",
            "tags": ["orchestration", "planning", "delegation"],
        },
        {
            "problem": "How to create a detailed implementation plan",
            "solution": "Break down features into verifiable units of work",
            "category": "orchestration",
            "subcategory": "planning",
            "tags": ["orchestration", "planning", "decomposition"],
        },
        # Orchestration - delegation cases
        {
            "problem": "How to delegate tasks to specialist agents",
            "solution": "Use delegation protocol with clear objectives",
            "category": "orchestration",
            "subcategory": "delegation",
            "tags": ["orchestration", "delegation", "agents"],
        },
        # Firebase - auth cases
        {
            "problem": "How to implement Firebase authentication",
            "solution": "Use firebase.auth().signInWithEmailAndPassword(...)",
            "category": "firebase",
            "subcategory": "auth",
            "tags": ["authentication", "firebase", "login"],
        },
        {
            "problem": "How to handle Firebase auth errors",
            "solution": "Use try-catch with specific error codes",
            "category": "firebase",
            "subcategory": "auth",
            "tags": ["firebase", "auth", "error-handling"],
        },
        # Firebase - database cases
        {
            "problem": "How to query Firestore collections",
            "solution": "Use collection.where() with query constraints",
            "category": "firebase",
            "subcategory": "database",
            "tags": ["firebase", "firestore", "query"],
        },
        # Rust - database cases
        {
            "problem": "How to implement async database operations in Rust",
            "solution": "Use tokio with async database drivers",
            "category": "rust",
            "subcategory": "database",
            "tags": ["rust", "async", "database"],
        },
        {
            "problem": "How to handle database errors in Rust",
            "solution": "Use Result types with custom error enums",
            "category": "rust",
            "subcategory": "database",
            "tags": ["rust", "error-handling", "database"],
        },
    ]


@pytest.fixture
def populated_db_with_complete_metadata(
    temp_db_dir,
    mock_embedding_model,
    sample_cases_for_category_search,
    unique_collection_name,
):
    """
    Create and populate a test database with complete metadata.

    This simulates what the database SHOULD look like after the metadata bug is fixed.
    Returns a client, collection, and collection name ready for category-based queries.
    """
    # Create ChromaDB client and collection with unique name
    client = chromadb.PersistentClient(path=temp_db_dir)
    collection = client.create_collection(name=unique_collection_name)

    # Extract data from cases
    problems = [case["problem"] for case in sample_cases_for_category_search]
    solutions = [case["solution"] for case in sample_cases_for_category_search]
    ids = [f"id{i}" for i in range(len(sample_cases_for_category_search))]

    # Generate embeddings
    embeddings = mock_embedding_model.encode(problems)

    # Build COMPLETE metadata (this is what the fix should produce)
    metadatas = [
        {
            "problem": case["problem"],
            "category": case.get("category", "unknown"),
            "subcategory": case.get("subcategory", "unknown"),
            "tags": ",".join(case.get("tags", [])),
        }
        for case in sample_cases_for_category_search
    ]

    # Add to collection with complete metadata
    collection.add(
        embeddings=embeddings,
        documents=solutions,
        metadatas=metadatas,
        ids=ids,
    )

    return client, collection, unique_collection_name


@pytest.fixture
def test_retriever(
    temp_db_dir,
    mock_embedding_model,
    unique_collection_name,
    populated_db_with_complete_metadata,
):
    """
    Create a ProductionCBRRetriever instance for testing.

    Returns a retriever configured with the temporary database and mock embedding model.
    The retriever uses the same collection name as populated_db_with_complete_metadata
    to ensure test isolation during parallel execution.
    """
    # Get the collection name from the populated database to ensure consistency
    _, _, collection_name = populated_db_with_complete_metadata

    # Create config pointing to temporary database with the SAME collection name
    config = CBRServerConfig(
        database_path=temp_db_dir,
        collection_name=collection_name,
        use_real_db=True,
    )

    # Create a mock logger
    mock_logger = Mock(spec=StructuredLogger)
    mock_logger.info = Mock()
    mock_logger.debug = Mock()
    mock_logger.warning = Mock()
    mock_logger.error = Mock()

    # Create retriever instance
    retriever = ProductionCBRRetriever(config=config, logger=mock_logger)

    # Override the embedding model with our mock
    retriever.embedding_model = mock_embedding_model

    return retriever


# ============================================================================
# Test 1: Search by Category - Orchestration
# ============================================================================


@pytest.mark.asyncio
async def test_search_by_category_orchestration(
    populated_db_with_complete_metadata, test_retriever
):
    """
    Test that searching by category="orchestration" returns orchestration cases.

    Given: Database with complete metadata including orchestration cases
    When: Calling search_by_category(category="orchestration")
    Then:
      - Query succeeds (no error)
      - Returns approximately 3 orchestration cases from sample data
      - All returned cases have category="orchestration" in metadata
    """
    # Ensure database is populated before test
    client, collection, _ = populated_db_with_complete_metadata

    # Execute category search using the test retriever
    results = await test_retriever.search_by_category(
        category="orchestration", limit=50
    )

    # Assertion 1: Query succeeds (no exception raised)
    assert results is not None, "Query should return results, not None"

    # Assertion 2: Returns approximately 3 orchestration cases from sample data
    assert len(results) == 3, f"Expected 3 orchestration cases, got {len(results)}"

    # Assertion 3: All returned cases have category="orchestration"
    for result in results:
        metadata = result.get("metadata", {})
        assert "category" in metadata, "Result metadata should contain 'category' field"
        assert (
            metadata["category"] == "orchestration"
        ), f"Expected category='orchestration', got '{metadata.get('category')}'"


# ============================================================================
# Test 2: Search by Category - Firebase
# ============================================================================


@pytest.mark.asyncio
async def test_search_by_category_firebase(
    populated_db_with_complete_metadata, test_retriever
):
    """
    Test that searching by category="firebase" returns only firebase cases.

    Given: Database with complete metadata including firebase cases
    When: Calling search_by_category(category="firebase")
    Then:
      - Query succeeds
      - Returns firebase cases (3 in sample data: 2 auth + 1 database)
      - All returned cases have category="firebase"
    """
    # Ensure database is populated before test
    client, collection, _ = populated_db_with_complete_metadata

    # Execute category search using the test retriever
    results = await test_retriever.search_by_category(category="firebase", limit=50)

    # Assertion 1: Query succeeds
    assert results is not None, "Query should return results, not None"

    # Assertion 2: Returns firebase cases (3 firebase cases in sample data)
    assert len(results) == 3, f"Expected 3 firebase cases, got {len(results)}"

    # Assertion 3: All returned cases have category="firebase"
    for result in results:
        metadata = result.get("metadata", {})
        assert "category" in metadata, "Result metadata should contain 'category' field"
        assert (
            metadata["category"] == "firebase"
        ), f"Expected category='firebase', got '{metadata.get('category')}'"


# ============================================================================
# Test 3: Search by Category - Rust
# ============================================================================


@pytest.mark.asyncio
async def test_search_by_category_rust(
    populated_db_with_complete_metadata, test_retriever
):
    """
    Test that searching by category="rust" returns only rust cases.

    Given: Database with complete metadata including rust cases
    When: Calling search_by_category(category="rust")
    Then:
      - Query succeeds
      - Returns rust cases (2 in sample data)
      - All returned cases have category="rust"
    """
    # Ensure database is populated before test
    client, collection, _ = populated_db_with_complete_metadata

    # Execute category search using the test retriever
    results = await test_retriever.search_by_category(category="rust", limit=50)

    # Assertion 1: Query succeeds
    assert results is not None, "Query should return results, not None"

    # Assertion 2: Returns rust cases (2 rust cases in sample data)
    assert len(results) == 2, f"Expected 2 rust cases, got {len(results)}"

    # Assertion 3: All returned cases have category="rust"
    for result in results:
        metadata = result.get("metadata", {})
        assert "category" in metadata, "Result metadata should contain 'category' field"
        assert (
            metadata["category"] == "rust"
        ), f"Expected category='rust', got '{metadata.get('category')}'"


# ============================================================================
# Test 4: Search by Category and Subcategory
# ============================================================================


@pytest.mark.asyncio
async def test_search_by_category_and_subcategory(
    populated_db_with_complete_metadata, test_retriever
):
    """
    Test that filtering by both category and subcategory returns only matching cases.

    Given: Database with orchestration cases of different subcategories
    When: Calling search_by_category(category="orchestration", subcategory="planning")
    Then:
      - Query succeeds
      - Returns only orchestration planning cases (2 in sample)
      - All returned cases have BOTH category="orchestration" AND subcategory="planning"
    """
    # Ensure database is populated before test
    client, collection, _ = populated_db_with_complete_metadata

    # Execute category + subcategory search using the test retriever
    results = await test_retriever.search_by_category(
        category="orchestration", subcategory="planning", limit=50
    )

    # Assertion 1: Query succeeds
    assert results is not None, "Query should return results, not None"

    # Assertion 2: Returns only planning cases (2 in sample data)
    assert (
        len(results) == 2
    ), f"Expected 2 orchestration planning cases, got {len(results)}"

    # Assertion 3: All cases have both category="orchestration" AND subcategory="planning"
    for result in results:
        metadata = result.get("metadata", {})
        assert "category" in metadata, "Result metadata should contain 'category' field"
        assert (
            "subcategory" in metadata
        ), "Result metadata should contain 'subcategory' field"
        assert (
            metadata["category"] == "orchestration"
        ), f"Expected category='orchestration', got '{metadata.get('category')}'"
        assert (
            metadata["subcategory"] == "planning"
        ), f"Expected subcategory='planning', got '{metadata.get('subcategory')}'"


# ============================================================================
# Test 5: Search by Category with Query Text
# ============================================================================


@pytest.mark.asyncio
async def test_search_by_category_with_query_text(
    populated_db_with_complete_metadata, test_retriever
):
    """
    Test that adding a query text filters results by semantic similarity.

    Given: Database with orchestration cases
    When: Calling search_by_category(category="orchestration", query="delegation pattern")
    Then:
      - Query succeeds
      - Returns orchestration cases
      - All returned cases have category="orchestration"
      - Results should be filtered/ranked by similarity (may be fewer than all orchestration cases)
    """
    # Ensure database is populated before test
    client, collection, _ = populated_db_with_complete_metadata

    # Execute category search with query text using the test retriever
    results = await test_retriever.search_by_category(
        category="orchestration", query="delegation pattern", limit=50
    )

    # Assertion 1: Query succeeds
    assert results is not None, "Query should return results, not None"

    # Assertion 2: Returns orchestration cases (may be filtered by similarity)
    assert (
        len(results) > 0
    ), "Should return at least some orchestration cases matching query"
    assert (
        len(results) <= 3
    ), "Should not return more orchestration cases than exist in sample"

    # Assertion 3: All returned cases have category="orchestration"
    for result in results:
        metadata = result.get("metadata", {})
        assert "category" in metadata, "Result metadata should contain 'category' field"
        assert (
            metadata["category"] == "orchestration"
        ), f"Expected category='orchestration', got '{metadata.get('category')}'"


# ============================================================================
# Test 6: Search Nonexistent Category
# ============================================================================


@pytest.mark.asyncio
async def test_search_nonexistent_category(test_retriever):
    """
    Test that searching for a non-existent category returns empty results.

    Given: Database with any metadata
    When: Calling search_by_category(category="nonexistent")
    Then: Returns empty list (no error raised)
    """
    # Assertion: Should return empty results for non-existent category
    results = await test_retriever.search_by_category(category="nonexistent", limit=10)

    # Verify empty results (category doesn't exist in database)
    assert isinstance(results, list), "Should return a list"
    assert (
        len(results) == 0
    ), f"Should return empty results for non-existent category, got {len(results)} results"


# ============================================================================
# Test 7: Search Invalid Subcategory for Category
# ============================================================================


@pytest.mark.asyncio
async def test_search_invalid_subcategory_for_category(test_retriever):
    """
    Test that searching with an invalid subcategory for a category raises ValueError.

    Given: Database with any metadata
    When: Calling search_by_category(category="orchestration", subcategory="invalid")
    Then: Raises ValueError with message about invalid subcategory
    """
    # Assertion: Should raise ValueError for invalid subcategory
    with pytest.raises(ValueError) as exc_info:
        await test_retriever.search_by_category(
            category="orchestration", subcategory="invalid", limit=10
        )

    # Verify error message mentions invalid subcategory
    error_message = str(exc_info.value)
    assert (
        "Invalid subcategory" in error_message or "subcategory" in error_message.lower()
    ), f"Error message should mention invalid subcategory, got: {error_message}"
    assert (
        "invalid" in error_message
    ), f"Error message should mention the invalid subcategory name, got: {error_message}"
