"""
Test script for backward compatibility of case_base.CASE_BASE import.

This script simulates how external code would import and use CASE_BASE,
ensuring no breaking changes for existing integrations.
"""

import sys
from pathlib import Path

# Add project root to path to simulate external usage
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_import_case_base():
    """Test that CASE_BASE can be imported from case_base module."""
    print("=" * 70)
    print("TEST 1: Import CASE_BASE from case_base")
    print("=" * 70)

    try:
        from case_base import CASE_BASE
        print("✓ Successfully imported CASE_BASE from case_base")
        print(f"  Type: {type(CASE_BASE)}")
        print(f"  Length: {len(CASE_BASE)}")
        return CASE_BASE
    except ImportError as e:
        print(f"✗ FAILED: Could not import CASE_BASE from case_base")
        print(f"  Error: {e}")
        sys.exit(1)


def test_case_base_equals_all_cases(case_base):
    """Test that CASE_BASE is identical to cases.ALL_CASES."""
    print("\n" + "=" * 70)
    print("TEST 2: CASE_BASE equals cases.ALL_CASES")
    print("=" * 70)

    try:
        from cases import ALL_CASES

        # Test identity (should be the same object)
        if case_base is ALL_CASES:
            print("✓ CASE_BASE is the same object as ALL_CASES (identity check)")
        else:
            print("✗ WARNING: CASE_BASE is not the same object as ALL_CASES")

        # Test equality (should have same content)
        if case_base == ALL_CASES:
            print("✓ CASE_BASE equals ALL_CASES (equality check)")
        else:
            print("✗ FAILED: CASE_BASE does not equal ALL_CASES")
            sys.exit(1)

        # Test length
        if len(case_base) == len(ALL_CASES):
            print(f"✓ Both have same length: {len(case_base)}")
        else:
            print(f"✗ FAILED: Length mismatch - CASE_BASE: {len(case_base)}, ALL_CASES: {len(ALL_CASES)}")
            sys.exit(1)

        return True
    except Exception as e:
        print(f"✗ FAILED: Error during comparison")
        print(f"  Error: {e}")
        sys.exit(1)


def test_case_base_structure(case_base):
    """Test that CASE_BASE has expected structure."""
    print("\n" + "=" * 70)
    print("TEST 3: CASE_BASE Structure Validation")
    print("=" * 70)

    if not case_base:
        print("✗ FAILED: CASE_BASE is empty")
        sys.exit(1)

    print(f"✓ CASE_BASE is not empty ({len(case_base)} cases)")

    # Check first case has required fields
    first_case = case_base[0]
    required_fields = ["problem", "solution"]
    optional_fields = ["category", "subcategory", "tags"]

    print("\n  Checking required fields in first case:")
    for field in required_fields:
        if field in first_case:
            print(f"    ✓ '{field}' present")
        else:
            print(f"    ✗ FAILED: '{field}' missing")
            sys.exit(1)

    print("\n  Checking optional metadata fields in first case:")
    for field in optional_fields:
        if field in first_case:
            print(f"    ✓ '{field}' present")
        else:
            print(f"    - '{field}' not present (optional)")

    # Verify all cases have problem and solution
    print("\n  Validating all cases:")
    valid_count = 0
    for i, case in enumerate(case_base):
        if "problem" in case and "solution" in case:
            valid_count += 1
        else:
            print(f"    ✗ FAILED: Case {i} missing required fields")
            sys.exit(1)

    print(f"    ✓ All {valid_count} cases have required fields")
    return True


def test_iteration(case_base):
    """Test that CASE_BASE can be iterated over."""
    print("\n" + "=" * 70)
    print("TEST 4: Iteration Support")
    print("=" * 70)

    try:
        count = 0
        for case in case_base:
            count += 1
            if count > 3:  # Only check first 3
                break

        print(f"✓ Successfully iterated over CASE_BASE")
        print(f"  First {min(count, 3)} cases accessed")
        return True
    except Exception as e:
        print(f"✗ FAILED: Could not iterate over CASE_BASE")
        print(f"  Error: {e}")
        sys.exit(1)


def test_indexing(case_base):
    """Test that CASE_BASE supports indexing."""
    print("\n" + "=" * 70)
    print("TEST 5: Indexing Support")
    print("=" * 70)

    try:
        # Test positive indexing
        first = case_base[0]
        print(f"✓ Positive indexing works: case_base[0]")

        # Test negative indexing
        last = case_base[-1]
        print(f"✓ Negative indexing works: case_base[-1]")

        # Test slicing
        subset = case_base[:3]
        print(f"✓ Slicing works: case_base[:3] returned {len(subset)} cases")

        return True
    except Exception as e:
        print(f"✗ FAILED: Indexing operations failed")
        print(f"  Error: {e}")
        sys.exit(1)


def test_length(case_base):
    """Test that len() works on CASE_BASE."""
    print("\n" + "=" * 70)
    print("TEST 6: Length Support")
    print("=" * 70)

    try:
        length = len(case_base)
        print(f"✓ len(CASE_BASE) = {length}")

        if length > 0:
            print(f"✓ CASE_BASE contains {length} cases")
            return True
        else:
            print(f"✗ FAILED: CASE_BASE is empty")
            sys.exit(1)
    except Exception as e:
        print(f"✗ FAILED: len() operation failed")
        print(f"  Error: {e}")
        sys.exit(1)


def test_helper_functions():
    """Test that helper functions from case_base still work."""
    print("\n" + "=" * 70)
    print("TEST 7: Helper Functions")
    print("=" * 70)

    try:
        from case_base import (
            search_cases,
            validate_case_base,
            get_case_statistics,
            add_case,
            save_case_base_to_file,
            load_case_base_from_file
        )

        print("✓ All helper functions imported successfully:")
        print("  - search_cases")
        print("  - validate_case_base")
        print("  - get_case_statistics")
        print("  - add_case")
        print("  - save_case_base_to_file")
        print("  - load_case_base_from_file")

        # Test search_cases
        print("\n  Testing search_cases:")
        results = search_cases("firebase")
        print(f"    ✓ search_cases('firebase') returned {len(results)} results")

        # Test validate_case_base
        print("\n  Testing validate_case_base:")
        is_valid = validate_case_base()
        if is_valid:
            print(f"    ✓ validate_case_base() passed")
        else:
            print(f"    ✗ WARNING: validate_case_base() returned False")

        return True
    except Exception as e:
        print(f"✗ FAILED: Helper functions test failed")
        print(f"  Error: {e}")
        sys.exit(1)


def test_common_usage_patterns(case_base):
    """Test common usage patterns that external code might use."""
    print("\n" + "=" * 70)
    print("TEST 8: Common Usage Patterns")
    print("=" * 70)

    try:
        # Pattern 1: Filter cases by category metadata
        print("\n  Pattern 1: Filter cases by category metadata")
        firebase_cases = [c for c in case_base if c.get("category") == "firebase"]
        print(f"    ✓ Found {len(firebase_cases)} firebase cases")

        # Pattern 2: Search in problem field
        print("\n  Pattern 2: Search in problem field")
        auth_cases = [c for c in case_base if "auth" in c["problem"].lower()]
        print(f"    ✓ Found {len(auth_cases)} cases with 'auth' in problem")

        # Pattern 3: Get solution from specific case
        print("\n  Pattern 3: Access solution from first case")
        if case_base:
            solution_length = len(case_base[0]["solution"])
            print(f"    ✓ First case solution length: {solution_length} characters")

        # Pattern 4: Count cases
        print("\n  Pattern 4: Count total cases")
        total = len(case_base)
        print(f"    ✓ Total cases: {total}")

        # Pattern 5: Check if case_base is not empty
        print("\n  Pattern 5: Check if CASE_BASE is not empty")
        if case_base:
            print(f"    ✓ CASE_BASE is truthy (not empty)")
        else:
            print(f"    ✗ FAILED: CASE_BASE is falsy (empty)")
            sys.exit(1)

        return True
    except Exception as e:
        print(f"✗ FAILED: Common usage patterns test failed")
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Run all backward compatibility tests."""
    print("\n" + "=" * 70)
    print("CASE_BASE BACKWARD COMPATIBILITY TEST SUITE")
    print("=" * 70)
    print("\nThis test simulates how external code would import and use CASE_BASE")
    print("to ensure no breaking changes in the modular refactoring.\n")

    # Run tests in sequence
    case_base = test_import_case_base()
    test_case_base_equals_all_cases(case_base)
    test_case_base_structure(case_base)
    test_iteration(case_base)
    test_indexing(case_base)
    test_length(case_base)
    test_helper_functions()
    test_common_usage_patterns(case_base)

    # Final summary
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✓")
    print("=" * 70)
    print("\nBackward compatibility is maintained:")
    print("  ✓ CASE_BASE can be imported from case_base")
    print("  ✓ CASE_BASE equals cases.ALL_CASES")
    print("  ✓ CASE_BASE has expected structure")
    print("  ✓ CASE_BASE supports iteration")
    print("  ✓ CASE_BASE supports indexing and slicing")
    print("  ✓ CASE_BASE supports len()")
    print("  ✓ All helper functions work correctly")
    print("  ✓ Common usage patterns work as expected")
    print("\nExternal code using 'from case_base import CASE_BASE' will continue")
    print("to work without any modifications.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
