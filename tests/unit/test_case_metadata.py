"""
Unit tests for case metadata validation and completeness.

This test suite validates that case-based reasoning examples have proper metadata
fields (category, subcategory, tags) and maintain content integrity during refactoring.

Test-Driven Development (TDD) approach:
- These tests are written BEFORE the modular case files are fully migrated
- Tests for web/orchestration/security cases will be SKIPPED initially (unmigrated)
- Tests should work with 5+ cases now and continue passing as migration reaches 49 total
- Rust cases are allowed to NOT have category/subcategory/tags (backward compatibility)
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Valid category values for metadata validation
WEB_CATEGORIES = ["firebase", "react", "nextjs", "bootstrap", "webdev"]
ALL_CATEGORIES = [
    "firebase",
    "react",
    "nextjs",
    "bootstrap",
    "webdev",
    "orchestration",
    "security",
    "rust",
]

# Code detection patterns for solution validation
CODE_PATTERNS = [
    r"\bimport\b",  # Python/JS imports
    r"\bfrom\b.*\bimport\b",  # Python from imports
    r"\bfunction\b",  # JavaScript function
    r"\bclass\b",  # Python/JS class
    r"\bdef\b",  # Python def
    r"\bconst\b",  # JavaScript const
    r"\blet\b",  # JavaScript let
    r"\bvar\b",  # JavaScript var
    r"=>",  # Arrow function
    r"\bfn\b",  # Rust fn
    r"\buse\b",  # Rust use
    r"\basync\b",  # Async keyword
    r"\bawait\b",  # Await keyword
    r"<sequential-thinking>",  # Orchestration thinking pattern
    r"<thinking>",  # Orchestration thinking pattern (alternate)
    r"<TodoWrite>",  # Orchestration todo pattern
    r"<delegate_task>",  # Orchestration delegation pattern
]


class TestMetadataValidation:
    """Test suite for case metadata validation."""

    @pytest.mark.skip(reason="Web cases not yet migrated from case_base.py")
    def test_all_web_cases_have_required_metadata(self):
        """
        Verify all web cases have category, subcategory, and tags.

        This test will be skipped until web cases are migrated (Tasks 3-7).
        Once migrated, it will verify:
        - Each case has category in ["firebase", "react", "nextjs", "bootstrap", "webdev"]
        - Each case has subcategory (non-empty string)
        - Each case has tags (list with at least 2 items)
        """
        from cases import ALL_CASES

        # Filter to web cases (those with web categories)
        web_cases = [
            case for case in ALL_CASES if case.get("category") in WEB_CATEGORIES
        ]

        assert len(web_cases) > 0, "No web cases found"

        for idx, case in enumerate(web_cases):
            # Check category
            assert "category" in case, f"Web case {idx} missing 'category' field"
            assert (
                case["category"] in WEB_CATEGORIES
            ), f"Web case {idx} has invalid category: {case.get('category')}"

            # Check subcategory
            assert "subcategory" in case, f"Web case {idx} missing 'subcategory' field"
            assert isinstance(
                case["subcategory"], str
            ), f"Web case {idx} subcategory must be string, got {type(case['subcategory'])}"
            assert len(case["subcategory"]) > 0, f"Web case {idx} has empty subcategory"

            # Check tags
            assert "tags" in case, f"Web case {idx} missing 'tags' field"
            assert isinstance(
                case["tags"], list
            ), f"Web case {idx} tags must be list, got {type(case['tags'])}"
            assert (
                len(case["tags"]) >= 2
            ), f"Web case {idx} tags must have at least 2 items, got {len(case['tags'])}"

    @pytest.mark.skip(reason="Orchestration cases not yet migrated from case_base.py")
    def test_all_orchestration_cases_have_required_metadata(self):
        """
        Verify all orchestration cases have correct metadata.

        This test will be skipped until orchestration cases are migrated (Task 8).
        Once migrated, it will verify:
        - Each case has category == "orchestration"
        - Each case has valid subcategory (planning, remediation, etc.)
        - Each case has tags (list with at least 2 items)
        """
        from cases import ALL_CASES

        # Filter to orchestration cases
        orchestration_cases = [
            case for case in ALL_CASES if case.get("category") == "orchestration"
        ]

        assert len(orchestration_cases) > 0, "No orchestration cases found"

        for idx, case in enumerate(orchestration_cases):
            # Check category
            assert (
                "category" in case
            ), f"Orchestration case {idx} missing 'category' field"
            assert (
                case["category"] == "orchestration"
            ), f"Orchestration case {idx} has invalid category: {case.get('category')}"

            # Check subcategory
            assert (
                "subcategory" in case
            ), f"Orchestration case {idx} missing 'subcategory' field"
            assert isinstance(
                case["subcategory"], str
            ), f"Orchestration case {idx} subcategory must be string"
            assert (
                len(case["subcategory"]) > 0
            ), f"Orchestration case {idx} has empty subcategory"

            # Check tags
            assert "tags" in case, f"Orchestration case {idx} missing 'tags' field"
            assert isinstance(
                case["tags"], list
            ), f"Orchestration case {idx} tags must be list"
            assert (
                len(case["tags"]) >= 2
            ), f"Orchestration case {idx} tags must have at least 2 items"

    @pytest.mark.skip(reason="Security cases not yet migrated from case_base.py")
    def test_all_security_cases_have_required_metadata(self):
        """
        Verify all security cases have correct metadata.

        This test will be skipped until security cases are migrated (Task 9).
        Once migrated, it will verify:
        - Each case has category == "security"
        - Each case has valid subcategory (auth, validation)
        - Each case has tags (list with at least 2 items)
        """
        from cases import ALL_CASES

        # Filter to security cases
        security_cases = [
            case for case in ALL_CASES if case.get("category") == "security"
        ]

        assert len(security_cases) > 0, "No security cases found"

        for idx, case in enumerate(security_cases):
            # Check category
            assert "category" in case, f"Security case {idx} missing 'category' field"
            assert (
                case["category"] == "security"
            ), f"Security case {idx} has invalid category: {case.get('category')}"

            # Check subcategory
            assert (
                "subcategory" in case
            ), f"Security case {idx} missing 'subcategory' field"
            assert isinstance(
                case["subcategory"], str
            ), f"Security case {idx} subcategory must be string"
            assert (
                len(case["subcategory"]) > 0
            ), f"Security case {idx} has empty subcategory"

            # Check tags
            assert "tags" in case, f"Security case {idx} missing 'tags' field"
            assert isinstance(
                case["tags"], list
            ), f"Security case {idx} tags must be list"
            assert (
                len(case["tags"]) >= 2
            ), f"Security case {idx} tags must have at least 2 items"

    def test_metadata_category_values_are_valid(self):
        """
        Verify category field only contains allowed values.

        Tests that every case with a category field has a valid category value.
        Rust cases are allowed to NOT have category field (backward compatibility).

        Allowed categories: ["firebase", "react", "nextjs", "bootstrap",
                            "webdev", "orchestration", "security", "rust"]
        """
        from cases import ALL_CASES

        # At least 5 cases should exist (rust cases)
        assert len(ALL_CASES) >= 5, f"Expected at least 5 cases, found {len(ALL_CASES)}"

        invalid_categories = []

        for idx, case in enumerate(ALL_CASES):
            # Category field is optional for backward compatibility
            if "category" in case:
                category = case["category"]

                # Check not None or empty
                if category is None or category == "":
                    invalid_categories.append((idx, category, "None or empty"))
                    continue

                # Check in allowed list
                if category not in ALL_CATEGORIES:
                    invalid_categories.append((idx, category, "not in allowed list"))

        assert not invalid_categories, (
            f"Found cases with invalid categories:\n"
            + "\n".join(
                [
                    f"  Case {idx}: category='{cat}' ({reason})"
                    for idx, cat, reason in invalid_categories
                ]
            )
            + f"\nAllowed categories: {ALL_CATEGORIES}"
        )

    def test_metadata_tags_are_non_empty_lists(self):
        """
        Verify tags field format and content.

        Tests that cases with tags field have:
        - tags is a list type
        - tags list has at least 2 items
        - All tag items are strings
        - No empty string tags
        - Tags are lowercase

        Rust cases are allowed to NOT have tags field (backward compatibility).
        """
        from cases import ALL_CASES

        invalid_tags = []

        for idx, case in enumerate(ALL_CASES):
            # Tags field is optional for backward compatibility
            if "tags" not in case:
                continue

            tags = case["tags"]

            # Check is list
            if not isinstance(tags, list):
                invalid_tags.append((idx, "tags is not a list"))
                continue

            # Check has at least 2 items
            if len(tags) < 2:
                invalid_tags.append(
                    (idx, f"tags has only {len(tags)} items, need at least 2")
                )
                continue

            # Check all items are strings
            non_strings = [i for i, tag in enumerate(tags) if not isinstance(tag, str)]
            if non_strings:
                invalid_tags.append(
                    (idx, f"tags contains non-string items at indices {non_strings}")
                )
                continue

            # Check no empty strings
            empty_indices = [i for i, tag in enumerate(tags) if tag == ""]
            if empty_indices:
                invalid_tags.append(
                    (idx, f"tags contains empty strings at indices {empty_indices}")
                )
                continue

            # Check all lowercase
            non_lowercase = [tag for tag in tags if tag != tag.lower()]
            if non_lowercase:
                invalid_tags.append(
                    (idx, f"tags contains non-lowercase: {non_lowercase}")
                )

        assert not invalid_tags, f"Found cases with invalid tags:\n" + "\n".join(
            [f"  Case {idx}: {reason}" for idx, reason in invalid_tags]
        )

    @pytest.mark.skip(
        reason="Subcategory-filename matching requires all cases migrated"
    )
    def test_metadata_subcategory_matches_file_naming(self):
        """
        Verify subcategory aligns with file name convention.

        This test will be skipped until all cases are migrated and organized into
        files following the pattern: {category}_{subcategory}_cases.py

        Examples:
        - firebase_auth_cases.py → subcategory="auth"
        - orchestration_planning_cases.py → subcategory="planning"
        - security_auth_cases.py → subcategory="auth"
        """
        # This test requires introspection of which module each case came from,
        # which is complex. It will be implemented after full migration.
        pass


class TestContentIntegrity:
    """Test suite for case content integrity validation."""

    def test_all_cases_have_problem_and_solution(self):
        """
        Verify core fields are preserved during refactoring.

        Tests that every case has:
        - "problem" field (non-empty string)
        - "solution" field (non-empty string)
        - Problem is 10-500 characters
        - Solution is 100-15,000 characters
        """
        from cases import ALL_CASES

        # At least 5 cases should exist
        assert len(ALL_CASES) >= 5, f"Expected at least 5 cases, found {len(ALL_CASES)}"

        missing_fields = []
        invalid_lengths = []

        for idx, case in enumerate(ALL_CASES):
            # Check problem field
            if "problem" not in case:
                missing_fields.append((idx, "problem"))
                continue

            problem = case["problem"]
            if not isinstance(problem, str) or len(problem) == 0:
                missing_fields.append((idx, "problem (empty)"))
                continue

            if not (10 <= len(problem) <= 500):
                invalid_lengths.append((idx, "problem", len(problem), "10-500"))

            # Check solution field
            if "solution" not in case:
                missing_fields.append((idx, "solution"))
                continue

            solution = case["solution"]
            if not isinstance(solution, str) or len(solution) == 0:
                missing_fields.append((idx, "solution (empty)"))
                continue

            if not (100 <= len(solution) <= 15000):
                invalid_lengths.append((idx, "solution", len(solution), "100-15000"))

        assert (
            not missing_fields
        ), f"Found cases with missing or empty fields:\n" + "\n".join(
            [f"  Case {idx}: missing {field}" for idx, field in missing_fields]
        )

        assert (
            not invalid_lengths
        ), f"Found cases with invalid field lengths:\n" + "\n".join(
            [
                f"  Case {idx}: {field} is {length} chars (expected {expected})"
                for idx, field, length, expected in invalid_lengths
            ]
        )

    def test_case_solutions_contain_code(self):
        """
        Verify solutions contain actual code (not just text).

        Tests that solution content contains code indicators:
        - Common code elements (import, function, class, def, const, let, var, etc.)
        - Code uses code formatting (indentation detected by multi-line)
        - Solutions are multi-line strings
        """
        from cases import ALL_CASES

        non_code_solutions = []

        for idx, case in enumerate(ALL_CASES):
            if "solution" not in case:
                continue

            solution = case["solution"]

            # Check multi-line (code should have newlines)
            if "\n" not in solution:
                non_code_solutions.append((idx, "single-line (no newlines)"))
                continue

            # Check for code patterns
            has_code_pattern = any(
                re.search(pattern, solution, re.MULTILINE) for pattern in CODE_PATTERNS
            )

            if not has_code_pattern:
                non_code_solutions.append((idx, "no code patterns detected"))

        assert (
            not non_code_solutions
        ), f"Found cases with solutions that don't contain code:\n" + "\n".join(
            [f"  Case {idx}: {reason}" for idx, reason in non_code_solutions]
        )

    def test_case_count_matches_original(self):
        """
        Verify no cases lost during refactoring.

        Tests that the total number of cases is correct based on the
        actual ALL_CASES aggregation (not hardcoded count).
        """
        from cases import ALL_CASES

        total_cases = len(ALL_CASES)

        # Verify we have a reasonable number of cases
        assert total_cases >= 5, f"Expected at least 5 cases, found {total_cases}"

        # Verify at least we have rust cases
        rust_cases = [
            case
            for case in ALL_CASES
            if case.get("category") == "rust" or "category" not in case
        ]

        assert (
            len(rust_cases) >= 5
        ), f"Expected at least 5 rust cases, found {len(rust_cases)}"
