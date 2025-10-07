# Inventory Manager (PyQt6 + SQLite)

**Version 2.1.0** | **Developer: Nemanja Komadina**

A modern desktop inventory management system built with PyQt6 and SQLite. Features a sleek dark theme interface with comprehensive audit logging, transaction history, multi-language support, and verbose logging.

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🎯 Features

### Core Functionality

- ✅ **Box Management**: Create, read, update, and delete storage boxes with location tracking
- ✅ **Item Management**: Track items with quantities assigned to boxes
- ✅ **Search & Filter**: Advanced filtering by name, box, location, and other criteria
- ✅ **Modern Dark Theme**: Clean, professional interface with custom styling
- 🌍 **Multi-Language Support**: 6 languages (English, Serbian, German, Spanish, French, Italian)

### Data Management

- 📁 **CSV Import**: Import inventory data with comprehensive validation
  - Pre-import validation checks
  - Preview dialog before committing
  - Error detection and reporting
- 📤 **CSV Export**: Export inventory and audit logs to CSV format
- 💾 **Database Backups**: Automatic backup reminders and manual backup capability
- 🗄️ **SQLite Database**: Reliable persistence with foreign key constraints
- 📍 **Location Tracking**: Track physical storage locations for boxes

### Audit & Logging

- 📝 **Audit Logs**: Complete transaction history with detailed change tracking
- 🕐 **History Tab**: View all operations with filtering by action type and entity
- 📊 **Statistics**: Real-time counts of creates, updates, and deletes
- 📄 **Verbose File Logging**: Comprehensive daily log files with timestamps
  - Application lifecycle events
  - Database operations
  - Dialog interactions
  - User actions
  - Language changes
  - Export/Import operations
  - Error tracking
- 🔍 **Change Tracking**: Stores before/after values for all updates

### User Experience

- 🎨 **Responsive UI**: Clean table layouts with alternating row colors
- 🔎 **Real-time Search**: Instant filtering as you type
- ⚡ **Quick Actions**: In-table edit and delete buttons
- ⚠️ **Validation**: Input validation with helpful error messages
- 🔔 **Backup Reminders**: Automatic 7-day backup notifications
- 🌐 **Language Selector**: Easy language switching with persistence

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
python gui.py
```

## 📖 Usage Guide

### Managing Boxes

1. Navigate to the **Boxes** tab
2. Click **+ Add Box** to create a new storage box
3. Enter box name and location (e.g., "Garage Shelf 2")
4. Use the search bar to filter boxes by name or location
5. Click **Edit** to modify or **Del** to remove a box

### Managing Items

1. Navigate to the **Items** tab
2. Click **+ Add Item** to create a new inventory item
3. Select the box, enter quantity, and item details
4. Use filters to search by item name or box
5. Edit or delete items using the action buttons

### Changing Language

1. Click **Language** in the menu bar
2. Select your preferred language
3. Restart the application for changes to take effect
4. Your language preference is saved automatically

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
├── gui.py                       # Application entry point
├── cli.py                       # CLI version (legacy)
├── modules/                     # Modular codebase
│   ├── __init__.py             # Package initialization
│   ├── app.py                   # Main application window
│   ├── styles.py                # UI themes and styles
│   ├── dialogs.py               # Dialog windows
│   ├── tabs_items.py            # Items tab
│   ├── tabs_boxes.py            # Boxes tab
│   ├── tabs_history.py          # History/audit log tab
│   └── translations.py          # Multi-language support
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
- `location` (TEXT) - Physical storage location

**items**

- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT NOT NULL)
- `box_id` (INTEGER, FOREIGN KEY → boxes.id)
- `quantity` (INTEGER DEFAULT 1)

**audit_logs**

- `id` (INTEGER PRIMARY KEY)
- `timestamp` (TEXT)
- `action` (TEXT) - CREATE/UPDATE/DELETE/IMPORT/EXPORT/BACKUP/SHUTDOWN/LANGUAGE_CHANGE
- `entity_type` (TEXT) - ITEM/BOX/INVENTORY/DATABASE/APPLICATION/SETTINGS
- `entity_id` (INTEGER)
- `entity_name` (TEXT)
- `details` (TEXT)
- `old_value` (TEXT)
- `new_value` (TEXT)

**settings**

- `key` (TEXT PRIMARY KEY)
- `value` (TEXT)

## 🌍 Supported Languages

- 🇬🇧 English
- 🇷🇸 Српски (Serbian)
- 🇩🇪 Deutsch (German)
- 🇪🇸 Español (Spanish)
- 🇫🇷 Français (French)
- 🇮🇹 Italiano (Italian)

## 🎨 UI Features

- **Modern Dark Theme**: Custom color scheme with green accents
- **Responsive Tables**: Auto-sizing columns with fixed action columns
- **Color-Coded Actions**: Visual distinction between create (green), update (blue), and delete (red)
- **Inline Editing**: Quick edit/delete buttons in each row
- **No Selection Artifacts**: Clean focus states without distracting borders
- **Consistent Borders**: Uniform gridlines throughout tables
- **Translated UI**: All menus, buttons, and labels support multiple languages

## 📊 Logging Features

The application logs comprehensive information to help track all operations:

### What Gets Logged

- ✅ Application startup and shutdown
- ✅ Database initialization and migrations
- ✅ Database statistics (box count, item count, log count)
- ✅ Language changes and preferences
- ✅ All dialog opens (Add/Edit Item, Add/Edit Box)
- ✅ Dialog save operations with full data
- ✅ Validation errors and warnings
- ✅ Backup operations (folder creation, file copying)
- ✅ CSV export operations (file writing, item counts)
- ✅ CSV import previews and validations
- ✅ All CRUD operations (Create, Read, Update, Delete)
- ✅ Error conditions and exceptions

### Log Locations

- **File**: `logs/inventory_YYYY-MM-DD.log` (daily rotation)
- **Console**: stdout (real-time viewing during development)
- **Encoding**: UTF-8 (supports all languages including Cyrillic)

### Log Format

```
YYYY-MM-DD HH:MM:SS,mmm - LEVEL - MESSAGE
```

**Example:**

```
2025-10-07 15:15:42,318 - INFO - === Database Setup Started ===
2025-10-07 15:15:42,319 - INFO - Database statistics: 5 boxes, 102 items, 69 audit logs
2025-10-07 15:15:42,319 - INFO - Language set to: en (English)
```

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

### Language Not Changing

- Make sure to restart the application after changing language
- Check `logs/` folder for language change confirmation
- Language preference is stored in the database `settings` table

## 📝 Version History

### Version 2.1.0 (Current)

- 🌍 **Added multi-language support**: 6 languages with persistent preferences
- 📝 **Added comprehensive verbose logging**: Track all application operations
- 📍 **Added box location tracking**: Store physical location of boxes
- 🎨 **Updated UI with translations**: All menus, tabs, and buttons support multiple languages
- 🔍 **Enhanced search**: Filter boxes by both name and location
- 📊 **Improved logging**: Database operations, dialog interactions, language changes
- ✨ **Better developer experience**: Detailed logs for debugging and auditing

### Version 2.0.0

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
- **Check Logs**: Review daily log files in `logs/` for troubleshooting
- **Track Locations**: Use the location field to remember where boxes are stored
- **Switch Languages**: Use the Language menu to change the interface language

---

**Built with ❤️ by Nemanja Komadina using PyQt6 and SQLite**
