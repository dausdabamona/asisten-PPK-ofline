"""
Dokumen Checklist Component - Menampilkan daftar dokumen wajib/opsional per fase
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QMessageBox, QFileDialog, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QColor
from typing import List, Dict, Optional
import os


class DokumenItem(QFrame):
    """Single item dalam dokumen checklist"""
    
    status_changed = Signal(str, str)  # dokumen_id, status
    file_selected = Signal(str, str)  # dokumen_id, file_path
    view_clicked = Signal(str)  # dokumen_id
    
    STATUS_COLORS = {
        'pending': '#ecf0f1',
        'draft': '#fff3cd',
        'final': '#d4edda',
        'signed': '#c3e6cb',
        'uploaded': '#d4edda'
    }
    
    STATUS_ICON = {
        'pending': '⭕',
        'draft': '✏️',
        'final': '📄',
        'signed': '✅',
        'uploaded': '📤'
    }
    
    def __init__(self, dokumen: Dict, dokumen_id: str = None):
        super().__init__()
        self.dokumen = dokumen
        self.dokumen_id = dokumen_id or dokumen.get('kode_dokumen')
        self.status = dokumen.get('status', 'pending')
        self.file_path = dokumen.get('file_path')
        
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0px;
            }
            QFrame:hover {
                background-color: #f9f9f9;
                border: 1px solid #3498db;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI untuk dokumen item"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Status & Kategori
        status_layout = QVBoxLayout()
        status_layout.setSpacing(3)
        
        status_icon = QLabel(self.STATUS_ICON.get(self.status, '❓'))
        status_icon.setFixedSize(QSize(30, 30))
        status_font = QFont()
        status_font.setPointSize(14)
        status_icon.setFont(status_font)
        
        kategori_label = QLabel(self._get_kategori_text())
        kategori_font = QFont()
        kategori_font.setPointSize(7)
        kategori_font.setBold(True)
        kategori_label.setFont(kategori_font)
        kategori_label.setStyleSheet("color: #7f8c8d;")
        
        status_layout.addWidget(status_icon)
        status_layout.addWidget(kategori_label)
        status_layout.addStretch()
        
        # Info Dokumen
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        nama_label = QLabel(self.dokumen.get('nama_dokumen', 'Unknown'))
        nama_font = QFont()
        nama_font.setPointSize(10)
        nama_font.setBold(True)
        nama_label.setFont(nama_font)
        
        status_text = QLabel(f"Status: {self._get_status_text()}")
        status_text_font = QFont()
        status_text_font.setPointSize(8)
        status_text.setFont(status_text_font)
        
        if self.file_path:
            file_label = QLabel(f"📁 {os.path.basename(self.file_path)}")
            file_font = QFont()
            file_font.setPointSize(8)
            file_label.setFont(file_font)
            file_label.setStyleSheet("color: #27ae60;")
            info_layout.addWidget(file_label)
        
        info_layout.addWidget(nama_label)
        info_layout.addWidget(status_text)
        info_layout.addStretch()
        
        # Action Buttons
        action_layout = QVBoxLayout()
        action_layout.setSpacing(5)
        
        if self.dokumen.get('kategori') == 'upload':
            upload_btn = QPushButton("📤 Upload")
            upload_btn.setFixedWidth(90)
            upload_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                    font-size: 9px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            upload_btn.clicked.connect(self.on_upload)
            action_layout.addWidget(upload_btn)
        else:
            create_btn = QPushButton("+ Buat")
            create_btn.setFixedWidth(90)
            create_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                    font-size: 9px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            create_btn.clicked.connect(self.on_create)
            action_layout.addWidget(create_btn)
        
        if self.file_path and self.dokumen.get('kategori') != 'upload':
            view_btn = QPushButton("📄 Lihat")
            view_btn.setFixedWidth(90)
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                    font-size: 9px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            view_btn.clicked.connect(self.on_view)
            action_layout.addWidget(view_btn)
        
        action_layout.addStretch()
        
        # Combine all layouts
        layout.addLayout(status_layout, 0)
        layout.addLayout(info_layout, 1)
        layout.addLayout(action_layout, 0)
        
        self.setLayout(layout)
    
    def _get_kategori_text(self) -> str:
        """Get kategori text"""
        kategori = self.dokumen.get('kategori', 'wajib')
        mapping = {
            'wajib': '⚠️ Wajib',
            'opsional': '💡 Opsional',
            'upload': '📤 Upload',
            'kondisional': '❓ Kondisional'
        }
        return mapping.get(kategori, kategori)
    
    def _get_status_text(self) -> str:
        """Get status text"""
        mapping = {
            'pending': 'Menunggu',
            'draft': 'Draft',
            'final': 'Final',
            'signed': 'Ditandatangani',
            'uploaded': 'Terupload'
        }
        return mapping.get(self.status, self.status)
    
    def on_create(self):
        """Handle create button clicked"""
        # This will be handled by parent
        self.status_changed.emit(self.dokumen_id, 'draft')
    
    def on_upload(self):
        """Handle upload button clicked"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih File Dokumen",
            "",
            "All Files (*.*)"
        )
        
        if file_path:
            self.file_path = file_path
            self.file_selected.emit(self.dokumen_id, file_path)
            self.status = 'uploaded'
            self.update_status()
    
    def on_view(self):
        """Handle view button clicked"""
        if self.file_path:
            self.view_clicked.emit(self.dokumen_id)
    
    def update_status(self, status: str = None):
        """Update status dokumen"""
        if status:
            self.status = status
        
        # Update UI
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {self.STATUS_COLORS.get(self.status, '#ecf0f1')};
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0px;
                background-color: {self.STATUS_COLORS.get(self.status, '#ffffff')};
            }}
        """)


class DokumenChecklist(QWidget):
    """Dokumen Checklist - menampilkan semua dokumen per fase"""
    
    dokumen_created = Signal(str)  # dokumen_id
    dokumen_uploaded = Signal(str, str)  # dokumen_id, file_path
    dokumen_viewed = Signal(str)  # dokumen_id
    
    def __init__(self, fase: int = 1, dokumen_list: List[Dict] = None, parent=None):
        super().__init__(parent)
        self.fase = fase
        self.dokumen_list = dokumen_list or []
        self.dokumen_items = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI untuk checklist"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Scroll area untuk dokumen items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #f5f6fa;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 4px;
            }
        """)
        
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(5)
        
        # Group by kategori
        kategori_groups = {
            'wajib': ('⚠️ Dokumen Wajib', []),
            'opsional': ('💡 Dokumen Opsional', []),
            'kondisional': ('❓ Dokumen Kondisional', []),
            'upload': ('📤 Upload Dokumen', [])
        }
        
        for dok in self.dokumen_list:
            kategori = dok.get('kategori', 'wajib')
            if kategori in kategori_groups:
                kategori_groups[kategori][1].append(dok)
        
        for kategori, (title, dok_list) in kategori_groups.items():
            if dok_list:
                # Category header
                header = QLabel(title)
                header_font = QFont()
                header_font.setPointSize(9)
                header_font.setBold(True)
                header.setFont(header_font)
                header.setStyleSheet("color: #2c3e50; margin-top: 10px;")
                container_layout.addWidget(header)
                
                # Items
                for dok in dok_list:
                    item = DokumenItem(dok)
                    item.status_changed.connect(self.on_dokumen_status_changed)
                    item.file_selected.connect(self.on_dokumen_file_selected)
                    item.view_clicked.connect(self.on_dokumen_view_clicked)
                    
                    self.dokumen_items[dok.get('kode_dokumen')] = item
                    container_layout.addWidget(item)
        
        container_layout.addStretch()
        container.setLayout(container_layout)
        scroll.setWidget(container)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
    
    def on_dokumen_status_changed(self, dokumen_id: str, status: str):
        """Handle dokumen status changed"""
        self.dokumen_created.emit(dokumen_id)
    
    def on_dokumen_file_selected(self, dokumen_id: str, file_path: str):
        """Handle dokumen file selected"""
        self.dokumen_uploaded.emit(dokumen_id, file_path)
    
    def on_dokumen_view_clicked(self, dokumen_id: str):
        """Handle dokumen view clicked"""
        self.dokumen_viewed.emit(dokumen_id)
    
    def update_dokumen_list(self, dokumen_list: List[Dict]):
        """Update dokumen list dan refresh UI"""
        self.dokumen_list = dokumen_list
        # Clear dan rebuild
        for widget in self.findChildren(DokumenItem):
            widget.deleteLater()
        self.dokumen_items.clear()
        self.setup_ui()
    
    def get_status_summary(self) -> Dict[str, int]:
        """Get summary status dokumen"""
        summary = {
            'pending': 0,
            'draft': 0,
            'final': 0,
            'signed': 0,
            'uploaded': 0
        }
        
        for item in self.dokumen_items.values():
            status = item.status
            if status in summary:
                summary[status] += 1
        
        return summary
    
    def is_semua_wajib_selesai(self) -> bool:
        """Check if semua dokumen wajib sudah selesai"""
        for dok in self.dokumen_list:
            if dok.get('kategori') == 'wajib':
                item_id = dok.get('kode_dokumen')
                if item_id in self.dokumen_items:
                    item = self.dokumen_items[item_id]
                    if item.status == 'pending':
                        return False
        
        return True
