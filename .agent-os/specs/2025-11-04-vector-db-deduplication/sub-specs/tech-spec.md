# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-11-04-vector-db-deduplication/spec.md

> Created: 2025-11-04
> Version: 1.0.0

## Technical Architecture

### Content-Based ID Generation

**Hashing Algorithm:**
- Use SHA-256 for deterministic, collision-resistant hashing
- Input: Concatenation of `case["problem"]` + `case["solution"]`
- Output format: `case_<first_16_chars_of_hash>` (e.g., `case_a7f3b2c1d4e5f6g7`)

**Rationale:**
- SHA-256 provides 256-bit hash space (~10^77 possibilities), making collisions astronomically unlikely
- First 16 characters (64 bits) provide sufficient uniqueness for practical case bases (collision probability ~10^-19 for 1 million cases)
- Deterministic: same content always generates same ID regardless of load order
- Content-based: different content always generates different ID

**Implementation Location:**
- New function `generate_case_id(case: dict) -> str` in setup_vectordb.py
- Called for each case before adding to database

**Example:**
```python
import hashlib

def generate_case_id(case: dict) -> str:
    """Generate a stable, content-based ID for a case.

    Args:
        case: Dictionary with 'problem' and 'solution' keys

    Returns:
        Stable ID string in format 'case_<hash_prefix>'
    """
    # Concatenate problem and solution for content hash
    content = case["problem"] + case["solution"]

    # Generate SHA-256 hash
    hash_object = hashlib.sha256(content.encode('utf-8'))
    hash_hex = hash_object.hexdigest()

    # Use first 16 characters for ID
    return f"case_{hash_hex[:16]}"
```

### Deduplication Logic

**Strategy:**
1. Before adding cases, retrieve all existing IDs from ChromaDB collection
2. Generate content-based IDs for all cases to be loaded
3. Separate cases into two sets:
   - `new_cases`: IDs not present in database
   - `existing_cases`: IDs already in database
4. Add only `new_cases` to the database

**ChromaDB API Usage:**
- Use `collection.get(ids=None, limit=None)` to retrieve all existing IDs
- This is efficient as we only fetch IDs, not embeddings or documents
- Compare sets using Python set operations for O(n) performance

**Implementation Location:**
- New function `identify_new_cases(cases: list, collection) -> tuple[list, list]`
- Returns `(new_cases, existing_cases)` tuple

**Example:**
```python
def identify_new_cases(cases: list, collection) -> tuple[list, list]:
    """Identify which cases are new vs already in database.

    Args:
        cases: List of case dictionaries to check
        collection: ChromaDB collection object

    Returns:
        Tuple of (new_cases, existing_cases) lists
    """
    # Get all existing IDs from database
    try:
        existing_data = collection.get(limit=None)
        existing_ids = set(existing_data['ids']) if existing_data['ids'] else set()
    except Exception:
        # If collection is empty or error occurs, assume no existing cases
        existing_ids = set()

    # Generate IDs for all cases
    case_ids = [(generate_case_id(case), case) for case in cases]

    # Separate new from existing
    new_cases = [case for case_id, case in case_ids if case_id not in existing_ids]
    existing_cases = [case for case_id, case in case_ids if case_id in existing_ids]

    return new_cases, existing_cases
```

### Incremental Update Mode

**Approach:**
- Replace "delete and rebuild" logic with "add only new cases" logic
- Remove the `current_count < len(CASE_BASE)` deletion branch (lines 288-315)
- Use ChromaDB's `.add()` method with only new case IDs (no duplicates, so no error)

**Modified Main Logic Flow:**
```
1. Load cases and apply filters
2. Check collection count
3. If count == 0 or --force flag:
   - If --force and count > 0: delete collection
   - Create collection
   - Generate embeddings for all cases
   - Add all cases
4. Else (collection has cases):
   - Identify new vs existing cases
   - If new_cases exist:
     - Generate embeddings only for new cases
     - Add only new cases
   - Report: "Added X new cases, skipped Y existing cases, total Z"
```

**ChromaDB Upsert Consideration:**
- ChromaDB supports `.upsert()` method for "insert or update"
- However, we don't want to update existing cases (embeddings are expensive to regenerate)
- Therefore, use `.add()` with only new cases instead of `.upsert()`
- This avoids re-embedding existing cases and preserves database state

### Validation Mode

**Implementation:**
- New `--validate` command-line argument
- Mutually exclusive with loading operations (exits after validation)
- Compares case file contents with database contents

**Validation Logic:**
```
1. Load all cases from files
2. Generate content IDs for all file cases
3. Retrieve all IDs from database
4. Compare sets:
   - in_files_not_db = file_ids - db_ids
   - in_db_not_files = db_ids - file_ids
   - in_both = file_ids & db_ids
5. Report statistics and discrepancies
6. Exit with code 0 if perfect match, code 1 if discrepancies found
```

**New Function:**
```python
def validate_database(cases: list, collection):
    """Validate database contents against case files.

    Args:
        cases: List of case dictionaries from files
        collection: ChromaDB collection object

    Returns:
        Exit code (0 = valid, 1 = discrepancies found)
    """
    # Generate IDs for file cases
    file_ids = {generate_case_id(case) for case in cases}

    # Get IDs from database
    existing_data = collection.get(limit=None)
    db_ids = set(existing_data['ids']) if existing_data['ids'] else set()

    # Compare sets
    in_files_not_db = file_ids - db_ids
    in_db_not_files = db_ids - file_ids
    matches = file_ids & db_ids

    # Report
    print("\n=== Database Validation Report ===")
    print(f"Cases in files: {len(file_ids)}")
    print(f"Cases in database: {len(db_ids)}")
    print(f"Matching cases: {len(matches)}")

    if in_files_not_db:
        print(f"\n⚠ Missing from database: {len(in_files_not_db)}")
        for case_id in sorted(in_files_not_db)[:10]:  # Show first 10
            print(f"  - {case_id}")
        if len(in_files_not_db) > 10:
            print(f"  ... and {len(in_files_not_db) - 10} more")

    if in_db_not_files:
        print(f"\n⚠ Extra in database (not in files): {len(in_db_not_files)}")
        for case_id in sorted(in_db_not_files)[:10]:
            print(f"  - {case_id}")
        if len(in_db_not_files) > 10:
            print(f"  ... and {len(in_db_not_files) - 10} more")

    if not in_files_not_db and not in_db_not_files:
        print("\n✓ Database is in perfect sync with case files")
        return 0
    else:
        print("\n✗ Database has discrepancies")
        return 1
```

## User Flow Logic

### Standard Loading Flow

```
User runs: python setup_vectordb.py [--category X] [--tags Y]

1. Parse arguments and load all cases
2. Apply filters to get CASE_BASE
3. Initialize embedding model
4. Connect to ChromaDB
5. Get or create collection

6. Check collection count:

   If count == 0:
     → "Populating the vector database..."
     → Generate embeddings for all cases
     → Add all cases with content-based IDs
     → "Successfully added N cases to the database"

   Else if --force flag:
     → "Force rebuild requested. Clearing existing cases..."
     → Delete and recreate collection
     → Generate embeddings for all cases
     → Add all cases
     → "Successfully added N cases to the database"

   Else (count > 0):
     → "Checking for new cases..."
     → Identify new vs existing cases

     If new_cases exist:
       → "Found X new cases to add..."
       → Generate embeddings only for new cases
       → Add only new cases
       → "Successfully added X new cases. Skipped Y existing cases. Total: Z cases"

     Else:
       → "All cases already in database. No updates needed."
       → "Total: N cases"
```

### Validation Flow

```
User runs: python setup_vectordb.py --validate

1. Parse arguments and load all cases
2. Connect to ChromaDB
3. Get collection (must exist)

4. If collection doesn't exist:
   → "Error: Database not found. Run setup first."
   → Exit with code 1

5. Run validation:
   → Generate IDs for file cases
   → Retrieve IDs from database
   → Compare and report discrepancies
   → Exit with code 0 (perfect match) or 1 (discrepancies)
```

## Error Handling

### Hash Collision Handling

**Scenario:** Two different cases generate the same content hash (extremely unlikely)

**Detection:** When adding cases, ChromaDB would return an error if duplicate ID exists

**Mitigation:**
```python
try:
    collection.add(
        embeddings=embeddings,
        documents=solutions,
        metadatas=metadatas,
        ids=ids
    )
except Exception as e:
    if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
        print(f"ERROR: Duplicate ID detected. This may indicate a hash collision.")
        print(f"This is extremely rare. Please report this issue.")
        sys.exit(1)
    else:
        raise
```

### Empty Collection After Filtering

**Scenario:** User filters result in zero cases

**Current Handling:** Already handled at line 238-241

**No changes needed** - existing logic is correct

### ChromaDB Connection Errors

**Scenario:** Database path is inaccessible or ChromaDB fails to initialize

**Current Handling:** No explicit handling

**Enhancement:**
```python
try:
    client = chromadb.PersistentClient(path="./db")
except Exception as e:
    print(f"ERROR: Failed to connect to ChromaDB: {e}")
    print("Ensure the database path is accessible and ChromaDB is properly installed.")
    sys.exit(1)
```

### Embedding Generation Failures

**Scenario:** Embedding model fails to encode cases

**Current Handling:** No explicit handling

**Enhancement:**
```python
try:
    problem_embeddings = embedding_model.encode(problems, normalize_embeddings=True)
except Exception as e:
    print(f"ERROR: Failed to generate embeddings: {e}")
    print("Check that the embedding model is properly loaded.")
    sys.exit(1)
```

### Validation Mode Errors

**Scenario:** Collection doesn't exist when running `--validate`

**Handling:**
```python
try:
    collection = client.get_collection(name="code_solutions_case_base")
except Exception:
    print("ERROR: Database collection not found.")
    print("Run setup_vectordb.py without --validate first to create the database.")
    sys.exit(1)
```

## Performance Considerations

### ID Generation Performance

- SHA-256 hashing: ~1 microsecond per case on modern hardware
- For 10,000 cases: ~10ms total hashing time
- Negligible compared to embedding generation (seconds to minutes)

### Deduplication Performance

- Retrieving existing IDs: O(n) where n = number of cases in database
- Set comparison: O(n) where n = number of cases to load
- Total overhead: <100ms for typical case bases (1,000-10,000 cases)
- Significantly faster than re-embedding (which takes seconds per case)

### Memory Considerations

- Storing all IDs in memory: ~100 bytes per ID
- 10,000 cases: ~1MB memory for ID sets
- Acceptable overhead for any modern system

## Backward Compatibility

### Existing Databases

**Issue:** Existing databases use sequential IDs (`id0`, `id1`, etc.)

**Solution:** Force rebuild on first run with new version

**Recommendation:**
- Document in migration notes that `--force` is required for existing databases
- Old IDs and new IDs won't match, so incremental updates won't work
- After `--force` rebuild, all future updates will work incrementally

**Migration Command:**
```bash
python setup_vectordb.py --force
```

### Script Interface

**No breaking changes:**
- All existing command-line arguments remain unchanged
- New `--validate` flag is additive
- Default behavior changes but produces same end result (all cases in database)
- Only difference: second run won't rebuild unnecessarily
