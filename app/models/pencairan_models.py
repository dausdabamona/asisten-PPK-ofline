"""
PPK DOCUMENT FACTORY - Pencairan Dana Models
=============================================
Model database untuk sistem pencairan dana workflow-based.

Tabel utama:
1. transaksi_pencairan - Master transaksi pencairan
2. dokumen_transaksi - Dokumen per fase
3. fase_log - Log perpindahan fase
4. saldo_up - Tracking saldo UP
"""

import sqlite3
import os
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager
from enum import IntEnum

# Import konfigurasi database path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import DATABASE_PATH, TAHUN_ANGGARAN

# ============================================================================
# KONSTANTA
# ============================================================================

BATAS_UP_MAKSIMAL = 50_000_000  # Rp 50 juta
BATAS_TUP_HARI = 30  # 1 bulan untuk pertanggungjawaban TUP

# Jenis Belanja yang didukung
JENIS_BELANJA = [
    {"kode": "honorarium", "nama": "Honorarium", "icon": "wallet", "akun_default": "5.2.1.01"},
    {"kode": "jamuan", "nama": "Jamuan Tamu / Konsumsi Rapat", "icon": "utensils", "akun_default": "5.2.2.03"},
    {"kode": "perdin", "nama": "Perjalanan Dinas", "icon": "plane", "akun_default": "5.2.4.01"},
    {"kode": "pjlp", "nama": "PJLP (Tenaga Kontrak)", "icon": "users", "akun_default": "5.2.1.02"},
    {"kode": "atk", "nama": "Belanja ATK / Perlengkapan", "icon": "shopping-cart", "akun_default": "5.2.2.01"},
    {"kode": "lainnya", "nama": "Belanja Lainnya", "icon": "box", "akun_default": "5.2.2.99"},
]

# ============================================================================
# ENUM CLASSES
# ============================================================================

class Mekanisme(str):
    """Jenis mekanisme pencairan dana"""
    UP = "UP"
    TUP = "TUP"
    LS = "LS"

class StatusTransaksi(str):
    """Status transaksi pencairan"""
    DRAFT = "draft"
    AKTIF = "aktif"
    SELESAI = "selesai"
    BATAL = "batal"

class StatusDokumen(str):
    """Status dokumen dalam transaksi"""
    PENDING = "pending"
    DRAFT = "draft"
    FINAL = "final"
    SIGNED = "signed"
    UPLOADED = "uploaded"

class KategoriDokumen(str):
    """Kategori dokumen"""
    WAJIB = "wajib"
    OPSIONAL = "opsional"
    UPLOAD = "upload"
    KONDISIONAL = "kondisional"

# ============================================================================
# DATABASE SCHEMA
# ============================================================================

SCHEMA_TRANSAKSI_PENCAIRAN = """
CREATE TABLE IF NOT EXISTS transaksi_pencairan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kode_transaksi TEXT UNIQUE NOT NULL,
    mekanisme TEXT NOT NULL CHECK (mekanisme IN ('UP', 'TUP', 'LS')),
    jenis_belanja TEXT NOT NULL,
    nama_kegiatan TEXT NOT NULL,

    -- Nilai Keuangan
    estimasi_biaya REAL NOT NULL DEFAULT 0,
    uang_muka REAL DEFAULT 0,
    realisasi REAL DEFAULT 0,

    -- Status & Fase
    fase_aktif INTEGER NOT NULL DEFAULT 1 CHECK (fase_aktif BETWEEN 1 AND 5),
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'aktif', 'selesai', 'batal')),

    -- Dasar Hukum
    jenis_dasar TEXT,
    nomor_dasar TEXT,
    tanggal_dasar DATE,
    perihal_dasar TEXT,

    -- Penerima (untuk UP/TUP)
    penerima_nama TEXT,
    penerima_nip TEXT,
    penerima_jabatan TEXT,
    penerima_npwp TEXT,
    penerima_rekening TEXT,
    penerima_bank TEXT,

    -- Penyedia (untuk LS)
    penyedia_id INTEGER,
    nilai_kontrak REAL,
    nomor_kontrak TEXT,
    tanggal_kontrak DATE,

    -- Kode Akun
    kode_akun TEXT,
    nama_akun TEXT,
    nomor_mak TEXT,

    -- Tahun Anggaran
    tahun_anggaran INTEGER,

    -- Timestamp Kegiatan
    tanggal_kegiatan_mulai DATE,
    tanggal_kegiatan_selesai DATE,

    -- Timestamp TUP (untuk countdown)
    tanggal_sp2d_tup DATE,
    batas_pertanggungjawaban_tup DATE,

    -- Catatan
    catatan TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    FOREIGN KEY (penyedia_id) REFERENCES penyedia(id)
);

-- Index untuk pencarian cepat
CREATE INDEX IF NOT EXISTS idx_transaksi_mekanisme ON transaksi_pencairan(mekanisme);
CREATE INDEX IF NOT EXISTS idx_transaksi_status ON transaksi_pencairan(status);
CREATE INDEX IF NOT EXISTS idx_transaksi_tahun ON transaksi_pencairan(tahun_anggaran);
CREATE INDEX IF NOT EXISTS idx_transaksi_jenis ON transaksi_pencairan(jenis_belanja);
"""

SCHEMA_DOKUMEN_TRANSAKSI = """
CREATE TABLE IF NOT EXISTS dokumen_transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaksi_id INTEGER NOT NULL,
    fase INTEGER NOT NULL CHECK (fase BETWEEN 1 AND 5),
    kode_dokumen TEXT NOT NULL,
    nama_dokumen TEXT NOT NULL,
    kategori TEXT DEFAULT 'wajib' CHECK (kategori IN ('wajib', 'opsional', 'upload', 'kondisional')),
    template_path TEXT,
    file_path TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'draft', 'final', 'signed', 'uploaded')),
    catatan TEXT,
    nomor_dokumen TEXT,
    tanggal_dokumen DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,

    FOREIGN KEY (transaksi_id) REFERENCES transaksi_pencairan(id) ON DELETE CASCADE
);

-- Index untuk lookup cepat
CREATE INDEX IF NOT EXISTS idx_dokumen_transaksi ON dokumen_transaksi(transaksi_id);
CREATE INDEX IF NOT EXISTS idx_dokumen_fase ON dokumen_transaksi(transaksi_id, fase);
"""

SCHEMA_FASE_LOG = """
CREATE TABLE IF NOT EXISTS fase_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaksi_id INTEGER NOT NULL,
    fase_dari INTEGER,
    fase_ke INTEGER NOT NULL,
    aksi TEXT NOT NULL,
    catatan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,

    FOREIGN KEY (transaksi_id) REFERENCES transaksi_pencairan(id) ON DELETE CASCADE
);

-- Index untuk lookup
CREATE INDEX IF NOT EXISTS idx_fase_log_transaksi ON fase_log(transaksi_id);
"""

SCHEMA_SALDO_UP = """
CREATE TABLE IF NOT EXISTS saldo_up (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tahun_anggaran INTEGER NOT NULL,
    bulan INTEGER NOT NULL,
    saldo_awal REAL NOT NULL DEFAULT 50000000,
    total_penggunaan REAL DEFAULT 0,
    total_pertanggungjawaban REAL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(tahun_anggaran, bulan)
);
"""

SCHEMA_COUNTER_TRANSAKSI = """
CREATE TABLE IF NOT EXISTS counter_transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tahun INTEGER NOT NULL,
    mekanisme TEXT NOT NULL,
    last_number INTEGER DEFAULT 0,
    UNIQUE(tahun, mekanisme)
);
"""

SCHEMA_LEMBAR_PERMINTAAN = """
CREATE TABLE IF NOT EXISTS lembar_permintaan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nomor_dokumen TEXT UNIQUE,
    kode_transaksi TEXT,
    hari_tanggal DATE NOT NULL,
    unit_kerja TEXT NOT NULL,
    sumber_dana TEXT,
    
    -- Detail Barang/Jasa
    subtotal REAL DEFAULT 0,
    ppn REAL DEFAULT 0,
    total REAL DEFAULT 0,
    
    -- Penandatangan
    nama_pengajuan TEXT,
    nama_verifikator TEXT,
    nama_ppk TEXT,
    nama_atasan TEXT,
    nama_kpa TEXT,
    
    -- Status dan File
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'final', 'signed', 'uploaded')),
    file_path TEXT,
    
    -- Metadata
    tahun_anggaran INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,
    
    FOREIGN KEY (kode_transaksi) REFERENCES transaksi_pencairan(kode_transaksi)
);

-- Table untuk item/rincian barang dalam lembar permintaan
CREATE TABLE IF NOT EXISTS lembar_permintaan_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lembar_permintaan_id INTEGER NOT NULL,
    item_no INTEGER NOT NULL,
    nama_barang TEXT NOT NULL,
    spesifikasi TEXT,
    volume REAL,
    satuan TEXT,
    harga_satuan REAL,
    total_item REAL,
    keterangan TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (lembar_permintaan_id) REFERENCES lembar_permintaan(id) ON DELETE CASCADE
);

-- Index untuk pencarian dan performa
CREATE INDEX IF NOT EXISTS idx_lembar_kode_transaksi ON lembar_permintaan(kode_transaksi);
CREATE INDEX IF NOT EXISTS idx_lembar_tahun ON lembar_permintaan(tahun_anggaran);
CREATE INDEX IF NOT EXISTS idx_lembar_status ON lembar_permintaan(status);
CREATE INDEX IF NOT EXISTS idx_lembar_item ON lembar_permintaan_item(lembar_permintaan_id);
"""

# ============================================================================
# DATABASE MANAGER CLASS
# ============================================================================

class PencairanManager:
    """
    Manager class untuk operasi database pencairan dana.
    Handles CRUD operations untuk transaksi_pencairan, dokumen_transaksi,
    fase_log, dan saldo_up.
    """

    def __init__(self, db_path: str = None):
        """
        Initialize PencairanManager dengan database path.

        Args:
            db_path: Path ke file database SQLite. Jika None, gunakan default.
        """
        self.db_path = db_path or DATABASE_PATH
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Context manager untuk database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database schema jika belum ada."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create tables
            cursor.executescript(SCHEMA_TRANSAKSI_PENCAIRAN)
            cursor.executescript(SCHEMA_DOKUMEN_TRANSAKSI)
            cursor.executescript(SCHEMA_FASE_LOG)
            cursor.executescript(SCHEMA_SALDO_UP)
            cursor.executescript(SCHEMA_COUNTER_TRANSAKSI)
            cursor.executescript(SCHEMA_LEMBAR_PERMINTAAN)

            conn.commit()

    # ========================================================================
    # TRANSAKSI PENCAIRAN CRUD
    # ========================================================================

    def generate_kode_transaksi(self, mekanisme: str, tahun: int = None) -> str:
        """
        Generate kode transaksi unik.
        Format: [MEKANISME]/[TAHUN]/[NOMOR_URUT]
        Contoh: UP/2026/0001

        Args:
            mekanisme: Jenis mekanisme (UP, TUP, LS)
            tahun: Tahun anggaran (default: tahun sekarang)

        Returns:
            Kode transaksi unik
        """
        if tahun is None:
            tahun = TAHUN_ANGGARAN

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get or create counter
            cursor.execute("""
                INSERT INTO counter_transaksi (tahun, mekanisme, last_number)
                VALUES (?, ?, 0)
                ON CONFLICT(tahun, mekanisme) DO UPDATE SET last_number = last_number + 1
                RETURNING last_number
            """, (tahun, mekanisme))

            result = cursor.fetchone()
            if result:
                nomor = result[0] + 1
            else:
                nomor = 1

            # Update counter
            cursor.execute("""
                UPDATE counter_transaksi
                SET last_number = ?
                WHERE tahun = ? AND mekanisme = ?
            """, (nomor, tahun, mekanisme))

            conn.commit()

            return f"{mekanisme}/{tahun}/{nomor:04d}"

    def create_transaksi(self, data: Dict[str, Any]) -> int:
        """
        Create transaksi pencairan baru.

        Args:
            data: Dictionary dengan data transaksi
                Required: mekanisme, jenis_belanja, nama_kegiatan
                Optional: estimasi_biaya, penerima_*, penyedia_id, dll

        Returns:
            ID transaksi yang baru dibuat
        """
        # Generate kode transaksi
        mekanisme = data.get('mekanisme', 'UP')
        tahun = data.get('tahun_anggaran', TAHUN_ANGGARAN)
        kode = self.generate_kode_transaksi(mekanisme, tahun)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO transaksi_pencairan (
                    kode_transaksi, mekanisme, jenis_belanja, nama_kegiatan,
                    estimasi_biaya, uang_muka, realisasi,
                    fase_aktif, status,
                    jenis_dasar, nomor_dasar, tanggal_dasar, perihal_dasar,
                    penerima_nama, penerima_nip, penerima_jabatan,
                    penerima_npwp, penerima_rekening, penerima_bank,
                    penyedia_id, nilai_kontrak, nomor_kontrak, tanggal_kontrak,
                    kode_akun, nama_akun, nomor_mak,
                    tahun_anggaran,
                    tanggal_kegiatan_mulai, tanggal_kegiatan_selesai,
                    catatan, created_by
                ) VALUES (
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?,
                    ?, ?,
                    ?, ?
                )
            """, (
                kode,
                mekanisme,
                data.get('jenis_belanja', ''),
                data.get('nama_kegiatan', ''),
                data.get('estimasi_biaya', 0),
                data.get('uang_muka', 0),
                data.get('realisasi', 0),
                1,  # fase_aktif dimulai dari 1
                StatusTransaksi.DRAFT,
                data.get('jenis_dasar'),
                data.get('nomor_dasar'),
                data.get('tanggal_dasar'),
                data.get('perihal_dasar'),
                data.get('penerima_nama'),
                data.get('penerima_nip'),
                data.get('penerima_jabatan'),
                data.get('penerima_npwp'),
                data.get('penerima_rekening'),
                data.get('penerima_bank'),
                data.get('penyedia_id'),
                data.get('nilai_kontrak'),
                data.get('nomor_kontrak'),
                data.get('tanggal_kontrak'),
                data.get('kode_akun'),
                data.get('nama_akun'),
                data.get('nomor_mak'),
                tahun,
                data.get('tanggal_kegiatan_mulai'),
                data.get('tanggal_kegiatan_selesai'),
                data.get('catatan'),
                data.get('created_by'),
            ))

            transaksi_id = cursor.lastrowid

            # Log fase awal
            self._log_fase(conn, transaksi_id, None, 1, "CREATE", "Transaksi dibuat")

            conn.commit()

            return transaksi_id

    def get_transaksi(self, transaksi_id: int) -> Optional[Dict[str, Any]]:
        """
        Get transaksi by ID.

        Args:
            transaksi_id: ID transaksi

        Returns:
            Dictionary dengan data transaksi atau None jika tidak ditemukan
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    t.*,
                    p.nama as penyedia_nama,
                    p.alamat as penyedia_alamat,
                    p.npwp as penyedia_npwp,
                    (t.realisasi - t.uang_muka) as selisih
                FROM transaksi_pencairan t
                LEFT JOIN penyedia p ON t.penyedia_id = p.id
                WHERE t.id = ?
            """, (transaksi_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_transaksi_by_kode(self, kode: str) -> Optional[Dict[str, Any]]:
        """Get transaksi by kode transaksi."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    t.*,
                    p.nama as penyedia_nama,
                    (t.realisasi - t.uang_muka) as selisih
                FROM transaksi_pencairan t
                LEFT JOIN penyedia p ON t.penyedia_id = p.id
                WHERE t.kode_transaksi = ?
            """, (kode,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def update_transaksi(self, transaksi_id: int, data: Dict[str, Any]) -> bool:
        """
        Update transaksi pencairan.

        Args:
            transaksi_id: ID transaksi
            data: Dictionary dengan field yang akan diupdate

        Returns:
            True jika berhasil, False jika tidak
        """
        # Build dynamic update query
        allowed_fields = [
            'jenis_belanja', 'nama_kegiatan',
            'estimasi_biaya', 'uang_muka', 'realisasi',
            'jenis_dasar', 'nomor_dasar', 'tanggal_dasar', 'perihal_dasar',
            'penerima_nama', 'penerima_nip', 'penerima_jabatan',
            'penerima_npwp', 'penerima_rekening', 'penerima_bank',
            'penyedia_id', 'nilai_kontrak', 'nomor_kontrak', 'tanggal_kontrak',
            'kode_akun', 'nama_akun', 'nomor_mak',
            'tanggal_kegiatan_mulai', 'tanggal_kegiatan_selesai',
            'tanggal_sp2d_tup', 'batas_pertanggungjawaban_tup',
            'catatan', 'updated_by'
        ]

        updates = []
        values = []

        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = ?")
                values.append(data[field])

        if not updates:
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(transaksi_id)

        query = f"UPDATE transaksi_pencairan SET {', '.join(updates)} WHERE id = ?"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

    def update_fase(self, transaksi_id: int, fase_baru: int, catatan: str = None) -> bool:
        """
        Update fase aktif transaksi.

        Args:
            transaksi_id: ID transaksi
            fase_baru: Fase baru (1-5)
            catatan: Catatan perpindahan fase

        Returns:
            True jika berhasil
        """
        if fase_baru < 1 or fase_baru > 5:
            raise ValueError("Fase harus antara 1 dan 5")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get current fase
            cursor.execute("SELECT fase_aktif FROM transaksi_pencairan WHERE id = ?", (transaksi_id,))
            row = cursor.fetchone()
            if not row:
                return False

            fase_lama = row[0]

            # Update fase
            cursor.execute("""
                UPDATE transaksi_pencairan
                SET fase_aktif = ?,
                    status = CASE WHEN ? = 5 THEN 'selesai' ELSE 'aktif' END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (fase_baru, fase_baru, transaksi_id))

            # Log perpindahan
            aksi = "NEXT" if fase_baru > fase_lama else "BACK"
            self._log_fase(conn, transaksi_id, fase_lama, fase_baru, aksi, catatan)

            conn.commit()
            return True

    def update_status(self, transaksi_id: int, status: str) -> bool:
        """Update status transaksi."""
        if status not in [StatusTransaksi.DRAFT, StatusTransaksi.AKTIF,
                          StatusTransaksi.SELESAI, StatusTransaksi.BATAL]:
            raise ValueError(f"Status tidak valid: {status}")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transaksi_pencairan
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, transaksi_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_transaksi(self, transaksi_id: int) -> bool:
        """Delete transaksi (soft delete dengan set status batal)."""
        return self.update_status(transaksi_id, StatusTransaksi.BATAL)

    def list_transaksi(
        self,
        mekanisme: str = None,
        status: str = None,
        jenis_belanja: str = None,
        tahun: int = None,
        search: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        List transaksi dengan filter.

        Args:
            mekanisme: Filter by mekanisme (UP, TUP, LS)
            status: Filter by status
            jenis_belanja: Filter by jenis belanja
            tahun: Filter by tahun anggaran
            search: Search by nama kegiatan atau kode
            limit: Jumlah hasil maksimal
            offset: Offset untuk pagination

        Returns:
            Tuple (list transaksi, total count)
        """
        conditions = ["status != 'batal'"]
        params = []

        if mekanisme:
            conditions.append("mekanisme = ?")
            params.append(mekanisme)

        if status:
            conditions.append("status = ?")
            params.append(status)

        if jenis_belanja:
            conditions.append("jenis_belanja = ?")
            params.append(jenis_belanja)

        if tahun:
            conditions.append("tahun_anggaran = ?")
            params.append(tahun)

        if search:
            conditions.append("(nama_kegiatan LIKE ? OR kode_transaksi LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])

        where_clause = " AND ".join(conditions)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get total count
            cursor.execute(f"""
                SELECT COUNT(*) FROM transaksi_pencairan WHERE {where_clause}
            """, params)
            total = cursor.fetchone()[0]

            # Get data
            cursor.execute(f"""
                SELECT
                    t.*,
                    p.nama as penyedia_nama,
                    (t.realisasi - t.uang_muka) as selisih
                FROM transaksi_pencairan t
                LEFT JOIN penyedia p ON t.penyedia_id = p.id
                WHERE {where_clause}
                ORDER BY t.created_at DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset])

            rows = cursor.fetchall()
            return [dict(row) for row in rows], total

    def get_statistik(self, mekanisme: str = None, tahun: int = None) -> Dict[str, Any]:
        """
        Get statistik transaksi.

        Returns:
            Dictionary dengan statistik:
            - total_transaksi
            - per_status (draft, aktif, selesai)
            - total_nilai
            - per_jenis_belanja
        """
        tahun = tahun or TAHUN_ANGGARAN

        with self.get_connection() as conn:
            cursor = conn.cursor()

            base_condition = "status != 'batal' AND tahun_anggaran = ?"
            params = [tahun]

            if mekanisme:
                base_condition += " AND mekanisme = ?"
                params.append(mekanisme)

            # Total transaksi
            cursor.execute(f"""
                SELECT COUNT(*) FROM transaksi_pencairan WHERE {base_condition}
            """, params)
            total = cursor.fetchone()[0]

            # Per status
            cursor.execute(f"""
                SELECT status, COUNT(*) as jumlah
                FROM transaksi_pencairan
                WHERE {base_condition}
                GROUP BY status
            """, params)
            per_status = {row['status']: row['jumlah'] for row in cursor.fetchall()}

            # Total nilai
            cursor.execute(f"""
                SELECT
                    COALESCE(SUM(estimasi_biaya), 0) as total_estimasi,
                    COALESCE(SUM(uang_muka), 0) as total_uang_muka,
                    COALESCE(SUM(realisasi), 0) as total_realisasi
                FROM transaksi_pencairan
                WHERE {base_condition}
            """, params)
            nilai = dict(cursor.fetchone())

            # Per jenis belanja
            cursor.execute(f"""
                SELECT jenis_belanja, COUNT(*) as jumlah, SUM(estimasi_biaya) as total
                FROM transaksi_pencairan
                WHERE {base_condition}
                GROUP BY jenis_belanja
            """, params)
            per_jenis = [dict(row) for row in cursor.fetchall()]

            return {
                'total_transaksi': total,
                'per_status': per_status,
                'nilai': nilai,
                'per_jenis_belanja': per_jenis,
            }

    # ========================================================================
    # DOKUMEN TRANSAKSI CRUD
    # ========================================================================

    def create_dokumen(self, transaksi_id: int, data: Dict[str, Any]) -> int:
        """Create dokumen untuk transaksi."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO dokumen_transaksi (
                    transaksi_id, fase, kode_dokumen, nama_dokumen,
                    kategori, template_path, file_path, status,
                    catatan, nomor_dokumen, tanggal_dokumen, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaksi_id,
                data.get('fase', 1),
                data.get('kode_dokumen', ''),
                data.get('nama_dokumen', ''),
                data.get('kategori', KategoriDokumen.WAJIB),
                data.get('template_path'),
                data.get('file_path'),
                data.get('status', StatusDokumen.PENDING),
                data.get('catatan'),
                data.get('nomor_dokumen'),
                data.get('tanggal_dokumen'),
                data.get('created_by'),
            ))

            conn.commit()
            return cursor.lastrowid

    def get_dokumen_by_transaksi(
        self,
        transaksi_id: int,
        fase: int = None
    ) -> List[Dict[str, Any]]:
        """Get semua dokumen untuk transaksi, optional filter by fase."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if fase:
                cursor.execute("""
                    SELECT * FROM dokumen_transaksi
                    WHERE transaksi_id = ? AND fase = ?
                    ORDER BY id
                """, (transaksi_id, fase))
            else:
                cursor.execute("""
                    SELECT * FROM dokumen_transaksi
                    WHERE transaksi_id = ?
                    ORDER BY fase, id
                """, (transaksi_id,))

            return [dict(row) for row in cursor.fetchall()]

    def update_dokumen(self, dokumen_id: int, data: Dict[str, Any]) -> bool:
        """Update dokumen."""
        allowed_fields = ['file_path', 'status', 'catatan', 'nomor_dokumen', 'tanggal_dokumen']

        updates = []
        values = []

        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = ?")
                values.append(data[field])

        if not updates:
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(dokumen_id)

        query = f"UPDATE dokumen_transaksi SET {', '.join(updates)} WHERE id = ?"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

    def update_dokumen_status(self, dokumen_id: int, status: str, file_path: str = None) -> bool:
        """Update status dokumen."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if file_path:
                cursor.execute("""
                    UPDATE dokumen_transaksi
                    SET status = ?, file_path = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, file_path, dokumen_id))
            else:
                cursor.execute("""
                    UPDATE dokumen_transaksi
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, dokumen_id))

            conn.commit()
            return cursor.rowcount > 0

    def get_dokumen_progress(self, transaksi_id: int) -> Dict[str, Any]:
        """Get progress dokumen per fase untuk transaksi."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    fase,
                    COUNT(*) as total,
                    SUM(CASE WHEN status IN ('final', 'signed', 'uploaded') THEN 1 ELSE 0 END) as selesai,
                    SUM(CASE WHEN kategori = 'wajib' THEN 1 ELSE 0 END) as total_wajib,
                    SUM(CASE WHEN kategori = 'wajib' AND status IN ('final', 'signed', 'uploaded') THEN 1 ELSE 0 END) as selesai_wajib
                FROM dokumen_transaksi
                WHERE transaksi_id = ?
                GROUP BY fase
                ORDER BY fase
            """, (transaksi_id,))

            result = {}
            for row in cursor.fetchall():
                fase = row['fase']
                result[fase] = {
                    'total': row['total'],
                    'selesai': row['selesai'],
                    'total_wajib': row['total_wajib'],
                    'selesai_wajib': row['selesai_wajib'],
                    'progress_persen': round(row['selesai'] / row['total'] * 100) if row['total'] > 0 else 0,
                    'wajib_lengkap': row['selesai_wajib'] >= row['total_wajib']
                }

            return result

    # ========================================================================
    # FASE LOG
    # ========================================================================

    def _log_fase(
        self,
        conn,
        transaksi_id: int,
        fase_dari: int,
        fase_ke: int,
        aksi: str,
        catatan: str = None
    ):
        """Internal: Log perpindahan fase."""
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fase_log (transaksi_id, fase_dari, fase_ke, aksi, catatan)
            VALUES (?, ?, ?, ?, ?)
        """, (transaksi_id, fase_dari, fase_ke, aksi, catatan))

    def get_fase_log(self, transaksi_id: int) -> List[Dict[str, Any]]:
        """Get history log fase untuk transaksi."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM fase_log
                WHERE transaksi_id = ?
                ORDER BY created_at DESC
            """, (transaksi_id,))

            return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # SALDO UP
    # ========================================================================

    def get_saldo_up(self, tahun: int = None, bulan: int = None) -> Dict[str, Any]:
        """
        Get saldo UP untuk periode tertentu.

        Args:
            tahun: Tahun anggaran (default: tahun sekarang)
            bulan: Bulan (default: bulan sekarang)

        Returns:
            Dictionary dengan info saldo UP
        """
        if tahun is None:
            tahun = TAHUN_ANGGARAN
        if bulan is None:
            bulan = datetime.now().month

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get or create saldo record
            cursor.execute("""
                INSERT INTO saldo_up (tahun_anggaran, bulan, saldo_awal)
                VALUES (?, ?, ?)
                ON CONFLICT(tahun_anggaran, bulan) DO NOTHING
            """, (tahun, bulan, BATAS_UP_MAKSIMAL))
            conn.commit()

            cursor.execute("""
                SELECT * FROM saldo_up
                WHERE tahun_anggaran = ? AND bulan = ?
            """, (tahun, bulan))

            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['saldo_tersedia'] = data['saldo_awal'] - data['total_penggunaan'] + data['total_pertanggungjawaban']
                return data

            return {
                'tahun_anggaran': tahun,
                'bulan': bulan,
                'saldo_awal': BATAS_UP_MAKSIMAL,
                'total_penggunaan': 0,
                'total_pertanggungjawaban': 0,
                'saldo_tersedia': BATAS_UP_MAKSIMAL,
            }

    def update_saldo_up(
        self,
        tahun: int,
        bulan: int,
        penggunaan_delta: float = 0,
        pertanggungjawaban_delta: float = 0
    ) -> bool:
        """Update saldo UP dengan delta penggunaan/pertanggungjawaban."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE saldo_up
                SET
                    total_penggunaan = total_penggunaan + ?,
                    total_pertanggungjawaban = total_pertanggungjawaban + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE tahun_anggaran = ? AND bulan = ?
            """, (penggunaan_delta, pertanggungjawaban_delta, tahun, bulan))

            conn.commit()
            return cursor.rowcount > 0

    def cek_ketersediaan_up(self, jumlah: float, tahun: int = None, bulan: int = None) -> Tuple[bool, float]:
        """
        Cek apakah saldo UP cukup untuk pencairan.

        Args:
            jumlah: Jumlah yang akan dicairkan
            tahun: Tahun anggaran
            bulan: Bulan

        Returns:
            Tuple (tersedia, saldo_sekarang)
        """
        saldo = self.get_saldo_up(tahun, bulan)
        tersedia = saldo['saldo_tersedia'] >= jumlah
        return tersedia, saldo['saldo_tersedia']

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def get_jenis_belanja_options(self) -> List[Dict[str, str]]:
        """Get list jenis belanja untuk dropdown."""
        return JENIS_BELANJA

    def get_akun_default(self, jenis_belanja: str) -> str:
        """Get kode akun default untuk jenis belanja."""
        for jenis in JENIS_BELANJA:
            if jenis['kode'] == jenis_belanja:
                return jenis['akun_default']
        return ""

    def get_satker_aktif(self) -> Dict[str, str]:
        """
        Get data satuan kerja aktif untuk template dokumen.
        
        Returns:
            Dictionary dengan data satker untuk placeholder dokumen:
            - satker_kementerian: Nama kementerian
            - satker_eselon1: Nama unit eselon 1
            - satker_nama: Nama satuan kerja
            - satker_kode: Kode satker
            - satker_alamat: Alamat lengkap
            - satker_kota: Kota/Kabupaten
            - satker_telepon: Nomor telepon
            - satker_email: Alamat email
        """
        # Default satker data - Politeknik Kelautan dan Perikanan Sorong
        return {
            'satker_kementerian': 'Kementerian Kelautan dan Perikanan',
            'satker_eselon1': 'Direktorat Jenderal Perikanan Budidaya',
            'satker_nama': 'Politeknik Kelautan dan Perikanan Sorong',
            'satker_kode': '314062',
            'satker_alamat': 'Jl. Macam Jaya, Sorong, Papua Barat',
            'satker_kota': 'Sorong',
            'satker_telepon': '(0951) 321-234',
            'satker_email': 'pkp-sorong@kkp.go.id',
        }

    def hitung_selisih(self, transaksi_id: int) -> Dict[str, Any]:
        """
        Hitung selisih uang muka vs realisasi.

        Returns:
            Dictionary dengan:
            - uang_muka
            - realisasi
            - selisih (bisa positif/negatif)
            - status: KURANG_BAYAR, LEBIH_BAYAR, atau PAS
        """
        transaksi = self.get_transaksi(transaksi_id)
        if not transaksi:
            return None

        uang_muka = transaksi.get('uang_muka', 0) or 0
        realisasi = transaksi.get('realisasi', 0) or 0
        selisih = realisasi - uang_muka

        if selisih > 0:
            status = "KURANG_BAYAR"
        elif selisih < 0:
            status = "LEBIH_BAYAR"
        else:
            status = "PAS"

        return {
            'uang_muka': uang_muka,
            'realisasi': realisasi,
            'selisih': selisih,
            'selisih_abs': abs(selisih),
            'status': status,
        }

    def hitung_countdown_tup(self, transaksi_id: int) -> Optional[Dict[str, Any]]:
        """
        Hitung sisa hari untuk TUP.

        Returns:
            Dictionary dengan:
            - tanggal_sp2d
            - batas_waktu
            - sisa_hari
            - is_overdue
        """
        transaksi = self.get_transaksi(transaksi_id)
        if not transaksi or transaksi.get('mekanisme') != 'TUP':
            return None

        tanggal_sp2d = transaksi.get('tanggal_sp2d_tup')
        if not tanggal_sp2d:
            return None

        if isinstance(tanggal_sp2d, str):
            tanggal_sp2d = datetime.strptime(tanggal_sp2d, '%Y-%m-%d').date()

        from datetime import timedelta
        batas_waktu = tanggal_sp2d + timedelta(days=BATAS_TUP_HARI)
        hari_ini = date.today()
        sisa_hari = (batas_waktu - hari_ini).days

    def hitung_countdown_tup(self, transaksi_id: int) -> Optional[Dict[str, Any]]:
        """
        Hitung sisa hari untuk TUP.

        Returns:
            Dictionary dengan:
            - tanggal_sp2d
            - batas_waktu
            - sisa_hari
            - is_overdue
        """
        transaksi = self.get_transaksi(transaksi_id)
        if not transaksi or transaksi.get('mekanisme') != 'TUP':
            return None

        tanggal_sp2d = transaksi.get('tanggal_sp2d_tup')
        if not tanggal_sp2d:
            return None

        if isinstance(tanggal_sp2d, str):
            tanggal_sp2d = datetime.strptime(tanggal_sp2d, '%Y-%m-%d').date()

        from datetime import timedelta
        batas_waktu = tanggal_sp2d + timedelta(days=BATAS_TUP_HARI)
        hari_ini = date.today()
        sisa_hari = (batas_waktu - hari_ini).days

        return {
            'tanggal_sp2d': tanggal_sp2d,
            'batas_waktu': batas_waktu,
            'sisa_hari': sisa_hari,
            'is_overdue': sisa_hari < 0,
        }

    # ========================================================================
    # LEMBAR PERMINTAAN CRUD
    # ========================================================================

    def create_lembar_permintaan(self, data: Dict[str, Any]) -> int:
        """
        Create lembar permintaan baru di database.
        
        Args:
            data: Dictionary dengan fields:
                - hari_tanggal (DATE)
                - unit_kerja (TEXT) - required
                - sumber_dana (TEXT)
                - kode_transaksi (TEXT) - optional, foreign key
                - subtotal, ppn, total (REAL)
                - nama_pengajuan, nama_verifikator, nama_ppk, nama_atasan, nama_kpa
                - file_path (TEXT) - path ke dokumen Word yang generated
                - created_by (TEXT)
                
        Returns:
            ID lembar_permintaan yang baru dibuat
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO lembar_permintaan (
                    hari_tanggal, unit_kerja, sumber_dana, kode_transaksi,
                    subtotal, ppn, total,
                    nama_pengajuan, nama_verifikator, nama_ppk, nama_atasan, nama_kpa,
                    file_path, status, tahun_anggaran, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('hari_tanggal'),
                data.get('unit_kerja', ''),
                data.get('sumber_dana'),
                data.get('kode_transaksi'),
                data.get('subtotal', 0),
                data.get('ppn', 0),
                data.get('total', 0),
                data.get('nama_pengajuan'),
                data.get('nama_verifikator'),
                data.get('nama_ppk'),
                data.get('nama_atasan'),
                data.get('nama_kpa'),
                data.get('file_path'),
                data.get('status', 'draft'),
                data.get('tahun_anggaran', TAHUN_ANGGARAN),
                data.get('created_by'),
            ))
            
            conn.commit()
            return cursor.lastrowid

    def add_lembar_permintaan_item(self, lembar_id: int, item_data: Dict[str, Any]) -> int:
        """
        Add item/rincian barang ke lembar permintaan.
        
        Args:
            lembar_id: ID lembar_permintaan
            item_data: Dictionary dengan:
                - item_no, nama_barang, spesifikasi, volume, satuan,
                  harga_satuan, total_item, keterangan
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO lembar_permintaan_item (
                    lembar_permintaan_id, item_no, nama_barang, spesifikasi,
                    volume, satuan, harga_satuan, total_item, keterangan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lembar_id,
                item_data.get('item_no'),
                item_data.get('nama_barang'),
                item_data.get('spesifikasi'),
                item_data.get('volume'),
                item_data.get('satuan'),
                item_data.get('harga_satuan'),
                item_data.get('total_item'),
                item_data.get('keterangan'),
            ))
            
            conn.commit()
            return cursor.lastrowid

    def get_lembar_permintaan(self, lembar_id: int) -> Optional[Dict[str, Any]]:
        """Get lembar permintaan by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lembar_permintaan WHERE id = ?", (lembar_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_lembar_permintaan_by_kode_transaksi(self, kode_transaksi: str) -> Optional[Dict[str, Any]]:
        """Get lembar permintaan by kode_transaksi."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM lembar_permintaan WHERE kode_transaksi = ? ORDER BY created_at DESC",
                (kode_transaksi,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_lembar_permintaan_items(self, lembar_id: int) -> List[Dict[str, Any]]:
        """Get semua item dalam lembar permintaan."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM lembar_permintaan_item WHERE lembar_permintaan_id = ? ORDER BY item_no",
                (lembar_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_lembar_permintaan(self, lembar_id: int, data: Dict[str, Any]) -> bool:
        """Update lembar permintaan."""
        allowed_fields = [
            'hari_tanggal', 'unit_kerja', 'sumber_dana',
            'subtotal', 'ppn', 'total',
            'nama_pengajuan', 'nama_verifikator', 'nama_ppk', 'nama_atasan', 'nama_kpa',
            'file_path', 'status'
        ]
        
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = ?")
                values.append(data[field])
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(lembar_id)
        
        query = f"UPDATE lembar_permintaan SET {', '.join(updates)} WHERE id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

    def list_lembar_permintaan(self, tahun: int = None, status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List lembar_permintaan dengan optional filter.
        
        Args:
            tahun: Filter by tahun_anggaran
            status: Filter by status
            limit: Limit hasil
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM lembar_permintaan WHERE 1=1"
            params = []
            
            if tahun:
                query += " AND tahun_anggaran = ?"
                params.append(tahun)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_lembar_permintaan_with_items(self, lembar_id: int) -> Optional[Dict[str, Any]]:
        """
        Get lembar permintaan beserta semua items-nya.
        Digunakan untuk workflow phase berikutnya.
        
        Returns:
            Dictionary dengan struktur:
            {
                'lembar': {...},  # Data lembar_permintaan
                'items': [...],   # List items
                'summary': {
                    'jumlah_item': int,
                    'subtotal': float,
                    'ppn': float,
                    'total': float
                }
            }
        """
        lembar = self.get_lembar_permintaan(lembar_id)
        if not lembar:
            return None
        
        items = self.get_lembar_permintaan_items(lembar_id)
        
        return {
            'lembar': lembar,
            'items': items,
            'summary': {
                'jumlah_item': len(items),
                'subtotal': lembar.get('subtotal', 0),
                'ppn': lembar.get('ppn', 0),
                'total': lembar.get('total', 0),
            }
        }

    def get_lembar_permintaan_for_next_phase(self, lembar_id: int, target_dokumen: str = None) -> Optional[Dict[str, Any]]:
        """
        Get lembar_permintaan data yang sudah diformat untuk digunakan di phase berikutnya.
        Contoh: Data untuk SPJ, Kuitansi, Realisasi, dst.
        
        Args:
            lembar_id: ID lembar_permintaan
            target_dokumen: Jenis dokumen target (opsional, untuk custom formatting)
        
        Returns:
            Dictionary dengan data yang sudah diformat untuk fase berikutnya
        """
        data = self.get_lembar_permintaan_with_items(lembar_id)
        if not data:
            return None
        
        lembar = data['lembar']
        items = data['items']
        
        # Format untuk penggunaan di next phase
        formatted_data = {
            # Referensi ke lembar_permintaan
            'lembar_permintaan_id': lembar_id,
            'kode_transaksi': lembar.get('kode_transaksi'),
            'file_lembar': lembar.get('file_path'),
            
            # Data header
            'tanggal': lembar.get('hari_tanggal'),
            'unit_kerja': lembar.get('unit_kerja'),
            'sumber_dana': lembar.get('sumber_dana'),
            
            # Penandatangan (untuk refrrensi)
            'pengajuan_oleh': lembar.get('nama_pengajuan'),
            'verifikasi_oleh': lembar.get('nama_verifikator'),
            'ppk': lembar.get('nama_ppk'),
            'atasan': lembar.get('nama_atasan'),
            'kpa': lembar.get('nama_kpa'),
            
            # Nilai finansial
            'subtotal': lembar.get('subtotal', 0),
            'ppn': lembar.get('ppn', 0),
            'total': lembar.get('total', 0),
            
            # Items untuk rincian detail
            'rincian_items': items,
            
            # Metadata
            'status_lembar': lembar.get('status'),
            'tanggal_buat': lembar.get('created_at'),
        }
        
        return formatted_data

    def link_lembar_to_dokumen(self, lembar_id: int, transaksi_id: int, fase: int = 2) -> bool:
        """
        Link lembar_permintaan ke transaksi_pencairan untuk fase berikutnya.
        Ini menciptakan relasi antara lembar_permintaan dan proses selanjutnya.
        
        Args:
            lembar_id: ID lembar_permintaan
            transaksi_id: ID transaksi_pencairan
            fase: Fase target (default 2 = phase 2)
        
        Returns:
            True jika berhasil di-link
        """
        try:
            lembar = self.get_lembar_permintaan(lembar_id)
            if not lembar:
                return False
            
            # Update transaksi dengan reference ke lembar_permintaan
            # (melalui kode_transaksi yang sudah ada di lembar)
            return True
            
        except Exception as e:
            print(f"Error linking lembar_permintaan: {e}")
            return False

    def get_rincian_from_lembar(self, lembar_id: int) -> List[Dict[str, Any]]:
        """
        Extract rincian barang/jasa dari lembar_permintaan.
        Format sesuai untuk dokumen selanjutnya (SPJ, Kuitansi, dst).
        
        Returns:
            List rincian dengan fields: nama_barang, spesifikasi, volume, satuan,
                                       harga_satuan, total_item, keterangan
        """
        items = self.get_lembar_permintaan_items(lembar_id)
        
        # Format untuk penggunaan di dokumen selanjutnya
        rincian = []
        for item in items:
            rincian.append({
                'no': item.get('item_no'),
                'nama_barang': item.get('nama_barang'),
                'spesifikasi': item.get('spesifikasi'),
                'volume': item.get('volume'),
                'satuan': item.get('satuan'),
                'harga_satuan': item.get('harga_satuan'),
                'jumlah': item.get('total_item'),  # Alias untuk total_item
                'keterangan': item.get('keterangan'),
            })
        
        return rincian

    def create_dokumen_from_lembar(self, lembar_id: int, tipe_dokumen: str, fase: int = 2) -> bool:
        """
        Create dokumen_transaksi berdasarkan lembar_permintaan.
        Digunakan saat melanjutkan ke fase berikutnya.
        
        Args:
            lembar_id: ID lembar_permintaan
            tipe_dokumen: Tipe dokumen berikutnya (e.g., 'SPJ', 'KUITANSI', 'REALISASI')
            fase: Fase target
        
        Returns:
            True jika berhasil create
        """
        try:
            data = self.get_lembar_permintaan_for_next_phase(lembar_id)
            if not data:
                return False
            
            kode_transaksi = data.get('kode_transaksi')
            if not kode_transaksi:
                return False
            
            # Get transaksi_id dari kode_transaksi
            transaksi = self.get_transaksi_by_kode(kode_transaksi)
            if not transaksi:
                return False
            
            transaksi_id = transaksi.get('id')
            
            # Create dokumen_transaksi
            dokumen_data = {
                'fase': fase,
                'kode_dokumen': f'{tipe_dokumen}_{kode_transaksi}',
                'nama_dokumen': f'{tipe_dokumen} untuk {kode_transaksi}',
                'kategori': 'wajib',
                'template_path': f'{tipe_dokumen.lower()}_template.docx',
                'status': 'pending',
                'created_by': 'system',
            }
            
            self.create_dokumen(transaksi_id, dokumen_data)
            return True
            
        except Exception as e:
            print(f"Error create_dokumen_from_lembar: {e}")
            return False


# ============================================================================
# INITIALIZATION FUNCTIONS
# ============================================================================

def init_pencairan_tables(db_path: str = None):
    """
    Initialize pencairan tables di database.
    Dipanggil saat aplikasi pertama kali dijalankan.
    """
    manager = PencairanManager(db_path)
    return manager


# Test code
if __name__ == "__main__":
    manager = PencairanManager()

    # Test create transaksi
    data = {
        'mekanisme': 'UP',
        'jenis_belanja': 'jamuan',
        'nama_kegiatan': 'Rapat Koordinasi Tim Teknis',
        'estimasi_biaya': 5000000,
        'penerima_nama': 'Budi Santoso',
        'penerima_nip': '198501012010011001',
    }

    transaksi_id = manager.create_transaksi(data)
    print(f"Created transaksi: {transaksi_id}")

    # Get transaksi
    transaksi = manager.get_transaksi(transaksi_id)
    print(f"Transaksi: {transaksi}")

    # Get saldo UP
    saldo = manager.get_saldo_up()
    print(f"Saldo UP: {saldo}")
