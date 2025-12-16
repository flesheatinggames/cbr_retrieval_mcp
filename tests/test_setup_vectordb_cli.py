"""
Comprehensive test suite for CLI functionality in setup_vectordb.py.

This test file verifies the command-line interface features added to setup_vectordb.py:
- Argument parsing with argparse
- Case filtering logic with AND/OR combinations
- Category and subcategory listing functionality
- Main execution flow with early exits
"""

# Add the src directory to path for importing setup_vectordb
import os
import sys
from argparse import Namespace
from unittest.mock import MagicMock, Mock, patch

import pytest

src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
sys.path.insert(0, src_path)

# Mock ChromaDB and SentenceTransformer before importing setup_vectordb
# This prevents attempting to download models or connect to databases during import
with (
    patch("chromadb.PersistentClient"),
    patch("sentence_transformers.SentenceTransformer"),
):
    from cbr_mcp_server.utilities.setup_vectordb import (
        filter_cases,
        list_categories,
        list_subcategories,
        main,
        parse_arguments,
    )


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_cases():
    """Fixture providing a diverse sample case list for testing filters."""
    return [
        {
            "problem": "Firebase auth problem 1",
            "solution": "Firebase auth solution 1",
            "category": "firebase",
            "subcategory": "auth",
            "tags": ["authentication", "login"],
        },
        {
            "problem": "Firebase storage problem",
            "solution": "Firebase storage solution",
            "category": "firebase",
            "subcategory": "storage",
            "tags": ["storage", "upload"],
        },
        {
            "problem": "React hooks problem",
            "solution": "React hooks solution",
            "category": "react",
            "subcategory": "hooks",
            "tags": ["hooks", "state"],
        },
        {
            "problem": "React components problem",
            "solution": "React components solution",
            "category": "react",
            "subcategory": "components",
            "tags": ["components", "ui"],
        },
        {
            "problem": "Next.js routing problem",
            "solution": "Next.js routing solution",
            "category": "nextjs",
            "subcategory": "routing",
            "tags": ["routing", "pages"],
        },
        {
            "problem": "Security auth problem",
            "solution": "Security auth solution",
            "category": "security",
            "subcategory": "auth",
            "tags": ["authentication", "security"],
        },
    ]


@pytest.fixture
def empty_cases():
    """Fixture providing an empty case list for edge case testing."""
    return []


# ============================================================================
# Test parse_arguments()
# ============================================================================


class TestParseArguments:
    """Test suite for CLI argument parsing functionality."""

    def test_no_arguments_returns_defaults(self, monkeypatch):
        """Test that parse_arguments with no args returns default values."""
        monkeypatch.setattr(sys, "argv", ["setup_vectordb.py"])
        args = parse_arguments()

        assert args.category is None
        assert args.subcategory is None
        assert args.tags is None
        assert args.modules is None
        assert args.list_categories is False
        assert args.list_subcategories is None
        assert args.force is False

    def test_single_category_argument(self, monkeypatch):
        """Test parsing a single category filter."""
        monkeypatch.setattr(
            sys, "argv", ["setup_vectordb.py", "--category", "firebase"]
        )
        args = parse_arguments()

        assert args.category == ["firebase"]
        assert args.subcategory is None
        assert args.tags is None

    def test_multiple_categories_argument(self, monkeypatch):
        """Test parsing multiple category filters."""
        monkeypatch.setattr(
            sys,
            "argv",
            ["setup_vectordb.py", "--category", "firebase", "rust", "nextjs"],
        )
        args = parse_arguments()

        assert args.category == ["firebase", "rust", "nextjs"]
        assert len(args.category) == 3

    def test_subcategory_argument(self, monkeypatch):
        """Test parsing subcategory filter."""
        monkeypatch.setattr(
            sys, "argv", ["setup_vectordb.py", "--subcategory", "auth", "components"]
        )
        args = parse_arguments()

        assert args.subcategory == ["auth", "components"]
        assert len(args.subcategory) == 2

    def test_tags_argument(self, monkeypatch):
        """Test parsing tags filter."""
        monkeypatch.setattr(
            sys, "argv", ["setup_vectordb.py", "--tags", "authentication", "security"]
        )
        args = parse_arguments()

        assert args.tags == ["authentication", "security"]
        assert len(args.tags) == 2

    def test_combined_category_and_tags(self, monkeypatch):
        """Test parsing combined category and tags filters."""
        monkeypatch.setattr(
            sys,
            "argv",
            ["setup_vectordb.py", "--category", "firebase", "--tags", "authentication"],
        )
        args = parse_arguments()

        assert args.category == ["firebase"]
        assert args.tags == ["authentication"]

    def test_force_flag(self, monkeypatch):
        """Test parsing --force flag."""
        monkeypatch.setattr(sys, "argv", ["setup_vectordb.py", "--force"])
        args = parse_arguments()

        assert args.force is True

    def test_list_categories_flag(self, monkeypatch):
        """Test parsing --list-categories flag."""
        monkeypatch.setattr(sys, "argv", ["setup_vectordb.py", "--list-categories"])
        args = parse_arguments()

        assert args.list_categories is True

    def test_list_subcategories_argument(self, monkeypatch):
        """Test parsing --list-subcategories with category name."""
        monkeypatch.setattr(
            sys, "argv", ["setup_vectordb.py", "--list-subcategories", "orchestration"]
        )
        args = parse_arguments()

        assert args.list_subcategories == "orchestration"

    def test_modules_argument(self, monkeypatch):
        """Test parsing --modules with file paths."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "setup_vectordb.py",
                "--modules",
                "cases/firebase/firebase_auth_cases.py",
                "cases/react/react_components_cases.py",
            ],
        )
        args = parse_arguments()

        assert args.modules == [
            "cases/firebase/firebase_auth_cases.py",
            "cases/react/react_components_cases.py",
        ]
        assert len(args.modules) == 2


# ============================================================================
# Test filter_cases()
# ============================================================================


class TestFilterCases:
    """Test suite for case filtering logic."""

    def test_no_filters_returns_all_cases(self, sample_cases):
        """Test that filter_cases with no filters returns all input cases."""
        args = Namespace(category=None, subcategory=None, tags=None, modules=None)

        result = filter_cases(sample_cases, args)

        assert len(result) == len(sample_cases)
        assert result == sample_cases

    def test_single_category_filter(self, sample_cases):
        """Test filtering by a single category."""
        args = Namespace(
            category=["firebase"], subcategory=None, tags=None, modules=None
        )

        result = filter_cases(sample_cases, args)

        assert len(result) == 2
        assert all(case["category"] == "firebase" for case in result)

    def test_multiple_categories_or_logic(self, sample_cases):
        """Test filtering by multiple categories uses OR logic."""
        args = Namespace(
            category=["firebase", "nextjs"], subcategory=None, tags=None, modules=None
        )

        result = filter_cases(sample_cases, args)

        assert len(result) == 3
        assert all(case["category"] in ["firebase", "nextjs"] for case in result)

    def test_subcategory_filter(self, sample_cases):
        """Test filtering by subcategory."""
        args = Namespace(category=None, subcategory=["auth"], tags=None, modules=None)

        result = filter_cases(sample_cases, args)

        assert len(result) == 2
        assert all(case["subcategory"] == "auth" for case in result)

    def test_tag_filter_or_logic(self, sample_cases):
        """Test filtering by tags uses OR logic (any tag match)."""
        args = Namespace(
            category=None, subcategory=None, tags=["authentication"], modules=None
        )

        result = filter_cases(sample_cases, args)

        # Should match firebase auth and security auth cases
        assert len(result) == 2
        assert all("authentication" in case["tags"] for case in result)

    def test_combined_category_and_subcategory_and_logic(self, sample_cases):
        """Test combined category and subcategory filters use AND logic."""
        args = Namespace(
            category=["firebase"], subcategory=["auth"], tags=None, modules=None
        )

        result = filter_cases(sample_cases, args)

        assert len(result) == 1
        assert result[0]["category"] == "firebase"
        assert result[0]["subcategory"] == "auth"

    def test_combined_category_and_tags_and_logic(self, sample_cases):
        """Test combined category and tags filters use AND logic."""
        args = Namespace(
            category=["firebase"],
            subcategory=None,
            tags=["authentication"],
            modules=None,
        )

        result = filter_cases(sample_cases, args)

        assert len(result) == 1
        assert result[0]["category"] == "firebase"
        assert "authentication" in result[0]["tags"]

    def test_all_filters_combined_and_logic(self, sample_cases):
        """Test all filters combined use AND logic across all dimensions."""
        args = Namespace(
            category=["firebase", "security"],
            subcategory=["auth"],
            tags=["authentication"],
            modules=None,
        )

        result = filter_cases(sample_cases, args)

        # Should match firebase auth and security auth
        assert len(result) == 2
        assert all(case["category"] in ["firebase", "security"] for case in result)
        assert all(case["subcategory"] == "auth" for case in result)
        assert all("authentication" in case["tags"] for case in result)

    def test_nonexistent_category_returns_empty_list(self, sample_cases):
        """Test filtering by non-existent category returns empty list."""
        args = Namespace(
            category=["nonexistent"], subcategory=None, tags=None, modules=None
        )

        result = filter_cases(sample_cases, args)

        assert len(result) == 0
        assert result == []

    def test_empty_case_list_returns_empty_list(self, empty_cases):
        """Test filtering an empty case list returns empty list."""
        args = Namespace(
            category=["firebase"], subcategory=None, tags=None, modules=None
        )

        result = filter_cases(empty_cases, args)

        assert len(result) == 0
        assert result == []

    def test_modules_filter_prints_warning(self, sample_cases, capsys):
        """Test that modules filter prints not-implemented warning."""
        args = Namespace(
            category=None,
            subcategory=None,
            tags=None,
            modules=["cases/firebase/firebase_auth_cases.py"],
        )

        result = filter_cases(sample_cases, args)

        captured = capsys.readouterr()
        assert "Warning: --modules filtering not yet implemented" in captured.out
        # Should still return all cases since module filtering is not implemented
        assert len(result) == len(sample_cases)


# ============================================================================
# Test list_categories()
# ============================================================================


class TestListCategories:
    """Test suite for category listing functionality."""

    def test_normal_case_list_prints_all_categories(self, sample_cases, capsys):
        """Test that list_categories prints all unique categories."""
        list_categories(sample_cases)

        captured = capsys.readouterr()
        output = captured.out

        assert "firebase" in output
        assert "react" in output
        assert "nextjs" in output
        assert "security" in output

    def test_category_counts_are_accurate(self, sample_cases, capsys):
        """Test that category counts match actual case distribution."""
        list_categories(sample_cases)

        captured = capsys.readouterr()
        output = captured.out

        # Firebase has 2 cases
        assert "(2 cases)" in output
        # React has 2 cases
        assert "(2 cases)" in output
        # Nextjs has 1 case
        assert "(1 case)" in output or "(1 cases)" in output
        # Security has 1 case
        assert "(1 case)" in output or "(1 cases)" in output

    def test_output_format_has_separators(self, sample_cases, capsys):
        """Test that output has proper separator lines."""
        list_categories(sample_cases)

        captured = capsys.readouterr()
        output = captured.out

        # Should have separator lines
        assert "=" * 50 in output
        assert "Available Categories:" in output

    def test_total_count_matches_case_list_length(self, sample_cases, capsys):
        """Test that total count matches the input case list length."""
        list_categories(sample_cases)

        captured = capsys.readouterr()
        output = captured.out

        assert f"Total: {len(sample_cases)} cases" in output

    def test_empty_case_list_graceful_handling(self, empty_cases, capsys):
        """Test that empty case list is handled gracefully."""
        list_categories(empty_cases)

        captured = capsys.readouterr()
        output = captured.out

        assert "Total: 0 cases" in output
        assert "0 categories" in output

    def test_categories_are_sorted_alphabetically(self, sample_cases, capsys):
        """Test that categories are displayed in alphabetical order."""
        list_categories(sample_cases)

        captured = capsys.readouterr()
        output = captured.out

        # Find positions of categories in output
        firebase_pos = output.find("firebase")
        nextjs_pos = output.find("nextjs")
        react_pos = output.find("react")
        security_pos = output.find("security")

        # Verify alphabetical ordering
        assert firebase_pos < nextjs_pos < react_pos < security_pos


# ============================================================================
# Test list_subcategories()
# ============================================================================


class TestListSubcategories:
    """Test suite for subcategory listing functionality."""

    def test_valid_category_prints_all_subcategories(self, sample_cases, capsys):
        """Test that list_subcategories prints all subcategories for valid category."""
        list_subcategories(sample_cases, "firebase")

        captured = capsys.readouterr()
        output = captured.out

        assert "auth" in output
        assert "storage" in output
        assert "Subcategories for 'firebase'" in output

    def test_subcategory_counts_are_accurate(self, sample_cases, capsys):
        """Test that subcategory counts match actual distribution."""
        list_subcategories(sample_cases, "react")

        captured = capsys.readouterr()
        output = captured.out

        # React has 1 hooks case and 1 components case
        assert "(1 case)" in output or "(1 cases)" in output

    def test_invalid_category_prints_error(self, sample_cases, capsys):
        """Test that invalid category prints error message."""
        list_subcategories(sample_cases, "nonexistent")

        captured = capsys.readouterr()
        output = captured.out

        assert "Error: Category 'nonexistent' not found" in output
        assert "Available categories:" in output

    def test_invalid_category_lists_available_categories(self, sample_cases, capsys):
        """Test that invalid category shows list of available categories."""
        list_subcategories(sample_cases, "invalid")

        captured = capsys.readouterr()
        output = captured.out

        assert "firebase" in output
        assert "react" in output
        assert "nextjs" in output
        assert "security" in output

    def test_output_format_has_separators(self, sample_cases, capsys):
        """Test that subcategory output has proper separator lines."""
        list_subcategories(sample_cases, "firebase")

        captured = capsys.readouterr()
        output = captured.out

        # Should have separator lines
        assert "=" * 50 in output

    def test_total_count_matches_filtered_cases(self, sample_cases, capsys):
        """Test that total count matches the number of cases in the category."""
        list_subcategories(sample_cases, "firebase")

        captured = capsys.readouterr()
        output = captured.out

        # Firebase has 2 cases total
        assert "Total: 2 cases" in output

    def test_subcategories_are_sorted_alphabetically(self, sample_cases, capsys):
        """Test that subcategories are displayed in alphabetical order."""
        list_subcategories(sample_cases, "firebase")

        captured = capsys.readouterr()
        output = captured.out

        # Find positions in output
        auth_pos = output.find("auth")
        storage_pos = output.find("storage")

        # Verify alphabetical ordering (auth comes before storage)
        assert auth_pos < storage_pos


# ============================================================================
# Test main() integration
# ============================================================================


class TestMainIntegration:
    """Test suite for main() execution flow and integration."""

    def test_list_categories_exits_early(self, monkeypatch, sample_cases):
        """Test that --list-categories exits early with code 0."""
        monkeypatch.setattr(sys, "argv", ["setup_vectordb.py", "--list-categories"])

        with (
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.load_all_cases",
                return_value=sample_cases,
            ),
            patch("cbr_mcp_server.utilities.setup_vectordb.sys.exit") as mock_exit,
        ):
            main()

            mock_exit.assert_called_once_with(0)

    def test_list_subcategories_exits_early(self, monkeypatch, sample_cases):
        """Test that --list-subcategories exits early with code 0."""
        monkeypatch.setattr(
            sys, "argv", ["setup_vectordb.py", "--list-subcategories", "firebase"]
        )

        with (
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.load_all_cases",
                return_value=sample_cases,
            ),
            patch("cbr_mcp_server.utilities.setup_vectordb.sys.exit") as mock_exit,
        ):
            main()

            mock_exit.assert_called_once_with(0)

    def test_filtering_produces_feedback_message(
        self, monkeypatch, sample_cases, capsys
    ):
        """Test that filtering produces feedback with correct counts."""
        monkeypatch.setattr(
            sys, "argv", ["setup_vectordb.py", "--category", "firebase"]
        )

        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]]

        mock_collection = Mock()
        mock_collection.count.return_value = 0
        mock_collection.add = Mock()

        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection

        with (
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.load_all_cases",
                return_value=sample_cases,
            ),
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.SentenceTransformer",
                return_value=mock_model,
            ),
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient",
                return_value=mock_client,
            ),
        ):
            main()

        captured = capsys.readouterr()
        output = captured.out

        # Should show filtered count
        assert "Filtered to 2 cases (out of 6 total)" in output
        assert "Categories: firebase" in output

    def test_backward_compatibility_no_args_loads_all_cases(
        self, monkeypatch, sample_cases, capsys
    ):
        """Test that no arguments loads all cases (backward compatibility)."""
        monkeypatch.setattr(sys, "argv", ["setup_vectordb.py"])

        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]]

        mock_collection = Mock()
        mock_collection.count.return_value = 0
        mock_collection.add = Mock()

        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection

        with (
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.load_all_cases",
                return_value=sample_cases,
            ),
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.SentenceTransformer",
                return_value=mock_model,
            ),
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient",
                return_value=mock_client,
            ),
        ):
            main()

        captured = capsys.readouterr()
        output = captured.out

        # Should indicate loading all cases
        assert "Loading all 6 cases" in output

    def test_empty_filter_result_exits_with_warning(self, monkeypatch, sample_cases):
        """Test that empty filter result exits with code 1 and warning."""
        monkeypatch.setattr(
            sys, "argv", ["setup_vectordb.py", "--category", "nonexistent"]
        )

        with (
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.load_all_cases",
                return_value=sample_cases,
            ),
            patch("cbr_mcp_server.utilities.setup_vectordb.sys.exit") as mock_exit,
        ):
            main()

            mock_exit.assert_called_once_with(1)

    def test_force_rebuild_when_database_exists(self, monkeypatch, sample_cases):
        """Test that --force triggers rebuild when database exists."""
        monkeypatch.setattr(sys, "argv", ["setup_vectordb.py", "--force"])

        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]]

        mock_collection = Mock()
        mock_collection.count.return_value = 10  # Existing database
        mock_collection.add = Mock()

        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client.delete_collection = Mock()
        mock_client.create_collection.return_value = mock_collection

        with (
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.load_all_cases",
                return_value=sample_cases,
            ),
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.SentenceTransformer",
                return_value=mock_model,
            ),
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient",
                return_value=mock_client,
            ),
        ):
            main()

        # Verify delete_collection was called for force rebuild
        mock_client.delete_collection.assert_called_once_with(
            name="code_solutions_case_base"
        )

    def test_module_filter_warning_is_printed(self, monkeypatch, sample_cases, capsys):
        """Test that module filter prints not-implemented warning."""
        monkeypatch.setattr(
            sys,
            "argv",
            ["setup_vectordb.py", "--modules", "cases/firebase/firebase_auth_cases.py"],
        )

        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]]

        mock_collection = Mock()
        mock_collection.count.return_value = 0
        mock_collection.add = Mock()

        mock_client = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection

        with (
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.load_all_cases",
                return_value=sample_cases,
            ),
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.SentenceTransformer",
                return_value=mock_model,
            ),
            patch(
                "cbr_mcp_server.utilities.setup_vectordb.chromadb.PersistentClient",
                return_value=mock_client,
            ),
        ):
            main()

        captured = capsys.readouterr()
        output = captured.out

        assert "Warning: --modules filtering not yet implemented" in output
