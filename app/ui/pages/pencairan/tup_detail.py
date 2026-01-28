"""
PPK DOCUMENT FACTORY - TUP Detail Page
=======================================
Detail page for Tambahan Uang Persediaan (TUP) transactions.
Includes countdown widget for 30-day deadline.
"""

from PySide6.QtWidgets import QVBoxLayout, QTabWidget

from .base_detail_page import BaseDetailPage
from ...components.countdown_widget import CountdownWidget

from typing import Dict, Any


class TUPDetailPage(BaseDetailPage):
    """Detail page for TUP transactions with countdown."""

    MEKANISME = "TUP"
    COLOR = "#f39c12"

    def _create_detail_panel(self):
        """Override to add countdown widget."""
        from PySide6.QtWidgets import QFrame, QVBoxLayout, QTabWidget

        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Countdown widget at top
        self.countdown_widget = CountdownWidget()
        layout.addWidget(self.countdown_widget)

        # Tabs for different sections
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                background-color: #f5f6fa;
                color: #7f8c8d;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #f39c12;
                font-weight: 500;
            }
        """)

        # Info tab
        info_widget = self._create_info_tab()
        tabs.addTab(info_widget, "Informasi")

        # Kalkulasi tab
        from ...components.kalkulasi_widget import KalkulasiWidget
        self.kalkulasi_widget = KalkulasiWidget()
        tabs.addTab(self.kalkulasi_widget, "Kalkulasi")

        # Log tab
        log_widget = self._create_log_tab()
        tabs.addTab(log_widget, "Riwayat")

        layout.addWidget(tabs)

        return panel

    def set_transaksi(self, transaksi_id: int, data: Dict[str, Any]):
        """Override to set countdown."""
        super().set_transaksi(transaksi_id, data)

        # Set countdown
        tanggal_sp2d = data.get('tanggal_sp2d_tup')
        if tanggal_sp2d:
            self.countdown_widget.set_tanggal_sp2d(tanggal_sp2d)
        else:
            self.countdown_widget.reset()
