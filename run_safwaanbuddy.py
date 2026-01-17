#!/usr/bin/env python3
"""SafwaanBuddy Ultimate++ launcher script."""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
src_path = project_root / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    from safwaanbuddy.main import main
    main()
