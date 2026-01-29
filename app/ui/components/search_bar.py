"""
PPK DOCUMENT FACTORY - Search Bar Component
============================================
Modern search bar dengan:
- Debounce untuk mengurangi frequency signal
- Clear button
- Optional filter dropdowns
- Advanced search support

Author: PPK Document Factory Team
Version: 4.0
"""

from typing import Optional, List, Dict, Callable

from PySide6.QtWidgets import (
    QFrame, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
    QPushButton, QComboBox, QLabel, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QKeySequence, QShortcut


# =============================================================================
# SEARCH BAR
# =============================================================================

class SearchBar(QFrame):
    """
    Modern search bar component.

    Features:
    - Debounce for search_changed signal
    - Clear button
    - Search icon
    - Optional filter dropdowns
    - Keyboard shortcuts (Ctrl+F to focus, Escape to clear)

    Signals:
        search_changed(str): Emitted after debounce when text changes
        search_submitted(str): Emitted when Enter is pressed
        cleared(): Emitted when search is cleared

    Usage:
        search = SearchBar(placeholder="Cari transaksi...")
        search.add_filter("status", ["Semua", "Aktif", "Selesai"])
        search.search_changed.connect(self._filter_data)
    """

    # Signals
    search_changed = Signal(str)
    search_submitted = Signal(str)
    cleared = Signal()
    filter_changed = Signal(str, str)  # filter_name, value

    def __init__(
        self,
        placeholder: str = "Cari...",
        debounce_ms: int = 300,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize search bar.

        Args:
            placeholder: Placeholder text for input
            debounce_ms: Debounce delay in milliseconds
            parent: Parent widget
        """
        super().__init__(parent)

        self._placeholder = placeholder
        self._debounce_ms = debounce_ms
        self._filters: Dict[str, QComboBox] = {}

        # Debounce timer
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_search_changed)

        self._setup_ui()
        self._setup_shortcuts()

    def _setup_ui(self) -> None:
        """Setup search bar UI."""
        self.setObjectName("searchBar")
        self.setStyleSheet("""
            QFrame#searchBar {
                background-color: #ffffff;
                border: 2px solid #e9ecef;
                border-radius: 8px;
            }
            QFrame#searchBar:focus-within {
                border-color: #3498db;
            }
        """)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Search icon
        icon_label = QLabel("\U0001F50D")  # Magnifying glass
        icon_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 16px;
            }
        """)
        icon_label.setFixedWidth(24)
        layout.addWidget(icon_label)

        # Search input
        self._input = QLineEdit()
        self._input.setPlaceholderText(self._placeholder)
        self._input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 14px;
                color: #2c3e50;
                padding: 4px 0;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
        """)
        self._input.textChanged.connect(self._on_text_changed)
        self._input.returnPressed.connect(self._on_return_pressed)
        layout.addWidget(self._input)

        # Filter container (for dropdowns)
        self._filter_container = QHBoxLayout()
        self._filter_container.setSpacing(8)
        layout.addLayout(self._filter_container)

        # Clear button
        self._clear_btn = QPushButton("\u00D7")
        self._clear_btn.setObjectName("clearBtn")
        self._clear_btn.setFixedSize(24, 24)
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.setStyleSheet("""
            QPushButton#clearBtn {
                background-color: transparent;
                color: #95a5a6;
                border: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 12px;
            }
            QPushButton#clearBtn:hover {
                background-color: #ecf0f1;
                color: #7f8c8d;
            }
        """)
        self._clear_btn.clicked.connect(self.clear)
        self._clear_btn.hide()  # Hidden until there's text
        layout.addWidget(self._clear_btn)

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        # Escape to clear
        escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self._input)
        escape_shortcut.activated.connect(self.clear)

    def _on_text_changed(self, text: str) -> None:
        """Handle text changed with debounce."""
        # Show/hide clear button
        self._clear_btn.setVisible(bool(text))

        # Restart debounce timer
        self._debounce_timer.stop()
        self._debounce_timer.start(self._debounce_ms)

    def _on_return_pressed(self) -> None:
        """Handle Enter key press."""
        self._debounce_timer.stop()
        self.search_submitted.emit(self._input.text())

    def _emit_search_changed(self) -> None:
        """Emit search_changed signal after debounce."""
        self.search_changed.emit(self._input.text())

    def set_text(self, text: str) -> None:
        """
        Set search text.

        Args:
            text: Text to set
        """
        self._input.setText(text)

    def get_text(self) -> str:
        """
        Get current search text.

        Returns:
            Current search text
        """
        return self._input.text()

    def clear(self) -> None:
        """Clear search text."""
        self._input.clear()
        self._clear_btn.hide()
        self.cleared.emit()

    def focus(self) -> None:
        """Focus the search input."""
        self._input.setFocus()
        self._input.selectAll()

    def add_filter(
        self,
        name: str,
        options: List[str],
        default_index: int = 0
    ) -> None:
        """
        Add a filter dropdown.

        Args:
            name: Filter name (for identification)
            options: List of options
            default_index: Default selected index
        """
        combo = QComboBox()
        combo.setObjectName(f"filter_{name}")
        combo.addItems(options)
        combo.setCurrentIndex(default_index)
        combo.setStyleSheet("""
            QComboBox {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 4px 24px 4px 8px;
                font-size: 13px;
                color: #2c3e50;
                min-width: 80px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #7f8c8d;
                margin-right: 8px;
            }
        """)
        combo.currentTextChanged.connect(
            lambda value: self.filter_changed.emit(name, value)
        )

        self._filters[name] = combo
        self._filter_container.addWidget(combo)

    def get_filter_value(self, name: str) -> Optional[str]:
        """
        Get current value of a filter.

        Args:
            name: Filter name

        Returns:
            Filter value or None if not found
        """
        if name in self._filters:
            return self._filters[name].currentText()
        return None

    def set_filter_value(self, name: str, value: str) -> None:
        """
        Set value of a filter.

        Args:
            name: Filter name
            value: Value to set
        """
        if name in self._filters:
            self._filters[name].setCurrentText(value)

    def get_all_filter_values(self) -> Dict[str, str]:
        """
        Get all filter values.

        Returns:
            Dictionary of filter name -> value
        """
        return {
            name: combo.currentText()
            for name, combo in self._filters.items()
        }


# =============================================================================
# ADVANCED SEARCH BAR
# =============================================================================

class AdvancedSearchBar(SearchBar):
    """
    Advanced search bar with expandable options.

    Features:
    - All SearchBar features
    - Date range filter
    - Expandable advanced options panel

    Signals:
        advanced_search(dict): Emitted with all search parameters

    Usage:
        search = AdvancedSearchBar()
        search.add_filter("mekanisme", ["Semua", "UP", "TUP", "LS"])
        search.set_date_range_enabled(True)
        search.advanced_search.connect(self._do_advanced_search)
    """

    # Signals
    advanced_search = Signal(dict)

    def __init__(
        self,
        placeholder: str = "Cari...",
        debounce_ms: int = 300,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize advanced search bar.

        Args:
            placeholder: Placeholder text
            debounce_ms: Debounce delay
            parent: Parent widget
        """
        self._show_date_range = False
        self._advanced_expanded = False
        self._date_from = None
        self._date_to = None

        super().__init__(placeholder, debounce_ms, parent)

    def _setup_ui(self) -> None:
        """Setup advanced search bar UI."""
        # Call parent setup
        super()._setup_ui()

        # Add advanced toggle button
        self._advanced_btn = QPushButton("\u2699")  # Gear icon
        self._advanced_btn.setObjectName("advancedBtn")
        self._advanced_btn.setFixedSize(24, 24)
        self._advanced_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._advanced_btn.setStyleSheet("""
            QPushButton#advancedBtn {
                background-color: transparent;
                color: #95a5a6;
                border: none;
                font-size: 16px;
                border-radius: 12px;
            }
            QPushButton#advancedBtn:hover {
                background-color: #ecf0f1;
                color: #3498db;
            }
            QPushButton#advancedBtn:checked {
                background-color: #3498db;
                color: #ffffff;
            }
        """)
        self._advanced_btn.setCheckable(True)
        self._advanced_btn.clicked.connect(self._toggle_advanced)

        # Insert before clear button
        main_layout = self.layout()
        main_layout.insertWidget(main_layout.count() - 1, self._advanced_btn)

    def _toggle_advanced(self, checked: bool) -> None:
        """Toggle advanced options panel."""
        self._advanced_expanded = checked
        # Could emit signal or show/hide advanced panel
        # For now, just change button state

    def set_date_range_enabled(self, enabled: bool) -> None:
        """
        Enable/disable date range filter.

        Args:
            enabled: Whether to show date range filter
        """
        self._show_date_range = enabled
        # Would add date pickers to UI when enabled

    def get_search_params(self) -> dict:
        """
        Get all search parameters.

        Returns:
            Dictionary with text, filters, date_range
        """
        params = {
            'text': self.get_text(),
            'filters': self.get_all_filter_values(),
        }

        if self._show_date_range:
            params['date_from'] = self._date_from
            params['date_to'] = self._date_to

        return params

    def do_search(self) -> None:
        """Emit advanced search with all parameters."""
        self.advanced_search.emit(self.get_search_params())


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_search_bar(
    placeholder: str = "Cari...",
    filters: Optional[Dict[str, List[str]]] = None,
    debounce_ms: int = 300,
    parent: Optional[QWidget] = None
) -> SearchBar:
    """
    Create a search bar with optional filters.

    Args:
        placeholder: Placeholder text
        filters: Dictionary of filter name -> options list
        debounce_ms: Debounce delay
        parent: Parent widget

    Returns:
        Configured SearchBar
    """
    search = SearchBar(placeholder, debounce_ms, parent)

    if filters:
        for name, options in filters.items():
            search.add_filter(name, options)

    return search
