# Inventory Manager - Help

## Getting Started

Welcome to **Inventory Manager**! This application helps you organize and track your inventory using a simple box-based system.

### Basic Concepts

- **Boxes**: Storage containers where you keep your items (e.g., "Toolbox", "Kitchen Cabinet")
- **Items**: Individual things you want to track, stored in boxes
- **Location**: Physical place where a box is stored (e.g., "Garage Shelf 2")

### First Steps

1. **Create Boxes**: Start by adding boxes that represent your storage containers
2. **Add Items**: Then add items to those boxes with their quantities
3. **Search & Filter**: Use the search bar to quickly find what you need

---

## Features

### Box Management
- Create boxes with names and locations
- Edit box details anytime
- Delete boxes (warning: this deletes all items inside!)
- Search boxes by name or location

### Item Management
- Add items to boxes with quantities
- Move items between boxes
- Update quantities as you use items
- Delete items when no longer needed
- Filter items by box or search by name

### History & Audit
- View complete history of all changes
- Filter by action type (Create/Update/Delete)
- Search by item or box name
- Track who changed what and when

### Statistics
- View total boxes, items, and quantities
- See charts showing items per box
- Identify which boxes have the most items
- Monitor your inventory trends

---

## Keyboard Shortcuts

Speed up your workflow with these shortcuts:

- **Ctrl+F** - Focus search box in current tab
- **Ctrl+N** - Add new box/item (context-aware)
- **Ctrl+B** - Create database backup
- **Ctrl+E** - Export inventory to CSV
- **Ctrl+T** - Toggle dark/light theme
- **Ctrl+1** - Switch to Boxes tab
- **Ctrl+2** - Switch to Items tab
- **Ctrl+3** - Switch to History tab
- **Ctrl+4** - Switch to Statistics tab
- **F1** - Open this help dialog

---

## Data Management

### Importing Data
1. Go to **Help → Export CSV Import Template**
2. Fill in the template with your data
3. Go to **File → Import from CSV**
4. Review the preview and confirm

**CSV Format:**
```
Item Name,Box,Quantity
Screwdriver,Toolbox,5
Hammer,Toolbox,2
```

### Exporting Data
- **File → Export Inventory to CSV** - Export all items and boxes
- **File → Export Audit Logs to CSV** - Export complete history

### Backups
- **File → Backup Database** - Create manual backup
- Automatic reminders every 7 days
- Backups saved in `backup/` folder

---

## Tips & Tricks

### Organization
- Use descriptive box names (e.g., "Kitchen Drawer 3" instead of just "Drawer")
- Add locations to remember where boxes are stored
- Group similar items in the same box

### Searching
- Search works across box names, item names, and locations
- Use filters to narrow down results
- Clear filters to see all items again

### Themes
- Press **Ctrl+T** to switch between dark and light themes
- Your theme preference is saved automatically

### Languages
- Change language via **Language** menu
- Restart application after changing language
- 6 languages available: English, Serbian, German, Spanish, French, Italian

### Performance
- Database is indexed for fast searching
- Regular backups protect your data
- Logs stored daily in `logs/` folder

---

## Troubleshooting

### Import Issues
- Ensure CSV has correct headers: `Item Name`, `Box`, `Quantity`
- Create boxes before importing items
- Quantities must be positive numbers

### Can't Find Items
- Check if filters are active (click "Clear Filters")
- Try searching in different tabs
- Verify box exists in Boxes tab

### Application Issues
- Check `logs/` folder for error messages
- Create a backup before making major changes
- Restart application if interface seems stuck

---

**Need more help?** Check out the project documentation or report issues on GitHub.

**Version**: 2.3.3 | **Developer**: Nemanja Komadina
