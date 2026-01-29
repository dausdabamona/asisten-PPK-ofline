"""
Dashboard Menu Handlers
========================
Handler methods for dashboard menu actions.

This module contains all menu action handlers to keep the main
dashboard file clean and focused on UI layout.

Author: PPK Document Factory Team
Version: 1.0
"""

import os
import sys
import traceback
from datetime import datetime
from typing import Callable, Optional

from PySide6.QtWidgets import (
    QMainWindow, QDialog, QVBoxLayout, QMessageBox, QFileDialog
)
from PySide6.QtCore import QTimer


class MenuHandlersMixin:
    """Mixin class providing menu handler methods for DashboardWindow.

    This mixin should be used with a class that has:
    - self.db: Database manager
    - self.current_paket_id: Current selected paket ID
    - self._load_paket_list(): Method to reload paket list
    - self._load_paket_detail(paket_id): Method to reload paket detail
    """

    # ========================================================================
    # PAKET MANAGER DIALOGS
    # ========================================================================

    def _open_item_barang_manager(self):
        """Open Item Barang Manager."""
        if not self._check_paket_selected():
            return
        self._open_manager_dialog(
            'app.ui.item_barang_manager', 'ItemBarangManager',
            paket_id=self.current_paket_id,
            signal_name='items_changed'
        )

    def _open_timeline_manager(self):
        """Open Timeline Manager."""
        if not self._check_paket_selected():
            return
        self._open_manager_dialog(
            'app.ui.timeline_manager', 'TimelineManager',
            paket_id=self.current_paket_id,
            signal_name='timeline_changed'
        )

    def _open_survey_toko_manager(self):
        """Open Survey Toko Manager."""
        if not self._check_paket_selected():
            return
        self._open_manager_dialog(
            'app.ui.survey_toko_manager', 'SurveyTokoManager',
            paket_id=self.current_paket_id,
            signal_name='data_changed'
        )

    def _open_checklist_spj(self):
        """Open Checklist SPJ Manager."""
        if not self._check_paket_selected():
            return
        self._open_manager_dialog(
            'app.ui.checklist_spj_manager', 'ChecklistDialog',
            paket_id=self.current_paket_id
        )

    def _open_foto_dokumentasi(self, jenis: str = 'BAHP'):
        """Open Foto Dokumentasi Manager."""
        if not self._check_paket_selected():
            return
        try:
            from app.ui.foto_dokumentasi_manager import FotoDokumentasiDialog
            dialog = FotoDokumentasiDialog(self.current_paket_id, jenis, self)
            dialog.exec()
        except Exception as e:
            self._show_error(e)

    def _open_paket_pejabat(self):
        """Open Paket Pejabat Manager."""
        if not self._check_paket_selected():
            return
        self._open_manager_dialog(
            'app.ui.paket_pejabat_manager', 'PaketPejabatManager',
            paket_id=self.current_paket_id,
            signal_name='pejabat_changed'
        )

    def _open_harga_lifecycle(self):
        """Open Harga Lifecycle Manager."""
        if not self._check_paket_selected():
            return
        self._open_manager_dialog(
            'app.ui.harga_lifecycle_manager', 'HargaLifecycleManager',
            paket_id=self.current_paket_id,
            signal_name='data_changed'
        )

    # ========================================================================
    # MASTER DATA
    # ========================================================================

    def _open_template_manager(self):
        """Open Template Manager."""
        self._open_manager_dialog('app.ui.template_manager', 'TemplateManagerDialog')

    def _open_pegawai_manager(self):
        """Open Pegawai Manager."""
        self._open_manager_dialog(
            'app.ui.pegawai_manager', 'PegawaiManager',
            signal_name='pegawai_changed',
            signal_callback=self._load_paket_list
        )

    def _open_penyedia_manager(self):
        """Open Penyedia Manager."""
        self._open_manager_dialog(
            'app.ui.penyedia_manager', 'PenyediaManager',
            signal_name='penyedia_changed',
            signal_callback=self._load_paket_list
        )

    def _open_satker_manager(self):
        """Open Satker Manager."""
        self._open_manager_dialog('app.ui.satker_manager', 'SatkerManager')

    def _backup_master_data(self):
        """Backup master data."""
        default_name = f"backup_master_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Backup Master Data", default_name, "JSON Files (*.json)"
        )
        if filepath and self.db.backup_master_data(filepath):
            QMessageBox.information(self, "Sukses", f"Backup berhasil disimpan ke:\n{filepath}")

    def _restore_master_data(self):
        """Restore master data."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Restore Master Data", "", "JSON Files (*.json)"
        )
        if not filepath:
            return

        reply = QMessageBox.question(
            self, "Konfirmasi",
            "Restore master data dari backup?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success_msg, errors = self.db.restore_master_data(filepath)
            if success_msg:
                QMessageBox.information(self, "Restore Selesai", success_msg)

    # ========================================================================
    # PERJALANAN DINAS
    # ========================================================================

    def _create_perjalanan_dinas(self):
        """Create new perjalanan dinas."""
        self._open_manager_dialog(
            'app.ui.perjalanan_dinas_manager', 'PerjalananDinasDialog'
        )

    def _list_perjalanan_dinas(self):
        """List perjalanan dinas."""
        self._open_manager_dialog(
            'app.ui.perjalanan_dinas_manager', 'PerjalananDinasManager'
        )

    # ========================================================================
    # SWAKELOLA
    # ========================================================================

    def _create_swakelola(self):
        """Create new swakelola kegiatan."""
        self._open_manager_dialog('app.ui.swakelola_manager', 'SwakelolaDialog')

    def _list_swakelola(self):
        """List swakelola kegiatan."""
        self._open_manager_dialog('app.ui.swakelola_manager', 'SwakelolaManager')

    # ========================================================================
    # PJLP
    # ========================================================================

    def _create_pjlp(self):
        """Create new PJLP contract."""
        try:
            from app.ui.pjlp_manager import PJLPDialog
            if PJLPDialog(parent=self).exec() == QDialog.DialogCode.Accepted:
                QMessageBox.information(self, "Sukses", "Kontrak PJLP berhasil dibuat!")
        except Exception as e:
            self._show_error(e)

    def _list_pjlp(self):
        """List PJLP contracts."""
        self._open_pjlp_manager(tab_index=0, title="PJLP Manager")

    def _pembayaran_pjlp(self):
        """Open PJLP pembayaran tab."""
        self._open_pjlp_manager(tab_index=1, title="Pembayaran PJLP")

    def _rekap_pjlp(self):
        """Open PJLP rekap tab."""
        self._open_pjlp_manager(tab_index=2, title="Rekap Pembayaran PJLP")

    def _open_pjlp_manager(self, tab_index: int = 0, title: str = "PJLP Manager"):
        """Open PJLP manager with specific tab."""
        try:
            from app.ui.pjlp_manager import PJLPManager
            dialog = QDialog(self)
            dialog.setWindowTitle(title)
            dialog.setMinimumSize(1200, 700)
            layout = QVBoxLayout(dialog)
            manager = PJLPManager(dialog)
            if tab_index > 0:
                manager.tabs.setCurrentIndex(tab_index)
            layout.addWidget(manager)
            dialog.exec()
        except Exception as e:
            self._show_error(e)

    # ========================================================================
    # PEMBAYARAN LAINNYA
    # ========================================================================

    def _manage_sk_kpa(self):
        """Manage SK KPA."""
        self._open_pembayaran_lainnya(tab_index=0, title="SK KPA")

    def _manage_honorarium(self):
        """Manage Honorarium."""
        self._open_pembayaran_lainnya(tab_index=1, title="Honorarium")

    def _manage_jamuan_tamu(self):
        """Manage Jamuan Tamu."""
        self._open_pembayaran_lainnya(tab_index=2, title="Jamuan Tamu")

    def _manage_pembayaran_lainnya(self):
        """Open all pembayaran lainnya."""
        self._open_pembayaran_lainnya(tab_index=None, title="Pembayaran Lainnya")

    def _open_pembayaran_lainnya(self, tab_index: Optional[int] = None, title: str = "Pembayaran"):
        """Open Pembayaran Lainnya manager with specific tab."""
        try:
            from app.ui.pembayaran_lainnya_manager import PembayaranLainnyaManager
            dialog = QDialog(self)
            dialog.setWindowTitle(title)
            dialog.setMinimumSize(1200, 700)
            layout = QVBoxLayout(dialog)
            manager = PembayaranLainnyaManager(dialog)
            if tab_index is not None:
                manager.tabs.setCurrentIndex(tab_index)
            layout.addWidget(manager)
            dialog.exec()
        except Exception as e:
            self._show_error(e)

    # ========================================================================
    # FA DETAIL
    # ========================================================================

    def _manage_fa_detail(self):
        """Manage FA Detail (POK)."""
        self._open_fa_detail_manager(tab_index=0, title="FA Detail - Pagu Anggaran (POK)")

    def _import_fa_excel(self):
        """Import FA from Excel."""
        try:
            from app.ui.fa_detail_manager import FADetailManager
            dialog = QDialog(self)
            dialog.setWindowTitle("FA Detail - Import Excel")
            dialog.setMinimumSize(1300, 800)
            layout = QVBoxLayout(dialog)
            manager = FADetailManager(dialog)
            layout.addWidget(manager)
            # Trigger import after dialog shows
            QTimer.singleShot(100, manager.import_excel)
            dialog.exec()
        except Exception as e:
            self._show_error(e)

    def _rekap_fa_akun(self):
        """Show FA rekap per akun."""
        self._open_fa_detail_manager(tab_index=1, title="FA Detail - Rekap per Akun")

    def _monitoring_realisasi(self):
        """Show monitoring realisasi."""
        self._open_fa_detail_manager(tab_index=2, title="FA Detail - Monitoring Realisasi")

    def _open_fa_detail_manager(self, tab_index: int = 0, title: str = "FA Detail"):
        """Open FA Detail manager with specific tab."""
        try:
            from app.ui.fa_detail_manager import FADetailManager
            dialog = QDialog(self)
            dialog.setWindowTitle(title)
            dialog.setMinimumSize(1300, 800)
            layout = QVBoxLayout(dialog)
            manager = FADetailManager(dialog)
            if tab_index > 0:
                manager.tab_widget.setCurrentIndex(tab_index)
            layout.addWidget(manager)
            dialog.exec()
        except Exception as e:
            self._show_error(e)

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _check_paket_selected(self) -> bool:
        """Check if a paket is selected, show warning if not."""
        if not self.current_paket_id:
            QMessageBox.warning(self, "Peringatan", "Pilih paket terlebih dahulu!")
            return False
        return True

    def _open_manager_dialog(
        self,
        module_path: str,
        class_name: str,
        paket_id: Optional[int] = None,
        signal_name: Optional[str] = None,
        signal_callback: Optional[Callable] = None
    ):
        """Generic method to open a manager dialog.

        Args:
            module_path: Full module path (e.g., 'app.ui.pegawai_manager')
            class_name: Dialog class name
            paket_id: Optional paket ID to pass to constructor
            signal_name: Optional signal name to connect
            signal_callback: Optional callback for signal (defaults to reload paket detail)
        """
        try:
            import importlib
            module = importlib.import_module(module_path)
            dialog_class = getattr(module, class_name)

            if paket_id is not None:
                dialog = dialog_class(paket_id, self)
            else:
                dialog = dialog_class(self)

            if signal_name:
                signal = getattr(dialog, signal_name, None)
                if signal:
                    if signal_callback:
                        signal.connect(signal_callback)
                    elif paket_id and hasattr(self, '_load_paket_detail'):
                        signal.connect(lambda: self._load_paket_detail(self.current_paket_id))

            dialog.exec()
        except Exception as e:
            self._show_error(e)

    def _show_error(self, e: Exception):
        """Show error message dialog."""
        QMessageBox.critical(
            self, "Error",
            f"Terjadi error:\n{str(e)}\n\n{traceback.format_exc()}"
        )
