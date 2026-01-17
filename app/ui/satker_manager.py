"""
PPK DOCUMENT FACTORY v3.0 - Satker Manager
============================================
Master Data Satuan Kerja
"""

from typing import Dict, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QGroupBox,
    QMessageBox, QFrame
)
from PySide6.QtCore import Signal

from app.core.database import get_db_manager


class SatkerManager(QDialog):
    """Dialog for managing Satker (Satuan Kerja) data"""

    satker_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db_manager()

        self.setWindowTitle("Data Satuan Kerja")
        self.setMinimumWidth(600)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Data Satuan Kerja (Satker)")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)

        info = QLabel("Data satker digunakan untuk mengisi placeholder dokumen.")
        info.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(info)

        # Instansi Group
        instansi_group = QGroupBox("Identitas Instansi")
        instansi_layout = QFormLayout()

        self.txt_kementerian = QLineEdit()
        self.txt_kementerian.setPlaceholderText("Nama Kementerian/Lembaga...")
        instansi_layout.addRow("Kementerian:", self.txt_kementerian)

        self.txt_eselon1 = QLineEdit()
        self.txt_eselon1.setPlaceholderText("Nama Unit Eselon I...")
        instansi_layout.addRow("Eselon I:", self.txt_eselon1)

        self.txt_kode = QLineEdit()
        self.txt_kode.setPlaceholderText("Kode Satker (6 digit)...")
        self.txt_kode.setMaximumWidth(150)
        instansi_layout.addRow("Kode Satker:", self.txt_kode)

        self.txt_nama = QLineEdit()
        self.txt_nama.setPlaceholderText("Nama lengkap satuan kerja...")
        instansi_layout.addRow("Nama Satker:", self.txt_nama)

        self.txt_nama_pendek = QLineEdit()
        self.txt_nama_pendek.setPlaceholderText("Nama pendek/singkatan...")
        instansi_layout.addRow("Nama Pendek:", self.txt_nama_pendek)

        instansi_group.setLayout(instansi_layout)
        layout.addWidget(instansi_group)

        # Alamat Group
        alamat_group = QGroupBox("Alamat")
        alamat_layout = QFormLayout()

        self.txt_alamat = QLineEdit()
        self.txt_alamat.setPlaceholderText("Jl. Nama Jalan No. XX...")
        alamat_layout.addRow("Alamat:", self.txt_alamat)

        lokasi_layout = QHBoxLayout()
        self.txt_kota = QLineEdit()
        self.txt_kota.setPlaceholderText("Nama Kota/Kabupaten...")
        lokasi_layout.addWidget(self.txt_kota)

        self.txt_kode_pos = QLineEdit()
        self.txt_kode_pos.setPlaceholderText("Kode Pos")
        self.txt_kode_pos.setMaximumWidth(80)
        lokasi_layout.addWidget(self.txt_kode_pos)

        alamat_layout.addRow("Kota:", lokasi_layout)

        self.txt_provinsi = QLineEdit()
        self.txt_provinsi.setPlaceholderText("Nama Provinsi...")
        alamat_layout.addRow("Provinsi:", self.txt_provinsi)

        alamat_group.setLayout(alamat_layout)
        layout.addWidget(alamat_group)

        # Kontak Group
        kontak_group = QGroupBox("Kontak")
        kontak_layout = QFormLayout()

        telp_layout = QHBoxLayout()
        self.txt_telepon = QLineEdit()
        self.txt_telepon.setPlaceholderText("(0xx) xxxxxxx")
        telp_layout.addWidget(self.txt_telepon)

        telp_layout.addWidget(QLabel("Fax:"))
        self.txt_fax = QLineEdit()
        self.txt_fax.setPlaceholderText("(0xx) xxxxxxx")
        telp_layout.addWidget(self.txt_fax)

        kontak_layout.addRow("Telepon:", telp_layout)

        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("email@domain.go.id")
        kontak_layout.addRow("Email:", self.txt_email)

        self.txt_website = QLineEdit()
        self.txt_website.setPlaceholderText("www.example.go.id")
        kontak_layout.addRow("Website:", self.txt_website)

        kontak_group.setLayout(kontak_layout)
        layout.addWidget(kontak_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_save = QPushButton("Simpan")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        btn_save.clicked.connect(self.save_data)
        btn_layout.addWidget(btn_save)

        btn_cancel = QPushButton("Tutup")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    def load_data(self):
        """Load satker data from database"""
        satker = self.db.get_satker()

        self.satker_id = satker.get('id')

        self.txt_kementerian.setText(satker.get('kementerian', '') or '')
        self.txt_eselon1.setText(satker.get('eselon1', '') or '')
        self.txt_kode.setText(satker.get('kode', '') or '')
        self.txt_nama.setText(satker.get('nama', '') or '')
        self.txt_nama_pendek.setText(satker.get('nama_pendek', '') or '')
        self.txt_alamat.setText(satker.get('alamat', '') or '')
        self.txt_kota.setText(satker.get('kota', '') or '')
        self.txt_kode_pos.setText(satker.get('kode_pos', '') or '')
        self.txt_provinsi.setText(satker.get('provinsi', '') or '')
        self.txt_telepon.setText(satker.get('telepon', '') or '')
        self.txt_fax.setText(satker.get('fax', '') or '')
        self.txt_email.setText(satker.get('email', '') or '')
        self.txt_website.setText(satker.get('website', '') or '')

    def get_data(self) -> Dict:
        """Get form data"""
        data = {
            'kementerian': self.txt_kementerian.text().strip() or None,
            'eselon1': self.txt_eselon1.text().strip() or None,
            'kode': self.txt_kode.text().strip() or None,
            'nama': self.txt_nama.text().strip() or None,
            'nama_pendek': self.txt_nama_pendek.text().strip() or None,
            'alamat': self.txt_alamat.text().strip() or None,
            'kota': self.txt_kota.text().strip() or None,
            'kode_pos': self.txt_kode_pos.text().strip() or None,
            'provinsi': self.txt_provinsi.text().strip() or None,
            'telepon': self.txt_telepon.text().strip() or None,
            'fax': self.txt_fax.text().strip() or None,
            'email': self.txt_email.text().strip() or None,
            'website': self.txt_website.text().strip() or None,
        }

        if hasattr(self, 'satker_id') and self.satker_id:
            data['id'] = self.satker_id

        return data

    def save_data(self):
        """Validate and save data"""
        data = self.get_data()

        # Validation
        if not data.get('nama'):
            QMessageBox.warning(self, "Validasi", "Nama Satker wajib diisi!")
            self.txt_nama.setFocus()
            return

        if not data.get('kode'):
            QMessageBox.warning(self, "Validasi", "Kode Satker wajib diisi!")
            self.txt_kode.setFocus()
            return

        try:
            self.db.save_satker(data)
            QMessageBox.information(self, "Sukses", "Data Satker berhasil disimpan!")
            self.satker_changed.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data:\n{str(e)}")
