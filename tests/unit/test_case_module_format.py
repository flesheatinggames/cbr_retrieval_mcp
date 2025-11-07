"""
Tests for case module file format validation.

This module contains tests that validate case module files follow the correct
naming pattern and export the required list constant with proper structure.
"""

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest


class TestCaseModuleFormat:
    """Test suite for case module format validation."""

    # Naming pattern: <technology>_<subtopic>_cases.py
    CASE_FILE_PATTERN = re.compile(r"^[a-z]+_[a-z]+_cases\.py$")

    # Export name pattern: <TECHNOLOGY>_<SUBTOPIC>_CASES
    CASE_LIST_PATTERN = re.compile(r"^[A-Z]+_[A-Z]+_CASES$")

    REQUIRED_CASE_FIELDS = {"problem", "solution", "category", "subcategory", "tags"}

    @pytest.fixture
    def valid_case_module_content(self) -> str:
        """Fixture providing valid case module content."""
        return """
FIREBASE_AUTH_CASES = [
    {
        "problem": "User authentication with Firebase",
        "solution": "Use Firebase Auth SDK",
        "category": "firebase",
        "subcategory": "auth",
        "tags": "firebase,authentication"
    }
]
"""

    @pytest.fixture
    def invalid_naming_cases(self) -> List[str]:
        """Fixture providing invalid case file names."""
        return [
            "FirebaseAuth.py",  # CamelCase
            "firebase_cases.py",  # Missing subtopic (only one word)
            "firebase-auth-cases.py",  # Hyphens instead of underscores
            "firebase_auth.py",  # Missing _cases suffix
            "FIREBASE_AUTH_CASES.py",  # Uppercase
            "firebase.py",  # No subtopic, no _cases
        ]

    @pytest.fixture
    def valid_naming_cases(self) -> List[str]:
        """Fixture providing valid case file names."""
        return [
            "firebase_auth_cases.py",
            "react_components_cases.py",
            "nextjs_routing_cases.py",
            "python_testing_cases.py",
        ]

    def test_case_file_naming_pattern(
        self, valid_naming_cases: List[str], invalid_naming_cases: List[str]
    ):
        """
        Test that case files follow the <technology>_<subtopic>_cases.py naming pattern.

        Valid examples:
        - firebase_auth_cases.py
        - react_components_cases.py

        Invalid examples:
        - FirebaseAuth.py (CamelCase)
        - firebase_cases.py (missing subtopic - only one word)
        - firebase-auth-cases.py (hyphens instead of underscores)
        """
        # Test valid names
        for valid_name in valid_naming_cases:
            assert self.CASE_FILE_PATTERN.match(
                valid_name
            ), f"Valid name '{valid_name}' should match pattern"

        # Test invalid names
        for invalid_name in invalid_naming_cases:
            assert not self.CASE_FILE_PATTERN.match(
                invalid_name
            ), f"Invalid name '{invalid_name}' should not match pattern"

    def test_case_file_exports_list(
        self, tmp_path: Path, valid_case_module_content: str
    ):
        """
        Test that case module files export a list constant.

        The module should export a list, not None, dict, tuple, or other types.
        """
        # Create a valid case module file
        module_file = tmp_path / "firebase_auth_cases.py"
        module_file.write_text(valid_case_module_content)

        # Dynamically import the module
        spec = importlib.util.spec_from_file_location(
            "firebase_auth_cases", module_file
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules["firebase_auth_cases"] = module
        spec.loader.exec_module(module)

        # Verify the module exports a list
        assert hasattr(
            module, "FIREBASE_AUTH_CASES"
        ), "Module should export FIREBASE_AUTH_CASES"
        assert isinstance(
            module.FIREBASE_AUTH_CASES, list
        ), "Exported constant should be a list"

        # Cleanup
        del sys.modules["firebase_auth_cases"]

    def test_case_file_exports_wrong_type(self, tmp_path: Path):
        """
        Test that case module fails validation when exporting non-list types.
        """
        # Test with dict export
        dict_content = """
FIREBASE_AUTH_CASES = {
    "problem": "test"
}
"""
        module_file = tmp_path / "firebase_auth_cases_dict.py"
        module_file.write_text(dict_content)

        spec = importlib.util.spec_from_file_location(
            "firebase_auth_cases_dict", module_file
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules["firebase_auth_cases_dict"] = module
        spec.loader.exec_module(module)

        # Should have the export but it's not a list
        assert hasattr(module, "FIREBASE_AUTH_CASES")
        assert not isinstance(
            module.FIREBASE_AUTH_CASES, list
        ), "Should detect non-list export"

        # Cleanup
        del sys.modules["firebase_auth_cases_dict"]

    @pytest.mark.parametrize(
        "export_name,should_match",
        [
            ("FIREBASE_AUTH_CASES", True),
            ("REACT_COMPONENTS_CASES", True),
            ("NEXTJS_ROUTING_CASES", True),
            ("firebase_auth_cases", False),  # Lowercase
            ("FIREBASE_CASES", False),  # Missing subtopic (only one word)
            ("FIREBASE_AUTH", False),  # Missing _CASES suffix
            ("Firebase_Auth_Cases", False),  # Mixed case
            ("FIREBASE", False),  # Only one word
        ],
    )
    def test_case_list_naming_convention(self, export_name: str, should_match: bool):
        """
        Test that exported list constant follows <TECHNOLOGY>_<SUBTOPIC>_CASES uppercase pattern.

        Valid examples:
        - FIREBASE_AUTH_CASES
        - REACT_COMPONENTS_CASES

        Invalid examples:
        - firebase_auth_cases (lowercase)
        - FIREBASE_CASES (missing subtopic - only one word)
        - FIREBASE_AUTH (missing _CASES suffix)
        """
        matches = bool(self.CASE_LIST_PATTERN.match(export_name))
        assert (
            matches == should_match
        ), f"Export name '{export_name}' match result should be {should_match}"

    def test_case_list_contains_dicts(self, tmp_path: Path):
        """
        Test that the exported list contains dictionary items.

        Should validate:
        - All items are dictionaries
        - Empty lists pass (no items to validate)
        - Lists with non-dict items fail
        """
        # Test with valid dict items
        valid_content = """
FIREBASE_AUTH_CASES = [
    {"problem": "test1", "solution": "test1"},
    {"problem": "test2", "solution": "test2"}
]
"""
        module_file = tmp_path / "valid_dicts.py"
        module_file.write_text(valid_content)

        spec = importlib.util.spec_from_file_location("valid_dicts", module_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules["valid_dicts"] = module
        spec.loader.exec_module(module)

        cases = module.FIREBASE_AUTH_CASES
        assert all(
            isinstance(case, dict) for case in cases
        ), "All items in case list should be dictionaries"

        # Cleanup
        del sys.modules["valid_dicts"]

        # Test with invalid string items
        invalid_content = """
FIREBASE_AUTH_CASES = [
    "not a dict",
    "another string"
]
"""
        module_file = tmp_path / "invalid_strings.py"
        module_file.write_text(invalid_content)

        spec = importlib.util.spec_from_file_location("invalid_strings", module_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules["invalid_strings"] = module
        spec.loader.exec_module(module)

        cases = module.FIREBASE_AUTH_CASES
        assert not all(
            isinstance(case, dict) for case in cases
        ), "Should detect non-dict items in case list"

        # Cleanup
        del sys.modules["invalid_strings"]

    def test_case_list_empty_is_valid(self, tmp_path: Path):
        """Test that an empty case list is considered valid."""
        empty_content = """
FIREBASE_AUTH_CASES = []
"""
        module_file = tmp_path / "empty_cases.py"
        module_file.write_text(empty_content)

        spec = importlib.util.spec_from_file_location("empty_cases", module_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules["empty_cases"] = module
        spec.loader.exec_module(module)

        cases = module.FIREBASE_AUTH_CASES
        assert isinstance(cases, list)
        assert len(cases) == 0
        # Empty list passes dict validation (no items to check)
        assert all(isinstance(case, dict) for case in cases)

        # Cleanup
        del sys.modules["empty_cases"]

    @pytest.mark.parametrize(
        "missing_field",
        [
            "problem",
            "solution",
            "category",
            "subcategory",
            "tags",
        ],
    )
    def test_case_dict_has_required_fields(self, tmp_path: Path, missing_field: str):
        """
        Test that each case dictionary has all required fields.

        Required fields:
        - problem
        - solution
        - category
        - subcategory
        - tags
        """
        # Create a case with all required fields
        all_fields = {
            "problem": "test problem",
            "solution": "test solution",
            "category": "test_category",
            "subcategory": "test_subcategory",
            "tags": "test,tags",
        }

        # Test with all fields present
        assert self.REQUIRED_CASE_FIELDS.issubset(
            all_fields.keys()
        ), "Case with all required fields should pass validation"

        # Test with missing field
        incomplete_case = all_fields.copy()
        del incomplete_case[missing_field]

        assert not self.REQUIRED_CASE_FIELDS.issubset(
            incomplete_case.keys()
        ), f"Case missing '{missing_field}' should fail validation"

    def test_case_dict_allows_extra_fields(self):
        """Test that case dictionaries can have additional fields beyond required ones."""
        case_with_extras = {
            "problem": "test problem",
            "solution": "test solution",
            "category": "test_category",
            "subcategory": "test_subcategory",
            "tags": "test,tags",
            "author": "test author",  # Extra field
            "created_at": "2025-10-28",  # Extra field
        }

        # Should pass validation even with extra fields
        assert self.REQUIRED_CASE_FIELDS.issubset(
            case_with_extras.keys()
        ), "Case with extra fields should still pass validation"

    def test_case_dict_empty_strings_are_valid(self):
        """Test that empty strings in required fields still pass validation."""
        case_with_empty_strings = {
            "problem": "",  # Empty but present
            "solution": "",
            "category": "",
            "subcategory": "",
            "tags": "",
        }

        # Field exists check should pass
        assert self.REQUIRED_CASE_FIELDS.issubset(
            case_with_empty_strings.keys()
        ), "Case with empty string values should pass field existence check"

    def test_complete_module_validation(self, tmp_path: Path):
        """
        Integration test: Validate a complete case module file.

        This test combines all validation rules:
        1. File naming pattern
        2. Exports a list
        3. List name follows convention
        4. List contains dicts
        5. Dicts have required fields
        """
        # Create a complete valid module
        module_content = """
FIREBASE_AUTH_CASES = [
    {
        "problem": "Implement user authentication with Firebase",
        "solution": "Use Firebase Auth SDK with email/password",
        "category": "firebase",
        "subcategory": "auth",
        "tags": "firebase,authentication,security"
    },
    {
        "problem": "Handle Firebase auth state changes",
        "solution": "Use onAuthStateChanged listener",
        "category": "firebase",
        "subcategory": "auth",
        "tags": "firebase,authentication,state"
    }
]
"""
        module_file = tmp_path / "firebase_auth_cases.py"
        module_file.write_text(module_content)

        # 1. Validate filename
        assert self.CASE_FILE_PATTERN.match(
            module_file.name
        ), "Filename should match pattern"

        # 2. Import and validate export
        spec = importlib.util.spec_from_file_location("complete_test", module_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules["complete_test"] = module
        spec.loader.exec_module(module)

        # 3. Validate export name
        assert hasattr(module, "FIREBASE_AUTH_CASES")
        assert self.CASE_LIST_PATTERN.match("FIREBASE_AUTH_CASES")

        # 4. Validate it's a list
        cases = module.FIREBASE_AUTH_CASES
        assert isinstance(cases, list)

        # 5. Validate list contains dicts
        assert all(isinstance(case, dict) for case in cases)

        # 6. Validate all dicts have required fields
        for case in cases:
            assert self.REQUIRED_CASE_FIELDS.issubset(
                case.keys()
            ), f"Case missing required fields. Has: {case.keys()}"

        # Cleanup
        del sys.modules["complete_test"]

    def test_existing_case_files_have_required_metadata(self):
        """
        Test that validates migrated case files have all required metadata fields.

        This test confirms that case files have been successfully migrated to include
        category, subcategory, and tags fields in addition to problem and solution.
        """
        # Add project root to path for imports
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        # Import an actual existing case file
        from cases.rust import rust_actix_cases

        # Verify the module has the expected export
        assert hasattr(rust_actix_cases, "RUST_ACTIX_CASES")
        cases = rust_actix_cases.RUST_ACTIX_CASES

        # Verify it's a list of dicts
        assert isinstance(cases, list)
        assert all(isinstance(case, dict) for case in cases)

        # All cases should now have the required fields after migration
        for case in cases:
            missing_fields = self.REQUIRED_CASE_FIELDS - set(case.keys())
            assert len(missing_fields) == 0, (
                f"Case should have all required fields after migration. "
                f"Missing: {missing_fields}, Has: {case.keys()}"
            )

            # Verify all required fields are present
            assert self.REQUIRED_CASE_FIELDS.issubset(
                case.keys()
            ), f"Case missing required fields: {missing_fields}"
