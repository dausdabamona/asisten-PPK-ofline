"""
PPK DOCUMENT FACTORY - DIPA Import Dialog
==========================================
Dialog untuk import data DIPA dari file CSV.

Format CSV yang didukung:
- KDSATKER, KODE_PROGRAM, KODE_KEGIATAN, KODE_OUTPUT
- KODE_AKUN, URAIAN_ITEM, VOLKEG, SATKEG, HARGASAT, TOTAL
- POK_NILAI_1 sampai POK_NILAI_12

Author: PPK Document Factory Team
Version: 4.0
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLineEdit, QPushButton, QLabel,
    QFileDialog, QMessageBox, QProgressBar, QTextEdit,
    QSpinBox, QFrame
)
from PySide6.QtCore import Qt, Signal

from app.core.config import TAHUN_ANGGARAN
from app.core.database import get_db_manager


class DipaImportDialog(QDialog):
    """Dialog for importing DIPA data from CSV."""

    import_completed = Signal(int, int)  # success_count, error_count

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db_manager()
        self.selected_file = None

        self.setWindowTitle("Import Data DIPA")
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)

        self._setup_ui()
        self._load_current_data()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title = QLabel("Import Data DIPA dari CSV")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px 0;
        """)
        layout.addWidget(title)

        # Current data info
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(10, 10, 10, 10)

        self.lbl_current_data = QLabel("Memuat data...")
        self.lbl_current_data.setStyleSheet("color: #7f8c8d;")
        info_layout.addWidget(self.lbl_current_data)

        layout.addWidget(self.info_frame)

        # File selection
        file_group = QGroupBox("Pilih File CSV")
        file_layout = QVBoxLayout()

        # File path row
        path_layout = QHBoxLayout()
        self.txt_file_path = QLineEdit()
        self.txt_file_path.setPlaceholderText("Pilih file CSV...")
        self.txt_file_path.setReadOnly(True)
        path_layout.addWidget(self.txt_file_path, 1)

        btn_browse = QPushButton("Browse...")
        btn_browse.setFixedWidth(100)
        btn_browse.clicked.connect(self._browse_file)
        path_layout.addWidget(btn_browse)

        file_layout.addLayout(path_layout)

        # Format info
        format_label = QLabel("""
<b>Format CSV yang didukung:</b><br/>
Kolom wajib: KODE_AKUN, URAIAN_ITEM<br/>
Kolom opsional: KDSATKER, KODE_PROGRAM, KODE_KEGIATAN, KODE_OUTPUT,
VOLKEG, SATKEG, HARGASAT, TOTAL, POK_NILAI_1 s/d POK_NILAI_12
        """)
        format_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        format_label.setWordWrap(True)
        file_layout.addWidget(format_label)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Options
        options_group = QGroupBox("Opsi Import")
        options_layout = QFormLayout()

        self.spn_tahun = QSpinBox()
        self.spn_tahun.setRange(2020, 2099)
        self.spn_tahun.setValue(TAHUN_ANGGARAN)
        options_layout.addRow("Tahun Anggaran:", self.spn_tahun)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Log output
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(100)
        self.txt_log.setVisible(False)
        self.txt_log.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.txt_log)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_delete = QPushButton("Hapus Data Tahun Ini")
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_delete.clicked.connect(self._delete_data)
        btn_layout.addWidget(self.btn_delete)

        btn_layout.addStretch()

        btn_cancel = QPushButton("Batal")
        btn_cancel.setFixedWidth(100)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        self.btn_import = QPushButton("Import")
        self.btn_import.setFixedWidth(100)
        self.btn_import.setEnabled(False)
        self.btn_import.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.btn_import.clicked.connect(self._do_import)
        btn_layout.addWidget(self.btn_import)

        layout.addLayout(btn_layout)

    def _load_current_data(self):
        """Load and display current DIPA data summary."""
        try:
            summary = self.db.get_dipa_summary(TAHUN_ANGGARAN)
            total_item = summary.get('total_item', 0) or 0
            total_akun = summary.get('total_akun', 0) or 0
            total_pagu = summary.get('total_pagu', 0) or 0

            if total_item > 0:
                pagu_text = f"Rp {total_pagu:,.0f}".replace(',', '.')
                self.lbl_current_data.setText(
                    f"Data DIPA {TAHUN_ANGGARAN}: {total_item} item, "
                    f"{total_akun} kode akun, Total Pagu: {pagu_text}"
                )
                self.lbl_current_data.setStyleSheet("color: #27ae60; font-weight: bold;")
            else:
                self.lbl_current_data.setText(
                    f"Belum ada data DIPA untuk tahun {TAHUN_ANGGARAN}"
                )
                self.lbl_current_data.setStyleSheet("color: #e74c3c;")
        except Exception as e:
            self.lbl_current_data.setText(f"Error: {str(e)}")
            self.lbl_current_data.setStyleSheet("color: #e74c3c;")

    def _browse_file(self):
        """Open file browser dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih File CSV DIPA",
            str(Path.home()),
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            self.selected_file = file_path
            self.txt_file_path.setText(file_path)
            self.btn_import.setEnabled(True)

    def _do_import(self):
        """Perform the import."""
        if not self.selected_file:
            QMessageBox.warning(self, "Error", "Pilih file CSV terlebih dahulu.")
            return

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.txt_log.setVisible(True)
        self.txt_log.clear()
        self.btn_import.setEnabled(False)

        self._log(f"Memulai import dari: {self.selected_file}")
        self._log(f"Tahun Anggaran: {self.spn_tahun.value()}")

        # Do import
        try:
            success, errors, messages = self.db.import_dipa_csv(
                self.selected_file,
                self.spn_tahun.value()
            )

            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

            self._log(f"Import selesai: {success} berhasil, {errors} gagal")

            for msg in messages:
                self._log(f"  - {msg}")

            if success > 0:
                self._log("Import data DIPA berhasil!")
                QMessageBox.information(
                    self,
                    "Import Berhasil",
                    f"Berhasil import {success} data DIPA.\n"
                    f"Error: {errors}"
                )
                self._load_current_data()
                self.import_completed.emit(success, errors)
            else:
                QMessageBox.warning(
                    self,
                    "Import Gagal",
                    f"Tidak ada data yang berhasil diimport.\n"
                    f"Error: {'; '.join(messages)}"
                )

        except Exception as e:
            self._log(f"Error: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Terjadi kesalahan saat import:\n{str(e)}"
            )

        self.btn_import.setEnabled(True)

    def _delete_data(self):
        """Delete all DIPA data for selected year."""
        tahun = self.spn_tahun.value()

        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus semua data DIPA tahun {tahun}?\n\n"
            "Tindakan ini tidak dapat dibatalkan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                deleted = self.db.delete_all_dipa(tahun)
                QMessageBox.information(
                    self,
                    "Berhasil",
                    f"Berhasil menghapus {deleted} data DIPA."
                )
                self._load_current_data()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Gagal menghapus data:\n{str(e)}"
                )

    def _log(self, message: str):
        """Add message to log."""
        self.txt_log.append(message)
