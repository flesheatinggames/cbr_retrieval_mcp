"""
Comprehensive unit tests for firebase_auth_cases.py module.

This test suite validates the structure, content, and metadata of Firebase Authentication
cases following TDD best practices. Tests ensure the modular case file meets all
specifications for the case-base-modular-refactoring project.

Test Coverage:
- File existence and import validation
- FIREBASE_AUTH_CASES variable structure
- Case count validation (exactly 5 cases)
- Required field presence for all cases
- Field type validation
- Field content validation (non-empty, correct values)
- Firebase Auth topic coverage
- Tag keyword validation
"""

from pathlib import Path
from typing import Any, Dict, List

import pytest


# Test Group 1: File and Module Structure
class TestFileAndModuleStructure:
    """Test suite for validating file existence and module import."""

    def test_firebase_auth_cases_file_exists(self):
        """Verify that cases/firebase/firebase_auth_cases.py file exists."""
        file_path = Path("cases/firebase/firebase_auth_cases.py")
        assert file_path.exists(), f"Expected file not found: {file_path}"
        assert file_path.is_file(), f"Expected path to be a file: {file_path}"
        assert file_path.suffix == ".py", f"Expected .py extension: {file_path}"

    def test_firebase_auth_cases_module_importable(self):
        """Verify that firebase_auth_cases module can be imported without errors."""
        try:
            from cases.firebase import firebase_auth_cases

            assert firebase_auth_cases is not None
        except ImportError as e:
            pytest.fail(f"Failed to import firebase_auth_cases module: {e}")


# Test Group 2: FIREBASE_AUTH_CASES Variable Structure
class TestFirebaseAuthCasesVariable:
    """Test suite for validating FIREBASE_AUTH_CASES variable structure."""

    def test_firebase_auth_cases_variable_exists(self):
        """Verify that FIREBASE_AUTH_CASES variable exists in the module."""
        from cases.firebase import firebase_auth_cases

        assert hasattr(
            firebase_auth_cases, "FIREBASE_AUTH_CASES"
        ), "Module must define FIREBASE_AUTH_CASES variable"

    def test_firebase_auth_cases_is_list(self):
        """Verify that FIREBASE_AUTH_CASES is a list."""
        from cases.firebase.firebase_auth_cases import FIREBASE_AUTH_CASES

        assert isinstance(
            FIREBASE_AUTH_CASES, list
        ), f"FIREBASE_AUTH_CASES must be a list, got {type(FIREBASE_AUTH_CASES)}"


# Test Group 3: Case Count Validation
class TestCaseCount:
    """Test suite for validating the number of Firebase Auth cases."""

    def test_firebase_auth_cases_count(self):
        """Verify that FIREBASE_AUTH_CASES contains exactly 5 cases."""
        from cases.firebase.firebase_auth_cases import FIREBASE_AUTH_CASES

        assert (
            len(FIREBASE_AUTH_CASES) == 5
        ), f"Expected exactly 5 cases, got {len(FIREBASE_AUTH_CASES)}"


# Test Group 4: Required Fields Presence
class TestRequiredFieldsPresence:
    """Test suite for validating presence of all required fields in every case."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing FIREBASE_AUTH_CASES for tests."""
        from cases.firebase.firebase_auth_cases import FIREBASE_AUTH_CASES

        return FIREBASE_AUTH_CASES

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
        """Fixture providing FIREBASE_AUTH_CASES for tests."""
        from cases.firebase.firebase_auth_cases import FIREBASE_AUTH_CASES

        return FIREBASE_AUTH_CASES

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
        """Fixture providing FIREBASE_AUTH_CASES for tests."""
        from cases.firebase.firebase_auth_cases import FIREBASE_AUTH_CASES

        return FIREBASE_AUTH_CASES

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

    def test_category_equals_firebase(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have category='firebase'."""
        for idx, case in enumerate(cases):
            assert (
                case.get("category") == "firebase"
            ), f'Case {idx} category must be "firebase", got "{case.get("category")}"'

    def test_subcategory_equals_auth(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have subcategory='auth'."""
        for idx, case in enumerate(cases):
            assert (
                case.get("subcategory") == "auth"
            ), f'Case {idx} subcategory must be "auth", got "{case.get("subcategory")}"'

    def test_tags_non_empty_lists(self, cases: List[Dict[str, Any]]):
        """Verify that all 'tags' fields are non-empty lists."""
        for idx, case in enumerate(cases):
            tags = case.get("tags", [])
            assert len(tags) > 0, f"Case {idx} tags list must not be empty"

    def test_all_tags_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all elements in 'tags' lists are strings."""
        for case_idx, case in enumerate(cases):
            tags = case.get("tags", [])
            for tag_idx, tag in enumerate(tags):
                assert isinstance(
                    tag, str
                ), f"Case {case_idx} tag {tag_idx} must be str, got {type(tag)}"


# Test Group 7: Firebase Auth Topic Coverage
class TestFirebaseAuthTopicCoverage:
    """Test suite for validating coverage of key Firebase Auth topics."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing FIREBASE_AUTH_CASES for tests."""
        from cases.firebase.firebase_auth_cases import FIREBASE_AUTH_CASES

        return FIREBASE_AUTH_CASES

    def _search_in_case(self, case: Dict[str, Any], keywords: List[str]) -> bool:
        """
        Helper method to search for keywords in case problem field and tags.

        Args:
            case: The case dictionary to search
            keywords: List of keywords to search for (case-insensitive)

        Returns:
            True if any keyword is found in problem or tags, False otherwise
        """
        problem_lower = case.get("problem", "").lower()
        tags_lower = [tag.lower() for tag in case.get("tags", [])]

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in problem_lower:
                return True
            if any(keyword_lower in tag for tag in tags_lower):
                return True

        return False

    def test_sign_up_topic_covered(self, cases: List[Dict[str, Any]]):
        """Verify that sign-up/registration topic is covered in at least one case."""
        keywords = ["sign-up", "signup", "sign up", "registration", "register"]
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert (
            found
        ), f"No case found covering sign-up/registration topic. Keywords: {keywords}"

    def test_sign_in_topic_covered(self, cases: List[Dict[str, Any]]):
        """Verify that sign-in/login topic is covered in at least one case."""
        keywords = ["sign-in", "signin", "sign in", "login", "log in"]
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert (
            found
        ), f"No case found covering sign-in/login topic. Keywords: {keywords}"

    def test_sign_out_topic_covered(self, cases: List[Dict[str, Any]]):
        """Verify that sign-out topic is covered in at least one case."""
        keywords = ["sign-out", "signout", "sign out", "logout", "log out"]
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert found, f"No case found covering sign-out topic. Keywords: {keywords}"

    def test_session_management_topic_covered(self, cases: List[Dict[str, Any]]):
        """Verify that session management topic is covered in at least one case."""
        keywords = ["session", "jwt", "token", "refresh-token", "auth-state"]
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert (
            found
        ), f"No case found covering session management topic. Keywords: {keywords}"


# Test Group 8: Firebase/Auth Keyword Validation
class TestFirebaseAuthKeywords:
    """Test suite for validating presence of Firebase and authentication keywords in tags."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing FIREBASE_AUTH_CASES for tests."""
        from cases.firebase.firebase_auth_cases import FIREBASE_AUTH_CASES

        return FIREBASE_AUTH_CASES

    def test_tags_contain_firebase_keywords(self, cases: List[Dict[str, Any]]):
        """Verify that tags across all cases contain Firebase/auth related keywords."""
        firebase_auth_keywords = [
            "firebase",
            "auth",
            "authentication",
            "authorization",
            "user",
            "login",
            "signup",
            "password",
            "security",
            "identity",
            "credential",
            "token",
            "session",
        ]

        all_tags_lower = []
        for case in cases:
            all_tags_lower.extend([tag.lower() for tag in case.get("tags", [])])

        found_keywords = []
        for keyword in firebase_auth_keywords:
            if any(keyword in tag for tag in all_tags_lower):
                found_keywords.append(keyword)

        assert (
            len(found_keywords) > 0
        ), f"Tags must contain Firebase/auth keywords. Expected any of: {firebase_auth_keywords}"
