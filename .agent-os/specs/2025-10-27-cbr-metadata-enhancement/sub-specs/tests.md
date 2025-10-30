# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-10-27-cbr-metadata-enhancement/spec.md

> Created: 2025-10-27
> Version: 1.0.0

## Unit Tests

### MetadataMigration Class Tests

**test_detect_category_subcategory_code_firebase:**
- Input: Problem text containing "Firebase authentication"
- Expected: Returns ("code", "firebase-auth")

**test_detect_category_subcategory_code_react:**
- Input: Problem text containing "React component"
- Expected: Returns ("code", "react-components")

**test_detect_category_subcategory_orchestration_remediation:**
- Input: Problem text containing "remediation protocol"
- Expected: Returns ("orchestration", "remediation")

**test_detect_category_subcategory_orchestration_planning:**
- Input: Problem text containing "plan decomposition"
- Expected: Returns ("orchestration", "planning")

**test_detect_category_subcategory_default:**
- Input: Problem text with no recognizable patterns
- Expected: Returns ("code", "general")

**test_extract_tags_multiple_keywords:**
- Input: Problem text "React Firebase authentication with TypeScript"
- Expected: Returns "react,firebase,authentication,typescript"

**test_extract_tags_no_keywords:**
- Input: Problem text with no technology keywords
- Expected: Returns "" (empty string)

**test_extract_tags_case_insensitive:**
- Input: Problem text "REACT Component with FIREBASE"
- Expected: Returns "react,firebase" (lowercase)

### ProductionCBRRetriever.search_by_category Tests

**test_search_by_category_filter_category_only:**
- Setup: Collection with mixed categories
- Input: category="orchestration", no subcategory
- Expected: Returns only orchestration cases, filters out code/best-practice

**test_search_by_category_filter_category_and_subcategory:**
- Setup: Collection with multiple subcategories
- Input: category="code", subcategory="firebase-auth"
- Expected: Returns only code/firebase-auth cases

**test_search_by_category_with_query_text:**
- Setup: Collection with orchestration cases
- Input: category="orchestration", query="remediation workflow"
- Expected: Returns orchestration cases ranked by similarity to query

**test_search_by_category_no_query_text:**
- Setup: Collection with code cases
- Input: category="code", subcategory="react-components", query=""
- Expected: Returns all react-components cases (no similarity ranking)

**test_search_by_category_empty_results:**
- Setup: Collection with no orchestration cases
- Input: category="orchestration"
- Expected: Returns empty list []

**test_search_by_category_invalid_category:**
- Input: category="invalid-category"
- Expected: Raises ValueError with message about valid categories

**test_search_by_category_invalid_subcategory:**
- Input: category="code", subcategory="invalid-subcat"
- Expected: Returns empty list (ChromaDB returns no matches)

**test_search_by_category_chromadb_error_fallback:**
- Setup: Mock ChromaDB query to raise exception
- Input: category="code"
- Expected: Logs error, falls back to unfiltered query with warning

### ProductionCBRRetriever.get_categories Tests

**test_get_categories_returns_hierarchical_structure:**
- Setup: Collection with cases across all categories
- Expected: Returns list with 4 top-level categories, each with subcategories list

**test_get_categories_includes_counts:**
- Setup: Collection with 5 code/firebase-auth cases, 3 orchestration/remediation cases
- Expected: Each category shows correct count, each subcategory shows correct count

**test_get_categories_empty_collection:**
- Setup: Empty collection
- Expected: Returns 4 categories with count=0, empty subcategories lists

**test_get_categories_all_subcategories_present:**
- Setup: Collection with at least one case per subcategory
- Expected: All defined subcategories appear in results

**test_get_categories_unknown_subcategory:**
- Setup: Collection with case having subcategory="unknown"
- Expected: "unknown" appears in subcategories list with count

## Integration Tests

### End-to-End Migration Tests

**test_migration_full_collection:**
- Setup: ChromaDB collection with 50 existing cases (no category metadata)
- Execute: Run migration script
- Verify:
  - All 50 cases have category field
  - All 50 cases have subcategory field
  - All 50 cases have tags field (may be empty)
  - No embeddings were changed (verify embedding vectors unchanged)

**test_migration_idempotent:**
- Setup: Collection already migrated
- Execute: Run migration script again
- Verify:
  - No errors
  - Metadata unchanged (same categories/subcategories/tags)
  - Migration count shows 0 cases migrated

**test_migration_partial_completion:**
- Setup: Collection with 25 migrated cases, 25 unmigrated cases
- Execute: Run migration script
- Verify:
  - Only 25 new cases migrated
  - Existing migrated cases unchanged
  - All 50 cases have complete metadata

**test_migration_categorization_accuracy:**
- Setup: Collection with known test cases
  - Case 1: "Firebase authentication with React"
  - Case 2: "Remediation protocol for failed verification"
  - Case 3: "Completion bias anti-pattern example"
- Execute: Run migration
- Verify:
  - Case 1: category="code", subcategory="firebase-auth", tags contains "firebase,react"
  - Case 2: category="orchestration", subcategory="remediation"
  - Case 3: category="anti-pattern", subcategory="completion-bias"

### Category Filtering Integration Tests

**test_filter_by_category_e2e:**
- Setup: Load collection with mixed categories (code, orchestration, best-practice)
- Query: cbr_search_category with category="orchestration"
- Verify:
  - Results contain only orchestration cases
  - No code or best-practice cases in results
  - Results ranked by similarity if query text provided

**test_filter_by_category_and_subcategory_e2e:**
- Setup: Load collection with multiple code subcategories
- Query: cbr_search_category with category="code", subcategory="firebase-auth"
- Verify:
  - Results contain only code/firebase-auth cases
  - No react-components or api-routes cases in results

**test_backward_compatibility_no_filter:**
- Setup: Migrated collection
- Query: cbr_retrieve (original tool, no category parameter)
- Verify:
  - Returns cases from all categories
  - No filtering applied
  - Existing behavior unchanged

**test_backward_compatibility_existing_metadata:**
- Setup: Collection with existing "source" and "type" metadata
- Execute: Migration
- Verify:
  - Existing "source" field preserved
  - Existing "type" field preserved
  - New category/subcategory/tags fields added

### MCP Tool Integration Tests

**test_mcp_cbr_search_category_with_filters:**
- Setup: MCP server with migrated collection
- Request: Call cbr_search_category tool with category="orchestration", subcategory="remediation"
- Verify:
  - MCP response successful
  - Results contain only orchestration/remediation cases
  - Response format matches MCP specification

**test_mcp_cbr_retrieve_unchanged:**
- Setup: MCP server with migrated collection
- Request: Call cbr_retrieve tool (no category parameter)
- Verify:
  - MCP response successful
  - Returns cases across all categories
  - Backward compatibility maintained

**test_mcp_get_categories_resource:**
- Setup: MCP server with migrated collection
- Request: Access cbr://categories resource
- Verify:
  - Returns hierarchical category structure
  - Each category includes subcategories list with counts
  - JSON format valid

## Performance Tests

**test_category_filter_performance:**
- Setup: Collection with 1000 cases across all categories
- Query: 100 queries with category filter
- Verify:
  - Average response time < 200ms
  - No performance degradation vs. unfiltered queries
  - Memory usage stable

**test_migration_performance:**
- Setup: Collection with 1000 existing cases
- Execute: Migration script
- Verify:
  - Migration completes in < 30 seconds
  - Memory usage < 500MB
  - No database corruption

**test_large_result_set_filtering:**
- Setup: Collection with 500 cases in single category
- Query: Category filter that matches all 500 cases
- Verify:
  - Query returns successfully (may warn about large results)
  - No memory issues
  - Response time < 1 second

## Error Handling Tests

**test_missing_collection_error:**
- Setup: ChromaDB client without collection
- Execute: Run migration
- Verify:
  - Raises appropriate error
  - Error message indicates collection not found
  - No partial migration

**test_chromadb_connection_failure:**
- Setup: Mock ChromaDB to raise connection error
- Query: search_by_category
- Verify:
  - Logs error with connection details
  - Falls back gracefully (unfiltered query or empty results)
  - No crash

**test_invalid_metadata_during_migration:**
- Setup: Case with malformed metadata (not a dict)
- Execute: Migration
- Verify:
  - Skips malformed case or applies default values
  - Logs warning with case ID
  - Continues migration for remaining cases

**test_embedding_model_unavailable:**
- Setup: Mock SentenceTransformer to be unavailable
- Query: search_by_category with query text
- Verify:
  - Returns cases without similarity ranking (get instead of query)
  - Logs warning about embedding model
  - No crash

## Validation Tests

**test_validate_all_cases_have_category:**
- Setup: Migrated collection
- Execute: Validation query
- Verify:
  - All cases have "category" field in metadata
  - All category values are valid (in allowed list)

**test_validate_all_cases_have_subcategory:**
- Setup: Migrated collection
- Execute: Validation query
- Verify:
  - All cases have "subcategory" field
  - All subcategories valid for their category

**test_validate_tags_format:**
- Setup: Migrated collection
- Execute: Validation query
- Verify:
  - All tags fields are strings
  - Tags are comma-separated (if not empty)
  - Tags are lowercase

**test_validate_subcategory_matches_category:**
- Setup: Migrated collection
- Execute: Validation check
- Verify:
  - No code cases with orchestration subcategories
  - No orchestration cases with code subcategories
  - All subcategories belong to their parent category
