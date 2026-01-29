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

# Import RincianKalkulasiWidget
from app.ui.components.rincian_kalkulasi_widget import RincianKalkulasiWidget


class DokumenGeneratorDialog(QDialog):
    """Dialog untuk generate dokumen dari template."""

    dokumen_generated = Signal(str)  # filepath

    def __init__(self, transaksi: Dict[str, Any], kode_dokumen: str,
                 template_name: str, nama_dokumen: str = None,
                 satker: Dict[str, Any] = None,
                 additional_data: Dict[str, Any] = None,
                 db_manager=None, parent=None):
        super().__init__(parent)
        self.transaksi = transaksi
        self.kode_dokumen = kode_dokumen
        self.nama_dokumen = nama_dokumen or kode_dokumen
        self.template_name = template_name
        self.satker = satker or {}
        self.additional_data = additional_data or {}
        self.rincian_items = self.additional_data.get('rincian_items', [])
        self.db_manager = db_manager  # For saving rincian to database
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
        data_layout.setSpacing(10)

        # Nama Kegiatan
        data_layout.addWidget(QLabel("Nama Kegiatan:"), 0, 0)
        self.nama_kegiatan_edit = QLineEdit()
        self.nama_kegiatan_edit.setText(self.transaksi.get('nama_kegiatan', ''))
        data_layout.addWidget(self.nama_kegiatan_edit, 0, 1)

        # Kode Akun/MAK
        data_layout.addWidget(QLabel("Kode Akun/MAK:"), 1, 0)
        self.kode_akun_edit = QLineEdit()
        self.kode_akun_edit.setText(self.transaksi.get('kode_akun', ''))
        data_layout.addWidget(self.kode_akun_edit, 1, 1)

        # Nilai/Estimasi
        data_layout.addWidget(QLabel("Estimasi Biaya:"), 2, 0)
        self.estimasi_spin = QDoubleSpinBox()
        self.estimasi_spin.setRange(0, 999999999999)
        self.estimasi_spin.setDecimals(0)
        self.estimasi_spin.setPrefix("Rp ")
        self.estimasi_spin.setGroupSeparatorShown(True)
        self.estimasi_spin.setValue(self.transaksi.get('estimasi_biaya', 0))
        data_layout.addWidget(self.estimasi_spin, 2, 1)

        # Tanggal
        data_layout.addWidget(QLabel("Tanggal:"), 3, 0)
        self.tanggal_edit = QDateEdit()
        self.tanggal_edit.setDate(QDate.currentDate())
        self.tanggal_edit.setCalendarPopup(True)
        data_layout.addWidget(self.tanggal_edit, 3, 1)

        # Penerima
        data_layout.addWidget(QLabel("Nama Penerima:"), 4, 0)
        self.penerima_nama_edit = QLineEdit()
        self.penerima_nama_edit.setText(self.transaksi.get('penerima_nama', ''))
        data_layout.addWidget(self.penerima_nama_edit, 4, 1)

        data_layout.addWidget(QLabel("NIP Penerima:"), 5, 0)
        self.penerima_nip_edit = QLineEdit()
        self.penerima_nip_edit.setText(self.transaksi.get('penerima_nip', ''))
        data_layout.addWidget(self.penerima_nip_edit, 5, 1)

        data_layout.addWidget(QLabel("Jabatan:"), 6, 0)
        self.penerima_jabatan_edit = QLineEdit()
        self.penerima_jabatan_edit.setText(self.transaksi.get('penerima_jabatan', ''))
        data_layout.addWidget(self.penerima_jabatan_edit, 6, 1)

        scroll_layout.addWidget(data_group)

        # Rincian widget (for LBR_REQ, KUIT_UM, KUIT_RAMP)
        self.rincian_widget = None
        if self.kode_dokumen in ['LBR_REQ', 'KUIT_UM', 'KUIT_RAMP']:
            # Determine mode based on document type
            if self.kode_dokumen == 'LBR_REQ':
                # Full editable mode for Lembar Permintaan
                self.rincian_widget = RincianKalkulasiWidget(
                    title="Rincian Barang/Jasa",
                    editable=True,
                    inline_edit=False
                )
            elif self.kode_dokumen == 'KUIT_UM':
                # Readonly mode for Kuitansi Uang Muka - shows items from LBR_REQ
                self.rincian_widget = RincianKalkulasiWidget(
                    title="Rincian Barang/Jasa (dari Lembar Permintaan)",
                    editable=False,
                    inline_edit=False
                )
                self.rincian_widget.set_readonly(True)
            elif self.kode_dokumen == 'KUIT_RAMP':
                # Inline edit mode for Kuitansi Rampung
                self.rincian_widget = RincianKalkulasiWidget(
                    title="Rincian Barang/Jasa (edit volume/harga)",
                    editable=True,
                    inline_edit=True
                )
                self.rincian_widget.set_inline_edit(True)

            # Connect total_changed signal to update estimasi
            self.rincian_widget.total_changed.connect(self._on_rincian_total_changed)

            scroll_layout.addWidget(self.rincian_widget)

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

    def _load_data(self):
        """Load initial data including pre-filled rincian items."""
        # For KUIT_UM and KUIT_RAMP, load rincian from database
        if self.rincian_widget and self.db_manager and self.kode_dokumen in ['KUIT_UM', 'KUIT_RAMP']:
            transaksi_id = self.transaksi.get('id')
            if transaksi_id:
                try:
                    self.rincian_widget.load_from_db(self.db_manager, transaksi_id)
                    return
                except Exception as e:
                    print(f"Warning: Gagal memuat rincian dari database: {e}")

        # Load rincian items into widget if provided (fallback or for LBR_REQ)
        if self.rincian_items and self.rincian_widget:
            self.rincian_widget.set_items(self.rincian_items)

    def _on_rincian_total_changed(self, total: float):
        """Handle rincian total change - update estimasi biaya."""
        if hasattr(self, 'estimasi_spin'):
            self.estimasi_spin.setValue(total)

    def _collect_data(self) -> Dict[str, Any]:
        """Collect all form data."""
        data = {
            'nama_kegiatan': self.nama_kegiatan_edit.text(),
            'kode_akun': self.kode_akun_edit.text(),
            'estimasi_biaya': self.estimasi_spin.value(),
            'tanggal_dokumen': self.tanggal_edit.date().toString("yyyy-MM-dd"),
            'penerima_nama': self.penerima_nama_edit.text(),
            'penerima_nip': self.penerima_nip_edit.text(),
            'penerima_jabatan': self.penerima_jabatan_edit.text(),
        }

        # Get rincian data from widget if available
        if self.rincian_widget:
            kuitansi_data = self.rincian_widget.get_data_for_kuitansi()
            data['rincian_items'] = self.rincian_widget.get_items()
            data['rincian_total'] = kuitansi_data.get('total', 0)
            data['rincian_total_rupiah'] = kuitansi_data.get('total_rupiah', 'Rp 0')
            data['rincian_total_terbilang'] = kuitansi_data.get('total_terbilang', 'nol rupiah')
            data['jumlah_item'] = kuitansi_data.get('jumlah_item', 0)

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

            # Get rincian items from widget if available
            rincian_items = None
            if self.rincian_widget:
                rincian_items = self.rincian_widget.get_items()

            # Generate document
            output_path, error = generator.generate_document(
                transaksi=merged_transaksi,
                kode_dokumen=self.kode_dokumen,
                template_name=self.template_name,
                satker=self.satker,
                rincian=rincian_items if rincian_items else self.rincian_items,
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

                # Save rincian to database if we have db_manager and items
                if self.db_manager and self.rincian_widget and self.kode_dokumen == 'LBR_REQ':
                    transaksi_id = self.transaksi.get('id')
                    if transaksi_id:
                        try:
                            self.rincian_widget.save_to_db(self.db_manager, transaksi_id)
                        except Exception as db_err:
                            print(f"Warning: Gagal menyimpan rincian ke database: {db_err}")

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
