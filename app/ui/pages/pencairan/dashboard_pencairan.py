"""
PPK DOCUMENT FACTORY - Dashboard Pencairan Page
================================================
Dashboard utama untuk pencairan dana dengan overview UP, TUP, dan LS.

Refactored to use modular components from app.ui.dashboard_components.

Author: PPK Document Factory Team
Version: 4.0
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from typing import Dict, Any, List
from datetime import datetime

# Import modular components from dashboard_components
from app.ui.dashboard_components import (
    StatisticsSection,
    SaldoUPWidget,
    QuickActionsWidget,
    RecentActivityWidget,
)


class DashboardPencairanPage(QWidget):
    """
    Dashboard utama pencairan dana.

    Menggunakan komponen modular:
    - StatisticsSection: 3 card UP/TUP/LS
    - SaldoUPWidget: Sisa saldo UP tersedia
    - QuickActionsWidget: Tombol aksi cepat
    - RecentActivityWidget: Transaksi yang perlu tindakan

    Signals:
        mekanisme_selected(str): Emitted when a mekanisme card is clicked
        transaksi_selected(str): Emitted when a transaction is selected (transaction_id)
        new_transaksi(str): Emitted when new transaction button is clicked (mekanisme)
        view_all_clicked(): Emitted when view all transactions button is clicked
    """

    mekanisme_selected = Signal(str)
    transaksi_selected = Signal(str)
    new_transaksi = Signal(str)
    view_all_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup dashboard UI."""
        # Scroll area for responsive content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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

        # ========================================
        # Row 1: Header
        # ========================================
        header = self._create_header()
        main_layout.addWidget(header)

        # ========================================
        # Row 2: Quick Actions
        # ========================================
        self.quick_actions = QuickActionsWidget(show_title=False)
        self.quick_actions.action_clicked.connect(self._on_quick_action)
        main_layout.addWidget(self.quick_actions)

        # ========================================
        # Row 3: Statistics Section (UP, TUP, LS cards)
        # ========================================
        self.statistics_section = StatisticsSection()
        self.statistics_section.card_clicked.connect(self.mekanisme_selected.emit)
        self.statistics_section.action_clicked.connect(self._on_card_action)
        main_layout.addWidget(self.statistics_section)

        # ========================================
        # Row 4: Saldo UP + Recent Activity
        # ========================================
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        # Saldo UP widget (left)
        self.saldo_widget = SaldoUPWidget()
        self.saldo_widget.setMaximumWidth(320)
        self.saldo_widget.setMinimumWidth(280)
        self.saldo_widget.warning_threshold.connect(self._on_saldo_warning)
        bottom_layout.addWidget(self.saldo_widget)

        # Recent Activity / Transaksi Aktif (right)
        self.recent_activity = RecentActivityWidget(
            title="Perlu Tindakan",
            max_items=5
        )
        self.recent_activity.item_clicked.connect(self.transaksi_selected.emit)
        self.recent_activity.view_all_clicked.connect(self.view_all_clicked.emit)
        self.recent_activity.set_view_all_button_text("Lihat Semua Transaksi")
        bottom_layout.addWidget(self.recent_activity, 1)

        main_layout.addLayout(bottom_layout)

        # Stretch to push content up
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
        bulan_names = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        now = datetime.now()
        period = QLabel(f"{bulan_names[now.month - 1]} {now.year}")
        period.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            background-color: #ecf0f1;
            padding: 5px 15px;
            border-radius: 15px;
        """)
        layout.addWidget(period)

        return header

    def _on_quick_action(self, action_id: str):
        """Handle quick action button click."""
        mekanisme_map = {
            "new_up": "UP",
            "new_tup": "TUP",
            "new_ls": "LS",
        }
        if action_id in mekanisme_map:
            self.new_transaksi.emit(mekanisme_map[action_id])
        elif action_id == "new_dokumen":
            # Handle document creation action
            pass

    def _on_card_action(self, mekanisme: str):
        """Handle action button click on mekanisme card."""
        self.new_transaksi.emit(mekanisme)

    def _on_saldo_warning(self):
        """Handle saldo UP warning threshold."""
        # Implement warning notification if needed
        pass

    # ========================================
    # PUBLIC API - Data Update Methods
    # ========================================

    def update_statistics(self, stats: Dict[str, Dict[str, Any]]):
        """
        Update all statistics displays.

        Args:
            stats: Dictionary with stats per mekanisme
                {
                    "UP": {"total": 5, "nilai": 25000000, "selesai": 3},
                    "TUP": {"total": 2, "nilai": 10000000, "selesai": 1},
                    "LS": {"total": 8, "nilai": 150000000, "selesai": 5}
                }
        """
        self.statistics_section.update_statistics(stats)

    def set_mekanisme_stats(
        self,
        mekanisme: str,
        total: int = 0,
        nilai: float = 0,
        selesai: int = 0
    ):
        """
        Update statistics for a specific mekanisme.

        Args:
            mekanisme: UP, TUP, or LS
            total: Total active transactions
            nilai: Total value in Rupiah
            selesai: Number of completed transactions
        """
        self.statistics_section.set_mekanisme_stats(
            mekanisme=mekanisme,
            total=total,
            nilai=nilai,
            selesai=selesai
        )

    def update_saldo_up(
        self,
        tersedia: float,
        terpakai: float,
        maksimal: float = None
    ):
        """
        Update saldo UP display.

        Args:
            tersedia: Available balance
            terpakai: Used balance
            maksimal: Maximum limit (optional, uses default if not provided)
        """
        if maksimal is not None:
            self.saldo_widget.set_batas_maksimal(maksimal)
        self.saldo_widget.update_saldo(tersedia, terpakai)

    def set_transaksi_aktif(self, transaksi_list: List[Dict[str, Any]]):
        """
        Set list of active transactions that need action.

        Args:
            transaksi_list: List of transaction dictionaries with format:
                [
                    {
                        "id": "UP-001",
                        "mekanisme": "UP",
                        "nama": "Belanja ATK",
                        "nilai": 5000000,
                        "status": "proses",
                        "tanggal": "2024-01-15"
                    },
                    ...
                ]

        Note: Field mapping from old format:
            - "id" or "kode_transaksi" -> "id"
            - "nama_kegiatan" -> "nama"
            - "nilai" -> "nilai"
            - "fase_aktif" -> mapped to status
        """
        # Transform data if needed for compatibility
        transformed = []
        for item in transaksi_list:
            trans = {
                "id": item.get("id") or item.get("kode_transaksi", ""),
                "mekanisme": item.get("mekanisme", "UP"),
                "nama": item.get("nama") or item.get("nama_kegiatan", "Transaksi"),
                "nilai": item.get("nilai", 0),
                "status": self._map_fase_to_status(item.get("fase_aktif", 1)),
                "tanggal": item.get("tanggal") or item.get("tanggal_input"),
            }
            transformed.append(trans)

        self.recent_activity.set_transactions(transformed)

    def _map_fase_to_status(self, fase: int) -> str:
        """Map fase number to status string."""
        fase_map = {
            1: "draft",
            2: "proses",
            3: "proses",
            4: "selesai",
        }
        return fase_map.get(fase, "draft")

    def add_transaksi(self, transaksi: Dict[str, Any]):
        """Add a single transaction to the recent activity list."""
        trans = {
            "id": transaksi.get("id") or transaksi.get("kode_transaksi", ""),
            "mekanisme": transaksi.get("mekanisme", "UP"),
            "nama": transaksi.get("nama") or transaksi.get("nama_kegiatan", "Transaksi"),
            "nilai": transaksi.get("nilai", 0),
            "status": self._map_fase_to_status(transaksi.get("fase_aktif", 1)),
            "tanggal": transaksi.get("tanggal") or transaksi.get("tanggal_input"),
        }
        self.recent_activity.add_transaction(trans)

    def clear_transaksi_aktif(self):
        """Clear all transactions from recent activity."""
        self.recent_activity.clear()

    def refresh(self):
        """Refresh all data displays."""
        # Refresh is triggered by parent component
        # This method can be overridden or connected to data refresh signals
        self.recent_activity.refresh()

    # ========================================
    # Component Access Methods
    # ========================================

    def get_statistics_section(self) -> StatisticsSection:
        """Get the statistics section component."""
        return self.statistics_section

    def get_saldo_widget(self) -> SaldoUPWidget:
        """Get the saldo UP widget component."""
        return self.saldo_widget

    def get_quick_actions(self) -> QuickActionsWidget:
        """Get the quick actions widget component."""
        return self.quick_actions

    def get_recent_activity(self) -> RecentActivityWidget:
        """Get the recent activity widget component."""
        return self.recent_activity

    def set_quick_action_enabled(self, action_id: str, enabled: bool):
        """Enable or disable a quick action button."""
        self.quick_actions.set_button_enabled(action_id, enabled)

    def set_quick_action_visible(self, action_id: str, visible: bool):
        """Show or hide a quick action button."""
        self.quick_actions.set_button_visible(action_id, visible)
