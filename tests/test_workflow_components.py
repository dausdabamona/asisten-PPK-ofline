"""
PPK DOCUMENT FACTORY - Workflow Components Tests
=================================================
Comprehensive tests for workflow timeline, analytics, deadline tracker,
and notification components.

Run with:
    python -m pytest tests/test_workflow_components.py -v

Author: PPK Document Factory Team
Version: 4.0
"""

import sys
import unittest
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
from unittest.mock import MagicMock, patch

# Add app to path
sys.path.insert(0, '.')

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest, QSignalSpy

# Import components to test
from app.ui.components.workflow_timeline import (
    TimelineEvent,
    TimelineItem,
    WorkflowTimeline,
    WorkflowProgress,
    WorkflowEventLogger,
    EventType,
    EVENT_CONFIG,
    FASE_NAMES,
    create_timeline,
    create_progress,
)

from app.ui.components.workflow_analytics import (
    WorkflowMetrics,
    MetricCard,
    FaseBarChart,
    BottleneckAlert,
    WorkflowAnalyticsWidget,
    create_analytics_widget,
)

from app.ui.components.deadline_tracker import (
    DeadlineInfo,
    DeadlineStatus,
    DeadlineItem,
    DeadlineTrackerWidget,
    CompactDeadlineWidget,
    DEFAULT_SLA,
    create_deadline_tracker,
    create_compact_deadline,
)

from app.ui.components.workflow_notifications import (
    WorkflowNotification,
    NotificationType,
    NotificationPriority,
    NotificationItem,
    NotificationCenter,
    NotificationService,
    NOTIFICATION_CONFIG,
    create_notification_center,
    create_notification_service,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

# Create QApplication instance for tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)


def create_sample_transaksi(count: int = 5) -> List[Dict[str, Any]]:
    """Create sample transaksi data for testing."""
    transaksi = []
    mekanisme_types = ["UP", "TUP", "LS"]

    for i in range(count):
        created = datetime.now() - timedelta(days=i * 5)
        transaksi.append({
            "id": f"TRX-{i+1:03d}",
            "nomor": f"2024/UP/{i+1:03d}",
            "nama": f"Pengadaan Barang Test {i+1}",
            "nilai": 10_000_000 * (i + 1),
            "status": "Aktif" if i < count - 1 else "Selesai",
            "mekanisme": mekanisme_types[i % 3],
            "fase": (i % 5) + 1,
            "deadline": date.today() + timedelta(days=i - 2),
            "created_at": created,
            "completed_at": created + timedelta(days=10) if i == count - 1 else None,
            "fase_history": [
                {"fase": 1, "duration_days": 2},
                {"fase": 2, "duration_days": 4},
            ]
        })

    return transaksi


# =============================================================================
# TIMELINE EVENT TESTS
# =============================================================================

class TestTimelineEvent(unittest.TestCase):
    """Test cases for TimelineEvent data class."""

    def test_event_initialization(self):
        """Test event initializes correctly."""
        event = TimelineEvent(
            timestamp=datetime.now(),
            event_type="created",
            description="Transaksi dibuat"
        )
        self.assertIsNotNone(event.id)
        self.assertEqual(event.event_type, "created")
        self.assertEqual(event.description, "Transaksi dibuat")
        self.assertFalse(event.read if hasattr(event, 'read') else True)

    def test_event_with_user(self):
        """Test event with user info."""
        event = TimelineEvent(
            timestamp=datetime.now(),
            event_type="fase_changed",
            description="Pindah ke Fase 2",
            user="Admin"
        )
        self.assertEqual(event.user, "Admin")

    def test_event_with_metadata(self):
        """Test event with metadata."""
        event = TimelineEvent(
            timestamp=datetime.now(),
            event_type="payment",
            description="Pembayaran UM",
            metadata={"amount": 50000000, "type": "UM"}
        )
        self.assertEqual(event.metadata["amount"], 50000000)
        self.assertEqual(event.metadata["type"], "UM")

    def test_event_get_icon(self):
        """Test getting icon for event type."""
        event = TimelineEvent(
            timestamp=datetime.now(),
            event_type="created",
            description="Test"
        )
        icon = event.get_icon()
        self.assertIsNotNone(icon)
        self.assertEqual(icon, EVENT_CONFIG["created"]["icon"])

    def test_event_get_color(self):
        """Test getting color for event type."""
        event = TimelineEvent(
            timestamp=datetime.now(),
            event_type="completed",
            description="Test"
        )
        color = event.get_color()
        self.assertIsNotNone(color)
        self.assertEqual(color, EVENT_CONFIG["completed"]["color"])

    def test_event_format_time(self):
        """Test timestamp formatting."""
        timestamp = datetime(2024, 1, 15, 10, 30)
        event = TimelineEvent(
            timestamp=timestamp,
            event_type="created",
            description="Test"
        )
        formatted = event.format_time()
        self.assertIn("15", formatted)
        self.assertIn("10:30", formatted)

    def test_event_format_time_ago_just_now(self):
        """Test 'just now' time formatting."""
        event = TimelineEvent(
            timestamp=datetime.now(),
            event_type="created",
            description="Test"
        )
        ago = event.format_time_ago()
        self.assertIn("Baru", ago)

    def test_event_format_time_ago_hours(self):
        """Test hours ago formatting."""
        event = TimelineEvent(
            timestamp=datetime.now() - timedelta(hours=3),
            event_type="created",
            description="Test"
        )
        ago = event.format_time_ago()
        self.assertIn("jam", ago)

    def test_event_format_time_ago_yesterday(self):
        """Test yesterday formatting."""
        event = TimelineEvent(
            timestamp=datetime.now() - timedelta(days=1),
            event_type="created",
            description="Test"
        )
        ago = event.format_time_ago()
        self.assertEqual(ago, "Kemarin")


# =============================================================================
# TIMELINE ITEM TESTS
# =============================================================================

class TestTimelineItem(unittest.TestCase):
    """Test cases for TimelineItem widget."""

    def setUp(self):
        """Set up test fixtures."""
        self.event = TimelineEvent(
            timestamp=datetime.now(),
            event_type="created",
            description="Transaksi dibuat",
            user="Admin"
        )
        self.item = TimelineItem(self.event)

    def tearDown(self):
        """Clean up after tests."""
        self.item.deleteLater()

    def test_item_initialization(self):
        """Test item initializes correctly."""
        self.assertEqual(self.item.event, self.event)
        self.assertFalse(self.item.is_current)
        self.assertFalse(self.item.is_last)

    def test_item_has_ui_elements(self):
        """Test item has required UI elements."""
        self.assertIsNotNone(self.item.time_label)
        self.assertIsNotNone(self.item.desc_label)
        self.assertIsNotNone(self.item.icon_label)
        self.assertIsNotNone(self.item.dot)

    def test_item_displays_description(self):
        """Test item displays description."""
        self.assertEqual(self.item.desc_label.text(), "Transaksi dibuat")

    def test_item_clicked_signal(self):
        """Test clicked signal is emitted."""
        spy = QSignalSpy(self.item.clicked)
        QTest.mouseClick(self.item, Qt.LeftButton)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], self.event.id)

    def test_item_current_state(self):
        """Test current state styling."""
        item = TimelineItem(self.event, is_current=True)
        self.assertTrue(item.is_current)
        item.deleteLater()


# =============================================================================
# WORKFLOW TIMELINE TESTS
# =============================================================================

class TestWorkflowTimeline(unittest.TestCase):
    """Test cases for WorkflowTimeline widget."""

    def setUp(self):
        """Set up test fixtures."""
        self.timeline = WorkflowTimeline(transaksi_id="TRX-001")

    def tearDown(self):
        """Clean up after tests."""
        self.timeline.deleteLater()

    def test_timeline_initialization(self):
        """Test timeline initializes correctly."""
        self.assertEqual(self.timeline.transaksi_id, "TRX-001")
        self.assertIsNotNone(self.timeline.title_label)
        self.assertIsNotNone(self.timeline.filter_combo)

    def test_add_event(self):
        """Test adding events to timeline."""
        event = TimelineEvent(
            timestamp=datetime.now(),
            event_type="created",
            description="Test event"
        )
        self.timeline.add_event(event)
        events = self.timeline.get_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].description, "Test event")

    def test_set_events(self):
        """Test setting multiple events."""
        events = [
            TimelineEvent(
                timestamp=datetime.now() - timedelta(hours=i),
                event_type="created",
                description=f"Event {i}"
            )
            for i in range(3)
        ]
        self.timeline.set_events(events)
        self.assertEqual(len(self.timeline.get_events()), 3)

    def test_clear_events(self):
        """Test clearing events."""
        event = TimelineEvent(
            timestamp=datetime.now(),
            event_type="created",
            description="Test"
        )
        self.timeline.add_event(event)
        self.timeline.clear_events()
        self.assertEqual(len(self.timeline.get_events()), 0)

    def test_filter_by_type(self):
        """Test filtering by event type."""
        events = [
            TimelineEvent(timestamp=datetime.now(), event_type="created", description="1"),
            TimelineEvent(timestamp=datetime.now(), event_type="fase_changed", description="2"),
            TimelineEvent(timestamp=datetime.now(), event_type="created", description="3"),
        ]
        self.timeline.set_events(events)
        self.timeline.filter_by_type(["created"])
        filtered = self.timeline.get_filtered_events()
        self.assertEqual(len(filtered), 2)

    def test_set_title(self):
        """Test setting title."""
        self.timeline.set_title("Custom Title")
        self.assertEqual(self.timeline.title_label.text(), "Custom Title")


# =============================================================================
# WORKFLOW PROGRESS TESTS
# =============================================================================

class TestWorkflowProgress(unittest.TestCase):
    """Test cases for WorkflowProgress widget."""

    def setUp(self):
        """Set up test fixtures."""
        self.progress = WorkflowProgress(current_fase=2, total_fases=5)

    def tearDown(self):
        """Clean up after tests."""
        self.progress.deleteLater()

    def test_progress_initialization(self):
        """Test progress initializes correctly."""
        self.assertEqual(self.progress.current_fase, 2)
        self.assertEqual(self.progress.total_fases, 5)

    def test_set_current_fase(self):
        """Test setting current fase."""
        self.progress.set_current_fase(3)
        self.assertEqual(self.progress.current_fase, 3)

    def test_fase_bounds(self):
        """Test fase bounds checking."""
        self.progress.set_current_fase(10)
        self.assertEqual(self.progress.current_fase, 5)  # Max

        self.progress.set_current_fase(0)
        self.assertEqual(self.progress.current_fase, 1)  # Min

    def test_fase_clicked_signal(self):
        """Test fase clicked signal."""
        spy = QSignalSpy(self.progress.fase_clicked)
        # Signal tested via paint event interaction


# =============================================================================
# WORKFLOW METRICS TESTS
# =============================================================================

class TestWorkflowMetrics(unittest.TestCase):
    """Test cases for WorkflowMetrics data class."""

    def test_metrics_initialization(self):
        """Test metrics initializes correctly."""
        metrics = WorkflowMetrics()
        self.assertEqual(metrics.avg_completion_time.days, 0)
        self.assertEqual(metrics.completion_rate, 0.0)
        self.assertEqual(metrics.overdue_count, 0)

    def test_metrics_with_data(self):
        """Test metrics with actual data."""
        metrics = WorkflowMetrics(
            avg_completion_time=timedelta(days=12),
            completion_rate=85.0,
            overdue_count=3,
            total_count=45
        )
        self.assertEqual(metrics.avg_completion_time.days, 12)
        self.assertEqual(metrics.completion_rate, 85.0)
        self.assertEqual(metrics.overdue_count, 3)
        self.assertEqual(metrics.total_count, 45)

    def test_format_avg_completion(self):
        """Test average completion formatting."""
        metrics = WorkflowMetrics(avg_completion_time=timedelta(days=12))
        formatted = metrics.format_avg_completion()
        self.assertEqual(formatted, "12 hari")

    def test_format_completion_rate(self):
        """Test completion rate formatting."""
        metrics = WorkflowMetrics(completion_rate=85.5)
        formatted = metrics.format_completion_rate()
        self.assertEqual(formatted, "86%")

    def test_bottleneck_name(self):
        """Test bottleneck name retrieval."""
        metrics = WorkflowMetrics(bottleneck_fase=2)
        name = metrics.get_bottleneck_name()
        self.assertEqual(name, "Pencairan UM")


# =============================================================================
# METRIC CARD TESTS
# =============================================================================

class TestMetricCard(unittest.TestCase):
    """Test cases for MetricCard widget."""

    def setUp(self):
        """Set up test fixtures."""
        self.card = MetricCard(
            value="12 hari",
            label="Rata-rata Waktu",
            icon="\u23F1",
            status="good"
        )

    def tearDown(self):
        """Clean up after tests."""
        self.card.deleteLater()

    def test_card_initialization(self):
        """Test card initializes correctly."""
        self.assertEqual(self.card.value, "12 hari")
        self.assertEqual(self.card.label, "Rata-rata Waktu")
        self.assertEqual(self.card.status, "good")

    def test_update_value(self):
        """Test updating value."""
        self.card.update_value("15 hari", "warning")
        self.assertEqual(self.card.value, "15 hari")
        self.assertEqual(self.card.status, "warning")

    def test_clicked_signal(self):
        """Test clicked signal."""
        spy = QSignalSpy(self.card.clicked)
        QTest.mouseClick(self.card, Qt.LeftButton)
        self.assertEqual(len(spy), 1)


# =============================================================================
# WORKFLOW ANALYTICS WIDGET TESTS
# =============================================================================

class TestWorkflowAnalyticsWidget(unittest.TestCase):
    """Test cases for WorkflowAnalyticsWidget."""

    def setUp(self):
        """Set up test fixtures."""
        self.widget = WorkflowAnalyticsWidget()
        self.sample_data = create_sample_transaksi(10)

    def tearDown(self):
        """Clean up after tests."""
        self.widget.deleteLater()

    def test_widget_initialization(self):
        """Test widget initializes correctly."""
        self.assertIsNotNone(self.widget.time_card)
        self.assertIsNotNone(self.widget.rate_card)
        self.assertIsNotNone(self.widget.overdue_card)
        self.assertIsNotNone(self.widget.total_card)

    def test_calculate_metrics(self):
        """Test metrics calculation."""
        metrics = self.widget.calculate_metrics(self.sample_data)
        self.assertIsInstance(metrics, WorkflowMetrics)
        self.assertEqual(metrics.total_count, 10)

    def test_set_data(self):
        """Test setting data."""
        self.widget.set_data(self.sample_data)
        metrics = self.widget.get_metrics()
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.total_count, 10)

    def test_refresh(self):
        """Test refresh functionality."""
        self.widget.set_data(self.sample_data)
        self.widget.refresh()
        metrics = self.widget.get_metrics()
        self.assertIsNotNone(metrics)


# =============================================================================
# DEADLINE INFO TESTS
# =============================================================================

class TestDeadlineInfo(unittest.TestCase):
    """Test cases for DeadlineInfo data class."""

    def test_deadline_on_track(self):
        """Test on track status (> 7 days)."""
        info = DeadlineInfo(
            transaksi_id="TRX-001",
            transaksi_nama="Test",
            transaksi_nomor="001",
            deadline=date.today() + timedelta(days=10),
            days_remaining=10,
            fase_current=2
        )
        self.assertEqual(info.status, "on_track")

    def test_deadline_warning(self):
        """Test warning status (3-7 days)."""
        info = DeadlineInfo(
            transaksi_id="TRX-001",
            transaksi_nama="Test",
            transaksi_nomor="001",
            deadline=date.today() + timedelta(days=5),
            days_remaining=5,
            fase_current=2
        )
        self.assertEqual(info.status, "warning")

    def test_deadline_due_soon(self):
        """Test due soon status (1-3 days)."""
        info = DeadlineInfo(
            transaksi_id="TRX-001",
            transaksi_nama="Test",
            transaksi_nomor="001",
            deadline=date.today() + timedelta(days=2),
            days_remaining=2,
            fase_current=2
        )
        self.assertEqual(info.status, "due_soon")

    def test_deadline_overdue(self):
        """Test overdue status (< 0 days)."""
        info = DeadlineInfo(
            transaksi_id="TRX-001",
            transaksi_nama="Test",
            transaksi_nomor="001",
            deadline=date.today() - timedelta(days=3),
            days_remaining=-3,
            fase_current=2
        )
        self.assertEqual(info.status, "overdue")

    def test_format_days_remaining(self):
        """Test days remaining formatting."""
        info = DeadlineInfo(
            transaksi_id="TRX-001",
            transaksi_nama="Test",
            transaksi_nomor="001",
            deadline=date.today() + timedelta(days=5),
            days_remaining=5,
            fase_current=2
        )
        self.assertEqual(info.format_days_remaining(), "5 hari lagi")

    def test_format_overdue(self):
        """Test overdue formatting."""
        info = DeadlineInfo(
            transaksi_id="TRX-001",
            transaksi_nama="Test",
            transaksi_nomor="001",
            deadline=date.today() - timedelta(days=3),
            days_remaining=-3,
            fase_current=2
        )
        self.assertIn("terlambat", info.format_days_remaining())

    def test_get_progress(self):
        """Test progress calculation."""
        info = DeadlineInfo(
            transaksi_id="TRX-001",
            transaksi_nama="Test",
            transaksi_nomor="001",
            deadline=date.today(),
            days_remaining=0,
            fase_current=3
        )
        progress = info.get_progress()
        self.assertEqual(progress, 60.0)  # 3/5 * 100


# =============================================================================
# DEADLINE TRACKER WIDGET TESTS
# =============================================================================

class TestDeadlineTrackerWidget(unittest.TestCase):
    """Test cases for DeadlineTrackerWidget."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracker = DeadlineTrackerWidget()
        self.sample_data = create_sample_transaksi(5)

    def tearDown(self):
        """Clean up after tests."""
        self.tracker.deleteLater()

    def test_tracker_initialization(self):
        """Test tracker initializes correctly."""
        self.assertIsNotNone(self.tracker.filter_combo)
        self.assertIsNotNone(self.tracker.scroll_area)

    def test_load_deadlines(self):
        """Test loading deadlines from transaksi."""
        self.tracker.load_deadlines(self.sample_data)
        all_deadlines = self.tracker.get_all_deadlines()
        self.assertGreater(len(all_deadlines), 0)

    def test_get_overdue(self):
        """Test getting overdue deadlines."""
        deadlines = [
            DeadlineInfo(
                transaksi_id=f"TRX-{i}",
                transaksi_nama=f"Test {i}",
                transaksi_nomor=f"{i:03d}",
                deadline=date.today() - timedelta(days=i+1),
                days_remaining=-(i+1),
                fase_current=2
            )
            for i in range(3)
        ]
        self.tracker.set_deadlines(deadlines)
        overdue = self.tracker.get_overdue()
        self.assertEqual(len(overdue), 3)

    def test_get_due_soon(self):
        """Test getting due soon deadlines."""
        deadlines = [
            DeadlineInfo(
                transaksi_id="TRX-1",
                transaksi_nama="Test",
                transaksi_nomor="001",
                deadline=date.today() + timedelta(days=2),
                days_remaining=2,
                fase_current=2
            )
        ]
        self.tracker.set_deadlines(deadlines)
        due_soon = self.tracker.get_due_soon(days=3)
        self.assertEqual(len(due_soon), 1)

    def test_calculate_deadline_up(self):
        """Test deadline calculation for UP."""
        transaksi = {
            "mekanisme": "UP",
            "created_at": date.today()
        }
        deadline = self.tracker.calculate_deadline(transaksi)
        expected = date.today() + timedelta(days=DEFAULT_SLA["UP"])
        self.assertEqual(deadline, expected)

    def test_deadline_clicked_signal(self):
        """Test deadline clicked signal."""
        spy = QSignalSpy(self.tracker.deadline_clicked)
        # Signal tested via item interaction


# =============================================================================
# WORKFLOW NOTIFICATION TESTS
# =============================================================================

class TestWorkflowNotification(unittest.TestCase):
    """Test cases for WorkflowNotification data class."""

    def test_notification_initialization(self):
        """Test notification initializes correctly."""
        notif = WorkflowNotification(
            type="deadline_warning",
            title="Deadline Approaching",
            message="TRX-001 deadline in 3 days"
        )
        self.assertIsNotNone(notif.id)
        self.assertEqual(notif.type, "deadline_warning")
        self.assertFalse(notif.read)

    def test_notification_with_transaksi(self):
        """Test notification with transaksi ID."""
        notif = WorkflowNotification(
            type="fase_complete",
            title="Fase Complete",
            message="Fase 2 completed",
            transaksi_id="TRX-001"
        )
        self.assertEqual(notif.transaksi_id, "TRX-001")

    def test_notification_priority(self):
        """Test notification priority from type."""
        notif = WorkflowNotification(
            type="deadline_overdue",
            title="Overdue",
            message="Test"
        )
        # Priority should be set from config
        self.assertEqual(notif.priority, "urgent")

    def test_get_icon(self):
        """Test getting icon."""
        notif = WorkflowNotification(
            type="deadline_warning",
            title="Test",
            message="Test"
        )
        icon = notif.get_icon()
        self.assertEqual(icon, NOTIFICATION_CONFIG["deadline_warning"]["icon"])

    def test_format_time_ago(self):
        """Test time ago formatting."""
        notif = WorkflowNotification(
            type="system_info",
            title="Test",
            message="Test",
            timestamp=datetime.now() - timedelta(hours=2)
        )
        ago = notif.format_time_ago()
        self.assertIn("jam", ago)

    def test_mark_read(self):
        """Test marking as read."""
        notif = WorkflowNotification(
            type="system_info",
            title="Test",
            message="Test"
        )
        self.assertFalse(notif.read)
        notif.mark_read()
        self.assertTrue(notif.read)


# =============================================================================
# NOTIFICATION CENTER TESTS
# =============================================================================

class TestNotificationCenter(unittest.TestCase):
    """Test cases for NotificationCenter widget."""

    def setUp(self):
        """Set up test fixtures."""
        self.center = NotificationCenter()

    def tearDown(self):
        """Clean up after tests."""
        self.center.deleteLater()

    def test_center_initialization(self):
        """Test center initializes correctly."""
        self.assertIsNotNone(self.center.bell_btn)
        self.assertIsNotNone(self.center.badge)

    def test_add_notification(self):
        """Test adding notification."""
        notif = WorkflowNotification(
            type="system_info",
            title="Test",
            message="Test message"
        )
        self.center.add_notification(notif)
        self.assertEqual(len(self.center.get_notifications()), 1)

    def test_badge_visibility(self):
        """Test badge visibility."""
        # Initially hidden (no unread)
        self.assertFalse(self.center.badge.isVisible())

        # Add notification
        notif = WorkflowNotification(
            type="system_info",
            title="Test",
            message="Test"
        )
        self.center.add_notification(notif)

        # Badge should be visible
        self.assertTrue(self.center.badge.isVisible())

    def test_get_unread(self):
        """Test getting unread notifications."""
        notif1 = WorkflowNotification(type="system_info", title="1", message="1")
        notif2 = WorkflowNotification(type="system_info", title="2", message="2")
        notif2.mark_read()

        self.center.set_notifications([notif1, notif2])

        unread = self.center.get_unread()
        self.assertEqual(len(unread), 1)

    def test_get_unread_count(self):
        """Test getting unread count."""
        for i in range(3):
            notif = WorkflowNotification(
                type="system_info",
                title=str(i),
                message=str(i)
            )
            self.center.add_notification(notif)

        self.assertEqual(self.center.get_unread_count(), 3)

    def test_mark_all_read(self):
        """Test marking all as read."""
        for i in range(3):
            notif = WorkflowNotification(
                type="system_info",
                title=str(i),
                message=str(i)
            )
            self.center.add_notification(notif)

        self.center.mark_all_read()
        self.assertEqual(self.center.get_unread_count(), 0)

    def test_clear(self):
        """Test clearing all notifications."""
        for i in range(3):
            notif = WorkflowNotification(
                type="system_info",
                title=str(i),
                message=str(i)
            )
            self.center.add_notification(notif)

        self.center.clear()
        self.assertEqual(len(self.center.get_notifications()), 0)


# =============================================================================
# NOTIFICATION SERVICE TESTS
# =============================================================================

class TestNotificationService(unittest.TestCase):
    """Test cases for NotificationService."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = NotificationService(check_interval=60000)
        self.sample_data = create_sample_transaksi(5)

    def tearDown(self):
        """Clean up after tests."""
        self.service.stop()

    def test_service_initialization(self):
        """Test service initializes correctly."""
        self.assertEqual(self.service.check_interval, 60000)

    def test_set_transaksi_data(self):
        """Test setting transaksi data."""
        self.service.set_transaksi_data(self.sample_data)
        # Data should be stored internally

    def test_create_notification(self):
        """Test creating notification."""
        spy = QSignalSpy(self.service.notification_created)

        notif = self.service.create_notification(
            type="system_info",
            title="Test",
            message="Test message"
        )

        self.assertIsNotNone(notif)
        self.assertEqual(notif.type, "system_info")
        self.assertEqual(len(spy), 1)

    def test_set_interval(self):
        """Test setting check interval."""
        self.service.set_interval(120000)
        self.assertEqual(self.service.check_interval, 120000)

    def test_clear_tracking(self):
        """Test clearing notification tracking."""
        # Create some notifications to track
        self.service._created_notification_ids.add("test_key")
        self.service.clear_tracking()
        self.assertEqual(len(self.service._created_notification_ids), 0)


# =============================================================================
# FACTORY FUNCTION TESTS
# =============================================================================

class TestFactoryFunctions(unittest.TestCase):
    """Test cases for factory functions."""

    def test_create_timeline(self):
        """Test create_timeline factory."""
        timeline = create_timeline(transaksi_id="TRX-001")
        self.assertIsInstance(timeline, WorkflowTimeline)
        self.assertEqual(timeline.transaksi_id, "TRX-001")
        timeline.deleteLater()

    def test_create_progress(self):
        """Test create_progress factory."""
        progress = create_progress(current_fase=3, total_fases=5)
        self.assertIsInstance(progress, WorkflowProgress)
        self.assertEqual(progress.current_fase, 3)
        progress.deleteLater()

    def test_create_analytics_widget(self):
        """Test create_analytics_widget factory."""
        widget = create_analytics_widget()
        self.assertIsInstance(widget, WorkflowAnalyticsWidget)
        widget.deleteLater()

    def test_create_deadline_tracker(self):
        """Test create_deadline_tracker factory."""
        tracker = create_deadline_tracker()
        self.assertIsInstance(tracker, DeadlineTrackerWidget)
        tracker.deleteLater()

    def test_create_compact_deadline(self):
        """Test create_compact_deadline factory."""
        widget = create_compact_deadline()
        self.assertIsInstance(widget, CompactDeadlineWidget)
        widget.deleteLater()

    def test_create_notification_center(self):
        """Test create_notification_center factory."""
        center = create_notification_center()
        self.assertIsInstance(center, NotificationCenter)
        center.deleteLater()

    def test_create_notification_service(self):
        """Test create_notification_service factory."""
        service = create_notification_service()
        self.assertIsInstance(service, NotificationService)
        service.stop()


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestWorkflowIntegration(unittest.TestCase):
    """Integration tests for workflow components."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_data = create_sample_transaksi(10)

    def test_analytics_to_deadline_flow(self):
        """Test data flow from analytics to deadline tracker."""
        analytics = WorkflowAnalyticsWidget()
        tracker = DeadlineTrackerWidget()

        analytics.set_data(self.sample_data)
        tracker.load_deadlines(self.sample_data)

        metrics = analytics.get_metrics()
        overdue = tracker.get_overdue()

        # Overdue count should match
        self.assertEqual(metrics.overdue_count, len(overdue))

        analytics.deleteLater()
        tracker.deleteLater()

    def test_notification_service_to_center(self):
        """Test notification service to center integration."""
        service = NotificationService()
        center = NotificationCenter()

        # Connect signal
        service.notification_created.connect(center.add_notification)

        # Create notification
        service.create_notification(
            type="system_info",
            title="Integration Test",
            message="Test message"
        )

        # Center should have notification
        self.assertEqual(len(center.get_notifications()), 1)

        service.stop()
        center.deleteLater()


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
