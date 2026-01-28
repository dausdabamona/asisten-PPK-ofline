"""
PPK DOCUMENT FACTORY - SPM Lainnya Manager
===========================================
Manager untuk pembayaran SPM Lainnya dengan:
- Kuitansi Uang Muka SPM Lainnya
- Kuitansi Rampung SPM Lainnya

Support untuk:
- Honorarium
- Jamuan Tamu
- PJLP
- Perjalanan Dinas
- Pembayaran Lainnya
"""

import os
from datetime import datetime, date
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QMessageBox, QCheckBox, QFrame, QTabWidget,
    QAbstractItemView, QDateEdit, QSpinBox, QDoubleSpinBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QDate, QLocale
from PySide6.QtGui import QColor

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
        locale = QLocale(QLocale.Indonesian, QLocale.Indonesia)
        self.setLocale(locale)

    def textFromValue(self, value: float) -> str:
        return f"Rp {value:,.0f}".replace(",", ".")

    def valueFromText(self, text: str) -> float:
        clean = text.replace("Rp ", "").replace(".", "").replace(",", "").strip()
        try:
            return float(clean) if clean else 0
        except ValueError:
            return 0


# ============================================================================
# KUITANSI UANG MUKA SPM LAINNYA DIALOG
# ============================================================================

class KuitansiUangMukaDialog(QDialog):
    """Dialog for Kuitansi Uang Muka SPM Lainnya"""

    JENIS_PEMBAYARAN = [
        ('honorarium', 'Honorarium'),
        ('jamuan_tamu', 'Jamuan Tamu'),
        ('pjlp', 'PJLP'),
        ('perjalanan_dinas', 'Perjalanan Dinas'),
        ('lainnya', 'Pembayaran Lainnya')
    ]

    def __init__(self, kuitansi_data: dict = None, parent=None):
        super().__init__(parent)
        self.kuitansi_data = kuitansi_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Tambah Kuitansi Uang Muka SPM Lainnya" if not kuitansi_data else "Edit Kuitansi Uang Muka SPM Lainnya")
        self.setMinimumWidth(800)
        self.setMinimumHeight(700)
        self.setup_ui()

        if kuitansi_data:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # ========== SECTION A: DATA DIPA ==========
        dipa_group = QGroupBox("A. Data DIPA / Anggaran")
        dipa_form = QFormLayout()

        self.spn_tahun = QSpinBox()
        self.spn_tahun.setRange(2020, 2050)
        self.spn_tahun.setValue(TAHUN_ANGGARAN)
        dipa_form.addRow("Tahun Anggaran:", self.spn_tahun)

        nomor_layout = QHBoxLayout()
        self.txt_nomor_dipa = QLineEdit()
        self.txt_nomor_dipa.setPlaceholderText("0092.01.2.26.0006.0.0000.XXXXXX")
        nomor_layout.addWidget(self.txt_nomor_dipa)
        nomor_layout.addWidget(QLabel("Bulan:"))
        self.cmb_bulan = QComboBox()
        self.cmb_bulan.addItems([
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ])
        self.cmb_bulan.setCurrentIndex(datetime.now().month - 1)
        nomor_layout.addWidget(self.cmb_bulan)
        dipa_form.addRow("Nomor DIPA:", nomor_layout)

        dipa_group.setLayout(dipa_form)
        scroll_layout.addWidget(dipa_group)

        # ========== SECTION B: DATA KUITANSI ==========
        kuitansi_group = QGroupBox("B. Data Kuitansi")
        kuitansi_form = QFormLayout()

        nomor_kuitansi_layout = QHBoxLayout()
        self.txt_nomor_kuitansi = QLineEdit()
        self.txt_nomor_kuitansi.setPlaceholderText("KU-UM/001/2026")
        nomor_kuitansi_layout.addWidget(self.txt_nomor_kuitansi)
        nomor_kuitansi_layout.addWidget(QLabel("Tanggal:"))
        self.date_kuitansi = QDateEdit()
        self.date_kuitansi.setCalendarPopup(True)
        self.date_kuitansi.setDate(QDate.currentDate())
        nomor_kuitansi_layout.addWidget(self.date_kuitansi)
        kuitansi_form.addRow("Nomor Kuitansi:", nomor_kuitansi_layout)

        self.cmb_jenis_pembayaran = QComboBox()
        for code, name in self.JENIS_PEMBAYARAN:
            self.cmb_jenis_pembayaran.addItem(name, code)
        kuitansi_form.addRow("Jenis Pembayaran:", self.cmb_jenis_pembayaran)

        self.txt_uraian_pembayaran = QLineEdit()
        self.txt_uraian_pembayaran.setPlaceholderText("Uraian kegiatan / pembayaran")
        kuitansi_form.addRow("Uraian Pembayaran:", self.txt_uraian_pembayaran)

        kuitansi_group.setLayout(kuitansi_form)
        scroll_layout.addWidget(kuitansi_group)

        # ========== SECTION C: DATA PENERIMA ==========
        penerima_group = QGroupBox("C. Data Penerima Uang Muka")
        penerima_form = QFormLayout()

        self.txt_penerima_nama = QLineEdit()
        self.txt_penerima_nama.setPlaceholderText("Nama penerima uang muka")
        penerima_form.addRow("Nama Penerima:", self.txt_penerima_nama)

        nip_layout = QHBoxLayout()
        self.txt_penerima_nip = QLineEdit()
        self.txt_penerima_nip.setPlaceholderText("NIP Penerima")
        nip_layout.addWidget(self.txt_penerima_nip)
        nip_layout.addWidget(QLabel("Jabatan:"))
        self.txt_penerima_jabatan = QLineEdit()
        nip_layout.addWidget(self.txt_penerima_jabatan)
        penerima_form.addRow("NIP & Jabatan:", nip_layout)

        self.txt_penerima_alamat = QLineEdit()
        self.txt_penerima_alamat.setPlaceholderText("Alamat penerima")
        penerima_form.addRow("Alamat:", self.txt_penerima_alamat)

        penerima_group.setLayout(penerima_form)
        scroll_layout.addWidget(penerima_group)

        # ========== SECTION D: DATA UANG MUKA ==========
        uang_muka_group = QGroupBox("D. Data Uang Muka")
        uang_muka_form = QFormLayout()

        self.spn_uang_muka = CurrencySpinBox()
        uang_muka_form.addRow("Jumlah Uang Muka:", self.spn_uang_muka)

        self.cmb_sumber_dana = QComboBox()
        self.cmb_sumber_dana.addItems(["DIPA", "BLU", "PNBP", "BOPTN", "Lainnya"])
        uang_muka_form.addRow("Sumber Dana:", self.cmb_sumber_dana)

        akun_layout = QHBoxLayout()
        self.txt_kode_akun = QLineEdit()
        self.txt_kode_akun.setPlaceholderText("521213")
        akun_layout.addWidget(self.txt_kode_akun)
        akun_layout.addWidget(QLabel("MAK:"))
        self.txt_mak = QLineEdit()
        akun_layout.addWidget(self.txt_mak)
        uang_muka_form.addRow("Kode Akun:", akun_layout)

        uang_muka_group.setLayout(uang_muka_form)
        scroll_layout.addWidget(uang_muka_group)

        # ========== SECTION E: DATA DASAR PEMBAYARAN ==========
        dasar_group = QGroupBox("E. Dasar Pembayaran")
        dasar_form = QFormLayout()

        nomor_spk_layout = QHBoxLayout()
        self.txt_nomor_spk = QLineEdit()
        self.txt_nomor_spk.setPlaceholderText("SPK/001/2026")
        nomor_spk_layout.addWidget(self.txt_nomor_spk)
        nomor_spk_layout.addWidget(QLabel("Tanggal:"))
        self.date_spk = QDateEdit()
        self.date_spk.setCalendarPopup(True)
        self.date_spk.setDate(QDate.currentDate())
        nomor_spk_layout.addWidget(self.date_spk)
        dasar_form.addRow("Nomor SPK:", nomor_spk_layout)

        self.txt_dasar_pembayaran = QTextEdit()
        self.txt_dasar_pembayaran.setPlaceholderText("Dasar hukum pembayaran (SK KPA, dll)")
        self.txt_dasar_pembayaran.setMaximumHeight(80)
        dasar_form.addRow("Dasar Pembayaran:", self.txt_dasar_pembayaran)

        dasar_group.setLayout(dasar_form)
        scroll_layout.addWidget(dasar_group)

        # ========== SECTION F: DATA PENGESAHAN ==========
        pengesahan_group = QGroupBox("F. Pengesahan (Tanda Tangan)")
        pengesahan_form = QFormLayout()

        # KPA
        kpa_layout = QHBoxLayout()
        self.txt_kpa_nama = QLineEdit()
        self.txt_kpa_nama.setText(self.db.get_satker_pejabat().get('kpa_nama', ''))
        kpa_layout.addWidget(self.txt_kpa_nama)
        kpa_layout.addWidget(QLabel("NIP:"))
        self.txt_kpa_nip = QLineEdit()
        self.txt_kpa_nip.setText(self.db.get_satker_pejabat().get('kpa_nip', ''))
        kpa_layout.addWidget(self.txt_kpa_nip)
        pengesahan_form.addRow("KPA:", kpa_layout)

        # PPK
        ppk_layout = QHBoxLayout()
        self.txt_ppk_nama = QLineEdit()
        self.txt_ppk_nama.setText(self.db.get_satker_pejabat().get('ppk_nama', ''))
        ppk_layout.addWidget(self.txt_ppk_nama)
        ppk_layout.addWidget(QLabel("NIP:"))
        self.txt_ppk_nip = QLineEdit()
        self.txt_ppk_nip.setText(self.db.get_satker_pejabat().get('ppk_nip', ''))
        ppk_layout.addWidget(self.txt_ppk_nip)
        pengesahan_form.addRow("PPK:", ppk_layout)

        # Bendahara
        bendahara_layout = QHBoxLayout()
        self.txt_bendahara_nama = QLineEdit()
        self.txt_bendahara_nama.setText(self.db.get_satker_pejabat().get('bendahara_nama', ''))
        bendahara_layout.addWidget(self.txt_bendahara_nama)
        bendahara_layout.addWidget(QLabel("NIP:"))
        self.txt_bendahara_nip = QLineEdit()
        self.txt_bendahara_nip.setText(self.db.get_satker_pejabat().get('bendahara_nip', ''))
        bendahara_layout.addWidget(self.txt_bendahara_nip)
        pengesahan_form.addRow("Bendahara:", bendahara_layout)

        pengesahan_group.setLayout(pengesahan_form)
        scroll_layout.addWidget(pengesahan_group)

        # Keterangan
        self.txt_keterangan = QTextEdit()
        self.txt_keterangan.setPlaceholderText("Keterangan tambahan...")
        self.txt_keterangan.setMaximumHeight(60)
        scroll_layout.addWidget(QLabel("Keterangan:"))
        scroll_layout.addWidget(self.txt_keterangan)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # ========== BUTTONS ==========
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

    def load_data(self):
        d = self.kuitansi_data
        self.spn_tahun.setValue(d.get('tahun_anggaran', TAHUN_ANGGARAN))
        self.txt_nomor_dipa.setText(d.get('nomor_dipa', ''))
        self.cmb_bulan.setCurrentIndex(d.get('bulan', 1) - 1)

        self.txt_nomor_kuitansi.setText(d.get('nomor_kuitansi', ''))
        if d.get('tanggal_kuitansi'):
            self.date_kuitansi.setDate(QDate.fromString(str(d['tanggal_kuitansi']), 'yyyy-MM-dd'))

        idx = self.cmb_jenis_pembayaran.findData(d.get('jenis_pembayaran', ''))
        if idx >= 0:
            self.cmb_jenis_pembayaran.setCurrentIndex(idx)

        self.txt_uraian_pembayaran.setText(d.get('uraian_pembayaran', ''))

        self.txt_penerima_nama.setText(d.get('penerima_nama', ''))
        self.txt_penerima_nip.setText(d.get('penerima_nip', ''))
        self.txt_penerima_jabatan.setText(d.get('penerima_jabatan', ''))
        self.txt_penerima_alamat.setText(d.get('penerima_alamat', ''))

        self.spn_uang_muka.setValue(d.get('uang_muka', 0))

        self.cmb_sumber_dana.setCurrentText(d.get('sumber_dana', 'DIPA'))
        self.txt_kode_akun.setText(d.get('kode_akun', ''))
        self.txt_mak.setText(d.get('mak', ''))

        self.txt_nomor_spk.setText(d.get('nomor_spk', ''))
        if d.get('tanggal_spk'):
            self.date_spk.setDate(QDate.fromString(str(d['tanggal_spk']), 'yyyy-MM-dd'))

        self.txt_dasar_pembayaran.setPlainText(d.get('dasar_pembayaran', ''))

        self.txt_kpa_nama.setText(d.get('kpa_nama', ''))
        self.txt_kpa_nip.setText(d.get('kpa_nip', ''))
        self.txt_ppk_nama.setText(d.get('ppk_nama', ''))
        self.txt_ppk_nip.setText(d.get('ppk_nip', ''))
        self.txt_bendahara_nama.setText(d.get('bendahara_nama', ''))
        self.txt_bendahara_nip.setText(d.get('bendahara_nip', ''))

        self.txt_keterangan.setPlainText(d.get('keterangan', ''))

    def save_data(self):
        if not self.txt_nomor_kuitansi.text().strip():
            QMessageBox.warning(self, "Validasi", "Nomor kuitansi harus diisi!")
            return

        if self.spn_uang_muka.value() <= 0:
            QMessageBox.warning(self, "Validasi", "Jumlah uang muka harus lebih dari 0!")
            return

        data = {
            'tahun_anggaran': self.spn_tahun.value(),
            'nomor_dipa': self.txt_nomor_dipa.text(),
            'bulan': self.cmb_bulan.currentIndex() + 1,
            'nomor_kuitansi': self.txt_nomor_kuitansi.text(),
            'tanggal_kuitansi': self.date_kuitansi.date().toString('yyyy-MM-dd'),
            'jenis_pembayaran': self.cmb_jenis_pembayaran.currentData(),
            'uraian_pembayaran': self.txt_uraian_pembayaran.text(),
            'penerima_nama': self.txt_penerima_nama.text(),
            'penerima_nip': self.txt_penerima_nip.text(),
            'penerima_jabatan': self.txt_penerima_jabatan.text(),
            'penerima_alamat': self.txt_penerima_alamat.text(),
            'uang_muka': self.spn_uang_muka.value(),
            'sumber_dana': self.cmb_sumber_dana.currentText(),
            'kode_akun': self.txt_kode_akun.text(),
            'mak': self.txt_mak.text(),
            'nomor_spk': self.txt_nomor_spk.text(),
            'tanggal_spk': self.date_spk.date().toString('yyyy-MM-dd'),
            'dasar_pembayaran': self.txt_dasar_pembayaran.toPlainText(),
            'kpa_nama': self.txt_kpa_nama.text(),
            'kpa_nip': self.txt_kpa_nip.text(),
            'ppk_nama': self.txt_ppk_nama.text(),
            'ppk_nip': self.txt_ppk_nip.text(),
            'bendahara_nama': self.txt_bendahara_nama.text(),
            'bendahara_nip': self.txt_bendahara_nip.text(),
            'keterangan': self.txt_keterangan.toPlainText(),
            'status': 'draft'
        }

        try:
            if self.kuitansi_data:
                # Update existing
                self.kuitansi_data.update(data)
                QMessageBox.information(self, "Sukses", "Data berhasil diperbarui!")
            else:
                # Create new - would be handled by parent manager
                self.tag = data
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {str(e)}")


# ============================================================================
# KUITANSI RAMPUNG SPM LAINNYA DIALOG
# ============================================================================

class KuitansiRampungDialog(QDialog):
    """Dialog for Kuitansi Rampung SPM Lainnya"""

    JENIS_PEMBAYARAN = [
        ('honorarium', 'Honorarium'),
        ('jamuan_tamu', 'Jamuan Tamu'),
        ('pjlp', 'PJLP'),
        ('perjalanan_dinas', 'Perjalanan Dinas'),
        ('lainnya', 'Pembayaran Lainnya')
    ]

    def __init__(self, kuitansi_data: dict = None, parent=None):
        super().__init__(parent)
        self.kuitansi_data = kuitansi_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Tambah Kuitansi Rampung SPM Lainnya" if not kuitansi_data else "Edit Kuitansi Rampung SPM Lainnya")
        self.setMinimumWidth(800)
        self.setMinimumHeight(750)
        self.setup_ui()

        if kuitansi_data:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # ========== SECTION A: DATA DIPA ==========
        dipa_group = QGroupBox("A. Data DIPA / Anggaran")
        dipa_form = QFormLayout()

        self.spn_tahun = QSpinBox()
        self.spn_tahun.setRange(2020, 2050)
        self.spn_tahun.setValue(TAHUN_ANGGARAN)
        dipa_form.addRow("Tahun Anggaran:", self.spn_tahun)

        nomor_layout = QHBoxLayout()
        self.txt_nomor_dipa = QLineEdit()
        self.txt_nomor_dipa.setPlaceholderText("0092.01.2.26.0006.0.0000.XXXXXX")
        nomor_layout.addWidget(self.txt_nomor_dipa)
        nomor_layout.addWidget(QLabel("Bulan:"))
        self.cmb_bulan = QComboBox()
        self.cmb_bulan.addItems([
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ])
        self.cmb_bulan.setCurrentIndex(datetime.now().month - 1)
        nomor_layout.addWidget(self.cmb_bulan)
        dipa_form.addRow("Nomor DIPA:", nomor_layout)

        dipa_group.setLayout(dipa_form)
        scroll_layout.addWidget(dipa_group)

        # ========== SECTION B: DATA PENERIMA ==========
        penerima_group = QGroupBox("B. Data Penerima Pembayaran Rampung")
        penerima_form = QFormLayout()

        self.txt_penerima_nama = QLineEdit()
        self.txt_penerima_nama.setPlaceholderText("Nama penerima")
        penerima_form.addRow("Nama Penerima:", self.txt_penerima_nama)

        nip_layout = QHBoxLayout()
        self.txt_penerima_nip = QLineEdit()
        self.txt_penerima_nip.setPlaceholderText("NIP Penerima")
        nip_layout.addWidget(self.txt_penerima_nip)
        nip_layout.addWidget(QLabel("Jabatan:"))
        self.txt_penerima_jabatan = QLineEdit()
        nip_layout.addWidget(self.txt_penerima_jabatan)
        penerima_form.addRow("NIP & Jabatan:", nip_layout)

        penerima_group.setLayout(penerima_form)
        scroll_layout.addWidget(penerima_group)

        # ========== SECTION C: RINCIAN PEMBAYARAN ==========
        rincian_group = QGroupBox("C. Rincian Pembayaran")
        rincian_form = QFormLayout()

        self.cmb_jenis_pembayaran = QComboBox()
        for code, name in self.JENIS_PEMBAYARAN:
            self.cmb_jenis_pembayaran.addItem(name, code)
        rincian_form.addRow("Jenis Pembayaran:", self.cmb_jenis_pembayaran)

        self.txt_uraian_pembayaran = QLineEdit()
        self.txt_uraian_pembayaran.setPlaceholderText("Uraian kegiatan / pembayaran")
        rincian_form.addRow("Uraian Pembayaran:", self.txt_uraian_pembayaran)

        # Total Kontrak
        self.spn_total_kontrak = CurrencySpinBox()
        rincian_form.addRow("Total Kontrak/Kegiatan:", self.spn_total_kontrak)
        self.spn_total_kontrak.valueChanged.connect(self.calc_rampung)

        # Uang Muka Sebelumnya
        self.spn_uang_muka = CurrencySpinBox()
        rincian_form.addRow("Uang Muka Sebelumnya:", self.spn_uang_muka)
        self.spn_uang_muka.valueChanged.connect(self.calc_rampung)

        # Pembayaran Rampung (Auto-calculated)
        self.spn_pembayaran_rampung = CurrencySpinBox()
        self.spn_pembayaran_rampung.setReadOnly(True)
        self.spn_pembayaran_rampung.setStyleSheet("background-color: #d4edda; font-weight: bold;")
        rincian_form.addRow("Pembayaran Rampung:", self.spn_pembayaran_rampung)

        rincian_group.setLayout(rincian_form)
        scroll_layout.addWidget(rincian_group)

        # ========== SECTION D: RINGKASAN ==========
        ringkasan_group = QGroupBox("D. Ringkasan")
        ringkasan_form = QFormLayout()

        nomor_kuitansi_layout = QHBoxLayout()
        self.txt_nomor_kuitansi = QLineEdit()
        self.txt_nomor_kuitansi.setPlaceholderText("KU-RP/001/2026")
        nomor_kuitansi_layout.addWidget(self.txt_nomor_kuitansi)
        nomor_kuitansi_layout.addWidget(QLabel("Tanggal:"))
        self.date_kuitansi = QDateEdit()
        self.date_kuitansi.setCalendarPopup(True)
        self.date_kuitansi.setDate(QDate.currentDate())
        nomor_kuitansi_layout.addWidget(self.date_kuitansi)
        ringkasan_form.addRow("Nomor Kuitansi:", nomor_kuitansi_layout)

        self.cmb_sumber_dana = QComboBox()
        self.cmb_sumber_dana.addItems(["DIPA", "BLU", "PNBP", "BOPTN", "Lainnya"])
        ringkasan_form.addRow("Sumber Dana:", self.cmb_sumber_dana)

        akun_layout = QHBoxLayout()
        self.txt_kode_akun = QLineEdit()
        self.txt_kode_akun.setPlaceholderText("521213")
        akun_layout.addWidget(self.txt_kode_akun)
        akun_layout.addWidget(QLabel("MAK:"))
        self.txt_mak = QLineEdit()
        akun_layout.addWidget(self.txt_mak)
        ringkasan_form.addRow("Kode Akun:", akun_layout)

        ringkasan_group.setLayout(ringkasan_form)
        scroll_layout.addWidget(ringkasan_group)

        # ========== SECTION E: DATA DASAR PEMBAYARAN ==========
        dasar_group = QGroupBox("E. Dasar Pembayaran")
        dasar_form = QFormLayout()

        self.txt_dasar_pembayaran = QTextEdit()
        self.txt_dasar_pembayaran.setPlaceholderText("Dasar hukum pembayaran (SK KPA, dll)")
        self.txt_dasar_pembayaran.setMaximumHeight(80)
        dasar_form.addRow("Dasar Pembayaran:", self.txt_dasar_pembayaran)

        dasar_group.setLayout(dasar_form)
        scroll_layout.addWidget(dasar_group)

        # ========== SECTION F: DATA PENGESAHAN ==========
        pengesahan_group = QGroupBox("F. Pengesahan (Tanda Tangan)")
        pengesahan_form = QFormLayout()

        # KPA
        kpa_layout = QHBoxLayout()
        self.txt_kpa_nama = QLineEdit()
        self.txt_kpa_nama.setText(self.db.get_satker_pejabat().get('kpa_nama', ''))
        kpa_layout.addWidget(self.txt_kpa_nama)
        kpa_layout.addWidget(QLabel("NIP:"))
        self.txt_kpa_nip = QLineEdit()
        self.txt_kpa_nip.setText(self.db.get_satker_pejabat().get('kpa_nip', ''))
        kpa_layout.addWidget(self.txt_kpa_nip)
        pengesahan_form.addRow("KPA:", kpa_layout)

        # PPK
        ppk_layout = QHBoxLayout()
        self.txt_ppk_nama = QLineEdit()
        self.txt_ppk_nama.setText(self.db.get_satker_pejabat().get('ppk_nama', ''))
        ppk_layout.addWidget(self.txt_ppk_nama)
        ppk_layout.addWidget(QLabel("NIP:"))
        self.txt_ppk_nip = QLineEdit()
        self.txt_ppk_nip.setText(self.db.get_satker_pejabat().get('ppk_nip', ''))
        ppk_layout.addWidget(self.txt_ppk_nip)
        pengesahan_form.addRow("PPK:", ppk_layout)

        # Bendahara
        bendahara_layout = QHBoxLayout()
        self.txt_bendahara_nama = QLineEdit()
        self.txt_bendahara_nama.setText(self.db.get_satker_pejabat().get('bendahara_nama', ''))
        bendahara_layout.addWidget(self.txt_bendahara_nama)
        bendahara_layout.addWidget(QLabel("NIP:"))
        self.txt_bendahara_nip = QLineEdit()
        self.txt_bendahara_nip.setText(self.db.get_satker_pejabat().get('bendahara_nip', ''))
        bendahara_layout.addWidget(self.txt_bendahara_nip)
        pengesahan_form.addRow("Bendahara:", bendahara_layout)

        pengesahan_group.setLayout(pengesahan_form)
        scroll_layout.addWidget(pengesahan_group)

        # Keterangan
        self.txt_keterangan = QTextEdit()
        self.txt_keterangan.setPlaceholderText("Keterangan tambahan...")
        self.txt_keterangan.setMaximumHeight(60)
        scroll_layout.addWidget(QLabel("Keterangan:"))
        scroll_layout.addWidget(self.txt_keterangan)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # ========== BUTTONS ==========
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

    def calc_rampung(self):
        """Calculate pembayaran rampung = Total - Uang Muka"""
        total = self.spn_total_kontrak.value()
        uang_muka = self.spn_uang_muka.value()
        rampung = total - uang_muka
        self.spn_pembayaran_rampung.setValue(max(0, rampung))

    def load_data(self):
        d = self.kuitansi_data
        self.spn_tahun.setValue(d.get('tahun_anggaran', TAHUN_ANGGARAN))
        self.txt_nomor_dipa.setText(d.get('nomor_dipa', ''))
        self.cmb_bulan.setCurrentIndex(d.get('bulan', 1) - 1)

        self.txt_penerima_nama.setText(d.get('penerima_nama', ''))
        self.txt_penerima_nip.setText(d.get('penerima_nip', ''))
        self.txt_penerima_jabatan.setText(d.get('penerima_jabatan', ''))

        idx = self.cmb_jenis_pembayaran.findData(d.get('jenis_pembayaran', ''))
        if idx >= 0:
            self.cmb_jenis_pembayaran.setCurrentIndex(idx)

        self.txt_uraian_pembayaran.setText(d.get('uraian_pembayaran', ''))
        self.spn_total_kontrak.setValue(d.get('total_kontrak', 0))
        self.spn_uang_muka.setValue(d.get('uang_muka', 0))
        self.spn_pembayaran_rampung.setValue(d.get('pembayaran_rampung', 0))

        self.txt_nomor_kuitansi.setText(d.get('nomor_kuitansi', ''))
        if d.get('tanggal_kuitansi'):
            self.date_kuitansi.setDate(QDate.fromString(str(d['tanggal_kuitansi']), 'yyyy-MM-dd'))

        self.cmb_sumber_dana.setCurrentText(d.get('sumber_dana', 'DIPA'))
        self.txt_kode_akun.setText(d.get('kode_akun', ''))
        self.txt_mak.setText(d.get('mak', ''))

        self.txt_dasar_pembayaran.setPlainText(d.get('dasar_pembayaran', ''))

        self.txt_kpa_nama.setText(d.get('kpa_nama', ''))
        self.txt_kpa_nip.setText(d.get('kpa_nip', ''))
        self.txt_ppk_nama.setText(d.get('ppk_nama', ''))
        self.txt_ppk_nip.setText(d.get('ppk_nip', ''))
        self.txt_bendahara_nama.setText(d.get('bendahara_nama', ''))
        self.txt_bendahara_nip.setText(d.get('bendahara_nip', ''))

        self.txt_keterangan.setPlainText(d.get('keterangan', ''))

    def save_data(self):
        if not self.txt_nomor_kuitansi.text().strip():
            QMessageBox.warning(self, "Validasi", "Nomor kuitansi harus diisi!")
            return

        if self.spn_pembayaran_rampung.value() <= 0:
            QMessageBox.warning(self, "Validasi", "Pembayaran rampung harus lebih dari 0!")
            return

        data = {
            'tahun_anggaran': self.spn_tahun.value(),
            'nomor_dipa': self.txt_nomor_dipa.text(),
            'bulan': self.cmb_bulan.currentIndex() + 1,
            'penerima_nama': self.txt_penerima_nama.text(),
            'penerima_nip': self.txt_penerima_nip.text(),
            'penerima_jabatan': self.txt_penerima_jabatan.text(),
            'jenis_pembayaran': self.cmb_jenis_pembayaran.currentData(),
            'uraian_pembayaran': self.txt_uraian_pembayaran.text(),
            'total_kontrak': self.spn_total_kontrak.value(),
            'uang_muka': self.spn_uang_muka.value(),
            'pembayaran_rampung': self.spn_pembayaran_rampung.value(),
            'nomor_kuitansi': self.txt_nomor_kuitansi.text(),
            'tanggal_kuitansi': self.date_kuitansi.date().toString('yyyy-MM-dd'),
            'sumber_dana': self.cmb_sumber_dana.currentText(),
            'kode_akun': self.txt_kode_akun.text(),
            'mak': self.txt_mak.text(),
            'dasar_pembayaran': self.txt_dasar_pembayaran.toPlainText(),
            'kpa_nama': self.txt_kpa_nama.text(),
            'kpa_nip': self.txt_kpa_nip.text(),
            'ppk_nama': self.txt_ppk_nama.text(),
            'ppk_nip': self.txt_ppk_nip.text(),
            'bendahara_nama': self.txt_bendahara_nama.text(),
            'bendahara_nip': self.txt_bendahara_nip.text(),
            'keterangan': self.txt_keterangan.toPlainText(),
            'status': 'draft'
        }

        try:
            if self.kuitansi_data:
                # Update existing
                self.kuitansi_data.update(data)
                QMessageBox.information(self, "Sukses", "Data berhasil diperbarui!")
            else:
                # Create new - would be handled by parent manager
                self.tag = data
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {str(e)}")


# ============================================================================
# SPM LAINNYA MANAGER (Main Widget)
# ============================================================================

class SPMLainnyaManager(QWidget):
    """Main manager for SPM Lainnya - Kuitansi Uang Muka & Rampung"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db_manager_v4()
        # In-memory storage for kuitansi data
        self.kuitansi_um_list: List[Dict] = []
        self.kuitansi_rp_list: List[Dict] = []
        self.setup_ui()
        self.refresh_all()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("SPM Lainnya - Kuitansi")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()

        # ========== TAB 1: KUITANSI UANG MUKA ==========
        tab_um = QWidget()
        um_layout = QVBoxLayout(tab_um)

        um_toolbar = QHBoxLayout()
        btn_add_um = QPushButton("+ Tambah Kuitansi Uang Muka")
        btn_add_um.setStyleSheet("background-color: #3498db; color: white; padding: 8px 16px;")
        btn_add_um.clicked.connect(self.add_kuitansi_um)
        um_toolbar.addWidget(btn_add_um)
        um_toolbar.addStretch()

        um_toolbar.addWidget(QLabel("Jenis:"))
        self.cmb_um_jenis = QComboBox()
        self.cmb_um_jenis.addItem("Semua", None)
        self.cmb_um_jenis.addItems(["Honorarium", "Jamuan Tamu", "PJLP", "Perjalanan Dinas", "Pembayaran Lainnya"])
        self.cmb_um_jenis.currentIndexChanged.connect(self.refresh_kuitansi_um)
        um_toolbar.addWidget(self.cmb_um_jenis)

        um_layout.addLayout(um_toolbar)

        self.tbl_um = QTableWidget()
        self.tbl_um.setColumnCount(7)
        self.tbl_um.setHorizontalHeaderLabels([
            "ID", "Nomor Kuitansi", "Penerima", "Jenis", "Uang Muka", "Tanggal", "Aksi"
        ])
        self.tbl_um.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_um.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_um.horizontalHeader().setStretchLastSection(True)
        self.tbl_um.setColumnWidth(0, 50)
        self.tbl_um.setColumnWidth(1, 150)
        self.tbl_um.setColumnWidth(2, 150)
        self.tbl_um.setColumnWidth(3, 120)
        self.tbl_um.setColumnWidth(4, 120)
        self.tbl_um.setColumnWidth(5, 100)
        um_layout.addWidget(self.tbl_um)

        self.tabs.addTab(tab_um, "Kuitansi Uang Muka")

        # ========== TAB 2: KUITANSI RAMPUNG ==========
        tab_rp = QWidget()
        rp_layout = QVBoxLayout(tab_rp)

        rp_toolbar = QHBoxLayout()
        btn_add_rp = QPushButton("+ Tambah Kuitansi Rampung")
        btn_add_rp.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 16px;")
        btn_add_rp.clicked.connect(self.add_kuitansi_rp)
        rp_toolbar.addWidget(btn_add_rp)
        rp_toolbar.addStretch()

        rp_toolbar.addWidget(QLabel("Jenis:"))
        self.cmb_rp_jenis = QComboBox()
        self.cmb_rp_jenis.addItem("Semua", None)
        self.cmb_rp_jenis.addItems(["Honorarium", "Jamuan Tamu", "PJLP", "Perjalanan Dinas", "Pembayaran Lainnya"])
        self.cmb_rp_jenis.currentIndexChanged.connect(self.refresh_kuitansi_rp)
        rp_toolbar.addWidget(self.cmb_rp_jenis)

        rp_layout.addLayout(rp_toolbar)

        self.tbl_rp = QTableWidget()
        self.tbl_rp.setColumnCount(8)
        self.tbl_rp.setHorizontalHeaderLabels([
            "ID", "Nomor Kuitansi", "Penerima", "Jenis", "Total", "Uang Muka", "Rampung", "Aksi"
        ])
        self.tbl_rp.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_rp.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_rp.horizontalHeader().setStretchLastSection(True)
        rp_layout.addWidget(self.tbl_rp)

        self.tabs.addTab(tab_rp, "Kuitansi Rampung")

        layout.addWidget(self.tabs)

    def format_currency(self, value):
        return f"Rp {value:,.0f}".replace(",", ".")

    def refresh_all(self):
        self.refresh_kuitansi_um()
        self.refresh_kuitansi_rp()

    def refresh_kuitansi_um(self):
        # Load from in-memory list
        data = self.kuitansi_um_list
        jenis_filter = self.cmb_um_jenis.currentData()

        if jenis_filter:
            data = [d for d in data if d.get('jenis_pembayaran') == jenis_filter]

        self.tbl_um.setRowCount(len(data))

        for row, d in enumerate(data):
            self.tbl_um.setItem(row, 0, QTableWidgetItem(str(d.get('id', row))))
            self.tbl_um.setItem(row, 1, QTableWidgetItem(d.get('nomor_kuitansi', '')))
            self.tbl_um.setItem(row, 2, QTableWidgetItem(d.get('penerima_nama', '')))
            self.tbl_um.setItem(row, 3, QTableWidgetItem(d.get('jenis_pembayaran', '')))
            self.tbl_um.setItem(row, 4, QTableWidgetItem(self.format_currency(d.get('uang_muka', 0))))
            self.tbl_um.setItem(row, 5, QTableWidgetItem(str(d.get('tanggal_kuitansi', ''))))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background: #3498db; color: white; padding: 2px 8px;")
            btn_edit.clicked.connect(lambda checked, r=row: self.edit_kuitansi_um(r))
            btn_layout.addWidget(btn_edit)

            btn_del = QPushButton("Hapus")
            btn_del.setStyleSheet("background: #e74c3c; color: white; padding: 2px 8px;")
            btn_del.clicked.connect(lambda checked, r=row: self.delete_kuitansi_um(r))
            btn_layout.addWidget(btn_del)

            btn_cetak = QPushButton("Cetak")
            btn_cetak.setStyleSheet("background: #27ae60; color: white; padding: 2px 8px;")
            btn_cetak.clicked.connect(lambda checked, r=row: self.generate_kuitansi_um(r))
            btn_layout.addWidget(btn_cetak)

            self.tbl_um.setCellWidget(row, 6, btn_widget)

    def refresh_kuitansi_rp(self):
        # Load from in-memory list
        data = self.kuitansi_rp_list
        jenis_filter = self.cmb_rp_jenis.currentData()

        if jenis_filter:
            data = [d for d in data if d.get('jenis_pembayaran') == jenis_filter]

        self.tbl_rp.setRowCount(len(data))

        for row, d in enumerate(data):
            self.tbl_rp.setItem(row, 0, QTableWidgetItem(str(d.get('id', row))))
            self.tbl_rp.setItem(row, 1, QTableWidgetItem(d.get('nomor_kuitansi', '')))
            self.tbl_rp.setItem(row, 2, QTableWidgetItem(d.get('penerima_nama', '')))
            self.tbl_rp.setItem(row, 3, QTableWidgetItem(d.get('jenis_pembayaran', '')))
            self.tbl_rp.setItem(row, 4, QTableWidgetItem(self.format_currency(d.get('total_kontrak', 0))))
            self.tbl_rp.setItem(row, 5, QTableWidgetItem(self.format_currency(d.get('uang_muka', 0))))
            self.tbl_rp.setItem(row, 6, QTableWidgetItem(self.format_currency(d.get('pembayaran_rampung', 0))))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background: #3498db; color: white; padding: 2px 8px;")
            btn_edit.clicked.connect(lambda checked, r=row: self.edit_kuitansi_rp(r))
            btn_layout.addWidget(btn_edit)

            btn_del = QPushButton("Hapus")
            btn_del.setStyleSheet("background: #e74c3c; color: white; padding: 2px 8px;")
            btn_del.clicked.connect(lambda checked, r=row: self.delete_kuitansi_rp(r))
            btn_layout.addWidget(btn_del)

            btn_cetak = QPushButton("Cetak")
            btn_cetak.setStyleSheet("background: #27ae60; color: white; padding: 2px 8px;")
            btn_cetak.clicked.connect(lambda checked, r=row: self.generate_kuitansi_rp(r))
            btn_layout.addWidget(btn_cetak)

            self.tbl_rp.setCellWidget(row, 7, btn_widget)

    def add_kuitansi_um(self):
        dialog = KuitansiUangMukaDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.tag if hasattr(dialog, 'tag') else None
            if data:
                data['id'] = len(self.kuitansi_um_list) + 1
                self.kuitansi_um_list.append(data)
                self.refresh_kuitansi_um()
                QMessageBox.information(self, "Sukses", "Kuitansi Uang Muka berhasil ditambahkan!")

    def edit_kuitansi_um(self, row):
        if row < len(self.kuitansi_um_list):
            kuitansi = self.kuitansi_um_list[row]
            dialog = KuitansiUangMukaDialog(kuitansi, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_kuitansi_um()
                QMessageBox.information(self, "Sukses", "Kuitansi Uang Muka berhasil diperbarui!")

    def delete_kuitansi_um(self, row):
        reply = QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus kuitansi ini?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes and row < len(self.kuitansi_um_list):
            self.kuitansi_um_list.pop(row)
            self.refresh_kuitansi_um()
            QMessageBox.information(self, "Sukses", "Kuitansi berhasil dihapus!")

    def generate_kuitansi_um(self, row):
        if row < len(self.kuitansi_um_list):
            kuitansi = self.kuitansi_um_list[row]
            QMessageBox.information(self, "Generate", 
                                   f"Fitur cetak untuk:\n{kuitansi.get('nomor_kuitansi', '')}\n\nSedang dalam pengembangan...")

    def add_kuitansi_rp(self):
        dialog = KuitansiRampungDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.tag if hasattr(dialog, 'tag') else None
            if data:
                data['id'] = len(self.kuitansi_rp_list) + 1
                self.kuitansi_rp_list.append(data)
                self.refresh_kuitansi_rp()
                QMessageBox.information(self, "Sukses", "Kuitansi Rampung berhasil ditambahkan!")

    def edit_kuitansi_rp(self, row):
        if row < len(self.kuitansi_rp_list):
            kuitansi = self.kuitansi_rp_list[row]
            dialog = KuitansiRampungDialog(kuitansi, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_kuitansi_rp()
                QMessageBox.information(self, "Sukses", "Kuitansi Rampung berhasil diperbarui!")

    def delete_kuitansi_rp(self, row):
        reply = QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus kuitansi ini?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes and row < len(self.kuitansi_rp_list):
            self.kuitansi_rp_list.pop(row)
            self.refresh_kuitansi_rp()
            QMessageBox.information(self, "Sukses", "Kuitansi berhasil dihapus!")

    def generate_kuitansi_rp(self, row):
        if row < len(self.kuitansi_rp_list):
            kuitansi = self.kuitansi_rp_list[row]
            QMessageBox.information(self, "Generate", 
                                   f"Fitur cetak untuk:\n{kuitansi.get('nomor_kuitansi', '')}\n\nSedang dalam pengembangan...")
