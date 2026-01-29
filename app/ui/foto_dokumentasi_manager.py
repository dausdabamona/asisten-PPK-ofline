"""
PPK DOCUMENT FACTORY - Foto Dokumentasi Manager
================================================
Fitur:
1. Upload foto dengan ekstraksi metadata EXIF (GPS, timestamp)
2. Kategorisasi foto (0%, 50%, 100%, Before, During, After)
3. Tagging lokasi dan waktu
4. Watermark otomatis dengan info paket
5. Generate laporan foto dokumentasi
"""

import os
import shutil
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QComboBox, QFileDialog,
    QMessageBox, QProgressBar, QFrame, QScrollArea,
    QTextEdit, QDialog, QDialogButtonBox, QLineEdit,
    QSpinBox, QDoubleSpinBox, QCheckBox, QListWidget,
    QListWidgetItem, QSplitter, QTabWidget
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QColor, QPixmap, QImage, QPainter, QIcon

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db_manager


# =============================================================================
# KONFIGURASI
# =============================================================================

FOTO_KATEGORI = {
    'PROGRESS_0': ('Progress 0%', 'Kondisi Awal', '#e74c3c'),
    'PROGRESS_50': ('Progress 50%', 'Proses Pengerjaan', '#f39c12'),
    'PROGRESS_100': ('Progress 100%', 'Pekerjaan Selesai', '#27ae60'),
    'BEFORE': ('Sebelum', 'Kondisi Sebelum Pekerjaan', '#3498db'),
    'DURING': ('Selama', 'Proses Pengerjaan', '#9b59b6'),
    'AFTER': ('Sesudah', 'Kondisi Setelah Pekerjaan', '#1abc9c'),
    'DETAIL': ('Detail', 'Foto Detail/Close-up', '#34495e'),
    'OVERVIEW': ('Overview', 'Foto Keseluruhan/Wide', '#95a5a6'),
    'LABEL': ('Label/Merk', 'Label Produk/Spesifikasi', '#e67e22'),
    'SERTIFIKAT': ('Sertifikat', 'Sertifikat/Garansi', '#16a085'),
}

JENIS_DOKUMENTASI = {
    'BAHP': 'Berita Acara Hasil Pemeriksaan',
    'BAST': 'Berita Acara Serah Terima',
    'PROGRESS': 'Laporan Progress',
    'SURVEY': 'Survey Lapangan',
    'INSTALASI': 'Dokumentasi Instalasi',
    'LAINNYA': 'Dokumentasi Lainnya',
}


# =============================================================================
# DATA CLASS
# =============================================================================

@dataclass
class FotoMetadata:
    """Metadata foto dari EXIF"""
    filepath: str
    filename: str
    width: int = 0
    height: int = 0
    datetime_taken: datetime = None
    latitude: float = None
    longitude: float = None
    altitude: float = None
    camera_make: str = None
    camera_model: str = None
    orientation: int = 1

    @property
    def has_gps(self) -> bool:
        return self.latitude is not None and self.longitude is not None

    @property
    def gps_string(self) -> str:
        if self.has_gps:
            return f"{self.latitude:.6f}, {self.longitude:.6f}"
        return "Tidak tersedia"

    @property
    def datetime_string(self) -> str:
        if self.datetime_taken:
            return self.datetime_taken.strftime("%d/%m/%Y %H:%M:%S")
        return "Tidak tersedia"


# =============================================================================
# EXIF EXTRACTOR
# =============================================================================

def extract_exif_metadata(filepath: str) -> FotoMetadata:
    """Ekstrak metadata EXIF dari foto"""
    metadata = FotoMetadata(filepath=filepath, filename=os.path.basename(filepath))

    try:
        # Coba gunakan PIL/Pillow untuk EXIF
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS

        img = Image.open(filepath)
        metadata.width, metadata.height = img.size

        exif_data = img._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)

                if tag == 'DateTimeOriginal':
                    try:
                        metadata.datetime_taken = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    except:
                        pass
                elif tag == 'Make':
                    metadata.camera_make = value
                elif tag == 'Model':
                    metadata.camera_model = value
                elif tag == 'Orientation':
                    metadata.orientation = value
                elif tag == 'GPSInfo':
                    gps_info = {}
                    for gps_tag_id, gps_value in value.items():
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_info[gps_tag] = gps_value

                    # Extract GPS coordinates
                    if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                        lat = gps_info['GPSLatitude']
                        lat_ref = gps_info.get('GPSLatitudeRef', 'N')
                        lon = gps_info['GPSLongitude']
                        lon_ref = gps_info.get('GPSLongitudeRef', 'E')

                        # Convert to decimal degrees
                        metadata.latitude = convert_to_degrees(lat)
                        if lat_ref == 'S':
                            metadata.latitude = -metadata.latitude

                        metadata.longitude = convert_to_degrees(lon)
                        if lon_ref == 'W':
                            metadata.longitude = -metadata.longitude

                        if 'GPSAltitude' in gps_info:
                            metadata.altitude = float(gps_info['GPSAltitude'])

        img.close()

    except ImportError:
        # PIL tidak tersedia, gunakan fallback
        try:
            img = QImage(filepath)
            if not img.isNull():
                metadata.width = img.width()
                metadata.height = img.height()
        except:
            pass
    except Exception as e:
        print(f"Error extracting EXIF: {e}")

    # Fallback: gunakan waktu modifikasi file jika tidak ada EXIF datetime
    if metadata.datetime_taken is None:
        try:
            mtime = os.path.getmtime(filepath)
            metadata.datetime_taken = datetime.fromtimestamp(mtime)
        except:
            metadata.datetime_taken = datetime.now()

    return metadata


def convert_to_degrees(value) -> float:
    """Convert GPS coordinates to decimal degrees"""
    try:
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    except:
        return 0.0


# =============================================================================
# FOTO ITEM WIDGET
# =============================================================================

class FotoItemWidget(QFrame):
    """Widget untuk menampilkan satu foto dengan metadata"""

    clicked = Signal(int)  # foto_id
    delete_requested = Signal(int)  # foto_id

    def __init__(self, foto_data: Dict, parent=None):
        super().__init__(parent)
        self.foto_data = foto_data
        self.foto_id = foto_data.get('id', 0)
        self.init_ui()

    def init_ui(self):
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            FotoItemWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 5px;
            }
            FotoItemWidget:hover {
                border: 2px solid #3498db;
            }
        """)
        self.setFixedSize(200, 250)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Thumbnail
        thumbnail_label = QLabel()
        thumbnail_label.setFixedSize(180, 135)
        thumbnail_label.setAlignment(Qt.AlignCenter)
        thumbnail_label.setStyleSheet("background-color: #f8f9fa; border-radius: 4px;")

        filepath = self.foto_data.get('filepath', '')
        if filepath and os.path.exists(filepath):
            pixmap = QPixmap(filepath)
            if not pixmap.isNull():
                scaled = pixmap.scaled(180, 135, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                thumbnail_label.setPixmap(scaled)
            else:
                thumbnail_label.setText("📷")
        else:
            thumbnail_label.setText("📷 No Image")

        layout.addWidget(thumbnail_label)

        # Kategori badge
        kategori = self.foto_data.get('kategori', 'LAINNYA')
        kat_info = FOTO_KATEGORI.get(kategori, ('Lainnya', '', '#95a5a6'))

        kat_label = QLabel(kat_info[0])
        kat_label.setAlignment(Qt.AlignCenter)
        kat_label.setStyleSheet(f"""
            QLabel {{
                background-color: {kat_info[2]};
                color: white;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(kat_label)

        # Info
        info_text = []

        # Waktu
        waktu = self.foto_data.get('waktu_foto')
        if waktu:
            if isinstance(waktu, str):
                info_text.append(f"📅 {waktu[:10]}")
            else:
                info_text.append(f"📅 {waktu.strftime('%d/%m/%Y')}")

        # GPS
        lat = self.foto_data.get('latitude')
        lon = self.foto_data.get('longitude')
        if lat and lon:
            info_text.append(f"📍 GPS OK")

        info_label = QLabel(" | ".join(info_text) if info_text else "No metadata")
        info_label.setStyleSheet("color: #6c757d; font-size: 9px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        # Keterangan (truncated)
        keterangan = self.foto_data.get('keterangan', '')[:30]
        if keterangan:
            ket_label = QLabel(keterangan + "..." if len(self.foto_data.get('keterangan', '')) > 30 else keterangan)
            ket_label.setStyleSheet("color: #495057; font-size: 10px;")
            ket_label.setAlignment(Qt.AlignCenter)
            ket_label.setWordWrap(True)
            layout.addWidget(ket_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.foto_id)
        super().mousePressEvent(event)


# =============================================================================
# FOTO DOKUMENTASI MANAGER
# =============================================================================

class FotoDokumentasiManager(QWidget):
    """Manager untuk foto dokumentasi BAHP/BAST"""

    photos_changed = Signal()

    def __init__(self, paket_id: int, jenis: str = 'BAHP', parent=None):
        super().__init__(parent)
        self.db = get_db_manager()
        self.paket_id = paket_id
        self.jenis = jenis
        self.current_foto_id = None
        self.foto_list = []

        self.init_database()
        self.init_ui()
        self.load_photos()

    def init_database(self):
        """Pastikan tabel foto_dokumentasi ada"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS foto_dokumentasi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paket_id INTEGER NOT NULL,
                    jenis TEXT NOT NULL,
                    kategori TEXT DEFAULT 'LAINNYA',
                    filepath TEXT NOT NULL,
                    filename TEXT,
                    keterangan TEXT,

                    -- Metadata EXIF
                    waktu_foto TIMESTAMP,
                    latitude REAL,
                    longitude REAL,
                    altitude REAL,
                    camera_make TEXT,
                    camera_model TEXT,

                    -- Dimensi
                    width INTEGER,
                    height INTEGER,

                    -- Tracking
                    urutan INTEGER DEFAULT 0,
                    is_cover INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    uploaded_by TEXT,

                    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_foto_paket ON foto_dokumentasi(paket_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_foto_jenis ON foto_dokumentasi(jenis)
            """)

            conn.commit()
        except Exception as e:
            print(f"Error creating foto_dokumentasi table: {e}")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header
        header = self.create_header()
        layout.addWidget(header)

        # Main content dengan splitter
        splitter = QSplitter(Qt.Horizontal)

        # Panel kiri: Gallery
        gallery_panel = self.create_gallery_panel()
        splitter.addWidget(gallery_panel)

        # Panel kanan: Detail & Upload
        detail_panel = self.create_detail_panel()
        splitter.addWidget(detail_panel)

        splitter.setSizes([600, 400])
        layout.addWidget(splitter)

        # Footer
        footer = self.create_footer()
        layout.addWidget(footer)

    def create_header(self) -> QWidget:
        group = QGroupBox(f"Foto Dokumentasi - {JENIS_DOKUMENTASI.get(self.jenis, self.jenis)}")
        layout = QHBoxLayout(group)

        # Info paket
        paket = self.db.get_paket(self.paket_id)
        if paket:
            self.lbl_paket = QLabel(f"📦 {paket.get('nama', 'Tanpa Nama')}")
            self.lbl_paket.setFont(QFont("Segoe UI", 11, QFont.Bold))
            layout.addWidget(self.lbl_paket)

        layout.addStretch()

        # Filter kategori
        layout.addWidget(QLabel("Filter:"))
        self.cmb_filter = QComboBox()
        self.cmb_filter.addItem("Semua Kategori", "ALL")
        for key, (label, desc, color) in FOTO_KATEGORI.items():
            self.cmb_filter.addItem(f"{label}", key)
        self.cmb_filter.currentIndexChanged.connect(self.apply_filter)
        layout.addWidget(self.cmb_filter)

        # Tombol upload
        self.btn_upload = QPushButton("📤 Upload Foto")
        self.btn_upload.setStyleSheet("background-color: #27ae60;")
        self.btn_upload.clicked.connect(self.upload_photos)
        layout.addWidget(self.btn_upload)

        return group

    def create_gallery_panel(self) -> QWidget:
        group = QGroupBox("Gallery Foto")
        layout = QVBoxLayout(group)

        # Scroll area untuk gallery
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.gallery_layout.setSpacing(10)

        scroll.setWidget(self.gallery_widget)
        layout.addWidget(scroll)

        return group

    def create_detail_panel(self) -> QWidget:
        group = QGroupBox("Detail Foto")
        layout = QVBoxLayout(group)

        # Preview foto
        self.preview_label = QLabel("Pilih foto untuk melihat detail")
        self.preview_label.setFixedHeight(200)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.preview_label)

        # Metadata info
        info_group = QGroupBox("Informasi Metadata")
        info_layout = QGridLayout(info_group)

        info_layout.addWidget(QLabel("Waktu Foto:"), 0, 0)
        self.lbl_waktu = QLabel("-")
        self.lbl_waktu.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(self.lbl_waktu, 0, 1)

        info_layout.addWidget(QLabel("Lokasi GPS:"), 1, 0)
        self.lbl_gps = QLabel("-")
        self.lbl_gps.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(self.lbl_gps, 1, 1)

        info_layout.addWidget(QLabel("Kamera:"), 2, 0)
        self.lbl_camera = QLabel("-")
        info_layout.addWidget(self.lbl_camera, 2, 1)

        info_layout.addWidget(QLabel("Dimensi:"), 3, 0)
        self.lbl_dimensi = QLabel("-")
        info_layout.addWidget(self.lbl_dimensi, 3, 1)

        layout.addWidget(info_group)

        # Edit kategori
        edit_group = QGroupBox("Edit Foto")
        edit_layout = QGridLayout(edit_group)

        edit_layout.addWidget(QLabel("Kategori:"), 0, 0)
        self.cmb_kategori = QComboBox()
        for key, (label, desc, color) in FOTO_KATEGORI.items():
            self.cmb_kategori.addItem(f"{label} - {desc}", key)
        edit_layout.addWidget(self.cmb_kategori, 0, 1)

        edit_layout.addWidget(QLabel("Keterangan:"), 1, 0)
        self.txt_keterangan = QTextEdit()
        self.txt_keterangan.setMaximumHeight(60)
        self.txt_keterangan.setPlaceholderText("Tambahkan keterangan foto...")
        edit_layout.addWidget(self.txt_keterangan, 1, 1)

        self.chk_cover = QCheckBox("Jadikan foto cover")
        edit_layout.addWidget(self.chk_cover, 2, 0, 1, 2)

        layout.addWidget(edit_group)

        # Action buttons - Row 1
        btn_layout = QHBoxLayout()

        self.btn_save = QPushButton("💾 Simpan")
        self.btn_save.clicked.connect(self.save_photo_details)
        self.btn_save.setEnabled(False)
        btn_layout.addWidget(self.btn_save)

        self.btn_view_full = QPushButton("🔍 Buka")
        self.btn_view_full.clicked.connect(self.view_full_photo)
        self.btn_view_full.setEnabled(False)
        btn_layout.addWidget(self.btn_view_full)

        self.btn_download = QPushButton("📥 Download")
        self.btn_download.clicked.connect(self.download_photo)
        self.btn_download.setEnabled(False)
        self.btn_download.setStyleSheet("background-color: #17a2b8;")
        btn_layout.addWidget(self.btn_download)

        self.btn_delete = QPushButton("🗑 Hapus")
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.clicked.connect(self.delete_photo)
        self.btn_delete.setEnabled(False)
        btn_layout.addWidget(self.btn_delete)

        layout.addLayout(btn_layout)

        # Map link (jika ada GPS)
        self.btn_map = QPushButton("🗺 Lihat di Google Maps")
        self.btn_map.clicked.connect(self.open_in_maps)
        self.btn_map.setEnabled(False)
        self.btn_map.setStyleSheet("background-color: #3498db;")
        layout.addWidget(self.btn_map)

        layout.addStretch()

        return group

    def create_footer(self) -> QWidget:
        group = QGroupBox("Ringkasan")
        layout = QHBoxLayout(group)

        self.lbl_total = QLabel("Total: 0 foto")
        layout.addWidget(self.lbl_total)

        self.lbl_dengan_gps = QLabel("Dengan GPS: 0")
        self.lbl_dengan_gps.setStyleSheet("color: #27ae60;")
        layout.addWidget(self.lbl_dengan_gps)

        layout.addStretch()

        # Export buttons
        self.btn_export_report = QPushButton("📄 Export Laporan Foto")
        self.btn_export_report.clicked.connect(self.export_photo_report)
        layout.addWidget(self.btn_export_report)

        self.btn_export_zip = QPushButton("📦 Export ZIP")
        self.btn_export_zip.clicked.connect(self.export_photos_zip)
        layout.addWidget(self.btn_export_zip)

        return group

    def load_photos(self):
        """Load foto dari database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM foto_dokumentasi
                WHERE paket_id = ? AND jenis = ?
                ORDER BY urutan, created_at
            """, (self.paket_id, self.jenis))

            columns = [desc[0] for desc in cursor.description]
            self.foto_list = [dict(zip(columns, row)) for row in cursor.fetchall()]

            self.refresh_gallery()
            self.update_summary()

        except Exception as e:
            print(f"Error loading photos: {e}")
            self.foto_list = []

    def refresh_gallery(self):
        """Refresh tampilan gallery"""
        # Clear existing widgets
        for i in reversed(range(self.gallery_layout.count())):
            widget = self.gallery_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Filter
        filter_value = self.cmb_filter.currentData()

        # Add photo widgets
        col = 0
        row = 0
        max_cols = 3

        for foto in self.foto_list:
            if filter_value != "ALL" and foto.get('kategori') != filter_value:
                continue

            widget = FotoItemWidget(foto)
            widget.clicked.connect(self.on_photo_selected)
            widget.delete_requested.connect(self.delete_photo_by_id)

            self.gallery_layout.addWidget(widget, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Add empty placeholder if no photos
        if self.gallery_layout.count() == 0:
            placeholder = QLabel("📷 Belum ada foto\nKlik 'Upload Foto' untuk menambahkan")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #6c757d; padding: 50px;")
            self.gallery_layout.addWidget(placeholder, 0, 0, 1, max_cols)

    def update_summary(self):
        """Update ringkasan foto"""
        total = len(self.foto_list)
        with_gps = sum(1 for f in self.foto_list if f.get('latitude') and f.get('longitude'))

        self.lbl_total.setText(f"Total: {total} foto")
        self.lbl_dengan_gps.setText(f"Dengan GPS: {with_gps}")

    def apply_filter(self):
        """Apply filter kategori"""
        self.refresh_gallery()

    def upload_photos(self):
        """Upload multiple photos"""
        filepaths, _ = QFileDialog.getOpenFileNames(
            self,
            "Pilih Foto Dokumentasi",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp);;JPEG (*.jpg *.jpeg);;PNG (*.png);;All Files (*)"
        )

        if not filepaths:
            return

        # Dialog untuk memilih kategori
        dialog = QDialog(self)
        dialog.setWindowTitle("Kategori Foto")
        dialog.setMinimumWidth(300)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Pilih kategori untuk foto yang diupload:"))

        cmb = QComboBox()
        for key, (label, desc, color) in FOTO_KATEGORI.items():
            cmb.addItem(f"{label} - {desc}", key)
        layout.addWidget(cmb)

        txt_ket = QTextEdit()
        txt_ket.setMaximumHeight(60)
        txt_ket.setPlaceholderText("Keterangan (opsional)...")
        layout.addWidget(txt_ket)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.Accepted:
            return

        kategori = cmb.currentData()
        keterangan = txt_ket.toPlainText()

        # Process each photo
        success_count = 0
        for filepath in filepaths:
            try:
                # Validate file size (max 20MB)
                if os.path.getsize(filepath) > 20 * 1024 * 1024:
                    QMessageBox.warning(self, "Peringatan", f"File terlalu besar (>20MB):\n{os.path.basename(filepath)}")
                    continue

                # Extract metadata
                metadata = extract_exif_metadata(filepath)

                # Copy to output folder
                dest_folder = self.get_photo_folder()
                os.makedirs(dest_folder, exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ext = os.path.splitext(filepath)[1]
                new_filename = f"{self.jenis}_{kategori}_{timestamp}_{success_count}{ext}"
                dest_path = os.path.join(dest_folder, new_filename)

                shutil.copy2(filepath, dest_path)

                # Save to database
                self.save_photo_to_db(dest_path, new_filename, kategori, keterangan, metadata)

                success_count += 1

            except Exception as e:
                print(f"Error uploading {filepath}: {e}")

        if success_count > 0:
            QMessageBox.information(self, "Sukses", f"{success_count} foto berhasil diupload!")
            self.load_photos()
            self.photos_changed.emit()

    def get_photo_folder(self) -> str:
        """Get folder for storing photos"""
        from app.core.config import OUTPUT_DIR, TAHUN_ANGGARAN

        paket = self.db.get_paket(self.paket_id)
        paket_kode = paket.get('kode', 'unknown') if paket else 'unknown'
        paket_nama = (paket.get('nama', 'unknown')[:30] if paket else 'unknown')

        folder_name = f"{paket_kode}_{paket_nama}".replace(' ', '_')
        folder_name = "".join(c for c in folder_name if c.isalnum() or c in ('_', '-'))

        return os.path.join(OUTPUT_DIR, str(TAHUN_ANGGARAN), folder_name, "foto_dokumentasi", self.jenis)

    def save_photo_to_db(self, filepath: str, filename: str, kategori: str,
                         keterangan: str, metadata: FotoMetadata):
        """Save photo info to database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Get next urutan
            cursor.execute("""
                SELECT COALESCE(MAX(urutan), 0) + 1 FROM foto_dokumentasi
                WHERE paket_id = ? AND jenis = ?
            """, (self.paket_id, self.jenis))
            next_urutan = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO foto_dokumentasi (
                    paket_id, jenis, kategori, filepath, filename, keterangan,
                    waktu_foto, latitude, longitude, altitude,
                    camera_make, camera_model, width, height, urutan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.paket_id, self.jenis, kategori, filepath, filename, keterangan,
                metadata.datetime_taken, metadata.latitude, metadata.longitude, metadata.altitude,
                metadata.camera_make, metadata.camera_model, metadata.width, metadata.height,
                next_urutan
            ))

            conn.commit()

        except Exception as e:
            print(f"Error saving photo to db: {e}")

    def on_photo_selected(self, foto_id: int):
        """Handle photo selection"""
        self.current_foto_id = foto_id

        # Find foto data
        foto = next((f for f in self.foto_list if f.get('id') == foto_id), None)
        if not foto:
            return

        # Update preview
        filepath = foto.get('filepath', '')
        if filepath and os.path.exists(filepath):
            pixmap = QPixmap(filepath)
            if not pixmap.isNull():
                scaled = pixmap.scaled(380, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_label.setPixmap(scaled)

        # Update metadata info
        waktu = foto.get('waktu_foto')
        if waktu:
            self.lbl_waktu.setText(str(waktu)[:19] if isinstance(waktu, str) else waktu.strftime("%d/%m/%Y %H:%M:%S"))
        else:
            self.lbl_waktu.setText("-")

        lat = foto.get('latitude')
        lon = foto.get('longitude')
        if lat and lon:
            self.lbl_gps.setText(f"{lat:.6f}, {lon:.6f}")
            self.btn_map.setEnabled(True)
        else:
            self.lbl_gps.setText("Tidak tersedia")
            self.btn_map.setEnabled(False)

        camera = []
        if foto.get('camera_make'):
            camera.append(foto['camera_make'])
        if foto.get('camera_model'):
            camera.append(foto['camera_model'])
        self.lbl_camera.setText(" ".join(camera) if camera else "-")

        w = foto.get('width', 0)
        h = foto.get('height', 0)
        self.lbl_dimensi.setText(f"{w} x {h}" if w and h else "-")

        # Update edit fields
        kategori = foto.get('kategori', 'LAINNYA')
        idx = self.cmb_kategori.findData(kategori)
        if idx >= 0:
            self.cmb_kategori.setCurrentIndex(idx)

        self.txt_keterangan.setText(foto.get('keterangan', ''))
        self.chk_cover.setChecked(bool(foto.get('is_cover')))

        # Enable buttons
        self.btn_save.setEnabled(True)
        self.btn_view_full.setEnabled(True)
        self.btn_download.setEnabled(True)
        self.btn_delete.setEnabled(True)

    def save_photo_details(self):
        """Save photo details"""
        if not self.current_foto_id:
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            kategori = self.cmb_kategori.currentData()
            keterangan = self.txt_keterangan.toPlainText()
            is_cover = 1 if self.chk_cover.isChecked() else 0

            # If setting as cover, unset others
            if is_cover:
                cursor.execute("""
                    UPDATE foto_dokumentasi SET is_cover = 0
                    WHERE paket_id = ? AND jenis = ?
                """, (self.paket_id, self.jenis))

            cursor.execute("""
                UPDATE foto_dokumentasi
                SET kategori = ?, keterangan = ?, is_cover = ?
                WHERE id = ?
            """, (kategori, keterangan, is_cover, self.current_foto_id))

            conn.commit()

            QMessageBox.information(self, "Sukses", "Detail foto berhasil disimpan!")
            self.load_photos()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {e}")

    def view_full_photo(self):
        """Open photo in default viewer"""
        if not self.current_foto_id:
            return

        foto = next((f for f in self.foto_list if f.get('id') == self.current_foto_id), None)
        if not foto:
            return

        filepath = foto.get('filepath', '')
        if filepath and os.path.exists(filepath):
            import subprocess
            import platform

            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', filepath])
            else:
                subprocess.run(['xdg-open', filepath])

    def download_photo(self):
        """Download/save photo to user-selected location"""
        if not self.current_foto_id:
            return

        foto = next((f for f in self.foto_list if f.get('id') == self.current_foto_id), None)
        if not foto:
            return

        filepath = foto.get('filepath', '')
        if not filepath or not os.path.exists(filepath):
            QMessageBox.warning(self, "Peringatan", "File foto tidak ditemukan!")
            return

        # Get original filename
        original_name = foto.get('filename', os.path.basename(filepath))

        # Ask user where to save
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Foto",
            original_name,
            "Images (*.jpg *.jpeg *.png *.bmp);;All Files (*)"
        )

        if save_path:
            try:
                shutil.copy2(filepath, save_path)
                QMessageBox.information(self, "Sukses", f"Foto berhasil disimpan:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menyimpan foto:\n{str(e)}")

    def delete_photo(self):
        """Delete current photo"""
        if not self.current_foto_id:
            return

        self.delete_photo_by_id(self.current_foto_id)

    def delete_photo_by_id(self, foto_id: int):
        """Delete photo by ID"""
        reply = QMessageBox.question(
            self, "Konfirmasi",
            "Hapus foto ini?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            # Get filepath
            foto = next((f for f in self.foto_list if f.get('id') == foto_id), None)
            if foto:
                filepath = foto.get('filepath', '')
                if filepath and os.path.exists(filepath):
                    os.remove(filepath)

            # Delete from database
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM foto_dokumentasi WHERE id = ?", (foto_id,))
            conn.commit()

            self.current_foto_id = None
            self.load_photos()
            self.photos_changed.emit()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menghapus foto: {e}")

    def open_in_maps(self):
        """Open GPS location in Google Maps"""
        if not self.current_foto_id:
            return

        foto = next((f for f in self.foto_list if f.get('id') == self.current_foto_id), None)
        if not foto:
            return

        lat = foto.get('latitude')
        lon = foto.get('longitude')

        if lat and lon:
            import webbrowser
            url = f"https://www.google.com/maps?q={lat},{lon}"
            webbrowser.open(url)

    def export_photo_report(self):
        """Export photo documentation report"""
        if not self.foto_list:
            QMessageBox.warning(self, "Peringatan", "Tidak ada foto untuk diekspor!")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Laporan Foto",
            f"Laporan_Foto_{self.jenis}_{self.paket_id}.html",
            "HTML Files (*.html);;All Files (*)"
        )

        if not filepath:
            return

        try:
            self.generate_html_report(filepath)
            QMessageBox.information(self, "Sukses", f"Laporan berhasil diekspor:\n{filepath}")

            # Open file
            import webbrowser
            webbrowser.open(f"file://{filepath}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export: {e}")

    def generate_html_report(self, filepath: str):
        """Generate HTML report with photos"""
        paket = self.db.get_paket(self.paket_id)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Laporan Foto Dokumentasi - {self.jenis}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; }}
        .info {{ background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .photo-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
        .photo-card {{ border: 1px solid #dee2e6; border-radius: 8px; padding: 10px; }}
        .photo-card img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 4px; }}
        .photo-meta {{ font-size: 12px; color: #6c757d; margin-top: 10px; }}
        .kategori {{ display: inline-block; padding: 2px 8px; border-radius: 10px; color: white; font-size: 11px; }}
        .gps {{ color: #27ae60; }}
        .no-gps {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #dee2e6; padding: 8px; text-align: left; }}
        th {{ background-color: #34495e; color: white; }}
    </style>
</head>
<body>
    <h1>LAPORAN FOTO DOKUMENTASI</h1>
    <h2>{JENIS_DOKUMENTASI.get(self.jenis, self.jenis)}</h2>

    <div class="info">
        <p><strong>Paket:</strong> {paket.get('nama', '-') if paket else '-'}</p>
        <p><strong>Kode:</strong> {paket.get('kode', '-') if paket else '-'}</p>
        <p><strong>Tanggal Cetak:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        <p><strong>Total Foto:</strong> {len(self.foto_list)}</p>
    </div>

    <h2>Daftar Foto</h2>
    <div class="photo-grid">
"""

        for foto in self.foto_list:
            kategori = foto.get('kategori', 'LAINNYA')
            kat_info = FOTO_KATEGORI.get(kategori, ('Lainnya', '', '#95a5a6'))

            lat = foto.get('latitude')
            lon = foto.get('longitude')
            gps_class = 'gps' if lat and lon else 'no-gps'
            gps_text = f"{lat:.6f}, {lon:.6f}" if lat and lon else "Tidak tersedia"

            waktu = foto.get('waktu_foto', '')
            if waktu:
                waktu = str(waktu)[:19]

            # Convert filepath to relative or base64
            filepath_foto = foto.get('filepath', '')
            img_src = filepath_foto if filepath_foto else ''

            html += f"""
        <div class="photo-card">
            <img src="file://{img_src}" alt="{foto.get('filename', '')}">
            <p><span class="kategori" style="background-color: {kat_info[2]}">{kat_info[0]}</span></p>
            <p><strong>{foto.get('keterangan', '-')}</strong></p>
            <div class="photo-meta">
                <p>📅 Waktu: {waktu or '-'}</p>
                <p class="{gps_class}">📍 GPS: {gps_text}</p>
                <p>📷 {foto.get('camera_make', '')} {foto.get('camera_model', '')}</p>
            </div>
        </div>
"""

        html += """
    </div>

    <h2>Tabel Ringkasan</h2>
    <table>
        <tr>
            <th>No</th>
            <th>Kategori</th>
            <th>Waktu Foto</th>
            <th>GPS</th>
            <th>Keterangan</th>
        </tr>
"""

        for i, foto in enumerate(self.foto_list, 1):
            kategori = foto.get('kategori', 'LAINNYA')
            kat_info = FOTO_KATEGORI.get(kategori, ('Lainnya', '', '#95a5a6'))

            lat = foto.get('latitude')
            lon = foto.get('longitude')
            gps_text = f"{lat:.6f}, {lon:.6f}" if lat and lon else "-"

            waktu = foto.get('waktu_foto', '')
            if waktu:
                waktu = str(waktu)[:19]

            html += f"""
        <tr>
            <td>{i}</td>
            <td>{kat_info[0]}</td>
            <td>{waktu or '-'}</td>
            <td>{gps_text}</td>
            <td>{foto.get('keterangan', '-')}</td>
        </tr>
"""

        html += """
    </table>

    <p style="margin-top: 30px; text-align: center; color: #6c757d;">
        Dokumen ini dibuat secara otomatis oleh Asisten PPK Offline
    </p>
</body>
</html>
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

    def export_photos_zip(self):
        """Export all photos as ZIP"""
        if not self.foto_list:
            QMessageBox.warning(self, "Peringatan", "Tidak ada foto untuk diekspor!")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Foto ke ZIP",
            f"Foto_{self.jenis}_{self.paket_id}.zip",
            "ZIP Files (*.zip)"
        )

        if not filepath:
            return

        try:
            import zipfile

            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for foto in self.foto_list:
                    foto_path = foto.get('filepath', '')
                    if foto_path and os.path.exists(foto_path):
                        kategori = foto.get('kategori', 'LAINNYA')
                        arcname = f"{kategori}/{os.path.basename(foto_path)}"
                        zipf.write(foto_path, arcname)

            QMessageBox.information(self, "Sukses", f"Foto berhasil diekspor ke:\n{filepath}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export ZIP: {e}")


# =============================================================================
# DIALOG
# =============================================================================

class FotoDokumentasiDialog(QDialog):
    """Dialog untuk foto dokumentasi"""

    def __init__(self, paket_id: int, jenis: str = 'BAHP', parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Foto Dokumentasi - {JENIS_DOKUMENTASI.get(jenis, jenis)}")
        self.setMinimumSize(1100, 700)

        layout = QVBoxLayout(self)

        self.manager = FotoDokumentasiManager(paket_id, jenis)
        layout.addWidget(self.manager)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)


# =============================================================================
# TEST
# =============================================================================

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = FotoDokumentasiDialog(1, 'BAHP')
    dialog.show()
    sys.exit(app.exec())
