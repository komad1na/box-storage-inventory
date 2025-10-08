"""
UI Styles and Themes
"""


class ModernStyle:
    """Modern theme styles with dark and light modes."""

    # Current theme (will be set dynamically)
    current_theme = "dark"

    # Dark theme colors
    DARK = {
        "BACKGROUND": "#1a1a1a",
        "SURFACE": "#262626",
        "PRIMARY": "#33b36b",
        "DANGER": "#e64d4d",
        "TEXT": "#ffffff",
        "TEXT_SECONDARY": "#b3b3b3",
        "BORDER": "#404040",
        "HEADER": "#222222",
        "TAB_SELECTED": "#3498db",
        "HOVER_PRIMARY": "#2da35f",
        "PRESSED_PRIMARY": "#258a50",
        "HOVER_DANGER": "#d63d3d",
        "HOVER_NEUTRAL": "#707070",
    }

    # Light theme colors - Professional light color palette
    LIGHT = {
        "BACKGROUND": "#f8f9fa",        # Soft off-white background
        "SURFACE": "#ffffff",           # Pure white for cards/tables
        "PRIMARY": "#28a745",           # Professional green
        "DANGER": "#dc3545",            # Bootstrap-style red
        "TEXT": "#212529",              # Near-black for text
        "TEXT_SECONDARY": "#6c757d",    # Medium gray for secondary text
        "BORDER": "#dee2e6",            # Light gray borders
        "HEADER": "#e9ecef",            # Slightly darker than background
        "TAB_SELECTED": "#0d6efd",      # Professional blue
        "HOVER_PRIMARY": "#218838",     # Darker green on hover
        "PRESSED_PRIMARY": "#1e7e34",   # Even darker when pressed
        "HOVER_DANGER": "#c82333",      # Darker red on hover
        "HOVER_NEUTRAL": "#5a6268",     # Dark gray on hover
    }

    # Backward compatibility - default to dark theme
    BACKGROUND = DARK["BACKGROUND"]
    SURFACE = DARK["SURFACE"]
    PRIMARY = DARK["PRIMARY"]
    DANGER = DARK["DANGER"]
    TEXT = DARK["TEXT"]
    TEXT_SECONDARY = DARK["TEXT_SECONDARY"]
    BORDER = DARK["BORDER"]

    @classmethod
    def set_theme(cls, theme_name):
        """Set the current theme (dark or light)."""
        cls.current_theme = theme_name
        theme = cls.DARK if theme_name == "dark" else cls.LIGHT
        cls.BACKGROUND = theme["BACKGROUND"]
        cls.SURFACE = theme["SURFACE"]
        cls.PRIMARY = theme["PRIMARY"]
        cls.DANGER = theme["DANGER"]
        cls.TEXT = theme["TEXT"]
        cls.TEXT_SECONDARY = theme["TEXT_SECONDARY"]
        cls.BORDER = theme["BORDER"]

    @classmethod
    def get_stylesheet(cls):
        return f"""
            QMainWindow, QDialog {{
                background-color: {ModernStyle.BACKGROUND};
                color: {ModernStyle.TEXT};
                font-family: Inter;
            }}

            QTabWidget::pane {{
                border: 1px solid {ModernStyle.BORDER};
                background-color: {ModernStyle.BACKGROUND};
                border-top-left-radius: 0px;
                border-top-right-radius: 8px;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                font-family: Inter;
            }}

            QTabBar::tab {{
                background-color: {ModernStyle.SURFACE};
                color: {ModernStyle.TEXT};
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }}

            QTabBar::tab:selected {{
                background-color: #3498db;
            }}

            QTableWidget {{
                background-color: {ModernStyle.BACKGROUND};
                alternate-background-color: {ModernStyle.SURFACE};
                color: {ModernStyle.TEXT};
                gridline-color: {ModernStyle.BORDER};
                font-family: Inter;
                font-size: 14px;
            }}

            QTableWidget::item {{
                padding-top: 8px;
                padding-bottom: 8px;
                border-right: 0px solid {ModernStyle.BORDER};
                border-bottom: 0px solid {ModernStyle.BORDER};
                border-left: none;
                border-top: none;
                outline: none;
            }}
            QTableWidget::item:last {{
                padding-top: 2px;
                padding-bottom: 2px;
            }}

            QTableWidget::item:selected {{
                background-color: #3498db;
                outline: none;
            }}

            QTableWidget::item:focus {{
                outline: none;
            }}

            QTableWidget:focus {{
                outline: none;
            }}

            QHeaderView::section {{
                background-color: {cls.DARK["HEADER"] if cls.current_theme == "dark" else cls.LIGHT["HEADER"]};
                color: {ModernStyle.TEXT};
                padding: 6px;
                border-right: 1px solid {ModernStyle.BORDER};
                border-bottom: 1px solid {ModernStyle.BORDER};
                border-left: none;
                border-top: none;
                font-weight: bold;
                font-size: 13px;
                font-family: Inter;
            }}

            QScrollBar:vertical, QScrollBar:horizontal {{
                width: 0px;
                height: 0px;
                background: transparent;
            }}

            QPushButton {{
                background-color: {ModernStyle.PRIMARY};
                color: {ModernStyle.TEXT};
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
                min-height: 24px;
                font-family: Inter;
            }}

            QPushButton:hover {{
                background-color: #2da35f;
            }}

            QPushButton:pressed {{
                background-color: #258a50;
            }}

            QPushButton.danger {{
                background-color: {ModernStyle.DANGER};
            }}

            QPushButton.danger:hover {{
                background-color: #d63d3d;
            }}

            QPushButton.neutral {{
                background-color: #808080;
            }}

            QPushButton.neutral:hover {{
                background-color: #707070;
            }}

            QLineEdit, QComboBox, QSpinBox {{
                background-color: {ModernStyle.SURFACE};
                color: {ModernStyle.TEXT};
                border: 1px solid {ModernStyle.BORDER};
                padding: 8px;
                border-radius: 8px;
                font-family: Inter;
            }}

            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border: 1px solid #3498db;
            }}

            QComboBox::drop-down {{
                border: none;
                width: 30px;
                background-color: {ModernStyle.SURFACE};
                border-radius: 8px;
            }}

            QComboBox::down-arrow {{
                width: 0;
                height: 0;
                margin-right: 10px;
                border-radius: 8px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {ModernStyle.SURFACE};
                color: {ModernStyle.TEXT};
                selection-background-color: #3498db;
                border: 1px solid {ModernStyle.BORDER};
            }}

            QLabel {{
                color: {ModernStyle.TEXT};
            }}
        """
