"""
Tests for webdev_state_management_cases module.

This test suite validates the webdev state management cases module following TDD principles.
Tests will initially fail since the module doesn't exist yet.
"""

import pytest


class TestWebdevStateManagementCasesModule:
    """Test suite for webdev state management cases module structure and content."""

    def test_module_import(self):
        """
        Test that the webdev_state_management_cases module can be imported successfully.

        This is the most basic test - if the module doesn't exist or has syntax errors,
        this test will fail.
        """
        try:
            from cases.webdev import webdev_state_management_cases
            assert webdev_state_management_cases is not None
        except ImportError as e:
            pytest.fail(f"Failed to import webdev_state_management_cases module: {e}")

    def test_case_list_variable_exists(self):
        """
        Test that WEBDEV_STATE_MANAGEMENT_CASES variable exists and is a list.

        Verifies that the module exports the expected variable name and that
        it's the correct type (list).
        """
        from cases.webdev import webdev_state_management_cases

        assert hasattr(webdev_state_management_cases, 'WEBDEV_STATE_MANAGEMENT_CASES'), \
            "Module must export WEBDEV_STATE_MANAGEMENT_CASES variable"

        cases = webdev_state_management_cases.WEBDEV_STATE_MANAGEMENT_CASES
        assert isinstance(cases, list), \
            "WEBDEV_STATE_MANAGEMENT_CASES must be a list"

    def test_case_count(self):
        """
        Test that the list contains exactly 3 cases.

        According to the spec, there should be exactly 3 state management cases
        extracted from the original case_base.py.
        """
        from cases.webdev.webdev_state_management_cases import WEBDEV_STATE_MANAGEMENT_CASES

        assert len(WEBDEV_STATE_MANAGEMENT_CASES) == 3, \
            f"Expected exactly 3 cases, found {len(WEBDEV_STATE_MANAGEMENT_CASES)}"

    def test_metadata_fields_presence(self):
        """
        Test that all cases have required metadata fields.

        Each case must have:
        - category: "webdev"
        - subcategory: "state-management"
        - tags: list
        - problem: string
        - solution: string
        """
        from cases.webdev.webdev_state_management_cases import WEBDEV_STATE_MANAGEMENT_CASES

        for i, case in enumerate(WEBDEV_STATE_MANAGEMENT_CASES):
            # Test category
            assert 'category' in case, \
                f"Case {i} missing 'category' field"
            assert case['category'] == 'webdev', \
                f"Case {i} has incorrect category: {case.get('category')}"

            # Test subcategory
            assert 'subcategory' in case, \
                f"Case {i} missing 'subcategory' field"
            assert case['subcategory'] == 'state-management', \
                f"Case {i} has incorrect subcategory: {case.get('subcategory')}"

            # Test tags
            assert 'tags' in case, \
                f"Case {i} missing 'tags' field"
            assert isinstance(case['tags'], list), \
                f"Case {i} tags must be a list, got {type(case['tags'])}"

            # Test problem
            assert 'problem' in case, \
                f"Case {i} missing 'problem' field"

            # Test solution
            assert 'solution' in case, \
                f"Case {i} missing 'solution' field"

    def test_tags_content_validation(self):
        """
        Test that tags contain at least 2 items with relevant keywords.

        Each case's tags should have:
        - At least 2 tags
        - All tags are strings
        - Relevant state management keywords
        """
        from cases.webdev.webdev_state_management_cases import WEBDEV_STATE_MANAGEMENT_CASES

        # Expected relevant keywords for state management cases
        relevant_keywords = {
            'state', 'zustand', 'react-query', 'forms', 'context',
            'global', 'server', 'client', 'management', 'react'
        }

        for i, case in enumerate(WEBDEV_STATE_MANAGEMENT_CASES):
            tags = case['tags']

            # Test minimum tag count
            assert len(tags) >= 2, \
                f"Case {i} must have at least 2 tags, found {len(tags)}"

            # Test that all tags are strings
            for j, tag in enumerate(tags):
                assert isinstance(tag, str), \
                    f"Case {i} tag[{j}] must be a string, got {type(tag)}"

            # Test that tags contain relevant keywords
            tags_lower = [tag.lower() for tag in tags]
            tags_text = ' '.join(tags_lower)

            has_relevant_keyword = any(
                keyword in tags_text for keyword in relevant_keywords
            )

            assert has_relevant_keyword, \
                f"Case {i} tags should contain relevant state management keywords. " \
                f"Found tags: {tags}"

    def test_required_fields_non_empty(self):
        """
        Test that problem and solution fields have actual content.

        Verifies that:
        - problem is a non-empty string
        - solution is a non-empty string
        - Both have substantial content (> 10 characters)
        """
        from cases.webdev.webdev_state_management_cases import WEBDEV_STATE_MANAGEMENT_CASES

        for i, case in enumerate(WEBDEV_STATE_MANAGEMENT_CASES):
            # Test problem field
            problem = case['problem']
            assert isinstance(problem, str), \
                f"Case {i} problem must be a string, got {type(problem)}"
            assert len(problem.strip()) > 0, \
                f"Case {i} problem cannot be empty"
            assert len(problem.strip()) > 10, \
                f"Case {i} problem seems too short: {len(problem)} characters"

            # Test solution field
            solution = case['solution']
            assert isinstance(solution, str), \
                f"Case {i} solution must be a string, got {type(solution)}"
            assert len(solution.strip()) > 0, \
                f"Case {i} solution cannot be empty"
            assert len(solution.strip()) > 10, \
                f"Case {i} solution seems too short: {len(solution)} characters"

    def test_content_preservation_zustand_case(self):
        """
        Test that the Zustand global state case content is preserved from original.

        Verifies that the Zustand case:
        - Can be identified by problem description
        - Contains expected problem content
        - Contains expected solution content (Zustand store implementation)
        """
        from cases.webdev.webdev_state_management_cases import WEBDEV_STATE_MANAGEMENT_CASES

        # Find the Zustand case
        zustand_case = None
        for case in WEBDEV_STATE_MANAGEMENT_CASES:
            problem_lower = case['problem'].lower()
            if 'zustand' in problem_lower or 'global state' in problem_lower:
                zustand_case = case
                break

        assert zustand_case is not None, \
            "Could not find Zustand global state case"

        # Verify problem content
        problem = zustand_case['problem']
        assert 'state' in problem.lower(), \
            "Zustand case problem should mention state management"

        # Verify solution contains Zustand implementation patterns
        solution = zustand_case['solution']
        assert 'zustand' in solution.lower() or 'create' in solution.lower(), \
            "Zustand case solution should contain Zustand store patterns"

    def test_content_preservation_react_query_case(self):
        """
        Test that the React Query server state case content is preserved.

        Verifies that the React Query case:
        - Can be identified by problem description
        - Contains server state management concepts
        - Contains useQuery/useMutation patterns
        """
        from cases.webdev.webdev_state_management_cases import WEBDEV_STATE_MANAGEMENT_CASES

        # Find the React Query case
        react_query_case = None
        for case in WEBDEV_STATE_MANAGEMENT_CASES:
            problem_lower = case['problem'].lower()
            solution_lower = case['solution'].lower()
            if ('react query' in problem_lower or 'react query' in solution_lower or
                'server state' in problem_lower or 'usequery' in solution_lower):
                react_query_case = case
                break

        assert react_query_case is not None, \
            "Could not find React Query server state case"

        # Verify problem content
        problem = react_query_case['problem']
        assert 'state' in problem.lower() or 'data' in problem.lower(), \
            "React Query case problem should mention state or data management"

        # Verify solution contains React Query patterns
        solution = react_query_case['solution']
        solution_lower = solution.lower()
        has_react_query_pattern = (
            'usequery' in solution_lower or
            'usemutation' in solution_lower or
            'react query' in solution_lower or
            'query' in solution_lower
        )

        assert has_react_query_pattern, \
            "React Query case solution should contain React Query patterns"

    def test_content_preservation_form_state_case(self):
        """
        Test that the form state management case content is preserved.

        Verifies that the form state case:
        - Can be identified by problem description
        - Contains form state management concepts
        - Contains form handling patterns
        """
        from cases.webdev.webdev_state_management_cases import WEBDEV_STATE_MANAGEMENT_CASES

        # Find the form state case
        form_case = None
        for case in WEBDEV_STATE_MANAGEMENT_CASES:
            problem_lower = case['problem'].lower()
            solution_lower = case['solution'].lower()
            if 'form' in problem_lower or 'form' in solution_lower:
                form_case = case
                break

        assert form_case is not None, \
            "Could not find form state management case"

        # Verify problem content
        problem = form_case['problem']
        assert 'form' in problem.lower() or 'state' in problem.lower(), \
            "Form case problem should mention forms or state management"

        # Verify solution contains form handling patterns
        solution = form_case['solution']
        solution_lower = solution.lower()
        has_form_pattern = (
            'form' in solution_lower or
            'input' in solution_lower or
            'state' in solution_lower or
            'setstate' in solution_lower
        )

        assert has_form_pattern, \
            "Form case solution should contain form handling patterns"


class TestWebdevStateManagementCasesIntegration:
    """Integration tests for webdev state management cases."""

    def test_all_cases_are_valid_dicts(self):
        """
        Test that all cases are valid dictionaries with expected structure.

        This integration test verifies the overall data structure integrity.
        """
        from cases.webdev.webdev_state_management_cases import WEBDEV_STATE_MANAGEMENT_CASES

        for i, case in enumerate(WEBDEV_STATE_MANAGEMENT_CASES):
            assert isinstance(case, dict), \
                f"Case {i} must be a dictionary, got {type(case)}"

            # Verify minimum expected keys
            required_keys = {'category', 'subcategory', 'tags', 'problem', 'solution'}
            case_keys = set(case.keys())

            missing_keys = required_keys - case_keys
            assert not missing_keys, \
                f"Case {i} missing required keys: {missing_keys}"

    def test_no_duplicate_cases(self):
        """
        Test that there are no duplicate cases based on problem content.

        Verifies that each case has unique problem content (no copy-paste errors).
        """
        from cases.webdev.webdev_state_management_cases import WEBDEV_STATE_MANAGEMENT_CASES

        problems = [case['problem'] for case in WEBDEV_STATE_MANAGEMENT_CASES]

        # Check for duplicates
        unique_problems = set(problems)
        assert len(unique_problems) == len(problems), \
            f"Found duplicate cases. Expected {len(problems)} unique problems, " \
            f"found {len(unique_problems)}"

    def test_cases_have_consistent_structure(self):
        """
        Test that all cases have the same dictionary structure.

        Verifies that all cases have the same keys (consistent structure).
        """
        from cases.webdev.webdev_state_management_cases import WEBDEV_STATE_MANAGEMENT_CASES

        if not WEBDEV_STATE_MANAGEMENT_CASES:
            pytest.skip("No cases to test")

        # Get keys from first case as reference
        reference_keys = set(WEBDEV_STATE_MANAGEMENT_CASES[0].keys())

        # Verify all other cases have the same keys
        for i, case in enumerate(WEBDEV_STATE_MANAGEMENT_CASES[1:], start=1):
            case_keys = set(case.keys())
            assert case_keys == reference_keys, \
                f"Case {i} has different keys than Case 0. " \
                f"Difference: {case_keys.symmetric_difference(reference_keys)}"
