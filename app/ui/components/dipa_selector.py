"""
DIPA Selector Component
======================
Komponen untuk memilih data DIPA dengan fitur:
- Multi-select DIPA items
- Auto-calculate total biaya (estimasi biaya)
- Auto-fill MAK (kode_akun) dari DIPA terpilih
- Tampilkan summary biaya dan MAK
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel,
    QLineEdit, QComboBox, QDialog, QMessageBox, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QColor, QIcon

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple


def format_rupiah(value: float) -> str:
    """Format number as Rupiah."""
    if value is None:
        value = 0
    return f"Rp {int(value):,.0f}".replace(",", ".")


class DipaItem:
    """Model untuk item DIPA yang dipilih."""
    
    def __init__(self, dipa_id: int, kode_akun: str, kode_detail: str, 
                 uraian: str, jumlah: float, level: int):
        self.dipa_id = dipa_id
        self.kode_akun = kode_akun
        self.kode_detail = kode_detail
        self.uraian = uraian
        self.jumlah = jumlah
        self.level = level
        self.nomor_mak = f"{kode_akun}.{kode_detail}" if kode_detail else kode_akun
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'dipa_id': self.dipa_id,
            'kode_akun': self.kode_akun,
            'kode_detail': self.kode_detail,
            'nomor_mak': self.nomor_mak,
            'uraian': self.uraian,
            'jumlah': self.jumlah,
        }


class DipaSelectorDialog(QDialog):
    """Dialog untuk memilih DIPA items dengan multi-select."""
    
    items_selected = Signal(list)  # Emit list of DipaItem
    
    def __init__(self, db_path: str, tahun_anggaran: int, parent=None):
        super().__init__(parent)
        
        self.db_path = db_path
        self.tahun_anggaran = tahun_anggaran
        self.selected_items: List[DipaItem] = []
        
        self.setWindowTitle("Pilih Data DIPA")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(1000, 600)
        
        self._setup_ui()
        self._load_dipa_data()
    
    def _setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("Pilih Item DIPA untuk Estimasi Biaya")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)
        
        # Filter section
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        # Search by uraian
        filter_layout.addWidget(QLabel("Cari:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ketik uraian atau kode...")
        self.search_input.textChanged.connect(self._filter_table)
        filter_layout.addWidget(self.search_input)
        
        # Filter by level
        filter_layout.addWidget(QLabel("Level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItem("Semua Level", None)
        self.level_combo.addItem("Akun (Level 7)", 7)
        self.level_combo.addItem("Detail (Level 8)", 8)
        self.level_combo.currentIndexChanged.connect(self._filter_table)
        filter_layout.addWidget(self.level_combo)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Table untuk browse DIPA
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "✓", "Kode Akun", "Kode Detail", "MAK", 
            "Uraian", "Jumlah", "Level", "ID"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.table.setAlternatingRowColors(True)
        
        # Configure columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Kode Akun
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Kode Detail
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # MAK
        header.setSectionResizeMode(4, QHeaderView.Stretch)            # Uraian
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Jumlah
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Level
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # ID
        
        self.table.hideColumn(7)  # Hide ID
        
        self.table.itemSelectionChanged.connect(self._update_selection)
        layout.addWidget(self.table)
        
        # Summary section
        summary_group = QGroupBox("Ringkasan Pilihan")
        summary_layout = QFormLayout(summary_group)
        
        # Total biaya
        self.total_label = QLabel("Rp 0")
        self.total_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #27ae60;")
        summary_layout.addRow("Total Biaya:", self.total_label)
        
        # MAK codes
        self.mak_label = QLabel("-")
        self.mak_label.setStyleSheet("font-size: 11px; color: #34495e;")
        self.mak_label.setWordWrap(True)
        summary_layout.addRow("MAK Terpilih:", self.mak_label)
        
        # Item count
        self.count_label = QLabel("0 item dipilih")
        summary_layout.addRow("Jumlah Item:", self.count_label)
        
        layout.addWidget(summary_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_clear = QPushButton("Bersihkan Pilihan")
        btn_clear.setMinimumWidth(150)
        btn_clear.clicked.connect(self._clear_selection)
        button_layout.addWidget(btn_clear)
        
        btn_cancel = QPushButton("Batal")
        btn_cancel.setMinimumWidth(100)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        btn_ok = QPushButton("Gunakan Pilihan")
        btn_ok.setMinimumWidth(150)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_ok.clicked.connect(self._confirm_selection)
        button_layout.addWidget(btn_ok)
        
        layout.addLayout(button_layout)
    
    def _load_dipa_data(self):
        """Load DIPA data ke table."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Query detail-level DIPA (level 8) dan akun (level 7)
            query = """
                SELECT 
                    id, kode_akun, kode_detail, uraian, jumlah, 
                    level_kode, nomor_mak
                FROM pagu_anggaran
                WHERE tahun_anggaran = ?
                    AND level_kode IN (7, 8)
                    AND jumlah > 0
                ORDER BY kode_akun, kode_detail, uraian
            """
            
            cursor.execute(query, (self.tahun_anggaran,))
            rows = cursor.fetchall()
            
            self.table.setRowCount(len(rows))
            self.dipa_rows = []
            
            for idx, row in enumerate(rows):
                dipa_id = row['id']
                kode_akun = row['kode_akun'] or ""
                kode_detail = row['kode_detail'] or ""
                nomor_mak = row['nomor_mak'] or f"{kode_akun}.{kode_detail}"
                uraian = row['uraian'] or ""
                jumlah = row['jumlah'] or 0
                level = row['level_kode'] or 0
                
                # Store data
                self.dipa_rows.append({
                    'id': dipa_id,
                    'kode_akun': kode_akun,
                    'kode_detail': kode_detail,
                    'nomor_mak': nomor_mak,
                    'uraian': uraian,
                    'jumlah': jumlah,
                    'level': level
                })
                
                # Checkbox column
                checkbox_item = QTableWidgetItem("")
                checkbox_item.setCheckState(Qt.Unchecked)
                self.table.setItem(idx, 0, checkbox_item)
                
                # Kode Akun
                self.table.setItem(idx, 1, QTableWidgetItem(kode_akun))
                
                # Kode Detail
                self.table.setItem(idx, 2, QTableWidgetItem(kode_detail))
                
                # MAK
                self.table.setItem(idx, 3, QTableWidgetItem(nomor_mak))
                
                # Uraian
                self.table.setItem(idx, 4, QTableWidgetItem(uraian))
                
                # Jumlah
                jumlah_item = QTableWidgetItem(format_rupiah(jumlah))
                jumlah_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(idx, 5, jumlah_item)
                
                # Level
                level_item = QTableWidgetItem(f"Level {level}")
                level_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(idx, 6, level_item)
                
                # ID (hidden)
                self.table.setItem(idx, 7, QTableWidgetItem(str(dipa_id)))
            
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal load DIPA: {str(e)}")
    
    def _filter_table(self):
        """Filter table berdasarkan search dan level."""
        search_text = self.search_input.text().lower()
        selected_level = self.level_combo.currentData()
        
        for row in range(self.table.rowCount()):
            # Get search terms
            kode_akun = self.table.item(row, 1).text()
            kode_detail = self.table.item(row, 2).text()
            uraian = self.table.item(row, 4).text()
            level = int(self.table.item(row, 6).text().replace("Level ", ""))
            
            # Check search
            search_match = (search_text == "" or 
                          search_text in kode_akun.lower() or
                          search_text in kode_detail.lower() or
                          search_text in uraian.lower())
            
            # Check level
            level_match = (selected_level is None or level == selected_level)
            
            # Show/hide row
            show_row = search_match and level_match
            self.table.setRowHidden(row, not show_row)
    
    def _update_selection(self):
        """Update selected items dan summary."""
        # Collect selected rows
        selected_rows = self.table.selectionModel().selectedRows()
        self.selected_items = []
        
        for model_index in selected_rows:
            row = model_index.row()
            dipa_data = self.dipa_rows[row]
            
            dipa_item = DipaItem(
                dipa_id=dipa_data['id'],
                kode_akun=dipa_data['kode_akun'],
                kode_detail=dipa_data['kode_detail'],
                uraian=dipa_data['uraian'],
                jumlah=dipa_data['jumlah'],
                level=dipa_data['level']
            )
            self.selected_items.append(dipa_item)
        
        # Update summary
        self._update_summary()
    
    def _update_summary(self):
        """Update tampilan summary."""
        if not self.selected_items:
            self.total_label.setText("Rp 0")
            self.mak_label.setText("-")
            self.count_label.setText("0 item dipilih")
            return
        
        # Calculate total
        total = sum(item.jumlah for item in self.selected_items)
        self.total_label.setText(format_rupiah(total))
        
        # Collect unique MAKs
        mak_codes = list(set(item.nomor_mak for item in self.selected_items))
        mak_text = ", ".join(sorted(mak_codes))
        self.mak_label.setText(mak_text if mak_text else "-")
        
        # Item count
        self.count_label.setText(f"{len(self.selected_items)} item dipilih")
    
    def _clear_selection(self):
        """Bersihkan semua pilihan."""
        self.table.setCurrentItem(None)
        self.selected_items = []
        self._update_summary()
    
    def _confirm_selection(self):
        """Konfirmasi dan close dialog."""
        if not self.selected_items:
            QMessageBox.warning(self, "Peringatan", "Pilih minimal 1 item DIPA!")
            return
        
        self.items_selected.emit(self.selected_items)
        self.accept()


class DipaSelectionWidget(QWidget):
    """Widget untuk display dan manage DIPA selection dalam form."""
    
    data_changed = Signal()  # Emitted when selection changes
    
    def __init__(self, db_path: str, tahun_anggaran: int, parent=None):
        super().__init__(parent)
        
        self.db_path = db_path
        self.tahun_anggaran = tahun_anggaran
        self.selected_items: List[DipaItem] = []
        self.total_biaya = 0.0
        self.mak_codes = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Button to open selector
        btn_select = QPushButton("📋 Pilih dari DIPA")
        btn_select.setMinimumHeight(40)
        btn_select.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_select.clicked.connect(self._open_selector)
        layout.addWidget(btn_select)
        
        # Table untuk display selected items
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "MAK", "Uraian", "Jumlah", "Persentase", ""
        ])
        self.table.setMaximumHeight(150)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        
        # Summary section
        summary_group = QGroupBox("Summary DIPA")
        summary_layout = QFormLayout(summary_group)
        
        # Total biaya
        total_layout = QHBoxLayout()
        self.total_input = QDoubleSpinBox()
        self.total_input.setRange(0, 999999999999)
        self.total_input.setDecimals(0)
        self.total_input.setPrefix("Rp ")
        self.total_input.setGroupSeparatorShown(True)
        self.total_input.setReadOnly(True)
        self.total_input.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 5px;
                font-weight: bold;
                color: #27ae60;
            }
        """)
        total_layout.addWidget(self.total_input)
        summary_layout.addRow("Total Estimasi Biaya *", total_layout)
        
        # MAK codes
        mak_layout = QHBoxLayout()
        self.mak_input = QLineEdit()
        self.mak_input.setReadOnly(True)
        self.mak_input.setStyleSheet("background-color: #ecf0f1; border: 1px solid #bdc3c7; padding: 5px;")
        self.mak_input.setPlaceholderText("MAK akan terisi otomatis...")
        mak_layout.addWidget(self.mak_input)
        summary_layout.addRow("Kode MAK *", mak_layout)
        
        layout.addWidget(summary_group)
        layout.addStretch()
    
    def _open_selector(self):
        """Open DIPA selector dialog."""
        dialog = DipaSelectorDialog(self.db_path, self.tahun_anggaran, self)
        dialog.items_selected.connect(self._on_items_selected)
        dialog.exec()
    
    def _on_items_selected(self, items: List[DipaItem]):
        """Handle items selected dari dialog."""
        self.selected_items = items
        self._update_display()
        self.data_changed.emit()
    
    def _update_display(self):
        """Update display dengan selected items."""
        # Update table
        self.table.setRowCount(len(self.selected_items))
        self.total_biaya = 0
        self.mak_codes = []
        
        for idx, item in enumerate(self.selected_items):
            self.table.setItem(idx, 0, QTableWidgetItem(item.nomor_mak))
            self.table.setItem(idx, 1, QTableWidgetItem(item.uraian))
            
            jumlah_item = QTableWidgetItem(format_rupiah(item.jumlah))
            jumlah_item.setTextAlignment(Qt.AlignRight)
            self.table.setItem(idx, 2, jumlah_item)
            
            self.total_biaya += item.jumlah
            
            if item.nomor_mak not in self.mak_codes:
                self.mak_codes.append(item.nomor_mak)
            
            # Percentage
            persen = 0  # Will calculate after total is known
            self.table.setItem(idx, 3, QTableWidgetItem(f"{persen:.1f}%"))
            
            # Remove button
            btn_remove = QPushButton("Hapus")
            btn_remove.setMaximumWidth(60)
            btn_remove.clicked.connect(lambda checked, i=idx: self._remove_item(i))
            self.table.setCellWidget(idx, 4, btn_remove)
        
        # Update percentages
        for idx, item in enumerate(self.selected_items):
            if self.total_biaya > 0:
                persen = (item.jumlah / self.total_biaya) * 100
                self.table.item(idx, 3).setText(f"{persen:.1f}%")
        
        # Update summary inputs
        self.total_input.setValue(self.total_biaya)
        self.mak_input.setText(", ".join(self.mak_codes))
    
    def _remove_item(self, idx: int):
        """Remove item dari selection."""
        if 0 <= idx < len(self.selected_items):
            self.selected_items.pop(idx)
            self._update_display()
            self.data_changed.emit()
    
    def get_total_biaya(self) -> float:
        """Get total biaya dari selected items."""
        return self.total_biaya
    
    def get_mak_codes(self) -> List[str]:
        """Get list of MAK codes."""
        return self.mak_codes
    
    def get_mak_string(self) -> str:
        """Get MAK codes as comma-separated string."""
        return ", ".join(self.mak_codes)
    
    def set_editable_biaya(self, editable: bool = True):
        """Allow manual edit of biaya (untuk override)."""
        self.total_input.setReadOnly(not editable)
        if editable:
            self.total_input.setStyleSheet("""
                QDoubleSpinBox {
                    background-color: white;
                    border: 1px solid #3498db;
                    padding: 5px;
                    font-weight: bold;
                    color: #27ae60;
                }
            """)
    
    def clear_selection(self):
        """Clear all selections."""
        self.selected_items = []
        self.total_biaya = 0
        self.mak_codes = []
        self._update_display()
