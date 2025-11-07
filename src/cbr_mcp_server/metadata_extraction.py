"""
Metadata extraction utilities for ChromaDB case storage.

This module provides functions to extract metadata from case dictionaries
and convert them into ChromaDB-compatible format.
"""

from typing import Any, Dict, List


def extract_metadata_from_case(case: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract metadata from a single case dictionary.

    Converts case data into ChromaDB-compatible metadata format with proper
    defaults for missing fields. Tags are converted from list to comma-separated string.

    Args:
        case: Dictionary containing case data with optional fields:
              - problem (str): Problem description
              - category (str): Category classification
              - subcategory (str): Subcategory classification
              - tags (list[str]): List of tags

    Returns:
        Dictionary with metadata in ChromaDB-compatible format:
        - problem (str): Problem text from case
        - category (str): Category or "unknown" if missing
        - subcategory (str): Subcategory or "unknown" if missing
        - tags (str): Comma-separated tags or "" if missing/empty
    """
    return {
        "problem": case.get("problem", ""),
        "category": case.get("category", "unknown"),
        "subcategory": case.get("subcategory", "unknown"),
        "tags": ",".join(case.get("tags", [])),
    }


def extract_metadata_list(cases: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Extract metadata from a list of cases.

    Processes each case through extract_metadata_from_case() to convert
    a list of case dictionaries into ChromaDB-compatible metadata format.

    Args:
        cases: List of case dictionaries, each containing case data

    Returns:
        List of metadata dictionaries in ChromaDB-compatible format,
        with the same length as the input list
    """
    return [extract_metadata_from_case(case) for case in cases]
