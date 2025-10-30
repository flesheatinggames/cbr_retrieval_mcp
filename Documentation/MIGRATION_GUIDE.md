# CBR MCP Server Metadata Migration Guide

> **Version:** 1.0.0
> **Last Updated:** 2025-10-28
> **Target Release:** Metadata Enhancement v1.0

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Migration Script Documentation](#migration-script-documentation)
4. [Production Deployment Runbook](#production-deployment-runbook)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Command Reference](#command-reference)
7. [Validation Reference](#validation-reference)

---

## Overview

### What This Migration Accomplishes

This migration adds structured metadata categorization to the CBR MCP Server case base. It enhances the existing ChromaDB collection by adding three new metadata fields to each case:

- **category**: Top-level category (`code`, `orchestration`, `best-practice`, `anti-pattern`)
- **subcategory**: Specific subcategory based on the category (e.g., `firebase-auth`, `remediation`)
- **tags**: Comma-separated technology tags (e.g., `react,firebase,typescript`)

**Key Benefits:**
- Enables category-based case retrieval for AI agents
- Improves relevance of search results through filtering
- Maintains backward compatibility with existing queries
- No re-embedding required (preserves existing vectors)

### When to Use This Guide

Use this guide when:
- Deploying the metadata enhancement feature to production
- Migrating an existing CBR case base to the new metadata structure
- Troubleshooting migration issues
- Validating metadata integrity after migration

### Migration Safety

**This migration is safe and idempotent:**
- ✅ Runs multiple times without duplicating work
- ✅ Skips already-migrated cases automatically
- ✅ No vector re-embedding required (preserves existing embeddings)
- ✅ All existing metadata fields preserved
- ✅ Can be validated before and after migration
- ✅ Rollback available through backup restoration

---

## Prerequisites

### System Requirements

**Python Environment:**
```bash
Python >= 3.8
chromadb >= 0.4.0
sentence-transformers (existing dependency)
```

**Database Requirements:**
- ChromaDB collection: `code_solutions_case_base` (or custom collection name)
- Database path: `./db` (or custom path)
- Read/write access to the database directory

**Disk Space:**
- Minimal additional space required (metadata only, no new embeddings)
- Recommend 100MB free space for backup safety

### Pre-Migration Checklist

Before running the migration, ensure:

- [ ] **Backup created** - Full backup of `./db` directory
- [ ] **Sufficient disk space** - At least 100MB available
- [ ] **No active connections** - Stop any running CBR MCP Server instances
- [ ] **Python environment activated** - Virtual environment with dependencies installed
- [ ] **Database accessible** - ChromaDB database directory exists and is readable
- [ ] **Collection exists** - Target collection is present in the database

---

## Migration Script Documentation

### What migrate_metadata.py Does

The migration script performs these operations:

1. **Connects to ChromaDB** - Establishes connection to the persistent database
2. **Reads existing cases** - Fetches all documents and their current metadata
3. **Detects categories** - Uses pattern matching to auto-categorize cases
4. **Extracts tags** - Identifies technology tags from case content
5. **Updates metadata** - Adds category, subcategory, and tags fields
6. **Validates results** - Verifies all cases have complete metadata

**Pattern-Based Detection:**

The script uses substring matching against predefined patterns to categorize cases. Categories are checked in precedence order to handle overlapping patterns:

```
Priority Order: anti-pattern > best-practice > orchestration > code
```

**Example Pattern Matching:**
```python
# Problem text: "How to implement firebase authentication in React?"
# Result: category="code", subcategory="firebase-auth", tags="react,firebase,authentication"

# Problem text: "Remediation protocol for incomplete verification"
# Result: category="orchestration", subcategory="remediation", tags="orchestration"
```

### Command-Line Usage

#### Basic Usage

```bash
# Standard migration (default database and collection)
python migrate_metadata.py
```

**Expected Output:**
```
Starting CBR metadata migration...
Found 150 total cases in collection

Migrating cases...

Migration complete:
  - Migrated: 150 cases
  - Unchanged: 0 cases

Validating migration...
✅ All cases have complete metadata
```

#### Custom Database Path

The script currently uses hardcoded paths. To use a custom database path, modify the script:

```python
# In migrate_metadata.py, line 24
client = chromadb.PersistentClient(path="/custom/path/to/db")
```

#### Custom Collection Name

```python
# In migrate_metadata.py, line 25
collection = client.get_collection("custom_collection_name")
```

### Migration Process Step-by-Step

**Phase 1: Connection**
```
1. Import MetadataMigration class
2. Connect to ChromaDB at ./db
3. Get collection 'code_solutions_case_base'
4. Count total cases
```

**Phase 2: Migration**
```
5. Fetch all documents and metadata
6. For each case:
   a. Check if already migrated (has category/subcategory)
   b. If not migrated:
      - Detect category/subcategory from document text
      - Extract technology tags from content
      - Add fields to metadata
   c. Add to batch update list
7. Perform single batched update to ChromaDB
```

**Phase 3: Validation**
```
8. Fetch all cases again
9. Check each case has category and subcategory
10. Report any missing metadata
11. Exit with status code (0=success, 1=errors)
```

### Idempotency Guarantee

**The migration script is safe to run multiple times:**

```python
# Skip logic in metadata_migration.py (lines 127-129)
if "category" in metadata and "subcategory" in metadata:
    continue  # Already migrated, skip this case
```

**Scenarios:**
- **First run:** Migrates all cases, returns count of migrated cases
- **Second run:** Skips all cases, returns 0 migrated (all unchanged)
- **Partial failure recovery:** Migrates only non-migrated cases after fixing issues

### Expected Output Examples

**Successful Migration:**
```
Starting CBR metadata migration...
Found 150 total cases in collection

Migrating cases...

Migration complete:
  - Migrated: 150 cases
  - Unchanged: 0 cases

Validating migration...
✅ All cases have complete metadata
```

**Already Migrated:**
```
Starting CBR metadata migration...
Found 150 total cases in collection

Migrating cases...

Migration complete:
  - Migrated: 0 cases
  - Unchanged: 150 cases

Validating migration...
✅ All cases have complete metadata
```

**Partial Migration (Error Recovery):**
```
Starting CBR metadata migration...
Found 150 total cases in collection

Migrating cases...

Migration complete:
  - Migrated: 50 cases
  - Unchanged: 100 cases

Validating migration...
✅ All cases have complete metadata
```

**Migration Error:**
```
Starting CBR metadata migration...
❌ Error connecting to ChromaDB: [Errno 2] No such file or directory: './db'
```

---

## Production Deployment Runbook

### Pre-Migration Phase

#### 1. Create Backup

**⚠️ CRITICAL: Always backup before migration**

```bash
# Stop any running CBR MCP Server instances
# (Check process manager or close applications using the server)

# Create timestamped backup
BACKUP_DIR="./backups/pre-metadata-migration-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r ./db "$BACKUP_DIR/"

# Verify backup
ls -lh "$BACKUP_DIR/db"
echo "Backup created at: $BACKUP_DIR"
```

**Backup Verification:**
```bash
# Verify backup size matches original
du -sh ./db
du -sh "$BACKUP_DIR/db"

# Verify collection files present
ls "$BACKUP_DIR/db/"
```

#### 2. Validate Pre-Migration State

**Run validation to establish baseline:**

```bash
python validate_metadata.py --db-path ./db --collection code_solutions_case_base
```

**Expected Pre-Migration Output:**
```
Validating metadata for collection: code_solutions_case_base
Database path: ./db

Validation Results:
==================================================
Total cases: 150
✗ Cases missing category field: 150/150
✗ Cases missing subcategory field: 150/150
✗ Cases missing tags field: 150/150
✓ All category values valid: 0/150
✓ All subcategory-category pairs valid: 0/150
✓ All tags formats valid: 0/150

Total validation errors: 450
```

**⚠️ Expected Errors:** Missing category/subcategory/tags fields are normal before migration.

#### 3. Stop Active Connections

**Ensure no active connections to ChromaDB:**

```bash
# Check for running processes
ps aux | grep cbr-mcp-server
ps aux | grep main_cbr_rag

# Stop processes if found
# Example (adjust based on your process management):
kill -TERM <pid>

# Verify no ChromaDB lock files
ls ./db/*.lock 2>/dev/null || echo "No lock files (good)"
```

### Migration Phase

#### 4. Execute Migration

**Run the migration script:**

```bash
# Activate Python environment (if using virtualenv)
source venv/bin/activate

# Run migration
python migrate_metadata.py

# Expected duration: ~1-2 seconds per 100 cases
```

**Monitor Output:**
```
Starting CBR metadata migration...
Found 150 total cases in collection

Migrating cases...
[Processing occurs here - may take 1-2 seconds per 100 cases]

Migration complete:
  - Migrated: 150 cases
  - Unchanged: 0 cases

Validating migration...
✅ All cases have complete metadata
```

**Success Criteria:**
- Exit code: 0
- Migrated count matches total cases (or 0 if already migrated)
- Validation shows "All cases have complete metadata"

#### 5. Post-Migration Validation

**Run comprehensive validation:**

```bash
python validate_metadata.py --db-path ./db --collection code_solutions_case_base
```

**Expected Post-Migration Output:**
```
Validating metadata for collection: code_solutions_case_base
Database path: ./db

Validation Results:
==================================================
Total cases: 150
✓ All cases have category field: 150/150
✓ All cases have subcategory field: 150/150
✓ All cases have tags field: 150/150
✓ All category values valid: 150/150
✓ All subcategory-category pairs valid: 150/150
✓ All tags formats valid: 150/150

All validations passed! ✓
```

**Success Criteria:**
- All validation checks pass (✓)
- No validation errors reported
- Exit code: 0

### Post-Migration Phase

#### 6. Verify Service Functionality

**Test category-based retrieval:**

```bash
# Start CBR MCP Server
cbr-mcp-server

# In another terminal, test category search
# (Use your MCP client or test script)
```

**Sample Test Queries:**
```python
# Test 1: Search code/firebase-auth category
category_results = await retriever.search_by_category(
    category="code",
    subcategory="firebase-auth",
    limit=5
)
assert len(category_results) > 0
assert all(r["category"] == "code" for r in category_results)

# Test 2: Search orchestration/remediation category
orchestration_results = await retriever.search_by_category(
    category="orchestration",
    subcategory="remediation",
    limit=5
)
assert len(orchestration_results) > 0

# Test 3: Backward compatibility (no category filter)
general_results = await retriever.retrieve(
    query="authentication example",
    top_k=5
)
assert len(general_results) > 0
```

#### 7. Performance Verification

**Check query performance:**

```bash
# Test query latency (should be similar to pre-migration)
time python -c "
from retriever import ProductionCBRRetriever
import asyncio

async def test():
    retriever = ProductionCBRRetriever()
    results = await retriever.search_by_category('code', limit=10)
    print(f'Found {len(results)} results')

asyncio.run(test())
"
```

**Expected Performance:**
- Query latency: <200ms for typical queries
- No significant slowdown compared to pre-migration
- Memory usage: Similar to pre-migration

#### 8. Update Documentation

**Document migration completion:**

```bash
# Create migration record
cat >> ./Documentation/MIGRATION_HISTORY.md << EOF
## Metadata Enhancement Migration

**Date:** $(date +%Y-%m-%d)
**Database:** ./db
**Collection:** code_solutions_case_base
**Cases Migrated:** <count>
**Backup Location:** $BACKUP_DIR
**Status:** Completed Successfully
**Validated:** Yes

EOF
```

### Timeline and Downtime Expectations

**Estimated Timeline:**

| Phase | Duration | Downtime Required |
|-------|----------|-------------------|
| Backup | 1-2 minutes | No |
| Pre-validation | 1 minute | No |
| Stop services | 30 seconds | **Yes** |
| Migration | 1-2 seconds per 100 cases | **Yes** |
| Validation | 1 minute | **Yes** |
| Restart services | 30 seconds | **Yes** |
| **Total Downtime** | **~5-10 minutes** | - |

**For 1000 cases:**
- Migration: ~10-20 seconds
- Total downtime: ~5-10 minutes

**For 10,000 cases:**
- Migration: ~100-200 seconds (~2-3 minutes)
- Total downtime: ~10-15 minutes

### Rollback Procedures

**If migration fails or issues are detected:**

#### Rollback Step 1: Stop Services

```bash
# Stop any running CBR MCP Server instances
ps aux | grep cbr-mcp-server | awk '{print $2}' | xargs kill -TERM
```

#### Rollback Step 2: Restore Backup

```bash
# Identify backup directory
ls -l ./backups/
# Example: pre-metadata-migration-20251027-143022

# Remove current database
rm -rf ./db

# Restore from backup
cp -r ./backups/pre-metadata-migration-TIMESTAMP/db ./db

# Verify restoration
python validate_metadata.py --db-path ./db
```

#### Rollback Step 3: Verify Service

```bash
# Restart CBR MCP Server
cbr-mcp-server

# Test basic retrieval
# (Use your standard test procedure)
```

#### Rollback Step 4: Document Rollback

```bash
cat >> ./Documentation/MIGRATION_HISTORY.md << EOF
**Rollback Performed:** $(date +%Y-%m-%d)
**Reason:** <describe issue>
**Backup Restored:** <backup directory>
**Status:** Rolled back to pre-migration state

EOF
```

---

## Troubleshooting Guide

### Common Migration Issues

#### Issue 1: ChromaDB Connection Failed

**Symptom:**
```
❌ Error connecting to ChromaDB: [Errno 2] No such file or directory: './db'
```

**Cause:** Database directory does not exist or incorrect path

**Solution:**
```bash
# Check if database directory exists
ls -la ./db

# If missing, verify you're in the correct project directory
pwd

# Verify ChromaDB installation
python -c "import chromadb; print(chromadb.__version__)"

# If database truly doesn't exist, initialize it first
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
print('Database initialized')
"
```

#### Issue 2: Collection Not Found

**Symptom:**
```
❌ Error connecting to ChromaDB: Collection 'code_solutions_case_base' not found
```

**Cause:** Collection name mismatch or collection doesn't exist

**Solution:**
```bash
# List available collections
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collections = client.list_collections()
for c in collections:
    print(f'Collection: {c.name}')
"

# Update script with correct collection name
# Or create collection if it doesn't exist
```

#### Issue 3: Partial Migration (Some Cases Failed)

**Symptom:**
```
Migration complete:
  - Migrated: 120 cases
  - Unchanged: 30 cases

Validating migration...
⚠️  Warning: 10 cases missing metadata
  - case-id-1
  - case-id-2
  ...
```

**Cause:** Some cases failed to migrate due to data issues

**Solution:**
```bash
# Re-run migration (idempotent - will only migrate remaining cases)
python migrate_metadata.py

# If still failing, investigate specific cases
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
result = collection.get(ids=['case-id-1'], include=['documents', 'metadatas'])
print(result)
"

# Check for missing document content or malformed metadata
```

#### Issue 4: Validation Errors After Migration

**Symptom:**
```
Validation Results:
✗ Invalid category values: 5/150
✗ Invalid subcategory-category pairs: 3/150

Validation Errors:
Invalid Category:
  - case-123
  - case-456
```

**Cause:** Pattern matching assigned invalid categories

**Solution:**
```bash
# Examine problematic cases
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
result = collection.get(ids=['case-123'], include=['documents', 'metadatas'])
print('Document:', result['documents'][0])
print('Metadata:', result['metadatas'][0])
"

# Fix manually if needed
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
collection.update(
    ids=['case-123'],
    metadatas=[{
        'category': 'code',
        'subcategory': 'general',
        'tags': 'python,api'
    }]
)
print('Updated case-123')
"

# Re-run validation
python validate_metadata.py
```

### ChromaDB Connection Problems

#### Problem: Permission Denied

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: './db/chroma.sqlite3'
```

**Solution:**
```bash
# Check file permissions
ls -la ./db

# Fix permissions
chmod -R u+rw ./db

# Verify ownership
chown -R $USER:$USER ./db
```

#### Problem: Database Locked

**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Check for active connections
lsof ./db/chroma.sqlite3

# Kill processes using the database
ps aux | grep cbr-mcp-server
kill -TERM <pid>

# Remove lock files if safe
rm ./db/*.lock

# Re-run migration
python migrate_metadata.py
```

#### Problem: Corrupted Database

**Symptom:**
```
sqlite3.DatabaseError: database disk image is malformed
```

**Solution:**
```bash
# Restore from backup immediately
rm -rf ./db
cp -r ./backups/latest/db ./db

# If no backup available, try ChromaDB recovery
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
client._client._db.execute('PRAGMA integrity_check')
"

# Contact support if recovery needed
```

### Metadata Validation Failures

#### Failure: Missing Required Fields

**Symptom:**
```
✗ Cases missing category field: 10/150
✗ Cases missing subcategory field: 10/150
```

**Diagnostic Steps:**
```bash
# Check if migration completed
python -c "
import chromadb
client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
result = collection.get(include=['metadatas'], limit=1)
print('Sample metadata:', result['metadatas'][0])
"

# Re-run migration
python migrate_metadata.py
```

#### Failure: Invalid Category Values

**Symptom:**
```
✗ Invalid category values: 5/150

Validation Errors:
Invalid Category:
  - example-case-1: category='code-example'
```

**Valid Categories:**
- `code`
- `orchestration`
- `best-practice`
- `anti-pattern`

**Fix:**
```python
# Manual correction script
import chromadb

client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')

# Get cases with invalid categories
results = collection.get(include=['metadatas'])
invalid_ids = []
invalid_metadatas = []

for i, metadata in enumerate(results['metadatas']):
    if metadata.get('category') not in ['code', 'orchestration', 'best-practice', 'anti-pattern']:
        # Fix category
        metadata['category'] = 'code'  # Default to code
        if 'subcategory' not in metadata:
            metadata['subcategory'] = 'general'
        invalid_ids.append(results['ids'][i])
        invalid_metadatas.append(metadata)

# Update invalid cases
if invalid_ids:
    collection.update(ids=invalid_ids, metadatas=invalid_metadatas)
    print(f"Fixed {len(invalid_ids)} invalid categories")
```

#### Failure: Invalid Subcategory-Category Pairs

**Symptom:**
```
✗ Invalid subcategory-category pairs: 3/150
```

**Valid Pairs (excerpt):**
```python
CATEGORY_SUBCATEGORIES = {
    "code": ["firebase-auth", "react-components", "api-routes", "database", "testing", "general"],
    "orchestration": ["remediation", "planning", "delegation", "verification", "completion"],
    "best-practice": ["planning", "verification", "error-handling"],
    "anti-pattern": ["completion-bias", "verification-skip", "protocol-violation"]
}
```

**Fix:**
```python
# Correct invalid pairs
import chromadb

VALID_PAIRS = {
    "code": ["firebase-auth", "react-components", "api-routes", "database", "testing", "general"],
    "orchestration": ["remediation", "planning", "delegation", "verification", "completion"],
    "best-practice": ["planning", "verification", "error-handling"],
    "anti-pattern": ["completion-bias", "verification-skip", "protocol-violation"]
}

client = chromadb.PersistentClient(path='./db')
collection = client.get_collection('code_solutions_case_base')
results = collection.get(include=['metadatas'])

fix_ids = []
fix_metadatas = []

for i, metadata in enumerate(results['metadatas']):
    category = metadata.get('category')
    subcategory = metadata.get('subcategory')

    if category and subcategory:
        valid_subs = VALID_PAIRS.get(category, [])
        if subcategory not in valid_subs:
            # Fix to 'general' for code, first valid subcategory for others
            metadata['subcategory'] = 'general' if category == 'code' else valid_subs[0]
            fix_ids.append(results['ids'][i])
            fix_metadatas.append(metadata)

if fix_ids:
    collection.update(ids=fix_ids, metadatas=fix_metadatas)
    print(f"Fixed {len(fix_ids)} invalid subcategory pairs")
```

### Performance Issues During Migration

#### Issue: Migration Taking Too Long

**Symptom:**
```
# Migration appears stuck or very slow
Migrating cases...
[No progress for several minutes]
```

**Diagnostic:**
```bash
# Check system resources
top
# Look for high CPU or memory usage

# Check database size
du -sh ./db

# Monitor migration progress (add logging)
# Modify migrate_metadata.py temporarily:
# Add print statements in the loop to show progress
```

**Solutions:**

1. **Batch Size Optimization** (if very large case base):
```python
# Process in smaller batches
BATCH_SIZE = 100
for i in range(0, len(ids_to_update), BATCH_SIZE):
    batch_ids = ids_to_update[i:i+BATCH_SIZE]
    batch_metadatas = metadatas_to_update[i:i+BATCH_SIZE]
    collection.update(ids=batch_ids, metadatas=batch_metadatas)
    print(f"Processed {i+len(batch_ids)}/{len(ids_to_update)}")
```

2. **Increase System Resources:**
```bash
# Close other applications
# Ensure sufficient RAM available
free -h

# Check disk I/O
iostat -x 1
```

#### Issue: High Memory Usage

**Symptom:**
```
# System memory usage spikes during migration
```

**Solution:**
```bash
# Process in smaller batches
# Modify migrate_metadata.py to process incrementally

# Or increase available memory
# Close other applications
# Consider using a machine with more RAM for large migrations
```

### Recovery Procedures for Failed Migrations

#### Recovery Procedure 1: Migration Interrupted

**Scenario:** Migration interrupted by system crash or process kill

**Recovery Steps:**

```bash
# 1. Verify database integrity
python -c "
import chromadb
try:
    client = chromadb.PersistentClient(path='./db')
    collection = client.get_collection('code_solutions_case_base')
    count = collection.count()
    print(f'Database accessible. {count} cases found.')
except Exception as e:
    print(f'Database issue: {e}')
"

# 2. Re-run migration (idempotent)
python migrate_metadata.py

# 3. Validate results
python validate_metadata.py

# 4. If database corrupted, restore from backup
rm -rf ./db
cp -r ./backups/latest/db ./db
```

#### Recovery Procedure 2: Validation Failures After Migration

**Scenario:** Migration completes but validation shows errors

**Recovery Steps:**

```bash
# 1. Identify issue types
python validate_metadata.py > validation_report.txt
cat validation_report.txt

# 2. If minor issues (invalid values), fix manually
# See "Metadata Validation Failures" section above

# 3. If major issues (widespread missing fields), rollback and investigate
rm -rf ./db
cp -r ./backups/latest/db ./db

# 4. Debug migration logic
python -c "
from metadata_migration import MetadataMigration
migrator = MetadataMigration()

# Test pattern detection
test_text = 'Example problematic case text'
category, subcategory = migrator.detect_category_subcategory(test_text)
print(f'Detected: {category}/{subcategory}')
"

# 5. Re-run migration after fixes
python migrate_metadata.py
python validate_metadata.py
```

#### Recovery Procedure 3: Complete Rollback Required

**Scenario:** Migration caused unexpected issues requiring full rollback

**Rollback Steps:**

```bash
# 1. Stop all services
ps aux | grep cbr | awk '{print $2}' | xargs kill -TERM

# 2. Document issue
echo "Rollback: $(date) - Reason: <issue>" >> ./Documentation/MIGRATION_HISTORY.md

# 3. Remove current database
rm -rf ./db

# 4. Restore from backup
BACKUP_DIR=$(ls -t ./backups | head -1)
cp -r "./backups/$BACKUP_DIR/db" ./db

# 5. Verify restoration
python validate_metadata.py
# Should show pre-migration state (missing fields expected)

# 6. Test service
cbr-mcp-server
# Run your standard test suite

# 7. Investigate root cause before retrying
```

---

## Command Reference

### migrate_metadata.py

**Purpose:** Migrate existing cases to new metadata structure

**Usage:**
```bash
python migrate_metadata.py
```

**Parameters:**
- None (uses hardcoded defaults)
- Database path: `./db` (modify in script for custom path)
- Collection: `code_solutions_case_base` (modify in script for custom collection)

**Exit Codes:**
- `0`: Success (all cases have complete metadata)
- `1`: Error (connection failed or validation errors)

**Output Format:**
```
Starting CBR metadata migration...
Found <N> total cases in collection

Migrating cases...

Migration complete:
  - Migrated: <N> cases
  - Unchanged: <N> cases

Validating migration...
✅ All cases have complete metadata
```

**Idempotency:** Safe to run multiple times; skips already-migrated cases

---

### validate_metadata.py

**Purpose:** Validate metadata integrity in ChromaDB collection

**Usage:**
```bash
# Default database and collection
python validate_metadata.py

# Custom database path
python validate_metadata.py --db-path /custom/path/to/db

# Custom collection name
python validate_metadata.py --collection custom_collection_name

# Both custom
python validate_metadata.py --db-path /custom/path --collection custom_collection
```

**Parameters:**
- `--db-path`: Path to ChromaDB database directory (default: `./db`)
- `--collection`: Name of ChromaDB collection (default: `code_solutions_case_base`)

**Exit Codes:**
- `0`: Success (all validations passed)
- `1`: Failure (validation errors found or connection failed)

**Validation Checks:**

1. **Field Presence:**
   - All cases have `category` field
   - All cases have `subcategory` field
   - All cases have `tags` field

2. **Value Validity:**
   - Category values in `["code", "orchestration", "best-practice", "anti-pattern"]`
   - Subcategory matches category (valid pairs)
   - Tags format: comma-separated lowercase strings

**Output Format:**
```
Validation Results:
==================================================
Total cases: <N>
✓ All cases have category field: <N>/<N>
✓ All cases have subcategory field: <N>/<N>
✓ All cases have tags field: <N>/<N>
✓ All category values valid: <N>/<N>
✓ All subcategory-category pairs valid: <N>/<N>
✓ All tags formats valid: <N>/<N>

All validations passed! ✓
```

**Error Details:**
```
Validation Errors:
--------------------------------------------------

Invalid Category:
  - case-id-1
  - case-id-2
  ... and N more

Total validation errors: <N>
```

---

## Validation Reference

### Valid Category Values

```python
VALID_CATEGORIES = [
    "code",
    "orchestration",
    "best-practice",
    "anti-pattern"
]
```

### Valid Category-Subcategory Pairs

#### Code Category
```python
"code": [
    "firebase-auth",      # Firebase authentication
    "react-components",   # React component patterns
    "api-routes",         # API endpoint implementations
    "database",           # Database operations
    "testing",            # Test patterns
    "general"             # Uncategorized code examples
]
```

#### Orchestration Category
```python
"orchestration": [
    "remediation",        # Remediation Protocol patterns
    "planning",           # Planning and decomposition
    "delegation",         # Agent delegation patterns
    "verification",       # Karen verification workflows
    "completion"          # Task completion protocols
]
```

#### Best-Practice Category
```python
"best-practice": [
    "planning",           # How to structure plans
    "verification",       # Verification protocols
    "error-handling"      # Error recovery patterns
]
```

#### Anti-Pattern Category
```python
"anti-pattern": [
    "completion-bias",    # Premature completion patterns
    "verification-skip",  # Skipped verification issues
    "protocol-violation"  # Protocol violations
]
```

### Tags Format

**Valid:**
```
tags: "react,firebase,typescript,authentication"
tags: "python,api,async"
tags: ""  # Empty is valid
```

**Invalid:**
```
tags: "React,Firebase"  # Mixed case
tags: "react, ,firebase"  # Empty tag in list
tags: "REACT,FIREBASE"  # Uppercase
```

**Tag Validation Rules:**
1. Must be a string
2. Comma-separated values
3. All lowercase
4. No empty tags after splitting
5. Empty string is valid (no tags)

---

## Support and Resources

### Getting Help

**If you encounter issues not covered in this guide:**

1. Check the technical specification: `.agent-os/specs/2025-10-27-cbr-metadata-enhancement/sub-specs/tech_spec.md`
2. Review test cases: `test_metadata_migration.py`, `test_migration_integration.py`
3. Examine migration implementation: `metadata_migration.py`
4. Create a detailed bug report including:
   - Migration command used
   - Full error output
   - Database state (case count, sample metadata)
   - System environment (Python version, OS)

### Related Documentation

- **Migration Implementation:** `metadata_migration.py`
- **Validation Implementation:** `validate_metadata.py`
- **Technical Specification:** `.agent-os/specs/2025-10-27-cbr-metadata-enhancement/sub-specs/tech_spec.md`
- **Test Suite:** `test_metadata_migration.py`, `test_migration_integration.py`
- **Product Mission:** `.agent-os/product/mission.md`

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-28 | Initial migration guide |

---

**End of Migration Guide**
