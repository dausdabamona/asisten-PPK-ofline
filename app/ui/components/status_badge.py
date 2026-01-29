"""
PPK DOCUMENT FACTORY - Status Badge Components
===============================================
Badge components untuk menampilkan status dengan warna:
- StatusBadge: Generic status badge
- MekanismeBadge: Badge untuk UP/TUP/LS
- FaseBadge: Badge untuk fase dengan icon

Author: PPK Document Factory Team
Version: 4.0
"""

from enum import Enum
from typing import Optional, Dict

from PySide6.QtWidgets import (
    QLabel, QWidget, QHBoxLayout, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt


# =============================================================================
# STATUS TYPES
# =============================================================================

class StatusType(Enum):
    """Predefined status types with colors."""
    DRAFT = "draft"
    AKTIF = "aktif"
    ACTIVE = "active"
    PROSES = "proses"
    PENDING = "pending"
    SELESAI = "selesai"
    COMPLETED = "completed"
    BATAL = "batal"
    CANCELLED = "cancelled"
    ERROR = "error"
    # Additional common statuses
    SUCCESS = "success"
    WARNING = "warning"
    INFO = "info"


# Status configuration: bg_color, text_color
STATUS_CONFIG: Dict[str, tuple] = {
    # Draft/inactive states
    'draft': ('#95a5a6', '#ffffff'),
    'inactive': ('#95a5a6', '#ffffff'),
    'disabled': ('#bdc3c7', '#7f8c8d'),

    # Active/in-progress states
    'aktif': ('#3498db', '#ffffff'),
    'active': ('#3498db', '#ffffff'),
    'proses': ('#f39c12', '#ffffff'),
    'pending': ('#f39c12', '#ffffff'),
    'waiting': ('#e67e22', '#ffffff'),

    # Success/completed states
    'selesai': ('#27ae60', '#ffffff'),
    'completed': ('#27ae60', '#ffffff'),
    'success': ('#27ae60', '#ffffff'),
    'approved': ('#27ae60', '#ffffff'),

    # Error/cancelled states
    'batal': ('#e74c3c', '#ffffff'),
    'cancelled': ('#e74c3c', '#ffffff'),
    'error': ('#c0392b', '#ffffff'),
    'rejected': ('#e74c3c', '#ffffff'),

    # Info/warning states
    'info': ('#3498db', '#ffffff'),
    'warning': ('#f39c12', '#ffffff'),

    # Default
    'default': ('#7f8c8d', '#ffffff'),
}

# Size configurations
SIZE_CONFIG = {
    'small': {
        'font_size': 11,
        'padding_h': 6,
        'padding_v': 2,
        'border_radius': 8,
    },
    'medium': {
        'font_size': 12,
        'padding_h': 10,
        'padding_v': 4,
        'border_radius': 10,
    },
    'large': {
        'font_size': 14,
        'padding_h': 14,
        'padding_v': 6,
        'border_radius': 12,
    },
}


# =============================================================================
# STATUS BADGE
# =============================================================================

class StatusBadge(QLabel):
    """
    Generic status badge with preset colors.

    Features:
    - Preset status types with colors
    - Multiple sizes
    - Pill/rounded shape
    - Custom color support

    Usage:
        badge = StatusBadge("Selesai", "completed")
        badge = StatusBadge("Custom", size="large")
        badge.set_custom_color("#9b59b6", "#ffffff")
    """

    def __init__(
        self,
        text: str,
        status_type: str = "default",
        size: str = "medium",
        parent: Optional[QWidget] = None
    ):
        """
        Initialize status badge.

        Args:
            text: Badge text
            status_type: Status type (draft, aktif, selesai, etc.)
            size: Badge size (small, medium, large)
            parent: Parent widget
        """
        super().__init__(parent)

        self._text = text
        self._status_type = status_type.lower()
        self._size = size
        self._custom_bg = None
        self._custom_text = None

        self._apply_style()

    def _apply_style(self) -> None:
        """Apply badge styling."""
        self.setText(self._text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Get size config
        size_cfg = SIZE_CONFIG.get(self._size, SIZE_CONFIG['medium'])

        # Get colors
        if self._custom_bg and self._custom_text:
            bg_color = self._custom_bg
            text_color = self._custom_text
        else:
            bg_color, text_color = STATUS_CONFIG.get(
                self._status_type,
                STATUS_CONFIG['default']
            )

        # Apply style
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                font-size: {size_cfg['font_size']}px;
                font-weight: 500;
                padding: {size_cfg['padding_v']}px {size_cfg['padding_h']}px;
                border-radius: {size_cfg['border_radius']}px;
            }}
        """)

    def set_status(self, text: str, status_type: str) -> None:
        """
        Set status text and type.

        Args:
            text: Badge text
            status_type: Status type
        """
        self._text = text
        self._status_type = status_type.lower()
        self._custom_bg = None
        self._custom_text = None
        self._apply_style()

    def set_custom_color(self, bg_color: str, text_color: str) -> None:
        """
        Set custom colors.

        Args:
            bg_color: Background color (hex)
            text_color: Text color (hex)
        """
        self._custom_bg = bg_color
        self._custom_text = text_color
        self._apply_style()

    def set_size(self, size: str) -> None:
        """
        Set badge size.

        Args:
            size: Size (small, medium, large)
        """
        self._size = size
        self._apply_style()


# =============================================================================
# MEKANISME BADGE
# =============================================================================

# Mekanisme colors
MEKANISME_CONFIG = {
    'UP': ('#27ae60', '#ffffff'),    # Green
    'TUP': ('#f39c12', '#ffffff'),   # Orange
    'LS': ('#3498db', '#ffffff'),    # Blue
}


class MekanismeBadge(StatusBadge):
    """
    Badge for mekanisme pembayaran (UP/TUP/LS).

    Features:
    - Pre-configured colors for UP, TUP, LS
    - Consistent styling

    Usage:
        badge = MekanismeBadge("UP")
        badge = MekanismeBadge("TUP", size="small")
    """

    def __init__(
        self,
        mekanisme: str,
        size: str = "medium",
        parent: Optional[QWidget] = None
    ):
        """
        Initialize mekanisme badge.

        Args:
            mekanisme: Mekanisme type (UP, TUP, LS)
            size: Badge size
            parent: Parent widget
        """
        super().__init__(mekanisme.upper(), "default", size, parent)

        self._mekanisme = mekanisme.upper()
        self._apply_mekanisme_style()

    def _apply_mekanisme_style(self) -> None:
        """Apply mekanisme-specific styling."""
        bg_color, text_color = MEKANISME_CONFIG.get(
            self._mekanisme,
            ('#7f8c8d', '#ffffff')
        )
        self.set_custom_color(bg_color, text_color)

    def set_mekanisme(self, mekanisme: str) -> None:
        """
        Set mekanisme type.

        Args:
            mekanisme: Mekanisme type (UP, TUP, LS)
        """
        self._mekanisme = mekanisme.upper()
        self._text = self._mekanisme
        self._apply_mekanisme_style()


# =============================================================================
# FASE BADGE
# =============================================================================

class FaseStatus(Enum):
    """Fase status types."""
    COMPLETED = "completed"
    ACTIVE = "active"
    PENDING = "pending"
    LOCKED = "locked"


# Fase status configuration
FASE_CONFIG = {
    FaseStatus.COMPLETED: {
        'icon': '\u2713',  # Checkmark
        'bg_color': '#27ae60',
        'text_color': '#ffffff',
        'icon_color': '#ffffff',
    },
    FaseStatus.ACTIVE: {
        'icon': '\u25B6',  # Play arrow
        'bg_color': '#3498db',
        'text_color': '#ffffff',
        'icon_color': '#ffffff',
    },
    FaseStatus.PENDING: {
        'icon': '\u25CB',  # Empty circle
        'bg_color': '#ecf0f1',
        'text_color': '#7f8c8d',
        'icon_color': '#7f8c8d',
    },
    FaseStatus.LOCKED: {
        'icon': '\U0001F512',  # Lock
        'bg_color': '#bdc3c7',
        'text_color': '#95a5a6',
        'icon_color': '#95a5a6',
    },
}


class FaseBadge(QFrame):
    """
    Badge for fase/tahapan with icon and text.

    Features:
    - Fase number
    - Fase name
    - Status icon (completed, active, pending, locked)
    - Consistent styling

    Usage:
        badge = FaseBadge(3, "Pelaksanaan", FaseStatus.ACTIVE)
        badge = FaseBadge(1, "Persiapan", FaseStatus.COMPLETED)
    """

    def __init__(
        self,
        fase_number: int,
        fase_name: str,
        status: FaseStatus = FaseStatus.PENDING,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize fase badge.

        Args:
            fase_number: Fase number
            fase_name: Fase name
            status: Fase status
            parent: Parent widget
        """
        super().__init__(parent)

        self._fase_number = fase_number
        self._fase_name = fase_name
        self._status = status

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup fase badge UI."""
        config = FASE_CONFIG[self._status]

        self.setObjectName("faseBadge")
        self.setStyleSheet(f"""
            QFrame#faseBadge {{
                background-color: {config['bg_color']};
                border-radius: 8px;
                padding: 0px;
            }}
        """)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 12, 6)
        layout.setSpacing(8)

        # Status icon
        icon_label = QLabel(config['icon'])
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {config['icon_color']};
                font-size: 14px;
            }}
        """)
        icon_label.setFixedWidth(20)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Fase number
        number_label = QLabel(f"Fase {self._fase_number}")
        number_label.setStyleSheet(f"""
            QLabel {{
                color: {config['text_color']};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(number_label)

        # Separator
        sep_label = QLabel("-")
        sep_label.setStyleSheet(f"""
            QLabel {{
                color: {config['text_color']};
                font-size: 12px;
            }}
        """)
        layout.addWidget(sep_label)

        # Fase name
        name_label = QLabel(self._fase_name)
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {config['text_color']};
                font-size: 12px;
            }}
        """)
        layout.addWidget(name_label)

    def set_status(self, status: FaseStatus) -> None:
        """
        Set fase status.

        Args:
            status: New status
        """
        self._status = status
        # Rebuild UI
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._setup_ui()


# =============================================================================
# PRIORITY BADGE
# =============================================================================

PRIORITY_CONFIG = {
    'low': ('#95a5a6', '#ffffff', 'Rendah'),
    'medium': ('#f39c12', '#ffffff', 'Sedang'),
    'high': ('#e74c3c', '#ffffff', 'Tinggi'),
    'urgent': ('#9b59b6', '#ffffff', 'Urgent'),
}


class PriorityBadge(StatusBadge):
    """
    Badge for priority levels.

    Usage:
        badge = PriorityBadge("high")
        badge = PriorityBadge("urgent", size="small")
    """

    def __init__(
        self,
        priority: str,
        size: str = "medium",
        parent: Optional[QWidget] = None
    ):
        """
        Initialize priority badge.

        Args:
            priority: Priority level (low, medium, high, urgent)
            size: Badge size
            parent: Parent widget
        """
        priority_lower = priority.lower()
        config = PRIORITY_CONFIG.get(priority_lower, PRIORITY_CONFIG['medium'])

        super().__init__(config[2], "default", size, parent)

        self._priority = priority_lower
        self.set_custom_color(config[0], config[1])

    def set_priority(self, priority: str) -> None:
        """
        Set priority level.

        Args:
            priority: Priority level
        """
        self._priority = priority.lower()
        config = PRIORITY_CONFIG.get(self._priority, PRIORITY_CONFIG['medium'])
        self._text = config[2]
        self.set_custom_color(config[0], config[1])


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_status_badge(
    text: str,
    status: str,
    size: str = "medium"
) -> StatusBadge:
    """Create a status badge."""
    return StatusBadge(text, status, size)


def create_mekanisme_badge(mekanisme: str) -> MekanismeBadge:
    """Create a mekanisme badge."""
    return MekanismeBadge(mekanisme)


def create_fase_badge(
    number: int,
    name: str,
    status: str = "pending"
) -> FaseBadge:
    """Create a fase badge."""
    status_map = {
        'completed': FaseStatus.COMPLETED,
        'active': FaseStatus.ACTIVE,
        'pending': FaseStatus.PENDING,
        'locked': FaseStatus.LOCKED,
    }
    return FaseBadge(number, name, status_map.get(status, FaseStatus.PENDING))
