# Data Specification

This is the data specification for the spec detailed in @.agent-os/specs/2025-11-04-vector-db-deduplication/spec.md

> Created: 2025-11-04
> Version: 1.0.0

## Overview

This specification documents the data structures and formats used in the vector database deduplication implementation. **Note:** There are no database schema changes or API endpoints for this spec, as it only modifies the internal logic of the setup_vectordb.py utility script.

## Data Models

### Case Dictionary Structure

**Existing Structure (Unchanged):**

```python
case = {
    "problem": str,      # Problem description
    "solution": str,     # Code solution
    "category": str,     # Category (e.g., "firebase", "rust")
    "subcategory": str,  # Subcategory (e.g., "auth", "components")
    "tags": List[str]    # List of tags
}
```

**No changes to case dictionary structure.** The deduplication logic works with existing case format.

### Case ID Format

**New ID Format:**

```
Format: case_<hash_prefix>
Example: case_a7f3b2c1d4e5f6g7

Where:
- Prefix: "case_"
- Hash: First 16 characters of SHA-256 hash of (problem + solution)
- Character set: [a-f0-9] (hexadecimal)
- Total length: 21 characters (5 prefix + 16 hash)
```

**Generation Logic:**

```python
import hashlib

def generate_case_id(case: dict) -> str:
    content = case["problem"] + case["solution"]
    hash_hex = hashlib.sha256(content.encode('utf-8')).hexdigest()
    return f"case_{hash_hex[:16]}"
```

**Properties:**
- **Deterministic:** Same content always generates same ID
- **Unique:** Different content generates different ID (collision probability: ~10^-19)
- **Stable:** ID doesn't change regardless of load order or database state

### ChromaDB Data Structure

**Existing ChromaDB Schema (Unchanged):**

```python
collection.add(
    embeddings=List[List[float]],  # 768-dimensional vectors from nomic-ai model
    documents=List[str],            # Case solutions (code)
    metadatas=List[dict],           # Case problems and metadata
    ids=List[str]                   # Case IDs (NOW CONTENT-BASED)
)
```

**What Changed:**
- Only the ID generation method changes from sequential (`id0`, `id1`...) to content-based (`case_<hash>`)
- Collection structure, embeddings, documents, and metadata format remain identical

**Metadata Structure (Unchanged):**

```python
metadata = {
    "problem": str  # Problem description
}
```

### Deduplication Data Structures

**New Function Return Types:**

```python
def identify_new_cases(cases: List[dict], collection) -> Tuple[List[dict], List[dict]]:
    """
    Returns:
        Tuple of (new_cases, existing_cases)
        - new_cases: List[dict] - Cases not in database
        - existing_cases: List[dict] - Cases already in database
    """
```

**Internal Data Structures:**

```python
# Set of existing IDs in database
existing_ids: Set[str] = {"case_abc123...", "case_def456..."}

# Set of IDs from case files
file_ids: Set[str] = {"case_abc123...", "case_ghi789..."}

# Set operations for comparison
new_ids = file_ids - existing_ids
existing_ids_overlap = file_ids & existing_ids
```

### Validation Report Structure

**Validation Output Format:**

```
=== Database Validation Report ===
Cases in files: <int>
Cases in database: <int>
Matching cases: <int>

[Optional: if discrepancies exist]
⚠ Missing from database: <int>
  - case_<hash1>
  - case_<hash2>
  ... and <N> more

⚠ Extra in database (not in files): <int>
  - case_<hash3>
  - case_<hash4>
  ... and <N> more

[Result line]
✓ Database is in perfect sync with case files
OR
✗ Database has discrepancies
```

**Exit Codes:**
- `0`: Perfect match (all cases in sync)
- `1`: Discrepancies found OR validation errors

## API Endpoints

**Not Applicable:** This spec only modifies the setup_vectordb.py utility script. No API endpoints are created, modified, or removed.

## Database Schema Changes

**Not Applicable:** ChromaDB collection schema remains unchanged. Only the ID generation method changes from sequential to content-based.

**Migration Path:**
- Existing databases with sequential IDs (`id0`, `id1`...) must be rebuilt using `--force` flag
- After rebuild, all IDs will be content-based (`case_<hash>`)
- No automatic migration (requires explicit user action)

## Command-Line Interface

### New Arguments

**`--validate` Flag:**

```bash
python setup_vectordb.py --validate
```

**Purpose:** Validate database integrity without modifying it

**Mutually Exclusive With:** All loading operations (exits after validation)

**Output:** Validation report (see Validation Report Structure above)

**Exit Codes:**
- `0`: Database matches case files perfectly
- `1`: Discrepancies found

### Existing Arguments (Unchanged)

All existing arguments remain functional with no breaking changes:

- `--category`: Filter by categories
- `--subcategory`: Filter by subcategories
- `--tags`: Filter by tags
- `--modules`: Filter by module files (placeholder, not yet implemented)
- `--force`: Force rebuild database
- `--list-categories`: Show available categories
- `--list-subcategories`: Show subcategories for a category

## Configuration

**No Configuration Changes:**
- ChromaDB path: `./db` (unchanged)
- Collection name: `code_solutions_case_base` (unchanged)
- Embedding model: `nomic-ai/nomic-embed-text-v1.5` (unchanged)
- Embedding dimensions: 768 (unchanged)

## Data Integrity Guarantees

### ID Uniqueness Guarantee

**Guarantee:** Content-based IDs ensure the same case content always gets the same ID, preventing duplicate cases in the database.

**Mechanism:**
1. SHA-256 hash provides 256-bit hash space (~10^77 possible values)
2. Using first 64 bits (16 hex characters) still provides ~10^19 possible IDs
3. Collision probability for 1 million cases: ~10^-19 (astronomically unlikely)

**Failure Mode:** If hash collision occurs (extremely rare), ChromaDB will reject duplicate ID and script will exit with error

### Data Consistency Guarantee

**Guarantee:** Incremental updates preserve all existing cases while adding only new ones.

**Mechanism:**
1. Retrieve all existing IDs from database before adding
2. Compare with IDs of cases to be loaded
3. Add only cases whose IDs are not in database
4. Existing cases remain untouched (no updates, no deletions)

**Validation:** `--validate` flag verifies database consistency with case files

### Embedding Consistency Guarantee

**Guarantee:** Each case's embedding is generated exactly once and never regenerated (unless force rebuild is used).

**Mechanism:**
1. Embeddings are only generated for new cases
2. Existing cases are skipped, so their embeddings are preserved
3. `--force` flag is the only way to regenerate embeddings

**Rationale:** Embedding generation is expensive (seconds per case), so preserving existing embeddings improves performance

## Memory and Performance Characteristics

### Memory Usage

**ID Storage:**
- ~21 bytes per ID (string "case_" + 16 hex chars)
- 10,000 cases = ~210 KB for ID storage
- Negligible compared to embeddings (768 floats × 4 bytes × 10,000 = ~30 MB)

**Set Operations:**
- Python sets store IDs in memory for comparison
- 10,000 IDs = ~1 MB memory for set operations
- Acceptable overhead for any modern system

### Performance Characteristics

**ID Generation:**
- SHA-256 hashing: ~1 microsecond per case
- 10,000 cases: ~10 ms total
- Negligible compared to embedding generation (seconds to minutes)

**Deduplication Check:**
- Retrieving existing IDs: O(n) where n = database size
- Set comparison: O(n) where n = cases to load
- 10,000 existing + 1,000 new: ~50-100 ms total
- Much faster than re-embedding (which would take minutes)

## Error Handling Data

### Error Message Format

**ChromaDB Connection Error:**
```
ERROR: Failed to connect to ChromaDB: <error_details>
Ensure the database path is accessible and ChromaDB is properly installed.
```

**Embedding Generation Error:**
```
ERROR: Failed to generate embeddings: <error_details>
Check that the embedding model is properly loaded.
```

**Hash Collision Error (extremely rare):**
```
ERROR: Duplicate ID detected. This may indicate a hash collision.
This is extremely rare. Please report this issue.
```

**Validation Error (no database):**
```
ERROR: Database collection not found.
Run setup_vectordb.py without --validate first to create the database.
```

## Backward Compatibility

### Data Migration

**Old ID Format:** `id0`, `id1`, `id2`, ... (sequential)

**New ID Format:** `case_<hash>` (content-based)

**Migration Required:** Yes, via `--force` flag

**Migration Command:**
```bash
python setup_vectordb.py --force
```

**Migration Process:**
1. Old collection with sequential IDs is deleted
2. New collection is created
3. All cases are re-embedded with content-based IDs
4. After migration, incremental updates work as expected

**No Automatic Migration:** User must explicitly use `--force` flag to migrate existing databases
