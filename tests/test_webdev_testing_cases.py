"""
Tests for webdev_testing_cases module.

This test suite validates the web development testing cases module,
ensuring proper structure, metadata, and content for Jest and React Testing Library
code examples.
"""

import pytest


class TestModuleImport:
    """Test suite for module import validation."""

    def test_module_can_be_imported(self):
        """
        Test that cases.webdev.webdev_testing_cases can be imported successfully.

        This verifies the module exists and has no import-time errors.
        """
        try:
            import cases.webdev.webdev_testing_cases
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import module: {e}")


class TestCaseListVariable:
    """Test suite for WEBDEV_TESTING_CASES variable validation."""

    def test_case_list_variable_exists(self):
        """
        Test that WEBDEV_TESTING_CASES variable exists in the module.

        This verifies the expected export is present.
        """
        import cases.webdev.webdev_testing_cases as module
        assert hasattr(module, "WEBDEV_TESTING_CASES"), \
            "Module must export WEBDEV_TESTING_CASES variable"

    def test_case_list_is_list_type(self):
        """
        Test that WEBDEV_TESTING_CASES is a list.

        This verifies the variable has the correct type.
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES
        assert isinstance(WEBDEV_TESTING_CASES, list), \
            "WEBDEV_TESTING_CASES must be a list"

    def test_case_list_contains_exactly_two_cases(self):
        """
        Test that WEBDEV_TESTING_CASES contains exactly 2 cases.

        This verifies the expected number of testing cases are present
        (Jest unit tests and React Testing Library examples).
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES
        assert len(WEBDEV_TESTING_CASES) == 2, \
            f"Expected 2 cases, found {len(WEBDEV_TESTING_CASES)}"


class TestRequiredFields:
    """Test suite for required case fields validation."""

    def test_all_cases_have_problem_field(self):
        """
        Test that all cases have a 'problem' field.

        This verifies each case includes the problem description.
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES
        for i, case in enumerate(WEBDEV_TESTING_CASES):
            assert "problem" in case, \
                f"Case {i} missing 'problem' field"

    def test_all_cases_have_solution_field(self):
        """
        Test that all cases have a 'solution' field.

        This verifies each case includes the solution code.
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES
        for i, case in enumerate(WEBDEV_TESTING_CASES):
            assert "solution" in case, \
                f"Case {i} missing 'solution' field"

    def test_all_problem_fields_are_non_empty_strings(self):
        """
        Test that all 'problem' fields contain non-empty string content.

        This verifies problem descriptions are properly populated.
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES
        for i, case in enumerate(WEBDEV_TESTING_CASES):
            assert isinstance(case["problem"], str), \
                f"Case {i} 'problem' field must be a string"
            assert len(case["problem"].strip()) > 0, \
                f"Case {i} 'problem' field must not be empty"

    def test_all_solution_fields_are_non_empty_strings(self):
        """
        Test that all 'solution' fields contain non-empty string content.

        This verifies solution code is properly populated.
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES
        for i, case in enumerate(WEBDEV_TESTING_CASES):
            assert isinstance(case["solution"], str), \
                f"Case {i} 'solution' field must be a string"
            assert len(case["solution"].strip()) > 0, \
                f"Case {i} 'solution' field must not be empty"


class TestMetadataValidation:
    """Test suite for metadata field validation."""

    def test_all_cases_have_category_webdev(self):
        """
        Test that all cases have category='webdev'.

        This verifies cases are properly categorized as web development.
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES
        for i, case in enumerate(WEBDEV_TESTING_CASES):
            assert "category" in case, \
                f"Case {i} missing 'category' field"
            assert case["category"] == "webdev", \
                f"Case {i} must have category='webdev', found '{case['category']}'"

    def test_all_cases_have_subcategory_testing(self):
        """
        Test that all cases have subcategory='testing'.

        This verifies cases are properly subcategorized as testing examples.
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES
        for i, case in enumerate(WEBDEV_TESTING_CASES):
            assert "subcategory" in case, \
                f"Case {i} missing 'subcategory' field"
            assert case["subcategory"] == "testing", \
                f"Case {i} must have subcategory='testing', found '{case['subcategory']}'"

    def test_all_cases_have_tags_list(self):
        """
        Test that all cases have a 'tags' field that is a list.

        This verifies tags are present and properly typed.
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES
        for i, case in enumerate(WEBDEV_TESTING_CASES):
            assert "tags" in case, \
                f"Case {i} missing 'tags' field"
            assert isinstance(case["tags"], list), \
                f"Case {i} 'tags' field must be a list"

    def test_all_cases_have_at_least_two_tags(self):
        """
        Test that all cases have at least 2 tags.

        This verifies adequate tagging for searchability.
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES
        for i, case in enumerate(WEBDEV_TESTING_CASES):
            assert len(case["tags"]) >= 2, \
                f"Case {i} must have at least 2 tags, found {len(case['tags'])}"

    def test_tags_contain_relevant_testing_keywords(self):
        """
        Test that tags contain relevant testing keywords.

        This verifies tags are meaningful for testing cases.
        Expected keywords: jest, testing-library, unit-tests, mocking, assertions,
        test, spec, describe, it, expect, react, component
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES

        relevant_keywords = {
            "jest", "testing-library", "unit-tests", "unit-test", "mocking", "mock",
            "assertions", "assert", "test", "testing", "spec", "describe", "it",
            "expect", "react", "component", "rtl", "fireEvent", "render", "screen",
            "waitFor", "hooks", "integration", "snapshot"
        }

        for i, case in enumerate(WEBDEV_TESTING_CASES):
            tags_lower = [tag.lower() for tag in case["tags"]]
            has_relevant_tag = any(
                keyword in tag for tag in tags_lower for keyword in relevant_keywords
            )
            assert has_relevant_tag, \
                f"Case {i} should have at least one testing-related tag from {relevant_keywords}, found {case['tags']}"


class TestContentPreservation:
    """Test suite for content preservation and testing scenario coverage."""

    def test_jest_unit_test_case_exists(self):
        """
        Test that a case about Jest unit testing exists.

        This verifies content for Jest unit test examples
        (testing functions, mocking, assertions, describe/it blocks).
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES

        jest_keywords = [
            "jest", "describe", "it(", "test(", "expect",
            "unit test", "mock", "spy", "toBe", "toEqual"
        ]

        jest_case_found = False
        for case in WEBDEV_TESTING_CASES:
            problem_lower = case["problem"].lower()
            solution_lower = case["solution"].lower()

            # Check if this case is about Jest unit testing
            if any(keyword in problem_lower or keyword in solution_lower
                   for keyword in jest_keywords):
                jest_case_found = True
                # Verify solution contains Jest test patterns
                assert any(pattern in solution_lower for pattern in ["describe(", "it(", "test(", "expect("]), \
                    "Jest case must contain test block patterns (describe/it/test/expect)"
                break

        assert jest_case_found, \
            "Must have a case about Jest unit testing"

    def test_react_testing_library_case_exists(self):
        """
        Test that a case about React Testing Library exists.

        This verifies content for React Testing Library examples
        (render, screen, fireEvent, waitFor, user interactions).
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES

        rtl_keywords = [
            "testing-library", "react testing library", "@testing-library/react",
            "render", "screen", "fireEvent", "waitFor", "getByRole",
            "getByText", "getByTestId", "userEvent"
        ]

        rtl_case_found = False
        for case in WEBDEV_TESTING_CASES:
            problem_lower = case["problem"].lower()
            solution_lower = case["solution"].lower()

            # Check if this case is about React Testing Library
            if any(keyword in problem_lower or keyword in solution_lower
                   for keyword in rtl_keywords):
                rtl_case_found = True
                # Verify solution contains RTL patterns
                assert any(pattern in solution_lower for pattern in ["render(", "screen.", "fireEvent", "waitFor"]), \
                    "React Testing Library case must contain RTL patterns (render/screen/fireEvent/waitFor)"
                break

        assert rtl_case_found, \
            "Must have a case about React Testing Library"

    def test_cases_have_distinct_problems(self):
        """
        Test that the two cases address distinct problems.

        This verifies that cases are not duplicates and cover different
        testing scenarios (e.g., one Jest unit test, one RTL component test).
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES

        assert len(WEBDEV_TESTING_CASES) == 2, \
            "Expected exactly 2 cases"

        problem_0 = WEBDEV_TESTING_CASES[0]["problem"].strip()
        problem_1 = WEBDEV_TESTING_CASES[1]["problem"].strip()

        assert problem_0 != problem_1, \
            "Cases 0 and 1 must have distinct problem descriptions"


class TestCodeQuality:
    """Test suite for solution code quality validation."""

    def test_solutions_contain_testing_patterns(self):
        """
        Test that solutions contain actual testing code patterns.

        This verifies that solutions include test blocks, assertions,
        or testing library functions.
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES

        testing_patterns = [
            "describe", "it(", "test(", "expect", "assert",
            "render(", "screen", "fireEvent", "waitFor",
            "jest.fn", "jest.mock", "beforeEach", "afterEach"
        ]

        for i, case in enumerate(WEBDEV_TESTING_CASES):
            solution_lower = case["solution"].lower()
            has_testing_pattern = any(pattern.lower() in solution_lower
                                      for pattern in testing_patterns)
            assert has_testing_pattern, \
                f"Case {i} solution should contain testing patterns (describe/it/expect/render/etc.)"

    def test_solutions_contain_jest_or_rtl_imports(self):
        """
        Test that at least one solution contains Jest or RTL import statements.

        This verifies that testing examples include proper imports.
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES

        import_patterns = [
            "import", "from '@testing-library", "from 'jest'",
            "require('@testing-library", "require('jest')",
            "@testing-library/react", "@testing-library/jest-dom"
        ]

        has_testing_imports = False
        for case in WEBDEV_TESTING_CASES:
            solution_lower = case["solution"].lower()
            if any(pattern.lower() in solution_lower for pattern in import_patterns):
                has_testing_imports = True
                break

        assert has_testing_imports, \
            "At least one case should contain testing library imports"

    def test_solutions_are_substantial_code_examples(self):
        """
        Test that solutions contain substantial code (not just snippets).

        This verifies that testing examples provide complete,
        usable test implementations.
        """
        from cases.webdev.webdev_testing_cases import WEBDEV_TESTING_CASES

        for i, case in enumerate(WEBDEV_TESTING_CASES):
            # Substantial code should be at least 500 characters
            assert len(case["solution"]) >= 500, \
                f"Case {i} solution should be a substantial code example (>= 500 chars), found {len(case['solution'])} chars"
