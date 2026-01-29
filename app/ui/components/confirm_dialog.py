"""
PPK DOCUMENT FACTORY - Confirmation Dialog System
==================================================
Modern confirmation dialogs dengan:
- Multiple types: confirm, warning, danger, info
- Custom styling dengan rounded corners
- Shadow effect
- Input dialog support

Author: PPK Document Factory Team
Version: 4.0
"""

from enum import Enum
from typing import Optional, List, Any

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QDateEdit, QGraphicsDropShadowEffect,
    QSizePolicy, QFrame, QApplication
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor, QFont


# =============================================================================
# DIALOG TYPES
# =============================================================================

class DialogType(Enum):
    """Types of confirmation dialogs."""
    CONFIRM = "confirm"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"


# Dialog configuration per type
DIALOG_CONFIG = {
    DialogType.CONFIRM: {
        'icon': '\u2713',  # Checkmark
        'icon_color': '#3498db',
        'button_bg': '#3498db',
        'button_hover': '#2980b9',
        'button_text': '#ffffff',
    },
    DialogType.WARNING: {
        'icon': '\u26A0',  # Warning sign
        'icon_color': '#f39c12',
        'button_bg': '#f39c12',
        'button_hover': '#d68910',
        'button_text': '#ffffff',
    },
    DialogType.DANGER: {
        'icon': '\u26A0',  # Warning sign (exclamation)
        'icon_color': '#e74c3c',
        'button_bg': '#e74c3c',
        'button_hover': '#c0392b',
        'button_text': '#ffffff',
    },
    DialogType.INFO: {
        'icon': '\u2139',  # Info symbol
        'icon_color': '#3498db',
        'button_bg': '#3498db',
        'button_hover': '#2980b9',
        'button_text': '#ffffff',
    },
}


# =============================================================================
# CONFIRM DIALOG
# =============================================================================

class ConfirmDialog(QDialog):
    """
    Modern confirmation dialog.

    Features:
    - Multiple types (confirm, warning, danger, info)
    - Custom styling with rounded corners
    - Shadow effect
    - Icon based on type

    Usage:
        # Method 1: Instance
        dialog = ConfirmDialog(
            title="Hapus Data",
            message="Yakin ingin menghapus?",
            dialog_type=DialogType.DANGER,
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            self.delete_data()

        # Method 2: Class methods (recommended)
        if ConfirmDialog.danger("Hapus Data", "Yakin?", self):
            self.delete_data()
    """

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Ya",
        cancel_text: str = "Batal",
        dialog_type: DialogType = DialogType.CONFIRM,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize confirmation dialog.

        Args:
            title: Dialog title
            message: Message to display (can be multi-line)
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button
            dialog_type: Type of dialog (confirm, warning, danger, info)
            parent: Parent widget
        """
        super().__init__(parent)

        self._title = title
        self._message = message
        self._confirm_text = confirm_text
        self._cancel_text = cancel_text
        self._dialog_type = dialog_type

        self._setup_ui()
        self._apply_shadow()

    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        config = DIALOG_CONFIG[self._dialog_type]

        # Window settings
        self.setWindowTitle(self._title)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumWidth(350)
        self.setMaximumWidth(450)

        # Main container with rounded corners
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

        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        # Icon
        icon_label = QLabel(config['icon'])
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {config['icon_color']};
                font-size: 32px;
                font-weight: bold;
            }}
        """)
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)

        # Title and message
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)

        title_label = QLabel(self._title)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        text_layout.addWidget(title_label)

        message_label = QLabel(self._message)
        message_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
            }
        """)
        message_label.setWordWrap(True)
        text_layout.addWidget(message_label)

        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #ecf0f1;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        # Cancel button (secondary style)
        if self._cancel_text:
            cancel_btn = QPushButton(self._cancel_text)
            cancel_btn.setObjectName("cancelBtn")
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.setMinimumWidth(100)
            cancel_btn.setStyleSheet("""
                QPushButton#cancelBtn {
                    background-color: #ecf0f1;
                    color: #7f8c8d;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton#cancelBtn:hover {
                    background-color: #d5dbdb;
                }
                QPushButton#cancelBtn:pressed {
                    background-color: #bdc3c7;
                }
            """)
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)

        # Confirm button (primary style based on type)
        confirm_btn = QPushButton(self._confirm_text)
        confirm_btn.setObjectName("confirmBtn")
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setMinimumWidth(100)
        confirm_btn.setStyleSheet(f"""
            QPushButton#confirmBtn {{
                background-color: {config['button_bg']};
                color: {config['button_text']};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton#confirmBtn:hover {{
                background-color: {config['button_hover']};
            }}
            QPushButton#confirmBtn:pressed {{
                background-color: {config['button_hover']};
            }}
        """)
        confirm_btn.clicked.connect(self.accept)
        confirm_btn.setDefault(True)
        button_layout.addWidget(confirm_btn)

        layout.addLayout(button_layout)

    def _apply_shadow(self) -> None:
        """Apply drop shadow effect."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

    # -------------------------------------------------------------------------
    # Class methods for quick dialogs
    # -------------------------------------------------------------------------

    @classmethod
    def confirm(
        cls,
        title: str,
        message: str,
        parent: Optional[QWidget] = None,
        confirm_text: str = "Ya",
        cancel_text: str = "Batal"
    ) -> bool:
        """
        Show confirm dialog and return result.

        Args:
            title: Dialog title
            message: Message to display
            parent: Parent widget
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button

        Returns:
            True if confirmed, False otherwise
        """
        dialog = cls(
            title=title,
            message=message,
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            dialog_type=DialogType.CONFIRM,
            parent=parent
        )
        return dialog.exec() == QDialog.DialogCode.Accepted

    @classmethod
    def warning(
        cls,
        title: str,
        message: str,
        parent: Optional[QWidget] = None,
        confirm_text: str = "Ya",
        cancel_text: str = "Batal"
    ) -> bool:
        """
        Show warning dialog and return result.

        Args:
            title: Dialog title
            message: Message to display
            parent: Parent widget
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button

        Returns:
            True if confirmed, False otherwise
        """
        dialog = cls(
            title=title,
            message=message,
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            dialog_type=DialogType.WARNING,
            parent=parent
        )
        return dialog.exec() == QDialog.DialogCode.Accepted

    @classmethod
    def danger(
        cls,
        title: str,
        message: str,
        parent: Optional[QWidget] = None,
        confirm_text: str = "Ya, Hapus",
        cancel_text: str = "Batal"
    ) -> bool:
        """
        Show danger dialog and return result.

        Args:
            title: Dialog title
            message: Message to display
            parent: Parent widget
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button

        Returns:
            True if confirmed, False otherwise
        """
        dialog = cls(
            title=title,
            message=message,
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            dialog_type=DialogType.DANGER,
            parent=parent
        )
        return dialog.exec() == QDialog.DialogCode.Accepted

    @classmethod
    def info(
        cls,
        title: str,
        message: str,
        parent: Optional[QWidget] = None,
        confirm_text: str = "OK"
    ) -> None:
        """
        Show info dialog.

        Args:
            title: Dialog title
            message: Message to display
            parent: Parent widget
            confirm_text: Text for confirm button
        """
        dialog = cls(
            title=title,
            message=message,
            confirm_text=confirm_text,
            cancel_text="",  # No cancel button for info
            dialog_type=DialogType.INFO,
            parent=parent
        )
        dialog.exec()


# =============================================================================
# INPUT DIALOG
# =============================================================================

class InputType(Enum):
    """Types of input in InputDialog."""
    TEXT = "text"
    NUMBER = "number"
    FLOAT = "float"
    DATE = "date"
    COMBO = "combo"


class InputDialog(QDialog):
    """
    Dialog with single input field.

    Features:
    - Multiple input types (text, number, date, combo)
    - Validation support
    - Modern styling

    Usage:
        # Method 1: Instance
        dialog = InputDialog(
            title="Masukkan Nama",
            label="Nama:",
            input_type=InputType.TEXT,
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            name = dialog.get_value()

        # Method 2: Class method (recommended)
        name = InputDialog.get_text("Masukkan Nama", "Nama:", parent=self)
        if name is not None:
            print(f"Nama: {name}")
    """

    def __init__(
        self,
        title: str,
        label: str,
        default_value: Any = None,
        input_type: InputType = InputType.TEXT,
        options: Optional[List[str]] = None,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize input dialog.

        Args:
            title: Dialog title
            label: Label for input field
            default_value: Default value for input
            input_type: Type of input (text, number, date, combo)
            options: Options for combo input type
            parent: Parent widget
        """
        super().__init__(parent)

        self._title = title
        self._label = label
        self._default_value = default_value
        self._input_type = input_type
        self._options = options or []
        self._input_widget: Optional[QWidget] = None

        self._setup_ui()
        self._apply_shadow()

    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        # Window settings
        self.setWindowTitle(self._title)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumWidth(350)
        self.setMaximumWidth(450)

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

        # Title
        title_label = QLabel(self._title)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title_label)

        # Input label
        label = QLabel(self._label)
        label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
            }
        """)
        layout.addWidget(label)

        # Input widget based on type
        self._input_widget = self._create_input_widget()
        self._input_widget.setStyleSheet("""
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                color: #2c3e50;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
            QComboBox:focus, QDateEdit:focus {
                border-color: #3498db;
                background-color: #ffffff;
            }
        """)
        layout.addWidget(self._input_widget)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #ecf0f1;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("Batal")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton#cancelBtn {
                background-color: #ecf0f1;
                color: #7f8c8d;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton#cancelBtn:hover {
                background-color: #d5dbdb;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("okBtn")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setMinimumWidth(100)
        ok_btn.setStyleSheet("""
            QPushButton#okBtn {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton#okBtn:hover {
                background-color: #2980b9;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

    def _create_input_widget(self) -> QWidget:
        """Create input widget based on type."""
        if self._input_type == InputType.TEXT:
            widget = QLineEdit()
            if self._default_value:
                widget.setText(str(self._default_value))
            return widget

        elif self._input_type == InputType.NUMBER:
            widget = QSpinBox()
            widget.setRange(-999999999, 999999999)
            if self._default_value is not None:
                widget.setValue(int(self._default_value))
            return widget

        elif self._input_type == InputType.FLOAT:
            widget = QDoubleSpinBox()
            widget.setRange(-999999999.99, 999999999.99)
            widget.setDecimals(2)
            if self._default_value is not None:
                widget.setValue(float(self._default_value))
            return widget

        elif self._input_type == InputType.DATE:
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            if self._default_value:
                widget.setDate(self._default_value)
            else:
                widget.setDate(QDate.currentDate())
            return widget

        elif self._input_type == InputType.COMBO:
            widget = QComboBox()
            widget.addItems(self._options)
            if self._default_value and self._default_value in self._options:
                widget.setCurrentText(self._default_value)
            return widget

        else:
            return QLineEdit()

    def _apply_shadow(self) -> None:
        """Apply drop shadow effect."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

    def get_value(self) -> Any:
        """
        Get current input value.

        Returns:
            Input value (type depends on input_type)
        """
        if isinstance(self._input_widget, QLineEdit):
            return self._input_widget.text()
        elif isinstance(self._input_widget, QSpinBox):
            return self._input_widget.value()
        elif isinstance(self._input_widget, QDoubleSpinBox):
            return self._input_widget.value()
        elif isinstance(self._input_widget, QDateEdit):
            return self._input_widget.date()
        elif isinstance(self._input_widget, QComboBox):
            return self._input_widget.currentText()
        return None

    # -------------------------------------------------------------------------
    # Class methods for quick dialogs
    # -------------------------------------------------------------------------

    @classmethod
    def get_text(
        cls,
        title: str,
        label: str,
        default: str = "",
        parent: Optional[QWidget] = None
    ) -> Optional[str]:
        """
        Show text input dialog and return result.

        Args:
            title: Dialog title
            label: Input label
            default: Default value
            parent: Parent widget

        Returns:
            Entered text or None if cancelled
        """
        dialog = cls(
            title=title,
            label=label,
            default_value=default,
            input_type=InputType.TEXT,
            parent=parent
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_value()
        return None

    @classmethod
    def get_number(
        cls,
        title: str,
        label: str,
        default: int = 0,
        parent: Optional[QWidget] = None
    ) -> Optional[int]:
        """
        Show number input dialog and return result.

        Args:
            title: Dialog title
            label: Input label
            default: Default value
            parent: Parent widget

        Returns:
            Entered number or None if cancelled
        """
        dialog = cls(
            title=title,
            label=label,
            default_value=default,
            input_type=InputType.NUMBER,
            parent=parent
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_value()
        return None

    @classmethod
    def get_float(
        cls,
        title: str,
        label: str,
        default: float = 0.0,
        parent: Optional[QWidget] = None
    ) -> Optional[float]:
        """
        Show float input dialog and return result.

        Args:
            title: Dialog title
            label: Input label
            default: Default value
            parent: Parent widget

        Returns:
            Entered float or None if cancelled
        """
        dialog = cls(
            title=title,
            label=label,
            default_value=default,
            input_type=InputType.FLOAT,
            parent=parent
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_value()
        return None

    @classmethod
    def get_date(
        cls,
        title: str,
        label: str,
        default: Optional[QDate] = None,
        parent: Optional[QWidget] = None
    ) -> Optional[QDate]:
        """
        Show date input dialog and return result.

        Args:
            title: Dialog title
            label: Input label
            default: Default date
            parent: Parent widget

        Returns:
            Selected date or None if cancelled
        """
        dialog = cls(
            title=title,
            label=label,
            default_value=default or QDate.currentDate(),
            input_type=InputType.DATE,
            parent=parent
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_value()
        return None

    @classmethod
    def get_choice(
        cls,
        title: str,
        label: str,
        options: List[str],
        default: Optional[str] = None,
        parent: Optional[QWidget] = None
    ) -> Optional[str]:
        """
        Show combo input dialog and return result.

        Args:
            title: Dialog title
            label: Input label
            options: List of options
            default: Default selection
            parent: Parent widget

        Returns:
            Selected option or None if cancelled
        """
        dialog = cls(
            title=title,
            label=label,
            default_value=default,
            input_type=InputType.COMBO,
            options=options,
            parent=parent
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_value()
        return None
