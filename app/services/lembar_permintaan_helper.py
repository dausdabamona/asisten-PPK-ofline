"""
Lembar Permintaan Helper Service
=================================
Helper functions untuk mengakses dan menggunakan data lembar_permintaan
di workflow fase-fase selanjutnya (SPJ, Kuitansi, Realisasi, dst).

Fitur:
- Get lembar_permintaan dengan all items
- Extract data untuk dokumen berikutnya
- Link lembar_permintaan ke fase berikutnya
- Generate dokumen dari data lembar
- Sync items ke transaksi_item (master data)
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path

# ============================================================================
# CORE HELPER FUNCTIONS
# ============================================================================

def get_lembar_data_complete(db, lembar_id: int) -> Optional[Dict[str, Any]]:
    """
    Get lembar_permintaan lengkap dengan semua items dan summary.
    
    Args:
        db: PencairanManager instance
        lembar_id: ID lembar_permintaan
    
    Returns:
        Complete data structure atau None jika tidak ada
    """
    if not db:
        return None
    
    return db.get_lembar_permintaan_with_items(lembar_id)


def get_rincian_barang(db, lembar_id: int) -> List[Dict[str, Any]]:
    """
    Get rincian barang/jasa dari lembar_permintaan.
    Format khusus untuk dokumen selanjutnya.
    
    Returns:
        List dengan fields: no, nama_barang, spesifikasi, volume, satuan,
                           harga_satuan, jumlah, keterangan
    """
    if not db:
        return []
    
    return db.get_rincian_from_lembar(lembar_id)


def get_rincian_from_transaksi(db, transaksi_id: int, tipe_dokumen: str = None) -> List[Dict[str, Any]]:
    """
    Get rincian barang/jasa dari transaksi_item (master data).
    Ini adalah method UTAMA untuk mendapatkan rincian di fase selanjutnya.
    
    Args:
        db: PencairanManager instance
        transaksi_id: ID transaksi pencairan
        tipe_dokumen: Tipe dokumen (HPS, SPK, BAST, KUITANSI, dll) untuk format khusus
    
    Returns:
        List dengan fields sesuai kebutuhan dokumen
    """
    if not db:
        return []
    
    return db.get_items_for_dokumen(transaksi_id, tipe_dokumen)


def sync_lembar_to_transaksi_items(db, lembar_id: int, transaksi_id: int = None) -> Tuple[bool, Optional[str], int]:
    """
    Sync items dari lembar_permintaan ke transaksi_item.
    Ini adalah operasi PENTING yang harus dipanggil ketika:
    1. Lembar permintaan di-approve
    2. Transaksi dilanjutkan ke fase berikutnya
    3. Items di-edit dan perlu disinkronkan ulang
    
    Args:
        db: PencairanManager instance
        lembar_id: ID lembar_permintaan
        transaksi_id: ID transaksi (opsional, akan diambil dari kode_transaksi lembar)
    
    Returns:
        Tuple of (success, error_message, items_count)
    """
    if not db:
        return False, "Database connection not available", 0
    
    # Get lembar data
    lembar = db.get_lembar_permintaan(lembar_id)
    if not lembar:
        return False, f"Lembar Permintaan {lembar_id} tidak ditemukan", 0
    
    # Get transaksi_id jika tidak diberikan
    if not transaksi_id:
        kode_transaksi = lembar.get('kode_transaksi')
        if kode_transaksi:
            transaksi = db.get_transaksi_by_kode(kode_transaksi)
            if transaksi:
                transaksi_id = transaksi.get('id')
    
    if not transaksi_id:
        return False, "Transaksi tidak ditemukan untuk lembar ini", 0
    
    # Sync items
    try:
        count = db.sync_items_to_transaksi(transaksi_id, lembar_id)
        return True, None, count
    except Exception as e:
        return False, f"Error sync items: {str(e)}", 0


def approve_lembar_and_sync(db, lembar_id: int, transaksi_id: int = None) -> Tuple[bool, Optional[str]]:
    """
    Approve lembar permintaan dan sync items ke transaksi_item.
    Ini adalah operasi gabungan untuk kemudahan.
    
    Args:
        db: PencairanManager instance
        lembar_id: ID lembar_permintaan
        transaksi_id: ID transaksi (opsional)
    
    Returns:
        Tuple of (success, error_message)
    """
    # Validate dulu
    is_valid, error = validate_lembar_for_next_phase(db, lembar_id)
    if not is_valid:
        return False, error
    
    # Update status ke 'final' (approved)
    success = update_lembar_status(db, lembar_id, 'final')
    if not success:
        return False, "Gagal update status lembar"
    
    # Sync ke transaksi_item
    sync_success, sync_error, count = sync_lembar_to_transaksi_items(db, lembar_id, transaksi_id)
    if not sync_success:
        return False, sync_error
    
    return True, None


def get_nilai_finansial(db, lembar_id: int) -> Optional[Dict[str, float]]:
    """
    Get nilai finansial dari lembar_permintaan.
    
    Returns:
        Dictionary dengan keys: subtotal, ppn, total
    """
    lembar = db.get_lembar_permintaan(lembar_id) if db else None
    if not lembar:
        return None
    
    return {
        'subtotal': lembar.get('subtotal', 0),
        'ppn': lembar.get('ppn', 0),
        'total': lembar.get('total', 0),
    }


def get_penandatangan(db, lembar_id: int) -> Optional[Dict[str, str]]:
    """
    Get data penandatangan dari lembar_permintaan.
    
    Returns:
        Dictionary dengan keys: nama_pengajuan, nama_verifikator, nama_ppk,
                               nama_atasan, nama_kpa
    """
    lembar = db.get_lembar_permintaan(lembar_id) if db else None
    if not lembar:
        return None
    
    return {
        'nama_pengajuan': lembar.get('nama_pengajuan', ''),
        'nama_verifikator': lembar.get('nama_verifikator', ''),
        'nama_ppk': lembar.get('nama_ppk', ''),
        'nama_atasan': lembar.get('nama_atasan', ''),
        'nama_kpa': lembar.get('nama_kpa', ''),
    }


# ============================================================================
# TRANSAKSI ITEM HELPER FUNCTIONS (MASTER DATA)
# ============================================================================

def get_items_from_transaksi(db, transaksi_id: int, status_filter: str = None) -> List[Dict[str, Any]]:
    """
    Get items dari transaksi_item (master data).
    Ini adalah method UTAMA untuk mendapatkan items di semua fase.
    
    Args:
        db: PencairanManager instance
        transaksi_id: ID transaksi pencairan
        status_filter: Filter status optional (diminta, disetujui, dipesan, diterima, diserahterimakan)
    
    Returns:
        List of items dengan full tracking info
    """
    if not db:
        return []
    
    return db.get_transaksi_items(transaksi_id, status_filter)


def get_items_summary_for_transaksi(db, transaksi_id: int) -> Dict[str, Any]:
    """
    Get summary items dari transaksi_item.
    
    Returns:
        Dictionary dengan total_items, total_nilai, items_by_status
    """
    if not db:
        return {'total_items': 0, 'total_nilai': 0, 'items_by_status': {}}
    
    return db.get_items_summary(transaksi_id)


def update_item_in_transaksi(db, item_id: int, updates: Dict[str, Any], user: str = None) -> bool:
    """
    Update item di transaksi_item.
    
    Args:
        db: PencairanManager instance
        item_id: ID item di transaksi_item
        updates: Dictionary fields to update
        user: User yang melakukan update
    
    Returns:
        True jika berhasil
    """
    if not db:
        return False
    
    return db.update_transaksi_item(item_id, updates, user)


def update_item_status_in_transaksi(db, item_id: int, new_status: str, user: str = None, keterangan: str = None) -> bool:
    """
    Update status item di transaksi_item.
    
    Status progression: diminta → disetujui → dipesan → diterima → diserahterimakan
    
    Args:
        db: PencairanManager instance
        item_id: ID item
        new_status: Status baru
        user: User yang melakukan update
        keterangan: Keterangan tambahan
    
    Returns:
        True jika berhasil
    """
    if not db:
        return False
    
    return db.update_item_status(item_id, new_status, user, keterangan)


def bulk_update_items_status(db, transaksi_id: int, new_status: str, user: str = None, keterangan: str = None) -> int:
    """
    Update status semua items dalam transaksi sekaligus.
    
    Args:
        db: PencairanManager instance
        transaksi_id: ID transaksi
        new_status: Status baru untuk semua items
        user: User yang melakukan update
        keterangan: Keterangan tambahan
    
    Returns:
        Jumlah items yang diupdate
    """
    if not db:
        return 0
    
    items = db.get_transaksi_items(transaksi_id)
    count = 0
    for item in items:
        if db.update_item_status(item['id'], new_status, user, keterangan):
            count += 1
    return count


# ============================================================================
# DATA TRANSFORMATION FUNCTIONS
# ============================================================================

def transform_to_spj_format(db, lembar_id: int) -> Optional[Dict[str, Any]]:
    """
    Transform lembar_permintaan data ke format SPJ (Surat Pertanggung Jawaban).
    
    Returns:
        Dictionary siap untuk SPJ dokumen generation
    """
    data = get_lembar_data_complete(db, lembar_id)
    if not data:
        return None
    
    lembar = data['lembar']
    items = data['items']
    
    return {
        'ref_lembar_id': lembar_id,
        'nomor_sp2d': '',  # Will be filled later
        'tanggal_sp2d': datetime.now().strftime('%Y-%m-%d'),
        'tanggal_pengajuan': lembar.get('hari_tanggal'),
        'unit_kerja': lembar.get('unit_kerja'),
        'sumber_dana': lembar.get('sumber_dana'),
        
        # Penandatangan
        'pengajuan_oleh': lembar.get('nama_pengajuan'),
        'verifikasi_oleh': lembar.get('nama_verifikator'),
        'ppk': lembar.get('nama_ppk'),
        'kpa': lembar.get('nama_kpa'),
        
        # Nilai
        'subtotal': lembar.get('subtotal', 0),
        'ppn': lembar.get('ppn', 0),
        'total': lembar.get('total', 0),
        
        # Detail rincian
        'rincian': transform_items_to_spj_format(items),
    }


def transform_to_kuitansi_format(db, lembar_id: int) -> Optional[Dict[str, Any]]:
    """
    Transform lembar_permintaan data ke format Kuitansi.
    
    Returns:
        Dictionary siap untuk Kuitansi dokumen generation
    """
    data = get_lembar_data_complete(db, lembar_id)
    if not data:
        return None
    
    lembar = data['lembar']
    items = data['items']
    
    return {
        'ref_lembar_id': lembar_id,
        'nomor_kuitansi': '',  # Will be filled by system
        'tanggal_kuitansi': datetime.now().strftime('%Y-%m-%d'),
        'tanggal_pengajuan_lembar': lembar.get('hari_tanggal'),
        'unit_kerja': lembar.get('unit_kerja'),
        'penerima_dana': lembar.get('nama_pengajuan'),
        'sumber_dana': lembar.get('sumber_dana'),
        
        # Verifikasi
        'verifikator': lembar.get('nama_verifikator'),
        'ppk': lembar.get('nama_ppk'),
        'kpa': lembar.get('nama_kpa'),
        
        # Nilai
        'nilai_uang_muka': lembar.get('total', 0),
        'nilai_realisasi': lembar.get('total', 0),
        'selisih': 0,  # Calculated later
        
        # Detail rincian
        'rincian': transform_items_to_kuitansi_format(items),
    }


def transform_to_realisasi_format(db, lembar_id: int) -> Optional[Dict[str, Any]]:
    """
    Transform lembar_permintaan data ke format Realisasi.
    
    Returns:
        Dictionary siap untuk Realisasi dokumen generation
    """
    data = get_lembar_data_complete(db, lembar_id)
    if not data:
        return None
    
    lembar = data['lembar']
    items = data['items']
    
    return {
        'ref_lembar_id': lembar_id,
        'tanggal_realisasi': datetime.now().strftime('%Y-%m-%d'),
        'tanggal_rencana': lembar.get('hari_tanggal'),
        'unit_kerja': lembar.get('unit_kerja'),
        'nama_kegiatan': lembar.get('unit_kerja'),  # Use unit_kerja as activity name
        'sumber_dana': lembar.get('sumber_dana'),
        
        # Penandatangan
        'pelaksana': lembar.get('nama_pengajuan'),
        'verifikator': lembar.get('nama_verifikator'),
        'ppk': lembar.get('nama_ppk'),
        'kpa': lembar.get('nama_kpa'),
        
        # Nilai realisasi
        'anggaran': lembar.get('total', 0),
        'realisasi': 0,  # Will be filled by actual spending
        'sisa': 0,  # Calculated: anggaran - realisasi
        
        # Detail rincian realisasi
        'rincian': transform_items_to_realisasi_format(items),
    }


def transform_items_to_spj_format(items: List[Dict]) -> List[Dict[str, Any]]:
    """Transform items ke SPJ format."""
    result = []
    for item in items:
        result.append({
            'no': item.get('item_no'),
            'uraian': item.get('nama_barang'),
            'spesifikasi': item.get('spesifikasi', ''),
            'volume': item.get('volume'),
            'satuan': item.get('satuan'),
            'harga': item.get('harga_satuan'),
            'jumlah': item.get('total_item'),
            'keterangan': item.get('keterangan', ''),
        })
    return result


def transform_items_to_kuitansi_format(items: List[Dict]) -> List[Dict[str, Any]]:
    """Transform items ke Kuitansi format."""
    result = []
    for item in items:
        result.append({
            'no': item.get('item_no'),
            'uraian': item.get('nama_barang'),
            'volume': item.get('volume'),
            'satuan': item.get('satuan'),
            'harga_satuan': item.get('harga_satuan'),
            'jumlah': item.get('total_item'),
            'keterangan': item.get('keterangan', ''),
        })
    return result


def transform_items_to_realisasi_format(items: List[Dict]) -> List[Dict[str, Any]]:
    """Transform items ke Realisasi format."""
    result = []
    for item in items:
        result.append({
            'no': item.get('item_no'),
            'uraian': item.get('nama_barang'),
            'spesifikasi': item.get('spesifikasi', ''),
            'volume_rencana': item.get('volume'),
            'satuan': item.get('satuan'),
            'volume_realisasi': 0,  # Will be filled by actual realization
            'harga': item.get('harga_satuan'),
            'jumlah_rencana': item.get('total_item'),
            'jumlah_realisasi': 0,  # Will be filled by actual realization
            'keterangan': item.get('keterangan', ''),
        })
    return result


# ============================================================================
# STATUS & WORKFLOW FUNCTIONS
# ============================================================================

def update_lembar_status(db, lembar_id: int, status: str) -> bool:
    """
    Update status lembar_permintaan.
    
    Status values: 'draft', 'final', 'signed', 'uploaded', 'used', 'archived'
    
    Args:
        db: PencairanManager instance
        lembar_id: ID lembar_permintaan
        status: Status baru
    
    Returns:
        True jika berhasil
    """
    if not db:
        return False
    
    return db.update_lembar_permintaan(lembar_id, {'status': status})


def mark_as_used_in_next_phase(db, lembar_id: int, fase_target: int = 2) -> bool:
    """
    Mark lembar_permintaan sebagai sudah digunakan di fase berikutnya.
    
    Args:
        db: PencairanManager instance
        lembar_id: ID lembar_permintaan
        fase_target: Fase berikutnya yang menggunakan data ini
    
    Returns:
        True jika berhasil
    """
    return update_lembar_status(db, lembar_id, 'used')


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_lembar_for_next_phase(db, lembar_id: int) -> Tuple[bool, Optional[str]]:
    """
    Validate lembar_permintaan sebelum digunakan di fase berikutnya.
    
    Checks:
    - Lembar exists
    - Has items (minimal 1 item)
    - Total > 0
    - All required signatures present
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    lembar = db.get_lembar_permintaan(lembar_id) if db else None
    if not lembar:
        return False, f"Lembar Permintaan {lembar_id} tidak ditemukan"
    
    items = db.get_lembar_permintaan_items(lembar_id) if db else []
    if not items:
        return False, "Lembar Permintaan harus memiliki minimal 1 item"
    
    total = lembar.get('total', 0)
    if not total or total <= 0:
        return False, "Total lembar permintaan harus lebih besar dari 0"
    
    # Check penandatangan
    required_signatures = ['nama_pengajuan', 'nama_ppk', 'nama_kpa']
    for sig_field in required_signatures:
        sig_value = lembar.get(sig_field, '')
        if not sig_value or not sig_value.strip():
            return False, f"Penandatangan '{sig_field}' harus diisi"
    
    return True, None


# ============================================================================
# SUMMARY & REPORTING FUNCTIONS
# ============================================================================

def get_lembar_summary(db, lembar_id: int) -> Optional[Dict[str, Any]]:
    """
    Get ringkasan lengkap lembar_permintaan.
    Cocok untuk display di UI atau laporan.
    
    Returns:
        Dictionary dengan semua informasi penting lembar
    """
    data = get_lembar_data_complete(db, lembar_id)
    if not data:
        return None
    
    lembar = data['lembar']
    items = data['items']
    
    return {
        'id': lembar_id,
        'kode_transaksi': lembar.get('kode_transaksi'),
        'tanggal': lembar.get('hari_tanggal'),
        'unit_kerja': lembar.get('unit_kerja'),
        'sumber_dana': lembar.get('sumber_dana'),
        'status': lembar.get('status'),
        
        'jumlah_item': len(items),
        'subtotal': lembar.get('subtotal', 0),
        'ppn': lembar.get('ppn', 0),
        'total': lembar.get('total', 0),
        
        'pengajuan_oleh': lembar.get('nama_pengajuan'),
        'verifikasi_oleh': lembar.get('nama_verifikator'),
        'ppk': lembar.get('nama_ppk'),
        'kpa': lembar.get('nama_kpa'),
        
        'file': lembar.get('file_path'),
        'created_at': lembar.get('created_at'),
        'created_by': lembar.get('created_by'),
        
        'items': items,
    }
