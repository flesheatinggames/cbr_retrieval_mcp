# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-10-28-case-base-modular-refactoring/spec.md

> Created: 2025-10-28
> Version: 1.0.0

## Test Coverage Overview

This spec requires comprehensive testing of:
1. Dynamic case loader (cases/__init__.py)
2. Individual case module integrity
3. Metadata validation and completeness
4. Backward compatibility (case_base.py wrapper)
5. Integration with existing CBR MCP Server components

## Unit Tests

### Test Module: test_cases_loader.py

Tests for the dynamic case loader in cases/__init__.py

#### Test Group: Module Discovery

**test_discover_case_modules_finds_all_subdirectories**
- **Purpose:** Verify module discovery finds all expected subdirectories
- **Setup:** Use existing cases/ directory structure
- **Action:** Call discover_case_modules()
- **Assertions:**
  - Returned list includes modules from firebase/, react/, nextjs/, bootstrap/, webdev/, orchestration/, security/, rust/
  - Module paths use correct format: "cases.{subdir}.{filename}"
  - No __init__.py files included in results
  - No hidden directories (starting with _) included

**test_discover_case_modules_handles_empty_subdirectory**
- **Purpose:** Verify discovery handles subdirectories with no *_cases.py files
- **Setup:** Create temporary empty subdirectory in cases/
- **Action:** Call discover_case_modules()
- **Assertions:**
  - Empty subdirectory does not cause errors
  - Other valid modules still discovered

**test_discover_case_modules_excludes_non_cases_files**
- **Purpose:** Verify discovery ignores files not matching *_cases.py pattern
- **Setup:** Create test file cases/webdev/helper.py (not matching pattern)
- **Action:** Call discover_case_modules()
- **Assertions:**
  - helper.py not included in results
  - Only *_cases.py files returned

#### Test Group: Case Loading

**test_load_cases_from_module_success**
- **Purpose:** Verify successful case loading from valid module
- **Setup:** Use cases.firebase.firebase_auth_cases (known to exist)
- **Action:** Call load_cases_from_module("cases.firebase.firebase_auth_cases")
- **Assertions:**
  - Returns non-empty list
  - All items are dictionaries
  - Each case has "problem" and "solution" keys
  - Module's case list variable name ends with _CASES

**test_load_cases_from_module_handles_import_error**
- **Purpose:** Verify graceful handling of module import failures
- **Setup:** Mock importlib.import_module to raise ImportError
- **Action:** Call load_cases_from_module("cases.invalid.nonexistent")
- **Assertions:**
  - Returns empty list (not exception)
  - Error logged to logger
  - Log message includes module path and error details

**test_load_cases_from_module_handles_missing_case_list**
- **Purpose:** Verify handling of module without *_CASES variable
- **Setup:** Create temporary module with no case list variable
- **Action:** Call load_cases_from_module("cases.test.empty_module")
- **Assertions:**
  - Returns empty list
  - Warning logged to logger
  - Log message indicates no case list found

**test_load_cases_from_module_handles_non_list_case_variable**
- **Purpose:** Verify handling of *_CASES variable that's not a list
- **Setup:** Create temporary module with CASES = {} (dict instead of list)
- **Action:** Call load_cases_from_module("cases.test.invalid_type")
- **Assertions:**
  - Returns empty list or skips non-list variable
  - Warning logged if applicable

**test_loader_handles_cases_without_metadata**
- **Purpose:** Verify loader handles cases missing metadata fields gracefully
- **Setup:** Create test case without category/subcategory/tags fields
- **Action:** Load case through dynamic loader
- **Assertions:**
  - Case loads without errors
  - Warning logged for missing metadata
  - Case still accessible with problem/solution fields
  - Compatible with rust cases that may lack new metadata

#### Test Group: Aggregation

**test_load_all_cases_aggregates_from_all_modules**
- **Purpose:** Verify all cases from all modules are aggregated
- **Setup:** Use complete cases/ directory structure
- **Action:** Call load_all_cases()
- **Assertions:**
  - Returns list with exactly 49 cases (matching original case_base.py)
  - Cases from different modules are combined
  - Each case is a dictionary with required fields
  - No duplicate references (each case is a distinct object)

**test_load_all_cases_handles_partial_failure**
- **Purpose:** Verify partial loading continues despite individual module failures
- **Setup:** Mock one module to raise exception during import
- **Action:** Call load_all_cases()
- **Assertions:**
  - Returns cases from successful modules
  - Failed module logged as error
  - Overall process completes successfully
  - Case count reflects partial load (e.g., 44 instead of 49)

**test_load_all_cases_logs_progress**
- **Purpose:** Verify logging provides visibility into loading process
- **Setup:** Use complete cases/ directory
- **Action:** Call load_all_cases() with logger at INFO level
- **Assertions:**
  - Log shows module discovery count
  - Log shows per-module case counts
  - Log shows total cases loaded
  - Log format is clear and actionable

### Test Module: test_case_metadata.py

Tests for case metadata validation and completeness

#### Test Group: Metadata Validation

**test_all_web_cases_have_required_metadata**
- **Purpose:** Verify all web cases have category, subcategory, and tags
- **Setup:** Import all web case modules
- **Action:** Iterate through all cases in WEB_*_CASES lists
- **Assertions:**
  - Each case has "category" in ["firebase", "react", "nextjs", "bootstrap", "webdev"]
  - Each case has "subcategory" (non-empty string)
  - Each case has "tags" (list with at least 2 items)
  - Subcategory matches file naming convention

**test_all_orchestration_cases_have_required_metadata**
- **Purpose:** Verify all orchestration cases have correct metadata
- **Setup:** Import all orchestration case modules
- **Action:** Iterate through all ORCHESTRATION_*_CASES lists
- **Assertions:**
  - Each case has "category" == "orchestration"
  - Each case has valid "subcategory" (planning, remediation, etc.)
  - Each case has "tags" (list with at least 2 items)

**test_all_security_cases_have_required_metadata**
- **Purpose:** Verify all security cases have correct metadata
- **Setup:** Import all security case modules
- **Action:** Iterate through all SECURITY_*_CASES lists
- **Assertions:**
  - Each case has "category" == "security"
  - Each case has valid "subcategory" (auth, validation)
  - Each case has "tags" (list with at least 2 items)

**test_metadata_category_values_are_valid**
- **Purpose:** Verify category field only contains allowed values
- **Setup:** Import ALL_CASES from cases module
- **Action:** Check category field on all cases
- **Assertions:**
  - Every category in ["firebase", "react", "nextjs", "bootstrap", "webdev", "orchestration", "security", "rust"]
  - No typos or alternative spellings
  - No None or empty string categories

**test_metadata_tags_are_non_empty_lists**
- **Purpose:** Verify tags field format and content
- **Setup:** Import ALL_CASES from cases module
- **Action:** Check tags field on all cases
- **Assertions:**
  - tags is always a list type
  - tags list has at least 2 items
  - All tag items are strings
  - No empty string tags
  - Tags are lowercase

**test_metadata_subcategory_matches_file_naming**
- **Purpose:** Verify subcategory aligns with file name convention
- **Setup:** Check all case modules
- **Action:** For each module, verify subcategory matches file name pattern
- **Assertions:**
  - firebase_auth_cases.py → subcategory="auth"
  - orchestration_planning_cases.py → subcategory="planning"
  - security_auth_cases.py → subcategory="auth"
  - Pattern: {category}_{subcategory}_cases.py

#### Test Group: Content Integrity

**test_all_cases_have_problem_and_solution**
- **Purpose:** Verify core fields are preserved during refactoring
- **Setup:** Import ALL_CASES from cases module
- **Action:** Check each case for required fields
- **Assertions:**
  - Every case has "problem" (non-empty string)
  - Every case has "solution" (non-empty string)
  - Problem is 10-500 characters
  - Solution is 100-10,000 characters

**test_case_solutions_contain_code**
- **Purpose:** Verify solutions contain actual code (not just text)
- **Setup:** Import ALL_CASES from cases module
- **Action:** Check solution content for code indicators
- **Assertions:**
  - Solutions contain common code elements (import, function, class, etc.)
  - Solutions use code formatting (indentation, quotes)
  - Solutions are multi-line strings

**test_case_count_matches_original**
- **Purpose:** Verify no cases lost during refactoring
- **Setup:** Import ALL_CASES from cases module
- **Action:** Count total cases
- **Assertions:**
  - len(ALL_CASES) == 49 (exact match to original case_base.py)
  - Web cases: ~40
  - Security cases: ~4
  - Orchestration cases: ~5

### Test Module: test_case_base_wrapper.py

Tests for backward compatibility wrapper in case_base.py

#### Test Group: Backward Compatibility

**test_case_base_imports_from_cases_module**
- **Purpose:** Verify case_base.py correctly imports from new structure
- **Setup:** Import case_base module
- **Action:** Check CASE_BASE variable
- **Assertions:**
  - case_base.CASE_BASE exists
  - case_base.CASE_BASE is a list
  - case_base.CASE_BASE equals cases.ALL_CASES
  - Same object reference (not a copy)

**test_case_base_case_count_matches_all_cases**
- **Purpose:** Verify CASE_BASE has correct count
- **Setup:** Import both case_base and cases modules
- **Action:** Compare lengths
- **Assertions:**
  - len(case_base.CASE_BASE) == len(cases.ALL_CASES)
  - Both equal 49 cases

**test_case_base_helper_functions_work**
- **Purpose:** Verify legacy helper functions still work
- **Setup:** Import case_base module
- **Action:** Call save_case_base_to_file, search_cases, validate_case_base
- **Assertions:**
  - save_case_base_to_file creates JSON file with all cases
  - search_cases("firebase") returns relevant cases
  - validate_case_base returns True
  - get_case_statistics returns correct counts

**test_case_base_can_be_imported_standalone**
- **Purpose:** Verify case_base.py works as entry point
- **Setup:** Import only case_base (not cases)
- **Action:** Access case_base.CASE_BASE
- **Assertions:**
  - Import succeeds without errors
  - CASE_BASE is available
  - All cases loaded correctly
  - No circular import issues

**test_case_base_array_indexing_works**
- **Purpose:** Verify CASE_BASE supports array indexing patterns
- **Setup:** Import case_base module
- **Action:** Access CASE_BASE[0], CASE_BASE[-1], CASE_BASE[5]
- **Assertions:**
  - CASE_BASE[0] returns first case
  - CASE_BASE[-1] returns last case
  - Index access works as expected for list type

**test_case_base_iteration_works**
- **Purpose:** Verify CASE_BASE supports iteration patterns
- **Setup:** Import case_base module
- **Action:** Iterate with for case in CASE_BASE
- **Assertions:**
  - Iteration completes without errors
  - All 49 cases accessible via iteration
  - Each case is a dictionary with required fields

**test_case_base_slicing_works**
- **Purpose:** Verify CASE_BASE supports slicing patterns
- **Setup:** Import case_base module
- **Action:** Access CASE_BASE[0:10], CASE_BASE[10:], CASE_BASE[:5]
- **Assertions:**
  - CASE_BASE[0:10] returns 10 cases
  - Slicing operations return list type
  - Sliced results contain valid case dictionaries

## Integration Tests

### Test Module: test_cbr_integration.py

Tests for integration with existing CBR MCP Server components

#### Test Group: Setup Integration

**test_setup_vectordb_imports_all_cases**
- **Purpose:** Verify setup_vectordb.py works with new case structure
- **Setup:** Mock ChromaDB, import setup_vectordb
- **Action:** Run setup process
- **Assertions:**
  - setup_vectordb can import cases successfully
  - All 49 cases passed to ChromaDB
  - No import errors or exceptions
  - Embeddings generated for all cases

**test_setup_vectordb_handles_metadata_fields**
- **Purpose:** Verify setup processes new metadata fields
- **Setup:** Import setup_vectordb, mock ChromaDB
- **Action:** Setup case base with metadata
- **Assertions:**
  - Setup doesn't fail on new fields
  - Metadata fields passed to ChromaDB metadata (if implemented)
  - No errors about unexpected fields

#### Test Group: Retriever Integration

**test_retriever_works_with_new_case_structure**
- **Purpose:** Verify retriever.py works with modular cases
- **Setup:** Initialize retriever with ALL_CASES
- **Action:** Query for cases
- **Assertions:**
  - Retriever imports cases successfully
  - Semantic search returns relevant cases
  - Case format compatible with retriever
  - Results include new metadata fields

**test_retriever_backward_compatible_with_case_base**
- **Purpose:** Verify retriever works with case_base.CASE_BASE
- **Setup:** Initialize retriever using case_base.CASE_BASE
- **Action:** Query for cases
- **Assertions:**
  - Import from case_base works
  - Search results identical to ALL_CASES
  - No behavior changes

#### Test Group: MCP Server Integration

**test_mcp_server_loads_cases_on_startup**
- **Purpose:** Verify cbr_mcp_server.py initializes with new structure
- **Setup:** Start MCP server (or mock initialization)
- **Action:** Check case base loading
- **Assertions:**
  - Server starts successfully
  - Cases loaded from modular structure
  - All 49 cases available
  - No startup errors

**test_mcp_tools_return_cases_with_metadata**
- **Purpose:** Verify MCP tools return enhanced cases
- **Setup:** Initialize MCP server, call cbr_retrieve
- **Action:** Retrieve cases via MCP tool
- **Assertions:**
  - Cases returned with category field
  - Cases returned with subcategory field
  - Cases returned with tags field
  - Tools don't fail on new fields

## Performance Tests

### Test Module: test_loading_performance.py

Tests for performance characteristics of new structure

#### Test Group: Load Time

**test_load_all_cases_completes_within_time_limit**
- **Purpose:** Verify loading doesn't add significant startup overhead
- **Setup:** Time the load_all_cases() function
- **Action:** Measure execution time over 10 runs
- **Assertions:**
  - Average load time < 200ms
  - Maximum load time < 500ms
  - No outliers > 1 second
  - Comparable to original case_base.py import

**test_module_discovery_is_fast**
- **Purpose:** Verify module discovery is efficient
- **Setup:** Time discover_case_modules()
- **Action:** Measure execution time over 100 runs
- **Assertions:**
  - Average discovery time < 10ms
  - File system operations minimal
  - No redundant directory scans

#### Test Group: Memory Usage

**test_modular_structure_memory_overhead_acceptable**
- **Purpose:** Verify memory footprint is reasonable
- **Setup:** Measure memory before and after loading
- **Action:** Load ALL_CASES, measure memory delta
- **Assertions:**
  - Memory overhead < 15% vs original case_base.py
  - No memory leaks on repeated loads
  - Module objects don't persist unnecessarily

## Regression Tests

### Test Module: test_no_case_content_changes.py

Tests to ensure case content is preserved exactly

#### Test Group: Content Preservation

**test_firebase_auth_cases_unchanged**
- **Purpose:** Verify Firebase auth cases preserved exactly
- **Setup:** Load original case_base.py (git checkout), load new structure
- **Action:** Compare problem and solution fields
- **Assertions:**
  - All 5 Firebase auth cases present
  - Problem text identical character-by-character
  - Solution code identical character-by-character
  - Only metadata fields added

**test_orchestration_cases_unchanged**
- **Purpose:** Verify orchestration cases preserved exactly
- **Setup:** Load original case_base.py, load new structure
- **Action:** Compare all orchestration cases
- **Assertions:**
  - All 5 orchestration cases present
  - Content identical (excluding metadata)
  - Sequential thinking examples preserved

**test_all_case_ids_preserved_if_used**
- **Purpose:** Verify case IDs unchanged (if cases have IDs)
- **Setup:** Check if original cases have ID fields
- **Action:** Compare IDs between old and new structure
- **Assertions:**
  - If IDs exist, they are preserved
  - ID generation method unchanged
  - No ID collisions in new structure

## Test Execution Strategy

### Test Organization

```
tests/
├── unit/
│   ├── test_cases_loader.py           # Dynamic loader tests
│   ├── test_case_metadata.py          # Metadata validation tests
│   └── test_case_base_wrapper.py      # Backward compatibility tests
├── integration/
│   ├── test_cbr_integration.py        # CBR component integration
│   └── test_mcp_integration.py        # MCP server integration
├── performance/
│   └── test_loading_performance.py    # Load time and memory tests
└── regression/
    └── test_no_case_content_changes.py # Content preservation tests
```

### Test Execution Order

1. **Unit Tests First** - Validate individual components (loader, metadata, wrapper)
2. **Integration Tests Second** - Verify components work together
3. **Performance Tests Third** - Ensure acceptable performance
4. **Regression Tests Last** - Confirm no unintended changes

### Coverage Requirements

- **Line Coverage:** 95%+ for cases/__init__.py
- **Branch Coverage:** 90%+ for error handling paths
- **Integration Coverage:** All existing CBR functionality tested
- **Regression Coverage:** 100% of case content validated

## Test Data

### Fixtures

**fixture_sample_case** - Valid case with metadata
```python
@pytest.fixture
def sample_case():
    return {
        "problem": "Example problem description",
        "solution": "def example():\n    pass",
        "category": "firebase",
        "subcategory": "auth",
        "tags": ["firebase", "authentication"]
    }
```

**fixture_invalid_case_missing_fields** - Case missing required fields
```python
@pytest.fixture
def invalid_case_missing_fields():
    return {
        "problem": "Example problem",
        # Missing solution, category, subcategory, tags
    }
```

**fixture_case_with_invalid_category** - Case with invalid category
```python
@pytest.fixture
def invalid_case_category():
    return {
        "problem": "Example",
        "solution": "code",
        "category": "invalid",  # Not in allowed list
        "subcategory": "test",
        "tags": ["tag1", "tag2"]
    }
```

### Mock Objects

**mock_chromadb** - Mock ChromaDB client for setup tests
**mock_logger** - Mock logger for testing log output
**mock_importlib** - Mock importlib for testing error handling

## Success Criteria

All tests must pass with:
- ✅ 49 total cases loaded from modular structure
- ✅ All cases have valid metadata (category, subcategory, tags)
- ✅ case_base.CASE_BASE equals cases.ALL_CASES
- ✅ No case content changes (problem/solution identical)
- ✅ All existing CBR MCP Server functionality works
- ✅ Load time < 200ms average
- ✅ Memory overhead < 15%
- ✅ 95%+ code coverage on new loader code
