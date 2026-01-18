"""
Settings dialog for configuring application preferences.
"""

from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLabel, QLineEdit, QSpinBox, QCheckBox,
    QComboBox, QPushButton, QDialogButtonBox, QGroupBox,
    QFileDialog, QMessageBox, QFrame, QListWidget, QListWidgetItem,
)
from PyQt6.QtCore import Qt

try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False

from .styles import StyleManager
from ..core.settings import Settings


def get_icon(name: str, color: str = "#cdd6f4"):
    """Get an icon, with fallback for missing qtawesome."""
    if HAS_QTAWESOME:
        try:
            return qta.icon(name, color=color)
        except Exception:
            from PyQt6.QtGui import QIcon
            return QIcon()
    from PyQt6.QtGui import QIcon
    return QIcon()


class SettingsDialog(QDialog):
    """
    Settings dialog for configuring application preferences.
    
    Tabs:
    - General: Theme, confirmations, startup
    - Editor: Font, indentation, highlighting
    - Execution: Simulation, notifications
    - Locations: Pinned locations list
    """
    
    def __init__(
        self,
        settings: Settings,
        style_manager: StyleManager,
        parent: Optional[QWidget] = None,
    ):
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.settings = settings
        self.style_manager = style_manager
        
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(style_manager.get_stylesheet())
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # General tab
        general_tab = self._create_general_tab()
        tabs.addTab(general_tab, "General")
        
        # Editor tab
        editor_tab = self._create_editor_tab()
        tabs.addTab(editor_tab, "Editor")
        
        # Execution tab
        execution_tab = self._create_execution_tab()
        tabs.addTab(execution_tab, "Execution")
        
        # Locations tab
        locations_tab = self._create_locations_tab()
        tabs.addTab(locations_tab, "Locations")
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(
            self._restore_defaults
        )
        layout.addWidget(buttons)
    
    def _create_general_tab(self) -> QWidget:
        """Create the General settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        appearance_layout.addRow("Font Size:", self.font_size_spin)
        
        self.toolbar_cb = QCheckBox("Show toolbar")
        appearance_layout.addRow("", self.toolbar_cb)
        
        self.statusbar_cb = QCheckBox("Show status bar")
        appearance_layout.addRow("", self.statusbar_cb)
        
        layout.addWidget(appearance_group)
        
        # Behavior group
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout(behavior_group)
        
        self.confirm_dangerous_cb = QCheckBox("Confirm before running (non-simulation)")
        behavior_layout.addRow("", self.confirm_dangerous_cb)
        
        self.welcome_cb = QCheckBox("Show welcome screen on startup")
        behavior_layout.addRow("", self.welcome_cb)
        
        layout.addWidget(behavior_group)
        
        # Log group
        log_group = QGroupBox("Log")
        log_layout = QFormLayout(log_group)
        
        self.log_lines_spin = QSpinBox()
        self.log_lines_spin.setRange(100, 10000)
        self.log_lines_spin.setSingleStep(100)
        log_layout.addRow("Max log lines:", self.log_lines_spin)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        
        return tab
    
    def _create_editor_tab(self) -> QWidget:
        """Create the Editor settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Editor group
        editor_group = QGroupBox("Code Editor")
        editor_layout = QFormLayout(editor_group)
        
        self.editor_font_edit = QLineEdit()
        self.editor_font_edit.setPlaceholderText("e.g., Consolas, Monaco, monospace")
        editor_layout.addRow("Font Family:", self.editor_font_edit)
        
        self.editor_font_size_spin = QSpinBox()
        self.editor_font_size_spin.setRange(8, 24)
        editor_layout.addRow("Font Size:", self.editor_font_size_spin)
        
        self.tab_size_spin = QSpinBox()
        self.tab_size_spin.setRange(1, 8)
        editor_layout.addRow("Tab Size:", self.tab_size_spin)
        
        self.use_spaces_cb = QCheckBox("Use spaces instead of tabs")
        editor_layout.addRow("", self.use_spaces_cb)
        
        layout.addWidget(editor_group)
        
        # Features group
        features_group = QGroupBox("Features")
        features_layout = QFormLayout(features_group)
        
        self.syntax_highlight_cb = QCheckBox("Syntax highlighting")
        features_layout.addRow("", self.syntax_highlight_cb)
        
        self.line_numbers_cb = QCheckBox("Show line numbers")
        features_layout.addRow("", self.line_numbers_cb)
        
        self.word_wrap_cb = QCheckBox("Word wrap")
        features_layout.addRow("", self.word_wrap_cb)
        
        self.bracket_matching_cb = QCheckBox("Bracket matching")
        features_layout.addRow("", self.bracket_matching_cb)
        
        layout.addWidget(features_group)
        
        # Auto-save group
        autosave_group = QGroupBox("Auto-Save")
        autosave_layout = QFormLayout(autosave_group)
        
        self.autosave_cb = QCheckBox("Enable auto-save")
        autosave_layout.addRow("", self.autosave_cb)
        
        self.autosave_interval_spin = QSpinBox()
        self.autosave_interval_spin.setRange(5, 300)
        self.autosave_interval_spin.setSuffix(" seconds")
        autosave_layout.addRow("Interval:", self.autosave_interval_spin)
        
        layout.addWidget(autosave_group)
        
        layout.addStretch()
        
        return tab
    
    def _create_execution_tab(self) -> QWidget:
        """Create the Execution settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Run settings group
        run_group = QGroupBox("Run Settings")
        run_layout = QFormLayout(run_group)
        
        self.simulate_default_cb = QCheckBox("Simulate by default (recommended)")
        run_layout.addRow("", self.simulate_default_cb)
        
        self.working_dir_edit = QLineEdit()
        self.working_dir_edit.setPlaceholderText("Leave empty to use current directory")
        run_layout.addRow("Default Working Directory:", self.working_dir_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_working_dir)
        run_layout.addRow("", browse_btn)
        
        layout.addWidget(run_group)
        
        # Output settings group
        output_group = QGroupBox("Output")
        output_layout = QFormLayout(output_group)
        
        self.notifications_cb = QCheckBox("Show system notifications on completion")
        output_layout.addRow("", self.notifications_cb)
        
        self.auto_scroll_cb = QCheckBox("Auto-scroll log to bottom")
        output_layout.addRow("", self.auto_scroll_cb)
        
        self.clear_log_cb = QCheckBox("Clear log before each run")
        output_layout.addRow("", self.clear_log_cb)
        
        layout.addWidget(output_group)
        
        layout.addStretch()
        
        return tab
    
    def _create_locations_tab(self) -> QWidget:
        """Create the Locations settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Pinned locations group
        pinned_group = QGroupBox("Pinned Locations")
        pinned_layout = QVBoxLayout(pinned_group)
        
        info_label = QLabel(
            "These locations appear in quick-access menus for easy selection."
        )
        info_label.setStyleSheet(f"color: {self.style_manager.colors['text_secondary']};")
        info_label.setWordWrap(True)
        pinned_layout.addWidget(info_label)
        
        self.locations_list = QListWidget()
        pinned_layout.addWidget(self.locations_list)
        
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Location")
        add_btn.setIcon(get_icon("mdi.folder-plus", self.style_manager.get_icon_color()))
        add_btn.clicked.connect(self._add_location)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.setIcon(get_icon("mdi.delete", self.style_manager.colors["error"]))
        remove_btn.clicked.connect(self._remove_location)
        btn_layout.addWidget(remove_btn)
        
        btn_layout.addStretch()
        
        pinned_layout.addLayout(btn_layout)
        layout.addWidget(pinned_group)
        
        # Config locations info
        config_group = QGroupBox("Configuration Locations")
        config_layout = QVBoxLayout(config_group)
        
        config_info = QLabel(
            f"<b>User Config:</b> {self.settings.get_configs_dir()}<br>"
            f"<b>App Data:</b> {self.settings.get_data_dir()}<br>"
            f"<b>Logs:</b> {self.settings.get_logs_dir()}"
        )
        config_info.setStyleSheet(f"color: {self.style_manager.colors['text_secondary']};")
        config_info.setWordWrap(True)
        config_layout.addWidget(config_info)
        
        layout.addWidget(config_group)
        
        layout.addStretch()
        
        return tab
    
    def _load_settings(self) -> None:
        """Load current settings into the form."""
        # General
        self.theme_combo.setCurrentText(self.settings.ui.theme.title())
        self.font_size_spin.setValue(self.settings.ui.font_size)
        self.toolbar_cb.setChecked(self.settings.ui.show_toolbar)
        self.statusbar_cb.setChecked(self.settings.ui.show_statusbar)
        self.confirm_dangerous_cb.setChecked(self.settings.ui.confirm_dangerous_actions)
        self.welcome_cb.setChecked(self.settings.ui.show_welcome_screen)
        self.log_lines_spin.setValue(self.settings.ui.log_max_lines)
        
        # Editor
        self.editor_font_edit.setText(self.settings.editor.editor_font_family)
        self.editor_font_size_spin.setValue(self.settings.editor.editor_font_size)
        self.tab_size_spin.setValue(self.settings.editor.tab_size)
        self.use_spaces_cb.setChecked(self.settings.editor.use_spaces)
        self.syntax_highlight_cb.setChecked(self.settings.editor.syntax_highlighting)
        self.line_numbers_cb.setChecked(self.settings.editor.line_numbers)
        self.word_wrap_cb.setChecked(self.settings.editor.word_wrap)
        self.bracket_matching_cb.setChecked(self.settings.editor.bracket_matching)
        self.autosave_cb.setChecked(self.settings.editor.auto_save)
        self.autosave_interval_spin.setValue(self.settings.editor.auto_save_interval)
        
        # Execution
        self.simulate_default_cb.setChecked(self.settings.run.simulate_by_default)
        self.working_dir_edit.setText(self.settings.run.default_working_dir)
        self.notifications_cb.setChecked(self.settings.run.show_notifications)
        self.auto_scroll_cb.setChecked(self.settings.run.auto_scroll_log)
        self.clear_log_cb.setChecked(self.settings.run.clear_log_on_run)
        
        # Locations
        for loc in self.settings.pinned_locations:
            self.locations_list.addItem(loc)
    
    def _save_settings(self) -> None:
        """Save form values to settings."""
        # General
        self.settings.ui.theme = self.theme_combo.currentText().lower()
        self.settings.ui.font_size = self.font_size_spin.value()
        self.settings.ui.show_toolbar = self.toolbar_cb.isChecked()
        self.settings.ui.show_statusbar = self.statusbar_cb.isChecked()
        self.settings.ui.confirm_dangerous_actions = self.confirm_dangerous_cb.isChecked()
        self.settings.ui.show_welcome_screen = self.welcome_cb.isChecked()
        self.settings.ui.log_max_lines = self.log_lines_spin.value()
        
        # Editor
        self.settings.editor.editor_font_family = self.editor_font_edit.text()
        self.settings.editor.editor_font_size = self.editor_font_size_spin.value()
        self.settings.editor.tab_size = self.tab_size_spin.value()
        self.settings.editor.use_spaces = self.use_spaces_cb.isChecked()
        self.settings.editor.syntax_highlighting = self.syntax_highlight_cb.isChecked()
        self.settings.editor.line_numbers = self.line_numbers_cb.isChecked()
        self.settings.editor.word_wrap = self.word_wrap_cb.isChecked()
        self.settings.editor.bracket_matching = self.bracket_matching_cb.isChecked()
        self.settings.editor.auto_save = self.autosave_cb.isChecked()
        self.settings.editor.auto_save_interval = self.autosave_interval_spin.value()
        
        # Execution
        self.settings.run.simulate_by_default = self.simulate_default_cb.isChecked()
        self.settings.run.default_working_dir = self.working_dir_edit.text()
        self.settings.run.show_notifications = self.notifications_cb.isChecked()
        self.settings.run.auto_scroll_log = self.auto_scroll_cb.isChecked()
        self.settings.run.clear_log_on_run = self.clear_log_cb.isChecked()
        
        # Locations
        self.settings.pinned_locations = [
            self.locations_list.item(i).text()
            for i in range(self.locations_list.count())
        ]
    
    def _save_and_accept(self) -> None:
        """Save settings and close the dialog."""
        self._save_settings()
        self.accept()
    
    def _restore_defaults(self) -> None:
        """Restore default settings."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all settings to their defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.reset_to_defaults()
            self._load_settings()
    
    def _browse_working_dir(self) -> None:
        """Browse for working directory."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Working Directory",
            self.working_dir_edit.text() or ""
        )
        if path:
            self.working_dir_edit.setText(path)
    
    def _add_location(self) -> None:
        """Add a pinned location."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Location to Pin"
        )
        if path:
            # Check for duplicates
            for i in range(self.locations_list.count()):
                if self.locations_list.item(i).text() == path:
                    return
            self.locations_list.addItem(path)
    
    def _remove_location(self) -> None:
        """Remove the selected pinned location."""
        row = self.locations_list.currentRow()
        if row >= 0:
            self.locations_list.takeItem(row)
