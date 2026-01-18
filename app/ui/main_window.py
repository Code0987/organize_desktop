"""
Main application window for Organize Desktop.
Provides the primary user interface with sidebar, editor, and log viewer.
"""

import sys
from pathlib import Path
from typing import Optional, List

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QToolBar, QStatusBar, QMenuBar, QMenu, QLabel, QPushButton,
    QFileDialog, QMessageBox, QStackedWidget, QDockWidget,
    QApplication, QSizePolicy, QFrame, QToolButton, QSpacerItem,
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QSettings
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QCloseEvent

try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False

from ..core.settings import Settings
from ..core.config_manager import ConfigManager
from ..core.rule_engine import RuleEngine, ExecutionStatus, LogEntry
from ..core.file_watcher import ConfigFileWatcher
from .styles import StyleManager, Theme
from .rule_editor import RuleEditor
from .config_editor import ConfigEditor
from .log_viewer import LogViewer
from .settings_dialog import SettingsDialog


def get_icon(name: str, color: str = "#cdd6f4") -> QIcon:
    """Get an icon, with fallback for missing qtawesome."""
    if HAS_QTAWESOME:
        try:
            return qta.icon(name, color=color)
        except Exception:
            return QIcon()
    return QIcon()


class MainWindow(QMainWindow):
    """
    Main application window.
    
    Features:
    - Sidebar with config file list and quick actions
    - Rule editor with visual builder
    - YAML config editor with syntax highlighting
    - Log viewer for execution output
    - Toolbar with common actions
    """
    
    config_changed = pyqtSignal()
    execution_started = pyqtSignal()
    execution_finished = pyqtSignal()
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize core components
        self.settings = Settings.load()
        self.style_manager = StyleManager(
            Theme.DARK if self.settings.ui.theme == "dark" else Theme.LIGHT
        )
        self.config_manager = ConfigManager()
        self.rule_engine = RuleEngine()
        self.file_watcher = ConfigFileWatcher()
        
        # Set up the window
        self.setWindowTitle("Organize Desktop")
        self.setMinimumSize(1200, 700)
        self._restore_geometry()
        
        # Apply stylesheet
        self.setStyleSheet(self.style_manager.get_stylesheet())
        
        # Create UI components
        self._create_menu_bar()
        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()
        
        # Set up signals
        self._setup_signals()
        
        # Load initial state
        self._load_initial_state()
        
        # Start file watcher
        self.file_watcher.start()
    
    def _create_menu_bar(self) -> None:
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction(get_icon("mdi.file-plus", self.style_manager.get_icon_color()), "&New Config", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._on_new_config)
        file_menu.addAction(new_action)
        
        open_action = QAction(get_icon("mdi.folder-open", self.style_manager.get_icon_color()), "&Open Config...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_config)
        file_menu.addAction(open_action)
        
        # Recent files submenu
        self.recent_menu = QMenu("Open &Recent", self)
        self.recent_menu.setIcon(get_icon("mdi.history", self.style_manager.get_icon_color()))
        self._update_recent_menu()
        file_menu.addMenu(self.recent_menu)
        
        file_menu.addSeparator()
        
        save_action = QAction(get_icon("mdi.content-save", self.style_manager.get_icon_color()), "&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save_config)
        file_menu.addAction(save_action)
        
        save_as_action = QAction(get_icon("mdi.content-save-edit", self.style_manager.get_icon_color()), "Save &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self._on_save_config_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(get_icon("mdi.exit-to-app", self.style_manager.get_icon_color()), "E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction(get_icon("mdi.undo", self.style_manager.get_icon_color()), "&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._on_undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction(get_icon("mdi.redo", self.style_manager.get_icon_color()), "&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._on_redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        add_rule_action = QAction(get_icon("mdi.plus", self.style_manager.get_icon_color()), "Add &Rule", self)
        add_rule_action.setShortcut(QKeySequence("Ctrl+R"))
        add_rule_action.triggered.connect(self._on_add_rule)
        edit_menu.addAction(add_rule_action)
        
        edit_menu.addSeparator()
        
        settings_action = QAction(get_icon("mdi.cog", self.style_manager.get_icon_color()), "&Settings...", self)
        settings_action.setShortcut(QKeySequence.StandardKey.Preferences)
        settings_action.triggered.connect(self._on_settings)
        edit_menu.addAction(settings_action)
        
        # Run menu
        run_menu = menubar.addMenu("&Run")
        
        simulate_action = QAction(get_icon("mdi.test-tube", self.style_manager.get_icon_color()), "&Simulate", self)
        simulate_action.setShortcut(QKeySequence("F5"))
        simulate_action.triggered.connect(self._on_simulate)
        run_menu.addAction(simulate_action)
        
        run_action = QAction(get_icon("mdi.play", self.style_manager.get_icon_color()), "&Run", self)
        run_action.setShortcut(QKeySequence("F6"))
        run_action.triggered.connect(self._on_run)
        run_menu.addAction(run_action)
        
        run_menu.addSeparator()
        
        stop_action = QAction(get_icon("mdi.stop", self.style_manager.get_icon_color()), "S&top", self)
        stop_action.setShortcut(QKeySequence("Shift+F5"))
        stop_action.triggered.connect(self._on_stop)
        run_menu.addAction(stop_action)
        
        run_menu.addSeparator()
        
        clear_log_action = QAction(get_icon("mdi.delete-sweep", self.style_manager.get_icon_color()), "&Clear Log", self)
        clear_log_action.triggered.connect(self._on_clear_log)
        run_menu.addAction(clear_log_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        toggle_log_action = QAction("Toggle &Log Panel", self)
        toggle_log_action.setShortcut(QKeySequence("Ctrl+L"))
        toggle_log_action.setCheckable(True)
        toggle_log_action.setChecked(True)
        toggle_log_action.triggered.connect(self._on_toggle_log)
        view_menu.addAction(toggle_log_action)
        self._toggle_log_action = toggle_log_action
        
        view_menu.addSeparator()
        
        theme_menu = view_menu.addMenu("&Theme")
        dark_action = QAction("&Dark", self)
        dark_action.setCheckable(True)
        dark_action.setChecked(self.settings.ui.theme == "dark")
        dark_action.triggered.connect(lambda: self._on_theme_change("dark"))
        theme_menu.addAction(dark_action)
        
        light_action = QAction("&Light", self)
        light_action.setCheckable(True)
        light_action.setChecked(self.settings.ui.theme == "light")
        light_action.triggered.connect(lambda: self._on_theme_change("light"))
        theme_menu.addAction(light_action)
        
        self._theme_actions = [dark_action, light_action]
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        docs_action = QAction(get_icon("mdi.book-open-variant", self.style_manager.get_icon_color()), "&Documentation", self)
        docs_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        docs_action.triggered.connect(self._on_documentation)
        help_menu.addAction(docs_action)
        
        help_menu.addSeparator()
        
        about_action = QAction(get_icon("mdi.information", self.style_manager.get_icon_color()), "&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self) -> None:
        """Create the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addToolBar(toolbar)
        
        # New config
        new_btn = QToolButton()
        new_btn.setIcon(get_icon("mdi.file-plus", self.style_manager.get_icon_color()))
        new_btn.setToolTip("New Config (Ctrl+N)")
        new_btn.clicked.connect(self._on_new_config)
        toolbar.addWidget(new_btn)
        
        # Open config
        open_btn = QToolButton()
        open_btn.setIcon(get_icon("mdi.folder-open", self.style_manager.get_icon_color()))
        open_btn.setToolTip("Open Config (Ctrl+O)")
        open_btn.clicked.connect(self._on_open_config)
        toolbar.addWidget(open_btn)
        
        # Save config
        self.save_btn = QToolButton()
        self.save_btn.setIcon(get_icon("mdi.content-save", self.style_manager.get_icon_color()))
        self.save_btn.setToolTip("Save Config (Ctrl+S)")
        self.save_btn.clicked.connect(self._on_save_config)
        toolbar.addWidget(self.save_btn)
        
        toolbar.addSeparator()
        
        # Add rule
        add_rule_btn = QToolButton()
        add_rule_btn.setIcon(get_icon("mdi.plus-box", self.style_manager.get_icon_color()))
        add_rule_btn.setToolTip("Add Rule (Ctrl+R)")
        add_rule_btn.clicked.connect(self._on_add_rule)
        toolbar.addWidget(add_rule_btn)
        
        toolbar.addSeparator()
        
        # Simulate
        self.simulate_btn = QToolButton()
        self.simulate_btn.setIcon(get_icon("mdi.test-tube", self.style_manager.get_icon_color()))
        self.simulate_btn.setToolTip("Simulate (F5)")
        self.simulate_btn.clicked.connect(self._on_simulate)
        toolbar.addWidget(self.simulate_btn)
        
        # Run
        self.run_btn = QToolButton()
        self.run_btn.setIcon(get_icon("mdi.play", self.style_manager.get_accent_icon_color()))
        self.run_btn.setToolTip("Run (F6)")
        self.run_btn.clicked.connect(self._on_run)
        toolbar.addWidget(self.run_btn)
        
        # Stop
        self.stop_btn = QToolButton()
        self.stop_btn.setIcon(get_icon("mdi.stop", self.style_manager.colors["error"]))
        self.stop_btn.setToolTip("Stop (Shift+F5)")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        toolbar.addWidget(self.stop_btn)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # Settings
        settings_btn = QToolButton()
        settings_btn.setIcon(get_icon("mdi.cog", self.style_manager.get_icon_color()))
        settings_btn.setToolTip("Settings")
        settings_btn.clicked.connect(self._on_settings)
        toolbar.addWidget(settings_btn)
    
    def _create_central_widget(self) -> None:
        """Create the central widget with splitters."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Left sidebar (config list)
        self.sidebar = self._create_sidebar()
        self.main_splitter.addWidget(self.sidebar)
        
        # Right content area (editor + log)
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.addWidget(right_splitter)
        
        # Editor area (tabs for visual and YAML editor)
        self.editor_stack = QStackedWidget()
        
        # Rule editor (visual)
        self.rule_editor = RuleEditor(self.style_manager)
        self.rule_editor.rules_changed.connect(self._on_rules_changed)
        self.editor_stack.addWidget(self.rule_editor)
        
        # Config editor (YAML)
        self.config_editor = ConfigEditor(self.style_manager)
        self.config_editor.content_changed.connect(self._on_content_changed)
        self.editor_stack.addWidget(self.config_editor)
        
        # Editor container with tabs
        editor_container = self._create_editor_container()
        right_splitter.addWidget(editor_container)
        
        # Log viewer
        self.log_viewer = LogViewer(self.style_manager)
        self.log_dock = self.log_viewer
        right_splitter.addWidget(self.log_viewer)
        
        # Set splitter sizes
        self.main_splitter.setSizes([250, 950])
        right_splitter.setSizes([500, 200])
        
        # Store reference
        self.right_splitter = right_splitter
    
    def _create_sidebar(self) -> QWidget:
        """Create the sidebar with config file list."""
        sidebar = QFrame()
        sidebar.setProperty("class", "sidebar")
        sidebar.setFixedWidth(250)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        
        title = QLabel("Configs")
        title.setProperty("heading", True)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        refresh_btn = QToolButton()
        refresh_btn.setIcon(get_icon("mdi.refresh", self.style_manager.get_icon_color()))
        refresh_btn.setToolTip("Refresh list")
        refresh_btn.clicked.connect(self._refresh_config_list)
        header_layout.addWidget(refresh_btn)
        
        layout.addWidget(header)
        
        # Config list
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem
        self.config_list = QListWidget()
        self.config_list.itemClicked.connect(self._on_config_selected)
        self.config_list.itemDoubleClicked.connect(self._on_config_double_clicked)
        layout.addWidget(self.config_list)
        
        # Quick actions
        actions_frame = QFrame()
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setContentsMargins(12, 12, 12, 12)
        actions_layout.setSpacing(8)
        
        new_btn = QPushButton("New Config")
        new_btn.setIcon(get_icon("mdi.plus", self.style_manager.get_icon_color()))
        new_btn.clicked.connect(self._on_new_config)
        actions_layout.addWidget(new_btn)
        
        open_folder_btn = QPushButton("Open Folder")
        open_folder_btn.setIcon(get_icon("mdi.folder-open", self.style_manager.get_icon_color()))
        open_folder_btn.clicked.connect(self._on_open_config_folder)
        actions_layout.addWidget(open_folder_btn)
        
        layout.addWidget(actions_frame)
        
        return sidebar
    
    def _create_editor_container(self) -> QWidget:
        """Create the editor container with view toggle."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tab bar
        tab_bar = QFrame()
        tab_layout = QHBoxLayout(tab_bar)
        tab_layout.setContentsMargins(12, 8, 12, 8)
        tab_layout.setSpacing(8)
        
        self.visual_tab = QPushButton("Visual Editor")
        self.visual_tab.setCheckable(True)
        self.visual_tab.setChecked(True)
        self.visual_tab.clicked.connect(lambda: self._switch_editor(0))
        tab_layout.addWidget(self.visual_tab)
        
        self.yaml_tab = QPushButton("YAML Editor")
        self.yaml_tab.setCheckable(True)
        self.yaml_tab.clicked.connect(lambda: self._switch_editor(1))
        tab_layout.addWidget(self.yaml_tab)
        
        tab_layout.addStretch()
        
        # Config name label
        self.config_label = QLabel("Untitled")
        self.config_label.setProperty("subheading", True)
        tab_layout.addWidget(self.config_label)
        
        layout.addWidget(tab_bar)
        
        # Editor stack
        layout.addWidget(self.editor_stack)
        
        return container
    
    def _create_status_bar(self) -> None:
        """Create the status bar."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)
        
        status_bar.addPermanentWidget(QLabel("|"))
        
        # Config status
        self.config_status = QLabel("No config loaded")
        status_bar.addPermanentWidget(self.config_status)
        
        status_bar.addPermanentWidget(QLabel("|"))
        
        # Execution status
        self.exec_status = QLabel("Idle")
        status_bar.addPermanentWidget(self.exec_status)
    
    def _setup_signals(self) -> None:
        """Set up signal connections."""
        # Rule engine callbacks
        self.rule_engine.set_callbacks(
            on_status_change=self._on_execution_status_change,
            on_log=self._on_log_entry,
            on_complete=self._on_execution_complete,
        )
        
        # File watcher callback
        self.file_watcher.set_config_callback(self._on_config_file_changed)
    
    def _load_initial_state(self) -> None:
        """Load the initial application state."""
        # Refresh config list
        self._refresh_config_list()
        
        # Load last config or create new
        if self.settings.last_config_path:
            path = Path(self.settings.last_config_path)
            if path.exists():
                self._load_config(path)
                return
        
        # Create new config
        self.config_manager.new()
        self._update_editors()
    
    def _restore_geometry(self) -> None:
        """Restore window geometry from settings."""
        if self.settings.window_geometry:
            geo = self.settings.window_geometry
            if all(k in geo for k in ["x", "y", "width", "height"]):
                self.setGeometry(geo["x"], geo["y"], geo["width"], geo["height"])
    
    def _save_geometry(self) -> None:
        """Save window geometry to settings."""
        geo = self.geometry()
        self.settings.window_geometry = {
            "x": geo.x(),
            "y": geo.y(),
            "width": geo.width(),
            "height": geo.height(),
        }
        self.settings.save()
    
    def _switch_editor(self, index: int) -> None:
        """Switch between visual and YAML editor."""
        self.editor_stack.setCurrentIndex(index)
        self.visual_tab.setChecked(index == 0)
        self.yaml_tab.setChecked(index == 1)
        
        # Sync content when switching
        if index == 1:  # Switching to YAML
            self.config_editor.set_content(self.config_manager.raw_content)
        else:  # Switching to Visual
            rules = self.config_manager.get_rules()
            self.rule_editor.set_rules(rules)
    
    def _update_editors(self) -> None:
        """Update editor contents from config manager."""
        self.rule_editor.set_rules(self.config_manager.get_rules())
        self.config_editor.set_content(self.config_manager.raw_content)
        self.config_label.setText(self.config_manager.filename)
        self._update_window_title()
    
    def _update_window_title(self) -> None:
        """Update the window title."""
        title = "Organize Desktop"
        if self.config_manager.config_path:
            title = f"{self.config_manager.filename} - {title}"
        if self.config_manager.is_modified:
            title = f"* {title}"
        self.setWindowTitle(title)
    
    def _update_recent_menu(self) -> None:
        """Update the recent files menu."""
        self.recent_menu.clear()
        
        for entry in self.settings.recent_files:
            action = QAction(entry.get("name", "Unknown"), self)
            action.setData(entry.get("path"))
            action.triggered.connect(lambda checked, p=entry.get("path"): self._load_config(Path(p)))
            self.recent_menu.addAction(action)
        
        if not self.settings.recent_files:
            action = QAction("No recent files", self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
        else:
            self.recent_menu.addSeparator()
            clear_action = QAction("Clear Recent", self)
            clear_action.triggered.connect(self._on_clear_recent)
            self.recent_menu.addAction(clear_action)
    
    def _refresh_config_list(self) -> None:
        """Refresh the config file list."""
        self.config_list.clear()
        
        from PyQt6.QtWidgets import QListWidgetItem
        
        configs = ConfigManager.list_available_configs()
        for config_path in configs:
            item = QListWidgetItem(config_path.stem)
            item.setData(Qt.ItemDataRole.UserRole, str(config_path))
            item.setIcon(get_icon("mdi.file-document", self.style_manager.get_icon_color()))
            self.config_list.addItem(item)
    
    def _load_config(self, path: Path) -> bool:
        """Load a configuration file."""
        if self.config_manager.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if not self._on_save_config():
                    return False
            elif reply == QMessageBox.StandardButton.Cancel:
                return False
        
        if self.config_manager.load(path):
            self._update_editors()
            self.settings.last_config_path = str(path)
            self.settings.add_recent_file(str(path), path.name)
            self._update_recent_menu()
            self.config_status.setText(f"Loaded: {path.name}")
            
            # Start watching the config file
            self.file_watcher.watch_config(path)
            
            return True
        else:
            QMessageBox.warning(
                self,
                "Error Loading Config",
                f"Failed to load config:\n{self.config_manager.last_error}"
            )
            return False
    
    # Action handlers
    def _on_new_config(self) -> None:
        """Create a new configuration."""
        if self.config_manager.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if not self._on_save_config():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.config_manager.new()
        self._update_editors()
        self.config_status.setText("New config created")
    
    def _on_open_config(self) -> None:
        """Open a configuration file."""
        config_dir = ConfigManager.get_default_config_dir()
        
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Config",
            str(config_dir),
            "YAML Files (*.yaml *.yml);;All Files (*)"
        )
        
        if path:
            self._load_config(Path(path))
    
    def _on_save_config(self) -> bool:
        """Save the current configuration."""
        if not self.config_manager.config_path:
            return self._on_save_config_as()
        
        # Sync content from active editor
        if self.editor_stack.currentIndex() == 1:  # YAML editor
            content = self.config_editor.get_content()
            self.config_manager.set_content(content)
        else:  # Visual editor
            rules = self.rule_editor.get_rules()
            self.config_manager.set_rules(rules)
        
        if self.config_manager.save():
            self._update_window_title()
            self.config_status.setText(f"Saved: {self.config_manager.filename}")
            self.status_label.setText("Saved successfully")
            QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))
            return True
        else:
            QMessageBox.warning(
                self,
                "Error Saving Config",
                f"Failed to save config:\n{self.config_manager.last_error}"
            )
            return False
    
    def _on_save_config_as(self) -> bool:
        """Save the configuration to a new file."""
        config_dir = ConfigManager.get_default_config_dir()
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Config As",
            str(config_dir / "config.yaml"),
            "YAML Files (*.yaml *.yml)"
        )
        
        if path:
            # Sync content from active editor
            if self.editor_stack.currentIndex() == 1:
                content = self.config_editor.get_content()
                self.config_manager.set_content(content)
            else:
                rules = self.rule_editor.get_rules()
                self.config_manager.set_rules(rules)
            
            if self.config_manager.save(Path(path)):
                self._update_window_title()
                self._refresh_config_list()
                self.settings.add_recent_file(path, Path(path).name)
                self._update_recent_menu()
                return True
            else:
                QMessageBox.warning(
                    self,
                    "Error Saving Config",
                    f"Failed to save config:\n{self.config_manager.last_error}"
                )
        return False
    
    def _on_config_selected(self, item) -> None:
        """Handle config list item selection."""
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.config_status.setText(f"Selected: {item.text()}")
    
    def _on_config_double_clicked(self, item) -> None:
        """Handle config list item double-click."""
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self._load_config(Path(path))
    
    def _on_open_config_folder(self) -> None:
        """Open the config folder in file manager."""
        from ..utils.helpers import open_file_manager
        config_dir = ConfigManager.get_default_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        open_file_manager(config_dir)
    
    def _on_clear_recent(self) -> None:
        """Clear recent files list."""
        self.settings.clear_recent_files()
        self._update_recent_menu()
    
    def _on_undo(self) -> None:
        """Handle undo action."""
        if self.editor_stack.currentIndex() == 1:
            self.config_editor.undo()
    
    def _on_redo(self) -> None:
        """Handle redo action."""
        if self.editor_stack.currentIndex() == 1:
            self.config_editor.redo()
    
    def _on_add_rule(self) -> None:
        """Add a new rule."""
        self.rule_editor.add_empty_rule()
        self._switch_editor(0)  # Switch to visual editor
    
    def _on_rules_changed(self, rules: list) -> None:
        """Handle rules change from visual editor."""
        self.config_manager.set_rules(rules)
        self._update_window_title()
    
    def _on_content_changed(self, content: str) -> None:
        """Handle content change from YAML editor."""
        self.config_manager.set_content(content)
        self._update_window_title()
    
    def _on_simulate(self) -> None:
        """Run simulation."""
        self._execute(simulate=True)
    
    def _on_run(self) -> None:
        """Run actual execution."""
        if self.settings.ui.confirm_dangerous_actions:
            reply = QMessageBox.question(
                self,
                "Confirm Run",
                "This will actually modify your files. Are you sure?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self._execute(simulate=False)
    
    def _execute(self, simulate: bool) -> None:
        """Execute the rules."""
        # Sync content from active editor
        if self.editor_stack.currentIndex() == 1:
            content = self.config_editor.get_content()
        else:
            rules = self.rule_editor.get_rules()
            import yaml
            content = yaml.dump({"rules": rules}, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Validate config
        is_valid, error = self.config_manager.validate(content)
        if not is_valid:
            QMessageBox.warning(
                self,
                "Invalid Config",
                f"Cannot execute - config is invalid:\n{error}"
            )
            return
        
        # Clear log if configured
        if self.settings.run.clear_log_on_run:
            self.log_viewer.clear()
        
        # Run the engine
        self.rule_engine.run_from_string(
            config_string=content,
            config_path=self.config_manager.config_path,
            simulate=simulate,
        )
    
    def _on_stop(self) -> None:
        """Stop execution."""
        self.rule_engine.cancel()
    
    def _on_clear_log(self) -> None:
        """Clear the log viewer."""
        self.log_viewer.clear()
        self.rule_engine.clear_logs()
    
    def _on_toggle_log(self, checked: bool) -> None:
        """Toggle log panel visibility."""
        self.log_viewer.setVisible(checked)
    
    def _on_execution_status_change(self, status: ExecutionStatus) -> None:
        """Handle execution status change."""
        self.exec_status.setText(status.name.title())
        
        is_running = status in (ExecutionStatus.RUNNING, ExecutionStatus.PAUSED)
        self.simulate_btn.setEnabled(not is_running)
        self.run_btn.setEnabled(not is_running)
        self.stop_btn.setEnabled(is_running)
        
        if status == ExecutionStatus.RUNNING:
            self.status_label.setText("Running...")
        elif status == ExecutionStatus.COMPLETED:
            self.status_label.setText("Completed")
        elif status == ExecutionStatus.FAILED:
            self.status_label.setText("Failed")
        elif status == ExecutionStatus.CANCELLED:
            self.status_label.setText("Cancelled")
    
    def _on_log_entry(self, entry: LogEntry) -> None:
        """Handle log entry from rule engine."""
        self.log_viewer.add_entry(entry)
    
    def _on_execution_complete(self, result) -> None:
        """Handle execution completion."""
        self.status_label.setText(
            f"Done: {result.success_count} success, {result.error_count} errors"
        )
    
    def _on_config_file_changed(self, path: Path) -> None:
        """Handle external config file change."""
        reply = QMessageBox.question(
            self,
            "File Changed",
            f"The config file has been modified externally.\n\n"
            f"Do you want to reload it?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._load_config(path)
    
    def _on_theme_change(self, theme: str) -> None:
        """Handle theme change."""
        self.settings.ui.theme = theme
        self.settings.save()
        
        self.style_manager.set_theme(Theme.DARK if theme == "dark" else Theme.LIGHT)
        self.setStyleSheet(self.style_manager.get_stylesheet())
        
        # Refresh styles on child widgets
        self._refresh_child_styles()
        
        # Update theme menu checkmarks
        for action in self._theme_actions:
            action.setChecked(action.text().lower().replace("&", "") == theme)
    
    def _refresh_child_styles(self) -> None:
        """Refresh styles on all child widgets after theme change."""
        # Refresh rule editor
        if hasattr(self, 'rule_editor'):
            self.rule_editor.refresh_style(self.style_manager)
        
        # Refresh config editor
        if hasattr(self, 'config_editor'):
            self.config_editor.refresh_style(self.style_manager)
        
        # Refresh log viewer
        if hasattr(self, 'log_viewer'):
            self.log_viewer.refresh_style(self.style_manager)
        
        # Refresh sidebar
        if hasattr(self, 'sidebar'):
            self.sidebar.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.style_manager.colors["surface"]};
                    border-right: 1px solid {self.style_manager.colors["border"]};
                }}
            """)
    
    def _on_settings(self) -> None:
        """Open settings dialog."""
        dialog = SettingsDialog(self.settings, self.style_manager, self)
        if dialog.exec():
            self.settings.save()
            # Apply settings
            if self.settings.ui.theme != ("dark" if self.style_manager.theme == Theme.DARK else "light"):
                self._on_theme_change(self.settings.ui.theme)
    
    def _on_documentation(self) -> None:
        """Open documentation."""
        import webbrowser
        webbrowser.open("https://organize.readthedocs.io")
    
    def _on_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Organize Desktop",
            "<h2>Organize Desktop</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A modern desktop application for the organize "
            "file management automation tool.</p>"
            "<p><a href='https://github.com/tfeldmann/organize'>organize on GitHub</a></p>"
            "<p>Built with PyQt6</p>"
        )
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event."""
        if self.config_manager.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if not self._on_save_config():
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        # Stop file watcher
        self.file_watcher.stop()
        
        # Save geometry
        self._save_geometry()
        
        # Accept the close event
        event.accept()
