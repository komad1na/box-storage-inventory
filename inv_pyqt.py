import sys
import sqlite3
import os
import shutil
import csv
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLineEdit,
    QLabel,
    QDialog,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QMessageBox,
    QTabWidget,
    QHeaderView,
    QAbstractItemView,
    QFileDialog,
    QTextEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QFont, QAction


class ModernStyle:
    """Modern dark theme styles."""

    BACKGROUND = "#1a1a1a"
    SURFACE = "#262626"
    PRIMARY = "#33b36b"
    DANGER = "#e64d4d"
    TEXT = "#ffffff"
    TEXT_SECONDARY = "#b3b3b3"
    BORDER = "#404040"

    @staticmethod
    def get_stylesheet():
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
                border: 1px solid {ModernStyle.BORDER};
                font-family: Inter;
                font-size: 14px;
            }}

            QTableWidget::item {{
                padding-top: 10px;
                padding-bottom: 10px;
                
                outline: none;
            }}
            QTableWidget::item:last {{
                padding-top: 2px;
                padding-bottom: 2px;
                border: 0px;
            }}

            QTableWidget::item:selected {{
                background-color: #3498db;
                outline: none;
                border: 0px;
            }}

            QTableWidget::item:focus {{
                outline: none;
                border: 1px solid {ModernStyle.BORDER};
            }}

            QTableWidget:focus {{
                outline: none;
            }}

            QHeaderView::section {{
                background-color: #222222;
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


class ItemsTab(QWidget):
    """Tab for managing items."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        # Search and filter bar
        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.textChanged.connect(self.load_items)
        filter_layout.addWidget(self.search_input, 2)

        self.box_filter = QComboBox()
        self.box_filter.addItem("All Boxes", None)
        self.load_box_filter()
        self.box_filter.currentIndexChanged.connect(self.load_items)
        filter_layout.addWidget(self.box_filter, 2)

        clear_btn = QPushButton("Clear Filters")
        clear_btn.setProperty("class", "neutral")
        clear_btn.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_btn, 1)

        add_btn = QPushButton("+ Add Item")
        add_btn.clicked.connect(self.add_item)
        filter_layout.addWidget(add_btn, 1)

        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels(
            ["ID", "Item Name", "Box", "Quantity", "Actions"]
        )

        # Set column widths
        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )  # Item Name stretches
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Box stretches
        self.table.setColumnWidth(0, 50)  # ID column narrow
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(3, 80)  # Quantity column
        self.table.setColumnWidth(4, 200)  # Actions column

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)  # Hide row numbers
        self.table.verticalHeader().setDefaultSectionSize(50)  # Fixed row height

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_items()

    def load_box_filter(self):
        """Load boxes into filter dropdown."""
        self.parent.cursor.execute("SELECT id, name FROM boxes ORDER BY name")
        boxes = self.parent.cursor.fetchall()

        for box_id, name in boxes:
            self.box_filter.addItem(name, box_id)

    def load_items(self):
        """Load items into table."""
        self.table.setRowCount(0)

        query = """
            SELECT items.id, items.name, boxes.name, items.quantity, items.box_id
            FROM items
            LEFT JOIN boxes ON items.box_id = boxes.id
            WHERE 1=1
        """
        params = []

        # Apply filters
        search_text = self.search_input.text().strip()
        if search_text:
            query += " AND items.name LIKE ?"
            params.append(f"%{search_text}%")

        box_id = self.box_filter.currentData()
        if box_id:
            query += " AND items.box_id = ?"
            params.append(box_id)

        query += " ORDER BY items.id"

        self.parent.cursor.execute(query, params)
        items = self.parent.cursor.fetchall()

        for row_idx, (item_id, name, box_name, quantity, box_id) in enumerate(items):
            self.table.insertRow(row_idx)

            # ID
            id_item = QTableWidgetItem(str(item_id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, id_item)

            # Name
            name_item = QTableWidgetItem(name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 1, name_item)

            # Box
            box_item = QTableWidgetItem(box_name or "N/A")
            box_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 2, box_item)

            # Quantity
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, qty_item)

            # Actions
            actions_widget = QWidget()
            actions_widget.setStyleSheet("QWidget { background: transparent; border: none; }")
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(45, 22)
            edit_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {ModernStyle.PRIMARY};
                    color: {ModernStyle.TEXT};
                    border: none;
                    padding: 1px;
                    border-radius: 4px;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: #2da35f;
                }}
            """
            )
            edit_btn.clicked.connect(
                lambda checked, i=item_id, n=name, q=quantity, b=box_id: self.edit_item(
                    i, n, q, b
                )
            )
            actions_layout.addWidget(edit_btn)

            delete_btn = QPushButton("Del")
            delete_btn.setFixedSize(45, 22)
            delete_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {ModernStyle.DANGER};
                    color: {ModernStyle.TEXT};
                    border: none;
                    padding: 1px;
                    border-radius: 4px;
                    height: 10px;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: #d63d3d;
                }}
            """
            )
            delete_btn.clicked.connect(lambda checked, i=item_id: self.delete_item(i))
            actions_layout.addWidget(delete_btn)

            self.table.setCellWidget(row_idx, 4, actions_widget)

    def clear_filters(self):
        """Clear all filters."""
        self.search_input.clear()
        self.box_filter.setCurrentIndex(0)

    def add_item(self):
        """Show add item dialog."""
        if self.box_filter.count() <= 1:
            QMessageBox.warning(
                self, "Error", "No boxes available. Please create a box first."
            )
            return

        dialog = EditItemDialog(self, self.parent.cursor)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, box_id, quantity = dialog.result
            try:
                self.parent.cursor.execute(
                    "INSERT INTO items (name, box_id, quantity) VALUES (?, ?, ?)",
                    (name, box_id, quantity),
                )
                item_id = self.parent.cursor.lastrowid
                self.parent.conn.commit()

                # Get box name for logging
                self.parent.cursor.execute(
                    "SELECT name FROM boxes WHERE id = ?", (box_id,)
                )
                box_name = self.parent.cursor.fetchone()[0]

                # Log the action
                self.parent.log_action(
                    action="CREATE",
                    entity_type="ITEM",
                    entity_id=item_id,
                    entity_name=name,
                    details=f"Added {quantity} units to box '{box_name}'",
                )

                QMessageBox.information(self, "Success", "Item added successfully")
                self.load_items()
                self.load_box_filter()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")

    def edit_item(self, item_id, name, quantity, box_id):
        """Show edit item dialog."""
        item_data = (item_id, name, None, quantity, box_id)
        old_values = {"name": name, "quantity": quantity, "box_id": box_id}

        dialog = EditItemDialog(self, self.parent.cursor, item_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name, new_box_id, new_quantity = dialog.result
            try:
                self.parent.cursor.execute(
                    "UPDATE items SET name = ?, box_id = ?, quantity = ? WHERE id = ?",
                    (new_name, new_box_id, new_quantity, item_id),
                )
                self.parent.conn.commit()

                # Get box names for logging
                self.parent.cursor.execute(
                    "SELECT name FROM boxes WHERE id = ?", (new_box_id,)
                )
                new_box_name = self.parent.cursor.fetchone()[0]

                # Build change details
                changes = []
                if old_values["name"] != new_name:
                    changes.append(f"name: '{old_values['name']}' → '{new_name}'")
                if old_values["quantity"] != new_quantity:
                    changes.append(
                        f"quantity: {old_values['quantity']} → {new_quantity}"
                    )
                if old_values["box_id"] != new_box_id:
                    self.parent.cursor.execute(
                        "SELECT name FROM boxes WHERE id = ?", (old_values["box_id"],)
                    )
                    old_box_name = self.parent.cursor.fetchone()[0]
                    changes.append(f"box: '{old_box_name}' → '{new_box_name}'")

                # Log the action
                self.parent.log_action(
                    action="UPDATE",
                    entity_type="ITEM",
                    entity_id=item_id,
                    entity_name=new_name,
                    details=", ".join(changes) if changes else "No changes",
                    old_value=str(old_values),
                    new_value=f"{{'name': '{new_name}', 'quantity': {new_quantity}, 'box_id': {new_box_id}}}",
                )

                QMessageBox.information(self, "Success", "Item updated successfully")
                self.load_items()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")

    def delete_item(self, item_id):
        """Delete an item."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this item?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Get item details before deletion for logging
                self.parent.cursor.execute(
                    """SELECT items.name, items.quantity, boxes.name
                       FROM items
                       LEFT JOIN boxes ON items.box_id = boxes.id
                       WHERE items.id = ?""",
                    (item_id,),
                )
                item_data = self.parent.cursor.fetchone()
                item_name, quantity, box_name = (
                    item_data if item_data else ("Unknown", 0, "Unknown")
                )

                self.parent.cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
                self.parent.conn.commit()

                # Log the action
                self.parent.log_action(
                    action="DELETE",
                    entity_type="ITEM",
                    entity_id=item_id,
                    entity_name=item_name,
                    details=f"Deleted {quantity} units from box '{box_name}'",
                )

                QMessageBox.information(self, "Success", "Item deleted successfully")
                self.load_items()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")


class BoxesTab(QWidget):
    """Tab for managing boxes."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        # Search bar
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search boxes...")
        self.search_input.textChanged.connect(self.load_boxes)
        search_layout.addWidget(self.search_input, 4)

        clear_btn = QPushButton("Clear Search")
        clear_btn.setProperty("class", "neutral")
        clear_btn.clicked.connect(self.search_input.clear)
        search_layout.addWidget(clear_btn, 1)

        add_btn = QPushButton("+ Add Box")
        add_btn.clicked.connect(self.add_box)
        search_layout.addWidget(add_btn, 1)

        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Box Name", "Actions"])

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )  # Box Name stretches
        self.table.setColumnWidth(0, 50)  # ID column narrow
        self.table.setColumnWidth(2, 200)  # Actions column

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)  # Hide row numbers
        self.table.verticalHeader().setDefaultSectionSize(50)  # Fixed row height

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_boxes()

    def load_boxes(self):
        """Load boxes into table."""
        self.table.setRowCount(0)

        query = "SELECT id, name FROM boxes WHERE 1=1"
        params = []

        search_text = self.search_input.text().strip()
        if search_text:
            query += " AND name LIKE ?"
            params.append(f"%{search_text}%")

        query += " ORDER BY id"

        self.parent.cursor.execute(query, params)
        boxes = self.parent.cursor.fetchall()

        for row_idx, (box_id, name) in enumerate(boxes):
            self.table.insertRow(row_idx)

            # ID
            id_item = QTableWidgetItem(str(box_id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, id_item)

            # Name
            name_item = QTableWidgetItem(name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 1, name_item)

            # Actions
            actions_widget = QWidget()
            actions_widget.setStyleSheet("QWidget { background: transparent; border: none; }")
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(45, 22)
            edit_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {ModernStyle.PRIMARY};
                    color: {ModernStyle.TEXT};
                    border: none;
                    padding: 1px;
                    border-radius: 4px;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: #2da35f;
                }}
            """
            )
            edit_btn.clicked.connect(
                lambda checked, i=box_id, n=name: self.edit_box(i, n)
            )
            actions_layout.addWidget(edit_btn)

            delete_btn = QPushButton("Del")
            delete_btn.setFixedSize(45, 22)
            delete_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {ModernStyle.DANGER};
                    color: {ModernStyle.TEXT};
                    border: none;
                    padding: 1px;
                    border-radius: 4px;
                    height: 10px;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: #d63d3d;
                }}
            """
            )
            delete_btn.clicked.connect(lambda checked, i=box_id: self.delete_box(i))
            actions_layout.addWidget(delete_btn)

            self.table.setCellWidget(row_idx, 2, actions_widget)

    def add_box(self):
        """Show add box dialog."""
        dialog = EditBoxDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.result
            try:
                self.parent.cursor.execute(
                    "INSERT INTO boxes (name) VALUES (?)", (name,)
                )
                box_id = self.parent.cursor.lastrowid
                self.parent.conn.commit()

                # Log the action
                self.parent.log_action(
                    action="CREATE",
                    entity_type="BOX",
                    entity_id=box_id,
                    entity_name=name,
                    details="Created new box",
                )

                QMessageBox.information(self, "Success", "Box added successfully")
                self.load_boxes()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")

    def edit_box(self, box_id, name):
        """Show edit box dialog."""
        box_data = (box_id, name)
        old_name = name

        dialog = EditBoxDialog(self, box_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.result
            try:
                self.parent.cursor.execute(
                    "UPDATE boxes SET name = ? WHERE id = ?", (new_name, box_id)
                )
                self.parent.conn.commit()

                # Log the action
                changes = (
                    f"name: '{old_name}' → '{new_name}'"
                    if old_name != new_name
                    else "No changes"
                )
                self.parent.log_action(
                    action="UPDATE",
                    entity_type="BOX",
                    entity_id=box_id,
                    entity_name=new_name,
                    details=changes,
                    old_value=old_name,
                    new_value=new_name,
                )

                QMessageBox.information(self, "Success", "Box updated successfully")
                self.load_boxes()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")

    def delete_box(self, box_id):
        """Delete a box."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this box and all its items?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Get box details before deletion for logging
                self.parent.cursor.execute(
                    "SELECT name FROM boxes WHERE id = ?", (box_id,)
                )
                box_data = self.parent.cursor.fetchone()
                box_name = box_data[0] if box_data else "Unknown"

                # Count items in box
                self.parent.cursor.execute(
                    "SELECT COUNT(*) FROM items WHERE box_id = ?", (box_id,)
                )
                item_count = self.parent.cursor.fetchone()[0]

                self.parent.cursor.execute("DELETE FROM boxes WHERE id = ?", (box_id,))
                self.parent.conn.commit()

                # Log the action
                self.parent.log_action(
                    action="DELETE",
                    entity_type="BOX",
                    entity_id=box_id,
                    entity_name=box_name,
                    details=f"Deleted box with {item_count} items",
                )

                QMessageBox.information(self, "Success", "Box deleted successfully")
                self.load_boxes()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")


class HistoryTab(QWidget):
    """Tab for viewing audit logs and transaction history."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Filter bar
        filter_layout = QHBoxLayout()

        # Action filter
        self.action_filter = QComboBox()
        self.action_filter.addItem("All Actions", None)
        self.action_filter.addItem("CREATE", "CREATE")
        self.action_filter.addItem("UPDATE", "UPDATE")
        self.action_filter.addItem("DELETE", "DELETE")
        self.action_filter.currentIndexChanged.connect(self.load_logs)
        filter_layout.addWidget(QLabel("Action:"))
        filter_layout.addWidget(self.action_filter, 1)

        # Entity type filter
        self.entity_filter = QComboBox()
        self.entity_filter.addItem("All Types", None)
        self.entity_filter.addItem("ITEM", "ITEM")
        self.entity_filter.addItem("BOX", "BOX")
        self.entity_filter.currentIndexChanged.connect(self.load_logs)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.entity_filter, 1)

        # Search by entity name
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by entity name...")
        self.search_input.textChanged.connect(self.load_logs)
        filter_layout.addWidget(self.search_input, 2)

        clear_btn = QPushButton("Clear Filters")
        clear_btn.setProperty("class", "neutral")
        clear_btn.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_btn, 1)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_logs)
        filter_layout.addWidget(refresh_btn, 1)

        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Timestamp", "Action", "Type", "Entity", "Details", "ID"]
        )

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch
        )  # Details stretches
        self.table.setColumnWidth(0, 150)  # Timestamp
        self.table.setColumnWidth(1, 80)  # Action
        self.table.setColumnWidth(2, 60)  # Type
        self.table.setColumnWidth(3, 180)  # Entity
        self.table.setColumnWidth(5, 50)  # ID

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)

        layout.addWidget(self.table)

        # Stats summary
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(
            f"color: {ModernStyle.TEXT_SECONDARY}; padding: 5px;"
        )
        layout.addWidget(self.stats_label)

        self.setLayout(layout)
        self.load_logs()

    def clear_filters(self):
        """Clear all filters."""
        self.action_filter.setCurrentIndex(0)
        self.entity_filter.setCurrentIndex(0)
        self.search_input.clear()

    def load_logs(self):
        """Load audit logs into table."""
        self.table.setRowCount(0)

        query = """
            SELECT timestamp, action, entity_type, entity_name, details, entity_id
            FROM audit_logs
            WHERE 1=1
        """
        params = []

        # Apply filters
        action = self.action_filter.currentData()
        if action:
            query += " AND action = ?"
            params.append(action)

        entity_type = self.entity_filter.currentData()
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)

        search_text = self.search_input.text().strip()
        if search_text:
            query += " AND entity_name LIKE ?"
            params.append(f"%{search_text}%")

        query += " ORDER BY id DESC LIMIT 1000"

        self.parent.cursor.execute(query, params)
        logs = self.parent.cursor.fetchall()

        for row_idx, (
            timestamp,
            action,
            entity_type,
            entity_name,
            details,
            entity_id,
        ) in enumerate(logs):
            self.table.insertRow(row_idx)

            # Timestamp
            time_item = QTableWidgetItem(timestamp)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, time_item)

            # Action with color coding
            action_item = QTableWidgetItem(action)
            action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if action == "CREATE":
                action_item.setForeground(QColor(ModernStyle.PRIMARY))
            elif action == "UPDATE":
                action_item.setForeground(QColor("#3498db"))
            elif action == "DELETE":
                action_item.setForeground(QColor(ModernStyle.DANGER))
            self.table.setItem(row_idx, 1, action_item)

            # Type
            type_item = QTableWidgetItem(entity_type)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 2, type_item)

            # Entity name
            entity_item = QTableWidgetItem(entity_name or "N/A")
            entity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, entity_item)

            # Details
            details_item = QTableWidgetItem(details or "")
            details_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(row_idx, 4, details_item)

            # ID
            id_item = QTableWidgetItem(str(entity_id) if entity_id else "")
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 5, id_item)

        # Update stats
        self.update_stats()

    def update_stats(self):
        """Update statistics label."""
        # Count by action type
        self.parent.cursor.execute(
            """
            SELECT action, COUNT(*) FROM audit_logs GROUP BY action
        """
        )
        stats = dict(self.parent.cursor.fetchall())

        total = sum(stats.values())
        creates = stats.get("CREATE", 0)
        updates = stats.get("UPDATE", 0)
        deletes = stats.get("DELETE", 0)

        self.stats_label.setText(
            f"Total Logs: {total} | Creates: {creates} | Updates: {updates} | Deletes: {deletes}"
        )


class InventoryApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Manager")
        self.setMinimumSize(900, 700)

        # Setup database
        self.conn = sqlite3.connect("inventory.db")
        self.cursor = self.conn.cursor()
        self.setup_database()

        # Apply modern style
        self.setStyleSheet(ModernStyle.get_stylesheet())

        # Setup UI
        self.setup_ui()

        # Check backup status after UI is ready
        self.check_backup_status()

    def setup_database(self):
        """Setup database tables."""
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS boxes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """
        )

        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            box_id INTEGER,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (box_id) REFERENCES boxes(id) ON DELETE CASCADE
        )
        """
        )

        # Audit logs table
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER,
            entity_name TEXT,
            details TEXT,
            old_value TEXT,
            new_value TEXT
        )
        """
        )

        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()

        # Setup file logging
        self.setup_logging()

    def setup_logging(self):
        """Setup file-based logging."""
        # Create logs folder if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Setup logger
        log_filename = f"logs/inventory_{datetime.now().strftime('%Y-%m-%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Application started")

    def log_action(
        self,
        action,
        entity_type,
        entity_id=None,
        entity_name=None,
        details=None,
        old_value=None,
        new_value=None,
    ):
        """Log an action to the database and file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log to database
        self.cursor.execute(
            """
            INSERT INTO audit_logs
            (timestamp, action, entity_type, entity_id, entity_name, details, old_value, new_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                action,
                entity_type,
                entity_id,
                entity_name,
                details,
                old_value,
                new_value,
            ),
        )
        self.conn.commit()

        # Log to file
        log_message = f"{action} - {entity_type}"
        if entity_name:
            log_message += f" '{entity_name}'"
        if entity_id:
            log_message += f" (ID: {entity_id})"
        if details:
            log_message += f" - {details}"

        self.logger.info(log_message)

    def setup_ui(self):
        """Setup the main UI."""
        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        # Backup action
        backup_action = QAction("Backup Database", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)

        # Export to CSV action
        export_action = QAction("Export Inventory to CSV", self)
        export_action.triggered.connect(self.export_to_csv)
        file_menu.addAction(export_action)

        # Export logs action
        export_logs_action = QAction("Export Audit Logs to CSV", self)
        export_logs_action.triggered.connect(self.export_logs_to_csv)
        file_menu.addAction(export_logs_action)

        file_menu.addSeparator()

        # Import CSV action
        import_action = QAction("Import from CSV", self)
        import_action.triggered.connect(self.import_from_csv)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Inventory Manager")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(BoxesTab(self), "Boxes")
        tabs.addTab(ItemsTab(self), "Items")
        tabs.addTab(HistoryTab(self), "History")

        layout.addWidget(tabs)

    def get_latest_backup_date(self):
        """Get the date of the most recent backup."""
        backup_folder = "backup"
        if not os.path.exists(backup_folder):
            return None

        # Get all backup files
        backup_files = [
            f
            for f in os.listdir(backup_folder)
            if f.startswith("inventory_backup_") and f.endswith(".db")
        ]

        if not backup_files:
            return None

        # Extract timestamps from filenames and find the most recent
        latest_date = None
        for filename in backup_files:
            try:
                # Extract timestamp from filename: inventory_backup_YYYY-MM-DD_HH-MM-SS.db
                timestamp_str = filename.replace("inventory_backup_", "").replace(
                    ".db", ""
                )
                backup_date = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

                if latest_date is None or backup_date > latest_date:
                    latest_date = backup_date
            except ValueError:
                continue

        return latest_date

    def check_backup_status(self):
        """Check if a backup was made in the last 7 days and notify user if not."""
        latest_backup = self.get_latest_backup_date()

        if latest_backup is None:
            # No backups exist
            reply = QMessageBox.warning(
                self,
                "No Backup Found",
                "No database backup found!\n\nWould you like to create a backup now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.backup_database()
        else:
            # Check if backup is older than 7 days
            days_since_backup = (datetime.now() - latest_backup).days

            if days_since_backup >= 7:
                reply = QMessageBox.warning(
                    self,
                    "Backup Outdated",
                    f"Last backup was {days_since_backup} days ago ({latest_backup.strftime('%Y-%m-%d %H:%M:%S')}).\n\nWould you like to create a backup now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.backup_database()

    def backup_database(self):
        """Backup the database to backup folder with timestamp."""
        try:
            # Create backup folder if it doesn't exist
            backup_folder = "backup"
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)

            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_filename = f"inventory_backup_{timestamp}.db"
            backup_path = os.path.join(backup_folder, backup_filename)

            # Copy the database file
            shutil.copy2("inventory.db", backup_path)

            # Log the backup
            self.log_action(
                action="BACKUP",
                entity_type="DATABASE",
                details=f"Database backed up to {backup_filename}",
            )

            QMessageBox.information(
                self,
                "Backup Successful",
                f"Database backed up successfully to:\n{backup_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Backup Failed", f"Failed to backup database:\n{str(e)}"
            )

    def export_to_csv(self):
        """Export inventory data to CSV file."""
        # Let user choose file location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            f"inventory_export_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(["ID", "Item Name", "Box", "Quantity"])

                # Get all items with box names
                self.cursor.execute(
                    """
                    SELECT items.id, items.name, boxes.name, items.quantity
                    FROM items
                    LEFT JOIN boxes ON items.box_id = boxes.id
                    ORDER BY items.id
                """
                )

                items = self.cursor.fetchall()

                # Write data
                for item in items:
                    writer.writerow([item[0], item[1], item[2] or "N/A", item[3]])

            # Log the export
            self.log_action(
                action="EXPORT",
                entity_type="INVENTORY",
                details=f"Exported {len(items)} items to CSV",
            )

            QMessageBox.information(
                self,
                "Export Successful",
                f"Data exported successfully to:\n{file_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Export Failed", f"Failed to export data:\n{str(e)}"
            )

    def import_from_csv(self):
        """Import inventory data from CSV file with validation."""
        # Let user choose file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import from CSV",
            "",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            import_data = []
            validation_errors = []

            # Get all existing boxes for validation
            self.cursor.execute("SELECT id, name FROM boxes")
            existing_boxes = {name.lower(): box_id for box_id, name in self.cursor.fetchall()}

            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                # Validate header
                required_headers = ['Item Name', 'Box', 'Quantity']
                if not all(header in reader.fieldnames for header in required_headers):
                    QMessageBox.critical(
                        self,
                        "Invalid CSV Format",
                        f"CSV must contain headers: {', '.join(required_headers)}\n"
                        f"Found headers: {', '.join(reader.fieldnames)}"
                    )
                    return

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 for header)
                    item_name = row.get('Item Name', '').strip()
                    box_name = row.get('Box', '').strip()
                    quantity_str = row.get('Quantity', '').strip()

                    item_error = False

                    # Validate item name
                    if not item_name:
                        validation_errors.append(f"Row {row_num}: Item name is empty")
                        item_error = True

                    # Validate box
                    if not box_name:
                        validation_errors.append(f"Row {row_num}: Box name is empty")
                        item_error = True
                    elif box_name.lower() not in existing_boxes:
                        validation_errors.append(
                            f"Row {row_num}: Box '{box_name}' does not exist. Create it first."
                        )
                        item_error = True

                    # Validate quantity
                    try:
                        quantity = int(quantity_str)
                        if quantity < 1:
                            validation_errors.append(f"Row {row_num}: Quantity must be at least 1")
                            item_error = True
                    except ValueError:
                        validation_errors.append(
                            f"Row {row_num}: Invalid quantity '{quantity_str}' (must be a number)"
                        )
                        item_error = True
                        quantity = 0

                    # Add to import data
                    import_data.append({
                        'row': row_num,
                        'name': item_name,
                        'box_name': box_name,
                        'box_id': existing_boxes.get(box_name.lower()),
                        'quantity': quantity,
                        'error': item_error
                    })

            # Show preview dialog
            if not import_data:
                QMessageBox.warning(self, "No Data", "No data found in CSV file")
                return

            preview_dialog = ImportPreviewDialog(self, import_data, validation_errors)
            if preview_dialog.exec() == QDialog.DialogCode.Accepted:
                # User confirmed import - commit to database
                success_count = 0
                failed_count = 0

                for item in import_data:
                    if not item['error']:
                        try:
                            self.cursor.execute(
                                "INSERT INTO items (name, box_id, quantity) VALUES (?, ?, ?)",
                                (item['name'], item['box_id'], item['quantity'])
                            )
                            success_count += 1
                        except sqlite3.Error as e:
                            failed_count += 1
                            self.logger.error(f"Failed to import item '{item['name']}': {e}")

                self.conn.commit()

                # Log the import
                self.log_action(
                    action="IMPORT",
                    entity_type="INVENTORY",
                    details=f"Imported {success_count} items from CSV ({failed_count} failed)"
                )

                QMessageBox.information(
                    self,
                    "Import Complete",
                    f"Successfully imported {success_count} items!\n"
                    + (f"{failed_count} items failed to import." if failed_count > 0 else "")
                )

                # Refresh the items tab if it exists
                for i in range(self.centralWidget().findChild(QTabWidget).count()):
                    tab = self.centralWidget().findChild(QTabWidget).widget(i)
                    if isinstance(tab, ItemsTab):
                        tab.load_items()
                        tab.load_box_filter()
                        break

        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import CSV:\n{str(e)}"
            )
            self.logger.error(f"CSV import failed: {e}")

    def export_logs_to_csv(self):
        """Export audit logs to CSV file."""
        # Let user choose file location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Audit Logs to CSV",
            f"audit_logs_export_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(
                    [
                        "Timestamp",
                        "Action",
                        "Entity Type",
                        "Entity ID",
                        "Entity Name",
                        "Details",
                        "Old Value",
                        "New Value",
                    ]
                )

                # Get all logs
                self.cursor.execute(
                    """
                    SELECT timestamp, action, entity_type, entity_id,
                           entity_name, details, old_value, new_value
                    FROM audit_logs
                    ORDER BY id DESC
                    """
                )

                logs = self.cursor.fetchall()

                # Write data
                for log in logs:
                    writer.writerow(log)

            # Log the export (but don't create infinite loop)
            self.log_action(
                action="EXPORT",
                entity_type="LOGS",
                details=f"Exported {len(logs)} audit logs to CSV",
            )

            QMessageBox.information(
                self,
                "Export Successful",
                f"Audit logs exported successfully to:\n{file_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Export Failed", f"Failed to export logs:\n{str(e)}"
            )

    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Application closing")
        self.log_action(
            action="SHUTDOWN", entity_type="APPLICATION", details="Application closed"
        )
        self.conn.close()
        event.accept()


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create and show main window
    window = InventoryApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
