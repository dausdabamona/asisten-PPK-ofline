"""
PPK DOCUMENT FACTORY - Base List Page
======================================
Base class for transaksi list pages (UP, TUP, LS).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QHeaderView,
    QAbstractItemView, QMenu, QHBoxLayout as HBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from typing import Dict, Any, List, Optional
from abc import abstractmethod


def format_rupiah(value: float) -> str:
    """Format angka ke format Rupiah."""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


class BaseListPage(QWidget):
    """
    Base class for list pages.

    Signals:
        item_selected(int): Emitted when a row is selected
        item_double_clicked(int): Emitted when a row is double-clicked
        edit_clicked(int): Emitted when edit button is clicked
        new_clicked(): Emitted when new button is clicked
        refresh_requested(): Emitted when refresh is needed
    """

    item_selected = Signal(int)
    item_double_clicked = Signal(int)
    edit_clicked = Signal(int)
    new_clicked = Signal()
    refresh_requested = Signal()

    # Override in subclasses
    MEKANISME = "UP"
    TITLE = "Daftar Transaksi"
    COLOR = "#3498db"

    STATUS_COLORS = {
        "draft": "#bdc3c7",
        "aktif": "#3498db",
        "selesai": "#27ae60",
        "batal": "#e74c3c",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: List[Dict[str, Any]] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup list page UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Filter bar
        filter_bar = self._create_filter_bar()
        main_layout.addWidget(filter_bar)

        # Table
        self.table = self._create_table()
        main_layout.addWidget(self.table, 1)

        # Footer with pagination
        footer = self._create_footer()
        main_layout.addWidget(footer)

    def _create_header(self) -> QWidget:
        """Create page header."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title with icon
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)

        icon = QLabel(self._get_icon())
        icon.setStyleSheet(f"""
            font-size: 24px;
            color: {self.COLOR};
        """)
        title_layout.addWidget(icon)

        title = QLabel(self.TITLE)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
        """)
        title_layout.addWidget(title)

        layout.addLayout(title_layout)
        layout.addStretch()

        # New button
        new_btn = QPushButton(f"+ {self.MEKANISME} Baru")
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: 500;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(self.COLOR)};
            }}
        """)
        new_btn.clicked.connect(self.new_clicked.emit)
        layout.addWidget(new_btn)

        return header

    def _create_filter_bar(self) -> QWidget:
        """Create filter bar."""
        bar = QFrame()
        bar.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari kegiatan atau kode...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                border: 1px solid #dcdfe6;
                border-radius: 5px;
                padding: 8px 12px;
                min-width: 250px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self.search_input)

        # Status filter
        status_label = QLabel("Status:")
        status_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(status_label)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Semua", "Draft", "Aktif", "Selesai"])
        self.status_combo.setStyleSheet("""
            QComboBox {
                background-color: #f8f9fa;
                border: 1px solid #dcdfe6;
                border-radius: 5px;
                padding: 8px 12px;
                min-width: 100px;
            }
        """)
        self.status_combo.currentTextChanged.connect(self._on_filter_changed)
        layout.addWidget(self.status_combo)

        # Jenis belanja filter
        jenis_label = QLabel("Jenis:")
        jenis_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(jenis_label)

        self.jenis_combo = QComboBox()
        self.jenis_combo.addItems([
            "Semua", "Honorarium", "Jamuan/Konsumsi",
            "Perjalanan Dinas", "PJLP", "ATK", "Lainnya"
        ])
        self.jenis_combo.setStyleSheet("""
            QComboBox {
                background-color: #f8f9fa;
                border: 1px solid #dcdfe6;
                border-radius: 5px;
                padding: 8px 12px;
                min-width: 120px;
            }
        """)
        self.jenis_combo.currentTextChanged.connect(self._on_filter_changed)
        layout.addWidget(self.jenis_combo)

        layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(refresh_btn)

        return bar

    def _create_table(self) -> QTableWidget:
        """Create data table."""
        table = QTableWidget()

        # Columns
        columns = self._get_columns()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        # Styling
        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                gridline-color: #f5f6fa;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f5f6fa;
            }
            QTableWidget::item:selected {
                background-color: #ebf5fb;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #2c3e50;
                font-weight: bold;
                padding: 12px 10px;
                border: none;
                border-bottom: 2px solid #ecf0f1;
            }
        """)

        # Behavior
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)

        # Column sizing
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # No
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Kode
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Nama
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Jenis
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Nilai
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Fase
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # Status
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # Aksi

        table.setColumnWidth(0, 50)
        table.setColumnWidth(1, 120)
        table.setColumnWidth(3, 120)
        table.setColumnWidth(4, 130)
        table.setColumnWidth(5, 80)
        table.setColumnWidth(6, 100)
        table.setColumnWidth(7, 80)

        # Signals
        table.itemSelectionChanged.connect(self._on_selection_changed)
        table.itemDoubleClicked.connect(self._on_double_click)

        # Context menu
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._show_context_menu)

        return table

    def _create_footer(self) -> QWidget:
        """Create footer with count and pagination."""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 10, 0, 0)

        self.count_label = QLabel("0 transaksi")
        self.count_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.count_label)

        layout.addStretch()

        # Pagination (simplified)
        self.page_label = QLabel("Halaman 1")
        self.page_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.page_label)

        return footer

    def _get_columns(self) -> List[str]:
        """Get column headers. Override if needed."""
        return ["No", "Kode", "Nama Kegiatan", "Jenis", "Nilai", "Fase", "Status", "Aksi"]

    def _get_icon(self) -> str:
        """Get page icon. Override in subclass."""
        return "W"

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color."""
        darken_map = {
            "#27ae60": "#1e8449",
            "#f39c12": "#d68910",
            "#3498db": "#2980b9",
        }
        return darken_map.get(hex_color, hex_color)

    def _on_filter_changed(self):
        """Handle filter change."""
        self._apply_filters()

    def _apply_filters(self):
        """Apply current filters to data."""
        search = self.search_input.text().lower()
        status = self.status_combo.currentText().lower()
        jenis = self.jenis_combo.currentText()

        for row in range(self.table.rowCount()):
            show = True

            # Search filter
            if search:
                nama = self.table.item(row, 2)
                kode = self.table.item(row, 1)
                if nama and kode:
                    if search not in nama.text().lower() and search not in kode.text().lower():
                        show = False

            # Status filter
            if status != "semua":
                status_item = self.table.item(row, 6)
                if status_item and status not in status_item.text().lower():
                    show = False

            # Jenis filter
            if jenis != "Semua":
                jenis_item = self.table.item(row, 3)
                if jenis_item and jenis.lower() not in jenis_item.text().lower():
                    show = False

            self.table.setRowHidden(row, not show)

    def _on_selection_changed(self):
        """Handle row selection."""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            if row < len(self._data):
                transaksi_id = self._data[row].get('id', 0)
                self.item_selected.emit(transaksi_id)

    def _on_double_click(self, item):
        """Handle double click on row."""
        row = item.row()
        if row < len(self._data):
            transaksi_id = self._data[row].get('id', 0)
            self.item_double_clicked.emit(transaksi_id)

    def _show_context_menu(self, pos):
        """Show context menu."""
        item = self.table.itemAt(pos)
        if not item:
            return

        row = item.row()
        if row >= len(self._data):
            return

        transaksi_id = self._data[row].get('id', 0)

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #ecf0f1;
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #ebf5fb;
                color: #3498db;
            }
        """)

        open_action = menu.addAction("Buka Detail")
        open_action.triggered.connect(lambda: self.item_double_clicked.emit(transaksi_id))

        menu.addSeparator()

        delete_action = menu.addAction("Batalkan")
        delete_action.triggered.connect(lambda: self._on_delete(transaksi_id))

        menu.exec(self.table.mapToGlobal(pos))

    def _on_delete(self, transaksi_id: int):
        """Handle delete action."""
        # Implement in subclass or emit signal
        pass

    def set_data(self, data: List[Dict[str, Any]]):
        """Set table data."""
        self._data = data

        self.table.setRowCount(len(data))

        for row, item in enumerate(data):
            self._set_row_data(row, item)

        self.count_label.setText(f"{len(data)} transaksi")

    def _set_row_data(self, row: int, item: Dict[str, Any]):
        """Set data for a single row."""
        # No
        no_item = QTableWidgetItem(str(row + 1))
        no_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, no_item)

        # Kode
        kode_item = QTableWidgetItem(item.get('kode_transaksi', '-'))
        self.table.setItem(row, 1, kode_item)

        # Nama
        nama_item = QTableWidgetItem(item.get('nama_kegiatan', '-'))
        self.table.setItem(row, 2, nama_item)

        # Jenis
        jenis_item = QTableWidgetItem(item.get('jenis_belanja', '-').title())
        self.table.setItem(row, 3, jenis_item)

        # Nilai
        nilai = item.get('estimasi_biaya', 0)
        nilai_item = QTableWidgetItem(format_rupiah(nilai))
        nilai_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 4, nilai_item)

        # Fase
        fase = item.get('fase_aktif', 1)
        fase_item = QTableWidgetItem(f"Fase {fase}")
        fase_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 5, fase_item)

        # Status
        status = item.get('status', 'draft')
        status_item = QTableWidgetItem(status.title())
        status_item.setTextAlignment(Qt.AlignCenter)

        color = self.STATUS_COLORS.get(status, "#bdc3c7")
        status_item.setForeground(QColor(color))

        self.table.setItem(row, 6, status_item)

        # Aksi (Edit button)
        transaksi_id = item.get('id', 0)
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(5, 2, 5, 2)
        action_layout.setSpacing(5)

        edit_btn = QPushButton("Edit")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 12px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        edit_btn.clicked.connect(lambda checked, tid=transaksi_id: self.edit_clicked.emit(tid))
        action_layout.addWidget(edit_btn)

        self.table.setCellWidget(row, 7, action_widget)

    def refresh(self):
        """Refresh data. Override to implement actual refresh."""
        self.refresh_requested.emit()

    def get_selected_id(self) -> Optional[int]:
        """Get currently selected transaksi ID."""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            if row < len(self._data):
                return self._data[row].get('id')
        return None
