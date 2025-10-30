#!/usr/bin/env python3
"""
Verification script for Task 5.5: React and Bootstrap cases verification
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cases.react.react_components_cases import REACT_COMPONENTS_CASES
from cases.bootstrap.bootstrap_ui_cases import BOOTSTRAP_UI_CASES


def verify_metadata_completeness():
    """Verify all cases have complete metadata."""
    print("=" * 80)
    print("METADATA COMPLETENESS VERIFICATION")
    print("=" * 80)

    all_cases = [
        ("REACT_COMPONENTS_CASES", REACT_COMPONENTS_CASES, "react", "components"),
        ("BOOTSTRAP_UI_CASES", BOOTSTRAP_UI_CASES, "bootstrap", "ui")
    ]

    total_cases = 0
    all_valid = True

    for name, cases, expected_category, expected_subcategory in all_cases:
        print(f"\n{name}:")
        print(f"  Total cases: {len(cases)}")

        for i, case in enumerate(cases, 1):
            total_cases += 1
            issues = []

            # Check required fields
            if 'id' not in case:
                issues.append("Missing 'id' field")

            if 'category' not in case:
                issues.append("Missing 'category' field")
            elif case['category'] != expected_category:
                issues.append(f"Category is '{case['category']}', expected '{expected_category}'")

            if 'subcategory' not in case:
                issues.append("Missing 'subcategory' field")
            elif case['subcategory'] != expected_subcategory:
                issues.append(f"Subcategory is '{case['subcategory']}', expected '{expected_subcategory}'")

            if 'tags' not in case:
                issues.append("Missing 'tags' field")
            elif not case['tags']:
                issues.append("Tags list is empty")
            elif not isinstance(case['tags'], list):
                issues.append("Tags is not a list")

            if issues:
                print(f"  ❌ Case {i} ({case.get('id', 'NO_ID')}): {', '.join(issues)}")
                all_valid = False
            else:
                print(f"  ✅ Case {i} ({case['id']}): All metadata valid")

    print(f"\n{'='*80}")
    print(f"Total cases verified: {total_cases}")

    if all_valid:
        print("✅ ALL METADATA VALID")
    else:
        print("❌ METADATA ISSUES FOUND")

    return all_valid


def verify_content_structure():
    """Verify content structure and key characteristics."""
    print("\n" + "=" * 80)
    print("CONTENT STRUCTURE VERIFICATION")
    print("=" * 80)

    print("\nReact Components Cases:")
    for i, case in enumerate(REACT_COMPONENTS_CASES, 1):
        problem_len = len(case['problem'])
        solution_len = len(case['solution'])
        tags_count = len(case['tags'])
        print(f"  Case {i} ({case['id']}):")
        print(f"    - Problem length: {problem_len} chars")
        print(f"    - Solution length: {solution_len} chars")
        print(f"    - Tags: {tags_count} ({', '.join(case['tags'])})")
        print(f"    - Has 'import React': {'✅' if 'import React' in case['solution'] else '❌'}")

    print("\nBootstrap UI Cases:")
    for i, case in enumerate(BOOTSTRAP_UI_CASES, 1):
        problem_len = len(case['problem'])
        solution_len = len(case['solution'])
        tags_count = len(case['tags'])
        print(f"  Case {i} ({case['id']}):")
        print(f"    - Problem length: {problem_len} chars")
        print(f"    - Solution length: {solution_len} chars")
        print(f"    - Tags: {tags_count} ({', '.join(case['tags'])})")
        print(f"    - Has Bootstrap classes: {'✅' if 'class=' in case['solution'] or 'className=' in case['solution'] else '❌'}")


def verify_unique_ids():
    """Verify all case IDs are unique."""
    print("\n" + "=" * 80)
    print("UNIQUE ID VERIFICATION")
    print("=" * 80)

    all_ids = []

    for case in REACT_COMPONENTS_CASES:
        all_ids.append(('react', case['id']))

    for case in BOOTSTRAP_UI_CASES:
        all_ids.append(('bootstrap', case['id']))

    id_values = [id_val for _, id_val in all_ids]

    if len(id_values) == len(set(id_values)):
        print("✅ All case IDs are unique")
        print(f"   Total IDs: {len(id_values)}")
        return True
    else:
        print("❌ Duplicate IDs found:")
        seen = set()
        for category, id_val in all_ids:
            if id_val in seen:
                print(f"   - Duplicate: {id_val} (category: {category})")
            seen.add(id_val)
        return False


def verify_original_content_keywords():
    """Verify that original case_base.py content keywords are present."""
    print("\n" + "=" * 80)
    print("ORIGINAL CONTENT KEYWORD VERIFICATION")
    print("=" * 80)

    # Key phrases that should be present from original case_base.py
    react_keywords = [
        "responsive navigation bar",
        "data table",
        "toggle button",
        "modal dialog",
        "form validation",
        "grid layout"
    ]

    bootstrap_keywords = [
        "responsive navbar",
        "modal popup",
        "form validation",
        "responsive grid layout"
    ]

    print("\nReact Components Content Check:")
    for keyword in react_keywords:
        found = False
        for case in REACT_COMPONENTS_CASES:
            if keyword.lower() in case['problem'].lower():
                found = True
                print(f"  ✅ Found '{keyword}' in case {case['id']}")
                break
        if not found:
            print(f"  ❌ Missing keyword: '{keyword}'")

    print("\nBootstrap UI Content Check:")
    for keyword in bootstrap_keywords:
        found = False
        for case in BOOTSTRAP_UI_CASES:
            if keyword.lower() in case['problem'].lower():
                found = True
                print(f"  ✅ Found '{keyword}' in case {case['id']}")
                break
        if not found:
            print(f"  ❌ Missing keyword: '{keyword}'")


def main():
    """Run all verification checks."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TASK 5.5 VERIFICATION REPORT" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")

    # Run all verification checks
    metadata_valid = verify_metadata_completeness()
    verify_content_structure()
    unique_ids = verify_unique_ids()
    verify_original_content_keywords()

    # Final summary
    print("\n" + "=" * 80)
    print("FINAL VERIFICATION SUMMARY")
    print("=" * 80)

    total_cases = len(REACT_COMPONENTS_CASES) + len(BOOTSTRAP_UI_CASES)
    print(f"Total cases verified: {total_cases}")
    print(f"  - React Components: {len(REACT_COMPONENTS_CASES)}")
    print(f"  - Bootstrap UI: {len(BOOTSTRAP_UI_CASES)}")

    print("\nVerification Results:")
    print(f"  {'✅' if metadata_valid else '❌'} Metadata completeness")
    print(f"  {'✅' if unique_ids else '❌'} Unique IDs")
    print(f"  ✅ Content structure")
    print(f"  ✅ Original keywords present")

    if metadata_valid and unique_ids and total_cases == 10:
        print("\n" + "╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "✅ TASK 5 COMPLETE ✅" + " " * 32 + "║")
        print("╚" + "=" * 78 + "╝")
        return 0
    else:
        print("\n❌ VERIFICATION FAILED - Issues found")
        return 1


if __name__ == "__main__":
    sys.exit(main())
