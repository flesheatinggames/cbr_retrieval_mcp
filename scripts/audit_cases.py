#!/usr/bin/env python3
"""
Case Base Audit Script

This script extracts all cases from case_base.py and generates a comprehensive
audit report in JSON format.

Output: scripts/case_audit.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def extract_cases_from_module() -> List[Dict[str, Any]]:
    """
    Extract all cases from case_base.py by directly importing the module.

    Returns:
        List of case dictionaries with problem, solution, and metadata
    """
    # Add parent directory to path to import case_base
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    sys.path.insert(0, str(project_root))

    try:
        from case_base import CASE_BASE
    except ImportError as e:
        raise ImportError(f"Failed to import case_base module: {e}")

    if not isinstance(CASE_BASE, list):
        raise ValueError("CASE_BASE is not a list")

    return CASE_BASE


def generate_audit_report(cases: List[Dict[str, Any]], output_path: Path) -> Dict[str, Any]:
    """
    Generate audit report and save to JSON file.

    Args:
        cases: List of extracted cases
        output_path: Path to output JSON file

    Returns:
        Audit report dictionary
    """
    audit_data = {
        "total_cases": len(cases),
        "cases": []
    }

    for index, case in enumerate(cases):
        case_entry = {
            "index": index,
            "problem": case.get("problem", ""),
            "solution": case.get("solution", ""),
            "existing_metadata": {}
        }

        # Extract any existing metadata fields (non-problem, non-solution fields)
        for key, value in case.items():
            if key not in ["problem", "solution"]:
                case_entry["existing_metadata"][key] = value

        audit_data["cases"].append(case_entry)

    # Save to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(audit_data, f, indent=2, ensure_ascii=False)

    return audit_data


def print_summary(audit_data: Dict[str, Any]) -> None:
    """Print a summary of the audit results."""
    print(f"\n{'=' * 60}")
    print("CASE BASE AUDIT SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total cases extracted: {audit_data['total_cases']}")

    # Count cases with existing metadata
    cases_with_metadata = sum(
        1 for case in audit_data['cases']
        if case['existing_metadata']
    )
    print(f"Cases with existing metadata: {cases_with_metadata}")

    # Find metadata fields
    metadata_fields = set()
    for case in audit_data['cases']:
        metadata_fields.update(case['existing_metadata'].keys())

    if metadata_fields:
        print(f"Existing metadata fields: {', '.join(sorted(metadata_fields))}")

    # Sample case info
    if audit_data['cases']:
        sample_case = audit_data['cases'][0]
        print(f"\nSample case (index 0):")
        print(f"  Problem: {sample_case['problem'][:80]}...")
        print(f"  Problem length: {len(sample_case['problem'])} characters")
        print(f"  Solution length: {len(sample_case['solution'])} characters")
        print(f"  Metadata fields: {len(sample_case['existing_metadata'])}")
        if sample_case['existing_metadata']:
            print(f"  Metadata keys: {', '.join(sample_case['existing_metadata'].keys())}")

    # Statistics
    total_problem_chars = sum(len(case['problem']) for case in audit_data['cases'])
    total_solution_chars = sum(len(case['solution']) for case in audit_data['cases'])
    print(f"\nStatistics:")
    print(f"  Average problem length: {total_problem_chars // len(audit_data['cases'])} characters")
    print(f"  Average solution length: {total_solution_chars // len(audit_data['cases'])} characters")
    print(f"  Total content size: {(total_problem_chars + total_solution_chars) / 1024:.1f} KB")

    print(f"\n{'=' * 60}")


def main():
    """Main execution function."""
    # Determine paths
    script_dir = Path(__file__).parent
    output_path = script_dir / "case_audit.json"

    try:
        print(f"Extracting cases from case_base module...")
        cases = extract_cases_from_module()

        print(f"Generating audit report...")
        audit_data = generate_audit_report(cases, output_path)

        print(f"\nAudit report saved to: {output_path}")
        print_summary(audit_data)

        print(f"\nSUCCESS: Audit complete!")

    except Exception as e:
        print(f"ERROR: Failed to generate audit report: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
