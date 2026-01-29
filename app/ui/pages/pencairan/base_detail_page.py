"""
PPK DOCUMENT FACTORY - Base Detail Page
========================================
Base class for transaksi detail pages with fase stepper and document checklist.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QFrame, QSplitter, QSizePolicy,
    QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt, Signal

from typing import Dict, Any, List, Optional

# Import components
from ...components.fase_stepper import FaseStepper
from ...components.dokumen_checklist import DokumenChecklist
from ...components.kalkulasi_widget import KalkulasiWidget


def format_rupiah(value: float) -> str:
    """Format angka ke format Rupiah."""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


class BaseDetailPage(QWidget):
    """
    Base class for detail pages.

    Signals:
        back_clicked(): Emitted when back button is clicked
        save_clicked(dict): Emitted when save button is clicked
        next_fase_clicked(): Emitted when next fase button is clicked
        dokumen_action(str, str, int): kode_dokumen, action, fase
    """

    back_clicked = Signal()
    save_clicked = Signal(dict)
    next_fase_clicked = Signal()
    dokumen_action = Signal(str, str, int)

    # Override in subclasses
    MEKANISME = "UP"
    COLOR = "#3498db"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._transaksi_id: Optional[int] = None
        self._transaksi_data: Dict[str, Any] = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup detail page UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header with back button
        header = self._create_header()
        main_layout.addWidget(header)

        # Info bar
        self.info_bar = self._create_info_bar()
        main_layout.addWidget(self.info_bar)

        # Fase stepper
        self.fase_stepper = FaseStepper(mekanisme=self.MEKANISME)
        self.fase_stepper.fase_clicked.connect(self._on_fase_clicked)
        main_layout.addWidget(self.fase_stepper)

        # Content area with splitter
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setHandleWidth(1)

        # Left: Document checklist
        self.checklist = DokumenChecklist(fase=1)
        self.checklist.dokumen_action.connect(
            lambda kode, action, fase: self.dokumen_action.emit(kode, action, fase)
        )
        self.checklist.setMinimumWidth(400)
        content_splitter.addWidget(self.checklist)

        # Right: Detail panel (can include kalkulasi for fase 4)
        self.detail_panel = self._create_detail_panel()
        content_splitter.addWidget(self.detail_panel)

        content_splitter.setSizes([500, 400])
        main_layout.addWidget(content_splitter, 1)

        # Action bar at bottom
        action_bar = self._create_action_bar()
        main_layout.addWidget(action_bar)

    def _create_header(self) -> QWidget:
        """Create page header."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 10)

        # Back button
        back_btn = QPushButton("< Kembali")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #2980b9;
                text-decoration: underline;
            }
        """)
        back_btn.clicked.connect(self.back_clicked.emit)
        layout.addWidget(back_btn)

        layout.addStretch()

        # Mekanisme badge
        self.mekanisme_badge = QLabel(self.MEKANISME)
        self.mekanisme_badge.setStyleSheet(f"""
            background-color: {self.COLOR};
            color: white;
            border-radius: 12px;
            padding: 4px 12px;
            font-weight: bold;
            font-size: 12px;
        """)
        layout.addWidget(self.mekanisme_badge)

        return header

    def _create_info_bar(self) -> QWidget:
        """Create transaksi info bar."""
        bar = QFrame()
        bar.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(30)

        # Kode transaksi
        kode_layout = QVBoxLayout()
        kode_layout.setSpacing(4)

        kode_label = QLabel("Kode Transaksi")
        kode_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        kode_layout.addWidget(kode_label)

        self.kode_value = QLabel("-")
        self.kode_value.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        kode_layout.addWidget(self.kode_value)

        layout.addLayout(kode_layout)

        # Nama kegiatan
        nama_layout = QVBoxLayout()
        nama_layout.setSpacing(4)

        nama_label = QLabel("Nama Kegiatan")
        nama_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        nama_layout.addWidget(nama_label)

        self.nama_value = QLabel("-")
        self.nama_value.setStyleSheet("font-size: 14px; font-weight: 500; color: #2c3e50;")
        nama_layout.addWidget(self.nama_value)

        layout.addLayout(nama_layout, 1)

        # Status
        status_layout = QVBoxLayout()
        status_layout.setSpacing(4)
        status_layout.setAlignment(Qt.AlignRight)

        status_label = QLabel("Status")
        status_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        status_label.setAlignment(Qt.AlignRight)
        status_layout.addWidget(status_label)

        self.status_badge = QLabel("Draft")
        self.status_badge.setStyleSheet("""
            background-color: #bdc3c7;
            color: white;
            border-radius: 10px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: bold;
        """)
        status_layout.addWidget(self.status_badge, alignment=Qt.AlignRight)

        layout.addLayout(status_layout)

        # Nilai
        nilai_layout = QVBoxLayout()
        nilai_layout.setSpacing(4)
        nilai_layout.setAlignment(Qt.AlignRight)

        nilai_label = QLabel("Estimasi Biaya")
        nilai_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        nilai_label.setAlignment(Qt.AlignRight)
        nilai_layout.addWidget(nilai_label)

        self.nilai_value = QLabel("Rp 0")
        self.nilai_value.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {self.COLOR};")
        nilai_layout.addWidget(self.nilai_value, alignment=Qt.AlignRight)

        layout.addLayout(nilai_layout)

        return bar

    def _create_detail_panel(self) -> QWidget:
        """Create right detail panel."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Tabs for different sections
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                background-color: #f5f6fa;
                color: #7f8c8d;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #3498db;
                font-weight: 500;
            }
        """)

        # Info tab
        info_widget = self._create_info_tab()
        tabs.addTab(info_widget, "Informasi")

        # Kalkulasi tab (for fase 4) - enable rincian for UP/TUP workflows
        show_rincian = self.MEKANISME in ("UP", "TUP")
        self.kalkulasi_widget = KalkulasiWidget(show_rincian=show_rincian)
        tabs.addTab(self.kalkulasi_widget, "Kalkulasi")

        # Log tab
        log_widget = self._create_log_tab()
        tabs.addTab(log_widget, "Riwayat")

        layout.addWidget(tabs)

        return panel

    def _create_info_tab(self) -> QWidget:
        """Create info tab content."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)

        # Penerima info
        penerima_frame = QFrame()
        penerima_frame.setObjectName("penerimaFrame")
        penerima_frame.setStyleSheet("""
            #penerimaFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        penerima_layout = QVBoxLayout(penerima_frame)
        penerima_layout.setSpacing(8)

        penerima_title = QLabel("Penerima / Pelaksana")
        penerima_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #2c3e50; background-color: transparent;")
        penerima_layout.addWidget(penerima_title)

        self.penerima_nama_label = QLabel("Nama: -")
        self.penerima_nama_label.setStyleSheet("font-size: 12px; color: #2c3e50; background-color: transparent;")
        penerima_layout.addWidget(self.penerima_nama_label)

        self.penerima_nip_label = QLabel("NIP: -")
        self.penerima_nip_label.setStyleSheet("font-size: 12px; color: #7f8c8d; background-color: transparent;")
        penerima_layout.addWidget(self.penerima_nip_label)

        layout.addWidget(penerima_frame)

        # Dasar hukum
        dasar_frame = QFrame()
        dasar_frame.setObjectName("dasarFrame")
        dasar_frame.setStyleSheet("""
            #dasarFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        dasar_layout = QVBoxLayout(dasar_frame)
        dasar_layout.setSpacing(8)

        dasar_title = QLabel("Dasar Hukum")
        dasar_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #2c3e50; background-color: transparent;")
        dasar_layout.addWidget(dasar_title)

        self.dasar_nomor_label = QLabel("Nomor: -")
        self.dasar_nomor_label.setStyleSheet("font-size: 12px; color: #2c3e50; background-color: transparent;")
        dasar_layout.addWidget(self.dasar_nomor_label)

        self.dasar_tanggal_label = QLabel("Tanggal: -")
        self.dasar_tanggal_label.setStyleSheet("font-size: 12px; color: #7f8c8d; background-color: transparent;")
        dasar_layout.addWidget(self.dasar_tanggal_label)

        layout.addWidget(dasar_frame)

        # Document status checklist
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_frame.setStyleSheet("""
            #statusFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(8)

        status_title = QLabel("Status Kelengkapan Dokumen")
        status_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #2c3e50; background-color: transparent;")
        status_layout.addWidget(status_title)

        # Progress bar
        self.doc_progress_frame = QFrame()
        self.doc_progress_frame.setFixedHeight(8)
        self.doc_progress_frame.setStyleSheet("background-color: #e0e0e0; border-radius: 4px;")
        progress_layout = QHBoxLayout(self.doc_progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(0)

        self.doc_progress_bar = QFrame()
        self.doc_progress_bar.setStyleSheet("background-color: #3498db; border-radius: 4px;")
        progress_layout.addWidget(self.doc_progress_bar)
        progress_layout.addStretch()

        status_layout.addWidget(self.doc_progress_frame)

        self.doc_progress_label = QLabel("0 / 0 dokumen (0%)")
        self.doc_progress_label.setStyleSheet("font-size: 11px; color: #7f8c8d; background-color: transparent;")
        status_layout.addWidget(self.doc_progress_label)

        # Warning for missing docs
        self.doc_warning_label = QLabel("")
        self.doc_warning_label.setStyleSheet("""
            font-size: 11px;
            color: #e74c3c;
            background-color: #fadbd8;
            padding: 5px 8px;
            border-radius: 3px;
        """)
        self.doc_warning_label.setWordWrap(True)
        self.doc_warning_label.setVisible(False)
        status_layout.addWidget(self.doc_warning_label)

        # Missing document list
        self.missing_docs_label = QLabel("")
        self.missing_docs_label.setStyleSheet("font-size: 10px; color: #7f8c8d; background-color: transparent;")
        self.missing_docs_label.setWordWrap(True)
        self.missing_docs_label.setVisible(False)
        status_layout.addWidget(self.missing_docs_label)

        layout.addWidget(status_frame)

        # ========== Dokumen yang Sudah Dibuat ==========
        docs_frame = QFrame()
        docs_frame.setObjectName("docsFrame")
        docs_frame.setStyleSheet("""
            #docsFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        docs_layout = QVBoxLayout(docs_frame)
        docs_layout.setSpacing(8)

        docs_title = QLabel("📋 Status Dokumen Per Fase")
        docs_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #2c3e50; background-color: transparent;")
        docs_layout.addWidget(docs_title)

        # Scroll area for document list per fase
        docs_scroll = QScrollArea()
        docs_scroll.setWidgetResizable(True)
        docs_scroll.setFrameShape(QFrame.NoFrame)
        docs_scroll.setMaximumHeight(300)
        docs_scroll.setStyleSheet("background-color: transparent;")

        docs_scroll_widget = QWidget()
        docs_scroll_widget.setStyleSheet("background-color: transparent;")
        self.docs_per_fase_layout = QVBoxLayout(docs_scroll_widget)
        self.docs_per_fase_layout.setSpacing(8)
        self.docs_per_fase_layout.setContentsMargins(0, 0, 0, 0)

        # Placeholder
        self.docs_empty_label = QLabel("Memuat dokumen...")
        self.docs_empty_label.setStyleSheet("font-size: 11px; color: #95a5a6; font-style: italic; background-color: transparent;")
        self.docs_per_fase_layout.addWidget(self.docs_empty_label)

        docs_scroll.setWidget(docs_scroll_widget)
        docs_layout.addWidget(docs_scroll)

        layout.addWidget(docs_frame)

        layout.addStretch()

        return widget

    def _create_log_tab(self) -> QWidget:
        """Create log/history tab content."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)

        self.log_container = QVBoxLayout()
        self.log_container.setSpacing(10)

        # Empty state
        empty = QLabel("Belum ada riwayat")
        empty.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 20px;")
        empty.setAlignment(Qt.AlignCenter)
        self.log_container.addWidget(empty)

        layout.addLayout(self.log_container)
        layout.addStretch()

        return widget

    def _create_action_bar(self) -> QWidget:
        """Create bottom action bar."""
        bar = QFrame()
        bar.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(15, 12, 15, 12)

        # Left: Status info
        self.fase_info_label = QLabel("Fase 1: Inisiasi & SK")
        self.fase_info_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        layout.addWidget(self.fase_info_label)

        layout.addStretch()

        # Prepare documents button (for PERJALANAN/SWAKELOLA activities)
        self.prepare_btn = QPushButton("Persiapan Dokumen")
        self.prepare_btn.setCursor(Qt.PointingHandCursor)
        self.prepare_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.prepare_btn.clicked.connect(self._on_prepare_dokumen)
        self.prepare_btn.setVisible(False)  # Hidden by default
        layout.addWidget(self.prepare_btn)

        # Save button
        save_btn = QPushButton("Simpan Perubahan")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)

        # Next fase button
        self.next_btn = QPushButton("Lanjut ke Fase Berikutnya >")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(self.COLOR)};
            }}
        """)
        self.next_btn.clicked.connect(self._on_next_fase)
        layout.addWidget(self.next_btn)

        return bar

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color."""
        darken_map = {
            "#27ae60": "#1e8449",
            "#f39c12": "#d68910",
            "#3498db": "#2980b9",
        }
        return darken_map.get(hex_color, hex_color)

    def _on_fase_clicked(self, fase: int):
        """Handle fase step click."""
        # Update checklist to show documents for clicked fase
        self._update_checklist_for_fase(fase)

    def _update_checklist_for_fase(self, fase: int):
        """Update document checklist for given fase."""
        from ....config.workflow_config import get_nama_fase

        nama_fase = get_nama_fase(self.MEKANISME, fase)

        # Get document checklist with actual status from dokumen_generator
        dokumen_data = []
        try:
            from ....services.dokumen_generator import get_dokumen_generator

            generator = get_dokumen_generator()
            checklist = generator.get_document_checklist(self._transaksi_data, fase)

            for dok in checklist:
                # Map is_uploaded to status
                if dok.get('is_uploaded', False):
                    status = 'final'
                else:
                    status = 'pending'

                dokumen_data.append({
                    'kode': dok.get('kode', ''),
                    'nama': dok.get('nama', ''),
                    'kategori': dok.get('kategori', 'wajib'),
                    'status': status,
                    'deskripsi': dok.get('deskripsi'),
                    'template': dok.get('template'),
                })
        except Exception as e:
            print(f"Error getting document checklist: {e}")
            # Fallback to workflow config without status
            from ....config.workflow_config import get_dokumen_list
            dokumen_list = get_dokumen_list(self.MEKANISME, fase)
            for dok in dokumen_list:
                dokumen_data.append({
                    'kode': dok.get('kode', ''),
                    'nama': dok.get('nama', ''),
                    'kategori': dok.get('kategori', 'wajib'),
                    'status': 'pending',
                    'deskripsi': dok.get('deskripsi'),
                    'template': dok.get('template'),
                })

        self.checklist.fase = fase
        self.checklist.nama_fase = nama_fase
        self.checklist.set_dokumen(dokumen_data)

        # Update fase info label
        self.fase_info_label.setText(f"Fase {fase}: {nama_fase}")

    def _on_save(self):
        """Handle save button click."""
        data = self._collect_form_data()
        self.save_clicked.emit(data)

    def _on_next_fase(self):
        """Handle next fase button click."""
        # Validate current fase before proceeding
        if self._validate_current_fase():
            self.next_fase_clicked.emit()
        else:
            QMessageBox.warning(
                self,
                "Tidak Dapat Lanjut",
                "Lengkapi semua dokumen wajib sebelum melanjutkan ke fase berikutnya."
            )

    def _on_prepare_dokumen(self):
        """Handle prepare documents button click."""
        # Emit prepare action
        fase = self._transaksi_data.get('fase_aktif', 1)
        self.dokumen_action.emit("PREPARE", "prepare", fase)

    def _validate_current_fase(self) -> bool:
        """Validate current fase is complete."""
        progress = self.checklist.get_progress()
        return progress.get('wajib_selesai', 0) >= progress.get('wajib_total', 0)

    def _collect_form_data(self) -> Dict[str, Any]:
        """Collect form data for saving."""
        return {
            'id': self._transaksi_id,
            'uang_muka': self.kalkulasi_widget.get_values().get('uang_muka', 0),
            'realisasi': self.kalkulasi_widget.get_values().get('realisasi', 0),
        }

    def set_transaksi(self, transaksi_id: int, data: Dict[str, Any]):
        """Load transaksi data into page."""
        self._transaksi_id = transaksi_id
        self._transaksi_data = data

        # Update header info
        self.kode_value.setText(data.get('kode_transaksi', '-'))
        self.nama_value.setText(data.get('nama_kegiatan', '-'))
        self.nilai_value.setText(format_rupiah(data.get('estimasi_biaya', 0)))

        # Update status badge
        status = data.get('status', 'draft')
        status_colors = {
            'draft': '#bdc3c7',
            'aktif': '#3498db',
            'selesai': '#27ae60',
            'batal': '#e74c3c',
        }
        self.status_badge.setText(status.title())
        self.status_badge.setStyleSheet(f"""
            background-color: {status_colors.get(status, '#bdc3c7')};
            color: white;
            border-radius: 10px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: bold;
        """)

        # Update penerima info
        self.penerima_nama_label.setText(f"Nama: {data.get('penerima_nama', '-')}")
        self.penerima_nip_label.setText(f"NIP: {data.get('penerima_nip', '-')}")

        # Update dasar hukum
        self.dasar_nomor_label.setText(f"Nomor: {data.get('nomor_dasar', '-')}")
        self.dasar_tanggal_label.setText(f"Tanggal: {data.get('tanggal_dasar', '-')}")

        # Update fase stepper
        fase_aktif = data.get('fase_aktif', 1)
        self.fase_stepper.set_fase_aktif(fase_aktif)

        # Update checklist for current fase
        self._update_checklist_for_fase(fase_aktif)

        # Update kalkulasi widget
        self.kalkulasi_widget.set_values(
            uang_muka=data.get('uang_muka', 0) or 0,
            realisasi=data.get('realisasi', 0) or 0
        )

        # Update next button visibility
        if fase_aktif >= 5:
            self.next_btn.setText("Selesaikan Transaksi")
        else:
            self.next_btn.setText("Lanjut ke Fase Berikutnya >")

        # Show/hide prepare button based on jenis_kegiatan
        jenis_kegiatan = data.get('jenis_kegiatan', '')
        special_activities = ['PERJALANAN_DINAS', 'KEPANITIAAN', 'RAPAT', 'JAMUAN_TAMU', 'OPERASIONAL']
        self.prepare_btn.setVisible(jenis_kegiatan in special_activities)

        # Update document status checklist
        self._update_document_status()

    def _update_document_status(self):
        """Update document completion status display."""
        try:
            from ...services.dokumen_generator import get_dokumen_generator

            generator = get_dokumen_generator()
            status = generator.get_completion_status(self._transaksi_data)
            missing_docs = generator.get_missing_documents(self._transaksi_data)

            # Update progress bar width
            percentage = status.get('percentage', 0)
            # Set minimum width to show some color
            bar_width = max(int(percentage), 5) if status.get('uploaded', 0) > 0 else 0
            self.doc_progress_bar.setFixedWidth(int(self.doc_progress_frame.width() * bar_width / 100))

            # Update progress label
            uploaded = status.get('uploaded', 0)
            total = status.get('total', 0)
            self.doc_progress_label.setText(f"{uploaded} / {total} dokumen ({percentage:.0f}%)")

            # Update progress bar color based on completion
            if status.get('is_complete', False):
                self.doc_progress_bar.setStyleSheet("background-color: #27ae60; border-radius: 4px;")
            elif percentage >= 50:
                self.doc_progress_bar.setStyleSheet("background-color: #f39c12; border-radius: 4px;")
            else:
                self.doc_progress_bar.setStyleSheet("background-color: #3498db; border-radius: 4px;")

            # Update warning
            missing_count = status.get('missing', 0)
            if missing_count > 0:
                self.doc_warning_label.setText(f"Peringatan: {missing_count} dokumen wajib belum diupload!")
                self.doc_warning_label.setVisible(True)

                # Show missing document names
                missing_names = [doc['nama'] for doc in missing_docs[:5]]  # Show max 5
                if len(missing_docs) > 5:
                    missing_names.append(f"... dan {len(missing_docs) - 5} lainnya")
                self.missing_docs_label.setText("Dokumen: " + ", ".join(missing_names))
                self.missing_docs_label.setVisible(True)
            else:
                self.doc_warning_label.setVisible(False)
                self.missing_docs_label.setVisible(False)

            # Update document list display
            self._update_docs_list()

        except Exception as e:
            print(f"Error updating document status: {e}")
            self.doc_progress_label.setText("Tidak dapat memuat status")

    def _update_docs_list(self):
        """Update the list of documents per fase with status."""
        try:
            # Clear existing items
            while self.docs_per_fase_layout.count():
                child = self.docs_per_fase_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Get document checklist from generator
            from ....services.dokumen_generator import get_dokumen_generator
            from ....config.workflow_config import get_workflow

            generator = get_dokumen_generator()
            workflow = get_workflow(self.MEKANISME)

            if not workflow:
                empty_label = QLabel("Tidak ada konfigurasi workflow")
                empty_label.setStyleSheet("font-size: 11px; color: #95a5a6; font-style: italic; background-color: transparent;")
                self.docs_per_fase_layout.addWidget(empty_label)
                return

            # Get checklist for all phases
            all_checklist = generator.get_document_checklist(self._transaksi_data, fase=None)

            # Group by fase
            docs_by_fase = {}
            for dok in all_checklist:
                fase = dok.get('fase', 1)
                if fase not in docs_by_fase:
                    docs_by_fase[fase] = []
                docs_by_fase[fase].append(dok)

            # Display each fase
            for fase_num in sorted(docs_by_fase.keys()):
                fase_config = workflow.get('fase', {}).get(fase_num, {})
                fase_nama = fase_config.get('nama', f'Fase {fase_num}')
                docs = docs_by_fase[fase_num]

                # Fase header
                fase_header = QLabel(f"Fase {fase_num}: {fase_nama}")
                fase_header.setStyleSheet("""
                    font-size: 11px;
                    font-weight: bold;
                    color: #7f8c8d;
                    padding: 5px 0 3px 0;
                    border-bottom: 1px solid #ecf0f1;
                    background-color: transparent;
                """)
                self.docs_per_fase_layout.addWidget(fase_header)

                # Documents in this fase
                for dok in docs:
                    doc_widget = self._create_doc_status_item(dok)
                    self.docs_per_fase_layout.addWidget(doc_widget)

            self.docs_per_fase_layout.addStretch()

        except Exception as e:
            print(f"Error updating docs list: {e}")
            error_label = QLabel("Gagal memuat daftar dokumen")
            error_label.setStyleSheet("font-size: 11px; color: #e74c3c; background-color: transparent;")
            self.docs_per_fase_layout.addWidget(error_label)

    def _create_doc_status_item(self, dok_info: Dict[str, Any]) -> QFrame:
        """Create a document status item with open button."""
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #ecf0f1;
                border-radius: 4px;
                margin: 2px 0;
            }
        """)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # Status icon
        is_uploaded = dok_info.get('is_uploaded', False)
        file_path = dok_info.get('file_path')

        if is_uploaded and file_path:
            icon_label = QLabel("✅")
            icon_label.setStyleSheet("font-size: 14px; background-color: transparent;")
            icon_label.setToolTip("Sudah diarsipkan")
        else:
            icon_label = QLabel("⬜")
            icon_label.setStyleSheet("font-size: 14px; color: #bdc3c7; background-color: transparent;")
            icon_label.setToolTip("Belum dibuat")
        layout.addWidget(icon_label)

        # Document info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        nama_label = QLabel(dok_info.get('nama', 'Dokumen'))
        nama_label.setStyleSheet("font-size: 11px; font-weight: 500; color: #2c3e50; background-color: transparent;")
        info_layout.addWidget(nama_label)

        if is_uploaded and file_path:
            import os
            from datetime import datetime
            file_name = os.path.basename(file_path)
            # Try to get file modification time
            try:
                mtime = os.path.getmtime(file_path)
                time_str = datetime.fromtimestamp(mtime).strftime("%d %b %Y, %H:%M")
                detail_text = f"{file_name} • {time_str}"
            except:
                detail_text = file_name

            detail_label = QLabel(detail_text)
            detail_label.setStyleSheet("font-size: 10px; color: #27ae60; background-color: transparent;")
            info_layout.addWidget(detail_label)
        else:
            kategori = dok_info.get('kategori', 'wajib')
            if kategori == 'wajib':
                status_text = "Belum dibuat (Wajib)"
                status_color = "#e74c3c"
            else:
                status_text = "Belum dibuat (Opsional)"
                status_color = "#95a5a6"

            status_label = QLabel(status_text)
            status_label.setStyleSheet(f"font-size: 10px; color: {status_color}; background-color: transparent;")
            info_layout.addWidget(status_label)

        layout.addLayout(info_layout, 1)

        # Action buttons (if file exists)
        if is_uploaded and file_path:
            btn_buka = QPushButton("Buka")
            btn_buka.setFixedHeight(24)
            btn_buka.setCursor(Qt.PointingHandCursor)
            btn_buka.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 3px 10px;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn_buka.clicked.connect(lambda checked, fp=file_path: self._open_file(fp))
            layout.addWidget(btn_buka)

        return item

    def _create_doc_item(self, file_path) -> QFrame:
        """Create a clickable document item widget."""
        from pathlib import Path

        item = QFrame()
        item.setObjectName("docItem")
        item.setStyleSheet("""
            #docItem {
                background-color: #ffffff;
                border: 1px solid #ecf0f1;
                border-radius: 4px;
                padding: 5px;
            }
            #docItem:hover {
                background-color: #f0f8ff;
                border-color: #3498db;
            }
        """)
        item.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(8)

        # Icon based on file type
        suffix = file_path.suffix.lower()
        if suffix == '.docx':
            icon = "📝"
            color = "#2980b9"
            file_type = "Word"
        elif suffix == '.pdf':
            icon = "📕"
            color = "#c0392b"
            file_type = "PDF"
        else:
            icon = "🖼️"
            color = "#27ae60"
            file_type = "Gambar"

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 14px; background-color: transparent;")
        layout.addWidget(icon_label)

        # File name
        name = file_path.stem
        if len(name) > 25:
            name = name[:22] + "..."
        name_label = QLabel(name)
        name_label.setStyleSheet(f"font-size: 11px; color: #2c3e50; background-color: transparent;")
        name_label.setToolTip(str(file_path))
        layout.addWidget(name_label, 1)

        # File type badge
        type_label = QLabel(file_type)
        type_label.setStyleSheet(f"font-size: 9px; color: {color}; font-weight: bold; background-color: transparent;")
        layout.addWidget(type_label)

        # Open button
        open_btn = QPushButton("Buka")
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.clicked.connect(lambda checked, fp=str(file_path): self._open_file(fp))
        layout.addWidget(open_btn)

        return item

    def _open_file(self, file_path: str):
        """Open file with default application."""
        import subprocess
        import platform
        import os

        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Gagal membuka file:\n{str(e)}")

    def set_dokumen_list(self, dokumen_list: List[Dict[str, Any]]):
        """Set document list for current fase."""
        self.checklist.set_dokumen(dokumen_list)

    def set_log_entries(self, entries: List[Dict[str, Any]]):
        """Set log/history entries."""
        # Clear existing
        while self.log_container.count():
            child = self.log_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not entries:
            empty = QLabel("Belum ada riwayat")
            empty.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 20px;")
            empty.setAlignment(Qt.AlignCenter)
            self.log_container.addWidget(empty)
            return

        for entry in entries:
            item = QFrame()
            item.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    padding: 8px;
                }
            """)

            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(10, 8, 10, 8)

            # Action text
            aksi = entry.get('aksi', '')
            fase_dari = entry.get('fase_dari')
            fase_ke = entry.get('fase_ke')

            if aksi == "NEXT":
                text = f"Fase {fase_dari} -> Fase {fase_ke}"
            elif aksi == "CREATE":
                text = "Transaksi dibuat"
            else:
                text = entry.get('catatan', aksi)

            aksi_label = QLabel(text)
            aksi_label.setStyleSheet("font-size: 12px; color: #2c3e50;")
            item_layout.addWidget(aksi_label)

            item_layout.addStretch()

            # Timestamp
            timestamp = entry.get('created_at', '')
            time_label = QLabel(timestamp[:16] if timestamp else '-')
            time_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
            item_layout.addWidget(time_label)

            self.log_container.addWidget(item)

    def refresh(self):
        """Refresh the page - update checklist and document status."""
        if self._transaksi_id and self._transaksi_data:
            # Get current fase
            fase_aktif = self._transaksi_data.get('fase_aktif', 1)

            # Refresh checklist for current fase
            self._update_checklist_for_fase(fase_aktif)

            # Update document status display
            self._update_document_status()
