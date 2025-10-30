# Spec Requirements Document

> Spec: CBR Metadata Enhancement
> Created: 2025-10-27
> Status: Planning

## Overview

Enhance the CBR MCP Server's case organization and retrieval capabilities by implementing hierarchical category taxonomy and tag-based filtering. This will enable AI agents to more precisely discover relevant code examples through structured categorization (code, orchestration, best-practice, anti-pattern) and flexible tag-based queries.

## User Stories

### Enhanced Case Organization

As a Claude Code agent, I want to retrieve code examples organized by hierarchical categories (category + subcategory), so that I can quickly narrow my search to relevant domains like "orchestration/remediation" or "code/firebase-auth" without sifting through unrelated examples.

**Workflow:** When an agent queries for orchestration patterns, the system filters to only orchestration-related cases, then further refines to specific subcategories like remediation or planning flows. The agent receives focused results rather than mixed categories.

### Tag-Based Discovery

As a Claude Code agent, I want to filter cases by multiple tags using OR logic, so that I can find examples matching any of several related technologies (e.g., "React" OR "Firebase" OR "TypeScript").

**Workflow:** When searching for authentication examples, the agent can specify tags like ["authentication", "firebase", "security"] and receive all cases tagged with any of these terms, enabling broader discovery of related solutions.

### Backward-Compatible Migration

As the CBR system administrator, I want existing cases to be automatically migrated to the new metadata structure with intelligent categorization, so that the enhanced filtering capabilities work immediately without manual data cleanup.

**Workflow:** A migration script analyzes existing case problem texts, detects patterns like "Firebase" or "React component", and assigns appropriate categories/subcategories/tags. All existing cases become searchable through the new taxonomy without manual intervention.

## Spec Scope

1. **Hierarchical Category Structure** - Implement two-level taxonomy (category/subcategory) with predefined categories: code, orchestration, best-practice, anti-pattern
2. **Tag Metadata Support** - Add tags field to ChromaDB metadata with comma-separated string storage
3. **Category Filtering** - Update search_by_category to use ChromaDB where filters for category and subcategory
4. **Migration Script** - Create automated migration for existing cases with pattern-based categorization
5. **Updated MCP Tools** - Enhance cbr_retrieve and cbr_search_category to support new filtering options

## Out of Scope

- Tag filtering implementation (deferred to Phase 2)
- AND/NOT tag logic (OR logic only in future phases)
- Multi-collection category management (single collection approach maintained)
- User interface for category management (API-only implementation)
- Full-text search beyond vector similarity

## Expected Deliverable

1. AI agents can query cases by hierarchical category (e.g., "orchestration/remediation")
2. All existing cases have been migrated to the new metadata structure with auto-detected categories
3. The get_categories resource returns hierarchical category structure with subcategory counts
4. ChromaDB metadata includes category, subcategory, and tags fields for all cases
5. Backward compatibility maintained - existing queries continue to work without modification

## Spec Documentation

- Tasks: @.agent-os/specs/2025-10-27-cbr-metadata-enhancement/tasks.md
- Technical Specification: @.agent-os/specs/2025-10-27-cbr-metadata-enhancement/sub-specs/tech_spec.md
- Database Schema: @.agent-os/specs/2025-10-27-cbr-metadata-enhancement/sub-specs/data_spec.md
- Tests Specification: @.agent-os/specs/2025-10-27-cbr-metadata-enhancement/sub-specs/tests.md
