"""
PPK DOCUMENT FACTORY - Dashboard Card Components
=================================================
Card components untuk dashboard utama.

Components:
- MekanismeCard: Card besar untuk UP/TUP/LS dengan statistik
- TransaksiAktifCard: Card untuk transaksi yang perlu tindakan
- SaldoUPWidget: Menampilkan sisa UP tersedia
- QuickActionBar: Tombol aksi cepat (+ Baru, dll)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QProgressBar,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from typing import Dict, Any, Optional, List


def format_rupiah(value: float) -> str:
    """Format angka ke format Rupiah."""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


class MekanismeCard(QFrame):
    """
    Card untuk menampilkan statistik per mekanisme pencairan.

    Signals:
        clicked(): Emitted when card is clicked
        action_clicked(str): Emitted when action button clicked
    """

    clicked = Signal()
    action_clicked = Signal(str)

    COLORS = {
        "UP": {"primary": "#27ae60", "light": "#d5f5e3", "dark": "#1e8449"},
        "TUP": {"primary": "#f39c12", "light": "#fef5e7", "dark": "#d68910"},
        "LS": {"primary": "#3498db", "light": "#ebf5fb", "dark": "#2980b9"},
    }

    def __init__(
        self,
        mekanisme: str,
        title: str = None,
        parent=None
    ):
        super().__init__(parent)
        self.mekanisme = mekanisme.upper()
        self.title = title or self._get_default_title()
        self.colors = self.COLORS.get(self.mekanisme, self.COLORS["UP"])

        self._setup_ui()
        self._add_shadow()

    def _get_default_title(self) -> str:
        """Get default title based on mekanisme."""
        titles = {
            "UP": "Uang Persediaan",
            "TUP": "Tambahan UP",
            "LS": "Pembayaran Langsung"
        }
        return titles.get(self.mekanisme, "Unknown")

    def _setup_ui(self):
        """Setup card UI."""
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(280, 180)
        self.setMaximumHeight(220)

        # Styling
        self.setStyleSheet(f"""
            MekanismeCard {{
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
                border-top: 4px solid {self.colors['primary']};
            }}
            MekanismeCard:hover {{
                border-color: {self.colors['primary']};
                background-color: {self.colors['light']};
            }}
        """)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()

        # Icon and title
        icon_label = QLabel(self._get_icon())
        icon_label.setStyleSheet(f"""
            font-size: 24px;
            color: {self.colors['primary']};
        """)
        header.addWidget(icon_label)

        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header.addWidget(title_label)
        header.addStretch()

        layout.addLayout(header)

        # Statistics
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)

        # Total transaksi
        self.total_label = QLabel("0")
        self.total_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {self.colors['primary']};
        """)
        stats_layout.addWidget(self.total_label, 0, 0)

        total_desc = QLabel("Transaksi Aktif")
        total_desc.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        stats_layout.addWidget(total_desc, 1, 0)

        # Nilai
        self.nilai_label = QLabel("Rp 0")
        self.nilai_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        """)
        stats_layout.addWidget(self.nilai_label, 0, 1, Qt.AlignRight)

        nilai_desc = QLabel("Total Nilai")
        nilai_desc.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        stats_layout.addWidget(nilai_desc, 1, 1, Qt.AlignRight)

        layout.addLayout(stats_layout)

        # Progress bar for completion
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #ecf0f1;
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        # Status text
        self.status_label = QLabel("0 selesai dari 0 transaksi")
        self.status_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        layout.addWidget(self.status_label)

        # Action button
        action_btn = QPushButton(f"+ Buat {self.mekanisme} Baru")
        action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['primary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {self.colors['dark']};
            }}
        """)
        action_btn.clicked.connect(lambda: self.action_clicked.emit(self.mekanisme))
        layout.addWidget(action_btn)

    def _get_icon(self) -> str:
        """Get icon for mekanisme."""
        icons = {
            "UP": "W",  # wallet
            "TUP": "+",  # plus
            "LS": "S",  # send
        }
        return icons.get(self.mekanisme, "*")

    def _add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

    def update_stats(
        self,
        total: int = 0,
        nilai: float = 0,
        selesai: int = 0
    ):
        """Update card statistics."""
        self.total_label.setText(str(total))
        self.nilai_label.setText(format_rupiah(nilai))

        # Update progress
        if total > 0:
            progress = int((selesai / total) * 100)
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"{selesai} selesai dari {total} transaksi")
        else:
            self.progress_bar.setValue(0)
            self.status_label.setText("Belum ada transaksi")

    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class TransaksiAktifCard(QFrame):
    """
    Card untuk menampilkan transaksi yang membutuhkan tindakan.

    Signals:
        item_clicked(int): Emitted when a transaction is clicked
    """

    item_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._add_shadow()

    def _setup_ui(self):
        """Setup card UI."""
        self.setStyleSheet("""
            TransaksiAktifCard {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title = QLabel("Perlu Tindakan")
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header.addWidget(title)
        header.addStretch()

        self.badge = QLabel("0")
        self.badge.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: bold;
        """)
        self.badge.hide()
        header.addWidget(self.badge)

        layout.addLayout(header)

        # Items container
        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(8)
        layout.addLayout(self.items_layout)

        # Empty state
        self.empty_label = QLabel("Tidak ada transaksi yang membutuhkan tindakan")
        self.empty_label.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
            padding: 20px;
        """)
        self.empty_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.empty_label)

    def _add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

    def set_items(self, items: List[Dict[str, Any]]):
        """Set the list of active transactions."""
        # Clear existing items
        while self.items_layout.count():
            child = self.items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not items:
            self.empty_label.show()
            self.badge.hide()
            return

        self.empty_label.hide()
        self.badge.setText(str(len(items)))
        self.badge.show()

        # Add items
        for item in items[:5]:  # Limit to 5 items
            item_widget = self._create_item_widget(item)
            self.items_layout.addWidget(item_widget)

    def _create_item_widget(self, item: Dict[str, Any]) -> QWidget:
        """Create a widget for a transaction item."""
        widget = QFrame()
        widget.setCursor(Qt.PointingHandCursor)
        widget.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
            }
            QFrame:hover {
                background-color: #ebf5fb;
            }
        """)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # Mekanisme badge
        mekanisme = item.get('mekanisme', 'UP')
        colors = MekanismeCard.COLORS.get(mekanisme, MekanismeCard.COLORS["UP"])
        badge = QLabel(mekanisme)
        badge.setFixedWidth(35)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"""
            background-color: {colors['light']};
            color: {colors['dark']};
            border-radius: 3px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: bold;
        """)
        layout.addWidget(badge)

        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        nama = QLabel(item.get('nama_kegiatan', 'Transaksi'))
        nama.setStyleSheet("font-size: 12px; color: #2c3e50; font-weight: 500;")
        info_layout.addWidget(nama)

        kode = QLabel(item.get('kode_transaksi', ''))
        kode.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        info_layout.addWidget(kode)

        layout.addLayout(info_layout)
        layout.addStretch()

        # Fase
        fase = item.get('fase_aktif', 1)
        fase_label = QLabel(f"Fase {fase}")
        fase_label.setStyleSheet("""
            background-color: #3498db;
            color: white;
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 10px;
        """)
        layout.addWidget(fase_label)

        # Click handler
        transaksi_id = item.get('id', 0)
        widget.mousePressEvent = lambda e: self.item_clicked.emit(transaksi_id)

        return widget


class SaldoUPWidget(QFrame):
    """Widget untuk menampilkan saldo UP tersedia."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._add_shadow()

    def _setup_ui(self):
        """Setup widget UI."""
        self.setStyleSheet("""
            SaldoUPWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("Saldo UP Tersedia")
        title.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(title)

        # Value
        self.value_label = QLabel("Rp 50.000.000")
        self.value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #27ae60;
        """)
        layout.addWidget(self.value_label)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #ecf0f1;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Details
        details_layout = QHBoxLayout()

        self.used_label = QLabel("Terpakai: Rp 0")
        self.used_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        details_layout.addWidget(self.used_label)

        details_layout.addStretch()

        self.max_label = QLabel("Maks: Rp 50.000.000")
        self.max_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        details_layout.addWidget(self.max_label)

        layout.addLayout(details_layout)

    def _add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

    def update_saldo(
        self,
        tersedia: float,
        terpakai: float,
        maksimal: float = 50_000_000
    ):
        """Update saldo display."""
        self.value_label.setText(format_rupiah(tersedia))
        self.used_label.setText(f"Terpakai: {format_rupiah(terpakai)}")
        self.max_label.setText(f"Maks: {format_rupiah(maksimal)}")

        # Update progress
        if maksimal > 0:
            persen = int((tersedia / maksimal) * 100)
            self.progress_bar.setValue(persen)

            # Change color based on remaining
            if persen < 20:
                color = "#e74c3c"
            elif persen < 50:
                color = "#f39c12"
            else:
                color = "#27ae60"

            self.value_label.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {color};
            """)
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #ecf0f1;
                    border: none;
                    border-radius: 4px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 4px;
                }}
            """)


class QuickActionBar(QFrame):
    """Bar dengan tombol aksi cepat."""

    action_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup action bar UI."""
        self.setStyleSheet("""
            QuickActionBar {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        # Action buttons
        actions = [
            ("new_up", "+ UP Baru", "#27ae60"),
            ("new_tup", "+ TUP Baru", "#f39c12"),
            ("new_ls", "+ LS Baru", "#3498db"),
        ]

        for action_id, text, color in actions:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {self._darken_color(color)};
                }}
            """)
            btn.clicked.connect(lambda checked, aid=action_id: self.action_clicked.emit(aid))
            layout.addWidget(btn)

        layout.addStretch()

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color."""
        # Simple darkening by reducing RGB values
        darken_map = {
            "#27ae60": "#1e8449",
            "#f39c12": "#d68910",
            "#3498db": "#2980b9",
        }
        return darken_map.get(hex_color, hex_color)
