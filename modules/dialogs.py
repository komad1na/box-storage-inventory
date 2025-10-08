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

        if item_data:
            self.logger.info(f"Opened Edit Item dialog for item ID: {item_data[0]}, Name: {item_data[1]}")
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
            self.logger.warning("Item save cancelled: name is empty")
            QMessageBox.warning(self, "Error", "Item name cannot be empty")
            return

        box_id = self.box_combo.currentData()
        if not box_id:
            self.logger.warning("Item save cancelled: no box selected")
            QMessageBox.warning(self, "Error", "Please select a box")
            return

        quantity = self.quantity_spin.value()
        if quantity < 1:
            self.logger.warning(f"Item save cancelled: invalid quantity {quantity}")
            QMessageBox.warning(self, "Error", "Quantity must be at least 1")
            return

        # Validate name length
        if len(name) > 255:
            self.logger.warning(f"Item save cancelled: name too long ({len(name)} characters)")
            QMessageBox.warning(self, "Error", "Item name is too long (max 255 characters)")
            return

        self.logger.info(f"Item dialog saved: name='{name}', box_id={box_id}, quantity={quantity}")
        self.result = (name, box_id, quantity)
        self.accept()
        self.logger.info("Item dialog closed (accepted)")


class ImportPreviewDialog(QDialog):
    """Dialog for previewing CSV import data before committing."""

    def __init__(self, parent, import_data, validation_errors):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.import_data = import_data
        self.validation_errors = validation_errors
        self.setWindowTitle("CSV Import Preview")
        self.setModal(True)
        self.setMinimumSize(800, 600)

        self.logger.info(f"Opened CSV Import Preview dialog: {len(import_data)} items, {len(validation_errors)} errors")

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
        self.logger = logging.getLogger(__name__)
        self.box_data = box_data
        dialog_type = "Edit Box" if box_data else "Add New Box"
        self.setWindowTitle(dialog_type)
        self.setModal(True)
        self.setMinimumWidth(400)

        if box_data:
            self.logger.info(f"Opened Edit Box dialog for box ID: {box_data[0]}, Name: {box_data[1]}")
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
        self.name_input.setPlaceholderText("Enter box name")
        if self.box_data:
            self.name_input.setText(self.box_data[1])
        form_layout.addRow("Box Name:", self.name_input)

        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g., Garage Shelf 2, Basement Cabinet A")
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
            self.logger.warning("Box save cancelled: name is empty")
            QMessageBox.warning(self, "Error", "Box name cannot be empty")
            return

        # Validate name length
        if len(name) > 255:
            self.logger.warning(f"Box save cancelled: name too long ({len(name)} characters)")
            QMessageBox.warning(self, "Error", "Box name is too long (max 255 characters)")
            return

        location = self.location_input.text().strip()

        # Validate location length
        if location and len(location) > 255:
            self.logger.warning(f"Box save cancelled: location too long ({len(location)} characters)")
            QMessageBox.warning(self, "Error", "Location is too long (max 255 characters)")
            return

        self.logger.info(f"Box dialog saved: name='{name}', location='{location}'")
        self.result = (name, location)
        self.accept()
        self.logger.info("Box dialog closed (accepted)")


class HelpDialog(QDialog):
    """Comprehensive help dialog with all application information."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Help - Inventory Manager")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Inventory Manager - Help & Documentation")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabs for different help sections
        tabs = QTabWidget()

        # Getting Started tab
        getting_started = self.create_scrollable_text(self.get_getting_started_text())
        tabs.addTab(getting_started, "Getting Started")

        # Keyboard Shortcuts tab
        shortcuts = self.create_scrollable_text(self.get_shortcuts_text())
        tabs.addTab(shortcuts, "Keyboard Shortcuts")

        # Features tab
        features = self.create_scrollable_text(self.get_features_text())
        tabs.addTab(features, "Features")

        # Tips & Tricks tab
        tips = self.create_scrollable_text(self.get_tips_text())
        tabs.addTab(tips, "Tips & Tricks")

        # Database Info tab
        db_info = self.create_scrollable_text(self.get_database_text())
        tabs.addTab(db_info, "Database Info")

        layout.addWidget(tabs)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setMaximumWidth(100)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def create_scrollable_text(self, html_text):
        """Create a scrollable text widget."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        text_widget.setHtml(html_text)

        scroll.setWidget(text_widget)
        return scroll

    def get_getting_started_text(self):
        """Return getting started guide HTML."""
        return """
        <style>
            h2 { color: #33b36b; margin-top: 20px; }
            h3 { color: #3498db; margin-top: 15px; }
            ul { margin-left: 20px; }
            code { background-color: rgba(0,0,0,0.1); padding: 2px 5px; border-radius: 3px; }
        </style>

        <h2>Welcome to Inventory Manager!</h2>
        <p>A modern desktop application for managing your items and storage boxes with comprehensive audit logging.</p>

        <h3>📦 Managing Boxes</h3>
        <p>Boxes are storage containers where you organize your items.</p>
        <ul>
            <li><b>Add a Box:</b> Click "+ Add Box" or press <code>Ctrl+N</code> on the Boxes tab</li>
            <li><b>Edit a Box:</b> Click the "Edit" button next to any box</li>
            <li><b>Delete a Box:</b> Click "Delete" (this will remove all items in the box)</li>
            <li><b>Location:</b> Specify where the box is stored (e.g., "Garage Shelf 2", "Basement Cabinet A")</li>
            <li><b>Search:</b> Use the search bar to find boxes by name or location</li>
        </ul>

        <h3>📋 Managing Items</h3>
        <p>Items are the actual things you store in boxes.</p>
        <ul>
            <li><b>Add an Item:</b> Click "+ Add Item" or press <code>Ctrl+N</code> on the Items tab</li>
            <li><b>Edit an Item:</b> Click the "Edit" button to modify name, quantity, or box location</li>
            <li><b>Delete an Item:</b> Click "Del" to remove the item</li>
            <li><b>Quantity:</b> Track how many units of each item you have (minimum 1)</li>
            <li><b>Filter:</b> Use the dropdown to show items in a specific box only</li>
            <li><b>Search:</b> Find items quickly by typing their name</li>
        </ul>

        <h3>📊 History & Audit Logs</h3>
        <p>Every action is logged automatically for complete traceability.</p>
        <ul>
            <li>View all changes made to boxes and items</li>
            <li>See when items were created, updated, or deleted</li>
            <li>Track quantity changes and box movements</li>
            <li>Export logs to CSV for external analysis</li>
        </ul>

        <h3>💾 Backup & Export</h3>
        <ul>
            <li><b>Automatic Backups:</b> You'll be reminded if no backup was made in the last 7 days</li>
            <li><b>Manual Backup:</b> File → Backup Database or press <code>Ctrl+B</code></li>
            <li><b>Export Inventory:</b> File → Export to CSV or press <code>Ctrl+E</code></li>
            <li><b>Import Data:</b> File → Import from CSV (with validation preview)</li>
        </ul>
        """

    def get_shortcuts_text(self):
        """Return keyboard shortcuts HTML."""
        return """
        <style>
            h2 { color: #33b36b; margin-top: 20px; }
            table { border-collapse: collapse; width: 100%; margin-top: 15px; }
            th { background-color: rgba(51, 179, 107, 0.2); padding: 10px; text-align: left; border: 1px solid #404040; }
            td { padding: 10px; border: 1px solid #404040; }
            tr:nth-child(even) { background-color: rgba(0,0,0,0.05); }
            code { background-color: rgba(0,0,0,0.1); padding: 2px 8px; border-radius: 3px; font-weight: bold; }
        </style>

        <h2>⌨️ Keyboard Shortcuts</h2>
        <p>Speed up your workflow with these keyboard shortcuts:</p>

        <table>
            <tr>
                <th>Shortcut</th>
                <th>Action</th>
                <th>Description</th>
            </tr>
            <tr>
                <td><code>Ctrl+F</code></td>
                <td>Focus Search</td>
                <td>Jump to the search box in the current tab</td>
            </tr>
            <tr>
                <td><code>Ctrl+N</code></td>
                <td>Add New</td>
                <td>Add new box/item depending on active tab</td>
            </tr>
            <tr>
                <td><code>Ctrl+B</code></td>
                <td>Backup</td>
                <td>Create database backup immediately</td>
            </tr>
            <tr>
                <td><code>Ctrl+E</code></td>
                <td>Export</td>
                <td>Export inventory to CSV file</td>
            </tr>
            <tr>
                <td><code>Ctrl+T</code></td>
                <td>Toggle Theme</td>
                <td>Switch between dark and light theme</td>
            </tr>
            <tr>
                <td><code>Ctrl+1</code></td>
                <td>Boxes Tab</td>
                <td>Switch to the Boxes management tab</td>
            </tr>
            <tr>
                <td><code>Ctrl+2</code></td>
                <td>Items Tab</td>
                <td>Switch to the Items management tab</td>
            </tr>
            <tr>
                <td><code>Ctrl+3</code></td>
                <td>History Tab</td>
                <td>Switch to the History/Audit Logs tab</td>
            </tr>
        </table>

        <p style="margin-top: 20px;"><b>💡 Tip:</b> All shortcuts are also available through the menu bar for easy discovery!</p>
        """

    def get_features_text(self):
        """Return features overview HTML."""
        return """
        <style>
            h2 { color: #33b36b; margin-top: 20px; }
            h3 { color: #3498db; margin-top: 15px; }
            ul { margin-left: 20px; }
            .feature-box { background-color: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 8px; margin: 10px 0; }
        </style>

        <h2>✨ Key Features</h2>

        <div class="feature-box">
            <h3>🎨 Modern User Interface</h3>
            <ul>
                <li>Clean, intuitive design with dark and light themes</li>
                <li>Responsive tables with alternating row colors</li>
                <li>Quick action buttons for common operations</li>
                <li>Real-time search and filtering</li>
            </ul>
        </div>

        <div class="feature-box">
            <h3>📦 Smart Inventory Management</h3>
            <ul>
                <li>Organize items into storage boxes</li>
                <li>Track quantities for each item</li>
                <li>Specify physical locations for easy retrieval</li>
                <li>Support for unlimited boxes and items</li>
            </ul>
        </div>

        <div class="feature-box">
            <h3>🔍 Advanced Search & Filtering</h3>
            <ul>
                <li>Search boxes by name or location</li>
                <li>Search items by name</li>
                <li>Filter items by specific box</li>
                <li>Database indexes for fast searches</li>
            </ul>
        </div>

        <div class="feature-box">
            <h3>📊 Comprehensive Audit Trail</h3>
            <ul>
                <li>Every action is automatically logged</li>
                <li>Track what changed, when, and from what value</li>
                <li>Export audit logs to CSV</li>
                <li>Perfect for accountability and compliance</li>
            </ul>
        </div>

        <div class="feature-box">
            <h3>💾 Data Protection</h3>
            <ul>
                <li>SQLite database for reliable storage</li>
                <li>Automatic backup reminders (every 7 days)</li>
                <li>One-click manual backups</li>
                <li>Import/Export via CSV files</li>
                <li>Data validation to prevent errors</li>
            </ul>
        </div>

        <div class="feature-box">
            <h3>🌍 Multi-Language Support</h3>
            <ul>
                <li>Switch languages on the fly</li>
                <li>Language preference saved automatically</li>
                <li>Easy to add more translations</li>
            </ul>
        </div>

        <div class="feature-box">
            <h3>📝 Detailed Logging</h3>
            <ul>
                <li>Daily log files in the 'logs' folder</li>
                <li>Track application startup, errors, and user actions</li>
                <li>UTF-8 encoding for international characters</li>
                <li>Console output for debugging</li>
            </ul>
        </div>
        """

    def get_tips_text(self):
        """Return tips and tricks HTML."""
        return """
        <style>
            h2 { color: #33b36b; margin-top: 20px; }
            .tip { background-color: rgba(51, 179, 107, 0.1); padding: 12px; border-left: 4px solid #33b36b; margin: 10px 0; }
            .warning { background-color: rgba(230, 77, 77, 0.1); padding: 12px; border-left: 4px solid #e64d4d; margin: 10px 0; }
            .info { background-color: rgba(52, 152, 219, 0.1); padding: 12px; border-left: 4px solid #3498db; margin: 10px 0; }
        </style>

        <h2>💡 Tips & Tricks</h2>

        <div class="tip">
            <b>🏷️ Use Descriptive Box Names</b><br>
            Instead of "Box 1", use names like "Kitchen - Baking Supplies" or "Garage - Power Tools" for easier identification.
        </div>

        <div class="tip">
            <b>📍 Always Add Locations</b><br>
            Specify where each box is physically stored. Use a consistent naming scheme like "Garage-Shelf2-Left" to find items quickly.
        </div>

        <div class="tip">
            <b>🔄 Regular Backups</b><br>
            Create backups before making bulk changes or imports. Backups are timestamped and stored in the 'backup' folder.
        </div>

        <div class="tip">
            <b>📊 Use CSV Import for Bulk Data</b><br>
            Instead of adding items one by one, prepare a CSV file with your inventory and import it. The preview feature helps catch errors before importing.
        </div>

        <div class="info">
            <b>🔍 Search Tips</b><br>
            Search is case-insensitive and searches partial matches. For example, searching "screw" will find "Screws", "Screwdriver", etc.
        </div>

        <div class="info">
            <b>⌨️ Keyboard Navigation</b><br>
            Use Tab to move between fields in dialogs, and Enter to submit. This speeds up data entry significantly.
        </div>

        <div class="warning">
            <b>⚠️ Deleting Boxes</b><br>
            When you delete a box, ALL items in that box are also deleted. You'll get a confirmation dialog showing how many items will be affected.
        </div>

        <div class="warning">
            <b>⚠️ Minimum Quantity</b><br>
            Items must have at least quantity 1. If you use up an item completely, delete it rather than setting quantity to 0.
        </div>

        <div class="tip">
            <b>🎨 Theme Preference</b><br>
            Your theme choice (dark/light) is saved automatically. The app will remember your preference next time you launch it.
        </div>

        <div class="tip">
            <b>📈 Review History Regularly</b><br>
            Check the History tab to see what items were added, removed, or moved. Great for tracking inventory changes over time.
        </div>

        <div class="info">
            <b>📄 CSV Export Format</b><br>
            Exported CSV files include: Item ID, Item Name, Box Name, and Quantity. Perfect for spreadsheet analysis or reporting.
        </div>
        """

    def get_database_text(self):
        """Return database information HTML."""
        return """
        <style>
            h2 { color: #33b36b; margin-top: 20px; }
            h3 { color: #3498db; margin-top: 15px; }
            code { background-color: rgba(0,0,0,0.1); padding: 2px 5px; border-radius: 3px; font-family: monospace; }
            ul { margin-left: 20px; }
            table { border-collapse: collapse; width: 100%; margin-top: 10px; }
            th { background-color: rgba(51, 179, 107, 0.2); padding: 8px; text-align: left; border: 1px solid #404040; }
            td { padding: 8px; border: 1px solid #404040; }
        </style>

        <h2>💾 Database Information</h2>

        <h3>Database Location</h3>
        <p>The inventory database is stored as <code>inventory.db</code> in the application directory.</p>

        <h3>Tables Structure</h3>

        <table>
            <tr>
                <th>Table</th>
                <th>Purpose</th>
                <th>Key Fields</th>
            </tr>
            <tr>
                <td><b>boxes</b></td>
                <td>Storage box information</td>
                <td>id, name, location</td>
            </tr>
            <tr>
                <td><b>items</b></td>
                <td>Items stored in boxes</td>
                <td>id, name, box_id, quantity</td>
            </tr>
            <tr>
                <td><b>audit_logs</b></td>
                <td>Complete action history</td>
                <td>timestamp, action, entity_type, details</td>
            </tr>
            <tr>
                <td><b>settings</b></td>
                <td>User preferences</td>
                <td>key, value (language, theme)</td>
            </tr>
        </table>

        <h3>Performance Optimizations</h3>
        <ul>
            <li><b>Indexes:</b> Created on frequently searched columns (box names, item names, locations)</li>
            <li><b>Foreign Keys:</b> Enabled for referential integrity</li>
            <li><b>Constraints:</b> Quantity must be > 0, names cannot be empty</li>
        </ul>

        <h3>Backup Files</h3>
        <p>Backups are stored in the <code>backup/</code> folder with timestamps:</p>
        <ul>
            <li>Format: <code>inventory_backup_YYYY-MM-DD_HH-MM-SS.db</code></li>
            <li>Full database copy - can be restored by renaming to <code>inventory.db</code></li>
            <li>Check backup age on startup (warning after 7 days)</li>
        </ul>

        <h3>Log Files</h3>
        <p>Application logs are stored in the <code>logs/</code> folder:</p>
        <ul>
            <li>Format: <code>inventory_YYYY-MM-DD.log</code></li>
            <li>One log file per day</li>
            <li>UTF-8 encoded for international character support</li>
            <li>Records startup, database operations, user actions, errors</li>
        </ul>

        <h3>Data Validation</h3>
        <ul>
            <li>Box/item names: Required, max 255 characters</li>
            <li>Location: Optional, max 255 characters</li>
            <li>Quantity: Must be integer ≥ 1</li>
            <li>CSV imports: Pre-validated before committing to database</li>
        </ul>

        <h3>Technology Stack</h3>
        <ul>
            <li><b>Database:</b> SQLite 3 (serverless, zero-configuration)</li>
            <li><b>GUI Framework:</b> PyQt6 (cross-platform)</li>
            <li><b>Language:</b> Python 3.13+</li>
            <li><b>Style:</b> Custom modern theme with Fusion base</li>
        </ul>
        """
