"""
Organize Desktop - A modern desktop application for file management automation.

This application provides a user-friendly graphical interface for the organize CLI tool,
allowing users to create, manage, and execute file organization rules without writing YAML.
"""

__version__ = "1.0.0"
__app_name__ = "Organize Desktop"
__author__ = "Organize Desktop Team"

from .main import main

__all__ = ["main", "__version__", "__app_name__"]
