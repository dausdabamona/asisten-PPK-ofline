"""
PPK DOCUMENT FACTORY - TUP List Page
=====================================
List page for Tambahan Uang Persediaan (TUP) transactions.
"""

from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from .base_list_page import BaseListPage, format_rupiah
from datetime import date


class TUPListPage(BaseListPage):
    """List page for TUP transactions."""

    MEKANISME = "TUP"
    TITLE = "Tambahan UP (TUP)"
    COLOR = "#f39c12"

    def _get_icon(self) -> str:
        return "+"  # Plus icon placeholder

    def _get_columns(self):
        """Override columns to include countdown."""
        return ["No", "Kode", "Nama Kegiatan", "Nilai", "Fase", "Sisa Hari", "Status"]

    def _set_row_data(self, row: int, item: dict):
        """Override to add countdown column."""
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

        # Nilai
        nilai = item.get('estimasi_biaya', 0)
        nilai_item = QTableWidgetItem(format_rupiah(nilai))
        nilai_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 3, nilai_item)

        # Fase
        fase = item.get('fase_aktif', 1)
        fase_item = QTableWidgetItem(f"Fase {fase}")
        fase_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 4, fase_item)

        # Sisa Hari (countdown)
        sisa_item = self._get_countdown_item(item)
        self.table.setItem(row, 5, sisa_item)

        # Status
        status = item.get('status', 'draft')
        status_item = QTableWidgetItem(status.title())
        status_item.setTextAlignment(Qt.AlignCenter)
        color = self.STATUS_COLORS.get(status, "#bdc3c7")
        status_item.setForeground(QColor(color))
        self.table.setItem(row, 6, status_item)

    def _get_countdown_item(self, item: dict) -> QTableWidgetItem:
        """Create countdown table item."""
        tanggal_sp2d = item.get('tanggal_sp2d_tup')

        if not tanggal_sp2d:
            countdown_item = QTableWidgetItem("-")
            countdown_item.setTextAlignment(Qt.AlignCenter)
            countdown_item.setForeground(QColor("#bdc3c7"))
            return countdown_item

        # Calculate remaining days
        from datetime import datetime, timedelta

        if isinstance(tanggal_sp2d, str):
            tanggal_sp2d = datetime.strptime(tanggal_sp2d, '%Y-%m-%d').date()

        batas = tanggal_sp2d + timedelta(days=30)
        today = date.today()
        sisa = (batas - today).days

        countdown_item = QTableWidgetItem(f"{sisa} hari")
        countdown_item.setTextAlignment(Qt.AlignCenter)

        # Color based on remaining days
        if sisa < 0:
            countdown_item.setText(f"Terlambat!")
            countdown_item.setForeground(QColor("#c0392b"))
        elif sisa <= 5:
            countdown_item.setForeground(QColor("#e74c3c"))
        elif sisa <= 10:
            countdown_item.setForeground(QColor("#f39c12"))
        else:
            countdown_item.setForeground(QColor("#27ae60"))

        return countdown_item
