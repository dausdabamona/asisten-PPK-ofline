"""
PPK DOCUMENT FACTORY - Checklist Dokumen Pertanggungjawaban
============================================================
Konfigurasi checklist dokumen berdasarkan jenis kegiatan/belanja.
Setiap jenis memiliki daftar dokumen yang wajib dilengkapi.
"""

from typing import Dict, List, Any

# ============================================================================
# A. HONORARIUM
# ============================================================================

HONORARIUM_CHECKLIST = {
    "PENGELOLA_KEUANGAN": {
        "nama": "Pengelola Keuangan/PBJ/PNBP/SAI/BMN",
        "dokumen": [
            {"kode": "SK_PENETAPAN", "nama": "SK Penetapan", "wajib": True},
            {"kode": "DAFTAR_NOMINATIF", "nama": "Daftar Nominatif + Bukti Bayar", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "SSP", "nama": "SSP (Surat Setoran Pajak)", "wajib": True},
        ]
    },
    "NARASUMBER": {
        "nama": "Narasumber/Moderator/Pembawa Acara",
        "dokumen": [
            {"kode": "UNDANGAN", "nama": "Surat Undangan + Susunan Acara", "wajib": True},
            {"kode": "SURAT_TUGAS", "nama": "Surat Tugas", "wajib": True},
            {"kode": "MATERI", "nama": "Materi Presentasi", "wajib": True},
            {"kode": "BIODATA", "nama": "Biodata Narasumber", "wajib": True},
            {"kode": "DAFTAR_HADIR", "nama": "Daftar Hadir", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
            {"kode": "NOTULENSI", "nama": "Notulensi", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "SAKSI_AHLI": {
        "nama": "Saksi Ahli/Beracara",
        "dokumen": [
            {"kode": "UNDANGAN", "nama": "Surat Undangan/Pemanggilan", "wajib": True},
            {"kode": "SURAT_TUGAS", "nama": "Surat Tugas", "wajib": True},
            {"kode": "NOTULENSI", "nama": "Notulensi", "wajib": True},
            {"kode": "DAFTAR_HADIR", "nama": "Daftar Hadir", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "PENYULUH_NON_PNS": {
        "nama": "Penyuluh Non-PNS",
        "dokumen": [
            {"kode": "SK_PENETAPAN", "nama": "SK Penetapan (Eselon I)", "wajib": True},
            {"kode": "LAPORAN", "nama": "Laporan Penyuluhan", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
            {"kode": "REKAP_ABSENSI", "nama": "Rekap Absensi Bulanan", "wajib": True},
        ]
    },
    "ROHANIWAN": {
        "nama": "Rohaniwan",
        "dokumen": [
            {"kode": "PERMOHONAN", "nama": "Surat Permohonan", "wajib": True},
            {"kode": "UNDANGAN", "nama": "Undangan Pegawai Dilantik", "wajib": True},
            {"kode": "DAFTAR_HADIR", "nama": "Daftar Hadir", "wajib": True},
            {"kode": "FOTO", "nama": "Foto Dokumentasi", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "TIM_PELAKSANA": {
        "nama": "Tim Pelaksana/Sekretariat",
        "dokumen": [
            {"kode": "SK", "nama": "SK Menteri/Es.I/KPA", "wajib": True},
            {"kode": "UNDANGAN", "nama": "Undangan Peserta", "wajib": True},
            {"kode": "DAFTAR_NOMINATIF", "nama": "Daftar Nominatif + Bukti Bayar", "wajib": True},
            {"kode": "DAFTAR_HADIR", "nama": "Daftar Hadir", "wajib": True},
            {"kode": "LAPORAN", "nama": "Laporan + Foto Geotagging", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "TIM_JURNAL": {
        "nama": "Tim Jurnal/Buletin/Website",
        "dokumen": [
            {"kode": "SK", "nama": "SK Penetapan", "wajib": True},
            {"kode": "DAFTAR_NOMINATIF", "nama": "Daftar Nominatif", "wajib": True},
            {"kode": "SAMPUL", "nama": "Sampul/Tangkapan Layar Penerbitan", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "PENYELENGGARA_UJIAN": {
        "nama": "Penyelenggara Ujian & Vakasi",
        "dokumen": [
            {"kode": "SK", "nama": "SK KPA", "wajib": True},
            {"kode": "DAFTAR_NOMINATIF", "nama": "Daftar Nominatif", "wajib": True},
            {"kode": "LAPORAN", "nama": "Laporan + Foto", "wajib": True},
            {"kode": "DAFTAR_HADIR", "nama": "Daftar Hadir", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "PENYELENGGARA_DIKLAT": {
        "nama": "Penyelenggara Diklat",
        "dokumen": [
            {"kode": "SK", "nama": "SK Penetapan", "wajib": True},
            {"kode": "DAFTAR_NOMINATIF", "nama": "Daftar Nominatif", "wajib": True},
            {"kode": "LAPORAN", "nama": "Laporan Kegiatan", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
}

# ============================================================================
# B. PERJALANAN DINAS
# ============================================================================

PERJALANAN_DINAS_CHECKLIST = {
    "DALAM_NEGERI": {
        "nama": "Perjalanan Dinas Dalam Negeri",
        "dokumen": [
            {"kode": "SURAT_TUGAS", "nama": "Surat Tugas", "wajib": True},
            {"kode": "SPD", "nama": "SPD (distempel tujuan)", "wajib": True},
            {"kode": "RINCIAN_BIAYA", "nama": "Rincian Biaya", "wajib": True},
            {"kode": "DAFTAR_NOMINATIF", "nama": "Daftar Nominatif (jika >1 orang/LS)", "wajib": False},
            {"kode": "TIKET", "nama": "Tiket + Boarding Pass", "wajib": True},
            {"kode": "STRUK_TRANSPORT", "nama": "Struk Taksi/Toll/BBM", "wajib": False},
            {"kode": "INVOICE_HOTEL", "nama": "Invoice Hotel", "wajib": True},
            {"kode": "FOTO_GEOTAG_BERANGKAT", "nama": "Foto Geotagging Keberangkatan", "wajib": True},
            {"kode": "FOTO_GEOTAG_PULANG", "nama": "Foto Geotagging Kepulangan", "wajib": True},
            {"kode": "LAPORAN", "nama": "Laporan + Foto", "wajib": True},
        ]
    },
    "LUAR_NEGERI": {
        "nama": "Perjalanan Dinas Luar Negeri",
        "dokumen": [
            {"kode": "UNDANGAN", "nama": "Surat Undangan", "wajib": True},
            {"kode": "SURAT_TUGAS", "nama": "Surat Tugas", "wajib": True},
            {"kode": "AGENDA", "nama": "Agenda Kegiatan", "wajib": True},
            {"kode": "PASPOR", "nama": "Fotokopi Paspor + Exit Permit", "wajib": True},
            {"kode": "PERSETUJUAN_SETNEG", "nama": "Persetujuan Setneg", "wajib": True},
            {"kode": "TIKET", "nama": "Tiket + Boarding Pass", "wajib": True},
            {"kode": "RINCIAN_BIAYA", "nama": "Rincian Biaya", "wajib": True},
            {"kode": "SPD_LN", "nama": "SPD-LN", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
            {"kode": "LAPORAN", "nama": "Laporan Perjalanan", "wajib": True},
        ]
    },
    "TRANSPORT_LOKAL": {
        "nama": "Transport Lokal",
        "dokumen": [
            {"kode": "SURAT_TUGAS", "nama": "Surat Tugas", "wajib": True},
            {"kode": "FORM_5", "nama": "Form 5 (distempel)", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "LAPORAN", "nama": "Laporan", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
        ]
    },
}

# ============================================================================
# C. LEMBUR
# ============================================================================

LEMBUR_CHECKLIST = {
    "LEMBUR": {
        "nama": "Uang Lembur",
        "dokumen": [
            {"kode": "SURAT_TUGAS", "nama": "Surat Tugas/Perintah Lembur", "wajib": True},
            {"kode": "DAFTAR_HADIR", "nama": "Daftar Hadir Lembur", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
            {"kode": "LAPORAN", "nama": "Laporan Hasil Kerja", "wajib": True},
            {"kode": "DAFTAR_JAM", "nama": "Daftar Jam Lembur", "wajib": True},
            {"kode": "REKAP_ABSENSI", "nama": "Rekap Absensi Bulanan", "wajib": True},
            {"kode": "BUKTI_BAYAR", "nama": "Bukti Pembayaran", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
}

# ============================================================================
# D. SEWA & KONSUMSI
# ============================================================================

SEWA_KONSUMSI_CHECKLIST = {
    "SEWA_KENDARAAN_INSIDENTIL": {
        "nama": "Sewa Kendaraan Insidentil",
        "dokumen": [
            {"kode": "KUITANSI", "nama": "Kuitansi + Stempel Penyedia", "wajib": True},
            {"kode": "SURAT_TUGAS", "nama": "Surat Tugas", "wajib": True},
            {"kode": "SIM_STNK", "nama": "Fotokopi SIM & STNK", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "SEWA_KENDARAAN_OPERASIONAL": {
        "nama": "Sewa Kendaraan Operasional",
        "dokumen": [
            {"kode": "KONTRAK", "nama": "Kontrak/Perjanjian", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi + Stempel", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "SEWA_GEDUNG": {
        "nama": "Sewa Gedung Pertemuan",
        "dokumen": [
            {"kode": "SPK", "nama": "SPK/Perjanjian", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "SEWA_MESIN_FOTOKOPI": {
        "nama": "Sewa Mesin Fotokopi",
        "dokumen": [
            {"kode": "SPK", "nama": "SPK/Perjanjian", "wajib": True},
            {"kode": "TAGIHAN", "nama": "Tagihan Bulanan", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "FOTO_COUNTER", "nama": "Foto Counter Awal-Akhir Geotagging", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "PAKET_RAPAT_LUAR": {
        "nama": "Paket Rapat Luar Kantor",
        "dokumen": [
            {"kode": "UNDANGAN", "nama": "Undangan", "wajib": True},
            {"kode": "DAFTAR_HADIR", "nama": "Daftar Hadir", "wajib": True},
            {"kode": "SPK", "nama": "SPK/Perjanjian", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
            {"kode": "NOTULENSI", "nama": "Notulensi", "wajib": True},
            {"kode": "SURAT_PERNYATAAN", "nama": "Surat Pernyataan PPK (fasilitas kantor tidak cukup)", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "KONSUMSI_RAPAT": {
        "nama": "Konsumsi Rapat",
        "dokumen": [
            {"kode": "UNDANGAN", "nama": "Undangan", "wajib": True},
            {"kode": "DAFTAR_HADIR", "nama": "Daftar Hadir", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "FOTO_KONSUMSI", "nama": "Foto Konsumsi + Rapat Geotagging", "wajib": True},
            {"kode": "NOTULENSI", "nama": "Notulensi", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "KONSUMSI_JAMUAN": {
        "nama": "Konsumsi Jamuan Tamu",
        "dokumen": [
            {"kode": "BUKU_TAMU", "nama": "Buku Tamu", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
}

# ============================================================================
# E. PENGADAAN BARANG/JASA
# ============================================================================

PENGADAAN_CHECKLIST = {
    "BARANG_LANGSUNG": {
        "nama": "Pengadaan Barang Langsung/Swakelola",
        "dokumen": [
            {"kode": "SPK", "nama": "SPK/Perjanjian/Pesanan", "wajib": True},
            {"kode": "BA_PEMERIKSAAN", "nama": "BA Pemeriksaan", "wajib": True},
            {"kode": "BA_PENYELESAIAN", "nama": "BA Penyelesaian", "wajib": True},
            {"kode": "BAST", "nama": "BAST", "wajib": True},
            {"kode": "PERMOHONAN_BAYAR", "nama": "Permohonan Bayar", "wajib": True},
            {"kode": "BA_PEMBAYARAN", "nama": "BA Pembayaran", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi Bermaterai", "wajib": True},
            {"kode": "EFAKTUR", "nama": "e-Faktur", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
            {"kode": "NPWP_REKENING", "nama": "Fotokopi NPWP + Rekening", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
        ]
    },
    "KONSTRUKSI": {
        "nama": "Pekerjaan Konstruksi",
        "dokumen": [
            {"kode": "SPK", "nama": "SPK/Perjanjian", "wajib": True},
            {"kode": "LAPORAN_PROGRES", "nama": "Laporan Progres Fisik", "wajib": True},
            {"kode": "BA_PEMERIKSAAN", "nama": "BA Pemeriksaan", "wajib": True},
            {"kode": "BA_PENYELESAIAN", "nama": "BA Penyelesaian", "wajib": True},
            {"kode": "BAST", "nama": "BAST", "wajib": True},
            {"kode": "PERMOHONAN_BAYAR", "nama": "Permohonan Bayar", "wajib": True},
            {"kode": "BA_PEMBAYARAN", "nama": "BA Pembayaran", "wajib": True},
            {"kode": "SIUK", "nama": "SIUK/NIB", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi Bermaterai", "wajib": True},
            {"kode": "EFAKTUR", "nama": "e-Faktur", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
            {"kode": "NPWP_REKENING", "nama": "Fotokopi NPWP + Rekening", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
        ]
    },
    "JASA_KONSULTAN": {
        "nama": "Jasa Konsultan (Konstruksi & Non)",
        "dokumen": [
            {"kode": "SPK", "nama": "SPK/Perjanjian", "wajib": True},
            {"kode": "LAPORAN_PENDAHULUAN", "nama": "Laporan Pendahuluan", "wajib": True},
            {"kode": "LAPORAN_KEMAJUAN", "nama": "Laporan Kemajuan", "wajib": True},
            {"kode": "LAPORAN_AKHIR", "nama": "Laporan Akhir", "wajib": True},
            {"kode": "BAST", "nama": "BAST", "wajib": True},
            {"kode": "PERMOHONAN_BAYAR", "nama": "Permohonan Bayar", "wajib": True},
            {"kode": "BA_PEMBAYARAN", "nama": "BA Pembayaran", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi Bermaterai", "wajib": True},
            {"kode": "EFAKTUR", "nama": "e-Faktur", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
            {"kode": "NPWP_REKENING", "nama": "Fotokopi NPWP + Rekening", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
        ]
    },
}

# ============================================================================
# F. OPERASIONAL & PEMELIHARAAN
# ============================================================================

OPERASIONAL_CHECKLIST = {
    "LANGGANAN_DAYA": {
        "nama": "Langganan Daya & Jasa",
        "dokumen": [
            {"kode": "BUKTI_TAGIHAN", "nama": "Bukti Tagihan", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
        ]
    },
    "BBM_KENDARAAN": {
        "nama": "BBM Kendaraan Dinas",
        "dokumen": [
            {"kode": "SK_PJ", "nama": "SK Penanggung Jawab", "wajib": True},
            {"kode": "PERHITUNGAN", "nama": "Perhitungan Biaya", "wajib": True},
            {"kode": "STRUK_BBM", "nama": "Struk BBM/MyPertamina", "wajib": True},
            {"kode": "FOTO_ODOMETER", "nama": "Foto Odometer Awal-Akhir", "wajib": True},
        ]
    },
    "PEMELIHARAAN_KENDARAAN": {
        "nama": "Pemeliharaan Kendaraan",
        "dokumen": [
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "FAKTUR", "nama": "Faktur Rincian", "wajib": True},
            {"kode": "FOTO_HASIL", "nama": "Foto Hasil Perbaikan", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "PEMELIHARAAN_PERALATAN": {
        "nama": "Pemeliharaan Peralatan/Mesin",
        "dokumen": [
            {"kode": "SPK", "nama": "SPK/Perjanjian", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "FAKTUR", "nama": "Faktur Rincian", "wajib": True},
            {"kode": "FOTO_HASIL", "nama": "Foto Hasil", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "PEMELIHARAAN_GEDUNG": {
        "nama": "Pemeliharaan Gedung/Bangunan",
        "dokumen": [
            {"kode": "SPK", "nama": "SPK/Perjanjian", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "FAKTUR", "nama": "Faktur Rincian", "wajib": True},
            {"kode": "FOTO_HASIL", "nama": "Foto Hasil", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
        ]
    },
    "PENGGANDAAN": {
        "nama": "Penggandaan/Penjilidan",
        "dokumen": [
            {"kode": "KUITANSI", "nama": "Kuitansi", "wajib": True},
            {"kode": "FAKTUR", "nama": "Faktur Rincian", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Hasil Geotagging", "wajib": True},
        ]
    },
}

# ============================================================================
# G. BANTUAN PEMERINTAH
# ============================================================================

BANTUAN_PEMERINTAH_CHECKLIST = {
    "BANTUAN_BARANG": {
        "nama": "Bantuan Pemerintah Bentuk Barang",
        "dokumen": [
            {"kode": "SK_PENERIMA", "nama": "SK Penetapan Penerima", "wajib": True},
            {"kode": "SPK", "nama": "SPK/Perjanjian", "wajib": True},
            {"kode": "BA_PEMERIKSAAN", "nama": "BA Pemeriksaan", "wajib": True},
            {"kode": "BA_PENYELESAIAN", "nama": "BA Penyelesaian", "wajib": True},
            {"kode": "BAST_PENYEDIA", "nama": "BAST (Penyedia ke PPK)", "wajib": True},
            {"kode": "PERMOHONAN_BAYAR", "nama": "Permohonan Bayar", "wajib": True},
            {"kode": "BA_PEMBAYARAN", "nama": "BA Pembayaran", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi Bermaterai", "wajib": True},
            {"kode": "EFAKTUR", "nama": "e-Faktur", "wajib": True},
            {"kode": "SSP", "nama": "SSP", "wajib": True},
            {"kode": "NPWP_REKENING", "nama": "NPWP + Rekening", "wajib": True},
            {"kode": "BAST_PENERIMA", "nama": "BAST (KPB ke Penerima)", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
        ]
    },
    "BANTUAN_UANG": {
        "nama": "Bantuan Pemerintah Bentuk Uang",
        "dokumen": [
            {"kode": "SK_PENERIMA", "nama": "SK Penetapan Penerima", "wajib": True},
            {"kode": "PKS", "nama": "Perjanjian Kerja Sama (PKS)", "wajib": True},
            {"kode": "PERMOHONAN", "nama": "Permohonan Pencairan", "wajib": True},
            {"kode": "KUITANSI", "nama": "Kuitansi Penerimaan", "wajib": True},
            {"kode": "LAPORAN_KEMAJUAN", "nama": "Laporan Kemajuan", "wajib": True},
            {"kode": "BAST", "nama": "BAST", "wajib": True},
            {"kode": "FOTO_GEOTAG", "nama": "Foto Geotagging", "wajib": True},
        ]
    },
}

# ============================================================================
# COMBINED - ALL CATEGORIES
# ============================================================================

ALL_CHECKLIST_CATEGORIES = {
    "HONORARIUM": {
        "nama": "A. Honorarium",
        "icon": "users",
        "color": "#3498db",
        "items": HONORARIUM_CHECKLIST,
    },
    "PERJALANAN_DINAS": {
        "nama": "B. Perjalanan Dinas",
        "icon": "plane",
        "color": "#27ae60",
        "items": PERJALANAN_DINAS_CHECKLIST,
    },
    "LEMBUR": {
        "nama": "C. Lembur",
        "icon": "clock",
        "color": "#9b59b6",
        "items": LEMBUR_CHECKLIST,
    },
    "SEWA_KONSUMSI": {
        "nama": "D. Sewa & Konsumsi",
        "icon": "home",
        "color": "#f39c12",
        "items": SEWA_KONSUMSI_CHECKLIST,
    },
    "PENGADAAN": {
        "nama": "E. Pengadaan Barang/Jasa",
        "icon": "shopping-cart",
        "color": "#e74c3c",
        "items": PENGADAAN_CHECKLIST,
    },
    "OPERASIONAL": {
        "nama": "F. Operasional & Pemeliharaan",
        "icon": "tool",
        "color": "#1abc9c",
        "items": OPERASIONAL_CHECKLIST,
    },
    "BANTUAN_PEMERINTAH": {
        "nama": "G. Bantuan Pemerintah",
        "icon": "gift",
        "color": "#e67e22",
        "items": BANTUAN_PEMERINTAH_CHECKLIST,
    },
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_categories() -> Dict[str, Any]:
    """Get all checklist categories."""
    return ALL_CHECKLIST_CATEGORIES


def get_category(category_code: str) -> Dict[str, Any]:
    """Get a specific category by code."""
    return ALL_CHECKLIST_CATEGORIES.get(category_code, {})


def get_checklist_items(category_code: str, jenis_code: str) -> List[Dict[str, Any]]:
    """
    Get checklist items for a specific category and type.

    Args:
        category_code: Category code (e.g., 'HONORARIUM', 'PERJALANAN_DINAS')
        jenis_code: Type code within the category (e.g., 'NARASUMBER', 'DALAM_NEGERI')

    Returns:
        List of document items for the checklist
    """
    category = ALL_CHECKLIST_CATEGORIES.get(category_code, {})
    items = category.get("items", {})
    jenis = items.get(jenis_code, {})
    return jenis.get("dokumen", [])


def get_jenis_options(category_code: str) -> List[Dict[str, str]]:
    """
    Get list of jenis options for a category.

    Returns:
        List of {kode, nama} for each jenis
    """
    category = ALL_CHECKLIST_CATEGORIES.get(category_code, {})
    items = category.get("items", {})
    return [{"kode": k, "nama": v.get("nama", k)} for k, v in items.items()]


def get_flat_checklist_options() -> List[Dict[str, str]]:
    """
    Get flat list of all checklist options for dropdown.

    Returns:
        List of {category, jenis, nama} for all options
    """
    options = []
    for cat_code, cat_data in ALL_CHECKLIST_CATEGORIES.items():
        cat_nama = cat_data.get("nama", cat_code)
        for jenis_code, jenis_data in cat_data.get("items", {}).items():
            jenis_nama = jenis_data.get("nama", jenis_code)
            options.append({
                "category": cat_code,
                "jenis": jenis_code,
                "nama": f"{cat_nama} - {jenis_nama}",
                "full_code": f"{cat_code}_{jenis_code}",
            })
    return options


# CATATAN PENTING untuk ditampilkan di UI
CATATAN_PENTING = [
    "Foto geotagging wajib di hampir semua kegiatan",
    "SSP diperlukan untuk semua pembayaran yang kena pajak",
    "Tatap muka: tanda tangan basah; Online: tanda tangan digital + tangkapan layar",
    "Mekanisme pembayaran menentukan bukti bayar (UP tunai, LS-BP, atau LS banyak penerima)",
]
