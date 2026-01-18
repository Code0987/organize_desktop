"""
Application settings management using platformdirs for cross-platform paths.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field, asdict

import platformdirs


@dataclass
class UISettings:
    """User interface settings."""
    theme: str = "dark"  # dark, light, system
    font_size: int = 12
    editor_font_family: str = "monospace"
    editor_font_size: int = 11
    show_toolbar: bool = True
    show_statusbar: bool = True
    sidebar_width: int = 250
    log_max_lines: int = 1000
    confirm_dangerous_actions: bool = True
    show_welcome_screen: bool = True


@dataclass
class RunSettings:
    """Settings for running organize rules."""
    simulate_by_default: bool = True
    default_working_dir: str = ""
    show_notifications: bool = True
    auto_scroll_log: bool = True
    clear_log_on_run: bool = False


@dataclass
class EditorSettings:
    """Code editor settings."""
    tab_size: int = 2
    use_spaces: bool = True
    auto_save: bool = True
    auto_save_interval: int = 30  # seconds
    syntax_highlighting: bool = True
    line_numbers: bool = True
    word_wrap: bool = False
    bracket_matching: bool = True


@dataclass
class RecentFile:
    """Recent config file entry."""
    path: str
    name: str
    last_accessed: str


@dataclass
class Settings:
    """Main application settings."""
    ui: UISettings = field(default_factory=UISettings)
    run: RunSettings = field(default_factory=RunSettings)
    editor: EditorSettings = field(default_factory=EditorSettings)
    recent_files: List[Dict[str, str]] = field(default_factory=list)
    pinned_locations: List[str] = field(default_factory=list)
    last_config_path: str = ""
    window_geometry: Dict[str, int] = field(default_factory=dict)
    
    _app_name: str = field(default="organize-desktop", repr=False)
    _settings_path: Optional[Path] = field(default=None, repr=False)
    
    def __post_init__(self):
        """Initialize settings path after creation."""
        if self._settings_path is None:
            config_dir = platformdirs.user_config_path(appname=self._app_name)
            config_dir.mkdir(parents=True, exist_ok=True)
            self._settings_path = config_dir / "settings.json"
    
    @classmethod
    def load(cls, app_name: str = "organize-desktop") -> "Settings":
        """
        Load settings from disk.
        
        Args:
            app_name: Application name for config directory
            
        Returns:
            Settings instance
        """
        config_dir = platformdirs.user_config_path(appname=app_name)
        settings_path = config_dir / "settings.json"
        
        if not settings_path.exists():
            settings = cls(_app_name=app_name)
            settings._settings_path = settings_path
            return settings
        
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Parse nested dataclasses
            ui = UISettings(**data.get("ui", {}))
            run = RunSettings(**data.get("run", {}))
            editor = EditorSettings(**data.get("editor", {}))
            
            settings = cls(
                ui=ui,
                run=run,
                editor=editor,
                recent_files=data.get("recent_files", []),
                pinned_locations=data.get("pinned_locations", []),
                last_config_path=data.get("last_config_path", ""),
                window_geometry=data.get("window_geometry", {}),
                _app_name=app_name,
            )
            settings._settings_path = settings_path
            return settings
        except (json.JSONDecodeError, TypeError, KeyError):
            # Return default settings if loading fails
            settings = cls(_app_name=app_name)
            settings._settings_path = settings_path
            return settings
    
    def save(self) -> bool:
        """
        Save settings to disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self._settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "ui": asdict(self.ui),
                "run": asdict(self.run),
                "editor": asdict(self.editor),
                "recent_files": self.recent_files,
                "pinned_locations": self.pinned_locations,
                "last_config_path": self.last_config_path,
                "window_geometry": self.window_geometry,
            }
            
            with open(self._settings_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
    
    def add_recent_file(self, path: str, name: str = "") -> None:
        """
        Add a file to recent files list.
        
        Args:
            path: File path
            name: Display name (optional)
        """
        from datetime import datetime
        
        if not name:
            name = Path(path).name
        
        # Remove existing entry if present
        self.recent_files = [f for f in self.recent_files if f.get("path") != path]
        
        # Add to beginning
        self.recent_files.insert(0, {
            "path": path,
            "name": name,
            "last_accessed": datetime.now().isoformat(),
        })
        
        # Keep only last 10
        self.recent_files = self.recent_files[:10]
        self.save()
    
    def clear_recent_files(self) -> None:
        """Clear the recent files list."""
        self.recent_files = []
        self.save()
    
    def add_pinned_location(self, path: str) -> None:
        """
        Add a location to pinned locations.
        
        Args:
            path: Location path
        """
        if path not in self.pinned_locations:
            self.pinned_locations.append(path)
            self.save()
    
    def remove_pinned_location(self, path: str) -> None:
        """
        Remove a location from pinned locations.
        
        Args:
            path: Location path
        """
        if path in self.pinned_locations:
            self.pinned_locations.remove(path)
            self.save()
    
    def get_configs_dir(self) -> Path:
        """Get the directory where organize configs are stored."""
        return platformdirs.user_config_path(appname="organize")
    
    def get_logs_dir(self) -> Path:
        """Get the directory for log files."""
        log_dir = platformdirs.user_log_path(appname=self._app_name)
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    def get_data_dir(self) -> Path:
        """Get the directory for application data."""
        data_dir = platformdirs.user_data_path(appname=self._app_name)
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.ui = UISettings()
        self.run = RunSettings()
        self.editor = EditorSettings()
        self.save()
