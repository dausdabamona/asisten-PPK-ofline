"""
PPK DOCUMENT FACTORY - Recent Activity Widget
==============================================
Widget untuk menampilkan daftar transaksi/aktivitas terbaru di dashboard.

Menampilkan:
- Badge mekanisme (UP/TUP/LS) dengan warna berbeda
- Nama/deskripsi transaksi
- Nilai dalam format Rupiah
- Status dengan indicator warna
- Tanggal transaksi

Author: PPK Document Factory Team
Version: 4.0
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QPushButton, QGraphicsDropShadowEffect,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from typing import List, Dict, Any, Optional
from datetime import datetime


def format_rupiah(value: float) -> str:
    """Format angka ke format Rupiah."""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


def format_tanggal(tanggal: Any) -> str:
    """Format tanggal ke format Indonesia."""
    if tanggal is None:
        return "-"

    if isinstance(tanggal, str):
        try:
            tanggal = datetime.strptime(tanggal, "%Y-%m-%d")
        except ValueError:
            try:
                tanggal = datetime.strptime(tanggal, "%d/%m/%Y")
            except ValueError:
                return tanggal

    if isinstance(tanggal, datetime):
        return tanggal.strftime("%d %b %Y")

    return str(tanggal)


class TransactionItemWidget(QFrame):
    """
    Widget untuk satu item transaksi dalam daftar.

    Menampilkan badge mekanisme, nama, nilai, status, dan tanggal.
    """

    clicked = Signal(str)  # transaction_id

    # Color schemes per mekanisme
    MEKANISME_COLORS = {
        "UP": {"bg": "#d5f5e3", "text": "#27ae60"},
        "TUP": {"bg": "#fef5e7", "text": "#f39c12"},
        "LS": {"bg": "#ebf5fb", "text": "#3498db"},
    }

    # Status colors
    STATUS_COLORS = {
        "draft": {"bg": "#f8f9fa", "text": "#6c757d", "label": "Draft"},
        "proses": {"bg": "#fff3cd", "text": "#856404", "label": "Proses"},
        "selesai": {"bg": "#d4edda", "text": "#155724", "label": "Selesai"},
        "dibatalkan": {"bg": "#f8d7da", "text": "#721c24", "label": "Dibatalkan"},
        "pending": {"bg": "#cce5ff", "text": "#004085", "label": "Pending"},
    }

    def __init__(
        self,
        transaction_id: str,
        mekanisme: str,
        nama: str,
        nilai: float,
        status: str,
        tanggal: Any,
        parent: QWidget = None
    ):
        """
        Initialize TransactionItemWidget.

        Args:
            transaction_id: Unique identifier untuk transaksi
            mekanisme: Mekanisme pencairan (UP, TUP, LS)
            nama: Nama/deskripsi transaksi
            nilai: Nilai transaksi dalam Rupiah
            status: Status transaksi (draft, proses, selesai, dibatalkan, pending)
            tanggal: Tanggal transaksi
            parent: Parent widget
        """
        super().__init__(parent)

        self._transaction_id = transaction_id
        self._mekanisme = mekanisme.upper()
        self._nama = nama
        self._nilai = nilai
        self._status = status.lower()
        self._tanggal = tanggal

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup item UI."""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            TransactionItemWidget {
                background-color: #ffffff;
                border: 1px solid #ecf0f1;
                border-radius: 6px;
                padding: 5px;
            }
            TransactionItemWidget:hover {
                background-color: #f8f9fa;
                border-color: #3498db;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        # Badge mekanisme
        mek_colors = self.MEKANISME_COLORS.get(
            self._mekanisme,
            {"bg": "#ecf0f1", "text": "#7f8c8d"}
        )

        badge = QLabel(self._mekanisme)
        badge.setFixedWidth(40)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"""
            background-color: {mek_colors['bg']};
            color: {mek_colors['text']};
            font-size: 11px;
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
        """)
        layout.addWidget(badge)

        # Info container (nama + tanggal)
        info_container = QVBoxLayout()
        info_container.setSpacing(2)

        # Nama transaksi
        nama_label = QLabel(self._nama)
        nama_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 500;
            color: #2c3e50;
        """)
        nama_label.setWordWrap(True)
        info_container.addWidget(nama_label)

        # Tanggal
        tanggal_label = QLabel(format_tanggal(self._tanggal))
        tanggal_label.setStyleSheet("font-size: 11px; color: #95a5a6;")
        info_container.addWidget(tanggal_label)

        layout.addLayout(info_container, 1)

        # Nilai dan status container
        right_container = QVBoxLayout()
        right_container.setSpacing(4)
        right_container.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Nilai
        nilai_label = QLabel(format_rupiah(self._nilai))
        nilai_label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #2c3e50;
        """)
        nilai_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_container.addWidget(nilai_label)

        # Status badge
        status_info = self.STATUS_COLORS.get(
            self._status,
            {"bg": "#ecf0f1", "text": "#7f8c8d", "label": self._status.title()}
        )

        status_label = QLabel(status_info['label'])
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet(f"""
            background-color: {status_info['bg']};
            color: {status_info['text']};
            font-size: 10px;
            font-weight: 500;
            padding: 2px 8px;
            border-radius: 3px;
        """)
        right_container.addWidget(status_label, 0, Qt.AlignmentFlag.AlignRight)

        layout.addLayout(right_container)

    def mousePressEvent(self, event) -> None:
        """Handle mouse press to emit clicked signal."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._transaction_id)
        super().mousePressEvent(event)

    def get_transaction_id(self) -> str:
        """Get transaction ID."""
        return self._transaction_id


class RecentActivityWidget(QFrame):
    """
    Widget untuk menampilkan daftar transaksi/aktivitas terbaru.

    Features:
    - Menampilkan maksimal 5-10 transaksi terbaru
    - Badge mekanisme dengan warna berbeda (UP/TUP/LS)
    - Status indicator dengan warna
    - Empty state jika tidak ada transaksi
    - Tombol 'Lihat Semua' di bawah

    Signals:
        item_clicked(str): Emitted ketika item diklik, dengan transaction_id
        view_all_clicked(): Emitted ketika tombol 'Lihat Semua' diklik

    Usage:
        widget = RecentActivityWidget()
        widget.item_clicked.connect(self.on_transaction_selected)
        widget.view_all_clicked.connect(self.show_all_transactions)

        # Set transactions
        widget.set_transactions([
            {
                "id": "UP-001",
                "mekanisme": "UP",
                "nama": "Belanja ATK Kantor",
                "nilai": 5000000,
                "status": "proses",
                "tanggal": "2024-01-15"
            },
            # ...
        ])
    """

    # Signals
    item_clicked = Signal(str)  # transaction_id
    view_all_clicked = Signal()

    # Configuration
    MAX_ITEMS = 7  # Maximum items to display

    def __init__(
        self,
        title: str = "Aktivitas Terbaru",
        max_items: int = None,
        parent: QWidget = None
    ):
        """
        Initialize RecentActivityWidget.

        Args:
            title: Section title
            max_items: Maximum items to display (default: 7)
            parent: Parent widget
        """
        super().__init__(parent)

        self._title = title
        self._max_items = max_items or self.MAX_ITEMS
        self._transactions: List[Dict[str, Any]] = []
        self._item_widgets: List[TransactionItemWidget] = []

        self._setup_ui()
        self._add_shadow()
        self._show_empty_state()

    def _setup_ui(self) -> None:
        """Setup widget UI."""
        self.setObjectName("recentActivityWidget")
        self.setStyleSheet("""
            QFrame#recentActivityWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()

        # Title
        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Count badge
        self.count_label = QLabel("0")
        self.count_label.setStyleSheet("""
            background-color: #3498db;
            color: white;
            font-size: 12px;
            font-weight: bold;
            padding: 2px 10px;
            border-radius: 10px;
        """)
        header_layout.addWidget(self.count_label)

        layout.addLayout(header_layout)

        # Items container (scrollable)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)

        self.items_container = QWidget()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(8)

        self.scroll_area.setWidget(self.items_container)
        layout.addWidget(self.scroll_area, 1)

        # Empty state (hidden by default)
        self.empty_state = QWidget()
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        empty_icon = QLabel("📋")
        empty_icon.setStyleSheet("font-size: 48px;")
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_icon)

        empty_text = QLabel("Belum ada transaksi")
        empty_text.setStyleSheet("""
            font-size: 14px;
            color: #95a5a6;
            margin-top: 10px;
        """)
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_text)

        empty_subtext = QLabel("Transaksi terbaru akan muncul di sini")
        empty_subtext.setStyleSheet("font-size: 12px; color: #bdc3c7;")
        empty_subtext.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_subtext)

        layout.addWidget(self.empty_state)

        # View all button
        self.view_all_btn = QPushButton("Lihat Semua Transaksi")
        self.view_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_all_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: 1px solid #3498db;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)
        self.view_all_btn.clicked.connect(self.view_all_clicked.emit)
        layout.addWidget(self.view_all_btn)

    def _add_shadow(self) -> None:
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

    def _show_empty_state(self) -> None:
        """Show empty state, hide items."""
        self.empty_state.show()
        self.scroll_area.hide()
        self.view_all_btn.hide()
        self.count_label.setText("0")

    def _show_items_state(self) -> None:
        """Show items, hide empty state."""
        self.empty_state.hide()
        self.scroll_area.show()
        self.view_all_btn.show()

    def _clear_items(self) -> None:
        """Clear all item widgets."""
        for widget in self._item_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self._item_widgets.clear()

    def _create_item_widget(self, data: Dict[str, Any]) -> TransactionItemWidget:
        """
        Create a TransactionItemWidget from data.

        Args:
            data: Transaction data dictionary

        Returns:
            TransactionItemWidget instance
        """
        widget = TransactionItemWidget(
            transaction_id=data.get("id", ""),
            mekanisme=data.get("mekanisme", "UP"),
            nama=data.get("nama", "Transaksi"),
            nilai=data.get("nilai", 0),
            status=data.get("status", "draft"),
            tanggal=data.get("tanggal")
        )
        widget.clicked.connect(self.item_clicked.emit)
        return widget

    def set_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """
        Set list of transactions to display.

        Args:
            transactions: List of transaction dictionaries with keys:
                - id: str - Unique identifier
                - mekanisme: str - UP, TUP, or LS
                - nama: str - Transaction name/description
                - nilai: float - Transaction value
                - status: str - draft, proses, selesai, dibatalkan, pending
                - tanggal: str/datetime - Transaction date

        Example:
            widget.set_transactions([
                {
                    "id": "UP-001",
                    "mekanisme": "UP",
                    "nama": "Belanja ATK Kantor",
                    "nilai": 5000000,
                    "status": "proses",
                    "tanggal": "2024-01-15"
                }
            ])
        """
        self._transactions = transactions[:self._max_items] if transactions else []

        # Clear existing items
        self._clear_items()

        if not self._transactions:
            self._show_empty_state()
            return

        # Create item widgets
        for data in self._transactions:
            widget = self._create_item_widget(data)
            self._item_widgets.append(widget)
            self.items_layout.addWidget(widget)

        # Add stretch to push items to top
        self.items_layout.addStretch()

        # Update count and show items
        self.count_label.setText(str(len(self._transactions)))
        self._show_items_state()

    def add_transaction(self, transaction: Dict[str, Any], prepend: bool = True) -> None:
        """
        Add a single transaction to the list.

        Args:
            transaction: Transaction data dictionary
            prepend: If True, add to beginning; if False, add to end
        """
        if prepend:
            self._transactions.insert(0, transaction)
        else:
            self._transactions.append(transaction)

        # Trim to max items
        self._transactions = self._transactions[:self._max_items]

        # Rebuild the list
        self.set_transactions(self._transactions)

    def remove_transaction(self, transaction_id: str) -> bool:
        """
        Remove a transaction by ID.

        Args:
            transaction_id: Transaction ID to remove

        Returns:
            True if removed, False if not found
        """
        for i, t in enumerate(self._transactions):
            if t.get("id") == transaction_id:
                self._transactions.pop(i)
                self.set_transactions(self._transactions)
                return True
        return False

    def update_transaction(self, transaction_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a transaction's data.

        Args:
            transaction_id: Transaction ID to update
            updates: Dictionary of fields to update

        Returns:
            True if updated, False if not found
        """
        for t in self._transactions:
            if t.get("id") == transaction_id:
                t.update(updates)
                self.set_transactions(self._transactions)
                return True
        return False

    def clear(self) -> None:
        """Clear all transactions and show empty state."""
        self._transactions.clear()
        self._clear_items()
        self._show_empty_state()

    def get_transactions(self) -> List[Dict[str, Any]]:
        """
        Get current list of transactions.

        Returns:
            List of transaction dictionaries
        """
        return self._transactions.copy()

    def set_title(self, title: str) -> None:
        """
        Set section title.

        Args:
            title: New title text
        """
        self._title = title
        self.title_label.setText(title)

    def set_max_items(self, max_items: int) -> None:
        """
        Set maximum number of items to display.

        Args:
            max_items: Maximum items count
        """
        self._max_items = max_items
        # Re-apply with new limit
        if self._transactions:
            self.set_transactions(self._transactions)

    def set_view_all_button_visible(self, visible: bool) -> None:
        """
        Show or hide the 'View All' button.

        Args:
            visible: True to show, False to hide
        """
        if visible and self._transactions:
            self.view_all_btn.show()
        else:
            self.view_all_btn.hide()

    def set_view_all_button_text(self, text: str) -> None:
        """
        Set the 'View All' button text.

        Args:
            text: New button text
        """
        self.view_all_btn.setText(text)

    def refresh(self) -> None:
        """Refresh the display with current data."""
        self.set_transactions(self._transactions)
