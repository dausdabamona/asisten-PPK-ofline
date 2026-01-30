"""
PPK DOCUMENT FACTORY - Workflow Dashboard Page
===============================================
Enhanced workflow-centric dashboard page.

Features:
- Kanban, List, and Timeline view modes
- Integrated quick actions
- Notification center
- Deadline tracker
- Analytics summary

Author: PPK Document Factory Team
Version: 4.0
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QStackedWidget, QSizePolicy, QScrollArea,
    QSplitter, QButtonGroup, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from app.ui.base.base_page import BasePage

# Import workflow components
from app.ui.components.kanban_board import KanbanBoard, create_kanban_board
from app.ui.components.workflow_timeline import (
    WorkflowTimeline, WorkflowProgress, TimelineEvent
)
from app.ui.components.workflow_analytics import (
    WorkflowAnalyticsWidget, WorkflowMetrics
)
from app.ui.components.deadline_tracker import (
    DeadlineTrackerWidget, CompactDeadlineWidget
)
from app.ui.components.workflow_notifications import (
    NotificationCenter, NotificationService
)
from app.ui.components.workflow_quick_actions import (
    WorkflowQuickActionsWidget, create_quick_actions
)


# =============================================================================
# CONSTANTS
# =============================================================================

class ViewMode(Enum):
    """Dashboard view modes."""
    KANBAN = "kanban"
    LIST = "list"
    TIMELINE = "timeline"


# =============================================================================
# VIEW MODE TOGGLE
# =============================================================================

class ViewModeToggle(QFrame):
    """Toggle buttons for switching view modes."""

    mode_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._current_mode = ViewMode.KANBAN.value
        self._setup_ui()

    def _setup_ui(self):
        """Setup toggle UI."""
        self.setStyleSheet("""
            ViewModeToggle {
                background-color: #f5f5f5;
                border-radius: 6px;
                padding: 2px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        modes = [
            (ViewMode.KANBAN.value, "Kanban", "\U0001F4CB"),
            (ViewMode.LIST.value, "List", "\U0001F4C3"),
            (ViewMode.TIMELINE.value, "Timeline", "\U0001F4C5"),
        ]

        self.buttons = {}
        for mode, label, icon in modes:
            btn = QPushButton(f"{icon} {label}")
            btn.setCheckable(True)
            btn.setFixedHeight(32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, m=mode: self._on_mode_clicked(m))

            self.button_group.addButton(btn)
            self.buttons[mode] = btn
            layout.addWidget(btn)

            self._apply_button_style(btn, mode == self._current_mode)

        # Set initial
        self.buttons[self._current_mode].setChecked(True)

    def _apply_button_style(self, btn: QPushButton, active: bool):
        """Apply button styling."""
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196f3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #616161;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)

    def _on_mode_clicked(self, mode: str):
        """Handle mode button click."""
        self._current_mode = mode

        for m, btn in self.buttons.items():
            self._apply_button_style(btn, m == mode)

        self.mode_changed.emit(mode)

    def set_mode(self, mode: str):
        """Set current mode programmatically."""
        if mode in self.buttons:
            self.buttons[mode].setChecked(True)
            self._on_mode_clicked(mode)

    def get_mode(self) -> str:
        """Get current mode."""
        return self._current_mode


# =============================================================================
# GANTT/TIMELINE VIEW
# =============================================================================

class GanttTimelineView(QWidget):
    """
    Gantt-style timeline view showing transaksi over time.

    Features:
    - Horizontal bars showing transaksi duration
    - Phase colors
    - Scrollable by date
    """

    transaksi_clicked = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._transaksi_list: List[Dict[str, Any]] = []
        self._current_month = date.today().replace(day=1)

        self._setup_ui()

    def _setup_ui(self):
        """Setup timeline UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Navigation header
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("< Prev")
        self.prev_btn.clicked.connect(self._go_prev_month)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        nav_layout.addWidget(self.prev_btn)

        nav_layout.addStretch()

        self.month_label = QLabel()
        self.month_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.month_label.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.month_label)

        nav_layout.addStretch()

        self.next_btn = QPushButton("Next >")
        self.next_btn.clicked.connect(self._go_next_month)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet(self.prev_btn.styleSheet())
        nav_layout.addWidget(self.next_btn)

        layout.addLayout(nav_layout)

        # Timeline content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
        """)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(16, 16, 16, 16)
        self.content_layout.setSpacing(8)
        self.content_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area, 1)

        self._update_month_label()

    def _update_month_label(self):
        """Update month label."""
        self.month_label.setText(
            self._current_month.strftime("%B %Y")
        )

    def _go_prev_month(self):
        """Go to previous month."""
        if self._current_month.month == 1:
            self._current_month = self._current_month.replace(
                year=self._current_month.year - 1, month=12
            )
        else:
            self._current_month = self._current_month.replace(
                month=self._current_month.month - 1
            )
        self._update_month_label()
        self._rebuild_timeline()

    def _go_next_month(self):
        """Go to next month."""
        if self._current_month.month == 12:
            self._current_month = self._current_month.replace(
                year=self._current_month.year + 1, month=1
            )
        else:
            self._current_month = self._current_month.replace(
                month=self._current_month.month + 1
            )
        self._update_month_label()
        self._rebuild_timeline()

    def _rebuild_timeline(self):
        """Rebuild timeline display."""
        # Clear existing
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Filter transaksi for current month
        month_start = self._current_month
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)

        for t in self._transaksi_list:
            # Create timeline row
            row = self._create_timeline_row(t, month_start, month_end)
            if row:
                self.content_layout.addWidget(row)

        if self.content_layout.count() == 0:
            empty = QLabel("Tidak ada transaksi di bulan ini")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #9e9e9e; padding: 40px;")
            self.content_layout.addWidget(empty)

        self.content_layout.addStretch()

    def _create_timeline_row(
        self,
        transaksi: Dict[str, Any],
        month_start: date,
        month_end: date
    ) -> Optional[QFrame]:
        """Create a timeline row for a transaksi."""
        created = transaksi.get("created_at")
        if not created:
            return None

        if isinstance(created, str):
            created = datetime.fromisoformat(created).date()
        elif isinstance(created, datetime):
            created = created.date()

        # Calculate deadline
        deadline = transaksi.get("deadline")
        if deadline:
            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline).date()
            elif isinstance(deadline, datetime):
                deadline = deadline.date()
        else:
            deadline = created + timedelta(days=30)

        # Check if overlaps with current month
        if deadline < month_start or created > month_end:
            return None

        row = QFrame()
        row.setFixedHeight(36)
        row.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Nomor label
        nomor = QLabel(transaksi.get("nomor", ""))
        nomor.setFixedWidth(120)
        nomor.setFont(QFont("Segoe UI", 9))
        layout.addWidget(nomor)

        # Progress bar
        bar_container = QFrame()
        bar_container.setFixedHeight(24)
        bar_layout = QHBoxLayout(bar_container)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(0)

        # Calculate bar position and width
        days_in_month = (month_end - month_start).days
        start_offset = max(0, (created - month_start).days)
        end_offset = min(days_in_month, (deadline - month_start).days)

        start_pct = (start_offset / days_in_month) * 100
        width_pct = ((end_offset - start_offset) / days_in_month) * 100

        # Fase color
        fase = transaksi.get("fase", 1)
        fase_colors = {
            1: "#9c27b0", 2: "#2196f3", 3: "#ff9800",
            4: "#4caf50", 5: "#607d8b"
        }
        color = fase_colors.get(fase, "#607d8b")

        status = transaksi.get("status", "")
        if status == "Selesai":
            color = "#4caf50"

        bar_container.setStyleSheet(f"""
            QFrame {{
                background-color: #f5f5f5;
                border-radius: 4px;
            }}
        """)

        # Inner bar
        inner = QFrame(bar_container)
        inner.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
        inner.setGeometry(
            int(start_pct * 2),  # Scale for container width
            4,
            int(max(width_pct * 2, 20)),
            16
        )

        layout.addWidget(bar_container, 1)

        # Status label
        status_label = QLabel(f"Fase {fase}" if status != "Selesai" else "\u2705 Selesai")
        status_label.setFixedWidth(80)
        status_label.setFont(QFont("Segoe UI", 9))
        status_label.setStyleSheet(f"color: {color};")
        layout.addWidget(status_label)

        # Click handler
        transaksi_id = str(transaksi.get("id", ""))
        row.mousePressEvent = lambda e: self.transaksi_clicked.emit(transaksi_id)

        return row

    def set_data(self, transaksi_list: List[Dict[str, Any]]):
        """Set transaksi data."""
        self._transaksi_list = transaksi_list
        self._rebuild_timeline()


# =============================================================================
# WORKFLOW DASHBOARD PAGE
# =============================================================================

class WorkflowDashboardPage(BasePage):
    """
    Enhanced workflow-centric dashboard page.

    Features:
    - Multiple view modes (Kanban, List, Timeline)
    - Quick actions
    - Notification center
    - Deadline tracking
    - Analytics summary

    Signals:
        transaksi_selected(str): Emit transaksi_id when selected
        view_mode_changed(str): Emit when view mode changes
        refresh_requested(): Emit when refresh is requested
    """

    transaksi_selected = Signal(str)
    view_mode_changed = Signal(str)
    refresh_requested = Signal()

    REFRESH_INTERVAL = 30000  # 30 seconds

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(
            page_id="workflow_dashboard",
            page_title="Workflow Dashboard",
            can_go_back=False,
            parent=parent
        )

        self._transaksi_list: List[Dict[str, Any]] = []
        self._current_mekanisme = "Semua"

        self._setup_ui()
        self._setup_refresh_timer()
        self._setup_shortcuts()

    def _setup_ui(self):
        """Setup dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # ----- Header -----
        header_layout = QHBoxLayout()

        # Title
        title_layout = QHBoxLayout()
        title_layout.setSpacing(12)

        icon = QLabel("\U0001F4CA")
        icon.setFont(QFont("Segoe UI", 20))
        title_layout.addWidget(icon)

        title = QLabel("Workflow Dashboard")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #212121;")
        title_layout.addWidget(title)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # View mode toggle
        self.view_toggle = ViewModeToggle()
        self.view_toggle.mode_changed.connect(self._on_view_mode_changed)
        header_layout.addWidget(self.view_toggle)

        # Notification center
        self.notification_center = NotificationCenter()
        self.notification_center.notification_clicked.connect(
            self._on_notification_clicked
        )
        header_layout.addWidget(self.notification_center)

        layout.addLayout(header_layout)

        # ----- Top Row: Quick Actions + Notifications Summary -----
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # Quick actions
        self.quick_actions = WorkflowQuickActionsWidget(context="dashboard")
        self.quick_actions.action_executed.connect(self._on_quick_action)
        self.quick_actions.setMaximumHeight(100)
        top_row.addWidget(self.quick_actions, 2)

        # Compact deadline widget
        self.compact_deadline = CompactDeadlineWidget()
        self.compact_deadline.view_all_clicked.connect(self._show_full_deadline_tracker)
        self.compact_deadline.deadline_clicked.connect(self.transaksi_selected.emit)
        self.compact_deadline.setMaximumHeight(100)
        self.compact_deadline.setMaximumWidth(300)
        top_row.addWidget(self.compact_deadline)

        layout.addLayout(top_row)

        # ----- Main Content (Stacked Views) -----
        self.view_stack = QStackedWidget()

        # Kanban view
        self.kanban_view = KanbanBoard()
        self.kanban_view.transaksi_selected.connect(self.transaksi_selected.emit)
        self.kanban_view.transaksi_moved.connect(self._on_transaksi_moved)
        self.view_stack.addWidget(self.kanban_view)

        # List view (placeholder - would use base_list_page pattern)
        self.list_view = QFrame()
        self.list_view.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        list_layout = QVBoxLayout(self.list_view)
        list_placeholder = QLabel("List View - Coming Soon")
        list_placeholder.setAlignment(Qt.AlignCenter)
        list_placeholder.setStyleSheet("color: #9e9e9e;")
        list_layout.addWidget(list_placeholder)
        self.view_stack.addWidget(self.list_view)

        # Timeline view
        self.timeline_view = GanttTimelineView()
        self.timeline_view.transaksi_clicked.connect(self.transaksi_selected.emit)
        self.view_stack.addWidget(self.timeline_view)

        layout.addWidget(self.view_stack, 1)

        # ----- Bottom Row: Deadline Tracker + Analytics -----
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)

        # Deadline tracker (collapsible)
        self.deadline_tracker = DeadlineTrackerWidget()
        self.deadline_tracker.deadline_clicked.connect(self.transaksi_selected.emit)
        self.deadline_tracker.setMaximumHeight(200)
        bottom_row.addWidget(self.deadline_tracker, 1)

        # Analytics summary
        self.analytics_widget = WorkflowAnalyticsWidget()
        self.analytics_widget.fase_selected.connect(self._on_fase_selected)
        self.analytics_widget.setMaximumHeight(200)
        bottom_row.addWidget(self.analytics_widget, 1)

        layout.addLayout(bottom_row)

    def _setup_refresh_timer(self):
        """Setup auto-refresh timer."""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(self.REFRESH_INTERVAL)

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        from PySide6.QtGui import QShortcut, QKeySequence

        # View mode shortcuts
        QShortcut(QKeySequence("1"), self, lambda: self.view_toggle.set_mode("kanban"))
        QShortcut(QKeySequence("2"), self, lambda: self.view_toggle.set_mode("list"))
        QShortcut(QKeySequence("3"), self, lambda: self.view_toggle.set_mode("timeline"))

        # Refresh
        QShortcut(QKeySequence("R"), self, self.refresh)

        # New transaksi
        QShortcut(QKeySequence("N"), self, lambda: self._on_quick_action("new_up", {}))

    def _on_view_mode_changed(self, mode: str):
        """Handle view mode change."""
        mode_index = {
            "kanban": 0,
            "list": 1,
            "timeline": 2
        }
        self.view_stack.setCurrentIndex(mode_index.get(mode, 0))
        self.view_mode_changed.emit(mode)

    def _on_quick_action(self, action_id: str, context: Dict[str, Any]):
        """Handle quick action execution."""
        if action_id == "new_up":
            self.navigate_to.emit("new_up")
        elif action_id == "new_tup":
            self.navigate_to.emit("new_tup")
        elif action_id == "new_ls":
            self.navigate_to.emit("new_ls")
        elif action_id == "batch_docs":
            # Handle batch document generation
            pass

    def _on_transaksi_moved(
        self,
        transaksi_id: str,
        from_fase: int,
        to_fase: int
    ):
        """Handle transaksi moved in Kanban."""
        # This would call workflow service to validate and execute
        # For now, just emit and let parent handle
        self.refresh_requested.emit()

    def _on_notification_clicked(self, notification_id: str):
        """Handle notification click."""
        # Find transaksi_id from notification and navigate
        pass

    def _on_fase_selected(self, fase: int):
        """Handle fase selection in analytics."""
        # Filter Kanban to show only this fase
        pass

    def _show_full_deadline_tracker(self):
        """Show full deadline tracker dialog."""
        # Could open a dialog or navigate to a page
        pass

    # -------------------------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------------------------

    def set_data(self, transaksi_list: List[Dict[str, Any]]):
        """Set transaksi data for all views."""
        self._transaksi_list = transaksi_list

        # Update Kanban
        self.kanban_view.set_data(transaksi_list)

        # Update Timeline
        self.timeline_view.set_data(transaksi_list)

        # Update Analytics
        self.analytics_widget.set_data(transaksi_list)

        # Update Deadline Tracker
        self.deadline_tracker.load_deadlines(transaksi_list)

        # Update Compact Deadline
        deadline_infos = self.deadline_tracker.get_all_deadlines()
        self.compact_deadline.set_deadlines(deadline_infos)

    def refresh(self):
        """Refresh all data."""
        self.refresh_requested.emit()
        # Re-apply current data
        self.set_data(self._transaksi_list)

    def set_mekanisme_filter(self, mekanisme: str):
        """Set mekanisme filter."""
        self._current_mekanisme = mekanisme
        self.kanban_view.filter_by(mekanisme=mekanisme)

    def get_current_view_mode(self) -> str:
        """Get current view mode."""
        return self.view_toggle.get_mode()

    def set_view_mode(self, mode: str):
        """Set view mode."""
        self.view_toggle.set_mode(mode)

    def add_notification(self, notification):
        """Add a notification to the center."""
        self.notification_center.add_notification(notification)

    def set_notifications(self, notifications):
        """Set all notifications."""
        self.notification_center.set_notifications(notifications)

    def _load_data(self):
        """Load data from database (override from BasePage)."""
        # This would be called by parent/controller with actual data
        pass


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_workflow_dashboard(
    transaksi_list: Optional[List[Dict[str, Any]]] = None,
    parent: Optional[QWidget] = None
) -> WorkflowDashboardPage:
    """
    Factory function to create WorkflowDashboardPage.

    Args:
        transaksi_list: Initial transaksi data
        parent: Parent widget

    Returns:
        Configured WorkflowDashboardPage instance
    """
    page = WorkflowDashboardPage(parent=parent)

    if transaksi_list:
        page.set_data(transaksi_list)

    return page
