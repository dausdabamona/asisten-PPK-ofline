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

        # Pejabat Group - ambil dari master data
        pejabat = self.db.get_satker_pejabat()
        pejabat_group = QGroupBox("Data Pejabat")
        pejabat_form = QFormLayout()

        # KPA
        self.txt_kpa_nama = QLineEdit()
        self.txt_kpa_nama.setText(pejabat.get('kpa_nama', ''))
        pejabat_form.addRow("Nama KPA:", self.txt_kpa_nama)

        kpa_layout = QHBoxLayout()
        self.txt_kpa_nip = QLineEdit()
        self.txt_kpa_nip.setText(pejabat.get('kpa_nip', ''))
        kpa_layout.addWidget(QLabel("NIP:"))
        kpa_layout.addWidget(self.txt_kpa_nip)
        self.txt_kpa_jabatan = QLineEdit()
        self.txt_kpa_jabatan.setText(pejabat.get('kpa_jabatan', '') or 'Kuasa Pengguna Anggaran')
        kpa_layout.addWidget(QLabel("Jabatan:"))
        kpa_layout.addWidget(self.txt_kpa_jabatan)
        pejabat_form.addRow("", kpa_layout)

        # PPK
        self.txt_ppk_nama = QLineEdit()
        self.txt_ppk_nama.setText(pejabat.get('ppk_nama', ''))
        pejabat_form.addRow("Nama PPK:", self.txt_ppk_nama)

        ppk_layout = QHBoxLayout()
        self.txt_ppk_nip = QLineEdit()
        self.txt_ppk_nip.setText(pejabat.get('ppk_nip', ''))
        ppk_layout.addWidget(QLabel("NIP:"))
        ppk_layout.addWidget(self.txt_ppk_nip)
        self.txt_ppk_jabatan = QLineEdit()
        self.txt_ppk_jabatan.setText(pejabat.get('ppk_jabatan', '') or 'Pejabat Pembuat Komitmen')
        ppk_layout.addWidget(QLabel("Jabatan:"))
        ppk_layout.addWidget(self.txt_ppk_jabatan)
        pejabat_form.addRow("", ppk_layout)

        # Bendahara
        bend_layout = QHBoxLayout()
        self.txt_bendahara_nama = QLineEdit()
        self.txt_bendahara_nama.setText(pejabat.get('bendahara_nama', ''))
        bend_layout.addWidget(QLabel("Nama:"))
        bend_layout.addWidget(self.txt_bendahara_nama)
        self.txt_bendahara_nip = QLineEdit()
        self.txt_bendahara_nip.setText(pejabat.get('bendahara_nip', ''))
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

        # Pejabat - Hybrid approach dengan ComboBox dan editable text
        pejabat_default = self.db.get_satker_pejabat()
        pejabat_group = QGroupBox("Pejabat")
        pejabat_form = QFormLayout()

        # KPA
        self.cmb_kpa = QComboBox()
        self.cmb_kpa.setEditable(True)
        self._load_kpa_combo()
        self.cmb_kpa.currentIndexChanged.connect(self._on_kpa_selected)
        pejabat_form.addRow("Pilih KPA:", self.cmb_kpa)

        kpa_layout = QHBoxLayout()
        self.txt_kpa_nama = QLineEdit()
        self.txt_kpa_nama.setText(pejabat_default.get('kpa_nama', ''))
        kpa_layout.addWidget(self.txt_kpa_nama)
        self.txt_kpa_nip = QLineEdit()
        self.txt_kpa_nip.setText(pejabat_default.get('kpa_nip', ''))
        kpa_layout.addWidget(QLabel("NIP:"))
        kpa_layout.addWidget(self.txt_kpa_nip)
        pejabat_form.addRow("KPA:", kpa_layout)

        # PPK
        self.cmb_ppk = QComboBox()
        self.cmb_ppk.setEditable(True)
        self._load_ppk_combo()
        self.cmb_ppk.currentIndexChanged.connect(self._on_ppk_selected)
        pejabat_form.addRow("Pilih PPK:", self.cmb_ppk)

        ppk_layout = QHBoxLayout()
        self.txt_ppk_nama = QLineEdit()
        self.txt_ppk_nama.setText(pejabat_default.get('ppk_nama', ''))
        ppk_layout.addWidget(self.txt_ppk_nama)
        self.txt_ppk_nip = QLineEdit()
        self.txt_ppk_nip.setText(pejabat_default.get('ppk_nip', ''))
        ppk_layout.addWidget(QLabel("NIP:"))
        ppk_layout.addWidget(self.txt_ppk_nip)
        pejabat_form.addRow("PPK:", ppk_layout)

        # Bendahara
        self.cmb_bendahara = QComboBox()
        self.cmb_bendahara.setEditable(True)
        self._load_bendahara_combo()
        self.cmb_bendahara.currentIndexChanged.connect(self._on_bendahara_selected)
        pejabat_form.addRow("Pilih Bendahara:", self.cmb_bendahara)

        bend_layout = QHBoxLayout()
        self.txt_bendahara_nama = QLineEdit()
        self.txt_bendahara_nama.setText(pejabat_default.get('bendahara_nama', ''))
        bend_layout.addWidget(self.txt_bendahara_nama)
        self.txt_bendahara_nip = QLineEdit()
        self.txt_bendahara_nip.setText(pejabat_default.get('bendahara_nip', ''))
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

    def _load_kpa_combo(self):
        """Load KPA pegawai into combo box"""
        self.cmb_kpa.clear()
        self.cmb_kpa.addItem("-- Pilih KPA --", None)
        try:
            pegawai_list = self.db.get_pegawai_by_role('kpa')
            for p in pegawai_list:
                nama = self._format_nama(p)
                self.cmb_kpa.addItem(nama, p)
        except Exception as e:
            print(f"Error loading KPA: {e}")

    def _load_ppk_combo(self):
        """Load PPK pegawai into combo box"""
        self.cmb_ppk.clear()
        self.cmb_ppk.addItem("-- Pilih PPK --", None)
        try:
            pegawai_list = self.db.get_pegawai_by_role('ppk')
            for p in pegawai_list:
                nama = self._format_nama(p)
                self.cmb_ppk.addItem(nama, p)
        except Exception as e:
            print(f"Error loading PPK: {e}")

    def _load_bendahara_combo(self):
        """Load Bendahara pegawai into combo box"""
        self.cmb_bendahara.clear()
        self.cmb_bendahara.addItem("-- Pilih Bendahara --", None)
        try:
            pegawai_list = self.db.get_pegawai_by_role('bendahara')
            for p in pegawai_list:
                nama = self._format_nama(p)
                self.cmb_bendahara.addItem(nama, p)
        except Exception as e:
            print(f"Error loading Bendahara: {e}")

    def _format_nama(self, p: dict) -> str:
        """Format nama pegawai dengan gelar"""
        nama = p.get('nama', '')
        if p.get('gelar_depan'):
            nama = f"{p['gelar_depan']} {nama}"
        if p.get('gelar_belakang'):
            nama = f"{nama}, {p['gelar_belakang']}"
        return nama

    def _on_kpa_selected(self, index):
        data = self.cmb_kpa.currentData()
        if data and isinstance(data, dict):
            self.txt_kpa_nama.setText(self._format_nama(data))
            self.txt_kpa_nip.setText(data.get('nip', '') or '')

    def _on_ppk_selected(self, index):
        data = self.cmb_ppk.currentData()
        if data and isinstance(data, dict):
            self.txt_ppk_nama.setText(self._format_nama(data))
            self.txt_ppk_nip.setText(data.get('nip', '') or '')

    def _on_bendahara_selected(self, index):
        data = self.cmb_bendahara.currentData()
        if data and isinstance(data, dict):
            self.txt_bendahara_nama.setText(self._format_nama(data))
            self.txt_bendahara_nip.setText(data.get('nip', '') or '')

    def _set_combo_by_id(self, combo: QComboBox, pegawai_id: int):
        """Helper to set ComboBox selection by pegawai ID"""
        if not pegawai_id:
            return
        for i in range(combo.count()):
            data = combo.itemData(i)
            if data and isinstance(data, dict) and data.get('id') == pegawai_id:
                combo.setCurrentIndex(i)
                return

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

        # Set ComboBox first if _id exists, then text fields
        if d.get('kpa_id'):
            self._set_combo_by_id(self.cmb_kpa, d['kpa_id'])
        self.txt_kpa_nama.setText(d.get('kpa_nama', ''))
        self.txt_kpa_nip.setText(d.get('kpa_nip', ''))

        if d.get('ppk_id'):
            self._set_combo_by_id(self.cmb_ppk, d['ppk_id'])
        self.txt_ppk_nama.setText(d.get('ppk_nama', ''))
        self.txt_ppk_nip.setText(d.get('ppk_nip', ''))

        if d.get('bendahara_id'):
            self._set_combo_by_id(self.cmb_bendahara, d['bendahara_id'])
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

        # Get pegawai data from ComboBox selections
        kpa_data = self.cmb_kpa.currentData()
        ppk_data = self.cmb_ppk.currentData()
        bendahara_data = self.cmb_bendahara.currentData()

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
            # Pejabat dengan foreign key _id
            'kpa_id': kpa_data.get('id') if kpa_data and isinstance(kpa_data, dict) else None,
            'kpa_nama': self.txt_kpa_nama.text(),
            'kpa_nip': self.txt_kpa_nip.text(),
            'ppk_id': ppk_data.get('id') if ppk_data and isinstance(ppk_data, dict) else None,
            'ppk_nama': self.txt_ppk_nama.text(),
            'ppk_nip': self.txt_ppk_nip.text(),
            'bendahara_id': bendahara_data.get('id') if bendahara_data and isinstance(bendahara_data, dict) else None,
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

        # Get pejabat from satker settings
        pejabat = self.db.get_satker_pejabat()

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
            'kpa_nama': pejabat.get('kpa_nama', ''),
            'kpa_nip': pejabat.get('kpa_nip', ''),
            'ppk_nama': pejabat.get('ppk_nama', ''),
            'ppk_nip': pejabat.get('ppk_nip', ''),
            'bendahara_nama': pejabat.get('bendahara_nama', ''),
            'bendahara_nip': pejabat.get('bendahara_nip', ''),
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
# HONORARIUM PENGELOLA KEUANGAN DIALOG
# ============================================================================

class HonorariumPengelolaDialog(QDialog):
    """Dialog for Honorarium Pengelola Keuangan"""

    JABATAN_PENGELOLA = [
        ('KPA', 'Kuasa Pengguna Anggaran'),
        ('PPK', 'Pejabat Pembuat Komitmen'),
        ('PPSPM', 'Pejabat Penandatangan SPM'),
        ('Bendahara', 'Bendahara Pengeluaran'),
        ('Bendahara_PNBP', 'Bendahara Pengelola PNBP'),
        ('Operator', 'Operator Keuangan'),
        ('Staf', 'Staf Pengelola Keuangan')
    ]

    BULAN_NAMES = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    def __init__(self, hpk_data: dict = None, parent=None):
        super().__init__(parent)
        self.hpk_data = hpk_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Tambah Honor Pengelola Keuangan" if not hpk_data else "Edit Honor Pengelola Keuangan")
        self.setMinimumWidth(600)
        self.setup_ui()
        self.load_pegawai()

        if hpk_data:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        # Tahun & Bulan
        periode_layout = QHBoxLayout()
        self.spn_tahun = QSpinBox()
        self.spn_tahun.setRange(2020, 2050)
        self.spn_tahun.setValue(TAHUN_ANGGARAN)
        periode_layout.addWidget(self.spn_tahun)
        periode_layout.addWidget(QLabel("Bulan:"))
        self.cmb_bulan = QComboBox()
        for i, b in enumerate(self.BULAN_NAMES):
            self.cmb_bulan.addItem(b, i + 1)
        self.cmb_bulan.setCurrentIndex(datetime.now().month - 1)
        periode_layout.addWidget(self.cmb_bulan)
        form.addRow("Tahun:", periode_layout)

        # Jabatan
        self.cmb_jabatan = QComboBox()
        for code, name in self.JABATAN_PENGELOLA:
            self.cmb_jabatan.addItem(f"{code} - {name}", code)
        self.cmb_jabatan.currentIndexChanged.connect(self.on_jabatan_changed)
        form.addRow("Jabatan:", self.cmb_jabatan)

        # Pegawai
        self.cmb_pegawai = QComboBox()
        self.cmb_pegawai.addItem("-- Pilih Pegawai --", None)
        form.addRow("Pegawai:", self.cmb_pegawai)

        # Jumlah
        self.spn_jumlah = CurrencySpinBox()
        form.addRow("Jumlah Bruto:", self.spn_jumlah)

        # Pajak
        self.spn_pajak = CurrencySpinBox()
        self.spn_pajak.valueChanged.connect(self.calc_netto)
        form.addRow("Pajak (PPh 21):", self.spn_pajak)

        # Netto
        self.lbl_netto = QLabel("Rp 0")
        self.lbl_netto.setStyleSheet("font-weight: bold; font-size: 14px; color: #27ae60;")
        form.addRow("Jumlah Netto:", self.lbl_netto)

        # Keterangan
        self.txt_keterangan = QLineEdit()
        self.txt_keterangan.setPlaceholderText("Keterangan tambahan...")
        form.addRow("Keterangan:", self.txt_keterangan)

        layout.addLayout(form)

        # Auto-fill from satker pejabat
        info = QLabel("Tip: Pilihan pegawai akan otomatis mengisi dari Data Satker jika sudah diatur.")
        info.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(info)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_save = QPushButton("Simpan")
        btn_save.setStyleSheet("background: #27ae60; color: white; padding: 10px 30px;")
        btn_save.clicked.connect(self.save_data)
        btn_layout.addWidget(btn_save)
        btn_cancel = QPushButton("Batal")
        btn_cancel.setStyleSheet("background: #95a5a6; color: white; padding: 10px 30px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        # Calculate netto on jumlah change
        self.spn_jumlah.valueChanged.connect(self.calc_netto)

    def load_pegawai(self):
        """Load pegawai list"""
        pegawai = self.db.get_all_pegawai(active_only=True)
        for p in pegawai:
            display = f"{p['nama']} - {p.get('nip', 'N/A')}"
            self.cmb_pegawai.addItem(display, p['id'])

    def on_jabatan_changed(self):
        """Auto-fill pegawai from satker settings"""
        jabatan = self.cmb_jabatan.currentData()
        satker = self.db.get_satker_pejabat()

        pegawai_id = None
        if jabatan == 'KPA':
            pegawai_id = satker.get('kpa_id')
        elif jabatan == 'PPK':
            pegawai_id = satker.get('ppk_id')
        elif jabatan == 'PPSPM':
            pegawai_id = satker.get('ppspm_id')
        elif jabatan == 'Bendahara':
            pegawai_id = satker.get('bendahara_id')

        if pegawai_id:
            for i in range(self.cmb_pegawai.count()):
                if self.cmb_pegawai.itemData(i) == pegawai_id:
                    self.cmb_pegawai.setCurrentIndex(i)
                    break

    def calc_netto(self):
        """Calculate netto amount"""
        bruto = self.spn_jumlah.value()
        pajak = self.spn_pajak.value()
        netto = bruto - pajak
        self.lbl_netto.setText(f"Rp {netto:,.0f}".replace(",", "."))

    def load_data(self):
        """Load existing data"""
        if not self.hpk_data:
            return
        self.spn_tahun.setValue(self.hpk_data.get('tahun', TAHUN_ANGGARAN))
        bulan = self.hpk_data.get('bulan', 1)
        self.cmb_bulan.setCurrentIndex(bulan - 1)

        jabatan = self.hpk_data.get('jabatan', '')
        for i in range(self.cmb_jabatan.count()):
            if self.cmb_jabatan.itemData(i) == jabatan:
                self.cmb_jabatan.setCurrentIndex(i)
                break

        pegawai_id = self.hpk_data.get('pegawai_id')
        if pegawai_id:
            for i in range(self.cmb_pegawai.count()):
                if self.cmb_pegawai.itemData(i) == pegawai_id:
                    self.cmb_pegawai.setCurrentIndex(i)
                    break

        self.spn_jumlah.setValue(self.hpk_data.get('jumlah', 0))
        self.spn_pajak.setValue(self.hpk_data.get('pajak', 0))
        self.txt_keterangan.setText(self.hpk_data.get('keterangan', '') or '')
        self.calc_netto()

    def save_data(self):
        """Validate and save data"""
        pegawai_id = self.cmb_pegawai.currentData()
        if not pegawai_id:
            QMessageBox.warning(self, "Validasi", "Pilih pegawai terlebih dahulu!")
            return

        jumlah = self.spn_jumlah.value()
        if jumlah <= 0:
            QMessageBox.warning(self, "Validasi", "Jumlah harus lebih dari 0!")
            return

        data = {
            'tahun': self.spn_tahun.value(),
            'bulan': self.cmb_bulan.currentData(),
            'jabatan': self.cmb_jabatan.currentData(),
            'pegawai_id': pegawai_id,
            'jumlah': jumlah,
            'pajak': self.spn_pajak.value(),
            'netto': jumlah - self.spn_pajak.value(),
            'keterangan': self.txt_keterangan.text().strip() or None
        }

        try:
            if self.hpk_data:
                self.db.update_honorarium_pengelola(self.hpk_data['id'], data)
            else:
                self.db.create_honorarium_pengelola(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data:\n{str(e)}")


# ============================================================================
# IMPORT FA DIALOG
# ============================================================================

class ImportFADialog(QDialog):
    """Dialog to select pagu from FA Detail for import"""

    def __init__(self, pagu_list: List[Dict], parent=None):
        super().__init__(parent)
        self.pagu_list = pagu_list
        self.db = get_db_manager_v4()

        self.setWindowTitle("Import dari FA Detail")
        self.setMinimumWidth(700)
        self.setMinimumHeight(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        header = QLabel("Pilih item pagu anggaran untuk honorarium pengelola keuangan:")
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Pilih", "Kode Akun", "Uraian", "Pagu", "Sisa"
        ])
        self.table.setRowCount(len(self.pagu_list))
        self.table.horizontalHeader().setStretchLastSection(True)

        self.checkboxes = []
        for row, pagu in enumerate(self.pagu_list):
            # Checkbox
            chk = QCheckBox()
            self.checkboxes.append(chk)
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, chk_widget)

            self.table.setItem(row, 1, QTableWidgetItem(pagu.get('kode_akun', '')))
            self.table.setItem(row, 2, QTableWidgetItem(pagu.get('uraian', '')))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rp {pagu.get('jumlah', 0):,.0f}".replace(",", ".")))
            self.table.setItem(row, 4, QTableWidgetItem(f"Rp {pagu.get('sisa', 0):,.0f}".replace(",", ".")))

        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 150)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_import = QPushButton("Import Terpilih")
        btn_import.setStyleSheet("background: #27ae60; color: white; padding: 10px 30px;")
        btn_import.clicked.connect(self.do_import)
        btn_layout.addWidget(btn_import)
        btn_cancel = QPushButton("Batal")
        btn_cancel.setStyleSheet("background: #95a5a6; color: white; padding: 10px 30px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def do_import(self):
        """Import selected pagu items"""
        selected = []
        for i, chk in enumerate(self.checkboxes):
            if chk.isChecked():
                selected.append(self.pagu_list[i])

        if not selected:
            QMessageBox.warning(self, "Info", "Pilih minimal satu item untuk diimpor!")
            return

        QMessageBox.information(self, "Info", f"{len(selected)} item telah ditandai.\n"
                                               "Silakan buat honorarium dengan jumlah sesuai pagu yang dipilih.")
        self.accept()


# ============================================================================
# GENERATE JAMUAN TAMU DOCUMENT DIALOG
# ============================================================================

class GenerateJTDocumentDialog(QDialog):
    """Dialog for generating Jamuan Tamu documents"""

    def __init__(self, jt_data: dict, parent=None):
        super().__init__(parent)
        self.jt_data = jt_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Generate Dokumen Jamuan Tamu")
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Info
        info_group = QGroupBox("Informasi Jamuan Tamu")
        info_form = QFormLayout()
        info_form.addRow("Kegiatan:", QLabel(self.jt_data.get('nama_kegiatan', '-')))
        info_form.addRow("Tanggal:", QLabel(str(self.jt_data.get('tanggal_kegiatan', '-'))))
        info_form.addRow("Tamu:", QLabel(self.jt_data.get('nama_tamu', '-')))
        info_group.setLayout(info_form)
        layout.addWidget(info_group)

        # Document checkboxes - sesuai Kepmen KP 56/2025
        doc_group = QGroupBox("Pilih Dokumen (Kepmen KP 56/2025)")
        doc_layout = QVBoxLayout()

        # Info label
        info_label = QLabel("Checklist kelengkapan dokumen Jamuan Tamu:")
        info_label.setStyleSheet("font-style: italic; color: #7f8c8d;")
        doc_layout.addWidget(info_label)

        self.chk_kuitansi = QCheckBox("💰 Kuitansi Jamuan Tamu")
        self.chk_kuitansi.setChecked(True)
        doc_layout.addWidget(self.chk_kuitansi)

        self.chk_daftar_hadir = QCheckBox("📋 Daftar Hadir")
        self.chk_daftar_hadir.setChecked(True)
        doc_layout.addWidget(self.chk_daftar_hadir)

        self.chk_laporan = QCheckBox("📊 Laporan Kegiatan Jamuan Tamu")
        self.chk_laporan.setChecked(True)
        doc_layout.addWidget(self.chk_laporan)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #bdc3c7;")
        doc_layout.addWidget(line)

        # Catatan dokumen pendukung
        note_label = QLabel("Dokumen pendukung (disiapkan manual):")
        note_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        doc_layout.addWidget(note_label)

        note_items = QLabel("• Faktur/Nota/Bon dari restoran/katering\n"
                           "• Foto tagging menu makanan\n"
                           "• Foto tagging jumlah peserta")
        note_items.setStyleSheet("color: #7f8c8d; margin-left: 10px;")
        doc_layout.addWidget(note_items)

        doc_group.setLayout(doc_layout)
        layout.addWidget(doc_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_generate = QPushButton("🖨️ Generate Dokumen")
        btn_generate.setStyleSheet("background-color: #27ae60; color: white; padding: 10px 20px;")
        btn_generate.clicked.connect(self.generate)
        btn_layout.addWidget(btn_generate)

        btn_cancel = QPushButton("Batal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    def generate(self):
        """Generate selected documents"""
        import os
        import traceback
        from app.core.config import WORD_TEMPLATES_DIR, OUTPUT_DIR, TAHUN_ANGGARAN

        generated = []
        errors = []

        try:
            from app.templates.engine import get_template_engine
            engine = get_template_engine()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal load template engine:\n{str(e)}\n\n{traceback.format_exc()}")
            return

        # Prepare placeholders
        try:
            placeholders = self._prepare_placeholders()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyiapkan data:\n{str(e)}\n\n{traceback.format_exc()}")
            return

        # Output folder
        try:
            output_folder = os.path.join(
                OUTPUT_DIR,
                str(TAHUN_ANGGARAN),
                "Jamuan_Tamu",
                f"JT_{self.jt_data['id']}_{self.jt_data.get('nama_kegiatan', 'unknown')[:20]}"
            )
            os.makedirs(output_folder, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membuat folder output:\n{str(e)}")
            return

        # Generate each selected document - sesuai Kepmen KP 56/2025
        docs_to_generate = []
        if self.chk_kuitansi.isChecked():
            docs_to_generate.append(('kuitansi_jamuan_tamu', 'Kuitansi_Jamuan_Tamu', 'word'))
        if self.chk_daftar_hadir.isChecked():
            docs_to_generate.append(('daftar_hadir_jamuan_tamu', 'Daftar_Hadir', 'word'))
        if self.chk_laporan.isChecked():
            docs_to_generate.append(('laporan_jamuan_tamu', 'Laporan_Kegiatan', 'word'))

        if not docs_to_generate:
            QMessageBox.warning(self, "Peringatan", "Pilih minimal satu dokumen untuk di-generate!")
            return

        for template_name, output_name, doc_type in docs_to_generate:
            try:
                template_path = os.path.join(WORD_TEMPLATES_DIR, f"{template_name}.docx")
                output_path = os.path.join(output_folder, f"{output_name}.docx")

                # Check if template exists
                if not os.path.exists(template_path):
                    errors.append(f"{output_name}: Template tidak ditemukan di {template_path}")
                    continue

                engine.merge_word(
                    template_path=template_path,
                    data=placeholders,
                    output_path=output_path
                )
                generated.append(output_name)
            except Exception as e:
                errors.append(f"{output_name}: {str(e)}\n{traceback.format_exc()}")

        # Show result
        if generated:
            msg = f"Berhasil generate {len(generated)} dokumen:\n"
            msg += "\n".join([f"✅ {d}" for d in generated])
            if errors:
                msg += f"\n\n⚠️ Error:\n" + "\n".join(errors)
            msg += f"\n\n📁 Output: {output_folder}"

            QMessageBox.information(self, "Generate Selesai", msg)

            # Open folder
            import sys
            if sys.platform == 'win32':
                os.startfile(output_folder)
            elif sys.platform == 'darwin':
                os.system(f'open "{output_folder}"')
            else:
                os.system(f'xdg-open "{output_folder}"')

            self.accept()
        else:
            error_msg = "Tidak ada dokumen yang berhasil di-generate."
            if errors:
                error_msg += "\n\n" + "\n".join(errors)
            QMessageBox.warning(self, "Error", error_msg)

    def _prepare_placeholders(self) -> dict:
        """Prepare placeholders from jamuan tamu data"""
        from app.core.config import TAHUN_ANGGARAN
        from app.templates.engine import terbilang

        d = self.jt_data

        # Format currency
        def fmt_rp(value):
            return f"Rp {value:,.0f}".replace(',', '.')

        # Get satker data from database
        satker = self.db.get_satker()
        pejabat = self.db.get_satker_pejabat()

        return {
            # Satker
            'satker_kode': satker.get('kode', ''),
            'satker_nama': satker.get('nama', ''),
            'satker_alamat': satker.get('alamat', ''),
            'satker_kota': satker.get('kota', ''),
            'satker_provinsi': satker.get('provinsi', ''),
            'kementerian': satker.get('kementerian', ''),
            'eselon1': satker.get('eselon1', ''),
            'tahun_anggaran': str(TAHUN_ANGGARAN),

            # Kegiatan
            'nama_kegiatan': d.get('nama_kegiatan', ''),
            'tanggal_kegiatan': str(d.get('tanggal_kegiatan', '')),
            'tempat_kegiatan': d.get('tempat', ''),
            'waktu_mulai': d.get('waktu_mulai', '08:00'),
            'kategori': d.get('kategori', ''),

            # Tamu
            'nama_tamu': d.get('nama_tamu', ''),
            'instansi_tamu': d.get('instansi_tamu', ''),
            'jabatan_tamu': d.get('jabatan_tamu', ''),
            'jumlah_tamu': str(d.get('jumlah_tamu', 1)),

            # Dokumen
            'nomor_sk_kpa': d.get('nomor_sk_kpa', ''),
            'tanggal_sk_kpa': str(d.get('tanggal_sk_kpa', '')),
            'nomor_nd': d.get('nomor_nd', ''),
            'tanggal_nd': str(d.get('tanggal_nd', '')),
            'nomor_kuitansi': d.get('nomor_kuitansi', ''),
            'tanggal_kuitansi': str(d.get('tanggal_kuitansi', '')),

            # Sumber Dana
            'sumber_dana': d.get('sumber_dana', 'DIPA'),
            'kode_akun': d.get('kode_akun', ''),
            'mak': d.get('mak', ''),

            # Biaya
            'biaya_konsumsi': fmt_rp(d.get('biaya_konsumsi', 0) or 0),
            'biaya_akomodasi': fmt_rp(d.get('biaya_akomodasi', 0) or 0),
            'biaya_transportasi': fmt_rp(d.get('biaya_transportasi', 0) or 0),
            'biaya_lainnya': fmt_rp(d.get('biaya_lainnya', 0) or 0),
            'total_biaya': fmt_rp(d.get('total_biaya', 0) or 0),
            'total_biaya_terbilang': terbilang(d.get('total_biaya', 0) or 0),

            # Pejabat
            'kpa_nama': pejabat.get('kpa_nama', ''),
            'kpa_nip': pejabat.get('kpa_nip', ''),
            'ppk_nama': d.get('ppk_nama', '') or pejabat.get('ppk_nama', ''),
            'ppk_nip': d.get('ppk_nip', '') or pejabat.get('ppk_nip', ''),
            'ppk_jabatan': 'Pejabat Pembuat Komitmen',
            'bendahara_nama': d.get('bendahara_nama', '') or pejabat.get('bendahara_nama', ''),
            'bendahara_nip': d.get('bendahara_nip', '') or pejabat.get('bendahara_nip', ''),

            # Penanggung Jawab (bisa diisi dari data atau default)
            'pj_nama': d.get('pj_nama', '') or pejabat.get('ppk_nama', ''),
            'pj_nip': d.get('pj_nip', '') or pejabat.get('ppk_nip', ''),

            'keterangan': d.get('keterangan', ''),
        }


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

        # ========== TAB 4: HONORARIUM PENGELOLA KEUANGAN ==========
        tab_hpk = QWidget()
        hpk_layout = QVBoxLayout(tab_hpk)

        # Info
        info_label = QLabel("Honorarium Pengelola Keuangan diambil dari FA Detail (Pagu Anggaran)")
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        hpk_layout.addWidget(info_label)

        # Toolbar
        hpk_toolbar = QHBoxLayout()
        btn_add_hpk = QPushButton("+ Tambah Pembayaran")
        btn_add_hpk.setStyleSheet("background-color: #9b59b6; color: white; padding: 8px 16px;")
        btn_add_hpk.clicked.connect(self.add_honorarium_pengelola)
        hpk_toolbar.addWidget(btn_add_hpk)

        btn_from_fa = QPushButton("Import dari FA Detail")
        btn_from_fa.setStyleSheet("background-color: #1abc9c; color: white; padding: 8px 16px;")
        btn_from_fa.clicked.connect(self.import_from_fa_detail)
        hpk_toolbar.addWidget(btn_from_fa)
        hpk_toolbar.addStretch()

        hpk_toolbar.addWidget(QLabel("Tahun:"))
        self.cmb_hpk_tahun = QComboBox()
        for y in range(TAHUN_ANGGARAN - 2, TAHUN_ANGGARAN + 3):
            self.cmb_hpk_tahun.addItem(str(y), y)
        self.cmb_hpk_tahun.setCurrentText(str(TAHUN_ANGGARAN))
        self.cmb_hpk_tahun.currentIndexChanged.connect(self.refresh_honorarium_pengelola)
        hpk_toolbar.addWidget(self.cmb_hpk_tahun)

        hpk_layout.addLayout(hpk_toolbar)

        # Table
        self.tbl_hpk = QTableWidget()
        self.tbl_hpk.setColumnCount(9)
        self.tbl_hpk.setHorizontalHeaderLabels([
            "ID", "Bulan", "Jabatan", "Pegawai", "NIP", "Jumlah", "Pajak", "Netto", "Aksi"
        ])
        self.tbl_hpk.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_hpk.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_hpk.horizontalHeader().setStretchLastSection(True)
        self.tbl_hpk.setColumnWidth(0, 50)
        self.tbl_hpk.setColumnWidth(1, 100)
        self.tbl_hpk.setColumnWidth(2, 120)
        self.tbl_hpk.setColumnWidth(3, 200)
        self.tbl_hpk.setColumnWidth(4, 150)
        self.tbl_hpk.setColumnWidth(5, 120)
        self.tbl_hpk.setColumnWidth(6, 100)
        self.tbl_hpk.setColumnWidth(7, 120)
        hpk_layout.addWidget(self.tbl_hpk)

        # FA Detail reference
        fa_group = QGroupBox("Referensi Pagu Anggaran (FA Detail)")
        fa_layout = QVBoxLayout()
        self.tbl_fa_ref = QTableWidget()
        self.tbl_fa_ref.setColumnCount(5)
        self.tbl_fa_ref.setHorizontalHeaderLabels([
            "Kode Akun", "Uraian", "Pagu", "Realisasi", "Sisa"
        ])
        self.tbl_fa_ref.setMaximumHeight(150)
        self.tbl_fa_ref.horizontalHeader().setStretchLastSection(True)
        fa_layout.addWidget(self.tbl_fa_ref)
        fa_group.setLayout(fa_layout)
        hpk_layout.addWidget(fa_group)

        self.tabs.addTab(tab_hpk, "Honor Pengelola Keuangan")

        layout.addWidget(self.tabs)

    def format_currency(self, value):
        return f"Rp {value:,.0f}".replace(",", ".")

    def refresh_all(self):
        self.refresh_sk_kpa()
        self.refresh_honorarium()
        self.refresh_jamuan_tamu()
        self.refresh_honorarium_pengelola()
        self.refresh_fa_reference()

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

            btn_gen = QPushButton("Cetak")
            btn_gen.setStyleSheet("background: #27ae60; color: white; padding: 2px 8px;")
            btn_gen.clicked.connect(lambda checked, r=row: self.generate_jamuan_tamu(r))
            btn_layout.addWidget(btn_gen)

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

    def generate_jamuan_tamu(self, row):
        """Generate documents for selected Jamuan Tamu"""
        jt_id = int(self.tbl_jt.item(row, 0).text())
        jt_data = self.db.get_jamuan_tamu(jt_id)
        if jt_data:
            dialog = GenerateJTDocumentDialog(jt_data, parent=self)
            dialog.exec()

    # =========================================================================
    # HONORARIUM PENGELOLA KEUANGAN
    # =========================================================================

    JABATAN_PENGELOLA = [
        ('KPA', 'Kuasa Pengguna Anggaran'),
        ('PPK', 'Pejabat Pembuat Komitmen'),
        ('PPSPM', 'Pejabat Penandatangan SPM'),
        ('Bendahara', 'Bendahara Pengeluaran'),
        ('Bendahara_PNBP', 'Bendahara Pengelola PNBP'),
        ('Operator', 'Operator Keuangan'),
        ('Staf', 'Staf Pengelola Keuangan')
    ]

    BULAN_NAMES = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    def refresh_honorarium_pengelola(self):
        """Refresh honorarium pengelola keuangan table"""
        tahun = self.cmb_hpk_tahun.currentData()
        if not tahun:
            tahun = TAHUN_ANGGARAN
        data = self.db.get_all_honorarium_pengelola(tahun=tahun)
        self.tbl_hpk.setRowCount(len(data))

        for row, d in enumerate(data):
            self.tbl_hpk.setItem(row, 0, QTableWidgetItem(str(d['id'])))
            # Get bulan name
            bulan_idx = d.get('bulan', 1) - 1
            bulan_name = self.BULAN_NAMES[bulan_idx] if 0 <= bulan_idx < 12 else str(d.get('bulan'))
            self.tbl_hpk.setItem(row, 1, QTableWidgetItem(bulan_name))
            self.tbl_hpk.setItem(row, 2, QTableWidgetItem(d.get('jabatan', '')))
            self.tbl_hpk.setItem(row, 3, QTableWidgetItem(d.get('pegawai_nama', '')))
            self.tbl_hpk.setItem(row, 4, QTableWidgetItem(d.get('pegawai_nip', '')))
            self.tbl_hpk.setItem(row, 5, QTableWidgetItem(self.format_currency(d.get('jumlah', 0))))
            self.tbl_hpk.setItem(row, 6, QTableWidgetItem(self.format_currency(d.get('pajak', 0))))
            self.tbl_hpk.setItem(row, 7, QTableWidgetItem(self.format_currency(d.get('netto', 0))))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background: #3498db; color: white; padding: 2px 8px;")
            btn_edit.clicked.connect(lambda checked, r=row: self.edit_honorarium_pengelola(r))
            btn_layout.addWidget(btn_edit)

            btn_del = QPushButton("Hapus")
            btn_del.setStyleSheet("background: #e74c3c; color: white; padding: 2px 8px;")
            btn_del.clicked.connect(lambda checked, r=row: self.delete_honorarium_pengelola(r))
            btn_layout.addWidget(btn_del)

            self.tbl_hpk.setCellWidget(row, 8, btn_widget)

    def refresh_fa_reference(self):
        """Refresh FA Detail reference table for pengelola keuangan"""
        tahun = self.cmb_hpk_tahun.currentData()
        if not tahun:
            tahun = TAHUN_ANGGARAN
        # Get pagu with akun 52xxxx (Belanja Barang - Honor Pengelola Keuangan)
        data = self.db.get_pagu_for_honorarium_pengelola(tahun=tahun)
        self.tbl_fa_ref.setRowCount(len(data))

        for row, d in enumerate(data):
            self.tbl_fa_ref.setItem(row, 0, QTableWidgetItem(d.get('kode_akun', '')))
            self.tbl_fa_ref.setItem(row, 1, QTableWidgetItem(d.get('uraian', '')))
            self.tbl_fa_ref.setItem(row, 2, QTableWidgetItem(self.format_currency(d.get('jumlah', 0))))
            self.tbl_fa_ref.setItem(row, 3, QTableWidgetItem(self.format_currency(d.get('realisasi', 0))))
            self.tbl_fa_ref.setItem(row, 4, QTableWidgetItem(self.format_currency(d.get('sisa', 0))))

    def add_honorarium_pengelola(self):
        """Add honorarium pengelola keuangan"""
        dialog = HonorariumPengelolaDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_honorarium_pengelola()
            self.refresh_fa_reference()
            QMessageBox.information(self, "Sukses", "Honorarium berhasil ditambahkan!")

    def edit_honorarium_pengelola(self, row):
        hpk_id = int(self.tbl_hpk.item(row, 0).text())
        hpk_data = self.db.get_honorarium_pengelola(hpk_id)
        if hpk_data:
            dialog = HonorariumPengelolaDialog(hpk_data, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.refresh_honorarium_pengelola()
                self.refresh_fa_reference()

    def delete_honorarium_pengelola(self, row):
        hpk_id = int(self.tbl_hpk.item(row, 0).text())
        reply = QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus Honorarium ini?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_honorarium_pengelola(hpk_id):
                self.refresh_honorarium_pengelola()
                self.refresh_fa_reference()

    def import_from_fa_detail(self):
        """Import honorarium amounts from FA Detail"""
        tahun = self.cmb_hpk_tahun.currentData()
        if not tahun:
            tahun = TAHUN_ANGGARAN

        # Get pagu for honorarium pengelola
        pagu_list = self.db.get_pagu_for_honorarium_pengelola(tahun=tahun)

        if not pagu_list:
            QMessageBox.warning(self, "Info", "Tidak ada data pagu untuk honorarium pengelola keuangan.\n"
                                               "Pastikan sudah mengisi FA Detail dengan akun 52xxxx.")
            return

        # Show dialog to select which pagu to use
        dialog = ImportFADialog(pagu_list, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_fa_reference()
            QMessageBox.information(self, "Sukses", "Data berhasil diimpor dari FA Detail!")
