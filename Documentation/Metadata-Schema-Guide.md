# CBR MCP Server - Metadata Schema Guide

> Last Updated: 2025-11-05
> Version: 1.0.0
> Related Spec: 2025-11-04-metadata-storage-bug-fix

## Overview

This guide documents the complete metadata schema for the CBR MCP Server, including how metadata flows from case files through to ChromaDB storage, and how it enables category-based search functionality. Understanding this schema is essential for adding new cases and troubleshooting category filtering issues.

## Metadata Architecture

The CBR MCP Server uses a comprehensive metadata system that enables semantic search combined with category-based filtering. Metadata flows through three stages:

1. **Case Files** - Cases defined in Python modules with full metadata
2. **Case Loader** - Dynamic loader validates and aggregates cases
3. **ChromaDB Storage** - Metadata stored in vector database for filtering

### Metadata Flow Diagram

```
Case Files (Python)          Case Loader              ChromaDB Storage
==================          ==============           =================
{                           validate_case()          {
  "problem": str,      -->  check required    -->    "problem": str,
  "solution": str,          fields                   "category": str,
  "category": str,                                   "subcategory": str,
  "subcategory": str,                                "tags": str (comma-separated)
  "tags": List[str]                                }
}
```

## Complete Metadata Schema

### Case File Schema (Python)

**Location:** All `*_cases.py` files in `cases/` subdirectories

**Required Fields:**

```python
{
    "problem": str,       # Required - Problem description/user request
    "solution": str,      # Required - Code solution/example
    "category": str,      # Required - Top-level category
    "subcategory": str,   # Required - Specific subcategory
    "tags": List[str]     # Required - List of searchable tags
}
```

**Example Case:**
```python
{
    "problem": """
    User: 'I need to add Google Sign-In to our application.'

    How should I plan the implementation?
    """,
    "solution": """
    <tool_code>
        <tool name="sequential-thinking">
            <prompt>
                **Implementation Phase:** Decomposing "Google Sign-In" into verifiable units of work:
                1. UI Work: Create the `GoogleSignInButton` component...
            </prompt>
        </tool>
    </tool_code>
    """,
    "category": "orchestration",
    "subcategory": "planning",
    "tags": ["orchestration", "planning", "delegation", "tdd", "ui", "backend", "google-auth"]
}
```

### Field Definitions

#### problem (string, required)

The problem field describes the scenario, user request, or technical challenge that the case addresses. This field is:
- Used for semantic vector search (embeddings are generated from problem text)
- Stored in ChromaDB metadata for display in search results
- Typically 50-500 words describing the context and requirements

**Best Practices:**
- Include enough context for semantic understanding
- Describe the scenario clearly and completely
- Use natural language that matches how users will search

#### solution (string, required)

The solution field contains the actual code, implementation, or response that solves the problem. This field is:
- Stored as the ChromaDB document (the main content)
- Retrieved when cases match search criteria
- Can be code snippets, complete implementations, or agent conversation examples

**Best Practices:**
- Provide complete, working code when applicable
- Include comments explaining key concepts
- Format code properly for readability

#### category (string, required)

The category field classifies the case into a top-level domain. This field is:
- Used for category-based filtering in `cbr_search_category()`
- Must be one of the values in `ALLOWED_CATEGORIES`
- Stored in ChromaDB metadata as a string

**Valid Categories:**
- `firebase` - Firebase backend services (auth, storage, functions, Firestore)
- `react` - React UI components and patterns
- `nextjs` - Next.js framework patterns (routing, API routes, SSR)
- `bootstrap` - Bootstrap UI components and styling
- `webdev` - General web development patterns
- `orchestration` - Agent orchestration and workflow patterns
- `security` - Security best practices and implementations
- `rust` - Rust programming patterns (surrealdb, axum, tokio, etc.)

**Example Usage:**
```python
"category": "orchestration"  # For agent workflow patterns
"category": "firebase"       # For Firebase implementation examples
"category": "rust"          # For Rust code patterns
```

#### subcategory (string, required)

The subcategory field provides more specific classification within a category. This field is:
- Used for refined filtering in `cbr_search_category(category="X", subcategory="Y")`
- Should be specific to the work type or component
- Stored in ChromaDB metadata as a string

**Common Subcategories by Category:**

**orchestration:**
- `planning` - Task breakdown and decomposition patterns
- `delegation` - Agent delegation patterns
- `remediation` - Error recovery and issue fixing workflows
- `verification` - Quality check and verification protocols
- `completion` - Task completion patterns and checkpoints

**firebase:**
- `auth` - Authentication and user management
- `firestore` - Firestore database operations
- `functions` - Cloud Functions implementations
- `storage` - Firebase Storage operations

**react:**
- `components` - React component patterns
- `hooks` - Custom hooks implementations
- `context` - Context API usage
- `state` - State management patterns

**nextjs:**
- `routing` - App Router and page patterns
- `api` - API routes and server actions
- `middleware` - Middleware implementations

**rust:**
- `axum` - Axum web framework patterns
- `tokio` - Async runtime patterns
- `surrealdb` - SurrealDB database operations
- `wasm` - WebAssembly patterns

**Example Usage:**
```python
"category": "orchestration",
"subcategory": "planning"  # Specific to planning phase workflows
```

#### tags (list of strings, required)

The tags field provides searchable keywords for discovering related cases. This field is:
- A Python list of strings in case files
- Converted to comma-separated string when stored in ChromaDB
- Used for technology-specific discovery and cross-category search
- Should include all relevant technologies, frameworks, and concepts

**Tag Guidelines:**
- Include the category and subcategory as tags
- Add all relevant technologies (e.g., "react", "typescript", "firebase")
- Include patterns and concepts (e.g., "authentication", "async", "hooks")
- Use lowercase with hyphens for multi-word tags (e.g., "password-reset")
- Provide 3-7 tags per case for optimal discoverability

**Example Usage:**
```python
"tags": ["orchestration", "planning", "tdd", "rust", "database", "delegation"]
```

This indicates the case is about orchestration planning, uses TDD, involves Rust and database work, and includes delegation patterns.

### ChromaDB Storage Schema

When cases are stored in ChromaDB, metadata is converted to a compatible format:

```python
{
    "problem": str,        # Problem text (backward compatible)
    "category": str,       # Category for filtering
    "subcategory": str,    # Subcategory for filtering
    "tags": str           # Comma-separated tags (ChromaDB constraint)
}
```

**ChromaDB Storage Constraints:**
- Metadata values must be: string, number, or boolean
- Lists are NOT supported → tags converted to comma-separated string
- Field names are case-sensitive
- Null values not allowed → defaults used for missing fields

**Conversion Example:**
```python
# Case file format
case = {
    "problem": "How to implement Firebase auth?",
    "solution": "...",
    "category": "firebase",
    "subcategory": "auth",
    "tags": ["firebase", "authentication", "react"]
}

# ChromaDB metadata format (after conversion)
metadata = {
    "problem": "How to implement Firebase auth?",
    "category": "firebase",
    "subcategory": "auth",
    "tags": "firebase,authentication,react"  # List → comma-separated string
}
```

## Metadata Validation

### Case File Validation

The `validate_case()` function in `cases/__init__.py` validates all case metadata before loading:

**Validation Rules:**
1. All required fields must be present: `problem`, `solution`, `category`, `subcategory`, `tags`
2. Tags field must be a Python list (not tuple, string, or other type)
3. Category must be in `ALLOWED_CATEGORIES` whitelist
4. All fields must have appropriate types

**Validation Function:**
```python
def validate_case(case: Dict[str, Any]) -> bool:
    """
    Validate that a case has all required metadata fields.

    Returns True if valid, False if validation fails.
    Logs warnings for any validation failures.
    """
    required_fields = ["problem", "solution", "category", "subcategory", "tags"]

    # Check all fields present
    for field in required_fields:
        if field not in case:
            logger.warning(f"Case missing required field '{field}'")
            return False

    # Validate tags is a list
    if not isinstance(case.get("tags"), list):
        logger.warning("Case 'tags' must be a list")
        return False

    # Validate category whitelist
    if case.get("category") not in ALLOWED_CATEGORIES:
        logger.warning(f"Category '{case['category']}' not in whitelist")
        return False

    return True
```

### Database Population Validation

The `setup_vectordb.py` script validates metadata before storing in ChromaDB:

**Validation Steps:**
1. Extract metadata using `extract_metadata_list()`
2. Verify metadata count matches case count
3. Check all metadata dicts have required fields
4. Log sample metadata for verification

**Validation Code:**
```python
# Extract and validate metadata
metadatas = extract_metadata_list(CASE_BASE)

# Count validation
assert len(metadatas) == len(CASE_BASE), \
    f"Metadata count mismatch: {len(metadatas)} != {len(CASE_BASE)}"

# Sample verification
print(f"Sample metadata (first case): {metadatas[0]}")

# Field validation
required_fields = {"problem", "category", "subcategory", "tags"}
for i, metadata in enumerate(metadatas):
    missing_fields = required_fields - set(metadata.keys())
    if missing_fields:
        print(f"Warning: Case {i} missing fields: {missing_fields}")
```

## Database Setup and Migration

### Initial Database Setup

**Command:**
```bash
python scripts/utilities/setup_vectordb.py
```

**Process:**
1. Load all cases from modular case files
2. Validate each case has complete metadata
3. Generate embeddings for problem text
4. Extract metadata into ChromaDB format
5. Store cases with complete metadata in vector database

**Verification:**
```bash
# Check metadata was stored correctly
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
result = collection.get(limit=1, include=['metadatas'])
print('Sample metadata:', result['metadatas'][0])
"
```

Expected output should show all four metadata fields:
```python
{
    'problem': '...',
    'category': 'orchestration',
    'subcategory': 'planning',
    'tags': 'orchestration,planning,tdd,...'
}
```

### Database Migration (Rebuilding with Complete Metadata)

If you have an existing database with incomplete metadata (missing category, subcategory, or tags), you must rebuild it:

**Command:**
```bash
python scripts/utilities/setup_vectordb.py --force
```

**What --force Does:**
1. Detects existing database (103 cases)
2. Deletes old collection with incomplete metadata
3. Creates new empty collection
4. Reloads all cases from source files (with complete metadata)
5. Regenerates embeddings
6. Stores cases with complete metadata

**Migration Safety:**
- Source data remains in case files (unchanged)
- Embeddings are regenerated from source (deterministic)
- No user-generated data is lost
- Migration is idempotent (can run multiple times safely)

**Before Migration (Broken State):**
```python
# Database has only problem field
{
    "problem": "How to plan orchestration?",
    # Missing: category, subcategory, tags
}

# Category search fails
cbr_search_category(category="orchestration")
# Error: Cannot filter by category - field doesn't exist
```

**After Migration (Fixed State):**
```python
# Database has all metadata fields
{
    "problem": "How to plan orchestration?",
    "category": "orchestration",
    "subcategory": "planning",
    "tags": "orchestration,planning,tdd,delegation"
}

# Category search works
cbr_search_category(category="orchestration")
# Returns: 24 orchestration cases with full metadata
```

### Backup Recommendations

**Before Migration:**
```bash
# Optional: Backup existing database directory
cp -r ./db ./db.backup_$(date +%Y%m%d)
```

**After Successful Migration:**
```bash
# Remove backup if migration succeeded
rm -rf ./db.backup_*
```

### Verification After Migration

**Step 1: Check Case Count**
```bash
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
print(f'Case count: {collection.count()}')
"
```
Expected: `Case count: 135` (or current total case count)

**Step 2: Verify Metadata Fields**
```bash
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
result = collection.get(limit=5, include=['metadatas'])
for i, meta in enumerate(result['metadatas']):
    fields = set(meta.keys())
    required = {'problem', 'category', 'subcategory', 'tags'}
    missing = required - fields
    if missing:
        print(f'Case {i} missing: {missing}')
    else:
        print(f'Case {i}: ✓ Complete metadata')
"
```
Expected: All cases show "Complete metadata"

**Step 3: Test Category Filtering**
```bash
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
results = collection.get(
    where={'category': 'orchestration'},
    limit=5
)
print(f'Orchestration cases: {len(results[\"ids\"])}')
"
```
Expected: Should return orchestration cases (not zero or error)

## Using Metadata in Queries

### Category-Based Search

**Basic Category Filtering:**
```python
# Search all cases in orchestration category
results = cbr_search_category(category="orchestration", limit=20)

# Returns cases where metadata["category"] == "orchestration"
```

**Category + Subcategory Filtering:**
```python
# Search for specific orchestration planning patterns
results = cbr_search_category(
    category="orchestration",
    subcategory="planning",
    limit=10
)

# Returns cases where:
# - metadata["category"] == "orchestration" AND
# - metadata["subcategory"] == "planning"
```

**Category + Semantic Query:**
```python
# Combine category filtering with semantic search
results = cbr_search_category(
    category="orchestration",
    subcategory="planning",
    query="how to break down tasks using TDD",
    limit=5
)

# Returns orchestration planning cases semantically similar to query
```

### Understanding Search Results

**Result Metadata Structure:**
```python
result = {
    "id": "id42",
    "document": "...solution code...",
    "metadata": {
        "problem": "How to plan orchestration?",
        "category": "orchestration",
        "subcategory": "planning",
        "tags": "orchestration,planning,tdd,delegation"
    },
    "distance": 0.15  # Similarity score (lower = more similar)
}
```

**Using Result Metadata:**
```python
for result in results:
    problem = result["metadata"]["problem"]
    category = result["metadata"]["category"]
    subcategory = result["metadata"]["subcategory"]
    tags = result["metadata"]["tags"].split(",")  # Convert back to list

    print(f"Category: {category}/{subcategory}")
    print(f"Tags: {', '.join(tags)}")
    print(f"Problem: {problem}")
```

## Adding New Cases with Complete Metadata

### Step 1: Choose Case File Location

Select or create a case file based on category:
- `cases/orchestration/orchestration_*_cases.py` for orchestration patterns
- `cases/firebase/firebase_*_cases.py` for Firebase examples
- `cases/react/react_*_cases.py` for React components
- etc.

### Step 2: Write Case with Complete Metadata

```python
# Add to appropriate case list (e.g., ORCHESTRATION_PLANNING_CASES)
{
    "problem": """
    Clear description of the problem or scenario.
    Include context and requirements.
    """,
    "solution": """
    Complete code solution or implementation example.
    Include comments and proper formatting.
    """,
    "category": "orchestration",        # Must be in ALLOWED_CATEGORIES
    "subcategory": "planning",          # Specific to work type
    "tags": [                           # 3-7 searchable keywords
        "orchestration",
        "planning",
        "tdd",
        "rust",
        "database"
    ]
}
```

### Step 3: Validate Case Metadata

```python
from cases import validate_case

# Test your case
your_case = {
    "problem": "...",
    "solution": "...",
    "category": "orchestration",
    "subcategory": "planning",
    "tags": ["orchestration", "planning"]
}

is_valid = validate_case(your_case)
print(f"Valid: {is_valid}")
```

### Step 4: Rebuild Database

After adding new cases, rebuild the database to include them:

```bash
# Rebuild with new cases
python scripts/utilities/setup_vectordb.py --force

# Verify new case count
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
print(f'Total cases: {collection.count()}')
"
```

## Troubleshooting Metadata Issues

### Issue: Category Search Returns No Results

**Symptom:**
```python
results = cbr_search_category(category="orchestration")
# Returns empty list or error
```

**Diagnosis:**
```python
# Check if metadata has category field
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
sample = collection.get(limit=1, include=['metadatas'])
print(sample['metadatas'][0])
```

**If only "problem" field exists:**
```python
# Output: {'problem': '...'}
# Missing: category, subcategory, tags
```

**Solution:**
```bash
# Rebuild database with complete metadata
python scripts/utilities/setup_vectordb.py --force
```

### Issue: Case Fails Validation

**Symptom:**
```
WARNING: Case missing required field 'category'
```

**Diagnosis:**
- Check case file has all required fields
- Verify tags is a list, not a string
- Confirm category is in ALLOWED_CATEGORIES

**Solution:**
```python
# Fix case structure
{
    "problem": "...",
    "solution": "...",
    "category": "orchestration",     # ✓ Add missing field
    "subcategory": "planning",       # ✓ Add missing field
    "tags": ["tag1", "tag2"]         # ✓ Must be list
}
```

### Issue: Metadata Count Mismatch

**Symptom:**
```
AssertionError: Metadata count mismatch: 102 != 103
```

**Diagnosis:**
- One or more cases missing metadata fields
- Metadata extraction function skipping invalid cases

**Solution:**
1. Check validation warnings during case loading
2. Fix cases with missing metadata
3. Rebuild database

### Issue: Tags Not Searchable

**Symptom:**
```python
# Tags appear in metadata but search doesn't work well
```

**Explanation:**
- Tags are stored as comma-separated string in ChromaDB
- ChromaDB doesn't natively search within string values
- Tags are primarily for display and manual filtering

**Solution:**
- Use category/subcategory for filtering
- Use semantic search on problem text to match tag concepts
- Tags are informational for result interpretation

## Metadata Schema History

### Version 1.0 (Broken) - Pre-November 2025

**Schema:**
```python
{"problem": str}  # Only field stored
```

**Issue:** Category-based search completely non-functional due to missing metadata fields.

### Version 2.0 (Fixed) - November 2025

**Schema:**
```python
{
    "problem": str,
    "category": str,
    "subcategory": str,
    "tags": str  # Comma-separated
}
```

**Fix:** Spec 2025-11-04-metadata-storage-bug-fix implemented complete metadata storage.

**Migration:** All existing databases require `--force` rebuild to upgrade schema.

## Summary

The CBR MCP Server metadata schema enables powerful category-based filtering on top of semantic search. Key points:

1. **All cases must have complete metadata**: problem, solution, category, subcategory, tags
2. **Validation occurs at two stages**: case loading and database population
3. **ChromaDB storage converts list tags to comma-separated strings** due to database constraints
4. **Migration requires --force rebuild** to add metadata to existing databases
5. **Category filtering depends on complete metadata** being stored in ChromaDB

For more information:
- See `cases/__init__.py` for case validation logic
- See `scripts/utilities/setup_vectordb.py` for database population
- See `src/cbr_mcp_server/metadata_extraction.py` for metadata conversion
- See spec `2025-11-04-metadata-storage-bug-fix` for implementation details
