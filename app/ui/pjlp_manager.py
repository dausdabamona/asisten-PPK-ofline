"""
PPK DOCUMENT FACTORY - PJLP Manager
====================================
Manager untuk Penyedia Jasa Lainnya Perorangan (PJLP) dengan:
- Input data kontrak PJLP
- Monitoring pelaksanaan bulanan
- Pembayaran honor bulanan
- Generate dokumen kuitansi
"""

import os
import sys
from datetime import datetime, date
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QMessageBox, QCheckBox, QFrame, QSplitter, QTabWidget,
    QAbstractItemView, QMenu, QFileDialog, QDateEdit, QSpinBox,
    QDoubleSpinBox, QScrollArea, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QDate, QLocale
from PySide6.QtGui import QAction, QColor

from app.core.database_v4 import get_db_manager_v4
from app.core.config import SATKER_DEFAULT, TAHUN_ANGGARAN, OUTPUT_DIR


# ============================================================================
# CUSTOM CURRENCY SPINBOX WITH THOUSAND SEPARATOR
# ============================================================================

class CurrencySpinBox(QDoubleSpinBox):
    """Custom SpinBox for Indonesian currency with thousand separator"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 999999999999)
        self.setDecimals(0)
        self.setSingleStep(100000)

        # Use Indonesian locale for thousand separator
        locale = QLocale(QLocale.Indonesian, QLocale.Indonesia)
        self.setLocale(locale)

    def textFromValue(self, value: float) -> str:
        """Format value with thousand separator"""
        return f"Rp {value:,.0f}".replace(",", ".")

    def valueFromText(self, text: str) -> float:
        """Parse text to value"""
        # Remove "Rp " prefix and thousand separators
        clean = text.replace("Rp ", "").replace(".", "").replace(",", "").strip()
        try:
            return float(clean) if clean else 0
        except ValueError:
            return 0

    def validate(self, text: str, pos: int):
        """Validate input"""
        return QDoubleSpinBox.validate(self, text, pos)


# ============================================================================
# PJLP DIALOG (Add/Edit Contract)
# ============================================================================

class PJLPDialog(QDialog):
    """Dialog for adding/editing PJLP contract"""

    def __init__(self, pjlp_data: dict = None, parent=None):
        super().__init__(parent)
        self.pjlp_data = pjlp_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Tambah Kontrak PJLP" if not pjlp_data else "Edit Kontrak PJLP")
        self.setMinimumWidth(800)
        self.setMinimumHeight(700)
        self.setup_ui()

        if pjlp_data:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Scroll area for long form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Tab widget
        tabs = QTabWidget()

        # ========== TAB 1: DATA PJLP ==========
        tab_pjlp = QWidget()
        form1 = QVBoxLayout(tab_pjlp)

        # Info Dasar
        info_group = QGroupBox("Informasi Kontrak")
        info_form = QFormLayout()

        self.spn_tahun = QSpinBox()
        self.spn_tahun.setRange(2020, 2050)
        self.spn_tahun.setValue(TAHUN_ANGGARAN)
        info_form.addRow("Tahun Anggaran:", self.spn_tahun)

        self.txt_nama_pekerjaan = QLineEdit()
        self.txt_nama_pekerjaan.setPlaceholderText("Tenaga Kebersihan / Tenaga Keamanan / dll")
        info_form.addRow("Nama Pekerjaan:", self.txt_nama_pekerjaan)

        # Nomor Kontrak
        nomor_layout = QHBoxLayout()
        self.txt_nomor_kontrak = QLineEdit()
        self.txt_nomor_kontrak.setPlaceholderText("SPK-PJLP-001/2024")
        nomor_layout.addWidget(self.txt_nomor_kontrak)
        nomor_layout.addWidget(QLabel("Tanggal:"))
        self.date_kontrak = QDateEdit()
        self.date_kontrak.setCalendarPopup(True)
        self.date_kontrak.setDate(QDate.currentDate())
        nomor_layout.addWidget(self.date_kontrak)
        info_form.addRow("Nomor Kontrak:", nomor_layout)

        # Sumber Dana
        dana_layout = QHBoxLayout()
        self.cmb_sumber_dana = QComboBox()
        self.cmb_sumber_dana.addItems(["DIPA", "BLU", "PNBP", "BOPTN", "Lainnya"])
        dana_layout.addWidget(self.cmb_sumber_dana)
        dana_layout.addWidget(QLabel("Kode Akun:"))
        self.txt_kode_akun = QLineEdit()
        self.txt_kode_akun.setPlaceholderText("522151")
        dana_layout.addWidget(self.txt_kode_akun)
        info_form.addRow("Sumber Dana:", dana_layout)

        info_group.setLayout(info_form)
        form1.addWidget(info_group)

        # Data Penyedia
        penyedia_group = QGroupBox("Data Penyedia Jasa")
        penyedia_form = QFormLayout()

        self.txt_nama_pjlp = QLineEdit()
        self.txt_nama_pjlp.setPlaceholderText("Nama lengkap penyedia jasa")
        penyedia_form.addRow("Nama PJLP:", self.txt_nama_pjlp)

        id_layout = QHBoxLayout()
        self.txt_nik = QLineEdit()
        self.txt_nik.setPlaceholderText("3201234567890001")
        id_layout.addWidget(QLabel("NIK:"))
        id_layout.addWidget(self.txt_nik)
        self.txt_npwp = QLineEdit()
        self.txt_npwp.setPlaceholderText("01.234.567.8-901.000")
        id_layout.addWidget(QLabel("NPWP:"))
        id_layout.addWidget(self.txt_npwp)
        penyedia_form.addRow("Identitas:", id_layout)

        self.txt_alamat = QTextEdit()
        self.txt_alamat.setMaximumHeight(60)
        self.txt_alamat.setPlaceholderText("Alamat lengkap sesuai KTP")
        penyedia_form.addRow("Alamat:", self.txt_alamat)

        kontak_layout = QHBoxLayout()
        self.txt_telepon = QLineEdit()
        self.txt_telepon.setPlaceholderText("081234567890")
        kontak_layout.addWidget(QLabel("Telepon:"))
        kontak_layout.addWidget(self.txt_telepon)
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("email@contoh.com")
        kontak_layout.addWidget(QLabel("Email:"))
        kontak_layout.addWidget(self.txt_email)
        penyedia_form.addRow("Kontak:", kontak_layout)

        # Bank
        bank_layout = QHBoxLayout()
        self.txt_nama_bank = QLineEdit()
        self.txt_nama_bank.setPlaceholderText("Bank BRI")
        bank_layout.addWidget(QLabel("Bank:"))
        bank_layout.addWidget(self.txt_nama_bank)
        self.txt_no_rekening = QLineEdit()
        self.txt_no_rekening.setPlaceholderText("1234567890")
        bank_layout.addWidget(QLabel("No. Rekening:"))
        bank_layout.addWidget(self.txt_no_rekening)
        penyedia_form.addRow("Rekening:", bank_layout)

        penyedia_group.setLayout(penyedia_form)
        form1.addWidget(penyedia_group)

        # Periode dan Nilai
        periode_group = QGroupBox("Periode dan Nilai Kontrak")
        periode_form = QFormLayout()

        # Periode
        periode_layout = QHBoxLayout()
        self.date_mulai = QDateEdit()
        self.date_mulai.setCalendarPopup(True)
        self.date_mulai.setDate(QDate(TAHUN_ANGGARAN, 1, 1))
        periode_layout.addWidget(QLabel("Mulai:"))
        periode_layout.addWidget(self.date_mulai)
        self.date_selesai = QDateEdit()
        self.date_selesai.setCalendarPopup(True)
        self.date_selesai.setDate(QDate(TAHUN_ANGGARAN, 12, 31))
        periode_layout.addWidget(QLabel("Selesai:"))
        periode_layout.addWidget(self.date_selesai)
        self.spn_jangka_waktu = QSpinBox()
        self.spn_jangka_waktu.setRange(1, 12)
        self.spn_jangka_waktu.setValue(12)
        self.spn_jangka_waktu.setSuffix(" bulan")
        periode_layout.addWidget(self.spn_jangka_waktu)
        periode_form.addRow("Periode:", periode_layout)

        # Nilai
        nilai_layout = QHBoxLayout()
        self.spn_honor_bulanan = CurrencySpinBox()
        nilai_layout.addWidget(QLabel("Honor/Bulan:"))
        nilai_layout.addWidget(self.spn_honor_bulanan)
        self.spn_total_kontrak = CurrencySpinBox()
        nilai_layout.addWidget(QLabel("Total Kontrak:"))
        nilai_layout.addWidget(self.spn_total_kontrak)
        periode_form.addRow("Nilai:", nilai_layout)

        # Auto calculate total
        self.spn_honor_bulanan.valueChanged.connect(self.calculate_total)
        self.spn_jangka_waktu.valueChanged.connect(self.calculate_total)

        periode_group.setLayout(periode_form)
        form1.addWidget(periode_group)

        form1.addStretch()
        tabs.addTab(tab_pjlp, "Data Kontrak")

        # ========== TAB 2: PEJABAT ==========
        tab_pejabat = QWidget()
        form2 = QVBoxLayout(tab_pejabat)

        # PPK
        ppk_group = QGroupBox("Pejabat Pembuat Komitmen (PPK)")
        ppk_form = QFormLayout()

        self.txt_ppk_nama = QLineEdit()
        self.txt_ppk_nama.setText(SATKER_DEFAULT.get('ppk_nama', ''))
        ppk_form.addRow("Nama PPK:", self.txt_ppk_nama)

        self.txt_ppk_nip = QLineEdit()
        self.txt_ppk_nip.setText(SATKER_DEFAULT.get('ppk_nip', ''))
        ppk_form.addRow("NIP:", self.txt_ppk_nip)

        self.txt_ppk_jabatan = QLineEdit()
        self.txt_ppk_jabatan.setText(SATKER_DEFAULT.get('ppk_jabatan', 'Pejabat Pembuat Komitmen'))
        ppk_form.addRow("Jabatan:", self.txt_ppk_jabatan)

        ppk_group.setLayout(ppk_form)
        form2.addWidget(ppk_group)

        # Bendahara
        bendahara_group = QGroupBox("Bendahara Pengeluaran")
        bendahara_form = QFormLayout()

        self.txt_bendahara_nama = QLineEdit()
        self.txt_bendahara_nama.setText(SATKER_DEFAULT.get('bendahara_nama', ''))
        bendahara_form.addRow("Nama:", self.txt_bendahara_nama)

        self.txt_bendahara_nip = QLineEdit()
        self.txt_bendahara_nip.setText(SATKER_DEFAULT.get('bendahara_nip', ''))
        bendahara_form.addRow("NIP:", self.txt_bendahara_nip)

        bendahara_group.setLayout(bendahara_form)
        form2.addWidget(bendahara_group)

        # Status
        status_group = QGroupBox("Status Kontrak")
        status_form = QFormLayout()

        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["aktif", "selesai", "dibatalkan"])
        status_form.addRow("Status:", self.cmb_status)

        status_group.setLayout(status_form)
        form2.addWidget(status_group)

        form2.addStretch()
        tabs.addTab(tab_pejabat, "Pejabat")

        scroll_layout.addWidget(tabs)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Batal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Simpan")
        btn_save.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 20px;")
        btn_save.clicked.connect(self.save_data)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def calculate_total(self):
        """Calculate total contract value"""
        honor = self.spn_honor_bulanan.value()
        bulan = self.spn_jangka_waktu.value()
        self.spn_total_kontrak.setValue(honor * bulan)

    def load_data(self):
        """Load existing PJLP data"""
        d = self.pjlp_data

        self.spn_tahun.setValue(d.get('tahun_anggaran', TAHUN_ANGGARAN))
        self.txt_nama_pekerjaan.setText(d.get('nama_pekerjaan', ''))
        self.txt_nomor_kontrak.setText(d.get('nomor_kontrak', ''))

        if d.get('tanggal_kontrak'):
            self.date_kontrak.setDate(QDate.fromString(str(d['tanggal_kontrak']), 'yyyy-MM-dd'))

        self.cmb_sumber_dana.setCurrentText(d.get('sumber_dana', 'DIPA'))
        self.txt_kode_akun.setText(d.get('kode_akun', ''))

        self.txt_nama_pjlp.setText(d.get('nama_pjlp', ''))
        self.txt_nik.setText(d.get('nik', ''))
        self.txt_npwp.setText(d.get('npwp', ''))
        self.txt_alamat.setPlainText(d.get('alamat', ''))
        self.txt_telepon.setText(d.get('telepon', ''))
        self.txt_email.setText(d.get('email', ''))
        self.txt_nama_bank.setText(d.get('nama_bank', ''))
        self.txt_no_rekening.setText(d.get('no_rekening', ''))

        if d.get('tanggal_mulai'):
            self.date_mulai.setDate(QDate.fromString(str(d['tanggal_mulai']), 'yyyy-MM-dd'))
        if d.get('tanggal_selesai'):
            self.date_selesai.setDate(QDate.fromString(str(d['tanggal_selesai']), 'yyyy-MM-dd'))

        self.spn_jangka_waktu.setValue(d.get('jangka_waktu', 12))
        self.spn_honor_bulanan.setValue(d.get('honor_bulanan', 0))
        self.spn_total_kontrak.setValue(d.get('total_nilai_kontrak', 0))

        self.txt_ppk_nama.setText(d.get('ppk_nama', ''))
        self.txt_ppk_nip.setText(d.get('ppk_nip', ''))
        self.txt_ppk_jabatan.setText(d.get('ppk_jabatan', ''))
        self.txt_bendahara_nama.setText(d.get('bendahara_nama', ''))
        self.txt_bendahara_nip.setText(d.get('bendahara_nip', ''))

        self.cmb_status.setCurrentText(d.get('status', 'aktif'))

    def save_data(self):
        """Save PJLP data"""
        if not self.txt_nama_pjlp.text().strip():
            QMessageBox.warning(self, "Peringatan", "Nama PJLP harus diisi!")
            return

        if not self.txt_nama_pekerjaan.text().strip():
            QMessageBox.warning(self, "Peringatan", "Nama Pekerjaan harus diisi!")
            return

        data = {
            'tahun_anggaran': self.spn_tahun.value(),
            'nomor_kontrak': self.txt_nomor_kontrak.text(),
            'tanggal_kontrak': self.date_kontrak.date().toString('yyyy-MM-dd'),
            'nama_pekerjaan': self.txt_nama_pekerjaan.text(),
            'nama_pjlp': self.txt_nama_pjlp.text(),
            'nik': self.txt_nik.text(),
            'npwp': self.txt_npwp.text(),
            'alamat': self.txt_alamat.toPlainText(),
            'telepon': self.txt_telepon.text(),
            'email': self.txt_email.text(),
            'no_rekening': self.txt_no_rekening.text(),
            'nama_bank': self.txt_nama_bank.text(),
            'tanggal_mulai': self.date_mulai.date().toString('yyyy-MM-dd'),
            'tanggal_selesai': self.date_selesai.date().toString('yyyy-MM-dd'),
            'jangka_waktu': self.spn_jangka_waktu.value(),
            'honor_bulanan': self.spn_honor_bulanan.value(),
            'total_nilai_kontrak': self.spn_total_kontrak.value(),
            'sumber_dana': self.cmb_sumber_dana.currentText(),
            'kode_akun': self.txt_kode_akun.text(),
            'ppk_nama': self.txt_ppk_nama.text(),
            'ppk_nip': self.txt_ppk_nip.text(),
            'ppk_jabatan': self.txt_ppk_jabatan.text(),
            'bendahara_nama': self.txt_bendahara_nama.text(),
            'bendahara_nip': self.txt_bendahara_nip.text(),
            'status': self.cmb_status.currentText()
        }

        try:
            if self.pjlp_data:
                self.db.update_pjlp(self.pjlp_data['id'], data)
            else:
                self.db.create_pjlp(data)

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data: {str(e)}")


# ============================================================================
# PEMBAYARAN PJLP DIALOG
# ============================================================================

class PembayaranPJLPDialog(QDialog):
    """Dialog for adding/editing monthly payment"""

    BULAN_NAMES = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    def __init__(self, pjlp_data: dict, payment_data: dict = None, parent=None):
        super().__init__(parent)
        self.pjlp_data = pjlp_data
        self.payment_data = payment_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Tambah Pembayaran" if not payment_data else "Edit Pembayaran")
        self.setMinimumWidth(600)
        self.setup_ui()

        if payment_data:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header info
        header = QLabel(f"<b>{self.pjlp_data.get('nama_pjlp', '')}</b><br>"
                        f"{self.pjlp_data.get('nama_pekerjaan', '')}")
        header.setStyleSheet("background: #ecf0f1; padding: 10px; border-radius: 5px;")
        layout.addWidget(header)

        # Form
        form = QFormLayout()

        # Bulan & Tahun
        periode_layout = QHBoxLayout()
        self.cmb_bulan = QComboBox()
        for i, b in enumerate(self.BULAN_NAMES):
            self.cmb_bulan.addItem(b, i + 1)
        current_month = datetime.now().month
        self.cmb_bulan.setCurrentIndex(current_month - 1)
        periode_layout.addWidget(self.cmb_bulan)

        self.spn_tahun = QSpinBox()
        self.spn_tahun.setRange(2020, 2050)
        self.spn_tahun.setValue(self.pjlp_data.get('tahun_anggaran', TAHUN_ANGGARAN))
        periode_layout.addWidget(self.spn_tahun)
        form.addRow("Periode:", periode_layout)

        # Nomor Kuitansi
        kuitansi_layout = QHBoxLayout()
        self.txt_nomor_kuitansi = QLineEdit()
        self.txt_nomor_kuitansi.setPlaceholderText("KU-PJLP-001/2024")
        kuitansi_layout.addWidget(self.txt_nomor_kuitansi)
        kuitansi_layout.addWidget(QLabel("Tanggal:"))
        self.date_kuitansi = QDateEdit()
        self.date_kuitansi.setCalendarPopup(True)
        self.date_kuitansi.setDate(QDate.currentDate())
        kuitansi_layout.addWidget(self.date_kuitansi)
        form.addRow("Kuitansi:", kuitansi_layout)

        # Nomor SPP
        spp_layout = QHBoxLayout()
        self.txt_nomor_spp = QLineEdit()
        self.txt_nomor_spp.setPlaceholderText("SPP-PJLP-001/2024")
        spp_layout.addWidget(self.txt_nomor_spp)
        spp_layout.addWidget(QLabel("Tanggal:"))
        self.date_spp = QDateEdit()
        self.date_spp.setCalendarPopup(True)
        self.date_spp.setDate(QDate.currentDate())
        spp_layout.addWidget(self.date_spp)
        form.addRow("SPP:", spp_layout)

        # Kehadiran
        kehadiran_layout = QHBoxLayout()
        self.spn_kehadiran = QSpinBox()
        self.spn_kehadiran.setRange(0, 31)
        self.spn_kehadiran.setValue(22)
        kehadiran_layout.addWidget(self.spn_kehadiran)
        kehadiran_layout.addWidget(QLabel("dari"))
        self.spn_total_hari = QSpinBox()
        self.spn_total_hari.setRange(1, 31)
        self.spn_total_hari.setValue(22)
        kehadiran_layout.addWidget(self.spn_total_hari)
        kehadiran_layout.addWidget(QLabel("hari kerja"))
        kehadiran_layout.addStretch()
        form.addRow("Kehadiran:", kehadiran_layout)

        # Nilai
        nilai_group = QGroupBox("Perhitungan Nilai")
        nilai_form = QFormLayout()

        self.spn_bruto = CurrencySpinBox()
        self.spn_bruto.setValue(self.pjlp_data.get('honor_bulanan', 0))
        nilai_form.addRow("Nilai Bruto:", self.spn_bruto)

        self.spn_pajak = CurrencySpinBox()
        nilai_form.addRow("Potongan Pajak:", self.spn_pajak)

        self.spn_potongan_lain = CurrencySpinBox()
        nilai_form.addRow("Potongan Lain:", self.spn_potongan_lain)

        self.spn_netto = CurrencySpinBox()
        self.spn_netto.setReadOnly(True)
        self.spn_netto.setStyleSheet("background-color: #ecf0f1;")
        nilai_form.addRow("Nilai Netto:", self.spn_netto)

        nilai_group.setLayout(nilai_form)
        form.addRow(nilai_group)

        # Auto calculate netto
        self.spn_bruto.valueChanged.connect(self.calculate_netto)
        self.spn_pajak.valueChanged.connect(self.calculate_netto)
        self.spn_potongan_lain.valueChanged.connect(self.calculate_netto)
        self.calculate_netto()

        # Catatan
        self.txt_catatan = QTextEdit()
        self.txt_catatan.setMaximumHeight(60)
        self.txt_catatan.setPlaceholderText("Catatan kinerja...")
        form.addRow("Catatan:", self.txt_catatan)

        # Status
        status_layout = QHBoxLayout()
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["draft", "diproses", "dibayar"])
        status_layout.addWidget(self.cmb_status)
        status_layout.addWidget(QLabel("Tgl Bayar:"))
        self.date_bayar = QDateEdit()
        self.date_bayar.setCalendarPopup(True)
        self.date_bayar.setDate(QDate.currentDate())
        status_layout.addWidget(self.date_bayar)
        form.addRow("Status:", status_layout)

        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Batal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Simpan")
        btn_save.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 20px;")
        btn_save.clicked.connect(self.save_data)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def calculate_netto(self):
        """Calculate netto value"""
        bruto = self.spn_bruto.value()
        pajak = self.spn_pajak.value()
        lain = self.spn_potongan_lain.value()
        self.spn_netto.setValue(bruto - pajak - lain)

    def load_data(self):
        """Load existing payment data"""
        d = self.payment_data

        bulan = d.get('bulan', 1) - 1
        self.cmb_bulan.setCurrentIndex(bulan)
        self.spn_tahun.setValue(d.get('tahun', TAHUN_ANGGARAN))

        self.txt_nomor_kuitansi.setText(d.get('nomor_kuitansi', ''))
        if d.get('tanggal_kuitansi'):
            self.date_kuitansi.setDate(QDate.fromString(str(d['tanggal_kuitansi']), 'yyyy-MM-dd'))

        self.txt_nomor_spp.setText(d.get('nomor_spp', ''))
        if d.get('tanggal_spp'):
            self.date_spp.setDate(QDate.fromString(str(d['tanggal_spp']), 'yyyy-MM-dd'))

        self.spn_kehadiran.setValue(d.get('kehadiran_hari', 22))
        self.spn_total_hari.setValue(d.get('total_hari_kerja', 22))

        self.spn_bruto.setValue(d.get('nilai_bruto', 0))
        self.spn_pajak.setValue(d.get('potongan_pajak', 0))
        self.spn_potongan_lain.setValue(d.get('potongan_lain', 0))

        self.txt_catatan.setPlainText(d.get('catatan_kinerja', ''))
        self.cmb_status.setCurrentText(d.get('status', 'draft'))

        if d.get('tanggal_bayar'):
            self.date_bayar.setDate(QDate.fromString(str(d['tanggal_bayar']), 'yyyy-MM-dd'))

    def save_data(self):
        """Save payment data"""
        data = {
            'pjlp_id': self.pjlp_data['id'],
            'bulan': self.cmb_bulan.currentData(),
            'tahun': self.spn_tahun.value(),
            'nomor_kuitansi': self.txt_nomor_kuitansi.text(),
            'tanggal_kuitansi': self.date_kuitansi.date().toString('yyyy-MM-dd'),
            'nomor_spp': self.txt_nomor_spp.text(),
            'tanggal_spp': self.date_spp.date().toString('yyyy-MM-dd'),
            'nilai_bruto': self.spn_bruto.value(),
            'potongan_pajak': self.spn_pajak.value(),
            'potongan_lain': self.spn_potongan_lain.value(),
            'nilai_netto': self.spn_netto.value(),
            'kehadiran_hari': self.spn_kehadiran.value(),
            'total_hari_kerja': self.spn_total_hari.value(),
            'catatan_kinerja': self.txt_catatan.toPlainText(),
            'status': self.cmb_status.currentText(),
            'tanggal_bayar': self.date_bayar.date().toString('yyyy-MM-dd') if self.cmb_status.currentText() == 'dibayar' else None
        }

        try:
            if self.payment_data:
                self.db.update_pembayaran_pjlp(self.payment_data['id'], data)
            else:
                self.db.create_pembayaran_pjlp(data)

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data: {str(e)}")


# ============================================================================
# PJLP MANAGER (Main Widget)
# ============================================================================

class PJLPManager(QWidget):
    """Main PJLP management widget with tabs"""

    BULAN_NAMES = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db_manager_v4()
        self.setup_ui()
        self.refresh_kontrak_list()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("PJLP Manager")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Tab widget
        self.tabs = QTabWidget()

        # ========== TAB 1: DAFTAR KONTRAK ==========
        tab_kontrak = QWidget()
        kontrak_layout = QVBoxLayout(tab_kontrak)

        # Toolbar
        toolbar = QHBoxLayout()

        btn_add = QPushButton("+ Tambah Kontrak PJLP")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        btn_add.clicked.connect(self.add_kontrak)
        toolbar.addWidget(btn_add)

        toolbar.addStretch()

        # Filter by year
        toolbar.addWidget(QLabel("Tahun:"))
        self.cmb_filter_tahun = QComboBox()
        self.cmb_filter_tahun.addItem("Semua", None)
        for y in range(TAHUN_ANGGARAN - 2, TAHUN_ANGGARAN + 3):
            self.cmb_filter_tahun.addItem(str(y), y)
        self.cmb_filter_tahun.setCurrentText(str(TAHUN_ANGGARAN))
        self.cmb_filter_tahun.currentIndexChanged.connect(self.refresh_kontrak_list)
        toolbar.addWidget(self.cmb_filter_tahun)

        # Filter by status
        toolbar.addWidget(QLabel("Status:"))
        self.cmb_filter_status = QComboBox()
        self.cmb_filter_status.addItem("Semua", None)
        self.cmb_filter_status.addItems(["aktif", "selesai", "dibatalkan"])
        self.cmb_filter_status.currentIndexChanged.connect(self.refresh_kontrak_list)
        toolbar.addWidget(self.cmb_filter_status)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.refresh_kontrak_list)
        toolbar.addWidget(btn_refresh)

        kontrak_layout.addLayout(toolbar)

        # Table
        self.tbl_kontrak = QTableWidget()
        self.tbl_kontrak.setColumnCount(8)
        self.tbl_kontrak.setHorizontalHeaderLabels([
            "ID", "Nama PJLP", "Pekerjaan", "No. Kontrak",
            "Honor/Bulan", "Periode", "Status", "Aksi"
        ])
        self.tbl_kontrak.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_kontrak.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_kontrak.horizontalHeader().setStretchLastSection(True)
        self.tbl_kontrak.setColumnWidth(0, 50)
        self.tbl_kontrak.setColumnWidth(1, 200)
        self.tbl_kontrak.setColumnWidth(2, 200)
        self.tbl_kontrak.setColumnWidth(3, 150)
        self.tbl_kontrak.setColumnWidth(4, 120)
        self.tbl_kontrak.setColumnWidth(5, 150)
        self.tbl_kontrak.setColumnWidth(6, 80)
        self.tbl_kontrak.doubleClicked.connect(self.edit_kontrak)
        kontrak_layout.addWidget(self.tbl_kontrak)

        self.tabs.addTab(tab_kontrak, "Daftar Kontrak")

        # ========== TAB 2: MONITORING PEMBAYARAN ==========
        tab_monitoring = QWidget()
        monitoring_layout = QVBoxLayout(tab_monitoring)

        # Filter
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Pilih PJLP:"))
        self.cmb_pjlp = QComboBox()
        self.cmb_pjlp.setMinimumWidth(300)
        self.cmb_pjlp.currentIndexChanged.connect(self.refresh_pembayaran)
        filter_layout.addWidget(self.cmb_pjlp)

        filter_layout.addStretch()

        btn_add_payment = QPushButton("+ Tambah Pembayaran")
        btn_add_payment.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #219a52; }
        """)
        btn_add_payment.clicked.connect(self.add_pembayaran)
        filter_layout.addWidget(btn_add_payment)

        monitoring_layout.addLayout(filter_layout)

        # Summary info
        self.lbl_summary = QLabel()
        self.lbl_summary.setStyleSheet("""
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        """)
        monitoring_layout.addWidget(self.lbl_summary)

        # Payment table
        self.tbl_pembayaran = QTableWidget()
        self.tbl_pembayaran.setColumnCount(8)
        self.tbl_pembayaran.setHorizontalHeaderLabels([
            "ID", "Bulan", "No. Kuitansi", "Nilai Bruto",
            "Potongan", "Nilai Netto", "Status", "Aksi"
        ])
        self.tbl_pembayaran.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_pembayaran.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_pembayaran.horizontalHeader().setStretchLastSection(True)
        self.tbl_pembayaran.doubleClicked.connect(self.edit_pembayaran)
        monitoring_layout.addWidget(self.tbl_pembayaran)

        # Progress bar
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progress Pembayaran:"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(12)
        progress_layout.addWidget(self.progress_bar)
        self.lbl_progress = QLabel("0/12 bulan")
        progress_layout.addWidget(self.lbl_progress)
        monitoring_layout.addLayout(progress_layout)

        self.tabs.addTab(tab_monitoring, "Monitoring Pembayaran")

        # ========== TAB 3: REKAP BULANAN ==========
        tab_rekap = QWidget()
        rekap_layout = QVBoxLayout(tab_rekap)

        # Filter
        rekap_filter = QHBoxLayout()
        rekap_filter.addWidget(QLabel("Bulan:"))
        self.cmb_rekap_bulan = QComboBox()
        for i, b in enumerate(self.BULAN_NAMES):
            self.cmb_rekap_bulan.addItem(b, i + 1)
        current_month = datetime.now().month
        self.cmb_rekap_bulan.setCurrentIndex(current_month - 1)
        rekap_filter.addWidget(self.cmb_rekap_bulan)

        rekap_filter.addWidget(QLabel("Tahun:"))
        self.spn_rekap_tahun = QSpinBox()
        self.spn_rekap_tahun.setRange(2020, 2050)
        self.spn_rekap_tahun.setValue(TAHUN_ANGGARAN)
        rekap_filter.addWidget(self.spn_rekap_tahun)

        btn_rekap = QPushButton("Tampilkan Rekap")
        btn_rekap.setStyleSheet("background-color: #3498db; color: white; padding: 8px 16px;")
        btn_rekap.clicked.connect(self.refresh_rekap)
        rekap_filter.addWidget(btn_rekap)

        rekap_filter.addStretch()
        rekap_layout.addLayout(rekap_filter)

        # Rekap table
        self.tbl_rekap = QTableWidget()
        self.tbl_rekap.setColumnCount(7)
        self.tbl_rekap.setHorizontalHeaderLabels([
            "Nama PJLP", "Pekerjaan", "Honor", "Nilai Bruto",
            "Potongan", "Nilai Netto", "Status"
        ])
        self.tbl_rekap.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_rekap.horizontalHeader().setStretchLastSection(True)
        rekap_layout.addWidget(self.tbl_rekap)

        # Total summary
        self.lbl_rekap_total = QLabel()
        self.lbl_rekap_total.setStyleSheet("""
            background: #d4edda;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
        """)
        rekap_layout.addWidget(self.lbl_rekap_total)

        self.tabs.addTab(tab_rekap, "Rekap Bulanan")

        layout.addWidget(self.tabs)

    def format_currency(self, value):
        """Format value as Indonesian currency"""
        return f"Rp {value:,.0f}".replace(",", ".")

    def refresh_kontrak_list(self):
        """Refresh contract list"""
        tahun = self.cmb_filter_tahun.currentData()
        status = self.cmb_filter_status.currentText()
        if status == "Semua":
            status = None

        contracts = self.db.get_all_pjlp(tahun=tahun, status=status)

        self.tbl_kontrak.setRowCount(len(contracts))

        # Also refresh PJLP combo in monitoring tab
        self.cmb_pjlp.clear()
        self.cmb_pjlp.addItem("-- Pilih PJLP --", None)

        for row, c in enumerate(contracts):
            self.tbl_kontrak.setItem(row, 0, QTableWidgetItem(str(c['id'])))
            self.tbl_kontrak.setItem(row, 1, QTableWidgetItem(c.get('nama_pjlp', '')))
            self.tbl_kontrak.setItem(row, 2, QTableWidgetItem(c.get('nama_pekerjaan', '')))
            self.tbl_kontrak.setItem(row, 3, QTableWidgetItem(c.get('nomor_kontrak', '')))
            self.tbl_kontrak.setItem(row, 4, QTableWidgetItem(self.format_currency(c.get('honor_bulanan', 0))))

            periode = f"{c.get('tanggal_mulai', '')} s/d {c.get('tanggal_selesai', '')}"
            self.tbl_kontrak.setItem(row, 5, QTableWidgetItem(periode))

            status_item = QTableWidgetItem(c.get('status', ''))
            if c.get('status') == 'aktif':
                status_item.setBackground(QColor('#d4edda'))
            elif c.get('status') == 'selesai':
                status_item.setBackground(QColor('#cce5ff'))
            else:
                status_item.setBackground(QColor('#f8d7da'))
            self.tbl_kontrak.setItem(row, 6, status_item)

            # Action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background: #3498db; color: white; padding: 2px 8px;")
            btn_edit.clicked.connect(lambda checked, r=row: self.edit_kontrak_by_row(r))
            btn_layout.addWidget(btn_edit)

            btn_del = QPushButton("Hapus")
            btn_del.setStyleSheet("background: #e74c3c; color: white; padding: 2px 8px;")
            btn_del.clicked.connect(lambda checked, r=row: self.delete_kontrak(r))
            btn_layout.addWidget(btn_del)

            self.tbl_kontrak.setCellWidget(row, 7, btn_widget)

            # Add to combo
            self.cmb_pjlp.addItem(f"{c['nama_pjlp']} - {c['nama_pekerjaan']}", c)

    def add_kontrak(self):
        """Add new PJLP contract"""
        dialog = PJLPDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_kontrak_list()
            QMessageBox.information(self, "Sukses", "Kontrak PJLP berhasil ditambahkan!")

    def edit_kontrak(self):
        """Edit selected contract"""
        row = self.tbl_kontrak.currentRow()
        if row >= 0:
            self.edit_kontrak_by_row(row)

    def edit_kontrak_by_row(self, row):
        """Edit contract by row number"""
        pjlp_id = int(self.tbl_kontrak.item(row, 0).text())
        pjlp_data = self.db.get_pjlp(pjlp_id)
        if pjlp_data:
            dialog = PJLPDialog(pjlp_data, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_kontrak_list()

    def delete_kontrak(self, row):
        """Delete contract"""
        pjlp_id = int(self.tbl_kontrak.item(row, 0).text())
        nama = self.tbl_kontrak.item(row, 1).text()

        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Yakin ingin menghapus kontrak PJLP:\n{nama}?\n\n"
            "Semua data pembayaran terkait juga akan dihapus!",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db.delete_pjlp(pjlp_id):
                self.refresh_kontrak_list()
                QMessageBox.information(self, "Sukses", "Kontrak berhasil dihapus!")
            else:
                QMessageBox.warning(self, "Gagal", "Gagal menghapus kontrak!")

    def refresh_pembayaran(self):
        """Refresh payment list for selected PJLP"""
        pjlp_data = self.cmb_pjlp.currentData()
        if not pjlp_data:
            self.tbl_pembayaran.setRowCount(0)
            self.lbl_summary.setText("Pilih PJLP untuk melihat data pembayaran")
            self.progress_bar.setValue(0)
            self.lbl_progress.setText("0/12 bulan")
            return

        # Update summary
        summary = self.db.get_pjlp_summary(pjlp_data['id'])
        total_bruto = summary.get('total_bruto', 0) or 0
        total_pajak = summary.get('total_pajak', 0) or 0
        total_netto = summary.get('total_netto', 0) or 0
        bulan_dibayar = summary.get('total_bulan_dibayar', 0) or 0

        self.lbl_summary.setText(
            f"<b>{pjlp_data.get('nama_pjlp', '')}</b> - {pjlp_data.get('nama_pekerjaan', '')}<br><br>"
            f"Honor/Bulan: {self.format_currency(pjlp_data.get('honor_bulanan', 0))} | "
            f"Total Kontrak: {self.format_currency(pjlp_data.get('total_nilai_kontrak', 0))}<br>"
            f"<span style='color: green'>Total Dibayar: {self.format_currency(total_netto)} "
            f"({bulan_dibayar} bulan)</span>"
        )

        # Update progress
        jangka_waktu = pjlp_data.get('jangka_waktu', 12)
        self.progress_bar.setMaximum(jangka_waktu)
        self.progress_bar.setValue(bulan_dibayar)
        self.lbl_progress.setText(f"{bulan_dibayar}/{jangka_waktu} bulan")

        # Get payments
        payments = self.db.get_pembayaran_by_pjlp(pjlp_data['id'])
        self.tbl_pembayaran.setRowCount(len(payments))

        for row, p in enumerate(payments):
            self.tbl_pembayaran.setItem(row, 0, QTableWidgetItem(str(p['id'])))

            bulan_idx = p.get('bulan', 1) - 1
            bulan_nama = self.BULAN_NAMES[bulan_idx] if 0 <= bulan_idx < 12 else ""
            self.tbl_pembayaran.setItem(row, 1, QTableWidgetItem(f"{bulan_nama} {p.get('tahun', '')}"))

            self.tbl_pembayaran.setItem(row, 2, QTableWidgetItem(p.get('nomor_kuitansi', '')))
            self.tbl_pembayaran.setItem(row, 3, QTableWidgetItem(self.format_currency(p.get('nilai_bruto', 0))))

            potongan = (p.get('potongan_pajak', 0) or 0) + (p.get('potongan_lain', 0) or 0)
            self.tbl_pembayaran.setItem(row, 4, QTableWidgetItem(self.format_currency(potongan)))
            self.tbl_pembayaran.setItem(row, 5, QTableWidgetItem(self.format_currency(p.get('nilai_netto', 0))))

            status_item = QTableWidgetItem(p.get('status', ''))
            if p.get('status') == 'dibayar':
                status_item.setBackground(QColor('#d4edda'))
            elif p.get('status') == 'diproses':
                status_item.setBackground(QColor('#fff3cd'))
            else:
                status_item.setBackground(QColor('#f8f9fa'))
            self.tbl_pembayaran.setItem(row, 6, status_item)

            # Action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background: #3498db; color: white; padding: 2px 8px;")
            btn_edit.clicked.connect(lambda checked, r=row: self.edit_pembayaran_by_row(r))
            btn_layout.addWidget(btn_edit)

            btn_del = QPushButton("Hapus")
            btn_del.setStyleSheet("background: #e74c3c; color: white; padding: 2px 8px;")
            btn_del.clicked.connect(lambda checked, r=row: self.delete_pembayaran(r))
            btn_layout.addWidget(btn_del)

            self.tbl_pembayaran.setCellWidget(row, 7, btn_widget)

    def add_pembayaran(self):
        """Add new payment"""
        pjlp_data = self.cmb_pjlp.currentData()
        if not pjlp_data:
            QMessageBox.warning(self, "Peringatan", "Pilih PJLP terlebih dahulu!")
            return

        dialog = PembayaranPJLPDialog(pjlp_data, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_pembayaran()
            QMessageBox.information(self, "Sukses", "Pembayaran berhasil ditambahkan!")

    def edit_pembayaran(self):
        """Edit selected payment"""
        row = self.tbl_pembayaran.currentRow()
        if row >= 0:
            self.edit_pembayaran_by_row(row)

    def edit_pembayaran_by_row(self, row):
        """Edit payment by row"""
        payment_id = int(self.tbl_pembayaran.item(row, 0).text())
        payment_data = self.db.get_pembayaran_pjlp(payment_id)
        pjlp_data = self.cmb_pjlp.currentData()

        if payment_data and pjlp_data:
            dialog = PembayaranPJLPDialog(pjlp_data, payment_data, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_pembayaran()

    def delete_pembayaran(self, row):
        """Delete payment"""
        payment_id = int(self.tbl_pembayaran.item(row, 0).text())
        bulan = self.tbl_pembayaran.item(row, 1).text()

        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Yakin ingin menghapus pembayaran {bulan}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db.delete_pembayaran_pjlp(payment_id):
                self.refresh_pembayaran()
                QMessageBox.information(self, "Sukses", "Pembayaran berhasil dihapus!")
            else:
                QMessageBox.warning(self, "Gagal", "Gagal menghapus pembayaran!")

    def refresh_rekap(self):
        """Refresh monthly recap"""
        bulan = self.cmb_rekap_bulan.currentData()
        tahun = self.spn_rekap_tahun.value()

        payments = self.db.get_pembayaran_by_bulan(bulan, tahun)
        self.tbl_rekap.setRowCount(len(payments))

        total_bruto = 0
        total_potongan = 0
        total_netto = 0

        for row, p in enumerate(payments):
            self.tbl_rekap.setItem(row, 0, QTableWidgetItem(p.get('nama_pjlp', '')))
            self.tbl_rekap.setItem(row, 1, QTableWidgetItem(p.get('nama_pekerjaan', '')))
            self.tbl_rekap.setItem(row, 2, QTableWidgetItem(self.format_currency(p.get('honor_bulanan', 0))))
            self.tbl_rekap.setItem(row, 3, QTableWidgetItem(self.format_currency(p.get('nilai_bruto', 0))))

            potongan = (p.get('potongan_pajak', 0) or 0) + (p.get('potongan_lain', 0) or 0)
            self.tbl_rekap.setItem(row, 4, QTableWidgetItem(self.format_currency(potongan)))
            self.tbl_rekap.setItem(row, 5, QTableWidgetItem(self.format_currency(p.get('nilai_netto', 0))))

            status_item = QTableWidgetItem(p.get('status', ''))
            if p.get('status') == 'dibayar':
                status_item.setBackground(QColor('#d4edda'))
            self.tbl_rekap.setItem(row, 6, status_item)

            total_bruto += p.get('nilai_bruto', 0) or 0
            total_potongan += potongan
            total_netto += p.get('nilai_netto', 0) or 0

        bulan_nama = self.BULAN_NAMES[bulan - 1]
        self.lbl_rekap_total.setText(
            f"Rekap Pembayaran PJLP {bulan_nama} {tahun}\n\n"
            f"Jumlah PJLP: {len(payments)} orang\n"
            f"Total Bruto: {self.format_currency(total_bruto)}\n"
            f"Total Potongan: {self.format_currency(total_potongan)}\n"
            f"Total Netto: {self.format_currency(total_netto)}"
        )
