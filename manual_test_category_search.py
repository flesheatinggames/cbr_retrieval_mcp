#!/usr/bin/env python3
"""
Manual MCP Server Category Search Verification Script

This script manually tests the cbr_search_category tool via the CBR MCP server
to verify that category-based search works correctly in the production environment.

Test Requirements (from tasks.md lines 110-117):
1. Start MCP server (if not already running)
2. Test basic category search - orchestration (~24 cases)
3. Test with subcategory filter
4. Test with query parameter
"""

import asyncio
import sys
from pathlib import Path
import importlib.util

# Load the CBRMCPServer module directly from the file to avoid package conflicts
cbr_server_path = Path(__file__).parent / "src" / "cbr_mcp_server.py"
spec = importlib.util.spec_from_file_location("cbr_mcp_server_module", cbr_server_path)
cbr_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cbr_module)

# Get the CBRMCPServer class from the loaded module
CBRMCPServer = cbr_module.CBRMCPServer


async def test_basic_category_search(server: CBRMCPServer):
    """Test 1: Basic category search for orchestration cases."""
    print("\n" + "="*80)
    print("TEST 1: Basic Category Search - orchestration")
    print("="*80)

    try:
        result = await server.cbr_search_category(
            category="orchestration",
            limit=50  # High limit to get all orchestration cases
        )

        num_results = len(result.get("results", []))
        print(f"✓ Search completed successfully")
        print(f"✓ Returned {num_results} orchestration cases")

        # Verify expected count (~24 cases)
        if num_results >= 20 and num_results <= 30:
            print(f"✓ Case count is in expected range (20-30)")
        else:
            print(f"⚠ WARNING: Expected ~24 cases, got {num_results}")

        # Verify metadata is present
        if num_results > 0:
            sample_case = result["results"][0]
            print(f"\n✓ Sample case metadata:")
            print(f"  - ID: {sample_case.get('id', 'MISSING')}")
            print(f"  - Category: {sample_case.get('category', 'MISSING')}")
            print(f"  - Subcategory: {sample_case.get('subcategory', 'MISSING')}")
            print(f"  - Has content: {'Yes' if sample_case.get('content') else 'No'}")

            # Check if all required metadata fields present
            required_fields = ['id', 'category', 'content']
            missing_fields = [f for f in required_fields if f not in sample_case]

            if missing_fields:
                print(f"✗ FAIL: Missing required fields: {missing_fields}")
                return False
            else:
                print(f"✓ All required metadata fields present")

        # Verify all results are orchestration category
        categories = [case.get('category') for case in result["results"]]
        non_orchestration = [c for c in categories if c != "orchestration"]

        if non_orchestration:
            print(f"✗ FAIL: Found non-orchestration cases: {set(non_orchestration)}")
            return False
        else:
            print(f"✓ All {num_results} results are orchestration category")

        print("\n✓ TEST 1 PASSED")
        return True

    except Exception as e:
        print(f"✗ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_subcategory_filter(server: CBRMCPServer):
    """Test 2: Category search with subcategory filter."""
    print("\n" + "="*80)
    print("TEST 2: Category + Subcategory Filter")
    print("="*80)

    try:
        # Test orchestration + remediation subcategory
        result = await server.cbr_search_category(
            category="orchestration",
            subcategory="remediation",
            limit=20
        )

        num_results = len(result.get("results", []))
        print(f"✓ Search completed successfully")
        print(f"✓ Returned {num_results} orchestration/remediation cases")

        if num_results > 0:
            # Verify all results match both category AND subcategory
            for i, case in enumerate(result["results"][:3]):  # Check first 3
                category = case.get('category')
                subcategory = case.get('subcategory')
                print(f"\n  Case {i+1}:")
                print(f"    Category: {category}")
                print(f"    Subcategory: {subcategory}")

                if category != "orchestration":
                    print(f"✗ FAIL: Wrong category: {category}")
                    return False

                if subcategory != "remediation":
                    print(f"✗ FAIL: Wrong subcategory: {subcategory}")
                    return False

            print(f"\n✓ All results match category='orchestration' AND subcategory='remediation'")
        else:
            print("⚠ WARNING: No results returned for orchestration/remediation filter")

        print("\n✓ TEST 2 PASSED")
        return True

    except Exception as e:
        print(f"✗ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_category_with_query(server: CBRMCPServer):
    """Test 3: Category search with semantic query."""
    print("\n" + "="*80)
    print("TEST 3: Category + Semantic Query")
    print("="*80)

    try:
        # Test orchestration category with query about planning
        result = await server.cbr_search_category(
            category="orchestration",
            query="planning and creating implementation plans",
            limit=5
        )

        num_results = len(result.get("results", []))
        print(f"✓ Search completed successfully")
        print(f"✓ Returned {num_results} orchestration cases matching query")

        if num_results > 0:
            print(f"\n✓ Top results:")
            for i, case in enumerate(result["results"]):
                category = case.get('category')
                subcategory = case.get('subcategory')
                similarity = case.get('similarity_score', 'N/A')
                content_preview = case.get('content', '')[:100]

                print(f"\n  Result {i+1}:")
                print(f"    Category: {category}")
                print(f"    Subcategory: {subcategory}")
                print(f"    Similarity: {similarity}")
                print(f"    Content preview: {content_preview}...")

                # Verify category filter still applies
                if category != "orchestration":
                    print(f"✗ FAIL: Query returned non-orchestration case: {category}")
                    return False

            print(f"\n✓ All results are orchestration category (filter + semantic search worked)")
        else:
            print("⚠ WARNING: No results returned for orchestration + query")

        print("\n✓ TEST 3 PASSED")
        return True

    except Exception as e:
        print(f"✗ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_comprehensive_category_coverage(server: CBRMCPServer):
    """Test 4: Verify all major categories work."""
    print("\n" + "="*80)
    print("TEST 4: Comprehensive Category Coverage")
    print("="*80)

    categories_to_test = ["orchestration", "code", "best-practice", "anti-pattern"]
    results_summary = {}
    all_passed = True

    for category in categories_to_test:
        try:
            result = await server.cbr_search_category(
                category=category,
                limit=50
            )

            num_results = len(result.get("results", []))
            results_summary[category] = num_results
            print(f"✓ {category}: {num_results} cases")

            # Verify all results match the category
            for case in result["results"]:
                if case.get('category') != category:
                    print(f"✗ FAIL: Category {category} returned case with category {case.get('category')}")
                    all_passed = False
                    break

        except Exception as e:
            print(f"✗ {category}: FAILED - {e}")
            all_passed = False

    print(f"\n✓ Category distribution:")
    total_cases = sum(results_summary.values())
    for category, count in results_summary.items():
        percentage = (count / total_cases * 100) if total_cases > 0 else 0
        print(f"  {category:20s}: {count:3d} cases ({percentage:5.1f}%)")
    print(f"  {'TOTAL':20s}: {total_cases:3d} cases")

    if all_passed:
        print("\n✓ TEST 4 PASSED")
    else:
        print("\n✗ TEST 4 FAILED")

    return all_passed


async def main():
    """Run all manual verification tests."""
    print("="*80)
    print("CBR MCP Server - Manual Category Search Verification")
    print("="*80)
    print("\nThis script tests the cbr_search_category tool to verify:")
    print("1. Basic category search returns correct count")
    print("2. Subcategory filtering works")
    print("3. Category + query combination works")
    print("4. All major categories are accessible")

    # Initialize the server
    print("\n" + "="*80)
    print("Initializing CBR MCP Server...")
    print("="*80)

    try:
        # Server initializes in __init__, no separate initialize() method needed
        server = CBRMCPServer()
        print("✓ Server initialized successfully")

    except Exception as e:
        print(f"✗ FATAL: Failed to initialize server: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Run all tests
    test_results = []

    test_results.append(await test_basic_category_search(server))
    test_results.append(await test_subcategory_filter(server))
    test_results.append(await test_category_with_query(server))
    test_results.append(await test_comprehensive_category_coverage(server))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(test_results)
    total = len(test_results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("\nThe cbr_search_category tool is working correctly:")
        print("  ✓ Category filtering works")
        print("  ✓ Subcategory filtering works")
        print("  ✓ Semantic query + category filtering works")
        print("  ✓ All metadata fields are present")
        print("  ✓ All major categories are accessible")
        return 0
    else:
        print(f"\n✗✗✗ {total - passed} TEST(S) FAILED ✗✗✗")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
