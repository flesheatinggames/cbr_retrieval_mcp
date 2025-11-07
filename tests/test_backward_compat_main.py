"""
Backward Compatibility Tests for Metadata Storage Bug Fix.

This test suite verifies that the metadata storage fix (storing complete metadata
including category, subcategory, tags, problem) maintains backward compatibility
with existing functionality. These tests ensure that core retrieval operations,
MCP tools, and data access patterns continue to work unchanged after the fix.

Related Spec: @.agent-os/specs/2025-11-04-metadata-storage-bug-fix/spec.md
Task: Task 11 - Backward Compatibility Testing

Test Coverage:
1. Semantic search by problem text still works
2. Problem field still accessible in metadata
3. Solution retrieval unchanged (stored in documents, not metadata)
4. cbr_retrieve MCP tool still works correctly
5. cbr_find_similar MCP tool still works correctly
"""

from unittest.mock import AsyncMock, Mock, patch

# Standard Python imports
import chromadb
import pytest

import cbr_mcp_server as cbr_mcp_server_module
from cbr_mcp_server import CBRMCPServer, ProductionCBRRetriever

# ============================================================================
# Mock Context for MCP Testing
# ============================================================================


class MockContext:
    """Mock Context for MCP tool testing without requiring MCP request context."""

    def __init__(self):
        self.debug = AsyncMock()
        self.info = AsyncMock()
        self.warning = AsyncMock()
        self.error = AsyncMock()


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def real_database_client():
    """
    Fixture providing access to the real ChromaDB database.

    This is an integration test fixture that connects to the actual database
    to verify backward compatibility with existing data.
    """
    client = chromadb.PersistentClient(path="./db")
    collection = client.get_collection(name="code_solutions_case_base")
    return client, collection


@pytest.fixture
def real_sentence_transformer(monkeypatch):
    """Bypass conftest mock to use real SentenceTransformer for integration tests."""
    # Remove the conftest mock by un-setting the patch
    # Import the real class directly
    import importlib

    import sentence_transformers

    # Reload the module to get the real class
    importlib.reload(sentence_transformers)

    # Store the real class
    real_st = sentence_transformers.SentenceTransformer

    # Yield the real class for test use
    yield real_st


@pytest.fixture
def mock_server_config():
    """Fixture providing a mock server configuration for MCP tool testing."""
    mock_config = Mock()
    mock_config.validate_production.return_value = None
    mock_config.require_auth = False
    mock_config.rate_limit_enabled = False
    mock_config.use_real_db = True  # Use real database for integration tests
    mock_config.cache_enabled = False
    mock_config.database_path = "./db"
    mock_config.collection_name = "code_solutions_case_base"
    mock_config.embedding_model = "nomic-ai/nomic-embed-text-v1.5"
    mock_config.max_results_default = 10
    mock_config.similarity_threshold_default = 0.7
    mock_config.enable_health_checks = True
    mock_config.log_level = "INFO"
    mock_config.db_path = "./db"
    mock_config.api_keys = []
    mock_config.admin_keys = []
    mock_config.rate_limit_requests = 100
    mock_config.rate_limit_window = 3600
    mock_config.input_validation = "permissive"
    mock_config.max_query_length = 10000
    mock_config.sanitization = True
    mock_config.health_check_interval = 60
    mock_config.circuit_breaker_failure_threshold = 5
    mock_config.circuit_breaker_timeout = 60
    mock_config.cache_ttl = 300
    mock_config.cache_max_size = 100
    mock_config.retry_enabled = False

    return mock_config


# ============================================================================
# Test 1: Existing Semantic Search Still Works
# ============================================================================


def test_existing_semantic_search_still_works(
    real_database_client, real_sentence_transformer
):
    """
    Verify that semantic search by problem text still works unchanged.

    This test ensures that the core CBR retrieval functionality continues
    to work after the metadata fix. Semantic similarity search should return
    relevant cases based on the query text, with proper similarity scores.

    Test Steps:
    1. Initialize ChromaDB client with existing database
    2. Perform semantic query with known problem domain
    3. Verify results are returned
    4. Verify results contain expected fields (id, metadata with problem, documents)
    5. Verify similarity scores are reasonable
    6. Verify at least one relevant result is returned
    """
    client, collection = real_database_client

    # Test the core retrieval functionality directly (same as retrieve_relevant_cases)
    query = "How to implement user authentication with Firebase"

    # Load embedding model and perform semantic search
    embedding_model = real_sentence_transformer(
        "nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True
    )
    query_embedding = embedding_model.encode(query, normalize_embeddings=True)

    # This core functionality should still work exactly as before
    # Convert to list if it's a numpy array
    if hasattr(query_embedding, "tolist"):
        query_embedding_list = query_embedding.tolist()
    else:
        query_embedding_list = query_embedding

    results = collection.query(query_embeddings=[query_embedding_list], n_results=5)

    # Assertion 1: Results are returned (not None or empty)
    assert results is not None, "Query should return results, not None"
    assert "documents" in results, "Results should contain 'documents' field"
    assert "metadatas" in results, "Results should contain 'metadatas' field"
    assert "distances" in results, "Results should contain 'distances' field"

    # Assertion 2: Results contain expected structure
    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []

    assert len(documents) > 0, "Should return at least one document (solution)"
    assert len(metadatas) > 0, "Should return at least one metadata object"
    assert len(distances) > 0, "Should return at least one distance score"

    # Assertion 3: All result arrays have same length (data integrity)
    assert (
        len(documents) == len(metadatas) == len(distances)
    ), "Documents, metadatas, and distances should have matching lengths"

    # Assertion 4: Similarity scores are reasonable (distances should be low for relevant results)
    # ChromaDB returns L2 distances, lower is better (0.0 = perfect match)
    for i, distance in enumerate(distances):
        assert distance >= 0.0, f"Distance {i} should be non-negative, got {distance}"
        assert distance < 2.0, (
            f"Distance {i} seems too high for relevant result: {distance}. "
            "This may indicate semantic search is not working properly."
        )

    # Assertion 5: At least one highly relevant result (distance < 1.0)
    relevant_results = [d for d in distances if d < 1.0]
    assert len(relevant_results) > 0, (
        "Should have at least one highly relevant result (distance < 1.0). "
        f"Got distances: {distances}"
    )


# ============================================================================
# Test 2: Problem Field Still Accessible
# ============================================================================


def test_problem_field_still_accessible(real_database_client):
    """
    Ensure backward compatibility - the 'problem' field still exists in metadata.

    This test verifies that code expecting to access metadata["problem"] will
    continue to work after the metadata fix. This is critical for backward
    compatibility with existing integrations.

    Test Steps:
    1. Initialize ChromaDB client with existing database
    2. Retrieve multiple cases from collection
    3. Verify each case's metadata contains 'problem' key
    4. Verify problem field contains non-empty string
    5. Verify problem field is accessible via metadata["problem"]
    6. Test at least 5 different cases for consistency
    """
    client, collection = real_database_client

    # Get a sample of cases from the database (first 10)
    results = collection.get(limit=10, include=["metadatas", "documents"])

    # Assertion 1: Database query returns results
    assert results is not None, "Database query should return results"
    assert "metadatas" in results, "Results should contain 'metadatas' field"
    assert (
        len(results["metadatas"]) > 0
    ), "Should retrieve at least one case from database"

    metadatas = results["metadatas"]

    # Assertion 2: At least 5 cases retrieved for thorough testing
    assert len(metadatas) >= 5, (
        f"Expected at least 5 cases for testing, got {len(metadatas)}. "
        "Database may not be properly populated."
    )

    # Assertion 3: Every case has 'problem' field in metadata
    for i, metadata in enumerate(metadatas):
        assert "problem" in metadata, (
            f"Case {i} is missing 'problem' field in metadata. "
            f"Available fields: {list(metadata.keys())}. "
            "This breaks backward compatibility!"
        )

    # Assertion 4: Every 'problem' field contains non-empty string
    for i, metadata in enumerate(metadatas):
        problem = metadata["problem"]
        assert isinstance(
            problem, str
        ), f"Case {i} 'problem' field should be string, got {type(problem)}"
        assert len(problem) > 0, f"Case {i} 'problem' field should not be empty"
        assert (
            len(problem) > 10
        ), f"Case {i} 'problem' field seems too short ({len(problem)} chars): '{problem}'"

    # Assertion 5: Problem field is directly accessible (backward compatibility test)
    # This simulates existing code that does metadata["problem"]
    try:
        for i, metadata in enumerate(metadatas[:5]):
            problem_text = metadata["problem"]  # Direct access should work
            assert problem_text is not None, f"Case {i} problem should not be None"
    except KeyError as e:
        pytest.fail(
            f"Direct access to metadata['problem'] failed: {e}. Backward compatibility broken!"
        )


# ============================================================================
# Test 3: Solution Retrieval Unchanged
# ============================================================================


def test_solution_retrieval_unchanged(real_database_client, real_sentence_transformer):
    """
    Verify solutions are still stored in document field, not in metadata.

    This test ensures that the storage schema hasn't changed in a breaking way.
    Solutions should remain in the 'documents' field (ChromaDB's primary content
    field), NOT in the metadata. This is critical for proper vector embedding.

    Test Steps:
    1. Initialize ChromaDB client with existing database
    2. Query collection for cases
    3. Verify solutions are in the 'documents' field
    4. Verify solutions are NOT in the metadata field
    5. Verify solution text is non-empty
    6. Verify solution field contains expected code/text content
    """
    client, collection = real_database_client

    # Query for orchestration cases to test solution retrieval
    query_text = "How to plan a multi-step agent workflow"

    # Use direct ChromaDB query to test storage structure
    embedding_model = real_sentence_transformer(
        "nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True
    )
    query_embedding = embedding_model.encode(query_text, normalize_embeddings=True)

    # Convert to list if it's a numpy array
    if hasattr(query_embedding, "tolist"):
        query_embedding_list = query_embedding.tolist()
    else:
        query_embedding_list = query_embedding

    results = collection.query(
        query_embeddings=[query_embedding_list],
        n_results=5,
        include=["documents", "metadatas"],
    )

    # Assertion 1: Query returns results with both documents and metadatas
    assert results is not None, "Query should return results"
    assert "documents" in results, "Results should contain 'documents' field"
    assert "metadatas" in results, "Results should contain 'metadatas' field"

    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []

    assert len(documents) > 0, "Should return at least one document"
    assert len(metadatas) > 0, "Should return at least one metadata object"

    # Assertion 2: Solutions are in the 'documents' field (primary content)
    for i, document in enumerate(documents):
        assert isinstance(
            document, str
        ), f"Document {i} should be a string, got {type(document)}"
        assert len(document) > 0, f"Document {i} should not be empty"
        assert (
            len(document) > 20
        ), f"Document {i} seems too short to be a solution ({len(document)} chars)"

    # Assertion 3: Solutions are NOT in metadata (correct storage schema)
    for i, metadata in enumerate(metadatas):
        assert "solution" not in metadata, (
            f"Metadata {i} should NOT contain 'solution' field. "
            f"Solutions belong in documents field, not metadata. "
            f"Found metadata keys: {list(metadata.keys())}"
        )

    # Assertion 4: Documents contain expected code/text content patterns
    # Solutions typically contain code keywords, formatting, or structured text
    code_patterns = [
        "def ",
        "class ",
        "function",
        "const ",
        "let ",
        "var ",
        "import",
        "return",
        "//",
        "/*",
        "```",
    ]

    at_least_one_code = False
    for document in documents:
        doc_lower = document.lower()
        if any(pattern.lower() in doc_lower for pattern in code_patterns):
            at_least_one_code = True
            break

    assert at_least_one_code, (
        "Expected at least one document to contain code-like content. "
        "Documents may not be properly formatted solutions."
    )

    # Assertion 5: Documents are distinct from problem text in metadata
    for i, (document, metadata) in enumerate(zip(documents, metadatas)):
        problem = metadata.get("problem", "")

        # Solution should be significantly different from problem statement
        assert document != problem, (
            f"Document {i} should not be identical to problem text. "
            "Solutions should be stored in documents, problems in metadata."
        )


# ============================================================================
# Test 4: cbr_retrieve MCP Tool Still Works
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_retrieve_tool_still_works(mock_server_config):
    """
    Verify the MCP cbr_retrieve tool continues to function correctly.

    This test ensures that the primary MCP tool interface for retrieving
    relevant cases continues to work after the metadata fix. The tool should
    accept queries and return properly structured results.

    Test Steps:
    1. Create MCP server with real database
    2. Call cbr_retrieve tool with test query
    3. Verify tool accepts query parameter without errors
    4. Verify returns structured results with cases
    5. Verify each case contains required fields
    6. Verify results are semantically relevant
    7. Verify tool response format matches expected MCP output
    """
    with (patch.object(cbr_mcp_server_module, "StructuredLogger"),):
        # Create server with real database for integration test
        server = CBRMCPServer(config=mock_server_config)

        # Mock context
        mock_ctx = MockContext()

        # Test query relevant to the case base
        test_query = "How to implement Firebase authentication in a React application"

        # Call cbr_retrieve tool
        result = await server.cbr_retrieve(
            query=test_query, max_results=5, similarity_threshold=0.7, ctx=mock_ctx
        )

        # Assertion 1: Tool call succeeds (no exception raised)
        assert result is not None, "cbr_retrieve tool should return a result, not None"

        # Assertion 2: Returns structured results dictionary
        assert isinstance(result, dict), "Result should be a dictionary (JSON response)"
        assert "examples" in result, (
            "Result should have 'examples' field. " f"Got keys: {list(result.keys())}"
        )

        # Assertion 3: Examples field contains list of cases
        examples = result["examples"]
        assert isinstance(examples, list), "Examples should be a list"
        assert len(examples) > 0, (
            "Should return at least one example case for the query. "
            "cbr_retrieve tool may not be working properly."
        )

        # Assertion 4: Each case contains required fields
        required_fields = ["id", "similarity_score", "content", "metadata"]

        for i, case in enumerate(examples):
            for field in required_fields:
                assert field in case, (
                    f"Case {i} is missing required field '{field}'. "
                    f"Available fields: {list(case.keys())}. "
                    "MCP tool response format may have changed."
                )

        # Assertion 5: Each case has valid data in required fields
        for i, case in enumerate(examples):
            assert isinstance(case["id"], str), f"Case {i} id should be string"
            assert len(case["id"]) > 0, f"Case {i} id should not be empty"

            assert isinstance(
                case["metadata"], dict
            ), f"Case {i} metadata should be dict"
            assert (
                "problem" in case["metadata"]
            ), f"Case {i} metadata should have problem field"
            assert isinstance(
                case["metadata"]["problem"], str
            ), f"Case {i} metadata problem should be string"
            assert (
                len(case["metadata"]["problem"]) > 0
            ), f"Case {i} metadata problem should not be empty"

            assert isinstance(
                case["content"], str
            ), f"Case {i} content should be string"
            assert len(case["content"]) > 0, f"Case {i} content should not be empty"

            assert (
                "category" in case["metadata"]
            ), f"Case {i} metadata should have category field"
            assert isinstance(
                case["metadata"]["category"], str
            ), f"Case {i} metadata category should be string"

            assert isinstance(
                case["similarity_score"], (int, float)
            ), f"Case {i} similarity_score should be numeric"
            assert (
                0.0 <= case["similarity_score"] <= 1.0
            ), f"Case {i} similarity_score should be between 0 and 1, got {case['similarity_score']}"

        # Assertion 6: Results are semantically relevant (similarity scores reasonable)
        # At least one case should have high similarity (> 0.7)
        high_similarity_cases = [c for c in examples if c["similarity_score"] > 0.7]
        assert len(high_similarity_cases) > 0, (
            "Should have at least one case with similarity > 0.7. "
            f"Got scores: {[c['similarity_score'] for c in examples]}. "
            "Semantic relevance may be degraded."
        )

        # Assertion 7: Tool response format is consistent (backward compatibility)
        # The first case should follow expected structure
        first_case = examples[0]
        assert "id" in first_case, "First case should have id"
        assert "metadata" in first_case, "First case should have metadata"
        assert (
            "problem" in first_case["metadata"]
        ), "First case metadata should have problem"
        assert "content" in first_case, "First case should have content"


# ============================================================================
# Test 5: cbr_find_similar MCP Tool Still Works
# ============================================================================


@pytest.mark.asyncio
async def test_cbr_find_similar_tool_still_works(
    mock_server_config, real_database_client
):
    """
    Verify the MCP cbr_find_similar tool continues to function correctly.

    This test ensures that the similar case discovery tool works after the
    metadata fix. The tool should accept a case_id and return similar cases
    based on vector similarity.

    Test Steps:
    1. Get a known case_id from the database
    2. Create MCP server with real database
    3. Call cbr_find_similar tool with the case_id
    4. Verify tool accepts case_id parameter without errors
    5. Verify returns similar cases
    6. Verify each case contains required fields
    7. Verify similar cases exclude the original case_id
    8. Verify tool response format matches expected MCP output
    """
    client, collection = real_database_client

    # Step 1: Get a known case_id from the database
    sample_cases = collection.get(limit=1, include=["metadatas"])
    assert len(sample_cases["ids"]) > 0, "Database should have at least one case"

    test_case_id = sample_cases["ids"][0]

    with (patch.object(cbr_mcp_server_module, "StructuredLogger"),):
        # Create server with real database
        server = CBRMCPServer(config=mock_server_config)

        # Mock context
        mock_ctx = MockContext()

        # Call cbr_find_similar tool with known case_id
        result = await server.cbr_find_similar(
            example_id=test_case_id,
            similarity_threshold=0.8,
            max_results=8,
            ctx=mock_ctx,
        )

        # Assertion 1: Tool call succeeds (no exception raised)
        assert (
            result is not None
        ), "cbr_find_similar tool should return a result, not None"

        # Assertion 2: Returns structured results dictionary
        assert isinstance(result, dict), "Result should be a dictionary (JSON response)"
        assert "reference_id" in result, (
            "Result should have 'reference_id' field. "
            f"Got keys: {list(result.keys())}"
        )
        assert "similar_cases" in result, (
            "Result should have 'similar_cases' field. "
            f"Got keys: {list(result.keys())}"
        )

        # Assertion 3: Reference ID matches input
        assert result["reference_id"] == test_case_id, (
            f"Reference ID should match input case_id. "
            f"Expected: {test_case_id}, Got: {result['reference_id']}"
        )

        # Assertion 4: Similar cases field contains list
        similar_cases = result["similar_cases"]
        assert isinstance(similar_cases, list), "Similar cases should be a list"

        # Note: It's possible no similar cases meet the threshold, which is valid behavior
        if len(similar_cases) > 0:
            # Assertion 5: Each similar case contains required fields
            required_fields = ["id", "similarity", "content", "category"]

            for i, case in enumerate(similar_cases):
                for field in required_fields:
                    assert field in case, (
                        f"Similar case {i} is missing required field '{field}'. "
                        f"Available fields: {list(case.keys())}. "
                        "MCP tool response format may have changed."
                    )

            # Assertion 6: Each case has valid data
            for i, case in enumerate(similar_cases):
                assert isinstance(case["id"], str), f"Case {i} id should be string"
                assert isinstance(
                    case["similarity"], (int, float)
                ), f"Case {i} similarity should be numeric"
                assert (
                    0.0 <= case["similarity"] <= 1.0
                ), f"Case {i} similarity should be between 0 and 1"

            # Assertion 7: Similar cases exclude the original case_id
            similar_case_ids = [c["id"] for c in similar_cases]
            assert test_case_id not in similar_case_ids, (
                "Similar cases should not include the reference case itself. "
                f"Reference: {test_case_id}, Similar: {similar_case_ids}"
            )

            # Assertion 8: Similarity scores are reasonable (meeting threshold)
            for i, case in enumerate(similar_cases):
                assert case["similarity"] >= 0.8, (
                    f"Case {i} should meet similarity threshold of 0.8, "
                    f"got {case['similarity']}"
                )
        else:
            # If no similar cases found, that's a valid result (case may be unique)
            # Just verify the structure is correct
            assert (
                similar_cases == []
            ), "Similar cases should be empty list if none found"
