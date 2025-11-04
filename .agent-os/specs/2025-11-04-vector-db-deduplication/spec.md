# Spec Requirements Document

> Spec: Vector Database Deduplication and Smart Updates
> Created: 2025-11-04
> Status: Planning

## Overview

Implement content-based deduplication and smart incremental updates for the setup_vectordb.py script to prevent data loss, eliminate duplicate case loading, and enable safe incremental database updates.

## User Stories

### Data Integrity Protection

As a CBR system maintainer, I want the vector database setup script to use content-based identification instead of sequential IDs, so that loading cases in different orders or subsets doesn't create duplicates or cause data loss.

**Detailed Workflow:**
When I run `setup_vectordb.py` multiple times with different case selections, the script should:
- Generate stable, content-based IDs (e.g., hash of problem + solution)
- Detect when a case already exists in the database
- Skip cases that are already present instead of creating duplicates
- Add only genuinely new cases to the database

This solves the current problem where:
- Sequential IDs (`id0`, `id1`, `id2...`) create collisions when different case sets are loaded
- The same case loaded at different positions gets different IDs
- There's no way to detect if case content already exists

### Incremental Updates Without Data Loss

As a CBR system maintainer, I want to add new cases to the database without deleting existing cases, so that I can grow the case base incrementally without risking data loss.

**Detailed Workflow:**
When I have 100 cases in the database and want to add 50 more cases (150 total), the script should:
- Identify which of the 150 cases are already in the database
- Add only the 50 new cases
- Keep all 100 existing cases intact
- Report statistics: "Added 50 new cases, skipped 100 existing cases, total now 150"

This solves the current problem where:
- When `current_count < len(CASE_BASE)`, the entire collection is deleted (lines 288-315)
- Loading 150 cases when 100 exist causes all 100 to be deleted and rebuilt
- No incremental update capability exists

### Database Validation

As a CBR system maintainer, I want to validate database integrity without modifying it, so that I can verify the database contents match my case files.

**Detailed Workflow:**
When I run `setup_vectordb.py --validate`, the script should:
- Read all cases from the case files
- Compare with what's in the ChromaDB database
- Report discrepancies:
  - Cases in database but not in files
  - Cases in files but not in database
  - Cases with content mismatches
- Exit without modifying the database

This solves the need for:
- Verifying database integrity after updates
- Detecting cases that may have been manually deleted
- Identifying when case files have changed

## Spec Scope

1. **Content-Based ID Generation** - Replace sequential IDs with SHA-256 hashes of case content (problem + solution)
2. **Smart Deduplication Logic** - Detect existing cases by content hash before adding to database
3. **Incremental Update Mode** - Add new cases without deleting existing ones using ChromaDB upsert or add-only logic
4. **Validation Mode** - `--validate` flag to check database integrity without modifications
5. **Enhanced User Feedback** - Detailed statistics showing added, skipped, existing, and total case counts

## Out of Scope

- Changes to ChromaDB schema or collection structure
- Changes to API endpoints or MCP tools
- Migration of existing database IDs (existing databases can be rebuilt with `--force`)
- Module-based filtering implementation (already noted as TODO in line 198)
- Changes to case loading logic in `load_all_cases()`

## Expected Deliverable

1. **Running `setup_vectordb.py` twice with same cases:**
   - First run: "Added 100 cases"
   - Second run: "Skipped 100 existing cases, added 0 new cases, total 100"

2. **Running `setup_vectordb.py` with subset then full set:**
   - First run with 50 cases: "Added 50 cases"
   - Second run with 150 cases: "Skipped 50 existing cases, added 100 new cases, total 150"

3. **Running `setup_vectordb.py --validate`:**
   - Output showing database integrity report
   - Cases in DB: 150
   - Cases in files: 150
   - Matches: 150
   - Missing from DB: 0
   - Extra in DB: 0

## Spec Documentation

- Technical Specification: @.agent-os/specs/2025-11-04-vector-db-deduplication/sub-specs/tech-spec.md
- Tests Specification: @.agent-os/specs/2025-11-04-vector-db-deduplication/sub-specs/tests.md
