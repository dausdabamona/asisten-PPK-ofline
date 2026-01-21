"""
PPK DOCUMENT FACTORY v4.0 - Paket Pejabat Manager
==================================================
Penetapan Pejabat per Paket:
- PPK
- Pejabat Pengadaan
- PPSPM
- Bendahara
- Tim PPHP (Ketua + Anggota)
"""

from datetime import datetime
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QWidget, QPushButton, QLabel, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QMessageBox, QCheckBox, QFrame, QListWidget, QListWidgetItem,
    QAbstractItemView, QDateEdit, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor

from app.core.database_v4 import get_db_manager_v4, PERAN_PEJABAT


# ============================================================================
# PEJABAT SELECTOR WIDGET
# ============================================================================

class PejabatSelector(QWidget):
    """Widget for selecting single pejabat"""
    
    changed = Signal()
    
    def __init__(self, peran: str, label: str, parent=None):
        super().__init__(parent)
        self.peran = peran
        self.db = get_db_manager_v4()
        self.selected_id = None
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        lbl = QLabel(f"{label}:")
        lbl.setMinimumWidth(150)
        layout.addWidget(lbl)
        
        # Combo
        self.cmb_pegawai = QComboBox()
        self.cmb_pegawai.setMinimumWidth(300)
        self.cmb_pegawai.currentIndexChanged.connect(self._on_changed)
        layout.addWidget(self.cmb_pegawai)
        
        # Info
        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.lbl_info)
        
        layout.addStretch()
        
        self.load_pegawai()
    
    def load_pegawai(self):
        """Load pegawai options"""
        self.cmb_pegawai.clear()
        self.cmb_pegawai.addItem("-- Pilih Pegawai --", None)
        
        # Map role to filter
        role_map = {
            'PPK': 'ppk',
            'PEJABAT_PENGADAAN': 'pejabat_pengadaan',
            'PPSPM': 'ppspm',
            'BENDAHARA': 'bendahara',
            'KETUA_PPHP': 'pemeriksa',
        }
        
        role_filter = role_map.get(self.peran)
        
        if role_filter:
            pegawai_list = self.db.get_pegawai_by_role(role_filter)
        else:
            pegawai_list = self.db.get_all_pegawai(active_only=True)
        
        for p in pegawai_list:
            nama = p.get('nama', '')
            if p.get('gelar_depan'):
                nama = f"{p['gelar_depan']} {nama}"
            if p.get('gelar_belakang'):
                nama = f"{nama}, {p['gelar_belakang']}"
            
            display = f"{nama}"
            if p.get('jabatan'):
                display += f" - {p['jabatan']}"
            
            self.cmb_pegawai.addItem(display, p['id'])
    
    def _on_changed(self):
        """Handle selection change"""
        pegawai_id = self.cmb_pegawai.currentData()
        self.selected_id = pegawai_id
        
        if pegawai_id:
            pegawai = self.db.get_pegawai(pegawai_id)
            if pegawai:
                info_parts = []
                if pegawai.get('nip'):
                    info_parts.append(f"NIP: {pegawai['nip']}")
                if pegawai.get('golongan'):
                    info_parts.append(f"Gol: {pegawai['golongan']}")
                self.lbl_info.setText(" | ".join(info_parts))
            else:
                self.lbl_info.setText("")
        else:
            self.lbl_info.setText("")
        
        self.changed.emit()
    
    def set_value(self, pegawai_id: int):
        """Set selected pegawai"""
        idx = self.cmb_pegawai.findData(pegawai_id)
        if idx >= 0:
            self.cmb_pegawai.setCurrentIndex(idx)
    
    def get_value(self) -> Optional[int]:
        """Get selected pegawai ID"""
        return self.cmb_pegawai.currentData()


# ============================================================================
# TIM PPHP SELECTOR (Multi-select)
# ============================================================================

class TimPPHPSelector(QWidget):
    """Widget for selecting Tim PPHP (Ketua + Anggota)"""
    
    changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db_manager_v4()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QHBoxLayout()
        lbl = QLabel("👥 Tim Pejabat Pemeriksa Hasil Pekerjaan (PPHP):")
        lbl.setStyleSheet("font-weight: bold;")
        header.addWidget(lbl)
        header.addStretch()
        layout.addLayout(header)
        
        # Ketua
        ketua_layout = QHBoxLayout()
        ketua_layout.addWidget(QLabel("Ketua:"))
        
        self.cmb_ketua = QComboBox()
        self.cmb_ketua.setMinimumWidth(350)
        self.cmb_ketua.currentIndexChanged.connect(self._on_changed)
        ketua_layout.addWidget(self.cmb_ketua)
        ketua_layout.addStretch()
        layout.addLayout(ketua_layout)
        
        # Anggota
        anggota_layout = QHBoxLayout()
        
        anggota_left = QVBoxLayout()
        anggota_left.addWidget(QLabel("Tersedia:"))
        self.list_available = QListWidget()
        self.list_available.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_available.setMaximumHeight(150)
        anggota_left.addWidget(self.list_available)
        anggota_layout.addLayout(anggota_left)
        
        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.addStretch()
        btn_add = QPushButton("→")
        btn_add.setMaximumWidth(40)
        btn_add.clicked.connect(self.add_anggota)
        btn_layout.addWidget(btn_add)
        btn_remove = QPushButton("←")
        btn_remove.setMaximumWidth(40)
        btn_remove.clicked.connect(self.remove_anggota)
        btn_layout.addWidget(btn_remove)
        btn_layout.addStretch()
        anggota_layout.addLayout(btn_layout)
        
        anggota_right = QVBoxLayout()
        anggota_right.addWidget(QLabel("Anggota Tim:"))
        self.list_selected = QListWidget()
        self.list_selected.setMaximumHeight(150)
        anggota_right.addWidget(self.list_selected)
        anggota_layout.addLayout(anggota_right)
        
        layout.addLayout(anggota_layout)
        
        self.load_pegawai()
    
    def load_pegawai(self):
        """Load pegawai options"""
        self.cmb_ketua.clear()
        self.cmb_ketua.addItem("-- Pilih Ketua --", None)
        
        self.list_available.clear()
        
        # Get pemeriksa
        pegawai_list = self.db.get_pegawai_by_role('pemeriksa')
        
        for p in pegawai_list:
            nama = self._format_nama(p)
            
            # Add to ketua combo
            self.cmb_ketua.addItem(nama, p['id'])
            
            # Add to available list
            item = QListWidgetItem(nama)
            item.setData(Qt.UserRole, p['id'])
            self.list_available.addItem(item)
    
    def _format_nama(self, p: Dict) -> str:
        """Format pegawai name"""
        nama = p.get('nama', '')
        if p.get('gelar_depan'):
            nama = f"{p['gelar_depan']} {nama}"
        if p.get('gelar_belakang'):
            nama = f"{nama}, {p['gelar_belakang']}"
        return nama
    
    def _on_changed(self):
        self.changed.emit()
    
    def add_anggota(self):
        """Add selected to anggota"""
        for item in self.list_available.selectedItems():
            # Check if already in selected
            already = False
            for i in range(self.list_selected.count()):
                if self.list_selected.item(i).data(Qt.UserRole) == item.data(Qt.UserRole):
                    already = True
                    break
            
            if not already:
                new_item = QListWidgetItem(item.text())
                new_item.setData(Qt.UserRole, item.data(Qt.UserRole))
                self.list_selected.addItem(new_item)
        
        self.changed.emit()
    
    def remove_anggota(self):
        """Remove selected from anggota"""
        for item in self.list_selected.selectedItems():
            self.list_selected.takeItem(self.list_selected.row(item))
        
        self.changed.emit()
    
    def set_ketua(self, pegawai_id: int):
        """Set ketua"""
        idx = self.cmb_ketua.findData(pegawai_id)
        if idx >= 0:
            self.cmb_ketua.setCurrentIndex(idx)
    
    def get_ketua(self) -> Optional[int]:
        """Get ketua ID"""
        return self.cmb_ketua.currentData()
    
    def set_anggota(self, pegawai_ids: List[int]):
        """Set anggota list"""
        self.list_selected.clear()
        
        for pid in pegawai_ids:
            pegawai = self.db.get_pegawai(pid)
            if pegawai:
                item = QListWidgetItem(self._format_nama(pegawai))
                item.setData(Qt.UserRole, pid)
                self.list_selected.addItem(item)
    
    def get_anggota(self) -> List[int]:
        """Get list of anggota IDs"""
        result = []
        for i in range(self.list_selected.count()):
            result.append(self.list_selected.item(i).data(Qt.UserRole))
        return result


# ============================================================================
# PAKET PEJABAT MANAGER (Main Dialog)
# ============================================================================

class PaketPejabatManager(QDialog):
    """Dialog for managing pejabat assignment per paket"""
    
    pejabat_changed = Signal()
    
    def __init__(self, paket_id: int, parent=None):
        super().__init__(parent)
        self.paket_id = paket_id
        self.db = get_db_manager_v4()
        
        # Get paket info
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM paket WHERE id = ?", (paket_id,))
            row = cursor.fetchone()
            self.paket = dict(row) if row else {}
        
        self.setWindowTitle(f"Penetapan Pejabat - {self.paket.get('nama', '')}")
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"📋 Penetapan Pejabat: {self.paket.get('nama', '')}")
        header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px; background: #f8f9fa;")
        layout.addWidget(header)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Info
        info = QLabel(
            "💡 Pilih pejabat yang akan ditetapkan untuk paket ini.\n"
            "Hanya pegawai dengan peran yang sesuai yang akan tampil di daftar pilihan."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; padding: 8px; background: #fff3cd; border-radius: 4px;")
        content_layout.addWidget(info)
        
        # Pejabat Utama
        utama_group = QGroupBox("Pejabat Utama")
        utama_layout = QVBoxLayout()
        
        self.sel_ppk = PejabatSelector('PPK', 'Pejabat Pembuat Komitmen (PPK)')
        self.sel_ppk.changed.connect(self._on_changed)
        utama_layout.addWidget(self.sel_ppk)
        
        self.sel_pp = PejabatSelector('PEJABAT_PENGADAAN', 'Pejabat Pengadaan')
        self.sel_pp.changed.connect(self._on_changed)
        utama_layout.addWidget(self.sel_pp)
        
        self.sel_ppspm = PejabatSelector('PPSPM', 'Pejabat Penandatangan SPM (PPSPM)')
        self.sel_ppspm.changed.connect(self._on_changed)
        utama_layout.addWidget(self.sel_ppspm)
        
        self.sel_bendahara = PejabatSelector('BENDAHARA', 'Bendahara Pengeluaran')
        self.sel_bendahara.changed.connect(self._on_changed)
        utama_layout.addWidget(self.sel_bendahara)
        
        utama_group.setLayout(utama_layout)
        content_layout.addWidget(utama_group)
        
        # Tim PPHP
        pphp_group = QGroupBox("Tim Pemeriksa Hasil Pekerjaan")
        pphp_layout = QVBoxLayout()
        
        self.tim_pphp = TimPPHPSelector()
        self.tim_pphp.changed.connect(self._on_changed)
        pphp_layout.addWidget(self.tim_pphp)
        
        pphp_group.setLayout(pphp_layout)
        content_layout.addWidget(pphp_group)
        
        # SK Info
        sk_group = QGroupBox("Informasi Surat Keputusan (Opsional)")
        sk_layout = QFormLayout()
        
        self.date_sk = QDateEdit()
        self.date_sk.setCalendarPopup(True)
        self.date_sk.setDate(QDate.currentDate())
        sk_layout.addRow("Tanggal SK:", self.date_sk)
        
        self.txt_nomor_sk = QLineEdit()
        self.txt_nomor_sk.setPlaceholderText("Nomor SK penetapan pejabat...")
        sk_layout.addRow("Nomor SK:", self.txt_nomor_sk)
        
        sk_group.setLayout(sk_layout)
        content_layout.addWidget(sk_group)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_save = QPushButton("💾 Simpan")
        btn_save.setObjectName("btnSuccess")
        btn_save.clicked.connect(self.save)
        btn_layout.addWidget(btn_save)
        
        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        
        # Style
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
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
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#btnSuccess:hover {
                background-color: #219a52;
            }
        """)
    
    def _on_changed(self):
        """Mark as changed"""
        pass
    
    def load_data(self):
        """Load existing pejabat assignments"""
        pejabat_list = self.db.get_paket_pejabat(self.paket_id)
        
        for pp in pejabat_list:
            peran = pp['peran']
            pegawai_id = pp['pegawai_id']
            
            if peran == 'PPK':
                self.sel_ppk.set_value(pegawai_id)
            elif peran == 'PEJABAT_PENGADAAN':
                self.sel_pp.set_value(pegawai_id)
            elif peran == 'PPSPM':
                self.sel_ppspm.set_value(pegawai_id)
            elif peran == 'BENDAHARA':
                self.sel_bendahara.set_value(pegawai_id)
            elif peran == 'KETUA_PPHP':
                self.tim_pphp.set_ketua(pegawai_id)
            elif peran == 'ANGGOTA_PPHP':
                # Collect anggota
                pass
        
        # Load anggota PPHP
        anggota_list = self.db.get_paket_pejabat_by_role(self.paket_id, 'ANGGOTA_PPHP')
        self.tim_pphp.set_anggota([a['pegawai_id'] for a in anggota_list])
    
    def save(self):
        """Save pejabat assignments"""
        try:
            tanggal = self.date_sk.date().toPython()
            nomor_sk = self.txt_nomor_sk.text().strip() or None
            
            # Save each role
            roles = [
                ('PPK', self.sel_ppk.get_value()),
                ('PEJABAT_PENGADAAN', self.sel_pp.get_value()),
                ('PPSPM', self.sel_ppspm.get_value()),
                ('BENDAHARA', self.sel_bendahara.get_value()),
                ('KETUA_PPHP', self.tim_pphp.get_ketua()),
            ]
            
            for peran, pegawai_id in roles:
                if pegawai_id:
                    self.db.set_paket_pejabat(
                        self.paket_id, peran, pegawai_id,
                        tanggal_penetapan=str(tanggal),
                        nomor_sk=nomor_sk
                    )
                else:
                    self.db.remove_paket_pejabat(self.paket_id, peran)
            
            # Save anggota PPHP
            self.db.remove_paket_pejabat(self.paket_id, 'ANGGOTA_PPHP')
            for i, pegawai_id in enumerate(self.tim_pphp.get_anggota(), 1):
                self.db.set_paket_pejabat(
                    self.paket_id, 'ANGGOTA_PPHP', pegawai_id,
                    urutan=i,
                    tanggal_penetapan=str(tanggal),
                    nomor_sk=nomor_sk
                )
            
            # Also update legacy paket fields for backward compatibility
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE paket SET
                        ppk_id = ?,
                        ppspm_id = ?,
                        bendahara_id = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    self.sel_ppk.get_value(),
                    self.sel_ppspm.get_value(),
                    self.sel_bendahara.get_value(),
                    self.paket_id
                ))
                conn.commit()
            
            QMessageBox.information(self, "Sukses", "Penetapan pejabat berhasil disimpan!")
            self.pejabat_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan:\n{str(e)}")


# ============================================================================
# HELPER FUNCTION
# ============================================================================

def show_paket_pejabat_manager(paket_id: int, parent=None) -> PaketPejabatManager:
    """Show paket pejabat manager dialog"""
    dialog = PaketPejabatManager(paket_id, parent)
    dialog.exec()
    return dialog
