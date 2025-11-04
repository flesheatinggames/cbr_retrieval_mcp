"""Metadata migration for CBR case base enhancement."""

from typing import Any, Tuple


class MetadataMigration:
    """Migrate existing cases to new metadata structure."""

    CATEGORY_PATTERNS = {
        "anti-pattern": {
            "completion-bias": [
                "premature completion",
                "completion bias",
                "satisfaction bias",
            ],
            "verification-skip": ["skip verification", "skipped verification"],
            "protocol-violation": ["protocol violation", "violate protocol"],
        },
        "best-practice": {
            "planning": [
                "planning best",
                "best practice planning",
                "plan structure",
            ],
            "verification": ["verification protocol", "verify best"],
            "error-handling": ["error handling", "error recovery"],
        },
        "orchestration": {
            "remediation": [
                "remediation",
                "fix ",
                "repair",
                "recover",
                "incomplete",
            ],
            "planning": ["plan", "decompose", "decomposition", "breakdown"],
            "delegation": ["delegate", "assign", "agent"],
            "verification": ["verify", "verification", "karen", "validate"],
            "completion": ["complete", "completion", "finish", "done"],
        },
        "code": {
            "firebase-auth": ["firebase", "auth", "authentication", "firebaseauth"],
            "react-components": ["react component", "component", "jsx", "tsx"],
            "api-routes": ["api", "endpoint", "route", "express"],
            "database": ["database", "firestore", "mongodb", "sql"],
            "testing": ["pytest", "jest", "unittest", "test", "fixture"],
        },
    }

    # Explicit precedence order: highest to lowest priority
    PRECEDENCE_ORDER = ["anti-pattern", "best-practice", "orchestration", "code"]

    def detect_category_subcategory(self, problem_text: str) -> Tuple[str, str]:
        """Auto-detect category and subcategory from problem text.

        Checks categories in explicit precedence order (anti-pattern > best-practice
        > orchestration > code) to resolve pattern collisions consistently.

        Args:
            problem_text: Case description or problem statement

        Returns:
            Tuple of (category, subcategory). Defaults to ("code", "general") if no match.
        """
        problem_lower = problem_text.lower()

        # Check categories in explicit precedence order
        for category in self.PRECEDENCE_ORDER:
            subcategories = self.CATEGORY_PATTERNS[category]
            for subcategory, patterns in subcategories.items():
                for pattern in patterns:
                    if pattern in problem_lower:
                        return (category, subcategory)

        return ("code", "general")

    def extract_tags(self, problem_text: str, solution_text: str) -> str:
        """Extract tags from case content."""
        content = f"{problem_text} {solution_text}".lower()

        tech_keywords = [
            "react",
            "firebase",
            "typescript",
            "javascript",
            "python",
            "rust",
            "go",
            "authentication",
            "auth",
            "database",
            "api",
            "testing",
            "orchestration",
            "express",
            "fastapi",
            "next",
            "vue",
            "mongodb",
            "postgresql",
            "mysql",
            "async",
        ]

        found_tags = [tag for tag in tech_keywords if tag in content]
        return ",".join(found_tags) if found_tags else ""

    def migrate_collection(self, collection: Any) -> int:
        """Migrate all documents in collection to new metadata structure.

        Args:
            collection: ChromaDB collection object

        Returns:
            Number of cases migrated
        """
        results = collection.get(include=["documents", "metadatas"])

        # Collect cases to migrate for batched update
        ids_to_update = []
        metadatas_to_update = []

        for i, doc_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i]
            document = results["documents"][i]

            # Skip if already migrated
            if "category" in metadata and "subcategory" in metadata:
                continue

            # Detect category and subcategory
            category, subcategory = self.detect_category_subcategory(document)

            # Extract tags (simplified for MVP)
            tags = self.extract_tags(document, metadata.get("solution", ""))

            # Create new metadata dict with existing fields (shallow copy)
            new_metadata = dict(metadata)
            new_metadata["category"] = category
            new_metadata["subcategory"] = subcategory
            new_metadata["tags"] = tags

            # Add to batched update
            ids_to_update.append(doc_id)
            metadatas_to_update.append(new_metadata)  # Append copy, not original

        # Perform single batched update for efficiency
        if ids_to_update:
            collection.update(ids=ids_to_update, metadatas=metadatas_to_update)

        return len(ids_to_update)
