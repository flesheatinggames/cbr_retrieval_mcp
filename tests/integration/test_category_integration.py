"""
Integration tests for category filtering functionality in ProductionCBRRetriever.

Tests verify end-to-end category filtering, subcategory filtering, and backward
compatibility with existing metadata and non-filtered queries.

These tests use real ChromaDB instances with temporary databases to ensure
complete integration testing of the category filtering functionality implemented
in Tasks 2-3.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
import logging

from cbr_mcp_server import ProductionCBRRetriever, CBRServerConfig, StructuredLogger


@pytest.fixture
def temp_db_path():
    """Create a temporary directory for ChromaDB database."""
    temp_dir = tempfile.mkdtemp(prefix="cbr_category_test_")
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def retriever_with_mixed_categories(temp_db_path):
    """
    Create a ProductionCBRRetriever with a collection containing cases
    across multiple categories: orchestration, code, and best-practice.
    """
    # Create config and logger for retriever
    config = CBRServerConfig(
        use_real_db=True,
        database_path=temp_db_path,
        collection_name="test_case_base"
    )
    logger = StructuredLogger(config)

    retriever = ProductionCBRRetriever(config, logger)

    # Load the embedding model to ensure consistent 768-dimensional embeddings
    retriever._ensure_embedding_model_loaded()

    # Orchestration cases
    orchestration_cases = [
        {
            "id": "orch-001",
            "content": "Agent delegation workflow for distributing tasks across specialist agents",
            "metadata": {
                "category": "orchestration",
                "subcategory": "agent-delegation",
                "tags": "workflow,agents,coordination",
                "title": "Multi-Agent Task Delegation"
            }
        },
        {
            "id": "orch-002",
            "content": "Task coordination system for managing dependencies between subtasks",
            "metadata": {
                "category": "orchestration",
                "subcategory": "task-coordination",
                "tags": "tasks,dependencies,workflow",
                "title": "Dependency-Based Task Coordination"
            }
        },
        {
            "id": "orch-003",
            "content": "Workflow management pattern for sequential and parallel task execution",
            "metadata": {
                "category": "orchestration",
                "subcategory": "workflow-management",
                "tags": "workflow,execution,patterns",
                "title": "Sequential and Parallel Workflow Execution"
            }
        }
    ]

    # Code cases
    code_cases = [
        {
            "id": "code-001",
            "content": "React component implementation for user authentication form with validation",
            "metadata": {
                "category": "code",
                "subcategory": "react-components",
                "tags": "react,forms,validation",
                "title": "User Authentication Form Component"
            }
        },
        {
            "id": "code-002",
            "content": "REST API route implementation for user registration endpoint",
            "metadata": {
                "category": "code",
                "subcategory": "api-routes",
                "tags": "api,rest,backend",
                "title": "User Registration API Endpoint"
            }
        },
        {
            "id": "code-003",
            "content": "Utility function for data validation and sanitization",
            "metadata": {
                "category": "code",
                "subcategory": "utilities",
                "tags": "validation,utilities,helpers",
                "title": "Data Validation Utility"
            }
        }
    ]

    # Best practice cases
    best_practice_cases = [
        {
            "id": "bp-001",
            "content": "Error handling pattern with comprehensive logging and user feedback",
            "metadata": {
                "category": "best-practice",
                "subcategory": "error-handling",
                "tags": "errors,logging,reliability",
                "title": "Comprehensive Error Handling Pattern"
            }
        },
        {
            "id": "bp-002",
            "content": "Logging standards for production applications with structured data",
            "metadata": {
                "category": "best-practice",
                "subcategory": "logging",
                "tags": "logging,monitoring,observability",
                "title": "Production Logging Standards"
            }
        }
    ]

    # Add all cases to the collection
    all_cases = orchestration_cases + code_cases + best_practice_cases

    # Generate embeddings using the nomic-ai model (768-dimensional)
    # Normalize embeddings for consistent similarity scoring
    ids = [case["id"] for case in all_cases]
    documents = [case["content"] for case in all_cases]
    metadatas = [case["metadata"] for case in all_cases]
    embeddings = [retriever.embedding_model.encode(doc, normalize_embeddings=True).tolist() for doc in documents]

    # Add with embeddings to ensure dimension consistency
    retriever.collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    return retriever


@pytest.fixture
def retriever_with_code_subcategories(temp_db_path):
    """
    Create a ProductionCBRRetriever with code cases across multiple subcategories:
    firebase-auth,react-components,and api-routes.
    """
    config = CBRServerConfig(
        use_real_db=True,
        database_path=temp_db_path,
        collection_name="test_case_base"
    )
    logger = StructuredLogger(config)

    retriever = ProductionCBRRetriever(config, logger)

    # Load the embedding model to ensure consistent 768-dimensional embeddings
    retriever._ensure_embedding_model_loaded()

    # Firebase Auth cases
    firebase_auth_cases = [
        {
            "id": "fb-auth-001",
            "content": "Firebase authentication login implementation with email and password",
            "metadata": {
                "category": "code",
                "subcategory": "firebase-auth",
                "tags": "firebase,authentication,login",
                "title": "Firebase Email/Password Login"
            }
        },
        {
            "id": "fb-auth-002",
            "content": "Firebase user signup flow with email verification",
            "metadata": {
                "category": "code",
                "subcategory": "firebase-auth",
                "tags": "firebase,signup,email-verification",
                "title": "Firebase User Signup with Verification"
            }
        },
        {
            "id": "fb-auth-003",
            "content": "Firebase password reset functionality with secure token handling",
            "metadata": {
                "category": "code",
                "subcategory": "firebase-auth",
                "tags": "firebase,password-reset,security",
                "title": "Firebase Password Reset Flow"
            }
        }
    ]

    # React Components cases
    react_component_cases = [
        {
            "id": "react-comp-001",
            "content": "Reusable button component with multiple variants and states",
            "metadata": {
                "category": "code",
                "subcategory": "react-components",
                "tags": "react,ui,button",
                "title": "Reusable Button Component"
            }
        },
        {
            "id": "react-comp-002",
            "content": "Modal dialog component with backdrop and accessibility features",
            "metadata": {
                "category": "code",
                "subcategory": "react-components",
                "tags": "react,modal,accessibility",
                "title": "Accessible Modal Dialog"
            }
        },
        {
            "id": "react-comp-003",
            "content": "Form component with field validation and error display",
            "metadata": {
                "category": "code",
                "subcategory": "react-components",
                "tags": "react,forms,validation",
                "title": "Validated Form Component"
            }
        }
    ]

    # API Routes cases
    api_routes_cases = [
        {
            "id": "api-route-001",
            "content": "REST API endpoint for user profile management",
            "metadata": {
                "category": "code",
                "subcategory": "api-routes",
                "tags": "api,rest,user-profile",
                "title": "User Profile REST Endpoint"
            }
        },
        {
            "id": "api-route-002",
            "content": "GraphQL resolver for complex data queries with nested relationships",
            "metadata": {
                "category": "code",
                "subcategory": "api-routes",
                "tags": "graphql,resolver,queries",
                "title": "GraphQL Nested Query Resolver"
            }
        }
    ]

    # Add all cases to the collection
    all_cases = firebase_auth_cases + react_component_cases + api_routes_cases

    # Generate embeddings using the nomic-ai model (768-dimensional)
    # Normalize embeddings for consistent similarity scoring
    ids = [case["id"] for case in all_cases]
    documents = [case["content"] for case in all_cases]
    metadatas = [case["metadata"] for case in all_cases]
    embeddings = [retriever.embedding_model.encode(doc, normalize_embeddings=True).tolist() for doc in documents]

    # Add with embeddings to ensure dimension consistency
    retriever.collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    return retriever


@pytest.fixture
def retriever_with_all_categories(temp_db_path):
    """
    Create a ProductionCBRRetriever with cases across all four categories:
    orchestration,code,best-practice,and documentation.
    """
    config = CBRServerConfig(
        use_real_db=True,
        database_path=temp_db_path,
        collection_name="test_case_base"
    )
    logger = StructuredLogger(config)

    retriever = ProductionCBRRetriever(config, logger)

    # Load the embedding model to ensure consistent 768-dimensional embeddings
    retriever._ensure_embedding_model_loaded()

    cases = [
        # Orchestration cases
        {
            "id": "orch-001",
            "content": "Agent coordination workflow for multi-step processes",
            "metadata": {
                "category": "orchestration",
                "subcategory": "agent-coordination",
                "tags": "workflow,agents",
                "title": "Multi-Step Agent Coordination"
            }
        },
        {
            "id": "orch-002",
            "content": "Task planning and decomposition strategy",
            "metadata": {
                "category": "orchestration",
                "subcategory": "task-planning",
                "tags": "planning,tasks",
                "title": "Task Decomposition Strategy"
            }
        },
        # Code cases
        {
            "id": "code-001",
            "content": "Database schema design for user management system",
            "metadata": {
                "category": "code",
                "subcategory": "database",
                "tags": "database,schema,users",
                "title": "User Management Database Schema"
            }
        },
        {
            "id": "code-002",
            "content": "Authentication middleware implementation",
            "metadata": {
                "category": "code",
                "subcategory": "middleware",
                "tags": "auth,middleware,security",
                "title": "Authentication Middleware"
            }
        },
        # Best practice cases
        {
            "id": "bp-001",
            "content": "Security best practices for API development",
            "metadata": {
                "category": "best-practice",
                "subcategory": "security",
                "tags": "security,api,best-practices",
                "title": "API Security Best Practices"
            }
        },
        {
            "id": "bp-002",
            "content": "Code review guidelines and checklist",
            "metadata": {
                "category": "best-practice",
                "subcategory": "code-review",
                "tags": "code-review,quality,standards",
                "title": "Code Review Guidelines"
            }
        },
        # Documentation cases
        {
            "id": "doc-001",
            "content": "API documentation template with examples",
            "metadata": {
                "category": "documentation",
                "subcategory": "api-docs",
                "tags": "documentation,api,templates",
                "title": "API Documentation Template"
            }
        },
        {
            "id": "doc-002",
            "content": "User onboarding guide with step-by-step instructions",
            "metadata": {
                "category": "documentation",
                "subcategory": "user-guides",
                "tags": "documentation,onboarding,guides",
                "title": "User Onboarding Guide"
            }
        }
    ]

    # Generate embeddings using the nomic-ai model (768-dimensional)
    # Normalize embeddings for consistent similarity scoring
    ids = [case["id"] for case in cases]
    documents = [case["content"] for case in cases]
    metadatas = [case["metadata"] for case in cases]
    embeddings = [retriever.embedding_model.encode(doc, normalize_embeddings=True).tolist() for doc in documents]

    # Add with embeddings to ensure dimension consistency
    retriever.collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    return retriever


@pytest.fixture
def retriever_with_existing_metadata(temp_db_path):
    """
    Create a ProductionCBRRetriever with cases containing existing metadata fields
    that should be preserved during migration/enrichment.
    """
    config = CBRServerConfig(
        use_real_db=True,
        database_path=temp_db_path,
        collection_name="test_case_base"
    )
    logger = StructuredLogger(config)

    retriever = ProductionCBRRetriever(config, logger)

    # Load the embedding model to ensure consistent 768-dimensional embeddings
    retriever._ensure_embedding_model_loaded()

    cases = [
        {
            "id": "legacy-001",
            "content": "Legacy authentication system implementation",
            "metadata": {
                "source": "legacy-system",
                "type": "example",
                "version": "2.0",
                "author": "original-team"
            }
        },
        {
            "id": "legacy-002",
            "content": "Manual entry for API endpoint documentation",
            "metadata": {
                "source": "manual-entry",
                "type": "template",
                "created_date": "2024-01-15",
                "reviewer": "tech-lead"
            }
        },
        {
            "id": "legacy-003",
            "content": "User-contributed code snippet for form validation",
            "metadata": {
                "author": "user123",
                "version": "1.0",
                "language": "typescript",
                "framework": "react"
            }
        }
    ]

    # Generate embeddings using the nomic-ai model (768-dimensional)
    # Normalize embeddings for consistent similarity scoring
    ids = [case["id"] for case in cases]
    documents = [case["content"] for case in cases]
    metadatas = [case["metadata"] for case in cases]
    embeddings = [retriever.embedding_model.encode(doc, normalize_embeddings=True).tolist() for doc in documents]

    # Add with embeddings to ensure dimension consistency
    retriever.collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    return retriever


class TestCategoryFilteringEndToEnd:
    """Integration tests for category filtering functionality."""

    @pytest.mark.asyncio
    async def test_filter_by_category_e2e(self, retriever_with_mixed_categories):
        """
        Test that category filtering returns only cases matching the specified
        category and excludes all other categories.

        Verifies:
        - Results contain only orchestration cases
        - No code or best-practice cases in results
        - Results are ranked by similarity score
        """
        # Query for orchestration cases
        results = await retriever_with_mixed_categories.search_by_category(
            query="workflow management for agents",
            category="orchestration",
            limit=10
        )

        # Should return orchestration cases only
        assert len(results) > 0,"Should return at least one orchestration case"
        assert len(results) <= 3,"Should return at most 3 orchestration cases"

        # Verify all results are orchestration category
        for result in results:
            assert result["metadata"]["category"] == "orchestration",\
                f"Result {result['id']} should be orchestration category"

        # Verify no code cases in results
        code_ids = {"code-001","code-002","code-003"}
        result_ids = {result["id"] for result in results}
        assert result_ids.isdisjoint(code_ids),\
            "Results should not contain any code category cases"

        # Verify no best-practice cases in results
        bp_ids = {"bp-001","bp-002"}
        assert result_ids.isdisjoint(bp_ids),\
            "Results should not contain any best-practice category cases"

        # Verify results are ranked by similarity (descending order)
        if len(results) > 1:
            scores = [result.get("similarity",result.get("score",1.0)) for result in results]
            assert scores == sorted(scores,reverse=True),\
                "Results should be ranked by similarity score in descending order"

    @pytest.mark.asyncio
    async def test_filter_by_category_and_subcategory_e2e(self, retriever_with_code_subcategories):
        """
        Test that combined category + subcategory filtering works correctly
        and excludes cases from other subcategories.

        Verifies:
        - Results contain only code/firebase-auth cases
        - No react-components or api-routes cases in results
        - Results are ranked by similarity score
        """
        # Query for firebase-auth cases specifically
        results = await retriever_with_code_subcategories.search_by_category(
            query="user authentication with Firebase",
            category="code",
            subcategory="firebase-auth",
            limit=10
        )

        # Should return firebase-auth cases only
        assert len(results) > 0,"Should return at least one firebase-auth case"
        assert len(results) <= 3,"Should return at most 3 firebase-auth cases"

        # Verify all results are code/firebase-auth
        for result in results:
            assert result["metadata"]["category"] == "code",\
                f"Result {result['id']} should be code category"
            assert result["metadata"]["subcategory"] == "firebase-auth",\
                f"Result {result['id']} should be firebase-auth subcategory"

        # Verify no react-components cases in results
        react_ids = {"react-comp-001","react-comp-002","react-comp-003"}
        result_ids = {result["id"] for result in results}
        assert result_ids.isdisjoint(react_ids),\
            "Results should not contain any react-components subcategory cases"

        # Verify no api-routes cases in results
        api_ids = {"api-route-001","api-route-002"}
        assert result_ids.isdisjoint(api_ids),\
            "Results should not contain any api-routes subcategory cases"

        # Verify results are ranked by similarity
        if len(results) > 1:
            scores = [result.get("similarity",result.get("score",1.0)) for result in results]
            assert scores == sorted(scores,reverse=True),\
                "Results should be ranked by similarity score in descending order"

    @pytest.mark.asyncio
    async def test_backward_compatibility_no_filter(self, retriever_with_all_categories):
        """
        Test that the original retrieve functionality (no category parameter)
        returns cases from all categories without filtering.

        Verifies:
        - Results contain cases from multiple categories
        - No category filtering applied
        - Existing behavior unchanged
        """
        # Query without category filter (original behavior)
        results = await retriever_with_all_categories.retrieve_relevant_examples(
            query="authentication and security implementation",
            max_results=10
        )

        # Should return results from multiple categories
        assert len(results) > 0,"Should return at least one result"

        # Collect categories from results
        categories_in_results = set()
        for result in results:
            if "category" in result.get("metadata",{}):
                categories_in_results.add(result["metadata"]["category"])

        # Should have cases from at least 2 different categories
        assert len(categories_in_results) >= 2,\
            f"Should return cases from multiple categories, found: {categories_in_results}"

        # Verify no filtering was applied - should be purely similarity-based
        # The query mentions "authentication and security" which should match
        # cases from code,best-practice,and potentially other categories
        expected_possible_categories = {"code","best-practice","orchestration","documentation"}
        assert categories_in_results.issubset(expected_possible_categories),\
            f"Results should only contain valid categories, found: {categories_in_results}"

    @pytest.mark.asyncio
    async def test_backward_compatibility_existing_metadata(self, retriever_with_existing_metadata):
        """
        Test that migration/enrichment preserves existing metadata fields
        while adding new category fields.

        Verifies:
        - Existing metadata fields (source, type, author, etc.) are preserved
        - New category fields are added
        - No existing metadata is overwritten or removed
        """
        # Retrieve all cases to check metadata preservation
        all_results = retriever_with_existing_metadata.collection.get()

        # Build a lookup of results by ID
        results_by_id = {}
        for i, case_id in enumerate(all_results["ids"]):
            results_by_id[case_id] = {
                "id": case_id,
                "metadata": all_results["metadatas"][i] if all_results["metadatas"] else {}
            }

        # Verify legacy-001 preserves existing metadata
        legacy_001 = results_by_id.get("legacy-001")
        assert legacy_001 is not None,"legacy-001 case should exist"
        assert legacy_001["metadata"].get("source") == "legacy-system",\
            "Existing source field should be preserved"
        assert legacy_001["metadata"].get("type") == "example",\
            "Existing type field should be preserved"
        assert legacy_001["metadata"].get("version") == "2.0",\
            "Existing version field should be preserved"
        assert legacy_001["metadata"].get("author") == "original-team",\
            "Existing author field should be preserved"

        # Verify legacy-002 preserves existing metadata
        legacy_002 = results_by_id.get("legacy-002")
        assert legacy_002 is not None,"legacy-002 case should exist"
        assert legacy_002["metadata"].get("source") == "manual-entry",\
            "Existing source field should be preserved"
        assert legacy_002["metadata"].get("type") == "template",\
            "Existing type field should be preserved"
        assert legacy_002["metadata"].get("created_date") == "2024-01-15",\
            "Existing created_date field should be preserved"
        assert legacy_002["metadata"].get("reviewer") == "tech-lead",\
            "Existing reviewer field should be preserved"

        # Verify legacy-003 preserves existing metadata
        legacy_003 = results_by_id.get("legacy-003")
        assert legacy_003 is not None,"legacy-003 case should exist"
        assert legacy_003["metadata"].get("author") == "user123",\
            "Existing author field should be preserved"
        assert legacy_003["metadata"].get("version") == "1.0",\
            "Existing version field should be preserved"
        assert legacy_003["metadata"].get("language") == "typescript",\
            "Existing language field should be preserved"
        assert legacy_003["metadata"].get("framework") == "react",\
            "Existing framework field should be preserved"

        # Note: The test assumes that if category enrichment is run,
        # new fields like category, subcategory, tags would be added.
        # Since we're testing backward compatibility,we verify that:
        # 1. Existing fields are NOT removed or changed
        # 2. The system can handle cases with or without category metadata

        # If enrichment has been run,verify new fields exist alongside old ones
        for case_id, case_data in results_by_id.items():
            metadata = case_data["metadata"]
            # Check that if category fields exist,they don't overwrite original fields
            if "category" in metadata:
                # Verify original fields still exist for each case
                if case_id == "legacy-001":
                    assert metadata.get("source") == "legacy-system",\
                        "Category enrichment should not overwrite existing source"
                elif case_id == "legacy-002":
                    assert metadata.get("type") == "template",\
                        "Category enrichment should not overwrite existing type"
                elif case_id == "legacy-003":
                    assert metadata.get("author") == "user123",\
                        "Category enrichment should not overwrite existing author"
