# Data Specification

This is the data specification for the spec detailed in @.agent-os/specs/2025-10-28-case-base-modular-refactoring/spec.md

> Created: 2025-10-28
> Version: 1.0.0

## Overview

This refactoring is **code organization only** - there are no database schema changes, API modifications, or data model alterations. The ChromaDB vector database structure remains unchanged, and case retrieval behavior is preserved.

## Data Models

### Case Dictionary Schema (Enhanced with Metadata)

**Current Schema** (in existing case_base.py):
```python
{
    "problem": str,   # Description of the problem or use case
    "solution": str   # Code solution with formatting
}
```

**Enhanced Schema** (all new modular case files):
```python
{
    "problem": str,          # Description of the problem or use case (unchanged)
    "solution": str,         # Code solution with formatting (unchanged)
    "category": str,         # NEW: Top-level category
    "subcategory": str,      # NEW: Specific domain/technology
    "tags": List[str]        # NEW: Search keywords
}
```

**Field Specifications:**

1. **problem** (str, required)
   - Description: Natural language description of the code example use case
   - Format: Free text, typically 1-3 sentences
   - Example: "A React component for user sign-up with Firebase Authentication."
   - Constraints: 10-500 characters
   - Usage: Primary field for semantic search and embedding generation

2. **solution** (str, required)
   - Description: Complete code implementation with syntax highlighting
   - Format: Multi-line string with proper indentation
   - Example: Complete React component with imports, types, and implementation
   - Constraints: 100-10,000 characters (most are 500-2,000)
   - Usage: Retrieved code example for AI agent context

3. **category** (str, required, NEW)
   - Description: Top-level domain classification
   - Format: Lowercase, hyphen-separated
   - Allowed Values: ["firebase", "react", "nextjs", "bootstrap", "webdev", "orchestration", "security", "rust"]
   - Example: "firebase"
   - Constraints: Must be one of the eight allowed values
   - Usage: Enables category-based filtering and retrieval

4. **subcategory** (str, required, NEW)
   - Description: Specific technology or domain within category
   - Format: Lowercase, hyphen-separated
   - Examples: "firebase-auth", "react-components", "planning", "axum"
   - Constraints: Alphanumeric with hyphens, 3-30 characters
   - Usage: Fine-grained filtering and semantic relevance

5. **tags** (List[str], required, NEW)
   - Description: Technology keywords and concepts for enhanced search
   - Format: Array of lowercase strings
   - Example: ["authentication", "firebase", "react", "hooks", "typescript"]
   - Constraints: 2-10 tags per case, each tag 3-20 characters
   - Usage: Keyword-based filtering and semantic search enhancement

### Metadata Assignment Map

Based on case_base.py analysis, here's the metadata mapping for each category:

#### Firebase Cases (category="firebase")

| File | Subcategory | Tag Examples | Case Count |
|------|-------------|--------------|------------|
| firebase_auth_cases.py | auth | ["firebase", "authentication", "react", "email", "password"] | 5 |
| firebase_firestore_cases.py | firestore | ["firestore", "crud", "database", "transactions", "nosql"] | 4 |

#### Next.js Cases (category="nextjs")

| File | Subcategory | Tag Examples | Case Count |
|------|-------------|--------------|------------|
| nextjs_routing_cases.py | routing | ["nextjs", "routing", "app-router", "dynamic-routes", "middleware"] | 3 |
| nextjs_api_cases.py | api | ["nextjs", "api", "server-actions", "edge-functions", "backend"] | 3 |

#### React Cases (category="react")

| File | Subcategory | Tag Examples | Case Count |
|------|-------------|--------------|------------|
| react_components_cases.py | components | ["react", "hooks", "components", "typescript", "state"] | 6 |

#### Bootstrap Cases (category="bootstrap")

| File | Subcategory | Tag Examples | Case Count |
|------|-------------|--------------|------------|
| bootstrap_ui_cases.py | ui | ["bootstrap", "ui", "responsive", "components", "css"] | 4 |

#### Web Development Cases (category="webdev")

| File | Subcategory | Tag Examples | Case Count |
|------|-------------|--------------|------------|
| webdev_state_management_cases.py | state-management | ["state", "zustand", "react-query", "forms", "context"] | 3 |
| webdev_forms_validation_cases.py | forms-validation | ["forms", "validation", "zod", "schemas", "client-side"] | 3 |
| webdev_api_integration_cases.py | api-integration | ["api", "fetch", "async", "error-handling", "rest"] | 2 |
| webdev_error_handling_cases.py | error-handling | ["errors", "boundaries", "toast", "logging", "recovery"] | 3 |
| webdev_testing_cases.py | testing | ["jest", "testing-library", "unit-tests", "mocking", "assertions"] | 2 |
| webdev_deployment_cases.py | deployment | ["vercel", "deployment", "environment", "config", "production"] | 2 |

#### Orchestration Cases (category="orchestration")

| File | Subcategory | Tag Examples | Case Count |
|------|-------------|--------------|------------|
| orchestration_planning_cases.py | planning | ["tdd", "workflow", "planning", "agents", "tasks"] | 2 |
| orchestration_remediation_cases.py | remediation | ["remediation", "verification", "failure", "recovery", "karen"] | 1 |
| orchestration_delegation_cases.py | delegation | ["delegation", "agents", "coordination", "workflow", "handoff"] | 1 |
| orchestration_verification_cases.py | verification | ["verification", "karen", "testing", "validation", "quality"] | 1 |
| orchestration_completion_cases.py | completion | ["completion", "workflow", "tasks", "reporting", "summary"] | 1 |

#### Security Cases (category="security")

| File | Subcategory | Tag Examples | Case Count |
|------|-------------|--------------|------------|
| security_auth_cases.py | auth | ["jwt", "authentication", "authorization", "tokens", "rbac"] | 2 |
| security_validation_cases.py | validation | ["validation", "sanitization", "input", "environment", "zod"] | 2 |

#### Rust Cases (category="rust", already exists)

26 existing files with RUST_*_CASES lists, examples:
- rust_axum_cases.py (subcategory="axum", tags=["axum", "web", "async", "middleware"])
- rust_tokio_cases.py (subcategory="tokio", tags=["tokio", "async", "runtime", "futures"])
- rust_serde_cases.py (subcategory="serde", tags=["serde", "serialization", "json", "derive"])

**Note:** Rust cases already exist and do not need metadata enhancement in this spec.

## ChromaDB Storage Structure (Unchanged)

### Collection Schema

**Collection Name:** `code_solutions_case_base` (unchanged)

**Document Structure:**
```python
{
    "id": str,                  # Auto-generated UUID or sequential ID
    "embedding": List[float],   # 768-dimensional vector from nomic-ai/nomic-embed-text-v1.5
    "metadata": {
        "problem": str,         # Case problem description
        "category": str,        # NEW in metadata, but ChromaDB structure unchanged
        "subcategory": str,     # NEW in metadata, but ChromaDB structure unchanged
        "tags": str             # NEW in metadata (JSON serialized), but ChromaDB structure unchanged
    },
    "document": str             # Full case solution text
}
```

**Important:** ChromaDB storage format is determined by setup_vectordb.py and retriever.py, which may or may not store the new metadata fields. This spec only adds metadata to the Python case dictionaries - the ChromaDB integration is separate and remains unchanged.

**Metadata Storage Clarification:** New metadata fields (category, subcategory, tags) will be stored in each case dict in Python and passed through to ChromaDB when cases are added to the vector database. This enables future category-based filtering in retriever.py, though that functionality is out of scope for this refactoring.

## API Endpoints (No Changes)

### MCP Tools (Unchanged)

1. **cbr_retrieve** - Semantic similarity search
   - Parameters: query (str), max_results (int), similarity_threshold (float)
   - Returns: List of cases with similarity scores
   - **No changes** - retrieves cases regardless of internal metadata

2. **cbr_search_category** - Category-based browsing
   - Parameters: category (str), query (str), limit (int)
   - Returns: Filtered list of cases
   - **Potential enhancement** - could use new metadata, but not required for this spec

3. **cbr_find_similar** - Find related cases
   - Parameters: example_id (str), max_results (int), similarity_threshold (float)
   - Returns: Similar cases
   - **No changes** - similarity based on embeddings, not metadata

### MCP Resources (Unchanged)

1. **cbr://categories** - List available categories
   - Returns: List of unique categories
   - **May reflect new metadata** - if resource reads from case metadata

2. **cbr://example/{id}** - Retrieve specific case
   - Returns: Single case dictionary
   - **Will include new metadata fields** - cases now have category/subcategory/tags

3. **cbr://stats** - System statistics
   - Returns: Case base stats
   - **May include metadata stats** - if stats calculation reads new fields

## Data Migration

### Migration Strategy: None Required

This is a **code refactoring only** with no persistent data migration:

1. **ChromaDB** - No migration needed (database reads from Python case dictionaries dynamically)
2. **Case Files** - New files created, old file replaced with wrapper
3. **Embeddings** - Re-generated automatically by setup_vectordb.py on next run
4. **Backward Compatibility** - case_base.CASE_BASE maintains existing API

### Validation Requirements

After refactoring, validate:

1. **Case Count** - Ensure ALL_CASES contains exactly 49 cases (matching original case_base.py)
2. **Metadata Completeness** - All cases have category, subcategory, and tags fields
3. **Metadata Validity** - Categories in allowed list, tags are non-empty arrays
4. **Solution Integrity** - All solution text preserved exactly (no content changes)
5. **Import Success** - case_base.CASE_BASE imports successfully and equals ALL_CASES

## File Format Examples

### Example Firebase Case File (firebase_auth_cases.py)

```python
"""
Firebase Authentication Cases for CBR MCP Server
Examples: sign-up, sign-in, password reset, MFA, session management
"""

FIREBASE_AUTH_CASES = [
    {
        "problem": "A React component for user sign-up with Firebase Authentication.",
        "solution": """
import React, { useState } from 'react';
import { getAuth, createUserWithEmailAndPassword, updateProfile } from 'firebase/auth';
// ... (full solution code)
        """,
        "category": "firebase",
        "subcategory": "auth",
        "tags": ["firebase", "authentication", "react", "signup", "email", "password", "typescript"]
    },
    {
        "problem": "Implement Firebase email/password sign-in with error handling and loading states.",
        "solution": """
import React, { useState } from 'react';
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';
// ... (full solution code)
        """,
        "category": "firebase",
        "subcategory": "auth",
        "tags": ["firebase", "authentication", "signin", "error-handling", "react", "hooks"]
    }
    // ... 3 more Firebase Auth cases
]
```

### Example Orchestration Case File (orchestration_planning_cases.py)

```python
"""
Orchestration Planning Cases for CBR MCP Server
Examples: TDD workflow planning, multi-agent task breakdown
"""

ORCHESTRATION_PLANNING_CASES = [
    {
        "problem": "Refactor the PaymentProcessor service to use the new StripeClient instead of the legacy BraintreeClient.",
        "solution": """
<sequential-thinking>
The user wants to refactor a service. This involves changing implementation details while ensuring behavior remains the same. A Test-Driven Development (TDD) approach is safest.

1.  **Write Refactoring Tests:** Ensure existing tests cover all legacy client behavior.
    -   Agent: tdd-test-engineer
    -   Verification: karen
// ... (full solution)
        """,
        "category": "orchestration",
        "subcategory": "planning",
        "tags": ["tdd", "refactoring", "workflow", "test-driven", "agents", "planning"]
    }
    // ... 1 more planning case
]
```

## Data Validation Rules

### Case Validation Function (in cases/__init__.py)

```python
def validate_case(case: Dict[str, Any], index: int, module: str) -> List[str]:
    """Validate a single case and return list of validation errors."""
    errors = []

    # Required fields
    if "problem" not in case or not case["problem"].strip():
        errors.append(f"Case {index} in {module}: missing or empty 'problem'")

    if "solution" not in case or not case["solution"].strip():
        errors.append(f"Case {index} in {module}: missing or empty 'solution'")

    if "category" not in case:
        errors.append(f"Case {index} in {module}: missing 'category'")
    elif case["category"] not in ["firebase", "react", "nextjs", "bootstrap", "webdev", "orchestration", "security", "rust"]:
        errors.append(f"Case {index} in {module}: invalid category '{case['category']}'")

    if "subcategory" not in case or not case["subcategory"].strip():
        errors.append(f"Case {index} in {module}: missing or empty 'subcategory'")

    if "tags" not in case:
        errors.append(f"Case {index} in {module}: missing 'tags'")
    elif not isinstance(case["tags"], list) or len(case["tags"]) < 2:
        errors.append(f"Case {index} in {module}: 'tags' must be a list with at least 2 tags")

    return errors
```

## Summary

This data specification confirms:

1. **No Database Changes** - ChromaDB structure and embeddings unchanged
2. **No API Changes** - MCP tools and resources maintain compatibility
3. **Metadata Enhancement** - All cases gain category, subcategory, and tags fields
4. **Backward Compatibility** - case_base.CASE_BASE preserves existing integrations
5. **Validation Required** - 49 cases with complete, valid metadata

The refactoring is purely organizational with metadata enrichment, requiring no data migration and maintaining full backward compatibility.
