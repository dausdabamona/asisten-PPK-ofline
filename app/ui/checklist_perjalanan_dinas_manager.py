"""
PPK DOCUMENT FACTORY - Checklist Perjalanan Dinas Manager
==========================================================
Fitur:
1. Checklist kelengkapan dokumen perjalanan dinas
2. Upload dokumen yang sudah ditandatangani
3. Tracking status dokumen per fase (Persiapan, Pelaksanaan, Pertanggungjawaban)
4. Kondisional dokumen berdasarkan data perjalanan
5. Export checklist ke PDF
"""

import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QComboBox, QFileDialog,
    QMessageBox, QProgressBar, QFrame, QScrollArea,
    QTextEdit, QDialog, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database_v4 import get_db_manager_v4
from app.core.config import OUTPUT_DIR, TAHUN_ANGGARAN


# =============================================================================
# KONFIGURASI CHECKLIST PERJALANAN DINAS
# =============================================================================

# (kode, nama, kategori, wajib, kondisi_field)
# kondisi_field: None = selalu tampil, 'field_name > 0' = tampil jika kondisi terpenuhi

CHECKLIST_CONFIG_PD = {
    'PERSIAPAN': [
        ('SURAT_TUGAS', 'Surat Tugas', 'PERSIAPAN', True, None),
        ('SPPD', 'SPPD (Surat Perintah Perjalanan Dinas)', 'PERSIAPAN', True, None),
        ('KUITANSI_UM', 'Kuitansi Uang Muka', 'PERSIAPAN', False, 'uang_muka'),
    ],
    'PELAKSANAAN': [
        ('TIKET_TRANSPORT', 'Tiket Transportasi (PP)', 'PELAKSANAAN', False, 'biaya_transport'),
        ('BOARDING_PASS', 'Boarding Pass', 'PELAKSANAAN', False, 'biaya_transport'),
        ('BILL_HOTEL', 'Bill/Invoice Hotel', 'PELAKSANAAN', False, 'biaya_penginapan'),
        ('BUKTI_TRANSPORT_LOKAL', 'Bukti Transport Lokal', 'PELAKSANAAN', False, None),
    ],
    'PERTANGGUNGJAWABAN': [
        ('LAPORAN_PD', 'Laporan Perjalanan Dinas', 'PERTANGGUNGJAWABAN', True, None),
        ('DAFTAR_PENGELUARAN', 'Daftar Pengeluaran Riil', 'PERTANGGUNGJAWABAN', True, None),
        ('RINCIAN_BIAYA', 'Rincian Biaya Perjalanan', 'PERTANGGUNGJAWABAN', True, None),
        ('KUITANSI_RAMPUNG', 'Kuitansi Rampung', 'PERTANGGUNGJAWABAN', True, None),
        ('SPPD_LEGALISIR', 'SPPD yang Sudah Dilegalisir', 'PERTANGGUNGJAWABAN', True, None),
    ],
    'PENDUKUNG': [
        ('UNDANGAN', 'Undangan/Surat Panggilan', 'PENDUKUNG', False, None),
        ('DAFTAR_HADIR', 'Daftar Hadir Kegiatan', 'PENDUKUNG', False, None),
        ('SERTIFIKAT', 'Sertifikat/Materi Pelatihan', 'PENDUKUNG', False, None),
        ('FOTO_DOKUMENTASI', 'Foto Dokumentasi Kegiatan', 'PENDUKUNG', False, None),
    ],
}

KATEGORI_LABELS = {
    'PERSIAPAN': ('Persiapan', '#3498db'),
    'PELAKSANAAN': ('Pelaksanaan', '#9b59b6'),
    'PERTANGGUNGJAWABAN': ('Pertanggungjawaban', '#27ae60'),
    'PENDUKUNG': ('Pendukung', '#95a5a6'),
}

STATUS_DOKUMEN = {
    'BELUM': ('Belum Ada', '🔲', '#bdc3c7'),
    'DRAFT': ('Draft', '📝', '#f39c12'),
    'SIGNED': ('Sudah TTD', '✅', '#27ae60'),
    'UPLOADED': ('Terupload', '📤', '#3498db'),
    'VERIFIED': ('Terverifikasi', '✔️', '#2ecc71'),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_all_checklist_items() -> List[Tuple]:
    """Get flat list of all checklist items"""
    items = []
    for kategori, docs in CHECKLIST_CONFIG_PD.items():
        for doc in docs:
            items.append(doc)
    return items


def evaluate_condition(pd_data: Dict, kondisi_field: str) -> bool:
    """Evaluate if a conditional document should be shown"""
    if not kondisi_field:
        return True

    # Simple evaluation: check if field > 0
    value = pd_data.get(kondisi_field, 0) or 0
    return value > 0


def get_checklist_for_pd(pd_data: Dict) -> List[Tuple]:
    """Get checklist items applicable for this perjalanan dinas"""
    items = []
    for doc in get_all_checklist_items():
        kode, nama, kategori, wajib, kondisi = doc

        # Check condition
        if kondisi:
            if evaluate_condition(pd_data, kondisi):
                # Conditional doc becomes wajib when condition is met
                items.append((kode, nama, kategori, True, kondisi))
            # Skip if condition not met
        else:
            items.append(doc)

    return items


# =============================================================================
# CHECKLIST PERJALANAN DINAS MANAGER WIDGET
# =============================================================================

class ChecklistPerjalananDinasManager(QWidget):
    """Manager untuk checklist kelengkapan dokumen Perjalanan Dinas"""

    document_uploaded = Signal(int, str, str)  # pd_id, doc_type, filepath

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db_manager_v4()
        self.current_pd_id = None
        self.current_pd = None
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

        splitter.setSizes([550, 350])
        layout.addWidget(splitter)

        # Footer dengan progress
        footer = self.create_footer()
        layout.addWidget(footer)

    def create_header(self) -> QWidget:
        """Buat header dengan info perjalanan dinas"""
        group = QGroupBox("Checklist Kelengkapan Dokumen Perjalanan Dinas")
        layout = QVBoxLayout(group)

        # Info perjalanan dinas
        info_layout = QHBoxLayout()

        self.lbl_pd_nama = QLabel("Pilih perjalanan dinas untuk melihat checklist")
        self.lbl_pd_nama.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_pd_nama.setWordWrap(True)
        info_layout.addWidget(self.lbl_pd_nama, 1)

        self.lbl_pelaksana = QLabel("")
        self.lbl_pelaksana.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                padding: 5px 15px;
                border-radius: 12px;
                font-weight: bold;
            }
        """)
        info_layout.addWidget(self.lbl_pelaksana)

        layout.addLayout(info_layout)

        # Info tujuan dan tanggal
        detail_layout = QHBoxLayout()

        self.lbl_tujuan = QLabel("")
        self.lbl_tujuan.setStyleSheet("color: #7f8c8d;")
        detail_layout.addWidget(self.lbl_tujuan)

        detail_layout.addStretch()

        self.lbl_tanggal = QLabel("")
        self.lbl_tanggal.setStyleSheet("color: #27ae60; font-weight: bold;")
        detail_layout.addWidget(self.lbl_tanggal)

        layout.addLayout(detail_layout)

        # Filter dan tombol
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter Kategori:"))

        self.cmb_filter = QComboBox()
        self.cmb_filter.addItem("Semua Kategori", "ALL")
        for key, (label, color) in KATEGORI_LABELS.items():
            self.cmb_filter.addItem(f"{label}", key)
        self.cmb_filter.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.cmb_filter)

        filter_layout.addStretch()

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

        self.tbl_checklist.setColumnWidth(0, 70)
        self.tbl_checklist.setColumnWidth(2, 120)
        self.tbl_checklist.setColumnWidth(3, 60)
        self.tbl_checklist.setColumnWidth(4, 70)

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
        self.btn_delete.setStyleSheet("color: #e74c3c;")
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
        group = QGroupBox("Progress Kelengkapan SPJ")
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

        # Keterangan kurang
        self.lbl_kurang = QLabel("")
        self.lbl_kurang.setStyleSheet("color: #e74c3c; font-style: italic;")
        self.lbl_kurang.setWordWrap(True)
        layout.addWidget(self.lbl_kurang)

        return group

    def load_perjalanan_dinas(self, pd_id: int):
        """Load data perjalanan dinas dan checklist"""
        self.current_pd_id = pd_id

        # Ambil data perjalanan dinas
        pd_data = self.db.get_perjalanan_dinas(pd_id)
        if not pd_data:
            QMessageBox.warning(self, "Error", "Perjalanan dinas tidak ditemukan!")
            return

        self.current_pd = pd_data

        # Update header
        self.lbl_pd_nama.setText(pd_data.get('nama_kegiatan', 'Tanpa Nama'))
        self.lbl_pelaksana.setText(pd_data.get('pelaksana_nama', '-'))

        tujuan = pd_data.get('kota_tujuan', '')
        if pd_data.get('provinsi_tujuan'):
            tujuan = f"{tujuan}, {pd_data['provinsi_tujuan']}"
        self.lbl_tujuan.setText(f"Tujuan: {tujuan}")

        tgl_berangkat = pd_data.get('tanggal_berangkat', '')
        tgl_kembali = pd_data.get('tanggal_kembali', '')
        self.lbl_tanggal.setText(f"{tgl_berangkat} s/d {tgl_kembali}")

        # Initialize checklist if not exists
        existing = self.db.get_checklist_perjalanan_dinas(pd_id)
        if not existing:
            checklist_items = get_checklist_for_pd(pd_data)
            self.db.init_checklist_perjalanan_dinas(pd_id, checklist_items)

        # Load checklist
        self.load_checklist()

    def load_checklist(self):
        """Load daftar checklist ke tabel"""
        if not self.current_pd_id:
            return

        # Get applicable checklist for this PD
        checklist_config = get_checklist_for_pd(self.current_pd)

        # Get saved data from database
        saved_items = self.db.get_checklist_perjalanan_dinas(self.current_pd_id)
        saved_dict = {item['doc_type']: item for item in saved_items}

        self.tbl_checklist.setRowCount(len(checklist_config))
        self.checklist_items = {}

        for row, (kode, nama, kategori, wajib, kondisi) in enumerate(checklist_config):
            # Get saved data or use defaults
            saved = saved_dict.get(kode, {})
            status = saved.get('status', 'BELUM')
            filepath = saved.get('filepath_signed')
            catatan = saved.get('catatan')

            # Status
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
            has_file = bool(filepath)
            file_item = QTableWidgetItem("📄" if has_file else "-")
            file_item.setTextAlignment(Qt.AlignCenter)
            self.tbl_checklist.setItem(row, 4, file_item)

            # Simpan info
            self.checklist_items[kode] = {
                'nama': nama,
                'kategori': kategori,
                'wajib': wajib,
                'status': status,
                'filepath': filepath,
                'catatan': catatan,
            }

        self.update_progress()

    def update_progress(self):
        """Update progress bar dan summary"""
        if not self.checklist_items:
            return

        total_wajib = 0
        done_wajib = 0
        total_opsional = 0
        done_opsional = 0
        total_uploaded = 0
        kurang_list = []

        for kode, info in self.checklist_items.items():
            is_done = info['status'] in ('SIGNED', 'UPLOADED', 'VERIFIED')
            has_file = bool(info.get('filepath'))

            if info['wajib']:
                total_wajib += 1
                if is_done:
                    done_wajib += 1
                else:
                    kurang_list.append(info['nama'])
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

        # Update progress bar
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
                self.lbl_kurang.setText("")
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

            # Show missing docs
            if kurang_list:
                self.lbl_kurang.setText(f"Kurang: {', '.join(kurang_list[:5])}" +
                                        (f" (+{len(kurang_list)-5} lainnya)" if len(kurang_list) > 5 else ""))
            else:
                self.lbl_kurang.setText("")

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
        self.txt_catatan.setText(info.get('catatan', '') or '')

    def apply_filter(self):
        """Apply filter kategori"""
        filter_value = self.cmb_filter.currentData()

        for row in range(self.tbl_checklist.rowCount()):
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
            self.db.update_checklist_status(
                self.current_pd_id, kode, 'UPLOADED', dest_path
            )

            # Update UI
            self.checklist_items[kode]['status'] = 'UPLOADED'
            self.checklist_items[kode]['filepath'] = dest_path

            # Refresh
            self.refresh_checklist()

            QMessageBox.information(self, "Sukses", f"Dokumen berhasil diupload!\n{new_filename}")

            # Emit signal
            self.document_uploaded.emit(self.current_pd_id, kode, dest_path)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal upload dokumen:\n{str(e)}")

    def get_upload_folder(self) -> str:
        """Dapatkan folder upload untuk perjalanan dinas ini"""
        pelaksana = self.current_pd.get('pelaksana_nama', 'unknown')[:20]
        pd_id = self.current_pd.get('id', 0)

        # Bersihkan nama folder
        folder_name = f"PD_{pd_id}_{pelaksana}".replace(' ', '_')
        folder_name = "".join(c for c in folder_name if c.isalnum() or c in ('_', '-'))

        return os.path.join(OUTPUT_DIR, str(TAHUN_ANGGARAN), "Perjalanan_Dinas", folder_name, "signed_documents")

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
        self.db.delete_checklist_file(self.current_pd_id, kode)

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

        self.db.update_checklist_status(
            self.current_pd_id, kode,
            info.get('status', 'BELUM'),
            info.get('filepath'),
            catatan
        )

        self.checklist_items[kode]['catatan'] = catatan

        QMessageBox.information(self, "Sukses", "Catatan berhasil disimpan!")

    def refresh_checklist(self):
        """Refresh checklist dari database"""
        if self.current_pd_id:
            self.load_checklist()

    def export_to_pdf(self):
        """Export checklist ke PDF"""
        if not self.current_pd_id:
            QMessageBox.warning(self, "Peringatan", "Pilih perjalanan dinas terlebih dahulu!")
            return

        # Pilih lokasi simpan
        pelaksana = self.current_pd.get('pelaksana_nama', 'unknown')[:20]
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Checklist ke PDF",
            f"Checklist_PD_{pelaksana}.pdf",
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
        """Generate PDF checklist"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet

            doc = SimpleDocTemplate(filepath, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Title
            elements.append(Paragraph("CHECKLIST KELENGKAPAN DOKUMEN PERJALANAN DINAS", styles['Title']))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Kegiatan: {self.current_pd.get('nama_kegiatan', '-')}", styles['Normal']))
            elements.append(Paragraph(f"Pelaksana: {self.current_pd.get('pelaksana_nama', '-')}", styles['Normal']))
            elements.append(Paragraph(f"Tujuan: {self.current_pd.get('kota_tujuan', '-')}", styles['Normal']))
            elements.append(Paragraph(f"Tanggal: {self.current_pd.get('tanggal_berangkat', '')} s/d {self.current_pd.get('tanggal_kembali', '')}", styles['Normal']))
            elements.append(Spacer(1, 24))

            # Table data
            data = [['No', 'Dokumen', 'Kategori', 'Wajib', 'Status']]

            for i, (kode, info) in enumerate(self.checklist_items.items(), 1):
                status_label, _, _ = STATUS_DOKUMEN.get(info['status'], STATUS_DOKUMEN['BELUM'])
                kat_label, _ = KATEGORI_LABELS.get(info['kategori'], ('', ''))
                data.append([
                    str(i),
                    info['nama'],
                    kat_label,
                    'Ya' if info['wajib'] else 'Tidak',
                    status_label
                ])

            table = Table(data, colWidths=[30, 220, 100, 50, 90])
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

            # Progress summary
            progress = self.db.get_checklist_progress(self.current_pd_id)
            elements.append(Spacer(1, 24))
            elements.append(Paragraph(f"Progress: {progress['progress']}% ({progress['done_wajib']}/{progress['total_wajib']} dokumen wajib)", styles['Normal']))

            doc.build(elements)

        except ImportError:
            # Fallback: Generate simple text file
            txt_path = filepath.replace('.pdf', '.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("CHECKLIST KELENGKAPAN DOKUMEN PERJALANAN DINAS\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Kegiatan: {self.current_pd.get('nama_kegiatan', '-')}\n")
                f.write(f"Pelaksana: {self.current_pd.get('pelaksana_nama', '-')}\n")
                f.write(f"Tujuan: {self.current_pd.get('kota_tujuan', '-')}\n")
                f.write(f"Tanggal: {self.current_pd.get('tanggal_berangkat', '')} s/d {self.current_pd.get('tanggal_kembali', '')}\n\n")
                f.write("-" * 60 + "\n")

                for i, (kode, info) in enumerate(self.checklist_items.items(), 1):
                    status_label, _, _ = STATUS_DOKUMEN.get(info['status'], STATUS_DOKUMEN['BELUM'])
                    wajib = "WAJIB" if info['wajib'] else "Opsional"
                    f.write(f"{i}. [{status_label}] {info['nama']} ({wajib})\n")

            QMessageBox.warning(self, "Info", f"reportlab tidak tersedia.\nFile disimpan sebagai TXT: {txt_path}")


# =============================================================================
# DIALOG UNTUK STANDALONE
# =============================================================================

class ChecklistPerjalananDinasDialog(QDialog):
    """Dialog untuk menampilkan checklist perjalanan dinas"""

    def __init__(self, pd_id: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Checklist Kelengkapan Dokumen Perjalanan Dinas")
        self.setMinimumSize(1000, 700)

        layout = QVBoxLayout(self)

        self.manager = ChecklistPerjalananDinasManager()
        self.manager.load_perjalanan_dinas(pd_id)
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

    # Test dialog - ganti dengan ID yang valid
    dialog = ChecklistPerjalananDinasDialog(1)
    dialog.show()

    sys.exit(app.exec())
