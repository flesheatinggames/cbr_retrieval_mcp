"""
Comprehensive unit tests for orchestration_planning_cases.py module.

This test suite validates the structure, content, and metadata of Orchestration Planning
cases following TDD best practices. Tests ensure the modular case file meets all
specifications for the case-base-modular-refactoring project.

Test Coverage:
- File existence and import validation
- ORCHESTRATION_PLANNING_CASES variable structure
- Case count validation (exactly 2 cases)
- Required field presence for all cases
- Field type validation
- Field content validation (non-empty, correct values)
- Orchestration planning topic coverage
- Tag keyword validation
"""

from pathlib import Path
from typing import Any, Dict, List

import pytest


# Test Group 1: File and Module Structure
class TestFileAndModuleStructure:
    """Test suite for validating file existence and module import."""

    def test_orchestration_planning_cases_file_exists(self):
        """Verify that cases/orchestration/orchestration_planning_cases.py file exists."""
        file_path = Path("cases/orchestration/orchestration_planning_cases.py")
        assert file_path.exists(), f"Expected file not found: {file_path}"
        assert file_path.is_file(), f"Expected path to be a file: {file_path}"
        assert file_path.suffix == ".py", f"Expected .py extension: {file_path}"

    def test_orchestration_planning_cases_module_importable(self):
        """Verify that orchestration_planning_cases module can be imported without errors."""
        try:
            from cases.orchestration import orchestration_planning_cases

            assert orchestration_planning_cases is not None
        except ImportError as e:
            pytest.fail(f"Failed to import orchestration_planning_cases module: {e}")


# Test Group 2: ORCHESTRATION_PLANNING_CASES Variable Structure
class TestOrchestrationPlanningCasesVariable:
    """Test suite for validating ORCHESTRATION_PLANNING_CASES variable structure."""

    def test_orchestration_planning_cases_variable_exists(self):
        """Verify that ORCHESTRATION_PLANNING_CASES variable exists in the module."""
        from cases.orchestration import orchestration_planning_cases

        assert hasattr(
            orchestration_planning_cases, "ORCHESTRATION_PLANNING_CASES"
        ), "Module must define ORCHESTRATION_PLANNING_CASES variable"

    def test_orchestration_planning_cases_is_list(self):
        """Verify that ORCHESTRATION_PLANNING_CASES is a list."""
        from cases.orchestration.orchestration_planning_cases import (
            ORCHESTRATION_PLANNING_CASES,
        )

        assert isinstance(
            ORCHESTRATION_PLANNING_CASES, list
        ), f"ORCHESTRATION_PLANNING_CASES must be a list, got {type(ORCHESTRATION_PLANNING_CASES)}"


# Test Group 3: Case Count Validation
class TestCaseCount:
    """Test suite for validating the number of Orchestration Planning cases."""

    def test_orchestration_planning_cases_count(self):
        """Verify that ORCHESTRATION_PLANNING_CASES contains exactly 19 cases."""
        from cases.orchestration.orchestration_planning_cases import (
            ORCHESTRATION_PLANNING_CASES,
        )

        assert (
            len(ORCHESTRATION_PLANNING_CASES) == 19
        ), f"Expected exactly 19 cases, got {len(ORCHESTRATION_PLANNING_CASES)}"


# Test Group 4: Required Fields Presence
class TestRequiredFieldsPresence:
    """Test suite for validating presence of all required fields in every case."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing ORCHESTRATION_PLANNING_CASES for tests."""
        from cases.orchestration.orchestration_planning_cases import (
            ORCHESTRATION_PLANNING_CASES,
        )

        return ORCHESTRATION_PLANNING_CASES

    def test_all_cases_have_problem_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'problem' field."""
        for idx, case in enumerate(cases):
            assert "problem" in case, f"Case {idx} missing required field: problem"

    def test_all_cases_have_solution_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'solution' field."""
        for idx, case in enumerate(cases):
            assert "solution" in case, f"Case {idx} missing required field: solution"

    def test_all_cases_have_category_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'category' field."""
        for idx, case in enumerate(cases):
            assert "category" in case, f"Case {idx} missing required field: category"

    def test_all_cases_have_subcategory_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'subcategory' field."""
        for idx, case in enumerate(cases):
            assert (
                "subcategory" in case
            ), f"Case {idx} missing required field: subcategory"

    def test_all_cases_have_tags_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'tags' field."""
        for idx, case in enumerate(cases):
            assert "tags" in case, f"Case {idx} missing required field: tags"


# Test Group 5: Field Type Validation
class TestFieldTypes:
    """Test suite for validating data types of all fields."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing ORCHESTRATION_PLANNING_CASES for tests."""
        from cases.orchestration.orchestration_planning_cases import (
            ORCHESTRATION_PLANNING_CASES,
        )

        return ORCHESTRATION_PLANNING_CASES

    def test_problem_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'problem' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(
                case.get("problem"), str
            ), f'Case {idx} problem field must be str, got {type(case.get("problem"))}'

    def test_solution_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'solution' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(
                case.get("solution"), str
            ), f'Case {idx} solution field must be str, got {type(case.get("solution"))}'

    def test_category_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'category' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(
                case.get("category"), str
            ), f'Case {idx} category field must be str, got {type(case.get("category"))}'

    def test_subcategory_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'subcategory' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(
                case.get("subcategory"), str
            ), f'Case {idx} subcategory field must be str, got {type(case.get("subcategory"))}'

    def test_tags_fields_are_lists(self, cases: List[Dict[str, Any]]):
        """Verify that all 'tags' fields are lists."""
        for idx, case in enumerate(cases):
            assert isinstance(
                case.get("tags"), list
            ), f'Case {idx} tags field must be list, got {type(case.get("tags"))}'


# Test Group 6: Field Content Validation
class TestFieldContent:
    """Test suite for validating content and values of all fields."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing ORCHESTRATION_PLANNING_CASES for tests."""
        from cases.orchestration.orchestration_planning_cases import (
            ORCHESTRATION_PLANNING_CASES,
        )

        return ORCHESTRATION_PLANNING_CASES

    def test_problem_fields_non_empty(self, cases: List[Dict[str, Any]]):
        """Verify that all 'problem' fields are non-empty strings."""
        for idx, case in enumerate(cases):
            problem = case.get("problem", "")
            assert len(problem) > 0, f"Case {idx} problem field must not be empty"
            assert (
                problem.strip() != ""
            ), f"Case {idx} problem field must not be only whitespace"

    def test_solution_fields_non_empty(self, cases: List[Dict[str, Any]]):
        """Verify that all 'solution' fields are non-empty strings."""
        for idx, case in enumerate(cases):
            solution = case.get("solution", "")
            assert len(solution) > 0, f"Case {idx} solution field must not be empty"
            assert (
                solution.strip() != ""
            ), f"Case {idx} solution field must not be only whitespace"

    def test_category_equals_orchestration(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have category='orchestration'."""
        for idx, case in enumerate(cases):
            assert (
                case.get("category") == "orchestration"
            ), f'Case {idx} category must be "orchestration", got "{case.get("category")}"'

    def test_subcategory_equals_planning(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have subcategory='planning'."""
        for idx, case in enumerate(cases):
            assert (
                case.get("subcategory") == "planning"
            ), f'Case {idx} subcategory must be "planning", got "{case.get("subcategory")}"'

    def test_tags_non_empty_lists(self, cases: List[Dict[str, Any]]):
        """Verify that all 'tags' fields are non-empty lists."""
        for idx, case in enumerate(cases):
            tags = case.get("tags", [])
            assert len(tags) > 0, f"Case {idx} tags list must not be empty"

    def test_all_tags_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all elements in 'tags' lists are strings."""
        for case_idx, case in enumerate(cases):
            tags = case.get("tags", [])
            for tag_idx, tag in enumerate(tags):
                assert isinstance(
                    tag, str
                ), f"Case {case_idx} tag {tag_idx} must be str, got {type(tag)}"

    def test_problem_minimum_length(self, cases: List[Dict[str, Any]]):
        """Verify that all 'problem' fields have meaningful content (at least 20 characters)."""
        for idx, case in enumerate(cases):
            problem = case.get("problem", "")
            assert (
                len(problem.strip()) >= 20
            ), f"Case {idx} problem field must be at least 20 characters, got {len(problem.strip())}"

    def test_solution_minimum_length(self, cases: List[Dict[str, Any]]):
        """Verify that all 'solution' fields have meaningful content (at least 50 characters)."""
        for idx, case in enumerate(cases):
            solution = case.get("solution", "")
            assert (
                len(solution.strip()) >= 50
            ), f"Case {idx} solution field must be at least 50 characters, got {len(solution.strip())}"

    def test_problem_and_solution_are_distinct(self, cases: List[Dict[str, Any]]):
        """Verify that problem and solution are not identical."""
        for idx, case in enumerate(cases):
            problem = case.get("problem", "").strip()
            solution = case.get("solution", "").strip()
            assert (
                problem != solution
            ), f"Case {idx} problem and solution must be distinct"


# Test Group 7: Orchestration Planning Topic Coverage
class TestOrchestrationPlanningTopicCoverage:
    """Test suite for validating coverage of key Orchestration Planning topics."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing ORCHESTRATION_PLANNING_CASES for tests."""
        from cases.orchestration.orchestration_planning_cases import (
            ORCHESTRATION_PLANNING_CASES,
        )

        return ORCHESTRATION_PLANNING_CASES

    def _search_in_case(self, case: Dict[str, Any], keywords: List[str]) -> bool:
        """
        Helper method to search for keywords in case problem/solution fields and tags.

        Args:
            case: The case dictionary to search
            keywords: List of keywords to search for (case-insensitive)

        Returns:
            True if any keyword is found in problem, solution, or tags, False otherwise
        """
        problem_lower = case.get("problem", "").lower()
        solution_lower = case.get("solution", "").lower()
        tags_lower = [tag.lower() for tag in case.get("tags", [])]

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in problem_lower:
                return True
            if keyword_lower in solution_lower:
                return True
            if any(keyword_lower in tag for tag in tags_lower):
                return True

        return False

    def test_tdd_workflow_topic_covered(self, cases: List[Dict[str, Any]]):
        """Verify that TDD workflow topic is covered in at least one case."""
        keywords = ["tdd", "test-driven", "test driven", "testing", "test first"]
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert found, f"No case found covering TDD workflow topic. Keywords: {keywords}"

    def test_multi_agent_coordination_topic_covered(self, cases: List[Dict[str, Any]]):
        """Verify that multi-agent coordination topic is covered in at least one case."""
        keywords = [
            "agent",
            "agents",
            "orchestration",
            "orchestrator",
            "coordination",
            "delegate",
            "delegation",
        ]
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert (
            found
        ), f"No case found covering multi-agent coordination topic. Keywords: {keywords}"

    def test_cases_are_distinct(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have distinct problems."""
        problems = [case.get("problem", "").strip().lower() for case in cases]
        unique_problems = set(problems)
        assert len(unique_problems) == len(
            problems
        ), f"Cases must have distinct problems. Found {len(problems)} cases but only {len(unique_problems)} unique problems"


# Test Group 8: Orchestration/Planning Keyword Validation
class TestOrchestrationPlanningKeywords:
    """Test suite for validating presence of orchestration and planning keywords in tags."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing ORCHESTRATION_PLANNING_CASES for tests."""
        from cases.orchestration.orchestration_planning_cases import (
            ORCHESTRATION_PLANNING_CASES,
        )

        return ORCHESTRATION_PLANNING_CASES

    def test_tags_contain_planning_keywords(self, cases: List[Dict[str, Any]]):
        """Verify that each case contains at least one planning-related keyword in tags."""
        planning_keywords = [
            "tdd",
            "workflow",
            "planning",
            "agents",
            "tasks",
            "refactoring",
            "orchestration",
            "orchestrator",
            "delegation",
            "testing",
            "test-driven",
        ]

        for idx, case in enumerate(cases):
            tags_lower = [tag.lower() for tag in case.get("tags", [])]
            found_keywords = []
            for keyword in planning_keywords:
                if any(keyword in tag for tag in tags_lower):
                    found_keywords.append(keyword)

            assert (
                len(found_keywords) > 0
            ), f"Case {idx} tags must contain at least one planning keyword. Expected any of: {planning_keywords}"

    def test_tags_contain_orchestration_or_planning_base_term(
        self, cases: List[Dict[str, Any]]
    ):
        """Verify that tags across all cases contain base orchestration or planning terms."""
        base_terms = ["orchestration", "planning", "workflow", "agents"]

        all_tags_lower = []
        for case in cases:
            all_tags_lower.extend([tag.lower() for tag in case.get("tags", [])])

        found_terms = []
        for term in base_terms:
            if any(term in tag for tag in all_tags_lower):
                found_terms.append(term)

        assert (
            len(found_terms) > 0
        ), f"Tags must contain orchestration/planning base terms. Expected any of: {base_terms}"
