"""Unit tests for generate_case_id() function in setup_vectordb.py

This test suite validates the content-based ID generation functionality that creates
stable, SHA-256 hash-based IDs for case deduplication. These tests follow Test-Driven
Development (TDD) principles and are written BEFORE the implementation.

Function Specification:
-----------------------
generate_case_id(case: dict) -> str

Input: Dictionary with 'problem' and 'solution' keys (plus optional metadata)
Output: Stable ID string in format 'case_<first_16_chars_of_sha256_hash>'

The ID is generated from the concatenation of case["problem"] + case["solution"],
ensuring that:
1. Same content always produces same ID (deterministic)
2. Different content always produces different ID (collision-resistant)
3. Only problem+solution affect ID (metadata doesn't change ID)

Expected ID format example: "case_a7f3b2c1d4e5f6g7"
"""

import hashlib
from typing import Dict, Any

import pytest

# Import will fail initially (TDD - function doesn't exist yet)
from scripts.utilities.setup_vectordb import generate_case_id


# Test data fixtures
BASIC_CASE = {
    "problem": "How do I implement user authentication?",
    "solution": "Use Firebase Authentication with email/password provider.",
    "category": "code",
    "subcategory": "firebase-auth",
    "tags": ["firebase", "auth", "security"],
}

MINIMAL_CASE = {
    "problem": "Test problem text",
    "solution": "Test solution text",
}

CASE_WITH_METADATA = {
    "problem": "Same problem text",
    "solution": "Same solution text",
    "category": "orchestration",
    "subcategory": "planning",
    "tags": ["example", "test"],
}

CASE_WITHOUT_METADATA = {
    "problem": "Same problem text",
    "solution": "Same solution text",
}


def test_generate_case_id_basic_functionality():
    """
    Test: Verify the function generates a content-based SHA-256 hash ID.

    Given: A case dictionary with problem and solution
    When: generate_case_id() is called
    Then: Returns a string in format 'case_<16_char_hex_hash>'
          where the hash portion is exactly 16 hexadecimal characters
    """
    # Given: A basic case with problem and solution
    case = BASIC_CASE

    # When: Generating a case ID
    case_id = generate_case_id(case)

    # Then: ID format is correct
    assert isinstance(case_id, str), "Case ID must be a string"
    assert case_id.startswith("case_"), "Case ID must start with 'case_'"

    # Extract the hash portion
    hash_portion = case_id[5:]  # Remove "case_" prefix
    assert len(hash_portion) == 16, "Hash portion must be exactly 16 characters"

    # Verify it's hexadecimal
    try:
        int(hash_portion, 16)
    except ValueError:
        pytest.fail(f"Hash portion '{hash_portion}' is not valid hexadecimal")


def test_generate_case_id_deterministic():
    """
    Test: Verify same content always generates same ID (deterministic behavior).

    Given: The same case dictionary
    When: generate_case_id() is called multiple times
    Then: All calls produce the exact same ID string
    """
    # Given: A case with specific content
    case = BASIC_CASE

    # When: Generating ID multiple times
    id1 = generate_case_id(case)
    id2 = generate_case_id(case)
    id3 = generate_case_id(case)

    # Generate 10 times to be thorough
    ids = [generate_case_id(case) for _ in range(10)]

    # Then: All IDs are identical
    assert id1 == id2, "Same case must produce same ID on repeated calls"
    assert id1 == id3, "Same case must produce same ID on repeated calls"
    assert len(set(ids)) == 1, "All 10 calls must produce identical IDs"


def test_generate_case_id_unique_content():
    """
    Test: Verify different content generates different IDs.

    Given: Cases with different problem and/or solution text
    When: generate_case_id() is called for each case
    Then: Each case produces a unique ID
    """
    # Given: Cases with different content
    case1 = {
        "problem": "Problem A",
        "solution": "Solution A",
    }
    case2 = {
        "problem": "Problem B",  # Different problem
        "solution": "Solution A",
    }
    case3 = {
        "problem": "Problem A",
        "solution": "Solution B",  # Different solution
    }
    case4 = {
        "problem": "Problem B",
        "solution": "Solution B",  # Both different
    }

    # When: Generating IDs
    id1 = generate_case_id(case1)
    id2 = generate_case_id(case2)
    id3 = generate_case_id(case3)
    id4 = generate_case_id(case4)

    # Then: All IDs are unique
    ids = [id1, id2, id3, id4]
    assert len(set(ids)) == 4, "Different content must produce different IDs"
    assert id1 != id2, "Different problem must produce different ID"
    assert id1 != id3, "Different solution must produce different ID"
    assert id1 != id4, "Different problem+solution must produce different ID"


def test_generate_case_id_minimal_valid_case():
    """
    Test: Verify function works with minimal case structure (only problem + solution).

    Given: A case with only "problem" and "solution" keys (no metadata)
    When: generate_case_id() is called
    Then: Generates valid ID in correct format
    """
    # Given: Minimal case (no category, subcategory, or tags)
    case = MINIMAL_CASE

    # When: Generating case ID
    case_id = generate_case_id(case)

    # Then: Valid ID is produced
    assert isinstance(case_id, str), "Must return string"
    assert case_id.startswith("case_"), "Must have correct prefix"
    assert len(case_id) == 21, "Must be exactly 21 chars (case_ + 16 hex chars)"


def test_generate_case_id_with_metadata_fields():
    """
    Test: Verify category and subcategory affect ID, but tags don't.

    Given: Cases with identical problem/solution but different category/subcategory
    When: generate_case_id() is called for each
    Then: Different category/subcategory produces different IDs
          Different tags alone don't change ID (tags are ignored)
    """
    # Given: Two cases with same problem/solution but different category/subcategory
    case_with_metadata = CASE_WITH_METADATA  # Has orchestration/planning
    case_without_metadata = CASE_WITHOUT_METADATA  # No category/subcategory

    # When: Generating IDs
    id_with = generate_case_id(case_with_metadata)
    id_without = generate_case_id(case_without_metadata)

    # Then: IDs are different (category/subcategory affects ID)
    assert (
        id_with != id_without
    ), "Category and subcategory must affect ID generation"

    # Test: Different category produces different ID
    case_different_category = {
        "problem": "Same problem text",
        "solution": "Same solution text",
        "category": "different_category",
        "subcategory": "planning",  # Same subcategory as CASE_WITH_METADATA
        "tags": ["example", "test"],
    }
    id_different_category = generate_case_id(case_different_category)

    assert (
        id_with != id_different_category
    ), "Different category must produce different ID"

    # Test: Different subcategory produces different ID
    case_different_subcategory = {
        "problem": "Same problem text",
        "solution": "Same solution text",
        "category": "orchestration",  # Same category as CASE_WITH_METADATA
        "subcategory": "different_subcategory",
        "tags": ["example", "test"],
    }
    id_different_subcategory = generate_case_id(case_different_subcategory)

    assert (
        id_with != id_different_subcategory
    ), "Different subcategory must produce different ID"

    # Test: Different tags alone don't change ID
    case_different_tags = {
        "problem": "Same problem text",
        "solution": "Same solution text",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": ["totally", "different", "tags"],  # Different tags
    }
    id_different_tags = generate_case_id(case_different_tags)

    assert (
        id_with == id_different_tags
    ), "Different tags must not change ID (tags are ignored)"


def test_generate_case_id_empty_problem():
    """
    Test: Verify handling of empty problem field.

    Given: A case with empty string in problem field
    When: generate_case_id() is called
    Then: Function handles it without error and generates valid ID
    """
    # Given: Case with empty problem
    case = {
        "problem": "",
        "solution": "Some solution text",
    }

    # When: Generating case ID
    case_id = generate_case_id(case)

    # Then: Valid ID is produced
    assert isinstance(case_id, str), "Must return string even with empty problem"
    assert case_id.startswith("case_"), "Must have correct format"
    assert len(case_id) == 21, "Must be correct length"


def test_generate_case_id_empty_solution():
    """
    Test: Verify handling of empty solution field.

    Given: A case with empty string in solution field
    When: generate_case_id() is called
    Then: Function handles it without error and generates valid ID
    """
    # Given: Case with empty solution
    case = {
        "problem": "Some problem text",
        "solution": "",
    }

    # When: Generating case ID
    case_id = generate_case_id(case)

    # Then: Valid ID is produced
    assert isinstance(case_id, str), "Must return string even with empty solution"
    assert case_id.startswith("case_"), "Must have correct format"
    assert len(case_id) == 21, "Must be correct length"


def test_generate_case_id_both_empty():
    """
    Test: Verify handling when both problem and solution are empty.

    Given: A case with empty strings for both problem and solution
    When: generate_case_id() is called
    Then: Function handles it without error and generates valid ID
          (edge case but should not crash)
    """
    # Given: Case with both fields empty
    case = {
        "problem": "",
        "solution": "",
    }

    # When: Generating case ID
    case_id = generate_case_id(case)

    # Then: Valid ID is produced
    assert isinstance(case_id, str), "Must return string even with empty fields"
    assert case_id.startswith("case_"), "Must have correct format"
    assert len(case_id) == 21, "Must be correct length"


def test_generate_case_id_special_characters():
    """
    Test: Verify handling of special characters in content.

    Given: Cases with newlines, tabs, quotes, and other special characters
    When: generate_case_id() is called
    Then: Function handles them without error and generates valid ID
    """
    # Given: Case with various special characters
    case = {
        "problem": "Problem with\nnewlines\tand\ttabs",
        "solution": 'Solution with "quotes" and \'apostrophes\' and symbols: @#$%^&*()',
    }

    # When: Generating case ID
    case_id = generate_case_id(case)

    # Then: Valid ID is produced
    assert isinstance(case_id, str), "Must handle special characters"
    assert case_id.startswith("case_"), "Must have correct format"
    assert len(case_id) == 21, "Must be correct length"

    # Verify it's deterministic even with special chars
    case_id_2 = generate_case_id(case)
    assert case_id == case_id_2, "Must be deterministic with special characters"


def test_generate_case_id_unicode_characters():
    """
    Test: Verify handling of Unicode characters (emoji, non-ASCII text).

    Given: Cases with Unicode text including emoji, Chinese, Arabic, etc.
    When: generate_case_id() is called
    Then: Function correctly encodes Unicode and generates valid ID
    """
    # Given: Cases with various Unicode content
    cases = [
        {
            "problem": "问题：如何实现用户认证？",  # Chinese
            "solution": "使用 Firebase Authentication",
        },
        {
            "problem": "مشكلة: كيفية تنفيذ المصادقة؟",  # Arabic
            "solution": "استخدم Firebase Authentication",
        },
        {
            "problem": "Problem with emoji 😀🎉🚀",
            "solution": "Solution with symbols ✓✗→",
        },
    ]

    # When: Generating IDs for Unicode cases
    for case in cases:
        case_id = generate_case_id(case)

        # Then: Valid ID is produced
        assert isinstance(case_id, str), "Must handle Unicode characters"
        assert case_id.startswith("case_"), "Must have correct format"
        assert len(case_id) == 21, "Must be correct length"

        # Verify deterministic
        case_id_2 = generate_case_id(case)
        assert case_id == case_id_2, "Must be deterministic with Unicode"


def test_generate_case_id_very_long_content():
    """
    Test: Verify handling of very long problem/solution text.

    Given: A case with very long text (10KB+)
    When: generate_case_id() is called
    Then: Function handles it efficiently and generates valid ID
    """
    # Given: Case with very long content
    long_text = "A" * 10000  # 10KB of text
    case = {
        "problem": long_text,
        "solution": long_text * 2,  # 20KB
    }

    # When: Generating case ID
    case_id = generate_case_id(case)

    # Then: Valid ID is produced
    assert isinstance(case_id, str), "Must handle very long content"
    assert case_id.startswith("case_"), "Must have correct format"
    assert len(case_id) == 21, "Must be correct length"

    # Verify deterministic even with long content
    case_id_2 = generate_case_id(case)
    assert case_id == case_id_2, "Must be deterministic with long content"


def test_generate_case_id_sha256_prefix_verification():
    """
    Test: Verify the hash portion is actually a SHA-256 hash prefix.

    Given: A case with known problem, solution, category, and subcategory
    When: generate_case_id() is called
    Then: The hash portion matches the first 16 chars of manually computed SHA-256 hash
    """
    # Given: Case with known content including metadata
    case = {
        "problem": "Test problem",
        "solution": "Test solution",
        "category": "test_category",
        "subcategory": "test_subcategory",
    }

    # When: Generating case ID
    case_id = generate_case_id(case)

    # Then: Hash matches manual SHA-256 computation
    # Manually compute the expected hash (problem + solution + category + subcategory)
    content = case["problem"] + case["solution"] + case["category"] + case["subcategory"]
    hash_object = hashlib.sha256(content.encode("utf-8"))
    expected_hash_prefix = hash_object.hexdigest()[:16]
    expected_id = f"case_{expected_hash_prefix}"

    assert (
        case_id == expected_id
    ), f"Expected ID '{expected_id}', got '{case_id}'"


def test_generate_case_id_concatenation_order():
    """
    Test: Verify concatenation order is problem + solution (not solution + problem).

    Given: Two cases where one has swapped problem/solution content
    When: generate_case_id() is called for both
    Then: They produce different IDs (order matters)
    """
    # Given: Cases with swapped problem/solution
    case1 = {
        "problem": "Text A",
        "solution": "Text B",
    }
    case2 = {
        "problem": "Text B",
        "solution": "Text A",
    }

    # When: Generating IDs
    id1 = generate_case_id(case1)
    id2 = generate_case_id(case2)

    # Then: IDs are different (order matters)
    assert id1 != id2, "Concatenation order must matter (problem+solution != solution+problem)"
