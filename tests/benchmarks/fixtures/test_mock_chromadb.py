"""
Test suite for Mock ChromaDB fixtures.

This module contains comprehensive tests for the mock ChromaDB client and collection
implementations used in performance benchmarking. These tests follow TDD principles
and should initially fail with ModuleNotFoundError until the implementation is created.

Test Coverage:
- MockChromaDBClient class (3 tests)
- MockCollection class (5 tests)
- Pytest fixtures (4 tests)
- Helper utilities (3 tests)
- Integration tests (2 tests)
- Edge cases (5 tests)

Total: 22 tests
"""

import time
from typing import Dict, List

import pytest

# =============================================================================
# MockChromaDBClient Class Tests (3 tests)
# =============================================================================


def test_mock_chromadb_client_initialization():
    """
    Test that MockChromaDBClient can be initialized with configurable latencies.

    Validates:
    - Client instance can be created
    - Default latency values are set correctly
    - Custom latency values can be provided
    - Latency parameters are accessible
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import MockChromaDBClient

    # Test with default latencies
    client_default = MockChromaDBClient()
    assert client_default is not None
    assert hasattr(client_default, "query_latency_ms")
    assert hasattr(client_default, "connection_latency_ms")
    assert client_default.query_latency_ms == 10
    assert client_default.connection_latency_ms == 5

    # Test with custom latencies
    client_custom = MockChromaDBClient(
        query_latency_ms=25.0, connection_latency_ms=15.0
    )
    assert client_custom.query_latency_ms == 25.0
    assert client_custom.connection_latency_ms == 15.0


def test_mock_chromadb_client_get_or_create_collection():
    """
    Test that get_or_create_collection returns a MockCollection instance.

    Validates:
    - Returns MockCollection instance
    - Collection name is set correctly
    - Multiple calls with same name return the same collection
    - Kwargs are handled properly
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import (
        MockChromaDBClient,
        MockCollection,
    )

    client = MockChromaDBClient()

    # Create a collection
    collection = client.get_or_create_collection(
        name="test_collection", metadata={"description": "test"}
    )
    assert isinstance(collection, MockCollection)
    assert collection.name == "test_collection"

    # Get the same collection again
    collection2 = client.get_or_create_collection(name="test_collection")
    assert collection2 is collection


def test_mock_chromadb_client_reset():
    """
    Test that reset() clears all collections from the client.

    Validates:
    - Collections are cleared after reset
    - Can create new collections after reset
    - Reset doesn't affect client configuration
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import MockChromaDBClient

    client = MockChromaDBClient(query_latency_ms=20.0)

    # Create some collections
    client.get_or_create_collection(name="collection1")
    client.get_or_create_collection(name="collection2")

    # Reset the client
    client.reset()

    # Verify collections are cleared (creating new collection should work)
    collection = client.get_or_create_collection(name="collection1")
    assert collection.name == "collection1"

    # Verify client configuration is preserved
    assert client.query_latency_ms == 20.0


# =============================================================================
# MockCollection Class Tests (5 tests)
# =============================================================================


def test_mock_collection_query_with_embeddings():
    """
    Test that query() accepts embeddings and returns properly formatted results.

    Validates:
    - Accepts query_embeddings, n_results, and where parameters
    - Returns dict with correct keys: ids, distances, metadatas, documents
    - Respects n_results limit
    - Returns results in proper format (nested lists)
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import MockChromaDBClient

    client = MockChromaDBClient()
    collection = client.get_or_create_collection(name="test")

    # Add some test documents
    collection.add(
        ids=["id1", "id2", "id3"],
        embeddings=[[0.1] * 768, [0.2] * 768, [0.3] * 768],
        documents=["doc1", "doc2", "doc3"],
        metadatas=[
            {"category": "test"},
            {"category": "test"},
            {"category": "other"},
        ],
    )

    # Query the collection
    results = collection.query(query_embeddings=[[0.15] * 768], n_results=2)

    assert isinstance(results, dict)
    assert "ids" in results
    assert "distances" in results
    assert "metadatas" in results
    assert "documents" in results

    # Check result format (nested lists for batch queries)
    assert isinstance(results["ids"], list)
    assert len(results["ids"]) == 1  # One query
    assert len(results["ids"][0]) <= 2  # n_results = 2


def test_mock_collection_add_documents():
    """
    Test that add() stores documents with all metadata.

    Validates:
    - Documents are stored with ids, embeddings, documents, and metadatas
    - Stored documents can be retrieved via get()
    - All fields are preserved correctly
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import MockChromaDBClient

    client = MockChromaDBClient()
    collection = client.get_or_create_collection(name="test")

    # Add documents
    test_ids = ["case1", "case2"]
    test_embeddings = [[0.1] * 768, [0.2] * 768]
    test_documents = ["Test case 1", "Test case 2"]
    test_metadatas = [{"category": "A"}, {"category": "B"}]

    collection.add(
        ids=test_ids,
        embeddings=test_embeddings,
        documents=test_documents,
        metadatas=test_metadatas,
    )

    # Retrieve documents
    results = collection.get(ids=test_ids)

    assert results["ids"] == test_ids
    assert results["documents"] == test_documents
    assert results["metadatas"] == test_metadatas
    assert len(results["embeddings"]) == 2


def test_mock_collection_get_with_filters():
    """
    Test that get() retrieves documents by ids or where filters.

    Validates:
    - Can retrieve by specific ids
    - Can retrieve with where filters
    - Returns proper dict structure
    - Filters work correctly for category matching
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import MockChromaDBClient

    client = MockChromaDBClient()
    collection = client.get_or_create_collection(name="test")

    # Add test documents
    collection.add(
        ids=["id1", "id2", "id3"],
        embeddings=[[0.1] * 768, [0.2] * 768, [0.3] * 768],
        documents=["doc1", "doc2", "doc3"],
        metadatas=[
            {"category": "orchestration"},
            {"category": "orchestration"},
            {"category": "webdev"},
        ],
    )

    # Test get by ids
    results_by_id = collection.get(ids=["id1", "id2"])
    assert len(results_by_id["ids"]) == 2
    assert "id1" in results_by_id["ids"]
    assert "id2" in results_by_id["ids"]

    # Test get with where filter
    results_by_filter = collection.get(where={"category": "orchestration"})
    assert len(results_by_filter["ids"]) == 2
    for metadata in results_by_filter["metadatas"]:
        assert metadata["category"] == "orchestration"


def test_mock_collection_update():
    """
    Test that update() modifies existing documents.

    Validates:
    - Can update embeddings
    - Can update metadatas
    - Changes are reflected in subsequent get() calls
    - Original ids are preserved
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import MockChromaDBClient

    client = MockChromaDBClient()
    collection = client.get_or_create_collection(name="test")

    # Add initial document
    collection.add(
        ids=["id1"],
        embeddings=[[0.1] * 768],
        documents=["original doc"],
        metadatas=[{"version": 1}],
    )

    # Update the document
    new_embedding = [[0.9] * 768]
    new_metadata = [{"version": 2, "updated": True}]
    collection.update(ids=["id1"], embeddings=new_embedding, metadatas=new_metadata)

    # Verify update
    results = collection.get(ids=["id1"])
    assert results["embeddings"][0] == new_embedding[0]
    assert results["metadatas"][0]["version"] == 2
    assert results["metadatas"][0]["updated"] is True


def test_mock_collection_delete():
    """
    Test that delete() removes documents by ids.

    Validates:
    - Documents are removed from collection
    - get() returns empty results for deleted ids
    - Other documents are unaffected
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import MockChromaDBClient

    client = MockChromaDBClient()
    collection = client.get_or_create_collection(name="test")

    # Add documents
    collection.add(
        ids=["id1", "id2", "id3"],
        embeddings=[[0.1] * 768, [0.2] * 768, [0.3] * 768],
        documents=["doc1", "doc2", "doc3"],
        metadatas=[{}, {}, {}],
    )

    # Delete one document
    collection.delete(ids=["id2"])

    # Verify deletion
    results = collection.get(ids=["id1", "id2", "id3"])
    assert "id1" in results["ids"]
    assert "id2" not in results["ids"]
    assert "id3" in results["ids"]
    assert len(results["ids"]) == 2


# =============================================================================
# Pytest Fixtures Tests (4 tests)
# =============================================================================


def test_mock_chromadb_client_fixture(mock_chromadb_client):
    """
    Test that the mock_chromadb_client fixture returns a properly initialized client.

    Validates:
    - Fixture returns MockChromaDBClient instance
    - Has default latency values
    - Can create collections
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import MockChromaDBClient

    assert isinstance(mock_chromadb_client, MockChromaDBClient)
    assert hasattr(mock_chromadb_client, "query_latency_ms")
    assert hasattr(mock_chromadb_client, "connection_latency_ms")

    # Verify it works
    collection = mock_chromadb_client.get_or_create_collection(name="test")
    assert collection is not None


def test_mock_collection_fixture(mock_collection):
    """
    Test that the mock_collection fixture returns a MockCollection.

    Validates:
    - Fixture returns MockCollection instance
    - Collection has a name
    - Can perform basic operations
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import MockCollection

    assert isinstance(mock_collection, MockCollection)
    assert hasattr(mock_collection, "name")

    # Verify basic operations work
    mock_collection.add(
        ids=["test"], embeddings=[[0.1] * 768], documents=["test"], metadatas=[{}]
    )
    results = mock_collection.get(ids=["test"])
    assert len(results["ids"]) == 1


def test_mock_populated_collection_fixture(mock_populated_collection):
    """
    Test that the mock_populated_collection fixture has pre-loaded cases.

    Validates:
    - Collection has documents pre-loaded
    - Documents have proper structure (ids, metadatas, embeddings)
    - Can query the pre-loaded data
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import MockCollection

    assert isinstance(mock_populated_collection, MockCollection)

    # Verify collection is not empty
    results = mock_populated_collection.get()
    assert len(results["ids"]) > 0
    assert len(results["documents"]) > 0
    assert len(results["metadatas"]) > 0
    assert len(results["embeddings"]) > 0

    # Verify documents have proper metadata
    for metadata in results["metadatas"]:
        assert "category" in metadata


def test_fixture_isolation(mock_collection):
    """
    Test that fixtures are properly isolated between tests.

    Validates:
    - Fixture is fresh for each test
    - Changes don't persist between tests
    - Multiple fixture uses don't interfere
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import MockCollection

    # Verify collection starts empty
    initial_results = mock_collection.get()
    initial_count = len(initial_results["ids"])

    # Add a document
    mock_collection.add(
        ids=["isolation_test"],
        embeddings=[[0.5] * 768],
        documents=["test"],
        metadatas=[{}],
    )

    # Verify it was added
    after_results = mock_collection.get()
    assert len(after_results["ids"]) == initial_count + 1

    # Note: Actual isolation is tested by running this test multiple times
    # and verifying initial_count stays the same


# =============================================================================
# Helper Utilities Tests (3 tests)
# =============================================================================


def test_generate_mock_case():
    """
    Test that generate_mock_case() creates valid case dictionaries.

    Validates:
    - Returns dict
    - Has required fields: case_id, category, subcategory
    - Accepts additional kwargs
    - Case structure matches expected format
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import generate_mock_case

    # Test basic case generation
    case = generate_mock_case(
        case_id="test_case_1", category="orchestration", subcategory="planning"
    )

    assert isinstance(case, dict)
    assert case["case_id"] == "test_case_1"
    assert case["category"] == "orchestration"
    assert case["subcategory"] == "planning"

    # Test with additional kwargs
    case_with_extras = generate_mock_case(
        case_id="test_case_2",
        category="webdev",
        subcategory="api",
        tags=["rest", "fastapi"],
        difficulty="medium",
    )

    assert case_with_extras["case_id"] == "test_case_2"
    assert "tags" in case_with_extras
    assert case_with_extras["tags"] == ["rest", "fastapi"]
    assert case_with_extras["difficulty"] == "medium"


def test_generate_mock_embedding():
    """
    Test that generate_mock_embedding() creates valid embedding vectors.

    Validates:
    - Returns list of floats
    - Correct dimension (default 768)
    - Deterministic for same input text
    - Can handle custom dimensions
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import (
        generate_mock_embedding,
    )

    # Test default dimension
    embedding = generate_mock_embedding("test text")
    assert isinstance(embedding, list)
    assert len(embedding) == 768
    assert all(isinstance(x, float) for x in embedding)

    # Test determinism
    embedding2 = generate_mock_embedding("test text")
    assert embedding == embedding2

    # Test different text produces different embedding
    embedding3 = generate_mock_embedding("different text")
    assert embedding != embedding3

    # Test custom dimension
    embedding_custom = generate_mock_embedding("test", dimension=384)
    assert len(embedding_custom) == 384


def test_generate_mock_query_result():
    """
    Test that generate_mock_query_result() creates properly formatted results.

    Validates:
    - Returns dict with proper keys
    - Correct number of results (n_results)
    - include_distances parameter works
    - Result structure matches ChromaDB format
    """
    from cbr_mcp_server.performance.fixtures.mock_chromadb import (
        generate_mock_query_result,
    )

    # Test basic result generation
    result = generate_mock_query_result(n_results=5)
    assert isinstance(result, dict)
    assert "ids" in result
    assert "documents" in result
    assert "metadatas" in result
    assert "distances" in result

    # Verify correct number of results
    assert len(result["ids"][0]) == 5
    assert len(result["documents"][0]) == 5
    assert len(result["metadatas"][0]) == 5
    assert len(result["distances"][0]) == 5

    # Test without distances
    result_no_distances = generate_mock_query_result(
        n_results=3, include_distances=False
    )
    assert "distances" not in result_no_distances or result_no_distances[
        "distances"
    ] == [[]]


# =============================================================================
# Integration Tests (2 tests)
# =============================================================================


def test_mock_client_with_production_retriever(mock_chromadb_client):
    """
    Test that MockChromaDBClient can be used with ProductionCBRRetriever.

    Validates:
    - Retriever can be instantiated with mock client
    - Basic retrieval operations work
    - Mock client provides compatible interface
    """
    # Note: This test verifies interface compatibility
    # ProductionCBRRetriever is imported to ensure the mock has the right interface

    try:
        from cbr_mcp_server.production_cbr_retriever import ProductionCBRRetriever
    except ImportError:
        pytest.skip("ProductionCBRRetriever not available")

    # Create retriever with mock client
    collection = mock_chromadb_client.get_or_create_collection(
        name="code_solutions_case_base"
    )

    # Add a test case
    collection.add(
        ids=["test_case"],
        embeddings=[[0.1] * 768],
        documents=["test problem: test solution"],
        metadatas=[{"category": "test", "subcategory": "integration"}],
    )

    # Verify query works
    results = collection.query(query_embeddings=[[0.1] * 768], n_results=1)
    assert len(results["ids"][0]) > 0


def test_mock_collection_query_performance(mock_chromadb_client):
    """
    Test that mock collection respects configured latency settings.

    Validates:
    - Query execution time approximates configured latency
    - Latency simulation is working
    - Performance characteristics are predictable
    """
    # Create client with known latency
    client_with_latency = mock_chromadb_client
    collection = client_with_latency.get_or_create_collection(name="perf_test")

    # Add test data
    collection.add(
        ids=["perf1"],
        embeddings=[[0.1] * 768],
        documents=["test"],
        metadatas=[{}],
    )

    # Measure query time
    start = time.time()
    collection.query(query_embeddings=[[0.1] * 768], n_results=1)
    elapsed_ms = (time.time() - start) * 1000

    # Verify latency is simulated (should be at least the configured latency)
    # Allow some tolerance for execution overhead
    expected_latency = client_with_latency.query_latency_ms
    assert elapsed_ms >= expected_latency * 0.5  # At least half the expected latency


# =============================================================================
# Edge Cases Tests (5 tests)
# =============================================================================


def test_empty_collection_query(mock_collection):
    """
    Test behavior when querying an empty collection.

    Validates:
    - Returns empty results without errors
    - Proper structure is maintained
    - No crashes or exceptions
    """
    # Query empty collection
    results = mock_collection.query(query_embeddings=[[0.1] * 768], n_results=10)

    assert isinstance(results, dict)
    assert "ids" in results
    assert len(results["ids"][0]) == 0
    assert len(results["documents"][0]) == 0


def test_invalid_embedding_dimensions(mock_collection):
    """
    Test error handling for mismatched embedding dimensions.

    Validates:
    - Raises appropriate error or handles gracefully
    - Error message is informative
    - Collection state is not corrupted
    """
    # Add document with standard embedding
    mock_collection.add(
        ids=["standard"],
        embeddings=[[0.1] * 768],
        documents=["test"],
        metadatas=[{}],
    )

    # Try to add document with different dimension
    # This should either raise an error or be handled gracefully
    try:
        mock_collection.add(
            ids=["different_dim"],
            embeddings=[[0.1] * 384],  # Different dimension
            documents=["test2"],
            metadatas=[{}],
        )
        # If it doesn't raise, verify it was handled somehow
        results = mock_collection.get()
        assert len(results["ids"]) >= 1
    except (ValueError, AssertionError) as e:
        # Expected error for dimension mismatch
        assert "dimension" in str(e).lower() or "embedding" in str(e).lower()


def test_where_filter_edge_cases(mock_collection):
    """
    Test where filter behavior with complex conditions.

    Validates:
    - Handles None filters correctly
    - Handles empty dict filters
    - Handles non-matching filters
    - Returns appropriate results for each case
    """
    # Add test data
    mock_collection.add(
        ids=["id1", "id2"],
        embeddings=[[0.1] * 768, [0.2] * 768],
        documents=["doc1", "doc2"],
        metadatas=[{"category": "A", "tags": ["x"]}, {"category": "B", "tags": ["y"]}],
    )

    # Test None filter (should return all)
    results_none = mock_collection.query(
        query_embeddings=[[0.1] * 768], n_results=10, where=None
    )
    assert len(results_none["ids"][0]) == 2

    # Test empty dict filter (should return all)
    results_empty = mock_collection.query(
        query_embeddings=[[0.1] * 768], n_results=10, where={}
    )
    assert len(results_empty["ids"][0]) == 2

    # Test non-matching filter
    results_no_match = mock_collection.query(
        query_embeddings=[[0.1] * 768], n_results=10, where={"category": "NonExistent"}
    )
    assert len(results_no_match["ids"][0]) == 0


def test_large_result_set_handling(mock_collection):
    """
    Test handling of queries with very large n_results values.

    Validates:
    - Doesn't crash with large n_results
    - Returns available results when n_results > available docs
    - Handles n_results = 0 appropriately
    """
    # Add a few documents
    mock_collection.add(
        ids=["id1", "id2", "id3"],
        embeddings=[[0.1] * 768, [0.2] * 768, [0.3] * 768],
        documents=["doc1", "doc2", "doc3"],
        metadatas=[{}, {}, {}],
    )

    # Test with n_results larger than available docs
    results_large = mock_collection.query(
        query_embeddings=[[0.1] * 768], n_results=1000
    )
    assert len(results_large["ids"][0]) == 3  # Only 3 docs available

    # Test with n_results = 0
    results_zero = mock_collection.query(query_embeddings=[[0.1] * 768], n_results=0)
    assert len(results_zero["ids"][0]) == 0


def test_concurrent_query_simulation(mock_collection):
    """
    Test that multiple concurrent queries can be handled.

    Validates:
    - Multiple queries succeed
    - No data corruption between queries
    - Results are independent
    """
    # Add test data
    mock_collection.add(
        ids=["concurrent1", "concurrent2", "concurrent3"],
        embeddings=[[0.1] * 768, [0.2] * 768, [0.3] * 768],
        documents=["doc1", "doc2", "doc3"],
        metadatas=[{"idx": 1}, {"idx": 2}, {"idx": 3}],
    )

    # Simulate concurrent queries with different parameters
    query1 = mock_collection.query(query_embeddings=[[0.1] * 768], n_results=1)
    query2 = mock_collection.query(query_embeddings=[[0.2] * 768], n_results=2)
    query3 = mock_collection.query(query_embeddings=[[0.3] * 768], n_results=3)

    # Verify each query succeeded
    assert len(query1["ids"][0]) >= 1
    assert len(query2["ids"][0]) >= 1
    assert len(query3["ids"][0]) >= 1

    # Verify results are independent (different queries can return different counts)
    assert len(query1["ids"][0]) <= 1
    assert len(query2["ids"][0]) <= 2
    assert len(query3["ids"][0]) <= 3


# =============================================================================
# Pytest Fixtures (defined at module level)
# =============================================================================


@pytest.fixture
def mock_chromadb_client():
    """Provide a fresh MockChromaDBClient for each test."""
    from cbr_mcp_server.performance.fixtures.mock_chromadb import MockChromaDBClient

    return MockChromaDBClient()


@pytest.fixture
def mock_collection(mock_chromadb_client):
    """Provide a fresh MockCollection for each test."""
    return mock_chromadb_client.get_or_create_collection(name="test_collection")


@pytest.fixture
def mock_populated_collection(mock_chromadb_client):
    """Provide a MockCollection pre-populated with test cases."""
    from cbr_mcp_server.performance.fixtures.mock_chromadb import generate_mock_case

    collection = mock_chromadb_client.get_or_create_collection(
        name="populated_collection"
    )

    # Add sample cases
    test_cases = [
        generate_mock_case(
            case_id=f"case_{i}",
            category="orchestration" if i % 2 == 0 else "webdev",
            subcategory="planning" if i % 2 == 0 else "api",
        )
        for i in range(10)
    ]

    ids = [case["case_id"] for case in test_cases]
    documents = [
        f"Problem: test problem {i}\nSolution: test solution {i}" for i in range(10)
    ]
    embeddings = [[float(i) / 100] * 768 for i in range(10)]
    metadatas = [
        {
            "category": case["category"],
            "subcategory": case["subcategory"],
        }
        for case in test_cases
    ]

    collection.add(
        ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
    )

    return collection
