# Spec Requirements Document

> Spec: Metadata Storage Bug Fix
> Created: 2025-11-04
> Status: Planning

## Overview

Fix critical bug in vector database population that discards case metadata (category, subcategory, tags), causing category-based search functionality to fail completely. The bug prevents AI agents from filtering code examples by domain, rendering the core category-based search feature unusable.

## User Stories

### Story 1: AI Agent Category Search

As a Claude Code agent, I want to search for code examples by category (e.g., "orchestration", "firebase", "rust"), so that I can find domain-specific patterns relevant to my current planning task.

**Current Broken Workflow:**
1. Agent calls `cbr_search_category(category="orchestration")`
2. ChromaDB attempts to filter by `{"category": "orchestration"}`
3. Query fails because metadata only contains `{"problem": "..."}` - no category field exists
4. Agent receives error: "Failed to query cases for category 'orchestration'"
5. Agent cannot access any category-filtered code examples

**Expected Fixed Workflow:**
1. Agent calls `cbr_search_category(category="orchestration")`
2. ChromaDB successfully filters by `{"category": "orchestration"}` using stored metadata
3. Query returns 24 orchestration cases with full metadata
4. Agent receives relevant orchestration pattern examples for planning

### Story 2: Subcategory Filtering

As a Claude Code agent, I want to search for code examples by both category and subcategory (e.g., "orchestration" + "planning"), so that I can find highly specific patterns for the exact phase of work I'm planning.

**Workflow:**
1. Agent calls `cbr_search_category(category="orchestration", subcategory="planning")`
2. ChromaDB filters by both category AND subcategory
3. Query returns orchestration cases specifically about planning patterns
4. Agent receives precise examples for orchestration planning phase

### Story 3: Tag-Based Discovery

As a Claude Code agent, I want case metadata to include tags, so that I can understand the technical context and related concepts for each code example I retrieve.

**Workflow:**
1. Agent retrieves case with ID "id42"
2. Case metadata includes: `category: "orchestration"`, `subcategory: "planning"`, `tags: ["orchestration", "planning", "tdd", "rust", "database"]`
3. Agent understands the case applies to orchestration planning for Rust database work using TDD
4. Agent can decide if this case is relevant to current technical context

## Spec Scope

1. **Fix Metadata Storage in setup_vectordb.py** - Modify lines 284 and 312 to store complete case metadata (category, subcategory, tags, problem) instead of only problem field
2. **Database Migration Strategy** - Provide mechanism to update existing database with 103 cases to include full metadata without data loss
3. **Metadata Validation** - Ensure all required fields are present in case data before storage
4. **Backward Compatibility** - Maintain compatibility with existing query patterns that only use problem field
5. **Test Coverage** - Comprehensive tests for metadata storage, retrieval, and category filtering

## Out of Scope

- Changing the case file structure (cases are already correct with full metadata)
- Modifying the `load_all_cases()` function (already loads metadata correctly)
- Changing the ChromaDB schema or collection configuration
- Altering the embedding generation process (embeddings remain based on problem text)
- Modifying the MCP tool interface for `cbr_search_category`
- Performance optimization (focus is correctness, not performance)

## Expected Deliverable

After this spec is implemented:

1. **In Browser/CLI**: Run `python scripts/utilities/setup_vectordb.py --force` and verify:
   - Script successfully stores 103 cases with full metadata
   - Console output confirms all cases loaded with metadata fields
   - No errors during database population

2. **In MCP Server**: Start server and verify:
   - `cbr_search_category(category="orchestration")` returns 24 orchestration cases
   - Each returned case includes category, subcategory, and tags in metadata
   - `cbr_search_category(category="firebase")` returns firebase cases
   - `cbr_search_category(category="rust")` returns rust cases
   - Subcategory filtering works: `cbr_search_category(category="orchestration", subcategory="planning")` returns only planning cases

3. **In Tests**: Run pytest and verify:
   - All metadata storage tests pass
   - Category filtering tests pass
   - Database migration tests pass
   - No regressions in existing test suite

## Spec Documentation

- Tasks: @.agent-os/specs/2025-11-04-metadata-storage-bug-fix/tasks.md
- Technical Specification: @.agent-os/specs/2025-11-04-metadata-storage-bug-fix/sub-specs/tech-spec.md
- Data Specification: @.agent-os/specs/2025-11-04-metadata-storage-bug-fix/sub-specs/data-spec.md
- Tests Specification: @.agent-os/specs/2025-11-04-metadata-storage-bug-fix/sub-specs/tests.md
