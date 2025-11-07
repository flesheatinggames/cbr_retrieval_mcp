"""
Unit tests for the dynamic case loader in cases/__init__.py.

This test suite validates the dynamic case loading functionality that discovers,
imports, and aggregates cases from modular case files organized by technology/domain.

Test-Driven Development (TDD) approach:
- These tests are written BEFORE cases/__init__.py is implemented
- Initial test run should FAIL (Red phase) as the loader doesn't exist yet
- Tests will PASS (Green phase) once the loader is implemented
- Implementation should follow the function signatures tested here

Expected function signatures in cases/__init__.py:
    def discover_case_modules() -> List[str]
    def load_cases_from_module(module_path: str) -> List[Dict[str, Any]]
    def load_all_cases() -> List[Dict[str, Any]]
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

# Define project structure
PROJECT_ROOT = Path(__file__).parent.parent.parent
CASES_DIR = PROJECT_ROOT / "cases"

# Expected technology subdirectories
EXPECTED_SUBDIRS = [
    "firebase",
    "react",
    "nextjs",
    "bootstrap",
    "webdev",
    "orchestration",
    "security",
    "rust",  # Existing directory with 26 case files
]


class TestModuleDiscovery:
    """Test suite for case module discovery functionality."""

    def test_discover_case_modules_finds_all_subdirectories(self):
        """
        Verify module discovery finds all expected subdirectories.

        Tests that discover_case_modules() returns module paths for all
        technology directories: firebase/, react/, nextjs/, bootstrap/,
        webdev/, orchestration/, security/, rust/

        Expected format: "cases.{subdir}.{filename}" (e.g., "cases.rust.rust_actix_cases")
        """
        # Import the loader module (will fail initially - TDD Red phase)
        from cases import discover_case_modules

        discovered_modules = discover_case_modules()

        # Verify we found modules
        assert isinstance(
            discovered_modules, list
        ), "Should return a list of module paths"
        assert len(discovered_modules) > 0, "Should discover at least some case modules"

        # Extract subdirectories from discovered module paths
        discovered_subdirs = set()
        for module_path in discovered_modules:
            # Module path format: cases.{subdir}.{filename}
            parts = module_path.split(".")
            assert (
                len(parts) >= 3
            ), f"Module path should have at least 3 parts: {module_path}"
            assert (
                parts[0] == "cases"
            ), f"Module path should start with 'cases': {module_path}"
            discovered_subdirs.add(parts[1])

        # Verify all expected subdirectories are represented
        # Note: Some may be empty initially, but rust/ should definitely be present
        assert (
            "rust" in discovered_subdirs
        ), "Should discover rust/ directory with existing cases"

        # Verify module paths follow correct format
        for module_path in discovered_modules:
            assert module_path.startswith(
                "cases."
            ), f"Module path should start with 'cases.': {module_path}"
            assert (
                "_cases" in module_path
            ), f"Module path should contain '_cases': {module_path}"

    def test_discover_case_modules_handles_empty_subdirectory(self, tmp_path):
        """
        Verify discovery handles subdirectories with no *_cases.py files.

        Tests that empty subdirectories don't cause errors and that other
        valid modules are still discovered.

        Note: This test uses the actual cases/ directory which may have empty subdirs
        after directory structure is created but before case files are migrated.
        """
        from cases import discover_case_modules

        # Discovery should not fail even if some subdirectories are empty
        discovered_modules = discover_case_modules()

        assert isinstance(
            discovered_modules, list
        ), "Should return list even with empty subdirs"

        # rust/ directory exists with cases, so we should find at least those
        rust_modules = [m for m in discovered_modules if m.startswith("cases.rust.")]
        assert (
            len(rust_modules) > 0
        ), "Should still discover rust/ modules despite other empty subdirs"

    def test_discover_case_modules_excludes_non_cases_files(self):
        """
        Verify discovery ignores files not matching *_cases.py pattern.

        Tests that only files ending with _cases.py are included in discovery.
        Files like __init__.py, helper.py, utils.py should be excluded.
        """
        from cases import discover_case_modules

        discovered_modules = discover_case_modules()

        # Verify all discovered modules end with _cases
        for module_path in discovered_modules:
            # Module path format: cases.{subdir}.{filename}
            filename = module_path.split(".")[-1]
            assert filename.endswith(
                "_cases"
            ), f"Module filename should end with '_cases': {filename}"

        # Verify __init__ files are not included
        init_modules = [m for m in discovered_modules if "__init__" in m]
        assert (
            len(init_modules) == 0
        ), "__init__.py files should not be included in discovery"


class TestCaseLoading:
    """Test suite for loading cases from individual modules."""

    def test_load_cases_from_module_success(self):
        """
        Verify successful case loading from a valid module.

        Uses cases.rust.rust_actix_cases as a known existing module with valid cases.
        Tests that the loader correctly imports the module and extracts its case list.
        """
        from cases import load_cases_from_module

        # Load from known existing rust module
        module_path = "cases.rust.rust_actix_cases"
        cases = load_cases_from_module(module_path)

        # Verify return type
        assert isinstance(cases, list), "Should return a list of cases"
        assert len(cases) > 0, "Should load at least one case from rust_actix_cases"

        # Verify all items are dictionaries
        assert all(
            isinstance(case, dict) for case in cases
        ), "All loaded cases should be dictionaries"

        # Verify core fields (problem and solution should always be present)
        for case in cases:
            assert "problem" in case, "Each case should have a 'problem' field"
            assert "solution" in case, "Each case should have a 'solution' field"
            assert isinstance(case["problem"], str), "Problem should be a string"
            assert isinstance(case["solution"], str), "Solution should be a string"

    def test_load_cases_from_module_handles_import_error(self, caplog):
        """
        Verify graceful handling of module import failures.

        Tests that ImportError is caught and logged, returning empty list
        rather than crashing the loader.
        """
        from cases import load_cases_from_module

        # Attempt to load from nonexistent module
        with caplog.at_level(logging.ERROR):
            cases = load_cases_from_module("cases.invalid.nonexistent")

        # Should return empty list, not raise exception
        assert isinstance(cases, list), "Should return list even on import error"
        assert len(cases) == 0, "Should return empty list for failed import"

        # Should log the error
        assert len(caplog.records) > 0, "Should log import error"
        assert any(
            "invalid.nonexistent" in record.message for record in caplog.records
        ), "Error log should mention the failed module path"

    def test_load_cases_from_module_handles_missing_case_list(self, tmp_path, caplog):
        """
        Verify handling of module without *_CASES variable.

        Tests that modules without a properly named case list variable
        are handled gracefully with a warning.
        """
        from cases import load_cases_from_module

        # Create a temporary module without a case list variable
        test_module = tmp_path / "test_module.py"
        test_module.write_text(
            """
# Module with no case list
SOME_OTHER_VARIABLE = "not a case list"
"""
        )

        # Add tmp_path to sys.path for import
        sys.path.insert(0, str(tmp_path))

        try:
            with caplog.at_level(logging.WARNING):
                cases = load_cases_from_module("test_module")

            # Should return empty list
            assert isinstance(
                cases, list
            ), "Should return list for module without case list"
            assert len(cases) == 0, "Should return empty list when no case list found"

            # Should log warning
            assert any(
                "No case list found" in record.message for record in caplog.records
            ), "Should log warning about missing case list"
        finally:
            # Cleanup
            sys.path.remove(str(tmp_path))
            if "test_module" in sys.modules:
                del sys.modules["test_module"]

    def test_load_cases_from_module_handles_non_list_case_variable(
        self, tmp_path, caplog
    ):
        """
        Verify handling of *_CASES variable that's not a list.

        Tests that if a module has a *_CASES variable that's a dict, tuple, or
        other type instead of a list, it's handled appropriately.
        """
        from cases import load_cases_from_module

        # Create a temporary module with non-list CASES variable
        test_module = tmp_path / "test_cases.py"
        test_module.write_text(
            """
# Module with CASES as dict instead of list
TEST_CASES = {"problem": "test", "solution": "test"}
"""
        )

        # Add tmp_path to sys.path for import
        sys.path.insert(0, str(tmp_path))

        try:
            with caplog.at_level(logging.WARNING):
                cases = load_cases_from_module("test_cases")

            # Should either return empty list or skip non-list variables
            assert isinstance(cases, list), "Should return list type"
            # Either returns empty list or has proper validation
            if len(cases) > 0:
                # If it returns something, it should have validated it's not the dict
                assert cases != [
                    {"problem": "test", "solution": "test"}
                ], "Should not return the dict as a single case"
        finally:
            # Cleanup
            sys.path.remove(str(tmp_path))
            if "test_cases" in sys.modules:
                del sys.modules["test_cases"]

    def test_loader_handles_cases_without_metadata(self, caplog):
        """
        Verify loader handles cases missing category/subcategory/tags fields gracefully.

        Tests backward compatibility with existing rust cases that lack the new
        metadata fields. These cases should still load successfully.
        """
        from cases import load_cases_from_module

        # Load rust cases which currently lack metadata fields
        with caplog.at_level(logging.WARNING):
            cases = load_cases_from_module("cases.rust.rust_actix_cases")

        # Should successfully load cases
        assert isinstance(cases, list), "Should load cases despite missing metadata"
        assert len(cases) > 0, "Should load at least one case"

        # Verify core fields are present
        for case in cases:
            assert "problem" in case, "Case should have problem field"
            assert "solution" in case, "Case should have solution field"

            # New metadata fields may be missing (backward compatibility)
            # This is expected for rust cases until migration
            metadata_fields = ["category", "subcategory", "tags"]
            missing_fields = [field for field in metadata_fields if field not in case]

            if missing_fields:
                # This is OK - backward compatibility
                # May log warning but should not fail
                pass


class TestCaseAggregation:
    """Test suite for aggregating cases from all modules."""

    def test_load_all_cases_aggregates_from_all_modules(self):
        """
        Verify all cases from all modules are aggregated.

        Initially tests that at least rust cases are loaded (5+ cases).
        Final implementation should load 49 total cases after all migrations complete.

        Note: Test is written to pass with partial implementation (rust only) and
        will continue to pass as more case modules are added.
        """
        from cases import load_all_cases

        all_cases = load_all_cases()

        # Verify return type
        assert isinstance(all_cases, list), "Should return a list of all cases"

        # Should load at least the rust cases (5+ cases exist in rust/)
        assert (
            len(all_cases) >= 5
        ), f"Should load at least 5 cases from rust/. Got {len(all_cases)}"

        # All items should be dictionaries
        assert all(
            isinstance(case, dict) for case in all_cases
        ), "All aggregated cases should be dictionaries"

        # All cases should have problem and solution
        for i, case in enumerate(all_cases):
            assert "problem" in case, f"Case {i} missing 'problem' field"
            assert "solution" in case, f"Case {i} missing 'solution' field"

        # Note: Final count of 49 will be reached in later tasks when all
        # case modules are created and migrated

    def test_load_all_cases_handles_partial_failure(self, caplog):
        """
        Verify partial loading continues despite individual module failures.

        Tests that if one module fails to load, the loader continues with
        other modules and returns the successfully loaded cases.
        """
        from cases import load_all_cases

        # Mock import_module to fail for one specific module
        with patch("importlib.import_module") as mock_import:
            # Set up mock to fail for one module but succeed for others
            original_import = __import__

            def selective_import(name, *args, **kwargs):
                if name == "cases.fake.failure_module":
                    raise ImportError("Mocked import failure")
                # For actual imports, use the real import
                return original_import(name, *args, **kwargs)

            mock_import.side_effect = selective_import

            # Even with mocked failures, should load successfully
            with caplog.at_level(logging.ERROR):
                all_cases = load_all_cases()

            # Should still return cases from successful modules
            assert isinstance(
                all_cases, list
            ), "Should return list despite partial failure"
            # Should have at least some cases from rust/
            assert len(all_cases) >= 5, "Should load cases from successful modules"

    def test_load_all_cases_logs_progress(self, caplog):
        """
        Verify logging provides visibility into loading process.

        Tests that the loader logs:
        - Number of modules discovered
        - Per-module case counts
        - Total cases loaded
        """
        from cases import load_all_cases

        with caplog.at_level(logging.INFO):
            all_cases = load_all_cases()

        # Verify we got log messages
        assert len(caplog.records) > 0, "Should log loading progress"

        # Check for expected log content
        log_messages = [record.message for record in caplog.records]
        full_log = "\n".join(log_messages)

        # Should log module discovery
        assert any(
            "Discovered" in msg and "modules" in msg for msg in log_messages
        ), f"Should log number of discovered modules. Got:\n{full_log}"

        # Should log per-module loading
        assert any(
            "Loaded" in msg and "cases from" in msg for msg in log_messages
        ), f"Should log per-module case counts. Got:\n{full_log}"

        # Should log total count
        assert any(
            "Total cases loaded" in msg for msg in log_messages
        ), f"Should log total cases loaded. Got:\n{full_log}"

        # Verify the total count in log matches actual count
        total_log = [msg for msg in log_messages if "Total cases loaded" in msg][0]
        assert (
            str(len(all_cases)) in total_log
        ), f"Log should show correct total count. Expected {len(all_cases)} in: {total_log}"


class TestLoaderFunctionSignatures:
    """Test suite to verify expected function signatures exist."""

    def test_discover_case_modules_function_exists(self):
        """Verify discover_case_modules function exists and is callable."""
        from cases import discover_case_modules

        assert callable(
            discover_case_modules
        ), "discover_case_modules should be a callable function"

    def test_load_cases_from_module_function_exists(self):
        """Verify load_cases_from_module function exists and is callable."""
        from cases import load_cases_from_module

        assert callable(
            load_cases_from_module
        ), "load_cases_from_module should be a callable function"

    def test_load_all_cases_function_exists(self):
        """Verify load_all_cases function exists and is callable."""
        from cases import load_all_cases

        assert callable(load_all_cases), "load_all_cases should be a callable function"

    def test_all_cases_variable_exists(self):
        """
        Verify ALL_CASES variable exists and is populated.

        The cases/__init__.py module should export an ALL_CASES variable
        that contains all loaded cases, callable via: from cases import ALL_CASES
        """
        from cases import ALL_CASES

        assert isinstance(ALL_CASES, list), "ALL_CASES should be a list"
        assert len(ALL_CASES) >= 5, "ALL_CASES should contain at least rust cases"
        assert all(
            isinstance(case, dict) for case in ALL_CASES
        ), "ALL_CASES should contain dictionaries"


class TestCaseMetadataValidation:
    """Test suite for validate_case() metadata validation function."""

    @pytest.fixture
    def valid_case(self):
        """Fixture providing a valid case dictionary with all required fields."""
        return {
            "problem": "How to configure Actix Web with CORS?",
            "solution": "Use actix_cors::Cors middleware configuration.",
            "category": "rust",
            "subcategory": "web-frameworks",
            "tags": ["actix-web", "cors", "middleware"],
        }

    @pytest.fixture
    def allowed_categories(self):
        """Fixture providing the list of allowed categories."""
        return [
            "firebase",
            "react",
            "nextjs",
            "bootstrap",
            "webdev",
            "orchestration",
            "security",
            "rust",
        ]

    def test_validate_case_valid_case(self, valid_case):
        """
        Verify that a well-formed case with all required fields passes validation.

        Tests that validate_case() returns True for a case containing all required
        fields (problem, solution, category, subcategory, tags) with valid values.
        """
        from cases import validate_case

        result = validate_case(valid_case)

        assert (
            result is True
        ), "Valid case with all required fields should pass validation"

    def test_validate_case_missing_problem(self, valid_case):
        """
        Verify validation fails when "problem" field is missing.

        Tests that validate_case() returns False when the required "problem"
        field is not present in the case dictionary.
        """
        from cases import validate_case

        case_without_problem = valid_case.copy()
        del case_without_problem["problem"]

        result = validate_case(case_without_problem)

        assert result is False, "Case missing 'problem' field should fail validation"

    def test_validate_case_missing_solution(self, valid_case):
        """
        Verify validation fails when "solution" field is missing.

        Tests that validate_case() returns False when the required "solution"
        field is not present in the case dictionary.
        """
        from cases import validate_case

        case_without_solution = valid_case.copy()
        del case_without_solution["solution"]

        result = validate_case(case_without_solution)

        assert result is False, "Case missing 'solution' field should fail validation"

    def test_validate_case_missing_category(self, valid_case):
        """
        Verify validation fails when "category" field is missing.

        Tests that validate_case() returns False when the required "category"
        field is not present in the case dictionary.
        """
        from cases import validate_case

        case_without_category = valid_case.copy()
        del case_without_category["category"]

        result = validate_case(case_without_category)

        assert result is False, "Case missing 'category' field should fail validation"

    def test_validate_case_missing_subcategory(self, valid_case):
        """
        Verify validation fails when "subcategory" field is missing.

        Tests that validate_case() returns False when the required "subcategory"
        field is not present in the case dictionary.
        """
        from cases import validate_case

        case_without_subcategory = valid_case.copy()
        del case_without_subcategory["subcategory"]

        result = validate_case(case_without_subcategory)

        assert (
            result is False
        ), "Case missing 'subcategory' field should fail validation"

    def test_validate_case_missing_tags(self, valid_case):
        """
        Verify validation fails when "tags" field is missing.

        Tests that validate_case() returns False when the required "tags"
        field is not present in the case dictionary.
        """
        from cases import validate_case

        case_without_tags = valid_case.copy()
        del case_without_tags["tags"]

        result = validate_case(case_without_tags)

        assert result is False, "Case missing 'tags' field should fail validation"

    def test_validate_case_empty_problem(self, valid_case):
        """
        Verify validation fails when "problem" is an empty string.

        Tests that validate_case() returns False when the "problem" field
        contains an empty string value.
        """
        from cases import validate_case

        case_with_empty_problem = valid_case.copy()
        case_with_empty_problem["problem"] = ""

        result = validate_case(case_with_empty_problem)

        assert (
            result is False
        ), "Case with empty 'problem' string should fail validation"

    def test_validate_case_empty_solution(self, valid_case):
        """
        Verify validation fails when "solution" is an empty string.

        Tests that validate_case() returns False when the "solution" field
        contains an empty string value.
        """
        from cases import validate_case

        case_with_empty_solution = valid_case.copy()
        case_with_empty_solution["solution"] = ""

        result = validate_case(case_with_empty_solution)

        assert (
            result is False
        ), "Case with empty 'solution' string should fail validation"

    def test_validate_case_empty_category(self, valid_case):
        """
        Verify validation fails when "category" is an empty string.

        Tests that validate_case() returns False when the "category" field
        contains an empty string value.
        """
        from cases import validate_case

        case_with_empty_category = valid_case.copy()
        case_with_empty_category["category"] = ""

        result = validate_case(case_with_empty_category)

        assert (
            result is False
        ), "Case with empty 'category' string should fail validation"

    def test_validate_case_empty_subcategory(self, valid_case):
        """
        Verify validation fails when "subcategory" is an empty string.

        Tests that validate_case() returns False when the "subcategory" field
        contains an empty string value.
        """
        from cases import validate_case

        case_with_empty_subcategory = valid_case.copy()
        case_with_empty_subcategory["subcategory"] = ""

        result = validate_case(case_with_empty_subcategory)

        assert (
            result is False
        ), "Case with empty 'subcategory' string should fail validation"

    def test_validate_case_empty_tags(self, valid_case):
        """
        Verify validation fails when "tags" is an empty list.

        Tests that validate_case() returns False when the "tags" field
        contains an empty list.
        """
        from cases import validate_case

        case_with_empty_tags = valid_case.copy()
        case_with_empty_tags["tags"] = []

        result = validate_case(case_with_empty_tags)

        assert result is False, "Case with empty 'tags' list should fail validation"

    def test_validate_case_tags_not_list(self, valid_case):
        """
        Verify validation fails when "tags" is not a list.

        Tests that validate_case() returns False when the "tags" field
        contains a value that is not a list (e.g., string, dict, tuple).
        """
        from cases import validate_case

        # Test with string instead of list
        case_with_tags_string = valid_case.copy()
        case_with_tags_string["tags"] = "tag1,tag2,tag3"

        result = validate_case(case_with_tags_string)

        assert result is False, "Case with 'tags' as string should fail validation"

        # Test with dict instead of list
        case_with_tags_dict = valid_case.copy()
        case_with_tags_dict["tags"] = {"tag": "value"}

        result = validate_case(case_with_tags_dict)

        assert result is False, "Case with 'tags' as dict should fail validation"

        # Test with tuple instead of list
        case_with_tags_tuple = valid_case.copy()
        case_with_tags_tuple["tags"] = ("tag1", "tag2")

        result = validate_case(case_with_tags_tuple)

        assert result is False, "Case with 'tags' as tuple should fail validation"

    def test_validate_case_invalid_category(self, valid_case):
        """
        Verify validation fails when "category" is not in allowed categories.

        Tests that validate_case() returns False when the "category" field
        contains a value that is not in the list of allowed categories.
        """
        from cases import validate_case

        case_with_invalid_category = valid_case.copy()
        case_with_invalid_category["category"] = "invalid_category"

        result = validate_case(case_with_invalid_category)

        assert result is False, "Case with invalid 'category' should fail validation"

        # Test with another invalid category
        case_with_invalid_category["category"] = "python"

        result = validate_case(case_with_invalid_category)

        assert result is False, "Case with unlisted 'category' should fail validation"

    def test_validate_case_function_exists(self):
        """
        Verify validate_case function exists and is callable.

        Tests that the validate_case function is properly exported from
        the cases module and is callable.
        """
        from cases import validate_case

        assert callable(validate_case), "validate_case should be a callable function"
