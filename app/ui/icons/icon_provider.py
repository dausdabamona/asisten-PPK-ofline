"""
PPK DOCUMENT FACTORY - Icon Provider
====================================
Centralized icon management system dengan:
- Singleton pattern untuk consistent access
- Icon caching untuk performance
- Fallback mechanism untuk missing icons
- Support untuk SVG icons

Author: PPK Document Factory Team
Version: 4.0
"""

import os
import sys
from typing import Dict, List, Optional
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import QSize, Qt
from PySide6.QtSvg import QSvgRenderer


class IconProvider:
    """
    Centralized icon management dengan singleton pattern.

    Menyediakan:
    - Mapping nama icon ke file path
    - Caching untuk icons yang sudah di-load
    - Fallback ke default icon jika tidak ditemukan
    - Support untuk berbagai ukuran icon

    Usage:
        # Get QIcon
        icon = IconProvider.get_icon("home", size=24)
        button.setIcon(icon)

        # Get QPixmap
        pixmap = IconProvider.get_pixmap("settings", size=32)
        label.setPixmap(pixmap)

        # Register custom icon
        IconProvider.register_icon("custom", "/path/to/custom.svg")

        # List available icons
        icons = IconProvider.list_available_icons()
    """

    # Base path untuk icon files (akan di-set saat runtime)
    _BASE_PATH: str = ""
    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls) -> None:
        """Ensure base path is initialized."""
        if not cls._initialized:
            cls._initialize_base_path()

    @classmethod
    def _initialize_base_path(cls) -> None:
        """Initialize base path untuk icon files."""
        # Try multiple possible locations
        possible_paths = [
            # Relative to this file (development)
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                "assets", "icons"
            ),
            # Relative to current working directory
            os.path.join(os.getcwd(), "assets", "icons"),
            # For PyInstaller bundled app
            os.path.join(
                getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))),
                "assets", "icons"
            ),
        ]

        for path in possible_paths:
            if os.path.isdir(path):
                cls._BASE_PATH = path
                cls._initialized = True
                return

        # Fallback to first option even if doesn't exist
        cls._BASE_PATH = possible_paths[0]
        cls._initialized = True

    # Icon mapping: name -> relative path from BASE_PATH
    ICON_MAP: Dict[str, str] = {
        # Navigation
        "home": "home.svg",
        "dashboard": "dashboard.svg",
        "arrow-left": "arrow-left.svg",
        "arrow-right": "arrow-right.svg",

        # Finance/Money
        "wallet": "wallet.svg",
        "money": "money.svg",
        "send": "send.svg",

        # Actions
        "plus-circle": "plus-circle.svg",
        "plus": "plus.svg",
        "edit": "edit.svg",
        "delete": "delete.svg",
        "view": "view.svg",
        "save": "save.svg",
        "print": "print.svg",
        "export": "export.svg",
        "download": "download.svg",
        "upload": "upload.svg",
        "refresh": "refresh.svg",
        "search": "search.svg",

        # Objects
        "package": "package.svg",
        "users": "users.svg",
        "user": "user.svg",
        "box": "box.svg",
        "building": "building.svg",
        "database": "database.svg",
        "file-text": "file-text.svg",
        "folder": "folder.svg",
        "document": "document.svg",

        # Status/Feedback
        "check": "check.svg",
        "check-circle": "check-circle.svg",
        "x": "x.svg",
        "x-circle": "x-circle.svg",
        "warning": "warning.svg",
        "info": "info.svg",
        "error": "error.svg",

        # UI
        "settings": "settings.svg",
        "menu": "menu.svg",
        "close": "close.svg",
        "minimize": "minimize.svg",
        "maximize": "maximize.svg",

        # Misc
        "calendar": "calendar.svg",
        "clock": "clock.svg",
        "filter": "filter.svg",
        "sort": "sort.svg",
    }

    # Cache untuk icons yang sudah di-load
    _icon_cache: Dict[str, QIcon] = {}
    _pixmap_cache: Dict[str, QPixmap] = {}

    # Default fallback color
    _FALLBACK_COLOR: str = "#95a5a6"

    @classmethod
    def get_icon(
        cls,
        name: str,
        size: int = 24,
        color: Optional[str] = None
    ) -> QIcon:
        """
        Get QIcon by name.

        Args:
            name: Nama icon (dari ICON_MAP)
            size: Ukuran icon dalam pixels (default: 24)
            color: Optional color untuk tint icon (hex string)

        Returns:
            QIcon: Icon yang diminta, atau fallback icon jika tidak ditemukan

        Example:
            icon = IconProvider.get_icon("home", size=24)
            button.setIcon(icon)
        """
        cache_key = f"{name}_{size}_{color or 'default'}"

        # Check cache
        if cache_key in cls._icon_cache:
            return cls._icon_cache[cache_key]

        # Get pixmap and create icon
        pixmap = cls.get_pixmap(name, size, color)
        icon = QIcon(pixmap)

        # Cache and return
        cls._icon_cache[cache_key] = icon
        return icon

    @classmethod
    def get_pixmap(
        cls,
        name: str,
        size: int = 24,
        color: Optional[str] = None
    ) -> QPixmap:
        """
        Get QPixmap by name.

        Args:
            name: Nama icon (dari ICON_MAP)
            size: Ukuran icon dalam pixels (default: 24)
            color: Optional color untuk tint icon (hex string)

        Returns:
            QPixmap: Pixmap yang diminta, atau fallback pixmap jika tidak ditemukan

        Example:
            pixmap = IconProvider.get_pixmap("settings", size=32)
            label.setPixmap(pixmap)
        """
        cache_key = f"{name}_{size}_{color or 'default'}"

        # Check cache
        if cache_key in cls._pixmap_cache:
            return cls._pixmap_cache[cache_key]

        # Try to load from file
        pixmap = cls._load_icon_file(name, size, color)

        if pixmap.isNull():
            # Create fallback pixmap
            pixmap = cls._create_fallback_pixmap(name, size, color)

        # Cache and return
        cls._pixmap_cache[cache_key] = pixmap
        return pixmap

    @classmethod
    def _load_icon_file(
        cls,
        name: str,
        size: int,
        color: Optional[str] = None
    ) -> QPixmap:
        """
        Load icon dari file.

        Args:
            name: Nama icon
            size: Ukuran icon
            color: Optional color untuk tint

        Returns:
            QPixmap: Loaded pixmap atau null pixmap jika gagal
        """
        # Ensure base path is initialized
        cls._ensure_initialized()

        # Get file path
        if name not in cls.ICON_MAP:
            return QPixmap()

        file_path = os.path.join(cls._BASE_PATH, cls.ICON_MAP[name])

        if not os.path.exists(file_path):
            return QPixmap()

        # Check if SVG
        if file_path.lower().endswith('.svg'):
            return cls._load_svg(file_path, size, color)
        else:
            # Load as regular image
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    QSize(size, size),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            return pixmap

    @classmethod
    def _load_svg(
        cls,
        file_path: str,
        size: int,
        color: Optional[str] = None
    ) -> QPixmap:
        """
        Load SVG file dan render ke QPixmap.

        Args:
            file_path: Path ke file SVG
            size: Ukuran output
            color: Optional color untuk tint

        Returns:
            QPixmap: Rendered SVG
        """
        renderer = QSvgRenderer(file_path)
        if not renderer.isValid():
            return QPixmap()

        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        # Apply color tint if specified
        if color:
            pixmap = cls._apply_color_tint(pixmap, color)

        return pixmap

    @classmethod
    def _apply_color_tint(cls, pixmap: QPixmap, color: str) -> QPixmap:
        """
        Apply color tint ke pixmap.

        Args:
            pixmap: Source pixmap
            color: Color hex string

        Returns:
            QPixmap: Tinted pixmap
        """
        tinted = QPixmap(pixmap.size())
        tinted.fill(Qt.GlobalColor.transparent)

        painter = QPainter(tinted)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(tinted.rect(), QColor(color))
        painter.end()

        return tinted

    @classmethod
    def _create_fallback_pixmap(
        cls,
        name: str,
        size: int,
        color: Optional[str] = None
    ) -> QPixmap:
        """
        Create fallback pixmap ketika icon tidak ditemukan.

        Membuat placeholder dengan initial letter dari nama icon.

        Args:
            name: Nama icon
            size: Ukuran icon
            color: Optional color

        Returns:
            QPixmap: Fallback pixmap dengan placeholder
        """
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw circle background
        fill_color = QColor(color if color else cls._FALLBACK_COLOR)
        fill_color.setAlpha(50)
        painter.setBrush(fill_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, size - 4, size - 4)

        # Draw border
        border_color = QColor(color if color else cls._FALLBACK_COLOR)
        painter.setPen(border_color)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(2, 2, size - 4, size - 4)

        # Draw initial letter
        if name:
            font = painter.font()
            font.setPixelSize(int(size * 0.4))
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor(color if color else cls._FALLBACK_COLOR))
            painter.drawText(
                pixmap.rect(),
                Qt.AlignmentFlag.AlignCenter,
                name[0].upper()
            )

        painter.end()
        return pixmap

    @classmethod
    def register_icon(cls, name: str, path: str) -> bool:
        """
        Register custom icon.

        Args:
            name: Nama icon untuk digunakan di get_icon/get_pixmap
            path: Path absolut atau relatif ke file icon

        Returns:
            bool: True jika berhasil, False jika file tidak ditemukan

        Example:
            IconProvider.register_icon("my_custom", "/path/to/icon.svg")
            icon = IconProvider.get_icon("my_custom")
        """
        # Convert to absolute path if relative
        if not os.path.isabs(path):
            path = os.path.join(cls._BASE_PATH, path)

        if not os.path.exists(path):
            return False

        # Add to icon map (store relative path)
        relative_path = os.path.relpath(path, cls._BASE_PATH)
        cls.ICON_MAP[name] = relative_path

        # Clear cache for this icon
        cls._clear_cache_for_icon(name)

        return True

    @classmethod
    def _clear_cache_for_icon(cls, name: str) -> None:
        """
        Clear cache entries untuk icon tertentu.

        Args:
            name: Nama icon
        """
        # Clear from icon cache
        keys_to_remove = [k for k in cls._icon_cache if k.startswith(f"{name}_")]
        for key in keys_to_remove:
            del cls._icon_cache[key]

        # Clear from pixmap cache
        keys_to_remove = [k for k in cls._pixmap_cache if k.startswith(f"{name}_")]
        for key in keys_to_remove:
            del cls._pixmap_cache[key]

    @classmethod
    def list_available_icons(cls) -> List[str]:
        """
        Get list of all available icon names.

        Returns:
            List[str]: Sorted list of icon names

        Example:
            icons = IconProvider.list_available_icons()
            for icon_name in icons:
                print(icon_name)
        """
        return sorted(cls.ICON_MAP.keys())

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear all cached icons.

        Berguna untuk membebaskan memory atau setelah mengubah icons.
        """
        cls._icon_cache.clear()
        cls._pixmap_cache.clear()

    @classmethod
    def set_base_path(cls, path: str) -> None:
        """
        Set base path untuk icon files.

        Args:
            path: Path absolut ke folder icons

        Example:
            IconProvider.set_base_path("/app/assets/icons")
        """
        cls._BASE_PATH = path
        cls.clear_cache()

    @classmethod
    def icon_exists(cls, name: str) -> bool:
        """
        Check apakah icon file exists.

        Args:
            name: Nama icon

        Returns:
            bool: True jika file exists, False jika tidak

        Example:
            if IconProvider.icon_exists("home"):
                icon = IconProvider.get_icon("home")
        """
        cls._ensure_initialized()

        if name not in cls.ICON_MAP:
            return False

        file_path = os.path.join(cls._BASE_PATH, cls.ICON_MAP[name])
        return os.path.exists(file_path)

    @classmethod
    def get_icon_path(cls, name: str) -> Optional[str]:
        """
        Get full path untuk icon file.

        Args:
            name: Nama icon

        Returns:
            Optional[str]: Full path jika ada di ICON_MAP, None jika tidak

        Example:
            path = IconProvider.get_icon_path("home")
            if path:
                print(f"Icon file: {path}")
        """
        cls._ensure_initialized()

        if name not in cls.ICON_MAP:
            return None

        return os.path.join(cls._BASE_PATH, cls.ICON_MAP[name])

    @classmethod
    def get_base_path(cls) -> str:
        """
        Get current base path untuk icon files.

        Returns:
            str: Base path directory
        """
        cls._ensure_initialized()
        return cls._BASE_PATH
