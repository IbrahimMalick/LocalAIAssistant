"""
Shared bootstrap so the scripts can import the ``assistant`` package whether
they are run as ``python src/scripts/test_llm.py`` or from inside ``src/``.
"""

import sys
from pathlib import Path

# Add the ``src`` directory (parent of this file's parent) to sys.path.
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
