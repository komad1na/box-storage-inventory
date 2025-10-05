# Inventory Manager (PyQt6 + SQLite)

**Version 2.0.0**

A modern desktop inventory management system built with PyQt6 and SQLite. Features a sleek dark theme interface with comprehensive audit logging, transaction history, and data import/export capabilities.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🎯 Features

### Core Functionality

- ✅ **Box Management**: Create, read, update, and delete storage boxes
- ✅ **Item Management**: Track items with quantities assigned to boxes
- ✅ **Search & Filter**: Advanced filtering by name, box, and other criteria
- ✅ **Modern Dark Theme**: Clean, professional interface with custom styling

### Data Management

- 📁 **CSV Import**: Import inventory data with comprehensive validation
  - Pre-import validation checks
  - Preview dialog before committing
  - Error detection and reporting
- 📤 **CSV Export**: Export inventory and audit logs to CSV format
- 💾 **Database Backups**: Automatic backup reminders and manual backup capability
- 🗄️ **SQLite Database**: Reliable persistence with foreign key constraints

### Audit & Logging

- 📝 **Audit Logs**: Complete transaction history with detailed change tracking
- 🕐 **History Tab**: View all operations with filtering by action type and entity
- 📊 **Statistics**: Real-time counts of creates, updates, and deletes
- 📄 **File Logging**: Daily log files with timestamps
- 🔍 **Change Tracking**: Stores before/after values for all updates

### User Experience

- 🎨 **Responsive UI**: Clean table layouts with alternating row colors
- 🔎 **Real-time Search**: Instant filtering as you type
- ⚡ **Quick Actions**: In-table edit and delete buttons
- ⚠️ **Validation**: Input validation with helpful error messages
- 🔔 **Backup Reminders**: Automatic 7-day backup notifications

## 📋 Requirements

- Python 3.10+
- PyQt6

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🚀 Getting Started

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install PyQt6
   ```

### Running the Application

```bash
python main.py
```

Or using the legacy file:

```bash
python inv_pyqt.py
```

## 📖 Usage Guide

### Managing Boxes

1. Navigate to the **Boxes** tab
2. Click **+ Add Box** to create a new storage box
3. Use the search bar to filter boxes
4. Click **Edit** to modify or **Del** to remove a box

### Managing Items

1. Navigate to the **Items** tab
2. Click **+ Add Item** to create a new inventory item
3. Select the box, enter quantity, and item details
4. Use filters to search by item name or box
5. Edit or delete items using the action buttons

### Viewing History

1. Navigate to the **History** tab
2. Filter by action type (CREATE/UPDATE/DELETE)
3. Filter by entity type (ITEM/BOX)
4. Search by entity name
5. View detailed change information with timestamps

### Importing Data

1. Go to **File → Import from CSV**
2. Select a CSV file with columns: `Item Name`, `Box`, `Quantity`
3. Review the preview and validation results
4. Confirm import if no errors

**CSV Format Example:**

```csv
Item Name,Box,Quantity
Screwdriver,Toolbox A,5
Hammer,Toolbox A,2
Nails,Storage 1,100
```

### Exporting Data

- **Export Inventory**: File → Export Inventory to CSV
- **Export Audit Logs**: File → Export Audit Logs to CSV

### Backups

- **Manual Backup**: File → Backup Database
- **Automatic Reminders**: Prompted if no backup in 7 days
- Backups stored in `backup/` folder with timestamps

## 📁 File Structure

```
inventory/
├── main.py                      # Application entry point (NEW)
├── inv_pyqt.py                  # Legacy monolithic file (still works)
├── modules/                     # Modular codebase (NEW)
│   ├── __init__.py             # Package initialization
│   ├── app.py                   # Main application window
│   ├── styles.py                # UI themes and styles
│   ├── dialogs.py               # Dialog windows
│   ├── tabs_items.py            # Items tab
│   ├── tabs_boxes.py            # Boxes tab
│   └── tabs_history.py          # History/audit log tab
├── inventory.db                 # SQLite database (auto-created)
├── backup/                      # Database backups (auto-created)
├── logs/                        # Daily log files (auto-created)
│   └── inventory_YYYY-MM-DD.log
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🗃️ Database Schema

### Tables

**boxes**

- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT NOT NULL)

**items**

- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT NOT NULL)
- `box_id` (INTEGER, FOREIGN KEY → boxes.id)
- `quantity` (INTEGER DEFAULT 1)

**audit_logs**

- `id` (INTEGER PRIMARY KEY)
- `timestamp` (TEXT)
- `action` (TEXT) - CREATE/UPDATE/DELETE/IMPORT/EXPORT/BACKUP/SHUTDOWN
- `entity_type` (TEXT) - ITEM/BOX/INVENTORY/DATABASE/APPLICATION
- `entity_id` (INTEGER)
- `entity_name` (TEXT)
- `details` (TEXT)
- `old_value` (TEXT)
- `new_value` (TEXT)

## 🎨 UI Features

- **Modern Dark Theme**: Custom color scheme with green accents
- **Responsive Tables**: Auto-sizing columns with fixed action columns
- **Color-Coded Actions**: Visual distinction between create (green), update (blue), and delete (red)
- **Inline Editing**: Quick edit/delete buttons in each row
- **No Selection Artifacts**: Clean focus states without distracting borders
- **Consistent Borders**: Uniform gridlines throughout tables

## 🔧 Troubleshooting

### Import Errors

- Ensure CSV has correct headers: `Item Name`, `Box`, `Quantity`
- Boxes must exist before importing items
- Quantities must be positive integers

### Database Issues

- Check that `inventory.db` has write permissions
- Review logs in `logs/` folder for detailed error messages

### Display Issues

- Ensure PyQt6 is properly installed
- Try restarting the application

## 📝 Version History

### Version 2.0.0 (Current)

- ✨ Added comprehensive audit logging system
- ✨ Added History tab with filtering and statistics
- ✨ Added CSV import with validation and preview
- ✨ Added CSV export for both inventory and logs
- ✨ Added file-based logging to daily log files
- ✨ Added version tracking and About dialog
- ✨ **Refactored codebase into modular architecture**
- ✨ Improved UI with consistent borders and focus states
- 📦 **New**: Organized code into `modules/` folder for better maintainability

### Version 1.0.0

- Initial GUI release with basic CRUD operations
- Box and Item management
- Search and filter functionality
- Dark theme UI

### Version 0.5.0

- Initial CLI version with CRUD operations
- Colored console text

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

MIT License - Feel free to use this project for personal or commercial purposes.

## 💡 Tips

- **Backup Regularly**: Use the automatic backup feature to protect your data
- **Review History**: Check the History tab to audit all changes
- **Use Import**: Bulk import items using CSV for faster setup
- **Search Effectively**: Use filters to quickly find items or boxes
- **Export Reports**: Export audit logs for external analysis

---

**Built with ❤️ using PyQt6 and SQLite**
