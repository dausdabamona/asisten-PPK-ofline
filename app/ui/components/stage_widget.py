"""
Stage Widget Component
=======================
Widget untuk menampilkan stage workflow pengadaan.

Author: PPK Document Factory Team
Version: 1.0
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class StageWidget(QWidget):
    """Widget representing a single workflow stage."""

    clicked = Signal(str)

    COLORS = {
        'pending': '#bdc3c7',
        'in_progress': '#f39c12',
        'completed': '#27ae60',
        'skipped': '#95a5a6',
        'locked': '#e74c3c',
    }

    ICONS = {
        'pending': '\u23f3',      # ⏳
        'in_progress': '\U0001f504',  # 🔄
        'completed': '\u2705',    # ✅
        'skipped': '\u23ed\ufe0f',     # ⏭️
        'locked': '\U0001f512',   # 🔒
    }

    STATUS_TEXT = {
        'pending': 'Menunggu',
        'in_progress': 'Sedang Proses',
        'completed': 'Selesai',
        'skipped': 'Dilewati',
        'locked': 'Terkunci',
    }

    def __init__(self, stage_code: str, stage_name: str, parent=None):
        super().__init__(parent)
        self.stage_code = stage_code
        self.stage_name = stage_name
        self.status = 'pending'
        self.is_current = False
        self.is_allowed = False

        self._setup_ui()

    def _setup_ui(self):
        """Setup widget UI."""
        self.setMinimumHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Status indicator
        self.status_indicator = QLabel(self.ICONS['pending'])
        self.status_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_indicator.setFont(QFont("", 20))
        layout.addWidget(self.status_indicator)

        # Stage name
        self.name_label = QLabel(self.stage_name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(self.name_label)

        # Status text
        self.status_label = QLabel(self.STATUS_TEXT['pending'])
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("", 8))
        layout.addWidget(self.status_label)

        self._update_style()

    def set_status(self, status: str, is_current: bool = False, is_allowed: bool = False):
        """Set stage status.

        Args:
            status: Status string ('pending', 'in_progress', 'completed', 'skipped', 'locked')
            is_current: Whether this is the current active stage
            is_allowed: Whether clicking this stage is allowed
        """
        self.status = status
        self.is_current = is_current
        self.is_allowed = is_allowed
        self._update_style()

    def _update_style(self):
        """Update styling based on state."""
        color = self.COLORS.get(self.status, '#bdc3c7')

        # Status indicator
        self.status_indicator.setText(self.ICONS.get(self.status, self.ICONS['pending']))

        # Status text
        self.status_label.setText(self.STATUS_TEXT.get(self.status, 'Menunggu'))

        # Frame style
        border_width = 3 if self.is_current else 1
        bg_color = '#fff9e6' if self.is_current else 'white'

        self.setStyleSheet(f"""
            StageWidget {{
                background-color: {bg_color};
                border: {border_width}px solid {color};
                border-radius: 8px;
            }}
            StageWidget:hover {{
                background-color: #f8f9fa;
            }}
        """)

        self.status_label.setStyleSheet(f"color: {color};")

    def mousePressEvent(self, event):
        """Handle mouse press."""
        if self.is_allowed:
            self.clicked.emit(self.stage_code)
        super().mousePressEvent(event)
