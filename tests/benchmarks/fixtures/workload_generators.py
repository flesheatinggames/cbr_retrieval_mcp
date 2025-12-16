"""
Workload Generator Module for Benchmark Testing.

This module provides functions to generate realistic workloads for performance testing,
including queries, category searches, load patterns, and case sets.
"""

import random
from typing import Any, Dict, List, Tuple

# =============================================================================
# Query Workload Generators
# =============================================================================


def generate_simple_queries(count: int, seed: int = None) -> List[str]:
    """
    Generate simple queries (< 50 characters).

    Args:
        count: Number of queries to generate
        seed: Optional random seed for reproducibility

    Returns:
        List of simple query strings
    """
    if seed is not None:
        random.seed(seed)

    if count == 0:
        return []

    simple_templates = [
        "user authentication",
        "database query",
        "api endpoint",
        "error handling",
        "form validation",
        "data model",
        "session management",
        "cache implementation",
        "logging setup",
        "config file",
        "unit test",
        "async function",
        "http request",
        "json parsing",
        "file upload",
        "pagination",
        "search filter",
        "date formatting",
        "password hash",
        "token generation",
    ]

    return [random.choice(simple_templates) for _ in range(count)]


def generate_medium_queries(count: int, seed: int = None) -> List[str]:
    """
    Generate medium-complexity queries (50-150 characters).

    Args:
        count: Number of queries to generate
        seed: Optional random seed for reproducibility

    Returns:
        List of medium query strings
    """
    if seed is not None:
        random.seed(seed)

    if count == 0:
        return []

    medium_templates = [
        "implement user authentication with email verification and password reset functionality using firebase auth",
        "create a paginated api endpoint that returns filtered results with sorting and includes error handling",
        "build a form validation system that checks required fields email format and password strength requirements",
        "develop a caching layer for database queries with ttl expiration and automatic invalidation on updates",
        "implement session management with secure cookies jwt tokens and refresh token rotation for api security",
        "create a search functionality with full text indexing filters and autocomplete suggestions for better ux",
        "build an async data processing pipeline that handles large files with progress tracking and error recovery",
        "implement role based access control with permissions groups and hierarchical resource protection patterns",
        "create a notification system with email sms and push notifications including template management features",
        "develop a file upload handler with validation size limits virus scanning and cloud storage integration",
    ]

    return [random.choice(medium_templates) for _ in range(count)]


def generate_complex_queries(count: int, seed: int = None) -> List[str]:
    """
    Generate complex queries (> 150 characters).

    Args:
        count: Number of queries to generate
        seed: Optional random seed for reproducibility

    Returns:
        List of complex query strings
    """
    if seed is not None:
        random.seed(seed)

    if count == 0:
        return []

    complex_templates = [
        "implement a comprehensive user management system with role based access control multi factor authentication email verification password reset workflows account lockout policies session management with jwt tokens and refresh token rotation including audit logging for security compliance and integration with external identity providers like oauth2 and saml for enterprise single sign on capabilities",
        "create a scalable microservices architecture with api gateway service discovery circuit breakers retry logic distributed tracing with opentelemetry centralized logging aggregation metrics collection with prometheus grafana dashboards health checks for kubernetes deployments blue green deployment strategies and comprehensive error handling with graceful degradation patterns for high availability production environments",
        "build a real time data processing pipeline using apache kafka for event streaming with multiple consumer groups schema registry for avro serialization exactly once delivery semantics fault tolerant processing with checkpointing state management for aggregations windowing operations integration with data warehouses for analytics and monitoring dashboards with alerting on processing lag throughput and error rates",
        "develop a comprehensive e commerce platform with product catalog management shopping cart functionality inventory tracking payment processing integration with stripe and paypal order management with order status tracking shipping integration with multiple carriers tax calculation for different jurisdictions customer reviews and ratings recommendation engine promotional codes and discounts reporting and analytics dashboard with sales metrics",
        "implement a content management system with wysiwyg editor media library with image optimization and cdn integration versioning and revision history multi language support with translation workflows role based content approval workflows seo optimization features with meta tags and sitemaps scheduled publishing custom content types with flexible field definitions and a graphql api for headless cms capabilities",
    ]

    return [random.choice(complex_templates) for _ in range(count)]


def generate_mixed_workload(count: int, seed: int = None) -> List[str]:
    """
    Generate a mixed workload with variety of query complexities.

    Distribution: 50% simple, 30% medium, 20% complex

    Args:
        count: Total number of queries to generate
        seed: Optional random seed for reproducibility

    Returns:
        List of mixed query strings
    """
    if seed is not None:
        random.seed(seed)

    if count == 0:
        return []

    # Calculate distribution
    simple_count = int(count * 0.5)
    medium_count = int(count * 0.3)
    complex_count = count - simple_count - medium_count

    queries = []
    queries.extend(generate_simple_queries(simple_count, seed))
    queries.extend(generate_medium_queries(medium_count, seed))
    queries.extend(generate_complex_queries(complex_count, seed))

    # Shuffle to mix them up
    random.shuffle(queries)

    return queries


# =============================================================================
# Category Search Workload Generators
# =============================================================================


def generate_category_searches(count: int, seed: int = None) -> List[Dict[str, Any]]:
    """
    Generate category-only search parameters (no subcategory).

    Args:
        count: Number of searches to generate
        seed: Optional random seed for reproducibility

    Returns:
        List of dictionaries with 'category' key
    """
    if seed is not None:
        random.seed(seed)

    if count == 0:
        return []

    categories = ["orchestration", "web-development", "firebase", "security"]

    return [
        {"category": random.choice(categories), "subcategory": None}
        for _ in range(count)
    ]


def generate_hierarchical_searches(
    count: int, seed: int = None
) -> List[Dict[str, Any]]:
    """
    Generate hierarchical searches with category and subcategory.

    Args:
        count: Number of searches to generate
        seed: Optional random seed for reproducibility

    Returns:
        List of dictionaries with 'category' and 'subcategory' keys
    """
    if seed is not None:
        random.seed(seed)

    if count == 0:
        return []

    hierarchy = {
        "orchestration": ["planning", "delegation", "verification", "remediation"],
        "web-development": ["api", "forms", "routing", "state-management"],
        "firebase": ["authentication", "firestore", "functions"],
        "security": ["authentication", "validation"],
    }

    results = []
    for _ in range(count):
        category = random.choice(list(hierarchy.keys()))
        subcategory = random.choice(hierarchy[category])
        results.append({"category": category, "subcategory": subcategory})

    return results


def generate_tag_filtered_searches(
    count: int, seed: int = None
) -> List[Dict[str, Any]]:
    """
    Generate searches with tag filters.

    Args:
        count: Number of searches to generate
        seed: Optional random seed for reproducibility

    Returns:
        List of dictionaries with 'tags' key
    """
    if seed is not None:
        random.seed(seed)

    if count == 0:
        return []

    all_tags = [
        "python",
        "javascript",
        "react",
        "firebase",
        "authentication",
        "api",
        "database",
        "async",
        "testing",
        "security",
        "performance",
        "caching",
        "logging",
        "error-handling",
    ]

    results = []
    for _ in range(count):
        num_tags = random.randint(1, 3)
        tags = random.sample(all_tags, num_tags)
        results.append({"tags": tags})

    return results


# =============================================================================
# Concurrent Load Pattern Generators
# =============================================================================


def generate_burst_load(burst_size: int, interval_ms: int) -> Dict[str, Any]:
    """
    Generate burst load pattern configuration.

    Args:
        burst_size: Number of requests per burst
        interval_ms: Interval between bursts in milliseconds

    Returns:
        Dictionary describing burst load pattern
    """
    return {
        "pattern_type": "burst",
        "burst_size": burst_size,
        "interval_ms": interval_ms,
    }


def generate_sustained_load(rate_per_sec: int, duration_sec: int) -> Dict[str, Any]:
    """
    Generate sustained load pattern configuration.

    Args:
        rate_per_sec: Requests per second
        duration_sec: Duration in seconds

    Returns:
        Dictionary describing sustained load pattern
    """
    return {
        "pattern_type": "sustained",
        "rate_per_sec": rate_per_sec,
        "duration_sec": duration_sec,
        "total_requests": rate_per_sec * duration_sec,
    }


def generate_ramp_load(
    start_rate: int, end_rate: int, duration_sec: int
) -> Dict[str, Any]:
    """
    Generate ramping load pattern configuration.

    Args:
        start_rate: Starting requests per second
        end_rate: Ending requests per second
        duration_sec: Duration of ramp in seconds

    Returns:
        Dictionary describing ramp load pattern
    """
    return {
        "pattern_type": "ramp",
        "start_rate": start_rate,
        "end_rate": end_rate,
        "duration_sec": duration_sec,
    }


# =============================================================================
# Case Base Workload Generators
# =============================================================================


def generate_case_set(
    num_cases: int, categories: List[str], seed: int = None
) -> List[Dict[str, Any]]:
    """
    Generate a set of test cases distributed across categories.

    Args:
        num_cases: Number of cases to generate
        categories: List of categories to distribute cases across
        seed: Optional random seed for reproducibility

    Returns:
        List of case dictionaries with content and metadata
    """
    if seed is not None:
        random.seed(seed)

    if num_cases == 0:
        return []

    subcategories = {
        "orchestration": ["planning", "delegation", "verification"],
        "web-development": ["api", "forms", "routing"],
        "firebase": ["authentication", "firestore", "functions"],
        "security": ["authentication", "validation"],
    }

    tags_by_category = {
        "orchestration": ["planning", "delegation", "agents"],
        "web-development": ["api", "frontend", "backend"],
        "firebase": ["auth", "database", "serverless"],
        "security": ["auth", "validation", "encryption"],
    }

    cases = []
    for i in range(num_cases):
        category = categories[i % len(categories)]
        subcategory = random.choice(subcategories.get(category, ["general"]))
        tags = random.sample(
            tags_by_category.get(category, ["general"]), k=random.randint(1, 2)
        )

        case = {
            "id": f"case_{i:04d}",
            "content": f"Example {category} case for {subcategory} with implementation details and code samples",
            "metadata": {
                "category": category,
                "subcategory": subcategory,
                "tags": tags,
            },
        }
        cases.append(case)

    return cases


def generate_diverse_embeddings(
    count: int, dimension: int, seed: int = None
) -> List[List[float]]:
    """
    Generate diverse normalized embeddings.

    Args:
        count: Number of embeddings to generate
        dimension: Dimensionality of embeddings
        seed: Optional random seed for reproducibility

    Returns:
        List of embedding vectors (lists of floats)
    """
    if seed is not None:
        random.seed(seed)

    if count == 0:
        return []

    embeddings = []
    for _ in range(count):
        # Generate random vector
        vector = [random.gauss(0, 1) for _ in range(dimension)]
        # Normalize
        magnitude = sum(x**2 for x in vector) ** 0.5
        normalized = [x / magnitude for x in vector]
        embeddings.append(normalized)

    return embeddings


def generate_similar_cases(
    base_case: Dict[str, Any], similarity_level: float, count: int, seed: int = None
) -> List[Dict[str, Any]]:
    """
    Generate cases similar to a base case.

    Args:
        base_case: Base case to generate similar cases from
        similarity_level: Similarity level (0.0-1.0)
        count: Number of similar cases to generate
        seed: Optional random seed for reproducibility

    Returns:
        List of similar case dictionaries
    """
    if seed is not None:
        random.seed(seed)

    if count == 0:
        return []

    cases = []
    base_content = base_case["content"]
    base_category = base_case["metadata"]["category"]

    for i in range(count):
        # Create similar content by modifying base
        similar_content = (
            base_content + f" with additional implementation variant {i+1}"
        )

        case = {
            "id": f"similar_{i:04d}",
            "content": similar_content,
            "metadata": {
                "category": base_category,  # Keep same category for similarity
                "subcategory": base_case["metadata"].get("subcategory", "general"),
                "tags": base_case["metadata"].get("tags", []),
            },
        }
        cases.append(case)

    return cases


# =============================================================================
# Helper Utilities
# =============================================================================


def create_realistic_query_distribution() -> Dict[str, float]:
    """
    Create a realistic query complexity distribution.

    Returns:
        Dictionary with percentage distribution
    """
    return {
        "simple": 50.0,
        "medium": 30.0,
        "complex": 20.0,
    }


def simulate_user_session(duration_sec: int, seed: int = None) -> Dict[str, Any]:
    """
    Simulate a user session with temporal query patterns.

    Args:
        duration_sec: Duration of session in seconds
        seed: Optional random seed for reproducibility

    Returns:
        Dictionary with session information
    """
    if seed is not None:
        random.seed(seed)

    # Generate queries for session
    num_queries = random.randint(3, 10)
    queries = generate_mixed_workload(num_queries, seed)

    # Generate timestamps
    timestamps = sorted([random.uniform(0, duration_sec) for _ in range(num_queries)])

    return {
        "duration_sec": duration_sec,
        "queries": queries,
        "timestamps": timestamps,
        "query_count": num_queries,
    }


def measure_workload_characteristics(queries: List[str]) -> Dict[str, Any]:
    """
    Analyze workload characteristics.

    Args:
        queries: List of query strings

    Returns:
        Dictionary with workload statistics
    """
    if not queries:
        return {
            "avg_length": 0,
            "min_length": 0,
            "max_length": 0,
            "avg_word_count": 0,
            "complexity": "empty",
            "diversity": 0.0,
        }

    lengths = [len(q) for q in queries]
    word_counts = [len(q.split()) for q in queries]
    unique_words = len(set(word for q in queries for word in q.split()))

    return {
        "avg_length": sum(lengths) / len(lengths),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "avg_word_count": sum(word_counts) / len(word_counts),
        "complexity": "mixed",
        "unique_terms": unique_words,
        "diversity": unique_words / sum(word_counts) if sum(word_counts) > 0 else 0.0,
        "variety_score": len(set(lengths)) / len(lengths) if lengths else 0.0,
    }
