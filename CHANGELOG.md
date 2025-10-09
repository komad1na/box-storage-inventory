# Changelog

All notable changes to the Inventory Manager project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.1] - 2025-10-09

### Added
- 📄 **CHANGELOG.md**: Comprehensive version history and change documentation
- 📜 **LICENSE**: Creative Commons BY-NC-SA 4.0 license (non-commercial use)
- 🤝 **CODE_OF_CONDUCT.md**: Community guidelines and contribution standards

### Changed
- 📖 **README.md**: Restructured to reference separate CHANGELOG and LICENSE files
- 📖 **README.md**: Updated license information to reflect CC BY-NC-SA 4.0

## [2.2.0] - 2025-10-09

### Added
- 🎨 **Dark & Light Themes**: Toggle between themes with Ctrl+T, preference saved automatically
- ⌨️ **Keyboard Shortcuts**: 8 shortcuts for power users (Ctrl+F, N, B, E, T, 1-4, F1)
- 📖 **Comprehensive Help System**: Built-in documentation with 5 sections (Getting Started, Shortcuts, Features, Tips, Database Info)
- 📊 **Statistics Dashboard**: New Stats tab with inventory analytics and charts
  - Summary cards showing total boxes, items, and quantities
  - Bar charts for items per box and quantity per box
  - Flat, minimalistic design matching app theme
- 📄 **CSV Import Template Export**: Generate template files with real box names as examples
- 🗄️ **Database Indexes**: Performance optimization for searches (boxes.name, items.name, locations, box_id)
- ✅ **Enhanced Data Validation**: Input validation for names (max 255 chars), quantities (>0), required fields
- 🖼️ **Custom Application Icon**: Storage unit themed SVG/ICO icon
- 🔧 **Database Constraints**: Quantity check constraint at database level

### Improved
- 📊 **Enhanced Logging**: Theme changes, help dialog usage, template exports
- 🎨 **Refined Light Theme**: Professional color palette for better readability
- ⚡ **Better Performance**: Database indexes speed up search operations

## [2.1.0] - 2025-10-07

### Added
- 🌍 **Multi-language Support**: 6 languages (English, Serbian, German, Spanish, French, Italian)
- 📝 **Comprehensive Verbose Logging**: Track all application operations
- 📍 **Box Location Tracking**: Store physical location of boxes
- 🎨 **Translated UI**: All menus, tabs, and buttons support multiple languages
- 🔍 **Enhanced Search**: Filter boxes by both name and location
- 📊 **Improved Logging**: Database operations, dialog interactions, language changes

### Improved
- ✨ **Better Developer Experience**: Detailed logs for debugging and auditing

## [2.0.0] - 2025-10-05

### Added
- ✨ **Comprehensive Audit Logging System**: Track all changes to boxes and items
- ✨ **History Tab**: View audit logs with filtering and statistics
- ✨ **CSV Import**: Bulk import with validation and preview
- ✨ **CSV Export**: Export inventory and audit logs to CSV
- ✨ **File-based Logging**: Daily log files for troubleshooting
- ✨ **Version Tracking**: About dialog with version information
- ✨ **Modular Architecture**: Refactored codebase into `modules/` folder

### Improved
- 🎨 **UI Consistency**: Consistent borders and focus states across tables
- 📦 **Better Maintainability**: Organized code structure for easier development

## [1.0.0] - 2025-10-01

### Added
- 🎨 **GUI Application**: PyQt6-based graphical interface
- 📦 **Box Management**: Create, read, update, and delete storage boxes
- 📋 **Item Management**: Track items with quantities assigned to boxes
- 🔍 **Search & Filter**: Real-time filtering by name, box, location
- 🌑 **Dark Theme UI**: Modern dark color scheme with green accents

### Changed
- Migrated from CLI to GUI application

## [0.5.0] - 2025-09-28

### Added
- 💻 **CLI Application**: Command-line interface for inventory management
- 🎨 **Colored Console Text**: Visual distinction for different operations
- 📦 **Basic CRUD Operations**: Create, read, update, delete boxes and items
- 🗄️ **SQLite Database**: Persistent storage for inventory data

---

## Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities
