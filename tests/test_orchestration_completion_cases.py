"""
Comprehensive test suite for orchestration_completion_cases.py module.

This test suite validates the structure, metadata, and content of the
orchestration completion cases following TDD principles.

Test Coverage:
- Module and file structure validation
- Case count verification (exactly 1 case)
- Metadata schema validation
- Category and subcategory validation
- Tags content and structure validation
- Problem and solution field validation
- Topic coverage validation (completion-specific)
- Copy-paste error prevention
- Case completeness checks
"""

import os
from pathlib import Path

import pytest


# Fixtures for reusable test data
@pytest.fixture
def completion_cases():
    """Load the orchestration completion cases module."""
    from cases.orchestration.orchestration_completion_cases import (
        ORCHESTRATION_COMPLETION_CASES,
    )

    return ORCHESTRATION_COMPLETION_CASES


@pytest.fixture
def completion_case(completion_cases):
    """Get the single completion case for testing."""
    return completion_cases[0] if completion_cases else None


@pytest.fixture
def case_metadata(completion_case):
    """Get the metadata from the completion case."""
    return completion_case if completion_case else {}


@pytest.fixture
def completion_keywords():
    """Define completion-related keywords that should appear in the case."""
    return [
        "completion",
        "workflow",
        "tasks",
        "reporting",
        "summary",
        "finalization",
        "wrap-up",
        "orchestration",
        "complete",
        "finish",
        "final",
        "conclude",
        "end",
        "done",
    ]


@pytest.fixture
def inappropriate_keywords():
    """Define keywords from other subcategories that should NOT appear."""
    return {
        "planning": ["plan", "sequential-thinking", "decompose"],
        "remediation": ["remediation", "INCOMPLETE", "FAILED", "fix", "retry"],
        "delegation": ["delegate", "agent", "specialist", "handoff"],
        "verification": ["karen", "verify", "validation", "test"],
    }


# Module and File Structure Tests
class TestModuleStructure:
    """Test the module and file structure of orchestration_completion_cases."""

    def test_module_can_be_imported(self):
        """Test that the module can be imported successfully."""
        try:
            from cases.orchestration import orchestration_completion_cases

            assert orchestration_completion_cases is not None
        except ImportError as e:
            pytest.fail(f"Failed to import orchestration_completion_cases: {e}")

    def test_cases_variable_exists(self, completion_cases):
        """Test that ORCHESTRATION_COMPLETION_CASES variable exists."""
        assert completion_cases is not None

    def test_module_file_exists(self):
        """Test that the module file exists at the expected location."""
        expected_path = Path("cases/orchestration/orchestration_completion_cases.py")
        assert expected_path.exists(), f"Expected file not found: {expected_path}"


# Case Count Validation Tests
class TestCaseCount:
    """Test that exactly 1 case exists in the module."""

    def test_cases_is_list(self, completion_cases):
        """Test that ORCHESTRATION_COMPLETION_CASES is a list."""
        assert isinstance(
            completion_cases, list
        ), "ORCHESTRATION_COMPLETION_CASES must be a list"

    def test_exactly_one_case(self, completion_cases):
        """Test that exactly 1 case exists."""
        assert (
            len(completion_cases) == 1
        ), f"Expected exactly 1 case, found {len(completion_cases)}"


# Metadata Schema Validation Tests
class TestMetadataSchema:
    """Test the metadata schema structure and required fields."""

    def test_case_has_required_keys(self, completion_case):
        """Test that the case has all required top-level keys."""
        required_keys = ["category", "subcategory", "tags", "problem", "solution"]
        for key in required_keys:
            assert key in completion_case, f"Case must have '{key}' key"

    def test_metadata_has_category(self, case_metadata):
        """Test that metadata contains 'category' field."""
        assert "category" in case_metadata, "Metadata must have 'category' field"

    def test_metadata_has_subcategory(self, case_metadata):
        """Test that metadata contains 'subcategory' field."""
        assert "subcategory" in case_metadata, "Metadata must have 'subcategory' field"

    def test_metadata_has_tags(self, case_metadata):
        """Test that metadata contains 'tags' field."""
        assert "tags" in case_metadata, "Metadata must have 'tags' field"

    def test_metadata_has_problem(self, case_metadata):
        """Test that metadata contains 'problem' field."""
        assert "problem" in case_metadata, "Metadata must have 'problem' field"

    def test_metadata_has_solution(self, case_metadata):
        """Test that metadata contains 'solution' field."""
        assert "solution" in case_metadata, "Metadata must have 'solution' field"

    def test_category_is_string(self, case_metadata):
        """Test that category is a string."""
        assert isinstance(case_metadata["category"], str), "Category must be a string"

    def test_subcategory_is_string(self, case_metadata):
        """Test that subcategory is a string."""
        assert isinstance(
            case_metadata["subcategory"], str
        ), "Subcategory must be a string"

    def test_tags_is_list(self, case_metadata):
        """Test that tags is a list."""
        assert isinstance(case_metadata["tags"], list), "Tags must be a list"

    def test_tags_is_non_empty(self, case_metadata):
        """Test that tags list is not empty."""
        assert len(case_metadata["tags"]) > 0, "Tags list must not be empty"

    def test_tags_has_minimum_count(self, case_metadata):
        """Test that tags contains at least 2 items."""
        assert (
            len(case_metadata["tags"]) >= 2
        ), f"Tags must have at least 2 items, found {len(case_metadata['tags'])}"


# Category and Subcategory Validation Tests
class TestCategoryAndSubcategory:
    """Test category and subcategory field values."""

    def test_category_is_orchestration(self, case_metadata):
        """Test that category is exactly 'orchestration'."""
        assert (
            case_metadata["category"] == "orchestration"
        ), f"Category must be 'orchestration', found '{case_metadata['category']}'"

    def test_subcategory_is_completion(self, case_metadata):
        """Test that subcategory is exactly 'completion'."""
        assert (
            case_metadata["subcategory"] == "completion"
        ), f"Subcategory must be 'completion', found '{case_metadata['subcategory']}'"

    def test_category_not_empty(self, case_metadata):
        """Test that category is not an empty string."""
        assert case_metadata["category"].strip() != "", "Category must not be empty"

    def test_subcategory_not_empty(self, case_metadata):
        """Test that subcategory is not an empty string."""
        assert (
            case_metadata["subcategory"].strip() != ""
        ), "Subcategory must not be empty"


# Tags Content Validation Tests
class TestTagsContent:
    """Test the content and structure of tags."""

    def test_all_tags_are_strings(self, case_metadata):
        """Test that all tags are non-empty strings."""
        for tag in case_metadata["tags"]:
            assert isinstance(tag, str), f"Tag must be string, found {type(tag)}"
            assert tag.strip() != "", "Tag must not be empty"

    def test_tags_include_completion_keywords(self, case_metadata, completion_keywords):
        """Test that tags include completion-related keywords."""
        tags_lower = [tag.lower() for tag in case_metadata["tags"]]
        matching_keywords = [
            keyword
            for keyword in completion_keywords
            if any(keyword in tag for tag in tags_lower)
        ]
        assert (
            len(matching_keywords) >= 1
        ), f"Tags should include at least 1 completion keyword, found: {matching_keywords}"

    def test_orchestration_tag_present(self, case_metadata):
        """Test that 'orchestration' tag is present."""
        tags_lower = [tag.lower() for tag in case_metadata["tags"]]
        assert any(
            "orchestration" in tag for tag in tags_lower
        ), "Tags should include 'orchestration' keyword"


# Problem and Solution Validation Tests
class TestProblemAndSolution:
    """Test problem and solution field content."""

    def test_problem_is_non_empty_string(self, case_metadata):
        """Test that problem is a non-empty string."""
        assert isinstance(case_metadata["problem"], str), "Problem must be a string"
        assert case_metadata["problem"].strip() != "", "Problem must not be empty"

    def test_solution_is_non_empty_string(self, case_metadata):
        """Test that solution is a non-empty string."""
        assert isinstance(case_metadata["solution"], str), "Solution must be a string"
        assert case_metadata["solution"].strip() != "", "Solution must not be empty"

    def test_problem_has_substantial_content(self, case_metadata):
        """Test that problem has substantial content (>20 characters)."""
        assert (
            len(case_metadata["problem"].strip()) > 20
        ), f"Problem should have >20 characters, found {len(case_metadata['problem'].strip())}"

    def test_solution_has_substantial_content(self, case_metadata):
        """Test that solution has substantial content (>50 characters)."""
        assert (
            len(case_metadata["solution"].strip()) > 50
        ), f"Solution should have >50 characters, found {len(case_metadata['solution'].strip())}"


# Topic Coverage Tests
class TestTopicCoverage:
    """Test that the case covers completion-specific topics."""

    def test_solution_contains_completion_keywords(
        self, case_metadata, completion_keywords
    ):
        """Test that solution contains completion-related keywords."""
        solution_lower = case_metadata["solution"].lower()
        matching_keywords = [
            keyword for keyword in completion_keywords if keyword in solution_lower
        ]
        assert (
            len(matching_keywords) >= 2
        ), f"Solution should contain at least 2 completion keywords, found: {matching_keywords}"

    def test_case_covers_completion_patterns(self, case_metadata):
        """Test that the case discusses completion patterns."""
        solution_lower = case_metadata["solution"].lower()
        completion_patterns = [
            "complete",
            "finish",
            "workflow",
            "tasks",
            "summary",
            "final",
        ]
        matching_patterns = [
            pattern for pattern in completion_patterns if pattern in solution_lower
        ]
        assert (
            len(matching_patterns) >= 1
        ), f"Solution should discuss completion patterns, found: {matching_patterns}"


# Copy-Paste Error Prevention Tests
class TestCopyPasteErrorPrevention:
    """Test that no copy-paste errors from other case files exist."""

    def test_category_not_wrong_value(self, case_metadata):
        """Test that category is not from other subcategories."""
        wrong_categories = ["planning", "remediation", "delegation", "verification"]
        assert (
            case_metadata["category"] not in wrong_categories
        ), f"Category should not be {wrong_categories}"

    def test_subcategory_not_wrong_value(self, case_metadata):
        """Test that subcategory is not from other subcategories."""
        wrong_subcategories = ["planning", "remediation", "delegation", "verification"]
        assert (
            case_metadata["subcategory"] not in wrong_subcategories
        ), f"Subcategory should not be {wrong_subcategories}"

    def test_tags_do_not_contain_planning_specific_keywords(self, case_metadata):
        """Test that tags don't contain planning-specific keywords inappropriately."""
        tags_lower = " ".join(case_metadata["tags"]).lower()
        planning_only_keywords = ["sequential-thinking", "decompose"]
        for keyword in planning_only_keywords:
            assert (
                keyword.lower() not in tags_lower
            ), f"Tags should not contain planning-specific keyword: {keyword}"

    def test_tags_do_not_contain_remediation_specific_keywords(self, case_metadata):
        """Test that tags don't contain remediation-specific keywords inappropriately."""
        tags_lower = " ".join(case_metadata["tags"]).lower()
        remediation_only_keywords = ["INCOMPLETE", "FAILED", "remediation protocol"]
        for keyword in remediation_only_keywords:
            assert (
                keyword.lower() not in tags_lower
            ), f"Tags should not contain remediation-specific keyword: {keyword}"

    def test_tags_do_not_contain_delegation_specific_keywords(self, case_metadata):
        """Test that tags don't contain delegation-specific keywords inappropriately."""
        tags_lower = " ".join(case_metadata["tags"]).lower()
        delegation_only_keywords = ["delegate", "specialist", "handoff"]
        for keyword in delegation_only_keywords:
            assert (
                keyword.lower() not in tags_lower
            ), f"Tags should not contain delegation-specific keyword: {keyword}"

    def test_tags_do_not_contain_verification_specific_keywords(self, case_metadata):
        """Test that tags don't contain verification-specific keywords inappropriately."""
        tags_lower = " ".join(case_metadata["tags"]).lower()
        verification_only_keywords = ["karen", "validate", "test"]
        for keyword in verification_only_keywords:
            assert (
                keyword.lower() not in tags_lower
            ), f"Tags should not contain verification-specific keyword: {keyword}"


# Case Completeness Tests
class TestCaseCompleteness:
    """Test that the case is complete and has no placeholders."""

    def test_no_placeholder_text_in_problem(self, case_metadata):
        """Test that problem has no placeholder text."""
        placeholders = ["TODO", "TBD", "XXX", "FIXME", "PLACEHOLDER"]
        problem_upper = case_metadata["problem"].upper()
        for placeholder in placeholders:
            assert (
                placeholder not in problem_upper
            ), f"Problem contains placeholder: {placeholder}"

    def test_no_placeholder_text_in_solution(self, case_metadata):
        """Test that solution has no placeholder text (excluding TodoWrite)."""
        placeholders = ["TBD", "XXX", "FIXME", "PLACEHOLDER"]
        solution_upper = case_metadata["solution"].upper()
        for placeholder in placeholders:
            assert (
                placeholder not in solution_upper
            ), f"Solution contains placeholder: {placeholder}"

        # Check for TODO but exclude TodoWrite
        if "TODO" in solution_upper and "TODOWRITE" not in solution_upper:
            pytest.fail("Solution contains placeholder: TODO")

    def test_case_structure_matches_schema(self, completion_case):
        """Test that the case structure matches expected schema."""
        required_keys = ["category", "subcategory", "tags", "problem", "solution"]
        for key in required_keys:
            assert key in completion_case, f"Case missing required key: {key}"

    def test_all_metadata_fields_non_empty(self, case_metadata):
        """Test that all metadata fields have non-empty values."""
        for key in ["category", "subcategory", "problem", "solution"]:
            assert (
                case_metadata[key].strip() != ""
            ), f"Metadata field '{key}' must not be empty"
        assert len(case_metadata["tags"]) > 0, "Tags list must not be empty"
