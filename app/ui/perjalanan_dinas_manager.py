"""
PPK DOCUMENT FACTORY - Perjalanan Dinas Manager
================================================
Manager untuk data Perjalanan Dinas dengan:
- Input data perjalanan dinas lengkap
- Generate dokumen: Surat Tugas, SPPD, Kuitansi UM, Kuitansi Rampung
- List dan edit perjalanan dinas
"""

import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QMessageBox, QCheckBox, QFrame, QSplitter, QTabWidget,
    QAbstractItemView, QMenu, QFileDialog, QDateEdit, QSpinBox,
    QDoubleSpinBox, QScrollArea
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
# PERJALANAN DINAS DIALOG (Add/Edit)
# ============================================================================

class PerjalananDinasDialog(QDialog):
    """Dialog for adding/editing perjalanan dinas"""

    def __init__(self, pd_data: dict = None, parent=None):
        super().__init__(parent)
        self.pd_data = pd_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Tambah Perjalanan Dinas" if not pd_data else "Edit Perjalanan Dinas")
        self.setMinimumWidth(800)
        self.setMinimumHeight(700)
        self.setup_ui()

        if pd_data:
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

        # ========== TAB 1: DATA DINAS ==========
        tab_dinas = QWidget()
        form1 = QVBoxLayout(tab_dinas)

        # Info Dasar
        info_group = QGroupBox("Informasi Dasar")
        info_form = QFormLayout()

        self.txt_nama_kegiatan = QLineEdit()
        self.txt_nama_kegiatan.setPlaceholderText("Monitoring dan Evaluasi...")
        info_form.addRow("Nama Kegiatan:", self.txt_nama_kegiatan)

        self.txt_maksud = QTextEdit()
        self.txt_maksud.setPlaceholderText("Maksud dan tujuan perjalanan dinas...")
        self.txt_maksud.setMaximumHeight(80)
        info_form.addRow("Maksud Perjalanan:", self.txt_maksud)

        # Nomor Surat
        nomor_layout = QHBoxLayout()
        self.txt_nomor_surat_tugas = QLineEdit()
        self.txt_nomor_surat_tugas.setPlaceholderText("ST-001/POLTEK/2024")
        nomor_layout.addWidget(QLabel("No. Surat Tugas:"))
        nomor_layout.addWidget(self.txt_nomor_surat_tugas)
        self.txt_nomor_sppd = QLineEdit()
        self.txt_nomor_sppd.setPlaceholderText("SPPD-001/POLTEK/2024")
        nomor_layout.addWidget(QLabel("No. SPPD:"))
        nomor_layout.addWidget(self.txt_nomor_sppd)
        info_form.addRow("Nomor Dokumen:", nomor_layout)

        info_group.setLayout(info_form)
        form1.addWidget(info_group)

        # Pelaksana
        pelaksana_group = QGroupBox("Data Pelaksana")
        pelaksana_form = QFormLayout()

        self.cmb_pelaksana = QComboBox()
        self.cmb_pelaksana.setEditable(True)
        self.load_pegawai_combo()
        self.cmb_pelaksana.currentIndexChanged.connect(self.on_pelaksana_selected)
        pelaksana_form.addRow("Pilih Pegawai:", self.cmb_pelaksana)

        self.txt_pelaksana_nama = QLineEdit()
        pelaksana_form.addRow("Nama Pelaksana:", self.txt_pelaksana_nama)

        self.txt_pelaksana_nip = QLineEdit()
        pelaksana_form.addRow("NIP:", self.txt_pelaksana_nip)

        pg_layout = QHBoxLayout()
        self.txt_pelaksana_pangkat = QLineEdit()
        pg_layout.addWidget(self.txt_pelaksana_pangkat)
        self.txt_pelaksana_golongan = QComboBox()
        self.txt_pelaksana_golongan.setEditable(True)
        self.txt_pelaksana_golongan.addItems([
            '', 'I/a', 'I/b', 'I/c', 'I/d',
            'II/a', 'II/b', 'II/c', 'II/d',
            'III/a', 'III/b', 'III/c', 'III/d',
            'IV/a', 'IV/b', 'IV/c', 'IV/d', 'IV/e'
        ])
        self.txt_pelaksana_golongan.setMaximumWidth(80)
        pg_layout.addWidget(self.txt_pelaksana_golongan)
        pelaksana_form.addRow("Pangkat/Gol:", pg_layout)

        self.txt_pelaksana_jabatan = QLineEdit()
        pelaksana_form.addRow("Jabatan:", self.txt_pelaksana_jabatan)

        pelaksana_group.setLayout(pelaksana_form)
        form1.addWidget(pelaksana_group)

        # Tujuan
        tujuan_group = QGroupBox("Tujuan Perjalanan")
        tujuan_form = QFormLayout()

        self.txt_kota_asal = QLineEdit()
        # Ambil kota dari master data satker
        satker = self.db.get_satker()
        self.txt_kota_asal.setText(satker.get('kota', ''))
        tujuan_form.addRow("Kota Asal:", self.txt_kota_asal)

        self.txt_kota_tujuan = QLineEdit()
        self.txt_kota_tujuan.setPlaceholderText("Kota tujuan perjalanan")
        tujuan_form.addRow("Kota Tujuan:", self.txt_kota_tujuan)

        self.txt_provinsi_tujuan = QLineEdit()
        self.txt_provinsi_tujuan.setPlaceholderText("Provinsi tujuan")
        tujuan_form.addRow("Provinsi:", self.txt_provinsi_tujuan)

        self.txt_alamat_tujuan = QLineEdit()
        self.txt_alamat_tujuan.setPlaceholderText("Alamat lengkap tujuan (opsional)")
        tujuan_form.addRow("Alamat Tujuan:", self.txt_alamat_tujuan)

        tujuan_group.setLayout(tujuan_form)
        form1.addWidget(tujuan_group)

        tabs.addTab(tab_dinas, "Data Perjalanan")

        # ========== TAB 2: WAKTU & ANGGARAN ==========
        tab_waktu = QWidget()
        form2 = QVBoxLayout(tab_waktu)

        # Waktu
        waktu_group = QGroupBox("Waktu Perjalanan")
        waktu_form = QFormLayout()

        self.date_surat_tugas = QDateEdit()
        self.date_surat_tugas.setCalendarPopup(True)
        self.date_surat_tugas.setDate(QDate.currentDate())
        waktu_form.addRow("Tanggal Surat Tugas:", self.date_surat_tugas)

        self.date_berangkat = QDateEdit()
        self.date_berangkat.setCalendarPopup(True)
        self.date_berangkat.setDate(QDate.currentDate())
        self.date_berangkat.dateChanged.connect(self.update_lama_perjalanan)
        waktu_form.addRow("Tanggal Berangkat:", self.date_berangkat)

        self.date_kembali = QDateEdit()
        self.date_kembali.setCalendarPopup(True)
        self.date_kembali.setDate(QDate.currentDate().addDays(3))
        self.date_kembali.dateChanged.connect(self.update_lama_perjalanan)
        waktu_form.addRow("Tanggal Kembali:", self.date_kembali)

        self.spn_lama = QSpinBox()
        self.spn_lama.setRange(1, 30)
        self.spn_lama.setValue(3)
        self.spn_lama.setSuffix(" hari")
        self.spn_lama.setReadOnly(True)
        waktu_form.addRow("Lama Perjalanan:", self.spn_lama)

        waktu_group.setLayout(waktu_form)
        form2.addWidget(waktu_group)

        # Anggaran
        anggaran_group = QGroupBox("Anggaran DIPA")
        anggaran_form = QFormLayout()

        self.txt_sumber_dana = QLineEdit()
        self.txt_sumber_dana.setText("DIPA")
        anggaran_form.addRow("Sumber Dana:", self.txt_sumber_dana)

        self.txt_kode_akun = QLineEdit()
        self.txt_kode_akun.setPlaceholderText("524111")
        anggaran_form.addRow("Kode Akun/MAK:", self.txt_kode_akun)

        anggaran_group.setLayout(anggaran_form)
        form2.addWidget(anggaran_group)

        # Biaya
        biaya_group = QGroupBox("Rincian Biaya")
        biaya_form = QFormLayout()

        self.spn_biaya_transport = CurrencySpinBox()
        self.spn_biaya_transport.valueChanged.connect(self.update_total_biaya)
        biaya_form.addRow("Biaya Transport:", self.spn_biaya_transport)

        self.spn_biaya_uang_harian = CurrencySpinBox()
        self.spn_biaya_uang_harian.valueChanged.connect(self.update_total_biaya)
        biaya_form.addRow("Uang Harian:", self.spn_biaya_uang_harian)

        self.spn_biaya_penginapan = CurrencySpinBox()
        self.spn_biaya_penginapan.valueChanged.connect(self.update_total_biaya)
        biaya_form.addRow("Biaya Penginapan:", self.spn_biaya_penginapan)

        self.spn_biaya_representasi = CurrencySpinBox()
        self.spn_biaya_representasi.valueChanged.connect(self.update_total_biaya)
        biaya_form.addRow("Uang Representasi:", self.spn_biaya_representasi)

        self.spn_biaya_lain = CurrencySpinBox()
        self.spn_biaya_lain.valueChanged.connect(self.update_total_biaya)
        biaya_form.addRow("Biaya Lain-lain:", self.spn_biaya_lain)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        biaya_form.addRow(sep)

        self.lbl_total_biaya = QLabel("Rp 0")
        self.lbl_total_biaya.setStyleSheet("font-weight: bold; font-size: 14px;")
        biaya_form.addRow("TOTAL BIAYA:", self.lbl_total_biaya)

        self.spn_uang_muka = CurrencySpinBox()
        biaya_form.addRow("Uang Muka Diterima:", self.spn_uang_muka)

        biaya_group.setLayout(biaya_form)
        form2.addWidget(biaya_group)

        tabs.addTab(tab_waktu, "Waktu & Biaya")

        # ========== TAB 3: PEJABAT ==========
        tab_pejabat = QWidget()
        form3 = QVBoxLayout(tab_pejabat)

        # PPK
        ppk_group = QGroupBox("Pejabat Pembuat Komitmen (PPK)")
        ppk_form = QFormLayout()

        self.cmb_ppk = QComboBox()
        self.cmb_ppk.setEditable(True)
        self.load_ppk_combo()
        self.cmb_ppk.currentIndexChanged.connect(self.on_ppk_selected)
        ppk_form.addRow("Pilih PPK:", self.cmb_ppk)

        self.txt_ppk_nama = QLineEdit()
        ppk_form.addRow("Nama PPK:", self.txt_ppk_nama)

        self.txt_ppk_nip = QLineEdit()
        ppk_form.addRow("NIP PPK:", self.txt_ppk_nip)

        self.txt_ppk_jabatan = QLineEdit()
        self.txt_ppk_jabatan.setText("Pejabat Pembuat Komitmen")
        ppk_form.addRow("Jabatan:", self.txt_ppk_jabatan)

        ppk_group.setLayout(ppk_form)
        form3.addWidget(ppk_group)

        # Bendahara
        bendahara_group = QGroupBox("Bendahara Pengeluaran")
        bendahara_form = QFormLayout()

        self.cmb_bendahara = QComboBox()
        self.cmb_bendahara.setEditable(True)
        self.load_bendahara_combo()
        self.cmb_bendahara.currentIndexChanged.connect(self.on_bendahara_selected)
        bendahara_form.addRow("Pilih Bendahara:", self.cmb_bendahara)

        self.txt_bendahara_nama = QLineEdit()
        bendahara_form.addRow("Nama:", self.txt_bendahara_nama)

        self.txt_bendahara_nip = QLineEdit()
        bendahara_form.addRow("NIP:", self.txt_bendahara_nip)

        bendahara_group.setLayout(bendahara_form)
        form3.addWidget(bendahara_group)

        form3.addStretch()
        tabs.addTab(tab_pejabat, "Pejabat")

        scroll_layout.addWidget(tabs)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_save = QPushButton("💾 Simpan")
        btn_save.setObjectName("btnSuccess")
        btn_save.clicked.connect(self.save)
        btn_layout.addWidget(btn_save)

        btn_cancel = QPushButton("Batal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

        # Style
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton#btnSuccess {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#btnSuccess:hover {
                background-color: #219a52;
            }
        """)

    def load_pegawai_combo(self):
        """Load pegawai into combo box"""
        self.cmb_pelaksana.clear()
        self.cmb_pelaksana.addItem("-- Pilih Pegawai --", None)

        try:
            pegawai_list = self.db.get_all_pegawai(active_only=True)
            for p in pegawai_list:
                nama = p.get('nama', '')
                if p.get('gelar_depan'):
                    nama = f"{p['gelar_depan']} {nama}"
                if p.get('gelar_belakang'):
                    nama = f"{nama}, {p['gelar_belakang']}"
                self.cmb_pelaksana.addItem(nama, p)
        except Exception as e:
            print(f"Error loading pegawai: {e}")

    def load_ppk_combo(self):
        """Load PPK into combo box"""
        self.cmb_ppk.clear()
        self.cmb_ppk.addItem("-- Pilih PPK --", None)

        try:
            pegawai_list = self.db.get_pegawai_by_role('ppk')
            for p in pegawai_list:
                nama = p.get('nama', '')
                if p.get('gelar_depan'):
                    nama = f"{p['gelar_depan']} {nama}"
                if p.get('gelar_belakang'):
                    nama = f"{nama}, {p['gelar_belakang']}"
                self.cmb_ppk.addItem(nama, p)
        except Exception as e:
            print(f"Error loading PPK: {e}")

    def load_bendahara_combo(self):
        """Load Bendahara into combo box"""
        self.cmb_bendahara.clear()
        self.cmb_bendahara.addItem("-- Pilih Bendahara --", None)

        try:
            pegawai_list = self.db.get_pegawai_by_role('bendahara')
            for p in pegawai_list:
                nama = p.get('nama', '')
                if p.get('gelar_depan'):
                    nama = f"{p['gelar_depan']} {nama}"
                if p.get('gelar_belakang'):
                    nama = f"{nama}, {p['gelar_belakang']}"
                self.cmb_bendahara.addItem(nama, p)
        except Exception as e:
            print(f"Error loading bendahara: {e}")

    def on_pelaksana_selected(self, index):
        """Fill form when pelaksana selected"""
        data = self.cmb_pelaksana.currentData()
        if data and isinstance(data, dict):
            nama = data.get('nama', '')
            if data.get('gelar_depan'):
                nama = f"{data['gelar_depan']} {nama}"
            if data.get('gelar_belakang'):
                nama = f"{nama}, {data['gelar_belakang']}"
            self.txt_pelaksana_nama.setText(nama)
            self.txt_pelaksana_nip.setText(data.get('nip', '') or '')
            self.txt_pelaksana_pangkat.setText(data.get('pangkat', '') or '')
            self.txt_pelaksana_golongan.setCurrentText(data.get('golongan', '') or '')
            self.txt_pelaksana_jabatan.setText(data.get('jabatan', '') or '')

    def on_ppk_selected(self, index):
        """Fill PPK data"""
        data = self.cmb_ppk.currentData()
        if data and isinstance(data, dict):
            nama = data.get('nama', '')
            if data.get('gelar_depan'):
                nama = f"{data['gelar_depan']} {nama}"
            if data.get('gelar_belakang'):
                nama = f"{nama}, {data['gelar_belakang']}"
            self.txt_ppk_nama.setText(nama)
            self.txt_ppk_nip.setText(data.get('nip', '') or '')

    def on_bendahara_selected(self, index):
        """Fill Bendahara data"""
        data = self.cmb_bendahara.currentData()
        if data and isinstance(data, dict):
            nama = data.get('nama', '')
            if data.get('gelar_depan'):
                nama = f"{data['gelar_depan']} {nama}"
            if data.get('gelar_belakang'):
                nama = f"{nama}, {data['gelar_belakang']}"
            self.txt_bendahara_nama.setText(nama)
            self.txt_bendahara_nip.setText(data.get('nip', '') or '')

    def update_lama_perjalanan(self):
        """Calculate travel duration"""
        berangkat = self.date_berangkat.date().toPython()
        kembali = self.date_kembali.date().toPython()
        lama = (kembali - berangkat).days + 1
        self.spn_lama.setValue(max(1, lama))

    def update_total_biaya(self):
        """Calculate total cost"""
        total = (
            self.spn_biaya_transport.value() +
            self.spn_biaya_uang_harian.value() +
            self.spn_biaya_penginapan.value() +
            self.spn_biaya_representasi.value() +
            self.spn_biaya_lain.value()
        )
        self.lbl_total_biaya.setText(f"Rp {total:,.0f}".replace(',', '.'))

    def load_data(self):
        """Load existing data"""
        if not self.pd_data:
            return

        d = self.pd_data

        self.txt_nama_kegiatan.setText(d.get('nama_kegiatan', '') or '')
        self.txt_maksud.setText(d.get('maksud_perjalanan', '') or '')
        self.txt_nomor_surat_tugas.setText(d.get('nomor_surat_tugas', '') or '')
        self.txt_nomor_sppd.setText(d.get('nomor_sppd', '') or '')

        # Set pelaksana combo berdasarkan pelaksana_id jika ada
        if d.get('pelaksana_id'):
            self._set_combo_by_id(self.cmb_pelaksana, d['pelaksana_id'])
        self.txt_pelaksana_nama.setText(d.get('pelaksana_nama', '') or '')
        self.txt_pelaksana_nip.setText(d.get('pelaksana_nip', '') or '')
        self.txt_pelaksana_pangkat.setText(d.get('pelaksana_pangkat', '') or '')
        self.txt_pelaksana_golongan.setCurrentText(d.get('pelaksana_golongan', '') or '')
        self.txt_pelaksana_jabatan.setText(d.get('pelaksana_jabatan', '') or '')

        self.txt_kota_asal.setText(d.get('kota_asal', '') or '')
        self.txt_kota_tujuan.setText(d.get('kota_tujuan', '') or '')
        self.txt_provinsi_tujuan.setText(d.get('provinsi_tujuan', '') or '')
        self.txt_alamat_tujuan.setText(d.get('alamat_tujuan', '') or '')

        if d.get('tanggal_surat_tugas'):
            self.date_surat_tugas.setDate(QDate.fromString(str(d['tanggal_surat_tugas']), 'yyyy-MM-dd'))
        if d.get('tanggal_berangkat'):
            self.date_berangkat.setDate(QDate.fromString(str(d['tanggal_berangkat']), 'yyyy-MM-dd'))
        if d.get('tanggal_kembali'):
            self.date_kembali.setDate(QDate.fromString(str(d['tanggal_kembali']), 'yyyy-MM-dd'))

        self.txt_sumber_dana.setText(d.get('sumber_dana', 'DIPA') or 'DIPA')
        self.txt_kode_akun.setText(d.get('kode_akun', '') or '')

        self.spn_biaya_transport.setValue(d.get('biaya_transport', 0) or 0)
        self.spn_biaya_uang_harian.setValue(d.get('biaya_uang_harian', 0) or 0)
        self.spn_biaya_penginapan.setValue(d.get('biaya_penginapan', 0) or 0)
        self.spn_biaya_representasi.setValue(d.get('biaya_representasi', 0) or 0)
        self.spn_biaya_lain.setValue(d.get('biaya_lain_lain', 0) or 0)
        self.spn_uang_muka.setValue(d.get('uang_muka', 0) or 0)

        # Set PPK combo berdasarkan ppk_id jika ada
        if d.get('ppk_id'):
            self._set_combo_by_id(self.cmb_ppk, d['ppk_id'])
        self.txt_ppk_nama.setText(d.get('ppk_nama', '') or '')
        self.txt_ppk_nip.setText(d.get('ppk_nip', '') or '')

        # Set Bendahara combo berdasarkan bendahara_id jika ada
        if d.get('bendahara_id'):
            self._set_combo_by_id(self.cmb_bendahara, d['bendahara_id'])
        self.txt_bendahara_nama.setText(d.get('bendahara_nama', '') or '')
        self.txt_bendahara_nip.setText(d.get('bendahara_nip', '') or '')

        self.update_total_biaya()

    def _set_combo_by_id(self, combo: QComboBox, pegawai_id: int):
        """Set combo selection by pegawai ID"""
        for i in range(combo.count()):
            data = combo.itemData(i)
            if data and isinstance(data, dict) and data.get('id') == pegawai_id:
                combo.setCurrentIndex(i)
                return

    def get_data(self) -> dict:
        """Get form data"""
        # Get pegawai IDs from ComboBox selections
        pelaksana_data = self.cmb_pelaksana.currentData()
        ppk_data = self.cmb_ppk.currentData()
        bendahara_data = self.cmb_bendahara.currentData()

        return {
            'nama_kegiatan': self.txt_nama_kegiatan.text().strip(),
            'maksud_perjalanan': self.txt_maksud.toPlainText().strip(),
            'nomor_surat_tugas': self.txt_nomor_surat_tugas.text().strip(),
            'nomor_sppd': self.txt_nomor_sppd.text().strip(),

            # Pelaksana - simpan ID dan data text
            'pelaksana_id': pelaksana_data.get('id') if pelaksana_data else None,
            'pelaksana_nama': self.txt_pelaksana_nama.text().strip(),
            'pelaksana_nip': self.txt_pelaksana_nip.text().strip(),
            'pelaksana_pangkat': self.txt_pelaksana_pangkat.text().strip(),
            'pelaksana_golongan': self.txt_pelaksana_golongan.currentText().strip(),
            'pelaksana_jabatan': self.txt_pelaksana_jabatan.text().strip(),

            'kota_asal': self.txt_kota_asal.text().strip(),
            'kota_tujuan': self.txt_kota_tujuan.text().strip(),
            'provinsi_tujuan': self.txt_provinsi_tujuan.text().strip(),
            'alamat_tujuan': self.txt_alamat_tujuan.text().strip(),

            'tanggal_surat_tugas': self.date_surat_tugas.date().toPython(),
            'tanggal_berangkat': self.date_berangkat.date().toPython(),
            'tanggal_kembali': self.date_kembali.date().toPython(),
            'lama_perjalanan': self.spn_lama.value(),

            'sumber_dana': self.txt_sumber_dana.text().strip(),
            'kode_akun': self.txt_kode_akun.text().strip(),

            'biaya_transport': self.spn_biaya_transport.value(),
            'biaya_uang_harian': self.spn_biaya_uang_harian.value(),
            'biaya_penginapan': self.spn_biaya_penginapan.value(),
            'biaya_representasi': self.spn_biaya_representasi.value(),
            'biaya_lain_lain': self.spn_biaya_lain.value(),
            'uang_muka': self.spn_uang_muka.value(),

            # Pejabat - simpan ID dan data text
            'ppk_id': ppk_data.get('id') if ppk_data else None,
            'ppk_nama': self.txt_ppk_nama.text().strip(),
            'ppk_nip': self.txt_ppk_nip.text().strip(),
            'ppk_jabatan': self.txt_ppk_jabatan.text().strip(),
            'bendahara_id': bendahara_data.get('id') if bendahara_data else None,
            'bendahara_nama': self.txt_bendahara_nama.text().strip(),
            'bendahara_nip': self.txt_bendahara_nip.text().strip(),

            'tahun_anggaran': TAHUN_ANGGARAN,
            'status': 'draft'
        }

    def save(self):
        """Save data"""
        data = self.get_data()

        # Validation
        if not data['nama_kegiatan']:
            QMessageBox.warning(self, "Validasi", "Nama kegiatan wajib diisi!")
            return

        if not data['pelaksana_nama']:
            QMessageBox.warning(self, "Validasi", "Nama pelaksana wajib diisi!")
            return

        if not data['kota_tujuan']:
            QMessageBox.warning(self, "Validasi", "Kota tujuan wajib diisi!")
            return

        try:
            if self.pd_data:
                self.db.update_perjalanan_dinas(self.pd_data['id'], data)
            else:
                self.db.create_perjalanan_dinas(data)

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan:\n{str(e)}")


# ============================================================================
# PERJALANAN DINAS MANAGER (Main Window)
# ============================================================================

class PerjalananDinasManager(QDialog):
    """Main dialog for managing perjalanan dinas"""

    data_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db_manager_v4()

        self.setWindowTitle("✈️ Perjalanan Dinas")
        self.setMinimumSize(1100, 700)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()

        title = QLabel("✈️ Daftar Perjalanan Dinas")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(title)

        header.addStretch()

        # Filter tahun
        header.addWidget(QLabel("Tahun:"))
        self.cmb_tahun = QComboBox()
        for year in range(TAHUN_ANGGARAN - 2, TAHUN_ANGGARAN + 2):
            self.cmb_tahun.addItem(str(year), year)
        self.cmb_tahun.setCurrentText(str(TAHUN_ANGGARAN))
        self.cmb_tahun.currentIndexChanged.connect(self.load_data)
        header.addWidget(self.cmb_tahun)

        # Search
        header.addWidget(QLabel("🔍"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Cari nama/tujuan...")
        self.txt_search.setMinimumWidth(200)
        self.txt_search.textChanged.connect(self.filter_data)
        header.addWidget(self.txt_search)

        layout.addLayout(header)

        # Toolbar
        toolbar = QHBoxLayout()

        btn_add = QPushButton("➕ Tambah Perjalanan Dinas")
        btn_add.setStyleSheet("background-color: #3498db; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_add.clicked.connect(self.add_perjalanan_dinas)
        toolbar.addWidget(btn_add)

        btn_edit = QPushButton("✏️ Edit")
        btn_edit.clicked.connect(self.edit_perjalanan_dinas)
        toolbar.addWidget(btn_edit)

        btn_delete = QPushButton("🗑️ Hapus")
        btn_delete.setStyleSheet("background-color: #e74c3c; color: white;")
        btn_delete.clicked.connect(self.delete_perjalanan_dinas)
        toolbar.addWidget(btn_delete)

        toolbar.addStretch()

        # Generate documents
        btn_generate = QPushButton("📄 Generate Dokumen")
        btn_generate.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_generate.clicked.connect(self.generate_documents)
        toolbar.addWidget(btn_generate)

        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "No", "Nama Kegiatan", "Pelaksana", "Tujuan",
            "Tgl Berangkat", "Tgl Kembali", "Total Biaya",
            "Status", "Dokumen", "ID"
        ])

        self.table.setColumnHidden(9, True)  # Hide ID

        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 120)
        self.table.setColumnWidth(7, 80)
        self.table.setColumnWidth(8, 100)

        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.edit_perjalanan_dinas)

        layout.addWidget(self.table)

        # Summary
        summary = QHBoxLayout()
        self.lbl_total = QLabel("Total: 0 perjalanan dinas")
        self.lbl_total.setStyleSheet("font-weight: bold;")
        summary.addWidget(self.lbl_total)

        summary.addStretch()

        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.accept)
        summary.addWidget(btn_close)

        layout.addLayout(summary)

    def load_data(self):
        """Load perjalanan dinas data"""
        tahun = self.cmb_tahun.currentData()
        self.all_data = self.db.get_all_perjalanan_dinas(tahun=tahun)
        self.filter_data()

    def filter_data(self):
        """Filter displayed data"""
        search = self.txt_search.text().lower()

        filtered = []
        for pd in self.all_data:
            if search:
                searchable = f"{pd.get('nama_kegiatan', '')} {pd.get('pelaksana_nama', '')} {pd.get('kota_tujuan', '')}".lower()
                if search not in searchable:
                    continue
            filtered.append(pd)

        self.display_data(filtered)

    def display_data(self, data_list: List[Dict]):
        """Display data in table"""
        self.table.setRowCount(len(data_list))

        for row, pd in enumerate(data_list):
            # No
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))

            # Nama Kegiatan
            self.table.setItem(row, 1, QTableWidgetItem(pd.get('nama_kegiatan', '') or '-'))

            # Pelaksana
            self.table.setItem(row, 2, QTableWidgetItem(pd.get('pelaksana_nama', '') or '-'))

            # Tujuan
            tujuan = pd.get('kota_tujuan', '')
            if pd.get('provinsi_tujuan'):
                tujuan = f"{tujuan}, {pd['provinsi_tujuan']}"
            self.table.setItem(row, 3, QTableWidgetItem(tujuan))

            # Tanggal
            self.table.setItem(row, 4, QTableWidgetItem(str(pd.get('tanggal_berangkat', '') or '-')))
            self.table.setItem(row, 5, QTableWidgetItem(str(pd.get('tanggal_kembali', '') or '-')))

            # Total Biaya
            total = (
                (pd.get('biaya_transport', 0) or 0) +
                (pd.get('biaya_uang_harian', 0) or 0) +
                (pd.get('biaya_penginapan', 0) or 0) +
                (pd.get('biaya_representasi', 0) or 0) +
                (pd.get('biaya_lain_lain', 0) or 0)
            )
            self.table.setItem(row, 6, QTableWidgetItem(f"Rp {total:,.0f}".replace(',', '.')))

            # Status
            status = pd.get('status', 'draft')
            status_item = QTableWidgetItem(status.title())
            if status == 'completed':
                status_item.setForeground(QColor('#27ae60'))
            elif status == 'in_progress':
                status_item.setForeground(QColor('#f39c12'))
            self.table.setItem(row, 7, status_item)

            # Dokumen
            doc_count = pd.get('doc_count', 0)
            self.table.setItem(row, 8, QTableWidgetItem(f"{doc_count} dok"))

            # ID (hidden)
            self.table.setItem(row, 9, QTableWidgetItem(str(pd['id'])))

        self.lbl_total.setText(f"Total: {len(data_list)} perjalanan dinas")

    def get_selected_id(self) -> Optional[int]:
        """Get selected ID"""
        row = self.table.currentRow()
        if row < 0:
            return None
        id_item = self.table.item(row, 9)
        return int(id_item.text()) if id_item else None

    def add_perjalanan_dinas(self):
        """Add new perjalanan dinas"""
        dialog = PerjalananDinasDialog(parent=self)
        if dialog.exec():
            self.load_data()
            self.data_changed.emit()

    def edit_perjalanan_dinas(self):
        """Edit selected perjalanan dinas"""
        pd_id = self.get_selected_id()
        if not pd_id:
            QMessageBox.warning(self, "Peringatan", "Pilih perjalanan dinas terlebih dahulu!")
            return

        pd_data = self.db.get_perjalanan_dinas(pd_id)
        if not pd_data:
            return

        dialog = PerjalananDinasDialog(pd_data, parent=self)
        if dialog.exec():
            self.load_data()
            self.data_changed.emit()

    def delete_perjalanan_dinas(self):
        """Delete selected perjalanan dinas"""
        pd_id = self.get_selected_id()
        if not pd_id:
            QMessageBox.warning(self, "Peringatan", "Pilih perjalanan dinas terlebih dahulu!")
            return

        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            "Hapus perjalanan dinas ini?\n\n"
            "Data dan dokumen terkait akan dihapus.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.delete_perjalanan_dinas(pd_id)
                self.load_data()
                self.data_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus:\n{str(e)}")

    def generate_documents(self):
        """Generate documents for selected perjalanan dinas"""
        pd_id = self.get_selected_id()
        if not pd_id:
            QMessageBox.warning(self, "Peringatan", "Pilih perjalanan dinas terlebih dahulu!")
            return

        pd_data = self.db.get_perjalanan_dinas(pd_id)
        if not pd_data:
            return

        # Show document selection dialog
        dialog = GeneratePDDocumentDialog(pd_data, parent=self)
        if dialog.exec():
            self.load_data()


# ============================================================================
# GENERATE DOCUMENT DIALOG
# ============================================================================

class GeneratePDDocumentDialog(QDialog):
    """Dialog for generating perjalanan dinas documents"""

    def __init__(self, pd_data: dict, parent=None):
        super().__init__(parent)
        self.pd_data = pd_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Generate Dokumen Perjalanan Dinas")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Info
        info_group = QGroupBox("Perjalanan Dinas")
        info_form = QFormLayout()
        info_form.addRow("Kegiatan:", QLabel(self.pd_data.get('nama_kegiatan', '-')))
        info_form.addRow("Pelaksana:", QLabel(self.pd_data.get('pelaksana_nama', '-')))
        info_form.addRow("Tujuan:", QLabel(self.pd_data.get('kota_tujuan', '-')))
        info_group.setLayout(info_form)
        layout.addWidget(info_group)

        # Document checkboxes
        doc_group = QGroupBox("Pilih Dokumen yang akan di-generate")
        doc_layout = QVBoxLayout()

        self.chk_surat_tugas = QCheckBox("📄 Surat Tugas")
        self.chk_surat_tugas.setChecked(True)
        doc_layout.addWidget(self.chk_surat_tugas)

        self.chk_sppd = QCheckBox("📄 SPPD (Surat Perintah Perjalanan Dinas)")
        self.chk_sppd.setChecked(True)
        doc_layout.addWidget(self.chk_sppd)

        self.chk_kuitansi_um = QCheckBox("💰 Kuitansi Uang Muka")
        self.chk_kuitansi_um.setChecked(True)
        doc_layout.addWidget(self.chk_kuitansi_um)

        self.chk_rincian = QCheckBox("📊 Rincian Biaya Perjalanan Dinas")
        doc_layout.addWidget(self.chk_rincian)

        self.chk_kuitansi_rampung = QCheckBox("💰 Kuitansi Rampung")
        doc_layout.addWidget(self.chk_kuitansi_rampung)

        self.chk_daftar_riil = QCheckBox("📋 Daftar Pengeluaran Riil")
        doc_layout.addWidget(self.chk_daftar_riil)

        self.chk_laporan = QCheckBox("📝 Laporan Perjalanan Dinas")
        doc_layout.addWidget(self.chk_laporan)

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
        import traceback
        from app.core.config import WORD_TEMPLATES_DIR

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
                "Perjalanan_Dinas",
                f"PD_{self.pd_data['id']}_{self.pd_data.get('pelaksana_nama', 'unknown')[:20]}"
            )
            os.makedirs(output_folder, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membuat folder output:\n{str(e)}")
            return

        # Generate each selected document
        docs_to_generate = []
        if self.chk_surat_tugas.isChecked():
            docs_to_generate.append(('surat_tugas', 'Surat_Tugas'))
        if self.chk_sppd.isChecked():
            docs_to_generate.append(('sppd', 'SPPD'))
        if self.chk_kuitansi_um.isChecked():
            docs_to_generate.append(('kuitansi_uang_muka', 'Kuitansi_Uang_Muka'))
        if self.chk_rincian.isChecked():
            docs_to_generate.append(('rincian_biaya_pd', 'Rincian_Biaya'))
        if self.chk_kuitansi_rampung.isChecked():
            docs_to_generate.append(('kuitansi_rampung', 'Kuitansi_Rampung'))
        if self.chk_daftar_riil.isChecked():
            docs_to_generate.append(('daftar_pengeluaran_riil', 'Daftar_Pengeluaran_Riil'))
        if self.chk_laporan.isChecked():
            docs_to_generate.append(('laporan_perjalanan_dinas', 'Laporan_Perjalanan_Dinas'))

        if not docs_to_generate:
            QMessageBox.warning(self, "Peringatan", "Pilih minimal satu dokumen untuk di-generate!")
            return

        for template_name, output_name in docs_to_generate:
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
        """Prepare placeholders from perjalanan dinas data"""
        d = self.pd_data

        # Calculate total
        total_biaya = (
            (d.get('biaya_transport', 0) or 0) +
            (d.get('biaya_uang_harian', 0) or 0) +
            (d.get('biaya_penginapan', 0) or 0) +
            (d.get('biaya_representasi', 0) or 0) +
            (d.get('biaya_lain_lain', 0) or 0)
        )

        uang_muka = d.get('uang_muka', 0) or 0
        selisih = total_biaya - uang_muka

        # Format currency
        def fmt_rp(value):
            return f"Rp {value:,.0f}".replace(',', '.')

        # Terbilang
        def terbilang_rupiah(n):
            from app.templates.engine import terbilang
            return terbilang(n)

        # Get satker data from database
        satker = self.db.get_satker()
        pejabat = self.db.get_satker_pejabat()

        return {
            # DIPA - dari master data satker
            'satker_kode': satker.get('kode', ''),
            'satker_nama': satker.get('nama', ''),
            'satker_alamat': satker.get('alamat', ''),
            'satker_kota': satker.get('kota', ''),
            'satker_provinsi': satker.get('provinsi', ''),
            'kementerian': satker.get('kementerian', ''),
            'eselon1': satker.get('eselon1', ''),
            'tahun_anggaran': str(TAHUN_ANGGARAN),
            'sumber_dana': d.get('sumber_dana', 'DIPA'),
            'kode_akun': d.get('kode_akun', ''),

            # Kegiatan
            'nama_paket': d.get('nama_kegiatan', ''),
            'maksud_perjalanan': d.get('maksud_perjalanan', ''),

            # Pelaksana
            'pelaksana_nama': d.get('pelaksana_nama', ''),
            'pelaksana_nip': d.get('pelaksana_nip', ''),
            'pelaksana_pangkat': d.get('pelaksana_pangkat', ''),
            'pelaksana_golongan': d.get('pelaksana_golongan', ''),
            'pelaksana_jabatan': d.get('pelaksana_jabatan', ''),

            # Tujuan
            'kota_asal': d.get('kota_asal', ''),
            'kota_tujuan': d.get('kota_tujuan', ''),
            'provinsi_tujuan': d.get('provinsi_tujuan', ''),
            'alamat_tujuan': d.get('alamat_tujuan', ''),

            # Waktu
            'tanggal_surat_tugas': str(d.get('tanggal_surat_tugas', '')),
            'tanggal_berangkat': str(d.get('tanggal_berangkat', '')),
            'tanggal_kembali': str(d.get('tanggal_kembali', '')),
            'lama_perjalanan': str(d.get('lama_perjalanan', 1)),

            # Nomor dokumen
            'nomor_surat_tugas': d.get('nomor_surat_tugas', ''),
            'nomor_sppd': d.get('nomor_sppd', ''),

            # Biaya
            'biaya_transport': fmt_rp(d.get('biaya_transport', 0) or 0),
            'biaya_uang_harian': fmt_rp(d.get('biaya_uang_harian', 0) or 0),
            'biaya_penginapan': fmt_rp(d.get('biaya_penginapan', 0) or 0),
            'biaya_representasi': fmt_rp(d.get('biaya_representasi', 0) or 0),
            'biaya_lain_lain': fmt_rp(d.get('biaya_lain_lain', 0) or 0),
            'total_biaya': fmt_rp(total_biaya),
            'uang_muka': fmt_rp(uang_muka),
            'uang_muka_terbilang': terbilang_rupiah(uang_muka),
            'kekurangan_bayar': fmt_rp(max(0, selisih)),
            'kelebihan_bayar': fmt_rp(max(0, -selisih)),
            'sisa_terbilang': terbilang_rupiah(abs(selisih)),

            # Pejabat - dari master data satker
            'kpa_nama': pejabat.get('kpa_nama', ''),
            'kpa_nip': pejabat.get('kpa_nip', ''),
            'ppk_nama': d.get('ppk_nama', '') or pejabat.get('ppk_nama', ''),
            'ppk_nip': d.get('ppk_nip', '') or pejabat.get('ppk_nip', ''),
            'ppk_jabatan': d.get('ppk_jabatan', '') or 'Pejabat Pembuat Komitmen',
            'bendahara_nama': d.get('bendahara_nama', '') or pejabat.get('bendahara_nama', ''),
            'bendahara_nip': d.get('bendahara_nip', '') or pejabat.get('bendahara_nip', ''),
        }


# ============================================================================
# HELPER FUNCTION
# ============================================================================

def show_perjalanan_dinas_manager(parent=None) -> PerjalananDinasManager:
    """Show perjalanan dinas manager dialog"""
    dialog = PerjalananDinasManager(parent)
    dialog.exec()
    return dialog
