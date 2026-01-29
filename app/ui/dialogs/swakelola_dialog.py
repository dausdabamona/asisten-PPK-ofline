"""
PPK DOCUMENT FACTORY - Swakelola Dialog
========================================
Dialog untuk membuat dokumen kegiatan swakelola lengkap.
Termasuk checklist dokumen dan generate batch templates.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QGroupBox, QCheckBox,
    QScrollArea, QWidget, QMessageBox, QProgressBar,
    QTabWidget, QLineEdit, QDateEdit, QComboBox, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont

from typing import Dict, Any, List, Optional
from datetime import datetime


# Daftar dokumen swakelola berdasarkan jenis kegiatan
DOKUMEN_SWAKELOLA = {
    "KEPANITIAAN": [
        {
            "kode": "ND_REQ",
            "nama": "Nota Dinas Permintaan",
            "template": "nota_dinas_pp.docx",
            "kategori": "persiapan",
            "wajib": True,
            "deskripsi": "Nota dinas permohonan pencairan dana kegiatan"
        },
        {
            "kode": "SK_KPA",
            "nama": "SK Penetapan Panitia",
            "template": "sk_kpa.docx",
            "kategori": "persiapan",
            "wajib": True,
            "deskripsi": "SK Penetapan kepanitiaan dari KPA"
        },
        {
            "kode": "TOR",
            "nama": "TOR/KAK",
            "template": "kak.docx",
            "kategori": "persiapan",
            "wajib": True,
            "deskripsi": "Kerangka Acuan Kerja kegiatan"
        },
        {
            "kode": "RAB",
            "nama": "RAB Kegiatan",
            "template": "rab_swakelola.xlsx",
            "kategori": "persiapan",
            "wajib": True,
            "deskripsi": "Rencana Anggaran Biaya kegiatan"
        },
        {
            "kode": "UNDANGAN",
            "nama": "Undangan",
            "template": "undangan_pl.docx",
            "kategori": "persiapan",
            "wajib": False,
            "deskripsi": "Surat undangan kegiatan"
        },
        {
            "kode": "KUITANSI_UM",
            "nama": "Kuitansi Uang Muka",
            "template": "kuitansi_uang_muka.docx",
            "kategori": "persiapan",
            "wajib": True,
            "deskripsi": "Kuitansi pengambilan uang muka kegiatan"
        },
        {
            "kode": "DAFTAR_HADIR",
            "nama": "Daftar Hadir",
            "template": "daftar_hadir_swakelola.docx",
            "kategori": "pelaksanaan",
            "wajib": True,
            "deskripsi": "Daftar hadir peserta kegiatan (diisi saat pelaksanaan)"
        },
        {
            "kode": "NOTULEN",
            "nama": "Notulen",
            "template": "notulen.docx",
            "kategori": "pelaksanaan",
            "wajib": False,
            "deskripsi": "Notulen/catatan hasil kegiatan"
        },
        {
            "kode": "DOKUMENTASI",
            "nama": "Dokumentasi Kegiatan",
            "template": None,
            "kategori": "pelaksanaan",
            "wajib": True,
            "deskripsi": "Foto-foto dokumentasi kegiatan (upload)"
        },
        {
            "kode": "LAPORAN",
            "nama": "Laporan Kegiatan",
            "template": "laporan_kegiatan.docx",
            "kategori": "pertanggungjawaban",
            "wajib": True,
            "deskripsi": "Laporan pelaksanaan kegiatan"
        },
        {
            "kode": "PENGELUARAN",
            "nama": "Daftar Pengeluaran",
            "template": "daftar_pengeluaran_riil.docx",
            "kategori": "pertanggungjawaban",
            "wajib": True,
            "deskripsi": "Daftar pengeluaran riil kegiatan"
        },
        {
            "kode": "KUITANSI_RAMPUNG",
            "nama": "Kuitansi Rampung",
            "template": "kuitansi_rampung.docx",
            "kategori": "pertanggungjawaban",
            "wajib": True,
            "deskripsi": "Kuitansi pertanggungjawaban akhir"
        },
    ],
    "RAPAT": [
        {
            "kode": "ND_REQ",
            "nama": "Nota Dinas Permintaan",
            "template": "nota_dinas_pp.docx",
            "kategori": "persiapan",
            "wajib": True,
            "deskripsi": "Nota dinas permohonan pencairan dana rapat"
        },
        {
            "kode": "UNDANGAN",
            "nama": "Undangan Rapat",
            "template": "undangan_pl.docx",
            "kategori": "persiapan",
            "wajib": True,
            "deskripsi": "Surat undangan rapat"
        },
        {
            "kode": "TOR",
            "nama": "TOR/KAK Rapat",
            "template": "kak.docx",
            "kategori": "persiapan",
            "wajib": False,
            "deskripsi": "Kerangka Acuan Kerja rapat (jika diperlukan)"
        },
        {
            "kode": "KUITANSI_UM",
            "nama": "Kuitansi Uang Muka",
            "template": "kuitansi_uang_muka.docx",
            "kategori": "persiapan",
            "wajib": True,
            "deskripsi": "Kuitansi pengambilan uang muka"
        },
        {
            "kode": "DAFTAR_HADIR",
            "nama": "Daftar Hadir Rapat",
            "template": "daftar_hadir_swakelola.docx",
            "kategori": "pelaksanaan",
            "wajib": True,
            "deskripsi": "Daftar hadir peserta rapat"
        },
        {
            "kode": "NOTULEN",
            "nama": "Notulen Rapat",
            "template": "notulen.docx",
            "kategori": "pelaksanaan",
            "wajib": True,
            "deskripsi": "Catatan hasil rapat"
        },
        {
            "kode": "DOKUMENTASI",
            "nama": "Dokumentasi Rapat",
            "template": None,
            "kategori": "pelaksanaan",
            "wajib": True,
            "deskripsi": "Foto-foto rapat (upload)"
        },
        {
            "kode": "PENGELUARAN",
            "nama": "Daftar Pengeluaran",
            "template": "daftar_pengeluaran_riil.docx",
            "kategori": "pertanggungjawaban",
            "wajib": True,
            "deskripsi": "Daftar pengeluaran riil"
        },
        {
            "kode": "KUITANSI_RAMPUNG",
            "nama": "Kuitansi Rampung",
            "template": "kuitansi_rampung.docx",
            "kategori": "pertanggungjawaban",
            "wajib": True,
            "deskripsi": "Kuitansi pertanggungjawaban"
        },
    ],
    "JAMUAN_TAMU": [
        {
            "kode": "ND_REQ",
            "nama": "Nota Dinas Permintaan",
            "template": "nota_dinas_pp.docx",
            "kategori": "persiapan",
            "wajib": True,
            "deskripsi": "Nota dinas permohonan jamuan tamu"
        },
        {
            "kode": "UNDANGAN",
            "nama": "Undangan/Jadwal",
            "template": "undangan_pl.docx",
            "kategori": "persiapan",
            "wajib": False,
            "deskripsi": "Undangan atau jadwal kunjungan tamu"
        },
        {
            "kode": "KUITANSI_UM",
            "nama": "Kuitansi Uang Muka",
            "template": "kuitansi_uang_muka.docx",
            "kategori": "persiapan",
            "wajib": True,
            "deskripsi": "Kuitansi pengambilan uang muka"
        },
        {
            "kode": "DAFTAR_HADIR",
            "nama": "Daftar Hadir",
            "template": "daftar_hadir_swakelola.docx",
            "kategori": "pelaksanaan",
            "wajib": True,
            "deskripsi": "Daftar hadir tamu"
        },
        {
            "kode": "DOKUMENTASI",
            "nama": "Dokumentasi",
            "template": None,
            "kategori": "pelaksanaan",
            "wajib": True,
            "deskripsi": "Foto dokumentasi jamuan (upload)"
        },
        {
            "kode": "LAPORAN",
            "nama": "Laporan Jamuan",
            "template": "laporan_kegiatan.docx",
            "kategori": "pertanggungjawaban",
            "wajib": False,
            "deskripsi": "Laporan pelaksanaan jamuan"
        },
        {
            "kode": "PENGELUARAN",
            "nama": "Daftar Pengeluaran",
            "template": "daftar_pengeluaran_riil.docx",
            "kategori": "pertanggungjawaban",
            "wajib": True,
            "deskripsi": "Daftar pengeluaran riil"
        },
        {
            "kode": "KUITANSI_RAMPUNG",
            "nama": "Kuitansi Rampung",
            "template": "kuitansi_rampung.docx",
            "kategori": "pertanggungjawaban",
            "wajib": True,
            "deskripsi": "Kuitansi pertanggungjawaban"
        },
    ],
    "OPERASIONAL": [
        {
            "kode": "LBR_REQ",
            "nama": "Lembar Permintaan",
            "template": "lembar_permintaan.docx",
            "kategori": "persiapan",
            "wajib": True,
            "deskripsi": "Lembar permintaan pencairan dana"
        },
        {
            "kode": "KUITANSI_UM",
            "nama": "Kuitansi Uang Muka",
            "template": "kuitansi_uang_muka.docx",
            "kategori": "persiapan",
            "wajib": True,
            "deskripsi": "Kuitansi pengambilan uang muka"
        },
        {
            "kode": "BUKTI_PEMBELIAN",
            "nama": "Bukti Pembelian",
            "template": None,
            "kategori": "pelaksanaan",
            "wajib": True,
            "deskripsi": "Kuitansi/nota pembelian (upload)"
        },
        {
            "kode": "PENGELUARAN",
            "nama": "Daftar Pengeluaran",
            "template": "daftar_pengeluaran_riil.docx",
            "kategori": "pertanggungjawaban",
            "wajib": True,
            "deskripsi": "Daftar pengeluaran riil"
        },
        {
            "kode": "KUITANSI_RAMPUNG",
            "nama": "Kuitansi Rampung",
            "template": "kuitansi_rampung.docx",
            "kategori": "pertanggungjawaban",
            "wajib": True,
            "deskripsi": "Kuitansi pertanggungjawaban"
        },
    ],
}


class SwakelolaDocItem(QFrame):
    """Widget untuk satu item dokumen dalam checklist."""

    toggled = Signal(str, bool)
    generate_clicked = Signal(str)

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

        # Badge
        kategori = self.dokumen.get('kategori', '')
        colors = {
            'persiapan': '#3498db',
            'pelaksanaan': '#27ae60',
            'pertanggungjawaban': '#9b59b6',
        }
        badge = QLabel(kategori.upper())
        badge.setStyleSheet(f"""
            background-color: {colors.get(kategori, '#95a5a6')};
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10px;
        """)
        layout.addWidget(badge)

        # Button
        if self.dokumen.get('template'):
            btn = QPushButton("Template")
            btn.setFixedWidth(70)
            btn.setStyleSheet("""
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
            btn.clicked.connect(lambda: self.generate_clicked.emit(self.dokumen['kode']))
            layout.addWidget(btn)
        else:
            lbl = QLabel("(Upload)")
            lbl.setStyleSheet("color: #95a5a6; font-size: 11px;")
            layout.addWidget(lbl)

        wajib = self.dokumen.get('wajib', False)
        self.setStyleSheet(f"""
            SwakelolaDocItem {{
                background-color: {'#fef9e7' if wajib else '#ffffff'};
                border: 1px solid {'#f39c12' if wajib else '#ecf0f1'};
                border-radius: 5px;
            }}
        """)

    def is_checked(self) -> bool:
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        self.checkbox.setChecked(checked)


class SwakelolaDialog(QDialog):
    """
    Dialog untuk membuat dokumen kegiatan swakelola lengkap.
    """

    documents_generated = Signal(list)

    def __init__(self, transaksi: Dict[str, Any] = None,
                 satker: Dict[str, Any] = None,
                 jenis_kegiatan: str = "KEPANITIAAN",
                 parent=None):
        super().__init__(parent)
        self.transaksi = transaksi or {}
        self.satker = satker or {}
        self.jenis_kegiatan = jenis_kegiatan
        self.doc_items: Dict[str, SwakelolaDocItem] = {}
        self.generated_files: List[str] = []

        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(f"Dokumen Kegiatan Swakelola - {self.jenis_kegiatan}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header
        header = QLabel(f"Persiapan Dokumen Kegiatan: {self.jenis_kegiatan}")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        layout.addWidget(header)

        # Tabs
        tabs = QTabWidget()

        # Tab 1: Info Kegiatan
        info_tab = self._create_info_tab()
        tabs.addTab(info_tab, "1. Info Kegiatan")

        # Tab 2: Rincian Biaya
        biaya_tab = self._create_biaya_tab()
        tabs.addTab(biaya_tab, "2. Rincian Biaya")

        # Tab 3: Checklist
        checklist_tab = self._create_checklist_tab()
        tabs.addTab(checklist_tab, "3. Checklist Dokumen")

        layout.addWidget(tabs)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.generate_all_btn = QPushButton("Generate Semua Dokumen Terpilih")
        self.generate_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1e8449; }
        """)
        self.generate_all_btn.clicked.connect(self._generate_all)
        btn_layout.addWidget(self.generate_all_btn)

        self.open_folder_btn = QPushButton("Buka Folder")
        self.open_folder_btn.setVisible(False)
        self.open_folder_btn.clicked.connect(self._open_folder)
        btn_layout.addWidget(self.open_folder_btn)

        close_btn = QPushButton("Tutup")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _create_info_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Kegiatan info
        group = QGroupBox("Informasi Kegiatan")
        grid = QGridLayout(group)
        grid.setSpacing(10)

        grid.addWidget(QLabel("Nama Kegiatan:"), 0, 0)
        self.nama_kegiatan_edit = QLineEdit()
        self.nama_kegiatan_edit.setText(self.transaksi.get('nama_kegiatan', ''))
        grid.addWidget(self.nama_kegiatan_edit, 0, 1, 1, 3)

        grid.addWidget(QLabel("Tanggal Pelaksanaan:"), 1, 0)
        self.tgl_mulai = QDateEdit()
        self.tgl_mulai.setDate(QDate.currentDate())
        self.tgl_mulai.setCalendarPopup(True)
        grid.addWidget(self.tgl_mulai, 1, 1)

        grid.addWidget(QLabel("s/d:"), 1, 2)
        self.tgl_selesai = QDateEdit()
        self.tgl_selesai.setDate(QDate.currentDate())
        self.tgl_selesai.setCalendarPopup(True)
        grid.addWidget(self.tgl_selesai, 1, 3)

        grid.addWidget(QLabel("Tempat:"), 2, 0)
        self.tempat_edit = QLineEdit()
        grid.addWidget(self.tempat_edit, 2, 1, 1, 3)

        grid.addWidget(QLabel("Penanggung Jawab:"), 3, 0)
        self.pj_edit = QLineEdit()
        self.pj_edit.setText(self.transaksi.get('penerima_nama', ''))
        grid.addWidget(self.pj_edit, 3, 1)

        grid.addWidget(QLabel("NIP:"), 3, 2)
        self.pj_nip_edit = QLineEdit()
        self.pj_nip_edit.setText(self.transaksi.get('penerima_nip', ''))
        grid.addWidget(self.pj_nip_edit, 3, 3)

        layout.addWidget(group)

        # Dasar
        dasar_group = QGroupBox("Dasar Kegiatan")
        dasar_layout = QGridLayout(dasar_group)

        dasar_layout.addWidget(QLabel("Nomor SK/Surat:"), 0, 0)
        self.no_sk_edit = QLineEdit()
        dasar_layout.addWidget(self.no_sk_edit, 0, 1)

        dasar_layout.addWidget(QLabel("Tanggal:"), 0, 2)
        self.tgl_sk = QDateEdit()
        self.tgl_sk.setDate(QDate.currentDate())
        self.tgl_sk.setCalendarPopup(True)
        dasar_layout.addWidget(self.tgl_sk, 0, 3)

        layout.addWidget(dasar_group)

        layout.addStretch()
        return widget

    def _create_biaya_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        from ..components.rincian_kalkulasi_widget import RincianKalkulasiWidget

        self.rincian_widget = RincianKalkulasiWidget(title="Rincian Biaya Kegiatan")
        layout.addWidget(self.rincian_widget)

        return widget

    def _create_checklist_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "Centang dokumen yang akan di-generate. Dokumen kuning adalah wajib.\n"
            "Dokumen 'Persiapan' diberikan sebelum kegiatan.\n"
            "Dokumen 'Pelaksanaan' diisi saat kegiatan.\n"
            "Dokumen 'Pertanggungjawaban' diisi setelah kegiatan selesai."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #7f8c8d; padding: 10px; background: #f8f9fa; border-radius: 5px;")
        layout.addWidget(info)

        # Actions
        action_layout = QHBoxLayout()

        select_all = QPushButton("Pilih Semua")
        select_all.clicked.connect(lambda: self._set_all_checked(True))
        action_layout.addWidget(select_all)

        select_none = QPushButton("Hapus Semua")
        select_none.clicked.connect(lambda: self._set_all_checked(False))
        action_layout.addWidget(select_none)

        select_wajib = QPushButton("Pilih Wajib")
        select_wajib.clicked.connect(self._select_wajib)
        action_layout.addWidget(select_wajib)

        action_layout.addStretch()

        self.count_label = QLabel("0 dokumen dipilih")
        self.count_label.setStyleSheet("color: #3498db; font-weight: bold;")
        action_layout.addWidget(self.count_label)

        layout.addLayout(action_layout)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Get documents for this jenis_kegiatan
        docs = DOKUMEN_SWAKELOLA.get(self.jenis_kegiatan, [])

        kategori_order = ['persiapan', 'pelaksanaan', 'pertanggungjawaban']
        kategori_labels = {
            'persiapan': 'Dokumen Persiapan (Sebelum Kegiatan)',
            'pelaksanaan': 'Dokumen Pelaksanaan (Saat Kegiatan)',
            'pertanggungjawaban': 'Dokumen Pertanggungjawaban (Setelah Kegiatan)',
        }

        for kategori in kategori_order:
            header = QLabel(kategori_labels.get(kategori, kategori))
            header.setStyleSheet("""
                font-weight: bold;
                color: #2c3e50;
                padding: 10px 0 5px 0;
                border-bottom: 2px solid #3498db;
            """)
            scroll_layout.addWidget(header)

            for dok in docs:
                if dok.get('kategori') == kategori:
                    item = SwakelolaDocItem(dok)
                    item.toggled.connect(self._on_toggled)
                    item.generate_clicked.connect(self._generate_single)
                    self.doc_items[dok['kode']] = item
                    scroll_layout.addWidget(item)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        self._update_count()

        return widget

    def _set_all_checked(self, checked: bool):
        for item in self.doc_items.values():
            item.set_checked(checked)
        self._update_count()

    def _select_wajib(self):
        docs = DOKUMEN_SWAKELOLA.get(self.jenis_kegiatan, [])
        for kode, item in self.doc_items.items():
            dok = next((d for d in docs if d['kode'] == kode), None)
            if dok:
                item.set_checked(dok.get('wajib', False))
        self._update_count()

    def _on_toggled(self, kode: str, checked: bool):
        self._update_count()

    def _update_count(self):
        count = sum(1 for item in self.doc_items.values() if item.is_checked())
        self.count_label.setText(f"{count} dokumen dipilih")

    def _collect_data(self) -> Dict[str, Any]:
        return {
            'nama_kegiatan': self.nama_kegiatan_edit.text(),
            'tanggal_mulai': self.tgl_mulai.date().toString("yyyy-MM-dd"),
            'tanggal_selesai': self.tgl_selesai.date().toString("yyyy-MM-dd"),
            'tempat_kegiatan': self.tempat_edit.text(),
            'penerima_nama': self.pj_edit.text(),
            'penerima_nip': self.pj_nip_edit.text(),
            'nomor_sk': self.no_sk_edit.text(),
            'tanggal_sk': self.tgl_sk.date().toString("yyyy-MM-dd"),
            'satker_nama': self.satker.get('nama', ''),
            'satker_kota': self.satker.get('kota', ''),
            'kementerian': self.satker.get('kementerian', ''),
            'ppk_nama': self.satker.get('ppk_nama', ''),
            'ppk_nip': self.satker.get('ppk_nip', ''),
            'bendahara_nama': self.satker.get('bendahara_nama', ''),
            'bendahara_nip': self.satker.get('bendahara_nip', ''),
            'rincian_items': self.rincian_widget.get_items(),
            'total': self.rincian_widget.get_total(),
            'uang_muka': self.rincian_widget.get_total(),
        }

    def _generate_single(self, kode: str):
        docs = DOKUMEN_SWAKELOLA.get(self.jenis_kegiatan, [])
        dok = next((d for d in docs if d['kode'] == kode), None)
        if not dok or not dok.get('template'):
            QMessageBox.warning(self, "Info", "Dokumen ini tidak memiliki template")
            return

        try:
            from app.services.dokumen_generator import get_dokumen_generator

            generator = get_dokumen_generator()
            data = self._collect_data()
            merged = {**self.transaksi, **data}

            output, error = generator.generate_document(
                transaksi=merged,
                kode_dokumen=kode,
                template_name=dok['template'],
                satker=self.satker,
                rincian=data.get('rincian_items'),
                additional_data=data
            )

            if error:
                QMessageBox.critical(self, "Error", f"Gagal: {error}")
            else:
                self.generated_files.append(output)
                QMessageBox.information(self, "Sukses", f"Berhasil:\n{output}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _generate_all(self):
        docs = DOKUMEN_SWAKELOLA.get(self.jenis_kegiatan, [])
        selected = [(k, i) for k, i in self.doc_items.items() if i.is_checked()]

        if not selected:
            QMessageBox.warning(self, "Peringatan", "Pilih minimal satu dokumen")
            return

        to_generate = []
        for kode, item in selected:
            dok = next((d for d in docs if d['kode'] == kode), None)
            if dok and dok.get('template'):
                to_generate.append(dok)

        if not to_generate:
            QMessageBox.warning(self, "Info", "Tidak ada dokumen dengan template")
            return

        reply = QMessageBox.question(
            self, "Konfirmasi",
            f"Generate {len(to_generate)} dokumen?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(to_generate))
        self.generate_all_btn.setEnabled(False)

        try:
            from app.services.dokumen_generator import get_dokumen_generator

            generator = get_dokumen_generator()
            data = self._collect_data()
            merged = {**self.transaksi, **data}

            success = 0
            errors = []

            for i, dok in enumerate(to_generate):
                self.status_label.setText(f"Generating {dok['nama']}...")
                self.progress_bar.setValue(i + 1)

                from PySide6.QtWidgets import QApplication
                QApplication.processEvents()

                output, error = generator.generate_document(
                    transaksi=merged,
                    kode_dokumen=dok['kode'],
                    template_name=dok['template'],
                    satker=self.satker,
                    rincian=data.get('rincian_items'),
                    additional_data=data
                )

                if error:
                    errors.append(f"{dok['nama']}: {error}")
                else:
                    self.generated_files.append(output)
                    success += 1

            if errors:
                QMessageBox.warning(self, "Hasil", f"Berhasil: {success}\n\nGagal:\n" + "\n".join(errors))
            else:
                self.status_label.setText(f"✓ {success} dokumen berhasil")
                self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                self.open_folder_btn.setVisible(True)
                QMessageBox.information(
                    self, "Sukses",
                    f"{success} dokumen berhasil dibuat!\n\n"
                    "Dokumen Persiapan: Diberikan sebelum kegiatan\n"
                    "Dokumen Pelaksanaan: Diisi saat kegiatan\n"
                    "Dokumen Pertanggungjawaban: Diisi setelah selesai"
                )

            self.documents_generated.emit(self.generated_files)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

        finally:
            self.generate_all_btn.setEnabled(True)
            self.progress_bar.setVisible(False)

    def _open_folder(self):
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
                QMessageBox.critical(self, "Error", str(e))
