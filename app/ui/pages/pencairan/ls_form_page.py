"""
LS Form Page - Form membuat transaksi Pembayaran Langsung baru
"""

from PySide6.QtWidgets import (QLabel, QMessageBox, QComboBox)
from PySide6.QtCore import Qt

from app.ui.pages.pencairan.up_form_page import UPFormPage
from app.models.pencairan_models import get_pencairan_manager


class LSFormPage(UPFormPage):
    """Form untuk membuat transaksi LS baru (cloned dari UP dengan modifikasi)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Override mekanisme ke LS
        self.mekanisme = 'LS'
        
        # Customize UI untuk LS
        self._customize_ls_form()
    
    def _customize_ls_form(self):
        """Customize form untuk LS"""
        # Update title di parent
        # Find dan update title label jika ada
        for label in self.findChildren(QLabel):
            if 'BUAT TRANSAKSI' in label.text():
                label.setText('📘 BUAT TRANSAKSI PEMBAYARAN LANGSUNG (LS) BARU')
                break
        
        # Add penyedia field
        # (akan di-update saat diperlukan dari database penyedia)
    
    def validate_form(self) -> bool:
        """Override validasi untuk LS"""
        # Run parent validasi
        if not super().validate_form():
            return False
        
        # LS-specific validasi
        # TODO: Add LS-specific validation rules
        # Misal: Pastikan penyedia terdaftar, dll
        
        return True
    
    def on_simpan_clicked(self):
        """Override untuk simpan transaksi LS"""
        if not self.validate_form():
            return
        
        try:
            # Get form data
            data = {
                'mekanisme': 'LS',  # Change to LS
                'nama_kegiatan': self.input_nama.text(),
                'jenis_belanja': self.combo_jenis_belanja.currentText(),
                'estimasi_biaya': self.spin_biaya.value(),
                'jenis_dasar': self.combo_jenis_dasar.currentText(),
                'nomor_dasar': self.input_nomor_dasar.text(),
                'tanggal_dasar': self.date_dasar.date().toPython(),
                'penerima_nama': self.input_penerima_nama.text(),
                'penerima_nip': self.input_penerima_nip.text(),
                'penerima_jabatan': self.input_penerima_jabatan.text(),
                'kode_akun': self.input_kode_akun.text(),
                'nama_akun': self.input_nama_akun.text(),
                'tanggal_kegiatan_mulai': self.date_mulai.date().toPython(),
                'tanggal_kegiatan_selesai': self.date_selesai.date().toPython(),
            }
            
            # Create transaksi
            pencairan_mgr = get_pencairan_manager()
            transaksi_id = pencairan_mgr.create_transaksi(data)
            
            # Show success
            QMessageBox.information(
                self,
                'Berhasil',
                f'Transaksi LS berhasil dibuat.\nID: {transaksi_id}',
                QMessageBox.StandardButton.Ok
            )
            
            # Emit signal
            self.transaksi_created.emit(transaksi_id)
            
            # Reset form
            self.reset_form()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                'Error',
                f'Gagal membuat transaksi: {str(e)}',
                QMessageBox.StandardButton.Ok
            )
