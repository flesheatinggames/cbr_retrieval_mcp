"""
Shared metadata transformation utilities for test suites.

This module provides helper functions for transforming case metadata
to ChromaDB-compatible formats across integration and unit tests.
"""

from typing import Any, Dict


def transform_metadata(case: Dict[str, Any]) -> Dict[str, str]:
    """
    Transform case metadata to ChromaDB-compatible format.

    Extracts category, subcategory, tags, and problem from case dictionary
    and converts tags list to comma-separated string.

    Args:
        case: Case dictionary with metadata fields

    Returns:
        Dictionary with string-typed metadata fields for ChromaDB

    Example:
        >>> case = {
        ...     "problem": "How to implement auth?",
        ...     "solution": "Use Firebase auth",
        ...     "category": "firebase",
        ...     "subcategory": "auth",
        ...     "tags": ["firebase", "authentication"]
        ... }
        >>> transform_metadata(case)
        {'problem': 'How to implement auth?', 'category': 'firebase',
         'subcategory': 'auth', 'tags': 'firebase,authentication'}
    """
    return {
        "problem": case["problem"],
        "category": case.get("category", ""),
        "subcategory": case.get("subcategory", ""),
        "tags": ",".join(case.get("tags", [])),
    }
