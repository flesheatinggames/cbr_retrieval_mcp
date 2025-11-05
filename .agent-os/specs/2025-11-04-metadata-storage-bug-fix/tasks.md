# Spec Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/specs/2025-11-04-metadata-storage-bug-fix/spec.md

> Created: 2025-11-04
> Status: Ready for Implementation

## Note
Always run tests in parallel mode using `pytest -n auto`.

## Tasks

- [x] 1. Create Metadata Extraction Tests
  - [x] 1.1 Write unit tests for metadata extraction from case dictionaries (test_metadata_extraction.py)
    - **Test Coverage:**
      - test_metadata_extraction_from_case_dict - Complete case with all fields
      - test_metadata_extraction_with_missing_category - Defaults to "unknown"
      - test_metadata_extraction_with_missing_subcategory - Defaults to "unknown"
      - test_metadata_extraction_with_missing_tags - Defaults to empty string
      - test_metadata_extraction_tags_list_to_string_conversion - Joins with comma
      - test_metadata_list_length_matches_cases - Verifies list lengths match
      - test_all_metadata_dicts_have_required_fields - Validates all dicts complete
  - [x] 1.2 Verify all metadata extraction tests fail (no implementation yet)

- [x] 2. Create Database Population Tests
  - [x] 2.1 Write integration tests for database population with complete metadata (test_database_population.py)
    - **Test Coverage:**
      - test_populate_empty_database_with_full_metadata - Populates fresh database
      - test_force_rebuild_replaces_broken_metadata - Migrates existing database
      - test_metadata_preserved_during_filtered_load - Filtered loading works
      - test_problem_field_backward_compatibility - Problem field still exists
      - test_solution_stored_as_document - Solutions stored correctly
  - [x] 2.2 Verify all database population tests fail (database still has broken metadata)

- [x] 3. Create Category Search Tests
  - [x] 3.1 Write integration tests for category-based search functionality (test_category_search.py)
    - **Test Coverage:**
      - test_search_by_category_orchestration - Searches orchestration category
      - test_search_by_category_firebase - Searches firebase category
      - test_search_by_category_rust - Searches rust category
      - test_search_by_category_and_subcategory - Filters by both fields
      - test_search_by_category_with_query_text - Combines filter and semantic search
      - test_search_nonexistent_category - Error handling for invalid category
      - test_search_invalid_subcategory_for_category - Error handling for invalid subcategory
  - [x] 3.2 Verify all category search tests fail (metadata not available for filtering)

- [x] 4. Create Metadata Validation Tests
  - [x] 4.1 Write unit tests for metadata validation logic (test_metadata_validation.py)
    - **Test Coverage:**
      - test_validate_case_with_all_fields - Valid case passes
      - test_validate_case_missing_category - Missing field detected
      - test_validate_case_missing_subcategory - Missing field detected
      - test_validate_case_missing_tags - Missing field detected
      - test_validate_case_tags_not_list - Type error detected
      - test_metadata_list_validation_before_storage - Length validation
  - [x] 4.2 Verify all validation tests fail (validation function doesn't exist yet)

- [x] 5. Implement Metadata Extraction Fix in setup_vectordb.py
  - [x] 5.1 Modify line 284 to extract complete metadata from CASE_BASE
    - **Implementation Details:**
      - Replace: `metadatas=[{"problem": p} for p in problems]`
      - With: Build metadata from CASE_BASE including category, subcategory, tags
      - Use `.get()` with defaults for missing fields
      - Convert tags list to comma-separated string
  - [x] 5.2 Modify line 312 to extract complete metadata from CASE_BASE (repopulation path)
    - **Implementation Details:**
      - Apply same fix as line 284
      - Ensure both code paths use identical metadata extraction logic
  - [x] 5.3 Add metadata validation before collection.add() calls
    - **Implementation Details:**
      - Assert metadata list length matches CASE_BASE length
      - Print sample metadata for verification
      - Check all metadata dicts have required fields
  - [x] 5.4 Run metadata extraction tests and verify they pass

- [x] 6. Add Optional Metadata Validation to Case Loading
  - [x] 6.1 Create validate_case() function in cases/__init__.py
    - **Implementation Details:**
      - Check all required fields present (problem, solution, category, subcategory, tags)
      - Verify tags is a list type
      - Log warnings for validation failures
      - Return boolean indicating validity
  - [x] 6.2 Integrate validation into load_cases_from_module() (optional validation with logging)
    - **Implementation Details:**
      - Call validate_case() for each loaded case
      - Log warnings but don't fail (validation is informational)
      - Count and report number of cases with issues
  - [x] 6.3 Run validation tests and verify they pass

- [x] 7. Migrate Existing Database with Fixed Metadata
  - [x] 7.1 Run setup_vectordb.py --force to rebuild database with complete metadata
    - **Migration Steps:**
      1. Backup existing database: `cp -r ./db ./db.backup.$(date +%Y%m%d)`
      2. Run: `python scripts/utilities/setup_vectordb.py --force`
      3. Verify output shows 103 cases loaded
      4. Verify sample metadata includes all fields
  - [x] 7.2 Verify database population tests pass
    - **Verification:**
      - Run test_database_population.py
      - All tests should pass
      - Database has 103 cases with complete metadata

- [x] 8. Verify Category Search Functionality
  - [x] 8.1 Run category search tests and verify they all pass
    - **Verification:**
      - Run test_category_search.py
      - All tests should pass
      - Category filtering now works correctly
  - [x] 8.2 Manual verification: Test cbr_search_category via MCP server
    - **Manual Test Steps:**
      1. Start MCP server
      2. Call cbr_search_category(category="orchestration")
      3. Verify returns ~24 orchestration cases
      4. Verify results include category metadata
      5. Test with subcategory filter
      6. Test with query parameter

- [x] 9. Create and Run End-to-End Tests
  - [x] 9.1 Write end-to-end integration tests (test_e2e_category_search.py)
    - **Test Coverage:**
      - test_e2e_populate_and_search_by_category - Full flow from population to search
      - test_e2e_force_rebuild_and_verify_metadata - Migration verification
      - test_e2e_filtered_load_and_category_search - Filtered loading works end-to-end
  - [x] 9.2 Run e2e tests and verify they pass

- [ ] 10. Create and Run MCP Tool Integration Tests
  - [ ] 10.1 Write MCP tool integration tests (test_mcp_category_tool.py)
    - **Test Coverage:**
      - test_mcp_cbr_search_category_tool_orchestration - Tool call with category
      - test_mcp_cbr_search_category_tool_with_subcategory - Tool call with subcategory
      - test_mcp_cbr_search_category_tool_error_handling - Error cases
  - [ ] 10.2 Run MCP tool tests and verify they pass

- [ ] 11. Create and Run Backward Compatibility Tests
  - [ ] 11.1 Write backward compatibility tests (test_backward_compatibility.py)
    - **Test Coverage:**
      - test_existing_semantic_search_still_works - Semantic search unchanged
      - test_problem_field_still_accessible - Problem field preserved
      - test_solution_retrieval_unchanged - Solution retrieval works
      - test_cbr_retrieve_tool_still_works - cbr_retrieve tool unaffected
      - test_cbr_find_similar_tool_still_works - cbr_find_similar tool unaffected
  - [ ] 11.2 Run backward compatibility tests and verify they pass

- [ ] 12. Run Complete Test Suite
  - [ ] 12.1 Run entire test suite and verify no regressions
    - **Command:** `pytest tests/ --cov`
    - **Verification:**
      - All new tests pass
      - All existing tests pass (no regressions)
      - Coverage report shows metadata code covered
  - [ ] 12.2 Verify all spec acceptance criteria met
    - **Acceptance Criteria:**
      - ✓ cbr_search_category(category="orchestration") returns orchestration cases
      - ✓ All metadata fields preserved in ChromaDB
      - ✓ Existing database migrated without data loss
      - ✓ Tests verify complete metadata storage

- [ ] 13. Code Review and Documentation
  - [ ] 13.1 Review all code changes for quality and adherence to standards
    - **Review Focus:**
      - Code style compliance (Black, isort)
      - Type hints present
      - Error handling appropriate
      - No security issues
      - Documentation complete
  - [ ] 13.2 Update README or documentation if needed
    - **Documentation Updates:**
      - Note metadata schema in setup_vectordb.py docstring
      - Update any developer documentation about case structure
      - Add migration notes if relevant

## Implementation Notes

### TDD Workflow
- Tests are written FIRST before any implementation code
- Each implementation task should make failing tests pass
- Verification (karen) happens after each implementation

### Database Migration Safety
- Always backup database before force rebuild: `cp -r ./db ./db.backup.$(date +%Y%m%d)`
- Migration is idempotent - can be run multiple times
- Source files (case files) are authoritative - database can always be rebuilt

### Critical Code Locations
- **Line 284:** `scripts/utilities/setup_vectordb.py` - Initial database population
- **Line 312:** `scripts/utilities/setup_vectordb.py` - Repopulation on count mismatch
- **Line 5306:** `src/cbr_mcp_server.py` - Category filter construction (no change needed, just relies on metadata)

### Testing Strategy
1. **Phase 1:** Unit tests (fast, no database needed)
2. **Phase 2:** Integration tests (require database operations)
3. **Phase 3:** MCP tool tests (require running server)
4. **Phase 4:** Backward compatibility verification

### Rollback Plan
If issues discovered after implementation:
1. Stop MCP server
2. Restore backup: `rm -rf ./db && cp -r ./db.backup.YYYYMMDD ./db`
3. Investigate issues
4. Fix and re-migrate
