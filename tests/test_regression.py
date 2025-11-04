"""
Regression tests for case base refactoring.

This test suite verifies that NO CASE CONTENT CHANGED during the modular refactoring.
It compares the original monolithic case_base.CASE_BASE with the new modular cases.ALL_CASES
to ensure:

1. Same number of cases (135 total)
2. Character-by-character identical problem text
3. Character-by-character identical solution text
4. New cases have metadata fields (category, subcategory, tags)
5. No whitespace, formatting, or character changes

Test-Driven Development (TDD) approach:
- These tests are written BEFORE the refactoring is complete
- Initial test run will FAIL (Red phase) if any case content differs
- Tests will PASS (Green phase) only when all 135 cases are identical

Purpose: Catch any regressions where problem/solution text was accidentally modified
during the modular refactoring process.
"""

import difflib
from typing import Dict, Any, List

import pytest


class TestCaseCountRegression:
    """Verify case counts match between old and new structure."""

    def test_case_count_matches(self):
        """
        Verify ALL_CASES has same count as original CASE_BASE.

        Expected: 135 cases in both structures

        This is the first checkpoint - if counts don't match, something was
        lost or duplicated during refactoring.
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("Could not import CASE_BASE from case_base")

        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        original_count = len(CASE_BASE)
        new_count = len(ALL_CASES)

        assert original_count == new_count, (
            f"Case count mismatch!\n"
            f"Original CASE_BASE: {original_count} cases\n"
            f"New ALL_CASES: {new_count} cases\n"
            f"Difference: {new_count - original_count:+d} cases\n"
            f"\n"
            f"This indicates cases were lost or duplicated during refactoring."
        )


class TestCaseIDCompleteness:
    """Verify all case IDs are preserved."""

    def test_all_case_ids_present(self):
        """
        Verify all case IDs from original are in new structure.

        Checks that:
        - No case IDs were lost
        - No duplicate case IDs were created
        - Case ID set matches exactly
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("Could not import CASE_BASE from case_base")

        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        # Build case ID mapping for both structures
        original_ids = {}
        for idx, case in enumerate(CASE_BASE):
            case_id = case.get('id', f'case_{idx}')
            original_ids[case_id] = case

        new_ids = {}
        for idx, case in enumerate(ALL_CASES):
            case_id = case.get('id', f'case_{idx}')
            new_ids[case_id] = case

        original_id_set = set(original_ids.keys())
        new_id_set = set(new_ids.keys())

        # Check for missing IDs
        missing_ids = original_id_set - new_id_set
        assert len(missing_ids) == 0, (
            f"Missing case IDs in new structure: {sorted(list(missing_ids))}\n"
            f"These {len(missing_ids)} cases were lost during refactoring!"
        )

        # Check for extra IDs
        extra_ids = new_id_set - original_id_set
        assert len(extra_ids) == 0, (
            f"Extra case IDs in new structure: {sorted(list(extra_ids))}\n"
            f"These {len(extra_ids)} cases are unexpected additions!"
        )

        # Verify exact match
        assert original_id_set == new_id_set, (
            f"Case ID sets don't match!\n"
            f"This should never fail if missing/extra checks pass."
        )


class TestProblemFieldRegression:
    """Verify problem field is identical character-by-character."""

    def test_problem_field_exact_match(self):
        """
        Verify problem field is identical for every case.

        This is character-by-character comparison including:
        - All characters (letters, numbers, symbols)
        - All whitespace (spaces, tabs, newlines)
        - String length
        - Encoding

        If this test fails, it shows the exact diff of what changed.
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("Could not import CASE_BASE from case_base")

        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        # Build case ID mapping
        original_cases = {}
        for idx, case in enumerate(CASE_BASE):
            case_id = case.get('id', f'case_{idx}')
            original_cases[case_id] = case

        new_cases = {}
        for idx, case in enumerate(ALL_CASES):
            case_id = case.get('id', f'case_{idx}')
            new_cases[case_id] = case

        # Compare problem field for each case
        differences = []
        for case_id in sorted(original_cases.keys()):
            if case_id not in new_cases:
                continue  # Skip cases not in new structure (handled by ID test)

            original_case = original_cases[case_id]
            new_case = new_cases[case_id]

            original_problem = original_case.get('problem', '')
            new_problem = new_case.get('problem', '')

            # Check exact match
            if original_problem != new_problem:
                # Generate unified diff
                diff = list(difflib.unified_diff(
                    original_problem.splitlines(keepends=True),
                    new_problem.splitlines(keepends=True),
                    fromfile=f'Original [{case_id}]',
                    tofile=f'New [{case_id}]',
                    lineterm=''
                ))

                differences.append({
                    'case_id': case_id,
                    'original_length': len(original_problem),
                    'new_length': len(new_problem),
                    'diff': ''.join(diff)
                })

        # Report all differences
        if differences:
            error_msg = f"\n{'='*80}\n"
            error_msg += f"PROBLEM FIELD REGRESSION: {len(differences)} case(s) have different problem text!\n"
            error_msg += f"{'='*80}\n\n"

            for idx, diff_info in enumerate(differences, 1):
                error_msg += f"Difference {idx}/{len(differences)}: Case ID = {diff_info['case_id']}\n"
                error_msg += f"  Original length: {diff_info['original_length']} characters\n"
                error_msg += f"  New length: {diff_info['new_length']} characters\n"
                error_msg += f"  Diff:\n{diff_info['diff']}\n"
                error_msg += f"{'-'*80}\n\n"

            pytest.fail(error_msg)


class TestSolutionFieldRegression:
    """Verify solution field is identical character-by-character."""

    def test_solution_field_exact_match(self):
        """
        Verify solution field is identical for every case.

        This is character-by-character comparison including:
        - All characters (letters, numbers, symbols)
        - All whitespace (spaces, tabs, newlines)
        - String length
        - Encoding

        If this test fails, it shows the exact diff of what changed.
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("Could not import CASE_BASE from case_base")

        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        # Build case ID mapping
        original_cases = {}
        for idx, case in enumerate(CASE_BASE):
            case_id = case.get('id', f'case_{idx}')
            original_cases[case_id] = case

        new_cases = {}
        for idx, case in enumerate(ALL_CASES):
            case_id = case.get('id', f'case_{idx}')
            new_cases[case_id] = case

        # Compare solution field for each case
        differences = []
        for case_id in sorted(original_cases.keys()):
            if case_id not in new_cases:
                continue  # Skip cases not in new structure (handled by ID test)

            original_case = original_cases[case_id]
            new_case = new_cases[case_id]

            original_solution = original_case.get('solution', '')
            new_solution = new_case.get('solution', '')

            # Check exact match
            if original_solution != new_solution:
                # Generate unified diff
                diff = list(difflib.unified_diff(
                    original_solution.splitlines(keepends=True),
                    new_solution.splitlines(keepends=True),
                    fromfile=f'Original [{case_id}]',
                    tofile=f'New [{case_id}]',
                    lineterm=''
                ))

                differences.append({
                    'case_id': case_id,
                    'original_length': len(original_solution),
                    'new_length': len(new_solution),
                    'diff': ''.join(diff)
                })

        # Report all differences
        if differences:
            error_msg = f"\n{'='*80}\n"
            error_msg += f"SOLUTION FIELD REGRESSION: {len(differences)} case(s) have different solution text!\n"
            error_msg += f"{'='*80}\n\n"

            for idx, diff_info in enumerate(differences, 1):
                error_msg += f"Difference {idx}/{len(differences)}: Case ID = {diff_info['case_id']}\n"
                error_msg += f"  Original length: {diff_info['original_length']} characters\n"
                error_msg += f"  New length: {diff_info['new_length']} characters\n"
                error_msg += f"  Diff:\n{diff_info['diff']}\n"
                error_msg += f"{'-'*80}\n\n"

            pytest.fail(error_msg)


class TestWhitespacePreservation:
    """Verify whitespace is preserved exactly."""

    def test_leading_trailing_whitespace_preserved(self):
        """
        Verify leading and trailing whitespace is preserved.

        This specifically checks for:
        - Leading spaces/tabs
        - Trailing spaces/tabs
        - Leading/trailing newlines
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("Could not import CASE_BASE from case_base")

        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        # Build case ID mapping
        original_cases = {}
        for idx, case in enumerate(CASE_BASE):
            case_id = case.get('id', f'case_{idx}')
            original_cases[case_id] = case

        new_cases = {}
        for idx, case in enumerate(ALL_CASES):
            case_id = case.get('id', f'case_{idx}')
            new_cases[case_id] = case

        # Check whitespace preservation
        whitespace_issues = []
        for case_id in sorted(original_cases.keys()):
            if case_id not in new_cases:
                continue

            original_case = original_cases[case_id]
            new_case = new_cases[case_id]

            # Check problem field
            orig_prob = original_case.get('problem', '')
            new_prob = new_case.get('problem', '')

            if orig_prob != new_prob:
                # Check for whitespace normalization
                if orig_prob.strip() == new_prob.strip():
                    whitespace_issues.append({
                        'case_id': case_id,
                        'field': 'problem',
                        'issue': 'leading/trailing whitespace changed'
                    })

            # Check solution field
            orig_sol = original_case.get('solution', '')
            new_sol = new_case.get('solution', '')

            if orig_sol != new_sol:
                # Check for whitespace normalization
                if orig_sol.strip() == new_sol.strip():
                    whitespace_issues.append({
                        'case_id': case_id,
                        'field': 'solution',
                        'issue': 'leading/trailing whitespace changed'
                    })

        assert len(whitespace_issues) == 0, (
            f"Whitespace normalization detected in {len(whitespace_issues)} case(s):\n"
            f"{whitespace_issues}\n"
            f"Leading/trailing whitespace must be preserved exactly!"
        )

    def test_internal_whitespace_preserved(self):
        """
        Verify internal whitespace (indentation) is preserved.

        This checks that:
        - Spaces in code examples are preserved
        - Tabs are preserved
        - Multiple consecutive spaces are preserved
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("Could not import CASE_BASE from case_base")

        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        # Build case ID mapping
        original_cases = {}
        for idx, case in enumerate(CASE_BASE):
            case_id = case.get('id', f'case_{idx}')
            original_cases[case_id] = case

        new_cases = {}
        for idx, case in enumerate(ALL_CASES):
            case_id = case.get('id', f'case_{idx}')
            new_cases[case_id] = case

        # Check for internal whitespace changes
        indentation_issues = []
        for case_id in sorted(original_cases.keys()):
            if case_id not in new_cases:
                continue

            original_case = original_cases[case_id]
            new_case = new_cases[case_id]

            # Check problem field
            orig_prob = original_case.get('problem', '')
            new_prob = new_case.get('problem', '')

            if orig_prob != new_prob:
                # Check if only internal whitespace differs
                if ''.join(orig_prob.split()) == ''.join(new_prob.split()):
                    indentation_issues.append({
                        'case_id': case_id,
                        'field': 'problem'
                    })

            # Check solution field
            orig_sol = original_case.get('solution', '')
            new_sol = new_case.get('solution', '')

            if orig_sol != new_sol:
                # Check if only internal whitespace differs
                if ''.join(orig_sol.split()) == ''.join(new_sol.split()):
                    indentation_issues.append({
                        'case_id': case_id,
                        'field': 'solution'
                    })

        assert len(indentation_issues) == 0, (
            f"Indentation/internal whitespace changed in {len(indentation_issues)} case(s):\n"
            f"{indentation_issues}\n"
            f"All internal whitespace (spaces, tabs, indentation) must be preserved!"
        )


class TestMetadataFieldsPresent:
    """Verify new metadata fields are present in modular structure."""

    def test_all_cases_have_category(self):
        """
        Verify all cases in ALL_CASES have 'category' field.

        New modular structure requires category metadata.
        """
        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        cases_without_category = []
        for idx, case in enumerate(ALL_CASES):
            case_id = case.get('id', f'case_{idx}')
            if 'category' not in case:
                cases_without_category.append(case_id)
            elif not case['category']:
                cases_without_category.append(f"{case_id} (empty)")

        assert len(cases_without_category) == 0, (
            f"Missing or empty 'category' field in {len(cases_without_category)} case(s):\n"
            f"{cases_without_category[:10]}...\n"
            f"All cases must have a non-empty 'category' field!"
        )

    def test_all_cases_have_subcategory(self):
        """
        Verify all cases in ALL_CASES have 'subcategory' field.

        New modular structure requires subcategory metadata.
        """
        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        cases_without_subcategory = []
        for idx, case in enumerate(ALL_CASES):
            case_id = case.get('id', f'case_{idx}')
            if 'subcategory' not in case:
                cases_without_subcategory.append(case_id)
            elif not case['subcategory']:
                cases_without_subcategory.append(f"{case_id} (empty)")

        assert len(cases_without_subcategory) == 0, (
            f"Missing or empty 'subcategory' field in {len(cases_without_subcategory)} case(s):\n"
            f"{cases_without_subcategory[:10]}...\n"
            f"All cases must have a non-empty 'subcategory' field!"
        )

    def test_all_cases_have_tags(self):
        """
        Verify all cases in ALL_CASES have 'tags' field.

        New modular structure requires tags metadata.
        Tags should be a non-empty list.
        """
        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        cases_with_tag_issues = []
        for idx, case in enumerate(ALL_CASES):
            case_id = case.get('id', f'case_{idx}')

            # Check field exists
            if 'tags' not in case:
                cases_with_tag_issues.append(f"{case_id}: missing 'tags' field")
                continue

            # Check it's a list
            if not isinstance(case['tags'], list):
                cases_with_tag_issues.append(
                    f"{case_id}: 'tags' is {type(case['tags']).__name__}, not list"
                )
                continue

            # Check it's not empty
            if not case['tags']:
                cases_with_tag_issues.append(f"{case_id}: 'tags' is empty list")

        assert len(cases_with_tag_issues) == 0, (
            f"Tag issues in {len(cases_with_tag_issues)} case(s):\n"
            f"{cases_with_tag_issues[:10]}...\n"
            f"All cases must have 'tags' as a non-empty list!"
        )


class TestOriginalFieldsUnchanged:
    """Verify original fields remain intact."""

    def test_original_field_names_present(self):
        """
        Verify all original field names are still present.

        Original fields should include:
        - problem
        - solution
        - id (if present)
        - embedding (if present)
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("Could not import CASE_BASE from case_base")

        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        # Get sample original case to determine expected fields
        if len(CASE_BASE) == 0:
            pytest.skip("No cases to compare")

        sample_original = CASE_BASE[0]
        original_fields = set(sample_original.keys())

        # Build case mapping
        new_cases = {}
        for idx, case in enumerate(ALL_CASES):
            case_id = case.get('id', f'case_{idx}')
            new_cases[case_id] = case

        # Check that original fields are present
        missing_fields = []
        for idx, original_case in enumerate(CASE_BASE):
            case_id = original_case.get('id', f'case_{idx}')
            if case_id not in new_cases:
                continue

            new_case = new_cases[case_id]
            new_fields = set(new_case.keys())

            # Check for missing original fields
            missing = original_fields - new_fields
            if missing:
                missing_fields.append({
                    'case_id': case_id,
                    'missing_fields': list(missing)
                })

        assert len(missing_fields) == 0, (
            f"Original fields missing in {len(missing_fields)} case(s):\n"
            f"{missing_fields[:10]}...\n"
            f"All original fields must be preserved!"
        )


class TestBinaryContentComparison:
    """Verify content matches at binary/bytes level."""

    def test_problem_bytes_match(self):
        """
        Verify problem field matches at bytes level.

        This catches subtle encoding differences that string comparison might miss.
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("Could not import CASE_BASE from case_base")

        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        # Build case mapping
        original_cases = {}
        for idx, case in enumerate(CASE_BASE):
            case_id = case.get('id', f'case_{idx}')
            original_cases[case_id] = case

        new_cases = {}
        for idx, case in enumerate(ALL_CASES):
            case_id = case.get('id', f'case_{idx}')
            new_cases[case_id] = case

        # Compare at bytes level
        encoding_issues = []
        for case_id in sorted(original_cases.keys()):
            if case_id not in new_cases:
                continue

            original_case = original_cases[case_id]
            new_case = new_cases[case_id]

            orig_prob = original_case.get('problem', '')
            new_prob = new_case.get('problem', '')

            # Encode to bytes and compare
            orig_bytes = orig_prob.encode('utf-8')
            new_bytes = new_prob.encode('utf-8')

            if orig_bytes != new_bytes:
                encoding_issues.append({
                    'case_id': case_id,
                    'field': 'problem',
                    'original_bytes': len(orig_bytes),
                    'new_bytes': len(new_bytes)
                })

        assert len(encoding_issues) == 0, (
            f"Encoding differences detected in {len(encoding_issues)} case(s):\n"
            f"{encoding_issues[:10]}...\n"
            f"Content must match at binary/bytes level!"
        )

    def test_solution_bytes_match(self):
        """
        Verify solution field matches at bytes level.

        This catches subtle encoding differences that string comparison might miss.
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("Could not import CASE_BASE from case_base")

        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        # Build case mapping
        original_cases = {}
        for idx, case in enumerate(CASE_BASE):
            case_id = case.get('id', f'case_{idx}')
            original_cases[case_id] = case

        new_cases = {}
        for idx, case in enumerate(ALL_CASES):
            case_id = case.get('id', f'case_{idx}')
            new_cases[case_id] = case

        # Compare at bytes level
        encoding_issues = []
        for case_id in sorted(original_cases.keys()):
            if case_id not in new_cases:
                continue

            original_case = original_cases[case_id]
            new_case = new_cases[case_id]

            orig_sol = original_case.get('solution', '')
            new_sol = new_case.get('solution', '')

            # Encode to bytes and compare
            orig_bytes = orig_sol.encode('utf-8')
            new_bytes = new_sol.encode('utf-8')

            if orig_bytes != new_bytes:
                encoding_issues.append({
                    'case_id': case_id,
                    'field': 'solution',
                    'original_bytes': len(orig_bytes),
                    'new_bytes': len(new_bytes)
                })

        assert len(encoding_issues) == 0, (
            f"Encoding differences detected in {len(encoding_issues)} case(s):\n"
            f"{encoding_issues[:10]}...\n"
            f"Content must match at binary/bytes level!"
        )


class TestComprehensiveCoverage:
    """Verify all cases are tested comprehensively."""

    def test_all_cases_covered(self):
        """
        Verify we're testing all cases comprehensively (not just a sample).

        This meta-test ensures complete coverage of the case base.
        Expected: At least 100 cases (likely 135 based on spec)
        """
        try:
            from case_base import CASE_BASE
        except ImportError:
            pytest.fail("Could not import CASE_BASE from case_base")

        try:
            from cases import ALL_CASES
        except ImportError:
            pytest.fail("Could not import ALL_CASES from cases module")

        # Verify we have sufficient cases (at least 100)
        min_expected_cases = 100
        assert len(CASE_BASE) >= min_expected_cases, (
            f"Expected at least {min_expected_cases} cases in CASE_BASE, got {len(CASE_BASE)}"
        )

        assert len(ALL_CASES) >= min_expected_cases, (
            f"Expected at least {min_expected_cases} cases in ALL_CASES, got {len(ALL_CASES)}"
        )

        # Verify counts match (most important check)
        assert len(CASE_BASE) == len(ALL_CASES), (
            f"Case count mismatch: CASE_BASE has {len(CASE_BASE)}, "
            f"ALL_CASES has {len(ALL_CASES)}"
        )

        # Build case ID sets
        original_ids = set()
        for idx, case in enumerate(CASE_BASE):
            case_id = case.get('id', f'case_{idx}')
            original_ids.add(case_id)

        new_ids = set()
        for idx, case in enumerate(ALL_CASES):
            case_id = case.get('id', f'case_{idx}')
            new_ids.add(case_id)

        # Verify all IDs are unique (no duplicates)
        assert len(original_ids) == len(CASE_BASE), (
            f"Duplicate case IDs detected in CASE_BASE! "
            f"{len(CASE_BASE)} cases but only {len(original_ids)} unique IDs"
        )

        assert len(new_ids) == len(ALL_CASES), (
            f"Duplicate case IDs detected in ALL_CASES! "
            f"{len(ALL_CASES)} cases but only {len(new_ids)} unique IDs"
        )

        # Verify ID sets match
        assert original_ids == new_ids, (
            f"Case ID sets don't match!\n"
            f"Missing from new: {original_ids - new_ids}\n"
            f"Extra in new: {new_ids - original_ids}"
        )
