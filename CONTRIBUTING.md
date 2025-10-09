# Contributing to Inventory Manager

Thank you for your interest in contributing to Inventory Manager! This document provides technical information about the project structure and guidelines for contributing.

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
│   ├── tabs_stats.py            # Statistics tab
│   └── translations.py          # Multi-language support
├── inventory.db                 # SQLite database (auto-created)
├── backup/                      # Database backups (auto-created)
├── logs/                        # Daily log files (auto-created)
│   └── inventory_YYYY-MM-DD.log
├── icon.svg                     # Application icon (SVG)
├── icon.ico                     # Application icon (Windows)
├── requirements.txt             # Python dependencies
├── README.md                    # Project overview
├── CHANGELOG.md                 # Version history
├── LICENSE                      # License information
├── CODE_OF_CONDUCT.md           # Community guidelines
└── CONTRIBUTING.md              # This file
```

## 🗃️ Database Schema

### Tables

**boxes**
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT NOT NULL, max 255 characters)
- `location` (TEXT, max 255 characters) - Physical storage location

**items**
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT NOT NULL, max 255 characters)
- `box_id` (INTEGER, FOREIGN KEY → boxes.id)
- `quantity` (INTEGER DEFAULT 1, CHECK constraint: quantity > 0)

**audit_logs**
- `id` (INTEGER PRIMARY KEY)
- `timestamp` (TEXT) - ISO 8601 format
- `action` (TEXT) - CREATE/UPDATE/DELETE/IMPORT/EXPORT/BACKUP/SHUTDOWN/LANGUAGE_CHANGE
- `entity_type` (TEXT) - ITEM/BOX/INVENTORY/DATABASE/APPLICATION/SETTINGS
- `entity_id` (INTEGER) - ID of affected entity
- `entity_name` (TEXT) - Name of affected entity
- `details` (TEXT) - Additional information
- `old_value` (TEXT) - Previous value (for updates)
- `new_value` (TEXT) - New value (for updates)

**settings**
- `key` (TEXT PRIMARY KEY) - Setting name (e.g., 'language', 'theme')
- `value` (TEXT) - Setting value

### Database Indexes

For optimal search performance:

- `idx_boxes_name` - Index on boxes.name
- `idx_boxes_location` - Index on boxes.location
- `idx_items_name` - Index on items.name
- `idx_items_box_id` - Index on items.box_id (foreign key)

### Constraints

- **Foreign Keys**: Enabled for referential integrity
- **Items quantity**: Must be greater than 0 (database-level CHECK constraint)
- **Names and locations**: Maximum 255 characters (validated at UI and database level)
- **Cascade Delete**: Deleting a box deletes all its items

## 🏗️ Architecture

### Module Responsibilities

- **app.py**: Main application window, menu bar, database setup, keyboard shortcuts
- **tabs_*.py**: Individual tab implementations (boxes, items, history, stats)
- **dialogs.py**: Modal dialogs (add/edit forms, import preview, help)
- **styles.py**: Theme management (dark/light mode), color constants
- **translations.py**: Multi-language support, translation strings

### Design Patterns

- **Separation of Concerns**: Each module has a specific responsibility
- **Observer Pattern**: UI refreshes when data changes
- **Factory Pattern**: Dialog creation and initialization
- **Singleton Pattern**: Translator instance (global state)

## 🌍 Adding Translations

To add a new language or update translations:

1. Open `modules/translations.py`
2. Add language code to `LANGUAGES` dictionary:
   ```python
   'xx': 'Language Name',
   ```
3. Add translations for all keys in `STRINGS` dictionary:
   ```python
   'key_name': {
       'en': 'English text',
       'sr': 'Serbian text',
       'xx': 'Your translation',
   },
   ```
4. Test by changing language in the application

### Translation Guidelines

- Keep translations concise for UI elements
- Maintain consistent terminology across the application
- Use formal/polite tone for user-facing messages
- Test with different character sets (Latin, Cyrillic, etc.)

## 🎨 Adding Themes

To modify or add themes:

1. Open `modules/styles.py`
2. Update color constants in `DARK` or `LIGHT` dictionaries
3. Ensure sufficient contrast for accessibility
4. Test all UI components with the new colors

### Theme Color Keys

- `BACKGROUND`: Main background color
- `SURFACE`: Card/panel background
- `PRIMARY`: Primary action color (buttons, highlights)
- `DANGER`: Delete/warning actions
- `TEXT`: Primary text color
- `TEXT_SECONDARY`: Secondary/muted text
- `BORDER`: Border and divider color
- `HEADER`: Table header background

## 🧪 Testing

### Manual Testing Checklist

Before submitting changes:

- [ ] Test all CRUD operations (Create, Read, Update, Delete)
- [ ] Verify data validation (empty names, invalid quantities)
- [ ] Test CSV import/export functionality
- [ ] Check keyboard shortcuts work correctly
- [ ] Test theme toggle (dark/light)
- [ ] Verify translations for all languages
- [ ] Test with empty database and populated database
- [ ] Check audit log entries are created correctly
- [ ] Verify backup functionality
- [ ] Test on Windows (primary platform)

### Common Test Scenarios

1. **Box Management**: Create box with location, edit name/location, delete box with items
2. **Item Management**: Add item to box, change quantity, move to different box, delete
3. **Search/Filter**: Test search in all tabs, verify case-insensitive matching
4. **Import**: Valid CSV, invalid CSV, CSV with missing boxes, CSV with errors
5. **Export**: Export inventory, export audit logs, verify CSV format
6. **Language**: Switch language, verify UI updates, restart application

## 📝 Code Style

- Follow PEP 8 guidelines for Python code
- Use descriptive variable and function names
- Add docstrings for classes and complex functions
- Keep functions focused and concise
- Use type hints where appropriate
- Add comments for complex logic

### Example

```python
def calculate_total_quantity(box_id: int) -> int:
    """Calculate total quantity of all items in a box.

    Args:
        box_id: The ID of the box

    Returns:
        Total quantity of items in the box
    """
    cursor.execute(
        "SELECT COALESCE(SUM(quantity), 0) FROM items WHERE box_id = ?",
        (box_id,)
    )
    return cursor.fetchone()[0]
```

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Version**: Application version (see Help → About)
2. **Platform**: Operating system and version
3. **Steps to Reproduce**: Detailed steps to recreate the issue
4. **Expected Behavior**: What you expected to happen
5. **Actual Behavior**: What actually happened
6. **Logs**: Relevant entries from `logs/inventory_YYYY-MM-DD.log`
7. **Screenshots**: If applicable

## 💡 Feature Requests

When requesting features:

1. **Use Case**: Describe the problem you're trying to solve
2. **Proposed Solution**: Your idea for solving it
3. **Alternatives**: Other approaches you've considered
4. **Impact**: How this would improve the application

## 🔧 Development Setup

### Prerequisites

- Python 3.13+
- PyQt6
- Git (for version control)

### Setup Steps

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python gui.py
   ```
4. Check logs for any startup errors

### Database Migrations

When modifying the database schema:

1. Update `setup_database()` in `modules/app.py`
2. Use `IF NOT EXISTS` for new tables/columns
3. Test migration with existing database
4. Document changes in CHANGELOG.md

## 📦 Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### PR Guidelines

- Provide clear description of changes
- Reference related issues
- Update documentation if needed
- Ensure code follows style guidelines
- Test thoroughly before submitting

## 📄 License Compliance

This project is licensed under **CC BY-NC-SA 4.0** (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International).

When contributing:

- Your contributions will be licensed under the same terms
- Do not include code with incompatible licenses
- Attribute any third-party code appropriately
- Maintain the non-commercial nature of the project

## 🙏 Recognition

Contributors will be recognized in:

- CHANGELOG.md for significant features
- Comments in code for specific implementations
- GitHub contributors page

Thank you for contributing to Inventory Manager!
