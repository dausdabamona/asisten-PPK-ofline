"""
PPK DOCUMENT FACTORY - Kanban Board Component Tests
====================================================
Comprehensive tests for KanbanCard, KanbanColumn, and KanbanBoard components.

Run with:
    python -m pytest tests/test_kanban_board.py -v

Author: PPK Document Factory Team
Version: 4.0
"""

import sys
import unittest
from datetime import date, timedelta
from typing import Dict, List, Any
from unittest.mock import MagicMock, patch

# Add app to path
sys.path.insert(0, '.')

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtTest import QTest, QSignalSpy

# Import components to test
from app.ui.components.kanban_board import (
    KanbanCard,
    KanbanColumn,
    KanbanBoard,
    Mekanisme,
    Urgency,
    MEKANISME_COLORS,
    URGENCY_COLORS,
    FASE_CONFIG,
    KANBAN_MIME_TYPE,
    create_kanban_board,
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
        transaksi.append({
            "id": f"TRX-{i+1:03d}",
            "nomor": f"2024/UP/{i+1:03d}",
            "nama": f"Pengadaan Barang Test {i+1}",
            "nilai": 10_000_000 * (i + 1),
            "status": "Aktif",
            "mekanisme": mekanisme_types[i % 3],
            "fase": (i % 5) + 1,
            "deadline": date.today() + timedelta(days=i - 2)  # Some overdue, some normal
        })

    return transaksi


# =============================================================================
# KANBAN CARD TESTS
# =============================================================================

class TestKanbanCard(unittest.TestCase):
    """Test cases for KanbanCard component."""

    def setUp(self):
        """Set up test fixtures."""
        self.card = KanbanCard(
            transaksi_id="TRX-001",
            nomor="2024/UP/001",
            nama="Pengadaan Laptop Kantor",
            nilai=50_000_000,
            status="Aktif",
            deadline=date.today() + timedelta(days=5),
            mekanisme="UP",
            fase=1
        )

    def tearDown(self):
        """Clean up after tests."""
        self.card.deleteLater()

    def test_card_initialization(self):
        """Test card initializes with correct data."""
        self.assertEqual(self.card.transaksi_id, "TRX-001")
        self.assertEqual(self.card.nomor, "2024/UP/001")
        self.assertEqual(self.card.nama, "Pengadaan Laptop Kantor")
        self.assertEqual(self.card.nilai, 50_000_000)
        self.assertEqual(self.card.status, "Aktif")
        self.assertEqual(self.card.mekanisme, "UP")
        self.assertEqual(self.card.fase, 1)

    def test_card_dimensions(self):
        """Test card has correct dimensions."""
        self.assertEqual(self.card.width(), KanbanCard.CARD_WIDTH)
        self.assertGreaterEqual(self.card.height(), KanbanCard.CARD_MIN_HEIGHT)

    def test_card_ui_elements_exist(self):
        """Test card UI elements are created."""
        self.assertIsNotNone(self.card.nomor_label)
        self.assertIsNotNone(self.card.nama_label)
        self.assertIsNotNone(self.card.nilai_label)
        self.assertIsNotNone(self.card.status_label)
        self.assertIsNotNone(self.card.mekanisme_badge)
        self.assertIsNotNone(self.card.urgency_bar)

    def test_card_labels_display_data(self):
        """Test labels display correct data."""
        self.assertEqual(self.card.nomor_label.text(), "2024/UP/001")
        self.assertEqual(self.card.nama_label.text(), "Pengadaan Laptop Kantor")
        self.assertEqual(self.card.mekanisme_badge.text(), "UP")
        self.assertEqual(self.card.status_label.text(), "Aktif")

    def test_currency_formatting_millions(self):
        """Test currency formatting for millions."""
        card = KanbanCard(
            transaksi_id="TRX-002",
            nomor="002",
            nama="Test",
            nilai=50_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1
        )
        self.assertIn("50", card.nilai_label.text())
        self.assertIn("jt", card.nilai_label.text())
        card.deleteLater()

    def test_currency_formatting_billions(self):
        """Test currency formatting for billions."""
        card = KanbanCard(
            transaksi_id="TRX-003",
            nomor="003",
            nama="Test",
            nilai=1_500_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1
        )
        self.assertIn("1.5", card.nilai_label.text())
        self.assertIn("M", card.nilai_label.text())
        card.deleteLater()

    def test_currency_formatting_thousands(self):
        """Test currency formatting for thousands."""
        card = KanbanCard(
            transaksi_id="TRX-004",
            nomor="004",
            nama="Test",
            nilai=500_000,
            status="Aktif",
            mekanisme="UP",
            fase=1
        )
        self.assertIn("500", card.nilai_label.text())
        self.assertIn("rb", card.nilai_label.text())
        card.deleteLater()

    def test_mekanisme_colors_up(self):
        """Test UP mekanisme uses green colors."""
        self.assertEqual(self.card.mekanisme, "UP")
        # Colors should be from MEKANISME_COLORS["UP"]
        colors = MEKANISME_COLORS["UP"]
        self.assertIsNotNone(colors)
        self.assertEqual(colors["bg"], "#e8f5e9")  # Green background

    def test_mekanisme_colors_tup(self):
        """Test TUP mekanisme uses orange colors."""
        card = KanbanCard(
            transaksi_id="TRX-TUP",
            nomor="TUP-001",
            nama="Test TUP",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="TUP",
            fase=1
        )
        colors = MEKANISME_COLORS["TUP"]
        self.assertEqual(colors["bg"], "#fff3e0")  # Orange background
        card.deleteLater()

    def test_mekanisme_colors_ls(self):
        """Test LS mekanisme uses blue colors."""
        card = KanbanCard(
            transaksi_id="TRX-LS",
            nomor="LS-001",
            nama="Test LS",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="LS",
            fase=1
        )
        colors = MEKANISME_COLORS["LS"]
        self.assertEqual(colors["bg"], "#e3f2fd")  # Blue background
        card.deleteLater()

    def test_urgency_normal(self):
        """Test normal urgency calculation (> 3 days)."""
        card = KanbanCard(
            transaksi_id="TRX-NORMAL",
            nomor="001",
            nama="Test",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1,
            deadline=date.today() + timedelta(days=10)
        )
        urgency = card._calculate_urgency()
        self.assertEqual(urgency, Urgency.NORMAL)
        card.deleteLater()

    def test_urgency_warning(self):
        """Test warning urgency calculation (1-3 days)."""
        card = KanbanCard(
            transaksi_id="TRX-WARN",
            nomor="001",
            nama="Test",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1,
            deadline=date.today() + timedelta(days=2)
        )
        urgency = card._calculate_urgency()
        self.assertEqual(urgency, Urgency.WARNING)
        card.deleteLater()

    def test_urgency_overdue(self):
        """Test overdue urgency calculation (< 0 days)."""
        card = KanbanCard(
            transaksi_id="TRX-OVER",
            nomor="001",
            nama="Test",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1,
            deadline=date.today() - timedelta(days=2)
        )
        urgency = card._calculate_urgency()
        self.assertEqual(urgency, Urgency.OVERDUE)
        card.deleteLater()

    def test_urgency_no_deadline(self):
        """Test urgency with no deadline returns normal."""
        card = KanbanCard(
            transaksi_id="TRX-NO-DL",
            nomor="001",
            nama="Test",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1,
            deadline=None
        )
        urgency = card._calculate_urgency()
        self.assertEqual(urgency, Urgency.NORMAL)
        card.deleteLater()

    def test_deadline_formatting_overdue(self):
        """Test deadline formatting for overdue."""
        card = KanbanCard(
            transaksi_id="TRX-FMT",
            nomor="001",
            nama="Test",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1,
            deadline=date.today() - timedelta(days=3)
        )
        text = card._format_deadline()
        self.assertIn("overdue", text)
        card.deleteLater()

    def test_deadline_formatting_today(self):
        """Test deadline formatting for today."""
        card = KanbanCard(
            transaksi_id="TRX-TODAY",
            nomor="001",
            nama="Test",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1,
            deadline=date.today()
        )
        text = card._format_deadline()
        self.assertEqual(text, "Hari ini")
        card.deleteLater()

    def test_deadline_formatting_tomorrow(self):
        """Test deadline formatting for tomorrow."""
        card = KanbanCard(
            transaksi_id="TRX-TOM",
            nomor="001",
            nama="Test",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1,
            deadline=date.today() + timedelta(days=1)
        )
        text = card._format_deadline()
        self.assertEqual(text, "Besok")
        card.deleteLater()

    def test_clicked_signal(self):
        """Test clicked signal is emitted on click."""
        spy = QSignalSpy(self.card.clicked)
        QTest.mouseClick(self.card, Qt.LeftButton)
        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], "TRX-001")

    def test_get_data(self):
        """Test get_data returns correct dictionary."""
        data = self.card.get_data()
        self.assertEqual(data["transaksi_id"], "TRX-001")
        self.assertEqual(data["nomor"], "2024/UP/001")
        self.assertEqual(data["nama"], "Pengadaan Laptop Kantor")
        self.assertEqual(data["nilai"], 50_000_000)
        self.assertEqual(data["status"], "Aktif")
        self.assertEqual(data["mekanisme"], "UP")
        self.assertEqual(data["fase"], 1)

    def test_update_data(self):
        """Test update_data modifies card."""
        self.card.update_data({
            "nomor": "2024/UP/002",
            "nama": "Updated Name",
            "nilai": 75_000_000,
            "status": "Selesai"
        })
        self.assertEqual(self.card.nomor, "2024/UP/002")
        self.assertEqual(self.card.nama, "Updated Name")
        self.assertEqual(self.card.nilai, 75_000_000)
        self.assertEqual(self.card.status, "Selesai")

    def test_cursor_is_pointing_hand(self):
        """Test card has pointing hand cursor."""
        self.assertEqual(self.card.cursor().shape(), Qt.PointingHandCursor)


# =============================================================================
# KANBAN COLUMN TESTS
# =============================================================================

class TestKanbanColumn(unittest.TestCase):
    """Test cases for KanbanColumn component."""

    def setUp(self):
        """Set up test fixtures."""
        self.column = KanbanColumn(fase=1)

    def tearDown(self):
        """Clean up after tests."""
        self.column.deleteLater()

    def test_column_initialization(self):
        """Test column initializes with correct data."""
        self.assertEqual(self.column.fase, 1)
        self.assertEqual(self.column.nama, "Inisiasi")  # From FASE_CONFIG
        self.assertFalse(self.column._collapsed)

    def test_column_dimensions(self):
        """Test column has correct dimensions."""
        self.assertEqual(self.column.width(), KanbanColumn.COLUMN_WIDTH)

    def test_column_ui_elements_exist(self):
        """Test column UI elements are created."""
        self.assertIsNotNone(self.column.header)
        self.assertIsNotNone(self.column.scroll_area)
        self.assertIsNotNone(self.column.footer)
        self.assertIsNotNone(self.column.count_badge)
        self.assertIsNotNone(self.column.nilai_label)
        self.assertIsNotNone(self.column.collapse_btn)

    def test_column_accepts_drops(self):
        """Test column accepts drops."""
        self.assertTrue(self.column.acceptDrops())

    def test_add_card(self):
        """Test adding a card to the column."""
        card = KanbanCard(
            transaksi_id="TRX-001",
            nomor="001",
            nama="Test",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1
        )
        self.column.add_card(card)

        self.assertEqual(len(self.column.get_cards()), 1)
        self.assertEqual(self.column.count_badge.text(), "1")

    def test_add_multiple_cards(self):
        """Test adding multiple cards."""
        for i in range(3):
            card = KanbanCard(
                transaksi_id=f"TRX-{i}",
                nomor=f"{i:03d}",
                nama=f"Test {i}",
                nilai=10_000_000 * (i + 1),
                status="Aktif",
                mekanisme="UP",
                fase=1
            )
            self.column.add_card(card)

        self.assertEqual(len(self.column.get_cards()), 3)
        self.assertEqual(self.column.count_badge.text(), "3")

    def test_remove_card(self):
        """Test removing a card from the column."""
        card = KanbanCard(
            transaksi_id="TRX-001",
            nomor="001",
            nama="Test",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1
        )
        self.column.add_card(card)
        self.assertEqual(len(self.column.get_cards()), 1)

        removed = self.column.remove_card("TRX-001")
        self.assertIsNotNone(removed)
        self.assertEqual(len(self.column.get_cards()), 0)
        self.assertEqual(self.column.count_badge.text(), "0")
        removed.deleteLater()

    def test_remove_nonexistent_card(self):
        """Test removing a nonexistent card returns None."""
        removed = self.column.remove_card("NONEXISTENT")
        self.assertIsNone(removed)

    def test_get_card(self):
        """Test getting a specific card by ID."""
        card = KanbanCard(
            transaksi_id="TRX-001",
            nomor="001",
            nama="Test",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1
        )
        self.column.add_card(card)

        found = self.column.get_card("TRX-001")
        self.assertIsNotNone(found)
        self.assertEqual(found.transaksi_id, "TRX-001")

    def test_get_nonexistent_card(self):
        """Test getting nonexistent card returns None."""
        found = self.column.get_card("NONEXISTENT")
        self.assertIsNone(found)

    def test_total_nilai_calculation(self):
        """Test total nilai is calculated correctly."""
        for i in range(3):
            card = KanbanCard(
                transaksi_id=f"TRX-{i}",
                nomor=f"{i:03d}",
                nama=f"Test {i}",
                nilai=10_000_000,  # 10 juta each
                status="Aktif",
                mekanisme="UP",
                fase=1
            )
            self.column.add_card(card)

        self.assertEqual(self.column.get_total_nilai(), 30_000_000)

    def test_collapse_column(self):
        """Test collapsing the column."""
        self.assertFalse(self.column.is_collapsed())

        self.column.set_collapsed(True)
        self.assertTrue(self.column.is_collapsed())
        self.assertEqual(self.column.collapse_btn.text(), "+")

        self.column.set_collapsed(False)
        self.assertFalse(self.column.is_collapsed())
        self.assertEqual(self.column.collapse_btn.text(), "−")

    def test_clear_column(self):
        """Test clearing all cards from column."""
        for i in range(3):
            card = KanbanCard(
                transaksi_id=f"TRX-{i}",
                nomor=f"{i:03d}",
                nama=f"Test {i}",
                nilai=10_000_000,
                status="Aktif",
                mekanisme="UP",
                fase=1
            )
            self.column.add_card(card)

        self.assertEqual(len(self.column.get_cards()), 3)

        self.column.clear()
        self.assertEqual(len(self.column.get_cards()), 0)
        self.assertEqual(self.column.get_total_nilai(), 0)

    def test_card_clicked_signal_forwarded(self):
        """Test card clicked signal is forwarded from column."""
        spy = QSignalSpy(self.column.card_clicked)

        card = KanbanCard(
            transaksi_id="TRX-001",
            nomor="001",
            nama="Test",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1
        )
        self.column.add_card(card)

        # Simulate click
        card.clicked.emit("TRX-001")

        self.assertEqual(len(spy), 1)
        self.assertEqual(spy[0][0], "TRX-001")

    def test_duplicate_card_not_added(self):
        """Test same card cannot be added twice."""
        card = KanbanCard(
            transaksi_id="TRX-001",
            nomor="001",
            nama="Test",
            nilai=10_000_000,
            status="Aktif",
            mekanisme="UP",
            fase=1
        )
        self.column.add_card(card)
        self.column.add_card(card)  # Try adding again

        self.assertEqual(len(self.column.get_cards()), 1)

    def test_fase_config_applied(self):
        """Test fase config is applied correctly."""
        # Fase 1 should have "Inisiasi" name
        col1 = KanbanColumn(fase=1)
        self.assertEqual(col1.nama, "Inisiasi")
        self.assertEqual(col1.icon, "📋")
        col1.deleteLater()

        # Fase 5 should have "SPBY & Selesai" name
        col5 = KanbanColumn(fase=5)
        self.assertEqual(col5.nama, "SPBY & Selesai")
        self.assertEqual(col5.icon, "✅")
        col5.deleteLater()


# =============================================================================
# KANBAN BOARD TESTS
# =============================================================================

class TestKanbanBoard(unittest.TestCase):
    """Test cases for KanbanBoard component."""

    def setUp(self):
        """Set up test fixtures."""
        self.board = KanbanBoard()
        self.sample_data = create_sample_transaksi(10)

    def tearDown(self):
        """Clean up after tests."""
        self.board.deleteLater()

    def test_board_initialization(self):
        """Test board initializes correctly."""
        self.assertEqual(len(self.board._columns), 5)  # 5 fases
        self.assertEqual(len(self.board._all_transaksi), 0)

    def test_board_with_default_mekanisme(self):
        """Test board with default mekanisme filter."""
        board = KanbanBoard(mekanisme="UP")
        self.assertEqual(board.default_mekanisme, "UP")
        self.assertEqual(board.mekanisme_combo.currentText(), "UP")
        board.deleteLater()

    def test_board_ui_elements_exist(self):
        """Test board UI elements are created."""
        self.assertIsNotNone(self.board.mekanisme_combo)
        self.assertIsNotNone(self.board.periode_combo)
        self.assertIsNotNone(self.board.search_input)
        self.assertIsNotNone(self.board.refresh_btn)
        self.assertIsNotNone(self.board.columns_scroll)

    def test_columns_created(self):
        """Test all 5 columns are created."""
        for fase in range(1, 6):
            column = self.board.get_column(fase)
            self.assertIsNotNone(column)
            self.assertEqual(column.fase, fase)

    def test_set_data(self):
        """Test setting transaksi data."""
        self.board.set_data(self.sample_data)
        self.assertEqual(len(self.board._all_transaksi), 10)

    def test_data_distributed_to_columns(self):
        """Test data is distributed to correct columns."""
        self.board.set_data(self.sample_data)

        total_cards = sum(
            len(self.board.get_column(fase).get_cards())
            for fase in range(1, 6)
        )
        self.assertEqual(total_cards, 10)

    def test_get_transaksi_by_fase(self):
        """Test getting transaksi by fase."""
        self.board.set_data(self.sample_data)

        fase1_transaksi = self.board.get_transaksi_by_fase(1)
        for trx in fase1_transaksi:
            self.assertEqual(trx["fase"], 1)

    def test_filter_by_mekanisme(self):
        """Test filtering by mekanisme."""
        self.board.set_data(self.sample_data)

        # Filter by UP
        self.board.filter_by(mekanisme="UP")

        # Check filtered data
        filtered = self.board.get_filtered_transaksi()
        for trx in filtered:
            self.assertEqual(trx["mekanisme"], "UP")

    def test_filter_by_search(self):
        """Test filtering by search text."""
        self.board.set_data(self.sample_data)

        # Search for "Test 1"
        self.board.filter_by(search="Test 1")

        # Should match "Test 1" and "Test 10"
        filtered = self.board.get_filtered_transaksi()
        for trx in filtered:
            self.assertIn("Test 1", trx["nama"])

    def test_move_transaksi(self):
        """Test moving transaksi between fases."""
        self.board.set_data(self.sample_data)

        # Get a transaksi from fase 1
        fase1_transaksi = self.board.get_transaksi_by_fase(1)
        if fase1_transaksi:
            transaksi_id = fase1_transaksi[0]["transaksi_id"]

            # Move to fase 2
            self.board.move_transaksi(transaksi_id, 1, 2)

            # Verify moved
            fase2_transaksi = self.board.get_transaksi_by_fase(2)
            ids = [t["transaksi_id"] for t in fase2_transaksi]
            self.assertIn(transaksi_id, ids)

    def test_transaksi_selected_signal(self):
        """Test transaksi_selected signal is emitted."""
        spy = QSignalSpy(self.board.transaksi_selected)

        self.board.set_data(self.sample_data)

        # Simulate card click
        column = self.board.get_column(1)
        cards = column.get_cards()
        if cards:
            cards[0].clicked.emit(cards[0].transaksi_id)
            self.assertEqual(len(spy), 1)

    def test_transaksi_moved_signal(self):
        """Test transaksi_moved signal is emitted."""
        spy = QSignalSpy(self.board.transaksi_moved)

        self.board.set_data(self.sample_data)

        # Get a transaksi from fase 1
        fase1_transaksi = self.board.get_transaksi_by_fase(1)
        if fase1_transaksi:
            transaksi_id = fase1_transaksi[0]["transaksi_id"]

            # Move to fase 2
            self.board.move_transaksi(transaksi_id, 1, 2)

            self.assertEqual(len(spy), 1)
            self.assertEqual(spy[0][0], transaksi_id)
            self.assertEqual(spy[0][1], 1)  # from_fase
            self.assertEqual(spy[0][2], 2)  # to_fase

    def test_refresh(self):
        """Test refresh reapplies filters."""
        self.board.set_data(self.sample_data)

        # Filter and then refresh
        self.board.filter_by(mekanisme="UP")
        initial_count = len(self.board.get_filtered_transaksi())

        self.board.refresh()

        # Count should be same after refresh
        self.assertEqual(len(self.board.get_filtered_transaksi()), initial_count)

    def test_get_all_transaksi(self):
        """Test getting all transaksi."""
        self.board.set_data(self.sample_data)

        all_trx = self.board.get_all_transaksi()
        self.assertEqual(len(all_trx), 10)

    def test_get_filtered_transaksi(self):
        """Test getting filtered transaksi."""
        self.board.set_data(self.sample_data)

        # Without filter, should be all
        self.assertEqual(len(self.board.get_filtered_transaksi()), 10)

        # With mekanisme filter
        self.board.filter_by(mekanisme="UP")
        filtered = self.board.get_filtered_transaksi()
        self.assertTrue(len(filtered) < 10)

    def test_mekanisme_combo_options(self):
        """Test mekanisme combo has correct options."""
        options = [
            self.board.mekanisme_combo.itemText(i)
            for i in range(self.board.mekanisme_combo.count())
        ]
        self.assertIn("Semua", options)
        self.assertIn("UP", options)
        self.assertIn("TUP", options)
        self.assertIn("LS", options)

    def test_periode_combo_options(self):
        """Test periode combo has correct options."""
        options = [
            self.board.periode_combo.itemText(i)
            for i in range(self.board.periode_combo.count())
        ]
        self.assertIn("Semua", options)
        self.assertIn("Hari Ini", options)
        self.assertIn("Minggu Ini", options)
        self.assertIn("Bulan Ini", options)
        self.assertIn("Tahun Ini", options)


# =============================================================================
# FACTORY FUNCTION TESTS
# =============================================================================

class TestCreateKanbanBoard(unittest.TestCase):
    """Test cases for create_kanban_board factory function."""

    def test_create_basic_board(self):
        """Test creating basic board."""
        board = create_kanban_board()
        self.assertIsInstance(board, KanbanBoard)
        board.deleteLater()

    def test_create_board_with_mekanisme(self):
        """Test creating board with mekanisme filter."""
        board = create_kanban_board(mekanisme="TUP")
        self.assertEqual(board.mekanisme_combo.currentText(), "TUP")
        board.deleteLater()

    def test_create_board_with_data(self):
        """Test creating board with initial data."""
        data = create_sample_transaksi(5)
        board = create_kanban_board(transaksi_list=data)
        self.assertEqual(len(board.get_all_transaksi()), 5)
        board.deleteLater()

    def test_create_board_with_all_params(self):
        """Test creating board with all parameters."""
        data = create_sample_transaksi(5)
        board = create_kanban_board(
            mekanisme="LS",
            transaksi_list=data
        )
        self.assertEqual(board.mekanisme_combo.currentText(), "LS")
        self.assertEqual(len(board.get_all_transaksi()), 5)
        board.deleteLater()


# =============================================================================
# CONFIGURATION TESTS
# =============================================================================

class TestKanbanConfiguration(unittest.TestCase):
    """Test cases for Kanban configuration constants."""

    def test_mekanisme_enum(self):
        """Test Mekanisme enum values."""
        self.assertEqual(Mekanisme.UP.value, "UP")
        self.assertEqual(Mekanisme.TUP.value, "TUP")
        self.assertEqual(Mekanisme.LS.value, "LS")

    def test_urgency_enum(self):
        """Test Urgency enum values."""
        self.assertEqual(Urgency.NORMAL.value, "normal")
        self.assertEqual(Urgency.WARNING.value, "warning")
        self.assertEqual(Urgency.OVERDUE.value, "overdue")

    def test_mekanisme_colors_complete(self):
        """Test all mekanisme colors are defined."""
        for mek in ["UP", "TUP", "LS", "default"]:
            self.assertIn(mek, MEKANISME_COLORS)
            colors = MEKANISME_COLORS[mek]
            self.assertIn("bg", colors)
            self.assertIn("border", colors)
            self.assertIn("header", colors)
            self.assertIn("accent", colors)

    def test_urgency_colors_complete(self):
        """Test all urgency colors are defined."""
        for urg in ["normal", "warning", "overdue"]:
            self.assertIn(urg, URGENCY_COLORS)
            colors = URGENCY_COLORS[urg]
            self.assertIn("indicator", colors)
            self.assertIn("text", colors)

    def test_fase_config_complete(self):
        """Test all fase configs are defined."""
        for fase in range(1, 6):
            self.assertIn(fase, FASE_CONFIG)
            config = FASE_CONFIG[fase]
            self.assertIn("nama", config)
            self.assertIn("icon", config)
            self.assertIn("color", config)

    def test_fase_config_names(self):
        """Test fase config names are correct."""
        self.assertEqual(FASE_CONFIG[1]["nama"], "Inisiasi")
        self.assertEqual(FASE_CONFIG[2]["nama"], "Pencairan UM")
        self.assertEqual(FASE_CONFIG[3]["nama"], "Pelaksanaan")
        self.assertEqual(FASE_CONFIG[4]["nama"], "Pertanggungjawaban")
        self.assertEqual(FASE_CONFIG[5]["nama"], "SPBY & Selesai")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestKanbanIntegration(unittest.TestCase):
    """Integration tests for Kanban components working together."""

    def setUp(self):
        """Set up test fixtures."""
        self.board = KanbanBoard()
        self.sample_data = create_sample_transaksi(10)
        self.board.set_data(self.sample_data)

    def tearDown(self):
        """Clean up after tests."""
        self.board.deleteLater()

    def test_full_workflow_move(self):
        """Test full workflow: create -> move -> verify."""
        # Get initial counts
        fase1_count = len(self.board.get_column(1).get_cards())
        fase2_count = len(self.board.get_column(2).get_cards())

        # Get a transaksi from fase 1
        fase1_transaksi = self.board.get_transaksi_by_fase(1)
        if fase1_transaksi and fase1_count > 0:
            transaksi_id = fase1_transaksi[0]["transaksi_id"]

            # Move to fase 2
            self.board.move_transaksi(transaksi_id, 1, 2)

            # Verify counts changed
            self.assertEqual(
                len(self.board.get_column(1).get_cards()),
                fase1_count - 1
            )
            self.assertEqual(
                len(self.board.get_column(2).get_cards()),
                fase2_count + 1
            )

    def test_filter_and_count(self):
        """Test filtering and counting cards."""
        # Count UP transaksi
        up_count = sum(1 for t in self.sample_data if t["mekanisme"] == "UP")

        # Apply filter
        self.board.filter_by(mekanisme="UP")

        # Count cards across all columns
        total_cards = sum(
            len(self.board.get_column(fase).get_cards())
            for fase in range(1, 6)
        )

        self.assertEqual(total_cards, up_count)

    def test_search_and_select(self):
        """Test searching and selecting a card."""
        spy = QSignalSpy(self.board.transaksi_selected)

        # Search for specific transaksi
        self.board.filter_by(search="Test 1")

        # Get filtered results and click first card
        for fase in range(1, 6):
            cards = self.board.get_column(fase).get_cards()
            if cards:
                cards[0].clicked.emit(cards[0].transaksi_id)
                break

        self.assertGreater(len(spy), 0)

    def test_clear_and_reload(self):
        """Test clearing and reloading data."""
        # Initial data
        self.assertEqual(len(self.board.get_all_transaksi()), 10)

        # Clear data
        self.board.set_data([])
        self.assertEqual(len(self.board.get_all_transaksi()), 0)

        # Reload data
        self.board.set_data(self.sample_data)
        self.assertEqual(len(self.board.get_all_transaksi()), 10)


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
