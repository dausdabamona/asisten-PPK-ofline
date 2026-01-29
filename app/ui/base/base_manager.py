"""
PPK DOCUMENT FACTORY - Base Manager Widget
==========================================
Base class untuk semua manager widgets dengan fitur:
- Loading state management
- Error/Success message display via Toast notifications
- Signal-based communication
- Abstract methods untuk implementasi konsisten

Author: PPK Document Factory Team
Version: 4.0
"""

from abc import abstractmethod
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal, Property
from PySide6.QtGui import QColor

# Import toast manager for modern notifications
try:
    from app.ui.components import ToastManager, ConfirmDialog
    HAS_TOAST = True
except ImportError:
    HAS_TOAST = False


class BaseManagerWidget(QWidget):
    """
    Base class untuk semua manager widgets.

    Menyediakan:
    - Signals untuk komunikasi antar komponen
    - Loading state management dengan visual feedback
    - Helper methods untuk menampilkan pesan error/success
    - Abstract methods yang harus diimplementasikan oleh subclass

    Signals:
        data_changed: Emitted ketika data berubah (CRUD operations)
        error_occurred: Emitted ketika terjadi error, dengan pesan error
        loading_started: Emitted ketika loading dimulai
        loading_finished: Emitted ketika loading selesai

    Usage:
        class MyManager(BaseManagerWidget):
            def _setup_ui(self):
                # Setup UI components
                pass

            def _connect_signals(self):
                # Connect internal signals
                pass

            def refresh(self):
                # Refresh data from database
                self.show_loading("Memuat data...")
                try:
                    # Load data
                    pass
                finally:
                    self.hide_loading()
    """

    # Signals
    data_changed = Signal()
    error_occurred = Signal(str)
    loading_started = Signal()
    loading_finished = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize base manager widget.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        # Internal state
        self._is_loading: bool = False
        self._loading_overlay: Optional[QFrame] = None
        self._loading_label: Optional[QLabel] = None

        # Setup
        self._init_base_ui()
        self._setup_ui()
        self._connect_signals()
        self._connect_base_signals()

    def _init_base_ui(self) -> None:
        """
        Initialize base UI components seperti loading overlay.
        Dipanggil sebelum _setup_ui().
        """
        # Loading overlay (hidden by default)
        self._loading_overlay = QFrame(self)
        self._loading_overlay.setObjectName("loadingOverlay")
        self._loading_overlay.setStyleSheet("""
            QFrame#loadingOverlay {
                background-color: rgba(255, 255, 255, 0.85);
                border-radius: 8px;
            }
        """)
        self._loading_overlay.hide()

        # Loading label inside overlay
        overlay_layout = QVBoxLayout(self._loading_overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._loading_label = QLabel("Memuat...")
        self._loading_label.setObjectName("loadingLabel")
        self._loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._loading_label.setStyleSheet("""
            QLabel#loadingLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                padding: 20px 40px;
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
        """)
        overlay_layout.addWidget(self._loading_label)

    def _connect_base_signals(self) -> None:
        """Connect base signals untuk internal handling."""
        self.loading_started.connect(self._on_loading_started)
        self.loading_finished.connect(self._on_loading_finished)

    def _on_loading_started(self) -> None:
        """Internal handler ketika loading dimulai."""
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

    def _on_loading_finished(self) -> None:
        """Internal handler ketika loading selesai."""
        QApplication.restoreOverrideCursor()

    # =========================================================================
    # Abstract Methods - Harus diimplementasikan oleh subclass
    # =========================================================================

    @abstractmethod
    def _setup_ui(self) -> None:
        """
        Setup UI components.

        Harus diimplementasikan oleh subclass untuk membuat
        layout dan widgets yang diperlukan.

        Example:
            def _setup_ui(self):
                layout = QVBoxLayout(self)
                self.table = QTableWidget()
                layout.addWidget(self.table)
        """
        pass

    @abstractmethod
    def _connect_signals(self) -> None:
        """
        Connect internal signals dan slots.

        Harus diimplementasikan oleh subclass untuk menghubungkan
        signals dari widgets ke handlers.

        Example:
            def _connect_signals(self):
                self.btn_add.clicked.connect(self.on_add)
                self.table.itemSelectionChanged.connect(self.on_selection_changed)
        """
        pass

    @abstractmethod
    def refresh(self) -> None:
        """
        Refresh/reload data dari sumber (database, API, dll).

        Harus diimplementasikan oleh subclass untuk memuat ulang
        data dan memperbarui tampilan.

        Example:
            def refresh(self):
                self.show_loading("Memuat data pegawai...")
                try:
                    data = self.db.get_all_pegawai()
                    self._populate_table(data)
                except Exception as e:
                    self.show_error(f"Gagal memuat data: {e}")
                finally:
                    self.hide_loading()
        """
        pass

    # =========================================================================
    # Loading State Management
    # =========================================================================

    @property
    def is_loading(self) -> bool:
        """
        Check apakah widget sedang dalam loading state.

        Returns:
            bool: True jika sedang loading, False jika tidak
        """
        return self._is_loading

    def show_loading(self, message: str = "Memuat...") -> None:
        """
        Tampilkan loading state dengan overlay dan pesan.

        Args:
            message: Pesan yang ditampilkan selama loading

        Example:
            self.show_loading("Menyimpan data...")
            # ... operasi async
            self.hide_loading()
        """
        if self._is_loading:
            # Update message if already loading
            if self._loading_label:
                self._loading_label.setText(message)
            return

        self._is_loading = True

        # Update label text
        if self._loading_label:
            self._loading_label.setText(message)

        # Show overlay (resize to match parent)
        if self._loading_overlay:
            self._loading_overlay.setGeometry(self.rect())
            self._loading_overlay.raise_()
            self._loading_overlay.show()

        # Emit signal
        self.loading_started.emit()

        # Process events to update UI immediately
        QApplication.processEvents()

    def hide_loading(self) -> None:
        """
        Sembunyikan loading state dan overlay.

        Dipanggil setelah operasi loading selesai.
        Sebaiknya dipanggil dalam finally block untuk memastikan
        loading state selalu di-reset.

        Example:
            try:
                self.show_loading("Memuat...")
                # ... operasi
            finally:
                self.hide_loading()
        """
        if not self._is_loading:
            return

        self._is_loading = False

        # Hide overlay
        if self._loading_overlay:
            self._loading_overlay.hide()

        # Emit signal
        self.loading_finished.emit()

    # =========================================================================
    # Message Display Helpers
    # =========================================================================

    def show_error(
        self,
        message: str,
        title: str = "Error",
        use_toast: bool = True
    ) -> None:
        """
        Tampilkan pesan error menggunakan Toast atau QMessageBox.

        Args:
            message: Pesan error yang akan ditampilkan
            title: Judul dialog (untuk QMessageBox fallback)
            use_toast: Gunakan Toast notification (default: True)

        Example:
            try:
                self.db.save(data)
            except Exception as e:
                self.show_error(f"Gagal menyimpan: {e}")
        """
        # Emit signal untuk external handling
        self.error_occurred.emit(message)

        # Show toast or message box
        if use_toast and HAS_TOAST:
            ToastManager.error(message, self)
        else:
            QMessageBox.critical(self, title, message)

    def show_success(
        self,
        message: str,
        title: str = "Sukses",
        use_toast: bool = True
    ) -> None:
        """
        Tampilkan pesan sukses menggunakan Toast atau QMessageBox.

        Args:
            message: Pesan sukses yang akan ditampilkan
            title: Judul dialog (untuk QMessageBox fallback)
            use_toast: Gunakan Toast notification (default: True)

        Example:
            self.db.save(data)
            self.show_success("Data berhasil disimpan!")
        """
        if use_toast and HAS_TOAST:
            ToastManager.success(message, self)
        else:
            QMessageBox.information(self, title, message)

    def show_warning(
        self,
        message: str,
        title: str = "Peringatan",
        use_toast: bool = True
    ) -> None:
        """
        Tampilkan pesan peringatan menggunakan Toast atau QMessageBox.

        Args:
            message: Pesan peringatan yang akan ditampilkan
            title: Judul dialog (untuk QMessageBox fallback)
            use_toast: Gunakan Toast notification (default: True)

        Example:
            if not self.validate():
                self.show_warning("Data tidak valid!")
        """
        if use_toast and HAS_TOAST:
            ToastManager.warning(message, self)
        else:
            QMessageBox.warning(self, title, message)

    def show_info(
        self,
        message: str,
        title: str = "Informasi",
        use_toast: bool = True
    ) -> None:
        """
        Tampilkan pesan informasi menggunakan Toast atau QMessageBox.

        Args:
            message: Pesan informasi yang akan ditampilkan
            title: Judul dialog (untuk QMessageBox fallback)
            use_toast: Gunakan Toast notification (default: True)

        Example:
            self.show_info("Proses sedang berjalan...")
        """
        if use_toast and HAS_TOAST:
            ToastManager.info(message, self)
        else:
            QMessageBox.information(self, title, message)

    def confirm(self, message: str, title: str = "Konfirmasi") -> bool:
        """
        Tampilkan dialog konfirmasi Yes/No.

        Args:
            message: Pesan konfirmasi
            title: Judul dialog (default: "Konfirmasi")

        Returns:
            bool: True jika user memilih Yes, False jika No

        Example:
            if self.confirm("Hapus data ini?"):
                self.delete_data()
        """
        if HAS_TOAST:
            return ConfirmDialog.confirm(title, message, self)

        result = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return result == QMessageBox.StandardButton.Yes

    def confirm_danger(self, message: str, title: str = "Hapus Data") -> bool:
        """
        Tampilkan dialog konfirmasi untuk aksi berbahaya (hapus, dll).

        Args:
            message: Pesan konfirmasi
            title: Judul dialog

        Returns:
            bool: True jika user mengkonfirmasi, False jika tidak

        Example:
            if self.confirm_danger("Data akan dihapus permanen!"):
                self.delete_permanently()
        """
        if HAS_TOAST:
            return ConfirmDialog.danger(title, message, self)

        result = QMessageBox.warning(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return result == QMessageBox.StandardButton.Yes

    # =========================================================================
    # Event Handlers
    # =========================================================================

    def resizeEvent(self, event) -> None:
        """
        Handle resize event untuk menyesuaikan ukuran loading overlay.

        Args:
            event: QResizeEvent
        """
        super().resizeEvent(event)

        # Resize loading overlay to match widget size
        if self._loading_overlay and self._loading_overlay.isVisible():
            self._loading_overlay.setGeometry(self.rect())

    def showEvent(self, event) -> None:
        """
        Handle show event. Override untuk melakukan inisialisasi
        saat widget pertama kali ditampilkan.

        Args:
            event: QShowEvent
        """
        super().showEvent(event)
