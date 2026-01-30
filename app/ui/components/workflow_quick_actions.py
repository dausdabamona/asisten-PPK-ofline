"""
PPK DOCUMENT FACTORY - Workflow Quick Actions Component
========================================================
Quick actions widget untuk aksi cepat workflow.

Features:
- QuickAction: Data class for action definition
- QuickActionButton: Styled action button with states
- WorkflowQuickActionsWidget: Context-aware quick actions container
- Batch actions support

Author: PPK Document Factory Team
Version: 4.0
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable, Set
from enum import Enum

from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMenu, QSizePolicy, QGraphicsDropShadowEffect,
    QSpacerItem, QToolButton
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QColor, QFont, QCursor, QKeySequence, QShortcut, QAction


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

class ActionContext(Enum):
    """Context types for quick actions."""
    DASHBOARD = "dashboard"
    TRANSAKSI_LIST = "transaksi_list"
    TRANSAKSI_DETAIL = "transaksi_detail"
    KANBAN = "kanban"
    BATCH = "batch"


# Default action icons
ACTION_ICONS = {
    "new_up": "+",
    "new_tup": "+",
    "new_ls": "+",
    "next_fase": "\u27A1\uFE0F",
    "prev_fase": "\u2B05\uFE0F",
    "generate_docs": "\U0001F4C4",
    "upload": "\U0001F4CE",
    "delete": "\U0001F5D1\uFE0F",
    "edit": "\u270F\uFE0F",
    "view": "\U0001F441\uFE0F",
    "refresh": "\U0001F504",
    "batch_move": "\U0001F4E6",
    "batch_export": "\U0001F4E4",
    "print": "\U0001F5A8\uFE0F",
}

# Action button colors by type
ACTION_COLORS = {
    "primary": {"bg": "#2196f3", "hover": "#1976d2", "text": "#ffffff"},
    "success": {"bg": "#4caf50", "hover": "#388e3c", "text": "#ffffff"},
    "warning": {"bg": "#ff9800", "hover": "#f57c00", "text": "#ffffff"},
    "danger": {"bg": "#f44336", "hover": "#d32f2f", "text": "#ffffff"},
    "secondary": {"bg": "#607d8b", "hover": "#455a64", "text": "#ffffff"},
    "outline": {"bg": "transparent", "hover": "#f5f5f5", "text": "#424242"},
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class QuickAction:
    """
    Data class representing a quick action.

    Attributes:
        id: Unique action identifier
        label: Display label
        icon: Icon character/emoji
        action: Callable to execute
        shortcut: Keyboard shortcut (optional)
        enabled_condition: Callable returning bool for enabled state
        color_type: Button color type (primary, success, etc.)
        tooltip: Tooltip text
        requires_selection: Whether action needs selected items
        batch_capable: Whether action can work with multiple items
    """
    id: str
    label: str
    icon: str = ""
    action: Optional[Callable] = None
    shortcut: Optional[str] = None
    enabled_condition: Optional[Callable[[], bool]] = None
    color_type: str = "primary"
    tooltip: Optional[str] = None
    requires_selection: bool = False
    batch_capable: bool = False
    disabled_reason: Optional[str] = None

    def is_enabled(self) -> bool:
        """Check if action is enabled."""
        if self.enabled_condition:
            return self.enabled_condition()
        return True

    def get_tooltip(self) -> str:
        """Get tooltip with shortcut info."""
        tip = self.tooltip or self.label
        if self.shortcut:
            tip += f" ({self.shortcut})"
        if self.disabled_reason and not self.is_enabled():
            tip += f"\n(Disabled: {self.disabled_reason})"
        return tip


# =============================================================================
# QUICK ACTION BUTTON
# =============================================================================

class QuickActionButton(QPushButton):
    """
    Styled button for quick actions.

    Features:
    - Icon + Label display
    - Tooltip with shortcut
    - Disabled state with reason
    - Loading state while processing

    Signals:
        action_triggered(str): Emit action_id when clicked
    """

    action_triggered = Signal(str)

    def __init__(
        self,
        action: QuickAction,
        compact: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.action = action
        self.compact = compact
        self._loading = False
        self._original_text = ""

        self._setup_ui()
        self._apply_style()
        self._setup_shortcut()

    def _setup_ui(self):
        """Setup button UI."""
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)

        # Set text
        if self.compact:
            self.setText(self.action.icon or self.action.label[:2])
            self.setFixedSize(40, 36)
        else:
            text = f"{self.action.icon} {self.action.label}" if self.action.icon else self.action.label
            self.setText(text)
            self.setMinimumHeight(36)

        self._original_text = self.text()

        # Tooltip
        self.setToolTip(self.action.get_tooltip())

        # Connect click
        self.clicked.connect(self._on_clicked)

        # Update enabled state
        self._update_enabled()

    def _apply_style(self):
        """Apply button styling."""
        colors = ACTION_COLORS.get(self.action.color_type, ACTION_COLORS["primary"])

        self.setStyleSheet(f"""
            QuickActionButton {{
                background-color: {colors['bg']};
                color: {colors['text']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QuickActionButton:hover {{
                background-color: {colors['hover']};
            }}
            QuickActionButton:pressed {{
                background-color: {colors['hover']};
                padding-top: 9px;
                padding-bottom: 7px;
            }}
            QuickActionButton:disabled {{
                background-color: #bdbdbd;
                color: #757575;
            }}
        """)

    def _setup_shortcut(self):
        """Setup keyboard shortcut if defined."""
        if self.action.shortcut:
            # Shortcuts are handled by parent widget
            pass

    def _on_clicked(self):
        """Handle button click."""
        if self._loading:
            return

        self.action_triggered.emit(self.action.id)

        if self.action.action:
            self.action.action()

    def _update_enabled(self):
        """Update enabled state based on condition."""
        enabled = self.action.is_enabled()
        self.setEnabled(enabled)

        if not enabled and self.action.disabled_reason:
            self.setToolTip(f"{self.action.label}\n(Disabled: {self.action.disabled_reason})")
        else:
            self.setToolTip(self.action.get_tooltip())

    def set_loading(self, loading: bool):
        """Set loading state."""
        self._loading = loading

        if loading:
            self.setText("\u23F3")  # Hourglass
            self.setEnabled(False)
        else:
            self.setText(self._original_text)
            self._update_enabled()

    def refresh_state(self):
        """Refresh enabled state."""
        self._update_enabled()

    def update_action(self, action: QuickAction):
        """Update the action definition."""
        self.action = action
        self._setup_ui()
        self._apply_style()


# =============================================================================
# WORKFLOW QUICK ACTIONS WIDGET
# =============================================================================

class WorkflowQuickActionsWidget(QWidget):
    """
    Context-aware quick actions container.

    Features:
    - Changes actions based on current context
    - Supports dashboard, list, detail, and kanban contexts
    - Batch action support for multiple selections

    Signals:
        action_executed(str, dict): Emit action_id and context data
        batch_action_executed(str, list): Emit action_id and selected items
    """

    action_executed = Signal(str, dict)
    batch_action_executed = Signal(str, list)

    def __init__(
        self,
        context: str = "dashboard",
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self._context = context
        self._context_data: Dict[str, Any] = {}
        self._actions: Dict[str, QuickAction] = {}
        self._buttons: Dict[str, QuickActionButton] = {}
        self._selected_items: List[str] = []
        self._shortcuts: List[QShortcut] = []

        self._setup_ui()
        self._setup_default_actions()

    def _setup_ui(self):
        """Setup widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main container
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(12, 10, 12, 10)
        container_layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.icon_label = QLabel("\u26A1")  # Lightning
        self.icon_label.setFont(QFont("Segoe UI", 14))
        header_layout.addWidget(self.icon_label)

        self.title_label = QLabel("Quick Actions")
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.title_label.setStyleSheet("color: #212121;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Selection count (for batch mode)
        self.selection_label = QLabel()
        self.selection_label.setFont(QFont("Segoe UI", 9))
        self.selection_label.setStyleSheet("color: #757575;")
        self.selection_label.setVisible(False)
        header_layout.addWidget(self.selection_label)

        container_layout.addLayout(header_layout)

        # Actions container
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(8)
        container_layout.addLayout(self.actions_layout)

        layout.addWidget(self.container)

    def _setup_default_actions(self):
        """Setup default actions based on context."""
        self._clear_actions()

        if self._context == "dashboard":
            self._setup_dashboard_actions()
        elif self._context == "transaksi_detail":
            self._setup_detail_actions()
        elif self._context == "kanban":
            self._setup_kanban_actions()
        elif self._context == "batch":
            self._setup_batch_actions()

    def _setup_dashboard_actions(self):
        """Setup dashboard quick actions."""
        actions = [
            QuickAction(
                id="new_up",
                label="UP Baru",
                icon="+",
                color_type="success",
                shortcut="Ctrl+U",
                tooltip="Buat transaksi UP baru"
            ),
            QuickAction(
                id="new_tup",
                label="TUP Baru",
                icon="+",
                color_type="warning",
                shortcut="Ctrl+T",
                tooltip="Buat transaksi TUP baru"
            ),
            QuickAction(
                id="new_ls",
                label="LS Baru",
                icon="+",
                color_type="primary",
                shortcut="Ctrl+L",
                tooltip="Buat transaksi LS baru"
            ),
            QuickAction(
                id="batch_docs",
                label="Batch Docs",
                icon="\U0001F4C4",
                color_type="secondary",
                tooltip="Generate dokumen batch"
            ),
        ]

        for action in actions:
            self.add_action(action)

        self.title_label.setText("Quick Actions")

    def _setup_detail_actions(self):
        """Setup transaksi detail quick actions."""
        transaksi_id = self._context_data.get("transaksi_id", "")
        nomor = self._context_data.get("nomor", "")

        actions = [
            QuickAction(
                id="next_fase",
                label="Next Fase",
                icon="\u27A1\uFE0F",
                color_type="success",
                shortcut="Ctrl+Right",
                tooltip="Pindah ke fase berikutnya"
            ),
            QuickAction(
                id="generate_docs",
                label="Generate Docs",
                icon="\U0001F4C4",
                color_type="primary",
                tooltip="Generate dokumen untuk transaksi ini"
            ),
            QuickAction(
                id="upload",
                label="Upload",
                icon="\U0001F4CE",
                color_type="secondary",
                tooltip="Upload dokumen"
            ),
            QuickAction(
                id="delete",
                label="Hapus",
                icon="\U0001F5D1\uFE0F",
                color_type="danger",
                tooltip="Hapus transaksi",
                shortcut="Delete"
            ),
        ]

        for action in actions:
            self.add_action(action)

        self.title_label.setText(f"Quick Actions - {nomor}" if nomor else "Quick Actions")

    def _setup_kanban_actions(self):
        """Setup kanban view quick actions."""
        actions = [
            QuickAction(
                id="new_transaksi",
                label="Transaksi Baru",
                icon="+",
                color_type="success",
                shortcut="N",
                tooltip="Buat transaksi baru"
            ),
            QuickAction(
                id="refresh",
                label="Refresh",
                icon="\U0001F504",
                color_type="outline",
                shortcut="R",
                tooltip="Refresh kanban board"
            ),
        ]

        for action in actions:
            self.add_action(action)

    def _setup_batch_actions(self):
        """Setup batch action buttons."""
        count = len(self._selected_items)

        actions = [
            QuickAction(
                id="batch_move",
                label=f"Pindahkan ({count})",
                icon="\U0001F4E6",
                color_type="primary",
                batch_capable=True,
                tooltip="Pindahkan transaksi terpilih ke fase lain"
            ),
            QuickAction(
                id="batch_generate",
                label=f"Generate Docs ({count})",
                icon="\U0001F4C4",
                color_type="secondary",
                batch_capable=True,
                tooltip="Generate dokumen untuk transaksi terpilih"
            ),
            QuickAction(
                id="batch_export",
                label=f"Export ({count})",
                icon="\U0001F4E4",
                color_type="outline",
                batch_capable=True,
                tooltip="Export data transaksi terpilih"
            ),
            QuickAction(
                id="clear_selection",
                label="Batal",
                icon="\u2715",
                color_type="outline",
                tooltip="Batalkan seleksi"
            ),
        ]

        for action in actions:
            self.add_action(action)

        self.selection_label.setText(f"{count} dipilih")
        self.selection_label.setVisible(True)
        self.title_label.setText("Batch Actions")

    def _clear_actions(self):
        """Clear all current actions."""
        # Remove buttons
        for button in self._buttons.values():
            self.actions_layout.removeWidget(button)
            button.deleteLater()

        self._buttons.clear()
        self._actions.clear()

        # Clear shortcuts
        for shortcut in self._shortcuts:
            shortcut.deleteLater()
        self._shortcuts.clear()

        # Remove stretch if exists
        while self.actions_layout.count():
            item = self.actions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _create_button(self, action: QuickAction) -> QuickActionButton:
        """Create a button for an action."""
        button = QuickActionButton(action)
        button.action_triggered.connect(self._on_action_triggered)
        return button

    def _on_action_triggered(self, action_id: str):
        """Handle action button click."""
        action = self._actions.get(action_id)
        if not action:
            return

        if action.batch_capable and self._selected_items:
            self.batch_action_executed.emit(action_id, self._selected_items.copy())
        else:
            self.action_executed.emit(action_id, self._context_data.copy())

    # -------------------------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------------------------

    def set_context(self, context: str, data: Optional[Dict[str, Any]] = None):
        """
        Set the current context and update actions.

        Args:
            context: Context type (dashboard, transaksi_detail, kanban, batch)
            data: Context-specific data
        """
        self._context = context
        self._context_data = data or {}

        if context != "batch":
            self._selected_items.clear()
            self.selection_label.setVisible(False)

        self._setup_default_actions()

    def add_action(self, action: QuickAction):
        """Add a quick action."""
        self._actions[action.id] = action
        button = self._create_button(action)
        self._buttons[action.id] = button
        self.actions_layout.addWidget(button)

        # Setup shortcut
        if action.shortcut:
            shortcut = QShortcut(QKeySequence(action.shortcut), self)
            shortcut.activated.connect(lambda aid=action.id: self._on_action_triggered(aid))
            self._shortcuts.append(shortcut)

    def remove_action(self, action_id: str):
        """Remove a quick action."""
        if action_id in self._buttons:
            button = self._buttons.pop(action_id)
            self.actions_layout.removeWidget(button)
            button.deleteLater()

        self._actions.pop(action_id, None)

    def enable_action(self, action_id: str, enabled: bool, reason: Optional[str] = None):
        """Enable or disable an action."""
        if action_id in self._actions:
            action = self._actions[action_id]
            action.enabled_condition = lambda e=enabled: e
            action.disabled_reason = reason if not enabled else None

        if action_id in self._buttons:
            self._buttons[action_id].refresh_state()

    def execute_action(self, action_id: str):
        """Programmatically execute an action."""
        if action_id in self._actions:
            action = self._actions[action_id]
            if action.is_enabled():
                self._on_action_triggered(action_id)

    def set_selected_items(self, items: List[str]):
        """Set selected items for batch actions."""
        self._selected_items = items.copy()

        if items:
            self.set_context("batch")
        elif self._context == "batch":
            self.set_context("dashboard")

    def add_selected_item(self, item_id: str):
        """Add an item to selection."""
        if item_id not in self._selected_items:
            self._selected_items.append(item_id)
            self.set_context("batch")

    def remove_selected_item(self, item_id: str):
        """Remove an item from selection."""
        if item_id in self._selected_items:
            self._selected_items.remove(item_id)
            if not self._selected_items:
                self.set_context("dashboard")
            else:
                self.set_context("batch")

    def clear_selection(self):
        """Clear all selected items."""
        self._selected_items.clear()
        self.set_context("dashboard")

    def get_selected_items(self) -> List[str]:
        """Get currently selected items."""
        return self._selected_items.copy()

    def set_action_loading(self, action_id: str, loading: bool):
        """Set loading state for an action button."""
        if action_id in self._buttons:
            self._buttons[action_id].set_loading(loading)

    def refresh_states(self):
        """Refresh all action states."""
        for button in self._buttons.values():
            button.refresh_state()

    def get_action(self, action_id: str) -> Optional[QuickAction]:
        """Get action by ID."""
        return self._actions.get(action_id)


# =============================================================================
# CONTEXT MENU BUILDER
# =============================================================================

class WorkflowContextMenu(QMenu):
    """
    Context menu for workflow items (Kanban cards, list items, etc.).

    Signals:
        action_selected(str, str): Emit action_id and item_id
    """

    action_selected = Signal(str, str)

    def __init__(
        self,
        item_id: str,
        item_data: Optional[Dict[str, Any]] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.item_id = item_id
        self.item_data = item_data or {}

        self._setup_menu()
        self._apply_style()

    def _setup_menu(self):
        """Setup context menu items."""
        fase = self.item_data.get("fase", 1)

        # View action
        view_action = self.addAction("\U0001F441\uFE0F Lihat Detail")
        view_action.triggered.connect(lambda: self.action_selected.emit("view", self.item_id))

        # Edit action
        edit_action = self.addAction("\u270F\uFE0F Edit")
        edit_action.triggered.connect(lambda: self.action_selected.emit("edit", self.item_id))

        self.addSeparator()

        # Move to fase submenu
        move_menu = self.addMenu("\U0001F4E6 Pindah ke...")
        for target_fase in range(1, 6):
            if target_fase != fase:
                fase_action = move_menu.addAction(f"Fase {target_fase}")
                fase_action.triggered.connect(
                    lambda checked, f=target_fase: self.action_selected.emit(f"move_to_{f}", self.item_id)
                )

        # Generate docs submenu
        docs_menu = self.addMenu("\U0001F4C4 Buat Dokumen...")
        docs = ["KAK", "Kuitansi", "SPJ", "BAST"]
        for doc in docs:
            doc_action = docs_menu.addAction(doc)
            doc_action.triggered.connect(
                lambda checked, d=doc: self.action_selected.emit(f"generate_{d.lower()}", self.item_id)
            )

        self.addSeparator()

        # Upload action
        upload_action = self.addAction("\U0001F4CE Upload Dokumen")
        upload_action.triggered.connect(lambda: self.action_selected.emit("upload", self.item_id))

        # Print action
        print_action = self.addAction("\U0001F5A8\uFE0F Cetak")
        print_action.triggered.connect(lambda: self.action_selected.emit("print", self.item_id))

        self.addSeparator()

        # Delete action
        delete_action = self.addAction("\U0001F5D1\uFE0F Hapus")
        delete_action.triggered.connect(lambda: self.action_selected.emit("delete", self.item_id))

    def _apply_style(self):
        """Apply menu styling."""
        self.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px 8px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e0e0e0;
                margin: 4px 8px;
            }
            QMenu::icon {
                padding-left: 8px;
            }
        """)


# =============================================================================
# COMPACT QUICK ACTIONS
# =============================================================================

class CompactQuickActions(QFrame):
    """
    Compact quick actions for toolbar or header.

    Shows icon-only buttons in a horizontal row.
    """

    action_executed = Signal(str)

    def __init__(
        self,
        actions: Optional[List[QuickAction]] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self._actions: Dict[str, QuickAction] = {}
        self._buttons: Dict[str, QuickActionButton] = {}

        self._setup_ui()

        if actions:
            for action in actions:
                self.add_action(action)

    def _setup_ui(self):
        """Setup compact UI."""
        self.setStyleSheet("""
            CompactQuickActions {
                background-color: transparent;
                border: none;
            }
        """)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)

    def add_action(self, action: QuickAction):
        """Add a compact action button."""
        self._actions[action.id] = action

        button = QuickActionButton(action, compact=True)
        button.action_triggered.connect(self.action_executed.emit)

        self._buttons[action.id] = button
        self.layout.addWidget(button)

    def remove_action(self, action_id: str):
        """Remove an action."""
        if action_id in self._buttons:
            button = self._buttons.pop(action_id)
            self.layout.removeWidget(button)
            button.deleteLater()
        self._actions.pop(action_id, None)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_quick_actions(
    context: str = "dashboard",
    context_data: Optional[Dict[str, Any]] = None,
    parent: Optional[QWidget] = None
) -> WorkflowQuickActionsWidget:
    """
    Factory function to create WorkflowQuickActionsWidget.

    Args:
        context: Initial context (dashboard, transaksi_detail, kanban, batch)
        context_data: Context-specific data
        parent: Parent widget

    Returns:
        Configured WorkflowQuickActionsWidget instance
    """
    widget = WorkflowQuickActionsWidget(context=context, parent=parent)

    if context_data:
        widget.set_context(context, context_data)

    return widget


def create_context_menu(
    item_id: str,
    item_data: Optional[Dict[str, Any]] = None,
    parent: Optional[QWidget] = None
) -> WorkflowContextMenu:
    """
    Factory function to create WorkflowContextMenu.

    Args:
        item_id: ID of the item
        item_data: Item data dictionary
        parent: Parent widget

    Returns:
        Configured WorkflowContextMenu instance
    """
    return WorkflowContextMenu(item_id=item_id, item_data=item_data, parent=parent)
