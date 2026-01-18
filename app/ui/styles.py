"""
Style manager for the application.
Provides modern dark and light themes with consistent styling.
"""

from typing import Optional, Dict
from enum import Enum, auto


class Theme(Enum):
    """Available themes."""
    DARK = auto()
    LIGHT = auto()
    SYSTEM = auto()


# Color palette - Material Design inspired
COLORS = {
    "dark": {
        "background": "#1e1e2e",
        "surface": "#2a2a3c",
        "surface_variant": "#363649",
        "primary": "#89b4fa",
        "primary_variant": "#74c7ec",
        "secondary": "#f5c2e7",
        "accent": "#a6e3a1",
        "error": "#f38ba8",
        "warning": "#fab387",
        "success": "#a6e3a1",
        "text": "#cdd6f4",
        "text_secondary": "#a6adc8",
        "text_disabled": "#6c7086",
        "border": "#45475a",
        "hover": "#313244",
        "selected": "#45475a",
        "scrollbar": "#585b70",
        "scrollbar_hover": "#6c7086",
    },
    "light": {
        "background": "#eff1f5",
        "surface": "#ffffff",
        "surface_variant": "#e6e9ef",
        "primary": "#1e66f5",
        "primary_variant": "#04a5e5",
        "secondary": "#ea76cb",
        "accent": "#40a02b",
        "error": "#d20f39",
        "warning": "#fe640b",
        "success": "#40a02b",
        "text": "#4c4f69",
        "text_secondary": "#6c6f85",
        "text_disabled": "#9ca0b0",
        "border": "#ccd0da",
        "hover": "#e6e9ef",
        "selected": "#dce0e8",
        "scrollbar": "#bcc0cc",
        "scrollbar_hover": "#acb0be",
    },
}


class StyleManager:
    """
    Manages application styles and themes.
    
    Provides:
    - Theme switching (dark/light/system)
    - Consistent color palette
    - Component-specific styles
    - QSS stylesheet generation
    """
    
    def __init__(self, theme: Theme = Theme.DARK):
        """
        Initialize the style manager.
        
        Args:
            theme: Initial theme
        """
        self._theme = theme
        self._colors = COLORS["dark"]
    
    @property
    def theme(self) -> Theme:
        """Get the current theme."""
        return self._theme
    
    @property
    def colors(self) -> Dict[str, str]:
        """Get the current color palette."""
        return self._colors
    
    def set_theme(self, theme: Theme) -> None:
        """
        Set the application theme.
        
        Args:
            theme: Theme to set
        """
        self._theme = theme
        
        if theme == Theme.SYSTEM:
            # Try to detect system theme
            try:
                import darkdetect
                is_dark = darkdetect.isDark()
                self._colors = COLORS["dark" if is_dark else "light"]
            except ImportError:
                self._colors = COLORS["dark"]
        else:
            self._colors = COLORS["dark" if theme == Theme.DARK else "light"]
    
    def get_color(self, name: str) -> str:
        """
        Get a color by name.
        
        Args:
            name: Color name
            
        Returns:
            Color hex code
        """
        return self._colors.get(name, "#ffffff")
    
    def get_stylesheet(self) -> str:
        """
        Get the complete QSS stylesheet.
        
        Returns:
            QSS stylesheet string
        """
        c = self._colors
        
        return f"""
/* Main Application */
QMainWindow, QDialog {{
    background-color: {c["background"]};
    color: {c["text"]};
}}

QWidget {{
    background-color: transparent;
    color: {c["text"]};
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}}

/* Menu Bar */
QMenuBar {{
    background-color: {c["surface"]};
    color: {c["text"]};
    border-bottom: 1px solid {c["border"]};
    padding: 4px;
}}

QMenuBar::item {{
    padding: 6px 12px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {c["hover"]};
}}

QMenu {{
    background-color: {c["surface"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
    padding: 8px 4px;
}}

QMenu::item {{
    padding: 8px 24px 8px 16px;
    border-radius: 4px;
    margin: 2px 4px;
}}

QMenu::item:selected {{
    background-color: {c["hover"]};
}}

QMenu::separator {{
    height: 1px;
    background-color: {c["border"]};
    margin: 6px 8px;
}}

/* Tool Bar */
QToolBar {{
    background-color: {c["surface"]};
    border: none;
    border-bottom: 1px solid {c["border"]};
    padding: 4px;
    spacing: 4px;
}}

QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 8px;
    margin: 2px;
}}

QToolButton:hover {{
    background-color: {c["hover"]};
}}

QToolButton:pressed {{
    background-color: {c["selected"]};
}}

QToolButton:checked {{
    background-color: {c["primary"]};
    color: {c["background"]};
}}

/* Status Bar */
QStatusBar {{
    background-color: {c["surface"]};
    color: {c["text_secondary"]};
    border-top: 1px solid {c["border"]};
}}

/* Scroll Areas */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: transparent;
    width: 12px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {c["scrollbar"]};
    min-height: 30px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {c["scrollbar_hover"]};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 12px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {c["scrollbar"]};
    min-width: 30px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {c["scrollbar_hover"]};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {{
    background: transparent;
    width: 0;
}}

/* Push Buttons */
QPushButton {{
    background-color: {c["surface_variant"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {c["hover"]};
    border-color: {c["primary"]};
}}

QPushButton:pressed {{
    background-color: {c["selected"]};
}}

QPushButton:disabled {{
    background-color: {c["surface"]};
    color: {c["text_disabled"]};
    border-color: {c["border"]};
}}

QPushButton[primary="true"] {{
    background-color: {c["primary"]};
    color: {c["background"]};
    border: none;
}}

QPushButton[primary="true"]:hover {{
    background-color: {c["primary_variant"]};
}}

QPushButton[danger="true"] {{
    background-color: {c["error"]};
    color: {c["background"]};
    border: none;
}}

/* Line Edit */
QLineEdit {{
    background-color: {c["surface"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: {c["primary"]};
}}

QLineEdit:focus {{
    border-color: {c["primary"]};
}}

QLineEdit:disabled {{
    background-color: {c["surface_variant"]};
    color: {c["text_disabled"]};
}}

/* Text Edit */
QTextEdit, QPlainTextEdit {{
    background-color: {c["surface"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
    border-radius: 6px;
    padding: 8px;
    selection-background-color: {c["primary"]};
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {c["primary"]};
}}

/* Combo Box */
QComboBox {{
    background-color: {c["surface"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 20px;
}}

QComboBox:hover {{
    border-color: {c["primary"]};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {c["text_secondary"]};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {c["surface"]};
    border: 1px solid {c["border"]};
    border-radius: 6px;
    selection-background-color: {c["hover"]};
}}

/* Spin Box */
QSpinBox, QDoubleSpinBox {{
    background-color: {c["surface"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
    border-radius: 6px;
    padding: 8px 12px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {c["primary"]};
}}

/* Check Box */
QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {c["border"]};
    border-radius: 4px;
    background-color: {c["surface"]};
}}

QCheckBox::indicator:checked {{
    background-color: {c["primary"]};
    border-color: {c["primary"]};
}}

QCheckBox::indicator:hover {{
    border-color: {c["primary"]};
}}

/* Radio Button */
QRadioButton {{
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {c["border"]};
    border-radius: 9px;
    background-color: {c["surface"]};
}}

QRadioButton::indicator:checked {{
    background-color: {c["primary"]};
    border-color: {c["primary"]};
}}

/* Group Box */
QGroupBox {{
    background-color: {c["surface"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
    margin-top: 16px;
    padding: 16px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    padding: 0 8px;
    color: {c["text"]};
}}

/* Tab Widget */
QTabWidget::pane {{
    background-color: {c["surface"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {c["surface_variant"]};
    color: {c["text_secondary"]};
    border: 1px solid {c["border"]};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 16px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {c["surface"]};
    color: {c["text"]};
    border-bottom: 2px solid {c["primary"]};
}}

QTabBar::tab:hover:!selected {{
    background-color: {c["hover"]};
}}

/* List Widget */
QListWidget, QListView {{
    background-color: {c["surface"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}

QListWidget::item, QListView::item {{
    padding: 10px 12px;
    border-radius: 6px;
    margin: 2px;
}}

QListWidget::item:selected, QListView::item:selected {{
    background-color: {c["selected"]};
    color: {c["text"]};
}}

QListWidget::item:hover:!selected, QListView::item:hover:!selected {{
    background-color: {c["hover"]};
}}

/* Tree Widget */
QTreeWidget, QTreeView {{
    background-color: {c["surface"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}

QTreeWidget::item, QTreeView::item {{
    padding: 8px 4px;
    border-radius: 4px;
}}

QTreeWidget::item:selected, QTreeView::item:selected {{
    background-color: {c["selected"]};
}}

QTreeWidget::item:hover:!selected, QTreeView::item:hover:!selected {{
    background-color: {c["hover"]};
}}

QTreeWidget::branch, QTreeView::branch {{
    background-color: transparent;
}}

/* Table Widget */
QTableWidget, QTableView {{
    background-color: {c["surface"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
    gridline-color: {c["border"]};
}}

QTableWidget::item, QTableView::item {{
    padding: 8px;
}}

QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {c["selected"]};
}}

QHeaderView::section {{
    background-color: {c["surface_variant"]};
    color: {c["text"]};
    border: none;
    border-bottom: 1px solid {c["border"]};
    border-right: 1px solid {c["border"]};
    padding: 10px;
    font-weight: 600;
}}

/* Progress Bar */
QProgressBar {{
    background-color: {c["surface_variant"]};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {c["primary"]};
    border-radius: 4px;
}}

/* Slider */
QSlider::groove:horizontal {{
    background-color: {c["surface_variant"]};
    height: 6px;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background-color: {c["primary"]};
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background-color: {c["primary_variant"]};
}}

/* Splitter */
QSplitter::handle {{
    background-color: {c["border"]};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:vertical {{
    height: 1px;
}}

/* Tool Tip */
QToolTip {{
    background-color: {c["surface"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
    border-radius: 6px;
    padding: 8px 12px;
}}

/* Dock Widget */
QDockWidget {{
    titlebar-close-icon: url(none);
    titlebar-normal-icon: url(none);
}}

QDockWidget::title {{
    background-color: {c["surface"]};
    color: {c["text"]};
    padding: 10px;
    border-bottom: 1px solid {c["border"]};
}}

/* Frame */
QFrame[frameShape="4"] {{ /* HLine */
    background-color: {c["border"]};
    max-height: 1px;
}}

QFrame[frameShape="5"] {{ /* VLine */
    background-color: {c["border"]};
    max-width: 1px;
}}

/* Labels */
QLabel {{
    color: {c["text"]};
}}

QLabel[heading="true"] {{
    font-size: 18px;
    font-weight: 600;
    color: {c["text"]};
}}

QLabel[subheading="true"] {{
    font-size: 14px;
    color: {c["text_secondary"]};
}}

QLabel[error="true"] {{
    color: {c["error"]};
}}

QLabel[success="true"] {{
    color: {c["success"]};
}}

QLabel[warning="true"] {{
    color: {c["warning"]};
}}

/* Message Box */
QMessageBox {{
    background-color: {c["surface"]};
}}

QMessageBox QLabel {{
    color: {c["text"]};
}}

/* File Dialog */
QFileDialog {{
    background-color: {c["background"]};
}}

/* Custom Classes */
.card {{
    background-color: {c["surface"]};
    border: 1px solid {c["border"]};
    border-radius: 12px;
    padding: 16px;
}}

.sidebar {{
    background-color: {c["surface"]};
    border-right: 1px solid {c["border"]};
}}

.toolbar-separator {{
    background-color: {c["border"]};
    width: 1px;
    margin: 8px 4px;
}}
"""
    
    def get_icon_color(self) -> str:
        """Get the appropriate icon color for the current theme."""
        return self._colors["text"]
    
    def get_accent_icon_color(self) -> str:
        """Get the accent color for icons."""
        return self._colors["primary"]
