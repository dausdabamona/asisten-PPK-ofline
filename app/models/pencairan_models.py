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

SCHEMA_RINCIAN_TRANSAKSI = """
CREATE TABLE IF NOT EXISTS rincian_transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaksi_id INTEGER NOT NULL,
    nomor_urut INTEGER DEFAULT 1,
    uraian TEXT NOT NULL,
    volume REAL DEFAULT 1,
    satuan TEXT DEFAULT 'paket',
    harga_satuan REAL DEFAULT 0,
    jumlah REAL DEFAULT 0,

    -- For tax calculations
    ppn_persen REAL DEFAULT 0,
    ppn_nilai REAL DEFAULT 0,

    -- For uang muka calculations
    uang_muka_persen REAL DEFAULT 100,
    uang_muka_nilai REAL DEFAULT 0,

    -- Document reference - which document generated this
    kode_dokumen TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (transaksi_id) REFERENCES transaksi_pencairan(id) ON DELETE CASCADE
);

-- Index for fast lookup
CREATE INDEX IF NOT EXISTS idx_rincian_transaksi ON rincian_transaksi(transaksi_id);
CREATE INDEX IF NOT EXISTS idx_rincian_dokumen ON rincian_transaksi(transaksi_id, kode_dokumen);
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
            cursor.executescript(SCHEMA_RINCIAN_TRANSAKSI)

            # Run migrations for existing databases
            self._run_migrations(cursor)

            conn.commit()

    def _run_migrations(self, cursor):
        """Run database migrations for existing databases."""
        # Placeholder for future migrations
        pass

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
                    kode_akun, nama_akun,
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
                    ?, ?,
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
            'kode_akun', 'nama_akun',
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

        return {
            'tanggal_sp2d': tanggal_sp2d,
            'batas_waktu': batas_waktu,
            'sisa_hari': sisa_hari,
            'is_overdue': sisa_hari < 0,
        }

    # ========================================================================
    # RINCIAN TRANSAKSI CRUD
    # ========================================================================

    def save_rincian_items(
        self,
        transaksi_id: int,
        items: List[Dict[str, Any]],
        kode_dokumen: str = None,
        ppn_persen: float = 0,
        uang_muka_persen: float = 100
    ) -> bool:
        """
        Simpan rincian items untuk transaksi.
        Items yang sudah ada untuk kode_dokumen yang sama akan dihapus dulu.

        Args:
            transaksi_id: ID transaksi
            items: List rincian items
            kode_dokumen: Kode dokumen yang membuat rincian (LBR_REQ, KUIT_UM, dll)
            ppn_persen: Persentase PPN (0 atau 11)
            uang_muka_persen: Persentase uang muka (80, 90, atau 100)

        Returns:
            True jika berhasil
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Delete existing rincian for this transaksi & kode_dokumen
            if kode_dokumen:
                cursor.execute("""
                    DELETE FROM rincian_transaksi
                    WHERE transaksi_id = ? AND kode_dokumen = ?
                """, (transaksi_id, kode_dokumen))
            else:
                cursor.execute("""
                    DELETE FROM rincian_transaksi
                    WHERE transaksi_id = ?
                """, (transaksi_id,))

            # Insert new items
            for i, item in enumerate(items, 1):
                jumlah = item.get('jumlah', 0) or (item.get('volume', 1) * item.get('harga_satuan', 0))
                ppn_nilai = jumlah * ppn_persen / 100 if ppn_persen > 0 else 0
                total_dengan_ppn = jumlah + ppn_nilai
                um_nilai = total_dengan_ppn * uang_muka_persen / 100

                cursor.execute("""
                    INSERT INTO rincian_transaksi (
                        transaksi_id, nomor_urut, uraian, volume, satuan,
                        harga_satuan, jumlah, ppn_persen, ppn_nilai,
                        uang_muka_persen, uang_muka_nilai, kode_dokumen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaksi_id,
                    i,
                    item.get('uraian', ''),
                    item.get('volume', 1),
                    item.get('satuan', 'paket'),
                    item.get('harga_satuan', 0),
                    jumlah,
                    ppn_persen,
                    ppn_nilai,
                    uang_muka_persen,
                    um_nilai,
                    kode_dokumen
                ))

            conn.commit()
            return True

    def get_rincian_items(
        self,
        transaksi_id: int,
        kode_dokumen: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get rincian items untuk transaksi.

        Args:
            transaksi_id: ID transaksi
            kode_dokumen: Optional filter by kode dokumen

        Returns:
            List of rincian items
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if kode_dokumen:
                cursor.execute("""
                    SELECT * FROM rincian_transaksi
                    WHERE transaksi_id = ? AND kode_dokumen = ?
                    ORDER BY nomor_urut
                """, (transaksi_id, kode_dokumen))
            else:
                cursor.execute("""
                    SELECT * FROM rincian_transaksi
                    WHERE transaksi_id = ?
                    ORDER BY kode_dokumen, nomor_urut
                """, (transaksi_id,))

            return [dict(row) for row in cursor.fetchall()]

    def get_rincian_summary(self, transaksi_id: int, kode_dokumen: str = None) -> Dict[str, Any]:
        """
        Get summary of rincian items for transaksi.

        Args:
            transaksi_id: ID transaksi
            kode_dokumen: Optional filter by kode dokumen

        Returns:
            Dictionary with totals
        """
        items = self.get_rincian_items(transaksi_id, kode_dokumen)

        if not items:
            return {
                'total_items': 0,
                'subtotal': 0,
                'ppn_persen': 0,
                'ppn_nilai': 0,
                'total_dengan_ppn': 0,
                'uang_muka_persen': 100,
                'uang_muka_nilai': 0,
            }

        subtotal = sum(item.get('jumlah', 0) for item in items)
        ppn_persen = items[0].get('ppn_persen', 0) if items else 0
        ppn_nilai = sum(item.get('ppn_nilai', 0) for item in items)
        uang_muka_persen = items[0].get('uang_muka_persen', 100) if items else 100
        uang_muka_nilai = sum(item.get('uang_muka_nilai', 0) for item in items)

        return {
            'total_items': len(items),
            'subtotal': subtotal,
            'ppn_persen': ppn_persen,
            'ppn_nilai': ppn_nilai,
            'total_dengan_ppn': subtotal + ppn_nilai,
            'uang_muka_persen': uang_muka_persen,
            'uang_muka_nilai': uang_muka_nilai,
        }

    def delete_rincian_items(self, transaksi_id: int, kode_dokumen: str = None) -> bool:
        """Delete rincian items for transaksi."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if kode_dokumen:
                cursor.execute("""
                    DELETE FROM rincian_transaksi
                    WHERE transaksi_id = ? AND kode_dokumen = ?
                """, (transaksi_id, kode_dokumen))
            else:
                cursor.execute("""
                    DELETE FROM rincian_transaksi
                    WHERE transaksi_id = ?
                """, (transaksi_id,))

            conn.commit()
            return cursor.rowcount > 0

    # ========================================================================
    # SATKER DATA
    # ========================================================================

    def get_satker_aktif(self) -> Dict[str, Any]:
        """Get active satker data with pejabat details."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*,
                    kpa.nama as kpa_nama, kpa.nip as kpa_nip, kpa.jabatan as kpa_jabatan,
                    kpa.pangkat as kpa_pangkat, kpa.golongan as kpa_golongan,
                    ppk.nama as ppk_nama, ppk.nip as ppk_nip, ppk.jabatan as ppk_jabatan,
                    ppk.pangkat as ppk_pangkat, ppk.golongan as ppk_golongan,
                    ppspm.nama as ppspm_nama, ppspm.nip as ppspm_nip, ppspm.jabatan as ppspm_jabatan,
                    ppspm.pangkat as ppspm_pangkat, ppspm.golongan as ppspm_golongan,
                    bendahara.nama as bendahara_nama, bendahara.nip as bendahara_nip,
                    bendahara.jabatan as bendahara_jabatan, bendahara.pangkat as bendahara_pangkat,
                    bendahara.golongan as bendahara_golongan
                FROM satker s
                LEFT JOIN pegawai kpa ON s.kpa_id = kpa.id
                LEFT JOIN pegawai ppk ON s.ppk_id = ppk.id
                LEFT JOIN pegawai ppspm ON s.ppspm_id = ppspm.id
                LEFT JOIN pegawai bendahara ON s.bendahara_id = bendahara.id
                LIMIT 1
            """)
            row = cursor.fetchone()
            return dict(row) if row else {}


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
