"""
Unit tests for case_base.py main execution block.

This test suite verifies that the main execution block (__main__) in case_base.py
works correctly after the modularization to CASE_BASE = ALL_CASES.

Test-Driven Development (TDD) approach:
- These tests are written BEFORE any implementation exists
- Initial test run will FAIL (Red phase) as the implementation doesn't exist yet
- Tests will PASS (Green phase) once the main block is properly implemented

Expected main block behavior (from case_base.py lines 232-252):
    1. Print decorative banner
    2. Call validate_case_base() and check result
    3. Call get_case_statistics() to show stats
    4. Call save_case_base_to_file() to create JSON file
    5. Print example search section
    6. Call search_cases("Firebase authentication")
    7. Display search results with problem and solution length
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List

import pytest


class TestMainBlockExecution:
    """Test suite for verifying the main block executes correctly."""

    def test_main_block_executes_without_errors(self):
        """
        Verify the main block runs successfully when executed as a script.

        Expected behavior:
        - Script exits with return code 0
        - No errors in stderr
        - Script completes all operations

        Current state (TDD Red phase):
        - Main block doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Verify successful execution
        assert result.returncode == 0, (
            f"Script should exit with code 0, got {result.returncode}\n"
            f"STDERR: {result.stderr}\n"
            f"STDOUT: {result.stdout}"
        )

        # Verify no errors in stderr (allow warnings)
        # Filter out common warnings that don't indicate failures
        stderr_lines = [
            line for line in result.stderr.split('\n')
            if line and not any(w in line.lower() for w in ['warning', 'deprecation'])
        ]
        if stderr_lines:
            # Some stderr output is acceptable, but check for actual errors
            assert not any('error' in line.lower() for line in stderr_lines), (
                f"Script stderr contains errors:\n{result.stderr}"
            )

    def test_main_block_validation_banner_is_printed(self):
        """
        Verify the decorative banner is shown at start.

        Expected output:
            ==================================================
            Firebase/Next.js/Bootstrap Case-Based Reasoning Dataset
            ==================================================

        Current state (TDD Red phase):
        - Banner doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout

        # Verify banner separator (50 equals signs)
        assert "=" * 50 in stdout, (
            "Output should contain decorative banner separator (50 equals signs)"
        )

        # Verify banner text
        assert "Firebase/Next.js/Bootstrap Case-Based Reasoning Dataset" in stdout, (
            "Output should contain banner title"
        )

        # Verify banner appears near the start (within first 200 characters)
        banner_position = stdout.find("Firebase/Next.js/Bootstrap")
        assert banner_position >= 0 and banner_position < 200, (
            "Banner should appear near the start of output"
        )


class TestMainBlockValidation:
    """Test suite for verifying validation is called in main block."""

    def test_validate_case_base_is_called(self):
        """
        Verify validate_case_base() is executed.

        Expected behavior:
        - validate_case_base() is called
        - Validation messages are printed
        - Either "Case base validation passed!" or validation issues shown

        Current state (TDD Red phase):
        - validate_case_base() call doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout.lower()

        # Verify validation was called (should see either success or issues)
        validation_indicators = [
            "validation passed",
            "validation issues",
            "total valid cases",
        ]

        assert any(indicator in stdout for indicator in validation_indicators), (
            f"Output should contain validation messages.\n"
            f"Expected one of: {validation_indicators}\n"
            f"Got output: {result.stdout[:500]}"
        )

    def test_validation_passes_for_valid_case_base(self):
        """
        Verify validation passes for the actual CASE_BASE.

        Expected behavior:
        - validate_case_base() returns True
        - Success message is printed
        - Case count is shown

        Current state (TDD Red phase):
        - Validation success message doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout.lower()

        # Verify validation passed
        assert "validation passed" in stdout, (
            "CASE_BASE should pass validation"
        )

        # Verify case count is shown
        assert "total valid cases:" in stdout or "total cases:" in stdout, (
            "Validation should show total case count"
        )


class TestMainBlockStatistics:
    """Test suite for verifying statistics are printed in main block."""

    def test_get_case_statistics_is_called(self):
        """
        Verify get_case_statistics() is executed.

        Expected behavior:
        - get_case_statistics() is called
        - Statistics section is printed
        - Contains total count and categories

        Current state (TDD Red phase):
        - Statistics call doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout

        # Verify statistics header is present
        assert "Case Base Statistics" in stdout, (
            "Output should contain 'Case Base Statistics' header"
        )

        # Verify total cases is shown
        assert "Total Cases:" in stdout, (
            "Statistics should include 'Total Cases:' line"
        )

        # Verify categories section is shown
        assert "Categories:" in stdout, (
            "Statistics should include 'Categories:' section"
        )

    def test_statistics_show_category_breakdown(self):
        """
        Verify statistics show category breakdown.

        Expected categories (from get_case_statistics):
        - firebase_auth
        - firestore
        - nextjs
        - bootstrap
        - combined

        Current state (TDD Red phase):
        - Category breakdown doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout.lower()

        # Verify at least some expected categories are shown
        # (actual categories depend on case base content)
        category_keywords = ["firebase", "nextjs", "bootstrap", "firestore"]
        category_found = any(keyword in stdout for keyword in category_keywords)

        assert category_found, (
            f"Statistics should show category breakdown with keywords: {category_keywords}\n"
            f"Output: {result.stdout[:1000]}"
        )

    def test_statistics_show_average_solution_length(self):
        """
        Verify statistics show average solution length.

        Expected output line:
            Average Solution Length: <number> characters

        Current state (TDD Red phase):
        - Average solution length doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout

        # Verify average solution length is shown
        assert "Average Solution Length:" in stdout, (
            "Statistics should include 'Average Solution Length:' line"
        )

        # Verify it has the "characters" unit
        assert "characters" in stdout, (
            "Average solution length should be measured in characters"
        )


class TestMainBlockJsonFileCreation:
    """Test suite for verifying JSON file is created in main block."""

    def test_save_case_base_to_file_is_called(self):
        """
        Verify save_case_base_to_file() is executed.

        Expected behavior:
        - save_case_base_to_file() is called
        - Success message is printed
        - File creation is confirmed

        Current state (TDD Red phase):
        - File saving call doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script in project directory
        # (need to run in project dir so cases module can be imported)
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout.lower()

        # Verify save message is shown
        assert "case base saved to" in stdout, (
            "Output should contain 'Case base saved to' message"
        )

    def test_json_file_is_created(self):
        """
        Verify JSON file is actually created.

        Expected behavior:
        - firebase_nextjs_bootstrap_cases.json is created
        - File contains valid JSON
        - File is not empty

        Current state (TDD Red phase):
        - JSON file creation doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script in project directory
        # (need to run in project dir so cases module can be imported)
        project_dir = "/Users/traviswilliams/Projects/cbr_retrieval_mcp"

        # Clean up any existing file first
        output_file = Path(project_dir) / "firebase_nextjs_bootstrap_cases.json"
        if output_file.exists():
            output_file.unlink()

        # Run the script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        try:
            # Verify file was created
            assert output_file.exists(), (
                f"JSON file should be created at {output_file}"
            )

            # Verify file is not empty
            assert output_file.stat().st_size > 0, (
                "JSON file should not be empty"
            )

            # Verify file contains valid JSON
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Verify JSON is a list
            assert isinstance(data, list), (
                "JSON file should contain a list"
            )

            # Verify list has cases (at least 1)
            assert len(data) > 0, (
                "JSON file should contain at least one case"
            )

            # Verify each case has required fields
            for i, case in enumerate(data[:3]):  # Check first 3 cases
                assert isinstance(case, dict), (
                    f"Case {i} should be a dictionary"
                )
                assert "problem" in case, (
                    f"Case {i} should have 'problem' field"
                )
                assert "solution" in case, (
                    f"Case {i} should have 'solution' field"
                )

        finally:
            # Clean up
            if output_file.exists():
                output_file.unlink()

    def test_json_file_matches_case_base_count(self):
        """
        Verify JSON file has same number of cases as CASE_BASE.

        Expected behavior:
        - File case count equals len(CASE_BASE)
        - All cases are saved

        Current state (TDD Red phase):
        - Case count verification doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Import CASE_BASE to get expected count
        sys.path.insert(0, "/Users/traviswilliams/Projects/cbr_retrieval_mcp")
        try:
            from case_base import CASE_BASE
            expected_count = len(CASE_BASE)
        except ImportError:
            pytest.skip("Cannot import CASE_BASE")
        finally:
            sys.path.pop(0)

        # Run case_base.py as a script
        project_dir = "/Users/traviswilliams/Projects/cbr_retrieval_mcp"
        output_file = Path(project_dir) / "firebase_nextjs_bootstrap_cases.json"

        if output_file.exists():
            output_file.unlink()

        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        try:
            # Load saved JSON
            with open(output_file, 'r', encoding='utf-8') as f:
                saved_cases = json.load(f)

            # Verify count matches
            assert len(saved_cases) == expected_count, (
                f"JSON file should have {expected_count} cases, got {len(saved_cases)}"
            )

        finally:
            if output_file.exists():
                output_file.unlink()


class TestMainBlockExampleSearch:
    """Test suite for verifying example search is executed in main block."""

    def test_example_search_section_is_shown(self):
        """
        Verify example search section is displayed.

        Expected output:
            ==================================================
            Example Search: 'Firebase authentication'
            ==================================================

        Current state (TDD Red phase):
        - Example search section doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout

        # Verify example search header
        assert "Example Search:" in stdout, (
            "Output should contain 'Example Search:' header"
        )

        # Verify search query is shown
        assert "Firebase authentication" in stdout, (
            "Output should show search query 'Firebase authentication'"
        )

    def test_search_results_are_displayed(self):
        """
        Verify search results are shown in numbered format.

        Expected format:
            1. <problem text>
               Solution length: <number> characters
            2. <problem text>
               Solution length: <number> characters

        Current state (TDD Red phase):
        - Search results display doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout

        # Verify numbered results (looking for patterns like "1. " or "2. ")
        has_numbered_results = any(
            f"\n{i}. " in stdout for i in range(1, 6)
        )

        assert has_numbered_results, (
            "Output should contain numbered search results (1., 2., etc.)"
        )

        # Verify solution length is shown
        assert "Solution length:" in stdout, (
            "Search results should show 'Solution length:' for each result"
        )

        # Verify "characters" unit is used
        assert "characters" in stdout, (
            "Solution length should be measured in characters"
        )

    def test_search_results_show_problem_text(self):
        """
        Verify search results display problem text.

        Expected behavior:
        - Each result shows the problem field
        - Problems are from actual cases in CASE_BASE
        - Results are relevant to "Firebase authentication"

        Current state (TDD Red phase):
        - Problem text display doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout.lower()

        # After "Example Search:" section, there should be case problems shown
        example_search_pos = stdout.find("example search")
        if example_search_pos == -1:
            pytest.fail("Cannot find 'Example Search' section")

        # Get text after the example search header
        search_results_section = stdout[example_search_pos:]

        # Verify we have numbered results in this section
        has_results = any(
            f"\n{i}. " in search_results_section for i in range(1, 6)
        )

        assert has_results, (
            "Example search section should contain numbered results"
        )


class TestMainBlockOutputFormatting:
    """Test suite for verifying output formatting is correct."""

    def test_output_sections_separated_by_banners(self):
        """
        Verify output sections are separated by decorative banners.

        Expected separators:
            ==================================================

        Expected sections:
        1. Main banner
        2. Example search banner

        Current state (TDD Red phase):
        - Section formatting doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout

        # Count occurrences of banner separator
        banner_count = stdout.count("=" * 50)

        # Should have at least 2 banners:
        # 1. Main title banner (open and close)
        # 2. Example search banner (open and close)
        assert banner_count >= 2, (
            f"Output should have at least 2 banner separators, got {banner_count}"
        )

    def test_output_is_readable_and_structured(self):
        """
        Verify output has readable structure.

        Expected structure:
        - Sections clearly separated
        - Headers present
        - Data properly formatted
        - Consistent indentation

        Current state (TDD Red phase):
        - Readable formatting doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout

        # Verify output is not empty
        assert len(stdout) > 0, "Output should not be empty"

        # Verify output has newlines (not all on one line)
        assert '\n' in stdout, "Output should have multiple lines"

        # Verify output has at least 10 lines (reasonable for all sections)
        line_count = len(stdout.split('\n'))
        assert line_count >= 10, (
            f"Output should have at least 10 lines, got {line_count}"
        )

        # Verify output has some indentation (spaces for formatting)
        assert '  ' in stdout, (
            "Output should have indentation for readability"
        )


class TestMainBlockGuard:
    """Test suite for verifying __name__ == '__main__' guard works."""

    def test_main_block_only_runs_when_script_executed(self):
        """
        Verify main block only runs when script is executed directly.

        Expected behavior:
        - Importing case_base as module does NOT trigger main block
        - Running python case_base.py DOES trigger main block
        - __name__ == '__main__' guard is properly implemented

        Current state (TDD Red phase):
        - Main block guard doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Test 1: Import case_base as module (should NOT trigger main block)
        sys.path.insert(0, "/Users/traviswilliams/Projects/cbr_retrieval_mcp")

        # Capture any print output during import
        import io
        from contextlib import redirect_stdout

        captured_output = io.StringIO()

        try:
            with redirect_stdout(captured_output):
                # Import case_base (main block should NOT run)
                import case_base
                # Force module to load
                _ = case_base.CASE_BASE
        finally:
            sys.path.pop(0)

        import_output = captured_output.getvalue()

        # Verify main block did NOT run during import
        # (no banner, no statistics, no search example)
        assert "Firebase/Next.js/Bootstrap Case-Based Reasoning Dataset" not in import_output, (
            "Main block should NOT run when importing as module"
        )
        assert "Case Base Statistics" not in import_output, (
            "Statistics should NOT print when importing as module"
        )
        assert "Example Search" not in import_output, (
            "Example search should NOT run when importing as module"
        )

    def test_main_block_runs_when_script_executed_directly(self):
        """
        Verify main block DOES run when script is executed directly.

        Expected behavior:
        - Running python case_base.py triggers main block
        - All main block operations execute

        Current state (TDD Red phase):
        - Direct execution doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout

        # Verify main block DID run
        assert "Firebase/Next.js/Bootstrap Case-Based Reasoning Dataset" in stdout, (
            "Main block should run when executing script directly"
        )
        assert "Case Base Statistics" in stdout, (
            "Statistics should print when executing script directly"
        )
        assert "Example Search" in stdout, (
            "Example search should run when executing script directly"
        )


class TestMainBlockModularStructure:
    """Test suite for verifying main block works with CASE_BASE = ALL_CASES."""

    def test_main_block_works_with_all_cases_import(self):
        """
        Verify main block works with modular CASE_BASE = ALL_CASES structure.

        Expected behavior:
        - No import errors when using ALL_CASES
        - validate_case_base() works with ALL_CASES
        - get_case_statistics() works with ALL_CASES
        - save_case_base_to_file() works with ALL_CASES
        - search_cases() works with ALL_CASES

        Current state (TDD Red phase):
        - Modular integration doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script (which uses CASE_BASE = ALL_CASES)
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Verify successful execution (no import errors)
        assert result.returncode == 0, (
            f"Script should execute successfully with CASE_BASE = ALL_CASES\n"
            f"Return code: {result.returncode}\n"
            f"STDERR: {result.stderr}"
        )

        # Verify no module import errors in stderr
        stderr_lower = result.stderr.lower()
        assert "importerror" not in stderr_lower, (
            f"Should not have ImportError with modular structure:\n{result.stderr}"
        )
        assert "modulenotfounderror" not in stderr_lower, (
            f"Should not have ModuleNotFoundError with modular structure:\n{result.stderr}"
        )

        # Verify all expected operations completed
        stdout = result.stdout
        assert "validation passed" in stdout.lower(), (
            "validate_case_base() should work with ALL_CASES"
        )
        assert "Case Base Statistics" in stdout, (
            "get_case_statistics() should work with ALL_CASES"
        )
        assert "Case base saved to" in stdout, (
            "save_case_base_to_file() should work with ALL_CASES"
        )
        assert "Example Search" in stdout, (
            "search_cases() should work with ALL_CASES"
        )

    def test_main_block_validates_new_metadata_structure(self):
        """
        Verify main block validates cases with new metadata fields.

        Expected behavior:
        - Validation accepts cases with category, subcategory, tags
        - Validation accepts cases without metadata (legacy format)
        - Mixed format case base validates successfully

        Current state (TDD Red phase):
        - Metadata validation doesn't exist yet
        - This test will FAIL until implementation is complete
        """
        # Run case_base.py as a script
        result = subprocess.run(
            [sys.executable, "case_base.py"],
            cwd="/Users/traviswilliams/Projects/cbr_retrieval_mcp",
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = result.stdout.lower()

        # Verify validation passed (accepts new metadata structure)
        assert "validation passed" in stdout, (
            "Validation should pass for cases with new metadata structure"
        )

        # Verify no validation errors about metadata fields
        assert "validation issues" not in stdout or "validation passed" in stdout, (
            "Should not have validation issues with new metadata fields"
        )
