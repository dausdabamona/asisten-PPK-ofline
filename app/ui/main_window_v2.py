"""
PPK DOCUMENT FACTORY - Main Window v2 (Workflow Edition)
=========================================================
Main window dengan sidebar navigation dan workflow-based pages.

Layout:
┌─────────────────────────────────────────────────────────────────────┐
│  Header Bar: Logo | App Name | User | Settings | Help              │
├────────────────┬────────────────────────────────────────────────────┤
│                │                                                    │
│   Sidebar      │              Content Area                         │
│   (Collapsible)│              (QStackedWidget)                     │
│                │                                                    │
│   - Dashboard  │   Pages:                                          │
│   - UP         │   - DashboardPencairanPage                        │
│   - TUP        │   - UPListPage, UPDetailPage                      │
│   - LS         │   - TUPListPage, TUPDetailPage                    │
│   - Pengadaan  │   - LSListPage, LSDetailPage                      │
│   - Pengaturan │   - TransaksiFormPage                             │
│                │                                                    │
└────────────────┴────────────────────────────────────────────────────┘
│  Status Bar: Connection Status | Saldo UP | Last Sync              │
└─────────────────────────────────────────────────────────────────────┘
"""

import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QSplitter, QStatusBar, QLabel,
    QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon

from typing import Dict, Any, Optional

# Import components
from .components.sidebar import Sidebar

# Import pages
from .pages.pencairan import (
    DashboardPencairanPage,
    UPListPage, UPDetailPage,
    TUPListPage, TUPDetailPage,
    LSListPage, LSDetailPage,
    TransaksiFormPage
)

# Import models
from ..models.pencairan_models import PencairanManager, BATAS_UP_MAKSIMAL

# Import config
from ..core.config import ROOT_DIR


def format_rupiah(value: float) -> str:
    """Format angka ke format Rupiah."""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


class MainWindowV2(QMainWindow):
    """
    Main window untuk Asisten PPK Offline - Workflow Edition.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asisten PPK Offline - Workflow Edition v4.0")
        self.setMinimumSize(1200, 800)

        # Initialize database manager
        self.db = PencairanManager()

        # Page stack for navigation history
        self._page_stack = []

        # Setup UI
        self._setup_ui()
        self._load_stylesheet()
        self._connect_signals()

        # Initial data load
        self._refresh_data()

        # Auto-refresh timer (every 5 minutes)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_data)
        self._refresh_timer.start(300000)  # 5 minutes

    def _setup_ui(self):
        """Setup main window UI."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #f5f6fa;")
        main_layout.addWidget(self.content_stack, 1)

        # Create pages
        self._create_pages()

        # Status bar
        self._setup_status_bar()

        # Start on dashboard
        self._navigate_to("dashboard")

    def _create_pages(self):
        """Create all pages."""
        # Dashboard
        self.dashboard_page = DashboardPencairanPage()
        self.content_stack.addWidget(self.dashboard_page)

        # UP pages
        self.up_list_page = UPListPage()
        self.up_detail_page = UPDetailPage()
        self.up_form_page = TransaksiFormPage(mekanisme="UP")
        self.content_stack.addWidget(self.up_list_page)
        self.content_stack.addWidget(self.up_detail_page)
        self.content_stack.addWidget(self.up_form_page)

        # TUP pages
        self.tup_list_page = TUPListPage()
        self.tup_detail_page = TUPDetailPage()
        self.tup_form_page = TransaksiFormPage(mekanisme="TUP")
        self.content_stack.addWidget(self.tup_list_page)
        self.content_stack.addWidget(self.tup_detail_page)
        self.content_stack.addWidget(self.tup_form_page)

        # LS pages
        self.ls_list_page = LSListPage()
        self.ls_detail_page = LSDetailPage()
        self.ls_form_page = TransaksiFormPage(mekanisme="LS")
        self.content_stack.addWidget(self.ls_list_page)
        self.content_stack.addWidget(self.ls_detail_page)
        self.content_stack.addWidget(self.ls_form_page)

        # Page map for navigation
        self._page_map = {
            "dashboard": self.dashboard_page,
            "up": self.up_list_page,
            "up_detail": self.up_detail_page,
            "up_form": self.up_form_page,
            "tup": self.tup_list_page,
            "tup_detail": self.tup_detail_page,
            "tup_form": self.tup_form_page,
            "ls": self.ls_list_page,
            "ls_detail": self.ls_detail_page,
            "ls_form": self.ls_form_page,
        }

    def _setup_status_bar(self):
        """Setup status bar."""
        status_bar = QStatusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 5px 10px;
            }
            QStatusBar::item {
                border: none;
            }
        """)

        # Connection status
        self.conn_label = QLabel("Database: OK")
        self.conn_label.setStyleSheet("color: #27ae60;")
        status_bar.addWidget(self.conn_label)

        # Spacer
        spacer = QLabel(" | ")
        spacer.setStyleSheet("color: #7f8c8d;")
        status_bar.addWidget(spacer)

        # Saldo UP
        self.saldo_label = QLabel(f"Saldo UP: {format_rupiah(BATAS_UP_MAKSIMAL)}")
        self.saldo_label.setStyleSheet("color: #ecf0f1;")
        status_bar.addWidget(self.saldo_label)

        # Permanent widget on right
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #95a5a6;")
        status_bar.addPermanentWidget(self.status_label)

        self.setStatusBar(status_bar)

    def _load_stylesheet(self):
        """Load QSS stylesheet."""
        qss_path = os.path.join(ROOT_DIR, "app", "ui", "styles", "main.qss")

        if os.path.exists(qss_path):
            with open(qss_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        else:
            # Fallback basic styling
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f6fa;
                }
            """)

    def _connect_signals(self):
        """Connect all signals."""
        # Sidebar navigation
        self.sidebar.menu_clicked.connect(self._on_menu_clicked)

        # Dashboard signals
        self.dashboard_page.mekanisme_selected.connect(self._on_mekanisme_selected)
        self.dashboard_page.transaksi_selected.connect(self._on_transaksi_selected)
        self.dashboard_page.new_transaksi.connect(self._on_new_transaksi)

        # UP list signals
        self.up_list_page.new_clicked.connect(lambda: self._on_new_transaksi("UP"))
        self.up_list_page.item_double_clicked.connect(
            lambda id: self._on_transaksi_selected(id, "UP")
        )
        self.up_list_page.refresh_requested.connect(lambda: self._refresh_list("UP"))

        # UP detail signals
        self.up_detail_page.back_clicked.connect(lambda: self._navigate_to("up"))
        self.up_detail_page.save_clicked.connect(self._on_save_transaksi)
        self.up_detail_page.next_fase_clicked.connect(
            lambda: self._on_next_fase(self.up_detail_page._transaksi_id)
        )
        self.up_detail_page.dokumen_action.connect(self._on_dokumen_action)

        # UP form signals
        self.up_form_page.saved.connect(self._on_form_saved)
        self.up_form_page.cancelled.connect(lambda: self._navigate_to("up"))

        # TUP list signals
        self.tup_list_page.new_clicked.connect(lambda: self._on_new_transaksi("TUP"))
        self.tup_list_page.item_double_clicked.connect(
            lambda id: self._on_transaksi_selected(id, "TUP")
        )
        self.tup_list_page.refresh_requested.connect(lambda: self._refresh_list("TUP"))

        # TUP detail signals
        self.tup_detail_page.back_clicked.connect(lambda: self._navigate_to("tup"))
        self.tup_detail_page.save_clicked.connect(self._on_save_transaksi)
        self.tup_detail_page.next_fase_clicked.connect(
            lambda: self._on_next_fase(self.tup_detail_page._transaksi_id)
        )
        self.tup_detail_page.dokumen_action.connect(self._on_dokumen_action)

        # TUP form signals
        self.tup_form_page.saved.connect(self._on_form_saved)
        self.tup_form_page.cancelled.connect(lambda: self._navigate_to("tup"))

        # LS list signals
        self.ls_list_page.new_clicked.connect(lambda: self._on_new_transaksi("LS"))
        self.ls_list_page.item_double_clicked.connect(
            lambda id: self._on_transaksi_selected(id, "LS")
        )
        self.ls_list_page.refresh_requested.connect(lambda: self._refresh_list("LS"))

        # LS detail signals
        self.ls_detail_page.back_clicked.connect(lambda: self._navigate_to("ls"))
        self.ls_detail_page.save_clicked.connect(self._on_save_transaksi)
        self.ls_detail_page.next_fase_clicked.connect(
            lambda: self._on_next_fase(self.ls_detail_page._transaksi_id)
        )
        self.ls_detail_page.dokumen_action.connect(self._on_dokumen_action)

        # LS form signals
        self.ls_form_page.saved.connect(self._on_form_saved)
        self.ls_form_page.cancelled.connect(lambda: self._navigate_to("ls"))

    # =========================================================================
    # NAVIGATION
    # =========================================================================

    def _navigate_to(self, page_id: str, push_stack: bool = True):
        """Navigate to a page."""
        if page_id in self._page_map:
            page = self._page_map[page_id]
            self.content_stack.setCurrentWidget(page)

            if push_stack:
                self._page_stack.append(page_id)

            # Update sidebar active state
            self.sidebar.set_active_menu(page_id.split("_")[0])

            # Update status
            self.status_label.setText(f"Viewing: {page_id}")

    def _navigate_back(self):
        """Navigate to previous page."""
        if len(self._page_stack) > 1:
            self._page_stack.pop()  # Remove current
            prev_page = self._page_stack[-1]
            self._navigate_to(prev_page, push_stack=False)

    def _on_menu_clicked(self, menu_id: str):
        """Handle sidebar menu click."""
        if menu_id in ["dashboard", "up", "tup", "ls"]:
            self._navigate_to(menu_id)
            self._refresh_list(menu_id.upper() if menu_id != "dashboard" else None)
        elif menu_id == "paket":
            # Navigate to existing paket manager (integration with old system)
            self._show_legacy_page("paket")
        elif menu_id == "penyedia":
            self._show_legacy_page("penyedia")
        elif menu_id == "pegawai":
            self._show_legacy_page("pegawai")
        elif menu_id == "satker":
            self._show_legacy_page("satker")
        elif menu_id == "template":
            self._show_legacy_page("template")
        else:
            QMessageBox.information(
                self,
                "Menu",
                f"Menu '{menu_id}' akan diimplementasikan."
            )

    def _show_legacy_page(self, page_type: str):
        """Show legacy manager page (from old dashboard)."""
        try:
            if page_type == "satker":
                from .satker_manager import SatkerManager
                dialog = SatkerManager(self)
                dialog.exec()
            elif page_type == "pegawai":
                from .pegawai_manager import PegawaiManager
                dialog = PegawaiManager(self)
                # Refresh data setelah perubahan pegawai
                dialog.pegawai_changed.connect(self._refresh_data)
                dialog.exec()
            elif page_type == "template":
                from .template_manager import TemplateManagerDialog
                dialog = TemplateManagerDialog(self)
                dialog.exec()
            elif page_type == "penyedia":
                from .penyedia_manager import PenyediaManager
                dialog = PenyediaManager(self)
                dialog.exec()
            elif page_type == "paket":
                # Paket pekerjaan - masih menggunakan fitur dari dashboard lama
                QMessageBox.information(
                    self,
                    "Fitur Paket Pekerjaan",
                    "Untuk mengelola paket pekerjaan, silakan gunakan mode legacy:\n"
                    "python main.py --legacy"
                )
            else:
                QMessageBox.information(
                    self,
                    "Fitur",
                    f"Fitur '{page_type}' akan diimplementasikan."
                )
        except ImportError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Gagal membuka dialog {page_type}:\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Terjadi kesalahan:\n{str(e)}"
            )

    def _refresh_data(self):
        """Refresh data after master data changes."""
        # Refresh current list if viewing transaksi list
        current_page = self._page_stack[-1] if self._page_stack else "dashboard"
        if current_page in ["up", "tup", "ls"]:
            self._refresh_list(current_page.upper())

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def _on_mekanisme_selected(self, mekanisme: str):
        """Handle mekanisme card click on dashboard."""
        self._navigate_to(mekanisme.lower())
        self._refresh_list(mekanisme)

    def _on_transaksi_selected(self, transaksi_id: int, mekanisme: str = None):
        """Handle transaksi selection to show detail."""
        # Get transaksi data
        transaksi = self.db.get_transaksi(transaksi_id)
        if not transaksi:
            QMessageBox.warning(self, "Error", "Transaksi tidak ditemukan.")
            return

        mekanisme = mekanisme or transaksi.get('mekanisme', 'UP')

        # Navigate to appropriate detail page
        detail_page_id = f"{mekanisme.lower()}_detail"
        self._navigate_to(detail_page_id)

        # Load data into detail page
        detail_page = self._page_map.get(detail_page_id)
        if detail_page:
            detail_page.set_transaksi(transaksi_id, transaksi)

            # Load dokumen for current fase
            fase_aktif = transaksi.get('fase_aktif', 1)
            dokumen_list = self.db.get_dokumen_by_transaksi(transaksi_id, fase_aktif)
            detail_page.set_dokumen_list(dokumen_list)

            # Load fase log
            log_entries = self.db.get_fase_log(transaksi_id)
            detail_page.set_log_entries(log_entries)

    def _on_new_transaksi(self, mekanisme: str):
        """Handle new transaksi creation."""
        form_page_id = f"{mekanisme.lower()}_form"
        self._navigate_to(form_page_id)

        # Clear form
        form_page = self._page_map.get(form_page_id)
        if form_page:
            form_page.clear()

    def _on_form_saved(self, data: Dict[str, Any]):
        """Handle form save."""
        try:
            if data.get('id'):
                # Update existing
                self.db.update_transaksi(data['id'], data)
                self.status_label.setText("Transaksi berhasil diperbarui")
            else:
                # Create new
                transaksi_id = self.db.create_transaksi(data)
                self.status_label.setText(f"Transaksi baru berhasil dibuat (ID: {transaksi_id})")

            # Navigate back to list
            mekanisme = data.get('mekanisme', 'UP').lower()
            self._navigate_to(mekanisme)
            self._refresh_list(mekanisme.upper())

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Gagal menyimpan transaksi: {str(e)}"
            )

    def _on_save_transaksi(self, data: Dict[str, Any]):
        """Handle detail page save."""
        try:
            transaksi_id = data.get('id')
            if transaksi_id:
                self.db.update_transaksi(transaksi_id, data)
                self.status_label.setText("Perubahan tersimpan")
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Gagal menyimpan: {str(e)}"
            )

    def _on_next_fase(self, transaksi_id: int):
        """Handle next fase button."""
        transaksi = self.db.get_transaksi(transaksi_id)
        if not transaksi:
            return

        fase_aktif = transaksi.get('fase_aktif', 1)
        if fase_aktif >= 5:
            # Mark as completed
            self.db.update_status(transaksi_id, 'selesai')
            QMessageBox.information(
                self,
                "Selesai",
                "Transaksi telah diselesaikan!"
            )
            mekanisme = transaksi.get('mekanisme', 'UP').lower()
            self._navigate_to(mekanisme)
        else:
            # Advance to next fase
            try:
                self.db.update_fase(transaksi_id, fase_aktif + 1)
                self.status_label.setText(f"Maju ke Fase {fase_aktif + 1}")

                # Refresh detail page
                mekanisme = transaksi.get('mekanisme', 'UP')
                self._on_transaksi_selected(transaksi_id, mekanisme)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Gagal memajukan fase: {str(e)}"
                )

    def _on_dokumen_action(self, kode_dokumen: str, action: str, fase: int):
        """Handle document action (create, view, edit, upload)."""
        if action == "create":
            # Would integrate with template engine to generate document
            QMessageBox.information(
                self,
                "Buat Dokumen",
                f"Membuat dokumen {kode_dokumen} untuk Fase {fase}...\n"
                "(Integrasi dengan template engine)"
            )
        elif action == "view":
            QMessageBox.information(
                self,
                "Lihat Dokumen",
                f"Membuka dokumen {kode_dokumen}..."
            )
        elif action == "edit":
            QMessageBox.information(
                self,
                "Edit Dokumen",
                f"Mengedit dokumen {kode_dokumen}..."
            )
        elif action == "upload":
            QMessageBox.information(
                self,
                "Upload Dokumen",
                f"Upload dokumen {kode_dokumen}..."
            )

    # =========================================================================
    # DATA OPERATIONS
    # =========================================================================

    def _refresh_data(self):
        """Refresh all data from database."""
        try:
            # Get statistics for dashboard
            stats = {}
            for mekanisme in ["UP", "TUP", "LS"]:
                stat = self.db.get_statistik(mekanisme)
                stats[mekanisme] = {
                    'total': stat.get('total_transaksi', 0),
                    'nilai': stat.get('nilai', {}).get('total_estimasi', 0),
                    'selesai': stat.get('per_status', {}).get('selesai', 0),
                }

            self.dashboard_page.update_statistics(stats)

            # Update saldo UP
            saldo = self.db.get_saldo_up()
            tersedia = saldo.get('saldo_tersedia', BATAS_UP_MAKSIMAL)
            terpakai = saldo.get('total_penggunaan', 0)

            self.dashboard_page.update_saldo_up(tersedia, terpakai)
            self.saldo_label.setText(f"Saldo UP: {format_rupiah(tersedia)}")

            # Get active transactions
            aktif_list, _ = self.db.list_transaksi(status='aktif', limit=5)
            self.dashboard_page.set_transaksi_aktif(aktif_list)

            # Update sidebar badges
            up_count = stats["UP"].get('total', 0) - stats["UP"].get('selesai', 0)
            tup_count = stats["TUP"].get('total', 0) - stats["TUP"].get('selesai', 0)
            ls_count = stats["LS"].get('total', 0) - stats["LS"].get('selesai', 0)

            self.sidebar.update_badges({
                'up': up_count,
                'tup': tup_count,
                'ls': ls_count,
            })

            self.conn_label.setText("Database: OK")
            self.conn_label.setStyleSheet("color: #27ae60;")

        except Exception as e:
            self.conn_label.setText(f"Database: Error - {str(e)}")
            self.conn_label.setStyleSheet("color: #e74c3c;")

    def _refresh_list(self, mekanisme: str = None):
        """Refresh list data for specific mekanisme."""
        try:
            if mekanisme == "UP" or mekanisme is None:
                data, _ = self.db.list_transaksi(mekanisme="UP")
                self.up_list_page.set_data(data)

            if mekanisme == "TUP" or mekanisme is None:
                data, _ = self.db.list_transaksi(mekanisme="TUP")
                self.tup_list_page.set_data(data)

            if mekanisme == "LS" or mekanisme is None:
                data, _ = self.db.list_transaksi(mekanisme="LS")
                self.ls_list_page.set_data(data)

        except Exception as e:
            self.status_label.setText(f"Error loading data: {str(e)}")


def main():
    """Main entry point."""
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindowV2()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
