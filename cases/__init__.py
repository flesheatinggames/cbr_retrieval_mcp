"""
Dynamic case loader for CBR MCP Server.

This module discovers and loads case modules from subdirectories,
aggregating them into a single ALL_CASES list for the MCP server.
"""

from pathlib import Path
from typing import List, Dict, Any
import logging
import importlib

logger = logging.getLogger(__name__)

# Allowed category values for case metadata validation
ALLOWED_CATEGORIES = [
    "firebase",
    "react",
    "nextjs",
    "bootstrap",
    "webdev",
    "orchestration",
    "security",
    "rust"
]


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
            if attr_name.endswith('_CASES'):
                attr_value = getattr(module, attr_name)
                if isinstance(attr_value, list):
                    return attr_value

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


def validate_case(case: Dict[str, Any]) -> bool:
    """
    Validate that a case dictionary has all required metadata fields.

    Args:
        case: Case dictionary to validate

    Returns:
        True if case is valid, False otherwise
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
    if not isinstance(case["category"], str) or not case["category"]:
        return False
    if case["category"] not in ALLOWED_CATEGORIES:
        return False

    # Validate subcategory is a non-empty string
    if not isinstance(case["subcategory"], str) or not case["subcategory"]:
        return False

    # Validate tags is a list (not tuple, dict, string, etc.) AND is non-empty
    if not isinstance(case["tags"], list):
        return False
    if not case["tags"]:  # Empty list check
        return False

    return True


# Main export
ALL_CASES = load_all_cases()
