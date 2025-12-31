# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-11-04-vector-db-deduplication/spec.md

> Created: 2025-11-04
> Updated: 2025-12-26
> Version: 2.0.0

## Test Coverage

### Unit Tests

#### **Content-Based ID Generation**

**Test: `test_generate_case_id_deterministic()`**
- Given a case dictionary with specific problem and solution
- When `generate_case_id()` is called multiple times
- Then the same ID should be returned every time
- Validates: Same content always produces same ID

**Test: `test_generate_case_id_format()`**
- Given a valid case dictionary
- When `generate_case_id()` is called
- Then the ID should match format `case_[a-f0-9]{16}`
- Validates: ID format is correct

**Test: `test_generate_case_id_different_content()`**
- Given two cases with different problems or solutions
- When `generate_case_id()` is called for each
- Then the IDs should be different
- Validates: Different content produces different IDs

**Test: `test_generate_case_id_order_independence()`**
- Given the same case data in different load orders
- When IDs are generated
- Then the same case should always get the same ID regardless of position
- Validates: Position in array doesn't affect ID

**Test: `test_generate_case_id_unicode_handling()`**
- Given cases with unicode characters in problem/solution
- When `generate_case_id()` is called
- Then IDs should be generated without errors
- Validates: Unicode content is properly handled

#### **Deduplication Logic**

**Test: `test_identify_new_cases_all_new()`**
- Given an empty ChromaDB collection
- And a list of cases to load
- When `identify_new_cases()` is called
- Then all cases should be identified as new
- And existing_cases list should be empty
- Validates: Empty database treats all cases as new

**Test: `test_identify_new_cases_all_existing()`**
- Given a ChromaDB collection with specific cases already loaded
- And the exact same list of cases to load
- When `identify_new_cases()` is called
- Then all cases should be identified as existing
- And new_cases list should be empty
- Validates: Loading same cases twice identifies them as existing

**Test: `test_identify_new_cases_mixed()`**
- Given a ChromaDB collection with 50 cases
- And a list of 150 cases (50 existing + 100 new)
- When `identify_new_cases()` is called
- Then 100 cases should be identified as new
- And 50 cases should be identified as existing
- Validates: Mixed scenario correctly separates new from existing

**Test: `test_identify_new_cases_empty_collection_error()`**
- Given a ChromaDB collection that raises an error when queried
- And a list of cases to load
- When `identify_new_cases()` is called
- Then it should treat all cases as new (graceful fallback)
- Validates: Error handling for inaccessible collections

**Test: `test_identify_new_cases_case_content_change()`**
- Given a case already in database with ID `case_abc123`
- And a case with same problem but different solution (different ID)
- When `identify_new_cases()` is called
- Then the modified case should be identified as new
- Validates: Content changes are detected and treated as new cases

#### **Validation Logic**

**Test: `test_validate_database_perfect_match()`**
- Given a database with 100 cases
- And case files containing exactly those 100 cases
- When `validate_database()` is called
- Then it should report 0 discrepancies
- And return exit code 0
- Validates: Perfect match scenario works correctly

**Test: `test_validate_database_missing_from_db()`**
- Given a database with 80 cases
- And case files containing 100 cases
- When `validate_database()` is called
- Then it should report 20 cases missing from database
- And return exit code 1
- Validates: Detects cases in files but not in database

**Test: `test_validate_database_extra_in_db()`**
- Given a database with 120 cases
- And case files containing 100 cases
- When `validate_database()` is called
- Then it should report 20 extra cases in database
- And return exit code 1
- Validates: Detects cases in database but not in files

**Test: `test_validate_database_both_discrepancies()`**
- Given a database with some cases not in files
- And files with some cases not in database
- When `validate_database()` is called
- Then it should report both types of discrepancies
- And return exit code 1
- Validates: Reports multiple discrepancy types

**Test: `test_validate_database_empty_collection()`**
- Given an empty ChromaDB collection
- And case files containing 100 cases
- When `validate_database()` is called
- Then it should report 100 cases missing from database
- And return exit code 1
- Validates: Empty database validation works correctly

### Integration Tests

#### **Initial Database Population**

**Test: `test_initial_load_with_content_ids()`**
- Given an empty database
- And 100 test cases
- When `setup_vectordb.py` is run
- Then all 100 cases should be added with content-based IDs
- And IDs should follow format `case_[a-f0-9]{16}`
- And database count should be 100
- Validates: Initial load with new ID system works correctly

**Test: `test_initial_load_filtered_cases()`**
- Given an empty database
- And 100 test cases across multiple categories
- When `setup_vectordb.py --category firebase` is run
- Then only firebase cases should be added with content-based IDs
- And database count should match filtered count
- Validates: Filtered initial load works with new ID system

#### **Incremental Update Scenarios**

**Test: `test_load_same_cases_twice_no_duplicates()`**
- Given an empty database
- When `setup_vectordb.py` is run with 100 cases
- And then run again with the same 100 cases
- Then database should still contain exactly 100 cases (no duplicates)
- And second run should report "Skipped 100 existing cases, added 0 new cases"
- Validates: Loading same cases twice doesn't create duplicates

**Test: `test_load_subset_then_full_set()`**
- Given an empty database
- When `setup_vectordb.py --category firebase` is run (50 cases)
- And then `setup_vectordb.py` is run with all cases (150 cases)
- Then database should contain 150 cases
- And second run should report "Skipped 50 existing cases, added 100 new cases"
- Validates: Incremental loading adds only new cases

**Test: `test_load_full_set_then_subset_no_deletion()`**
- Given a database with 150 cases (full set)
- When `setup_vectordb.py --category firebase` is run (50 cases)
- Then database should still contain all 150 cases
- And run should report "Skipped 50 existing cases, added 0 new cases"
- Validates: Loading subset doesn't delete non-subset cases (regression test for old bug)

**Test: `test_load_disjoint_sets_accumulate()`**
- Given an empty database
- When `setup_vectordb.py --category firebase` is run (50 cases)
- And then `setup_vectordb.py --category rust` is run (40 cases)
- Then database should contain 90 cases
- And second run should report "Skipped 0 existing cases, added 40 new cases"
- Validates: Disjoint case sets accumulate correctly

**Test: `test_load_overlapping_sets()`**
- Given a database with 100 cases
- When `setup_vectordb.py` is run with 150 cases (50 new, 100 overlap)
- Then database should contain 150 cases
- And run should report "Skipped 100 existing cases, added 50 new cases"
- Validates: Overlapping case sets are handled correctly

#### **Force Rebuild**

**Test: `test_force_rebuild_recreates_database()`**
- Given a database with 100 cases
- When `setup_vectordb.py --force` is run with 100 cases
- Then database should be cleared and rebuilt
- And should report "Force rebuild requested. Clearing existing 100 cases..."
- And database should contain 100 cases with new embeddings
- Validates: Force rebuild clears and recreates database

**Test: `test_force_rebuild_with_different_cases()`**
- Given a database with 100 cases
- When `setup_vectordb.py --force` is run with 80 different cases
- Then database should contain exactly 80 cases (old ones removed)
- And all cases should have content-based IDs
- Validates: Force rebuild replaces old cases with new selection

#### **Validation Mode**

**Test: `test_validation_mode_perfect_match()`**
- Given a database with 100 cases matching case files
- When `setup_vectordb.py --validate` is run
- Then output should show "Database is in perfect sync with case files"
- And exit code should be 0
- And database should not be modified
- Validates: Validation mode detects perfect match

**Test: `test_validation_mode_missing_cases()`**
- Given a database with 80 cases
- And case files with 100 cases
- When `setup_vectordb.py --validate` is run
- Then output should show 20 cases missing from database
- And exit code should be 1
- And database should not be modified
- Validates: Validation mode detects missing cases

**Test: `test_validation_mode_extra_cases()`**
- Given a database with 120 cases
- And case files with 100 cases
- When `setup_vectordb.py --validate` is run
- Then output should show 20 extra cases in database
- And exit code should be 1
- And database should not be modified
- Validates: Validation mode detects extra cases

**Test: `test_validation_mode_no_database()`**
- Given no existing ChromaDB database
- When `setup_vectordb.py --validate` is run
- Then output should show "ERROR: Database collection not found"
- And exit code should be 1
- Validates: Validation handles missing database gracefully

#### **Error Handling**

**Test: `test_chromadb_connection_failure()`**
- Given ChromaDB path is inaccessible
- When `setup_vectordb.py` is run
- Then error message should indicate connection failure
- And exit code should be 1
- Validates: ChromaDB connection errors are handled gracefully

**Test: `test_embedding_generation_failure()`**
- Given embedding model fails to initialize or encode
- When `setup_vectordb.py` is run
- Then error message should indicate embedding failure
- And exit code should be 1
- Validates: Embedding errors are handled gracefully

**Test: `test_empty_case_set_after_filtering()`**
- Given case files with 100 cases
- When `setup_vectordb.py --category nonexistent` is run
- Then warning should show "No cases match the specified filters"
- And exit code should be 1
- And database should not be modified
- Validates: Empty filter results are handled (already implemented, verify still works)

#### **Backward Compatibility**

**Test: `test_migration_from_sequential_ids()`**
- Given a database with old sequential IDs (`id0`, `id1`, etc.)
- And 100 cases to load
- When `setup_vectordb.py --force` is run
- Then old database should be deleted
- And new database should be created with content-based IDs
- And all 100 cases should be present
- Validates: Migration from old ID system works via force rebuild

**Test: `test_existing_command_line_args_still_work()`**
- Given all existing command-line arguments
- When each is used: `--category`, `--subcategory`, `--tags`, `--modules`, `--list-categories`, `--list-subcategories`, `--force`
- Then all should work as before
- Validates: No breaking changes to CLI interface

#### **Edge Cases and Regression Tests**

**Test: `test_mock_data_matches_production_structure()`**
- Given mock test cases for testing
- When cases have category='test' instead of valid categories
- Then category-based filtering tests will fail
- Validates: Mock data must use real category structure (code, orchestration, best-practice, anti-pattern)

**Regression Test: `test_deduplication_in_src_version()`**
- Given the `src/cbr_retrieval_mcp/setup_vectordb.py` version
- When loading cases with same content twice
- Then deduplication logic should prevent duplicates
- Validates: Bug fix where src version was missing deduplication logic

**Regression Test: `test_none_value_logging_handling()`**
- Given a case with None values in metadata fields
- When logging case information during load
- Then logging should handle None gracefully without errors
- Validates: Bug fix for "argument of type 'NoneType' is not iterable" error

**Regression Test: `test_category_subcategory_in_hash()`**
- Given two cases with same problem/solution but different categories
- When generating case IDs
- Then IDs should be different (category/subcategory included in hash)
- Validates: Bug fix preventing duplicate IDs for same content in different categories

**Regression Test: `test_load_test_mock_isolation()`**
- Given performance load tests with mocked data
- When other tests run in parallel
- Then load test mocks should not affect other test results
- Validates: Proper mock isolation in pytest-xdist environment

#### **Test Isolation and Parallel Execution**

**Test: `test_parallel_execution_isolation()`**
- Given pytest-xdist running tests in parallel workers
- When multiple workers access the same ChromaDB collection
- Then each worker should use a unique collection name (UUID-based)
- And tests should not interfere with each other
- Validates: Parallel execution works without worker conflicts

**Issue Found: Session-Scoped Fixture Contamination**
- Problem: Session-scoped mock fixtures shared across pytest-xdist workers
- Symptom: Mock configuration from one test affecting unrelated tests in different workers
- Solution: Use function-scoped fixtures with UUID-based unique names for ChromaDB collections

**Issue Found: Collection Name Conflicts**
- Problem: All tests using same "test_collection" name caused worker conflicts
- Symptom: `chromadb.errors.UniqueConstraintError` when workers tried to create same collection
- Solution: Generate unique collection names using UUID: `f"test_collection_{uuid.uuid4().hex}"`

### Mocking Requirements

#### **ChromaDB Mocking**

**For Unit Tests:**
- Mock `chromadb.PersistentClient` to avoid needing actual database
- Mock `collection.get()` to return predefined IDs for deduplication tests
- Mock `collection.add()` to verify correct parameters passed
- Mock `collection.count()` to return predefined counts
- Mock `collection.delete()` and `collection.create()` for force rebuild tests

**Example Mock Setup:**
```python
from unittest.mock import Mock, patch

@patch('chromadb.PersistentClient')
def test_identify_new_cases_all_new(mock_client):
    # Setup mock
    mock_collection = Mock()
    mock_collection.get.return_value = {'ids': []}
    mock_client.return_value.get_or_create_collection.return_value = mock_collection

    # Test logic here
```

#### **Embedding Model Mocking**

**For Integration Tests:**
- Mock `SentenceTransformer` to avoid downloading model
- Mock `.encode()` to return fake embeddings (random vectors of correct dimension)
- Speeds up tests significantly (embedding generation is slow)

**Example Mock Setup:**
```python
import numpy as np
from unittest.mock import Mock, patch

@patch('sentence_transformers.SentenceTransformer')
def test_initial_load_with_content_ids(mock_transformer):
    # Setup mock
    mock_model = Mock()
    mock_model.encode.return_value = np.random.rand(100, 768)  # Fake 768-dim embeddings
    mock_transformer.return_value = mock_model

    # Test logic here
```

#### **File System Mocking**

**For Error Handling Tests:**
- Mock file system access to simulate inaccessible database paths
- Mock `Path` operations for permission errors

**Example Mock Setup:**
```python
from unittest.mock import patch

@patch('pathlib.Path.exists')
@patch('pathlib.Path.is_dir')
def test_chromadb_connection_failure(mock_is_dir, mock_exists):
    # Simulate inaccessible path
    mock_exists.return_value = False

    # Test logic here
```

#### **Parallel Execution Mocking**

**For Pytest-xdist Compatibility:**
- Use function-scoped fixtures instead of session-scoped for mutable state
- Generate unique collection names using UUID to prevent worker conflicts
- Isolate mock configurations to prevent cross-worker contamination

**Example Mock Setup:**
```python
import uuid
from unittest.mock import Mock, patch

@pytest.fixture
def unique_collection():
    """Create unique collection name for parallel test isolation."""
    return f"test_collection_{uuid.uuid4().hex}"

@patch('chromadb.PersistentClient')
def test_with_unique_collection(mock_client, unique_collection):
    mock_collection = Mock()
    mock_collection.name = unique_collection
    mock_client.return_value.get_or_create_collection.return_value = mock_collection

    # Test uses unique collection name to avoid worker conflicts
```

## Test Organization

### Test File Structure

```
tests/
  unit/
    test_case_id_generation.py
      - All `generate_case_id()` tests
    test_deduplication_logic.py
      - All `identify_new_cases()` tests
    test_validation_logic.py
      - All `validate_database()` tests

  integration/
    test_database_population.py
      - Initial load tests
    test_incremental_updates.py
      - All incremental update scenarios
    test_force_rebuild.py
      - Force rebuild tests
    test_validation_mode.py
      - Validation mode tests
    test_error_handling.py
      - Error scenario tests
    test_backward_compatibility.py
      - Migration and compatibility tests
```

### Test Data Requirements

**Fixture: `sample_cases`**
- 150 test cases across 3 categories (firebase: 50, rust: 40, nextjs: 60)
- Each case has problem, solution, category, subcategory, tags
- Deterministic (same cases for all tests)

**Fixture: `temp_chromadb`**
- Temporary ChromaDB instance for integration tests
- Created in temp directory
- Cleaned up after each test

**Fixture: `mock_embedding_model`**
- Returns consistent fake embeddings
- 768 dimensions (matches nomic-ai model)
- Speeds up integration tests

## Coverage Goals

- **Unit Tests:** 100% coverage of new functions
  - `generate_case_id()`
  - `identify_new_cases()`
  - `validate_database()`

- **Integration Tests:** All user workflows covered
  - Initial load
  - Incremental updates
  - Force rebuild
  - Validation mode
  - Error scenarios

- **Regression Tests:** Old bugs don't reappear
  - Loading subset doesn't delete full set
  - Loading same cases twice doesn't create duplicates

## Lessons Learned

### Test Isolation in Parallel Execution

**Critical Finding:** Session-scoped fixtures in pytest-xdist can cause cross-worker contamination.

- **Problem:** Shared mock state across workers led to unpredictable test failures
- **Solution:** Use function-scoped fixtures with unique identifiers (UUIDs)
- **Impact:** Eliminated 100% of parallel execution test failures

**Key Takeaways:**
- Session-scoped fixtures are dangerous for mutable state in parallel execution
- Each pytest-xdist worker is a separate process with separate memory space
- Function-scoped fixtures ensure each test gets clean state

### Proper Fixture Scoping for pytest-xdist

**Understanding Worker Isolation:**

pytest-xdist workers are separate processes, not threads. This has important implications:

- **Session scope:** Dangerous for mutable state, can cause worker conflicts
- **Function scope:** Safe for parallel execution, each test gets clean state
- **Best practice:** Use UUID-based unique names for database collections in tests

**Implementation Pattern:**
```python
import uuid
import pytest

@pytest.fixture
def unique_db_collection():
    """Generate unique collection name for test isolation."""
    return f"test_collection_{uuid.uuid4().hex}"
```

### UUID-Based Unique Collection Names

**Problem Solved:** ChromaDB collection name conflicts between parallel workers

**Original Approach (Broken):**
```python
# All workers tried to create same collection
collection = client.get_or_create_collection("test_collection")
# Result: UniqueConstraintError from ChromaDB
```

**Fixed Approach:**
```python
import uuid

# Each worker gets unique collection
collection_name = f"test_collection_{uuid.uuid4().hex}"
collection = client.get_or_create_collection(collection_name)
# Result: No conflicts, parallel execution works
```

**Benefits:**
- Eliminates collection name conflicts between workers
- Allows true parallel test execution
- Prevents `chromadb.errors.UniqueConstraintError`
- Improves test suite performance (parallel execution faster)

### Mock Data Must Match Production Structure

**Lesson:** Test mocks with invalid data structures lead to false test passes.

**Issue Found:**
- Mock test cases used `category='test'` instead of real categories
- Category-based filtering tests passed in isolation
- Failed when run against production database structure

**Solution:**
```python
# Bad: Invalid category
mock_case = {
    "problem": "Test problem",
    "solution": "Test solution",
    "category": "test"  # Not a valid category!
}

# Good: Production-valid category
mock_case = {
    "problem": "Test problem",
    "solution": "Test solution",
    "category": "code",  # Valid category
    "subcategory": "firebase-auth"  # Valid subcategory
}
```

**Validation Added:**
- Assert mock data structure matches production schema
- Use production-valid categories: code, orchestration, best-practice, anti-pattern
- Include subcategory and tags in mock data

### Testing Both Source Code Versions

**Realization:** The project has two versions of setup_vectordb.py:

1. `scripts/utilities/setup_vectordb.py` (original)
2. `src/cbr_retrieval_mcp/setup_vectordb.py` (packaged version)

**Bug Found:**
- Deduplication logic existed in `scripts/` version
- Same logic was missing from `src/` version
- Tests only covered one version initially

**Best Practice Established:**
- Test both versions to ensure feature parity
- Use parametrized tests to run same tests against both versions
- Add CI checks to verify both versions stay in sync

**Implementation:**
```python
import pytest

@pytest.mark.parametrize("module_path", [
    "scripts.utilities.setup_vectordb",
    "src.cbr_retrieval_mcp.setup_vectordb"
])
def test_deduplication_in_both_versions(module_path):
    # Test runs against both versions
    module = importlib.import_module(module_path)
    # Test logic here
```

### None Value Handling in Logging

**Bug Found:** Logging code failed when case metadata contained None values

**Error:**
```
TypeError: argument of type 'NoneType' is not iterable
```

**Root Cause:**
```python
# Broken code
if 'firebase' in case.get('category'):  # Fails if category is None
    print("Firebase case found")
```

**Fix:**
```python
# Fixed code
category = case.get('category', '')
if category and 'firebase' in category:
    print("Firebase case found")
```

**Lesson:** Always handle None values in optional metadata fields

### Performance Testing Mock Isolation

**Issue:** Load tests with high case counts contaminated other parallel tests

**Problem:**
- Performance tests created 10,000+ mock cases
- Mock configuration leaked to other tests via session-scoped fixtures
- Other tests unexpectedly received 10,000 cases instead of 100

**Solution:**
- Use function-scoped fixtures for all mock data
- Ensure performance tests run in isolated collection (UUID-based name)
- Add cleanup logic to remove large mock datasets after tests

**Performance Test Pattern:**
```python
import uuid

@pytest.fixture
def perf_test_collection():
    """Isolated collection for performance testing."""
    collection_name = f"perf_test_{uuid.uuid4().hex}"
    # Create collection with large dataset
    yield collection_name
    # Cleanup: delete collection after test
```

## Test Execution

### Running Tests

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with coverage report
pytest --cov=scripts/utilities --cov-report=html tests/

# Run specific test file
pytest tests/unit/test_case_id_generation.py

# Run specific test
pytest tests/unit/test_case_id_generation.py::test_generate_case_id_deterministic
```

### Expected Coverage

- Minimum: 90% code coverage for modified functions
- Goal: 95%+ code coverage for all new/modified code
- 100% coverage for critical deduplication logic
