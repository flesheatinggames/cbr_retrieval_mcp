# Spec Requirements Document

> Spec: Case Base Modular Refactoring
> Created: 2025-10-28
> Status: Planning

## Overview

Refactor the monolithic case_base.py file (5,768 lines, 49 cases) into a modular, maintainable structure following the existing pattern established in cases/rust/. This refactoring will organize cases by technology domain (web, orchestration, security) into discrete files, implement a dynamic loader for automatic case discovery, and enhance all cases with proper metadata (category, subcategory, tags) while maintaining backward compatibility.

## User Stories

### Developer Case Management

As a developer maintaining the CBR case base, I want case files organized by technology and domain so that I can easily locate, update, and add code examples without navigating a massive 5,768-line monolithic file.

**Workflow:** Developer needs to add a new Firebase Authentication example. Instead of scrolling through 5,768 lines in case_base.py, they navigate to cases/firebase/firebase_auth_cases.py (containing only Firebase Auth examples) and add their case to the FIREBASE_AUTH_CASES list. The dynamic loader automatically includes the new case on next import.

**Problem Solved:** Eliminates cognitive overhead of maintaining large monolithic files, reduces merge conflicts in version control, and makes case curation significantly more efficient.

### System Administrator Selective Loading

As a system administrator deploying CBR MCP Server, I want selective case loading capabilities so that I can optimize memory usage and deployment size for specific contexts (e.g., frontend-only deployment doesn't need orchestration examples).

**Workflow:** Administrator configures deployment to load only specific technology cases for a frontend-focused AI agent. The dynamic loader reads configuration and imports only the required case modules, reducing memory footprint by ~60% by excluding orchestration and security cases.

**Problem Solved:** Enables deployment flexibility and resource optimization for different use cases without code changes.

### Case Curator Metadata Enhancement

As a case curator improving retrieval accuracy, I want all cases to have consistent category, subcategory, and tags metadata so that semantic search and category-based retrieval return more relevant results.

**Workflow:** Curator reviews cases/react/react_components_cases.py and adds metadata: category="react", subcategory="components", tags=["hooks", "state", "typescript"]. The retriever.py module uses this metadata to improve similarity scoring and filtering.

**Problem Solved:** Enhances retrieval accuracy by providing structured metadata for semantic understanding beyond embeddings alone.

## Spec Scope

1. **Modular Case File Structure** - Split case_base.py into 19 discrete case files organized under cases/firebase/, cases/react/, cases/nextjs/, cases/bootstrap/, cases/orchestration/, and additional technology directories (following existing cases/rust/ pattern)

2. **Dynamic Case Loader** - Create cases/__init__.py that automatically discovers and imports all *_cases.py modules from subdirectories, exposing a consolidated ALL_CASES list

3. **Metadata Enhancement** - Add category, subcategory, and tags fields to all 49 cases during the refactoring process

4. **Backward Compatibility Wrapper** - Maintain case_base.py as a compatibility shim that imports from cases module, preserving case_base.CASE_BASE for existing code

5. **Documentation Updates** - Update all references to case organization in README.md, CLAUDE.md, and inline documentation

## Out of Scope

- Modifying case content or solutions (only reorganization and metadata addition)
- Changing ChromaDB storage structure or embedding generation
- Altering CBR retrieval algorithms in retriever.py
- Performance optimization beyond modular loading benefits
- Creating new cases or removing existing ones
- Changing the MCP tool interfaces

## Expected Deliverable

1. **19 New Case Module Files Created:**
   - cases/firebase/firebase_auth_cases.py (5 cases)
   - cases/firebase/firebase_firestore_cases.py (4 cases)
   - cases/nextjs/nextjs_routing_cases.py (3 cases)
   - cases/nextjs/nextjs_api_cases.py (3 cases)
   - cases/react/react_components_cases.py (6 cases)
   - cases/bootstrap/bootstrap_ui_cases.py (4 cases)
   - cases/webdev/webdev_state_management_cases.py (3 cases)
   - cases/webdev/webdev_forms_validation_cases.py (3 cases)
   - cases/webdev/webdev_api_integration_cases.py (2 cases)
   - cases/webdev/webdev_error_handling_cases.py (3 cases)
   - cases/webdev/webdev_testing_cases.py (2 cases)
   - cases/webdev/webdev_deployment_cases.py (2 cases)
   - cases/orchestration/orchestration_planning_cases.py (2 cases)
   - cases/orchestration/orchestration_remediation_cases.py (1 case)
   - cases/orchestration/orchestration_delegation_cases.py (1 case)
   - cases/orchestration/orchestration_verification_cases.py (1 case)
   - cases/orchestration/orchestration_completion_cases.py (1 case)
   - cases/security/security_auth_cases.py (2 cases)
   - cases/security/security_validation_cases.py (2 cases)

2. **Dynamic Loader Implemented** - cases/__init__.py with automatic module discovery and ALL_CASES list aggregation

3. **Metadata Complete** - All 49 cases have category, subcategory, and tags metadata

4. **Backward Compatibility** - case_base.py imports from cases and exposes CASE_BASE for existing integrations

5. **Tests Passing** - All existing tests pass with new modular structure

6. **Documentation Updated** - README.md, CLAUDE.md reflect new case organization

## Spec Documentation

- Tasks: @.agent-os/specs/2025-10-28-case-base-modular-refactoring/tasks.md
- Technical Specification: @.agent-os/specs/2025-10-28-case-base-modular-refactoring/sub-specs/tech-spec.md
- Data Specification: @.agent-os/specs/2025-10-28-case-base-modular-refactoring/sub-specs/data-spec.md
- Tests Specification: @.agent-os/specs/2025-10-28-case-base-modular-refactoring/sub-specs/tests.md
