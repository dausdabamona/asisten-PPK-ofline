"""
PPK DOCUMENT FACTORY - Empty State Component
============================================
Empty state display untuk menampilkan pesan ketika tidak ada data.

Author: PPK Document Factory Team
Version: 4.0
"""

from typing import Optional, Callable

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal


class EmptyState(QFrame):
    """
    Empty state widget untuk tampilan ketika tidak ada data.

    Menampilkan:
    - Icon/emoji besar
    - Title
    - Description
    - Optional action button

    Signals:
        action_clicked(): Emitted when action button is clicked

    Usage:
        empty = EmptyState(
            icon="📋",
            title="Tidak Ada Data",
            description="Belum ada transaksi yang tercatat.",
            action_text="Tambah Transaksi",
            action_callback=self.add_transaction
        )
    """

    action_clicked = Signal()

    def __init__(
        self,
        icon: str = "📋",
        title: str = "Tidak Ada Data",
        description: str = "",
        action_text: Optional[str] = None,
        action_callback: Optional[Callable] = None,
        parent=None
    ):
        """
        Initialize empty state widget.

        Args:
            icon: Emoji or icon text
            title: Main title text
            description: Descriptive text
            action_text: Optional action button text
            action_callback: Optional callback for action button
            parent: Parent widget
        """
        super().__init__(parent)

        self._icon = icon
        self._title = title
        self._description = description
        self._action_text = action_text
        self._action_callback = action_callback

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        self.setObjectName("emptyState")
        self.setStyleSheet("""
            QFrame#emptyState {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 12px;
            }
        """)

        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        # Icon
        self._icon_label = QLabel(self._icon)
        self._icon_label.setObjectName("emptyStateIcon")
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setStyleSheet("""
            QLabel#emptyStateIcon {
                font-size: 48px;
                color: #adb5bd;
            }
        """)
        layout.addWidget(self._icon_label)

        # Title
        self._title_label = QLabel(self._title)
        self._title_label.setObjectName("emptyStateTitle")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setWordWrap(True)
        self._title_label.setStyleSheet("""
            QLabel#emptyStateTitle {
                font-size: 18px;
                font-weight: bold;
                color: #495057;
            }
        """)
        layout.addWidget(self._title_label)

        # Description
        self._desc_label = QLabel(self._description)
        self._desc_label.setObjectName("emptyStateDesc")
        self._desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._desc_label.setWordWrap(True)
        self._desc_label.setStyleSheet("""
            QLabel#emptyStateDesc {
                font-size: 14px;
                color: #6c757d;
            }
        """)
        if self._description:
            layout.addWidget(self._desc_label)
        else:
            self._desc_label.hide()

        # Spacer
        layout.addSpacing(8)

        # Action button
        self._action_btn = QPushButton(self._action_text or "")
        self._action_btn.setObjectName("emptyStateAction")
        self._action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._action_btn.setStyleSheet("""
            QPushButton#emptyStateAction {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton#emptyStateAction:hover {
                background-color: #2980b9;
            }
            QPushButton#emptyStateAction:pressed {
                background-color: #2472a4;
            }
        """)
        self._action_btn.clicked.connect(self._on_action_clicked)

        if self._action_text:
            layout.addWidget(self._action_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            self._action_btn.hide()

    def _on_action_clicked(self) -> None:
        """Handle action button click."""
        self.action_clicked.emit()
        if self._action_callback:
            self._action_callback()

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================

    def set_icon(self, icon: str) -> None:
        """Set icon/emoji."""
        self._icon = icon
        self._icon_label.setText(icon)

    def set_title(self, title: str) -> None:
        """Set title text."""
        self._title = title
        self._title_label.setText(title)

    def set_description(self, desc: str) -> None:
        """Set description text."""
        self._description = desc
        self._desc_label.setText(desc)
        if desc:
            self._desc_label.show()
        else:
            self._desc_label.hide()

    def set_action(
        self,
        text: str,
        callback: Optional[Callable] = None
    ) -> None:
        """
        Set action button.

        Args:
            text: Button text
            callback: Optional callback function
        """
        self._action_text = text
        self._action_callback = callback
        self._action_btn.setText(text)
        self._action_btn.show()

    def hide_action(self) -> None:
        """Hide action button."""
        self._action_btn.hide()

    # =========================================================================
    # PRESET FACTORY METHODS
    # =========================================================================

    @classmethod
    def no_data(
        cls,
        action_text: Optional[str] = None,
        action_callback: Optional[Callable] = None,
        parent=None
    ) -> 'EmptyState':
        """
        Create "No Data" empty state.

        Args:
            action_text: Optional action button text
            action_callback: Optional callback
            parent: Parent widget

        Returns:
            EmptyState instance
        """
        return cls(
            icon="📋",
            title="Tidak Ada Data",
            description="Belum ada data yang tersedia.",
            action_text=action_text,
            action_callback=action_callback,
            parent=parent
        )

    @classmethod
    def no_results(
        cls,
        search_term: str = "",
        action_text: Optional[str] = "Reset Filter",
        action_callback: Optional[Callable] = None,
        parent=None
    ) -> 'EmptyState':
        """
        Create "No Results" empty state for search.

        Args:
            search_term: Search term that returned no results
            action_text: Optional action button text
            action_callback: Optional callback
            parent: Parent widget

        Returns:
            EmptyState instance
        """
        desc = "Tidak ditemukan hasil yang cocok."
        if search_term:
            desc = f"Tidak ditemukan hasil untuk \"{search_term}\"."

        return cls(
            icon="🔍",
            title="Tidak Ditemukan",
            description=desc,
            action_text=action_text,
            action_callback=action_callback,
            parent=parent
        )

    @classmethod
    def no_transactions(
        cls,
        action_text: Optional[str] = "Buat Transaksi",
        action_callback: Optional[Callable] = None,
        parent=None
    ) -> 'EmptyState':
        """
        Create "No Transactions" empty state.

        Args:
            action_text: Optional action button text
            action_callback: Optional callback
            parent: Parent widget

        Returns:
            EmptyState instance
        """
        return cls(
            icon="💰",
            title="Belum Ada Transaksi",
            description="Belum ada transaksi yang tercatat pada periode ini.",
            action_text=action_text,
            action_callback=action_callback,
            parent=parent
        )

    @classmethod
    def error(
        cls,
        message: str = "Terjadi kesalahan saat memuat data.",
        action_text: Optional[str] = "Coba Lagi",
        action_callback: Optional[Callable] = None,
        parent=None
    ) -> 'EmptyState':
        """
        Create "Error" empty state.

        Args:
            message: Error message
            action_text: Optional action button text
            action_callback: Optional callback
            parent: Parent widget

        Returns:
            EmptyState instance
        """
        return cls(
            icon="⚠️",
            title="Terjadi Kesalahan",
            description=message,
            action_text=action_text,
            action_callback=action_callback,
            parent=parent
        )

    @classmethod
    def no_documents(
        cls,
        action_text: Optional[str] = "Upload Dokumen",
        action_callback: Optional[Callable] = None,
        parent=None
    ) -> 'EmptyState':
        """
        Create "No Documents" empty state.

        Args:
            action_text: Optional action button text
            action_callback: Optional callback
            parent: Parent widget

        Returns:
            EmptyState instance
        """
        return cls(
            icon="📁",
            title="Belum Ada Dokumen",
            description="Belum ada dokumen yang diupload.",
            action_text=action_text,
            action_callback=action_callback,
            parent=parent
        )

    @classmethod
    def coming_soon(
        cls,
        feature_name: str = "Fitur",
        parent=None
    ) -> 'EmptyState':
        """
        Create "Coming Soon" empty state.

        Args:
            feature_name: Name of the upcoming feature
            parent: Parent widget

        Returns:
            EmptyState instance
        """
        return cls(
            icon="🚀",
            title="Segera Hadir",
            description=f"{feature_name} sedang dalam pengembangan dan akan segera tersedia.",
            action_text=None,
            parent=parent
        )

    @classmethod
    def maintenance(
        cls,
        parent=None
    ) -> 'EmptyState':
        """
        Create "Maintenance" empty state.

        Args:
            parent: Parent widget

        Returns:
            EmptyState instance
        """
        return cls(
            icon="🔧",
            title="Dalam Pemeliharaan",
            description="Sistem sedang dalam pemeliharaan. Silakan coba beberapa saat lagi.",
            action_text=None,
            parent=parent
        )
