"""
PPK DOCUMENT FACTORY - Generate Document Dialog
=================================================
Dialog untuk generate dokumen berdasarkan stage workflow.

Author: PPK Document Factory Team
Version: 4.0
"""

import os
import sys
import json
from datetime import date

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLineEdit, QComboBox, QDateEdit,
    QPushButton, QLabel, QCheckBox, QTabWidget,
    QScrollArea, QWidget, QMessageBox, QProgressBar,
    QListWidget, QListWidgetItem, QFrame, QApplication
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

from app.core.config import (
    TAHUN_ANGGARAN, OUTPUT_DIR, SATKER_DEFAULT,
    WORKFLOW_STAGES, DOCUMENT_TEMPLATES
)
from app.core.database import get_db_manager
from app.workflow.engine import get_workflow_engine


class GenerateDocumentDialog(QDialog):
    """Dialog for generating documents for a stage with complete data input."""

    def __init__(self, paket_id: int, stage_code: str, parent=None):
        super().__init__(parent)
        self.paket_id = paket_id
        self.stage_code = stage_code
        self.db = get_db_manager()
        self.workflow = get_workflow_engine()
        self.paket = self.db.get_paket(paket_id)

        self.setWindowTitle(f"Generate Dokumen - {stage_code}")
        self.setMinimumWidth(800)
        self.setMinimumHeight(700)

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Use tabs for organized input
        self.tabs = QTabWidget()

        # === TAB 1: Dokumen & Tanggal ===
        tab_dokumen = QWidget()
        tab_dokumen_layout = QVBoxLayout(tab_dokumen)

        # Stage info
        info_group = QGroupBox("Informasi Stage")
        info_layout = QFormLayout()

        self.lbl_stage = QLabel()
        info_layout.addRow("Stage:", self.lbl_stage)

        self.lbl_status = QLabel()
        info_layout.addRow("Status:", self.lbl_status)

        info_group.setLayout(info_layout)
        tab_dokumen_layout.addWidget(info_group)

        # Documents to generate with date input
        self.doc_group = QGroupBox("Dokumen yang akan di-generate")
        self.doc_group_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Pilih"))
        header_layout.addWidget(QLabel("Nama Dokumen"), 1)
        header_layout.addWidget(QLabel("Tanggal Dokumen"))
        header_layout.addWidget(QLabel("Nomor (opsional)"))
        self.doc_group_layout.addLayout(header_layout)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        self.doc_group_layout.addWidget(sep)

        self.doc_entries = {}
        self.doc_group.setLayout(self.doc_group_layout)
        tab_dokumen_layout.addWidget(self.doc_group)

        # Quick date set
        quick_date_layout = QHBoxLayout()
        quick_date_layout.addWidget(QLabel("Set tanggal semua:"))
        self.quick_date = QDateEdit()
        self.quick_date.setCalendarPopup(True)
        self.quick_date.setDate(QDate.currentDate())
        self.quick_date.setDisplayFormat("dd MMMM yyyy")
        quick_date_layout.addWidget(self.quick_date)
        btn_apply_date = QPushButton("Terapkan ke Semua")
        btn_apply_date.clicked.connect(self._apply_date_to_all)
        quick_date_layout.addWidget(btn_apply_date)
        quick_date_layout.addStretch()
        tab_dokumen_layout.addLayout(quick_date_layout)

        tab_dokumen_layout.addStretch()
        self.tabs.addTab(tab_dokumen, "📄 Dokumen & Tanggal")

        # === TAB 2: Data Penyedia ===
        tab_penyedia = QWidget()
        tab_penyedia_layout = QVBoxLayout(tab_penyedia)

        # Penyedia selector
        selector_group = QGroupBox("Pilih Penyedia dari Database")
        selector_layout = QHBoxLayout()

        self.cmb_penyedia = QComboBox()
        self.cmb_penyedia.setMinimumWidth(400)
        self.cmb_penyedia.currentIndexChanged.connect(self._on_penyedia_selected)
        selector_layout.addWidget(self.cmb_penyedia, 1)

        btn_refresh_penyedia = QPushButton("🔄")
        btn_refresh_penyedia.setToolTip("Refresh daftar penyedia")
        btn_refresh_penyedia.setFixedWidth(40)
        btn_refresh_penyedia.clicked.connect(self._refresh_penyedia_list)
        selector_layout.addWidget(btn_refresh_penyedia)

        selector_group.setLayout(selector_layout)
        tab_penyedia_layout.addWidget(selector_group)

        penyedia_group = QGroupBox("Data Penyedia/Rekanan")
        penyedia_form = QFormLayout()

        self.txt_penyedia_nama = QLineEdit()
        self.txt_penyedia_nama.setPlaceholderText("PT/CV Nama Perusahaan")
        penyedia_form.addRow("Nama Perusahaan:", self.txt_penyedia_nama)

        self.txt_direktur_nama = QLineEdit()
        self.txt_direktur_nama.setPlaceholderText("Nama lengkap direktur")
        penyedia_form.addRow("Nama Direktur:", self.txt_direktur_nama)

        self.txt_penyedia_alamat = QLineEdit()
        self.txt_penyedia_alamat.setPlaceholderText("Jl. Contoh No. 123, Kota")
        penyedia_form.addRow("Alamat:", self.txt_penyedia_alamat)

        self.txt_penyedia_npwp = QLineEdit()
        self.txt_penyedia_npwp.setPlaceholderText("00.000.000.0-000.000")
        penyedia_form.addRow("NPWP:", self.txt_penyedia_npwp)

        self.txt_penyedia_rekening = QLineEdit()
        self.txt_penyedia_rekening.setPlaceholderText("1234567890")
        penyedia_form.addRow("No. Rekening:", self.txt_penyedia_rekening)

        self.txt_penyedia_bank = QLineEdit()
        self.txt_penyedia_bank.setPlaceholderText("Bank BRI/BNI/Mandiri/dll")
        penyedia_form.addRow("Nama Bank:", self.txt_penyedia_bank)

        self.txt_penyedia_bank_cabang = QLineEdit()
        self.txt_penyedia_bank_cabang.setPlaceholderText("Cabang Sorong")
        penyedia_form.addRow("Cabang Bank:", self.txt_penyedia_bank_cabang)

        penyedia_group.setLayout(penyedia_form)
        tab_penyedia_layout.addWidget(penyedia_group)

        btn_save_penyedia = QPushButton("💾 Simpan Data Penyedia ke Paket")
        btn_save_penyedia.clicked.connect(self._save_penyedia_to_paket)
        tab_penyedia_layout.addWidget(btn_save_penyedia)

        tab_penyedia_layout.addStretch()
        self.tabs.addTab(tab_penyedia, "🏢 Data Penyedia")

        # === TAB 3: Data Satker ===
        tab_satker = QWidget()
        tab_satker_layout = QVBoxLayout(tab_satker)

        satker_group = QGroupBox("Data Satuan Kerja")
        satker_form = QFormLayout()

        self.txt_kementerian = QLineEdit()
        self.txt_kementerian.setText("KEMENTERIAN KELAUTAN DAN PERIKANAN")
        satker_form.addRow("Kementerian:", self.txt_kementerian)

        self.txt_eselon1 = QLineEdit()
        self.txt_eselon1.setText("BADAN PENYULUHAN DAN PENGEMBANGAN SDM KP")
        satker_form.addRow("Eselon I:", self.txt_eselon1)

        self.txt_satker_nama = QLineEdit()
        self.txt_satker_nama.setText("POLITEKNIK KELAUTAN DAN PERIKANAN SORONG")
        satker_form.addRow("Nama Satker:", self.txt_satker_nama)

        self.txt_satker_alamat = QLineEdit()
        self.txt_satker_alamat.setText("Jl. Kapitan Pattimura, Tanjung Kasuari")
        satker_form.addRow("Alamat:", self.txt_satker_alamat)

        self.txt_satker_kota = QLineEdit()
        self.txt_satker_kota.setText("Kota Sorong")
        satker_form.addRow("Kota:", self.txt_satker_kota)

        self.txt_satker_telepon = QLineEdit()
        self.txt_satker_telepon.setText("(0951) 321234")
        satker_form.addRow("Telepon:", self.txt_satker_telepon)

        satker_group.setLayout(satker_form)
        tab_satker_layout.addWidget(satker_group)

        # Pejabat section
        pejabat_group = QGroupBox("Pejabat Terkait")
        pejabat_form = QFormLayout()

        self.txt_ppk_nama = QLineEdit()
        pejabat_form.addRow("Nama PPK:", self.txt_ppk_nama)

        self.txt_ppk_nip = QLineEdit()
        pejabat_form.addRow("NIP PPK:", self.txt_ppk_nip)

        self.txt_pp_nama = QLineEdit()
        pejabat_form.addRow("Nama Pejabat Pengadaan:", self.txt_pp_nama)

        self.txt_pp_nip = QLineEdit()
        pejabat_form.addRow("NIP Pejabat Pengadaan:", self.txt_pp_nip)

        pejabat_group.setLayout(pejabat_form)
        tab_satker_layout.addWidget(pejabat_group)

        tab_satker_layout.addStretch()
        self.tabs.addTab(tab_satker, "🏛️ Data Satker")

        layout.addWidget(self.tabs)

        # Progress
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)

        # Results
        self.results_list = QListWidget()
        self.results_list.hide()
        layout.addWidget(self.results_list)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_generate = QPushButton("🖨️ Generate Dokumen")
        self.btn_generate.setObjectName("btnSuccess")
        self.btn_generate.clicked.connect(self._generate_documents)
        btn_layout.addWidget(self.btn_generate)

        self.btn_open_folder = QPushButton("📂 Buka Folder")
        self.btn_open_folder.setObjectName("btnSecondary")
        self.btn_open_folder.clicked.connect(self._open_output_folder)
        self.btn_open_folder.hide()
        btn_layout.addWidget(self.btn_open_folder)

        btn_close = QPushButton("Tutup")
        btn_close.setObjectName("btnSecondary")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def _load_data(self):
        """Load all required data."""
        # Find stage
        stage_config = next((s for s in WORKFLOW_STAGES if s['code'] == self.stage_code), None)
        if not stage_config:
            return

        self.lbl_stage.setText(f"{stage_config['name']} ({self.stage_code})")

        # Check if allowed
        allowed, message = self.workflow.is_stage_allowed(self.paket_id, self.stage_code)
        if allowed:
            self.lbl_status.setText("✅ Dapat diproses")
            self.lbl_status.setStyleSheet("color: #27ae60;")
        else:
            self.lbl_status.setText(f"⚠️ {message}")
            self.lbl_status.setStyleSheet("color: #f39c12;")

        # Add document entries
        for doc_type in stage_config.get('outputs', []):
            template_info = DOCUMENT_TEMPLATES.get(doc_type, {})

            row_layout = QHBoxLayout()

            cb = QCheckBox()
            cb.setChecked(True)
            row_layout.addWidget(cb)

            lbl = QLabel(f"{template_info.get('name', doc_type)}")
            lbl.setMinimumWidth(250)
            row_layout.addWidget(lbl, 1)

            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDate(QDate.currentDate())
            date_edit.setDisplayFormat("dd/MM/yyyy")
            date_edit.setFixedWidth(120)
            row_layout.addWidget(date_edit)

            txt_nomor = QLineEdit()
            txt_nomor.setPlaceholderText("Auto")
            txt_nomor.setFixedWidth(150)
            row_layout.addWidget(txt_nomor)

            self.doc_entries[doc_type] = {
                'checkbox': cb,
                'date': date_edit,
                'nomor': txt_nomor,
                'label': lbl
            }

            self.doc_group_layout.addLayout(row_layout)

        # Load penyedia list
        self._refresh_penyedia_list()
        self._load_penyedia_from_db()
        self._load_satker_data()

    def _apply_date_to_all(self):
        """Apply quick date to all document entries."""
        selected_date = self.quick_date.date()
        for entry in self.doc_entries.values():
            entry['date'].setDate(selected_date)

    def _refresh_penyedia_list(self):
        """Load penyedia list from database."""
        self.cmb_penyedia.clear()
        self.cmb_penyedia.addItem("-- Pilih Penyedia --", None)

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, nama, nama_direktur, alamat, npwp,
                           no_rekening, nama_bank, kota
                    FROM penyedia
                    WHERE is_active = 1
                    ORDER BY nama
                """)
                penyedia_list = cursor.fetchall()

                for p in penyedia_list:
                    self.cmb_penyedia.addItem(f"{p[1]}", {
                        'id': p[0],
                        'nama': p[1],
                        'direktur': p[2] or '',
                        'alamat': p[3] or '',
                        'npwp': p[4] or '',
                        'rekening': p[5] or '',
                        'bank': p[6] or '',
                        'kota': p[7] or ''
                    })
        except Exception as e:
            print(f"Error loading penyedia list: {e}")

    def _on_penyedia_selected(self, index):
        """Fill form when penyedia selected."""
        penyedia_data = self.cmb_penyedia.currentData()
        if penyedia_data and isinstance(penyedia_data, dict):
            self.txt_penyedia_nama.setText(penyedia_data.get('nama', ''))
            self.txt_direktur_nama.setText(penyedia_data.get('direktur', ''))
            self.txt_penyedia_alamat.setText(penyedia_data.get('alamat', ''))
            self.txt_penyedia_npwp.setText(penyedia_data.get('npwp', ''))
            self.txt_penyedia_rekening.setText(penyedia_data.get('rekening', ''))
            self.txt_penyedia_bank.setText(penyedia_data.get('bank', ''))
            self.txt_penyedia_bank_cabang.setText(penyedia_data.get('kota', ''))

    def _load_penyedia_from_db(self):
        """Load penyedia data from paket."""
        if not self.paket:
            return

        penyedia = self.paket.get('penyedia_data', {})
        if isinstance(penyedia, str):
            try:
                penyedia = json.loads(penyedia)
            except:
                penyedia = {}

        if penyedia:
            self.txt_penyedia_nama.setText(penyedia.get('nama', ''))
            self.txt_direktur_nama.setText(penyedia.get('direktur', ''))
            self.txt_penyedia_alamat.setText(penyedia.get('alamat', ''))
            self.txt_penyedia_npwp.setText(penyedia.get('npwp', ''))
            self.txt_penyedia_rekening.setText(penyedia.get('rekening', ''))
            self.txt_penyedia_bank.setText(penyedia.get('bank', ''))
            self.txt_penyedia_bank_cabang.setText(penyedia.get('bank_cabang', ''))

    def _save_penyedia_to_paket(self):
        """Save penyedia data to paket."""
        penyedia_data = {
            'nama': self.txt_penyedia_nama.text(),
            'direktur': self.txt_direktur_nama.text(),
            'alamat': self.txt_penyedia_alamat.text(),
            'npwp': self.txt_penyedia_npwp.text(),
            'rekening': self.txt_penyedia_rekening.text(),
            'bank': self.txt_penyedia_bank.text(),
            'bank_cabang': self.txt_penyedia_bank_cabang.text(),
        }

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE paket SET penyedia_data = ? WHERE id = ?
                """, (json.dumps(penyedia_data), self.paket_id))
                conn.commit()

            QMessageBox.information(self, "Sukses", "Data penyedia berhasil disimpan!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal menyimpan: {str(e)}")

    def _load_satker_data(self):
        """Load satker and pejabat data."""
        self.txt_kementerian.setText(SATKER_DEFAULT.get('kementerian', ''))
        self.txt_eselon1.setText(SATKER_DEFAULT.get('eselon1', ''))
        self.txt_satker_nama.setText(SATKER_DEFAULT.get('nama', ''))
        self.txt_satker_alamat.setText(SATKER_DEFAULT.get('alamat', ''))
        self.txt_satker_kota.setText(SATKER_DEFAULT.get('kota', ''))
        self.txt_satker_telepon.setText(SATKER_DEFAULT.get('telepon', ''))

        if self.paket:
            ppk = self.db.get_paket_pejabat(self.paket_id, 'PPK')
            if ppk:
                self.txt_ppk_nama.setText(ppk.get('nama', ''))
                self.txt_ppk_nip.setText(ppk.get('nip', ''))

            pp = self.db.get_paket_pejabat(self.paket_id, 'PP')
            if pp:
                self.txt_pp_nama.setText(pp.get('nama', ''))
                self.txt_pp_nip.setText(pp.get('nip', ''))

    def _get_additional_data(self) -> dict:
        """Collect all additional data for document generation."""
        data = {}

        # Document-specific dates and nomor
        for doc_type, entry in self.doc_entries.items():
            date_val = entry['date'].date()
            data[f'tanggal_{doc_type.lower()}'] = date(date_val.year(), date_val.month(), date_val.day())
            data[f'tanggal_{doc_type.lower()}_fmt'] = date_val.toString("d MMMM yyyy")

            nomor = entry['nomor'].text().strip()
            if nomor:
                data[f'nomor_{doc_type.lower()}_override'] = nomor

        # Penyedia data
        data['penyedia_nama'] = self.txt_penyedia_nama.text()
        data['direktur_nama'] = self.txt_direktur_nama.text()
        data['penyedia_alamat'] = self.txt_penyedia_alamat.text()
        data['penyedia_npwp'] = self.txt_penyedia_npwp.text()
        data['penyedia_rekening'] = self.txt_penyedia_rekening.text()
        data['penyedia_bank'] = self.txt_penyedia_bank.text()
        data['penyedia_bank_cabang'] = self.txt_penyedia_bank_cabang.text()

        # Satker data
        data['kementerian'] = self.txt_kementerian.text()
        data['eselon1'] = self.txt_eselon1.text()
        data['satker_nama'] = self.txt_satker_nama.text()
        data['satker_alamat'] = self.txt_satker_alamat.text()
        data['satker_kota'] = self.txt_satker_kota.text()
        data['satker_telepon'] = self.txt_satker_telepon.text()

        # Pejabat data
        data['ppk_nama'] = self.txt_ppk_nama.text()
        data['ppk_nip'] = self.txt_ppk_nip.text()
        data['pp_nama'] = self.txt_pp_nama.text()
        data['pp_nip'] = self.txt_pp_nip.text()

        return data

    def _generate_documents(self):
        """Generate selected documents."""
        try:
            # Get selected documents
            selected = [dt for dt, entry in self.doc_entries.items() if entry['checkbox'].isChecked()]

            if not selected:
                QMessageBox.warning(self, "Peringatan", "Pilih minimal satu dokumen!")
                return

            # Validate required data
            if not self.txt_penyedia_nama.text().strip():
                reply = QMessageBox.question(
                    self, "Data Penyedia Kosong",
                    "Data penyedia belum diisi. Lanjutkan generate?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    self.tabs.setCurrentIndex(1)
                    return

            additional_data = self._get_additional_data()

            self.progress.setMaximum(len(selected))
            self.progress.setValue(0)
            self.progress.show()
            self.results_list.clear()
            self.results_list.show()
            self.btn_generate.setEnabled(False)

            QApplication.processEvents()

            results = []
            for i, doc_type in enumerate(selected):
                try:
                    entry = self.doc_entries[doc_type]
                    date_val = entry['date'].date()
                    doc_date = date(date_val.year(), date_val.month(), date_val.day())

                    additional_data[f'tanggal_{doc_type.lower()}'] = doc_date

                    filepath, nomor = self.workflow.generate_document(
                        self.paket_id, doc_type,
                        additional_data=additional_data,
                        force=True
                    )
                    results.append((doc_type, filepath, nomor))

                    item = QListWidgetItem(f"✅ {doc_type}: {nomor}")
                    item.setForeground(QColor("#27ae60"))
                    self.results_list.addItem(item)

                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    results.append((doc_type, None, str(e)))

                    item = QListWidgetItem(f"❌ {doc_type}: {str(e)}")
                    item.setForeground(QColor("#e74c3c"))
                    self.results_list.addItem(item)

                self.progress.setValue(i + 1)
                QApplication.processEvents()

            # Complete stage if all success
            all_success = all(r[1] is not None for r in results)
            if all_success:
                self.workflow.complete_stage(self.paket_id, self.stage_code)

            self.btn_generate.setEnabled(True)
            self.btn_open_folder.show()

            QMessageBox.information(
                self, "Selesai",
                f"Proses selesai!\n"
                f"Berhasil: {sum(1 for r in results if r[1])}\n"
                f"Gagal: {sum(1 for r in results if not r[1])}"
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.btn_generate.setEnabled(True)
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan:\n{str(e)}")

    def _open_output_folder(self):
        """Open the output folder in file explorer."""
        paket = self.db.get_paket(self.paket_id)
        if not paket:
            return

        import re
        paket_folder = f"{paket['kode']}_{paket['nama'][:30]}"
        paket_folder = re.sub(r'[<>:"/\\|?*]', '_', paket_folder)

        folder_path = os.path.join(OUTPUT_DIR, str(TAHUN_ANGGARAN), paket_folder)

        if os.path.exists(folder_path):
            if sys.platform == 'win32':
                os.startfile(folder_path)
            elif sys.platform == 'darwin':
                os.system(f'open "{folder_path}"')
            else:
                os.system(f'xdg-open "{folder_path}"')
        else:
            QMessageBox.warning(self, "Folder tidak ditemukan", f"Folder output belum ada:\n{folder_path}")
