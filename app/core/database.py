"""
PPK DOCUMENT FACTORY v3.0 - Database Manager
=============================================
Database schema and manager for workflow state tracking
"""

import sqlite3
import os
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

from .config import DATABASE_PATH, TAHUN_ANGGARAN, SATKER_DEFAULT

# ============================================================================
# DATABASE SCHEMA
# ============================================================================

SCHEMA_SQL = """
-- ============================================================================
-- MASTER DATA TABLES
-- ============================================================================

-- Satker / Unit Kerja
CREATE TABLE IF NOT EXISTS satker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kode TEXT NOT NULL UNIQUE,
    nama TEXT NOT NULL,
    nama_pendek TEXT,
    alamat TEXT,
    kota TEXT,
    kode_pos TEXT,
    provinsi TEXT,
    telepon TEXT,
    fax TEXT,
    email TEXT,
    website TEXT,
    kementerian TEXT,
    eselon1 TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pegawai
CREATE TABLE IF NOT EXISTS pegawai (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nip TEXT UNIQUE,
    nama TEXT NOT NULL,
    gelar_depan TEXT,
    gelar_belakang TEXT,
    pangkat TEXT,
    golongan TEXT,
    jabatan TEXT,
    unit_kerja TEXT,
    npwp TEXT,
    no_rekening TEXT,
    nama_bank TEXT,
    is_ppk INTEGER DEFAULT 0,
    is_ppspm INTEGER DEFAULT 0,
    is_bendahara INTEGER DEFAULT 0,
    is_pemeriksa INTEGER DEFAULT 0,
    signature_path TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Penyedia / Vendor
CREATE TABLE IF NOT EXISTS penyedia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    nama_direktur TEXT,
    jabatan_direktur TEXT DEFAULT 'Direktur',
    alamat TEXT,
    kota TEXT,
    npwp TEXT,
    no_rekening TEXT,
    nama_bank TEXT,
    nama_rekening TEXT,
    telepon TEXT,
    email TEXT,
    is_pkp INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PAKET PENGADAAN (PROCUREMENT PACKAGE)
-- ============================================================================

CREATE TABLE IF NOT EXISTS paket (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kode TEXT UNIQUE,
    nama TEXT NOT NULL,
    tahun_anggaran INTEGER NOT NULL,
    jenis_pengadaan TEXT,
    metode_pengadaan TEXT,
    lokasi TEXT,
    sumber_dana TEXT,
    kode_akun TEXT,
    
    -- Nilai
    nilai_pagu REAL,
    nilai_hps REAL,
    nilai_kontrak REAL,
    nilai_ppn REAL,
    nilai_pph REAL,
    jenis_pph TEXT,
    tarif_pph REAL,
    
    -- Waktu
    tanggal_mulai DATE,
    tanggal_selesai DATE,
    jangka_waktu INTEGER,
    
    -- Pihak terkait (foreign keys)
    ppk_id INTEGER,
    ppspm_id INTEGER,
    bendahara_id INTEGER,
    penyedia_id INTEGER,
    
    -- Status workflow
    current_stage TEXT DEFAULT 'SPESIFIKASI',
    status TEXT DEFAULT 'draft',  -- draft, in_progress, completed, cancelled
    metode_hps TEXT DEFAULT 'RATA',  -- RATA, TERTINGGI, TERENDAH
    
    -- Metadata
    data_json TEXT,  -- Additional data in JSON format
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (ppk_id) REFERENCES pegawai(id),
    FOREIGN KEY (ppspm_id) REFERENCES pegawai(id),
    FOREIGN KEY (bendahara_id) REFERENCES pegawai(id),
    FOREIGN KEY (penyedia_id) REFERENCES penyedia(id)
);

-- ============================================================================
-- ITEM BARANG / BILL OF QUANTITY
-- ============================================================================

CREATE TABLE IF NOT EXISTS item_barang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    nomor_urut INTEGER NOT NULL,
    kategori TEXT,           -- A, B, C, D
    kelompok TEXT,           -- Persiapan, Panen, dll
    uraian TEXT NOT NULL,
    spesifikasi TEXT,
    satuan TEXT,
    volume REAL DEFAULT 0,
    harga_dasar REAL DEFAULT 0,
    harga_survey1 REAL,
    harga_survey2 REAL,
    harga_survey3 REAL,
    harga_rata REAL,
    total REAL DEFAULT 0,
    keterangan TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE
);

-- Index for faster lookup
CREATE INDEX IF NOT EXISTS idx_item_barang_paket ON item_barang(paket_id);

-- ============================================================================
-- SURVEY TOKO / SUMBER HARGA
-- ============================================================================

CREATE TABLE IF NOT EXISTS survey_toko (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    nomor_urut INTEGER NOT NULL,        -- 1, 2, 3
    nama_toko TEXT NOT NULL,
    alamat TEXT,
    kota TEXT,
    telepon TEXT,
    email TEXT,
    website TEXT,
    jenis_survey TEXT,                  -- LURING, DARING, KONTRAK
    tanggal_survey DATE,
    nama_surveyor TEXT,
    nip_surveyor TEXT,
    -- Untuk jenis DARING
    platform_online TEXT,               -- Tokopedia, Shopee, Bukalapak, dll
    link_produk TEXT,
    -- Untuk jenis KONTRAK
    nomor_kontrak_referensi TEXT,
    tahun_kontrak_referensi INTEGER,
    instansi_referensi TEXT,
    keterangan TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_survey_toko_paket ON survey_toko(paket_id);

-- ============================================================================
-- DOCUMENT TIMELINE & NUMBERING
-- ============================================================================

CREATE TABLE IF NOT EXISTS dokumen_timeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL,           -- SPESIFIKASI, HPS, SPK, SPMK, etc.
    nomor_dokumen TEXT,
    tanggal_dokumen DATE,
    tanggal_input TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    catatan TEXT,
    is_locked INTEGER DEFAULT 0,      -- 1 jika sudah final/tidak bisa diubah
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    UNIQUE(paket_id, doc_type)
);

CREATE INDEX IF NOT EXISTS idx_dokumen_timeline_paket ON dokumen_timeline(paket_id);

-- Penomoran counter per jenis dokumen per tahun
CREATE TABLE IF NOT EXISTS nomor_counter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tahun INTEGER NOT NULL,
    doc_type TEXT NOT NULL,
    prefix TEXT,
    last_number INTEGER DEFAULT 0,
    format_template TEXT,             -- e.g., "{prefix}/{nomor}/{bulan}/{tahun}"
    
    UNIQUE(tahun, doc_type)
);

-- ============================================================================
-- TIM PEMERIKSA (PPHP Team)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tim_pemeriksa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    pegawai_id INTEGER NOT NULL,
    jabatan_tim TEXT,  -- Ketua, Sekretaris, Anggota
    urutan INTEGER,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    FOREIGN KEY (pegawai_id) REFERENCES pegawai(id),
    UNIQUE(paket_id, pegawai_id)
);

-- ============================================================================
-- WORKFLOW STATE
-- ============================================================================

-- Stage completion tracking
CREATE TABLE IF NOT EXISTS workflow_stage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    stage_code TEXT NOT NULL,
    stage_order INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, in_progress, completed, skipped
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    completed_by TEXT,
    notes TEXT,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    UNIQUE(paket_id, stage_code)
);

-- ============================================================================
-- DOCUMENT TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS dokumen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL,  -- SPESIFIKASI, HPS, KAK, SPK, etc.
    nomor TEXT,
    tanggal DATE,
    filename TEXT,
    filepath TEXT,
    template_used TEXT,
    template_version INTEGER,
    data_json TEXT,  -- Data used to generate
    status TEXT DEFAULT 'draft',  -- draft, final, superseded
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE
);

-- ============================================================================
-- CHECKLIST SPJ (Pertanggungjawaban)
-- ============================================================================

CREATE TABLE IF NOT EXISTS checklist_spj (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL,           -- Kode dokumen (SPESIFIKASI, HPS, SPK, dll)
    status TEXT DEFAULT 'BELUM',      -- BELUM, DRAFT, SIGNED, UPLOADED, ARCHIVED
    filepath_signed TEXT,             -- Path file yang sudah ditandatangani
    catatan TEXT,                     -- Catatan/keterangan
    uploaded_at TIMESTAMP,            -- Waktu upload
    uploaded_by TEXT,                 -- User yang upload
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    UNIQUE(paket_id, doc_type)
);

CREATE INDEX IF NOT EXISTS idx_checklist_spj_paket ON checklist_spj(paket_id);
CREATE INDEX IF NOT EXISTS idx_checklist_spj_status ON checklist_spj(status);

-- ============================================================================
-- FOTO DOKUMENTASI (untuk BAHP/BAST dengan GPS tagging)
-- ============================================================================

CREATE TABLE IF NOT EXISTS foto_dokumentasi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    jenis TEXT NOT NULL,              -- BAHP, BAST, PROGRESS, SURVEY, dll
    kategori TEXT DEFAULT 'LAINNYA',  -- PROGRESS_0, PROGRESS_50, PROGRESS_100, BEFORE, DURING, AFTER, dll
    filepath TEXT NOT NULL,           -- Path file foto
    filename TEXT,                    -- Nama file asli

    keterangan TEXT,                  -- Deskripsi/caption foto

    -- Metadata EXIF
    waktu_foto TIMESTAMP,             -- Waktu pengambilan foto (dari EXIF)
    latitude REAL,                    -- GPS Latitude
    longitude REAL,                   -- GPS Longitude
    altitude REAL,                    -- GPS Altitude
    camera_make TEXT,                 -- Merk kamera
    camera_model TEXT,                -- Model kamera

    -- Dimensi foto
    width INTEGER,
    height INTEGER,

    -- Tracking
    urutan INTEGER DEFAULT 0,         -- Urutan tampilan
    is_cover INTEGER DEFAULT 0,       -- 1 jika foto utama/cover
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by TEXT,

    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_foto_paket ON foto_dokumentasi(paket_id);
CREATE INDEX IF NOT EXISTS idx_foto_jenis ON foto_dokumentasi(jenis);
CREATE INDEX IF NOT EXISTS idx_foto_kategori ON foto_dokumentasi(kategori);

-- ============================================================================
-- TEMPLATE MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS template (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,  -- SPESIFIKASI, HPS, etc.
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- word, excel
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    placeholders TEXT,  -- JSON list of placeholders used
    description TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by TEXT
);

-- Template version history
CREATE TABLE IF NOT EXISTS template_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    replaced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    replaced_by TEXT,
    
    FOREIGN KEY (template_id) REFERENCES template(id)
);

-- ============================================================================
-- DOCUMENT NUMBERING
-- ============================================================================

CREATE TABLE IF NOT EXISTS doc_counter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_type TEXT NOT NULL,
    tahun INTEGER NOT NULL,
    counter INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doc_type, tahun)
);

-- ============================================================================
-- ITEM DETAIL (untuk HPS, Spesifikasi, dll)
-- ============================================================================

CREATE TABLE IF NOT EXISTS paket_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    item_no INTEGER,
    nama_item TEXT NOT NULL,
    spesifikasi TEXT,
    satuan TEXT,
    volume REAL,
    harga_satuan REAL,
    jumlah REAL,
    keterangan TEXT,
    
    -- Survey harga
    harga_survey1 REAL,
    harga_survey2 REAL,
    harga_survey3 REAL,
    harga_rata_rata REAL,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE
);

-- ============================================================================
-- PEMERIKSA / PPHP
-- ============================================================================

CREATE TABLE IF NOT EXISTS paket_pemeriksa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    pegawai_id INTEGER NOT NULL,
    urutan INTEGER DEFAULT 1,  -- 1=Ketua, 2+=Anggota
    jabatan_tim TEXT,  -- Ketua, Sekretaris, Anggota
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    FOREIGN KEY (pegawai_id) REFERENCES pegawai(id)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_paket_tahun ON paket(tahun_anggaran);
CREATE INDEX IF NOT EXISTS idx_paket_status ON paket(status);
CREATE INDEX IF NOT EXISTS idx_paket_stage ON paket(current_stage);
CREATE INDEX IF NOT EXISTS idx_dokumen_paket ON dokumen(paket_id);
CREATE INDEX IF NOT EXISTS idx_dokumen_type ON dokumen(doc_type);
CREATE INDEX IF NOT EXISTS idx_workflow_paket ON workflow_stage(paket_id);
CREATE INDEX IF NOT EXISTS idx_template_code ON template(code, is_active);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp on paket update
CREATE TRIGGER IF NOT EXISTS update_paket_timestamp 
AFTER UPDATE ON paket
BEGIN
    UPDATE paket SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
"""


# Item Barang Categories
KATEGORI_ITEM = {
    'A': 'Bahan/Material',
    'B': 'Peralatan',
    'C': 'Jasa/Tenaga',
    'D': 'Lain-lain'
}

KELOMPOK_ITEM = [
    'Persiapan',
    'Pelaksanaan', 
    'Panen/Produksi',
    'Pasca Panen',
    'Peralatan Utama',
    'Peralatan Pendukung',
    'Bahan Habis Pakai',
    'Jasa Teknis',
    'Jasa Non-Teknis',
    'Lainnya'
]


class DatabaseManager:
    """
    Database manager for PPK Document Factory
    Handles all database operations with connection pooling
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            
            # Insert default satker if not exists
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM satker")
            if cursor.fetchone()[0] == 0:
                self._insert_default_satker(cursor)
            
            # Run migrations
            self._run_migrations(cursor)
            
            conn.commit()
    
    def _run_migrations(self, cursor):
        """Run database migrations for v4 compatibility"""
        # Migration: Add columns to pegawai
        cursor.execute("PRAGMA table_info(pegawai)")
        pegawai_columns = [col[1] for col in cursor.fetchall()]
        
        pegawai_migrations = [
            ('email', "ALTER TABLE pegawai ADD COLUMN email TEXT"),
            ('telepon', "ALTER TABLE pegawai ADD COLUMN telepon TEXT"),
            ('is_pejabat_pengadaan', "ALTER TABLE pegawai ADD COLUMN is_pejabat_pengadaan INTEGER DEFAULT 0"),
            ('foto_path', "ALTER TABLE pegawai ADD COLUMN foto_path TEXT"),
        ]
        
        for col, sql in pegawai_migrations:
            if col not in pegawai_columns:
                try:
                    cursor.execute(sql)
                except:
                    pass
        
        # Migration: Add columns to paket
        cursor.execute("PRAGMA table_info(paket)")
        paket_columns = [col[1] for col in cursor.fetchall()]
        
        paket_migrations = [
            ('metode_hps', "ALTER TABLE paket ADD COLUMN metode_hps TEXT DEFAULT 'RATA'"),
            ('nilai_hps_final', "ALTER TABLE paket ADD COLUMN nilai_hps_final REAL"),
            ('nilai_kontrak_final', "ALTER TABLE paket ADD COLUMN nilai_kontrak_final REAL"),
            ('overhead_profit', "ALTER TABLE paket ADD COLUMN overhead_profit REAL DEFAULT 0.10"),
            ('spesifikasi_locked', "ALTER TABLE paket ADD COLUMN spesifikasi_locked INTEGER DEFAULT 0"),
            ('survey_locked', "ALTER TABLE paket ADD COLUMN survey_locked INTEGER DEFAULT 0"),
            ('hps_locked', "ALTER TABLE paket ADD COLUMN hps_locked INTEGER DEFAULT 0"),
            ('kak_locked', "ALTER TABLE paket ADD COLUMN kak_locked INTEGER DEFAULT 0"),
            ('kontrak_draft_locked', "ALTER TABLE paket ADD COLUMN kontrak_draft_locked INTEGER DEFAULT 0"),
            ('kontrak_final_locked', "ALTER TABLE paket ADD COLUMN kontrak_final_locked INTEGER DEFAULT 0"),
            ('penyedia_data', "ALTER TABLE paket ADD COLUMN penyedia_data TEXT"),  # JSON data penyedia
        ]
        
        for col, sql in paket_migrations:
            if col not in paket_columns:
                try:
                    cursor.execute(sql)
                except:
                    pass
        
        # Migration: Add columns to item_barang
        cursor.execute("PRAGMA table_info(item_barang)")
        item_columns = [col[1] for col in cursor.fetchall()]
        
        item_migrations = [
            ('harga_hps_satuan', "ALTER TABLE item_barang ADD COLUMN harga_hps_satuan REAL"),
            ('total_hps', "ALTER TABLE item_barang ADD COLUMN total_hps REAL"),
            ('harga_kontrak_satuan', "ALTER TABLE item_barang ADD COLUMN harga_kontrak_satuan REAL"),
            ('total_kontrak', "ALTER TABLE item_barang ADD COLUMN total_kontrak REAL"),
            ('selisih_harga', "ALTER TABLE item_barang ADD COLUMN selisih_harga REAL"),
            ('selisih_total', "ALTER TABLE item_barang ADD COLUMN selisih_total REAL"),
            ('overhead_profit', "ALTER TABLE item_barang ADD COLUMN overhead_profit REAL"),
        ]
        
        for col, sql in item_migrations:
            if col not in item_columns:
                try:
                    cursor.execute(sql)
                except:
                    pass
        
        # Create paket_pejabat table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paket_pejabat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paket_id INTEGER NOT NULL,
                pegawai_id INTEGER NOT NULL,
                peran TEXT NOT NULL,
                urutan INTEGER DEFAULT 1,
                tanggal_penetapan DATE,
                nomor_sk TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
                FOREIGN KEY (pegawai_id) REFERENCES pegawai(id),
                UNIQUE(paket_id, pegawai_id, peran)
            )
        """)
        
        # Create audit_log table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                user_name TEXT,
                action TEXT NOT NULL,
                table_name TEXT,
                record_id INTEGER,
                old_values TEXT,
                new_values TEXT,
                ip_address TEXT,
                notes TEXT
            )
        """)
        
        # Create survey_harga_detail table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_harga_detail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paket_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                sumber_ke INTEGER NOT NULL,
                jenis_survey TEXT NOT NULL,
                nama_sumber TEXT,
                alamat TEXT,
                kota TEXT,
                telepon TEXT,
                tanggal_survey DATE,
                surveyor TEXT,
                nip_surveyor TEXT,
                platform TEXT,
                link_produk TEXT,
                tanggal_akses DATE,
                nomor_kontrak TEXT,
                tahun_kontrak INTEGER,
                instansi TEXT,
                harga REAL NOT NULL,
                keterangan TEXT,
                bukti_path TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
                FOREIGN KEY (item_id) REFERENCES item_barang(id) ON DELETE CASCADE
            )
        """)
        
        # Create harga_lifecycle table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS harga_lifecycle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paket_id INTEGER NOT NULL,
                item_id INTEGER,
                tahap TEXT NOT NULL,
                tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                harga_satuan REAL,
                total REAL,
                keterangan TEXT,
                created_by TEXT,
                dokumen_ref TEXT,
                
                FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
                FOREIGN KEY (item_id) REFERENCES item_barang(id) ON DELETE CASCADE
            )
        """)
        
        # Create revisi_harga table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS revisi_harga (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paket_id INTEGER NOT NULL,
                tanggal_revisi DATE,
                nomor_ba_klarifikasi TEXT,
                total_hps_awal REAL,
                total_kontrak_hasil REAL,
                selisih REAL,
                persentase_selisih REAL,
                status TEXT DEFAULT 'draft',
                catatan TEXT,
                approved_by INTEGER,
                approved_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
                FOREIGN KEY (approved_by) REFERENCES pegawai(id)
            )
        """)
    
    def _insert_default_satker(self, cursor):
        """Insert default satker data"""
        cursor.execute("""
            INSERT INTO satker (kode, nama, nama_pendek, alamat, kota, kode_pos,
                provinsi, telepon, fax, email, website, kementerian, eselon1)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            SATKER_DEFAULT['kode'],
            SATKER_DEFAULT['nama'],
            SATKER_DEFAULT['nama_pendek'],
            SATKER_DEFAULT['alamat'],
            SATKER_DEFAULT['kota'],
            SATKER_DEFAULT['kode_pos'],
            SATKER_DEFAULT['provinsi'],
            SATKER_DEFAULT['telepon'],
            SATKER_DEFAULT['fax'],
            SATKER_DEFAULT['email'],
            SATKER_DEFAULT['website'],
            SATKER_DEFAULT['kementerian'],
            SATKER_DEFAULT['eselon1'],
        ))
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    # =========================================================================
    # PAKET OPERATIONS
    # =========================================================================
    
    def create_paket(self, data: Dict) -> int:
        """Create new paket pengadaan"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Generate kode if not provided
            if not data.get('kode'):
                tahun = data.get('tahun_anggaran', TAHUN_ANGGARAN)
                cursor.execute(
                    "SELECT COUNT(*) FROM paket WHERE tahun_anggaran = ?", 
                    (tahun,)
                )
                count = cursor.fetchone()[0] + 1
                data['kode'] = f"PKT-{tahun}-{count:04d}"
            
            # Serialize additional data
            data_json = json.dumps(data.get('additional_data', {}), default=str)
            
            cursor.execute("""
                INSERT INTO paket (
                    kode, nama, tahun_anggaran, jenis_pengadaan, metode_pengadaan,
                    lokasi, sumber_dana, kode_akun, nilai_pagu, nilai_hps,
                    nilai_kontrak, nilai_ppn, nilai_pph, jenis_pph, tarif_pph,
                    tanggal_mulai, tanggal_selesai, jangka_waktu,
                    ppk_id, ppspm_id, bendahara_id, penyedia_id,
                    current_stage, status, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['kode'],
                data['nama'],
                data.get('tahun_anggaran', TAHUN_ANGGARAN),
                data.get('jenis_pengadaan'),
                data.get('metode_pengadaan'),
                data.get('lokasi'),
                data.get('sumber_dana'),
                data.get('kode_akun'),
                data.get('nilai_pagu'),
                data.get('nilai_hps'),
                data.get('nilai_kontrak'),
                data.get('nilai_ppn'),
                data.get('nilai_pph'),
                data.get('jenis_pph'),
                data.get('tarif_pph'),
                data.get('tanggal_mulai'),
                data.get('tanggal_selesai'),
                data.get('jangka_waktu'),
                data.get('ppk_id'),
                data.get('ppspm_id'),
                data.get('bendahara_id'),
                data.get('penyedia_id'),
                'SPESIFIKASI',
                'draft',
                data_json
            ))
            
            paket_id = cursor.lastrowid
            
            # Initialize workflow stages
            self._init_workflow_stages(cursor, paket_id)
            
            conn.commit()
            return paket_id
    
    def _init_workflow_stages(self, cursor, paket_id: int):
        """Initialize workflow stages for a paket"""
        from .config import WORKFLOW_STAGES
        
        for stage in WORKFLOW_STAGES:
            cursor.execute("""
                INSERT INTO workflow_stage (paket_id, stage_code, stage_order, status)
                VALUES (?, ?, ?, 'pending')
            """, (paket_id, stage['code'], stage['id']))
    
    def get_paket(self, paket_id: int) -> Optional[Dict]:
        """Get paket by ID with all related data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.*, 
                       ppk.nama as ppk_nama, ppk.nip as ppk_nip, ppk.jabatan as ppk_jabatan,
                       ppspm.nama as ppspm_nama, ppspm.nip as ppspm_nip,
                       bend.nama as bendahara_nama, bend.nip as bendahara_nip,
                       peny.nama as penyedia_nama, peny.alamat as penyedia_alamat,
                       peny.npwp as penyedia_npwp, peny.nama_direktur as direktur_nama,
                       peny.no_rekening as penyedia_rekening, peny.nama_bank as penyedia_bank,
                       peny.is_pkp as penyedia_is_pkp
                FROM paket p
                LEFT JOIN pegawai ppk ON p.ppk_id = ppk.id
                LEFT JOIN pegawai ppspm ON p.ppspm_id = ppspm.id
                LEFT JOIN pegawai bend ON p.bendahara_id = bend.id
                LEFT JOIN penyedia peny ON p.penyedia_id = peny.id
                WHERE p.id = ?
            """, (paket_id,))
            
            row = cursor.fetchone()
            if row:
                result = dict(row)
                # Parse JSON data
                if result.get('data_json'):
                    result['additional_data'] = json.loads(result['data_json'])
                return result
            return None
    
    def get_paket_list(self, tahun: int = None, status: str = None) -> List[Dict]:
        """Get list of paket with filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM paket WHERE 1=1"
            params = []
            
            if tahun:
                query += " AND tahun_anggaran = ?"
                params.append(tahun)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_paket_pejabat(self, paket_id: int, peran: str) -> Optional[Dict]:
        """
        Get pejabat assigned to a paket by role
        
        Args:
            paket_id: ID of paket
            peran: Role code (PPK, PP, PPSPM, BENDAHARA, PEMERIKSA)
        
        Returns:
            Dict with pegawai data or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Try from paket_pejabat table first
            cursor.execute("""
                SELECT p.* FROM pegawai p
                JOIN paket_pejabat pp ON p.id = pp.pegawai_id
                WHERE pp.paket_id = ? AND pp.peran = ?
                LIMIT 1
            """, (paket_id, peran))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            
            # Fallback: try from paket table directly for PPK
            if peran == 'PPK':
                cursor.execute("""
                    SELECT p.* FROM pegawai p
                    JOIN paket pk ON p.id = pk.ppk_id
                    WHERE pk.id = ?
                """, (paket_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
            
            # Fallback for PPSPM
            elif peran == 'PPSPM':
                cursor.execute("""
                    SELECT p.* FROM pegawai p
                    JOIN paket pk ON p.id = pk.ppspm_id
                    WHERE pk.id = ?
                """, (paket_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
            
            return None
    
    def set_paket_pejabat(self, paket_id: int, pegawai_id: int, peran: str) -> bool:
        """
        Assign a pejabat to a paket
        
        Args:
            paket_id: ID of paket
            pegawai_id: ID of pegawai
            peran: Role code
        
        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete existing assignment for this role
            cursor.execute("""
                DELETE FROM paket_pejabat 
                WHERE paket_id = ? AND peran = ?
            """, (paket_id, peran))
            
            # Insert new assignment
            cursor.execute("""
                INSERT INTO paket_pejabat (paket_id, pegawai_id, peran)
                VALUES (?, ?, ?)
            """, (paket_id, pegawai_id, peran))
            
            conn.commit()
            return True
    
    def get_paket_pejabat_list(self, paket_id: int) -> List[Dict]:
        """Get all pejabat assigned to a paket"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pp.peran, p.* FROM paket_pejabat pp
                JOIN pegawai p ON pp.pegawai_id = p.id
                WHERE pp.paket_id = ?
                ORDER BY pp.peran
            """, (paket_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_paket(self, paket_id: int, data: Dict) -> bool:
        """Update paket data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically
            fields = []
            values = []
            
            updatable = [
                'nama', 'jenis_pengadaan', 'metode_pengadaan', 'lokasi',
                'sumber_dana', 'kode_akun', 'nilai_pagu', 'nilai_hps',
                'nilai_kontrak', 'nilai_ppn', 'nilai_pph', 'jenis_pph', 'tarif_pph',
                'tanggal_mulai', 'tanggal_selesai', 'jangka_waktu',
                'ppk_id', 'ppspm_id', 'bendahara_id', 'penyedia_id',
                'current_stage', 'status'
            ]
            
            for field in updatable:
                if field in data:
                    fields.append(f"{field} = ?")
                    values.append(data[field])
            
            if not fields:
                return False
            
            values.append(paket_id)
            query = f"UPDATE paket SET {', '.join(fields)} WHERE id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
    
    # =========================================================================
    # ITEM BARANG OPERATIONS (Bill of Quantity)
    # =========================================================================
    
    def get_item_barang(self, paket_id: int) -> List[Dict]:
        """Get all items for a paket"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM item_barang
                WHERE paket_id = ? AND is_active = 1
                ORDER BY nomor_urut
            """, (paket_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_item_barang_by_kategori(self, paket_id: int, kategori: str) -> List[Dict]:
        """Get items filtered by category"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM item_barang
                WHERE paket_id = ? AND kategori = ? AND is_active = 1
                ORDER BY nomor_urut
            """, (paket_id, kategori))
            return [dict(row) for row in cursor.fetchall()]
    
    def add_item_barang(self, paket_id: int, data: Dict) -> int:
        """Add new item to paket"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get next nomor_urut
            cursor.execute("""
                SELECT COALESCE(MAX(nomor_urut), 0) + 1 
                FROM item_barang WHERE paket_id = ?
            """, (paket_id,))
            nomor_urut = cursor.fetchone()[0]
            
            # Calculate total
            volume = float(data.get('volume', 0))
            harga_dasar = float(data.get('harga_dasar', 0))
            total = volume * harga_dasar
            
            # Calculate harga rata-rata if survey prices provided
            harga_survey1 = data.get('harga_survey1')
            harga_survey2 = data.get('harga_survey2')
            harga_survey3 = data.get('harga_survey3')
            harga_rata = None
            
            if any([harga_survey1, harga_survey2, harga_survey3]):
                survey_prices = [p for p in [harga_survey1, harga_survey2, harga_survey3] if p]
                if survey_prices:
                    harga_rata = sum(survey_prices) / len(survey_prices)
                    if not harga_dasar:
                        harga_dasar = harga_rata
                        total = volume * harga_rata
            
            cursor.execute("""
                INSERT INTO item_barang (
                    paket_id, nomor_urut, kategori, kelompok, uraian, spesifikasi,
                    satuan, volume, harga_dasar, harga_survey1, harga_survey2,
                    harga_survey3, harga_rata, total, keterangan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paket_id, nomor_urut, data.get('kategori'), data.get('kelompok'),
                data.get('uraian'), data.get('spesifikasi'), data.get('satuan'),
                volume, harga_dasar, harga_survey1, harga_survey2, harga_survey3,
                harga_rata, total, data.get('keterangan')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def update_item_barang(self, item_id: int, data: Dict) -> bool:
        """Update item barang"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Recalculate total
            volume = float(data.get('volume', 0))
            harga_dasar = float(data.get('harga_dasar', 0))
            
            # Calculate harga rata-rata if survey prices provided
            harga_survey1 = data.get('harga_survey1')
            harga_survey2 = data.get('harga_survey2')
            harga_survey3 = data.get('harga_survey3')
            harga_rata = None
            
            if any([harga_survey1, harga_survey2, harga_survey3]):
                survey_prices = [p for p in [harga_survey1, harga_survey2, harga_survey3] if p]
                if survey_prices:
                    harga_rata = sum(survey_prices) / len(survey_prices)
                    if not harga_dasar:
                        harga_dasar = harga_rata
            
            total = volume * harga_dasar
            
            cursor.execute("""
                UPDATE item_barang SET
                    kategori = ?, kelompok = ?, uraian = ?, spesifikasi = ?,
                    satuan = ?, volume = ?, harga_dasar = ?, harga_survey1 = ?,
                    harga_survey2 = ?, harga_survey3 = ?, harga_rata = ?,
                    total = ?, keterangan = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data.get('kategori'), data.get('kelompok'), data.get('uraian'),
                data.get('spesifikasi'), data.get('satuan'), volume, harga_dasar,
                harga_survey1, harga_survey2, harga_survey3, harga_rata,
                total, data.get('keterangan'), item_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_item_barang(self, item_id: int) -> bool:
        """Soft delete item barang"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE item_barang SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (item_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def bulk_delete_item_barang(self, paket_id: int) -> int:
        """Delete all items for a paket (soft delete)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE item_barang SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE paket_id = ? AND is_active = 1
            """, (paket_id,))
            conn.commit()
            return cursor.rowcount
    
    def bulk_add_item_barang(self, paket_id: int, items: List[Dict]) -> int:
        """
        Bulk insert items for better performance (up to 500 items)
        Returns number of items inserted
        """
        if not items:
            return 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get starting nomor_urut
            cursor.execute("""
                SELECT COALESCE(MAX(nomor_urut), 0) 
                FROM item_barang WHERE paket_id = ? AND is_active = 1
            """, (paket_id,))
            start_nomor = cursor.fetchone()[0] + 1
            
            # Prepare batch insert
            insert_data = []
            for i, data in enumerate(items):
                nomor_urut = start_nomor + i
                volume = data.get('volume', 0) or 0
                harga_dasar = data.get('harga_dasar', 0) or 0
                
                # Calculate harga rata-rata
                harga_survey1 = data.get('harga_survey1')
                harga_survey2 = data.get('harga_survey2')
                harga_survey3 = data.get('harga_survey3')
                harga_rata = None
                
                if any([harga_survey1, harga_survey2, harga_survey3]):
                    survey_prices = [p for p in [harga_survey1, harga_survey2, harga_survey3] if p]
                    if survey_prices:
                        harga_rata = sum(survey_prices) / len(survey_prices)
                        if not harga_dasar:
                            harga_dasar = harga_rata
                
                total = volume * harga_dasar
                
                insert_data.append((
                    paket_id, nomor_urut,
                    data.get('kategori'), data.get('kelompok'),
                    data.get('uraian'), data.get('spesifikasi'),
                    data.get('satuan'), volume, harga_dasar,
                    harga_survey1, harga_survey2, harga_survey3,
                    harga_rata, total, data.get('keterangan')
                ))
            
            # Execute batch insert
            cursor.executemany("""
                INSERT INTO item_barang (
                    paket_id, nomor_urut, kategori, kelompok, uraian, spesifikasi,
                    satuan, volume, harga_dasar, harga_survey1, harga_survey2,
                    harga_survey3, harga_rata, total, keterangan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, insert_data)
            
            conn.commit()
            return len(insert_data)
    
    def reorder_item_barang(self, paket_id: int, item_ids: List[int]) -> bool:
        """Reorder items by providing list of ids in desired order"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for i, item_id in enumerate(item_ids, 1):
                cursor.execute("""
                    UPDATE item_barang SET nomor_urut = ? 
                    WHERE id = ? AND paket_id = ?
                """, (i, item_id, paket_id))
            conn.commit()
            return True
    
    def get_item_barang_summary(self, paket_id: int) -> Dict:
        """Get summary totals for item barang"""
        items = self.get_item_barang(paket_id)
        
        subtotal = sum(item['total'] or 0 for item in items)
        ppn = subtotal * 0.11  # 11% PPN
        
        # Get paket info for PPh calculation
        paket = self.get_paket(paket_id)
        tarif_pph = paket.get('tarif_pph', 0.015) if paket else 0.015  # Default 1.5%
        pph = subtotal * tarif_pph
        
        grand_total = subtotal + ppn
        nilai_bersih = grand_total - pph
        
        return {
            'count': len(items),
            'subtotal': subtotal,
            'ppn': ppn,
            'pph': pph,
            'grand_total': grand_total,
            'nilai_bersih': nilai_bersih,
            'items': items
        }
    
    def copy_items_from_paket(self, source_paket_id: int, target_paket_id: int) -> int:
        """Copy all items from one paket to another"""
        items = self.get_item_barang(source_paket_id)
        copied = 0
        for item in items:
            item.pop('id', None)
            item.pop('paket_id', None)
            item.pop('nomor_urut', None)
            item.pop('created_at', None)
            item.pop('updated_at', None)
            item.pop('is_active', None)
            self.add_item_barang(target_paket_id, item)
            copied += 1
        return copied
    
    # =========================================================================
    # TIM PEMERIKSA OPERATIONS
    # =========================================================================
    
    def get_tim_pemeriksa(self, paket_id: int) -> List[Dict]:
        """Get tim pemeriksa for a paket"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tp.*, p.nama, p.nip, p.jabatan
                FROM tim_pemeriksa tp
                JOIN pegawai p ON tp.pegawai_id = p.id
                WHERE tp.paket_id = ?
                ORDER BY tp.urutan
            """, (paket_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def set_tim_pemeriksa(self, paket_id: int, team: List[Dict]) -> bool:
        """Set tim pemeriksa for a paket (replaces existing)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear existing
            cursor.execute("DELETE FROM tim_pemeriksa WHERE paket_id = ?", (paket_id,))
            
            # Insert new
            for i, member in enumerate(team, 1):
                cursor.execute("""
                    INSERT INTO tim_pemeriksa (paket_id, pegawai_id, jabatan_tim, urutan)
                    VALUES (?, ?, ?, ?)
                """, (paket_id, member['pegawai_id'], member['jabatan_tim'], i))
            
            conn.commit()
            return True
    
    # =========================================================================
    # SURVEY TOKO OPERATIONS
    # =========================================================================
    
    def get_survey_toko(self, paket_id: int) -> List[Dict]:
        """Get all survey toko for a paket"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM survey_toko
                WHERE paket_id = ? AND is_active = 1
                ORDER BY nomor_urut
            """, (paket_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_survey_toko_by_id(self, toko_id: int) -> Optional[Dict]:
        """Get single survey toko by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM survey_toko WHERE id = ?", (toko_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def add_survey_toko(self, paket_id: int, data: Dict) -> int:
        """Add new survey toko"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get next nomor_urut (max 3)
            cursor.execute("""
                SELECT COALESCE(MAX(nomor_urut), 0) + 1 
                FROM survey_toko WHERE paket_id = ? AND is_active = 1
            """, (paket_id,))
            nomor_urut = cursor.fetchone()[0]
            
            if nomor_urut > 3:
                raise ValueError("Maksimal 3 toko survey per paket")
            
            cursor.execute("""
                INSERT INTO survey_toko (
                    paket_id, nomor_urut, nama_toko, alamat, kota, telepon,
                    email, website, jenis_survey, tanggal_survey, nama_surveyor,
                    nip_surveyor, platform_online, link_produk, nomor_kontrak_referensi,
                    tahun_kontrak_referensi, instansi_referensi, keterangan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paket_id, nomor_urut, data.get('nama_toko'), data.get('alamat'),
                data.get('kota'), data.get('telepon'), data.get('email'),
                data.get('website'), data.get('jenis_survey'), data.get('tanggal_survey'),
                data.get('nama_surveyor'), data.get('nip_surveyor'),
                data.get('platform_online'), data.get('link_produk'),
                data.get('nomor_kontrak_referensi'), data.get('tahun_kontrak_referensi'),
                data.get('instansi_referensi'), data.get('keterangan')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def update_survey_toko(self, toko_id: int, data: Dict) -> bool:
        """Update survey toko"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE survey_toko SET
                    nama_toko = ?, alamat = ?, kota = ?, telepon = ?,
                    email = ?, website = ?, jenis_survey = ?, tanggal_survey = ?,
                    nama_surveyor = ?, nip_surveyor = ?, platform_online = ?,
                    link_produk = ?, nomor_kontrak_referensi = ?,
                    tahun_kontrak_referensi = ?, instansi_referensi = ?,
                    keterangan = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data.get('nama_toko'), data.get('alamat'), data.get('kota'),
                data.get('telepon'), data.get('email'), data.get('website'),
                data.get('jenis_survey'), data.get('tanggal_survey'),
                data.get('nama_surveyor'), data.get('nip_surveyor'),
                data.get('platform_online'), data.get('link_produk'),
                data.get('nomor_kontrak_referensi'), data.get('tahun_kontrak_referensi'),
                data.get('instansi_referensi'), data.get('keterangan'), toko_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_survey_toko(self, toko_id: int) -> bool:
        """Soft delete survey toko"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE survey_toko SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (toko_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def reorder_survey_toko(self, paket_id: int) -> bool:
        """Reorder survey toko to ensure 1, 2, 3 sequence"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM survey_toko 
                WHERE paket_id = ? AND is_active = 1 
                ORDER BY nomor_urut
            """, (paket_id,))
            
            for i, row in enumerate(cursor.fetchall(), 1):
                cursor.execute("""
                    UPDATE survey_toko SET nomor_urut = ? WHERE id = ?
                """, (i, row['id']))
            
            conn.commit()
            return True
    
    # =========================================================================
    # DOCUMENT TIMELINE & NUMBERING OPERATIONS
    # =========================================================================
    
    def get_dokumen_timeline(self, paket_id: int) -> List[Dict]:
        """Get all document timeline entries for a paket"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM dokumen_timeline
                WHERE paket_id = ?
                ORDER BY tanggal_dokumen
            """, (paket_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_dokumen_timeline_by_type(self, paket_id: int, doc_type: str) -> Optional[Dict]:
        """Get timeline entry for specific document type"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM dokumen_timeline
                WHERE paket_id = ? AND doc_type = ?
            """, (paket_id, doc_type))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def set_dokumen_timeline(self, paket_id: int, doc_type: str, 
                            nomor: str, tanggal: str, catatan: str = None) -> int:
        """Set or update document timeline entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute("""
                SELECT id FROM dokumen_timeline
                WHERE paket_id = ? AND doc_type = ?
            """, (paket_id, doc_type))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE dokumen_timeline SET
                        nomor_dokumen = ?, tanggal_dokumen = ?, catatan = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE paket_id = ? AND doc_type = ?
                """, (nomor, tanggal, catatan, paket_id, doc_type))
                return existing['id']
            else:
                cursor.execute("""
                    INSERT INTO dokumen_timeline (paket_id, doc_type, nomor_dokumen, tanggal_dokumen, catatan)
                    VALUES (?, ?, ?, ?, ?)
                """, (paket_id, doc_type, nomor, tanggal, catatan))
                conn.commit()
                return cursor.lastrowid
    
    def lock_dokumen_timeline(self, paket_id: int, doc_type: str) -> bool:
        """Lock document timeline entry (mark as final)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE dokumen_timeline SET is_locked = 1
                WHERE paket_id = ? AND doc_type = ?
            """, (paket_id, doc_type))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_next_nomor(self, doc_type: str, tahun: int = None, 
                       prefix: str = None, format_template: str = None) -> str:
        """
        Get next document number
        Format template variables: {prefix}, {nomor}, {bulan}, {tahun}, {romawi}
        """
        from datetime import datetime
        
        if tahun is None:
            tahun = datetime.now().year
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get or create counter
            cursor.execute("""
                SELECT * FROM nomor_counter
                WHERE tahun = ? AND doc_type = ?
            """, (tahun, doc_type))
            
            counter = cursor.fetchone()
            
            if counter:
                next_num = counter['last_number'] + 1
                prefix = prefix or counter['prefix'] or ''
                fmt = format_template or counter['format_template'] or "{nomor}/{prefix}/{bulan}/{tahun}"
            else:
                next_num = 1
                prefix = prefix or ''
                fmt = format_template or "{nomor}/{prefix}/{bulan}/{tahun}"
                
                cursor.execute("""
                    INSERT INTO nomor_counter (tahun, doc_type, prefix, last_number, format_template)
                    VALUES (?, ?, ?, 0, ?)
                """, (tahun, doc_type, prefix, fmt))
            
            # Update counter
            cursor.execute("""
                UPDATE nomor_counter SET last_number = ?
                WHERE tahun = ? AND doc_type = ?
            """, (next_num, tahun, doc_type))
            
            conn.commit()
            
            # Format number
            now = datetime.now()
            bulan = now.month
            romawi = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 
                     'VII', 'VIII', 'IX', 'X', 'XI', 'XII'][bulan]
            
            nomor = fmt.format(
                prefix=prefix,
                nomor=f"{next_num:03d}",
                bulan=f"{bulan:02d}",
                tahun=tahun,
                romawi=romawi
            )
            
            return nomor
    
    def preview_next_nomor(self, doc_type: str, tahun: int = None,
                          prefix: str = None, format_template: str = None) -> str:
        """Preview next number without incrementing counter"""
        from datetime import datetime
        
        if tahun is None:
            tahun = datetime.now().year
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM nomor_counter
                WHERE tahun = ? AND doc_type = ?
            """, (tahun, doc_type))
            
            counter = cursor.fetchone()
            
            if counter:
                next_num = counter['last_number'] + 1
                prefix = prefix or counter['prefix'] or ''
                fmt = format_template or counter['format_template'] or "{nomor}/{prefix}/{bulan}/{tahun}"
            else:
                next_num = 1
                prefix = prefix or ''
                fmt = format_template or "{nomor}/{prefix}/{bulan}/{tahun}"
            
            # Format number
            now = datetime.now()
            bulan = now.month
            romawi = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 
                     'VII', 'VIII', 'IX', 'X', 'XI', 'XII'][bulan]
            
            nomor = fmt.format(
                prefix=prefix,
                nomor=f"{next_num:03d}",
                bulan=f"{bulan:02d}",
                tahun=tahun,
                romawi=romawi
            )
            
            return nomor
    
    def set_nomor_format(self, doc_type: str, tahun: int, 
                        prefix: str, format_template: str) -> bool:
        """Set numbering format for a document type"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO nomor_counter (tahun, doc_type, prefix, last_number, format_template)
                VALUES (?, ?, ?, 0, ?)
                ON CONFLICT(tahun, doc_type) DO UPDATE SET
                    prefix = excluded.prefix,
                    format_template = excluded.format_template
            """, (tahun, doc_type, prefix, format_template))
            
            conn.commit()
            return True
    
    def reset_nomor_counter(self, doc_type: str, tahun: int, start_from: int = 0) -> bool:
        """Reset counter to specific number"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE nomor_counter SET last_number = ?
                WHERE tahun = ? AND doc_type = ?
            """, (start_from, tahun, doc_type))
            conn.commit()
            return cursor.rowcount > 0
    
    # =========================================================================
    # WORKFLOW OPERATIONS
    # =========================================================================
    
    def get_workflow_status(self, paket_id: int) -> List[Dict]:
        """Get workflow status for a paket"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM workflow_stage
                WHERE paket_id = ?
                ORDER BY stage_order
            """, (paket_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_stage_status(self, paket_id: int, stage_code: str, 
                           status: str, notes: str = None) -> bool:
        """Update workflow stage status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            if status == 'in_progress':
                cursor.execute("""
                    UPDATE workflow_stage 
                    SET status = ?, started_at = ?, notes = ?
                    WHERE paket_id = ? AND stage_code = ?
                """, (status, now, notes, paket_id, stage_code))
            elif status == 'completed':
                cursor.execute("""
                    UPDATE workflow_stage 
                    SET status = ?, completed_at = ?, notes = ?
                    WHERE paket_id = ? AND stage_code = ?
                """, (status, now, notes, paket_id, stage_code))
            else:
                cursor.execute("""
                    UPDATE workflow_stage 
                    SET status = ?, notes = ?
                    WHERE paket_id = ? AND stage_code = ?
                """, (status, notes, paket_id, stage_code))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def is_stage_allowed(self, paket_id: int, stage_code: str) -> tuple:
        """
        Check if a stage is allowed based on workflow rules
        Returns: (allowed: bool, message: str)
        """
        from .config import WORKFLOW_STAGES, STAGE_CODE_MAP
        
        target_order = STAGE_CODE_MAP.get(stage_code)
        if target_order is None:
            return False, f"Stage {stage_code} tidak dikenal"
        
        workflow = self.get_workflow_status(paket_id)
        
        # Check all previous stages
        for stage in workflow:
            if stage['stage_order'] < target_order:
                if stage['status'] != 'completed' and stage['status'] != 'skipped':
                    prev_stage = next(
                        (s for s in WORKFLOW_STAGES if s['code'] == stage['stage_code']), 
                        None
                    )
                    stage_name = prev_stage['name'] if prev_stage else stage['stage_code']
                    return False, f"Stage '{stage_name}' belum selesai"
        
        return True, "Stage dapat diproses"
    
    # =========================================================================
    # DOCUMENT OPERATIONS
    # =========================================================================
    
    def save_document(self, paket_id: int, doc_type: str, data: Dict) -> int:
        """Save generated document record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO dokumen (
                    paket_id, doc_type, nomor, tanggal, filename, filepath,
                    template_used, template_version, data_json, status, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paket_id,
                doc_type,
                data.get('nomor'),
                data.get('tanggal'),
                data.get('filename'),
                data.get('filepath'),
                data.get('template_used'),
                data.get('template_version', 1),
                json.dumps(data.get('data', {}), default=str),
                'draft',
                data.get('created_by')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_documents(self, paket_id: int, doc_type: str = None) -> List[Dict]:
        """Get documents for a paket"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if doc_type:
                cursor.execute("""
                    SELECT * FROM dokumen
                    WHERE paket_id = ? AND doc_type = ?
                    ORDER BY created_at DESC
                """, (paket_id, doc_type))
            else:
                cursor.execute("""
                    SELECT * FROM dokumen
                    WHERE paket_id = ?
                    ORDER BY created_at DESC
                """, (paket_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # NUMBERING
    # =========================================================================
    
    def get_next_number(self, doc_type: str, tahun: int = None, 
                        prefix: str = None, preview: bool = False) -> str:
        """Get next document number"""
        from .config import NUMBERING_PREFIXES
        
        tahun = tahun or TAHUN_ANGGARAN
        prefix = prefix or NUMBERING_PREFIXES.get(doc_type, doc_type)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT counter FROM doc_counter
                WHERE doc_type = ? AND tahun = ?
            """, (doc_type, tahun))
            
            row = cursor.fetchone()
            next_num = (row['counter'] + 1) if row else 1
            
            if not preview:
                cursor.execute("""
                    INSERT INTO doc_counter (doc_type, tahun, counter)
                    VALUES (?, ?, ?)
                    ON CONFLICT(doc_type, tahun) DO UPDATE SET
                        counter = ?, last_updated = CURRENT_TIMESTAMP
                """, (doc_type, tahun, next_num, next_num))
                conn.commit()
            
            return f"{next_num:04d}/{prefix}/PKP.SRG/{tahun}"
    
    # =========================================================================
    # TEMPLATE OPERATIONS
    # =========================================================================
    
    def save_template(self, data: Dict) -> int:
        """Save template record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if template exists
            cursor.execute("""
                SELECT id, version, filepath FROM template
                WHERE code = ? AND is_active = 1
            """, (data['code'],))
            
            existing = cursor.fetchone()
            
            if existing:
                # Archive old version
                cursor.execute("""
                    INSERT INTO template_history (template_id, version, filename, filepath)
                    VALUES (?, ?, ?, ?)
                """, (existing['id'], existing['version'], 
                      os.path.basename(existing['filepath']), existing['filepath']))
                
                # Update existing
                new_version = existing['version'] + 1
                cursor.execute("""
                    UPDATE template SET
                        filename = ?, filepath = ?, version = ?,
                        placeholders = ?, description = ?, uploaded_by = ?
                    WHERE id = ?
                """, (
                    data['filename'],
                    data['filepath'],
                    new_version,
                    json.dumps(data.get('placeholders', [])),
                    data.get('description'),
                    data.get('uploaded_by'),
                    existing['id']
                ))
                
                conn.commit()
                return existing['id']
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO template (code, name, type, filename, filepath, 
                                         placeholders, description, uploaded_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['code'],
                    data['name'],
                    data['type'],
                    data['filename'],
                    data['filepath'],
                    json.dumps(data.get('placeholders', [])),
                    data.get('description'),
                    data.get('uploaded_by')
                ))
                
                conn.commit()
                return cursor.lastrowid
    
    def get_template(self, code: str) -> Optional[Dict]:
        """Get active template by code"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM template
                WHERE code = ? AND is_active = 1
            """, (code,))
            
            row = cursor.fetchone()
            if row:
                result = dict(row)
                if result.get('placeholders'):
                    result['placeholders'] = json.loads(result['placeholders'])
                return result
            return None
    
    def get_all_templates(self) -> List[Dict]:
        """Get all active templates"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM template WHERE is_active = 1
                ORDER BY code
            """)
            
            results = []
            for row in cursor.fetchall():
                item = dict(row)
                if item.get('placeholders'):
                    item['placeholders'] = json.loads(item['placeholders'])
                results.append(item)
            
            return results
    
    # =========================================================================
    # PEGAWAI OPERATIONS
    # =========================================================================
    
    def get_pegawai_list(self, role: str = None) -> List[Dict]:
        """Get list of pegawai, optionally filtered by role"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if role == 'ppk':
                cursor.execute("SELECT * FROM pegawai WHERE is_ppk = 1 AND is_active = 1")
            elif role == 'ppspm':
                cursor.execute("SELECT * FROM pegawai WHERE is_ppspm = 1 AND is_active = 1")
            elif role == 'bendahara':
                cursor.execute("SELECT * FROM pegawai WHERE is_bendahara = 1 AND is_active = 1")
            elif role == 'pemeriksa':
                cursor.execute("SELECT * FROM pegawai WHERE is_pemeriksa = 1 AND is_active = 1")
            else:
                cursor.execute("SELECT * FROM pegawai WHERE is_active = 1 ORDER BY nama")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def save_pegawai(self, data: Dict) -> int:
        """Save pegawai data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if data.get('id'):
                # Update
                cursor.execute("""
                    UPDATE pegawai SET
                        nip = ?, nama = ?, gelar_depan = ?, gelar_belakang = ?,
                        pangkat = ?, golongan = ?, jabatan = ?, unit_kerja = ?,
                        npwp = ?, no_rekening = ?, nama_bank = ?,
                        is_ppk = ?, is_ppspm = ?, is_bendahara = ?, is_pemeriksa = ?,
                        signature_path = ?
                    WHERE id = ?
                """, (
                    data.get('nip'), data.get('nama'), data.get('gelar_depan'),
                    data.get('gelar_belakang'), data.get('pangkat'), data.get('golongan'),
                    data.get('jabatan'), data.get('unit_kerja'), data.get('npwp'),
                    data.get('no_rekening'), data.get('nama_bank'),
                    data.get('is_ppk', 0), data.get('is_ppspm', 0),
                    data.get('is_bendahara', 0), data.get('is_pemeriksa', 0),
                    data.get('signature_path'), data['id']
                ))
                conn.commit()
                return data['id']
            else:
                # Insert
                cursor.execute("""
                    INSERT INTO pegawai (
                        nip, nama, gelar_depan, gelar_belakang, pangkat, golongan,
                        jabatan, unit_kerja, npwp, no_rekening, nama_bank,
                        is_ppk, is_ppspm, is_bendahara, is_pemeriksa, signature_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data.get('nip'), data.get('nama'), data.get('gelar_depan'),
                    data.get('gelar_belakang'), data.get('pangkat'), data.get('golongan'),
                    data.get('jabatan'), data.get('unit_kerja'), data.get('npwp'),
                    data.get('no_rekening'), data.get('nama_bank'),
                    data.get('is_ppk', 0), data.get('is_ppspm', 0),
                    data.get('is_bendahara', 0), data.get('is_pemeriksa', 0),
                    data.get('signature_path')
                ))
                conn.commit()
                return cursor.lastrowid
    
    # =========================================================================
    # PENYEDIA OPERATIONS
    # =========================================================================
    
    def get_penyedia_list(self) -> List[Dict]:
        """Get list of penyedia"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM penyedia WHERE is_active = 1 ORDER BY nama")
            return [dict(row) for row in cursor.fetchall()]
    
    def save_penyedia(self, data: Dict) -> int:
        """Save penyedia data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if data.get('id'):
                cursor.execute("""
                    UPDATE penyedia SET
                        nama = ?, nama_direktur = ?, jabatan_direktur = ?,
                        alamat = ?, kota = ?, npwp = ?, no_rekening = ?,
                        nama_bank = ?, nama_rekening = ?, telepon = ?,
                        email = ?, is_pkp = ?
                    WHERE id = ?
                """, (
                    data.get('nama'), data.get('nama_direktur'),
                    data.get('jabatan_direktur', 'Direktur'),
                    data.get('alamat'), data.get('kota'), data.get('npwp'),
                    data.get('no_rekening'), data.get('nama_bank'),
                    data.get('nama_rekening'), data.get('telepon'),
                    data.get('email'), data.get('is_pkp', 1), data['id']
                ))
                conn.commit()
                return data['id']
            else:
                cursor.execute("""
                    INSERT INTO penyedia (
                        nama, nama_direktur, jabatan_direktur, alamat, kota,
                        npwp, no_rekening, nama_bank, nama_rekening,
                        telepon, email, is_pkp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data.get('nama'), data.get('nama_direktur'),
                    data.get('jabatan_direktur', 'Direktur'),
                    data.get('alamat'), data.get('kota'), data.get('npwp'),
                    data.get('no_rekening'), data.get('nama_bank'),
                    data.get('nama_rekening'), data.get('telepon'),
                    data.get('email'), data.get('is_pkp', 1)
                ))
                conn.commit()
                return cursor.lastrowid
    
    # =========================================================================
    # SATKER OPERATIONS
    # =========================================================================
    
    def get_satker(self) -> Dict:
        """Get satker data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM satker WHERE is_active = 1 LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else SATKER_DEFAULT


# ============================================================================
# SINGLETON
# ============================================================================

_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get singleton database manager"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


__all__ = ['DatabaseManager', 'get_db_manager']
