# Data Specification

This is the data specification for the spec detailed in @.agent-os/specs/2025-11-04-metadata-storage-bug-fix/spec.md

> Created: 2025-11-04
> Version: 1.0.0

## Data Models

### Case Dictionary Schema (Python - Already Correct)

**Source:** `cases/__init__.py` - loaded by `load_all_cases()`

```python
{
    "problem": str,      # Required - Problem description/user request
    "solution": str,     # Required - Code solution/example
    "category": str,     # Required - Top-level category (orchestration, firebase, rust, etc.)
    "subcategory": str,  # Required - Specific subcategory (planning, auth, components, etc.)
    "tags": List[str]    # Required - List of searchable tags
}
```

**Example:**
```python
{
    "problem": "User: 'I need to add Google Sign-In to our application.'",
    "solution": "<tool_code>...</tool_code>",
    "category": "orchestration",
    "subcategory": "planning",
    "tags": ["orchestration", "planning", "delegation", "tdd", "ui", "backend"]
}
```

**Validation:**
- All fields are required in case files
- Category must be one of valid categories (orchestration, firebase, rust, nextjs, react, etc.)
- Subcategory must be valid for the category
- Tags must be a list of strings

### ChromaDB Metadata Schema (Storage - Needs Fixing)

**Current Broken Schema:**
```python
{
    "problem": str  # Only field stored
}
```

**Fixed Schema:**
```python
{
    "problem": str,      # Problem description (backward compatible)
    "category": str,     # Category for filtering
    "subcategory": str,  # Subcategory for filtering
    "tags": str          # Comma-separated tags (ChromaDB doesn't support list type)
}
```

**Example ChromaDB Metadata:**
```python
{
    "problem": "User: 'I need to add Google Sign-In to our application.'",
    "category": "orchestration",
    "subcategory": "planning",
    "tags": "orchestration,planning,delegation,tdd,ui,backend"
}
```

**ChromaDB Storage Constraints:**
- Metadata values must be: string, number, or boolean
- Lists are NOT supported → convert tags list to comma-separated string
- Field names are case-sensitive
- Null values not allowed → use defaults for missing fields

### ChromaDB Collection Schema

**Collection Name:** `code_solutions_case_base`

**Collection Structure:**
```python
collection = {
    "name": "code_solutions_case_base",
    "metadata": {},  # No collection-level metadata
    "documents": [
        # List of solution code strings (one per case)
    ],
    "embeddings": [
        # List of 768-dimensional vectors (nomic-ai embeddings)
    ],
    "metadatas": [
        # List of metadata dictionaries (one per case)
        # FIXED: Now includes category, subcategory, tags
    ],
    "ids": [
        # List of string IDs: "id0", "id1", ..., "id102"
    ]
}
```

**Current Collection State (Broken):**
- Count: 103 cases
- Documents: 103 solution code strings ✓
- Embeddings: 103 vectors ✓
- Metadatas: 103 dictionaries with ONLY "problem" field ❌
- IDs: 103 IDs ("id0" to "id102") ✓

**Fixed Collection State:**
- Count: 103 cases
- Documents: 103 solution code strings ✓
- Embeddings: 103 vectors ✓
- Metadatas: 103 dictionaries with ALL fields (problem, category, subcategory, tags) ✓
- IDs: 103 IDs ("id0" to "id102") ✓

## Database Migration Strategy

### Migration Approach: Force Rebuild

**Method:** Use `--force` flag to delete and recreate collection

**Why Not In-Place Update:**
1. ChromaDB doesn't support updating metadata for existing documents
2. Must delete collection and recreate to change metadata schema
3. Force rebuild is safe because source data (case files) is authoritative
4. Embeddings can be regenerated from case files

**Migration Command:**
```bash
python scripts/utilities/setup_vectordb.py --force
```

**Migration Process:**
1. **Detect existing data**: `current_count = collection.count()` → 103
2. **User provides --force**: `args.force = True`
3. **Delete collection**: `client.delete_collection(name="code_solutions_case_base")`
4. **Recreate empty collection**: `collection = client.create_collection(name="code_solutions_case_base")`
5. **Load cases**: `CASE_BASE = load_all_cases()` → 103 cases with full metadata
6. **Extract data**:
   - `problems = [case["problem"] for case in CASE_BASE]`
   - `solutions = [case["solution"] for case in CASE_BASE]`
7. **Generate embeddings**: `problem_embeddings = embedding_model.encode(problems, ...)`
8. **Build fixed metadata**:
   ```python
   metadatas = [
       {
           "problem": case["problem"],
           "category": case.get("category", "unknown"),
           "subcategory": case.get("subcategory", "unknown"),
           "tags": ",".join(case.get("tags", []))
       }
       for case in CASE_BASE
   ]
   ```
9. **Populate collection**: `collection.add(embeddings=..., documents=..., metadatas=..., ids=...)`
10. **Verify**: `collection.count()` → 103

**Data Loss Prevention:**
- Source data remains in case files (unchanged)
- Embeddings regenerated from source (deterministic)
- No user-generated data lost
- Migration is idempotent (can run multiple times safely)

### Rollback Strategy

**If Migration Fails:**
1. Delete broken collection: `client.delete_collection("code_solutions_case_base")`
2. Revert code changes in `setup_vectordb.py`
3. Run original script: `python scripts/utilities/setup_vectordb.py`
4. Database restored to previous state (with broken metadata, but functional for semantic search)

**If Migration Succeeds But Issues Found:**
1. Keep fixed code
2. Run `--force` again to regenerate from source
3. No data loss possible since source files are authoritative

## Data Validation

### Input Validation (Case Loading)

**Location:** `cases/__init__.py` - `load_cases_from_module()`

**Current Validation:**
- Basic structure validation exists
- Ensures problem and solution fields present

**Additional Validation Needed:**
- Verify category field exists: `assert "category" in case`
- Verify subcategory field exists: `assert "subcategory" in case`
- Verify tags field exists and is list: `assert isinstance(case.get("tags", []), list)`
- Log warning if any validation fails

**Validation Code:**
```python
def validate_case(case: Dict[str, Any], module_path: str) -> bool:
    """Validate case has all required metadata fields."""
    required_fields = ["problem", "solution", "category", "subcategory", "tags"]

    for field in required_fields:
        if field not in case:
            logger.warning(
                f"Case missing '{field}' in {module_path}",
                {"case_preview": case.get("problem", "unknown")[:100]}
            )
            return False

    if not isinstance(case["tags"], list):
        logger.warning(
            f"Case 'tags' field is not a list in {module_path}",
            {"case_preview": case.get("problem", "unknown")[:100]}
        )
        return False

    return True
```

### Storage Validation (Database Population)

**Location:** `scripts/utilities/setup_vectordb.py` - before `collection.add()`

**Validation:**
- Verify metadata list length matches cases: `assert len(metadatas) == len(CASE_BASE)`
- Verify each metadata dict has required fields
- Log sample metadata for verification

**Validation Code:**
```python
# Before collection.add()
assert len(metadatas) == len(CASE_BASE), "Metadata count mismatch"
print(f"Sample metadata (first case): {metadatas[0]}")

# Verify all metadata has required fields
required_fields = {"problem", "category", "subcategory", "tags"}
for i, meta in enumerate(metadatas):
    missing = required_fields - set(meta.keys())
    if missing:
        print(f"WARNING: Case {i} metadata missing fields: {missing}")
```

### Query Validation (Retrieval)

**Location:** `src/cbr_mcp_server.py` - `search_by_category()`

**Existing Validation:**
- Category must be in VALID_CATEGORIES
- Subcategory must be in VALID_SUBCATEGORIES for category
- Limit must be 1-1000

**No Changes Needed:** Query validation already correct, just needs database to have proper metadata

## Backward Compatibility

### Existing Query Patterns

**Pattern 1: Problem-Only Queries (Semantic Search)**
```python
# Existing code that only uses problem field
results = collection.query(
    query_embeddings=[embedding],
    n_results=5
)
# Still works - problem field still in metadata
```

**Pattern 2: Metadata Access**
```python
# Existing code reading metadata
for result in results:
    problem = result["metadata"]["problem"]  # Still works
    # NEW: Can now also access:
    # category = result["metadata"]["category"]
    # subcategory = result["metadata"]["subcategory"]
    # tags = result["metadata"]["tags"]
```

**Pattern 3: Category Filtering (Currently Broken, Will Fix)**
```python
# Currently broken, will be fixed by this spec
results = collection.query(
    query_embeddings=[embedding],
    where={"category": "orchestration"},  # Now works!
    n_results=10
)
```

### Schema Evolution

**Phase 1 (Current):** Broken schema with only problem field
```python
{"problem": "..."}
```

**Phase 2 (After Fix):** Complete schema with all fields
```python
{"problem": "...", "category": "...", "subcategory": "...", "tags": "..."}
```

**No Intermediate Phase Needed:** Force rebuild means instant transition from Phase 1 to Phase 2
