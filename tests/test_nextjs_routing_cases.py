"""
Test suite for cases.nextjs.nextjs_routing_cases module.

This test suite validates the structure, metadata, and content of Next.js routing cases
extracted from the legacy case_base.py file. Tests follow TDD approach and will fail
until the nextjs_routing_cases.py module is properly implemented.
"""

import pytest
from typing import Dict, List, Any


class TestModuleStructure:
    """Tests for module existence and basic structure."""

    def test_module_exists(self):
        """Test that the cases.nextjs.nextjs_routing_cases module can be imported."""
        try:
            import cases.nextjs.nextjs_routing_cases
        except ImportError as e:
            pytest.fail(f"Failed to import cases.nextjs.nextjs_routing_cases: {e}")

    def test_cases_list_exists(self):
        """Test that NEXTJS_ROUTING_CASES list exists in the module."""
        from cases.nextjs import nextjs_routing_cases

        assert hasattr(nextjs_routing_cases, 'NEXTJS_ROUTING_CASES'), \
            "Module must define NEXTJS_ROUTING_CASES list"

    def test_cases_list_length(self):
        """Test that NEXTJS_ROUTING_CASES contains exactly 4 cases."""
        from cases.nextjs.nextjs_routing_cases import NEXTJS_ROUTING_CASES

        assert len(NEXTJS_ROUTING_CASES) == 4, \
            f"Expected 4 cases, found {len(NEXTJS_ROUTING_CASES)}"

    def test_all_cases_are_dicts(self):
        """Test that each case in the list is a dictionary."""
        from cases.nextjs.nextjs_routing_cases import NEXTJS_ROUTING_CASES

        for idx, case in enumerate(NEXTJS_ROUTING_CASES):
            assert isinstance(case, dict), \
                f"Case at index {idx} must be a dictionary, got {type(case)}"


class TestRequiredFields:
    """Tests for required fields in each case."""

    @pytest.fixture
    def cases(self):
        """Fixture to provide NEXTJS_ROUTING_CASES for testing."""
        from cases.nextjs.nextjs_routing_cases import NEXTJS_ROUTING_CASES
        return NEXTJS_ROUTING_CASES

    def test_problem_field_exists(self, cases: List[Dict[str, Any]]):
        """Test that each case has a 'problem' field."""
        for idx, case in enumerate(cases):
            assert "problem" in case, \
                f"Case at index {idx} missing 'problem' field"

    def test_problem_field_is_string(self, cases: List[Dict[str, Any]]):
        """Test that 'problem' field is a string."""
        for idx, case in enumerate(cases):
            assert isinstance(case["problem"], str), \
                f"Case at index {idx} 'problem' field must be string, got {type(case['problem'])}"

    def test_problem_field_not_empty(self, cases: List[Dict[str, Any]]):
        """Test that 'problem' field is non-empty."""
        for idx, case in enumerate(cases):
            assert len(case["problem"]) > 0, \
                f"Case at index {idx} 'problem' field must not be empty"

    def test_solution_field_exists(self, cases: List[Dict[str, Any]]):
        """Test that each case has a 'solution' field."""
        for idx, case in enumerate(cases):
            assert "solution" in case, \
                f"Case at index {idx} missing 'solution' field"

    def test_solution_field_is_string(self, cases: List[Dict[str, Any]]):
        """Test that 'solution' field is a string."""
        for idx, case in enumerate(cases):
            assert isinstance(case["solution"], str), \
                f"Case at index {idx} 'solution' field must be string, got {type(case['solution'])}"

    def test_solution_field_not_empty(self, cases: List[Dict[str, Any]]):
        """Test that 'solution' field is non-empty."""
        for idx, case in enumerate(cases):
            assert len(case["solution"]) > 0, \
                f"Case at index {idx} 'solution' field must not be empty"

    def test_category_field_exists(self, cases: List[Dict[str, Any]]):
        """Test that each case has a 'category' field."""
        for idx, case in enumerate(cases):
            assert "category" in case, \
                f"Case at index {idx} missing 'category' field"

    def test_category_equals_nextjs(self, cases: List[Dict[str, Any]]):
        """Test that 'category' field equals 'nextjs'."""
        for idx, case in enumerate(cases):
            assert case["category"] == "nextjs", \
                f"Case at index {idx} 'category' must be 'nextjs', got '{case['category']}'"

    def test_subcategory_field_exists(self, cases: List[Dict[str, Any]]):
        """Test that each case has a 'subcategory' field."""
        for idx, case in enumerate(cases):
            assert "subcategory" in case, \
                f"Case at index {idx} missing 'subcategory' field"

    def test_subcategory_equals_routing(self, cases: List[Dict[str, Any]]):
        """Test that 'subcategory' field equals 'routing'."""
        for idx, case in enumerate(cases):
            assert case["subcategory"] == "routing", \
                f"Case at index {idx} 'subcategory' must be 'routing', got '{case['subcategory']}'"

    def test_tags_field_exists(self, cases: List[Dict[str, Any]]):
        """Test that each case has a 'tags' field."""
        for idx, case in enumerate(cases):
            assert "tags" in case, \
                f"Case at index {idx} missing 'tags' field"

    def test_tags_field_is_list(self, cases: List[Dict[str, Any]]):
        """Test that 'tags' field is a list."""
        for idx, case in enumerate(cases):
            assert isinstance(case["tags"], list), \
                f"Case at index {idx} 'tags' field must be list, got {type(case['tags'])}"

    def test_tags_field_not_empty(self, cases: List[Dict[str, Any]]):
        """Test that 'tags' list is non-empty."""
        for idx, case in enumerate(cases):
            assert len(case["tags"]) > 0, \
                f"Case at index {idx} 'tags' list must not be empty"

    def test_tags_contain_strings(self, cases: List[Dict[str, Any]]):
        """Test that all tags are strings."""
        for idx, case in enumerate(cases):
            assert all(isinstance(tag, str) for tag in case["tags"]), \
                f"Case at index {idx} all tags must be strings"


class TestMetadataCompleteness:
    """Tests for metadata completeness and correctness."""

    @pytest.fixture
    def cases(self):
        """Fixture to provide NEXTJS_ROUTING_CASES for testing."""
        from cases.nextjs.nextjs_routing_cases import NEXTJS_ROUTING_CASES
        return NEXTJS_ROUTING_CASES

    def test_all_required_fields_present(self, cases: List[Dict[str, Any]]):
        """Test that all cases have all required fields."""
        required_fields = {"problem", "solution", "category", "subcategory", "tags"}

        for idx, case in enumerate(cases):
            case_keys = set(case.keys())
            missing_fields = required_fields - case_keys

            assert not missing_fields, \
                f"Case at index {idx} missing required fields: {missing_fields}"

    def test_tags_include_nextjs(self, cases: List[Dict[str, Any]]):
        """Test that tags include 'nextjs' keyword."""
        for idx, case in enumerate(cases):
            tags_lower = [tag.lower() for tag in case["tags"]]
            assert "nextjs" in tags_lower, \
                f"Case at index {idx} must include 'nextjs' tag"

    def test_tags_include_routing(self, cases: List[Dict[str, Any]]):
        """Test that tags include 'routing' keyword."""
        for idx, case in enumerate(cases):
            tags_lower = [tag.lower() for tag in case["tags"]]
            assert "routing" in tags_lower, \
                f"Case at index {idx} must include 'routing' tag"


class TestCaseContent:
    """Tests for specific case content based on case_base.py analysis."""

    @pytest.fixture
    def cases(self):
        """Fixture to provide NEXTJS_ROUTING_CASES for testing."""
        from cases.nextjs.nextjs_routing_cases import NEXTJS_ROUTING_CASES
        return NEXTJS_ROUTING_CASES

    def test_case1_app_router_navigation(self, cases: List[Dict[str, Any]]):
        """Test that first case is about Next.js App Router navigation."""
        case = cases[0]

        # Check problem contains relevant keywords
        problem_lower = case["problem"].lower()
        assert any(keyword in problem_lower for keyword in ["app router", "navigation", "link", "navigate"]), \
            "Case 1 problem must be about App Router navigation"

        # Check solution contains relevant keywords
        solution_lower = case["solution"].lower()
        assert any(keyword in solution_lower for keyword in ["app router", "link", "next/link", "navigation"]), \
            "Case 1 solution must include App Router navigation implementation"

        # Check tags include relevant keywords
        tags_lower = [tag.lower() for tag in case["tags"]]
        assert any(keyword in tags_lower for keyword in ["app-router", "navigation", "link"]), \
            "Case 1 tags must include App Router or navigation keywords"

    def test_case2_dynamic_routes(self, cases: List[Dict[str, Any]]):
        """Test that second case is about Dynamic Routes."""
        case = cases[1]

        # Check problem contains relevant keywords
        problem_lower = case["problem"].lower()
        assert any(keyword in problem_lower for keyword in ["dynamic", "route", "param", "[id]", "slug"]), \
            "Case 2 problem must be about Dynamic Routes"

        # Check solution contains relevant keywords
        solution_lower = case["solution"].lower()
        assert any(keyword in solution_lower for keyword in ["dynamic", "params", "[", "]", "route"]), \
            "Case 2 solution must include Dynamic Route implementation"

        # Check tags include relevant keywords
        tags_lower = [tag.lower() for tag in case["tags"]]
        assert any(keyword in tags_lower for keyword in ["dynamic", "params", "dynamic-routes"]), \
            "Case 2 tags must include Dynamic Route keywords"

    def test_case3_middleware(self, cases: List[Dict[str, Any]]):
        """Test that third case is about Middleware."""
        case = cases[2]

        # Check problem contains relevant keywords
        problem_lower = case["problem"].lower()
        assert any(keyword in problem_lower for keyword in ["middleware", "request", "intercept", "edge"]), \
            "Case 3 problem must be about Middleware"

        # Check solution contains relevant keywords
        solution_lower = case["solution"].lower()
        assert any(keyword in solution_lower for keyword in ["middleware", "nextrequest", "nextresponse", "edge"]), \
            "Case 3 solution must include Middleware implementation"

        # Check tags include relevant keywords
        tags_lower = [tag.lower() for tag in case["tags"]]
        assert any(keyword in tags_lower for keyword in ["middleware", "edge", "request"]), \
            "Case 3 tags must include Middleware keywords"


class TestDynamicLoaderIntegration:
    """Tests for dynamic loader integration."""

    def test_module_importable_via_cases_package(self):
        """Test that the module can be imported via cases.nextjs.nextjs_routing_cases."""
        try:
            from cases.nextjs import nextjs_routing_cases
            assert hasattr(nextjs_routing_cases, 'NEXTJS_ROUTING_CASES'), \
                "Module must be importable and define NEXTJS_ROUTING_CASES"
        except ImportError as e:
            pytest.fail(f"Failed to import via cases.nextjs package: {e}")

    def test_dynamic_loader_can_discover_module(self):
        """Test that the dynamic loader can discover this module."""
        import importlib
        import pkgutil

        # Check that cases.nextjs package exists
        try:
            import cases.nextjs
        except ImportError:
            pytest.fail("cases.nextjs package does not exist")

        # Check that nextjs_routing_cases is discoverable in the package
        module_found = False
        for importer, modname, ispkg in pkgutil.iter_modules(cases.nextjs.__path__, prefix='cases.nextjs.'):
            if modname == 'cases.nextjs.nextjs_routing_cases':
                module_found = True
                break

        assert module_found, \
            "nextjs_routing_cases module not discoverable by dynamic loader"
