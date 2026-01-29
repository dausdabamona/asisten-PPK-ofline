"""
PPK DOCUMENT FACTORY - Rincian Kalkulasi Widget Component
==========================================================
Widget untuk menginput rincian barang/jasa dengan kalkulasi otomatis.

Format sesuai Lembar Permintaan:
- No, Nama Barang, Spesifikasi, Volume, Satuan, Harga Satuan, Total, Keterangan

Features:
- Tabel input rincian barang/jasa
- Auto-calculate total per item dan grand total
- Bisa generate data untuk Lembar Permintaan, Kuitansi Uang Muka, dan Kuitansi Rampung
- Hasil bisa ditampilkan dalam terbilang
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QLineEdit, QDoubleSpinBox,
    QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QGraphicsDropShadowEffect, QSizePolicy, QMessageBox,
    QComboBox, QAbstractItemView, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from typing import Dict, Any, List, Optional


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


class RincianKalkulasiWidget(QFrame):
    """
    Widget untuk input rincian barang/jasa dan kalkulasi otomatis.

    Modes:
        - editable (default): Full edit, add, delete - untuk Lembar Permintaan
        - inline_edit: Edit volume/harga di tabel - untuk Kuitansi Rampung
        - readonly: Hanya tampil, tidak bisa edit - untuk Kuitansi Uang Muka

    Signals:
        total_changed(float): Emitted when total changes
        items_changed(): Emitted when items are modified
    """

    total_changed = Signal(float)
    items_changed = Signal()

    # Column indices
    COL_NO = 0
    COL_NAMA = 1
    COL_SPEK = 2
    COL_VOL = 3
    COL_SAT = 4
    COL_HARGA = 5
    COL_TOTAL = 6
    COL_KET = 7

    def __init__(self, title: str = "Rincian Barang/Jasa", editable: bool = True,
                 inline_edit: bool = False, parent=None):
        super().__init__(parent)
        self._title = title
        self._items: List[Dict[str, Any]] = []
        self._total = 0.0
        self._editable = editable
        self._inline_edit = inline_edit

        self._setup_ui()
        self._add_shadow()

        # Apply mode
        if not editable:
            self.set_readonly(True)

    def _setup_ui(self):
        """Setup widget UI."""
        self.setObjectName("rincianWidget")
        self.setStyleSheet("""
            #rincianWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()

        header = QLabel(self._title)
        header.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(header)

        header_layout.addStretch()

        # Add item button
        self.add_btn = QPushButton("+ Tambah Item")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 6px 15px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        self.add_btn.clicked.connect(self._add_item)
        header_layout.addWidget(self.add_btn)

        main_layout.addLayout(header_layout)

        # Input form for new item
        self.input_frame = QFrame()
        self.input_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        input_layout = QGridLayout(self.input_frame)
        input_layout.setSpacing(8)

        # Row 0: Nama Barang
        input_layout.addWidget(QLabel("Nama Barang:"), 0, 0)
        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText("Nama barang/jasa")
        self.nama_input.setStyleSheet(self._get_input_style())
        input_layout.addWidget(self.nama_input, 0, 1, 1, 3)

        # Row 1: Spesifikasi
        input_layout.addWidget(QLabel("Spesifikasi:"), 1, 0)
        self.spek_input = QLineEdit()
        self.spek_input.setPlaceholderText("Ukuran, merk, tipe, dll (opsional)")
        self.spek_input.setStyleSheet(self._get_input_style())
        input_layout.addWidget(self.spek_input, 1, 1, 1, 3)

        # Row 2: Volume + Satuan
        input_layout.addWidget(QLabel("Volume:"), 2, 0)
        self.volume_input = QSpinBox()
        self.volume_input.setRange(1, 9999)
        self.volume_input.setValue(1)
        self.volume_input.setStyleSheet(self._get_input_style())
        input_layout.addWidget(self.volume_input, 2, 1)

        input_layout.addWidget(QLabel("Satuan:"), 2, 2)
        self.satuan_input = QComboBox()
        self.satuan_input.setEditable(True)
        self.satuan_input.addItems(["Unit", "Buah", "Paket", "Set", "Lembar", "Orang", "Kg", "Liter", "Meter"])
        self.satuan_input.setStyleSheet(self._get_input_style())
        input_layout.addWidget(self.satuan_input, 2, 3)

        # Row 3: Harga Satuan
        input_layout.addWidget(QLabel("Harga Satuan:"), 3, 0)
        self.harga_input = QDoubleSpinBox()
        self.harga_input.setRange(0, 999999999999)
        self.harga_input.setDecimals(0)
        self.harga_input.setPrefix("Rp ")
        self.harga_input.setGroupSeparatorShown(True)
        self.harga_input.setStyleSheet(self._get_input_style())
        input_layout.addWidget(self.harga_input, 3, 1, 1, 2)

        # Row 4: Keterangan
        input_layout.addWidget(QLabel("Keterangan:"), 4, 0)
        self.ket_input = QLineEdit()
        self.ket_input.setPlaceholderText("Catatan tambahan (opsional)")
        self.ket_input.setStyleSheet(self._get_input_style())
        input_layout.addWidget(self.ket_input, 4, 1, 1, 2)

        # Add to table button
        add_to_table_btn = QPushButton("Tambahkan")
        add_to_table_btn.setCursor(Qt.PointingHandCursor)
        add_to_table_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        add_to_table_btn.clicked.connect(self._add_item_to_table)
        input_layout.addWidget(add_to_table_btn, 4, 3)

        main_layout.addWidget(self.input_frame)
        self.input_frame.hide()  # Initially hidden

        # Table with 8 columns
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "No", "Nama Barang", "Spesifikasi", "Volume", "Satuan", "Harga Satuan", "Total", "Keterangan"
        ])

        # Column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(self.COL_NO, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_NAMA, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_SPEK, QHeaderView.Interactive)
        header.setSectionResizeMode(self.COL_VOL, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_SAT, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_HARGA, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_TOTAL, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_KET, QHeaderView.Interactive)

        self.table.setColumnWidth(self.COL_NO, 35)
        self.table.setColumnWidth(self.COL_SPEK, 120)
        self.table.setColumnWidth(self.COL_VOL, 55)
        self.table.setColumnWidth(self.COL_SAT, 60)
        self.table.setColumnWidth(self.COL_HARGA, 100)
        self.table.setColumnWidth(self.COL_TOTAL, 100)
        self.table.setColumnWidth(self.COL_KET, 100)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #ecf0f1;
                border-radius: 4px;
                gridline-color: #ecf0f1;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #ecf0f1;
                font-weight: bold;
                color: #2c3e50;
                font-size: 11px;
            }
            QTableWidget::item:selected {
                background-color: #ebf5fb;
                color: #2c3e50;
            }
        """)
        self.table.setMinimumHeight(180)
        main_layout.addWidget(self.table)

        # Delete selected button
        delete_layout = QHBoxLayout()
        delete_layout.addStretch()

        self.delete_btn = QPushButton("Hapus Item Terpilih")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 6px 15px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.delete_btn.clicked.connect(self._delete_selected)
        delete_layout.addWidget(self.delete_btn)

        main_layout.addLayout(delete_layout)

        # Total section
        total_frame = QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f8f0;
                border: 1px solid #27ae60;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        total_layout = QVBoxLayout(total_frame)
        total_layout.setSpacing(5)

        # Total row
        total_row = QHBoxLayout()
        total_label = QLabel("TOTAL:")
        total_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        """)
        total_row.addWidget(total_label)

        total_row.addStretch()

        self.total_display = QLabel("Rp 0")
        self.total_display.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #27ae60;
        """)
        total_row.addWidget(self.total_display)

        total_layout.addLayout(total_row)

        # Terbilang
        self.terbilang_label = QLabel("( nol rupiah )")
        self.terbilang_label.setStyleSheet("""
            font-size: 11px;
            color: #7f8c8d;
            font-style: italic;
        """)
        self.terbilang_label.setWordWrap(True)
        total_layout.addWidget(self.terbilang_label)

        main_layout.addWidget(total_frame)

    def _add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

    def _get_input_style(self) -> str:
        """Get common input field style."""
        return """
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #ffffff;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border-color: #3498db;
            }
        """

    def _add_item(self):
        """Show/hide input form."""
        if self.input_frame.isVisible():
            self.input_frame.hide()
        else:
            self.input_frame.show()
            self.nama_input.setFocus()

    def _add_item_to_table(self):
        """Add item from input form to table."""
        nama = self.nama_input.text().strip()
        if not nama:
            QMessageBox.warning(self, "Validasi", "Nama barang/jasa wajib diisi")
            return

        spek = self.spek_input.text().strip()
        volume = self.volume_input.value()
        satuan = self.satuan_input.currentText()
        harga = self.harga_input.value()
        ket = self.ket_input.text().strip()
        jumlah = volume * harga

        # Add to internal list
        item = {
            'nama': nama,
            'spesifikasi': spek,
            'volume': volume,
            'satuan': satuan,
            'harga_satuan': harga,
            'jumlah': jumlah,
            'keterangan': ket,
        }
        self._items.append(item)

        # Add to table
        self._add_row_to_table(item)

        # Clear input
        self.nama_input.clear()
        self.spek_input.clear()
        self.volume_input.setValue(1)
        self.harga_input.setValue(0)
        self.ket_input.clear()

        # Update total
        self._update_total()

        # Emit signal
        self.items_changed.emit()

    def _add_row_to_table(self, item: Dict[str, Any]):
        """Add a single row to table."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, self.COL_NO, QTableWidgetItem(str(row + 1)))
        self.table.setItem(row, self.COL_NAMA, QTableWidgetItem(item.get('nama', '')))
        self.table.setItem(row, self.COL_SPEK, QTableWidgetItem(item.get('spesifikasi', '')))
        self.table.setItem(row, self.COL_VOL, QTableWidgetItem(str(item.get('volume', 0))))
        self.table.setItem(row, self.COL_SAT, QTableWidgetItem(item.get('satuan', '')))
        self.table.setItem(row, self.COL_HARGA, QTableWidgetItem(format_rupiah(item.get('harga_satuan', 0))))
        self.table.setItem(row, self.COL_TOTAL, QTableWidgetItem(format_rupiah(item.get('jumlah', 0))))
        self.table.setItem(row, self.COL_KET, QTableWidgetItem(item.get('keterangan', '')))

        # Center align some columns
        for col in [self.COL_NO, self.COL_VOL, self.COL_SAT]:
            self.table.item(row, col).setTextAlignment(Qt.AlignCenter)
        # Right align numbers
        for col in [self.COL_HARGA, self.COL_TOTAL]:
            self.table.item(row, col).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def _delete_selected(self):
        """Delete selected rows."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.information(self, "Info", "Pilih item yang akan dihapus")
            return

        # Remove from internal list (reverse order to maintain indices)
        for row in sorted(selected_rows, reverse=True):
            if row < len(self._items):
                self._items.pop(row)
            self.table.removeRow(row)

        # Renumber rows
        for i in range(self.table.rowCount()):
            self.table.setItem(i, self.COL_NO, QTableWidgetItem(str(i + 1)))
            self.table.item(i, self.COL_NO).setTextAlignment(Qt.AlignCenter)

        # Update total
        self._update_total()

        # Emit signal
        self.items_changed.emit()

    def _update_total(self):
        """Calculate and update total."""
        self._total = sum(item['jumlah'] for item in self._items)
        self.total_display.setText(format_rupiah(self._total))

        # Update terbilang
        terbilang_text = terbilang(self._total).strip()
        # Capitalize first letter and add "rupiah"
        if terbilang_text:
            terbilang_text = terbilang_text[0].upper() + terbilang_text[1:]
            if not terbilang_text.endswith("rupiah"):
                terbilang_text += " rupiah"
        self.terbilang_label.setText(f"( {terbilang_text} )")

        # Emit signal
        self.total_changed.emit(self._total)

    def get_items(self) -> List[Dict[str, Any]]:
        """Get all items."""
        return self._items.copy()

    def get_total(self) -> float:
        """Get current total."""
        return self._total

    def get_terbilang(self) -> str:
        """Get terbilang text."""
        return terbilang(self._total)

    def set_items(self, items: List[Dict[str, Any]]):
        """Set items from list."""
        # Clear table
        self.table.setRowCount(0)
        self._items.clear()

        # Add items
        for item in items:
            # Normalize item keys (support both 'nama' and 'uraian')
            normalized = {
                'nama': item.get('nama', item.get('uraian', '')),
                'spesifikasi': item.get('spesifikasi', ''),
                'volume': item.get('volume', 1),
                'satuan': item.get('satuan', 'unit'),
                'harga_satuan': item.get('harga_satuan', 0),
                'jumlah': item.get('jumlah', 0),
                'keterangan': item.get('keterangan', ''),
            }
            self._items.append(normalized)
            self._add_row_to_table(normalized)

        # Update total
        self._update_total()

    def clear(self):
        """Clear all items."""
        self.table.setRowCount(0)
        self._items.clear()
        self._update_total()

    def get_data_for_kuitansi(self) -> Dict[str, Any]:
        """Get formatted data for kuitansi document."""
        return {
            'rincian_items': self._items,
            'total': self._total,
            'total_rupiah': format_rupiah(self._total),
            'total_terbilang': self.get_terbilang(),
            'jumlah_item': len(self._items),
        }

    def set_readonly(self, readonly: bool = True):
        """Set widget to readonly mode (for Kuitansi Uang Muka)."""
        self._editable = not readonly

        # Hide add button and input form
        if hasattr(self, 'input_frame'):
            self.input_frame.hide()

        # Find and hide add/delete buttons
        if hasattr(self, 'add_btn'):
            self.add_btn.setVisible(not readonly)
        if hasattr(self, 'delete_btn'):
            self.delete_btn.setVisible(not readonly)

        # Disable table editing
        if readonly:
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            self.table.setEditTriggers(QAbstractItemView.DoubleClicked)

    def set_inline_edit(self, enabled: bool = True):
        """
        Enable inline editing mode (for Kuitansi Rampung).
        Allows editing volume and harga_satuan directly in table.
        """
        self._inline_edit = enabled

        if enabled:
            # Hide add button and form
            if hasattr(self, 'input_frame'):
                self.input_frame.hide()
            if hasattr(self, 'add_btn'):
                self.add_btn.hide()

            # Enable cell editing
            self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
            self.table.cellChanged.connect(self._on_cell_changed)
        else:
            try:
                self.table.cellChanged.disconnect(self._on_cell_changed)
            except RuntimeError:
                pass

    def _on_cell_changed(self, row: int, col: int):
        """Handle cell value changed for inline editing."""
        if not self._inline_edit or row >= len(self._items):
            return

        try:
            # Only allow editing volume (col 3) and harga_satuan (col 5)
            if col == self.COL_VOL:  # Volume
                new_volume = int(self.table.item(row, col).text())
                self._items[row]['volume'] = new_volume
            elif col == self.COL_HARGA:  # Harga satuan
                # Parse rupiah format
                text = self.table.item(row, col).text()
                text = text.replace("Rp", "").replace(".", "").replace(",", "").strip()
                new_harga = float(text) if text else 0
                self._items[row]['harga_satuan'] = new_harga

            # Recalculate jumlah
            volume = self._items[row]['volume']
            harga = self._items[row]['harga_satuan']
            jumlah = volume * harga
            self._items[row]['jumlah'] = jumlah

            # Update total column
            self.table.blockSignals(True)
            self.table.setItem(row, self.COL_TOTAL, QTableWidgetItem(format_rupiah(jumlah)))
            self.table.item(row, self.COL_TOTAL).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.blockSignals(False)

            # Update total
            self._update_total()
            self.items_changed.emit()

        except (ValueError, AttributeError):
            pass

    def load_from_db(self, db_manager, transaksi_id: int):
        """
        Load rincian items from database.

        Args:
            db_manager: PencairanManager instance
            transaksi_id: ID transaksi
        """
        try:
            items = db_manager.get_rincian_transaksi(transaksi_id)
            # Convert db format to widget format
            widget_items = []
            for item in items:
                widget_items.append({
                    'nama': item.get('nama_item', ''),
                    'spesifikasi': item.get('spesifikasi', ''),
                    'volume': item.get('volume', 1),
                    'satuan': item.get('satuan', 'unit'),
                    'harga_satuan': item.get('harga_satuan', 0),
                    'jumlah': item.get('jumlah', 0),
                    'keterangan': item.get('keterangan', ''),
                    'db_id': item.get('id'),  # Keep track of DB id
                })
            self.set_items(widget_items)
        except Exception as e:
            print(f"Error loading rincian from db: {e}")

    def save_to_db(self, db_manager, transaksi_id: int) -> bool:
        """
        Save rincian items to database.

        Args:
            db_manager: PencairanManager instance
            transaksi_id: ID transaksi

        Returns:
            True if successful
        """
        try:
            # Convert widget format to db format
            db_items = []
            for item in self._items:
                db_items.append({
                    'nama_item': item.get('nama', ''),
                    'spesifikasi': item.get('spesifikasi', ''),
                    'satuan': item.get('satuan', 'unit'),
                    'volume': item.get('volume', 1),
                    'harga_satuan': item.get('harga_satuan', 0),
                    'keterangan': item.get('keterangan', ''),
                })
            return db_manager.save_rincian_batch(transaksi_id, db_items)
        except Exception as e:
            print(f"Error saving rincian to db: {e}")
            return False

    def get_items_for_db(self) -> List[Dict[str, Any]]:
        """Get items formatted for database save."""
        return [
            {
                'nama_item': item.get('nama', ''),
                'spesifikasi': item.get('spesifikasi', ''),
                'satuan': item.get('satuan', 'unit'),
                'volume': item.get('volume', 1),
                'harga_satuan': item.get('harga_satuan', 0),
                'keterangan': item.get('keterangan', ''),
            }
            for item in self._items
        ]
