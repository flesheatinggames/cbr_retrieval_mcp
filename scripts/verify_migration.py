#!/usr/bin/env python3
"""
Migration Verification Script for CBR MCP Server

This script verifies that all 76 cases from case_base.py have been
successfully migrated to the modular structure in cases/.

It matches cases by their problem field and generates a detailed report
of matched and missing cases.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Set

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from case_base import CASE_BASE, ORCHESTRATION_EXAMPLES, SECURITY_CASES
from cases import ALL_CASES


def normalize_problem_text(text: str) -> str:
    """
    Normalize problem text for comparison.

    Strips whitespace, converts to lowercase, and removes extra spaces
    to enable fuzzy matching between old and new cases.
    """
    return ' '.join(text.strip().lower().split())


def find_matching_case(
    problem: str,
    modular_cases: List[Dict[str, Any]]
) -> Dict[str, Any] | None:
    """
    Find a matching case in modular structure by problem text.

    Args:
        problem: Problem text to search for
        modular_cases: List of modular cases to search

    Returns:
        Matching case dict or None if not found
    """
    normalized_problem = normalize_problem_text(problem)

    for case in modular_cases:
        if normalize_problem_text(case['problem']) == normalized_problem:
            return case

    return None


def get_solution_preview(solution: str, max_length: int = 100) -> str:
    """
    Get a preview of the solution text.

    Args:
        solution: Full solution text
        max_length: Maximum length of preview

    Returns:
        Truncated solution text
    """
    solution_clean = ' '.join(solution.strip().split())
    if len(solution_clean) <= max_length:
        return solution_clean
    return solution_clean[:max_length] + '...'


def verify_migration() -> Dict[str, Any]:
    """
    Verify that all cases from case_base.py are present in modular structure.

    Returns:
        Dictionary containing verification results and statistics
    """
    # Collect all original cases with source tracking
    original_cases = []

    for idx, case in enumerate(CASE_BASE):
        original_cases.append({
            'source': 'CASE_BASE',
            'index': idx,
            'case': case
        })

    for idx, case in enumerate(ORCHESTRATION_EXAMPLES):
        original_cases.append({
            'source': 'ORCHESTRATION_EXAMPLES',
            'index': idx,
            'case': case
        })

    for idx, case in enumerate(SECURITY_CASES):
        original_cases.append({
            'source': 'SECURITY_CASES',
            'index': idx,
            'case': case
        })

    # Track matched and missing cases
    matched_cases = []
    missing_cases = []

    # Track which modular cases have been matched (for duplicate detection)
    matched_modular_indices: Set[int] = set()

    # Match each original case
    for original in original_cases:
        case = original['case']
        matching_case = find_matching_case(case['problem'], ALL_CASES)

        if matching_case:
            # Find index of matched case
            modular_idx = None
            for idx, modular_case in enumerate(ALL_CASES):
                if modular_case is matching_case and idx not in matched_modular_indices:
                    modular_idx = idx
                    matched_modular_indices.add(idx)
                    break

            matched_cases.append({
                'source': original['source'],
                'source_index': original['index'],
                'modular_index': modular_idx,
                'problem': case['problem'],
                'has_metadata': all(
                    key in matching_case
                    for key in ['category', 'subcategory', 'tags']
                )
            })
        else:
            missing_cases.append({
                'source': original['source'],
                'index': original['index'],
                'problem': case['problem'],
                'solution_preview': get_solution_preview(case['solution'])
            })

    # Calculate statistics
    total_original = len(original_cases)
    matched_count = len(matched_cases)
    missing_count = len(missing_cases)
    migration_complete = missing_count == 0

    # Check metadata completeness for matched cases
    cases_with_metadata = sum(
        1 for case in matched_cases if case['has_metadata']
    )

    # Generate report
    report = {
        'summary': {
            'total_original_cases': total_original,
            'case_base_cases': len(CASE_BASE),
            'orchestration_examples': len(ORCHESTRATION_EXAMPLES),
            'security_cases': len(SECURITY_CASES),
            'total_modular_cases': len(ALL_CASES),
            'matched_cases': matched_count,
            'missing_cases': missing_count,
            'migration_complete': migration_complete,
            'metadata_complete': cases_with_metadata == matched_count
        },
        'matched_cases': matched_cases,
        'missing_cases': missing_cases,
        'statistics': {
            'match_rate_percentage': round((matched_count / total_original) * 100, 2),
            'cases_with_metadata': cases_with_metadata,
            'metadata_rate_percentage': round(
                (cases_with_metadata / matched_count) * 100, 2
            ) if matched_count > 0 else 0,
            'extra_modular_cases': len(ALL_CASES) - matched_count
        }
    }

    return report


def main():
    """Main execution function."""
    print("=" * 80)
    print("CBR MCP Server - Migration Verification")
    print("=" * 80)
    print()

    print("Loading original cases from case_base.py...")
    print(f"  - CASE_BASE: {len(CASE_BASE)} cases")
    print(f"  - ORCHESTRATION_EXAMPLES: {len(ORCHESTRATION_EXAMPLES)} cases")
    print(f"  - SECURITY_CASES: {len(SECURITY_CASES)} cases")
    print(f"  - Total: {len(CASE_BASE) + len(ORCHESTRATION_EXAMPLES) + len(SECURITY_CASES)} cases")
    print()

    print("Loading modular cases from cases/...")
    print(f"  - ALL_CASES: {len(ALL_CASES)} cases")
    print()

    print("Performing migration verification...")
    report = verify_migration()
    print()

    # Display summary
    summary = report['summary']
    print("VERIFICATION SUMMARY")
    print("-" * 80)
    print(f"Original cases: {summary['total_original_cases']}")
    print(f"Modular cases:  {summary['total_modular_cases']}")
    print(f"Matched:        {summary['matched_cases']}")
    print(f"Missing:        {summary['missing_cases']}")
    print(f"Migration:      {'✓ COMPLETE' if summary['migration_complete'] else '✗ INCOMPLETE'}")
    print(f"Metadata:       {'✓ COMPLETE' if summary['metadata_complete'] else '✗ INCOMPLETE'}")
    print()

    stats = report['statistics']
    print("STATISTICS")
    print("-" * 80)
    print(f"Match rate:     {stats['match_rate_percentage']}%")
    print(f"Metadata rate:  {stats['metadata_rate_percentage']}%")
    print(f"Extra cases:    {stats['extra_modular_cases']}")
    print()

    # Display missing cases if any
    if report['missing_cases']:
        print("MISSING CASES")
        print("-" * 80)
        for missing in report['missing_cases']:
            print(f"\nSource: {missing['source']} [Index: {missing['index']}]")
            print(f"Problem: {missing['problem']}")
            print(f"Solution: {missing['solution_preview']}")
            print()

    # Save report to file
    output_path = project_root / 'scripts' / 'migration_verification_report.json'
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Report saved to: {output_path}")
    print()

    # Exit with appropriate code
    if summary['migration_complete']:
        print("✓ All cases successfully migrated!")
        sys.exit(0)
    else:
        print(f"✗ Migration incomplete: {summary['missing_cases']} cases not found")
        sys.exit(1)


if __name__ == '__main__':
    main()
