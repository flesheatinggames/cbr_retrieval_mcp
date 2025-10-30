"""
Test suite for cases.webdev.webdev_forms_validation_cases module.

This test suite validates the web development forms validation cases module
following TDD principles. Tests verify module structure, metadata, and content
preservation from the original case_base.py file.
"""

import pytest


def test_module_import():
    """
    Test that the webdev_forms_validation_cases module can be imported successfully.

    This test verifies:
    - Module can be imported without ImportError
    - Module object is not None
    """
    import cases.webdev.webdev_forms_validation_cases as module
    assert module is not None


def test_cases_variable_exists():
    """
    Test that WEBDEV_FORMS_VALIDATION_CASES variable exists and is a list.

    This test verifies:
    - Variable WEBDEV_FORMS_VALIDATION_CASES is defined in the module
    - Variable is of type list
    """
    from cases.webdev import webdev_forms_validation_cases

    assert hasattr(webdev_forms_validation_cases, 'WEBDEV_FORMS_VALIDATION_CASES')
    assert isinstance(webdev_forms_validation_cases.WEBDEV_FORMS_VALIDATION_CASES, list)


def test_case_count():
    """
    Test that the cases list contains exactly 3 cases.

    This test verifies:
    - WEBDEV_FORMS_VALIDATION_CASES list has exactly 3 elements
    """
    from cases.webdev.webdev_forms_validation_cases import WEBDEV_FORMS_VALIDATION_CASES

    assert len(WEBDEV_FORMS_VALIDATION_CASES) == 3


def test_all_cases_have_required_metadata():
    """
    Test that all cases have required metadata fields with correct values.

    This test verifies each case has:
    - category: "webdev"
    - subcategory: "forms-validation"
    - tags: list with at least 2 tags containing relevant keywords
    """
    from cases.webdev.webdev_forms_validation_cases import WEBDEV_FORMS_VALIDATION_CASES

    required_keywords = {'forms', 'validation', 'zod', 'schemas', 'client-side', 'server-side'}

    for i, case in enumerate(WEBDEV_FORMS_VALIDATION_CASES):
        # Check category
        assert 'category' in case, f"Case {i} missing 'category' field"
        assert case['category'] == 'webdev', f"Case {i} has incorrect category: {case['category']}"

        # Check subcategory
        assert 'subcategory' in case, f"Case {i} missing 'subcategory' field"
        assert case['subcategory'] == 'forms-validation', f"Case {i} has incorrect subcategory: {case['subcategory']}"

        # Check tags
        assert 'tags' in case, f"Case {i} missing 'tags' field"
        assert isinstance(case['tags'], list), f"Case {i} tags is not a list"
        assert len(case['tags']) >= 2, f"Case {i} has fewer than 2 tags"

        # Check for relevant keywords in tags
        case_tags_lower = [tag.lower() for tag in case['tags']]
        has_relevant_keyword = any(
            keyword in ' '.join(case_tags_lower) for keyword in required_keywords
        )
        assert has_relevant_keyword, f"Case {i} tags do not contain relevant keywords: {case['tags']}"


def test_all_cases_have_required_fields():
    """
    Test that all cases have problem and solution fields with non-empty content.

    This test verifies each case has:
    - problem: non-empty string
    - solution: non-empty string
    """
    from cases.webdev.webdev_forms_validation_cases import WEBDEV_FORMS_VALIDATION_CASES

    for i, case in enumerate(WEBDEV_FORMS_VALIDATION_CASES):
        # Check problem field
        assert 'problem' in case, f"Case {i} missing 'problem' field"
        assert isinstance(case['problem'], str), f"Case {i} problem is not a string"
        assert len(case['problem'].strip()) > 0, f"Case {i} has empty problem field"

        # Check solution field
        assert 'solution' in case, f"Case {i} missing 'solution' field"
        assert isinstance(case['solution'], str), f"Case {i} solution is not a string"
        assert len(case['solution'].strip()) > 0, f"Case {i} has empty solution field"


def test_content_preservation_client_side_validation():
    """
    Test that client-side validation case content is preserved from original.

    This test verifies:
    - One case's problem description contains "client-side form validation"
    - Case includes relevant client-side validation patterns
    """
    from cases.webdev.webdev_forms_validation_cases import WEBDEV_FORMS_VALIDATION_CASES

    client_side_indicators = [
        'client-side',
        'client side',
        'browser validation',
        'html5 validation',
        'form validation in react'
    ]

    found_client_side_case = False
    for case in WEBDEV_FORMS_VALIDATION_CASES:
        problem_lower = case['problem'].lower()
        if any(indicator in problem_lower for indicator in client_side_indicators):
            found_client_side_case = True
            # Verify it's a forms/validation related case
            assert 'form' in problem_lower or 'validation' in problem_lower
            break

    assert found_client_side_case, "No client-side validation case found"


def test_content_preservation_server_side_validation():
    """
    Test that server-side validation case content is preserved from original.

    This test verifies:
    - One case's problem description contains "server-side form validation"
    - Case includes relevant server-side validation patterns
    """
    from cases.webdev.webdev_forms_validation_cases import WEBDEV_FORMS_VALIDATION_CASES

    server_side_indicators = [
        'server-side',
        'server side',
        'backend validation',
        'api validation',
        'express validation'
    ]

    found_server_side_case = False
    for case in WEBDEV_FORMS_VALIDATION_CASES:
        problem_lower = case['problem'].lower()
        if any(indicator in problem_lower for indicator in server_side_indicators):
            found_server_side_case = True
            # Verify it's a forms/validation related case
            assert 'form' in problem_lower or 'validation' in problem_lower
            break

    assert found_server_side_case, "No server-side validation case found"


def test_content_preservation_zod_schema():
    """
    Test that Zod schema validation case content is preserved from original.

    This test verifies:
    - One case's problem description contains "Zod" or "schema validation"
    - Case includes Zod-specific patterns
    """
    from cases.webdev.webdev_forms_validation_cases import WEBDEV_FORMS_VALIDATION_CASES

    zod_indicators = [
        'zod',
        'schema validation',
        'type-safe validation',
        'typescript validation'
    ]

    found_zod_case = False
    for case in WEBDEV_FORMS_VALIDATION_CASES:
        problem_lower = case['problem'].lower()
        solution_lower = case['solution'].lower()
        combined = problem_lower + ' ' + solution_lower

        if any(indicator in combined for indicator in zod_indicators):
            found_zod_case = True
            # Verify it's a validation related case
            assert 'validation' in combined or 'schema' in combined
            break

    assert found_zod_case, "No Zod schema validation case found"
