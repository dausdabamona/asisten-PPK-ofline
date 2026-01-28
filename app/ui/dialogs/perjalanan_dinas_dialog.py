"""
PPK DOCUMENT FACTORY - Perjalanan Dinas Dialog
===============================================
Dialog untuk membuat dokumen perjalanan dinas lengkap.
Termasuk checklist dokumen dan generate batch templates.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QGroupBox, QCheckBox,
    QScrollArea, QWidget, QMessageBox, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QTabWidget, QLineEdit, QDateEdit,
    QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QColor

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


# Daftar dokumen perjalanan dinas
DOKUMEN_PERJALANAN_DINAS = [
    {
        "kode": "SURAT_TUGAS",
        "nama": "Surat Tugas",
        "template": "surat_tugas.docx",
        "kategori": "persiapan",
        "wajib": True,
        "deskripsi": "Surat tugas dari atasan untuk melakukan perjalanan dinas"
    },
    {
        "kode": "SPPD",
        "nama": "Surat Perjalanan Dinas (SPPD)",
        "template": "sppd.docx",
        "kategori": "persiapan",
        "wajib": True,
        "deskripsi": "Surat resmi perjalanan dinas yang ditandatangani pejabat"
    },
    {
        "kode": "KUITANSI_UM_PD",
        "nama": "Kuitansi Uang Muka Perjalanan Dinas",
        "template": "kuitansi_uang_muka_pd.docx",
        "kategori": "persiapan",
        "wajib": True,
        "deskripsi": "Kuitansi untuk pengambilan uang muka perjalanan"
    },
    {
        "kode": "RINCIAN_BIAYA",
        "nama": "Rincian Biaya Perjalanan Dinas",
        "template": "rincian_biaya_pd.docx",
        "kategori": "persiapan",
        "wajib": True,
        "deskripsi": "Rincian estimasi biaya perjalanan"
    },
    {
        "kode": "PENGELUARAN_RIIL",
        "nama": "Daftar Pengeluaran Riil",
        "template": "daftar_pengeluaran_riil.docx",
        "kategori": "pertanggungjawaban",
        "wajib": True,
        "deskripsi": "Daftar pengeluaran sebenarnya selama perjalanan (diisi setelah pulang)"
    },
    {
        "kode": "KUITANSI_RAMPUNG",
        "nama": "Kuitansi Rampung SPPD",
        "template": "kuitansi_rampung.docx",
        "kategori": "pertanggungjawaban",
        "wajib": True,
        "deskripsi": "Kuitansi pertanggungjawaban setelah perjalanan selesai"
    },
    {
        "kode": "LAPORAN_PD",
        "nama": "Laporan Perjalanan Dinas",
        "template": "laporan_perjalanan_dinas.docx",
        "kategori": "pertanggungjawaban",
        "wajib": True,
        "deskripsi": "Laporan hasil perjalanan dinas"
    },
    {
        "kode": "BOARDING_PASS",
        "nama": "Boarding Pass / Tiket",
        "template": None,
        "kategori": "bukti",
        "wajib": True,
        "deskripsi": "Boarding pass atau bukti tiket perjalanan (upload)"
    },
    {
        "kode": "BUKTI_HOTEL",
        "nama": "Bukti Penginapan / Hotel",
        "template": None,
        "kategori": "bukti",
        "wajib": False,
        "deskripsi": "Bill atau kuitansi hotel (upload)"
    },
]


class DokumenCheckItem(QFrame):
    """Widget untuk satu item dokumen dalam checklist."""

    toggled = Signal(str, bool)  # kode, checked
    generate_clicked = Signal(str)  # kode

    def __init__(self, dokumen: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.dokumen = dokumen
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.dokumen.get('wajib', False))
        self.checkbox.stateChanged.connect(
            lambda state: self.toggled.emit(self.dokumen['kode'], state == Qt.Checked)
        )
        layout.addWidget(self.checkbox)

        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        nama = QLabel(self.dokumen['nama'])
        nama.setStyleSheet("font-weight: bold; color: #2c3e50;")
        info_layout.addWidget(nama)

        desc = QLabel(self.dokumen.get('deskripsi', ''))
        desc.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        desc.setWordWrap(True)
        info_layout.addWidget(desc)

        layout.addLayout(info_layout, 1)

        # Badge kategori
        kategori = self.dokumen.get('kategori', 'lainnya')
        badge_colors = {
            'persiapan': '#3498db',
            'pertanggungjawaban': '#9b59b6',
            'bukti': '#f39c12',
        }
        badge = QLabel(kategori.upper())
        badge.setStyleSheet(f"""
            background-color: {badge_colors.get(kategori, '#95a5a6')};
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10px;
        """)
        layout.addWidget(badge)

        # Generate button (only if has template)
        if self.dokumen.get('template'):
            gen_btn = QPushButton("Template")
            gen_btn.setFixedWidth(70)
            gen_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover { background-color: #1e8449; }
            """)
            gen_btn.clicked.connect(lambda: self.generate_clicked.emit(self.dokumen['kode']))
            layout.addWidget(gen_btn)
        else:
            upload_label = QLabel("(Upload)")
            upload_label.setStyleSheet("color: #95a5a6; font-size: 11px;")
            layout.addWidget(upload_label)

        # Styling
        wajib = self.dokumen.get('wajib', False)
        self.setStyleSheet(f"""
            DokumenCheckItem {{
                background-color: {'#fef9e7' if wajib else '#ffffff'};
                border: 1px solid {'#f39c12' if wajib else '#ecf0f1'};
                border-radius: 5px;
            }}
        """)

    def is_checked(self) -> bool:
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        self.checkbox.setChecked(checked)


class PerjalananDinasDialog(QDialog):
    """
    Dialog untuk membuat dokumen perjalanan dinas lengkap.

    Features:
    - Form info perjalanan dinas
    - Kalkulasi biaya otomatis
    - Checklist dokumen yang diperlukan
    - Generate batch templates
    """

    documents_generated = Signal(list)  # list of generated file paths

    def __init__(self, transaksi: Dict[str, Any] = None,
                 satker: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        self.transaksi = transaksi or {}
        self.satker = satker or {}
        self.doc_items: Dict[str, DokumenCheckItem] = {}
        self.generated_files: List[str] = []

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setWindowTitle("Perjalanan Dinas - Persiapan Dokumen")
        self.setMinimumSize(900, 700)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header
        header = QLabel("Persiapan Dokumen Perjalanan Dinas")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        layout.addWidget(header)

        # Main content with tabs
        tabs = QTabWidget()

        # Tab 1: Info Perjalanan
        info_tab = self._create_info_tab()
        tabs.addTab(info_tab, "1. Info Perjalanan")

        # Tab 2: Perhitungan Biaya
        biaya_tab = self._create_biaya_tab()
        tabs.addTab(biaya_tab, "2. Perhitungan Biaya")

        # Tab 3: Checklist Dokumen
        checklist_tab = self._create_checklist_tab()
        tabs.addTab(checklist_tab, "3. Checklist Dokumen")

        layout.addWidget(tabs)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(self.status_label)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # Generate semua dokumen
        self.generate_all_btn = QPushButton("Generate Semua Dokumen Terpilih")
        self.generate_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #1e8449; }
        """)
        self.generate_all_btn.clicked.connect(self._generate_all)
        btn_layout.addWidget(self.generate_all_btn)

        # Buka folder
        self.open_folder_btn = QPushButton("Buka Folder")
        self.open_folder_btn.setVisible(False)
        self.open_folder_btn.clicked.connect(self._open_folder)
        btn_layout.addWidget(self.open_folder_btn)

        # Tutup
        close_btn = QPushButton("Tutup")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _create_info_tab(self) -> QWidget:
        """Create info perjalanan tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # Pelaksana info
        pelaksana_group = QGroupBox("Data Pelaksana")
        pelaksana_layout = QGridLayout(pelaksana_group)
        pelaksana_layout.setSpacing(10)

        pelaksana_layout.addWidget(QLabel("Nama:"), 0, 0)
        self.nama_edit = QLineEdit()
        self.nama_edit.setText(self.transaksi.get('penerima_nama', ''))
        pelaksana_layout.addWidget(self.nama_edit, 0, 1)

        pelaksana_layout.addWidget(QLabel("NIP:"), 0, 2)
        self.nip_edit = QLineEdit()
        self.nip_edit.setText(self.transaksi.get('penerima_nip', ''))
        pelaksana_layout.addWidget(self.nip_edit, 0, 3)

        pelaksana_layout.addWidget(QLabel("Pangkat/Golongan:"), 1, 0)
        self.pangkat_edit = QLineEdit()
        pelaksana_layout.addWidget(self.pangkat_edit, 1, 1)

        pelaksana_layout.addWidget(QLabel("Jabatan:"), 1, 2)
        self.jabatan_edit = QLineEdit()
        self.jabatan_edit.setText(self.transaksi.get('penerima_jabatan', ''))
        pelaksana_layout.addWidget(self.jabatan_edit, 1, 3)

        layout.addWidget(pelaksana_group)

        # Perjalanan info
        perjalanan_group = QGroupBox("Data Perjalanan")
        perjalanan_layout = QGridLayout(perjalanan_group)
        perjalanan_layout.setSpacing(10)

        perjalanan_layout.addWidget(QLabel("Kota Asal:"), 0, 0)
        self.kota_asal_edit = QLineEdit()
        self.kota_asal_edit.setText(self.satker.get('kota', 'Jakarta'))
        perjalanan_layout.addWidget(self.kota_asal_edit, 0, 1)

        perjalanan_layout.addWidget(QLabel("Kota Tujuan:"), 0, 2)
        self.kota_tujuan_edit = QLineEdit()
        perjalanan_layout.addWidget(self.kota_tujuan_edit, 0, 3)

        perjalanan_layout.addWidget(QLabel("Tanggal Berangkat:"), 1, 0)
        self.tgl_berangkat = QDateEdit()
        self.tgl_berangkat.setDate(QDate.currentDate())
        self.tgl_berangkat.setCalendarPopup(True)
        perjalanan_layout.addWidget(self.tgl_berangkat, 1, 1)

        perjalanan_layout.addWidget(QLabel("Tanggal Kembali:"), 1, 2)
        self.tgl_kembali = QDateEdit()
        self.tgl_kembali.setDate(QDate.currentDate().addDays(1))
        self.tgl_kembali.setCalendarPopup(True)
        perjalanan_layout.addWidget(self.tgl_kembali, 1, 3)

        perjalanan_layout.addWidget(QLabel("Maksud Perjalanan:"), 2, 0)
        self.maksud_edit = QLineEdit()
        self.maksud_edit.setText(self.transaksi.get('nama_kegiatan', ''))
        perjalanan_layout.addWidget(self.maksud_edit, 2, 1, 1, 3)

        perjalanan_layout.addWidget(QLabel("Alat Angkut:"), 3, 0)
        self.alat_angkut_combo = QComboBox()
        self.alat_angkut_combo.addItems([
            "Pesawat Udara", "Kereta Api", "Bus/Travel",
            "Kendaraan Dinas", "Kendaraan Pribadi"
        ])
        perjalanan_layout.addWidget(self.alat_angkut_combo, 3, 1)

        perjalanan_layout.addWidget(QLabel("Tingkat Biaya:"), 3, 2)
        self.tingkat_combo = QComboBox()
        self.tingkat_combo.addItems(["Eselon I", "Eselon II", "Eselon III", "Eselon IV", "Staf"])
        self.tingkat_combo.setCurrentIndex(4)
        perjalanan_layout.addWidget(self.tingkat_combo, 3, 3)

        layout.addWidget(perjalanan_group)

        # Dasar/Surat Tugas
        dasar_group = QGroupBox("Dasar Perjalanan")
        dasar_layout = QGridLayout(dasar_group)
        dasar_layout.setSpacing(10)

        dasar_layout.addWidget(QLabel("Nomor Surat Tugas:"), 0, 0)
        self.no_st_edit = QLineEdit()
        dasar_layout.addWidget(self.no_st_edit, 0, 1)

        dasar_layout.addWidget(QLabel("Tanggal ST:"), 0, 2)
        self.tgl_st = QDateEdit()
        self.tgl_st.setDate(QDate.currentDate())
        self.tgl_st.setCalendarPopup(True)
        dasar_layout.addWidget(self.tgl_st, 0, 3)

        dasar_layout.addWidget(QLabel("Nomor SPPD:"), 1, 0)
        self.no_sppd_edit = QLineEdit()
        dasar_layout.addWidget(self.no_sppd_edit, 1, 1)

        layout.addWidget(dasar_group)

        layout.addStretch()
        return widget

    def _create_biaya_tab(self) -> QWidget:
        """Create biaya calculation tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Import BiayaPerjalananWidget
        from ..components.biaya_perjalanan_widget import BiayaPerjalananWidget

        self.biaya_widget = BiayaPerjalananWidget()
        layout.addWidget(self.biaya_widget)

        return widget

    def _create_checklist_tab(self) -> QWidget:
        """Create document checklist tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Info
        info = QLabel(
            "Centang dokumen yang akan di-generate. Dokumen bertanda kuning adalah dokumen wajib.\n"
            "Dokumen 'Persiapan' diberikan kepada pelaksana sebelum berangkat.\n"
            "Dokumen 'Pertanggungjawaban' diisi setelah perjalanan selesai."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #7f8c8d; padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
        layout.addWidget(info)

        # Quick actions
        action_layout = QHBoxLayout()

        select_all_btn = QPushButton("Pilih Semua")
        select_all_btn.clicked.connect(lambda: self._set_all_checked(True))
        action_layout.addWidget(select_all_btn)

        select_none_btn = QPushButton("Hapus Semua")
        select_none_btn.clicked.connect(lambda: self._set_all_checked(False))
        action_layout.addWidget(select_none_btn)

        select_wajib_btn = QPushButton("Pilih Wajib Saja")
        select_wajib_btn.clicked.connect(self._select_wajib_only)
        action_layout.addWidget(select_wajib_btn)

        action_layout.addStretch()

        # Count label
        self.count_label = QLabel("0 dokumen dipilih")
        self.count_label.setStyleSheet("color: #3498db; font-weight: bold;")
        action_layout.addWidget(self.count_label)

        layout.addLayout(action_layout)

        # Scroll area for checklist
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)

        # Group by kategori
        kategori_order = ['persiapan', 'pertanggungjawaban', 'bukti']
        kategori_labels = {
            'persiapan': 'Dokumen Persiapan (Sebelum Berangkat)',
            'pertanggungjawaban': 'Dokumen Pertanggungjawaban (Setelah Pulang)',
            'bukti': 'Bukti Pendukung (Upload)',
        }

        for kategori in kategori_order:
            # Section header
            header = QLabel(kategori_labels.get(kategori, kategori))
            header.setStyleSheet("""
                font-weight: bold;
                color: #2c3e50;
                padding: 10px 0 5px 0;
                border-bottom: 2px solid #3498db;
            """)
            scroll_layout.addWidget(header)

            # Add documents for this category
            for dok in DOKUMEN_PERJALANAN_DINAS:
                if dok.get('kategori') == kategori:
                    item = DokumenCheckItem(dok)
                    item.toggled.connect(self._on_item_toggled)
                    item.generate_clicked.connect(self._generate_single)
                    self.doc_items[dok['kode']] = item
                    scroll_layout.addWidget(item)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        self._update_count()

        return widget

    def _load_data(self):
        """Load initial data."""
        pass

    def _set_all_checked(self, checked: bool):
        """Set all items checked or unchecked."""
        for item in self.doc_items.values():
            item.set_checked(checked)
        self._update_count()

    def _select_wajib_only(self):
        """Select only wajib documents."""
        for kode, item in self.doc_items.items():
            dok = next((d for d in DOKUMEN_PERJALANAN_DINAS if d['kode'] == kode), None)
            if dok:
                item.set_checked(dok.get('wajib', False))
        self._update_count()

    def _on_item_toggled(self, kode: str, checked: bool):
        """Handle item toggle."""
        self._update_count()

    def _update_count(self):
        """Update selected count label."""
        count = sum(1 for item in self.doc_items.values() if item.is_checked())
        self.count_label.setText(f"{count} dokumen dipilih")

    def _collect_data(self) -> Dict[str, Any]:
        """Collect all form data."""
        biaya_data = self.biaya_widget.get_data()

        return {
            # Pelaksana
            'pelaksana_nama': self.nama_edit.text(),
            'pelaksana_nip': self.nip_edit.text(),
            'pelaksana_pangkat': self.pangkat_edit.text(),
            'pelaksana_jabatan': self.jabatan_edit.text(),
            'penerima_nama': self.nama_edit.text(),
            'penerima_nip': self.nip_edit.text(),

            # Perjalanan
            'kota_asal': self.kota_asal_edit.text(),
            'kota_tujuan': self.kota_tujuan_edit.text(),
            'tanggal_berangkat': self.tgl_berangkat.date().toString("yyyy-MM-dd"),
            'tanggal_kembali': self.tgl_kembali.date().toString("yyyy-MM-dd"),
            'maksud_perjalanan': self.maksud_edit.text(),
            'alat_angkut': self.alat_angkut_combo.currentText(),
            'tingkat_biaya': self.tingkat_combo.currentText(),

            # Dasar
            'nomor_surat_tugas': self.no_st_edit.text(),
            'tanggal_surat_tugas': self.tgl_st.date().toString("yyyy-MM-dd"),
            'nomor_sppd': self.no_sppd_edit.text(),

            # Satker
            'satker_nama': self.satker.get('nama', ''),
            'satker_kode': self.satker.get('kode', ''),
            'satker_kota': self.satker.get('kota', ''),
            'kementerian': self.satker.get('kementerian', ''),
            'ppk_nama': self.satker.get('ppk_nama', ''),
            'ppk_nip': self.satker.get('ppk_nip', ''),
            'bendahara_nama': self.satker.get('bendahara_nama', ''),
            'bendahara_nip': self.satker.get('bendahara_nip', ''),

            # Biaya
            **biaya_data,
            'uang_muka': biaya_data.get('total', 0),
            'rincian_items': self.biaya_widget.get_rincian_items(),
        }

    def _generate_single(self, kode: str):
        """Generate single document."""
        dok = next((d for d in DOKUMEN_PERJALANAN_DINAS if d['kode'] == kode), None)
        if not dok or not dok.get('template'):
            QMessageBox.warning(self, "Info", "Dokumen ini tidak memiliki template (perlu upload)")
            return

        try:
            from app.services.dokumen_generator import get_dokumen_generator

            generator = get_dokumen_generator()
            data = self._collect_data()

            # Merge dengan transaksi data
            merged_data = {**self.transaksi, **data}

            output_path, error = generator.generate_document(
                transaksi=merged_data,
                kode_dokumen=kode,
                template_name=dok['template'],
                satker=self.satker,
                rincian=data.get('rincian_items'),
                additional_data=data
            )

            if error:
                QMessageBox.critical(self, "Error", f"Gagal generate {dok['nama']}:\n{error}")
            else:
                self.generated_files.append(output_path)
                QMessageBox.information(
                    self, "Sukses",
                    f"{dok['nama']} berhasil dibuat:\n{output_path}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal generate dokumen:\n{str(e)}")

    def _generate_all(self):
        """Generate all selected documents."""
        selected = [(kode, item) for kode, item in self.doc_items.items() if item.is_checked()]

        if not selected:
            QMessageBox.warning(self, "Peringatan", "Pilih minimal satu dokumen untuk di-generate")
            return

        # Filter only documents with templates
        to_generate = []
        for kode, item in selected:
            dok = next((d for d in DOKUMEN_PERJALANAN_DINAS if d['kode'] == kode), None)
            if dok and dok.get('template'):
                to_generate.append(dok)

        if not to_generate:
            QMessageBox.warning(self, "Info", "Tidak ada dokumen dengan template yang dipilih")
            return

        # Confirm
        reply = QMessageBox.question(
            self, "Konfirmasi",
            f"Akan generate {len(to_generate)} dokumen. Lanjutkan?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(to_generate))
        self.progress_bar.setValue(0)
        self.generate_all_btn.setEnabled(False)

        try:
            from app.services.dokumen_generator import get_dokumen_generator

            generator = get_dokumen_generator()
            data = self._collect_data()
            merged_data = {**self.transaksi, **data}

            success_count = 0
            errors = []

            for i, dok in enumerate(to_generate):
                self.status_label.setText(f"Generating {dok['nama']}...")
                self.progress_bar.setValue(i + 1)

                # Process events to update UI
                from PySide6.QtWidgets import QApplication
                QApplication.processEvents()

                output_path, error = generator.generate_document(
                    transaksi=merged_data,
                    kode_dokumen=dok['kode'],
                    template_name=dok['template'],
                    satker=self.satker,
                    rincian=data.get('rincian_items'),
                    additional_data=data
                )

                if error:
                    errors.append(f"{dok['nama']}: {error}")
                else:
                    self.generated_files.append(output_path)
                    success_count += 1

            self.progress_bar.setValue(len(to_generate))

            # Show result
            if errors:
                msg = f"Berhasil: {success_count} dokumen\n\nGagal:\n" + "\n".join(errors)
                QMessageBox.warning(self, "Hasil", msg)
            else:
                self.status_label.setText(f"✓ {success_count} dokumen berhasil dibuat")
                self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                self.open_folder_btn.setVisible(True)

                QMessageBox.information(
                    self, "Sukses",
                    f"Semua {success_count} dokumen berhasil dibuat!\n\n"
                    "Dokumen Persiapan dapat diberikan kepada pelaksana sebelum berangkat.\n"
                    "Dokumen Pertanggungjawaban diisi setelah perjalanan selesai."
                )

            self.documents_generated.emit(self.generated_files)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan:\n{str(e)}")

        finally:
            self.generate_all_btn.setEnabled(True)
            self.progress_bar.setVisible(False)

    def _open_folder(self):
        """Open output folder."""
        if self.generated_files:
            import subprocess
            import platform
            import os
            from pathlib import Path

            folder = str(Path(self.generated_files[0]).parent)

            try:
                if platform.system() == 'Windows':
                    os.startfile(folder)
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', folder])
                else:
                    subprocess.run(['xdg-open', folder])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal membuka folder:\n{str(e)}")
