"""
PPK DOCUMENT FACTORY v3.0 - Survey Toko Manager
================================================
UI untuk mengelola Data Toko/Sumber Harga Survey
"""

import os
from datetime import date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QMessageBox, QFrame, QStackedWidget, QDateEdit, QTabWidget,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont

from app.core.database import get_db_manager


# Jenis Survey
JENIS_SURVEY = {
    'LURING': 'Luring (Offline/Langsung)',
    'DARING': 'Daring (Online/Marketplace)',
    'KONTRAK': 'Kontrak Sebelumnya'
}

# Platform Online
PLATFORM_ONLINE = [
    'Tokopedia',
    'Shopee',
    'Bukalapak',
    'Blibli',
    'Lazada',
    'Amazon',
    'Website Resmi',
    'E-Katalog LKPP',
    'Lainnya'
]


class SurveyTokoDialog(QDialog):
    """Dialog untuk add/edit single toko survey"""
    
    def __init__(self, paket_id: int, toko_data: dict = None, parent=None):
        super().__init__(parent)
        self.paket_id = paket_id
        self.toko_data = toko_data  # None for new
        self.db = get_db_manager()
        
        self.setWindowTitle("Tambah Toko Survey" if not toko_data else "Edit Toko Survey")
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)
        
        self.setup_ui()
        
        if toko_data:
            self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Jenis Survey
        jenis_group = QGroupBox("Jenis Sumber Harga")
        jenis_layout = QHBoxLayout()
        
        self.cmb_jenis = QComboBox()
        for code, name in JENIS_SURVEY.items():
            self.cmb_jenis.addItem(name, code)
        self.cmb_jenis.currentIndexChanged.connect(self.on_jenis_changed)
        jenis_layout.addWidget(self.cmb_jenis)
        
        jenis_group.setLayout(jenis_layout)
        layout.addWidget(jenis_group)
        
        # Stacked widget for different forms
        self.stack = QStackedWidget()
        
        # =====================================================================
        # PAGE 0: LURING (Offline)
        # =====================================================================
        page_luring = QWidget()
        luring_layout = QFormLayout(page_luring)
        
        self.txt_nama_toko = QLineEdit()
        self.txt_nama_toko.setPlaceholderText("Nama toko/supplier...")
        luring_layout.addRow("Nama Toko *:", self.txt_nama_toko)
        
        self.txt_alamat = QTextEdit()
        self.txt_alamat.setMaximumHeight(60)
        self.txt_alamat.setPlaceholderText("Alamat lengkap toko...")
        luring_layout.addRow("Alamat:", self.txt_alamat)
        
        self.txt_kota = QLineEdit()
        self.txt_kota.setPlaceholderText("Kota/Kabupaten...")
        luring_layout.addRow("Kota:", self.txt_kota)
        
        self.txt_telepon = QLineEdit()
        self.txt_telepon.setPlaceholderText("Nomor telepon...")
        luring_layout.addRow("Telepon:", self.txt_telepon)
        
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("Email (opsional)...")
        luring_layout.addRow("Email:", self.txt_email)
        
        self.date_survey = QDateEdit()
        self.date_survey.setCalendarPopup(True)
        self.date_survey.setDate(QDate.currentDate())
        luring_layout.addRow("Tanggal Survey:", self.date_survey)
        
        self.txt_surveyor = QLineEdit()
        self.txt_surveyor.setPlaceholderText("Nama petugas survey...")
        luring_layout.addRow("Nama Surveyor:", self.txt_surveyor)
        
        self.txt_nip_surveyor = QLineEdit()
        self.txt_nip_surveyor.setPlaceholderText("NIP petugas (jika PNS)...")
        luring_layout.addRow("NIP Surveyor:", self.txt_nip_surveyor)
        
        self.stack.addWidget(page_luring)
        
        # =====================================================================
        # PAGE 1: DARING (Online)
        # =====================================================================
        page_daring = QWidget()
        daring_layout = QFormLayout(page_daring)
        
        self.txt_nama_toko_d = QLineEdit()
        self.txt_nama_toko_d.setPlaceholderText("Nama toko online...")
        daring_layout.addRow("Nama Toko *:", self.txt_nama_toko_d)
        
        self.cmb_platform = QComboBox()
        self.cmb_platform.setEditable(True)
        self.cmb_platform.addItems(PLATFORM_ONLINE)
        daring_layout.addRow("Platform:", self.cmb_platform)
        
        self.txt_link = QLineEdit()
        self.txt_link.setPlaceholderText("https://...")
        daring_layout.addRow("Link Produk:", self.txt_link)
        
        self.txt_alamat_d = QTextEdit()
        self.txt_alamat_d.setMaximumHeight(60)
        self.txt_alamat_d.setPlaceholderText("Alamat toko (dari profil seller)...")
        daring_layout.addRow("Alamat Seller:", self.txt_alamat_d)
        
        self.txt_kota_d = QLineEdit()
        self.txt_kota_d.setPlaceholderText("Lokasi seller...")
        daring_layout.addRow("Kota Seller:", self.txt_kota_d)
        
        self.date_survey_d = QDateEdit()
        self.date_survey_d.setCalendarPopup(True)
        self.date_survey_d.setDate(QDate.currentDate())
        daring_layout.addRow("Tanggal Akses:", self.date_survey_d)
        
        self.txt_surveyor_d = QLineEdit()
        self.txt_surveyor_d.setPlaceholderText("Nama petugas yang mengakses...")
        daring_layout.addRow("Diakses Oleh:", self.txt_surveyor_d)
        
        self.stack.addWidget(page_daring)
        
        # =====================================================================
        # PAGE 2: KONTRAK (Reference)
        # =====================================================================
        page_kontrak = QWidget()
        kontrak_layout = QFormLayout(page_kontrak)
        
        self.txt_nama_penyedia = QLineEdit()
        self.txt_nama_penyedia.setPlaceholderText("Nama penyedia pada kontrak referensi...")
        kontrak_layout.addRow("Nama Penyedia *:", self.txt_nama_penyedia)
        
        self.txt_nomor_kontrak = QLineEdit()
        self.txt_nomor_kontrak.setPlaceholderText("Nomor kontrak/SPK referensi...")
        kontrak_layout.addRow("Nomor Kontrak:", self.txt_nomor_kontrak)
        
        self.cmb_tahun_kontrak = QComboBox()
        current_year = date.today().year
        for year in range(current_year, current_year - 5, -1):
            self.cmb_tahun_kontrak.addItem(str(year), year)
        kontrak_layout.addRow("Tahun Kontrak:", self.cmb_tahun_kontrak)
        
        self.txt_instansi = QLineEdit()
        self.txt_instansi.setPlaceholderText("Nama instansi/satker pemilik kontrak...")
        kontrak_layout.addRow("Instansi:", self.txt_instansi)
        
        self.txt_alamat_k = QTextEdit()
        self.txt_alamat_k.setMaximumHeight(60)
        self.txt_alamat_k.setPlaceholderText("Alamat penyedia...")
        kontrak_layout.addRow("Alamat Penyedia:", self.txt_alamat_k)
        
        self.txt_kota_k = QLineEdit()
        kontrak_layout.addRow("Kota:", self.txt_kota_k)
        
        self.txt_telepon_k = QLineEdit()
        kontrak_layout.addRow("Telepon:", self.txt_telepon_k)
        
        self.stack.addWidget(page_kontrak)
        
        layout.addWidget(self.stack)
        
        # Keterangan (common)
        ket_group = QGroupBox("Keterangan")
        ket_layout = QVBoxLayout()
        self.txt_keterangan = QTextEdit()
        self.txt_keterangan.setMaximumHeight(60)
        self.txt_keterangan.setPlaceholderText("Catatan tambahan...")
        ket_layout.addWidget(self.txt_keterangan)
        ket_group.setLayout(ket_layout)
        layout.addWidget(ket_group)
        
        layout.addStretch()
        
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
                border: 1px solid #bdc3c7;
                border-radius: 5px;
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
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton#btnSuccess:hover {
                background-color: #219a52;
            }
        """)
    
    def on_jenis_changed(self, index):
        """Switch form based on jenis survey"""
        self.stack.setCurrentIndex(index)
    
    def load_data(self):
        """Load existing data"""
        if not self.toko_data:
            return
        
        jenis = self.toko_data.get('jenis_survey', 'LURING')
        idx = self.cmb_jenis.findData(jenis)
        if idx >= 0:
            self.cmb_jenis.setCurrentIndex(idx)
        
        self.txt_keterangan.setPlainText(self.toko_data.get('keterangan', ''))
        
        # Load based on jenis
        if jenis == 'LURING':
            self.txt_nama_toko.setText(self.toko_data.get('nama_toko', ''))
            self.txt_alamat.setPlainText(self.toko_data.get('alamat', ''))
            self.txt_kota.setText(self.toko_data.get('kota', ''))
            self.txt_telepon.setText(self.toko_data.get('telepon', ''))
            self.txt_email.setText(self.toko_data.get('email', ''))
            self.txt_surveyor.setText(self.toko_data.get('nama_surveyor', ''))
            self.txt_nip_surveyor.setText(self.toko_data.get('nip_surveyor', ''))
            if self.toko_data.get('tanggal_survey'):
                self.date_survey.setDate(QDate.fromString(self.toko_data['tanggal_survey'], 'yyyy-MM-dd'))
                
        elif jenis == 'DARING':
            self.txt_nama_toko_d.setText(self.toko_data.get('nama_toko', ''))
            self.cmb_platform.setCurrentText(self.toko_data.get('platform_online', ''))
            self.txt_link.setText(self.toko_data.get('link_produk', ''))
            self.txt_alamat_d.setPlainText(self.toko_data.get('alamat', ''))
            self.txt_kota_d.setText(self.toko_data.get('kota', ''))
            self.txt_surveyor_d.setText(self.toko_data.get('nama_surveyor', ''))
            if self.toko_data.get('tanggal_survey'):
                self.date_survey_d.setDate(QDate.fromString(self.toko_data['tanggal_survey'], 'yyyy-MM-dd'))
                
        elif jenis == 'KONTRAK':
            self.txt_nama_penyedia.setText(self.toko_data.get('nama_toko', ''))
            self.txt_nomor_kontrak.setText(self.toko_data.get('nomor_kontrak_referensi', ''))
            idx = self.cmb_tahun_kontrak.findData(self.toko_data.get('tahun_kontrak_referensi'))
            if idx >= 0:
                self.cmb_tahun_kontrak.setCurrentIndex(idx)
            self.txt_instansi.setText(self.toko_data.get('instansi_referensi', ''))
            self.txt_alamat_k.setPlainText(self.toko_data.get('alamat', ''))
            self.txt_kota_k.setText(self.toko_data.get('kota', ''))
            self.txt_telepon_k.setText(self.toko_data.get('telepon', ''))
    
    def get_data(self) -> dict:
        """Get form data"""
        jenis = self.cmb_jenis.currentData()
        
        data = {
            'jenis_survey': jenis,
            'keterangan': self.txt_keterangan.toPlainText().strip()
        }
        
        if jenis == 'LURING':
            data.update({
                'nama_toko': self.txt_nama_toko.text().strip(),
                'alamat': self.txt_alamat.toPlainText().strip(),
                'kota': self.txt_kota.text().strip(),
                'telepon': self.txt_telepon.text().strip(),
                'email': self.txt_email.text().strip(),
                'tanggal_survey': self.date_survey.date().toString('yyyy-MM-dd'),
                'nama_surveyor': self.txt_surveyor.text().strip(),
                'nip_surveyor': self.txt_nip_surveyor.text().strip(),
            })
            
        elif jenis == 'DARING':
            data.update({
                'nama_toko': self.txt_nama_toko_d.text().strip(),
                'platform_online': self.cmb_platform.currentText(),
                'link_produk': self.txt_link.text().strip(),
                'alamat': self.txt_alamat_d.toPlainText().strip(),
                'kota': self.txt_kota_d.text().strip(),
                'tanggal_survey': self.date_survey_d.date().toString('yyyy-MM-dd'),
                'nama_surveyor': self.txt_surveyor_d.text().strip(),
            })
            
        elif jenis == 'KONTRAK':
            data.update({
                'nama_toko': self.txt_nama_penyedia.text().strip(),
                'nomor_kontrak_referensi': self.txt_nomor_kontrak.text().strip(),
                'tahun_kontrak_referensi': self.cmb_tahun_kontrak.currentData(),
                'instansi_referensi': self.txt_instansi.text().strip(),
                'alamat': self.txt_alamat_k.toPlainText().strip(),
                'kota': self.txt_kota_k.text().strip(),
                'telepon': self.txt_telepon_k.text().strip(),
            })
        
        return data
    
    def save(self):
        """Validate and save"""
        data = self.get_data()
        
        if not data.get('nama_toko'):
            QMessageBox.warning(self, "Validasi", "Nama toko/penyedia wajib diisi!")
            return
        
        try:
            if self.toko_data:
                # Update
                self.db.update_survey_toko(self.toko_data['id'], data)
            else:
                # Check count
                existing = self.db.get_survey_toko(self.paket_id)
                if len(existing) >= 3:
                    QMessageBox.warning(self, "Validasi", "Maksimal 3 toko survey per paket!")
                    return
                
                # Insert
                self.db.add_survey_toko(self.paket_id, data)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {str(e)}")


class SurveyTokoManager(QDialog):
    """Main dialog untuk mengelola semua survey toko dalam paket"""
    
    data_changed = Signal()
    
    def __init__(self, paket_id: int, parent=None):
        super().__init__(parent)
        self.paket_id = paket_id
        self.db = get_db_manager()
        
        # Get paket info
        self.paket = self.db.get_paket(paket_id)
        
        self.setWindowTitle(f"Sumber Harga Survey - {self.paket.get('nama', '')}")
        self.setMinimumSize(900, 500)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("🏪 Data Toko / Sumber Harga Survey")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Add button
        btn_add = QPushButton("➕ Tambah Toko")
        btn_add.setObjectName("btnPrimary")
        btn_add.clicked.connect(self.add_toko)
        header.addWidget(btn_add)
        
        layout.addLayout(header)
        
        # Info
        info_label = QLabel(
            "💡 Masukkan data 3 toko/sumber harga untuk keperluan survey. "
            "Data ini akan digunakan pada template Survey Harga dan HPS."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 5px; background: #f8f9fa; border-radius: 4px;")
        layout.addWidget(info_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "No", "Jenis", "Nama Toko/Penyedia", "Alamat", "Kota", 
            "Platform/Kontrak", "Tanggal", "Aksi"
        ])
        
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 80)
        
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.edit_toko)
        
        layout.addWidget(self.table)
        
        # Summary cards
        cards_layout = QHBoxLayout()
        
        for i in range(1, 4):
            card = QGroupBox(f"Toko {i}")
            card_layout = QVBoxLayout()
            
            lbl_nama = QLabel("-")
            lbl_nama.setObjectName(f"lbl_toko{i}_nama")
            lbl_nama.setStyleSheet("font-weight: bold;")
            card_layout.addWidget(lbl_nama)
            
            lbl_jenis = QLabel("")
            lbl_jenis.setObjectName(f"lbl_toko{i}_jenis")
            lbl_jenis.setStyleSheet("color: #666; font-size: 11px;")
            card_layout.addWidget(lbl_jenis)
            
            lbl_alamat = QLabel("")
            lbl_alamat.setObjectName(f"lbl_toko{i}_alamat")
            lbl_alamat.setStyleSheet("color: #666; font-size: 11px;")
            lbl_alamat.setWordWrap(True)
            card_layout.addWidget(lbl_alamat)
            
            card.setLayout(card_layout)
            cards_layout.addWidget(card)
        
        layout.addLayout(cards_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        
        # Style
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton#btnPrimary {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton#btnPrimary:hover {
                background-color: #2980b9;
            }
        """)
    
    def load_data(self):
        """Load toko data"""
        tokos = self.db.get_survey_toko(self.paket_id)
        
        self.table.setRowCount(len(tokos))
        
        for row, toko in enumerate(tokos):
            # No
            self.table.setItem(row, 0, QTableWidgetItem(str(toko['nomor_urut'])))
            
            # Jenis
            jenis = toko.get('jenis_survey', 'LURING')
            jenis_display = {'LURING': '🏪 Luring', 'DARING': '🌐 Daring', 'KONTRAK': '📄 Kontrak'}
            self.table.setItem(row, 1, QTableWidgetItem(jenis_display.get(jenis, jenis)))
            
            # Nama
            self.table.setItem(row, 2, QTableWidgetItem(toko.get('nama_toko', '')))
            
            # Alamat
            self.table.setItem(row, 3, QTableWidgetItem(toko.get('alamat', '')))
            
            # Kota
            self.table.setItem(row, 4, QTableWidgetItem(toko.get('kota', '')))
            
            # Platform/Kontrak
            if jenis == 'DARING':
                platform = toko.get('platform_online', '')
            elif jenis == 'KONTRAK':
                platform = f"SPK {toko.get('tahun_kontrak_referensi', '')}"
            else:
                platform = toko.get('telepon', '')
            self.table.setItem(row, 5, QTableWidgetItem(platform))
            
            # Tanggal
            self.table.setItem(row, 6, QTableWidgetItem(toko.get('tanggal_survey', '')))
            
            # Aksi
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(2)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(30, 25)
            btn_edit.setToolTip("Edit")
            btn_edit.clicked.connect(lambda checked, id=toko['id']: self.edit_toko_by_id(id))
            btn_layout.addWidget(btn_edit)
            
            btn_delete = QPushButton("🗑️")
            btn_delete.setFixedSize(30, 25)
            btn_delete.setToolTip("Hapus")
            btn_delete.clicked.connect(lambda checked, id=toko['id']: self.delete_toko(id))
            btn_layout.addWidget(btn_delete)
            
            self.table.setCellWidget(row, 7, btn_widget)
        
        # Update summary cards
        for i in range(1, 4):
            lbl_nama = self.findChild(QLabel, f"lbl_toko{i}_nama")
            lbl_jenis = self.findChild(QLabel, f"lbl_toko{i}_jenis")
            lbl_alamat = self.findChild(QLabel, f"lbl_toko{i}_alamat")
            
            if i <= len(tokos):
                toko = tokos[i-1]
                lbl_nama.setText(toko.get('nama_toko', '-'))
                jenis = toko.get('jenis_survey', 'LURING')
                lbl_jenis.setText(JENIS_SURVEY.get(jenis, jenis))
                alamat = toko.get('alamat', '')
                kota = toko.get('kota', '')
                lbl_alamat.setText(f"{alamat}, {kota}" if alamat else kota)
            else:
                lbl_nama.setText("(Belum diisi)")
                lbl_jenis.setText("")
                lbl_alamat.setText("")
    
    def add_toko(self):
        """Add new toko"""
        # Check count
        existing = self.db.get_survey_toko(self.paket_id)
        if len(existing) >= 3:
            QMessageBox.warning(self, "Peringatan", "Maksimal 3 toko survey per paket!")
            return
        
        dialog = SurveyTokoDialog(self.paket_id, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()
            self.data_changed.emit()
    
    def edit_toko(self):
        """Edit selected toko"""
        row = self.table.currentRow()
        if row >= 0:
            tokos = self.db.get_survey_toko(self.paket_id)
            if row < len(tokos):
                self.edit_toko_by_id(tokos[row]['id'])
    
    def edit_toko_by_id(self, toko_id: int):
        """Edit toko by ID"""
        toko_data = self.db.get_survey_toko_by_id(toko_id)
        if toko_data:
            dialog = SurveyTokoDialog(self.paket_id, toko_data, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.load_data()
                self.data_changed.emit()
    
    def delete_toko(self, toko_id: int):
        """Delete toko"""
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            "Hapus data toko ini?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.delete_survey_toko(toko_id)
            self.db.reorder_survey_toko(self.paket_id)
            self.load_data()
            self.data_changed.emit()


def show_survey_toko_manager(paket_id: int, parent=None) -> SurveyTokoManager:
    """Show survey toko manager dialog"""
    dialog = SurveyTokoManager(paket_id, parent)
    dialog.exec()
    return dialog
