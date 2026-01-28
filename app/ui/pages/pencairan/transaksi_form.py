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

        # Penyedia section (for LS)
        if self.mekanisme == "LS":
            penyedia_section = self._create_penyedia_section()
            form_layout.addWidget(penyedia_section)

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
        """Create basic info section."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        layout.addWidget(self._create_section_title("Informasi Dasar"))

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Nama Kegiatan
        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText("Contoh: Rapat Koordinasi Tim Teknis")
        self.nama_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("Nama Kegiatan *", self.nama_input)

        # Jenis Belanja
        self.jenis_combo = QComboBox()
        for jenis in JENIS_BELANJA:
            self.jenis_combo.addItem(jenis['nama'], jenis['kode'])
        self.jenis_combo.setStyleSheet(self._get_input_style())
        form_layout.addRow("Jenis Belanja *", self.jenis_combo)

        # Kode Akun
        self.akun_input = QLineEdit()
        self.akun_input.setPlaceholderText("Contoh: 5.2.2.03")
        self.akun_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("Kode Akun", self.akun_input)

        # Auto-fill kode akun when jenis changes
        self.jenis_combo.currentIndexChanged.connect(self._on_jenis_changed)

        layout.addLayout(form_layout)

        return section

    def _create_financial_section_up(self) -> QWidget:
        """Create financial section for UP/TUP."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        layout.addWidget(self._create_section_title("Informasi Keuangan"))

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Estimasi Biaya
        self.estimasi_input = QDoubleSpinBox()
        self.estimasi_input.setRange(0, BATAS_UP_MAKSIMAL)
        self.estimasi_input.setDecimals(0)
        self.estimasi_input.setPrefix("Rp ")
        self.estimasi_input.setGroupSeparatorShown(True)
        self.estimasi_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("Estimasi Biaya *", self.estimasi_input)

        # Warning for UP limit
        if self.mekanisme == "UP":
            warning = QLabel(f"Maksimal UP: {format_rupiah(BATAS_UP_MAKSIMAL)}")
            warning.setStyleSheet("font-size: 11px; color: #f39c12; font-style: italic;")
            form_layout.addRow("", warning)

        # Tanggal kegiatan
        date_layout = QHBoxLayout()

        self.tgl_mulai_input = QDateEdit()
        self.tgl_mulai_input.setCalendarPopup(True)
        self.tgl_mulai_input.setDate(QDate.currentDate())
        self.tgl_mulai_input.setStyleSheet(self._get_input_style())
        date_layout.addWidget(QLabel("Mulai:"))
        date_layout.addWidget(self.tgl_mulai_input)

        self.tgl_selesai_input = QDateEdit()
        self.tgl_selesai_input.setCalendarPopup(True)
        self.tgl_selesai_input.setDate(QDate.currentDate())
        self.tgl_selesai_input.setStyleSheet(self._get_input_style())
        date_layout.addWidget(QLabel("Selesai:"))
        date_layout.addWidget(self.tgl_selesai_input)

        form_layout.addRow("Tanggal Kegiatan", date_layout)

        layout.addLayout(form_layout)

        return section

    def _create_financial_section_ls(self) -> QWidget:
        """Create financial section for LS."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        layout.addWidget(self._create_section_title("Informasi Kontrak"))

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Nomor Kontrak
        self.kontrak_nomor_input = QLineEdit()
        self.kontrak_nomor_input.setPlaceholderText("Contoh: 001/SPK/2026")
        self.kontrak_nomor_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("Nomor Kontrak/SPK *", self.kontrak_nomor_input)

        # Tanggal Kontrak
        self.kontrak_tgl_input = QDateEdit()
        self.kontrak_tgl_input.setCalendarPopup(True)
        self.kontrak_tgl_input.setDate(QDate.currentDate())
        self.kontrak_tgl_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("Tanggal Kontrak *", self.kontrak_tgl_input)

        # Nilai Kontrak
        self.nilai_kontrak_input = QDoubleSpinBox()
        self.nilai_kontrak_input.setRange(0, 999999999999)
        self.nilai_kontrak_input.setDecimals(0)
        self.nilai_kontrak_input.setPrefix("Rp ")
        self.nilai_kontrak_input.setGroupSeparatorShown(True)
        self.nilai_kontrak_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("Nilai Kontrak *", self.nilai_kontrak_input)

        layout.addLayout(form_layout)

        return section

    def _create_penerima_section(self) -> QWidget:
        """Create penerima (recipient) section for UP/TUP."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        layout.addWidget(self._create_section_title("Penerima / Pelaksana"))

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Nama
        self.penerima_nama_input = QLineEdit()
        self.penerima_nama_input.setPlaceholderText("Nama lengkap dengan gelar")
        self.penerima_nama_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("Nama *", self.penerima_nama_input)

        # NIP
        self.penerima_nip_input = QLineEdit()
        self.penerima_nip_input.setPlaceholderText("NIP 18 digit")
        self.penerima_nip_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("NIP", self.penerima_nip_input)

        # Jabatan
        self.penerima_jabatan_input = QLineEdit()
        self.penerima_jabatan_input.setPlaceholderText("Jabatan penerima")
        self.penerima_jabatan_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("Jabatan", self.penerima_jabatan_input)

        layout.addLayout(form_layout)

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
        """Create dasar hukum section."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        layout.addWidget(self._create_section_title("Dasar Hukum / SK"))

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Jenis dasar
        self.dasar_jenis_combo = QComboBox()
        self.dasar_jenis_combo.addItems([
            "SK KPA", "Surat Tugas", "Nota Dinas", "Undangan", "Lainnya"
        ])
        self.dasar_jenis_combo.setStyleSheet(self._get_input_style())
        form_layout.addRow("Jenis Dasar", self.dasar_jenis_combo)

        # Nomor
        self.dasar_nomor_input = QLineEdit()
        self.dasar_nomor_input.setPlaceholderText("Nomor SK/Surat Tugas")
        self.dasar_nomor_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("Nomor", self.dasar_nomor_input)

        # Tanggal
        self.dasar_tgl_input = QDateEdit()
        self.dasar_tgl_input.setCalendarPopup(True)
        self.dasar_tgl_input.setDate(QDate.currentDate())
        self.dasar_tgl_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("Tanggal", self.dasar_tgl_input)

        # Perihal
        self.dasar_perihal_input = QTextEdit()
        self.dasar_perihal_input.setPlaceholderText("Perihal/tentang...")
        self.dasar_perihal_input.setMaximumHeight(80)
        self.dasar_perihal_input.setStyleSheet(self._get_input_style())
        form_layout.addRow("Perihal", self.dasar_perihal_input)

        layout.addLayout(form_layout)

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

    def _on_jenis_changed(self, index: int):
        """Handle jenis belanja change to auto-fill kode akun."""
        kode = self.jenis_combo.currentData()
        for jenis in JENIS_BELANJA:
            if jenis['kode'] == kode:
                self.akun_input.setText(jenis['akun_default'])
                break

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
            if not self.kontrak_nomor_input.text().strip():
                errors.append("Nomor kontrak wajib diisi")
            if self.nilai_kontrak_input.value() <= 0:
                errors.append("Nilai kontrak wajib diisi")

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
            'kode_akun': self.akun_input.text().strip(),
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
        else:
            data['nomor_kontrak'] = self.kontrak_nomor_input.text().strip()
            data['tanggal_kontrak'] = self.kontrak_tgl_input.date().toString('yyyy-MM-dd')
            data['nilai_kontrak'] = self.nilai_kontrak_input.value()
            data['estimasi_biaya'] = self.nilai_kontrak_input.value()
            data['penyedia_id'] = self.penyedia_combo.currentData()

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

        self.akun_input.setText(data.get('kode_akun', ''))

        if self.mekanisme in ["UP", "TUP"]:
            self.estimasi_input.setValue(data.get('estimasi_biaya', 0) or 0)
            self.penerima_nama_input.setText(data.get('penerima_nama', ''))
            self.penerima_nip_input.setText(data.get('penerima_nip', ''))
            self.penerima_jabatan_input.setText(data.get('penerima_jabatan', ''))

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
        self.akun_input.clear()

        if hasattr(self, 'estimasi_input'):
            self.estimasi_input.setValue(0)

        if hasattr(self, 'penerima_nama_input'):
            self.penerima_nama_input.clear()
            self.penerima_nip_input.clear()
            self.penerima_jabatan_input.clear()

        self.dasar_nomor_input.clear()
        self.dasar_perihal_input.clear()
