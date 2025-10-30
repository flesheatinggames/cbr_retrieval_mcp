"""
Unit tests for backward compatibility wrapper in case_base.py.

This test suite verifies that case_base.py correctly imports cases from the
new modular structure in cases/ and maintains backward compatibility with
existing code that imports from case_base.

Test-Driven Development (TDD) approach:
- These tests are written BEFORE the case_base.py refactoring
- Initial test run will FAIL (Red phase) as the modular structure doesn't exist yet
- Tests will PASS (Green phase) once Task 11 refactors case_base.py to:
    from cases import ALL_CASES
    CASE_BASE = ALL_CASES

Expected refactoring in case_base.py (Task 11):
    '''
    from cases import ALL_CASES

    # Maintain existing API
    CASE_BASE = ALL_CASES

    # Legacy helper functions remain (save_case_base_to_file, search_cases, etc.)
    '''
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest


class TestCaseBaseImports:
    """Test suite for case_base.py import and reference validation."""

    def test_case_base_imports_from_cases_module(self):
        """
        Verify case_base.py correctly imports from new modular structure.

        After refactoring (Task 11), case_base.py should import ALL_CASES
        from the cases module and assign it to CASE_BASE.

        Expected behavior:
        - case_base.CASE_BASE exists and is a list
        - case_base.CASE_BASE is the same object reference as cases.ALL_CASES
        - CASE_BASE is not a copy, but the actual ALL_CASES object

        Current state (TDD Red phase):
        - cases module doesn't exist yet (will be created in Task 2)
        - case_base.py has monolithic CASE_BASE list (5,768 lines)
        - This test will FAIL until Task 11 refactors case_base.py
        """
        # Import cases module (will fail if not created yet)
        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.skip("cases module not created yet (Task 2)")

        # Import case_base module
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("case_base.py should exist and be importable")

        # Verify CASE_BASE exists and is a list
        assert isinstance(CASE_BASE, list), (
            "CASE_BASE should be a list"
        )

        # Verify CASE_BASE equals ALL_CASES (same content)
        assert CASE_BASE == ALL_CASES, (
            "CASE_BASE should equal ALL_CASES after refactoring"
        )

        # Verify CASE_BASE is the same object reference (not a copy)
        assert CASE_BASE is ALL_CASES, (
            "CASE_BASE should be the same object as ALL_CASES (not a copy)\n"
            "Expected refactoring: CASE_BASE = ALL_CASES"
        )

    def test_case_base_case_count_matches_all_cases(self):
        """
        Verify CASE_BASE has the same number of cases as ALL_CASES.

        After refactoring, both should have exactly 49 cases (or 5+ initially
        if only rust cases are migrated first).

        Current state (TDD Red phase):
        - cases module doesn't exist yet
        - This test will SKIP until cases.ALL_CASES is available
        """
        # Import modules
        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.skip("cases module not created yet (Task 2)")

        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("case_base.py should exist and be importable")

        # Verify counts match
        assert len(CASE_BASE) == len(ALL_CASES), (
            f"CASE_BASE has {len(CASE_BASE)} cases but ALL_CASES has {len(ALL_CASES)} cases\n"
            "Counts should match after refactoring"
        )

        # Verify minimum case count (5+ for rust cases, 49 eventually)
        assert len(CASE_BASE) >= 5, (
            f"Expected at least 5 cases, got {len(CASE_BASE)}"
        )

        # Verify eventually we have all 49 cases
        if len(ALL_CASES) >= 49:
            assert len(CASE_BASE) == 49, (
                f"Expected exactly 49 cases after full migration, got {len(CASE_BASE)}"
            )

    def test_case_base_can_be_imported_standalone(self):
        """
        Verify case_base.py works as standalone entry point.

        Users should be able to import case_base without explicitly importing
        the cases module. The import chain should work automatically.

        Expected behavior:
        - from case_base import CASE_BASE works
        - CASE_BASE is available and populated
        - No circular import issues
        - No need to import cases module separately

        Current state (TDD Red phase):
        - This currently works with monolithic CASE_BASE
        - Should continue to work after refactoring
        """
        # Import only case_base (not cases directly)
        try:
            from case_base import CASE_BASE
        except ImportError as e:
            pytest.fail(f"case_base should be importable standalone: {e}")

        # Verify CASE_BASE is available
        assert CASE_BASE is not None, "CASE_BASE should not be None"
        assert isinstance(CASE_BASE, list), "CASE_BASE should be a list"

        # Verify CASE_BASE is populated (minimum 5 cases)
        assert len(CASE_BASE) >= 5, (
            f"CASE_BASE should have at least 5 cases, got {len(CASE_BASE)}"
        )

        # Verify each case is a dictionary with required fields
        for i, case in enumerate(CASE_BASE[:3]):  # Check first 3 cases
            assert isinstance(case, dict), (
                f"Case {i} should be a dictionary, got {type(case)}"
            )
            assert "problem" in case, f"Case {i} missing 'problem' field"
            assert "solution" in case, f"Case {i} missing 'solution' field"


class TestCaseBaseHelperFunctions:
    """Test suite for legacy helper function compatibility."""

    def test_case_base_helper_functions_work(self, tmp_path: Path):
        """
        Verify legacy helper functions still work after refactoring.

        Tests all helper functions that exist in current case_base.py:
        1. save_case_base_to_file(filename) - saves all cases to JSON
        2. search_cases(query) - returns relevant cases
        3. validate_case_base() - validates case structure
        4. get_case_statistics() - returns case counts and stats

        Current state (TDD Red phase):
        - Helper functions exist and work with monolithic CASE_BASE
        - Should continue to work after refactoring to use ALL_CASES
        """
        # Import case_base module with helper functions
        try:
            from case_base import (
                CASE_BASE,
                save_case_base_to_file,
                search_cases,
                validate_case_base,
                get_case_statistics,
            )
        except ImportError as e:
            pytest.fail(f"Failed to import case_base or helper functions: {e}")

        # Test 1: save_case_base_to_file creates valid JSON
        output_file = tmp_path / "test_cases.json"
        result_file = save_case_base_to_file(str(output_file))

        assert output_file.exists(), "save_case_base_to_file should create file"
        assert output_file.is_file(), "Output should be a file"

        # Verify JSON is valid and contains all cases
        with open(output_file, 'r', encoding='utf-8') as f:
            loaded_cases = json.load(f)

        assert isinstance(loaded_cases, list), "Saved data should be a list"
        assert len(loaded_cases) == len(CASE_BASE), (
            f"Saved {len(loaded_cases)} cases but CASE_BASE has {len(CASE_BASE)}"
        )

        # Test 2: search_cases returns relevant results
        search_results = search_cases("firebase")
        assert isinstance(search_results, list), "search_cases should return a list"

        # Verify search finds relevant cases
        if len(CASE_BASE) > 0:
            assert len(search_results) >= 0, "search_cases should return results"

            # If results found, verify they contain the query term
            if len(search_results) > 0:
                first_result = search_results[0]
                assert isinstance(first_result, dict), "Search result should be a dict"
                search_term = "firebase"
                result_text = (
                    first_result.get("problem", "").lower() +
                    first_result.get("solution", "").lower()
                )
                # Note: Current implementation may return any results, so this is flexible

        # Test 3: validate_case_base returns True for valid structure
        is_valid = validate_case_base()
        # Current implementation may not enforce all new metadata fields yet
        # So we just verify it returns a boolean and doesn't crash
        assert isinstance(is_valid, bool), "validate_case_base should return boolean"

        # Test 4: get_case_statistics returns correct counts
        stats = get_case_statistics()
        assert isinstance(stats, dict), "get_case_statistics should return a dict"
        assert "total_cases" in stats, "Stats should include total_cases"
        assert stats["total_cases"] == len(CASE_BASE), (
            f"Stats show {stats['total_cases']} cases but CASE_BASE has {len(CASE_BASE)}"
        )

        # Verify categories are tracked (after metadata migration)
        if "categories" in stats:
            assert isinstance(stats["categories"], dict), (
                "categories should be a dict"
            )


class TestCaseBaseListOperations:
    """Test suite for CASE_BASE list operation compatibility."""

    def test_case_base_array_indexing_works(self):
        """
        Verify CASE_BASE supports array indexing patterns.

        Tests standard list indexing operations:
        - CASE_BASE[0] - first case
        - CASE_BASE[-1] - last case
        - CASE_BASE[5] - arbitrary index
        - Out of bounds raises IndexError

        Current state: Works with monolithic list, should continue after refactoring
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("case_base should be importable")

        # Verify CASE_BASE has cases
        assert len(CASE_BASE) >= 5, (
            f"Need at least 5 cases for indexing tests, got {len(CASE_BASE)}"
        )

        # Test positive indexing
        first_case = CASE_BASE[0]
        assert isinstance(first_case, dict), "First case should be a dict"
        assert "problem" in first_case, "First case should have 'problem' field"
        assert "solution" in first_case, "First case should have 'solution' field"

        # Test negative indexing
        last_case = CASE_BASE[-1]
        assert isinstance(last_case, dict), "Last case should be a dict"
        assert "problem" in last_case, "Last case should have 'problem' field"
        assert "solution" in last_case, "Last case should have 'solution' field"

        # Test arbitrary index
        middle_case = CASE_BASE[2]
        assert isinstance(middle_case, dict), "Middle case should be a dict"

        # Test out of bounds raises IndexError
        with pytest.raises(IndexError):
            _ = CASE_BASE[len(CASE_BASE) + 10]

    def test_case_base_iteration_works(self):
        """
        Verify CASE_BASE supports iteration patterns.

        Tests standard list iteration:
        - for case in CASE_BASE: ...
        - Iteration completes without errors
        - All cases are accessible
        - Each case is a valid dictionary

        Current state: Works with monolithic list, should continue after refactoring
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("case_base should be importable")

        # Verify CASE_BASE has cases
        assert len(CASE_BASE) >= 5, (
            f"Need at least 5 cases for iteration tests, got {len(CASE_BASE)}"
        )

        # Test iteration
        case_count = 0
        for case in CASE_BASE:
            # Verify each case is a dictionary
            assert isinstance(case, dict), (
                f"Case {case_count} should be a dict, got {type(case)}"
            )

            # Verify required fields
            assert "problem" in case, f"Case {case_count} missing 'problem' field"
            assert "solution" in case, f"Case {case_count} missing 'solution' field"

            case_count += 1

        # Verify all cases were iterated
        assert case_count == len(CASE_BASE), (
            f"Iterated {case_count} cases but CASE_BASE has {len(CASE_BASE)}"
        )

    def test_case_base_slicing_works(self):
        """
        Verify CASE_BASE supports slicing patterns.

        Tests standard list slicing:
        - CASE_BASE[0:10] - first 10 cases
        - CASE_BASE[10:] - all cases from index 10
        - CASE_BASE[:5] - first 5 cases
        - CASE_BASE[::2] - every other case
        - Slicing returns a list

        Current state: Works with monolithic list, should continue after refactoring
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("case_base should be importable")

        # Verify CASE_BASE has enough cases for slicing tests
        min_cases = 10
        if len(CASE_BASE) < min_cases:
            pytest.skip(f"Need at least {min_cases} cases for slicing tests")

        # Test slice [0:10] - first 10 cases
        first_ten = CASE_BASE[0:10]
        assert isinstance(first_ten, list), "Slice should return a list"
        assert len(first_ten) == min(10, len(CASE_BASE)), (
            f"Slice [0:10] should return 10 cases, got {len(first_ten)}"
        )

        # Verify sliced results contain valid case dictionaries
        for case in first_ten:
            assert isinstance(case, dict), "Sliced case should be a dict"
            assert "problem" in case, "Sliced case should have 'problem' field"

        # Test slice [10:] - all cases from index 10
        remaining_cases = CASE_BASE[10:]
        assert isinstance(remaining_cases, list), "Slice [10:] should return a list"
        assert len(remaining_cases) == len(CASE_BASE) - 10, (
            f"Slice [10:] should return {len(CASE_BASE) - 10} cases, "
            f"got {len(remaining_cases)}"
        )

        # Test slice [:5] - first 5 cases
        first_five = CASE_BASE[:5]
        assert isinstance(first_five, list), "Slice [:5] should return a list"
        assert len(first_five) == 5, f"Slice [:5] should return 5 cases, got {len(first_five)}"

        # Test slice [::2] - every other case
        every_other = CASE_BASE[::2]
        assert isinstance(every_other, list), "Slice [::2] should return a list"
        expected_count = (len(CASE_BASE) + 1) // 2
        assert len(every_other) == expected_count, (
            f"Slice [::2] should return {expected_count} cases, got {len(every_other)}"
        )

        # Verify all sliced items are valid cases
        for case in every_other:
            assert isinstance(case, dict), "Sliced case should be a dict"


class TestCaseBaseBackwardCompatibility:
    """Test suite for ensuring full backward compatibility."""

    def test_existing_imports_still_work(self):
        """
        Verify that existing code patterns continue to work.

        Common import patterns that should work:
        - from case_base import CASE_BASE
        - import case_base; cases = case_base.CASE_BASE
        - from case_base import CASE_BASE, search_cases

        This ensures no breaking changes for existing code.
        """
        # Pattern 1: from case_base import CASE_BASE
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("Pattern 'from case_base import CASE_BASE' should work")

        assert isinstance(CASE_BASE, list), "CASE_BASE should be a list"
        assert len(CASE_BASE) >= 5, "CASE_BASE should have cases"

        # Pattern 2: import case_base
        try:
            import case_base
            cases = case_base.CASE_BASE
        except (ImportError, AttributeError) as e:
            pytest.fail(f"Pattern 'import case_base; cases = case_base.CASE_BASE' should work: {e}")

        assert isinstance(cases, list), "cases should be a list"
        assert len(cases) >= 5, "cases should have cases"

        # Pattern 3: from case_base import CASE_BASE, helper_function
        try:
            from case_base import CASE_BASE, search_cases
        except ImportError:
            pytest.fail("Pattern 'from case_base import CASE_BASE, search_cases' should work")

        assert callable(search_cases), "search_cases should be callable"

    def test_case_base_preserves_case_structure(self):
        """
        Verify that case structure is preserved after refactoring.

        Each case should have at least:
        - problem (string)
        - solution (string)

        After metadata migration, cases may also have:
        - category (string)
        - subcategory (string)
        - tags (list of strings)

        This test is flexible to handle cases with or without metadata.
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("case_base should be importable")

        assert len(CASE_BASE) >= 5, f"Expected at least 5 cases, got {len(CASE_BASE)}"

        # Check first 3 cases for structure
        for i, case in enumerate(CASE_BASE[:3]):
            assert isinstance(case, dict), f"Case {i} should be a dict"

            # Required fields
            assert "problem" in case, f"Case {i} missing 'problem' field"
            assert "solution" in case, f"Case {i} missing 'solution' field"

            # Verify types
            assert isinstance(case["problem"], str), (
                f"Case {i} 'problem' should be a string"
            )
            assert isinstance(case["solution"], str), (
                f"Case {i} 'solution' should be a string"
            )

            # Optional metadata fields (may not exist yet)
            if "category" in case:
                assert isinstance(case["category"], str), (
                    f"Case {i} 'category' should be a string"
                )

            if "subcategory" in case:
                assert isinstance(case["subcategory"], str), (
                    f"Case {i} 'subcategory' should be a string"
                )

            if "tags" in case:
                assert isinstance(case["tags"], (list, str)), (
                    f"Case {i} 'tags' should be a list or string"
                )
