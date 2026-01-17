"""
PPK DOCUMENT FACTORY v3.0 - Penyedia Manager
=============================================
Master Data Penyedia / Vendor / Rekanan
"""

from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QWidget, QPushButton, QLabel, QLineEdit, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QMessageBox, QAbstractItemView, QMenu, QSplitter, QTabWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QColor

from app.core.database import get_db_manager


# ============================================================================
# PENYEDIA DIALOG (Add/Edit)
# ============================================================================

class PenyediaDialog(QDialog):
    """Dialog for adding/editing penyedia"""

    def __init__(self, penyedia_data: dict = None, parent=None):
        super().__init__(parent)
        self.penyedia_data = penyedia_data
        self.db = get_db_manager()

        self.setWindowTitle("Tambah Penyedia" if not penyedia_data else "Edit Penyedia")
        self.setMinimumWidth(550)

        self.setup_ui()

        if penyedia_data:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Tabs
        tabs = QTabWidget()

        # Tab 1: Data Perusahaan
        tab_perusahaan = QWidget()
        form1 = QFormLayout(tab_perusahaan)

        self.txt_nama = QLineEdit()
        self.txt_nama.setPlaceholderText("PT/CV Nama Perusahaan...")
        form1.addRow("Nama Perusahaan:", self.txt_nama)

        self.txt_alamat = QLineEdit()
        self.txt_alamat.setPlaceholderText("Jl. Nama Jalan No. XX...")
        form1.addRow("Alamat:", self.txt_alamat)

        self.txt_kota = QLineEdit()
        self.txt_kota.setPlaceholderText("Kota/Kabupaten...")
        form1.addRow("Kota:", self.txt_kota)

        self.txt_telepon = QLineEdit()
        self.txt_telepon.setPlaceholderText("08xx-xxxx-xxxx")
        form1.addRow("Telepon:", self.txt_telepon)

        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("email@perusahaan.com")
        form1.addRow("Email:", self.txt_email)

        self.txt_npwp = QLineEdit()
        self.txt_npwp.setPlaceholderText("XX.XXX.XXX.X-XXX.XXX")
        form1.addRow("NPWP:", self.txt_npwp)

        self.chk_pkp = QCheckBox("Pengusaha Kena Pajak (PKP)")
        self.chk_pkp.setChecked(True)
        self.chk_pkp.setToolTip("Centang jika penyedia adalah PKP (dikenakan PPN 11%)")
        form1.addRow("Status Pajak:", self.chk_pkp)

        tabs.addTab(tab_perusahaan, "Data Perusahaan")

        # Tab 2: Data Direktur
        tab_direktur = QWidget()
        form2 = QFormLayout(tab_direktur)

        self.txt_nama_direktur = QLineEdit()
        self.txt_nama_direktur.setPlaceholderText("Nama lengkap direktur...")
        form2.addRow("Nama Direktur:", self.txt_nama_direktur)

        self.txt_jabatan_direktur = QLineEdit()
        self.txt_jabatan_direktur.setText("Direktur")
        self.txt_jabatan_direktur.setPlaceholderText("Direktur/Direktur Utama/Owner...")
        form2.addRow("Jabatan:", self.txt_jabatan_direktur)

        tabs.addTab(tab_direktur, "Data Direktur")

        # Tab 3: Data Bank
        tab_bank = QWidget()
        form3 = QFormLayout(tab_bank)

        self.txt_no_rekening = QLineEdit()
        self.txt_no_rekening.setPlaceholderText("Nomor rekening bank...")
        form3.addRow("No. Rekening:", self.txt_no_rekening)

        self.txt_nama_bank = QLineEdit()
        self.txt_nama_bank.setPlaceholderText("Bank BRI/BNI/Mandiri/dll")
        form3.addRow("Nama Bank:", self.txt_nama_bank)

        self.txt_nama_rekening = QLineEdit()
        self.txt_nama_rekening.setPlaceholderText("Nama sesuai rekening...")
        form3.addRow("Nama Pemilik Rek:", self.txt_nama_rekening)

        tabs.addTab(tab_bank, "Data Bank")

        layout.addWidget(tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_save = QPushButton("Simpan")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        btn_save.clicked.connect(self.save)
        btn_layout.addWidget(btn_save)

        btn_cancel = QPushButton("Batal")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    def load_data(self):
        """Load existing penyedia data"""
        if not self.penyedia_data:
            return

        self.txt_nama.setText(self.penyedia_data.get('nama', '') or '')
        self.txt_alamat.setText(self.penyedia_data.get('alamat', '') or '')
        self.txt_kota.setText(self.penyedia_data.get('kota', '') or '')
        self.txt_telepon.setText(self.penyedia_data.get('telepon', '') or '')
        self.txt_email.setText(self.penyedia_data.get('email', '') or '')
        self.txt_npwp.setText(self.penyedia_data.get('npwp', '') or '')
        self.chk_pkp.setChecked(bool(self.penyedia_data.get('is_pkp', 1)))
        self.txt_nama_direktur.setText(self.penyedia_data.get('nama_direktur', '') or '')
        self.txt_jabatan_direktur.setText(self.penyedia_data.get('jabatan_direktur', 'Direktur') or 'Direktur')
        self.txt_no_rekening.setText(self.penyedia_data.get('no_rekening', '') or '')
        self.txt_nama_bank.setText(self.penyedia_data.get('nama_bank', '') or '')
        self.txt_nama_rekening.setText(self.penyedia_data.get('nama_rekening', '') or '')

    def get_data(self) -> dict:
        """Get form data"""
        return {
            'nama': self.txt_nama.text().strip(),
            'alamat': self.txt_alamat.text().strip() or None,
            'kota': self.txt_kota.text().strip() or None,
            'telepon': self.txt_telepon.text().strip() or None,
            'email': self.txt_email.text().strip() or None,
            'npwp': self.txt_npwp.text().strip() or None,
            'is_pkp': 1 if self.chk_pkp.isChecked() else 0,
            'nama_direktur': self.txt_nama_direktur.text().strip() or None,
            'jabatan_direktur': self.txt_jabatan_direktur.text().strip() or 'Direktur',
            'no_rekening': self.txt_no_rekening.text().strip() or None,
            'nama_bank': self.txt_nama_bank.text().strip() or None,
            'nama_rekening': self.txt_nama_rekening.text().strip() or None,
        }

    def save(self):
        """Validate and save"""
        data = self.get_data()

        if not data['nama']:
            QMessageBox.warning(self, "Validasi", "Nama perusahaan wajib diisi!")
            self.txt_nama.setFocus()
            return

        try:
            if self.penyedia_data:
                data['id'] = self.penyedia_data['id']

            self.db.save_penyedia(data)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan:\n{str(e)}")


# ============================================================================
# PENYEDIA MANAGER (Main Window)
# ============================================================================

class PenyediaManager(QDialog):
    """Main dialog for managing penyedia"""

    penyedia_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db_manager()

        self.setWindowTitle("Master Data Penyedia")
        self.setMinimumSize(900, 500)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()

        title = QLabel("Master Data Penyedia / Rekanan")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        header.addWidget(title)

        header.addStretch()

        # Search
        header.addWidget(QLabel("Cari:"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Nama perusahaan...")
        self.txt_search.setMinimumWidth(200)
        self.txt_search.textChanged.connect(self.filter_data)
        header.addWidget(self.txt_search)

        layout.addLayout(header)

        # Toolbar
        toolbar = QHBoxLayout()

        btn_add = QPushButton("+ Tambah Penyedia")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_add.clicked.connect(self.add_penyedia)
        toolbar.addWidget(btn_add)

        toolbar.addStretch()

        # Show inactive
        self.chk_show_inactive = QCheckBox("Tampilkan non-aktif")
        self.chk_show_inactive.stateChanged.connect(self.load_data)
        toolbar.addWidget(self.chk_show_inactive)

        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Nama Perusahaan", "Direktur", "Alamat", "Kota",
            "NPWP", "No. Rekening", "Bank", "PKP", "ID"
        ])

        # Hide ID column
        self.table.setColumnHidden(8, True)

        # Column widths
        self.table.setColumnWidth(0, 200)   # Nama
        self.table.setColumnWidth(1, 150)   # Direktur
        self.table.setColumnWidth(2, 200)   # Alamat
        self.table.setColumnWidth(3, 100)   # Kota
        self.table.setColumnWidth(4, 150)   # NPWP
        self.table.setColumnWidth(5, 120)   # Rekening
        self.table.setColumnWidth(6, 100)   # Bank
        self.table.setColumnWidth(7, 50)    # PKP

        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.edit_penyedia)

        # Context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)

        # Summary
        summary = QHBoxLayout()
        self.lbl_total = QLabel("Total: 0 penyedia")
        self.lbl_total.setStyleSheet("font-weight: bold;")
        summary.addWidget(self.lbl_total)

        summary.addStretch()

        btn_close = QPushButton("Tutup")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_close.clicked.connect(self.accept)
        summary.addWidget(btn_close)

        layout.addLayout(summary)

    def load_data(self):
        """Load penyedia data into table"""
        show_inactive = self.chk_show_inactive.isChecked()

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if show_inactive:
                cursor.execute("SELECT * FROM penyedia ORDER BY nama")
            else:
                cursor.execute("SELECT * FROM penyedia WHERE is_active = 1 ORDER BY nama")

            self.all_data = [dict(row) for row in cursor.fetchall()]

        self.filter_data()

    def filter_data(self):
        """Filter displayed data based on search"""
        search = self.txt_search.text().lower()

        filtered = []
        for p in self.all_data:
            if search:
                searchable = f"{p.get('nama', '')} {p.get('nama_direktur', '')} {p.get('kota', '')}".lower()
                if search not in searchable:
                    continue
            filtered.append(p)

        self.display_data(filtered)

    def display_data(self, penyedia_list: List[Dict]):
        """Display data in table"""
        self.table.setRowCount(len(penyedia_list))

        for row, p in enumerate(penyedia_list):
            # Nama
            nama_item = QTableWidgetItem(p.get('nama', '') or '')
            if not p.get('is_active', 1):
                nama_item.setForeground(QColor('#999'))
            self.table.setItem(row, 0, nama_item)

            # Direktur
            self.table.setItem(row, 1, QTableWidgetItem(p.get('nama_direktur', '') or '-'))

            # Alamat
            self.table.setItem(row, 2, QTableWidgetItem(p.get('alamat', '') or '-'))

            # Kota
            self.table.setItem(row, 3, QTableWidgetItem(p.get('kota', '') or '-'))

            # NPWP
            self.table.setItem(row, 4, QTableWidgetItem(p.get('npwp', '') or '-'))

            # No. Rekening
            self.table.setItem(row, 5, QTableWidgetItem(p.get('no_rekening', '') or '-'))

            # Bank
            self.table.setItem(row, 6, QTableWidgetItem(p.get('nama_bank', '') or '-'))

            # PKP
            pkp_item = QTableWidgetItem("Ya" if p.get('is_pkp') else "Tidak")
            pkp_item.setTextAlignment(Qt.AlignCenter)
            if p.get('is_pkp'):
                pkp_item.setForeground(QColor('#27ae60'))
            else:
                pkp_item.setForeground(QColor('#e74c3c'))
            self.table.setItem(row, 7, pkp_item)

            # ID (hidden)
            self.table.setItem(row, 8, QTableWidgetItem(str(p['id'])))

        self.lbl_total.setText(f"Total: {len(penyedia_list)} penyedia")

    def show_context_menu(self, pos):
        """Show context menu"""
        row = self.table.rowAt(pos.y())
        if row < 0:
            return

        menu = QMenu(self)

        action_edit = QAction("Edit", self)
        action_edit.triggered.connect(self.edit_penyedia)
        menu.addAction(action_edit)

        menu.addSeparator()

        # Check if active
        penyedia_id = self.get_selected_id()
        if penyedia_id:
            penyedia = self.db.get_penyedia(penyedia_id)
            if penyedia and penyedia.get('is_active', 1):
                action_delete = QAction("Hapus", self)
                action_delete.triggered.connect(self.delete_penyedia)
                menu.addAction(action_delete)
            else:
                action_restore = QAction("Aktifkan Kembali", self)
                action_restore.triggered.connect(self.restore_penyedia)
                menu.addAction(action_restore)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def get_selected_id(self) -> Optional[int]:
        """Get selected penyedia ID"""
        row = self.table.currentRow()
        if row < 0:
            return None
        id_item = self.table.item(row, 8)
        return int(id_item.text()) if id_item else None

    def add_penyedia(self):
        """Add new penyedia"""
        dialog = PenyediaDialog(parent=self)
        if dialog.exec():
            self.load_data()
            self.penyedia_changed.emit()

    def edit_penyedia(self):
        """Edit selected penyedia"""
        penyedia_id = self.get_selected_id()
        if not penyedia_id:
            QMessageBox.warning(self, "Peringatan", "Pilih penyedia terlebih dahulu!")
            return

        penyedia = self.db.get_penyedia(penyedia_id)
        if not penyedia:
            return

        dialog = PenyediaDialog(penyedia, parent=self)
        if dialog.exec():
            self.load_data()
            self.penyedia_changed.emit()

    def delete_penyedia(self):
        """Delete (deactivate) selected penyedia"""
        penyedia_id = self.get_selected_id()
        if not penyedia_id:
            return

        reply = QMessageBox.question(
            self, "Konfirmasi",
            "Hapus penyedia ini?\n\n"
            "Penyedia yang dihapus tidak akan muncul di daftar pilihan.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.db.delete_penyedia(penyedia_id)
            self.load_data()
            self.penyedia_changed.emit()

    def restore_penyedia(self):
        """Restore deleted penyedia"""
        penyedia_id = self.get_selected_id()
        if not penyedia_id:
            return

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE penyedia SET is_active = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (penyedia_id,))
            conn.commit()

        self.load_data()
        self.penyedia_changed.emit()
