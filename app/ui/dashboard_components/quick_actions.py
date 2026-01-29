"""
PPK DOCUMENT FACTORY - Quick Actions Widget
============================================
Widget untuk menampilkan tombol-tombol aksi cepat di dashboard.

Menyediakan akses cepat untuk:
- Membuat transaksi UP baru
- Membuat transaksi TUP baru
- Membuat transaksi LS baru
- Membuat dokumen

Author: PPK Document Factory Team
Version: 4.0
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QFrame, QGraphicsDropShadowEffect, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QIcon

from typing import List, Tuple, Optional

from app.ui.icons.icon_provider import IconProvider


class QuickActionButton(QPushButton):
    """
    Styled button untuk quick action dengan icon.

    Features:
    - Icon di samping text
    - Color-coded berdasarkan tipe action
    - Hover effect
    """

    def __init__(
        self,
        text: str,
        action_id: str,
        color: str = "#3498db",
        icon_name: str = None,
        parent: QWidget = None
    ):
        """
        Initialize QuickActionButton.

        Args:
            text: Button text
            action_id: Identifier untuk action ini
            color: Primary color (hex)
            icon_name: Icon name dari IconProvider
            parent: Parent widget
        """
        super().__init__(parent)
        self.action_id = action_id
        self._color = color
        self._dark_color = self._darken_color(color)
        self._icon_name = icon_name

        self._setup_ui(text)

    def _setup_ui(self, text: str) -> None:
        """Setup button UI."""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(42)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # Set icon if provided
        if self._icon_name:
            try:
                icon = IconProvider.get_icon(self._icon_name, size=18, color="#ffffff")
                if not icon.isNull():
                    self.setIcon(icon)
                    self.setIconSize(QSize(18, 18))
            except Exception:
                pass

        self.setText(text)
        self._apply_style()

    def _apply_style(self) -> None:
        """Apply button styling."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self._dark_color};
            }}
            QPushButton:pressed {{
                background-color: {self._dark_color};
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
                color: #7f8c8d;
            }}
        """)

    def _darken_color(self, hex_color: str) -> str:
        """
        Darken a hex color for hover state.

        Args:
            hex_color: Original color in hex format

        Returns:
            Darkened color in hex format
        """
        # Predefined dark colors for common colors
        darken_map = {
            "#27ae60": "#1e8449",
            "#f39c12": "#d68910",
            "#3498db": "#2980b9",
            "#9b59b6": "#7d3c98",
            "#e74c3c": "#c0392b",
            "#1abc9c": "#16a085",
            "#34495e": "#2c3e50",
            "#95a5a6": "#7f8c8d",
        }

        if hex_color in darken_map:
            return darken_map[hex_color]

        # Fallback: simple darkening by adjusting RGB values
        try:
            hex_color = hex_color.lstrip('#')
            r = max(0, int(hex_color[0:2], 16) - 25)
            g = max(0, int(hex_color[2:4], 16) - 25)
            b = max(0, int(hex_color[4:6], 16) - 25)
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return hex_color

    def set_color(self, color: str) -> None:
        """
        Change button color.

        Args:
            color: New color in hex format
        """
        self._color = color
        self._dark_color = self._darken_color(color)
        self._apply_style()


class QuickActionsWidget(QFrame):
    """
    Widget untuk menampilkan tombol-tombol aksi cepat.

    Signals:
        action_clicked(str): Emitted ketika tombol diklik, dengan action_id

    Action IDs:
        - "new_up": Transaksi UP Baru
        - "new_tup": Transaksi TUP Baru
        - "new_ls": Transaksi LS Baru
        - "new_dokumen": Buat Dokumen

    Usage:
        widget = QuickActionsWidget()
        widget.action_clicked.connect(self.on_quick_action)

        def on_quick_action(self, action_id: str):
            if action_id == "new_up":
                self.create_new_up()
            elif action_id == "new_tup":
                self.create_new_tup()
            # ...
    """

    # Signal
    action_clicked = Signal(str)

    # Default actions configuration
    DEFAULT_ACTIONS: List[Tuple[str, str, str, str]] = [
        # (action_id, text, color, icon_name)
        ("new_up", "Transaksi UP Baru", "#27ae60", "plus-circle"),
        ("new_tup", "Transaksi TUP Baru", "#f39c12", "plus-circle"),
        ("new_ls", "Transaksi LS Baru", "#3498db", "plus-circle"),
        ("new_dokumen", "Buat Dokumen", "#9b59b6", "file-text"),
    ]

    def __init__(
        self,
        show_title: bool = False,
        title: str = "Aksi Cepat",
        parent: QWidget = None
    ):
        """
        Initialize QuickActionsWidget.

        Args:
            show_title: Whether to show section title
            title: Section title text
            parent: Parent widget
        """
        super().__init__(parent)

        self._show_title = show_title
        self._title = title
        self._buttons: dict = {}

        self._setup_ui()
        self._add_shadow()

    def _setup_ui(self) -> None:
        """Setup widget UI."""
        self.setObjectName("quickActionsWidget")
        self.setStyleSheet("""
            QFrame#quickActionsWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(12)

        # Title (optional)
        if self._show_title:
            title_label = QLabel(self._title)
            title_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            """)
            main_layout.addWidget(title_label)

        # Buttons container
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        # Create action buttons
        for action_id, text, color, icon_name in self.DEFAULT_ACTIONS:
            btn = QuickActionButton(
                text=text,
                action_id=action_id,
                color=color,
                icon_name=icon_name
            )
            btn.clicked.connect(lambda checked, aid=action_id: self.action_clicked.emit(aid))

            self._buttons[action_id] = btn
            buttons_layout.addWidget(btn)

        # Add stretch to push buttons to the left
        buttons_layout.addStretch()

        main_layout.addLayout(buttons_layout)

    def _add_shadow(self) -> None:
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

    def set_button_enabled(self, action_id: str, enabled: bool) -> None:
        """
        Enable or disable a specific button.

        Args:
            action_id: Action identifier
            enabled: True to enable, False to disable
        """
        if action_id in self._buttons:
            self._buttons[action_id].setEnabled(enabled)

    def set_button_visible(self, action_id: str, visible: bool) -> None:
        """
        Show or hide a specific button.

        Args:
            action_id: Action identifier
            visible: True to show, False to hide
        """
        if action_id in self._buttons:
            self._buttons[action_id].setVisible(visible)

    def set_button_text(self, action_id: str, text: str) -> None:
        """
        Change button text.

        Args:
            action_id: Action identifier
            text: New button text
        """
        if action_id in self._buttons:
            self._buttons[action_id].setText(text)

    def get_button(self, action_id: str) -> Optional[QuickActionButton]:
        """
        Get button widget by action ID.

        Args:
            action_id: Action identifier

        Returns:
            QuickActionButton or None if not found
        """
        return self._buttons.get(action_id)

    def add_custom_action(
        self,
        action_id: str,
        text: str,
        color: str = "#34495e",
        icon_name: str = None,
        position: int = -1
    ) -> QuickActionButton:
        """
        Add a custom action button.

        Args:
            action_id: Unique identifier for this action
            text: Button text
            color: Button color (hex)
            icon_name: Icon name from IconProvider
            position: Position in layout (-1 for end)

        Returns:
            Created QuickActionButton
        """
        btn = QuickActionButton(
            text=text,
            action_id=action_id,
            color=color,
            icon_name=icon_name
        )
        btn.clicked.connect(lambda: self.action_clicked.emit(action_id))

        self._buttons[action_id] = btn

        # Get the buttons layout (first layout in main layout if no title, second if has title)
        main_layout = self.layout()
        buttons_layout = None

        for i in range(main_layout.count()):
            item = main_layout.itemAt(i)
            if item.layout() is not None:
                buttons_layout = item.layout()
                break

        if buttons_layout:
            # Remove stretch first
            stretch_item = buttons_layout.takeAt(buttons_layout.count() - 1)

            # Add button at position
            if position < 0 or position >= buttons_layout.count():
                buttons_layout.addWidget(btn)
            else:
                buttons_layout.insertWidget(position, btn)

            # Re-add stretch
            buttons_layout.addStretch()

        return btn

    def remove_action(self, action_id: str) -> bool:
        """
        Remove an action button.

        Args:
            action_id: Action identifier to remove

        Returns:
            True if removed successfully, False if not found
        """
        if action_id not in self._buttons:
            return False

        btn = self._buttons.pop(action_id)
        btn.setParent(None)
        btn.deleteLater()
        return True

    def set_title(self, title: str) -> None:
        """
        Set section title.

        Args:
            title: New title text
        """
        self._title = title
        # Find and update title label if exists
        main_layout = self.layout()
        if main_layout and main_layout.count() > 0:
            first_item = main_layout.itemAt(0)
            if first_item and first_item.widget():
                widget = first_item.widget()
                if isinstance(widget, QLabel):
                    widget.setText(title)

    def set_title_visible(self, visible: bool) -> None:
        """
        Show or hide section title.

        Args:
            visible: True to show, False to hide
        """
        main_layout = self.layout()
        if main_layout and main_layout.count() > 0:
            first_item = main_layout.itemAt(0)
            if first_item and first_item.widget():
                widget = first_item.widget()
                if isinstance(widget, QLabel):
                    widget.setVisible(visible)
