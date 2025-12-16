"""
Validation tests for CBR metadata completeness and consistency.

This test module validates that migrated cases have:
1. Complete metadata (category, subcategory, tags fields)
2. Valid category values (from allowed list)
3. Proper tags format (string, comma-separated, lowercase)
4. Consistent subcategory-category relationships

These are integration tests using actual ChromaDB collections.
"""

import os
import shutil
import tempfile
from typing import Any, Dict, List

import chromadb
import pytest
from chromadb.config import Settings

# Category taxonomy from tech_spec.md
VALID_CATEGORIES = ["code", "orchestration", "best-practice", "anti-pattern"]


# Mark all tests in this module for serial execution to avoid database conflicts
# Skip in parallel mode to avoid file descriptor exhaustion (Errno 24: Too many open files)
pytestmark = [
    pytest.mark.xdist_group("serial"),
    pytest.mark.skipif(
        os.environ.get("PYTEST_XDIST_WORKER") is not None,
        reason="ChromaDB file descriptor exhaustion - skip in parallel execution mode",
    ),
]

# Subcategory mappings from tech_spec.md
CATEGORY_SUBCATEGORIES = {
    "code": [
        "firebase-auth",
        "react-components",
        "api-routes",
        "database",
        "testing",
        "general",
    ],
    "orchestration": [
        "remediation",
        "planning",
        "delegation",
        "verification",
        "completion",
    ],
    "best-practice": [
        "planning",
        "verification",
        "error-handling",
    ],
    "anti-pattern": [
        "completion-bias",
        "verification-skip",
        "protocol-violation",
    ],
}


class TestMetadataValidation:
    """Validation tests for metadata completeness and consistency."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary directory for ChromaDB test database."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup after test
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def chroma_client(self, temp_db_path):
        """Create a ChromaDB client with temporary database."""
        client = chromadb.PersistentClient(
            path=temp_db_path, settings=Settings(anonymized_telemetry=False)
        )
        return client

    @pytest.fixture
    def test_collection(self, chroma_client):
        """Create a test collection that gets cleaned up after each test."""
        collection_name = "test_validation_collection"

        # Delete if exists from previous failed test
        try:
            chroma_client.delete_collection(collection_name)
        except Exception:
            pass

        collection = chroma_client.create_collection(
            name=collection_name,
            metadata={"description": "Test collection for validation"},
        )

        yield collection

        # Cleanup
        try:
            chroma_client.delete_collection(collection_name)
        except Exception:
            pass

    def _create_valid_test_cases(self, collection, count: int = 10) -> List[str]:
        """
        Create test cases with valid metadata for validation testing.

        Returns list of case IDs.
        """
        test_cases = [
            {
                "content": "Firebase authentication setup",
                "category": "code",
                "subcategory": "firebase-auth",
                "tags": "firebase,auth,security",
            },
            {
                "content": "React component implementation",
                "category": "code",
                "subcategory": "react-components",
                "tags": "react,frontend,ui",
            },
            {
                "content": "Remediation protocol workflow",
                "category": "orchestration",
                "subcategory": "remediation",
                "tags": "remediation,protocol",
            },
            {
                "content": "Planning decomposition pattern",
                "category": "orchestration",
                "subcategory": "planning",
                "tags": "planning,workflow",
            },
            {
                "content": "Completion bias anti-pattern",
                "category": "anti-pattern",
                "subcategory": "completion-bias",
                "tags": "bias,workflow",
            },
            {
                "content": "API endpoint implementation",
                "category": "code",
                "subcategory": "api-routes",
                "tags": "api,backend,rest",
            },
            {
                "content": "Database query optimization",
                "category": "code",
                "subcategory": "database",
                "tags": "database,optimization",
            },
            {
                "content": "Error handling best practice",
                "category": "best-practice",
                "subcategory": "error-handling",
                "tags": "error,handling,best-practice",
            },
            {
                "content": "Verification protocol pattern",
                "category": "best-practice",
                "subcategory": "verification",
                "tags": "verification,protocol",
            },
            {
                "content": "Testing patterns and practices",
                "category": "code",
                "subcategory": "testing",
                "tags": "testing,patterns",
            },
        ]

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for i in range(count):
            case = test_cases[i % len(test_cases)]
            case_id = f"case_{i:04d}"
            ids.append(case_id)
            documents.append(case["content"])

            # Simple embeddings (not used in validation tests)
            embeddings.append([0.1] * 384)

            metadatas.append(
                {
                    "source": "test_case",
                    "category": case["category"],
                    "subcategory": case["subcategory"],
                    "tags": case["tags"],
                }
            )

        collection.add(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )

        return ids

    def _create_invalid_category_cases(self, collection) -> List[str]:
        """Create test cases with invalid category values."""
        ids = ["invalid_cat_1", "invalid_cat_2"]
        documents = ["Test case 1", "Test case 2"]
        embeddings = [[0.1] * 384, [0.1] * 384]
        metadatas = [
            {
                "source": "test",
                "category": "invalid-category",
                "subcategory": "some-subcat",
                "tags": "",
            },
            {
                "source": "test",
                "category": "wrong-category",
                "subcategory": "another-subcat",
                "tags": "",
            },
        ]

        collection.add(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )

        return ids

    def _create_mismatched_subcategory_cases(self, collection) -> List[str]:
        """Create test cases with mismatched subcategory-category pairs."""
        ids = ["mismatch_1", "mismatch_2", "mismatch_3"]
        documents = ["Test case 1", "Test case 2", "Test case 3"]
        embeddings = [[0.1] * 384] * 3
        metadatas = [
            {
                "source": "test",
                "category": "code",
                "subcategory": "remediation",  # orchestration subcategory
                "tags": "",
            },
            {
                "source": "test",
                "category": "orchestration",
                "subcategory": "firebase-auth",  # code subcategory
                "tags": "",
            },
            {
                "source": "test",
                "category": "anti-pattern",
                "subcategory": "planning",  # orchestration/best-practice subcategory
                "tags": "",
            },
        ]

        collection.add(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )

        return ids

    def _create_invalid_tags_cases(self, collection) -> List[str]:
        """Create test cases with invalid tags format."""
        ids = ["invalid_tags_1", "invalid_tags_2", "invalid_tags_3"]
        documents = ["Test case 1", "Test case 2", "Test case 3"]
        embeddings = [[0.1] * 384] * 3
        metadatas = [
            {
                "source": "test",
                "category": "code",
                "subcategory": "general",
                "tags": "UPPERCASE,Tags,Here",  # uppercase tags
            },
            {
                "source": "test",
                "category": "code",
                "subcategory": "general",
                "tags": "Mixed,CASE,tags",  # mixed case
            },
            {
                "source": "test",
                "category": "code",
                "subcategory": "general",
                "tags": 123,  # non-string tags
            },
        ]

        collection.add(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )

        return ids

    # ========================================================================
    # Category Field Validation Tests
    # ========================================================================

    def test_validate_all_cases_have_category(self, test_collection):
        """
        Validate that all cases have a "category" field with valid values.

        Test from tests.md:
        - All cases have "category" field in metadata
        - All category values are valid (in allowed list)
        """
        # Setup: Create cases with valid categories
        case_ids = self._create_valid_test_cases(test_collection, count=20)

        # Query all cases
        results = test_collection.get(include=["metadatas"])

        # Verify: All cases have category field
        assert len(results["ids"]) == 20, "Expected 20 cases in collection"

        for i, case_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i]

            # Check category field exists
            assert "category" in metadata, f"Case {case_id} missing category field"

            # Check category value is valid
            category = metadata["category"]
            assert (
                category in VALID_CATEGORIES
            ), f"Case {case_id} has invalid category '{category}'. Must be one of {VALID_CATEGORIES}"

    def test_validate_all_cases_have_category_with_invalid(self, test_collection):
        """
        Validate detection of invalid category values.

        This test verifies that validation can detect cases with
        categories not in the allowed list.
        """
        # Setup: Create cases with invalid categories
        invalid_ids = self._create_invalid_category_cases(test_collection)

        # Query all cases
        results = test_collection.get(include=["metadatas"])

        # Verify: Can detect invalid categories
        invalid_categories = []
        for i, case_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i]
            category = metadata.get("category", "")
            if category not in VALID_CATEGORIES:
                invalid_categories.append((case_id, category))

        # Should find 2 invalid categories
        assert (
            len(invalid_categories) == 2
        ), f"Expected 2 invalid categories, found {len(invalid_categories)}"

    # ========================================================================
    # Subcategory Field Validation Tests
    # ========================================================================

    def test_validate_all_cases_have_subcategory(self, test_collection):
        """
        Validate that all cases have a "subcategory" field.

        Test from tests.md:
        - All cases have "subcategory" field
        - All subcategories valid for their category
        """
        # Setup: Create cases with valid subcategories
        case_ids = self._create_valid_test_cases(test_collection, count=15)

        # Query all cases
        results = test_collection.get(include=["metadatas"])

        # Verify: All cases have subcategory field
        assert len(results["ids"]) == 15, "Expected 15 cases in collection"

        for i, case_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i]

            # Check subcategory field exists
            assert (
                "subcategory" in metadata
            ), f"Case {case_id} missing subcategory field"

            # Check subcategory is valid for its category
            category = metadata.get("category", "")
            subcategory = metadata["subcategory"]

            if category in CATEGORY_SUBCATEGORIES:
                valid_subcats = CATEGORY_SUBCATEGORIES[category]
                assert (
                    subcategory in valid_subcats
                ), f"Case {case_id} has invalid subcategory '{subcategory}' for category '{category}'. Valid subcategories: {valid_subcats}"

    # ========================================================================
    # Tags Format Validation Tests
    # ========================================================================

    def test_validate_tags_format(self, test_collection):
        """
        Validate tags field format across all cases.

        Test from tests.md:
        - All tags fields are strings
        - Tags are comma-separated (if not empty)
        - Tags are lowercase
        """
        # Setup: Create cases with valid tags
        case_ids = self._create_valid_test_cases(test_collection, count=10)

        # Query all cases
        results = test_collection.get(include=["metadatas"])

        # Verify: All cases have properly formatted tags
        for i, case_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i]

            # Check tags field exists
            assert "tags" in metadata, f"Case {case_id} missing tags field"

            tags = metadata["tags"]

            # Check tags is a string
            assert isinstance(
                tags, str
            ), f"Case {case_id} tags should be string, got {type(tags)}"

            # If tags not empty, verify comma-separated format
            if tags:
                # Check for lowercase (all characters should be lowercase if alphabetic)
                assert (
                    tags == tags.lower()
                ), f"Case {case_id} tags should be lowercase, got '{tags}'"

                # Verify comma-separated format (no spaces after commas in our standard)
                # Tags should not have leading/trailing whitespace
                assert (
                    tags.strip() == tags
                ), f"Case {case_id} tags should not have leading/trailing whitespace"

    def test_validate_tags_format_with_invalid(self, test_collection):
        """
        Validate detection of invalid tags format.

        This test verifies that validation can detect:
        - Non-string tags
        - Uppercase tags
        - Mixed case tags
        """
        # Setup: Create cases with invalid tags format
        invalid_ids = self._create_invalid_tags_cases(test_collection)

        # Query all cases
        results = test_collection.get(include=["metadatas"])

        # Verify: Can detect invalid tags
        invalid_tags_cases = []
        for i, case_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i]
            tags = metadata.get("tags", "")

            # Check if tags is not a string
            if not isinstance(tags, str):
                invalid_tags_cases.append((case_id, "non-string", tags))
                continue

            # Check if tags has uppercase characters
            if tags and tags != tags.lower():
                invalid_tags_cases.append((case_id, "not-lowercase", tags))

        # Should find 3 invalid cases
        assert (
            len(invalid_tags_cases) == 3
        ), f"Expected 3 invalid tags cases, found {len(invalid_tags_cases)}"

    def test_validate_empty_tags_allowed(self, test_collection):
        """
        Validate that empty tags are allowed.

        Cases without tags should have empty string, not missing field.
        """
        # Setup: Create case with empty tags
        test_collection.add(
            ids=["empty_tags_case"],
            documents=["Test case with no tags"],
            embeddings=[[0.1] * 384],
            metadatas=[
                {
                    "source": "test",
                    "category": "code",
                    "subcategory": "general",
                    "tags": "",  # empty tags
                }
            ],
        )

        # Query case
        results = test_collection.get(ids=["empty_tags_case"], include=["metadatas"])

        metadata = results["metadatas"][0]

        # Verify: Empty tags is valid
        assert "tags" in metadata, "Case should have tags field"
        assert metadata["tags"] == "", "Empty tags should be empty string"
        assert isinstance(
            metadata["tags"], str
        ), "Empty tags should still be string type"

    # ========================================================================
    # Subcategory-Category Consistency Tests
    # ========================================================================

    def test_validate_subcategory_matches_category(self, test_collection):
        """
        Validate that subcategories match their parent categories.

        Test from tests.md:
        - No code cases with orchestration subcategories
        - No orchestration cases with code subcategories
        - All subcategories belong to their parent category
        """
        # Setup: Create cases with valid category-subcategory pairs
        case_ids = self._create_valid_test_cases(test_collection, count=20)

        # Query all cases
        results = test_collection.get(include=["metadatas"])

        # Verify: All subcategories match their categories
        mismatches = []
        for i, case_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i]
            category = metadata.get("category", "")
            subcategory = metadata.get("subcategory", "")

            if category in CATEGORY_SUBCATEGORIES:
                valid_subcats = CATEGORY_SUBCATEGORIES[category]
                if subcategory not in valid_subcats:
                    mismatches.append((case_id, category, subcategory))

        # Should find no mismatches
        assert (
            len(mismatches) == 0
        ), f"Found {len(mismatches)} mismatched subcategory-category pairs: {mismatches}"

    def test_validate_subcategory_matches_category_detects_mismatches(
        self, test_collection
    ):
        """
        Validate detection of mismatched subcategory-category pairs.

        This test verifies that validation can detect:
        - Code categories with orchestration subcategories
        - Orchestration categories with code subcategories
        - Other mismatched pairs
        """
        # Setup: Create cases with mismatched category-subcategory pairs
        mismatch_ids = self._create_mismatched_subcategory_cases(test_collection)

        # Query all cases
        results = test_collection.get(include=["metadatas"])

        # Verify: Can detect mismatches
        mismatches = []
        for i, case_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i]
            category = metadata.get("category", "")
            subcategory = metadata.get("subcategory", "")

            if category in CATEGORY_SUBCATEGORIES:
                valid_subcats = CATEGORY_SUBCATEGORIES[category]
                if subcategory not in valid_subcats:
                    mismatches.append((case_id, category, subcategory))

        # Should find 3 mismatches
        assert (
            len(mismatches) == 3
        ), f"Expected 3 mismatched pairs, found {len(mismatches)}: {mismatches}"

        # Verify specific mismatches
        mismatch_dict = {m[0]: (m[1], m[2]) for m in mismatches}

        # Case 1: code category with orchestration subcategory
        assert "mismatch_1" in mismatch_dict
        assert mismatch_dict["mismatch_1"][0] == "code"
        assert mismatch_dict["mismatch_1"][1] == "remediation"

        # Case 2: orchestration category with code subcategory
        assert "mismatch_2" in mismatch_dict
        assert mismatch_dict["mismatch_2"][0] == "orchestration"
        assert mismatch_dict["mismatch_2"][1] == "firebase-auth"

        # Case 3: anti-pattern category with orchestration/best-practice subcategory
        assert "mismatch_3" in mismatch_dict
        assert mismatch_dict["mismatch_3"][0] == "anti-pattern"
        assert mismatch_dict["mismatch_3"][1] == "planning"

    # ========================================================================
    # Edge Cases and Comprehensive Validation
    # ========================================================================

    def test_validate_empty_collection(self, test_collection):
        """
        Validate that empty collections don't cause errors.
        """
        # Setup: Collection is empty (from fixture)

        # Query all cases
        results = test_collection.get(include=["metadatas"])

        # Verify: No errors, zero cases
        assert len(results["ids"]) == 0, "Empty collection should have zero cases"

    def test_validate_missing_metadata_fields(self, test_collection):
        """
        Validate detection of cases missing required metadata fields.
        """
        # Setup: Create cases with missing metadata fields
        test_collection.add(
            ids=["missing_category", "missing_subcategory", "missing_tags"],
            documents=["Case 1", "Case 2", "Case 3"],
            embeddings=[[0.1] * 384] * 3,
            metadatas=[
                {
                    "source": "test",
                    # missing category
                    "subcategory": "general",
                    "tags": "",
                },
                {
                    "source": "test",
                    "category": "code",
                    # missing subcategory
                    "tags": "",
                },
                {
                    "source": "test",
                    "category": "code",
                    "subcategory": "general",
                    # missing tags
                },
            ],
        )

        # Query all cases
        results = test_collection.get(include=["metadatas"])

        # Verify: Can detect missing fields
        missing_fields = []
        for i, case_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i]

            if "category" not in metadata:
                missing_fields.append((case_id, "category"))
            if "subcategory" not in metadata:
                missing_fields.append((case_id, "subcategory"))
            if "tags" not in metadata:
                missing_fields.append((case_id, "tags"))

        # Should find 3 missing fields
        assert (
            len(missing_fields) == 3
        ), f"Expected 3 missing fields, found {len(missing_fields)}: {missing_fields}"

    def test_validate_complete_metadata_all_categories(self, test_collection):
        """
        Comprehensive validation test covering all categories and subcategories.

        This test verifies that valid cases from all categories pass validation.
        """
        # Setup: Create cases covering all categories and multiple subcategories
        test_cases = []

        # Code category cases
        for subcat in CATEGORY_SUBCATEGORIES["code"]:
            test_cases.append(
                {
                    "id": f"code_{subcat}",
                    "content": f"Test case for {subcat}",
                    "category": "code",
                    "subcategory": subcat,
                    "tags": f"{subcat},test",
                }
            )

        # Orchestration category cases
        for subcat in CATEGORY_SUBCATEGORIES["orchestration"]:
            test_cases.append(
                {
                    "id": f"orch_{subcat}",
                    "content": f"Test case for {subcat}",
                    "category": "orchestration",
                    "subcategory": subcat,
                    "tags": f"{subcat},workflow",
                }
            )

        # Best-practice category cases
        for subcat in CATEGORY_SUBCATEGORIES["best-practice"]:
            test_cases.append(
                {
                    "id": f"best_{subcat}",
                    "content": f"Test case for {subcat}",
                    "category": "best-practice",
                    "subcategory": subcat,
                    "tags": f"{subcat},best-practice",
                }
            )

        # Anti-pattern category cases
        for subcat in CATEGORY_SUBCATEGORIES["anti-pattern"]:
            test_cases.append(
                {
                    "id": f"anti_{subcat}",
                    "content": f"Test case for {subcat}",
                    "category": "anti-pattern",
                    "subcategory": subcat,
                    "tags": f"{subcat},anti-pattern",
                }
            )

        # Add all cases to collection
        ids = [case["id"] for case in test_cases]
        documents = [case["content"] for case in test_cases]
        embeddings = [[0.1] * 384] * len(test_cases)
        metadatas = [
            {
                "source": "test",
                "category": case["category"],
                "subcategory": case["subcategory"],
                "tags": case["tags"],
            }
            for case in test_cases
        ]

        test_collection.add(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )

        # Query all cases
        results = test_collection.get(include=["metadatas"])

        # Verify: All validations pass
        validation_errors = []

        for i, case_id in enumerate(results["ids"]):
            metadata = results["metadatas"][i]

            # Check all required fields present
            if "category" not in metadata:
                validation_errors.append((case_id, "missing category"))
                continue
            if "subcategory" not in metadata:
                validation_errors.append((case_id, "missing subcategory"))
                continue
            if "tags" not in metadata:
                validation_errors.append((case_id, "missing tags"))
                continue

            category = metadata["category"]
            subcategory = metadata["subcategory"]
            tags = metadata["tags"]

            # Check category is valid
            if category not in VALID_CATEGORIES:
                validation_errors.append((case_id, f"invalid category: {category}"))

            # Check subcategory matches category
            if category in CATEGORY_SUBCATEGORIES:
                valid_subcats = CATEGORY_SUBCATEGORIES[category]
                if subcategory not in valid_subcats:
                    validation_errors.append(
                        (
                            case_id,
                            f"mismatched subcategory: {subcategory} for category {category}",
                        )
                    )

            # Check tags format
            if not isinstance(tags, str):
                validation_errors.append((case_id, f"tags not string: {type(tags)}"))
            elif tags and tags != tags.lower():
                validation_errors.append((case_id, f"tags not lowercase: {tags}"))

        # Should have no validation errors
        assert (
            len(validation_errors) == 0
        ), f"Found {len(validation_errors)} validation errors: {validation_errors}"

        # Verify we tested all expected cases
        expected_count = sum(
            len(subcats) for subcats in CATEGORY_SUBCATEGORIES.values()
        )
        assert (
            len(results["ids"]) == expected_count
        ), f"Expected {expected_count} cases, found {len(results['ids'])}"
