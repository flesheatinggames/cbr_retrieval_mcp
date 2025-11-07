"""
Comprehensive unit tests for bootstrap_ui_cases.py module.

This test suite validates the structure, content, and metadata of Bootstrap UI
cases following TDD best practices. Tests ensure the modular case file meets all
specifications for the case-base-modular-refactoring project.

Test Coverage:
- File existence and import validation
- BOOTSTRAP_UI_CASES variable structure
- Case count validation (exactly 4 cases)
- Required field presence for all cases
- Field type validation
- Field content validation (non-empty, correct values)
- Bootstrap UI topic coverage
- Tag keyword validation
"""

from pathlib import Path
from typing import Any, Dict, List

import pytest


# Test Group 1: File and Module Structure
class TestFileAndModuleStructure:
    """Test suite for validating file existence and module import."""

    def test_bootstrap_ui_cases_file_exists(self):
        """Verify that cases/bootstrap/bootstrap_ui_cases.py file exists."""
        file_path = Path("cases/bootstrap/bootstrap_ui_cases.py")
        assert file_path.exists(), f"Expected file not found: {file_path}"
        assert file_path.is_file(), f"Expected path to be a file: {file_path}"
        assert file_path.suffix == ".py", f"Expected .py extension: {file_path}"

    def test_bootstrap_ui_cases_module_importable(self):
        """Verify that bootstrap_ui_cases module can be imported without errors."""
        try:
            from cases.bootstrap import bootstrap_ui_cases

            assert bootstrap_ui_cases is not None
        except ImportError as e:
            pytest.fail(f"Failed to import bootstrap_ui_cases module: {e}")

    def test_bootstrap_ui_cases_variable_exists(self):
        """Verify that BOOTSTRAP_UI_CASES variable exists in the module."""
        from cases.bootstrap import bootstrap_ui_cases

        assert hasattr(
            bootstrap_ui_cases, "BOOTSTRAP_UI_CASES"
        ), "Module must define BOOTSTRAP_UI_CASES variable"

    def test_bootstrap_ui_cases_is_list(self):
        """Verify that BOOTSTRAP_UI_CASES is a list."""
        from cases.bootstrap.bootstrap_ui_cases import BOOTSTRAP_UI_CASES

        assert isinstance(
            BOOTSTRAP_UI_CASES, list
        ), f"BOOTSTRAP_UI_CASES must be a list, got {type(BOOTSTRAP_UI_CASES)}"


# Test Group 2: Case Count Validation
class TestCaseCount:
    """Test suite for validating the number of Bootstrap UI cases."""

    def test_bootstrap_ui_cases_count(self):
        """Verify that BOOTSTRAP_UI_CASES contains exactly 4 cases."""
        from cases.bootstrap.bootstrap_ui_cases import BOOTSTRAP_UI_CASES

        assert (
            len(BOOTSTRAP_UI_CASES) == 4
        ), f"Expected exactly 4 cases, got {len(BOOTSTRAP_UI_CASES)}"

    def test_all_cases_are_dicts(self):
        """Verify that all cases in the list are dictionaries."""
        from cases.bootstrap.bootstrap_ui_cases import BOOTSTRAP_UI_CASES

        for idx, case in enumerate(BOOTSTRAP_UI_CASES):
            assert isinstance(
                case, dict
            ), f"Case {idx} must be a dictionary, got {type(case)}"


# Test Group 3: Required Fields Presence
class TestRequiredFieldsPresence:
    """Test suite for validating presence of all required fields in every case."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing BOOTSTRAP_UI_CASES for tests."""
        from cases.bootstrap.bootstrap_ui_cases import BOOTSTRAP_UI_CASES

        return BOOTSTRAP_UI_CASES

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


# Test Group 4: Field Type Validation
class TestFieldTypes:
    """Test suite for validating data types of all fields."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing BOOTSTRAP_UI_CASES for tests."""
        from cases.bootstrap.bootstrap_ui_cases import BOOTSTRAP_UI_CASES

        return BOOTSTRAP_UI_CASES

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

    def test_all_tags_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all elements in 'tags' lists are strings."""
        for case_idx, case in enumerate(cases):
            tags = case.get("tags", [])
            for tag_idx, tag in enumerate(tags):
                assert isinstance(
                    tag, str
                ), f"Case {case_idx} tag {tag_idx} must be str, got {type(tag)}"


# Test Group 5: Field Content Validation
class TestFieldContent:
    """Test suite for validating content and values of all fields."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing BOOTSTRAP_UI_CASES for tests."""
        from cases.bootstrap.bootstrap_ui_cases import BOOTSTRAP_UI_CASES

        return BOOTSTRAP_UI_CASES

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

    def test_category_equals_bootstrap(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have category='bootstrap'."""
        for idx, case in enumerate(cases):
            assert (
                case.get("category") == "bootstrap"
            ), f'Case {idx} category must be "bootstrap", got "{case.get("category")}"'

    def test_subcategory_equals_ui(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have subcategory='ui'."""
        for idx, case in enumerate(cases):
            assert (
                case.get("subcategory") == "ui"
            ), f'Case {idx} subcategory must be "ui", got "{case.get("subcategory")}"'

    def test_tags_non_empty_lists(self, cases: List[Dict[str, Any]]):
        """Verify that all 'tags' fields are non-empty lists."""
        for idx, case in enumerate(cases):
            tags = case.get("tags", [])
            assert len(tags) > 0, f"Case {idx} tags list must not be empty"


# Test Group 6: Bootstrap UI Topic Coverage
class TestBootstrapUITopicCoverage:
    """Test suite for validating coverage of key Bootstrap UI topics."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing BOOTSTRAP_UI_CASES for tests."""
        from cases.bootstrap.bootstrap_ui_cases import BOOTSTRAP_UI_CASES

        return BOOTSTRAP_UI_CASES

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

    def test_navbar_component_covered(self, cases: List[Dict[str, Any]]):
        """Verify that navbar/navigation component topic is covered in at least one case."""
        keywords = ["navbar", "navigation", "nav bar", "nav", "navigation bar"]
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert (
            found
        ), f"No case found covering navbar/navigation component topic. Keywords: {keywords}"

    def test_modal_component_covered(self, cases: List[Dict[str, Any]]):
        """Verify that modal/dialog component topic is covered in at least one case."""
        keywords = ["modal", "dialog", "popup", "overlay", "confirmation"]
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert (
            found
        ), f"No case found covering modal/dialog component topic. Keywords: {keywords}"

    def test_form_validation_covered(self, cases: List[Dict[str, Any]]):
        """Verify that form validation component topic is covered in at least one case."""
        keywords = ["form", "validation", "validated", "feedback", "form validation"]
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert (
            found
        ), f"No case found covering form validation component topic. Keywords: {keywords}"

    def test_grid_layout_covered(self, cases: List[Dict[str, Any]]):
        """Verify that grid/card layout component topic is covered in at least one case."""
        keywords = [
            "grid",
            "card",
            "row",
            "col",
            "responsive",
            "layout",
            "display data",
        ]
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert (
            found
        ), f"No case found covering grid/card layout component topic. Keywords: {keywords}"


# Test Group 7: Bootstrap Keyword Validation
class TestBootstrapKeywords:
    """Test suite for validating presence of Bootstrap keywords in tags."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing BOOTSTRAP_UI_CASES for tests."""
        from cases.bootstrap.bootstrap_ui_cases import BOOTSTRAP_UI_CASES

        return BOOTSTRAP_UI_CASES

    def test_tags_contain_bootstrap_keywords(self, cases: List[Dict[str, Any]]):
        """Verify that tags across all cases contain Bootstrap-specific keywords."""
        bootstrap_keywords = [
            "bootstrap",
            "react-bootstrap",
            "navbar",
            "modal",
            "form",
            "card",
            "grid",
            "button",
            "row",
            "col",
            "container",
            "validation",
            "feedback",
            "responsive",
            "layout",
            "ui",
            "component",
        ]

        all_tags_lower = []
        for case in cases:
            all_tags_lower.extend([tag.lower() for tag in case.get("tags", [])])

        found_keywords = []
        for keyword in bootstrap_keywords:
            if any(keyword in tag for tag in all_tags_lower):
                found_keywords.append(keyword)

        assert (
            len(found_keywords) > 0
        ), f"Tags must contain Bootstrap keywords. Expected any of: {bootstrap_keywords}"


# Test Group 8: Dynamic Loader Integration
class TestDynamicLoaderIntegration:
    """Tests for dynamic loader integration."""

    def test_module_importable_via_cases_package(self):
        """Test that the module can be imported via cases.bootstrap.bootstrap_ui_cases."""
        try:
            from cases.bootstrap import bootstrap_ui_cases

            assert hasattr(
                bootstrap_ui_cases, "BOOTSTRAP_UI_CASES"
            ), "Module must be importable and define BOOTSTRAP_UI_CASES"
        except ImportError as e:
            pytest.fail(f"Failed to import via cases.bootstrap package: {e}")

    def test_dynamic_loader_can_discover_module(self):
        """Test that the dynamic loader can discover this module."""
        import importlib
        import pkgutil

        # Check that cases.bootstrap package exists
        try:
            import cases.bootstrap
        except ImportError:
            pytest.fail("cases.bootstrap package does not exist")

        # Check that bootstrap_ui_cases is discoverable in the package
        module_found = False
        for importer, modname, ispkg in pkgutil.iter_modules(
            cases.bootstrap.__path__, prefix="cases.bootstrap."
        ):
            if modname == "cases.bootstrap.bootstrap_ui_cases":
                module_found = True
                break

        assert (
            module_found
        ), "bootstrap_ui_cases module not discoverable by dynamic loader"


# Test Group 9: Case Content Validation
class TestCaseContentMatching:
    """Test suite for validating case content matches original case_base.py."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing BOOTSTRAP_UI_CASES for tests."""
        from cases.bootstrap.bootstrap_ui_cases import BOOTSTRAP_UI_CASES

        return BOOTSTRAP_UI_CASES

    def test_case_content_matches_original(self, cases: List[Dict[str, Any]]):
        """Verify problem statements match the 4 identified Bootstrap UI cases."""
        expected_problems = [
            "\nA responsive navigation bar in a React component using react-bootstrap.\n",
            "\nA React component that displays a Bootstrap modal dialog.\n",
            "\nA Bootstrap-styled form with validation feedback in React.\n",
            "\nA React component that displays data in a responsive Bootstrap grid.\n",
        ]

        actual_problems = [case.get("problem", "") for case in cases]

        for expected in expected_problems:
            assert (
                expected in actual_problems
            ), f'Expected problem statement not found: "{expected}"'

    def test_solution_content_bootstrap_imports(self, cases: List[Dict[str, Any]]):
        """Verify solutions contain Bootstrap-specific imports."""
        bootstrap_import_patterns = [
            "from 'react-bootstrap'",
            "react-bootstrap",
            "Navbar",
            "Modal",
            "Form",
            "Card",
            "Container",
            "Row",
            "Col",
            "Button",
        ]

        for idx, case in enumerate(cases):
            solution = case.get("solution", "")
            has_bootstrap_import = any(
                pattern in solution for pattern in bootstrap_import_patterns
            )
            assert (
                has_bootstrap_import
            ), f"Case {idx} solution does not contain Bootstrap imports"
