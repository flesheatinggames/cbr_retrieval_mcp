"""
Tests for webdev_deployment_cases module.

This test suite validates the web development deployment cases module,
ensuring proper structure, metadata, and content for deployment configuration
examples (Vercel, environment variables, production builds).
"""

import pytest


class TestModuleImport:
    """Test suite for module import validation."""

    def test_module_can_be_imported(self):
        """
        Test that cases.webdev.webdev_deployment_cases can be imported successfully.

        This verifies the module exists and has no import-time errors.
        """
        try:
            import cases.webdev.webdev_deployment_cases
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import module: {e}")


class TestCaseListVariable:
    """Test suite for WEBDEV_DEPLOYMENT_CASES variable validation."""

    def test_case_list_variable_exists(self):
        """
        Test that WEBDEV_DEPLOYMENT_CASES variable exists in the module.

        This verifies the expected export is present.
        """
        import cases.webdev.webdev_deployment_cases as module
        assert hasattr(module, "WEBDEV_DEPLOYMENT_CASES"), \
            "Module must export WEBDEV_DEPLOYMENT_CASES variable"

    def test_case_list_is_list_type(self):
        """
        Test that WEBDEV_DEPLOYMENT_CASES is a list.

        This verifies the variable has the correct type.
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES
        assert isinstance(WEBDEV_DEPLOYMENT_CASES, list), \
            "WEBDEV_DEPLOYMENT_CASES must be a list"

    def test_case_list_contains_exactly_two_cases(self):
        """
        Test that WEBDEV_DEPLOYMENT_CASES contains exactly 2 cases.

        This verifies the expected number of deployment cases are present
        (e.g., Vercel config and environment variables).
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES
        assert len(WEBDEV_DEPLOYMENT_CASES) == 2, \
            f"Expected 2 cases, found {len(WEBDEV_DEPLOYMENT_CASES)}"


class TestRequiredFields:
    """Test suite for required case fields validation."""

    def test_all_cases_have_problem_field(self):
        """
        Test that all cases have a 'problem' field.

        This verifies each case includes the problem description.
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES
        for i, case in enumerate(WEBDEV_DEPLOYMENT_CASES):
            assert "problem" in case, \
                f"Case {i} missing 'problem' field"

    def test_all_cases_have_solution_field(self):
        """
        Test that all cases have a 'solution' field.

        This verifies each case includes the solution code.
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES
        for i, case in enumerate(WEBDEV_DEPLOYMENT_CASES):
            assert "solution" in case, \
                f"Case {i} missing 'solution' field"

    def test_all_problem_fields_are_non_empty_strings(self):
        """
        Test that all 'problem' fields contain non-empty string content.

        This verifies problem descriptions are properly populated.
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES
        for i, case in enumerate(WEBDEV_DEPLOYMENT_CASES):
            assert isinstance(case["problem"], str), \
                f"Case {i} 'problem' field must be a string"
            assert len(case["problem"].strip()) > 0, \
                f"Case {i} 'problem' field must not be empty"

    def test_all_solution_fields_are_non_empty_strings(self):
        """
        Test that all 'solution' fields contain non-empty string content.

        This verifies solution code is properly populated.
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES
        for i, case in enumerate(WEBDEV_DEPLOYMENT_CASES):
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
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES
        for i, case in enumerate(WEBDEV_DEPLOYMENT_CASES):
            assert "category" in case, \
                f"Case {i} missing 'category' field"
            assert case["category"] == "webdev", \
                f"Case {i} must have category='webdev', found '{case['category']}'"

    def test_all_cases_have_subcategory_deployment(self):
        """
        Test that all cases have subcategory='deployment'.

        This verifies cases are properly subcategorized as deployment.
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES
        for i, case in enumerate(WEBDEV_DEPLOYMENT_CASES):
            assert "subcategory" in case, \
                f"Case {i} missing 'subcategory' field"
            assert case["subcategory"] == "deployment", \
                f"Case {i} must have subcategory='deployment', found '{case['subcategory']}'"

    def test_all_cases_have_tags_list(self):
        """
        Test that all cases have a 'tags' field that is a list.

        This verifies tags are present and properly typed.
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES
        for i, case in enumerate(WEBDEV_DEPLOYMENT_CASES):
            assert "tags" in case, \
                f"Case {i} missing 'tags' field"
            assert isinstance(case["tags"], list), \
                f"Case {i} 'tags' field must be a list"

    def test_all_cases_have_at_least_two_tags(self):
        """
        Test that all cases have at least 2 tags.

        This verifies adequate tagging for searchability.
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES
        for i, case in enumerate(WEBDEV_DEPLOYMENT_CASES):
            assert len(case["tags"]) >= 2, \
                f"Case {i} must have at least 2 tags, found {len(case['tags'])}"

    def test_tags_contain_relevant_deployment_keywords(self):
        """
        Test that tags contain relevant deployment keywords.

        This verifies tags are meaningful for deployment cases.
        Expected keywords: vercel, deployment, environment, config, production,
        env, nextjs, build, ci-cd, docker, aws, hosting
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES

        relevant_keywords = {
            "vercel", "deployment", "deploy", "environment", "config",
            "production", "env", "nextjs", "build", "ci-cd", "ci",
            "docker", "aws", "hosting", "server", "static", "ssr",
            "edge", "cdn", "variables", "secrets", ".env"
        }

        for i, case in enumerate(WEBDEV_DEPLOYMENT_CASES):
            tags_lower = [tag.lower() for tag in case["tags"]]
            has_relevant_tag = any(
                keyword in tag for tag in tags_lower for keyword in relevant_keywords
            )
            assert has_relevant_tag, \
                f"Case {i} should have at least one deployment-related tag from {relevant_keywords}, found {case['tags']}"


class TestContentPreservation:
    """Test suite for content preservation and deployment scenario coverage."""

    def test_vercel_deployment_case_exists(self):
        """
        Test that a case about Vercel deployment configuration exists.

        This verifies content for Vercel deployment examples
        (vercel.json, build settings, deployment configuration).
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES

        vercel_keywords = [
            "vercel", "vercel.json", "deployment", "build command",
            "output directory", "framework", "next.js deployment"
        ]

        vercel_case_found = False
        for case in WEBDEV_DEPLOYMENT_CASES:
            problem_lower = case["problem"].lower()
            solution_lower = case["solution"].lower()

            # Check if this case is about Vercel deployment
            if any(keyword in problem_lower or keyword in solution_lower
                   for keyword in vercel_keywords):
                vercel_case_found = True
                # Verify solution contains Vercel configuration patterns
                assert any(pattern in solution_lower for pattern in ["vercel", "build", "deploy", "production"]), \
                    "Vercel case must contain deployment configuration"
                break

        assert vercel_case_found, \
            "Must have a case about Vercel deployment configuration"

    def test_environment_variables_case_exists(self):
        """
        Test that a case about environment variable configuration exists.

        This verifies content for environment variable examples
        (.env files, process.env, configuration management).
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES

        env_keywords = [
            "environment variable", "env", ".env", "process.env",
            "environment config", "secrets", "api key", "configuration",
            "dotenv", "env.local", "env.production"
        ]

        env_case_found = False
        for case in WEBDEV_DEPLOYMENT_CASES:
            problem_lower = case["problem"].lower()
            solution_lower = case["solution"].lower()

            # Check if this case is about environment variables
            if any(keyword in problem_lower or keyword in solution_lower
                   for keyword in env_keywords):
                env_case_found = True
                # Verify solution contains environment variable patterns
                assert any(pattern in solution_lower for pattern in ["env", "process.env", "variable", "config"]), \
                    "Environment variable case must contain env configuration"
                break

        assert env_case_found, \
            "Must have a case about environment variable configuration"

    def test_cases_have_distinct_problems(self):
        """
        Test that the two cases address distinct problems.

        This verifies that cases are not duplicates and cover different
        deployment scenarios (e.g., one Vercel config, one env vars).
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES

        assert len(WEBDEV_DEPLOYMENT_CASES) == 2, \
            "Expected exactly 2 cases"

        problem_0 = WEBDEV_DEPLOYMENT_CASES[0]["problem"].strip()
        problem_1 = WEBDEV_DEPLOYMENT_CASES[1]["problem"].strip()

        assert problem_0 != problem_1, \
            "Cases 0 and 1 must have distinct problem descriptions"


class TestCodeQuality:
    """Test suite for solution code quality validation."""

    def test_solutions_contain_deployment_patterns(self):
        """
        Test that solutions contain actual deployment code patterns.

        This verifies that solutions include deployment configurations,
        environment variables, or build settings.
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES

        deployment_patterns = [
            "vercel", "build", "deploy", "production", "environment",
            "env", "config", ".env", "process.env", "NEXT_PUBLIC",
            "API_KEY", "DATABASE_URL", "NODE_ENV", "PORT"
        ]

        for i, case in enumerate(WEBDEV_DEPLOYMENT_CASES):
            solution_lower = case["solution"].lower()
            has_deployment_pattern = any(pattern.lower() in solution_lower
                                        for pattern in deployment_patterns)
            assert has_deployment_pattern, \
                f"Case {i} solution should contain deployment patterns (vercel/env/config/build)"

    def test_solutions_contain_configuration_files_or_code(self):
        """
        Test that at least one solution contains configuration file examples or code.

        This verifies that deployment examples include actual config files
        (vercel.json, .env examples, or deployment code).
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES

        config_patterns = [
            "vercel.json", ".env", "json", "{", "module.exports",
            "export default", "const", "process.env", "buildCommand",
            "outputDirectory", "framework", "routes", "headers"
        ]

        has_config = False
        for case in WEBDEV_DEPLOYMENT_CASES:
            solution = case["solution"]
            if any(pattern in solution for pattern in config_patterns):
                has_config = True
                break

        assert has_config, \
            "At least one case should contain configuration file examples or deployment code"

    def test_solutions_are_substantial_code_examples(self):
        """
        Test that solutions contain substantial code (not just snippets).

        This verifies that deployment examples provide complete,
        usable configurations.
        """
        from cases.webdev.webdev_deployment_cases import WEBDEV_DEPLOYMENT_CASES

        for i, case in enumerate(WEBDEV_DEPLOYMENT_CASES):
            # Substantial code should be at least 500 characters
            assert len(case["solution"]) >= 500, \
                f"Case {i} solution should be a substantial code example (>= 500 chars), found {len(case['solution'])} chars"
