"""
PPK Document Factory - Lazy Loading Components
==============================================
Components for lazy/virtual loading of large data lists.

Features:
- Virtual scrolling for large datasets
- Automatic pagination
- Loading indicators
- Pagination controls

Components:
- LazyListModel: QAbstractListModel with virtual loading
- LazyTableWidget: Table with automatic load-more
- PaginationWidget: Page navigation controls

Example Usage:
-------------
```python
# LazyTableWidget
table = LazyTableWidget(columns=["ID", "Nama", "Nilai"])
table.set_total_count(1000)
table.load_more_requested.connect(self._load_more)

def _load_more(offset):
    data = db.list_transaksi(offset=offset, limit=50)
    table.append_data(data)

# PaginationWidget
pagination = PaginationWidget(total_items=1000, page_size=50)
pagination.page_changed.connect(self._on_page_change)
```
"""

from typing import Any, Dict, List, Optional, Callable
from PySide6.QtCore import (
    Qt, Signal, QAbstractListModel, QAbstractTableModel, QModelIndex,
    QTimer, QSize
)
from PySide6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QFrame, QHeaderView, QScrollBar,
    QAbstractItemView, QSizePolicy, QSpacerItem, QApplication
)
from PySide6.QtGui import QColor, QFont
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# LAZY LIST MODEL
# =============================================================================


class LazyListModel(QAbstractListModel):
    """
    List model with lazy/virtual loading support.

    Loads data on demand as user scrolls, rather than
    loading everything upfront.

    Example:
    --------
    ```python
    model = LazyListModel()
    model.set_total_count(1000)
    model.data_requested.connect(load_page)

    def load_page(offset, limit):
        data = db.query(offset=offset, limit=limit)
        model.set_page_data(offset, data)
    ```
    """

    data_requested = Signal(int, int)  # offset, limit

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._data: Dict[int, Any] = {}  # index -> item
        self._total_count = 0
        self._page_size = 50
        self._loaded_ranges: List[tuple] = []  # [(start, end), ...]
        self._display_role = Qt.ItemDataRole.DisplayRole

    @property
    def total_count(self) -> int:
        """Get total item count."""
        return self._total_count

    @property
    def page_size(self) -> int:
        """Get page size."""
        return self._page_size

    def set_total_count(self, count: int) -> None:
        """Set total number of items."""
        self.beginResetModel()
        self._total_count = count
        self.endResetModel()

    def set_page_size(self, size: int) -> None:
        """Set page size for loading."""
        self._page_size = max(10, size)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return total row count (virtual)."""
        return self._total_count

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Get data for index, requesting load if needed."""
        if not index.isValid():
            return None

        row = index.row()

        # Check if data is loaded
        if row not in self._data:
            # Request load for this page
            page_start = (row // self._page_size) * self._page_size
            if not self._is_range_loaded(page_start, page_start + self._page_size):
                self.data_requested.emit(page_start, self._page_size)
            return "Loading..."

        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[row])

        return None

    def set_page_data(self, offset: int, data: List[Any]) -> None:
        """Set data for a page."""
        for i, item in enumerate(data):
            self._data[offset + i] = item

        # Mark range as loaded
        self._loaded_ranges.append((offset, offset + len(data)))

        # Notify views
        start_index = self.index(offset, 0)
        end_index = self.index(offset + len(data) - 1, 0)
        self.dataChanged.emit(start_index, end_index)

    def _is_range_loaded(self, start: int, end: int) -> bool:
        """Check if a range is already loaded."""
        for loaded_start, loaded_end in self._loaded_ranges:
            if loaded_start <= start and loaded_end >= end:
                return True
        return False

    def clear(self) -> None:
        """Clear all data."""
        self.beginResetModel()
        self._data.clear()
        self._loaded_ranges.clear()
        self._total_count = 0
        self.endResetModel()

    def get_item(self, index: int) -> Optional[Any]:
        """Get item at index."""
        return self._data.get(index)


# =============================================================================
# LAZY TABLE MODEL
# =============================================================================


class LazyTableModel(QAbstractTableModel):
    """
    Table model with lazy loading support.

    Similar to LazyListModel but for tables with multiple columns.
    """

    data_requested = Signal(int, int)  # offset, limit

    def __init__(
        self,
        columns: List[str],
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self._columns = columns
        self._data: List[Dict] = []
        self._total_count = 0
        self._page_size = 50
        self._loaded_pages: set = set()

    def set_columns(self, columns: List[str]) -> None:
        """Set column headers."""
        self.beginResetModel()
        self._columns = columns
        self.endResetModel()

    def set_total_count(self, count: int) -> None:
        """Set total row count."""
        self.beginResetModel()
        self._total_count = count
        # Initialize data array
        self._data = [None] * count
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self._total_count

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._columns)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(self._columns):
                return self._columns[section]
        return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        # Check if page is loaded
        page = row // self._page_size
        if page not in self._loaded_pages:
            offset = page * self._page_size
            self.data_requested.emit(offset, self._page_size)
            return "..."

        # Get data
        row_data = self._data[row]
        if row_data is None:
            return ""

        if role == Qt.ItemDataRole.DisplayRole:
            col_name = self._columns[col]
            return str(row_data.get(col_name, ""))

        return None

    def set_page_data(self, offset: int, data: List[Dict]) -> None:
        """Set data for a page."""
        for i, item in enumerate(data):
            if offset + i < self._total_count:
                self._data[offset + i] = item

        page = offset // self._page_size
        self._loaded_pages.add(page)

        # Notify
        start = self.index(offset, 0)
        end = self.index(min(offset + len(data), self._total_count) - 1,
                         len(self._columns) - 1)
        self.dataChanged.emit(start, end)

    def clear(self) -> None:
        """Clear all data."""
        self.beginResetModel()
        self._data.clear()
        self._loaded_pages.clear()
        self._total_count = 0
        self.endResetModel()


# =============================================================================
# LAZY TABLE WIDGET
# =============================================================================


class LazyTableWidget(QTableWidget):
    """
    Table widget with automatic lazy loading.

    Automatically requests more data when user scrolls near bottom.

    Signals:
        load_more_requested(int): Emitted with offset when more data needed
        scroll_near_end(): Emitted when scroll reaches 80% of content

    Example:
    --------
    ```python
    table = LazyTableWidget(columns=["ID", "Nama", "Nilai", "Status"])
    table.set_page_size(50)
    table.set_total_count(1000)
    table.load_more_requested.connect(self._load_more)

    def _load_more(offset):
        data = db.query(offset=offset, limit=50)
        table.append_data(data)
    ```
    """

    load_more_requested = Signal(int)  # offset
    scroll_near_end = Signal()
    row_clicked = Signal(int, dict)  # row, data
    row_double_clicked = Signal(int, dict)

    def __init__(
        self,
        columns: Optional[List[str]] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self._columns = columns or []
        self._column_keys: List[str] = []  # Internal column keys
        self._column_headers: Dict[str, str] = {}  # key -> header
        self._total_count = 0
        self._loaded_count = 0
        self._page_size = 50
        self._is_loading = False
        self._data: List[Dict] = []
        self._load_threshold = 0.8  # 80%

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup table UI."""
        # Set columns
        if self._columns:
            self.setColumnCount(len(self._columns))
            self.setHorizontalHeaderLabels(self._columns)
            self._column_keys = self._columns.copy()

        # Styling
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Header
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Vertical header
        self.verticalHeader().setVisible(False)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)
        self.cellClicked.connect(self._on_cell_clicked)
        self.cellDoubleClicked.connect(self._on_cell_double_clicked)

    def set_columns(
        self,
        columns: List[str],
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Set table columns.

        Args:
            columns: List of column keys
            headers: Optional mapping of key -> display header
        """
        self._column_keys = columns
        self._column_headers = headers or {}

        self.setColumnCount(len(columns))

        # Set headers
        display_headers = [
            self._column_headers.get(col, col)
            for col in columns
        ]
        self.setHorizontalHeaderLabels(display_headers)

    def set_page_size(self, size: int) -> None:
        """Set number of items to load per page."""
        self._page_size = max(10, size)

    def set_total_count(self, count: int) -> None:
        """Set total number of items (enables virtual scrolling info)."""
        self._total_count = count

    def set_load_threshold(self, threshold: float) -> None:
        """Set scroll threshold for loading more (0.0 - 1.0)."""
        self._load_threshold = max(0.5, min(0.95, threshold))

    def set_data(self, data: List[Dict]) -> None:
        """
        Set initial data, replacing any existing data.

        Args:
            data: List of dictionaries
        """
        self.clear_data()
        self.append_data(data)

    def append_data(self, data: List[Dict]) -> None:
        """
        Append data to the table.

        Args:
            data: List of dictionaries
        """
        if not data:
            return

        start_row = self.rowCount()
        self.setRowCount(start_row + len(data))

        for i, row_data in enumerate(data):
            row = start_row + i
            self._data.append(row_data)

            for col, key in enumerate(self._column_keys):
                value = row_data.get(key, "")
                item = QTableWidgetItem(str(value) if value is not None else "")
                self.setItem(row, col, item)

        self._loaded_count = len(self._data)
        self._is_loading = False

        logger.debug(f"LazyTable: appended {len(data)} rows, total={self._loaded_count}")

    def clear_data(self) -> None:
        """Clear all data from table."""
        self.setRowCount(0)
        self._data.clear()
        self._loaded_count = 0

    def reset(self) -> None:
        """Reset table to initial state."""
        self.clear_data()
        self._total_count = 0
        self._is_loading = False

    def get_row_data(self, row: int) -> Optional[Dict]:
        """Get data for a specific row."""
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def get_selected_data(self) -> Optional[Dict]:
        """Get data for selected row."""
        rows = self.selectionModel().selectedRows()
        if rows:
            return self.get_row_data(rows[0].row())
        return None

    def _on_scroll(self, value: int) -> None:
        """Handle scroll event."""
        scrollbar = self.verticalScrollBar()
        max_value = scrollbar.maximum()

        if max_value == 0:
            return

        # Calculate scroll position
        position = value / max_value

        # Check if we need to load more
        if position >= self._load_threshold:
            self.scroll_near_end.emit()
            self._request_load_more()

    def _request_load_more(self) -> None:
        """Request loading of more data."""
        if self._is_loading:
            return

        # Check if more data available
        if self._total_count > 0 and self._loaded_count >= self._total_count:
            return

        self._is_loading = True
        offset = self._loaded_count
        logger.debug(f"LazyTable: requesting more data at offset {offset}")
        self.load_more_requested.emit(offset)

    def _on_cell_clicked(self, row: int, column: int) -> None:
        """Handle cell click."""
        data = self.get_row_data(row)
        if data:
            self.row_clicked.emit(row, data)

    def _on_cell_double_clicked(self, row: int, column: int) -> None:
        """Handle cell double click."""
        data = self.get_row_data(row)
        if data:
            self.row_double_clicked.emit(row, data)

    @property
    def is_loading(self) -> bool:
        """Check if currently loading data."""
        return self._is_loading

    @property
    def loaded_count(self) -> int:
        """Get number of loaded rows."""
        return self._loaded_count

    @property
    def has_more(self) -> bool:
        """Check if more data is available."""
        if self._total_count == 0:
            return True  # Unknown total
        return self._loaded_count < self._total_count


# =============================================================================
# PAGINATION WIDGET
# =============================================================================


class PaginationWidget(QWidget):
    """
    Pagination controls widget.

    Provides page navigation buttons and info display.

    Signals:
        page_changed(int): Emitted when page changes (1-indexed)
        page_size_changed(int): Emitted when page size changes

    Example:
    --------
    ```python
    pagination = PaginationWidget()
    pagination.set_total_items(1000)
    pagination.set_page_size(50)
    pagination.page_changed.connect(self._load_page)

    def _load_page(page):
        offset = (page - 1) * pagination.page_size
        data = db.query(offset=offset, limit=pagination.page_size)
        table.set_data(data)
    ```
    """

    page_changed = Signal(int)  # 1-indexed page number
    page_size_changed = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._total_items = 0
        self._page_size = 50
        self._current_page = 1
        self._page_sizes = [25, 50, 100, 200]

        self._setup_ui()
        self._connect_signals()
        self._update_display()

    def _setup_ui(self) -> None:
        """Setup pagination UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(8)

        # Info label
        self._info_label = QLabel()
        self._info_label.setStyleSheet("color: #666;")
        layout.addWidget(self._info_label)

        layout.addStretch()

        # First page button
        self._first_btn = QPushButton("|<")
        self._first_btn.setFixedWidth(40)
        self._first_btn.setToolTip("Halaman pertama")
        layout.addWidget(self._first_btn)

        # Previous button
        self._prev_btn = QPushButton("<")
        self._prev_btn.setFixedWidth(40)
        self._prev_btn.setToolTip("Halaman sebelumnya")
        layout.addWidget(self._prev_btn)

        # Page buttons container
        self._page_buttons_layout = QHBoxLayout()
        self._page_buttons_layout.setSpacing(4)
        layout.addLayout(self._page_buttons_layout)

        # Next button
        self._next_btn = QPushButton(">")
        self._next_btn.setFixedWidth(40)
        self._next_btn.setToolTip("Halaman berikutnya")
        layout.addWidget(self._next_btn)

        # Last page button
        self._last_btn = QPushButton(">|")
        self._last_btn.setFixedWidth(40)
        self._last_btn.setToolTip("Halaman terakhir")
        layout.addWidget(self._last_btn)

        layout.addSpacing(16)

        # Page size selector
        size_label = QLabel("Tampilkan:")
        layout.addWidget(size_label)

        self._size_combo = QComboBox()
        for size in self._page_sizes:
            self._size_combo.addItem(str(size), size)
        self._size_combo.setCurrentText(str(self._page_size))
        self._size_combo.setFixedWidth(70)
        layout.addWidget(self._size_combo)

        per_page_label = QLabel("per halaman")
        layout.addWidget(per_page_label)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self._first_btn.clicked.connect(lambda: self.go_to_page(1))
        self._prev_btn.clicked.connect(self.previous_page)
        self._next_btn.clicked.connect(self.next_page)
        self._last_btn.clicked.connect(lambda: self.go_to_page(self.total_pages))
        self._size_combo.currentIndexChanged.connect(self._on_size_changed)

    def _update_display(self) -> None:
        """Update display based on current state."""
        total_pages = self.total_pages

        # Update info label
        if self._total_items == 0:
            self._info_label.setText("Tidak ada data")
        else:
            start = (self._current_page - 1) * self._page_size + 1
            end = min(self._current_page * self._page_size, self._total_items)
            self._info_label.setText(
                f"Menampilkan {start}-{end} dari {self._total_items}"
            )

        # Update button states
        self._first_btn.setEnabled(self._current_page > 1)
        self._prev_btn.setEnabled(self._current_page > 1)
        self._next_btn.setEnabled(self._current_page < total_pages)
        self._last_btn.setEnabled(self._current_page < total_pages)

        # Update page buttons
        self._update_page_buttons()

    def _update_page_buttons(self) -> None:
        """Update page number buttons."""
        # Clear existing buttons
        while self._page_buttons_layout.count():
            item = self._page_buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total_pages = self.total_pages
        if total_pages <= 1:
            return

        # Calculate which pages to show
        pages_to_show = []
        max_buttons = 7

        if total_pages <= max_buttons:
            pages_to_show = list(range(1, total_pages + 1))
        else:
            # Always show first, last, current, and neighbors
            pages_to_show = [1]

            start = max(2, self._current_page - 1)
            end = min(total_pages - 1, self._current_page + 1)

            if start > 2:
                pages_to_show.append(-1)  # Ellipsis

            for p in range(start, end + 1):
                if p not in pages_to_show:
                    pages_to_show.append(p)

            if end < total_pages - 1:
                pages_to_show.append(-1)  # Ellipsis

            if total_pages not in pages_to_show:
                pages_to_show.append(total_pages)

        # Create buttons
        for page in pages_to_show:
            if page == -1:
                # Ellipsis
                label = QLabel("...")
                label.setStyleSheet("color: #666; padding: 0 4px;")
                self._page_buttons_layout.addWidget(label)
            else:
                btn = QPushButton(str(page))
                btn.setFixedWidth(36)
                btn.setCheckable(True)
                btn.setChecked(page == self._current_page)

                if page == self._current_page:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2196F3;
                            color: white;
                            font-weight: bold;
                        }
                    """)

                btn.clicked.connect(lambda checked, p=page: self.go_to_page(p))
                self._page_buttons_layout.addWidget(btn)

    def _on_size_changed(self, index: int) -> None:
        """Handle page size change."""
        new_size = self._size_combo.currentData()
        if new_size != self._page_size:
            self._page_size = new_size
            self._current_page = 1  # Reset to first page
            self._update_display()
            self.page_size_changed.emit(new_size)
            self.page_changed.emit(1)

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================

    def set_total_items(self, count: int) -> None:
        """Set total number of items."""
        self._total_items = max(0, count)
        self._current_page = 1
        self._update_display()

    def set_page_size(self, size: int) -> None:
        """Set page size."""
        if size in self._page_sizes:
            self._page_size = size
            self._size_combo.setCurrentText(str(size))
        self._update_display()

    def set_page_size_options(self, sizes: List[int]) -> None:
        """Set available page size options."""
        self._page_sizes = sizes
        self._size_combo.clear()
        for size in sizes:
            self._size_combo.addItem(str(size), size)

    def go_to_page(self, page: int) -> None:
        """Go to specific page (1-indexed)."""
        page = max(1, min(page, self.total_pages))
        if page != self._current_page:
            self._current_page = page
            self._update_display()
            self.page_changed.emit(page)

    def next_page(self) -> None:
        """Go to next page."""
        if self._current_page < self.total_pages:
            self.go_to_page(self._current_page + 1)

    def previous_page(self) -> None:
        """Go to previous page."""
        if self._current_page > 1:
            self.go_to_page(self._current_page - 1)

    @property
    def total_pages(self) -> int:
        """Get total number of pages."""
        if self._total_items == 0 or self._page_size == 0:
            return 1
        return (self._total_items + self._page_size - 1) // self._page_size

    @property
    def current_page(self) -> int:
        """Get current page (1-indexed)."""
        return self._current_page

    @property
    def page_size(self) -> int:
        """Get current page size."""
        return self._page_size

    @property
    def offset(self) -> int:
        """Get current offset for database queries."""
        return (self._current_page - 1) * self._page_size


# =============================================================================
# PAGINATED TABLE WIDGET
# =============================================================================


class PaginatedTableWidget(QFrame):
    """
    Table widget with built-in pagination controls.

    Combines LazyTableWidget and PaginationWidget for easy use.

    Signals:
        data_requested(int, int): Emitted with (offset, limit) when data needed
        row_clicked(int, dict): Emitted when row is clicked
        row_double_clicked(int, dict): Emitted when row is double-clicked

    Example:
    --------
    ```python
    table = PaginatedTableWidget(
        columns=["ID", "Nama", "Nilai"],
        headers={"ID": "ID", "Nama": "Nama Transaksi", "Nilai": "Nilai (Rp)"}
    )
    table.set_total_count(1000)
    table.data_requested.connect(self._load_data)

    def _load_data(offset, limit):
        data = db.query(offset=offset, limit=limit)
        table.set_data(data)
    ```
    """

    data_requested = Signal(int, int)  # offset, limit
    row_clicked = Signal(int, dict)
    row_double_clicked = Signal(int, dict)

    def __init__(
        self,
        columns: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self._columns = columns or []
        self._headers = headers or {}

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup combined UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Table
        self._table = LazyTableWidget()
        if self._columns:
            self._table.set_columns(self._columns, self._headers)
        layout.addWidget(self._table, 1)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #e0e0e0;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Pagination
        self._pagination = PaginationWidget()
        layout.addWidget(self._pagination)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self._pagination.page_changed.connect(self._on_page_changed)
        self._pagination.page_size_changed.connect(self._on_page_size_changed)
        self._table.row_clicked.connect(self.row_clicked)
        self._table.row_double_clicked.connect(self.row_double_clicked)

    def _on_page_changed(self, page: int) -> None:
        """Handle page change."""
        offset = self._pagination.offset
        limit = self._pagination.page_size
        self.data_requested.emit(offset, limit)

    def _on_page_size_changed(self, size: int) -> None:
        """Handle page size change."""
        self.data_requested.emit(0, size)

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def set_columns(
        self,
        columns: List[str],
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        """Set table columns."""
        self._columns = columns
        self._headers = headers or {}
        self._table.set_columns(columns, headers)

    def set_total_count(self, count: int) -> None:
        """Set total item count."""
        self._pagination.set_total_items(count)

    def set_page_size(self, size: int) -> None:
        """Set page size."""
        self._pagination.set_page_size(size)

    def set_data(self, data: List[Dict]) -> None:
        """Set table data (for current page)."""
        self._table.set_data(data)

    def clear(self) -> None:
        """Clear table data."""
        self._table.clear_data()
        self._pagination.set_total_items(0)

    def get_selected_data(self) -> Optional[Dict]:
        """Get selected row data."""
        return self._table.get_selected_data()

    def refresh(self) -> None:
        """Trigger data refresh for current page."""
        offset = self._pagination.offset
        limit = self._pagination.page_size
        self.data_requested.emit(offset, limit)

    @property
    def table(self) -> LazyTableWidget:
        """Get underlying table widget."""
        return self._table

    @property
    def pagination(self) -> PaginationWidget:
        """Get pagination widget."""
        return self._pagination


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_lazy_table(
    columns: List[str],
    headers: Optional[Dict[str, str]] = None,
    page_size: int = 50
) -> LazyTableWidget:
    """
    Create a lazy loading table.

    Args:
        columns: Column keys
        headers: Optional header display names
        page_size: Items per page

    Returns:
        LazyTableWidget instance
    """
    table = LazyTableWidget()
    table.set_columns(columns, headers)
    table.set_page_size(page_size)
    return table


def create_paginated_table(
    columns: List[str],
    headers: Optional[Dict[str, str]] = None,
    page_size: int = 50
) -> PaginatedTableWidget:
    """
    Create a paginated table with controls.

    Args:
        columns: Column keys
        headers: Optional header display names
        page_size: Items per page

    Returns:
        PaginatedTableWidget instance
    """
    table = PaginatedTableWidget(columns=columns, headers=headers)
    table.set_page_size(page_size)
    return table


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Models
    'LazyListModel',
    'LazyTableModel',

    # Widgets
    'LazyTableWidget',
    'PaginationWidget',
    'PaginatedTableWidget',

    # Factory functions
    'create_lazy_table',
    'create_paginated_table',
]
