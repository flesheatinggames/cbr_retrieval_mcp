# Spec Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/specs/2025-11-04-vector-db-deduplication/spec.md

> Created: 2025-11-04
> Status: Ready for Implementation

## Note
Always run tests in parallel mode using `pytest -n auto`.

## Tasks

- [x] 1. Content-Based ID Generation
  - [x] 1.1 Write unit tests for `generate_case_id()` function
    - Test SHA-256 hash generation from case content
    - Test deterministic ID generation (same content → same ID)
    - Test ID format (`case_<16_char_hash>`)
    - Test handling of different case structures
    - Test edge cases (empty fields, special characters, Unicode)
  - [x] 1.2 Implement `generate_case_id(case: Dict[str, Any]) -> str` function
    - Create canonical string representation of case content
    - Implement SHA-256 hashing
    - Extract first 16 characters of hex digest
    - Return formatted ID string (`case_<hash>`)
  - [x] 1.3 Update existing ID generation code (lines 273, 301) to use new function
    - Replace sequential ID logic with content-based ID calls
    - Ensure backward compatibility with existing ID format
  - [x] 1.4 Verify all tests pass for content-based ID generation

- [x] 2. Deduplication Logic Implementation
  - [x] 2.1 Write unit tests for `identify_new_cases()` function
    - Test detection of new cases not in collection
    - Test identification of existing cases (should be skipped)
    - Test handling of empty collections
    - Test handling of large case sets (performance)
    - Test edge cases (malformed IDs, missing metadata)
  - [x] 2.2 Implement `identify_new_cases(all_cases: List[Dict], collection) -> Tuple[List[Dict], int]` function
    - Query collection for existing case IDs
    - Compare input cases against existing IDs
    - Return list of new cases and count of skipped duplicates
    - Optimize for performance with batch ID lookups
  - [ ] 2.3 Write integration tests for deduplication workflow
    - Test full workflow: load cases → identify new → add to collection
    - Test behavior with partially populated database
    - Test behavior with fully populated database (all duplicates)
    - Test behavior with empty database (all new)
  - [x] 2.4 Verify all tests pass for deduplication logic

- [x] 3. Incremental Update Workflow
  - [x] 3.1 Write integration tests for incremental update mode
    - Test that existing cases are not deleted
    - Test that new cases are added successfully
    - Test that duplicate cases are skipped correctly
    - Test statistics output (added, skipped, total counts)
    - Test workflow with multiple runs (idempotency)
  - [x] 3.2 Remove deletion logic (lines 288-315 in setup_vectordb.py)
    - Delete code block that deletes existing collection
    - Remove associated deletion confirmation logic
    - Preserve collection existence check
  - [x] 3.3 Implement incremental update workflow in main logic
    - Check if collection exists
    - If exists, identify new cases using `identify_new_cases()`
    - Add only new cases to collection
    - If not exists, create collection and add all cases
  - [x] 3.4 Update console output with incremental statistics
    - Display count of cases added
    - Display count of duplicates skipped
    - Display total cases in database after operation
    - Maintain clear, user-friendly messaging
  - [x] 3.5 Verify all tests pass for incremental update workflow

- [x] 4. Validation Mode Implementation
  - [x] 4.1 Write unit tests for `validate_database()` function
    - Test detection of missing cases (in files but not in DB)
    - Test detection of orphaned cases (in DB but not in files)
    - Test validation report format and content
    - Test handling of valid database (no discrepancies)
    - Test handling of invalid database (discrepancies found)
  - [x] 4.2 Write integration tests for `--validate` flag
    - Test command line parsing of `--validate` flag
    - Test validation mode execution path
    - Test that validation mode does not modify database
    - Test validation output format and clarity
  - [x] 4.3 Implement `validate_database(all_cases: List[Dict], collection) -> Dict[str, Any]` function
    - Generate IDs for all file-based cases
    - Query all IDs from collection
    - Identify missing cases (files → DB)
    - Identify orphaned cases (DB → files)
    - Return validation report dictionary
  - [x] 4.4 Add `--validate` command line argument
    - Update argument parser with `--validate` flag
    - Add help text explaining validation mode
  - [x] 4.5 Implement validation mode execution path
    - Check for `--validate` flag in main logic
    - If set, run `validate_database()` instead of update
    - Display validation report to user
    - Exit without modifying database
  - [x] 4.6 Verify all tests pass for validation mode

- [x] 5. Enhanced User Feedback and Error Handling
  - [x] 5.1 Write tests for user feedback output
    - Test console message formatting
    - Test statistics display accuracy
    - Test error message clarity
    - Test logging output completeness
  - [x] 5.2 Implement enhanced console output
    - Add clear section headers for operation stages
    - Display progress indicators for long operations
    - Show detailed statistics after completion
    - Maintain consistent message formatting
  - [x] 5.3 Implement comprehensive error handling
    - Add try-catch blocks around ID generation
    - Add error handling for collection queries
    - Add validation for case data integrity
    - Provide helpful error messages for common failures
  - [x] 5.4 Add logging for debugging and audit
    - Log ID generation for each case
    - Log deduplication decisions
    - Log validation results
    - Log any errors or warnings
  - [x] 5.5 Update documentation in script docstrings
    - Document new functions with examples
    - Update main script docstring with new behavior
    - Add usage examples for all modes
  - [x] 5.6 Verify all tests pass for user feedback and error handling

- [x] 6. Integration Testing and Verification
  - [x] 6.1 Write end-to-end integration tests
    - Test complete workflow: fresh database → populate → re-run (no duplicates)
    - Test workflow: partial database → add new cases → verify no duplicates
    - Test validation mode on known-good database
    - Test validation mode on database with discrepancies
    - Test error recovery scenarios
  - [x] 6.2 Run full test suite and verify 100% pass rate
    - Execute all unit tests
    - Execute all integration tests
    - Execute end-to-end tests
    - Verify no test failures or warnings
  - [x] 6.3 Perform manual testing of key scenarios
    - Test with real case base files
    - Test incremental updates with actual data
    - Test validation mode with production-like database
    - Verify performance with large case sets
  - [x] 6.4 Update tests.md with any additional test cases discovered
    - Document any edge cases found during testing
    - Add regression tests for any bugs fixed
    - Ensure test coverage is comprehensive
  - [x] 6.5 Final verification: all acceptance criteria met
    - Verify no duplicate cases loaded on re-runs
    - Verify content-based IDs are deterministic
    - Verify incremental updates work correctly
    - Verify validation mode provides accurate reports
    - Verify user feedback is clear and helpful
