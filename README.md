# Inventory Manager (PyQt6 + SQLite)

**Version 2.3.3** | **Developer: Nemanja Komadina**

A modern desktop inventory management system built with PyQt6 and SQLite. Features dark/light themes, keyboard shortcuts, comprehensive help system, audit logging, multi-language support, and data validation.

![Version](https://img.shields.io/badge/version-2.3.3-blue)
![Python](https://img.shields.io/badge/python-3.13+-green)
![License](https://img.shields.io/badge/license-CC--BY--NC--SA--4.0-orange)

## 🎯 Features

### Core Functionality

- ✅ **Box Management**: Create, read, update, and delete storage boxes with location tracking
- ✅ **Item Management**: Track items with quantities assigned to boxes
- ✅ **Search & Filter**: Advanced filtering by name, box, location with database indexes for performance
- 🎨 **Dark & Light Themes**: Toggle between themes with saved preference (Ctrl+T)
- ⌨️ **Keyboard Shortcuts**: 8 shortcuts for power users (Ctrl+F, Ctrl+N, Ctrl+B, etc.)
- 🌍 **Multi-Language Support**: 6 languages (English, Serbian, German, Spanish, French, Italian)
- ❓ **Comprehensive Help**: Built-in help system with 5 sections (F1)

### Data Management

- 📁 **CSV Import**: Import inventory data with comprehensive validation
  - Pre-import validation checks
  - Preview dialog before committing
  - Error detection and reporting
  - **NEW:** Export import template with real box names as examples
- 📤 **CSV Export**: Export inventory and audit logs to CSV format
- 💾 **Database Backups**: Automatic backup reminders and manual backup capability
- 🗄️ **SQLite Database**: Reliable persistence with foreign key constraints and indexes
- 📍 **Location Tracking**: Track physical storage locations for boxes
- ✅ **Data Validation**: Input validation prevents empty names, zero quantities, and invalid data

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
- 🌗 **Theme Toggle**: Dark and light themes with persistent preference
- 🔎 **Real-time Search**: Instant filtering as you type with Ctrl+F shortcut
- ⚡ **Quick Actions**: In-table edit and delete buttons
- ⚠️ **Validation**: Input validation with helpful error messages (max length, required fields)
- 🔔 **Backup Reminders**: Automatic 7-day backup notifications
- 🌐 **Language Selector**: Easy language switching with persistence
- ⌨️ **Keyboard Navigation**: Full keyboard support with 8 shortcuts
- 📖 **Integrated Help**: Press F1 for comprehensive documentation

## ⌨️ Keyboard Shortcuts

Speed up your workflow with these keyboard shortcuts:

| Shortcut | Action       | Description                       |
| -------- | ------------ | --------------------------------- |
| `Ctrl+F` | Focus Search | Jump to search box in current tab |
| `Ctrl+N` | Add New      | Add new box/item (context-aware)  |
| `Ctrl+B` | Backup       | Create database backup            |
| `Ctrl+E` | Export       | Export inventory to CSV           |
| `Ctrl+T` | Toggle Theme | Switch between dark/light theme   |
| `Ctrl+1` | Boxes Tab    | Switch to Boxes tab               |
| `Ctrl+2` | Items Tab    | Switch to Items tab               |
| `Ctrl+3` | History Tab  | Switch to History tab             |
| `F1`     | Help         | Open comprehensive help dialog    |

## 📋 Requirements

- Python 3.13+
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

#### Getting a Template

1. Go to **Help → Export CSV Import Template**
2. Save the template file
3. The template includes:
   - Correct headers
   - Example rows using your actual box names
   - Detailed instructions as comments

#### Importing Your Data

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

## 🌍 Supported Languages

- 🇬🇧 English
- 🇷🇸 Српски (Serbian)
- 🇩🇪 Deutsch (German)
- 🇪🇸 Español (Spanish)
- 🇫🇷 Français (French)
- 🇮🇹 Italiano (Italian)

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

## 🔧 Troubleshooting

### Import Errors

- Ensure CSV has correct headers: `Item Name`, `Box`, `Quantity`
- Boxes must exist before importing items
- Quantities must be positive integers

### Database Issues

- Check that `inventory.db` has write permissions
- Review logs in `logs/` folder for detailed error messages

## 📝 Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and changes.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Project structure and architecture
- Database schema details
- Development setup instructions
- Code style guidelines
- Pull request process

Also read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## 📄 License

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

See [LICENSE](LICENSE) for full details.

## 💡 Tips

- **Press F1 for Help**: Comprehensive built-in documentation with all features explained
- **Use Keyboard Shortcuts**: Speed up workflow with Ctrl+F (search), Ctrl+N (add), Ctrl+B (backup)
- **Toggle Theme**: Press Ctrl+T to switch between dark and light themes
- **Get Import Template**: Help → Export CSV Import Template for easy bulk imports
- **Backup Regularly**: Use the automatic backup feature to protect your data
- **Review History**: Check the History tab to audit all changes
- **Search Effectively**: Use filters and Ctrl+F to quickly find items or boxes
- **Export Reports**: Export audit logs for external analysis
- **Check Logs**: Review daily log files in `logs/` for troubleshooting
- **Track Locations**: Use the location field to remember where boxes are stored
- **Switch Languages**: Use the Language menu to change the interface language

---

**Built with ❤️ by Nemanja Komadina using PyQt6 and SQLite**
