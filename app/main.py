#!/usr/bin/env python3
"""
Organize Desktop - Main entry point.

A modern desktop application for the organize file management automation tool.
"""

import sys
import os
from pathlib import Path


def setup_environment():
    """Set up environment for the application."""
    # Enable High DPI scaling
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    
    # Set application info for Qt
    os.environ.setdefault("QT_QPA_PLATFORM", "")  # Let Qt auto-detect


def main():
    """Main entry point for the application."""
    setup_environment()
    
    # Add parent directory to path if needed (for direct script execution)
    app_dir = Path(__file__).parent
    parent_dir = str(app_dir.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Organize Desktop")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Organize Desktop")
    app.setOrganizationDomain("organize-desktop.app")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Import and create main window
    from app.ui.main_window import MainWindow
    
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
