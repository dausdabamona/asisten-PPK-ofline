"""
PPK DOCUMENT FACTORY - Paket Form Dialog
=========================================
Dialog untuk membuat dan mengedit paket pengadaan.

Author: PPK Document Factory Team
Version: 4.0
"""

from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLineEdit, QComboBox, QDateEdit,
    QSpinBox, QDoubleSpinBox, QPushButton, QLabel,
    QScrollArea, QWidget, QMessageBox
)
from PySide6.QtCore import Qt, QDate

from app.core.config import TAHUN_ANGGARAN, SATKER_DEFAULT
from app.core.database import get_db_manager


class PaketFormDialog(QDialog):
    """Dialog for creating/editing paket pengadaan."""

    def __init__(self, paket_id: int = None, parent=None):
        super().__init__(parent)
        self.paket_id = paket_id
        self.db = get_db_manager()

        self.setWindowTitle("Tambah Paket Baru" if not paket_id else "Edit Paket")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)

        self._setup_ui()

        if paket_id:
            self._load_paket()

    def _setup_ui(self):
        """Setup dialog UI."""
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
        self.spn_jangka.valueChanged.connect(self._update_tanggal_selesai)
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
        self._load_pegawai_combo(self.cmb_ppk, 'ppk')
        pejabat_layout.addRow("PPK:", self.cmb_ppk)

        self.cmb_ppspm = QComboBox()
        self._load_pegawai_combo(self.cmb_ppspm, 'ppspm')
        pejabat_layout.addRow("PPSPM:", self.cmb_ppspm)

        self.cmb_bendahara = QComboBox()
        self._load_pegawai_combo(self.cmb_bendahara, 'bendahara')
        pejabat_layout.addRow("Bendahara:", self.cmb_bendahara)

        pejabat_group.setLayout(pejabat_layout)
        scroll_layout.addWidget(pejabat_group)

        # Penyedia
        penyedia_group = QGroupBox("Penyedia")
        penyedia_layout = QFormLayout()

        self.cmb_penyedia = QComboBox()
        self._load_penyedia_combo()
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
        btn_save.clicked.connect(self._save_paket)
        btn_layout.addWidget(btn_save)

        btn_cancel = QPushButton("Batal")
        btn_cancel.setObjectName("btnSecondary")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    def _load_pegawai_combo(self, combo: QComboBox, role: str):
        """Load pegawai list into combo box."""
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

    def _load_penyedia_combo(self):
        """Load penyedia list into combo box."""
        self.cmb_penyedia.clear()
        self.cmb_penyedia.addItem("-- Pilih --", None)

        penyedia_list = self.db.get_penyedia_list()
        for pen in penyedia_list:
            self.cmb_penyedia.addItem(pen['nama'], pen['id'])

    def _update_tanggal_selesai(self):
        """Update end date based on duration."""
        start = self.date_mulai.date()
        days = self.spn_jangka.value()
        self.date_selesai.setDate(start.addDays(days))

    def _load_paket(self):
        """Load paket data for editing."""
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

        # Workflow validation: HPS status
        survey_locked = paket.get('survey_locked', 0)
        hps_locked = paket.get('hps_locked', 0)

        if not survey_locked:
            self.spn_hps.setEnabled(False)
            self.spn_hps.setToolTip("HPS akan otomatis dihitung dari survey harga.")
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
            self.spn_hps.setToolTip("Nilai HPS dapat diubah.")
            self.spn_hps.setStyleSheet("")
            self.lbl_hps_status.setText("✏️ Dapat diedit")
            self.lbl_hps_status.setStyleSheet("font-size: 10px; color: #2196f3;")

        # Workflow validation: Kontrak status
        kontrak_final_locked = paket.get('kontrak_final_locked', 0)

        if kontrak_final_locked:
            self.spn_kontrak.setEnabled(False)
            self.spn_kontrak.setToolTip("Nilai Kontrak sudah FINAL.")
            self.spn_kontrak.setStyleSheet("background-color: #c8e6c9; color: #2e7d32;")
            self.lbl_kontrak_status.setText("🔒 Kontrak Final")
            self.lbl_kontrak_status.setStyleSheet("font-size: 10px; color: #2e7d32;")
        elif not hps_locked:
            self.spn_kontrak.setEnabled(False)
            self.spn_kontrak.setToolTip("HPS harus ditetapkan terlebih dahulu.")
            self.spn_kontrak.setStyleSheet("background-color: #e0e0e0;")
            self.lbl_kontrak_status.setText("⏳ Menunggu HPS")
            self.lbl_kontrak_status.setStyleSheet("font-size: 10px; color: #ff9800;")
        else:
            self.spn_kontrak.setEnabled(True)
            self.spn_kontrak.setToolTip("Nilai Kontrak hasil negosiasi.")
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

    def _save_paket(self):
        """Save paket data."""
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
