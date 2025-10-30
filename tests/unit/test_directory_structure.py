"""
Unit tests for validating the modular case base directory structure.

This test suite verifies that the required directory structure exists for
organizing case-based reasoning examples by technology/domain.

Test-Driven Development (TDD) approach:
- These tests are written BEFORE the directory structure is created
- Initial test run should FAIL as directories don't exist yet
- Tests will PASS once the directory structure is implemented
"""

import pytest
from pathlib import Path


# Define the project root and expected structure
PROJECT_ROOT = Path(__file__).parent.parent.parent
CASES_DIR = PROJECT_ROOT / "cases"

# Technology directories that must exist
REQUIRED_TECHNOLOGY_DIRS = [
    "firebase",
    "react",
    "nextjs",
    "bootstrap",
    "webdev",
    "orchestration",
    "security",
]

# Complete directory structure (including existing rust/ directory)
ALL_TECHNOLOGY_DIRS = REQUIRED_TECHNOLOGY_DIRS + ["rust"]


class TestCaseBaseDirectoryStructure:
    """Test suite for case base directory structure validation."""

    def test_cases_directory_exists(self):
        """
        Verify that the root cases/ directory exists.

        This is the parent directory for all technology-specific case bases.
        It should exist and be a directory (not a file).
        """
        assert CASES_DIR.exists(), f"cases/ directory does not exist at {CASES_DIR}"
        assert CASES_DIR.is_dir(), f"cases/ exists but is not a directory at {CASES_DIR}"

    def test_technology_directories_exist(self):
        """
        Verify that all 7 new technology-specific directories exist under cases/.

        Tests for: firebase, react, nextjs, bootstrap, webdev, orchestration, security
        Each directory should exist and be a valid directory.
        """
        missing_dirs = []
        invalid_dirs = []

        for tech_name in REQUIRED_TECHNOLOGY_DIRS:
            tech_dir = CASES_DIR / tech_name

            if not tech_dir.exists():
                missing_dirs.append(tech_name)
            elif not tech_dir.is_dir():
                invalid_dirs.append(tech_name)

        assert not missing_dirs, (
            f"Missing technology directories: {', '.join(missing_dirs)}\n"
            f"Expected location: {CASES_DIR}/"
        )

        assert not invalid_dirs, (
            f"Invalid technology directories (exist but not directories): "
            f"{', '.join(invalid_dirs)}"
        )

    def test_directory_structure_complete(self):
        """
        Verify the complete directory structure including the existing rust/ directory.

        Tests all 8 technology directories:
        - 7 new directories (firebase, react, nextjs, bootstrap, webdev, orchestration, security)
        - 1 existing directory (rust)
        """
        missing_dirs = []
        invalid_dirs = []

        for tech_name in ALL_TECHNOLOGY_DIRS:
            tech_dir = CASES_DIR / tech_name

            if not tech_dir.exists():
                missing_dirs.append(tech_name)
            elif not tech_dir.is_dir():
                invalid_dirs.append(tech_name)

        assert not missing_dirs, (
            f"Incomplete directory structure. Missing: {', '.join(missing_dirs)}\n"
            f"Expected all of: {', '.join(ALL_TECHNOLOGY_DIRS)}"
        )

        assert not invalid_dirs, (
            f"Invalid entries in directory structure: {', '.join(invalid_dirs)}"
        )

    def test_init_files_present(self):
        """
        Verify that __init__.py files are present in each technology directory.

        This ensures each technology directory is a proper Python package,
        allowing for future imports and module organization.

        Tests:
        - cases/__init__.py exists
        - Each technology directory contains __init__.py
        - Each __init__.py is a file (not a directory)
        """
        # Check root cases/__init__.py
        cases_init = CASES_DIR / "__init__.py"
        assert cases_init.exists(), (
            f"Missing __init__.py in cases/ directory at {cases_init}"
        )
        assert cases_init.is_file(), (
            f"cases/__init__.py exists but is not a file at {cases_init}"
        )

        # Check __init__.py in each technology directory
        missing_inits = []
        invalid_inits = []

        for tech_name in ALL_TECHNOLOGY_DIRS:
            init_file = CASES_DIR / tech_name / "__init__.py"

            if not init_file.exists():
                missing_inits.append(f"{tech_name}/__init__.py")
            elif not init_file.is_file():
                invalid_inits.append(f"{tech_name}/__init__.py")

        assert not missing_inits, (
            f"Missing __init__.py files in: {', '.join(missing_inits)}\n"
            f"Each technology directory should be a Python package."
        )

        assert not invalid_inits, (
            f"Invalid __init__.py entries (exist but not files): "
            f"{', '.join(invalid_inits)}"
        )


class TestDirectoryStructureIntegrity:
    """Additional tests for directory structure integrity and consistency."""

    def test_no_unexpected_directories(self):
        """
        Verify that only expected technology directories exist in cases/.

        This helps maintain a clean, organized structure and catches
        accidental directory creation or typos.

        Ignores __pycache__ directories which are automatically created by Python.
        """
        if not CASES_DIR.exists():
            pytest.skip("cases/ directory does not exist yet")

        expected_items = set(ALL_TECHNOLOGY_DIRS + ["__init__.py"])
        # Filter out __pycache__ directories (auto-generated by Python)
        actual_items = set(item.name for item in CASES_DIR.iterdir() if item.name != '__pycache__')

        unexpected_items = actual_items - expected_items

        assert not unexpected_items, (
            f"Unexpected items found in cases/ directory: {', '.join(unexpected_items)}\n"
            f"Expected only: {', '.join(sorted(expected_items))}"
        )

    def test_directory_structure_is_readable(self):
        """
        Verify that all directories in the structure are readable.

        This ensures proper filesystem permissions for accessing case files.
        """
        if not CASES_DIR.exists():
            pytest.skip("cases/ directory does not exist yet")

        unreadable_dirs = []

        # Check cases/ directory
        if not CASES_DIR.is_dir() or not CASES_DIR.stat().st_mode & 0o400:
            unreadable_dirs.append("cases/")

        # Check each technology directory
        for tech_name in ALL_TECHNOLOGY_DIRS:
            tech_dir = CASES_DIR / tech_name
            if tech_dir.exists() and (not tech_dir.is_dir() or not tech_dir.stat().st_mode & 0o400):
                unreadable_dirs.append(f"cases/{tech_name}/")

        assert not unreadable_dirs, (
            f"Directories without read permissions: {', '.join(unreadable_dirs)}"
        )
