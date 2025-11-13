"""
Mock ChromaDB client and collection for performance benchmarking.

This module provides lightweight mock implementations of ChromaDB's client
and collection interfaces for use in performance testing and benchmarking.
"""

import hashlib
import time
from typing import Any, Dict, List, Optional, Union


class MockCollection:
    """
    Mock ChromaDB collection that stores documents in-memory.

    Provides a simplified interface compatible with ChromaDB's Collection API
    for testing purposes without requiring an actual database connection.
    """

    def __init__(self, name: str, client: "MockChromaDBClient"):
        """
        Initialize a mock collection.

        Args:
            name: Collection name
            client: Parent MockChromaDBClient instance
        """
        self.name = name
        self.client = client
        self._documents: Dict[str, Dict[str, Any]] = {}

    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """
        Add documents to the collection.

        Args:
            ids: List of document IDs
            embeddings: List of embedding vectors
            documents: List of document texts
            metadatas: List of metadata dictionaries
        """
        for i, doc_id in enumerate(ids):
            self._documents[doc_id] = {
                "id": doc_id,
                "embedding": embeddings[i],
                "document": documents[i],
                "metadata": metadatas[i],
            }

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, List[List[Any]]]:
        """
        Query the collection for similar documents.

        Args:
            query_embeddings: Query embedding vectors
            n_results: Maximum number of results to return
            where: Optional metadata filter

        Returns:
            Dict with keys: ids, distances, metadatas, documents
        """
        # Simulate query latency
        time.sleep(self.client.query_latency_ms / 1000.0)

        # Filter documents by where clause if provided
        filtered_docs = []
        for doc_id, doc_data in self._documents.items():
            if where is None:
                filtered_docs.append((doc_id, doc_data))
            else:
                # Simple filter matching - check if all where conditions match
                match = all(
                    doc_data["metadata"].get(key) == value
                    for key, value in where.items()
                )
                if match:
                    filtered_docs.append((doc_id, doc_data))

        # Calculate distances (simple L2 distance)
        results_with_distances = []
        query_emb = query_embeddings[0]

        for doc_id, doc_data in filtered_docs:
            doc_emb = doc_data["embedding"]
            # Simple distance calculation
            distance = sum(
                (q - d) ** 2 for q, d in zip(query_emb, doc_emb)
            ) ** 0.5
            results_with_distances.append((distance, doc_id, doc_data))

        # Sort by distance and limit results
        results_with_distances.sort(key=lambda x: x[0])
        results_with_distances = results_with_distances[:n_results]

        # Format results to match ChromaDB output format
        ids = [[doc_id for _, doc_id, _ in results_with_distances]]
        distances = [[dist for dist, _, _ in results_with_distances]]
        metadatas = [
            [doc_data["metadata"] for _, _, doc_data in results_with_distances]
        ]
        documents = [
            [doc_data["document"] for _, _, doc_data in results_with_distances]
        ]

        return {
            "ids": ids,
            "distances": distances,
            "metadatas": metadatas,
            "documents": documents,
        }

    def get(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, List[Any]]:
        """
        Get documents by IDs or filter.

        Args:
            ids: Optional list of document IDs to retrieve
            where: Optional metadata filter

        Returns:
            Dict with keys: ids, embeddings, documents, metadatas
        """
        if ids is not None:
            # Get specific documents by ID
            selected_docs = []
            for doc_id in ids:
                if doc_id in self._documents:
                    selected_docs.append(self._documents[doc_id])
        elif where is not None:
            # Filter by metadata
            selected_docs = []
            for doc_data in self._documents.values():
                match = all(
                    doc_data["metadata"].get(key) == value
                    for key, value in where.items()
                )
                if match:
                    selected_docs.append(doc_data)
        else:
            # Return all documents
            selected_docs = list(self._documents.values())

        return {
            "ids": [doc["id"] for doc in selected_docs],
            "embeddings": [doc["embedding"] for doc in selected_docs],
            "documents": [doc["document"] for doc in selected_docs],
            "metadatas": [doc["metadata"] for doc in selected_docs],
        }

    def update(
        self,
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None,
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Update existing documents.

        Args:
            ids: List of document IDs to update
            embeddings: Optional new embeddings
            documents: Optional new document texts
            metadatas: Optional new metadata
        """
        for i, doc_id in enumerate(ids):
            if doc_id in self._documents:
                if embeddings is not None:
                    self._documents[doc_id]["embedding"] = embeddings[i]
                if documents is not None:
                    self._documents[doc_id]["document"] = documents[i]
                if metadatas is not None:
                    self._documents[doc_id]["metadata"] = metadatas[i]

    def delete(self, ids: List[str]) -> None:
        """
        Delete documents by IDs.

        Args:
            ids: List of document IDs to delete
        """
        for doc_id in ids:
            if doc_id in self._documents:
                del self._documents[doc_id]


class MockChromaDBClient:
    """
    Mock ChromaDB client for testing without actual database.

    Provides configurable latencies to simulate real database behavior
    in performance benchmarks.
    """

    def __init__(
        self,
        query_latency_ms: float = 10.0,
        connection_latency_ms: float = 5.0,
    ):
        """
        Initialize mock ChromaDB client.

        Args:
            query_latency_ms: Simulated query latency in milliseconds
            connection_latency_ms: Simulated connection latency in milliseconds
        """
        self.query_latency_ms = query_latency_ms
        self.connection_latency_ms = connection_latency_ms
        self._collections: Dict[str, MockCollection] = {}

    def get_or_create_collection(
        self, name: str, **kwargs: Any
    ) -> MockCollection:
        """
        Get or create a collection by name.

        Args:
            name: Collection name
            **kwargs: Additional collection parameters (ignored in mock)

        Returns:
            MockCollection instance
        """
        if name not in self._collections:
            self._collections[name] = MockCollection(name, self)
        return self._collections[name]

    def reset(self) -> None:
        """Clear all collections from the client."""
        self._collections.clear()


# =============================================================================
# Helper Functions for Test Data Generation
# =============================================================================


def generate_mock_case(
    case_id: str,
    category: str,
    subcategory: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Generate a mock case dictionary for testing.

    Args:
        case_id: Unique case identifier
        category: Case category
        subcategory: Case subcategory
        **kwargs: Additional fields to include in case

    Returns:
        Case dictionary with required fields and any additional kwargs
    """
    case = {
        "case_id": case_id,
        "category": category,
        "subcategory": subcategory,
    }
    case.update(kwargs)
    return case


def generate_mock_embedding(
    text: str,
    dimension: int = 768,
) -> List[float]:
    """
    Generate a deterministic mock embedding vector for given text.

    Uses hashing to create consistent embeddings for the same input text.

    Args:
        text: Input text to generate embedding for
        dimension: Embedding vector dimension

    Returns:
        List of floats representing the embedding
    """
    # Use hash to generate deterministic values
    hash_value = int(hashlib.sha256(text.encode()).hexdigest(), 16)

    # Generate embedding values based on hash
    embedding = []
    for i in range(dimension):
        # Use different hash offsets for each dimension
        seed = hash_value + i
        # Normalize to [-1, 1] range
        value = ((seed % 10000) / 10000.0) * 2 - 1
        embedding.append(value)

    return embedding


def generate_mock_query_result(
    n_results: int = 5,
    include_distances: bool = True,
) -> Dict[str, List[List[Any]]]:
    """
    Generate a mock query result matching ChromaDB format.

    Args:
        n_results: Number of results to generate
        include_distances: Whether to include distance values

    Returns:
        Dict with keys: ids, documents, metadatas, distances (if include_distances)
    """
    result = {
        "ids": [[f"case_{i}" for i in range(n_results)]],
        "documents": [[f"Document {i}" for i in range(n_results)]],
        "metadatas": [
            [
                {"category": "test", "subcategory": f"sub{i}"}
                for i in range(n_results)
            ]
        ],
    }

    if include_distances:
        # Generate mock distances (sorted from closest to furthest)
        result["distances"] = [[i * 0.1 for i in range(n_results)]]

    return result
