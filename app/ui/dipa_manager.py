"""
Data DIPA Manager
==================
Manager untuk mengelola data DIPA/POK (Pagu Anggaran).

Fitur:
- Import data DIPA dari Excel
- Browse/filter data anggaran hierarkis
- Edit manual item pagu
- View realisasi dan sisa anggaran
- Export data DIPA
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QLabel, QLineEdit, QComboBox, QFileDialog, QMessageBox,
    QGroupBox, QFormLayout, QDoubleSpinBox, QSpinBox,
    QTreeWidget, QTreeWidgetItem, QSplitter, QTextEdit,
    QWidget, QTabWidget, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any


class DipaManager(QDialog):
    """Dialog untuk mengelola Data DIPA/POK."""
    
    data_changed = Signal()
    
    def __init__(self, db_path: str = None, parent=None):
        super().__init__(parent)
        
        from app.core.config import DATABASE_PATH, TAHUN_ANGGARAN
        
        self.db_path = db_path or DATABASE_PATH
        self.tahun_anggaran = TAHUN_ANGGARAN
        
        self.setWindowTitle("Data DIPA / POK")
        self.resize(1200, 700)
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Tab 1: Hierarki DIPA
        tab_tree = self._create_tree_tab()
        tabs.addTab(tab_tree, "Hierarki DIPA")
        
        # Tab 2: Data Tabel
        tab_table = self._create_table_tab()
        tabs.addTab(tab_table, "Data Tabel")
        
        # Tab 3: Import/Export
        tab_io = self._create_io_tab()
        tabs.addTab(tab_io, "Import/Export")
        
        layout.addWidget(tabs)
        
        # Footer buttons
        footer = self._create_footer()
        layout.addWidget(footer)
    
    def _create_header(self) -> QWidget:
        """Create header dengan filter."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 10)
        
        # Title
        title = QLabel("📊 Data DIPA / POK")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Filter section
        filter_group = QGroupBox("Filter & Pencarian")
        filter_layout = QHBoxLayout(filter_group)
        
        # Tahun anggaran
        filter_layout.addWidget(QLabel("Tahun:"))
        self.tahun_combo = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 2, current_year + 3):
            self.tahun_combo.addItem(str(year), year)
        # Set to current tahun_anggaran
        idx = self.tahun_combo.findData(self.tahun_anggaran)
        if idx >= 0:
            self.tahun_combo.setCurrentIndex(idx)
        self.tahun_combo.currentIndexChanged.connect(self._on_tahun_changed)
        filter_layout.addWidget(self.tahun_combo)
        
        # Search
        filter_layout.addWidget(QLabel("Cari:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari kode atau uraian...")
        self.search_input.textChanged.connect(self._on_search)
        filter_layout.addWidget(self.search_input)
        
        # Level filter
        filter_layout.addWidget(QLabel("Level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItem("Semua", None)
        self.level_combo.addItem("Program", 1)
        self.level_combo.addItem("Kegiatan", 2)
        self.level_combo.addItem("KRO", 3)
        self.level_combo.addItem("RO", 4)
        self.level_combo.addItem("Komponen", 5)
        self.level_combo.addItem("Sub Komponen", 6)
        self.level_combo.addItem("Akun", 7)
        self.level_combo.addItem("Detail", 8)
        self.level_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.level_combo)
        
        # Refresh button
        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.clicked.connect(self._load_data)
        filter_layout.addWidget(btn_refresh)
        
        filter_layout.addStretch()
        
        layout.addWidget(filter_group)
        
        return widget
    
    def _create_tree_tab(self) -> QWidget:
        """Create tree view tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter
        splitter = QSplitter(Qt.Vertical)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([
            "Kode", "Uraian", "Volume", "Satuan", 
            "Harga Satuan", "Jumlah", "Realisasi", "Sisa", "%"
        ])
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 300)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        splitter.addWidget(self.tree)
        
        # Detail panel
        detail_widget = self._create_detail_panel()
        splitter.addWidget(detail_widget)
        
        splitter.setSizes([500, 200])
        layout.addWidget(splitter)
        
        return widget
    
    def _create_detail_panel(self) -> QWidget:
        """Create detail panel."""
        widget = QGroupBox("Detail Item")
        layout = QFormLayout(widget)
        
        self.detail_kode = QLabel("-")
        self.detail_uraian = QTextEdit()
        self.detail_uraian.setMaximumHeight(80)
        self.detail_uraian.setReadOnly(True)
        self.detail_volume = QLabel("-")
        self.detail_satuan = QLabel("-")
        self.detail_harga = QLabel("-")
        self.detail_jumlah = QLabel("-")
        self.detail_realisasi = QLabel("-")
        self.detail_sisa = QLabel("-")
        
        layout.addRow("Kode:", self.detail_kode)
        layout.addRow("Uraian:", self.detail_uraian)
        layout.addRow("Volume:", self.detail_volume)
        layout.addRow("Satuan:", self.detail_satuan)
        layout.addRow("Harga Satuan:", self.detail_harga)
        layout.addRow("Jumlah:", self.detail_jumlah)
        layout.addRow("Realisasi:", self.detail_realisasi)
        layout.addRow("Sisa:", self.detail_sisa)
        
        return widget
    
    def _create_table_tab(self) -> QWidget:
        """Create table view tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        btn_add = QPushButton("➕ Tambah")
        btn_add.clicked.connect(self._add_item)
        toolbar.addWidget(btn_add)
        
        btn_edit = QPushButton("✏️ Edit")
        btn_edit.clicked.connect(self._edit_item)
        toolbar.addWidget(btn_edit)
        
        btn_delete = QPushButton("🗑️ Hapus")
        btn_delete.clicked.connect(self._delete_item)
        toolbar.addWidget(btn_delete)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Kode", "Uraian", "Volume", "Satuan",
            "Harga Satuan", "Jumlah", "Realisasi", "Sisa"
        ])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.hideColumn(0)  # Hide ID
        self.table.doubleClicked.connect(self._edit_item)
        
        layout.addWidget(self.table)
        
        # Summary
        summary_layout = QHBoxLayout()
        summary_layout.addWidget(QLabel("Total Data:"))
        self.total_label = QLabel("0")
        self.total_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.total_label)
        
        summary_layout.addSpacing(20)
        summary_layout.addWidget(QLabel("Total Pagu:"))
        self.pagu_label = QLabel("Rp 0")
        self.pagu_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        summary_layout.addWidget(self.pagu_label)
        
        summary_layout.addSpacing(20)
        summary_layout.addWidget(QLabel("Total Realisasi:"))
        self.realisasi_label = QLabel("Rp 0")
        self.realisasi_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        summary_layout.addWidget(self.realisasi_label)
        
        summary_layout.addSpacing(20)
        summary_layout.addWidget(QLabel("Sisa:"))
        self.sisa_label = QLabel("Rp 0")
        self.sisa_label.setStyleSheet("font-weight: bold; color: #3498db;")
        summary_layout.addWidget(self.sisa_label)
        
        summary_layout.addStretch()
        layout.addLayout(summary_layout)
        
        return widget
    
    def _create_io_tab(self) -> QWidget:
        """Create import/export tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Import section
        import_group = QGroupBox("📥 Import Data DIPA")
        import_layout = QVBoxLayout(import_group)
        
        info = QLabel(
            "Import data DIPA dari file CSV (format DIPA standar).\n\n"
            "Format CSV harus memiliki kolom:\n"
            "- KODE_PROGRAM, KODE_KEGIATAN, KODE_OUTPUT\n"
            "- KODE_KOMPONEN, KODE_SUBKOMPONEN, KODE_AKUN\n"
            "- URAIAN_ITEM, VOLKEG, SATKEG, HARGASAT, TOTAL\n\n"
            "Data yang sudah ada akan dilewati (tidak ditimpa)."
        )
        info.setWordWrap(True)
        info.setStyleSheet("background: #fff3cd; padding: 10px; border-radius: 5px;")
        import_layout.addWidget(info)
        
        btn_import = QPushButton("📂 Pilih File CSV untuk Import")
        btn_import.setStyleSheet("padding: 10px; font-size: 13px;")
        btn_import.clicked.connect(self._import_excel)
        import_layout.addWidget(btn_import)
        
        layout.addWidget(import_group)
        
        # Export section
        export_group = QGroupBox("📤 Export Data DIPA")
        export_layout = QVBoxLayout(export_group)
        
        export_info = QLabel(
            "Export data DIPA ke file CSV untuk backup atau editing."
        )
        export_info.setWordWrap(True)
        export_layout.addWidget(export_info)
        
        btn_export = QPushButton("💾 Export ke CSV")
        btn_export.setStyleSheet("padding: 10px; font-size: 13px;")
        btn_export.clicked.connect(self._export_excel)
        export_layout.addWidget(btn_export)
        
        layout.addWidget(export_group)
        
        # Clear data section
        clear_group = QGroupBox("🗑️ Hapus Data")
        clear_layout = QVBoxLayout(clear_group)
        
        clear_info = QLabel(
            "Hapus semua data DIPA untuk tahun anggaran yang dipilih.\n"
            "⚠️ HATI-HATI: Tindakan ini tidak dapat dibatalkan!"
        )
        clear_info.setWordWrap(True)
        clear_info.setStyleSheet("background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;")
        clear_layout.addWidget(clear_info)
        
        btn_clear = QPushButton("🗑️ Hapus Semua Data Tahun Ini")
        btn_clear.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 13px;
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        btn_clear.clicked.connect(self._clear_data)
        clear_layout.addWidget(btn_clear)
        
        layout.addWidget(clear_group)
        
        # Template section
        template_group = QGroupBox("📋 Template Import")
        template_layout = QVBoxLayout(template_group)
        
        template_info = QLabel(
            "Download template CSV untuk memudahkan import data DIPA.\n"
            "Template sudah berisi contoh format yang sesuai."
        )
        template_info.setWordWrap(True)
        template_layout.addWidget(template_info)
        
        btn_template = QPushButton("📥 Download Template CSV")
        btn_template.setStyleSheet("padding: 10px; font-size: 13px;")
        btn_template.clicked.connect(self._download_template)
        template_layout.addWidget(btn_template)
        
        layout.addWidget(template_group)
        
        layout.addStretch()
        
        return widget
    
    def _create_footer(self) -> QWidget:
        """Create footer buttons."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        layout.addStretch()
        
        btn_close = QPushButton("Tutup")
        btn_close.setMinimumWidth(100)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
        return widget
    
    # =========================================================================
    # DATA LOADING
    # =========================================================================
    
    def _load_data(self):
        """Load data from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verify table exists first
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pagu_anggaran'")
            if not cursor.fetchone():
                conn.close()
                raise Exception(
                    f"Table 'pagu_anggaran' tidak ditemukan.\n\n"
                    f"Database path: {self.db_path}\n\n"
                    f"Solusi: Jalankan import DIPA terlebih dahulu untuk membuat data."
                )
            
            tahun = self.tahun_combo.currentData()
            
            # Get data
            cursor.execute("""
                SELECT 
                    id, kode_full, uraian, volume, satuan,
                    harga_satuan, jumlah, realisasi, sisa,
                    persen_realisasi, level_kode, parent_id
                FROM pagu_anggaran
                WHERE tahun_anggaran = ?
                ORDER BY kode_full
            """, (tahun,))
            
            rows = cursor.fetchall()
            conn.close()
            
            self._populate_tree(rows)
            self._populate_table(rows)
            self._update_summary(rows)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat data: {str(e)}")
    
    def _populate_tree(self, rows: List[tuple]):
        """Populate tree widget."""
        self.tree.clear()
        
        # Build hierarchy
        items_map = {}  # id -> QTreeWidgetItem
        
        for row in rows:
            id_, kode, uraian, volume, satuan, harga, jumlah, realisasi, sisa, persen, level, parent_id = row
            
            item = QTreeWidgetItem()
            item.setText(0, kode or "-")
            item.setText(1, uraian or "-")
            item.setText(2, self._format_number(volume))
            item.setText(3, satuan or "-")
            item.setText(4, self._format_rupiah(harga))
            item.setText(5, self._format_rupiah(jumlah))
            item.setText(6, self._format_rupiah(realisasi))
            item.setText(7, self._format_rupiah(sisa))
            item.setText(8, f"{persen:.1f}%" if persen else "0%")
            
            item.setData(0, Qt.UserRole, id_)
            
            items_map[id_] = item
            
            # Add to parent or root
            if parent_id and parent_id in items_map:
                items_map[parent_id].addChild(item)
            else:
                self.tree.addTopLevelItem(item)
        
        # Expand first level
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setExpanded(True)
    
    def _populate_table(self, rows: List[tuple]):
        """Populate table widget."""
        self.table.setRowCount(0)
        
        # Filter based on search and level
        search_text = self.search_input.text().lower()
        level_filter = self.level_combo.currentData()
        
        for row in rows:
            id_, kode, uraian, volume, satuan, harga, jumlah, realisasi, sisa, persen, level, parent_id = row
            
            # Apply filters
            if search_text:
                if search_text not in (kode or "").lower() and search_text not in (uraian or "").lower():
                    continue
            
            if level_filter and level != level_filter:
                continue
            
            # Add row
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(id_)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(kode or "-"))
            self.table.setItem(row_idx, 2, QTableWidgetItem(uraian or "-"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(self._format_number(volume)))
            self.table.setItem(row_idx, 4, QTableWidgetItem(satuan or "-"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(self._format_rupiah(harga)))
            self.table.setItem(row_idx, 6, QTableWidgetItem(self._format_rupiah(jumlah)))
            self.table.setItem(row_idx, 7, QTableWidgetItem(self._format_rupiah(realisasi)))
            self.table.setItem(row_idx, 8, QTableWidgetItem(self._format_rupiah(sisa)))
        
        self.table.resizeColumnsToContents()
    
    def _update_summary(self, rows: List[tuple]):
        """Update summary labels."""
        total_items = len(rows)
        total_pagu = sum(row[6] or 0 for row in rows)
        total_realisasi = sum(row[7] or 0 for row in rows)
        total_sisa = sum(row[8] or 0 for row in rows)
        
        self.total_label.setText(str(total_items))
        self.pagu_label.setText(self._format_rupiah(total_pagu))
        self.realisasi_label.setText(self._format_rupiah(total_realisasi))
        self.sisa_label.setText(self._format_rupiah(total_sisa))
    
    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================
    
    def _on_tahun_changed(self):
        """Handle tahun change."""
        self.tahun_anggaran = self.tahun_combo.currentData()
        self._load_data()
    
    def _on_search(self):
        """Handle search."""
        # Re-populate table with filter
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            tahun = self.tahun_combo.currentData()
            cursor.execute("""
                SELECT 
                    id, kode_full, uraian, volume, satuan,
                    harga_satuan, jumlah, realisasi, sisa,
                    persen_realisasi, level_kode, parent_id
                FROM pagu_anggaran
                WHERE tahun_anggaran = ?
                ORDER BY kode_full
            """, (tahun,))
            
            rows = cursor.fetchall()
            conn.close()
            
            self._populate_table(rows)
            
        except Exception as e:
            pass
    
    def _on_filter_changed(self):
        """Handle filter change."""
        self._on_search()  # Reuse search logic
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item double click."""
        item_id = item.data(0, Qt.UserRole)
        if item_id:
            self._show_detail(item_id)
    
    def _show_detail(self, item_id: int):
        """Show item detail."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    kode_full, uraian, volume, satuan,
                    harga_satuan, jumlah, realisasi, sisa
                FROM pagu_anggaran
                WHERE id = ?
            """, (item_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                kode, uraian, volume, satuan, harga, jumlah, realisasi, sisa = row
                
                self.detail_kode.setText(kode or "-")
                self.detail_uraian.setPlainText(uraian or "-")
                self.detail_volume.setText(self._format_number(volume))
                self.detail_satuan.setText(satuan or "-")
                self.detail_harga.setText(self._format_rupiah(harga))
                self.detail_jumlah.setText(self._format_rupiah(jumlah))
                self.detail_realisasi.setText(self._format_rupiah(realisasi))
                self.detail_sisa.setText(self._format_rupiah(sisa))
        
        except Exception as e:
            pass
    
    # =========================================================================
    # CRUD OPERATIONS
    # =========================================================================
    
    def _add_item(self):
        """Add new item."""
        QMessageBox.information(
            self, "Info", 
            "Fitur tambah manual sedang dalam pengembangan.\n"
            "Silakan gunakan Import Excel."
        )
    
    def _edit_item(self):
        """Edit selected item."""
        QMessageBox.information(
            self, "Info", 
            "Fitur edit manual sedang dalam pengembangan.\n"
            "Silakan gunakan Import Excel."
        )
    
    def _delete_item(self):
        """Delete selected item."""
        QMessageBox.information(
            self, "Info", 
            "Fitur hapus manual sedang dalam pengembangan.\n"
            "Gunakan dengan hati-hati!"
        )
    
    def _clear_data(self):
        """Clear all data for selected year."""
        tahun = self.tahun_combo.currentData()
        
        reply = QMessageBox.warning(
            self,
            "⚠️ Konfirmasi Hapus",
            f"Anda akan menghapus SEMUA data DIPA tahun {tahun}!\n\n"
            "Tindakan ini tidak dapat dibatalkan.\n"
            "Lanjutkan?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Double confirmation
        reply2 = QMessageBox.warning(
            self,
            "⚠️ Konfirmasi Terakhir",
            f"KONFIRMASI TERAKHIR!\n\n"
            f"Hapus semua data DIPA tahun {tahun}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply2 != QMessageBox.Yes:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get count before delete
            cursor.execute("""
                SELECT COUNT(*) FROM pagu_anggaran
                WHERE tahun_anggaran = ?
            """, (tahun,))
            count = cursor.fetchone()[0]
            
            # Delete
            cursor.execute("""
                DELETE FROM pagu_anggaran
                WHERE tahun_anggaran = ?
            """, (tahun,))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(
                self,
                "Hapus Berhasil",
                f"Berhasil menghapus {count} data DIPA tahun {tahun}"
            )
            
            # Reload
            self._load_data()
            self.data_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Gagal menghapus data:\n{str(e)}"
            )
    
    # =========================================================================
    # IMPORT/EXPORT
    # =========================================================================
    
    def _import_excel(self):
        """Import from CSV/Excel."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih File CSV/Excel",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        # Check file extension
        if file_path.lower().endswith('.csv'):
            self._import_from_csv(file_path)
        else:
            QMessageBox.information(
                self, "Info",
                "Import Excel (.xlsx/.xls) sedang dalam pengembangan.\n"
                "Silakan gunakan format CSV terlebih dahulu."
            )
    
    def _import_from_csv(self, file_path: str):
        """Import data from CSV file (DIPA format)."""
        try:
            import csv
            
            # Konfirmasi
            reply = QMessageBox.question(
                self,
                "Konfirmasi Import",
                f"Import data dari:\n{file_path}\n\n"
                "Data yang sudah ada akan ditambahkan (tidak ditimpa).\n"
                "Lanjutkan?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Parse CSV
            imported_count = 0
            skipped_count = 0
            error_count = 0
            
            tahun = self.tahun_combo.currentData()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Extract data dari format DIPA CSV
                        kode_program = row.get('KODE_PROGRAM', '').strip()
                        kode_kegiatan = row.get('KODE_KEGIATAN', '').strip()
                        kode_output = row.get('KODE_OUTPUT', '').strip()
                        kode_komponen = row.get('KODE_KOMPONEN', '').strip()
                        kode_subkomponen = row.get('KODE_SUBKOMPONEN', '').strip()
                        kode_akun = row.get('KODE_AKUN', '').strip()
                        kode_item = row.get('KODE_ITEM', '').strip()
                        
                        # Build kode_full
                        kode_parts = [p for p in [
                            kode_program, kode_kegiatan, kode_output,
                            kode_komponen, kode_subkomponen, kode_akun, kode_item
                        ] if p]
                        kode_full = '.'.join(kode_parts)
                        
                        if not kode_full:
                            skipped_count += 1
                            continue
                        
                        # Uraian
                        uraian = row.get('URAIAN_ITEM', '').strip()
                        if not uraian:
                            uraian = row.get('URAIAN_SUBKOMPON', '').strip()
                        
                        # Volume dan satuan
                        volume = self._parse_number(row.get('VOLKEG', '0'))
                        satuan = row.get('SATKEG', '').strip()
                        
                        # Harga
                        harga_satuan = self._parse_number(row.get('HARGASAT', '0'))
                        jumlah = self._parse_number(row.get('TOTAL', '0'))
                        
                        # Sumber dana
                        sumber_dana = row.get('SUMBER_DANA', 'RM').strip()
                        
                        # Determine level (8 = detail item)
                        level = 8
                        
                        # Check if exists
                        cursor.execute("""
                            SELECT id FROM pagu_anggaran
                            WHERE tahun_anggaran = ? AND kode_full = ?
                        """, (tahun, kode_full))
                        
                        if cursor.fetchone():
                            # Update existing
                            cursor.execute("""
                                UPDATE pagu_anggaran
                                SET uraian = ?, volume = ?, satuan = ?,
                                    harga_satuan = ?, jumlah = ?,
                                    sisa = ?, sumber_dana = ?,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE tahun_anggaran = ? AND kode_full = ?
                            """, (
                                uraian, volume, satuan,
                                harga_satuan, jumlah,
                                jumlah,  # sisa = jumlah (belum ada realisasi)
                                sumber_dana,
                                tahun, kode_full
                            ))
                            skipped_count += 1
                        else:
                            # Insert new
                            cursor.execute("""
                                INSERT INTO pagu_anggaran (
                                    tahun_anggaran, kode_full, uraian,
                                    volume, satuan, harga_satuan, jumlah,
                                    realisasi, sisa, persen_realisasi,
                                    level_kode, sumber_dana,
                                    kode_program, kode_kegiatan, kode_akun
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, 0, ?, ?, ?, ?, ?)
                            """, (
                                tahun, kode_full, uraian,
                                volume, satuan, harga_satuan, jumlah,
                                jumlah,  # sisa
                                level,
                                sumber_dana,
                                kode_program, kode_kegiatan, kode_akun
                            ))
                            imported_count += 1
                    
                    except Exception as e:
                        print(f"Error on row {row_num}: {str(e)}")
                        error_count += 1
                        continue
            
            conn.commit()
            conn.close()
            
            # Show result
            msg = f"Import selesai!\n\n"
            msg += f"✅ Berhasil diimpor: {imported_count}\n"
            if skipped_count > 0:
                msg += f"⏭️ Dilewati (sudah ada): {skipped_count}\n"
            if error_count > 0:
                msg += f"❌ Error: {error_count}\n"
            
            QMessageBox.information(self, "Import Selesai", msg)
            
            # Reload data
            self._load_data()
            self.data_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Import",
                f"Gagal import data:\n{str(e)}"
            )
    
    def _parse_number(self, value: str) -> float:
        """Parse string to number, handle empty/invalid values."""
        if not value or value.strip() == '':
            return 0.0
        try:
            # Remove any non-numeric characters except decimal point
            cleaned = ''.join(c for c in str(value) if c.isdigit() or c == '.')
            return float(cleaned) if cleaned else 0.0
        except:
            return 0.0
    
    def _export_excel(self):
        """Export to CSV/Excel."""
        # Choose file
        default_name = f"export_dipa_{self.tahun_anggaran}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data DIPA",
            default_name,
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        # Check extension
        if file_path.lower().endswith('.csv'):
            self._export_to_csv(file_path)
        else:
            QMessageBox.information(
                self, "Info",
                "Export Excel (.xlsx) sedang dalam pengembangan.\n"
                "Silakan gunakan format CSV terlebih dahulu."
            )
    
    def _export_to_csv(self, file_path: str):
        """Export data to CSV file."""
        try:
            import csv
            
            tahun = self.tahun_combo.currentData()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verify table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pagu_anggaran'")
            if not cursor.fetchone():
                conn.close()
                raise Exception(f"Table 'pagu_anggaran' tidak ditemukan di database:\n{self.db_path}")
            
            # Get all data
            cursor.execute("""
                SELECT 
                    kode_full, uraian, volume, satuan,
                    harga_satuan, jumlah, realisasi, sisa,
                    persen_realisasi, sumber_dana,
                    kode_program, kode_kegiatan, kode_akun
                FROM pagu_anggaran
                WHERE tahun_anggaran = ?
                ORDER BY kode_full
            """, (tahun,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Check if data exists
            if not rows:
                QMessageBox.warning(
                    self,
                    "Data Kosong",
                    f"Tidak ada data DIPA untuk tahun {tahun}"
                )
                return
            
            # Write to CSV
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Kode', 'Uraian', 'Volume', 'Satuan',
                    'Harga Satuan', 'Jumlah', 'Realisasi', 'Sisa',
                    'Persen Realisasi', 'Sumber Dana',
                    'Kode Program', 'Kode Kegiatan', 'Kode Akun'
                ])
                
                # Data
                for row in rows:
                    writer.writerow(row)
            
            QMessageBox.information(
                self,
                "Export Berhasil",
                f"Data berhasil diekspor ke:\n{file_path}\n\n"
                f"Total: {len(rows)} baris"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Export",
                f"Gagal export data:\n{str(e)}"
            )
    
    def _download_template(self):
        """Download template CSV."""
        # Choose save location
        default_name = f"template_import_dipa.csv"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Template CSV",
            default_name,
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            import csv
            
            # Create template with headers and sample data
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # Header (sesuai format DIPA standar)
                writer.writerow([
                    'KDSATKER', 'KODE_PROGRAM', 'KODE_KEGIATAN', 'KODE_OUTPUT',
                    'KODE_KOMPONEN', 'KODE_SUBKOMPONEN', 'URAIAN_SUBKOMPON',
                    'KODE_AKUN', 'KODE_ITEM', 'URAIAN_ITEM', 'SUMBER_DANA',
                    'VOLKEG', 'SATKEG', 'HARGASAT', 'TOTAL'
                ])
                
                # Sample data
                writer.writerow([
                    '634146', 'DL', '2376', 'FAN',
                    'ZZ1', 'A', 'Pemenuhan prioritas direktif presiden',
                    '522191', '1', 'Pemenuhan Prioritas Direktif Presiden', 'A',
                    '1', 'pkt', '2919141000', '2919141000'
                ])
                
                writer.writerow([
                    '634146', 'DL', '2376', 'FAN',
                    'ZZ1', 'A', 'Pemenuhan prioritas direktif presiden',
                    '524111', '2', 'Belanja Operasional', 'A',
                    '1', 'pkt', '214677000', '214677000'
                ])
            
            QMessageBox.information(
                self,
                "Template Berhasil Dibuat",
                f"Template CSV berhasil disimpan ke:\n{file_path}\n\n"
                "Silakan isi data sesuai format yang disediakan."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Gagal membuat template:\n{str(e)}"
            )
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _format_rupiah(self, value: float) -> str:
        """Format number as Rupiah."""
        if value is None or value == 0:
            return "-"
        return f"Rp {value:,.0f}".replace(",", ".")
    
    def _format_number(self, value: float) -> str:
        """Format number."""
        if value is None or value == 0:
            return "-"
        return f"{value:,.2f}".replace(",", ".")


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = DipaManager()
    dialog.exec()
    sys.exit(app.exec())
