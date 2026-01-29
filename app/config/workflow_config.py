"""
PPK DOCUMENT FACTORY - Workflow Configuration V2
=================================================
Konfigurasi workflow yang disederhanakan dan terintegrasi dengan master data.

Mekanisme Pencairan Dana:
1. UP (Uang Persediaan) - Maksimal Rp 50.000.000
2. TUP (Tambahan Uang Persediaan) - Jika UP tidak cukup, wajib selesai 1 bulan
3. LS (Langsung) - Pembayaran langsung ke penyedia via KPPN
"""

from typing import Dict, List, Any, Optional

# ============================================================================
# JENIS KEGIATAN CONFIGURATION
# ============================================================================

# UP - Jenis Kegiatan yang didukung
UP_JENIS_KEGIATAN = {
    "OPERASIONAL": {
        "label": "Belanja Operasional Kantor",
        "deskripsi": "Belanja rutin operasional < Rp 1 juta",
        "icon": "shopping-cart",
        "max_nilai": 1_000_000,
    },
    "KEPANITIAAN": {
        "label": "Kegiatan Kepanitiaan",
        "deskripsi": "Kegiatan dengan SK Panitia",
        "icon": "users",
        "perlu_sk": True,
    },
    "JAMUAN_TAMU": {
        "label": "Jamuan Tamu",
        "deskripsi": "Jamuan/konsumsi penerimaan tamu",
        "icon": "coffee",
        "perlu_sk": True,
    },
    "RAPAT": {
        "label": "Rapat/Pertemuan/Workshop",
        "deskripsi": "Kegiatan rapat atau pertemuan",
        "icon": "message-square",
        "perlu_sk": True,
    },
    "PERJALANAN_DINAS": {
        "label": "Perjalanan Dinas Lokal",
        "deskripsi": "Perjalanan dinas dalam kota/lokal",
        "icon": "map-pin",
        "perlu_surat_tugas": True,
    },
    "LAINNYA": {
        "label": "Kegiatan Lainnya",
        "deskripsi": "Kegiatan lain yang tidak termasuk kategori di atas",
        "icon": "folder",
    },
}

# LS - Jenis Dasar yang didukung
LS_JENIS_DASAR = {
    "KONTRAK": {
        "label": "Kontrak/SPK (Pengadaan Barang/Jasa)",
        "deskripsi": "Pembayaran berdasarkan kontrak dengan penyedia",
        "icon": "file-text",
    },
    "PERJALANAN_DINAS": {
        "label": "Perjalanan Dinas",
        "deskripsi": "Pembayaran perjalanan dinas luar kota",
        "icon": "plane",
        "perlu_surat_tugas": True,
    },
}

# ============================================================================
# WORKFLOW UP (UANG PERSEDIAAN)
# ============================================================================

UP_WORKFLOW = {
    "kode": "UP",
    "nama": "Uang Persediaan",
    "deskripsi": "Pencairan dana untuk belanja operasional <= Rp 50 juta",
    "batas_maksimal": 50_000_000,
    "icon": "wallet",
    "color": "#27ae60",
    "color_light": "#d5f5e3",

    "jenis_kegiatan": UP_JENIS_KEGIATAN,

    "fase": {
        # ================================================================
        # FASE 1: INISIASI & DASAR HUKUM
        # ================================================================
        1: {
            "nama": "Inisiasi & Dasar Hukum",
            "deskripsi": "Persiapan awal dan kelengkapan dasar hukum",
            "icon": "file-text",
            "color": "#3498db",

            "dokumen": [
                # Checklist - WAJIB untuk semua
                {
                    "kode": "CHECKLIST",
                    "nama": "Checklist Kelengkapan Dokumen",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Upload checklist kelengkapan dokumen",
                    "untuk_semua": True,
                },
                # SK Upload - Opsional untuk semua
                {
                    "kode": "SK_UPLOAD",
                    "nama": "Upload SK (Opsional)",
                    "kategori": "opsional",
                    "template": None,
                    "deskripsi": "Upload scan SK jika diperlukan",
                    "untuk_semua": True,
                },
                # Lembar Permintaan - Untuk NON perjalanan dinas
                {
                    "kode": "LBR_REQ",
                    "nama": "Lembar Permintaan",
                    "kategori": "wajib",
                    "template": "lembar_permintaan.docx",
                    "deskripsi": "Lembar permintaan pencairan dana",
                    "jenis_kegiatan": ["OPERASIONAL", "KEPANITIAAN", "JAMUAN_TAMU", "RAPAT", "LAINNYA"],
                },
                # Surat Tugas - Untuk perjalanan dinas
                {
                    "kode": "SURAT_TUGAS",
                    "nama": "Upload Surat Tugas",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Upload scan Surat Tugas perjalanan dinas",
                    "jenis_kegiatan": ["PERJALANAN_DINAS"],
                },
                # TOR/KAK - Untuk kepanitiaan
                {
                    "kode": "TOR",
                    "nama": "TOR/KAK",
                    "kategori": "wajib",
                    "template": "kak.docx",
                    "deskripsi": "Terms of Reference / Kerangka Acuan Kerja",
                    "jenis_kegiatan": ["KEPANITIAAN"],
                },
                # RAB - Untuk kepanitiaan dan rapat (opsional untuk rapat)
                {
                    "kode": "RAB",
                    "nama": "Rencana Anggaran Biaya",
                    "kategori": "wajib",
                    "template": "rab_swakelola.xlsx",
                    "deskripsi": "Rincian estimasi biaya kegiatan",
                    "jenis_kegiatan": ["KEPANITIAAN"],
                },
                {
                    "kode": "RAB",
                    "nama": "Rencana Anggaran Biaya",
                    "kategori": "opsional",
                    "template": "rab_swakelola.xlsx",
                    "deskripsi": "Rincian estimasi biaya rapat (jika diperlukan)",
                    "jenis_kegiatan": ["RAPAT"],
                },
                # Undangan - Untuk jamuan tamu dan rapat
                {
                    "kode": "UNDANGAN",
                    "nama": "Undangan",
                    "kategori": "wajib",
                    "template": "undangan_pl.docx",
                    "deskripsi": "Surat undangan",
                    "jenis_kegiatan": ["JAMUAN_TAMU", "RAPAT"],
                },
            ],

            "validasi": [
                {"field": "estimasi_biaya", "rule": "max:50000000", "message": "Estimasi biaya UP maksimal Rp 50 juta"},
            ],
            "next_condition": "Semua dokumen wajib sudah dibuat"
        },

        # ================================================================
        # FASE 2: PENCAIRAN UANG MUKA
        # ================================================================
        2: {
            "nama": "Pencairan Uang Muka",
            "deskripsi": "Pengajuan dan pencairan uang muka dari UP",
            "icon": "dollar-sign",
            "color": "#f39c12",

            "dokumen": [
                {
                    "kode": "KUIT_UM",
                    "nama": "Kuitansi Uang Muka",
                    "kategori": "wajib",
                    "template": "kuitansi_uang_muka.docx",
                    "deskripsi": "Kuitansi penerimaan uang muka",
                    "untuk_semua": True,
                },
            ],

            "validasi": [
                {"field": "uang_muka", "rule": "required", "message": "Jumlah uang muka wajib diisi"},
                {"field": "penerima_id", "rule": "required", "message": "Penerima wajib dipilih"},
            ],
            "next_condition": "Uang muka sudah dicairkan dan diterima"
        },

        # ================================================================
        # FASE 3: PELAKSANAAN KEGIATAN
        # ================================================================
        3: {
            "nama": "Pelaksanaan Kegiatan",
            "deskripsi": "Kegiatan dilaksanakan dan bukti dikumpulkan",
            "icon": "activity",
            "color": "#9b59b6",

            "dokumen": [
                # Dokumentasi foto - WAJIB untuk semua
                {
                    "kode": "DOK_FOTO",
                    "nama": "Dokumentasi Foto (Tagging)",
                    "kategori": "wajib",
                    "template": None,
                    "deskripsi": "Foto dokumentasi pelaksanaan dengan tagging lokasi/waktu",
                    "untuk_semua": True,
                },
                # Nota/Faktur - Upload untuk semua
                {
                    "kode": "NOTA_BLJ",
                    "nama": "Nota/Faktur Belanja",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Nota pembelian dari toko/penyedia",
                    "untuk_semua": True,
                },
                # Kwitansi Toko - Upload untuk semua
                {
                    "kode": "KWIT_TOKO",
                    "nama": "Kwitansi Toko",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Kwitansi pembayaran dari toko",
                    "untuk_semua": True,
                },
                # Daftar Hadir - Wajib untuk rapat, jamuan, kepanitiaan
                {
                    "kode": "DH",
                    "nama": "Daftar Hadir",
                    "kategori": "wajib",
                    "template": "daftar_hadir_swakelola.docx",
                    "deskripsi": "Daftar hadir peserta",
                    "jenis_kegiatan": ["RAPAT", "JAMUAN_TAMU", "KEPANITIAAN"],
                },
                # Notulensi - Wajib untuk rapat dan jamuan
                {
                    "kode": "NOTULEN",
                    "nama": "Notulensi Rapat",
                    "kategori": "wajib",
                    "template": "notulen.docx",
                    "deskripsi": "Notulen/catatan hasil rapat",
                    "jenis_kegiatan": ["RAPAT", "JAMUAN_TAMU"],
                },
                # Laporan Kegiatan - Wajib untuk kepanitiaan
                {
                    "kode": "LAP_KEG",
                    "nama": "Laporan Kegiatan",
                    "kategori": "wajib",
                    "template": "laporan_kegiatan.docx",
                    "deskripsi": "Laporan pelaksanaan kegiatan kepanitiaan",
                    "jenis_kegiatan": ["KEPANITIAAN"],
                },
                # Laporan Perjalanan - Wajib untuk perjalanan dinas
                {
                    "kode": "LAP_PJD",
                    "nama": "Laporan Perjalanan Dinas",
                    "kategori": "wajib",
                    "template": "laporan_perjalanan_dinas.docx",
                    "deskripsi": "Laporan hasil perjalanan dinas",
                    "jenis_kegiatan": ["PERJALANAN_DINAS"],
                },
            ],

            "validasi": [
                {"field": "dokumen_foto", "rule": "required", "message": "Dokumentasi foto wajib ada"},
            ],
            "next_condition": "Kegiatan selesai dan semua bukti terkumpul"
        },

        # ================================================================
        # FASE 4: PERTANGGUNGJAWABAN
        # ================================================================
        4: {
            "nama": "Pertanggungjawaban",
            "deskripsi": "Membuat dokumen pertanggungjawaban dan perhitungan tambah/kurang",
            "icon": "calculator",
            "color": "#e74c3c",

            "dokumen": [
                {
                    "kode": "KUIT_RAMP",
                    "nama": "Kuitansi Rampung",
                    "kategori": "wajib",
                    "template": "kuitansi_rampung.docx",
                    "deskripsi": "Kuitansi penyelesaian/rampung kegiatan",
                    "untuk_semua": True,
                },
                {
                    "kode": "HITUNG_TK",
                    "nama": "Perhitungan Tambah/Kurang",
                    "kategori": "wajib",
                    "template": "perhitungan_tambah_kurang.xlsx",
                    "deskripsi": "Perhitungan selisih uang muka vs realisasi",
                    "untuk_semua": True,
                },
                {
                    "kode": "REKAP_BKT",
                    "nama": "Rekap Bukti Pengeluaran",
                    "kategori": "wajib",
                    "template": "rekap_bukti_pengeluaran.xlsx",
                    "deskripsi": "Rekap seluruh bukti pengeluaran",
                    "untuk_semua": True,
                },
                {
                    "kode": "LPJ",
                    "nama": "LPJ Kegiatan",
                    "kategori": "opsional",
                    "template": "lpj.docx",
                    "deskripsi": "Laporan Pertanggungjawaban kegiatan",
                    "jenis_kegiatan": ["KEPANITIAAN", "RAPAT"],
                },
            ],

            "kalkulasi": {
                "formula": "selisih = realisasi - uang_muka",
                "hasil_positif": {
                    "label": "KURANG BAYAR",
                    "aksi": "Ajukan pembayaran tambahan",
                    "color": "#e74c3c",
                },
                "hasil_negatif": {
                    "label": "LEBIH BAYAR",
                    "aksi": "Kembalikan kelebihan ke kas",
                    "color": "#f39c12",
                },
                "hasil_nol": {
                    "label": "PAS / NIHIL",
                    "aksi": "Lanjut ke rekap",
                    "color": "#27ae60",
                },
            },

            "validasi": [
                {"field": "realisasi", "rule": "required", "message": "Total realisasi wajib diisi"},
            ],
            "next_condition": "Perhitungan selesai dan dokumen pertanggungjawaban lengkap"
        },

        # ================================================================
        # FASE 5: REKAP & ARSIP
        # ================================================================
        5: {
            "nama": "Rekap & Arsip",
            "deskripsi": "Rekap final dan arsip dokumen (SPBY diinput via SAKTI)",
            "icon": "check-circle",
            "color": "#27ae60",

            "dokumen": [
                {
                    "kode": "REKAP_FINAL",
                    "nama": "Rekap Final Transaksi",
                    "kategori": "wajib",
                    "template": "rekap_final.xlsx",
                    "deskripsi": "Rekap akhir seluruh transaksi",
                    "untuk_semua": True,
                },
            ],

            "aksi_tambahan": [
                "Input SPBY di SAKTI",
                "Arsip ke folder tahun berjalan",
                "Update sisa UP tersedia",
            ],

            "catatan": "SPBY diinput langsung di aplikasi SAKTI, bukan di aplikasi ini",
            "next_condition": "Transaksi selesai dan semua dokumen diarsipkan"
        }
    }
}

# ============================================================================
# WORKFLOW TUP (TAMBAHAN UANG PERSEDIAAN)
# ============================================================================

TUP_WORKFLOW = {
    "kode": "TUP",
    "nama": "Tambahan Uang Persediaan",
    "deskripsi": "Tambahan UP jika kebutuhan melebihi sisa UP, wajib selesai 1 bulan",
    "batas_hari": 30,
    "icon": "plus-circle",
    "color": "#f39c12",
    "color_light": "#fef5e7",

    "fase": {
        1: {
            "nama": "Pengajuan TUP",
            "deskripsi": "Mengajukan kebutuhan TUP ke KPPN",
            "icon": "file-plus",
            "color": "#3498db",
            "dokumen": [
                {
                    "kode": "SP_TUP",
                    "nama": "Surat Permohonan TUP",
                    "kategori": "wajib",
                    "template": "surat_permohonan_tup.docx",
                    "deskripsi": "Surat pengajuan TUP ke KPPN"
                },
                {
                    "kode": "RINCI_TUP",
                    "nama": "Rincian Penggunaan TUP",
                    "kategori": "wajib",
                    "template": "rincian_tup.xlsx",
                    "deskripsi": "Rincian rencana penggunaan TUP"
                },
                {
                    "kode": "REK_KORAN",
                    "nama": "Rekening Koran/Saldo UP",
                    "kategori": "wajib",
                    "template": None,
                    "deskripsi": "Bukti saldo UP saat ini tidak mencukupi"
                },
            ],
            "next_condition": "Surat permohonan diajukan ke KPPN"
        },

        2: {
            "nama": "Persetujuan KPPN",
            "deskripsi": "Menunggu persetujuan TUP dari Kepala KPPN",
            "icon": "clock",
            "color": "#f39c12",
            "dokumen": [
                {
                    "kode": "APPR_TUP",
                    "nama": "Surat Persetujuan TUP dari KPPN",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Surat persetujuan dari Kepala KPPN"
                },
            ],
            "next_condition": "TUP disetujui oleh Kepala KPPN"
        },

        3: {
            "nama": "Pencairan TUP",
            "deskripsi": "Dana TUP dicairkan ke rekening bendahara",
            "icon": "credit-card",
            "color": "#9b59b6",
            "dokumen": [
                {
                    "kode": "SP2D_TUP",
                    "nama": "SP2D TUP",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Surat Perintah Pencairan Dana TUP"
                },
                {
                    "kode": "KUIT_UM_TUP",
                    "nama": "Kuitansi Uang Muka TUP",
                    "kategori": "wajib",
                    "template": "kuitansi_uang_muka.docx",
                    "deskripsi": "Kuitansi penerimaan uang muka TUP"
                },
            ],
            "catatan": "Catat tanggal SP2D untuk menghitung batas 1 bulan",
            "next_condition": "Dana TUP sudah masuk ke rekening bendahara"
        },

        4: {
            "nama": "Penggunaan TUP",
            "deskripsi": "Menggunakan TUP sesuai rincian yang diajukan",
            "icon": "shopping-bag",
            "color": "#e74c3c",
            "dokumen": [
                {
                    "kode": "DH",
                    "nama": "Daftar Hadir",
                    "kategori": "wajib",
                    "template": "daftar_hadir_swakelola.docx",
                    "deskripsi": "Daftar hadir peserta kegiatan"
                },
                {
                    "kode": "DOK_FOTO",
                    "nama": "Dokumentasi Foto",
                    "kategori": "wajib",
                    "template": None,
                    "deskripsi": "Foto dokumentasi pelaksanaan"
                },
                {
                    "kode": "NOTA_BLJ",
                    "nama": "Nota/Faktur Belanja",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Bukti pembelian"
                },
            ],
            "catatan": "WAJIB selesai dalam 1 BULAN sejak SP2D diterbitkan",
            "countdown": True,
            "next_condition": "Semua dana TUP sudah digunakan atau batas waktu tercapai"
        },

        5: {
            "nama": "Pertanggungjawaban TUP",
            "deskripsi": "Mempertanggungjawabkan penggunaan TUP, sisa dikembalikan",
            "icon": "check-circle",
            "color": "#27ae60",
            "dokumen": [
                {
                    "kode": "KUIT_RAMP_TUP",
                    "nama": "Kuitansi Rampung TUP",
                    "kategori": "wajib",
                    "template": "kuitansi_rampung.docx",
                    "deskripsi": "Kuitansi penyelesaian/rampung TUP"
                },
                {
                    "kode": "HITUNG_TK_TUP",
                    "nama": "Perhitungan Tambah/Kurang TUP",
                    "kategori": "wajib",
                    "template": "perhitungan_tambah_kurang.xlsx",
                    "deskripsi": "Perhitungan selisih uang muka vs realisasi TUP"
                },
                {
                    "kode": "REKAP_TUP",
                    "nama": "Rekap Penggunaan TUP",
                    "kategori": "wajib",
                    "template": "rekap_tup.xlsx",
                    "deskripsi": "Rekap seluruh penggunaan TUP"
                },
                {
                    "kode": "SSBP",
                    "nama": "SSBP Pengembalian (jika ada sisa)",
                    "kategori": "kondisional",
                    "template": "ssbp.xlsx",
                    "deskripsi": "Surat Setoran Bukan Pajak untuk pengembalian"
                },
            ],
            "catatan": "SPBY diinput di SAKTI. Sisa TUP wajib dikembalikan ke kas negara.",
            "next_condition": "TUP nihil atau sisa sudah dikembalikan ke kas negara"
        }
    }
}

# ============================================================================
# WORKFLOW LS (LANGSUNG)
# ============================================================================

LS_WORKFLOW = {
    "kode": "LS",
    "nama": "Pembayaran Langsung",
    "deskripsi": "Pembayaran langsung ke penyedia via KPPN",
    "icon": "send",
    "color": "#3498db",
    "color_light": "#ebf5fb",

    "jenis_dasar": LS_JENIS_DASAR,

    "fase": {
        # ================================================================
        # FASE 1: DASAR HUKUM
        # ================================================================
        1: {
            "nama": "Dasar Hukum",
            "deskripsi": "Pembuatan dasar hukum (Kontrak/SPK atau Surat Tugas)",
            "icon": "file-signature",
            "color": "#3498db",

            "dokumen": [
                # Checklist - Wajib untuk semua
                {
                    "kode": "CHECKLIST",
                    "nama": "Checklist Kelengkapan Dokumen",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Upload checklist kelengkapan dokumen pencairan LS",
                    "untuk_semua": True,
                },

                # === DOKUMEN KONTRAK ===
                {
                    "kode": "LBR_REQ",
                    "nama": "Lembar Permintaan",
                    "kategori": "wajib",
                    "template": "lembar_permintaan.docx",
                    "deskripsi": "Lembar permintaan pencairan dana",
                    "jenis_dasar": "KONTRAK",
                },
                {
                    "kode": "SPK",
                    "nama": "Surat Perjanjian Kerja",
                    "kategori": "wajib",
                    "template": "spk.docx",
                    "deskripsi": "Kontrak kerja dengan penyedia",
                    "jenis_dasar": "KONTRAK",
                },
                {
                    "kode": "SSUK",
                    "nama": "Syarat-Syarat Umum Kontrak",
                    "kategori": "wajib",
                    "template": "ssuk.docx",
                    "deskripsi": "Syarat umum kontrak",
                    "jenis_dasar": "KONTRAK",
                },
                {
                    "kode": "SSKK",
                    "nama": "Syarat-Syarat Khusus Kontrak",
                    "kategori": "wajib",
                    "template": "sskk.docx",
                    "deskripsi": "Syarat khusus kontrak",
                    "jenis_dasar": "KONTRAK",
                },
                {
                    "kode": "SPMK",
                    "nama": "Surat Perintah Mulai Kerja",
                    "kategori": "wajib",
                    "template": "spmk.docx",
                    "deskripsi": "Perintah untuk memulai pekerjaan",
                    "jenis_dasar": "KONTRAK",
                },
                {
                    "kode": "JAM_PELAKS",
                    "nama": "Jaminan Pelaksanaan",
                    "kategori": "kondisional",
                    "template": None,
                    "deskripsi": "Jaminan pelaksanaan dari bank/asuransi (nilai > 200jt)",
                    "jenis_dasar": "KONTRAK",
                },

                # === DOKUMEN PERJALANAN DINAS ===
                {
                    "kode": "SURAT_TUGAS",
                    "nama": "Upload Surat Tugas",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Upload scan Surat Tugas perjalanan dinas",
                    "jenis_dasar": "PERJALANAN_DINAS",
                },
                {
                    "kode": "SPD",
                    "nama": "Surat Perjalanan Dinas",
                    "kategori": "wajib",
                    "template": "sppd.docx",
                    "deskripsi": "Surat Perjalanan Dinas (SPPD)",
                    "jenis_dasar": "PERJALANAN_DINAS",
                },
                {
                    "kode": "RAB_SPPD",
                    "nama": "Rincian Biaya Perjalanan",
                    "kategori": "wajib",
                    "template": "rab_sppd.xlsx",
                    "deskripsi": "Rincian anggaran biaya perjalanan dinas",
                    "jenis_dasar": "PERJALANAN_DINAS",
                },
            ],

            "validasi_kontrak": [
                {"field": "nomor_kontrak", "rule": "required", "message": "Nomor kontrak/SPK wajib diisi"},
                {"field": "nilai_kontrak", "rule": "required", "message": "Nilai kontrak wajib diisi"},
                {"field": "penyedia_id", "rule": "required", "message": "Penyedia wajib dipilih"},
            ],
            "validasi_perjalanan_dinas": [
                {"field": "nomor_st", "rule": "required", "message": "Nomor Surat Tugas wajib diisi"},
                {"field": "tujuan", "rule": "required", "message": "Tujuan perjalanan wajib diisi"},
            ],
            "next_condition": "Dasar hukum sudah ditandatangani"
        },

        # ================================================================
        # FASE 2: PELAKSANAAN
        # ================================================================
        2: {
            "nama": "Pelaksanaan",
            "deskripsi": "Pelaksanaan pekerjaan/kegiatan sesuai dasar hukum",
            "icon": "hard-hat",
            "color": "#f39c12",

            "dokumen": [
                # === DOKUMEN KONTRAK ===
                {
                    "kode": "LAP_PROG",
                    "nama": "Laporan Progress Pekerjaan",
                    "kategori": "wajib",
                    "template": "laporan_kemajuan.docx",
                    "deskripsi": "Laporan kemajuan pekerjaan",
                    "jenis_dasar": "KONTRAK",
                },
                {
                    "kode": "BA_MC",
                    "nama": "BA Monthly Certificate (jika termin)",
                    "kategori": "kondisional",
                    "template": "ba_mc.docx",
                    "deskripsi": "Berita acara progress bulanan",
                    "jenis_dasar": "KONTRAK",
                },

                # === DOKUMEN PERJALANAN DINAS ===
                {
                    "kode": "DH_PJD",
                    "nama": "Daftar Hadir / Bukti Kehadiran",
                    "kategori": "wajib",
                    "template": "daftar_hadir_swakelola.docx",
                    "deskripsi": "Daftar hadir atau bukti kehadiran di lokasi tujuan",
                    "jenis_dasar": "PERJALANAN_DINAS",
                },
                {
                    "kode": "DOK_FOTO_PJD",
                    "nama": "Dokumentasi Foto Kegiatan",
                    "kategori": "wajib",
                    "template": None,
                    "deskripsi": "Foto dokumentasi pelaksanaan kegiatan perjalanan",
                    "jenis_dasar": "PERJALANAN_DINAS",
                },
                {
                    "kode": "TIKET",
                    "nama": "Tiket/Boarding Pass",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Tiket pesawat/kereta/kapal atau boarding pass",
                    "jenis_dasar": "PERJALANAN_DINAS",
                },
                {
                    "kode": "BUKTI_HOTEL",
                    "nama": "Bukti Penginapan/Hotel",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Bill/invoice dari hotel atau penginapan",
                    "jenis_dasar": "PERJALANAN_DINAS",
                },
            ],

            "next_condition": "Pekerjaan/kegiatan selesai dilaksanakan"
        },

        # ================================================================
        # FASE 3: SERAH TERIMA / LAPORAN
        # ================================================================
        3: {
            "nama": "Serah Terima / Laporan",
            "deskripsi": "Pemeriksaan dan serah terima hasil pekerjaan atau laporan kegiatan",
            "icon": "clipboard-check",
            "color": "#9b59b6",

            "dokumen": [
                # === DOKUMEN KONTRAK ===
                {
                    "kode": "BA_PMR",
                    "nama": "BA Pemeriksaan Pekerjaan",
                    "kategori": "wajib",
                    "template": "bahp.docx",
                    "deskripsi": "Berita acara pemeriksaan oleh PPHP",
                    "jenis_dasar": "KONTRAK",
                },
                {
                    "kode": "BAST",
                    "nama": "Berita Acara Serah Terima",
                    "kategori": "wajib",
                    "template": "bast.docx",
                    "deskripsi": "BAST hasil pekerjaan",
                    "jenis_dasar": "KONTRAK",
                },
                {
                    "kode": "BA_PHO",
                    "nama": "BA Provisional Hand Over (PHO)",
                    "kategori": "kondisional",
                    "template": "bast_konstruksi_pho.docx",
                    "deskripsi": "Serah terima sementara (untuk konstruksi)",
                    "jenis_dasar": "KONTRAK",
                },

                # === DOKUMEN PERJALANAN DINAS ===
                {
                    "kode": "LAP_PJD",
                    "nama": "Laporan Perjalanan Dinas",
                    "kategori": "wajib",
                    "template": "laporan_perjalanan_dinas.docx",
                    "deskripsi": "Laporan hasil perjalanan dinas",
                    "jenis_dasar": "PERJALANAN_DINAS",
                },
                {
                    "kode": "SPD_TTD",
                    "nama": "SPD yang Sudah Ditandatangani",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "SPD dengan tanda tangan pejabat di lokasi tujuan",
                    "jenis_dasar": "PERJALANAN_DINAS",
                },
            ],

            "next_condition": "Serah terima/laporan selesai"
        },

        # ================================================================
        # FASE 4: PENGAJUAN TAGIHAN SPM
        # ================================================================
        4: {
            "nama": "Pengajuan Tagihan SPM",
            "deskripsi": "Pemrosesan dokumen SPP/SPM untuk pembayaran",
            "icon": "file-invoice-dollar",
            "color": "#e74c3c",

            "dokumen": [
                # Dokumen umum untuk semua jenis
                {
                    "kode": "SPP_LS",
                    "nama": "Surat Permintaan Pembayaran",
                    "kategori": "wajib",
                    "template": "spp_ls.docx",
                    "deskripsi": "SPP untuk pengajuan ke PPSPM",
                    "untuk_semua": True,
                },
                {
                    "kode": "SPM_LS",
                    "nama": "Surat Perintah Membayar",
                    "kategori": "wajib",
                    "template": "spm_ls.docx",
                    "deskripsi": "SPM untuk dikirim ke KPPN",
                    "untuk_semua": True,
                },
                {
                    "kode": "KUIT_LS",
                    "nama": "Kuitansi Pembayaran LS",
                    "kategori": "wajib",
                    "template": "kuitansi.docx",
                    "deskripsi": "Kuitansi pembayaran LS",
                    "untuk_semua": True,
                },

                # === DOKUMEN KONTRAK ===
                {
                    "kode": "INVOICE",
                    "nama": "Invoice/Tagihan dari Penyedia",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Tagihan resmi dari penyedia",
                    "jenis_dasar": "KONTRAK",
                },
                {
                    "kode": "FAKTUR_PJK",
                    "nama": "Faktur Pajak",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Faktur pajak dari PKP",
                    "jenis_dasar": "KONTRAK",
                },
                {
                    "kode": "SSP_PPN",
                    "nama": "SSP PPN",
                    "kategori": "wajib",
                    "template": "ssp.xlsx",
                    "deskripsi": "Surat Setoran Pajak PPN",
                    "jenis_dasar": "KONTRAK",
                },
                {
                    "kode": "SSP_PPH",
                    "nama": "SSP PPh",
                    "kategori": "wajib",
                    "template": "ssp.xlsx",
                    "deskripsi": "Surat Setoran Pajak PPh",
                    "jenis_dasar": "KONTRAK",
                },

                # === DOKUMEN PERJALANAN DINAS ===
                {
                    "kode": "RINCIAN_BIAYA",
                    "nama": "Rincian Biaya Perjalanan",
                    "kategori": "wajib",
                    "template": "rincian_biaya_pd.docx",
                    "deskripsi": "Rincian biaya perjalanan dinas yang direalisasi",
                    "jenis_dasar": "PERJALANAN_DINAS",
                },
                {
                    "kode": "BUKTI_BAYAR_PJD",
                    "nama": "Bukti-bukti Pembayaran",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Bukti pembayaran (tiket, hotel, transport lokal)",
                    "jenis_dasar": "PERJALANAN_DINAS",
                },
            ],

            "next_condition": "SPM diajukan ke KPPN"
        },

        # ================================================================
        # FASE 5: SP2D & PENYELESAIAN
        # ================================================================
        5: {
            "nama": "SP2D & Penyelesaian",
            "deskripsi": "KPPN menerbitkan SP2D, dana masuk ke rekening penerima",
            "icon": "check-circle",
            "color": "#27ae60",

            "dokumen": [
                {
                    "kode": "SP2D_LS",
                    "nama": "Surat Perintah Pencairan Dana",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "SP2D dari KPPN",
                    "untuk_semua": True,
                },
                {
                    "kode": "BUKTI_TRF",
                    "nama": "Bukti Transfer ke Penerima",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Bukti transfer pembayaran",
                    "untuk_semua": True,
                },
            ],

            "aksi_tambahan": [
                "Verifikasi dana sudah diterima",
                "Update status menjadi SELESAI",
                "Arsip seluruh dokumen",
                "Update realisasi anggaran di DIPA",
            ],

            "next_condition": "Transaksi selesai dan pembayaran diterima"
        }
    }
}

# ============================================================================
# EXPORT & HELPER FUNCTIONS
# ============================================================================

ALL_WORKFLOWS = {
    "UP": UP_WORKFLOW,
    "TUP": TUP_WORKFLOW,
    "LS": LS_WORKFLOW,
}

# Alias for backwards compatibility
WORKFLOW_CONFIGS = ALL_WORKFLOWS


def get_workflow(mekanisme: str) -> Optional[Dict[str, Any]]:
    """Get konfigurasi workflow berdasarkan mekanisme."""
    return ALL_WORKFLOWS.get(mekanisme.upper())


def get_fase_config(mekanisme: str, fase: int) -> Optional[Dict[str, Any]]:
    """Get konfigurasi fase tertentu."""
    workflow = get_workflow(mekanisme)
    if workflow and fase in workflow.get("fase", {}):
        return workflow["fase"][fase]
    return None


def get_dokumen_list(mekanisme: str, fase: int, jenis_kegiatan: str = None, jenis_dasar: str = None) -> List[Dict[str, Any]]:
    """
    Get daftar dokumen untuk fase tertentu, difilter berdasarkan jenis kegiatan/dasar.

    Args:
        mekanisme: UP, TUP, atau LS
        fase: Nomor fase (1-5)
        jenis_kegiatan: Untuk UP (OPERASIONAL, KEPANITIAAN, dll)
        jenis_dasar: Untuk LS (KONTRAK atau PERJALANAN_DINAS)

    Returns:
        List dokumen yang sesuai
    """
    fase_config = get_fase_config(mekanisme, fase)
    if not fase_config:
        return []

    all_docs = fase_config.get("dokumen", [])
    filtered_docs = []

    for doc in all_docs:
        # Dokumen untuk semua jenis
        if doc.get("untuk_semua"):
            filtered_docs.append(doc)
            continue

        # Filter berdasarkan jenis_kegiatan (untuk UP)
        if jenis_kegiatan and "jenis_kegiatan" in doc:
            if jenis_kegiatan in doc["jenis_kegiatan"]:
                filtered_docs.append(doc)
            continue

        # Filter berdasarkan jenis_dasar (untuk LS)
        if jenis_dasar and "jenis_dasar" in doc:
            if doc["jenis_dasar"] == jenis_dasar:
                filtered_docs.append(doc)
            continue

        # Dokumen tanpa filter khusus (untuk TUP atau dokumen umum)
        if "jenis_kegiatan" not in doc and "jenis_dasar" not in doc:
            filtered_docs.append(doc)

    return filtered_docs


def get_all_dokumen(mekanisme: str, jenis_kegiatan: str = None, jenis_dasar: str = None) -> List[Dict[str, Any]]:
    """
    Get semua dokumen untuk mekanisme tertentu.

    Returns:
        List semua dokumen dengan informasi fase
    """
    workflow = get_workflow(mekanisme)
    if not workflow:
        return []

    dokumen_list = []
    for fase_num in workflow.get("fase", {}).keys():
        docs = get_dokumen_list(mekanisme, fase_num, jenis_kegiatan, jenis_dasar)
        for dok in docs:
            dok_copy = dok.copy()
            dok_copy["fase"] = fase_num
            dok_copy["fase_nama"] = workflow["fase"][fase_num].get("nama", "")
            dokumen_list.append(dok_copy)

    return dokumen_list


def get_jenis_kegiatan_options(mekanisme: str) -> Dict[str, Dict]:
    """Get opsi jenis kegiatan untuk mekanisme tertentu."""
    workflow = get_workflow(mekanisme)
    if not workflow:
        return {}

    if mekanisme == "UP":
        return workflow.get("jenis_kegiatan", {})
    elif mekanisme == "LS":
        return workflow.get("jenis_dasar", {})
    return {}


def get_validasi_rules(mekanisme: str, fase: int, jenis: str = None) -> List[Dict[str, str]]:
    """
    Get aturan validasi untuk fase tertentu.

    Args:
        mekanisme: UP, TUP, atau LS
        fase: Nomor fase
        jenis: Jenis kegiatan/dasar untuk validasi spesifik
    """
    fase_config = get_fase_config(mekanisme, fase)
    if not fase_config:
        return []

    # Validasi umum
    rules = fase_config.get("validasi", [])

    # Validasi spesifik per jenis
    if jenis:
        jenis_key = f"validasi_{jenis.lower()}"
        rules.extend(fase_config.get(jenis_key, []))

    return rules


def get_workflow_summary(mekanisme: str) -> Dict[str, Any]:
    """Get ringkasan workflow untuk display."""
    workflow = get_workflow(mekanisme)
    if not workflow:
        return {}

    fase_summary = []
    for fase_num, fase_config in workflow.get("fase", {}).items():
        fase_summary.append({
            "nomor": fase_num,
            "nama": fase_config.get("nama", ""),
            "icon": fase_config.get("icon", ""),
            "color": fase_config.get("color", "#666"),
            "jumlah_dokumen": len(fase_config.get("dokumen", [])),
        })

    return {
        "kode": workflow.get("kode"),
        "nama": workflow.get("nama"),
        "deskripsi": workflow.get("deskripsi"),
        "icon": workflow.get("icon"),
        "color": workflow.get("color"),
        "jumlah_fase": len(workflow.get("fase", {})),
        "fase": fase_summary,
    }


# Nama fase untuk display
NAMA_FASE = {
    "UP": {
        1: "Inisiasi & Dasar",
        2: "Pencairan UM",
        3: "Pelaksanaan",
        4: "Pertanggungjawaban",
        5: "Rekap & Arsip"
    },
    "TUP": {
        1: "Pengajuan TUP",
        2: "Persetujuan",
        3: "Pencairan",
        4: "Penggunaan",
        5: "Pertanggungjawaban"
    },
    "LS": {
        1: "Dasar Hukum",
        2: "Pelaksanaan",
        3: "Serah Terima",
        4: "Tagihan SPM",
        5: "SP2D & Selesai"
    }
}


def get_nama_fase(mekanisme: str, fase: int) -> str:
    """Get nama singkat fase untuk display."""
    return NAMA_FASE.get(mekanisme, {}).get(fase, f"Fase {fase}")
