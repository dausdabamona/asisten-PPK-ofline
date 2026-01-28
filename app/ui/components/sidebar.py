"""
PPK DOCUMENT FACTORY - Sidebar Navigation Component
====================================================
Sidebar navigation dengan struktur menu hierarkis.

Struktur Menu:
- Dashboard
- Pencairan Dana
  - UP (dengan badge jumlah aktif)
  - TUP (dengan badge jumlah aktif)
  - LS (dengan badge jumlah aktif)
- Pengadaan
  - Paket Pekerjaan
  - Data Penyedia
  - Master Barang
- Pengaturan
  - Data Satker
  - Data Pegawai
  - Template

Fitur:
- Collapsible/expandable menu
- Active state indicator
- Badge counter untuk item aktif
- Signal untuk navigasi
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QSpacerItem, QSizePolicy,
    QScrollArea, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor

from typing import Dict, Optional


class SidebarBadge(QLabel):
    """Badge untuk menampilkan counter di menu item."""

    def __init__(self, count: int = 0, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(24, 18)
        self.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            border-radius: 9px;
            font-size: 11px;
            font-weight: bold;
        """)
        self.set_count(count)

    def set_count(self, count: int):
        """Update badge count."""
        if count > 0:
            self.setText(str(count) if count < 100 else "99+")
            self.show()
        else:
            self.hide()


class SidebarMenuItem(QPushButton):
    """Menu item dalam sidebar."""

    def __init__(
        self,
        text: str,
        icon: str = None,
        menu_id: str = None,
        parent=None,
        indent: int = 0,
        badge_count: int = 0
    ):
        super().__init__(parent)
        self.menu_id = menu_id or text.lower().replace(" ", "_")
        self.indent = indent
        self._is_active = False

        # Setup layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20 + (indent * 15), 12, 15, 12)
        layout.setSpacing(12)

        # Icon placeholder (using text for now, can be replaced with QIcon)
        if icon:
            icon_label = QLabel(icon)
            icon_label.setFixedWidth(20)
            icon_label.setStyleSheet("color: inherit;")
            layout.addWidget(icon_label)

        # Text
        text_label = QLabel(text)
        text_label.setStyleSheet("color: inherit; background: transparent;")
        layout.addWidget(text_label)

        # Spacer
        layout.addStretch()

        # Badge
        self.badge = SidebarBadge(badge_count)
        layout.addWidget(self.badge)

        # Styling
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(44)
        self._update_style()

    def set_active(self, active: bool):
        """Set active state."""
        self._is_active = active
        self.setChecked(active)
        self._update_style()

    def set_badge_count(self, count: int):
        """Update badge count."""
        self.badge.set_count(count)

    def _update_style(self):
        """Update styling based on state."""
        base_style = """
            QPushButton {
                background-color: transparent;
                color: #bdc3c7;
                text-align: left;
                border: none;
                border-radius: 0;
            }
            QPushButton:hover {
                background-color: #34495e;
                color: #ffffff;
            }
        """

        if self._is_active:
            # Determine color based on menu_id
            if "up" in self.menu_id.lower() and "tup" not in self.menu_id.lower():
                bg_color = "#27ae60"
                border_color = "#1e8449"
            elif "tup" in self.menu_id.lower():
                bg_color = "#f39c12"
                border_color = "#d68910"
            elif "ls" in self.menu_id.lower():
                bg_color = "#3498db"
                border_color = "#2980b9"
            else:
                bg_color = "#3498db"
                border_color = "#2980b9"

            base_style = f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: #ffffff;
                    border-left: 4px solid {border_color};
                    text-align: left;
                    border-radius: 0;
                }}
                QPushButton:hover {{
                    background-color: {border_color};
                }}
            """

        self.setStyleSheet(base_style)


class SidebarSection(QWidget):
    """Section header dalam sidebar."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 8)
        layout.setSpacing(0)

        label = QLabel(title.upper())
        label.setStyleSheet("""
            color: #95a5a6;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        layout.addWidget(label)


class Sidebar(QWidget):
    """
    Sidebar navigation component.

    Signals:
        menu_clicked(str): Emitted when a menu item is clicked, with menu_id
        collapse_toggled(bool): Emitted when sidebar collapse state changes
    """

    menu_clicked = Signal(str)
    collapse_toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._is_collapsed = False
        self._menu_items: Dict[str, SidebarMenuItem] = {}
        self._current_menu = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup the sidebar UI."""
        self.setFixedWidth(240)
        self.setMinimumHeight(600)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Scrollable menu area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)

        menu_widget = QWidget()
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)

        # Dashboard
        self._add_menu_item(menu_layout, "Dashboard", "home", "dashboard")

        # Pencairan Dana Section
        menu_layout.addWidget(SidebarSection("Pencairan Dana"))
        self._add_menu_item(menu_layout, "Uang Persediaan (UP)", "wallet", "up", indent=1)
        self._add_menu_item(menu_layout, "Tambahan UP (TUP)", "plus-circle", "tup", indent=1)
        self._add_menu_item(menu_layout, "Pembayaran LS", "send", "ls", indent=1)

        # Pengadaan Section
        menu_layout.addWidget(SidebarSection("Pengadaan"))
        self._add_menu_item(menu_layout, "Paket Pekerjaan", "package", "paket", indent=1)
        self._add_menu_item(menu_layout, "Data Penyedia", "users", "penyedia", indent=1)
        self._add_menu_item(menu_layout, "Master Barang", "box", "master_barang", indent=1)

        # Pengaturan Section
        menu_layout.addWidget(SidebarSection("Pengaturan"))
        self._add_menu_item(menu_layout, "Data Satker", "building", "satker", indent=1)
        self._add_menu_item(menu_layout, "Data Pegawai", "user", "pegawai", indent=1)
        self._add_menu_item(menu_layout, "Template Dokumen", "file-text", "template", indent=1)
        self._add_menu_item(menu_layout, "Backup & Restore", "save", "backup", indent=1)

        # Spacer
        menu_layout.addStretch()

        scroll.setWidget(menu_widget)
        main_layout.addWidget(scroll)

        # Footer with version
        footer = self._create_footer()
        main_layout.addWidget(footer)

        # Background color
        self.setStyleSheet("""
            #sidebar {
                background-color: #2c3e50;
            }
        """)

    def _create_header(self) -> QWidget:
        """Create sidebar header with app title."""
        header = QWidget()
        header.setStyleSheet("background-color: #243342;")

        layout = QVBoxLayout(header)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(5)

        # App title
        title = QLabel("Asisten PPK")
        title.setStyleSheet("""
            color: #ecf0f1;
            font-size: 18px;
            font-weight: bold;
        """)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Workflow Pencairan Dana")
        subtitle.setStyleSheet("""
            color: #95a5a6;
            font-size: 11px;
        """)
        layout.addWidget(subtitle)

        return header

    def _create_footer(self) -> QWidget:
        """Create sidebar footer."""
        footer = QWidget()
        footer.setStyleSheet("background-color: #243342;")

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(15, 10, 15, 10)

        version = QLabel("v4.0 Workflow Edition")
        version.setStyleSheet("""
            color: #7f8c8d;
            font-size: 10px;
        """)
        layout.addWidget(version)

        layout.addStretch()

        # Collapse button
        collapse_btn = QPushButton("<")
        collapse_btn.setFixedSize(28, 28)
        collapse_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: #95a5a6;
                border: none;
                border-radius: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
        """)
        collapse_btn.clicked.connect(self._toggle_collapse)
        layout.addWidget(collapse_btn)

        return footer

    def _add_menu_item(
        self,
        layout: QVBoxLayout,
        text: str,
        icon: str,
        menu_id: str,
        indent: int = 0,
        badge_count: int = 0
    ):
        """Add a menu item to the sidebar."""
        item = SidebarMenuItem(
            text=text,
            icon=self._get_icon_char(icon),
            menu_id=menu_id,
            indent=indent,
            badge_count=badge_count
        )
        item.clicked.connect(lambda: self._on_menu_clicked(menu_id))

        self._menu_items[menu_id] = item
        layout.addWidget(item)

    def _get_icon_char(self, icon_name: str) -> str:
        """Get unicode character for icon (placeholder - can be replaced with actual icons)."""
        icons = {
            "home": "H",
            "wallet": "W",
            "plus-circle": "+",
            "send": "S",
            "package": "P",
            "users": "U",
            "box": "B",
            "building": "O",
            "user": "U",
            "file-text": "F",
        }
        return icons.get(icon_name, "*")

    def _on_menu_clicked(self, menu_id: str):
        """Handle menu item click."""
        # Update active state
        self.set_active_menu(menu_id)

        # Emit signal
        self.menu_clicked.emit(menu_id)

    def set_active_menu(self, menu_id: str):
        """Set the active menu item."""
        # Deactivate previous
        if self._current_menu and self._current_menu in self._menu_items:
            self._menu_items[self._current_menu].set_active(False)

        # Activate new
        if menu_id in self._menu_items:
            self._menu_items[menu_id].set_active(True)
            self._current_menu = menu_id

    def set_badge_count(self, menu_id: str, count: int):
        """Set badge count for a menu item."""
        if menu_id in self._menu_items:
            self._menu_items[menu_id].set_badge_count(count)

    def update_badges(self, counts: Dict[str, int]):
        """Update multiple badge counts at once."""
        for menu_id, count in counts.items():
            self.set_badge_count(menu_id, count)

    def _toggle_collapse(self):
        """Toggle sidebar collapse state."""
        self._is_collapsed = not self._is_collapsed

        if self._is_collapsed:
            self.setFixedWidth(60)
        else:
            self.setFixedWidth(240)

        self.collapse_toggled.emit(self._is_collapsed)

    def is_collapsed(self) -> bool:
        """Check if sidebar is collapsed."""
        return self._is_collapsed

    def get_menu_item(self, menu_id: str) -> Optional[SidebarMenuItem]:
        """Get a menu item by ID."""
        return self._menu_items.get(menu_id)
