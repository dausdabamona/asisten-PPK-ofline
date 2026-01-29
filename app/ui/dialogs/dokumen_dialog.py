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

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle(f"Buat Dokumen - {self.nama_dokumen}")
        self.setMinimumSize(700, 600)

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
        data_layout.setSpacing(5)  # Reduced spacing for compact layout
        data_layout.setContentsMargins(10, 10, 10, 10)

        row = 0

        # Nama Kegiatan
        data_layout.addWidget(QLabel("Nama Kegiatan:"), row, 0)
        self.nama_kegiatan_edit = QLineEdit()
        self.nama_kegiatan_edit.setText(self.transaksi.get('nama_kegiatan', ''))
        data_layout.addWidget(self.nama_kegiatan_edit, row, 1)
        row += 1

        # Kode Akun
        data_layout.addWidget(QLabel("Kode Akun:"), row, 0)
        self.kode_akun_edit = QLineEdit()
        self.kode_akun_edit.setText(self.transaksi.get('kode_akun', ''))
        data_layout.addWidget(self.kode_akun_edit, row, 1)
        row += 1

        # Tanggal
        data_layout.addWidget(QLabel("Tanggal:"), row, 0)
        self.tanggal_edit = QDateEdit()
        self.tanggal_edit.setDate(QDate.currentDate())
        self.tanggal_edit.setCalendarPopup(True)
        data_layout.addWidget(self.tanggal_edit, row, 1)
        row += 1

        # Penerima - dropdown with search (disable scroll wheel)
        data_layout.addWidget(QLabel("Nama Penerima:"), row, 0)
        self.penerima_nama_combo = QComboBox()
        self.penerima_nama_combo.setEditable(True)
        self.penerima_nama_combo.setInsertPolicy(QComboBox.NoInsert)
        # Disable scroll wheel on combobox
        self.penerima_nama_combo.wheelEvent = lambda e: e.ignore()
        self.penerima_nama_combo.currentIndexChanged.connect(self._on_penerima_changed)
        self._load_pegawai_dropdown()
        data_layout.addWidget(self.penerima_nama_combo, row, 1)
        row += 1

        data_layout.addWidget(QLabel("NIP Penerima:"), row, 0)
        self.penerima_nip_edit = QLineEdit()
        self.penerima_nip_edit.setText(self.transaksi.get('penerima_nip', ''))
        data_layout.addWidget(self.penerima_nip_edit, row, 1)
        row += 1

        data_layout.addWidget(QLabel("Jabatan:"), row, 0)
        self.penerima_jabatan_edit = QLineEdit()
        self.penerima_jabatan_edit.setText(self.transaksi.get('penerima_jabatan', ''))
        data_layout.addWidget(self.penerima_jabatan_edit, row, 1)

        scroll_layout.addWidget(data_group)

        # KUIT_RAMP = Kuitansi Rampung (final settlement) - Summary only, no rincian input
        if self.kode_dokumen == 'KUIT_RAMP':
            self._setup_kuitansi_rampung_ui(scroll_layout)

        # Rincian group (for documents with item details)
        # LBR_REQ = Lembar Permintaan (estimasi)
        # REKAP_BKT = Rekap Bukti Pengeluaran (realisasi aktual)
        # KUIT_UM = Kuitansi Uang Muka
        elif self.kode_dokumen in ['KUIT_UM', 'LBR_REQ', 'REKAP_BKT']:
            # Set label based on document type
            if self.kode_dokumen == 'REKAP_BKT':
                rincian_label = "Rincian Bukti Pengeluaran (Realisasi)"
            else:
                rincian_label = "Rincian Barang/Jasa"
            rincian_group = QGroupBox(rincian_label)
            rincian_layout = QVBoxLayout(rincian_group)
            rincian_layout.setSpacing(5)  # Compact spacing

            # Add item form - row 1: uraian
            add_layout1 = QHBoxLayout()
            add_layout1.addWidget(QLabel("Uraian:"))
            self.uraian_edit = QLineEdit()
            self.uraian_edit.setPlaceholderText("Uraian barang/jasa")
            add_layout1.addWidget(self.uraian_edit)
            rincian_layout.addLayout(add_layout1)

            # Add item form - row 2: volume, satuan, harga, jumlah preview
            add_layout2 = QHBoxLayout()

            add_layout2.addWidget(QLabel("Vol:"))
            self.volume_spin = QSpinBox()
            self.volume_spin.setRange(1, 9999)
            self.volume_spin.setValue(1)
            self.volume_spin.valueChanged.connect(self._update_jumlah_preview)
            add_layout2.addWidget(self.volume_spin)

            add_layout2.addWidget(QLabel("Sat:"))
            self.satuan_combo = QComboBox()
            self.satuan_combo.setEditable(True)
            self.satuan_combo.addItems(["paket", "unit", "buah", "lembar", "orang", "set"])
            # Disable scroll wheel on combobox
            self.satuan_combo.wheelEvent = lambda e: e.ignore()
            add_layout2.addWidget(self.satuan_combo)

            add_layout2.addWidget(QLabel("Harga:"))
            self.harga_spin = QDoubleSpinBox()
            self.harga_spin.setRange(0, 999999999)
            self.harga_spin.setDecimals(0)
            self.harga_spin.setPrefix("Rp ")
            self.harga_spin.valueChanged.connect(self._update_jumlah_preview)
            add_layout2.addWidget(self.harga_spin)

            # Jumlah preview (auto-calculated)
            add_layout2.addWidget(QLabel("="))
            self.jumlah_preview = QLabel("Rp 0")
            self.jumlah_preview.setStyleSheet("font-weight: bold; color: #27ae60; min-width: 100px;")
            add_layout2.addWidget(self.jumlah_preview)

            add_btn = QPushButton("+ Tambah")
            add_btn.clicked.connect(self._add_rincian_item)
            add_layout2.addWidget(add_btn)

            rincian_layout.addLayout(add_layout2)

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

            # Tax Options (PPN & PPh)
            from PySide6.QtWidgets import QCheckBox
            tax_group = QGroupBox("Pajak")
            tax_layout = QGridLayout(tax_group)
            tax_layout.setSpacing(5)

            # PPN 11%
            self.ppn_checkbox = QCheckBox("PPN 11%")
            self.ppn_checkbox.stateChanged.connect(self._update_total)
            tax_layout.addWidget(self.ppn_checkbox, 0, 0)
            self.ppn_label = QLabel("Rp 0")
            self.ppn_label.setStyleSheet("color: #e74c3c;")
            tax_layout.addWidget(self.ppn_label, 0, 1)

            # PPh options
            self.pph_checkbox = QCheckBox("PPh")
            self.pph_checkbox.stateChanged.connect(self._update_total)
            tax_layout.addWidget(self.pph_checkbox, 1, 0)

            self.pph_rate_combo = QComboBox()
            self.pph_rate_combo.addItems(["1.5% (PPh 23)", "2% (PPh 23 Jasa)", "4% (PPh 23)", "15% (PPh 23)"])
            self.pph_rate_combo.wheelEvent = lambda e: e.ignore()  # Disable scroll
            self.pph_rate_combo.currentIndexChanged.connect(self._update_total)
            self.pph_rate_combo.setEnabled(False)
            tax_layout.addWidget(self.pph_rate_combo, 1, 1)

            self.pph_label = QLabel("Rp 0")
            self.pph_label.setStyleSheet("color: #e74c3c;")
            tax_layout.addWidget(self.pph_label, 1, 2)

            rincian_layout.addWidget(tax_group)

            # Grand Total after taxes
            grand_total_layout = QHBoxLayout()
            grand_total_layout.addStretch()
            grand_total_layout.addWidget(QLabel("GRAND TOTAL:"))
            self.grand_total_label = QLabel("Rp 0")
            self.grand_total_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #27ae60;")
            grand_total_layout.addWidget(self.grand_total_label)
            rincian_layout.addLayout(grand_total_layout)

            # Perhitungan Tambah/Kurang Panel (for REKAP_BKT)
            if self.kode_dokumen == 'REKAP_BKT':
                calc_group = QGroupBox("Perhitungan Tambah/Kurang")
                calc_group.setStyleSheet("""
                    QGroupBox {
                        font-weight: bold;
                        font-size: 14px;
                        border: 2px solid #3498db;
                        border-radius: 8px;
                        margin-top: 15px;
                        padding: 15px;
                        background-color: #f8f9fa;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 15px;
                        padding: 0 10px;
                        color: #2c3e50;
                        background-color: #f8f9fa;
                    }
                """)
                calc_layout = QGridLayout(calc_group)
                calc_layout.setSpacing(12)
                calc_layout.setContentsMargins(15, 20, 15, 15)

                # Style for labels
                label_style = "font-size: 13px; color: #2c3e50; padding: 5px;"
                value_style = "font-weight: bold; font-size: 14px; color: #2c3e50; padding: 5px;"

                # Uang Muka (from LBR_REQ)
                lbl_um = QLabel("Uang Muka Diterima:")
                lbl_um.setStyleSheet(label_style)
                calc_layout.addWidget(lbl_um, 0, 0)
                self.uang_muka_label = QLabel("Rp 0")
                self.uang_muka_label.setStyleSheet(value_style + "color: #3498db;")
                calc_layout.addWidget(self.uang_muka_label, 0, 1)

                # Realisasi (current input)
                lbl_real = QLabel("Total Realisasi:")
                lbl_real.setStyleSheet(label_style)
                calc_layout.addWidget(lbl_real, 1, 0)
                self.realisasi_label = QLabel("Rp 0")
                self.realisasi_label.setStyleSheet(value_style)
                calc_layout.addWidget(self.realisasi_label, 1, 1)

                # Separator line
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setStyleSheet("background-color: #bdc3c7; margin: 5px 0;")
                calc_layout.addWidget(separator, 2, 0, 1, 2)

                # Selisih
                lbl_selisih = QLabel("Selisih:")
                lbl_selisih.setStyleSheet(label_style + "font-weight: bold;")
                calc_layout.addWidget(lbl_selisih, 3, 0)
                self.selisih_label = QLabel("Rp 0")
                self.selisih_label.setStyleSheet("font-weight: bold; font-size: 16px; padding: 5px;")
                calc_layout.addWidget(self.selisih_label, 3, 1)

                # Status (Kurang Bayar / Lebih Bayar / Nihil)
                self.status_calc_label = QLabel("")
                self.status_calc_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px; margin-top: 5px;")
                self.status_calc_label.setAlignment(Qt.AlignCenter)
                calc_layout.addWidget(self.status_calc_label, 4, 0, 1, 2)

                rincian_layout.addWidget(calc_group)

                # Load uang muka from database
                self._load_uang_muka_for_calc()

            # Uang Muka Percentage Option (for KUIT_UM / Kuitansi Uang Muka)
            if self.kode_dokumen == 'KUIT_UM':
                from PySide6.QtWidgets import QRadioButton, QButtonGroup

                # Nomor Tanda Terima (auto-generated)
                nomor_tt_group = QGroupBox("Nomor Tanda Terima Uang Muka")
                nomor_tt_layout = QHBoxLayout(nomor_tt_group)
                self._generate_nomor_tanda_terima()
                self.nomor_tt_label = QLabel(self._nomor_tanda_terima)
                self.nomor_tt_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #27ae60; padding: 5px;")
                nomor_tt_layout.addWidget(self.nomor_tt_label)
                nomor_tt_layout.addStretch()
                rincian_layout.addWidget(nomor_tt_group)

                um_group_box = QGroupBox("Persentase Uang Muka Diterima")
                um_layout = QHBoxLayout(um_group_box)

                self.um_btn_group = QButtonGroup(self)
                self.um_100 = QRadioButton("100%")
                self.um_100.setChecked(True)
                self.um_90 = QRadioButton("90%")
                self.um_80 = QRadioButton("80%")

                self.um_btn_group.addButton(self.um_100, 100)
                self.um_btn_group.addButton(self.um_90, 90)
                self.um_btn_group.addButton(self.um_80, 80)

                um_layout.addWidget(self.um_100)
                um_layout.addWidget(self.um_90)
                um_layout.addWidget(self.um_80)
                um_layout.addStretch()

                self.um_nilai_label = QLabel("Nilai Diterima: Rp 0")
                self.um_nilai_label.setStyleSheet("font-weight: bold; color: #3498db;")
                um_layout.addWidget(self.um_nilai_label)

                self.um_btn_group.buttonClicked.connect(self._update_total)
                rincian_layout.addWidget(um_group_box)

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

    def _load_pegawai_dropdown(self):
        """Load pegawai data into dropdown."""
        try:
            from app.core.database_v4 import get_db_manager_v4
            db = get_db_manager_v4()
            pegawai_list = db.get_all_pegawai(active_only=True)

            self.penerima_nama_combo.clear()
            self.penerima_nama_combo.addItem("-- Pilih Pegawai --", None)

            # Store pegawai data for lookup
            self._pegawai_data = {}

            for p in pegawai_list:
                # Format display name with gelar
                nama_display = p.get('nama', '')
                gelar_depan = p.get('gelar_depan', '')
                gelar_belakang = p.get('gelar_belakang', '')

                if gelar_depan:
                    nama_display = f"{gelar_depan} {nama_display}"
                if gelar_belakang:
                    nama_display = f"{nama_display}, {gelar_belakang}"

                nip = p.get('nip', '')
                display_text = f"{nama_display}" + (f" ({nip})" if nip else "")

                self.penerima_nama_combo.addItem(display_text, p.get('id'))
                self._pegawai_data[p.get('id')] = p

            # Set initial value from transaksi if exists
            penerima_nama = self.transaksi.get('penerima_nama', '')
            penerima_nip = self.transaksi.get('penerima_nip', '')
            found = False

            for i in range(self.penerima_nama_combo.count()):
                item_text = self.penerima_nama_combo.itemText(i)
                # Check if NIP matches
                if penerima_nip and f"({penerima_nip})" in item_text:
                    self.penerima_nama_combo.setCurrentIndex(i)
                    found = True
                    break

            if not found and penerima_nama:
                # Set as custom text if not found in dropdown
                self.penerima_nama_combo.setEditText(penerima_nama)

        except Exception as e:
            print(f"Error loading pegawai: {e}")
            # Fallback - allow manual entry
            self.penerima_nama_combo.addItem("-- Data pegawai tidak tersedia --", None)
            penerima_nama = self.transaksi.get('penerima_nama', '')
            if penerima_nama:
                self.penerima_nama_combo.setEditText(penerima_nama)

    def _on_penerima_changed(self, index: int):
        """Handle pegawai selection change - auto-fill NIP and jabatan."""
        pegawai_id = self.penerima_nama_combo.currentData()

        if pegawai_id and hasattr(self, '_pegawai_data') and pegawai_id in self._pegawai_data:
            p = self._pegawai_data[pegawai_id]
            self.penerima_nip_edit.setText(p.get('nip', ''))
            self.penerima_jabatan_edit.setText(p.get('jabatan', ''))
        # Don't clear if user is typing custom name

    def _setup_kuitansi_rampung_ui(self, parent_layout):
        """Setup UI for Kuitansi Rampung - summary only without rincian input."""
        from PySide6.QtWidgets import QTextEdit

        # Load data from database first
        self._load_kuitansi_rampung_data()

        # Summary Panel
        summary_group = QGroupBox("Ringkasan Pertanggungjawaban")
        summary_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #2c3e50;
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #2c3e50;
                background-color: #f8f9fa;
            }
        """)
        summary_layout = QGridLayout(summary_group)
        summary_layout.setSpacing(12)
        summary_layout.setContentsMargins(20, 25, 20, 20)

        # Style for labels
        label_style = "font-size: 14px; color: #2c3e50; padding: 8px 5px;"
        value_style = "font-weight: bold; font-size: 15px; padding: 8px 5px;"

        # Uang Muka Diterima
        lbl_um = QLabel("Uang Muka Diterima:")
        lbl_um.setStyleSheet(label_style)
        summary_layout.addWidget(lbl_um, 0, 0)
        self.kr_uang_muka_label = QLabel(f"Rp {self._kr_uang_muka:,.0f}".replace(",", "."))
        self.kr_uang_muka_label.setStyleSheet(value_style + "color: #3498db;")
        summary_layout.addWidget(self.kr_uang_muka_label, 0, 1)

        # Total Realisasi
        lbl_real = QLabel("Total Realisasi Belanja:")
        lbl_real.setStyleSheet(label_style)
        summary_layout.addWidget(lbl_real, 1, 0)
        self.kr_realisasi_label = QLabel(f"Rp {self._kr_realisasi:,.0f}".replace(",", "."))
        self.kr_realisasi_label.setStyleSheet(value_style + "color: #2c3e50;")
        summary_layout.addWidget(self.kr_realisasi_label, 1, 1)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #bdc3c7; margin: 8px 0;")
        summary_layout.addWidget(separator, 2, 0, 1, 2)

        # Selisih
        lbl_selisih = QLabel("Selisih:")
        lbl_selisih.setStyleSheet(label_style + "font-weight: bold;")
        summary_layout.addWidget(lbl_selisih, 3, 0)
        self.kr_selisih_label = QLabel(f"Rp {abs(self._kr_selisih):,.0f}".replace(",", "."))
        self.kr_selisih_label.setStyleSheet("font-weight: bold; font-size: 18px; padding: 8px 5px;")
        summary_layout.addWidget(self.kr_selisih_label, 3, 1)

        # Status Badge
        self.kr_status_label = QLabel("")
        self.kr_status_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(self.kr_status_label, 4, 0, 1, 2)

        # Update status display
        self._update_kuitansi_rampung_status()

        parent_layout.addWidget(summary_group)

        # Klausul/Keterangan Panel
        klausul_group = QGroupBox("Keterangan Pertanggungjawaban")
        klausul_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 15px;
                padding: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #27ae60;
                background-color: #f8f9fa;
            }
        """)
        klausul_layout = QVBoxLayout(klausul_group)
        klausul_layout.setContentsMargins(15, 20, 15, 15)

        self.kr_klausul_text = QTextEdit()
        self.kr_klausul_text.setMaximumHeight(120)
        self.kr_klausul_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 12px;
                font-size: 13px;
                line-height: 1.5;
                background-color: white;
            }
        """)

        # Generate klausul text based on status
        self._generate_klausul_text()

        klausul_layout.addWidget(self.kr_klausul_text)
        parent_layout.addWidget(klausul_group)

    def _load_kuitansi_rampung_data(self):
        """Load data for Kuitansi Rampung from database."""
        self._kr_uang_muka = 0
        self._kr_realisasi = 0
        self._kr_selisih = 0
        self._kr_status = 'NIHIL'

        try:
            transaksi_id = self.transaksi.get('id')
            if not transaksi_id:
                return

            from app.models.pencairan_models import PencairanManager
            manager = PencairanManager()

            # Get uang_muka from transaksi or LBR_REQ
            self._kr_uang_muka = self.transaksi.get('uang_muka', 0) or 0
            if not self._kr_uang_muka:
                summary = manager.get_rincian_summary(transaksi_id, 'LBR_REQ')
                if summary:
                    self._kr_uang_muka = summary.get('uang_muka_nilai', 0) or summary.get('total_dengan_ppn', 0)

            # Get realisasi from transaksi or REKAP_BKT
            self._kr_realisasi = self.transaksi.get('realisasi', 0) or 0
            if not self._kr_realisasi:
                summary = manager.get_rincian_summary(transaksi_id, 'REKAP_BKT')
                if summary:
                    self._kr_realisasi = summary.get('total_dengan_ppn', 0) or summary.get('subtotal', 0)

            # Calculate selisih
            self._kr_selisih = self._kr_realisasi - self._kr_uang_muka

            # Determine status
            if self._kr_selisih > 0:
                self._kr_status = 'KURANG_BAYAR'
            elif self._kr_selisih < 0:
                self._kr_status = 'LEBIH_BAYAR'
            else:
                self._kr_status = 'NIHIL'

            print(f"Kuitansi Rampung Data: UM={self._kr_uang_muka}, Real={self._kr_realisasi}, Selisih={self._kr_selisih}, Status={self._kr_status}")

        except Exception as e:
            print(f"Error loading Kuitansi Rampung data: {e}")

    def _update_kuitansi_rampung_status(self):
        """Update status label styling for Kuitansi Rampung."""
        base_status_style = "font-weight: bold; font-size: 16px; padding: 12px 25px; margin-top: 10px; border-radius: 8px;"
        base_selisih_style = "font-weight: bold; font-size: 18px; padding: 8px 5px;"

        if self._kr_status == 'KURANG_BAYAR':
            self.kr_status_label.setText("⚠ KURANG BAYAR")
            self.kr_status_label.setStyleSheet(base_status_style + "background-color: #e74c3c; color: white;")
            self.kr_selisih_label.setStyleSheet(base_selisih_style + "color: #e74c3c;")
        elif self._kr_status == 'LEBIH_BAYAR':
            self.kr_status_label.setText("✓ LEBIH BAYAR (Dikembalikan ke Kas)")
            self.kr_status_label.setStyleSheet(base_status_style + "background-color: #27ae60; color: white;")
            self.kr_selisih_label.setStyleSheet(base_selisih_style + "color: #27ae60;")
        else:
            self.kr_status_label.setText("✓ NIHIL (Pas)")
            self.kr_status_label.setStyleSheet(base_status_style + "background-color: #3498db; color: white;")
            self.kr_selisih_label.setStyleSheet(base_selisih_style + "color: #3498db;")

    def _generate_klausul_text(self):
        """Generate klausul text based on calculation status."""
        penerima = self.transaksi.get('penerima_nama', '[Nama Penerima]')
        selisih_str = f"Rp {abs(self._kr_selisih):,.0f}".replace(",", ".")

        if self._kr_status == 'KURANG_BAYAR':
            klausul = (
                f"Berdasarkan perhitungan di atas, terdapat kekurangan pembayaran "
                f"sebesar {selisih_str} yang harus dibayarkan oleh Bendahara Pengeluaran "
                f"kepada {penerima} untuk menyelesaikan pertanggungjawaban kegiatan ini."
            )
        elif self._kr_status == 'LEBIH_BAYAR':
            klausul = (
                f"Berdasarkan perhitungan di atas, terdapat sisa uang muka "
                f"sebesar {selisih_str} yang harus dikembalikan oleh {penerima} "
                f"kepada Bendahara Pengeluaran/Kas Negara untuk menyelesaikan "
                f"pertanggungjawaban kegiatan ini."
            )
        else:
            klausul = (
                f"Berdasarkan perhitungan di atas, penggunaan uang muka telah sesuai "
                f"dengan realisasi belanja (NIHIL). Tidak ada sisa uang yang perlu "
                f"dikembalikan maupun kekurangan yang perlu dibayarkan."
            )

        self.kr_klausul_text.setText(klausul)

    def _load_data(self):
        """Load initial data including pre-filled rincian items."""
        # KUIT_RAMP has its own data loading in _setup_kuitansi_rampung_ui
        if self.kode_dokumen == 'KUIT_RAMP':
            return

        # For documents in the workflow flow - try to load from database if no items provided
        # KUIT_UM = Kuitansi Uang Muka (loads from LBR_REQ)
        # REKAP_BKT = Rekap Bukti Pengeluaran (loads from LBR_REQ as template)
        if self.kode_dokumen in ['KUIT_UM', 'REKAP_BKT'] and not self.rincian_items:
            self._load_rincian_from_db()

        # Load rincian items if available (either provided or loaded from DB)
        if self.rincian_items and hasattr(self, 'rincian_table'):
            for item in self.rincian_items:
                row = self.rincian_table.rowCount()
                self.rincian_table.insertRow(row)

                volume = item.get('volume', 1)
                harga = item.get('harga_satuan', 0)
                # Auto-calculate jumlah from volume × harga (not from stored value)
                jumlah = volume * harga
                # Update item with calculated jumlah
                item['jumlah'] = jumlah

                self.rincian_table.setItem(row, 0, QTableWidgetItem(item.get('uraian', '')))
                self.rincian_table.setItem(row, 1, QTableWidgetItem(str(volume)))
                self.rincian_table.setItem(row, 2, QTableWidgetItem(item.get('satuan', '')))
                self.rincian_table.setItem(row, 3, QTableWidgetItem(f"Rp {harga:,.0f}".replace(",", ".")))
                self.rincian_table.setItem(row, 4, QTableWidgetItem(f"Rp {jumlah:,.0f}".replace(",", ".")))

            # Load PPN and uang muka settings from the saved data
            if self.rincian_items:
                first_item = self.rincian_items[0]
                ppn_persen = first_item.get('ppn_persen', 0)
                um_persen = first_item.get('uang_muka_persen', 100)

                # Set PPN checkbox if applicable
                if hasattr(self, 'ppn_checkbox') and ppn_persen > 0:
                    self.ppn_checkbox.setChecked(True)

                # Set uang muka percentage if applicable
                if hasattr(self, 'um_btn_group'):
                    if um_persen == 90:
                        self.um_90.setChecked(True)
                    elif um_persen == 80:
                        self.um_80.setChecked(True)
                    else:
                        self.um_100.setChecked(True)

            self._update_total()

    def _load_rincian_from_db(self):
        """
        Load rincian items from database based on document flow:

        Document Flow:
        1. LBR_REQ (Lembar Permintaan) → User enters estimasi items
        2. REKAP_BKT (Rekap Bukti) → Load from LBR_REQ as template, user modifies with actual
        3. KUIT_RAMP (Kuitansi Rampung) → Load from REKAP_BKT (realisasi aktual)
        """
        try:
            transaksi_id = self.transaksi.get('id')
            if not transaksi_id:
                return

            from app.models.pencairan_models import PencairanManager
            manager = PencairanManager()

            # Determine source based on document type
            if self.kode_dokumen == 'KUIT_RAMP':
                # Kuitansi Rampung: Load from REKAP_BKT (realisasi aktual)
                # If no REKAP_BKT data, fall back to LBR_REQ
                items = manager.get_rincian_items(transaksi_id, 'REKAP_BKT')
                source = 'REKAP_BKT'
                if not items:
                    items = manager.get_rincian_items(transaksi_id, 'LBR_REQ')
                    source = 'LBR_REQ'

            elif self.kode_dokumen == 'REKAP_BKT':
                # Rekap Bukti: Check if own data exists first
                items = manager.get_rincian_items(transaksi_id, 'REKAP_BKT')
                source = 'REKAP_BKT'
                if not items:
                    # Load from LBR_REQ as template
                    items = manager.get_rincian_items(transaksi_id, 'LBR_REQ')
                    source = 'LBR_REQ (as template)'

            elif self.kode_dokumen == 'KUIT_UM':
                # Kuitansi Uang Muka: Load from LBR_REQ
                items = manager.get_rincian_items(transaksi_id, 'LBR_REQ')
                source = 'LBR_REQ'

            else:
                # Default: Load from LBR_REQ
                items = manager.get_rincian_items(transaksi_id, 'LBR_REQ')
                source = 'LBR_REQ'

            if items:
                # Convert to proper format (remove database IDs)
                self.rincian_items = []
                for item in items:
                    self.rincian_items.append({
                        'uraian': item.get('uraian', ''),
                        'volume': item.get('volume', 1),
                        'satuan': item.get('satuan', 'paket'),
                        'harga_satuan': item.get('harga_satuan', 0),
                        'jumlah': item.get('jumlah', 0),
                        'ppn_persen': item.get('ppn_persen', 0),
                        'uang_muka_persen': item.get('uang_muka_persen', 100),
                    })
                print(f"Loaded {len(items)} rincian items from {source} for transaksi {transaksi_id}")

        except Exception as e:
            print(f"Error loading rincian from database: {e}")

    def _generate_nomor_tanda_terima(self):
        """Generate nomor tanda terima uang muka."""
        try:
            from app.services.dokumen_generator import get_dokumen_generator
            generator = get_dokumen_generator()

            if self.kode_dokumen == 'KUIT_UM':
                self._nomor_tanda_terima = generator.generate_nomor_tanda_terima('UM')
            elif self.kode_dokumen == 'KUIT_RAMP':
                self._nomor_tanda_terima = generator.generate_nomor_tanda_terima('RAMP')
            else:
                self._nomor_tanda_terima = ""

            print(f"Generated nomor tanda terima: {self._nomor_tanda_terima}")

        except Exception as e:
            print(f"Error generating nomor tanda terima: {e}")
            from datetime import datetime
            now = datetime.now()
            self._nomor_tanda_terima = f"001/TT-UM/{now.year}"

    def _load_uang_muka_for_calc(self):
        """Load uang muka value for REKAP_BKT calculation panel."""
        try:
            transaksi_id = self.transaksi.get('id')
            if not transaksi_id:
                return

            # First try to get from transaksi
            self._uang_muka_nilai = self.transaksi.get('uang_muka', 0) or 0

            # If not set, calculate from LBR_REQ
            if not self._uang_muka_nilai:
                from app.models.pencairan_models import PencairanManager
                manager = PencairanManager()
                summary = manager.get_rincian_summary(transaksi_id, 'LBR_REQ')
                if summary:
                    self._uang_muka_nilai = summary.get('uang_muka_nilai', 0) or summary.get('total_dengan_ppn', 0)

            if hasattr(self, 'uang_muka_label'):
                self.uang_muka_label.setText(f"Rp {self._uang_muka_nilai:,.0f}".replace(",", "."))
                print(f"Loaded uang_muka for calculation: {self._uang_muka_nilai}")

        except Exception as e:
            self._uang_muka_nilai = 0
            print(f"Error loading uang_muka for calculation: {e}")

    def _update_jumlah_preview(self, *args):
        """Auto-calculate and display jumlah preview when volume or harga changes."""
        if hasattr(self, 'volume_spin') and hasattr(self, 'harga_spin') and hasattr(self, 'jumlah_preview'):
            volume = self.volume_spin.value()
            harga = self.harga_spin.value()
            jumlah = volume * harga
            self.jumlah_preview.setText(f"Rp {jumlah:,.0f}".replace(",", "."))

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

        # Clear inputs and reset preview
        self.uraian_edit.clear()
        self.volume_spin.setValue(1)
        self.harga_spin.setValue(0)
        if hasattr(self, 'jumlah_preview'):
            self.jumlah_preview.setText("Rp 0")

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

    def _update_total(self, *args):
        """Update total label with PPN, PPh, and calculation panel."""
        total = sum(item['jumlah'] for item in self.rincian_items)
        self.total_label.setText(f"Rp {total:,.0f}".replace(",", "."))

        # Calculate PPN if checkbox exists and is checked
        ppn_nilai = 0
        if hasattr(self, 'ppn_checkbox') and self.ppn_checkbox.isChecked():
            ppn_nilai = total * 0.11  # 11%
            self.ppn_label.setText(f"Rp {ppn_nilai:,.0f}".replace(",", "."))
        elif hasattr(self, 'ppn_label'):
            self.ppn_label.setText("Rp 0")

        # Calculate PPh if checkbox exists and is checked
        pph_nilai = 0
        if hasattr(self, 'pph_checkbox'):
            self.pph_rate_combo.setEnabled(self.pph_checkbox.isChecked())
            if self.pph_checkbox.isChecked():
                # Parse rate from combo text
                rate_text = self.pph_rate_combo.currentText()
                if "1.5%" in rate_text:
                    pph_rate = 0.015
                elif "2%" in rate_text:
                    pph_rate = 0.02
                elif "4%" in rate_text:
                    pph_rate = 0.04
                elif "15%" in rate_text:
                    pph_rate = 0.15
                else:
                    pph_rate = 0.02  # default
                pph_nilai = total * pph_rate
                self.pph_label.setText(f"Rp {pph_nilai:,.0f}".replace(",", "."))
            else:
                self.pph_label.setText("Rp 0")

        # Grand total = total + PPN - PPh (PPh is a deduction)
        grand_total = total + ppn_nilai - pph_nilai

        if hasattr(self, 'grand_total_label'):
            self.grand_total_label.setText(f"Rp {grand_total:,.0f}".replace(",", "."))

        # Calculate uang muka percentage (for KUIT_UM)
        if hasattr(self, 'um_btn_group'):
            persen = self.um_btn_group.checkedId()
            if persen > 0:
                nilai_diterima = grand_total * persen / 100
                self.um_nilai_label.setText(f"Nilai Diterima: Rp {nilai_diterima:,.0f}".replace(",", "."))

        # Update calculation panel (for REKAP_BKT)
        if hasattr(self, 'realisasi_label') and hasattr(self, 'selisih_label'):
            self.realisasi_label.setText(f"Rp {grand_total:,.0f}".replace(",", "."))

            # Calculate selisih
            uang_muka = getattr(self, '_uang_muka_nilai', 0) or 0
            selisih = grand_total - uang_muka

            self.selisih_label.setText(f"Rp {abs(selisih):,.0f}".replace(",", "."))

            # Styling constants
            base_status_style = "font-weight: bold; font-size: 14px; padding: 10px 20px; border-radius: 6px; margin-top: 5px;"
            base_selisih_style = "font-weight: bold; font-size: 16px; padding: 5px;"

            # Update status
            if selisih > 0:
                self.status_calc_label.setText("⚠ KURANG BAYAR")
                self.status_calc_label.setStyleSheet(base_status_style + "background-color: #e74c3c; color: white;")
                self.selisih_label.setStyleSheet(base_selisih_style + "color: #e74c3c;")
            elif selisih < 0:
                self.status_calc_label.setText("✓ LEBIH BAYAR (Kembali ke Kas)")
                self.status_calc_label.setStyleSheet(base_status_style + "background-color: #27ae60; color: white;")
                self.selisih_label.setStyleSheet(base_selisih_style + "color: #27ae60;")
            else:
                self.status_calc_label.setText("✓ NIHIL")
                self.status_calc_label.setStyleSheet(base_status_style + "background-color: #3498db; color: white;")
                self.selisih_label.setStyleSheet(base_selisih_style + "color: #3498db;")

    def _collect_data(self) -> Dict[str, Any]:
        """Collect all form data."""
        # Get nama from combo - extract name without NIP
        selected_text = self.penerima_nama_combo.currentText().strip()
        # If format is "Nama (NIP)", extract just the name
        if ' (' in selected_text and selected_text.endswith(')'):
            penerima_nama = selected_text.rsplit(' (', 1)[0].strip()
        else:
            penerima_nama = selected_text

        data = {
            'nama_kegiatan': self.nama_kegiatan_edit.text(),
            'kode_akun': self.kode_akun_edit.text(),
            'tanggal_dokumen': self.tanggal_edit.date().toString("yyyy-MM-dd"),
            'penerima_nama': penerima_nama,
            'penerima_nip': self.penerima_nip_edit.text(),
            'penerima_jabatan': self.penerima_jabatan_edit.text(),
        }

        # Add PPh data if exists
        if hasattr(self, 'pph_checkbox') and self.pph_checkbox.isChecked():
            rate_text = self.pph_rate_combo.currentText()
            if "1.5%" in rate_text:
                data['pph_persen'] = 1.5
            elif "2%" in rate_text:
                data['pph_persen'] = 2
            elif "4%" in rate_text:
                data['pph_persen'] = 4
            elif "15%" in rate_text:
                data['pph_persen'] = 15
            else:
                data['pph_persen'] = 0
        else:
            data['pph_persen'] = 0

        # Add PPN percentage if checkbox exists and is checked
        if hasattr(self, 'ppn_checkbox') and self.ppn_checkbox.isChecked():
            data['ppn_persen'] = 11
        else:
            data['ppn_persen'] = 0

        # Add uang muka percentage if option exists
        if hasattr(self, 'um_btn_group'):
            data['uang_muka_persen'] = self.um_btn_group.checkedId()
        else:
            data['uang_muka_persen'] = 100

        # Add nomor tanda terima if generated (for KUIT_UM)
        if hasattr(self, '_nomor_tanda_terima') and self._nomor_tanda_terima:
            data['nomor_tanda_terima'] = self._nomor_tanda_terima

        # Add Kuitansi Rampung specific data
        if self.kode_dokumen == 'KUIT_RAMP':
            data['uang_muka'] = getattr(self, '_kr_uang_muka', 0)
            data['realisasi'] = getattr(self, '_kr_realisasi', 0)
            data['selisih'] = getattr(self, '_kr_selisih', 0)
            data['status_selisih'] = getattr(self, '_kr_status', 'NIHIL')
            if hasattr(self, 'kr_klausul_text'):
                data['klausul'] = self.kr_klausul_text.toPlainText()

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

            self.progress_bar.setValue(50)
            self.status_label.setText("Menyimpan data rincian...")

            # Save rincian items to database for documents with rincian
            # LBR_REQ = Lembar Permintaan (estimasi)
            # REKAP_BKT = Rekap Bukti Pengeluaran (realisasi aktual)
            if self.kode_dokumen in ['LBR_REQ', 'REKAP_BKT'] and self.rincian_items:
                self._save_rincian_to_db(form_data)

                # For REKAP_BKT, also update realisasi in transaksi
                if self.kode_dokumen == 'REKAP_BKT':
                    total_realisasi = sum(item.get('jumlah', 0) for item in self.rincian_items)
                    self._update_transaksi_realisasi(total_realisasi)

            # For KUIT_UM, update uang_muka in transaksi based on percentage selected
            if self.kode_dokumen == 'KUIT_UM' and self.rincian_items:
                total = sum(item.get('jumlah', 0) for item in self.rincian_items)
                ppn_persen = form_data.get('ppn_persen', 0)
                ppn_nilai = total * ppn_persen / 100 if ppn_persen > 0 else 0
                grand_total = total + ppn_nilai
                uang_muka_persen = form_data.get('uang_muka_persen', 100)
                uang_muka_nilai = grand_total * uang_muka_persen / 100
                self._update_transaksi_uang_muka(uang_muka_nilai)

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

    def _save_rincian_to_db(self, form_data: Dict[str, Any]):
        """Save rincian items to database."""
        try:
            transaksi_id = self.transaksi.get('id')
            if not transaksi_id:
                print("Warning: No transaksi_id, cannot save rincian")
                return

            from app.models.pencairan_models import PencairanManager
            manager = PencairanManager()

            ppn_persen = form_data.get('ppn_persen', 0)
            uang_muka_persen = form_data.get('uang_muka_persen', 100)

            manager.save_rincian_items(
                transaksi_id=transaksi_id,
                items=self.rincian_items,
                kode_dokumen=self.kode_dokumen,
                ppn_persen=ppn_persen,
                uang_muka_persen=uang_muka_persen
            )
            print(f"Saved {len(self.rincian_items)} rincian items for transaksi {transaksi_id}")

        except Exception as e:
            print(f"Error saving rincian to database: {e}")

    def _update_transaksi_realisasi(self, total_realisasi: float):
        """Update realisasi value in transaksi after saving REKAP_BKT."""
        try:
            transaksi_id = self.transaksi.get('id')
            if not transaksi_id:
                return

            from app.models.pencairan_models import PencairanManager
            manager = PencairanManager()
            manager.update_transaksi(transaksi_id, {'realisasi': total_realisasi})
            print(f"Updated transaksi {transaksi_id} realisasi to {total_realisasi}")

        except Exception as e:
            print(f"Error updating transaksi realisasi: {e}")

    def _update_transaksi_uang_muka(self, uang_muka_nilai: float):
        """Update uang_muka value in transaksi after generating KUIT_UM."""
        try:
            transaksi_id = self.transaksi.get('id')
            if not transaksi_id:
                return

            from app.models.pencairan_models import PencairanManager
            manager = PencairanManager()
            manager.update_transaksi(transaksi_id, {'uang_muka': uang_muka_nilai})
            print(f"Updated transaksi {transaksi_id} uang_muka to {uang_muka_nilai}")

        except Exception as e:
            print(f"Error updating transaksi uang_muka: {e}")

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

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(self.status_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # View file button (hidden initially) - renamed to "Buka"
        self.view_file_btn = QPushButton("Buka")
        self.view_file_btn.setVisible(False)
        self.view_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.view_file_btn.clicked.connect(self._view_file)
        btn_layout.addWidget(self.view_file_btn)

        # Download button (hidden initially)
        self.download_btn = QPushButton("Download")
        self.download_btn.setVisible(False)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.download_btn.clicked.connect(self._download_file)
        btn_layout.addWidget(self.download_btn)

        # Open folder button (hidden initially)
        self.open_folder_btn = QPushButton("Buka Folder")
        self.open_folder_btn.setVisible(False)
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.open_folder_btn.clicked.connect(self._open_folder)
        btn_layout.addWidget(self.open_folder_btn)

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

        self.close_btn = QPushButton("Tutup")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

        # Store uploaded file path
        self.uploaded_path = None

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

            # Store uploaded path
            self.uploaded_path = str(dest)

            # Update UI
            self.status_label.setText(f"✓ File berhasil diupload:\n{dest}")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")

            # Show view buttons
            self.view_file_btn.setVisible(True)
            self.download_btn.setVisible(True)
            self.open_folder_btn.setVisible(True)

            # Change upload button to "Upload Lagi"
            self.upload_btn.setText("Upload Lagi")

            # Emit signal
            self.dokumen_uploaded.emit(str(dest))

        except Exception as e:
            self.status_label.setText(f"✗ Gagal upload: {str(e)}")
            self.status_label.setStyleSheet("color: #e74c3c;")
            QMessageBox.critical(self, "Error", f"Gagal upload file:\n{str(e)}")

    def _view_file(self):
        """Open uploaded file with default application."""
        if self.uploaded_path:
            import subprocess
            import platform
            import os

            try:
                if platform.system() == 'Windows':
                    os.startfile(self.uploaded_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', self.uploaded_path])
                else:  # Linux
                    subprocess.run(['xdg-open', self.uploaded_path])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal membuka file:\n{str(e)}")

    def _open_folder(self):
        """Open folder containing uploaded file."""
        if self.uploaded_path:
            import subprocess
            import platform
            import os
            from pathlib import Path

            folder = str(Path(self.uploaded_path).parent)

            try:
                if platform.system() == 'Windows':
                    os.startfile(folder)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', folder])
                else:  # Linux
                    subprocess.run(['xdg-open', folder])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal membuka folder:\n{str(e)}")

    def _download_file(self):
        """Download/save file to user-selected location."""
        if not self.uploaded_path:
            return

        import os
        import shutil
        from pathlib import Path

        if not os.path.exists(self.uploaded_path):
            QMessageBox.warning(self, "Peringatan", "File tidak ditemukan!")
            return

        # Get original filename
        original_name = Path(self.uploaded_path).name

        # Ask user where to save
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan File",
            original_name,
            "All Files (*)"
        )

        if save_path:
            try:
                shutil.copy2(self.uploaded_path, save_path)
                QMessageBox.information(self, "Sukses", f"File berhasil disimpan:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menyimpan file:\n{str(e)}")
