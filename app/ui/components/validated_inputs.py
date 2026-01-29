"""
PPK DOCUMENT FACTORY - Validated Input Components
=================================================
Form input components dengan built-in validation:
- Visual feedback untuk validation errors
- Reusable validators
- Signals untuk state changes

Author: PPK Document Factory Team
Version: 4.0
"""

import re
from typing import Any, Callable, List, Optional, Tuple
from functools import partial

from PySide6.QtWidgets import (
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
    QDateEdit, QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate, QLocale
from PySide6.QtGui import QColor, QIntValidator, QDoubleValidator


# =============================================================================
# VALIDATORS (Module-level functions)
# =============================================================================

def required(value: Any) -> Tuple[bool, str]:
    """
    Validate that value is not empty.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        return False, "Field ini wajib diisi"

    if isinstance(value, str) and not value.strip():
        return False, "Field ini wajib diisi"

    if isinstance(value, (list, dict)) and len(value) == 0:
        return False, "Field ini wajib diisi"

    return True, ""


def min_length(min_len: int) -> Callable[[Any], Tuple[bool, str]]:
    """
    Create validator for minimum length.

    Args:
        min_len: Minimum required length

    Returns:
        Validator function
    """
    def validator(value: Any) -> Tuple[bool, str]:
        if value is None or (isinstance(value, str) and not value.strip()):
            return True, ""  # Skip if empty (use required for mandatory)

        if isinstance(value, str) and len(value.strip()) < min_len:
            return False, f"Minimal {min_len} karakter"

        return True, ""

    return validator


def max_length(max_len: int) -> Callable[[Any], Tuple[bool, str]]:
    """
    Create validator for maximum length.

    Args:
        max_len: Maximum allowed length

    Returns:
        Validator function
    """
    def validator(value: Any) -> Tuple[bool, str]:
        if value is None:
            return True, ""

        if isinstance(value, str) and len(value) > max_len:
            return False, f"Maksimal {max_len} karakter"

        return True, ""

    return validator


def email(value: Any) -> Tuple[bool, str]:
    """
    Validate email format.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return True, ""  # Skip if empty

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, str(value)):
        return False, "Format email tidak valid"

    return True, ""


def numeric(value: Any) -> Tuple[bool, str]:
    """
    Validate that value is numeric.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return True, ""  # Skip if empty

    try:
        float(str(value).replace(".", "").replace(",", "."))
        return True, ""
    except ValueError:
        return False, "Harus berupa angka"


def rupiah_range(
    min_val: Optional[float] = None,
    max_val: Optional[float] = None
) -> Callable[[Any], Tuple[bool, str]]:
    """
    Create validator for rupiah value range.

    Args:
        min_val: Minimum value (None for no limit)
        max_val: Maximum value (None for no limit)

    Returns:
        Validator function
    """
    def validator(value: Any) -> Tuple[bool, str]:
        if value is None:
            return True, ""

        try:
            num = float(value)
        except (TypeError, ValueError):
            return False, "Harus berupa angka"

        if min_val is not None and num < min_val:
            return False, f"Minimal Rp {min_val:,.0f}".replace(",", ".")

        if max_val is not None and num > max_val:
            return False, f"Maksimal Rp {max_val:,.0f}".replace(",", ".")

        return True, ""

    return validator


def regex(
    pattern: str,
    message: str = "Format tidak valid"
) -> Callable[[Any], Tuple[bool, str]]:
    """
    Create validator for regex pattern.

    Args:
        pattern: Regex pattern
        message: Error message

    Returns:
        Validator function
    """
    compiled = re.compile(pattern)

    def validator(value: Any) -> Tuple[bool, str]:
        if value is None or (isinstance(value, str) and not value.strip()):
            return True, ""  # Skip if empty

        if not compiled.match(str(value)):
            return False, message

        return True, ""

    return validator


def date_range(
    min_date: Optional[QDate] = None,
    max_date: Optional[QDate] = None
) -> Callable[[Any], Tuple[bool, str]]:
    """
    Create validator for date range.

    Args:
        min_date: Minimum date
        max_date: Maximum date

    Returns:
        Validator function
    """
    def validator(value: Any) -> Tuple[bool, str]:
        if value is None:
            return True, ""

        if isinstance(value, QDate):
            date_val = value
        else:
            return True, ""  # Can't validate non-QDate

        if min_date and date_val < min_date:
            return False, f"Tanggal minimal {min_date.toString('dd/MM/yyyy')}"

        if max_date and date_val > max_date:
            return False, f"Tanggal maksimal {max_date.toString('dd/MM/yyyy')}"

        return True, ""

    return validator


# =============================================================================
# BASE VALIDATION MIXIN
# =============================================================================

class ValidationMixin:
    """
    Mixin providing validation functionality.

    Add to input widgets to gain validation capabilities.
    """

    # Signals (to be connected in subclass)
    validation_changed: Signal  # bool

    def _init_validation(self) -> None:
        """Initialize validation state."""
        self._validators: List[Tuple[Callable, str]] = []
        self._is_required = False
        self._error_message = ""
        self._is_valid = True

        # Styling
        self._normal_style = ""
        self._error_style = """
            border: 2px solid #e74c3c;
            background-color: #fdf2f2;
        """

    def add_validator(
        self,
        validator: Callable[[Any], Tuple[bool, str]],
        error_message: Optional[str] = None
    ) -> None:
        """
        Add validator function.

        Args:
            validator: Function that returns (is_valid, error_message)
            error_message: Override error message (optional)
        """
        self._validators.append((validator, error_message or ""))

    def set_required(self, required_flag: bool = True) -> None:
        """
        Set whether field is required.

        Args:
            required_flag: True if required
        """
        self._is_required = required_flag

    def validate(self) -> bool:
        """
        Run all validators.

        Returns:
            True if all validators pass
        """
        value = self._get_value()

        # Check required
        if self._is_required:
            is_valid, msg = required(value)
            if not is_valid:
                self._set_error(msg)
                return False

        # Run custom validators
        for validator, override_msg in self._validators:
            is_valid, msg = validator(value)
            if not is_valid:
                self._set_error(override_msg or msg)
                return False

        # All passed
        self.clear_error()
        return True

    def _get_value(self) -> Any:
        """Get current value. Override in subclass."""
        return None

    def _set_error(self, message: str) -> None:
        """Set error state."""
        self._is_valid = False
        self._error_message = message
        self._apply_error_style()
        self.setToolTip(message)
        if hasattr(self, 'validation_changed'):
            self.validation_changed.emit(False)

    def clear_error(self) -> None:
        """Clear error state."""
        self._is_valid = True
        self._error_message = ""
        self._apply_normal_style()
        self.setToolTip("")
        if hasattr(self, 'validation_changed'):
            self.validation_changed.emit(True)

    def _apply_error_style(self) -> None:
        """Apply error styling. Override for custom styling."""
        pass

    def _apply_normal_style(self) -> None:
        """Apply normal styling. Override for custom styling."""
        pass

    def get_error(self) -> str:
        """Get current error message."""
        return self._error_message

    @property
    def is_valid(self) -> bool:
        """Check if currently valid."""
        return self._is_valid


# =============================================================================
# VALIDATED LINE EDIT
# =============================================================================

class ValidatedLineEdit(QLineEdit, ValidationMixin):
    """
    Line edit with built-in validation.

    Signals:
        validation_changed(bool): Emitted when validation state changes
        value_changed(str): Emitted when value changes

    Usage:
        edit = ValidatedLineEdit()
        edit.set_required(True)
        edit.add_validator(min_length(3))
        edit.add_validator(email)

        if edit.validate():
            value = edit.text()
    """

    validation_changed = Signal(bool)
    value_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_validation()
        self._setup_style()

        # Connect text change
        self.textChanged.connect(self._on_text_changed)

    def _setup_style(self) -> None:
        """Setup styling."""
        self._normal_style = """
            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """
        self.setStyleSheet(self._normal_style)

    def _on_text_changed(self, text: str) -> None:
        """Handle text change."""
        self.value_changed.emit(text)
        # Auto-validate on change if there was an error
        if not self._is_valid:
            self.validate()

    def _get_value(self) -> str:
        return self.text()

    def _apply_error_style(self) -> None:
        self.setStyleSheet(self._normal_style + """
            QLineEdit {
                border: 2px solid #e74c3c;
                background-color: #fdf2f2;
            }
        """)

    def _apply_normal_style(self) -> None:
        self.setStyleSheet(self._normal_style)


# =============================================================================
# VALIDATED SPIN BOX
# =============================================================================

class ValidatedSpinBox(QSpinBox, ValidationMixin):
    """
    Spin box with built-in validation.

    Signals:
        validation_changed(bool): Emitted when validation state changes
        value_changed(int): Emitted when value changes
    """

    validation_changed = Signal(bool)
    value_changed_signal = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_validation()
        self._setup_style()

        self.valueChanged.connect(self._on_value_changed)

    def _setup_style(self) -> None:
        self._normal_style = """
            QSpinBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
            }
            QSpinBox:focus {
                border-color: #3498db;
            }
        """
        self.setStyleSheet(self._normal_style)

    def _on_value_changed(self, value: int) -> None:
        self.value_changed_signal.emit(value)
        if not self._is_valid:
            self.validate()

    def _get_value(self) -> int:
        return self.value()

    def _apply_error_style(self) -> None:
        self.setStyleSheet(self._normal_style + """
            QSpinBox {
                border: 2px solid #e74c3c;
                background-color: #fdf2f2;
            }
        """)

    def _apply_normal_style(self) -> None:
        self.setStyleSheet(self._normal_style)


# =============================================================================
# VALIDATED CURRENCY SPIN BOX
# =============================================================================

class ValidatedCurrencySpinBox(QDoubleSpinBox, ValidationMixin):
    """
    Currency spin box (Rupiah) with validation.

    Displays values in Indonesian Rupiah format.

    Signals:
        validation_changed(bool): Emitted when validation state changes
        value_changed(float): Emitted when value changes
    """

    validation_changed = Signal(bool)
    value_changed_signal = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_validation()
        self._setup_style()

        # Currency settings
        self.setRange(0, 999999999999)
        self.setDecimals(0)
        self.setSingleStep(100000)
        self.setPrefix("Rp ")

        # Indonesian locale
        locale = QLocale(QLocale.Language.Indonesian, QLocale.Country.Indonesia)
        self.setLocale(locale)

        self.valueChanged.connect(self._on_value_changed)

    def _setup_style(self) -> None:
        self._normal_style = """
            QDoubleSpinBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
            }
            QDoubleSpinBox:focus {
                border-color: #3498db;
            }
        """
        self.setStyleSheet(self._normal_style)

    def textFromValue(self, value: float) -> str:
        """Format value with thousand separator."""
        return f"{value:,.0f}".replace(",", ".")

    def valueFromText(self, text: str) -> float:
        """Parse text to value."""
        clean = text.replace("Rp ", "").replace(".", "").replace(",", "").strip()
        try:
            return float(clean) if clean else 0
        except ValueError:
            return 0

    def _on_value_changed(self, value: float) -> None:
        self.value_changed_signal.emit(value)
        if not self._is_valid:
            self.validate()

    def _get_value(self) -> float:
        return self.value()

    def _apply_error_style(self) -> None:
        self.setStyleSheet(self._normal_style + """
            QDoubleSpinBox {
                border: 2px solid #e74c3c;
                background-color: #fdf2f2;
            }
        """)

    def _apply_normal_style(self) -> None:
        self.setStyleSheet(self._normal_style)


# =============================================================================
# VALIDATED COMBO BOX
# =============================================================================

class ValidatedComboBox(QComboBox, ValidationMixin):
    """
    Combo box with built-in validation.

    Supports placeholder "Pilih..." as invalid selection.

    Signals:
        validation_changed(bool): Emitted when validation state changes
        value_changed(object): Emitted when selection changes
    """

    validation_changed = Signal(bool)
    value_changed_signal = Signal(object)

    PLACEHOLDER_TEXT = "-- Pilih --"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_validation()
        self._setup_style()
        self._has_placeholder = False

        self.currentIndexChanged.connect(self._on_index_changed)

    def _setup_style(self) -> None:
        self._normal_style = """
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
        """
        self.setStyleSheet(self._normal_style)

    def add_placeholder(self, text: str = None) -> None:
        """
        Add placeholder item at index 0.

        Args:
            text: Placeholder text
        """
        placeholder = text or self.PLACEHOLDER_TEXT
        self.insertItem(0, placeholder, None)
        self.setCurrentIndex(0)
        self._has_placeholder = True

    def _on_index_changed(self, index: int) -> None:
        data = self.currentData()
        self.value_changed_signal.emit(data)
        if not self._is_valid:
            self.validate()

    def _get_value(self) -> Any:
        return self.currentData()

    def validate(self) -> bool:
        """Override to check placeholder."""
        # If required and placeholder selected, invalid
        if self._is_required and self._has_placeholder:
            if self.currentIndex() == 0:
                self._set_error("Pilih salah satu opsi")
                return False

        return super().validate()

    def _apply_error_style(self) -> None:
        self.setStyleSheet(self._normal_style + """
            QComboBox {
                border: 2px solid #e74c3c;
                background-color: #fdf2f2;
            }
        """)

    def _apply_normal_style(self) -> None:
        self.setStyleSheet(self._normal_style)


# =============================================================================
# VALIDATED DATE EDIT
# =============================================================================

class ValidatedDateEdit(QDateEdit, ValidationMixin):
    """
    Date edit with built-in validation.

    Supports date range validation.

    Signals:
        validation_changed(bool): Emitted when validation state changes
        value_changed(QDate): Emitted when date changes
    """

    validation_changed = Signal(bool)
    value_changed_signal = Signal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_validation()
        self._setup_style()

        self.setCalendarPopup(True)
        self.setDate(QDate.currentDate())

        self.dateChanged.connect(self._on_date_changed)

    def _setup_style(self) -> None:
        self._normal_style = """
            QDateEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
            }
            QDateEdit:focus {
                border-color: #3498db;
            }
        """
        self.setStyleSheet(self._normal_style)

    def set_min_date(self, date: QDate) -> None:
        """Set minimum allowed date."""
        self.setMinimumDate(date)

    def set_max_date(self, date: QDate) -> None:
        """Set maximum allowed date."""
        self.setMaximumDate(date)

    def _on_date_changed(self, date: QDate) -> None:
        self.value_changed_signal.emit(date)
        if not self._is_valid:
            self.validate()

    def _get_value(self) -> QDate:
        return self.date()

    def _apply_error_style(self) -> None:
        self.setStyleSheet(self._normal_style + """
            QDateEdit {
                border: 2px solid #e74c3c;
                background-color: #fdf2f2;
            }
        """)

    def _apply_normal_style(self) -> None:
        self.setStyleSheet(self._normal_style)


# =============================================================================
# VALIDATED TEXT EDIT
# =============================================================================

class ValidatedTextEdit(QWidget, ValidationMixin):
    """
    Text edit with validation and character counter.

    Signals:
        validation_changed(bool): Emitted when validation state changes
        value_changed(str): Emitted when text changes
    """

    validation_changed = Signal(bool)
    value_changed = Signal(str)

    def __init__(
        self,
        max_length: Optional[int] = None,
        show_counter: bool = True,
        parent=None
    ):
        super().__init__(parent)
        self._init_validation()
        self._max_length = max_length
        self._show_counter = show_counter

        self._setup_ui()

        if max_length:
            self.add_validator(max_length_validator(max_length))

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Text edit
        self._text_edit = QTextEdit()
        self._text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        self._text_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._text_edit)

        # Counter label
        if self._show_counter and self._max_length:
            self._counter_label = QLabel(f"0/{self._max_length}")
            self._counter_label.setStyleSheet("""
                color: #6c757d;
                font-size: 11px;
            """)
            self._counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addWidget(self._counter_label)

    def _on_text_changed(self) -> None:
        text = self._text_edit.toPlainText()
        self.value_changed.emit(text)

        # Update counter
        if self._show_counter and self._max_length:
            count = len(text)
            self._counter_label.setText(f"{count}/{self._max_length}")

            if count > self._max_length:
                self._counter_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
            else:
                self._counter_label.setStyleSheet("color: #6c757d; font-size: 11px;")

        if not self._is_valid:
            self.validate()

    def _get_value(self) -> str:
        return self._text_edit.toPlainText()

    def text(self) -> str:
        """Get text content."""
        return self._text_edit.toPlainText()

    def setText(self, text: str) -> None:
        """Set text content."""
        self._text_edit.setPlainText(text)

    def setPlainText(self, text: str) -> None:
        """Set plain text content."""
        self._text_edit.setPlainText(text)

    def toPlainText(self) -> str:
        """Get plain text content."""
        return self._text_edit.toPlainText()

    def setMaximumHeight(self, height: int) -> None:
        """Set maximum height."""
        self._text_edit.setMaximumHeight(height)

    def setPlaceholderText(self, text: str) -> None:
        """Set placeholder text."""
        self._text_edit.setPlaceholderText(text)

    def _apply_error_style(self) -> None:
        self._text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e74c3c;
                border-radius: 4px;
                padding: 8px;
                background-color: #fdf2f2;
            }
        """)

    def _apply_normal_style(self) -> None:
        self._text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)

    def setToolTip(self, text: str) -> None:
        """Set tooltip on text edit."""
        self._text_edit.setToolTip(text)


# Helper for ValidatedTextEdit
def max_length_validator(max_len: int) -> Callable[[Any], Tuple[bool, str]]:
    """Create max length validator for text."""
    return max_length(max_len)
