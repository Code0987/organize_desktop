"""
Log viewer component for displaying execution output.
"""

from typing import Optional, List
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QFrame, QPushButton, QToolButton, QComboBox, QLineEdit,
    QFileDialog, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat, QFont

try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False

from .styles import StyleManager
from ..core.rule_engine import LogEntry


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


class LogViewer(QWidget):
    """
    Log viewer widget for displaying execution output.
    
    Features:
    - Color-coded log levels
    - Auto-scrolling
    - Filtering by level
    - Search functionality
    - Export to file
    """
    
    def __init__(self, style_manager: StyleManager, parent: Optional[QWidget] = None):
        """Initialize the log viewer."""
        super().__init__(parent)
        self.style_manager = style_manager
        self.entries: List[LogEntry] = []
        self.filtered_entries: List[LogEntry] = []
        
        self._auto_scroll = True
        self._filter_level = "all"
        self._search_text = ""
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {self.style_manager.colors["surface"]};
                border-bottom: 1px solid {self.style_manager.colors["border"]};
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(8)
        
        # Title
        title = QLabel("Output")
        title.setStyleSheet(f"font-weight: bold; color: {self.style_manager.colors['text']};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Filter dropdown
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet(f"color: {self.style_manager.colors['text_secondary']};")
        header_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Info", "Success", "Warning", "Error", "Debug"])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        header_layout.addWidget(self.filter_combo)
        
        # Search
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.setMaximumWidth(200)
        self.search_edit.textChanged.connect(self._on_search_changed)
        header_layout.addWidget(self.search_edit)
        
        # Clear button
        clear_btn = QToolButton()
        clear_btn.setIcon(get_icon("mdi.delete-sweep", self.style_manager.get_icon_color()))
        clear_btn.setToolTip("Clear log")
        clear_btn.clicked.connect(self.clear)
        header_layout.addWidget(clear_btn)
        
        # Auto-scroll toggle
        self.scroll_btn = QToolButton()
        self.scroll_btn.setIcon(get_icon("mdi.arrow-down-bold", self.style_manager.colors["primary"]))
        self.scroll_btn.setToolTip("Auto-scroll")
        self.scroll_btn.setCheckable(True)
        self.scroll_btn.setChecked(True)
        self.scroll_btn.clicked.connect(self._on_scroll_toggle)
        header_layout.addWidget(self.scroll_btn)
        
        # Export button
        export_btn = QToolButton()
        export_btn.setIcon(get_icon("mdi.download", self.style_manager.get_icon_color()))
        export_btn.setToolTip("Export log")
        export_btn.clicked.connect(self._on_export)
        header_layout.addWidget(export_btn)
        
        layout.addWidget(header)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.style_manager.colors["background"]};
                color: {self.style_manager.colors["text"]};
                border: none;
                padding: 8px;
            }}
        """)
        layout.addWidget(self.log_text)
        
        # Status bar
        status_bar = QFrame()
        status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {self.style_manager.colors["surface"]};
                border-top: 1px solid {self.style_manager.colors["border"]};
            }}
        """)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(12, 4, 12, 4)
        
        self.count_label = QLabel("0 entries")
        self.count_label.setStyleSheet(f"color: {self.style_manager.colors['text_secondary']}; font-size: 11px;")
        status_layout.addWidget(self.count_label)
        
        status_layout.addStretch()
        
        # Stats
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet(f"color: {self.style_manager.colors['text_secondary']}; font-size: 11px;")
        status_layout.addWidget(self.stats_label)
        
        layout.addWidget(status_bar)
    
    def add_entry(self, entry: LogEntry) -> None:
        """
        Add a log entry.
        
        Args:
            entry: Log entry to add
        """
        self.entries.append(entry)
        
        # Check if entry matches current filter
        if self._matches_filter(entry):
            self.filtered_entries.append(entry)
            self._append_entry_to_display(entry)
        
        self._update_status()
    
    def _append_entry_to_display(self, entry: LogEntry) -> None:
        """Append an entry to the text display."""
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Format based on level
        format = QTextCharFormat()
        colors = self.style_manager.colors
        
        level_colors = {
            "info": colors["text"],
            "success": colors["success"],
            "warning": colors["warning"],
            "error": colors["error"],
            "debug": colors["text_secondary"],
        }
        
        level_icons = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✗",
            "debug": "🔧",
        }
        
        color = level_colors.get(entry.level, colors["text"])
        icon = level_icons.get(entry.level, "•")
        format.setForeground(QColor(color))
        
        # Timestamp
        timestamp = entry.timestamp.strftime("%H:%M:%S")
        
        # Build message
        parts = [f"[{timestamp}]", icon]
        
        if entry.rule_name:
            parts.append(f"[{entry.rule_name}]")
        
        if entry.file_path:
            # Truncate long paths
            path = entry.file_path
            if len(path) > 60:
                path = "..." + path[-57:]
            parts.append(f"({path})")
        
        if entry.action_name:
            parts.append(f"<{entry.action_name}>")
        
        parts.append(entry.message)
        
        # Insert text
        cursor.insertText(" ".join(parts) + "\n", format)
        
        # Auto-scroll
        if self._auto_scroll:
            self.log_text.moveCursor(QTextCursor.MoveOperation.End)
    
    def clear(self) -> None:
        """Clear all log entries."""
        self.entries = []
        self.filtered_entries = []
        self.log_text.clear()
        self._update_status()
    
    def _matches_filter(self, entry: LogEntry) -> bool:
        """Check if an entry matches the current filter."""
        # Level filter
        if self._filter_level != "all":
            if entry.level != self._filter_level:
                return False
        
        # Search filter
        if self._search_text:
            search_lower = self._search_text.lower()
            if (search_lower not in entry.message.lower() and
                search_lower not in (entry.file_path or "").lower() and
                search_lower not in (entry.rule_name or "").lower()):
                return False
        
        return True
    
    def _refresh_display(self) -> None:
        """Refresh the display with current filters."""
        self.log_text.clear()
        self.filtered_entries = []
        
        for entry in self.entries:
            if self._matches_filter(entry):
                self.filtered_entries.append(entry)
                self._append_entry_to_display(entry)
        
        self._update_status()
    
    def _update_status(self) -> None:
        """Update the status bar."""
        total = len(self.entries)
        filtered = len(self.filtered_entries)
        
        if total == filtered:
            self.count_label.setText(f"{total} entries")
        else:
            self.count_label.setText(f"{filtered} of {total} entries")
        
        # Calculate stats
        success = sum(1 for e in self.entries if e.level == "success")
        errors = sum(1 for e in self.entries if e.level == "error")
        warnings = sum(1 for e in self.entries if e.level == "warning")
        
        stats_parts = []
        if success:
            stats_parts.append(f"✓ {success}")
        if warnings:
            stats_parts.append(f"⚠ {warnings}")
        if errors:
            stats_parts.append(f"✗ {errors}")
        
        self.stats_label.setText("  ".join(stats_parts))
    
    def _on_filter_changed(self, text: str) -> None:
        """Handle filter change."""
        self._filter_level = text.lower() if text.lower() != "all" else "all"
        self._refresh_display()
    
    def _on_search_changed(self, text: str) -> None:
        """Handle search text change."""
        self._search_text = text
        self._refresh_display()
    
    def _on_scroll_toggle(self, checked: bool) -> None:
        """Handle auto-scroll toggle."""
        self._auto_scroll = checked
        if checked:
            self.log_text.moveCursor(QTextCursor.MoveOperation.End)
    
    def _on_export(self) -> None:
        """Export log to file."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Log",
            f"organize_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if not path:
            return
        
        try:
            if path.endswith(".json"):
                import json
                data = [entry.to_dict() for entry in self.entries]
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            elif path.endswith(".csv"):
                import csv
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Level", "Message", "Rule", "File", "Action"])
                    for entry in self.entries:
                        writer.writerow([
                            entry.timestamp.isoformat(),
                            entry.level,
                            entry.message,
                            entry.rule_name or "",
                            entry.file_path or "",
                            entry.action_name or "",
                        ])
            else:
                lines = []
                for entry in self.entries:
                    timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    lines.append(f"[{timestamp}] [{entry.level.upper()}] {entry.message}")
                with open(path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Export Failed", f"Failed to export log: {e}")
