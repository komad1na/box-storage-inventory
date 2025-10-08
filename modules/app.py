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
from PyQt6.QtGui import QFont, QAction, QIcon, QKeySequence, QShortcut

from . import __version__, __app_name__, __developer__
from .styles import ModernStyle
from .tabs_boxes import BoxesTab
from .tabs_items import ItemsTab
from .tabs_history import HistoryTab
from .tabs_stats import StatsTab
from .dialogs import ImportPreviewDialog, HelpDialog


class InventoryApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(1200, 800)

        # Setup database
        self.conn = sqlite3.connect("inventory.db")
        self.cursor = self.conn.cursor()
        self.setup_database()

        # Load language preference
        self.load_language_preference()

        # Set window title with translated app name
        self.setWindowTitle(f"{self.translator.tr('app_name')} v{__version__}")
        self.logger.info(
            f"Window title set to: {self.translator.tr('app_name')} v{__version__}"
        )

        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            self.logger.info(f"Window icon set to: {icon_path}")
        else:
            self.logger.warning(f"Icon file not found at: {icon_path}")

        # Load theme preference first
        self.load_theme_preference_initial()

        # Apply modern style
        self.setStyleSheet(ModernStyle.get_stylesheet())
        self.logger.info("Modern style applied")

        # Setup UI
        self.logger.info("Setting up UI components...")
        self.setup_ui()
        self.logger.info("UI setup complete")

        # Check backup status after UI is ready
        self.logger.info("Checking backup status...")
        self.check_backup_status()

    def setup_database(self):
        """Setup database tables."""
        # Setup logging first so we can log database operations
        self.setup_logging()

        self.logger.info("=== Database Setup Started ===")
        self.logger.info("Creating/verifying database tables...")

        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS boxes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT
        )
        """
        )
        self.logger.info("Boxes table verified")

        # Add location column if it doesn't exist (migration for existing databases)
        try:
            self.cursor.execute("ALTER TABLE boxes ADD COLUMN location TEXT")
            self.conn.commit()
            self.logger.info(
                "Database migration: Added 'location' column to boxes table"
            )
        except sqlite3.OperationalError:
            # Column already exists
            self.logger.info("Database migration: 'location' column already exists")

        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            box_id INTEGER,
            quantity INTEGER DEFAULT 1 CHECK(quantity > 0),
            FOREIGN KEY (box_id) REFERENCES boxes(id) ON DELETE CASCADE
        )
        """
        )
        self.logger.info("Items table verified")

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
        self.logger.info("Audit logs table verified")

        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()
        self.logger.info("Foreign keys enabled")

        # Create indexes for better search performance
        self.logger.info("Creating database indexes...")
        try:
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_boxes_name ON boxes(name)"
            )
            self.logger.info("Index created: idx_boxes_name")
        except sqlite3.OperationalError as e:
            self.logger.warning(f"Index creation warning for boxes.name: {e}")

        try:
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_boxes_location ON boxes(location)"
            )
            self.logger.info("Index created: idx_boxes_location")
        except sqlite3.OperationalError as e:
            self.logger.warning(f"Index creation warning for boxes.location: {e}")

        try:
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_items_name ON items(name)"
            )
            self.logger.info("Index created: idx_items_name")
        except sqlite3.OperationalError as e:
            self.logger.warning(f"Index creation warning for items.name: {e}")

        try:
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_items_box_id ON items(box_id)"
            )
            self.logger.info("Index created: idx_items_box_id")
        except sqlite3.OperationalError as e:
            self.logger.warning(f"Index creation warning for items.box_id: {e}")

        self.conn.commit()
        self.logger.info("Database indexes created successfully")
        self.logger.info("=== Database Setup Complete ===")

        # Log database statistics
        self.cursor.execute("SELECT COUNT(*) FROM boxes")
        box_count = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM items")
        item_count = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM audit_logs")
        log_count = self.cursor.fetchone()[0]
        self.logger.info(
            f"Database statistics: {box_count} boxes, {item_count} items, {log_count} audit logs"
        )

    def setup_logging(self):
        """Setup file-based logging."""
        # Create logs folder if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Setup logger with UTF-8 encoding
        log_filename = f"logs/inventory_{datetime.now().strftime('%Y-%m-%d')}.log"

        # Create handlers with proper encoding
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        # StreamHandler with UTF-8 for console (handles Windows encoding issues)
        import sys

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, stream_handler],
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

        # Log to file (with safe encoding for console)
        log_message = f"{action} - {entity_type}"
        if entity_name:
            log_message += f" '{entity_name}'"
        if entity_id:
            log_message += f" (ID: {entity_id})"
        if details:
            log_message += f" - {details}"

        # Safe logging that handles Unicode issues on Windows console
        try:
            self.logger.info(log_message)
        except UnicodeEncodeError:
            # Fallback: replace problematic characters for console output
            safe_message = (
                log_message.replace("→", "->").replace("✓", "OK").replace("⚠", "WARN")
            )
            self.logger.info(safe_message)

    def setup_ui(self):
        """Setup the main UI."""
        tr = self.translator

        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu(tr.tr("menu_file"))

        # Backup action
        backup_action = QAction(tr.tr("menu_backup"), self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)

        # Export to CSV action
        export_action = QAction(tr.tr("menu_export_inventory"), self)
        export_action.triggered.connect(self.export_to_csv)
        file_menu.addAction(export_action)

        # Export logs action
        export_logs_action = QAction(tr.tr("menu_export_logs"), self)
        export_logs_action.triggered.connect(self.export_logs_to_csv)
        file_menu.addAction(export_logs_action)

        file_menu.addSeparator()

        # Import CSV action
        import_action = QAction(tr.tr("menu_import"), self)
        import_action.triggered.connect(self.import_from_csv)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction(tr.tr("menu_exit"), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Language menu
        language_menu = menubar.addMenu(tr.tr("menu_language"))

        # Get available languages
        from .translations import Translations

        temp_tr = Translations()
        languages = temp_tr.get_languages()

        # Create language action group for radio button behavior
        from PyQt6.QtGui import QActionGroup

        self.language_action_group = QActionGroup(self)
        self.language_action_group.setExclusive(True)

        # Add language actions
        for lang_code, lang_name in languages.items():
            lang_action = QAction(lang_name, self)
            lang_action.setCheckable(True)
            lang_action.setData(lang_code)

            # Check if this is the current language
            current_lang = self.get_current_language()
            if lang_code == current_lang:
                lang_action.setChecked(True)

            lang_action.triggered.connect(
                lambda checked, code=lang_code: self.change_language(code)
            )
            self.language_action_group.addAction(lang_action)
            language_menu.addAction(lang_action)

        # View menu
        view_menu = menubar.addMenu("View")

        # Theme toggle action
        self.theme_action = QAction("Switch to Light Theme", self)
        self.theme_action.setShortcut("Ctrl+T")
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)

        # Help menu
        help_menu = menubar.addMenu(tr.tr("menu_help"))

        # Help action
        help_action = QAction("Help & Documentation", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        # Export import template
        template_action = QAction("Export CSV Import Template", self)
        template_action.triggered.connect(self.export_import_template)
        help_menu.addAction(template_action)

        help_menu.addSeparator()

        # About action
        about_action = QAction(tr.tr("menu_about"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(tr.tr("app_name"))
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(BoxesTab(self), tr.tr("tab_boxes"))
        self.tabs.addTab(ItemsTab(self), tr.tr("tab_items"))
        self.tabs.addTab(HistoryTab(self), tr.tr("tab_history"))
        self.tabs.addTab(StatsTab(self), "Stats")

        layout.addWidget(self.tabs)

        # Setup keyboard shortcuts
        self.setup_shortcuts()

        # Load theme preference
        self.load_theme_preference()

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
        self.logger.info("=== Backup Database Started ===")
        try:
            # Create backup folder if it doesn't exist
            backup_folder = "backup"
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)
                self.logger.info(f"Created backup folder: {backup_folder}")

            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_filename = f"inventory_backup_{timestamp}.db"
            backup_path = os.path.join(backup_folder, backup_filename)
            self.logger.info(f"Backup destination: {backup_path}")

            # Copy the database file
            shutil.copy2("inventory.db", backup_path)
            self.logger.info("Database file copied successfully")

            # Log the backup
            self.log_action(
                action="BACKUP",
                entity_type="DATABASE",
                details=f"Database backed up to {backup_filename}",
            )

            self.logger.info("Showing backup success dialog")
            QMessageBox.information(
                self,
                "Backup Successful",
                f"Database backed up successfully to:\n{backup_path}",
            )
            self.logger.info("=== Backup Database Complete ===")
        except Exception as e:
            self.logger.error(f"Backup failed with error: {str(e)}")
            QMessageBox.critical(
                self, "Backup Failed", f"Failed to backup database:\n{str(e)}"
            )
            self.logger.info("Backup error dialog closed")

    def export_to_csv(self):
        """Export inventory data to CSV file."""
        self.logger.info("=== Export to CSV Started ===")
        # Let user choose file location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            f"inventory_export_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            self.logger.info("Export cancelled by user")
            return

        self.logger.info(f"Export destination: {file_path}")
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(["ID", "Item Name", "Box", "Quantity"])
                self.logger.info("CSV header written")

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
                self.logger.info(f"Retrieved {len(items)} items for export")

                # Write data
                for item in items:
                    writer.writerow([item[0], item[1], item[2] or "N/A", item[3]])

            self.logger.info(f"Wrote {len(items)} items to CSV file")

            # Log the export
            self.log_action(
                action="EXPORT",
                entity_type="INVENTORY",
                details=f"Exported {len(items)} items to CSV",
            )

            self.logger.info("Showing export success dialog")
            QMessageBox.information(
                self,
                "Export Successful",
                f"Data exported successfully to:\n{file_path}",
            )
            self.logger.info("=== Export to CSV Complete ===")
        except Exception as e:
            self.logger.error(f"Export failed with error: {str(e)}")
            QMessageBox.critical(
                self, "Export Failed", f"Failed to export data:\n{str(e)}"
            )
            self.logger.info("Export error dialog closed")

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

                for row_num, row in enumerate(
                    reader, start=2
                ):  # Start at 2 (1 for header)
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
                    + (
                        f"{failed_count} items failed to import."
                        if failed_count > 0
                        else ""
                    ),
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

    def export_import_template(self):
        """Export a CSV template file for importing items."""
        self.logger.info("=== Export Import Template Started ===")

        # Let user choose file location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV Import Template",
            "import_template.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            self.logger.info("Template export cancelled by user")
            return

        self.logger.info(f"Template export destination: {file_path}")

        try:
            # Get current boxes for examples
            self.cursor.execute("SELECT name FROM boxes ORDER BY name LIMIT 3")
            boxes = self.cursor.fetchall()

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(["Item Name", "Box", "Quantity"])
                self.logger.info("CSV template header written")

                # Write example rows
                if boxes:
                    # Use real box names as examples
                    writer.writerow(["Example Item 1", boxes[0][0], "5"])
                    if len(boxes) > 1:
                        writer.writerow(["Example Item 2", boxes[1][0], "10"])
                    if len(boxes) > 2:
                        writer.writerow(["Example Item 3", boxes[2][0], "3"])
                else:
                    # No boxes exist, use placeholder examples
                    writer.writerow(["Example Item 1", "Box Name Here", "5"])
                    writer.writerow(["Example Item 2", "Box Name Here", "10"])
                    writer.writerow(["Example Item 3", "Box Name Here", "3"])

                # Write instructions as comments (Excel/LibreOffice will show these)
                writer.writerow([])
                writer.writerow(["# INSTRUCTIONS:"])
                writer.writerow(["# 1. Replace example rows with your actual items"])
                writer.writerow(["# 2. Item Name: Name of the item (required)"])
                writer.writerow(
                    ["# 3. Box: Must match an existing box name exactly (required)"]
                )
                writer.writerow(
                    ["# 4. Quantity: Number of items, must be 1 or higher (required)"]
                )
                writer.writerow(["# 5. Delete these instruction rows before importing"])
                writer.writerow(
                    ["# 6. Use File -> Import from CSV to import this file"]
                )

                if not boxes:
                    writer.writerow([])
                    writer.writerow(["# WARNING: No boxes found in database!"])
                    writer.writerow(["# Create boxes first before importing items."])

            self.logger.info("Template file created successfully")

            # Log the action
            self.log_action(
                action="EXPORT",
                entity_type="TEMPLATE",
                details="Exported CSV import template",
            )

            # Show success message with instructions
            instruction_text = (
                f"CSV import template saved to:\n{file_path}\n\n"
                "Instructions:\n"
                "1. Open the file in Excel or any spreadsheet editor\n"
                "2. Replace the example rows with your actual items\n"
                "3. Make sure box names match existing boxes exactly\n"
                "4. Delete the instruction rows at the bottom\n"
                "5. Save and use File → Import from CSV to import\n\n"
            )

            if not boxes:
                instruction_text += "⚠️ NOTE: You have no boxes yet!\nCreate boxes first before importing items."

            QMessageBox.information(self, "Template Exported", instruction_text)
            self.logger.info("=== Export Import Template Complete ===")

        except Exception as e:
            self.logger.error(f"Template export failed with error: {str(e)}")
            QMessageBox.critical(
                self, "Export Failed", f"Failed to export template:\n{str(e)}"
            )
            self.logger.info("Template export error dialog closed")

    def show_help(self):
        """Show comprehensive help dialog."""
        self.logger.info("Opening help dialog")
        help_dialog = HelpDialog(self)
        help_dialog.exec()
        self.logger.info("Help dialog closed")

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
            <li>✓ Dark & Light theme support</li>
            <li>✓ Keyboard shortcuts for power users</li>
        </ul>

        <p><b>Database:</b> SQLite</p>
        <p><b>Framework:</b> PyQt6</p>
        <p><b>Press F1 for detailed help</b></p>
        """

        QMessageBox.about(self, f"About {__app_name__}", about_text)

    def get_current_language(self):
        """Get the current language preference."""
        try:
            self.cursor.execute("SELECT value FROM settings WHERE key = 'language'")
            result = self.cursor.fetchone()
            lang = result[0] if result else "en"
            self.logger.info(f"Retrieved language preference from database: {lang}")
            return lang
        except sqlite3.OperationalError:
            self.logger.info("Settings table not found, defaulting to English")
            return "en"

    def load_language_preference(self):
        """Load saved language preference."""
        self.logger.info("Loading language preference...")
        from modules import get_translator

        self.translator = get_translator()
        lang = self.get_current_language()
        success = self.translator.set_language(lang)
        if success:
            self.logger.info(
                f"Language set to: {lang} ({self.translator.LANGUAGES[lang]})"
            )
        else:
            self.logger.warning(f"Failed to set language to: {lang}, using default")

    def save_language_preference(self, language):
        """Save language preference to database."""
        self.logger.info(f"Saving language preference: {language}")
        try:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """
            )
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO settings (key, value) VALUES ('language', ?)
            """,
                (language,),
            )
            self.conn.commit()
            self.logger.info(f"Language preference saved successfully: {language}")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to save language preference: {e}")

    def change_language(self, language_code):
        """Change the application language."""
        self.logger.info(f"User requested language change to: {language_code}")
        from modules import get_translator

        translator = get_translator()

        if translator.set_language(language_code):
            self.save_language_preference(language_code)

            self.logger.info(f"Showing language change confirmation dialog")
            QMessageBox.information(
                self,
                "Language Changed",
                "Language has been changed. Please restart the application for changes to take effect.",
            )
            self.logger.info("Language change dialog closed")

            self.log_action(
                action="LANGUAGE_CHANGE",
                entity_type="SETTINGS",
                details=f"Language changed to {language_code}",
            )

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+F - Focus search in current tab
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.focus_search)

        # Ctrl+N - Add new item/box in current tab
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.add_new_in_current_tab)

        # Ctrl+B - Create backup
        backup_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        backup_shortcut.activated.connect(self.backup_database)

        # Ctrl+E - Export to CSV
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self.export_to_csv)

        # Ctrl+1, Ctrl+2, Ctrl+3, Ctrl+4 - Switch tabs
        tab1_shortcut = QShortcut(QKeySequence("Ctrl+1"), self)
        tab1_shortcut.activated.connect(lambda: self.tabs.setCurrentIndex(0))

        tab2_shortcut = QShortcut(QKeySequence("Ctrl+2"), self)
        tab2_shortcut.activated.connect(lambda: self.tabs.setCurrentIndex(1))

        tab3_shortcut = QShortcut(QKeySequence("Ctrl+3"), self)
        tab3_shortcut.activated.connect(lambda: self.tabs.setCurrentIndex(2))

        tab4_shortcut = QShortcut(QKeySequence("Ctrl+4"), self)
        tab4_shortcut.activated.connect(lambda: self.tabs.setCurrentIndex(3))

        self.logger.info("Keyboard shortcuts configured")

    def focus_search(self):
        """Focus the search box in the current tab."""
        current_tab = self.tabs.currentWidget()
        if hasattr(current_tab, "search_input"):
            current_tab.search_input.setFocus()
            current_tab.search_input.selectAll()
            self.logger.info("Search box focused via keyboard shortcut")

    def add_new_in_current_tab(self):
        """Add new item or box depending on current tab."""
        current_index = self.tabs.currentIndex()
        current_tab = self.tabs.currentWidget()

        if current_index == 0:  # Boxes tab
            if hasattr(current_tab, "add_box"):
                current_tab.add_box()
                self.logger.info("Add box triggered via keyboard shortcut")
        elif current_index == 1:  # Items tab
            if hasattr(current_tab, "add_item"):
                current_tab.add_item()
                self.logger.info("Add item triggered via keyboard shortcut")

    def toggle_theme(self):
        """Toggle between dark and light theme."""
        current_theme = ModernStyle.current_theme
        new_theme = "light" if current_theme == "dark" else "dark"

        ModernStyle.set_theme(new_theme)
        self.setStyleSheet(ModernStyle.get_stylesheet())

        # Update theme action text
        if new_theme == "dark":
            self.theme_action.setText("Switch to Light Theme")
        else:
            self.theme_action.setText("Switch to Dark Theme")

        # Save preference
        self.save_theme_preference(new_theme)

        self.logger.info(f"Theme switched to: {new_theme}")
        self.log_action(
            action="THEME_CHANGE",
            entity_type="SETTINGS",
            details=f"Theme changed to {new_theme}",
        )

        # Inform user
        QMessageBox.information(
            self,
            "Theme Changed",
            f"Theme changed to {new_theme.capitalize()} mode.\nSome elements may require a restart to fully update.",
        )

    def save_theme_preference(self, theme):
        """Save theme preference to database."""
        try:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """
            )
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO settings (key, value) VALUES ('theme', ?)
            """,
                (theme,),
            )
            self.conn.commit()
            self.logger.info(f"Theme preference saved: {theme}")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to save theme preference: {e}")

    def load_theme_preference_initial(self):
        """Load saved theme preference at startup (before UI is created)."""
        try:
            self.cursor.execute("SELECT value FROM settings WHERE key = 'theme'")
            result = self.cursor.fetchone()
            if result:
                theme = result[0]
                ModernStyle.set_theme(theme)
                self.logger.info(f"Loaded theme preference: {theme}")
        except sqlite3.OperationalError:
            self.logger.info("No theme preference found, using default")

    def load_theme_preference(self):
        """Load saved theme preference and update UI."""
        try:
            self.cursor.execute("SELECT value FROM settings WHERE key = 'theme'")
            result = self.cursor.fetchone()
            if result:
                theme = result[0]
                ModernStyle.set_theme(theme)
                if hasattr(self, "theme_action"):
                    if theme == "light":
                        self.theme_action.setText("Switch to Dark Theme")
                    else:
                        self.theme_action.setText("Switch to Light Theme")
                self.logger.info(f"Loaded theme preference: {theme}")
        except sqlite3.OperationalError:
            self.logger.info("No theme preference found, using default")

    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Application closing")
        self.log_action(
            action="SHUTDOWN", entity_type="APPLICATION", details="Application closed"
        )
        self.conn.close()
        event.accept()
