"""
PPK DOCUMENT FACTORY v3.0 - Configuration & Placeholder Dictionary
===================================================================
Template-Driven Procurement Workflow System
"""

import os
from datetime import datetime
from typing import Dict, List

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

# APP_DIR points to 'app/' folder
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ROOT_DIR points to main application folder (parent of 'app/')
ROOT_DIR = os.path.dirname(APP_DIR)

# Data and output in root folder
DATA_DIR = os.path.join(ROOT_DIR, "data")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")

# Templates in root folder (not in app/)
TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")
WORD_TEMPLATES_DIR = os.path.join(TEMPLATES_DIR, "word")
EXCEL_TEMPLATES_DIR = os.path.join(TEMPLATES_DIR, "excel")
BACKUP_TEMPLATES_DIR = os.path.join(TEMPLATES_DIR, "backup")

# Assets in root folder
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
SIGNATURES_DIR = os.path.join(ASSETS_DIR, "signatures")

# Ensure directories exist
for d in [DATA_DIR, OUTPUT_DIR, WORD_TEMPLATES_DIR, EXCEL_TEMPLATES_DIR, 
          BACKUP_TEMPLATES_DIR, ASSETS_DIR, SIGNATURES_DIR]:
    os.makedirs(d, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, "ppk_workflow.db")

# ============================================================================
# TAHUN ANGGARAN
# ============================================================================

TAHUN_ANGGARAN = datetime.now().year

# ============================================================================
# METODE PERHITUNGAN HPS
# ============================================================================

METODE_HPS = {
    'RATA': 'Rata-rata',
    'TERTINGGI': 'Harga Tertinggi',
    'TERENDAH': 'Harga Terendah'
}

def hitung_harga_hps(survey1: float, survey2: float, survey3: float, metode: str = 'RATA') -> float:
    """
    Hitung harga HPS berdasarkan metode yang dipilih
    
    Args:
        survey1: Harga survey toko 1
        survey2: Harga survey toko 2
        survey3: Harga survey toko 3
        metode: 'RATA', 'TERTINGGI', atau 'TERENDAH'
    
    Returns:
        Harga HPS hasil perhitungan
    """
    # Filter valid prices (> 0)
    prices = [p for p in [survey1, survey2, survey3] if p and p > 0]
    
    if not prices:
        return 0
    
    if metode == 'TERTINGGI':
        return max(prices)
    elif metode == 'TERENDAH':
        return min(prices)
    else:  # RATA (default)
        return sum(prices) / len(prices)

# ============================================================================
# SATKER DEFAULT
# ============================================================================

SATKER_DEFAULT = {
    'kode': '634146',
    'nama': 'POLITEKNIK KELAUTAN DAN PERIKANAN SORONG',
    'nama_pendek': 'Politeknik KP Sorong',
    'alamat': 'Jl. Kapitan Pattimura, Klademak II, Distrik Sorong Manoi',
    'kota': 'Sorong',
    'kode_pos': '98417',
    'provinsi': 'Papua Barat Daya',
    'telepon': '(0951) 321456',
    'fax': '(0951) 321456',
    'email': 'poltek.sorong@kkp.go.id',
    'website': 'www.polsorong.ac.id',
    'kementerian': 'KEMENTERIAN KELAUTAN DAN PERIKANAN',
    'eselon1': 'BADAN PENYULUHAN DAN PENGEMBANGAN SDM KP',
}

# ============================================================================
# PROCUREMENT WORKFLOW STAGES
# ============================================================================

WORKFLOW_STAGES = [
    {
        'id': 1,
        'code': 'SPESIFIKASI',
        'name': 'Spesifikasi Teknis',
        'description': 'Dokumen spesifikasi teknis barang/jasa',
        'template_type': 'word',
        'template_file': 'spesifikasi_teknis.docx',
        'required': True,
        'outputs': ['SPESIFIKASI'],
    },
    {
        'id': 2,
        'code': 'SURVEY',
        'name': 'Survey Harga',
        'description': 'Survey harga pasar dari minimal 3 sumber',
        'template_type': 'excel',
        'template_file': 'survey_harga.xlsx',
        'required': True,
        'outputs': ['SURVEY_HARGA', 'BA_SURVEY_HARGA'],
    },
    {
        'id': 3,
        'code': 'HPS',
        'name': 'Penetapan HPS',
        'description': 'Harga Perkiraan Sendiri',
        'template_type': 'excel',
        'template_file': 'hps.xlsx',
        'required': True,
        'outputs': ['HPS'],
    },
    {
        'id': 4,
        'code': 'KAK',
        'name': 'Kerangka Acuan Kerja',
        'description': 'KAK / Terms of Reference',
        'template_type': 'word',
        'template_file': 'kak.docx',
        'required': True,
        'outputs': ['KAK'],
    },
    {
        'id': 5,
        'code': 'NOTA_DINAS_PP',
        'name': 'Nota Dinas ke Pejabat Pengadaan',
        'description': 'Permintaan pelaksanaan pengadaan (akhir persiapan)',
        'template_type': 'word',
        'template_file': 'nota_dinas_pp.docx',
        'required': True,
        'outputs': ['NOTA_DINAS_PP', 'SURAT_PERMINTAAN'],
    },
    {
        'id': 6,
        'code': 'SPK',
        'name': 'Surat Perintah Kerja',
        'description': 'Kontrak / Surat Perintah Kerja',
        'template_type': 'word',
        'template_file': 'spk.docx',
        'required': True,
        'outputs': ['SPK'],
    },
    {
        'id': 7,
        'code': 'SPMK',
        'name': 'Surat Perintah Mulai Kerja',
        'description': 'Perintah untuk memulai pekerjaan',
        'template_type': 'word',
        'template_file': 'spmk.docx',
        'required': True,
        'outputs': ['SPMK'],
    },
    {
        'id': 8,
        'code': 'BAHP',
        'name': 'Berita Acara Hasil Pemeriksaan',
        'description': 'Hasil pemeriksaan pekerjaan oleh PPHP',
        'template_type': 'word',
        'template_file': 'bahp.docx',
        'required': True,
        'outputs': ['BAHP'],
    },
    {
        'id': 9,
        'code': 'BAST',
        'name': 'Berita Acara Serah Terima',
        'description': 'Serah terima hasil pekerjaan',
        'template_type': 'word',
        'template_file': 'bast.docx',
        'required': True,
        'outputs': ['BAST'],
    },
    {
        'id': 10,
        'code': 'SPP',
        'name': 'Surat Permintaan Pembayaran',
        'description': 'SPP-LS, DRPP, Kuitansi',
        'template_type': 'word',
        'template_file': 'spp_ls.docx',
        'required': True,
        'outputs': ['SPP_LS', 'DRPP', 'KUITANSI'],
    },
    {
        'id': 11,
        'code': 'SSP',
        'name': 'Surat Setoran Pajak',
        'description': 'SSP PPN dan PPh',
        'template_type': 'excel',
        'template_file': 'ssp.xlsx',
        'required': True,
        'outputs': ['SSP_PPN', 'SSP_PPH'],
    },
]

# Stage code to ID mapping
STAGE_CODE_MAP = {s['code']: s['id'] for s in WORKFLOW_STAGES}
STAGE_ID_MAP = {s['id']: s for s in WORKFLOW_STAGES}

# ============================================================================
# PLACEHOLDER DICTIONARY
# ============================================================================

PLACEHOLDERS = {
    # -------------------------------------------------------------------------
    # PAKET / PEKERJAAN
    # -------------------------------------------------------------------------
    'paket': {
        'nama_paket': {'label': 'Nama Paket Pekerjaan', 'type': 'text', 'required': True},
        'kode_paket': {'label': 'Kode Paket', 'type': 'text', 'required': False},
        'lokasi_pekerjaan': {'label': 'Lokasi Pekerjaan', 'type': 'text', 'required': True},
        'jenis_pengadaan': {'label': 'Jenis Pengadaan', 'type': 'select', 
                           'options': ['Barang', 'Jasa Lainnya', 'Jasa Konsultansi', 'Pekerjaan Konstruksi'],
                           'required': True},
        'metode_pengadaan': {'label': 'Metode Pengadaan', 'type': 'select',
                            'options': ['Pengadaan Langsung', 'Penunjukan Langsung', 'Tender', 'Seleksi'],
                            'required': True},
        'sumber_dana': {'label': 'Sumber Dana', 'type': 'text', 'required': True},
        'kode_akun': {'label': 'Kode Akun/MAK', 'type': 'text', 'required': True},
        'tahun_anggaran': {'label': 'Tahun Anggaran', 'type': 'number', 'required': True},
    },
    
    # -------------------------------------------------------------------------
    # NILAI / HARGA
    # -------------------------------------------------------------------------
    'nilai': {
        'nilai_pagu': {'label': 'Nilai Pagu Anggaran', 'type': 'currency', 'required': True},
        'nilai_hps': {'label': 'Nilai HPS', 'type': 'currency', 'required': True},
        'nilai_hps_terbilang': {'label': 'HPS Terbilang', 'type': 'text', 'auto': True},
        'nilai_kontrak': {'label': 'Nilai Kontrak (sebelum PPN)', 'type': 'currency', 'required': True},
        'nilai_kontrak_terbilang': {'label': 'Kontrak Terbilang', 'type': 'text', 'auto': True},
        'nilai_ppn': {'label': 'PPN 11%', 'type': 'currency', 'auto': True},
        'nilai_pph': {'label': 'PPh', 'type': 'currency', 'auto': True},
        'jenis_pph': {'label': 'Jenis PPh', 'type': 'select', 
                     'options': ['PPh 21', 'PPh 22', 'PPh 23', 'PPh 4(2)'], 'required': True},
        'tarif_pph': {'label': 'Tarif PPh (%)', 'type': 'percent', 'required': True},
        'nilai_bruto': {'label': 'Nilai Bruto (DPP + PPN)', 'type': 'currency', 'auto': True},
        'nilai_bersih': {'label': 'Nilai Bersih', 'type': 'currency', 'auto': True},
        'nilai_bersih_terbilang': {'label': 'Nilai Bersih Terbilang', 'type': 'text', 'auto': True},
    },
    
    # -------------------------------------------------------------------------
    # WAKTU / TANGGAL
    # -------------------------------------------------------------------------
    'waktu': {
        'tanggal_spesifikasi': {'label': 'Tanggal Spesifikasi', 'type': 'date', 'required': False},
        'tanggal_hps': {'label': 'Tanggal HPS', 'type': 'date', 'required': True},
        'tanggal_kak': {'label': 'Tanggal KAK', 'type': 'date', 'required': False},
        'tanggal_spk': {'label': 'Tanggal SPK', 'type': 'date', 'required': True},
        'tanggal_spmk': {'label': 'Tanggal SPMK', 'type': 'date', 'required': True},
        'tanggal_mulai': {'label': 'Tanggal Mulai Kerja', 'type': 'date', 'required': True},
        'tanggal_selesai': {'label': 'Tanggal Selesai', 'type': 'date', 'required': True},
        'tanggal_bahp': {'label': 'Tanggal BAHP', 'type': 'date', 'required': True},
        'tanggal_bast': {'label': 'Tanggal BAST', 'type': 'date', 'required': True},
        'tanggal_spp': {'label': 'Tanggal SPP', 'type': 'date', 'required': True},
        'jangka_waktu': {'label': 'Jangka Waktu (hari)', 'type': 'number', 'required': True},
        'masa_pemeliharaan': {'label': 'Masa Pemeliharaan (hari)', 'type': 'number', 'required': False},
    },
    
    # -------------------------------------------------------------------------
    # NOMOR DOKUMEN
    # -------------------------------------------------------------------------
    'nomor': {
        'nomor_spesifikasi': {'label': 'Nomor Spesifikasi', 'type': 'text', 'auto': True},
        'nomor_hps': {'label': 'Nomor HPS', 'type': 'text', 'auto': True},
        'nomor_kak': {'label': 'Nomor KAK', 'type': 'text', 'auto': True},
        'nomor_spk': {'label': 'Nomor SPK/Kontrak', 'type': 'text', 'auto': True},
        'nomor_spmk': {'label': 'Nomor SPMK', 'type': 'text', 'auto': True},
        'nomor_bahp': {'label': 'Nomor BAHP', 'type': 'text', 'auto': True},
        'nomor_bast': {'label': 'Nomor BAST', 'type': 'text', 'auto': True},
        'nomor_spp': {'label': 'Nomor SPP', 'type': 'text', 'auto': True},
        'nomor_kuitansi': {'label': 'Nomor Kuitansi', 'type': 'text', 'auto': True},
        'nomor_ssp_ppn': {'label': 'Nomor SSP PPN', 'type': 'text', 'auto': True},
        'nomor_ssp_pph': {'label': 'Nomor SSP PPh', 'type': 'text', 'auto': True},
    },
    
    # -------------------------------------------------------------------------
    # SATKER
    # -------------------------------------------------------------------------
    'satker': {
        'satker_kode': {'label': 'Kode Satker', 'type': 'text', 'required': True},
        'satker_nama': {'label': 'Nama Satker', 'type': 'text', 'required': True},
        'satker_alamat': {'label': 'Alamat Satker', 'type': 'text', 'required': True},
        'satker_kota': {'label': 'Kota', 'type': 'text', 'required': True},
        'satker_provinsi': {'label': 'Provinsi', 'type': 'text', 'required': True},
        'satker_telepon': {'label': 'Telepon', 'type': 'text', 'required': False},
        'satker_email': {'label': 'Email', 'type': 'text', 'required': False},
        'kementerian': {'label': 'Kementerian', 'type': 'text', 'required': True},
        'eselon1': {'label': 'Eselon 1', 'type': 'text', 'required': True},
    },
    
    # -------------------------------------------------------------------------
    # PPK
    # -------------------------------------------------------------------------
    'ppk': {
        'ppk_nama': {'label': 'Nama PPK', 'type': 'text', 'required': True},
        'ppk_nip': {'label': 'NIP PPK', 'type': 'text', 'required': True},
        'ppk_pangkat': {'label': 'Pangkat PPK', 'type': 'text', 'required': False},
        'ppk_golongan': {'label': 'Golongan PPK', 'type': 'text', 'required': False},
        'ppk_jabatan': {'label': 'Jabatan PPK', 'type': 'text', 'required': True},
    },
    
    # -------------------------------------------------------------------------
    # PPSPM
    # -------------------------------------------------------------------------
    'ppspm': {
        'ppspm_nama': {'label': 'Nama PPSPM', 'type': 'text', 'required': True},
        'ppspm_nip': {'label': 'NIP PPSPM', 'type': 'text', 'required': True},
        'ppspm_jabatan': {'label': 'Jabatan PPSPM', 'type': 'text', 'required': False},
    },
    
    # -------------------------------------------------------------------------
    # BENDAHARA
    # -------------------------------------------------------------------------
    'bendahara': {
        'bendahara_nama': {'label': 'Nama Bendahara', 'type': 'text', 'required': True},
        'bendahara_nip': {'label': 'NIP Bendahara', 'type': 'text', 'required': True},
    },
    
    # -------------------------------------------------------------------------
    # PENYEDIA
    # -------------------------------------------------------------------------
    'penyedia': {
        'penyedia_nama': {'label': 'Nama Perusahaan', 'type': 'text', 'required': True},
        'penyedia_alamat': {'label': 'Alamat Perusahaan', 'type': 'text', 'required': True},
        'penyedia_kota': {'label': 'Kota', 'type': 'text', 'required': False},
        'penyedia_npwp': {'label': 'NPWP Perusahaan', 'type': 'text', 'required': True},
        'penyedia_rekening': {'label': 'No. Rekening', 'type': 'text', 'required': True},
        'penyedia_bank': {'label': 'Nama Bank', 'type': 'text', 'required': True},
        'penyedia_nama_rekening': {'label': 'Nama Pemilik Rekening', 'type': 'text', 'required': True},
        'penyedia_telepon': {'label': 'Telepon', 'type': 'text', 'required': False},
        'penyedia_email': {'label': 'Email', 'type': 'text', 'required': False},
        'penyedia_is_pkp': {'label': 'PKP (Kena PPN)', 'type': 'boolean', 'required': True},
        'direktur_nama': {'label': 'Nama Direktur', 'type': 'text', 'required': True},
        'direktur_jabatan': {'label': 'Jabatan Direktur', 'type': 'text', 'required': False},
    },
    
    # -------------------------------------------------------------------------
    # PEMERIKSA (PPHP)
    # -------------------------------------------------------------------------
    'pemeriksa': {
        'pemeriksa1_nama': {'label': 'Nama Pemeriksa 1', 'type': 'text', 'required': True},
        'pemeriksa1_nip': {'label': 'NIP Pemeriksa 1', 'type': 'text', 'required': True},
        'pemeriksa1_jabatan': {'label': 'Jabatan Pemeriksa 1', 'type': 'text', 'required': False},
        'pemeriksa2_nama': {'label': 'Nama Pemeriksa 2', 'type': 'text', 'required': False},
        'pemeriksa2_nip': {'label': 'NIP Pemeriksa 2', 'type': 'text', 'required': False},
        'pemeriksa2_jabatan': {'label': 'Jabatan Pemeriksa 2', 'type': 'text', 'required': False},
        'pemeriksa3_nama': {'label': 'Nama Pemeriksa 3', 'type': 'text', 'required': False},
        'pemeriksa3_nip': {'label': 'NIP Pemeriksa 3', 'type': 'text', 'required': False},
        'pemeriksa3_jabatan': {'label': 'Jabatan Pemeriksa 3', 'type': 'text', 'required': False},
    },
    
    # -------------------------------------------------------------------------
    # HASIL PEMERIKSAAN
    # -------------------------------------------------------------------------
    'pemeriksaan': {
        'hasil_pemeriksaan': {'label': 'Hasil Pemeriksaan', 'type': 'textarea', 'required': True},
        'kesimpulan': {'label': 'Kesimpulan', 'type': 'select', 
                      'options': ['Sesuai', 'Tidak Sesuai'], 'required': True},
        'catatan_pemeriksaan': {'label': 'Catatan', 'type': 'textarea', 'required': False},
        'volume_serah_terima': {'label': 'Volume yang Diserahkan', 'type': 'text', 'required': True},
        'kondisi_barang': {'label': 'Kondisi Barang/Pekerjaan', 'type': 'text', 'required': True},
    },
    
    # -------------------------------------------------------------------------
    # SURVEY HARGA (untuk HPS Excel)
    # -------------------------------------------------------------------------
    'survey': {
        'survey1_toko': {'label': 'Nama Toko 1', 'type': 'text', 'required': True},
        'survey1_alamat': {'label': 'Alamat Toko 1', 'type': 'text', 'required': False},
        'survey1_tanggal': {'label': 'Tanggal Survey 1', 'type': 'date', 'required': True},
        'survey2_toko': {'label': 'Nama Toko 2', 'type': 'text', 'required': True},
        'survey2_alamat': {'label': 'Alamat Toko 2', 'type': 'text', 'required': False},
        'survey2_tanggal': {'label': 'Tanggal Survey 2', 'type': 'date', 'required': True},
        'survey3_toko': {'label': 'Nama Toko 3', 'type': 'text', 'required': True},
        'survey3_alamat': {'label': 'Alamat Toko 3', 'type': 'text', 'required': False},
        'survey3_tanggal': {'label': 'Tanggal Survey 3', 'type': 'date', 'required': True},
    },
    
    # -------------------------------------------------------------------------
    # SPESIFIKASI TEKNIS
    # -------------------------------------------------------------------------
    'spesifikasi': {
        'latar_belakang': {'label': 'Latar Belakang', 'type': 'textarea', 'required': True},
        'maksud_tujuan': {'label': 'Maksud dan Tujuan', 'type': 'textarea', 'required': True},
        'ruang_lingkup': {'label': 'Ruang Lingkup', 'type': 'textarea', 'required': True},
        'spesifikasi_teknis': {'label': 'Spesifikasi Teknis', 'type': 'textarea', 'required': True},
        'volume_pekerjaan': {'label': 'Volume Pekerjaan', 'type': 'text', 'required': True},
        'syarat_penyedia': {'label': 'Persyaratan Penyedia', 'type': 'textarea', 'required': False},
    },

    # -------------------------------------------------------------------------
    # PERJALANAN DINAS
    # -------------------------------------------------------------------------
    'perjalanan_dinas': {
        'pelaksana_nama': {'label': 'Nama Pelaksana', 'type': 'text', 'required': True},
        'pelaksana_nip': {'label': 'NIP Pelaksana', 'type': 'text', 'required': True},
        'pelaksana_pangkat': {'label': 'Pangkat/Golongan', 'type': 'text', 'required': True},
        'pelaksana_jabatan': {'label': 'Jabatan Pelaksana', 'type': 'text', 'required': True},
        'maksud_perjalanan': {'label': 'Maksud Perjalanan', 'type': 'textarea', 'required': True},
        'kota_asal': {'label': 'Kota Asal', 'type': 'text', 'required': True},
        'kota_tujuan': {'label': 'Kota Tujuan', 'type': 'text', 'required': True},
        'provinsi_tujuan': {'label': 'Provinsi Tujuan', 'type': 'text', 'required': False},
        'tanggal_berangkat': {'label': 'Tanggal Berangkat', 'type': 'date', 'required': True},
        'tanggal_kembali': {'label': 'Tanggal Kembali', 'type': 'date', 'required': True},
        'lama_perjalanan': {'label': 'Lama Perjalanan (hari)', 'type': 'number', 'required': True},
        'alat_angkut': {'label': 'Alat Angkutan', 'type': 'select',
                       'options': ['Pesawat Udara', 'Kendaraan Dinas', 'Kendaraan Umum', 'Kapal Laut'],
                       'required': True},
        'tingkat_biaya': {'label': 'Tingkat Biaya Perjalanan', 'type': 'select',
                         'options': ['A', 'B', 'C', 'D'], 'required': True},
        'instansi_tujuan': {'label': 'Instansi Tujuan', 'type': 'text', 'required': False},
        # Komponen Biaya
        'biaya_transport': {'label': 'Biaya Transportasi', 'type': 'currency', 'required': True},
        'biaya_uang_harian': {'label': 'Uang Harian', 'type': 'currency', 'required': True},
        'biaya_penginapan': {'label': 'Biaya Penginapan', 'type': 'currency', 'required': False},
        'biaya_representasi': {'label': 'Uang Representasi', 'type': 'currency', 'required': False},
        'biaya_lain_lain': {'label': 'Biaya Lain-lain', 'type': 'currency', 'required': False},
        'total_biaya': {'label': 'Total Biaya', 'type': 'currency', 'auto': True},
        'total_biaya_terbilang': {'label': 'Total Biaya Terbilang', 'type': 'text', 'auto': True},
        # Uang Muka
        'uang_muka': {'label': 'Uang Muka Diterima', 'type': 'currency', 'required': False},
        'uang_muka_terbilang': {'label': 'Uang Muka Terbilang', 'type': 'text', 'auto': True},
        # Rampung
        'kelebihan_bayar': {'label': 'Kelebihan Bayar', 'type': 'currency', 'auto': True},
        'kekurangan_bayar': {'label': 'Kekurangan Bayar', 'type': 'currency', 'auto': True},
        'sisa_terbilang': {'label': 'Sisa Terbilang', 'type': 'text', 'auto': True},
        # Nomor Dokumen
        'nomor_surat_tugas': {'label': 'Nomor Surat Tugas', 'type': 'text', 'auto': True},
        'tanggal_surat_tugas': {'label': 'Tanggal Surat Tugas', 'type': 'date', 'required': True},
        'nomor_sppd': {'label': 'Nomor SPPD', 'type': 'text', 'auto': True},
        # Atasan
        'atasan_nama': {'label': 'Nama Atasan Langsung', 'type': 'text', 'required': True},
        'atasan_nip': {'label': 'NIP Atasan', 'type': 'text', 'required': True},
        'atasan_jabatan': {'label': 'Jabatan Atasan', 'type': 'text', 'required': True},
    },

    # -------------------------------------------------------------------------
    # SWAKELOLA
    # -------------------------------------------------------------------------
    'swakelola': {
        'nama_kegiatan': {'label': 'Nama Kegiatan Swakelola', 'type': 'text', 'required': True},
        'tipe_swakelola': {'label': 'Tipe Swakelola', 'type': 'select',
                          'options': ['Tipe I', 'Tipe II', 'Tipe III', 'Tipe IV'], 'required': True},
        'penyelenggara': {'label': 'Penyelenggara Swakelola', 'type': 'text', 'required': True},
        'latar_belakang_swakelola': {'label': 'Latar Belakang', 'type': 'textarea', 'required': True},
        'tujuan_swakelola': {'label': 'Tujuan Kegiatan', 'type': 'textarea', 'required': True},
        'sasaran_swakelola': {'label': 'Sasaran Kegiatan', 'type': 'textarea', 'required': True},
        'ruang_lingkup_swakelola': {'label': 'Ruang Lingkup', 'type': 'textarea', 'required': True},
        'output_swakelola': {'label': 'Output/Keluaran', 'type': 'textarea', 'required': True},
        'waktu_pelaksanaan': {'label': 'Waktu Pelaksanaan', 'type': 'text', 'required': True},
        'lokasi_kegiatan': {'label': 'Lokasi Kegiatan', 'type': 'text', 'required': True},
        'pagu_swakelola': {'label': 'Pagu Swakelola', 'type': 'currency', 'required': True},
        'pagu_swakelola_terbilang': {'label': 'Pagu Terbilang', 'type': 'text', 'auto': True},
        # Tim Swakelola
        'ketua_tim_nama': {'label': 'Nama Ketua Tim', 'type': 'text', 'required': True},
        'ketua_tim_nip': {'label': 'NIP Ketua Tim', 'type': 'text', 'required': True},
        'ketua_tim_jabatan': {'label': 'Jabatan Ketua Tim', 'type': 'text', 'required': True},
        'sekretaris_nama': {'label': 'Nama Sekretaris', 'type': 'text', 'required': False},
        'sekretaris_nip': {'label': 'NIP Sekretaris', 'type': 'text', 'required': False},
        'anggota1_nama': {'label': 'Nama Anggota 1', 'type': 'text', 'required': False},
        'anggota1_nip': {'label': 'NIP Anggota 1', 'type': 'text', 'required': False},
        'anggota2_nama': {'label': 'Nama Anggota 2', 'type': 'text', 'required': False},
        'anggota2_nip': {'label': 'NIP Anggota 2', 'type': 'text', 'required': False},
        'anggota3_nama': {'label': 'Nama Anggota 3', 'type': 'text', 'required': False},
        'anggota3_nip': {'label': 'NIP Anggota 3', 'type': 'text', 'required': False},
        # Progres & Realisasi
        'nomor_sk_tim': {'label': 'Nomor SK Tim', 'type': 'text', 'auto': True},
        'tanggal_sk_tim': {'label': 'Tanggal SK Tim', 'type': 'date', 'required': True},
        'progres_persen': {'label': 'Progres (%)', 'type': 'percent', 'required': False},
        'realisasi_biaya': {'label': 'Realisasi Biaya', 'type': 'currency', 'required': False},
        'realisasi_biaya_terbilang': {'label': 'Realisasi Terbilang', 'type': 'text', 'auto': True},
        'sisa_anggaran': {'label': 'Sisa Anggaran', 'type': 'currency', 'auto': True},
        'keterangan_progres': {'label': 'Keterangan Progres', 'type': 'textarea', 'required': False},
    },
}

# Flatten placeholders for easy lookup
ALL_PLACEHOLDERS: Dict[str, dict] = {}
for category, items in PLACEHOLDERS.items():
    for key, value in items.items():
        ALL_PLACEHOLDERS[key] = {**value, 'category': category}

# ============================================================================
# DOCUMENT TYPE TEMPLATES MAPPING
# ============================================================================

DOCUMENT_TEMPLATES = {
    'SPESIFIKASI': {
        'name': 'Spesifikasi Teknis',
        'type': 'word',
        'template': 'spesifikasi_teknis.docx',
        'placeholders': ['paket', 'waktu', 'satker', 'ppk', 'spesifikasi'],
    },
    'SURVEY_HARGA': {
        'name': 'Survey Harga',
        'type': 'excel',
        'template': 'survey_harga.xlsx',
        'placeholders': ['paket', 'survey'],
    },
    'SURVEY_HARGA_WORD': {
        'name': 'Survey Harga (Word)',
        'type': 'word',
        'template': 'survey_harga.docx',
        'placeholders': ['paket', 'survey'],
    },
    'HPS': {
        'name': 'Harga Perkiraan Sendiri',
        'type': 'excel',
        'template': 'hps.xlsx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk'],
    },
    'HPS_WORD': {
        'name': 'Harga Perkiraan Sendiri (Word)',
        'type': 'word',
        'template': 'hps.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk'],
    },
    'KAK': {
        'name': 'Kerangka Acuan Kerja',
        'type': 'word',
        'template': 'kak.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'spesifikasi'],
    },
    # === PROSES PEMILIHAN PENGADAAN LANGSUNG ===
    'UNDANGAN_PL': {
        'name': 'Surat Undangan Pengadaan Langsung',
        'type': 'word',
        'template': 'undangan_pl.docx',
        'placeholders': ['paket', 'nilai', 'satker', 'pp', 'penyedia'],
    },
    'BAHPL': {
        'name': 'Berita Acara Hasil Pengadaan Langsung',
        'type': 'word',
        'template': 'bahpl.docx',
        'placeholders': ['paket', 'nilai', 'satker', 'pp', 'penyedia', 'negosiasi'],
    },
    # === KONTRAK ===
    'SPK': {
        'name': 'Surat Perintah Kerja',
        'type': 'word',
        'template': 'spk.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'nomor', 'satker', 'ppk', 'penyedia'],
    },
    'SPMK': {
        'name': 'Surat Perintah Mulai Kerja',
        'type': 'word',
        'template': 'spmk.docx',
        'placeholders': ['paket', 'waktu', 'nomor', 'satker', 'ppk', 'penyedia'],
    },
    # === SURAT PESANAN (untuk Barang) & SPMK per Jenis Pengadaan ===
    'SURAT_PESANAN': {
        'name': 'Surat Pesanan',
        'type': 'word',
        'template': 'surat_pesanan.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'nomor', 'satker', 'ppk', 'penyedia'],
        'jenis_pengadaan': 'BARANG',
    },
    'SPMK_JASA_LAINNYA': {
        'name': 'SPMK Jasa Lainnya',
        'type': 'word',
        'template': 'spmk_jasa_lainnya.docx',
        'placeholders': ['paket', 'waktu', 'nomor', 'satker', 'ppk', 'penyedia'],
        'jenis_pengadaan': 'JASA_LAINNYA',
    },
    'SPMK_KONSTRUKSI': {
        'name': 'SPMK Konstruksi',
        'type': 'word',
        'template': 'spmk_konstruksi.docx',
        'placeholders': ['paket', 'waktu', 'nomor', 'satker', 'ppk', 'penyedia'],
        'jenis_pengadaan': 'KONSTRUKSI',
    },
    'BAHP': {
        'name': 'Berita Acara Hasil Pemeriksaan',
        'type': 'word',
        'template': 'bahp.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'nomor', 'penyedia', 'pemeriksa', 'pemeriksaan'],
    },
    'BAST': {
        'name': 'Berita Acara Serah Terima',
        'type': 'word',
        'template': 'bast.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'nomor', 'satker', 'ppk', 'penyedia', 'pemeriksaan'],
    },
    'SPP_LS': {
        'name': 'SPP Langsung',
        'type': 'word',
        'template': 'spp_ls.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'nomor', 'satker', 'ppk', 'ppspm', 'penyedia'],
    },
    'SPM_LS': {
        'name': 'SPM Langsung',
        'type': 'word',
        'template': 'spm_ls.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'nomor', 'satker', 'bendahara'],
    },
    'DRPP': {
        'name': 'Daftar Rincian Permintaan Pembayaran',
        'type': 'word',
        'template': 'drpp.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'nomor', 'ppk'],
    },
    'KUITANSI': {
        'name': 'Kuitansi',
        'type': 'word',
        'template': 'kuitansi.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'nomor', 'satker', 'ppk', 'bendahara', 'penyedia'],
    },
    'SSP_PPN': {
        'name': 'SSP PPN',
        'type': 'excel',
        'template': 'ssp.xlsx',
        'sheet': 'PPN',
        'placeholders': ['nilai', 'waktu', 'penyedia'],
    },
    'SSP_PPH': {
        'name': 'SSP PPh',
        'type': 'excel',
        'template': 'ssp.xlsx',
        'sheet': 'PPh',
        'placeholders': ['nilai', 'waktu', 'penyedia'],
    },
    'NOTA_DINAS_PP': {
        'name': 'Nota Dinas ke Pejabat Pengadaan',
        'type': 'word',
        'template': 'nota_dinas_pp.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'nomor', 'satker', 'ppk', 'pejabat_pengadaan'],
    },
    'SURAT_PERMINTAAN': {
        'name': 'Surat Permintaan Pelaksanaan Pengadaan',
        'type': 'word',
        'template': 'surat_permintaan_pengadaan.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'nomor', 'satker', 'ppk'],
    },
    'BA_SURVEY_HARGA': {
        'name': 'Berita Acara Survey Harga',
        'type': 'word',
        'template': 'ba_survey_harga.docx',
        'placeholders': ['paket', 'waktu', 'satker', 'ppk', 'survey'],
    },
    # === RANCANGAN KONTRAK - SPK ===
    'SPK_BARANG': {
        'name': 'SPK Pengadaan Barang',
        'type': 'word',
        'template': 'spk_barang.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia'],
        'jenis_pengadaan': 'BARANG',
    },
    'SPK_JASA_LAINNYA': {
        'name': 'SPK Jasa Lainnya',
        'type': 'word',
        'template': 'spk_jasa_lainnya.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'kak'],
        'jenis_pengadaan': 'JASA_LAINNYA',
    },
    'SPK_KONSTRUKSI': {
        'name': 'SPK Konstruksi',
        'type': 'word',
        'template': 'spk_konstruksi.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'jaminan', 'retensi'],
        'jenis_pengadaan': 'KONSTRUKSI',
    },
    # === RANCANGAN KONTRAK - SURAT PERJANJIAN ===
    'PERJANJIAN_BARANG': {
        'name': 'Surat Perjanjian Pengadaan Barang',
        'type': 'word',
        'template': 'surat_perjanjian_barang.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'garansi'],
        'jenis_pengadaan': 'BARANG',
    },
    'PERJANJIAN_JASA_LAINNYA': {
        'name': 'Surat Perjanjian Jasa Lainnya',
        'type': 'word',
        'template': 'surat_perjanjian_jasa_lainnya.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'kak', 'hki'],
        'jenis_pengadaan': 'JASA_LAINNYA',
    },
    'PERJANJIAN_KONSTRUKSI': {
        'name': 'Surat Perjanjian Konstruksi',
        'type': 'word',
        'template': 'surat_perjanjian_konstruksi.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'jaminan', 'retensi', 'pemeliharaan', 'k3'],
        'jenis_pengadaan': 'KONSTRUKSI',
    },
    # === BERITA ACARA PEMERIKSAAN (BAHP) ===
    'BAHP_BARANG': {
        'name': 'BA Pemeriksaan Barang',
        'type': 'word',
        'template': 'bahp_barang.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'pphp', 'items'],
        'jenis_pengadaan': 'BARANG',
    },
    'BAHP_JASA_LAINNYA': {
        'name': 'BA Pemeriksaan Jasa Lainnya',
        'type': 'word',
        'template': 'bahp_jasa_lainnya.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'pphp', 'output'],
        'jenis_pengadaan': 'JASA_LAINNYA',
    },
    'BAHP_KONSTRUKSI': {
        'name': 'BA Pemeriksaan Konstruksi',
        'type': 'word',
        'template': 'bahp_konstruksi.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'pphp', 'konsultan', 'progres', 'mutu'],
        'jenis_pengadaan': 'KONSTRUKSI',
    },
    # === BERITA ACARA SERAH TERIMA (BAST) ===
    'BAST_BARANG': {
        'name': 'BA Serah Terima Barang',
        'type': 'word',
        'template': 'bast_barang.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'pphp', 'garansi', 'items'],
        'jenis_pengadaan': 'BARANG',
    },
    'BAST_JASA_LAINNYA': {
        'name': 'BA Serah Terima Jasa Lainnya',
        'type': 'word',
        'template': 'bast_jasa_lainnya.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'pphp', 'output'],
        'jenis_pengadaan': 'JASA_LAINNYA',
    },
    'BAST_KONSTRUKSI_PHO': {
        'name': 'BA Serah Terima Pertama (PHO)',
        'type': 'word',
        'template': 'bast_konstruksi_pho.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'pphp', 'pemeliharaan', 'retensi', 'progres'],
        'jenis_pengadaan': 'KONSTRUKSI',
    },
    'BAST_KONSTRUKSI_FHO': {
        'name': 'BA Serah Terima Akhir (FHO)',
        'type': 'word',
        'template': 'bast_konstruksi_fho.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'pphp', 'retensi'],
        'jenis_pengadaan': 'KONSTRUKSI',
    },
    # === BERITA ACARA PEMBAYARAN (BAP) ===
    'BAP_SEKALIGUS': {
        'name': 'BA Pembayaran Sekaligus',
        'type': 'word',
        'template': 'bap_sekaligus.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'pajak', 'rekening'],
        'cara_bayar': 'SEKALIGUS',
    },
    'BAP_TERMIN': {
        'name': 'BA Pembayaran Termin',
        'type': 'word',
        'template': 'bap_termin.docx',
        'placeholders': ['paket', 'nilai', 'waktu', 'satker', 'ppk', 'penyedia', 'termin', 'progres', 'retensi', 'pajak', 'rekening'],
        'cara_bayar': 'TERMIN',
    },

    # ========================================================================
    # PERJALANAN DINAS
    # ========================================================================
    'SURAT_TUGAS': {
        'name': 'Surat Tugas',
        'type': 'word',
        'template': 'surat_tugas.docx',
        'placeholders': ['satker', 'ppk', 'perjalanan_dinas'],
    },
    'SURAT_PERMOHONAN_TUP': {
        'name': 'Surat Permohonan TUP',
        'type': 'word',
        'template': 'surat_permohonan_tup.docx',
        'placeholders': ['satker', 'ppk'],
    },
    'SPPD': {
        'name': 'Surat Perintah Perjalanan Dinas',
        'type': 'word',
        'template': 'sppd.docx',
        'placeholders': ['paket', 'satker', 'ppk', 'bendahara', 'perjalanan_dinas'],
    },
    'KUITANSI_UM': {
        'name': 'Kuitansi Uang Muka Perjalanan Dinas',
        'type': 'word',
        'template': 'kuitansi_uang_muka.docx',
        'placeholders': ['paket', 'satker', 'ppk', 'bendahara', 'perjalanan_dinas'],
    },
    'RINCIAN_BIAYA_PD': {
        'name': 'Rincian Biaya Perjalanan Dinas',
        'type': 'word',
        'template': 'rincian_biaya_pd.docx',
        'placeholders': ['satker', 'ppk', 'perjalanan_dinas'],
    },
    'LAPORAN_PD': {
        'name': 'Laporan Perjalanan Dinas',
        'type': 'word',
        'template': 'laporan_perjalanan_dinas.docx',
        'placeholders': ['satker', 'ppk', 'perjalanan_dinas'],
    },
    'KUITANSI_RAMPUNG': {
        'name': 'Kuitansi Rampung Perjalanan Dinas',
        'type': 'word',
        'template': 'kuitansi_rampung.docx',
        'placeholders': ['paket', 'satker', 'ppk', 'bendahara', 'perjalanan_dinas'],
    },
    'DAFTAR_PENGELUARAN_RIIL': {
        'name': 'Daftar Pengeluaran Riil',
        'type': 'word',
        'template': 'daftar_pengeluaran_riil.docx',
        'placeholders': ['satker', 'ppk', 'perjalanan_dinas'],
    },

    # ========================================================================
    # SWAKELOLA
    # ========================================================================
    'KAK_SWAKELOLA': {
        'name': 'KAK Swakelola',
        'type': 'word',
        'template': 'kak_swakelola.docx',
        'placeholders': ['satker', 'ppk', 'swakelola'],
    },
    'RAB_SWAKELOLA': {
        'name': 'RAB Swakelola',
        'type': 'excel',
        'template': 'rab_swakelola.xlsx',
        'placeholders': ['satker', 'ppk', 'swakelola'],
    },
    'SK_TIM_SWAKELOLA': {
        'name': 'SK Tim Pelaksana Swakelola',
        'type': 'word',
        'template': 'sk_tim_swakelola.docx',
        'placeholders': ['satker', 'ppk', 'swakelola'],
    },
    'BAP_SWAKELOLA': {
        'name': 'Berita Acara Pembayaran Swakelola',
        'type': 'word',
        'template': 'bap_swakelola.docx',
        'placeholders': ['satker', 'ppk', 'bendahara', 'swakelola'],
    },
    'LAPORAN_KEMAJUAN': {
        'name': 'Laporan Kemajuan Swakelola',
        'type': 'word',
        'template': 'laporan_kemajuan.docx',
        'placeholders': ['satker', 'ppk', 'swakelola'],
    },
    'BAST_SWAKELOLA': {
        'name': 'BA Serah Terima Swakelola',
        'type': 'word',
        'template': 'bast_swakelola.docx',
        'placeholders': ['satker', 'ppk', 'swakelola'],
    },

    # ========================================================================
    # JAMUAN TAMU / RAPAT
    # ========================================================================
    'DAFTAR_HADIR_JAMUAN_TAMU': {
        'name': 'Daftar Hadir Jamuan Tamu',
        'type': 'word',
        'template': 'daftar_hadir_jamuan_tamu.docx',
        'placeholders': ['satker', 'ppk'],
    },
    'NOTA_DINAS_JAMUAN_TAMU': {
        'name': 'Nota Dinas Jamuan Tamu',
        'type': 'word',
        'template': 'nota_dinas_jamuan_tamu.docx',
        'placeholders': ['satker', 'ppk'],
    },
    'SK_KPA_JAMUAN_TAMU': {
        'name': 'SK KPA Jamuan Tamu',
        'type': 'word',
        'template': 'sk_kpa_jamuan_tamu.docx',
        'placeholders': ['satker', 'ppk'],
    },
    'KUITANSI_JAMUAN_TAMU': {
        'name': 'Kuitansi Jamuan Tamu',
        'type': 'word',
        'template': 'kuitansi_jamuan_tamu.docx',
        'placeholders': ['satker', 'ppk', 'bendahara'],
    },
    'LAPORAN_JAMUAN_TAMU': {
        'name': 'Laporan Jamuan Tamu',
        'type': 'word',
        'template': 'laporan_jamuan_tamu.docx',
        'placeholders': ['satker', 'ppk'],
    },

    # ========================================================================
    # DAFTAR HADIR (UMUM)
    # ========================================================================
    'DAFTAR_HADIR_SWAKELOLA': {
        'name': 'Daftar Hadir Swakelola',
        'type': 'word',
        'template': 'daftar_hadir_swakelola.docx',
        'placeholders': ['satker', 'ppk', 'swakelola'],
    },

    # ========================================================================
    # KUITANSI TAMBAHAN
    # ========================================================================
    'KUITANSI_HONORARIUM': {
        'name': 'Kuitansi Honorarium',
        'type': 'word',
        'template': 'kuitansi_honorarium.docx',
        'placeholders': ['satker', 'ppk', 'bendahara'],
    },
    'KUITANSI_HONOR_PENGELOLA': {
        'name': 'Kuitansi Honor Pengelola',
        'type': 'word',
        'template': 'kuitansi_honor_pengelola.docx',
        'placeholders': ['satker', 'ppk', 'bendahara'],
    },

    # ========================================================================
    # DOKUMEN LAINNYA
    # ========================================================================
    'BUKTI_SERAH_TERIMA_UM': {
        'name': 'Bukti Serah Terima Uang Muka',
        'type': 'word',
        'template': 'bukti_serah_terima_um.docx',
        'placeholders': ['satker', 'ppk', 'penyedia'],
    },
    'BA_MC': {
        'name': 'Berita Acara Monitoring dan Evaluasi',
        'type': 'word',
        'template': 'ba_mc.docx',
        'placeholders': ['satker', 'ppk', 'paket'],
    },
    'LEMBAR_PERMINTAAN': {
        'name': 'Lembar Permintaan/Order',
        'type': 'word',
        'template': 'lembar_permintaan.docx',
        'placeholders': ['satker', 'ppk', 'penyedia'],
    },
    'NOTULEN': {
        'name': 'Notulen Rapat',
        'type': 'word',
        'template': 'notulen.docx',
        'placeholders': ['satker', 'ppk'],
    },
    'SK_KPA': {
        'name': 'Surat Keputusan KPA',
        'type': 'word',
        'template': 'sk_kpa.docx',
        'placeholders': ['satker', 'ppk'],
    },
    'SPBY': {
        'name': 'Surat Penawaran Barang/Jasa',
        'type': 'word',
        'template': 'spby.docx',
        'placeholders': ['satker', 'ppk', 'penyedia'],
    },
    'SSKK': {
        'name': 'Surat Setoran Kemasan/Karung',
        'type': 'word',
        'template': 'sskk.docx',
        'placeholders': ['satker', 'ppk'],
    },
    'SSUK': {
        'name': 'Surat Setoran Uang Kembalian',
        'type': 'word',
        'template': 'ssuk.docx',
        'placeholders': ['satker', 'ppk', 'bendahara'],
    },
    'LPJ': {
        'name': 'Laporan Pertanggungjawaban',
        'type': 'word',
        'template': 'lpj.docx',
        'placeholders': ['satker', 'ppk'],
    },
    'MONEV': {
        'name': 'Laporan Monitoring dan Evaluasi',
        'type': 'word',
        'template': 'monev.docx',
        'placeholders': ['satker', 'ppk', 'paket'],
    },
    'LAPORAN_KEGIATAN': {
        'name': 'Laporan Kegiatan',
        'type': 'word',
        'template': 'laporan_kegiatan.docx',
        'placeholders': ['satker', 'ppk'],
    },

    # ========================================================================
    # EXCEL - LAPORAN DAN REKAPITULASI
    # ========================================================================
    'PERHITUNGAN_TAMBAH_KURANG': {
        'name': 'Perhitungan Tambah/Kurang',
        'type': 'excel',
        'template': 'perhitungan_tambah_kurang.xlsx',
        'placeholders': ['paket', 'nilai'],
    },
    'RAB_SPPD': {
        'name': 'RAB SPPD',
        'type': 'excel',
        'template': 'rab_sppd.xlsx',
        'placeholders': ['paket', 'perjalanan_dinas'],
    },
    'REKAP_BUKTI_PENGELUARAN': {
        'name': 'Rekap Bukti Pengeluaran',
        'type': 'excel',
        'template': 'rekap_bukti_pengeluaran.xlsx',
        'placeholders': ['paket'],
    },
    'REKAP_FINAL': {
        'name': 'Rekapitulasi Final',
        'type': 'excel',
        'template': 'rekap_final.xlsx',
        'placeholders': ['paket'],
    },
    'REKAP_TUP': {
        'name': 'Rekapitulasi TUP',
        'type': 'excel',
        'template': 'rekap_tup.xlsx',
        'placeholders': ['paket'],
    },
    'RINCIAN_TUP': {
        'name': 'Rincian TUP',
        'type': 'excel',
        'template': 'rincian_tup.xlsx',
        'placeholders': ['paket'],
    },
    'SSBP': {
        'name': 'Surat Setoran Barang Persediaan',
        'type': 'excel',
        'template': 'ssbp.xlsx',
        'placeholders': ['satker'],
    },
}

# ============================================================================
# PHASE → DOCUMENT CHECKLIST MAPPING
# ============================================================================

PHASE_TEMPLATE_GROUPS = [
    {
        'id': 'PERENCANAAN',
        'name': 'Perencanaan',
        'description': 'Dokumen dasar sebelum pemilihan',
        'documents': [
            {'code': 'SPESIFIKASI', 'label': 'Spesifikasi Teknis'},
            {'code': 'SURVEY_HARGA', 'label': 'Survey Harga (Excel)'},
            {'code': 'BA_SURVEY_HARGA', 'label': 'BA Survey Harga'},
            {'code': 'HPS', 'label': 'HPS'},
            {'code': 'KAK', 'label': 'KAK/TOR'},
            {'code': 'NOTA_DINAS_PP', 'label': 'Nota Dinas PP'},
            {'code': 'SURAT_PERMINTAAN', 'label': 'Surat Permintaan Pengadaan'},
        ],
    },
    {
        'id': 'PEMILIHAN',
        'name': 'Pemilihan',
        'description': 'Undangan dan hasil pemilihan/negosiasi',
        'documents': [
            {'code': 'UNDANGAN_PL', 'label': 'Undangan Pengadaan Langsung'},
            {'code': 'BAHPL', 'label': 'BA Hasil Pengadaan Langsung'},
        ],
    },
    {
        'id': 'KONTRAK',
        'name': 'Kontrak',
        'description': 'Kontrak/SPK dan surat perjanjian',
        'documents': [
            {'code': 'SPK', 'label': 'SPK (default)'},
            {'code': 'SPK_BARANG', 'label': 'SPK Barang'},
            {'code': 'SPK_JASA_LAINNYA', 'label': 'SPK Jasa Lainnya'},
            {'code': 'SPK_KONSTRUKSI', 'label': 'SPK Konstruksi'},
            {'code': 'SURAT_PESANAN', 'label': 'Surat Pesanan'},
            {'code': 'PERJANJIAN_BARANG', 'label': 'Surat Perjanjian Barang'},
            {'code': 'PERJANJIAN_JASA_LAINNYA', 'label': 'Surat Perjanjian Jasa Lainnya'},
            {'code': 'PERJANJIAN_KONSTRUKSI', 'label': 'Surat Perjanjian Konstruksi'},
        ],
    },
    {
        'id': 'PELAKSANAAN',
        'name': 'Pelaksanaan',
        'description': 'Perintah mulai dan berita acara pemeriksaan',
        'documents': [
            {'code': 'SPMK', 'label': 'SPMK (default)'},
            {'code': 'SPMK_JASA_LAINNYA', 'label': 'SPMK Jasa Lainnya'},
            {'code': 'SPMK_KONSTRUKSI', 'label': 'SPMK Konstruksi'},
            {'code': 'BAHP', 'label': 'BAHP (default)'},
            {'code': 'BAHP_BARANG', 'label': 'BAHP Barang'},
            {'code': 'BAHP_JASA_LAINNYA', 'label': 'BAHP Jasa Lainnya'},
            {'code': 'BAHP_KONSTRUKSI', 'label': 'BAHP Konstruksi'},
        ],
    },
    {
        'id': 'PEMBAYARAN',
        'name': 'Pembayaran',
        'description': 'Serah terima, BAP, dan dokumen bayar',
        'documents': [
            {'code': 'BAST', 'label': 'BAST (default)'},
            {'code': 'BAST_BARANG', 'label': 'BAST Barang'},
            {'code': 'BAST_JASA_LAINNYA', 'label': 'BAST Jasa Lainnya'},
            {'code': 'BAST_KONSTRUKSI_PHO', 'label': 'BAST Konstruksi PHO'},
            {'code': 'BAST_KONSTRUKSI_FHO', 'label': 'BAST Konstruksi FHO'},
            {'code': 'BAP_TERMIN', 'label': 'BAP Termin'},
            {'code': 'BAP_SEKALIGUS', 'label': 'BAP Sekaligus'},
            {'code': 'SPP_LS', 'label': 'SPP-LS'},
            {'code': 'DRPP', 'label': 'DRPP'},
            {'code': 'KUITANSI', 'label': 'Kuitansi'},
            {'code': 'SSP_PPN', 'label': 'SSP PPN (Excel)'},
            {'code': 'SSP_PPH', 'label': 'SSP PPh (Excel)'},
        ],
    },
    {
        'id': 'PENUTUP',
        'name': 'Penutup/Audit',
        'description': 'Arsip akhir dan jejak audit',
        'documents': [
            {'code': None, 'label': 'Checklist arsip akhir (belum ada template)'},
            {'code': None, 'label': 'Log aktivitas/audit trail (belum ada template)'},
        ],
    },
]

# ============================================================================
# TAX CONFIGURATION
# ============================================================================

TAX_RATES = {
    'PPN': 0.11,
    'PPH_21_NPWP': 0.05,
    'PPH_21_NON_NPWP': 0.06,
    'PPH_22': 0.015,
    'PPH_23': 0.02,
    'PPH_4_2_KONSTRUKSI': 0.025,
}

# ============================================================================
# NUMBERING PREFIXES
# ============================================================================

NUMBERING_PREFIXES = {
    'SPESIFIKASI': 'SPEC',
    'HPS': 'HPS',
    'KAK': 'KAK',
    'SPK': 'SPK',
    'SPMK': 'SPMK',
    'BAHP': 'BAHP',
    'BAST': 'BAST',
    'SPP_LS': 'SPP-LS',
    'DRPP': 'DRPP',
    'KUITANSI': 'KWT',
    'SSP_PPN': 'SSP-PPN',
    'SSP_PPH': 'SSP-PPH',
    'NOTA_DINAS_PP': 'ND',
    'SURAT_PERMINTAAN': 'SP',
    'BA_SURVEY_HARGA': 'BA-SH',
    # Proses Pemilihan Pengadaan Langsung
    'UNDANGAN_PL': 'UND.PL',
    'BAHPL': 'BA.HPL',
    # SPK per jenis pengadaan
    'SPK_BARANG': 'SPK-B',
    'SPK_JASA_LAINNYA': 'SPK-J',
    'SPK_KONSTRUKSI': 'SPK-K',
    # Surat Pesanan (Barang) & SPMK per jenis pengadaan
    'SURAT_PESANAN': 'SP-B',
    'SPMK_JASA_LAINNYA': 'SPMK-J',
    'SPMK_KONSTRUKSI': 'SPMK-K',
    # Surat Perjanjian per jenis pengadaan
    'PERJANJIAN_BARANG': 'KTR-B',
    'PERJANJIAN_JASA_LAINNYA': 'KTR-J',
    'PERJANJIAN_KONSTRUKSI': 'KTR-K',
    # BAHP per jenis pengadaan
    'BAHP_BARANG': 'BAHP-B',
    'BAHP_JASA_LAINNYA': 'BAHP-J',
    'BAHP_KONSTRUKSI': 'BAHP-K',
    # BAST per jenis pengadaan
    'BAST_BARANG': 'BAST-B',
    'BAST_JASA_LAINNYA': 'BAST-J',
    'BAST_KONSTRUKSI_PHO': 'PHO',
    'BAST_KONSTRUKSI_FHO': 'FHO',
    # BAP per cara bayar
    'BAP_SEKALIGUS': 'BAP',
    'BAP_TERMIN': 'BAP-T',
    # Perjalanan Dinas
    'SURAT_TUGAS': 'ST',
    'SPPD': 'SPPD',
    'KUITANSI_UM': 'KWT-UM',
    'RINCIAN_BIAYA_PD': 'RBPD',
    'LAPORAN_PD': 'LPD',
    'KUITANSI_RAMPUNG': 'KWT-R',
    'DAFTAR_PENGELUARAN_RIIL': 'DPR',
    # Swakelola
    'KAK_SWAKELOLA': 'KAK-SW',
    'RAB_SWAKELOLA': 'RAB-SW',
    'SK_TIM_SWAKELOLA': 'SK-TIM',
    'BAP_SWAKELOLA': 'BAP-SW',
    'LAPORAN_KEMAJUAN': 'LK-SW',
    'BAST_SWAKELOLA': 'BAST-SW',
}

# ============================================================================
# BULAN INDONESIA
# ============================================================================

BULAN_INDONESIA = [
    '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]

HARI_INDONESIA = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
