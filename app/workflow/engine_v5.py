"""
PPK DOCUMENT FACTORY v5.0 - Workflow Engine
============================================
Filosofi: "Membantu, Bukan Menghalangi"

Sistem ini menggunakan:
- Soft Validation (warning, bukan block)
- Progressive Disclosure (field muncul sesuai fase)
- Auto-Suggest (tanggal, nilai)
- Auto-Fill (data inheritance)
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple, Optional, Any
from enum import IntEnum
from dataclasses import dataclass


# =============================================================================
# STATUS CODES
# =============================================================================

class PaketStatus(IntEnum):
    """Status paket pengadaan"""
    DRAFT = 0
    PERSIAPAN = 10
    DIKIRIM_KE_PP = 20
    PEMILIHAN = 30
    PENYEDIA_OK = 40
    KONTRAK_AKTIF = 50
    PELAKSANAAN = 60
    SERAH_TERIMA = 70
    SELESAI = 99
    DIBATALKAN = -1


STATUS_NAMES = {
    PaketStatus.DRAFT: "Draft",
    PaketStatus.PERSIAPAN: "Persiapan",
    PaketStatus.DIKIRIM_KE_PP: "Dikirim ke PP",
    PaketStatus.PEMILIHAN: "Pemilihan Penyedia",
    PaketStatus.PENYEDIA_OK: "Penyedia Ditetapkan",
    PaketStatus.KONTRAK_AKTIF: "Kontrak Aktif",
    PaketStatus.PELAKSANAAN: "Pelaksanaan",
    PaketStatus.SERAH_TERIMA: "Serah Terima",
    PaketStatus.SELESAI: "Selesai",
    PaketStatus.DIBATALKAN: "Dibatalkan",
}


# =============================================================================
# VALIDATION TYPES
# =============================================================================

class ValidationType:
    """Jenis validasi - TIDAK ADA HARD BLOCK kecuali fatal"""
    INFO = "INFO"           # 💡 Saran
    WARNING = "WARNING"     # ⚠️ Peringatan
    INCOMPLETE = "INCOMPLETE"  # 🔲 Belum lengkap
    COMPLETE = "COMPLETE"   # ✅ Lengkap
    BLOCKED = "BLOCKED"     # 🚫 Fatal error only (sangat jarang!)


@dataclass
class ValidationResult:
    """Hasil validasi"""
    type: str
    field: str
    message: str
    icon: str
    
    def __init__(self, vtype: str, field: str, message: str):
        self.type = vtype
        self.field = field
        self.message = message
        self.icon = {
            ValidationType.INFO: "💡",
            ValidationType.WARNING: "⚠️",
            ValidationType.INCOMPLETE: "🔲",
            ValidationType.COMPLETE: "✅",
            ValidationType.BLOCKED: "🚫",
        }.get(vtype, "")


# =============================================================================
# VISIBILITY RULES - Kapan Field MUNCUL (bukan kapan dikunci)
# =============================================================================

FIELD_VISIBILITY = {
    # Field yang selalu terlihat
    'nama': {'min_status': PaketStatus.DRAFT},
    'jenis_pengadaan': {'min_status': PaketStatus.DRAFT},
    'metode_pengadaan': {'min_status': PaketStatus.DRAFT},
    'nilai_pagu': {'min_status': PaketStatus.DRAFT},
    'jangka_waktu': {'min_status': PaketStatus.DRAFT},
    
    # Field nilai - muncul bertahap
    'nilai_hps': {'min_status': PaketStatus.DRAFT},  # Selalu visible, tapi soft-warn jika survey belum lengkap
    'nilai_negosiasi': {'min_status': PaketStatus.PEMILIHAN},
    'nilai_kontrak': {'min_status': PaketStatus.PENYEDIA_OK},
    
    # Field penyedia
    'penyedia_id': {'min_status': PaketStatus.PENYEDIA_OK},
    'penyedia_nama': {'min_status': PaketStatus.PENYEDIA_OK},
    
    # Modul/Section
    'modul_survey': {'min_status': PaketStatus.DRAFT},
    'modul_hps': {'min_status': PaketStatus.DRAFT},
    'modul_pemilihan': {'min_status': PaketStatus.DIKIRIM_KE_PP},
    'modul_kontrak': {'min_status': PaketStatus.PENYEDIA_OK},
    'modul_adendum': {'min_status': PaketStatus.KONTRAK_AKTIF},
    'modul_serah_terima': {'min_status': PaketStatus.PELAKSANAAN},
    'modul_pembayaran': {'min_status': PaketStatus.SERAH_TERIMA},
}


DOCUMENT_VISIBILITY = {
    # Fase Persiapan - selalu tersedia
    'SPESIFIKASI_TEKNIS': {'min_status': PaketStatus.DRAFT},
    'KAK': {'min_status': PaketStatus.DRAFT},
    'SURVEY_HARGA': {'min_status': PaketStatus.DRAFT},
    'BA_SURVEY': {'min_status': PaketStatus.DRAFT},
    'RAB': {'min_status': PaketStatus.DRAFT},
    'HPS': {'min_status': PaketStatus.DRAFT},
    'RANCANGAN_KONTRAK': {'min_status': PaketStatus.DRAFT},
    'SSUK': {'min_status': PaketStatus.DRAFT},
    'SSKK': {'min_status': PaketStatus.DRAFT},
    'NOTA_DINAS_PP': {'min_status': PaketStatus.DRAFT},
    
    # Fase Pemilihan
    'UNDANGAN': {'min_status': PaketStatus.DIKIRIM_KE_PP},
    'BA_EVALUASI_ADMIN': {'min_status': PaketStatus.DIKIRIM_KE_PP},
    'BA_EVALUASI_TEKNIS': {'min_status': PaketStatus.DIKIRIM_KE_PP},
    'BA_EVALUASI_HARGA': {'min_status': PaketStatus.DIKIRIM_KE_PP},
    'BA_NEGOSIASI': {'min_status': PaketStatus.DIKIRIM_KE_PP},
    'BAHP_PEMILIHAN': {'min_status': PaketStatus.DIKIRIM_KE_PP},
    'PENETAPAN_PENYEDIA': {'min_status': PaketStatus.PEMILIHAN},
    
    # Fase Kontrak
    'SPK': {'min_status': PaketStatus.PENYEDIA_OK},
    'SURAT_PERJANJIAN': {'min_status': PaketStatus.PENYEDIA_OK},
    'SPMK': {'min_status': PaketStatus.PENYEDIA_OK},
    'JAMINAN_PELAKSANAAN': {'min_status': PaketStatus.PENYEDIA_OK},
    
    # Fase Pelaksanaan
    'ADENDUM_KONTRAK': {'min_status': PaketStatus.KONTRAK_AKTIF},
    'ADENDUM_SPMK': {'min_status': PaketStatus.KONTRAK_AKTIF},
    'BA_PERUBAHAN': {'min_status': PaketStatus.KONTRAK_AKTIF},
    
    # Fase Serah Terima
    'BAHP_HASIL': {'min_status': PaketStatus.PELAKSANAAN},
    'BA_PERBAIKAN': {'min_status': PaketStatus.PELAKSANAAN},
    'BAST': {'min_status': PaketStatus.PELAKSANAAN},
    
    # Fase Pembayaran
    'KUITANSI': {'min_status': PaketStatus.SERAH_TERIMA},
    'FAKTUR_PAJAK': {'min_status': PaketStatus.SERAH_TERIMA},
    'SSP': {'min_status': PaketStatus.SERAH_TERIMA},
    'SPP': {'min_status': PaketStatus.SERAH_TERIMA},
    'SPM': {'min_status': PaketStatus.SERAH_TERIMA},
    'SP2D': {'min_status': PaketStatus.SERAH_TERIMA},
}


# =============================================================================
# SOFT VALIDATION RULES
# =============================================================================

def validate_paket(paket: Dict, items: List[Dict] = None) -> List[ValidationResult]:
    """
    Validasi paket dengan pendekatan RAMAH PPK
    Returns list of ValidationResult (mostly INFO/WARNING, rarely BLOCKED)
    """
    results = []
    items = items or []
    
    # Count surveys
    survey_complete_count = 0
    survey_incomplete_count = 0
    for item in items:
        count = sum(1 for i in range(1, 4) if item.get(f'harga_survey{i}', 0) and item.get(f'harga_survey{i}', 0) > 0)
        if count >= 3:
            survey_complete_count += 1
        elif count > 0:
            survey_incomplete_count += 1
    
    total_items = len(items)
    
    # =================================================================
    # SURVEY VALIDATION (Soft)
    # =================================================================
    if total_items > 0 and survey_complete_count < total_items:
        if survey_incomplete_count > 0:
            results.append(ValidationResult(
                ValidationType.INCOMPLETE,
                'survey_harga',
                f"Survey Harga: {survey_complete_count}/{total_items} item lengkap (min 3 sumber)"
            ))
        else:
            results.append(ValidationResult(
                ValidationType.INFO,
                'survey_harga',
                "💡 Mulai input survey harga untuk setiap item (disarankan min 3 sumber)"
            ))
    elif total_items > 0:
        results.append(ValidationResult(
            ValidationType.COMPLETE,
            'survey_harga',
            f"Survey Harga: Lengkap ({survey_complete_count} item)"
        ))
    
    # =================================================================
    # HPS VALIDATION (Soft)
    # =================================================================
    nilai_hps = paket.get('nilai_hps', 0) or 0
    if nilai_hps > 0 and survey_complete_count < total_items:
        results.append(ValidationResult(
            ValidationType.INFO,
            'nilai_hps',
            "💡 Sebaiknya survey harga dilengkapi terlebih dahulu untuk konsistensi HPS"
        ))
    
    # =================================================================
    # TIMELINE VALIDATION (Soft)
    # =================================================================
    tgl_survey = paket.get('tanggal_survey_selesai')
    tgl_hps = paket.get('tanggal_hps')
    tgl_nota = paket.get('tanggal_nota_dinas')
    tgl_penetapan = paket.get('tanggal_penetapan_penyedia')
    tgl_kontrak = paket.get('tanggal_kontrak')
    tgl_spmk = paket.get('tanggal_spmk')
    tgl_mulai = paket.get('tanggal_mulai_kerja')
    tgl_selesai = paket.get('tanggal_selesai_kerja')
    tgl_bahp = paket.get('tanggal_bahp')
    tgl_bast = paket.get('tanggal_bast')
    
    # Timeline checks (WARNING, not BLOCK)
    if tgl_hps and tgl_survey and tgl_hps < tgl_survey:
        results.append(ValidationResult(
            ValidationType.WARNING,
            'tanggal_hps',
            "⚠️ Tanggal HPS lebih awal dari tanggal survey selesai"
        ))
    
    if tgl_nota and tgl_hps and tgl_nota < tgl_hps:
        results.append(ValidationResult(
            ValidationType.WARNING,
            'tanggal_nota_dinas',
            "⚠️ Tanggal Nota Dinas lebih awal dari tanggal HPS"
        ))
    
    if tgl_kontrak and tgl_penetapan and tgl_kontrak < tgl_penetapan:
        results.append(ValidationResult(
            ValidationType.WARNING,
            'tanggal_kontrak',
            "⚠️ Tanggal Kontrak lebih awal dari tanggal Penetapan Penyedia"
        ))
    
    if tgl_spmk and tgl_kontrak and tgl_spmk < tgl_kontrak:
        results.append(ValidationResult(
            ValidationType.WARNING,
            'tanggal_spmk',
            "⚠️ Tanggal SPMK lebih awal dari tanggal Kontrak"
        ))
    
    if tgl_bast and tgl_bahp and tgl_bast < tgl_bahp:
        results.append(ValidationResult(
            ValidationType.WARNING,
            'tanggal_bast',
            "⚠️ Tanggal BAST lebih awal dari tanggal BAHP"
        ))
    
    # =================================================================
    # NILAI VALIDATION (Soft)
    # =================================================================
    nilai_pagu = paket.get('nilai_pagu', 0) or 0
    nilai_negosiasi = paket.get('nilai_negosiasi', 0) or 0
    nilai_kontrak = paket.get('nilai_kontrak', 0) or 0
    
    if nilai_negosiasi > 0 and nilai_hps > 0 and nilai_negosiasi > nilai_hps:
        results.append(ValidationResult(
            ValidationType.WARNING,
            'nilai_negosiasi',
            "⚠️ Nilai negosiasi melebihi HPS"
        ))
    
    if nilai_kontrak > 0 and nilai_pagu > 0 and nilai_kontrak > nilai_pagu:
        results.append(ValidationResult(
            ValidationType.WARNING,
            'nilai_kontrak',
            "⚠️ Nilai kontrak melebihi pagu anggaran"
        ))
    
    # =================================================================
    # HARD BLOCK (sangat terbatas - hanya logika fatal)
    # =================================================================
    if tgl_selesai and tgl_mulai and tgl_selesai < tgl_mulai:
        results.append(ValidationResult(
            ValidationType.BLOCKED,
            'tanggal_selesai_kerja',
            "🚫 Tanggal selesai tidak boleh sebelum tanggal mulai"
        ))
    
    # Check for negative values
    for field in ['nilai_pagu', 'nilai_hps', 'nilai_kontrak']:
        val = paket.get(field, 0) or 0
        if val < 0:
            results.append(ValidationResult(
                ValidationType.BLOCKED,
                field,
                f"🚫 {field.replace('_', ' ').title()} tidak boleh negatif"
            ))
    
    return results


def has_blocking_errors(results: List[ValidationResult]) -> bool:
    """Check if there are any BLOCKED validation results"""
    return any(r.type == ValidationType.BLOCKED for r in results)


# =============================================================================
# VISIBILITY CHECKER
# =============================================================================

def is_field_visible(field: str, status: int) -> bool:
    """Check if field should be visible based on status"""
    rule = FIELD_VISIBILITY.get(field)
    if not rule:
        return True  # Default visible
    return status >= rule.get('min_status', 0)


def is_document_visible(doc_type: str, status: int) -> bool:
    """Check if document type should be available based on status"""
    rule = DOCUMENT_VISIBILITY.get(doc_type)
    if not rule:
        return True  # Default visible
    return status >= rule.get('min_status', 0)


def get_visible_fields(status: int) -> List[str]:
    """Get list of visible fields for a status"""
    return [f for f, r in FIELD_VISIBILITY.items() if status >= r.get('min_status', 0)]


def get_visible_documents(status: int) -> List[str]:
    """Get list of available documents for a status"""
    return [d for d, r in DOCUMENT_VISIBILITY.items() if status >= r.get('min_status', 0)]


# =============================================================================
# DATE AUTO-SUGGEST
# =============================================================================

DATE_SUGGEST_RULES = {
    'tanggal_survey_selesai': {'from': 'tanggal_spesifikasi', 'offset': 3},
    'tanggal_hps': {'from': 'tanggal_survey_selesai', 'offset': 2},
    'tanggal_nota_dinas': {'from': 'tanggal_hps', 'offset': 1},
    'tanggal_undangan': {'from': 'tanggal_nota_dinas', 'offset': 2},
    'tanggal_penetapan_penyedia': {'from': 'tanggal_undangan', 'offset': 7},
    'tanggal_kontrak': {'from': 'tanggal_penetapan_penyedia', 'offset': 1},
    'tanggal_spmk': {'from': 'tanggal_kontrak', 'offset': 1},
    'tanggal_mulai_kerja': {'from': 'tanggal_spmk', 'offset': 1},
    'tanggal_bahp': {'from': 'tanggal_selesai_kerja', 'offset': 3},
    'tanggal_bast': {'from': 'tanggal_bahp', 'offset': 2},
    'tanggal_spp': {'from': 'tanggal_bast', 'offset': 2},
}


def suggest_date(field: str, paket: Dict) -> Optional[date]:
    """
    Suggest a date based on previous dates
    Returns None if no suggestion available
    """
    rule = DATE_SUGGEST_RULES.get(field)
    if not rule:
        return None
    
    from_field = rule['from']
    offset = rule['offset']
    
    # Handle dynamic offset (jangka_waktu)
    if from_field == 'tanggal_mulai_kerja' and field == 'tanggal_selesai_kerja':
        jangka = paket.get('jangka_waktu', 30) or 30
        offset = jangka
    
    from_date = paket.get(from_field)
    if not from_date:
        return None
    
    # Convert string to date if needed
    if isinstance(from_date, str):
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        except:
            return None
    
    return from_date + timedelta(days=offset)


def get_date_suggestion_message(field: str, suggested: date, paket: Dict) -> str:
    """Get friendly message for date suggestion"""
    rule = DATE_SUGGEST_RULES.get(field)
    if not rule:
        return ""
    
    from_field = rule['from']
    from_name = from_field.replace('tanggal_', '').replace('_', ' ').title()
    
    return f"💡 Disarankan: {suggested.strftime('%d/%m/%Y')} ({rule['offset']} hari setelah {from_name})"


# =============================================================================
# DOCUMENT COMPLETENESS CHECKER
# =============================================================================

def get_document_checklist(paket: Dict, existing_docs: List[str], status: int) -> List[Dict]:
    """
    Get document checklist with completion status
    Returns list of {doc_type, name, status, icon, visible}
    """
    DOC_NAMES = {
        'SPESIFIKASI_TEKNIS': 'Spesifikasi Teknis',
        'KAK': 'KAK',
        'SURVEY_HARGA': 'Survey Harga',
        'BA_SURVEY': 'BA Survey Harga',
        'RAB': 'RAB',
        'HPS': 'HPS',
        'NOTA_DINAS_PP': 'Nota Dinas ke PP',
        'SPK': 'SPK / Kontrak',
        'SPMK': 'SPMK',
        'BAHP_HASIL': 'BAHP Hasil Pekerjaan',
        'BAST': 'BAST',
        'KUITANSI': 'Kuitansi',
        'SSP': 'SSP',
        'SPP': 'SPP',
    }
    
    checklist = []
    for doc_type, rule in DOCUMENT_VISIBILITY.items():
        visible = status >= rule.get('min_status', 0)
        exists = doc_type in existing_docs
        
        checklist.append({
            'doc_type': doc_type,
            'name': DOC_NAMES.get(doc_type, doc_type),
            'status': 'complete' if exists else 'incomplete',
            'icon': '✅' if exists else ('🔲' if visible else '🔒'),
            'visible': visible,
        })
    
    return checklist


# =============================================================================
# STATUS TRANSITION
# =============================================================================

def can_advance_status(paket: Dict, items: List[Dict], current_status: int) -> Tuple[bool, str]:
    """
    Check if paket can advance to next status
    Uses SOFT logic - mostly allows with warnings
    """
    # From DRAFT to PERSIAPAN - always allowed
    if current_status == PaketStatus.DRAFT:
        return True, "Mulai persiapan dokumen"
    
    # From PERSIAPAN to DIKIRIM - suggest completing docs
    if current_status == PaketStatus.PERSIAPAN:
        # Soft check - just return suggestion
        return True, "💡 Pastikan dokumen persiapan sudah lengkap sebelum mengirim ke PP"
    
    # From DIKIRIM to PEMILIHAN - PP takes over
    if current_status == PaketStatus.DIKIRIM_KE_PP:
        return True, "Proses pemilihan oleh Pejabat Pengadaan"
    
    # From PEMILIHAN to PENYEDIA_OK
    if current_status == PaketStatus.PEMILIHAN:
        if not paket.get('penyedia_id'):
            return True, "💡 Lengkapi data penyedia sebelum melanjutkan"
        return True, "Penyedia telah ditetapkan"
    
    # From PENYEDIA_OK to KONTRAK_AKTIF
    if current_status == PaketStatus.PENYEDIA_OK:
        return True, "💡 Pastikan SPK/Kontrak sudah ditandatangani"
    
    # From KONTRAK_AKTIF to PELAKSANAAN
    if current_status == PaketStatus.KONTRAK_AKTIF:
        return True, "💡 SPMK harus sudah terbit"
    
    # From PELAKSANAAN to SERAH_TERIMA
    if current_status == PaketStatus.PELAKSANAAN:
        return True, "💡 Pastikan pekerjaan sudah selesai 100%"
    
    # From SERAH_TERIMA to SELESAI
    if current_status == PaketStatus.SERAH_TERIMA:
        return True, "💡 Pastikan pembayaran sudah selesai"
    
    return True, ""


def get_next_status(current: int) -> int:
    """Get next status in sequence"""
    sequence = [
        PaketStatus.DRAFT,
        PaketStatus.PERSIAPAN,
        PaketStatus.DIKIRIM_KE_PP,
        PaketStatus.PEMILIHAN,
        PaketStatus.PENYEDIA_OK,
        PaketStatus.KONTRAK_AKTIF,
        PaketStatus.PELAKSANAAN,
        PaketStatus.SERAH_TERIMA,
        PaketStatus.SELESAI,
    ]
    
    try:
        idx = sequence.index(current)
        if idx < len(sequence) - 1:
            return sequence[idx + 1]
    except ValueError:
        pass
    
    return current


def get_status_progress(status: int) -> Dict:
    """Get progress info for status"""
    total = 8  # Total steps (excluding DRAFT and SELESAI as endpoints)
    
    progress_map = {
        PaketStatus.DRAFT: 0,
        PaketStatus.PERSIAPAN: 1,
        PaketStatus.DIKIRIM_KE_PP: 2,
        PaketStatus.PEMILIHAN: 3,
        PaketStatus.PENYEDIA_OK: 4,
        PaketStatus.KONTRAK_AKTIF: 5,
        PaketStatus.PELAKSANAAN: 6,
        PaketStatus.SERAH_TERIMA: 7,
        PaketStatus.SELESAI: 8,
    }
    
    current = progress_map.get(status, 0)
    
    return {
        'current': current,
        'total': total,
        'percentage': int((current / total) * 100),
        'status_name': STATUS_NAMES.get(status, 'Unknown'),
    }


# =============================================================================
# AUTO-FILL RULES
# =============================================================================

def get_auto_fill_values(paket: Dict, penyedia: Dict = None) -> Dict:
    """
    Get auto-filled values for document generation
    """
    auto_values = {}
    
    # Nilai kontrak = nilai negosiasi
    if paket.get('nilai_negosiasi') and not paket.get('nilai_kontrak'):
        auto_values['nilai_kontrak'] = paket['nilai_negosiasi']
    
    # Tanggal selesai = tanggal mulai + jangka waktu
    if paket.get('tanggal_mulai_kerja') and paket.get('jangka_waktu'):
        mulai = paket['tanggal_mulai_kerja']
        if isinstance(mulai, str):
            mulai = datetime.strptime(mulai, '%Y-%m-%d').date()
        auto_values['tanggal_selesai_kerja'] = mulai + timedelta(days=paket['jangka_waktu'])
    
    return auto_values


# =============================================================================
# NEXT ACTION SUGGESTER
# =============================================================================

def get_next_actions(paket: Dict, items: List[Dict], existing_docs: List[str]) -> List[Dict]:
    """
    Get suggested next actions for PPK
    Returns list of {action, description, priority, button_text}
    """
    actions = []
    status = paket.get('status_code', 0)
    
    # Check survey completion
    total_items = len(items)
    survey_complete = sum(1 for item in items 
                         if sum(1 for i in range(1, 4) 
                                if item.get(f'harga_survey{i}', 0) and item.get(f'harga_survey{i}', 0) > 0) >= 3)
    
    if status == PaketStatus.DRAFT:
        actions.append({
            'action': 'start_preparation',
            'description': 'Mulai persiapan dokumen pengadaan',
            'priority': 'high',
            'button_text': '📝 Mulai Persiapan'
        })
    
    elif status == PaketStatus.PERSIAPAN:
        # Suggest based on what's missing
        if total_items == 0:
            actions.append({
                'action': 'add_items',
                'description': 'Tambahkan item barang/jasa',
                'priority': 'high',
                'button_text': '➕ Tambah Item'
            })
        
        if survey_complete < total_items:
            actions.append({
                'action': 'complete_survey',
                'description': f'Lengkapi survey harga ({survey_complete}/{total_items} item)',
                'priority': 'high',
                'button_text': '📊 Lengkapi Survey'
            })
        
        if 'HPS' not in existing_docs and survey_complete > 0:
            actions.append({
                'action': 'create_hps',
                'description': 'Buat dokumen HPS',
                'priority': 'medium',
                'button_text': '📄 Buat HPS'
            })
        
        if 'NOTA_DINAS_PP' not in existing_docs:
            actions.append({
                'action': 'create_nota_dinas',
                'description': 'Buat Nota Dinas ke Pejabat Pengadaan',
                'priority': 'medium',
                'button_text': '📋 Buat Nota Dinas'
            })
        
        actions.append({
            'action': 'send_to_pp',
            'description': 'Kirim ke Pejabat Pengadaan untuk pemilihan',
            'priority': 'low',
            'button_text': '📤 Kirim ke PP'
        })
    
    elif status == PaketStatus.PENYEDIA_OK:
        if 'SPK' not in existing_docs:
            actions.append({
                'action': 'create_spk',
                'description': 'Buat Surat Perintah Kerja',
                'priority': 'high',
                'button_text': '📝 Buat SPK'
            })
        
        if 'SPMK' not in existing_docs:
            actions.append({
                'action': 'create_spmk',
                'description': 'Buat Surat Perintah Mulai Kerja',
                'priority': 'high',
                'button_text': '📝 Buat SPMK'
            })
    
    elif status == PaketStatus.PELAKSANAAN:
        if 'BAHP_HASIL' not in existing_docs:
            actions.append({
                'action': 'create_bahp',
                'description': 'Buat BAHP Hasil Pekerjaan',
                'priority': 'high',
                'button_text': '📝 Buat BAHP'
            })
        
        if 'BAST' not in existing_docs:
            actions.append({
                'action': 'create_bast',
                'description': 'Buat Berita Acara Serah Terima',
                'priority': 'high',
                'button_text': '📝 Buat BAST'
            })
    
    elif status == PaketStatus.SERAH_TERIMA:
        actions.append({
            'action': 'create_payment_docs',
            'description': 'Buat dokumen pembayaran (Kuitansi, SSP, SPP)',
            'priority': 'high',
            'button_text': '💰 Buat Dok. Pembayaran'
        })
    
    return actions
