"""Unit tests for metadata extraction logic in setup_vectordb.py

This test suite validates the metadata extraction functionality that converts
case dictionaries into ChromaDB-compatible metadata format. These tests follow
Test-Driven Development (TDD) principles and are written BEFORE the implementation.

Expected metadata format:
{
    "problem": str,      # Problem text from case
    "category": str,     # Category or "unknown" if missing
    "subcategory": str,  # Subcategory or "unknown" if missing
    "tags": str          # Comma-separated tags or "" if missing/empty
}
"""

from typing import Any

import pytest

from cbr_mcp_server.metadata_extraction import (
    extract_metadata_from_case,
    extract_metadata_list,
)

# Test data fixtures
COMPLETE_CASE = {
    "problem": "Test problem with all fields",
    "solution": "Test solution implementation",
    "category": "orchestration",
    "subcategory": "planning",
    "tags": ["tag1", "tag2", "tag3"],
}

MISSING_CATEGORY = {
    "problem": "Test problem without category",
    "solution": "Test solution",
    "subcategory": "planning",
    "tags": ["tag1"],
}

MISSING_SUBCATEGORY = {
    "problem": "Test problem without subcategory",
    "solution": "Test solution",
    "category": "orchestration",
    "tags": ["tag1", "tag2"],
}

MISSING_TAGS = {
    "problem": "Test problem without tags",
    "solution": "Test solution",
    "category": "code",
    "subcategory": "react-components",
}

EMPTY_TAGS = {
    "problem": "Test problem with empty tags list",
    "solution": "Test solution",
    "category": "best-practice",
    "subcategory": "planning",
    "tags": [],
}


def test_metadata_extraction_from_case_dict():
    """
    Test: Verify complete case with all fields extracts to proper metadata dict.

    Given: A complete case dictionary with problem, category, subcategory, and tags
    When: The metadata extraction function is called
    Then: A metadata dictionary is returned with all fields correctly mapped:
          - problem field matches case["problem"]
          - category field matches case["category"]
          - subcategory field matches case["subcategory"]
          - tags field is comma-separated string from case["tags"] list
    """
    # Given: A complete case with all metadata fields
    case = COMPLETE_CASE

    # When: Extracting metadata from the case
    metadata = extract_metadata_from_case(case)

    # Then: All fields are correctly extracted
    assert "problem" in metadata, "Metadata must contain 'problem' field"
    assert "category" in metadata, "Metadata must contain 'category' field"
    assert "subcategory" in metadata, "Metadata must contain 'subcategory' field"
    assert "tags" in metadata, "Metadata must contain 'tags' field"

    assert metadata["problem"] == case["problem"], "Problem field must match"
    assert metadata["category"] == case["category"], "Category field must match"
    assert (
        metadata["subcategory"] == case["subcategory"]
    ), "Subcategory field must match"
    assert metadata["tags"] == "tag1,tag2,tag3", "Tags must be comma-separated string"


def test_metadata_extraction_with_missing_category():
    """
    Test: Verify missing category defaults to "unknown".

    Given: A case dictionary without a category field
    When: The metadata extraction function is called
    Then: The metadata dictionary has "unknown" as the category value
          and other fields are correctly extracted
    """
    # Given: A case missing the category field
    case = MISSING_CATEGORY

    # When: Extracting metadata from the case
    metadata = extract_metadata_from_case(case)

    # Then: Category defaults to "unknown" and no error is raised
    assert (
        metadata["category"] == "unknown"
    ), "Missing category must default to 'unknown'"
    assert metadata["problem"] == case["problem"], "Problem field must be extracted"
    assert (
        metadata["subcategory"] == case["subcategory"]
    ), "Subcategory field must be extracted"
    assert metadata["tags"] == "tag1", "Tags field must be extracted"


def test_metadata_extraction_with_missing_subcategory():
    """
    Test: Verify missing subcategory defaults to "unknown".

    Given: A case dictionary without a subcategory field
    When: The metadata extraction function is called
    Then: The metadata dictionary has "unknown" as the subcategory value
          and other fields are correctly extracted
    """
    # Given: A case missing the subcategory field
    case = MISSING_SUBCATEGORY

    # When: Extracting metadata from the case
    metadata = extract_metadata_from_case(case)

    # Then: Subcategory defaults to "unknown" and no error is raised
    assert (
        metadata["subcategory"] == "unknown"
    ), "Missing subcategory must default to 'unknown'"
    assert metadata["problem"] == case["problem"], "Problem field must be extracted"
    assert metadata["category"] == case["category"], "Category field must be extracted"
    assert metadata["tags"] == "tag1,tag2", "Tags field must be extracted"


def test_metadata_extraction_with_missing_tags():
    """
    Test: Verify missing tags defaults to empty string.

    Given: A case dictionary without a tags field
    When: The metadata extraction function is called
    Then: The metadata dictionary has "" (empty string) as the tags value
          and other fields are correctly extracted
    """
    # Given: A case missing the tags field
    case = MISSING_TAGS

    # When: Extracting metadata from the case
    metadata = extract_metadata_from_case(case)

    # Then: Tags defaults to empty string and no error is raised
    assert metadata["tags"] == "", "Missing tags must default to empty string"
    assert metadata["problem"] == case["problem"], "Problem field must be extracted"
    assert metadata["category"] == case["category"], "Category field must be extracted"
    assert (
        metadata["subcategory"] == case["subcategory"]
    ), "Subcategory field must be extracted"


def test_metadata_extraction_tags_list_to_string_conversion():
    """
    Test: Verify tags list converts to comma-separated string.

    Given: Cases with different tags configurations (single, multiple, empty)
    When: The metadata extraction function is called
    Then: Tags are correctly converted to comma-separated strings:
          - ["tag1"] → "tag1"
          - ["tag1", "tag2", "tag3"] → "tag1,tag2,tag3"
          - [] → ""
    """
    # Given: Case with single tag
    case_single = {**COMPLETE_CASE, "tags": ["single_tag"]}
    metadata_single = extract_metadata_from_case(case_single)
    assert (
        metadata_single["tags"] == "single_tag"
    ), "Single tag must be converted to string"

    # Given: Case with multiple tags
    case_multiple = {**COMPLETE_CASE, "tags": ["first", "second", "third"]}
    metadata_multiple = extract_metadata_from_case(case_multiple)
    assert (
        metadata_multiple["tags"] == "first,second,third"
    ), "Multiple tags must be comma-separated"

    # Given: Case with empty tags list
    case_empty = EMPTY_TAGS
    metadata_empty = extract_metadata_from_case(case_empty)
    assert metadata_empty["tags"] == "", "Empty tags list must convert to empty string"


def test_metadata_list_length_matches_cases():
    """
    Test: Verify metadata list length matches case list length.

    Given: Lists of cases with various sizes (0, 1, 3, 5)
    When: The metadata list extraction function is called
    Then: The resulting metadata list has the same length as the input case list
    """
    # Given: Empty case list
    empty_cases = []
    metadata_empty = extract_metadata_list(empty_cases)
    assert len(metadata_empty) == 0, "Empty case list must produce empty metadata list"

    # Given: Single case
    single_case = [COMPLETE_CASE]
    metadata_single = extract_metadata_list(single_case)
    assert len(metadata_single) == 1, "Single case must produce single metadata dict"

    # Given: Three cases
    three_cases = [COMPLETE_CASE, MISSING_CATEGORY, MISSING_SUBCATEGORY]
    metadata_three = extract_metadata_list(three_cases)
    assert len(metadata_three) == 3, "Three cases must produce three metadata dicts"

    # Given: Five cases
    five_cases = [
        COMPLETE_CASE,
        MISSING_CATEGORY,
        MISSING_SUBCATEGORY,
        MISSING_TAGS,
        EMPTY_TAGS,
    ]
    metadata_five = extract_metadata_list(five_cases)
    assert len(metadata_five) == 5, "Five cases must produce five metadata dicts"


def test_all_metadata_dicts_have_required_fields():
    """
    Test: Verify every metadata dict has required fields.

    Given: A list of cases with various missing fields
    When: The metadata list extraction function is called
    Then: Every metadata dictionary in the list contains all four required fields:
          - problem
          - category
          - subcategory
          - tags
    """
    # Given: Multiple cases with different missing fields
    cases = [
        COMPLETE_CASE,
        MISSING_CATEGORY,
        MISSING_SUBCATEGORY,
        MISSING_TAGS,
        EMPTY_TAGS,
    ]

    # When: Extracting metadata list
    metadata_list = extract_metadata_list(cases)

    # Then: Every metadata dict has all required fields
    required_fields = {"problem", "category", "subcategory", "tags"}

    for i, metadata in enumerate(metadata_list):
        metadata_keys = set(metadata.keys())
        assert required_fields.issubset(metadata_keys), (
            f"Metadata dict at index {i} missing required fields. "
            f"Expected {required_fields}, got {metadata_keys}"
        )

        # Verify all values are strings
        for field in required_fields:
            assert isinstance(metadata[field], str), (
                f"Field '{field}' at index {i} must be a string, "
                f"got {type(metadata[field])}"
            )
