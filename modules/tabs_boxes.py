"""
Boxes Tab
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
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
    QDialog,
)
from PyQt6.QtCore import Qt

from .styles import ModernStyle
from .dialogs import EditBoxDialog


class BoxesTab(QWidget):
    """Tab for managing boxes."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        tr = self.parent.translator
        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr.tr('placeholder_search_boxes'))
        self.search_input.textChanged.connect(self.load_boxes)
        search_layout.addWidget(self.search_input, 4)

        clear_btn = QPushButton(tr.tr('btn_clear_search'))
        clear_btn.setProperty("class", "neutral")
        clear_btn.clicked.connect(self.search_input.clear)
        search_layout.addWidget(clear_btn, 1)

        add_btn = QPushButton(tr.tr('btn_add_box'))
        add_btn.clicked.connect(self.add_box)
        search_layout.addWidget(add_btn, 1)

        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            tr.tr('header_id'),
            tr.tr('header_box_name'),
            tr.tr('header_location'),
            tr.tr('header_actions')
        ])

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )  # Box Name stretches
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )  # Location stretches
        self.table.setColumnWidth(0, 50)  # ID column narrow
        self.table.setColumnWidth(3, 200)  # Actions column

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
        tr = self.parent.translator
        self.table.setRowCount(0)

        query = "SELECT id, name, location FROM boxes WHERE 1=1"
        params = []

        search_text = self.search_input.text().strip()
        if search_text:
            query += " AND (name LIKE ? OR location LIKE ?)"
            params.append(f"%{search_text}%")
            params.append(f"%{search_text}%")

        query += " ORDER BY id"

        self.parent.cursor.execute(query, params)
        boxes = self.parent.cursor.fetchall()

        for row_idx, (box_id, name, location) in enumerate(boxes):
            self.table.insertRow(row_idx)

            # ID
            id_item = QTableWidgetItem(str(box_id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, id_item)

            # Name
            name_item = QTableWidgetItem(name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 1, name_item)

            # Location
            location_item = QTableWidgetItem(location or "")
            location_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 2, location_item)

            # Actions
            actions_widget = QWidget()
            actions_widget.setStyleSheet("QWidget { background: transparent; border: none; }")
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            edit_btn = QPushButton(tr.tr('btn_edit'))
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
                lambda checked, i=box_id, n=name, loc=location: self.edit_box(i, n, loc)
            )
            actions_layout.addWidget(edit_btn)

            delete_btn = QPushButton(tr.tr('btn_delete'))
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

            self.table.setCellWidget(row_idx, 3, actions_widget)

    def add_box(self):
        """Show add box dialog."""
        dialog = EditBoxDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, location = dialog.result
            try:
                self.parent.cursor.execute(
                    "INSERT INTO boxes (name, location) VALUES (?, ?)", (name, location)
                )
                box_id = self.parent.cursor.lastrowid
                self.parent.conn.commit()

                # Log the action
                details = f"Created new box at location: {location}" if location else "Created new box"
                self.parent.log_action(
                    action="CREATE",
                    entity_type="BOX",
                    entity_id=box_id,
                    entity_name=name,
                    details=details
                )

                QMessageBox.information(self, "Success", "Box added successfully")
                self.load_boxes()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")

    def edit_box(self, box_id, name, location):
        """Show edit box dialog."""
        box_data = (box_id, name, location)
        old_name = name
        old_location = location

        dialog = EditBoxDialog(self, box_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name, new_location = dialog.result
            try:
                self.parent.cursor.execute(
                    "UPDATE boxes SET name = ?, location = ? WHERE id = ?", (new_name, new_location, box_id)
                )
                self.parent.conn.commit()

                # Log the action
                changes = []
                if old_name != new_name:
                    changes.append(f"name: '{old_name}' → '{new_name}'")
                if old_location != new_location:
                    changes.append(f"location: '{old_location or 'None'}' → '{new_location or 'None'}'")

                change_details = ", ".join(changes) if changes else "No changes"
                self.parent.log_action(
                    action="UPDATE",
                    entity_type="BOX",
                    entity_id=box_id,
                    entity_name=new_name,
                    details=change_details,
                    old_value=f"name: {old_name}, location: {old_location}",
                    new_value=f"name: {new_name}, location: {new_location}"
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
                self.parent.cursor.execute("SELECT name FROM boxes WHERE id = ?", (box_id,))
                box_data = self.parent.cursor.fetchone()
                box_name = box_data[0] if box_data else "Unknown"

                # Count items in box
                self.parent.cursor.execute("SELECT COUNT(*) FROM items WHERE box_id = ?", (box_id,))
                item_count = self.parent.cursor.fetchone()[0]

                self.parent.cursor.execute("DELETE FROM boxes WHERE id = ?", (box_id,))
                self.parent.conn.commit()

                # Log the action
                self.parent.log_action(
                    action="DELETE",
                    entity_type="BOX",
                    entity_id=box_id,
                    entity_name=box_name,
                    details=f"Deleted box with {item_count} items"
                )

                QMessageBox.information(self, "Success", "Box deleted successfully")
                self.load_boxes()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")
