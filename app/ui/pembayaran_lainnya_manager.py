"""
PPK DOCUMENT FACTORY - Pembayaran Lainnya Manager
==================================================
Manager untuk pembayaran:
- SK KPA (Surat Keputusan Kuasa Pengguna Anggaran)
- Honorarium (Reguler & Insidentil)
- Jamuan Tamu
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
# SK KPA DIALOG
# ============================================================================

class SKKPADialog(QDialog):
    """Dialog for SK KPA"""

    JENIS_PEMBAYARAN = [
        ('swakelola', 'Swakelola'),
        ('honorarium', 'Honorarium'),
        ('jamuan_tamu', 'Jamuan Tamu'),
        ('pjlp', 'PJLP'),
        ('perjalanan_dinas', 'Perjalanan Dinas'),
        ('lainnya', 'Lainnya')
    ]

    def __init__(self, sk_data: dict = None, parent=None):
        super().__init__(parent)
        self.sk_data = sk_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Tambah SK KPA" if not sk_data else "Edit SK KPA")
        self.setMinimumWidth(700)
        self.setup_ui()

        if sk_data:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Form
        form = QFormLayout()

        # Tahun
        self.spn_tahun = QSpinBox()
        self.spn_tahun.setRange(2020, 2050)
        self.spn_tahun.setValue(TAHUN_ANGGARAN)
        form.addRow("Tahun Anggaran:", self.spn_tahun)

        # Nomor SK
        nomor_layout = QHBoxLayout()
        self.txt_nomor_sk = QLineEdit()
        self.txt_nomor_sk.setPlaceholderText("SK-KPA/001/2024")
        nomor_layout.addWidget(self.txt_nomor_sk)
        nomor_layout.addWidget(QLabel("Tanggal:"))
        self.date_sk = QDateEdit()
        self.date_sk.setCalendarPopup(True)
        self.date_sk.setDate(QDate.currentDate())
        nomor_layout.addWidget(self.date_sk)
        form.addRow("Nomor SK:", nomor_layout)

        # Perihal
        self.txt_perihal = QLineEdit()
        self.txt_perihal.setPlaceholderText("Pembayaran Honor Narasumber...")
        form.addRow("Perihal:", self.txt_perihal)

        # Jenis Pembayaran
        self.cmb_jenis = QComboBox()
        for code, name in self.JENIS_PEMBAYARAN:
            self.cmb_jenis.addItem(name, code)
        form.addRow("Jenis Pembayaran:", self.cmb_jenis)

        # Nilai
        self.spn_nilai = CurrencySpinBox()
        form.addRow("Nilai Pembayaran:", self.spn_nilai)

        # Dasar Pembayaran
        self.txt_dasar = QTextEdit()
        self.txt_dasar.setMaximumHeight(80)
        self.txt_dasar.setPlaceholderText("1. DIPA ...\n2. POK ...")
        form.addRow("Dasar Pembayaran:", self.txt_dasar)

        layout.addLayout(form)

        # Pejabat Group
        pejabat_group = QGroupBox("Data Pejabat")
        pejabat_form = QFormLayout()

        # KPA
        self.txt_kpa_nama = QLineEdit()
        self.txt_kpa_nama.setText(SATKER_DEFAULT.get('kpa_nama', ''))
        pejabat_form.addRow("Nama KPA:", self.txt_kpa_nama)

        kpa_layout = QHBoxLayout()
        self.txt_kpa_nip = QLineEdit()
        self.txt_kpa_nip.setText(SATKER_DEFAULT.get('kpa_nip', ''))
        kpa_layout.addWidget(QLabel("NIP:"))
        kpa_layout.addWidget(self.txt_kpa_nip)
        self.txt_kpa_jabatan = QLineEdit()
        self.txt_kpa_jabatan.setText(SATKER_DEFAULT.get('kpa_jabatan', 'Kuasa Pengguna Anggaran'))
        kpa_layout.addWidget(QLabel("Jabatan:"))
        kpa_layout.addWidget(self.txt_kpa_jabatan)
        pejabat_form.addRow("", kpa_layout)

        # PPK
        self.txt_ppk_nama = QLineEdit()
        self.txt_ppk_nama.setText(SATKER_DEFAULT.get('ppk_nama', ''))
        pejabat_form.addRow("Nama PPK:", self.txt_ppk_nama)

        ppk_layout = QHBoxLayout()
        self.txt_ppk_nip = QLineEdit()
        self.txt_ppk_nip.setText(SATKER_DEFAULT.get('ppk_nip', ''))
        ppk_layout.addWidget(QLabel("NIP:"))
        ppk_layout.addWidget(self.txt_ppk_nip)
        self.txt_ppk_jabatan = QLineEdit()
        self.txt_ppk_jabatan.setText(SATKER_DEFAULT.get('ppk_jabatan', 'Pejabat Pembuat Komitmen'))
        ppk_layout.addWidget(QLabel("Jabatan:"))
        ppk_layout.addWidget(self.txt_ppk_jabatan)
        pejabat_form.addRow("", ppk_layout)

        # Bendahara
        bend_layout = QHBoxLayout()
        self.txt_bendahara_nama = QLineEdit()
        self.txt_bendahara_nama.setText(SATKER_DEFAULT.get('bendahara_nama', ''))
        bend_layout.addWidget(QLabel("Nama:"))
        bend_layout.addWidget(self.txt_bendahara_nama)
        self.txt_bendahara_nip = QLineEdit()
        self.txt_bendahara_nip.setText(SATKER_DEFAULT.get('bendahara_nip', ''))
        bend_layout.addWidget(QLabel("NIP:"))
        bend_layout.addWidget(self.txt_bendahara_nip)
        pejabat_form.addRow("Bendahara:", bend_layout)

        pejabat_group.setLayout(pejabat_form)
        layout.addWidget(pejabat_group)

        # Keterangan
        self.txt_keterangan = QTextEdit()
        self.txt_keterangan.setMaximumHeight(60)
        layout.addWidget(QLabel("Keterangan:"))
        layout.addWidget(self.txt_keterangan)

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

    def load_data(self):
        d = self.sk_data
        self.spn_tahun.setValue(d.get('tahun_anggaran', TAHUN_ANGGARAN))
        self.txt_nomor_sk.setText(d.get('nomor_sk', ''))
        if d.get('tanggal_sk'):
            self.date_sk.setDate(QDate.fromString(str(d['tanggal_sk']), 'yyyy-MM-dd'))
        self.txt_perihal.setText(d.get('perihal', ''))

        idx = self.cmb_jenis.findData(d.get('jenis_pembayaran', ''))
        if idx >= 0:
            self.cmb_jenis.setCurrentIndex(idx)

        self.spn_nilai.setValue(d.get('nilai_pembayaran', 0))
        self.txt_dasar.setPlainText(d.get('dasar_pembayaran', ''))

        self.txt_kpa_nama.setText(d.get('kpa_nama', ''))
        self.txt_kpa_nip.setText(d.get('kpa_nip', ''))
        self.txt_kpa_jabatan.setText(d.get('kpa_jabatan', ''))
        self.txt_ppk_nama.setText(d.get('ppk_nama', ''))
        self.txt_ppk_nip.setText(d.get('ppk_nip', ''))
        self.txt_ppk_jabatan.setText(d.get('ppk_jabatan', ''))
        self.txt_bendahara_nama.setText(d.get('bendahara_nama', ''))
        self.txt_bendahara_nip.setText(d.get('bendahara_nip', ''))
        self.txt_keterangan.setPlainText(d.get('keterangan', ''))

    def save_data(self):
        if not self.txt_nomor_sk.text().strip():
            QMessageBox.warning(self, "Peringatan", "Nomor SK harus diisi!")
            return

        data = {
            'tahun_anggaran': self.spn_tahun.value(),
            'nomor_sk': self.txt_nomor_sk.text(),
            'tanggal_sk': self.date_sk.date().toString('yyyy-MM-dd'),
            'perihal': self.txt_perihal.text(),
            'jenis_pembayaran': self.cmb_jenis.currentData(),
            'nilai_pembayaran': self.spn_nilai.value(),
            'dasar_pembayaran': self.txt_dasar.toPlainText(),
            'kpa_nama': self.txt_kpa_nama.text(),
            'kpa_nip': self.txt_kpa_nip.text(),
            'kpa_jabatan': self.txt_kpa_jabatan.text(),
            'ppk_nama': self.txt_ppk_nama.text(),
            'ppk_nip': self.txt_ppk_nip.text(),
            'ppk_jabatan': self.txt_ppk_jabatan.text(),
            'bendahara_nama': self.txt_bendahara_nama.text(),
            'bendahara_nip': self.txt_bendahara_nip.text(),
            'keterangan': self.txt_keterangan.toPlainText(),
            'status': 'final'
        }

        try:
            if self.sk_data:
                self.db.update_sk_kpa(self.sk_data['id'], data)
            else:
                self.db.create_sk_kpa(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {str(e)}")


# ============================================================================
# HONORARIUM DIALOG
# ============================================================================

class HonorariumDialog(QDialog):
    """Dialog for Honorarium"""

    JENIS_HONORARIUM = [
        ('narasumber', 'Narasumber'),
        ('moderator', 'Moderator'),
        ('panitia', 'Panitia'),
        ('tim_kerja', 'Tim Kerja'),
        ('penguji', 'Penguji'),
        ('pembimbing', 'Pembimbing'),
        ('lainnya', 'Lainnya')
    ]

    BULAN_NAMES = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    def __init__(self, hon_data: dict = None, parent=None):
        super().__init__(parent)
        self.hon_data = hon_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Tambah Honorarium" if not hon_data else "Edit Honorarium")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setup_ui()

        if hon_data:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Info Kegiatan
        info_group = QGroupBox("Informasi Kegiatan")
        info_form = QFormLayout()

        self.spn_tahun = QSpinBox()
        self.spn_tahun.setRange(2020, 2050)
        self.spn_tahun.setValue(TAHUN_ANGGARAN)
        info_form.addRow("Tahun Anggaran:", self.spn_tahun)

        self.txt_nama_kegiatan = QLineEdit()
        self.txt_nama_kegiatan.setPlaceholderText("Workshop / Seminar / Rapat...")
        info_form.addRow("Nama Kegiatan:", self.txt_nama_kegiatan)

        jenis_layout = QHBoxLayout()
        self.cmb_jenis = QComboBox()
        for code, name in self.JENIS_HONORARIUM:
            self.cmb_jenis.addItem(name, code)
        jenis_layout.addWidget(self.cmb_jenis)
        jenis_layout.addWidget(QLabel("Kategori:"))
        self.cmb_kategori = QComboBox()
        self.cmb_kategori.addItems(["reguler", "insidentil"])
        jenis_layout.addWidget(self.cmb_kategori)
        info_form.addRow("Jenis:", jenis_layout)

        # Periode (untuk reguler)
        periode_layout = QHBoxLayout()
        self.cmb_bulan = QComboBox()
        for i, b in enumerate(self.BULAN_NAMES):
            self.cmb_bulan.addItem(b, i + 1)
        periode_layout.addWidget(QLabel("Bulan:"))
        periode_layout.addWidget(self.cmb_bulan)
        self.date_mulai = QDateEdit()
        self.date_mulai.setCalendarPopup(True)
        self.date_mulai.setDate(QDate.currentDate())
        periode_layout.addWidget(QLabel("Mulai:"))
        periode_layout.addWidget(self.date_mulai)
        self.date_selesai = QDateEdit()
        self.date_selesai.setCalendarPopup(True)
        self.date_selesai.setDate(QDate.currentDate())
        periode_layout.addWidget(QLabel("Selesai:"))
        periode_layout.addWidget(self.date_selesai)
        info_form.addRow("Periode:", periode_layout)

        info_group.setLayout(info_form)
        scroll_layout.addWidget(info_group)

        # SK KPA
        sk_group = QGroupBox("SK KPA")
        sk_form = QFormLayout()

        sk_layout = QHBoxLayout()
        self.txt_nomor_sk = QLineEdit()
        self.txt_nomor_sk.setPlaceholderText("SK-KPA/001/2024")
        sk_layout.addWidget(self.txt_nomor_sk)
        sk_layout.addWidget(QLabel("Tanggal:"))
        self.date_sk = QDateEdit()
        self.date_sk.setCalendarPopup(True)
        self.date_sk.setDate(QDate.currentDate())
        sk_layout.addWidget(self.date_sk)
        sk_form.addRow("SK KPA:", sk_layout)

        spt_layout = QHBoxLayout()
        self.txt_nomor_spt = QLineEdit()
        self.txt_nomor_spt.setPlaceholderText("SPT/001/2024")
        spt_layout.addWidget(self.txt_nomor_spt)
        spt_layout.addWidget(QLabel("Tanggal:"))
        self.date_spt = QDateEdit()
        self.date_spt.setCalendarPopup(True)
        self.date_spt.setDate(QDate.currentDate())
        spt_layout.addWidget(self.date_spt)
        sk_form.addRow("SPT:", spt_layout)

        kuitansi_layout = QHBoxLayout()
        self.txt_nomor_kuitansi = QLineEdit()
        self.txt_nomor_kuitansi.setPlaceholderText("KU/001/2024")
        kuitansi_layout.addWidget(self.txt_nomor_kuitansi)
        kuitansi_layout.addWidget(QLabel("Tanggal:"))
        self.date_kuitansi = QDateEdit()
        self.date_kuitansi.setCalendarPopup(True)
        self.date_kuitansi.setDate(QDate.currentDate())
        kuitansi_layout.addWidget(self.date_kuitansi)
        sk_form.addRow("Kuitansi:", kuitansi_layout)

        sk_group.setLayout(sk_form)
        scroll_layout.addWidget(sk_group)

        # Sumber Dana
        dana_group = QGroupBox("Sumber Dana")
        dana_form = QFormLayout()

        dana_layout = QHBoxLayout()
        self.cmb_sumber_dana = QComboBox()
        self.cmb_sumber_dana.addItems(["DIPA", "BLU", "PNBP", "BOPTN", "Lainnya"])
        dana_layout.addWidget(self.cmb_sumber_dana)
        dana_layout.addWidget(QLabel("Kode Akun:"))
        self.txt_kode_akun = QLineEdit()
        self.txt_kode_akun.setPlaceholderText("521213")
        dana_layout.addWidget(self.txt_kode_akun)
        dana_layout.addWidget(QLabel("MAK:"))
        self.txt_mak = QLineEdit()
        dana_layout.addWidget(self.txt_mak)
        dana_form.addRow("Sumber:", dana_layout)

        dana_group.setLayout(dana_form)
        scroll_layout.addWidget(dana_group)

        # Pejabat
        pejabat_group = QGroupBox("Pejabat")
        pejabat_form = QFormLayout()

        kpa_layout = QHBoxLayout()
        self.txt_kpa_nama = QLineEdit()
        self.txt_kpa_nama.setText(SATKER_DEFAULT.get('kpa_nama', ''))
        kpa_layout.addWidget(self.txt_kpa_nama)
        self.txt_kpa_nip = QLineEdit()
        self.txt_kpa_nip.setText(SATKER_DEFAULT.get('kpa_nip', ''))
        kpa_layout.addWidget(QLabel("NIP:"))
        kpa_layout.addWidget(self.txt_kpa_nip)
        pejabat_form.addRow("KPA:", kpa_layout)

        ppk_layout = QHBoxLayout()
        self.txt_ppk_nama = QLineEdit()
        self.txt_ppk_nama.setText(SATKER_DEFAULT.get('ppk_nama', ''))
        ppk_layout.addWidget(self.txt_ppk_nama)
        self.txt_ppk_nip = QLineEdit()
        self.txt_ppk_nip.setText(SATKER_DEFAULT.get('ppk_nip', ''))
        ppk_layout.addWidget(QLabel("NIP:"))
        ppk_layout.addWidget(self.txt_ppk_nip)
        pejabat_form.addRow("PPK:", ppk_layout)

        bend_layout = QHBoxLayout()
        self.txt_bendahara_nama = QLineEdit()
        self.txt_bendahara_nama.setText(SATKER_DEFAULT.get('bendahara_nama', ''))
        bend_layout.addWidget(self.txt_bendahara_nama)
        self.txt_bendahara_nip = QLineEdit()
        self.txt_bendahara_nip.setText(SATKER_DEFAULT.get('bendahara_nip', ''))
        bend_layout.addWidget(QLabel("NIP:"))
        bend_layout.addWidget(self.txt_bendahara_nip)
        pejabat_form.addRow("Bendahara:", bend_layout)

        pejabat_group.setLayout(pejabat_form)
        scroll_layout.addWidget(pejabat_group)

        # Total
        total_group = QGroupBox("Total Pembayaran")
        total_form = QFormLayout()

        self.spn_total_bruto = CurrencySpinBox()
        total_form.addRow("Total Bruto:", self.spn_total_bruto)

        self.spn_total_pajak = CurrencySpinBox()
        total_form.addRow("Total Pajak (PPh 21):", self.spn_total_pajak)

        self.spn_total_netto = CurrencySpinBox()
        self.spn_total_netto.setReadOnly(True)
        self.spn_total_netto.setStyleSheet("background-color: #ecf0f1;")
        total_form.addRow("Total Netto:", self.spn_total_netto)

        self.spn_total_bruto.valueChanged.connect(self.calc_netto)
        self.spn_total_pajak.valueChanged.connect(self.calc_netto)

        total_group.setLayout(total_form)
        scroll_layout.addWidget(total_group)

        # Keterangan
        self.txt_keterangan = QTextEdit()
        self.txt_keterangan.setMaximumHeight(60)
        scroll_layout.addWidget(QLabel("Keterangan:"))
        scroll_layout.addWidget(self.txt_keterangan)

        scroll_layout.addStretch()
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

    def calc_netto(self):
        self.spn_total_netto.setValue(self.spn_total_bruto.value() - self.spn_total_pajak.value())

    def load_data(self):
        d = self.hon_data
        self.spn_tahun.setValue(d.get('tahun_anggaran', TAHUN_ANGGARAN))
        self.txt_nama_kegiatan.setText(d.get('nama_kegiatan', ''))

        idx = self.cmb_jenis.findData(d.get('jenis_honorarium', ''))
        if idx >= 0:
            self.cmb_jenis.setCurrentIndex(idx)

        self.cmb_kategori.setCurrentText(d.get('kategori', 'reguler'))

        if d.get('bulan'):
            self.cmb_bulan.setCurrentIndex(d['bulan'] - 1)
        if d.get('periode_mulai'):
            self.date_mulai.setDate(QDate.fromString(str(d['periode_mulai']), 'yyyy-MM-dd'))
        if d.get('periode_selesai'):
            self.date_selesai.setDate(QDate.fromString(str(d['periode_selesai']), 'yyyy-MM-dd'))

        self.txt_nomor_sk.setText(d.get('nomor_sk_kpa', ''))
        if d.get('tanggal_sk_kpa'):
            self.date_sk.setDate(QDate.fromString(str(d['tanggal_sk_kpa']), 'yyyy-MM-dd'))
        self.txt_nomor_spt.setText(d.get('nomor_spt', ''))
        if d.get('tanggal_spt'):
            self.date_spt.setDate(QDate.fromString(str(d['tanggal_spt']), 'yyyy-MM-dd'))
        self.txt_nomor_kuitansi.setText(d.get('nomor_kuitansi', ''))
        if d.get('tanggal_kuitansi'):
            self.date_kuitansi.setDate(QDate.fromString(str(d['tanggal_kuitansi']), 'yyyy-MM-dd'))

        self.cmb_sumber_dana.setCurrentText(d.get('sumber_dana', 'DIPA'))
        self.txt_kode_akun.setText(d.get('kode_akun', ''))
        self.txt_mak.setText(d.get('mak', ''))

        self.txt_kpa_nama.setText(d.get('kpa_nama', ''))
        self.txt_kpa_nip.setText(d.get('kpa_nip', ''))
        self.txt_ppk_nama.setText(d.get('ppk_nama', ''))
        self.txt_ppk_nip.setText(d.get('ppk_nip', ''))
        self.txt_bendahara_nama.setText(d.get('bendahara_nama', ''))
        self.txt_bendahara_nip.setText(d.get('bendahara_nip', ''))

        self.spn_total_bruto.setValue(d.get('total_bruto', 0))
        self.spn_total_pajak.setValue(d.get('total_pajak', 0))
        self.spn_total_netto.setValue(d.get('total_netto', 0))

        self.txt_keterangan.setPlainText(d.get('keterangan', ''))

    def save_data(self):
        if not self.txt_nama_kegiatan.text().strip():
            QMessageBox.warning(self, "Peringatan", "Nama kegiatan harus diisi!")
            return

        data = {
            'tahun_anggaran': self.spn_tahun.value(),
            'nama_kegiatan': self.txt_nama_kegiatan.text(),
            'jenis_honorarium': self.cmb_jenis.currentData(),
            'kategori': self.cmb_kategori.currentText(),
            'bulan': self.cmb_bulan.currentData(),
            'periode_mulai': self.date_mulai.date().toString('yyyy-MM-dd'),
            'periode_selesai': self.date_selesai.date().toString('yyyy-MM-dd'),
            'nomor_sk_kpa': self.txt_nomor_sk.text(),
            'tanggal_sk_kpa': self.date_sk.date().toString('yyyy-MM-dd'),
            'nomor_spt': self.txt_nomor_spt.text(),
            'tanggal_spt': self.date_spt.date().toString('yyyy-MM-dd'),
            'nomor_kuitansi': self.txt_nomor_kuitansi.text(),
            'tanggal_kuitansi': self.date_kuitansi.date().toString('yyyy-MM-dd'),
            'sumber_dana': self.cmb_sumber_dana.currentText(),
            'kode_akun': self.txt_kode_akun.text(),
            'mak': self.txt_mak.text(),
            'kpa_nama': self.txt_kpa_nama.text(),
            'kpa_nip': self.txt_kpa_nip.text(),
            'ppk_nama': self.txt_ppk_nama.text(),
            'ppk_nip': self.txt_ppk_nip.text(),
            'bendahara_nama': self.txt_bendahara_nama.text(),
            'bendahara_nip': self.txt_bendahara_nip.text(),
            'total_bruto': self.spn_total_bruto.value(),
            'total_pajak': self.spn_total_pajak.value(),
            'total_netto': self.spn_total_netto.value(),
            'keterangan': self.txt_keterangan.toPlainText(),
            'status': 'draft'
        }

        try:
            if self.hon_data:
                self.db.update_honorarium(self.hon_data['id'], data)
            else:
                self.db.create_honorarium(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {str(e)}")


# ============================================================================
# JAMUAN TAMU DIALOG
# ============================================================================

class JamuanTamuDialog(QDialog):
    """Dialog for Jamuan Tamu"""

    def __init__(self, jt_data: dict = None, parent=None):
        super().__init__(parent)
        self.jt_data = jt_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Tambah Jamuan Tamu" if not jt_data else "Edit Jamuan Tamu")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setup_ui()

        if jt_data:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Info Kegiatan
        info_group = QGroupBox("Informasi Kegiatan")
        info_form = QFormLayout()

        self.spn_tahun = QSpinBox()
        self.spn_tahun.setRange(2020, 2050)
        self.spn_tahun.setValue(TAHUN_ANGGARAN)
        info_form.addRow("Tahun Anggaran:", self.spn_tahun)

        self.txt_nama_kegiatan = QLineEdit()
        self.txt_nama_kegiatan.setPlaceholderText("Penerimaan Tamu / Rapat Koordinasi...")
        info_form.addRow("Nama Kegiatan:", self.txt_nama_kegiatan)

        tgl_layout = QHBoxLayout()
        self.date_kegiatan = QDateEdit()
        self.date_kegiatan.setCalendarPopup(True)
        self.date_kegiatan.setDate(QDate.currentDate())
        tgl_layout.addWidget(self.date_kegiatan)
        tgl_layout.addWidget(QLabel("Kategori:"))
        self.cmb_kategori = QComboBox()
        self.cmb_kategori.addItems(["reguler", "insidentil"])
        tgl_layout.addWidget(self.cmb_kategori)
        info_form.addRow("Tanggal:", tgl_layout)

        self.txt_tempat = QLineEdit()
        self.txt_tempat.setPlaceholderText("Ruang Rapat / Restoran...")
        info_form.addRow("Tempat:", self.txt_tempat)

        info_group.setLayout(info_form)
        scroll_layout.addWidget(info_group)

        # Data Tamu
        tamu_group = QGroupBox("Data Tamu")
        tamu_form = QFormLayout()

        self.txt_nama_tamu = QLineEdit()
        self.txt_nama_tamu.setPlaceholderText("Nama tamu / rombongan")
        tamu_form.addRow("Nama Tamu:", self.txt_nama_tamu)

        self.txt_instansi_tamu = QLineEdit()
        tamu_form.addRow("Instansi:", self.txt_instansi_tamu)

        jab_layout = QHBoxLayout()
        self.txt_jabatan_tamu = QLineEdit()
        jab_layout.addWidget(self.txt_jabatan_tamu)
        jab_layout.addWidget(QLabel("Jumlah:"))
        self.spn_jumlah_tamu = QSpinBox()
        self.spn_jumlah_tamu.setRange(1, 1000)
        self.spn_jumlah_tamu.setValue(1)
        self.spn_jumlah_tamu.setSuffix(" orang")
        jab_layout.addWidget(self.spn_jumlah_tamu)
        tamu_form.addRow("Jabatan:", jab_layout)

        tamu_group.setLayout(tamu_form)
        scroll_layout.addWidget(tamu_group)

        # Dokumen
        dok_group = QGroupBox("Dokumen")
        dok_form = QFormLayout()

        sk_layout = QHBoxLayout()
        self.txt_nomor_sk = QLineEdit()
        self.txt_nomor_sk.setPlaceholderText("SK-KPA/001/2024")
        sk_layout.addWidget(self.txt_nomor_sk)
        sk_layout.addWidget(QLabel("Tanggal:"))
        self.date_sk = QDateEdit()
        self.date_sk.setCalendarPopup(True)
        self.date_sk.setDate(QDate.currentDate())
        sk_layout.addWidget(self.date_sk)
        dok_form.addRow("SK KPA:", sk_layout)

        nd_layout = QHBoxLayout()
        self.txt_nomor_nd = QLineEdit()
        self.txt_nomor_nd.setPlaceholderText("ND/001/2024")
        nd_layout.addWidget(self.txt_nomor_nd)
        nd_layout.addWidget(QLabel("Tanggal:"))
        self.date_nd = QDateEdit()
        self.date_nd.setCalendarPopup(True)
        self.date_nd.setDate(QDate.currentDate())
        nd_layout.addWidget(self.date_nd)
        dok_form.addRow("Nota Dinas:", nd_layout)

        ku_layout = QHBoxLayout()
        self.txt_nomor_kuitansi = QLineEdit()
        self.txt_nomor_kuitansi.setPlaceholderText("KU/001/2024")
        ku_layout.addWidget(self.txt_nomor_kuitansi)
        ku_layout.addWidget(QLabel("Tanggal:"))
        self.date_kuitansi = QDateEdit()
        self.date_kuitansi.setCalendarPopup(True)
        self.date_kuitansi.setDate(QDate.currentDate())
        ku_layout.addWidget(self.date_kuitansi)
        dok_form.addRow("Kuitansi:", ku_layout)

        dok_group.setLayout(dok_form)
        scroll_layout.addWidget(dok_group)

        # Sumber Dana
        dana_group = QGroupBox("Sumber Dana")
        dana_form = QFormLayout()

        dana_layout = QHBoxLayout()
        self.cmb_sumber_dana = QComboBox()
        self.cmb_sumber_dana.addItems(["DIPA", "BLU", "PNBP", "BOPTN", "Lainnya"])
        dana_layout.addWidget(self.cmb_sumber_dana)
        dana_layout.addWidget(QLabel("Kode Akun:"))
        self.txt_kode_akun = QLineEdit()
        self.txt_kode_akun.setPlaceholderText("521111")
        dana_layout.addWidget(self.txt_kode_akun)
        dana_layout.addWidget(QLabel("MAK:"))
        self.txt_mak = QLineEdit()
        dana_layout.addWidget(self.txt_mak)
        dana_form.addRow("Sumber:", dana_layout)

        dana_group.setLayout(dana_form)
        scroll_layout.addWidget(dana_group)

        # Pejabat
        pejabat_group = QGroupBox("Pejabat")
        pejabat_form = QFormLayout()

        kpa_layout = QHBoxLayout()
        self.txt_kpa_nama = QLineEdit()
        self.txt_kpa_nama.setText(SATKER_DEFAULT.get('kpa_nama', ''))
        kpa_layout.addWidget(self.txt_kpa_nama)
        self.txt_kpa_nip = QLineEdit()
        self.txt_kpa_nip.setText(SATKER_DEFAULT.get('kpa_nip', ''))
        kpa_layout.addWidget(QLabel("NIP:"))
        kpa_layout.addWidget(self.txt_kpa_nip)
        pejabat_form.addRow("KPA:", kpa_layout)

        ppk_layout = QHBoxLayout()
        self.txt_ppk_nama = QLineEdit()
        self.txt_ppk_nama.setText(SATKER_DEFAULT.get('ppk_nama', ''))
        ppk_layout.addWidget(self.txt_ppk_nama)
        self.txt_ppk_nip = QLineEdit()
        self.txt_ppk_nip.setText(SATKER_DEFAULT.get('ppk_nip', ''))
        ppk_layout.addWidget(QLabel("NIP:"))
        ppk_layout.addWidget(self.txt_ppk_nip)
        pejabat_form.addRow("PPK:", ppk_layout)

        bend_layout = QHBoxLayout()
        self.txt_bendahara_nama = QLineEdit()
        self.txt_bendahara_nama.setText(SATKER_DEFAULT.get('bendahara_nama', ''))
        bend_layout.addWidget(self.txt_bendahara_nama)
        self.txt_bendahara_nip = QLineEdit()
        self.txt_bendahara_nip.setText(SATKER_DEFAULT.get('bendahara_nip', ''))
        bend_layout.addWidget(QLabel("NIP:"))
        bend_layout.addWidget(self.txt_bendahara_nip)
        pejabat_form.addRow("Bendahara:", bend_layout)

        pejabat_group.setLayout(pejabat_form)
        scroll_layout.addWidget(pejabat_group)

        # Biaya
        biaya_group = QGroupBox("Rincian Biaya")
        biaya_form = QFormLayout()

        self.spn_konsumsi = CurrencySpinBox()
        self.spn_konsumsi.valueChanged.connect(self.calc_total)
        biaya_form.addRow("Biaya Konsumsi:", self.spn_konsumsi)

        self.spn_akomodasi = CurrencySpinBox()
        self.spn_akomodasi.valueChanged.connect(self.calc_total)
        biaya_form.addRow("Biaya Akomodasi:", self.spn_akomodasi)

        self.spn_transportasi = CurrencySpinBox()
        self.spn_transportasi.valueChanged.connect(self.calc_total)
        biaya_form.addRow("Biaya Transportasi:", self.spn_transportasi)

        self.spn_lainnya = CurrencySpinBox()
        self.spn_lainnya.valueChanged.connect(self.calc_total)
        biaya_form.addRow("Biaya Lainnya:", self.spn_lainnya)

        self.spn_total = CurrencySpinBox()
        self.spn_total.setReadOnly(True)
        self.spn_total.setStyleSheet("background-color: #d4edda; font-weight: bold;")
        biaya_form.addRow("Total Biaya:", self.spn_total)

        biaya_group.setLayout(biaya_form)
        scroll_layout.addWidget(biaya_group)

        # Keterangan
        self.txt_keterangan = QTextEdit()
        self.txt_keterangan.setMaximumHeight(60)
        scroll_layout.addWidget(QLabel("Keterangan:"))
        scroll_layout.addWidget(self.txt_keterangan)

        scroll_layout.addStretch()
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

    def calc_total(self):
        total = (self.spn_konsumsi.value() + self.spn_akomodasi.value() +
                 self.spn_transportasi.value() + self.spn_lainnya.value())
        self.spn_total.setValue(total)

    def load_data(self):
        d = self.jt_data
        self.spn_tahun.setValue(d.get('tahun_anggaran', TAHUN_ANGGARAN))
        self.txt_nama_kegiatan.setText(d.get('nama_kegiatan', ''))
        if d.get('tanggal_kegiatan'):
            self.date_kegiatan.setDate(QDate.fromString(str(d['tanggal_kegiatan']), 'yyyy-MM-dd'))
        self.cmb_kategori.setCurrentText(d.get('kategori', 'reguler'))
        self.txt_tempat.setText(d.get('tempat', ''))

        self.txt_nama_tamu.setText(d.get('nama_tamu', ''))
        self.txt_instansi_tamu.setText(d.get('instansi_tamu', ''))
        self.txt_jabatan_tamu.setText(d.get('jabatan_tamu', ''))
        self.spn_jumlah_tamu.setValue(d.get('jumlah_tamu', 1))

        self.txt_nomor_sk.setText(d.get('nomor_sk_kpa', ''))
        if d.get('tanggal_sk_kpa'):
            self.date_sk.setDate(QDate.fromString(str(d['tanggal_sk_kpa']), 'yyyy-MM-dd'))
        self.txt_nomor_nd.setText(d.get('nomor_nota_dinas', ''))
        if d.get('tanggal_nota_dinas'):
            self.date_nd.setDate(QDate.fromString(str(d['tanggal_nota_dinas']), 'yyyy-MM-dd'))
        self.txt_nomor_kuitansi.setText(d.get('nomor_kuitansi', ''))
        if d.get('tanggal_kuitansi'):
            self.date_kuitansi.setDate(QDate.fromString(str(d['tanggal_kuitansi']), 'yyyy-MM-dd'))

        self.cmb_sumber_dana.setCurrentText(d.get('sumber_dana', 'DIPA'))
        self.txt_kode_akun.setText(d.get('kode_akun', ''))
        self.txt_mak.setText(d.get('mak', ''))

        self.txt_kpa_nama.setText(d.get('kpa_nama', ''))
        self.txt_kpa_nip.setText(d.get('kpa_nip', ''))
        self.txt_ppk_nama.setText(d.get('ppk_nama', ''))
        self.txt_ppk_nip.setText(d.get('ppk_nip', ''))
        self.txt_bendahara_nama.setText(d.get('bendahara_nama', ''))
        self.txt_bendahara_nip.setText(d.get('bendahara_nip', ''))

        self.spn_konsumsi.setValue(d.get('biaya_konsumsi', 0))
        self.spn_akomodasi.setValue(d.get('biaya_akomodasi', 0))
        self.spn_transportasi.setValue(d.get('biaya_transportasi', 0))
        self.spn_lainnya.setValue(d.get('biaya_lainnya', 0))
        self.spn_total.setValue(d.get('total_biaya', 0))

        self.txt_keterangan.setPlainText(d.get('keterangan', ''))

    def save_data(self):
        if not self.txt_nama_kegiatan.text().strip():
            QMessageBox.warning(self, "Peringatan", "Nama kegiatan harus diisi!")
            return

        data = {
            'tahun_anggaran': self.spn_tahun.value(),
            'nama_kegiatan': self.txt_nama_kegiatan.text(),
            'tanggal_kegiatan': self.date_kegiatan.date().toString('yyyy-MM-dd'),
            'tempat': self.txt_tempat.text(),
            'kategori': self.cmb_kategori.currentText(),
            'nama_tamu': self.txt_nama_tamu.text(),
            'instansi_tamu': self.txt_instansi_tamu.text(),
            'jabatan_tamu': self.txt_jabatan_tamu.text(),
            'jumlah_tamu': self.spn_jumlah_tamu.value(),
            'nomor_sk_kpa': self.txt_nomor_sk.text(),
            'tanggal_sk_kpa': self.date_sk.date().toString('yyyy-MM-dd'),
            'nomor_nota_dinas': self.txt_nomor_nd.text(),
            'tanggal_nota_dinas': self.date_nd.date().toString('yyyy-MM-dd'),
            'nomor_kuitansi': self.txt_nomor_kuitansi.text(),
            'tanggal_kuitansi': self.date_kuitansi.date().toString('yyyy-MM-dd'),
            'sumber_dana': self.cmb_sumber_dana.currentText(),
            'kode_akun': self.txt_kode_akun.text(),
            'mak': self.txt_mak.text(),
            'kpa_nama': self.txt_kpa_nama.text(),
            'kpa_nip': self.txt_kpa_nip.text(),
            'ppk_nama': self.txt_ppk_nama.text(),
            'ppk_nip': self.txt_ppk_nip.text(),
            'bendahara_nama': self.txt_bendahara_nama.text(),
            'bendahara_nip': self.txt_bendahara_nip.text(),
            'biaya_konsumsi': self.spn_konsumsi.value(),
            'biaya_akomodasi': self.spn_akomodasi.value(),
            'biaya_transportasi': self.spn_transportasi.value(),
            'biaya_lainnya': self.spn_lainnya.value(),
            'total_biaya': self.spn_total.value(),
            'keterangan': self.txt_keterangan.toPlainText(),
            'status': 'draft'
        }

        try:
            if self.jt_data:
                self.db.update_jamuan_tamu(self.jt_data['id'], data)
            else:
                self.db.create_jamuan_tamu(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {str(e)}")


# ============================================================================
# PEMBAYARAN LAINNYA MANAGER (Main Widget)
# ============================================================================

class PembayaranLainnyaManager(QWidget):
    """Main manager for SK KPA, Honorarium, and Jamuan Tamu"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db_manager_v4()
        self.setup_ui()
        self.refresh_all()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Pembayaran Lainnya")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()

        # ========== TAB 1: SK KPA ==========
        tab_sk = QWidget()
        sk_layout = QVBoxLayout(tab_sk)

        sk_toolbar = QHBoxLayout()
        btn_add_sk = QPushButton("+ Buat SK KPA")
        btn_add_sk.setStyleSheet("background-color: #3498db; color: white; padding: 8px 16px;")
        btn_add_sk.clicked.connect(self.add_sk_kpa)
        sk_toolbar.addWidget(btn_add_sk)
        sk_toolbar.addStretch()

        sk_toolbar.addWidget(QLabel("Tahun:"))
        self.cmb_sk_tahun = QComboBox()
        self.cmb_sk_tahun.addItem("Semua", None)
        for y in range(TAHUN_ANGGARAN - 2, TAHUN_ANGGARAN + 3):
            self.cmb_sk_tahun.addItem(str(y), y)
        self.cmb_sk_tahun.setCurrentText(str(TAHUN_ANGGARAN))
        self.cmb_sk_tahun.currentIndexChanged.connect(self.refresh_sk_kpa)
        sk_toolbar.addWidget(self.cmb_sk_tahun)

        sk_layout.addLayout(sk_toolbar)

        self.tbl_sk = QTableWidget()
        self.tbl_sk.setColumnCount(7)
        self.tbl_sk.setHorizontalHeaderLabels([
            "ID", "Nomor SK", "Tanggal", "Perihal", "Jenis", "Nilai", "Aksi"
        ])
        self.tbl_sk.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_sk.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_sk.horizontalHeader().setStretchLastSection(True)
        self.tbl_sk.setColumnWidth(0, 50)
        self.tbl_sk.setColumnWidth(1, 150)
        self.tbl_sk.setColumnWidth(2, 100)
        self.tbl_sk.setColumnWidth(3, 250)
        self.tbl_sk.setColumnWidth(4, 100)
        self.tbl_sk.setColumnWidth(5, 120)
        sk_layout.addWidget(self.tbl_sk)

        self.tabs.addTab(tab_sk, "SK KPA")

        # ========== TAB 2: HONORARIUM ==========
        tab_hon = QWidget()
        hon_layout = QVBoxLayout(tab_hon)

        hon_toolbar = QHBoxLayout()
        btn_add_hon = QPushButton("+ Tambah Honorarium")
        btn_add_hon.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 16px;")
        btn_add_hon.clicked.connect(self.add_honorarium)
        hon_toolbar.addWidget(btn_add_hon)
        hon_toolbar.addStretch()

        hon_toolbar.addWidget(QLabel("Kategori:"))
        self.cmb_hon_kategori = QComboBox()
        self.cmb_hon_kategori.addItem("Semua", None)
        self.cmb_hon_kategori.addItems(["reguler", "insidentil"])
        self.cmb_hon_kategori.currentIndexChanged.connect(self.refresh_honorarium)
        hon_toolbar.addWidget(self.cmb_hon_kategori)

        hon_toolbar.addWidget(QLabel("Tahun:"))
        self.cmb_hon_tahun = QComboBox()
        self.cmb_hon_tahun.addItem("Semua", None)
        for y in range(TAHUN_ANGGARAN - 2, TAHUN_ANGGARAN + 3):
            self.cmb_hon_tahun.addItem(str(y), y)
        self.cmb_hon_tahun.setCurrentText(str(TAHUN_ANGGARAN))
        self.cmb_hon_tahun.currentIndexChanged.connect(self.refresh_honorarium)
        hon_toolbar.addWidget(self.cmb_hon_tahun)

        hon_layout.addLayout(hon_toolbar)

        self.tbl_hon = QTableWidget()
        self.tbl_hon.setColumnCount(8)
        self.tbl_hon.setHorizontalHeaderLabels([
            "ID", "Kegiatan", "Jenis", "Kategori", "SK KPA", "Total Bruto", "Status", "Aksi"
        ])
        self.tbl_hon.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_hon.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_hon.horizontalHeader().setStretchLastSection(True)
        hon_layout.addWidget(self.tbl_hon)

        self.tabs.addTab(tab_hon, "Honorarium")

        # ========== TAB 3: JAMUAN TAMU ==========
        tab_jt = QWidget()
        jt_layout = QVBoxLayout(tab_jt)

        jt_toolbar = QHBoxLayout()
        btn_add_jt = QPushButton("+ Tambah Jamuan Tamu")
        btn_add_jt.setStyleSheet("background-color: #e67e22; color: white; padding: 8px 16px;")
        btn_add_jt.clicked.connect(self.add_jamuan_tamu)
        jt_toolbar.addWidget(btn_add_jt)
        jt_toolbar.addStretch()

        jt_toolbar.addWidget(QLabel("Kategori:"))
        self.cmb_jt_kategori = QComboBox()
        self.cmb_jt_kategori.addItem("Semua", None)
        self.cmb_jt_kategori.addItems(["reguler", "insidentil"])
        self.cmb_jt_kategori.currentIndexChanged.connect(self.refresh_jamuan_tamu)
        jt_toolbar.addWidget(self.cmb_jt_kategori)

        jt_toolbar.addWidget(QLabel("Tahun:"))
        self.cmb_jt_tahun = QComboBox()
        self.cmb_jt_tahun.addItem("Semua", None)
        for y in range(TAHUN_ANGGARAN - 2, TAHUN_ANGGARAN + 3):
            self.cmb_jt_tahun.addItem(str(y), y)
        self.cmb_jt_tahun.setCurrentText(str(TAHUN_ANGGARAN))
        self.cmb_jt_tahun.currentIndexChanged.connect(self.refresh_jamuan_tamu)
        jt_toolbar.addWidget(self.cmb_jt_tahun)

        jt_layout.addLayout(jt_toolbar)

        self.tbl_jt = QTableWidget()
        self.tbl_jt.setColumnCount(8)
        self.tbl_jt.setHorizontalHeaderLabels([
            "ID", "Kegiatan", "Tanggal", "Tamu", "Kategori", "Total Biaya", "Status", "Aksi"
        ])
        self.tbl_jt.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_jt.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_jt.horizontalHeader().setStretchLastSection(True)
        jt_layout.addWidget(self.tbl_jt)

        self.tabs.addTab(tab_jt, "Jamuan Tamu")

        layout.addWidget(self.tabs)

    def format_currency(self, value):
        return f"Rp {value:,.0f}".replace(",", ".")

    def refresh_all(self):
        self.refresh_sk_kpa()
        self.refresh_honorarium()
        self.refresh_jamuan_tamu()

    def refresh_sk_kpa(self):
        tahun = self.cmb_sk_tahun.currentData()
        data = self.db.get_all_sk_kpa(tahun=tahun)
        self.tbl_sk.setRowCount(len(data))

        for row, d in enumerate(data):
            self.tbl_sk.setItem(row, 0, QTableWidgetItem(str(d['id'])))
            self.tbl_sk.setItem(row, 1, QTableWidgetItem(d.get('nomor_sk', '')))
            self.tbl_sk.setItem(row, 2, QTableWidgetItem(str(d.get('tanggal_sk', ''))))
            self.tbl_sk.setItem(row, 3, QTableWidgetItem(d.get('perihal', '')))
            self.tbl_sk.setItem(row, 4, QTableWidgetItem(d.get('jenis_pembayaran', '')))
            self.tbl_sk.setItem(row, 5, QTableWidgetItem(self.format_currency(d.get('nilai_pembayaran', 0))))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background: #3498db; color: white; padding: 2px 8px;")
            btn_edit.clicked.connect(lambda checked, r=row: self.edit_sk_kpa(r))
            btn_layout.addWidget(btn_edit)

            btn_del = QPushButton("Hapus")
            btn_del.setStyleSheet("background: #e74c3c; color: white; padding: 2px 8px;")
            btn_del.clicked.connect(lambda checked, r=row: self.delete_sk_kpa(r))
            btn_layout.addWidget(btn_del)

            self.tbl_sk.setCellWidget(row, 6, btn_widget)

    def add_sk_kpa(self):
        dialog = SKKPADialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_sk_kpa()
            QMessageBox.information(self, "Sukses", "SK KPA berhasil ditambahkan!")

    def edit_sk_kpa(self, row):
        sk_id = int(self.tbl_sk.item(row, 0).text())
        sk_data = self.db.get_sk_kpa(sk_id)
        if sk_data:
            dialog = SKKPADialog(sk_data, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_sk_kpa()

    def delete_sk_kpa(self, row):
        sk_id = int(self.tbl_sk.item(row, 0).text())
        reply = QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus SK KPA ini?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_sk_kpa(sk_id):
                self.refresh_sk_kpa()

    def refresh_honorarium(self):
        tahun = self.cmb_hon_tahun.currentData()
        kategori = self.cmb_hon_kategori.currentText()
        if kategori == "Semua":
            kategori = None
        data = self.db.get_all_honorarium(tahun=tahun, kategori=kategori)
        self.tbl_hon.setRowCount(len(data))

        for row, d in enumerate(data):
            self.tbl_hon.setItem(row, 0, QTableWidgetItem(str(d['id'])))
            self.tbl_hon.setItem(row, 1, QTableWidgetItem(d.get('nama_kegiatan', '')))
            self.tbl_hon.setItem(row, 2, QTableWidgetItem(d.get('jenis_honorarium', '')))

            kat_item = QTableWidgetItem(d.get('kategori', ''))
            if d.get('kategori') == 'reguler':
                kat_item.setBackground(QColor('#d4edda'))
            else:
                kat_item.setBackground(QColor('#fff3cd'))
            self.tbl_hon.setItem(row, 3, kat_item)

            self.tbl_hon.setItem(row, 4, QTableWidgetItem(d.get('nomor_sk_kpa', '')))
            self.tbl_hon.setItem(row, 5, QTableWidgetItem(self.format_currency(d.get('total_bruto', 0))))
            self.tbl_hon.setItem(row, 6, QTableWidgetItem(d.get('status', '')))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background: #3498db; color: white; padding: 2px 8px;")
            btn_edit.clicked.connect(lambda checked, r=row: self.edit_honorarium(r))
            btn_layout.addWidget(btn_edit)

            btn_del = QPushButton("Hapus")
            btn_del.setStyleSheet("background: #e74c3c; color: white; padding: 2px 8px;")
            btn_del.clicked.connect(lambda checked, r=row: self.delete_honorarium(r))
            btn_layout.addWidget(btn_del)

            self.tbl_hon.setCellWidget(row, 7, btn_widget)

    def add_honorarium(self):
        dialog = HonorariumDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_honorarium()
            QMessageBox.information(self, "Sukses", "Honorarium berhasil ditambahkan!")

    def edit_honorarium(self, row):
        hon_id = int(self.tbl_hon.item(row, 0).text())
        hon_data = self.db.get_honorarium(hon_id)
        if hon_data:
            dialog = HonorariumDialog(hon_data, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_honorarium()

    def delete_honorarium(self, row):
        hon_id = int(self.tbl_hon.item(row, 0).text())
        reply = QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus Honorarium ini?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_honorarium(hon_id):
                self.refresh_honorarium()

    def refresh_jamuan_tamu(self):
        tahun = self.cmb_jt_tahun.currentData()
        kategori = self.cmb_jt_kategori.currentText()
        if kategori == "Semua":
            kategori = None
        data = self.db.get_all_jamuan_tamu(tahun=tahun, kategori=kategori)
        self.tbl_jt.setRowCount(len(data))

        for row, d in enumerate(data):
            self.tbl_jt.setItem(row, 0, QTableWidgetItem(str(d['id'])))
            self.tbl_jt.setItem(row, 1, QTableWidgetItem(d.get('nama_kegiatan', '')))
            self.tbl_jt.setItem(row, 2, QTableWidgetItem(str(d.get('tanggal_kegiatan', ''))))
            self.tbl_jt.setItem(row, 3, QTableWidgetItem(d.get('nama_tamu', '')))

            kat_item = QTableWidgetItem(d.get('kategori', ''))
            if d.get('kategori') == 'reguler':
                kat_item.setBackground(QColor('#d4edda'))
            else:
                kat_item.setBackground(QColor('#fff3cd'))
            self.tbl_jt.setItem(row, 4, kat_item)

            self.tbl_jt.setItem(row, 5, QTableWidgetItem(self.format_currency(d.get('total_biaya', 0))))
            self.tbl_jt.setItem(row, 6, QTableWidgetItem(d.get('status', '')))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background: #3498db; color: white; padding: 2px 8px;")
            btn_edit.clicked.connect(lambda checked, r=row: self.edit_jamuan_tamu(r))
            btn_layout.addWidget(btn_edit)

            btn_del = QPushButton("Hapus")
            btn_del.setStyleSheet("background: #e74c3c; color: white; padding: 2px 8px;")
            btn_del.clicked.connect(lambda checked, r=row: self.delete_jamuan_tamu(r))
            btn_layout.addWidget(btn_del)

            self.tbl_jt.setCellWidget(row, 7, btn_widget)

    def add_jamuan_tamu(self):
        dialog = JamuanTamuDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_jamuan_tamu()
            QMessageBox.information(self, "Sukses", "Jamuan Tamu berhasil ditambahkan!")

    def edit_jamuan_tamu(self, row):
        jt_id = int(self.tbl_jt.item(row, 0).text())
        jt_data = self.db.get_jamuan_tamu(jt_id)
        if jt_data:
            dialog = JamuanTamuDialog(jt_data, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_jamuan_tamu()

    def delete_jamuan_tamu(self, row):
        jt_id = int(self.tbl_jt.item(row, 0).text())
        reply = QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus Jamuan Tamu ini?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_jamuan_tamu(jt_id):
                self.refresh_jamuan_tamu()
