"""
Legacy case_base.py - Backward compatibility wrapper

This module now imports cases from the new modular structure in cases/
rather than defining CASE_BASE directly.

The modular structure in cases/ organizes cases by category:
- cases/firebase/firebase_auth_cases.py
- cases/firebase/firebase_firestore_cases.py
- cases/nextjs/nextjs_routing_cases.py
- cases/nextjs/nextjs_api_cases.py
- cases/react/react_components_cases.py
- cases/bootstrap/bootstrap_ui_cases.py
- cases/webdev/webdev_*_cases.py
- cases/orchestration/orchestration_*_cases.py
- cases/security/security_*_cases.py
- cases/rust/rust_*_cases.py

All cases are aggregated into ALL_CASES by cases/__init__.py
This module maintains the CASE_BASE API for backward compatibility.
"""

from cases import ALL_CASES

# Maintain existing API - CASE_BASE is now a reference to ALL_CASES
CASE_BASE = ALL_CASES

# ============================================
# HELPER FUNCTIONS
# ============================================


def save_case_base_to_file(filename="firebase_nextjs_bootstrap_cases.json"):
    """Save the case base to a JSON file for easy loading."""
    import json

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(CASE_BASE, f, indent=2, ensure_ascii=False)

    print(f"Case base saved to {filename}")
    print(f"Total cases: {len(CASE_BASE)}")
    return filename


def load_case_base_from_file(filename="firebase_nextjs_bootstrap_cases.json"):
    """Load the case base from a JSON file."""
    import json

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {filename} not found. Using default case base.")
        return CASE_BASE


def search_cases(query, case_base=None):
    """Search for relevant cases based on a query.

    Searches across problem, solution, category, subcategory, and tags fields.
    """
    if case_base is None:
        case_base = CASE_BASE

    query_lower = query.lower()
    results = []

    for case in case_base:
        problem_lower = case["problem"].lower()
        solution_lower = case["solution"].lower()

        # Calculate relevance score
        score = 0
        query_words = query_lower.split()

        for word in query_words:
            if word in problem_lower:
                score += 2  # Higher weight for problem matches
            if word in solution_lower:
                score += 1

            # Search in metadata fields if present (new modular structure)
            if "category" in case and word in case["category"].lower():
                score += 1.5  # Category matches are highly relevant
            if "subcategory" in case and word in case["subcategory"].lower():
                score += 1.5  # Subcategory matches are highly relevant
            if "tags" in case and isinstance(case["tags"], list):
                for tag in case["tags"]:
                    if word in tag.lower():
                        score += 1  # Tag matches are relevant

        if score > 0:
            results.append((score, case))

    # Sort by relevance score (descending)
    results.sort(key=lambda x: x[0], reverse=True)

    # Return top 5 most relevant cases
    return [case for _, case in results[:5]]


def add_case(problem, solution, case_base=None):
    """Add a new case to the case base."""
    if case_base is None:
        case_base = CASE_BASE

    new_case = {"problem": problem, "solution": solution}

    case_base.append(new_case)
    print(f"Added new case. Total cases: {len(case_base)}")
    return case_base


def validate_case_base(case_base=None):
    """Validate that all cases have proper structure.

    Validates both legacy format (problem, solution) and new modular format
    (problem, solution, category, subcategory, tags).
    """
    if case_base is None:
        case_base = CASE_BASE

    issues = []

    for i, case in enumerate(case_base):
        # Required fields for all cases
        if "problem" not in case:
            issues.append(f"Case {i}: Missing 'problem' field")
        if "solution" not in case:
            issues.append(f"Case {i}: Missing 'solution' field")
        if not isinstance(case.get("problem", ""), str):
            issues.append(f"Case {i}: 'problem' must be a string")
        if not isinstance(case.get("solution", ""), str):
            issues.append(f"Case {i}: 'solution' must be a string")

        # Validate metadata fields if present (new modular structure)
        if "category" in case:
            if not isinstance(case["category"], str):
                issues.append(f"Case {i}: 'category' must be a string")
        if "subcategory" in case:
            if not isinstance(case["subcategory"], str):
                issues.append(f"Case {i}: 'subcategory' must be a string")
        if "tags" in case:
            if not isinstance(case["tags"], list):
                issues.append(f"Case {i}: 'tags' must be a list")
            else:
                for j, tag in enumerate(case["tags"]):
                    if not isinstance(tag, str):
                        issues.append(f"Case {i}: tag {j} must be a string")

    if issues:
        print("Validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("Case base validation passed!")
        print(f"Total valid cases: {len(case_base)}")
        return True


def get_case_statistics(case_base=None):
    """Get statistics about the case base.

    Provides statistics using actual metadata categories if available (new modular
    structure), otherwise falls back to keyword matching in problem field (legacy).
    """
    if case_base is None:
        case_base = CASE_BASE

    stats = {
        "total_cases": len(case_base),
        "categories": {
            "firebase_auth": 0,
            "firestore": 0,
            "nextjs": 0,
            "bootstrap": 0,
            "combined": 0,
        },
        "avg_solution_length": 0,
    }

    total_length = 0
    # Track if any cases have metadata (new modular structure)
    has_metadata = any("category" in case for case in case_base)

    for case in case_base:
        # Use actual category metadata if available (new modular structure)
        if "category" in case:
            category = case["category"].lower()
            # Map actual categories to stats categories
            if category == "firebase":
                subcategory = case.get("subcategory", "").lower()
                if "auth" in subcategory:
                    stats["categories"]["firebase_auth"] += 1
                elif "firestore" in subcategory:
                    stats["categories"]["firestore"] += 1
                else:
                    stats["categories"]["combined"] += 1
            elif category == "nextjs":
                stats["categories"]["nextjs"] += 1
            elif category == "bootstrap":
                stats["categories"]["bootstrap"] += 1
            else:
                stats["categories"]["combined"] += 1
        else:
            # Fallback to keyword matching for legacy cases
            problem_lower = case["problem"].lower()

            if "firebase" in problem_lower and "auth" in problem_lower:
                stats["categories"]["firebase_auth"] += 1
            elif "firestore" in problem_lower:
                stats["categories"]["firestore"] += 1
            elif "next.js" in problem_lower or "nextjs" in problem_lower:
                stats["categories"]["nextjs"] += 1
            elif "bootstrap" in problem_lower:
                stats["categories"]["bootstrap"] += 1
            else:
                stats["categories"]["combined"] += 1

        total_length += len(case["solution"])

    stats["avg_solution_length"] = total_length // len(case_base) if case_base else 0

    print("\nCase Base Statistics:")
    print(f"Total Cases: {stats['total_cases']}")
    print("\nCategories:")
    for category, count in stats["categories"].items():
        print(f"  {category}: {count}")
    print(f"\nAverage Solution Length: {stats['avg_solution_length']} characters")

    return stats


# Main execution - demonstrates backward compatibility with CASE_BASE = ALL_CASES
if __name__ == "__main__":
    print("=" * 50)
    print("Firebase/Next.js/Bootstrap Case-Based Reasoning Dataset")
    print("=" * 50)

    # Validate the case base (now uses modular ALL_CASES structure)
    if validate_case_base():
        # Get statistics
        get_case_statistics()

        # Save to JSON file
        filename = save_case_base_to_file()

        # Example: Search for Firebase authentication cases
        print("\n" + "=" * 50)
        print("Example Search: 'Firebase authentication'")
        print("=" * 50)
        results = search_cases("Firebase authentication")
        for i, case in enumerate(results, 1):
            print(f"\n{i}. {case['problem']}")
            # Show category metadata if available (new modular structure feature)
            if "category" in case:
                metadata_info = f"   Category: {case['category']}"
                if "subcategory" in case:
                    metadata_info += f" / {case['subcategory']}"
                print(metadata_info)
            print(f"   Solution length: {len(case['solution'])} characters")
