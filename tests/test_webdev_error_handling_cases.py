"""
Tests for webdev_error_handling_cases module.

This test suite validates the web development error handling cases module,
ensuring proper structure, metadata, and content preservation from the original
case_base.py file.
"""

import pytest


class TestModuleImport:
    """Test suite for module import validation."""

    def test_module_can_be_imported(self):
        """
        Test that cases.webdev.webdev_error_handling_cases can be imported successfully.

        This verifies the module exists and has no import-time errors.
        """
        try:
            import cases.webdev.webdev_error_handling_cases

            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import module: {e}")


class TestCaseListVariable:
    """Test suite for WEBDEV_ERROR_HANDLING_CASES variable validation."""

    def test_case_list_variable_exists(self):
        """
        Test that WEBDEV_ERROR_HANDLING_CASES variable exists in the module.

        This verifies the expected export is present.
        """
        import cases.webdev.webdev_error_handling_cases as module

        assert hasattr(
            module, "WEBDEV_ERROR_HANDLING_CASES"
        ), "Module must export WEBDEV_ERROR_HANDLING_CASES variable"

    def test_case_list_is_list_type(self):
        """
        Test that WEBDEV_ERROR_HANDLING_CASES is a list.

        This verifies the variable has the correct type.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        assert isinstance(
            WEBDEV_ERROR_HANDLING_CASES, list
        ), "WEBDEV_ERROR_HANDLING_CASES must be a list"

    def test_case_list_contains_exactly_three_cases(self):
        """
        Test that WEBDEV_ERROR_HANDLING_CASES contains exactly 3 cases.

        This verifies the expected number of error handling cases are present.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        assert (
            len(WEBDEV_ERROR_HANDLING_CASES) == 3
        ), f"Expected 3 cases, found {len(WEBDEV_ERROR_HANDLING_CASES)}"


class TestRequiredFields:
    """Test suite for required case fields validation."""

    def test_all_cases_have_problem_field(self):
        """
        Test that all cases have a 'problem' field.

        This verifies each case includes the problem description.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        for i, case in enumerate(WEBDEV_ERROR_HANDLING_CASES):
            assert "problem" in case, f"Case {i} missing 'problem' field"

    def test_all_cases_have_solution_field(self):
        """
        Test that all cases have a 'solution' field.

        This verifies each case includes the solution code.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        for i, case in enumerate(WEBDEV_ERROR_HANDLING_CASES):
            assert "solution" in case, f"Case {i} missing 'solution' field"

    def test_all_problem_fields_are_non_empty_strings(self):
        """
        Test that all 'problem' fields contain non-empty string content.

        This verifies problem descriptions are properly populated.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        for i, case in enumerate(WEBDEV_ERROR_HANDLING_CASES):
            assert isinstance(
                case["problem"], str
            ), f"Case {i} 'problem' field must be a string"
            assert (
                len(case["problem"].strip()) > 0
            ), f"Case {i} 'problem' field must not be empty"

    def test_all_solution_fields_are_non_empty_strings(self):
        """
        Test that all 'solution' fields contain non-empty string content.

        This verifies solution code is properly populated.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        for i, case in enumerate(WEBDEV_ERROR_HANDLING_CASES):
            assert isinstance(
                case["solution"], str
            ), f"Case {i} 'solution' field must be a string"
            assert (
                len(case["solution"].strip()) > 0
            ), f"Case {i} 'solution' field must not be empty"


class TestMetadataValidation:
    """Test suite for metadata field validation."""

    def test_all_cases_have_category_webdev(self):
        """
        Test that all cases have category='webdev'.

        This verifies cases are properly categorized as web development.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        for i, case in enumerate(WEBDEV_ERROR_HANDLING_CASES):
            assert "category" in case, f"Case {i} missing 'category' field"
            assert (
                case["category"] == "webdev"
            ), f"Case {i} must have category='webdev', found '{case['category']}'"

    def test_all_cases_have_subcategory_error_handling(self):
        """
        Test that all cases have subcategory='error-handling'.

        This verifies cases are properly subcategorized as error handling.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        for i, case in enumerate(WEBDEV_ERROR_HANDLING_CASES):
            assert "subcategory" in case, f"Case {i} missing 'subcategory' field"
            assert (
                case["subcategory"] == "error-handling"
            ), f"Case {i} must have subcategory='error-handling', found '{case['subcategory']}'"

    def test_all_cases_have_tags_list(self):
        """
        Test that all cases have a 'tags' field that is a list.

        This verifies tags are present and properly typed.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        for i, case in enumerate(WEBDEV_ERROR_HANDLING_CASES):
            assert "tags" in case, f"Case {i} missing 'tags' field"
            assert isinstance(
                case["tags"], list
            ), f"Case {i} 'tags' field must be a list"

    def test_all_cases_have_at_least_two_tags(self):
        """
        Test that all cases have at least 2 tags.

        This verifies adequate tagging for searchability.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        for i, case in enumerate(WEBDEV_ERROR_HANDLING_CASES):
            assert (
                len(case["tags"]) >= 2
            ), f"Case {i} must have at least 2 tags, found {len(case['tags'])}"

    def test_tags_contain_relevant_error_handling_keywords(self):
        """
        Test that tags contain relevant error handling keywords.

        This verifies tags are meaningful for error handling cases.
        Expected keywords: errors, boundaries, toast, logging, recovery, exception,
        try-catch, error-handling, notifications, monitoring
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        relevant_keywords = {
            "error",
            "errors",
            "boundary",
            "boundaries",
            "toast",
            "logging",
            "recovery",
            "exception",
            "try-catch",
            "error-handling",
            "notification",
            "notifications",
            "monitoring",
            "sentry",
            "winston",
            "react",
            "catch",
            "throw",
        }

        for i, case in enumerate(WEBDEV_ERROR_HANDLING_CASES):
            tags_lower = [tag.lower() for tag in case["tags"]]
            has_relevant_tag = any(
                keyword in tag for tag in tags_lower for keyword in relevant_keywords
            )
            assert (
                has_relevant_tag
            ), f"Case {i} should have at least one error-handling-related tag from {relevant_keywords}, found {case['tags']}"


class TestContentPreservation:
    """Test suite for content preservation from original case_base.py."""

    def test_secure_error_logging_case_exists(self):
        """
        Test that a case about secure error handling and logging exists.

        This verifies content preservation for the secure error logging case
        from the original case_base.py (around line 3524).
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        logging_keywords = [
            "secure error handling",
            "logging",
            "winston",
            "sentry",
            "sensitive information",
            "production",
            "secure logger",
        ]

        logging_case_found = False
        for case in WEBDEV_ERROR_HANDLING_CASES:
            problem_lower = case["problem"].lower()
            solution_lower = case["solution"].lower()

            # Check if this case is about secure logging
            if any(keyword in problem_lower for keyword in logging_keywords):
                logging_case_found = True
                # Verify solution contains logging implementation
                assert any(
                    impl in solution_lower
                    for impl in ["winston", "logger", "log(", "sentry"]
                ), "Secure logging case must contain logging implementation"
                break

        assert (
            logging_case_found
        ), "Must have a case about secure error handling and logging"

    def test_react_error_boundary_case_exists(self):
        """
        Test that a case about React error boundaries exists.

        This verifies content preservation for the React error boundary case
        from the original case_base.py (around line 3943).
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        boundary_keywords = [
            "error boundary",
            "errorboundary",
            "componentdidcatch",
            "getderivedstatefromerror",
            "react error",
        ]

        boundary_case_found = False
        for case in WEBDEV_ERROR_HANDLING_CASES:
            problem_lower = case["problem"].lower()
            solution_lower = case["solution"].lower()

            # Check if this case is about error boundaries
            if any(
                keyword in problem_lower or keyword in solution_lower
                for keyword in boundary_keywords
            ):
                boundary_case_found = True
                # Verify solution contains error boundary implementation
                assert (
                    "errorboundary" in solution_lower
                    or "componentdidcatch" in solution_lower
                ), "Error boundary case must contain ErrorBoundary class or componentDidCatch"
                break

        assert boundary_case_found, "Must have a case about React error boundaries"

    def test_error_recovery_or_notification_case_exists(self):
        """
        Test that a case about error recovery, toast notifications, or user-facing errors exists.

        This verifies content preservation for error handling UI patterns.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        ui_error_keywords = [
            "toast",
            "notification",
            "alert",
            "error message",
            "user error",
            "error state",
            "error ui",
            "recovery",
            "fallback",
            "retry",
        ]

        ui_error_case_found = False
        for case in WEBDEV_ERROR_HANDLING_CASES:
            problem_lower = case["problem"].lower()
            solution_lower = case["solution"].lower()

            # Check if this case is about error UI/notifications
            if any(
                keyword in problem_lower or keyword in solution_lower
                for keyword in ui_error_keywords
            ):
                ui_error_case_found = True
                break

        assert (
            ui_error_case_found
        ), "Must have a case about error recovery, notifications, or user-facing error handling"

    def test_cases_have_distinct_problems(self):
        """
        Test that the three cases address distinct problems.

        This verifies that cases are not duplicates and cover different
        error handling scenarios.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        assert len(WEBDEV_ERROR_HANDLING_CASES) == 3, "Expected exactly 3 cases"

        problem_0 = WEBDEV_ERROR_HANDLING_CASES[0]["problem"].strip()
        problem_1 = WEBDEV_ERROR_HANDLING_CASES[1]["problem"].strip()
        problem_2 = WEBDEV_ERROR_HANDLING_CASES[2]["problem"].strip()

        assert (
            problem_0 != problem_1
        ), "Cases 0 and 1 must have distinct problem descriptions"
        assert (
            problem_0 != problem_2
        ), "Cases 0 and 2 must have distinct problem descriptions"
        assert (
            problem_1 != problem_2
        ), "Cases 1 and 2 must have distinct problem descriptions"


class TestCodeQuality:
    """Test suite for solution code quality validation."""

    def test_solutions_contain_error_handling_patterns(self):
        """
        Test that solutions contain actual error handling code patterns.

        This verifies that solutions include try/catch, error classes,
        or error handling logic.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        error_patterns = ["try", "catch", "throw", "error", "exception", "Error("]

        for i, case in enumerate(WEBDEV_ERROR_HANDLING_CASES):
            solution_lower = case["solution"].lower()
            has_error_pattern = any(
                pattern.lower() in solution_lower for pattern in error_patterns
            )
            assert (
                has_error_pattern
            ), f"Case {i} solution should contain error handling patterns (try/catch/throw/Error)"

    def test_solutions_contain_react_or_typescript_patterns(self):
        """
        Test that at least one solution contains React or TypeScript patterns.

        This verifies that error handling examples are in the expected
        web development context.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        react_ts_patterns = [
            "import",
            "export",
            "interface",
            "type",
            "const",
            "function",
            "react",
            "component",
            "usestate",
            "useeffect",
        ]

        has_react_ts = False
        for case in WEBDEV_ERROR_HANDLING_CASES:
            solution_lower = case["solution"].lower()
            if any(pattern in solution_lower for pattern in react_ts_patterns):
                has_react_ts = True
                break

        assert (
            has_react_ts
        ), "At least one case should contain React or TypeScript code patterns"

    def test_solutions_are_substantial_code_examples(self):
        """
        Test that solutions contain substantial code (not just snippets).

        This verifies that error handling examples provide complete,
        usable implementations.
        """
        from cases.webdev.webdev_error_handling_cases import WEBDEV_ERROR_HANDLING_CASES

        for i, case in enumerate(WEBDEV_ERROR_HANDLING_CASES):
            # Substantial code should be at least 500 characters
            assert (
                len(case["solution"]) >= 500
            ), f"Case {i} solution should be a substantial code example (>= 500 chars), found {len(case['solution'])} chars"
