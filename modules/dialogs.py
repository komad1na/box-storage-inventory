"""
Dialog windows for the application
"""

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
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from .styles import ModernStyle


class EditItemDialog(QDialog):
    """Dialog for editing an item."""

    def __init__(self, parent, cursor, item_data=None):
        super().__init__(parent)
        self.cursor = cursor
        self.item_data = item_data
        self.setWindowTitle("Edit Item" if item_data else "Add New Item")
        self.setModal(True)
        self.setMinimumWidth(400)
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
        self.name_input.setPlaceholderText("Enter item name")
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

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "danger")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Update" if self.item_data else "Add")
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_boxes(self):
        """Load boxes into combobox."""
        self.cursor.execute("SELECT id, name FROM boxes ORDER BY name")
        boxes = self.cursor.fetchall()

        for box_id, name in boxes:
            self.box_combo.addItem(f"{box_id} - {name}", box_id)

    def save(self):
        """Save the item."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Item name cannot be empty")
            return

        box_id = self.box_combo.currentData()
        quantity = self.quantity_spin.value()

        self.result = (name, box_id, quantity)
        self.accept()


class ImportPreviewDialog(QDialog):
    """Dialog for previewing CSV import data before committing."""

    def __init__(self, parent, import_data, validation_errors):
        super().__init__(parent)
        self.import_data = import_data
        self.validation_errors = validation_errors
        self.setWindowTitle("CSV Import Preview")
        self.setModal(True)
        self.setMinimumSize(800, 600)
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
            error_text.setStyleSheet(f"background-color: {ModernStyle.SURFACE}; color: {ModernStyle.DANGER};")
            layout.addWidget(error_text)

        # Preview table
        preview_label = QLabel("Preview Data:")
        preview_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(preview_label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Row", "Item Name", "Box Name", "Quantity"])
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
            row_item = QTableWidgetItem(str(item.get('row', idx + 1)))
            row_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(idx, 0, row_item)

            # Item name
            name_item = QTableWidgetItem(item.get('name', ''))
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            if item.get('error'):
                name_item.setForeground(QColor(ModernStyle.DANGER))
            self.table.setItem(idx, 1, name_item)

            # Box name
            box_item = QTableWidgetItem(item.get('box_name', ''))
            box_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            if item.get('error'):
                box_item.setForeground(QColor(ModernStyle.DANGER))
            self.table.setItem(idx, 2, box_item)

            # Quantity
            qty_item = QTableWidgetItem(str(item.get('quantity', '')))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if item.get('error'):
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

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "danger")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # Only allow import if no errors
        if not self.validation_errors:
            import_btn = QPushButton(f"Import {len(self.import_data)} Items")
            import_btn.clicked.connect(self.accept)
            button_layout.addWidget(import_btn)
        else:
            error_btn = QPushButton("Fix Errors First")
            error_btn.setEnabled(False)
            error_btn.setProperty("class", "neutral")
            button_layout.addWidget(error_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)


class EditBoxDialog(QDialog):
    """Dialog for editing a box."""

    def __init__(self, parent, box_data=None):
        super().__init__(parent)
        self.box_data = box_data
        self.setWindowTitle("Edit Box" if box_data else "Add New Box")
        self.setModal(True)
        self.setMinimumWidth(400)
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
        self.name_input.setPlaceholderText("Enter box name")
        if self.box_data:
            self.name_input.setText(self.box_data[1])
        form_layout.addRow("Box Name:", self.name_input)

        layout.addLayout(form_layout)

        # Separator
        separator = QWidget()
        separator.setFixedHeight(2)
        separator.setStyleSheet(f"background-color: {ModernStyle.BORDER};")
        layout.addWidget(separator)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "danger")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Update" if self.box_data else "Add")
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save(self):
        """Save the box."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Box name cannot be empty")
            return

        self.result = name
        self.accept()
