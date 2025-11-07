# Database Migration Guide - Metadata Schema Upgrade

> Last Updated: 2025-11-05
> Version: 1.0.0
> Related Spec: 2025-11-04-metadata-storage-bug-fix

## Overview

This guide provides step-by-step instructions for migrating your CBR MCP Server database from the old metadata schema (problem-only) to the new complete metadata schema (problem, category, subcategory, tags).

**Migration Required If:**
- Your database was created before November 2025
- Category-based search returns no results or errors
- Database metadata only contains the "problem" field

## Why Migrate?

### Before Migration (Broken State)

**Database Metadata:**
```python
{
    "problem": "How to implement Firebase authentication?"
    # Missing: category, subcategory, tags
}
```

**Symptoms:**
- `cbr_search_category(category="firebase")` returns empty list or error
- Category filtering completely non-functional
- Can only use semantic search, not category-based filtering
- AI agents cannot filter examples by domain

### After Migration (Fixed State)

**Database Metadata:**
```python
{
    "problem": "How to implement Firebase authentication?",
    "category": "firebase",
    "subcategory": "auth",
    "tags": "firebase,authentication,react,hooks"
}
```

**Benefits:**
- `cbr_search_category(category="firebase")` returns all Firebase cases
- Subcategory filtering works: `cbr_search_category(category="firebase", subcategory="auth")`
- AI agents can efficiently filter examples by domain
- Both semantic search AND category filtering work together

## Pre-Migration Checklist

### Step 1: Verify You Need Migration

Check your current database metadata:

```bash
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
sample = collection.get(limit=1, include=['metadatas'])
print('Current metadata fields:', list(sample['metadatas'][0].keys()))
"
```

**If output shows only `['problem']`:**
- ✅ You need migration - proceed with this guide

**If output shows `['problem', 'category', 'subcategory', 'tags']`:**
- ✅ Already migrated - no action needed

### Step 2: Verify Case Files Have Complete Metadata

Check that your case source files have all required fields:

```bash
python -c "
from cases import load_all_cases

cases = load_all_cases()
print(f'Total cases: {len(cases)}')

# Check first case structure
first_case = cases[0]
required_fields = ['problem', 'solution', 'category', 'subcategory', 'tags']
missing = [f for f in required_fields if f not in first_case]

if missing:
    print(f'WARNING: Cases missing fields: {missing}')
else:
    print('✓ Case files have complete metadata')
"
```

**Expected Result:**
- ✓ Case files have complete metadata

**If warning appears:**
- Update your case files to include missing fields before migrating
- See [Metadata Schema Guide](Metadata-Schema-Guide.md) for required fields

### Step 3: Backup Your Current Database (Optional)

While the migration is safe (source data is in case files, not the database), you may want a backup:

```bash
# Create timestamped backup
cp -r ./db ./db.backup_$(date +%Y%m%d_%H%M%S)

# Verify backup created
ls -lh ./db.backup_*
```

**Note:** The backup is optional because:
- Source data remains in case files (unchanged)
- Migration can be repeated if needed
- No user-generated data is in the database

## Migration Procedure

### Step 1: Stop Any Running Servers

If the CBR MCP Server is running, stop it before migration:

```bash
# Find and stop any running instances
pkill -f cbr-mcp-server

# Verify no processes remain
ps aux | grep cbr-mcp-server
```

### Step 2: Run Migration Command

Execute the force rebuild to migrate the database:

```bash
cd /path/to/cbr_retrieval_mcp

# Run force rebuild with complete metadata
python scripts/utilities/setup_vectordb.py --force
```

**What Happens:**
1. Script detects existing database (e.g., 103 cases)
2. Prints: "Force rebuild requested. Clearing existing X cases..."
3. Deletes old collection with incomplete metadata
4. Creates new empty collection
5. Loads all cases from source files (with complete metadata)
6. Prints: "Loading all 103 cases from modular structure"
7. Generates embeddings for all problem texts
8. Extracts complete metadata for all cases
9. Prints sample metadata: `{'problem': '...', 'category': '...', 'subcategory': '...', 'tags': '...'}`
10. Validates all metadata has required fields
11. Stores cases with complete metadata in ChromaDB
12. Prints: "Successfully added X cases to the database."

**Expected Output:**
```
Force rebuild requested. Clearing existing 103 cases...
Loading all 103 cases from modular structure

Initializing embedding model...
Connecting to ChromaDB...
Populating the vector database...
Generating embeddings for 103 cases...
Sample metadata (first case): {'problem': '...', 'category': 'orchestration', 'subcategory': 'planning', 'tags': 'orchestration,planning,tdd'}
Adding cases to database...
Successfully added 103 cases to the database.
```

### Step 3: Verify Migration Success

Run verification checks to confirm the migration completed correctly:

#### Check 1: Case Count

```bash
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
print(f'Total cases in database: {collection.count()}')
"
```

**Expected:** Should match your total case count (e.g., 103, 135)

#### Check 2: Metadata Completeness

```bash
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
sample = collection.get(limit=5, include=['metadatas'])

required_fields = {'problem', 'category', 'subcategory', 'tags'}
for i, meta in enumerate(sample['metadatas']):
    fields = set(meta.keys())
    if required_fields.issubset(fields):
        print(f'✓ Case {i}: Complete metadata')
    else:
        missing = required_fields - fields
        print(f'✗ Case {i}: Missing {missing}')
"
```

**Expected:** All cases show "✓ Complete metadata"

#### Check 3: Category Filtering

```bash
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')

# Test category filtering
results = collection.get(
    where={'category': 'orchestration'},
    limit=10
)

print(f'Orchestration cases found: {len(results[\"ids\"])}')
if len(results['ids']) > 0:
    print(f'✓ Category filtering works')
    print(f'Sample metadata: {results[\"metadatas\"][0]}')
else:
    print('✗ Category filtering failed - no results')
"
```

**Expected:** Should find orchestration cases and display complete metadata

#### Check 4: MCP Server Test

Start the server and test category search:

```bash
# Start server (in one terminal)
python -m cbr_mcp_server

# In another terminal, test the MCP tool (if you have MCP client)
# Or just verify server starts without errors
```

**Expected:** Server starts successfully, category search returns results

## Post-Migration Tasks

### Step 1: Remove Backup (Optional)

If migration succeeded and everything works:

```bash
# Remove backup to save disk space
rm -rf ./db.backup_*

# Verify removed
ls -lh ./db.backup_* 2>&1 | grep "No such file"
```

### Step 2: Update Documentation

If you maintain project-specific documentation, update any references to:
- Database setup procedures
- Metadata schema
- Migration status

### Step 3: Verify AI Agent Integration

Test with actual AI agent queries to ensure category filtering works in production:

```python
# Example MCP tool calls to test
cbr_search_category(category="orchestration", limit=10)
cbr_search_category(category="firebase", subcategory="auth")
cbr_search_category(category="rust", subcategory="axum", query="authentication")
```

**Expected:** All queries return relevant, filtered results with complete metadata

## Troubleshooting

### Issue: Migration Fails with Import Error

**Symptom:**
```
ImportError: cannot import name 'load_all_cases' from 'cases'
```

**Solution:**
```bash
# Ensure you're in the project root directory
cd /path/to/cbr_retrieval_mcp

# Verify cases/__init__.py exists
ls -la cases/__init__.py

# Run with explicit Python path
PYTHONPATH=. python scripts/utilities/setup_vectordb.py --force
```

### Issue: Metadata Still Missing After Migration

**Symptom:**
Verification shows metadata still only has "problem" field after running --force

**Diagnosis:**
```bash
# Check if script is using updated code
python -c "
from cbr_mcp_server.metadata_extraction import extract_metadata_from_case
test_case = {
    'problem': 'test',
    'solution': 'test',
    'category': 'firebase',
    'subcategory': 'auth',
    'tags': ['test']
}
meta = extract_metadata_from_case(test_case)
print('Extracted metadata:', meta)
"
```

**Expected Output:**
```python
Extracted metadata: {'problem': 'test', 'category': 'firebase', 'subcategory': 'auth', 'tags': 'test'}
```

**If only problem shows:**
1. Verify you have the latest code with metadata fix
2. Check git status for uncommitted changes
3. Reinstall package: `pip install -e .`

### Issue: Category Filtering Returns Zero Results

**Symptom:**
Metadata exists but `where={'category': 'orchestration'}` returns empty list

**Diagnosis:**
```bash
# Check exact metadata values
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
all_cases = collection.get(include=['metadatas'])

# Find unique categories
categories = set(m.get('category', 'MISSING') for m in all_cases['metadatas'])
print('Categories in database:', sorted(categories))
"
```

**Check:**
- Are categories exactly matching? (case-sensitive: "orchestration" not "Orchestration")
- Are there any "MISSING" or "unknown" values?

**Solution:**
```bash
# If categories are wrong, rebuild again
python scripts/utilities/setup_vectordb.py --force

# Verify categories after rebuild
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
result = collection.get(where={'category': 'orchestration'}, limit=1)
print(f'Found {len(result[\"ids\"])} orchestration cases')
"
```

### Issue: Case Count Decreased After Migration

**Symptom:**
Database had 103 cases, after migration only has 95 cases

**Diagnosis:**
```bash
# Check validation warnings during migration
python scripts/utilities/setup_vectordb.py --force 2>&1 | grep -i warning

# Check case files have complete metadata
python -c "
from cases import load_all_cases, validate_case

cases = load_all_cases()
print(f'Loaded {len(cases)} cases from files')

invalid_count = 0
for i, case in enumerate(cases):
    if not validate_case(case):
        invalid_count += 1
        print(f'Case {i} failed validation')

print(f'\\nInvalid cases: {invalid_count}')
"
```

**Solution:**
1. Fix case files with validation warnings (missing required fields)
2. Re-run migration after fixing cases
3. Verify case count matches: `len(load_all_cases()) == collection.count()`

### Issue: Tags Are Empty String

**Symptom:**
Metadata has `"tags": ""` instead of comma-separated values

**Diagnosis:**
```bash
# Check tag extraction
python -c "
from cbr_mcp_server.metadata_extraction import extract_metadata_from_case

# Test case with tags
test_case = {
    'problem': 'test',
    'solution': 'test',
    'category': 'firebase',
    'subcategory': 'auth',
    'tags': ['firebase', 'auth', 'react']
}

meta = extract_metadata_from_case(test_case)
print('Tags:', meta['tags'])
print('Type:', type(meta['tags']))
"
```

**Expected:** `Tags: firebase,auth,react` (comma-separated string)

**If empty:**
1. Check case files have tags as list: `"tags": ["tag1", "tag2"]`
2. Verify not using tuple or string: `"tags": ("tag1",)` ❌
3. Rebuild after fixing: `python scripts/utilities/setup_vectordb.py --force`

## Rollback Procedure

If migration causes issues and you need to rollback:

### Step 1: Restore from Backup (if created)

```bash
# Stop server
pkill -f cbr-mcp-server

# Remove broken database
rm -rf ./db

# Restore backup
cp -r ./db.backup_YYYYMMDD_HHMMSS ./db

# Restart server
python -m cbr_mcp_server
```

### Step 2: Use Old Database Without Metadata

If you don't have a backup but want to use the old schema:

```bash
# Delete current database
rm -rf ./db

# Revert code to pre-migration version (if needed)
# Then rebuild with old version
# This will create database with problem-only metadata
```

**Note:** The old database will work for semantic search but category filtering will not function.

## Migration Best Practices

### For Teams

1. **Coordinate Migration:** Ensure all team members migrate at the same time
2. **Commit Updated Code:** Ensure everyone has the latest metadata extraction code
3. **Share Migration Status:** Document migration date and database version
4. **Test After Migration:** Verify category search works for your use cases

### For Production Systems

1. **Test in Staging First:** Migrate staging database and verify before production
2. **Schedule Downtime:** Plan for brief server restart during migration
3. **Monitor After Migration:** Check logs for any category filtering errors
4. **Keep Backup:** Retain backup for 24-48 hours after successful migration

### For Development

1. **Migrate Immediately:** No reason to keep old schema in development
2. **Document Changes:** Update any local documentation about database structure
3. **Verify New Cases:** Test adding new cases after migration

## Migration Summary

**Pre-Migration State:**
- Database metadata: `{"problem": "..."}`
- Category search: ❌ Broken
- Semantic search: ✅ Works

**Migration Command:**
```bash
python scripts/utilities/setup_vectordb.py --force
```

**Post-Migration State:**
- Database metadata: `{"problem": "...", "category": "...", "subcategory": "...", "tags": "..."}`
- Category search: ✅ Works
- Semantic search: ✅ Works
- Combined filtering: ✅ Works

**Time Required:** 2-5 minutes depending on case count

**Data Loss:** None (source data is in case files)

**Reversibility:** Yes (restore from backup or rebuild with old code)

## Additional Resources

- [Metadata Schema Guide](Metadata-Schema-Guide.md) - Complete metadata documentation
- [README.md](../README.md) - Database setup instructions
- Spec: `.agent-os/specs/2025-11-04-metadata-storage-bug-fix/` - Technical details of the fix
- `scripts/utilities/setup_vectordb.py` - Migration script source code
- `src/cbr_mcp_server/metadata_extraction.py` - Metadata extraction functions
