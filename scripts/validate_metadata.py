#!/usr/bin/env python3
"""
Metadata Validation Script for CBR MCP Server

This script validates metadata integrity in the ChromaDB collection,
ensuring all cases have proper category, subcategory, and tags fields.

Usage:
    python validate_metadata.py --db-path ./db --collection code_solutions_case_base
"""

import argparse
import logging
import sys
from typing import Dict, List, Tuple, Any
import chromadb

# Valid categories from tech spec
VALID_CATEGORIES = ["code", "orchestration", "best-practice", "anti-pattern"]

# Category-subcategory mapping from tech spec
CATEGORY_SUBCATEGORIES = {
    "code": [
        "firebase-auth",
        "react-components",
        "api-routes",
        "database",
        "testing",
        "general",
    ],
    "orchestration": [
        "remediation",
        "planning",
        "delegation",
        "verification",
        "completion",
    ],
    "best-practice": [
        "planning",
        "verification",
        "error-handling",
    ],
    "anti-pattern": [
        "completion-bias",
        "verification-skip",
        "protocol-violation",
    ],
}


class ValidationResults:
    """Container for validation results."""

    def __init__(self):
        self.total_cases = 0
        self.errors_by_type: Dict[str, List[str]] = {
            "missing_category": [],
            "missing_subcategory": [],
            "missing_tags": [],
            "invalid_category": [],
            "invalid_subcategory": [],
            "invalid_tags_format": [],
        }

    def add_error(self, error_type: str, case_id: str):
        """Add an error for a specific case."""
        if error_type in self.errors_by_type:
            self.errors_by_type[error_type].append(case_id)

    def has_errors(self) -> bool:
        """Check if any validation errors exist."""
        return any(len(errors) > 0 for errors in self.errors_by_type.values())

    def error_count(self) -> int:
        """Get total count of validation errors."""
        return sum(len(errors) for errors in self.errors_by_type.values())


def validate_required_fields(
    case_id: str, metadata: Dict[str, Any], results: ValidationResults
) -> None:
    """Validate that all required metadata fields are present."""
    if "category" not in metadata:
        results.add_error("missing_category", case_id)

    if "subcategory" not in metadata:
        results.add_error("missing_subcategory", case_id)

    if "tags" not in metadata:
        results.add_error("missing_tags", case_id)


def validate_category_values(
    case_id: str, metadata: Dict[str, Any], results: ValidationResults
) -> None:
    """Validate that category values are in VALID_CATEGORIES."""
    category = metadata.get("category")
    if category and category not in VALID_CATEGORIES:
        results.add_error("invalid_category", case_id)


def validate_subcategory_consistency(
    case_id: str, metadata: Dict[str, Any], results: ValidationResults
) -> None:
    """Validate subcategory-category consistency."""
    category = metadata.get("category")
    subcategory = metadata.get("subcategory")

    if category and subcategory:
        if category in CATEGORY_SUBCATEGORIES:
            valid_subcategories = CATEGORY_SUBCATEGORIES[category]
            if subcategory not in valid_subcategories:
                results.add_error("invalid_subcategory", case_id)
        else:
            # Category is invalid, will be caught by validate_category_values
            pass


def validate_tags_format(
    case_id: str, metadata: Dict[str, Any], results: ValidationResults
) -> None:
    """Validate tags format (comma-separated strings, lowercase)."""
    tags = metadata.get("tags")

    if tags is None:
        # Missing tags field caught by validate_required_fields
        return

    # Empty string is valid
    if tags == "":
        return

    # Tags should be a string
    if not isinstance(tags, str):
        results.add_error("invalid_tags_format", case_id)
        return

    # Check if tags are lowercase and comma-separated
    tag_list = [tag.strip() for tag in tags.split(",")]
    for tag in tag_list:
        if tag != tag.lower():
            results.add_error("invalid_tags_format", case_id)
            return

        # Tags should not be empty after stripping
        if not tag:
            results.add_error("invalid_tags_format", case_id)
            return


def validate_collection(collection: Any) -> ValidationResults:
    """Validate all cases in the collection."""
    results = ValidationResults()

    # Get all cases with metadata
    try:
        data = collection.get(include=["metadatas"])
    except Exception as e:
        logging.error(f"Error fetching collection data: {e}", exc_info=True)
        raise

    results.total_cases = len(data["ids"])

    # Validate each case
    for i, case_id in enumerate(data["ids"]):
        metadata = data["metadatas"][i]

        validate_required_fields(case_id, metadata, results)
        validate_category_values(case_id, metadata, results)
        validate_subcategory_consistency(case_id, metadata, results)
        validate_tags_format(case_id, metadata, results)

    return results


def print_validation_results(results: ValidationResults) -> None:
    """Print formatted validation results."""
    print("\nValidation Results:")
    print("=" * 50)
    print(f"Total cases: {results.total_cases}")

    # Count validations passed
    missing_category_count = len(results.errors_by_type["missing_category"])
    missing_subcategory_count = len(results.errors_by_type["missing_subcategory"])
    missing_tags_count = len(results.errors_by_type["missing_tags"])
    invalid_category_count = len(results.errors_by_type["invalid_category"])
    invalid_subcategory_count = len(results.errors_by_type["invalid_subcategory"])
    invalid_tags_count = len(results.errors_by_type["invalid_tags_format"])

    # Print field presence checks
    if missing_category_count == 0:
        print(
            f"✓ All cases have category field: {results.total_cases}/{results.total_cases}"
        )
    else:
        print(
            f"✗ Cases missing category field: {missing_category_count}/{results.total_cases}"
        )

    if missing_subcategory_count == 0:
        print(
            f"✓ All cases have subcategory field: {results.total_cases}/{results.total_cases}"
        )
    else:
        print(
            f"✗ Cases missing subcategory field: {missing_subcategory_count}/{results.total_cases}"
        )

    if missing_tags_count == 0:
        print(
            f"✓ All cases have tags field: {results.total_cases}/{results.total_cases}"
        )
    else:
        print(
            f"✗ Cases missing tags field: {missing_tags_count}/{results.total_cases}"
        )

    # Print value validation checks
    valid_category_count = results.total_cases - invalid_category_count
    if invalid_category_count == 0:
        print(
            f"✓ All category values valid: {valid_category_count}/{results.total_cases}"
        )
    else:
        print(
            f"✗ Invalid category values: {invalid_category_count}/{results.total_cases}"
        )

    valid_subcategory_count = results.total_cases - invalid_subcategory_count
    if invalid_subcategory_count == 0:
        print(
            f"✓ All subcategory-category pairs valid: {valid_subcategory_count}/{results.total_cases}"
        )
    else:
        print(
            f"✗ Invalid subcategory-category pairs: {invalid_subcategory_count}/{results.total_cases}"
        )

    valid_tags_count = results.total_cases - invalid_tags_count
    if invalid_tags_count == 0:
        print(
            f"✓ All tags formats valid: {valid_tags_count}/{results.total_cases}"
        )
    else:
        print(f"✗ Invalid tags formats: {invalid_tags_count}/{results.total_cases}")

    # Print error details if any
    if results.has_errors():
        print("\nValidation Errors:")
        print("-" * 50)

        for error_type, case_ids in results.errors_by_type.items():
            if case_ids:
                print(f"\n{error_type.replace('_', ' ').title()}:")
                for case_id in case_ids[:10]:  # Show first 10
                    print(f"  - {case_id}")
                if len(case_ids) > 10:
                    print(f"  ... and {len(case_ids) - 10} more")

        print(f"\nTotal validation errors: {results.error_count()}")
    else:
        print("\nAll validations passed! ✓")


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate metadata integrity in CBR collection"
    )
    parser.add_argument(
        "--db-path",
        default="./db",
        help="Path to ChromaDB database directory (default: ./db)",
    )
    parser.add_argument(
        "--collection",
        default="code_solutions_case_base",
        help="Name of ChromaDB collection (default: code_solutions_case_base)",
    )

    args = parser.parse_args()

    print(f"Validating metadata for collection: {args.collection}")
    print(f"Database path: {args.db_path}")

    # Connect to ChromaDB
    try:
        client = chromadb.PersistentClient(path=args.db_path)
        collection = client.get_collection(args.collection)
    except Exception as e:
        logging.error(f"Error connecting to ChromaDB: {e}", exc_info=True)
        print(f"\n❌ Error connecting to ChromaDB: {e}")
        return 1

    # Check collection is not empty
    try:
        total_cases = collection.count()
        if total_cases == 0:
            print("\nCollection is empty. Nothing to validate.")
            return 0
    except Exception as e:
        logging.error(f"Error counting collection: {e}", exc_info=True)
        print(f"\n❌ Error counting collection: {e}")
        return 1

    # Run validation
    try:
        results = validate_collection(collection)
    except Exception as e:
        logging.error(f"Error during validation: {e}", exc_info=True)
        print(f"\n❌ Error during validation: {e}")
        return 1

    # Print results
    print_validation_results(results)

    # Return exit code
    if results.has_errors():
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
