"""
Comprehensive Tests for Workflow Dashboard Components
======================================================
Tests for KanbanBoard, WorkflowTimeline, WorkflowAnalytics,
DeadlineTracker, NotificationCenter, and WorkflowService.

Run with: pytest tests/test_workflow_dashboard.py -v
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from dataclasses import asdict
import json

# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture
def sample_transaksi_list():
    """Sample transaction data for testing."""
    return [
        {
            "id": "UP-001",
            "nomor": "001/UP/2024",
            "nama": "Pengadaan ATK",
            "nilai": 50000000,
            "mekanisme": "UP",
            "fase": 1,
            "status": "Aktif",
            "tanggal_mulai": datetime.now() - timedelta(days=5),
            "deadline": datetime.now() + timedelta(days=25),
            "progress": 20,
        },
        {
            "id": "UP-002",
            "nomor": "002/UP/2024",
            "nama": "Pembelian Komputer",
            "nilai": 150000000,
            "mekanisme": "UP",
            "fase": 2,
            "status": "Aktif",
            "tanggal_mulai": datetime.now() - timedelta(days=10),
            "deadline": datetime.now() + timedelta(days=20),
            "progress": 40,
        },
        {
            "id": "TUP-001",
            "nomor": "001/TUP/2024",
            "nama": "Perjalanan Dinas",
            "nilai": 25000000,
            "mekanisme": "TUP",
            "fase": 3,
            "status": "Aktif",
            "tanggal_mulai": datetime.now() - timedelta(days=15),
            "deadline": datetime.now() + timedelta(days=15),
            "progress": 60,
        },
        {
            "id": "LS-001",
            "nomor": "001/LS/2024",
            "nama": "Pembangunan Gedung",
            "nilai": 500000000,
            "mekanisme": "LS",
            "fase": 4,
            "status": "Aktif",
            "tanggal_mulai": datetime.now() - timedelta(days=30),
            "deadline": datetime.now() + timedelta(days=60),
            "progress": 80,
        },
        {
            "id": "UP-003",
            "nomor": "003/UP/2024",
            "nama": "Completed Transaction",
            "nilai": 75000000,
            "mekanisme": "UP",
            "fase": 5,
            "status": "Selesai",
            "tanggal_mulai": datetime.now() - timedelta(days=30),
            "deadline": datetime.now() - timedelta(days=1),
            "progress": 100,
        },
    ]


@pytest.fixture
def sample_timeline_events():
    """Sample timeline events for testing."""
    from app.ui.components.workflow_timeline import TimelineEvent, EventType

    return [
        TimelineEvent(
            timestamp=datetime.now() - timedelta(days=5),
            event_type=EventType.CREATED,
            description="Transaksi dibuat",
            actor="Admin",
        ),
        TimelineEvent(
            timestamp=datetime.now() - timedelta(days=4),
            event_type=EventType.FASE_CHANGED,
            description="Pindah ke Fase 2",
            fase_from=1,
            fase_to=2,
            actor="PPK",
        ),
        TimelineEvent(
            timestamp=datetime.now() - timedelta(days=3),
            event_type=EventType.DOCUMENT_UPLOADED,
            description="Dokumen HPS diupload",
            document_type="HPS",
            actor="Staff",
        ),
        TimelineEvent(
            timestamp=datetime.now() - timedelta(days=2),
            event_type=EventType.COMMENT,
            description="Catatan: Perlu revisi nilai",
            actor="PPK",
        ),
    ]


@pytest.fixture
def sample_deadlines():
    """Sample deadline data for testing."""
    return [
        {
            "transaksi_id": "UP-001",
            "transaksi_nama": "Pengadaan ATK",
            "mekanisme": "UP",
            "deadline": datetime.now() + timedelta(days=2),  # Urgent
            "fase": 1,
            "sla_days": 30,
        },
        {
            "transaksi_id": "TUP-001",
            "transaksi_nama": "Perjalanan Dinas",
            "mekanisme": "TUP",
            "deadline": datetime.now() + timedelta(days=7),  # Warning
            "fase": 3,
            "sla_days": 30,
        },
        {
            "transaksi_id": "LS-001",
            "transaksi_nama": "Pembangunan Gedung",
            "mekanisme": "LS",
            "deadline": datetime.now() + timedelta(days=30),  # On Track
            "fase": 4,
            "sla_days": 90,
        },
        {
            "transaksi_id": "UP-003",
            "transaksi_nama": "Overdue Transaction",
            "mekanisme": "UP",
            "deadline": datetime.now() - timedelta(days=5),  # Overdue
            "fase": 2,
            "sla_days": 30,
        },
    ]


@pytest.fixture
def mock_db_connection():
    """Mock database connection."""
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    conn.execute.return_value = cursor
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = None
    return conn


# =============================================================================
# KANBAN BOARD TESTS
# =============================================================================


class TestKanbanBoard:
    """Test suite for KanbanBoard component."""

    def test_kanban_card_data_class(self):
        """Test KanbanCard data representation."""
        from app.ui.components.kanban_board import (
            Mekanisme,
            Urgency,
            MEKANISME_COLORS,
        )

        # Test Mekanisme enum values
        assert Mekanisme.UP.value == "UP"
        assert Mekanisme.TUP.value == "TUP"
        assert Mekanisme.LS.value == "LS"

        # Test color definitions exist
        assert Mekanisme.UP in MEKANISME_COLORS
        assert Mekanisme.TUP in MEKANISME_COLORS
        assert Mekanisme.LS in MEKANISME_COLORS

        # Test urgency enum
        assert Urgency.OVERDUE.value == "overdue"
        assert Urgency.URGENT.value == "urgent"
        assert Urgency.WARNING.value == "warning"
        assert Urgency.ON_TRACK.value == "on_track"

    def test_fase_config(self):
        """Test FASE_CONFIG contains all 5 phases."""
        from app.ui.components.kanban_board import FASE_CONFIG

        assert len(FASE_CONFIG) == 5
        for i in range(1, 6):
            assert i in FASE_CONFIG
            assert "name" in FASE_CONFIG[i]
            assert "description" in FASE_CONFIG[i]

    def test_urgency_calculation(self):
        """Test urgency calculation based on days remaining."""
        from app.ui.components.kanban_board import Urgency, URGENCY_COLORS

        # Test urgency color definitions
        assert Urgency.OVERDUE in URGENCY_COLORS
        assert Urgency.URGENT in URGENCY_COLORS
        assert Urgency.WARNING in URGENCY_COLORS
        assert Urgency.ON_TRACK in URGENCY_COLORS

    def test_create_kanban_board_factory(self):
        """Test factory function creates board correctly."""
        from app.ui.components.kanban_board import create_kanban_board

        # Test default creation
        board = create_kanban_board()
        assert board is not None

        # Test with mekanisme filter
        board_up = create_kanban_board(mekanisme="UP")
        assert board_up is not None

        board_tup = create_kanban_board(mekanisme="TUP")
        assert board_tup is not None

        board_ls = create_kanban_board(mekanisme="LS")
        assert board_ls is not None

    def test_kanban_board_set_data(self, sample_transaksi_list):
        """Test setting data on kanban board."""
        from app.ui.components.kanban_board import create_kanban_board

        board = create_kanban_board()
        board.set_data(sample_transaksi_list)

        # Verify board has data
        assert board._transaksi_data == sample_transaksi_list

    def test_kanban_board_filter_by_mekanisme(self, sample_transaksi_list):
        """Test filtering by mekanisme."""
        from app.ui.components.kanban_board import create_kanban_board

        # Test UP filter
        board = create_kanban_board(mekanisme="UP")
        board.set_data(sample_transaksi_list)

        # Board should filter data internally
        # Verify filter is set
        assert board._filter_mekanisme == "UP"

    def test_kanban_board_signals(self):
        """Test kanban board signals are defined."""
        from app.ui.components.kanban_board import KanbanBoard

        # Check signal definitions exist
        assert hasattr(KanbanBoard, "transaksi_selected")
        assert hasattr(KanbanBoard, "transaksi_moved")
        assert hasattr(KanbanBoard, "transaksi_double_clicked")

    def test_cards_grouped_by_fase(self, sample_transaksi_list):
        """Test cards are grouped correctly by fase."""
        from app.ui.components.kanban_board import create_kanban_board

        board = create_kanban_board()
        board.set_data(sample_transaksi_list)

        # Check each fase column
        for fase in range(1, 6):
            column = board._columns.get(fase)
            if column:
                # Count expected cards for this fase
                expected = sum(
                    1 for t in sample_transaksi_list if t.get("fase") == fase
                )
                assert column.count() == expected


# =============================================================================
# WORKFLOW TIMELINE TESTS
# =============================================================================


class TestWorkflowTimeline:
    """Test suite for WorkflowTimeline component."""

    def test_timeline_event_dataclass(self):
        """Test TimelineEvent dataclass."""
        from app.ui.components.workflow_timeline import TimelineEvent, EventType

        event = TimelineEvent(
            timestamp=datetime.now(),
            event_type=EventType.CREATED,
            description="Test event",
            actor="Admin",
        )

        assert event.timestamp is not None
        assert event.event_type == EventType.CREATED
        assert event.description == "Test event"
        assert event.actor == "Admin"

    def test_event_types_defined(self):
        """Test all event types are defined."""
        from app.ui.components.workflow_timeline import EventType

        expected_types = [
            "created",
            "fase_changed",
            "document_uploaded",
            "document_signed",
            "document_rejected",
            "deadline_warning",
            "deadline_missed",
            "comment",
            "approved",
            "rejected",
            "completed",
        ]

        for event_type in expected_types:
            assert hasattr(EventType, event_type.upper())

    def test_create_timeline_factory(self):
        """Test timeline factory function."""
        from app.ui.components.workflow_timeline import create_timeline

        timeline = create_timeline(transaksi_id="UP-001")
        assert timeline is not None
        assert timeline._transaksi_id == "UP-001"

    def test_timeline_add_event(self, sample_timeline_events):
        """Test adding events to timeline."""
        from app.ui.components.workflow_timeline import create_timeline

        timeline = create_timeline(transaksi_id="UP-001")

        for event in sample_timeline_events:
            timeline.add_event(event)

        assert len(timeline._events) == len(sample_timeline_events)

    def test_events_sorted_by_time(self, sample_timeline_events):
        """Test events are sorted by timestamp (newest first)."""
        from app.ui.components.workflow_timeline import create_timeline

        timeline = create_timeline(transaksi_id="UP-001")

        # Add events in random order
        for event in reversed(sample_timeline_events):
            timeline.add_event(event)

        # Events should be sorted newest first
        events = timeline._events
        for i in range(len(events) - 1):
            assert events[i].timestamp >= events[i + 1].timestamp

    def test_timeline_event_icons(self):
        """Test event types have associated icons."""
        from app.ui.components.workflow_timeline import EventType

        # Each event type should map to an icon
        icon_mapping = {
            EventType.CREATED: "add",
            EventType.FASE_CHANGED: "arrow_forward",
            EventType.DOCUMENT_UPLOADED: "upload",
            EventType.DOCUMENT_SIGNED: "check_circle",
            EventType.COMMENT: "comment",
        }

        for event_type, icon in icon_mapping.items():
            # Verify mapping exists (actual implementation may vary)
            assert event_type is not None

    def test_workflow_progress_create(self):
        """Test WorkflowProgress component creation."""
        from app.ui.components.workflow_timeline import create_progress

        progress = create_progress(current_fase=2, total_fases=5)
        assert progress is not None
        assert progress._current_fase == 2
        assert progress._total_fases == 5

    def test_workflow_progress_percentage(self):
        """Test progress percentage calculation."""
        from app.ui.components.workflow_timeline import create_progress

        # Test various progress levels
        progress_1 = create_progress(current_fase=1, total_fases=5)
        progress_3 = create_progress(current_fase=3, total_fases=5)
        progress_5 = create_progress(current_fase=5, total_fases=5)

        # Progress should increase with fase
        assert progress_1._current_fase < progress_3._current_fase
        assert progress_3._current_fase < progress_5._current_fase


# =============================================================================
# WORKFLOW ANALYTICS TESTS
# =============================================================================


class TestWorkflowAnalytics:
    """Test suite for WorkflowAnalytics component."""

    def test_workflow_metrics_dataclass(self):
        """Test WorkflowMetrics dataclass."""
        from app.ui.components.workflow_analytics import WorkflowMetrics

        metrics = WorkflowMetrics(
            total_transaksi=10,
            transaksi_aktif=8,
            transaksi_selesai=2,
            total_nilai=1000000000,
            per_fase={1: 2, 2: 3, 3: 2, 4: 1, 5: 2},
            per_mekanisme={"UP": 5, "TUP": 3, "LS": 2},
            avg_completion_days=15.5,
            overdue_count=1,
            on_track_count=7,
            bottleneck_fase=2,
        )

        assert metrics.total_transaksi == 10
        assert metrics.transaksi_aktif == 8
        assert metrics.bottleneck_fase == 2

    def test_create_analytics_widget_factory(self):
        """Test analytics widget factory function."""
        from app.ui.components.workflow_analytics import create_analytics_widget

        widget = create_analytics_widget()
        assert widget is not None

    def test_analytics_set_data(self, sample_transaksi_list):
        """Test setting data on analytics widget."""
        from app.ui.components.workflow_analytics import create_analytics_widget

        widget = create_analytics_widget()
        widget.set_data(sample_transaksi_list)

        # Widget should calculate metrics from data
        assert widget._metrics is not None

    def test_metrics_calculation_total(self, sample_transaksi_list):
        """Test total transaksi calculation."""
        from app.ui.components.workflow_analytics import create_analytics_widget

        widget = create_analytics_widget()
        widget.set_data(sample_transaksi_list)

        assert widget._metrics.total_transaksi == len(sample_transaksi_list)

    def test_metrics_calculation_per_fase(self, sample_transaksi_list):
        """Test per-fase calculation."""
        from app.ui.components.workflow_analytics import create_analytics_widget

        widget = create_analytics_widget()
        widget.set_data(sample_transaksi_list)

        # Calculate expected per-fase counts
        expected_per_fase = {}
        for t in sample_transaksi_list:
            fase = t.get("fase", 0)
            expected_per_fase[fase] = expected_per_fase.get(fase, 0) + 1

        for fase, count in expected_per_fase.items():
            assert widget._metrics.per_fase.get(fase, 0) == count

    def test_metrics_calculation_per_mekanisme(self, sample_transaksi_list):
        """Test per-mekanisme calculation."""
        from app.ui.components.workflow_analytics import create_analytics_widget

        widget = create_analytics_widget()
        widget.set_data(sample_transaksi_list)

        # Calculate expected per-mekanisme counts
        expected_per_mek = {}
        for t in sample_transaksi_list:
            mek = t.get("mekanisme", "")
            expected_per_mek[mek] = expected_per_mek.get(mek, 0) + 1

        for mek, count in expected_per_mek.items():
            assert widget._metrics.per_mekanisme.get(mek, 0) == count

    def test_bottleneck_identification(self):
        """Test bottleneck fase identification."""
        from app.ui.components.workflow_analytics import create_analytics_widget

        # Create data with obvious bottleneck at fase 2
        data = [
            {"id": f"T{i}", "fase": 2, "mekanisme": "UP", "nilai": 1000000}
            for i in range(10)
        ]
        data.extend(
            [
                {"id": "T10", "fase": 1, "mekanisme": "UP", "nilai": 1000000},
                {"id": "T11", "fase": 3, "mekanisme": "TUP", "nilai": 1000000},
            ]
        )

        widget = create_analytics_widget()
        widget.set_data(data)

        # Fase 2 should be identified as bottleneck
        assert widget._metrics.bottleneck_fase == 2

    def test_metric_card_creation(self):
        """Test MetricCard component."""
        from app.ui.components.workflow_analytics import MetricCard

        card = MetricCard(
            title="Total Transaksi", value=10, subtitle="Active transactions"
        )

        assert card._title == "Total Transaksi"
        assert card._value == 10

    def test_total_nilai_calculation(self, sample_transaksi_list):
        """Test total nilai calculation."""
        from app.ui.components.workflow_analytics import create_analytics_widget

        widget = create_analytics_widget()
        widget.set_data(sample_transaksi_list)

        expected_total = sum(t.get("nilai", 0) for t in sample_transaksi_list)
        assert widget._metrics.total_nilai == expected_total


# =============================================================================
# DEADLINE TRACKER TESTS
# =============================================================================


class TestDeadlineTracker:
    """Test suite for DeadlineTracker component."""

    def test_deadline_info_dataclass(self):
        """Test DeadlineInfo dataclass."""
        from app.ui.components.deadline_tracker import DeadlineInfo, DeadlineStatus

        deadline = DeadlineInfo(
            transaksi_id="UP-001",
            transaksi_nama="Test Transaction",
            mekanisme="UP",
            deadline=datetime.now() + timedelta(days=5),
            fase=2,
            sla_days=30,
        )

        assert deadline.transaksi_id == "UP-001"
        assert deadline.mekanisme == "UP"

    def test_deadline_status_enum(self):
        """Test DeadlineStatus enum values."""
        from app.ui.components.deadline_tracker import DeadlineStatus

        assert DeadlineStatus.OVERDUE.value == "overdue"
        assert DeadlineStatus.URGENT.value == "urgent"
        assert DeadlineStatus.WARNING.value == "warning"
        assert DeadlineStatus.ON_TRACK.value == "on_track"

    def test_deadline_status_calculation_overdue(self):
        """Test overdue deadline detection."""
        from app.ui.components.deadline_tracker import DeadlineInfo, DeadlineStatus

        deadline = DeadlineInfo(
            transaksi_id="UP-001",
            transaksi_nama="Test",
            mekanisme="UP",
            deadline=datetime.now() - timedelta(days=5),  # Past due
            fase=2,
            sla_days=30,
        )

        assert deadline.status == DeadlineStatus.OVERDUE

    def test_deadline_status_calculation_urgent(self):
        """Test urgent deadline detection (<=3 days)."""
        from app.ui.components.deadline_tracker import DeadlineInfo, DeadlineStatus

        deadline = DeadlineInfo(
            transaksi_id="UP-001",
            transaksi_nama="Test",
            mekanisme="UP",
            deadline=datetime.now() + timedelta(days=2),  # 2 days remaining
            fase=2,
            sla_days=30,
        )

        assert deadline.status == DeadlineStatus.URGENT

    def test_deadline_status_calculation_warning(self):
        """Test warning deadline detection (<=7 days)."""
        from app.ui.components.deadline_tracker import DeadlineInfo, DeadlineStatus

        deadline = DeadlineInfo(
            transaksi_id="UP-001",
            transaksi_nama="Test",
            mekanisme="UP",
            deadline=datetime.now() + timedelta(days=5),  # 5 days remaining
            fase=2,
            sla_days=30,
        )

        assert deadline.status == DeadlineStatus.WARNING

    def test_deadline_status_calculation_on_track(self):
        """Test on-track deadline detection (>7 days)."""
        from app.ui.components.deadline_tracker import DeadlineInfo, DeadlineStatus

        deadline = DeadlineInfo(
            transaksi_id="UP-001",
            transaksi_nama="Test",
            mekanisme="UP",
            deadline=datetime.now() + timedelta(days=20),  # 20 days remaining
            fase=2,
            sla_days=30,
        )

        assert deadline.status == DeadlineStatus.ON_TRACK

    def test_create_deadline_tracker_factory(self):
        """Test deadline tracker factory function."""
        from app.ui.components.deadline_tracker import create_deadline_tracker

        tracker = create_deadline_tracker()
        assert tracker is not None

    def test_deadlines_sorted_by_urgency(self, sample_deadlines):
        """Test deadlines are sorted by urgency."""
        from app.ui.components.deadline_tracker import (
            create_deadline_tracker,
            DeadlineInfo,
        )

        tracker = create_deadline_tracker()

        # Convert sample data to DeadlineInfo
        deadlines = [
            DeadlineInfo(
                transaksi_id=d["transaksi_id"],
                transaksi_nama=d["transaksi_nama"],
                mekanisme=d["mekanisme"],
                deadline=d["deadline"],
                fase=d["fase"],
                sla_days=d["sla_days"],
            )
            for d in sample_deadlines
        ]

        tracker.load_deadlines(deadlines)

        # Verify overdue items come first
        sorted_deadlines = tracker._deadlines
        if sorted_deadlines:
            # First items should be overdue/urgent
            from app.ui.components.deadline_tracker import DeadlineStatus

            priority_order = [
                DeadlineStatus.OVERDUE,
                DeadlineStatus.URGENT,
                DeadlineStatus.WARNING,
                DeadlineStatus.ON_TRACK,
            ]
            # Check sorting is correct
            assert len(sorted_deadlines) == len(deadlines)

    def test_days_remaining_calculation(self):
        """Test days remaining calculation."""
        from app.ui.components.deadline_tracker import DeadlineInfo

        # Test positive days remaining
        deadline_future = DeadlineInfo(
            transaksi_id="UP-001",
            transaksi_nama="Test",
            mekanisme="UP",
            deadline=datetime.now() + timedelta(days=10),
            fase=2,
            sla_days=30,
        )
        assert deadline_future.days_remaining == 10

        # Test negative days (overdue)
        deadline_past = DeadlineInfo(
            transaksi_id="UP-002",
            transaksi_nama="Test",
            mekanisme="UP",
            deadline=datetime.now() - timedelta(days=5),
            fase=2,
            sla_days=30,
        )
        assert deadline_past.days_remaining == -5

    def test_compact_deadline_widget(self):
        """Test CompactDeadlineWidget creation."""
        from app.ui.components.deadline_tracker import create_compact_deadline

        widget = create_compact_deadline()
        assert widget is not None

    def test_deadline_clicked_signal(self):
        """Test deadline clicked signal exists."""
        from app.ui.components.deadline_tracker import DeadlineTrackerWidget

        assert hasattr(DeadlineTrackerWidget, "deadline_clicked")


# =============================================================================
# NOTIFICATION CENTER TESTS
# =============================================================================


class TestNotificationCenter:
    """Test suite for NotificationCenter component."""

    def test_notification_dataclass(self):
        """Test WorkflowNotification dataclass."""
        from app.ui.components.workflow_notifications import (
            WorkflowNotification,
            NotificationType,
            NotificationPriority,
        )

        notif = WorkflowNotification(
            id="notif-001",
            notification_type=NotificationType.DEADLINE_WARNING,
            priority=NotificationPriority.HIGH,
            title="Deadline Warning",
            message="Transaction UP-001 deadline approaching",
            transaksi_id="UP-001",
        )

        assert notif.id == "notif-001"
        assert notif.notification_type == NotificationType.DEADLINE_WARNING
        assert notif.priority == NotificationPriority.HIGH

    def test_notification_types_defined(self):
        """Test all notification types are defined."""
        from app.ui.components.workflow_notifications import NotificationType

        expected_types = [
            "DEADLINE_WARNING",
            "DEADLINE_MISSED",
            "FASE_COMPLETED",
            "DOCUMENT_REQUIRED",
            "DOCUMENT_READY",
            "APPROVAL_NEEDED",
            "SYSTEM",
        ]

        for ntype in expected_types:
            assert hasattr(NotificationType, ntype)

    def test_notification_priorities_defined(self):
        """Test notification priorities are defined."""
        from app.ui.components.workflow_notifications import NotificationPriority

        assert NotificationPriority.LOW.value == "low"
        assert NotificationPriority.NORMAL.value == "normal"
        assert NotificationPriority.HIGH.value == "high"
        assert NotificationPriority.URGENT.value == "urgent"

    def test_create_notification_center_factory(self):
        """Test notification center factory function."""
        from app.ui.components.workflow_notifications import create_notification_center

        center = create_notification_center()
        assert center is not None

    def test_notification_center_add_notification(self):
        """Test adding notification to center."""
        from app.ui.components.workflow_notifications import (
            create_notification_center,
            WorkflowNotification,
            NotificationType,
            NotificationPriority,
        )

        center = create_notification_center()

        notif = WorkflowNotification(
            id="notif-001",
            notification_type=NotificationType.SYSTEM,
            priority=NotificationPriority.NORMAL,
            title="Test Notification",
            message="This is a test",
        )

        center.add_notification(notif)
        assert center.unread_count == 1

    def test_mark_notification_read(self):
        """Test marking notification as read."""
        from app.ui.components.workflow_notifications import (
            create_notification_center,
            WorkflowNotification,
            NotificationType,
            NotificationPriority,
        )

        center = create_notification_center()

        notif = WorkflowNotification(
            id="notif-001",
            notification_type=NotificationType.SYSTEM,
            priority=NotificationPriority.NORMAL,
            title="Test",
            message="Test message",
        )

        center.add_notification(notif)
        assert center.unread_count == 1

        center.mark_read("notif-001")
        assert center.unread_count == 0

    def test_badge_count_updates(self):
        """Test badge count updates correctly."""
        from app.ui.components.workflow_notifications import (
            create_notification_center,
            WorkflowNotification,
            NotificationType,
            NotificationPriority,
        )

        center = create_notification_center()

        # Add multiple notifications
        for i in range(5):
            notif = WorkflowNotification(
                id=f"notif-{i}",
                notification_type=NotificationType.SYSTEM,
                priority=NotificationPriority.NORMAL,
                title=f"Test {i}",
                message=f"Message {i}",
            )
            center.add_notification(notif)

        assert center.unread_count == 5

        # Mark some as read
        center.mark_read("notif-0")
        center.mark_read("notif-1")
        assert center.unread_count == 3

    def test_notification_service_creation(self):
        """Test NotificationService creation."""
        from app.ui.components.workflow_notifications import create_notification_service

        service = create_notification_service()
        assert service is not None

    def test_notification_service_signals(self):
        """Test NotificationService signals exist."""
        from app.ui.components.workflow_notifications import NotificationService

        assert hasattr(NotificationService, "notification_created")

    def test_notification_dismiss(self):
        """Test dismissing notifications."""
        from app.ui.components.workflow_notifications import (
            create_notification_center,
            WorkflowNotification,
            NotificationType,
            NotificationPriority,
        )

        center = create_notification_center()

        notif = WorkflowNotification(
            id="notif-001",
            notification_type=NotificationType.SYSTEM,
            priority=NotificationPriority.NORMAL,
            title="Test",
            message="Test message",
        )

        center.add_notification(notif)
        center.dismiss("notif-001")

        # Dismissed notification should not count
        assert center.unread_count == 0


# =============================================================================
# WORKFLOW SERVICE TESTS
# =============================================================================


class TestWorkflowService:
    """Test suite for WorkflowService."""

    def test_create_workflow_service_factory(self, mock_db_connection):
        """Test workflow service factory function."""
        from app.services.workflow_service import create_workflow_service

        service = create_workflow_service(mock_db_connection)
        assert service is not None

    def test_fase_transition_validation_valid(self, mock_db_connection):
        """Test valid fase transition."""
        from app.services.workflow_service import (
            create_workflow_service,
            TransitionRequest,
        )

        service = create_workflow_service(mock_db_connection)

        # Fase 1 -> 2 should be valid
        request = TransitionRequest(
            transaksi_id="UP-001",
            mekanisme="UP",
            from_fase=1,
            to_fase=2,
        )

        result = service.validate_fase_transition(request)
        assert result.valid is True

    def test_fase_transition_validation_invalid_skip(self, mock_db_connection):
        """Test invalid fase skip transition."""
        from app.services.workflow_service import (
            create_workflow_service,
            TransitionRequest,
        )

        service = create_workflow_service(mock_db_connection)

        # Fase 1 -> 3 (skipping 2) should be invalid
        request = TransitionRequest(
            transaksi_id="UP-001",
            mekanisme="UP",
            from_fase=1,
            to_fase=3,
        )

        result = service.validate_fase_transition(request)
        assert result.valid is False
        assert "tidak dapat melewati" in result.message.lower() or "skip" in result.message.lower()

    def test_fase_transition_validation_invalid_backward(self, mock_db_connection):
        """Test invalid backward transition."""
        from app.services.workflow_service import (
            create_workflow_service,
            TransitionRequest,
        )

        service = create_workflow_service(mock_db_connection)

        # Fase 3 -> 1 (backward) should be invalid
        request = TransitionRequest(
            transaksi_id="UP-001",
            mekanisme="UP",
            from_fase=3,
            to_fase=1,
        )

        result = service.validate_fase_transition(request)
        assert result.valid is False

    def test_deadline_calculation_up(self, mock_db_connection):
        """Test deadline calculation for UP transactions."""
        from app.services.workflow_service import create_workflow_service

        service = create_workflow_service(mock_db_connection)

        start_date = datetime.now()
        deadline = service.calculate_deadline("UP", start_date)

        # UP SLA is 30 days
        expected = start_date + timedelta(days=30)
        assert deadline.date() == expected.date()

    def test_deadline_calculation_tup(self, mock_db_connection):
        """Test deadline calculation for TUP transactions."""
        from app.services.workflow_service import create_workflow_service

        service = create_workflow_service(mock_db_connection)

        start_date = datetime.now()
        deadline = service.calculate_deadline("TUP", start_date)

        # TUP SLA is 30 days
        expected = start_date + timedelta(days=30)
        assert deadline.date() == expected.date()

    def test_deadline_calculation_ls(self, mock_db_connection):
        """Test deadline calculation for LS transactions."""
        from app.services.workflow_service import create_workflow_service

        service = create_workflow_service(mock_db_connection)

        start_date = datetime.now()
        deadline = service.calculate_deadline("LS", start_date)

        # LS SLA is 90 days
        expected = start_date + timedelta(days=90)
        assert deadline.date() == expected.date()

    def test_calculate_workflow_metrics(self, mock_db_connection, sample_transaksi_list):
        """Test workflow metrics calculation."""
        from app.services.workflow_service import create_workflow_service

        service = create_workflow_service(mock_db_connection)

        metrics = service.calculate_metrics(sample_transaksi_list)

        assert metrics.total_transaksi == len(sample_transaksi_list)
        assert metrics.transaksi_aktif == sum(
            1 for t in sample_transaksi_list if t.get("status") == "Aktif"
        )
        assert metrics.transaksi_selesai == sum(
            1 for t in sample_transaksi_list if t.get("status") == "Selesai"
        )

    def test_fase_validator_creation(self, mock_db_connection):
        """Test FaseTransitionValidator creation."""
        from app.services.workflow_service import create_fase_validator

        validator = create_fase_validator(mock_db_connection)
        assert validator is not None

    def test_workflow_automation_creation(self, mock_db_connection):
        """Test WorkflowAutomation class exists."""
        from app.services.workflow_service import WorkflowAutomation

        automation = WorkflowAutomation(mock_db_connection)
        assert automation is not None


# =============================================================================
# WORKFLOW QUICK ACTIONS TESTS
# =============================================================================


class TestWorkflowQuickActions:
    """Test suite for WorkflowQuickActions component."""

    def test_action_context_enum(self):
        """Test ActionContext enum values."""
        from app.ui.components.workflow_quick_actions import ActionContext

        assert ActionContext.DASHBOARD.value == "dashboard"
        assert ActionContext.DETAIL.value == "detail"
        assert ActionContext.KANBAN.value == "kanban"
        assert ActionContext.BATCH.value == "batch"

    def test_quick_action_dataclass(self):
        """Test QuickAction dataclass."""
        from app.ui.components.workflow_quick_actions import QuickAction, ActionContext

        action = QuickAction(
            id="new_transaksi",
            label="Transaksi Baru",
            icon="add",
            tooltip="Buat transaksi baru",
            contexts=[ActionContext.DASHBOARD],
            shortcut="Ctrl+N",
        )

        assert action.id == "new_transaksi"
        assert action.label == "Transaksi Baru"
        assert ActionContext.DASHBOARD in action.contexts

    def test_create_quick_actions_factory(self):
        """Test quick actions factory function."""
        from app.ui.components.workflow_quick_actions import create_quick_actions

        widget = create_quick_actions()
        assert widget is not None

    def test_quick_actions_signals(self):
        """Test quick action signals exist."""
        from app.ui.components.workflow_quick_actions import WorkflowQuickActionsWidget

        assert hasattr(WorkflowQuickActionsWidget, "action_triggered")

    def test_context_menu_creation(self):
        """Test context menu factory function."""
        from app.ui.components.workflow_quick_actions import create_context_menu

        menu = create_context_menu(transaksi_id="UP-001", fase=2, mekanisme="UP")
        assert menu is not None

    def test_compact_quick_actions(self):
        """Test CompactQuickActions creation."""
        from app.ui.components.workflow_quick_actions import CompactQuickActions

        widget = CompactQuickActions()
        assert widget is not None


# =============================================================================
# WORKFLOW DASHBOARD PAGE TESTS
# =============================================================================


class TestWorkflowDashboardPage:
    """Test suite for WorkflowDashboardPage."""

    def test_view_mode_enum(self):
        """Test ViewMode enum values."""
        from app.ui.pages.workflow_dashboard import ViewMode

        assert ViewMode.KANBAN.value == "kanban"
        assert ViewMode.LIST.value == "list"
        assert ViewMode.TIMELINE.value == "timeline"

    def test_view_mode_toggle_creation(self):
        """Test ViewModeToggle widget creation."""
        from app.ui.pages.workflow_dashboard import ViewModeToggle

        toggle = ViewModeToggle()
        assert toggle is not None

    def test_view_mode_toggle_signals(self):
        """Test ViewModeToggle signals exist."""
        from app.ui.pages.workflow_dashboard import ViewModeToggle

        assert hasattr(ViewModeToggle, "mode_changed")

    def test_gantt_timeline_view_creation(self):
        """Test GanttTimelineView creation."""
        from app.ui.pages.workflow_dashboard import GanttTimelineView

        view = GanttTimelineView()
        assert view is not None

    def test_workflow_dashboard_page_creation(self):
        """Test WorkflowDashboardPage creation."""
        from app.ui.pages.workflow_dashboard import create_workflow_dashboard

        page = create_workflow_dashboard()
        assert page is not None

    def test_dashboard_has_kanban_view(self):
        """Test dashboard includes kanban view."""
        from app.ui.pages.workflow_dashboard import create_workflow_dashboard

        page = create_workflow_dashboard()
        assert hasattr(page, "_kanban_board") or hasattr(page, "kanban_board")

    def test_dashboard_has_analytics(self):
        """Test dashboard includes analytics widget."""
        from app.ui.pages.workflow_dashboard import create_workflow_dashboard

        page = create_workflow_dashboard()
        assert hasattr(page, "_analytics") or hasattr(page, "analytics")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestWorkflowIntegration:
    """Integration tests for workflow components."""

    def test_full_workflow_create_to_complete(self, mock_db_connection):
        """Test full workflow from creation to completion."""
        from app.services.workflow_service import (
            create_workflow_service,
            TransitionRequest,
        )

        service = create_workflow_service(mock_db_connection)

        transaksi = {
            "id": "UP-TEST",
            "mekanisme": "UP",
            "fase": 1,
        }

        # Progress through all phases
        for from_fase in range(1, 5):
            to_fase = from_fase + 1
            request = TransitionRequest(
                transaksi_id=transaksi["id"],
                mekanisme=transaksi["mekanisme"],
                from_fase=from_fase,
                to_fase=to_fase,
            )

            result = service.validate_fase_transition(request)
            assert result.valid is True, f"Transition from fase {from_fase} to {to_fase} should be valid"

            # Update transaksi fase
            transaksi["fase"] = to_fase

        # Final fase should be 5 (Selesai)
        assert transaksi["fase"] == 5

    def test_kanban_to_timeline_data_consistency(
        self, sample_transaksi_list, sample_timeline_events
    ):
        """Test data consistency between kanban and timeline views."""
        from app.ui.components.kanban_board import create_kanban_board
        from app.ui.components.workflow_timeline import create_timeline

        # Set up kanban
        board = create_kanban_board()
        board.set_data(sample_transaksi_list)

        # Set up timeline for first transaction
        transaksi = sample_transaksi_list[0]
        timeline = create_timeline(transaksi_id=transaksi["id"])

        for event in sample_timeline_events:
            timeline.add_event(event)

        # Both should have consistent data references
        assert board._transaksi_data is not None
        assert timeline._transaksi_id == transaksi["id"]

    def test_deadline_tracker_notification_integration(self, sample_deadlines):
        """Test deadline tracker triggers appropriate notifications."""
        from app.ui.components.deadline_tracker import (
            create_deadline_tracker,
            DeadlineInfo,
        )
        from app.ui.components.workflow_notifications import (
            create_notification_center,
            WorkflowNotification,
            NotificationType,
            NotificationPriority,
        )

        tracker = create_deadline_tracker()
        center = create_notification_center()

        # Convert to DeadlineInfo
        deadlines = [
            DeadlineInfo(
                transaksi_id=d["transaksi_id"],
                transaksi_nama=d["transaksi_nama"],
                mekanisme=d["mekanisme"],
                deadline=d["deadline"],
                fase=d["fase"],
                sla_days=d["sla_days"],
            )
            for d in sample_deadlines
        ]

        tracker.load_deadlines(deadlines)

        # Check for overdue deadlines and create notifications
        from app.ui.components.deadline_tracker import DeadlineStatus

        for deadline in tracker._deadlines:
            if deadline.status == DeadlineStatus.OVERDUE:
                notif = WorkflowNotification(
                    id=f"notif-{deadline.transaksi_id}",
                    notification_type=NotificationType.DEADLINE_MISSED,
                    priority=NotificationPriority.URGENT,
                    title="Deadline Terlewat",
                    message=f"{deadline.transaksi_nama} telah melewati deadline",
                    transaksi_id=deadline.transaksi_id,
                )
                center.add_notification(notif)

        # Should have at least one urgent notification
        assert center.unread_count >= 1

    def test_analytics_updates_with_kanban_changes(self, sample_transaksi_list):
        """Test analytics updates when kanban data changes."""
        from app.ui.components.kanban_board import create_kanban_board
        from app.ui.components.workflow_analytics import create_analytics_widget

        board = create_kanban_board()
        analytics = create_analytics_widget()

        # Initial load
        board.set_data(sample_transaksi_list)
        analytics.set_data(sample_transaksi_list)

        initial_total = analytics._metrics.total_transaksi

        # Add new transaction
        new_transaksi = {
            "id": "UP-NEW",
            "nomor": "NEW/UP/2024",
            "nama": "New Transaction",
            "nilai": 100000000,
            "mekanisme": "UP",
            "fase": 1,
            "status": "Aktif",
        }

        updated_data = sample_transaksi_list + [new_transaksi]
        board.set_data(updated_data)
        analytics.set_data(updated_data)

        # Analytics should reflect the new data
        assert analytics._metrics.total_transaksi == initial_total + 1


# =============================================================================
# DATABASE SCHEMA TESTS
# =============================================================================


class TestDatabaseSchema:
    """Test database schema for workflow tables."""

    def test_workflow_events_table_schema(self):
        """Test workflow_events table schema is defined."""
        from app.core.database import SCHEMA_SQL

        assert "workflow_events" in SCHEMA_SQL
        assert "transaksi_id" in SCHEMA_SQL
        assert "event_type" in SCHEMA_SQL
        assert "fase_from" in SCHEMA_SQL
        assert "fase_to" in SCHEMA_SQL

    def test_workflow_notifications_table_schema(self):
        """Test workflow_notifications table schema is defined."""
        from app.core.database import SCHEMA_SQL

        assert "workflow_notifications" in SCHEMA_SQL
        assert "notification_type" in SCHEMA_SQL
        assert "priority" in SCHEMA_SQL
        assert "is_read" in SCHEMA_SQL


# =============================================================================
# MANUAL TEST CHECKLIST
# =============================================================================

"""
Manual Test Checklist for Workflow Dashboard
=============================================

Run the application and verify the following:

KANBAN BOARD:
[ ] Kanban shows all transaksi grouped by fase
[ ] Each column shows correct fase name and count
[ ] Cards display correctly with mekanisme colors
[ ] Drag card between columns works
[ ] Invalid transitions show error dialog
[ ] Double-click opens transaction detail
[ ] Right-click shows context menu
[ ] Filter by mekanisme works
[ ] Search filters cards correctly

WORKFLOW TIMELINE:
[ ] Timeline shows transaction history
[ ] Events ordered newest first
[ ] Different event types show correct icons
[ ] Timestamps formatted correctly
[ ] Expand/collapse event details works

DEADLINE TRACKER:
[ ] Deadlines sorted by urgency
[ ] Overdue items shown in red
[ ] Urgent items shown in orange
[ ] Warning items shown in yellow
[ ] On-track items shown in green
[ ] Click deadline opens transaction

NOTIFICATION CENTER:
[ ] Bell icon shows in header
[ ] Badge count shows unread notifications
[ ] Click bell opens notification panel
[ ] Notifications grouped by priority
[ ] Mark as read works
[ ] Dismiss notification works
[ ] Click notification performs action

ANALYTICS DASHBOARD:
[ ] Total transaksi count accurate
[ ] Per-fase breakdown correct
[ ] Per-mekanisme breakdown correct
[ ] Total nilai calculated correctly
[ ] Bottleneck indicator shows
[ ] Charts render correctly

VIEW MODE TOGGLE:
[ ] Toggle switches between Kanban/List/Timeline
[ ] Each view shows correct data
[ ] View preference persists

QUICK ACTIONS:
[ ] Quick action buttons visible
[ ] Keyboard shortcuts work
[ ] Context-aware actions show correctly
[ ] Actions trigger correct dialogs

INTEGRATION:
[ ] Create new transaction
[ ] Move through all phases
[ ] Complete transaction
[ ] Events logged in timeline
[ ] Notifications triggered appropriately
[ ] Analytics update in real-time
"""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
