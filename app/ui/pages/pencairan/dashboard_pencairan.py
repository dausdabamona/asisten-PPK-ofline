"""
PPK DOCUMENT FACTORY - Dashboard Pencairan Page
================================================
Dashboard utama untuk pencairan dana dengan overview UP, TUP, dan LS.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QScrollArea, QFrame, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from typing import Dict, Any

# Import components
from ...components.dashboard_cards import (
    MekanismeCard,
    TransaksiAktifCard,
    SaldoUPWidget,
    QuickActionBar
)


class DashboardPencairanPage(QWidget):
    """
    Dashboard utama pencairan dana.

    Signals:
        mekanisme_selected(str): Emitted when a mekanisme card is clicked
        transaksi_selected(int): Emitted when a transaction is selected
        new_transaksi(str): Emitted when new transaction button is clicked
    """

    mekanisme_selected = Signal(str)
    transaksi_selected = Signal(int)
    new_transaksi = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup dashboard UI."""
        # Scroll area for responsive content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Quick action bar
        self.action_bar = QuickActionBar()
        self.action_bar.action_clicked.connect(self._on_quick_action)
        main_layout.addWidget(self.action_bar)

        # Mekanisme cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # UP Card
        self.up_card = MekanismeCard("UP")
        self.up_card.clicked.connect(lambda: self.mekanisme_selected.emit("UP"))
        self.up_card.action_clicked.connect(lambda m: self.new_transaksi.emit(m))
        cards_layout.addWidget(self.up_card)

        # TUP Card
        self.tup_card = MekanismeCard("TUP")
        self.tup_card.clicked.connect(lambda: self.mekanisme_selected.emit("TUP"))
        self.tup_card.action_clicked.connect(lambda m: self.new_transaksi.emit(m))
        cards_layout.addWidget(self.tup_card)

        # LS Card
        self.ls_card = MekanismeCard("LS")
        self.ls_card.clicked.connect(lambda: self.mekanisme_selected.emit("LS"))
        self.ls_card.action_clicked.connect(lambda m: self.new_transaksi.emit(m))
        cards_layout.addWidget(self.ls_card)

        main_layout.addLayout(cards_layout)

        # Bottom row: Saldo UP + Transaksi Aktif
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        # Saldo UP widget
        self.saldo_widget = SaldoUPWidget()
        self.saldo_widget.setMaximumWidth(300)
        bottom_layout.addWidget(self.saldo_widget)

        # Transaksi Aktif card
        self.aktif_card = TransaksiAktifCard()
        self.aktif_card.item_clicked.connect(self.transaksi_selected.emit)
        bottom_layout.addWidget(self.aktif_card, 1)

        main_layout.addLayout(bottom_layout)

        # Stretch
        main_layout.addStretch()

        scroll.setWidget(content)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def _create_header(self) -> QWidget:
        """Create page header."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 10)

        # Title
        title = QLabel("Dashboard Pencairan Dana")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        """)
        layout.addWidget(title)

        layout.addStretch()

        # Period info
        from datetime import datetime
        bulan_names = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        now = datetime.now()
        period = QLabel(f"{bulan_names[now.month - 1]} {now.year}")
        period.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
        """)
        layout.addWidget(period)

        return header

    def _on_quick_action(self, action: str):
        """Handle quick action button click."""
        mekanisme_map = {
            "new_up": "UP",
            "new_tup": "TUP",
            "new_ls": "LS",
        }
        if action in mekanisme_map:
            self.new_transaksi.emit(mekanisme_map[action])

    def update_statistics(self, stats: Dict[str, Dict[str, Any]]):
        """
        Update all statistics displays.

        Args:
            stats: Dictionary with stats per mekanisme
                {
                    "UP": {"total": 5, "nilai": 25000000, "selesai": 3},
                    "TUP": {...},
                    "LS": {...}
                }
        """
        if "UP" in stats:
            s = stats["UP"]
            self.up_card.update_stats(
                total=s.get("total", 0),
                nilai=s.get("nilai", 0),
                selesai=s.get("selesai", 0)
            )

        if "TUP" in stats:
            s = stats["TUP"]
            self.tup_card.update_stats(
                total=s.get("total", 0),
                nilai=s.get("nilai", 0),
                selesai=s.get("selesai", 0)
            )

        if "LS" in stats:
            s = stats["LS"]
            self.ls_card.update_stats(
                total=s.get("total", 0),
                nilai=s.get("nilai", 0),
                selesai=s.get("selesai", 0)
            )

    def update_saldo_up(self, tersedia: float, terpakai: float, maksimal: float = 50_000_000):
        """Update saldo UP display."""
        self.saldo_widget.update_saldo(tersedia, terpakai, maksimal)

    def set_transaksi_aktif(self, transaksi_list: list):
        """Set list of active transactions."""
        self.aktif_card.set_items(transaksi_list)

    def refresh(self):
        """Refresh all data from database."""
        # This would be called by parent to refresh data
        pass
