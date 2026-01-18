#!/usr/bin/env python3
"""
Launcher script for Organize Desktop.
Run this file to start the application.
"""

import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import main

if __name__ == "__main__":
    main()
