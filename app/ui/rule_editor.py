"""
Visual rule editor component.
Provides a graphical interface for creating and editing organize rules.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox,
    QSpinBox, QTextEdit, QListWidget, QListWidgetItem,
    QMenu, QDialog, QDialogButtonBox, QFormLayout, QGroupBox,
    QSplitter, QToolButton, QSizePolicy, QMessageBox,
    QFileDialog, QStackedWidget, QTabWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag, QAction, QIcon

try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False

from .styles import StyleManager
from ..utils.constants import FILTERS, ACTIONS, FILTER_MODES, FILE_CATEGORIES


def get_icon(name: str, color: str = "#cdd6f4") -> QIcon:
    """Get an icon, with fallback for missing qtawesome."""
    if HAS_QTAWESOME:
        try:
            return qta.icon(name, color=color)
        except Exception:
            return QIcon()
    return QIcon()


class RuleCard(QFrame):
    """
    A card widget representing a single rule.
    Displays rule information and provides edit/delete controls.
    """
    
    edit_requested = pyqtSignal(int)  # Emits rule index
    delete_requested = pyqtSignal(int)
    duplicate_requested = pyqtSignal(int)
    move_up_requested = pyqtSignal(int)
    move_down_requested = pyqtSignal(int)
    toggle_enabled = pyqtSignal(int, bool)
    
    def __init__(
        self,
        index: int,
        rule: Dict[str, Any],
        style_manager: StyleManager,
        parent: Optional[QWidget] = None,
    ):
        """Initialize the rule card."""
        super().__init__(parent)
        self.index = index
        self.rule = rule
        self.style_manager = style_manager
        
        self.setProperty("class", "card")
        self.setStyleSheet(f"""
            RuleCard {{
                background-color: {style_manager.colors["surface"]};
                border: 1px solid {style_manager.colors["border"]};
                border-radius: 8px;
                padding: 12px;
            }}
            RuleCard:hover {{
                border-color: {style_manager.colors["primary"]};
            }}
        """)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Header row
        header = QHBoxLayout()
        header.setSpacing(8)
        
        # Enable checkbox
        self.enabled_cb = QCheckBox()
        self.enabled_cb.setChecked(self.rule.get("enabled", True))
        self.enabled_cb.stateChanged.connect(
            lambda state: self.toggle_enabled.emit(self.index, state == Qt.CheckState.Checked.value)
        )
        header.addWidget(self.enabled_cb)
        
        # Rule name
        name = self.rule.get("name", f"Rule {self.index + 1}")
        name_label = QLabel(f"<b>{name}</b>")
        header.addWidget(name_label)
        
        header.addStretch()
        
        # Target indicator
        targets = self.rule.get("targets", "files")
        target_icon = "mdi.file" if targets == "files" else "mdi.folder"
        target_btn = QToolButton()
        target_btn.setIcon(get_icon(target_icon, self.style_manager.colors["text_secondary"]))
        target_btn.setToolTip(f"Target: {targets}")
        target_btn.setEnabled(False)
        header.addWidget(target_btn)
        
        layout.addLayout(header)
        
        # Info row
        info_layout = QHBoxLayout()
        info_layout.setSpacing(16)
        
        # Locations count
        locations = self.rule.get("locations", [])
        if isinstance(locations, str):
            locations = [locations]
        loc_label = QLabel(f"📁 {len(locations)} location(s)")
        loc_label.setStyleSheet(f"color: {self.style_manager.colors['text_secondary']};")
        info_layout.addWidget(loc_label)
        
        # Filters count
        filters = self.rule.get("filters", [])
        filter_label = QLabel(f"🔍 {len(filters)} filter(s)")
        filter_label.setStyleSheet(f"color: {self.style_manager.colors['text_secondary']};")
        info_layout.addWidget(filter_label)
        
        # Actions count
        actions = self.rule.get("actions", [])
        action_label = QLabel(f"⚡ {len(actions)} action(s)")
        action_label.setStyleSheet(f"color: {self.style_manager.colors['text_secondary']};")
        info_layout.addWidget(action_label)
        
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)
        
        edit_btn = QPushButton("Edit")
        edit_btn.setIcon(get_icon("mdi.pencil", self.style_manager.get_icon_color()))
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.index))
        btn_layout.addWidget(edit_btn)
        
        duplicate_btn = QToolButton()
        duplicate_btn.setIcon(get_icon("mdi.content-copy", self.style_manager.get_icon_color()))
        duplicate_btn.setToolTip("Duplicate")
        duplicate_btn.clicked.connect(lambda: self.duplicate_requested.emit(self.index))
        btn_layout.addWidget(duplicate_btn)
        
        up_btn = QToolButton()
        up_btn.setIcon(get_icon("mdi.arrow-up", self.style_manager.get_icon_color()))
        up_btn.setToolTip("Move up")
        up_btn.clicked.connect(lambda: self.move_up_requested.emit(self.index))
        btn_layout.addWidget(up_btn)
        
        down_btn = QToolButton()
        down_btn.setIcon(get_icon("mdi.arrow-down", self.style_manager.get_icon_color()))
        down_btn.setToolTip("Move down")
        down_btn.clicked.connect(lambda: self.move_down_requested.emit(self.index))
        btn_layout.addWidget(down_btn)
        
        btn_layout.addStretch()
        
        delete_btn = QToolButton()
        delete_btn.setIcon(get_icon("mdi.delete", self.style_manager.colors["error"]))
        delete_btn.setToolTip("Delete")
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.index))
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)


class RuleEditDialog(QDialog):
    """
    Dialog for editing a single rule.
    Provides forms for locations, filters, and actions.
    """
    
    def __init__(
        self,
        rule: Dict[str, Any],
        style_manager: StyleManager,
        parent: Optional[QWidget] = None,
    ):
        """Initialize the rule edit dialog."""
        super().__init__(parent)
        self.rule = rule.copy() if rule else {}
        self.style_manager = style_manager
        
        self.setWindowTitle("Edit Rule")
        self.setMinimumSize(700, 600)
        self.setStyleSheet(style_manager.get_stylesheet())
        
        self._setup_ui()
        self._load_rule()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # General tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Optional rule name")
        general_layout.addRow("Name:", self.name_edit)
        
        self.enabled_cb = QCheckBox("Enabled")
        self.enabled_cb.setChecked(True)
        general_layout.addRow("", self.enabled_cb)
        
        self.targets_combo = QComboBox()
        self.targets_combo.addItems(["files", "dirs"])
        general_layout.addRow("Targets:", self.targets_combo)
        
        self.subfolders_cb = QCheckBox("Include subfolders")
        general_layout.addRow("", self.subfolders_cb)
        
        self.filter_mode_combo = QComboBox()
        for mode, info in FILTER_MODES.items():
            self.filter_mode_combo.addItem(info["name"], mode)
        general_layout.addRow("Filter Mode:", self.filter_mode_combo)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Comma-separated tags")
        general_layout.addRow("Tags:", self.tags_edit)
        
        tabs.addTab(general_tab, "General")
        
        # Locations tab
        locations_tab = QWidget()
        locations_layout = QVBoxLayout(locations_tab)
        
        # Location list
        self.locations_list = QListWidget()
        locations_layout.addWidget(self.locations_list)
        
        # Location buttons
        loc_btn_layout = QHBoxLayout()
        
        add_loc_btn = QPushButton("Add Location")
        add_loc_btn.setIcon(get_icon("mdi.folder-plus", self.style_manager.get_icon_color()))
        add_loc_btn.clicked.connect(self._add_location)
        loc_btn_layout.addWidget(add_loc_btn)
        
        remove_loc_btn = QPushButton("Remove")
        remove_loc_btn.setIcon(get_icon("mdi.delete", self.style_manager.colors["error"]))
        remove_loc_btn.clicked.connect(self._remove_location)
        loc_btn_layout.addWidget(remove_loc_btn)
        
        loc_btn_layout.addStretch()
        
        locations_layout.addLayout(loc_btn_layout)
        tabs.addTab(locations_tab, "Locations")
        
        # Filters tab
        filters_tab = QWidget()
        filters_layout = QVBoxLayout(filters_tab)
        
        # Filter list
        self.filters_list = QListWidget()
        filters_layout.addWidget(self.filters_list)
        
        # Filter buttons
        filter_btn_layout = QHBoxLayout()
        
        add_filter_btn = QPushButton("Add Filter")
        add_filter_btn.setIcon(get_icon("mdi.filter-plus", self.style_manager.get_icon_color()))
        add_filter_menu = QMenu()
        for filter_name, filter_info in FILTERS.items():
            action = add_filter_menu.addAction(
                get_icon(filter_info.get("icon", "mdi.filter"), self.style_manager.get_icon_color()),
                filter_info["name"]
            )
            action.setData(filter_name)
            action.triggered.connect(lambda checked, fn=filter_name: self._add_filter(fn))
        add_filter_btn.setMenu(add_filter_menu)
        filter_btn_layout.addWidget(add_filter_btn)
        
        remove_filter_btn = QPushButton("Remove")
        remove_filter_btn.setIcon(get_icon("mdi.delete", self.style_manager.colors["error"]))
        remove_filter_btn.clicked.connect(self._remove_filter)
        filter_btn_layout.addWidget(remove_filter_btn)
        
        filter_btn_layout.addStretch()
        
        filters_layout.addLayout(filter_btn_layout)
        tabs.addTab(filters_tab, "Filters")
        
        # Actions tab
        actions_tab = QWidget()
        actions_layout = QVBoxLayout(actions_tab)
        
        # Actions list
        self.actions_list = QListWidget()
        actions_layout.addWidget(self.actions_list)
        
        # Actions buttons
        action_btn_layout = QHBoxLayout()
        
        add_action_btn = QPushButton("Add Action")
        add_action_btn.setIcon(get_icon("mdi.plus-box", self.style_manager.get_icon_color()))
        add_action_menu = QMenu()
        for action_name, action_info in ACTIONS.items():
            action = add_action_menu.addAction(
                get_icon(action_info.get("icon", "mdi.flash"), self.style_manager.get_icon_color()),
                action_info["name"]
            )
            action.setData(action_name)
            action.triggered.connect(lambda checked, an=action_name: self._add_action(an))
        add_action_btn.setMenu(add_action_menu)
        action_btn_layout.addWidget(add_action_btn)
        
        remove_action_btn = QPushButton("Remove")
        remove_action_btn.setIcon(get_icon("mdi.delete", self.style_manager.colors["error"]))
        remove_action_btn.clicked.connect(self._remove_action)
        action_btn_layout.addWidget(remove_action_btn)
        
        action_btn_layout.addStretch()
        
        actions_layout.addLayout(action_btn_layout)
        tabs.addTab(actions_tab, "Actions")
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _load_rule(self) -> None:
        """Load rule data into the form."""
        self.name_edit.setText(self.rule.get("name", ""))
        self.enabled_cb.setChecked(self.rule.get("enabled", True))
        self.subfolders_cb.setChecked(self.rule.get("subfolders", False))
        
        # Target
        targets = self.rule.get("targets", "files")
        self.targets_combo.setCurrentText(targets)
        
        # Filter mode
        filter_mode = self.rule.get("filter_mode", "all")
        index = self.filter_mode_combo.findData(filter_mode)
        if index >= 0:
            self.filter_mode_combo.setCurrentIndex(index)
        
        # Tags
        tags = self.rule.get("tags", [])
        if isinstance(tags, list):
            self.tags_edit.setText(", ".join(tags))
        
        # Locations
        locations = self.rule.get("locations", [])
        if isinstance(locations, str):
            locations = [locations]
        for loc in locations:
            if isinstance(loc, dict):
                loc_str = loc.get("path", str(loc))
            else:
                loc_str = str(loc)
            item = QListWidgetItem(loc_str)
            item.setData(Qt.ItemDataRole.UserRole, loc)
            self.locations_list.addItem(item)
        
        # Filters
        filters = self.rule.get("filters", [])
        for f in filters:
            if isinstance(f, str):
                f = {f: None}
            if isinstance(f, dict):
                for name, value in f.items():
                    display = f"{name}: {value}" if value else name
                    item = QListWidgetItem(display)
                    item.setData(Qt.ItemDataRole.UserRole, {name: value})
                    self.filters_list.addItem(item)
        
        # Actions
        actions = self.rule.get("actions", [])
        for a in actions:
            if isinstance(a, str):
                a = {a: None}
            if isinstance(a, dict):
                for name, value in a.items():
                    display = f"{name}: {value}" if value else name
                    item = QListWidgetItem(display)
                    item.setData(Qt.ItemDataRole.UserRole, {name: value})
                    self.actions_list.addItem(item)
    
    def _add_location(self) -> None:
        """Add a new location."""
        path = QFileDialog.getExistingDirectory(self, "Select Location")
        if path:
            item = QListWidgetItem(path)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.locations_list.addItem(item)
    
    def _remove_location(self) -> None:
        """Remove the selected location."""
        row = self.locations_list.currentRow()
        if row >= 0:
            self.locations_list.takeItem(row)
    
    def _add_filter(self, filter_name: str) -> None:
        """Add a new filter."""
        filter_info = FILTERS.get(filter_name, {})
        display = filter_info.get("name", filter_name)
        item = QListWidgetItem(display)
        item.setData(Qt.ItemDataRole.UserRole, {filter_name: None})
        self.filters_list.addItem(item)
    
    def _remove_filter(self) -> None:
        """Remove the selected filter."""
        row = self.filters_list.currentRow()
        if row >= 0:
            self.filters_list.takeItem(row)
    
    def _add_action(self, action_name: str) -> None:
        """Add a new action."""
        action_info = ACTIONS.get(action_name, {})
        display = action_info.get("name", action_name)
        item = QListWidgetItem(display)
        item.setData(Qt.ItemDataRole.UserRole, {action_name: None})
        self.actions_list.addItem(item)
    
    def _remove_action(self) -> None:
        """Remove the selected action."""
        row = self.actions_list.currentRow()
        if row >= 0:
            self.actions_list.takeItem(row)
    
    def get_rule(self) -> Dict[str, Any]:
        """Get the edited rule."""
        rule = {}
        
        # Name
        name = self.name_edit.text().strip()
        if name:
            rule["name"] = name
        
        # Enabled
        if not self.enabled_cb.isChecked():
            rule["enabled"] = False
        
        # Targets
        targets = self.targets_combo.currentText()
        if targets != "files":
            rule["targets"] = targets
        
        # Subfolders
        if self.subfolders_cb.isChecked():
            rule["subfolders"] = True
        
        # Filter mode
        filter_mode = self.filter_mode_combo.currentData()
        if filter_mode != "all":
            rule["filter_mode"] = filter_mode
        
        # Tags
        tags_str = self.tags_edit.text().strip()
        if tags_str:
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]
            if tags:
                rule["tags"] = tags
        
        # Locations
        locations = []
        for i in range(self.locations_list.count()):
            item = self.locations_list.item(i)
            loc_data = item.data(Qt.ItemDataRole.UserRole)
            locations.append(loc_data)
        if locations:
            rule["locations"] = locations
        
        # Filters
        filters = []
        for i in range(self.filters_list.count()):
            item = self.filters_list.item(i)
            filter_data = item.data(Qt.ItemDataRole.UserRole)
            filters.append(filter_data)
        if filters:
            rule["filters"] = filters
        
        # Actions
        actions = []
        for i in range(self.actions_list.count()):
            item = self.actions_list.item(i)
            action_data = item.data(Qt.ItemDataRole.UserRole)
            actions.append(action_data)
        if actions:
            rule["actions"] = actions
        else:
            # At least one action is required
            rule["actions"] = [{"echo": "Hello World!"}]
        
        return rule


class RuleEditor(QWidget):
    """
    Visual rule editor widget.
    Displays rules as cards and allows editing, reordering, and deletion.
    """
    
    rules_changed = pyqtSignal(list)  # Emits the updated rules list
    
    def __init__(self, style_manager: StyleManager, parent: Optional[QWidget] = None):
        """Initialize the rule editor."""
        super().__init__(parent)
        self.style_manager = style_manager
        self.rules: List[Dict[str, Any]] = []
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area for rule cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.style_manager.colors["background"]};
                border: none;
            }}
        """)
        
        # Container for rule cards
        self.container = QWidget()
        self.container.setStyleSheet(f"background-color: {self.style_manager.colors['background']};")
        self.cards_layout = QVBoxLayout(self.container)
        self.cards_layout.setContentsMargins(16, 16, 16, 16)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        
        # Empty state
        self.empty_label = QLabel("No rules defined.\nClick 'Add Rule' to create your first rule.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"color: {self.style_manager.colors['text_secondary']}; padding: 40px;")
        self.cards_layout.insertWidget(0, self.empty_label)
    
    def set_rules(self, rules: List[Dict[str, Any]]) -> None:
        """Set the rules to display."""
        self.rules = rules.copy() if rules else []
        self._refresh_cards()
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """Get the current rules."""
        return self.rules.copy()
    
    def add_empty_rule(self) -> None:
        """Add an empty rule."""
        new_rule = {
            "name": f"New Rule {len(self.rules) + 1}",
            "locations": [],
            "filters": [],
            "actions": [{"echo": "Hello World!"}],
        }
        
        dialog = RuleEditDialog(new_rule, self.style_manager, self)
        if dialog.exec():
            self.rules.append(dialog.get_rule())
            self._refresh_cards()
            self.rules_changed.emit(self.rules)
    
    def _refresh_cards(self) -> None:
        """Refresh the rule cards display."""
        # Clear existing cards (but not the empty label or stretch)
        while self.cards_layout.count() > 0:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget and widget != self.empty_label:
                widget.deleteLater()
        
        # Re-add the empty label
        self.cards_layout.addWidget(self.empty_label)
        self.empty_label.setVisible(len(self.rules) == 0)
        
        # Add rule cards
        for i, rule in enumerate(self.rules):
            card = RuleCard(i, rule, self.style_manager)
            card.edit_requested.connect(self._on_edit_rule)
            card.delete_requested.connect(self._on_delete_rule)
            card.duplicate_requested.connect(self._on_duplicate_rule)
            card.move_up_requested.connect(self._on_move_up)
            card.move_down_requested.connect(self._on_move_down)
            card.toggle_enabled.connect(self._on_toggle_enabled)
            self.cards_layout.insertWidget(i, card)
        
        # Add stretch at the end
        self.cards_layout.addStretch()
    
    def refresh_style(self, style_manager: StyleManager) -> None:
        """Refresh styles after theme change."""
        self.style_manager = style_manager
        self.empty_label.setStyleSheet(f"color: {style_manager.colors['text_secondary']}; padding: 40px;")
        
        # Update scroll area and container backgrounds
        self.scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {style_manager.colors["background"]};
                border: none;
            }}
        """)
        self.container.setStyleSheet(f"background-color: {style_manager.colors['background']};")
        
        # Refresh all cards (they will be recreated with new style_manager)
        self._refresh_cards()
    
    def _on_edit_rule(self, index: int) -> None:
        """Handle rule edit request."""
        if 0 <= index < len(self.rules):
            dialog = RuleEditDialog(self.rules[index], self.style_manager, self)
            if dialog.exec():
                self.rules[index] = dialog.get_rule()
                self._refresh_cards()
                self.rules_changed.emit(self.rules)
    
    def _on_delete_rule(self, index: int) -> None:
        """Handle rule delete request."""
        if 0 <= index < len(self.rules):
            reply = QMessageBox.question(
                self,
                "Delete Rule",
                f"Are you sure you want to delete this rule?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.rules.pop(index)
                self._refresh_cards()
                self.rules_changed.emit(self.rules)
    
    def _on_duplicate_rule(self, index: int) -> None:
        """Handle rule duplicate request."""
        if 0 <= index < len(self.rules):
            import copy
            new_rule = copy.deepcopy(self.rules[index])
            if "name" in new_rule:
                new_rule["name"] = f"{new_rule['name']} (copy)"
            self.rules.insert(index + 1, new_rule)
            self._refresh_cards()
            self.rules_changed.emit(self.rules)
    
    def _on_move_up(self, index: int) -> None:
        """Handle move up request."""
        if index > 0:
            self.rules[index], self.rules[index - 1] = self.rules[index - 1], self.rules[index]
            self._refresh_cards()
            self.rules_changed.emit(self.rules)
    
    def _on_move_down(self, index: int) -> None:
        """Handle move down request."""
        if index < len(self.rules) - 1:
            self.rules[index], self.rules[index + 1] = self.rules[index + 1], self.rules[index]
            self._refresh_cards()
            self.rules_changed.emit(self.rules)
    
    def _on_toggle_enabled(self, index: int, enabled: bool) -> None:
        """Handle rule enable/disable toggle."""
        if 0 <= index < len(self.rules):
            self.rules[index]["enabled"] = enabled
            self.rules_changed.emit(self.rules)
