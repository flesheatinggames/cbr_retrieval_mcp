"""
Unit tests for ProductionCBRRetriever.search_by_category method.

This test module follows TDD approach - tests are written before implementation.
Tests should initially fail (red phase) until the actual implementation is created.

Test Coverage:
- Subtask 2.1: Category-only filtering
- Subtask 2.2: Category + subcategory filtering
- Subtask 2.3: Query text with filters
- Subtask 2.4: Error handling
"""

import asyncio
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Valid categories as defined in data_spec.md
VALID_CATEGORIES = ["code", "orchestration", "best-practice", "anti-pattern"]


class TestProductionCBRRetrieverSearchByCategory:
    """Test suite for ProductionCBRRetriever.search_by_category method."""

    @pytest.fixture
    def mock_retriever(self):
        """Create a mock ProductionCBRRetriever instance."""
        from cbr_mcp_server import CBRServerConfig, ProductionCBRRetriever

        config = CBRServerConfig(use_real_db=False)  # Don't initialize real DB
        mock_logger = Mock()
        retriever = ProductionCBRRetriever(config, mock_logger)

        # Mock the collection
        retriever.collection = Mock()
        retriever.embedding_model = Mock()

        return retriever

    @pytest.fixture
    def mock_collection_with_mixed_categories(self):
        """Create a mock collection with mixed category cases."""
        mock_collection = Mock()

        # Mock data with different categories
        code_cases = {
            "ids": ["code-1", "code-2"],
            "documents": ["Firebase auth setup", "React component pattern"],
            "metadatas": [
                {
                    "category": "code",
                    "subcategory": "firebase-auth",
                    "source": "example1.py",
                },
                {
                    "category": "code",
                    "subcategory": "react-components",
                    "source": "example2.py",
                },
            ],
            "distances": [[0.1], [0.2]],
        }

        orchestration_cases = {
            "ids": ["orch-1", "orch-2"],
            "documents": ["Remediation protocol", "Planning workflow"],
            "metadatas": [
                {
                    "category": "orchestration",
                    "subcategory": "remediation",
                    "source": "example3.py",
                },
                {
                    "category": "orchestration",
                    "subcategory": "planning",
                    "source": "example4.py",
                },
            ],
            "distances": [[0.15], [0.25]],
        }

        best_practice_cases = {
            "ids": ["bp-1"],
            "documents": ["Error handling pattern"],
            "metadatas": [
                {
                    "category": "best-practice",
                    "subcategory": "error-handling",
                    "source": "example5.py",
                }
            ],
            "distances": [[0.18]],
        }

        return {
            "code": code_cases,
            "orchestration": orchestration_cases,
            "best-practice": best_practice_cases,
            "all": {
                "ids": code_cases["ids"]
                + orchestration_cases["ids"]
                + best_practice_cases["ids"],
                "documents": code_cases["documents"]
                + orchestration_cases["documents"]
                + best_practice_cases["documents"],
                "metadatas": code_cases["metadatas"]
                + orchestration_cases["metadatas"]
                + best_practice_cases["metadatas"],
                "distances": [[0.1], [0.2], [0.15], [0.25], [0.18]],
            },
        }

    # ========================================================================
    # Test Group 1: Category-Only Filtering (Subtask 2.1)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_search_by_category_orchestration_only(
        self, mock_retriever, mock_collection_with_mixed_categories
    ):
        """Test filtering returns only orchestration cases when category='orchestration'."""
        # Setup: Mock collection to return only orchestration cases for where filter
        mock_retriever.collection.query.return_value = (
            mock_collection_with_mixed_categories["orchestration"]
        )
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        # Execute
        results = await mock_retriever.search_by_category(
            category="orchestration", query="workflow examples"
        )

        # Verify: collection.query called with correct where filter
        mock_retriever.collection.query.assert_called_once()
        call_kwargs = mock_retriever.collection.query.call_args[1]
        assert call_kwargs["where"] == {"category": "orchestration"}

        # Verify: Results contain only orchestration cases
        assert len(results) == 2
        for result in results:
            assert result["category"] == "orchestration"
            assert "orch" in result["id"]

    @pytest.mark.asyncio
    async def test_search_by_category_code_only(
        self, mock_retriever, mock_collection_with_mixed_categories
    ):
        """Test filtering by code category only."""
        mock_retriever.collection.query.return_value = (
            mock_collection_with_mixed_categories["code"]
        )
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        results = await mock_retriever.search_by_category(
            category="code", query="implementation"
        )

        # Verify where filter
        call_kwargs = mock_retriever.collection.query.call_args[1]
        assert call_kwargs["where"] == {"category": "code"}

        # Verify results
        assert len(results) == 2
        for result in results:
            assert result["category"] == "code"

    @pytest.mark.asyncio
    async def test_search_by_category_best_practice_only(
        self, mock_retriever, mock_collection_with_mixed_categories
    ):
        """Test filtering by best-practice category."""
        mock_retriever.collection.query.return_value = (
            mock_collection_with_mixed_categories["best-practice"]
        )
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        results = await mock_retriever.search_by_category(
            category="best-practice", query="patterns"
        )

        call_kwargs = mock_retriever.collection.query.call_args[1]
        assert call_kwargs["where"] == {"category": "best-practice"}

        assert len(results) == 1
        assert results[0]["category"] == "best-practice"

    @pytest.mark.asyncio
    async def test_search_by_category_anti_pattern_only(self, mock_retriever):
        """Test filtering by anti-pattern category."""
        anti_pattern_cases = {
            "ids": ["ap-1", "ap-2"],
            "documents": ["Premature completion", "Verification skip"],
            "metadatas": [
                {"category": "anti-pattern", "subcategory": "completion-bias"},
                {"category": "anti-pattern", "subcategory": "verification-skip"},
            ],
            "distances": [[0.12], [0.22]],
        }

        mock_retriever.collection.query.return_value = anti_pattern_cases
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        results = await mock_retriever.search_by_category(
            category="anti-pattern", query="issues"
        )

        call_kwargs = mock_retriever.collection.query.call_args[1]
        assert call_kwargs["where"] == {"category": "anti-pattern"}

        assert len(results) == 2
        for result in results:
            assert result["category"] == "anti-pattern"

    # ========================================================================
    # Test Group 2: Category + Subcategory Filtering (Subtask 2.2)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_search_by_category_and_subcategory_firebase_auth(
        self, mock_retriever
    ):
        """Test filtering by category='code' and subcategory='firebase-auth'."""
        firebase_auth_cases = {
            "ids": ["code-fb-1", "code-fb-2"],
            "documents": ["Firebase auth setup", "Firebase auth tokens"],
            "metadatas": [
                {
                    "category": "code",
                    "subcategory": "firebase-auth",
                    "tags": "firebase,authentication",
                },
                {
                    "category": "code",
                    "subcategory": "firebase-auth",
                    "tags": "firebase,tokens",
                },
            ],
            "distances": [[0.1], [0.15]],
        }

        mock_retriever.collection.query.return_value = firebase_auth_cases
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        results = await mock_retriever.search_by_category(
            category="code", subcategory="firebase-auth", query="authentication"
        )

        # Verify where filter includes both category and subcategory
        call_kwargs = mock_retriever.collection.query.call_args[1]
        assert call_kwargs["where"] == {
            "$and": [{"category": "code"}, {"subcategory": "firebase-auth"}]
        }

        # Verify results contain only code/firebase-auth cases
        assert len(results) == 2
        for result in results:
            assert result["category"] == "code"
            assert result["subcategory"] == "firebase-auth"

    @pytest.mark.asyncio
    async def test_search_by_category_and_subcategory_remediation(self, mock_retriever):
        """Test filtering by category='orchestration' and subcategory='remediation'."""
        remediation_cases = {
            "ids": ["orch-rem-1", "orch-rem-2"],
            "documents": ["Remediation protocol flow", "Fix incomplete verification"],
            "metadatas": [
                {"category": "orchestration", "subcategory": "remediation"},
                {"category": "orchestration", "subcategory": "remediation"},
            ],
            "distances": [[0.08], [0.12]],
        }

        mock_retriever.collection.query.return_value = remediation_cases
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        results = await mock_retriever.search_by_category(
            category="orchestration", subcategory="remediation", query="fix issues"
        )

        call_kwargs = mock_retriever.collection.query.call_args[1]
        assert call_kwargs["where"] == {
            "$and": [{"category": "orchestration"}, {"subcategory": "remediation"}]
        }

        assert len(results) == 2
        for result in results:
            assert result["category"] == "orchestration"
            assert result["subcategory"] == "remediation"

    @pytest.mark.asyncio
    async def test_search_by_category_and_subcategory_empty_results(
        self, mock_retriever
    ):
        """Test ValueError raised when invalid subcategory provided (secure behavior)."""
        # SECURITY FIX: Invalid subcategory now raises ValueError instead of returning empty results
        # This prevents configuration drift attacks (CWE-20)

        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        # Expect ValueError with helpful message about valid subcategories
        with pytest.raises(ValueError) as exc_info:
            await mock_retriever.search_by_category(
                category="code", subcategory="nonexistent-subcat", query="test"
            )

        # Verify error message includes subcategory name and guidance
        error_message = str(exc_info.value)
        assert "nonexistent-subcat" in error_message
        assert "code" in error_message

    # ========================================================================
    # Test Group 3: Query Text with Filters (Subtask 2.3)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_search_by_category_with_query_text_similarity_ranking(
        self, mock_retriever
    ):
        """Test query text filters by category AND ranks by similarity."""
        orchestration_cases_ranked = {
            "ids": ["orch-1", "orch-2", "orch-3"],
            "documents": [
                "Remediation workflow pattern",
                "Planning workflow",
                "Delegation workflow",
            ],
            "metadatas": [
                {"category": "orchestration", "subcategory": "remediation"},
                {"category": "orchestration", "subcategory": "planning"},
                {"category": "orchestration", "subcategory": "delegation"},
            ],
            "distances": [[0.05], [0.15], [0.25]],  # Sorted by similarity
        }

        mock_retriever.collection.query.return_value = orchestration_cases_ranked
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        results = await mock_retriever.search_by_category(
            category="orchestration", query="remediation workflow"
        )

        # Verify embedding was generated
        mock_retriever.embedding_model.encode.assert_called_once_with(
            "remediation workflow", normalize_embeddings=True
        )

        # Verify query called with embedding
        call_kwargs = mock_retriever.collection.query.call_args[1]
        assert "query_embeddings" in call_kwargs
        assert call_kwargs["where"] == {"category": "orchestration"}

        # Verify results are ranked by similarity
        assert len(results) == 3
        assert results[0]["id"] == "orch-1"  # Highest similarity (0.05 distance)

    @pytest.mark.asyncio
    async def test_search_by_category_no_query_text_uses_get(self, mock_retriever):
        """Test no query text uses collection.get() instead of query()."""
        code_cases = {
            "ids": ["code-1", "code-2"],
            "documents": ["React component", "Firebase auth"],
            "metadatas": [
                {"category": "code", "subcategory": "react-components"},
                {"category": "code", "subcategory": "firebase-auth"},
            ],
        }

        mock_retriever.collection.get.return_value = code_cases

        results = await mock_retriever.search_by_category(
            category="code", query=""  # Empty query
        )

        # Verify get() was called instead of query()
        mock_retriever.collection.get.assert_called_once()
        call_kwargs = mock_retriever.collection.get.call_args[1]
        assert call_kwargs["where"] == {"category": "code"}
        assert call_kwargs["limit"] == 10

        # Verify query() was NOT called
        mock_retriever.collection.query.assert_not_called()

        # Verify embedding model was NOT used
        mock_retriever.embedding_model.encode.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_by_category_query_text_embeds_query(self, mock_retriever):
        """Test query text triggers embedding model loading and encoding."""
        mock_retriever.collection.query.return_value = {
            "ids": ["test-1"],
            "documents": ["test doc"],
            "metadatas": [{"category": "code"}],
            "distances": [[0.1]],
        }
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        await mock_retriever.search_by_category(
            category="code", query="test query text"
        )

        # Verify _ensure_embedding_model_loaded would be called
        # (in actual implementation, verify this happens before encode)

        # Verify encode was called with query text
        mock_retriever.embedding_model.encode.assert_called_once_with(
            "test query text", normalize_embeddings=True
        )

    @pytest.mark.asyncio
    async def test_search_by_category_query_combines_filter_and_similarity(
        self, mock_retriever
    ):
        """Test query combines metadata filter with vector similarity."""
        # Setup: Collection with multiple categories, but query should filter and rank
        filtered_results = {
            "ids": ["code-1", "code-2"],
            "documents": ["Relevant code", "Less relevant code"],
            "metadatas": [
                {"category": "code", "subcategory": "general"},
                {"category": "code", "subcategory": "general"},
            ],
            "distances": [[0.1], [0.3]],
        }

        mock_retriever.collection.query.return_value = filtered_results
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        results = await mock_retriever.search_by_category(
            category="code", query="relevant example"
        )

        # Verify both where filter and query_embeddings used
        call_kwargs = mock_retriever.collection.query.call_args[1]
        assert "where" in call_kwargs
        assert "query_embeddings" in call_kwargs
        assert call_kwargs["where"]["category"] == "code"

        # Verify results filtered and ranked
        assert all(r["category"] == "code" for r in results)

    # ========================================================================
    # Test Group 4: Error Handling (Subtask 2.4)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_search_by_category_invalid_category_raises_value_error(
        self, mock_retriever
    ):
        """Test invalid category raises ValueError with helpful message."""
        with pytest.raises(ValueError) as exc_info:
            await mock_retriever.search_by_category(
                category="invalid-category", query="test"
            )

        # Verify error message is helpful
        error_message = str(exc_info.value)
        assert "invalid-category" in error_message.lower()
        assert any(cat in error_message for cat in VALID_CATEGORIES)

    @pytest.mark.asyncio
    async def test_search_by_category_chromadb_query_error_fallback(
        self, mock_retriever
    ):
        """Test ChromaDB query error fails fast (secure fail-secure behavior)."""
        # SECURITY FIX: ChromaDB errors now fail fast instead of falling back to unfiltered queries
        # This prevents information disclosure via error fallback (CWE-755)

        mock_retriever.collection.query.side_effect = Exception(
            "ChromaDB connection error"
        )
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        # Expect RuntimeError with sanitized error message
        with pytest.raises(RuntimeError) as exc_info:
            await mock_retriever.search_by_category(category="code", query="test")

        # Verify error message is sanitized and helpful
        error_message = str(exc_info.value)
        assert "Failed to query cases for category 'code'" in error_message
        assert "verify the category exists" in error_message.lower()

        # Verify error was logged (internal logging should capture full details)
        assert mock_retriever.logger.error.called
        error_call_args = mock_retriever.logger.error.call_args
        # Check that internal logging used descriptive message
        logged_message = error_call_args[0][0] if error_call_args[0] else ""
        assert (
            "category filter" in logged_message.lower()
            or "query failed" in logged_message.lower()
        )

    @pytest.mark.asyncio
    async def test_search_by_category_chromadb_get_error_fallback(self, mock_retriever):
        """Test ChromaDB get() error (no query text) triggers fallback."""
        # get() raises exception
        mock_retriever.collection.get.side_effect = Exception("Database read error")

        # Expect error to be logged and gracefully handled
        with pytest.raises(Exception):
            await mock_retriever.search_by_category(
                category="code", query=""  # No query text, uses get()
            )

        # Verify error was logged with filter details
        assert mock_retriever.logger.error.called

    @pytest.mark.asyncio
    async def test_search_by_category_embedding_model_load_failure(
        self, mock_retriever
    ):
        """Test embedding model load failure is handled gracefully."""
        # Mock embedding to raise exception
        mock_retriever.embedding_model.encode.side_effect = Exception(
            "Model load failed"
        )

        # Should handle gracefully, possibly falling back to get() without similarity
        with pytest.raises(Exception):
            await mock_retriever.search_by_category(category="code", query="test query")

        # Verify error was logged
        assert (
            mock_retriever.logger.error.called or mock_retriever.logger.warning.called
        )

    @pytest.mark.asyncio
    async def test_search_by_category_empty_results_no_matches(self, mock_retriever):
        """Test empty results when no cases match the filter."""
        mock_retriever.collection.get.return_value = {
            "ids": [],
            "documents": [],
            "metadatas": [],
        }

        results = await mock_retriever.search_by_category(
            category="orchestration", query=""
        )

        # Verify empty list returned with no errors
        assert results == []
        assert isinstance(results, list)

    # ========================================================================
    # Test Group 5: Result Formatting
    # ========================================================================

    @pytest.mark.asyncio
    async def test_search_by_category_result_includes_category_field(
        self, mock_retriever
    ):
        """Test results include category field in formatted output."""
        mock_retriever.collection.query.return_value = {
            "ids": ["code-1"],
            "documents": ["Test doc"],
            "metadatas": [{"category": "code", "subcategory": "firebase-auth"}],
            "distances": [[0.1]],
        }
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        results = await mock_retriever.search_by_category(category="code", query="test")

        # Verify category field is included
        assert len(results) > 0
        for result in results:
            assert "category" in result
            assert result["category"] == "code"

    @pytest.mark.asyncio
    async def test_search_by_category_result_includes_subcategory_field(
        self, mock_retriever
    ):
        """Test results include subcategory field from metadata."""
        mock_retriever.collection.query.return_value = {
            "ids": ["code-1"],
            "documents": ["Test doc"],
            "metadatas": [
                {"category": "code", "subcategory": "firebase-auth", "tags": "firebase"}
            ],
            "distances": [[0.1]],
        }
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        results = await mock_retriever.search_by_category(
            category="code", subcategory="firebase-auth", query="test"
        )

        # Verify subcategory field is included
        assert len(results) > 0
        for result in results:
            assert "subcategory" in result
            assert result["subcategory"] == "firebase-auth"

    @pytest.mark.asyncio
    async def test_search_by_category_preserves_existing_metadata(self, mock_retriever):
        """Test existing metadata fields are preserved in results."""
        mock_retriever.collection.get.return_value = {
            "ids": ["code-1"],
            "documents": ["Test doc"],
            "metadatas": [
                {
                    "category": "code",
                    "subcategory": "general",
                    "source": "example.py",
                    "author": "test-author",
                    "tags": "python,api",
                }
            ],
        }

        results = await mock_retriever.search_by_category(category="code", query="")

        # Verify original metadata preserved
        assert len(results) > 0
        result = results[0]
        assert result["metadata"]["source"] == "example.py"
        assert result["metadata"]["author"] == "test-author"
        assert result["metadata"]["tags"] == "python,api"

    # ========================================================================
    # Test Group 6: Limit Parameter
    # ========================================================================

    @pytest.mark.asyncio
    async def test_search_by_category_respects_limit_parameter(self, mock_retriever):
        """Test limit parameter controls number of results."""
        # Create 20 mock cases
        mock_cases = {
            "ids": [f"code-{i}" for i in range(20)],
            "documents": [f"Document {i}" for i in range(20)],
            "metadatas": [
                {"category": "code", "subcategory": "general"} for _ in range(20)
            ],
            "distances": [[0.1 + i * 0.01] for i in range(20)],
        }

        mock_retriever.collection.query.return_value = mock_cases
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        results = await mock_retriever.search_by_category(
            category="code", query="test", limit=5
        )

        # Verify n_results parameter passed to query
        call_kwargs = mock_retriever.collection.query.call_args[1]
        assert call_kwargs["n_results"] == 5

    @pytest.mark.asyncio
    async def test_search_by_category_limit_default_value(self, mock_retriever):
        """Test default limit is 10."""
        mock_retriever.collection.query.return_value = {
            "ids": [f"code-{i}" for i in range(15)],
            "documents": [f"Doc {i}" for i in range(15)],
            "metadatas": [{"category": "code"} for _ in range(15)],
            "distances": [[0.1] for _ in range(15)],
        }
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        results = await mock_retriever.search_by_category(
            category="code",
            query="test",
            # limit not specified, should default to 10
        )

        # Verify default limit of 10 used
        call_kwargs = mock_retriever.collection.query.call_args[1]
        assert call_kwargs["n_results"] == 10

    # ========================================================================
    # Additional Edge Cases
    # ========================================================================

    @pytest.mark.asyncio
    async def test_search_by_category_none_subcategory_explicit(self, mock_retriever):
        """Test None subcategory is handled correctly."""
        mock_retriever.collection.query.return_value = {
            "ids": ["code-1"],
            "documents": ["Test"],
            "metadatas": [{"category": "code", "subcategory": "general"}],
            "distances": [[0.1]],
        }
        mock_retriever.embedding_model.encode.return_value = Mock(
            tolist=lambda: [0.1] * 384
        )

        results = await mock_retriever.search_by_category(
            category="code", subcategory=None, query="test"
        )

        # Verify where filter only includes category
        call_kwargs = mock_retriever.collection.query.call_args[1]
        assert call_kwargs["where"] == {"category": "code"}
        assert "subcategory" not in call_kwargs["where"]

    @pytest.mark.asyncio
    async def test_search_by_category_empty_string_subcategory(self, mock_retriever):
        """Test empty string subcategory is treated as None."""
        mock_retriever.collection.get.return_value = {
            "ids": ["code-1"],
            "documents": ["Test"],
            "metadatas": [{"category": "code"}],
        }

        results = await mock_retriever.search_by_category(
            category="code", subcategory="", query=""
        )

        # Verify where filter only includes category
        call_kwargs = mock_retriever.collection.get.call_args[1]
        assert call_kwargs["where"] == {"category": "code"}


class TestProductionCBRRetrieverGetCategories:
    """Test suite for ProductionCBRRetriever.get_categories method.

    Covers Task 3 (subtasks 3.1-3.3): Testing hierarchical category structure
    with subcategory counts.
    """

    @pytest.fixture
    def mock_retriever(self):
        """Create a mock ProductionCBRRetriever instance."""
        from cbr_mcp_server import CBRServerConfig, ProductionCBRRetriever

        config = CBRServerConfig(use_real_db=False)
        mock_logger = Mock()
        retriever = ProductionCBRRetriever(config, mock_logger)

        # Mock the collection
        retriever.collection = Mock()
        retriever.embedding_model = Mock()

        return retriever

    # ========================================================================
    # Test Group 1: Hierarchical Structure Tests (Subtask 3.1)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_categories_returns_four_top_level_categories(
        self, mock_retriever
    ):
        """Test that get_categories returns exactly 4 top-level categories."""
        # Setup: Mock ChromaDB to return empty results for all categories
        mock_retriever.collection.get.return_value = {"ids": [], "metadatas": []}

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: Returns list with 4 categories
        assert isinstance(categories, list)
        assert len(categories) == 4

        # Verify: Category names are correct
        category_names = [cat["name"] for cat in categories]
        assert set(category_names) == {
            "code",
            "orchestration",
            "best-practice",
            "anti-pattern",
        }

    @pytest.mark.asyncio
    async def test_get_categories_includes_required_fields(self, mock_retriever):
        """Test that each category has all required fields: name, description, count, subcategories."""

        # Setup: Mock ChromaDB to return sample data
        def mock_get_side_effect(**kwargs):
            category = kwargs.get("where", {}).get("category", "")
            if category == "code":
                return {
                    "ids": ["code-1", "code-2"],
                    "metadatas": [
                        {"category": "code", "subcategory": "firebase-auth"},
                        {"category": "code", "subcategory": "react-components"},
                    ],
                }
            return {"ids": [], "metadatas": []}

        mock_retriever.collection.get.side_effect = mock_get_side_effect

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: Each category has required fields
        required_fields = {"name", "description", "count", "subcategories"}
        for category in categories:
            assert (
                set(category.keys()) >= required_fields
            ), f"Category {category.get('name')} missing required fields"
            assert isinstance(category["name"], str)
            assert isinstance(category["description"], str)
            assert isinstance(category["count"], int)
            assert isinstance(category["subcategories"], list)

    @pytest.mark.asyncio
    async def test_get_categories_subcategories_have_required_fields(
        self, mock_retriever
    ):
        """Test that each subcategory has required fields: name, count."""

        # Setup: Mock ChromaDB to return cases with subcategories
        def mock_get_side_effect(**kwargs):
            category = kwargs.get("where", {}).get("category", "")
            if category == "code":
                return {
                    "ids": ["code-1", "code-2", "code-3"],
                    "metadatas": [
                        {"category": "code", "subcategory": "firebase-auth"},
                        {"category": "code", "subcategory": "firebase-auth"},
                        {"category": "code", "subcategory": "react-components"},
                    ],
                }
            return {"ids": [], "metadatas": []}

        mock_retriever.collection.get.side_effect = mock_get_side_effect

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: Subcategories have required fields
        code_category = next(cat for cat in categories if cat["name"] == "code")
        assert len(code_category["subcategories"]) > 0

        for subcategory in code_category["subcategories"]:
            assert "name" in subcategory
            assert "count" in subcategory
            assert isinstance(subcategory["name"], str)
            assert isinstance(subcategory["count"], int)

    @pytest.mark.asyncio
    async def test_get_categories_subcategories_are_lists(self, mock_retriever):
        """Test that subcategories field is always a list (empty or populated)."""

        # Setup: Mock ChromaDB with mixed results
        def mock_get_side_effect(**kwargs):
            category = kwargs.get("where", {}).get("category", "")
            if category == "code":
                return {
                    "ids": ["code-1"],
                    "metadatas": [{"category": "code", "subcategory": "firebase-auth"}],
                }
            # Other categories return empty
            return {"ids": [], "metadatas": []}

        mock_retriever.collection.get.side_effect = mock_get_side_effect

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: All subcategories fields are lists
        for category in categories:
            assert isinstance(category["subcategories"], list)

        # Verify: Code has populated list, others are empty
        code_category = next(cat for cat in categories if cat["name"] == "code")
        assert len(code_category["subcategories"]) > 0

        orchestration_category = next(
            cat for cat in categories if cat["name"] == "orchestration"
        )
        assert len(orchestration_category["subcategories"]) == 0

    # ========================================================================
    # Test Group 2: Count Accuracy Tests (Subtask 3.2)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_categories_correct_category_counts(self, mock_retriever):
        """Test that category counts match actual cases in collection."""

        # Setup: Mock ChromaDB to return specific counts per category
        def mock_get_side_effect(**kwargs):
            category = kwargs.get("where", {}).get("category", "")

            if category == "code":
                return {
                    "ids": ["code-1", "code-2", "code-3", "code-4", "code-5"],
                    "metadatas": [{"category": "code", "subcategory": "general"}] * 5,
                }
            elif category == "orchestration":
                return {
                    "ids": ["orch-1", "orch-2", "orch-3"],
                    "metadatas": [
                        {"category": "orchestration", "subcategory": "remediation"}
                    ]
                    * 3,
                }
            elif category == "best-practice":
                return {
                    "ids": ["bp-1", "bp-2"],
                    "metadatas": [
                        {"category": "best-practice", "subcategory": "planning"}
                    ]
                    * 2,
                }
            elif category == "anti-pattern":
                return {
                    "ids": ["ap-1"],
                    "metadatas": [
                        {"category": "anti-pattern", "subcategory": "completion-bias"}
                    ],
                }
            return {"ids": [], "metadatas": []}

        mock_retriever.collection.get.side_effect = mock_get_side_effect

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: Category counts are correct
        category_counts = {cat["name"]: cat["count"] for cat in categories}
        assert category_counts["code"] == 5
        assert category_counts["orchestration"] == 3
        assert category_counts["best-practice"] == 2
        assert category_counts["anti-pattern"] == 1

    @pytest.mark.asyncio
    async def test_get_categories_correct_subcategory_counts(self, mock_retriever):
        """Test that subcategory counts are accurate."""

        # Setup: Mock ChromaDB to return cases with multiple subcategories
        def mock_get_side_effect(**kwargs):
            category = kwargs.get("where", {}).get("category", "")

            if category == "code":
                return {
                    "ids": ["code-1", "code-2", "code-3", "code-4", "code-5"],
                    "metadatas": [
                        {"category": "code", "subcategory": "firebase-auth"},
                        {"category": "code", "subcategory": "firebase-auth"},
                        {"category": "code", "subcategory": "firebase-auth"},
                        {"category": "code", "subcategory": "react-components"},
                        {"category": "code", "subcategory": "react-components"},
                    ],
                }
            return {"ids": [], "metadatas": []}

        mock_retriever.collection.get.side_effect = mock_get_side_effect

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: Subcategory counts are correct
        code_category = next(cat for cat in categories if cat["name"] == "code")
        assert code_category["count"] == 5

        subcategory_counts = {
            sub["name"]: sub["count"] for sub in code_category["subcategories"]
        }
        assert subcategory_counts["firebase-auth"] == 3
        assert subcategory_counts["react-components"] == 2

        # Verify: Total subcategory counts equals total category count
        total_subcat_count = sum(sub["count"] for sub in code_category["subcategories"])
        assert total_subcat_count == code_category["count"]

    @pytest.mark.asyncio
    async def test_get_categories_all_subcategories_present(self, mock_retriever):
        """Test that all defined subcategories appear when cases exist."""

        # Setup: Mock ChromaDB to return at least one case per subcategory
        def mock_get_side_effect(**kwargs):
            category = kwargs.get("where", {}).get("category", "")

            if category == "code":
                return {
                    "ids": ["c1", "c2", "c3", "c4", "c5", "c6"],
                    "metadatas": [
                        {"category": "code", "subcategory": "firebase-auth"},
                        {"category": "code", "subcategory": "react-components"},
                        {"category": "code", "subcategory": "api-routes"},
                        {"category": "code", "subcategory": "database"},
                        {"category": "code", "subcategory": "testing"},
                        {"category": "code", "subcategory": "general"},
                    ],
                }
            elif category == "orchestration":
                return {
                    "ids": ["o1", "o2", "o3", "o4", "o5"],
                    "metadatas": [
                        {"category": "orchestration", "subcategory": "remediation"},
                        {"category": "orchestration", "subcategory": "planning"},
                        {"category": "orchestration", "subcategory": "delegation"},
                        {"category": "orchestration", "subcategory": "verification"},
                        {"category": "orchestration", "subcategory": "completion"},
                    ],
                }
            elif category == "best-practice":
                return {
                    "ids": ["b1", "b2", "b3"],
                    "metadatas": [
                        {"category": "best-practice", "subcategory": "planning"},
                        {"category": "best-practice", "subcategory": "verification"},
                        {"category": "best-practice", "subcategory": "error-handling"},
                    ],
                }
            elif category == "anti-pattern":
                return {
                    "ids": ["a1", "a2", "a3"],
                    "metadatas": [
                        {"category": "anti-pattern", "subcategory": "completion-bias"},
                        {
                            "category": "anti-pattern",
                            "subcategory": "verification-skip",
                        },
                        {
                            "category": "anti-pattern",
                            "subcategory": "protocol-violation",
                        },
                    ],
                }
            return {"ids": [], "metadatas": []}

        mock_retriever.collection.get.side_effect = mock_get_side_effect

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: Code category includes all expected subcategories
        code_category = next(cat for cat in categories if cat["name"] == "code")
        code_subcats = {sub["name"] for sub in code_category["subcategories"]}
        expected_code_subcats = {
            "firebase-auth",
            "react-components",
            "api-routes",
            "database",
            "testing",
            "general",
        }
        assert code_subcats == expected_code_subcats

        # Verify: Orchestration category includes all expected subcategories
        orch_category = next(
            cat for cat in categories if cat["name"] == "orchestration"
        )
        orch_subcats = {sub["name"] for sub in orch_category["subcategories"]}
        expected_orch_subcats = {
            "remediation",
            "planning",
            "delegation",
            "verification",
            "completion",
        }
        assert orch_subcats == expected_orch_subcats

        # Verify: Best-practice category includes all expected subcategories
        bp_category = next(cat for cat in categories if cat["name"] == "best-practice")
        bp_subcats = {sub["name"] for sub in bp_category["subcategories"]}
        expected_bp_subcats = {"planning", "verification", "error-handling"}
        assert bp_subcats == expected_bp_subcats

        # Verify: Anti-pattern category includes all expected subcategories
        ap_category = next(cat for cat in categories if cat["name"] == "anti-pattern")
        ap_subcats = {sub["name"] for sub in ap_category["subcategories"]}
        expected_ap_subcats = {
            "completion-bias",
            "verification-skip",
            "protocol-violation",
        }
        assert ap_subcats == expected_ap_subcats

    @pytest.mark.asyncio
    async def test_get_categories_unknown_subcategory_handling(self, mock_retriever):
        """Test that unknown subcategories are included in results."""

        # Setup: Mock ChromaDB to return case with unknown subcategory
        def mock_get_side_effect(**kwargs):
            category = kwargs.get("where", {}).get("category", "")

            if category == "code":
                return {
                    "ids": ["code-1", "code-2"],
                    "metadatas": [
                        {"category": "code", "subcategory": "firebase-auth"},
                        {"category": "code", "subcategory": "unknown-custom"},
                    ],
                }
            return {"ids": [], "metadatas": []}

        mock_retriever.collection.get.side_effect = mock_get_side_effect

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: Unknown subcategory appears in results
        code_category = next(cat for cat in categories if cat["name"] == "code")
        subcategory_names = {sub["name"] for sub in code_category["subcategories"]}

        assert "unknown-custom" in subcategory_names
        assert "firebase-auth" in subcategory_names

        # Verify: Unknown subcategory has correct count
        unknown_subcat = next(
            sub
            for sub in code_category["subcategories"]
            if sub["name"] == "unknown-custom"
        )
        assert unknown_subcat["count"] == 1

    # ========================================================================
    # Test Group 3: Empty Collection Tests (Subtask 3.3)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_categories_empty_collection_returns_four_categories(
        self, mock_retriever
    ):
        """Test that empty collection still returns 4 categories."""
        # Setup: Mock ChromaDB to return empty results for all categories
        mock_retriever.collection.get.return_value = {"ids": [], "metadatas": []}

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: Returns list with 4 categories
        assert isinstance(categories, list)
        assert len(categories) == 4

        # Verify: All category names present
        category_names = {cat["name"] for cat in categories}
        assert category_names == {
            "code",
            "orchestration",
            "best-practice",
            "anti-pattern",
        }

    @pytest.mark.asyncio
    async def test_get_categories_empty_collection_zero_counts(self, mock_retriever):
        """Test that empty collection has count=0 for all categories."""
        # Setup: Mock ChromaDB to return empty results
        mock_retriever.collection.get.return_value = {"ids": [], "metadatas": []}

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: All categories have count=0
        for category in categories:
            assert (
                category["count"] == 0
            ), f"Category {category['name']} should have count=0"

    @pytest.mark.asyncio
    async def test_get_categories_empty_collection_empty_subcategories(
        self, mock_retriever
    ):
        """Test that empty collection has empty subcategories lists."""
        # Setup: Mock ChromaDB to return empty results
        mock_retriever.collection.get.return_value = {"ids": [], "metadatas": []}

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: All categories have empty subcategories lists
        for category in categories:
            assert (
                category["subcategories"] == []
            ), f"Category {category['name']} should have empty subcategories"

    # ========================================================================
    # Test Group 4: ChromaDB Integration Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_categories_calls_chromadb_correctly(self, mock_retriever):
        """Test that get_categories calls ChromaDB with correct parameters."""
        # Setup: Mock ChromaDB
        mock_retriever.collection.get.return_value = {"ids": [], "metadatas": []}

        # Execute
        await mock_retriever.get_categories()

        # Verify: collection.get called 4 times (once per category)
        assert mock_retriever.collection.get.call_count == 4

        # Verify: Each call has correct where filter
        call_args_list = mock_retriever.collection.get.call_args_list
        categories_queried = [call[1]["where"]["category"] for call in call_args_list]
        assert set(categories_queried) == {
            "code",
            "orchestration",
            "best-practice",
            "anti-pattern",
        }

        # Verify: include parameter contains metadatas
        for call in call_args_list:
            assert "include" in call[1]
            assert "metadatas" in call[1]["include"]

    @pytest.mark.asyncio
    async def test_get_categories_sorted_subcategories(self, mock_retriever):
        """Test that subcategories are sorted alphabetically."""

        # Setup: Mock ChromaDB to return subcategories in random order
        def mock_get_side_effect(**kwargs):
            category = kwargs.get("where", {}).get("category", "")

            if category == "code":
                return {
                    "ids": ["c1", "c2", "c3", "c4"],
                    "metadatas": [
                        {"category": "code", "subcategory": "testing"},
                        {"category": "code", "subcategory": "api-routes"},
                        {"category": "code", "subcategory": "react-components"},
                        {"category": "code", "subcategory": "firebase-auth"},
                    ],
                }
            return {"ids": [], "metadatas": []}

        mock_retriever.collection.get.side_effect = mock_get_side_effect

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: Subcategories are sorted alphabetically
        code_category = next(cat for cat in categories if cat["name"] == "code")
        subcategory_names = [sub["name"] for sub in code_category["subcategories"]]

        expected_sorted = ["api-routes", "firebase-auth", "react-components", "testing"]
        assert subcategory_names == expected_sorted

    # ========================================================================
    # Test Group 5: Edge Cases and Error Handling
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_categories_missing_subcategory_field(self, mock_retriever):
        """Test handling of metadata missing subcategory field."""

        # Setup: Mock ChromaDB to return metadata without subcategory field
        def mock_get_side_effect(**kwargs):
            category = kwargs.get("where", {}).get("category", "")

            if category == "code":
                return {
                    "ids": ["code-1", "code-2"],
                    "metadatas": [
                        {"category": "code", "subcategory": "firebase-auth"},
                        {"category": "code"},  # Missing subcategory field
                    ],
                }
            return {"ids": [], "metadatas": []}

        mock_retriever.collection.get.side_effect = mock_get_side_effect

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: Missing subcategory defaults to "unknown"
        code_category = next(cat for cat in categories if cat["name"] == "code")
        subcategory_names = {sub["name"] for sub in code_category["subcategories"]}

        assert "firebase-auth" in subcategory_names
        assert "unknown" in subcategory_names

    @pytest.mark.asyncio
    async def test_get_categories_has_correct_descriptions(self, mock_retriever):
        """Test that category descriptions are meaningful and correct."""
        # Setup: Mock ChromaDB
        mock_retriever.collection.get.return_value = {"ids": [], "metadatas": []}

        # Execute
        categories = await mock_retriever.get_categories()

        # Verify: Each category has a non-empty description
        category_descriptions = {cat["name"]: cat["description"] for cat in categories}

        assert len(category_descriptions["code"]) > 0
        assert len(category_descriptions["orchestration"]) > 0
        assert len(category_descriptions["best-practice"]) > 0
        assert len(category_descriptions["anti-pattern"]) > 0

        # Verify: Descriptions contain relevant keywords
        assert (
            "code" in category_descriptions["code"].lower()
            or "implementation" in category_descriptions["code"].lower()
        )
        assert (
            "orchestration" in category_descriptions["orchestration"].lower()
            or "agent" in category_descriptions["orchestration"].lower()
        )
        assert (
            "best" in category_descriptions["best-practice"].lower()
            or "practice" in category_descriptions["best-practice"].lower()
        )
        assert (
            "anti" in category_descriptions["anti-pattern"].lower()
            or "mistake" in category_descriptions["anti-pattern"].lower()
        )
