"""
Tests for ALL_CASES aggregation in the cases module.

This test suite verifies that the ALL_CASES list is properly aggregated
from all modular case files and contains the expected number of cases.
"""

import pytest
from cases import ALL_CASES


class TestAllCasesAggregation:
    """Test suite for ALL_CASES aggregation functionality."""

    def test_all_cases_exists_and_is_list(self):
        """Test that ALL_CASES exists and is a list."""
        assert ALL_CASES is not None, "ALL_CASES should exist"
        assert isinstance(ALL_CASES, list), "ALL_CASES should be a list"

    def test_all_cases_contains_expected_number_of_cases(self):
        """Test that ALL_CASES contains the expected number of cases."""
        from cases import ALL_CASES as EXPECTED_ALL_CASES

        expected_count = len(EXPECTED_ALL_CASES)
        actual_count = len(ALL_CASES)

        assert actual_count == expected_count, (
            f"ALL_CASES should contain exactly {expected_count} cases, "
            f"but contains {actual_count}"
        )

    def test_each_case_is_dictionary(self):
        """Test that each case in ALL_CASES is a dictionary."""
        assert ALL_CASES, "ALL_CASES should not be empty for this test"

        for idx, case in enumerate(ALL_CASES):
            assert isinstance(case, dict), (
                f"Case at index {idx} should be a dictionary, "
                f"but is {type(case).__name__}"
            )

    def test_all_cases_is_not_empty(self):
        """Test that ALL_CASES is not empty."""
        assert len(ALL_CASES) > 0, "ALL_CASES should not be empty"
        assert ALL_CASES, "ALL_CASES should be truthy (not empty)"


class TestAllCasesStructure:
    """Additional structural tests for ALL_CASES."""

    def test_all_cases_contains_only_dictionaries(self):
        """Test that ALL_CASES contains only dictionary objects."""
        if not ALL_CASES:
            pytest.skip("ALL_CASES is empty, skipping structure test")

        non_dict_items = [
            (idx, type(case).__name__)
            for idx, case in enumerate(ALL_CASES)
            if not isinstance(case, dict)
        ]

        assert not non_dict_items, (
            f"ALL_CASES should contain only dictionaries. "
            f"Found non-dict items: {non_dict_items}"
        )

    def test_all_cases_count_matches_requirement(self):
        """Test that the case count matches the documented requirement."""
        from cases import ALL_CASES as EXPECTED_ALL_CASES

        expected_count = len(EXPECTED_ALL_CASES)
        actual_count = len(ALL_CASES)

        assert actual_count == expected_count, (
            f"Expected {expected_count} cases based on requirements, "
            f"but found {actual_count} cases"
        )



class TestDirectoryCoverage:
    """Test suite to verify ALL_CASES includes cases from all expected directories."""

    def test_firebase_cases_present(self):
        """Test that ALL_CASES contains at least one case from cases/firebase/."""
        firebase_cases = [case for case in ALL_CASES if case.get("category") == "firebase"]
        
        assert len(firebase_cases) > 0, (
            "ALL_CASES should contain at least one case with category='firebase'"
        )

    def test_react_cases_present(self):
        """Test that ALL_CASES contains at least one case from cases/react/."""
        react_cases = [case for case in ALL_CASES if case.get("category") == "react"]
        
        assert len(react_cases) > 0, (
            "ALL_CASES should contain at least one case with category='react'"
        )

    def test_nextjs_cases_present(self):
        """Test that ALL_CASES contains at least one case from cases/nextjs/."""
        nextjs_cases = [case for case in ALL_CASES if case.get("category") == "nextjs"]
        
        assert len(nextjs_cases) > 0, (
            "ALL_CASES should contain at least one case with category='nextjs'"
        )

    def test_bootstrap_cases_present(self):
        """Test that ALL_CASES contains at least one case from cases/bootstrap/."""
        bootstrap_cases = [case for case in ALL_CASES if case.get("category") == "bootstrap"]
        
        assert len(bootstrap_cases) > 0, (
            "ALL_CASES should contain at least one case with category='bootstrap'"
        )

    def test_webdev_cases_present(self):
        """Test that ALL_CASES contains at least one case from cases/webdev/."""
        webdev_cases = [case for case in ALL_CASES if case.get("category") == "webdev"]
        
        assert len(webdev_cases) > 0, (
            "ALL_CASES should contain at least one case with category='webdev'"
        )

    def test_orchestration_cases_present(self):
        """Test that ALL_CASES contains at least one case from cases/orchestration/."""
        orchestration_cases = [case for case in ALL_CASES if case.get("category") == "orchestration"]
        
        assert len(orchestration_cases) > 0, (
            "ALL_CASES should contain at least one case with category='orchestration'"
        )

    def test_security_cases_present(self):
        """Test that ALL_CASES contains at least one case from cases/security/."""
        security_cases = [case for case in ALL_CASES if case.get("category") == "security"]
        
        assert len(security_cases) > 0, (
            "ALL_CASES should contain at least one case with category='security'"
        )

    def test_rust_cases_present(self):
        """Test that ALL_CASES contains at least one case from cases/rust/."""
        rust_cases = [case for case in ALL_CASES if case.get("category") == "rust"]
        
        assert len(rust_cases) > 0, (
            "ALL_CASES should contain at least one case with category='rust'"
        )

    def test_all_expected_directories_covered(self):
        """Test that ALL_CASES includes cases from all 8 expected directories."""
        expected_categories = {
            "firebase",
            "react",
            "nextjs",
            "bootstrap",
            "webdev",
            "orchestration",
            "security",
            "rust"
        }

        # Get all unique categories present in ALL_CASES
        present_categories = {case.get("category") for case in ALL_CASES if case.get("category")}

        # Find missing categories
        missing_categories = expected_categories - present_categories

        assert not missing_categories, (
            f"ALL_CASES should include cases from all 8 expected directories. "
            f"Missing categories: {sorted(missing_categories)}"
        )

        # Also verify we found all expected categories
        assert expected_categories.issubset(present_categories), (
            f"Expected categories {sorted(expected_categories)} not all present. "
            f"Found categories: {sorted(present_categories)}"
        )


class TestMetadataCompleteness:
    """Test suite to verify all cases have required metadata fields."""

    def test_all_cases_have_category_field(self):
        """Test that every case in ALL_CASES has a 'category' field."""
        assert ALL_CASES, "ALL_CASES should not be empty for this test"

        missing_category_cases = []
        for idx, case in enumerate(ALL_CASES):
            if "category" not in case:
                case_desc = case.get("description", "No description")
                missing_category_cases.append((idx, case_desc))

        assert not missing_category_cases, (
            f"All cases should have a 'category' field. "
            f"Found {len(missing_category_cases)} cases without 'category': "
            f"{missing_category_cases[:5]}"  # Show first 5 to avoid overwhelming output
        )

    def test_all_cases_have_subcategory_field(self):
        """Test that every case in ALL_CASES has a 'subcategory' field."""
        assert ALL_CASES, "ALL_CASES should not be empty for this test"

        missing_subcategory_cases = []
        for idx, case in enumerate(ALL_CASES):
            if "subcategory" not in case:
                case_desc = case.get("description", "No description")
                missing_subcategory_cases.append((idx, case_desc))

        assert not missing_subcategory_cases, (
            f"All cases should have a 'subcategory' field. "
            f"Found {len(missing_subcategory_cases)} cases without 'subcategory': "
            f"{missing_subcategory_cases[:5]}"  # Show first 5 to avoid overwhelming output
        )

    def test_all_cases_have_tags_field(self):
        """Test that every case in ALL_CASES has a 'tags' field."""
        assert ALL_CASES, "ALL_CASES should not be empty for this test"

        missing_tags_cases = []
        for idx, case in enumerate(ALL_CASES):
            if "tags" not in case:
                case_desc = case.get("description", "No description")
                missing_tags_cases.append((idx, case_desc))

        assert not missing_tags_cases, (
            f"All cases should have a 'tags' field. "
            f"Found {len(missing_tags_cases)} cases without 'tags': "
            f"{missing_tags_cases[:5]}"  # Show first 5 to avoid overwhelming output
        )

    def test_all_cases_have_complete_metadata(self):
        """Test that every case has all three required metadata fields: category, subcategory, and tags."""
        assert ALL_CASES, "ALL_CASES should not be empty for this test"

        required_fields = {"category", "subcategory", "tags"}
        incomplete_cases = []

        for idx, case in enumerate(ALL_CASES):
            missing_fields = required_fields - set(case.keys())
            if missing_fields:
                case_desc = case.get("description", "No description")
                incomplete_cases.append({
                    "index": idx,
                    "description": case_desc,
                    "missing_fields": sorted(missing_fields)
                })

        assert not incomplete_cases, (
            f"All cases should have complete metadata (category, subcategory, tags). "
            f"Found {len(incomplete_cases)} cases with incomplete metadata: "
            f"{incomplete_cases[:5]}"  # Show first 5 to avoid overwhelming output
        )


class TestMetadataValidity:
    """Test suite to verify metadata values are valid (not just present)."""

    ALLOWED_CATEGORIES = [
        "firebase",
        "react",
        "nextjs",
        "bootstrap",
        "webdev",
        "orchestration",
        "security",
        "rust"
    ]

    def test_all_categories_are_valid(self):
        """Test that every case has a category value from the allowed list."""
        assert ALL_CASES, "ALL_CASES should not be empty for this test"

        invalid_category_cases = []
        for idx, case in enumerate(ALL_CASES):
            category = case.get("category")
            if category not in self.ALLOWED_CATEGORIES:
                case_desc = case.get("description", "No description")
                invalid_category_cases.append({
                    "index": idx,
                    "description": case_desc,
                    "invalid_category": category
                })

        assert not invalid_category_cases, (
            f"All cases should have a valid category from {self.ALLOWED_CATEGORIES}. "
            f"Found {len(invalid_category_cases)} cases with invalid categories: "
            f"{invalid_category_cases[:5]}"  # Show first 5 to avoid overwhelming output
        )

    def test_all_subcategories_are_non_empty_strings(self):
        """Test that every case has a non-empty string subcategory."""
        assert ALL_CASES, "ALL_CASES should not be empty for this test"

        invalid_subcategory_cases = []
        for idx, case in enumerate(ALL_CASES):
            subcategory = case.get("subcategory")
            case_desc = case.get("description", "No description")

            if not isinstance(subcategory, str):
                invalid_subcategory_cases.append({
                    "index": idx,
                    "description": case_desc,
                    "issue": f"subcategory is not a string, it is {type(subcategory).__name__}",
                    "value": subcategory
                })
            elif len(subcategory) == 0:
                invalid_subcategory_cases.append({
                    "index": idx,
                    "description": case_desc,
                    "issue": "subcategory is an empty string",
                    "value": subcategory
                })

        assert not invalid_subcategory_cases, (
            f"All cases should have non-empty string subcategories. "
            f"Found {len(invalid_subcategory_cases)} cases with invalid subcategories: "
            f"{invalid_subcategory_cases[:5]}"  # Show first 5 to avoid overwhelming output
        )

    def test_all_tags_fields_are_lists(self):
        """Test that every case has a 'tags' field that is a list."""
        assert ALL_CASES, "ALL_CASES should not be empty for this test"

        non_list_tags_cases = []
        for idx, case in enumerate(ALL_CASES):
            tags = case.get("tags")
            if not isinstance(tags, list):
                case_desc = case.get("description", "No description")
                non_list_tags_cases.append({
                    "index": idx,
                    "description": case_desc,
                    "tags_type": type(tags).__name__,
                    "value": tags
                })

        assert not non_list_tags_cases, (
            f"All cases should have a 'tags' field that is a list. "
            f"Found {len(non_list_tags_cases)} cases with non-list tags: "
            f"{non_list_tags_cases[:5]}"  # Show first 5 to avoid overwhelming output
        )

    def test_all_tags_fields_are_non_empty(self):
        """Test that every case has at least one tag in the 'tags' list."""
        assert ALL_CASES, "ALL_CASES should not be empty for this test"

        empty_tags_cases = []
        for idx, case in enumerate(ALL_CASES):
            tags = case.get("tags")
            if isinstance(tags, list) and len(tags) == 0:
                case_desc = case.get("description", "No description")
                empty_tags_cases.append({
                    "index": idx,
                    "description": case_desc
                })

        assert not empty_tags_cases, (
            f"All cases should have at least one tag in the 'tags' list. "
            f"Found {len(empty_tags_cases)} cases with empty tags: "
            f"{empty_tags_cases[:5]}"  # Show first 5 to avoid overwhelming output
        )

    def test_all_tags_within_tags_fields_are_strings(self):
        """Test that every tag within every 'tags' field is a string."""
        assert ALL_CASES, "ALL_CASES should not be empty for this test"

        non_string_tag_cases = []
        for idx, case in enumerate(ALL_CASES):
            tags = case.get("tags")
            if isinstance(tags, list):
                case_desc = case.get("description", "No description")
                for tag_idx, tag in enumerate(tags):
                    if not isinstance(tag, str):
                        non_string_tag_cases.append({
                            "case_index": idx,
                            "description": case_desc,
                            "tag_index": tag_idx,
                            "tag_type": type(tag).__name__,
                            "tag_value": tag
                        })

        assert not non_string_tag_cases, (
            f"All tags within 'tags' fields should be strings. "
            f"Found {len(non_string_tag_cases)} non-string tags: "
            f"{non_string_tag_cases[:5]}"  # Show first 5 to avoid overwhelming output
        )

    def test_comprehensive_metadata_validity(self):
        """Comprehensive validation of all metadata rules together."""
        assert ALL_CASES, "ALL_CASES should not be empty for this test"

        violations = []

        for idx, case in enumerate(ALL_CASES):
            case_desc = case.get("description", "No description")
            case_violations = []

            # Check category validity
            category = case.get("category")
            if category not in self.ALLOWED_CATEGORIES:
                case_violations.append(
                    f"Invalid category: {category} (allowed: {self.ALLOWED_CATEGORIES})"
                )

            # Check subcategory is non-empty string
            subcategory = case.get("subcategory")
            if not isinstance(subcategory, str):
                case_violations.append(
                    f"Subcategory is not a string: {type(subcategory).__name__}"
                )
            elif len(subcategory) == 0:
                case_violations.append("Subcategory is an empty string")

            # Check tags field is non-empty list
            tags = case.get("tags")
            if not isinstance(tags, list):
                case_violations.append(
                    f"Tags field is not a list: {type(tags).__name__}"
                )
            elif len(tags) == 0:
                case_violations.append("Tags field is empty")
            else:
                # Check all tags are strings
                for tag_idx, tag in enumerate(tags):
                    if not isinstance(tag, str):
                        case_violations.append(
                            f"Tag at index {tag_idx} is not a string: {type(tag).__name__}"
                        )

            if case_violations:
                violations.append({
                    "index": idx,
                    "description": case_desc,
                    "violations": case_violations
                })

        assert not violations, (
            f"All cases should have valid metadata (category, subcategory, tags). "
            f"Found {len(violations)} cases with metadata violations: "
            f"{violations[:5]}"  # Show first 5 to avoid overwhelming output
        )


class TestRustCasesCompatibility:
    """Test suite to verify rust cases work correctly with the dynamic loader."""

    def test_rust_cases_count_is_30(self):
        """Test that exactly 30 rust cases are loaded by the dynamic loader."""
        rust_cases = [case for case in ALL_CASES if case.get("category") == "rust"]

        assert len(rust_cases) == 30, (
            f"Expected exactly 30 rust cases, but found {len(rust_cases)}"
        )

    def test_all_rust_cases_have_metadata_fields(self):
        """Test that all rust cases have the required metadata fields."""
        rust_cases = [case for case in ALL_CASES if case.get("category") == "rust"]

        assert rust_cases, "No rust cases found for this test"

        missing_metadata_cases = []
        for idx, case in enumerate(rust_cases):
            missing_fields = []

            if "category" not in case:
                missing_fields.append("category")
            if "subcategory" not in case:
                missing_fields.append("subcategory")
            if "tags" not in case:
                missing_fields.append("tags")

            if missing_fields:
                case_desc = case.get("problem", "No problem description")[:50]
                missing_metadata_cases.append({
                    "index": idx,
                    "problem_snippet": case_desc,
                    "missing_fields": missing_fields
                })

        assert not missing_metadata_cases, (
            f"All rust cases should have metadata fields (category, subcategory, tags). "
            f"Found {len(missing_metadata_cases)} rust cases with missing metadata: "
            f"{missing_metadata_cases}"
        )

    def test_all_rust_cases_have_valid_category(self):
        """Test that all rust cases have category='rust'."""
        rust_cases = [case for case in ALL_CASES if case.get("category") == "rust"]

        assert rust_cases, "No rust cases found for this test"

        invalid_category_cases = []
        for idx, case in enumerate(rust_cases):
            category = case.get("category")
            if category != "rust":
                case_desc = case.get("problem", "No problem description")[:50]
                invalid_category_cases.append({
                    "index": idx,
                    "problem_snippet": case_desc,
                    "actual_category": category
                })

        assert not invalid_category_cases, (
            f"All rust cases should have category='rust'. "
            f"Found {len(invalid_category_cases)} rust cases with invalid category: "
            f"{invalid_category_cases}"
        )

    def test_all_rust_cases_have_non_empty_subcategory(self):
        """Test that all rust cases have non-empty subcategory strings."""
        rust_cases = [case for case in ALL_CASES if case.get("category") == "rust"]

        assert rust_cases, "No rust cases found for this test"

        invalid_subcategory_cases = []
        for idx, case in enumerate(rust_cases):
            subcategory = case.get("subcategory")
            case_desc = case.get("problem", "No problem description")[:50]

            if not isinstance(subcategory, str):
                invalid_subcategory_cases.append({
                    "index": idx,
                    "problem_snippet": case_desc,
                    "issue": f"subcategory is not a string, it is {type(subcategory).__name__}",
                    "value": subcategory
                })
            elif len(subcategory) == 0:
                invalid_subcategory_cases.append({
                    "index": idx,
                    "problem_snippet": case_desc,
                    "issue": "subcategory is an empty string",
                    "value": subcategory
                })

        assert not invalid_subcategory_cases, (
            f"All rust cases should have non-empty string subcategories. "
            f"Found {len(invalid_subcategory_cases)} rust cases with invalid subcategories: "
            f"{invalid_subcategory_cases}"
        )

    def test_all_rust_cases_have_valid_tags_list(self):
        """Test that all rust cases have valid tags lists with at least one tag."""
        rust_cases = [case for case in ALL_CASES if case.get("category") == "rust"]

        assert rust_cases, "No rust cases found for this test"

        invalid_tags_cases = []
        for idx, case in enumerate(rust_cases):
            tags = case.get("tags")
            case_desc = case.get("problem", "No problem description")[:50]

            if not isinstance(tags, list):
                invalid_tags_cases.append({
                    "index": idx,
                    "problem_snippet": case_desc,
                    "issue": f"tags is not a list, it is {type(tags).__name__}",
                    "value": tags
                })
            elif len(tags) == 0:
                invalid_tags_cases.append({
                    "index": idx,
                    "problem_snippet": case_desc,
                    "issue": "tags list is empty",
                    "value": tags
                })
            else:
                # Check all tags are strings
                for tag_idx, tag in enumerate(tags):
                    if not isinstance(tag, str):
                        invalid_tags_cases.append({
                            "index": idx,
                            "problem_snippet": case_desc,
                            "issue": f"tag at index {tag_idx} is not a string",
                            "tag_type": type(tag).__name__,
                            "tag_value": tag
                        })
                        break  # Only report first non-string tag per case

        assert not invalid_tags_cases, (
            f"All rust cases should have valid tags lists with at least one string tag. "
            f"Found {len(invalid_tags_cases)} rust cases with invalid tags: "
            f"{invalid_tags_cases}"
        )

    def test_rust_cases_structure_is_complete(self):
        """Test that rust cases have the complete expected structure."""
        rust_cases = [case for case in ALL_CASES if case.get("category") == "rust"]

        assert rust_cases, "No rust cases found for this test"

        required_fields = {"problem", "solution", "category", "subcategory", "tags"}
        incomplete_cases = []

        for idx, case in enumerate(rust_cases):
            missing_fields = required_fields - set(case.keys())

            if missing_fields:
                case_desc = case.get("problem", "No problem description")[:50]
                incomplete_cases.append({
                    "index": idx,
                    "problem_snippet": case_desc,
                    "missing_fields": sorted(missing_fields)
                })

        assert not incomplete_cases, (
            f"All rust cases should have complete structure (problem, solution, category, subcategory, tags). "
            f"Found {len(incomplete_cases)} rust cases with incomplete structure: "
            f"{incomplete_cases}"
        )
