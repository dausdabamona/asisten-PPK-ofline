"""
PPK Document Factory - UI Utilities
====================================
Helper functions for common UI operations.

This module provides convenient wrapper functions for:
- Toast notifications
- Loading overlays
- Confirmation dialogs
- UI formatting utilities

Author: PPK Document Factory Team
Version: 4.0
"""

from typing import Optional, Callable, Any

from PySide6.QtWidgets import QWidget

from app.ui.components import (
    ToastManager,
    ToastType,
    ConfirmDialog,
    InputDialog,
    InputType,
)


# =============================================================================
# TOAST NOTIFICATION HELPERS
# =============================================================================

def show_toast(
    message: str,
    toast_type: str = "info",
    parent: Optional[QWidget] = None,
    duration: int = 3000
) -> None:
    """
    Show a toast notification.

    Args:
        message: Message to display
        toast_type: Type of toast (info, success, error, warning)
        parent: Parent widget
        duration: Duration in milliseconds

    Example:
        show_toast("Data berhasil disimpan", "success", self)
    """
    type_map = {
        'info': ToastType.INFO,
        'success': ToastType.SUCCESS,
        'error': ToastType.ERROR,
        'warning': ToastType.WARNING,
    }
    toast_type_enum = type_map.get(toast_type.lower(), ToastType.INFO)
    ToastManager.show(message, toast_type_enum, duration, parent)


def show_success(message: str, parent: Optional[QWidget] = None) -> None:
    """
    Show success toast notification.

    Args:
        message: Success message
        parent: Parent widget

    Example:
        show_success("Transaksi berhasil dibuat!", self)
    """
    ToastManager.success(message, parent)


def show_error(message: str, parent: Optional[QWidget] = None) -> None:
    """
    Show error toast notification.

    Args:
        message: Error message
        parent: Parent widget

    Example:
        show_error("Gagal menyimpan data!", self)
    """
    ToastManager.error(message, parent)


def show_warning(message: str, parent: Optional[QWidget] = None) -> None:
    """
    Show warning toast notification.

    Args:
        message: Warning message
        parent: Parent widget

    Example:
        show_warning("Data belum lengkap", self)
    """
    ToastManager.warning(message, parent)


def show_info(message: str, parent: Optional[QWidget] = None) -> None:
    """
    Show info toast notification.

    Args:
        message: Info message
        parent: Parent widget

    Example:
        show_info("Data sedang diproses", self)
    """
    ToastManager.info(message, parent)


# =============================================================================
# CONFIRMATION DIALOG HELPERS
# =============================================================================

def confirm(
    title: str,
    message: str,
    parent: Optional[QWidget] = None
) -> bool:
    """
    Show confirmation dialog.

    Args:
        title: Dialog title
        message: Confirmation message
        parent: Parent widget

    Returns:
        True if confirmed, False otherwise

    Example:
        if confirm("Simpan Data", "Yakin ingin menyimpan?", self):
            self.save_data()
    """
    return ConfirmDialog.confirm(title, message, parent)


def confirm_warning(
    title: str,
    message: str,
    parent: Optional[QWidget] = None
) -> bool:
    """
    Show warning confirmation dialog.

    Args:
        title: Dialog title
        message: Warning message
        parent: Parent widget

    Returns:
        True if confirmed, False otherwise

    Example:
        if confirm_warning("Perhatian", "Data akan diubah", self):
            self.update_data()
    """
    return ConfirmDialog.warning(title, message, parent)


def confirm_danger(
    title: str,
    message: str,
    parent: Optional[QWidget] = None
) -> bool:
    """
    Show danger confirmation dialog (for destructive actions).

    Args:
        title: Dialog title
        message: Warning message about destructive action
        parent: Parent widget

    Returns:
        True if confirmed, False otherwise

    Example:
        if confirm_danger("Hapus Data", "Data akan dihapus permanen!", self):
            self.delete_data()
    """
    return ConfirmDialog.danger(title, message, parent)


def show_info_dialog(
    title: str,
    message: str,
    parent: Optional[QWidget] = None
) -> None:
    """
    Show info dialog.

    Args:
        title: Dialog title
        message: Info message
        parent: Parent widget

    Example:
        show_info_dialog("Informasi", "Proses selesai", self)
    """
    ConfirmDialog.info(title, message, parent)


# =============================================================================
# INPUT DIALOG HELPERS
# =============================================================================

def get_text_input(
    title: str,
    label: str,
    default: str = "",
    parent: Optional[QWidget] = None
) -> Optional[str]:
    """
    Show text input dialog.

    Args:
        title: Dialog title
        label: Input label
        default: Default value
        parent: Parent widget

    Returns:
        Entered text or None if cancelled

    Example:
        name = get_text_input("Nama", "Masukkan nama:", parent=self)
        if name:
            self.set_name(name)
    """
    return InputDialog.get_text(title, label, default, parent)


def get_number_input(
    title: str,
    label: str,
    default: int = 0,
    parent: Optional[QWidget] = None
) -> Optional[int]:
    """
    Show number input dialog.

    Args:
        title: Dialog title
        label: Input label
        default: Default value
        parent: Parent widget

    Returns:
        Entered number or None if cancelled

    Example:
        qty = get_number_input("Jumlah", "Masukkan jumlah:", parent=self)
        if qty is not None:
            self.set_quantity(qty)
    """
    return InputDialog.get_number(title, label, default, parent)


def get_choice_input(
    title: str,
    label: str,
    options: list,
    default: Optional[str] = None,
    parent: Optional[QWidget] = None
) -> Optional[str]:
    """
    Show choice input dialog.

    Args:
        title: Dialog title
        label: Input label
        options: List of options
        default: Default selection
        parent: Parent widget

    Returns:
        Selected option or None if cancelled

    Example:
        status = get_choice_input(
            "Status",
            "Pilih status:",
            ["Aktif", "Nonaktif"],
            parent=self
        )
    """
    return InputDialog.get_choice(title, label, options, default, parent)


# =============================================================================
# FORMATTING UTILITIES
# =============================================================================

def format_rupiah(value: Any, prefix: str = "Rp ") -> str:
    """
    Format number as Indonesian Rupiah.

    Args:
        value: Number to format
        prefix: Currency prefix (default "Rp ")

    Returns:
        Formatted currency string

    Example:
        format_rupiah(1000000) -> "Rp 1.000.000"
    """
    if value is None:
        return f"{prefix}0"

    try:
        num = int(float(value))
        formatted = f"{num:,}".replace(",", ".")
        return f"{prefix}{formatted}"
    except (ValueError, TypeError):
        return f"{prefix}0"


def format_tanggal(date_str: str, format_out: str = "%d %B %Y") -> str:
    """
    Format date string to Indonesian format.

    Args:
        date_str: Date string (YYYY-MM-DD or datetime)
        format_out: Output format

    Returns:
        Formatted date string

    Example:
        format_tanggal("2024-01-15") -> "15 Januari 2024"
    """
    from datetime import datetime

    bulan_id = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }

    try:
        if isinstance(date_str, datetime):
            dt = date_str
        else:
            dt = datetime.fromisoformat(str(date_str)[:10])

        day = dt.day
        month = bulan_id.get(dt.month, str(dt.month))
        year = dt.year

        return f"{day} {month} {year}"
    except (ValueError, AttributeError):
        return str(date_str)


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncated

    Returns:
        Truncated text

    Example:
        truncate_text("Very long text here", 10) -> "Very lo..."
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix
