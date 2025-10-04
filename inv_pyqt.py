import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QDialog, QFormLayout, QComboBox, QSpinBox, QMessageBox, QTabWidget,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QFont


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
            }}

            QTabWidget::pane {{
                border: 1px solid {ModernStyle.BORDER};
                background-color: {ModernStyle.BACKGROUND};
                border-radius: 8px;
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
                border-radius: 8px;
            }}

            QTableWidget::item {{
                padding: 10px;
            }}

            QTableWidget::item:selected {{
                background-color: #3498db;
            }}

            QHeaderView::section {{
                background-color: #333333;
                color: {ModernStyle.TEXT};
                padding: 10px;
                border: none;
                font-weight: bold;
            }}

            QPushButton {{
                background-color: {ModernStyle.PRIMARY};
                color: {ModernStyle.TEXT};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
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
            }}

            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border: 1px solid #3498db;
            }}

            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {ModernStyle.TEXT};
                margin-right: 5px;
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
        self.table.setHorizontalHeaderLabels(["ID", "Item Name", "Box", "Quantity", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

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
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, i=item_id, n=name, q=quantity, b=box_id: self.edit_item(i, n, q, b))
            actions_layout.addWidget(edit_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setProperty("class", "danger")
            delete_btn.clicked.connect(lambda checked, i=item_id: self.delete_item(i))
            actions_layout.addWidget(delete_btn)

            self.table.setCellWidget(row_idx, 4, actions_widget)

        self.table.resizeRowsToContents()

    def clear_filters(self):
        """Clear all filters."""
        self.search_input.clear()
        self.box_filter.setCurrentIndex(0)

    def add_item(self):
        """Show add item dialog."""
        if self.box_filter.count() <= 1:
            QMessageBox.warning(self, "Error", "No boxes available. Please create a box first.")
            return

        dialog = EditItemDialog(self, self.parent.cursor)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, box_id, quantity = dialog.result
            try:
                self.parent.cursor.execute(
                    "INSERT INTO items (name, box_id, quantity) VALUES (?, ?, ?)",
                    (name, box_id, quantity)
                )
                self.parent.conn.commit()
                QMessageBox.information(self, "Success", "Item added successfully")
                self.load_items()
                self.load_box_filter()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")

    def edit_item(self, item_id, name, quantity, box_id):
        """Show edit item dialog."""
        item_data = (item_id, name, None, quantity, box_id)
        dialog = EditItemDialog(self, self.parent.cursor, item_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, box_id, quantity = dialog.result
            try:
                self.parent.cursor.execute(
                    "UPDATE items SET name = ?, box_id = ?, quantity = ? WHERE id = ?",
                    (name, box_id, quantity, item_id)
                )
                self.parent.conn.commit()
                QMessageBox.information(self, "Success", "Item updated successfully")
                self.load_items()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")

    def delete_item(self, item_id):
        """Delete an item."""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this item?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.parent.cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
                self.parent.conn.commit()
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
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

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
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, i=box_id, n=name: self.edit_box(i, n))
            actions_layout.addWidget(edit_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setProperty("class", "danger")
            delete_btn.clicked.connect(lambda checked, i=box_id: self.delete_box(i))
            actions_layout.addWidget(delete_btn)

            self.table.setCellWidget(row_idx, 2, actions_widget)

        self.table.resizeRowsToContents()

    def add_box(self):
        """Show add box dialog."""
        dialog = EditBoxDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.result
            try:
                self.parent.cursor.execute("INSERT INTO boxes (name) VALUES (?)", (name,))
                self.parent.conn.commit()
                QMessageBox.information(self, "Success", "Box added successfully")
                self.load_boxes()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")

    def edit_box(self, box_id, name):
        """Show edit box dialog."""
        box_data = (box_id, name)
        dialog = EditBoxDialog(self, box_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.result
            try:
                self.parent.cursor.execute("UPDATE boxes SET name = ? WHERE id = ?", (name, box_id))
                self.parent.conn.commit()
                QMessageBox.information(self, "Success", "Box updated successfully")
                self.load_boxes()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")

    def delete_box(self, box_id):
        """Delete a box."""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this box and all its items?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.parent.cursor.execute("DELETE FROM boxes WHERE id = ?", (box_id,))
                self.parent.conn.commit()
                QMessageBox.information(self, "Success", "Box deleted successfully")
                self.load_boxes()
            except sqlite3.Error as e:
                self.parent.conn.rollback()
                QMessageBox.critical(self, "Error", f"Database error: {e}")


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

    def setup_database(self):
        """Setup database tables."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS boxes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            box_id INTEGER,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (box_id) REFERENCES boxes(id) ON DELETE CASCADE
        )
        """)

        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()

    def setup_ui(self):
        """Setup the main UI."""
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
        tabs.addTab(ItemsTab(self), "Items")
        tabs.addTab(BoxesTab(self), "Boxes")

        layout.addWidget(tabs)

    def closeEvent(self, event):
        """Handle window close event."""
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
