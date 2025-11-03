"""
Test suite for case_base.py backward compatibility wrapper.

This test suite verifies that the refactored case_base.py module correctly
imports ALL_CASES from the cases module and assigns it to CASE_BASE,
maintaining backward compatibility with existing code that imports CASE_BASE
from case_base.

These tests are designed to FAIL initially (before the refactoring is complete)
and PASS once case_base.py has been refactored to import from the cases module.
"""

import pytest
from typing import Dict, Any, List


class TestCaseBaseImport:
    """Test that CASE_BASE can be imported from case_base module."""

    def test_case_base_can_be_imported(self):
        """
        Verify that CASE_BASE can be successfully imported from case_base module.

        This tests the basic import pattern used by existing code:
        from case_base import CASE_BASE
        """
        # Attempt to import CASE_BASE
        from case_base import CASE_BASE

        # Verify it's defined and not None
        assert CASE_BASE is not None, "CASE_BASE should be defined and not None"


class TestCaseBaseEquality:
    """Test that CASE_BASE equals ALL_CASES from cases module."""

    def test_case_base_equals_all_cases_by_reference(self):
        """
        Verify that CASE_BASE is the exact same object as ALL_CASES (identity check).

        This is the ideal scenario - case_base.CASE_BASE should be assigned
        directly from cases.ALL_CASES, making them the same object in memory.
        """
        from case_base import CASE_BASE
        from cases import ALL_CASES

        # Check if they are the same object (identity)
        assert CASE_BASE is ALL_CASES, (
            "CASE_BASE should be the same object as ALL_CASES (same reference)"
        )

    def test_case_base_equals_all_cases_by_content(self):
        """
        Verify that CASE_BASE has identical content to ALL_CASES (equality check).

        This is a fallback test in case they are different objects but with
        identical content. The reference test is preferred.
        """
        from case_base import CASE_BASE
        from cases import ALL_CASES

        # Check if they have the same content (equality)
        assert CASE_BASE == ALL_CASES, (
            "CASE_BASE should have identical content to ALL_CASES"
        )

        # Also verify they have the same length
        assert len(CASE_BASE) == len(ALL_CASES), (
            f"CASE_BASE length ({len(CASE_BASE)}) should equal "
            f"ALL_CASES length ({len(ALL_CASES)})"
        )


class TestCaseBaseStructure:
    """Test that CASE_BASE has the expected structure and data types."""

    def test_case_base_is_list(self):
        """
        Verify that CASE_BASE is a list type.

        Existing code expects CASE_BASE to be a list of case dictionaries.
        """
        from case_base import CASE_BASE

        assert isinstance(CASE_BASE, list), (
            f"CASE_BASE should be a list, but got {type(CASE_BASE).__name__}"
        )

    def test_case_base_contains_case_dictionaries(self):
        """
        Verify that CASE_BASE contains dictionaries (case objects).

        Each item in CASE_BASE should be a dictionary representing a case.
        """
        from case_base import CASE_BASE

        # Verify CASE_BASE is not empty
        assert len(CASE_BASE) > 0, "CASE_BASE should contain at least one case"

        # Verify each item is a dictionary
        for idx, case in enumerate(CASE_BASE):
            assert isinstance(case, dict), (
                f"Case at index {idx} should be a dict, but got {type(case).__name__}"
            )


class TestCaseBaseRequiredFields:
    """Test that case dictionaries in CASE_BASE have all required fields."""

    def test_case_base_cases_have_required_fields(self):
        """
        Verify that each case dictionary has all required fields for CBR functionality.

        Required fields:
        - problem: str (the problem description)
        - solution: str (the solution code/text)
        - category: str (the case category)
        - subcategory: str (the case subcategory)
        - tags: list (list of tags for the case)
        """
        from case_base import CASE_BASE

        required_fields = ["problem", "solution", "category", "subcategory", "tags"]

        # Check first few cases to verify structure
        # (checking all cases could be slow if there are many)
        sample_size = min(10, len(CASE_BASE))

        for idx in range(sample_size):
            case = CASE_BASE[idx]

            for field in required_fields:
                assert field in case, (
                    f"Case at index {idx} is missing required field '{field}'. "
                    f"Case keys: {list(case.keys())}"
                )

    def test_case_base_cases_have_valid_field_types(self):
        """
        Verify that required fields have the expected data types.

        This ensures backward compatibility with code that expects specific
        field types in case dictionaries.
        """
        from case_base import CASE_BASE

        # Check first few cases
        sample_size = min(10, len(CASE_BASE))

        for idx in range(sample_size):
            case = CASE_BASE[idx]

            # problem should be a string
            assert isinstance(case.get("problem"), str), (
                f"Case {idx}: 'problem' should be a string, "
                f"got {type(case.get('problem')).__name__}"
            )

            # solution should be a string
            assert isinstance(case.get("solution"), str), (
                f"Case {idx}: 'solution' should be a string, "
                f"got {type(case.get('solution')).__name__}"
            )

            # category should be a string
            assert isinstance(case.get("category"), str), (
                f"Case {idx}: 'category' should be a string, "
                f"got {type(case.get('category')).__name__}"
            )

            # subcategory should be a string
            assert isinstance(case.get("subcategory"), str), (
                f"Case {idx}: 'subcategory' should be a string, "
                f"got {type(case.get('subcategory')).__name__}"
            )

            # tags should be a list
            assert isinstance(case.get("tags"), list), (
                f"Case {idx}: 'tags' should be a list, "
                f"got {type(case.get('tags')).__name__}"
            )


class TestBackwardCompatibilityImportPattern:
    """Test the exact import pattern used by existing code."""

    def test_backward_compatibility_import_pattern(self):
        """
        Verify the exact import pattern used by existing code works correctly.

        This simulates the way existing code imports and uses CASE_BASE:
        from case_base import CASE_BASE
        """
        # Import using the legacy pattern
        from case_base import CASE_BASE

        # Verify it's usable as expected
        assert CASE_BASE is not None
        assert isinstance(CASE_BASE, list)
        assert len(CASE_BASE) > 0

        # Verify first case has expected structure
        first_case = CASE_BASE[0]
        assert isinstance(first_case, dict)
        assert "problem" in first_case
        assert "solution" in first_case

    def test_case_base_module_can_be_imported(self):
        """
        Verify that the case_base module itself can be imported.

        This tests the import pattern: import case_base
        """
        import case_base

        # Verify the module has CASE_BASE attribute
        assert hasattr(case_base, "CASE_BASE"), (
            "case_base module should have CASE_BASE attribute"
        )

        # Verify CASE_BASE is accessible via module
        assert case_base.CASE_BASE is not None
        assert isinstance(case_base.CASE_BASE, list)
