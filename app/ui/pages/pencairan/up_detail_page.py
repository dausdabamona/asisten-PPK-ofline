"""
UP Detail Page - Halaman detail transaksi UP dengan fase stepper
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,
    QGroupBox, QMessageBox, QTabWidget, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QColor
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.pencairan_models import get_pencairan_manager
from app.config.workflow_config import UP_WORKFLOW, get_dokumen_fase
from app.ui.components import FaseStepper, FaseIndicator, DokumenChecklist, KalkulasiWidget
from app.templates.engine import format_rupiah


class UPDetailPage(QWidget):
    """Halaman detail transaksi UP dengan workflow phases"""
    
    back_requested = Signal()
    transaksi_updated = Signal(int)  # transaksi_id
    
    def __init__(self, transaksi_id: int, parent=None):
        super().__init__(parent)
        self.transaksi_id = transaksi_id
        self.pencairan_mgr = get_pencairan_manager()
        self.transaksi = None
        self.current_fase = 1
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup UI untuk detail page"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with back button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        btn_back = QPushButton("← Kembali")
        btn_back.setFixedWidth(100)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_back.clicked.connect(self.back_requested.emit)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        self.title = QLabel("📗 UANG PERSEDIAAN - Detail Transaksi")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title.setFont(title_font)
        
        self.kode_label = QLabel("Kode: —")
        kode_font = QFont()
        kode_font.setPointSize(10)
        self.kode_label.setFont(kode_font)
        self.kode_label.setStyleSheet("color: #3498db;")
        
        title_layout.addWidget(self.title)
        title_layout.addWidget(self.kode_label)
        
        header_layout.addWidget(btn_back)
        header_layout.addLayout(title_layout, 1)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Info Box
        info_group = QGroupBox("Informasi Transaksi")
        info_layout = QHBoxLayout()
        info_layout.setSpacing(40)
        
        self.info_nama = QLabel()
        self.info_nilai = QLabel()
        self.info_jenis = QLabel()
        self.info_status = QLabel()
        
        info_font = QFont()
        info_font.setPointSize(9)
        
        for label in [self.info_nama, self.info_nilai, self.info_jenis, self.info_status]:
            label.setFont(info_font)
        
        info_layout.addWidget(self.info_nama)
        info_layout.addWidget(self.info_nilai)
        info_layout.addWidget(self.info_jenis)
        info_layout.addWidget(self.info_status)
        info_layout.addStretch()
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Fase Stepper
        self.stepper = FaseStepper(current_fase=1)
        self.stepper.fase_changed.connect(self.on_fase_changed)
        layout.addWidget(self.stepper)
        
        # Scroll area untuk content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
            }
        """)
        
        self.scroll_container = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_container.setLayout(self.scroll_layout)
        scroll.setWidget(self.scroll_container)
        
        layout.addWidget(scroll, 1)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        self.btn_edit = QPushButton("✏️ Edit Data")
        self.btn_edit.setFixedWidth(120)
        self.btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_edit.clicked.connect(self.on_edit_clicked)
        
        self.btn_lanjut = QPushButton("➜ Lanjut ke Fase Berikutnya")
        self.btn_lanjut.setFixedWidth(200)
        self.btn_lanjut.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.btn_lanjut.clicked.connect(self.on_lanjut_fase_clicked)
        
        self.btn_selesaikan = QPushButton("✅ Selesaikan Transaksi")
        self.btn_selesaikan.setFixedWidth(180)
        self.btn_selesaikan.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.btn_selesaikan.clicked.connect(self.on_selesaikan_clicked)
        
        action_layout.addWidget(self.btn_edit)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_lanjut)
        action_layout.addWidget(self.btn_selesaikan)
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Load transaksi data"""
        self.transaksi = self.pencairan_mgr.get_transaksi(self.transaksi_id)
        
        if not self.transaksi:
            QMessageBox.critical(self, "Error", "Transaksi tidak ditemukan!")
            self.back_requested.emit()
            return
        
        # Update header
        self.kode_label.setText(f"Kode: {self.transaksi['kode_transaksi']}")
        
        # Update info
        self.info_nama.setText(f"📌 Nama: {self.transaksi['nama_kegiatan']}")
        self.info_nilai.setText(f"💰 Nilai: {format_rupiah(self.transaksi['estimasi_biaya'])}")
        self.info_jenis.setText(f"🏷️ Jenis: {self.transaksi['jenis_belanja']}")
        self.info_status.setText(f"📊 Status: {self.transaksi['status'].upper()}")
        
        # Update stepper
        self.current_fase = self.transaksi['fase_aktif']
        self.stepper.set_current_fase(self.current_fase)
        
        # Load content untuk fase aktif
        self.show_fase_content(self.current_fase)
    
    def show_fase_content(self, fase: int):
        """Show content untuk fase tertentu"""
        # Clear previous content
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        fase_config = UP_WORKFLOW['fase'].get(fase, {})
        
        # Fase header
        fase_header = QLabel(f"{fase_config.get('icon', '📋')} FASE {fase}: {fase_config.get('nama', '')}")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        fase_header.setFont(header_font)
        self.scroll_layout.addWidget(fase_header)
        
        # Fase description
        deskripsi = QLabel(fase_config.get('deskripsi', ''))
        desc_font = QFont()
        desc_font.setPointSize(9)
        desc_font.setItalic(True)
        deskripsi.setFont(desc_font)
        deskripsi.setStyleSheet("color: #7f8c8d;")
        self.scroll_layout.addWidget(deskripsi)
        
        # Separator
        sep = QFrame()
        sep.setStyleSheet("background-color: #ecf0f1; max-height: 1px;")
        sep.setFixedHeight(1)
        self.scroll_layout.addWidget(sep)
        
        # Dokumen checklist
        dokumen_list = self.pencairan_mgr.list_dokumen_by_transaksi(self.transaksi_id, fase)
        
        if not dokumen_list:
            # Create dokumen records jika belum ada
            for dok_config in fase_config.get('dokumen', []):
                self.pencairan_mgr.create_dokumen(
                    transaksi_id=self.transaksi_id,
                    fase=fase,
                    kode_dokumen=dok_config['kode'],
                    nama_dokumen=dok_config['nama'],
                    kategori=dok_config.get('kategori', 'wajib'),
                    template_file=dok_config.get('template')
                )
            
            dokumen_list = self.pencairan_mgr.list_dokumen_by_transaksi(self.transaksi_id, fase)
        
        checklist = DokumenChecklist(fase=fase, dokumen_list=dokumen_list)
        checklist.dokumen_created.connect(self.on_dokumen_created)
        checklist.dokumen_uploaded.connect(self.on_dokumen_uploaded)
        self.scroll_layout.addWidget(checklist)
        
        # Special widget untuk Fase 4 (Kalkulasi)
        if fase == 4:
            sep2 = QFrame()
            sep2.setStyleSheet("background-color: #ecf0f1;")
            sep2.setFixedHeight(2)
            self.scroll_layout.addWidget(sep2)
            
            kalkulasi = KalkulasiWidget(
                uang_muka=self.transaksi['uang_muka'],
                estimasi_biaya=self.transaksi['estimasi_biaya']
            )
            kalkulasi.set_values(
                uang_muka=self.transaksi['uang_muka'],
                estimasi_biaya=self.transaksi['estimasi_biaya'],
                realisasi=self.transaksi['realisasi']
            )
            kalkulasi.realisasi_changed.connect(self.on_realisasi_changed)
            self.scroll_layout.addWidget(kalkulasi)
        
        # Condition untuk lanjut
        syarat_lanjut = fase_config.get('syarat_lanjut', [])
        if syarat_lanjut:
            syarat_group = QGroupBox("✓ Syarat Lanjut ke Fase Berikutnya")
            syarat_layout = QVBoxLayout()
            
            for syarat in syarat_lanjut:
                item = QLabel(f"• {syarat}")
                item_font = QFont()
                item_font.setPointSize(9)
                item.setFont(item_font)
                syarat_layout.addWidget(item)
            
            syarat_group.setLayout(syarat_layout)
            self.scroll_layout.addWidget(syarat_group)
        
        self.scroll_layout.addStretch()
        
        # Update button state
        self.btn_lanjut.setEnabled(fase < 5)
        self.btn_selesaikan.setEnabled(fase == 5)
    
    def on_fase_changed(self, fase: int):
        """Handle fase changed dari stepper"""
        if fase <= self.current_fase:
            self.show_fase_content(fase)
    
    def on_edit_clicked(self):
        """Handle edit button clicked"""
        QMessageBox.information(self, "Info", "Feature edit akan segera tersedia")
    
    def on_dokumen_created(self, dokumen_id: str):
        """Handle dokumen created"""
        QMessageBox.information(
            self,
            "Success",
            f"Dokumen '{dokumen_id}' siap di-generate dari template"
        )
    
    def on_dokumen_uploaded(self, dokumen_id: str, file_path: str):
        """Handle dokumen uploaded"""
        # Update database
        dokumen_list = self.pencairan_mgr.list_dokumen_by_transaksi(self.transaksi_id)
        for dok in dokumen_list:
            if dok['kode_dokumen'] == dokumen_id:
                self.pencairan_mgr.update_dokumen(
                    dok['id'],
                    {
                        'file_path': file_path,
                        'status': 'uploaded'
                    }
                )
                break
        
        QMessageBox.information(
            self,
            "Success",
            f"Dokumen {dokumen_id} berhasil diupload"
        )
    
    def on_realisasi_changed(self, value: float):
        """Handle realisasi changed"""
        # Update ke database
        self.pencairan_mgr.update_transaksi(
            self.transaksi_id,
            {'realisasi': value}
        )
    
    def on_lanjut_fase_clicked(self):
        """Handle lanjut fase button clicked"""
        fase_berikutnya = self.current_fase + 1
        
        if fase_berikutnya <= 5:
            reply = QMessageBox.question(
                self,
                "Konfirmasi",
                f"Lanjut ke Fase {fase_berikutnya}?\n\n"
                "Pastikan semua dokumen wajib sudah selesai.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.pencairan_mgr.pindah_fase(
                    self.transaksi_id,
                    fase_berikutnya,
                    f"Lanjut ke Fase {fase_berikutnya}",
                    f"User lanjut ke fase {fase_berikutnya}"
                )
                
                self.transaksi = self.pencairan_mgr.get_transaksi(self.transaksi_id)
                self.current_fase = fase_berikutnya
                
                self.stepper.set_current_fase(fase_berikutnya)
                self.show_fase_content(fase_berikutnya)
                
                self.transaksi_updated.emit(self.transaksi_id)
    
    def on_selesaikan_clicked(self):
        """Handle selesaikan transaksi button clicked"""
        reply = QMessageBox.question(
            self,
            "Konfirmasi Penyelesaian",
            "Selesaikan transaksi ini?\n\n"
            "Pastikan semua dokumen sudah lengkap dan disimpan dengan baik.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.pencairan_mgr.update_transaksi(
                self.transaksi_id,
                {'status': 'selesai'}
            )
            
            QMessageBox.information(
                self,
                "Success",
                "Transaksi UP selesai! Semua dokumen sudah diarsipkan."
            )
            
            self.transaksi_updated.emit(self.transaksi_id)
            self.back_requested.emit()
