"""
PPK DOCUMENT FACTORY - Base Page Widget
=======================================
Base class untuk semua page widgets dengan fitur:
- Navigation signals (navigate_to, navigate_back)
- Page title dan identifier management
- Loading state management
- Toast notifications for messages
- Consistent UI setup pattern

Author: PPK Document Factory Team
Version: 4.0
"""

from abc import abstractmethod
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QApplication, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Property

# Import toast manager for modern notifications
try:
    from app.ui.components import ToastManager, ConfirmDialog
    HAS_TOAST = True
except ImportError:
    HAS_TOAST = False


class BasePage(QWidget):
    """
    Base class untuk semua page widgets.

    Menyediakan:
    - Navigation signals untuk komunikasi dengan main window
    - Page title dan identifier management
    - Loading state dengan visual feedback
    - Consistent setup pattern

    Signals:
        navigate_to(str): Emitted untuk navigasi ke page lain (by page_id)
        navigate_back(): Emitted untuk kembali ke page sebelumnya
        title_changed(str): Emitted ketika title page berubah

    Properties:
        page_title (str): Judul halaman yang ditampilkan
        page_id (str): Identifier unik untuk page ini
        can_go_back (bool): Apakah page ini bisa navigate back

    Usage:
        class DashboardPage(BasePage):
            def __init__(self, parent=None):
                super().__init__(
                    page_id="dashboard",
                    page_title="Dashboard",
                    can_go_back=False,
                    parent=parent
                )

            def _setup_ui(self):
                layout = QVBoxLayout(self)
                # Setup UI components
                pass

            def _load_data(self):
                # Load data from database
                pass
    """

    # Signals
    navigate_to = Signal(str)  # page_id
    navigate_back = Signal()
    title_changed = Signal(str)

    def __init__(
        self,
        page_id: str = "",
        page_title: str = "",
        can_go_back: bool = True,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize base page widget.

        Args:
            page_id: Identifier unik untuk page (e.g., "dashboard", "up_list")
            page_title: Judul halaman yang ditampilkan
            can_go_back: Apakah page ini bisa navigate back (default: True)
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        # Page properties
        self._page_id: str = page_id
        self._page_title: str = page_title
        self._can_go_back: bool = can_go_back

        # Internal state
        self._is_loading: bool = False
        self._loading_overlay: Optional[QFrame] = None
        self._loading_label: Optional[QLabel] = None
        self._is_initialized: bool = False

        # Setup
        self._init_base_ui()
        self._setup_ui()

    def _init_base_ui(self) -> None:
        """
        Initialize base UI components seperti loading overlay.
        Dipanggil sebelum _setup_ui().
        """
        # Loading overlay (hidden by default)
        self._loading_overlay = QFrame(self)
        self._loading_overlay.setObjectName("pageLoadingOverlay")
        self._loading_overlay.setStyleSheet("""
            QFrame#pageLoadingOverlay {
                background-color: rgba(255, 255, 255, 0.9);
            }
        """)
        self._loading_overlay.hide()

        # Loading content
        overlay_layout = QVBoxLayout(self._loading_overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._loading_label = QLabel("Memuat...")
        self._loading_label.setObjectName("pageLoadingLabel")
        self._loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._loading_label.setStyleSheet("""
            QLabel#pageLoadingLabel {
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

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def page_id(self) -> str:
        """
        Get page identifier.

        Returns:
            str: Unique identifier untuk page ini
        """
        return self._page_id

    @page_id.setter
    def page_id(self, value: str) -> None:
        """
        Set page identifier.

        Args:
            value: New page identifier
        """
        self._page_id = value

    @property
    def page_title(self) -> str:
        """
        Get page title.

        Returns:
            str: Judul halaman
        """
        return self._page_title

    @page_title.setter
    def page_title(self, value: str) -> None:
        """
        Set page title dan emit signal.

        Args:
            value: New page title
        """
        if self._page_title != value:
            self._page_title = value
            self.title_changed.emit(value)

    @property
    def can_go_back(self) -> bool:
        """
        Check apakah page ini bisa navigate back.

        Returns:
            bool: True jika bisa go back, False jika tidak
        """
        return self._can_go_back

    @can_go_back.setter
    def can_go_back(self, value: bool) -> None:
        """
        Set can_go_back flag.

        Args:
            value: New value
        """
        self._can_go_back = value

    @property
    def is_loading(self) -> bool:
        """
        Check apakah page sedang dalam loading state.

        Returns:
            bool: True jika sedang loading, False jika tidak
        """
        return self._is_loading

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

                # Header
                header = self._create_header()
                layout.addWidget(header)

                # Content
                self.content = QWidget()
                layout.addWidget(self.content, 1)
        """
        pass

    @abstractmethod
    def _load_data(self) -> None:
        """
        Load/refresh data untuk page ini.

        Harus diimplementasikan oleh subclass untuk memuat
        data dari database atau sumber lain.

        Example:
            def _load_data(self):
                self.show_loading("Memuat data...")
                try:
                    data = self.db.get_all_items()
                    self._populate_view(data)
                except Exception as e:
                    self._show_error(str(e))
                finally:
                    self.hide_loading()
        """
        pass

    # =========================================================================
    # Navigation Methods
    # =========================================================================

    def go_to(self, page_id: str) -> None:
        """
        Navigate ke page lain.

        Args:
            page_id: Identifier page tujuan

        Example:
            self.go_to("up_detail")
        """
        self.navigate_to.emit(page_id)

    def go_back(self) -> None:
        """
        Navigate kembali ke page sebelumnya.

        Hanya bekerja jika can_go_back == True.
        """
        if self._can_go_back:
            self.navigate_back.emit()

    # =========================================================================
    # Title Management
    # =========================================================================

    def set_title(self, title: str) -> None:
        """
        Set page title.

        Args:
            title: New page title

        Example:
            self.set_title("Detail Transaksi UP")
        """
        self.page_title = title

    # =========================================================================
    # Loading State Management
    # =========================================================================

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

        # Show overlay
        if self._loading_overlay:
            self._loading_overlay.setGeometry(self.rect())
            self._loading_overlay.raise_()
            self._loading_overlay.show()

        # Set cursor
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        # Process events to update UI immediately
        QApplication.processEvents()

    def hide_loading(self) -> None:
        """
        Sembunyikan loading state dan overlay.

        Dipanggil setelah operasi loading selesai.
        Sebaiknya dipanggil dalam finally block.

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

        # Restore cursor
        QApplication.restoreOverrideCursor()

    # =========================================================================
    # Helper Methods untuk Subclass
    # =========================================================================

    def _create_back_button(self, text: str = "< Kembali") -> QPushButton:
        """
        Create styled back button.

        Args:
            text: Button text (default: "< Kembali")

        Returns:
            QPushButton: Styled back button
        """
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                font-size: 13px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                color: #2980b9;
                text-decoration: underline;
            }
        """)
        btn.clicked.connect(self.go_back)
        return btn

    def _create_page_title_label(self, text: Optional[str] = None) -> QLabel:
        """
        Create styled page title label.

        Args:
            text: Title text (default: uses page_title property)

        Returns:
            QLabel: Styled title label
        """
        label = QLabel(text or self._page_title)
        label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
        """)
        return label

    # =========================================================================
    # Event Handlers
    # =========================================================================

    def showEvent(self, event) -> None:
        """
        Handle show event.

        Memanggil _load_data() saat page pertama kali ditampilkan.

        Args:
            event: QShowEvent
        """
        super().showEvent(event)

        # Load data on first show
        if not self._is_initialized:
            self._is_initialized = True
            self._load_data()

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

    # =========================================================================
    # Public Methods
    # =========================================================================

    def refresh(self) -> None:
        """
        Refresh page data.

        Memanggil _load_data() untuk memuat ulang data.
        Dapat di-override oleh subclass jika perlu logic tambahan.
        """
        self._load_data()

    def reset(self) -> None:
        """
        Reset page state.

        Reset initialized flag sehingga _load_data() akan dipanggil
        lagi pada showEvent berikutnya.
        """
        self._is_initialized = False

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
            if self.confirm("Simpan perubahan?"):
                self.save_data()
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
