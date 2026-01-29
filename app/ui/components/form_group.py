"""
PPK DOCUMENT FACTORY - Form Group Components
============================================
Components untuk mengelompokkan form fields:
- FormGroup: Label + Input + Error
- FormSection: Titled section dengan multiple groups
- FormBuilder: Fluent API untuk membangun form

Author: PPK Document Factory Team
Version: 4.0
"""

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field

from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QDateEdit, QCheckBox, QGroupBox, QPushButton,
    QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QDate

from .validated_inputs import (
    ValidatedLineEdit,
    ValidatedSpinBox,
    ValidatedCurrencySpinBox,
    ValidatedComboBox,
    ValidatedDateEdit,
    ValidatedTextEdit,
    ValidationMixin,
    required,
    min_length,
    max_length,
    email,
)


# =============================================================================
# FORM GROUP
# =============================================================================

class FormGroup(QWidget):
    """
    Widget yang mengelompokkan label + input + error message.

    Structure:
    - Label (dengan * merah jika required)
    - Help text (optional, italic)
    - Input widget
    - Error message (hidden by default)

    Usage:
        input_widget = ValidatedLineEdit()
        group = FormGroup("Nama Lengkap", input_widget, required=True)
        group.set_error("Nama wajib diisi")
    """

    value_changed = Signal(object)

    def __init__(
        self,
        label: str,
        widget: QWidget,
        required: bool = False,
        help_text: Optional[str] = None,
        parent=None
    ):
        """
        Initialize form group.

        Args:
            label: Label text
            widget: Input widget
            required: Show required indicator
            help_text: Optional help text below label
            parent: Parent widget
        """
        super().__init__(parent)

        self._label_text = label
        self._widget = widget
        self._required = required
        self._help_text = help_text
        self._name = ""  # Set by FormSection

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(4)

        # Label with required indicator
        label_layout = QHBoxLayout()
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(4)

        self._label = QLabel(self._label_text)
        self._label.setStyleSheet("""
            font-weight: 500;
            color: #2c3e50;
        """)
        label_layout.addWidget(self._label)

        if self._required:
            required_indicator = QLabel("*")
            required_indicator.setStyleSheet("color: #e74c3c; font-weight: bold;")
            label_layout.addWidget(required_indicator)

        label_layout.addStretch()
        layout.addLayout(label_layout)

        # Help text
        if self._help_text:
            help_label = QLabel(self._help_text)
            help_label.setStyleSheet("""
                font-style: italic;
                font-size: 11px;
                color: #6c757d;
            """)
            help_label.setWordWrap(True)
            layout.addWidget(help_label)

        # Input widget
        layout.addWidget(self._widget)

        # Error label (hidden by default)
        self._error_label = QLabel()
        self._error_label.setStyleSheet("""
            color: #e74c3c;
            font-size: 11px;
        """)
        self._error_label.hide()
        layout.addWidget(self._error_label)

    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Try to connect value change signals
        if hasattr(self._widget, 'textChanged'):
            self._widget.textChanged.connect(lambda: self.value_changed.emit(self.get_value()))
        elif hasattr(self._widget, 'valueChanged'):
            self._widget.valueChanged.connect(lambda: self.value_changed.emit(self.get_value()))
        elif hasattr(self._widget, 'currentIndexChanged'):
            self._widget.currentIndexChanged.connect(lambda: self.value_changed.emit(self.get_value()))
        elif hasattr(self._widget, 'dateChanged'):
            self._widget.dateChanged.connect(lambda: self.value_changed.emit(self.get_value()))
        elif hasattr(self._widget, 'stateChanged'):
            self._widget.stateChanged.connect(lambda: self.value_changed.emit(self.get_value()))

    def set_error(self, message: str) -> None:
        """
        Show error message.

        Args:
            message: Error message to display
        """
        self._error_label.setText(message)
        self._error_label.show()

        # Apply error style to widget if it supports it
        if hasattr(self._widget, '_apply_error_style'):
            self._widget._apply_error_style()

    def clear_error(self) -> None:
        """Clear error message."""
        self._error_label.hide()
        self._error_label.setText("")

        # Clear error style
        if hasattr(self._widget, '_apply_normal_style'):
            self._widget._apply_normal_style()
        if hasattr(self._widget, 'clear_error'):
            self._widget.clear_error()

    def set_value(self, value: Any) -> None:
        """
        Set widget value.

        Args:
            value: Value to set
        """
        if isinstance(self._widget, QLineEdit):
            self._widget.setText(str(value) if value is not None else "")
        elif isinstance(self._widget, (QTextEdit, ValidatedTextEdit)):
            if hasattr(self._widget, 'setPlainText'):
                self._widget.setPlainText(str(value) if value is not None else "")
            else:
                self._widget.setText(str(value) if value is not None else "")
        elif isinstance(self._widget, (QSpinBox, QDoubleSpinBox)):
            self._widget.setValue(float(value) if value is not None else 0)
        elif isinstance(self._widget, QComboBox):
            idx = self._widget.findData(value)
            if idx >= 0:
                self._widget.setCurrentIndex(idx)
            elif isinstance(value, str):
                self._widget.setCurrentText(value)
        elif isinstance(self._widget, QDateEdit):
            if value:
                if isinstance(value, str):
                    self._widget.setDate(QDate.fromString(value, "yyyy-MM-dd"))
                elif isinstance(value, QDate):
                    self._widget.setDate(value)
                elif hasattr(value, 'year'):
                    self._widget.setDate(QDate(value.year, value.month, value.day))
        elif isinstance(self._widget, QCheckBox):
            self._widget.setChecked(bool(value))

    def get_value(self) -> Any:
        """
        Get widget value.

        Returns:
            Current value
        """
        if isinstance(self._widget, QLineEdit):
            return self._widget.text().strip()
        elif isinstance(self._widget, (QTextEdit, ValidatedTextEdit)):
            if hasattr(self._widget, 'toPlainText'):
                return self._widget.toPlainText().strip()
            return ""
        elif isinstance(self._widget, (QSpinBox, QDoubleSpinBox)):
            return self._widget.value()
        elif isinstance(self._widget, QComboBox):
            return self._widget.currentData()
        elif isinstance(self._widget, QDateEdit):
            return self._widget.date().toPython()
        elif isinstance(self._widget, QCheckBox):
            return self._widget.isChecked()
        return None

    def set_enabled(self, enabled: bool) -> None:
        """
        Set enabled state.

        Args:
            enabled: True to enable
        """
        self._widget.setEnabled(enabled)

    def validate(self) -> bool:
        """
        Validate widget if it supports validation.

        Returns:
            True if valid or no validation
        """
        # Check if widget has our ValidationMixin (has _is_valid attribute)
        if hasattr(self._widget, '_is_valid') and hasattr(self._widget, 'validate'):
            try:
                is_valid = self._widget.validate()
                if not is_valid and hasattr(self._widget, 'get_error'):
                    self.set_error(self._widget.get_error())
                else:
                    self.clear_error()
                return is_valid
            except TypeError:
                # validate() has different signature, skip
                pass

        # If required but widget doesn't support validation
        if self._required:
            value = self.get_value()
            if value is None or (isinstance(value, str) and not value.strip()):
                self.set_error("Field ini wajib diisi")
                return False

        return True

    @property
    def widget(self) -> QWidget:
        """Get the input widget."""
        return self._widget

    @property
    def name(self) -> str:
        """Get field name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set field name."""
        self._name = value


# =============================================================================
# FORM SECTION
# =============================================================================

class FormSection(QFrame):
    """
    Section dengan title untuk mengelompokkan FormGroups.

    Usage:
        section = FormSection("Data Transaksi")
        section.add_row("nama", "Nama Paket", ValidatedLineEdit(), required=True)
        section.add_row("nilai", "Nilai", ValidatedCurrencySpinBox())

        values = section.get_values()
        section.set_values({'nama': 'Test', 'nilai': 1000000})
    """

    def __init__(
        self,
        title: str,
        collapsible: bool = False,
        parent=None
    ):
        """
        Initialize form section.

        Args:
            title: Section title
            collapsible: Allow collapsing section
            parent: Parent widget
        """
        super().__init__(parent)

        self._title = title
        self._collapsible = collapsible
        self._groups: Dict[str, FormGroup] = {}
        self._is_collapsed = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        self.setObjectName("formSection")
        self.setStyleSheet("""
            QFrame#formSection {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(8)

        # Title header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        self._title_label = QLabel(self._title)
        self._title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(self._title_label)

        header_layout.addStretch()

        if self._collapsible:
            self._toggle_btn = QPushButton("▼")
            self._toggle_btn.setFixedSize(24, 24)
            self._toggle_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    color: #6c757d;
                }
                QPushButton:hover {
                    color: #2c3e50;
                }
            """)
            self._toggle_btn.clicked.connect(self._toggle_collapse)
            header_layout.addWidget(self._toggle_btn)

        layout.addLayout(header_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #e9ecef;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Content container
        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 8, 0, 0)
        self._content_layout.setSpacing(4)
        layout.addWidget(self._content)

    def _toggle_collapse(self) -> None:
        """Toggle section collapse state."""
        self._is_collapsed = not self._is_collapsed
        self._content.setVisible(not self._is_collapsed)
        self._toggle_btn.setText("▶" if self._is_collapsed else "▼")

    def add_group(self, name: str, form_group: FormGroup) -> FormGroup:
        """
        Add existing FormGroup to section.

        Args:
            name: Field name (key)
            form_group: FormGroup instance

        Returns:
            The added FormGroup
        """
        form_group.name = name
        self._groups[name] = form_group
        self._content_layout.addWidget(form_group)
        return form_group

    def add_row(
        self,
        name: str,
        label: str,
        widget: QWidget,
        required: bool = False,
        help_text: Optional[str] = None
    ) -> FormGroup:
        """
        Add new row to section.

        Args:
            name: Field name (key)
            label: Label text
            widget: Input widget
            required: Is field required
            help_text: Optional help text

        Returns:
            Created FormGroup
        """
        group = FormGroup(label, widget, required, help_text)
        return self.add_group(name, group)

    def get_values(self) -> Dict[str, Any]:
        """
        Get all field values.

        Returns:
            Dictionary of {name: value}
        """
        return {name: group.get_value() for name, group in self._groups.items()}

    def set_values(self, data: Dict[str, Any]) -> None:
        """
        Set multiple field values.

        Args:
            data: Dictionary of {name: value}
        """
        for name, value in data.items():
            if name in self._groups:
                self._groups[name].set_value(value)

    def validate_all(self) -> bool:
        """
        Validate all fields.

        Returns:
            True if all fields are valid
        """
        all_valid = True
        for group in self._groups.values():
            if not group.validate():
                all_valid = False
        return all_valid

    def get_group(self, name: str) -> Optional[FormGroup]:
        """Get FormGroup by name."""
        return self._groups.get(name)

    def clear_errors(self) -> None:
        """Clear all errors."""
        for group in self._groups.values():
            group.clear_error()


# =============================================================================
# FORM BUILDER
# =============================================================================

@dataclass
class FieldDefinition:
    """Definition for a form field."""
    name: str
    label: str
    field_type: str
    required: bool = False
    help_text: Optional[str] = None
    validators: List[Callable] = field(default_factory=list)
    options: List[tuple] = field(default_factory=list)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    max_length: Optional[int] = None
    placeholder: str = ""
    default_value: Any = None


class FormBuilder:
    """
    Fluent API untuk membangun form.

    Usage:
        form = (FormBuilder()
            .add_section("Data Transaksi")
            .add_text("nama", "Nama Paket", required=True)
            .add_currency("nilai", "Nilai (Rp)", min_value=0)
            .add_section("Waktu")
            .add_date("tanggal", "Tanggal")
            .build())

        values = form.get_values()
        form.set_values({'nama': 'Test'})
    """

    def __init__(self):
        """Initialize form builder."""
        self._sections: List[tuple] = []  # [(title, [FieldDefinition, ...])]
        self._current_section: Optional[str] = None
        self._current_fields: List[FieldDefinition] = []
        self._use_scroll = False
        self._show_buttons = False

    def add_section(self, title: str) -> 'FormBuilder':
        """
        Add new section.

        Args:
            title: Section title

        Returns:
            Self for chaining
        """
        # Save current section
        if self._current_section is not None:
            self._sections.append((self._current_section, self._current_fields))

        self._current_section = title
        self._current_fields = []
        return self

    def add_text(
        self,
        name: str,
        label: str,
        required: bool = False,
        help_text: Optional[str] = None,
        validators: Optional[List[Callable]] = None,
        placeholder: str = "",
        default_value: Any = None
    ) -> 'FormBuilder':
        """Add text input field."""
        self._current_fields.append(FieldDefinition(
            name=name,
            label=label,
            field_type="text",
            required=required,
            help_text=help_text,
            validators=validators or [],
            placeholder=placeholder,
            default_value=default_value
        ))
        return self

    def add_password(
        self,
        name: str,
        label: str,
        required: bool = False,
        help_text: Optional[str] = None
    ) -> 'FormBuilder':
        """Add password input field."""
        self._current_fields.append(FieldDefinition(
            name=name,
            label=label,
            field_type="password",
            required=required,
            help_text=help_text
        ))
        return self

    def add_number(
        self,
        name: str,
        label: str,
        required: bool = False,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        help_text: Optional[str] = None,
        default_value: Any = None
    ) -> 'FormBuilder':
        """Add number input field."""
        self._current_fields.append(FieldDefinition(
            name=name,
            label=label,
            field_type="number",
            required=required,
            min_value=min_value,
            max_value=max_value,
            help_text=help_text,
            default_value=default_value
        ))
        return self

    def add_currency(
        self,
        name: str,
        label: str,
        required: bool = False,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        help_text: Optional[str] = None,
        default_value: Any = None
    ) -> 'FormBuilder':
        """Add currency (Rupiah) input field."""
        self._current_fields.append(FieldDefinition(
            name=name,
            label=label,
            field_type="currency",
            required=required,
            min_value=min_value,
            max_value=max_value,
            help_text=help_text,
            default_value=default_value
        ))
        return self

    def add_date(
        self,
        name: str,
        label: str,
        required: bool = False,
        help_text: Optional[str] = None,
        default_value: Any = None
    ) -> 'FormBuilder':
        """Add date input field."""
        self._current_fields.append(FieldDefinition(
            name=name,
            label=label,
            field_type="date",
            required=required,
            help_text=help_text,
            default_value=default_value
        ))
        return self

    def add_combo(
        self,
        name: str,
        label: str,
        options: List[tuple],
        required: bool = False,
        help_text: Optional[str] = None,
        default_value: Any = None
    ) -> 'FormBuilder':
        """
        Add combo box field.

        Args:
            name: Field name
            label: Label text
            options: List of (value, label) tuples
            required: Is required
            help_text: Help text
            default_value: Default selection value

        Returns:
            Self for chaining
        """
        self._current_fields.append(FieldDefinition(
            name=name,
            label=label,
            field_type="combo",
            options=options,
            required=required,
            help_text=help_text,
            default_value=default_value
        ))
        return self

    def add_textarea(
        self,
        name: str,
        label: str,
        required: bool = False,
        max_length: Optional[int] = None,
        help_text: Optional[str] = None,
        default_value: Any = None
    ) -> 'FormBuilder':
        """Add textarea field."""
        self._current_fields.append(FieldDefinition(
            name=name,
            label=label,
            field_type="textarea",
            required=required,
            max_length=max_length,
            help_text=help_text,
            default_value=default_value
        ))
        return self

    def add_checkbox(
        self,
        name: str,
        label: str,
        default_value: bool = False,
        help_text: Optional[str] = None
    ) -> 'FormBuilder':
        """Add checkbox field."""
        self._current_fields.append(FieldDefinition(
            name=name,
            label=label,
            field_type="checkbox",
            default_value=default_value,
            help_text=help_text
        ))
        return self

    def use_scroll(self, scroll: bool = True) -> 'FormBuilder':
        """Enable scroll area."""
        self._use_scroll = scroll
        return self

    def build(self) -> 'BuiltForm':
        """
        Build and return the form widget.

        Returns:
            BuiltForm widget with get_values(), set_values(), validate() methods
        """
        # Save last section
        if self._current_section is not None:
            self._sections.append((self._current_section, self._current_fields))
        elif self._current_fields:
            # No section defined, use default
            self._sections.append(("", self._current_fields))

        return BuiltForm(self._sections, self._use_scroll)


class BuiltForm(QWidget):
    """
    Form widget built by FormBuilder.

    Provides:
    - get_values(): Get all field values
    - set_values(data): Set field values
    - validate(): Validate all fields
    - get_section(title): Get FormSection by title
    """

    def __init__(self, sections: List[tuple], use_scroll: bool = False):
        """
        Initialize built form.

        Args:
            sections: List of (title, [FieldDefinition, ...])
            use_scroll: Wrap in scroll area
        """
        super().__init__()

        self._sections: Dict[str, FormSection] = {}
        self._groups: Dict[str, FormGroup] = {}

        self._setup_ui(sections, use_scroll)

    def _setup_ui(self, sections: List[tuple], use_scroll: bool) -> None:
        """Setup UI from section definitions."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # Container
        if use_scroll:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)

            container = QWidget()
            content_layout = QVBoxLayout(container)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(16)

            scroll.setWidget(container)
            main_layout.addWidget(scroll)
        else:
            content_layout = main_layout

        # Create sections
        for title, fields in sections:
            if title:
                section = FormSection(title)
            else:
                # No title, use simple container
                section = FormSection("")
                section._title_label.hide()

            # Add fields
            for field_def in fields:
                widget = self._create_widget(field_def)
                group = section.add_row(
                    field_def.name,
                    field_def.label,
                    widget,
                    field_def.required,
                    field_def.help_text
                )

                # Set default value
                if field_def.default_value is not None:
                    group.set_value(field_def.default_value)

                # Store reference
                self._groups[field_def.name] = group

            self._sections[title] = section
            content_layout.addWidget(section)

        content_layout.addStretch()

    def _create_widget(self, field_def: FieldDefinition) -> QWidget:
        """Create widget from field definition."""
        widget: QWidget

        if field_def.field_type == "text":
            widget = ValidatedLineEdit()
            if field_def.placeholder:
                widget.setPlaceholderText(field_def.placeholder)
            if field_def.required:
                widget.set_required(True)
            for validator in field_def.validators:
                widget.add_validator(validator)

        elif field_def.field_type == "password":
            widget = ValidatedLineEdit()
            widget.setEchoMode(QLineEdit.EchoMode.Password)
            if field_def.required:
                widget.set_required(True)

        elif field_def.field_type == "number":
            widget = ValidatedSpinBox()
            if field_def.min_value is not None:
                widget.setMinimum(int(field_def.min_value))
            if field_def.max_value is not None:
                widget.setMaximum(int(field_def.max_value))
            if field_def.required:
                widget.set_required(True)

        elif field_def.field_type == "currency":
            widget = ValidatedCurrencySpinBox()
            if field_def.min_value is not None:
                widget.setMinimum(field_def.min_value)
            if field_def.max_value is not None:
                widget.setMaximum(field_def.max_value)
            if field_def.required:
                widget.set_required(True)

        elif field_def.field_type == "date":
            widget = ValidatedDateEdit()
            if field_def.required:
                widget.set_required(True)

        elif field_def.field_type == "combo":
            widget = ValidatedComboBox()
            if field_def.required:
                widget.add_placeholder()
                widget.set_required(True)
            for value, label in field_def.options:
                widget.addItem(label, value)

        elif field_def.field_type == "textarea":
            widget = ValidatedTextEdit(
                max_length=field_def.max_length,
                show_counter=field_def.max_length is not None
            )
            widget.setMaximumHeight(100)
            if field_def.required:
                widget.set_required(True)

        elif field_def.field_type == "checkbox":
            widget = QCheckBox()

        else:
            widget = QLineEdit()

        return widget

    def get_values(self) -> Dict[str, Any]:
        """
        Get all field values.

        Returns:
            Dictionary of {name: value}
        """
        return {name: group.get_value() for name, group in self._groups.items()}

    def set_values(self, data: Dict[str, Any]) -> None:
        """
        Set field values.

        Args:
            data: Dictionary of {name: value}
        """
        for name, value in data.items():
            if name in self._groups:
                self._groups[name].set_value(value)

    def validate(self) -> bool:
        """
        Validate all fields.

        Returns:
            True if all valid
        """
        all_valid = True
        for group in self._groups.values():
            if not group.validate():
                all_valid = False
        return all_valid

    def get_section(self, title: str) -> Optional[FormSection]:
        """Get FormSection by title."""
        return self._sections.get(title)

    def get_group(self, name: str) -> Optional[FormGroup]:
        """Get FormGroup by name."""
        return self._groups.get(name)

    def clear_errors(self) -> None:
        """Clear all validation errors."""
        for group in self._groups.values():
            group.clear_error()

    def clear(self) -> None:
        """Clear all field values."""
        for group in self._groups.values():
            group.set_value(None)
        self.clear_errors()
