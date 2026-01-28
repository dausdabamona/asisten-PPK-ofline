"""
LS Detail Page - Detail transaksi Pembayaran Langsung dengan workflow
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QScrollArea)
from PySide6.QtCore import Qt, Signal

from app.ui.pages.pencairan.up_detail_page import UPDetailPage
from app.config.workflow_config import LS_WORKFLOW, get_fase_config
from app.ui.components import (FaseStepper, FaseIndicator, DokumenChecklist)
from app.models.pencairan_models import get_pencairan_manager
from app.templates.engine import format_rupiah


class LSDetailPage(UPDetailPage):
    """Halaman detail transaksi LS (cloned dari UP dengan modifikasi)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Override mekanisme ke LS
        self.mekanisme = 'LS'
        
        # Override workflow ke LS
        self.workflow = LS_WORKFLOW
    
    def show_fase_content(self, fase: int):
        """Override untuk menampilkan konten fase LS (tanpa countdown)"""
        # Clear existing content
        while self.scroll_layout.count():
            widget = self.scroll_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        
        # Get fase config
        fase_config = get_fase_config('LS', fase)
        if not fase_config:
            return
        
        # Add fase description
        desc_label = QLabel(fase_config.get('deskripsi', ''))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-size: 13px; padding: 10px;")
        self.scroll_layout.addWidget(desc_label)
        
        # Add separator
        separator = QLabel()
        separator.setStyleSheet("border-bottom: 1px solid #ddd;")
        separator.setFixedHeight(1)
        self.scroll_layout.addWidget(separator)
        
        # Add dokumen checklist
        dokumen_list = fase_config.get('dokumen', [])
        if dokumen_list:
            # Get or create dokumen records
            existing_dokumen = self.pencairan_mgr.list_dokumen_by_transaksi(self.transaksi_id)
            existing_ids = {d['kode_dokumen'] for d in existing_dokumen}
            
            # Create missing dokumen
            for doc_config in dokumen_list:
                if doc_config['kode'] not in existing_ids:
                    self.pencairan_mgr.create_dokumen_transaksi(
                        transaksi_id=self.transaksi_id,
                        kode_dokumen=doc_config['kode'],
                        nama_dokumen=doc_config['nama'],
                        kategori=doc_config['kategori'],
                        template_id=doc_config.get('template_id'),
                        status='pending'
                    )
            
            # Reload dokumen
            existing_dokumen = self.pencairan_mgr.list_dokumen_by_transaksi(self.transaksi_id)
            
            # Create checklist
            self.dokumen_checklist = DokumenChecklist(dokumen_list, existing_dokumen)
            self.dokumen_checklist.dokumen_created.connect(self.on_dokumen_created)
            self.dokumen_checklist.dokumen_uploaded.connect(self.on_dokumen_uploaded)
            self.scroll_layout.addWidget(self.dokumen_checklist)
        
        # LS Fase 4: Tambahkan kalkulasi widget
        if fase == 4:
            # Get transaksi data
            transaksi = self.pencairan_mgr.get_transaksi(self.transaksi_id)
            
            from app.ui.components import KalkulasiWidget
            self.kalkulasi_widget = KalkulasiWidget()
            
            # Set nilai
            if transaksi:
                # Get uang_muka dari dokumen (jika ada)
                uang_muka = transaksi.get('uang_muka', 0)
                self.kalkulasi_widget.set_values(
                    uang_muka=uang_muka,
                    estimasi_biaya=transaksi['estimasi_biaya']
                )
            
            self.scroll_layout.addWidget(self.kalkulasi_widget)
        
        # Add stretch
        self.scroll_layout.addStretch()
