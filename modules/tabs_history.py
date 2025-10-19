"""
History Tab
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLineEdit,
    QLabel,
    QComboBox,
    QHeaderView,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from .styles import ModernStyle
from . import get_translator


class HistoryTab(QWidget):
    """Tab for viewing audit logs and transaction history."""

    def __init__(self, parent):
        super().__init__(parent)
        self.translator = get_translator()
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Filter bar
        filter_layout = QHBoxLayout()

        # Action filter
        self.action_filter = QComboBox()
        self.action_filter.addItem("All Actions", None)
        self.action_filter.addItem("CREATE", "CREATE")
        self.action_filter.addItem("UPDATE", "UPDATE")
        self.action_filter.addItem("DELETE", "DELETE")
        self.action_filter.currentIndexChanged.connect(self.load_logs)
        filter_layout.addWidget(QLabel("Action:"))
        filter_layout.addWidget(self.action_filter, 1)

        # Entity type filter
        self.entity_filter = QComboBox()
        self.entity_filter.addItem("All Types", None)
        self.entity_filter.addItem("ITEM", "ITEM")
        self.entity_filter.addItem("BOX", "BOX")
        self.entity_filter.currentIndexChanged.connect(self.load_logs)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.entity_filter, 1)

        # Search by entity name
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.translator.tr('placeholder_search_history'))
        self.search_input.textChanged.connect(self.load_logs)
        filter_layout.addWidget(self.search_input, 2)

        clear_btn = QPushButton(self.translator.tr('btn_clear_filters'))
        clear_btn.setProperty("class", "neutral")
        clear_btn.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_btn, 1)

        refresh_btn = QPushButton(self.translator.tr('btn_refresh'))
        refresh_btn.clicked.connect(self.load_logs)
        filter_layout.addWidget(refresh_btn, 1)

        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            self.translator.tr('label_timestamp'),
            self.translator.tr('label_action'),
            self.translator.tr('label_type'),
            self.translator.tr('label_entity'),
            self.translator.tr('label_details'),
            self.translator.tr('header_id')
        ])

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch
        )  # Details stretches
        self.table.setColumnWidth(0, 150)  # Timestamp
        self.table.setColumnWidth(1, 140)  # Action
        self.table.setColumnWidth(2, 100)  # Type
        self.table.setColumnWidth(3, 180)  # Entity
        self.table.setColumnWidth(5, 50)  # ID

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)

        layout.addWidget(self.table)

        # Stats summary
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(
            f"color: {ModernStyle.TEXT_SECONDARY}; padding: 5px;"
        )
        layout.addWidget(self.stats_label)

        self.setLayout(layout)
        self.load_logs()

    def clear_filters(self):
        """Clear all filters."""
        self.action_filter.setCurrentIndex(0)
        self.entity_filter.setCurrentIndex(0)
        self.search_input.clear()

    def load_logs(self):
        """Load audit logs into table."""
        self.table.setRowCount(0)

        query = """
            SELECT timestamp, action, entity_type, entity_name, details, entity_id
            FROM audit_logs
            WHERE 1=1
        """
        params = []

        # Apply filters
        action = self.action_filter.currentData()
        if action:
            query += " AND action = ?"
            params.append(action)

        entity_type = self.entity_filter.currentData()
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)

        search_text = self.search_input.text().strip()
        if search_text:
            query += " AND entity_name LIKE ?"
            params.append(f"%{search_text}%")

        query += " ORDER BY id DESC LIMIT 1000"

        self.parent.cursor.execute(query, params)
        logs = self.parent.cursor.fetchall()

        for row_idx, (
            timestamp,
            action,
            entity_type,
            entity_name,
            details,
            entity_id,
        ) in enumerate(logs):
            self.table.insertRow(row_idx)

            # Timestamp
            time_item = QTableWidgetItem(timestamp)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, time_item)

            # Action with color coding
            action_item = QTableWidgetItem(action)
            action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if action == "CREATE":
                action_item.setForeground(QColor(ModernStyle.PRIMARY))
            elif action == "UPDATE":
                action_item.setForeground(QColor("#3498db"))
            elif action == "DELETE":
                action_item.setForeground(QColor(ModernStyle.DANGER))
            self.table.setItem(row_idx, 1, action_item)

            # Type
            type_item = QTableWidgetItem(entity_type)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 2, type_item)

            # Entity name
            entity_item = QTableWidgetItem(entity_name or "N/A")
            entity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, entity_item)

            # Details
            details_item = QTableWidgetItem(details or "")
            details_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(row_idx, 4, details_item)

            # ID
            id_item = QTableWidgetItem(str(entity_id) if entity_id else "")
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 5, id_item)

        # Update stats
        self.update_stats()

    def update_stats(self):
        """Update statistics label."""
        # Count by action type
        self.parent.cursor.execute(
            """
            SELECT action, COUNT(*) FROM audit_logs GROUP BY action
        """
        )
        stats = dict(self.parent.cursor.fetchall())

        total = sum(stats.values())
        creates = stats.get("CREATE", 0)
        updates = stats.get("UPDATE", 0)
        deletes = stats.get("DELETE", 0)

        self.stats_label.setText(
            f"Total Logs: {total} | Creates: {creates} | Updates: {updates} | Deletes: {deletes}"
        )
