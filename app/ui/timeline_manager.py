"""
PPK DOCUMENT FACTORY v3.0 - Timeline Manager
=============================================
UI untuk mengelola Timeline Tanggal dan Penomoran Dokumen
"""

import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QMessageBox, QFrame, QDateEdit, QSpinBox, QCheckBox,
    QAbstractItemView, QScrollArea, QSplitter, QTabWidget
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QColor, QIcon

from app.core.database import get_db_manager
from app.core.config import WORKFLOW_STAGES, TAHUN_ANGGARAN


# ============================================================================
# INDONESIAN DATE FORMATTING
# ============================================================================

BULAN_INDONESIA = [
    '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]

HARI_INDONESIA = [
    'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'
]

def format_tanggal_indonesia(tgl, format_type: str = 'long') -> str:
    """
    Format tanggal ke bahasa Indonesia
    
    format_type:
        - 'long': 15 Januari 2026
        - 'full': Kamis, 15 Januari 2026
        - 'short': 15/01/2026
        - 'medium': 15 Jan 2026
    """
    if tgl is None:
        return ''
    
    if isinstance(tgl, str):
        try:
            if '-' in tgl:
                tgl = datetime.strptime(tgl, '%Y-%m-%d').date()
            elif '/' in tgl:
                tgl = datetime.strptime(tgl, '%d/%m/%Y').date()
            else:
                return tgl
        except ValueError:
            return tgl
    
    if isinstance(tgl, datetime):
        tgl = tgl.date()
    
    if format_type == 'short':
        return tgl.strftime('%d/%m/%Y')
    elif format_type == 'medium':
        bulan_short = BULAN_INDONESIA[tgl.month][:3]
        return f"{tgl.day} {bulan_short} {tgl.year}"
    elif format_type == 'full':
        hari = HARI_INDONESIA[tgl.weekday()]
        bulan = BULAN_INDONESIA[tgl.month]
        return f"{hari}, {tgl.day} {bulan} {tgl.year}"
    else:  # long
        bulan = BULAN_INDONESIA[tgl.month]
        return f"{tgl.day} {bulan} {tgl.year}"


def parse_tanggal(tgl_str: str) -> Optional[date]:
    """Parse various date formats to date object"""
    if not tgl_str:
        return None
    
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%d %B %Y',
        '%d %b %Y',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(tgl_str, fmt).date()
        except ValueError:
            continue
    
    return None


# ============================================================================
# DOCUMENT TIMELINE CONFIGURATION
# ============================================================================

# Document types dengan urutan kronologis dan aturan validasi
DOKUMEN_TIMELINE = [
    {
        'code': 'SPESIFIKASI',
        'name': 'Spesifikasi Teknis',
        'prefix': 'SPEK',
        'format': '{nomor}/SPEK.PL/{romawi}/{tahun}',
        'can_be_before': [],  # Tidak ada dokumen yang harus sebelumnya
        'description': 'Dokumen awal, tanggal bebas'
    },
    {
        'code': 'HPS',
        'name': 'Harga Perkiraan Sendiri',
        'prefix': 'HPS',
        'format': '{nomor}/HPS.PL/{romawi}/{tahun}',
        'can_be_before': ['SPESIFIKASI'],
        'description': 'Tanggal >= Spesifikasi'
    },
    {
        'code': 'KAK',
        'name': 'Kerangka Acuan Kerja',
        'prefix': 'KAK',
        'format': '{nomor}/KAK.PL/{romawi}/{tahun}',
        'can_be_before': ['SPESIFIKASI', 'HPS'],
        'description': 'Tanggal >= HPS'
    },
    # === PROSES PEMILIHAN PENGADAAN LANGSUNG ===
    {
        'code': 'UNDANGAN_PL',
        'name': 'Surat Undangan Pengadaan Langsung',
        'prefix': 'UND.PL',
        'format': '{nomor}/UND.PL/{romawi}/{tahun}',
        'can_be_before': ['KAK'],
        'must_same_or_after': 'KAK',
        'description': 'Undangan ke penyedia setelah dokumen persiapan selesai'
    },
    {
        'code': 'BAHPL',
        'name': 'Berita Acara Hasil Pengadaan Langsung',
        'prefix': 'BA.HPL',
        'format': '{nomor}/BA.HPL/{romawi}/{tahun}',
        'can_be_before': ['UNDANGAN_PL'],
        'must_same_or_after': 'UNDANGAN_PL',
        'description': 'BA hasil negosiasi/evaluasi pengadaan langsung'
    },
    # === KONTRAK ===
    {
        'code': 'SPK',
        'name': 'Surat Perintah Kerja',
        'prefix': 'SPK',
        'format': '{nomor}/SPK.PL/{romawi}/{tahun}',
        'can_be_before': ['SPESIFIKASI', 'HPS', 'KAK', 'UNDANGAN_PL', 'BAHPL'],
        'must_same_or_after': 'BAHPL',
        'description': 'Tanggal >= BA Hasil PL, setelah proses pemilihan'
    },
    {
        'code': 'SPMK',
        'name': 'Surat Perintah Mulai Kerja',
        'prefix': 'SPMK',
        'format': '{nomor}/SPMK.PL/{romawi}/{tahun}',
        'can_be_before': ['SPK'],
        'must_same_or_after': 'SPK',
        'description': 'Tanggal >= SPK (bisa sama)'
    },
    {
        'code': 'BAHP',
        'name': 'Berita Acara Hasil Pemeriksaan',
        'prefix': 'BAHP',
        'format': '{nomor}/BAHP.PL/{romawi}/{tahun}',
        'can_be_before': ['SPMK'],
        'min_days_after': {'SPMK': 'jangka_waktu'},  # Minimal setelah jangka waktu
        'description': 'Tanggal >= SPMK + jangka waktu'
    },
    {
        'code': 'BAST',
        'name': 'Berita Acara Serah Terima',
        'prefix': 'BAST',
        'format': '{nomor}/BAST.PL/{romawi}/{tahun}',
        'can_be_before': ['BAHP'],
        'must_same_or_after': 'BAHP',
        'description': 'Tanggal >= BAHP'
    },
    {
        'code': 'SPP',
        'name': 'Surat Permintaan Pembayaran',
        'prefix': 'SPP',
        'format': '{nomor}/SPP.LS/{romawi}/{tahun}',
        'can_be_before': ['BAST'],
        'must_same_or_after': 'BAST',
        'description': 'Tanggal >= BAST'
    },
    {
        'code': 'KUITANSI',
        'name': 'Kuitansi',
        'prefix': 'KWT',
        'format': '{nomor}/KWT.PL/{romawi}/{tahun}',
        'can_be_before': ['SPP'],
        'must_same_or_after': 'SPP',
        'description': 'Tanggal >= SPP'
    },
]

# Build lookup
DOKUMEN_CONFIG = {d['code']: d for d in DOKUMEN_TIMELINE}


# ============================================================================
# TIMELINE VALIDATOR
# ============================================================================

class TimelineValidator:
    """Validate document timeline dates"""
    
    def __init__(self, paket_id: int):
        self.paket_id = paket_id
        self.db = get_db_manager()
        self.paket = self.db.get_paket(paket_id)
        self.jangka_waktu = self.paket.get('jangka_waktu', 30) if self.paket else 30
    
    def get_all_dates(self) -> Dict[str, date]:
        """Get all timeline dates for the paket"""
        timeline = self.db.get_dokumen_timeline(self.paket_id)
        dates = {}
        for entry in timeline:
            if entry.get('tanggal_dokumen'):
                tgl = parse_tanggal(entry['tanggal_dokumen'])
                if tgl:
                    dates[entry['doc_type']] = tgl
        return dates
    
    def validate_date(self, doc_type: str, proposed_date: date) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a proposed date for a document
        
        Returns:
            (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        config = DOKUMEN_CONFIG.get(doc_type)
        if not config:
            return True, [], []
        
        all_dates = self.get_all_dates()
        
        # Check must_same_or_after
        if 'must_same_or_after' in config:
            ref_doc = config['must_same_or_after']
            if ref_doc in all_dates:
                ref_date = all_dates[ref_doc]
                if proposed_date < ref_date:
                    errors.append(
                        f"Tanggal {doc_type} ({format_tanggal_indonesia(proposed_date)}) "
                        f"tidak boleh sebelum {ref_doc} ({format_tanggal_indonesia(ref_date)})"
                    )
        
        # Check min_days_after
        if 'min_days_after' in config:
            for ref_doc, days_spec in config['min_days_after'].items():
                if ref_doc in all_dates:
                    ref_date = all_dates[ref_doc]
                    
                    if days_spec == 'jangka_waktu':
                        min_days = self.jangka_waktu
                    else:
                        min_days = int(days_spec)
                    
                    expected_date = ref_date + timedelta(days=min_days)
                    
                    if proposed_date < expected_date:
                        # Warning, not error - could be early completion
                        days_diff = (expected_date - proposed_date).days
                        warnings.append(
                            f"Tanggal {doc_type} ({format_tanggal_indonesia(proposed_date)}) "
                            f"adalah {days_diff} hari sebelum perkiraan selesai "
                            f"({format_tanggal_indonesia(expected_date)}). "
                            f"Pastikan pekerjaan memang sudah selesai lebih awal."
                        )
        
        # Check can_be_before (all referenced docs should have earlier or equal dates)
        can_be_before = config.get('can_be_before', [])
        for ref_doc in can_be_before:
            if ref_doc in all_dates:
                ref_date = all_dates[ref_doc]
                if proposed_date < ref_date:
                    errors.append(
                        f"Tanggal {doc_type} ({format_tanggal_indonesia(proposed_date)}) "
                        f"tidak boleh sebelum {ref_doc} ({format_tanggal_indonesia(ref_date)})"
                    )
        
        # Check for future dates
        today = date.today()
        if proposed_date > today:
            warnings.append(
                f"Tanggal {doc_type} ({format_tanggal_indonesia(proposed_date)}) "
                f"adalah tanggal di masa depan"
            )
        
        # Check year matches tahun_anggaran
        tahun_anggaran = self.paket.get('tahun_anggaran', TAHUN_ANGGARAN) if self.paket else TAHUN_ANGGARAN
        if proposed_date.year != tahun_anggaran:
            warnings.append(
                f"Tahun dokumen ({proposed_date.year}) berbeda dengan "
                f"tahun anggaran paket ({tahun_anggaran})"
            )
        
        is_valid = len(errors) == 0
        return is_valid, errors, warnings
    
    def suggest_date(self, doc_type: str) -> date:
        """Suggest appropriate date for a document"""
        config = DOKUMEN_CONFIG.get(doc_type)
        if not config:
            return date.today()
        
        all_dates = self.get_all_dates()
        
        # Find the latest date from documents that should come before
        latest_before = None
        can_be_before = config.get('can_be_before', [])
        
        for ref_doc in can_be_before:
            if ref_doc in all_dates:
                if latest_before is None or all_dates[ref_doc] > latest_before:
                    latest_before = all_dates[ref_doc]
        
        # Check min_days_after
        if 'min_days_after' in config:
            for ref_doc, days_spec in config['min_days_after'].items():
                if ref_doc in all_dates:
                    ref_date = all_dates[ref_doc]
                    
                    if days_spec == 'jangka_waktu':
                        min_days = self.jangka_waktu
                    else:
                        min_days = int(days_spec)
                    
                    expected = ref_date + timedelta(days=min_days)
                    if latest_before is None or expected > latest_before:
                        latest_before = expected
        
        if latest_before:
            return latest_before
        
        return date.today()


# ============================================================================
# TIMELINE ENTRY WIDGET
# ============================================================================

class TimelineEntryWidget(QFrame):
    """Widget for single timeline entry"""
    
    date_changed = Signal(str, str)  # doc_type, new_date
    
    def __init__(self, doc_config: dict, parent=None):
        super().__init__(parent)
        self.doc_config = doc_config
        self.doc_type = doc_config['code']
        self.validator = None
        self.paket_id = None
        
        self.setup_ui()
    
    def setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            TimelineEntryWidget {
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
            TimelineEntryWidget[status="completed"] {
                border-left: 4px solid #27ae60;
            }
            TimelineEntryWidget[status="warning"] {
                border-left: 4px solid #f39c12;
            }
            TimelineEntryWidget[status="error"] {
                border-left: 4px solid #e74c3c;
            }
            TimelineEntryWidget[status="pending"] {
                border-left: 4px solid #bdc3c7;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header
        header = QHBoxLayout()
        
        self.lbl_icon = QLabel("📄")
        self.lbl_icon.setStyleSheet("font-size: 20px;")
        header.addWidget(self.lbl_icon)
        
        self.lbl_name = QLabel(self.doc_config['name'])
        self.lbl_name.setStyleSheet("font-weight: bold; font-size: 13px;")
        header.addWidget(self.lbl_name)
        
        header.addStretch()
        
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("font-size: 11px;")
        header.addWidget(self.lbl_status)
        
        layout.addLayout(header)
        
        # Form
        form = QGridLayout()
        form.setSpacing(5)
        
        # Nomor
        form.addWidget(QLabel("Nomor:"), 0, 0)
        self.txt_nomor = QLineEdit()
        self.txt_nomor.setPlaceholderText("Klik 'Auto' untuk generate...")
        form.addWidget(self.txt_nomor, 0, 1)
        
        self.btn_auto_nomor = QPushButton("Auto")
        self.btn_auto_nomor.setFixedWidth(50)
        self.btn_auto_nomor.clicked.connect(self.generate_nomor)
        form.addWidget(self.btn_auto_nomor, 0, 2)
        
        # Tanggal
        form.addWidget(QLabel("Tanggal:"), 1, 0)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd MMMM yyyy")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self.on_date_changed)
        form.addWidget(self.date_edit, 1, 1)
        
        self.btn_suggest = QPushButton("Saran")
        self.btn_suggest.setFixedWidth(50)
        self.btn_suggest.setToolTip("Sarankan tanggal berdasarkan timeline")
        self.btn_suggest.clicked.connect(self.suggest_date)
        form.addWidget(self.btn_suggest, 1, 2)
        
        layout.addLayout(form)
        
        # Tanggal display (Indonesian format)
        self.lbl_tanggal_indo = QLabel("")
        self.lbl_tanggal_indo.setStyleSheet("color: #2980b9; font-style: italic;")
        layout.addWidget(self.lbl_tanggal_indo)
        
        # Validation message
        self.lbl_validation = QLabel("")
        self.lbl_validation.setWordWrap(True)
        self.lbl_validation.setStyleSheet("font-size: 11px;")
        self.lbl_validation.hide()
        layout.addWidget(self.lbl_validation)
        
        # Description
        self.lbl_desc = QLabel(self.doc_config.get('description', ''))
        self.lbl_desc.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.lbl_desc)
        
        self.update_tanggal_display()
    
    def set_paket(self, paket_id: int):
        """Set paket for validation"""
        self.paket_id = paket_id
        self.validator = TimelineValidator(paket_id)
    
    def set_data(self, nomor: str, tanggal: str):
        """Set entry data"""
        if nomor:
            self.txt_nomor.setText(nomor)
        
        if tanggal:
            tgl = parse_tanggal(tanggal)
            if tgl:
                self.date_edit.setDate(QDate(tgl.year, tgl.month, tgl.day))
        
        self.update_tanggal_display()
        self.validate()
    
    def get_data(self) -> Tuple[str, str]:
        """Get entry data (nomor, tanggal)"""
        nomor = self.txt_nomor.text().strip()
        qdate = self.date_edit.date()
        tanggal = f"{qdate.year()}-{qdate.month():02d}-{qdate.day():02d}"
        return nomor, tanggal
    
    def update_tanggal_display(self):
        """Update Indonesian date display"""
        qdate = self.date_edit.date()
        tgl = date(qdate.year(), qdate.month(), qdate.day())
        self.lbl_tanggal_indo.setText(f"📅 {format_tanggal_indonesia(tgl, 'full')}")
    
    def on_date_changed(self):
        """Handle date change"""
        self.update_tanggal_display()
        self.validate()
        
        nomor, tanggal = self.get_data()
        self.date_changed.emit(self.doc_type, tanggal)
    
    def validate(self) -> bool:
        """Validate current date"""
        if not self.validator:
            return True
        
        qdate = self.date_edit.date()
        tgl = date(qdate.year(), qdate.month(), qdate.day())
        
        is_valid, errors, warnings = self.validator.validate_date(self.doc_type, tgl)
        
        # Update status
        if errors:
            self.setProperty('status', 'error')
            self.lbl_status.setText("❌ Error")
            self.lbl_status.setStyleSheet("color: #e74c3c; font-size: 11px;")
            self.lbl_validation.setText("\n".join(errors))
            self.lbl_validation.setStyleSheet("color: #e74c3c; font-size: 11px;")
            self.lbl_validation.show()
        elif warnings:
            self.setProperty('status', 'warning')
            self.lbl_status.setText("⚠️ Peringatan")
            self.lbl_status.setStyleSheet("color: #f39c12; font-size: 11px;")
            self.lbl_validation.setText("\n".join(warnings))
            self.lbl_validation.setStyleSheet("color: #f39c12; font-size: 11px;")
            self.lbl_validation.show()
        else:
            nomor = self.txt_nomor.text().strip()
            if nomor:
                self.setProperty('status', 'completed')
                self.lbl_status.setText("✅ Lengkap")
                self.lbl_status.setStyleSheet("color: #27ae60; font-size: 11px;")
            else:
                self.setProperty('status', 'pending')
                self.lbl_status.setText("⏳ Belum lengkap")
                self.lbl_status.setStyleSheet("color: #95a5a6; font-size: 11px;")
            self.lbl_validation.hide()
        
        self.style().unpolish(self)
        self.style().polish(self)
        
        return is_valid
    
    def generate_nomor(self):
        """Generate auto number"""
        if not self.paket_id:
            return
        
        db = get_db_manager()
        config = self.doc_config
        
        nomor = db.get_next_nomor(
            self.doc_type,
            prefix=config.get('prefix', ''),
            format_template=config.get('format', '')
        )
        
        self.txt_nomor.setText(nomor)
        self.validate()
    
    def suggest_date(self):
        """Suggest appropriate date"""
        if not self.validator:
            return
        
        suggested = self.validator.suggest_date(self.doc_type)
        self.date_edit.setDate(QDate(suggested.year, suggested.month, suggested.day))


# ============================================================================
# TIMELINE MANAGER DIALOG
# ============================================================================

class TimelineManager(QDialog):
    """Main dialog for managing document timeline"""
    
    timeline_changed = Signal()
    
    def __init__(self, paket_id: int, parent=None):
        super().__init__(parent)
        self.paket_id = paket_id
        self.db = get_db_manager()
        self.paket = self.db.get_paket(paket_id)
        
        self.entries = {}
        
        self.setWindowTitle(f"Timeline Dokumen - {self.paket.get('nama', '')}")
        self.setMinimumSize(800, 700)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("📅 Timeline Tanggal & Penomoran Dokumen")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Auto-fill all button
        btn_auto_all = QPushButton("🔄 Auto Semua Nomor")
        btn_auto_all.clicked.connect(self.auto_fill_all_numbers)
        header.addWidget(btn_auto_all)
        
        layout.addLayout(header)
        
        # Info
        info = QLabel(
            "💡 Isi nomor dan tanggal dokumen. Sistem akan memvalidasi urutan kronologis.\n"
            "Format tanggal otomatis dalam Bahasa Indonesia."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; padding: 8px; background: #f8f9fa; border-radius: 4px;")
        layout.addWidget(info)
        
        # Paket info
        paket_info = QGroupBox("Informasi Paket")
        paket_layout = QGridLayout()
        
        paket_layout.addWidget(QLabel("Nama Paket:"), 0, 0)
        paket_layout.addWidget(QLabel(self.paket.get('nama', '-')), 0, 1)
        
        paket_layout.addWidget(QLabel("Tahun Anggaran:"), 0, 2)
        paket_layout.addWidget(QLabel(str(self.paket.get('tahun_anggaran', '-'))), 0, 3)
        
        paket_layout.addWidget(QLabel("Jangka Waktu:"), 1, 0)
        paket_layout.addWidget(QLabel(f"{self.paket.get('jangka_waktu', 30)} hari"), 1, 1)
        
        paket_info.setLayout(paket_layout)
        layout.addWidget(paket_info)
        
        # Timeline entries (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        entries_widget = QWidget()
        entries_layout = QVBoxLayout(entries_widget)
        entries_layout.setSpacing(10)
        
        for doc_config in DOKUMEN_TIMELINE:
            entry = TimelineEntryWidget(doc_config)
            entry.set_paket(self.paket_id)
            entry.date_changed.connect(self.on_entry_changed)
            
            self.entries[doc_config['code']] = entry
            entries_layout.addWidget(entry)
        
        entries_layout.addStretch()
        scroll.setWidget(entries_widget)
        layout.addWidget(scroll)
        
        # Numbering format settings
        format_group = QGroupBox("Pengaturan Format Penomoran")
        format_layout = QFormLayout()
        
        self.txt_format = QLineEdit()
        self.txt_format.setText("{nomor}/{prefix}/{romawi}/{tahun}")
        self.txt_format.setToolTip(
            "Variabel: {nomor}, {prefix}, {bulan}, {tahun}, {romawi}\n"
            "Contoh: {nomor}/SPK.PL/{romawi}/{tahun} → 001/SPK.PL/I/2026"
        )
        format_layout.addRow("Format Default:", self.txt_format)
        
        format_help = QLabel(
            "Variabel: {nomor} = nomor urut, {prefix} = kode dokumen, "
            "{bulan} = bulan (01-12), {romawi} = bulan romawi (I-XII), {tahun} = tahun"
        )
        format_help.setStyleSheet("color: #666; font-size: 10px;")
        format_help.setWordWrap(True)
        format_layout.addRow("", format_help)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_validate = QPushButton("✓ Validasi Semua")
        btn_validate.clicked.connect(self.validate_all)
        btn_layout.addWidget(btn_validate)
        
        btn_layout.addStretch()
        
        btn_save = QPushButton("💾 Simpan")
        btn_save.setObjectName("btnSuccess")
        btn_save.clicked.connect(self.save_all)
        btn_layout.addWidget(btn_save)
        
        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        
        # Style
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton#btnSuccess {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#btnSuccess:hover {
                background-color: #219a52;
            }
        """)
    
    def load_data(self):
        """Load existing timeline data"""
        timeline = self.db.get_dokumen_timeline(self.paket_id)
        
        for entry_data in timeline:
            doc_type = entry_data['doc_type']
            if doc_type in self.entries:
                self.entries[doc_type].set_data(
                    entry_data.get('nomor_dokumen', ''),
                    entry_data.get('tanggal_dokumen', '')
                )
    
    def on_entry_changed(self, doc_type: str, tanggal: str):
        """Handle entry change - revalidate affected entries"""
        # Revalidate all entries after this one
        found = False
        for code, entry in self.entries.items():
            if code == doc_type:
                found = True
                continue
            if found:
                entry.validate()
    
    def auto_fill_all_numbers(self):
        """Auto-fill all document numbers"""
        reply = QMessageBox.question(
            self, "Konfirmasi",
            "Generate nomor otomatis untuk semua dokumen yang belum memiliki nomor?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for entry in self.entries.values():
                if not entry.txt_nomor.text().strip():
                    entry.generate_nomor()
    
    def validate_all(self) -> bool:
        """Validate all entries"""
        all_valid = True
        errors = []
        warnings = []
        
        for doc_type, entry in self.entries.items():
            if not entry.validate():
                all_valid = False
        
        if all_valid:
            QMessageBox.information(self, "Validasi", "✅ Semua tanggal valid!")
        else:
            QMessageBox.warning(
                self, "Validasi",
                "⚠️ Ada beberapa tanggal yang perlu diperbaiki.\n"
                "Periksa entri yang ditandai merah atau kuning."
            )
        
        return all_valid
    
    def save_all(self):
        """Save all timeline entries"""
        # Validate first
        all_valid = True
        has_warnings = False
        
        for entry in self.entries.values():
            if not entry.validate():
                # Check if it's error or just warning
                qdate = entry.date_edit.date()
                tgl = date(qdate.year(), qdate.month(), qdate.day())
                is_valid, errors, warnings = entry.validator.validate_date(entry.doc_type, tgl)
                
                if errors:
                    all_valid = False
                if warnings:
                    has_warnings = True
        
        if not all_valid:
            reply = QMessageBox.warning(
                self, "Error Validasi",
                "Ada tanggal yang tidak valid (ditandai merah).\n"
                "Perbaiki terlebih dahulu sebelum menyimpan.",
                QMessageBox.Ok
            )
            return
        
        if has_warnings:
            reply = QMessageBox.question(
                self, "Peringatan",
                "Ada beberapa peringatan (ditandai kuning).\n"
                "Tetap simpan?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Save all entries
        try:
            for doc_type, entry in self.entries.items():
                nomor, tanggal = entry.get_data()
                if nomor or tanggal:
                    self.db.set_dokumen_timeline(
                        self.paket_id, doc_type, nomor, tanggal
                    )
            
            QMessageBox.information(self, "Sukses", "Timeline berhasil disimpan!")
            self.timeline_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {str(e)}")


# ============================================================================
# HELPER FUNCTION
# ============================================================================

def show_timeline_manager(paket_id: int, parent=None) -> TimelineManager:
    """Show timeline manager dialog"""
    dialog = TimelineManager(paket_id, parent)
    dialog.exec()
    return dialog
