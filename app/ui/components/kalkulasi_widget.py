"""
PPK DOCUMENT FACTORY - Kalkulasi Widget Component
==================================================
Widget untuk menghitung dan menampilkan selisih uang muka vs realisasi.

Features:
- Input rincian barang/jasa untuk kuitansi uang muka
- Auto-calculate total dari rincian
- Perhitungan selisih uang muka vs realisasi
- Visual indicator (KURANG/LEBIH/PAS)
- Formatted currency display dengan terbilang
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QLineEdit, QDoubleSpinBox,
    QGraphicsDropShadowEffect, QSizePolicy, QTabWidget,
    QScrollArea, QSpinBox, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from typing import Dict, Any, Optional, List


def format_rupiah(value: float) -> str:
    """Format angka ke format Rupiah."""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


def terbilang(n: float) -> str:
    """Konversi angka ke terbilang dalam Bahasa Indonesia."""
    if n == 0:
        return "nol"

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


class KalkulasiWidget(QFrame):
    """
    Widget untuk perhitungan selisih uang muka vs realisasi.

    Signals:
        nilai_changed(): Emitted when any value changes
    """

    nilai_changed = Signal()

    RESULT_STYLES = {
        "KURANG_BAYAR": {
            "bg": "#ffffff",
            "text_bg": "#e74c3c",
            "color": "#ffffff",
            "border": "#e74c3c",
            "icon": "↑",
            "label": "KURANG BAYAR",
            "action": "Ajukan pembayaran tambahan"
        },
        "LEBIH_BAYAR": {
            "bg": "#ffffff",
            "text_bg": "#f39c12",
            "color": "#ffffff",
            "border": "#f39c12",
            "icon": "↓",
            "label": "LEBIH BAYAR",
            "action": "Kembalikan kelebihan ke kas negara"
        },
        "PAS": {
            "bg": "#ffffff",
            "text_bg": "#27ae60",
            "color": "#ffffff",
            "border": "#27ae60",
            "icon": "✓",
            "label": "PAS / NIHIL",
            "action": "Lanjut ke pembuatan SPBY"
        }
    }

    def __init__(self, show_rincian: bool = False, parent=None):
        super().__init__(parent)
        self._uang_muka = 0.0
        self._realisasi = 0.0
        self._show_rincian = show_rincian
        self._rincian_items = []

        self._setup_ui()
        self._calculate()

    def _setup_ui(self):
        """Setup widget UI."""
        self.setObjectName("kalkulasiWidget")
        self.setStyleSheet("""
            #kalkulasiWidget {
                background-color: #ffffff;
                border-radius: 8px;
            }
            #kalkulasiWidget QLabel {
                color: #2c3e50;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # ========== SECTION 1: Input Uang Muka & Realisasi ==========
        calc_section = QFrame()
        calc_section.setObjectName("calcSection")
        calc_section.setStyleSheet("""
            #calcSection {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        calc_layout = QVBoxLayout(calc_section)
        calc_layout.setSpacing(10)

        # Header
        header = QLabel("💰 Perhitungan Tambah/Kurang")
        header.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            background-color: transparent;
            padding: 5px 0;
        """)
        calc_layout.addWidget(header)

        # Input Grid
        input_frame = QFrame()
        input_layout = QGridLayout(input_frame)
        input_layout.setSpacing(8)
        input_layout.setContentsMargins(0, 0, 0, 0)

        # Uang Muka Row
        um_label = QLabel("Uang Muka Diterima:")
        um_label.setStyleSheet("font-size: 12px; color: #2c3e50; font-weight: 500; background-color: transparent;")
        input_layout.addWidget(um_label, 0, 0)

        self.um_input = QDoubleSpinBox()
        self.um_input.setRange(0, 999999999999)
        self.um_input.setDecimals(0)
        self.um_input.setPrefix("Rp ")
        self.um_input.setGroupSeparatorShown(True)
        self.um_input.setMinimumHeight(36)
        self.um_input.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #ffffff;
                border: 2px solid #3498db;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
            QDoubleSpinBox:focus {
                border-color: #2980b9;
            }
        """)
        self.um_input.valueChanged.connect(self._on_value_changed)
        input_layout.addWidget(self.um_input, 0, 1)

        # Realisasi Row
        real_label = QLabel("Total Realisasi:")
        real_label.setStyleSheet("font-size: 12px; color: #2c3e50; font-weight: 500; background-color: transparent;")
        input_layout.addWidget(real_label, 1, 0)

        self.real_input = QDoubleSpinBox()
        self.real_input.setRange(0, 999999999999)
        self.real_input.setDecimals(0)
        self.real_input.setPrefix("Rp ")
        self.real_input.setGroupSeparatorShown(True)
        self.real_input.setMinimumHeight(36)
        self.real_input.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #ffffff;
                border: 2px solid #9b59b6;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
            QDoubleSpinBox:focus {
                border-color: #7d3c98;
            }
        """)
        self.real_input.valueChanged.connect(self._on_value_changed)
        input_layout.addWidget(self.real_input, 1, 1)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #bdc3c7;")
        separator.setFixedHeight(1)
        input_layout.addWidget(separator, 2, 0, 1, 2)

        # Selisih Row
        selisih_label = QLabel("SELISIH:")
        selisih_label.setStyleSheet("font-size: 13px; color: #2c3e50; font-weight: bold; background-color: transparent;")
        input_layout.addWidget(selisih_label, 3, 0)

        self.selisih_display = QLabel("Rp 0")
        self.selisih_display.setMinimumHeight(36)
        self.selisih_display.setAlignment(Qt.AlignCenter)
        self.selisih_display.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #27ae60;
            padding: 6px 10px;
            background-color: #e8f8f0;
            border-radius: 6px;
            border: 2px solid #27ae60;
        """)
        input_layout.addWidget(self.selisih_display, 3, 1)

        calc_layout.addWidget(input_frame)
        main_layout.addWidget(calc_section)

        # ========== SECTION 2: Result Box ==========
        self.result_frame = QFrame()
        self.result_frame.setMinimumHeight(80)
        self.result_frame.setStyleSheet("""
            QFrame {
                background-color: #27ae60;
                border-radius: 10px;
            }
        """)

        result_layout = QVBoxLayout(self.result_frame)
        result_layout.setContentsMargins(15, 12, 15, 12)
        result_layout.setSpacing(5)

        # Result label (status)
        self.result_label = QLabel("✓ PAS / NIHIL")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            background-color: transparent;
        """)
        result_layout.addWidget(self.result_label)

        # Action hint
        self.action_label = QLabel("Lanjut ke pembuatan SPBY")
        self.action_label.setAlignment(Qt.AlignCenter)
        self.action_label.setStyleSheet("""
            font-size: 12px;
            color: rgba(255, 255, 255, 0.9);
            background-color: transparent;
        """)
        result_layout.addWidget(self.action_label)

        main_layout.addWidget(self.result_frame)

        # ========== SECTION 3: Summary ==========
        self.summary_label = QLabel("Uang muka sama dengan realisasi")
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.summary_label.setStyleSheet("""
            font-size: 11px;
            color: #7f8c8d;
            padding: 5px;
            font-style: italic;
        """)
        main_layout.addWidget(self.summary_label)

        # ========== SECTION 4: Rincian (optional) ==========
        if self._show_rincian:
            self._setup_rincian_section(main_layout)

        main_layout.addStretch()

    def _setup_rincian_section(self, parent_layout):
        """Setup rincian barang/jasa section."""
        rincian_frame = QFrame()
        rincian_frame.setObjectName("rincianSection")
        rincian_frame.setStyleSheet("""
            #rincianSection {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        rincian_layout = QVBoxLayout(rincian_frame)
        rincian_layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()
        header = QLabel("📋 Rincian Barang/Jasa")
        header.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50; background-color: transparent;")
        header_layout.addWidget(header)

        header_layout.addStretch()

        add_btn = QPushButton("+ Tambah")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 12px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        add_btn.clicked.connect(self._toggle_input_form)
        header_layout.addWidget(add_btn)

        rincian_layout.addLayout(header_layout)

        # Input form (hidden by default)
        self.input_form = QFrame()
        self.input_form.setVisible(False)
        form_layout = QHBoxLayout(self.input_form)
        form_layout.setContentsMargins(0, 5, 0, 5)
        form_layout.setSpacing(5)

        self.uraian_edit = QLineEdit()
        self.uraian_edit.setPlaceholderText("Uraian")
        self.uraian_edit.setStyleSheet("padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
        form_layout.addWidget(self.uraian_edit, 3)

        self.volume_spin = QSpinBox()
        self.volume_spin.setRange(1, 9999)
        self.volume_spin.setStyleSheet("padding: 5px;")
        form_layout.addWidget(self.volume_spin)

        self.satuan_combo = QComboBox()
        self.satuan_combo.setEditable(True)
        self.satuan_combo.addItems(["pkt", "unit", "bh", "org", "set"])
        form_layout.addWidget(self.satuan_combo)

        self.harga_spin = QDoubleSpinBox()
        self.harga_spin.setRange(0, 999999999)
        self.harga_spin.setDecimals(0)
        self.harga_spin.setPrefix("Rp ")
        form_layout.addWidget(self.harga_spin)

        add_item_btn = QPushButton("OK")
        add_item_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; padding: 5px 10px; border-radius: 3px; }
            QPushButton:hover { background-color: #1e8449; }
        """)
        add_item_btn.clicked.connect(self._add_rincian_item)
        form_layout.addWidget(add_item_btn)

        rincian_layout.addWidget(self.input_form)

        # Table
        self.rincian_table = QTableWidget()
        self.rincian_table.setColumnCount(5)
        self.rincian_table.setHorizontalHeaderLabels(["Uraian", "Vol", "Sat", "Harga", "Jumlah"])
        self.rincian_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.rincian_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.rincian_table.setMaximumHeight(120)
        self.rincian_table.setStyleSheet("""
            QTableWidget { border: 1px solid #ddd; font-size: 11px; }
            QHeaderView::section { background-color: #ecf0f1; padding: 4px; font-weight: bold; }
        """)
        rincian_layout.addWidget(self.rincian_table)

        # Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()

        del_btn = QPushButton("Hapus")
        del_btn.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; padding: 4px 10px; border-radius: 3px; font-size: 10px; }
        """)
        del_btn.clicked.connect(self._delete_rincian_item)
        total_layout.addWidget(del_btn)

        total_layout.addWidget(QLabel("TOTAL:"))
        self.rincian_total_label = QLabel("Rp 0")
        self.rincian_total_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        total_layout.addWidget(self.rincian_total_label)

        rincian_layout.addLayout(total_layout)

        parent_layout.addWidget(rincian_frame)

    def _toggle_input_form(self):
        """Toggle input form visibility."""
        if hasattr(self, 'input_form'):
            self.input_form.setVisible(not self.input_form.isVisible())

    def _add_rincian_item(self):
        """Add rincian item."""
        if not hasattr(self, 'uraian_edit'):
            return

        uraian = self.uraian_edit.text().strip()
        if not uraian:
            return

        volume = self.volume_spin.value()
        satuan = self.satuan_combo.currentText()
        harga = self.harga_spin.value()
        jumlah = volume * harga

        # Add to table
        row = self.rincian_table.rowCount()
        self.rincian_table.insertRow(row)
        self.rincian_table.setItem(row, 0, QTableWidgetItem(uraian))
        self.rincian_table.setItem(row, 1, QTableWidgetItem(str(volume)))
        self.rincian_table.setItem(row, 2, QTableWidgetItem(satuan))
        self.rincian_table.setItem(row, 3, QTableWidgetItem(format_rupiah(harga)))
        self.rincian_table.setItem(row, 4, QTableWidgetItem(format_rupiah(jumlah)))

        # Add to list
        self._rincian_items.append({
            'uraian': uraian, 'volume': volume, 'satuan': satuan,
            'harga_satuan': harga, 'jumlah': jumlah
        })

        # Clear and update
        self.uraian_edit.clear()
        self.volume_spin.setValue(1)
        self.harga_spin.setValue(0)
        self._update_rincian_total()

    def _delete_rincian_item(self):
        """Delete selected rincian."""
        if not hasattr(self, 'rincian_table'):
            return

        rows = set(item.row() for item in self.rincian_table.selectedItems())
        for row in sorted(rows, reverse=True):
            self.rincian_table.removeRow(row)
            if row < len(self._rincian_items):
                self._rincian_items.pop(row)
        self._update_rincian_total()

    def _update_rincian_total(self):
        """Update rincian total."""
        if hasattr(self, 'rincian_total_label'):
            total = sum(item['jumlah'] for item in self._rincian_items)
            self.rincian_total_label.setText(format_rupiah(total))

    def _on_value_changed(self):
        """Handle value change."""
        self._uang_muka = self.um_input.value()
        self._realisasi = self.real_input.value()
        self._calculate()
        self.nilai_changed.emit()

    def _calculate(self):
        """Calculate selisih and update display."""
        selisih = self._realisasi - self._uang_muka

        # Update selisih display
        if selisih >= 0:
            selisih_text = format_rupiah(selisih)
        else:
            selisih_text = f"- {format_rupiah(abs(selisih))}"

        # Determine result type
        if selisih > 0:
            result_type = "KURANG_BAYAR"
        elif selisih < 0:
            result_type = "LEBIH_BAYAR"
        else:
            result_type = "PAS"

        style = self.RESULT_STYLES[result_type]

        # Update selisih display
        self.selisih_display.setText(selisih_text)
        if result_type == "KURANG_BAYAR":
            self.selisih_display.setStyleSheet("""
                font-size: 16px; font-weight: bold; color: #e74c3c;
                padding: 6px 10px; background-color: #fdeaea;
                border-radius: 6px; border: 2px solid #e74c3c;
            """)
        elif result_type == "LEBIH_BAYAR":
            self.selisih_display.setStyleSheet("""
                font-size: 16px; font-weight: bold; color: #f39c12;
                padding: 6px 10px; background-color: #fef5e7;
                border-radius: 6px; border: 2px solid #f39c12;
            """)
        else:
            self.selisih_display.setStyleSheet("""
                font-size: 16px; font-weight: bold; color: #27ae60;
                padding: 6px 10px; background-color: #e8f8f0;
                border-radius: 6px; border: 2px solid #27ae60;
            """)

        # Update result frame - solid color background with white text
        self.result_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {style['text_bg']};
                border-radius: 10px;
            }}
        """)

        self.result_label.setText(f"{style['icon']} {style['label']}")
        self.result_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            background-color: transparent;
        """)

        self.action_label.setText(style['action'])
        self.action_label.setStyleSheet("""
            font-size: 12px;
            color: rgba(255, 255, 255, 0.9);
            background-color: transparent;
        """)

        # Update summary
        if selisih > 0:
            self.summary_label.setText(f"Perlu pembayaran tambahan sebesar {format_rupiah(selisih)}")
        elif selisih < 0:
            self.summary_label.setText(f"Kelebihan {format_rupiah(abs(selisih))} harus dikembalikan ke kas negara")
        else:
            self.summary_label.setText("Uang muka sama dengan realisasi - tidak ada selisih")

    def set_uang_muka(self, value: float):
        """Set uang muka value."""
        self.um_input.setValue(value)

    def set_realisasi(self, value: float):
        """Set realisasi value."""
        self.real_input.setValue(value)

    def set_values(self, uang_muka: float, realisasi: float):
        """Set both values at once."""
        self.um_input.blockSignals(True)
        self.real_input.blockSignals(True)

        self.um_input.setValue(uang_muka)
        self.real_input.setValue(realisasi)

        self.um_input.blockSignals(False)
        self.real_input.blockSignals(False)

        self._uang_muka = uang_muka
        self._realisasi = realisasi
        self._calculate()

    def get_values(self) -> Dict[str, float]:
        """Get current values."""
        return {
            'uang_muka': self._uang_muka,
            'realisasi': self._realisasi,
            'selisih': self._realisasi - self._uang_muka,
        }

    def get_result(self) -> Dict[str, Any]:
        """Get calculation result."""
        selisih = self._realisasi - self._uang_muka

        if selisih > 0:
            status = "KURANG_BAYAR"
        elif selisih < 0:
            status = "LEBIH_BAYAR"
        else:
            status = "PAS"

        return {
            'uang_muka': self._uang_muka,
            'realisasi': self._realisasi,
            'selisih': selisih,
            'selisih_abs': abs(selisih),
            'status': status,
            'rincian_items': self._rincian_items,
        }

    def get_rincian_items(self) -> List[Dict]:
        """Get rincian items."""
        return self._rincian_items

    def set_readonly(self, readonly: bool):
        """Set inputs to readonly mode."""
        self.um_input.setReadOnly(readonly)
        self.real_input.setReadOnly(readonly)

        if readonly:
            style = """
                QDoubleSpinBox {
                    background-color: #f5f6fa;
                    border: 1px solid #ecf0f1;
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-size: 14px;
                    color: #7f8c8d;
                }
            """
        else:
            style = """
                QDoubleSpinBox {
                    background-color: #ffffff;
                    border: 2px solid #3498db;
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #2c3e50;
                }
                QDoubleSpinBox:focus {
                    border-color: #2980b9;
                }
            """

        self.um_input.setStyleSheet(style)
        self.real_input.setStyleSheet(style)
