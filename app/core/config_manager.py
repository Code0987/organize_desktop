"""
Configuration file manager for organize rules.
Handles loading, saving, validating, and converting configurations.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

import yaml
import platformdirs

from organize import Config, ConfigError
from organize.find_config import find_config, list_configs, create_example_config


class ConfigManager:
    """
    Manages organize configuration files.
    
    Provides methods to:
    - Load and save configurations
    - Validate YAML syntax and organize schema
    - Convert between YAML and Python dictionaries
    - Create backup copies
    - List available configurations
    """
    
    EXAMPLE_CONFIG = """\
# organize configuration file
# https://organize.readthedocs.io

rules:
  - name: "Example Rule"
    locations:
      - ~/Downloads
    filters:
      - extension: pdf
    actions:
      - echo: "Found PDF: {path.name}"
"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the config manager.
        
        Args:
            config_path: Path to a configuration file (optional)
        """
        self._config_path = config_path
        self._config: Optional[Config] = None
        self._raw_content: str = ""
        self._last_error: Optional[str] = None
        self._is_modified: bool = False
    
    @property
    def config_path(self) -> Optional[Path]:
        """Get the current configuration file path."""
        return self._config_path
    
    @property
    def config(self) -> Optional[Config]:
        """Get the parsed organize Config object."""
        return self._config
    
    @property
    def raw_content(self) -> str:
        """Get the raw YAML content."""
        return self._raw_content
    
    @property
    def last_error(self) -> Optional[str]:
        """Get the last error message."""
        return self._last_error
    
    @property
    def is_modified(self) -> bool:
        """Check if the configuration has been modified."""
        return self._is_modified
    
    @property
    def is_valid(self) -> bool:
        """Check if the current configuration is valid."""
        return self._config is not None
    
    @property
    def filename(self) -> str:
        """Get the configuration filename."""
        if self._config_path:
            return self._config_path.name
        return "Untitled"
    
    def load(self, path: Optional[Path] = None) -> bool:
        """
        Load a configuration file.
        
        Args:
            path: Path to load, or None to use current path
            
        Returns:
            True if successful, False otherwise
        """
        if path is not None:
            self._config_path = path
        
        if self._config_path is None:
            self._last_error = "No configuration path specified"
            return False
        
        try:
            self._raw_content = self._config_path.read_text(encoding="utf-8")
            self._config = Config.from_string(
                config=self._raw_content,
                config_path=self._config_path,
            )
            self._is_modified = False
            self._last_error = None
            return True
        except FileNotFoundError:
            self._last_error = f"File not found: {self._config_path}"
            return False
        except ConfigError as e:
            self._last_error = str(e)
            return False
        except yaml.YAMLError as e:
            self._last_error = f"YAML syntax error: {e}"
            return False
        except Exception as e:
            self._last_error = f"Error loading config: {e}"
            return False
    
    def load_from_string(self, content: str, path: Optional[Path] = None) -> bool:
        """
        Load configuration from a string.
        
        Args:
            content: YAML content
            path: Optional file path for context
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._raw_content = content
            self._config_path = path
            self._config = Config.from_string(
                config=content,
                config_path=path,
            )
            self._is_modified = True
            self._last_error = None
            return True
        except ConfigError as e:
            self._last_error = str(e)
            return False
        except yaml.YAMLError as e:
            self._last_error = f"YAML syntax error: {e}"
            return False
        except Exception as e:
            self._last_error = f"Error parsing config: {e}"
            return False
    
    def save(self, path: Optional[Path] = None) -> bool:
        """
        Save the configuration to file.
        
        Args:
            path: Path to save to, or None to use current path
            
        Returns:
            True if successful, False otherwise
        """
        save_path = path or self._config_path
        
        if save_path is None:
            self._last_error = "No save path specified"
            return False
        
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_text(self._raw_content, encoding="utf-8")
            self._config_path = save_path
            self._is_modified = False
            self._last_error = None
            return True
        except Exception as e:
            self._last_error = f"Error saving config: {e}"
            return False
    
    def set_content(self, content: str) -> bool:
        """
        Set the raw YAML content and validate it.
        
        Args:
            content: New YAML content
            
        Returns:
            True if content is valid, False otherwise
        """
        old_content = self._raw_content
        self._raw_content = content
        self._is_modified = (content != old_content) or self._is_modified
        
        # Try to parse the new content
        try:
            self._config = Config.from_string(
                config=content,
                config_path=self._config_path,
            )
            self._last_error = None
            return True
        except (ConfigError, yaml.YAMLError) as e:
            self._last_error = str(e)
            self._config = None
            return False
    
    def validate(self, content: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate configuration content.
        
        Args:
            content: YAML content to validate, or None to validate current
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        content = content or self._raw_content
        
        try:
            Config.from_string(config=content, config_path=self._config_path)
            return True, None
        except ConfigError as e:
            return False, str(e)
        except yaml.YAMLError as e:
            return False, f"YAML syntax error: {e}"
        except Exception as e:
            return False, str(e)
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """
        Get rules as a list of dictionaries.
        
        Returns:
            List of rule dictionaries
        """
        if not self._raw_content:
            return []
        
        try:
            data = yaml.safe_load(self._raw_content)
            return data.get("rules", []) if data else []
        except yaml.YAMLError:
            return []
    
    def set_rules(self, rules: List[Dict[str, Any]]) -> bool:
        """
        Set rules from a list of dictionaries.
        
        Args:
            rules: List of rule dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {"rules": rules}
            content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
            return self.set_content(content)
        except Exception as e:
            self._last_error = str(e)
            return False
    
    def add_rule(self, rule: Dict[str, Any], index: Optional[int] = None) -> bool:
        """
        Add a new rule to the configuration.
        
        Args:
            rule: Rule dictionary
            index: Position to insert at, or None to append
            
        Returns:
            True if successful, False otherwise
        """
        rules = self.get_rules()
        
        if index is None:
            rules.append(rule)
        else:
            rules.insert(index, rule)
        
        return self.set_rules(rules)
    
    def update_rule(self, index: int, rule: Dict[str, Any]) -> bool:
        """
        Update a rule at the specified index.
        
        Args:
            index: Rule index
            rule: New rule dictionary
            
        Returns:
            True if successful, False otherwise
        """
        rules = self.get_rules()
        
        if 0 <= index < len(rules):
            rules[index] = rule
            return self.set_rules(rules)
        
        return False
    
    def delete_rule(self, index: int) -> bool:
        """
        Delete a rule at the specified index.
        
        Args:
            index: Rule index
            
        Returns:
            True if successful, False otherwise
        """
        rules = self.get_rules()
        
        if 0 <= index < len(rules):
            rules.pop(index)
            return self.set_rules(rules)
        
        return False
    
    def move_rule(self, from_index: int, to_index: int) -> bool:
        """
        Move a rule from one position to another.
        
        Args:
            from_index: Current position
            to_index: New position
            
        Returns:
            True if successful, False otherwise
        """
        rules = self.get_rules()
        
        if 0 <= from_index < len(rules) and 0 <= to_index < len(rules):
            rule = rules.pop(from_index)
            rules.insert(to_index, rule)
            return self.set_rules(rules)
        
        return False
    
    def duplicate_rule(self, index: int) -> bool:
        """
        Duplicate a rule at the specified index.
        
        Args:
            index: Rule index to duplicate
            
        Returns:
            True if successful, False otherwise
        """
        rules = self.get_rules()
        
        if 0 <= index < len(rules):
            import copy
            new_rule = copy.deepcopy(rules[index])
            if "name" in new_rule:
                new_rule["name"] = f"{new_rule['name']} (copy)"
            rules.insert(index + 1, new_rule)
            return self.set_rules(rules)
        
        return False
    
    def create_backup(self) -> Optional[Path]:
        """
        Create a backup of the current configuration.
        
        Returns:
            Path to backup file, or None if failed
        """
        if not self._config_path or not self._config_path.exists():
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self._config_path.with_name(
                f"{self._config_path.stem}_backup_{timestamp}{self._config_path.suffix}"
            )
            shutil.copy2(self._config_path, backup_path)
            return backup_path
        except Exception:
            return None
    
    def new(self) -> None:
        """Create a new empty configuration."""
        self._config_path = None
        self._raw_content = self.EXAMPLE_CONFIG
        self._config = None
        self._is_modified = True
        self._last_error = None
        
        # Try to parse the example config
        try:
            self._config = Config.from_string(config=self._raw_content)
        except Exception:
            pass
    
    @staticmethod
    def get_default_config_dir() -> Path:
        """Get the default directory for organize configs."""
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config).expanduser() / "organize"
        return platformdirs.user_config_path(appname="organize")
    
    @staticmethod
    def list_available_configs() -> List[Path]:
        """
        List all available configuration files.
        
        Returns:
            List of config file paths
        """
        return list(list_configs())
    
    @staticmethod
    def find_config_by_name(name: Optional[str] = None) -> Optional[Path]:
        """
        Find a configuration file by name.
        
        Args:
            name: Config name or path
            
        Returns:
            Path to config file, or None if not found
        """
        try:
            return find_config(name)
        except Exception:
            return None
    
    @staticmethod
    def create_new_config(name: str) -> Optional[Path]:
        """
        Create a new configuration file with the given name.
        
        Args:
            name: Name for the new config
            
        Returns:
            Path to created config, or None if failed
        """
        try:
            return create_example_config(name)
        except FileExistsError:
            return None
        except Exception:
            return None
