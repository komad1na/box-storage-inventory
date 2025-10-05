"""
Items Tab
"""

import sqlite3
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
    QDialog,
)
from PyQt6.QtCore import Qt

from .styles import ModernStyle
from .dialogs import EditItemDialog


class ItemsTab(QWidget):
    """Tab for managing items."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

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
                self.parent.cursor.execute("SELECT name FROM boxes WHERE id = ?", (box_id,))
                box_name = self.parent.cursor.fetchone()[0]

                # Log the action
                self.parent.log_action(
                    action="CREATE",
                    entity_type="ITEM",
                    entity_id=item_id,
                    entity_name=name,
                    details=f"Added {quantity} units to box '{box_name}'"
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
                self.parent.cursor.execute("SELECT name FROM boxes WHERE id = ?", (new_box_id,))
                new_box_name = self.parent.cursor.fetchone()[0]

                # Build change details
                changes = []
                if old_values["name"] != new_name:
                    changes.append(f"name: '{old_values['name']}' → '{new_name}'")
                if old_values["quantity"] != new_quantity:
                    changes.append(f"quantity: {old_values['quantity']} → {new_quantity}")
                if old_values["box_id"] != new_box_id:
                    self.parent.cursor.execute("SELECT name FROM boxes WHERE id = ?", (old_values["box_id"],))
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
                    new_value=f"{{'name': '{new_name}', 'quantity': {new_quantity}, 'box_id': {new_box_id}}}"
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
                    (item_id,)
                )
                item_data = self.parent.cursor.fetchone()
                item_name, quantity, box_name = item_data if item_data else ("Unknown", 0, "Unknown")

                self.parent.cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
                self.parent.conn.commit()

                # Log the action
                self.parent.log_action(
                    action="DELETE",
                    entity_type="ITEM",
                    entity_id=item_id,
                    entity_name=item_name,
                    details=f"Deleted {quantity} units from box '{box_name}'"
                )

                QMessageBox.information(self, "Success", "Item deleted successfully")
                self.load_items()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")
