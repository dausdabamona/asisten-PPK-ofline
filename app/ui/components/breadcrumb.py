"""
PPK DOCUMENT FACTORY - Breadcrumb Navigation Component
=======================================================
Breadcrumb navigation untuk:
- Menampilkan path navigasi
- Clickable items untuk navigation
- Custom separator
- Truncation untuk path panjang

Author: PPK Document Factory Team
Version: 4.0
"""

from dataclasses import dataclass
from typing import Optional, List

from PySide6.QtWidgets import (
    QFrame, QWidget, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal


# =============================================================================
# BREADCRUMB ITEM
# =============================================================================

@dataclass
class BreadcrumbItem:
    """
    Single breadcrumb item.

    Attributes:
        label: Display text
        path: Navigation path/identifier
        icon: Optional icon text
    """
    label: str
    path: str
    icon: str = ""


# =============================================================================
# BREADCRUMB
# =============================================================================

class Breadcrumb(QFrame):
    """
    Breadcrumb navigation component.

    Features:
    - Clickable navigation items
    - Custom separator
    - Last item is bold (current page)
    - Truncation for long paths

    Signals:
        item_clicked(str): Emitted when an item is clicked (path)

    Usage:
        breadcrumb = Breadcrumb()
        breadcrumb.set_items([
            BreadcrumbItem("Dashboard", "dashboard"),
            BreadcrumbItem("UP", "up"),
            BreadcrumbItem("UP-2024-001", "up_detail"),
        ])
        breadcrumb.item_clicked.connect(self._navigate)
    """

    # Signals
    item_clicked = Signal(str)  # path

    # Default separator
    DEFAULT_SEPARATOR = "\u203A"  # › character

    def __init__(
        self,
        separator: str = DEFAULT_SEPARATOR,
        max_visible: int = 5,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize breadcrumb.

        Args:
            separator: Separator string between items
            max_visible: Maximum visible items (others truncated)
            parent: Parent widget
        """
        super().__init__(parent)

        self._separator = separator
        self._max_visible = max_visible
        self._items: List[BreadcrumbItem] = []
        self._item_widgets: List[QWidget] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup breadcrumb UI."""
        self.setObjectName("breadcrumb")
        self.setStyleSheet("""
            QFrame#breadcrumb {
                background-color: transparent;
            }
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(36)

        # Main layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def set_items(self, items: List[BreadcrumbItem]) -> None:
        """
        Set breadcrumb items.

        Args:
            items: List of BreadcrumbItem
        """
        self._items = items
        self._rebuild_ui()

    def push(self, label: str, path: str, icon: str = "") -> None:
        """
        Push new item to breadcrumb.

        Args:
            label: Display text
            path: Navigation path
            icon: Optional icon
        """
        self._items.append(BreadcrumbItem(label, path, icon))
        self._rebuild_ui()

    def pop(self) -> Optional[BreadcrumbItem]:
        """
        Pop last item from breadcrumb.

        Returns:
            Removed BreadcrumbItem or None if empty
        """
        if self._items:
            item = self._items.pop()
            self._rebuild_ui()
            return item
        return None

    def clear(self) -> None:
        """Clear all items."""
        self._items.clear()
        self._rebuild_ui()

    def set_separator(self, separator: str) -> None:
        """
        Set separator string.

        Args:
            separator: New separator string
        """
        self._separator = separator
        self._rebuild_ui()

    def _rebuild_ui(self) -> None:
        """Rebuild breadcrumb UI."""
        # Clear existing widgets
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._item_widgets.clear()

        if not self._items:
            return

        # Determine visible items (truncate if needed)
        visible_items = self._items
        show_ellipsis = False

        if len(self._items) > self._max_visible:
            # Show first, ellipsis, and last (max_visible - 1) items
            first_item = self._items[0]
            last_items = self._items[-(self._max_visible - 1):]
            visible_items = [first_item] + last_items
            show_ellipsis = True

        # Add items
        for i, item in enumerate(visible_items):
            is_last = (i == len(visible_items) - 1)
            is_first = (i == 0)

            # Add ellipsis after first item if truncated
            if show_ellipsis and is_first:
                self._add_item_widget(item, clickable=True)
                self._add_separator()
                self._add_ellipsis()
                self._add_separator()
                continue

            # Add item widget
            self._add_item_widget(item, clickable=not is_last)

            # Add separator (except after last item)
            if not is_last:
                self._add_separator()

        # Add stretch at the end
        self._layout.addStretch()

    def _add_item_widget(self, item: BreadcrumbItem, clickable: bool = True) -> None:
        """Add item widget to layout."""
        if clickable:
            # Clickable button
            btn = QPushButton()
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName("breadcrumbItem")

            # Build label with icon if present
            label = item.label
            if item.icon:
                label = f"{item.icon} {label}"

            btn.setText(label)
            btn.setStyleSheet("""
                QPushButton#breadcrumbItem {
                    background-color: transparent;
                    color: #3498db;
                    border: none;
                    font-size: 14px;
                    padding: 4px 8px;
                    border-radius: 4px;
                }
                QPushButton#breadcrumbItem:hover {
                    background-color: #ecf0f1;
                    color: #2980b9;
                }
            """)
            btn.clicked.connect(lambda checked, p=item.path: self.item_clicked.emit(p))
            self._layout.addWidget(btn)
            self._item_widgets.append(btn)
        else:
            # Current page (not clickable, bold)
            label = QLabel()
            text = item.label
            if item.icon:
                text = f"{item.icon} {text}"
            label.setText(text)
            label.setStyleSheet("""
                QLabel {
                    color: #2c3e50;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 4px 8px;
                }
            """)
            self._layout.addWidget(label)
            self._item_widgets.append(label)

    def _add_separator(self) -> None:
        """Add separator to layout."""
        sep = QLabel(self._separator)
        sep.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 14px;
                padding: 0 2px;
            }
        """)
        self._layout.addWidget(sep)

    def _add_ellipsis(self) -> None:
        """Add ellipsis indicator for truncated items."""
        ellipsis = QLabel("...")
        ellipsis.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 14px;
                padding: 4px 4px;
            }
        """)
        self._layout.addWidget(ellipsis)

    def get_items(self) -> List[BreadcrumbItem]:
        """
        Get all breadcrumb items.

        Returns:
            List of BreadcrumbItem
        """
        return self._items.copy()

    def get_current(self) -> Optional[BreadcrumbItem]:
        """
        Get current (last) breadcrumb item.

        Returns:
            Last BreadcrumbItem or None if empty
        """
        if self._items:
            return self._items[-1]
        return None

    def navigate_to(self, path: str) -> bool:
        """
        Navigate to a path (trim items after it).

        Args:
            path: Path to navigate to

        Returns:
            True if path was found and navigated
        """
        for i, item in enumerate(self._items):
            if item.path == path:
                # Trim items after this one
                self._items = self._items[:i + 1]
                self._rebuild_ui()
                return True
        return False


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_breadcrumb(
    items: Optional[List[tuple]] = None,
    separator: str = Breadcrumb.DEFAULT_SEPARATOR,
    parent: Optional[QWidget] = None
) -> Breadcrumb:
    """
    Create a breadcrumb with initial items.

    Args:
        items: List of (label, path) tuples
        separator: Separator string
        parent: Parent widget

    Returns:
        Configured Breadcrumb

    Example:
        breadcrumb = create_breadcrumb([
            ("Dashboard", "dashboard"),
            ("UP", "up"),
            ("Detail", "detail"),
        ])
    """
    bc = Breadcrumb(separator, parent=parent)

    if items:
        bc.set_items([
            BreadcrumbItem(label, path)
            for label, path in items
        ])

    return bc
