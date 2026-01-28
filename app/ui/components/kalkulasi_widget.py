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
    QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from typing import Dict, Any, Optional, List

from .rincian_kalkulasi_widget import RincianKalkulasiWidget, format_rupiah, terbilang


class KalkulasiWidget(QFrame):
    """
    Widget untuk perhitungan selisih uang muka vs realisasi.

    Signals:
        nilai_changed(): Emitted when any value changes
    """

    nilai_changed = Signal()

    RESULT_STYLES = {
        "KURANG_BAYAR": {
            "bg": "#fdeaea",
            "color": "#e74c3c",
            "border": "#e74c3c",
            "icon": "^",
            "label": "KURANG BAYAR",
            "action": "Ajukan pembayaran tambahan"
        },
        "LEBIH_BAYAR": {
            "bg": "#fef5e7",
            "color": "#f39c12",
            "border": "#f39c12",
            "icon": "v",
            "label": "LEBIH BAYAR",
            "action": "Kembalikan kelebihan ke kas"
        },
        "PAS": {
            "bg": "#e8f8f0",
            "color": "#27ae60",
            "border": "#27ae60",
            "icon": "=",
            "label": "PAS / NIHIL",
            "action": "Lanjut ke SPBY"
        }
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._uang_muka = 0.0
        self._realisasi = 0.0

        self._setup_ui()
        self._add_shadow()
        self._calculate()

    def _setup_ui(self):
        """Setup widget UI."""
        self.setObjectName("kalkulasiWidget")
        self.setStyleSheet("""
            #kalkulasiWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)

        # Header
        header = QLabel("Perhitungan Tambah/Kurang")
        header.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        """)
        main_layout.addWidget(header)

        # Input rows
        input_layout = QGridLayout()
        input_layout.setSpacing(10)

        # Uang Muka
        um_label = QLabel("Uang Muka Diterima")
        um_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        input_layout.addWidget(um_label, 0, 0)

        self.um_input = QDoubleSpinBox()
        self.um_input.setRange(0, 999999999999)
        self.um_input.setDecimals(0)
        self.um_input.setPrefix("Rp ")
        self.um_input.setGroupSeparatorShown(True)
        self.um_input.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #f8f9fa;
                border: 1px solid #dcdfe6;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                color: #2c3e50;
            }
            QDoubleSpinBox:focus {
                border-color: #3498db;
            }
        """)
        self.um_input.valueChanged.connect(self._on_value_changed)
        input_layout.addWidget(self.um_input, 0, 1)

        # Realisasi
        real_label = QLabel("Total Realisasi")
        real_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        input_layout.addWidget(real_label, 1, 0)

        self.real_input = QDoubleSpinBox()
        self.real_input.setRange(0, 999999999999)
        self.real_input.setDecimals(0)
        self.real_input.setPrefix("Rp ")
        self.real_input.setGroupSeparatorShown(True)
        self.real_input.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #ffffff;
                border: 1px solid #dcdfe6;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                color: #2c3e50;
            }
            QDoubleSpinBox:focus {
                border-color: #3498db;
            }
        """)
        self.real_input.valueChanged.connect(self._on_value_changed)
        input_layout.addWidget(self.real_input, 1, 1)

        # Selisih (read-only)
        selisih_label = QLabel("Selisih (Realisasi - Uang Muka)")
        selisih_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        input_layout.addWidget(selisih_label, 2, 0)

        self.selisih_display = QLabel("Rp 0")
        self.selisih_display.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        """)
        input_layout.addWidget(self.selisih_display, 2, 1)

        main_layout.addLayout(input_layout)

        # Result box
        self.result_frame = QFrame()
        self.result_frame.setStyleSheet("""
            background-color: #e8f8f0;
            border: 2px solid #27ae60;
            border-radius: 8px;
            padding: 15px;
        """)

        result_layout = QVBoxLayout(self.result_frame)
        result_layout.setSpacing(8)

        # Result label
        self.result_label = QLabel("PAS / NIHIL")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #27ae60;
        """)
        result_layout.addWidget(self.result_label)

        # Action hint
        self.action_label = QLabel("Lanjut ke SPBY")
        self.action_label.setAlignment(Qt.AlignCenter)
        self.action_label.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
        """)
        result_layout.addWidget(self.action_label)

        main_layout.addWidget(self.result_frame)

        # Summary
        summary_layout = QHBoxLayout()

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        summary_layout.addWidget(self.summary_label)

        summary_layout.addStretch()

        main_layout.addLayout(summary_layout)

    def _add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

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
            self.selisih_display.setText(format_rupiah(selisih))
        else:
            self.selisih_display.setText(f"- {format_rupiah(abs(selisih))}")

        # Determine result type
        if selisih > 0:
            result_type = "KURANG_BAYAR"
        elif selisih < 0:
            result_type = "LEBIH_BAYAR"
        else:
            result_type = "PAS"

        # Update result display
        style = self.RESULT_STYLES[result_type]
        self.result_frame.setStyleSheet(f"""
            background-color: {style['bg']};
            border: 2px solid {style['border']};
            border-radius: 8px;
            padding: 15px;
        """)
        self.result_label.setText(style['label'])
        self.result_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {style['color']};
        """)
        self.action_label.setText(style['action'])

        # Update selisih display color
        self.selisih_display.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {style['color']};
            padding: 10px;
            background-color: {style['bg']};
            border-radius: 5px;
        """)

        # Update summary
        if selisih > 0:
            self.summary_label.setText(f"Perlu pembayaran tambahan sebesar {format_rupiah(selisih)}")
        elif selisih < 0:
            self.summary_label.setText(f"Kelebihan {format_rupiah(abs(selisih))} harus dikembalikan ke kas")
        else:
            self.summary_label.setText("Uang muka sama dengan realisasi")

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
        }

    def set_readonly(self, readonly: bool):
        """Set inputs to readonly mode."""
        self.um_input.setReadOnly(readonly)
        self.real_input.setReadOnly(readonly)

        if readonly:
            style = """
                QDoubleSpinBox {
                    background-color: #f5f6fa;
                    border: 1px solid #ecf0f1;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 14px;
                    color: #7f8c8d;
                }
            """
        else:
            style = """
                QDoubleSpinBox {
                    background-color: #ffffff;
                    border: 1px solid #dcdfe6;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 14px;
                    color: #2c3e50;
                }
                QDoubleSpinBox:focus {
                    border-color: #3498db;
                }
            """

        self.um_input.setStyleSheet(style)
        self.real_input.setStyleSheet(style)
