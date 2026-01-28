"""
PPK DOCUMENT FACTORY - Biaya Perjalanan Dinas Widget
=====================================================
Widget untuk menghitung estimasi biaya perjalanan dinas.

Komponen Biaya:
- Tiket Pesawat (pergi & pulang)
- Transportasi Darat (bandara, lokal)
- Penginapan
- Uang Harian
- Uang Representasi (jika ada)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QLineEdit, QDoubleSpinBox,
    QSpinBox, QComboBox, QGroupBox, QScrollArea,
    QGraphicsDropShadowEffect, QSizePolicy, QDateEdit,
    QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor, QFont

from typing import Dict, Any, List, Optional
from datetime import datetime, date


def format_rupiah(value: float) -> str:
    """Format angka ke format Rupiah."""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


def terbilang(n: float) -> str:
    """Konversi angka ke terbilang dalam Bahasa Indonesia."""
    if n == 0:
        return "nol rupiah"

    satuan = ["", "satu", "dua", "tiga", "empat", "lima",
              "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]

    n = int(n)

    if n < 0:
        return "minus " + terbilang(-n)
    elif n < 12:
        return satuan[n]
    elif n < 20:
        return satuan[n - 10] + " belas"
    elif n < 100:
        return satuan[n // 10] + " puluh " + satuan[n % 10]
    elif n < 200:
        return "seratus " + terbilang(n - 100)
    elif n < 1000:
        return satuan[n // 100] + " ratus " + terbilang(n % 100)
    elif n < 2000:
        return "seribu " + terbilang(n - 1000)
    elif n < 1000000:
        return terbilang(n // 1000) + " ribu " + terbilang(n % 1000)
    elif n < 1000000000:
        return terbilang(n // 1000000) + " juta " + terbilang(n % 1000000)
    elif n < 1000000000000:
        return terbilang(n // 1000000000) + " miliar " + terbilang(n % 1000000000)
    else:
        return terbilang(n // 1000000000000) + " triliun " + terbilang(n % 1000000000000)


# Standar biaya umum (SBU) - dapat disesuaikan
STANDAR_BIAYA = {
    "uang_harian": {
        "dalam_kota": 150000,
        "luar_kota": 430000,
        "luar_negeri": 850000,
    },
    "uang_penginapan": {
        "eselon_1": 1500000,
        "eselon_2": 1000000,
        "eselon_3": 750000,
        "eselon_4": 600000,
        "staf": 500000,
    },
    "transport_lokal": {
        "dalam_kota": 150000,
        "luar_kota": 200000,
    }
}


class BiayaPerjalananWidget(QFrame):
    """
    Widget untuk menghitung estimasi biaya perjalanan dinas.

    Signals:
        total_changed(float): Emitted when total changes
        data_changed(): Emitted when any data changes
    """

    total_changed = Signal(float)
    data_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._total = 0.0
        self._setup_ui()
        self._connect_signals()
        self._calculate()

    def _setup_ui(self):
        """Setup widget UI."""
        self.setObjectName("biayaPerjalananWidget")
        self.setStyleSheet("""
            #biayaPerjalananWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Header
        header = QLabel("Perhitungan Biaya Perjalanan Dinas")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        main_layout.addWidget(header)

        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)

        # ========== Info Perjalanan ==========
        info_group = QGroupBox("Informasi Perjalanan")
        info_layout = QGridLayout(info_group)
        info_layout.setSpacing(10)

        # Jenis perjalanan
        info_layout.addWidget(QLabel("Jenis Perjalanan:"), 0, 0)
        self.jenis_combo = QComboBox()
        self.jenis_combo.addItems(["Dalam Kota", "Luar Kota", "Luar Negeri"])
        self.jenis_combo.setCurrentIndex(1)
        info_layout.addWidget(self.jenis_combo, 0, 1)

        # Tingkat biaya
        info_layout.addWidget(QLabel("Tingkat Biaya:"), 0, 2)
        self.tingkat_combo = QComboBox()
        self.tingkat_combo.addItems(["Eselon I", "Eselon II", "Eselon III", "Eselon IV", "Staf"])
        self.tingkat_combo.setCurrentIndex(4)
        info_layout.addWidget(self.tingkat_combo, 0, 3)

        # Jumlah orang
        info_layout.addWidget(QLabel("Jumlah Orang:"), 1, 0)
        self.jumlah_orang_spin = QSpinBox()
        self.jumlah_orang_spin.setRange(1, 99)
        self.jumlah_orang_spin.setValue(1)
        info_layout.addWidget(self.jumlah_orang_spin, 1, 1)

        # Jumlah hari
        info_layout.addWidget(QLabel("Jumlah Hari:"), 1, 2)
        self.jumlah_hari_spin = QSpinBox()
        self.jumlah_hari_spin.setRange(1, 365)
        self.jumlah_hari_spin.setValue(1)
        info_layout.addWidget(self.jumlah_hari_spin, 1, 3)

        # Jumlah malam
        info_layout.addWidget(QLabel("Jumlah Malam:"), 2, 0)
        self.jumlah_malam_spin = QSpinBox()
        self.jumlah_malam_spin.setRange(0, 364)
        self.jumlah_malam_spin.setValue(0)
        info_layout.addWidget(self.jumlah_malam_spin, 2, 1)

        form_layout.addWidget(info_group)

        # ========== Tiket Perjalanan ==========
        tiket_group = QGroupBox("Tiket Perjalanan")
        tiket_layout = QGridLayout(tiket_group)
        tiket_layout.setSpacing(10)

        # Tiket pergi
        tiket_layout.addWidget(QLabel("Tiket Pergi:"), 0, 0)
        self.tiket_pergi_spin = QDoubleSpinBox()
        self.tiket_pergi_spin.setRange(0, 99999999)
        self.tiket_pergi_spin.setDecimals(0)
        self.tiket_pergi_spin.setPrefix("Rp ")
        self.tiket_pergi_spin.setGroupSeparatorShown(True)
        tiket_layout.addWidget(self.tiket_pergi_spin, 0, 1)

        # Tiket pulang
        tiket_layout.addWidget(QLabel("Tiket Pulang:"), 0, 2)
        self.tiket_pulang_spin = QDoubleSpinBox()
        self.tiket_pulang_spin.setRange(0, 99999999)
        self.tiket_pulang_spin.setDecimals(0)
        self.tiket_pulang_spin.setPrefix("Rp ")
        self.tiket_pulang_spin.setGroupSeparatorShown(True)
        tiket_layout.addWidget(self.tiket_pulang_spin, 0, 3)

        # Checkbox PP sama
        self.tiket_pp_cb = QCheckBox("Tiket PP (harga sama)")
        self.tiket_pp_cb.stateChanged.connect(self._on_tiket_pp_changed)
        tiket_layout.addWidget(self.tiket_pp_cb, 1, 0, 1, 2)

        # Subtotal tiket
        tiket_layout.addWidget(QLabel("Subtotal Tiket:"), 1, 2)
        self.subtotal_tiket_label = QLabel("Rp 0")
        self.subtotal_tiket_label.setStyleSheet("font-weight: bold; color: #3498db;")
        tiket_layout.addWidget(self.subtotal_tiket_label, 1, 3)

        form_layout.addWidget(tiket_group)

        # ========== Transport Darat ==========
        transport_group = QGroupBox("Transportasi Darat")
        transport_layout = QGridLayout(transport_group)
        transport_layout.setSpacing(10)

        # Transport bandara/stasiun (PP)
        transport_layout.addWidget(QLabel("Transport Bandara/Stasiun (PP):"), 0, 0)
        self.transport_bandara_spin = QDoubleSpinBox()
        self.transport_bandara_spin.setRange(0, 99999999)
        self.transport_bandara_spin.setDecimals(0)
        self.transport_bandara_spin.setPrefix("Rp ")
        self.transport_bandara_spin.setGroupSeparatorShown(True)
        transport_layout.addWidget(self.transport_bandara_spin, 0, 1)

        # Transport lokal per hari
        transport_layout.addWidget(QLabel("Transport Lokal (per hari):"), 1, 0)
        self.transport_lokal_spin = QDoubleSpinBox()
        self.transport_lokal_spin.setRange(0, 99999999)
        self.transport_lokal_spin.setDecimals(0)
        self.transport_lokal_spin.setPrefix("Rp ")
        self.transport_lokal_spin.setGroupSeparatorShown(True)
        self.transport_lokal_spin.setValue(200000)
        transport_layout.addWidget(self.transport_lokal_spin, 1, 1)

        # Subtotal transport
        transport_layout.addWidget(QLabel("Subtotal Transport:"), 1, 2)
        self.subtotal_transport_label = QLabel("Rp 0")
        self.subtotal_transport_label.setStyleSheet("font-weight: bold; color: #3498db;")
        transport_layout.addWidget(self.subtotal_transport_label, 1, 3)

        form_layout.addWidget(transport_group)

        # ========== Penginapan ==========
        hotel_group = QGroupBox("Penginapan")
        hotel_layout = QGridLayout(hotel_group)
        hotel_layout.setSpacing(10)

        # Biaya per malam
        hotel_layout.addWidget(QLabel("Biaya per Malam:"), 0, 0)
        self.hotel_spin = QDoubleSpinBox()
        self.hotel_spin.setRange(0, 99999999)
        self.hotel_spin.setDecimals(0)
        self.hotel_spin.setPrefix("Rp ")
        self.hotel_spin.setGroupSeparatorShown(True)
        self.hotel_spin.setValue(500000)
        hotel_layout.addWidget(self.hotel_spin, 0, 1)

        # Gunakan standar
        self.hotel_standar_cb = QCheckBox("Gunakan standar sesuai tingkat")
        self.hotel_standar_cb.stateChanged.connect(self._on_hotel_standar_changed)
        hotel_layout.addWidget(self.hotel_standar_cb, 0, 2, 1, 2)

        # Subtotal
        hotel_layout.addWidget(QLabel("Subtotal Penginapan:"), 1, 0)
        self.subtotal_hotel_label = QLabel("Rp 0")
        self.subtotal_hotel_label.setStyleSheet("font-weight: bold; color: #3498db;")
        hotel_layout.addWidget(self.subtotal_hotel_label, 1, 1)

        form_layout.addWidget(hotel_group)

        # ========== Uang Harian ==========
        harian_group = QGroupBox("Uang Harian")
        harian_layout = QGridLayout(harian_group)
        harian_layout.setSpacing(10)

        # Uang harian per hari
        harian_layout.addWidget(QLabel("Uang Harian per Hari:"), 0, 0)
        self.harian_spin = QDoubleSpinBox()
        self.harian_spin.setRange(0, 99999999)
        self.harian_spin.setDecimals(0)
        self.harian_spin.setPrefix("Rp ")
        self.harian_spin.setGroupSeparatorShown(True)
        self.harian_spin.setValue(430000)
        harian_layout.addWidget(self.harian_spin, 0, 1)

        # Gunakan standar
        self.harian_standar_cb = QCheckBox("Gunakan standar sesuai jenis")
        self.harian_standar_cb.stateChanged.connect(self._on_harian_standar_changed)
        harian_layout.addWidget(self.harian_standar_cb, 0, 2, 1, 2)

        # Subtotal
        harian_layout.addWidget(QLabel("Subtotal Uang Harian:"), 1, 0)
        self.subtotal_harian_label = QLabel("Rp 0")
        self.subtotal_harian_label.setStyleSheet("font-weight: bold; color: #3498db;")
        harian_layout.addWidget(self.subtotal_harian_label, 1, 1)

        form_layout.addWidget(harian_group)

        # ========== Biaya Lainnya ==========
        lain_group = QGroupBox("Biaya Lainnya")
        lain_layout = QGridLayout(lain_group)
        lain_layout.setSpacing(10)

        # Uang representasi
        lain_layout.addWidget(QLabel("Uang Representasi:"), 0, 0)
        self.representasi_spin = QDoubleSpinBox()
        self.representasi_spin.setRange(0, 99999999)
        self.representasi_spin.setDecimals(0)
        self.representasi_spin.setPrefix("Rp ")
        self.representasi_spin.setGroupSeparatorShown(True)
        lain_layout.addWidget(self.representasi_spin, 0, 1)

        # Biaya lain-lain
        lain_layout.addWidget(QLabel("Biaya Lain-lain:"), 1, 0)
        self.lainnya_spin = QDoubleSpinBox()
        self.lainnya_spin.setRange(0, 99999999)
        self.lainnya_spin.setDecimals(0)
        self.lainnya_spin.setPrefix("Rp ")
        self.lainnya_spin.setGroupSeparatorShown(True)
        lain_layout.addWidget(self.lainnya_spin, 1, 1)

        # Keterangan
        lain_layout.addWidget(QLabel("Keterangan:"), 1, 2)
        self.lainnya_ket = QLineEdit()
        self.lainnya_ket.setPlaceholderText("Ket. biaya lainnya")
        lain_layout.addWidget(self.lainnya_ket, 1, 3)

        form_layout.addWidget(lain_group)

        form_layout.addStretch()
        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll)

        # ========== Total Section ==========
        total_frame = QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background-color: #27ae60;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        total_layout = QVBoxLayout(total_frame)
        total_layout.setSpacing(8)

        # Grand total
        total_row = QHBoxLayout()
        total_label = QLabel("TOTAL ESTIMASI BIAYA:")
        total_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        total_row.addWidget(total_label)

        total_row.addStretch()

        self.total_display = QLabel("Rp 0")
        self.total_display.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        total_row.addWidget(self.total_display)

        total_layout.addLayout(total_row)

        # Terbilang
        self.terbilang_label = QLabel("( nol rupiah )")
        self.terbilang_label.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.8); font-style: italic;")
        self.terbilang_label.setWordWrap(True)
        total_layout.addWidget(self.terbilang_label)

        main_layout.addWidget(total_frame)

    def _connect_signals(self):
        """Connect all input signals to calculate."""
        # Info
        self.jenis_combo.currentIndexChanged.connect(self._calculate)
        self.tingkat_combo.currentIndexChanged.connect(self._calculate)
        self.jumlah_orang_spin.valueChanged.connect(self._calculate)
        self.jumlah_hari_spin.valueChanged.connect(self._calculate)
        self.jumlah_malam_spin.valueChanged.connect(self._calculate)

        # Tiket
        self.tiket_pergi_spin.valueChanged.connect(self._calculate)
        self.tiket_pulang_spin.valueChanged.connect(self._calculate)

        # Transport
        self.transport_bandara_spin.valueChanged.connect(self._calculate)
        self.transport_lokal_spin.valueChanged.connect(self._calculate)

        # Hotel
        self.hotel_spin.valueChanged.connect(self._calculate)

        # Harian
        self.harian_spin.valueChanged.connect(self._calculate)

        # Lainnya
        self.representasi_spin.valueChanged.connect(self._calculate)
        self.lainnya_spin.valueChanged.connect(self._calculate)

    def _on_tiket_pp_changed(self, state):
        """Handle tiket PP checkbox."""
        if state == Qt.Checked:
            self.tiket_pulang_spin.setValue(self.tiket_pergi_spin.value())
            self.tiket_pulang_spin.setEnabled(False)
        else:
            self.tiket_pulang_spin.setEnabled(True)

    def _on_hotel_standar_changed(self, state):
        """Handle hotel standar checkbox."""
        if state == Qt.Checked:
            tingkat_map = {
                0: "eselon_1", 1: "eselon_2", 2: "eselon_3",
                3: "eselon_4", 4: "staf"
            }
            tingkat = tingkat_map.get(self.tingkat_combo.currentIndex(), "staf")
            standar = STANDAR_BIAYA["uang_penginapan"].get(tingkat, 500000)
            self.hotel_spin.setValue(standar)
            self.hotel_spin.setEnabled(False)
        else:
            self.hotel_spin.setEnabled(True)

    def _on_harian_standar_changed(self, state):
        """Handle harian standar checkbox."""
        if state == Qt.Checked:
            jenis_map = {
                0: "dalam_kota", 1: "luar_kota", 2: "luar_negeri"
            }
            jenis = jenis_map.get(self.jenis_combo.currentIndex(), "luar_kota")
            standar = STANDAR_BIAYA["uang_harian"].get(jenis, 430000)
            self.harian_spin.setValue(standar)
            self.harian_spin.setEnabled(False)
        else:
            self.harian_spin.setEnabled(True)

    def _calculate(self):
        """Calculate all costs."""
        orang = self.jumlah_orang_spin.value()
        hari = self.jumlah_hari_spin.value()
        malam = self.jumlah_malam_spin.value()

        # Tiket
        tiket_pergi = self.tiket_pergi_spin.value()
        tiket_pulang = self.tiket_pulang_spin.value()
        if self.tiket_pp_cb.isChecked():
            tiket_pulang = tiket_pergi
            self.tiket_pulang_spin.setValue(tiket_pergi)
        subtotal_tiket = (tiket_pergi + tiket_pulang) * orang
        self.subtotal_tiket_label.setText(format_rupiah(subtotal_tiket))

        # Transport
        transport_bandara = self.transport_bandara_spin.value() * orang
        transport_lokal = self.transport_lokal_spin.value() * hari * orang
        subtotal_transport = transport_bandara + transport_lokal
        self.subtotal_transport_label.setText(format_rupiah(subtotal_transport))

        # Hotel
        hotel_per_malam = self.hotel_spin.value()
        subtotal_hotel = hotel_per_malam * malam * orang
        self.subtotal_hotel_label.setText(format_rupiah(subtotal_hotel))

        # Harian
        harian_per_hari = self.harian_spin.value()
        subtotal_harian = harian_per_hari * hari * orang
        self.subtotal_harian_label.setText(format_rupiah(subtotal_harian))

        # Lainnya
        representasi = self.representasi_spin.value() * orang
        lainnya = self.lainnya_spin.value()

        # Grand total
        self._total = (subtotal_tiket + subtotal_transport +
                       subtotal_hotel + subtotal_harian +
                       representasi + lainnya)

        self.total_display.setText(format_rupiah(self._total))

        # Terbilang
        terbilang_text = terbilang(self._total)
        if terbilang_text:
            terbilang_text = terbilang_text[0].upper() + terbilang_text[1:]
            if not terbilang_text.endswith("rupiah"):
                terbilang_text += " rupiah"
        self.terbilang_label.setText(f"( {terbilang_text} )")

        # Emit signals
        self.total_changed.emit(self._total)
        self.data_changed.emit()

    def get_total(self) -> float:
        """Get total biaya."""
        return self._total

    def get_data(self) -> Dict[str, Any]:
        """Get all form data."""
        orang = self.jumlah_orang_spin.value()
        hari = self.jumlah_hari_spin.value()
        malam = self.jumlah_malam_spin.value()

        return {
            'jenis_perjalanan': self.jenis_combo.currentText(),
            'tingkat_biaya': self.tingkat_combo.currentText(),
            'jumlah_orang': orang,
            'jumlah_hari': hari,
            'jumlah_malam': malam,
            'tiket_pergi': self.tiket_pergi_spin.value(),
            'tiket_pulang': self.tiket_pulang_spin.value(),
            'subtotal_tiket': (self.tiket_pergi_spin.value() + self.tiket_pulang_spin.value()) * orang,
            'transport_bandara': self.transport_bandara_spin.value(),
            'transport_lokal': self.transport_lokal_spin.value(),
            'subtotal_transport': self.transport_bandara_spin.value() * orang + self.transport_lokal_spin.value() * hari * orang,
            'penginapan_per_malam': self.hotel_spin.value(),
            'subtotal_penginapan': self.hotel_spin.value() * malam * orang,
            'uang_harian': self.harian_spin.value(),
            'subtotal_uang_harian': self.harian_spin.value() * hari * orang,
            'uang_representasi': self.representasi_spin.value(),
            'biaya_lainnya': self.lainnya_spin.value(),
            'keterangan_lainnya': self.lainnya_ket.text(),
            'total': self._total,
            'total_terbilang': terbilang(self._total),
        }

    def set_data(self, data: Dict[str, Any]):
        """Set form data."""
        if 'jumlah_orang' in data:
            self.jumlah_orang_spin.setValue(data['jumlah_orang'])
        if 'jumlah_hari' in data:
            self.jumlah_hari_spin.setValue(data['jumlah_hari'])
        if 'jumlah_malam' in data:
            self.jumlah_malam_spin.setValue(data['jumlah_malam'])
        if 'tiket_pergi' in data:
            self.tiket_pergi_spin.setValue(data['tiket_pergi'])
        if 'tiket_pulang' in data:
            self.tiket_pulang_spin.setValue(data['tiket_pulang'])
        if 'transport_bandara' in data:
            self.transport_bandara_spin.setValue(data['transport_bandara'])
        if 'transport_lokal' in data:
            self.transport_lokal_spin.setValue(data['transport_lokal'])
        if 'penginapan_per_malam' in data:
            self.hotel_spin.setValue(data['penginapan_per_malam'])
        if 'uang_harian' in data:
            self.harian_spin.setValue(data['uang_harian'])
        if 'uang_representasi' in data:
            self.representasi_spin.setValue(data['uang_representasi'])
        if 'biaya_lainnya' in data:
            self.lainnya_spin.setValue(data['biaya_lainnya'])
        if 'keterangan_lainnya' in data:
            self.lainnya_ket.setText(data['keterangan_lainnya'])

    def clear(self):
        """Clear all inputs."""
        self.jumlah_orang_spin.setValue(1)
        self.jumlah_hari_spin.setValue(1)
        self.jumlah_malam_spin.setValue(0)
        self.tiket_pergi_spin.setValue(0)
        self.tiket_pulang_spin.setValue(0)
        self.transport_bandara_spin.setValue(0)
        self.transport_lokal_spin.setValue(200000)
        self.hotel_spin.setValue(500000)
        self.harian_spin.setValue(430000)
        self.representasi_spin.setValue(0)
        self.lainnya_spin.setValue(0)
        self.lainnya_ket.clear()
        self.tiket_pp_cb.setChecked(False)
        self.hotel_standar_cb.setChecked(False)
        self.harian_standar_cb.setChecked(False)

    def get_rincian_items(self) -> List[Dict[str, Any]]:
        """Get rincian items for document generation."""
        orang = self.jumlah_orang_spin.value()
        hari = self.jumlah_hari_spin.value()
        malam = self.jumlah_malam_spin.value()

        items = []

        # Tiket
        tiket_pergi = self.tiket_pergi_spin.value()
        if tiket_pergi > 0:
            items.append({
                'uraian': 'Tiket Pergi',
                'volume': orang,
                'satuan': 'orang',
                'harga_satuan': tiket_pergi,
                'jumlah': tiket_pergi * orang,
            })

        tiket_pulang = self.tiket_pulang_spin.value()
        if tiket_pulang > 0:
            items.append({
                'uraian': 'Tiket Pulang',
                'volume': orang,
                'satuan': 'orang',
                'harga_satuan': tiket_pulang,
                'jumlah': tiket_pulang * orang,
            })

        # Transport bandara
        transport_bandara = self.transport_bandara_spin.value()
        if transport_bandara > 0:
            items.append({
                'uraian': 'Transport Bandara/Stasiun (PP)',
                'volume': orang,
                'satuan': 'orang',
                'harga_satuan': transport_bandara,
                'jumlah': transport_bandara * orang,
            })

        # Transport lokal
        transport_lokal = self.transport_lokal_spin.value()
        if transport_lokal > 0 and hari > 0:
            items.append({
                'uraian': 'Transport Lokal',
                'volume': hari * orang,
                'satuan': 'OH',
                'harga_satuan': transport_lokal,
                'jumlah': transport_lokal * hari * orang,
            })

        # Penginapan
        hotel = self.hotel_spin.value()
        if hotel > 0 and malam > 0:
            items.append({
                'uraian': 'Penginapan/Hotel',
                'volume': malam * orang,
                'satuan': 'malam',
                'harga_satuan': hotel,
                'jumlah': hotel * malam * orang,
            })

        # Uang harian
        harian = self.harian_spin.value()
        if harian > 0 and hari > 0:
            items.append({
                'uraian': 'Uang Harian',
                'volume': hari * orang,
                'satuan': 'OH',
                'harga_satuan': harian,
                'jumlah': harian * hari * orang,
            })

        # Representasi
        representasi = self.representasi_spin.value()
        if representasi > 0:
            items.append({
                'uraian': 'Uang Representasi',
                'volume': orang,
                'satuan': 'orang',
                'harga_satuan': representasi,
                'jumlah': representasi * orang,
            })

        # Lainnya
        lainnya = self.lainnya_spin.value()
        if lainnya > 0:
            ket = self.lainnya_ket.text() or 'Biaya Lain-lain'
            items.append({
                'uraian': ket,
                'volume': 1,
                'satuan': 'paket',
                'harga_satuan': lainnya,
                'jumlah': lainnya,
            })

        return items
