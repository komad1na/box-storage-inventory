"""
Main Application Window
"""

import os
import shutil
import csv
import logging
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QTabWidget,
    QMessageBox,
    QFileDialog,
    QDialog,
)
from PyQt6.QtGui import QFont, QAction

from . import __version__, __app_name__, __developer__
from .styles import ModernStyle
from .tabs_boxes import BoxesTab
from .tabs_items import ItemsTab
from .tabs_history import HistoryTab
from .dialogs import ImportPreviewDialog


class InventoryApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{__app_name__} v{__version__}")
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

        # Help menu
        help_menu = menubar.addMenu("Help")

        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

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
            self, "Import from CSV", "", "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            import_data = []
            validation_errors = []

            # Get all existing boxes for validation
            self.cursor.execute("SELECT id, name FROM boxes")
            existing_boxes = {
                name.lower(): box_id for box_id, name in self.cursor.fetchall()
            }

            with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                # Validate header
                required_headers = ["Item Name", "Box", "Quantity"]
                if not all(header in reader.fieldnames for header in required_headers):
                    QMessageBox.critical(
                        self,
                        "Invalid CSV Format",
                        f"CSV must contain headers: {', '.join(required_headers)}\n"
                        f"Found headers: {', '.join(reader.fieldnames)}",
                    )
                    return

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 for header)
                    item_name = row.get("Item Name", "").strip()
                    box_name = row.get("Box", "").strip()
                    quantity_str = row.get("Quantity", "").strip()

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
                            validation_errors.append(
                                f"Row {row_num}: Quantity must be at least 1"
                            )
                            item_error = True
                    except ValueError:
                        validation_errors.append(
                            f"Row {row_num}: Invalid quantity '{quantity_str}' (must be a number)"
                        )
                        item_error = True
                        quantity = 0

                    # Add to import data
                    import_data.append(
                        {
                            "row": row_num,
                            "name": item_name,
                            "box_name": box_name,
                            "box_id": existing_boxes.get(box_name.lower()),
                            "quantity": quantity,
                            "error": item_error,
                        }
                    )

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
                    if not item["error"]:
                        try:
                            self.cursor.execute(
                                "INSERT INTO items (name, box_id, quantity) VALUES (?, ?, ?)",
                                (item["name"], item["box_id"], item["quantity"]),
                            )
                            success_count += 1
                        except sqlite3.Error as e:
                            failed_count += 1
                            self.logger.error(
                                f"Failed to import item '{item['name']}': {e}"
                            )

                self.conn.commit()

                # Log the import
                self.log_action(
                    action="IMPORT",
                    entity_type="INVENTORY",
                    details=f"Imported {success_count} items from CSV ({failed_count} failed)",
                )

                QMessageBox.information(
                    self,
                    "Import Complete",
                    f"Successfully imported {success_count} items!\n"
                    + (f"{failed_count} items failed to import." if failed_count > 0 else ""),
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
                self, "Import Failed", f"Failed to import CSV:\n{str(e)}"
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

    def show_about(self):
        """Show about dialog."""
        about_text = f"""
        <h2>{__app_name__}</h2>
        <p><b>Version:</b> {__version__}</p>
        <p><b>Developer:</b> {__developer__}</p>
        <p>A modern inventory management system with comprehensive logging and audit trails.</p>

        <h3>Features:</h3>
        <ul>
            <li>✓ Manage items and storage boxes</li>
            <li>✓ Search and filter capabilities</li>
            <li>✓ CSV import/export functionality</li>
            <li>✓ Complete audit log and transaction history</li>
            <li>✓ Automatic database backups</li>
            <li>✓ Modern dark theme interface</li>
        </ul>

        <p><b>Database:</b> SQLite</p>
        <p><b>Framework:</b> PyQt6</p>
        """

        QMessageBox.about(self, f"About {__app_name__}", about_text)

    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Application closing")
        self.log_action(
            action="SHUTDOWN", entity_type="APPLICATION", details="Application closed"
        )
        self.conn.close()
        event.accept()
