#!/usr/bin/env python3
"""
Inventory Manager
Version: 2.0.0
Developer: Nemanja Komadina

A modern desktop inventory management system with audit logging and transaction history.
"""

import sys
from PyQt6.QtWidgets import QApplication

from modules.app import InventoryApp


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create and show main window
    window = InventoryApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
