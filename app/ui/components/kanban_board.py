"""
PPK DOCUMENT FACTORY - Kanban Board Component
==============================================
Komponen Kanban board untuk visualisasi transaksi per fase workflow.

Features:
- KanbanCard: Card draggable untuk setiap transaksi
- KanbanColumn: Kolom per fase dengan drop target
- KanbanBoard: Container dengan filter dan horizontal scroll

Author: PPK Document Factory Team
Version: 4.0
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
    QMenu, QLineEdit, QComboBox, QApplication, QSpacerItem
)
from PySide6.QtCore import (
    Qt, Signal, QMimeData, QPoint, QSize, QPropertyAnimation,
    QEasingCurve, QTimer, Property, QByteArray
)
from PySide6.QtGui import (
    QDrag, QPixmap, QPainter, QColor, QFont, QCursor,
    QDragEnterEvent, QDragMoveEvent, QDropEvent, QMouseEvent
)


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

class Mekanisme(Enum):
    """Tipe mekanisme pembayaran."""
    UP = "UP"
    TUP = "TUP"
    LS = "LS"


class Urgency(Enum):
    """Level urgensi berdasarkan deadline."""
    NORMAL = "normal"
    WARNING = "warning"  # < 3 hari
    OVERDUE = "overdue"  # Sudah lewat


# Konfigurasi warna berdasarkan mekanisme
MEKANISME_COLORS = {
    "UP": {
        "bg": "#e8f5e9",
        "border": "#4caf50",
        "header": "#2e7d32",
        "accent": "#81c784"
    },
    "TUP": {
        "bg": "#fff3e0",
        "border": "#ff9800",
        "header": "#e65100",
        "accent": "#ffb74d"
    },
    "LS": {
        "bg": "#e3f2fd",
        "border": "#2196f3",
        "header": "#1565c0",
        "accent": "#64b5f6"
    },
    "default": {
        "bg": "#f5f5f5",
        "border": "#9e9e9e",
        "header": "#616161",
        "accent": "#bdbdbd"
    }
}

# Konfigurasi warna berdasarkan urgency
URGENCY_COLORS = {
    "normal": {"indicator": "#4caf50", "text": "#2e7d32"},
    "warning": {"indicator": "#ff9800", "text": "#e65100"},
    "overdue": {"indicator": "#f44336", "text": "#c62828"}
}

# Konfigurasi fase
FASE_CONFIG = {
    1: {"nama": "Inisiasi", "icon": "📋", "color": "#9c27b0"},
    2: {"nama": "Pencairan UM", "icon": "💰", "color": "#2196f3"},
    3: {"nama": "Pelaksanaan", "icon": "⚙️", "color": "#ff9800"},
    4: {"nama": "Pertanggungjawaban", "icon": "📝", "color": "#4caf50"},
    5: {"nama": "SPBY & Selesai", "icon": "✅", "color": "#607d8b"}
}

# MIME type untuk drag-drop
KANBAN_MIME_TYPE = "application/x-kanban-card"


# =============================================================================
# KANBAN CARD
# =============================================================================

class KanbanCard(QFrame):
    """
    Card untuk menampilkan satu transaksi dalam Kanban board.

    Features:
    - Draggable untuk move antar fase
    - Color-coded berdasarkan mekanisme dan urgency
    - Click untuk buka detail
    - Context menu: View, Edit, Move to...

    Signals:
        clicked(str): Emit transaksi_id saat card di-click
        move_requested(str, int): Emit transaksi_id dan target_fase
        context_action(str, str): Emit action dan transaksi_id
    """

    clicked = Signal(str)
    move_requested = Signal(str, int)
    context_action = Signal(str, str)

    # Card dimensions
    CARD_WIDTH = 220
    CARD_MIN_HEIGHT = 120

    def __init__(
        self,
        transaksi_id: str,
        nomor: str,
        nama: str,
        nilai: float,
        status: str,
        deadline: Optional[date] = None,
        mekanisme: str = "UP",
        fase: int = 1,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.transaksi_id = transaksi_id
        self.nomor = nomor
        self.nama = nama
        self.nilai = nilai
        self.status = status
        self.deadline = deadline
        self.mekanisme = mekanisme
        self.fase = fase

        self._drag_start_pos: Optional[QPoint] = None
        self._is_dragging = False

        self._setup_ui()
        self._apply_style()
        self._setup_shadow()

    def _setup_ui(self):
        """Setup card UI."""
        self.setFixedWidth(self.CARD_WIDTH)
        self.setMinimumHeight(self.CARD_MIN_HEIGHT)
        self.setCursor(Qt.PointingHandCursor)
        self.setAcceptDrops(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header row: Nomor + Mekanisme badge
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.nomor_label = QLabel(self.nomor)
        self.nomor_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.nomor_label.setStyleSheet("color: #37474f;")
        header_layout.addWidget(self.nomor_label)

        header_layout.addStretch()

        self.mekanisme_badge = QLabel(self.mekanisme)
        self.mekanisme_badge.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.mekanisme_badge.setAlignment(Qt.AlignCenter)
        self.mekanisme_badge.setFixedSize(32, 18)
        header_layout.addWidget(self.mekanisme_badge)

        layout.addLayout(header_layout)

        # Nama transaksi
        self.nama_label = QLabel(self.nama)
        self.nama_label.setFont(QFont("Segoe UI", 10))
        self.nama_label.setWordWrap(True)
        self.nama_label.setStyleSheet("color: #263238;")
        self.nama_label.setMaximumHeight(40)
        layout.addWidget(self.nama_label)

        # Nilai
        nilai_formatted = self._format_currency(self.nilai)
        self.nilai_label = QLabel(nilai_formatted)
        self.nilai_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.nilai_label.setStyleSheet("color: #1565c0;")
        layout.addWidget(self.nilai_label)

        # Footer row: Status + Deadline
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(6)

        self.status_label = QLabel(self.status)
        self.status_label.setFont(QFont("Segoe UI", 8))
        footer_layout.addWidget(self.status_label)

        footer_layout.addStretch()

        # Deadline indicator
        if self.deadline:
            urgency = self._calculate_urgency()
            deadline_text = self._format_deadline()
            self.deadline_label = QLabel(f"📅 {deadline_text}")
            self.deadline_label.setFont(QFont("Segoe UI", 8))
            urgency_color = URGENCY_COLORS.get(urgency.value, URGENCY_COLORS["normal"])
            self.deadline_label.setStyleSheet(f"color: {urgency_color['text']};")
            footer_layout.addWidget(self.deadline_label)

        layout.addLayout(footer_layout)

        # Urgency indicator bar
        self.urgency_bar = QFrame()
        self.urgency_bar.setFixedHeight(3)
        layout.addWidget(self.urgency_bar)

    def _setup_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def _apply_style(self):
        """Apply styling based on mekanisme and urgency."""
        colors = MEKANISME_COLORS.get(self.mekanisme, MEKANISME_COLORS["default"])
        urgency = self._calculate_urgency()
        urgency_color = URGENCY_COLORS.get(urgency.value, URGENCY_COLORS["normal"])

        # Card style
        self.setStyleSheet(f"""
            KanbanCard {{
                background-color: {colors['bg']};
                border: 2px solid {colors['border']};
                border-radius: 8px;
                border-left: 4px solid {colors['header']};
            }}
            KanbanCard:hover {{
                border: 2px solid {colors['header']};
                background-color: white;
            }}
        """)

        # Mekanisme badge style
        self.mekanisme_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {colors['header']};
                color: white;
                border-radius: 9px;
                padding: 2px 4px;
            }}
        """)

        # Urgency bar style
        self.urgency_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {urgency_color['indicator']};
                border-radius: 1px;
            }}
        """)

    def _calculate_urgency(self) -> Urgency:
        """Calculate urgency based on deadline."""
        if not self.deadline:
            return Urgency.NORMAL

        today = date.today()
        if isinstance(self.deadline, datetime):
            deadline_date = self.deadline.date()
        else:
            deadline_date = self.deadline

        days_remaining = (deadline_date - today).days

        if days_remaining < 0:
            return Urgency.OVERDUE
        elif days_remaining <= 3:
            return Urgency.WARNING
        return Urgency.NORMAL

    def _format_deadline(self) -> str:
        """Format deadline for display."""
        if not self.deadline:
            return ""

        if isinstance(self.deadline, datetime):
            deadline_date = self.deadline.date()
        else:
            deadline_date = self.deadline

        today = date.today()
        days_remaining = (deadline_date - today).days

        if days_remaining < 0:
            return f"{abs(days_remaining)}d overdue"
        elif days_remaining == 0:
            return "Hari ini"
        elif days_remaining == 1:
            return "Besok"
        elif days_remaining <= 7:
            return f"{days_remaining} hari"
        else:
            return deadline_date.strftime("%d/%m")

    def _format_currency(self, value: float) -> str:
        """Format nilai as Indonesian Rupiah."""
        if value >= 1_000_000_000:
            return f"Rp {value/1_000_000_000:.1f} M"
        elif value >= 1_000_000:
            return f"Rp {value/1_000_000:.1f} jt"
        elif value >= 1_000:
            return f"Rp {value/1_000:.0f} rb"
        return f"Rp {value:,.0f}"

    # -------------------------------------------------------------------------
    # Mouse Events for Drag & Drop
    # -------------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for drag initiation."""
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for drag operation."""
        if not (event.buttons() & Qt.LeftButton):
            return

        if not self._drag_start_pos:
            return

        # Check if moved enough to start drag
        if (event.pos() - self._drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return

        self._start_drag()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release - emit click if not dragging."""
        if event.button() == Qt.LeftButton and not self._is_dragging:
            if self._drag_start_pos:
                distance = (event.pos() - self._drag_start_pos).manhattanLength()
                if distance < QApplication.startDragDistance():
                    self.clicked.emit(self.transaksi_id)

        self._drag_start_pos = None
        self._is_dragging = False
        super().mouseReleaseEvent(event)

    def _start_drag(self):
        """Start drag operation with ghost card."""
        self._is_dragging = True

        # Create drag object
        drag = QDrag(self)

        # Set mime data
        mime_data = QMimeData()
        mime_data.setData(KANBAN_MIME_TYPE, self.transaksi_id.encode())
        mime_data.setText(self.transaksi_id)
        drag.setMimeData(mime_data)

        # Create ghost pixmap
        pixmap = self.grab()
        # Make it semi-transparent
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 180))
        painter.end()

        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))

        # Execute drag
        drag.exec_(Qt.MoveAction)

    # -------------------------------------------------------------------------
    # Context Menu
    # -------------------------------------------------------------------------

    def contextMenuEvent(self, event):
        """Show context menu."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
            }
        """)

        # View action
        view_action = menu.addAction("👁️ Lihat Detail")
        view_action.triggered.connect(lambda: self.context_action.emit("view", self.transaksi_id))

        # Edit action
        edit_action = menu.addAction("✏️ Edit")
        edit_action.triggered.connect(lambda: self.context_action.emit("edit", self.transaksi_id))

        menu.addSeparator()

        # Move to submenu
        move_menu = menu.addMenu("📦 Pindah ke...")
        for fase_num, fase_config in FASE_CONFIG.items():
            if fase_num != self.fase:
                action = move_menu.addAction(f"Fase {fase_num}: {fase_config['nama']}")
                action.triggered.connect(
                    lambda checked, f=fase_num: self.move_requested.emit(self.transaksi_id, f)
                )

        menu.exec_(event.globalPos())

    # -------------------------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------------------------

    def update_data(self, data: Dict[str, Any]):
        """Update card data."""
        if "nomor" in data:
            self.nomor = data["nomor"]
            self.nomor_label.setText(self.nomor)

        if "nama" in data:
            self.nama = data["nama"]
            self.nama_label.setText(self.nama)

        if "nilai" in data:
            self.nilai = data["nilai"]
            self.nilai_label.setText(self._format_currency(self.nilai))

        if "status" in data:
            self.status = data["status"]
            self.status_label.setText(self.status)

        if "deadline" in data:
            self.deadline = data["deadline"]

        if "mekanisme" in data:
            self.mekanisme = data["mekanisme"]

        self._apply_style()

    def get_data(self) -> Dict[str, Any]:
        """Get card data as dictionary."""
        return {
            "transaksi_id": self.transaksi_id,
            "nomor": self.nomor,
            "nama": self.nama,
            "nilai": self.nilai,
            "status": self.status,
            "deadline": self.deadline,
            "mekanisme": self.mekanisme,
            "fase": self.fase
        }


# =============================================================================
# KANBAN COLUMN
# =============================================================================

class KanbanColumn(QFrame):
    """
    Kolom Kanban untuk satu fase workflow.

    Features:
    - Header dengan nama fase, badge count, collapse button
    - Body scrollable dengan list of KanbanCard
    - Footer dengan total nilai
    - Drop target untuk drag-and-drop

    Signals:
        card_dropped(str, int): Emit transaksi_id dan fase_number saat card di-drop
        card_clicked(str): Forward click dari card
        card_context_action(str, str): Forward context action dari card
    """

    card_dropped = Signal(str, int)
    card_clicked = Signal(str)
    card_context_action = Signal(str, str)

    COLUMN_WIDTH = 260
    HEADER_HEIGHT = 50
    FOOTER_HEIGHT = 40

    def __init__(
        self,
        fase: int,
        nama: Optional[str] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.fase = fase
        self.nama = nama or FASE_CONFIG.get(fase, {}).get("nama", f"Fase {fase}")
        self.icon = FASE_CONFIG.get(fase, {}).get("icon", "📌")
        self.color = FASE_CONFIG.get(fase, {}).get("color", "#607d8b")

        self._cards: Dict[str, KanbanCard] = {}
        self._collapsed = False
        self._total_nilai = 0.0

        self.setAcceptDrops(True)
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        """Setup column UI."""
        self.setFixedWidth(self.COLUMN_WIDTH)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ----- Header -----
        self.header = QFrame()
        self.header.setFixedHeight(self.HEADER_HEIGHT)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(12, 8, 12, 8)

        # Icon + Nama
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)

        self.icon_label = QLabel(self.icon)
        self.icon_label.setFont(QFont("Segoe UI", 14))
        title_layout.addWidget(self.icon_label)

        self.title_label = QLabel(self.nama)
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.title_label.setStyleSheet("color: white;")
        title_layout.addWidget(self.title_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Count badge
        self.count_badge = QLabel("0")
        self.count_badge.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.count_badge.setAlignment(Qt.AlignCenter)
        self.count_badge.setFixedSize(28, 22)
        self.count_badge.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.9);
                color: #37474f;
                border-radius: 11px;
            }
        """)
        header_layout.addWidget(self.count_badge)

        # Collapse button
        self.collapse_btn = QPushButton("−")
        self.collapse_btn.setFixedSize(24, 24)
        self.collapse_btn.setCursor(Qt.PointingHandCursor)
        self.collapse_btn.clicked.connect(self._toggle_collapse)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        header_layout.addWidget(self.collapse_btn)

        layout.addWidget(self.header)

        # ----- Body (Scrollable) -----
        self.body_container = QFrame()
        body_outer_layout = QVBoxLayout(self.body_container)
        body_outer_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #bdbdbd;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(8, 8, 8, 8)
        self.cards_layout.setSpacing(8)
        self.cards_layout.setAlignment(Qt.AlignTop)

        # Empty state
        self.empty_label = QLabel("Tidak ada transaksi")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #9e9e9e; padding: 20px;")
        self.cards_layout.addWidget(self.empty_label)

        self.scroll_area.setWidget(self.cards_container)
        body_outer_layout.addWidget(self.scroll_area)

        layout.addWidget(self.body_container, 1)

        # ----- Footer -----
        self.footer = QFrame()
        self.footer.setFixedHeight(self.FOOTER_HEIGHT)
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(12, 8, 12, 8)

        self.total_label = QLabel("Total:")
        self.total_label.setFont(QFont("Segoe UI", 9))
        self.total_label.setStyleSheet("color: #616161;")
        footer_layout.addWidget(self.total_label)

        footer_layout.addStretch()

        self.nilai_label = QLabel("Rp 0")
        self.nilai_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.nilai_label.setStyleSheet("color: #1565c0;")
        footer_layout.addWidget(self.nilai_label)

        layout.addWidget(self.footer)

    def _apply_style(self):
        """Apply column styling."""
        self.setStyleSheet(f"""
            KanbanColumn {{
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }}
        """)

        self.header.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
        """)

        self.footer.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #e0e0e0;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)

    def _toggle_collapse(self):
        """Toggle column collapse state."""
        self.set_collapsed(not self._collapsed)

    def _update_stats(self):
        """Update count badge and total nilai."""
        count = len(self._cards)
        self.count_badge.setText(str(count))

        self._total_nilai = sum(card.nilai for card in self._cards.values())
        self.nilai_label.setText(self._format_currency(self._total_nilai))

        # Show/hide empty state
        self.empty_label.setVisible(count == 0)

    def _format_currency(self, value: float) -> str:
        """Format nilai as Indonesian Rupiah."""
        if value >= 1_000_000_000:
            return f"Rp {value/1_000_000_000:.1f} M"
        elif value >= 1_000_000:
            return f"Rp {value/1_000_000:.1f} jt"
        elif value >= 1_000:
            return f"Rp {value/1_000:.0f} rb"
        return f"Rp {value:,.0f}"

    # -------------------------------------------------------------------------
    # Drag & Drop Events
    # -------------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter."""
        if event.mimeData().hasFormat(KANBAN_MIME_TYPE):
            # Check if card is from different column
            transaksi_id = event.mimeData().data(KANBAN_MIME_TYPE).data().decode()
            if transaksi_id not in self._cards:
                event.acceptProposedAction()
                self._show_drop_highlight(True)
            else:
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        """Handle drag move."""
        if event.mimeData().hasFormat(KANBAN_MIME_TYPE):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Handle drag leave."""
        self._show_drop_highlight(False)

    def dropEvent(self, event: QDropEvent):
        """Handle drop."""
        self._show_drop_highlight(False)

        if event.mimeData().hasFormat(KANBAN_MIME_TYPE):
            transaksi_id = event.mimeData().data(KANBAN_MIME_TYPE).data().decode()
            event.acceptProposedAction()
            self.card_dropped.emit(transaksi_id, self.fase)
        else:
            event.ignore()

    def _show_drop_highlight(self, show: bool):
        """Show/hide drop target highlight."""
        if show:
            self.setStyleSheet(f"""
                KanbanColumn {{
                    background-color: #e3f2fd;
                    border: 2px dashed #2196f3;
                    border-radius: 8px;
                }}
            """)
        else:
            self._apply_style()

    # -------------------------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------------------------

    def add_card(self, card: KanbanCard):
        """Add a card to the column."""
        if card.transaksi_id in self._cards:
            return

        card.fase = self.fase
        card.clicked.connect(self.card_clicked.emit)
        card.context_action.connect(self.card_context_action.emit)
        card.move_requested.connect(lambda tid, f: self.card_dropped.emit(tid, f))

        self._cards[card.transaksi_id] = card
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)  # Before empty label

        self._update_stats()

    def remove_card(self, transaksi_id: str) -> Optional[KanbanCard]:
        """Remove a card from the column."""
        if transaksi_id not in self._cards:
            return None

        card = self._cards.pop(transaksi_id)
        self.cards_layout.removeWidget(card)
        card.setParent(None)

        self._update_stats()
        return card

    def get_cards(self) -> List[KanbanCard]:
        """Get all cards in the column."""
        return list(self._cards.values())

    def get_card(self, transaksi_id: str) -> Optional[KanbanCard]:
        """Get a specific card by ID."""
        return self._cards.get(transaksi_id)

    def set_collapsed(self, collapsed: bool):
        """Set column collapse state."""
        self._collapsed = collapsed
        self.body_container.setVisible(not collapsed)
        self.footer.setVisible(not collapsed)
        self.collapse_btn.setText("+" if collapsed else "−")

        if collapsed:
            self.setFixedWidth(60)
            self.title_label.hide()
        else:
            self.setFixedWidth(self.COLUMN_WIDTH)
            self.title_label.show()

    def is_collapsed(self) -> bool:
        """Check if column is collapsed."""
        return self._collapsed

    def clear(self):
        """Remove all cards from the column."""
        for transaksi_id in list(self._cards.keys()):
            self.remove_card(transaksi_id)

    def get_total_nilai(self) -> float:
        """Get total nilai of all cards."""
        return self._total_nilai


# =============================================================================
# KANBAN BOARD
# =============================================================================

class KanbanBoard(QWidget):
    """
    Main Kanban board container untuk visualisasi transaksi per fase.

    Features:
    - Horizontal scroll untuk semua columns
    - Filter controls (mekanisme, periode, search)
    - Drag-and-drop antar fase

    Signals:
        transaksi_selected(str): Emit transaksi_id saat card di-click
        transaksi_moved(str, int, int): Emit id, from_fase, to_fase
        fase_clicked(int): Emit fase number saat header di-click
    """

    transaksi_selected = Signal(str)
    transaksi_moved = Signal(str, int, int)
    fase_clicked = Signal(int)

    def __init__(
        self,
        mekanisme: Optional[str] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.default_mekanisme = mekanisme
        self._columns: Dict[int, KanbanColumn] = {}
        self._all_transaksi: List[Dict[str, Any]] = []
        self._filtered_transaksi: List[Dict[str, Any]] = []

        self._current_filter_mekanisme = mekanisme or "Semua"
        self._current_filter_search = ""
        self._current_filter_periode = "Bulan Ini"

        self._setup_ui()
        self._setup_columns()

    def _setup_ui(self):
        """Setup board UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # ----- Filter Bar -----
        filter_bar = QFrame()
        filter_bar.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        filter_layout = QHBoxLayout(filter_bar)
        filter_layout.setContentsMargins(12, 8, 12, 8)
        filter_layout.setSpacing(12)

        # Mekanisme filter
        mekanisme_label = QLabel("Mekanisme:")
        mekanisme_label.setFont(QFont("Segoe UI", 9))
        filter_layout.addWidget(mekanisme_label)

        self.mekanisme_combo = QComboBox()
        self.mekanisme_combo.addItems(["Semua", "UP", "TUP", "LS"])
        if self.default_mekanisme:
            self.mekanisme_combo.setCurrentText(self.default_mekanisme)
        self.mekanisme_combo.setFixedWidth(100)
        self.mekanisme_combo.currentTextChanged.connect(self._on_filter_changed)
        self.mekanisme_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #2196f3;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
        """)
        filter_layout.addWidget(self.mekanisme_combo)

        # Periode filter
        periode_label = QLabel("Periode:")
        periode_label.setFont(QFont("Segoe UI", 9))
        filter_layout.addWidget(periode_label)

        self.periode_combo = QComboBox()
        self.periode_combo.addItems(["Semua", "Hari Ini", "Minggu Ini", "Bulan Ini", "Tahun Ini"])
        self.periode_combo.setCurrentText("Bulan Ini")
        self.periode_combo.setFixedWidth(120)
        self.periode_combo.currentTextChanged.connect(self._on_filter_changed)
        self.periode_combo.setStyleSheet(self.mekanisme_combo.styleSheet())
        filter_layout.addWidget(self.periode_combo)

        filter_layout.addSpacing(20)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari nomor, nama...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2196f3;
            }
        """)
        filter_layout.addWidget(self.search_input)

        filter_layout.addStretch()

        # Refresh button
        self.refresh_btn = QPushButton("↻ Refresh")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
        """)
        filter_layout.addWidget(self.refresh_btn)

        layout.addWidget(filter_bar)

        # ----- Columns Container (Horizontal Scroll) -----
        self.columns_scroll = QScrollArea()
        self.columns_scroll.setWidgetResizable(True)
        self.columns_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.columns_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.columns_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:horizontal {
                height: 8px;
                background: #f5f5f5;
            }
            QScrollBar::handle:horizontal {
                background: #bdbdbd;
                border-radius: 4px;
                min-width: 40px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0;
            }
        """)

        self.columns_container = QWidget()
        self.columns_layout = QHBoxLayout(self.columns_container)
        self.columns_layout.setContentsMargins(0, 0, 0, 0)
        self.columns_layout.setSpacing(12)
        self.columns_layout.setAlignment(Qt.AlignLeft)

        self.columns_scroll.setWidget(self.columns_container)
        layout.addWidget(self.columns_scroll, 1)

    def _setup_columns(self):
        """Create columns for each fase."""
        for fase_num in range(1, 6):
            column = KanbanColumn(fase_num)
            column.card_dropped.connect(self._on_card_dropped)
            column.card_clicked.connect(self.transaksi_selected.emit)
            column.card_context_action.connect(self._on_card_context_action)

            self._columns[fase_num] = column
            self.columns_layout.addWidget(column)

        # Add stretch at the end
        self.columns_layout.addStretch()

    def _on_filter_changed(self):
        """Handle filter change."""
        self._current_filter_mekanisme = self.mekanisme_combo.currentText()
        self._current_filter_periode = self.periode_combo.currentText()
        self._apply_filters()

    def _on_search_changed(self, text: str):
        """Handle search text change."""
        self._current_filter_search = text.strip().lower()
        self._apply_filters()

    def _apply_filters(self):
        """Apply all filters to transaksi data."""
        self._filtered_transaksi = []

        for transaksi in self._all_transaksi:
            # Filter by mekanisme
            if self._current_filter_mekanisme != "Semua":
                if transaksi.get("mekanisme") != self._current_filter_mekanisme:
                    continue

            # Filter by search
            if self._current_filter_search:
                nomor = str(transaksi.get("nomor", "")).lower()
                nama = str(transaksi.get("nama", "")).lower()
                if (self._current_filter_search not in nomor and
                    self._current_filter_search not in nama):
                    continue

            # Filter by periode (simplified - real implementation should check dates)
            # For now, we'll include all transaksi when filtering by periode

            self._filtered_transaksi.append(transaksi)

        self._populate_columns()

    def _populate_columns(self):
        """Populate columns with filtered transaksi."""
        # Clear all columns
        for column in self._columns.values():
            column.clear()

        # Add cards to appropriate columns
        for transaksi in self._filtered_transaksi:
            fase = transaksi.get("fase", 1)
            if fase not in self._columns:
                continue

            card = KanbanCard(
                transaksi_id=str(transaksi.get("id", "")),
                nomor=transaksi.get("nomor", ""),
                nama=transaksi.get("nama", ""),
                nilai=transaksi.get("nilai", 0),
                status=transaksi.get("status", ""),
                deadline=transaksi.get("deadline"),
                mekanisme=transaksi.get("mekanisme", "UP"),
                fase=fase
            )

            self._columns[fase].add_card(card)

    def _on_card_dropped(self, transaksi_id: str, target_fase: int):
        """Handle card dropped on a column."""
        # Find source fase
        source_fase = None
        for fase, column in self._columns.items():
            if column.get_card(transaksi_id):
                source_fase = fase
                break

        if source_fase is None or source_fase == target_fase:
            return

        # Move the card
        self.move_transaksi(transaksi_id, source_fase, target_fase)

    def _on_card_context_action(self, action: str, transaksi_id: str):
        """Handle context menu action from card."""
        if action == "view":
            self.transaksi_selected.emit(transaksi_id)
        # Edit and other actions can be handled by parent widget

    # -------------------------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------------------------

    def set_data(self, transaksi_list: List[Dict[str, Any]]):
        """Set transaksi data to display."""
        self._all_transaksi = transaksi_list
        self._apply_filters()

    def refresh(self):
        """Refresh the board display."""
        self._apply_filters()

    def get_transaksi_by_fase(self, fase: int) -> List[Dict[str, Any]]:
        """Get list of transaksi in a specific fase."""
        if fase not in self._columns:
            return []
        return [card.get_data() for card in self._columns[fase].get_cards()]

    def move_transaksi(self, transaksi_id: str, from_fase: int, to_fase: int):
        """Move a transaksi from one fase to another."""
        if from_fase not in self._columns or to_fase not in self._columns:
            return

        source_column = self._columns[from_fase]
        target_column = self._columns[to_fase]

        # Remove from source
        card = source_column.remove_card(transaksi_id)
        if not card:
            return

        # Update fase in data
        card.fase = to_fase

        # Add to target
        target_column.add_card(card)

        # Update internal data
        for transaksi in self._all_transaksi:
            if str(transaksi.get("id", "")) == transaksi_id:
                transaksi["fase"] = to_fase
                break

        # Emit signal
        self.transaksi_moved.emit(transaksi_id, from_fase, to_fase)

    def filter_by(
        self,
        mekanisme: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ):
        """Apply filters programmatically."""
        if mekanisme:
            self.mekanisme_combo.setCurrentText(mekanisme)
        if search is not None:
            self.search_input.setText(search)
        # Status filter can be added as additional combo if needed

    def get_column(self, fase: int) -> Optional[KanbanColumn]:
        """Get a specific column by fase number."""
        return self._columns.get(fase)

    def get_all_transaksi(self) -> List[Dict[str, Any]]:
        """Get all transaksi data."""
        return self._all_transaksi

    def get_filtered_transaksi(self) -> List[Dict[str, Any]]:
        """Get filtered transaksi data."""
        return self._filtered_transaksi


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_kanban_board(
    mekanisme: Optional[str] = None,
    transaksi_list: Optional[List[Dict[str, Any]]] = None,
    parent: Optional[QWidget] = None
) -> KanbanBoard:
    """
    Factory function to create a KanbanBoard with optional initial data.

    Args:
        mekanisme: Default mekanisme filter (UP/TUP/LS)
        transaksi_list: Initial list of transaksi data
        parent: Parent widget

    Returns:
        Configured KanbanBoard instance
    """
    board = KanbanBoard(mekanisme=mekanisme, parent=parent)

    if transaksi_list:
        board.set_data(transaksi_list)

    return board
