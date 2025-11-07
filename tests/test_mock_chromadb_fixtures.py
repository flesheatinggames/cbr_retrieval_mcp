"""
Tests for mock ChromaDB fixtures module.

This test suite verifies the mock ChromaDB utilities used for
consistent, repeatable performance testing.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

import pytest

# Import the module we're testing (it doesn't exist yet - this is TDD!)
from tests.benchmarks.fixtures.mock_chromadb import (
    MockChromaDBClient,
    MockCollection,
    configure_latency,
    generate_mock_case,
    generate_mock_embedding,
    mock_chromadb_client,
    mock_collection_with_cases,
    mock_fast_db,
    mock_slow_db,
)

# ============================================================================
# MockChromaDBClient Tests
# ============================================================================


def test_mock_chromadb_client_initialization():
    """Verify MockChromaDBClient can be instantiated with default settings."""
    client = MockChromaDBClient()

    assert client is not None
    assert hasattr(client, "get_collection")
    assert hasattr(client, "get_or_create_collection")
    assert hasattr(client, "query_latency_ms")
    assert hasattr(client, "connection_latency_ms")
    assert client.query_latency_ms == 0
    assert client.connection_latency_ms == 0


def test_mock_chromadb_client_latency_simulation():
    """Verify query latency can be configured and simulated."""
    client = MockChromaDBClient(query_latency_ms=50, connection_latency_ms=10)

    assert client.query_latency_ms == 50
    assert client.connection_latency_ms == 10

    # Create a collection and verify latency is applied
    collection = client.get_or_create_collection("test_collection")

    start_time = time.time()
    collection.query(query_embeddings=[[0.1] * 768], n_results=10)
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

    # Verify query took at least the configured latency (with some tolerance)
    assert elapsed_time >= 45  # Allow 5ms tolerance


def test_mock_chromadb_client_memory_tracking():
    """Verify memory usage tracking for cache simulation."""
    client = MockChromaDBClient()

    assert hasattr(client, "memory_usage_bytes")
    assert client.memory_usage_bytes >= 0

    # Add a collection and verify memory tracking updates
    collection = client.get_or_create_collection("test_collection")
    collection.add(
        ids=["case1"],
        documents=["test code"],
        metadatas=[{"category": "test"}],
        embeddings=[[0.1] * 768],
    )

    assert client.memory_usage_bytes > 0


# ============================================================================
# MockCollection Tests
# ============================================================================


def test_mock_collection_initialization():
    """Verify MockCollection can be created with name and cases."""
    collection = MockCollection(name="test_collection")

    assert collection.name == "test_collection"
    assert hasattr(collection, "query")
    assert hasattr(collection, "get")
    assert hasattr(collection, "add")
    assert hasattr(collection, "count")


def test_mock_collection_query_basic():
    """Verify basic query functionality returns expected results."""
    collection = MockCollection(name="test_collection")

    # Add test cases
    collection.add(
        ids=["case1", "case2"],
        documents=["code example 1", "code example 2"],
        metadatas=[{"category": "web"}, {"category": "api"}],
        embeddings=[[0.1] * 768, [0.2] * 768],
    )

    # Query the collection
    results = collection.query(query_embeddings=[[0.15] * 768], n_results=2)

    assert "ids" in results
    assert "documents" in results
    assert "metadatas" in results
    assert "distances" in results
    assert len(results["ids"][0]) <= 2
    assert all(isinstance(d, float) for d in results["distances"][0])


def test_mock_collection_query_with_metadata_filter():
    """Verify metadata filtering (category, subcategory, tags)."""
    collection = MockCollection(name="test_collection")

    # Add test cases with different metadata
    collection.add(
        ids=["case1", "case2", "case3"],
        documents=["web code", "api code", "database code"],
        metadatas=[
            {"category": "web", "subcategory": "frontend", "tags": ["react"]},
            {"category": "api", "subcategory": "rest", "tags": ["fastapi"]},
            {"category": "database", "subcategory": "sql", "tags": ["postgres"]},
        ],
        embeddings=[[0.1] * 768, [0.2] * 768, [0.3] * 768],
    )

    # Query with category filter
    results = collection.query(
        query_embeddings=[[0.15] * 768],
        n_results=10,
        where={"category": "web"},
    )

    assert len(results["ids"][0]) == 1
    assert results["ids"][0][0] == "case1"
    assert results["metadatas"][0][0]["category"] == "web"

    # Query with subcategory filter
    results = collection.query(
        query_embeddings=[[0.15] * 768],
        n_results=10,
        where={"subcategory": "rest"},
    )

    assert len(results["ids"][0]) == 1
    assert results["ids"][0][0] == "case2"


def test_mock_collection_query_with_similarity_threshold():
    """Verify similarity threshold filtering."""
    collection = MockCollection(name="test_collection")

    # Add test cases with known distances
    collection.add(
        ids=["case1", "case2", "case3"],
        documents=["similar code", "somewhat similar", "very different"],
        metadatas=[{"score": 0.9}, {"score": 0.7}, {"score": 0.3}],
        embeddings=[[0.1] * 768, [0.3] * 768, [0.9] * 768],
    )

    # Query with similarity threshold
    # Note: ChromaDB uses distance (lower is better), not similarity
    # Distance of 0.5 corresponds to moderate similarity
    results = collection.query(
        query_embeddings=[[0.1] * 768],
        n_results=10,
    )

    # Verify distances are calculated
    assert all(isinstance(d, float) for d in results["distances"][0])
    assert all(0.0 <= d <= 2.0 for d in results["distances"][0])

    # Verify results are sorted by distance (closest first)
    distances = results["distances"][0]
    assert distances == sorted(distances)


def test_mock_collection_get_by_ids():
    """Verify get method retrieves specific cases by ID."""
    collection = MockCollection(name="test_collection")

    # Add test cases
    collection.add(
        ids=["case1", "case2", "case3"],
        documents=["code1", "code2", "code3"],
        metadatas=[{"cat": "a"}, {"cat": "b"}, {"cat": "c"}],
        embeddings=[[0.1] * 768, [0.2] * 768, [0.3] * 768],
    )

    # Get specific cases
    results = collection.get(ids=["case1", "case3"])

    assert len(results["ids"]) == 2
    assert "case1" in results["ids"]
    assert "case3" in results["ids"]
    assert len(results["documents"]) == 2
    assert len(results["metadatas"]) == 2


def test_mock_collection_add_cases():
    """Verify add method stores cases correctly."""
    collection = MockCollection(name="test_collection")

    # Initially empty
    assert collection.count() == 0

    # Add cases
    collection.add(
        ids=["case1", "case2"],
        documents=["doc1", "doc2"],
        metadatas=[{"m": 1}, {"m": 2}],
        embeddings=[[0.1] * 768, [0.2] * 768],
    )

    assert collection.count() == 2

    # Verify retrievable
    results = collection.get(ids=["case1"])
    assert len(results["ids"]) == 1
    assert results["ids"][0] == "case1"


# ============================================================================
# Pytest Fixture Tests
# ============================================================================


def test_mock_chromadb_client_fixture(mock_chromadb_client):
    """Verify mock_chromadb_client fixture provides configured client."""
    assert isinstance(mock_chromadb_client, MockChromaDBClient)
    assert hasattr(mock_chromadb_client, "get_collection")
    assert hasattr(mock_chromadb_client, "query_latency_ms")


def test_mock_collection_with_cases_fixture():
    """Verify fixture creates collection with N cases."""
    # This fixture is parametrized, so we test it with a specific value
    collection = mock_collection_with_cases(num_cases=10)

    assert isinstance(collection, MockCollection)
    assert collection.count() == 10

    # Verify all cases have complete metadata
    results = collection.get(ids=[f"case_{i}" for i in range(10)])
    assert len(results["ids"]) == 10
    for metadata in results["metadatas"]:
        assert "category" in metadata
        assert "subcategory" in metadata
        assert "tags" in metadata


def test_mock_fast_db_fixture(mock_fast_db):
    """Verify fast DB configuration (< 10ms latency)."""
    assert isinstance(mock_fast_db, MockChromaDBClient)
    assert mock_fast_db.query_latency_ms < 10
    assert mock_fast_db.connection_latency_ms < 10


def test_mock_slow_db_fixture(mock_slow_db):
    """Verify slow DB configuration (> 100ms latency)."""
    assert isinstance(mock_slow_db, MockChromaDBClient)
    assert mock_slow_db.query_latency_ms >= 100
    assert mock_slow_db.connection_latency_ms >= 10


# ============================================================================
# Helper Utility Tests
# ============================================================================


def test_generate_mock_case():
    """Verify consistent test case generation."""
    case = generate_mock_case(
        case_id="test_case_1",
        category="web",
        subcategory="frontend",
    )

    assert isinstance(case, dict)
    assert case["case_id"] == "test_case_1"
    assert case["category"] == "web"
    assert case["subcategory"] == "frontend"
    assert "code" in case
    assert "metadata" in case
    assert isinstance(case["code"], str)
    assert len(case["code"]) > 0


def test_generate_mock_embedding():
    """Verify consistent embedding generation."""
    text = "test code example"

    # Generate embedding
    embedding = generate_mock_embedding(text, dimension=768)

    assert isinstance(embedding, list)
    assert len(embedding) == 768
    assert all(isinstance(x, float) for x in embedding)
    assert all(-1.0 <= x <= 1.0 for x in embedding)

    # Verify deterministic (same input -> same output)
    embedding2 = generate_mock_embedding(text, dimension=768)
    assert embedding == embedding2

    # Verify different inputs give different embeddings
    embedding3 = generate_mock_embedding("different text", dimension=768)
    assert embedding != embedding3


def test_configure_latency():
    """Verify latency configuration utility."""
    client = MockChromaDBClient()

    # Configure latency
    configure_latency(client, query_ms=100, connection_ms=20)

    assert client.query_latency_ms == 100
    assert client.connection_latency_ms == 20


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.asyncio
async def test_mock_chromadb_async_operations():
    """Verify async operation support."""
    collection = MockCollection(name="async_test")

    # Add cases
    collection.add(
        ids=["case1"],
        documents=["async code"],
        metadatas=[{"category": "async"}],
        embeddings=[[0.1] * 768],
    )

    # Simulate async query
    async def async_query():
        await asyncio.sleep(0.01)  # Simulate async work
        return collection.query(query_embeddings=[[0.1] * 768], n_results=1)

    results = await async_query()

    assert "ids" in results
    assert len(results["ids"][0]) == 1


def test_mock_chromadb_deterministic_results():
    """Verify deterministic, repeatable results."""
    collection = MockCollection(name="deterministic_test")

    # Add cases
    collection.add(
        ids=["case1", "case2", "case3"],
        documents=["code1", "code2", "code3"],
        metadatas=[{"id": 1}, {"id": 2}, {"id": 3}],
        embeddings=[[0.1] * 768, [0.2] * 768, [0.3] * 768],
    )

    # Query multiple times with same input
    query_embedding = [[0.15] * 768]

    results1 = collection.query(query_embeddings=query_embedding, n_results=2)
    results2 = collection.query(query_embeddings=query_embedding, n_results=2)
    results3 = collection.query(query_embeddings=query_embedding, n_results=2)

    # Verify identical results
    assert results1["ids"] == results2["ids"] == results3["ids"]
    assert results1["distances"] == results2["distances"] == results3["distances"]
    assert results1["documents"] == results2["documents"] == results3["documents"]


# ============================================================================
# Edge Case Tests
# ============================================================================


def test_mock_collection_empty_query():
    """Verify behavior when querying empty collection."""
    collection = MockCollection(name="empty_test")

    results = collection.query(query_embeddings=[[0.1] * 768], n_results=10)

    assert results["ids"][0] == []
    assert results["documents"][0] == []
    assert results["metadatas"][0] == []
    assert results["distances"][0] == []


def test_mock_collection_get_nonexistent_ids():
    """Verify behavior when getting IDs that don't exist."""
    collection = MockCollection(name="test_collection")

    collection.add(
        ids=["case1"],
        documents=["code1"],
        metadatas=[{"m": 1}],
        embeddings=[[0.1] * 768],
    )

    # Get non-existent ID
    results = collection.get(ids=["nonexistent"])

    # Should return empty results, not error
    assert results["ids"] == []
    assert results["documents"] == []
    assert results["metadatas"] == []


def test_generate_mock_embedding_different_dimensions():
    """Verify embedding generation with different dimensions."""
    text = "test"

    # Test various dimensions
    for dim in [128, 384, 768, 1024]:
        embedding = generate_mock_embedding(text, dimension=dim)
        assert len(embedding) == dim


def test_mock_chromadb_client_multiple_collections():
    """Verify client can manage multiple collections."""
    client = MockChromaDBClient()

    col1 = client.get_or_create_collection("collection1")
    col2 = client.get_or_create_collection("collection2")

    assert col1.name == "collection1"
    assert col2.name == "collection2"
    assert col1 is not col2

    # Getting existing collection returns same instance
    col1_again = client.get_or_create_collection("collection1")
    assert col1 is col1_again
