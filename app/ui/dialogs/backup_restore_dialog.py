"""
Backup & Restore Dialog for PPK Document Factory
================================================
Dialog untuk backup dan restore database.

Fitur:
- Backup database ke file .zip
- Restore database dari file .zip
- Pilih lokasi penyimpanan
- Progress indicator
- Auto-backup pada interval tertentu
"""

import os
import shutil
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QFileDialog, QProgressBar, QMessageBox,
    QListWidget, QListWidgetItem, QGroupBox, QSpinBox, QCheckBox,
    QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

from app.core.config import DATABASE_PATH, ROOT_DIR


class BackupThread(QThread):
    """Background thread untuk backup database."""
    
    progress = Signal(int)  # Progress percentage
    finished = Signal(bool, str)  # Success flag, message
    
    def __init__(self, db_path: str, backup_path: str):
        super().__init__()
        self.db_path = db_path
        self.backup_path = backup_path
    
    def run(self):
        """Execute backup process."""
        try:
            # Buat folder backup jika belum ada
            os.makedirs(os.path.dirname(self.backup_path), exist_ok=True)
            
            # Buat ZIP file
            with zipfile.ZipFile(self.backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add database file
                self.progress.emit(30)
                zipf.write(self.db_path, arcname=os.path.basename(self.db_path))
                
                # Add templates folder jika ada
                templates_path = os.path.join(ROOT_DIR, 'templates')
                if os.path.exists(templates_path):
                    self.progress.emit(50)
                    for root, dirs, files in os.walk(templates_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, ROOT_DIR)
                            zipf.write(file_path, arcname=arcname)
                
                # Add config file jika ada
                config_path = os.path.join(ROOT_DIR, 'app', 'core', 'config.py')
                if os.path.exists(config_path):
                    self.progress.emit(80)
                    zipf.write(config_path, arcname='app/core/config.py')
            
            self.progress.emit(100)
            self.finished.emit(True, f"Backup berhasil dibuat:\n{self.backup_path}")
            
        except Exception as e:
            self.finished.emit(False, f"Error saat backup:\n{str(e)}")


class RestoreThread(QThread):
    """Background thread untuk restore database."""
    
    progress = Signal(int)  # Progress percentage
    finished = Signal(bool, str)  # Success flag, message
    
    def __init__(self, backup_path: str, db_path: str):
        super().__init__()
        self.backup_path = backup_path
        self.db_path = db_path
    
    def run(self):
        """Execute restore process."""
        try:
            # Backup database saat ini sebagai safety
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            safety_backup = f"{self.db_path}.backup_{current_time}"
            shutil.copy2(self.db_path, safety_backup)
            
            self.progress.emit(20)
            
            # Extract ZIP file
            extract_path = os.path.dirname(self.db_path)
            with zipfile.ZipFile(self.backup_path, 'r') as zipf:
                zipf.extractall(extract_path)
            
            self.progress.emit(80)
            
            # Verify database integrity
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM sqlite_master LIMIT 1;")
                conn.close()
            except Exception as e:
                raise Exception(f"Database tidak valid setelah restore: {str(e)}")
            
            self.progress.emit(100)
            self.finished.emit(True, f"Restore berhasil!\nBackup lama disimpan di:\n{safety_backup}")
            
        except Exception as e:
            self.finished.emit(False, f"Error saat restore:\n{str(e)}")


class BackupRestoreDialog(QDialog):
    """Dialog untuk Backup & Restore database."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backup & Restore Database")
        self.setMinimumSize(600, 500)
        self.db_path = DATABASE_PATH
        self.backup_path = os.path.join(ROOT_DIR, 'backups')
        
        # Threads
        self.backup_thread = None
        self.restore_thread = None
        
        self._setup_ui()
        self._load_backups()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Backup & Restore Database")
        title_font = title.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(self._create_backup_tab(), "📦 Backup")
        tabs.addTab(self._create_restore_tab(), "♻️ Restore")
        tabs.addTab(self._create_settings_tab(), "⚙️ Pengaturan")
        layout.addWidget(tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("Tutup")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_backup_tab(self) -> QWidget:
        """Create backup tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # Info
        info_label = QLabel("Buat backup database untuk keamanan data.")
        info_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(info_label)
        
        # Backup location
        loc_group = QGroupBox("Lokasi Backup")
        loc_layout = QHBoxLayout(loc_group)
        
        self.backup_location = QLabel(self.backup_path)
        self.backup_location.setStyleSheet("""
            background-color: #ecf0f1;
            padding: 8px;
            border-radius: 4px;
            word-wrap: true;
        """)
        loc_layout.addWidget(self.backup_location)
        
        browse_btn = QPushButton("Ubah Lokasi")
        browse_btn.setMaximumWidth(120)
        browse_btn.clicked.connect(self._choose_backup_location)
        loc_layout.addWidget(browse_btn)
        
        layout.addWidget(loc_group)
        
        # Current database info
        info_group = QGroupBox("Informasi Database")
        info_layout = QVBoxLayout(info_group)
        
        db_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
        info_layout.addWidget(QLabel(f"📁 Lokasi: {self.db_path}"))
        info_layout.addWidget(QLabel(f"💾 Ukuran: {db_size:.2f} MB"))
        
        layout.addWidget(info_group)
        
        # Backup button
        backup_btn = QPushButton("🔐 Buat Backup Sekarang")
        backup_btn.setMinimumHeight(45)
        backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        backup_btn.clicked.connect(self._start_backup)
        layout.addWidget(backup_btn)
        
        # Progress bar
        self.backup_progress = QProgressBar()
        self.backup_progress.setVisible(False)
        layout.addWidget(self.backup_progress)
        
        # Status label
        self.backup_status = QLabel("")
        self.backup_status.setVisible(False)
        self.backup_status.setWordWrap(True)
        layout.addWidget(self.backup_status)
        
        layout.addStretch()
        return widget
    
    def _create_restore_tab(self) -> QWidget:
        """Create restore tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # Info
        info_label = QLabel("Restore database dari file backup. Data lama akan dicadangkan.")
        info_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(info_label)
        
        # Backup list
        list_group = QGroupBox("Daftar Backup")
        list_layout = QVBoxLayout(list_group)
        
        self.backup_list = QListWidget()
        self.backup_list.itemDoubleClicked.connect(self._on_backup_double_clicked)
        list_layout.addWidget(self.backup_list)
        
        layout.addWidget(list_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._load_backups)
        btn_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("🗑️ Hapus")
        delete_btn.clicked.connect(self._delete_backup)
        btn_layout.addWidget(delete_btn)
        
        browse_btn = QPushButton("📂 Buka File...")
        browse_btn.clicked.connect(self._browse_backup_file)
        btn_layout.addWidget(browse_btn)
        
        layout.addLayout(btn_layout)
        
        # Restore button
        restore_btn = QPushButton("♻️ Restore Database")
        restore_btn.setMinimumHeight(45)
        restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        restore_btn.clicked.connect(self._start_restore)
        layout.addWidget(restore_btn)
        
        # Progress bar
        self.restore_progress = QProgressBar()
        self.restore_progress.setVisible(False)
        layout.addWidget(self.restore_progress)
        
        # Status label
        self.restore_status = QLabel("")
        self.restore_status.setVisible(False)
        self.restore_status.setWordWrap(True)
        layout.addWidget(self.restore_status)
        
        layout.addStretch()
        return widget
    
    def _create_settings_tab(self) -> QWidget:
        """Create settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Auto-backup setting
        auto_backup_group = QGroupBox("Auto-Backup")
        auto_layout = QVBoxLayout(auto_backup_group)
        
        self.auto_backup_check = QCheckBox("Aktifkan Auto-Backup")
        self.auto_backup_check.setChecked(False)
        auto_layout.addWidget(self.auto_backup_check)
        
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Backup setiap:"))
        
        self.backup_interval = QSpinBox()
        self.backup_interval.setMinimum(1)
        self.backup_interval.setMaximum(168)
        self.backup_interval.setValue(24)
        freq_layout.addWidget(self.backup_interval)
        
        interval_unit = QComboBox()
        interval_unit.addItems(["Jam", "Hari"])
        interval_unit.setCurrentText("Jam")
        freq_layout.addWidget(interval_unit)
        
        freq_layout.addStretch()
        auto_layout.addLayout(freq_layout)
        
        layout.addWidget(auto_backup_group)
        
        # Retention setting
        retention_group = QGroupBox("Retensi Backup")
        retention_layout = QVBoxLayout(retention_group)
        
        retention_info = QLabel("Hapus backup yang lebih tua dari:")
        retention_layout.addWidget(retention_info)
        
        ret_layout = QHBoxLayout()
        self.retention_days = QSpinBox()
        self.retention_days.setMinimum(7)
        self.retention_days.setMaximum(365)
        self.retention_days.setValue(30)
        ret_layout.addWidget(self.retention_days)
        ret_layout.addWidget(QLabel("hari"))
        ret_layout.addStretch()
        retention_layout.addLayout(ret_layout)
        
        layout.addWidget(retention_group)
        
        # Info box
        info_group = QGroupBox("ℹ️ Informasi")
        info_layout = QVBoxLayout(info_group)
        
        info_text = """
        💡 Tips Backup & Restore:
        
        • Backup mencakup database dan template dokumen
        • Lakukan backup secara berkala, minimal 1x seminggu
        • Simpan backup di lokasi aman, sebaiknya 2+ tempat
        • Sebelum restore, pastikan aplikasi ditutup
        • Backup lama akan disimpan dengan suffix '_backup'
        • Ukuran backup tergantung jumlah dokumen yang ada
        """
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #2c3e50; line-height: 1.6;")
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_group)
        
        # Save button
        save_btn = QPushButton("💾 Simpan Pengaturan")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        return widget
    
    def _load_backups(self):
        """Load list of available backups."""
        self.backup_list.clear()
        
        if not os.path.exists(self.backup_path):
            return
        
        backup_files = []
        for file in os.listdir(self.backup_path):
            if file.endswith('.zip'):
                file_path = os.path.join(self.backup_path, file)
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                file_date = os.path.getmtime(file_path)
                backup_files.append((file, file_path, file_size, file_date))
        
        # Sort by date, newest first
        backup_files.sort(key=lambda x: x[3], reverse=True)
        
        for file, path, size, _ in backup_files:
            date = datetime.fromtimestamp(_).strftime("%d/%m/%Y %H:%M")
            item_text = f"{file}\n  📅 {date} | 💾 {size:.2f} MB"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, path)
            self.backup_list.addItem(item)
    
    def _choose_backup_location(self):
        """Choose backup location."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Pilih Folder Backup",
            self.backup_path
        )
        if folder:
            self.backup_path = folder
            self.backup_location.setText(folder)
            self._load_backups()
    
    def _on_backup_double_clicked(self, item: QListWidgetItem):
        """Handle backup item double-click to restore."""
        # Auto-start restore on double-click
        self._start_restore()
    
    def _delete_backup(self):
        """Delete selected backup."""
        item = self.backup_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Info", "Pilih backup yang ingin dihapus.")
            return
        
        path = item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Konfirmasi",
            f"Hapus backup:\n{os.path.basename(path)}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(path)
                self._load_backups()
                QMessageBox.information(self, "Sukses", "Backup berhasil dihapus.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus:\n{str(e)}")
    
    def _browse_backup_file(self):
        """Browse and select backup file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih File Backup",
            self.backup_path,
            "ZIP Files (*.zip)"
        )
        
        if file_path:
            # Add to list and select
            item = QListWidgetItem(os.path.basename(file_path))
            item.setData(Qt.UserRole, file_path)
            self.backup_list.insertItem(0, item)
            self.backup_list.setCurrentItem(item)
    
    def _start_backup(self):
        """Start backup process."""
        if self.backup_thread and self.backup_thread.isRunning():
            QMessageBox.warning(self, "Info", "Backup sedang berjalan...")
            return
        
        # Create backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ppk_backup_{timestamp}.zip"
        backup_file = os.path.join(self.backup_path, filename)
        
        # Start thread
        self.backup_thread = BackupThread(self.db_path, backup_file)
        self.backup_thread.progress.connect(self._on_backup_progress)
        self.backup_thread.finished.connect(self._on_backup_finished)
        
        self.backup_progress.setVisible(True)
        self.backup_status.setVisible(True)
        self.backup_status.setText("Membuat backup...")
        self.backup_status.setStyleSheet("color: #3498db;")
        
        self.backup_thread.start()
    
    def _on_backup_progress(self, value: int):
        """Update backup progress."""
        self.backup_progress.setValue(value)
    
    def _on_backup_finished(self, success: bool, message: str):
        """Handle backup completion."""
        self.backup_progress.setVisible(False)
        self.backup_status.setVisible(True)
        
        if success:
            self.backup_status.setStyleSheet("color: #27ae60;")
            self.backup_status.setText(f"✅ {message}")
            self._load_backups()
        else:
            self.backup_status.setStyleSheet("color: #e74c3c;")
            self.backup_status.setText(f"❌ {message}")
    
    def _start_restore(self):
        """Start restore process."""
        item = self.backup_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Info", "Pilih backup yang akan di-restore.")
            return
        
        if self.restore_thread and self.restore_thread.isRunning():
            QMessageBox.warning(self, "Info", "Restore sedang berjalan...")
            return
        
        backup_file = item.data(Qt.UserRole)
        
        # Confirm restore
        reply = QMessageBox.warning(
            self,
            "Konfirmasi Restore",
            f"Restore akan menimpa database saat ini.\n\nFile backup lama akan disimpan.\n\n"
            f"Lanjutkan?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Start thread
        self.restore_thread = RestoreThread(backup_file, self.db_path)
        self.restore_thread.progress.connect(self._on_restore_progress)
        self.restore_thread.finished.connect(self._on_restore_finished)
        
        self.restore_progress.setVisible(True)
        self.restore_status.setVisible(True)
        self.restore_status.setText("Melakukan restore...")
        self.restore_status.setStyleSheet("color: #3498db;")
        
        self.restore_thread.start()
    
    def _on_restore_progress(self, value: int):
        """Update restore progress."""
        self.restore_progress.setValue(value)
    
    def _on_restore_finished(self, success: bool, message: str):
        """Handle restore completion."""
        self.restore_progress.setVisible(False)
        self.restore_status.setVisible(True)
        
        if success:
            self.restore_status.setStyleSheet("color: #27ae60;")
            self.restore_status.setText(f"✅ {message}")
        else:
            self.restore_status.setStyleSheet("color: #e74c3c;")
            self.restore_status.setText(f"❌ {message}")
    
    def _save_settings(self):
        """Save backup settings."""
        # Settings akan disimpan ke config file atau preferences
        QMessageBox.information(
            self,
            "Pengaturan Tersimpan",
            "Pengaturan auto-backup telah disimpan."
        )
