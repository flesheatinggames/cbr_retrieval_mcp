#!/usr/bin/env python3
"""
Metadata Migration Script for CBR MCP Server

This script migrates existing cases in the ChromaDB collection to the new
metadata structure with category, subcategory, and tags fields.

Usage:
    python migrate_metadata.py
"""

import logging
import sys
import chromadb
from metadata_migration import MetadataMigration


def main():
    """Main migration function."""
    print("Starting CBR metadata migration...")

    try:
        # Connect to ChromaDB
        client = chromadb.PersistentClient(path="./db")
        collection = client.get_collection("code_solutions_case_base")
    except Exception as e:
        logging.error(f"Error connecting to ChromaDB: {e}", exc_info=True)
        print(f"❌ Error connecting to ChromaDB: {e}")
        return 1

    # Show initial stats
    total_cases = collection.count()
    print(f"Found {total_cases} total cases in collection")

    if total_cases == 0:
        print("No cases to migrate.")
        return 0

    # Run migration
    print("\nMigrating cases...")
    migrator = MetadataMigration()
    migrated_count = migrator.migrate_collection(collection)

    print(f"\nMigration complete:")
    print(f"  - Migrated: {migrated_count} cases")
    print(f"  - Unchanged: {total_cases - migrated_count} cases")

    # Validation check
    print("\nValidating migration...")
    results = collection.get(include=["metadatas"])

    missing_metadata = []
    for i, doc_id in enumerate(results["ids"]):
        metadata = results["metadatas"][i]
        if "category" not in metadata or "subcategory" not in metadata:
            missing_metadata.append(doc_id)

    if missing_metadata:
        print(f"⚠️  Warning: {len(missing_metadata)} cases missing metadata")
        for doc_id in missing_metadata[:5]:  # Show first 5
            print(f"  - {doc_id}")
        return 1
    else:
        print("✅ All cases have complete metadata")
        return 0


if __name__ == "__main__":
    sys.exit(main())
