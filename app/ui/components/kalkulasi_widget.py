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
- Scrollable layout untuk akses mudah
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
        """Setup widget UI with scroll area."""
        self.setObjectName("kalkulasiWidget")
        self.setStyleSheet("""
            #kalkulasiWidget {
                background-color: #ffffff;
                border-radius: 8px;
            }
        """)

        # Main layout for the frame
        frame_layout = QVBoxLayout(self)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        # Scroll area to make everything scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)

        # Content widget inside scroll area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # ========== SECTION 1: Perhitungan Tambah/Kurang (Table Format) ==========
        calc_frame = QFrame()
        calc_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        calc_layout = QVBoxLayout(calc_frame)
        calc_layout.setContentsMargins(10, 10, 10, 10)
        calc_layout.setSpacing(8)

        # Header
        header = QLabel("💰 Perhitungan Tambah/Kurang")
        header.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #2c3e50;
            background-color: transparent;
        """)
        calc_layout.addWidget(header)

        # Table for calculation
        self.calc_table = QTableWidget()
        self.calc_table.setRowCount(3)
        self.calc_table.setColumnCount(2)
        self.calc_table.setHorizontalHeaderLabels(["Keterangan", "Nilai"])
        self.calc_table.verticalHeader().setVisible(False)
        self.calc_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.calc_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.calc_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.calc_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.calc_table.setMinimumHeight(120)
        self.calc_table.setMaximumHeight(120)
        self.calc_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                font-size: 12px;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
                font-size: 11px;
                border: none;
            }
        """)

        # Row 0: Uang Muka
        self.calc_table.setItem(0, 0, QTableWidgetItem("Uang Muka"))
        self.um_input = QDoubleSpinBox()
        self.um_input.setRange(0, 999999999999)
        self.um_input.setDecimals(0)
        self.um_input.setPrefix("Rp ")
        self.um_input.setGroupSeparatorShown(True)
        self.um_input.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #3498db;
                border-radius: 3px;
                padding: 4px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.um_input.valueChanged.connect(self._on_value_changed)
        self.calc_table.setCellWidget(0, 1, self.um_input)

        # Row 1: Realisasi
        self.calc_table.setItem(1, 0, QTableWidgetItem("Realisasi"))
        self.real_input = QDoubleSpinBox()
        self.real_input.setRange(0, 999999999999)
        self.real_input.setDecimals(0)
        self.real_input.setPrefix("Rp ")
        self.real_input.setGroupSeparatorShown(True)
        self.real_input.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #9b59b6;
                border-radius: 3px;
                padding: 4px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.real_input.valueChanged.connect(self._on_value_changed)
        self.calc_table.setCellWidget(1, 1, self.real_input)

        # Row 2: Selisih
        selisih_item = QTableWidgetItem("SELISIH")
        selisih_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.calc_table.setItem(2, 0, selisih_item)
        self.selisih_item = QTableWidgetItem("Rp 0")
        self.selisih_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.selisih_item.setTextAlignment(Qt.AlignCenter)
        self.calc_table.setItem(2, 1, self.selisih_item)

        calc_layout.addWidget(self.calc_table)

        # Result indicator
        self.result_frame = QFrame()
        self.result_frame.setMinimumHeight(50)
        self.result_frame.setMaximumHeight(50)
        self.result_frame.setStyleSheet("""
            QFrame {
                background-color: #27ae60;
                border-radius: 6px;
            }
        """)
        result_layout = QHBoxLayout(self.result_frame)
        result_layout.setContentsMargins(10, 5, 10, 5)

        self.result_label = QLabel("✓ PAS / NIHIL")
        self.result_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #ffffff;
            background-color: transparent;
        """)
        result_layout.addWidget(self.result_label)

        result_layout.addStretch()

        self.action_label = QLabel("Lanjut ke pembuatan SPBY")
        self.action_label.setStyleSheet("""
            font-size: 10px;
            color: rgba(255, 255, 255, 0.9);
            background-color: transparent;
        """)
        result_layout.addWidget(self.action_label)

        calc_layout.addWidget(self.result_frame)

        main_layout.addWidget(calc_frame)

        # ========== SECTION 2: Rincian Barang/Jasa (if enabled) ==========
        if self._show_rincian:
            self._setup_rincian_section(main_layout)

        main_layout.addStretch()

        scroll_area.setWidget(content_widget)
        frame_layout.addWidget(scroll_area)

    def _setup_rincian_section(self, parent_layout):
        """Setup rincian barang/jasa section."""
        rincian_frame = QFrame()
        rincian_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        rincian_layout = QVBoxLayout(rincian_frame)
        rincian_layout.setContentsMargins(10, 10, 10, 10)
        rincian_layout.setSpacing(8)

        # Header with add button
        header_layout = QHBoxLayout()
        header = QLabel("📋 Rincian Barang/Jasa")
        header.setStyleSheet("font-size: 12px; font-weight: bold; color: #2c3e50; background-color: transparent;")
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
        self.input_form.setStyleSheet("background-color: #e8f4fc; border-radius: 4px; padding: 5px;")
        form_layout = QVBoxLayout(self.input_form)
        form_layout.setContentsMargins(8, 8, 8, 8)
        form_layout.setSpacing(5)

        # Row 1: Uraian
        uraian_row = QHBoxLayout()
        uraian_row.addWidget(QLabel("Uraian:"))
        self.uraian_edit = QLineEdit()
        self.uraian_edit.setPlaceholderText("Nama barang/jasa...")
        self.uraian_edit.setStyleSheet("padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
        uraian_row.addWidget(self.uraian_edit)
        form_layout.addLayout(uraian_row)

        # Row 2: Volume, Satuan, Harga
        detail_row = QHBoxLayout()

        detail_row.addWidget(QLabel("Vol:"))
        self.volume_spin = QSpinBox()
        self.volume_spin.setRange(1, 9999)
        self.volume_spin.setFixedWidth(60)
        detail_row.addWidget(self.volume_spin)

        detail_row.addWidget(QLabel("Satuan:"))
        self.satuan_combo = QComboBox()
        self.satuan_combo.setEditable(True)
        self.satuan_combo.addItems(["pkt", "unit", "bh", "org", "set", "ls", "keg"])
        self.satuan_combo.setFixedWidth(70)
        detail_row.addWidget(self.satuan_combo)

        detail_row.addWidget(QLabel("Harga:"))
        self.harga_spin = QDoubleSpinBox()
        self.harga_spin.setRange(0, 999999999)
        self.harga_spin.setDecimals(0)
        self.harga_spin.setPrefix("Rp ")
        self.harga_spin.setFixedWidth(120)
        detail_row.addWidget(self.harga_spin)

        detail_row.addStretch()

        add_item_btn = QPushButton("OK")
        add_item_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; padding: 5px 15px; border-radius: 3px; }
            QPushButton:hover { background-color: #1e8449; }
        """)
        add_item_btn.clicked.connect(self._add_rincian_item)
        detail_row.addWidget(add_item_btn)

        form_layout.addLayout(detail_row)
        rincian_layout.addWidget(self.input_form)

        # Rincian table
        self.rincian_table = QTableWidget()
        self.rincian_table.setColumnCount(5)
        self.rincian_table.setHorizontalHeaderLabels(["Uraian", "Vol", "Sat", "Harga", "Jumlah"])
        self.rincian_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.rincian_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.rincian_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.rincian_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.rincian_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.rincian_table.setColumnWidth(1, 45)
        self.rincian_table.setColumnWidth(2, 45)
        self.rincian_table.setColumnWidth(3, 90)
        self.rincian_table.setColumnWidth(4, 90)
        self.rincian_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.rincian_table.setMinimumHeight(100)
        self.rincian_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                font-size: 11px;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 6px;
                font-weight: bold;
                font-size: 10px;
                border: none;
            }
        """)
        rincian_layout.addWidget(self.rincian_table)

        # Bottom row: Delete button and Total
        bottom_layout = QHBoxLayout()

        del_btn = QPushButton("Hapus")
        del_btn.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; padding: 4px 10px; border-radius: 3px; font-size: 10px; }
            QPushButton:hover { background-color: #c0392b; }
        """)
        del_btn.clicked.connect(self._delete_rincian_item)
        bottom_layout.addWidget(del_btn)

        bottom_layout.addStretch()

        total_label = QLabel("TOTAL:")
        total_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #2c3e50; background-color: transparent;")
        bottom_layout.addWidget(total_label)

        self.rincian_total_label = QLabel("Rp 0")
        self.rincian_total_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #27ae60; background-color: transparent;")
        bottom_layout.addWidget(self.rincian_total_label)

        rincian_layout.addLayout(bottom_layout)

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

        # Update selisih in table
        self.selisih_item.setText(selisih_text)
        if result_type == "KURANG_BAYAR":
            self.selisih_item.setForeground(QColor("#e74c3c"))
        elif result_type == "LEBIH_BAYAR":
            self.selisih_item.setForeground(QColor("#f39c12"))
        else:
            self.selisih_item.setForeground(QColor("#27ae60"))

        # Update result frame
        self.result_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {style['text_bg']};
                border-radius: 6px;
            }}
        """)

        self.result_label.setText(f"{style['icon']} {style['label']}")
        self.action_label.setText(style['action'])

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
                    border-radius: 3px;
                    padding: 4px;
                    font-size: 12px;
                    color: #7f8c8d;
                }
            """
        else:
            style = """
                QDoubleSpinBox {
                    border: 1px solid #3498db;
                    border-radius: 3px;
                    padding: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """

        self.um_input.setStyleSheet(style)
        self.real_input.setStyleSheet(style)
