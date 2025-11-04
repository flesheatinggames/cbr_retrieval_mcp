# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-11-04-metadata-storage-bug-fix/spec.md

> Created: 2025-11-04
> Version: 1.0.0

## Unit Tests

### Test Group 1: Metadata Extraction

**File:** `tests/test_metadata_extraction.py`

**Test: test_metadata_extraction_from_case_dict**
- **Given:** A case dictionary with all fields (problem, solution, category, subcategory, tags)
- **When:** Extracting metadata for ChromaDB storage
- **Then:** Metadata dict contains all four fields (problem, category, subcategory, tags as comma-separated string)

**Test: test_metadata_extraction_with_missing_category**
- **Given:** A case dictionary missing category field
- **When:** Extracting metadata with .get() and default value
- **Then:** Metadata dict contains category="unknown"

**Test: test_metadata_extraction_with_missing_subcategory**
- **Given:** A case dictionary missing subcategory field
- **When:** Extracting metadata with .get() and default value
- **Then:** Metadata dict contains subcategory="unknown"

**Test: test_metadata_extraction_with_missing_tags**
- **Given:** A case dictionary missing tags field
- **When:** Extracting metadata with .get() and default value of empty list
- **Then:** Metadata dict contains tags="" (empty string from join)

**Test: test_metadata_extraction_with_empty_tags_list**
- **Given:** A case dictionary with tags=[]
- **When:** Extracting metadata and joining tags
- **Then:** Metadata dict contains tags="" (empty string)

**Test: test_metadata_extraction_tags_list_to_string_conversion**
- **Given:** A case dictionary with tags=["orchestration", "planning", "tdd"]
- **When:** Extracting metadata and joining tags with comma
- **Then:** Metadata dict contains tags="orchestration,planning,tdd"

**Test: test_metadata_list_length_matches_cases**
- **Given:** CASE_BASE with 103 cases
- **When:** Building metadata list from CASE_BASE
- **Then:** len(metadatas) == 103

**Test: test_all_metadata_dicts_have_required_fields**
- **Given:** Metadata list built from CASE_BASE
- **When:** Checking each metadata dict
- **Then:** Every dict has keys: problem, category, subcategory, tags

### Test Group 2: Database Population with Metadata

**File:** `tests/test_database_population.py`

**Test: test_populate_empty_database_with_full_metadata**
- **Given:** Empty ChromaDB collection
- **When:** Running setup_vectordb.py with fixed metadata code
- **Then:**
  - Collection count is 103
  - First case metadata contains all four fields
  - Sample case has correct category value
  - Sample case has correct subcategory value
  - Sample case has correct tags string

**Test: test_force_rebuild_replaces_broken_metadata**
- **Given:** Existing database with broken metadata (only problem field)
- **When:** Running setup_vectordb.py --force with fixed code
- **Then:**
  - Old collection deleted
  - New collection created
  - Collection count is 103
  - All cases now have complete metadata

**Test: test_metadata_preserved_during_filtered_load**
- **Given:** Running setup_vectordb.py --category orchestration
- **When:** Loading only orchestration cases
- **Then:**
  - Filtered CASE_BASE contains only orchestration cases
  - All loaded cases have complete metadata
  - ChromaDB stores complete metadata for filtered subset

**Test: test_problem_field_backward_compatibility**
- **Given:** Database populated with new metadata code
- **When:** Querying for problem field in metadata
- **Then:** Problem field still exists and contains problem text

**Test: test_solution_stored_as_document**
- **Given:** Database populated with new metadata code
- **When:** Retrieving documents from collection
- **Then:** Documents contain solution code (unchanged from current behavior)

### Test Group 3: Category-Based Search Functionality

**File:** `tests/test_category_search.py`

**Test: test_search_by_category_orchestration**
- **Given:** Database with complete metadata
- **When:** Calling search_by_category(category="orchestration")
- **Then:**
  - Query succeeds (no error)
  - Returns approximately 24 orchestration cases
  - All returned cases have category="orchestration" in metadata

**Test: test_search_by_category_firebase**
- **Given:** Database with complete metadata
- **When:** Calling search_by_category(category="firebase")
- **Then:**
  - Query succeeds
  - Returns firebase cases
  - All returned cases have category="firebase"

**Test: test_search_by_category_rust**
- **Given:** Database with complete metadata
- **When:** Calling search_by_category(category="rust")
- **Then:**
  - Query succeeds
  - Returns rust cases (most numerous category)
  - All returned cases have category="rust"

**Test: test_search_by_category_and_subcategory**
- **Given:** Database with complete metadata
- **When:** Calling search_by_category(category="orchestration", subcategory="planning")
- **Then:**
  - Query succeeds
  - Returns only orchestration planning cases
  - All returned cases have category="orchestration" AND subcategory="planning"

**Test: test_search_by_category_with_query_text**
- **Given:** Database with complete metadata
- **When:** Calling search_by_category(category="orchestration", query="delegation pattern")
- **Then:**
  - Query succeeds
  - Returns orchestration cases ranked by similarity to query
  - All returned cases have category="orchestration"

**Test: test_search_nonexistent_category**
- **Given:** Database with complete metadata
- **When:** Calling search_by_category(category="nonexistent")
- **Then:** Raises ValueError with message about invalid category

**Test: test_search_invalid_subcategory_for_category**
- **Given:** Database with complete metadata
- **When:** Calling search_by_category(category="orchestration", subcategory="invalid")
- **Then:** Raises ValueError with message about invalid subcategory

### Test Group 4: Metadata Validation

**File:** `tests/test_metadata_validation.py`

**Test: test_validate_case_with_all_fields**
- **Given:** Case dictionary with all required fields
- **When:** Running validate_case() function
- **Then:** Returns True

**Test: test_validate_case_missing_category**
- **Given:** Case dictionary missing category field
- **When:** Running validate_case() function
- **Then:** Returns False and logs warning

**Test: test_validate_case_missing_subcategory**
- **Given:** Case dictionary missing subcategory field
- **When:** Running validate_case() function
- **Then:** Returns False and logs warning

**Test: test_validate_case_missing_tags**
- **Given:** Case dictionary missing tags field
- **When:** Running validate_case() function
- **Then:** Returns False and logs warning

**Test: test_validate_case_tags_not_list**
- **Given:** Case dictionary with tags as string instead of list
- **When:** Running validate_case() function
- **Then:** Returns False and logs warning

**Test: test_metadata_list_validation_before_storage**
- **Given:** Metadata list built from CASE_BASE
- **When:** Running validation before collection.add()
- **Then:** Assertion passes if lengths match, raises if mismatch

## Integration Tests

### Test Group 5: End-to-End Category Search Flow

**File:** `tests/test_e2e_category_search.py`

**Test: test_e2e_populate_and_search_by_category**
- **Given:** Clean database state
- **When:**
  1. Run setup_vectordb.py to populate with fixed metadata
  2. Initialize MCP server with retriever
  3. Call cbr_search_category(category="orchestration")
- **Then:**
  - Database population succeeds
  - Server initialization succeeds
  - Category search returns orchestration cases
  - All results have complete metadata

**Test: test_e2e_force_rebuild_and_verify_metadata**
- **Given:** Existing database with broken metadata
- **When:**
  1. Run setup_vectordb.py --force
  2. Verify collection count
  3. Retrieve sample case and check metadata
- **Then:**
  - Collection deleted and recreated
  - Count matches expected (103 cases)
  - Sample case has all metadata fields

**Test: test_e2e_filtered_load_and_category_search**
- **Given:** Clean database state
- **When:**
  1. Run setup_vectordb.py --category orchestration firebase
  2. Call cbr_search_category(category="orchestration")
  3. Call cbr_search_category(category="rust")
- **Then:**
  - Only orchestration and firebase cases loaded
  - Orchestration search succeeds
  - Rust search returns empty (not loaded)

### Test Group 6: MCP Tool Integration

**File:** `tests/test_mcp_category_tool.py`

**Test: test_mcp_cbr_search_category_tool_orchestration**
- **Given:** MCP server with fixed database
- **When:** Calling MCP tool cbr_search_category with category="orchestration"
- **Then:**
  - Tool call succeeds
  - Returns JSON response with category and results fields
  - Results contain orchestration cases

**Test: test_mcp_cbr_search_category_tool_with_subcategory**
- **Given:** MCP server with fixed database
- **When:** Calling MCP tool with category="orchestration", subcategory="planning"
- **Then:**
  - Tool call succeeds
  - Returns filtered results
  - All results match both category and subcategory

**Test: test_mcp_cbr_search_category_tool_error_handling**
- **Given:** MCP server with fixed database
- **When:** Calling MCP tool with invalid category
- **Then:**
  - Tool returns error response
  - Error message indicates invalid category
  - Server remains stable

### Test Group 7: Backward Compatibility

**File:** `tests/test_backward_compatibility.py`

**Test: test_existing_semantic_search_still_works**
- **Given:** Database with new metadata schema
- **When:** Performing semantic search without category filter
- **Then:** Search succeeds and returns relevant results

**Test: test_problem_field_still_accessible**
- **Given:** Database with new metadata schema
- **When:** Accessing metadata["problem"] field
- **Then:** Field exists and contains problem text

**Test: test_solution_retrieval_unchanged**
- **Given:** Database with new metadata schema
- **When:** Retrieving case by ID
- **Then:** Solution code retrieved correctly (no change from current behavior)

**Test: test_cbr_retrieve_tool_still_works**
- **Given:** MCP server with fixed database
- **When:** Calling cbr_retrieve tool (semantic search)
- **Then:** Tool works as before, now with enriched metadata in results

**Test: test_cbr_find_similar_tool_still_works**
- **Given:** MCP server with fixed database
- **When:** Calling cbr_find_similar tool
- **Then:** Tool works as before, now with enriched metadata in results

## Test Execution Order

### Phase 1: Unit Tests (Fast)
1. Run test_metadata_extraction.py - Verify data transformation logic
2. Run test_metadata_validation.py - Verify validation logic

### Phase 2: Integration Tests (Slow - requires database)
1. Run test_database_population.py - Verify database operations
2. Run test_category_search.py - Verify search functionality
3. Run test_e2e_category_search.py - Verify complete flow

### Phase 3: MCP Integration Tests (Slow - requires server)
1. Run test_mcp_category_tool.py - Verify MCP tool integration
2. Run test_backward_compatibility.py - Verify no regressions

## Test Data

### Mock Cases for Testing

```python
MOCK_CASE_COMPLETE = {
    "problem": "Test problem description",
    "solution": "Test solution code",
    "category": "test-category",
    "subcategory": "test-subcategory",
    "tags": ["tag1", "tag2", "tag3"]
}

MOCK_CASE_MISSING_CATEGORY = {
    "problem": "Test problem",
    "solution": "Test solution",
    "subcategory": "test-subcategory",
    "tags": ["tag1"]
}

MOCK_CASE_MISSING_TAGS = {
    "problem": "Test problem",
    "solution": "Test solution",
    "category": "test-category",
    "subcategory": "test-subcategory"
}

MOCK_CASE_EMPTY_TAGS = {
    "problem": "Test problem",
    "solution": "Test solution",
    "category": "test-category",
    "subcategory": "test-subcategory",
    "tags": []
}
```

### Expected Metadata Output

```python
EXPECTED_METADATA_COMPLETE = {
    "problem": "Test problem description",
    "category": "test-category",
    "subcategory": "test-subcategory",
    "tags": "tag1,tag2,tag3"
}

EXPECTED_METADATA_WITH_DEFAULTS = {
    "problem": "Test problem",
    "category": "unknown",
    "subcategory": "test-subcategory",
    "tags": "tag1"
}

EXPECTED_METADATA_EMPTY_TAGS = {
    "problem": "Test problem",
    "category": "test-category",
    "subcategory": "test-subcategory",
    "tags": ""
}
```

## Test Coverage Goals

- **Unit Tests:** 100% coverage of metadata extraction and validation logic
- **Integration Tests:** 100% coverage of database population and search paths
- **MCP Tool Tests:** 100% coverage of cbr_search_category tool with all parameter combinations
- **Regression Tests:** All existing tests continue to pass with new metadata schema

## Test Execution Commands

```bash
# Run all tests
pytest tests/

# Run specific test group
pytest tests/test_metadata_extraction.py
pytest tests/test_database_population.py
pytest tests/test_category_search.py

# Run with coverage report
pytest --cov=scripts.utilities.setup_vectordb --cov=src.cbr_mcp_server tests/

# Run only fast unit tests
pytest tests/test_metadata_extraction.py tests/test_metadata_validation.py

# Run only integration tests
pytest tests/test_database_population.py tests/test_category_search.py tests/test_e2e_category_search.py
```
