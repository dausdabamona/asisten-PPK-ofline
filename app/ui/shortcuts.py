"""
PPK DOCUMENT FACTORY - Keyboard Shortcuts System
=================================================
Centralized keyboard shortcut management dengan:
- Singleton pattern
- Context-based shortcuts
- Help dialog
- Default shortcuts for common actions

Author: PPK Document Factory Team
Version: 4.0
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Callable, Any
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QShortcut, QKeySequence, QColor


# =============================================================================
# SHORTCUT INFO
# =============================================================================

@dataclass
class ShortcutInfo:
    """Information about a registered shortcut."""
    key_sequence: str
    description: str
    context: str = "global"
    enabled: bool = True
    callback: Optional[Callable] = field(default=None, repr=False)
    shortcut: Optional[QShortcut] = field(default=None, repr=False)


# =============================================================================
# SHORTCUT CONTEXT
# =============================================================================

class ShortcutContext(Enum):
    """Predefined shortcut contexts."""
    GLOBAL = "global"
    NAVIGATION = "navigation"
    FORM = "form"
    TABLE = "table"
    DIALOG = "dialog"


# =============================================================================
# SHORTCUT MANAGER
# =============================================================================

class ShortcutManager(QObject):
    """
    Singleton manager for keyboard shortcuts.

    Features:
    - Register/unregister shortcuts
    - Context-based enable/disable
    - Help dialog
    - Default shortcuts

    Usage:
        # Get instance
        manager = ShortcutManager.instance()

        # In MainWindow
        manager.set_parent(self)
        manager.register("Ctrl+N", self._new_transaction, "Transaksi Baru")

        # Show help
        manager.show_help_dialog(self)
    """

    _instance: Optional['ShortcutManager'] = None
    _shortcuts: Dict[str, ShortcutInfo] = {}
    _current_context: str = "global"
    _parent: Optional[QWidget] = None

    # Signal emitted when shortcut is triggered
    shortcut_triggered = Signal(str)  # key_sequence

    def __new__(cls, parent: Optional[QWidget] = None):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize shortcut manager."""
        if self._initialized:
            if parent is not None:
                self.set_parent(parent)
            return

        super().__init__(parent)
        self._initialized = True
        self._shortcuts = {}
        self._current_context = "global"
        self._parent = parent

        # Register default shortcuts if parent is provided
        if parent is not None:
            self._register_defaults()

    @classmethod
    def instance(cls) -> 'ShortcutManager':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_parent(self, parent: QWidget) -> None:
        """
        Set parent widget for shortcuts.

        Args:
            parent: Parent widget (usually MainWindow)
        """
        self._parent = parent
        self.setParent(parent)

        # Re-register all shortcuts with new parent
        for key, info in self._shortcuts.items():
            if info.callback:
                self._create_shortcut(key, info)

    def register(
        self,
        key_sequence: str,
        callback: Optional[Callable] = None,
        description: str = "",
        context: str = "global",
        enabled: bool = True
    ) -> None:
        """
        Register a keyboard shortcut.

        Args:
            key_sequence: Key sequence (e.g., "Ctrl+N", "F5")
            callback: Callback function to execute
            description: Human-readable description
            context: Context for the shortcut
            enabled: Whether shortcut is enabled
        """
        info = ShortcutInfo(
            key_sequence=key_sequence,
            description=description,
            context=context,
            enabled=enabled,
            callback=callback
        )

        # Create Qt shortcut if parent exists
        if self._parent and callback:
            self._create_shortcut(key_sequence, info)

        self._shortcuts[key_sequence] = info

    def _create_shortcut(self, key_sequence: str, info: ShortcutInfo) -> None:
        """Create Qt shortcut object."""
        if not self._parent:
            return

        # Remove existing shortcut if any
        if info.shortcut:
            info.shortcut.deleteLater()

        shortcut = QShortcut(QKeySequence(key_sequence), self._parent)
        shortcut.activated.connect(lambda: self._on_shortcut_triggered(key_sequence))
        shortcut.setEnabled(info.enabled)
        info.shortcut = shortcut

    def _on_shortcut_triggered(self, key_sequence: str) -> None:
        """Handle shortcut triggered."""
        info = self._shortcuts.get(key_sequence)
        if not info or not info.enabled:
            return

        # Check context
        if info.context != "global" and info.context != self._current_context:
            return

        # Emit signal
        self.shortcut_triggered.emit(key_sequence)

        # Execute callback
        if info.callback:
            info.callback()

    def unregister(self, key_sequence: str) -> None:
        """
        Unregister a keyboard shortcut.

        Args:
            key_sequence: Key sequence to unregister
        """
        if key_sequence in self._shortcuts:
            info = self._shortcuts[key_sequence]
            if info.shortcut:
                info.shortcut.deleteLater()
            del self._shortcuts[key_sequence]

    def set_context(self, context: str) -> None:
        """
        Set current shortcut context.

        Only shortcuts matching this context (or global) will be active.

        Args:
            context: Context name
        """
        self._current_context = context

    def get_context(self) -> str:
        """Get current context."""
        return self._current_context

    def enable(self, key_sequence: str) -> None:
        """Enable a shortcut."""
        if key_sequence in self._shortcuts:
            self._shortcuts[key_sequence].enabled = True
            if self._shortcuts[key_sequence].shortcut:
                self._shortcuts[key_sequence].shortcut.setEnabled(True)

    def disable(self, key_sequence: str) -> None:
        """Disable a shortcut."""
        if key_sequence in self._shortcuts:
            self._shortcuts[key_sequence].enabled = False
            if self._shortcuts[key_sequence].shortcut:
                self._shortcuts[key_sequence].shortcut.setEnabled(False)

    def get_all_shortcuts(self) -> List[ShortcutInfo]:
        """
        Get all registered shortcuts.

        Returns:
            List of ShortcutInfo objects
        """
        return list(self._shortcuts.values())

    def get_shortcuts_by_context(self, context: str) -> List[ShortcutInfo]:
        """
        Get shortcuts for a specific context.

        Args:
            context: Context name

        Returns:
            List of ShortcutInfo objects
        """
        return [
            info for info in self._shortcuts.values()
            if info.context == context
        ]

    def show_help_dialog(self, parent: Optional[QWidget] = None) -> None:
        """
        Show keyboard shortcuts help dialog.

        Args:
            parent: Parent widget for dialog
        """
        dialog = ShortcutHelpDialog(self, parent or self._parent)
        dialog.exec()

    def _register_defaults(self) -> None:
        """Register default shortcuts."""
        # Global shortcuts
        self.register("Ctrl+N", None, "Transaksi Baru", "global")
        self.register("Ctrl+S", None, "Simpan", "global")
        self.register("Ctrl+P", None, "Print", "global")
        self.register("Ctrl+F", None, "Cari", "global")
        self.register("Ctrl+Q", None, "Keluar", "global")
        self.register("F1", lambda: self.show_help_dialog(), "Bantuan", "global")
        self.register("F5", None, "Refresh", "global")

        # Navigation shortcuts
        self.register("Ctrl+1", None, "Dashboard", "navigation")
        self.register("Ctrl+2", None, "UP", "navigation")
        self.register("Ctrl+3", None, "TUP", "navigation")
        self.register("Ctrl+4", None, "LS", "navigation")
        self.register("Alt+Left", None, "Kembali", "navigation")

        # Form shortcuts
        self.register("Ctrl+Return", None, "Submit Form", "form")
        self.register("Escape", None, "Cancel/Close", "form")

    def clear_all(self) -> None:
        """Clear all registered shortcuts."""
        for key, info in self._shortcuts.items():
            if info.shortcut:
                info.shortcut.deleteLater()
        self._shortcuts.clear()


# =============================================================================
# SHORTCUT HELP DIALOG
# =============================================================================

class ShortcutHelpDialog(QDialog):
    """
    Dialog showing all registered keyboard shortcuts.

    Features:
    - Grouped by context
    - Searchable
    - Modern styling
    """

    def __init__(
        self,
        manager: ShortcutManager,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize help dialog.

        Args:
            manager: ShortcutManager instance
            parent: Parent widget
        """
        super().__init__(parent)

        self._manager = manager
        self._search_text = ""

        self._setup_ui()
        self._apply_shadow()

    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        # Window settings
        self.setWindowTitle("Keyboard Shortcuts")
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.setMaximumSize(600, 600)

        # Main container
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        container.setStyleSheet("""
            QFrame#dialogContainer {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        # Container layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("Keyboard Shortcuts")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Close button
        close_btn = QPushButton("\u00D7")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton#closeBtn {
                background-color: transparent;
                color: #7f8c8d;
                border: none;
                font-size: 20px;
                font-weight: bold;
                border-radius: 16px;
            }
            QPushButton#closeBtn:hover {
                background-color: #ecf0f1;
            }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # Search box
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Cari shortcut...")
        self._search_input.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #ffffff;
            }
        """)
        self._search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_input)

        # Scroll area for shortcuts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        self._shortcuts_widget = QWidget()
        self._shortcuts_layout = QVBoxLayout(self._shortcuts_widget)
        self._shortcuts_layout.setContentsMargins(0, 0, 0, 0)
        self._shortcuts_layout.setSpacing(16)

        scroll.setWidget(self._shortcuts_widget)
        layout.addWidget(scroll)

        # Populate shortcuts
        self._populate_shortcuts()

    def _populate_shortcuts(self) -> None:
        """Populate shortcuts list."""
        # Clear existing
        while self._shortcuts_layout.count():
            child = self._shortcuts_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Group by context
        contexts = {}
        for info in self._manager.get_all_shortcuts():
            # Filter by search
            if self._search_text:
                search_lower = self._search_text.lower()
                if (search_lower not in info.key_sequence.lower() and
                    search_lower not in info.description.lower()):
                    continue

            if info.context not in contexts:
                contexts[info.context] = []
            contexts[info.context].append(info)

        # Context display names
        context_names = {
            "global": "Global",
            "navigation": "Navigasi",
            "form": "Form",
            "table": "Tabel",
            "dialog": "Dialog",
        }

        # Add sections
        for context, shortcuts in sorted(contexts.items()):
            if not shortcuts:
                continue

            # Section header
            section_label = QLabel(context_names.get(context, context.title()))
            section_label.setStyleSheet("""
                QLabel {
                    color: #7f8c8d;
                    font-size: 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
            """)
            self._shortcuts_layout.addWidget(section_label)

            # Shortcuts in section
            for info in sorted(shortcuts, key=lambda x: x.key_sequence):
                row = self._create_shortcut_row(info)
                self._shortcuts_layout.addWidget(row)

        self._shortcuts_layout.addStretch()

    def _create_shortcut_row(self, info: ShortcutInfo) -> QWidget:
        """Create a shortcut row widget."""
        row = QFrame()
        row.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 6px;
                padding: 4px;
            }
        """)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 8, 12, 8)

        # Description
        desc_label = QLabel(info.description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
        """)
        layout.addWidget(desc_label)
        layout.addStretch()

        # Key sequence badge
        key_label = QLabel(info.key_sequence)
        key_label.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                color: #3498db;
                font-size: 12px;
                font-weight: bold;
                font-family: monospace;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #e9ecef;
            }
        """)
        layout.addWidget(key_label)

        return row

    def _on_search_changed(self, text: str) -> None:
        """Handle search text changed."""
        self._search_text = text
        self._populate_shortcuts()

    def _apply_shadow(self) -> None:
        """Apply drop shadow effect."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_shortcut_manager() -> ShortcutManager:
    """Get the singleton ShortcutManager instance."""
    return ShortcutManager.instance()


def register_shortcut(
    key_sequence: str,
    callback: Optional[Callable] = None,
    description: str = "",
    context: str = "global"
) -> None:
    """
    Register a keyboard shortcut.

    Args:
        key_sequence: Key sequence (e.g., "Ctrl+N")
        callback: Callback function
        description: Human-readable description
        context: Context for the shortcut
    """
    get_shortcut_manager().register(key_sequence, callback, description, context)
