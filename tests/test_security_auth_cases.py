"""
Comprehensive unit tests for security_auth_cases.py module.

This test suite validates the structure, content, and metadata of Security Authentication
cases following TDD best practices. Tests ensure the modular case file meets all
specifications for the case-base-modular-refactoring project.

Test Coverage:
- File existence and import validation
- SECURITY_AUTH_CASES variable structure
- Case count validation (exactly 2 cases)
- Required field presence for all cases
- Field type validation
- Field content validation (non-empty, correct values)
- Metadata validation (category, subcategory, tags)
"""

from pathlib import Path
from typing import Any, Dict, List

import pytest


# Test Group 1: File and Module Structure
class TestFileAndModuleStructure:
    """Test suite for validating file existence and module import."""

    def test_security_auth_cases_file_exists(self):
        """Verify that cases/security/security_auth_cases.py file exists."""
        file_path = Path("cases/security/security_auth_cases.py")
        assert file_path.exists(), f"Expected file not found: {file_path}"
        assert file_path.is_file(), f"Expected path to be a file: {file_path}"
        assert file_path.suffix == ".py", f"Expected .py extension: {file_path}"

    def test_security_auth_cases_module_importable(self):
        """Verify that security_auth_cases module can be imported without errors."""
        try:
            from cases.security import security_auth_cases

            assert security_auth_cases is not None
        except ImportError as e:
            pytest.fail(f"Failed to import security_auth_cases module: {e}")


# Test Group 2: SECURITY_AUTH_CASES Variable Structure
class TestSecurityAuthCasesVariable:
    """Test suite for validating SECURITY_AUTH_CASES variable structure."""

    def test_security_auth_cases_variable_exists(self):
        """Verify that SECURITY_AUTH_CASES variable exists in the module."""
        from cases.security import security_auth_cases

        assert hasattr(
            security_auth_cases, "SECURITY_AUTH_CASES"
        ), "Module must define SECURITY_AUTH_CASES variable"

    def test_security_auth_cases_is_list(self):
        """Verify that SECURITY_AUTH_CASES is a list."""
        from cases.security.security_auth_cases import SECURITY_AUTH_CASES

        assert isinstance(
            SECURITY_AUTH_CASES, list
        ), f"SECURITY_AUTH_CASES must be a list, got {type(SECURITY_AUTH_CASES)}"


# Test Group 3: Case Count Validation
class TestCaseCount:
    """Test suite for validating the number of Security Auth cases."""

    def test_security_auth_cases_count(self):
        """Verify that SECURITY_AUTH_CASES contains exactly 2 cases."""
        from cases.security.security_auth_cases import SECURITY_AUTH_CASES

        assert (
            len(SECURITY_AUTH_CASES) == 2
        ), f"Expected exactly 2 cases, got {len(SECURITY_AUTH_CASES)}"


# Test Group 4: Required Fields Presence
class TestRequiredFieldsPresence:
    """Test suite for validating presence of all required fields in every case."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing SECURITY_AUTH_CASES for tests."""
        from cases.security.security_auth_cases import SECURITY_AUTH_CASES

        return SECURITY_AUTH_CASES

    def test_all_cases_have_problem_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'problem' field."""
        for idx, case in enumerate(cases):
            assert "problem" in case, f"Case {idx} missing required field: problem"

    def test_all_cases_have_solution_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'solution' field."""
        for idx, case in enumerate(cases):
            assert "solution" in case, f"Case {idx} missing required field: solution"

    def test_all_cases_have_category_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'category' field."""
        for idx, case in enumerate(cases):
            assert "category" in case, f"Case {idx} missing required field: category"

    def test_all_cases_have_subcategory_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'subcategory' field."""
        for idx, case in enumerate(cases):
            assert (
                "subcategory" in case
            ), f"Case {idx} missing required field: subcategory"

    def test_all_cases_have_tags_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'tags' field."""
        for idx, case in enumerate(cases):
            assert "tags" in case, f"Case {idx} missing required field: tags"


# Test Group 5: Field Type Validation
class TestFieldTypes:
    """Test suite for validating data types of all fields."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing SECURITY_AUTH_CASES for tests."""
        from cases.security.security_auth_cases import SECURITY_AUTH_CASES

        return SECURITY_AUTH_CASES

    def test_problem_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'problem' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(
                case.get("problem"), str
            ), f'Case {idx} problem field must be str, got {type(case.get("problem"))}'

    def test_solution_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'solution' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(
                case.get("solution"), str
            ), f'Case {idx} solution field must be str, got {type(case.get("solution"))}'

    def test_category_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'category' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(
                case.get("category"), str
            ), f'Case {idx} category field must be str, got {type(case.get("category"))}'

    def test_subcategory_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'subcategory' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(
                case.get("subcategory"), str
            ), f'Case {idx} subcategory field must be str, got {type(case.get("subcategory"))}'

    def test_tags_fields_are_lists(self, cases: List[Dict[str, Any]]):
        """Verify that all 'tags' fields are lists."""
        for idx, case in enumerate(cases):
            assert isinstance(
                case.get("tags"), list
            ), f'Case {idx} tags field must be list, got {type(case.get("tags"))}'


# Test Group 6: Field Content Validation
class TestFieldContent:
    """Test suite for validating content and values of all fields."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing SECURITY_AUTH_CASES for tests."""
        from cases.security.security_auth_cases import SECURITY_AUTH_CASES

        return SECURITY_AUTH_CASES

    def test_problem_fields_non_empty(self, cases: List[Dict[str, Any]]):
        """Verify that all 'problem' fields are non-empty strings."""
        for idx, case in enumerate(cases):
            problem = case.get("problem", "")
            assert len(problem) > 0, f"Case {idx} problem field must not be empty"
            assert (
                problem.strip() != ""
            ), f"Case {idx} problem field must not be only whitespace"

    def test_solution_fields_non_empty(self, cases: List[Dict[str, Any]]):
        """Verify that all 'solution' fields are non-empty strings."""
        for idx, case in enumerate(cases):
            solution = case.get("solution", "")
            assert len(solution) > 0, f"Case {idx} solution field must not be empty"
            assert (
                solution.strip() != ""
            ), f"Case {idx} solution field must not be only whitespace"

    def test_category_equals_security(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have category='security'."""
        for idx, case in enumerate(cases):
            assert (
                case.get("category") == "security"
            ), f'Case {idx} category must be "security", got "{case.get("category")}"'

    def test_subcategory_equals_auth(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have subcategory='auth'."""
        for idx, case in enumerate(cases):
            assert (
                case.get("subcategory") == "auth"
            ), f'Case {idx} subcategory must be "auth", got "{case.get("subcategory")}"'

    def test_tags_have_at_least_two_items(self, cases: List[Dict[str, Any]]):
        """Verify that all 'tags' fields have at least 2 items."""
        for idx, case in enumerate(cases):
            tags = case.get("tags", [])
            assert (
                len(tags) >= 2
            ), f"Case {idx} tags list must have at least 2 items, got {len(tags)}"

    def test_all_tags_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all elements in 'tags' lists are strings."""
        for case_idx, case in enumerate(cases):
            tags = case.get("tags", [])
            for tag_idx, tag in enumerate(tags):
                assert isinstance(
                    tag, str
                ), f"Case {case_idx} tag {tag_idx} must be str, got {type(tag)}"

    def test_all_tags_are_non_empty(self, cases: List[Dict[str, Any]]):
        """Verify that all tag strings are non-empty."""
        for case_idx, case in enumerate(cases):
            tags = case.get("tags", [])
            for tag_idx, tag in enumerate(tags):
                assert len(tag) > 0, f"Case {case_idx} tag {tag_idx} must not be empty"
                assert (
                    tag.strip() != ""
                ), f"Case {case_idx} tag {tag_idx} must not be only whitespace"


# Test Group 7: Metadata Completeness
class TestMetadataCompleteness:
    """Test suite for validating completeness of case metadata."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing SECURITY_AUTH_CASES for tests."""
        from cases.security.security_auth_cases import SECURITY_AUTH_CASES

        return SECURITY_AUTH_CASES

    def test_all_cases_have_complete_metadata(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have complete metadata (category, subcategory, tags)."""
        required_metadata_fields = ["category", "subcategory", "tags"]

        for idx, case in enumerate(cases):
            for field in required_metadata_fields:
                assert field in case, f"Case {idx} missing metadata field: {field}"
                assert (
                    case[field] is not None
                ), f"Case {idx} metadata field {field} must not be None"


# Test Group 8: Security Auth Keywords Validation
class TestSecurityAuthKeywords:
    """Test suite for validating presence of security and authentication keywords."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing SECURITY_AUTH_CASES for tests."""
        from cases.security.security_auth_cases import SECURITY_AUTH_CASES

        return SECURITY_AUTH_CASES

    def test_tags_contain_security_auth_keywords(self, cases: List[Dict[str, Any]]):
        """Verify that tags across all cases contain security/auth related keywords."""
        security_auth_keywords = [
            "security",
            "auth",
            "authentication",
            "authorization",
            "encryption",
            "password",
            "token",
            "jwt",
            "oauth",
            "access-control",
            "role",
            "permission",
            "credential",
        ]

        all_tags_lower = []
        for case in cases:
            all_tags_lower.extend([tag.lower() for tag in case.get("tags", [])])

        found_keywords = []
        for keyword in security_auth_keywords:
            if any(keyword in tag for tag in all_tags_lower):
                found_keywords.append(keyword)

        assert (
            len(found_keywords) > 0
        ), f"Tags must contain security/auth keywords. Expected any of: {security_auth_keywords}"
