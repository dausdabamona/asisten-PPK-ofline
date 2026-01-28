"""
UP List Page - Daftar semua transaksi Uang Persediaan
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QComboBox, QHeaderView, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QColor
from typing import Optional
import os
from datetime import datetime

from app.models.pencairan_models import get_pencairan_manager
from app.config.workflow_config import UP_WORKFLOW
from app.templates.engine import format_rupiah


class UPListPage(QWidget):
    """Halaman daftar transaksi UP"""
    
    transaksi_selected = Signal(int)  # transaksi_id
    create_new_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pencairan_mgr = get_pencairan_manager()
        self.current_filter_status = 'semua'
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup UI untuk list page"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        title = QLabel("📗 UANG PERSEDIAAN (UP)")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        
        desc = QLabel("Kelola transaksi pencairan uang untuk belanja operasional ≤ Rp 50 juta")
        desc_font = QFont()
        desc_font.setPointSize(9)
        desc.setFont(desc_font)
        desc.setStyleSheet("color: #7f8c8d;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(desc, 1)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Filter & Action Bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        # Filter status
        filter_label = QLabel("Filter Status:")
        filter_font = QFont()
        filter_font.setPointSize(9)
        filter_label.setFont(filter_font)
        
        self.combo_filter = QComboBox()
        self.combo_filter.setFixedWidth(150)
        self.combo_filter.addItems(["Semua Status", "Draft", "Aktif", "Selesai", "Batal"])
        self.combo_filter.currentIndexChanged.connect(self.on_filter_changed)
        
        # Search
        search_label = QLabel("Cari:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari kode/nama kegiatan...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.on_search_changed)
        
        # Buttons
        btn_tambah = QPushButton("➕ Transaksi Baru")
        btn_tambah.setFixedWidth(150)
        btn_tambah.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_tambah.clicked.connect(self.on_tambah_clicked)
        
        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.setFixedWidth(100)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_refresh.clicked.connect(self.load_data)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.combo_filter)
        filter_layout.addSpacing(20)
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.search_input)
        filter_layout.addStretch()
        filter_layout.addWidget(btn_tambah)
        filter_layout.addWidget(btn_refresh)
        
        layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Kode", "Nama Kegiatan", "Nilai", "Jenis Belanja", 
            "Fase", "Status", "Tindakan"
        ])
        
        # Setup header
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        # Styling
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 5px;
                border: none;
            }
        """)
        
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(self.table.styleSheet() + """
            QTableWidget {
                alternate-background-color: #f9f9f9;
            }
        """)
        
        self.table.doubleClicked.connect(self.on_table_double_clicked)
        
        layout.addWidget(self.table)
        
        # Summary
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(20)
        
        self.label_draft = QLabel("📋 Draft: 0")
        self.label_aktif = QLabel("⚙️ Aktif: 0")
        self.label_selesai = QLabel("✅ Selesai: 0")
        self.label_total = QLabel("📊 Total: 0")
        
        summary_font = QFont()
        summary_font.setPointSize(9)
        
        for label in [self.label_draft, self.label_aktif, self.label_selesai, self.label_total]:
            label.setFont(summary_font)
        
        summary_layout.addWidget(self.label_draft)
        summary_layout.addWidget(self.label_aktif)
        summary_layout.addWidget(self.label_selesai)
        summary_layout.addWidget(self.label_total)
        summary_layout.addStretch()
        
        layout.addLayout(summary_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Load data transaksi UP"""
        status_map = {
            'Semua Status': None,
            'Draft': 'draft',
            'Aktif': 'aktif',
            'Selesai': 'selesai',
            'Batal': 'batal'
        }
        
        status_filter = status_map.get(self.combo_filter.currentText())
        transaksi_list = self.pencairan_mgr.list_transaksi(
            mekanisme='UP',
            status=status_filter
        )
        
        # Filter by search
        search_text = self.search_input.text().lower()
        if search_text:
            transaksi_list = [
                t for t in transaksi_list
                if search_text in t['kode_transaksi'].lower() or
                   search_text in t['nama_kegiatan'].lower()
            ]
        
        # Load ke table
        self.table.setRowCount(0)
        
        for row, transaksi in enumerate(transaksi_list):
            self.table.insertRow(row)
            
            # Kode
            kode_item = QTableWidgetItem(transaksi['kode_transaksi'])
            kode_font = QFont()
            kode_font.setBold(True)
            kode_item.setFont(kode_font)
            kode_item.setForeground(QColor('#2980b9'))
            self.table.setItem(row, 0, kode_item)
            
            # Nama kegiatan
            self.table.setItem(row, 1, QTableWidgetItem(transaksi['nama_kegiatan']))
            
            # Nilai
            nilai_item = QTableWidgetItem(format_rupiah(transaksi['estimasi_biaya']))
            nilai_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(row, 2, nilai_item)
            
            # Jenis belanja
            self.table.setItem(row, 3, QTableWidgetItem(transaksi['jenis_belanja']))
            
            # Fase
            fase_item = QTableWidgetItem(f"Fase {transaksi['fase_aktif']}")
            self.table.setItem(row, 4, fase_item)
            
            # Status
            status_icon = self._get_status_icon(transaksi['status'])
            status_item = QTableWidgetItem(f"{status_icon} {transaksi['status'].upper()}")
            self.table.setItem(row, 5, status_item)
            
            # ID (hidden)
            transaksi['id']
        
        # Update summary
        self._update_summary()
    
    def _get_status_icon(self, status: str) -> str:
        """Get status icon"""
        icons = {
            'draft': '📋',
            'aktif': '⚙️',
            'selesai': '✅',
            'batal': '❌'
        }
        return icons.get(status, '❓')
    
    def _update_summary(self):
        """Update summary statistics"""
        draft = self.pencairan_mgr.count_transaksi(mekanisme='UP', status='draft')
        aktif = self.pencairan_mgr.count_transaksi(mekanisme='UP', status='aktif')
        selesai = self.pencairan_mgr.count_transaksi(mekanisme='UP', status='selesai')
        total = draft + aktif + selesai
        
        self.label_draft.setText(f"📋 Draft: {draft}")
        self.label_aktif.setText(f"⚙️ Aktif: {aktif}")
        self.label_selesai.setText(f"✅ Selesai: {selesai}")
        self.label_total.setText(f"📊 Total: {total}")
    
    def on_filter_changed(self, index: int):
        """Handle filter changed"""
        self.load_data()
    
    def on_search_changed(self, text: str):
        """Handle search text changed"""
        self.load_data()
    
    def on_tambah_clicked(self):
        """Handle tambah button clicked"""
        self.create_new_requested.emit()
    
    def on_table_double_clicked(self, index):
        """Handle table double clicked"""
        if index.isValid():
            row = index.row()
            # Get transaksi ID from table
            kode = self.table.item(row, 0).text()
            transaksi = self.pencairan_mgr.get_transaksi_by_kode(kode)
            if transaksi:
                self.transaksi_selected.emit(transaksi['id'])
