"""
UP Form Page - Form input transaksi Uang Persediaan baru
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QDoubleSpinBox, QComboBox, QDateEdit, QMessageBox, QGroupBox,
    QSpinBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QIntValidator
from typing import Optional
from datetime import datetime

from app.models.pencairan_models import get_pencairan_manager
from app.config.workflow_config import JENIS_BELANJA, BATAS_UP_MAKSIMAL
from app.templates.engine import format_rupiah


class UPFormPage(QWidget):
    """Form untuk membuat transaksi UP baru"""
    
    transaksi_created = Signal(int)  # transaksi_id
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pencairan_mgr = get_pencairan_manager()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI untuk form"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        btn_back = QPushButton("← Kembali")
        btn_back.setFixedWidth(100)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_back.clicked.connect(self.back_requested.emit)
        
        title = QLabel("📋 BUAT TRANSAKSI UP BARU")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        
        header_layout.addWidget(btn_back)
        header_layout.addWidget(title, 1)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Scroll area untuk form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        form_container = QWidget()
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # ===== BAGIAN 1: INFORMASI KEGIATAN =====
        group1 = QGroupBox("1️⃣ INFORMASI KEGIATAN")
        group1_layout = QVBoxLayout()
        group1_layout.setSpacing(12)
        
        # Nama kegiatan
        label_nama = QLabel("Nama Kegiatan *")
        label_nama.setFont(self._get_label_font())
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Contoh: Workshop Python Programming")
        self.input_nama.setMinimumHeight(35)
        group1_layout.addWidget(label_nama)
        group1_layout.addWidget(self.input_nama)
        
        # Jenis belanja
        label_jenis = QLabel("Jenis Belanja *")
        label_jenis.setFont(self._get_label_font())
        self.combo_jenis = QComboBox()
        self.combo_jenis.setMinimumHeight(35)
        
        jenis_items = [f"{item['icon']} {item['nama']}" for item in JENIS_BELANJA]
        self.combo_jenis.addItems(jenis_items)
        self.jenis_belanja_codes = [item['kode'] for item in JENIS_BELANJA]
        
        group1_layout.addWidget(label_jenis)
        group1_layout.addWidget(self.combo_jenis)
        
        # Row: Estimasi biaya & Info Batas
        biaya_row_layout = QHBoxLayout()
        biaya_row_layout.setSpacing(20)
        
        biaya_col = QVBoxLayout()
        biaya_col.setSpacing(8)
        
        label_biaya = QLabel("Estimasi Biaya *")
        label_biaya.setFont(self._get_label_font())
        
        self.spin_biaya = QDoubleSpinBox()
        self.spin_biaya.setRange(0, BATAS_UP_MAKSIMAL)
        self.spin_biaya.setValue(0)
        self.spin_biaya.setSingleStep(100000)
        self.spin_biaya.setMinimumHeight(35)
        self.spin_biaya.setSuffix(" Rp")
        self.spin_biaya.setLocale(__import__('locale').getlocale())
        self.spin_biaya.valueChanged.connect(self.on_biaya_changed)
        
        biaya_col.addWidget(label_biaya)
        biaya_col.addWidget(self.spin_biaya)
        
        # Info batas
        info_col = QVBoxLayout()
        info_col.setSpacing(8)
        info_col.addSpacing(25)
        
        self.label_batas = QLabel(
            f"⚠️ Batas maksimal UP: {format_rupiah(BATAS_UP_MAKSIMAL)}\n"
            f"Sisa tersedia: {format_rupiah(BATAS_UP_MAKSIMAL)}"
        )
        info_font = QFont()
        info_font.setPointSize(8)
        self.label_batas.setFont(info_font)
        self.label_batas.setStyleSheet("color: #27ae60;")
        info_col.addWidget(self.label_batas)
        
        biaya_row_layout.addLayout(biaya_col, 1)
        biaya_row_layout.addLayout(info_col, 1)
        
        group1_layout.addLayout(biaya_row_layout)
        
        group1.setLayout(group1_layout)
        form_layout.addWidget(group1)
        
        # ===== BAGIAN 2: DASAR HUKUM =====
        group2 = QGroupBox("2️⃣ DASAR HUKUM / SK KPA")
        group2_layout = QVBoxLayout()
        group2_layout.setSpacing(12)
        
        # Jenis dasar
        label_jenis_dasar = QLabel("Jenis Dasar Hukum *")
        label_jenis_dasar.setFont(self._get_label_font())
        self.combo_jenis_dasar = QComboBox()
        self.combo_jenis_dasar.setMinimumHeight(35)
        self.combo_jenis_dasar.addItems([
            "SK KPA",
            "Surat Tugas",
            "Nota Dinas",
            "Keputusan Pimpinan"
        ])
        group2_layout.addWidget(label_jenis_dasar)
        group2_layout.addWidget(self.combo_jenis_dasar)
        
        # Row: Nomor & Tanggal
        row_layout = QHBoxLayout()
        row_layout.setSpacing(20)
        
        # Nomor
        col_nomor = QVBoxLayout()
        col_nomor.setSpacing(8)
        label_nomor = QLabel("Nomor SK *")
        label_nomor.setFont(self._get_label_font())
        self.input_nomor = QLineEdit()
        self.input_nomor.setPlaceholderText("Contoh: SK-KPA/HRM/001/2026")
        self.input_nomor.setMinimumHeight(35)
        col_nomor.addWidget(label_nomor)
        col_nomor.addWidget(self.input_nomor)
        
        # Tanggal
        col_tanggal = QVBoxLayout()
        col_tanggal.setSpacing(8)
        label_tanggal = QLabel("Tanggal SK *")
        label_tanggal.setFont(self._get_label_font())
        self.date_sk = QDateEdit()
        self.date_sk.setDate(QDate.currentDate())
        self.date_sk.setMinimumHeight(35)
        col_tanggal.addWidget(label_tanggal)
        col_tanggal.addWidget(self.date_sk)
        
        row_layout.addLayout(col_nomor, 1)
        row_layout.addLayout(col_tanggal, 1)
        
        group2_layout.addLayout(row_layout)
        
        group2.setLayout(group2_layout)
        form_layout.addWidget(group2)
        
        # ===== BAGIAN 3: PENERIMA DANA =====
        group3 = QGroupBox("3️⃣ DATA PENERIMA DANA")
        group3_layout = QVBoxLayout()
        group3_layout.setSpacing(12)
        
        # Nama penerima
        label_penerima = QLabel("Nama Penerima *")
        label_penerima.setFont(self._get_label_font())
        self.input_penerima_nama = QLineEdit()
        self.input_penerima_nama.setPlaceholderText("Contoh: Budi Santoso, S.P.")
        self.input_penerima_nama.setMinimumHeight(35)
        group3_layout.addWidget(label_penerima)
        group3_layout.addWidget(self.input_penerima_nama)
        
        # Row: NIP & Jabatan
        row_penerima = QHBoxLayout()
        row_penerima.setSpacing(20)
        
        # NIP
        col_nip = QVBoxLayout()
        col_nip.setSpacing(8)
        label_nip = QLabel("NIP Penerima *")
        label_nip.setFont(self._get_label_font())
        self.input_penerima_nip = QLineEdit()
        self.input_penerima_nip.setPlaceholderText("Contoh: 19800115200801001")
        self.input_penerima_nip.setMinimumHeight(35)
        col_nip.addWidget(label_nip)
        col_nip.addWidget(self.input_penerima_nip)
        
        # Jabatan
        col_jabatan = QVBoxLayout()
        col_jabatan.setSpacing(8)
        label_jabatan = QLabel("Jabatan Penerima *")
        label_jabatan.setFont(self._get_label_font())
        self.input_penerima_jabatan = QLineEdit()
        self.input_penerima_jabatan.setPlaceholderText("Contoh: Narasumber, Moderator")
        self.input_penerima_jabatan.setMinimumHeight(35)
        col_jabatan.addWidget(label_jabatan)
        col_jabatan.addWidget(self.input_penerima_jabatan)
        
        row_penerima.addLayout(col_nip, 1)
        row_penerima.addLayout(col_jabatan, 1)
        
        group3_layout.addLayout(row_penerima)
        
        group3.setLayout(group3_layout)
        form_layout.addWidget(group3)
        
        # ===== BAGIAN 4: KODE AKUN / DIPA =====
        group4 = QGroupBox("4️⃣ KODE AKUN / DIPA")
        group4_layout = QVBoxLayout()
        group4_layout.setSpacing(12)
        
        # Kode akun
        label_kode = QLabel("Kode Akun (MAK) *")
        label_kode.setFont(self._get_label_font())
        self.input_kode_akun = QLineEdit()
        self.input_kode_akun.setPlaceholderText("Contoh: 5.2.1.01.01")
        self.input_kode_akun.setMinimumHeight(35)
        group4_layout.addWidget(label_kode)
        group4_layout.addWidget(self.input_kode_akun)
        
        # Nama akun
        label_nama_akun = QLabel("Nama Akun")
        label_nama_akun.setFont(self._get_label_font())
        self.input_nama_akun = QLineEdit()
        self.input_nama_akun.setPlaceholderText("Otomatis dari kode akun atau isikan manual")
        self.input_nama_akun.setMinimumHeight(35)
        group4_layout.addWidget(label_nama_akun)
        group4_layout.addWidget(self.input_nama_akun)
        
        group4.setLayout(group4_layout)
        form_layout.addWidget(group4)
        
        # ===== BAGIAN 5: TANGGAL KEGIATAN =====
        group5 = QGroupBox("5️⃣ TANGGAL KEGIATAN")
        group5_layout = QVBoxLayout()
        group5_layout.setSpacing(12)
        
        row_tgl = QHBoxLayout()
        row_tgl.setSpacing(20)
        
        # Tanggal mulai
        col_mulai = QVBoxLayout()
        col_mulai.setSpacing(8)
        label_mulai = QLabel("Tanggal Mulai Kegiatan")
        label_mulai.setFont(self._get_label_font())
        self.date_mulai = QDateEdit()
        self.date_mulai.setDate(QDate.currentDate())
        self.date_mulai.setMinimumHeight(35)
        col_mulai.addWidget(label_mulai)
        col_mulai.addWidget(self.date_mulai)
        
        # Tanggal selesai
        col_selesai = QVBoxLayout()
        col_selesai.setSpacing(8)
        label_selesai = QLabel("Tanggal Selesai Kegiatan")
        label_selesai.setFont(self._get_label_font())
        self.date_selesai = QDateEdit()
        self.date_selesai.setDate(QDate.currentDate())
        self.date_selesai.setMinimumHeight(35)
        col_selesai.addWidget(label_selesai)
        col_selesai.addWidget(self.date_selesai)
        
        row_tgl.addLayout(col_mulai, 1)
        row_tgl.addLayout(col_selesai, 1)
        
        group5_layout.addLayout(row_tgl)
        
        group5.setLayout(group5_layout)
        form_layout.addWidget(group5)
        
        form_layout.addStretch()
        form_container.setLayout(form_layout)
        scroll.setWidget(form_container)
        
        layout.addWidget(scroll, 1)
        
        # ===== ACTION BUTTONS =====
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        btn_reset = QPushButton("🔄 Reset")
        btn_reset.setFixedWidth(100)
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_reset.clicked.connect(self.reset_form)
        
        btn_simpan = QPushButton("💾 Buat Transaksi UP")
        btn_simpan.setFixedWidth(200)
        btn_simpan.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_simpan.clicked.connect(self.on_simpan_clicked)
        
        action_layout.addWidget(btn_reset)
        action_layout.addStretch()
        action_layout.addWidget(btn_simpan)
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
    
    def _get_label_font(self) -> QFont:
        """Get font untuk label"""
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        return font
    
    def on_biaya_changed(self, value: float):
        """Handle biaya changed - check saldo"""
        # TODO: Check saldo UP tersedia dari database
        saldo_tersedia = BATAS_UP_MAKSIMAL
        
        if value > BATAS_UP_MAKSIMAL:
            self.label_batas.setText(
                f"❌ Estimasi biaya melebihi batas maksimal UP!\n"
                f"Maksimal: {format_rupiah(BATAS_UP_MAKSIMAL)}"
            )
            self.label_batas.setStyleSheet("color: #e74c3c;")
        else:
            sisa = saldo_tersedia - value
            self.label_batas.setText(
                f"✓ Estimasi biaya sesuai\n"
                f"Sisa saldo UP: {format_rupiah(sisa)}"
            )
            self.label_batas.setStyleSheet("color: #27ae60;")
    
    def reset_form(self):
        """Reset form ke state awal"""
        self.input_nama.clear()
        self.combo_jenis.setCurrentIndex(0)
        self.spin_biaya.setValue(0)
        self.combo_jenis_dasar.setCurrentIndex(0)
        self.input_nomor.clear()
        self.date_sk.setDate(QDate.currentDate())
        self.input_penerima_nama.clear()
        self.input_penerima_nip.clear()
        self.input_penerima_jabatan.clear()
        self.input_kode_akun.clear()
        self.input_nama_akun.clear()
        self.date_mulai.setDate(QDate.currentDate())
        self.date_selesai.setDate(QDate.currentDate())
    
    def validate_form(self) -> tuple[bool, str]:
        """Validasi form sebelum submit"""
        
        # Nama kegiatan
        if not self.input_nama.text().strip():
            return False, "Nama kegiatan wajib diisi"
        
        # Estimasi biaya
        if self.spin_biaya.value() <= 0:
            return False, "Estimasi biaya harus lebih dari 0"
        
        if self.spin_biaya.value() > BATAS_UP_MAKSIMAL:
            return False, f"Estimasi biaya tidak boleh melebihi {format_rupiah(BATAS_UP_MAKSIMAL)}"
        
        # Nomor SK
        if not self.input_nomor.text().strip():
            return False, "Nomor SK/Surat Tugas wajib diisi"
        
        # Nama penerima
        if not self.input_penerima_nama.text().strip():
            return False, "Nama penerima wajib diisi"
        
        # NIP penerima
        if not self.input_penerima_nip.text().strip():
            return False, "NIP penerima wajib diisi"
        
        # Jabatan penerima
        if not self.input_penerima_jabatan.text().strip():
            return False, "Jabatan penerima wajib diisi"
        
        # Kode akun
        if not self.input_kode_akun.text().strip():
            return False, "Kode akun wajib diisi"
        
        return True, ""
    
    def on_simpan_clicked(self):
        """Handle simpan button clicked"""
        ok, msg = self.validate_form()
        
        if not ok:
            QMessageBox.warning(self, "Validasi Form", msg)
            return
        
        try:
            # Prepare data
            jenis_belanja_idx = self.combo_jenis.currentIndex()
            jenis_belanja_code = self.jenis_belanja_codes[jenis_belanja_idx]
            
            data = {
                'mekanisme': 'UP',
                'jenis_belanja': jenis_belanja_code,
                'nama_kegiatan': self.input_nama.text().strip(),
                'estimasi_biaya': self.spin_biaya.value(),
                'jenis_dasar': self.combo_jenis_dasar.currentText(),
                'nomor_dasar': self.input_nomor.text().strip(),
                'tanggal_dasar': self.date_sk.date().toString('yyyy-MM-dd'),
                'penerima_nama': self.input_penerima_nama.text().strip(),
                'penerima_nip': self.input_penerima_nip.text().strip(),
                'penerima_jabatan': self.input_penerima_jabatan.text().strip(),
                'kode_akun': self.input_kode_akun.text().strip(),
                'nama_akun': self.input_nama_akun.text().strip() or 'Auto',
                'tanggal_kegiatan_mulai': self.date_mulai.date().toString('yyyy-MM-dd'),
                'tanggal_kegiatan_selesai': self.date_selesai.date().toString('yyyy-MM-dd'),
            }
            
            # Create transaksi
            transaksi_id = self.pencairan_mgr.create_transaksi(data)
            
            QMessageBox.information(
                self,
                "Sukses",
                f"Transaksi UP berhasil dibuat!\n\n"
                f"Kode: {self.pencairan_mgr.get_transaksi(transaksi_id)['kode_transaksi']}\n\n"
                f"Anda dapat mulai menambahkan dokumen di tahap Inisiasi."
            )
            
            self.transaksi_created.emit(transaksi_id)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Gagal membuat transaksi UP:\n\n{str(e)}"
            )
