"""
PPK DOCUMENT FACTORY - Saldo UP Widget
======================================
Widget untuk menampilkan saldo Uang Persediaan (UP) dengan:
- Nilai tersedia dan terpakai
- Progress bar dengan color coding
- Persentase penggunaan

Author: PPK Document Factory Team
Version: 4.0
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QProgressBar, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from typing import Optional

# Import batas maksimal UP dari models
try:
    from app.models.pencairan_models import BATAS_UP_MAKSIMAL
except ImportError:
    BATAS_UP_MAKSIMAL = 50_000_000  # Default Rp 50 juta


def format_rupiah(value: float) -> str:
    """Format angka ke format Rupiah."""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


class SaldoUPWidget(QFrame):
    """
    Widget untuk menampilkan saldo Uang Persediaan (UP).

    Menampilkan:
    - Nilai saldo tersedia dalam format Rupiah
    - Nilai terpakai
    - Progress bar penggunaan dengan color coding
    - Persentase penggunaan

    Color coding:
    - Hijau (#27ae60): Penggunaan < 50%
    - Kuning (#f39c12): Penggunaan 50-80%
    - Merah (#e74c3c): Penggunaan > 80%

    Signals:
        saldo_changed(): Emitted ketika saldo diupdate
        warning_threshold(): Emitted ketika saldo mencapai level warning (< 20%)

    Usage:
        widget = SaldoUPWidget()
        widget.update_saldo(tersedia=35000000, terpakai=15000000)

        # Atau set batas maksimal custom
        widget.set_batas_maksimal(100000000)
        widget.update_saldo(tersedia=70000000, terpakai=30000000)
    """

    # Signals
    saldo_changed = Signal()
    warning_threshold = Signal()  # Emitted when saldo < 20%

    # Color thresholds
    COLOR_HEALTHY = "#27ae60"  # Hijau - penggunaan < 50%
    COLOR_WARNING = "#f39c12"  # Kuning - penggunaan 50-80%
    COLOR_DANGER = "#e74c3c"   # Merah - penggunaan > 80%

    def __init__(self, parent: QWidget = None):
        """
        Initialize SaldoUPWidget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Internal state
        self._batas_maksimal: float = BATAS_UP_MAKSIMAL
        self._saldo_tersedia: float = BATAS_UP_MAKSIMAL
        self._saldo_terpakai: float = 0.0

        self._setup_ui()
        self._add_shadow()

    def _setup_ui(self) -> None:
        """Setup widget UI."""
        self.setObjectName("saldoUPWidget")
        self.setStyleSheet("""
            QFrame#saldoUPWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        # Header with title and percentage
        header_layout = QHBoxLayout()

        # Title
        title = QLabel("Saldo UP Tersedia")
        title.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Percentage label
        self.persen_label = QLabel("100%")
        self.persen_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {self.COLOR_HEALTHY};
            background-color: #d5f5e3;
            padding: 2px 8px;
            border-radius: 10px;
        """)
        header_layout.addWidget(self.persen_label)

        layout.addLayout(header_layout)

        # Main value (saldo tersedia)
        self.value_label = QLabel(format_rupiah(self._batas_maksimal))
        self.value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {self.COLOR_HEALTHY};
        """)
        layout.addWidget(self.value_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self._update_progress_style(self.COLOR_HEALTHY)
        layout.addWidget(self.progress_bar)

        # Details row
        details_layout = QHBoxLayout()
        details_layout.setSpacing(20)

        # Terpakai
        terpakai_container = QVBoxLayout()
        terpakai_container.setSpacing(2)

        terpakai_title = QLabel("Terpakai")
        terpakai_title.setStyleSheet("font-size: 10px; color: #95a5a6;")
        terpakai_container.addWidget(terpakai_title)

        self.used_label = QLabel("Rp 0")
        self.used_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #e74c3c;")
        terpakai_container.addWidget(self.used_label)

        details_layout.addLayout(terpakai_container)

        details_layout.addStretch()

        # Batas Maksimal
        maks_container = QVBoxLayout()
        maks_container.setSpacing(2)

        maks_title = QLabel("Batas Maksimal")
        maks_title.setStyleSheet("font-size: 10px; color: #95a5a6;")
        maks_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        maks_container.addWidget(maks_title)

        self.max_label = QLabel(format_rupiah(self._batas_maksimal))
        self.max_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")
        self.max_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        maks_container.addWidget(self.max_label)

        details_layout.addLayout(maks_container)

        layout.addLayout(details_layout)

    def _add_shadow(self) -> None:
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

    def _update_progress_style(self, color: str) -> None:
        """Update progress bar style with given color."""
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #ecf0f1;
                border: none;
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)

    def _get_color_for_percentage(self, persen_tersedia: float) -> str:
        """
        Get color based on percentage of remaining saldo.

        Args:
            persen_tersedia: Percentage of saldo tersedia (0-100)

        Returns:
            Color hex string
        """
        if persen_tersedia > 50:
            return self.COLOR_HEALTHY
        elif persen_tersedia > 20:
            return self.COLOR_WARNING
        else:
            return self.COLOR_DANGER

    def _get_bg_color_for_percentage(self, persen_tersedia: float) -> str:
        """Get background color for percentage badge."""
        if persen_tersedia > 50:
            return "#d5f5e3"  # Light green
        elif persen_tersedia > 20:
            return "#fef5e7"  # Light orange
        else:
            return "#fdedec"  # Light red

    def set_batas_maksimal(self, batas: float) -> None:
        """
        Set batas maksimal UP.

        Args:
            batas: Batas maksimal dalam Rupiah
        """
        self._batas_maksimal = batas
        self.max_label.setText(format_rupiah(batas))

        # Recalculate if we have existing values
        self._update_display()

    def update_saldo(self, tersedia: float, terpakai: float) -> None:
        """
        Update saldo display.

        Args:
            tersedia: Saldo tersedia dalam Rupiah
            terpakai: Saldo yang sudah terpakai dalam Rupiah
        """
        self._saldo_tersedia = tersedia
        self._saldo_terpakai = terpakai

        self._update_display()

        # Emit signals
        self.saldo_changed.emit()

        # Check warning threshold
        if self._batas_maksimal > 0:
            persen = (tersedia / self._batas_maksimal) * 100
            if persen < 20:
                self.warning_threshold.emit()

    def _update_display(self) -> None:
        """Update all display elements based on current state."""
        # Calculate percentage
        persen_tersedia = 100.0
        if self._batas_maksimal > 0:
            persen_tersedia = (self._saldo_tersedia / self._batas_maksimal) * 100

        # Clamp to 0-100
        persen_tersedia = max(0, min(100, persen_tersedia))

        # Get color based on percentage
        color = self._get_color_for_percentage(persen_tersedia)
        bg_color = self._get_bg_color_for_percentage(persen_tersedia)

        # Update value label
        self.value_label.setText(format_rupiah(self._saldo_tersedia))
        self.value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {color};
        """)

        # Update percentage label
        self.persen_label.setText(f"{persen_tersedia:.0f}%")
        self.persen_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {color};
            background-color: {bg_color};
            padding: 2px 8px;
            border-radius: 10px;
        """)

        # Update progress bar
        self.progress_bar.setValue(int(persen_tersedia))
        self._update_progress_style(color)

        # Update terpakai label
        self.used_label.setText(format_rupiah(self._saldo_terpakai))

    def get_saldo_tersedia(self) -> float:
        """
        Get current saldo tersedia.

        Returns:
            Saldo tersedia dalam Rupiah
        """
        return self._saldo_tersedia

    def get_saldo_terpakai(self) -> float:
        """
        Get current saldo terpakai.

        Returns:
            Saldo terpakai dalam Rupiah
        """
        return self._saldo_terpakai

    def get_batas_maksimal(self) -> float:
        """
        Get batas maksimal UP.

        Returns:
            Batas maksimal dalam Rupiah
        """
        return self._batas_maksimal

    def get_persentase_tersedia(self) -> float:
        """
        Get percentage of saldo tersedia.

        Returns:
            Percentage (0-100)
        """
        if self._batas_maksimal > 0:
            return (self._saldo_tersedia / self._batas_maksimal) * 100
        return 100.0

    def reset(self) -> None:
        """Reset saldo to maksimal (full)."""
        self._saldo_tersedia = self._batas_maksimal
        self._saldo_terpakai = 0.0
        self._update_display()
