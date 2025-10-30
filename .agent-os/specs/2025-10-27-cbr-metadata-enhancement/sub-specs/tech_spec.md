# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-10-27-cbr-metadata-enhancement/spec.md

> Created: 2025-10-27
> Version: 1.0.0

## Technical Requirements

### Metadata Structure

**Category Taxonomy:**
- Top-level categories: `code`, `orchestration`, `best-practice`, `anti-pattern`
- Subcategories defined per category (see Category Taxonomy section below)
- Stored as separate `category` and `subcategory` metadata fields in ChromaDB

**Tags Structure:**
- Stored as comma-separated string in ChromaDB metadata
- Example: `tags: "react,firebase,typescript,authentication"`
- Tags are case-insensitive for matching
- Empty tags field allowed for cases without tags

**ChromaDB Metadata Schema:**
```python
metadata = {
    "category": str,          # Required: code|orchestration|best-practice|anti-pattern
    "subcategory": str,       # Required: specific subcategory based on category
    "tags": str,              # Optional: comma-separated tags
    "source": str,            # Existing field: maintained for compatibility
    # Other existing fields preserved
}
```

### Category Taxonomy

**Code Category:**
- `firebase-auth` - Firebase authentication examples
- `react-components` - React component patterns
- `api-routes` - API endpoint implementations
- `database` - Database operations
- `testing` - Test patterns
- `general` - Uncategorized code examples

**Orchestration Category:**
- `remediation` - Remediation Protocol patterns
- `planning` - Planning and decomposition patterns
- `delegation` - Agent delegation patterns
- `verification` - Karen verification workflows
- `completion` - Task completion protocols

**Best-Practice Category:**
- `planning` - How to structure plans
- `verification` - Verification protocols
- `error-handling` - Error recovery patterns

**Anti-Pattern Category:**
- `completion-bias` - Premature completion patterns
- `verification-skip` - Skipped verification issues
- `protocol-violation` - Protocol violations

## Approach

### Selected Approach: Single Collection with Metadata Filtering

**Rationale:**
- Maintains backward compatibility with existing ChromaDB collection
- Leverages ChromaDB's where filter capabilities for efficient category queries
- Avoids complexity of multi-collection management
- Preserves existing vector embeddings (no re-embedding required)

**Implementation Strategy:**
1. Add new metadata fields to existing collection documents
2. Update ProductionCBRRetriever methods to use ChromaDB where filters
3. Create migration script to populate new metadata fields for existing cases
4. Maintain backward compatibility by defaulting to no filter when category not specified

### Alternative Approaches Considered

**Option A: Multi-Collection Approach**
- Pros: Clear separation of categories, independent scaling per category
- Cons: Complex collection management, query complexity for cross-category searches, migration overhead
- Rejected: Unnecessary complexity for current scale

**Option B: Prefix-Based Categorization**
- Pros: Simple implementation using document IDs
- Cons: Cannot change categories without re-embedding, poor query flexibility
- Rejected: Inflexible metadata structure

## Technical Architecture

### ProductionCBRRetriever Changes

**Method: search_by_category**
```python
async def search_by_category(
    self,
    category: str,
    subcategory: Optional[str] = None,
    query: str = "",
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Search for cases within a specific category and optional subcategory."""

    # Build ChromaDB where filter
    where_filter = {"category": category}
    if subcategory:
        where_filter["subcategory"] = subcategory

    # Encode query if provided
    if query:
        self._ensure_embedding_model_loaded()
        query_embedding = self.embedding_model.encode(query).tolist()
    else:
        query_embedding = None

    # Query with category filter
    if query_embedding:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            where=where_filter,
            n_results=limit
        )
    else:
        # No query, just return cases in category
        results = self.collection.get(
            where=where_filter,
            limit=limit
        )

    # Format results with category information
    formatted_results = self._format_query_results(results)
    for result in formatted_results:
        result['category'] = category
        result['subcategory'] = result['metadata'].get('subcategory', '')

    return formatted_results
```

**Method: get_categories**
```python
async def get_categories(self) -> List[Dict[str, Any]]:
    """Get hierarchical category structure with counts."""

    categories = {
        "code": {
            "name": "code",
            "description": "Code examples and implementations",
            "subcategories": []
        },
        "orchestration": {
            "name": "orchestration",
            "description": "Agent orchestration flow patterns",
            "subcategories": []
        },
        "best-practice": {
            "name": "best-practice",
            "description": "Best practice patterns and guidelines",
            "subcategories": []
        },
        "anti-pattern": {
            "name": "anti-pattern",
            "description": "Common mistakes and corrections",
            "subcategories": []
        }
    }

    # Query collection to get actual counts per category/subcategory
    for category_name in categories.keys():
        results = self.collection.get(
            where={"category": category_name},
            include=["metadatas"]
        )

        # Count subcategories
        subcategory_counts = {}
        for metadata in results.get("metadatas", []):
            subcat = metadata.get("subcategory", "unknown")
            subcategory_counts[subcat] = subcategory_counts.get(subcat, 0) + 1

        # Build subcategory list
        categories[category_name]["count"] = len(results.get("ids", []))
        categories[category_name]["subcategories"] = [
            {"name": subcat, "count": count}
            for subcat, count in sorted(subcategory_counts.items())
        ]

    return list(categories.values())
```

### Migration Script Architecture

**File: migrate_metadata.py**

```python
import chromadb
from sentence_transformers import SentenceTransformer
from typing import Any, Dict, Tuple

class MetadataMigration:
    """Migrate existing cases to new metadata structure.

    Uses simple substring matching (no regex) for pattern detection.
    """

    CATEGORY_PATTERNS = {
        "code": {
            "firebase-auth": ["firebase", "auth", "authentication", "firebaseauth"],
            "react-components": ["react component", "component", "jsx", "tsx"],
            "api-routes": ["api", "endpoint", "route", "express"],
            "database": ["database", "firestore", "mongodb", "sql"],
            "testing": ["test", "jest", "pytest", "unittest"],
        },
        "orchestration": {
            "remediation": ["remediation", "fix", "repair", "recover"],
            "planning": ["plan", "decompose", "breakdown"],
            "delegation": ["delegate", "assign", "agent"],
            "verification": ["verify", "karen", "validate"],
            "completion": ["complete", "finish", "done"],
        },
        "best-practice": {
            "planning": ["planning best", "plan structure"],
            "verification": ["verification protocol", "verify best"],
            "error-handling": ["error handling", "error recovery"],
        },
        "anti-pattern": {
            "completion-bias": ["premature completion", "completion bias"],
            "verification-skip": ["skip verification", "skipped verification"],
            "protocol-violation": ["protocol violation", "violate protocol"],
        }
    }

    def detect_category_subcategory(self, problem_text: str) -> Tuple[str, str]:
        """Auto-detect category and subcategory from problem text."""
        problem_lower = problem_text.lower()

        # Check each category's patterns
        for category, subcategories in self.CATEGORY_PATTERNS.items():
            for subcategory, patterns in subcategories.items():
                for pattern in patterns:
                    if pattern in problem_lower:
                        return category, subcategory

        # Default to code/general if no match
        return "code", "general"

    def extract_tags(self, problem_text: str, solution_text: str) -> str:
        """Extract tags from case content."""
        content = f"{problem_text} {solution_text}".lower()

        # Common technology tags
        tech_keywords = [
            "react", "firebase", "typescript", "javascript", "python",
            "authentication", "database", "api", "testing", "orchestration"
        ]

        found_tags = [tag for tag in tech_keywords if tag in content]
        return ",".join(found_tags) if found_tags else ""

    def migrate_collection(self, collection):
        """Migrate all documents in collection."""
        results = collection.get(include=["documents", "metadatas"])

        # Collect cases to migrate for batched update
        ids_to_update = []
        metadatas_to_update = []

        for i, doc_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i]
            document = results["documents"][i]

            # Skip if already migrated
            if "category" in metadata and "subcategory" in metadata:
                continue

            # Detect category and subcategory
            category, subcategory = self.detect_category_subcategory(document)

            # Extract tags (simplified for MVP)
            tags = self.extract_tags(document, metadata.get("solution", ""))

            # Update metadata
            metadata["category"] = category
            metadata["subcategory"] = subcategory
            metadata["tags"] = tags

            # Add to batched update
            ids_to_update.append(doc_id)
            metadatas_to_update.append(metadata)

        # Perform single batched update for efficiency
        if ids_to_update:
            collection.update(
                ids=ids_to_update,
                metadatas=metadatas_to_update
            )

        return len(ids_to_update)
```

## User Flow Logic

### Category-Based Search Flow

1. Agent requests cases in category "orchestration" with subcategory "remediation"
2. CBR MCP Server receives request via cbr_search_category tool
3. ProductionCBRRetriever.search_by_category builds ChromaDB where filter:
   ```python
   where = {"category": "orchestration", "subcategory": "remediation"}
   ```
4. ChromaDB filters collection to matching documents before similarity search
5. Results returned contain only orchestration/remediation cases
6. Agent receives focused, relevant examples

### Migration Flow

1. Administrator runs migration script: `python migrate_metadata.py`
2. Script connects to ChromaDB collection
3. For each existing case:
   - Read document content and existing metadata
   - Apply pattern matching to detect category/subcategory
   - Extract technology tags from content
   - Update metadata in place (no re-embedding)
4. Migration completes with summary of categorized cases
5. All cases now queryable via new category structure

## Error Handling

### Missing Category Metadata

**Scenario:** Query requests category filter but case lacks category metadata

**Handling:**
- Migration script ensures all cases have category/subcategory
- Validation step before marking migration complete
- Default to "code/general" for any cases without category

### Invalid Category Values

**Scenario:** Client requests non-existent category

**Handling:**
```python
VALID_CATEGORIES = ["code", "orchestration", "best-practice", "anti-pattern"]

if category not in VALID_CATEGORIES:
    raise ValueError(f"Invalid category: {category}. Must be one of {VALID_CATEGORIES}")
```

### ChromaDB Where Filter Errors

**Scenario:** ChromaDB query with where filter fails

**Handling:**
```python
try:
    results = self.collection.query(where=where_filter, ...)
except Exception as e:
    self.logger.error("Category filter query failed", {"error": str(e), "filter": where_filter})
    # Fallback to unfiltered query with warning
    results = self.collection.query(...)
    self.logger.warning("Falling back to unfiltered query")
```

## External Dependencies

**No new dependencies required:**
- ChromaDB: Already in use (>=0.4.0)
- sentence-transformers: Already in use for embeddings
- All changes use existing libraries

**Justification:**
- Metadata filtering is a built-in ChromaDB feature
- Migration uses standard Python libraries (typing)
- No additional external packages needed for enhanced categorization
