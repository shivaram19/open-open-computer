# acn/tests/conftest.py
"""Shared pytest fixtures and path setup."""

import sys
from pathlib import Path

# Ensure src/ is on the import path for tests run from any directory.
_SRC_DIR = Path(__file__).parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))
