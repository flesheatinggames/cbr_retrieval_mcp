"""Conftest for profiling tests to ensure correct imports."""
import sys
from pathlib import Path

# Add project root to sys.path to ensure benchmarks module can be imported
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    print(f"✓ Added {project_root} to sys.path for profiling tests")
else:
    print(f"ℹ {project_root} already in sys.path")
