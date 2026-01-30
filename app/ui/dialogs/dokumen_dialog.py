"""
PPK DOCUMENT FACTORY - Dokumen Generation Dialog
=================================================
Dialog untuk generate dan preview dokumen dari template.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QLineEdit, QTextEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit,
    QGroupBox, QScrollArea, QWidget, QMessageBox,
    QFileDialog, QProgressBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont

from typing import Dict, Any, List, Optional
from datetime import datetime

# Import database for pegawai data
from ...core.database import get_db_manager


class DokumenGeneratorDialog(QDialog):
    """Dialog untuk generate dokumen dari template."""

    dokumen_generated = Signal(str)  # filepath

    def __init__(self, transaksi: Dict[str, Any], kode_dokumen: str,
                 template_name: str, nama_dokumen: str = None,
                 satker: Dict[str, Any] = None,
                 additional_data: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        self.transaksi = transaksi
        self.kode_dokumen = kode_dokumen
        self.nama_dokumen = nama_dokumen or kode_dokumen
        self.template_name = template_name
        self.satker = satker or {}
        self.additional_data = additional_data or {}
        self.rincian_items = self.additional_data.get('rincian_items', [])
        self.generated_path = None
        self.pegawai_list = []  # List of pegawai for dropdown

        self._setup_ui()
        self._load_pegawai()
        self._load_data()

    def _setup_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle(f"Buat Dokumen - {self.nama_dokumen}")
        self.setMinimumSize(700, 600)

        # Set global stylesheet for better input field visibility
        self.setStyleSheet("""
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit {
                min-height: 32px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QComboBox {
                padding-right: 20px;
            }
            QComboBox::drop-down {
                width: 24px;
            }
            QGroupBox {
                font-weight: bold;
                padding-top: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header
        header = QLabel(f"Generate: {self.nama_dokumen}")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        layout.addWidget(header)

        # Template info
        info_group = QGroupBox("Informasi Template")
        info_layout = QGridLayout(info_group)

        info_layout.addWidget(QLabel("Kode Dokumen:"), 0, 0)
        info_layout.addWidget(QLabel(self.kode_dokumen), 0, 1)

        info_layout.addWidget(QLabel("Template:"), 1, 0)
        info_layout.addWidget(QLabel(self.template_name or "Tidak ada template"), 1, 1)

        info_layout.addWidget(QLabel("Transaksi:"), 2, 0)
        info_layout.addWidget(QLabel(self.transaksi.get('kode', '-')), 2, 1)

        layout.addWidget(info_group)

        # Data group - scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(300)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Basic data
        data_group = QGroupBox("Data Dokumen")
        data_layout = QGridLayout(data_group)
        data_layout.setSpacing(12)
        data_layout.setContentsMargins(15, 15, 15, 15)

        row = 0

        # Nama Kegiatan
        data_layout.addWidget(QLabel("Nama Kegiatan:"), row, 0)
        self.nama_kegiatan_edit = QLineEdit()
        self.nama_kegiatan_edit.setText(self.transaksi.get('nama_kegiatan', ''))
        data_layout.addWidget(self.nama_kegiatan_edit, row, 1)
        row += 1

        # Unit Kerja - Dropdown
        data_layout.addWidget(QLabel("Unit Kerja:"), row, 0)
        self.unit_kerja_combo = QComboBox()
        self.unit_kerja_combo.setEditable(True)
        self.unit_kerja_combo.setPlaceholderText("Pilih atau ketik unit kerja...")
        data_layout.addWidget(self.unit_kerja_combo, row, 1)
        row += 1

        # Kode Akun/MAK (Sumber Dana)
        data_layout.addWidget(QLabel("Sumber Dana/MAK:"), row, 0)
        self.kode_akun_edit = QLineEdit()
        self.kode_akun_edit.setText(self.transaksi.get('kode_akun', ''))
        self.kode_akun_edit.setPlaceholderText("DIPA ... TA. 2026")
        data_layout.addWidget(self.kode_akun_edit, row, 1)
        row += 1

        # Nilai/Estimasi
        data_layout.addWidget(QLabel("Estimasi Biaya:"), row, 0)
        self.estimasi_spin = QDoubleSpinBox()
        self.estimasi_spin.setRange(0, 999999999999)
        self.estimasi_spin.setDecimals(0)
        self.estimasi_spin.setPrefix("Rp ")
        self.estimasi_spin.setGroupSeparatorShown(True)
        self.estimasi_spin.setValue(self.transaksi.get('estimasi_biaya', 0))
        self.estimasi_spin.valueChanged.connect(self._on_estimasi_changed)
        data_layout.addWidget(self.estimasi_spin, row, 1)
        row += 1

        # === Khusus untuk Kuitansi Uang Muka ===
        if self.kode_dokumen == 'KUIT_UM':
            # Persentase Uang Muka
            data_layout.addWidget(QLabel("Persentase UM:"), row, 0)
            persen_layout = QHBoxLayout()
            self.persen_combo = QComboBox()
            self.persen_combo.addItems(["100%", "90%", "80%"])
            self.persen_combo.currentIndexChanged.connect(self._on_persen_changed)
            persen_layout.addWidget(self.persen_combo)

            # Info label
            self.persen_info_label = QLabel("")
            self.persen_info_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
            persen_layout.addWidget(self.persen_info_label)
            persen_layout.addStretch()

            data_layout.addLayout(persen_layout, row, 1)
            row += 1

            # Nilai Uang Muka (calculated)
            data_layout.addWidget(QLabel("Nilai Uang Muka:"), row, 0)
            self.uang_muka_spin = QDoubleSpinBox()
            self.uang_muka_spin.setRange(0, 999999999999)
            self.uang_muka_spin.setDecimals(0)
            self.uang_muka_spin.setPrefix("Rp ")
            self.uang_muka_spin.setGroupSeparatorShown(True)
            self.uang_muka_spin.setStyleSheet("font-weight: bold; color: #27ae60;")
            data_layout.addWidget(self.uang_muka_spin, row, 1)
            row += 1

            # Auto-set percentage based on amount
            self._auto_set_percentage()

        # Tanggal
        data_layout.addWidget(QLabel("Tanggal:"), row, 0)
        self.tanggal_edit = QDateEdit()
        self.tanggal_edit.setDate(QDate.currentDate())
        self.tanggal_edit.setCalendarPopup(True)
        data_layout.addWidget(self.tanggal_edit, row, 1)
        row += 1

        # === Untuk Kuitansi UM: Bendahara dan Penerima saja ===
        if self.kode_dokumen == 'KUIT_UM':
            # Separator - Bendahara (Yang Menyerahkan)
            data_layout.addWidget(QLabel("<b>Bendahara (Yang Menyerahkan):</b>"), row, 0, 1, 2)
            row += 1

            # Bendahara - auto-filled from satker
            data_layout.addWidget(QLabel("Nama:"), row, 0)
            self.bendahara_nama_edit = QLineEdit()
            self.bendahara_nama_edit.setReadOnly(True)
            self.bendahara_nama_edit.setStyleSheet("background-color: #f5f5f5;")
            data_layout.addWidget(self.bendahara_nama_edit, row, 1)
            row += 1

            data_layout.addWidget(QLabel("NIP:"), row, 0)
            self.bendahara_nip_edit = QLineEdit()
            self.bendahara_nip_edit.setReadOnly(True)
            self.bendahara_nip_edit.setStyleSheet("background-color: #f5f5f5;")
            data_layout.addWidget(self.bendahara_nip_edit, row, 1)
            row += 1

            # Separator - Penerima (Yang Menerima)
            data_layout.addWidget(QLabel("<b>Penerima (Yang Menerima):</b>"), row, 0, 1, 2)
            row += 1
        else:
            # Separator - Yang Mengajukan (untuk dokumen lain)
            data_layout.addWidget(QLabel("<b>Yang Mengajukan:</b>"), row, 0, 1, 2)
            row += 1

        # Penerima - Dropdown dari daftar pegawai
        data_layout.addWidget(QLabel("Nama:"), row, 0)
        self.penerima_nama_combo = QComboBox()
        self.penerima_nama_combo.setEditable(True)  # Allow manual entry if needed
        self.penerima_nama_combo.setPlaceholderText("Pilih atau ketik nama penerima...")
        self.penerima_nama_combo.currentIndexChanged.connect(self._on_penerima_changed)
        data_layout.addWidget(self.penerima_nama_combo, row, 1)
        row += 1

        data_layout.addWidget(QLabel("NIP:"), row, 0)
        self.penerima_nip_edit = QLineEdit()
        self.penerima_nip_edit.setText(self.transaksi.get('penerima_nip', ''))
        self.penerima_nip_edit.setReadOnly(True)  # Auto-filled from dropdown
        self.penerima_nip_edit.setStyleSheet("background-color: #f5f5f5;")
        data_layout.addWidget(self.penerima_nip_edit, row, 1)
        row += 1

        data_layout.addWidget(QLabel("Jabatan:"), row, 0)
        self.penerima_jabatan_edit = QLineEdit()
        self.penerima_jabatan_edit.setText(self.transaksi.get('penerima_jabatan', ''))
        self.penerima_jabatan_edit.setReadOnly(True)  # Auto-filled from dropdown
        self.penerima_jabatan_edit.setStyleSheet("background-color: #f5f5f5;")
        data_layout.addWidget(self.penerima_jabatan_edit, row, 1)
        row += 1

        # Verifikator (PPSPM) - hanya untuk dokumen non-kuitansi UM
        if self.kode_dokumen != 'KUIT_UM':
            # Separator - Verifikator (PPSPM)
            data_layout.addWidget(QLabel("<b>Verifikator (PPSPM):</b>"), row, 0, 1, 2)
            row += 1

            # Verifikator PPSPM - auto-filled from satker
            data_layout.addWidget(QLabel("Nama:"), row, 0)
            self.verifikator_nama_edit = QLineEdit()
            self.verifikator_nama_edit.setReadOnly(True)
            self.verifikator_nama_edit.setStyleSheet("background-color: #f5f5f5;")
            data_layout.addWidget(self.verifikator_nama_edit, row, 1)
            row += 1

            data_layout.addWidget(QLabel("NIP:"), row, 0)
            self.verifikator_nip_edit = QLineEdit()
            self.verifikator_nip_edit.setReadOnly(True)
            self.verifikator_nip_edit.setStyleSheet("background-color: #f5f5f5;")
            data_layout.addWidget(self.verifikator_nip_edit, row, 1)

        scroll_layout.addWidget(data_group)

        # Rincian group (for Kuitansi)
        if self.kode_dokumen in ['KUIT_UM', 'KUIT_RAMP', 'LBR_REQ']:
            rincian_group = QGroupBox("Rincian Barang/Jasa (Opsional)")
            rincian_layout = QVBoxLayout(rincian_group)

            # Add item form
            add_layout = QHBoxLayout()
            self.uraian_edit = QLineEdit()
            self.uraian_edit.setPlaceholderText("Uraian barang/jasa")
            add_layout.addWidget(self.uraian_edit, 3)

            self.volume_spin = QSpinBox()
            self.volume_spin.setRange(1, 9999)
            self.volume_spin.setValue(1)
            add_layout.addWidget(self.volume_spin)

            self.satuan_combo = QComboBox()
            self.satuan_combo.setEditable(True)
            self.satuan_combo.addItems(["paket", "unit", "buah", "lembar", "orang", "set"])
            add_layout.addWidget(self.satuan_combo)

            self.harga_spin = QDoubleSpinBox()
            self.harga_spin.setRange(0, 999999999)
            self.harga_spin.setDecimals(0)
            self.harga_spin.setPrefix("Rp ")
            add_layout.addWidget(self.harga_spin)

            add_btn = QPushButton("+ Tambah")
            add_btn.clicked.connect(self._add_rincian_item)
            add_layout.addWidget(add_btn)

            rincian_layout.addLayout(add_layout)

            # Table
            self.rincian_table = QTableWidget()
            self.rincian_table.setColumnCount(5)
            self.rincian_table.setHorizontalHeaderLabels(["Uraian", "Volume", "Satuan", "Harga", "Jumlah"])
            self.rincian_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            self.rincian_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.rincian_table.setMinimumHeight(150)
            rincian_layout.addWidget(self.rincian_table)

            # Delete button
            del_btn = QPushButton("Hapus Terpilih")
            del_btn.clicked.connect(self._delete_rincian_item)
            rincian_layout.addWidget(del_btn)

            # Total
            total_layout = QHBoxLayout()
            total_layout.addStretch()
            total_layout.addWidget(QLabel("TOTAL:"))
            self.total_label = QLabel("Rp 0")
            self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            total_layout.addWidget(self.total_label)
            rincian_layout.addLayout(total_layout)

            scroll_layout.addWidget(rincian_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(self.status_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.open_folder_btn = QPushButton("Buka Folder")
        self.open_folder_btn.setVisible(False)
        self.open_folder_btn.clicked.connect(self._open_folder)
        btn_layout.addWidget(self.open_folder_btn)

        self.open_doc_btn = QPushButton("Buka Dokumen")
        self.open_doc_btn.setVisible(False)
        self.open_doc_btn.clicked.connect(self._open_document)
        btn_layout.addWidget(self.open_doc_btn)

        self.generate_btn = QPushButton("Generate Dokumen")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 25px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        self.generate_btn.clicked.connect(self._generate)
        btn_layout.addWidget(self.generate_btn)

        cancel_btn = QPushButton("Tutup")
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _load_pegawai(self):
        """Load pegawai data for dropdown, unit kerja list, and PPSPM data."""
        try:
            db = get_db_manager()
            self.pegawai_list = db.get_all_pegawai(active_only=True)

            # ===== Load Unit Kerja dropdown =====
            unit_kerja_set = set()
            for pegawai in self.pegawai_list:
                uk = pegawai.get('unit_kerja', '')
                if uk:
                    unit_kerja_set.add(uk)

            self.unit_kerja_combo.addItem("-- Pilih Unit Kerja --")
            for uk in sorted(unit_kerja_set):
                self.unit_kerja_combo.addItem(uk)

            # Set current value if transaksi has unit_kerja
            unit_kerja = self.transaksi.get('unit_kerja', '')
            if unit_kerja:
                idx = self.unit_kerja_combo.findText(unit_kerja)
                if idx >= 0:
                    self.unit_kerja_combo.setCurrentIndex(idx)
                else:
                    self.unit_kerja_combo.setCurrentText(unit_kerja)

            # ===== Load Penerima dropdown =====
            self.penerima_nama_combo.addItem("-- Pilih Pegawai --", None)

            # Add pegawai to dropdown
            for pegawai in self.pegawai_list:
                nama = pegawai.get('nama', '')
                jabatan = pegawai.get('jabatan', '')
                display_text = f"{nama} - {jabatan}" if jabatan else nama
                self.penerima_nama_combo.addItem(display_text, pegawai)

            # Set current value if transaksi has penerima_nama
            penerima_nama = self.transaksi.get('penerima_nama', '')
            if penerima_nama:
                # Try to find and select matching pegawai
                for i in range(self.penerima_nama_combo.count()):
                    pegawai = self.penerima_nama_combo.itemData(i)
                    if pegawai and pegawai.get('nama') == penerima_nama:
                        self.penerima_nama_combo.setCurrentIndex(i)
                        break
                else:
                    # Not found in list, set as editable text
                    self.penerima_nama_combo.setCurrentText(penerima_nama)

            # ===== Load Verifikator (PPSPM) dan Bendahara from satker =====
            satker_pejabat = db.get_satker_pejabat()
            if satker_pejabat:
                # PPSPM untuk verifikator (dokumen non-KUIT_UM)
                if hasattr(self, 'verifikator_nama_edit'):
                    ppspm_nama = satker_pejabat.get('ppspm_nama', '')
                    ppspm_nip = satker_pejabat.get('ppspm_nip', '')
                    self.verifikator_nama_edit.setText(ppspm_nama)
                    self.verifikator_nip_edit.setText(ppspm_nip)

                # Bendahara untuk kuitansi uang muka
                if hasattr(self, 'bendahara_nama_edit'):
                    bendahara_nama = satker_pejabat.get('bendahara_nama', '')
                    bendahara_nip = satker_pejabat.get('bendahara_nip', '')
                    self.bendahara_nama_edit.setText(bendahara_nama)
                    self.bendahara_nip_edit.setText(bendahara_nip)

        except Exception as e:
            print(f"Error loading pegawai: {e}")
            # Fallback - allow manual entry
            self.penerima_nama_combo.addItem("-- Tidak ada data pegawai --", None)

    def _on_penerima_changed(self, index: int):
        """Handle pegawai selection changed."""
        pegawai = self.penerima_nama_combo.itemData(index)

        if pegawai:
            # Auto-fill NIP and Jabatan from selected pegawai
            self.penerima_nip_edit.setText(pegawai.get('nip', ''))
            self.penerima_jabatan_edit.setText(pegawai.get('jabatan', ''))
        else:
            # Clear fields if no pegawai selected
            self.penerima_nip_edit.clear()
            self.penerima_jabatan_edit.clear()

    def _auto_set_percentage(self):
        """Auto-set percentage based on estimasi biaya.

        Rules:
        - Jika nilai < 2 juta: 100%
        - Jika nilai >= 2 juta: 80%
        """
        if not hasattr(self, 'persen_combo'):
            return

        estimasi = self.estimasi_spin.value()
        batas_2_juta = 2_000_000

        if estimasi < batas_2_juta:
            # Set 100%
            self.persen_combo.setCurrentIndex(0)  # 100%
            self.persen_info_label.setText("(< 2 jt, otomatis 100%)")
        else:
            # Set 80%
            self.persen_combo.setCurrentIndex(2)  # 80%
            self.persen_info_label.setText("(>= 2 jt, otomatis 80%)")

        self._calculate_uang_muka()

    def _on_estimasi_changed(self, value: float):
        """Handle estimasi value changed - auto recalculate percentage."""
        if self.kode_dokumen == 'KUIT_UM':
            self._auto_set_percentage()

    def _on_persen_changed(self, index: int):
        """Handle percentage selection changed."""
        if hasattr(self, 'persen_info_label'):
            self.persen_info_label.setText("(manual)")
        self._calculate_uang_muka()

    def _calculate_uang_muka(self):
        """Calculate uang muka based on percentage."""
        if not hasattr(self, 'uang_muka_spin') or not hasattr(self, 'persen_combo'):
            return

        estimasi = self.estimasi_spin.value()
        persen_text = self.persen_combo.currentText()

        # Parse percentage
        if persen_text == "100%":
            persen = 1.0
        elif persen_text == "90%":
            persen = 0.9
        elif persen_text == "80%":
            persen = 0.8
        else:
            persen = 1.0

        uang_muka = estimasi * persen
        self.uang_muka_spin.setValue(uang_muka)

    def _load_data(self):
        """Load initial data including pre-filled rincian items."""
        # Load rincian items if provided
        if self.rincian_items and hasattr(self, 'rincian_table'):
            for item in self.rincian_items:
                row = self.rincian_table.rowCount()
                self.rincian_table.insertRow(row)

                self.rincian_table.setItem(row, 0, QTableWidgetItem(item.get('uraian', '')))
                self.rincian_table.setItem(row, 1, QTableWidgetItem(str(item.get('volume', 1))))
                self.rincian_table.setItem(row, 2, QTableWidgetItem(item.get('satuan', '')))
                harga = item.get('harga_satuan', 0)
                jumlah = item.get('jumlah', 0)
                self.rincian_table.setItem(row, 3, QTableWidgetItem(f"Rp {harga:,.0f}".replace(",", ".")))
                self.rincian_table.setItem(row, 4, QTableWidgetItem(f"Rp {jumlah:,.0f}".replace(",", ".")))

            self._update_total()

    def _add_rincian_item(self):
        """Add rincian item to table."""
        uraian = self.uraian_edit.text().strip()
        if not uraian:
            return

        volume = self.volume_spin.value()
        satuan = self.satuan_combo.currentText()
        harga = self.harga_spin.value()
        jumlah = volume * harga

        # Add to table
        row = self.rincian_table.rowCount()
        self.rincian_table.insertRow(row)

        self.rincian_table.setItem(row, 0, QTableWidgetItem(uraian))
        self.rincian_table.setItem(row, 1, QTableWidgetItem(str(volume)))
        self.rincian_table.setItem(row, 2, QTableWidgetItem(satuan))
        self.rincian_table.setItem(row, 3, QTableWidgetItem(f"Rp {harga:,.0f}".replace(",", ".")))
        self.rincian_table.setItem(row, 4, QTableWidgetItem(f"Rp {jumlah:,.0f}".replace(",", ".")))

        # Add to list
        self.rincian_items.append({
            'uraian': uraian,
            'volume': volume,
            'satuan': satuan,
            'harga_satuan': harga,
            'jumlah': jumlah,
        })

        # Clear inputs
        self.uraian_edit.clear()
        self.volume_spin.setValue(1)
        self.harga_spin.setValue(0)

        # Update total
        self._update_total()

    def _delete_rincian_item(self):
        """Delete selected rincian item."""
        rows = set()
        for item in self.rincian_table.selectedItems():
            rows.add(item.row())

        for row in sorted(rows, reverse=True):
            self.rincian_table.removeRow(row)
            if row < len(self.rincian_items):
                self.rincian_items.pop(row)

        self._update_total()

    def _update_total(self):
        """Update total label."""
        total = sum(item['jumlah'] for item in self.rincian_items)
        self.total_label.setText(f"Rp {total:,.0f}".replace(",", "."))

    def _collect_data(self) -> Dict[str, Any]:
        """Collect all form data."""
        # Get penerima name - from selected pegawai or manual entry
        pegawai = self.penerima_nama_combo.currentData()
        if pegawai:
            penerima_nama = pegawai.get('nama', '')
        else:
            # Manual entry - use the text directly
            penerima_nama = self.penerima_nama_combo.currentText()
            # Remove " - jabatan" suffix if present from display text
            if " - " in penerima_nama:
                penerima_nama = penerima_nama.split(" - ")[0]

        # Get unit kerja
        unit_kerja = self.unit_kerja_combo.currentText()
        if unit_kerja.startswith("--"):
            unit_kerja = ""

        data = {
            'nama_kegiatan': self.nama_kegiatan_edit.text(),
            'unit_kerja': unit_kerja,
            'sumber_dana': self.kode_akun_edit.text(),
            'kode_akun': self.kode_akun_edit.text(),
            'estimasi_biaya': self.estimasi_spin.value(),
            'tanggal_dokumen': self.tanggal_edit.date().toString("yyyy-MM-dd"),
            'penerima_nama': penerima_nama,
            'penerima_nip': self.penerima_nip_edit.text(),
            'penerima_jabatan': self.penerima_jabatan_edit.text(),
        }

        # Khusus untuk Kuitansi Uang Muka
        if self.kode_dokumen == 'KUIT_UM':
            data['uang_muka'] = self.uang_muka_spin.value() if hasattr(self, 'uang_muka_spin') else 0
            data['persentase_um'] = self.persen_combo.currentText() if hasattr(self, 'persen_combo') else '100%'
            data['bendahara_nama'] = self.bendahara_nama_edit.text() if hasattr(self, 'bendahara_nama_edit') else ''
            data['bendahara_nip'] = self.bendahara_nip_edit.text() if hasattr(self, 'bendahara_nip_edit') else ''
        else:
            # Verifikator (PPSPM) untuk dokumen non-KUIT_UM
            if hasattr(self, 'verifikator_nama_edit'):
                data['verifikator_nama'] = self.verifikator_nama_edit.text()
                data['verifikator_nip'] = self.verifikator_nip_edit.text()
                data['ppspm_nama'] = self.verifikator_nama_edit.text()
                data['ppspm_nip'] = self.verifikator_nip_edit.text()

        # Merge with transaksi data
        for key, value in self.transaksi.items():
            if key not in data:
                data[key] = value

        return data

    def _generate(self):
        """Generate the document."""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(20)
            self.status_label.setText("Mempersiapkan data...")

            # Import generator
            from app.services.dokumen_generator import get_dokumen_generator

            generator = get_dokumen_generator()

            self.progress_bar.setValue(40)
            self.status_label.setText("Mengambil template...")

            # Collect form data
            form_data = self._collect_data()

            # Update transaksi with form data
            merged_transaksi = {**self.transaksi, **form_data}

            self.progress_bar.setValue(60)
            self.status_label.setText("Generating dokumen...")

            # Generate document
            output_path, error = generator.generate_document(
                transaksi=merged_transaksi,
                kode_dokumen=self.kode_dokumen,
                template_name=self.template_name,
                satker=self.satker,
                rincian=self.rincian_items if self.rincian_items else None,
                additional_data=form_data
            )

            self.progress_bar.setValue(100)

            if error:
                self.status_label.setText(f"Error: {error}")
                self.status_label.setStyleSheet("color: #e74c3c;")
                QMessageBox.critical(self, "Error", error)
            else:
                self.generated_path = output_path
                self.status_label.setText(f"Dokumen berhasil dibuat: {output_path}")
                self.status_label.setStyleSheet("color: #27ae60;")

                # Show open buttons
                self.open_folder_btn.setVisible(True)
                self.open_doc_btn.setVisible(True)
                self.generate_btn.setText("Generate Ulang")

                # Emit signal
                self.dokumen_generated.emit(output_path)

                QMessageBox.information(
                    self,
                    "Sukses",
                    f"Dokumen berhasil dibuat:\n{output_path}"
                )

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("color: #e74c3c;")
            QMessageBox.critical(self, "Error", f"Gagal generate dokumen:\n{str(e)}")

        finally:
            self.progress_bar.setVisible(False)

    def _open_document(self):
        """Open generated document."""
        if self.generated_path:
            from app.services.dokumen_generator import get_dokumen_generator
            generator = get_dokumen_generator()
            generator.open_document(self.generated_path)

    def _open_folder(self):
        """Open output folder."""
        if self.generated_path:
            import os
            folder = os.path.dirname(self.generated_path)
            from app.services.dokumen_generator import get_dokumen_generator
            generator = get_dokumen_generator()
            generator.open_document(folder)


class UploadDokumenDialog(QDialog):
    """Dialog untuk upload dokumen arsip."""

    dokumen_uploaded = Signal(str)  # filepath

    def __init__(self, transaksi: Dict[str, Any], kode_dokumen: str,
                 nama_dokumen: str = None, is_arsip: bool = False, parent=None):
        super().__init__(parent)
        self.transaksi = transaksi
        self.kode_dokumen = kode_dokumen
        self.nama_dokumen = nama_dokumen or kode_dokumen
        self.is_arsip = is_arsip
        self.selected_file = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle(f"Upload Arsip - {self.nama_dokumen}")
        self.setMinimumSize(500, 300)

        # Set global stylesheet for better input field visibility
        self.setStyleSheet("""
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit {
                min-height: 32px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QLabel {
                padding: 2px 0;
            }
            QGroupBox {
                font-weight: bold;
                padding-top: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header
        header = QLabel(f"Upload Arsip: {self.nama_dokumen}")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        layout.addWidget(header)

        # Info
        info = QLabel("Pilih file PDF atau gambar (JPG, PNG) untuk diupload sebagai arsip dokumen.")
        info.setWordWrap(True)
        layout.addWidget(info)

        # File selection
        file_group = QGroupBox("File")
        file_layout = QHBoxLayout(file_group)

        self.file_label = QLabel("Belum ada file dipilih")
        self.file_label.setStyleSheet("color: #7f8c8d;")
        file_layout.addWidget(self.file_label, 1)

        browse_btn = QPushButton("Pilih File...")
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_btn)

        layout.addWidget(file_group)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.upload_btn = QPushButton("Upload")
        self.upload_btn.setEnabled(False)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px 25px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7d3c98;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.upload_btn.clicked.connect(self._upload)
        btn_layout.addWidget(self.upload_btn)

        cancel_btn = QPushButton("Batal")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _browse_file(self):
        """Browse for file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih File Arsip",
            "",
            "Documents (*.pdf *.jpg *.jpeg *.png);;PDF Files (*.pdf);;Images (*.jpg *.jpeg *.png);;All Files (*)"
        )

        if filepath:
            self.selected_file = filepath
            self.file_label.setText(filepath)
            self.file_label.setStyleSheet("color: #2c3e50;")
            self.upload_btn.setEnabled(True)

    def _upload(self):
        """Upload the file."""
        if not self.selected_file:
            return

        try:
            import shutil
            from pathlib import Path
            from datetime import datetime

            # Get output folder using new folder structure
            from app.services.dokumen_generator import get_dokumen_generator

            generator = get_dokumen_generator()
            output_folder = generator.get_output_folder(transaksi=self.transaksi)

            # Copy file
            src = Path(self.selected_file)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            suffix = "_ARSIP" if self.is_arsip else ""
            dest = output_folder / f"{self.kode_dokumen}{suffix}_{timestamp}{src.suffix}"

            shutil.copy2(src, dest)

            QMessageBox.information(
                self,
                "Sukses",
                f"File berhasil diupload:\n{dest}"
            )

            self.dokumen_uploaded.emit(str(dest))
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal upload file:\n{str(e)}")
