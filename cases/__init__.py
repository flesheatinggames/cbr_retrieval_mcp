"""
Dynamic Case Loader for CBR MCP Server.

This module implements a dynamic discovery and loading system for case-based reasoning
examples. It automatically discovers case modules from subdirectories, imports them,
and aggregates all cases into a unified collection for consumption by the MCP server.

Architecture
------------
The loader follows a three-phase approach:

1. **Discovery Phase**: Scan subdirectories for *_cases.py modules
2. **Import Phase**: Dynamically import discovered modules and extract case lists
3. **Aggregation Phase**: Combine all case lists into the ALL_CASES export

Directory Structure
-------------------
Expected case organization::

    cases/
    ├── __init__.py (this file)
    ├── firebase/
    │   └── firebase_auth_cases.py  # Contains FIREBASE_AUTH_CASES list
    ├── react/
    │   └── react_hooks_cases.py    # Contains REACT_HOOKS_CASES list
    ├── nextjs/
    │   └── nextjs_routing_cases.py # Contains NEXTJS_ROUTING_CASES list
    └── ...other categories.../

Each case module must export at least one list variable ending with '_CASES' containing
case dictionaries with the following required fields:
- problem: str - Description of the problem the case addresses
- solution: str - The solution/code example
- category: str - Top-level category (must be in ALLOWED_CATEGORIES)
- subcategory: str - More specific subcategory
- tags: List[str] - Searchable tags for the case

Module Usage
------------
This module is intended to be imported by the MCP server initialization::

    from cases import ALL_CASES

    # ALL_CASES now contains all discovered and validated cases
    for case in ALL_CASES:
        print(case['problem'], case['category'])

Exports
-------
ALL_CASES : List[Dict[str, Any]]
    The complete aggregated list of all cases from all discovered modules.
    This is populated at module import time.

ALLOWED_CATEGORIES : List[str]
    Whitelist of valid category values for case validation.
"""

import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Allowed category values for case metadata validation
# This whitelist ensures consistency and prevents typos in case definitions
# To add a new category:
# 1. Add the category string to this list
# 2. Create a corresponding subdirectory: cases/{category}/
# 3. Add case modules in that subdirectory following the *_cases.py pattern
ALLOWED_CATEGORIES = [
    "firebase",  # Firebase backend services (auth, storage, functions, etc.)
    "react",  # React UI components and patterns
    "nextjs",  # Next.js framework patterns
    "bootstrap",  # Bootstrap UI components and styling
    "webdev",  # General web development patterns
    "orchestration",  # Agent orchestration and workflow patterns
    "security",  # Security best practices and implementations
    "rust",  # Rust programming patterns (surrealdb, axum, tokio, etc.)
]


def discover_case_modules() -> List[str]:
    """
    Discover all *_cases.py modules in subdirectories.

    This function scans the cases/ directory for subdirectories (excluding those
    starting with '_') and finds all Python files matching the pattern '*_cases.py'.
    Each discovered file is converted to a fully-qualified module path for import.

    The discovery process:
    1. Gets the parent directory of this __init__.py file (the cases/ directory)
    2. Iterates through all immediate subdirectories
    3. Skips directories starting with '_' (like __pycache__)
    4. Within each valid subdirectory, finds all files matching '*_cases.py'
    5. Converts file paths to import-ready module paths

    Returns
    -------
    List[str]
        A list of fully-qualified module paths ready for importlib.import_module().
        Example: ['cases.firebase.firebase_auth_cases', 'cases.react.react_hooks_cases']

    Notes
    -----
    - Directories starting with '_' are excluded to skip Python internals like __pycache__
    - Only files ending with '_cases.py' are considered valid case modules
    - The module path format is 'cases.{subdirectory}.{filename_without_extension}'

    Examples
    --------
    Given this directory structure::

        cases/
        ├── firebase/
        │   ├── firebase_auth_cases.py
        │   └── firebase_storage_cases.py
        └── react/
            └── react_hooks_cases.py

    This function returns::

        [
            'cases.firebase.firebase_auth_cases',
            'cases.firebase.firebase_storage_cases',
            'cases.react.react_hooks_cases'
        ]
    """
    cases_dir = Path(__file__).parent
    modules = []

    # Scan all subdirectories for case modules
    for subdir in cases_dir.iterdir():
        # Skip non-directories and internal directories (starting with '_')
        if subdir.is_dir() and not subdir.name.startswith("_"):
            # Find all *_cases.py files in this subdirectory
            for file in subdir.glob("*_cases.py"):
                # Convert file path to module path: cases.subdirectory.filename
                module_path = f"cases.{subdir.name}.{file.stem}"
                modules.append(module_path)

    return modules


def load_cases_from_module(module_path: str) -> List[Dict[str, Any]]:
    """
    Load cases from a single module by importing it and extracting case lists.

    This function dynamically imports a case module and searches for exported
    case list variables. It looks for any module-level list variable whose name
    ends with '_CASES' (e.g., FIREBASE_AUTH_CASES, REACT_HOOKS_CASES).

    The case extraction process:
    1. Import the module using importlib.import_module()
    2. Iterate through all module attributes using dir()
    3. Find attributes ending with '_CASES'
    4. Verify the attribute is a list
    5. Return the first matching case list found

    Parameters
    ----------
    module_path : str
        Fully-qualified module path (e.g., 'cases.firebase.firebase_auth_cases')

    Returns
    -------
    List[Dict[str, Any]]
        A list of case dictionaries from the module. Returns an empty list if:
        - The module cannot be imported
        - No '_CASES' variable is found
        - The '_CASES' variable is not a list

    Notes
    -----
    - Only the first matching '_CASES' list is returned (though best practice
      is to have only one per module)
    - Import errors and missing case lists are logged but do not raise exceptions,
      allowing partial case base loading if some modules fail
    - The function gracefully handles import failures to prevent one broken module
      from breaking the entire case loading system

    Examples
    --------
    >>> cases = load_cases_from_module('cases.firebase.firebase_auth_cases')
    >>> len(cases)
    5
    >>> cases[0]['category']
    'firebase'

    Error handling example::

        # Module with import error - returns empty list, logs error
        cases = load_cases_from_module('cases.nonexistent.bad_module')
        # Returns: []
        # Logs: "Failed to load cases.nonexistent.bad_module: No module named 'cases.nonexistent'"
    """
    try:
        # Dynamically import the module
        module = importlib.import_module(module_path)

        # Search for case list variables ending with '_CASES'
        # Using dir() gives us all public and private attributes
        for attr_name in dir(module):
            if attr_name.endswith("_CASES"):
                attr_value = getattr(module, attr_name)
                # Ensure it's actually a list before returning
                if isinstance(attr_value, list):
                    return attr_value

        # No case list found in the module - log warning but don't fail
        logger.warning(f"No case list found in {module_path}")
        return []

    except Exception as e:
        # Import or attribute access failed - log error but don't fail
        # This allows other modules to load successfully
        logger.error(f"Failed to load {module_path}: {e}")
        return []


def load_all_cases() -> List[Dict[str, Any]]:
    """
    Load and aggregate all cases from all discovered case modules.

    This is the main orchestration function that coordinates the discovery and
    loading process. It discovers all case modules, loads cases from each module,
    and aggregates them into a single unified list.

    The aggregation process:
    1. Call discover_case_modules() to find all case modules
    2. Log the number of modules discovered
    3. For each discovered module:
       a. Load cases using load_cases_from_module()
       b. Extend the aggregated list with loaded cases
       c. Log the number of cases loaded from that module
    4. Log the total number of cases loaded
    5. Return the complete aggregated list

    Returns
    -------
    List[Dict[str, Any]]
        A complete list of all case dictionaries from all discovered modules.
        Each case dictionary contains:
        - problem: str - Problem description
        - solution: str - Solution/code example
        - category: str - Top-level category
        - subcategory: str - Specific subcategory
        - tags: List[str] - Search tags

    Notes
    -----
    - This function is called once at module import time to populate ALL_CASES
    - Failed module loads do not prevent other modules from loading
    - Progress is logged at INFO level for operational visibility
    - Empty case lists from failed modules are silently skipped in aggregation

    Examples
    --------
    >>> all_cases = load_all_cases()
    # Logs: "Discovered 8 case modules"
    # Logs: "Loaded 5 cases from cases.firebase.firebase_auth_cases"
    # Logs: "Loaded 3 cases from cases.react.react_hooks_cases"
    # ... (more modules)
    # Logs: "Total cases loaded: 47"

    >>> len(all_cases)
    47
    >>> all_cases[0].keys()
    dict_keys(['problem', 'solution', 'category', 'subcategory', 'tags'])
    """
    all_cases = []

    # Phase 1: Discover all case modules
    modules = discover_case_modules()
    logger.info(f"Discovered {len(modules)} case modules")

    # Phase 2: Load and aggregate cases from each module
    for module_path in modules:
        cases = load_cases_from_module(module_path)
        # Extend (not append) to flatten the list structure
        all_cases.extend(cases)
        logger.info(f"Loaded {len(cases)} cases from {module_path}")

    # Phase 3: Report final aggregation results
    logger.info(f"Total cases loaded: {len(all_cases)}")
    return all_cases


def validate_case(case: Dict[str, Any]) -> bool:
    """
    Validate that a case dictionary has all required metadata fields and correct types.

    This function performs comprehensive validation of case dictionaries to ensure
    they meet the schema requirements for the CBR system. It checks for presence of
    required fields, correct data types, non-empty values, and category whitelist compliance.

    Validation Rules
    ----------------
    1. **Required Fields**: All of ['problem', 'solution', 'category', 'subcategory', 'tags']
       must be present in the case dictionary
    2. **Problem Field**: Must be a non-empty string
    3. **Solution Field**: Must be a non-empty string
    4. **Category Field**: Must be a non-empty string AND in ALLOWED_CATEGORIES
    5. **Subcategory Field**: Must be a non-empty string
    6. **Tags Field**: Must be a list (not tuple/dict/string) AND non-empty

    Parameters
    ----------
    case : Dict[str, Any]
        The case dictionary to validate

    Returns
    -------
    bool
        True if the case passes all validation checks, False otherwise

    Notes
    -----
    - This function does not raise exceptions; it returns False for any validation failure
    - The category field is validated against the ALLOWED_CATEGORIES whitelist to prevent
      typos and ensure consistency
    - Tags must be a list type specifically; other iterables like tuples are rejected
    - Empty strings are considered invalid for string fields
    - Empty lists are considered invalid for the tags field

    Examples
    --------
    Valid case::

        valid_case = {
            'problem': 'How to authenticate with Firebase',
            'solution': 'Use firebase.auth().signInWithEmailAndPassword(...)',
            'category': 'firebase',
            'subcategory': 'authentication',
            'tags': ['auth', 'login', 'firebase']
        }
        validate_case(valid_case)  # Returns: True

    Invalid cases::

        # Missing required field
        invalid_case = {
            'problem': 'Test',
            'solution': 'Test solution',
            'category': 'firebase'
            # Missing 'subcategory' and 'tags'
        }
        validate_case(invalid_case)  # Returns: False

        # Invalid category
        invalid_case = {
            'problem': 'Test',
            'solution': 'Test solution',
            'category': 'invalid_category',  # Not in ALLOWED_CATEGORIES
            'subcategory': 'test',
            'tags': ['test']
        }
        validate_case(invalid_case)  # Returns: False

        # Empty tags list
        invalid_case = {
            'problem': 'Test',
            'solution': 'Test solution',
            'category': 'firebase',
            'subcategory': 'test',
            'tags': []  # Empty list not allowed
        }
        validate_case(invalid_case)  # Returns: False
    """
    # Check all required fields are present
    required_fields = ["problem", "solution", "category", "subcategory", "tags"]
    for field in required_fields:
        if field not in case:
            return False

    # Validate problem is a non-empty string
    if not isinstance(case["problem"], str) or not case["problem"]:
        return False

    # Validate solution is a non-empty string
    if not isinstance(case["solution"], str) or not case["solution"]:
        return False

    # Validate category is a non-empty string AND in allowed list
    # The whitelist check prevents typos and ensures consistency
    if not isinstance(case["category"], str) or not case["category"]:
        return False
    if case["category"] not in ALLOWED_CATEGORIES:
        return False

    # Validate subcategory is a non-empty string
    if not isinstance(case["subcategory"], str) or not case["subcategory"]:
        return False

    # Validate tags is a list (not tuple, dict, string, etc.) AND is non-empty
    # Must be specifically a list type for consistency
    if not isinstance(case["tags"], list):
        return False
    if not case["tags"]:  # Empty list check
        return False

    return True


# ============================================================================
# Module Initialization and Main Export
# ============================================================================

# ALL_CASES is the primary export of this module and is populated at import time.
# This list contains all cases from all discovered case modules, ready for use
# by the MCP server and other components.
#
# The loading happens synchronously during module import, which means:
# - Any import errors in case modules will be logged but won't prevent other modules from loading
# - The complete case base is available immediately after: from cases import ALL_CASES
# - No additional initialization or setup is required by consumers
#
# Performance Note: For large case bases, this import-time loading may add startup
# latency. If this becomes an issue, consider implementing lazy loading or
# async initialization patterns.

ALL_CASES = load_all_cases()

# After this point, ALL_CASES contains the complete aggregated case base
# and is ready for consumption by the CBR MCP Server
