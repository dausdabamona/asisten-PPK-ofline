"""
PPK DOCUMENT FACTORY - Base UI Components
=========================================
Base classes untuk UI widgets.

Classes:
    BaseManagerWidget: Base class untuk manager widgets dengan
                      loading state, signals, dan helper methods
    BasePage: Base class untuk page widgets dengan navigation,
              title management, dan loading state
    BaseFormWidget: Generic form builder dengan validation
    FormField: Definisi field untuk form
    FormBuilder: Fluent API untuk membuat form
"""

from app.ui.base.base_manager import BaseManagerWidget
from app.ui.base.base_page import BasePage
from app.ui.base.base_form import (
    BaseFormWidget,
    FormField,
    FormBuilder,
    FieldType,
    ValidationResult,
    # Validators
    required_validator,
    min_length_validator,
    max_length_validator,
    number_range_validator,
    regex_validator,
    email_validator,
    phone_validator,
    nip_validator,
    nik_validator,
    npwp_validator,
)
from app.ui.base.base_table import (
    BaseTableWidget,
    ColumnDef,
    ActionDef,
    # Formatters
    format_rupiah,
    format_date_id,
    format_datetime_id,
    format_boolean,
    format_status_badge,
    truncate_text,
)

__all__ = [
    # Base widgets
    'BaseManagerWidget',
    'BasePage',
    # Form
    'BaseFormWidget',
    'FormField',
    'FormBuilder',
    'FieldType',
    'ValidationResult',
    # Validators
    'required_validator',
    'min_length_validator',
    'max_length_validator',
    'number_range_validator',
    'regex_validator',
    'email_validator',
    'phone_validator',
    'nip_validator',
    'nik_validator',
    'npwp_validator',
    # Table
    'BaseTableWidget',
    'ColumnDef',
    'ActionDef',
    # Table formatters
    'format_rupiah',
    'format_date_id',
    'format_datetime_id',
    'format_boolean',
    'format_status_badge',
    'truncate_text',
]
