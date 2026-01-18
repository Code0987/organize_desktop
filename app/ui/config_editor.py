"""
YAML configuration editor with syntax highlighting.
"""

from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QLabel,
    QFrame, QPushButton, QToolButton, QSizePolicy, QTextEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRegularExpression
from PyQt6.QtGui import (
    QFont, QFontMetrics, QSyntaxHighlighter, QTextDocument,
    QTextCharFormat, QColor, QPainter, QTextFormat,
)

from .styles import StyleManager


class YAMLHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for YAML content."""
    
    def __init__(self, document: QTextDocument, style_manager: StyleManager):
        """Initialize the highlighter."""
        super().__init__(document)
        self.style_manager = style_manager
        self._setup_rules()
    
    def _setup_rules(self) -> None:
        """Set up highlighting rules."""
        self.rules = []
        colors = self.style_manager.colors
        
        # Key format (before colon)
        key_format = QTextCharFormat()
        key_format.setForeground(QColor(colors["primary"]))
        key_format.setFontWeight(600)
        self.rules.append((QRegularExpression(r"^\s*[\w\-]+(?=\s*:)"), key_format))
        self.rules.append((QRegularExpression(r"^\s*\"[^\"]+\"(?=\s*:)"), key_format))
        self.rules.append((QRegularExpression(r"^\s*'[^']+'(?=\s*:)"), key_format))
        
        # String values (double quotes)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(colors["success"]))
        self.rules.append((QRegularExpression(r'"[^"]*"'), string_format))
        
        # String values (single quotes)
        self.rules.append((QRegularExpression(r"'[^']*'"), string_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(colors["warning"]))
        self.rules.append((QRegularExpression(r"\b\d+\.?\d*\b"), number_format))
        
        # Booleans
        bool_format = QTextCharFormat()
        bool_format.setForeground(QColor(colors["secondary"]))
        self.rules.append((QRegularExpression(r"\b(true|false|yes|no|null|~)\b", 
                                               QRegularExpression.PatternOption.CaseInsensitiveOption), 
                          bool_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(colors["text_disabled"]))
        comment_format.setFontItalic(True)
        self.rules.append((QRegularExpression(r"#.*$"), comment_format))
        
        # List markers
        list_format = QTextCharFormat()
        list_format.setForeground(QColor(colors["accent"]))
        self.rules.append((QRegularExpression(r"^\s*-\s"), list_format))
        
        # Anchors and aliases
        anchor_format = QTextCharFormat()
        anchor_format.setForeground(QColor(colors["secondary"]))
        self.rules.append((QRegularExpression(r"[&*]\w+"), anchor_format))
        
        # Template variables
        template_format = QTextCharFormat()
        template_format.setForeground(QColor(colors["primary_variant"]))
        self.rules.append((QRegularExpression(r"\{[^}]+\}"), template_format))
    
    def highlightBlock(self, text: str) -> None:
        """Apply highlighting to a block of text."""
        for pattern, format in self.rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class LineNumberArea(QWidget):
    """Widget for displaying line numbers."""
    
    def __init__(self, editor: "YAMLEditor"):
        """Initialize the line number area."""
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return self.editor.line_number_area_width()
    
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class YAMLEditor(QPlainTextEdit):
    """
    YAML text editor with line numbers and syntax highlighting.
    """
    
    def __init__(self, style_manager: StyleManager, parent: Optional[QWidget] = None):
        """Initialize the YAML editor."""
        super().__init__(parent)
        self.style_manager = style_manager
        
        # Set up font
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Tab settings
        metrics = QFontMetrics(font)
        # Use the width of a space since Qt6 deprecated averageCharWidth properly
        try:
            char_width = metrics.horizontalAdvance(' ')
        except AttributeError:
            char_width = metrics.averageCharWidth()
        self.setTabStopDistance(2 * char_width)
        
        # Line number area
        self.line_number_area = LineNumberArea(self)
        
        # Highlighter
        self.highlighter = YAMLHighlighter(self.document(), style_manager)
        
        # Signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        
        # Apply styling
        self._apply_style()
    
    def _apply_style(self) -> None:
        """Apply styling to the editor."""
        colors = self.style_manager.colors
        self.setStyleSheet(f"""
            YAMLEditor {{
                background-color: {colors["surface"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                border-radius: 6px;
            }}
        """)
    
    def line_number_area_width(self) -> int:
        """Calculate the width needed for line numbers."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        metrics = QFontMetrics(self.font())
        try:
            char_width = metrics.horizontalAdvance('9')
        except AttributeError:
            char_width = metrics.width('9')
        
        return 20 + char_width * digits
    
    def update_line_number_area_width(self, _) -> None:
        """Update the margin for line numbers."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy) -> None:
        """Update the line number area on scroll."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                          self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event) -> None:
        """Handle resize event."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(), cr.top(),
            self.line_number_area_width(), cr.height()
        )
    
    def highlight_current_line(self) -> None:
        """Highlight the current line."""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(self.style_manager.colors["selected"])
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def line_number_area_paint_event(self, event) -> None:
        """Paint the line numbers."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(self.style_manager.colors["surface_variant"]))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        painter.setPen(QColor(self.style_manager.colors["text_secondary"]))
        font = self.font()
        painter.setFont(font)
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 10, 
                    int(self.blockBoundingRect(block).height()),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    number
                )
            
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1
        
        painter.end()


class ConfigEditor(QWidget):
    """
    YAML configuration editor widget.
    Provides a code editor with syntax highlighting and validation.
    """
    
    content_changed = pyqtSignal(str)  # Emits the new content
    
    def __init__(self, style_manager: StyleManager, parent: Optional[QWidget] = None):
        """Initialize the config editor."""
        super().__init__(parent)
        self.style_manager = style_manager
        
        self._setup_ui()
        self._setup_validation_timer()
    
    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Editor
        self.editor = YAMLEditor(self.style_manager)
        self.editor.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.editor)
        
        # Status bar
        status_bar = QFrame()
        status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {self.style_manager.colors["surface"]};
                border-top: 1px solid {self.style_manager.colors["border"]};
            }}
        """)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(12, 6, 12, 6)
        
        # Validation status
        self.validation_icon = QLabel("✓")
        self.validation_icon.setStyleSheet(f"color: {self.style_manager.colors['success']};")
        status_layout.addWidget(self.validation_icon)
        
        self.validation_label = QLabel("Valid YAML")
        self.validation_label.setStyleSheet(f"color: {self.style_manager.colors['text_secondary']};")
        status_layout.addWidget(self.validation_label)
        
        status_layout.addStretch()
        
        # Cursor position
        self.cursor_label = QLabel("Line 1, Col 1")
        self.cursor_label.setStyleSheet(f"color: {self.style_manager.colors['text_secondary']};")
        status_layout.addWidget(self.cursor_label)
        
        self.editor.cursorPositionChanged.connect(self._update_cursor_position)
        
        layout.addWidget(status_bar)
    
    def _setup_validation_timer(self) -> None:
        """Set up the validation debounce timer."""
        self._validation_timer = QTimer()
        self._validation_timer.setSingleShot(True)
        self._validation_timer.timeout.connect(self._validate)
    
    def set_content(self, content: str) -> None:
        """Set the editor content."""
        self.editor.setPlainText(content)
        self._validate()
    
    def get_content(self) -> str:
        """Get the editor content."""
        return self.editor.toPlainText()
    
    def undo(self) -> None:
        """Undo the last edit."""
        self.editor.undo()
    
    def redo(self) -> None:
        """Redo the last undone edit."""
        self.editor.redo()
    
    def refresh_style(self, style_manager: StyleManager) -> None:
        """Refresh styles after theme change."""
        self.style_manager = style_manager
        
        # Update editor style
        self.editor.style_manager = style_manager
        self.editor._apply_style()
        self.editor.highlighter.style_manager = style_manager
        self.editor.highlighter._setup_rules()
        self.editor.highlighter.rehighlight()
        
        # Update line number area
        self.editor.line_number_area.update()
        
        # Find and update status bar
        for child in self.children():
            if isinstance(child, QFrame):
                child.setStyleSheet(f"""
                    QFrame {{
                        background-color: {style_manager.colors["surface"]};
                        border-top: 1px solid {style_manager.colors["border"]};
                    }}
                """)
        
        # Update cursor label
        self.cursor_label.setStyleSheet(f"color: {style_manager.colors['text_secondary']};")
        
        # Update validation labels
        self._validate()
    
    def _on_text_changed(self) -> None:
        """Handle text change."""
        # Debounce validation
        self._validation_timer.start(500)
        
        # Emit change signal
        self.content_changed.emit(self.get_content())
    
    def _validate(self) -> None:
        """Validate the YAML content."""
        import yaml
        
        content = self.get_content()
        
        try:
            yaml.safe_load(content)
            self.validation_icon.setText("✓")
            self.validation_icon.setStyleSheet(f"color: {self.style_manager.colors['success']};")
            self.validation_label.setText("Valid YAML")
            self.validation_label.setStyleSheet(f"color: {self.style_manager.colors['text_secondary']};")
        except yaml.YAMLError as e:
            self.validation_icon.setText("✗")
            self.validation_icon.setStyleSheet(f"color: {self.style_manager.colors['error']};")
            
            # Get error position
            if hasattr(e, 'problem_mark') and e.problem_mark:
                line = e.problem_mark.line + 1
                col = e.problem_mark.column + 1
                self.validation_label.setText(f"Error at line {line}, col {col}: {e.problem}")
            else:
                self.validation_label.setText(f"YAML Error: {e}")
            
            self.validation_label.setStyleSheet(f"color: {self.style_manager.colors['error']};")
    
    def _update_cursor_position(self) -> None:
        """Update the cursor position display."""
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_label.setText(f"Line {line}, Col {col}")
