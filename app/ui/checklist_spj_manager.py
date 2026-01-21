"""
PPK DOCUMENT FACTORY - Checklist SPJ Manager
=============================================
Fitur:
1. Checklist kelengkapan dokumen berdasarkan nilai paket
2. Upload dokumen yang sudah ditandatangani/cap
3. Tracking status dokumen (draft, signed, archived)
4. Export checklist ke PDF
"""

import os
import shutil
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QComboBox, QFileDialog,
    QMessageBox, QProgressBar, QFrame, QScrollArea,
    QCheckBox, QTextEdit, QDialog, QDialogButtonBox,
    QTabWidget, QSplitter, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QIcon

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db_manager


# =============================================================================
# KONFIGURASI CHECKLIST BERDASARKAN NILAI
# =============================================================================

CHECKLIST_CONFIG = {
    'LS_MIKRO': {
        'label': 'Pembelian Langsung (≤ 10 Juta)',
        'max_nilai': 10_000_000,
        'dokumen': [
            # (kode, nama, kategori, wajib)
            ('SPESIFIKASI_SEDERHANA', 'Spesifikasi Teknis Sederhana', 'PERSIAPAN', False),
            ('NOTA_FAKTUR', 'Nota/Faktur Pembelian', 'TRANSAKSI', True),
            ('KUITANSI', 'Kuitansi Bermeterai', 'PEMBAYARAN', True),
            ('SSP_PPH', 'SSP PPh', 'PAJAK', True),
            ('BUKTI_TRANSFER', 'Bukti Transfer/Pembayaran', 'PEMBAYARAN', False),
            ('FOTO_BARANG', 'Foto Dokumentasi Barang', 'DOKUMENTASI', False),
        ]
    },
    'LS_KECIL': {
        'label': 'Pengadaan Langsung Kecil (10-50 Juta)',
        'max_nilai': 50_000_000,
        'dokumen': [
            # PERSIAPAN
            ('SPESIFIKASI', 'Spesifikasi Teknis', 'PERSIAPAN', True),
            ('SURVEY_HARGA', 'Survey Harga (3 Sumber)', 'PERSIAPAN', True),
            ('HPS', 'HPS (Harga Perkiraan Sendiri)', 'PERSIAPAN', True),
            ('RANCANGAN_SPK', 'Rancangan SPK', 'PERSIAPAN', True),
            # PEMILIHAN
            ('SURAT_PENAWARAN', 'Surat Penawaran Harga', 'PEMILIHAN', True),
            ('DAFTAR_HARGA', 'Daftar Kuantitas dan Harga', 'PEMILIHAN', True),
            # KONTRAK
            ('SPK', 'Surat Perintah Kerja (SPK)', 'KONTRAK', True),
            ('SPMK', 'Surat Perintah Mulai Kerja', 'KONTRAK', True),
            # SERAH TERIMA
            ('BAHP', 'Berita Acara Hasil Pemeriksaan', 'SERAH_TERIMA', True),
            ('BAST', 'Berita Acara Serah Terima', 'SERAH_TERIMA', True),
            ('DAFTAR_BARANG', 'Daftar Barang yang Diserahkan', 'SERAH_TERIMA', True),
            # PEMBAYARAN
            ('KUITANSI', 'Kuitansi Bermeterai', 'PEMBAYARAN', True),
            ('FAKTUR_PAJAK', 'Faktur Pajak (jika PKP)', 'PEMBAYARAN', False),
            ('SSP_PPN', 'SSP PPN (jika PKP)', 'PAJAK', False),
            ('SSP_PPH', 'SSP PPh', 'PAJAK', True),
            ('SPP_LS', 'SPP-LS', 'PEMBAYARAN', True),
            ('DRPP', 'DRPP', 'PEMBAYARAN', True),
        ]
    },
    'LS_STANDAR': {
        'label': 'Pengadaan Langsung Standar (50-200 Juta)',
        'max_nilai': 200_000_000,
        'dokumen': [
            # PERSIAPAN
            ('SPESIFIKASI', 'Spesifikasi Teknis', 'PERSIAPAN', True),
            ('SURVEY_HARGA', 'Survey Harga (3 Sumber)', 'PERSIAPAN', True),
            ('BA_SURVEY', 'BA Survey Harga', 'PERSIAPAN', True),
            ('HPS', 'HPS (Harga Perkiraan Sendiri)', 'PERSIAPAN', True),
            ('KAK', 'Kerangka Acuan Kerja', 'PERSIAPAN', True),
            ('RANCANGAN_KONTRAK', 'Rancangan Kontrak', 'PERSIAPAN', True),
            ('SSUK', 'SSUK (Syarat Umum Kontrak)', 'PERSIAPAN', True),
            ('SSKK', 'SSKK (Syarat Khusus Kontrak)', 'PERSIAPAN', True),
            ('NOTA_DINAS_PP', 'Nota Dinas ke PP', 'PERSIAPAN', True),
            # PEMILIHAN
            ('UNDANGAN_PL', 'Undangan Pengadaan Langsung', 'PEMILIHAN', True),
            ('SURAT_PENAWARAN', 'Surat Penawaran Harga', 'PEMILIHAN', True),
            ('DOK_KUALIFIKASI', 'Dokumen Kualifikasi Penyedia', 'PEMILIHAN', True),
            ('BA_EVALUASI', 'BA Evaluasi Penawaran', 'PEMILIHAN', True),
            ('BA_NEGOSIASI', 'BA Negosiasi Harga', 'PEMILIHAN', True),
            ('BAHPL', 'BA Hasil Pengadaan Langsung', 'PEMILIHAN', True),
            ('PENETAPAN_PENYEDIA', 'Surat Penetapan Penyedia', 'PEMILIHAN', True),
            # KONTRAK
            ('SPK', 'SPK + SSUK + SSKK', 'KONTRAK', True),
            ('SPMK', 'Surat Perintah Mulai Kerja', 'KONTRAK', True),
            # SERAH TERIMA
            ('SURAT_PERMOHONAN_PERIKSA', 'Surat Permohonan Pemeriksaan', 'SERAH_TERIMA', True),
            ('BAHP', 'Berita Acara Hasil Pemeriksaan', 'SERAH_TERIMA', True),
            ('BAST', 'Berita Acara Serah Terima', 'SERAH_TERIMA', True),
            ('DAFTAR_BARANG', 'Daftar Barang/Output', 'SERAH_TERIMA', True),
            ('FOTO_DOKUMENTASI', 'Foto Dokumentasi', 'SERAH_TERIMA', True),
            # PEMBAYARAN
            ('KUITANSI', 'Kuitansi Bermeterai', 'PEMBAYARAN', True),
            ('BAP', 'Berita Acara Pembayaran', 'PEMBAYARAN', True),
            ('FAKTUR_PAJAK', 'Faktur Pajak (jika PKP)', 'PEMBAYARAN', False),
            ('SSP_PPN', 'SSP PPN (jika PKP)', 'PAJAK', False),
            ('SSP_PPH', 'SSP PPh', 'PAJAK', True),
            ('SPP_LS', 'SPP-LS', 'PEMBAYARAN', True),
            ('DRPP', 'DRPP', 'PEMBAYARAN', True),
        ]
    },
    'KONTRAK': {
        'label': 'Surat Perjanjian (> 200 Juta)',
        'max_nilai': float('inf'),
        'dokumen': [
            # PERSIAPAN
            ('SPESIFIKASI', 'Spesifikasi Teknis', 'PERSIAPAN', True),
            ('SURVEY_HARGA', 'Survey Harga (3 Sumber)', 'PERSIAPAN', True),
            ('BA_SURVEY', 'BA Survey Harga', 'PERSIAPAN', True),
            ('HPS', 'HPS (Harga Perkiraan Sendiri)', 'PERSIAPAN', True),
            ('KAK', 'Kerangka Acuan Kerja', 'PERSIAPAN', True),
            ('RANCANGAN_KONTRAK', 'Rancangan Surat Perjanjian', 'PERSIAPAN', True),
            ('SSUK', 'SSUK (Syarat Umum Kontrak)', 'PERSIAPAN', True),
            ('SSKK', 'SSKK (Syarat Khusus Kontrak)', 'PERSIAPAN', True),
            ('NOTA_DINAS_PP', 'Nota Dinas ke PP', 'PERSIAPAN', True),
            # PEMILIHAN
            ('UNDANGAN_PL', 'Undangan Pengadaan Langsung', 'PEMILIHAN', True),
            ('SURAT_PENAWARAN', 'Surat Penawaran Harga', 'PEMILIHAN', True),
            ('DOK_KUALIFIKASI', 'Dokumen Kualifikasi Penyedia Lengkap', 'PEMILIHAN', True),
            ('BA_EVALUASI', 'BA Evaluasi Penawaran', 'PEMILIHAN', True),
            ('BA_NEGOSIASI', 'BA Negosiasi Harga', 'PEMILIHAN', True),
            ('BAHPL', 'BA Hasil Pengadaan Langsung', 'PEMILIHAN', True),
            ('PENETAPAN_PENYEDIA', 'Surat Penetapan Penyedia', 'PEMILIHAN', True),
            # KONTRAK
            ('SURAT_PERJANJIAN', 'Surat Perjanjian + SSUK + SSKK', 'KONTRAK', True),
            ('JAMINAN_PELAKSANAAN', 'Jaminan Pelaksanaan (5%)', 'KONTRAK', True),
            ('SPMK', 'Surat Perintah Mulai Kerja', 'KONTRAK', True),
            # PELAKSANAAN (untuk termin)
            ('LAPORAN_PROGRESS', 'Laporan Progress Pekerjaan', 'PELAKSANAAN', False),
            ('BA_PROGRESS', 'BA Pemeriksaan Progress', 'PELAKSANAAN', False),
            # SERAH TERIMA
            ('SURAT_PERMOHONAN_PERIKSA', 'Surat Permohonan Pemeriksaan', 'SERAH_TERIMA', True),
            ('BAHP', 'Berita Acara Hasil Pemeriksaan', 'SERAH_TERIMA', True),
            ('BAST', 'Berita Acara Serah Terima', 'SERAH_TERIMA', True),
            ('DAFTAR_BARANG', 'Daftar Barang/Output', 'SERAH_TERIMA', True),
            ('JAMINAN_PEMELIHARAAN', 'Jaminan Pemeliharaan', 'SERAH_TERIMA', False),
            ('FOTO_DOKUMENTASI', 'Foto Dokumentasi (0%, 50%, 100%)', 'SERAH_TERIMA', True),
            # PEMBAYARAN
            ('KUITANSI', 'Kuitansi Bermeterai', 'PEMBAYARAN', True),
            ('BAP', 'Berita Acara Pembayaran', 'PEMBAYARAN', True),
            ('INVOICE', 'Faktur/Invoice', 'PEMBAYARAN', True),
            ('FAKTUR_PAJAK', 'Faktur Pajak (jika PKP)', 'PEMBAYARAN', False),
            ('SSP_PPN', 'SSP PPN (jika PKP)', 'PAJAK', False),
            ('SSP_PPH', 'SSP PPh', 'PAJAK', True),
            ('SPP_LS', 'SPP-LS', 'PEMBAYARAN', True),
            ('DRPP', 'DRPP', 'PEMBAYARAN', True),
        ]
    },
}

KATEGORI_LABELS = {
    'PERSIAPAN': ('Persiapan', '#3498db'),
    'PEMILIHAN': ('Pemilihan', '#9b59b6'),
    'KONTRAK': ('Kontrak', '#e67e22'),
    'PELAKSANAAN': ('Pelaksanaan', '#1abc9c'),
    'SERAH_TERIMA': ('Serah Terima', '#27ae60'),
    'PEMBAYARAN': ('Pembayaran', '#2ecc71'),
    'PAJAK': ('Perpajakan', '#e74c3c'),
    'DOKUMENTASI': ('Dokumentasi', '#95a5a6'),
}

STATUS_DOKUMEN = {
    'BELUM': ('Belum Ada', '🔲', '#bdc3c7'),
    'DRAFT': ('Draft', '📝', '#f39c12'),
    'SIGNED': ('Sudah TTD', '✅', '#27ae60'),
    'UPLOADED': ('Terupload', '📤', '#3498db'),
    'ARCHIVED': ('Diarsipkan', '📁', '#95a5a6'),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_alur_by_nilai(nilai: float) -> str:
    """Tentukan alur pengadaan berdasarkan nilai"""
    if nilai <= 10_000_000:
        return 'LS_MIKRO'
    elif nilai <= 50_000_000:
        return 'LS_KECIL'
    elif nilai <= 200_000_000:
        return 'LS_STANDAR'
    else:
        return 'KONTRAK'


def get_checklist_for_paket(nilai: float) -> List[Tuple]:
    """Ambil daftar checklist berdasarkan nilai paket"""
    alur = get_alur_by_nilai(nilai)
    config = CHECKLIST_CONFIG.get(alur, CHECKLIST_CONFIG['LS_STANDAR'])
    return config['dokumen']


# =============================================================================
# CHECKLIST SPJ MANAGER WIDGET
# =============================================================================

class ChecklistSPJManager(QWidget):
    """Manager untuk checklist kelengkapan dokumen SPJ"""

    document_uploaded = Signal(int, str, str)  # paket_id, doc_type, filepath

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db_manager()
        self.current_paket_id = None
        self.current_paket = None
        self.checklist_items = {}

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header
        header = self.create_header()
        layout.addWidget(header)

        # Splitter untuk checklist dan detail
        splitter = QSplitter(Qt.Horizontal)

        # Panel Checklist
        checklist_panel = self.create_checklist_panel()
        splitter.addWidget(checklist_panel)

        # Panel Detail/Upload
        detail_panel = self.create_detail_panel()
        splitter.addWidget(detail_panel)

        splitter.setSizes([500, 400])
        layout.addWidget(splitter)

        # Footer dengan progress
        footer = self.create_footer()
        layout.addWidget(footer)

    def create_header(self) -> QWidget:
        """Buat header dengan info paket"""
        group = QGroupBox("Checklist Kelengkapan Dokumen SPJ")
        layout = QVBoxLayout(group)

        # Info paket
        info_layout = QHBoxLayout()

        self.lbl_paket_nama = QLabel("Pilih paket untuk melihat checklist")
        self.lbl_paket_nama.setFont(QFont("Segoe UI", 12, QFont.Bold))
        info_layout.addWidget(self.lbl_paket_nama)

        info_layout.addStretch()

        self.lbl_alur = QLabel("")
        self.lbl_alur.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                padding: 5px 15px;
                border-radius: 12px;
                font-weight: bold;
            }
        """)
        info_layout.addWidget(self.lbl_alur)

        self.lbl_nilai = QLabel("")
        self.lbl_nilai.setStyleSheet("color: #27ae60; font-weight: bold;")
        info_layout.addWidget(self.lbl_nilai)

        layout.addLayout(info_layout)

        # Filter kategori
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter Kategori:"))

        self.cmb_filter = QComboBox()
        self.cmb_filter.addItem("Semua Kategori", "ALL")
        for key, (label, color) in KATEGORI_LABELS.items():
            self.cmb_filter.addItem(f"{label}", key)
        self.cmb_filter.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.cmb_filter)

        filter_layout.addStretch()

        # Tombol aksi
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.clicked.connect(self.refresh_checklist)
        filter_layout.addWidget(self.btn_refresh)

        self.btn_export = QPushButton("📄 Export PDF")
        self.btn_export.clicked.connect(self.export_to_pdf)
        filter_layout.addWidget(self.btn_export)

        layout.addLayout(filter_layout)

        return group

    def create_checklist_panel(self) -> QWidget:
        """Buat panel checklist"""
        group = QGroupBox("Daftar Dokumen")
        layout = QVBoxLayout(group)

        # Tabel checklist
        self.tbl_checklist = QTableWidget()
        self.tbl_checklist.setColumnCount(5)
        self.tbl_checklist.setHorizontalHeaderLabels([
            "Status", "Dokumen", "Kategori", "Wajib", "File"
        ])

        header = self.tbl_checklist.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)

        self.tbl_checklist.setColumnWidth(0, 80)
        self.tbl_checklist.setColumnWidth(2, 100)
        self.tbl_checklist.setColumnWidth(3, 60)
        self.tbl_checklist.setColumnWidth(4, 80)

        self.tbl_checklist.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_checklist.setSelectionMode(QTableWidget.SingleSelection)
        self.tbl_checklist.itemSelectionChanged.connect(self.on_selection_changed)

        layout.addWidget(self.tbl_checklist)

        return group

    def create_detail_panel(self) -> QWidget:
        """Buat panel detail dan upload"""
        group = QGroupBox("Detail & Upload Dokumen")
        layout = QVBoxLayout(group)

        # Info dokumen terpilih
        self.lbl_doc_title = QLabel("Pilih dokumen dari daftar")
        self.lbl_doc_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(self.lbl_doc_title)

        self.lbl_doc_status = QLabel("")
        layout.addWidget(self.lbl_doc_status)

        # Frame upload
        upload_frame = QFrame()
        upload_frame.setFrameStyle(QFrame.StyledPanel)
        upload_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        upload_layout = QVBoxLayout(upload_frame)

        upload_label = QLabel("Upload Dokumen Bertandatangan")
        upload_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        upload_label.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(upload_label)

        upload_hint = QLabel("Format: PDF, JPG, PNG (maks. 10MB)")
        upload_hint.setStyleSheet("color: #6c757d;")
        upload_hint.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(upload_hint)

        btn_layout = QHBoxLayout()

        self.btn_upload = QPushButton("📤 Pilih File")
        self.btn_upload.setEnabled(False)
        self.btn_upload.clicked.connect(self.upload_document)
        btn_layout.addWidget(self.btn_upload)

        self.btn_scan = QPushButton("📷 Scan")
        self.btn_scan.setEnabled(False)
        self.btn_scan.setToolTip("Scan dokumen langsung (memerlukan scanner)")
        btn_layout.addWidget(self.btn_scan)

        upload_layout.addLayout(btn_layout)

        layout.addWidget(upload_frame)

        # File yang sudah diupload
        layout.addWidget(QLabel("File Terupload:"))

        self.lbl_uploaded_file = QLabel("Belum ada file")
        self.lbl_uploaded_file.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.lbl_uploaded_file)

        # Tombol aksi file
        file_btn_layout = QHBoxLayout()

        self.btn_view = QPushButton("👁 Lihat")
        self.btn_view.setEnabled(False)
        self.btn_view.clicked.connect(self.view_document)
        file_btn_layout.addWidget(self.btn_view)

        self.btn_replace = QPushButton("🔄 Ganti")
        self.btn_replace.setEnabled(False)
        self.btn_replace.clicked.connect(self.replace_document)
        file_btn_layout.addWidget(self.btn_replace)

        self.btn_delete = QPushButton("🗑 Hapus")
        self.btn_delete.setEnabled(False)
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.clicked.connect(self.delete_document)
        file_btn_layout.addWidget(self.btn_delete)

        layout.addLayout(file_btn_layout)

        # Catatan
        layout.addWidget(QLabel("Catatan:"))
        self.txt_catatan = QTextEdit()
        self.txt_catatan.setMaximumHeight(80)
        self.txt_catatan.setPlaceholderText("Tambahkan catatan untuk dokumen ini...")
        layout.addWidget(self.txt_catatan)

        self.btn_save_catatan = QPushButton("💾 Simpan Catatan")
        self.btn_save_catatan.clicked.connect(self.save_catatan)
        layout.addWidget(self.btn_save_catatan)

        layout.addStretch()

        return group

    def create_footer(self) -> QWidget:
        """Buat footer dengan progress"""
        group = QGroupBox("Progress Kelengkapan")
        layout = QVBoxLayout(group)

        # Progress bar
        progress_layout = QHBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v% Lengkap")
        progress_layout.addWidget(self.progress_bar)

        layout.addLayout(progress_layout)

        # Summary
        summary_layout = QHBoxLayout()

        self.lbl_wajib = QLabel("Wajib: 0/0")
        self.lbl_wajib.setStyleSheet("color: #e74c3c; font-weight: bold;")
        summary_layout.addWidget(self.lbl_wajib)

        self.lbl_opsional = QLabel("Opsional: 0/0")
        self.lbl_opsional.setStyleSheet("color: #3498db;")
        summary_layout.addWidget(self.lbl_opsional)

        self.lbl_uploaded = QLabel("Terupload: 0")
        self.lbl_uploaded.setStyleSheet("color: #27ae60;")
        summary_layout.addWidget(self.lbl_uploaded)

        summary_layout.addStretch()

        # Status SPJ
        self.lbl_status_spj = QLabel("Status SPJ: Belum Lengkap")
        self.lbl_status_spj.setStyleSheet("""
            QLabel {
                background-color: #f39c12;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        summary_layout.addWidget(self.lbl_status_spj)

        layout.addLayout(summary_layout)

        return group

    def load_paket(self, paket_id: int):
        """Load data paket dan checklist"""
        self.current_paket_id = paket_id

        # Ambil data paket
        paket = self.db.get_paket(paket_id)
        if not paket:
            QMessageBox.warning(self, "Error", "Paket tidak ditemukan!")
            return

        self.current_paket = paket

        # Update header
        self.lbl_paket_nama.setText(paket.get('nama', 'Tanpa Nama'))

        nilai = paket.get('nilai_pagu', 0) or 0
        alur = get_alur_by_nilai(nilai)
        config = CHECKLIST_CONFIG.get(alur, CHECKLIST_CONFIG['LS_STANDAR'])

        self.lbl_alur.setText(config['label'])
        self.lbl_nilai.setText(f"Rp {nilai:,.0f}".replace(',', '.'))

        # Load checklist
        self.load_checklist(alur)

    def load_checklist(self, alur: str):
        """Load daftar checklist ke tabel"""
        config = CHECKLIST_CONFIG.get(alur, CHECKLIST_CONFIG['LS_STANDAR'])
        dokumen_list = config['dokumen']

        self.tbl_checklist.setRowCount(len(dokumen_list))
        self.checklist_items = {}

        # Ambil status dokumen dari database
        uploaded_docs = self.get_uploaded_documents()

        for row, (kode, nama, kategori, wajib) in enumerate(dokumen_list):
            # Status
            doc_info = uploaded_docs.get(kode, {})
            status = doc_info.get('status', 'BELUM')
            status_label, status_icon, status_color = STATUS_DOKUMEN.get(status, STATUS_DOKUMEN['BELUM'])

            status_item = QTableWidgetItem(status_icon)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setToolTip(status_label)
            self.tbl_checklist.setItem(row, 0, status_item)

            # Nama dokumen
            nama_item = QTableWidgetItem(nama)
            nama_item.setData(Qt.UserRole, kode)
            self.tbl_checklist.setItem(row, 1, nama_item)

            # Kategori
            kat_label, kat_color = KATEGORI_LABELS.get(kategori, ('Lainnya', '#95a5a6'))
            kat_item = QTableWidgetItem(kat_label)
            kat_item.setBackground(QColor(kat_color))
            kat_item.setForeground(QColor('white'))
            kat_item.setTextAlignment(Qt.AlignCenter)
            self.tbl_checklist.setItem(row, 2, kat_item)

            # Wajib
            wajib_item = QTableWidgetItem("Ya" if wajib else "Tidak")
            wajib_item.setTextAlignment(Qt.AlignCenter)
            if wajib:
                wajib_item.setForeground(QColor('#e74c3c'))
                wajib_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.tbl_checklist.setItem(row, 3, wajib_item)

            # File
            has_file = bool(doc_info.get('filepath'))
            file_item = QTableWidgetItem("📄" if has_file else "-")
            file_item.setTextAlignment(Qt.AlignCenter)
            self.tbl_checklist.setItem(row, 4, file_item)

            # Simpan info
            self.checklist_items[kode] = {
                'nama': nama,
                'kategori': kategori,
                'wajib': wajib,
                'status': status,
                'filepath': doc_info.get('filepath'),
                'catatan': doc_info.get('catatan'),
            }

        self.update_progress()

    def get_uploaded_documents(self) -> Dict:
        """Ambil daftar dokumen yang sudah diupload dari database"""
        if not self.current_paket_id:
            return {}

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT doc_type, status, filepath_signed, catatan
                FROM checklist_spj
                WHERE paket_id = ?
            """, (self.current_paket_id,))

            result = {}
            for row in cursor.fetchall():
                result[row[0]] = {
                    'status': row[1],
                    'filepath': row[2],
                    'catatan': row[3],
                }

            return result
        except Exception as e:
            # Tabel mungkin belum ada
            return {}

    def update_progress(self):
        """Update progress bar dan summary"""
        if not self.checklist_items:
            return

        total_wajib = 0
        done_wajib = 0
        total_opsional = 0
        done_opsional = 0
        total_uploaded = 0

        for kode, info in self.checklist_items.items():
            is_done = info['status'] in ('SIGNED', 'UPLOADED', 'ARCHIVED')
            has_file = bool(info.get('filepath'))

            if info['wajib']:
                total_wajib += 1
                if is_done:
                    done_wajib += 1
            else:
                total_opsional += 1
                if is_done:
                    done_opsional += 1

            if has_file:
                total_uploaded += 1

        # Update labels
        self.lbl_wajib.setText(f"Wajib: {done_wajib}/{total_wajib}")
        self.lbl_opsional.setText(f"Opsional: {done_opsional}/{total_opsional}")
        self.lbl_uploaded.setText(f"Terupload: {total_uploaded}")

        # Update progress bar (hanya hitung yang wajib)
        if total_wajib > 0:
            progress = int((done_wajib / total_wajib) * 100)
            self.progress_bar.setValue(progress)

            # Update status SPJ
            if progress == 100:
                self.lbl_status_spj.setText("Status SPJ: LENGKAP ✅")
                self.lbl_status_spj.setStyleSheet("""
                    QLabel {
                        background-color: #27ae60;
                        color: white;
                        padding: 5px 15px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                """)
            elif progress >= 80:
                self.lbl_status_spj.setText(f"Status SPJ: Hampir Lengkap ({progress}%)")
                self.lbl_status_spj.setStyleSheet("""
                    QLabel {
                        background-color: #3498db;
                        color: white;
                        padding: 5px 15px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                """)
            else:
                self.lbl_status_spj.setText(f"Status SPJ: Belum Lengkap ({progress}%)")
                self.lbl_status_spj.setStyleSheet("""
                    QLabel {
                        background-color: #f39c12;
                        color: white;
                        padding: 5px 15px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                """)

    def on_selection_changed(self):
        """Handle selection change di tabel"""
        selected = self.tbl_checklist.selectedItems()
        if not selected:
            self.btn_upload.setEnabled(False)
            return

        row = selected[0].row()
        nama_item = self.tbl_checklist.item(row, 1)
        kode = nama_item.data(Qt.UserRole)

        info = self.checklist_items.get(kode, {})

        # Update detail panel
        self.lbl_doc_title.setText(info.get('nama', kode))

        status = info.get('status', 'BELUM')
        status_label, status_icon, _ = STATUS_DOKUMEN.get(status, STATUS_DOKUMEN['BELUM'])
        self.lbl_doc_status.setText(f"Status: {status_icon} {status_label}")

        # Enable upload button
        self.btn_upload.setEnabled(True)

        # Update file info
        filepath = info.get('filepath')
        if filepath and os.path.exists(filepath):
            filename = os.path.basename(filepath)
            self.lbl_uploaded_file.setText(f"📄 {filename}")
            self.btn_view.setEnabled(True)
            self.btn_replace.setEnabled(True)
            self.btn_delete.setEnabled(True)
        else:
            self.lbl_uploaded_file.setText("Belum ada file")
            self.btn_view.setEnabled(False)
            self.btn_replace.setEnabled(False)
            self.btn_delete.setEnabled(False)

        # Load catatan
        self.txt_catatan.setText(info.get('catatan', ''))

    def apply_filter(self):
        """Apply filter kategori"""
        filter_value = self.cmb_filter.currentData()

        for row in range(self.tbl_checklist.rowCount()):
            kat_item = self.tbl_checklist.item(row, 2)
            nama_item = self.tbl_checklist.item(row, 1)
            kode = nama_item.data(Qt.UserRole)
            info = self.checklist_items.get(kode, {})

            if filter_value == "ALL":
                self.tbl_checklist.setRowHidden(row, False)
            else:
                self.tbl_checklist.setRowHidden(row, info.get('kategori') != filter_value)

    def upload_document(self):
        """Upload dokumen bertandatangan"""
        selected = self.tbl_checklist.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        nama_item = self.tbl_checklist.item(row, 1)
        kode = nama_item.data(Qt.UserRole)
        info = self.checklist_items.get(kode, {})

        # Dialog pilih file
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            f"Upload Dokumen: {info.get('nama', kode)}",
            "",
            "Documents (*.pdf *.jpg *.jpeg *.png);;PDF Files (*.pdf);;Images (*.jpg *.jpeg *.png);;All Files (*)"
        )

        if not filepath:
            return

        # Validasi ukuran file (maks 10MB)
        file_size = os.path.getsize(filepath)
        if file_size > 10 * 1024 * 1024:
            QMessageBox.warning(self, "Error", "Ukuran file maksimal 10MB!")
            return

        # Copy file ke folder output
        try:
            dest_folder = self.get_upload_folder()
            os.makedirs(dest_folder, exist_ok=True)

            # Generate nama file unik
            ext = os.path.splitext(filepath)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{kode}_{timestamp}{ext}"
            dest_path = os.path.join(dest_folder, new_filename)

            shutil.copy2(filepath, dest_path)

            # Simpan ke database
            self.save_document_status(kode, 'UPLOADED', dest_path)

            # Update UI
            self.checklist_items[kode]['status'] = 'UPLOADED'
            self.checklist_items[kode]['filepath'] = dest_path

            # Refresh
            self.refresh_checklist()

            QMessageBox.information(self, "Sukses", f"Dokumen berhasil diupload!\n{new_filename}")

            # Emit signal
            self.document_uploaded.emit(self.current_paket_id, kode, dest_path)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal upload dokumen:\n{str(e)}")

    def get_upload_folder(self) -> str:
        """Dapatkan folder upload untuk paket ini"""
        from app.core.config import OUTPUT_DIR, TAHUN_ANGGARAN

        paket_kode = self.current_paket.get('kode', 'unknown')
        paket_nama = self.current_paket.get('nama', 'unknown')[:30]

        # Bersihkan nama folder
        folder_name = f"{paket_kode}_{paket_nama}".replace(' ', '_')
        folder_name = "".join(c for c in folder_name if c.isalnum() or c in ('_', '-'))

        return os.path.join(OUTPUT_DIR, str(TAHUN_ANGGARAN), folder_name, "signed_documents")

    def save_document_status(self, doc_type: str, status: str, filepath: str = None, catatan: str = None):
        """Simpan status dokumen ke database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Cek apakah sudah ada
            cursor.execute("""
                SELECT id FROM checklist_spj WHERE paket_id = ? AND doc_type = ?
            """, (self.current_paket_id, doc_type))

            existing = cursor.fetchone()

            if existing:
                cursor.execute("""
                    UPDATE checklist_spj
                    SET status = ?, filepath_signed = ?, catatan = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE paket_id = ? AND doc_type = ?
                """, (status, filepath, catatan, self.current_paket_id, doc_type))
            else:
                cursor.execute("""
                    INSERT INTO checklist_spj (paket_id, doc_type, status, filepath_signed, catatan)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.current_paket_id, doc_type, status, filepath, catatan))

            conn.commit()

        except Exception as e:
            print(f"Error saving document status: {e}")
            # Mungkin tabel belum ada, buat dulu
            self.create_checklist_table()
            # Coba lagi
            self.save_document_status(doc_type, status, filepath, catatan)

    def create_checklist_table(self):
        """Buat tabel checklist_spj jika belum ada"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checklist_spj (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paket_id INTEGER NOT NULL,
                    doc_type TEXT NOT NULL,
                    status TEXT DEFAULT 'BELUM',
                    filepath_signed TEXT,
                    catatan TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
                    UNIQUE(paket_id, doc_type)
                )
            """)

            conn.commit()

        except Exception as e:
            print(f"Error creating table: {e}")

    def view_document(self):
        """Buka dokumen untuk dilihat"""
        selected = self.tbl_checklist.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        nama_item = self.tbl_checklist.item(row, 1)
        kode = nama_item.data(Qt.UserRole)
        info = self.checklist_items.get(kode, {})

        filepath = info.get('filepath')
        if filepath and os.path.exists(filepath):
            import subprocess
            import platform

            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', filepath])
            else:
                subprocess.run(['xdg-open', filepath])

    def replace_document(self):
        """Ganti dokumen yang sudah diupload"""
        reply = QMessageBox.question(
            self, "Konfirmasi",
            "Dokumen lama akan diganti. Lanjutkan?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.upload_document()

    def delete_document(self):
        """Hapus dokumen yang diupload"""
        selected = self.tbl_checklist.selectedItems()
        if not selected:
            return

        reply = QMessageBox.question(
            self, "Konfirmasi",
            "Hapus dokumen ini?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        row = selected[0].row()
        nama_item = self.tbl_checklist.item(row, 1)
        kode = nama_item.data(Qt.UserRole)
        info = self.checklist_items.get(kode, {})

        # Hapus file
        filepath = info.get('filepath')
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass

        # Update database
        self.save_document_status(kode, 'BELUM', None)

        # Refresh
        self.refresh_checklist()

    def save_catatan(self):
        """Simpan catatan dokumen"""
        selected = self.tbl_checklist.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        nama_item = self.tbl_checklist.item(row, 1)
        kode = nama_item.data(Qt.UserRole)
        info = self.checklist_items.get(kode, {})

        catatan = self.txt_catatan.toPlainText()

        self.save_document_status(
            kode,
            info.get('status', 'BELUM'),
            info.get('filepath'),
            catatan
        )

        self.checklist_items[kode]['catatan'] = catatan

        QMessageBox.information(self, "Sukses", "Catatan berhasil disimpan!")

    def refresh_checklist(self):
        """Refresh checklist dari database"""
        if self.current_paket_id:
            nilai = self.current_paket.get('nilai_pagu', 0) or 0
            alur = get_alur_by_nilai(nilai)
            self.load_checklist(alur)

    def export_to_pdf(self):
        """Export checklist ke PDF"""
        if not self.current_paket_id:
            QMessageBox.warning(self, "Peringatan", "Pilih paket terlebih dahulu!")
            return

        # Pilih lokasi simpan
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Checklist ke PDF",
            f"Checklist_SPJ_{self.current_paket.get('kode', 'unknown')}.pdf",
            "PDF Files (*.pdf)"
        )

        if not filepath:
            return

        try:
            self.generate_pdf_checklist(filepath)
            QMessageBox.information(self, "Sukses", f"Checklist berhasil diekspor ke:\n{filepath}")

            # Buka file
            import subprocess
            import platform

            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', filepath])
            else:
                subprocess.run(['xdg-open', filepath])

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export PDF:\n{str(e)}")

    def generate_pdf_checklist(self, filepath: str):
        """Generate PDF checklist (simplified - menggunakan reportlab jika tersedia)"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet

            doc = SimpleDocTemplate(filepath, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Title
            elements.append(Paragraph(f"CHECKLIST KELENGKAPAN DOKUMEN SPJ", styles['Title']))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Paket: {self.current_paket.get('nama', '-')}", styles['Normal']))
            elements.append(Paragraph(f"Kode: {self.current_paket.get('kode', '-')}", styles['Normal']))
            elements.append(Paragraph(f"Nilai: Rp {self.current_paket.get('nilai_pagu', 0):,.0f}".replace(',', '.'), styles['Normal']))
            elements.append(Spacer(1, 24))

            # Table data
            data = [['No', 'Dokumen', 'Kategori', 'Wajib', 'Status']]

            for i, (kode, info) in enumerate(self.checklist_items.items(), 1):
                status_label, status_icon, _ = STATUS_DOKUMEN.get(info['status'], STATUS_DOKUMEN['BELUM'])
                data.append([
                    str(i),
                    info['nama'],
                    KATEGORI_LABELS.get(info['kategori'], ('', ''))[0],
                    'Ya' if info['wajib'] else 'Tidak',
                    status_label
                ])

            table = Table(data, colWidths=[30, 250, 80, 50, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(table)

            doc.build(elements)

        except ImportError:
            # Fallback: Generate simple text file
            with open(filepath.replace('.pdf', '.txt'), 'w') as f:
                f.write(f"CHECKLIST KELENGKAPAN DOKUMEN SPJ\n")
                f.write(f"=" * 50 + "\n\n")
                f.write(f"Paket: {self.current_paket.get('nama', '-')}\n")
                f.write(f"Kode: {self.current_paket.get('kode', '-')}\n")
                f.write(f"Nilai: Rp {self.current_paket.get('nilai_pagu', 0):,.0f}\n\n")
                f.write(f"-" * 50 + "\n")

                for i, (kode, info) in enumerate(self.checklist_items.items(), 1):
                    status_label, _, _ = STATUS_DOKUMEN.get(info['status'], STATUS_DOKUMEN['BELUM'])
                    wajib = "WAJIB" if info['wajib'] else "Opsional"
                    f.write(f"{i}. [{status_label}] {info['nama']} ({wajib})\n")

            raise Exception("reportlab tidak tersedia. File disimpan sebagai TXT.")


# =============================================================================
# DIALOG UNTUK STANDALONE
# =============================================================================

class ChecklistDialog(QDialog):
    """Dialog untuk menampilkan checklist"""

    def __init__(self, paket_id: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Checklist Kelengkapan Dokumen SPJ")
        self.setMinimumSize(1000, 700)

        layout = QVBoxLayout(self)

        self.manager = ChecklistSPJManager()
        self.manager.load_paket(paket_id)
        layout.addWidget(self.manager)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)


# =============================================================================
# TEST
# =============================================================================

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Test dialog
    dialog = ChecklistDialog(1)
    dialog.show()

    sys.exit(app.exec())
