"""
PPK DOCUMENT FACTORY - Dokumen Checklist Component
===================================================
Checklist dokumen per fase dengan status dan aksi.

Features:
- List dokumen dengan kategori (wajib, opsional, upload, kondisional)
- Status dokumen (pending, draft, final, signed, uploaded)
- Tombol aksi per dokumen (Buat, Lihat, Edit, Upload)
- Progress indicator per fase
- Responsive button layout (wraps when window is resized)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QScrollArea, QSizePolicy,
    QGraphicsDropShadowEffect, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from typing import Dict, Any, List, Optional

from .flow_layout import FlowLayout


class DokumenItem(QFrame):
    """Individual document item in checklist."""

    action_clicked = Signal(str, str)  # kode_dokumen, action

    STATUS_STYLES = {
        "pending": {"icon": "?", "color": "#bdc3c7", "text": "Belum dibuat"},
        "draft": {"icon": "D", "color": "#f39c12", "text": "Draft"},
        "final": {"icon": "F", "color": "#3498db", "text": "Final"},
        "signed": {"icon": "S", "color": "#27ae60", "text": "Ditandatangani"},
        "uploaded": {"icon": "U", "color": "#9b59b6", "text": "Diupload"},
    }

    KATEGORI_STYLES = {
        "wajib": {"bg": "#fdeaea", "color": "#e74c3c", "text": "Wajib"},
        "opsional": {"bg": "#e8f6fd", "color": "#3498db", "text": "Opsional"},
        "upload": {"bg": "#f5eef8", "color": "#9b59b6", "text": "Upload"},
        "kondisional": {"bg": "#fef5e7", "color": "#f39c12", "text": "Kondisional"},
    }

    def __init__(
        self,
        kode: str,
        nama: str,
        kategori: str = "wajib",
        status: str = "pending",
        deskripsi: str = None,
        template: str = None,
        fase: int = 1,
        file_path: str = None,
        parent=None
    ):
        super().__init__(parent)
        self.kode = kode
        self.nama = nama
        self.kategori = kategori
        self.status = status
        self.deskripsi = deskripsi
        self.template = template
        self.fase = fase
        self.file_path = file_path  # Path to generated/uploaded file

        self._setup_ui()

    def _setup_ui(self):
        """Setup item UI."""
        self.setStyleSheet("""
            DokumenItem {
                background-color: #ffffff;
                border-bottom: 1px solid #f5f6fa;
            }
            DokumenItem:hover {
                background-color: #f8f9fa;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)

        # Top row: Status icon + Document info
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)

        # Status icon
        status_style = self.STATUS_STYLES.get(self.status, self.STATUS_STYLES["pending"])
        self.status_icon = QLabel(status_style["icon"])
        self.status_icon.setFixedSize(28, 28)
        self.status_icon.setAlignment(Qt.AlignCenter)
        self.status_icon.setStyleSheet(f"""
            background-color: {status_style['color']};
            color: white;
            border-radius: 14px;
            font-weight: bold;
            font-size: 12px;
        """)
        self.status_icon.setToolTip(status_style["text"])
        top_layout.addWidget(self.status_icon)

        # Document info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        # Name with kategori badge
        name_layout = QHBoxLayout()
        name_layout.setSpacing(8)

        name_label = QLabel(self.nama)
        name_label.setStyleSheet("""
            font-size: 13px;
            color: #2c3e50;
            font-weight: 500;
        """)
        name_layout.addWidget(name_label)

        # Status badge (draft, final, signed, etc.)
        if self.status != "pending":
            status_badge = QLabel(status_style["text"])
            status_badge.setStyleSheet(f"""
                background-color: {status_style['color']}20;
                color: {status_style['color']};
                border-radius: 8px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 500;
            """)
            name_layout.addWidget(status_badge)

        # Kategori badge
        kat_style = self.KATEGORI_STYLES.get(self.kategori, self.KATEGORI_STYLES["wajib"])
        kat_badge = QLabel(kat_style["text"])
        kat_badge.setStyleSheet(f"""
            background-color: {kat_style['bg']};
            color: {kat_style['color']};
            border-radius: 8px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 500;
        """)
        name_layout.addWidget(kat_badge)
        name_layout.addStretch()

        info_layout.addLayout(name_layout)

        # Description
        if self.deskripsi:
            desc_label = QLabel(self.deskripsi)
            desc_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
            info_layout.addWidget(desc_label)

        top_layout.addLayout(info_layout, 1)
        layout.addLayout(top_layout)

        # Action buttons container (uses FlowLayout for responsive wrapping)
        self.actions_widget = QWidget()
        self.actions_layout = FlowLayout(self.actions_widget, margin=0, h_spacing=5, v_spacing=5)
        
        self._populate_action_buttons()
        
        layout.addWidget(self.actions_widget)

    def _populate_action_buttons(self):
        """Populate action buttons based on status and kategori."""
        # Clear existing buttons
        while self.actions_layout.count():
            item = self.actions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Determine which actions to show based on status and kategori
        if self.kategori == "upload" or self.template is None:
            # Upload-only documents
            if self.status == "pending":
                self._add_action_btn("upload", "📤 Upload", "#9b59b6")
            else:
                self._add_action_btn("open", "📂 Buka", "#3498db")
                self._add_action_btn("upload", "🔄 Ganti", "#95a5a6")
        else:
            # Template-based documents
            if self.status == "pending":
                # Belum dibuat - tombol Buat (akan jadi draft)
                self._add_action_btn("create", "✏️ Buat Draft", "#27ae60")
                self._add_action_btn("upload_arsip", "📁 Arsip", "#9b59b6")
            elif self.status == "draft":
                # Draft - tombol Buka, Edit/Generate Ulang, Upload TTD
                self._add_action_btn("open", "📂 Buka", "#3498db")
                self._add_action_btn("edit", "✏️ Edit", "#f39c12")
                self._add_action_btn("upload_signed", "📝 Upload TTD", "#27ae60")
            elif self.status == "signed":
                # Sudah di-TTD - tombol Buka, Upload Final
                self._add_action_btn("open", "📂 Buka", "#3498db")
                self._add_action_btn("upload_final", "📤 Upload Final", "#9b59b6")
            elif self.status == "uploaded":
                # Sudah diupload - tombol Buka saja
                self._add_action_btn("open", "📂 Buka", "#3498db")
                self._add_action_btn("open_folder", "📁 Folder", "#7f8c8d")
            else:  # final
                # Final - tombol Buka, Edit
                self._add_action_btn("open", "📂 Buka", "#3498db")
                self._add_action_btn("edit", "✏️ Edit", "#f39c12")
                self._add_action_btn("upload_arsip", "📁 Arsip", "#9b59b6")

    def _add_action_btn(self, action: str, text: str, color: str):
        """Add action button to FlowLayout."""
        btn = QPushButton(text)
        btn.setFixedHeight(28)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
        """)
        btn.clicked.connect(lambda checked, a=action: self.action_clicked.emit(self.kode, a))
        self.actions_layout.addWidget(btn)

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color."""
        darken_map = {
            "#27ae60": "#1e8449",
            "#f39c12": "#d68910",
            "#3498db": "#2980b9",
            "#9b59b6": "#7d3c98",
            "#95a5a6": "#7f8c8d",
            "#7f8c8d": "#6c7a7d",
        }
        return darken_map.get(hex_color, hex_color)

    def set_status(self, status: str, file_path: str = None):
        """Update document status and refresh buttons."""
        self.status = status
        if file_path:
            self.file_path = file_path
        
        # Update status icon
        status_style = self.STATUS_STYLES.get(self.status, self.STATUS_STYLES["pending"])
        self.status_icon.setText(status_style["icon"])
        self.status_icon.setStyleSheet(f"""
            background-color: {status_style['color']};
            color: white;
            border-radius: 14px;
            font-weight: bold;
            font-size: 12px;
        """)
        self.status_icon.setToolTip(status_style["text"])
        
        # Refresh action buttons
        self._populate_action_buttons()


class DokumenChecklist(QFrame):
    """
    Checklist dokumen untuk satu fase.

    Signals:
        dokumen_action(str, str, int): kode_dokumen, action, fase
    """

    dokumen_action = Signal(str, str, int)

    def __init__(
        self,
        fase: int,
        nama_fase: str = None,
        parent=None
    ):
        super().__init__(parent)
        self.fase = fase
        self.nama_fase = nama_fase or f"Fase {fase}"
        self._items: List[DokumenItem] = []

        self._setup_ui()
        self._add_shadow()

    def _setup_ui(self):
        """Setup checklist UI."""
        self.setObjectName("dokumenChecklist")
        self.setStyleSheet("""
            #dokumenChecklist {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("""
            background-color: #f8f9fa;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border-bottom: 1px solid #ecf0f1;
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 12, 15, 12)

        # Title
        title = QLabel(f"Dokumen {self.nama_fase}")
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Progress
        self.progress_label = QLabel("0/0 selesai")
        self.progress_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        header_layout.addWidget(self.progress_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(80)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #ecf0f1;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
        header_layout.addWidget(self.progress_bar)

        main_layout.addWidget(header)

        # Scroll area for items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.items_container = QWidget()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(0)

        # Empty state
        self.empty_label = QLabel("Tidak ada dokumen untuk fase ini")
        self.empty_label.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
            padding: 30px;
        """)
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.items_layout.addWidget(self.empty_label)

        scroll.setWidget(self.items_container)
        main_layout.addWidget(scroll)

    def _add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

    def set_dokumen(self, dokumen_list: List[Dict[str, Any]]):
        """Set the list of documents for this fase."""
        # Clear existing items
        self._items.clear()
        while self.items_layout.count():
            child = self.items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not dokumen_list:
            self.empty_label = QLabel("Tidak ada dokumen untuk fase ini")
            self.empty_label.setStyleSheet("""
                font-size: 12px;
                color: #7f8c8d;
                padding: 30px;
            """)
            self.empty_label.setAlignment(Qt.AlignCenter)
            self.items_layout.addWidget(self.empty_label)
            self._update_progress(0, 0)
            return

        # Add document items
        selesai = 0
        for dok in dokumen_list:
            item = DokumenItem(
                kode=dok.get('kode', ''),
                nama=dok.get('nama', 'Dokumen'),
                kategori=dok.get('kategori', 'wajib'),
                status=dok.get('status', 'pending'),
                deskripsi=dok.get('deskripsi'),
                template=dok.get('template'),
                fase=self.fase,
                file_path=dok.get('file_path'),
            )
            item.action_clicked.connect(
                lambda kode, action, f=self.fase: self.dokumen_action.emit(kode, action, f)
            )
            self._items.append(item)
            self.items_layout.addWidget(item)

            # Count completed (draft counts as in-progress, not completed)
            if dok.get('status') in ['final', 'signed', 'uploaded']:
                selesai += 1

        # Add stretch
        self.items_layout.addStretch()

        # Update progress
        self._update_progress(selesai, len(dokumen_list))

    def _update_progress(self, selesai: int, total: int):
        """Update progress display."""
        self.progress_label.setText(f"{selesai}/{total} selesai")

        if total > 0:
            persen = int((selesai / total) * 100)
            self.progress_bar.setValue(persen)

            # Change color based on progress
            if persen == 100:
                color = "#27ae60"
            elif persen >= 50:
                color = "#3498db"
            else:
                color = "#f39c12"

            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #ecf0f1;
                    border: none;
                    border-radius: 3px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 3px;
                }}
            """)
        else:
            self.progress_bar.setValue(0)

    def update_dokumen_status(self, kode: str, status: str):
        """Update status of a specific document."""
        for item in self._items:
            if item.kode == kode:
                item.set_status(status)
                break

    def get_progress(self) -> Dict[str, int]:
        """Get progress counts."""
        total = len(self._items)
        selesai = sum(1 for item in self._items if item.status in ['final', 'signed', 'uploaded'])
        wajib_total = sum(1 for item in self._items if item.kategori == 'wajib')
        wajib_selesai = sum(1 for item in self._items
                           if item.kategori == 'wajib' and item.status in ['final', 'signed', 'uploaded'])

        return {
            'total': total,
            'selesai': selesai,
            'wajib_total': wajib_total,
            'wajib_selesai': wajib_selesai,
        }
