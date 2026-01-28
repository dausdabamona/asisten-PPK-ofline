"""
Model database untuk sistem pencairan dana workflow-based.
Tabel utama:
1. transaksi_pencairan - Master transaksi
2. dokumen_transaksi - Dokumen per fase
3. fase_log - Log perpindahan fase
4. saldo_up - Tracking saldo UP
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from contextlib import contextmanager

# ============================================================================
# SCHEMA DEFINITION
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
    selisih REAL GENERATED ALWAYS AS (realisasi - uang_muka) STORED,
    
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
    
    -- Penyedia (untuk LS)
    penyedia_id INTEGER,
    nilai_kontrak REAL,
    nomor_kontrak TEXT,
    
    -- Kode Akun
    kode_akun TEXT,
    nama_akun TEXT,
    
    -- Timestamp
    tanggal_kegiatan_mulai DATE,
    tanggal_kegiatan_selesai DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (penyedia_id) REFERENCES penyedia(id)
);
"""

SCHEMA_DOKUMEN_TRANSAKSI = """
CREATE TABLE IF NOT EXISTS dokumen_transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaksi_id INTEGER NOT NULL,
    fase INTEGER NOT NULL CHECK (fase BETWEEN 1 AND 5),
    kode_dokumen TEXT NOT NULL,
    nama_dokumen TEXT NOT NULL,
    kategori TEXT DEFAULT 'wajib' CHECK (kategori IN ('wajib', 'opsional', 'upload')),
    template_file TEXT,
    file_path TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'draft', 'final', 'signed', 'uploaded')),
    catatan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(transaksi_id, kode_dokumen),
    FOREIGN KEY (transaksi_id) REFERENCES transaksi_pencairan(id) ON DELETE CASCADE
);
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
    FOREIGN KEY (transaksi_id) REFERENCES transaksi_pencairan(id) ON DELETE CASCADE
);
"""

SCHEMA_SALDO_UP = """
CREATE TABLE IF NOT EXISTS saldo_up (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tahun_anggaran INTEGER NOT NULL,
    bulan INTEGER NOT NULL,
    saldo_awal REAL NOT NULL DEFAULT 50000000,
    total_penggunaan REAL DEFAULT 0,
    total_pertanggungjawaban REAL DEFAULT 0,
    saldo_tersedia REAL GENERATED ALWAYS AS (saldo_awal - total_penggunaan + total_pertanggungjawaban) STORED,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tahun_anggaran, bulan)
);
"""

# ============================================================================
# DATABASE MANAGER CLASS
# ============================================================================

class PencairanDanaManager:
    """Manager untuk operasi database pencairan dana"""
    
    def __init__(self, db_path: str):
        """
        Initialize database manager
        
        Args:
            db_path: Path ke file database SQLite
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Inisialisasi database dengan schema yang diperlukan"""
        with self.get_connection() as conn:
            conn.execute(SCHEMA_TRANSAKSI_PENCAIRAN)
            conn.execute(SCHEMA_DOKUMEN_TRANSAKSI)
            conn.execute(SCHEMA_FASE_LOG)
            conn.execute(SCHEMA_SALDO_UP)
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager untuk database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    # ========================================================================
    # TRANSAKSI PENCAIRAN CRUD
    # ========================================================================
    
    def create_transaksi(self, data: Dict[str, Any]) -> int:
        """
        Buat transaksi pencairan baru
        
        Args:
            data: Dictionary berisi field transaksi
                  {mekanisme, jenis_belanja, nama_kegiatan, estimasi_biaya, ...}
        
        Returns:
            ID transaksi yang baru dibuat
        """
        # Generate kode transaksi
        kode = self._generate_kode_transaksi(data['mekanisme'])
        data['kode_transaksi'] = kode
        data['fase_aktif'] = 1
        data['status'] = 'draft'
        
        fields = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO transaksi_pencairan ({fields}) VALUES ({placeholders})"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid
    
    def get_transaksi(self, transaksi_id: int) -> Optional[Dict]:
        """Get transaksi by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transaksi_pencairan WHERE id = ?", (transaksi_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_transaksi_by_kode(self, kode: str) -> Optional[Dict]:
        """Get transaksi by kode"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transaksi_pencairan WHERE kode_transaksi = ?", (kode,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_transaksi(self, mekanisme: Optional[str] = None, 
                      status: Optional[str] = None,
                      limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        List transaksi dengan filter
        
        Args:
            mekanisme: Filter by mekanisme ('UP', 'TUP', 'LS')
            status: Filter by status
            limit: Limit hasil
            offset: Offset hasil
        
        Returns:
            List transaksi
        """
        query = "SELECT * FROM transaksi_pencairan WHERE 1=1"
        params = []
        
        if mekanisme:
            query += " AND mekanisme = ?"
            params.append(mekanisme)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_transaksi(self, transaksi_id: int, data: Dict[str, Any]) -> bool:
        """Update transaksi"""
        data['updated_at'] = datetime.now().isoformat()
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE transaksi_pencairan SET {set_clause} WHERE id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()) + (transaksi_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_transaksi(self, transaksi_id: int) -> bool:
        """Delete transaksi (soft delete: ubah status menjadi batal)"""
        return self.update_transaksi(transaksi_id, {'status': 'batal'})
    
    def count_transaksi(self, mekanisme: Optional[str] = None,
                       status: Optional[str] = None) -> int:
        """Count transaksi dengan filter"""
        query = "SELECT COUNT(*) as count FROM transaksi_pencairan WHERE 1=1"
        params = []
        
        if mekanisme:
            query += " AND mekanisme = ?"
            params.append(mekanisme)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['count'] if result else 0
    
    # ========================================================================
    # DOKUMEN TRANSAKSI CRUD
    # ========================================================================
    
    def create_dokumen(self, transaksi_id: int, fase: int, 
                      kode_dokumen: str, nama_dokumen: str,
                      kategori: str = 'wajib', template_file: Optional[str] = None) -> int:
        """Buat record dokumen transaksi"""
        data = {
            'transaksi_id': transaksi_id,
            'fase': fase,
            'kode_dokumen': kode_dokumen,
            'nama_dokumen': nama_dokumen,
            'kategori': kategori,
            'template_file': template_file,
            'status': 'pending'
        }
        
        fields = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO dokumen_transaksi ({fields}) VALUES ({placeholders})"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid
    
    def get_dokumen(self, dokumen_id: int) -> Optional[Dict]:
        """Get dokumen by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dokumen_transaksi WHERE id = ?", (dokumen_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_dokumen_by_transaksi(self, transaksi_id: int, 
                                 fase: Optional[int] = None) -> List[Dict]:
        """List dokumen per transaksi"""
        query = "SELECT * FROM dokumen_transaksi WHERE transaksi_id = ?"
        params = [transaksi_id]
        
        if fase:
            query += " AND fase = ?"
            params.append(fase)
        
        query += " ORDER BY fase, kategori"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_dokumen(self, dokumen_id: int, data: Dict[str, Any]) -> bool:
        """Update dokumen"""
        data['updated_at'] = datetime.now().isoformat()
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE dokumen_transaksi SET {set_clause} WHERE id = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()) + (dokumen_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_dokumen_status(self, dokumen_id: int, status: str) -> bool:
        """Update status dokumen"""
        return self.update_dokumen(dokumen_id, {'status': status})
    
    def update_dokumen_file(self, dokumen_id: int, file_path: str) -> bool:
        """Update file path dokumen"""
        return self.update_dokumen(dokumen_id, {'file_path': file_path, 'status': 'draft'})
    
    def count_dokumen_by_status(self, transaksi_id: int, fase: int, 
                               kategori: str = 'wajib') -> Dict[str, int]:
        """Count dokumen per status"""
        query = """
            SELECT status, COUNT(*) as count 
            FROM dokumen_transaksi 
            WHERE transaksi_id = ? AND fase = ? AND kategori = ?
            GROUP BY status
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (transaksi_id, fase, kategori))
            result = {row['status']: row['count'] for row in cursor.fetchall()}
        
        return result
    
    # ========================================================================
    # FASE MANAGEMENT
    # ========================================================================
    
    def pindah_fase(self, transaksi_id: int, fase_ke: int, 
                   aksi: str, catatan: Optional[str] = None) -> bool:
        """
        Pindah transaksi ke fase berikutnya
        
        Args:
            transaksi_id: ID transaksi
            fase_ke: Target fase (1-5)
            aksi: Deskripsi aksi (e.g., 'Lanjut ke fase persiapan')
            catatan: Catatan tambahan
        
        Returns:
            True jika berhasil
        """
        transaksi = self.get_transaksi(transaksi_id)
        if not transaksi:
            return False
        
        fase_dari = transaksi['fase_aktif']
        
        # Log perubahan fase
        log_data = {
            'transaksi_id': transaksi_id,
            'fase_dari': fase_dari,
            'fase_ke': fase_ke,
            'aksi': aksi,
            'catatan': catatan
        }
        
        fields = ', '.join(log_data.keys())
        placeholders = ', '.join(['?' for _ in log_data])
        query = f"INSERT INTO fase_log ({fields}) VALUES ({placeholders})"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(log_data.values()))
            
            # Update fase aktif
            cursor.execute(
                "UPDATE transaksi_pencairan SET fase_aktif = ?, status = ? WHERE id = ?",
                (fase_ke, 'aktif' if fase_ke < 5 else 'selesai', transaksi_id)
            )
            conn.commit()
        
        return True
    
    def get_fase_log(self, transaksi_id: int) -> List[Dict]:
        """Get log perubahan fase"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM fase_log WHERE transaksi_id = ? ORDER BY created_at",
                (transaksi_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ========================================================================
    # SALDO UP MANAGEMENT
    # ========================================================================
    
    def get_saldo_up(self, tahun: int, bulan: int) -> Optional[Dict]:
        """Get saldo UP untuk tahun dan bulan tertentu"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM saldo_up WHERE tahun_anggaran = ? AND bulan = ?",
                (tahun, bulan)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def init_saldo_up(self, tahun: int, bulan: int, 
                     saldo_awal: float = 50000000) -> bool:
        """Inisialisasi saldo UP untuk bulan tertentu"""
        data = {
            'tahun_anggaran': tahun,
            'bulan': bulan,
            'saldo_awal': saldo_awal,
            'total_penggunaan': 0,
            'total_pertanggungjawaban': 0
        }
        
        fields = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT OR IGNORE INTO saldo_up ({fields}) VALUES ({placeholders})"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_penggunaan_up(self, tahun: int, bulan: int, 
                            estimasi_biaya: float, tambah: bool = True) -> bool:
        """Update total penggunaan UP"""
        operator = '+' if tambah else '-'
        query = f"""
            UPDATE saldo_up 
            SET total_penggunaan = total_penggunaan {operator} ?
            WHERE tahun_anggaran = ? AND bulan = ?
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (estimasi_biaya, tahun, bulan))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_saldo_tersedia(self, tahun: int, bulan: int) -> float:
        """Get saldo UP yang masih tersedia"""
        saldo = self.get_saldo_up(tahun, bulan)
        if not saldo:
            return 0
        
        # saldo_tersedia = saldo_awal - total_penggunaan + total_pertanggungjawaban
        return (saldo['saldo_awal'] - saldo['total_penggunaan'] + 
                saldo['total_pertanggungjawaban'])
    
    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================
    
    def _generate_kode_transaksi(self, mekanisme: str) -> str:
        """Generate kode transaksi unik"""
        from datetime import datetime
        
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Count existing transaksi untuk bulan ini
        query = """
            SELECT COUNT(*) as count FROM transaksi_pencairan 
            WHERE mekanisme = ? 
            AND strftime('%Y-%m', created_at) = ?
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (mekanisme, f"{year}-{month:02d}"))
            result = cursor.fetchone()
            count = result['count'] + 1 if result else 1
        
        # Format: UP-2026-01-001, TUP-2026-01-001, LS-2026-01-001
        kode = f"{mekanisme}-{year}-{month:02d}-{count:03d}"
        return kode
    
    def get_statistik_pencairan(self, tahun: Optional[int] = None) -> Dict[str, Any]:
        """Get statistik pencairan dana"""
        from datetime import datetime
        
        tahun = tahun or datetime.now().year
        
        stats = {}
        for mekanisme in ['UP', 'TUP', 'LS']:
            draft = self.count_transaksi(mekanisme=mekanisme, status='draft')
            aktif = self.count_transaksi(mekanisme=mekanisme, status='aktif')
            selesai = self.count_transaksi(mekanisme=mekanisme, status='selesai')
            
            stats[mekanisme] = {
                'draft': draft,
                'aktif': aktif,
                'selesai': selesai,
                'total': draft + aktif + selesai
            }
        
        return stats


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def get_pencairan_manager(db_path: Optional[str] = None) -> PencairanDanaManager:
    """Get atau buat PencairanDanaManager instance"""
    if db_path is None:
        from app.core.config import DATABASE_PATH
        db_path = DATABASE_PATH
    
    return PencairanDanaManager(db_path)
