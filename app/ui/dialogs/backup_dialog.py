"""
PPK DOCUMENT FACTORY - Backup & Restore Dialog
===============================================
Dialog untuk backup dan restore database serta dokumen.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QGroupBox,
    QFileDialog, QMessageBox, QProgressBar,
    QListWidget, QListWidgetItem, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import shutil
import zipfile
import os
import json


class BackupWorker(QThread):
    """Worker thread for backup operation."""
    progress = Signal(int, str)  # percent, message
    finished = Signal(bool, str)  # success, message/path

    def __init__(self, backup_path: str, include_docs: bool = True):
        super().__init__()
        self.backup_path = backup_path
        self.include_docs = include_docs

    def run(self):
        try:
            from app.core.config import ROOT_DIR, DATA_DIR

            self.progress.emit(10, "Mempersiapkan backup...")

            # Create temp folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = Path(ROOT_DIR) / "temp" / f"backup_{timestamp}"
            temp_dir.mkdir(parents=True, exist_ok=True)

            self.progress.emit(20, "Menyalin database...")

            # Copy database
            db_path = DATA_DIR / "pencairan.db"
            if db_path.exists():
                shutil.copy2(db_path, temp_dir / "pencairan.db")

            # Copy settings/config if exists
            config_path = DATA_DIR / "settings.json"
            if config_path.exists():
                shutil.copy2(config_path, temp_dir / "settings.json")

            self.progress.emit(40, "Menyalin dokumen...")

            # Copy documents if requested
            if self.include_docs:
                docs_path = Path(ROOT_DIR) / "output" / "dokumen"
                if docs_path.exists():
                    dest_docs = temp_dir / "dokumen"
                    shutil.copytree(docs_path, dest_docs)

            self.progress.emit(70, "Membuat file backup...")

            # Create backup info
            info = {
                "version": "4.0",
                "created": datetime.now().isoformat(),
                "include_docs": self.include_docs,
            }
            with open(temp_dir / "backup_info.json", "w") as f:
                json.dump(info, f, indent=2)

            self.progress.emit(80, "Mengompres file...")

            # Create zip file
            with zipfile.ZipFile(self.backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)

            self.progress.emit(95, "Membersihkan file sementara...")

            # Cleanup temp
            shutil.rmtree(temp_dir)

            self.progress.emit(100, "Backup selesai!")
            self.finished.emit(True, self.backup_path)

        except Exception as e:
            self.finished.emit(False, str(e))


class RestoreWorker(QThread):
    """Worker thread for restore operation."""
    progress = Signal(int, str)
    finished = Signal(bool, str)

    def __init__(self, backup_path: str, restore_docs: bool = True):
        super().__init__()
        self.backup_path = backup_path
        self.restore_docs = restore_docs

    def run(self):
        try:
            from app.core.config import ROOT_DIR, DATA_DIR

            self.progress.emit(10, "Membaca file backup...")

            # Create temp folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = Path(ROOT_DIR) / "temp" / f"restore_{timestamp}"
            temp_dir.mkdir(parents=True, exist_ok=True)

            self.progress.emit(20, "Mengekstrak file...")

            # Extract zip
            with zipfile.ZipFile(self.backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)

            # Verify backup
            info_path = temp_dir / "backup_info.json"
            if not info_path.exists():
                raise Exception("File backup tidak valid (backup_info.json tidak ditemukan)")

            self.progress.emit(40, "Membackup data lama...")

            # Backup current database
            db_path = DATA_DIR / "pencairan.db"
            if db_path.exists():
                backup_old = db_path.with_suffix(f".db.bak_{timestamp}")
                shutil.copy2(db_path, backup_old)

            self.progress.emit(60, "Memulihkan database...")

            # Restore database
            extracted_db = temp_dir / "pencairan.db"
            if extracted_db.exists():
                shutil.copy2(extracted_db, db_path)

            # Restore settings
            extracted_settings = temp_dir / "settings.json"
            if extracted_settings.exists():
                shutil.copy2(extracted_settings, DATA_DIR / "settings.json")

            self.progress.emit(80, "Memulihkan dokumen...")

            # Restore documents if requested
            if self.restore_docs:
                extracted_docs = temp_dir / "dokumen"
                if extracted_docs.exists():
                    docs_path = Path(ROOT_DIR) / "output" / "dokumen"
                    if docs_path.exists():
                        # Backup old docs
                        old_docs_backup = Path(ROOT_DIR) / "output" / f"dokumen_bak_{timestamp}"
                        shutil.move(str(docs_path), str(old_docs_backup))
                    shutil.copytree(extracted_docs, docs_path)

            self.progress.emit(95, "Membersihkan file sementara...")

            # Cleanup
            shutil.rmtree(temp_dir)

            self.progress.emit(100, "Restore selesai!")
            self.finished.emit(True, "Data berhasil dipulihkan. Silakan restart aplikasi.")

        except Exception as e:
            self.finished.emit(False, str(e))


class BackupRestoreDialog(QDialog):
    """Dialog untuk backup dan restore data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.backup_worker = None
        self.restore_worker = None
        self._setup_ui()
        self._load_backup_history()

    def _setup_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle("Backup & Restore")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header
        header = QLabel("Backup & Restore Data")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        layout.addWidget(header)

        # Info
        info = QLabel(
            "Backup akan menyimpan database dan dokumen yang dihasilkan. "
            "Gunakan restore untuk memulihkan data dari file backup."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #7f8c8d; padding: 5px;")
        layout.addWidget(info)

        # Backup Section
        backup_group = QGroupBox("Backup Data")
        backup_layout = QVBoxLayout(backup_group)

        # Options
        self.include_docs_cb = QCheckBox("Sertakan dokumen yang dihasilkan")
        self.include_docs_cb.setChecked(True)
        backup_layout.addWidget(self.include_docs_cb)

        # Backup button
        backup_btn_layout = QHBoxLayout()
        backup_btn_layout.addStretch()

        self.backup_btn = QPushButton("Buat Backup")
        self.backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        self.backup_btn.clicked.connect(self._do_backup)
        backup_btn_layout.addWidget(self.backup_btn)

        backup_layout.addLayout(backup_btn_layout)
        layout.addWidget(backup_group)

        # Restore Section
        restore_group = QGroupBox("Restore Data")
        restore_layout = QVBoxLayout(restore_group)

        # Restore options
        self.restore_docs_cb = QCheckBox("Pulihkan juga dokumen yang dihasilkan")
        self.restore_docs_cb.setChecked(True)
        restore_layout.addWidget(self.restore_docs_cb)

        # Warning
        warning = QLabel(
            "PERHATIAN: Restore akan menggantikan data yang ada saat ini. "
            "Data lama akan di-backup terlebih dahulu."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #e74c3c; font-style: italic; padding: 5px;")
        restore_layout.addWidget(warning)

        # Restore button
        restore_btn_layout = QHBoxLayout()
        restore_btn_layout.addStretch()

        self.restore_btn = QPushButton("Pilih File & Restore")
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.restore_btn.clicked.connect(self._do_restore)
        restore_btn_layout.addWidget(self.restore_btn)

        restore_layout.addLayout(restore_btn_layout)
        layout.addWidget(restore_group)

        # Progress Section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Siap")
        self.status_label.setStyleSheet("color: #7f8c8d;")
        progress_layout.addWidget(self.status_label)

        layout.addWidget(progress_group)

        # Recent Backups
        history_group = QGroupBox("Backup Terakhir")
        history_layout = QVBoxLayout(history_group)

        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(100)
        self.history_list.itemDoubleClicked.connect(self._open_backup_location)
        history_layout.addWidget(self.history_list)

        layout.addWidget(history_group)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        close_btn = QPushButton("Tutup")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _load_backup_history(self):
        """Load recent backup history."""
        try:
            from app.core.config import ROOT_DIR

            backup_dir = Path(ROOT_DIR) / "backup"
            if backup_dir.exists():
                backups = sorted(backup_dir.glob("*.zip"), key=lambda x: x.stat().st_mtime, reverse=True)
                for backup in backups[:5]:
                    item = QListWidgetItem(f"{backup.name} ({backup.stat().st_size // 1024} KB)")
                    item.setData(Qt.UserRole, str(backup))
                    self.history_list.addItem(item)

            if self.history_list.count() == 0:
                self.history_list.addItem("Belum ada backup")
        except:
            pass

    def _open_backup_location(self, item):
        """Open backup file location."""
        filepath = item.data(Qt.UserRole)
        if filepath:
            import subprocess
            import platform

            folder = str(Path(filepath).parent)
            try:
                if platform.system() == 'Windows':
                    os.startfile(folder)
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', folder])
                else:
                    subprocess.run(['xdg-open', folder])
            except:
                pass

    def _do_backup(self):
        """Start backup process."""
        try:
            from app.core.config import ROOT_DIR

            # Get save path
            backup_dir = Path(ROOT_DIR) / "backup"
            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"ppk_backup_{timestamp}.zip"

            filepath, _ = QFileDialog.getSaveFileName(
                self,
                "Simpan Backup",
                str(backup_dir / default_name),
                "Zip Files (*.zip)"
            )

            if not filepath:
                return

            # Disable buttons
            self.backup_btn.setEnabled(False)
            self.restore_btn.setEnabled(False)

            # Start worker
            self.backup_worker = BackupWorker(
                filepath,
                include_docs=self.include_docs_cb.isChecked()
            )
            self.backup_worker.progress.connect(self._on_progress)
            self.backup_worker.finished.connect(self._on_backup_finished)
            self.backup_worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memulai backup:\n{str(e)}")

    def _do_restore(self):
        """Start restore process."""
        # Confirm
        reply = QMessageBox.question(
            self,
            "Konfirmasi Restore",
            "Apakah Anda yakin ingin memulihkan data dari backup?\n\n"
            "Data saat ini akan di-backup terlebih dahulu sebelum diganti.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Get backup file
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih File Backup",
            "",
            "Zip Files (*.zip)"
        )

        if not filepath:
            return

        # Disable buttons
        self.backup_btn.setEnabled(False)
        self.restore_btn.setEnabled(False)

        # Start worker
        self.restore_worker = RestoreWorker(
            filepath,
            restore_docs=self.restore_docs_cb.isChecked()
        )
        self.restore_worker.progress.connect(self._on_progress)
        self.restore_worker.finished.connect(self._on_restore_finished)
        self.restore_worker.start()

    def _on_progress(self, percent: int, message: str):
        """Handle progress update."""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)

    def _on_backup_finished(self, success: bool, message: str):
        """Handle backup completion."""
        self.backup_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)

        if success:
            self.status_label.setText(f"Backup berhasil: {message}")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")

            # Refresh history
            self.history_list.clear()
            self._load_backup_history()

            QMessageBox.information(
                self,
                "Backup Berhasil",
                f"Data berhasil di-backup ke:\n{message}"
            )
        else:
            self.status_label.setText(f"Backup gagal: {message}")
            self.status_label.setStyleSheet("color: #e74c3c;")
            QMessageBox.critical(self, "Error", f"Backup gagal:\n{message}")

    def _on_restore_finished(self, success: bool, message: str):
        """Handle restore completion."""
        self.backup_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)

        if success:
            self.status_label.setText("Restore berhasil!")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")

            QMessageBox.information(
                self,
                "Restore Berhasil",
                message + "\n\nAplikasi perlu di-restart untuk melihat perubahan."
            )
        else:
            self.status_label.setText(f"Restore gagal: {message}")
            self.status_label.setStyleSheet("color: #e74c3c;")
            QMessageBox.critical(self, "Error", f"Restore gagal:\n{message}")
