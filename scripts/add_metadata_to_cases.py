#!/usr/bin/env python3
"""
Add metadata (category, subcategory, tags) to all cases missing it.

This script intelligently assigns metadata based on:
- Directory name → category
- File name pattern → subcategory
- Content analysis → tags
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Set
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Allowed category values
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

# Technology keywords for tag generation
TECH_KEYWORDS = {
    'firebase', 'firestore', 'auth', 'authentication', 'react', 'typescript',
    'javascript', 'nextjs', 'next.js', 'bootstrap', 'html', 'css', 'rust',
    'actix', 'axum', 'tokio', 'async', 'serde', 'sqlx', 'diesel', 'reqwest',
    'clap', 'leptos', 'tower', 'wasm', 'webassembly', 'rayon', 'crossbeam',
    'node', 'express', 'api', 'rest', 'graphql', 'mongodb', 'postgresql',
    'mysql', 'redis', 'docker', 'kubernetes', 'aws', 'gcp', 'azure'
}

# Pattern keywords for tag generation
PATTERN_KEYWORDS = {
    'validation', 'form', 'routing', 'middleware', 'authentication', 'authorization',
    'session', 'jwt', 'oauth', 'security', 'error-handling', 'logging', 'testing',
    'deployment', 'state-management', 'hooks', 'components', 'ui', 'ux',
    'performance', 'optimization', 'caching', 'websocket', 'sse', 'streaming',
    'database', 'orm', 'migration', 'query', 'transaction', 'concurrency',
    'async-await', 'promise', 'callback', 'event', 'listener', 'handler',
    'pagination', 'search', 'filter', 'sort', 'crud', 'api-integration',
    'http', 'request', 'response', 'json', 'xml', 'csv', 'parser',
    'serialization', 'deserialization', 'encryption', 'hashing', 'token',
    'refresh-token', 'access-token', 'cookie', 'localstorage', 'sessionstorage'
}


def extract_category_from_directory(file_path: Path) -> str:
    """Extract category from directory name."""
    # Get the parent directory name (e.g., 'firebase', 'rust')
    directory = file_path.parent.name

    if directory in ALLOWED_CATEGORIES:
        return directory

    logger.warning(f"Unknown category directory: {directory}")
    return directory


def extract_subcategory_from_filename(file_path: Path) -> str:
    """Extract subcategory from file name pattern."""
    # Get filename without extension (e.g., 'firebase_auth_cases' -> 'firebase_auth_cases')
    filename = file_path.stem

    # Remove '_cases' suffix
    if filename.endswith('_cases'):
        filename = filename[:-6]

    # Get the category from directory
    category = extract_category_from_directory(file_path)

    # Remove category prefix if present (e.g., 'firebase_auth' -> 'auth')
    if filename.startswith(category + '_'):
        subcategory = filename[len(category) + 1:]
    else:
        subcategory = filename

    # Convert to kebab-case
    subcategory = subcategory.replace('_', '-')

    return subcategory


def extract_tags_from_content(problem: str, solution: str, category: str, subcategory: str, existing_tags: List[str] = None) -> List[str]:
    """
    Extract relevant tags from problem and solution text.

    Returns 3-7 relevant tags based on content analysis.
    """
    # If existing tags are provided and within range, just trim them
    if existing_tags and isinstance(existing_tags, list):
        if 3 <= len(existing_tags) <= 7:
            return existing_tags[:7]  # Keep up to 7
        elif len(existing_tags) > 7:
            # Trim to 7, prioritizing important tags
            priority_tags = []

            # Category always first
            if category in existing_tags:
                priority_tags.append(category)

            # Subcategory next if meaningful
            if subcategory and subcategory in existing_tags:
                priority_tags.append(subcategory)

            # Add remaining tags up to 7 total
            for tag in existing_tags:
                if tag not in priority_tags:
                    priority_tags.append(tag)
                if len(priority_tags) >= 7:
                    break

            return priority_tags[:7]

    tags: Set[str] = set()

    # Combine problem and solution text for analysis
    content = f"{problem.lower()} {solution.lower()}"

    # Always include the category as the first tag
    tags.add(category)

    # Check for technology keywords
    for keyword in TECH_KEYWORDS:
        if keyword.lower() in content:
            tags.add(keyword.lower())

    # Check for pattern keywords
    for keyword in PATTERN_KEYWORDS:
        # Handle compound keywords (e.g., 'error-handling')
        keyword_variants = [
            keyword,
            keyword.replace('-', ' '),
            keyword.replace('-', '_'),
            keyword.replace('-', '')
        ]

        for variant in keyword_variants:
            if variant.lower() in content:
                tags.add(keyword.lower())
                break

    # Add subcategory as a tag if it's meaningful
    if subcategory and len(subcategory) > 2:
        tags.add(subcategory)

    # Convert to sorted list and limit to 7 tags
    tag_list = sorted(tags)[:7]

    # Ensure at least 3 tags
    if len(tag_list) < 3:
        # Add generic tags based on category
        category_fallbacks = {
            'firebase': ['database', 'cloud', 'backend'],
            'react': ['frontend', 'ui', 'components'],
            'nextjs': ['ssr', 'routing', 'fullstack'],
            'bootstrap': ['css', 'ui', 'responsive'],
            'webdev': ['web', 'frontend', 'javascript'],
            'orchestration': ['ai', 'agent', 'workflow'],
            'security': ['secure', 'auth', 'encryption'],
            'rust': ['systems', 'performance', 'safe']
        }

        fallbacks = category_fallbacks.get(category, ['programming', 'development', 'code'])
        for fallback in fallbacks:
            if fallback not in tag_list:
                tag_list.append(fallback)
            if len(tag_list) >= 3:
                break

    return tag_list[:7]


def case_needs_metadata(case_dict: Dict[str, Any]) -> bool:
    """Check if a case needs metadata added."""
    return not (
        'category' in case_dict and
        'subcategory' in case_dict and
        'tags' in case_dict
    )


def add_metadata_to_case_dict(case_dict: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
    """Add metadata to a case dictionary if missing or trim tags if too many."""
    # Extract metadata
    category = case_dict.get('category') or extract_category_from_directory(file_path)
    subcategory = case_dict.get('subcategory') or extract_subcategory_from_filename(file_path)

    # Extract tags from content
    problem = case_dict.get('problem', '')
    solution = case_dict.get('solution', '')
    existing_tags = case_dict.get('tags')

    # Always process tags to ensure they're trimmed to 3-7
    tags = extract_tags_from_content(problem, solution, category, subcategory, existing_tags)

    # Set metadata
    case_dict['category'] = category
    case_dict['subcategory'] = subcategory
    case_dict['tags'] = tags

    return case_dict


def format_case_dict(case_dict: Dict[str, Any], indent: int = 4) -> str:
    """Format a case dictionary as Python code."""
    lines = [' ' * indent + '{']

    # Preferred field order
    field_order = ['problem', 'solution', 'category', 'subcategory', 'tags']

    # Add fields in order
    for field in field_order:
        if field in case_dict:
            value = case_dict[field]

            if field in ('problem', 'solution'):
                # Multi-line string
                lines.append(f'{" " * (indent + 4)}"{field}": """')
                # Clean up the solution/problem text
                text = value.strip()
                lines.append(text)
                lines.append('"""' + ',')
            elif field == 'tags':
                # List of tags
                tags_str = repr(value)
                lines.append(f'{" " * (indent + 4)}"{field}": {tags_str}')
            else:
                # Simple string
                lines.append(f'{" " * (indent + 4)}"{field}": {repr(value)},')

    lines.append(' ' * indent + '}')

    return '\n'.join(lines)


def process_case_file(file_path: Path) -> int:
    """
    Process a single case file and add metadata where needed.

    Returns the number of cases that were updated.
    """
    logger.info(f"\nProcessing: {file_path}")

    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse the Python file as AST
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        logger.error(f"Syntax error in {file_path}: {e}")
        return 0

    # Find the case list variable
    case_list_name = None
    case_list_node = None

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.endswith('_CASES'):
                    case_list_name = target.id
                    case_list_node = node.value
                    break

    if not case_list_name:
        logger.warning(f"No case list found in {file_path}")
        return 0

    # Evaluate the case list
    try:
        # Use ast.literal_eval for safe evaluation
        case_list = ast.literal_eval(content.split(f'{case_list_name} = ')[1])
    except:
        logger.error(f"Could not evaluate case list in {file_path}")
        return 0

    # Process each case
    updated_count = 0
    updated_cases = []

    for case in case_list:
        original_tags_count = len(case.get('tags', []))
        case = add_metadata_to_case_dict(case, file_path)
        new_tags_count = len(case.get('tags', []))

        # Track if we made changes
        if case_needs_metadata(case) or original_tags_count != new_tags_count:
            if case_needs_metadata(case):
                updated_count += 1
                logger.info(f"  Added metadata: category={case['category']}, "
                           f"subcategory={case['subcategory']}, tags={case['tags'][:3]}...")
            elif original_tags_count > 7:
                updated_count += 1
                logger.info(f"  Trimmed tags from {original_tags_count} to {new_tags_count}")

        updated_cases.append(case)

    # If any cases were updated, rewrite the file
    if updated_count > 0:
        # Format the updated cases
        cases_str = ',\n'.join(format_case_dict(case) for case in updated_cases)

        # Reconstruct the file content
        # Find the docstring (if it exists)
        docstring_match = re.search(r'^(""".*?""")', content, re.DOTALL | re.MULTILINE)
        docstring = docstring_match.group(1) if docstring_match else ''

        # Find any comments or blank lines before the case list
        case_list_start = content.find(f'{case_list_name} = [')
        prefix = content[:case_list_start] if case_list_start > 0 else ''

        # If we have a docstring, use it; otherwise use the prefix
        if docstring:
            new_content = f"{docstring}\n\n{case_list_name} = [\n{cases_str}\n]\n"
        else:
            # Keep any comments or whitespace before the case list
            new_content = f"{prefix}{case_list_name} = [\n{cases_str}\n]\n"

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        logger.info(f"  Updated {updated_count} case(s) in {file_path.name}")
    else:
        logger.info(f"  No updates needed for {file_path.name}")

    return updated_count


def main():
    """Main function to process all case files."""
    logger.info("=" * 60)
    logger.info("Adding metadata to cases missing it")
    logger.info("=" * 60)

    # Find the cases directory
    cases_dir = Path(__file__).parent.parent / 'cases'

    if not cases_dir.exists():
        logger.error(f"Cases directory not found: {cases_dir}")
        return

    # Find all *_cases.py files
    case_files = list(cases_dir.glob('**/*_cases.py'))
    logger.info(f"\nFound {len(case_files)} case files")

    # Process each file
    total_updated = 0
    for case_file in sorted(case_files):
        updated = process_case_file(case_file)
        total_updated += updated

    logger.info("\n" + "=" * 60)
    logger.info(f"Total cases updated: {total_updated}")
    logger.info("=" * 60)

    # Verify completion
    logger.info("\nVerifying metadata completion...")
    try:
        from cases import ALL_CASES

        total_cases = len(ALL_CASES)
        cases_with_metadata = sum(
            1 for c in ALL_CASES
            if 'category' in c and 'subcategory' in c and 'tags' in c
        )

        logger.info(f"Total cases: {total_cases}")
        logger.info(f"Cases with metadata: {cases_with_metadata}")
        logger.info(f"Completion: {cases_with_metadata}/{total_cases} "
                   f"({100 * cases_with_metadata / total_cases:.1f}%)")

        if cases_with_metadata == total_cases:
            logger.info("\n✅ SUCCESS: All cases now have complete metadata!")
        else:
            logger.warning(f"\n⚠️  WARNING: {total_cases - cases_with_metadata} "
                          f"cases still missing metadata")
    except Exception as e:
        logger.error(f"Failed to verify: {e}")


if __name__ == '__main__':
    main()
