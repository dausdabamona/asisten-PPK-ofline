"""
PPK Document Factory - UI Components
=====================================
Reusable UI components for the PPK Document Factory application.

Components Overview:
-------------------

**Notifications & Feedback:**
- Toast, ToastManager - Toast notification system
- LoadingOverlay, SpinnerWidget, LoadingMixin - Loading indicators
- EmptyState - Empty state displays

**Input Components:**
- ValidatedLineEdit, ValidatedSpinBox, ValidatedComboBox, etc. - Validated inputs
- FormGroup, FormSection, FormBuilder - Form building components
- SearchBar, AdvancedSearchBar - Search components

**Navigation:**
- Sidebar - Application sidebar navigation
- Breadcrumb, BreadcrumbItem - Breadcrumb navigation

**Dialogs:**
- ConfirmDialog - Confirmation dialogs (confirm, warning, danger, info)
- InputDialog - Input dialogs (text, number, date, combo)

**Status & Badges:**
- StatusBadge - Generic status badges
- MekanismeBadge - UP/TUP/LS badges
- FaseBadge - Workflow phase badges
- PriorityBadge - Priority level badges

**Kanban Board:**
- KanbanCard - Draggable transaction card
- KanbanColumn - Phase column with drop target
- KanbanBoard - Full kanban board with filters

**Workflow Components:**
- FaseStepper - Workflow phase stepper
- StageWidget - Stage display widget
- DokumenChecklist - Document checklist
- CountdownWidget - Countdown timer

**Dashboard Components:**
- StatisticsSection, SaldoUPWidget - Dashboard statistics
- QuickActionsWidget - Quick action buttons
- RecentActivityWidget - Recent activity list

**Calculation Widgets:**
- KalkulasiWidget - Calculation display
- RincianKalkulasiWidget - Detailed calculation

Note: Dashboard components are available here for convenience but the
canonical source is app.ui.dashboard_components module.

Usage Examples:
--------------
```python
# Toast notifications
from app.ui.components import ToastManager
ToastManager.success("Data berhasil disimpan!", parent=self)
ToastManager.error("Terjadi kesalahan!", parent=self)

# Loading overlay
from app.ui.components import LoadingMixin
class MyWidget(QWidget, LoadingMixin):
    def load_data(self):
        self.show_loading("Memuat data...")
        try:
            # do work
        finally:
            self.hide_loading()

# Confirmation dialog
from app.ui.components import ConfirmDialog
if ConfirmDialog.danger("Hapus?", "Data akan dihapus permanen", self):
    self.delete_item()

# Search bar
from app.ui.components import SearchBar
search = SearchBar(placeholder="Cari...")
search.add_filter("status", ["Semua", "Aktif", "Selesai"])
search.search_changed.connect(self.filter_data)

# Status badges
from app.ui.components import StatusBadge, MekanismeBadge
badge = StatusBadge("Selesai", "completed")
mek_badge = MekanismeBadge("UP")

# Kanban board
from app.ui.components import KanbanBoard, create_kanban_board
board = create_kanban_board(mekanisme="UP")
board.set_data([
    {"id": "1", "nomor": "001", "nama": "Transaksi A", "nilai": 50000000,
     "status": "Aktif", "mekanisme": "UP", "fase": 1},
])
board.transaksi_selected.connect(self.open_detail)
board.transaksi_moved.connect(self.handle_move)
```
"""

# =============================================================================
# SIDEBAR & NAVIGATION
# =============================================================================

from .sidebar import Sidebar
from .breadcrumb import (
    Breadcrumb,
    BreadcrumbItem,
    create_breadcrumb,
)

# =============================================================================
# LEGACY DASHBOARD CARDS (backward compatibility)
# =============================================================================

from .dashboard_cards import (
    MekanismeCard,
    TransaksiAktifCard,
    SaldoUPWidget as SaldoUPWidgetLegacy,
    QuickActionBar,
)

# =============================================================================
# NEW MODULAR DASHBOARD COMPONENTS
# =============================================================================

from app.ui.dashboard_components import (
    StatisticsSection,
    MekanismeStatCard,
    SaldoUPWidget,
    QuickActionsWidget,
    QuickActionButton,
    RecentActivityWidget,
    TransactionItemWidget,
)

# =============================================================================
# KANBAN BOARD
# =============================================================================

from .kanban_board import (
    KanbanCard,
    KanbanColumn,
    KanbanBoard,
    Mekanisme,
    Urgency,
    MEKANISME_COLORS,
    URGENCY_COLORS,
    FASE_CONFIG,
    create_kanban_board,
)

# =============================================================================
# WORKFLOW COMPONENTS
# =============================================================================

from .fase_stepper import FaseStepper
from .stage_widget import StageWidget
from .dokumen_checklist import DokumenChecklist
from .countdown_widget import CountdownWidget

# =============================================================================
# CALCULATION WIDGETS
# =============================================================================

from .kalkulasi_widget import KalkulasiWidget
from .rincian_kalkulasi_widget import RincianKalkulasiWidget

# =============================================================================
# TOAST NOTIFICATIONS
# =============================================================================

from .toast import (
    Toast,
    ToastType,
    ToastContainer,
    ToastManager,
    show_toast,
    toast_success,
    toast_error,
    toast_warning,
    toast_info,
)

# =============================================================================
# LOADING OVERLAY
# =============================================================================

from .loading_overlay import (
    SpinnerWidget,
    LoadingOverlay,
    LoadingMixin,
    LoadingDots,
)

# =============================================================================
# EMPTY STATE
# =============================================================================

from .empty_state import EmptyState

# =============================================================================
# VALIDATED INPUTS
# =============================================================================

from .validated_inputs import (
    # Input widgets
    ValidatedLineEdit,
    ValidatedSpinBox,
    ValidatedCurrencySpinBox,
    ValidatedComboBox,
    ValidatedDateEdit,
    ValidatedTextEdit,
    # Validators
    required,
    min_length,
    max_length,
    email,
    numeric,
    rupiah_range,
    regex,
    date_range,
)

# =============================================================================
# FORM GROUPS
# =============================================================================

from .form_group import (
    FormGroup,
    FormSection,
    FormBuilder,
    BuiltForm,
)

# =============================================================================
# DIALOGS
# =============================================================================

from .confirm_dialog import (
    ConfirmDialog,
    DialogType,
    InputDialog,
    InputType,
)

# =============================================================================
# SEARCH BAR
# =============================================================================

from .search_bar import (
    SearchBar,
    AdvancedSearchBar,
    create_search_bar,
)

# =============================================================================
# STATUS BADGES
# =============================================================================

from .status_badge import (
    StatusBadge,
    StatusType,
    MekanismeBadge,
    FaseBadge,
    FaseStatus,
    PriorityBadge,
    create_status_badge,
    create_mekanisme_badge,
    create_fase_badge,
)

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------
    'Sidebar',
    'Breadcrumb',
    'BreadcrumbItem',
    'create_breadcrumb',

    # -------------------------------------------------------------------------
    # Legacy Dashboard Cards (backward compatibility)
    # -------------------------------------------------------------------------
    'MekanismeCard',
    'TransaksiAktifCard',
    'SaldoUPWidgetLegacy',
    'QuickActionBar',

    # -------------------------------------------------------------------------
    # New Dashboard Components (recommended)
    # -------------------------------------------------------------------------
    'StatisticsSection',
    'MekanismeStatCard',
    'SaldoUPWidget',
    'QuickActionsWidget',
    'QuickActionButton',
    'RecentActivityWidget',
    'TransactionItemWidget',

    # -------------------------------------------------------------------------
    # Kanban Board
    # -------------------------------------------------------------------------
    'KanbanCard',
    'KanbanColumn',
    'KanbanBoard',
    'Mekanisme',
    'Urgency',
    'MEKANISME_COLORS',
    'URGENCY_COLORS',
    'FASE_CONFIG',
    'create_kanban_board',

    # -------------------------------------------------------------------------
    # Workflow Components
    # -------------------------------------------------------------------------
    'FaseStepper',
    'StageWidget',
    'DokumenChecklist',
    'CountdownWidget',

    # -------------------------------------------------------------------------
    # Calculation Widgets
    # -------------------------------------------------------------------------
    'KalkulasiWidget',
    'RincianKalkulasiWidget',

    # -------------------------------------------------------------------------
    # Toast Notifications
    # -------------------------------------------------------------------------
    'Toast',
    'ToastType',
    'ToastContainer',
    'ToastManager',
    'show_toast',
    'toast_success',
    'toast_error',
    'toast_warning',
    'toast_info',

    # -------------------------------------------------------------------------
    # Loading Overlay
    # -------------------------------------------------------------------------
    'SpinnerWidget',
    'LoadingOverlay',
    'LoadingMixin',
    'LoadingDots',

    # -------------------------------------------------------------------------
    # Empty State
    # -------------------------------------------------------------------------
    'EmptyState',

    # -------------------------------------------------------------------------
    # Validated Inputs
    # -------------------------------------------------------------------------
    'ValidatedLineEdit',
    'ValidatedSpinBox',
    'ValidatedCurrencySpinBox',
    'ValidatedComboBox',
    'ValidatedDateEdit',
    'ValidatedTextEdit',

    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------
    'required',
    'min_length',
    'max_length',
    'email',
    'numeric',
    'rupiah_range',
    'regex',
    'date_range',

    # -------------------------------------------------------------------------
    # Form Groups
    # -------------------------------------------------------------------------
    'FormGroup',
    'FormSection',
    'FormBuilder',
    'BuiltForm',

    # -------------------------------------------------------------------------
    # Dialogs
    # -------------------------------------------------------------------------
    'ConfirmDialog',
    'DialogType',
    'InputDialog',
    'InputType',

    # -------------------------------------------------------------------------
    # Search Bar
    # -------------------------------------------------------------------------
    'SearchBar',
    'AdvancedSearchBar',
    'create_search_bar',

    # -------------------------------------------------------------------------
    # Status Badges
    # -------------------------------------------------------------------------
    'StatusBadge',
    'StatusType',
    'MekanismeBadge',
    'FaseBadge',
    'FaseStatus',
    'PriorityBadge',
    'create_status_badge',
    'create_mekanisme_badge',
    'create_fase_badge',
]
