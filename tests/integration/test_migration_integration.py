"""
Integration tests for metadata migration script.

These integration tests verify the MetadataMigration class can correctly:
1. Migrate a full collection of unmigrated cases
2. Handle already-migrated collections idempotently
3. Complete partial migrations correctly
4. Categorize content accurately
5. Preserve embeddings during migration

These are TRUE integration tests using actual ChromaDB collections, not mocks.
"""

import shutil
import tempfile
from typing import Any, Dict, List

import chromadb
import numpy as np
import pytest
from chromadb.config import Settings

# Test will fail until MetadataMigration is implemented
try:
    from metadata_migration import MetadataMigration
except ImportError:
    MetadataMigration = None


class TestMetadataMigrationIntegration:
    """Integration tests for the metadata migration script."""

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
        collection_name = "test_migration_collection"

        # Delete if exists from previous failed test
        try:
            chroma_client.delete_collection(collection_name)
        except Exception:
            pass

        collection = chroma_client.create_collection(
            name=collection_name,
            metadata={"description": "Test collection for migration"},
        )

        yield collection

        # Cleanup
        try:
            chroma_client.delete_collection(collection_name)
        except Exception:
            pass

    def _create_unmigrated_cases(self, collection, count: int) -> List[str]:
        """
        Create unmigrated test cases (no category metadata).

        Returns list of case IDs.
        """
        case_contents = [
            "Firebase authentication setup with email/password",
            "React component for user profile display",
            "Remediation protocol for failed verification",
            "Completion bias in task execution",
            "API endpoint for user data retrieval",
            "Next.js routing configuration",
            "Bootstrap responsive navbar component",
            "TypeScript interface for user data",
            "Firebase Firestore query optimization",
            "Error handling for network requests",
            "Form validation with React Hook Form",
            "Authentication middleware for API routes",
            "ChromaDB vector similarity search",
            "Async operation handling in Python",
            "MCP tool implementation example",
            "Code review checklist template",
            "Security audit findings remediation",
            "Production deployment configuration",
            "Test-driven development workflow",
            "Git branch management strategy",
            "Performance optimization patterns",
            "Database schema migration guide",
            "API rate limiting implementation",
            "User permission management system",
            "Real-time data synchronization",
            "Cache invalidation strategy",
            "Logging and monitoring setup",
            "Docker containerization config",
            "CI/CD pipeline configuration",
            "Load balancing setup",
            "Backup and recovery procedures",
            "Data validation patterns",
            "State management with Redux",
            "WebSocket connection handling",
            "File upload processing",
            "Email notification service",
            "Search functionality implementation",
            "Pagination component design",
            "Internationalization setup",
            "Accessibility compliance checklist",
            "Mobile responsive design patterns",
            "Cross-browser compatibility testing",
            "Performance metrics tracking",
            "A/B testing framework",
            "Feature flag implementation",
            "User analytics integration",
            "Error tracking service setup",
            "Documentation generation tools",
            "Code quality metrics dashboard",
            "Dependency management strategy",
        ]

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for i in range(count):
            case_id = f"case_{i:04d}"
            ids.append(case_id)
            documents.append(case_contents[i % len(case_contents)])

            # Create realistic embeddings (384 dimensions for nomic-embed)
            embedding = np.random.randn(384).tolist()
            embeddings.append(embedding)

            # Unmigrated cases have no category metadata
            metadatas.append({"source": "test_case", "created_at": "2025-10-27"})

        collection.add(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )

        return ids

    def _create_migrated_cases(
        self, collection, count: int, start_id: int = 0
    ) -> List[str]:
        """
        Create already-migrated test cases (with complete metadata).

        Returns list of case IDs.
        """
        case_data = [
            {
                "content": "Firebase authentication setup with email/password",
                "category": "code",
                "subcategory": "firebase-auth",
                "tags": "firebase,auth,security",
            },
            {
                "content": "Remediation protocol for failed verification",
                "category": "orchestration",
                "subcategory": "remediation",
                "tags": "protocol,remediation,verification",
            },
            {
                "content": "Completion bias in task execution",
                "category": "anti-pattern",
                "subcategory": "completion-bias",
                "tags": "anti-pattern,bias,workflow",
            },
            {
                "content": "React component for user profile display",
                "category": "code",
                "subcategory": "react-components",
                "tags": "react,ui,frontend",
            },
            {
                "content": "API endpoint for user data retrieval",
                "category": "code",
                "subcategory": "api-routes",
                "tags": "api,backend,rest",
            },
        ]

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for i in range(count):
            case_id = f"migrated_case_{start_id + i:04d}"
            ids.append(case_id)

            case = case_data[i % len(case_data)]
            documents.append(case["content"])

            # Create realistic embeddings
            embedding = np.random.randn(384).tolist()
            embeddings.append(embedding)

            # Already migrated with complete metadata
            metadatas.append(
                {
                    "source": "test_case",
                    "created_at": "2025-10-27",
                    "category": case["category"],
                    "subcategory": case["subcategory"],
                    "tags": case["tags"],
                }
            )

        collection.add(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )

        return ids

    def _get_embeddings(self, collection, ids: List[str]) -> Dict[str, List[float]]:
        """Get embeddings for specified case IDs."""
        results = collection.get(ids=ids, include=["embeddings"])

        return {
            case_id: embedding
            for case_id, embedding in zip(results["ids"], results["embeddings"])
        }

    def _get_metadata(self, collection, ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get metadata for specified case IDs."""
        results = collection.get(ids=ids, include=["metadatas"])

        return {
            case_id: metadata
            for case_id, metadata in zip(results["ids"], results["metadatas"])
        }

    @pytest.mark.skipif(
        MetadataMigration is None, reason="MetadataMigration not yet implemented"
    )
    def test_full_collection_migration(self, test_collection):
        """
        Test Subtask 4.1: Full collection migration.

        Verifies that a complete collection of unmigrated cases gets properly
        categorized without affecting embeddings.
        """
        # Setup: Create 50 unmigrated cases
        case_ids = self._create_unmigrated_cases(test_collection, 50)

        # Get embeddings before migration
        embeddings_before = self._get_embeddings(test_collection, case_ids)

        # Verify cases are unmigrated (no category metadata)
        metadata_before = self._get_metadata(test_collection, case_ids)
        for case_id, metadata in metadata_before.items():
            assert (
                "category" not in metadata
            ), f"Case {case_id} should not have category before migration"
            assert (
                "subcategory" not in metadata
            ), f"Case {case_id} should not have subcategory before migration"
            assert (
                "tags" not in metadata
            ), f"Case {case_id} should not have tags before migration"

        # Execute: Run migration
        migrator = MetadataMigration()
        migrated_count = migrator.migrate_collection(test_collection)

        # Verify: Migration count is correct
        assert migrated_count == 50, f"Expected 50 cases migrated, got {migrated_count}"

        # Verify: All cases now have complete metadata
        metadata_after = self._get_metadata(test_collection, case_ids)
        for case_id, metadata in metadata_after.items():
            assert (
                "category" in metadata
            ), f"Case {case_id} missing category after migration"
            assert (
                "subcategory" in metadata
            ), f"Case {case_id} missing subcategory after migration"
            assert "tags" in metadata, f"Case {case_id} missing tags after migration"

            # Verify metadata values are non-empty
            assert metadata["category"], f"Case {case_id} has empty category"
            assert metadata["subcategory"], f"Case {case_id} has empty subcategory"
            assert isinstance(
                metadata["tags"], str
            ), f"Case {case_id} tags should be a string"

        # Verify: Embeddings unchanged (allow tiny floating-point precision differences)
        embeddings_after = self._get_embeddings(test_collection, case_ids)
        for case_id in case_ids:
            np.testing.assert_allclose(
                embeddings_before[case_id],
                embeddings_after[case_id],
                rtol=1e-6,
                atol=1e-6,
                err_msg=f"Embeddings significantly changed for case {case_id}",
            )

    @pytest.mark.skipif(
        MetadataMigration is None, reason="MetadataMigration not yet implemented"
    )
    def test_idempotent_migration(self, test_collection):
        """
        Test Subtask 4.2: Idempotent migration.

        Verifies that re-running migration on already-migrated data is safe
        and changes nothing.
        """
        # Setup: Create 30 already-migrated cases
        case_ids = self._create_migrated_cases(test_collection, 30)

        # Get state before migration
        embeddings_before = self._get_embeddings(test_collection, case_ids)
        metadata_before = self._get_metadata(test_collection, case_ids)

        # Verify cases are already migrated
        for case_id, metadata in metadata_before.items():
            assert (
                "category" in metadata
            ), f"Test setup error: {case_id} should be migrated"
            assert (
                "subcategory" in metadata
            ), f"Test setup error: {case_id} should be migrated"
            assert "tags" in metadata, f"Test setup error: {case_id} should be migrated"

        # Execute: Run migration on already-migrated collection
        migrator = MetadataMigration()
        migrated_count = migrator.migrate_collection(test_collection)

        # Verify: No cases were migrated
        assert (
            migrated_count == 0
        ), f"Expected 0 cases migrated on idempotent run, got {migrated_count}"

        # Verify: Metadata unchanged
        metadata_after = self._get_metadata(test_collection, case_ids)
        for case_id in case_ids:
            assert (
                metadata_before[case_id] == metadata_after[case_id]
            ), f"Metadata changed for already-migrated case {case_id}"

        # Verify: Embeddings unchanged (allow tiny floating-point precision differences)
        embeddings_after = self._get_embeddings(test_collection, case_ids)
        for case_id in case_ids:
            np.testing.assert_allclose(
                embeddings_before[case_id],
                embeddings_after[case_id],
                rtol=1e-6,
                atol=1e-6,
                err_msg=f"Embeddings significantly changed for case {case_id}",
            )

    @pytest.mark.skipif(
        MetadataMigration is None, reason="MetadataMigration not yet implemented"
    )
    def test_partial_migration_completion(self, test_collection):
        """
        Test Subtask 4.3: Partial migration completion.

        Verifies that migration correctly handles mixed migrated/unmigrated
        collections without affecting already-migrated cases.
        """
        # Setup: Create 25 migrated cases
        migrated_ids = self._create_migrated_cases(test_collection, 25, start_id=0)

        # Setup: Create 25 unmigrated cases
        unmigrated_ids = self._create_unmigrated_cases(test_collection, 25)

        all_ids = migrated_ids + unmigrated_ids

        # Get state before migration
        embeddings_before = self._get_embeddings(test_collection, all_ids)
        migrated_metadata_before = self._get_metadata(test_collection, migrated_ids)

        # Verify initial state
        for case_id in migrated_ids:
            metadata = migrated_metadata_before[case_id]
            assert (
                "category" in metadata
            ), f"Test setup error: {case_id} should be migrated"

        unmigrated_metadata_before = self._get_metadata(test_collection, unmigrated_ids)
        for case_id in unmigrated_ids:
            metadata = unmigrated_metadata_before[case_id]
            assert (
                "category" not in metadata
            ), f"Test setup error: {case_id} should be unmigrated"

        # Execute: Run migration
        migrator = MetadataMigration()
        migrated_count = migrator.migrate_collection(test_collection)

        # Verify: Only 25 new cases were migrated
        assert migrated_count == 25, f"Expected 25 cases migrated, got {migrated_count}"

        # Verify: Previously migrated cases unchanged
        migrated_metadata_after = self._get_metadata(test_collection, migrated_ids)
        for case_id in migrated_ids:
            assert (
                migrated_metadata_before[case_id] == migrated_metadata_after[case_id]
            ), f"Already-migrated case {case_id} was modified"

        # Verify: Previously unmigrated cases now have metadata
        unmigrated_metadata_after = self._get_metadata(test_collection, unmigrated_ids)
        for case_id in unmigrated_ids:
            metadata = unmigrated_metadata_after[case_id]
            assert (
                "category" in metadata
            ), f"Case {case_id} missing category after migration"
            assert (
                "subcategory" in metadata
            ), f"Case {case_id} missing subcategory after migration"
            assert "tags" in metadata, f"Case {case_id} missing tags after migration"

        # Verify: All 50 cases now have complete metadata
        all_metadata_after = self._get_metadata(test_collection, all_ids)
        for case_id, metadata in all_metadata_after.items():
            assert "category" in metadata, f"Case {case_id} missing category"
            assert "subcategory" in metadata, f"Case {case_id} missing subcategory"
            assert "tags" in metadata, f"Case {case_id} missing tags"

        # Verify: Embeddings unchanged for all cases
        embeddings_after = self._get_embeddings(test_collection, all_ids)
        for case_id in all_ids:
            np.testing.assert_array_equal(
                embeddings_before[case_id],
                embeddings_after[case_id],
                err_msg=f"Embeddings changed for case {case_id}",
            )

    @pytest.mark.skipif(
        MetadataMigration is None, reason="MetadataMigration not yet implemented"
    )
    def test_categorization_accuracy(self, test_collection):
        """
        Test categorization accuracy for specific content patterns.

        Verifies that known content patterns are categorized correctly.
        """
        # Setup: Create specific test cases with known content
        test_cases = [
            {
                "id": "firebase_auth_case",
                "content": "Firebase authentication implementation with email and password sign-in",
                "expected_category_keywords": ["firebase", "auth", "code"],
            },
            {
                "id": "remediation_case",
                "content": "Remediation protocol for handling failed verification from karen agent",
                "expected_category_keywords": ["orchestration", "remediation"],
            },
            {
                "id": "completion_bias_case",
                "content": "Completion bias anti-pattern where agent stops after feeling satisfied",
                "expected_category_keywords": ["anti-pattern", "bias", "completion"],
            },
            {
                "id": "react_component_case",
                "content": "React component for displaying user profile with TypeScript interfaces",
                "expected_category_keywords": ["react", "frontend", "code"],
            },
            {
                "id": "api_endpoint_case",
                "content": "API endpoint implementation for user data retrieval with Express",
                "expected_category_keywords": ["api", "backend", "code"],
            },
        ]

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for case in test_cases:
            ids.append(case["id"])
            documents.append(case["content"])
            embeddings.append(np.random.randn(384).tolist())
            metadatas.append({"source": "test_case", "created_at": "2025-10-27"})

        test_collection.add(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )

        # Execute: Run migration
        migrator = MetadataMigration()
        migrated_count = migrator.migrate_collection(test_collection)

        # Verify: All cases migrated
        assert migrated_count == len(
            test_cases
        ), f"Expected {len(test_cases)} cases migrated, got {migrated_count}"

        # Verify: Categorization accuracy
        metadata_after = self._get_metadata(test_collection, ids)

        for case in test_cases:
            case_id = case["id"]
            metadata = metadata_after[case_id]

            # Get category and tags for checking
            category = metadata.get("category", "").lower()
            subcategory = metadata.get("subcategory", "").lower()
            tags = metadata.get("tags", "").lower()

            # Combine all metadata text for keyword checking
            all_metadata_text = f"{category} {subcategory} {tags}"

            # Verify at least one expected keyword appears in metadata
            found_keywords = [
                keyword
                for keyword in case["expected_category_keywords"]
                if keyword.lower() in all_metadata_text
            ]

            assert len(found_keywords) > 0, (
                f"Case {case_id} with content '{case['content']}' "
                f"expected keywords {case['expected_category_keywords']} "
                f"but got category='{category}', subcategory='{subcategory}', tags={tags}"
            )

            # Verify tags is a string
            assert isinstance(
                metadata["tags"], str
            ), f"Case {case_id} tags should be a string"

    @pytest.mark.skipif(
        MetadataMigration is None, reason="MetadataMigration not yet implemented"
    )
    def test_empty_collection_handling(self, test_collection):
        """
        Test that migration handles empty collections gracefully.
        """
        # Setup: Collection is already empty (from fixture)

        # Execute: Run migration on empty collection
        migrator = MetadataMigration()
        migrated_count = migrator.migrate_collection(test_collection)

        # Verify: No errors and zero migrations
        assert (
            migrated_count == 0
        ), f"Expected 0 cases migrated from empty collection, got {migrated_count}"

        # Verify: Collection is still empty
        results = test_collection.get()
        assert len(results["ids"]) == 0, "Collection should remain empty"

    @pytest.mark.skipif(
        MetadataMigration is None, reason="MetadataMigration not yet implemented"
    )
    def test_embedding_preservation(self, test_collection):
        """
        Test that embeddings are never modified during migration.

        This test focuses specifically on embedding integrity to ensure
        vector search functionality is not affected.
        """
        # Setup: Create 10 cases with specific embeddings
        case_count = 10
        case_ids = []
        original_embeddings = {}

        for i in range(case_count):
            case_id = f"embedding_test_{i:04d}"
            case_ids.append(case_id)

            # Create distinctive embeddings for each case
            embedding = np.random.randn(384)
            # Add case-specific pattern to make them distinctive
            embedding[i] = 100.0  # Distinctive marker
            original_embeddings[case_id] = embedding.tolist()

        test_collection.add(
            ids=case_ids,
            documents=[f"Test case content {i}" for i in range(case_count)],
            embeddings=[original_embeddings[case_id] for case_id in case_ids],
            metadatas=[{"source": "test"} for _ in range(case_count)],
        )

        # Execute: Run migration
        migrator = MetadataMigration()
        migrated_count = migrator.migrate_collection(test_collection)

        # Verify: All cases migrated
        assert migrated_count == case_count, f"Expected {case_count} migrations"

        # Verify: Embeddings are exactly identical
        embeddings_after = self._get_embeddings(test_collection, case_ids)

        for case_id in case_ids:
            original = np.array(original_embeddings[case_id])
            after = np.array(embeddings_after[case_id])

            # Check near-equality (allow tiny floating-point precision differences)
            # ChromaDB may introduce minimal precision differences during storage/retrieval
            np.testing.assert_allclose(
                original,
                after,
                rtol=1e-6,  # relative tolerance
                atol=1e-6,  # absolute tolerance
                err_msg=f"Embedding significantly changed for {case_id}",
            )

            # Check no NaN or Inf values introduced
            assert not np.any(np.isnan(after)), f"NaN values in embedding for {case_id}"
            assert not np.any(np.isinf(after)), f"Inf values in embedding for {case_id}"

            # Verify distinctive marker still present (with tolerance)
            expected_marker = 100.0
            actual_marker = after[int(case_id.split("_")[-1])]
            assert (
                abs(actual_marker - expected_marker) < 1e-5
            ), f"Distinctive marker lost for {case_id}: expected {expected_marker}, got {actual_marker}"
