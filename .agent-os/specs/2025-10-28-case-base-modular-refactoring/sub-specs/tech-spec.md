# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-10-28-case-base-modular-refactoring/spec.md

> Created: 2025-10-28
> Version: 1.0.0

## Technical Architecture

### Directory Structure

```
cases/
├── __init__.py                                    # Dynamic loader with ALL_CASES aggregation
├── firebase/
│   ├── __init__.py                               # Empty, standard Python package marker
│   ├── firebase_auth_cases.py                    # FIREBASE_AUTH_CASES = [...]
│   └── firebase_firestore_cases.py               # FIREBASE_FIRESTORE_CASES = [...]
├── nextjs/
│   ├── __init__.py                               # Empty, standard Python package marker
│   ├── nextjs_routing_cases.py                   # NEXTJS_ROUTING_CASES = [...]
│   └── nextjs_api_cases.py                       # NEXTJS_API_CASES = [...]
├── react/
│   ├── __init__.py                               # Empty, standard Python package marker
│   └── react_components_cases.py                 # REACT_COMPONENTS_CASES = [...]
├── bootstrap/
│   ├── __init__.py                               # Empty, standard Python package marker
│   └── bootstrap_ui_cases.py                     # BOOTSTRAP_UI_CASES = [...]
├── webdev/
│   ├── __init__.py                               # Empty, standard Python package marker
│   ├── webdev_state_management_cases.py          # WEBDEV_STATE_MANAGEMENT_CASES = [...]
│   ├── webdev_forms_validation_cases.py          # WEBDEV_FORMS_VALIDATION_CASES = [...]
│   ├── webdev_api_integration_cases.py           # WEBDEV_API_INTEGRATION_CASES = [...]
│   ├── webdev_error_handling_cases.py            # WEBDEV_ERROR_HANDLING_CASES = [...]
│   ├── webdev_testing_cases.py                   # WEBDEV_TESTING_CASES = [...]
│   └── webdev_deployment_cases.py                # WEBDEV_DEPLOYMENT_CASES = [...]
├── orchestration/
│   ├── __init__.py                               # Empty, standard Python package marker
│   ├── orchestration_planning_cases.py           # ORCHESTRATION_PLANNING_CASES = [...]
│   ├── orchestration_remediation_cases.py        # ORCHESTRATION_REMEDIATION_CASES = [...]
│   ├── orchestration_delegation_cases.py         # ORCHESTRATION_DELEGATION_CASES = [...]
│   ├── orchestration_verification_cases.py       # ORCHESTRATION_VERIFICATION_CASES = [...]
│   └── orchestration_completion_cases.py         # ORCHESTRATION_COMPLETION_CASES = [...]
├── security/
│   ├── __init__.py                               # Empty, standard Python package marker
│   ├── security_auth_cases.py                    # SECURITY_AUTH_CASES = [...]
│   └── security_validation_cases.py              # SECURITY_VALIDATION_CASES = [...]
└── rust/                                          # Already exists with 26 files
    ├── rust_axum_cases.py                        # RUST_AXUM_CASES = [...]
    ├── rust_tokio_cases.py                       # RUST_TOKIO_CASES = [...]
    └── ... (24 more files)
```

### Dynamic Loader Implementation (cases/__init__.py)

The dynamic loader must:

1. **Discover Case Modules** - Use importlib to find all *_cases.py files in subdirectories (firebase/, react/, nextjs/, bootstrap/, webdev/, orchestration/, security/, rust/)
2. **Import Modules Dynamically** - Import each discovered module and extract its case list (e.g., FIREBASE_AUTH_CASES, RUST_AXUM_CASES)
3. **Aggregate Cases** - Combine all case lists into a single ALL_CASES list
4. **Error Handling** - Gracefully handle import errors with logging, allowing partial case base loading
5. **Optional Filtering** - Support environment variable CASE_CATEGORIES to load only specific subdirectories

**Implementation Pattern:**

```python
import os
import importlib
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def discover_case_modules() -> List[str]:
    """Discover all *_cases.py modules in subdirectories."""
    cases_dir = Path(__file__).parent
    modules = []

    for subdir in cases_dir.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('_'):
            for file in subdir.glob('*_cases.py'):
                module_path = f"cases.{subdir.name}.{file.stem}"
                modules.append(module_path)

    return modules

def load_cases_from_module(module_path: str) -> List[Dict[str, Any]]:
    """Load cases from a single module."""
    try:
        module = importlib.import_module(module_path)

        # Find the case list variable (e.g., FIREBASE_AUTH_CASES)
        for attr_name in dir(module):
            if attr_name.endswith('_CASES') and isinstance(getattr(module, attr_name), list):
                return getattr(module, attr_name)

        logger.warning(f"No case list found in {module_path}")
        return []

    except Exception as e:
        logger.error(f"Failed to load {module_path}: {e}")
        return []

def load_all_cases() -> List[Dict[str, Any]]:
    """Load all cases from all modules."""
    all_cases = []
    modules = discover_case_modules()

    logger.info(f"Discovered {len(modules)} case modules")

    for module_path in modules:
        cases = load_cases_from_module(module_path)
        all_cases.extend(cases)
        logger.info(f"Loaded {len(cases)} cases from {module_path}")

    logger.info(f"Total cases loaded: {len(all_cases)}")
    return all_cases

# Main export
ALL_CASES = load_all_cases()
```

### Case Module File Format

Each case module file follows this template:

```python
"""
[Technology/Domain] Cases for CBR MCP Server
"""

[MODULE_NAME]_CASES = [
    {
        "problem": "Description of the problem or use case",
        "solution": """
        Code solution with proper indentation and formatting
        """,
        "category": "firebase",                     # NEW: Top-level category
        "subcategory": "auth",                      # NEW: Specific subcategory
        "tags": ["authentication", "firebase", "react"]  # NEW: Search tags
    },
    # ... more cases
]
```

### Metadata Schema

All cases must include these new fields:

- **category** (str): Top-level category - e.g., "firebase", "react", "nextjs", "bootstrap", "webdev", "orchestration", "security", "rust"
- **subcategory** (str): Specific domain - e.g., "auth", "components", "routing"
- **tags** (List[str]): Search keywords - e.g., ["authentication", "hooks", "typescript", "async"]

**Metadata Assignment Rules:**

1. **Firebase Cases**: category="firebase", subcategory based on file name (e.g., "auth" from firebase_auth_cases.py)
2. **React Cases**: category="react", subcategory from file (e.g., "components" from react_components_cases.py)
3. **Next.js Cases**: category="nextjs", subcategory from file (e.g., "routing" from nextjs_routing_cases.py)
4. **Bootstrap Cases**: category="bootstrap", subcategory from file (e.g., "ui" from bootstrap_ui_cases.py)
5. **WebDev Cases**: category="webdev", subcategory from file (e.g., "state-management" from webdev_state_management_cases.py)
6. **Orchestration Cases**: category="orchestration", subcategory from file (e.g., "planning", "remediation")
7. **Security Cases**: category="security", subcategory from file (e.g., "auth", "validation")
8. **Rust Cases**: category="rust", subcategory from file (e.g., "axum", "tokio")
9. **Tags**: Extract from problem/solution content - technologies, concepts, frameworks mentioned

### Backward Compatibility Wrapper (case_base.py)

Transform existing case_base.py into a compatibility shim:

```python
"""
Legacy case_base.py - Backward compatibility wrapper
Imports cases from the new modular structure in cases/
"""
from cases import ALL_CASES

# Maintain existing API
CASE_BASE = ALL_CASES

# Maintain existing helper functions
def save_case_base_to_file(filename="firebase_nextjs_bootstrap_cases.json"):
    """Save the case base to a JSON file for easy loading."""
    import json

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(CASE_BASE, f, indent=2, ensure_ascii=False)

    print(f"Case base saved to {filename}")
    print(f"Total cases: {len(CASE_BASE)}")
    return filename

def load_case_base_from_file(filename="firebase_nextjs_bootstrap_cases.json"):
    """Load the case base from a JSON file."""
    import json

    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_cases(query, limit=5):
    """Simple keyword search for cases."""
    results = []
    query_lower = query.lower()

    for case in CASE_BASE:
        if query_lower in case["problem"].lower() or query_lower in case["solution"].lower():
            results.append(case)
            if len(results) >= limit:
                break

    return results

def validate_case_base():
    """Validate all cases have required fields."""
    required_fields = {"problem", "solution", "category", "subcategory", "tags"}

    for i, case in enumerate(CASE_BASE):
        missing = required_fields - set(case.keys())
        if missing:
            print(f"Case {i} missing fields: {missing}")
            return False

    print(f"✓ All {len(CASE_BASE)} cases validated")
    return True

def get_case_statistics():
    """Get statistics about the case base."""
    stats = {
        "total_cases": len(CASE_BASE),
        "categories": {},
        "subcategories": {},
        "avg_solution_length": sum(len(c["solution"]) for c in CASE_BASE) / len(CASE_BASE)
    }

    for case in CASE_BASE:
        cat = case.get("category", "unknown")
        subcat = case.get("subcategory", "unknown")
        stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
        stats["subcategories"][subcat] = stats["subcategories"].get(subcat, 0) + 1

    return stats

# Main execution
if __name__ == "__main__":
    print("=" * 50)
    print("CBR Case Base - Modular Structure")
    print("=" * 50)

    if validate_case_base():
        stats = get_case_statistics()
        print(f"\nTotal Cases: {stats['total_cases']}")
        print("\nCategories:")
        for category, count in stats["categories"].items():
            print(f"  {category}: {count}")
```

### Case Distribution Analysis

Based on analysis of case_base.py (5,768 lines, 49 cases):

**Frontend/Web Technology Cases** (~40 cases, lines 6-1783):
- Firebase Auth: 5 cases (sign-up, sign-in, password reset, MFA, session management)
- Firebase Firestore: 4 cases (create, read, update, delete with transactions)
- Next.js Routing: 3 cases (app router, dynamic routes, middleware)
- Next.js API: 3 cases (API routes, server actions, edge functions)
- React Components: 6 cases (hooks, context, forms, lists, error boundaries)
- Bootstrap UI: 4 cases (modals, cards, navigation, responsive layouts)
- Web Dev State Management: 3 cases (Zustand, React Query, form state)
- Web Dev Forms & Validation: 3 cases (client-side, server-side, Zod schemas)
- Web Dev API Integration: 2 cases (fetch patterns, error handling)
- Web Dev Error Handling: 3 cases (error boundaries, toast notifications, logging)
- Web Dev Testing: 2 cases (Jest unit tests, React Testing Library)
- Web Dev Deployment: 2 cases (Vercel config, environment variables)

**Security Cases** (~4 cases, lines 1784-4431):
- Authentication: 2 cases (JWT validation, role-based access)
- Validation: 2 cases (input sanitization, environment variable validation)

**Orchestration Cases** (~5 cases, lines 4432-5603):
- Planning: 2 cases (TDD workflow planning, refactoring plans)
- Remediation: 1 case (handling failed verification)
- Delegation: 1 case (multi-agent coordination)
- Verification: 1 case (using Karen for validation)
- Completion: 1 case (task completion workflow)

### Integration Points

**Existing Code Changes Required:**

1. **setup_vectordb.py** - Update import:
   ```python
   # OLD
   from case_base import CASE_BASE

   # NEW
   from cases import ALL_CASES as CASE_BASE
   ```

2. **retriever.py** - Update import (if used):
   ```python
   # OLD
   from case_base import CASE_BASE

   # NEW
   from cases import ALL_CASES as CASE_BASE
   ```

3. **cbr_mcp_server.py** - Verify import compatibility (likely uses setup_vectordb, no changes needed)

### Error Handling Strategy

1. **Module Import Failures** - Log error, continue loading other modules (partial case base better than failure)
2. **Missing Case List Variable** - Log warning, skip module
3. **Invalid Case Format** - Log error with case index, continue loading
4. **Missing Metadata Fields** - Log warning, allow backward compatibility with old cases

### Performance Considerations

1. **Startup Time** - Dynamic import adds ~50-100ms overhead, negligible for local MCP server
2. **Memory Footprint** - Modular structure adds ~10-15% overhead from multiple module objects
3. **Reload Capability** - New structure enables hot-reloading of individual case modules without server restart

### Python Compatibility

- **Minimum Version**: Python 3.8+ (matches existing tech stack)
- **Dependencies**: Only stdlib (importlib, pathlib, logging) - no new dependencies
- **Type Hints**: Use typing module for Python 3.8 compatibility (List, Dict, Any)

## User Flow Logic

### Case Addition Workflow

1. Developer identifies appropriate case module (e.g., firebase_auth_cases.py)
2. Opens module file (~100-200 lines instead of 5,768)
3. Adds case to module's case list with metadata
4. Saves file
5. Dynamic loader automatically includes new case on next import
6. No changes to case_base.py or other files needed

### Case Retrieval Workflow (No Changes)

1. AI agent queries CBR MCP Server via cbr_retrieve tool
2. setup_vectordb.py imports ALL_CASES (via cases/__init__.py)
3. ChromaDB generates embeddings and performs similarity search
4. Results returned to agent (unchanged behavior)

### Selective Loading Workflow (Optional Future Enhancement)

1. Administrator sets CASE_CATEGORIES="firebase,react,security" environment variable
2. Dynamic loader reads config and imports only cases/firebase/, cases/react/, and cases/security/
3. Memory footprint reduced by excluding orchestration and rust cases
4. MCP server starts with filtered case base

## Error Handling

1. **Import Error in Case Module**
   - Log: "ERROR: Failed to load cases.firebase.firebase_auth_cases: [exception]"
   - Action: Continue loading other modules
   - Result: Partial case base (missing one module's cases)

2. **Case List Not Found in Module**
   - Log: "WARNING: No case list found in cases.firebase.custom_module"
   - Action: Skip module
   - Result: Module ignored, other cases load normally

3. **Invalid Case Format (Missing Fields)**
   - Log: "WARNING: Case [index] in [module] missing required fields: {problem, solution}"
   - Action: Include case with warning (backward compatibility)
   - Result: Case included but flagged for review

4. **Duplicate Cases Across Modules**
   - Log: "INFO: [N] total cases loaded from [M] modules"
   - Action: Allow duplicates (deduplication is retrieval concern, not loading)
   - Result: All cases included

## Approach Rationale

### Selected Approach: Modular Files with Dynamic Loader

**Rationale:**
1. **Follows Existing Pattern** - cases/rust/ already uses this pattern with 26 separate files
2. **Maintainability** - 100-200 line files much easier to navigate than 5,768 lines
3. **Merge Conflict Reduction** - Separate files reduce Git conflicts in team environments
4. **Selective Loading** - Enables future memory optimization for specific deployments
5. **Backward Compatibility** - case_base.py wrapper preserves existing API

### Alternative Considered: JSON/YAML Configuration Files

**Pros:** Language-agnostic, easier parsing, schema validation
**Cons:** Loses Python syntax highlighting, multi-line string handling awkward, breaks existing pattern
**Decision:** Rejected - maintain consistency with existing cases/rust/ pattern

### Alternative Considered: Database-Backed Case Storage

**Pros:** True dynamic loading, versioning, rollback capabilities
**Cons:** Adds external dependency, overkill for 49 cases, complicates deployment
**Decision:** Rejected - current scale doesn't justify complexity

## External Dependencies

**None** - This refactoring uses only Python standard library:
- `importlib` - Dynamic module loading
- `pathlib` - Path manipulation
- `logging` - Error and info logging
- `typing` - Type hints for Python 3.8+

No new pip packages required.
