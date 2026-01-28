"""
PPK DOCUMENT FACTORY - LS List Page
====================================
List page for Pembayaran Langsung (LS) transactions.
"""

from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from .base_list_page import BaseListPage, format_rupiah


class LSListPage(BaseListPage):
    """List page for LS transactions."""

    MEKANISME = "LS"
    TITLE = "Pembayaran Langsung (LS)"
    COLOR = "#3498db"

    def _get_icon(self) -> str:
        return "S"  # Send icon placeholder

    def _get_columns(self):
        """Override columns to include penyedia."""
        return ["No", "Kode", "Nama Kegiatan", "Penyedia", "Nilai Kontrak", "Fase", "Status"]

    def _set_row_data(self, row: int, item: dict):
        """Override to add penyedia column."""
        # No
        no_item = QTableWidgetItem(str(row + 1))
        no_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, no_item)

        # Kode
        kode_item = QTableWidgetItem(item.get('kode_transaksi', '-'))
        self.table.setItem(row, 1, kode_item)

        # Nama
        nama_item = QTableWidgetItem(item.get('nama_kegiatan', '-'))
        self.table.setItem(row, 2, nama_item)

        # Penyedia
        penyedia = item.get('penyedia_nama', '-')
        penyedia_item = QTableWidgetItem(penyedia)
        self.table.setItem(row, 3, penyedia_item)

        # Nilai Kontrak
        nilai = item.get('nilai_kontrak', 0) or item.get('estimasi_biaya', 0)
        nilai_item = QTableWidgetItem(format_rupiah(nilai))
        nilai_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 4, nilai_item)

        # Fase
        fase = item.get('fase_aktif', 1)
        fase_item = QTableWidgetItem(f"Fase {fase}")
        fase_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 5, fase_item)

        # Status
        status = item.get('status', 'draft')
        status_item = QTableWidgetItem(status.title())
        status_item.setTextAlignment(Qt.AlignCenter)
        color = self.STATUS_COLORS.get(status, "#bdc3c7")
        status_item.setForeground(QColor(color))
        self.table.setItem(row, 6, status_item)
