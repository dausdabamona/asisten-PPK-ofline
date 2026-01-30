"""
PPK DOCUMENT FACTORY - Workflow Timeline Component
===================================================
Timeline component untuk visualisasi progress workflow satu transaksi.

Features:
- TimelineEvent: Data class untuk event
- TimelineItem: Single event display
- WorkflowTimeline: Vertical timeline dengan events
- WorkflowProgress: Compact progress bar untuk dashboard

Author: PPK Document Factory Team
Version: 4.0
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any, Callable

from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
    QComboBox, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

class EventType(Enum):
    """Types of workflow events."""
    CREATED = "created"
    FASE_CHANGED = "fase_changed"
    DOCUMENT_CREATED = "document_created"
    DOCUMENT_SIGNED = "document_signed"
    DOCUMENT_UPLOADED = "document_uploaded"
    PAYMENT = "payment"
    STATUS_CHANGED = "status_changed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NOTE_ADDED = "note_added"
    APPROVAL = "approval"
    REJECTION = "rejection"


# Event type configuration: icon, color, label
EVENT_CONFIG = {
    "created": {"icon": "\U0001F195", "color": "#9c27b0", "label": "Dibuat"},
    "fase_changed": {"icon": "\u27A1\uFE0F", "color": "#2196f3", "label": "Pindah Fase"},
    "document_created": {"icon": "\U0001F4C4", "color": "#ff9800", "label": "Dokumen Dibuat"},
    "document_signed": {"icon": "\u270D\uFE0F", "color": "#4caf50", "label": "Dokumen Ditandatangani"},
    "document_uploaded": {"icon": "\U0001F4E4", "color": "#00bcd4", "label": "Dokumen Diupload"},
    "payment": {"icon": "\U0001F4B0", "color": "#8bc34a", "label": "Pembayaran"},
    "status_changed": {"icon": "\U0001F504", "color": "#607d8b", "label": "Status Berubah"},
    "completed": {"icon": "\u2705", "color": "#4caf50", "label": "Selesai"},
    "cancelled": {"icon": "\u274C", "color": "#f44336", "label": "Dibatalkan"},
    "note_added": {"icon": "\U0001F4DD", "color": "#795548", "label": "Catatan"},
    "approval": {"icon": "\U0001F44D", "color": "#4caf50", "label": "Disetujui"},
    "rejection": {"icon": "\U0001F44E", "color": "#f44336", "label": "Ditolak"},
}

# Fase configuration
FASE_NAMES = {
    1: "Inisiasi",
    2: "Pencairan UM",
    3: "Pelaksanaan",
    4: "Pertanggungjawaban",
    5: "SPBY & Selesai"
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TimelineEvent:
    """
    Data class representing a single workflow event.

    Attributes:
        timestamp: When the event occurred
        event_type: Type of event (created, fase_changed, etc.)
        description: Human-readable description
        user: User who triggered the event (optional)
        metadata: Additional event data (optional)
        id: Unique event identifier (auto-generated)
    """
    timestamp: datetime
    event_type: str
    description: str
    user: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = f"evt_{self.timestamp.strftime('%Y%m%d%H%M%S')}_{id(self)}"
        if self.metadata is None:
            self.metadata = {}

    def get_icon(self) -> str:
        """Get icon for this event type."""
        config = EVENT_CONFIG.get(self.event_type, EVENT_CONFIG["note_added"])
        return config["icon"]

    def get_color(self) -> str:
        """Get color for this event type."""
        config = EVENT_CONFIG.get(self.event_type, EVENT_CONFIG["note_added"])
        return config["color"]

    def get_label(self) -> str:
        """Get label for this event type."""
        config = EVENT_CONFIG.get(self.event_type, EVENT_CONFIG["note_added"])
        return config["label"]

    def format_time(self) -> str:
        """Format timestamp for display."""
        return self.timestamp.strftime("%d %b %Y, %H:%M")

    def format_time_ago(self) -> str:
        """Format timestamp as relative time."""
        now = datetime.now()
        diff = now - self.timestamp

        if diff.days > 30:
            return self.timestamp.strftime("%d %b %Y")
        elif diff.days > 1:
            return f"{diff.days} hari lalu"
        elif diff.days == 1:
            return "Kemarin"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} jam lalu"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} menit lalu"
        else:
            return "Baru saja"


# =============================================================================
# TIMELINE ITEM
# =============================================================================

class TimelineItem(QFrame):
    """
    Single event display in the timeline.

    Features:
    - Icon based on event type
    - Timestamp and description
    - Optional user info
    - Expandable for metadata details

    Signals:
        clicked(str): Emit event_id when clicked
        expanded(str, bool): Emit event_id and expanded state
    """

    clicked = Signal(str)
    expanded = Signal(str, bool)

    def __init__(
        self,
        event: TimelineEvent,
        is_current: bool = False,
        is_last: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.event = event
        self.is_current = is_current
        self.is_last = is_last
        self._expanded = False

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        """Setup item UI."""
        self.setMinimumHeight(60)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(12)

        # ----- Timeline connector (left side) -----
        connector_widget = QWidget()
        connector_widget.setFixedWidth(40)
        connector_layout = QVBoxLayout(connector_widget)
        connector_layout.setContentsMargins(0, 0, 0, 0)
        connector_layout.setSpacing(0)

        # Dot/circle indicator
        self.dot = QLabel()
        self.dot.setFixedSize(20, 20)
        self.dot.setAlignment(Qt.AlignCenter)
        connector_layout.addWidget(self.dot, alignment=Qt.AlignHCenter)

        # Vertical line (connector to next item)
        if not self.is_last:
            self.line = QFrame()
            self.line.setFixedWidth(2)
            self.line.setMinimumHeight(40)
            self.line.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            connector_layout.addWidget(self.line, 1, alignment=Qt.AlignHCenter)
        else:
            connector_layout.addStretch()

        layout.addWidget(connector_widget)

        # ----- Content (right side) -----
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 8)
        content_layout.setSpacing(4)

        # Time row
        time_layout = QHBoxLayout()
        time_layout.setSpacing(8)

        self.time_label = QLabel(self.event.format_time())
        self.time_label.setFont(QFont("Segoe UI", 9))
        self.time_label.setStyleSheet("color: #757575;")
        time_layout.addWidget(self.time_label)

        time_layout.addStretch()

        # Time ago badge
        self.ago_label = QLabel(self.event.format_time_ago())
        self.ago_label.setFont(QFont("Segoe UI", 8))
        self.ago_label.setStyleSheet("""
            QLabel {
                color: #9e9e9e;
                background-color: #f5f5f5;
                padding: 2px 6px;
                border-radius: 8px;
            }
        """)
        time_layout.addWidget(self.ago_label)

        content_layout.addLayout(time_layout)

        # Event row (icon + description)
        event_layout = QHBoxLayout()
        event_layout.setSpacing(8)

        self.icon_label = QLabel(self.event.get_icon())
        self.icon_label.setFont(QFont("Segoe UI", 14))
        event_layout.addWidget(self.icon_label)

        self.desc_label = QLabel(self.event.description)
        self.desc_label.setFont(QFont("Segoe UI", 10))
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #212121;")
        event_layout.addWidget(self.desc_label, 1)

        content_layout.addLayout(event_layout)

        # User row (if available)
        if self.event.user:
            self.user_label = QLabel(f"Oleh: {self.event.user}")
            self.user_label.setFont(QFont("Segoe UI", 9))
            self.user_label.setStyleSheet("color: #757575; margin-left: 28px;")
            content_layout.addWidget(self.user_label)

        # Metadata panel (expandable)
        if self.event.metadata:
            self.metadata_panel = QFrame()
            self.metadata_panel.setVisible(False)
            metadata_layout = QVBoxLayout(self.metadata_panel)
            metadata_layout.setContentsMargins(28, 8, 0, 0)
            metadata_layout.setSpacing(4)

            for key, value in self.event.metadata.items():
                meta_label = QLabel(f"{key}: {value}")
                meta_label.setFont(QFont("Segoe UI", 9))
                meta_label.setStyleSheet("color: #616161;")
                metadata_layout.addWidget(meta_label)

            self.metadata_panel.setStyleSheet("""
                QFrame {
                    background-color: #fafafa;
                    border-left: 2px solid #e0e0e0;
                    padding: 4px;
                }
            """)
            content_layout.addWidget(self.metadata_panel)

            # Expand indicator
            self.expand_btn = QPushButton("▼ Detail")
            self.expand_btn.setFlat(True)
            self.expand_btn.setCursor(Qt.PointingHandCursor)
            self.expand_btn.setStyleSheet("""
                QPushButton {
                    color: #1976d2;
                    font-size: 9px;
                    padding: 2px 8px;
                    text-align: left;
                }
                QPushButton:hover {
                    color: #1565c0;
                }
            """)
            self.expand_btn.clicked.connect(self._toggle_expand)
            content_layout.addWidget(self.expand_btn)

        layout.addWidget(content_widget, 1)

    def _apply_style(self):
        """Apply styling based on event type and state."""
        color = self.event.get_color()

        # Dot style
        if self.is_current:
            # Current event - filled circle with animation-like border
            self.dot.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    border: 3px solid {color}40;
                    border-radius: 10px;
                }}
            """)
            self.desc_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        else:
            # Past event - simple filled circle
            self.dot.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    border: none;
                    border-radius: 10px;
                }}
            """)

        # Line style
        if hasattr(self, 'line'):
            self.line.setStyleSheet(f"""
                QFrame {{
                    background-color: #e0e0e0;
                }}
            """)

        # Frame style
        self.setStyleSheet("""
            TimelineItem {
                background-color: transparent;
            }
            TimelineItem:hover {
                background-color: #fafafa;
            }
        """)

    def _toggle_expand(self):
        """Toggle metadata panel visibility."""
        self._expanded = not self._expanded
        self.metadata_panel.setVisible(self._expanded)
        self.expand_btn.setText("▲ Tutup" if self._expanded else "▼ Detail")
        self.expanded.emit(self.event.id, self._expanded)

    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.event.id)
        super().mousePressEvent(event)

    def set_current(self, is_current: bool):
        """Set whether this is the current event."""
        self.is_current = is_current
        self._apply_style()


# =============================================================================
# WORKFLOW TIMELINE
# =============================================================================

class WorkflowTimeline(QWidget):
    """
    Vertical timeline displaying workflow events for a transaksi.

    Features:
    - Chronological event display
    - Filter by event type
    - Date range filtering
    - Current event highlighting

    Signals:
        event_clicked(str): Emit event_id when event clicked
        event_selected(TimelineEvent): Emit full event data
    """

    event_clicked = Signal(str)
    event_selected = Signal(object)

    def __init__(
        self,
        transaksi_id: Optional[str] = None,
        title: Optional[str] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.transaksi_id = transaksi_id
        self.title = title or f"Timeline Transaksi {transaksi_id or ''}"
        self._events: List[TimelineEvent] = []
        self._filtered_events: List[TimelineEvent] = []
        self._items: List[TimelineItem] = []
        self._filter_types: Optional[List[str]] = None
        self._date_start: Optional[date] = None
        self._date_end: Optional[date] = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup timeline UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ----- Header -----
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)

        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: #212121;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Filter combo
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Semua Event",
            "Perubahan Fase",
            "Dokumen",
            "Pembayaran",
            "Status"
        ])
        self.filter_combo.setFixedWidth(140)
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        self.filter_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
        """)
        header_layout.addWidget(self.filter_combo)

        layout.addWidget(header)

        # ----- Timeline Body (Scrollable) -----
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #bdbdbd;
                border-radius: 3px;
            }
        """)

        self.events_container = QWidget()
        self.events_layout = QVBoxLayout(self.events_container)
        self.events_layout.setContentsMargins(16, 16, 16, 16)
        self.events_layout.setSpacing(0)
        self.events_layout.setAlignment(Qt.AlignTop)

        # Empty state
        self.empty_label = QLabel("Belum ada event")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #9e9e9e; padding: 40px;")
        self.events_layout.addWidget(self.empty_label)

        self.scroll_area.setWidget(self.events_container)
        layout.addWidget(self.scroll_area, 1)

        # ----- Footer (Current status) -----
        self.footer = QFrame()
        self.footer.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border-top: 1px solid #bbdefb;
            }
        """)
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(16, 12, 16, 12)

        self.current_dot = QLabel()
        self.current_dot.setFixedSize(12, 12)
        self.current_dot.setStyleSheet("""
            QLabel {
                background-color: #2196f3;
                border-radius: 6px;
            }
        """)
        footer_layout.addWidget(self.current_dot)

        self.current_label = QLabel("Menunggu...")
        self.current_label.setFont(QFont("Segoe UI", 10))
        self.current_label.setStyleSheet("color: #1565c0;")
        footer_layout.addWidget(self.current_label)

        footer_layout.addStretch()

        layout.addWidget(self.footer)

    def _on_filter_changed(self, text: str):
        """Handle filter combo change."""
        filter_map = {
            "Semua Event": None,
            "Perubahan Fase": ["fase_changed"],
            "Dokumen": ["document_created", "document_signed", "document_uploaded"],
            "Pembayaran": ["payment"],
            "Status": ["status_changed", "completed", "cancelled"]
        }
        self._filter_types = filter_map.get(text)
        self._apply_filters()

    def _apply_filters(self):
        """Apply current filters to events."""
        self._filtered_events = []

        for event in self._events:
            # Filter by type
            if self._filter_types and event.event_type not in self._filter_types:
                continue

            # Filter by date range
            if self._date_start:
                event_date = event.timestamp.date()
                if event_date < self._date_start:
                    continue

            if self._date_end:
                event_date = event.timestamp.date()
                if event_date > self._date_end:
                    continue

            self._filtered_events.append(event)

        self._rebuild_timeline()

    def _rebuild_timeline(self):
        """Rebuild timeline items from filtered events."""
        # Clear existing items
        for item in self._items:
            self.events_layout.removeWidget(item)
            item.deleteLater()
        self._items.clear()

        # Show/hide empty state
        self.empty_label.setVisible(len(self._filtered_events) == 0)

        # Sort events by timestamp (newest first or oldest first)
        sorted_events = sorted(self._filtered_events, key=lambda e: e.timestamp)

        # Create new items
        for i, event in enumerate(sorted_events):
            is_last = (i == len(sorted_events) - 1)
            is_current = is_last  # Last event is current

            item = TimelineItem(event, is_current=is_current, is_last=is_last)
            item.clicked.connect(self._on_item_clicked)

            self._items.append(item)
            self.events_layout.insertWidget(self.events_layout.count() - 1, item)

        # Update footer with current status
        if sorted_events:
            last_event = sorted_events[-1]
            self.current_label.setText(last_event.description)

    def _on_item_clicked(self, event_id: str):
        """Handle timeline item click."""
        self.event_clicked.emit(event_id)

        # Find and emit full event
        for event in self._events:
            if event.id == event_id:
                self.event_selected.emit(event)
                break

    # -------------------------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------------------------

    def load_events(self, transaksi_id: str):
        """
        Load events for a transaksi.

        This method should be overridden or connected to a data source
        to load actual events from database.
        """
        self.transaksi_id = transaksi_id
        self.title_label.setText(f"Timeline Transaksi {transaksi_id}")
        # Events would be loaded from database here
        self._apply_filters()

    def add_event(self, event: TimelineEvent):
        """Add a new event to the timeline."""
        self._events.append(event)
        self._apply_filters()

    def set_events(self, events: List[TimelineEvent]):
        """Set all events for the timeline."""
        self._events = events
        self._apply_filters()

    def clear_events(self):
        """Clear all events from the timeline."""
        self._events.clear()
        self._apply_filters()

    def filter_by_type(self, event_types: Optional[List[str]]):
        """Filter timeline by event types."""
        self._filter_types = event_types
        self._apply_filters()

    def set_date_range(self, start: Optional[date], end: Optional[date]):
        """Set date range filter."""
        self._date_start = start
        self._date_end = end
        self._apply_filters()

    def get_events(self) -> List[TimelineEvent]:
        """Get all events."""
        return self._events.copy()

    def get_filtered_events(self) -> List[TimelineEvent]:
        """Get filtered events."""
        return self._filtered_events.copy()

    def set_current_status(self, status: str):
        """Set the current status message in footer."""
        self.current_label.setText(status)

    def set_title(self, title: str):
        """Set timeline title."""
        self.title = title
        self.title_label.setText(title)


# =============================================================================
# WORKFLOW PROGRESS (Compact View)
# =============================================================================

class WorkflowProgress(QWidget):
    """
    Compact progress view for dashboard showing workflow progress.

    Features:
    - Horizontal progress bar with fase markers
    - Current fase highlighted
    - Estimated completion date

    Signals:
        fase_clicked(int): Emit when a fase marker is clicked
    """

    fase_clicked = Signal(int)

    def __init__(
        self,
        current_fase: int = 1,
        total_fases: int = 5,
        estimated_completion: Optional[date] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.current_fase = current_fase
        self.total_fases = total_fases
        self.estimated_completion = estimated_completion

        self.setMinimumHeight(60)
        self.setMaximumHeight(80)

        self._setup_ui()

    def _setup_ui(self):
        """Setup progress UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Progress bar container
        self.progress_widget = QWidget()
        self.progress_widget.setMinimumHeight(40)
        layout.addWidget(self.progress_widget)

        # Status text
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(8, 0, 8, 0)

        self.fase_label = QLabel(f"Fase {self.current_fase}/{self.total_fases}")
        self.fase_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.fase_label.setStyleSheet("color: #1565c0;")
        status_layout.addWidget(self.fase_label)

        status_layout.addStretch()

        if self.estimated_completion:
            est_text = self.estimated_completion.strftime("%d %b %Y")
            self.est_label = QLabel(f"Est. selesai: {est_text}")
            self.est_label.setFont(QFont("Segoe UI", 9))
            self.est_label.setStyleSheet("color: #757575;")
            status_layout.addWidget(self.est_label)

        layout.addLayout(status_layout)

    def paintEvent(self, event):
        """Paint the progress bar."""
        super().paintEvent(event)

        painter = QPainter(self.progress_widget)
        painter.setRenderHint(QPainter.Antialiasing)

        widget = self.progress_widget
        width = widget.width()
        height = widget.height()
        margin = 20
        bar_y = height // 2

        # Calculate positions
        usable_width = width - (2 * margin)
        step_width = usable_width / (self.total_fases - 1) if self.total_fases > 1 else usable_width

        # Draw background line
        painter.setPen(QPen(QColor("#e0e0e0"), 4))
        painter.drawLine(margin, bar_y, width - margin, bar_y)

        # Draw completed line
        if self.current_fase > 1:
            completed_x = margin + (step_width * (self.current_fase - 1))
            painter.setPen(QPen(QColor("#4caf50"), 4))
            painter.drawLine(margin, bar_y, int(completed_x), bar_y)

        # Draw fase markers
        for i in range(self.total_fases):
            fase_num = i + 1
            x = margin + (step_width * i)

            if fase_num < self.current_fase:
                # Completed fase
                painter.setBrush(QBrush(QColor("#4caf50")))
                painter.setPen(QPen(QColor("#4caf50"), 2))
            elif fase_num == self.current_fase:
                # Current fase
                painter.setBrush(QBrush(QColor("#2196f3")))
                painter.setPen(QPen(QColor("#1565c0"), 3))
            else:
                # Future fase
                painter.setBrush(QBrush(QColor("#e0e0e0")))
                painter.setPen(QPen(QColor("#bdbdbd"), 2))

            # Draw circle
            radius = 10 if fase_num == self.current_fase else 8
            painter.drawEllipse(int(x - radius), bar_y - radius, radius * 2, radius * 2)

            # Draw fase number
            painter.setPen(QPen(QColor("#ffffff" if fase_num <= self.current_fase else "#757575")))
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.drawText(int(x - 4), bar_y + 4, str(fase_num))

        painter.end()

    def set_current_fase(self, fase: int):
        """Set current fase and update display."""
        self.current_fase = min(max(1, fase), self.total_fases)
        self.fase_label.setText(f"Fase {self.current_fase}/{self.total_fases}")
        self.update()

    def set_estimated_completion(self, est_date: Optional[date]):
        """Set estimated completion date."""
        self.estimated_completion = est_date
        if hasattr(self, 'est_label') and est_date:
            self.est_label.setText(f"Est. selesai: {est_date.strftime('%d %b %Y')}")

    def mousePressEvent(self, event):
        """Handle click on fase marker."""
        if event.button() == Qt.LeftButton:
            # Calculate which fase was clicked
            widget = self.progress_widget
            margin = 20
            usable_width = widget.width() - (2 * margin)
            step_width = usable_width / (self.total_fases - 1) if self.total_fases > 1 else usable_width

            click_x = event.pos().x()
            for i in range(self.total_fases):
                x = margin + (step_width * i)
                if abs(click_x - x) < 15:  # Click within 15px of marker
                    self.fase_clicked.emit(i + 1)
                    break

        super().mousePressEvent(event)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_timeline(
    transaksi_id: Optional[str] = None,
    events: Optional[List[TimelineEvent]] = None,
    title: Optional[str] = None,
    parent: Optional[QWidget] = None
) -> WorkflowTimeline:
    """
    Factory function to create a WorkflowTimeline.

    Args:
        transaksi_id: ID of the transaksi
        events: Initial list of events
        title: Timeline title
        parent: Parent widget

    Returns:
        Configured WorkflowTimeline instance
    """
    timeline = WorkflowTimeline(
        transaksi_id=transaksi_id,
        title=title,
        parent=parent
    )

    if events:
        timeline.set_events(events)

    return timeline


def create_progress(
    current_fase: int = 1,
    total_fases: int = 5,
    estimated_completion: Optional[date] = None,
    parent: Optional[QWidget] = None
) -> WorkflowProgress:
    """
    Factory function to create a WorkflowProgress.

    Args:
        current_fase: Current workflow fase
        total_fases: Total number of fases
        estimated_completion: Estimated completion date
        parent: Parent widget

    Returns:
        Configured WorkflowProgress instance
    """
    return WorkflowProgress(
        current_fase=current_fase,
        total_fases=total_fases,
        estimated_completion=estimated_completion,
        parent=parent
    )


# =============================================================================
# DATABASE INTEGRATION HELPER
# =============================================================================

class WorkflowEventLogger:
    """
    Helper class for logging workflow events to database.

    Usage:
        logger = WorkflowEventLogger(db_connection)
        logger.log_created(transaksi_id, "Admin")
        logger.log_fase_changed(transaksi_id, 1, 2, "Admin")
    """

    def __init__(self, db_connection=None):
        self.db = db_connection

    def log_event(
        self,
        transaksi_id: str,
        event_type: str,
        description: str,
        user: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TimelineEvent:
        """Log a generic event."""
        event = TimelineEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            description=description,
            user=user,
            metadata=metadata or {}
        )

        # Save to database if connection available
        if self.db:
            self._save_to_db(transaksi_id, event)

        return event

    def log_created(self, transaksi_id: str, user: Optional[str] = None) -> TimelineEvent:
        """Log transaksi created event."""
        return self.log_event(
            transaksi_id=transaksi_id,
            event_type="created",
            description="Transaksi dibuat",
            user=user
        )

    def log_fase_changed(
        self,
        transaksi_id: str,
        from_fase: int,
        to_fase: int,
        user: Optional[str] = None
    ) -> TimelineEvent:
        """Log fase change event."""
        to_name = FASE_NAMES.get(to_fase, f"Fase {to_fase}")
        return self.log_event(
            transaksi_id=transaksi_id,
            event_type="fase_changed",
            description=f"Pindah ke Fase {to_fase}: {to_name}",
            user=user,
            metadata={"from_fase": from_fase, "to_fase": to_fase}
        )

    def log_document_created(
        self,
        transaksi_id: str,
        document_name: str,
        user: Optional[str] = None
    ) -> TimelineEvent:
        """Log document created event."""
        return self.log_event(
            transaksi_id=transaksi_id,
            event_type="document_created",
            description=f"{document_name} dibuat",
            user=user,
            metadata={"document": document_name}
        )

    def log_payment(
        self,
        transaksi_id: str,
        amount: float,
        payment_type: str,
        user: Optional[str] = None
    ) -> TimelineEvent:
        """Log payment event."""
        formatted_amount = f"Rp {amount:,.0f}"
        return self.log_event(
            transaksi_id=transaksi_id,
            event_type="payment",
            description=f"Pembayaran {payment_type}: {formatted_amount}",
            user=user,
            metadata={"amount": amount, "type": payment_type}
        )

    def log_completed(self, transaksi_id: str, user: Optional[str] = None) -> TimelineEvent:
        """Log transaksi completed event."""
        return self.log_event(
            transaksi_id=transaksi_id,
            event_type="completed",
            description="Transaksi selesai",
            user=user
        )

    def _save_to_db(self, transaksi_id: str, event: TimelineEvent):
        """Save event to database. Override for actual implementation."""
        # This would be implemented based on the database schema
        pass

    def get_events(self, transaksi_id: str) -> List[TimelineEvent]:
        """Get all events for a transaksi from database."""
        # This would be implemented based on the database schema
        return []
