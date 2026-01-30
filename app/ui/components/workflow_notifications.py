"""
PPK DOCUMENT FACTORY - Workflow Notification System
====================================================
Sistem notifikasi untuk workflow events.

Features:
- WorkflowNotification: Data class untuk notification
- NotificationItem: Single notification display
- NotificationCenter: Bell icon dengan dropdown panel
- NotificationService: Background checking service

Author: PPK Document Factory Team
Version: 4.0
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from uuid import uuid4

from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
    QMenu, QWidgetAction, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint, QObject
from PySide6.QtGui import QColor, QFont, QCursor


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

class NotificationType(Enum):
    """Types of workflow notifications."""
    DEADLINE_WARNING = "deadline_warning"
    DEADLINE_URGENT = "deadline_urgent"
    DEADLINE_OVERDUE = "deadline_overdue"
    FASE_COMPLETE = "fase_complete"
    DOCUMENT_REQUIRED = "document_required"
    DOCUMENT_CREATED = "document_created"
    TRANSAKSI_STUCK = "transaksi_stuck"
    TRANSAKSI_CREATED = "transaksi_created"
    TRANSAKSI_COMPLETED = "transaksi_completed"
    PAYMENT_PENDING = "payment_pending"
    APPROVAL_REQUIRED = "approval_required"
    SYSTEM_INFO = "system_info"


class NotificationPriority(Enum):
    """Priority levels for notifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Notification type configuration
NOTIFICATION_CONFIG = {
    "deadline_warning": {
        "icon": "\U0001F7E1",  # Yellow circle
        "color": "#ff9800",
        "priority": "medium"
    },
    "deadline_urgent": {
        "icon": "\U0001F7E0",  # Orange circle
        "color": "#ff5722",
        "priority": "high"
    },
    "deadline_overdue": {
        "icon": "\U0001F534",  # Red circle
        "color": "#f44336",
        "priority": "urgent"
    },
    "fase_complete": {
        "icon": "\u2705",  # Check mark
        "color": "#4caf50",
        "priority": "low"
    },
    "document_required": {
        "icon": "\U0001F4C4",  # Document
        "color": "#ff9800",
        "priority": "medium"
    },
    "document_created": {
        "icon": "\U0001F4DD",  # Memo
        "color": "#4caf50",
        "priority": "low"
    },
    "transaksi_stuck": {
        "icon": "\u26A0\uFE0F",  # Warning
        "color": "#ff9800",
        "priority": "high"
    },
    "transaksi_created": {
        "icon": "\U0001F195",  # New
        "color": "#2196f3",
        "priority": "low"
    },
    "transaksi_completed": {
        "icon": "\U0001F389",  # Party popper
        "color": "#4caf50",
        "priority": "low"
    },
    "payment_pending": {
        "icon": "\U0001F4B0",  # Money bag
        "color": "#ff9800",
        "priority": "medium"
    },
    "approval_required": {
        "icon": "\U0001F44D",  # Thumbs up
        "color": "#2196f3",
        "priority": "high"
    },
    "system_info": {
        "icon": "\u2139\uFE0F",  # Info
        "color": "#607d8b",
        "priority": "low"
    },
}

# Priority colors
PRIORITY_COLORS = {
    "low": "#9e9e9e",
    "medium": "#2196f3",
    "high": "#ff9800",
    "urgent": "#f44336"
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class WorkflowNotification:
    """
    Data class representing a workflow notification.

    Attributes:
        id: Unique notification identifier
        type: Notification type
        title: Notification title
        message: Notification message
        transaksi_id: Related transaksi ID (optional)
        timestamp: When notification was created
        read: Whether notification has been read
        priority: Priority level
        metadata: Additional data
    """
    type: str
    title: str
    message: str
    transaksi_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    read: bool = False
    priority: str = "medium"
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid4())
        if self.metadata is None:
            self.metadata = {}

        # Auto-set priority from type config if not specified
        config = NOTIFICATION_CONFIG.get(self.type, {})
        if config and self.priority == "medium":
            self.priority = config.get("priority", "medium")

    def get_icon(self) -> str:
        """Get icon for this notification type."""
        config = NOTIFICATION_CONFIG.get(self.type, NOTIFICATION_CONFIG["system_info"])
        return config["icon"]

    def get_color(self) -> str:
        """Get color for this notification type."""
        config = NOTIFICATION_CONFIG.get(self.type, NOTIFICATION_CONFIG["system_info"])
        return config["color"]

    def format_time_ago(self) -> str:
        """Format timestamp as relative time."""
        now = datetime.now()
        diff = now - self.timestamp

        if diff.days > 7:
            return self.timestamp.strftime("%d %b")
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

    def mark_read(self):
        """Mark notification as read."""
        self.read = True


# =============================================================================
# NOTIFICATION ITEM
# =============================================================================

class NotificationItem(QFrame):
    """
    Single notification display.

    Features:
    - Icon based on type
    - Unread indicator
    - Time ago display
    - Click to mark read and navigate

    Signals:
        clicked(str): Emit notification_id when clicked
        dismissed(str): Emit notification_id when dismissed
    """

    clicked = Signal(str)
    dismissed = Signal(str)

    def __init__(
        self,
        notification: WorkflowNotification,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.notification = notification
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        """Setup item UI."""
        self.setMinimumHeight(70)
        self.setMaximumHeight(90)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        # Unread indicator
        self.unread_dot = QLabel()
        self.unread_dot.setFixedSize(8, 8)
        self.unread_dot.setStyleSheet("""
            QLabel {
                background-color: #2196f3;
                border-radius: 4px;
            }
        """)
        self.unread_dot.setVisible(not self.notification.read)
        layout.addWidget(self.unread_dot, alignment=Qt.AlignTop)

        # Icon
        self.icon_label = QLabel(self.notification.get_icon())
        self.icon_label.setFont(QFont("Segoe UI", 16))
        self.icon_label.setFixedWidth(30)
        layout.addWidget(self.icon_label, alignment=Qt.AlignTop)

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        # Title
        self.title_label = QLabel(self.notification.title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Bold if not self.notification.read else QFont.Normal))
        self.title_label.setStyleSheet(f"color: {self.notification.get_color()};")
        self.title_label.setWordWrap(True)
        content_layout.addWidget(self.title_label)

        # Message
        self.message_label = QLabel(self.notification.message)
        self.message_label.setFont(QFont("Segoe UI", 9))
        self.message_label.setStyleSheet("color: #616161;")
        self.message_label.setWordWrap(True)
        self.message_label.setMaximumHeight(36)
        content_layout.addWidget(self.message_label)

        # Time ago
        self.time_label = QLabel(self.notification.format_time_ago())
        self.time_label.setFont(QFont("Segoe UI", 8))
        self.time_label.setStyleSheet("color: #9e9e9e;")
        content_layout.addWidget(self.time_label)

        layout.addLayout(content_layout, 1)

        # Dismiss button
        self.dismiss_btn = QPushButton("\u2715")  # X
        self.dismiss_btn.setFixedSize(20, 20)
        self.dismiss_btn.setCursor(Qt.PointingHandCursor)
        self.dismiss_btn.clicked.connect(self._on_dismiss)
        self.dismiss_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #bdbdbd;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #757575;
                background-color: #f5f5f5;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.dismiss_btn, alignment=Qt.AlignTop)

    def _apply_style(self):
        """Apply styling based on read state."""
        bg_color = "#ffffff" if self.notification.read else "#f5f5f5"
        border_color = self.notification.get_color() if not self.notification.read else "#e0e0e0"

        self.setStyleSheet(f"""
            NotificationItem {{
                background-color: {bg_color};
                border-bottom: 1px solid #eeeeee;
                border-left: 3px solid {border_color};
            }}
            NotificationItem:hover {{
                background-color: #fafafa;
            }}
        """)

    def _on_dismiss(self):
        """Handle dismiss button click."""
        self.dismissed.emit(self.notification.id)

    def mousePressEvent(self, event):
        """Handle click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.notification.id)
        super().mousePressEvent(event)

    def mark_read(self):
        """Mark as read and update display."""
        self.notification.mark_read()
        self.unread_dot.setVisible(False)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Normal))
        self._apply_style()


# =============================================================================
# NOTIFICATION PANEL
# =============================================================================

class NotificationPanel(QFrame):
    """
    Dropdown panel for notifications.

    Features:
    - Scrollable notification list
    - Mark all as read
    - Clear all
    """

    notification_clicked = Signal(str)
    notification_dismissed = Signal(str)
    mark_all_read = Signal()
    clear_all = Signal()

    MAX_DISPLAY = 50

    def __init__(
        self,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self._notifications: List[WorkflowNotification] = []
        self._items: List[NotificationItem] = []

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedSize(360, 400)

        self._setup_ui()
        self._setup_shadow()

    def _setup_ui(self):
        """Setup panel UI."""
        self.setStyleSheet("""
            NotificationPanel {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-bottom: 1px solid #e0e0e0;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)

        title_label = QLabel("Notifikasi")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setStyleSheet("color: #212121;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Mark all read button
        self.mark_read_btn = QPushButton("Tandai Dibaca")
        self.mark_read_btn.setCursor(Qt.PointingHandCursor)
        self.mark_read_btn.clicked.connect(self.mark_all_read.emit)
        self.mark_read_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1976d2;
                border: none;
                font-size: 10px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
                border-radius: 4px;
            }
        """)
        header_layout.addWidget(self.mark_read_btn)

        # Clear button
        self.clear_btn = QPushButton("Hapus")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_all.emit)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #757575;
                border: none;
                font-size: 10px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border-radius: 4px;
            }
        """)
        header_layout.addWidget(self.clear_btn)

        layout.addWidget(header)

        # Notifications list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
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

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)
        self.list_layout.setAlignment(Qt.AlignTop)

        # Empty state
        self.empty_label = QLabel("Tidak ada notifikasi")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #9e9e9e; padding: 40px;")
        self.list_layout.addWidget(self.empty_label)

        self.scroll_area.setWidget(self.list_widget)
        layout.addWidget(self.scroll_area, 1)

    def _setup_shadow(self):
        """Add drop shadow."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def set_notifications(self, notifications: List[WorkflowNotification]):
        """Set notifications to display."""
        self._notifications = notifications

        # Clear existing items
        for item in self._items:
            self.list_layout.removeWidget(item)
            item.deleteLater()
        self._items.clear()

        # Show/hide empty state
        self.empty_label.setVisible(len(notifications) == 0)

        # Sort by timestamp (newest first) and priority
        sorted_notifs = sorted(
            notifications,
            key=lambda n: (n.read, -n.timestamp.timestamp()),
        )

        # Add items (limit display)
        for notif in sorted_notifs[:self.MAX_DISPLAY]:
            item = NotificationItem(notif)
            item.clicked.connect(self.notification_clicked.emit)
            item.dismissed.connect(self.notification_dismissed.emit)
            self._items.append(item)
            self.list_layout.insertWidget(self.list_layout.count() - 1, item)

    def add_notification(self, notification: WorkflowNotification):
        """Add a new notification."""
        self._notifications.insert(0, notification)
        self.set_notifications(self._notifications)

    def remove_notification(self, notification_id: str):
        """Remove a notification."""
        self._notifications = [n for n in self._notifications if n.id != notification_id]
        self.set_notifications(self._notifications)

    def mark_notification_read(self, notification_id: str):
        """Mark a notification as read."""
        for item in self._items:
            if item.notification.id == notification_id:
                item.mark_read()
                break

    def mark_all_notifications_read(self):
        """Mark all notifications as read."""
        for item in self._items:
            item.mark_read()

    def clear_notifications(self):
        """Clear all notifications."""
        self._notifications.clear()
        self.set_notifications([])


# =============================================================================
# NOTIFICATION CENTER (Bell Icon)
# =============================================================================

class NotificationCenter(QWidget):
    """
    Bell icon widget with notification count badge and dropdown panel.

    Features:
    - Bell icon with unread count badge
    - Click to open dropdown panel
    - Signals for notification interactions

    Signals:
        notification_clicked(str): Emit notification_id when clicked
        notification_count_changed(int): Emit when count changes
    """

    notification_clicked = Signal(str)
    notification_count_changed = Signal(int)

    def __init__(
        self,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self._notifications: List[WorkflowNotification] = []
        self._panel: Optional[NotificationPanel] = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup notification center UI."""
        self.setFixedSize(44, 44)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Bell button
        self.bell_btn = QPushButton("\U0001F514")  # Bell
        self.bell_btn.setFixedSize(40, 40)
        self.bell_btn.setFont(QFont("Segoe UI", 18))
        self.bell_btn.setCursor(Qt.PointingHandCursor)
        self.bell_btn.clicked.connect(self._toggle_panel)
        self.bell_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #eeeeee;
            }
        """)
        layout.addWidget(self.bell_btn)

        # Badge (overlaid on button)
        self.badge = QLabel("0")
        self.badge.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setFixedSize(18, 18)
        self.badge.setStyleSheet("""
            QLabel {
                background-color: #f44336;
                color: white;
                border-radius: 9px;
            }
        """)
        self.badge.setParent(self)
        self.badge.move(24, 4)
        self.badge.setVisible(False)

    def _toggle_panel(self):
        """Toggle notification panel visibility."""
        if self._panel and self._panel.isVisible():
            self._panel.hide()
        else:
            self._show_panel()

    def _show_panel(self):
        """Show the notification panel."""
        if not self._panel:
            self._panel = NotificationPanel()
            self._panel.notification_clicked.connect(self._on_notification_clicked)
            self._panel.notification_dismissed.connect(self._on_notification_dismissed)
            self._panel.mark_all_read.connect(self._on_mark_all_read)
            self._panel.clear_all.connect(self._on_clear_all)

        self._panel.set_notifications(self._notifications)

        # Position below the button
        global_pos = self.mapToGlobal(QPoint(0, self.height()))
        # Adjust to not go off screen
        screen = QApplication.primaryScreen().geometry()
        panel_x = global_pos.x() - self._panel.width() + self.width()
        panel_y = global_pos.y() + 4

        if panel_x < 0:
            panel_x = global_pos.x()
        if panel_y + self._panel.height() > screen.height():
            panel_y = global_pos.y() - self._panel.height() - self.height() - 8

        self._panel.move(panel_x, panel_y)
        self._panel.show()

    def _on_notification_clicked(self, notification_id: str):
        """Handle notification click."""
        # Mark as read
        for notif in self._notifications:
            if notif.id == notification_id:
                notif.mark_read()
                break

        if self._panel:
            self._panel.mark_notification_read(notification_id)

        self._update_badge()
        self.notification_clicked.emit(notification_id)

    def _on_notification_dismissed(self, notification_id: str):
        """Handle notification dismiss."""
        self._notifications = [n for n in self._notifications if n.id != notification_id]
        if self._panel:
            self._panel.remove_notification(notification_id)
        self._update_badge()

    def _on_mark_all_read(self):
        """Handle mark all as read."""
        for notif in self._notifications:
            notif.mark_read()
        if self._panel:
            self._panel.mark_all_notifications_read()
        self._update_badge()

    def _on_clear_all(self):
        """Handle clear all."""
        self._notifications.clear()
        if self._panel:
            self._panel.clear_notifications()
        self._update_badge()

    def _update_badge(self):
        """Update the unread count badge."""
        unread_count = sum(1 for n in self._notifications if not n.read)
        self.badge.setText(str(min(unread_count, 99)))
        self.badge.setVisible(unread_count > 0)
        self.notification_count_changed.emit(unread_count)

    # -------------------------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------------------------

    def add_notification(self, notification: WorkflowNotification):
        """Add a new notification."""
        self._notifications.insert(0, notification)
        if self._panel and self._panel.isVisible():
            self._panel.add_notification(notification)
        self._update_badge()

    def set_notifications(self, notifications: List[WorkflowNotification]):
        """Set all notifications."""
        self._notifications = notifications
        if self._panel and self._panel.isVisible():
            self._panel.set_notifications(notifications)
        self._update_badge()

    def get_notifications(self) -> List[WorkflowNotification]:
        """Get all notifications."""
        return self._notifications.copy()

    def get_unread(self) -> List[WorkflowNotification]:
        """Get unread notifications."""
        return [n for n in self._notifications if not n.read]

    def get_unread_count(self) -> int:
        """Get unread notification count."""
        return sum(1 for n in self._notifications if not n.read)

    def mark_read(self, notification_id: str):
        """Mark a specific notification as read."""
        for notif in self._notifications:
            if notif.id == notification_id:
                notif.mark_read()
                break
        if self._panel:
            self._panel.mark_notification_read(notification_id)
        self._update_badge()

    def mark_all_read(self):
        """Mark all notifications as read."""
        self._on_mark_all_read()

    def clear(self):
        """Clear all notifications."""
        self._on_clear_all()


# =============================================================================
# NOTIFICATION SERVICE
# =============================================================================

class NotificationService(QObject):
    """
    Background service for checking and creating notifications.

    Features:
    - Periodic deadline checking
    - Stuck transaksi detection
    - Incomplete document checking
    - Auto-notification creation

    Signals:
        notification_created(WorkflowNotification): Emit when new notification created
        check_completed(): Emit when check cycle completes
    """

    notification_created = Signal(object)
    check_completed = Signal()

    DEFAULT_INTERVAL = 5 * 60 * 1000  # 5 minutes in milliseconds
    STUCK_THRESHOLD_DAYS = 7  # Days before transaksi is considered stuck
    WARNING_DAYS = 7
    URGENT_DAYS = 3

    def __init__(
        self,
        check_interval: int = DEFAULT_INTERVAL,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)

        self.check_interval = check_interval
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._run_checks)

        self._transaksi_list: List[Dict[str, Any]] = []
        self._created_notification_ids: set = set()  # Track to avoid duplicates

    def start(self):
        """Start the notification service."""
        self._timer.start(self.check_interval)
        # Run initial check
        QTimer.singleShot(1000, self._run_checks)

    def stop(self):
        """Stop the notification service."""
        self._timer.stop()

    def set_interval(self, interval_ms: int):
        """Set check interval in milliseconds."""
        self.check_interval = interval_ms
        if self._timer.isActive():
            self._timer.setInterval(interval_ms)

    def set_transaksi_data(self, transaksi_list: List[Dict[str, Any]]):
        """Set transaksi data for checking."""
        self._transaksi_list = transaksi_list

    def _run_checks(self):
        """Run all notification checks."""
        self.check_deadlines()
        self.check_stuck_transaksi()
        self.check_incomplete_docs()
        self.check_completed.emit()

    def check_deadlines(self):
        """Check for approaching and overdue deadlines."""
        today = date.today()

        for t in self._transaksi_list:
            if t.get("status") == "Selesai":
                continue

            deadline = t.get("deadline")
            if not deadline:
                continue

            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline).date()
            elif isinstance(deadline, datetime):
                deadline = deadline.date()

            days_remaining = (deadline - today).days
            transaksi_id = str(t.get("id", ""))
            nomor = t.get("nomor", "")

            # Generate unique notification key
            notif_key = f"deadline_{transaksi_id}_{days_remaining // 3}"  # Group by 3-day windows

            if notif_key in self._created_notification_ids:
                continue

            if days_remaining < 0:
                # Overdue
                notif = self.create_notification(
                    type="deadline_overdue",
                    title=f"{nomor} melewati deadline",
                    message=f"Transaksi sudah terlambat {abs(days_remaining)} hari",
                    transaksi_id=transaksi_id
                )
                self._created_notification_ids.add(notif_key)

            elif days_remaining <= self.URGENT_DAYS:
                # Urgent (within 3 days)
                notif = self.create_notification(
                    type="deadline_urgent",
                    title=f"{nomor} deadline dalam {days_remaining} hari",
                    message=f"Segera selesaikan transaksi ini",
                    transaksi_id=transaksi_id
                )
                self._created_notification_ids.add(notif_key)

            elif days_remaining <= self.WARNING_DAYS:
                # Warning (within 7 days)
                notif = self.create_notification(
                    type="deadline_warning",
                    title=f"{nomor} deadline dalam {days_remaining} hari",
                    message=f"Perhatikan deadline transaksi",
                    transaksi_id=transaksi_id
                )
                self._created_notification_ids.add(notif_key)

    def check_stuck_transaksi(self):
        """Check for transaksi stuck in one fase for too long."""
        today = date.today()

        for t in self._transaksi_list:
            if t.get("status") == "Selesai":
                continue

            fase = t.get("fase", 1)
            if fase == 5:  # Don't check final fase
                continue

            fase_start = t.get("fase_start_date") or t.get("created_at")
            if not fase_start:
                continue

            if isinstance(fase_start, str):
                fase_start = datetime.fromisoformat(fase_start).date()
            elif isinstance(fase_start, datetime):
                fase_start = fase_start.date()

            days_in_fase = (today - fase_start).days
            transaksi_id = str(t.get("id", ""))
            nomor = t.get("nomor", "")

            notif_key = f"stuck_{transaksi_id}_{fase}"

            if notif_key in self._created_notification_ids:
                continue

            if days_in_fase >= self.STUCK_THRESHOLD_DAYS:
                notif = self.create_notification(
                    type="transaksi_stuck",
                    title=f"{nomor} stuck di Fase {fase}",
                    message=f"Transaksi sudah {days_in_fase} hari di fase yang sama",
                    transaksi_id=transaksi_id
                )
                self._created_notification_ids.add(notif_key)

    def check_incomplete_docs(self):
        """Check for transaksi with required but incomplete documents."""
        for t in self._transaksi_list:
            if t.get("status") == "Selesai":
                continue

            required_docs = t.get("required_documents", [])
            created_docs = t.get("created_documents", [])

            missing = [d for d in required_docs if d not in created_docs]

            if not missing:
                continue

            transaksi_id = str(t.get("id", ""))
            nomor = t.get("nomor", "")
            notif_key = f"doc_{transaksi_id}_{len(missing)}"

            if notif_key in self._created_notification_ids:
                continue

            notif = self.create_notification(
                type="document_required",
                title=f"{nomor} memerlukan dokumen",
                message=f"{len(missing)} dokumen wajib belum dibuat",
                transaksi_id=transaksi_id,
                metadata={"missing_docs": missing}
            )
            self._created_notification_ids.add(notif_key)

    def create_notification(
        self,
        type: str,
        title: str,
        message: str,
        transaksi_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowNotification:
        """
        Create and emit a new notification.

        Args:
            type: Notification type
            title: Notification title
            message: Notification message
            transaksi_id: Related transaksi ID
            metadata: Additional data

        Returns:
            Created WorkflowNotification
        """
        notif = WorkflowNotification(
            type=type,
            title=title,
            message=message,
            transaksi_id=transaksi_id,
            metadata=metadata
        )

        self.notification_created.emit(notif)
        return notif

    def get_unread(self) -> List[WorkflowNotification]:
        """
        Get unread notifications.

        Note: This should be implemented with database/storage
        """
        return []

    def mark_read(self, notification_id: str):
        """Mark notification as read."""
        pass

    def mark_all_read(self):
        """Mark all notifications as read."""
        pass

    def clear_tracking(self):
        """Clear notification tracking (for fresh check cycle)."""
        self._created_notification_ids.clear()


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_notification_center(
    notifications: Optional[List[WorkflowNotification]] = None,
    parent: Optional[QWidget] = None
) -> NotificationCenter:
    """
    Factory function to create a NotificationCenter.

    Args:
        notifications: Initial notifications
        parent: Parent widget

    Returns:
        Configured NotificationCenter instance
    """
    center = NotificationCenter(parent=parent)

    if notifications:
        center.set_notifications(notifications)

    return center


def create_notification_service(
    check_interval: int = NotificationService.DEFAULT_INTERVAL,
    transaksi_list: Optional[List[Dict[str, Any]]] = None,
    parent: Optional[QObject] = None
) -> NotificationService:
    """
    Factory function to create a NotificationService.

    Args:
        check_interval: Check interval in milliseconds
        transaksi_list: Initial transaksi data
        parent: Parent QObject

    Returns:
        Configured NotificationService instance
    """
    service = NotificationService(check_interval=check_interval, parent=parent)

    if transaksi_list:
        service.set_transaksi_data(transaksi_list)

    return service
