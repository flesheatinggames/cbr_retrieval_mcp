"""
Tests for webdev_api_integration_cases module.

This test suite validates the web development API integration cases module,
ensuring proper structure, metadata, and content preservation from the original
case_base.py file.
"""

import pytest


class TestModuleImport:
    """Test suite for module import validation."""

    def test_module_can_be_imported(self):
        """
        Test that cases.webdev.webdev_api_integration_cases can be imported successfully.

        This verifies the module exists and has no import-time errors.
        """
        try:
            import cases.webdev.webdev_api_integration_cases
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import module: {e}")


class TestCaseListVariable:
    """Test suite for WEBDEV_API_INTEGRATION_CASES variable validation."""

    def test_case_list_variable_exists(self):
        """
        Test that WEBDEV_API_INTEGRATION_CASES variable exists in the module.

        This verifies the expected export is present.
        """
        import cases.webdev.webdev_api_integration_cases as module
        assert hasattr(module, "WEBDEV_API_INTEGRATION_CASES"), \
            "Module must export WEBDEV_API_INTEGRATION_CASES variable"

    def test_case_list_is_list_type(self):
        """
        Test that WEBDEV_API_INTEGRATION_CASES is a list.

        This verifies the variable has the correct type.
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES
        assert isinstance(WEBDEV_API_INTEGRATION_CASES, list), \
            "WEBDEV_API_INTEGRATION_CASES must be a list"

    def test_case_list_contains_exactly_two_cases(self):
        """
        Test that WEBDEV_API_INTEGRATION_CASES contains exactly 2 cases.

        This verifies the expected number of API integration cases are present.
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES
        assert len(WEBDEV_API_INTEGRATION_CASES) == 2, \
            f"Expected 2 cases, found {len(WEBDEV_API_INTEGRATION_CASES)}"


class TestRequiredFields:
    """Test suite for required case fields validation."""

    def test_all_cases_have_problem_field(self):
        """
        Test that all cases have a 'problem' field.

        This verifies each case includes the problem description.
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES
        for i, case in enumerate(WEBDEV_API_INTEGRATION_CASES):
            assert "problem" in case, \
                f"Case {i} missing 'problem' field"

    def test_all_cases_have_solution_field(self):
        """
        Test that all cases have a 'solution' field.

        This verifies each case includes the solution code.
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES
        for i, case in enumerate(WEBDEV_API_INTEGRATION_CASES):
            assert "solution" in case, \
                f"Case {i} missing 'solution' field"

    def test_all_problem_fields_are_non_empty_strings(self):
        """
        Test that all 'problem' fields contain non-empty string content.

        This verifies problem descriptions are properly populated.
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES
        for i, case in enumerate(WEBDEV_API_INTEGRATION_CASES):
            assert isinstance(case["problem"], str), \
                f"Case {i} 'problem' field must be a string"
            assert len(case["problem"].strip()) > 0, \
                f"Case {i} 'problem' field must not be empty"

    def test_all_solution_fields_are_non_empty_strings(self):
        """
        Test that all 'solution' fields contain non-empty string content.

        This verifies solution code is properly populated.
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES
        for i, case in enumerate(WEBDEV_API_INTEGRATION_CASES):
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
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES
        for i, case in enumerate(WEBDEV_API_INTEGRATION_CASES):
            assert "category" in case, \
                f"Case {i} missing 'category' field"
            assert case["category"] == "webdev", \
                f"Case {i} must have category='webdev', found '{case['category']}'"

    def test_all_cases_have_subcategory_api_integration(self):
        """
        Test that all cases have subcategory='api-integration'.

        This verifies cases are properly subcategorized as API integration.
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES
        for i, case in enumerate(WEBDEV_API_INTEGRATION_CASES):
            assert "subcategory" in case, \
                f"Case {i} missing 'subcategory' field"
            assert case["subcategory"] == "api-integration", \
                f"Case {i} must have subcategory='api-integration', found '{case['subcategory']}'"

    def test_all_cases_have_tags_list(self):
        """
        Test that all cases have a 'tags' field that is a list.

        This verifies tags are present and properly typed.
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES
        for i, case in enumerate(WEBDEV_API_INTEGRATION_CASES):
            assert "tags" in case, \
                f"Case {i} missing 'tags' field"
            assert isinstance(case["tags"], list), \
                f"Case {i} 'tags' field must be a list"

    def test_all_cases_have_at_least_two_tags(self):
        """
        Test that all cases have at least 2 tags.

        This verifies adequate tagging for searchability.
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES
        for i, case in enumerate(WEBDEV_API_INTEGRATION_CASES):
            assert len(case["tags"]) >= 2, \
                f"Case {i} must have at least 2 tags, found {len(case['tags'])}"

    def test_tags_contain_relevant_api_keywords(self):
        """
        Test that tags contain relevant API-related keywords.

        This verifies tags are meaningful for API integration cases.
        Expected keywords: api, fetch, async, error-handling, rest, http, axios
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES

        relevant_keywords = {
            "api", "fetch", "async", "error-handling", "rest", "http", "axios",
            "ajax", "request", "response", "endpoint", "client"
        }

        for i, case in enumerate(WEBDEV_API_INTEGRATION_CASES):
            tags_lower = [tag.lower() for tag in case["tags"]]
            has_relevant_tag = any(
                keyword in tag for tag in tags_lower for keyword in relevant_keywords
            )
            assert has_relevant_tag, \
                f"Case {i} should have at least one API-related tag from {relevant_keywords}, found {case['tags']}"


class TestContentPreservation:
    """Test suite for content preservation from original case_base.py."""

    def test_fetch_pattern_case_exists(self):
        """
        Test that a case about fetch patterns exists.

        This verifies content preservation for the fetch/REST API pattern case
        from the original case_base.py file.
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES

        fetch_keywords = ["fetch", "rest api", "api call", "http request", "get request"]

        fetch_case_found = False
        for case in WEBDEV_API_INTEGRATION_CASES:
            problem_lower = case["problem"].lower()
            if any(keyword in problem_lower for keyword in fetch_keywords):
                fetch_case_found = True
                break

        assert fetch_case_found, \
            "Must have a case about fetch patterns or REST API calls"

    def test_error_handling_case_exists(self):
        """
        Test that a case about API error handling exists.

        This verifies content preservation for the error handling case
        from the original case_base.py file.
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES

        error_keywords = ["error handling", "error", "catch", "try", "exception", "failure"]
        api_keywords = ["api", "fetch", "request", "call"]

        error_case_found = False
        for case in WEBDEV_API_INTEGRATION_CASES:
            problem_lower = case["problem"].lower()
            has_error_keyword = any(keyword in problem_lower for keyword in error_keywords)
            has_api_keyword = any(keyword in problem_lower for keyword in api_keywords)

            if has_error_keyword and has_api_keyword:
                error_case_found = True
                break

        assert error_case_found, \
            "Must have a case about API error handling"

    def test_cases_have_distinct_problems(self):
        """
        Test that the two cases address distinct problems.

        This verifies that cases are not duplicates and cover different
        API integration scenarios.
        """
        from cases.webdev.webdev_api_integration_cases import WEBDEV_API_INTEGRATION_CASES

        assert len(WEBDEV_API_INTEGRATION_CASES) == 2, \
            "Expected exactly 2 cases"

        problem_0 = WEBDEV_API_INTEGRATION_CASES[0]["problem"].strip()
        problem_1 = WEBDEV_API_INTEGRATION_CASES[1]["problem"].strip()

        assert problem_0 != problem_1, \
            "Cases must have distinct problem descriptions"
