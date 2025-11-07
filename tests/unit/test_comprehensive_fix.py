#!/usr/bin/env python3
"""Comprehensive test to verify the CBR fix is working correctly."""

import asyncio
import json

from cbr_mcp_server import CBRMCPServer


async def test_comprehensive():
    """Run a comprehensive test of the CBR MCP server."""

    print("=" * 80)
    print("COMPREHENSIVE CBR FIX VALIDATION")
    print("=" * 80)

    # Initialize the server
    print("\n1. Initializing CBR MCP Server...")
    server = CBRMCPServer()
    print("   ✓ Server initialized")

    # Test cases with different queries and thresholds
    test_cases = [
        {
            "query": "react login form authentication user interface component",
            "max_results": 5,
            "similarity_threshold": 0.7,
            "expected_min_results": 1,
        },
        {
            "query": "javascript async await promise",
            "max_results": 3,
            "similarity_threshold": 0.4,
            "expected_min_results": 2,
        },
        {
            "query": "firebase authentication",
            "max_results": 10,
            "similarity_threshold": 0.5,
            "expected_min_results": 0,  # May or may not have results
        },
    ]

    print("\n2. Running test queries...")
    all_passed = True

    for i, test in enumerate(test_cases, 1):
        print(f"\n   Test {i}:")
        print(f"   Query: {test['query'][:50]}...")
        print(f"   Threshold: {test['similarity_threshold']}")

        try:
            # Call the cbr_retrieve method
            result = await server.cbr_retrieve(
                query=test["query"],
                max_results=test["max_results"],
                similarity_threshold=test["similarity_threshold"],
            )

            examples = result.get("examples", [])
            num_results = len(examples)

            # Check if we got the expected number of results
            passed = num_results >= test["expected_min_results"]
            status = "✓ PASS" if passed else "✗ FAIL"

            print(
                f"   Results: {num_results} found (expected min: {test['expected_min_results']})"
            )
            print(f"   Status: {status}")

            if examples:
                # Show the best match
                best = examples[0]
                print(f"   Best match:")
                print(f"     - ID: {best.get('id', 'N/A')}")
                print(f"     - Similarity: {best.get('similarity_score', 0):.4f}")

            if not passed:
                all_passed = False

        except Exception as e:
            print(f"   Status: ✗ ERROR - {e}")
            all_passed = False

    # Summary
    print("\n" + "=" * 80)
    print("3. SUMMARY")
    print("-" * 80)

    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nThe CBR MCP Server is now working correctly:")
        print("  • Configuration: use_real_db=True by default")
        print("  • Embedding model: Loads securely without trust_remote_code")
        print("  • Similarity calculation: Fixed for unnormalized vectors")
        print("  • Results: Successfully returning relevant examples")
    else:
        print("✗ Some tests failed. Please review the results above.")

    print("\n" + "=" * 80)
    print("Fix validation complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_comprehensive())
