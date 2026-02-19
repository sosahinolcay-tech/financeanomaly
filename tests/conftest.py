"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
for p in (str(project_root), str(project_root / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

