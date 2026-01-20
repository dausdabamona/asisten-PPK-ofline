"""
PPK DOCUMENT FACTORY v4.0 - Enhanced Database Manager
======================================================
Complete database schema with:
- Master Pegawai & Pejabat
- Paket Pejabat Assignment
- Survey Harga Detail
- Harga Lifecycle (HPS → Kontrak)
- Workflow Enforcement
- Audit Trail
"""

import sqlite3
import os
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager

from .config import DATABASE_PATH, TAHUN_ANGGARAN, SATKER_DEFAULT

# ============================================================================
# ENHANCED DATABASE SCHEMA v4.0
# ============================================================================

SCHEMA_V4_SQL = """
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

-- Pegawai (Enhanced)
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
    email TEXT,
    telepon TEXT,
    npwp TEXT,
    no_rekening TEXT,
    nama_bank TEXT,
    -- Role flags
    is_ppk INTEGER DEFAULT 0,
    is_ppspm INTEGER DEFAULT 0,
    is_bendahara INTEGER DEFAULT 0,
    is_pemeriksa INTEGER DEFAULT 0,
    is_pejabat_pengadaan INTEGER DEFAULT 0,
    -- Additional
    signature_path TEXT,
    foto_path TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pegawai_nip ON pegawai(nip);
CREATE INDEX IF NOT EXISTS idx_pegawai_nama ON pegawai(nama);
CREATE INDEX IF NOT EXISTS idx_pegawai_active ON pegawai(is_active);

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
-- PAKET PENGADAAN (PROCUREMENT PACKAGE) - Enhanced
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
    nilai_hps_final REAL,           -- HPS setelah ditetapkan
    nilai_kontrak REAL,
    nilai_kontrak_final REAL,       -- Kontrak setelah negosiasi
    nilai_ppn REAL,
    nilai_pph REAL,
    jenis_pph TEXT,
    tarif_pph REAL,
    overhead_profit REAL DEFAULT 0.10,  -- Default 10%
    
    -- Waktu
    tanggal_mulai DATE,
    tanggal_selesai DATE,
    jangka_waktu INTEGER,
    
    -- Pihak terkait (legacy - akan diganti paket_pejabat)
    ppk_id INTEGER,
    ppspm_id INTEGER,
    bendahara_id INTEGER,
    penyedia_id INTEGER,
    
    -- Status workflow
    current_stage TEXT DEFAULT 'SPESIFIKASI',
    status TEXT DEFAULT 'draft',
    metode_hps TEXT DEFAULT 'RATA',
    
    -- Workflow flags
    spesifikasi_locked INTEGER DEFAULT 0,
    survey_locked INTEGER DEFAULT 0,
    hps_locked INTEGER DEFAULT 0,
    kak_locked INTEGER DEFAULT 0,
    kontrak_draft_locked INTEGER DEFAULT 0,
    kontrak_final_locked INTEGER DEFAULT 0,
    
    -- Metadata
    data_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (ppk_id) REFERENCES pegawai(id),
    FOREIGN KEY (ppspm_id) REFERENCES pegawai(id),
    FOREIGN KEY (bendahara_id) REFERENCES pegawai(id),
    FOREIGN KEY (penyedia_id) REFERENCES penyedia(id)
);

-- ============================================================================
-- PAKET PEJABAT (Role Assignment per Paket)
-- ============================================================================

CREATE TABLE IF NOT EXISTS paket_pejabat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    pegawai_id INTEGER NOT NULL,
    peran TEXT NOT NULL,  -- PPK, PEJABAT_PENGADAAN, PPSPM, BENDAHARA, KETUA_PPHP, ANGGOTA_PPHP
    urutan INTEGER DEFAULT 1,  -- Untuk multi-select (anggota)
    tanggal_penetapan DATE,
    nomor_sk TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    FOREIGN KEY (pegawai_id) REFERENCES pegawai(id),
    UNIQUE(paket_id, pegawai_id, peran)
);

CREATE INDEX IF NOT EXISTS idx_paket_pejabat_paket ON paket_pejabat(paket_id);
CREATE INDEX IF NOT EXISTS idx_paket_pejabat_peran ON paket_pejabat(peran);

-- ============================================================================
-- ITEM BARANG / BILL OF QUANTITY - Enhanced
-- ============================================================================

CREATE TABLE IF NOT EXISTS item_barang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    nomor_urut INTEGER NOT NULL,
    kategori TEXT,
    kelompok TEXT,
    uraian TEXT NOT NULL,
    spesifikasi TEXT,
    satuan TEXT,
    volume REAL DEFAULT 0,
    
    -- Harga Survey
    harga_survey1 REAL,
    harga_survey2 REAL,
    harga_survey3 REAL,
    harga_rata REAL,
    
    -- Harga HPS
    harga_dasar REAL DEFAULT 0,       -- Harga satuan HPS
    overhead_profit REAL,              -- Overhead per item (jika berbeda)
    harga_hps_satuan REAL,            -- Harga HPS per satuan (setelah overhead)
    total_hps REAL DEFAULT 0,         -- Volume x Harga HPS
    
    -- Harga Kontrak Final
    harga_kontrak_satuan REAL,        -- Harga setelah negosiasi
    total_kontrak REAL,               -- Volume x Harga Kontrak
    
    -- Selisih
    selisih_harga REAL,               -- HPS - Kontrak per satuan
    selisih_total REAL,               -- Total HPS - Total Kontrak
    
    -- Legacy
    total REAL DEFAULT 0,
    keterangan TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_item_barang_paket ON item_barang(paket_id);

-- ============================================================================
-- SURVEY HARGA DETAIL (Per Item per Sumber)
-- ============================================================================

CREATE TABLE IF NOT EXISTS survey_harga_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    sumber_ke INTEGER NOT NULL,       -- 1, 2, 3
    
    -- Informasi Sumber
    jenis_survey TEXT NOT NULL,       -- LURING, DARING, KONTRAK, BROSUR, KATALOG
    nama_sumber TEXT,                 -- Nama toko/marketplace/kontrak
    alamat TEXT,
    
    -- Untuk LURING (Toko Fisik)
    kota TEXT,
    telepon TEXT,
    tanggal_survey DATE,
    surveyor TEXT,
    nip_surveyor TEXT,
    
    -- Untuk DARING (Marketplace)
    platform TEXT,                    -- Tokopedia, Shopee, dll
    link_produk TEXT,
    tanggal_akses DATE,
    
    -- Untuk KONTRAK (Kontrak Sebelumnya)
    nomor_kontrak TEXT,
    tahun_kontrak INTEGER,
    instansi TEXT,
    
    -- Harga
    harga REAL NOT NULL,
    keterangan TEXT,
    
    -- Bukti
    bukti_path TEXT,                  -- Path to uploaded file
    
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES item_barang(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_survey_detail_paket ON survey_harga_detail(paket_id);
CREATE INDEX IF NOT EXISTS idx_survey_detail_item ON survey_harga_detail(item_id);

-- ============================================================================
-- SURVEY TOKO / SUMBER HARGA (Global per Paket)
-- ============================================================================

CREATE TABLE IF NOT EXISTS survey_toko (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    nomor_urut INTEGER NOT NULL,
    nama_toko TEXT NOT NULL,
    alamat TEXT,
    kota TEXT,
    telepon TEXT,
    email TEXT,
    website TEXT,
    jenis_survey TEXT,
    tanggal_survey DATE,
    nama_surveyor TEXT,
    nip_surveyor TEXT,
    platform_online TEXT,
    link_produk TEXT,
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
-- HARGA LIFECYCLE (Track Price Changes)
-- ============================================================================

CREATE TABLE IF NOT EXISTS harga_lifecycle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    item_id INTEGER,                  -- NULL for paket-level
    
    tahap TEXT NOT NULL,              -- SURVEY, HPS, NEGOSIASI, KONTRAK_FINAL
    tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Values
    harga_satuan REAL,
    total REAL,
    
    -- Metadata
    keterangan TEXT,
    created_by TEXT,
    dokumen_ref TEXT,                 -- Nomor dokumen terkait
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES item_barang(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_harga_lifecycle_paket ON harga_lifecycle(paket_id);

-- ============================================================================
-- REVISI HARGA (dari Pejabat Pengadaan)
-- ============================================================================

CREATE TABLE IF NOT EXISTS revisi_harga (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    
    -- Tanggal & Nomor
    tanggal_revisi DATE,
    nomor_ba_klarifikasi TEXT,        -- Nomor BA Klarifikasi
    
    -- Summary
    total_hps_awal REAL,
    total_kontrak_hasil REAL,
    selisih REAL,
    persentase_selisih REAL,
    
    -- Status
    status TEXT DEFAULT 'draft',      -- draft, submitted, approved, rejected
    catatan TEXT,
    
    -- Approval
    approved_by INTEGER,
    approved_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES pegawai(id)
);

-- ============================================================================
-- BUKTI SURVEY (Attachments)
-- ============================================================================

CREATE TABLE IF NOT EXISTS bukti_survey (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    item_id INTEGER,
    survey_detail_id INTEGER,
    
    jenis TEXT,                       -- FOTO, SCREENSHOT, BROSUR, KONTRAK, NOTA
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    filesize INTEGER,
    mimetype TEXT,
    keterangan TEXT,
    
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by TEXT,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES item_barang(id) ON DELETE CASCADE,
    FOREIGN KEY (survey_detail_id) REFERENCES survey_harga_detail(id) ON DELETE CASCADE
);

-- ============================================================================
-- DOCUMENT TIMELINE & NUMBERING
-- ============================================================================

CREATE TABLE IF NOT EXISTS dokumen_timeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL,
    nomor_dokumen TEXT,
    tanggal_dokumen DATE,
    tanggal_input TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    catatan TEXT,
    is_locked INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    UNIQUE(paket_id, doc_type)
);

CREATE INDEX IF NOT EXISTS idx_dokumen_timeline_paket ON dokumen_timeline(paket_id);

CREATE TABLE IF NOT EXISTS nomor_counter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tahun INTEGER NOT NULL,
    doc_type TEXT NOT NULL,
    prefix TEXT,
    last_number INTEGER DEFAULT 0,
    format_template TEXT,
    
    UNIQUE(tahun, doc_type)
);

-- ============================================================================
-- TIM PEMERIKSA (PPHP Team)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tim_pemeriksa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    pegawai_id INTEGER NOT NULL,
    jabatan_tim TEXT,
    urutan INTEGER,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    FOREIGN KEY (pegawai_id) REFERENCES pegawai(id),
    UNIQUE(paket_id, pegawai_id)
);

-- ============================================================================
-- WORKFLOW STATE
-- ============================================================================

CREATE TABLE IF NOT EXISTS workflow_stage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    stage_code TEXT NOT NULL,
    stage_order INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    completed_by TEXT,
    notes TEXT,
    
    -- Validation results
    validation_passed INTEGER DEFAULT 0,
    validation_errors TEXT,           -- JSON array of errors
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
    UNIQUE(paket_id, stage_code)
);

-- ============================================================================
-- AUDIT TRAIL
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    user_name TEXT,
    action TEXT NOT NULL,             -- CREATE, UPDATE, DELETE, LOCK, APPROVE
    table_name TEXT,
    record_id INTEGER,
    old_values TEXT,                  -- JSON
    new_values TEXT,                  -- JSON
    ip_address TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_log_table ON audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);

-- ============================================================================
-- DOCUMENT TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS dokumen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL,
    nomor TEXT,
    tanggal DATE,
    filename TEXT,
    filepath TEXT,
    template_used TEXT,
    template_version INTEGER,
    data_json TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE
);

-- ============================================================================
-- TEMPLATE MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS template (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    placeholders TEXT,
    description TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by TEXT
);

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

CREATE TABLE IF NOT EXISTS doc_counter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_type TEXT NOT NULL,
    tahun INTEGER NOT NULL,
    counter INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doc_type, tahun)
);

-- ============================================================================
-- PERJALANAN DINAS (Official Travel)
-- ============================================================================

CREATE TABLE IF NOT EXISTS perjalanan_dinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tahun_anggaran INTEGER NOT NULL,

    -- Info kegiatan
    nama_kegiatan TEXT NOT NULL,
    maksud_perjalanan TEXT,
    nomor_surat_tugas TEXT,
    nomor_sppd TEXT,

    -- Pelaksana
    pelaksana_nama TEXT NOT NULL,
    pelaksana_nip TEXT,
    pelaksana_pangkat TEXT,
    pelaksana_golongan TEXT,
    pelaksana_jabatan TEXT,

    -- Tujuan
    kota_asal TEXT,
    kota_tujuan TEXT,
    provinsi_tujuan TEXT,
    alamat_tujuan TEXT,

    -- Waktu
    tanggal_surat_tugas DATE,
    tanggal_berangkat DATE,
    tanggal_kembali DATE,
    lama_perjalanan INTEGER DEFAULT 1,

    -- Anggaran DIPA
    sumber_dana TEXT DEFAULT 'DIPA',
    kode_akun TEXT,

    -- Biaya
    biaya_transport REAL DEFAULT 0,
    biaya_uang_harian REAL DEFAULT 0,
    biaya_penginapan REAL DEFAULT 0,
    biaya_representasi REAL DEFAULT 0,
    biaya_lain_lain REAL DEFAULT 0,
    uang_muka REAL DEFAULT 0,

    -- Pejabat
    ppk_nama TEXT,
    ppk_nip TEXT,
    ppk_jabatan TEXT,
    bendahara_nama TEXT,
    bendahara_nip TEXT,

    -- Status
    status TEXT DEFAULT 'draft',
    doc_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pd_tahun ON perjalanan_dinas(tahun_anggaran);
CREATE INDEX IF NOT EXISTS idx_pd_pelaksana ON perjalanan_dinas(pelaksana_nama);

-- ============================================================================
-- SWAKELOLA (Self-managed Procurement)
-- ============================================================================

CREATE TABLE IF NOT EXISTS swakelola (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tahun_anggaran INTEGER NOT NULL,

    -- Info kegiatan
    nama_kegiatan TEXT NOT NULL,
    tipe_swakelola INTEGER DEFAULT 0,
    tipe_swakelola_text TEXT,
    deskripsi TEXT,
    output_kegiatan TEXT,

    -- Nomor dokumen
    nomor_kak TEXT,
    nomor_sk_tim TEXT,

    -- Waktu
    tanggal_sk_tim DATE,
    tanggal_mulai DATE,
    tanggal_selesai DATE,
    jangka_waktu INTEGER DEFAULT 30,

    -- Anggaran DIPA
    sumber_dana TEXT DEFAULT 'DIPA',
    kode_akun TEXT,
    pagu_swakelola REAL DEFAULT 0,

    -- Pemegang Uang Muka
    pum_nama TEXT,
    pum_nip TEXT,
    pum_jabatan TEXT,
    uang_muka REAL DEFAULT 0,
    tanggal_uang_muka DATE,

    -- Realisasi / Rampung
    total_realisasi REAL DEFAULT 0,
    tanggal_rampung DATE,

    -- Tim Pelaksana
    ketua_nama TEXT,
    ketua_nip TEXT,
    ketua_jabatan TEXT,
    sekretaris_nama TEXT,
    sekretaris_nip TEXT,
    anggota_tim TEXT,

    -- Pejabat
    ppk_nama TEXT,
    ppk_nip TEXT,
    ppk_jabatan TEXT,
    bendahara_nama TEXT,
    bendahara_nip TEXT,

    -- Status
    status TEXT DEFAULT 'draft',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sw_tahun ON swakelola(tahun_anggaran);
CREATE INDEX IF NOT EXISTS idx_sw_kegiatan ON swakelola(nama_kegiatan);
"""

# ============================================================================
# PERAN PEJABAT
# ============================================================================

PERAN_PEJABAT = {
    'PPK': 'Pejabat Pembuat Komitmen',
    'PEJABAT_PENGADAAN': 'Pejabat Pengadaan',
    'PPSPM': 'Pejabat Penandatangan SPM',
    'BENDAHARA': 'Bendahara Pengeluaran',
    'KETUA_PPHP': 'Ketua Pejabat Pemeriksa Hasil Pekerjaan',
    'ANGGOTA_PPHP': 'Anggota Pejabat Pemeriksa Hasil Pekerjaan',
    'STAF_PPK': 'Staf PPK',
}

# ============================================================================
# WORKFLOW STAGES - Enhanced
# ============================================================================

WORKFLOW_STAGES_V4 = [
    {'code': 'SPESIFIKASI', 'name': 'Spesifikasi & BOQ', 'order': 1, 
     'required_before': [], 'can_generate': ['SPESIFIKASI_TEKNIS', 'BOQ']},
    {'code': 'SURVEY', 'name': 'Survey Harga', 'order': 2, 
     'required_before': ['SPESIFIKASI'], 'can_generate': ['BA_SURVEY', 'LAMPIRAN_SURVEY']},
    {'code': 'HPS', 'name': 'Penetapan HPS', 'order': 3, 
     'required_before': ['SURVEY'], 'can_generate': ['REKAP_HPS', 'PENETAPAN_HPS']},
    {'code': 'KAK', 'name': 'Kerangka Acuan Kerja', 'order': 4, 
     'required_before': ['HPS'], 'can_generate': ['KAK']},
    {'code': 'KONTRAK_DRAFT', 'name': 'Rancangan Kontrak', 'order': 5, 
     'required_before': ['KAK'], 'can_generate': ['SPK_DRAFT', 'SSUK', 'SSKK']},
    {'code': 'NOTA_DINAS', 'name': 'Nota Dinas ke PP', 'order': 6, 
     'required_before': ['KONTRAK_DRAFT'], 'can_generate': ['NOTA_DINAS_PP']},
    {'code': 'REVISI_HARGA', 'name': 'Revisi/Klarifikasi Harga', 'order': 7, 
     'required_before': ['NOTA_DINAS'], 'can_generate': ['BA_KLARIFIKASI', 'HPS_REVISI']},
    {'code': 'KONTRAK_FINAL', 'name': 'Kontrak Final', 'order': 8, 
     'required_before': ['REVISI_HARGA'], 'can_generate': ['SPK_FINAL']},
    {'code': 'SPMK', 'name': 'Surat Perintah Mulai Kerja', 'order': 9, 
     'required_before': ['KONTRAK_FINAL'], 'can_generate': ['SPMK']},
    {'code': 'BAHP', 'name': 'Berita Acara Pemeriksaan', 'order': 10, 
     'required_before': ['SPMK'], 'can_generate': ['BAHP']},
    {'code': 'BAST', 'name': 'Berita Acara Serah Terima', 'order': 11, 
     'required_before': ['BAHP'], 'can_generate': ['BAST']},
    {'code': 'SPP', 'name': 'Surat Permintaan Pembayaran', 'order': 12, 
     'required_before': ['BAST'], 'can_generate': ['SPP', 'SSP', 'KUITANSI']},
]

# ============================================================================
# DATABASE MANAGER CLASS
# ============================================================================

class DatabaseManagerV4:
    """Enhanced Database Manager for PPK Document Factory v4.0"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create/update tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_V4_SQL)
            
            # Migrations
            self._run_migrations(conn)
            
            # Insert default satker if not exists
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM satker")
            if cursor.fetchone()[0] == 0:
                self._insert_default_satker(cursor)
            
            conn.commit()
    
    def _run_migrations(self, conn):
        """Run database migrations"""
        cursor = conn.cursor()
        
        # Migration: Add new columns to pegawai if not exist
        cursor.execute("PRAGMA table_info(pegawai)")
        columns = [col[1] for col in cursor.fetchall()]
        
        migrations = [
            ('email', "ALTER TABLE pegawai ADD COLUMN email TEXT"),
            ('telepon', "ALTER TABLE pegawai ADD COLUMN telepon TEXT"),
            ('is_pejabat_pengadaan', "ALTER TABLE pegawai ADD COLUMN is_pejabat_pengadaan INTEGER DEFAULT 0"),
            ('foto_path', "ALTER TABLE pegawai ADD COLUMN foto_path TEXT"),
        ]
        
        for col, sql in migrations:
            if col not in columns:
                try:
                    cursor.execute(sql)
                except:
                    pass
        
        # Migration: Add new columns to paket if not exist
        cursor.execute("PRAGMA table_info(paket)")
        paket_columns = [col[1] for col in cursor.fetchall()]
        
        paket_migrations = [
            ('nilai_hps_final', "ALTER TABLE paket ADD COLUMN nilai_hps_final REAL"),
            ('nilai_kontrak_final', "ALTER TABLE paket ADD COLUMN nilai_kontrak_final REAL"),
            ('overhead_profit', "ALTER TABLE paket ADD COLUMN overhead_profit REAL DEFAULT 0.10"),
            ('spesifikasi_locked', "ALTER TABLE paket ADD COLUMN spesifikasi_locked INTEGER DEFAULT 0"),
            ('survey_locked', "ALTER TABLE paket ADD COLUMN survey_locked INTEGER DEFAULT 0"),
            ('hps_locked', "ALTER TABLE paket ADD COLUMN hps_locked INTEGER DEFAULT 0"),
            ('kak_locked', "ALTER TABLE paket ADD COLUMN kak_locked INTEGER DEFAULT 0"),
            ('kontrak_draft_locked', "ALTER TABLE paket ADD COLUMN kontrak_draft_locked INTEGER DEFAULT 0"),
            ('kontrak_final_locked', "ALTER TABLE paket ADD COLUMN kontrak_final_locked INTEGER DEFAULT 0"),
            ('metode_hps', "ALTER TABLE paket ADD COLUMN metode_hps TEXT DEFAULT 'RATA'"),
        ]
        
        for col, sql in paket_migrations:
            if col not in paket_columns:
                try:
                    cursor.execute(sql)
                except:
                    pass
        
        # Migration: Add new columns to item_barang
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
    # PEGAWAI OPERATIONS
    # =========================================================================
    
    def get_all_pegawai(self, active_only: bool = True, search: str = None) -> List[Dict]:
        """Get all pegawai with optional search"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            sql = "SELECT * FROM pegawai"
            params = []
            conditions = []
            
            if active_only:
                conditions.append("is_active = 1")
            
            if search:
                conditions.append("(nama LIKE ? OR nip LIKE ? OR jabatan LIKE ?)")
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            sql += " ORDER BY nama"
            
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_pegawai(self, pegawai_id: int) -> Optional[Dict]:
        """Get single pegawai by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pegawai WHERE id = ?", (pegawai_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_pegawai_by_nip(self, nip: str) -> Optional[Dict]:
        """Get pegawai by NIP"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pegawai WHERE nip = ?", (nip,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_pegawai(self, data: Dict) -> int:
        """Create new pegawai"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO pegawai (
                    nip, nama, gelar_depan, gelar_belakang, pangkat, golongan,
                    jabatan, unit_kerja, email, telepon, npwp, no_rekening, nama_bank,
                    is_ppk, is_ppspm, is_bendahara, is_pemeriksa, is_pejabat_pengadaan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('nip'), data.get('nama'), data.get('gelar_depan'),
                data.get('gelar_belakang'), data.get('pangkat'), data.get('golongan'),
                data.get('jabatan'), data.get('unit_kerja'), data.get('email'),
                data.get('telepon'), data.get('npwp'), data.get('no_rekening'),
                data.get('nama_bank'), data.get('is_ppk', 0), data.get('is_ppspm', 0),
                data.get('is_bendahara', 0), data.get('is_pemeriksa', 0),
                data.get('is_pejabat_pengadaan', 0)
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def update_pegawai(self, pegawai_id: int, data: Dict) -> bool:
        """Update pegawai"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE pegawai SET
                    nip = ?, nama = ?, gelar_depan = ?, gelar_belakang = ?,
                    pangkat = ?, golongan = ?, jabatan = ?, unit_kerja = ?,
                    email = ?, telepon = ?, npwp = ?, no_rekening = ?, nama_bank = ?,
                    is_ppk = ?, is_ppspm = ?, is_bendahara = ?, is_pemeriksa = ?,
                    is_pejabat_pengadaan = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data.get('nip'), data.get('nama'), data.get('gelar_depan'),
                data.get('gelar_belakang'), data.get('pangkat'), data.get('golongan'),
                data.get('jabatan'), data.get('unit_kerja'), data.get('email'),
                data.get('telepon'), data.get('npwp'), data.get('no_rekening'),
                data.get('nama_bank'), data.get('is_ppk', 0), data.get('is_ppspm', 0),
                data.get('is_bendahara', 0), data.get('is_pemeriksa', 0),
                data.get('is_pejabat_pengadaan', 0), pegawai_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def deactivate_pegawai(self, pegawai_id: int) -> bool:
        """Soft delete pegawai"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pegawai SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (pegawai_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_pegawai_by_role(self, role: str) -> List[Dict]:
        """Get pegawai by role flag"""
        role_column = {
            'ppk': 'is_ppk',
            'ppspm': 'is_ppspm',
            'bendahara': 'is_bendahara',
            'pemeriksa': 'is_pemeriksa',
            'pejabat_pengadaan': 'is_pejabat_pengadaan',
        }.get(role.lower())
        
        if not role_column:
            return []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM pegawai 
                WHERE {role_column} = 1 AND is_active = 1
                ORDER BY nama
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def bulk_import_pegawai(self, pegawai_list: List[Dict]) -> Tuple[int, int, List[str]]:
        """
        Bulk import pegawai from list
        Returns: (imported, updated, errors)
        """
        imported = 0
        updated = 0
        errors = []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for i, data in enumerate(pegawai_list):
                try:
                    nip = data.get('nip', '').strip()
                    nama = data.get('nama', '').strip()
                    
                    if not nama:
                        errors.append(f"Baris {i+1}: Nama wajib diisi")
                        continue
                    
                    # Check if exists
                    if nip:
                        cursor.execute("SELECT id FROM pegawai WHERE nip = ?", (nip,))
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Update
                            cursor.execute("""
                                UPDATE pegawai SET
                                    nama = ?, pangkat = ?, golongan = ?, jabatan = ?,
                                    unit_kerja = ?, email = ?, telepon = ?,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE nip = ?
                            """, (
                                nama, data.get('pangkat'), data.get('golongan'),
                                data.get('jabatan'), data.get('unit_kerja'),
                                data.get('email'), data.get('telepon'), nip
                            ))
                            updated += 1
                            continue
                    
                    # Insert new
                    cursor.execute("""
                        INSERT INTO pegawai (nip, nama, pangkat, golongan, jabatan, unit_kerja, email, telepon)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        nip or None, nama, data.get('pangkat'), data.get('golongan'),
                        data.get('jabatan'), data.get('unit_kerja'),
                        data.get('email'), data.get('telepon')
                    ))
                    imported += 1
                    
                except Exception as e:
                    errors.append(f"Baris {i+1}: {str(e)}")
            
            conn.commit()
        
        return imported, updated, errors
    
    # =========================================================================
    # PAKET PEJABAT OPERATIONS
    # =========================================================================
    
    def get_paket_pejabat(self, paket_id: int) -> List[Dict]:
        """Get all pejabat assigned to a paket"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pp.*, p.nip, p.nama, p.pangkat, p.golongan, p.jabatan
                FROM paket_pejabat pp
                JOIN pegawai p ON pp.pegawai_id = p.id
                WHERE pp.paket_id = ? AND pp.is_active = 1
                ORDER BY pp.peran, pp.urutan
            """, (paket_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_paket_pejabat_by_role(self, paket_id: int, peran: str) -> List[Dict]:
        """Get pejabat by role for a paket"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pp.*, p.nip, p.nama, p.pangkat, p.golongan, p.jabatan,
                       p.gelar_depan, p.gelar_belakang
                FROM paket_pejabat pp
                JOIN pegawai p ON pp.pegawai_id = p.id
                WHERE pp.paket_id = ? AND pp.peran = ? AND pp.is_active = 1
                ORDER BY pp.urutan
            """, (paket_id, peran))
            return [dict(row) for row in cursor.fetchall()]
    
    def set_paket_pejabat(self, paket_id: int, peran: str, pegawai_id: int, 
                         urutan: int = 1, tanggal_penetapan: str = None,
                         nomor_sk: str = None) -> int:
        """Set pejabat for a paket role"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # For single-select roles (PPK, PPSPM, etc), deactivate existing
            if peran not in ['ANGGOTA_PPHP']:
                cursor.execute("""
                    UPDATE paket_pejabat SET is_active = 0
                    WHERE paket_id = ? AND peran = ?
                """, (paket_id, peran))
            
            # Check if already exists
            cursor.execute("""
                SELECT id FROM paket_pejabat
                WHERE paket_id = ? AND pegawai_id = ? AND peran = ?
            """, (paket_id, pegawai_id, peran))
            
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE paket_pejabat SET 
                        is_active = 1, urutan = ?,
                        tanggal_penetapan = ?, nomor_sk = ?
                    WHERE id = ?
                """, (urutan, tanggal_penetapan, nomor_sk, existing[0]))
                result = existing[0]
            else:
                cursor.execute("""
                    INSERT INTO paket_pejabat (paket_id, pegawai_id, peran, urutan, 
                                              tanggal_penetapan, nomor_sk)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (paket_id, pegawai_id, peran, urutan, tanggal_penetapan, nomor_sk))
                result = cursor.lastrowid
            
            conn.commit()
            return result
    
    def remove_paket_pejabat(self, paket_id: int, peran: str, pegawai_id: int = None):
        """Remove pejabat from paket role"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if pegawai_id:
                cursor.execute("""
                    UPDATE paket_pejabat SET is_active = 0
                    WHERE paket_id = ? AND peran = ? AND pegawai_id = ?
                """, (paket_id, peran, pegawai_id))
            else:
                cursor.execute("""
                    UPDATE paket_pejabat SET is_active = 0
                    WHERE paket_id = ? AND peran = ?
                """, (paket_id, peran))
            
            conn.commit()
    
    # =========================================================================
    # SURVEY HARGA DETAIL OPERATIONS
    # =========================================================================
    
    def get_survey_harga_detail(self, paket_id: int, item_id: int = None) -> List[Dict]:
        """Get survey harga details"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if item_id:
                cursor.execute("""
                    SELECT * FROM survey_harga_detail
                    WHERE paket_id = ? AND item_id = ? AND is_active = 1
                    ORDER BY sumber_ke
                """, (paket_id, item_id))
            else:
                cursor.execute("""
                    SELECT * FROM survey_harga_detail
                    WHERE paket_id = ? AND is_active = 1
                    ORDER BY item_id, sumber_ke
                """, (paket_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def add_survey_harga_detail(self, paket_id: int, item_id: int, data: Dict) -> int:
        """Add survey harga detail"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO survey_harga_detail (
                    paket_id, item_id, sumber_ke, jenis_survey, nama_sumber,
                    alamat, kota, telepon, tanggal_survey, surveyor, nip_surveyor,
                    platform, link_produk, tanggal_akses,
                    nomor_kontrak, tahun_kontrak, instansi,
                    harga, keterangan, bukti_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paket_id, item_id, data.get('sumber_ke', 1),
                data.get('jenis_survey'), data.get('nama_sumber'),
                data.get('alamat'), data.get('kota'), data.get('telepon'),
                data.get('tanggal_survey'), data.get('surveyor'), data.get('nip_surveyor'),
                data.get('platform'), data.get('link_produk'), data.get('tanggal_akses'),
                data.get('nomor_kontrak'), data.get('tahun_kontrak'), data.get('instansi'),
                data.get('harga', 0), data.get('keterangan'), data.get('bukti_path')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def count_survey_per_item(self, paket_id: int) -> Dict[int, int]:
        """Count surveys per item"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT item_id, COUNT(*) as count
                FROM survey_harga_detail
                WHERE paket_id = ? AND is_active = 1
                GROUP BY item_id
            """, (paket_id,))
            return {row['item_id']: row['count'] for row in cursor.fetchall()}
    
    # =========================================================================
    # REVISI HARGA OPERATIONS
    # =========================================================================
    
    def create_revisi_harga(self, paket_id: int, data: Dict) -> int:
        """Create revisi harga record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO revisi_harga (
                    paket_id, tanggal_revisi, nomor_ba_klarifikasi,
                    total_hps_awal, total_kontrak_hasil, selisih, persentase_selisih,
                    catatan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paket_id, data.get('tanggal_revisi'), data.get('nomor_ba_klarifikasi'),
                data.get('total_hps_awal'), data.get('total_kontrak_hasil'),
                data.get('selisih'), data.get('persentase_selisih'),
                data.get('catatan')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_revisi_harga(self, paket_id: int) -> Optional[Dict]:
        """Get latest revisi harga for paket"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM revisi_harga
                WHERE paket_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (paket_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def approve_revisi_harga(self, revisi_id: int, approver_id: int) -> bool:
        """Approve revisi harga"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE revisi_harga SET
                    status = 'approved',
                    approved_by = ?,
                    approved_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (approver_id, revisi_id))
            conn.commit()
            return cursor.rowcount > 0
    
    # =========================================================================
    # HARGA LIFECYCLE OPERATIONS
    # =========================================================================
    
    def log_harga_change(self, paket_id: int, item_id: int, tahap: str,
                        harga_satuan: float, total: float, keterangan: str = None,
                        dokumen_ref: str = None) -> int:
        """Log harga change for audit trail"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO harga_lifecycle (
                    paket_id, item_id, tahap, harga_satuan, total,
                    keterangan, dokumen_ref
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (paket_id, item_id, tahap, harga_satuan, total, keterangan, dokumen_ref))
            conn.commit()
            return cursor.lastrowid
    
    def get_harga_history(self, paket_id: int, item_id: int = None) -> List[Dict]:
        """Get harga change history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if item_id:
                cursor.execute("""
                    SELECT * FROM harga_lifecycle
                    WHERE paket_id = ? AND item_id = ?
                    ORDER BY tanggal
                """, (paket_id, item_id))
            else:
                cursor.execute("""
                    SELECT * FROM harga_lifecycle
                    WHERE paket_id = ?
                    ORDER BY tanggal
                """, (paket_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # WORKFLOW ENFORCEMENT
    # =========================================================================
    
    def check_stage_requirements(self, paket_id: int, stage_code: str) -> Tuple[bool, List[str]]:
        """
        Check if stage requirements are met
        Returns: (can_proceed, list_of_missing_requirements)
        """
        stage_config = next((s for s in WORKFLOW_STAGES_V4 if s['code'] == stage_code), None)
        if not stage_config:
            return False, ["Stage tidak dikenal"]
        
        missing = []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check required_before stages
            for required_stage in stage_config.get('required_before', []):
                cursor.execute("""
                    SELECT status FROM workflow_stage
                    WHERE paket_id = ? AND stage_code = ?
                """, (paket_id, required_stage))
                row = cursor.fetchone()
                
                if not row or row['status'] != 'completed':
                    stage_name = next((s['name'] for s in WORKFLOW_STAGES_V4 
                                      if s['code'] == required_stage), required_stage)
                    missing.append(f"Stage '{stage_name}' harus diselesaikan terlebih dahulu")
            
            # Stage-specific validations
            if stage_code == 'SURVEY':
                # Check spesifikasi has items
                cursor.execute("""
                    SELECT COUNT(*) FROM item_barang
                    WHERE paket_id = ? AND is_active = 1
                """, (paket_id,))
                if cursor.fetchone()[0] == 0:
                    missing.append("Belum ada item barang/spesifikasi")
            
            elif stage_code == 'HPS':
                # Check all items have at least 3 survey sources
                cursor.execute("""
                    SELECT ib.id, ib.uraian, COUNT(shd.id) as survey_count
                    FROM item_barang ib
                    LEFT JOIN survey_harga_detail shd ON ib.id = shd.item_id AND shd.is_active = 1
                    WHERE ib.paket_id = ? AND ib.is_active = 1
                    GROUP BY ib.id
                    HAVING survey_count < 3
                """, (paket_id,))
                
                incomplete_items = cursor.fetchall()
                for item in incomplete_items:
                    missing.append(f"Item '{item['uraian']}' belum memiliki 3 sumber survey")
            
            elif stage_code == 'KONTRAK_FINAL':
                # Check revisi harga approved
                cursor.execute("""
                    SELECT status FROM revisi_harga
                    WHERE paket_id = ?
                    ORDER BY created_at DESC LIMIT 1
                """, (paket_id,))
                row = cursor.fetchone()
                if not row or row['status'] != 'approved':
                    missing.append("Revisi harga belum disetujui")
            
            elif stage_code in ['SPP', 'SSP', 'KUITANSI']:
                # Check kontrak_final_locked
                cursor.execute("""
                    SELECT kontrak_final_locked, nilai_kontrak_final
                    FROM paket WHERE id = ?
                """, (paket_id,))
                row = cursor.fetchone()
                if not row or not row['kontrak_final_locked']:
                    missing.append("Kontrak Final belum dikunci")
                if not row or not row['nilai_kontrak_final']:
                    missing.append("Nilai Kontrak Final belum ditetapkan")
        
        return len(missing) == 0, missing
    
    def lock_stage(self, paket_id: int, stage_code: str) -> bool:
        """Lock a stage (mark as completed and prevent changes)"""
        lock_column = {
            'SPESIFIKASI': 'spesifikasi_locked',
            'SURVEY': 'survey_locked',
            'HPS': 'hps_locked',
            'KAK': 'kak_locked',
            'KONTRAK_DRAFT': 'kontrak_draft_locked',
            'KONTRAK_FINAL': 'kontrak_final_locked',
        }.get(stage_code)
        
        if not lock_column:
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Update workflow_stage
            cursor.execute("""
                UPDATE workflow_stage SET
                    status = 'completed',
                    completed_at = CURRENT_TIMESTAMP
                WHERE paket_id = ? AND stage_code = ?
            """, (paket_id, stage_code))
            
            # Update paket lock flag
            cursor.execute(f"""
                UPDATE paket SET {lock_column} = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (paket_id,))
            
            conn.commit()
            return True
    
    def is_stage_locked(self, paket_id: int, stage_code: str) -> bool:
        """Check if stage is locked"""
        lock_column = {
            'SPESIFIKASI': 'spesifikasi_locked',
            'SURVEY': 'survey_locked',
            'HPS': 'hps_locked',
            'KAK': 'kak_locked',
            'KONTRAK_DRAFT': 'kontrak_draft_locked',
            'KONTRAK_FINAL': 'kontrak_final_locked',
        }.get(stage_code)
        
        if not lock_column:
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {lock_column} FROM paket WHERE id = ?", (paket_id,))
            row = cursor.fetchone()
            return bool(row and row[0])
    
    # =========================================================================
    # AUDIT TRAIL
    # =========================================================================
    
    def log_audit(self, action: str, table_name: str, record_id: int,
                 old_values: Dict = None, new_values: Dict = None,
                 user_name: str = None, notes: str = None):
        """Log audit trail entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (
                    user_name, action, table_name, record_id,
                    old_values, new_values, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_name, action, table_name, record_id,
                json.dumps(old_values) if old_values else None,
                json.dumps(new_values) if new_values else None,
                notes
            ))
            conn.commit()

    # =========================================================================
    # PERJALANAN DINAS (Official Travel)
    # =========================================================================

    def create_perjalanan_dinas(self, data: Dict) -> int:
        """Create new perjalanan dinas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO perjalanan_dinas (
                    tahun_anggaran, nama_kegiatan, maksud_perjalanan,
                    nomor_surat_tugas, nomor_sppd,
                    pelaksana_nama, pelaksana_nip, pelaksana_pangkat,
                    pelaksana_golongan, pelaksana_jabatan,
                    kota_asal, kota_tujuan, provinsi_tujuan, alamat_tujuan,
                    tanggal_surat_tugas, tanggal_berangkat, tanggal_kembali, lama_perjalanan,
                    sumber_dana, kode_akun,
                    biaya_transport, biaya_uang_harian, biaya_penginapan,
                    biaya_representasi, biaya_lain_lain, uang_muka,
                    ppk_nama, ppk_nip, ppk_jabatan,
                    bendahara_nama, bendahara_nip,
                    status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('tahun_anggaran', TAHUN_ANGGARAN),
                data.get('nama_kegiatan'),
                data.get('maksud_perjalanan'),
                data.get('nomor_surat_tugas'),
                data.get('nomor_sppd'),
                data.get('pelaksana_nama'),
                data.get('pelaksana_nip'),
                data.get('pelaksana_pangkat'),
                data.get('pelaksana_golongan'),
                data.get('pelaksana_jabatan'),
                data.get('kota_asal'),
                data.get('kota_tujuan'),
                data.get('provinsi_tujuan'),
                data.get('alamat_tujuan'),
                data.get('tanggal_surat_tugas'),
                data.get('tanggal_berangkat'),
                data.get('tanggal_kembali'),
                data.get('lama_perjalanan', 1),
                data.get('sumber_dana', 'DIPA'),
                data.get('kode_akun'),
                data.get('biaya_transport', 0),
                data.get('biaya_uang_harian', 0),
                data.get('biaya_penginapan', 0),
                data.get('biaya_representasi', 0),
                data.get('biaya_lain_lain', 0),
                data.get('uang_muka', 0),
                data.get('ppk_nama'),
                data.get('ppk_nip'),
                data.get('ppk_jabatan'),
                data.get('bendahara_nama'),
                data.get('bendahara_nip'),
                data.get('status', 'draft')
            ))
            conn.commit()
            return cursor.lastrowid

    def update_perjalanan_dinas(self, pd_id: int, data: Dict) -> bool:
        """Update perjalanan dinas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE perjalanan_dinas SET
                    nama_kegiatan = ?, maksud_perjalanan = ?,
                    nomor_surat_tugas = ?, nomor_sppd = ?,
                    pelaksana_nama = ?, pelaksana_nip = ?, pelaksana_pangkat = ?,
                    pelaksana_golongan = ?, pelaksana_jabatan = ?,
                    kota_asal = ?, kota_tujuan = ?, provinsi_tujuan = ?, alamat_tujuan = ?,
                    tanggal_surat_tugas = ?, tanggal_berangkat = ?, tanggal_kembali = ?, lama_perjalanan = ?,
                    sumber_dana = ?, kode_akun = ?,
                    biaya_transport = ?, biaya_uang_harian = ?, biaya_penginapan = ?,
                    biaya_representasi = ?, biaya_lain_lain = ?, uang_muka = ?,
                    ppk_nama = ?, ppk_nip = ?, ppk_jabatan = ?,
                    bendahara_nama = ?, bendahara_nip = ?,
                    status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data.get('nama_kegiatan'),
                data.get('maksud_perjalanan'),
                data.get('nomor_surat_tugas'),
                data.get('nomor_sppd'),
                data.get('pelaksana_nama'),
                data.get('pelaksana_nip'),
                data.get('pelaksana_pangkat'),
                data.get('pelaksana_golongan'),
                data.get('pelaksana_jabatan'),
                data.get('kota_asal'),
                data.get('kota_tujuan'),
                data.get('provinsi_tujuan'),
                data.get('alamat_tujuan'),
                data.get('tanggal_surat_tugas'),
                data.get('tanggal_berangkat'),
                data.get('tanggal_kembali'),
                data.get('lama_perjalanan', 1),
                data.get('sumber_dana', 'DIPA'),
                data.get('kode_akun'),
                data.get('biaya_transport', 0),
                data.get('biaya_uang_harian', 0),
                data.get('biaya_penginapan', 0),
                data.get('biaya_representasi', 0),
                data.get('biaya_lain_lain', 0),
                data.get('uang_muka', 0),
                data.get('ppk_nama'),
                data.get('ppk_nip'),
                data.get('ppk_jabatan'),
                data.get('bendahara_nama'),
                data.get('bendahara_nip'),
                data.get('status', 'draft'),
                pd_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def get_perjalanan_dinas(self, pd_id: int) -> Optional[Dict]:
        """Get single perjalanan dinas by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM perjalanan_dinas WHERE id = ?", (pd_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_all_perjalanan_dinas(self, tahun: int = None) -> List[Dict]:
        """Get all perjalanan dinas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if tahun:
                cursor.execute("""
                    SELECT * FROM perjalanan_dinas
                    WHERE tahun_anggaran = ?
                    ORDER BY created_at DESC
                """, (tahun,))
            else:
                cursor.execute("SELECT * FROM perjalanan_dinas ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_perjalanan_dinas(self, pd_id: int) -> bool:
        """Delete perjalanan dinas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM perjalanan_dinas WHERE id = ?", (pd_id,))
            conn.commit()
            return cursor.rowcount > 0

    # =========================================================================
    # SWAKELOLA (Self-managed Procurement)
    # =========================================================================

    def create_swakelola(self, data: Dict) -> int:
        """Create new swakelola activity"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO swakelola (
                    tahun_anggaran, nama_kegiatan, tipe_swakelola, tipe_swakelola_text,
                    deskripsi, output_kegiatan, nomor_kak, nomor_sk_tim,
                    tanggal_sk_tim, tanggal_mulai, tanggal_selesai, jangka_waktu,
                    sumber_dana, kode_akun, pagu_swakelola,
                    pum_nama, pum_nip, pum_jabatan, uang_muka, tanggal_uang_muka,
                    total_realisasi, tanggal_rampung,
                    ketua_nama, ketua_nip, ketua_jabatan,
                    sekretaris_nama, sekretaris_nip, anggota_tim,
                    ppk_nama, ppk_nip, ppk_jabatan,
                    bendahara_nama, bendahara_nip,
                    status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('tahun_anggaran', TAHUN_ANGGARAN),
                data.get('nama_kegiatan'),
                data.get('tipe_swakelola', 0),
                data.get('tipe_swakelola_text'),
                data.get('deskripsi'),
                data.get('output_kegiatan'),
                data.get('nomor_kak'),
                data.get('nomor_sk_tim'),
                data.get('tanggal_sk_tim'),
                data.get('tanggal_mulai'),
                data.get('tanggal_selesai'),
                data.get('jangka_waktu', 30),
                data.get('sumber_dana', 'DIPA'),
                data.get('kode_akun'),
                data.get('pagu_swakelola', 0),
                data.get('pum_nama'),
                data.get('pum_nip'),
                data.get('pum_jabatan'),
                data.get('uang_muka', 0),
                data.get('tanggal_uang_muka'),
                data.get('total_realisasi', 0),
                data.get('tanggal_rampung'),
                data.get('ketua_nama'),
                data.get('ketua_nip'),
                data.get('ketua_jabatan'),
                data.get('sekretaris_nama'),
                data.get('sekretaris_nip'),
                data.get('anggota_tim'),
                data.get('ppk_nama'),
                data.get('ppk_nip'),
                data.get('ppk_jabatan'),
                data.get('bendahara_nama'),
                data.get('bendahara_nip'),
                data.get('status', 'draft')
            ))
            conn.commit()
            return cursor.lastrowid

    def update_swakelola(self, sw_id: int, data: Dict) -> bool:
        """Update swakelola activity"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE swakelola SET
                    nama_kegiatan = ?, tipe_swakelola = ?, tipe_swakelola_text = ?,
                    deskripsi = ?, output_kegiatan = ?, nomor_kak = ?, nomor_sk_tim = ?,
                    tanggal_sk_tim = ?, tanggal_mulai = ?, tanggal_selesai = ?, jangka_waktu = ?,
                    sumber_dana = ?, kode_akun = ?, pagu_swakelola = ?,
                    pum_nama = ?, pum_nip = ?, pum_jabatan = ?, uang_muka = ?, tanggal_uang_muka = ?,
                    total_realisasi = ?, tanggal_rampung = ?,
                    ketua_nama = ?, ketua_nip = ?, ketua_jabatan = ?,
                    sekretaris_nama = ?, sekretaris_nip = ?, anggota_tim = ?,
                    ppk_nama = ?, ppk_nip = ?, ppk_jabatan = ?,
                    bendahara_nama = ?, bendahara_nip = ?,
                    status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data.get('nama_kegiatan'),
                data.get('tipe_swakelola', 0),
                data.get('tipe_swakelola_text'),
                data.get('deskripsi'),
                data.get('output_kegiatan'),
                data.get('nomor_kak'),
                data.get('nomor_sk_tim'),
                data.get('tanggal_sk_tim'),
                data.get('tanggal_mulai'),
                data.get('tanggal_selesai'),
                data.get('jangka_waktu', 30),
                data.get('sumber_dana', 'DIPA'),
                data.get('kode_akun'),
                data.get('pagu_swakelola', 0),
                data.get('pum_nama'),
                data.get('pum_nip'),
                data.get('pum_jabatan'),
                data.get('uang_muka', 0),
                data.get('tanggal_uang_muka'),
                data.get('total_realisasi', 0),
                data.get('tanggal_rampung'),
                data.get('ketua_nama'),
                data.get('ketua_nip'),
                data.get('ketua_jabatan'),
                data.get('sekretaris_nama'),
                data.get('sekretaris_nip'),
                data.get('anggota_tim'),
                data.get('ppk_nama'),
                data.get('ppk_nip'),
                data.get('ppk_jabatan'),
                data.get('bendahara_nama'),
                data.get('bendahara_nip'),
                data.get('status', 'draft'),
                sw_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def get_swakelola(self, sw_id: int) -> Optional[Dict]:
        """Get single swakelola by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM swakelola WHERE id = ?", (sw_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_all_swakelola(self, tahun: int = None) -> List[Dict]:
        """Get all swakelola activities"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if tahun:
                cursor.execute("""
                    SELECT * FROM swakelola
                    WHERE tahun_anggaran = ?
                    ORDER BY created_at DESC
                """, (tahun,))
            else:
                cursor.execute("SELECT * FROM swakelola ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_swakelola(self, sw_id: int) -> bool:
        """Delete swakelola"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM swakelola WHERE id = ?", (sw_id,))
            conn.commit()
            return cursor.rowcount > 0


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_db_manager_v4 = None

def get_db_manager_v4() -> DatabaseManagerV4:
    """Get singleton database manager instance"""
    global _db_manager_v4
    if _db_manager_v4 is None:
        _db_manager_v4 = DatabaseManagerV4()
    return _db_manager_v4
