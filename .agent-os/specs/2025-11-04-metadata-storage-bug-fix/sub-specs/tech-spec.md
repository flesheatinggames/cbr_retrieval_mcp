# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-11-04-metadata-storage-bug-fix/spec.md

> Created: 2025-11-04
> Version: 1.0.0

## Technical Architecture

### Problem Analysis

**Current Broken Implementation:**

In `scripts/utilities/setup_vectordb.py`, two locations store case data to ChromaDB:

**Line 284** (Initial database population):
```python
collection.add(
    embeddings=problem_embeddings,
    documents=solutions,
    metadatas=[{"problem": p} for p in problems],  # ❌ ONLY stores problem!
    ids=ids
)
```

**Line 312** (Repopulation when count mismatch):
```python
collection.add(
    embeddings=problem_embeddings,
    documents=solutions,
    metadatas=[{"problem": p} for p in problems],  # ❌ ONLY stores problem!
    ids=ids
)
```

**What This Causes:**
- ChromaDB metadata has 103 cases with structure: `{"problem": "User: Add Google Sign-In..."}`
- Missing fields: `category`, `subcategory`, `tags`
- `cbr_search_category` tries to filter: `where={"category": "orchestration"}`
- ChromaDB cannot find field "category" in metadata
- Query fails with error

**Case Data Structure (Already Correct):**

From `cases/__init__.py`, the `load_all_cases()` function returns:
```python
[
    {
        "problem": "User: 'I need to add Google Sign-In'",
        "solution": "<tool_code>...</tool_code>",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": ["orchestration", "planning", "delegation", "tdd"]
    },
    # ... 102 more cases with full metadata
]
```

The `CASE_BASE` variable in `setup_vectordb.py` receives this complete list with all metadata intact.

### Solution Architecture

**Fix: Extract and Store Complete Metadata**

Modify both lines 284 and 312 to extract all metadata fields from each case dictionary:

```python
# OLD (broken):
metadatas=[{"problem": p} for p in problems]

# NEW (fixed):
metadatas=[
    {
        "problem": case["problem"],
        "category": case.get("category", "unknown"),
        "subcategory": case.get("subcategory", "unknown"),
        "tags": ",".join(case.get("tags", []))  # Store as comma-separated string
    }
    for case in CASE_BASE
]
```

**Key Design Decisions:**

1. **Use `case.get()` with defaults**: Handles cases missing optional fields gracefully
2. **Store tags as comma-separated string**: ChromaDB metadata values must be strings, numbers, or booleans (not lists)
3. **Maintain problem field**: Preserves backward compatibility with any code expecting problem in metadata
4. **Extract from CASE_BASE not problems list**: Access full case dictionaries to get all fields

### User Flow Logic

**Step 1: Database Population**

```
User runs: python scripts/utilities/setup_vectordb.py --force

Flow:
1. Load all cases via load_all_cases() → 103 cases with full metadata
2. Filter cases (if filters provided) → CASE_BASE
3. Extract problems list: [case["problem"] for case in CASE_BASE]
4. Extract solutions list: [case["solution"] for case in CASE_BASE]
5. Generate embeddings from problems
6. **NEW**: Build metadata list from CASE_BASE with all fields
7. Store to ChromaDB: embeddings, documents=solutions, metadatas=full_metadata
8. Verify: collection.count() returns 103
```

**Step 2: Category Search**

```
Agent calls: cbr_search_category(category="orchestration")

Flow:
1. MCP tool validates category parameter
2. Calls retriever.search_by_category(category="orchestration")
3. Builds ChromaDB where filter: {"category": "orchestration"}
4. ChromaDB queries collection WHERE category="orchestration"
5. **NOW SUCCEEDS**: Finds 24 cases with category="orchestration" in metadata
6. Returns cases with complete metadata including category, subcategory, tags
7. Agent receives orchestration examples for planning
```

**Step 3: Subcategory Filtering**

```
Agent calls: cbr_search_category(category="orchestration", subcategory="planning")

Flow:
1. MCP tool validates both parameters
2. Builds where filter: {"$and": [{"category": "orchestration"}, {"subcategory": "planning"}]}
3. ChromaDB queries with compound filter
4. Returns only orchestration+planning cases
5. Agent receives highly targeted examples
```

### Error Handling

**Case Missing Category Field:**
```python
"category": case.get("category", "unknown")
```
- Defaults to "unknown" if category field missing
- Prevents KeyError
- Allows database population to complete
- Can identify problematic cases via "unknown" value

**Case Missing Tags Field:**
```python
"tags": ",".join(case.get("tags", []))
```
- Defaults to empty list if tags missing
- join() produces empty string ""
- No error during storage

**Database Migration Failure:**
```python
if force_rebuild and current_count > 0:
    print(f"Force rebuild requested. Clearing existing {current_count} cases...")
    client.delete_collection(name="code_solutions_case_base")
    collection = client.create_collection(name="code_solutions_case_base")
```
- Existing logic handles collection deletion
- Recreates empty collection
- New code populates with fixed metadata
- No special migration logic needed - just use --force flag

**ChromaDB Storage Error:**
- Existing try/except around collection.add() catches storage errors
- Error message indicates failure
- User can investigate and retry

### Backward Compatibility

**Maintains Compatibility:**

1. **Problem field still stored**: Any code expecting `metadata["problem"]` continues to work
2. **Embeddings unchanged**: Still generated from problem text, no change to vector search
3. **Documents unchanged**: Still stores solution code as document
4. **Collection name unchanged**: Still "code_solutions_case_base"
5. **ID format unchanged**: Still "id0", "id1", etc.

**New Capabilities:**

1. Category filtering now works
2. Subcategory filtering now works
3. Tag information available in results
4. Richer metadata for agent decision-making

### Performance Considerations

**Metadata Storage Overhead:**
- Additional fields add ~50-100 bytes per case
- 103 cases × 100 bytes = ~10KB total
- Negligible impact on storage

**Query Performance:**
- ChromaDB indexes metadata fields for filtering
- Category/subcategory filters improve query efficiency (fewer vectors to compare)
- No performance degradation expected

**Migration Time:**
- Deleting and recreating collection: <1 second
- Generating embeddings: 5-10 seconds (unchanged from current)
- Total migration time: <15 seconds
