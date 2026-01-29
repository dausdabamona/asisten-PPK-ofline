"""UI modules"""
from .dashboard import DashboardWindow
from .template_manager import TemplateManagerDialog
from .item_barang_manager import ItemBarangManager, ItemBarangDialog
from .survey_toko_manager import SurveyTokoManager, SurveyTokoDialog
from .timeline_manager import TimelineManager, format_tanggal_indonesia
from .shortcuts import (
    ShortcutManager,
    ShortcutInfo,
    ShortcutContext,
    ShortcutHelpDialog,
    get_shortcut_manager,
    register_shortcut,
)
from .utils import (
    # Toast helpers
    show_toast,
    show_success,
    show_error,
    show_warning,
    show_info,
    # Dialog helpers
    confirm,
    confirm_warning,
    confirm_danger,
    show_info_dialog,
    # Input helpers
    get_text_input,
    get_number_input,
    get_choice_input,
    # Formatters
    format_rupiah,
    format_tanggal,
    truncate_text,
)
