"""
Dialog windows for the application
"""

import logging
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QTextEdit,
    QWidget,
    QTabWidget,
    QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from .styles import ModernStyle
from . import get_translator


class EditItemDialog(QDialog):
    """Dialog for editing an item."""

    def __init__(self, parent, cursor, item_data=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.cursor = cursor
        self.item_data = item_data
        dialog_type = "Edit Item" if item_data else "Add New Item"
        self.setWindowTitle(dialog_type)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.translator = get_translator()

        if item_data:
            self.logger.info(
                f"Opened Edit Item dialog for item ID: {item_data[0]}, Name: {item_data[1]}"
            )
        else:
            self.logger.info("Opened Add New Item dialog")

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Edit Item" if self.item_data else "Add New Item")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Form
        form_layout = QFormLayout()

        # Item name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(self.translator.tr("placeholder_item_name"))
        if self.item_data:
            self.name_input.setText(self.item_data[1])
        form_layout.addRow("Item Name:", self.name_input)

        # Box selection
        self.box_combo = QComboBox()
        self.load_boxes()
        if self.item_data and self.item_data[4]:
            # Find and select current box
            for i in range(self.box_combo.count()):
                if self.box_combo.itemData(i) == self.item_data[4]:
                    self.box_combo.setCurrentIndex(i)
                    break
        form_layout.addRow("Box:", self.box_combo)

        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(99999)
        if self.item_data:
            self.quantity_spin.setValue(self.item_data[3])
        else:
            self.quantity_spin.setValue(1)
        form_layout.addRow("Quantity:", self.quantity_spin)

        layout.addLayout(form_layout)

        # Separator
        separator = QWidget()
        separator.setFixedHeight(2)
        separator.setStyleSheet(f"background-color: {ModernStyle.BORDER};")
        layout.addWidget(separator)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton(self.translator.tr("btn_cancel"))
        cancel_btn.setProperty("class", "danger")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton(
            self.translator.tr("btn_update")
            if self.item_data
            else self.translator.tr("btn_add")
        )
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_boxes(self):
        """Load boxes into combobox."""
        self.cursor.execute("SELECT id, name FROM boxes ORDER BY name")
        boxes = self.cursor.fetchall()

        # Get the last added box (highest ID)
        self.cursor.execute("SELECT MAX(id) FROM boxes")
        last_box_id = self.cursor.fetchone()[0]

        for box_id, name in boxes:
            self.box_combo.addItem(f"{box_id} - {name}", box_id)

        # Set default to last added box if adding new item
        if not self.item_data and last_box_id:
            for i in range(self.box_combo.count()):
                if self.box_combo.itemData(i) == last_box_id:
                    self.box_combo.setCurrentIndex(i)
                    break

    def save(self):
        """Save the item."""
        name = self.name_input.text().strip()
        if not name:
            self.logger.warning("Item save cancelled: name is empty")
            QMessageBox.warning(
                self,
                self.translator.tr("msg_error"),
                self.translator.tr("msg_item_name_empty"),
            )
            return

        box_id = self.box_combo.currentData()
        if not box_id:
            self.logger.warning("Item save cancelled: no box selected")
            QMessageBox.warning(
                self,
                self.translator.tr("msg_error"),
                self.translator.tr("msg_select_box"),
            )
            return

        quantity = self.quantity_spin.value()
        if quantity < 1:
            self.logger.warning(f"Item save cancelled: invalid quantity {quantity}")
            QMessageBox.warning(
                self,
                self.translator.tr("msg_error"),
                self.translator.tr("msg_quantity_min"),
            )
            return

        # Validate name length
        if len(name) > 255:
            self.logger.warning(
                f"Item save cancelled: name too long ({len(name)} characters)"
            )
            QMessageBox.warning(
                self,
                self.translator.tr("msg_error"),
                self.translator.tr("msg_item_name_too_long"),
            )
            return

        self.logger.info(
            f"Item dialog saved: name='{name}', box_id={box_id}, quantity={quantity}"
        )
        self.result = (name, box_id, quantity)
        self.accept()
        self.logger.info("Item dialog closed (accepted)")


class ImportPreviewDialog(QDialog):
    """Dialog for previewing CSV import data before committing."""

    def __init__(self, parent, import_data, validation_errors):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.translator = get_translator()
        self.import_data = import_data
        self.validation_errors = validation_errors
        self.setWindowTitle("CSV Import Preview")
        self.setModal(True)
        self.setMinimumSize(800, 600)

        self.logger.info(
            f"Opened CSV Import Preview dialog: {len(import_data)} items, {len(validation_errors)} errors"
        )

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Import Preview")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Summary
        summary = QLabel(
            f"Found {len(self.import_data)} items to import. "
            f"{'⚠️ ' + str(len(self.validation_errors)) + ' validation errors found!' if self.validation_errors else '✓ All validations passed!'}"
        )
        summary.setStyleSheet(
            f"color: {ModernStyle.DANGER if self.validation_errors else ModernStyle.PRIMARY}; "
            "font-size: 14px; font-weight: bold; padding: 10px;"
        )
        layout.addWidget(summary)

        # Validation errors section
        if self.validation_errors:
            error_label = QLabel("Validation Errors:")
            error_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            error_label.setStyleSheet(f"color: {ModernStyle.DANGER};")
            layout.addWidget(error_label)

            error_text = QTextEdit()
            error_text.setReadOnly(True)
            error_text.setMaximumHeight(150)
            error_text.setPlainText("\n".join(self.validation_errors))
            error_text.setStyleSheet(
                f"background-color: {ModernStyle.SURFACE}; color: {ModernStyle.DANGER};"
            )
            layout.addWidget(error_text)

        # Preview table
        preview_label = QLabel("Preview Data:")
        preview_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(preview_label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            [
                self.translator.tr("header_row"),
                self.translator.tr("header_item_name"),
                self.translator.tr("header_box_name"),
                self.translator.tr("header_quantity"),
            ]
        )
        self.table.setRowCount(len(self.import_data))

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(3, 100)

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        for idx, item in enumerate(self.import_data):
            # Row number
            row_item = QTableWidgetItem(str(item.get("row", idx + 1)))
            row_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(idx, 0, row_item)

            # Item name
            name_item = QTableWidgetItem(item.get("name", ""))
            name_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            if item.get("error"):
                name_item.setForeground(QColor(ModernStyle.DANGER))
            self.table.setItem(idx, 1, name_item)

            # Box name
            box_item = QTableWidgetItem(item.get("box_name", ""))
            box_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            if item.get("error"):
                box_item.setForeground(QColor(ModernStyle.DANGER))
            self.table.setItem(idx, 2, box_item)

            # Quantity
            qty_item = QTableWidgetItem(str(item.get("quantity", "")))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if item.get("error"):
                qty_item.setForeground(QColor(ModernStyle.DANGER))
            self.table.setItem(idx, 3, qty_item)

        layout.addWidget(self.table)

        # Separator
        separator = QWidget()
        separator.setFixedHeight(2)
        separator.setStyleSheet(f"background-color: {ModernStyle.BORDER};")
        layout.addWidget(separator)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton(self.translator.tr("btn_cancel"))
        cancel_btn.setProperty("class", "danger")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # Only allow import if no errors
        if not self.validation_errors:
            import_btn = QPushButton(
                f"{self.translator.tr('btn_import')} {len(self.import_data)} {self.translator.tr('tab_items')}"
            )
            import_btn.clicked.connect(self.accept)
            button_layout.addWidget(import_btn)
        else:
            error_btn = QPushButton(self.translator.tr("btn_fix_errors"))
            error_btn.setEnabled(False)
            error_btn.setProperty("class", "neutral")
            button_layout.addWidget(error_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)


class EditBoxDialog(QDialog):
    """Dialog for editing a box."""

    def __init__(self, parent, box_data=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.box_data = box_data
        dialog_type = "Edit Box" if box_data else "Add New Box"
        self.setWindowTitle(dialog_type)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.translator = get_translator()

        if box_data:
            self.logger.info(
                f"Opened Edit Box dialog for box ID: {box_data[0]}, Name: {box_data[1]}"
            )
        else:
            self.logger.info("Opened Add New Box dialog")

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Edit Box" if self.box_data else "Add New Box")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Form
        form_layout = QFormLayout()

        # Box name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(self.translator.tr("placeholder_box_name"))
        if self.box_data:
            self.name_input.setText(self.box_data[1])
        form_layout.addRow("Box Name:", self.name_input)

        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText(
            self.translator.tr("placeholder_location")
        )
        if self.box_data and len(self.box_data) > 2:
            self.location_input.setText(self.box_data[2] or "")
        form_layout.addRow("Location:", self.location_input)

        layout.addLayout(form_layout)

        # Separator
        separator = QWidget()
        separator.setFixedHeight(2)
        separator.setStyleSheet(f"background-color: {ModernStyle.BORDER};")
        layout.addWidget(separator)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton(self.translator.tr("btn_cancel"))
        cancel_btn.setProperty("class", "danger")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton(
            self.translator.tr("btn_update")
            if self.box_data
            else self.translator.tr("btn_add")
        )
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save(self):
        """Save the box."""
        name = self.name_input.text().strip()
        if not name:
            self.logger.warning("Box save cancelled: name is empty")
            QMessageBox.warning(
                self,
                self.translator.tr("msg_error"),
                self.translator.tr("msg_box_name_empty"),
            )
            return

        # Validate name length
        if len(name) > 255:
            self.logger.warning(
                f"Box save cancelled: name too long ({len(name)} characters)"
            )
            QMessageBox.warning(
                self,
                self.translator.tr("msg_error"),
                self.translator.tr("msg_box_name_too_long"),
            )
            return

        location = self.location_input.text().strip()

        # Validate location length
        if location and len(location) > 255:
            self.logger.warning(
                f"Box save cancelled: location too long ({len(location)} characters)"
            )
            QMessageBox.warning(
                self,
                self.translator.tr("msg_error"),
                self.translator.tr("msg_location_too_long"),
            )
            return

        self.logger.info(f"Box dialog saved: name='{name}', location='{location}'")
        self.result = (name, location)
        self.accept()
        self.logger.info("Box dialog closed (accepted)")


class HelpDialog(QDialog):
    """Help dialog that displays markdown-formatted help content."""

    def __init__(self, parent):
        super().__init__(parent)
        self.translator = get_translator()
        self.setWindowTitle("Help - Inventory Manager")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {ModernStyle.BACKGROUND};
                padding: 10px;
            }}
        """
        )
        self.setup_ui()

    def setup_ui(self):
        """Setup the help dialog UI with markdown content."""
        import os
        import markdown2

        layout = QVBoxLayout()

        # Text browser for markdown content
        text_browser = QTextEdit()
        text_browser.setReadOnly(True)

        # Load markdown file based on current language
        lang = self.translator.current_language
        help_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "help", f"help_{lang}.md"
        )

        # Fallback to English if language file doesn't exist
        if not os.path.exists(help_file):
            help_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "help", "help_en.md"
            )

        try:
            with open(help_file, "r", encoding="utf-8") as f:
                markdown_content = f.read()
                html_content = markdown2.markdown(
                    markdown_content, extras=["tables", "fenced-code-blocks"]
                )

                # Apply styling based on theme
                from .styles import ModernStyle

                styled_html = f"""
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        color: {ModernStyle.TEXT};
                        background-color: {ModernStyle.BACKGROUND};
                        padding: 20px;
                    }}
                    h1 {{
                        color: {ModernStyle.PRIMARY};
                        border-bottom: 2px solid {ModernStyle.PRIMARY};
                        padding-bottom: 10px;
                    }}
                    h2 {{
                        color: {ModernStyle.PRIMARY};
                        margin-top: 20px;
                    }}
                    h3 {{
                        color: {ModernStyle.TEXT};
                        margin-top: 15px;
                    }}
                    code {{
                        background-color: {ModernStyle.SURFACE};
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-family: 'Consolas', 'Courier New', monospace;
                    }}
                    pre {{
                        background-color: {ModernStyle.SURFACE};
                        padding: 10px;
                        border-radius: 5px;
                        border: 1px solid {ModernStyle.BORDER};
                        overflow-x: auto;
                    }}
                    ul, ol {{
                        line-height: 1.6;
                    }}
                    hr {{
                        border: none;
                        border-top: 1px solid {ModernStyle.BORDER};
                        margin: 20px 0;
                    }}
                    strong {{
                        color: {ModernStyle.PRIMARY};
                    }}
                </style>
                {html_content}
                """
                text_browser.setHtml(styled_html)
        except Exception as e:
            text_browser.setPlainText(f"Error loading help file: {e}")

        layout.addWidget(text_browser)

        # Close button
        close_btn = QPushButton(self.translator.tr("btn_close"))
        close_btn.clicked.connect(self.accept)
        close_btn.setMaximumWidth(100)
        close_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: red;
            }}
        """
        )
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
