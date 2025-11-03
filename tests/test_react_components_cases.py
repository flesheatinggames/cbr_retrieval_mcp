"""
Comprehensive unit tests for react_components_cases.py module.

This test suite validates the structure, content, and metadata of React Components
cases following TDD best practices. Tests ensure the modular case file meets all
specifications for the case-base-modular-refactoring project.

Test Coverage:
- File existence and import validation
- REACT_COMPONENTS_CASES variable structure
- Case count validation (exactly 6 cases)
- Required field presence for all cases
- Field type validation
- Field content validation (non-empty, correct values)
- React Component topic coverage
- Tag keyword validation
"""

import pytest
from pathlib import Path
from typing import Any, Dict, List


# Test Group 1: File and Module Structure
class TestFileAndModuleStructure:
    """Test suite for validating file existence and module import."""

    def test_react_components_cases_file_exists(self):
        """Verify that cases/react/react_components_cases.py file exists."""
        file_path = Path('cases/react/react_components_cases.py')
        assert file_path.exists(), f'Expected file not found: {file_path}'
        assert file_path.is_file(), f'Expected path to be a file: {file_path}'
        assert file_path.suffix == '.py', f'Expected .py extension: {file_path}'

    def test_react_components_cases_module_importable(self):
        """Verify that react_components_cases module can be imported without errors."""
        try:
            from cases.react import react_components_cases
            assert react_components_cases is not None
        except ImportError as e:
            pytest.fail(f'Failed to import react_components_cases module: {e}')

    def test_react_components_cases_variable_exists(self):
        """Verify that REACT_COMPONENTS_CASES variable exists in the module."""
        from cases.react import react_components_cases
        assert hasattr(react_components_cases, 'REACT_COMPONENTS_CASES'), \
            'Module must define REACT_COMPONENTS_CASES variable'

    def test_react_components_cases_is_list(self):
        """Verify that REACT_COMPONENTS_CASES is a list."""
        from cases.react.react_components_cases import REACT_COMPONENTS_CASES
        assert isinstance(REACT_COMPONENTS_CASES, list), \
            f'REACT_COMPONENTS_CASES must be a list, got {type(REACT_COMPONENTS_CASES)}'


# Test Group 2: Case Count Validation
class TestCaseCount:
    """Test suite for validating the number of React Components cases."""

    def test_react_components_cases_count(self):
        """Verify that REACT_COMPONENTS_CASES contains exactly 7 cases."""
        from cases.react.react_components_cases import REACT_COMPONENTS_CASES
        assert len(REACT_COMPONENTS_CASES) == 7, \
            f'Expected exactly 7 cases, got {len(REACT_COMPONENTS_CASES)}'

    def test_all_cases_are_dicts(self):
        """Verify that all cases in the list are dictionaries."""
        from cases.react.react_components_cases import REACT_COMPONENTS_CASES
        for idx, case in enumerate(REACT_COMPONENTS_CASES):
            assert isinstance(case, dict), \
                f'Case {idx} must be a dictionary, got {type(case)}'


# Test Group 3: Required Fields Presence
class TestRequiredFieldsPresence:
    """Test suite for validating presence of all required fields in every case."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing REACT_COMPONENTS_CASES for tests."""
        from cases.react.react_components_cases import REACT_COMPONENTS_CASES
        return REACT_COMPONENTS_CASES

    def test_all_cases_have_problem_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'problem' field."""
        for idx, case in enumerate(cases):
            assert 'problem' in case, \
                f'Case {idx} missing required field: problem'

    def test_all_cases_have_solution_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'solution' field."""
        for idx, case in enumerate(cases):
            assert 'solution' in case, \
                f'Case {idx} missing required field: solution'

    def test_all_cases_have_category_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'category' field."""
        for idx, case in enumerate(cases):
            assert 'category' in case, \
                f'Case {idx} missing required field: category'

    def test_all_cases_have_subcategory_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'subcategory' field."""
        for idx, case in enumerate(cases):
            assert 'subcategory' in case, \
                f'Case {idx} missing required field: subcategory'

    def test_all_cases_have_tags_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'tags' field."""
        for idx, case in enumerate(cases):
            assert 'tags' in case, \
                f'Case {idx} missing required field: tags'


# Test Group 4: Field Type Validation
class TestFieldTypes:
    """Test suite for validating data types of all fields."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing REACT_COMPONENTS_CASES for tests."""
        from cases.react.react_components_cases import REACT_COMPONENTS_CASES
        return REACT_COMPONENTS_CASES

    def test_problem_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'problem' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(case.get('problem'), str), \
                f'Case {idx} problem field must be str, got {type(case.get("problem"))}'

    def test_solution_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'solution' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(case.get('solution'), str), \
                f'Case {idx} solution field must be str, got {type(case.get("solution"))}'

    def test_category_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'category' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(case.get('category'), str), \
                f'Case {idx} category field must be str, got {type(case.get("category"))}'

    def test_subcategory_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'subcategory' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(case.get('subcategory'), str), \
                f'Case {idx} subcategory field must be str, got {type(case.get("subcategory"))}'

    def test_tags_fields_are_lists(self, cases: List[Dict[str, Any]]):
        """Verify that all 'tags' fields are lists."""
        for idx, case in enumerate(cases):
            assert isinstance(case.get('tags'), list), \
                f'Case {idx} tags field must be list, got {type(case.get("tags"))}'

    def test_all_tags_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all elements in 'tags' lists are strings."""
        for case_idx, case in enumerate(cases):
            tags = case.get('tags', [])
            for tag_idx, tag in enumerate(tags):
                assert isinstance(tag, str), \
                    f'Case {case_idx} tag {tag_idx} must be str, got {type(tag)}'


# Test Group 5: Field Content Validation
class TestFieldContent:
    """Test suite for validating content and values of all fields."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing REACT_COMPONENTS_CASES for tests."""
        from cases.react.react_components_cases import REACT_COMPONENTS_CASES
        return REACT_COMPONENTS_CASES

    def test_problem_fields_non_empty(self, cases: List[Dict[str, Any]]):
        """Verify that all 'problem' fields are non-empty strings."""
        for idx, case in enumerate(cases):
            problem = case.get('problem', '')
            assert len(problem) > 0, \
                f'Case {idx} problem field must not be empty'
            assert problem.strip() != '', \
                f'Case {idx} problem field must not be only whitespace'

    def test_solution_fields_non_empty(self, cases: List[Dict[str, Any]]):
        """Verify that all 'solution' fields are non-empty strings."""
        for idx, case in enumerate(cases):
            solution = case.get('solution', '')
            assert len(solution) > 0, \
                f'Case {idx} solution field must not be empty'
            assert solution.strip() != '', \
                f'Case {idx} solution field must not be only whitespace'

    def test_category_equals_react(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have category='react'."""
        for idx, case in enumerate(cases):
            assert case.get('category') == 'react', \
                f'Case {idx} category must be "react", got "{case.get("category")}"'

    def test_subcategory_equals_components(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have subcategory='components'."""
        for idx, case in enumerate(cases):
            assert case.get('subcategory') == 'components', \
                f'Case {idx} subcategory must be "components", got "{case.get("subcategory")}"'

    def test_tags_non_empty_lists(self, cases: List[Dict[str, Any]]):
        """Verify that all 'tags' fields are non-empty lists."""
        for idx, case in enumerate(cases):
            tags = case.get('tags', [])
            assert len(tags) > 0, \
                f'Case {idx} tags list must not be empty'


# Test Group 6: React Component Topic Coverage
class TestReactComponentTopicCoverage:
    """Test suite for validating coverage of key React Component topics."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing REACT_COMPONENTS_CASES for tests."""
        from cases.react.react_components_cases import REACT_COMPONENTS_CASES
        return REACT_COMPONENTS_CASES

    def _search_in_case(self, case: Dict[str, Any], keywords: List[str]) -> bool:
        """
        Helper method to search for keywords in case problem field and tags.

        Args:
            case: The case dictionary to search
            keywords: List of keywords to search for (case-insensitive)

        Returns:
            True if any keyword is found in problem or tags, False otherwise
        """
        problem_lower = case.get('problem', '').lower()
        tags_lower = [tag.lower() for tag in case.get('tags', [])]

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in problem_lower:
                return True
            if any(keyword_lower in tag for tag in tags_lower):
                return True

        return False

    def test_navigation_component_covered(self, cases: List[Dict[str, Any]]):
        """Verify that navigation/navbar component topic is covered in at least one case."""
        keywords = ['navigation', 'navbar', 'nav bar', 'menu', 'app bar']
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert found, \
            f'No case found covering navigation/navbar component topic. Keywords: {keywords}'

    def test_modal_component_covered(self, cases: List[Dict[str, Any]]):
        """Verify that modal/dialog component topic is covered in at least one case."""
        keywords = ['modal', 'dialog', 'popup', 'overlay']
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert found, \
            f'No case found covering modal/dialog component topic. Keywords: {keywords}'

    def test_grid_layout_component_covered(self, cases: List[Dict[str, Any]]):
        """Verify that grid/layout component topic is covered in at least one case."""
        keywords = ['grid', 'layout', 'row', 'col', 'card', 'display data', 'product grid']
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert found, \
            f'No case found covering grid/layout component topic. Keywords: {keywords}'

    def test_form_validation_component_covered(self, cases: List[Dict[str, Any]]):
        """Verify that form validation component topic is covered in at least one case."""
        keywords = ['form', 'validation', 'validated', 'input', 'feedback']
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert found, \
            f'No case found covering form validation component topic. Keywords: {keywords}'

    def test_data_display_component_covered(self, cases: List[Dict[str, Any]]):
        """Verify that data display/list component topic is covered in at least one case."""
        keywords = ['list', 'display', 'fetch', 'data', 'items', 'firestore']
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert found, \
            f'No case found covering data display/list component topic. Keywords: {keywords}'

    def test_button_action_component_covered(self, cases: List[Dict[str, Any]]):
        """Verify that button/action trigger component topic is covered in at least one case."""
        keywords = ['button', 'click', 'trigger', 'action', 'cloud function']
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert found, \
            f'No case found covering button/action trigger component topic. Keywords: {keywords}'


# Test Group 7: React/Component Keyword Validation
class TestReactComponentKeywords:
    """Test suite for validating presence of React and component keywords in tags."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing REACT_COMPONENTS_CASES for tests."""
        from cases.react.react_components_cases import REACT_COMPONENTS_CASES
        return REACT_COMPONENTS_CASES

    def test_tags_contain_react_keywords(self, cases: List[Dict[str, Any]]):
        """Verify that tags across all cases contain React/component related keywords."""
        react_component_keywords = [
            'react', 'component', 'jsx', 'tsx', 'hook', 'useState', 'useEffect',
            'props', 'bootstrap', 'ui', 'form', 'button', 'modal', 'navbar',
            'grid', 'layout', 'card', 'validation', 'navigation'
        ]

        all_tags_lower = []
        for case in cases:
            all_tags_lower.extend([tag.lower() for tag in case.get('tags', [])])

        found_keywords = []
        for keyword in react_component_keywords:
            if any(keyword in tag for tag in all_tags_lower):
                found_keywords.append(keyword)

        assert len(found_keywords) > 0, \
            f'Tags must contain React/component keywords. Expected any of: {react_component_keywords}'


# Test Group 8: Dynamic Loader Integration
class TestDynamicLoaderIntegration:
    """Tests for dynamic loader integration."""

    def test_module_importable_via_cases_package(self):
        """Test that the module can be imported via cases.react.react_components_cases."""
        try:
            from cases.react import react_components_cases
            assert hasattr(react_components_cases, 'REACT_COMPONENTS_CASES'), \
                "Module must be importable and define REACT_COMPONENTS_CASES"
        except ImportError as e:
            pytest.fail(f"Failed to import via cases.react package: {e}")

    def test_dynamic_loader_can_discover_module(self):
        """Test that the dynamic loader can discover this module."""
        import importlib
        import pkgutil

        # Check that cases.react package exists
        try:
            import cases.react
        except ImportError:
            pytest.fail("cases.react package does not exist")

        # Check that react_components_cases is discoverable in the package
        module_found = False
        for importer, modname, ispkg in pkgutil.iter_modules(cases.react.__path__, prefix='cases.react.'):
            if modname == 'cases.react.react_components_cases':
                module_found = True
                break

        assert module_found, \
            "react_components_cases module not discoverable by dynamic loader"
