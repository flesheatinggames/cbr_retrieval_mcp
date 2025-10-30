"""
Unit tests for MetadataMigration.detect_category_subcategory method.

This test module follows TDD approach - tests are written before implementation.
Tests should initially fail (red phase) until the actual implementation is created.
"""

import pytest
from typing import Tuple
from metadata_migration import MetadataMigration


class TestMetadataMigrationDetectCategorySubcategory:
    """Test suite for MetadataMigration.detect_category_subcategory method."""

    @pytest.fixture
    def migration(self):
        """Fixture providing MetadataMigration instance for tests."""
        return MetadataMigration()

    # ========================================================================
    # Code Category Detection Tests
    # ========================================================================

    def test_detect_firebase_auth(self, migration):
        """Test detection of Firebase authentication as code/firebase-auth."""
        result = migration.detect_category_subcategory("Firebase authentication")
        assert result == ("code", "firebase-auth")

    def test_detect_firebase_auth_case_insensitive(self, migration):
        """Test Firebase auth detection is case-insensitive."""
        result = migration.detect_category_subcategory("firebase AUTHENTICATION")
        assert result == ("code", "firebase-auth")

    def test_detect_auth_keyword(self, migration):
        """Test detection of 'auth' keyword triggers firebase-auth."""
        result = migration.detect_category_subcategory("auth implementation")
        assert result == ("code", "firebase-auth")

    def test_detect_firebaseauth_keyword(self, migration):
        """Test detection of 'firebaseauth' keyword triggers firebase-auth."""
        result = migration.detect_category_subcategory("firebaseauth setup")
        assert result == ("code", "firebase-auth")

    def test_detect_react_components(self, migration):
        """Test detection of React component as code/react-components."""
        result = migration.detect_category_subcategory("React component")
        assert result == ("code", "react-components")

    def test_detect_react_components_case_insensitive(self, migration):
        """Test React component detection is case-insensitive."""
        result = migration.detect_category_subcategory("REACT COMPONENT")
        assert result == ("code", "react-components")

    def test_detect_component_keyword(self, migration):
        """Test detection of 'component' keyword triggers react-components."""
        result = migration.detect_category_subcategory("component structure")
        assert result == ("code", "react-components")

    def test_detect_jsx_keyword(self, migration):
        """Test detection of 'jsx' keyword triggers react-components."""
        result = migration.detect_category_subcategory("jsx template")
        assert result == ("code", "react-components")

    def test_detect_tsx_keyword(self, migration):
        """Test detection of 'tsx' keyword triggers react-components."""
        result = migration.detect_category_subcategory("tsx file")
        assert result == ("code", "react-components")

    def test_detect_api_route(self, migration):
        """Test detection of API route as code/api-routes."""
        result = migration.detect_category_subcategory("API route")
        assert result == ("code", "api-routes")

    def test_detect_api_endpoint(self, migration):
        """Test detection of API endpoint as code/api-routes."""
        result = migration.detect_category_subcategory("API endpoint")
        assert result == ("code", "api-routes")

    def test_detect_route_keyword(self, migration):
        """Test detection of 'route' keyword triggers api-routes."""
        result = migration.detect_category_subcategory("route handler")
        assert result == ("code", "api-routes")

    def test_detect_express_keyword(self, migration):
        """Test detection of 'express' keyword triggers api-routes."""
        result = migration.detect_category_subcategory("express server")
        assert result == ("code", "api-routes")

    def test_detect_database_query(self, migration):
        """Test detection of database query as code/database."""
        result = migration.detect_category_subcategory("database query")
        assert result == ("code", "database")

    def test_detect_database_case_insensitive(self, migration):
        """Test database detection is case-insensitive."""
        result = migration.detect_category_subcategory("DATABASE QUERY")
        assert result == ("code", "database")

    def test_detect_firestore_keyword(self, migration):
        """Test detection of 'firestore' keyword triggers database."""
        result = migration.detect_category_subcategory("firestore collection")
        assert result == ("code", "database")

    def test_detect_mongodb_keyword(self, migration):
        """Test detection of 'mongodb' keyword triggers database."""
        result = migration.detect_category_subcategory("mongodb connection")
        assert result == ("code", "database")

    def test_detect_sql_keyword(self, migration):
        """Test detection of 'sql' keyword triggers database."""
        result = migration.detect_category_subcategory("sql query")
        assert result == ("code", "database")

    def test_detect_test_pattern(self, migration):
        """Test detection of test pattern as code/testing."""
        result = migration.detect_category_subcategory("test pattern")
        assert result == ("code", "testing")

    def test_detect_jest_keyword(self, migration):
        """Test detection of 'jest' keyword triggers testing."""
        result = migration.detect_category_subcategory("jest test suite")
        assert result == ("code", "testing")

    def test_detect_pytest_keyword(self, migration):
        """Test detection of 'pytest' keyword triggers testing."""
        result = migration.detect_category_subcategory("pytest fixture")
        assert result == ("code", "testing")

    def test_detect_unittest_keyword(self, migration):
        """Test detection of 'unittest' keyword triggers testing."""
        result = migration.detect_category_subcategory("unittest module")
        assert result == ("code", "testing")

    def test_detect_code_general_fallback(self, migration):
        """Test unmatched code text defaults to code/general."""
        result = migration.detect_category_subcategory(
            "some random code implementation"
        )
        assert result == ("code", "general")

    # ========================================================================
    # Orchestration Category Detection Tests
    # ========================================================================

    def test_detect_remediation_protocol(self, migration):
        """Test detection of remediation protocol as orchestration/remediation."""
        result = migration.detect_category_subcategory("remediation protocol")
        assert result == ("orchestration", "remediation")

    def test_detect_karen_incomplete(self, migration):
        """Test detection of karen INCOMPLETE as orchestration/remediation."""
        result = migration.detect_category_subcategory("karen INCOMPLETE feedback")
        assert result == ("orchestration", "remediation")

    def test_detect_fix_keyword(self, migration):
        """Test detection of 'fix' keyword triggers remediation."""
        result = migration.detect_category_subcategory("fix the issue")
        assert result == ("orchestration", "remediation")

    def test_detect_repair_keyword(self, migration):
        """Test detection of 'repair' keyword triggers remediation."""
        result = migration.detect_category_subcategory("repair the code")
        assert result == ("orchestration", "remediation")

    def test_detect_recover_keyword(self, migration):
        """Test detection of 'recover' keyword triggers remediation."""
        result = migration.detect_category_subcategory("recover from error")
        assert result == ("orchestration", "remediation")

    def test_detect_planning(self, migration):
        """Test detection of planning as orchestration/planning."""
        result = migration.detect_category_subcategory("planning phase")
        assert result == ("orchestration", "planning")

    def test_detect_decomposition(self, migration):
        """Test detection of decomposition as orchestration/planning."""
        result = migration.detect_category_subcategory("task decomposition")
        assert result == ("orchestration", "planning")

    def test_detect_plan_keyword(self, migration):
        """Test detection of 'plan' keyword triggers planning."""
        result = migration.detect_category_subcategory("plan the approach")
        assert result == ("orchestration", "planning")

    def test_detect_decompose_keyword(self, migration):
        """Test detection of 'decompose' keyword triggers planning."""
        result = migration.detect_category_subcategory("decompose the task")
        assert result == ("orchestration", "planning")

    def test_detect_breakdown_keyword(self, migration):
        """Test detection of 'breakdown' keyword triggers planning."""
        result = migration.detect_category_subcategory("breakdown of steps")
        assert result == ("orchestration", "planning")

    def test_detect_delegation(self, migration):
        """Test detection of delegate to agent as orchestration/delegation."""
        result = migration.detect_category_subcategory("delegate to agent")
        assert result == ("orchestration", "delegation")

    def test_detect_delegate_keyword(self, migration):
        """Test detection of 'delegate' keyword triggers delegation."""
        result = migration.detect_category_subcategory("delegate the work")
        assert result == ("orchestration", "delegation")

    def test_detect_assign_keyword(self, migration):
        """Test detection of 'assign' keyword triggers delegation."""
        result = migration.detect_category_subcategory("assign to specialist")
        assert result == ("orchestration", "delegation")

    def test_detect_agent_keyword(self, migration):
        """Test detection of 'agent' keyword triggers delegation."""
        result = migration.detect_category_subcategory("agent handles task")
        assert result == ("orchestration", "delegation")

    def test_detect_verification_with_karen(self, migration):
        """Test detection of verification with karen as orchestration/verification."""
        result = migration.detect_category_subcategory("karen verification")
        assert result == ("orchestration", "verification")

    def test_detect_verification_keyword(self, migration):
        """Test detection of verification keyword as orchestration/verification."""
        result = migration.detect_category_subcategory("verification step")
        assert result == ("orchestration", "verification")

    def test_detect_verify_keyword(self, migration):
        """Test detection of 'verify' keyword triggers verification."""
        result = migration.detect_category_subcategory("verify the output")
        assert result == ("orchestration", "verification")

    def test_detect_karen_keyword(self, migration):
        """Test detection of 'karen' keyword triggers verification."""
        result = migration.detect_category_subcategory("karen review")
        assert result == ("orchestration", "verification")

    def test_detect_validate_keyword(self, migration):
        """Test detection of 'validate' keyword triggers verification."""
        result = migration.detect_category_subcategory("validate the result")
        assert result == ("orchestration", "verification")

    def test_detect_task_completion(self, migration):
        """Test detection of task completion as orchestration/completion."""
        result = migration.detect_category_subcategory("task completion protocol")
        assert result == ("orchestration", "completion")

    def test_detect_complete_keyword(self, migration):
        """Test detection of 'complete' keyword triggers completion."""
        result = migration.detect_category_subcategory("complete the task")
        assert result == ("orchestration", "completion")

    def test_detect_finish_keyword(self, migration):
        """Test detection of 'finish' keyword triggers completion."""
        result = migration.detect_category_subcategory("finish the work")
        assert result == ("orchestration", "completion")

    def test_detect_done_keyword(self, migration):
        """Test detection of 'done' keyword triggers completion."""
        result = migration.detect_category_subcategory("mark as done")
        assert result == ("orchestration", "completion")

    def test_detect_orchestration_case_insensitive(self, migration):
        """Test orchestration detection is case-insensitive."""
        result = migration.detect_category_subcategory("DELEGATE TO AGENT")
        assert result == ("orchestration", "delegation")

    # ========================================================================
    # Best-Practice Category Detection Tests
    # ========================================================================

    def test_detect_best_practice_planning(self, migration):
        """Test detection of best practice planning."""
        result = migration.detect_category_subcategory("best practice planning")
        assert result == ("best-practice", "planning")

    def test_detect_verification_protocol(self, migration):
        """Test detection of verification protocol as best-practice."""
        result = migration.detect_category_subcategory("verification protocol")
        assert result == ("best-practice", "verification")

    def test_detect_error_handling(self, migration):
        """Test detection of error handling as best-practice."""
        result = migration.detect_category_subcategory("error handling pattern")
        assert result == ("best-practice", "error-handling")

    def test_detect_error_recovery(self, migration):
        """Test detection of error recovery as best-practice."""
        result = migration.detect_category_subcategory("error recovery strategy")
        assert result == ("best-practice", "error-handling")

    def test_detect_best_practice_case_insensitive(self, migration):
        """Test best-practice detection is case-insensitive."""
        result = migration.detect_category_subcategory("ERROR HANDLING")
        assert result == ("best-practice", "error-handling")

    # ========================================================================
    # Anti-Pattern Category Detection Tests
    # ========================================================================

    def test_detect_premature_completion(self, migration):
        """Test detection of premature completion as anti-pattern."""
        result = migration.detect_category_subcategory("premature completion issue")
        assert result == ("anti-pattern", "completion-bias")

    def test_detect_satisfaction_bias(self, migration):
        """Test detection of satisfaction bias as anti-pattern."""
        result = migration.detect_category_subcategory("satisfaction bias problem")
        assert result == ("anti-pattern", "completion-bias")

    def test_detect_skip_verification(self, migration):
        """Test detection of skip verification as anti-pattern."""
        result = migration.detect_category_subcategory("skip verification step")
        assert result == ("anti-pattern", "verification-skip")

    def test_detect_protocol_violation(self, migration):
        """Test detection of protocol violation as anti-pattern."""
        result = migration.detect_category_subcategory("protocol violation occurred")
        assert result == ("anti-pattern", "protocol-violation")

    def test_detect_anti_pattern_case_insensitive(self, migration):
        """Test anti-pattern detection is case-insensitive."""
        result = migration.detect_category_subcategory("PREMATURE COMPLETION")
        assert result == ("anti-pattern", "completion-bias")

    # ========================================================================
    # Edge Case Tests
    # ========================================================================

    def test_empty_string_returns_default(self, migration):
        """Test empty string returns default code/general category."""
        result = migration.detect_category_subcategory("")
        assert result == ("code", "general")

    def test_whitespace_only_returns_default(self, migration):
        """Test whitespace-only string returns default code/general category."""
        result = migration.detect_category_subcategory("   \n\t  ")
        assert result == ("code", "general")

    def test_case_insensitive_matching_mixed_case(self, migration):
        """Test case insensitive matching with mixed case input."""
        result = migration.detect_category_subcategory("FiReBase AuThEnTiCaTiOn")
        assert result == ("code", "firebase-auth")

    def test_multiple_pattern_precedence_orchestration_over_code(self, migration):
        """
        Test precedence when text matches multiple patterns.
        Orchestration patterns should take precedence over code patterns.
        """
        # Text contains both "verification" (orchestration) and "test" (code)
        result = migration.detect_category_subcategory(
            "verification test for delegate to agent"
        )
        # Should prioritize orchestration category
        assert result[0] == "orchestration"

    def test_multiple_pattern_precedence_anti_pattern_highest(self, migration):
        """
        Test anti-pattern has highest precedence.
        Anti-patterns should be detected even when other patterns present.
        """
        result = migration.detect_category_subcategory(
            "premature completion during planning phase"
        )
        assert result == ("anti-pattern", "completion-bias")

    def test_partial_word_no_match(self, migration):
        """Test partial word matches don't trigger detection."""
        # "fire" should not match "firebase"
        result = migration.detect_category_subcategory("fire alarm system")
        assert result == ("code", "general")

    def test_special_characters_in_text(self, migration):
        """Test handling of special characters in problem text."""
        result = migration.detect_category_subcategory(
            "Firebase authentication with @special #characters!"
        )
        assert result == ("code", "firebase-auth")

    def test_multiline_text_detection(self, migration):
        """Test pattern detection works across multiple lines."""
        multiline_text = """
    This is a test case about
    API endpoint implementation
    with multiple lines
    """
        result = migration.detect_category_subcategory(multiline_text)
        assert result == ("code", "api-routes")

    def test_unicode_text_handling(self, migration):
        """Test handling of unicode characters in problem text."""
        result = migration.detect_category_subcategory(
            "Firebase authentication 认证 with unicode"
        )
        assert result == ("code", "firebase-auth")


class TestMetadataMigrationExtractTags:
    """Test suite for MetadataMigration.extract_tags method."""

    @pytest.fixture
    def migration(self):
        """Fixture providing MetadataMigration instance for tests."""
        return MetadataMigration()

    # ========================================================================
    # Single Technology Keyword Detection Tests
    # ========================================================================

    def test_extract_react_tag(self, migration):
        """Test extraction of 'react' tag from React component text."""
        result = migration.extract_tags("React component", "")
        assert result == "react"

    def test_extract_firebase_authentication_tags(self, migration):
        """Test extraction of multiple tags from Firebase authentication text."""
        result = migration.extract_tags("Firebase authentication", "")
        assert "authentication" in result and "firebase" in result

    def test_extract_typescript_tag(self, migration):
        """Test extraction of 'typescript' tag from TypeScript interface text."""
        result = migration.extract_tags("TypeScript interface", "")
        assert result == "typescript"

    def test_extract_api_express_tags(self, migration):
        """Test extraction of multiple tags from API endpoint with Express."""
        result = migration.extract_tags("API endpoint with Express", "")
        assert "api" in result and "express" in result

    def test_extract_mongodb_database_tags(self, migration):
        """Test extraction of multiple tags from MongoDB database text."""
        result = migration.extract_tags("MongoDB database", "")
        assert "database" in result and "mongodb" in result

    # ========================================================================
    # Multiple Tags Extraction Tests
    # ========================================================================

    def test_extract_multiple_tags_react_firebase_typescript(self, migration):
        """Test extraction of multiple technology tags from combined text."""
        result = migration.extract_tags("React Firebase TypeScript app", "")
        assert "firebase" in result and "react" in result and "typescript" in result

    def test_extract_multiple_tags_python_fastapi_postgresql(self, migration):
        """Test extraction of backend technology stack tags."""
        result = migration.extract_tags("Python FastAPI PostgreSQL backend", "")
        assert "fastapi" in result and "postgresql" in result and "python" in result

    # ========================================================================
    # Case Insensitivity Tests
    # ========================================================================

    def test_extract_tags_case_insensitive_uppercase(self, migration):
        """Test tag extraction is case-insensitive for uppercase input."""
        result = migration.extract_tags("REACT Component", "")
        assert result == "react"

    def test_extract_tags_case_insensitive_mixed_case(self, migration):
        """Test tag extraction is case-insensitive for mixed case input."""
        result = migration.extract_tags("firebase AUTH", "")
        assert "auth" in result and "firebase" in result

    # ========================================================================
    # Edge Case Tests
    # ========================================================================

    def test_extract_tags_empty_string(self, migration):
        """Test empty string returns empty string."""
        result = migration.extract_tags("", "")
        assert result == ""

    def test_extract_tags_no_keywords(self, migration):
        """Test text with no recognizable keywords returns empty string."""
        result = migration.extract_tags("some random text without technology words", "")
        assert result == ""

    def test_extract_tags_duplicate_keywords(self, migration):
        """Test duplicate keywords appear only once in result."""
        result = migration.extract_tags(
            "React component with React hooks and React state", ""
        )
        assert result == "react"

    def test_extract_tags_special_characters(self, migration):
        """Test tag extraction handles special characters correctly."""
        result = migration.extract_tags(
            "React @component #with $special !characters & Firebase", ""
        )
        assert "firebase" in result and "react" in result

    def test_extract_tags_multiline_text(self, migration):
        """Test tag extraction works across multiple lines."""
        multiline_text = """
        This is a project using
        React and TypeScript
        with Firebase backend
        """
        result = migration.extract_tags(multiline_text, "")
        assert "firebase" in result and "react" in result and "typescript" in result

    # ========================================================================
    # Common Technology Keywords Tests
    # ========================================================================

    def test_extract_language_tags(self, migration):
        """Test extraction of programming language tags."""
        result = migration.extract_tags("Python JavaScript TypeScript Rust Go code", "")
        assert (
            "go" in result
            and "javascript" in result
            and "python" in result
            and "rust" in result
            and "typescript" in result
        )

    def test_extract_framework_tags(self, migration):
        """Test extraction of framework tags."""
        result = migration.extract_tags(
            "React Next Vue Express FastAPI application", ""
        )
        assert (
            "express" in result
            and "fastapi" in result
            and "next" in result
            and "react" in result
            and "vue" in result
        )

    def test_extract_database_tags(self, migration):
        """Test extraction of database technology tags."""
        result = migration.extract_tags(
            "Firebase MongoDB PostgreSQL MySQL database", ""
        )
        assert (
            "database" in result
            and "firebase" in result
            and "mongodb" in result
            and "mysql" in result
            and "postgresql" in result
        )

    def test_extract_concept_tags(self, migration):
        """Test extraction of concept-based tags."""
        result = migration.extract_tags(
            "API authentication async testing implementation", ""
        )
        assert (
            "api" in result
            and "async" in result
            and "authentication" in result
            and "testing" in result
        )

    def test_extract_auth_tag(self, migration):
        """Test extraction of 'auth' tag (authentication shorthand)."""
        result = migration.extract_tags("user auth system", "")
        assert result == "auth"

    # ========================================================================
    # Additional Edge Cases
    # ========================================================================

    def test_extract_tags_whitespace_only(self, migration):
        """Test whitespace-only string returns empty string."""
        result = migration.extract_tags("   \n\t  ", "")
        assert result == ""

    def test_extract_tags_partial_word_no_match(self, migration):
        """Test partial word matches don't trigger tag extraction."""
        # "fire" should not match "firebase"
        result = migration.extract_tags("fire alarm system", "")
        assert result == ""

    def test_extract_tags_unicode_text(self, migration):
        """Test tag extraction handles unicode characters correctly."""
        result = migration.extract_tags("React 组件 with Firebase 认证", "")
        assert "firebase" in result and "react" in result

    def test_extract_tags_lowercase_output(self, migration):
        """Test all extracted tags are returned in lowercase."""
        result = migration.extract_tags("REACT Component WITH TypeScript", "")
        # Check that the result is a string with lowercase content
        assert result == result.lower()
        assert "react" in result and "typescript" in result


class TestMetadataMigrationMigrateCollection:
    """Test suite for MetadataMigration.migrate_collection method."""

    @pytest.fixture
    def migration(self):
        """Fixture providing MetadataMigration instance for tests."""
        return MetadataMigration()

    @pytest.fixture
    def mock_collection(self):
        """Create a mock ChromaDB collection."""

        class MockCollection:
            def __init__(self):
                self.documents = []
                self.metadatas = []
                self.ids = []
                self.update_calls = []

            def get(self, include=None):
                """Simulate ChromaDB collection.get()."""
                return {
                    "documents": self.documents,
                    "metadatas": self.metadatas,
                    "ids": self.ids,
                }

            def update(self, ids, metadatas):
                """Simulate ChromaDB collection.update()."""
                self.update_calls.append({"ids": ids, "metadatas": metadatas})

            def add_case(self, doc_id, document, metadata):
                """Helper to add test cases."""
                self.ids.append(doc_id)
                self.documents.append(document)
                self.metadatas.append(metadata)

        return MockCollection()

    # ========================================================================
    # Basic Migration Tests
    # ========================================================================

    def test_migrate_empty_collection(self, migration, mock_collection):
        """Test migration of empty collection returns 0."""
        result = migration.migrate_collection(mock_collection)
        assert result == 0
        assert len(mock_collection.update_calls) == 0

    def test_migrate_single_case(self, migration, mock_collection):
        """Test migration of single case."""
        mock_collection.add_case(
            doc_id="case-1",
            document="Firebase authentication setup",
            metadata={"source": "example.py"},
        )

        result = migration.migrate_collection(mock_collection)

        assert result == 1
        assert len(mock_collection.update_calls) == 1
        updated_metadata = mock_collection.update_calls[0]["metadatas"][0]
        assert "category" in updated_metadata
        assert "subcategory" in updated_metadata
        assert "tags" in updated_metadata
        assert updated_metadata["source"] == "example.py"  # preserved

    def test_migrate_multiple_cases(self, migration, mock_collection):
        """Test migration of multiple cases."""
        mock_collection.add_case(
            doc_id="case-1",
            document="Firebase authentication setup",
            metadata={"source": "example1.py"},
        )
        mock_collection.add_case(
            doc_id="case-2",
            document="React component implementation",
            metadata={"source": "example2.py"},
        )
        mock_collection.add_case(
            doc_id="case-3",
            document="API endpoint creation",
            metadata={"source": "example3.py"},
        )

        result = migration.migrate_collection(mock_collection)

        assert result == 3
        assert len(mock_collection.update_calls) == 1
        updated_metadatas = mock_collection.update_calls[0]["metadatas"]
        assert len(updated_metadatas) == 3
        # Verify all cases have new metadata
        for metadata in updated_metadatas:
            assert "category" in metadata
            assert "subcategory" in metadata
            assert "tags" in metadata

    def test_migrate_returns_correct_count(self, migration, mock_collection):
        """Test migration returns accurate count of migrated cases."""
        for i in range(5):
            mock_collection.add_case(
                doc_id=f"case-{i}",
                document=f"Test case {i}",
                metadata={"source": f"example{i}.py"},
            )

        result = migration.migrate_collection(mock_collection)

        assert result == 5

    def test_migrate_updates_metadata_in_place(self, migration, mock_collection):
        """Test migration calls collection.update() correctly."""
        mock_collection.add_case(
            doc_id="case-1",
            document="Firebase authentication",
            metadata={"source": "example.py"},
        )
        mock_collection.add_case(
            doc_id="case-2",
            document="React component",
            metadata={"source": "example2.py"},
        )

        migration.migrate_collection(mock_collection)

        assert len(mock_collection.update_calls) == 1
        update_call = mock_collection.update_calls[0]
        assert "ids" in update_call
        assert "metadatas" in update_call
        assert len(update_call["ids"]) == 2
        assert len(update_call["metadatas"]) == 2

    # ========================================================================
    # Metadata Handling Tests
    # ========================================================================

    def test_migrate_adds_category_field(self, migration, mock_collection):
        """Test migration adds category to metadata."""
        mock_collection.add_case(
            doc_id="case-1",
            document="Firebase authentication setup",
            metadata={"source": "example.py"},
        )

        migration.migrate_collection(mock_collection)

        updated_metadata = mock_collection.update_calls[0]["metadatas"][0]
        assert "category" in updated_metadata
        assert updated_metadata["category"] == "code"

    def test_migrate_adds_subcategory_field(self, migration, mock_collection):
        """Test migration adds subcategory to metadata."""
        mock_collection.add_case(
            doc_id="case-1",
            document="Firebase authentication setup",
            metadata={"source": "example.py"},
        )

        migration.migrate_collection(mock_collection)

        updated_metadata = mock_collection.update_calls[0]["metadatas"][0]
        assert "subcategory" in updated_metadata
        assert updated_metadata["subcategory"] == "firebase-auth"

    def test_migrate_adds_tags_field(self, migration, mock_collection):
        """Test migration adds tags to metadata."""
        mock_collection.add_case(
            doc_id="case-1",
            document="Firebase authentication with React",
            metadata={"source": "example.py"},
        )

        migration.migrate_collection(mock_collection)

        updated_metadata = mock_collection.update_calls[0]["metadatas"][0]
        assert "tags" in updated_metadata
        assert "firebase" in updated_metadata["tags"]

    def test_migrate_preserves_existing_metadata(self, migration, mock_collection):
        """Test migration preserves existing metadata fields."""
        mock_collection.add_case(
            doc_id="case-1",
            document="Firebase authentication",
            metadata={
                "source": "example.py",
                "author": "test-author",
                "version": "1.0",
            },
        )

        migration.migrate_collection(mock_collection)

        updated_metadata = mock_collection.update_calls[0]["metadatas"][0]
        assert updated_metadata["source"] == "example.py"
        assert updated_metadata["author"] == "test-author"
        assert updated_metadata["version"] == "1.0"
        # New fields added
        assert "category" in updated_metadata
        assert "subcategory" in updated_metadata
        assert "tags" in updated_metadata

    # ========================================================================
    # Idempotent Migration Tests
    # ========================================================================

    def test_migrate_skips_already_migrated(self, migration, mock_collection):
        """Test that already-migrated cases are skipped."""
        mock_collection.add_case(
            doc_id="case-1",
            document="Firebase authentication setup",
            metadata={
                "source": "example.py",
                "category": "code",
                "subcategory": "firebase-auth",
            },
        )

        result = migration.migrate_collection(mock_collection)

        assert result == 0
        assert len(mock_collection.update_calls) == 0

    def test_migrate_partial_collection(self, migration, mock_collection):
        """Test migration of partially migrated collection."""
        # Already migrated case
        mock_collection.add_case(
            doc_id="case-1",
            document="Firebase authentication",
            metadata={
                "source": "example1.py",
                "category": "code",
                "subcategory": "firebase-auth",
            },
        )
        # Not migrated case
        mock_collection.add_case(
            doc_id="case-2",
            document="React component",
            metadata={"source": "example2.py"},
        )
        # Not migrated case
        mock_collection.add_case(
            doc_id="case-3",
            document="API endpoint",
            metadata={"source": "example3.py"},
        )

        result = migration.migrate_collection(mock_collection)

        assert result == 2
        assert len(mock_collection.update_calls) == 1
        updated_ids = mock_collection.update_calls[0]["ids"]
        assert "case-1" not in updated_ids
        assert "case-2" in updated_ids
        assert "case-3" in updated_ids

    def test_migrate_idempotent_returns_zero(self, migration, mock_collection):
        """Test idempotent migration returns 0 when all cases migrated."""
        for i in range(3):
            mock_collection.add_case(
                doc_id=f"case-{i}",
                document=f"Test case {i}",
                metadata={
                    "source": f"example{i}.py",
                    "category": "code",
                    "subcategory": "general",
                },
            )

        result = migration.migrate_collection(mock_collection)

        assert result == 0
        assert len(mock_collection.update_calls) == 0

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_migrate_with_missing_solution_field(self, migration, mock_collection):
        """Test migration handles missing solution metadata gracefully."""
        mock_collection.add_case(
            doc_id="case-1",
            document="Firebase authentication setup",
            metadata={"source": "example.py"},  # No "solution" field
        )

        result = migration.migrate_collection(mock_collection)

        assert result == 1
        updated_metadata = mock_collection.update_calls[0]["metadatas"][0]
        assert "category" in updated_metadata
        assert "subcategory" in updated_metadata

    def test_migrate_with_empty_document_text(self, migration, mock_collection):
        """Test migration handles empty document content."""
        mock_collection.add_case(
            doc_id="case-1", document="", metadata={"source": "example.py"}
        )

        result = migration.migrate_collection(mock_collection)

        assert result == 1
        updated_metadata = mock_collection.update_calls[0]["metadatas"][0]
        # Should get default category/subcategory for empty text
        assert updated_metadata["category"] == "code"
        assert updated_metadata["subcategory"] == "general"

    def test_migrate_with_special_characters(self, migration, mock_collection):
        """Test migration handles special characters in text."""
        mock_collection.add_case(
            doc_id="case-1",
            document="Firebase @authentication #with $special !characters & React",
            metadata={"source": "example.py"},
        )

        result = migration.migrate_collection(mock_collection)

        assert result == 1
        updated_metadata = mock_collection.update_calls[0]["metadatas"][0]
        assert "category" in updated_metadata
        assert "subcategory" in updated_metadata
        # Should still detect Firebase authentication despite special chars
        assert updated_metadata["category"] == "code"
        assert updated_metadata["subcategory"] == "firebase-auth"
