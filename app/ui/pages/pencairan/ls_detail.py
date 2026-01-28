"""
PPK DOCUMENT FACTORY - LS Detail Page
======================================
Detail page for Pembayaran Langsung (LS) transactions.
Includes penyedia/kontrak information.
"""

from PySide6.QtWidgets import QVBoxLayout, QFrame, QLabel, QHBoxLayout

from .base_detail_page import BaseDetailPage

from typing import Dict, Any


class LSDetailPage(BaseDetailPage):
    """Detail page for LS transactions with contract info."""

    MEKANISME = "LS"
    COLOR = "#3498db"

    def _create_info_tab(self):
        """Override to add contract/penyedia info."""
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)

        # Penyedia info
        penyedia_frame = QFrame()
        penyedia_frame.setStyleSheet("""
            QFrame {
                background-color: #ebf5fb;
                border-radius: 5px;
                padding: 10px;
                border-left: 4px solid #3498db;
            }
        """)

        penyedia_layout = QVBoxLayout(penyedia_frame)
        penyedia_layout.setSpacing(8)

        penyedia_title = QLabel("Penyedia Barang/Jasa")
        penyedia_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #2c3e50;")
        penyedia_layout.addWidget(penyedia_title)

        self.penyedia_nama_label = QLabel("Nama: -")
        self.penyedia_nama_label.setStyleSheet("font-size: 12px; color: #2c3e50;")
        penyedia_layout.addWidget(self.penyedia_nama_label)

        self.penyedia_npwp_label = QLabel("NPWP: -")
        self.penyedia_npwp_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        penyedia_layout.addWidget(self.penyedia_npwp_label)

        self.penyedia_bank_label = QLabel("Rekening: -")
        self.penyedia_bank_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        penyedia_layout.addWidget(self.penyedia_bank_label)

        layout.addWidget(penyedia_frame)

        # Kontrak info
        kontrak_frame = QFrame()
        kontrak_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        kontrak_layout = QVBoxLayout(kontrak_frame)
        kontrak_layout.setSpacing(8)

        kontrak_title = QLabel("Informasi Kontrak/SPK")
        kontrak_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #2c3e50;")
        kontrak_layout.addWidget(kontrak_title)

        self.kontrak_nomor_label = QLabel("Nomor: -")
        self.kontrak_nomor_label.setStyleSheet("font-size: 12px; color: #2c3e50;")
        kontrak_layout.addWidget(self.kontrak_nomor_label)

        self.kontrak_tanggal_label = QLabel("Tanggal: -")
        self.kontrak_tanggal_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        kontrak_layout.addWidget(self.kontrak_tanggal_label)

        self.kontrak_nilai_label = QLabel("Nilai: -")
        self.kontrak_nilai_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #3498db;")
        kontrak_layout.addWidget(self.kontrak_nilai_label)

        layout.addWidget(kontrak_frame)

        layout.addStretch()

        return widget

    def set_transaksi(self, transaksi_id: int, data: Dict[str, Any]):
        """Override to set penyedia/kontrak info."""
        super().set_transaksi(transaksi_id, data)

        # Penyedia info
        self.penyedia_nama_label.setText(f"Nama: {data.get('penyedia_nama', '-')}")
        self.penyedia_npwp_label.setText(f"NPWP: {data.get('penyedia_npwp', '-')}")

        # Kontrak info
        self.kontrak_nomor_label.setText(f"Nomor: {data.get('nomor_kontrak', '-')}")
        self.kontrak_tanggal_label.setText(f"Tanggal: {data.get('tanggal_kontrak', '-')}")

        nilai_kontrak = data.get('nilai_kontrak', 0)
        if nilai_kontrak:
            from .base_list_page import format_rupiah
            self.kontrak_nilai_label.setText(f"Nilai: {format_rupiah(nilai_kontrak)}")
        else:
            self.kontrak_nilai_label.setText("Nilai: -")
