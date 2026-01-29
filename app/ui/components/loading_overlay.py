"""
PPK DOCUMENT FACTORY - Loading Overlay Component
================================================
Elegant loading overlay dengan:
- Animated spinner
- Semi-transparent background
- Optional message text
- Mixin untuk easy integration

Author: PPK Document Factory Team
Version: 4.0
"""

from typing import Optional
import math

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect,
    QSizePolicy
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    Property, QSize, QRectF, QPointF
)
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QBrush


# =============================================================================
# SPINNER WIDGET
# =============================================================================

class SpinnerWidget(QWidget):
    """
    Animated circular spinner widget.

    Uses QPainter for smooth custom drawing animation.

    Usage:
        spinner = SpinnerWidget(size=48, color="#3498db")
        spinner.start()
        # ... later
        spinner.stop()
    """

    def __init__(
        self,
        size: int = 40,
        color: str = "#3498db",
        line_width: int = 4,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize spinner widget.

        Args:
            size: Diameter of spinner in pixels
            color: Color of spinner arc
            line_width: Width of spinner line
            parent: Parent widget
        """
        super().__init__(parent)

        self._size = size
        self._color = QColor(color)
        self._line_width = line_width
        self._angle = 0
        self._is_spinning = False

        # Animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)

        # Setup
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def start(self) -> None:
        """Start spinning animation."""
        if not self._is_spinning:
            self._is_spinning = True
            self._timer.start(16)  # ~60 FPS

    def stop(self) -> None:
        """Stop spinning animation."""
        self._is_spinning = False
        self._timer.stop()
        self._angle = 0
        self.update()

    def _rotate(self) -> None:
        """Rotate spinner by increment."""
        self._angle = (self._angle + 8) % 360
        self.update()

    def set_color(self, color: str) -> None:
        """Set spinner color."""
        self._color = QColor(color)
        self.update()

    def set_size(self, size: int) -> None:
        """Set spinner size."""
        self._size = size
        self.setFixedSize(size, size)
        self.update()

    def paintEvent(self, event) -> None:
        """Paint the spinner."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate dimensions
        side = min(self.width(), self.height())
        margin = self._line_width
        rect = QRectF(margin, margin, side - 2 * margin, side - 2 * margin)

        # Draw background arc (lighter)
        bg_color = QColor(self._color)
        bg_color.setAlpha(50)
        pen = QPen(bg_color)
        pen.setWidth(self._line_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Draw spinning arc
        pen.setColor(self._color)
        painter.setPen(pen)

        # Draw arc with gradient effect
        start_angle = self._angle * 16
        span_angle = 90 * 16  # 90 degree arc

        painter.drawArc(rect, start_angle, span_angle)

    @property
    def is_spinning(self) -> bool:
        """Check if spinner is currently spinning."""
        return self._is_spinning


# =============================================================================
# LOADING OVERLAY
# =============================================================================

class LoadingOverlay(QWidget):
    """
    Semi-transparent loading overlay with spinner and message.

    Covers entire parent widget and blocks mouse events.

    Usage:
        overlay = LoadingOverlay(parent_widget)
        overlay.show_loading("Menyimpan data...")
        # ... async operation
        overlay.hide_loading()
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        background_opacity: float = 0.85,
        spinner_size: int = 48,
        spinner_color: str = "#3498db"
    ):
        """
        Initialize loading overlay.

        Args:
            parent: Parent widget to cover
            background_opacity: Background opacity (0.0 - 1.0)
            spinner_size: Size of spinner
            spinner_color: Color of spinner
        """
        super().__init__(parent)

        self._background_opacity = background_opacity
        self._message = "Memuat..."

        # Setup widget
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Container for centering
        container = QWidget()
        container.setObjectName("loadingContainer")
        container.setStyleSheet("""
            QWidget#loadingContainer {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setSpacing(16)

        # Spinner
        self._spinner = SpinnerWidget(
            size=spinner_size,
            color=spinner_color,
            parent=container
        )
        container_layout.addWidget(self._spinner, alignment=Qt.AlignmentFlag.AlignCenter)

        # Message label
        self._message_label = QLabel(self._message)
        self._message_label.setObjectName("loadingMessage")
        self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._message_label.setStyleSheet("""
            QLabel#loadingMessage {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        container_layout.addWidget(self._message_label)

        layout.addWidget(container)

        # Initially hidden
        self.hide()

    def show_loading(self, message: str = "Memuat...") -> None:
        """
        Show loading overlay with message.

        Args:
            message: Message to display
        """
        self._message = message
        self._message_label.setText(message)

        # Resize to cover parent
        if self.parent():
            self.setGeometry(self.parent().rect())

        self._spinner.start()
        self.show()
        self.raise_()

    def hide_loading(self) -> None:
        """Hide loading overlay."""
        self._spinner.stop()
        self.hide()

    def set_message(self, message: str) -> None:
        """Update loading message."""
        self._message = message
        self._message_label.setText(message)

    def paintEvent(self, event) -> None:
        """Paint semi-transparent background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw semi-transparent white background
        bg_color = QColor(255, 255, 255, int(255 * self._background_opacity))
        painter.fillRect(self.rect(), bg_color)

    def resizeEvent(self, event) -> None:
        """Handle resize to match parent."""
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())

    def mousePressEvent(self, event) -> None:
        """Block mouse events."""
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        """Block mouse events."""
        event.accept()

    def mouseMoveEvent(self, event) -> None:
        """Block mouse events."""
        event.accept()


# =============================================================================
# LOADING MIXIN
# =============================================================================

class LoadingMixin:
    """
    Mixin class to add loading overlay capability to any widget.

    Usage:
        class MyWidget(QWidget, LoadingMixin):
            def __init__(self):
                super().__init__()
                # ...

            def do_something(self):
                self.show_loading("Processing...")
                try:
                    # ... async operation
                finally:
                    self.hide_loading()
    """

    _loading_overlay: Optional[LoadingOverlay] = None

    def _ensure_overlay(self) -> LoadingOverlay:
        """Ensure loading overlay exists."""
        if self._loading_overlay is None:
            self._loading_overlay = LoadingOverlay(self)
        return self._loading_overlay

    def show_loading(self, message: str = "Memuat...") -> None:
        """
        Show loading overlay.

        Args:
            message: Loading message to display
        """
        overlay = self._ensure_overlay()
        overlay.show_loading(message)

    def hide_loading(self) -> None:
        """Hide loading overlay."""
        if self._loading_overlay:
            self._loading_overlay.hide_loading()

    def set_loading_message(self, message: str) -> None:
        """
        Update loading message while showing.

        Args:
            message: New message to display
        """
        if self._loading_overlay and self._loading_overlay.isVisible():
            self._loading_overlay.set_message(message)

    @property
    def is_loading(self) -> bool:
        """Check if loading overlay is currently visible."""
        return (
            self._loading_overlay is not None
            and self._loading_overlay.isVisible()
        )


# =============================================================================
# SIMPLE LOADING INDICATOR (Alternative)
# =============================================================================

class LoadingDots(QWidget):
    """
    Simple animated loading dots indicator.

    Lighter alternative to spinner for inline loading.
    """

    def __init__(
        self,
        dot_count: int = 3,
        dot_size: int = 8,
        color: str = "#3498db",
        parent: Optional[QWidget] = None
    ):
        """
        Initialize loading dots.

        Args:
            dot_count: Number of dots
            dot_size: Size of each dot
            color: Dot color
            parent: Parent widget
        """
        super().__init__(parent)

        self._dot_count = dot_count
        self._dot_size = dot_size
        self._color = QColor(color)
        self._active_dot = 0
        self._is_animating = False

        # Timer for animation
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)

        # Calculate size
        width = dot_count * dot_size + (dot_count - 1) * dot_size // 2
        self.setFixedSize(width, dot_size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def start(self) -> None:
        """Start animation."""
        if not self._is_animating:
            self._is_animating = True
            self._timer.start(300)

    def stop(self) -> None:
        """Stop animation."""
        self._is_animating = False
        self._timer.stop()
        self._active_dot = 0
        self.update()

    def _animate(self) -> None:
        """Animate to next dot."""
        self._active_dot = (self._active_dot + 1) % self._dot_count
        self.update()

    def paintEvent(self, event) -> None:
        """Paint the dots."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        spacing = self._dot_size + self._dot_size // 2
        y = 0

        for i in range(self._dot_count):
            x = i * spacing

            # Active dot is larger and fully opaque
            if i == self._active_dot:
                color = self._color
                size = self._dot_size
            else:
                color = QColor(self._color)
                color.setAlpha(100)
                size = self._dot_size - 2

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)

            # Center smaller dots
            offset = (self._dot_size - size) // 2
            painter.drawEllipse(x + offset, y + offset, size, size)
