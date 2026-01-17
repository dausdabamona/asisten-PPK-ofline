"""
PPK DOCUMENT FACTORY v3.0 - Template Manager UI
================================================
UI for managing document templates
"""

import sys
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QTabWidget,
    QScrollArea, QFrame, QMessageBox, QFileDialog, QComboBox,
    QFormLayout, QListWidget, QListWidgetItem, QSplitter,
    QPlainTextEdit, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import (
    DOCUMENT_TEMPLATES, ALL_PLACEHOLDERS, PLACEHOLDERS,
    WORD_TEMPLATES_DIR, EXCEL_TEMPLATES_DIR, BACKUP_TEMPLATES_DIR
)
from app.templates.engine import get_template_manager


class TemplateManagerDialog(QDialog):
    """Dialog for managing document templates"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_manager = get_template_manager()
        
        self.setWindowTitle("📄 Template Manager")
        self.setMinimumSize(1000, 700)
        
        self.setup_ui()
        self.load_templates()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: Templates
        templates_tab = QWidget()
        templates_layout = QVBoxLayout(templates_tab)
        
        # Template list
        self.template_table = QTableWidget()
        self.template_table.setColumnCount(6)
        self.template_table.setHorizontalHeaderLabels([
            "Kode", "Nama", "Tipe", "Status", "Versi", "Aksi"
        ])
        self.template_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.template_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.template_table.itemSelectionChanged.connect(self.on_template_selected)
        templates_layout.addWidget(self.template_table)
        
        tabs.addTab(templates_tab, "📋 Daftar Template")
        
        # Tab 2: Upload
        upload_tab = QWidget()
        upload_layout = QVBoxLayout(upload_tab)
        
        # Upload form
        upload_group = QGroupBox("Upload Template Baru")
        upload_form = QFormLayout()
        
        self.cmb_doc_type = QComboBox()
        for code, config in DOCUMENT_TEMPLATES.items():
            self.cmb_doc_type.addItem(f"{config['name']} ({code})", code)
        upload_form.addRow("Jenis Dokumen:", self.cmb_doc_type)
        
        file_layout = QHBoxLayout()
        self.txt_file_path = QLineEdit()
        self.txt_file_path.setReadOnly(True)
        self.txt_file_path.setPlaceholderText("Pilih file template...")
        file_layout.addWidget(self.txt_file_path)
        
        btn_browse = QPushButton("📁 Browse")
        btn_browse.clicked.connect(self.browse_template)
        file_layout.addWidget(btn_browse)
        upload_form.addRow("File Template:", file_layout)
        
        self.txt_description = QTextEdit()
        self.txt_description.setMaximumHeight(80)
        self.txt_description.setPlaceholderText("Deskripsi perubahan (opsional)...")
        upload_form.addRow("Deskripsi:", self.txt_description)
        
        upload_group.setLayout(upload_form)
        upload_layout.addWidget(upload_group)
        
        # Upload button
        btn_upload = QPushButton("⬆️ Upload Template")
        btn_upload.setStyleSheet("background-color: #27ae60; color: white; padding: 15px;")
        btn_upload.clicked.connect(self.upload_template)
        upload_layout.addWidget(btn_upload)
        
        # Instructions
        instructions = QGroupBox("📋 Petunjuk Pembuatan Template")
        inst_layout = QVBoxLayout()
        
        inst_text = QPlainTextEdit()
        inst_text.setReadOnly(True)
        inst_text.setPlainText("""
PANDUAN MEMBUAT TEMPLATE:

1. FORMAT FILE
   • Word: .docx (Microsoft Word 2007+)
   • Excel: .xlsx (Microsoft Excel 2007+)

2. PLACEHOLDER
   Gunakan format {{nama_placeholder}} untuk data dinamis.
   Contoh: {{nama_paket}}, {{nilai_kontrak}}, {{ppk_nama}}
   
   Dengan format: {{placeholder:format}}
   Contoh: {{nilai_kontrak:rupiah}}, {{tanggal_spk:tanggal_long}}

3. FORMAT YANG TERSEDIA
   • rupiah    : Rp 1.500.000
   • angka     : 1.500.000
   • terbilang : satu juta lima ratus ribu rupiah
   • tanggal_long  : 15 Januari 2025
   • tanggal_short : 15/01/2025
   • tanggal_full  : Senin, 15 Januari 2025
   • nip       : 19720103 199503 1 001
   • npwp      : 01.234.567.8-951.000
   • upper     : HURUF BESAR
   • lower     : huruf kecil
   • title     : Huruf Kapital Setiap Kata

4. TIPS
   • Buat template dari dokumen yang sudah ada
   • Ganti data dengan placeholder yang sesuai
   • Test dengan satu paket sebelum digunakan massal
   • Backup template lama tersimpan otomatis
        """)
        inst_layout.addWidget(inst_text)
        instructions.setLayout(inst_layout)
        upload_layout.addWidget(instructions)
        
        tabs.addTab(upload_tab, "⬆️ Upload Template")
        
        # Tab 3: Placeholders
        placeholder_tab = QWidget()
        placeholder_layout = QVBoxLayout(placeholder_tab)
        
        # Category selector
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Kategori:"))
        
        self.cmb_category = QComboBox()
        self.cmb_category.addItem("-- Semua --", None)
        for cat in PLACEHOLDERS.keys():
            self.cmb_category.addItem(cat.title(), cat)
        self.cmb_category.currentIndexChanged.connect(self.filter_placeholders)
        cat_layout.addWidget(self.cmb_category)
        cat_layout.addStretch()
        placeholder_layout.addLayout(cat_layout)
        
        # Placeholder table
        self.placeholder_table = QTableWidget()
        self.placeholder_table.setColumnCount(5)
        self.placeholder_table.setHorizontalHeaderLabels([
            "Placeholder", "Label", "Tipe", "Required", "Kategori"
        ])
        self.placeholder_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        placeholder_layout.addWidget(self.placeholder_table)
        
        self.load_placeholders()
        
        tabs.addTab(placeholder_tab, "🔤 Daftar Placeholder")
        
        # Tab 4: Preview
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)
        
        preview_layout.addWidget(QLabel("Pilih template dari tab 'Daftar Template' untuk melihat placeholder yang digunakan."))
        
        self.preview_group = QGroupBox("Preview Template")
        preview_form = QVBoxLayout()
        
        self.lbl_preview_name = QLabel("-")
        self.lbl_preview_name.setFont(QFont("", 12, QFont.Bold))
        preview_form.addWidget(self.lbl_preview_name)
        
        self.lbl_preview_path = QLabel("-")
        self.lbl_preview_path.setStyleSheet("color: #7f8c8d;")
        preview_form.addWidget(self.lbl_preview_path)
        
        preview_form.addWidget(QLabel("\nPlaceholder yang digunakan:"))
        
        self.list_preview_placeholders = QListWidget()
        preview_form.addWidget(self.list_preview_placeholders)
        
        btn_open = QPushButton("📂 Buka File Template")
        btn_open.clicked.connect(self.open_selected_template)
        preview_form.addWidget(btn_open)
        
        self.preview_group.setLayout(preview_form)
        preview_layout.addWidget(self.preview_group)
        
        tabs.addTab(preview_tab, "👁️ Preview")
        
        layout.addWidget(tabs)
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.clicked.connect(self.load_templates)
        btn_layout.addWidget(btn_refresh)
        
        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
    
    def load_templates(self):
        """Load template list"""
        self.template_table.setRowCount(0)
        
        templates = self.template_manager.get_all_templates_status()
        
        for template in templates:
            row = self.template_table.rowCount()
            self.template_table.insertRow(row)
            
            # Code
            self.template_table.setItem(row, 0, QTableWidgetItem(template['code']))
            
            # Name
            self.template_table.setItem(row, 1, QTableWidgetItem(template['name']))
            
            # Type
            type_text = "📄 Word" if template['type'] == 'word' else "📊 Excel"
            self.template_table.setItem(row, 2, QTableWidgetItem(type_text))
            
            # Status
            status_item = QTableWidgetItem()
            if template['status'] == 'uploaded':
                status_item.setText("✅ Uploaded")
                status_item.setForeground(QColor("#27ae60"))
            elif template['status'] == 'exists':
                status_item.setText("📁 Default")
                status_item.setForeground(QColor("#3498db"))
            else:
                status_item.setText("❌ Missing")
                status_item.setForeground(QColor("#e74c3c"))
            self.template_table.setItem(row, 3, status_item)
            
            # Version
            self.template_table.setItem(row, 4, QTableWidgetItem(str(template['version'])))
            
            # Action button
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            
            if template['filepath']:
                btn_open = QPushButton("📂")
                btn_open.setToolTip("Buka file")
                btn_open.setMaximumWidth(30)
                btn_open.clicked.connect(lambda checked, fp=template['filepath']: self.open_file(fp))
                btn_layout.addWidget(btn_open)
            
            btn_upload = QPushButton("⬆️")
            btn_upload.setToolTip("Upload versi baru")
            btn_upload.setMaximumWidth(30)
            btn_upload.clicked.connect(lambda checked, code=template['code']: self.quick_upload(code))
            btn_layout.addWidget(btn_upload)
            
            self.template_table.setCellWidget(row, 5, btn_widget)
    
    def load_placeholders(self, category: str = None):
        """Load placeholder list"""
        self.placeholder_table.setRowCount(0)
        
        for key, info in ALL_PLACEHOLDERS.items():
            if category and info.get('category') != category:
                continue
            
            row = self.placeholder_table.rowCount()
            self.placeholder_table.insertRow(row)
            
            # Placeholder
            ph_item = QTableWidgetItem(f"{{{{{key}}}}}")
            ph_item.setFont(QFont("Consolas", 10))
            self.placeholder_table.setItem(row, 0, ph_item)
            
            # Label
            self.placeholder_table.setItem(row, 1, QTableWidgetItem(info.get('label', key)))
            
            # Type
            self.placeholder_table.setItem(row, 2, QTableWidgetItem(info.get('type', 'text')))
            
            # Required
            req_text = "✓" if info.get('required') else ""
            self.placeholder_table.setItem(row, 3, QTableWidgetItem(req_text))
            
            # Category
            self.placeholder_table.setItem(row, 4, QTableWidgetItem(info.get('category', '')))
    
    def filter_placeholders(self, index: int):
        category = self.cmb_category.currentData()
        self.load_placeholders(category)
    
    def on_template_selected(self):
        """Handle template selection"""
        rows = self.template_table.selectionModel().selectedRows()
        if not rows:
            return
        
        row = rows[0].row()
        code = self.template_table.item(row, 0).text()
        
        # Load preview
        template_info = self.template_manager.get_template_info(code)
        
        if template_info:
            self.lbl_preview_name.setText(f"{template_info['name']} ({code})")
            self.lbl_preview_path.setText(template_info.get('filepath', '-'))
            
            self.list_preview_placeholders.clear()
            for ph in template_info.get('placeholder_details', []):
                item = QListWidgetItem(f"{{{{{ph['name']}}}}} - {ph.get('label', ph['name'])}")
                if ph.get('required'):
                    item.setForeground(QColor("#e74c3c"))
                self.list_preview_placeholders.addItem(item)
        else:
            # Load from config
            config = DOCUMENT_TEMPLATES.get(code, {})
            self.lbl_preview_name.setText(f"{config.get('name', code)} ({code})")
            self.lbl_preview_path.setText("Template belum di-upload")
            
            self.list_preview_placeholders.clear()
            for category in config.get('placeholders', []):
                if category in PLACEHOLDERS:
                    for ph_name in PLACEHOLDERS[category].keys():
                        item = QListWidgetItem(f"{{{{{ph_name}}}}}")
                        self.list_preview_placeholders.addItem(item)
    
    def browse_template(self):
        """Browse for template file"""
        doc_type = self.cmb_doc_type.currentData()
        config = DOCUMENT_TEMPLATES.get(doc_type, {})
        
        if config.get('type') == 'word':
            filter_str = "Word Documents (*.docx)"
        else:
            filter_str = "Excel Documents (*.xlsx)"
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Pilih Template", "", filter_str
        )
        
        if filepath:
            self.txt_file_path.setText(filepath)
    
    def upload_template(self):
        """Upload new template"""
        doc_type = self.cmb_doc_type.currentData()
        filepath = self.txt_file_path.text()
        description = self.txt_description.toPlainText()
        
        if not filepath:
            QMessageBox.warning(self, "Peringatan", "Pilih file template terlebih dahulu!")
            return
        
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "Peringatan", "File tidak ditemukan!")
            return
        
        try:
            result = self.template_manager.upload_template(
                doc_type, filepath, description
            )
            
            if result['success']:
                QMessageBox.information(
                    self, "Sukses",
                    f"Template berhasil di-upload!\n\n"
                    f"Placeholder ditemukan: {len(result['placeholders'])}\n\n"
                    f"Placeholder:\n" + ", ".join(result['placeholders'][:10]) +
                    ("..." if len(result['placeholders']) > 10 else "")
                )
                
                self.txt_file_path.clear()
                self.txt_description.clear()
                self.load_templates()
            else:
                QMessageBox.warning(self, "Gagal", result.get('message', 'Upload gagal'))
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal upload template:\n{str(e)}")
    
    def quick_upload(self, code: str):
        """Quick upload for specific template"""
        # Set combo to correct type
        for i in range(self.cmb_doc_type.count()):
            if self.cmb_doc_type.itemData(i) == code:
                self.cmb_doc_type.setCurrentIndex(i)
                break
        
        # Browse
        self.browse_template()
        
        # Upload if file selected
        if self.txt_file_path.text():
            self.upload_template()
    
    def open_file(self, filepath: str):
        """Open file in default application"""
        if not filepath or not os.path.exists(filepath):
            QMessageBox.warning(self, "File tidak ditemukan", f"File tidak ada:\n{filepath}")
            return
        
        if sys.platform == 'win32':
            os.startfile(filepath)
        elif sys.platform == 'darwin':
            os.system(f'open "{filepath}"')
        else:
            os.system(f'xdg-open "{filepath}"')
    
    def open_selected_template(self):
        """Open currently selected template"""
        filepath = self.lbl_preview_path.text()
        if filepath and filepath != '-' and filepath != 'Template belum di-upload':
            self.open_file(filepath)
        else:
            QMessageBox.warning(self, "Info", "Tidak ada template yang dipilih atau template belum di-upload.")


class PlaceholderReferenceDialog(QDialog):
    """Quick reference dialog for placeholders"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔤 Referensi Placeholder")
        self.setMinimumSize(600, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍"))
        
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Cari placeholder...")
        self.txt_search.textChanged.connect(self.filter_list)
        search_layout.addWidget(self.txt_search)
        
        layout.addLayout(search_layout)
        
        # List
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.copy_placeholder)
        
        for key, info in ALL_PLACEHOLDERS.items():
            item = QListWidgetItem(f"{{{{{key}}}}} - {info.get('label', key)}")
            item.setData(Qt.UserRole, key)
            self.list_widget.addItem(item)
        
        layout.addWidget(self.list_widget)
        
        # Info
        layout.addWidget(QLabel("💡 Double-click untuk copy placeholder"))
        
        # Close
        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
    
    def filter_list(self, text: str):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def copy_placeholder(self, item: QListWidgetItem):
        key = item.data(Qt.UserRole)
        placeholder = f"{{{{{key}}}}}"
        
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(placeholder)
        
        QMessageBox.information(self, "Copied", f"Placeholder disalin:\n{placeholder}")
