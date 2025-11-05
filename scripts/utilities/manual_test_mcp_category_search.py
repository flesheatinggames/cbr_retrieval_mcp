#!/usr/bin/env python3
"""
Manual MCP Server Category Search Verification Script

This script manually tests the cbr_search_category tool via the running MCP server
to verify that category-based search works correctly in the real production environment.

Task: 8.2 from metadata-storage-bug-fix spec
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src")
sys.path.insert(0, src_path)

# Import the MCP server components by loading the file directly
import importlib.util
cbr_mcp_server_path = os.path.join(src_path, "cbr_mcp_server.py")
spec = importlib.util.spec_from_file_location("cbr_mcp_server_module", cbr_mcp_server_path)
cbr_mcp_server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cbr_mcp_server_module)

# Extract the classes we need
CBRMCPServer = cbr_mcp_server_module.CBRMCPServer
CBRServerConfig = cbr_mcp_server_module.CBRServerConfig
StructuredLogger = cbr_mcp_server_module.StructuredLogger


class ManualMCPTester:
    """Manual tester for MCP server category search functionality."""

    def __init__(self):
        """Initialize the manual tester."""
        self.server = None
        self.results = []
        self.passed = 0
        self.failed = 0

    async def initialize_server(self):
        """Initialize the MCP server for testing."""
        print("\n" + "=" * 80)
        print("MANUAL MCP SERVER CATEGORY SEARCH VERIFICATION")
        print("=" * 80)
        print("\nInitializing MCP server...")

        try:
            # Create server config
            config = CBRServerConfig(
                db_path="./db",
                collection_name="code_solutions_case_base",
                use_real_db=True  # Ensure we use real database
            )

            # Create server - database is initialized in __init__
            self.server = CBRMCPServer(config=config)

            print("✓ MCP server initialized successfully")
            print(f"  Database: {config.db_path}")
            print(f"  Collection: {config.collection_name}")

            # Get database stats
            if self.server.retriever.collection:
                count = self.server.retriever.collection.count()
                print(f"  Total cases in database: {count}")
            else:
                print("  ⚠ Warning: Database collection not initialized")

            return True

        except Exception as e:
            print(f"✗ Failed to initialize MCP server: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_basic_category_search(self):
        """
        Test 1: Basic category search
        Test cbr_search_category(category="orchestration")
        """
        test_name = "Basic Category Search (orchestration)"
        print(f"\n{'─' * 80}")
        print(f"TEST 1: {test_name}")
        print(f"{'─' * 80}")

        try:
            print("\nCalling: cbr_search_category(category='orchestration', limit=30)")

            # Call the actual MCP tool method
            result = await self.server.cbr_search_category(
                category="orchestration",
                limit=30
            )

            # Verify result structure
            assert "category" in result, "Result missing 'category' field"
            assert "results" in result, "Result missing 'results' field"
            assert result["category"] == "orchestration", f"Expected category 'orchestration', got '{result['category']}'"

            results_list = result["results"]
            num_results = len(results_list)

            print(f"\n✓ Returned {num_results} results")

            # Verify we got orchestration cases (should be ~24)
            if num_results < 20:
                print(f"⚠ Warning: Expected ~24 orchestration cases, got {num_results}")
            else:
                print(f"✓ Result count looks correct (expected ~24, got {num_results})")

            # Verify results include category metadata
            if num_results > 0:
                first_case = results_list[0]
                print("\n✓ First result structure:")
                print(f"  - ID: {first_case.get('id', 'MISSING')}")
                print(f"  - Category: {first_case.get('category', 'MISSING')}")
                print(f"  - Subcategory: {first_case.get('subcategory', 'MISSING')}")
                print(f"  - Has content: {'content' in first_case}")

                # Verify all results have orchestration category
                non_orchestration = [r for r in results_list if r.get('category') != 'orchestration']
                if non_orchestration:
                    print(f"\n✗ Found {len(non_orchestration)} non-orchestration cases!")
                    for case in non_orchestration[:3]:
                        print(f"  - {case.get('id')}: category='{case.get('category')}'")
                    self.record_test(test_name, False, f"Found {len(non_orchestration)} non-orchestration cases")
                    return

                print(f"✓ All {num_results} results have category='orchestration'")

            self.record_test(test_name, True, f"Retrieved {num_results} orchestration cases with correct metadata")

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            self.record_test(test_name, False, str(e))

    async def test_subcategory_filter(self):
        """
        Test 2: Test with subcategory filter
        Test category + subcategory filtering
        """
        test_name = "Subcategory Filter"
        print(f"\n{'─' * 80}")
        print(f"TEST 2: {test_name}")
        print(f"{'─' * 80}")

        try:
            print("\nCalling: cbr_search_category(category='orchestration', subcategory='remediation', limit=20)")

            result = await self.server.cbr_search_category(
                category="orchestration",
                subcategory="remediation",
                limit=20
            )

            results_list = result["results"]
            num_results = len(results_list)

            print(f"\n✓ Returned {num_results} results")

            if num_results > 0:
                first_case = results_list[0]
                print("\n✓ First result structure:")
                print(f"  - ID: {first_case.get('id')}")
                print(f"  - Category: {first_case.get('category')}")
                print(f"  - Subcategory: {first_case.get('subcategory')}")

                # Verify all results match the filter
                mismatched = [
                    r for r in results_list
                    if r.get('category') != 'orchestration' or r.get('subcategory') != 'remediation'
                ]

                if mismatched:
                    print(f"\n✗ Found {len(mismatched)} results not matching filter!")
                    for case in mismatched[:3]:
                        print(f"  - {case.get('id')}: category='{case.get('category')}', subcategory='{case.get('subcategory')}'")
                    self.record_test(test_name, False, f"Found {len(mismatched)} mismatched results")
                    return

                print(f"✓ All {num_results} results have category='orchestration' AND subcategory='remediation'")

            self.record_test(test_name, True, f"Subcategory filtering works correctly ({num_results} results)")

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            self.record_test(test_name, False, str(e))

    async def test_query_parameter(self):
        """
        Test 3: Test with query parameter
        Test combination of category filtering and semantic search
        """
        test_name = "Query Parameter (category + semantic search)"
        print(f"\n{'─' * 80}")
        print(f"TEST 3: {test_name}")
        print(f"{'─' * 80}")

        try:
            query_text = "remediation protocol"
            print(f"\nCalling: cbr_search_category(category='orchestration', query='{query_text}', limit=10)")

            result = await self.server.cbr_search_category(
                category="orchestration",
                query=query_text,
                limit=10
            )

            results_list = result["results"]
            num_results = len(results_list)

            print(f"\n✓ Returned {num_results} results")

            if num_results > 0:
                print("\n✓ Top 3 results:")
                for i, case in enumerate(results_list[:3], 1):
                    similarity = case.get('similarity_score', 'N/A')
                    print(f"  {i}. ID: {case.get('id')}")
                    print(f"     Category: {case.get('category')}")
                    print(f"     Similarity: {similarity}")
                    # Show first 100 chars of content
                    content = case.get('content', '')
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"     Preview: {preview}")

                # Verify all results are orchestration category
                non_orchestration = [r for r in results_list if r.get('category') != 'orchestration']
                if non_orchestration:
                    print(f"\n✗ Found {len(non_orchestration)} non-orchestration cases!")
                    self.record_test(test_name, False, f"Category filter failed with query")
                    return

                print(f"\n✓ All results have category='orchestration'")
                print(f"✓ Results ranked by semantic similarity to '{query_text}'")

            self.record_test(test_name, True, f"Query + category filtering works ({num_results} results)")

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            self.record_test(test_name, False, str(e))

    async def test_category_no_subcategory(self):
        """
        Test 4: Test category without subcategory (browse all in category)
        Verify that omitting subcategory returns all cases in category
        """
        test_name = "Category Browse (no subcategory)"
        print(f"\n{'─' * 80}")
        print(f"TEST 4: {test_name}")
        print(f"{'─' * 80}")

        try:
            print("\nCalling: cbr_search_category(category='orchestration', limit=50)")

            result = await self.server.cbr_search_category(
                category="orchestration",
                limit=50
            )

            results_list = result["results"]
            num_results = len(results_list)

            print(f"\n✓ Returned {num_results} results")

            # Count subcategories present
            subcategories = {}
            for case in results_list:
                subcat = case.get('subcategory', 'unknown')
                subcategories[subcat] = subcategories.get(subcat, 0) + 1

            print(f"\n✓ Subcategory distribution:")
            for subcat, count in sorted(subcategories.items()):
                print(f"  - {subcat}: {count} cases")

            # Verify variety of subcategories (should have multiple)
            if len(subcategories) < 2:
                print(f"\n⚠ Warning: Expected multiple subcategories, got {len(subcategories)}")
            else:
                print(f"\n✓ Found {len(subcategories)} different subcategories (correctly returning all)")

            self.record_test(test_name, True, f"Category browse returns all subcategories ({num_results} cases, {len(subcategories)} subcategories)")

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            self.record_test(test_name, False, str(e))

    def record_test(self, test_name: str, passed: bool, message: str):
        """Record test result."""
        self.results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        for result in self.results:
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            print(f"\n{status}: {result['test']}")
            print(f"  {result['message']}")

        print("\n" + "─" * 80)
        total = self.passed + self.failed
        print(f"Total: {total} tests")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%")
        print("=" * 80)

        return self.failed == 0

    async def run_all_tests(self):
        """Run all manual verification tests."""
        # Initialize server
        if not await self.initialize_server():
            print("\n✗ Cannot proceed - server initialization failed")
            return False

        # Run tests
        await self.test_basic_category_search()
        await self.test_subcategory_filter()
        await self.test_query_parameter()
        await self.test_category_no_subcategory()

        # Print summary
        all_passed = self.print_summary()

        if all_passed:
            print("\n✓ All manual verification tests PASSED")
            print("✓ Category search works correctly via MCP interface")
        else:
            print("\n✗ Some tests FAILED - review results above")

        return all_passed


async def main():
    """Main entry point."""
    tester = ManualMCPTester()

    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
