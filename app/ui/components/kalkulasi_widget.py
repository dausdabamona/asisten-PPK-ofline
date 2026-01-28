"""
Kalkulasi Widget - Untuk menampilkan perhitungan tambah/kurang di Fase 4
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from app.templates.engine import format_rupiah, terbilang


class KalkulasiWidget(QWidget):
    """Widget untuk menampilkan perhitungan pertanggungjawaban"""
    
    realisasi_changed = Signal(float)
    
    def __init__(self, uang_muka: float = 0, estimasi_biaya: float = 0, parent=None):
        super().__init__(parent)
        self.uang_muka = uang_muka
        self.estimasi_biaya = estimasi_biaya
        self.realisasi = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI untuk kalkulasi"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Group Box untuk kalkulasi
        group = QGroupBox("Perhitungan Pertanggungjawaban")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(15)
        
        # Row 1: Uang Muka (read-only)
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        
        label_um = QLabel("Uang Muka Diterima:")
        um_font = QFont()
        um_font.setPointSize(10)
        label_um.setFont(um_font)
        label_um.setFixedWidth(200)
        
        self.display_um = QLabel(format_rupiah(self.uang_muka))
        display_um_font = QFont()
        display_um_font.setPointSize(11)
        display_um_font.setBold(True)
        self.display_um.setFont(display_um_font)
        self.display_um.setStyleSheet("color: #3498db;")
        
        row1.addWidget(label_um)
        row1.addWidget(self.display_um)
        row1.addStretch()
        group_layout.addLayout(row1)
        
        # Row 2: Total Realisasi (editable)
        row2 = QHBoxLayout()
        row2.setSpacing(15)
        
        label_real = QLabel("Total Realisasi:")
        real_font = QFont()
        real_font.setPointSize(10)
        label_real.setFont(real_font)
        label_real.setFixedWidth(200)
        
        self.spin_realisasi = QDoubleSpinBox()
        self.spin_realisasi.setRange(0, 999999999)
        self.spin_realisasi.setValue(self.realisasi)
        self.spin_realisasi.setSingleStep(100000)
        self.spin_realisasi.setFixedWidth(200)
        self.spin_realisasi.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.spin_realisasi.valueChanged.connect(self.on_realisasi_changed)
        
        label_info = QLabel("(Jumlah uang yang benar-benar dikeluarkan)")
        info_font = QFont()
        info_font.setPointSize(8)
        info_font.setItalic(True)
        label_info.setFont(info_font)
        label_info.setStyleSheet("color: #7f8c8d;")
        
        row2.addWidget(label_real)
        row2.addWidget(self.spin_realisasi)
        row2.addWidget(label_info)
        row2.addStretch()
        group_layout.addLayout(row2)
        
        # Separator
        sep = QLabel("—" * 80)
        sep.setStyleSheet("color: #ecf0f1;")
        group_layout.addWidget(sep)
        
        # Row 3: Selisih (calculated)
        row3 = QHBoxLayout()
        row3.setSpacing(15)
        
        label_sel = QLabel("Selisih (Realisasi - UM):")
        sel_font = QFont()
        sel_font.setPointSize(11)
        sel_font.setBold(True)
        label_sel.setFont(sel_font)
        label_sel.setFixedWidth(200)
        
        self.display_selisih = QLabel(format_rupiah(0))
        display_sel_font = QFont()
        display_sel_font.setPointSize(12)
        display_sel_font.setBold(True)
        self.display_selisih.setFont(display_sel_font)
        self.display_selisih.setStyleSheet("color: #e74c3c;")  # Red for negative
        
        row3.addWidget(label_sel)
        row3.addWidget(self.display_selisih)
        row3.addStretch()
        group_layout.addLayout(row3)
        
        # Row 4: Hasil (kurang/lebih/pas)
        row4 = QHBoxLayout()
        row4.setSpacing(15)
        
        label_hasil = QLabel("Hasil:")
        hasil_font = QFont()
        hasil_font.setPointSize(11)
        hasil_font.setBold(True)
        label_hasil.setFont(hasil_font)
        label_hasil.setFixedWidth(200)
        
        self.label_hasil = QLabel("Menunggu input realisasi")
        hasil_text_font = QFont()
        hasil_text_font.setPointSize(11)
        hasil_text_font.setBold(True)
        self.label_hasil.setFont(hasil_text_font)
        self.label_hasil.setStyleSheet("color: #95a5a6;")
        
        row4.addWidget(label_hasil)
        row4.addWidget(self.label_hasil)
        row4.addStretch()
        group_layout.addLayout(row4)
        
        # Row 5: Terbilang
        row5 = QHBoxLayout()
        row5.setSpacing(15)
        
        label_terb = QLabel("Terbilang:")
        terb_font = QFont()
        terb_font.setPointSize(9)
        label_terb.setFont(terb_font)
        label_terb.setFixedWidth(200)
        
        self.display_terbilang = QLabel("—")
        terb_display_font = QFont()
        terb_display_font.setPointSize(9)
        terb_display_font.setItalic(True)
        self.display_terbilang.setFont(terb_display_font)
        self.display_terbilang.setStyleSheet("color: #7f8c8d;")
        self.display_terbilang.setWordWrap(True)
        
        row5.addWidget(label_terb)
        row5.addWidget(self.display_terbilang, 1)
        group_layout.addLayout(row5)
        
        # Row 6: Rekomendasi aksi
        row6 = QHBoxLayout()
        row6.setSpacing(15)
        
        label_aksi = QLabel("Rekomendasi:")
        aksi_font = QFont()
        aksi_font.setPointSize(10)
        aksi_font.setBold(True)
        label_aksi.setFont(aksi_font)
        label_aksi.setFixedWidth(200)
        
        self.label_aksi = QLabel("—")
        aksi_display_font = QFont()
        aksi_display_font.setPointSize(10)
        self.label_aksi.setFont(aksi_display_font)
        self.label_aksi.setWordWrap(True)
        
        row6.addWidget(label_aksi)
        row6.addWidget(self.label_aksi, 1)
        group_layout.addLayout(row6)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def on_realisasi_changed(self, value: float):
        """Handle realisasi changed"""
        self.realisasi = value
        self.update_kalkulasi()
        self.realisasi_changed.emit(value)
    
    def update_kalkulasi(self):
        """Update semua kalkulasi"""
        # Hitung selisih
        selisih = self.realisasi - self.uang_muka
        
        # Update display selisih
        self.display_selisih.setText(format_rupiah(selisih))
        
        # Update terbilang
        try:
            abs_selisih = abs(selisih)
            terb = terbilang(int(abs_selisih))
            self.display_terbilang.setText(terb + " rupiah")
        except:
            self.display_terbilang.setText("—")
        
        # Update hasil & warna
        if selisih < -0.01:  # LEBIH BAYAR
            self.label_hasil.setText("❌ LEBIH BAYAR")
            self.label_hasil.setStyleSheet("color: #f39c12;")
            self.display_selisih.setStyleSheet("color: #f39c12;")
            self.label_aksi.setText("⚠️ Uang harus dikembalikan ke Bendahara")
            self.label_aksi.setStyleSheet("color: #f39c12;")
        
        elif selisih > 0.01:  # KURANG BAYAR
            self.label_hasil.setText("⚠️ KURANG BAYAR")
            self.label_hasil.setStyleSheet("color: #e74c3c;")
            self.display_selisih.setStyleSheet("color: #e74c3c;")
            self.label_aksi.setText("📌 Ajukan SPP tambahan untuk pembayaran kekurangan")
            self.label_aksi.setStyleSheet("color: #e74c3c;")
        
        else:  # PAS / NIHIL
            self.label_hasil.setText("✅ PAS / NIHIL")
            self.label_hasil.setStyleSheet("color: #27ae60;")
            self.display_selisih.setStyleSheet("color: #27ae60;")
            self.label_aksi.setText("✓ Perhitungan seimbang, lanjut ke SPBY")
            self.label_aksi.setStyleSheet("color: #27ae60;")
    
    def set_values(self, uang_muka: float, estimasi_biaya: float, realisasi: float = None):
        """Set nilai-nilai kalkulasi"""
        self.uang_muka = uang_muka
        self.estimasi_biaya = estimasi_biaya
        
        # Update display UM
        self.display_um.setText(format_rupiah(self.uang_muka))
        
        # Update realisasi jika diberikan
        if realisasi is not None:
            self.spin_realisasi.setValue(realisasi)
            self.realisasi = realisasi
        
        self.update_kalkulasi()
    
    def get_realisasi(self) -> float:
        """Get nilai realisasi"""
        return self.realisasi
    
    def get_selisih(self) -> float:
        """Get nilai selisih"""
        return self.realisasi - self.uang_muka
    
    def get_hasil_tipe(self) -> str:
        """Get tipe hasil (kurang/lebih/pas)"""
        selisih = self.get_selisih()
        
        if selisih < -0.01:
            return 'lebih'
        elif selisih > 0.01:
            return 'kurang'
        else:
            return 'pas'
