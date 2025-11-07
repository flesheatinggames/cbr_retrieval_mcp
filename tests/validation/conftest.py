"""Pytest configuration for validation tests."""

import sys
from pathlib import Path

import pytest

# Add src to path for case_base import
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def case_base():
    """Provide CASE_BASE for backward compatibility tests."""
    from case_base import CASE_BASE

    return CASE_BASE
