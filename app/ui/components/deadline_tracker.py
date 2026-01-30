"""
PPK DOCUMENT FACTORY - Deadline Tracker Component
==================================================
Component untuk tracking deadline workflow.

Features:
- DeadlineInfo: Data class untuk deadline info
- DeadlineItem: Single deadline entry display
- DeadlineTrackerWidget: List semua deadline
- Deadline calculation logic

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
    QComboBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QFont


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

class DeadlineStatus(Enum):
    """Deadline status types."""
    ON_TRACK = "on_track"     # > 7 days remaining
    WARNING = "warning"       # 3-7 days remaining
    DUE_SOON = "due_soon"     # 1-3 days remaining
    OVERDUE = "overdue"       # Past deadline


# Status configuration
STATUS_CONFIG = {
    "on_track": {
        "color": "#4caf50",
        "bg": "#e8f5e9",
        "icon": "\U0001F7E2",  # Green circle
        "label": "On Track"
    },
    "warning": {
        "color": "#ff9800",
        "bg": "#fff3e0",
        "icon": "\U0001F7E1",  # Yellow circle
        "label": "Warning"
    },
    "due_soon": {
        "color": "#ff5722",
        "bg": "#fbe9e7",
        "icon": "\U0001F7E0",  # Orange circle
        "label": "Due Soon"
    },
    "overdue": {
        "color": "#f44336",
        "bg": "#ffebee",
        "icon": "\U0001F534",  # Red circle
        "label": "Overdue"
    },
}

# Default SLA per mekanisme (days)
DEFAULT_SLA = {
    "UP": 30,    # 30 hari dari pencairan UM
    "TUP": 30,   # 30 hari dari persetujuan
    "LS": 90,    # Sesuai kontrak, default 90 hari
}

# Fase names
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
class DeadlineInfo:
    """
    Data class representing deadline information.

    Attributes:
        transaksi_id: Unique transaksi identifier
        transaksi_nama: Display name
        transaksi_nomor: Transaksi number
        deadline: Deadline date
        days_remaining: Days until/since deadline (negative if overdue)
        fase_current: Current workflow fase
        mekanisme: Payment mechanism (UP/TUP/LS)
        nilai: Transaction value
        status: Deadline status (on_track, warning, due_soon, overdue)
    """
    transaksi_id: str
    transaksi_nama: str
    transaksi_nomor: str
    deadline: date
    days_remaining: int
    fase_current: int
    mekanisme: str = "UP"
    nilai: float = 0.0
    status: str = "on_track"

    def __post_init__(self):
        # Auto-calculate status if not provided
        if self.days_remaining < 0:
            self.status = "overdue"
        elif self.days_remaining <= 3:
            self.status = "due_soon"
        elif self.days_remaining <= 7:
            self.status = "warning"
        else:
            self.status = "on_track"

    def get_status_config(self) -> Dict[str, str]:
        """Get status configuration."""
        return STATUS_CONFIG.get(self.status, STATUS_CONFIG["on_track"])

    def format_days_remaining(self) -> str:
        """Format days remaining for display."""
        if self.days_remaining < 0:
            return f"{abs(self.days_remaining)} hari terlambat"
        elif self.days_remaining == 0:
            return "Hari ini"
        elif self.days_remaining == 1:
            return "Besok"
        else:
            return f"{self.days_remaining} hari lagi"

    def format_deadline(self) -> str:
        """Format deadline date for display."""
        return self.deadline.strftime("%d %b %Y")

    def get_progress(self) -> float:
        """Get progress percentage based on fase."""
        return (self.fase_current / 5) * 100


# =============================================================================
# DEADLINE ITEM
# =============================================================================

class DeadlineItem(QFrame):
    """
    Single deadline entry display.

    Features:
    - Status icon and color coding
    - Transaksi info
    - Days remaining
    - Progress bar
    - Click to open transaksi

    Signals:
        clicked(str): Emit transaksi_id when clicked
    """

    clicked = Signal(str)

    def __init__(
        self,
        info: DeadlineInfo,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.info = info
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        """Setup item UI."""
        self.setMinimumHeight(70)
        self.setMaximumHeight(90)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        # Status indicator
        config = self.info.get_status_config()
        self.status_icon = QLabel(config["icon"])
        self.status_icon.setFont(QFont("Segoe UI", 16))
        self.status_icon.setFixedWidth(30)
        layout.addWidget(self.status_icon)

        # Main content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        # First row: Nomor + Nama
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)

        self.nomor_label = QLabel(self.info.transaksi_nomor)
        self.nomor_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.nomor_label.setStyleSheet(f"color: {config['color']};")
        title_layout.addWidget(self.nomor_label)

        self.nama_label = QLabel(self.info.transaksi_nama)
        self.nama_label.setFont(QFont("Segoe UI", 10))
        self.nama_label.setStyleSheet("color: #212121;")
        self.nama_label.setWordWrap(False)
        title_layout.addWidget(self.nama_label, 1)

        # Mekanisme badge
        self.mekanisme_badge = QLabel(self.info.mekanisme)
        self.mekanisme_badge.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.mekanisme_badge.setAlignment(Qt.AlignCenter)
        self.mekanisme_badge.setFixedSize(32, 18)
        title_layout.addWidget(self.mekanisme_badge)

        content_layout.addLayout(title_layout)

        # Second row: Fase + Progress
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(8)

        fase_name = FASE_NAMES.get(self.info.fase_current, f"Fase {self.info.fase_current}")
        self.fase_label = QLabel(f"Fase {self.info.fase_current}: {fase_name}")
        self.fase_label.setFont(QFont("Segoe UI", 9))
        self.fase_label.setStyleSheet("color: #757575;")
        progress_layout.addWidget(self.fase_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(int(self.info.get_progress()))
        self.progress_bar.setFixedSize(80, 8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #e0e0e0;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {config['color']};
                border-radius: 4px;
            }}
        """)
        progress_layout.addWidget(self.progress_bar)

        progress_layout.addStretch()

        content_layout.addLayout(progress_layout)

        layout.addLayout(content_layout, 1)

        # Days remaining
        days_layout = QVBoxLayout()
        days_layout.setSpacing(2)
        days_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.days_label = QLabel(self.info.format_days_remaining())
        self.days_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.days_label.setAlignment(Qt.AlignRight)
        self.days_label.setStyleSheet(f"color: {config['color']};")
        days_layout.addWidget(self.days_label)

        self.deadline_label = QLabel(self.info.format_deadline())
        self.deadline_label.setFont(QFont("Segoe UI", 8))
        self.deadline_label.setAlignment(Qt.AlignRight)
        self.deadline_label.setStyleSheet("color: #9e9e9e;")
        days_layout.addWidget(self.deadline_label)

        layout.addLayout(days_layout)

    def _apply_style(self):
        """Apply styling based on status."""
        config = self.info.get_status_config()

        self.setStyleSheet(f"""
            DeadlineItem {{
                background-color: {config['bg']};
                border: 1px solid {config['color']}40;
                border-left: 4px solid {config['color']};
                border-radius: 6px;
            }}
            DeadlineItem:hover {{
                background-color: white;
                border: 1px solid {config['color']};
                border-left: 4px solid {config['color']};
            }}
        """)

        # Mekanisme badge colors
        mek_colors = {
            "UP": "#4caf50",
            "TUP": "#ff9800",
            "LS": "#2196f3"
        }
        mek_color = mek_colors.get(self.info.mekanisme, "#607d8b")
        self.mekanisme_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {mek_color};
                color: white;
                border-radius: 9px;
                padding: 2px 4px;
            }}
        """)

    def mousePressEvent(self, event):
        """Handle click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.info.transaksi_id)
        super().mousePressEvent(event)

    def update_info(self, info: DeadlineInfo):
        """Update deadline info."""
        self.info = info
        config = info.get_status_config()

        self.status_icon.setText(config["icon"])
        self.nomor_label.setText(info.transaksi_nomor)
        self.nama_label.setText(info.transaksi_nama)
        self.mekanisme_badge.setText(info.mekanisme)
        self.days_label.setText(info.format_days_remaining())
        self.deadline_label.setText(info.format_deadline())
        self.progress_bar.setValue(int(info.get_progress()))

        self._apply_style()


# =============================================================================
# DEADLINE SECTION HEADER
# =============================================================================

class DeadlineSectionHeader(QFrame):
    """Header for deadline sections (Overdue, Due Soon, etc.)."""

    def __init__(
        self,
        title: str,
        icon: str,
        count: int = 0,
        color: str = "#757575",
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.title = title
        self.icon = icon
        self.count = count
        self.color = color

        self._setup_ui()

    def _setup_ui(self):
        """Setup header UI."""
        self.setFixedHeight(36)
        self.setStyleSheet(f"""
            DeadlineSectionHeader {{
                background-color: {self.color}15;
                border-bottom: 1px solid {self.color}30;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)

        self.icon_label = QLabel(self.icon)
        self.icon_label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.icon_label)

        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {self.color};")
        layout.addWidget(self.title_label)

        layout.addStretch()

        self.count_badge = QLabel(str(self.count))
        self.count_badge.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.count_badge.setAlignment(Qt.AlignCenter)
        self.count_badge.setFixedSize(24, 20)
        self.count_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {self.color};
                color: white;
                border-radius: 10px;
            }}
        """)
        layout.addWidget(self.count_badge)

    def set_count(self, count: int):
        """Update the count badge."""
        self.count = count
        self.count_badge.setText(str(count))


# =============================================================================
# DEADLINE TRACKER WIDGET
# =============================================================================

class DeadlineTrackerWidget(QWidget):
    """
    Widget for tracking and displaying workflow deadlines.

    Features:
    - Grouped display (Overdue, Due Soon, Warning)
    - Sorted by urgency
    - Filter options
    - Click to open transaksi

    Signals:
        deadline_clicked(str): Emit transaksi_id when clicked
        overdue_alert(int): Emit count of overdue items
    """

    deadline_clicked = Signal(str)
    overdue_alert = Signal(int)

    def __init__(
        self,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self._all_deadlines: List[DeadlineInfo] = []
        self._filtered_deadlines: List[DeadlineInfo] = []
        self._items: List[DeadlineItem] = []
        self._filter = "Semua"

        self._setup_ui()

    def _setup_ui(self):
        """Setup tracker UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ----- Header -----
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)

        icon_label = QLabel("\u23F0")  # Alarm clock
        icon_label.setFont(QFont("Segoe UI", 16))
        header_layout.addWidget(icon_label)

        title_label = QLabel("Deadline Tracker")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setStyleSheet("color: #212121;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Filter combo
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Semua", "Overdue", "Due Soon", "Warning", "On Track"])
        self.filter_combo.setFixedWidth(100)
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

        # ----- Content (Scrollable) -----
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #fafafa;
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

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_layout.setSpacing(8)
        self.content_layout.setAlignment(Qt.AlignTop)

        # Section containers
        self.sections: Dict[str, QVBoxLayout] = {}

        # Empty state
        self.empty_label = QLabel("Tidak ada deadline yang perlu diperhatikan")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #9e9e9e; padding: 40px;")
        self.content_layout.addWidget(self.empty_label)

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area, 1)

    def _on_filter_changed(self, filter_text: str):
        """Handle filter change."""
        self._filter = filter_text
        self._apply_filter()

    def _apply_filter(self):
        """Apply current filter to deadlines."""
        filter_map = {
            "Semua": None,
            "Overdue": "overdue",
            "Due Soon": "due_soon",
            "Warning": "warning",
            "On Track": "on_track"
        }

        status_filter = filter_map.get(self._filter)

        if status_filter:
            self._filtered_deadlines = [
                d for d in self._all_deadlines
                if d.status == status_filter
            ]
        else:
            self._filtered_deadlines = self._all_deadlines.copy()

        self._rebuild_list()

    def _rebuild_list(self):
        """Rebuild the deadline list display."""
        # Clear existing items
        for item in self._items:
            self.content_layout.removeWidget(item)
            item.deleteLater()
        self._items.clear()

        # Clear sections
        for section in list(self.sections.values()):
            for i in reversed(range(section.count())):
                widget = section.itemAt(i).widget()
                if widget:
                    section.removeWidget(widget)
                    widget.deleteLater()

        # Remove section headers
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item and item.widget() and item.widget() != self.empty_label:
                widget = item.widget()
                self.content_layout.removeWidget(widget)
                widget.deleteLater()

        self.sections.clear()

        # Show/hide empty state
        self.empty_label.setVisible(len(self._filtered_deadlines) == 0)

        if not self._filtered_deadlines:
            return

        # Sort by days remaining (most urgent first)
        sorted_deadlines = sorted(self._filtered_deadlines, key=lambda d: d.days_remaining)

        # Group by status
        groups = {
            "overdue": [],
            "due_soon": [],
            "warning": [],
            "on_track": []
        }

        for deadline in sorted_deadlines:
            if deadline.status in groups:
                groups[deadline.status].append(deadline)

        # Create sections
        section_config = [
            ("overdue", "\U0001F534 OVERDUE", STATUS_CONFIG["overdue"]["color"]),
            ("due_soon", "\U0001F7E0 DUE SOON (< 3 hari)", STATUS_CONFIG["due_soon"]["color"]),
            ("warning", "\U0001F7E1 WARNING (< 7 hari)", STATUS_CONFIG["warning"]["color"]),
            ("on_track", "\U0001F7E2 ON TRACK", STATUS_CONFIG["on_track"]["color"]),
        ]

        for status, title, color in section_config:
            items = groups.get(status, [])
            if items:
                # Add section header
                icon = STATUS_CONFIG[status]["icon"]
                header = DeadlineSectionHeader(
                    title=title.split(" ", 1)[1],  # Remove emoji from title
                    icon=icon,
                    count=len(items),
                    color=color
                )
                self.content_layout.addWidget(header)

                # Add items
                for info in items:
                    item = DeadlineItem(info)
                    item.clicked.connect(self.deadline_clicked.emit)
                    self._items.append(item)
                    self.content_layout.addWidget(item)

        self.content_layout.addStretch()

    # -------------------------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------------------------

    def load_deadlines(self, transaksi_list: Optional[List[Dict[str, Any]]] = None):
        """
        Load deadlines from transaksi list.

        Args:
            transaksi_list: List of transaksi dictionaries
        """
        self._all_deadlines.clear()

        if transaksi_list:
            for t in transaksi_list:
                deadline = self.calculate_deadline(t)
                if deadline:
                    info = self._create_deadline_info(t, deadline)
                    self._all_deadlines.append(info)

        self._apply_filter()

        # Emit overdue alert
        overdue_count = len(self.get_overdue())
        if overdue_count > 0:
            self.overdue_alert.emit(overdue_count)

    def set_deadlines(self, deadlines: List[DeadlineInfo]):
        """Directly set deadline info list."""
        self._all_deadlines = deadlines
        self._apply_filter()

        overdue_count = len(self.get_overdue())
        if overdue_count > 0:
            self.overdue_alert.emit(overdue_count)

    def add_deadline(self, info: DeadlineInfo):
        """Add a single deadline."""
        self._all_deadlines.append(info)
        self._apply_filter()

    def remove_deadline(self, transaksi_id: str):
        """Remove a deadline by transaksi ID."""
        self._all_deadlines = [
            d for d in self._all_deadlines
            if d.transaksi_id != transaksi_id
        ]
        self._apply_filter()

    def get_overdue(self) -> List[DeadlineInfo]:
        """Get list of overdue deadlines."""
        return [d for d in self._all_deadlines if d.status == "overdue"]

    def get_due_soon(self, days: int = 3) -> List[DeadlineInfo]:
        """Get list of deadlines due within specified days."""
        return [
            d for d in self._all_deadlines
            if 0 <= d.days_remaining <= days
        ]

    def get_warning(self, days: int = 7) -> List[DeadlineInfo]:
        """Get list of warning deadlines (within specified days)."""
        return [
            d for d in self._all_deadlines
            if 0 < d.days_remaining <= days
        ]

    def calculate_deadline(self, transaksi: Dict[str, Any]) -> Optional[date]:
        """
        Calculate deadline for a transaksi.

        Default SLA:
        - UP: 30 days from UM disbursement
        - TUP: 30 days from approval
        - LS: Per contract (default 90 days)

        Args:
            transaksi: Transaksi dictionary

        Returns:
            Deadline date or None if cannot calculate
        """
        # Check for custom deadline
        if transaksi.get("deadline"):
            dl = transaksi["deadline"]
            if isinstance(dl, str):
                return datetime.fromisoformat(dl).date()
            elif isinstance(dl, datetime):
                return dl.date()
            elif isinstance(dl, date):
                return dl

        # Calculate based on mekanisme and creation date
        mekanisme = transaksi.get("mekanisme", "UP")
        sla_days = transaksi.get("sla_days") or DEFAULT_SLA.get(mekanisme, 30)

        # Get start date (UM disbursement, approval, or creation)
        start_date = None

        if mekanisme == "UP":
            # Start from UM disbursement date
            um_date = transaksi.get("um_date") or transaksi.get("created_at")
            if um_date:
                if isinstance(um_date, str):
                    start_date = datetime.fromisoformat(um_date).date()
                elif isinstance(um_date, datetime):
                    start_date = um_date.date()
                elif isinstance(um_date, date):
                    start_date = um_date

        elif mekanisme == "TUP":
            # Start from approval date
            approval_date = transaksi.get("approval_date") or transaksi.get("created_at")
            if approval_date:
                if isinstance(approval_date, str):
                    start_date = datetime.fromisoformat(approval_date).date()
                elif isinstance(approval_date, datetime):
                    start_date = approval_date.date()
                elif isinstance(approval_date, date):
                    start_date = approval_date

        else:  # LS
            # Start from contract date
            contract_date = transaksi.get("contract_date") or transaksi.get("created_at")
            if contract_date:
                if isinstance(contract_date, str):
                    start_date = datetime.fromisoformat(contract_date).date()
                elif isinstance(contract_date, datetime):
                    start_date = contract_date.date()
                elif isinstance(contract_date, date):
                    start_date = contract_date

        if start_date:
            return start_date + timedelta(days=sla_days)

        return None

    def _create_deadline_info(
        self,
        transaksi: Dict[str, Any],
        deadline: date
    ) -> DeadlineInfo:
        """Create DeadlineInfo from transaksi and calculated deadline."""
        days_remaining = (deadline - date.today()).days

        return DeadlineInfo(
            transaksi_id=str(transaksi.get("id", "")),
            transaksi_nama=transaksi.get("nama", ""),
            transaksi_nomor=transaksi.get("nomor", ""),
            deadline=deadline,
            days_remaining=days_remaining,
            fase_current=transaksi.get("fase", 1),
            mekanisme=transaksi.get("mekanisme", "UP"),
            nilai=transaksi.get("nilai", 0.0)
        )

    def refresh(self):
        """Refresh the display."""
        self._apply_filter()

    def get_all_deadlines(self) -> List[DeadlineInfo]:
        """Get all deadline info."""
        return self._all_deadlines.copy()

    def get_filtered_deadlines(self) -> List[DeadlineInfo]:
        """Get filtered deadline info."""
        return self._filtered_deadlines.copy()


# =============================================================================
# COMPACT DEADLINE WIDGET
# =============================================================================

class CompactDeadlineWidget(QFrame):
    """
    Compact deadline summary widget for dashboard.

    Shows:
    - Total count with breakdown
    - Most urgent deadlines
    - Link to full tracker
    """

    view_all_clicked = Signal()
    deadline_clicked = Signal(str)

    MAX_DISPLAY = 3

    def __init__(
        self,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self._deadlines: List[DeadlineInfo] = []
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        """Setup compact widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()

        icon_label = QLabel("\u23F0")
        icon_label.setFont(QFont("Segoe UI", 14))
        header_layout.addWidget(icon_label)

        title_label = QLabel("Deadline")
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet("color: #212121;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Summary badges
        self.overdue_badge = QLabel("0")
        self.overdue_badge.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.overdue_badge.setAlignment(Qt.AlignCenter)
        self.overdue_badge.setFixedSize(24, 18)
        self.overdue_badge.setStyleSheet("""
            QLabel {
                background-color: #f44336;
                color: white;
                border-radius: 9px;
            }
        """)
        self.overdue_badge.setToolTip("Overdue")
        header_layout.addWidget(self.overdue_badge)

        self.warning_badge = QLabel("0")
        self.warning_badge.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.warning_badge.setAlignment(Qt.AlignCenter)
        self.warning_badge.setFixedSize(24, 18)
        self.warning_badge.setStyleSheet("""
            QLabel {
                background-color: #ff9800;
                color: white;
                border-radius: 9px;
            }
        """)
        self.warning_badge.setToolTip("Warning")
        header_layout.addWidget(self.warning_badge)

        layout.addLayout(header_layout)

        # Items container
        self.items_container = QVBoxLayout()
        self.items_container.setSpacing(4)
        layout.addLayout(self.items_container)

        # Empty state
        self.empty_label = QLabel("Tidak ada deadline mendesak")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #9e9e9e; padding: 12px;")
        self.empty_label.setFont(QFont("Segoe UI", 9))
        self.items_container.addWidget(self.empty_label)

        # View all button
        self.view_all_btn = QPushButton("Lihat Semua")
        self.view_all_btn.setCursor(Qt.PointingHandCursor)
        self.view_all_btn.clicked.connect(self.view_all_clicked.emit)
        self.view_all_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1976d2;
                border: none;
                font-size: 10px;
                text-align: right;
            }
            QPushButton:hover {
                color: #1565c0;
                text-decoration: underline;
            }
        """)
        layout.addWidget(self.view_all_btn, alignment=Qt.AlignRight)

    def _apply_style(self):
        """Apply widget styling."""
        self.setStyleSheet("""
            CompactDeadlineWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)

    def set_deadlines(self, deadlines: List[DeadlineInfo]):
        """Set deadlines to display."""
        self._deadlines = sorted(deadlines, key=lambda d: d.days_remaining)

        # Update badges
        overdue = sum(1 for d in deadlines if d.status == "overdue")
        warning = sum(1 for d in deadlines if d.status in ("warning", "due_soon"))

        self.overdue_badge.setText(str(overdue))
        self.overdue_badge.setVisible(overdue > 0)
        self.warning_badge.setText(str(warning))
        self.warning_badge.setVisible(warning > 0)

        # Clear and rebuild items
        for i in reversed(range(self.items_container.count())):
            item = self.items_container.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                self.items_container.removeWidget(widget)
                widget.deleteLater()

        # Get urgent deadlines (overdue and due_soon first)
        urgent = [
            d for d in self._deadlines
            if d.status in ("overdue", "due_soon", "warning")
        ][:self.MAX_DISPLAY]

        self.empty_label = QLabel("Tidak ada deadline mendesak")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #9e9e9e; padding: 12px;")
        self.empty_label.setFont(QFont("Segoe UI", 9))

        if not urgent:
            self.items_container.addWidget(self.empty_label)
        else:
            for info in urgent:
                item = self._create_compact_item(info)
                self.items_container.addWidget(item)

    def _create_compact_item(self, info: DeadlineInfo) -> QFrame:
        """Create a compact deadline item."""
        frame = QFrame()
        frame.setCursor(Qt.PointingHandCursor)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {STATUS_CONFIG[info.status]['bg']};
                border-radius: 4px;
                padding: 4px;
            }}
            QFrame:hover {{
                background-color: {STATUS_CONFIG[info.status]['color']}20;
            }}
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # Status icon
        icon = QLabel(STATUS_CONFIG[info.status]['icon'])
        icon.setFont(QFont("Segoe UI", 10))
        layout.addWidget(icon)

        # Nomor
        nomor = QLabel(info.transaksi_nomor)
        nomor.setFont(QFont("Segoe UI", 9))
        nomor.setStyleSheet(f"color: {STATUS_CONFIG[info.status]['color']};")
        layout.addWidget(nomor, 1)

        # Days
        days = QLabel(info.format_days_remaining())
        days.setFont(QFont("Segoe UI", 9, QFont.Bold))
        days.setStyleSheet(f"color: {STATUS_CONFIG[info.status]['color']};")
        layout.addWidget(days)

        # Make clickable
        frame.mousePressEvent = lambda e: self.deadline_clicked.emit(info.transaksi_id)

        return frame


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_deadline_tracker(
    transaksi_list: Optional[List[Dict[str, Any]]] = None,
    parent: Optional[QWidget] = None
) -> DeadlineTrackerWidget:
    """
    Factory function to create a DeadlineTrackerWidget.

    Args:
        transaksi_list: Initial transaksi data
        parent: Parent widget

    Returns:
        Configured DeadlineTrackerWidget instance
    """
    tracker = DeadlineTrackerWidget(parent=parent)

    if transaksi_list:
        tracker.load_deadlines(transaksi_list)

    return tracker


def create_compact_deadline(
    deadlines: Optional[List[DeadlineInfo]] = None,
    parent: Optional[QWidget] = None
) -> CompactDeadlineWidget:
    """
    Factory function to create a CompactDeadlineWidget.

    Args:
        deadlines: Initial deadline data
        parent: Parent widget

    Returns:
        Configured CompactDeadlineWidget instance
    """
    widget = CompactDeadlineWidget(parent=parent)

    if deadlines:
        widget.set_deadlines(deadlines)

    return widget
