"""Unit tests for identify_new_cases() function in setup_vectordb.py

This test suite validates the deduplication logic that identifies which cases
are new vs. already existing in the ChromaDB collection. These tests follow
Test-Driven Development (TDD) principles and are written BEFORE implementation.

Function Specification:
-----------------------
identify_new_cases(all_cases: List[Dict], collection) -> Tuple[List[Dict], int]

Input:
  - all_cases: List of case dictionaries to check against database
  - collection: ChromaDB collection object to query for existing IDs

Output:
  - Tuple containing:
    1. List of new cases (not in database)
    2. Count of skipped cases (already in database)

The function determines which cases need to be added to the database by:
1. Generating content-based IDs for all input cases
2. Querying the collection for existing case IDs
3. Comparing sets to identify new cases
4. Returning only new cases and count of duplicates skipped

This enables incremental database updates without duplicates.
"""

import time
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

import pytest

# Import will fail initially (TDD - function doesn't exist yet)
from scripts.utilities.setup_vectordb import identify_new_cases, generate_case_id


# Test data fixtures
CASE_1 = {
    "problem": "How to implement authentication?",
    "solution": "Use Firebase Auth with email/password.",
    "category": "code",
    "subcategory": "firebase-auth",
}

CASE_2 = {
    "problem": "How to handle form validation?",
    "solution": "Use client-side validation with server-side verification.",
    "category": "code",
    "subcategory": "forms",
}

CASE_3 = {
    "problem": "How to deploy Next.js app?",
    "solution": "Deploy to Vercel with automatic CI/CD.",
    "category": "orchestration",
    "subcategory": "deployment",
}

CASE_4 = {
    "problem": "How to optimize React performance?",
    "solution": "Use React.memo and useMemo hooks.",
    "category": "code",
    "subcategory": "react-components",
}

CASE_5 = {
    "problem": "How to secure API endpoints?",
    "solution": "Implement JWT authentication with rate limiting.",
    "category": "security",
    "subcategory": "api-security",
}


def create_mock_collection(existing_ids: List[str]) -> Mock:
    """Helper to create a mock ChromaDB collection with specific existing IDs.

    Args:
        existing_ids: List of case IDs to simulate as existing in database

    Returns:
        Mock collection object with get() method
    """
    mock_collection = Mock()
    mock_collection.get.return_value = {"ids": existing_ids}
    return mock_collection


def test_identify_new_cases_all_new_cases_empty_collection():
    """
    Test: Verify all cases are identified as new when collection is empty.

    Given: A list of cases and an empty ChromaDB collection
    When: identify_new_cases() is called
    Then: Returns all cases as new, skipped count = 0
    """
    # Given: Three cases and an empty collection
    all_cases = [CASE_1, CASE_2, CASE_3]
    mock_collection = create_mock_collection([])

    # When: Identifying new cases
    new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)

    # Then: All cases are new, none skipped
    assert isinstance(new_cases, list), "new_cases must be a list"
    assert isinstance(skipped_count, int), "skipped_count must be an integer"
    assert len(new_cases) == 3, "All 3 cases should be new"
    assert skipped_count == 0, "No cases should be skipped"
    assert new_cases == all_cases, "New cases should match input cases"


def test_identify_new_cases_all_existing_cases():
    """
    Test: Verify all cases are skipped when they already exist in database.

    Given: A list of cases where all IDs already exist in the collection
    When: identify_new_cases() is called
    Then: Returns empty list for new cases, skipped count = len(all_cases)
    """
    # Given: Three cases, all existing in collection
    all_cases = [CASE_1, CASE_2, CASE_3]

    # Generate IDs for all cases to simulate they exist
    existing_ids = [generate_case_id(case) for case in all_cases]
    mock_collection = create_mock_collection(existing_ids)

    # When: Identifying new cases
    new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)

    # Then: No new cases, all skipped
    assert len(new_cases) == 0, "No cases should be new"
    assert skipped_count == 3, "All 3 cases should be skipped"
    assert new_cases == [], "New cases list should be empty"


def test_identify_new_cases_mixed_new_and_existing():
    """
    Test: Verify correct separation of new vs existing cases.

    Given: A list of 5 cases where 2 already exist and 3 are new
    When: identify_new_cases() is called
    Then: Returns list of 3 new cases, skipped count = 2
    """
    # Given: Five cases, two exist in collection
    all_cases = [CASE_1, CASE_2, CASE_3, CASE_4, CASE_5]

    # Only CASE_1 and CASE_3 exist in database
    existing_ids = [generate_case_id(CASE_1), generate_case_id(CASE_3)]
    mock_collection = create_mock_collection(existing_ids)

    # When: Identifying new cases
    new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)

    # Then: CASE_2, CASE_4, CASE_5 are new; CASE_1, CASE_3 skipped
    assert len(new_cases) == 3, "Should have 3 new cases"
    assert skipped_count == 2, "Should skip 2 existing cases"

    # Verify correct cases are identified as new
    new_case_ids = [generate_case_id(case) for case in new_cases]
    expected_new_ids = [
        generate_case_id(CASE_2),
        generate_case_id(CASE_4),
        generate_case_id(CASE_5),
    ]
    assert set(new_case_ids) == set(expected_new_ids), "Wrong cases identified as new"


def test_identify_new_cases_large_case_set_performance():
    """
    Test: Verify performance with large number of cases (1000+).

    Given: A list of 1000 cases with 500 existing in database
    When: identify_new_cases() is called
    Then: Function completes in reasonable time (<1 second), returns correct results
    """
    # Given: 1000 cases (500 new, 500 existing)
    all_cases = []
    for i in range(1000):
        case = {
            "problem": f"Problem {i}",
            "solution": f"Solution {i}",
        }
        all_cases.append(case)

    # First 500 cases exist in database
    existing_ids = [generate_case_id(case) for case in all_cases[:500]]
    mock_collection = create_mock_collection(existing_ids)

    # When: Identifying new cases (measure performance)
    start_time = time.time()
    new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)
    elapsed_time = time.time() - start_time

    # Then: Correct results and reasonable performance
    assert len(new_cases) == 500, "Should identify 500 new cases"
    assert skipped_count == 500, "Should skip 500 existing cases"
    assert elapsed_time < 1.0, f"Should complete in <1 second, took {elapsed_time:.2f}s"


def test_identify_new_cases_chromadb_exception_handling():
    """
    Test: Verify graceful handling when ChromaDB query fails.

    Given: A ChromaDB collection that raises an exception on get()
    When: identify_new_cases() is called
    Then: Treats all cases as new (defensive behavior, no crash)
    """
    # Given: Collection that throws exception
    mock_collection = Mock()
    mock_collection.get.side_effect = Exception("Database connection error")

    all_cases = [CASE_1, CASE_2, CASE_3]

    # When: Identifying new cases
    new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)

    # Then: Treats all as new (defensive fallback)
    assert len(new_cases) == 3, "Should treat all cases as new on error"
    assert skipped_count == 0, "Should not skip any cases on error"


def test_identify_new_cases_empty_input_list():
    """
    Test: Verify handling of empty input case list.

    Given: An empty list of cases
    When: identify_new_cases() is called
    Then: Returns empty list, skipped count = 0
    """
    # Given: Empty case list
    all_cases = []
    mock_collection = create_mock_collection([generate_case_id(CASE_1)])

    # When: Identifying new cases
    new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)

    # Then: Empty results
    assert len(new_cases) == 0, "Should return empty list for empty input"
    assert skipped_count == 0, "Should skip 0 cases for empty input"
    assert new_cases == [], "New cases should be empty list"


def test_identify_new_cases_malformed_case_ids_in_database():
    """
    Test: Verify handling when database contains non-standard ID formats.

    Given: ChromaDB collection with malformed IDs (missing prefix, wrong length)
    When: identify_new_cases() is called
    Then: Function handles gracefully, comparison works correctly
    """
    # Given: Cases and collection with mix of good and malformed IDs
    all_cases = [CASE_1, CASE_2, CASE_3]

    # Create malformed IDs: missing prefix, wrong length, etc.
    valid_id = generate_case_id(CASE_1)
    malformed_ids = [
        valid_id,  # One valid ID
        "malformed_id_without_prefix",  # No "case_" prefix
        "case_",  # Missing hash portion
        "case_abc",  # Too short hash
        "not_a_case_id_at_all",  # Completely wrong format
    ]

    mock_collection = create_mock_collection(malformed_ids)

    # When: Identifying new cases
    new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)

    # Then: CASE_1 is skipped (valid match), others are new
    assert len(new_cases) == 2, "Should identify 2 new cases (CASE_2, CASE_3)"
    assert skipped_count == 1, "Should skip 1 case (CASE_1)"

    # Verify CASE_2 and CASE_3 are in new_cases
    new_case_ids = [generate_case_id(case) for case in new_cases]
    expected_ids = [generate_case_id(CASE_2), generate_case_id(CASE_3)]
    assert set(new_case_ids) == set(expected_ids), "Wrong cases identified as new"


def test_identify_new_cases_missing_problem_field():
    """
    Test: Verify handling when case is missing 'problem' field.

    Given: A case dictionary without 'problem' key
    When: identify_new_cases() is called
    Then: Function handles missing field gracefully (may raise KeyError or skip)

    Note: This tests defensive behavior - implementation should either:
    1. Raise clear KeyError for invalid case structure
    2. Skip the malformed case with appropriate logging
    """
    # Given: Case missing 'problem' field
    malformed_case = {
        "solution": "Some solution",
        "category": "code",
    }
    all_cases = [CASE_1, malformed_case, CASE_2]
    mock_collection = create_mock_collection([])

    # When/Then: Either raises KeyError or handles gracefully
    try:
        new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)
        # If no exception, verify function handled it somehow
        assert isinstance(new_cases, list), "Should return a list"
        assert isinstance(skipped_count, int), "Should return an integer"
    except KeyError as e:
        # Acceptable to raise KeyError for invalid case structure
        assert "problem" in str(e).lower(), "KeyError should mention 'problem' field"


def test_identify_new_cases_missing_solution_field():
    """
    Test: Verify handling when case is missing 'solution' field.

    Given: A case dictionary without 'solution' key
    When: identify_new_cases() is called
    Then: Function handles missing field gracefully (may raise KeyError or skip)
    """
    # Given: Case missing 'solution' field
    malformed_case = {
        "problem": "Some problem",
        "category": "code",
    }
    all_cases = [CASE_1, malformed_case, CASE_2]
    mock_collection = create_mock_collection([])

    # When/Then: Either raises KeyError or handles gracefully
    try:
        new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)
        # If no exception, verify function handled it somehow
        assert isinstance(new_cases, list), "Should return a list"
        assert isinstance(skipped_count, int), "Should return an integer"
    except KeyError as e:
        # Acceptable to raise KeyError for invalid case structure
        assert "solution" in str(e).lower(), "KeyError should mention 'solution' field"


def test_identify_new_cases_preserves_case_order():
    """
    Test: Verify new cases list preserves original input order.

    Given: A list of cases in specific order, some existing and some new
    When: identify_new_cases() is called
    Then: New cases appear in same relative order as input
    """
    # Given: Five cases in specific order, alternating new/existing
    all_cases = [CASE_1, CASE_2, CASE_3, CASE_4, CASE_5]

    # Cases 2 and 4 exist (positions 1 and 3)
    existing_ids = [generate_case_id(CASE_2), generate_case_id(CASE_4)]
    mock_collection = create_mock_collection(existing_ids)

    # When: Identifying new cases
    new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)

    # Then: New cases maintain order: CASE_1, CASE_3, CASE_5
    assert len(new_cases) == 3, "Should have 3 new cases"

    # Verify order is preserved
    expected_order = [CASE_1, CASE_3, CASE_5]
    for i, expected_case in enumerate(expected_order):
        assert generate_case_id(new_cases[i]) == generate_case_id(expected_case), \
            f"Case at position {i} does not match expected order"


def test_identify_new_cases_return_type_validation():
    """
    Test: Verify return type is correct (tuple of list and int).

    Given: Any valid input cases and collection
    When: identify_new_cases() is called
    Then: Returns a tuple where first element is list, second is int
    """
    # Given: Basic setup
    all_cases = [CASE_1, CASE_2]
    mock_collection = create_mock_collection([])

    # When: Calling function
    result = identify_new_cases(all_cases, mock_collection)

    # Then: Verify return type structure
    assert isinstance(result, tuple), "Must return a tuple"
    assert len(result) == 2, "Tuple must have exactly 2 elements"

    new_cases, skipped_count = result
    assert isinstance(new_cases, list), "First element must be a list"
    assert isinstance(skipped_count, int), "Second element must be an integer"
    assert skipped_count >= 0, "Skipped count must be non-negative"


def test_identify_new_cases_uses_generate_case_id():
    """
    Test: Verify function uses generate_case_id() for ID generation.

    Given: A list of cases
    When: identify_new_cases() is called
    Then: generate_case_id() is called for each case to compute IDs
    """
    # Given: Cases and mock collection
    all_cases = [CASE_1, CASE_2, CASE_3]
    mock_collection = create_mock_collection([])

    # When: Calling function with patched generate_case_id
    with patch("scripts.utilities.setup_vectordb.generate_case_id",
               wraps=generate_case_id) as mock_gen_id:
        new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)

        # Then: generate_case_id was called for each case
        assert mock_gen_id.call_count >= len(all_cases), \
            f"generate_case_id should be called at least {len(all_cases)} times"


def test_identify_new_cases_none_collection_handling():
    """
    Test: Verify handling when collection parameter is None.

    Given: Valid cases but None as collection parameter
    When: identify_new_cases() is called
    Then: Either raises TypeError or treats all as new (defensive)
    """
    # Given: Cases with None collection
    all_cases = [CASE_1, CASE_2]

    # When/Then: Should handle None gracefully
    try:
        new_cases, skipped_count = identify_new_cases(all_cases, None)
        # If no exception, verify defensive behavior
        assert len(new_cases) == len(all_cases), "Should treat all as new if collection is None"
    except (TypeError, AttributeError) as e:
        # Acceptable to raise error for invalid collection parameter
        pass


def test_identify_new_cases_collection_with_none_ids():
    """
    Test: Verify handling when collection.get() returns None for 'ids'.

    Given: A collection that returns {'ids': None}
    When: identify_new_cases() is called
    Then: Treats all cases as new (no existing IDs to compare)
    """
    # Given: Collection returning None for IDs
    mock_collection = Mock()
    mock_collection.get.return_value = {"ids": None}

    all_cases = [CASE_1, CASE_2, CASE_3]

    # When: Identifying new cases
    new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)

    # Then: All cases treated as new
    assert len(new_cases) == 3, "Should treat all cases as new when IDs is None"
    assert skipped_count == 0, "Should not skip any cases"


def test_identify_new_cases_collection_returns_empty_dict():
    """
    Test: Verify handling when collection.get() returns empty dict.

    Given: A collection that returns {} (no 'ids' key)
    When: identify_new_cases() is called
    Then: Treats all cases as new (defensive behavior)
    """
    # Given: Collection returning empty dict
    mock_collection = Mock()
    mock_collection.get.return_value = {}

    all_cases = [CASE_1, CASE_2, CASE_3]

    # When: Identifying new cases
    new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)

    # Then: All cases treated as new
    assert len(new_cases) == 3, "Should treat all cases as new when 'ids' key missing"
    assert skipped_count == 0, "Should not skip any cases"


def test_identify_new_cases_skipped_count_accuracy():
    """
    Test: Verify skipped count equals number of existing cases found.

    Given: Various scenarios with different numbers of existing cases
    When: identify_new_cases() is called
    Then: skipped_count always equals len(all_cases) - len(new_cases)
    """
    test_scenarios = [
        ([], 0),  # No existing cases
        ([CASE_1], 1),  # One existing
        ([CASE_1, CASE_2], 2),  # Two existing
        ([CASE_1, CASE_2, CASE_3], 3),  # All existing
    ]

    all_cases = [CASE_1, CASE_2, CASE_3]

    for existing_cases, expected_skipped in test_scenarios:
        # Given: Collection with specific existing cases
        existing_ids = [generate_case_id(case) for case in existing_cases]
        mock_collection = create_mock_collection(existing_ids)

        # When: Identifying new cases
        new_cases, skipped_count = identify_new_cases(all_cases, mock_collection)

        # Then: skipped_count matches expected
        assert skipped_count == expected_skipped, \
            f"Expected {expected_skipped} skipped, got {skipped_count}"

        # Verify consistency: new + skipped = total
        assert len(new_cases) + skipped_count == len(all_cases), \
            "new_cases count + skipped_count must equal total input cases"
