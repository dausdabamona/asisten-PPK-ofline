"""
PPK Document Factory - Error Boundary System
============================================
Graceful error handling for UI components.

Features:
- ErrorBoundary: Wraps widgets with error handling
- ErrorFallback: Default error display widget
- Global error handler
- Decorators for method error handling

Example Usage:
-------------
```python
# Wrap a widget
boundary = ErrorBoundary(self.content_widget)
boundary.error_occurred.connect(self._log_error)
boundary.retry_requested.connect(self._reload)

# Trigger error display
try:
    self.load_data()
except Exception as e:
    boundary.show_error(str(e), traceback.format_exc())

# Using decorator
@catch_errors(fallback=None, show_toast=True)
def risky_operation(self):
    pass
```
"""

from typing import Any, Callable, Optional
from functools import wraps
import traceback
import sys
import logging

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QTextEdit, QStackedWidget, QSizePolicy,
    QApplication, QScrollArea
)
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

logger = logging.getLogger(__name__)


# =============================================================================
# ERROR FALLBACK WIDGET
# =============================================================================


class ErrorFallback(QFrame):
    """
    Default error display widget.

    Shows error message with optional details, retry and report buttons.

    Signals:
        retry_clicked: Emitted when retry button is clicked
        report_clicked: Emitted when report button is clicked
    """

    retry_clicked = Signal()
    report_clicked = Signal()

    def __init__(
        self,
        error_message: str = "Terjadi kesalahan",
        details: Optional[str] = None,
        show_retry: bool = True,
        show_report: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self._error_message = error_message
        self._details = details
        self._show_retry = show_retry
        self._show_report = show_report

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the error display UI."""
        self.setObjectName("ErrorFallback")
        self.setStyleSheet("""
            #ErrorFallback {
                background-color: #fff8f8;
                border: 1px solid #f5c6cb;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Error icon
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Error message
        message_label = QLabel(self._error_message)
        message_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #721c24;
        """)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # Details (collapsible)
        if self._details:
            self._details_widget = self._create_details_widget()
            layout.addWidget(self._details_widget)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self._show_retry:
            retry_btn = QPushButton("🔄 Coba Lagi")
            retry_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 10px 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            retry_btn.clicked.connect(self.retry_clicked.emit)
            buttons_layout.addWidget(retry_btn)

        if self._show_report:
            report_btn = QPushButton("📝 Laporkan Bug")
            report_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 10px 24px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            report_btn.clicked.connect(self.report_clicked.emit)
            buttons_layout.addWidget(report_btn)

        layout.addLayout(buttons_layout)

    def _create_details_widget(self) -> QWidget:
        """Create collapsible details widget."""
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Toggle button
        toggle_btn = QPushButton("▶ Lihat Detail")
        toggle_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #666;
                text-align: left;
                padding: 4px;
            }
            QPushButton:hover {
                color: #333;
            }
        """)
        layout.addWidget(toggle_btn)

        # Details text
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_text.setPlainText(self._details)
        details_text.setMaximumHeight(150)
        details_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-family: monospace;
                font-size: 11px;
                color: #666;
            }
        """)
        details_text.setVisible(False)
        layout.addWidget(details_text)

        # Toggle visibility
        def toggle():
            visible = not details_text.isVisible()
            details_text.setVisible(visible)
            toggle_btn.setText("▼ Sembunyikan Detail" if visible else "▶ Lihat Detail")

        toggle_btn.clicked.connect(toggle)

        return container

    def set_error(self, message: str, details: Optional[str] = None) -> None:
        """Update error message and details."""
        self._error_message = message
        self._details = details
        # Would need to recreate UI or update labels


# =============================================================================
# ERROR BOUNDARY
# =============================================================================


class ErrorBoundary(QStackedWidget):
    """
    Widget wrapper that provides error handling and fallback display.

    Wraps a child widget and shows an error fallback when an error occurs.

    Signals:
        error_occurred(str): Emitted when an error is shown
        retry_requested(): Emitted when user clicks retry

    Example:
    --------
    ```python
    # Wrap a widget
    content = ContentWidget()
    boundary = ErrorBoundary(content)

    # Show error
    try:
        boundary.child.load_data()
    except Exception as e:
        boundary.show_error(str(e), traceback.format_exc())

    # Connect to retry
    boundary.retry_requested.connect(self.reload_data)
    ```
    """

    error_occurred = Signal(str)
    retry_requested = Signal()

    def __init__(
        self,
        child_widget: Optional[QWidget] = None,
        fallback_widget: Optional[QWidget] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self._child_widget = child_widget
        self._fallback_widget = fallback_widget
        self._error_message = ""
        self._error_details = ""

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the stacked widget."""
        # Add child widget (index 0)
        if self._child_widget:
            self.addWidget(self._child_widget)
        else:
            # Placeholder
            placeholder = QWidget()
            self.addWidget(placeholder)

        # Add/create fallback widget (index 1)
        if self._fallback_widget:
            self.addWidget(self._fallback_widget)
        else:
            self._fallback_widget = ErrorFallback()
            self._fallback_widget.retry_clicked.connect(self._on_retry)
            self.addWidget(self._fallback_widget)

        # Show child by default
        self.setCurrentIndex(0)

    def _on_retry(self) -> None:
        """Handle retry button click."""
        self.show_child()
        self.retry_requested.emit()

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def set_child(self, widget: QWidget) -> None:
        """
        Set or replace the child widget.

        Args:
            widget: New child widget
        """
        if self._child_widget:
            self.removeWidget(self._child_widget)
            self._child_widget.deleteLater()

        self._child_widget = widget
        self.insertWidget(0, widget)
        self.setCurrentIndex(0)

    def set_fallback(self, widget: QWidget) -> None:
        """
        Set custom fallback widget.

        Args:
            widget: Custom fallback widget
        """
        old_fallback = self._fallback_widget
        self._fallback_widget = widget
        self.insertWidget(1, widget)

        if old_fallback:
            self.removeWidget(old_fallback)
            old_fallback.deleteLater()

    def show_error(
        self,
        error: str,
        details: Optional[str] = None
    ) -> None:
        """
        Show error fallback.

        Args:
            error: Error message to display
            details: Optional detailed error info (stack trace)
        """
        self._error_message = error
        self._error_details = details or ""

        # Update fallback widget if it's ErrorFallback
        if isinstance(self._fallback_widget, ErrorFallback):
            # Recreate with new error
            self.removeWidget(self._fallback_widget)
            self._fallback_widget.deleteLater()

            self._fallback_widget = ErrorFallback(
                error_message=error,
                details=details,
                show_retry=True
            )
            self._fallback_widget.retry_clicked.connect(self._on_retry)
            self.addWidget(self._fallback_widget)

        self.setCurrentIndex(1)  # Show fallback
        self.error_occurred.emit(error)

        logger.error(f"ErrorBoundary: {error}")
        if details:
            logger.debug(f"Details: {details}")

    def show_child(self) -> None:
        """Show the child widget (hide error)."""
        self.setCurrentIndex(0)

    def retry(self) -> None:
        """Programmatically trigger retry."""
        self._on_retry()

    @property
    def child(self) -> Optional[QWidget]:
        """Get the child widget."""
        return self._child_widget

    @property
    def is_showing_error(self) -> bool:
        """Check if currently showing error."""
        return self.currentIndex() == 1


# =============================================================================
# GLOBAL ERROR HANDLER
# =============================================================================


class GlobalErrorHandler(QObject):
    """
    Global error handler for uncaught exceptions.

    Handles exceptions that aren't caught elsewhere, logs them,
    and optionally shows notifications.

    Usage:
    ------
    ```python
    # Setup at application start
    GlobalErrorHandler.install()

    # Or handle manually
    GlobalErrorHandler.handle(exception, context="loading data")
    ```
    """

    _instance: Optional['GlobalErrorHandler'] = None
    error_handled = Signal(str, str)  # message, details

    def __init__(self):
        super().__init__()
        self._error_log: list = []
        self._show_toast = True
        self._max_log_size = 100

    @classmethod
    def instance(cls) -> 'GlobalErrorHandler':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def install(cls) -> None:
        """
        Install global exception handler.

        Replaces sys.excepthook to catch unhandled exceptions.
        """
        instance = cls.instance()
        sys.excepthook = instance._exception_hook
        logger.info("Global error handler installed")

    @classmethod
    def handle(
        cls,
        error: Exception,
        context: Optional[str] = None,
        show_toast: bool = True
    ) -> None:
        """
        Handle an error.

        Args:
            error: The exception
            context: Optional context description
            show_toast: Whether to show toast notification
        """
        instance = cls.instance()
        instance._handle_error(error, context, show_toast)

    def _exception_hook(
        self,
        exc_type,
        exc_value,
        exc_tb
    ) -> None:
        """System exception hook."""
        # Don't handle KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return

        # Format traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        tb_text = ''.join(tb_lines)

        self._handle_error(exc_value, None, self._show_toast, tb_text)

    def _handle_error(
        self,
        error: Exception,
        context: Optional[str],
        show_toast: bool,
        tb_text: Optional[str] = None
    ) -> None:
        """Internal error handling."""
        error_msg = str(error)
        if context:
            error_msg = f"{context}: {error_msg}"

        if tb_text is None:
            tb_text = traceback.format_exc()

        # Log error
        logger.error(f"Unhandled error: {error_msg}")
        logger.debug(tb_text)

        # Store in log
        self._error_log.append({
            'message': error_msg,
            'details': tb_text,
            'type': type(error).__name__,
            'context': context
        })

        # Trim log
        if len(self._error_log) > self._max_log_size:
            self._error_log = self._error_log[-self._max_log_size:]

        # Emit signal
        self.error_handled.emit(error_msg, tb_text)

        # Show toast if enabled
        if show_toast:
            try:
                from .toast import ToastManager
                ToastManager.error(f"Error: {error_msg[:100]}")
            except ImportError:
                pass

    @property
    def error_log(self) -> list:
        """Get error log."""
        return self._error_log.copy()

    def clear_log(self) -> None:
        """Clear error log."""
        self._error_log.clear()

    def set_show_toast(self, enabled: bool) -> None:
        """Enable/disable toast notifications for errors."""
        self._show_toast = enabled


# =============================================================================
# DECORATORS
# =============================================================================


def catch_errors(
    fallback: Any = None,
    show_toast: bool = True,
    reraise: bool = False,
    on_error: Optional[Callable[[Exception], None]] = None
):
    """
    Decorator for catching and handling errors in methods.

    Args:
        fallback: Value to return on error (default None)
        show_toast: Show toast notification on error
        reraise: Re-raise exception after handling
        on_error: Callback function called with exception

    Example:
    --------
    ```python
    @catch_errors(fallback=[], show_toast=True)
    def load_data(self):
        return db.query()  # If fails, returns []

    @catch_errors(on_error=lambda e: logger.error(e))
    def risky_operation(self):
        pass
    ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log error
                error_msg = f"{func.__name__}: {str(e)}"
                logger.error(error_msg)
                logger.debug(traceback.format_exc())

                # Call error callback
                if on_error:
                    on_error(e)

                # Show toast
                if show_toast:
                    try:
                        from .toast import ToastManager
                        ToastManager.error(f"Error: {str(e)[:100]}")
                    except ImportError:
                        pass

                # Re-raise if requested
                if reraise:
                    raise

                return fallback

        return wrapper
    return decorator


def safe_slot(fallback: Any = None, show_toast: bool = True):
    """
    Decorator for Qt slots that should not crash on error.

    Similar to catch_errors but specifically for slots.

    Example:
    --------
    ```python
    @safe_slot()
    def on_button_clicked(self):
        self.load_data()  # Won't crash app on error
    ```
    """
    return catch_errors(fallback=fallback, show_toast=show_toast, reraise=False)


# =============================================================================
# CONTEXT MANAGER
# =============================================================================


class error_context:
    """
    Context manager for error handling.

    Example:
    --------
    ```python
    with error_context("loading data", show_toast=True):
        data = db.query()
    ```
    """

    def __init__(
        self,
        context: str,
        show_toast: bool = True,
        fallback: Any = None
    ):
        self.context = context
        self.show_toast = show_toast
        self.fallback = fallback
        self.error: Optional[Exception] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.error = exc_val
            GlobalErrorHandler.handle(
                exc_val,
                context=self.context,
                show_toast=self.show_toast
            )
            return True  # Suppress exception
        return False


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Widgets
    'ErrorFallback',
    'ErrorBoundary',

    # Global handler
    'GlobalErrorHandler',

    # Decorators
    'catch_errors',
    'safe_slot',

    # Context manager
    'error_context',
]
