"""
PPK DOCUMENT FACTORY - Transaksi Form Page
===========================================
Form page for creating/editing pencairan transactions.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QDoubleSpinBox, QDateEdit, QFrame, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QDate

from typing import Dict, Any, Optional

from ....models.pencairan_models import JENIS_BELANJA, BATAS_UP_MAKSIMAL
from ....core.database import get_db_manager


def format_rupiah(value: float) -> str:
    """Format angka ke format Rupiah."""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


class TransaksiFormPage(QWidget):
    """
    Form for creating/editing transaksi pencairan.

    Signals:
        saved(dict): Emitted when form is saved
        cancelled(): Emitted when form is cancelled
    """

    saved = Signal(dict)
    cancelled = Signal()

    MEKANISME_COLORS = {
        "UP": "#27ae60",
        "TUP": "#f39c12",
        "LS": "#3498db",
    }

    def __init__(self, mekanisme: str = "UP", parent=None):
        super().__init__(parent)
        self.mekanisme = mekanisme.upper()
        self._transaksi_id: Optional[int] = None
        self._is_edit = False
        self._jenis_dasar_ls = "KONTRAK"  # Default mode for LS: KONTRAK or SURAT_TUGAS

        self._setup_ui()

    def _setup_ui(self):
        """Setup form UI."""
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Form sections
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(20)

        # Basic info section
        basic_section = self._create_basic_section()
        form_layout.addWidget(basic_section)

        # Financial section
        if self.mekanisme in ["UP", "TUP"]:
            financial_section = self._create_financial_section_up()
        else:
            financial_section = self._create_financial_section_ls()
        form_layout.addWidget(financial_section)

        # Penerima section (for UP/TUP)
        if self.mekanisme in ["UP", "TUP"]:
            penerima_section = self._create_penerima_section()
            form_layout.addWidget(penerima_section)

            # Perjalanan Dinas section (hidden by default, shown when jenis = perdin)
            self.perdin_section_widget = self._create_perjalanan_dinas_section()
            self.perdin_section_widget.setVisible(False)  # Hidden by default
            form_layout.addWidget(self.perdin_section_widget)

        # Penyedia section (for LS KONTRAK mode only)
        if self.mekanisme == "LS":
            self.penyedia_section_widget = self._create_penyedia_section()
            form_layout.addWidget(self.penyedia_section_widget)

        # Dasar hukum section
        dasar_section = self._create_dasar_section()
        form_layout.addWidget(dasar_section)

        main_layout.addWidget(form_frame)

        # Action buttons
        actions = self._create_actions()
        main_layout.addWidget(actions)

        main_layout.addStretch()

        scroll.setWidget(content)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def _create_header(self) -> QWidget:
        """Create form header."""
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
            }
        """)
        back_btn.clicked.connect(self.cancelled.emit)
        layout.addWidget(back_btn)

        layout.addStretch()

        # Title
        title_text = "Edit Transaksi" if self._is_edit else f"Buat {self.mekanisme} Baru"
        title = QLabel(title_text)
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
        """)
        layout.addWidget(title)

        layout.addStretch()

        # Mekanisme badge
        color = self.MEKANISME_COLORS.get(self.mekanisme, "#3498db")
        badge = QLabel(self.mekanisme)
        badge.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: 12px;
            padding: 4px 12px;
            font-weight: bold;
        """)
        layout.addWidget(badge)

        return header

    def _create_section_title(self, title: str) -> QLabel:
        """Create section title label."""
        label = QLabel(title)
        label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            padding-bottom: 10px;
            border-bottom: 1px solid #ecf0f1;
            margin-bottom: 10px;
        """)
        return label

    def _create_basic_section(self) -> QWidget:
        """Create basic info section with 2-column layout."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._create_section_title("Informasi Dasar"))

        # Grid layout for compact display
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Row 0: Nama Kegiatan (full width)
        grid.addWidget(QLabel("Nama Kegiatan *"), 0, 0)
        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText("Contoh: Rapat Koordinasi Tim Teknis")
        self.nama_input.setStyleSheet(self._get_input_style())
        grid.addWidget(self.nama_input, 0, 1, 1, 3)  # Span 3 columns

        # Row 1: Jenis Belanja & Kode Akun (side by side)
        grid.addWidget(QLabel("Jenis Belanja *"), 1, 0)
        self.jenis_combo = QComboBox()
        for jenis in JENIS_BELANJA:
            self.jenis_combo.addItem(jenis['nama'], jenis['kode'])
        self.jenis_combo.setStyleSheet(self._get_input_style())
        grid.addWidget(self.jenis_combo, 1, 1)

        grid.addWidget(QLabel("Kode Akun"), 1, 2)
        self.akun_input = QComboBox()
        self.akun_input.setEditable(True)
        self.akun_input.setStyleSheet(self._get_input_style())
        self.akun_input.lineEdit().setPlaceholderText("Pilih kode akun...")
        self._load_dipa_kode_akun()
        grid.addWidget(self.akun_input, 1, 3)

        # Auto-fill kode akun when jenis changes
        self.jenis_combo.currentIndexChanged.connect(self._on_jenis_changed)

        layout.addLayout(grid)

        return section

    def _create_financial_section_up(self) -> QWidget:
        """Create financial section for UP/TUP with DIPA budget selection."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._create_section_title("Ketersediaan Anggaran DIPA"))

        # Grid layout for compact display
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Row 0: RO (Output) & Akun dropdowns
        grid.addWidget(QLabel("Output (RO)"), 0, 0)
        self.dipa_ro_combo = QComboBox()
        self.dipa_ro_combo.setStyleSheet(self._get_input_style())
        self.dipa_ro_combo.currentIndexChanged.connect(self._on_dipa_ro_changed)
        grid.addWidget(self.dipa_ro_combo, 0, 1)

        grid.addWidget(QLabel("Akun"), 0, 2)
        self.dipa_akun_combo = QComboBox()
        self.dipa_akun_combo.setStyleSheet(self._get_input_style())
        self.dipa_akun_combo.currentIndexChanged.connect(self._on_dipa_akun_changed)
        grid.addWidget(self.dipa_akun_combo, 0, 3)

        # Row 1: Detail Item & Ketersediaan
        grid.addWidget(QLabel("Detail Item"), 1, 0)
        self.dipa_detail_combo = QComboBox()
        self.dipa_detail_combo.setStyleSheet(self._get_input_style())
        self.dipa_detail_combo.currentIndexChanged.connect(self._on_dipa_detail_changed)
        grid.addWidget(self.dipa_detail_combo, 1, 1)

        # Ketersediaan (read-only display)
        grid.addWidget(QLabel("Ketersediaan"), 1, 2)
        self.ketersediaan_label = QLabel("Rp 0")
        self.ketersediaan_label.setStyleSheet("""
            font-weight: bold;
            color: #27ae60;
            padding: 8px;
            background-color: #e8f8f5;
            border-radius: 4px;
        """)
        grid.addWidget(self.ketersediaan_label, 1, 3)

        # Row 2: Estimasi Biaya & Tanggal
        grid.addWidget(QLabel("Estimasi Biaya *"), 2, 0)
        estimasi_layout = QHBoxLayout()
        self.estimasi_input = QDoubleSpinBox()
        self.estimasi_input.setRange(0, BATAS_UP_MAKSIMAL)
        self.estimasi_input.setDecimals(0)
        self.estimasi_input.setPrefix("Rp ")
        self.estimasi_input.setGroupSeparatorShown(True)
        self.estimasi_input.setStyleSheet(self._get_input_style())
        estimasi_layout.addWidget(self.estimasi_input)

        if self.mekanisme == "UP":
            warning = QLabel(f"(Maks UP: {format_rupiah(BATAS_UP_MAKSIMAL)})")
            warning.setStyleSheet("font-size: 10px; color: #f39c12;")
            estimasi_layout.addWidget(warning)

        grid.addLayout(estimasi_layout, 2, 1)

        # Tanggal compact
        tgl_layout = QHBoxLayout()
        tgl_layout.addWidget(QLabel("Tgl:"))
        self.tgl_mulai_input = QDateEdit()
        self.tgl_mulai_input.setCalendarPopup(True)
        self.tgl_mulai_input.setDate(QDate.currentDate())
        self.tgl_mulai_input.setStyleSheet(self._get_input_style())
        self.tgl_mulai_input.dateChanged.connect(self._on_tanggal_changed)
        tgl_layout.addWidget(self.tgl_mulai_input)

        tgl_layout.addWidget(QLabel("s/d"))
        self.tgl_selesai_input = QDateEdit()
        self.tgl_selesai_input.setCalendarPopup(True)
        self.tgl_selesai_input.setDate(QDate.currentDate())
        self.tgl_selesai_input.setStyleSheet(self._get_input_style())
        self.tgl_selesai_input.dateChanged.connect(self._on_tanggal_changed)
        tgl_layout.addWidget(self.tgl_selesai_input)

        grid.addLayout(tgl_layout, 2, 2, 1, 2)

        layout.addLayout(grid)

        # Load DIPA data into dropdowns
        self._load_dipa_hierarchy()

        return section

    def _load_dipa_hierarchy(self):
        """Load DIPA data into hierarchical dropdowns."""
        try:
            db = get_db_manager()

            # Get unique RO (Output) codes
            all_dipa = db.get_all_dipa()

            # Group by kode_output (RO)
            ro_dict = {}
            for item in all_dipa:
                ro = item.get('kode_output', '') or 'Tanpa RO'
                if ro not in ro_dict:
                    ro_dict[ro] = {'total': 0, 'items': []}
                ro_dict[ro]['total'] += item.get('total', 0) or 0
                ro_dict[ro]['items'].append(item)

            self.dipa_ro_combo.clear()
            self.dipa_ro_combo.addItem("-- Pilih Output (RO) --", None)

            for ro, data in sorted(ro_dict.items()):
                total_text = format_rupiah(data['total'])
                self.dipa_ro_combo.addItem(f"{ro} ({total_text})", ro)

            # Store for filtering
            self._dipa_data = all_dipa
            self._dipa_by_ro = ro_dict

        except Exception as e:
            print(f"Error loading DIPA: {e}")
            self._dipa_data = []
            self._dipa_by_ro = {}

    def _on_dipa_ro_changed(self, index: int):
        """Handle RO selection change - filter akun dropdown."""
        self.dipa_akun_combo.clear()
        self.dipa_detail_combo.clear()
        self.ketersediaan_label.setText("Rp 0")

        ro = self.dipa_ro_combo.currentData()
        if not ro:
            self.dipa_akun_combo.addItem("-- Pilih Akun --", None)
            return

        # Get items for this RO and group by akun
        ro_items = self._dipa_by_ro.get(ro, {}).get('items', [])
        akun_dict = {}
        for item in ro_items:
            akun = item.get('kode_akun', '')
            if akun not in akun_dict:
                akun_dict[akun] = {'total': 0, 'items': []}
            akun_dict[akun]['total'] += item.get('total', 0) or 0
            akun_dict[akun]['items'].append(item)

        self.dipa_akun_combo.addItem("-- Pilih Akun --", None)
        for akun, data in sorted(akun_dict.items()):
            total_text = format_rupiah(data['total'])
            self.dipa_akun_combo.addItem(f"{akun} ({total_text})", akun)

        self._dipa_by_akun = akun_dict

    def _on_dipa_akun_changed(self, index: int):
        """Handle Akun selection change - filter detail dropdown."""
        self.dipa_detail_combo.clear()
        self.ketersediaan_label.setText("Rp 0")

        akun = self.dipa_akun_combo.currentData()
        if not akun or not hasattr(self, '_dipa_by_akun'):
            self.dipa_detail_combo.addItem("-- Pilih Detail --", None)
            return

        # Get items for this akun
        akun_items = self._dipa_by_akun.get(akun, {}).get('items', [])

        self.dipa_detail_combo.addItem("-- Pilih Detail --", None)
        for item in akun_items:
            uraian = item.get('uraian_item', '')[:50]  # Truncate long text
            total = item.get('total', 0) or 0
            total_text = format_rupiah(total)
            display = f"{uraian}... ({total_text})" if len(item.get('uraian_item', '')) > 50 else f"{uraian} ({total_text})"
            self.dipa_detail_combo.addItem(display, item)

        # Also update kode akun combo in basic section
        if hasattr(self, 'akun_input'):
            for i in range(self.akun_input.count()):
                if self.akun_input.itemData(i) == akun:
                    self.akun_input.setCurrentIndex(i)
                    break

    def _on_dipa_detail_changed(self, index: int):
        """Handle Detail selection change - show ketersediaan."""
        item = self.dipa_detail_combo.currentData()
        if not item or not isinstance(item, dict):
            self.ketersediaan_label.setText("Rp 0")
            self.ketersediaan_label.setStyleSheet("""
                font-weight: bold; color: #7f8c8d; padding: 8px;
                background-color: #ecf0f1; border-radius: 4px;
            """)
            return

        total = item.get('total', 0) or 0
        realisasi = item.get('realisasi', 0) or 0
        ketersediaan = total - realisasi

        self.ketersediaan_label.setText(format_rupiah(ketersediaan))

        # Color based on availability
        if ketersediaan > 0:
            self.ketersediaan_label.setStyleSheet("""
                font-weight: bold; color: #27ae60; padding: 8px;
                background-color: #e8f8f5; border-radius: 4px;
            """)
        else:
            self.ketersediaan_label.setStyleSheet("""
                font-weight: bold; color: #e74c3c; padding: 8px;
                background-color: #fdedec; border-radius: 4px;
            """)

    def _create_financial_section_ls(self) -> QWidget:
        """Create financial section for LS with mode selection (KONTRAK vs SURAT_TUGAS)."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        layout.addWidget(self._create_section_title("Jenis Dasar Hukum LS"))

        # Mode selector (KONTRAK vs SURAT_TUGAS)
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(15)

        from PySide6.QtWidgets import QRadioButton, QButtonGroup

        self.ls_mode_group = QButtonGroup(self)

        self.rb_kontrak = QRadioButton("Kontrak/SPK (Pengadaan)")
        self.rb_kontrak.setChecked(True)
        self.rb_kontrak.setStyleSheet("""
            QRadioButton {
                font-size: 13px;
                padding: 8px 15px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        self.ls_mode_group.addButton(self.rb_kontrak, 1)
        mode_layout.addWidget(self.rb_kontrak)

        self.rb_surat_tugas = QRadioButton("Surat Tugas (Perjalanan Dinas)")
        self.rb_surat_tugas.setStyleSheet("""
            QRadioButton {
                font-size: 13px;
                padding: 8px 15px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        self.ls_mode_group.addButton(self.rb_surat_tugas, 2)
        mode_layout.addWidget(self.rb_surat_tugas)

        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Container for mode-specific fields
        self.ls_fields_container = QWidget()
        ls_fields_layout = QVBoxLayout(self.ls_fields_container)
        ls_fields_layout.setContentsMargins(0, 10, 0, 0)
        ls_fields_layout.setSpacing(0)

        # === KONTRAK FIELDS ===
        self.kontrak_section = QWidget()
        kontrak_layout = QVBoxLayout(self.kontrak_section)
        kontrak_layout.setContentsMargins(0, 0, 0, 0)
        kontrak_layout.setSpacing(10)

        kontrak_form = QFormLayout()
        kontrak_form.setSpacing(10)
        kontrak_form.setLabelAlignment(Qt.AlignRight)

        # Nomor Kontrak
        self.kontrak_nomor_input = QLineEdit()
        self.kontrak_nomor_input.setPlaceholderText("Contoh: 001/SPK/2026")
        self.kontrak_nomor_input.setStyleSheet(self._get_input_style())
        kontrak_form.addRow("Nomor Kontrak/SPK *", self.kontrak_nomor_input)

        # Tanggal Kontrak
        self.kontrak_tgl_input = QDateEdit()
        self.kontrak_tgl_input.setCalendarPopup(True)
        self.kontrak_tgl_input.setDate(QDate.currentDate())
        self.kontrak_tgl_input.setStyleSheet(self._get_input_style())
        kontrak_form.addRow("Tanggal Kontrak *", self.kontrak_tgl_input)

        # Nilai Kontrak
        self.nilai_kontrak_input = QDoubleSpinBox()
        self.nilai_kontrak_input.setRange(0, 999999999999)
        self.nilai_kontrak_input.setDecimals(0)
        self.nilai_kontrak_input.setPrefix("Rp ")
        self.nilai_kontrak_input.setGroupSeparatorShown(True)
        self.nilai_kontrak_input.setStyleSheet(self._get_input_style())
        kontrak_form.addRow("Nilai Kontrak *", self.nilai_kontrak_input)

        kontrak_layout.addLayout(kontrak_form)
        ls_fields_layout.addWidget(self.kontrak_section)

        # === SURAT TUGAS FIELDS ===
        self.surat_tugas_section = QWidget()
        st_layout = QVBoxLayout(self.surat_tugas_section)
        st_layout.setContentsMargins(0, 0, 0, 0)
        st_layout.setSpacing(10)

        st_form = QFormLayout()
        st_form.setSpacing(10)
        st_form.setLabelAlignment(Qt.AlignRight)

        # Nomor Surat Tugas
        self.st_nomor_input = QLineEdit()
        self.st_nomor_input.setPlaceholderText("Contoh: 001/ST/2026")
        self.st_nomor_input.setStyleSheet(self._get_input_style())
        st_form.addRow("Nomor Surat Tugas *", self.st_nomor_input)

        # Tanggal Surat Tugas
        self.st_tgl_input = QDateEdit()
        self.st_tgl_input.setCalendarPopup(True)
        self.st_tgl_input.setDate(QDate.currentDate())
        self.st_tgl_input.setStyleSheet(self._get_input_style())
        st_form.addRow("Tanggal Surat Tugas *", self.st_tgl_input)

        # Tujuan Perjalanan
        self.st_tujuan_input = QLineEdit()
        self.st_tujuan_input.setPlaceholderText("Contoh: Jakarta - Rapat Koordinasi di Kemenkeu")
        self.st_tujuan_input.setStyleSheet(self._get_input_style())
        st_form.addRow("Tujuan Perjalanan *", self.st_tujuan_input)

        # Tanggal Perjalanan
        date_pjd_layout = QHBoxLayout()

        self.st_tgl_berangkat = QDateEdit()
        self.st_tgl_berangkat.setCalendarPopup(True)
        self.st_tgl_berangkat.setDate(QDate.currentDate())
        self.st_tgl_berangkat.setStyleSheet(self._get_input_style())
        date_pjd_layout.addWidget(QLabel("Berangkat:"))
        date_pjd_layout.addWidget(self.st_tgl_berangkat)

        self.st_tgl_kembali = QDateEdit()
        self.st_tgl_kembali.setCalendarPopup(True)
        self.st_tgl_kembali.setDate(QDate.currentDate())
        self.st_tgl_kembali.setStyleSheet(self._get_input_style())
        date_pjd_layout.addWidget(QLabel("Kembali:"))
        date_pjd_layout.addWidget(self.st_tgl_kembali)

        st_form.addRow("Tanggal Perjalanan *", date_pjd_layout)

        # Estimasi Biaya Perjalanan
        self.st_biaya_input = QDoubleSpinBox()
        self.st_biaya_input.setRange(0, 999999999999)
        self.st_biaya_input.setDecimals(0)
        self.st_biaya_input.setPrefix("Rp ")
        self.st_biaya_input.setGroupSeparatorShown(True)
        self.st_biaya_input.setStyleSheet(self._get_input_style())
        st_form.addRow("Estimasi Biaya *", self.st_biaya_input)

        st_layout.addLayout(st_form)
        ls_fields_layout.addWidget(self.surat_tugas_section)

        # Initially hide surat tugas section
        self.surat_tugas_section.hide()

        layout.addWidget(self.ls_fields_container)

        # Connect mode change
        self.ls_mode_group.buttonClicked.connect(self._on_ls_mode_changed)

        return section

    def _on_ls_mode_changed(self, button):
        """Handle LS mode change (KONTRAK vs SURAT_TUGAS)."""
        if button == self.rb_kontrak:
            self._jenis_dasar_ls = "KONTRAK"
            self.kontrak_section.show()
            self.surat_tugas_section.hide()
            # Show penyedia section for kontrak mode
            if hasattr(self, 'penyedia_section_widget'):
                self.penyedia_section_widget.show()
        else:
            self._jenis_dasar_ls = "SURAT_TUGAS"
            self.kontrak_section.hide()
            self.surat_tugas_section.show()
            # Hide penyedia section for surat tugas mode
            if hasattr(self, 'penyedia_section_widget'):
                self.penyedia_section_widget.hide()

    def _create_penerima_section(self) -> QWidget:
        """Create penerima (recipient) section for UP/TUP with compact layout."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._create_section_title("Penerima / Pelaksana"))

        # Grid layout for compact display
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Row 0: Nama (full width)
        grid.addWidget(QLabel("Nama *"), 0, 0)
        self.penerima_nama_input = QLineEdit()
        self.penerima_nama_input.setPlaceholderText("Nama lengkap dengan gelar")
        self.penerima_nama_input.setStyleSheet(self._get_input_style())
        grid.addWidget(self.penerima_nama_input, 0, 1, 1, 3)

        # Row 1: NIP & Jabatan (side by side)
        grid.addWidget(QLabel("NIP"), 1, 0)
        self.penerima_nip_input = QLineEdit()
        self.penerima_nip_input.setPlaceholderText("NIP 18 digit")
        self.penerima_nip_input.setStyleSheet(self._get_input_style())
        grid.addWidget(self.penerima_nip_input, 1, 1)

        grid.addWidget(QLabel("Jabatan"), 1, 2)
        self.penerima_jabatan_input = QLineEdit()
        self.penerima_jabatan_input.setPlaceholderText("Jabatan penerima")
        self.penerima_jabatan_input.setStyleSheet(self._get_input_style())
        grid.addWidget(self.penerima_jabatan_input, 1, 3)

        layout.addLayout(grid)

        return section

    def _create_perjalanan_dinas_section(self) -> QWidget:
        """Create Perjalanan Dinas specific fields section with compact layout."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._create_section_title("Detail Perjalanan Dinas"))

        # Grid layout for compact display
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Row 0: Tujuan & Maksud (side by side)
        grid.addWidget(QLabel("Tujuan *"), 0, 0)
        self.perdin_tujuan_input = QLineEdit()
        self.perdin_tujuan_input.setPlaceholderText("Kota/lokasi tujuan")
        self.perdin_tujuan_input.setStyleSheet(self._get_input_style())
        grid.addWidget(self.perdin_tujuan_input, 0, 1)

        grid.addWidget(QLabel("Maksud"), 0, 2)
        self.perdin_maksud_input = QLineEdit()
        self.perdin_maksud_input.setPlaceholderText("Tujuan perjalanan")
        self.perdin_maksud_input.setStyleSheet(self._get_input_style())
        grid.addWidget(self.perdin_maksud_input, 0, 3)

        # Row 1: Alat Angkut, Tingkat, Lama Hari (side by side)
        grid.addWidget(QLabel("Alat Angkut"), 1, 0)
        self.perdin_alat_angkut_combo = QComboBox()
        self.perdin_alat_angkut_combo.addItems([
            "Pesawat Udara", "Kereta Api", "Kapal Laut/Ferry",
            "Mobil Dinas", "Kendaraan Umum", "Lainnya"
        ])
        self.perdin_alat_angkut_combo.setStyleSheet(self._get_input_style())
        grid.addWidget(self.perdin_alat_angkut_combo, 1, 1)

        # Tingkat & Lama in same column
        tingkat_lama_layout = QHBoxLayout()

        tingkat_lama_layout.addWidget(QLabel("Tingkat:"))
        self.perdin_tingkat_combo = QComboBox()
        self.perdin_tingkat_combo.addItems(["A", "B", "C", "D"])
        self.perdin_tingkat_combo.setStyleSheet(self._get_input_style())
        self.perdin_tingkat_combo.setFixedWidth(60)
        tingkat_lama_layout.addWidget(self.perdin_tingkat_combo)

        tingkat_lama_layout.addSpacing(15)

        tingkat_lama_layout.addWidget(QLabel("Lama:"))
        self.perdin_lama_hari_input = QLineEdit()
        self.perdin_lama_hari_input.setPlaceholderText("Auto")
        self.perdin_lama_hari_input.setReadOnly(True)
        self.perdin_lama_hari_input.setStyleSheet(self._get_input_style() + "QLineEdit{background-color:#f5f6fa;}")
        self.perdin_lama_hari_input.setFixedWidth(50)
        tingkat_lama_layout.addWidget(self.perdin_lama_hari_input)
        tingkat_lama_layout.addWidget(QLabel("hari"))
        tingkat_lama_layout.addStretch()

        grid.addLayout(tingkat_lama_layout, 1, 2, 1, 2)

        layout.addLayout(grid)

        return section

    def _create_penyedia_section(self) -> QWidget:
        """Create penyedia (vendor) section for LS."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        layout.addWidget(self._create_section_title("Penyedia Barang/Jasa"))

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Penyedia dropdown (would be populated from database)
        self.penyedia_combo = QComboBox()
        self.penyedia_combo.addItem("-- Pilih Penyedia --", None)
        self.penyedia_combo.setStyleSheet(self._get_input_style())
        form_layout.addRow("Penyedia *", self.penyedia_combo)

        # Or manual entry
        hint = QLabel("Atau tambah penyedia baru melalui menu Pengadaan > Data Penyedia")
        hint.setStyleSheet("font-size: 11px; color: #7f8c8d; font-style: italic;")
        form_layout.addRow("", hint)

        layout.addLayout(form_layout)

        return section

    def _create_dasar_section(self) -> QWidget:
        """Create dasar hukum section with compact layout."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._create_section_title("Dasar Hukum / SK"))

        # Grid layout for compact display
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Row 0: Jenis, Nomor, Tanggal (side by side)
        grid.addWidget(QLabel("Jenis"), 0, 0)
        self.dasar_jenis_combo = QComboBox()
        self.dasar_jenis_combo.addItems([
            "SK KPA", "Surat Tugas", "Nota Dinas", "Undangan", "Lainnya"
        ])
        self.dasar_jenis_combo.setStyleSheet(self._get_input_style())
        grid.addWidget(self.dasar_jenis_combo, 0, 1)

        grid.addWidget(QLabel("Tanggal"), 0, 2)
        self.dasar_tgl_input = QDateEdit()
        self.dasar_tgl_input.setCalendarPopup(True)
        self.dasar_tgl_input.setDate(QDate.currentDate())
        self.dasar_tgl_input.setStyleSheet(self._get_input_style())
        grid.addWidget(self.dasar_tgl_input, 0, 3)

        # Row 1: Nomor (full width)
        grid.addWidget(QLabel("Nomor"), 1, 0)
        self.dasar_nomor_input = QLineEdit()
        self.dasar_nomor_input.setPlaceholderText("Nomor SK/Surat Tugas")
        self.dasar_nomor_input.setStyleSheet(self._get_input_style())
        grid.addWidget(self.dasar_nomor_input, 1, 1, 1, 3)

        # Row 2: Perihal (full width)
        grid.addWidget(QLabel("Perihal"), 2, 0)
        self.dasar_perihal_input = QTextEdit()
        self.dasar_perihal_input.setPlaceholderText("Perihal/tentang...")
        self.dasar_perihal_input.setMaximumHeight(60)
        self.dasar_perihal_input.setStyleSheet(self._get_input_style())
        grid.addWidget(self.dasar_perihal_input, 2, 1, 1, 3)

        layout.addLayout(grid)

        return section

    def _create_actions(self) -> QWidget:
        """Create action buttons."""
        actions = QWidget()
        layout = QHBoxLayout(actions)
        layout.setContentsMargins(0, 10, 0, 0)

        layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("Batal")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """)
        cancel_btn.clicked.connect(self.cancelled.emit)
        layout.addWidget(cancel_btn)

        # Save button
        save_text = "Simpan Perubahan" if self._is_edit else "Buat Transaksi"
        color = self.MEKANISME_COLORS.get(self.mekanisme, "#3498db")

        save_btn = QPushButton(save_text)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
        """)
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)

        return actions

    def _get_input_style(self) -> str:
        """Get common input field style."""
        return """
            QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit {
                background-color: #ffffff;
                border: 1px solid #dcdfe6;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
                min-width: 250px;
            }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus,
            QDateEdit:focus, QTextEdit:focus {
                border-color: #3498db;
            }
        """

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color."""
        darken_map = {
            "#27ae60": "#1e8449",
            "#f39c12": "#d68910",
            "#3498db": "#2980b9",
        }
        return darken_map.get(hex_color, hex_color)

    def _load_dipa_kode_akun(self):
        """Load kode akun from DIPA data into combobox."""
        try:
            db = get_db_manager()
            dipa_list = db.get_dipa_kode_akun_list()

            self.akun_input.clear()
            self.akun_input.addItem("", "")  # Empty option

            for item in dipa_list:
                kode = item.get('kode_akun', '')
                total = item.get('total_pagu', 0) or 0
                jumlah = item.get('jumlah_item', 0) or 0

                # Format: "521111 - Rp 10.000.000 (5 item)"
                pagu_text = f"Rp {total:,.0f}".replace(',', '.')
                display = f"{kode} - {pagu_text} ({jumlah} item)"

                self.akun_input.addItem(display, kode)
        except Exception:
            # If DIPA data not available, just keep empty combobox
            pass

    def _on_jenis_changed(self, index: int):
        """Handle jenis belanja change to auto-fill kode akun and show/hide perdin section."""
        kode = self.jenis_combo.currentData()

        # Show/hide Perjalanan Dinas section (only for UP/TUP)
        if self.mekanisme in ["UP", "TUP"] and hasattr(self, 'perdin_section_widget'):
            is_perdin = (kode == "perdin")
            self.perdin_section_widget.setVisible(is_perdin)

            # Auto-set dasar hukum type to Surat Tugas for perjalanan dinas
            if is_perdin and hasattr(self, 'dasar_jenis_combo'):
                for i in range(self.dasar_jenis_combo.count()):
                    if self.dasar_jenis_combo.itemText(i) == "Surat Tugas":
                        self.dasar_jenis_combo.setCurrentIndex(i)
                        break

        # Auto-fill kode akun
        for jenis in JENIS_BELANJA:
            if jenis['kode'] == kode:
                akun_default = jenis['akun_default']
                # Find and select matching item in combobox
                for i in range(self.akun_input.count()):
                    if self.akun_input.itemData(i) == akun_default:
                        self.akun_input.setCurrentIndex(i)
                        return
                # If not found in dropdown, set as text
                self.akun_input.setCurrentText(akun_default)
                break

    def _on_tanggal_changed(self):
        """Handle tanggal kegiatan change to calculate lama hari."""
        if not hasattr(self, 'tgl_mulai_input') or not hasattr(self, 'tgl_selesai_input'):
            return
        if not hasattr(self, 'perdin_lama_hari_input'):
            return

        tgl_mulai = self.tgl_mulai_input.date()
        tgl_selesai = self.tgl_selesai_input.date()

        # Calculate days difference (inclusive)
        lama_hari = tgl_mulai.daysTo(tgl_selesai) + 1

        if lama_hari >= 1:
            self.perdin_lama_hari_input.setText(str(lama_hari))
        else:
            self.perdin_lama_hari_input.setText("1")

    def _on_save(self):
        """Handle save button click."""
        # Validate
        if not self._validate():
            return

        # Collect data
        data = self._collect_data()

        # Emit signal
        self.saved.emit(data)

    def _validate(self) -> bool:
        """Validate form data."""
        errors = []

        if not self.nama_input.text().strip():
            errors.append("Nama kegiatan wajib diisi")

        if self.mekanisme == "UP":
            if self.estimasi_input.value() > BATAS_UP_MAKSIMAL:
                errors.append(f"Estimasi biaya UP maksimal {format_rupiah(BATAS_UP_MAKSIMAL)}")

        if self.mekanisme == "LS":
            if self._jenis_dasar_ls == "KONTRAK":
                # Validate kontrak fields
                if not self.kontrak_nomor_input.text().strip():
                    errors.append("Nomor kontrak wajib diisi")
                if self.nilai_kontrak_input.value() <= 0:
                    errors.append("Nilai kontrak wajib diisi")
            else:
                # Validate surat tugas fields
                if not self.st_nomor_input.text().strip():
                    errors.append("Nomor Surat Tugas wajib diisi")
                if not self.st_tujuan_input.text().strip():
                    errors.append("Tujuan perjalanan wajib diisi")
                if self.st_biaya_input.value() <= 0:
                    errors.append("Estimasi biaya perjalanan wajib diisi")

        if errors:
            QMessageBox.warning(
                self,
                "Validasi Error",
                "\n".join(errors)
            )
            return False

        return True

    def _collect_data(self) -> Dict[str, Any]:
        """Collect form data."""
        data = {
            'mekanisme': self.mekanisme,
            'nama_kegiatan': self.nama_input.text().strip(),
            'jenis_belanja': self.jenis_combo.currentData(),
            'kode_akun': self.akun_input.currentData() or self.akun_input.currentText().split(' - ')[0].strip(),
            'jenis_dasar': self.dasar_jenis_combo.currentText(),
            'nomor_dasar': self.dasar_nomor_input.text().strip(),
            'tanggal_dasar': self.dasar_tgl_input.date().toString('yyyy-MM-dd'),
            'perihal_dasar': self.dasar_perihal_input.toPlainText().strip(),
        }

        if self._transaksi_id:
            data['id'] = self._transaksi_id

        if self.mekanisme in ["UP", "TUP"]:
            data['estimasi_biaya'] = self.estimasi_input.value()
            data['tanggal_kegiatan_mulai'] = self.tgl_mulai_input.date().toString('yyyy-MM-dd')
            data['tanggal_kegiatan_selesai'] = self.tgl_selesai_input.date().toString('yyyy-MM-dd')
            data['penerima_nama'] = self.penerima_nama_input.text().strip()
            data['penerima_nip'] = self.penerima_nip_input.text().strip()
            data['penerima_jabatan'] = self.penerima_jabatan_input.text().strip()

            # DIPA selection info
            if hasattr(self, 'dipa_ro_combo'):
                data['dipa_ro'] = self.dipa_ro_combo.currentData()
                data['dipa_akun'] = self.dipa_akun_combo.currentData() if hasattr(self, 'dipa_akun_combo') else None
                dipa_item = self.dipa_detail_combo.currentData() if hasattr(self, 'dipa_detail_combo') else None
                if isinstance(dipa_item, dict):
                    data['dipa_item_id'] = dipa_item.get('id')
                    data['dipa_uraian'] = dipa_item.get('uraian_item', '')

            # Perjalanan Dinas specific fields (only if jenis = perdin)
            if self.jenis_combo.currentData() == "perdin" and hasattr(self, 'perdin_tujuan_input'):
                data['perdin_tujuan'] = self.perdin_tujuan_input.text().strip()
                data['perdin_maksud'] = self.perdin_maksud_input.text().strip()
                data['perdin_alat_angkut'] = self.perdin_alat_angkut_combo.currentText()
                data['perdin_tingkat'] = self.perdin_tingkat_combo.currentText()
                data['perdin_lama_hari'] = self.perdin_lama_hari_input.text().strip()
        else:
            # LS mode - check which mode (KONTRAK or SURAT_TUGAS)
            data['jenis_dasar_ls'] = self._jenis_dasar_ls

            if self._jenis_dasar_ls == "KONTRAK":
                data['nomor_kontrak'] = self.kontrak_nomor_input.text().strip()
                data['tanggal_kontrak'] = self.kontrak_tgl_input.date().toString('yyyy-MM-dd')
                data['nilai_kontrak'] = self.nilai_kontrak_input.value()
                data['estimasi_biaya'] = self.nilai_kontrak_input.value()
                data['penyedia_id'] = self.penyedia_combo.currentData()
            else:
                # SURAT_TUGAS mode
                data['nomor_st'] = self.st_nomor_input.text().strip()
                data['tanggal_st'] = self.st_tgl_input.date().toString('yyyy-MM-dd')
                data['tujuan_perjalanan'] = self.st_tujuan_input.text().strip()
                data['tanggal_berangkat'] = self.st_tgl_berangkat.date().toString('yyyy-MM-dd')
                data['tanggal_kembali'] = self.st_tgl_kembali.date().toString('yyyy-MM-dd')
                data['estimasi_biaya'] = self.st_biaya_input.value()
                # Override dasar info with surat tugas
                data['jenis_dasar'] = "Surat Tugas"
                data['nomor_dasar'] = self.st_nomor_input.text().strip()
                data['tanggal_dasar'] = self.st_tgl_input.date().toString('yyyy-MM-dd')

        return data

    def set_transaksi(self, data: Dict[str, Any]):
        """Load existing transaksi data into form."""
        self._is_edit = True
        self._transaksi_id = data.get('id')

        # Update header
        # ... would need to update title label

        # Fill form fields
        self.nama_input.setText(data.get('nama_kegiatan', ''))

        # Set jenis belanja
        jenis = data.get('jenis_belanja')
        for i in range(self.jenis_combo.count()):
            if self.jenis_combo.itemData(i) == jenis:
                self.jenis_combo.setCurrentIndex(i)
                break

        # Set kode akun - find in dropdown or set as text
        kode_akun = data.get('kode_akun', '')
        found = False
        for i in range(self.akun_input.count()):
            if self.akun_input.itemData(i) == kode_akun:
                self.akun_input.setCurrentIndex(i)
                found = True
                break
        if not found and kode_akun:
            self.akun_input.setCurrentText(kode_akun)

        if self.mekanisme in ["UP", "TUP"]:
            self.estimasi_input.setValue(data.get('estimasi_biaya', 0) or 0)
            self.penerima_nama_input.setText(data.get('penerima_nama', ''))
            self.penerima_nip_input.setText(data.get('penerima_nip', ''))
            self.penerima_jabatan_input.setText(data.get('penerima_jabatan', ''))

            # Load Perjalanan Dinas fields if available
            if hasattr(self, 'perdin_tujuan_input'):
                self.perdin_tujuan_input.setText(data.get('perdin_tujuan', ''))
                self.perdin_maksud_input.setText(data.get('perdin_maksud', ''))

                alat_angkut = data.get('perdin_alat_angkut', '')
                for i in range(self.perdin_alat_angkut_combo.count()):
                    if self.perdin_alat_angkut_combo.itemText(i) == alat_angkut:
                        self.perdin_alat_angkut_combo.setCurrentIndex(i)
                        break

                tingkat = data.get('perdin_tingkat', 'C')
                for i in range(self.perdin_tingkat_combo.count()):
                    if self.perdin_tingkat_combo.itemText(i) == tingkat:
                        self.perdin_tingkat_combo.setCurrentIndex(i)
                        break

                # Show perdin section if jenis is perdin
                if jenis == "perdin":
                    self.perdin_section_widget.setVisible(True)

        # Dasar hukum
        self.dasar_nomor_input.setText(data.get('nomor_dasar', ''))
        self.dasar_perihal_input.setPlainText(data.get('perihal_dasar', ''))

    def set_penyedia_list(self, penyedia_list: list):
        """Set penyedia dropdown options."""
        self.penyedia_combo.clear()
        self.penyedia_combo.addItem("-- Pilih Penyedia --", None)

        for p in penyedia_list:
            self.penyedia_combo.addItem(p.get('nama', ''), p.get('id'))

    def clear(self):
        """Clear all form fields."""
        self._transaksi_id = None
        self._is_edit = False

        self.nama_input.clear()
        self.jenis_combo.setCurrentIndex(0)
        self.akun_input.setCurrentIndex(0)  # Reset to first (empty) option

        if hasattr(self, 'estimasi_input'):
            self.estimasi_input.setValue(0)

        if hasattr(self, 'penerima_nama_input'):
            self.penerima_nama_input.clear()
            self.penerima_nip_input.clear()
            self.penerima_jabatan_input.clear()

        self.dasar_nomor_input.clear()
        self.dasar_perihal_input.clear()
