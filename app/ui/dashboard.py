"""
PPK DOCUMENT FACTORY v3.0 - Main Dashboard UI
==============================================
Workflow-based document generation dashboard
"""

import sys
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit,
    QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QTabWidget,
    QScrollArea, QFrame, QMessageBox, QFileDialog, QDialog,
    QDialogButtonBox, QStackedWidget, QListWidget, QListWidgetItem,
    QSplitter, QFormLayout, QCheckBox, QProgressBar, QStatusBar,
    QToolBar, QTreeWidget, QTreeWidgetItem, QSizePolicy, QPlainTextEdit
)
from PySide6.QtCore import Qt, QDate, Signal, QSize, QTimer
from PySide6.QtGui import QFont, QColor, QIcon, QAction, QPalette, QBrush

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import (
    TAHUN_ANGGARAN, OUTPUT_DIR, SATKER_DEFAULT, WORKFLOW_STAGES,
    DOCUMENT_TEMPLATES, ALL_PLACEHOLDERS
)
from app.core.database import get_db_manager
from app.templates.engine import get_template_engine, get_template_manager, format_rupiah
from app.workflow.engine import get_workflow_engine, StageStatus
from app.ui.item_barang_manager import ItemBarangManager


# ============================================================================
# STYLES
# ============================================================================

STYLE_SHEET = """
QMainWindow {
    background-color: #f0f2f5;
}

QGroupBox {
    font-weight: bold;
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
    background-color: white;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px;
    color: #2c3e50;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #1f6dad;
}

QPushButton:disabled {
    background-color: #bdc3c7;
    color: #7f8c8d;
}

QPushButton#btnSuccess {
    background-color: #27ae60;
}
QPushButton#btnSuccess:hover {
    background-color: #219a52;
}

QPushButton#btnWarning {
    background-color: #e67e22;
}
QPushButton#btnWarning:hover {
    background-color: #d35400;
}

QPushButton#btnDanger {
    background-color: #e74c3c;
}
QPushButton#btnDanger:hover {
    background-color: #c0392b;
}

QPushButton#btnSecondary {
    background-color: #95a5a6;
}
QPushButton#btnSecondary:hover {
    background-color: #7f8c8d;
}

QLabel#titleLabel {
    font-size: 24px;
    font-weight: bold;
    color: #2c3e50;
}

QLabel#subtitleLabel {
    font-size: 12px;
    color: #7f8c8d;
}

QTableWidget {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background-color: white;
    gridline-color: #ecf0f1;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QHeaderView::section {
    background-color: #34495e;
    color: white;
    padding: 10px;
    border: none;
    font-weight: bold;
}

QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 8px;
    background-color: white;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 2px solid #3498db;
}

QProgressBar {
    border: 1px solid #d0d0d0;
    border-radius: 5px;
    text-align: center;
    background-color: #ecf0f1;
}

QProgressBar::chunk {
    background-color: #27ae60;
    border-radius: 4px;
}

QListWidget {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background-color: white;
}

QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #ecf0f1;
}

QListWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QTreeWidget {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background-color: white;
}

QTreeWidget::item {
    padding: 5px;
}

QScrollArea {
    border: none;
}

QStatusBar {
    background-color: #34495e;
    color: white;
}

QTabWidget::pane {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background-color: white;
}

QTabBar::tab {
    background-color: #ecf0f1;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom: 2px solid #3498db;
}
"""


# ============================================================================
# WORKFLOW STAGE WIDGET
# ============================================================================

class StageWidget(QFrame):
    """Widget representing a single workflow stage"""
    
    clicked = Signal(str)
    generateClicked = Signal(str)
    
    COLORS = {
        'pending': '#bdc3c7',
        'in_progress': '#f39c12',
        'completed': '#27ae60',
        'skipped': '#95a5a6',
        'locked': '#e74c3c',
    }
    
    def __init__(self, stage_code: str, stage_name: str, parent=None):
        super().__init__(parent)
        self.stage_code = stage_code
        self.stage_name = stage_name
        self.status = 'pending'
        self.is_current = False
        self.is_allowed = False
        
        self.setup_ui()
    
    def setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setMinimumHeight(80)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Status indicator
        self.status_indicator = QLabel("⏳")
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_indicator.setFont(QFont("", 20))
        layout.addWidget(self.status_indicator)
        
        # Stage name
        self.name_label = QLabel(self.stage_name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setFont(QFont("", 10, QFont.Bold))
        layout.addWidget(self.name_label)
        
        # Status text
        self.status_label = QLabel("Menunggu")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("", 8))
        layout.addWidget(self.status_label)
        
        self.update_style()
    
    def set_status(self, status: str, is_current: bool = False, is_allowed: bool = False):
        self.status = status
        self.is_current = is_current
        self.is_allowed = is_allowed
        self.update_style()
    
    def update_style(self):
        color = self.COLORS.get(self.status, '#bdc3c7')
        
        # Status indicator
        icons = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'skipped': '⏭️',
            'locked': '🔒',
        }
        self.status_indicator.setText(icons.get(self.status, '⏳'))
        
        # Status text
        texts = {
            'pending': 'Menunggu',
            'in_progress': 'Sedang Proses',
            'completed': 'Selesai',
            'skipped': 'Dilewati',
            'locked': 'Terkunci',
        }
        self.status_label.setText(texts.get(self.status, 'Menunggu'))
        
        # Frame style
        border_width = 3 if self.is_current else 1
        bg_color = '#fff9e6' if self.is_current else 'white'
        
        self.setStyleSheet(f"""
            StageWidget {{
                background-color: {bg_color};
                border: {border_width}px solid {color};
                border-radius: 8px;
            }}
            StageWidget:hover {{
                background-color: #f8f9fa;
            }}
        """)
        
        self.status_label.setStyleSheet(f"color: {color};")
    
    def mousePressEvent(self, event):
        if self.is_allowed:
            self.clicked.emit(self.stage_code)
        super().mousePressEvent(event)


# ============================================================================
# PAKET FORM DIALOG
# ============================================================================

class PaketFormDialog(QDialog):
    """Dialog for creating/editing paket"""
    
    def __init__(self, paket_id: int = None, parent=None):
        super().__init__(parent)
        self.paket_id = paket_id
        self.db = get_db_manager()
        
        self.setWindowTitle("Tambah Paket Baru" if not paket_id else "Edit Paket")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        self.setup_ui()
        
        if paket_id:
            self.load_paket()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Basic Info
        basic_group = QGroupBox("Informasi Dasar")
        basic_layout = QFormLayout()
        
        self.txt_nama = QLineEdit()
        self.txt_nama.setPlaceholderText("Nama paket pekerjaan...")
        basic_layout.addRow("Nama Paket:", self.txt_nama)
        
        self.cmb_jenis = QComboBox()
        self.cmb_jenis.addItems(['Barang', 'Jasa Lainnya', 'Jasa Konsultansi', 'Pekerjaan Konstruksi'])
        basic_layout.addRow("Jenis Pengadaan:", self.cmb_jenis)
        
        self.cmb_metode = QComboBox()
        self.cmb_metode.addItems(['Pengadaan Langsung', 'Penunjukan Langsung', 'Tender', 'Seleksi'])
        basic_layout.addRow("Metode:", self.cmb_metode)
        
        self.txt_lokasi = QLineEdit()
        self.txt_lokasi.setText(SATKER_DEFAULT['nama_pendek'])
        basic_layout.addRow("Lokasi:", self.txt_lokasi)
        
        self.txt_sumber_dana = QLineEdit()
        self.txt_sumber_dana.setText("DIPA")
        basic_layout.addRow("Sumber Dana:", self.txt_sumber_dana)
        
        self.txt_kode_akun = QLineEdit()
        self.txt_kode_akun.setPlaceholderText("Contoh: 5211.001")
        basic_layout.addRow("Kode Akun/MAK:", self.txt_kode_akun)
        
        basic_group.setLayout(basic_layout)
        scroll_layout.addWidget(basic_group)
        
        # Nilai
        nilai_group = QGroupBox("Nilai Pekerjaan")
        nilai_layout = QFormLayout()
        
        self.spn_pagu = QDoubleSpinBox()
        self.spn_pagu.setRange(0, 999999999999)
        self.spn_pagu.setDecimals(0)
        self.spn_pagu.setPrefix("Rp ")
        self.spn_pagu.setSingleStep(1000000)
        nilai_layout.addRow("Nilai Pagu:", self.spn_pagu)
        
        # HPS with status label
        hps_layout = QHBoxLayout()
        self.spn_hps = QDoubleSpinBox()
        self.spn_hps.setRange(0, 999999999999)
        self.spn_hps.setDecimals(0)
        self.spn_hps.setPrefix("Rp ")
        self.spn_hps.setSingleStep(1000000)
        hps_layout.addWidget(self.spn_hps)
        
        self.lbl_hps_status = QLabel("")
        self.lbl_hps_status.setStyleSheet("font-size: 10px; color: #666;")
        hps_layout.addWidget(self.lbl_hps_status)
        
        nilai_layout.addRow("Nilai HPS:", hps_layout)
        
        # Kontrak with status label
        kontrak_layout = QHBoxLayout()
        self.spn_kontrak = QDoubleSpinBox()
        self.spn_kontrak.setRange(0, 999999999999)
        self.spn_kontrak.setDecimals(0)
        self.spn_kontrak.setPrefix("Rp ")
        self.spn_kontrak.setSingleStep(1000000)
        kontrak_layout.addWidget(self.spn_kontrak)
        
        self.lbl_kontrak_status = QLabel("")
        self.lbl_kontrak_status.setStyleSheet("font-size: 10px; color: #666;")
        kontrak_layout.addWidget(self.lbl_kontrak_status)
        
        nilai_layout.addRow("Nilai Kontrak:", kontrak_layout)
        
        # Set default status for new paket
        if not self.paket_id:
            self.lbl_hps_status.setText("📝 Manual (paket baru)")
            self.lbl_hps_status.setStyleSheet("font-size: 10px; color: #2196f3;")
            self.lbl_kontrak_status.setText("📝 Manual (paket baru)")
            self.lbl_kontrak_status.setStyleSheet("font-size: 10px; color: #2196f3;")
        
        self.cmb_pph = QComboBox()
        self.cmb_pph.addItems(['PPh 22 (1.5%)', 'PPh 23 (2%)', 'PPh 21 (5%)', 'PPh 4(2) (2.5%)'])
        nilai_layout.addRow("Jenis PPh:", self.cmb_pph)
        
        # Metode HPS
        self.cmb_metode_hps = QComboBox()
        self.cmb_metode_hps.addItem("📊 Rata-rata", "RATA")
        self.cmb_metode_hps.addItem("📈 Harga Tertinggi", "TERTINGGI")
        self.cmb_metode_hps.addItem("📉 Harga Terendah", "TERENDAH")
        self.cmb_metode_hps.setToolTip("Metode perhitungan harga HPS dari survey harga")
        nilai_layout.addRow("Metode HPS:", self.cmb_metode_hps)
        
        nilai_group.setLayout(nilai_layout)
        scroll_layout.addWidget(nilai_group)
        
        # Waktu
        waktu_group = QGroupBox("Waktu Pelaksanaan")
        waktu_layout = QFormLayout()
        
        self.date_mulai = QDateEdit()
        self.date_mulai.setCalendarPopup(True)
        self.date_mulai.setDate(QDate.currentDate())
        waktu_layout.addRow("Tanggal Mulai:", self.date_mulai)
        
        self.spn_jangka = QSpinBox()
        self.spn_jangka.setRange(1, 365)
        self.spn_jangka.setValue(30)
        self.spn_jangka.setSuffix(" hari")
        self.spn_jangka.valueChanged.connect(self.update_tanggal_selesai)
        waktu_layout.addRow("Jangka Waktu:", self.spn_jangka)
        
        self.date_selesai = QDateEdit()
        self.date_selesai.setCalendarPopup(True)
        self.date_selesai.setDate(QDate.currentDate().addDays(30))
        waktu_layout.addRow("Tanggal Selesai:", self.date_selesai)
        
        waktu_group.setLayout(waktu_layout)
        scroll_layout.addWidget(waktu_group)
        
        # Pejabat
        pejabat_group = QGroupBox("Pejabat Terkait")
        pejabat_layout = QFormLayout()
        
        self.cmb_ppk = QComboBox()
        self.load_pegawai_combo(self.cmb_ppk, 'ppk')
        pejabat_layout.addRow("PPK:", self.cmb_ppk)
        
        self.cmb_ppspm = QComboBox()
        self.load_pegawai_combo(self.cmb_ppspm, 'ppspm')
        pejabat_layout.addRow("PPSPM:", self.cmb_ppspm)
        
        self.cmb_bendahara = QComboBox()
        self.load_pegawai_combo(self.cmb_bendahara, 'bendahara')
        pejabat_layout.addRow("Bendahara:", self.cmb_bendahara)
        
        pejabat_group.setLayout(pejabat_layout)
        scroll_layout.addWidget(pejabat_group)
        
        # Penyedia
        penyedia_group = QGroupBox("Penyedia")
        penyedia_layout = QFormLayout()
        
        self.cmb_penyedia = QComboBox()
        self.load_penyedia_combo()
        penyedia_layout.addRow("Penyedia:", self.cmb_penyedia)
        
        penyedia_group.setLayout(penyedia_layout)
        scroll_layout.addWidget(penyedia_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_save = QPushButton("💾 Simpan")
        btn_save.setObjectName("btnSuccess")
        btn_save.clicked.connect(self.save_paket)
        btn_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("Batal")
        btn_cancel.setObjectName("btnSecondary")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
    
    def load_pegawai_combo(self, combo: QComboBox, role: str):
        combo.clear()
        combo.addItem("-- Pilih --", None)
        
        pegawai_list = self.db.get_pegawai_list(role)
        for peg in pegawai_list:
            nama = peg['nama']
            if peg.get('gelar_depan'):
                nama = f"{peg['gelar_depan']} {nama}"
            if peg.get('gelar_belakang'):
                nama = f"{nama}, {peg['gelar_belakang']}"
            combo.addItem(nama, peg['id'])
    
    def load_penyedia_combo(self):
        self.cmb_penyedia.clear()
        self.cmb_penyedia.addItem("-- Pilih --", None)
        
        penyedia_list = self.db.get_penyedia_list()
        for pen in penyedia_list:
            self.cmb_penyedia.addItem(pen['nama'], pen['id'])
    
    def update_tanggal_selesai(self):
        start = self.date_mulai.date()
        days = self.spn_jangka.value()
        self.date_selesai.setDate(start.addDays(days))
    
    def load_paket(self):
        paket = self.db.get_paket(self.paket_id)
        if not paket:
            return
        
        self.txt_nama.setText(paket.get('nama', ''))
        
        jenis_idx = self.cmb_jenis.findText(paket.get('jenis_pengadaan', ''))
        if jenis_idx >= 0:
            self.cmb_jenis.setCurrentIndex(jenis_idx)
        
        metode_idx = self.cmb_metode.findText(paket.get('metode_pengadaan', ''))
        if metode_idx >= 0:
            self.cmb_metode.setCurrentIndex(metode_idx)
        
        self.txt_lokasi.setText(paket.get('lokasi', ''))
        self.txt_sumber_dana.setText(paket.get('sumber_dana', ''))
        self.txt_kode_akun.setText(paket.get('kode_akun', ''))
        
        self.spn_pagu.setValue(paket.get('nilai_pagu', 0) or 0)
        self.spn_hps.setValue(paket.get('nilai_hps', 0) or 0)
        self.spn_kontrak.setValue(paket.get('nilai_kontrak', 0) or 0)
        
        # ========================================================
        # WORKFLOW VALIDATION: HPS only editable after survey
        # ========================================================
        survey_locked = paket.get('survey_locked', 0)
        hps_locked = paket.get('hps_locked', 0)
        
        if not survey_locked:
            # Survey belum selesai - HPS tidak bisa diedit manual
            self.spn_hps.setEnabled(False)
            self.spn_hps.setToolTip("HPS akan otomatis dihitung dari survey harga.\nSelesaikan survey terlebih dahulu di menu Lifecycle Harga.")
            self.spn_hps.setStyleSheet("background-color: #e0e0e0;")
            self.lbl_hps_status.setText("⏳ Menunggu Survey")
            self.lbl_hps_status.setStyleSheet("font-size: 10px; color: #ff9800;")
        elif hps_locked:
            self.spn_hps.setEnabled(False)
            self.spn_hps.setToolTip("Nilai HPS sudah ditetapkan dan dikunci.")
            self.spn_hps.setStyleSheet("background-color: #c8e6c9;")
            self.lbl_hps_status.setText("🔒 HPS Final")
            self.lbl_hps_status.setStyleSheet("font-size: 10px; color: #2e7d32;")
        else:
            self.spn_hps.setEnabled(True)
            self.spn_hps.setToolTip("Nilai HPS dapat diubah karena survey sudah selesai.")
            self.spn_hps.setStyleSheet("")
            self.lbl_hps_status.setText("✏️ Dapat diedit")
            self.lbl_hps_status.setStyleSheet("font-size: 10px; color: #2196f3;")
        
        # ========================================================
        # WORKFLOW VALIDATION: Kontrak locked after finalized
        # ========================================================
        kontrak_final_locked = paket.get('kontrak_final_locked', 0)
        
        if kontrak_final_locked:
            # Kontrak sudah final - tidak bisa diubah
            self.spn_kontrak.setEnabled(False)
            self.spn_kontrak.setToolTip("Nilai Kontrak sudah FINAL dan tidak dapat diubah.\n(Kontrak telah ditetapkan oleh Pejabat Pengadaan)")
            self.spn_kontrak.setStyleSheet("background-color: #c8e6c9; color: #2e7d32;")
            self.lbl_kontrak_status.setText("🔒 Kontrak Final")
            self.lbl_kontrak_status.setStyleSheet("font-size: 10px; color: #2e7d32;")
        elif not hps_locked:
            # HPS belum ditetapkan - kontrak belum bisa diisi
            self.spn_kontrak.setEnabled(False)
            self.spn_kontrak.setToolTip("Nilai Kontrak akan diisi setelah proses pemilihan penyedia.\nHPS harus ditetapkan terlebih dahulu.")
            self.spn_kontrak.setStyleSheet("background-color: #e0e0e0;")
            self.lbl_kontrak_status.setText("⏳ Menunggu HPS")
            self.lbl_kontrak_status.setStyleSheet("font-size: 10px; color: #ff9800;")
        else:
            self.spn_kontrak.setEnabled(True)
            self.spn_kontrak.setToolTip("Nilai Kontrak hasil negosiasi dengan penyedia.\nIsi melalui menu Lifecycle Harga untuk validasi tidak melebihi HPS.")
            self.spn_kontrak.setStyleSheet("")
            self.lbl_kontrak_status.setText("✏️ Input hasil negosiasi")
            self.lbl_kontrak_status.setStyleSheet("font-size: 10px; color: #2196f3;")
        
        # Metode HPS
        metode_hps = paket.get('metode_hps', 'RATA')
        idx = self.cmb_metode_hps.findData(metode_hps)
        if idx >= 0:
            self.cmb_metode_hps.setCurrentIndex(idx)
        
        self.spn_jangka.setValue(paket.get('jangka_waktu', 30) or 30)
        
        if paket.get('tanggal_mulai'):
            try:
                d = datetime.strptime(str(paket['tanggal_mulai']), '%Y-%m-%d')
                self.date_mulai.setDate(QDate(d.year, d.month, d.day))
            except:
                pass
        
        if paket.get('tanggal_selesai'):
            try:
                d = datetime.strptime(str(paket['tanggal_selesai']), '%Y-%m-%d')
                self.date_selesai.setDate(QDate(d.year, d.month, d.day))
            except:
                pass
        
        # Set combos by ID
        for i in range(self.cmb_ppk.count()):
            if self.cmb_ppk.itemData(i) == paket.get('ppk_id'):
                self.cmb_ppk.setCurrentIndex(i)
                break
        
        for i in range(self.cmb_ppspm.count()):
            if self.cmb_ppspm.itemData(i) == paket.get('ppspm_id'):
                self.cmb_ppspm.setCurrentIndex(i)
                break
        
        for i in range(self.cmb_bendahara.count()):
            if self.cmb_bendahara.itemData(i) == paket.get('bendahara_id'):
                self.cmb_bendahara.setCurrentIndex(i)
                break
        
        for i in range(self.cmb_penyedia.count()):
            if self.cmb_penyedia.itemData(i) == paket.get('penyedia_id'):
                self.cmb_penyedia.setCurrentIndex(i)
                break
    
    def save_paket(self):
        if not self.txt_nama.text().strip():
            QMessageBox.warning(self, "Peringatan", "Nama paket harus diisi!")
            return
        
        # Parse PPh
        pph_map = {
            'PPh 22 (1.5%)': ('PPh 22', 0.015),
            'PPh 23 (2%)': ('PPh 23', 0.02),
            'PPh 21 (5%)': ('PPh 21', 0.05),
            'PPh 4(2) (2.5%)': ('PPh 4(2)', 0.025),
        }
        pph_text = self.cmb_pph.currentText()
        jenis_pph, tarif_pph = pph_map.get(pph_text, ('PPh 22', 0.015))
        
        # Calculate taxes
        nilai_kontrak = self.spn_kontrak.value()
        nilai_ppn = round(nilai_kontrak * 0.11)
        nilai_pph = round(nilai_kontrak * tarif_pph)
        
        data = {
            'nama': self.txt_nama.text().strip(),
            'tahun_anggaran': TAHUN_ANGGARAN,
            'jenis_pengadaan': self.cmb_jenis.currentText(),
            'metode_pengadaan': self.cmb_metode.currentText(),
            'lokasi': self.txt_lokasi.text(),
            'sumber_dana': self.txt_sumber_dana.text(),
            'kode_akun': self.txt_kode_akun.text(),
            'nilai_pagu': self.spn_pagu.value(),
            'nilai_hps': self.spn_hps.value(),
            'nilai_kontrak': nilai_kontrak,
            'nilai_ppn': nilai_ppn,
            'nilai_pph': nilai_pph,
            'jenis_pph': jenis_pph,
            'tarif_pph': tarif_pph,
            'metode_hps': self.cmb_metode_hps.currentData(),
            'tanggal_mulai': self.date_mulai.date().toPython(),
            'tanggal_selesai': self.date_selesai.date().toPython(),
            'jangka_waktu': self.spn_jangka.value(),
            'ppk_id': self.cmb_ppk.currentData(),
            'ppspm_id': self.cmb_ppspm.currentData(),
            'bendahara_id': self.cmb_bendahara.currentData(),
            'penyedia_id': self.cmb_penyedia.currentData(),
        }
        
        try:
            if self.paket_id:
                self.db.update_paket(self.paket_id, data)
            else:
                self.paket_id = self.db.create_paket(data)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan paket:\n{str(e)}")


# ============================================================================
# DOCUMENT GENERATION DIALOG
# ============================================================================

class GenerateDocumentDialog(QDialog):
    """Dialog for generating documents for a stage with complete data input"""
    
    def __init__(self, paket_id: int, stage_code: str, parent=None):
        super().__init__(parent)
        self.paket_id = paket_id
        self.stage_code = stage_code
        self.db = get_db_manager()
        self.workflow = get_workflow_engine()
        self.paket = self.db.get_paket(paket_id)
        
        self.setWindowTitle(f"Generate Dokumen - {stage_code}")
        self.setMinimumWidth(800)
        self.setMinimumHeight(700)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Use tabs for organized input
        self.tabs = QTabWidget()
        
        # === TAB 1: Dokumen & Tanggal ===
        tab_dokumen = QWidget()
        tab_dokumen_layout = QVBoxLayout(tab_dokumen)
        
        # Stage info
        info_group = QGroupBox("Informasi Stage")
        info_layout = QFormLayout()
        
        self.lbl_stage = QLabel()
        info_layout.addRow("Stage:", self.lbl_stage)
        
        self.lbl_status = QLabel()
        info_layout.addRow("Status:", self.lbl_status)
        
        info_group.setLayout(info_layout)
        tab_dokumen_layout.addWidget(info_group)
        
        # Documents to generate with date input
        self.doc_group = QGroupBox("Dokumen yang akan di-generate")
        self.doc_group_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Pilih"))
        header_layout.addWidget(QLabel("Nama Dokumen"), 1)
        header_layout.addWidget(QLabel("Tanggal Dokumen"))
        header_layout.addWidget(QLabel("Nomor (opsional)"))
        self.doc_group_layout.addLayout(header_layout)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        self.doc_group_layout.addWidget(sep)
        
        self.doc_entries = {}  # {doc_type: {'checkbox': cb, 'date': date_edit, 'nomor': txt_nomor}}
        self.doc_group.setLayout(self.doc_group_layout)
        tab_dokumen_layout.addWidget(self.doc_group)
        
        # Quick date set
        quick_date_layout = QHBoxLayout()
        quick_date_layout.addWidget(QLabel("Set tanggal semua:"))
        self.quick_date = QDateEdit()
        self.quick_date.setCalendarPopup(True)
        self.quick_date.setDate(QDate.currentDate())
        self.quick_date.setDisplayFormat("dd MMMM yyyy")
        quick_date_layout.addWidget(self.quick_date)
        btn_apply_date = QPushButton("Terapkan ke Semua")
        btn_apply_date.clicked.connect(self.apply_date_to_all)
        quick_date_layout.addWidget(btn_apply_date)
        quick_date_layout.addStretch()
        tab_dokumen_layout.addLayout(quick_date_layout)
        
        tab_dokumen_layout.addStretch()
        self.tabs.addTab(tab_dokumen, "📄 Dokumen & Tanggal")
        
        # === TAB 2: Data Penyedia ===
        tab_penyedia = QWidget()
        tab_penyedia_layout = QVBoxLayout(tab_penyedia)
        
        # Penyedia selector from database
        selector_group = QGroupBox("Pilih Penyedia dari Database")
        selector_layout = QHBoxLayout()
        
        self.cmb_penyedia = QComboBox()
        self.cmb_penyedia.setMinimumWidth(400)
        self.cmb_penyedia.currentIndexChanged.connect(self.on_penyedia_selected)
        selector_layout.addWidget(self.cmb_penyedia, 1)
        
        btn_refresh_penyedia = QPushButton("🔄")
        btn_refresh_penyedia.setToolTip("Refresh daftar penyedia")
        btn_refresh_penyedia.setFixedWidth(40)
        btn_refresh_penyedia.clicked.connect(self.refresh_penyedia_list)
        selector_layout.addWidget(btn_refresh_penyedia)
        
        selector_group.setLayout(selector_layout)
        tab_penyedia_layout.addWidget(selector_group)
        
        penyedia_group = QGroupBox("Data Penyedia/Rekanan")
        penyedia_form = QFormLayout()
        
        self.txt_penyedia_nama = QLineEdit()
        self.txt_penyedia_nama.setPlaceholderText("PT/CV Nama Perusahaan")
        penyedia_form.addRow("Nama Perusahaan:", self.txt_penyedia_nama)
        
        self.txt_direktur_nama = QLineEdit()
        self.txt_direktur_nama.setPlaceholderText("Nama lengkap direktur")
        penyedia_form.addRow("Nama Direktur:", self.txt_direktur_nama)
        
        self.txt_penyedia_alamat = QLineEdit()
        self.txt_penyedia_alamat.setPlaceholderText("Jl. Contoh No. 123, Kota")
        penyedia_form.addRow("Alamat:", self.txt_penyedia_alamat)
        
        self.txt_penyedia_npwp = QLineEdit()
        self.txt_penyedia_npwp.setPlaceholderText("00.000.000.0-000.000")
        penyedia_form.addRow("NPWP:", self.txt_penyedia_npwp)
        
        self.txt_penyedia_rekening = QLineEdit()
        self.txt_penyedia_rekening.setPlaceholderText("1234567890")
        penyedia_form.addRow("No. Rekening:", self.txt_penyedia_rekening)
        
        self.txt_penyedia_bank = QLineEdit()
        self.txt_penyedia_bank.setPlaceholderText("Bank BRI/BNI/Mandiri/dll")
        penyedia_form.addRow("Nama Bank:", self.txt_penyedia_bank)
        
        self.txt_penyedia_bank_cabang = QLineEdit()
        self.txt_penyedia_bank_cabang.setPlaceholderText("Cabang Sorong")
        penyedia_form.addRow("Cabang Bank:", self.txt_penyedia_bank_cabang)
        
        penyedia_group.setLayout(penyedia_form)
        tab_penyedia_layout.addWidget(penyedia_group)
        
        # Save penyedia button
        btn_save_penyedia = QPushButton("💾 Simpan Data Penyedia ke Paket")
        btn_save_penyedia.clicked.connect(self.save_penyedia_to_paket)
        tab_penyedia_layout.addWidget(btn_save_penyedia)
        
        tab_penyedia_layout.addStretch()
        self.tabs.addTab(tab_penyedia, "🏢 Data Penyedia")
        
        # === TAB 3: Data Satker ===
        tab_satker = QWidget()
        tab_satker_layout = QVBoxLayout(tab_satker)
        
        satker_group = QGroupBox("Data Satuan Kerja")
        satker_form = QFormLayout()
        
        self.txt_kementerian = QLineEdit()
        self.txt_kementerian.setText("KEMENTERIAN KELAUTAN DAN PERIKANAN")
        satker_form.addRow("Kementerian:", self.txt_kementerian)
        
        self.txt_eselon1 = QLineEdit()
        self.txt_eselon1.setText("BADAN PENYULUHAN DAN PENGEMBANGAN SDM KP")
        satker_form.addRow("Eselon I:", self.txt_eselon1)
        
        self.txt_satker_nama = QLineEdit()
        self.txt_satker_nama.setText("POLITEKNIK KELAUTAN DAN PERIKANAN SORONG")
        satker_form.addRow("Nama Satker:", self.txt_satker_nama)
        
        self.txt_satker_alamat = QLineEdit()
        self.txt_satker_alamat.setText("Jl. Kapitan Pattimura, Tanjung Kasuari")
        satker_form.addRow("Alamat:", self.txt_satker_alamat)
        
        self.txt_satker_kota = QLineEdit()
        self.txt_satker_kota.setText("Kota Sorong")
        satker_form.addRow("Kota:", self.txt_satker_kota)
        
        self.txt_satker_telepon = QLineEdit()
        self.txt_satker_telepon.setText("(0951) 321234")
        satker_form.addRow("Telepon:", self.txt_satker_telepon)
        
        satker_group.setLayout(satker_form)
        tab_satker_layout.addWidget(satker_group)
        
        # Pejabat section
        pejabat_group = QGroupBox("Pejabat Terkait")
        pejabat_form = QFormLayout()
        
        self.txt_ppk_nama = QLineEdit()
        pejabat_form.addRow("Nama PPK:", self.txt_ppk_nama)
        
        self.txt_ppk_nip = QLineEdit()
        pejabat_form.addRow("NIP PPK:", self.txt_ppk_nip)
        
        self.txt_pp_nama = QLineEdit()
        pejabat_form.addRow("Nama Pejabat Pengadaan:", self.txt_pp_nama)
        
        self.txt_pp_nip = QLineEdit()
        pejabat_form.addRow("NIP Pejabat Pengadaan:", self.txt_pp_nip)
        
        pejabat_group.setLayout(pejabat_form)
        tab_satker_layout.addWidget(pejabat_group)
        
        tab_satker_layout.addStretch()
        self.tabs.addTab(tab_satker, "🏛️ Data Satker")
        
        layout.addWidget(self.tabs)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Results
        self.results_list = QListWidget()
        self.results_list.hide()
        layout.addWidget(self.results_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_generate = QPushButton("🖨️ Generate Dokumen")
        self.btn_generate.setObjectName("btnSuccess")
        self.btn_generate.clicked.connect(self.generate_documents)
        btn_layout.addWidget(self.btn_generate)
        
        self.btn_open_folder = QPushButton("📂 Buka Folder")
        self.btn_open_folder.setObjectName("btnSecondary")
        self.btn_open_folder.clicked.connect(self.open_output_folder)
        self.btn_open_folder.hide()
        btn_layout.addWidget(self.btn_open_folder)
        
        btn_close = QPushButton("Tutup")
        btn_close.setObjectName("btnSecondary")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
    
    def load_data(self):
        # Find stage
        stage_config = next((s for s in WORKFLOW_STAGES if s['code'] == self.stage_code), None)
        if not stage_config:
            return
        
        self.lbl_stage.setText(f"{stage_config['name']} ({self.stage_code})")
        
        # Check if allowed
        allowed, message = self.workflow.is_stage_allowed(self.paket_id, self.stage_code)
        if allowed:
            self.lbl_status.setText("✅ Dapat diproses")
            self.lbl_status.setStyleSheet("color: #27ae60;")
        else:
            self.lbl_status.setText(f"⚠️ {message}")
            self.lbl_status.setStyleSheet("color: #f39c12;")
            # Allow anyway but with warning
            # self.btn_generate.setEnabled(False)
        
        # Add document entries with date and nomor input
        for doc_type in stage_config.get('outputs', []):
            template_info = DOCUMENT_TEMPLATES.get(doc_type, {})
            
            row_layout = QHBoxLayout()
            
            cb = QCheckBox()
            cb.setChecked(True)
            row_layout.addWidget(cb)
            
            lbl = QLabel(f"{template_info.get('name', doc_type)}")
            lbl.setMinimumWidth(250)
            row_layout.addWidget(lbl, 1)
            
            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDate(QDate.currentDate())
            date_edit.setDisplayFormat("dd/MM/yyyy")
            date_edit.setFixedWidth(120)
            row_layout.addWidget(date_edit)
            
            txt_nomor = QLineEdit()
            txt_nomor.setPlaceholderText("Auto")
            txt_nomor.setFixedWidth(150)
            row_layout.addWidget(txt_nomor)
            
            self.doc_entries[doc_type] = {
                'checkbox': cb,
                'date': date_edit,
                'nomor': txt_nomor,
                'label': lbl
            }
            
            self.doc_group_layout.addLayout(row_layout)
        
        # Load penyedia list into dropdown
        self.refresh_penyedia_list()
        
        # Load penyedia data from paket
        self.load_penyedia_from_db()
        
        # Load satker and pejabat data
        self.load_satker_data()
    
    def apply_date_to_all(self):
        """Apply quick date to all document entries"""
        selected_date = self.quick_date.date()
        for entry in self.doc_entries.values():
            entry['date'].setDate(selected_date)
    
    def refresh_penyedia_list(self):
        """Load penyedia list from database into dropdown"""
        self.cmb_penyedia.clear()
        self.cmb_penyedia.addItem("-- Pilih Penyedia --", None)
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, nama, nama_direktur, alamat, npwp, 
                           no_rekening, nama_bank, kota
                    FROM penyedia
                    WHERE is_active = 1
                    ORDER BY nama
                """)
                penyedia_list = cursor.fetchall()
                
                for p in penyedia_list:
                    self.cmb_penyedia.addItem(f"{p[1]}", {
                        'id': p[0],
                        'nama': p[1],
                        'direktur': p[2] or '',
                        'alamat': p[3] or '',
                        'npwp': p[4] or '',
                        'rekening': p[5] or '',
                        'bank': p[6] or '',
                        'kota': p[7] or ''
                    })
        except Exception as e:
            print(f"Error loading penyedia list: {e}")
    
    def on_penyedia_selected(self, index):
        """Fill form when penyedia selected from dropdown"""
        penyedia_data = self.cmb_penyedia.currentData()
        if penyedia_data and isinstance(penyedia_data, dict):
            self.txt_penyedia_nama.setText(penyedia_data.get('nama', ''))
            self.txt_direktur_nama.setText(penyedia_data.get('direktur', ''))
            self.txt_penyedia_alamat.setText(penyedia_data.get('alamat', ''))
            self.txt_penyedia_npwp.setText(penyedia_data.get('npwp', ''))
            self.txt_penyedia_rekening.setText(penyedia_data.get('rekening', ''))
            self.txt_penyedia_bank.setText(penyedia_data.get('bank', ''))
            self.txt_penyedia_bank_cabang.setText(penyedia_data.get('kota', ''))
    
    def load_penyedia_from_db(self):
        """Load penyedia data from paket"""
        if not self.paket:
            return
        
        # Try to get penyedia from paket data
        penyedia = self.paket.get('penyedia_data', {})
        if isinstance(penyedia, str):
            import json
            try:
                penyedia = json.loads(penyedia)
            except:
                penyedia = {}
        
        if penyedia:
            self.txt_penyedia_nama.setText(penyedia.get('nama', ''))
            self.txt_direktur_nama.setText(penyedia.get('direktur', ''))
            self.txt_penyedia_alamat.setText(penyedia.get('alamat', ''))
            self.txt_penyedia_npwp.setText(penyedia.get('npwp', ''))
            self.txt_penyedia_rekening.setText(penyedia.get('rekening', ''))
            self.txt_penyedia_bank.setText(penyedia.get('bank', ''))
            self.txt_penyedia_bank_cabang.setText(penyedia.get('bank_cabang', ''))
    
    def save_penyedia_to_paket(self):
        """Save penyedia data to paket"""
        import json
        penyedia_data = {
            'nama': self.txt_penyedia_nama.text(),
            'direktur': self.txt_direktur_nama.text(),
            'alamat': self.txt_penyedia_alamat.text(),
            'npwp': self.txt_penyedia_npwp.text(),
            'rekening': self.txt_penyedia_rekening.text(),
            'bank': self.txt_penyedia_bank.text(),
            'bank_cabang': self.txt_penyedia_bank_cabang.text(),
        }
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE paket SET penyedia_data = ? WHERE id = ?
                """, (json.dumps(penyedia_data), self.paket_id))
                conn.commit()
            
            QMessageBox.information(self, "Sukses", "Data penyedia berhasil disimpan!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal menyimpan: {str(e)}")
    
    def load_satker_data(self):
        """Load satker and pejabat data"""
        # Load from config default
        self.txt_kementerian.setText(SATKER_DEFAULT.get('kementerian', ''))
        self.txt_eselon1.setText(SATKER_DEFAULT.get('eselon1', ''))
        self.txt_satker_nama.setText(SATKER_DEFAULT.get('nama', ''))
        self.txt_satker_alamat.setText(SATKER_DEFAULT.get('alamat', ''))
        self.txt_satker_kota.setText(SATKER_DEFAULT.get('kota', ''))
        self.txt_satker_telepon.setText(SATKER_DEFAULT.get('telepon', ''))
        
        # Load PPK from paket assignment
        if self.paket:
            ppk = self.db.get_paket_pejabat(self.paket_id, 'PPK')
            if ppk:
                self.txt_ppk_nama.setText(ppk.get('nama', ''))
                self.txt_ppk_nip.setText(ppk.get('nip', ''))
            
            pp = self.db.get_paket_pejabat(self.paket_id, 'PP')
            if pp:
                self.txt_pp_nama.setText(pp.get('nama', ''))
                self.txt_pp_nip.setText(pp.get('nip', ''))
    
    def get_additional_data(self) -> dict:
        """Collect all additional data for document generation"""
        data = {}
        
        # Document-specific dates and nomor
        for doc_type, entry in self.doc_entries.items():
            date_val = entry['date'].date()
            data[f'tanggal_{doc_type.lower()}'] = date(date_val.year(), date_val.month(), date_val.day())
            data[f'tanggal_{doc_type.lower()}_fmt'] = date_val.toString("d MMMM yyyy")
            
            nomor = entry['nomor'].text().strip()
            if nomor:
                data[f'nomor_{doc_type.lower()}_override'] = nomor
        
        # Penyedia data
        data['penyedia_nama'] = self.txt_penyedia_nama.text()
        data['direktur_nama'] = self.txt_direktur_nama.text()
        data['penyedia_alamat'] = self.txt_penyedia_alamat.text()
        data['penyedia_npwp'] = self.txt_penyedia_npwp.text()
        data['penyedia_rekening'] = self.txt_penyedia_rekening.text()
        data['penyedia_bank'] = self.txt_penyedia_bank.text()
        data['penyedia_bank_cabang'] = self.txt_penyedia_bank_cabang.text()
        
        # Satker data
        data['kementerian'] = self.txt_kementerian.text()
        data['eselon1'] = self.txt_eselon1.text()
        data['satker_nama'] = self.txt_satker_nama.text()
        data['satker_alamat'] = self.txt_satker_alamat.text()
        data['satker_kota'] = self.txt_satker_kota.text()
        data['satker_telepon'] = self.txt_satker_telepon.text()
        
        # Pejabat data
        data['ppk_nama'] = self.txt_ppk_nama.text()
        data['ppk_nip'] = self.txt_ppk_nip.text()
        data['pp_nama'] = self.txt_pp_nama.text()
        data['pp_nip'] = self.txt_pp_nip.text()
        
        return data
    
    def generate_documents(self):
        """Generate selected documents with full error handling"""
        print("[DEBUG] generate_documents started")
        
        try:
            # Get selected documents
            selected = [dt for dt, entry in self.doc_entries.items() if entry['checkbox'].isChecked()]
            print(f"[DEBUG] Selected: {selected}")
            
            if not selected:
                QMessageBox.warning(self, "Peringatan", "Pilih minimal satu dokumen!")
                return
            
            # Validate required data
            if not self.txt_penyedia_nama.text().strip():
                reply = QMessageBox.question(
                    self, "Data Penyedia Kosong",
                    "Data penyedia belum diisi. Lanjutkan generate?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    self.tabs.setCurrentIndex(1)  # Switch to penyedia tab
                    return
            
            # Get additional data
            additional_data = self.get_additional_data()
            print(f"[DEBUG] Additional data collected")
            
            self.progress.setMaximum(len(selected))
            self.progress.setValue(0)
            self.progress.show()
            self.results_list.clear()
            self.results_list.show()
            self.btn_generate.setEnabled(False)
            
            QApplication.processEvents()
            
            results = []
            for i, doc_type in enumerate(selected):
                print(f"[DEBUG] Processing: {doc_type}")
                try:
                    # Get document-specific date
                    entry = self.doc_entries[doc_type]
                    date_val = entry['date'].date()
                    doc_date = date(date_val.year(), date_val.month(), date_val.day())
                    
                    # Add document date to additional data
                    additional_data[f'tanggal_{doc_type.lower()}'] = doc_date
                    
                    # Check for nomor override
                    nomor_override = entry['nomor'].text().strip() or None
                    
                    filepath, nomor = self.workflow.generate_document(
                        self.paket_id, doc_type, 
                        additional_data=additional_data,
                        force=True
                    )
                    print(f"[DEBUG] Generated: {filepath}")
                    results.append((doc_type, filepath, nomor))
                    
                    item = QListWidgetItem(f"✅ {doc_type}: {nomor}")
                    item.setForeground(QColor("#27ae60"))
                    self.results_list.addItem(item)
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    results.append((doc_type, None, str(e)))
                    
                    item = QListWidgetItem(f"❌ {doc_type}: {str(e)}")
                    item.setForeground(QColor("#e74c3c"))
                    self.results_list.addItem(item)
                
                self.progress.setValue(i + 1)
                QApplication.processEvents()
            
            # Complete stage if all success
            all_success = all(r[1] is not None for r in results)
            if all_success:
                self.workflow.complete_stage(self.paket_id, self.stage_code)
            
            self.btn_generate.setEnabled(True)
            self.btn_open_folder.show()
            
            QMessageBox.information(
                self, "Selesai",
                f"Proses selesai!\n"
                f"Berhasil: {sum(1 for r in results if r[1])}\n"
                f"Gagal: {sum(1 for r in results if not r[1])}"
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.btn_generate.setEnabled(True)
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan:\n{str(e)}")
    
    def open_output_folder(self):
        paket = self.db.get_paket(self.paket_id)
        if not paket:
            return
        
        import re
        paket_folder = f"{paket['kode']}_{paket['nama'][:30]}"
        paket_folder = re.sub(r'[<>:"/\\|?*]', '_', paket_folder)
        
        folder_path = os.path.join(OUTPUT_DIR, str(TAHUN_ANGGARAN), paket_folder)
        
        if os.path.exists(folder_path):
            if sys.platform == 'win32':
                os.startfile(folder_path)
            elif sys.platform == 'darwin':
                os.system(f'open "{folder_path}"')
            else:
                os.system(f'xdg-open "{folder_path}"')
        else:
            QMessageBox.warning(self, "Folder tidak ditemukan", f"Folder output belum ada:\n{folder_path}")


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

class DashboardWindow(QMainWindow):
    """Main Dashboard Window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PPK Document Factory v3.0 - {SATKER_DEFAULT['nama_pendek']} - TA {TAHUN_ANGGARAN}")
        self.setMinimumSize(1400, 900)
        
        self.db = get_db_manager()
        self.workflow = get_workflow_engine()
        self.template_manager = get_template_manager()
        
        self.current_paket_id = None
        
        self.setup_ui()
        self.setStyleSheet(STYLE_SHEET)
        
        self.load_paket_list()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Left panel - Paket list
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_layout = QHBoxLayout()
        lbl_paket = QLabel("📋 Daftar Paket")
        lbl_paket.setObjectName("titleLabel")
        header_layout.addWidget(lbl_paket)
        header_layout.addStretch()
        
        btn_add_paket = QPushButton("➕ Tambah")
        btn_add_paket.clicked.connect(self.add_paket)
        header_layout.addWidget(btn_add_paket)
        
        left_layout.addLayout(header_layout)
        
        # Search
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Cari paket...")
        self.txt_search.textChanged.connect(self.filter_paket_list)
        left_layout.addWidget(self.txt_search)
        
        # Paket list
        self.paket_list = QListWidget()
        self.paket_list.itemClicked.connect(self.on_paket_selected)
        left_layout.addWidget(self.paket_list)
        
        main_layout.addWidget(left_panel)
        
        # Right panel - Workflow
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Paket info header
        self.paket_info_group = QGroupBox("Informasi Paket")
        paket_info_layout = QGridLayout()
        
        self.lbl_paket_nama = QLabel("-")
        self.lbl_paket_nama.setFont(QFont("", 14, QFont.Bold))
        paket_info_layout.addWidget(QLabel("Nama:"), 0, 0)
        paket_info_layout.addWidget(self.lbl_paket_nama, 0, 1, 1, 3)
        
        self.lbl_paket_nilai = QLabel("-")
        paket_info_layout.addWidget(QLabel("Nilai Kontrak:"), 1, 0)
        paket_info_layout.addWidget(self.lbl_paket_nilai, 1, 1)
        
        self.lbl_paket_penyedia = QLabel("-")
        paket_info_layout.addWidget(QLabel("Penyedia:"), 1, 2)
        paket_info_layout.addWidget(self.lbl_paket_penyedia, 1, 3)
        
        self.progress_workflow = QProgressBar()
        self.progress_workflow.setFormat("%p% Selesai")
        paket_info_layout.addWidget(QLabel("Progress:"), 2, 0)
        paket_info_layout.addWidget(self.progress_workflow, 2, 1, 1, 3)
        
        # Action buttons row 1
        btn_edit = QPushButton("✏️ Edit Paket")
        btn_edit.clicked.connect(self.edit_paket)
        paket_info_layout.addWidget(btn_edit, 3, 0)
        
        btn_items = QPushButton("📦 Daftar Item")
        btn_items.setToolTip("Kelola Daftar Kebutuhan Barang / Bill of Quantity")
        btn_items.clicked.connect(self.open_item_barang_manager)
        paket_info_layout.addWidget(btn_items, 3, 1)
        
        btn_timeline = QPushButton("📅 Timeline")
        btn_timeline.setToolTip("Kelola Tanggal & Penomoran Dokumen")
        btn_timeline.clicked.connect(self.open_timeline_manager)
        paket_info_layout.addWidget(btn_timeline, 3, 2)
        
        btn_open = QPushButton("📂 Buka Folder")
        btn_open.clicked.connect(self.open_paket_folder)
        paket_info_layout.addWidget(btn_open, 3, 3)
        
        # Row 4: Pejabat & Harga
        btn_pejabat = QPushButton("👥 Pejabat & Tim")
        btn_pejabat.setToolTip("Tetapkan PPK, PPSPM, Bendahara, Tim PPHP")
        btn_pejabat.clicked.connect(self.open_paket_pejabat)
        paket_info_layout.addWidget(btn_pejabat, 4, 0)
        
        btn_harga = QPushButton("💰 Lifecycle Harga")
        btn_harga.setToolTip("Kelola Survey → HPS → Kontrak")
        btn_harga.clicked.connect(self.open_harga_lifecycle)
        paket_info_layout.addWidget(btn_harga, 4, 1)
        
        btn_survey = QPushButton("🏪 Survey Toko")
        btn_survey.setToolTip("Data Toko/Sumber Survey Harga")
        btn_survey.clicked.connect(self.open_survey_toko_manager)
        paket_info_layout.addWidget(btn_survey, 4, 2)

        # Checklist SPJ button
        btn_checklist = QPushButton("📋 Checklist SPJ")
        btn_checklist.setToolTip("Checklist Kelengkapan Dokumen Pertanggungjawaban")
        btn_checklist.setStyleSheet("background-color: #27ae60;")
        btn_checklist.clicked.connect(self.open_checklist_spj)
        paket_info_layout.addWidget(btn_checklist, 5, 0)

        # Foto Dokumentasi button
        btn_foto = QPushButton("📷 Foto BAHP")
        btn_foto.setToolTip("Upload Foto Dokumentasi dengan GPS Tagging")
        btn_foto.setStyleSheet("background-color: #9b59b6;")
        btn_foto.clicked.connect(lambda: self.open_foto_dokumentasi('BAHP'))
        paket_info_layout.addWidget(btn_foto, 5, 1)

        # Open folder button
        btn_folder = QPushButton("📁 Folder")
        btn_folder.setToolTip("Buka folder output paket")
        btn_folder.clicked.connect(self.open_paket_folder)
        paket_info_layout.addWidget(btn_folder, 5, 2)

        # Action buttons row 3 - Generate All
        btn_batch = QPushButton("🚀 Generate Semua Dokumen")
        btn_batch.setObjectName("btnSuccess")
        btn_batch.clicked.connect(self.generate_all_pending)
        paket_info_layout.addWidget(btn_batch, 6, 0, 1, 3)
        
        self.paket_info_group.setLayout(paket_info_layout)
        right_layout.addWidget(self.paket_info_group)
        
        # Workflow stages
        workflow_group = QGroupBox("Workflow Pengadaan")
        workflow_layout = QVBoxLayout()
        
        # Stage widgets in grid
        self.stage_grid = QGridLayout()
        self.stage_widgets = {}
        
        for i, stage in enumerate(WORKFLOW_STAGES):
            widget = StageWidget(stage['code'], stage['name'])
            widget.clicked.connect(self.on_stage_clicked)
            self.stage_widgets[stage['code']] = widget
            
            row = i // 5
            col = i % 5
            self.stage_grid.addWidget(widget, row, col)
        
        workflow_layout.addLayout(self.stage_grid)
        
        # Documents list
        self.doc_tree = QTreeWidget()
        self.doc_tree.setHeaderLabels(["Dokumen", "Nomor", "Tanggal", "Status"])
        self.doc_tree.setMinimumHeight(200)
        workflow_layout.addWidget(self.doc_tree)
        
        workflow_group.setLayout(workflow_layout)
        right_layout.addWidget(workflow_group)
        
        main_layout.addWidget(right_panel)
        
        # Status bar
        self.statusBar().showMessage(f"📁 Output: {OUTPUT_DIR}")
        
        # Menu bar
        self.setup_menu()
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        action_new = QAction("&Paket Baru", self)
        action_new.setShortcut("Ctrl+N")
        action_new.triggered.connect(self.add_paket)
        file_menu.addAction(action_new)
        
        file_menu.addSeparator()
        
        action_exit = QAction("&Keluar", self)
        action_exit.setShortcut("Ctrl+Q")
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)
        
        # Master Data menu
        master_menu = menubar.addMenu("&Master Data")
        
        action_pegawai = QAction("👥 Data Pegawai", self)
        action_pegawai.setShortcut("Ctrl+P")
        action_pegawai.triggered.connect(self.open_pegawai_manager)
        master_menu.addAction(action_pegawai)
        
        action_penyedia = QAction("🏢 Data Penyedia", self)
        action_penyedia.triggered.connect(self.open_penyedia_manager)
        master_menu.addAction(action_penyedia)
        
        master_menu.addSeparator()
        
        action_satker = QAction("🏛️ Data Satker", self)
        action_satker.triggered.connect(self.open_satker_manager)
        master_menu.addAction(action_satker)

        master_menu.addSeparator()

        # Backup/Restore
        action_backup = QAction("💾 Backup Master Data", self)
        action_backup.triggered.connect(self.backup_master_data)
        master_menu.addAction(action_backup)

        action_restore = QAction("📂 Restore Master Data", self)
        action_restore.triggered.connect(self.restore_master_data)
        master_menu.addAction(action_restore)

        # Perjalanan Dinas menu
        pd_menu = menubar.addMenu("&Perjalanan Dinas")

        action_pd_buat = QAction("✈️ Buat Perjalanan Dinas Baru", self)
        action_pd_buat.triggered.connect(self.create_perjalanan_dinas)
        pd_menu.addAction(action_pd_buat)

        action_pd_list = QAction("📋 Daftar Perjalanan Dinas", self)
        action_pd_list.triggered.connect(self.list_perjalanan_dinas)
        pd_menu.addAction(action_pd_list)

        pd_menu.addSeparator()

        action_pd_surat_tugas = QAction("📄 Cetak Surat Tugas", self)
        action_pd_surat_tugas.triggered.connect(lambda: self.generate_pd_doc('SURAT_TUGAS'))
        pd_menu.addAction(action_pd_surat_tugas)

        action_pd_sppd = QAction("📄 Cetak SPPD", self)
        action_pd_sppd.triggered.connect(lambda: self.generate_pd_doc('SPPD'))
        pd_menu.addAction(action_pd_sppd)

        action_pd_kuitansi_um = QAction("💰 Cetak Kuitansi Uang Muka", self)
        action_pd_kuitansi_um.triggered.connect(lambda: self.generate_pd_doc('KUITANSI_UM'))
        pd_menu.addAction(action_pd_kuitansi_um)

        action_pd_rincian = QAction("📊 Cetak Rincian Biaya", self)
        action_pd_rincian.triggered.connect(lambda: self.generate_pd_doc('RINCIAN_BIAYA_PD'))
        pd_menu.addAction(action_pd_rincian)

        action_pd_kuitansi_rampung = QAction("💰 Cetak Kuitansi Rampung", self)
        action_pd_kuitansi_rampung.triggered.connect(lambda: self.generate_pd_doc('KUITANSI_RAMPUNG'))
        pd_menu.addAction(action_pd_kuitansi_rampung)

        # Swakelola menu
        sw_menu = menubar.addMenu("&Swakelola")

        action_sw_buat = QAction("📝 Buat Kegiatan Swakelola Baru", self)
        action_sw_buat.triggered.connect(self.create_swakelola)
        sw_menu.addAction(action_sw_buat)

        action_sw_list = QAction("📋 Daftar Kegiatan Swakelola", self)
        action_sw_list.triggered.connect(self.list_swakelola)
        sw_menu.addAction(action_sw_list)

        sw_menu.addSeparator()

        action_sw_kak = QAction("📄 Cetak KAK Swakelola", self)
        action_sw_kak.triggered.connect(lambda: self.generate_sw_doc('KAK_SWAKELOLA'))
        sw_menu.addAction(action_sw_kak)

        action_sw_rab = QAction("📊 Cetak RAB Swakelola", self)
        action_sw_rab.triggered.connect(lambda: self.generate_sw_doc('RAB_SWAKELOLA'))
        sw_menu.addAction(action_sw_rab)

        action_sw_sk_tim = QAction("📄 Cetak SK Tim", self)
        action_sw_sk_tim.triggered.connect(lambda: self.generate_sw_doc('SK_TIM_SWAKELOLA'))
        sw_menu.addAction(action_sw_sk_tim)

        action_sw_bap = QAction("📄 Cetak BA Pembayaran", self)
        action_sw_bap.triggered.connect(lambda: self.generate_sw_doc('BAP_SWAKELOLA'))
        sw_menu.addAction(action_sw_bap)

        action_sw_laporan = QAction("📄 Cetak Laporan Kemajuan", self)
        action_sw_laporan.triggered.connect(lambda: self.generate_sw_doc('LAPORAN_KEMAJUAN'))
        sw_menu.addAction(action_sw_laporan)

        action_sw_bast = QAction("📄 Cetak BAST Swakelola", self)
        action_sw_bast.triggered.connect(lambda: self.generate_sw_doc('BAST_SWAKELOLA'))
        sw_menu.addAction(action_sw_bast)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        action_templates = QAction("📄 Template Manager", self)
        action_templates.triggered.connect(self.open_template_manager)
        tools_menu.addAction(action_templates)
        
        tools_menu.addSeparator()
        
        action_import_csv = QAction("📥 Import Pegawai dari CSV", self)
        action_import_csv.triggered.connect(self.import_pegawai_csv)
        tools_menu.addAction(action_import_csv)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        action_about = QAction("&Tentang", self)
        action_about.triggered.connect(self.show_about)
        help_menu.addAction(action_about)
    
    def load_paket_list(self):
        self.paket_list.clear()
        
        paket_list = self.db.get_paket_list(tahun=TAHUN_ANGGARAN)
        
        for paket in paket_list:
            # Status indicator
            status_icon = {
                'draft': '📝',
                'in_progress': '🔄',
                'completed': '✅',
                'cancelled': '❌'
            }.get(paket.get('status', 'draft'), '📝')
            
            item = QListWidgetItem(f"{status_icon} {paket['kode']}\n{paket['nama'][:40]}...")
            item.setData(Qt.UserRole, paket['id'])
            self.paket_list.addItem(item)
    
    def filter_paket_list(self, text: str):
        for i in range(self.paket_list.count()):
            item = self.paket_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def on_paket_selected(self, item: QListWidgetItem):
        paket_id = item.data(Qt.UserRole)
        self.current_paket_id = paket_id
        self.load_paket_detail(paket_id)
    
    def load_paket_detail(self, paket_id: int):
        paket = self.db.get_paket(paket_id)
        if not paket:
            return
        
        # Update info
        self.lbl_paket_nama.setText(paket['nama'])
        self.lbl_paket_nilai.setText(format_rupiah(paket.get('nilai_kontrak', 0)))
        self.lbl_paket_penyedia.setText(paket.get('penyedia_nama', '-'))
        
        # Load workflow
        overview = self.workflow.get_workflow_overview(paket_id)
        
        self.progress_workflow.setValue(int(overview['progress']))
        
        # Update stage widgets
        for stage_info in overview['stages']:
            widget = self.stage_widgets.get(stage_info.code)
            if widget:
                widget.set_status(
                    stage_info.status.value,
                    stage_info.is_current,
                    stage_info.is_allowed
                )
        
        # Load documents
        self.doc_tree.clear()
        
        for stage_info in overview['stages']:
            if stage_info.documents:
                stage_item = QTreeWidgetItem([stage_info.name, "", "", ""])
                stage_item.setExpanded(True)
                
                for doc in stage_info.documents:
                    doc_item = QTreeWidgetItem([
                        doc['doc_type'],
                        doc.get('nomor', '-'),
                        str(doc.get('tanggal', '-')),
                        doc.get('status', 'draft')
                    ])
                    doc_item.setData(0, Qt.UserRole, doc.get('filepath'))
                    stage_item.addChild(doc_item)
                
                self.doc_tree.addTopLevelItem(stage_item)
        
        self.doc_tree.expandAll()
    
    def on_stage_clicked(self, stage_code: str):
        if not self.current_paket_id:
            return
        
        dialog = GenerateDocumentDialog(self.current_paket_id, stage_code, self)
        if dialog.exec():
            self.load_paket_detail(self.current_paket_id)
            self.load_paket_list()
    
    def add_paket(self):
        dialog = PaketFormDialog(parent=self)
        if dialog.exec():
            self.load_paket_list()
            
            # Select the new paket
            for i in range(self.paket_list.count()):
                item = self.paket_list.item(i)
                if item.data(Qt.UserRole) == dialog.paket_id:
                    self.paket_list.setCurrentItem(item)
                    self.on_paket_selected(item)
                    break
    
    def edit_paket(self):
        if not self.current_paket_id:
            QMessageBox.warning(self, "Peringatan", "Pilih paket terlebih dahulu!")
            return
        
        dialog = PaketFormDialog(self.current_paket_id, self)
        if dialog.exec():
            self.load_paket_list()
            self.load_paket_detail(self.current_paket_id)
    
    def open_item_barang_manager(self):
        """Open Item Barang / Bill of Quantity Manager"""
        if not self.current_paket_id:
            QMessageBox.warning(self, "Peringatan", "Pilih paket terlebih dahulu!")
            return
        
        dialog = ItemBarangManager(self.current_paket_id, self)
        dialog.items_changed.connect(lambda: self.load_paket_detail(self.current_paket_id))
        dialog.exec()
    
    def open_timeline_manager(self):
        """Open Timeline / Document Numbering Manager"""
        if not self.current_paket_id:
            QMessageBox.warning(self, "Peringatan", "Pilih paket terlebih dahulu!")
            return
        
        from app.ui.timeline_manager import TimelineManager
        dialog = TimelineManager(self.current_paket_id, self)
        dialog.timeline_changed.connect(lambda: self.load_paket_detail(self.current_paket_id))
        dialog.exec()
    
    def open_survey_toko_manager(self):
        """Open Survey Toko Manager"""
        if not self.current_paket_id:
            QMessageBox.warning(self, "Peringatan", "Pilih paket terlebih dahulu!")
            return

        try:
            from app.ui.survey_toko_manager import SurveyTokoManager
            dialog = SurveyTokoManager(self.current_paket_id, self)
            dialog.data_changed.connect(lambda: self.load_paket_detail(self.current_paket_id))
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")

    def open_checklist_spj(self):
        """Open Checklist SPJ / Kelengkapan Dokumen Manager"""
        if not self.current_paket_id:
            QMessageBox.warning(self, "Peringatan", "Pilih paket terlebih dahulu!")
            return

        try:
            from app.ui.checklist_spj_manager import ChecklistDialog
            dialog = ChecklistDialog(self.current_paket_id, self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")

    def open_foto_dokumentasi(self, jenis: str = 'BAHP'):
        """Open Foto Dokumentasi Manager untuk BAHP/BAST"""
        if not self.current_paket_id:
            QMessageBox.warning(self, "Peringatan", "Pilih paket terlebih dahulu!")
            return

        try:
            from app.ui.foto_dokumentasi_manager import FotoDokumentasiDialog
            dialog = FotoDokumentasiDialog(self.current_paket_id, jenis, self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")

    def open_paket_folder(self):
        if not self.current_paket_id:
            return
        
        paket = self.db.get_paket(self.current_paket_id)
        if not paket:
            return
        
        import re
        paket_folder = f"{paket['kode']}_{paket['nama'][:30]}"
        paket_folder = re.sub(r'[<>:"/\\|?*]', '_', paket_folder)
        
        folder_path = os.path.join(OUTPUT_DIR, str(TAHUN_ANGGARAN), paket_folder)
        os.makedirs(folder_path, exist_ok=True)
        
        if sys.platform == 'win32':
            os.startfile(folder_path)
        elif sys.platform == 'darwin':
            os.system(f'open "{folder_path}"')
        else:
            os.system(f'xdg-open "{folder_path}"')
    
    def generate_all_pending(self):
        if not self.current_paket_id:
            QMessageBox.warning(self, "Peringatan", "Pilih paket terlebih dahulu!")
            return
        
        reply = QMessageBox.question(
            self, "Konfirmasi",
            "Generate semua dokumen yang belum selesai?\n"
            "Proses akan dimulai dari stage pertama yang belum selesai.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        overview = self.workflow.get_workflow_overview(self.current_paket_id)
        
        for stage_info in overview['stages']:
            if stage_info.status == StageStatus.PENDING and stage_info.is_allowed:
                dialog = GenerateDocumentDialog(self.current_paket_id, stage_info.code, self)
                dialog.exec()
        
        self.load_paket_detail(self.current_paket_id)
        self.load_paket_list()
    
    def open_template_manager(self):
        from .template_manager import TemplateManagerDialog
        dialog = TemplateManagerDialog(self)
        dialog.exec()
    
    def open_pegawai_manager(self):
        """Open Master Data Pegawai"""
        try:
            from .pegawai_manager import PegawaiManager
            dialog = PegawaiManager(self)
            dialog.pegawai_changed.connect(self.load_paket_list)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")
    
    def open_penyedia_manager(self):
        """Open Master Data Penyedia"""
        try:
            from .penyedia_manager import PenyediaManager
            dialog = PenyediaManager(self)
            dialog.penyedia_changed.connect(self.load_paket_list)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")

    def open_satker_manager(self):
        """Open Master Data Satker"""
        try:
            from .satker_manager import SatkerManager
            dialog = SatkerManager(self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")
    
    def import_pegawai_csv(self):
        """Import pegawai from CSV file"""
        try:
            from .pegawai_manager import PegawaiManager
            dialog = PegawaiManager(self)
            dialog.import_csv()
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")
    
    def open_paket_pejabat(self):
        """Open Paket Pejabat Manager"""
        if not self.current_paket_id:
            QMessageBox.warning(self, "Peringatan", "Pilih paket terlebih dahulu!")
            return
        
        try:
            from .paket_pejabat_manager import PaketPejabatManager
            dialog = PaketPejabatManager(self.current_paket_id, self)
            dialog.pejabat_changed.connect(lambda: self.load_paket_detail(self.current_paket_id))
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")
    
    def open_harga_lifecycle(self):
        """Open Harga Lifecycle Manager"""
        if not self.current_paket_id:
            QMessageBox.warning(self, "Peringatan", "Pilih paket terlebih dahulu!")
            return
        
        try:
            from .harga_lifecycle_manager import HargaLifecycleManager
            dialog = HargaLifecycleManager(self.current_paket_id, self)
            dialog.data_changed.connect(lambda: self.load_paket_detail(self.current_paket_id))
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")
    
    def open_master_data(self):
        """Open Master Data (legacy - redirect to pegawai)"""
        self.open_pegawai_manager()

    def backup_master_data(self):
        """Backup all master data to JSON file"""
        from PySide6.QtWidgets import QFileDialog
        from datetime import datetime

        default_name = f"backup_master_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Backup Master Data",
            default_name,
            "JSON Files (*.json)"
        )

        if not filepath:
            return

        try:
            if self.db.backup_master_data(filepath):
                QMessageBox.information(
                    self, "Sukses",
                    f"Backup master data berhasil disimpan ke:\n{filepath}"
                )
            else:
                QMessageBox.warning(self, "Error", "Gagal membuat backup!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal backup:\n{str(e)}")

    def restore_master_data(self):
        """Restore master data from JSON backup file"""
        from PySide6.QtWidgets import QFileDialog

        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Restore Master Data",
            "",
            "JSON Files (*.json)"
        )

        if not filepath:
            return

        reply = QMessageBox.question(
            self, "Konfirmasi Restore",
            "Restore master data dari backup?\n\n"
            "Data yang sudah ada akan diupdate jika NIP/NPWP sama.\n"
            "Data baru akan ditambahkan.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            success_msg, errors = self.db.restore_master_data(filepath)
            if success_msg:
                msg = f"Restore berhasil!\n\n{success_msg}"
                if errors:
                    msg += f"\n\nError:\n" + "\n".join(errors[:5])
                QMessageBox.information(self, "Restore Selesai", msg)
            else:
                QMessageBox.warning(
                    self, "Restore Gagal",
                    "Tidak ada data yang berhasil di-restore.\n\n" + "\n".join(errors)
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal restore:\n{str(e)}")

    def create_perjalanan_dinas(self):
        """Create new Perjalanan Dinas"""
        try:
            from .perjalanan_dinas_manager import PerjalananDinasDialog
            dialog = PerjalananDinasDialog(parent=self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")

    def list_perjalanan_dinas(self):
        """List all Perjalanan Dinas"""
        try:
            from .perjalanan_dinas_manager import PerjalananDinasManager
            dialog = PerjalananDinasManager(self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")

    def generate_pd_doc(self, doc_type: str):
        """Generate Perjalanan Dinas document"""
        # Open manager to select and generate
        try:
            from .perjalanan_dinas_manager import PerjalananDinasManager
            dialog = PerjalananDinasManager(self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")

    def create_swakelola(self):
        """Create new Swakelola activity"""
        try:
            from .swakelola_manager import SwakelolaDialog
            dialog = SwakelolaDialog(parent=self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")

    def list_swakelola(self):
        """List all Swakelola activities"""
        try:
            from .swakelola_manager import SwakelolaManager
            dialog = SwakelolaManager(self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")

    def generate_sw_doc(self, doc_type: str):
        """Generate Swakelola document"""
        # Open manager to select and generate
        try:
            from .swakelola_manager import SwakelolaManager
            dialog = SwakelolaManager(self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Module tidak tersedia:\n{str(e)}")

    def show_about(self):
        QMessageBox.about(
            self, "Tentang",
            "PPK Document Factory v3.0\n\n"
            "Template-Driven Procurement Workflow System\n\n"
            "Fitur:\n"
            "• Workflow pengadaan lengkap\n"
            "• Template Word/Excel yang dapat diedit\n"
            "• Penomoran otomatis\n"
            "• Output terorganisir per paket\n\n"
            f"© {TAHUN_ANGGARAN} PPK Digital Assistant"
        )


# ============================================================================
# MAIN
# ============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = DashboardWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
