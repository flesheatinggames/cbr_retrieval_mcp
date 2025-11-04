# setup_vectordb.py
import argparse
import sys
from collections import defaultdict
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from cases import load_all_cases


def parse_arguments():
    """Parse command-line arguments for selective case loading."""
    parser = argparse.ArgumentParser(
        description='Setup vector database with selective case loading',
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

  # List available categories
  python setup_vectordb.py --list-categories

  # List subcategories for a category
  python setup_vectordb.py --list-subcategories orchestration
        """
    )

    # Filtering options
    parser.add_argument(
        '--category',
        nargs='+',
        help='Filter by one or more categories (e.g., firebase rust nextjs)'
    )
    parser.add_argument(
        '--subcategory',
        nargs='+',
        help='Filter by one or more subcategories (e.g., auth components)'
    )
    parser.add_argument(
        '--tags',
        nargs='+',
        help='Filter cases that have any of these tags'
    )
    parser.add_argument(
        '--modules',
        nargs='+',
        help='Load specific module file paths directly (e.g., cases/firebase/firebase_auth_cases.py)'
    )

    # List operations (mutually exclusive with loading)
    parser.add_argument(
        '--list-categories',
        action='store_true',
        help='Show available categories with case counts and exit'
    )
    parser.add_argument(
        '--list-subcategories',
        metavar='CATEGORY',
        help='Show subcategories for a specific category and exit'
    )

    # Force rebuild option
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force rebuild even if database exists'
    )

    return parser.parse_args()


def list_categories(all_cases):
    """Display all categories with case counts."""
    category_counts = defaultdict(int)

    for case in all_cases:
        category = case.get('category', 'unknown')
        category_counts[category] += 1

    print("\nAvailable Categories:")
    print("=" * 50)

    # Sort by category name
    for category in sorted(category_counts.keys()):
        count = category_counts[category]
        print(f"  {category:<20} ({count} cases)")

    print("=" * 50)
    print(f"Total: {len(all_cases)} cases across {len(category_counts)} categories\n")


def list_subcategories(all_cases, category):
    """Display subcategories for a specific category with counts."""
    # Verify category exists
    category_cases = [c for c in all_cases if c.get('category') == category]

    if not category_cases:
        print(f"\nError: Category '{category}' not found.")
        print("\nAvailable categories:")
        for cat in sorted(set(c.get('category', 'unknown') for c in all_cases)):
            print(f"  - {cat}")
        print()
        return

    subcategory_counts = defaultdict(int)

    for case in category_cases:
        subcategory = case.get('subcategory', 'unknown')
        subcategory_counts[subcategory] += 1

    print(f"\nSubcategories for '{category}':")
    print("=" * 50)

    # Sort by subcategory name
    for subcategory in sorted(subcategory_counts.keys()):
        count = subcategory_counts[subcategory]
        print(f"  {subcategory:<20} ({count} cases)")

    print("=" * 50)
    print(f"Total: {len(category_cases)} cases across {len(subcategory_counts)} subcategories\n")


def filter_cases(all_cases, args):
    """Filter cases based on command-line arguments.

    Args:
        all_cases: List of all case dictionaries
        args: Parsed command-line arguments

    Returns:
        Filtered list of cases based on provided criteria.
        Uses AND logic when multiple filters are specified.
    """
    # If no filters specified, return all cases
    has_filters = any([
        args.category,
        args.subcategory,
        args.tags,
        args.modules
    ])

    if not has_filters:
        return all_cases

    filtered = all_cases

    # Filter by category
    if args.category:
        filtered = [
            case for case in filtered
            if case.get('category') in args.category
        ]

    # Filter by subcategory
    if args.subcategory:
        filtered = [
            case for case in filtered
            if case.get('subcategory') in args.subcategory
        ]

    # Filter by tags (any tag match)
    if args.tags:
        filtered = [
            case for case in filtered
            if any(tag in case.get('tags', []) for tag in args.tags)
        ]

    # Filter by modules (match module file path)
    if args.modules:
        # This is a placeholder for module-based filtering
        # In practice, we'd need to track which module each case came from
        # For now, we'll skip this filter as it requires additional metadata
        print("Warning: --modules filtering not yet implemented (requires case source tracking)")

    return filtered


def main():
    """Main execution function."""
    # Parse command-line arguments
    args = parse_arguments()

    # Load all cases first (needed for list operations)
    all_cases = load_all_cases()

    # Handle list operations (exit after displaying)
    if args.list_categories:
        list_categories(all_cases)
        sys.exit(0)

    if args.list_subcategories:
        list_subcategories(all_cases, args.list_subcategories)
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
    embedding_model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)

    # 2. Initialize ChromaDB Client
    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path="./db")

    # 3. Create or load a collection
    collection = client.get_or_create_collection(
        name="code_solutions_case_base"
    )

    # 5. Populate the database
    # Check if the collection is already populated to avoid duplicates
    current_count = collection.count()
    force_rebuild = args.force

    if current_count == 0 or force_rebuild:
        if force_rebuild and current_count > 0:
            print(f"\nForce rebuild requested. Clearing existing {current_count} cases...")
            client.delete_collection(name="code_solutions_case_base")
            collection = client.create_collection(name="code_solutions_case_base")

        print("Populating the vector database...")
        # Separate problems and solutions from the case base
        problems = [case["problem"] for case in CASE_BASE]
        solutions = [case["solution"] for case in CASE_BASE]

        # [FIX] Generate unique string IDs for each entry, as required by ChromaDB
        ids = [f"id{i}" for i in range(len(problems))]

        # Generate embeddings for all the 'problem' descriptions
        print(f"Generating embeddings for {len(problems)} cases...")
        problem_embeddings = embedding_model.encode(problems, normalize_embeddings=True)

        # Add the data to the collection
        print("Adding cases to database...")
        collection.add(
            embeddings=problem_embeddings,
            documents=solutions,  # Store the code solutions as the main document
            metadatas=[{"problem": p} for p in problems], # Store the problem descriptions in metadata
            ids=ids # Provide the unique IDs
        )
        print(f"Successfully added {len(ids)} cases to the database.")
    elif current_count < len(CASE_BASE):
        print(f"WARNING: Database has {current_count} cases but filtered selection has {len(CASE_BASE)} cases.")
        print("Repopulating database with filtered cases...")

        # Clear existing collection and repopulate
        client.delete_collection(name="code_solutions_case_base")
        collection = client.create_collection(name="code_solutions_case_base")

        # Separate problems and solutions from the case base
        problems = [case["problem"] for case in CASE_BASE]
        solutions = [case["solution"] for case in CASE_BASE]

        # Generate unique string IDs for each entry
        ids = [f"id{i}" for i in range(len(problems))]

        # Generate embeddings for all the 'problem' descriptions
        print(f"Generating embeddings for {len(problems)} cases...")
        problem_embeddings = embedding_model.encode(problems, normalize_embeddings=True)

        # Add the data to the collection
        print("Adding cases to database...")
        collection.add(
            embeddings=problem_embeddings,
            documents=solutions,
            metadatas=[{"problem": p} for p in problems],
            ids=ids
        )
        print(f"Successfully added {len(ids)} cases to the database.")
    else:
        print(f"Vector database already populated with {current_count} cases.")
        print("Use --force to rebuild the database.")


if __name__ == "__main__":
    main()