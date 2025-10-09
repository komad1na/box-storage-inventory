"""
Statistics Tab
"""

import matplotlib

matplotlib.use("Qt5Agg")  # Use Qt backend for matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QGridLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .styles import ModernStyle
from . import get_translator


class StatsTab(QWidget):
    """Tab for displaying inventory statistics and charts."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.translator = get_translator()
        self.setup_ui()

    def setup_ui(self):
        """Setup the statistics UI."""
        # Set background color to match app
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {ModernStyle.BACKGROUND};
            }}
        """
        )
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel(self.translator.tr('stats_title'))
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        main_layout.addWidget(title)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            f"""
            QScrollArea {{
                background-color: {ModernStyle.BACKGROUND};
                border: none;
            }}
        """
        )

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Summary cards with flat minimalistic design
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)

        self.total_boxes_card = self.create_stat_card(
            self.translator.tr('stats_total_boxes'), "0", ModernStyle.PRIMARY
        )
        self.total_items_card = self.create_stat_card(self.translator.tr('stats_total_items'), "0", "#0d6efd")
        self.total_quantity_card = self.create_stat_card(
            self.translator.tr('stats_total_quantity'), "0", "#6610f2"
        )

        summary_layout.addWidget(self.total_boxes_card)
        summary_layout.addWidget(self.total_items_card)
        summary_layout.addWidget(self.total_quantity_card)
        summary_layout.addStretch()

        content_layout.addLayout(summary_layout)

        # Add spacing between stats and charts
        content_layout.addSpacing(25)

        # Charts section - only bar charts
        charts_layout = QGridLayout()
        charts_layout.setSpacing(15)

        # Items per box chart
        self.items_per_box_canvas = self.create_chart()
        items_chart_container = self.create_chart_container(self.items_per_box_canvas)
        charts_layout.addWidget(items_chart_container, 0, 0)

        # Quantity per box chart
        self.quantity_per_box_canvas = self.create_chart()
        quantity_chart_container = self.create_chart_container(
            self.quantity_per_box_canvas
        )
        charts_layout.addWidget(quantity_chart_container, 0, 1)

        content_layout.addLayout(charts_layout)
        content_layout.addStretch()

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

        # Load initial data
        print("StatsTab: Loading initial statistics...")
        self.refresh_stats()
        print("StatsTab: Initial statistics loaded")

    def create_stat_card(self, title, value, color):
        """Create a flat minimalistic statistics card widget."""
        card = QFrame()

        # Simple flat design without padding in stylesheet
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {ModernStyle.SURFACE};
                border: 1px solid {ModernStyle.BORDER};
                border-radius: 8px;
            }}
        """
        )
        card.setMinimumWidth(200)
        card.setMaximumWidth(250)
        card.setFixedHeight(120)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 18, 20, 18)

        # Title label
        title_label = QLabel(title.upper())
        title_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ModernStyle.TEXT_SECONDARY}; border: none;")
        layout.addWidget(title_label)

        # Value label
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 38, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        layout.addWidget(value_label)

        # Color bar
        bar = QFrame()
        bar.setFixedHeight(4)
        bar.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
        layout.addWidget(bar)

        layout.addStretch()

        # Store references
        card.value_label = value_label
        card.title_label = title_label
        card.color_bar = bar
        card.card_color = color

        return card

    def create_chart(self):
        """Create a matplotlib figure canvas."""
        figure = Figure(figsize=(6, 4.5), facecolor="none")
        canvas = FigureCanvas(figure)
        canvas.setMinimumHeight(360)
        return canvas

    def create_chart_container(self, canvas):
        """Create a container frame with border for the chart."""
        container = QFrame()
        container.setStyleSheet(
            f"""
            QFrame {{
                background-color: {ModernStyle.SURFACE};
                border: 1px solid {ModernStyle.BORDER};
                border-radius: 8px;
                padding: 10px;
            }}
        """
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(canvas)

        return container

    def refresh_stats(self):
        """Refresh all statistics and charts."""
        try:
            # Get statistics from database
            stats = self.get_statistics()

            print(
                f"Stats loaded: Boxes={stats['total_boxes']}, Items={stats['total_items']}, Qty={stats['total_quantity']}"
            )

            # Update summary cards
            self.total_boxes_card.value_label.setText(str(stats["total_boxes"]))
            self.total_items_card.value_label.setText(str(stats["total_items"]))
            self.total_quantity_card.value_label.setText(str(stats["total_quantity"]))

            # Force repaint
            self.total_boxes_card.update()
            self.total_items_card.update()
            self.total_quantity_card.update()

            # Update charts
            self.update_items_per_box_chart(stats["items_per_box"])
            self.update_quantity_per_box_chart(stats["quantity_per_box"])
        except Exception as e:
            print(f"Error refreshing stats: {e}")
            import traceback

            traceback.print_exc()

    def get_statistics(self):
        """Get statistics from database."""
        stats = {}

        # Total boxes
        self.parent.cursor.execute("SELECT COUNT(*) FROM boxes")
        stats["total_boxes"] = self.parent.cursor.fetchone()[0]

        # Total items (unique items)
        self.parent.cursor.execute("SELECT COUNT(*) FROM items")
        stats["total_items"] = self.parent.cursor.fetchone()[0]

        # Total quantity (sum of all quantities)
        self.parent.cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM items")
        stats["total_quantity"] = self.parent.cursor.fetchone()[0]

        # Items per box
        self.parent.cursor.execute(
            """
            SELECT boxes.name, COUNT(items.id) as item_count
            FROM boxes
            LEFT JOIN items ON boxes.id = items.box_id
            GROUP BY boxes.id, boxes.name
            ORDER BY item_count DESC
            LIMIT 10
        """
        )
        stats["items_per_box"] = self.parent.cursor.fetchall()

        # Quantity per box
        self.parent.cursor.execute(
            """
            SELECT boxes.name, COALESCE(SUM(items.quantity), 0) as total_quantity
            FROM boxes
            LEFT JOIN items ON boxes.id = items.box_id
            GROUP BY boxes.id, boxes.name
            ORDER BY total_quantity DESC
            LIMIT 10
        """
        )
        stats["quantity_per_box"] = self.parent.cursor.fetchall()

        return stats

    def update_items_per_box_chart(self, data):
        """Update the items per box bar chart."""
        # Clear previous chart
        figure = self.items_per_box_canvas.figure
        figure.clear()

        # Determine colors based on theme
        if ModernStyle.current_theme == "dark":
            bar_color = ModernStyle.PRIMARY
            text_color = ModernStyle.TEXT
            grid_color = ModernStyle.BORDER
            bg_color = ModernStyle.BACKGROUND
            face_color = ModernStyle.SURFACE
        else:
            bar_color = ModernStyle.PRIMARY
            text_color = ModernStyle.TEXT
            grid_color = ModernStyle.BORDER
            bg_color = ModernStyle.BACKGROUND
            face_color = ModernStyle.SURFACE

        # Set figure background
        figure.patch.set_facecolor(bg_color)

        if not data:
            ax = figure.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                self.translator.tr('stats_no_data'),
                ha="center",
                va="center",
                fontsize=11,
                color=text_color,
            )
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            ax.set_facecolor(face_color)
            self.items_per_box_canvas.draw()
            return

        # Extract data
        box_names = [name[:15] + "..." if len(name) > 15 else name for name, _ in data]
        item_counts = [count for _, count in data]

        # Create bar chart
        ax = figure.add_subplot(111)
        ax.set_facecolor(face_color)

        bars = ax.bar(
            box_names,
            item_counts,
            color=bar_color,
            alpha=0.85,
            edgecolor=bar_color,
            linewidth=2,
        )

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
                color=text_color,
            )

        ax.set_xlabel(self.translator.tr('stats_box_name'), fontsize=11, color=text_color, fontweight="bold")
        ax.set_ylabel(
            self.translator.tr('stats_number_of_items'), fontsize=11, color=text_color, fontweight="bold"
        )
        ax.set_title(
            self.translator.tr('stats_items_per_box'),
            fontsize=13,
            fontweight="bold",
            color=text_color,
            pad=15,
        )
        ax.tick_params(axis="x", rotation=45, labelsize=9, colors=text_color)
        ax.tick_params(axis="y", labelsize=10, colors=text_color)
        ax.grid(True, alpha=0.15, color=grid_color, linestyle="--", linewidth=1)

        # Set spine colors to match theme
        for spine in ax.spines.values():
            spine.set_edgecolor(grid_color)
            spine.set_linewidth(2)

        # Add a bit of room at the top for value labels
        ax.set_ylim(bottom=0, top=max(item_counts) * 1.1 if item_counts else 1)

        figure.tight_layout()
        self.items_per_box_canvas.draw()

    def update_quantity_per_box_chart(self, data):
        """Update the quantity per box bar chart."""
        # Clear previous chart
        figure = self.quantity_per_box_canvas.figure
        figure.clear()

        # Determine colors based on theme
        if ModernStyle.current_theme == "dark":
            bar_color = "#0d6efd"  # Blue
            text_color = ModernStyle.TEXT
            grid_color = ModernStyle.BORDER
            bg_color = ModernStyle.BACKGROUND
            face_color = ModernStyle.SURFACE
        else:
            bar_color = "#0d6efd"  # Blue
            text_color = ModernStyle.TEXT
            grid_color = ModernStyle.BORDER
            bg_color = ModernStyle.BACKGROUND
            face_color = ModernStyle.SURFACE

        # Set figure background
        figure.patch.set_facecolor(bg_color)

        if not data:
            ax = figure.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                self.translator.tr('stats_no_data'),
                ha="center",
                va="center",
                fontsize=11,
                color=text_color,
            )
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            ax.set_facecolor(face_color)
            self.quantity_per_box_canvas.draw()
            return

        # Extract data
        box_names = [name[:15] + "..." if len(name) > 15 else name for name, _ in data]
        quantities = [qty for _, qty in data]

        # Create bar chart
        ax = figure.add_subplot(111)
        ax.set_facecolor(face_color)

        bars = ax.bar(
            box_names,
            quantities,
            color=bar_color,
            alpha=0.85,
            edgecolor=bar_color,
            linewidth=2,
        )

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
                color=text_color,
            )

        ax.set_xlabel(self.translator.tr('stats_box_name'), fontsize=11, color=text_color, fontweight="bold")
        ax.set_ylabel(
            self.translator.tr('stats_total_quantity'), fontsize=11, color=text_color, fontweight="bold"
        )
        ax.set_title(
            self.translator.tr('stats_quantity_per_box'),
            fontsize=13,
            fontweight="bold",
            color=text_color,
            pad=15,
        )
        ax.tick_params(axis="x", rotation=45, labelsize=9, colors=text_color)
        ax.tick_params(axis="y", labelsize=10, colors=text_color)
        ax.grid(True, alpha=0.15, color=grid_color, linestyle="--", linewidth=1)

        # Set spine colors to match theme
        for spine in ax.spines.values():
            spine.set_edgecolor(grid_color)
            spine.set_linewidth(2)

        # Add a bit of room at the top for value labels
        ax.set_ylim(bottom=0, top=max(quantities) * 1.1 if quantities else 1)

        figure.tight_layout()
        self.quantity_per_box_canvas.draw()

    def showEvent(self, event):
        """Refresh stats when tab is shown."""
        super().showEvent(event)
        self.refresh_stats()
