# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-10-27-cbr-metadata-enhancement/spec.md

> Created: 2025-10-27
> Version: 1.0.0

## ChromaDB Metadata Schema Changes

### Current Metadata Structure

```python
# Existing metadata (varies by case)
metadata = {
    "source": str,           # Source of the case
    "type": str,             # Case type (optional)
    "category": str,         # Flat category (optional, inconsistent)
    # Other fields vary by case
}
```

### Enhanced Metadata Structure

```python
# Enhanced metadata with hierarchical categories and tags
metadata = {
    # NEW REQUIRED FIELDS
    "category": str,         # Top-level category: code|orchestration|best-practice|anti-pattern
    "subcategory": str,      # Second-level category (specific to top-level category)
    "tags": str,             # Comma-separated tags (optional, empty string if none)

    # EXISTING FIELDS (preserved)
    "source": str,           # Maintained for backward compatibility
    "type": str,             # Maintained if present
    # Other existing fields preserved
}
```

### Field Specifications

#### category (Required)

**Type:** String

**Allowed Values:**
- `"code"` - Code examples and implementations
- `"orchestration"` - Agent orchestration flow patterns
- `"best-practice"` - Best practice patterns and guidelines
- `"anti-pattern"` - Common mistakes and corrections

**Validation:**
```python
VALID_CATEGORIES = ["code", "orchestration", "best-practice", "anti-pattern"]
assert metadata["category"] in VALID_CATEGORIES
```

**Default:** `"code"` (applied during migration if undetectable)

#### subcategory (Required)

**Type:** String

**Allowed Values (by category):**

**Code subcategories:**
- `"firebase-auth"`
- `"react-components"`
- `"api-routes"`
- `"database"`
- `"testing"`
- `"general"`

**Orchestration subcategories:**
- `"remediation"`
- `"planning"`
- `"delegation"`
- `"verification"`
- `"completion"`

**Best-Practice subcategories:**
- `"planning"`
- `"verification"`
- `"error-handling"`

**Anti-Pattern subcategories:**
- `"completion-bias"`
- `"verification-skip"`
- `"protocol-violation"`

**Validation:**
```python
VALID_SUBCATEGORIES = {
    "code": ["firebase-auth", "react-components", "api-routes", "database", "testing", "general"],
    "orchestration": ["remediation", "planning", "delegation", "verification", "completion"],
    "best-practice": ["planning", "verification", "error-handling"],
    "anti-pattern": ["completion-bias", "verification-skip", "protocol-violation"]
}

assert metadata["subcategory"] in VALID_SUBCATEGORIES[metadata["category"]]
```

**Default:** `"general"` (for code category) or first subcategory for other categories

#### tags (Optional)

**Type:** String (comma-separated values)

**Format:** Lowercase, comma-separated, no spaces
- Valid: `"react,firebase,typescript,authentication"`
- Invalid: `"React, Firebase"` (capitals and spaces)

**Examples:**
- `"react,firebase,typescript,authentication"`
- `"python,api,database"`
- `"orchestration,remediation,karen"`
- `""` (empty string for no tags)

**Validation:**
```python
if metadata.get("tags"):
    assert "," in metadata["tags"] or metadata["tags"].isalpha()
    assert metadata["tags"] == metadata["tags"].lower()
    assert "  " not in metadata["tags"]  # No double spaces
```

**Default:** `""` (empty string)

## Migration Schema

### Migration Tracking

**No separate migration table needed** - ChromaDB metadata updated in place

### Migration Process

1. **Read all documents** from collection:
   ```python
   results = collection.get(include=["documents", "metadatas", "ids"])
   ```

2. **For each document**, detect and add new fields:
   ```python
   for i, doc_id in enumerate(results["ids"]):
       metadata = results["metadatas"][i]
       document_text = results["documents"][i]

       # Detect category/subcategory
       category, subcategory = detect_category_subcategory(document_text)

       # Extract tags
       tags = extract_tags(document_text, metadata)

       # Update metadata
       metadata["category"] = category
       metadata["subcategory"] = subcategory
       metadata["tags"] = tags

       # Update in ChromaDB (preserves embeddings)
       collection.update(
           ids=[doc_id],
           metadatas=[metadata]
       )
   ```

3. **Validation** - Verify all documents have required fields:
   ```python
   validation_results = collection.get(include=["metadatas"])
   for metadata in validation_results["metadatas"]:
       assert "category" in metadata
       assert "subcategory" in metadata
       assert "tags" in metadata  # May be empty string
   ```

## ChromaDB Query Changes

### Current Query Pattern

```python
# Current: No metadata filtering
results = collection.query(
    query_embeddings=[embedding],
    n_results=limit
)
```

### Enhanced Query Pattern with Filtering

```python
# Category filter only
results = collection.query(
    query_embeddings=[embedding],
    where={"category": "orchestration"},
    n_results=limit
)

# Category + subcategory filter
results = collection.query(
    query_embeddings=[embedding],
    where={
        "category": "code",
        "subcategory": "firebase-auth"
    },
    n_results=limit
)

# Get all cases in category (no semantic search)
results = collection.get(
    where={"category": "orchestration"},
    limit=limit
)
```

### Tag Filtering (Phase 2 - Not in MVP)

```python
# Future: OR logic for tags (not implemented in Phase 1)
# This is a placeholder for Phase 2 implementation
results = collection.query(
    query_embeddings=[embedding],
    where={
        "$or": [
            {"tags": {"$contains": "react"}},
            {"tags": {"$contains": "firebase"}}
        ]
    },
    n_results=limit
)
```

**Note:** Tag filtering is deferred to Phase 2. MVP stores tags but does not filter by them.

## Rationale for Schema Design

### Single Collection Approach

**Decision:** Keep all cases in single `code_solutions_case_base` collection

**Rationale:**
- Preserves existing vector embeddings (no costly re-embedding)
- Leverages ChromaDB's efficient metadata filtering
- Maintains backward compatibility with existing queries
- Simpler operational model (no cross-collection queries)

**Performance Impact:**
- Minimal: ChromaDB metadata filtering is optimized
- No additional latency from where clauses
- Indexes automatically maintained by ChromaDB

### Metadata vs. Separate Fields

**Decision:** Store categories as metadata fields, not in document text

**Rationale:**
- Enables efficient filtering without full-text search
- Keeps document content semantic (embeddings remain accurate)
- ChromaDB where clauses optimized for metadata filtering
- Easier to update categories without re-embedding

### Comma-Separated Tags vs. Array

**Decision:** Store tags as comma-separated string

**Rationale:**
- ChromaDB metadata supports string and numeric types best
- Simple to implement and migrate
- Sufficient for OR logic tag filtering (Phase 2)
- Easy to parse and display in clients

**Tradeoff:** String manipulation required for tag filtering (acceptable for MVP scale)

## Backward Compatibility

### Existing Query Support

**Guarantee:** All existing queries continue to work unchanged

**Mechanism:**
- Queries without where filter: Return all cases (existing behavior)
- New category parameter: Optional, defaults to no filter
- Existing metadata fields: Preserved during migration

**Validation:**
```python
# Existing query (no changes)
results = await retriever.retrieve_relevant_examples(
    query="Firebase authentication",
    max_results=5
)
# Still works, returns all matching cases regardless of category

# New query with category
results = await retriever.search_by_category(
    category="code",
    subcategory="firebase-auth",
    query="Firebase authentication",
    limit=5
)
# Returns only code/firebase-auth cases
```

### Migration Rollback

**If migration fails:**
1. ChromaDB metadata updates are atomic per document
2. Partial migration can be detected by checking for category field presence
3. Re-run migration to complete (idempotent)
4. No rollback needed (metadata additions don't break existing functionality)

**Validation Command:**
```python
# Check migration status
results = collection.get(include=["metadatas"])
migrated = sum(1 for m in results["metadatas"] if "category" in m)
total = len(results["metadatas"])
print(f"Migration status: {migrated}/{total} cases migrated")
```
