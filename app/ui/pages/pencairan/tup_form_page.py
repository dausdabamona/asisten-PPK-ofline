"""
TUP Form Page - Form input transaksi Tambahan Uang Persediaan
"""

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QMessageBox
from PySide6.QtGui import QFont

from app.ui.pages.pencairan.up_form_page import UPFormPage
from app.config.workflow_config import BATAS_UP_MAKSIMAL
from app.templates.engine import format_rupiah


class TUPFormPage(UPFormPage):
    """Form untuk membuat transaksi TUP baru (cloned dari UP)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mekanisme = 'TUP'
        
        # Customize untuk TUP
        self._customize_tup_form()
    
    def _customize_tup_form(self):
        """Customize form untuk TUP"""
        # Update title dan info
        # Find title label dan ubah
        title_label = None
        for label in self.findChildren(QLabel):
            if "BUAT TRANSAKSI UP BARU" in label.text():
                label.setText("📙 BUAT TRANSAKSI TUP BARU")
                break
        
        # Update batas info
        self.label_batas.setText(
            f"ℹ️ TUP adalah tambahan UP jika UP tidak mencukupi\n"
            f"Wajib diselesaikan dalam 1 BULAN (30 hari)"
        )
        self.label_batas.setStyleSheet("color: #f39c12;")
        
        # Add info group khusus TUP
        self._add_tup_info_group()
    
    def _add_tup_info_group(self):
        """Tambah info group untuk TUP"""
        # Cari scroll layout dan insert info group
        # Ini adalah custom info tentang TUP
        pass
    
    def validate_form(self) -> tuple[bool, str]:
        """Override validasi untuk TUP"""
        ok, msg = super().validate_form()
        
        if not ok:
            return ok, msg
        
        # Validasi tambahan untuk TUP
        # TUP harus lebih besar dari sisa UP
        saldo_tersedia = BATAS_UP_MAKSIMAL  # TODO: Get sisa UP dari database
        
        if self.spin_biaya.value() < 0:
            return False, "Nilai TUP yang diajukan harus positif"
        
        return True, ""
    
    def on_simpan_clicked(self):
        """Override simpan untuk TUP"""
        ok, msg = self.validate_form()
        
        if not ok:
            QMessageBox.warning(self, "Validasi Form", msg)
            return
        
        try:
            # Prepare data (sama seperti UP tapi mekanisme = TUP)
            jenis_belanja_idx = self.combo_jenis.currentIndex()
            jenis_belanja_code = self.jenis_belanja_codes[jenis_belanja_idx]
            
            data = {
                'mekanisme': 'TUP',  # Change to TUP
                'jenis_belanja': jenis_belanja_code,
                'nama_kegiatan': self.input_nama.text().strip(),
                'estimasi_biaya': self.spin_biaya.value(),
                'jenis_dasar': self.combo_jenis_dasar.currentText(),
                'nomor_dasar': self.input_nomor.text().strip(),
                'tanggal_dasar': self.date_sk.date().toString('yyyy-MM-dd'),
                'penerima_nama': self.input_penerima_nama.text().strip(),
                'penerima_nip': self.input_penerima_nip.text().strip(),
                'penerima_jabatan': self.input_penerima_jabatan.text().strip(),
                'kode_akun': self.input_kode_akun.text().strip(),
                'nama_akun': self.input_nama_akun.text().strip() or 'Auto',
                'tanggal_kegiatan_mulai': self.date_mulai.date().toString('yyyy-MM-dd'),
                'tanggal_kegiatan_selesai': self.date_selesai.date().toString('yyyy-MM-dd'),
            }
            
            # Create transaksi
            transaksi_id = self.pencairan_mgr.create_transaksi(data)
            
            QMessageBox.information(
                self,
                "Sukses",
                f"Transaksi TUP berhasil dibuat!\n\n"
                f"Kode: {self.pencairan_mgr.get_transaksi(transaksi_id)['kode_transaksi']}\n\n"
                f"⚠️ PENTING: TUP harus diselesaikan dalam 1 BULAN (30 hari)."
            )
            
            self.transaksi_created.emit(transaksi_id)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Gagal membuat transaksi TUP:\n\n{str(e)}"
            )
