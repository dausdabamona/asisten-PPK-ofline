"""
LS List Page - Daftar semua transaksi Pembayaran Langsung
"""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.ui.pages.pencairan.up_list_page import UPListPage
from app.templates.engine import format_rupiah


class LSListPage(UPListPage):
    """Halaman daftar transaksi LS (cloned dari UP dengan modifikasi)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Override mekanisme ke LS
        self.mekanisme = 'LS'
        
        # Customize UI untuk LS
        self._customize_ls_ui()
    
    def _customize_ls_ui(self):
        """Customize UI untuk LS"""
        # Update title
        for label in self.findChildren(type(self)):
            pass
    
    def load_data(self):
        """Override load_data untuk LS"""
        status_map = {
            'Semua Status': None,
            'Draft': 'draft',
            'Aktif': 'aktif',
            'Selesai': 'selesai',
            'Batal': 'batal'
        }
        
        status_filter = status_map.get(self.combo_filter.currentText())
        transaksi_list = self.pencairan_mgr.list_transaksi(
            mekanisme='LS',  # Change to LS
            status=status_filter
        )
        
        # Filter by search
        search_text = self.search_input.text().lower()
        if search_text:
            transaksi_list = [
                t for t in transaksi_list
                if search_text in t['kode_transaksi'].lower() or
                   search_text in t['nama_kegiatan'].lower()
            ]
        
        # Load ke table
        self.table.setRowCount(0)
        
        for row, transaksi in enumerate(transaksi_list):
            self.table.insertRow(row)
            
            # Kode
            kode_item = QTableWidgetItem(transaksi['kode_transaksi'])
            kode_font = QFont()
            kode_font.setBold(True)
            kode_item.setFont(kode_font)
            kode_item.setForeground(QColor('#3498db'))  # Blue for LS
            self.table.setItem(row, 0, kode_item)
            
            # Nama kegiatan
            self.table.setItem(row, 1, QTableWidgetItem(transaksi['nama_kegiatan']))
            
            # Nilai
            nilai_item = QTableWidgetItem(format_rupiah(transaksi['estimasi_biaya']))
            nilai_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 2, nilai_item)
            
            # Jenis belanja
            self.table.setItem(row, 3, QTableWidgetItem(transaksi['jenis_belanja']))
            
            # Fase
            fase_item = QTableWidgetItem(f"Fase {transaksi['fase_aktif']}")
            self.table.setItem(row, 4, fase_item)
            
            # Status
            status_icon = self._get_status_icon(transaksi['status'])
            status_item = QTableWidgetItem(f"{status_icon} {transaksi['status'].upper()}")
            self.table.setItem(row, 5, status_item)
        
        # Update summary
        self._update_summary()
    
    def _update_summary(self):
        """Update summary statistics untuk LS"""
        draft = self.pencairan_mgr.count_transaksi(mekanisme='LS', status='draft')
        aktif = self.pencairan_mgr.count_transaksi(mekanisme='LS', status='aktif')
        selesai = self.pencairan_mgr.count_transaksi(mekanisme='LS', status='selesai')
        total = draft + aktif + selesai
        
        self.label_draft.setText(f"📋 Draft: {draft}")
        self.label_aktif.setText(f"⚙️ Aktif: {aktif}")
        self.label_selesai.setText(f"✅ Selesai: {selesai}")
        self.label_total.setText(f"📊 Total: {total}")
