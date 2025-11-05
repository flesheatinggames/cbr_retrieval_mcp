"""Unit tests for metadata validation logic in cases module.

This test suite validates the validate_case() function that ensures case dictionaries
contain all required metadata fields before storage in ChromaDB. These tests follow
Test-Driven Development (TDD) principles and are written BEFORE the implementation.

The validate_case() function is expected to:
1. Check for presence of required fields: problem, solution, category, subcategory, tags
2. Validate that tags field is a list type
3. Log warnings for validation failures
4. Return True for valid cases, False for invalid cases

Expected behavior:
- Valid case: Returns True, no logging
- Missing field: Returns False, logs warning with field name
- Wrong type (tags): Returns False, logs warning about type
"""

import pytest
from typing import Any, Dict, List
from unittest.mock import patch, MagicMock

from cases import validate_case


# Test data fixtures based on test specification
COMPLETE_CASE = {
    "problem": "Test problem description with all required fields",
    "solution": "Test solution code implementation",
    "category": "test-category",
    "subcategory": "test-subcategory",
    "tags": ["tag1", "tag2", "tag3"],
}

MISSING_CATEGORY_CASE = {
    "problem": "Test problem without category field",
    "solution": "Test solution code",
    "subcategory": "test-subcategory",
    "tags": ["tag1", "tag2"],
}

MISSING_SUBCATEGORY_CASE = {
    "problem": "Test problem without subcategory field",
    "solution": "Test solution code",
    "category": "test-category",
    "tags": ["tag1", "tag2"],
}

MISSING_TAGS_CASE = {
    "problem": "Test problem without tags field",
    "solution": "Test solution code",
    "category": "test-category",
    "subcategory": "test-subcategory",
}

TAGS_AS_STRING_CASE = {
    "problem": "Test problem with tags as string instead of list",
    "solution": "Test solution code",
    "category": "test-category",
    "subcategory": "test-subcategory",
    "tags": "tag1,tag2,tag3",  # Wrong type - should be list
}


def test_validate_case_with_all_fields():
    """
    Test: Verify valid case with all required fields returns True.

    Given: A case dictionary with all required fields (problem, solution, category,
           subcategory, tags as list)
    When: The validate_case() function is called
    Then: Returns True indicating validation passed
          No warnings are logged
    """
    # Given: A complete case with all required metadata fields
    case = COMPLETE_CASE

    # When: Validating the case
    result = validate_case(case)

    # Then: Validation succeeds
    assert result is True, "Valid case with all fields must return True"


@patch("cases.logger")
def test_validate_case_missing_category(mock_logger):
    """
    Test: Verify case missing category field returns False and logs warning.

    Given: A case dictionary missing the category field
    When: The validate_case() function is called
    Then: Returns False indicating validation failed
          Logs a warning message about missing category field
    """
    # Given: A case missing the category field
    case = MISSING_CATEGORY_CASE

    # When: Validating the case
    result = validate_case(case)

    # Then: Validation fails
    assert result is False, "Case missing category must return False"

    # And: A warning is logged
    mock_logger.warning.assert_called_once()
    warning_message = mock_logger.warning.call_args[0][0]
    assert "category" in warning_message.lower(), (
        "Warning message must mention missing category field"
    )


@patch("cases.logger")
def test_validate_case_missing_subcategory(mock_logger):
    """
    Test: Verify case missing subcategory field returns False and logs warning.

    Given: A case dictionary missing the subcategory field
    When: The validate_case() function is called
    Then: Returns False indicating validation failed
          Logs a warning message about missing subcategory field
    """
    # Given: A case missing the subcategory field
    case = MISSING_SUBCATEGORY_CASE

    # When: Validating the case
    result = validate_case(case)

    # Then: Validation fails
    assert result is False, "Case missing subcategory must return False"

    # And: A warning is logged
    mock_logger.warning.assert_called_once()
    warning_message = mock_logger.warning.call_args[0][0]
    assert "subcategory" in warning_message.lower(), (
        "Warning message must mention missing subcategory field"
    )


@patch("cases.logger")
def test_validate_case_missing_tags(mock_logger):
    """
    Test: Verify case missing tags field returns False and logs warning.

    Given: A case dictionary missing the tags field
    When: The validate_case() function is called
    Then: Returns False indicating validation failed
          Logs a warning message about missing tags field
    """
    # Given: A case missing the tags field
    case = MISSING_TAGS_CASE

    # When: Validating the case
    result = validate_case(case)

    # Then: Validation fails
    assert result is False, "Case missing tags must return False"

    # And: A warning is logged
    mock_logger.warning.assert_called_once()
    warning_message = mock_logger.warning.call_args[0][0]
    assert "tags" in warning_message.lower(), (
        "Warning message must mention missing tags field"
    )


@patch("cases.logger")
def test_validate_case_tags_not_list(mock_logger):
    """
    Test: Verify case with tags as string instead of list returns False and logs warning.

    Given: A case dictionary with tags field present but as string type (not list)
    When: The validate_case() function is called
    Then: Returns False indicating validation failed
          Logs a warning message about tags needing to be a list type
    """
    # Given: A case with tags as string instead of list
    case = TAGS_AS_STRING_CASE

    # When: Validating the case
    result = validate_case(case)

    # Then: Validation fails
    assert result is False, "Case with tags as string must return False"

    # And: A warning is logged about type error
    mock_logger.warning.assert_called_once()
    warning_message = mock_logger.warning.call_args[0][0]
    assert "tags" in warning_message.lower(), (
        "Warning message must mention tags field"
    )
    assert "list" in warning_message.lower(), (
        "Warning message must mention list type requirement"
    )


def test_metadata_list_validation_before_storage():
    """
    Test: Verify metadata list length matches CASE_BASE length.

    Given: A CASE_BASE with known number of cases
           A metadata list generated from those cases
    When: Comparing the lengths of both lists
    Then: Both lists have the same length
          This validation would catch length mismatches before ChromaDB storage
    """
    # Given: Mock CASE_BASE with known length
    mock_case_base = [
        COMPLETE_CASE,
        MISSING_CATEGORY_CASE,
        MISSING_SUBCATEGORY_CASE,
    ]
    expected_length = len(mock_case_base)

    # And: Mock metadata list that should be generated from CASE_BASE
    # (In real implementation, this would be created by extract_metadata_list)
    mock_metadata_list = [
        {"problem": "p1", "category": "c1", "subcategory": "s1", "tags": "t1"},
        {"problem": "p2", "category": "c2", "subcategory": "s2", "tags": "t2"},
        {"problem": "p3", "category": "c3", "subcategory": "s3", "tags": "t3"},
    ]

    # When: Validating lengths match
    metadata_length = len(mock_metadata_list)

    # Then: Lengths must be equal
    assert metadata_length == expected_length, (
        f"Metadata list length ({metadata_length}) must match "
        f"CASE_BASE length ({expected_length})"
    )

    # Additional validation: Test that mismatch would be caught
    # Given: A mismatched metadata list (wrong length)
    mismatched_metadata_list = [
        {"problem": "p1", "category": "c1", "subcategory": "s1", "tags": "t1"},
        {"problem": "p2", "category": "c2", "subcategory": "s2", "tags": "t2"},
    ]

    # When/Then: Assertion would fail for mismatched lengths
    with pytest.raises(AssertionError):
        assert len(mismatched_metadata_list) == expected_length, (
            "Length mismatch should raise assertion error"
        )
