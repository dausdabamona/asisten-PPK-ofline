"""
PPK DOCUMENT FACTORY - Swakelola Manager
=========================================
Manager untuk kegiatan Swakelola dengan:
- Input data kegiatan swakelola lengkap
- Tim pelaksana swakelola
- Uang Muka dan Kuitansi Rampung
- Generate dokumen: KAK, RAB, SK Tim, BAP, Laporan Kemajuan, BAST
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
# SWAKELOLA DIALOG (Add/Edit)
# ============================================================================

class SwakelolaDialog(QDialog):
    """Dialog for adding/editing swakelola activity"""

    def __init__(self, sw_data: dict = None, parent=None):
        super().__init__(parent)
        self.sw_data = sw_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Tambah Kegiatan Swakelola" if not sw_data else "Edit Kegiatan Swakelola")
        self.setMinimumWidth(900)
        self.setMinimumHeight(750)
        self.setup_ui()

        if sw_data:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Tab widget
        tabs = QTabWidget()

        # ========== TAB 1: DATA KEGIATAN ==========
        tab_kegiatan = QWidget()
        form1 = QVBoxLayout(tab_kegiatan)

        # Info Dasar
        info_group = QGroupBox("Informasi Kegiatan")
        info_form = QFormLayout()

        self.txt_nama_kegiatan = QLineEdit()
        self.txt_nama_kegiatan.setPlaceholderText("Nama kegiatan swakelola...")
        info_form.addRow("Nama Kegiatan:", self.txt_nama_kegiatan)

        self.cmb_tipe_swakelola = QComboBox()
        self.cmb_tipe_swakelola.addItems([
            'Tipe I (Swakelola oleh K/L/D/I)',
            'Tipe II (Swakelola oleh Instansi Pemerintah Lain)',
            'Tipe III (Swakelola oleh Organisasi Kemasyarakatan)',
            'Tipe IV (Swakelola oleh Kelompok Masyarakat)'
        ])
        info_form.addRow("Tipe Swakelola:", self.cmb_tipe_swakelola)

        self.txt_deskripsi = QTextEdit()
        self.txt_deskripsi.setPlaceholderText("Deskripsi kegiatan swakelola...")
        self.txt_deskripsi.setMaximumHeight(80)
        info_form.addRow("Deskripsi:", self.txt_deskripsi)

        self.txt_output = QLineEdit()
        self.txt_output.setPlaceholderText("Output yang dihasilkan...")
        info_form.addRow("Output Kegiatan:", self.txt_output)

        info_group.setLayout(info_form)
        form1.addWidget(info_group)

        # Nomor Dokumen
        nomor_group = QGroupBox("Nomor Dokumen")
        nomor_form = QFormLayout()

        self.txt_nomor_kak = QLineEdit()
        self.txt_nomor_kak.setPlaceholderText("KAK-001/POLTEK/2024")
        nomor_form.addRow("No. KAK:", self.txt_nomor_kak)

        self.txt_nomor_sk_tim = QLineEdit()
        self.txt_nomor_sk_tim.setPlaceholderText("SK-001/POLTEK/2024")
        nomor_form.addRow("No. SK Tim:", self.txt_nomor_sk_tim)

        nomor_group.setLayout(nomor_form)
        form1.addWidget(nomor_group)

        # SK KPA Group
        sk_kpa_group = QGroupBox("SK KPA (Surat Keputusan Kuasa Pengguna Anggaran)")
        sk_kpa_group.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #e74c3c; }")
        sk_kpa_form = QFormLayout()

        sk_nomor_layout = QHBoxLayout()
        self.txt_nomor_sk_kpa = QLineEdit()
        self.txt_nomor_sk_kpa.setPlaceholderText("SK-KPA/001/2024")
        sk_nomor_layout.addWidget(self.txt_nomor_sk_kpa)
        sk_nomor_layout.addWidget(QLabel("Tanggal:"))
        self.date_sk_kpa = QDateEdit()
        self.date_sk_kpa.setCalendarPopup(True)
        self.date_sk_kpa.setDate(QDate.currentDate())
        sk_nomor_layout.addWidget(self.date_sk_kpa)
        sk_kpa_form.addRow("No. SK KPA:", sk_nomor_layout)

        self.txt_perihal_sk_kpa = QLineEdit()
        self.txt_perihal_sk_kpa.setPlaceholderText("Pembayaran Kegiatan Swakelola...")
        sk_kpa_form.addRow("Perihal:", self.txt_perihal_sk_kpa)

        sk_kpa_group.setLayout(sk_kpa_form)
        form1.addWidget(sk_kpa_group)

        # Waktu
        waktu_group = QGroupBox("Waktu Pelaksanaan")
        waktu_form = QFormLayout()

        self.date_sk_tim = QDateEdit()
        self.date_sk_tim.setCalendarPopup(True)
        self.date_sk_tim.setDate(QDate.currentDate())
        waktu_form.addRow("Tanggal SK Tim:", self.date_sk_tim)

        self.date_mulai = QDateEdit()
        self.date_mulai.setCalendarPopup(True)
        self.date_mulai.setDate(QDate.currentDate())
        waktu_form.addRow("Tanggal Mulai:", self.date_mulai)

        self.date_selesai = QDateEdit()
        self.date_selesai.setCalendarPopup(True)
        self.date_selesai.setDate(QDate.currentDate().addDays(30))
        waktu_form.addRow("Tanggal Selesai:", self.date_selesai)

        self.spn_jangka_waktu = QSpinBox()
        self.spn_jangka_waktu.setRange(1, 365)
        self.spn_jangka_waktu.setValue(30)
        self.spn_jangka_waktu.setSuffix(" hari")
        waktu_form.addRow("Jangka Waktu:", self.spn_jangka_waktu)

        waktu_group.setLayout(waktu_form)
        form1.addWidget(waktu_group)

        tabs.addTab(tab_kegiatan, "Data Kegiatan")

        # ========== TAB 2: ANGGARAN & UANG MUKA ==========
        tab_anggaran = QWidget()
        form2 = QVBoxLayout(tab_anggaran)

        # Anggaran DIPA
        anggaran_group = QGroupBox("Anggaran DIPA")
        anggaran_form = QFormLayout()

        self.txt_sumber_dana = QLineEdit()
        self.txt_sumber_dana.setText("DIPA")
        anggaran_form.addRow("Sumber Dana:", self.txt_sumber_dana)

        self.txt_kode_akun = QLineEdit()
        self.txt_kode_akun.setPlaceholderText("521211")
        anggaran_form.addRow("Kode Akun/MAK:", self.txt_kode_akun)

        self.spn_pagu = CurrencySpinBox()
        anggaran_form.addRow("Pagu Swakelola:", self.spn_pagu)

        anggaran_group.setLayout(anggaran_form)
        form2.addWidget(anggaran_group)

        # Uang Muka
        um_group = QGroupBox("Uang Muka Swakelola")
        um_form = QFormLayout()

        # Pemegang Uang Muka
        self.cmb_pum = QComboBox()
        self.cmb_pum.setEditable(True)
        self.load_pegawai_combo(self.cmb_pum)
        self.cmb_pum.currentIndexChanged.connect(self.on_pum_selected)
        um_form.addRow("Pemegang Uang Muka:", self.cmb_pum)

        self.txt_pum_nama = QLineEdit()
        um_form.addRow("Nama PUM:", self.txt_pum_nama)

        self.txt_pum_nip = QLineEdit()
        um_form.addRow("NIP PUM:", self.txt_pum_nip)

        self.txt_pum_jabatan = QLineEdit()
        um_form.addRow("Jabatan PUM:", self.txt_pum_jabatan)

        self.spn_uang_muka = CurrencySpinBox()
        um_form.addRow("Jumlah Uang Muka:", self.spn_uang_muka)

        self.date_uang_muka = QDateEdit()
        self.date_uang_muka.setCalendarPopup(True)
        self.date_uang_muka.setDate(QDate.currentDate())
        um_form.addRow("Tanggal Uang Muka:", self.date_uang_muka)

        um_group.setLayout(um_form)
        form2.addWidget(um_group)

        # Realisasi / Rampung
        rampung_group = QGroupBox("Realisasi / Kuitansi Rampung")
        rampung_form = QFormLayout()

        self.spn_realisasi = CurrencySpinBox()
        self.spn_realisasi.valueChanged.connect(self.update_selisih)
        rampung_form.addRow("Total Realisasi:", self.spn_realisasi)

        self.lbl_selisih = QLabel("Rp 0")
        self.lbl_selisih.setStyleSheet("font-weight: bold;")
        rampung_form.addRow("Sisa/Kekurangan:", self.lbl_selisih)

        self.date_rampung = QDateEdit()
        self.date_rampung.setCalendarPopup(True)
        self.date_rampung.setDate(QDate.currentDate().addDays(30))
        rampung_form.addRow("Tanggal Rampung:", self.date_rampung)

        rampung_group.setLayout(rampung_form)
        form2.addWidget(rampung_group)

        tabs.addTab(tab_anggaran, "Anggaran & Uang Muka")

        # ========== TAB 3: TIM PELAKSANA ==========
        tab_tim = QWidget()
        form3 = QVBoxLayout(tab_tim)

        # Ketua Tim
        ketua_group = QGroupBox("Ketua Tim Pelaksana")
        ketua_form = QFormLayout()

        self.cmb_ketua = QComboBox()
        self.cmb_ketua.setEditable(True)
        self.load_pegawai_combo(self.cmb_ketua)
        self.cmb_ketua.currentIndexChanged.connect(self.on_ketua_selected)
        ketua_form.addRow("Pilih Ketua Tim:", self.cmb_ketua)

        self.txt_ketua_nama = QLineEdit()
        ketua_form.addRow("Nama:", self.txt_ketua_nama)

        self.txt_ketua_nip = QLineEdit()
        ketua_form.addRow("NIP:", self.txt_ketua_nip)

        self.txt_ketua_jabatan = QLineEdit()
        ketua_form.addRow("Jabatan:", self.txt_ketua_jabatan)

        ketua_group.setLayout(ketua_form)
        form3.addWidget(ketua_group)

        # Sekretaris Tim
        sekretaris_group = QGroupBox("Sekretaris Tim")
        sekretaris_form = QFormLayout()

        self.cmb_sekretaris = QComboBox()
        self.cmb_sekretaris.setEditable(True)
        self.load_pegawai_combo(self.cmb_sekretaris)
        self.cmb_sekretaris.currentIndexChanged.connect(self.on_sekretaris_selected)
        sekretaris_form.addRow("Pilih Sekretaris:", self.cmb_sekretaris)

        self.txt_sekretaris_nama = QLineEdit()
        sekretaris_form.addRow("Nama:", self.txt_sekretaris_nama)

        self.txt_sekretaris_nip = QLineEdit()
        sekretaris_form.addRow("NIP:", self.txt_sekretaris_nip)

        sekretaris_group.setLayout(sekretaris_form)
        form3.addWidget(sekretaris_group)

        # Anggota Tim
        anggota_group = QGroupBox("Anggota Tim (pisahkan dengan baris baru)")
        anggota_layout = QVBoxLayout()

        self.txt_anggota = QTextEdit()
        self.txt_anggota.setPlaceholderText("Nama Anggota 1\nNama Anggota 2\nNama Anggota 3")
        self.txt_anggota.setMaximumHeight(100)
        anggota_layout.addWidget(self.txt_anggota)

        anggota_group.setLayout(anggota_layout)
        form3.addWidget(anggota_group)

        tabs.addTab(tab_tim, "Tim Pelaksana")

        # ========== TAB 4: PEJABAT ==========
        tab_pejabat = QWidget()
        form4 = QVBoxLayout(tab_pejabat)

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
        form4.addWidget(ppk_group)

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
        form4.addWidget(bendahara_group)

        form4.addStretch()
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

    def load_pegawai_combo(self, combo: QComboBox):
        """Load pegawai into combo box"""
        combo.clear()
        combo.addItem("-- Pilih Pegawai --", None)

        try:
            pegawai_list = self.db.get_all_pegawai(active_only=True)
            for p in pegawai_list:
                nama = p.get('nama', '')
                if p.get('gelar_depan'):
                    nama = f"{p['gelar_depan']} {nama}"
                if p.get('gelar_belakang'):
                    nama = f"{nama}, {p['gelar_belakang']}"
                combo.addItem(nama, p)
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

    def _fill_pegawai_fields(self, data, nama_field, nip_field, jabatan_field=None):
        """Helper to fill pegawai fields"""
        if data and isinstance(data, dict):
            nama = data.get('nama', '')
            if data.get('gelar_depan'):
                nama = f"{data['gelar_depan']} {nama}"
            if data.get('gelar_belakang'):
                nama = f"{nama}, {data['gelar_belakang']}"
            nama_field.setText(nama)
            nip_field.setText(data.get('nip', '') or '')
            if jabatan_field:
                jabatan_field.setText(data.get('jabatan', '') or '')

    def on_pum_selected(self, index):
        data = self.cmb_pum.currentData()
        self._fill_pegawai_fields(data, self.txt_pum_nama, self.txt_pum_nip, self.txt_pum_jabatan)

    def on_ketua_selected(self, index):
        data = self.cmb_ketua.currentData()
        self._fill_pegawai_fields(data, self.txt_ketua_nama, self.txt_ketua_nip, self.txt_ketua_jabatan)

    def on_sekretaris_selected(self, index):
        data = self.cmb_sekretaris.currentData()
        self._fill_pegawai_fields(data, self.txt_sekretaris_nama, self.txt_sekretaris_nip)

    def on_ppk_selected(self, index):
        data = self.cmb_ppk.currentData()
        self._fill_pegawai_fields(data, self.txt_ppk_nama, self.txt_ppk_nip)

    def on_bendahara_selected(self, index):
        data = self.cmb_bendahara.currentData()
        self._fill_pegawai_fields(data, self.txt_bendahara_nama, self.txt_bendahara_nip)

    def update_selisih(self):
        """Calculate difference between uang muka and realisasi"""
        uang_muka = self.spn_uang_muka.value()
        realisasi = self.spn_realisasi.value()
        selisih = uang_muka - realisasi

        if selisih >= 0:
            self.lbl_selisih.setText(f"Sisa: Rp {selisih:,.0f}".replace(',', '.'))
            self.lbl_selisih.setStyleSheet("font-weight: bold; color: #27ae60;")
        else:
            self.lbl_selisih.setText(f"Kekurangan: Rp {abs(selisih):,.0f}".replace(',', '.'))
            self.lbl_selisih.setStyleSheet("font-weight: bold; color: #e74c3c;")

    def load_data(self):
        """Load existing data"""
        if not self.sw_data:
            return

        d = self.sw_data

        self.txt_nama_kegiatan.setText(d.get('nama_kegiatan', '') or '')
        self.cmb_tipe_swakelola.setCurrentIndex(d.get('tipe_swakelola', 0) or 0)
        self.txt_deskripsi.setText(d.get('deskripsi', '') or '')
        self.txt_output.setText(d.get('output_kegiatan', '') or '')

        self.txt_nomor_kak.setText(d.get('nomor_kak', '') or '')
        self.txt_nomor_sk_tim.setText(d.get('nomor_sk_tim', '') or '')

        # SK KPA
        self.txt_nomor_sk_kpa.setText(d.get('nomor_sk_kpa', '') or '')
        self.txt_perihal_sk_kpa.setText(d.get('perihal_sk_kpa', '') or '')
        if d.get('tanggal_sk_kpa'):
            self.date_sk_kpa.setDate(QDate.fromString(str(d['tanggal_sk_kpa']), 'yyyy-MM-dd'))

        if d.get('tanggal_sk_tim'):
            self.date_sk_tim.setDate(QDate.fromString(str(d['tanggal_sk_tim']), 'yyyy-MM-dd'))
        if d.get('tanggal_mulai'):
            self.date_mulai.setDate(QDate.fromString(str(d['tanggal_mulai']), 'yyyy-MM-dd'))
        if d.get('tanggal_selesai'):
            self.date_selesai.setDate(QDate.fromString(str(d['tanggal_selesai']), 'yyyy-MM-dd'))
        self.spn_jangka_waktu.setValue(d.get('jangka_waktu', 30) or 30)

        self.txt_sumber_dana.setText(d.get('sumber_dana', 'DIPA') or 'DIPA')
        self.txt_kode_akun.setText(d.get('kode_akun', '') or '')
        self.spn_pagu.setValue(d.get('pagu_swakelola', 0) or 0)

        # Uang Muka
        self.txt_pum_nama.setText(d.get('pum_nama', '') or '')
        self.txt_pum_nip.setText(d.get('pum_nip', '') or '')
        self.txt_pum_jabatan.setText(d.get('pum_jabatan', '') or '')
        self.spn_uang_muka.setValue(d.get('uang_muka', 0) or 0)
        if d.get('tanggal_uang_muka'):
            self.date_uang_muka.setDate(QDate.fromString(str(d['tanggal_uang_muka']), 'yyyy-MM-dd'))

        # Realisasi
        self.spn_realisasi.setValue(d.get('total_realisasi', 0) or 0)
        if d.get('tanggal_rampung'):
            self.date_rampung.setDate(QDate.fromString(str(d['tanggal_rampung']), 'yyyy-MM-dd'))

        # Tim
        self.txt_ketua_nama.setText(d.get('ketua_nama', '') or '')
        self.txt_ketua_nip.setText(d.get('ketua_nip', '') or '')
        self.txt_ketua_jabatan.setText(d.get('ketua_jabatan', '') or '')
        self.txt_sekretaris_nama.setText(d.get('sekretaris_nama', '') or '')
        self.txt_sekretaris_nip.setText(d.get('sekretaris_nip', '') or '')
        self.txt_anggota.setText(d.get('anggota_tim', '') or '')

        # Pejabat
        self.txt_ppk_nama.setText(d.get('ppk_nama', '') or '')
        self.txt_ppk_nip.setText(d.get('ppk_nip', '') or '')
        self.txt_bendahara_nama.setText(d.get('bendahara_nama', '') or '')
        self.txt_bendahara_nip.setText(d.get('bendahara_nip', '') or '')

        self.update_selisih()

    def get_data(self) -> dict:
        """Get form data"""
        return {
            'nama_kegiatan': self.txt_nama_kegiatan.text().strip(),
            'tipe_swakelola': self.cmb_tipe_swakelola.currentIndex(),
            'tipe_swakelola_text': self.cmb_tipe_swakelola.currentText(),
            'deskripsi': self.txt_deskripsi.toPlainText().strip(),
            'output_kegiatan': self.txt_output.text().strip(),

            'nomor_kak': self.txt_nomor_kak.text().strip(),
            'nomor_sk_tim': self.txt_nomor_sk_tim.text().strip(),

            # SK KPA
            'nomor_sk_kpa': self.txt_nomor_sk_kpa.text().strip(),
            'tanggal_sk_kpa': self.date_sk_kpa.date().toPython(),
            'perihal_sk_kpa': self.txt_perihal_sk_kpa.text().strip(),

            'tanggal_sk_tim': self.date_sk_tim.date().toPython(),
            'tanggal_mulai': self.date_mulai.date().toPython(),
            'tanggal_selesai': self.date_selesai.date().toPython(),
            'jangka_waktu': self.spn_jangka_waktu.value(),

            'sumber_dana': self.txt_sumber_dana.text().strip(),
            'kode_akun': self.txt_kode_akun.text().strip(),
            'pagu_swakelola': self.spn_pagu.value(),

            # Uang Muka
            'pum_nama': self.txt_pum_nama.text().strip(),
            'pum_nip': self.txt_pum_nip.text().strip(),
            'pum_jabatan': self.txt_pum_jabatan.text().strip(),
            'uang_muka': self.spn_uang_muka.value(),
            'tanggal_uang_muka': self.date_uang_muka.date().toPython(),

            # Realisasi
            'total_realisasi': self.spn_realisasi.value(),
            'tanggal_rampung': self.date_rampung.date().toPython(),

            # Tim
            'ketua_nama': self.txt_ketua_nama.text().strip(),
            'ketua_nip': self.txt_ketua_nip.text().strip(),
            'ketua_jabatan': self.txt_ketua_jabatan.text().strip(),
            'sekretaris_nama': self.txt_sekretaris_nama.text().strip(),
            'sekretaris_nip': self.txt_sekretaris_nip.text().strip(),
            'anggota_tim': self.txt_anggota.toPlainText().strip(),

            # Pejabat
            'ppk_nama': self.txt_ppk_nama.text().strip(),
            'ppk_nip': self.txt_ppk_nip.text().strip(),
            'ppk_jabatan': self.txt_ppk_jabatan.text().strip(),
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

        try:
            if self.sw_data:
                self.db.update_swakelola(self.sw_data['id'], data)
            else:
                self.db.create_swakelola(data)

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan:\n{str(e)}")


# ============================================================================
# SWAKELOLA MANAGER (Main Window)
# ============================================================================

class SwakelolaManager(QDialog):
    """Main dialog for managing swakelola activities"""

    data_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db_manager_v4()

        self.setWindowTitle("📝 Kegiatan Swakelola")
        self.setMinimumSize(1200, 700)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()

        title = QLabel("📝 Daftar Kegiatan Swakelola")
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
        self.txt_search.setPlaceholderText("Cari kegiatan...")
        self.txt_search.setMinimumWidth(200)
        self.txt_search.textChanged.connect(self.filter_data)
        header.addWidget(self.txt_search)

        layout.addLayout(header)

        # Toolbar
        toolbar = QHBoxLayout()

        btn_add = QPushButton("➕ Tambah Kegiatan Swakelola")
        btn_add.setStyleSheet("background-color: #3498db; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_add.clicked.connect(self.add_swakelola)
        toolbar.addWidget(btn_add)

        btn_edit = QPushButton("✏️ Edit")
        btn_edit.clicked.connect(self.edit_swakelola)
        toolbar.addWidget(btn_edit)

        btn_delete = QPushButton("🗑️ Hapus")
        btn_delete.setStyleSheet("background-color: #e74c3c; color: white;")
        btn_delete.clicked.connect(self.delete_swakelola)
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
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "No", "Nama Kegiatan", "Tipe", "Pagu",
            "Uang Muka", "Realisasi", "Sisa/Kurang",
            "Status", "Tgl Mulai", "Tgl Selesai", "ID"
        ])

        self.table.setColumnHidden(10, True)  # Hide ID

        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 80)
        self.table.setColumnWidth(8, 90)
        self.table.setColumnWidth(9, 90)

        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.edit_swakelola)

        layout.addWidget(self.table)

        # Summary
        summary = QHBoxLayout()
        self.lbl_total = QLabel("Total: 0 kegiatan")
        self.lbl_total.setStyleSheet("font-weight: bold;")
        summary.addWidget(self.lbl_total)

        summary.addStretch()

        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.accept)
        summary.addWidget(btn_close)

        layout.addLayout(summary)

    def load_data(self):
        """Load swakelola data"""
        tahun = self.cmb_tahun.currentData()
        self.all_data = self.db.get_all_swakelola(tahun=tahun)
        self.filter_data()

    def filter_data(self):
        """Filter displayed data"""
        search = self.txt_search.text().lower()

        filtered = []
        for sw in self.all_data:
            if search:
                searchable = f"{sw.get('nama_kegiatan', '')}".lower()
                if search not in searchable:
                    continue
            filtered.append(sw)

        self.display_data(filtered)

    def display_data(self, data_list: List[Dict]):
        """Display data in table"""
        self.table.setRowCount(len(data_list))

        def fmt_rp(value):
            return f"Rp {value:,.0f}".replace(',', '.')

        for row, sw in enumerate(data_list):
            # No
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))

            # Nama Kegiatan
            self.table.setItem(row, 1, QTableWidgetItem(sw.get('nama_kegiatan', '') or '-'))

            # Tipe
            tipe = sw.get('tipe_swakelola', 0) or 0
            self.table.setItem(row, 2, QTableWidgetItem(f"Tipe {tipe + 1}"))

            # Pagu
            self.table.setItem(row, 3, QTableWidgetItem(fmt_rp(sw.get('pagu_swakelola', 0) or 0)))

            # Uang Muka
            uang_muka = sw.get('uang_muka', 0) or 0
            self.table.setItem(row, 4, QTableWidgetItem(fmt_rp(uang_muka)))

            # Realisasi
            realisasi = sw.get('total_realisasi', 0) or 0
            self.table.setItem(row, 5, QTableWidgetItem(fmt_rp(realisasi)))

            # Sisa/Kurang
            selisih = uang_muka - realisasi
            selisih_item = QTableWidgetItem(fmt_rp(abs(selisih)))
            if selisih >= 0:
                selisih_item.setForeground(QColor('#27ae60'))
            else:
                selisih_item.setForeground(QColor('#e74c3c'))
            self.table.setItem(row, 6, selisih_item)

            # Status
            status = sw.get('status', 'draft')
            status_item = QTableWidgetItem(status.title())
            if status == 'completed':
                status_item.setForeground(QColor('#27ae60'))
            elif status == 'in_progress':
                status_item.setForeground(QColor('#f39c12'))
            self.table.setItem(row, 7, status_item)

            # Tanggal
            self.table.setItem(row, 8, QTableWidgetItem(str(sw.get('tanggal_mulai', '') or '-')))
            self.table.setItem(row, 9, QTableWidgetItem(str(sw.get('tanggal_selesai', '') or '-')))

            # ID (hidden)
            self.table.setItem(row, 10, QTableWidgetItem(str(sw['id'])))

        self.lbl_total.setText(f"Total: {len(data_list)} kegiatan")

    def get_selected_id(self) -> Optional[int]:
        """Get selected ID"""
        row = self.table.currentRow()
        if row < 0:
            return None
        id_item = self.table.item(row, 10)
        return int(id_item.text()) if id_item else None

    def add_swakelola(self):
        """Add new swakelola"""
        dialog = SwakelolaDialog(parent=self)
        if dialog.exec():
            self.load_data()
            self.data_changed.emit()

    def edit_swakelola(self):
        """Edit selected swakelola"""
        sw_id = self.get_selected_id()
        if not sw_id:
            QMessageBox.warning(self, "Peringatan", "Pilih kegiatan swakelola terlebih dahulu!")
            return

        sw_data = self.db.get_swakelola(sw_id)
        if not sw_data:
            return

        dialog = SwakelolaDialog(sw_data, parent=self)
        if dialog.exec():
            self.load_data()
            self.data_changed.emit()

    def delete_swakelola(self):
        """Delete selected swakelola"""
        sw_id = self.get_selected_id()
        if not sw_id:
            QMessageBox.warning(self, "Peringatan", "Pilih kegiatan swakelola terlebih dahulu!")
            return

        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            "Hapus kegiatan swakelola ini?\n\n"
            "Data dan dokumen terkait akan dihapus.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.delete_swakelola(sw_id)
                self.load_data()
                self.data_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus:\n{str(e)}")

    def generate_documents(self):
        """Generate documents for selected swakelola"""
        sw_id = self.get_selected_id()
        if not sw_id:
            QMessageBox.warning(self, "Peringatan", "Pilih kegiatan swakelola terlebih dahulu!")
            return

        sw_data = self.db.get_swakelola(sw_id)
        if not sw_data:
            return

        dialog = GenerateSWDocumentDialog(sw_data, parent=self)
        if dialog.exec():
            self.load_data()


# ============================================================================
# GENERATE DOCUMENT DIALOG
# ============================================================================

class GenerateSWDocumentDialog(QDialog):
    """Dialog for generating swakelola documents"""

    def __init__(self, sw_data: dict, parent=None):
        super().__init__(parent)
        self.sw_data = sw_data
        self.db = get_db_manager_v4()

        self.setWindowTitle("Generate Dokumen Swakelola")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Info
        info_group = QGroupBox("Kegiatan Swakelola")
        info_form = QFormLayout()
        info_form.addRow("Kegiatan:", QLabel(self.sw_data.get('nama_kegiatan', '-')))
        tipe = self.sw_data.get('tipe_swakelola', 0) or 0
        info_form.addRow("Tipe:", QLabel(f"Tipe {tipe + 1}"))
        info_group.setLayout(info_form)
        layout.addWidget(info_group)

        # Document checkboxes
        doc_group = QGroupBox("Pilih Dokumen yang akan di-generate")
        doc_layout = QVBoxLayout()

        self.chk_kak = QCheckBox("📄 KAK Swakelola")
        self.chk_kak.setChecked(True)
        doc_layout.addWidget(self.chk_kak)

        self.chk_rab = QCheckBox("📊 RAB Swakelola (Excel)")
        self.chk_rab.setChecked(True)
        doc_layout.addWidget(self.chk_rab)

        self.chk_sk_tim = QCheckBox("📄 SK Tim Pelaksana")
        self.chk_sk_tim.setChecked(True)
        doc_layout.addWidget(self.chk_sk_tim)

        self.chk_kuitansi_um = QCheckBox("💰 Kuitansi Uang Muka Swakelola")
        doc_layout.addWidget(self.chk_kuitansi_um)

        self.chk_bap = QCheckBox("📄 Berita Acara Pembayaran")
        doc_layout.addWidget(self.chk_bap)

        self.chk_laporan = QCheckBox("📝 Laporan Kemajuan")
        doc_layout.addWidget(self.chk_laporan)

        self.chk_kuitansi_rampung = QCheckBox("💰 Kuitansi Rampung Swakelola")
        doc_layout.addWidget(self.chk_kuitansi_rampung)

        self.chk_bast = QCheckBox("📄 BAST Swakelola")
        doc_layout.addWidget(self.chk_bast)

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
        from app.templates.engine import get_template_engine
        from app.core.config import WORD_TEMPLATES_DIR, EXCEL_TEMPLATES_DIR

        engine = get_template_engine()
        generated = []
        errors = []

        # Prepare placeholders
        placeholders = self._prepare_placeholders()

        # Output folder
        output_folder = os.path.join(
            OUTPUT_DIR,
            str(TAHUN_ANGGARAN),
            "Swakelola",
            f"SW_{self.sw_data['id']}_{self.sw_data.get('nama_kegiatan', 'unknown')[:20]}"
        )
        os.makedirs(output_folder, exist_ok=True)

        # Generate each selected document
        docs_to_generate = []
        if self.chk_kak.isChecked():
            docs_to_generate.append(('kak_swakelola', 'KAK_Swakelola', 'word'))
        if self.chk_rab.isChecked():
            docs_to_generate.append(('rab_swakelola', 'RAB_Swakelola', 'excel'))
        if self.chk_sk_tim.isChecked():
            docs_to_generate.append(('sk_tim_swakelola', 'SK_Tim_Pelaksana', 'word'))
        if self.chk_kuitansi_um.isChecked():
            docs_to_generate.append(('kuitansi_uang_muka', 'Kuitansi_Uang_Muka', 'word'))
        if self.chk_bap.isChecked():
            docs_to_generate.append(('bap_swakelola', 'BA_Pembayaran', 'word'))
        if self.chk_laporan.isChecked():
            docs_to_generate.append(('laporan_kemajuan', 'Laporan_Kemajuan', 'word'))
        if self.chk_kuitansi_rampung.isChecked():
            docs_to_generate.append(('kuitansi_rampung', 'Kuitansi_Rampung', 'word'))
        if self.chk_bast.isChecked():
            docs_to_generate.append(('bast_swakelola', 'BAST_Swakelola', 'word'))

        for template_name, output_name, doc_type in docs_to_generate:
            try:
                if doc_type == 'word':
                    template_path = os.path.join(WORD_TEMPLATES_DIR, f"{template_name}.docx")
                    output_path = os.path.join(output_folder, f"{output_name}.docx")
                    engine.merge_word(
                        template_path=template_path,
                        data=placeholders,
                        output_path=output_path
                    )
                elif doc_type == 'excel':
                    template_path = os.path.join(EXCEL_TEMPLATES_DIR, f"{template_name}.xlsx")
                    output_path = os.path.join(output_folder, f"{output_name}.xlsx")
                    engine.merge_excel(
                        template_path=template_path,
                        data=placeholders,
                        output_path=output_path
                    )
                generated.append(output_name)
            except Exception as e:
                errors.append(f"{output_name}: {str(e)}")

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
            QMessageBox.warning(self, "Error", "Tidak ada dokumen yang berhasil di-generate.\n\n" + "\n".join(errors))

    def _prepare_placeholders(self) -> dict:
        """Prepare placeholders from swakelola data"""
        d = self.sw_data

        # Calculate selisih
        uang_muka = d.get('uang_muka', 0) or 0
        realisasi = d.get('total_realisasi', 0) or 0
        selisih = uang_muka - realisasi

        # Format currency
        def fmt_rp(value):
            return f"Rp {value:,.0f}".replace(',', '.')

        # Terbilang
        def terbilang(n):
            from app.templates.engine import format_terbilang
            return format_terbilang(n)

        return {
            # DIPA
            'satker_kode': SATKER_DEFAULT.get('kode', ''),
            'satker_nama': SATKER_DEFAULT.get('nama', ''),
            'satker_alamat': SATKER_DEFAULT.get('alamat', ''),
            'satker_kota': SATKER_DEFAULT.get('kota', ''),
            'satker_provinsi': SATKER_DEFAULT.get('provinsi', ''),
            'kementerian': SATKER_DEFAULT.get('kementerian', ''),
            'eselon1': SATKER_DEFAULT.get('eselon1', ''),
            'tahun_anggaran': str(TAHUN_ANGGARAN),
            'sumber_dana': d.get('sumber_dana', 'DIPA'),
            'kode_akun': d.get('kode_akun', ''),

            # Kegiatan
            'nama_kegiatan': d.get('nama_kegiatan', ''),
            'nama_paket': d.get('nama_kegiatan', ''),
            'tipe_swakelola': d.get('tipe_swakelola_text', ''),
            'deskripsi': d.get('deskripsi', ''),
            'output_kegiatan': d.get('output_kegiatan', ''),

            # Nomor dokumen
            'nomor_kak': d.get('nomor_kak', ''),
            'nomor_sk_tim': d.get('nomor_sk_tim', ''),

            # Waktu
            'tanggal_sk_tim': str(d.get('tanggal_sk_tim', '')),
            'tanggal_mulai': str(d.get('tanggal_mulai', '')),
            'tanggal_selesai': str(d.get('tanggal_selesai', '')),
            'jangka_waktu': str(d.get('jangka_waktu', 30)),

            # Anggaran
            'pagu_swakelola': fmt_rp(d.get('pagu_swakelola', 0) or 0),
            'pagu_swakelola_terbilang': terbilang(d.get('pagu_swakelola', 0) or 0),

            # Uang Muka
            'pum_nama': d.get('pum_nama', ''),
            'pum_nip': d.get('pum_nip', ''),
            'pum_jabatan': d.get('pum_jabatan', ''),
            'uang_muka': fmt_rp(uang_muka),
            'uang_muka_terbilang': terbilang(uang_muka),
            'tanggal_uang_muka': str(d.get('tanggal_uang_muka', '')),

            # Realisasi / Rampung
            'total_realisasi': fmt_rp(realisasi),
            'total_realisasi_terbilang': terbilang(realisasi),
            'sisa_uang_muka': fmt_rp(max(0, selisih)),
            'kekurangan_bayar': fmt_rp(max(0, -selisih)),
            'tanggal_rampung': str(d.get('tanggal_rampung', '')),

            # Tim
            'ketua_nama': d.get('ketua_nama', ''),
            'ketua_nip': d.get('ketua_nip', ''),
            'ketua_jabatan': d.get('ketua_jabatan', ''),
            'sekretaris_nama': d.get('sekretaris_nama', ''),
            'sekretaris_nip': d.get('sekretaris_nip', ''),
            'anggota_tim': d.get('anggota_tim', ''),

            # Pejabat
            'ppk_nama': d.get('ppk_nama', ''),
            'ppk_nip': d.get('ppk_nip', ''),
            'ppk_jabatan': d.get('ppk_jabatan', 'Pejabat Pembuat Komitmen'),
            'bendahara_nama': d.get('bendahara_nama', ''),
            'bendahara_nip': d.get('bendahara_nip', ''),
        }


# ============================================================================
# HELPER FUNCTION
# ============================================================================

def show_swakelola_manager(parent=None) -> SwakelolaManager:
    """Show swakelola manager dialog"""
    dialog = SwakelolaManager(parent)
    dialog.exec()
    return dialog
