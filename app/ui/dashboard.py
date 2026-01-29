"""
PPK DOCUMENT FACTORY v4.0 - Main Dashboard UI
==============================================
Workflow-based document generation dashboard.

Modular structure:
- StageWidget: app.ui.components.stage_widget
- PaketFormDialog: app.ui.dialogs.paket_form_dialog
- GenerateDocumentDialog: app.ui.dialogs.generate_document_dialog
- Menu handlers: app.ui.menu_handlers
- Styles: app.ui.styles.dashboard_styles

Author: PPK Document Factory Team
Version: 4.0
"""

import sys
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QGroupBox,
    QTreeWidget, QTreeWidgetItem, QProgressBar,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QAction

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import (
    TAHUN_ANGGARAN, OUTPUT_DIR, SATKER_DEFAULT, WORKFLOW_STAGES
)
from app.core.database import get_db_manager
from app.templates.engine import get_template_manager, format_rupiah
from app.workflow.engine import get_workflow_engine, StageStatus

# Import modular components
from app.ui.components.stage_widget import StageWidget
from app.ui.dialogs import PaketFormDialog, GenerateDocumentDialog
from app.ui.menu_handlers import MenuHandlersMixin
from app.ui.styles import DASHBOARD_STYLE


class DashboardWindow(MenuHandlersMixin, QMainWindow):
    """Main Dashboard Window.

    Uses MenuHandlersMixin for all menu action handlers.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PPK Document Factory v4.0 - {SATKER_DEFAULT['nama_pendek']} - TA {TAHUN_ANGGARAN}")
        self.setMinimumSize(1400, 900)

        self.db = get_db_manager()
        self.workflow = get_workflow_engine()
        self.template_manager = get_template_manager()

        self.current_paket_id = None

        self._setup_ui()
        self.setStyleSheet(DASHBOARD_STYLE)

        self._load_paket_list()

    def _setup_ui(self):
        """Setup main UI."""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Left panel - Paket list
        main_layout.addWidget(self._create_left_panel())

        # Right panel - Workflow
        main_layout.addWidget(self._create_right_panel())

        # Status bar
        self.statusBar().showMessage(f"📁 Output: {OUTPUT_DIR}")

        # Menu bar
        self._setup_menu()

    def _create_left_panel(self) -> QWidget:
        """Create left panel with paket list."""
        panel = QWidget()
        panel.setMaximumWidth(350)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QHBoxLayout()
        lbl = QLabel("📋 Daftar Paket")
        lbl.setObjectName("titleLabel")
        header.addWidget(lbl)
        header.addStretch()

        btn_add = QPushButton("➕ Tambah")
        btn_add.clicked.connect(self._add_paket)
        header.addWidget(btn_add)
        layout.addLayout(header)

        # Search
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Cari paket...")
        self.txt_search.textChanged.connect(self._filter_paket_list)
        layout.addWidget(self.txt_search)

        # Paket list
        self.paket_list = QListWidget()
        self.paket_list.itemClicked.connect(self._on_paket_selected)
        layout.addWidget(self.paket_list)

        return panel

    def _create_right_panel(self) -> QWidget:
        """Create right panel with workflow."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Paket info header
        layout.addWidget(self._create_paket_info_group())

        # Workflow stages
        layout.addWidget(self._create_workflow_group())

        return panel

    def _create_paket_info_group(self) -> QGroupBox:
        """Create paket info group box."""
        group = QGroupBox("Informasi Paket")
        layout = QGridLayout(group)

        # Row 0: Nama
        self.lbl_paket_nama = QLabel("-")
        self.lbl_paket_nama.setFont(QFont("", 14, QFont.Weight.Bold))
        layout.addWidget(QLabel("Nama:"), 0, 0)
        layout.addWidget(self.lbl_paket_nama, 0, 1, 1, 3)

        # Row 1: Nilai & Penyedia
        self.lbl_paket_nilai = QLabel("-")
        self.lbl_paket_penyedia = QLabel("-")
        layout.addWidget(QLabel("Nilai Kontrak:"), 1, 0)
        layout.addWidget(self.lbl_paket_nilai, 1, 1)
        layout.addWidget(QLabel("Penyedia:"), 1, 2)
        layout.addWidget(self.lbl_paket_penyedia, 1, 3)

        # Row 2: Progress
        self.progress_workflow = QProgressBar()
        self.progress_workflow.setFormat("%p% Selesai")
        layout.addWidget(QLabel("Progress:"), 2, 0)
        layout.addWidget(self.progress_workflow, 2, 1, 1, 3)

        # Action buttons
        self._add_action_buttons(layout)

        return group

    def _add_action_buttons(self, layout: QGridLayout):
        """Add action buttons to paket info layout."""
        buttons = [
            # Row 3
            (3, 0, "✏️ Edit Paket", self._edit_paket, None),
            (3, 1, "📦 Daftar Item", self._open_item_barang_manager, "Kelola Daftar Kebutuhan Barang"),
            (3, 2, "📅 Timeline", self._open_timeline_manager, "Kelola Tanggal & Penomoran"),
            (3, 3, "📂 Buka Folder", self._open_paket_folder, None),
            # Row 4
            (4, 0, "👥 Pejabat & Tim", self._open_paket_pejabat, None),
            (4, 1, "💰 Lifecycle Harga", self._open_harga_lifecycle, None),
            (4, 2, "🏪 Survey Toko", self._open_survey_toko_manager, None),
            # Row 5
            (5, 0, "📋 Checklist SPJ", self._open_checklist_spj, None),
            (5, 1, "📷 Foto BAHP", lambda: self._open_foto_dokumentasi('BAHP'), None),
        ]

        for row, col, text, handler, tooltip in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            if tooltip:
                btn.setToolTip(tooltip)
            if "Checklist" in text:
                btn.setStyleSheet("background-color: #27ae60;")
            elif "Foto" in text:
                btn.setStyleSheet("background-color: #9b59b6;")
            layout.addWidget(btn, row, col)

        # Row 6: Generate all
        btn_batch = QPushButton("🚀 Generate Semua Dokumen")
        btn_batch.setObjectName("btnSuccess")
        btn_batch.clicked.connect(self._generate_all_pending)
        layout.addWidget(btn_batch, 6, 0, 1, 4)

    def _create_workflow_group(self) -> QGroupBox:
        """Create workflow group box."""
        group = QGroupBox("Workflow Pengadaan")
        layout = QVBoxLayout(group)

        # Stage widgets in grid
        self.stage_grid = QGridLayout()
        self.stage_widgets = {}

        for i, stage in enumerate(WORKFLOW_STAGES):
            widget = StageWidget(stage['code'], stage['name'])
            widget.clicked.connect(self._on_stage_clicked)
            self.stage_widgets[stage['code']] = widget
            self.stage_grid.addWidget(widget, i // 5, i % 5)

        layout.addLayout(self.stage_grid)

        # Documents list
        self.doc_tree = QTreeWidget()
        self.doc_tree.setHeaderLabels(["Dokumen", "Nomor", "Tanggal", "Status"])
        self.doc_tree.setMinimumHeight(200)
        layout.addWidget(self.doc_tree)

        return group

    def _setup_menu(self):
        """Setup menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        self._add_menu_action(file_menu, "&Paket Baru", self._add_paket, "Ctrl+N")
        file_menu.addSeparator()
        self._add_menu_action(file_menu, "&Keluar", self.close, "Ctrl+Q")

        # Master Data menu
        master_menu = menubar.addMenu("&Master Data")
        self._add_menu_action(master_menu, "👥 Data Pegawai", self._open_pegawai_manager, "Ctrl+P")
        self._add_menu_action(master_menu, "🏢 Data Penyedia", self._open_penyedia_manager)
        master_menu.addSeparator()
        self._add_menu_action(master_menu, "🏛️ Data Satker", self._open_satker_manager)
        master_menu.addSeparator()
        self._add_menu_action(master_menu, "💾 Backup Master Data", self._backup_master_data)
        self._add_menu_action(master_menu, "📂 Restore Master Data", self._restore_master_data)

        # Perjalanan Dinas menu
        pd_menu = menubar.addMenu("&Perjalanan Dinas")
        self._add_menu_action(pd_menu, "✈️ Buat Perjalanan Dinas Baru", self._create_perjalanan_dinas)
        self._add_menu_action(pd_menu, "📋 Daftar Perjalanan Dinas", self._list_perjalanan_dinas)

        # Swakelola menu
        sw_menu = menubar.addMenu("&Swakelola")
        self._add_menu_action(sw_menu, "📝 Buat Kegiatan Swakelola Baru", self._create_swakelola)
        self._add_menu_action(sw_menu, "📋 Daftar Kegiatan Swakelola", self._list_swakelola)

        # PJLP menu
        pjlp_menu = menubar.addMenu("&PJLP")
        self._add_menu_action(pjlp_menu, "📝 Buat Kontrak PJLP Baru", self._create_pjlp)
        self._add_menu_action(pjlp_menu, "📋 Daftar Kontrak PJLP", self._list_pjlp)
        pjlp_menu.addSeparator()
        self._add_menu_action(pjlp_menu, "💰 Pembayaran Bulanan", self._pembayaran_pjlp)
        self._add_menu_action(pjlp_menu, "📊 Rekap Pembayaran", self._rekap_pjlp)

        # Pembayaran menu
        bayar_menu = menubar.addMenu("Pem&bayaran")
        self._add_menu_action(bayar_menu, "📜 SK KPA", self._manage_sk_kpa)
        bayar_menu.addSeparator()
        self._add_menu_action(bayar_menu, "💵 Honorarium", self._manage_honorarium)
        bayar_menu.addSeparator()
        self._add_menu_action(bayar_menu, "🍽️ Jamuan Tamu", self._manage_jamuan_tamu)
        bayar_menu.addSeparator()
        self._add_menu_action(bayar_menu, "📊 Lihat Semua Pembayaran", self._manage_pembayaran_lainnya)

        # FA Detail menu
        fa_menu = menubar.addMenu("&FA Detail")
        self._add_menu_action(fa_menu, "📋 Pagu Anggaran (POK)", self._manage_fa_detail)
        self._add_menu_action(fa_menu, "📥 Import Pagu dari Excel", self._import_fa_excel)
        fa_menu.addSeparator()
        self._add_menu_action(fa_menu, "📊 Rekap per Akun", self._rekap_fa_akun)
        self._add_menu_action(fa_menu, "💰 Monitoring Realisasi", self._monitoring_realisasi)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        self._add_menu_action(tools_menu, "📄 Template Manager", self._open_template_manager)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        self._add_menu_action(help_menu, "&Tentang", self._show_about)

    def _add_menu_action(self, menu, text, handler, shortcut=None):
        """Helper to add menu action."""
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(handler)
        menu.addAction(action)

    # ========================================================================
    # PAKET LIST METHODS
    # ========================================================================

    def _load_paket_list(self):
        """Load paket list from database."""
        self.paket_list.clear()

        for paket in self.db.get_paket_list(tahun=TAHUN_ANGGARAN):
            icon = {'draft': '📝', 'in_progress': '🔄', 'completed': '✅', 'cancelled': '❌'}.get(paket.get('status', 'draft'), '📝')
            item = QListWidgetItem(f"{icon} {paket['kode']}\n{paket['nama'][:40]}...")
            item.setData(Qt.ItemDataRole.UserRole, paket['id'])
            self.paket_list.addItem(item)

    def _filter_paket_list(self, text: str):
        """Filter paket list by search text."""
        for i in range(self.paket_list.count()):
            item = self.paket_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _on_paket_selected(self, item: QListWidgetItem):
        """Handle paket selection."""
        self.current_paket_id = item.data(Qt.ItemDataRole.UserRole)
        self._load_paket_detail(self.current_paket_id)

    def _load_paket_detail(self, paket_id: int):
        """Load paket detail and workflow."""
        paket = self.db.get_paket(paket_id)
        if not paket:
            return

        # Update info
        self.lbl_paket_nama.setText(paket['nama'])
        self.lbl_paket_nilai.setText(format_rupiah(paket.get('nilai_kontrak', 0)))
        self.lbl_paket_penyedia.setText(paket.get('penyedia_nama', '-'))

        # Load workflow
        overview = self.workflow.get_workflow_overview(paket_id)
        self.progress_workflow.setValue(int(overview['progress']))

        # Update stage widgets
        for stage_info in overview['stages']:
            widget = self.stage_widgets.get(stage_info.code)
            if widget:
                widget.set_status(stage_info.status.value, stage_info.is_current, stage_info.is_allowed)

        # Load documents
        self.doc_tree.clear()
        for stage_info in overview['stages']:
            if stage_info.documents:
                stage_item = QTreeWidgetItem([stage_info.name, "", "", ""])
                stage_item.setExpanded(True)

                for doc in stage_info.documents:
                    doc_item = QTreeWidgetItem([
                        doc['doc_type'], doc.get('nomor', '-'),
                        str(doc.get('tanggal', '-')), doc.get('status', 'draft')
                    ])
                    doc_item.setData(0, Qt.ItemDataRole.UserRole, doc.get('filepath'))
                    stage_item.addChild(doc_item)

                self.doc_tree.addTopLevelItem(stage_item)

        self.doc_tree.expandAll()

    # ========================================================================
    # PAKET ACTIONS
    # ========================================================================

    def _add_paket(self):
        """Add new paket."""
        dialog = PaketFormDialog(parent=self)
        if dialog.exec():
            self._load_paket_list()
            for i in range(self.paket_list.count()):
                item = self.paket_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == dialog.paket_id:
                    self.paket_list.setCurrentItem(item)
                    self._on_paket_selected(item)
                    break

    def _edit_paket(self):
        """Edit current paket."""
        if not self._check_paket_selected():
            return
        dialog = PaketFormDialog(self.current_paket_id, self)
        if dialog.exec():
            self._load_paket_list()
            self._load_paket_detail(self.current_paket_id)

    def _on_stage_clicked(self, stage_code: str):
        """Handle stage click."""
        if not self.current_paket_id:
            return
        dialog = GenerateDocumentDialog(self.current_paket_id, stage_code, self)
        if dialog.exec():
            self._load_paket_detail(self.current_paket_id)
            self._load_paket_list()

    def _generate_all_pending(self):
        """Generate all pending documents."""
        if not self._check_paket_selected():
            return

        if QMessageBox.question(
            self, "Konfirmasi", "Generate semua dokumen yang belum selesai?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) != QMessageBox.StandardButton.Yes:
            return

        overview = self.workflow.get_workflow_overview(self.current_paket_id)
        for stage_info in overview['stages']:
            if stage_info.status == StageStatus.PENDING and stage_info.is_allowed:
                GenerateDocumentDialog(self.current_paket_id, stage_info.code, self).exec()

        self._load_paket_detail(self.current_paket_id)
        self._load_paket_list()

    def _open_paket_folder(self):
        """Open paket output folder."""
        if not self.current_paket_id:
            return

        paket = self.db.get_paket(self.current_paket_id)
        if not paket:
            return

        import re
        folder_name = re.sub(r'[<>:"/\\|?*]', '_', f"{paket['kode']}_{paket['nama'][:30]}")
        folder_path = os.path.join(OUTPUT_DIR, str(TAHUN_ANGGARAN), folder_name)
        os.makedirs(folder_path, exist_ok=True)

        if sys.platform == 'win32':
            os.startfile(folder_path)
        elif sys.platform == 'darwin':
            os.system(f'open "{folder_path}"')
        else:
            os.system(f'xdg-open "{folder_path}"')

    # ========================================================================
    # ABOUT
    # ========================================================================

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "Tentang",
            f"PPK Document Factory v4.0\n\n"
            f"Template-Driven Procurement Workflow System\n\n"
            f"Fitur:\n"
            f"• Workflow pengadaan lengkap\n"
            f"• Template Word/Excel yang dapat diedit\n"
            f"• Penomoran otomatis\n"
            f"• Output terorganisir per paket\n\n"
            f"© {TAHUN_ANGGARAN} PPK Digital Assistant"
        )


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = DashboardWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
