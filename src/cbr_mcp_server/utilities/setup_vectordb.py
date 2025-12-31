# setup_vectordb.py
"""
ChromaDB Vector Database Setup Script for CBR MCP Server.

This script populates the ChromaDB vector database with case-based reasoning examples,
including complete metadata (category, subcategory, tags) for category-based filtering.

Metadata Schema
---------------
Each case is stored in ChromaDB with the following metadata structure:
- problem: str - Problem description (used for semantic search embeddings)
- category: str - Top-level category (e.g., "orchestration", "firebase", "rust")
- subcategory: str - Specific subcategory (e.g., "planning", "auth", "components")
- tags: str - Comma-separated tags (converted from list in case files)

The metadata enables powerful category-based filtering via the cbr_search_category() MCP tool
while maintaining backward compatibility with existing semantic search patterns.

Usage Examples
--------------
# Load all cases with complete metadata
python setup_vectordb.py

# Force rebuild (required after metadata schema changes)
python setup_vectordb.py --force

# Load specific categories only
python setup_vectordb.py --category orchestration firebase

# List available categories before filtering
python setup_vectordb.py --list-categories

Database Migration
------------------
If upgrading from a database created before November 2025 (which only stored problem field),
you MUST use --force to rebuild with complete metadata:

    python setup_vectordb.py --force

This will:
1. Delete the old collection (missing category/subcategory/tags in metadata)
2. Reload all cases from source files (with complete metadata)
3. Regenerate embeddings
4. Store cases with full metadata structure

See Documentation/Metadata-Schema-Guide.md for complete details on the metadata system.
"""
import argparse
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Add project root to Python path for imports
script_dir = Path(__file__).resolve().parent
project_root = (
    script_dir.parent.parent.parent
)  # Go up three levels from src/cbr_mcp_server/utilities/
sys.path.insert(0, str(project_root))

import chromadb
from sentence_transformers import SentenceTransformer

from cases import load_all_cases
from cbr_mcp_server.metadata_extraction import extract_metadata_list


def generate_case_id(case: Dict[str, Any]) -> str:
    """
    Generate a stable, content-based ID for a case using SHA-256 hashing.

    Creates a deterministic ID based on the concatenation of problem, solution, category,
    and subcategory, ensuring that cases with different categorizations get unique IDs
    even if they share the same problem/solution content. This prevents duplicate ID
    errors when the same code example appears in multiple categories.

    Args:
        case: Dictionary containing at least 'problem' and 'solution' keys.
              Optional: 'category', 'subcategory' keys for unique categorization.
              Note: 'tags' field does not affect ID generation.

    Returns:
        String in format 'case_<first_16_chars_of_sha256_hash>'
        Example: "case_a7f3b2c1d4e5f6g7"

    Algorithm:
        1. Concatenate case["problem"] + case["solution"] + case["category"] + case["subcategory"]
        2. Encode concatenated string as UTF-8
        3. Compute SHA-256 hash
        4. Extract first 16 characters of hexadecimal digest
        5. Return formatted as "case_<hash_prefix>"

    Notes:
        - Missing keys are treated as empty strings
        - Tags field does not affect ID (allows same categorization with different tags)
        - Hash is deterministic: same content always produces same ID
        - Hash is collision-resistant: different content produces different IDs
        - Including category/subcategory allows same code to appear in multiple categories
    """
    import hashlib

    # Extract all relevant fields, defaulting to empty string if missing
    problem = case.get("problem", "")
    solution = case.get("solution", "")
    category = case.get("category", "")
    subcategory = case.get("subcategory", "")

    # Create canonical string representation
    # Include category and subcategory to ensure unique IDs for different categorizations
    # Convert None to empty string to handle both missing keys and None values
    content = (
        (problem or "") + (solution or "") + (category or "") + (subcategory or "")
    )

    # Generate SHA-256 hash
    hash_object = hashlib.sha256(content.encode("utf-8"))
    hash_hex = hash_object.hexdigest()

    # Take first 16 characters of hash
    hash_prefix = hash_hex[:16]

    # Return formatted ID
    case_id = f"case_{hash_prefix}"

    # Log ID generation with truncated problem text
    # Convert None to empty string before checking length to avoid TypeError
    problem_str = problem or ""
    problem_preview = (
        (problem_str[:50] + "...") if len(problem_str) > 50 else problem_str
    )
    logger.debug(f"Generated ID {case_id} for problem: {problem_preview}")

    return case_id


def identify_new_cases(
    all_cases: List[Dict[str, Any]], collection: Optional[Any]
) -> Tuple[List[Dict[str, Any]], int]:
    """Identify which cases are new vs. already existing in ChromaDB collection.

    This function determines which cases need to be added to the database by:
    1. Generating content-based IDs for all input cases
    2. Querying the collection for existing case IDs
    3. Comparing sets to identify new cases
    4. Returning only new cases and count of duplicates skipped

    Args:
        all_cases: List of case dictionaries to check against database
        collection: ChromaDB collection object to query for existing IDs

    Returns:
        Tuple containing:
        - List of new cases (not in database)
        - Count of skipped cases (already in database)

    Raises:
        KeyError: If case is missing 'problem' or 'solution' field
    """
    # Handle edge case: empty input
    if not all_cases:
        logger.warning("identify_new_cases called with empty case list")
        return [], 0

    # Handle edge case: None collection (defensive)
    if collection is None:
        logger.warning(
            "identify_new_cases called with None collection, treating all cases as new"
        )
        return all_cases, 0

    # Query database for existing IDs (defensive error handling)
    try:
        result = collection.get()
        existing_ids = result.get("ids", []) if result else []

        # Handle None ids
        if existing_ids is None:
            logger.warning("Database returned None for ids, treating as empty")
            existing_ids = []

    except Exception as e:
        # On any database error, treat all cases as new (defensive behavior)
        logger.error(
            f"Error querying database for existing IDs: {e}, treating all cases as new"
        )
        return all_cases, 0

    # Convert to set for O(1) lookup performance
    existing_ids_set = set(existing_ids)

    # Identify new cases (preserve original order)
    # Generate ID for each case and check if it exists
    new_cases = []
    for case in all_cases:
        case_id = generate_case_id(case)  # May raise KeyError for missing fields
        if case_id not in existing_ids_set:
            new_cases.append(case)

    # Calculate skipped count
    skipped_count = len(all_cases) - len(new_cases)

    # Log deduplication decision
    logger.info(
        f"Deduplication: {len(new_cases)} new cases found, {skipped_count} duplicates skipped"
    )

    return new_cases, skipped_count


def parse_arguments(args=None) -> argparse.Namespace:
    """Parse command-line arguments for selective case loading.

    Args:
        args: Optional list of arguments to parse (defaults to sys.argv if None)
    """
    parser = argparse.ArgumentParser(
        description="Setup vector database with selective case loading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load all cases (default)
  python setup_vectordb.py

  # Load only firebase and rust cases
  python setup_vectordb.py --category firebase rust

  # Load specific subcategories
  python setup_vectordb.py --category orchestration --subcategory remediation verification

  # Load cases with specific tags
  python setup_vectordb.py --tags authentication security

  # Load specific module files
  python setup_vectordb.py --modules cases/firebase/firebase_auth_cases.py

  # Combine filters (AND logic)
  python setup_vectordb.py --category firebase --tags authentication

  # Force rebuild even if database exists
  python setup_vectordb.py --force

  # Validate database integrity (read-only)
  python setup_vectordb.py --validate

  # List available categories
  python setup_vectordb.py --list-categories

  # List subcategories for a category
  python setup_vectordb.py --list-subcategories orchestration
        """,
    )

    # Filtering options
    parser.add_argument(
        "--category",
        nargs="+",
        help="Filter by one or more categories (e.g., firebase rust nextjs)",
    )
    parser.add_argument(
        "--subcategory",
        nargs="+",
        help="Filter by one or more subcategories (e.g., auth components)",
    )
    parser.add_argument(
        "--tags", nargs="+", help="Filter cases that have any of these tags"
    )
    parser.add_argument(
        "--modules",
        nargs="+",
        help="Load specific module file paths directly (e.g., cases/firebase/firebase_auth_cases.py)",
    )

    # List operations (mutually exclusive with loading)
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="Show available categories with case counts and exit",
    )
    parser.add_argument(
        "--list-subcategories",
        metavar="CATEGORY",
        help="Show subcategories for a specific category and exit",
    )

    # Mutually exclusive group for --validate and --force
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--force", action="store_true", help="Force rebuild even if database exists"
    )
    mode_group.add_argument(
        "--validate",
        action="store_true",
        help="Validate database integrity without modification (exit 0 if valid, 1 if discrepancies)",
    )

    return parser.parse_args(args)


def list_categories(all_cases: List[Dict[str, Any]]) -> None:
    """Display all categories with case counts."""
    category_counts: Dict[str, int] = defaultdict(int)

    for case in all_cases:
        category = case.get("category", "unknown")
        category_counts[category] += 1

    print("\nAvailable Categories:")
    print("=" * 50)

    # Sort by category name
    for category in sorted(category_counts.keys()):
        count = category_counts[category]
        print(f"  {category:<20} ({count} cases)")

    print("=" * 50)
    print(f"Total: {len(all_cases)} cases across {len(category_counts)} categories\n")


def list_subcategories(all_cases: List[Dict[str, Any]], category: str) -> None:
    """Display subcategories for a specific category with counts."""
    # Verify category exists
    category_cases = [c for c in all_cases if c.get("category") == category]

    if not category_cases:
        print(f"\nError: Category '{category}' not found.")
        print("\nAvailable categories:")
        for cat in sorted(set(c.get("category", "unknown") for c in all_cases)):
            print(f"  - {cat}")
        print()
        return

    subcategory_counts: Dict[str, int] = defaultdict(int)

    for case in category_cases:
        subcategory = case.get("subcategory", "unknown")
        subcategory_counts[subcategory] += 1

    print(f"\nSubcategories for '{category}':")
    print("=" * 50)

    # Sort by subcategory name
    for subcategory in sorted(subcategory_counts.keys()):
        count = subcategory_counts[subcategory]
        print(f"  {subcategory:<20} ({count} cases)")

    print("=" * 50)
    print(
        f"Total: {len(category_cases)} cases across {len(subcategory_counts)} subcategories\n"
    )


def filter_cases(
    all_cases: List[Dict[str, Any]], args: argparse.Namespace
) -> List[Dict[str, Any]]:
    """Filter cases based on command-line arguments.

    Args:
        all_cases: List of all case dictionaries
        args: Parsed command-line arguments

    Returns:
        Filtered list of cases based on provided criteria.
        Uses AND logic when multiple filters are specified.
    """
    # If no filters specified, return all cases
    has_filters = any([args.category, args.subcategory, args.tags, args.modules])

    if not has_filters:
        return all_cases

    filtered = all_cases

    # Filter by category
    if args.category:
        filtered = [case for case in filtered if case.get("category") in args.category]

    # Filter by subcategory
    if args.subcategory:
        filtered = [
            case for case in filtered if case.get("subcategory") in args.subcategory
        ]

    # Filter by tags (any tag match)
    if args.tags:
        filtered = [
            case
            for case in filtered
            if any(tag in case.get("tags", []) for tag in args.tags)
        ]

    # Filter by modules (match module file path)
    if args.modules:
        # This is a placeholder for module-based filtering
        # In practice, we'd need to track which module each case came from
        # For now, we'll skip this filter as it requires additional metadata
        print(
            "Warning: --modules filtering not yet implemented (requires case source tracking)"
        )

    return filtered


def validate_database(
    all_cases: List[Dict[str, Any]], collection: Any
) -> Dict[str, Any]:
    """
    Validate database integrity by comparing case files against ChromaDB contents.

    This function compares the cases loaded from files with the cases stored in the
    ChromaDB database to detect discrepancies. It identifies cases that are missing
    from the database (in files but not in DB) and orphaned cases (in DB but not in files).

    Algorithm:
        1. Generate content-based IDs for all file cases using generate_case_id()
        2. Retrieve all IDs from the database collection
        3. Compare the two sets to find missing and orphaned cases
        4. Return comprehensive validation report

    Args:
        all_cases: List of case dictionaries loaded from case files
        collection: ChromaDB collection object

    Returns:
        Dictionary with validation report structure:
        {
            "cases_in_files": int,         # Total cases in files
            "cases_in_db": int,            # Total cases in database
            "matches": int,                # Number of matching cases
            "missing_from_db": List[str],  # Case IDs in files but not in DB
            "extra_in_db": List[str],      # Case IDs in DB but not in files
            "has_discrepancies": bool      # True if any discrepancies exist
        }

    Raises:
        Exception: Propagates any ChromaDB exceptions (connection errors, etc.)
    """
    # Generate IDs for all file cases
    file_case_ids = set(generate_case_id(case) for case in all_cases)

    # Retrieve all IDs from database (no limit to get all)
    db_result = collection.get()
    db_case_ids = set(db_result["ids"])

    # Calculate set differences
    matching_ids = file_case_ids & db_case_ids  # Intersection
    missing_from_db = file_case_ids - db_case_ids  # In files but not in DB
    extra_in_db = db_case_ids - file_case_ids  # In DB but not in files

    # Build validation report
    report = {
        "cases_in_files": len(file_case_ids),
        "cases_in_db": len(db_case_ids),
        "matches": len(matching_ids),
        "missing_from_db": sorted(list(missing_from_db)),
        "extra_in_db": sorted(list(extra_in_db)),
        "has_discrepancies": len(missing_from_db) > 0 or len(extra_in_db) > 0,
    }

    # Log validation results
    logger.info(
        f"Validation results: {len(matching_ids)} matches, {len(missing_from_db)} missing from DB, {len(extra_in_db)} extra in DB"
    )
    if report["has_discrepancies"]:
        logger.warning(
            f"Database validation found discrepancies: {len(missing_from_db)} missing, {len(extra_in_db)} extra"
        )

    return report


def main(argv=None) -> None:
    """
    Main execution function for vector database setup.

    Args:
        argv: Optional list of command-line arguments (defaults to sys.argv if None)

    This function orchestrates the complete database population process:
    1. Load cases from modular case files (with complete metadata validation)
    2. Apply optional filtering by category, subcategory, or tags
    3. Initialize embedding model and ChromaDB client
    4. Extract complete metadata (problem, category, subcategory, tags)
    5. Generate embeddings for problem text
    6. Store cases with complete metadata in ChromaDB

    The metadata storage enables category-based filtering in the MCP server while
    maintaining backward compatibility with existing semantic search patterns.

    Metadata Validation
    -------------------
    Before storing in ChromaDB, the function validates that all metadata contains
    the required fields (problem, category, subcategory, tags). If any cases are
    missing metadata, warnings are printed but the process continues.

    Database Migration
    ------------------
    Use --force flag to rebuild databases that don't have complete metadata:
        python setup_vectordb.py --force

    This is required when upgrading from databases created before November 2025.
    """
    try:
        # Parse command-line arguments
        args = parse_arguments(argv)

        # Load all cases first (needed for list operations)
        all_cases = load_all_cases()

        # Handle list operations (exit after displaying)
        if args.list_categories:
            list_categories(all_cases)
            sys.exit(0)

        if args.list_subcategories:
            list_subcategories(all_cases, args.list_subcategories)
            sys.exit(0)

        # Handle validation mode (read-only database check)
        if args.validate:
            print("\n=== Database Validation Mode ===\n")
            print("Connecting to ChromaDB...")
            client = chromadb.PersistentClient(path="./db")

            try:
                collection = client.get_collection(name="code_solutions_case_base")
            except Exception as e:
                print(f"\nError: Unable to access database collection: {e}")
                print("Database may not exist. Run without --validate to create it.")
                sys.exit(1)

            print("Running validation...\n")
            report = validate_database(all_cases, collection)

            # Display validation report
            print("=== Database Validation Report ===")
            print(f"Cases in files:      {report['cases_in_files']}")
            print(f"Cases in database:   {report['cases_in_db']}")
            print(f"Matching cases:      {report['matches']}")
            print(f"Missing from DB:     {len(report['missing_from_db'])}")
            print(f"Extra in DB:         {len(report['extra_in_db'])}")

            if report["has_discrepancies"]:
                print("\n⚠️  DISCREPANCIES FOUND")

                if report["missing_from_db"]:
                    print(
                        f"\nMissing from database ({len(report['missing_from_db'])} cases):"
                    )
                    for case_id in report["missing_from_db"][:10]:  # Show first 10
                        print(f"  - {case_id}")
                    if len(report["missing_from_db"]) > 10:
                        print(f"  ... and {len(report['missing_from_db']) - 10} more")

                if report["extra_in_db"]:
                    print(f"\nExtra in database ({len(report['extra_in_db'])} cases):")
                    for case_id in report["extra_in_db"][:10]:  # Show first 10
                        print(f"  - {case_id}")
                    if len(report["extra_in_db"]) > 10:
                        print(f"  ... and {len(report['extra_in_db']) - 10} more")

                print(
                    "\nRecommendation: Run with --force to rebuild database from case files."
                )
                sys.exit(1)
            else:
                print("\n✅ Database is valid - no discrepancies found")
                sys.exit(0)

        # Filter cases based on arguments
        CASE_BASE = filter_cases(all_cases, args)

        # Print feedback about what's being loaded
        if len(CASE_BASE) < len(all_cases):
            print(f"Filtered to {len(CASE_BASE)} cases (out of {len(all_cases)} total)")

            # Show breakdown of filtered cases
            if args.category:
                print(f"  Categories: {', '.join(args.category)}")
            if args.subcategory:
                print(f"  Subcategories: {', '.join(args.subcategory)}")
            if args.tags:
                print(f"  Tags: {', '.join(args.tags)}")
        else:
            print(f"Loading all {len(CASE_BASE)} cases from modular structure")

        # Check for empty result
        if not CASE_BASE:
            print("\nWarning: No cases match the specified filters.")
            print("Use --list-categories to see available categories.")
            sys.exit(1)

        # 1. Initialize the Embedding Model (runs locally)
        print("\nInitializing embedding model...")
        embedding_model = SentenceTransformer(
            "nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True
        )

        # 2. Initialize ChromaDB Client
        print("Connecting to ChromaDB...")
        client = chromadb.PersistentClient(path="./db")

        # 3. Create or load a collection
        collection = client.get_or_create_collection(name="code_solutions_case_base")

        # 5. Populate the database
        # Check if the collection is already populated to avoid duplicates
        current_count = collection.count()
        force_rebuild = args.force

        if current_count == 0 or force_rebuild:
            if force_rebuild and current_count > 0:
                print(
                    f"\nForce rebuild requested. Clearing existing {current_count} cases..."
                )
                client.delete_collection(name="code_solutions_case_base")
                collection = client.create_collection(name="code_solutions_case_base")

            print("Populating the vector database...")
            # Separate problems and solutions from the case base
            problems = [case["problem"] for case in CASE_BASE]
            solutions = [case["solution"] for case in CASE_BASE]

            # Generate content-based IDs for deduplication
            ids = [generate_case_id(case) for case in CASE_BASE]

            # Generate embeddings for all the 'problem' descriptions
            print(f"Generating embeddings for {len(problems)} cases...")
            problem_embeddings = embedding_model.encode(
                problems, normalize_embeddings=True
            )

            # Prepare metadata
            metadatas = extract_metadata_list(CASE_BASE)

            # Validate metadata before storage
            assert len(metadatas) == len(
                CASE_BASE
            ), f"Metadata count mismatch: {len(metadatas)} != {len(CASE_BASE)}"

            # Print sample metadata for verification
            print(f"Sample metadata (first case): {metadatas[0]}")

            # Verify all metadata dicts have required fields
            required_fields = {"problem", "category", "subcategory", "tags"}
            for i, metadata in enumerate(metadatas):
                missing_fields = required_fields - set(metadata.keys())
                if missing_fields:
                    print(f"Warning: Case {i} missing fields: {missing_fields}")

            # Add the data to the collection
            print("Adding cases to database...")
            collection.add(
                embeddings=problem_embeddings,
                documents=solutions,  # Store the code solutions as the main document
                metadatas=metadatas,  # Store complete metadata including problem, category, subcategory, tags
                ids=ids,  # Provide the unique IDs
            )
            print(f"Successfully added {len(ids)} cases to the database.")
        else:
            # Incremental update mode: add only new cases
            print(
                f"Database has {current_count} existing cases. Checking for new cases..."
            )

            # Identify new cases vs existing
            new_cases, skipped_count = identify_new_cases(CASE_BASE, collection)

            if len(new_cases) > 0:
                print(f"Found {len(new_cases)} new cases to add...")

                # Separate problems and solutions from new cases only
                problems = [case["problem"] for case in new_cases]
                solutions = [case["solution"] for case in new_cases]

                # Generate content-based IDs for new cases
                ids = [generate_case_id(case) for case in new_cases]

                # Generate embeddings for new cases only
                print(f"Generating embeddings for {len(problems)} new cases...")
                problem_embeddings = embedding_model.encode(
                    problems, normalize_embeddings=True
                )

                # Prepare metadata for new cases
                metadatas = extract_metadata_list(new_cases)

                # Validate metadata before storage
                assert len(metadatas) == len(
                    new_cases
                ), f"Metadata count mismatch: {len(metadatas)} != {len(new_cases)}"

                # Add only new cases to the collection
                print("Adding new cases to database...")
                collection.add(
                    embeddings=problem_embeddings,
                    documents=solutions,
                    metadatas=metadatas,
                    ids=ids,
                )

                # Display statistics
                final_count = collection.count()
                print(f"\nIncremental update complete:")
                print(f"  Added: {len(new_cases)} new cases")
                print(f"  Skipped: {skipped_count} existing cases")
                print(f"  Total: {final_count} cases in database")
            else:
                # No new cases to add
                print(f"All {len(CASE_BASE)} cases already exist in database.")
                print(f"  Skipped: {skipped_count} existing cases")
                print(f"  Total: {current_count} cases in database")
                print("\nUse --force to rebuild the database.")

    except Exception as e:
        # Comprehensive error handling for ChromaDB, embedding, and general failures
        error_msg = str(e).lower()

        # Determine error type and provide appropriate user message
        if "chromadb" in error_msg or "database" in error_msg or "chroma" in error_msg:
            # ChromaDB-specific error
            logger.error(f"ChromaDB connection or operation failed: {e}")
            print("\nError: Failed to connect to or operate ChromaDB database.")
            print(f"Details: {e}")
            print("\nPlease check:")
            print("  - Database directory permissions")
            print("  - Available disk space")
            print("  - ChromaDB installation")
        elif (
            "embedding" in error_msg
            or "model" in error_msg
            or "encode" in error_msg
            or "torch" in error_msg
        ):
            # Embedding model error
            logger.error(f"Embedding model generation failed: {e}")
            print("\nError: Failed to generate embeddings using the model.")
            print(f"Details: {e}")
            print("\nPlease check:")
            print("  - SentenceTransformer installation")
            print("  - Available memory")
            print("  - Model download/cache directory permissions")
        else:
            # General unexpected error
            logger.error(f"Unexpected error during database setup: {e}")
            print("\nError: An unexpected error occurred during database setup.")
            print(f"Details: {e}")

        # Exit with non-zero code
        sys.exit(1)


if __name__ == "__main__":
    main()
