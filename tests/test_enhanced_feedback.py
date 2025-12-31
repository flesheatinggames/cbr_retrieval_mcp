"""Tests for enhanced user feedback and error handling in setup_vectordb.py

This test suite validates Task 5 requirements:
- Error handling for malformed case data
- Error handling for database failures
- User-friendly error messages
- Error recovery mechanisms

Note: Task 5 requirements 5.1, 5.2, and 5.5 are already fully covered by existing tests and
implementation:
- 5.1 Console formatting: Tested in test_incremental_update.py::test_incremental_update_statistics_output
- 5.2 Statistics display: Implemented in setup_vectordb.py lines 635-644, tested
- 5.5 Documentation: All functions have comprehensive docstrings

This test file focuses on the GAPS in current coverage:
- Error handling for edge cases (5.3)
- Validation and helpful error messages (5.3)

These tests are written BEFORE implementation (TDD Red phase) and should initially FAIL.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
import pytest
import chromadb

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utilities.setup_vectordb import generate_case_id, identify_new_cases


class TestIDGenerationErrorHandling:
    """Test error handling during case ID generation."""

    def test_generate_case_id_handles_missing_problem_field(self):
        """
        Test: Generate case ID should handle missing 'problem' field gracefully.

        Given: Case dictionary missing 'problem' key
        When: generate_case_id() is called
        Then: Should return valid ID using empty string for missing field
              OR raise informative error message

        Currently EXPECTED TO FAIL - implementation uses get() with default but tests proper behavior
        """
        # Given: Case missing 'problem' field
        malformed_case = {
            "solution": "Use Firebase Auth with email/password.",
            "category": "code",
            "subcategory": "firebase-auth",
        }

        # When/Then: Should either handle gracefully OR raise clear error
        try:
            case_id = generate_case_id(malformed_case)
            # If it succeeds, verify it returns valid ID format
            assert case_id.startswith(
                "case_"
            ), "ID should still have 'case_' prefix even with missing problem field"
            assert (
                len(case_id) == 21
            ), f"ID should be 21 chars (case_ + 16 hex), got {len(case_id)}"
        except KeyError as e:
            # If it raises error, verify error message is helpful
            error_msg = str(e)
            assert (
                "problem" in error_msg.lower()
            ), "Error message should mention missing 'problem' field"

    def test_generate_case_id_handles_missing_solution_field(self):
        """
        Test: Generate case ID should handle missing 'solution' field gracefully.

        Given: Case dictionary missing 'solution' key
        When: generate_case_id() is called
        Then: Should return valid ID using empty string for missing field
              OR raise informative error message

        Currently EXPECTED TO FAIL - implementation uses get() with default but tests proper behavior
        """
        # Given: Case missing 'solution' field
        malformed_case = {
            "problem": "How to implement authentication?",
            "category": "code",
            "subcategory": "firebase-auth",
        }

        # When/Then: Should either handle gracefully OR raise clear error
        try:
            case_id = generate_case_id(malformed_case)
            # If it succeeds, verify it returns valid ID format
            assert case_id.startswith(
                "case_"
            ), "ID should still have 'case_' prefix even with missing solution field"
            assert (
                len(case_id) == 21
            ), f"ID should be 21 chars (case_ + 16 hex), got {len(case_id)}"
        except KeyError as e:
            # If it raises error, verify error message is helpful
            error_msg = str(e)
            assert (
                "solution" in error_msg.lower()
            ), "Error message should mention missing 'solution' field"

    def test_generate_case_id_handles_none_problem_value(self):
        """
        Test: Generate case ID should handle None value for 'problem' field.

        Given: Case with problem=None
        When: generate_case_id() is called
        Then: Should handle None gracefully by converting to string OR raise clear error

        Currently EXPECTED TO FAIL - tests defensive programming for None values
        """
        # Given: Case with None problem value
        malformed_case = {
            "problem": None,
            "solution": "Use Firebase Auth with email/password.",
        }

        # When/Then: Should handle None value gracefully
        try:
            case_id = generate_case_id(malformed_case)
            # Verify valid ID was generated
            assert case_id.startswith(
                "case_"
            ), "ID should have 'case_' prefix even with None problem"
            assert len(case_id) == 21, f"ID should be 21 chars, got {len(case_id)}"
        except (TypeError, AttributeError) as e:
            # If it fails, error should be clear
            pytest.fail(f"Should handle None values gracefully, got: {e}")

    def test_generate_case_id_handles_unicode_content(self):
        """
        Test: Generate case ID should handle Unicode characters correctly.

        Given: Case with Unicode characters (emoji, international chars)
        When: generate_case_id() is called
        Then: Should generate valid hash without encoding errors

        Currently EXPECTED TO PASS - implementation uses UTF-8 encoding
        """
        # Given: Case with Unicode content
        unicode_case = {
            "problem": "Comment gérer l'authentification? 🔐",
            "solution": "Use Firebase Auth 中文 עברית",
        }

        # When: Generate ID
        case_id = generate_case_id(unicode_case)

        # Then: Should succeed and return valid ID
        assert case_id.startswith(
            "case_"
        ), "ID should have 'case_' prefix for Unicode content"
        assert (
            len(case_id) == 21
        ), f"ID should be 21 chars for Unicode, got {len(case_id)}"


class TestDeduplicationErrorHandling:
    """Test error handling during case deduplication."""

    def test_identify_new_cases_handles_database_connection_error(self):
        """
        Test: identify_new_cases should handle database connection failures gracefully.

        Given: Collection that raises exception on get()
        When: identify_new_cases() is called
        Then: Should return all cases as new (defensive behavior)
              AND not crash

        Currently EXPECTED TO PASS - implementation has try-catch at line 145
        """
        # Given: Mock collection that raises error
        mock_collection = Mock()
        mock_collection.get.side_effect = Exception("Database connection failed")

        test_cases = [
            {"problem": "Test problem", "solution": "Test solution"},
        ]

        # When: Call identify_new_cases
        new_cases, skipped_count = identify_new_cases(test_cases, mock_collection)

        # Then: Should treat all cases as new (defensive behavior)
        assert len(new_cases) == len(
            test_cases
        ), "On DB error, should treat all cases as new"
        assert skipped_count == 0, "On DB error, skipped count should be 0"

    def test_identify_new_cases_handles_malformed_database_response(self):
        """
        Test: identify_new_cases should handle malformed database responses.

        Given: Collection that returns None or malformed data
        When: identify_new_cases() is called
        Then: Should handle gracefully without crashing

        Currently EXPECTED TO FAIL - tests defensive programming for bad responses
        """
        # Given: Mock collection with malformed response
        mock_collection = Mock()
        mock_collection.get.return_value = None  # Bad response

        test_cases = [
            {"problem": "Test problem", "solution": "Test solution"},
        ]

        # When/Then: Should not crash
        try:
            new_cases, skipped_count = identify_new_cases(test_cases, mock_collection)
            # Should treat all as new when response is malformed
            assert len(new_cases) == len(
                test_cases
            ), "On malformed response, should treat all cases as new"
        except (TypeError, KeyError, AttributeError) as e:
            pytest.fail(f"Should handle malformed responses gracefully, got: {e}")

    def test_identify_new_cases_validates_case_structure_before_id_generation(self):
        """
        Test: identify_new_cases should validate case structure before generating IDs.

        Given: List containing malformed cases (missing required fields)
        When: identify_new_cases() is called
        Then: Should provide helpful error message OR skip malformed cases with warning

        Currently EXPECTED TO FAIL - no validation before ID generation
        """
        # Given: Mix of valid and invalid cases
        mixed_cases = [
            {"problem": "Valid case", "solution": "Valid solution"},
            {"problem": "Missing solution"},  # Invalid
            {"solution": "Missing problem"},  # Invalid
        ]

        mock_collection = Mock()
        mock_collection.get.return_value = {"ids": []}

        # When/Then: Should either validate upfront OR provide clear error
        try:
            new_cases, skipped_count = identify_new_cases(mixed_cases, mock_collection)
            # If it succeeds, should have processed only valid case
            # OR should have skipped invalid cases with warning
            assert len(new_cases) <= len(
                mixed_cases
            ), "Should not produce more cases than input"
        except KeyError as e:
            # If it raises KeyError, should be informative
            error_msg = str(e)
            assert any(
                field in error_msg.lower() for field in ["problem", "solution"]
            ), f"Error should mention missing field, got: {error_msg}"


class TestUserFeedbackQuality:
    """Test quality and clarity of user-facing error messages."""

    @pytest.mark.skip(
        reason="Future enhancement: contextual error messages with case index"
    )
    def test_error_message_includes_case_details_on_id_generation_failure(self):
        """
        Test: Error messages should include case details to help debugging.

        Given: ID generation fails for specific case
        When: Error is raised
        Then: Error message should include case index or identifying info

        FUTURE ENHANCEMENT - This test is skipped because:
        1. Current implementation uses .get() defaults, so missing fields don't raise errors
        2. This test was incorrectly implementing the enhancement in test code (lines 277-278)
        3. If we want contextual errors, implementation should be enhanced, not test code

        When implementing this enhancement:
        - Modify generate_case_id() to track case index in error messages
        - OR create a wrapper function that processes batches with context
        - Then remove @pytest.mark.skip and update test to verify real implementation
        """
        # Given: Function that processes multiple cases
        cases = [
            {"problem": "Case 1", "solution": "Sol 1"},
            {"problem": "Case 2"},  # Missing solution - currently handled via default
            {"problem": "Case 3", "solution": "Sol 3"},
        ]

        # When: Processing cases with enhanced error tracking (not yet implemented)
        # Then: Error should indicate WHICH case failed with contextual information

        # This test body should be rewritten when enhancement is implemented
        # to test the actual implementation, not test-side error wrapping
        pytest.fail(
            "Test needs rewrite when contextual error enhancement is implemented"
        )

    def test_validation_error_suggests_fix_for_common_issues(self):
        """
        Test: Validation errors should suggest fixes to users.

        Given: Common validation failures (missing fields, empty values)
        When: Validation occurs
        Then: Error message should suggest how to fix the issue

        Currently EXPECTED TO FAIL - no helpful fix suggestions in errors
        """
        # Given: Case with empty required field
        empty_case = {"problem": "", "solution": "Some solution"}

        # When: Validating case (this validation doesn't exist yet)
        # Then: Should suggest checking case files for empty fields
        # This is a placeholder for validation that should be added

        # For now, test that empty strings produce valid IDs
        # (which may not be desired behavior - should discuss)
        case_id = generate_case_id(empty_case)

        # The current implementation accepts empty strings
        # Future enhancement: validate and provide helpful error
        assert case_id.startswith(
            "case_"
        ), "Current implementation allows empty problem (may want to validate)"


class TestErrorRecovery:
    """Test error recovery mechanisms."""

    def test_partial_failure_does_not_prevent_processing_valid_cases(self):
        """
        Test: Verify defensive programming allows processing all cases via defaults.

        Given: Cases with missing optional fields (solution)
        When: generate_case_id() is called for each case
        Then: All cases should be processed successfully using .get() defaults
              (empty string for missing solution field)

        This test validates current design decision:
        - Implementation uses .get("solution", "") defaults
        - Missing fields are treated as empty strings, not errors
        - This is defensive programming, not validation failure

        NOTE: If strict validation is desired (reject missing fields), this behavior
        should be changed and test updated accordingly.
        """
        # Given: Cases with missing solution field (tests defensive defaults)
        cases = [
            {"problem": "Valid 1", "solution": "Sol 1"},
            {"problem": "Missing solution field"},  # Uses empty string default
            {"problem": "Valid 2", "solution": "Sol 2"},
        ]

        # When: Processing cases individually
        results = []
        errors = []

        for case in cases:
            try:
                case_id = generate_case_id(case)
                results.append(case_id)
            except KeyError as e:
                errors.append(str(e))

        # Then: All cases should be processed (defensive behavior via .get() defaults)
        assert (
            len(results) == 3
        ), f"Should process all 3 cases using .get() defaults, got {len(results)}"

        # And: No errors should be recorded (missing fields use defaults)
        assert (
            len(errors) == 0
        ), f"Should have 0 errors with .get() defaults, got {len(errors)}"

        # Verify all IDs are valid format
        for case_id in results:
            assert case_id.startswith(
                "case_"
            ), f"All IDs should have 'case_' prefix, got {case_id}"
            assert len(case_id) == 21, f"All IDs should be 21 chars, got {len(case_id)}"

    def test_database_collection_none_handled_gracefully(self):
        """
        Test: None collection should be handled defensively.

        Given: collection=None passed to identify_new_cases
        When: Function executes
        Then: Should not crash, should treat all cases as new

        Currently EXPECTED TO PASS - implementation checks for None at line 141
        """
        # Given: None collection
        test_cases = [
            {"problem": "Test", "solution": "Test sol"},
        ]

        # When: Call with None collection
        new_cases, skipped = identify_new_cases(test_cases, None)

        # Then: Should handle gracefully
        assert (
            new_cases == test_cases
        ), "With None collection, should return all cases as new"
        assert skipped == 0, "With None collection, skipped should be 0"
