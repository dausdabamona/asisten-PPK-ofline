"""
TUP Detail Page - Detail transaksi TUP dengan countdown 30 hari
"""

from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Signal
from datetime import datetime

from app.ui.pages.pencairan.up_detail_page import UPDetailPage
from app.config.workflow_config import TUP_WORKFLOW
from app.ui.components import CountdownWidget


class TUPDetailPage(UPDetailPage):
    """Halaman detail transaksi TUP (cloned dari UP dengan countdown)"""
    
    def __init__(self, transaksi_id: int, parent=None):
        self.add_countdown = True  # Flag untuk menambah countdown di fase 4
        super().__init__(transaksi_id, parent)
    
    def show_fase_content(self, fase: int):
        """Override untuk TUP dengan countdown di fase 4"""
        # Clear previous content
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        fase_config = TUP_WORKFLOW['fase'].get(fase, {})
        
        # Fase header
        from PySide6.QtWidgets import QLabel, QFrame
        from PySide6.QtGui import QFont
        
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
        
        from app.ui.components import DokumenChecklist
        
        checklist = DokumenChecklist(fase=fase, dokumen_list=dokumen_list)
        checklist.dokumen_created.connect(self.on_dokumen_created)
        checklist.dokumen_uploaded.connect(self.on_dokumen_uploaded)
        self.scroll_layout.addWidget(checklist)
        
        # Special widget untuk Fase 4 (Countdown untuk TUP)
        if fase == 4:
            sep2 = QFrame()
            sep2.setStyleSheet("background-color: #ecf0f1;")
            sep2.setFixedHeight(2)
            self.scroll_layout.addWidget(sep2)
            
            # Countdown widget untuk TUP (max 30 hari)
            tanggal_sp2d = datetime.now()  # TODO: Get dari database
            countdown = CountdownWidget(
                tanggal_sp2d=tanggal_sp2d,
                max_hari=30
            )
            self.scroll_layout.addWidget(countdown)
            
            # Kalkulasi untuk sisa TUP
            from app.ui.components import KalkulasiWidget
            
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
            from PySide6.QtWidgets import QGroupBox, QVBoxLayout
            
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
