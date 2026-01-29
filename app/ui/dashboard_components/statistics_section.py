"""
PPK DOCUMENT FACTORY - Statistics Section Component
====================================================
Section untuk menampilkan statistik pencairan dana (UP, TUP, LS).

Komponen ini menggabungkan 3 MekanismeCard dalam layout horizontal
dan menyediakan interface untuk update data statistik.

Author: PPK Document Factory Team
Version: 4.0
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QFrame, QProgressBar, QGraphicsDropShadowEffect,
    QPushButton, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from typing import Dict, Any, Optional

from app.ui.icons.icon_provider import IconProvider


def format_rupiah(value: float) -> str:
    """Format angka ke format Rupiah."""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


class MekanismeStatCard(QFrame):
    """
    Card untuk menampilkan statistik per mekanisme pencairan.

    Signals:
        clicked(): Emitted when card is clicked
        action_clicked(str): Emitted when action button clicked (mekanisme)
    """

    clicked = Signal()
    action_clicked = Signal(str)

    # Color schemes per mekanisme
    COLORS = {
        "UP": {"primary": "#27ae60", "light": "#d5f5e3", "dark": "#1e8449"},
        "TUP": {"primary": "#f39c12", "light": "#fef5e7", "dark": "#d68910"},
        "LS": {"primary": "#3498db", "light": "#ebf5fb", "dark": "#2980b9"},
    }

    # Icon names per mekanisme
    ICONS = {
        "UP": "wallet",
        "TUP": "plus-circle",
        "LS": "send",
    }

    # Default titles
    TITLES = {
        "UP": "Uang Persediaan",
        "TUP": "Tambahan UP",
        "LS": "Pembayaran Langsung",
    }

    def __init__(
        self,
        mekanisme: str,
        title: str = None,
        parent: QWidget = None
    ):
        """
        Initialize MekanismeStatCard.

        Args:
            mekanisme: Mekanisme pencairan (UP, TUP, LS)
            title: Custom title (optional, uses default if not provided)
            parent: Parent widget
        """
        super().__init__(parent)
        self.mekanisme = mekanisme.upper()
        self.title = title or self.TITLES.get(self.mekanisme, "Unknown")
        self.colors = self.COLORS.get(self.mekanisme, self.COLORS["UP"])
        self._icon_name = self.ICONS.get(self.mekanisme, "wallet")

        self._setup_ui()
        self._add_shadow()

    def _setup_ui(self) -> None:
        """Setup card UI."""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(280, 180)
        self.setMaximumHeight(220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Styling
        self.setStyleSheet(f"""
            MekanismeStatCard {{
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
                border-top: 4px solid {self.colors['primary']};
            }}
            MekanismeStatCard:hover {{
                border-color: {self.colors['primary']};
                background-color: {self.colors['light']};
            }}
        """)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        # Header with icon and title
        header = QHBoxLayout()
        header.setSpacing(10)

        # Icon using IconProvider
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(28, 28)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_icon()
        header.addWidget(self.icon_label)

        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header.addWidget(title_label)
        header.addStretch()

        layout.addLayout(header)

        # Statistics grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)

        # Total transaksi (big number)
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

        # Nilai (money)
        self.nilai_label = QLabel("Rp 0")
        self.nilai_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        """)
        stats_layout.addWidget(self.nilai_label, 0, 1, Qt.AlignmentFlag.AlignRight)

        nilai_desc = QLabel("Total Nilai")
        nilai_desc.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        stats_layout.addWidget(nilai_desc, 1, 1, Qt.AlignmentFlag.AlignRight)

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
        self.status_label = QLabel("Belum ada transaksi")
        self.status_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        layout.addWidget(self.status_label)

        # Action button
        action_btn = QPushButton(f"+ Buat {self.mekanisme} Baru")
        action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
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

    def _update_icon(self) -> None:
        """Update icon using IconProvider."""
        try:
            pixmap = IconProvider.get_pixmap(
                self._icon_name,
                size=24,
                color=self.colors['primary']
            )
            if not pixmap.isNull():
                self.icon_label.setPixmap(pixmap)
            else:
                # Fallback to text
                self.icon_label.setText(self.mekanisme[0])
                self.icon_label.setStyleSheet(f"""
                    font-size: 18px;
                    font-weight: bold;
                    color: {self.colors['primary']};
                """)
        except Exception:
            # Fallback to text
            self.icon_label.setText(self.mekanisme[0])
            self.icon_label.setStyleSheet(f"""
                font-size: 18px;
                font-weight: bold;
                color: {self.colors['primary']};
            """)

    def _add_shadow(self) -> None:
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
    ) -> None:
        """
        Update card statistics.

        Args:
            total: Total jumlah transaksi aktif
            nilai: Total nilai transaksi dalam Rupiah
            selesai: Jumlah transaksi yang sudah selesai
        """
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

    def mousePressEvent(self, event) -> None:
        """Handle mouse press to emit clicked signal."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class StatisticsSection(QWidget):
    """
    Section yang menampilkan statistik pencairan dana untuk UP, TUP, dan LS.

    Komponen ini menggabungkan 3 MekanismeStatCard dalam layout horizontal
    dengan responsive sizing.

    Signals:
        card_clicked(str): Emitted when a card is clicked, dengan mekanisme (UP/TUP/LS)
        action_clicked(str): Emitted when action button clicked, dengan mekanisme

    Usage:
        section = StatisticsSection()
        section.card_clicked.connect(self.on_card_clicked)

        # Update single mekanisme
        section.set_mekanisme_stats("UP", total=5, nilai=25000000, selesai=2)

        # Update all at once
        section.update_statistics({
            "UP": {"total": 5, "nilai": 25000000, "selesai": 2},
            "TUP": {"total": 2, "nilai": 10000000, "selesai": 1},
            "LS": {"total": 8, "nilai": 150000000, "selesai": 5},
        })
    """

    # Signals
    card_clicked = Signal(str)  # mekanisme
    action_clicked = Signal(str)  # mekanisme

    def __init__(self, parent: QWidget = None):
        """
        Initialize StatisticsSection.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Store card references
        self._cards: Dict[str, MekanismeStatCard] = {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup section UI with 3 cards."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Section title (optional, can be hidden)
        self.title_label = QLabel("Statistik Pencairan Dana")
        self.title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        self.title_label.hide()  # Hidden by default
        layout.addWidget(self.title_label)

        # Cards container
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # Create cards for each mekanisme
        for mekanisme in ["UP", "TUP", "LS"]:
            card = MekanismeStatCard(mekanisme)
            card.clicked.connect(lambda m=mekanisme: self.card_clicked.emit(m))
            card.action_clicked.connect(self.action_clicked.emit)

            self._cards[mekanisme] = card
            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)

    def set_title_visible(self, visible: bool) -> None:
        """
        Show or hide section title.

        Args:
            visible: True to show, False to hide
        """
        self.title_label.setVisible(visible)

    def set_title(self, title: str) -> None:
        """
        Set section title text.

        Args:
            title: Title text
        """
        self.title_label.setText(title)

    def set_mekanisme_stats(
        self,
        mekanisme: str,
        total: int = 0,
        nilai: float = 0,
        selesai: int = 0
    ) -> None:
        """
        Set statistics for a specific mekanisme.

        Args:
            mekanisme: Mekanisme (UP, TUP, LS)
            total: Total jumlah transaksi aktif
            nilai: Total nilai transaksi dalam Rupiah
            selesai: Jumlah transaksi yang sudah selesai
        """
        mekanisme = mekanisme.upper()
        if mekanisme in self._cards:
            self._cards[mekanisme].update_stats(total, nilai, selesai)

    def update_statistics(self, stats: Dict[str, Dict[str, Any]]) -> None:
        """
        Update statistics for all mekanisme at once.

        Args:
            stats: Dictionary dengan struktur:
                {
                    "UP": {"total": int, "nilai": float, "selesai": int},
                    "TUP": {"total": int, "nilai": float, "selesai": int},
                    "LS": {"total": int, "nilai": float, "selesai": int},
                }

        Example:
            section.update_statistics({
                "UP": {"total": 5, "nilai": 25000000, "selesai": 2},
                "TUP": {"total": 2, "nilai": 10000000, "selesai": 1},
                "LS": {"total": 8, "nilai": 150000000, "selesai": 5},
            })
        """
        for mekanisme, data in stats.items():
            mekanisme = mekanisme.upper()
            if mekanisme in self._cards:
                self._cards[mekanisme].update_stats(
                    total=data.get("total", 0),
                    nilai=data.get("nilai", 0),
                    selesai=data.get("selesai", 0)
                )

    def get_card(self, mekanisme: str) -> Optional[MekanismeStatCard]:
        """
        Get card widget for a specific mekanisme.

        Args:
            mekanisme: Mekanisme (UP, TUP, LS)

        Returns:
            MekanismeStatCard or None if not found
        """
        return self._cards.get(mekanisme.upper())

    def reset_statistics(self) -> None:
        """Reset all statistics to zero."""
        for card in self._cards.values():
            card.update_stats(total=0, nilai=0, selesai=0)
