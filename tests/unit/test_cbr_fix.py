#!/usr/bin/env python3
"""Test script to verify the CBR fix works correctly."""

import asyncio
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cbr_mcp_server import CBRServerConfig, ProductionCBRRetriever, StructuredLogger


async def test_cbr_retrieval():
    """Test CBR retrieval with the fixed similarity calculation."""

    print("=" * 80)
    print("Testing CBR Retrieval Fix")
    print("=" * 80)

    # Create configuration
    config = CBRServerConfig.from_environment()
    print(f"\nConfiguration:")
    print(f"  use_real_db: {config.use_real_db}")
    print(f"  database_path: {config.database_path}")
    print(f"  collection_name: {config.collection_name}")

    # Create logger
    logger = StructuredLogger(config)

    # Create retriever
    retriever = ProductionCBRRetriever(config, logger)

    # Test queries
    test_queries = [
        ("react login form authentication user interface component", 0.7),
        ("python flask api endpoint", 0.5),
        ("javascript async await promise", 0.3),
    ]

    for query, threshold in test_queries:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print(f"Threshold: {threshold}")
        print("-" * 60)

        try:
            # Retrieve examples
            results = await retriever.retrieve_relevant_examples(
                query=query, max_results=5, similarity_threshold=threshold
            )

            print(f"Found {len(results)} results:")
            for i, result in enumerate(results[:3], 1):  # Show first 3
                print(f"\n  Result {i}:")
                print(f"    ID: {result.get('id', 'N/A')}")
                print(f"    Similarity: {result.get('similarity_score', 0):.4f}")
                print(
                    f"    Category: {result.get('metadata', {}).get('category', 'N/A')}"
                )
                content = result.get("content", "")
                if content:
                    preview = content[:100].replace("\n", " ")
                    print(f"    Content: {preview}...")

        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()

    print(f"\n{'=' * 80}")
    print("Test completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_cbr_retrieval())
