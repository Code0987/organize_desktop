"""
Tests for core components.
"""

import pytest
from pathlib import Path
import tempfile
import json

from app.core.settings import Settings, UISettings, RunSettings, EditorSettings
from app.core.config_manager import ConfigManager
from app.core.rule_engine import RuleEngine, LogEntry, ExecutionStatus
from app.utils.helpers import format_size, format_datetime, validate_yaml


class TestSettings:
    """Tests for the Settings class."""
    
    def test_default_settings(self):
        """Test that default settings are properly initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(_app_name="test-app")
            
            assert settings.ui.theme == "dark"
            assert settings.ui.font_size == 12
            assert settings.run.simulate_by_default is True
            assert settings.editor.tab_size == 2
    
    def test_save_and_load_settings(self):
        """Test saving and loading settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save settings
            settings = Settings(_app_name="test-app")
            settings.ui.theme = "light"
            settings.ui.font_size = 14
            settings.run.show_notifications = False
            
            # Manually set the path for testing
            settings._settings_path = Path(tmpdir) / "settings.json"
            settings.save()
            
            # Verify file was created
            assert settings._settings_path.exists()
            
            # Load settings
            with open(settings._settings_path, 'r') as f:
                data = json.load(f)
            
            assert data["ui"]["theme"] == "light"
            assert data["ui"]["font_size"] == 14
            assert data["run"]["show_notifications"] is False
    
    def test_add_recent_file(self):
        """Test adding recent files."""
        settings = Settings(_app_name="test-app")
        settings._settings_path = Path(tempfile.gettempdir()) / "test_settings.json"
        
        settings.add_recent_file("/path/to/file1.yaml", "file1.yaml")
        settings.add_recent_file("/path/to/file2.yaml", "file2.yaml")
        
        assert len(settings.recent_files) == 2
        assert settings.recent_files[0]["path"] == "/path/to/file2.yaml"
    
    def test_recent_files_limit(self):
        """Test that recent files are limited to 10."""
        settings = Settings(_app_name="test-app")
        settings._settings_path = Path(tempfile.gettempdir()) / "test_settings.json"
        
        for i in range(15):
            settings.add_recent_file(f"/path/to/file{i}.yaml", f"file{i}.yaml")
        
        assert len(settings.recent_files) == 10


class TestConfigManager:
    """Tests for the ConfigManager class."""
    
    def test_new_config(self):
        """Test creating a new config."""
        manager = ConfigManager()
        manager.new()
        
        assert manager.raw_content != ""
        assert manager.is_modified is True
        assert manager.config_path is None
    
    def test_load_from_string_valid(self):
        """Test loading valid YAML config."""
        manager = ConfigManager()
        
        config = """
rules:
  - name: Test Rule
    locations:
      - ~/Downloads
    filters:
      - extension: pdf
    actions:
      - echo: "Found PDF"
"""
        
        result = manager.load_from_string(config)
        
        assert result is True
        assert manager.is_valid is True
        assert manager.last_error is None
    
    def test_load_from_string_invalid(self):
        """Test loading invalid YAML config."""
        manager = ConfigManager()
        
        config = """
rules:
  - name: Test Rule
    locations: [
    actions:
      - echo: "Hello"
"""
        
        result = manager.load_from_string(config)
        
        assert result is False
        assert manager.last_error is not None
    
    def test_get_rules(self):
        """Test getting rules from config."""
        manager = ConfigManager()
        
        config = """
rules:
  - name: Rule 1
    locations:
      - ~/Downloads
    actions:
      - echo: "Hello"
  - name: Rule 2
    locations:
      - ~/Desktop
    actions:
      - echo: "World"
"""
        
        manager.load_from_string(config)
        rules = manager.get_rules()
        
        assert len(rules) == 2
        assert rules[0]["name"] == "Rule 1"
        assert rules[1]["name"] == "Rule 2"
    
    def test_set_rules(self):
        """Test setting rules."""
        manager = ConfigManager()
        
        rules = [
            {
                "name": "New Rule",
                "locations": ["~/Downloads"],
                "actions": [{"echo": "Hello"}],
            }
        ]
        
        result = manager.set_rules(rules)
        
        assert result is True
        assert "New Rule" in manager.raw_content
    
    def test_add_rule(self):
        """Test adding a rule."""
        manager = ConfigManager()
        manager.new()
        
        new_rule = {
            "name": "Added Rule",
            "locations": ["~/Documents"],
            "actions": [{"echo": "Added"}],
        }
        
        initial_count = len(manager.get_rules())
        manager.add_rule(new_rule)
        
        assert len(manager.get_rules()) == initial_count + 1
    
    def test_delete_rule(self):
        """Test deleting a rule."""
        manager = ConfigManager()
        
        config = """
rules:
  - name: Rule 1
    actions:
      - echo: "1"
  - name: Rule 2
    actions:
      - echo: "2"
"""
        
        manager.load_from_string(config)
        manager.delete_rule(0)
        
        rules = manager.get_rules()
        assert len(rules) == 1
        assert rules[0]["name"] == "Rule 2"
    
    def test_save_and_load_file(self):
        """Test saving and loading a config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager()
            manager.new()
            
            config_path = Path(tmpdir) / "test_config.yaml"
            result = manager.save(config_path)
            
            assert result is True
            assert config_path.exists()
            
            # Load the saved file
            manager2 = ConfigManager()
            result = manager2.load(config_path)
            
            assert result is True
            assert manager2.is_valid


class TestRuleEngine:
    """Tests for the RuleEngine class."""
    
    def test_initial_status(self):
        """Test initial engine status."""
        engine = RuleEngine()
        
        assert engine.status == ExecutionStatus.IDLE
        assert engine.is_running is False
        assert len(engine.logs) == 0
    
    def test_log_entry(self):
        """Test LogEntry creation."""
        from datetime import datetime
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level="info",
            message="Test message",
            rule_name="Test Rule",
        )
        
        assert entry.level == "info"
        assert entry.message == "Test message"
        assert entry.rule_name == "Test Rule"
    
    def test_log_entry_to_dict(self):
        """Test LogEntry serialization."""
        from datetime import datetime
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level="success",
            message="File moved",
            file_path="/path/to/file.txt",
            action_name="move",
        )
        
        data = entry.to_dict()
        
        assert "timestamp" in data
        assert data["level"] == "success"
        assert data["message"] == "File moved"
        assert data["file_path"] == "/path/to/file.txt"


class TestHelpers:
    """Tests for helper functions."""
    
    def test_format_size_bytes(self):
        """Test formatting bytes."""
        assert format_size(0) == "0 B"
        assert format_size(500) == "500 B"
    
    def test_format_size_kb(self):
        """Test formatting kilobytes."""
        assert "KB" in format_size(1024)
        assert "KB" in format_size(1500)
    
    def test_format_size_mb(self):
        """Test formatting megabytes."""
        assert "MB" in format_size(1024 * 1024)
        assert "MB" in format_size(5 * 1024 * 1024)
    
    def test_format_size_gb(self):
        """Test formatting gigabytes."""
        assert "GB" in format_size(1024 * 1024 * 1024)
    
    def test_format_datetime(self):
        """Test datetime formatting."""
        from datetime import datetime
        
        dt = datetime(2024, 1, 15, 10, 30, 45)
        formatted = format_datetime(dt)
        
        assert "2024-01-15" in formatted
        assert "10:30:45" in formatted
    
    def test_validate_yaml_valid(self):
        """Test validating valid YAML."""
        yaml_content = """
name: Test
value: 123
list:
  - item1
  - item2
"""
        
        is_valid, error = validate_yaml(yaml_content)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_yaml_invalid(self):
        """Test validating invalid YAML."""
        yaml_content = """
name: [invalid
value: 123
"""
        
        is_valid, error = validate_yaml(yaml_content)
        
        assert is_valid is False
        assert error is not None


class TestConstants:
    """Tests for constants module."""
    
    def test_filters_defined(self):
        """Test that filters are defined."""
        from app.utils.constants import FILTERS
        
        assert "extension" in FILTERS
        assert "size" in FILTERS
        assert "created" in FILTERS
        assert "duplicate" in FILTERS
        
        # Check filter structure
        ext_filter = FILTERS["extension"]
        assert "name" in ext_filter
        assert "description" in ext_filter
        assert "params" in ext_filter
    
    def test_actions_defined(self):
        """Test that actions are defined."""
        from app.utils.constants import ACTIONS
        
        assert "move" in ACTIONS
        assert "copy" in ACTIONS
        assert "delete" in ACTIONS
        assert "echo" in ACTIONS
        
        # Check action structure
        move_action = ACTIONS["move"]
        assert "name" in move_action
        assert "description" in move_action
        assert "params" in move_action
    
    def test_filter_modes_defined(self):
        """Test that filter modes are defined."""
        from app.utils.constants import FILTER_MODES
        
        assert "all" in FILTER_MODES
        assert "any" in FILTER_MODES
        assert "none" in FILTER_MODES


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
