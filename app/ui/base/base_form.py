"""
PPK DOCUMENT FACTORY - Base Form Widget
=======================================
Generic form builder dengan:
- Dynamic form generation dari field definitions
- Built-in validation dengan error messages
- Signals untuk form state management

Author: PPK Document Factory Team
Version: 4.0
"""

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QDateEdit, QTimeEdit, QDateTimeEdit,
    QGroupBox, QFrame, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QDate, QTime, QDateTime
from PySide6.QtGui import QColor


# =============================================================================
# VALIDATORS
# =============================================================================

class ValidationResult:
    """Result dari validation check."""

    def __init__(self, is_valid: bool, message: str = ""):
        self.is_valid = is_valid
        self.message = message

    def __bool__(self) -> bool:
        return self.is_valid


def required_validator(value: Any) -> ValidationResult:
    """
    Validator untuk field yang wajib diisi.

    Args:
        value: Nilai yang akan divalidasi

    Returns:
        ValidationResult dengan status valid/invalid
    """
    if value is None:
        return ValidationResult(False, "Field ini wajib diisi")

    if isinstance(value, str) and not value.strip():
        return ValidationResult(False, "Field ini wajib diisi")

    if isinstance(value, (list, dict)) and len(value) == 0:
        return ValidationResult(False, "Field ini wajib diisi")

    return ValidationResult(True)


def min_length_validator(min_len: int) -> Callable[[Any], ValidationResult]:
    """
    Factory untuk validator minimum panjang string.

    Args:
        min_len: Panjang minimum yang diizinkan

    Returns:
        Validator function

    Example:
        validators=[min_length_validator(3)]
    """
    def validator(value: Any) -> ValidationResult:
        if value is None or (isinstance(value, str) and not value.strip()):
            return ValidationResult(True)  # Skip jika kosong (gunakan required untuk wajib)

        if isinstance(value, str) and len(value.strip()) < min_len:
            return ValidationResult(False, f"Minimal {min_len} karakter")

        return ValidationResult(True)

    return validator


def max_length_validator(max_len: int) -> Callable[[Any], ValidationResult]:
    """
    Factory untuk validator maximum panjang string.

    Args:
        max_len: Panjang maximum yang diizinkan

    Returns:
        Validator function

    Example:
        validators=[max_length_validator(100)]
    """
    def validator(value: Any) -> ValidationResult:
        if value is None:
            return ValidationResult(True)

        if isinstance(value, str) and len(value) > max_len:
            return ValidationResult(False, f"Maksimal {max_len} karakter")

        return ValidationResult(True)

    return validator


def number_range_validator(
    min_val: Optional[float] = None,
    max_val: Optional[float] = None
) -> Callable[[Any], ValidationResult]:
    """
    Factory untuk validator rentang angka.

    Args:
        min_val: Nilai minimum (None untuk tanpa batas bawah)
        max_val: Nilai maximum (None untuk tanpa batas atas)

    Returns:
        Validator function

    Example:
        validators=[number_range_validator(0, 100)]
    """
    def validator(value: Any) -> ValidationResult:
        if value is None:
            return ValidationResult(True)

        try:
            num = float(value)
        except (TypeError, ValueError):
            return ValidationResult(False, "Harus berupa angka")

        if min_val is not None and num < min_val:
            return ValidationResult(False, f"Minimal {min_val}")

        if max_val is not None and num > max_val:
            return ValidationResult(False, f"Maksimal {max_val}")

        return ValidationResult(True)

    return validator


def regex_validator(
    pattern: str,
    message: str = "Format tidak valid"
) -> Callable[[Any], ValidationResult]:
    """
    Factory untuk validator regex pattern.

    Args:
        pattern: Regex pattern
        message: Pesan error jika tidak valid

    Returns:
        Validator function

    Example:
        validators=[regex_validator(r'^[A-Z]{2}\\d{4}$', 'Format: XX0000')]
    """
    compiled = re.compile(pattern)

    def validator(value: Any) -> ValidationResult:
        if value is None or (isinstance(value, str) and not value.strip()):
            return ValidationResult(True)  # Skip jika kosong

        if not isinstance(value, str):
            value = str(value)

        if not compiled.match(value):
            return ValidationResult(False, message)

        return ValidationResult(True)

    return validator


def email_validator(value: Any) -> ValidationResult:
    """Validator untuk format email."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return ValidationResult(True)

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, str(value)):
        return ValidationResult(False, "Format email tidak valid")

    return ValidationResult(True)


def phone_validator(value: Any) -> ValidationResult:
    """Validator untuk nomor telepon Indonesia."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return ValidationResult(True)

    # Remove common separators
    clean = re.sub(r'[\s\-\.]', '', str(value))

    # Check format: +62xxx, 62xxx, 08xxx, or 8xxx
    pattern = r'^(\+62|62|0)?8[1-9]\d{7,10}$'
    if not re.match(pattern, clean):
        return ValidationResult(False, "Format nomor telepon tidak valid")

    return ValidationResult(True)


def nip_validator(value: Any) -> ValidationResult:
    """Validator untuk NIP PNS (18 digit)."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return ValidationResult(True)

    clean = re.sub(r'\s', '', str(value))

    if not re.match(r'^\d{18}$', clean):
        return ValidationResult(False, "NIP harus 18 digit angka")

    return ValidationResult(True)


def nik_validator(value: Any) -> ValidationResult:
    """Validator untuk NIK KTP (16 digit)."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return ValidationResult(True)

    clean = re.sub(r'\s', '', str(value))

    if not re.match(r'^\d{16}$', clean):
        return ValidationResult(False, "NIK harus 16 digit angka")

    return ValidationResult(True)


def npwp_validator(value: Any) -> ValidationResult:
    """Validator untuk NPWP."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return ValidationResult(True)

    # Remove separators
    clean = re.sub(r'[\s\.\-]', '', str(value))

    # NPWP format: 15 digits or new format 16 digits
    if not re.match(r'^\d{15,16}$', clean):
        return ValidationResult(False, "Format NPWP tidak valid")

    return ValidationResult(True)


# =============================================================================
# FIELD TYPES
# =============================================================================

class FieldType(Enum):
    """Enum untuk tipe field yang didukung."""
    TEXT = "text"
    PASSWORD = "password"
    NUMBER = "number"
    DECIMAL = "decimal"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    COMBO = "combo"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    CURRENCY = "currency"


@dataclass
class FormField:
    """
    Definisi field untuk form builder.

    Attributes:
        name: Nama unik field (digunakan sebagai key)
        label: Label yang ditampilkan
        field_type: Tipe widget (text, number, date, combo, dll)
        required: Apakah field wajib diisi
        validators: List validator functions
        default_value: Nilai default
        placeholder: Placeholder text untuk input
        tooltip: Tooltip text
        options: List opsi untuk combo box [(value, label), ...]
        min_value: Nilai minimum untuk number fields
        max_value: Nilai maximum untuk number fields
        readonly: Apakah field readonly
        row_span: Berapa baris yang digunakan (untuk textarea)
        width: Custom width (None untuk auto)
        group: Nama group untuk grouping fields
    """
    name: str
    label: str
    field_type: Union[FieldType, str] = FieldType.TEXT
    required: bool = False
    validators: List[Callable[[Any], ValidationResult]] = field(default_factory=list)
    default_value: Any = None
    placeholder: str = ""
    tooltip: str = ""
    options: List[tuple] = field(default_factory=list)  # [(value, label), ...]
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    readonly: bool = False
    row_span: int = 1
    width: Optional[int] = None
    group: str = ""

    def __post_init__(self):
        # Convert string to FieldType if needed
        if isinstance(self.field_type, str):
            self.field_type = FieldType(self.field_type)

        # Add required validator if needed
        if self.required and required_validator not in self.validators:
            self.validators = [required_validator] + list(self.validators)


# =============================================================================
# BASE FORM WIDGET
# =============================================================================

class BaseFormWidget(QWidget):
    """
    Generic form widget dengan dynamic field generation.

    Features:
    - Auto-generate form layout dari field definitions
    - Built-in validation dengan visual feedback
    - Signals untuk form state management
    - Support multiple field types
    - Grouping fields

    Signals:
        form_submitted(dict): Emitted ketika form di-submit dengan data valid
        form_cancelled(): Emitted ketika form di-cancel
        validation_changed(bool): Emitted ketika validation state berubah
        field_changed(str, Any): Emitted ketika nilai field berubah (name, value)

    Example:
        form = BaseFormWidget()
        form.add_field('nama', 'Nama Lengkap', required=True)
        form.add_field('email', 'Email', validators=[email_validator])
        form.add_field('umur', 'Umur', field_type=FieldType.NUMBER,
                      min_value=0, max_value=150)

        if form.validate():
            data = form.get_values()
    """

    # Signals
    form_submitted = Signal(dict)
    form_cancelled = Signal()
    validation_changed = Signal(bool)
    field_changed = Signal(str, object)  # field_name, value

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        use_scroll: bool = False,
        show_buttons: bool = False
    ):
        """
        Initialize form widget.

        Args:
            parent: Parent widget
            use_scroll: Wrap form dalam scroll area
            show_buttons: Tampilkan tombol Submit/Cancel
        """
        super().__init__(parent)

        self._fields: Dict[str, FormField] = {}
        self._widgets: Dict[str, QWidget] = {}
        self._error_labels: Dict[str, QLabel] = {}
        self._groups: Dict[str, QGroupBox] = {}
        self._is_valid: bool = True
        self._readonly: bool = False

        self._use_scroll = use_scroll
        self._show_buttons = show_buttons

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup base UI structure."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Form container (optionally wrapped in scroll)
        if self._use_scroll:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)

            self._form_container = QWidget()
            self._form_layout = QFormLayout(self._form_container)
            scroll.setWidget(self._form_container)
            main_layout.addWidget(scroll)
        else:
            self._form_container = QWidget()
            self._form_layout = QFormLayout(self._form_container)
            main_layout.addWidget(self._form_container)

        self._form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self._form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Buttons (optional)
        if self._show_buttons:
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()

            self._btn_cancel = QPushButton("Batal")
            self._btn_cancel.clicked.connect(self._on_cancel)
            btn_layout.addWidget(self._btn_cancel)

            self._btn_submit = QPushButton("Simpan")
            self._btn_submit.setObjectName("btnSuccess")
            self._btn_submit.clicked.connect(self._on_submit)
            btn_layout.addWidget(self._btn_submit)

            main_layout.addLayout(btn_layout)

        # Error style
        self._error_style = """
            QLineEdit[hasError="true"],
            QTextEdit[hasError="true"],
            QComboBox[hasError="true"],
            QSpinBox[hasError="true"],
            QDoubleSpinBox[hasError="true"],
            QDateEdit[hasError="true"] {
                border: 2px solid #e74c3c;
                background-color: #fdf2f2;
            }
        """
        self.setStyleSheet(self._error_style)

    # =========================================================================
    # FIELD MANAGEMENT
    # =========================================================================

    def add_field(
        self,
        name: str,
        label: str,
        field_type: Union[FieldType, str] = FieldType.TEXT,
        required: bool = False,
        validators: Optional[List[Callable]] = None,
        default_value: Any = None,
        placeholder: str = "",
        tooltip: str = "",
        options: Optional[List[tuple]] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        readonly: bool = False,
        row_span: int = 1,
        width: Optional[int] = None,
        group: str = ""
    ) -> QWidget:
        """
        Tambah field ke form.

        Args:
            name: Nama unik field
            label: Label yang ditampilkan
            field_type: Tipe widget
            required: Wajib diisi
            validators: List validator functions
            default_value: Nilai default
            placeholder: Placeholder text
            tooltip: Tooltip text
            options: Opsi untuk combo [(value, label), ...]
            min_value: Nilai minimum
            max_value: Nilai maximum
            readonly: Readonly field
            row_span: Tinggi baris (untuk textarea)
            width: Custom width
            group: Nama group

        Returns:
            Widget yang dibuat

        Example:
            form.add_field('nama', 'Nama', required=True)
            form.add_field('status', 'Status', field_type='combo',
                          options=[('active', 'Aktif'), ('inactive', 'Nonaktif')])
        """
        field_def = FormField(
            name=name,
            label=label,
            field_type=field_type,
            required=required,
            validators=validators or [],
            default_value=default_value,
            placeholder=placeholder,
            tooltip=tooltip,
            options=options or [],
            min_value=min_value,
            max_value=max_value,
            readonly=readonly,
            row_span=row_span,
            width=width,
            group=group
        )

        return self.add_field_from_definition(field_def)

    def add_field_from_definition(self, field_def: FormField) -> QWidget:
        """
        Tambah field dari FormField definition.

        Args:
            field_def: FormField object

        Returns:
            Widget yang dibuat
        """
        if field_def.name in self._fields:
            raise ValueError(f"Field '{field_def.name}' already exists")

        # Create widget
        widget = self._create_widget(field_def)

        # Store references
        self._fields[field_def.name] = field_def
        self._widgets[field_def.name] = widget

        # Create label with required indicator
        label_text = field_def.label
        if field_def.required:
            label_text += " *"
        label = QLabel(label_text)

        if field_def.tooltip:
            label.setToolTip(field_def.tooltip)
            widget.setToolTip(field_def.tooltip)

        # Create error label (hidden by default)
        error_label = QLabel()
        error_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        error_label.hide()
        self._error_labels[field_def.name] = error_label

        # Create container with field and error
        container = QVBoxLayout()
        container.setSpacing(2)
        container.setContentsMargins(0, 0, 0, 0)
        container.addWidget(widget)
        container.addWidget(error_label)

        container_widget = QWidget()
        container_widget.setLayout(container)

        # Get or create group
        target_layout = self._form_layout
        if field_def.group:
            if field_def.group not in self._groups:
                group_box = QGroupBox(field_def.group)
                group_layout = QFormLayout()
                group_box.setLayout(group_layout)
                self._groups[field_def.group] = group_box
                self._form_layout.addRow(group_box)
            target_layout = self._groups[field_def.group].layout()

        # Add to layout
        target_layout.addRow(label, container_widget)

        # Set default value
        if field_def.default_value is not None:
            self.set_field_value(field_def.name, field_def.default_value)

        # Connect change signal
        self._connect_field_change(field_def.name, widget)

        # Apply readonly if form is readonly
        if self._readonly:
            self._set_widget_readonly(widget, True)

        return widget

    def add_fields(self, fields: List[FormField]) -> None:
        """
        Tambah multiple fields sekaligus.

        Args:
            fields: List of FormField definitions
        """
        for field_def in fields:
            self.add_field_from_definition(field_def)

    def _create_widget(self, field_def: FormField) -> QWidget:
        """Create appropriate widget based on field type."""
        widget: QWidget

        if field_def.field_type == FieldType.TEXT:
            widget = QLineEdit()
            if field_def.placeholder:
                widget.setPlaceholderText(field_def.placeholder)
            if field_def.readonly:
                widget.setReadOnly(True)

        elif field_def.field_type == FieldType.PASSWORD:
            widget = QLineEdit()
            widget.setEchoMode(QLineEdit.EchoMode.Password)
            if field_def.placeholder:
                widget.setPlaceholderText(field_def.placeholder)

        elif field_def.field_type == FieldType.TEXTAREA:
            widget = QTextEdit()
            if field_def.placeholder:
                widget.setPlaceholderText(field_def.placeholder)
            if field_def.row_span > 1:
                widget.setMinimumHeight(field_def.row_span * 25)
            else:
                widget.setMaximumHeight(80)
            if field_def.readonly:
                widget.setReadOnly(True)

        elif field_def.field_type == FieldType.NUMBER:
            widget = QSpinBox()
            widget.setRange(
                int(field_def.min_value or -999999999),
                int(field_def.max_value or 999999999)
            )
            if field_def.readonly:
                widget.setReadOnly(True)

        elif field_def.field_type == FieldType.DECIMAL:
            widget = QDoubleSpinBox()
            widget.setRange(
                field_def.min_value or -999999999.99,
                field_def.max_value or 999999999.99
            )
            widget.setDecimals(2)
            if field_def.readonly:
                widget.setReadOnly(True)

        elif field_def.field_type == FieldType.CURRENCY:
            widget = QDoubleSpinBox()
            widget.setRange(0, 999999999999)
            widget.setDecimals(0)
            widget.setPrefix("Rp ")
            widget.setSingleStep(100000)
            if field_def.readonly:
                widget.setReadOnly(True)

        elif field_def.field_type == FieldType.DATE:
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setDate(QDate.currentDate())
            if field_def.readonly:
                widget.setReadOnly(True)

        elif field_def.field_type == FieldType.TIME:
            widget = QTimeEdit()
            widget.setTime(QTime.currentTime())
            if field_def.readonly:
                widget.setReadOnly(True)

        elif field_def.field_type == FieldType.DATETIME:
            widget = QDateTimeEdit()
            widget.setCalendarPopup(True)
            widget.setDateTime(QDateTime.currentDateTime())
            if field_def.readonly:
                widget.setReadOnly(True)

        elif field_def.field_type == FieldType.COMBO:
            widget = QComboBox()
            widget.setEditable(not field_def.readonly)
            for value, label in field_def.options:
                widget.addItem(label, value)
            if field_def.readonly:
                widget.setEnabled(False)

        elif field_def.field_type == FieldType.CHECKBOX:
            widget = QCheckBox()
            if field_def.readonly:
                widget.setEnabled(False)

        else:
            widget = QLineEdit()

        if field_def.width:
            widget.setFixedWidth(field_def.width)

        return widget

    def _connect_field_change(self, name: str, widget: QWidget) -> None:
        """Connect widget's change signal to emit field_changed."""
        def emit_change():
            value = self.get_field_value(name)
            self.field_changed.emit(name, value)
            self._validate_field(name)

        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(emit_change)
        elif isinstance(widget, QTextEdit):
            widget.textChanged.connect(emit_change)
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.valueChanged.connect(emit_change)
        elif isinstance(widget, QComboBox):
            widget.currentIndexChanged.connect(emit_change)
        elif isinstance(widget, QCheckBox):
            widget.stateChanged.connect(emit_change)
        elif isinstance(widget, QDateEdit):
            widget.dateChanged.connect(emit_change)
        elif isinstance(widget, QTimeEdit):
            widget.timeChanged.connect(emit_change)
        elif isinstance(widget, QDateTimeEdit):
            widget.dateTimeChanged.connect(emit_change)

    # =========================================================================
    # VALUE MANAGEMENT
    # =========================================================================

    def get_field_value(self, name: str) -> Any:
        """
        Get value dari field tertentu.

        Args:
            name: Nama field

        Returns:
            Nilai field
        """
        if name not in self._widgets:
            raise KeyError(f"Field '{name}' not found")

        widget = self._widgets[name]
        field_def = self._fields[name]

        if isinstance(widget, QLineEdit):
            return widget.text().strip()
        elif isinstance(widget, QTextEdit):
            return widget.toPlainText().strip()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        elif isinstance(widget, QDoubleSpinBox):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return widget.currentData()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QDateEdit):
            return widget.date().toPython()
        elif isinstance(widget, QTimeEdit):
            return widget.time().toPython()
        elif isinstance(widget, QDateTimeEdit):
            return widget.dateTime().toPython()

        return None

    def set_field_value(self, name: str, value: Any) -> None:
        """
        Set value untuk field tertentu.

        Args:
            name: Nama field
            value: Nilai yang akan di-set
        """
        if name not in self._widgets:
            raise KeyError(f"Field '{name}' not found")

        widget = self._widgets[name]

        if isinstance(widget, QLineEdit):
            widget.setText(str(value) if value is not None else "")
        elif isinstance(widget, QTextEdit):
            widget.setPlainText(str(value) if value is not None else "")
        elif isinstance(widget, QSpinBox):
            widget.setValue(int(value) if value is not None else 0)
        elif isinstance(widget, QDoubleSpinBox):
            widget.setValue(float(value) if value is not None else 0.0)
        elif isinstance(widget, QComboBox):
            idx = widget.findData(value)
            if idx >= 0:
                widget.setCurrentIndex(idx)
            elif isinstance(value, str):
                widget.setCurrentText(value)
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))
        elif isinstance(widget, QDateEdit):
            if value:
                if isinstance(value, str):
                    widget.setDate(QDate.fromString(value, "yyyy-MM-dd"))
                else:
                    widget.setDate(QDate(value.year, value.month, value.day))
        elif isinstance(widget, QTimeEdit):
            if value:
                if isinstance(value, str):
                    widget.setTime(QTime.fromString(value, "HH:mm:ss"))
                else:
                    widget.setTime(QTime(value.hour, value.minute, value.second))
        elif isinstance(widget, QDateTimeEdit):
            if value:
                if isinstance(value, str):
                    widget.setDateTime(QDateTime.fromString(value, "yyyy-MM-dd HH:mm:ss"))

    def get_values(self) -> Dict[str, Any]:
        """
        Get semua nilai form sebagai dictionary.

        Returns:
            Dictionary dengan format {field_name: value}
        """
        return {name: self.get_field_value(name) for name in self._fields}

    def set_values(self, data: Dict[str, Any]) -> None:
        """
        Set multiple values sekaligus.

        Args:
            data: Dictionary {field_name: value}
        """
        for name, value in data.items():
            if name in self._fields:
                self.set_field_value(name, value)

    def clear(self) -> None:
        """Clear semua field ke default values."""
        for name, field_def in self._fields.items():
            if field_def.default_value is not None:
                self.set_field_value(name, field_def.default_value)
            else:
                widget = self._widgets[name]
                if isinstance(widget, QLineEdit):
                    widget.clear()
                elif isinstance(widget, QTextEdit):
                    widget.clear()
                elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    widget.setValue(widget.minimum())
                elif isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(False)
                elif isinstance(widget, QDateEdit):
                    widget.setDate(QDate.currentDate())

        # Clear errors
        self._clear_all_errors()

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def validate(self) -> bool:
        """
        Validate semua fields.

        Returns:
            bool: True jika semua valid
        """
        all_valid = True

        for name in self._fields:
            if not self._validate_field(name):
                all_valid = False

        self._is_valid = all_valid
        self.validation_changed.emit(all_valid)

        return all_valid

    def _validate_field(self, name: str) -> bool:
        """Validate single field."""
        if name not in self._fields:
            return True

        field_def = self._fields[name]
        value = self.get_field_value(name)

        # Run all validators
        for validator in field_def.validators:
            result = validator(value)
            if not result.is_valid:
                self._show_field_error(name, result.message)
                return False

        # Clear error if valid
        self._clear_field_error(name)
        return True

    def _show_field_error(self, name: str, message: str) -> None:
        """Show error for field."""
        if name in self._error_labels:
            self._error_labels[name].setText(message)
            self._error_labels[name].show()

        if name in self._widgets:
            self._widgets[name].setProperty("hasError", True)
            self._widgets[name].style().unpolish(self._widgets[name])
            self._widgets[name].style().polish(self._widgets[name])

    def _clear_field_error(self, name: str) -> None:
        """Clear error for field."""
        if name in self._error_labels:
            self._error_labels[name].hide()

        if name in self._widgets:
            self._widgets[name].setProperty("hasError", False)
            self._widgets[name].style().unpolish(self._widgets[name])
            self._widgets[name].style().polish(self._widgets[name])

    def _clear_all_errors(self) -> None:
        """Clear all field errors."""
        for name in self._fields:
            self._clear_field_error(name)

    def get_errors(self) -> Dict[str, str]:
        """Get all current validation errors."""
        errors = {}
        for name, label in self._error_labels.items():
            if label.isVisible():
                errors[name] = label.text()
        return errors

    # =========================================================================
    # READONLY STATE
    # =========================================================================

    def set_readonly(self, readonly: bool = True) -> None:
        """
        Set form ke readonly mode.

        Args:
            readonly: True untuk readonly, False untuk editable
        """
        self._readonly = readonly

        for widget in self._widgets.values():
            self._set_widget_readonly(widget, readonly)

        # Hide buttons in readonly mode
        if self._show_buttons:
            self._btn_submit.setVisible(not readonly)
            self._btn_cancel.setText("Tutup" if readonly else "Batal")

    def _set_widget_readonly(self, widget: QWidget, readonly: bool) -> None:
        """Set individual widget readonly state."""
        if isinstance(widget, (QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox)):
            widget.setReadOnly(readonly)
        elif isinstance(widget, (QComboBox, QCheckBox, QDateEdit, QTimeEdit, QDateTimeEdit)):
            widget.setEnabled(not readonly)

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def _on_submit(self) -> None:
        """Handle submit button click."""
        if self.validate():
            self.form_submitted.emit(self.get_values())

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.form_cancelled.emit()

    # =========================================================================
    # WIDGET ACCESS
    # =========================================================================

    def get_widget(self, name: str) -> Optional[QWidget]:
        """
        Get widget instance by field name.

        Args:
            name: Nama field

        Returns:
            Widget instance atau None
        """
        return self._widgets.get(name)

    def get_field_definition(self, name: str) -> Optional[FormField]:
        """
        Get field definition by name.

        Args:
            name: Nama field

        Returns:
            FormField instance atau None
        """
        return self._fields.get(name)

    @property
    def field_names(self) -> List[str]:
        """Get list of all field names."""
        return list(self._fields.keys())

    @property
    def is_valid(self) -> bool:
        """Check if form is currently valid."""
        return self._is_valid


# =============================================================================
# FORM BUILDER UTILITY
# =============================================================================

class FormBuilder:
    """
    Builder pattern untuk membuat BaseFormWidget dengan fluent API.

    Example:
        form = (FormBuilder()
            .add_text('nama', 'Nama Lengkap', required=True)
            .add_number('umur', 'Umur', min_value=0, max_value=150)
            .add_combo('status', 'Status', options=[('active', 'Aktif')])
            .add_date('tanggal', 'Tanggal')
            .build())
    """

    def __init__(
        self,
        use_scroll: bool = False,
        show_buttons: bool = False,
        parent: Optional[QWidget] = None
    ):
        self._fields: List[FormField] = []
        self._use_scroll = use_scroll
        self._show_buttons = show_buttons
        self._parent = parent

    def add_text(
        self,
        name: str,
        label: str,
        required: bool = False,
        validators: Optional[List[Callable]] = None,
        placeholder: str = "",
        group: str = "",
        **kwargs
    ) -> 'FormBuilder':
        """Add text field."""
        self._fields.append(FormField(
            name=name,
            label=label,
            field_type=FieldType.TEXT,
            required=required,
            validators=validators or [],
            placeholder=placeholder,
            group=group,
            **kwargs
        ))
        return self

    def add_password(
        self,
        name: str,
        label: str,
        required: bool = False,
        **kwargs
    ) -> 'FormBuilder':
        """Add password field."""
        self._fields.append(FormField(
            name=name,
            label=label,
            field_type=FieldType.PASSWORD,
            required=required,
            **kwargs
        ))
        return self

    def add_textarea(
        self,
        name: str,
        label: str,
        required: bool = False,
        row_span: int = 3,
        **kwargs
    ) -> 'FormBuilder':
        """Add textarea field."""
        self._fields.append(FormField(
            name=name,
            label=label,
            field_type=FieldType.TEXTAREA,
            required=required,
            row_span=row_span,
            **kwargs
        ))
        return self

    def add_number(
        self,
        name: str,
        label: str,
        required: bool = False,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        **kwargs
    ) -> 'FormBuilder':
        """Add integer number field."""
        self._fields.append(FormField(
            name=name,
            label=label,
            field_type=FieldType.NUMBER,
            required=required,
            min_value=min_value,
            max_value=max_value,
            **kwargs
        ))
        return self

    def add_decimal(
        self,
        name: str,
        label: str,
        required: bool = False,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        **kwargs
    ) -> 'FormBuilder':
        """Add decimal number field."""
        self._fields.append(FormField(
            name=name,
            label=label,
            field_type=FieldType.DECIMAL,
            required=required,
            min_value=min_value,
            max_value=max_value,
            **kwargs
        ))
        return self

    def add_currency(
        self,
        name: str,
        label: str,
        required: bool = False,
        **kwargs
    ) -> 'FormBuilder':
        """Add currency field (Rupiah)."""
        self._fields.append(FormField(
            name=name,
            label=label,
            field_type=FieldType.CURRENCY,
            required=required,
            min_value=0,
            **kwargs
        ))
        return self

    def add_date(
        self,
        name: str,
        label: str,
        required: bool = False,
        **kwargs
    ) -> 'FormBuilder':
        """Add date field."""
        self._fields.append(FormField(
            name=name,
            label=label,
            field_type=FieldType.DATE,
            required=required,
            **kwargs
        ))
        return self

    def add_time(
        self,
        name: str,
        label: str,
        required: bool = False,
        **kwargs
    ) -> 'FormBuilder':
        """Add time field."""
        self._fields.append(FormField(
            name=name,
            label=label,
            field_type=FieldType.TIME,
            required=required,
            **kwargs
        ))
        return self

    def add_datetime(
        self,
        name: str,
        label: str,
        required: bool = False,
        **kwargs
    ) -> 'FormBuilder':
        """Add datetime field."""
        self._fields.append(FormField(
            name=name,
            label=label,
            field_type=FieldType.DATETIME,
            required=required,
            **kwargs
        ))
        return self

    def add_combo(
        self,
        name: str,
        label: str,
        options: List[tuple],
        required: bool = False,
        **kwargs
    ) -> 'FormBuilder':
        """Add combo box field."""
        self._fields.append(FormField(
            name=name,
            label=label,
            field_type=FieldType.COMBO,
            required=required,
            options=options,
            **kwargs
        ))
        return self

    def add_checkbox(
        self,
        name: str,
        label: str,
        default_value: bool = False,
        **kwargs
    ) -> 'FormBuilder':
        """Add checkbox field."""
        self._fields.append(FormField(
            name=name,
            label=label,
            field_type=FieldType.CHECKBOX,
            default_value=default_value,
            **kwargs
        ))
        return self

    def add_field(self, field_def: FormField) -> 'FormBuilder':
        """Add custom field definition."""
        self._fields.append(field_def)
        return self

    def build(self) -> BaseFormWidget:
        """Build and return the form widget."""
        form = BaseFormWidget(
            parent=self._parent,
            use_scroll=self._use_scroll,
            show_buttons=self._show_buttons
        )
        form.add_fields(self._fields)
        return form
