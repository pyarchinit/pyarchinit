"""
PyArchInit Theme Manager
Provides centralized theme management for all PyArchInit forms.
Supports dark and light themes with uniform styling.
"""

from qgis.core import QgsSettings
from qgis.PyQt.QtWidgets import QPushButton, QToolButton, QWidget, QHBoxLayout
from qgis.PyQt.QtCore import Qt, QEvent
from qgis.PyQt.QtGui import QIcon
import os

# Dark theme stylesheet
DARK_THEME = """
/* Main window and dialogs */
QDialog, QMainWindow, QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    font-size: 12px;
}

/* Labels */
QLabel {
    color: #ffffff;
    font-size: 12px;
    padding: 2px;
}

/* Group boxes */
QGroupBox {
    color: #ffffff;
    font-size: 12px;
    font-weight: bold;
    border: 1px solid #555555;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #4da6ff;
}

/* Tab widgets */
QTabWidget::pane {
    border: 1px solid #555555;
    border-radius: 4px;
    background-color: #2b2b2b;
}

QTabBar::tab {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #555555;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 12px;
    margin-right: 2px;
    font-size: 12px;
}

QTabBar::tab:selected {
    background-color: #2b2b2b;
    color: #ffffff;
    border-bottom: 2px solid #4da6ff;
}

QTabBar::tab:hover:!selected {
    background-color: #454545;
}

/* Line edits and text edits */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    selection-background-color: #4da6ff;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #4da6ff;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #252525;
    color: #888888;
}

/* Combo boxes */
QComboBox {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    min-height: 20px;
}

QComboBox:hover {
    border: 1px solid #4da6ff;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #ffffff;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    selection-background-color: #4da6ff;
}

/* Spin boxes */
QSpinBox, QDoubleSpinBox {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #4da6ff;
}

/* Push buttons */
QPushButton {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 6px 16px;
    font-size: 12px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #4da6ff;
    border: 1px solid #4da6ff;
}

QPushButton:pressed {
    background-color: #3d8bd9;
}

QPushButton:disabled {
    background-color: #252525;
    color: #666666;
    border: 1px solid #404040;
}

/* Tool buttons */
QToolButton {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px;
}

QToolButton:hover {
    background-color: #4da6ff;
}

/* Check boxes and radio buttons */
QCheckBox, QRadioButton {
    color: #ffffff;
    font-size: 12px;
    spacing: 8px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {
    border: 1px solid #555555;
    background-color: #3c3c3c;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    border: 1px solid #4da6ff;
    background-color: #4da6ff;
    border-radius: 3px;
}

QRadioButton::indicator {
    border-radius: 8px;
}

QRadioButton::indicator:checked {
    border: 1px solid #4da6ff;
    background-color: #4da6ff;
}

/* Table widgets */
QTableWidget, QTableView {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    gridline-color: #404040;
    font-size: 12px;
}

QTableWidget::item, QTableView::item {
    padding: 4px;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #4da6ff;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #3c3c3c;
    color: #ffffff;
    padding: 6px;
    border: none;
    border-right: 1px solid #555555;
    border-bottom: 1px solid #555555;
    font-size: 12px;
    font-weight: bold;
}

/* List widgets */
QListWidget, QListView {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    font-size: 12px;
}

QListWidget::item:selected, QListView::item:selected {
    background-color: #4da6ff;
}

/* Scroll bars */
QScrollBar:vertical {
    background-color: #2b2b2b;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #555555;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #666666;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #2b2b2b;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #555555;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #666666;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Progress bar */
QProgressBar {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-size: 12px;
}

QProgressBar::chunk {
    background-color: #4da6ff;
    border-radius: 3px;
}

/* Menu */
QMenu {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    font-size: 12px;
}

QMenu::item:selected {
    background-color: #4da6ff;
}

/* Tooltips */
QToolTip {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px;
    font-size: 12px;
}

/* Splitter */
QSplitter::handle {
    background-color: #555555;
}

QSplitter::handle:hover {
    background-color: #4da6ff;
}

/* Frame */
QFrame {
    border-color: #555555;
}

/* Date/Time Edit */
QDateEdit, QTimeEdit, QDateTimeEdit {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}
"""

# Light theme stylesheet
LIGHT_THEME = """
/* Main window and dialogs */
QDialog, QMainWindow, QWidget {
    background-color: #f5f5f5;
    color: #333333;
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    font-size: 12px;
}

/* Labels */
QLabel {
    color: #333333;
    font-size: 12px;
    padding: 2px;
}

/* Group boxes */
QGroupBox {
    color: #333333;
    font-size: 12px;
    font-weight: bold;
    border: 1px solid #cccccc;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #0078d4;
}

/* Tab widgets */
QTabWidget::pane {
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #e8e8e8;
    color: #666666;
    border: 1px solid #cccccc;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 12px;
    margin-right: 2px;
    font-size: 12px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #333333;
    border-bottom: 2px solid #0078d4;
}

QTabBar::tab:hover:!selected {
    background-color: #d8d8d8;
}

/* Line edits and text edits */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #0078d4;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #f0f0f0;
    color: #999999;
}

/* Combo boxes */
QComboBox {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    min-height: 20px;
}

QComboBox:hover {
    border: 1px solid #0078d4;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #666666;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
}

/* Spin boxes */
QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #0078d4;
}

/* Push buttons */
QPushButton {
    background-color: #e8e8e8;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 6px 16px;
    font-size: 12px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #0078d4;
    color: #ffffff;
    border: 1px solid #0078d4;
}

QPushButton:pressed {
    background-color: #006cbd;
}

QPushButton:disabled {
    background-color: #f0f0f0;
    color: #999999;
    border: 1px solid #dddddd;
}

/* Tool buttons */
QToolButton {
    background-color: #e8e8e8;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px;
}

QToolButton:hover {
    background-color: #0078d4;
    color: #ffffff;
}

/* Check boxes and radio buttons */
QCheckBox, QRadioButton {
    color: #333333;
    font-size: 12px;
    spacing: 8px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {
    border: 1px solid #cccccc;
    background-color: #ffffff;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    border: 1px solid #0078d4;
    background-color: #0078d4;
    border-radius: 3px;
}

QRadioButton::indicator {
    border-radius: 8px;
}

QRadioButton::indicator:checked {
    border: 1px solid #0078d4;
    background-color: #0078d4;
}

/* Table widgets */
QTableWidget, QTableView {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 4px;
    gridline-color: #e0e0e0;
    font-size: 12px;
}

QTableWidget::item, QTableView::item {
    padding: 4px;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #0078d4;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #e8e8e8;
    color: #333333;
    padding: 6px;
    border: none;
    border-right: 1px solid #cccccc;
    border-bottom: 1px solid #cccccc;
    font-size: 12px;
    font-weight: bold;
}

/* List widgets */
QListWidget, QListView {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 4px;
    font-size: 12px;
}

QListWidget::item:selected, QListView::item:selected {
    background-color: #0078d4;
    color: #ffffff;
}

/* Scroll bars */
QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #cccccc;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #aaaaaa;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #f5f5f5;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #cccccc;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #aaaaaa;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Progress bar */
QProgressBar {
    background-color: #e8e8e8;
    border: 1px solid #cccccc;
    border-radius: 4px;
    text-align: center;
    color: #333333;
    font-size: 12px;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 3px;
}

/* Menu */
QMenu {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    font-size: 12px;
}

QMenu::item:selected {
    background-color: #0078d4;
    color: #ffffff;
}

/* Tooltips */
QToolTip {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px;
    font-size: 12px;
}

/* Splitter */
QSplitter::handle {
    background-color: #cccccc;
}

QSplitter::handle:hover {
    background-color: #0078d4;
}

/* Frame */
QFrame {
    border-color: #cccccc;
}

/* Date/Time Edit */
QDateEdit, QTimeEdit, QDateTimeEdit {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}
"""

# Settings key for theme preference
THEME_SETTING_KEY = "pyarchinit/ui_theme"


class ThemeManager:
    """Manages PyArchInit UI themes."""

    DARK = "dark"
    LIGHT = "light"

    _instance = None
    _current_theme = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize theme manager."""
        if self._current_theme is None:
            self._current_theme = self.get_saved_theme()

    @classmethod
    def get_saved_theme(cls) -> str:
        """Get the saved theme preference from settings."""
        settings = QgsSettings()
        return settings.value(THEME_SETTING_KEY, cls.DARK, type=str)

    @classmethod
    def save_theme(cls, theme: str):
        """Save theme preference to settings."""
        settings = QgsSettings()
        settings.setValue(THEME_SETTING_KEY, theme)
        cls._current_theme = theme

    @classmethod
    def get_current_theme(cls) -> str:
        """Get the current theme."""
        if cls._current_theme is None:
            cls._current_theme = cls.get_saved_theme()
        return cls._current_theme

    @classmethod
    def get_stylesheet(cls, theme: str = None) -> str:
        """Get stylesheet for the specified theme."""
        if theme is None:
            theme = cls.get_current_theme()

        if theme == cls.DARK:
            return DARK_THEME
        else:
            return LIGHT_THEME

    @classmethod
    def apply_theme(cls, widget, theme: str = None):
        """Apply theme to a widget and all its children."""
        if theme is None:
            theme = cls.get_current_theme()

        stylesheet = cls.get_stylesheet(theme)
        widget.setStyleSheet(stylesheet)

    @classmethod
    def toggle_theme(cls) -> str:
        """Toggle between dark and light themes."""
        current = cls.get_current_theme()
        new_theme = cls.LIGHT if current == cls.DARK else cls.DARK
        cls.save_theme(new_theme)
        return new_theme

    @classmethod
    def is_dark_theme(cls) -> bool:
        """Check if current theme is dark."""
        return cls.get_current_theme() == cls.DARK

    @classmethod
    def create_toggle_button(cls, parent_widget, button_type='tool'):
        """
        Create a theme toggle button.

        Args:
            parent_widget: The parent widget that owns this button
            button_type: 'tool' for QToolButton, 'push' for QPushButton

        Returns:
            The created button with toggle functionality
        """
        if button_type == 'tool':
            button = QToolButton(parent_widget)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        else:
            button = QPushButton(parent_widget)

        # Set initial appearance based on current theme
        cls._update_toggle_button_appearance(button)

        # Connect click to toggle function
        def on_toggle():
            cls.toggle_theme()
            cls._update_toggle_button_appearance(button)
            # Re-apply theme to parent widget
            cls.apply_theme(parent_widget)

        button.clicked.connect(on_toggle)

        return button

    @classmethod
    def _update_toggle_button_appearance(cls, button):
        """Update the toggle button's appearance based on current theme."""
        is_dark = cls.is_dark_theme()

        # Use text symbols for sun/moon icons
        if is_dark:
            button.setText("☀")  # Sun icon for switching to light
            button.setToolTip("Passa al tema chiaro / Switch to light theme")
        else:
            button.setText("🌙")  # Moon icon for switching to dark
            button.setToolTip("Passa al tema scuro / Switch to dark theme")

        # Style the button
        button_style = """
            QToolButton, QPushButton {
                font-size: 16px;
                padding: 4px 8px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: transparent;
            }
            QToolButton:hover, QPushButton:hover {
                background-color: rgba(77, 166, 255, 0.2);
            }
        """
        button.setStyleSheet(button_style)

    @classmethod
    def add_toggle_button_to_toolbar(cls, toolbar, parent_widget):
        """
        Add a theme toggle button to an existing toolbar.

        Args:
            toolbar: QToolBar to add the button to
            parent_widget: The parent widget to re-apply theme on toggle

        Returns:
            The created toggle button
        """
        button = cls.create_toggle_button(parent_widget, 'tool')
        toolbar.addWidget(button)
        return button

    @classmethod
    def add_theme_toggle_to_form(cls, form):
        """
        Add a theme toggle button to a form, positioned in the top-right corner.

        Args:
            form: The QDialog or QWidget to add the toggle button to

        Returns:
            The created toggle button
        """
        button = cls.create_toggle_button(form, 'tool')
        button.setFixedSize(28, 28)

        # Position the button in the top-right corner
        def reposition_button(event=None):
            # Position with some padding from the edges
            x = form.width() - button.width() - 10
            y = 10
            button.move(x, y)
            button.raise_()  # Ensure button is on top

        # Initial positioning
        reposition_button()

        # Re-position when form is resized
        original_resize_event = form.resizeEvent

        def new_resize_event(event):
            reposition_button()
            if original_resize_event:
                original_resize_event(event)

        form.resizeEvent = new_resize_event

        return button


def apply_theme_to_widget(widget, theme: str = None):
    """Convenience function to apply theme to a widget."""
    ThemeManager.apply_theme(widget, theme)


def get_current_stylesheet() -> str:
    """Convenience function to get current theme stylesheet."""
    return ThemeManager.get_stylesheet()


def toggle_theme() -> str:
    """Convenience function to toggle theme."""
    return ThemeManager.toggle_theme()


def is_dark_theme() -> bool:
    """Convenience function to check if dark theme is active."""
    return ThemeManager.is_dark_theme()
