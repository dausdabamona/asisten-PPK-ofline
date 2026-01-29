"""
PPK DOCUMENT FACTORY - Base Table Widget
========================================
Reusable table widget dengan:
- Dynamic column configuration
- Built-in filtering dan sorting
- Action buttons per row
- Empty state display
- Selection handling

Author: PPK Document Factory Team
Version: 4.0
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from functools import partial

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QLabel, QPushButton, QLineEdit,
    QFrame, QMenu, QStackedWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon, QColor

# Import EmptyState component
try:
    from app.ui.components import EmptyState
    HAS_EMPTY_STATE = True
except ImportError:
    HAS_EMPTY_STATE = False


# =============================================================================
# COLUMN DEFINITION
# =============================================================================

@dataclass
class ColumnDef:
    """
    Definisi kolom untuk table.

    Attributes:
        key: Key untuk akses data dari dictionary
        header: Header text yang ditampilkan
        width: Lebar kolom (None untuk auto)
        stretch: Apakah kolom stretch untuk fill space
        formatter: Function untuk format display value
        alignment: Text alignment
        hidden: Apakah kolom tersembunyi
        sortable: Apakah kolom bisa di-sort
        editable: Apakah kolom bisa diedit

    Example:
        columns = [
            ColumnDef('id', 'ID', width=50, alignment=Qt.AlignCenter),
            ColumnDef('nama', 'Nama Lengkap', stretch=True),
            ColumnDef('nilai', 'Nilai', formatter=format_rupiah),
            ColumnDef('tanggal', 'Tanggal', formatter=lambda d: d.strftime('%d/%m/%Y'))
        ]
    """
    key: str
    header: str
    width: Optional[int] = None
    stretch: bool = False
    formatter: Optional[Callable[[Any], str]] = None
    alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    hidden: bool = False
    sortable: bool = True
    editable: bool = False


@dataclass
class ActionDef:
    """
    Definisi action button untuk table row.

    Attributes:
        name: Unique identifier untuk action
        label: Text button (atau icon jika icon_only=True)
        icon: Emoji atau path icon
        tooltip: Tooltip text
        callback: Optional callback function(row_index, row_data)
        color: Button color
        icon_only: Tampilkan hanya icon tanpa text

    Example:
        actions = [
            ActionDef('edit', 'Edit', icon='✏️', tooltip='Edit data'),
            ActionDef('delete', 'Hapus', icon='🗑️', color='#e74c3c'),
            ActionDef('view', '', icon='👁️', icon_only=True)
        ]
    """
    name: str
    label: str = ""
    icon: str = ""
    tooltip: str = ""
    callback: Optional[Callable[[int, Dict], None]] = None
    color: str = ""
    icon_only: bool = False


# =============================================================================
# BASE TABLE WIDGET
# =============================================================================

class BaseTableWidget(QWidget):
    """
    Enhanced QTableWidget dengan fitur tambahan.

    Features:
    - Dynamic column configuration
    - Action buttons per row
    - Built-in search/filter
    - Empty state display
    - Row selection dengan data
    - Alternating row colors

    Signals:
        row_selected(int, dict): Emitted saat row dipilih (index, data)
        row_double_clicked(int, dict): Emitted saat row di-double click
        action_clicked(str, int, dict): Emitted saat action button diklik (name, index, data)
        data_changed(): Emitted saat data berubah

    Example:
        table = BaseTableWidget()
        table.set_columns([
            ColumnDef('id', 'ID', width=50),
            ColumnDef('nama', 'Nama', stretch=True),
            ColumnDef('nilai', 'Nilai', formatter=format_rupiah)
        ])
        table.add_action_column([
            ActionDef('edit', 'Edit', icon='✏️'),
            ActionDef('delete', 'Hapus', icon='🗑️', color='#e74c3c')
        ])
        table.set_data(data_list)

        table.row_selected.connect(self.on_row_selected)
        table.action_clicked.connect(self.on_action)
    """

    # Signals
    row_selected = Signal(int, dict)  # row_index, row_data
    row_double_clicked = Signal(int, dict)
    action_clicked = Signal(str, int, dict)  # action_name, row_index, row_data
    data_changed = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        show_search: bool = False,
        show_row_numbers: bool = True
    ):
        """
        Initialize table widget.

        Args:
            parent: Parent widget
            show_search: Show search box
            show_row_numbers: Show row numbers column
        """
        super().__init__(parent)

        self._columns: List[ColumnDef] = []
        self._actions: List[ActionDef] = []
        self._data: List[Dict] = []
        self._filtered_data: List[Dict] = []
        self._show_search = show_search
        self._show_row_numbers = show_row_numbers
        self._empty_message = "Tidak ada data"
        self._empty_description = ""
        self._empty_icon = "📋"
        self._empty_action_text = ""
        self._empty_action_callback: Optional[Callable] = None
        self._search_empty_message = "Tidak Ditemukan"
        self._search_empty_description = "Coba kata kunci yang berbeda"
        self._filter_func: Optional[Callable[[Dict], bool]] = None
        self._id_key = "id"  # Default key untuk identify row
        self._is_search_result = False  # Track if showing search results

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Search box (optional)
        if self._show_search:
            search_layout = QHBoxLayout()
            search_layout.setContentsMargins(0, 0, 0, 0)

            self._search_box = QLineEdit()
            self._search_box.setPlaceholderText("🔍 Cari...")
            self._search_box.textChanged.connect(self._on_search_changed)
            self._search_box.setMaximumWidth(300)
            search_layout.addWidget(self._search_box)
            search_layout.addStretch()

            layout.addLayout(search_layout)

        # Stacked widget for table/empty state
        self._stack = QStackedWidget()

        # Table
        self._table = QTableWidget()
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(True)
        self._table.setSortingEnabled(True)

        # Connect signals
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        self._table.itemDoubleClicked.connect(self._on_double_click)
        self._table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)

        # Context menu
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)

        self._stack.addWidget(self._table)

        # Empty state - use EmptyState component if available
        if HAS_EMPTY_STATE:
            self._empty_widget = EmptyState(
                icon=self._empty_icon,
                title=self._empty_message,
                description=self._empty_description
            )
            self._empty_widget.action_clicked.connect(self._on_empty_action)
        else:
            # Fallback to simple empty state
            self._empty_widget = QFrame()
            self._empty_widget.setObjectName("emptyState")
            empty_layout = QVBoxLayout(self._empty_widget)
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self._empty_icon_label = QLabel("📋")
            self._empty_icon_label.setStyleSheet("font-size: 48px;")
            self._empty_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(self._empty_icon_label)

            self._empty_label = QLabel(self._empty_message)
            self._empty_label.setStyleSheet("""
                color: #7f8c8d;
                font-size: 14px;
                font-weight: bold;
            """)
            self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(self._empty_label)

        self._stack.addWidget(self._empty_widget)

        layout.addWidget(self._stack)

        # Style
        self._apply_style()

    def _apply_style(self) -> None:
        """Apply table styling."""
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #e8f4fc;
                color: #2c3e50;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #f5f6fa;
                color: #2c3e50;
                font-weight: bold;
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid #dcdde1;
            }
            QHeaderView::section:hover {
                background-color: #e8e9ed;
            }
        """)

        self._empty_widget.setStyleSheet("""
            QFrame#emptyState {
                background-color: #f8f9fa;
                border: 2px dashed #dcdde1;
                border-radius: 8px;
                min-height: 200px;
            }
        """)

    # =========================================================================
    # COLUMN CONFIGURATION
    # =========================================================================

    def set_columns(self, columns: List[ColumnDef]) -> None:
        """
        Set column definitions.

        Args:
            columns: List of ColumnDef objects
        """
        self._columns = columns
        self._update_columns()

    def _update_columns(self) -> None:
        """Update table columns based on definitions."""
        # Calculate total columns
        total_cols = len(self._columns)
        if self._show_row_numbers:
            total_cols += 1
        if self._actions:
            total_cols += 1

        self._table.setColumnCount(total_cols)

        # Build headers
        headers = []
        col_index = 0

        # Row numbers column
        if self._show_row_numbers:
            headers.append("No")
            self._table.setColumnWidth(col_index, 40)
            col_index += 1

        # Data columns
        for col_def in self._columns:
            headers.append(col_def.header)

            if col_def.hidden:
                self._table.setColumnHidden(col_index, True)
            elif col_def.width:
                self._table.setColumnWidth(col_index, col_def.width)
            elif col_def.stretch:
                self._table.horizontalHeader().setSectionResizeMode(
                    col_index, QHeaderView.ResizeMode.Stretch
                )

            col_index += 1

        # Actions column
        if self._actions:
            headers.append("Aksi")
            # Auto width for actions
            action_width = sum(80 if not a.icon_only else 40 for a in self._actions)
            self._table.setColumnWidth(col_index, min(action_width, 250))

        self._table.setHorizontalHeaderLabels(headers)

    def add_action_column(self, actions: List[ActionDef]) -> None:
        """
        Add action buttons column.

        Args:
            actions: List of ActionDef objects
        """
        self._actions = actions
        self._update_columns()

    # =========================================================================
    # DATA MANAGEMENT
    # =========================================================================

    def set_data(self, data: List[Dict]) -> None:
        """
        Set table data.

        Args:
            data: List of dictionaries
        """
        self._data = data
        self._apply_filter()

    def _apply_filter(self) -> None:
        """Apply current filter to data."""
        if self._filter_func:
            self._filtered_data = [d for d in self._data if self._filter_func(d)]
        else:
            self._filtered_data = list(self._data)

        self._populate_table()

    def _populate_table(self) -> None:
        """Populate table with filtered data."""
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(self._filtered_data))

        for row_idx, row_data in enumerate(self._filtered_data):
            col_idx = 0

            # Row number
            if self._show_row_numbers:
                item = QTableWidgetItem(str(row_idx + 1))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setData(Qt.ItemDataRole.UserRole, row_data)  # Store data
                self._table.setItem(row_idx, col_idx, item)
                col_idx += 1

            # Data columns
            for col_def in self._columns:
                value = row_data.get(col_def.key, "")

                # Format value
                if col_def.formatter and value is not None:
                    try:
                        display_value = col_def.formatter(value)
                    except Exception:
                        display_value = str(value) if value is not None else ""
                else:
                    display_value = str(value) if value is not None else ""

                item = QTableWidgetItem(display_value)
                item.setTextAlignment(col_def.alignment)
                item.setData(Qt.ItemDataRole.UserRole, row_data)

                if not col_def.editable:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                self._table.setItem(row_idx, col_idx, item)
                col_idx += 1

            # Action buttons
            if self._actions:
                action_widget = self._create_action_widget(row_idx, row_data)
                self._table.setCellWidget(row_idx, col_idx, action_widget)

        self._table.setSortingEnabled(True)

        # Show empty state if no data
        if len(self._filtered_data) == 0:
            self._stack.setCurrentWidget(self._empty_widget)
        else:
            self._stack.setCurrentWidget(self._table)

        self.data_changed.emit()

    def _create_action_widget(self, row_idx: int, row_data: Dict) -> QWidget:
        """Create action buttons widget for row."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        for action in self._actions:
            if action.icon_only:
                btn = QPushButton(action.icon)
                btn.setFixedSize(28, 28)
            else:
                btn_text = f"{action.icon} {action.label}".strip()
                btn = QPushButton(btn_text)
                btn.setMinimumWidth(60)

            if action.tooltip:
                btn.setToolTip(action.tooltip)

            if action.color:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {action.color};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                    }}
                    QPushButton:hover {{
                        opacity: 0.8;
                    }}
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ecf0f1;
                        color: #2c3e50;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                    }
                    QPushButton:hover {
                        background-color: #dcdde1;
                    }
                """)

            # Connect click
            btn.clicked.connect(partial(self._on_action_clicked, action.name, row_idx))

            layout.addWidget(btn)

        layout.addStretch()
        return widget

    def add_row(self, data: Dict) -> None:
        """
        Add single row to table.

        Args:
            data: Row data dictionary
        """
        self._data.append(data)
        self._apply_filter()

    def update_row(self, index: int, data: Dict) -> None:
        """
        Update row at index.

        Args:
            index: Row index
            data: New row data
        """
        if 0 <= index < len(self._filtered_data):
            # Find in original data
            old_data = self._filtered_data[index]
            try:
                original_idx = self._data.index(old_data)
                self._data[original_idx] = data
            except ValueError:
                pass

            self._apply_filter()

    def remove_row(self, index: int) -> None:
        """
        Remove row at index.

        Args:
            index: Row index to remove
        """
        if 0 <= index < len(self._filtered_data):
            row_data = self._filtered_data[index]
            try:
                self._data.remove(row_data)
            except ValueError:
                pass

            self._apply_filter()

    def get_selected_data(self) -> Optional[Dict]:
        """
        Get data of selected row.

        Returns:
            Dictionary of selected row data, or None if nothing selected
        """
        selected_rows = self._table.selectionModel().selectedRows()
        if selected_rows:
            row_idx = selected_rows[0].row()
            if 0 <= row_idx < len(self._filtered_data):
                return self._filtered_data[row_idx]
        return None

    def get_selected_index(self) -> int:
        """
        Get index of selected row.

        Returns:
            Selected row index, or -1 if nothing selected
        """
        selected_rows = self._table.selectionModel().selectedRows()
        if selected_rows:
            return selected_rows[0].row()
        return -1

    def get_all_data(self) -> List[Dict]:
        """
        Get all data (unfiltered).

        Returns:
            List of all row data dictionaries
        """
        return list(self._data)

    def get_filtered_data(self) -> List[Dict]:
        """
        Get currently displayed (filtered) data.

        Returns:
            List of filtered row data dictionaries
        """
        return list(self._filtered_data)

    def get_row_data(self, index: int) -> Optional[Dict]:
        """
        Get data at specific row index.

        Args:
            index: Row index

        Returns:
            Row data or None
        """
        if 0 <= index < len(self._filtered_data):
            return self._filtered_data[index]
        return None

    # =========================================================================
    # FILTERING & SORTING
    # =========================================================================

    def filter_data(self, filter_func: Optional[Callable[[Dict], bool]]) -> None:
        """
        Apply custom filter function.

        Args:
            filter_func: Function that takes row dict and returns True to include

        Example:
            table.filter_data(lambda row: row['status'] == 'active')
        """
        self._filter_func = filter_func
        self._apply_filter()

    def clear_filter(self) -> None:
        """Clear all filters."""
        self._filter_func = None
        if self._show_search:
            self._search_box.clear()
        self._apply_filter()

    def _on_search_changed(self, text: str) -> None:
        """Handle search text changed."""
        search_text = text.lower().strip()

        if search_text:
            self._is_search_result = True

            def search_filter(row: Dict) -> bool:
                for col in self._columns:
                    value = row.get(col.key, "")
                    if value and search_text in str(value).lower():
                        return True
                return False

            self._filter_func = search_filter
        else:
            self._is_search_result = False
            self._filter_func = None

        self._update_empty_state()
        self._apply_filter()

    def sort_by_column(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        """
        Sort table by column.

        Args:
            column: Column index
            order: Sort order
        """
        self._table.sortItems(column, order)

    def _on_header_clicked(self, logical_index: int) -> None:
        """Handle header click for sorting."""
        # Sorting is handled automatically by QTableWidget
        pass

    # =========================================================================
    # EMPTY STATE
    # =========================================================================

    def set_empty_state(
        self,
        title: str = "Tidak ada data",
        description: str = "",
        icon: str = "📋",
        action_text: Optional[str] = None,
        action_callback: Optional[Callable] = None
    ) -> None:
        """
        Configure empty state display.

        Args:
            title: Title text when no data
            description: Description text
            icon: Emoji or icon to display
            action_text: Text for action button (None to hide)
            action_callback: Callback when action button clicked

        Example:
            table.set_empty_state(
                title="Belum ada transaksi",
                description="Buat transaksi baru untuk memulai",
                icon="📄",
                action_text="Buat Transaksi",
                action_callback=self._on_add_new
            )
        """
        self._empty_message = title
        self._empty_description = description
        self._empty_icon = icon
        self._empty_action_text = action_text or ""
        self._empty_action_callback = action_callback

        self._update_empty_state()

    def set_search_empty_state(
        self,
        title: str = "Tidak Ditemukan",
        description: str = "Coba kata kunci yang berbeda"
    ) -> None:
        """
        Configure empty state for search results.

        Args:
            title: Title when search returns no results
            description: Description text
        """
        self._search_empty_message = title
        self._search_empty_description = description

    def _update_empty_state(self) -> None:
        """Update empty state widget based on current settings."""
        if self._is_search_result:
            # Search results empty state
            title = self._search_empty_message
            description = self._search_empty_description
            icon = "🔍"
            action_text = ""
        else:
            # Regular empty state
            title = self._empty_message
            description = self._empty_description
            icon = self._empty_icon
            action_text = self._empty_action_text

        if HAS_EMPTY_STATE:
            # Use EmptyState individual setters
            self._empty_widget.set_icon(icon)
            self._empty_widget.set_title(title)
            self._empty_widget.set_description(description)
            if action_text:
                self._empty_widget.set_action(action_text, self._empty_action_callback)
            else:
                self._empty_widget.hide_action()
        else:
            # Update fallback empty state
            if hasattr(self, '_empty_icon_label'):
                self._empty_icon_label.setText(icon)
            if hasattr(self, '_empty_label'):
                self._empty_label.setText(title)

    def _on_empty_action(self) -> None:
        """Handle empty state action button click."""
        if self._empty_action_callback:
            self._empty_action_callback()

    def set_empty_message(self, message: str, icon: str = "📋") -> None:
        """
        Set empty state message and icon (legacy method).

        Args:
            message: Message to display when no data
            icon: Emoji or icon to display
        """
        self.set_empty_state(title=message, icon=icon)

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def _on_selection_changed(self) -> None:
        """Handle row selection changed."""
        data = self.get_selected_data()
        index = self.get_selected_index()
        if data is not None:
            self.row_selected.emit(index, data)

    def _on_double_click(self, item: QTableWidgetItem) -> None:
        """Handle row double click."""
        row_idx = item.row()
        if 0 <= row_idx < len(self._filtered_data):
            self.row_double_clicked.emit(row_idx, self._filtered_data[row_idx])

    def _on_action_clicked(self, action_name: str, row_idx: int) -> None:
        """Handle action button click."""
        if 0 <= row_idx < len(self._filtered_data):
            row_data = self._filtered_data[row_idx]

            # Emit signal
            self.action_clicked.emit(action_name, row_idx, row_data)

            # Call callback if defined
            for action in self._actions:
                if action.name == action_name and action.callback:
                    action.callback(row_idx, row_data)

    def _show_context_menu(self, position) -> None:
        """Show context menu on right click."""
        if not self._actions:
            return

        row_idx = self._table.rowAt(position.y())
        if row_idx < 0:
            return

        row_data = self._filtered_data[row_idx] if row_idx < len(self._filtered_data) else None
        if not row_data:
            return

        menu = QMenu(self)

        for action in self._actions:
            label = f"{action.icon} {action.label}".strip() if action.label else action.icon
            menu_action = QAction(label, self)
            menu_action.triggered.connect(partial(self._on_action_clicked, action.name, row_idx))
            menu.addAction(menu_action)

        menu.exec(self._table.viewport().mapToGlobal(position))

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def clear(self) -> None:
        """Clear all data from table."""
        self._data = []
        self._filtered_data = []
        self._table.setRowCount(0)
        self._stack.setCurrentWidget(self._empty_widget)

    def refresh(self) -> None:
        """Refresh table display."""
        self._apply_filter()

    def select_row(self, index: int) -> None:
        """
        Select row by index.

        Args:
            index: Row index to select
        """
        if 0 <= index < self._table.rowCount():
            self._table.selectRow(index)

    def select_by_id(self, id_value: Any) -> None:
        """
        Select row by ID value.

        Args:
            id_value: Value of ID field to match
        """
        for idx, row_data in enumerate(self._filtered_data):
            if row_data.get(self._id_key) == id_value:
                self.select_row(idx)
                return

    def set_id_key(self, key: str) -> None:
        """
        Set the key used for identifying rows.

        Args:
            key: Dictionary key for row ID
        """
        self._id_key = key

    @property
    def row_count(self) -> int:
        """Get number of rows displayed."""
        return len(self._filtered_data)

    @property
    def total_count(self) -> int:
        """Get total number of rows (unfiltered)."""
        return len(self._data)

    def get_table_widget(self) -> QTableWidget:
        """
        Get underlying QTableWidget for advanced customization.

        Returns:
            QTableWidget instance
        """
        return self._table


# =============================================================================
# HELPER FORMATTERS
# =============================================================================

def format_rupiah(value: Any) -> str:
    """Format number as Indonesian Rupiah."""
    if value is None:
        return "Rp 0"
    try:
        return f"Rp {float(value):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return str(value)


def format_date_id(value: Any) -> str:
    """Format date as Indonesian format (dd/mm/yyyy)."""
    if value is None:
        return "-"
    try:
        if hasattr(value, 'strftime'):
            return value.strftime('%d/%m/%Y')
        return str(value)
    except Exception:
        return str(value)


def format_datetime_id(value: Any) -> str:
    """Format datetime as Indonesian format."""
    if value is None:
        return "-"
    try:
        if hasattr(value, 'strftime'):
            return value.strftime('%d/%m/%Y %H:%M')
        return str(value)
    except Exception:
        return str(value)


def format_boolean(value: Any, true_text: str = "Ya", false_text: str = "Tidak") -> str:
    """Format boolean value."""
    if value is None:
        return "-"
    return true_text if value else false_text


def format_status_badge(status_map: Dict[str, str]) -> Callable[[Any], str]:
    """
    Create status formatter with emoji badges.

    Args:
        status_map: Mapping of status values to display text with emoji

    Example:
        formatter = format_status_badge({
            'draft': '📝 Draft',
            'active': '✅ Aktif',
            'completed': '🏁 Selesai'
        })
    """
    def formatter(value: Any) -> str:
        return status_map.get(str(value), str(value))
    return formatter


def truncate_text(max_length: int, suffix: str = "...") -> Callable[[Any], str]:
    """
    Create text truncation formatter.

    Args:
        max_length: Maximum characters before truncation
        suffix: Suffix to add when truncated

    Example:
        formatter = truncate_text(50)
    """
    def formatter(value: Any) -> str:
        text = str(value) if value else ""
        if len(text) > max_length:
            return text[:max_length - len(suffix)] + suffix
        return text
    return formatter
