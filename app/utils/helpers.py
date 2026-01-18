"""
Helper functions and utilities for the desktop application.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Optional, Union

import yaml


def get_platform() -> str:
    """Get the current operating system platform."""
    if sys.platform.startswith("darwin"):
        return "darwin"
    elif sys.platform.startswith("win"):
        return "windows"
    elif sys.platform.startswith("linux"):
        return "linux"
    return "unknown"


def get_icon(name: str) -> str:
    """
    Get an icon name in QtAwesome format.
    
    Args:
        name: Icon name (e.g., 'mdi.folder')
        
    Returns:
        Formatted icon name for QtAwesome
    """
    # Ensure the icon name is in proper format
    if not name:
        return "mdi.help-circle"
    if not name.startswith(("mdi.", "fa.", "ph.", "ri.")):
        return f"mdi.{name}"
    return name


def format_size(size_bytes: int, decimal_places: int = 2) -> str:
    """
    Format a file size in bytes to a human-readable string.
    
    Args:
        size_bytes: Size in bytes
        decimal_places: Number of decimal places
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes < 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.{decimal_places}f} {units[unit_index]}"


def format_datetime(dt: Union[datetime, float, int], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime or timestamp to a string.
    
    Args:
        dt: Datetime object or Unix timestamp
        format_str: strftime format string
        
    Returns:
        Formatted datetime string
    """
    if isinstance(dt, (int, float)):
        dt = datetime.fromtimestamp(dt)
    return dt.strftime(format_str)


def open_file_manager(path: Union[str, Path]) -> bool:
    """
    Open the system file manager at the specified path.
    
    Args:
        path: Path to open
        
    Returns:
        True if successful, False otherwise
    """
    path = Path(path)
    platform = get_platform()
    
    try:
        if platform == "darwin":
            subprocess.run(["open", str(path)], check=True)
        elif platform == "windows":
            os.startfile(str(path))
        elif platform == "linux":
            subprocess.run(["xdg-open", str(path)], check=True)
        else:
            webbrowser.open(path.as_uri())
        return True
    except Exception:
        return False


def reveal_in_file_manager(path: Union[str, Path]) -> bool:
    """
    Reveal (select) a file in the system file manager.
    
    Args:
        path: Path to reveal
        
    Returns:
        True if successful, False otherwise
    """
    path = Path(path)
    platform = get_platform()
    
    try:
        if platform == "darwin":
            subprocess.run(["open", "-R", str(path)], check=True)
        elif platform == "windows":
            subprocess.run(["explorer", "/select,", str(path)], check=True)
        elif platform == "linux":
            # Try various file managers
            for fm in ["nautilus", "dolphin", "thunar", "nemo", "pcmanfm"]:
                try:
                    subprocess.run([fm, "--select", str(path)], check=True, timeout=2)
                    return True
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
            # Fallback: open parent directory
            return open_file_manager(path.parent)
        return True
    except Exception:
        return False


def validate_yaml(yaml_content: str) -> tuple[bool, Optional[str]]:
    """
    Validate YAML content.
    
    Args:
        yaml_content: YAML string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        yaml.safe_load(yaml_content)
        return True, None
    except yaml.YAMLError as e:
        return False, str(e)


def yaml_to_dict(yaml_content: str) -> Optional[dict]:
    """
    Parse YAML content to dictionary.
    
    Args:
        yaml_content: YAML string to parse
        
    Returns:
        Parsed dictionary or None if invalid
    """
    try:
        return yaml.safe_load(yaml_content)
    except yaml.YAMLError:
        return None


def dict_to_yaml(data: dict, default_flow_style: bool = False) -> str:
    """
    Convert dictionary to YAML string.
    
    Args:
        data: Dictionary to convert
        default_flow_style: Whether to use flow style
        
    Returns:
        YAML string
    """
    return yaml.dump(data, default_flow_style=default_flow_style, allow_unicode=True, sort_keys=False)


def is_path_valid(path: Union[str, Path]) -> bool:
    """
    Check if a path exists and is accessible.
    
    Args:
        path: Path to check
        
    Returns:
        True if path exists and is accessible
    """
    try:
        path = Path(path).expanduser().resolve()
        return path.exists()
    except Exception:
        return False


def expand_path(path: Union[str, Path]) -> Path:
    """
    Expand user home and environment variables in path.
    
    Args:
        path: Path to expand
        
    Returns:
        Expanded path
    """
    path_str = str(path)
    # Expand environment variables
    path_str = os.path.expandvars(path_str)
    # Expand user home
    return Path(path_str).expanduser()


def get_file_info(path: Union[str, Path]) -> dict:
    """
    Get information about a file.
    
    Args:
        path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    path = Path(path)
    if not path.exists():
        return {"exists": False}
    
    stat = path.stat()
    return {
        "exists": True,
        "name": path.name,
        "stem": path.stem,
        "suffix": path.suffix,
        "size": stat.st_size,
        "size_formatted": format_size(stat.st_size),
        "created": datetime.fromtimestamp(stat.st_ctime),
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "is_symlink": path.is_symlink(),
    }


def count_files_in_directory(path: Union[str, Path], recursive: bool = False) -> dict:
    """
    Count files and directories in a path.
    
    Args:
        path: Directory path
        recursive: Whether to count recursively
        
    Returns:
        Dictionary with counts
    """
    path = Path(path)
    if not path.is_dir():
        return {"files": 0, "dirs": 0}
    
    files = 0
    dirs = 0
    
    try:
        if recursive:
            for item in path.rglob("*"):
                if item.is_file():
                    files += 1
                elif item.is_dir():
                    dirs += 1
        else:
            for item in path.iterdir():
                if item.is_file():
                    files += 1
                elif item.is_dir():
                    dirs += 1
    except PermissionError:
        pass
    
    return {"files": files, "dirs": dirs}


def create_backup_path(path: Union[str, Path]) -> Path:
    """
    Create a backup path for a file.
    
    Args:
        path: Original path
        
    Returns:
        Backup path with timestamp
    """
    path = Path(path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return path.with_name(f"{path.stem}_backup_{timestamp}{path.suffix}")
