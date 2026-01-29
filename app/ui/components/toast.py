"""
PPK DOCUMENT FACTORY - Toast Notification System
================================================
Modern toast notification dengan:
- Multiple types: success, error, warning, info
- Animasi fade in/out
- Auto-dismiss
- Stackable notifications

Author: PPK Document Factory Team
Version: 4.0
"""

from enum import Enum
from typing import Optional, List, Dict
from weakref import WeakValueDictionary

from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGraphicsOpacityEffect, QSizePolicy,
    QApplication
)
from PySide6.QtCore import (
    Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve,
    Property, QPoint, QSize
)
from PySide6.QtGui import QColor, QFont


# =============================================================================
# TOAST TYPES
# =============================================================================

class ToastType(Enum):
    """Types of toast notifications."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# Toast configuration per type
TOAST_CONFIG = {
    ToastType.SUCCESS: {
        'icon': '\u2713',  # Checkmark
        'bg_color': '#27ae60',
        'border_color': '#1e8449',
        'text_color': '#ffffff',
    },
    ToastType.ERROR: {
        'icon': '\u2717',  # X mark
        'bg_color': '#e74c3c',
        'border_color': '#c0392b',
        'text_color': '#ffffff',
    },
    ToastType.WARNING: {
        'icon': '\u26A0',  # Warning sign
        'bg_color': '#f39c12',
        'border_color': '#d68910',
        'text_color': '#ffffff',
    },
    ToastType.INFO: {
        'icon': '\u2139',  # Info symbol
        'bg_color': '#3498db',
        'border_color': '#2980b9',
        'text_color': '#ffffff',
    },
}


# =============================================================================
# TOAST WIDGET
# =============================================================================

class Toast(QFrame):
    """
    Single toast notification widget.

    Features:
    - Auto-dismiss after duration
    - Fade in/out animations
    - Close button
    - Icon based on type

    Signals:
        closed(): Emitted when toast is closed/dismissed

    Usage:
        toast = Toast("Operation successful!", ToastType.SUCCESS)
        toast.show()
    """

    closed = Signal()

    # Default settings
    DEFAULT_DURATION = 3000  # 3 seconds
    FADE_DURATION = 200  # 200ms for fade animation
    MIN_WIDTH = 300
    MAX_WIDTH = 400

    def __init__(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration: int = DEFAULT_DURATION,
        show_close: bool = True,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize toast notification.

        Args:
            message: Message to display
            toast_type: Type of toast (success, error, warning, info)
            duration: Auto-dismiss duration in ms (0 = no auto-dismiss)
            show_close: Show close button
            parent: Parent widget
        """
        super().__init__(parent)

        self._message = message
        self._toast_type = toast_type
        self._duration = duration
        self._show_close = show_close
        self._opacity = 0.0

        # Timers and animations
        self._dismiss_timer: Optional[QTimer] = None
        self._fade_animation: Optional[QPropertyAnimation] = None
        self._opacity_effect: Optional[QGraphicsOpacityEffect] = None

        self._setup_ui()
        self._setup_animation()

    def _setup_ui(self) -> None:
        """Setup toast UI."""
        config = TOAST_CONFIG[self._toast_type]

        # Frame settings
        self.setObjectName("toast")
        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMaximumWidth(self.MAX_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # Apply styling
        self.setStyleSheet(f"""
            QFrame#toast {{
                background-color: {config['bg_color']};
                border: 1px solid {config['border_color']};
                border-radius: 8px;
                padding: 0px;
            }}
        """)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(config['icon'])
        icon_label.setStyleSheet(f"""
            color: {config['text_color']};
            font-size: 18px;
            font-weight: bold;
        """)
        icon_label.setFixedWidth(24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Message
        message_label = QLabel(self._message)
        message_label.setStyleSheet(f"""
            color: {config['text_color']};
            font-size: 13px;
        """)
        message_label.setWordWrap(True)
        message_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(message_label)

        # Close button
        if self._show_close:
            close_btn = QPushButton("\u00D7")  # × symbol
            close_btn.setObjectName("toastCloseBtn")
            close_btn.setFixedSize(20, 20)
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            close_btn.setStyleSheet(f"""
                QPushButton#toastCloseBtn {{
                    background-color: transparent;
                    color: {config['text_color']};
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton#toastCloseBtn:hover {{
                    background-color: rgba(255, 255, 255, 0.2);
                    border-radius: 10px;
                }}
            """)
            close_btn.clicked.connect(self.dismiss)
            layout.addWidget(close_btn)

    def _setup_animation(self) -> None:
        """Setup opacity effect and animation."""
        # Opacity effect
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        # Fade animation
        self._fade_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_animation.setDuration(self.FADE_DURATION)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def show(self) -> None:
        """Show toast with fade-in animation."""
        super().show()

        # Fade in
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.start()

        # Start dismiss timer if duration > 0
        if self._duration > 0:
            self._dismiss_timer = QTimer(self)
            self._dismiss_timer.setSingleShot(True)
            self._dismiss_timer.timeout.connect(self.dismiss)
            self._dismiss_timer.start(self._duration)

    def dismiss(self) -> None:
        """Dismiss toast with fade-out animation."""
        # Stop dismiss timer if running
        if self._dismiss_timer and self._dismiss_timer.isActive():
            self._dismiss_timer.stop()

        # Fade out
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.finished.connect(self._on_fade_out_finished)
        self._fade_animation.start()

    def _on_fade_out_finished(self) -> None:
        """Handle fade out animation finished."""
        self.closed.emit()
        self.deleteLater()

    @property
    def toast_type(self) -> ToastType:
        """Get toast type."""
        return self._toast_type

    @property
    def message(self) -> str:
        """Get toast message."""
        return self._message


# =============================================================================
# TOAST CONTAINER
# =============================================================================

class ToastContainer(QWidget):
    """
    Container widget to hold and manage multiple toasts.

    Toasts are stacked vertically from top-right corner.
    Automatically manages toast lifecycle and positioning.
    """

    # Spacing between toasts
    TOAST_SPACING = 10
    # Margin from parent edges
    MARGIN = 20
    # Maximum toasts visible at once
    MAX_VISIBLE = 5

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize toast container.

        Args:
            parent: Parent widget (usually main window)
        """
        super().__init__(parent)

        self._toasts: List[Toast] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup container UI."""
        # Make container transparent and non-blocking
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        # Layout for stacking toasts
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.TOAST_SPACING)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        # Make sure container doesn't block parent
        self.setStyleSheet("background: transparent;")

    def add_toast(self, toast: Toast) -> None:
        """
        Add toast to container.

        Args:
            toast: Toast widget to add
        """
        # Remove oldest if at max
        while len(self._toasts) >= self.MAX_VISIBLE:
            oldest = self._toasts[0]
            oldest.dismiss()

        # Add to layout and list
        self.layout().addWidget(toast)
        self._toasts.append(toast)

        # Connect closed signal
        toast.closed.connect(lambda: self._on_toast_closed(toast))

        # Show toast
        toast.show()

        # Update position
        self._update_position()

    def _on_toast_closed(self, toast: Toast) -> None:
        """Handle toast closed."""
        if toast in self._toasts:
            self._toasts.remove(toast)

        # Hide container if empty
        if not self._toasts:
            self.hide()

    def _update_position(self) -> None:
        """Update container position relative to parent."""
        if not self.parent():
            return

        parent = self.parent()

        # Calculate size based on toasts
        self.adjustSize()

        # Position at top-right of parent
        x = parent.width() - self.width() - self.MARGIN
        y = self.MARGIN

        self.move(x, y)
        self.show()
        self.raise_()

    def clear(self) -> None:
        """Clear all toasts."""
        for toast in self._toasts[:]:  # Copy list to avoid modification during iteration
            toast.dismiss()

    def resizeEvent(self, event) -> None:
        """Handle resize event."""
        super().resizeEvent(event)
        self._update_position()


# =============================================================================
# TOAST MANAGER (Singleton)
# =============================================================================

class ToastManager:
    """
    Singleton manager for toast notifications.

    Provides static methods for showing toasts from anywhere in the application.
    Manages containers per parent window.

    Usage:
        ToastManager.success("Operation successful!", parent_widget)
        ToastManager.error("Something went wrong!", parent_widget)
        ToastManager.warning("Please check your input", parent_widget)
        ToastManager.info("New update available", parent_widget)
    """

    # Container cache per parent window
    _containers: WeakValueDictionary = WeakValueDictionary()

    @classmethod
    def _get_container(cls, parent: QWidget) -> ToastContainer:
        """
        Get or create container for parent widget.

        Args:
            parent: Parent widget

        Returns:
            ToastContainer for the parent
        """
        # Find top-level window
        window = parent.window() if parent else None

        if window is None:
            # Fallback to active window
            window = QApplication.activeWindow()

        if window is None:
            raise ValueError("No valid parent window found for toast")

        # Get or create container
        window_id = id(window)
        if window_id not in cls._containers:
            container = ToastContainer(window)
            cls._containers[window_id] = container

            # Connect to window resize
            # Note: This is a simple approach; for more robust handling,
            # you might want to install an event filter
            original_resize = window.resizeEvent

            def new_resize(event):
                original_resize(event)
                container._update_position()

            window.resizeEvent = new_resize

        return cls._containers[window_id]

    @classmethod
    def show(
        cls,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration: int = Toast.DEFAULT_DURATION,
        parent: Optional[QWidget] = None,
        show_close: bool = True
    ) -> Toast:
        """
        Show a toast notification.

        Args:
            message: Message to display
            toast_type: Type of toast
            duration: Auto-dismiss duration in ms (0 = no auto-dismiss)
            parent: Parent widget
            show_close: Show close button

        Returns:
            Toast widget

        Example:
            ToastManager.show("Hello!", ToastType.INFO, parent=self)
        """
        if parent is None:
            parent = QApplication.activeWindow()

        container = cls._get_container(parent)

        toast = Toast(
            message=message,
            toast_type=toast_type,
            duration=duration,
            show_close=show_close,
            parent=container
        )

        container.add_toast(toast)

        return toast

    @classmethod
    def success(
        cls,
        message: str,
        parent: Optional[QWidget] = None,
        duration: int = Toast.DEFAULT_DURATION
    ) -> Toast:
        """
        Show success toast.

        Args:
            message: Success message
            parent: Parent widget
            duration: Auto-dismiss duration

        Returns:
            Toast widget

        Example:
            ToastManager.success("Data saved successfully!", self)
        """
        return cls.show(message, ToastType.SUCCESS, duration, parent)

    @classmethod
    def error(
        cls,
        message: str,
        parent: Optional[QWidget] = None,
        duration: int = 5000  # Errors stay longer
    ) -> Toast:
        """
        Show error toast.

        Args:
            message: Error message
            parent: Parent widget
            duration: Auto-dismiss duration (default 5s for errors)

        Returns:
            Toast widget

        Example:
            ToastManager.error("Failed to save data!", self)
        """
        return cls.show(message, ToastType.ERROR, duration, parent)

    @classmethod
    def warning(
        cls,
        message: str,
        parent: Optional[QWidget] = None,
        duration: int = 4000  # Warnings stay a bit longer
    ) -> Toast:
        """
        Show warning toast.

        Args:
            message: Warning message
            parent: Parent widget
            duration: Auto-dismiss duration

        Returns:
            Toast widget

        Example:
            ToastManager.warning("Please review your input", self)
        """
        return cls.show(message, ToastType.WARNING, duration, parent)

    @classmethod
    def info(
        cls,
        message: str,
        parent: Optional[QWidget] = None,
        duration: int = Toast.DEFAULT_DURATION
    ) -> Toast:
        """
        Show info toast.

        Args:
            message: Info message
            parent: Parent widget
            duration: Auto-dismiss duration

        Returns:
            Toast widget

        Example:
            ToastManager.info("New version available", self)
        """
        return cls.show(message, ToastType.INFO, duration, parent)

    @classmethod
    def clear_all(cls, parent: Optional[QWidget] = None) -> None:
        """
        Clear all toasts.

        Args:
            parent: Parent widget (if None, clears all containers)
        """
        if parent is not None:
            window = parent.window()
            window_id = id(window)
            if window_id in cls._containers:
                cls._containers[window_id].clear()
        else:
            # Clear all containers
            for container in cls._containers.values():
                container.clear()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def show_toast(
    message: str,
    toast_type: ToastType = ToastType.INFO,
    parent: Optional[QWidget] = None,
    duration: int = Toast.DEFAULT_DURATION
) -> Toast:
    """
    Convenience function to show a toast.

    Args:
        message: Message to display
        toast_type: Type of toast
        parent: Parent widget
        duration: Auto-dismiss duration

    Returns:
        Toast widget

    Example:
        show_toast("Hello World!", ToastType.SUCCESS, self)
    """
    return ToastManager.show(message, toast_type, duration, parent)


def toast_success(message: str, parent: Optional[QWidget] = None) -> Toast:
    """Show success toast."""
    return ToastManager.success(message, parent)


def toast_error(message: str, parent: Optional[QWidget] = None) -> Toast:
    """Show error toast."""
    return ToastManager.error(message, parent)


def toast_warning(message: str, parent: Optional[QWidget] = None) -> Toast:
    """Show warning toast."""
    return ToastManager.warning(message, parent)


def toast_info(message: str, parent: Optional[QWidget] = None) -> Toast:
    """Show info toast."""
    return ToastManager.info(message, parent)
