"""
PPK DOCUMENT FACTORY - Workflow Configuration
==============================================
Konfigurasi workflow untuk setiap mekanisme pencairan.
Mendefinisikan fase, dokumen wajib/opsional, dan validasi per fase.

Mekanisme Pencairan Dana:
1. UP (Uang Persediaan) - Maksimal Rp 50.000.000
2. TUP (Tambahan Uang Persediaan) - Jika UP tidak cukup, wajib selesai 1 bulan
3. LS (Langsung) - Pembayaran langsung ke penyedia via KPPN
"""

from typing import Dict, List, Any, Optional

# ============================================================================
# WORKFLOW UP (UANG PERSEDIAAN)
# ============================================================================

UP_WORKFLOW = {
    "kode": "UP",
    "nama": "Uang Persediaan",
    "deskripsi": "Pencairan dana untuk belanja operasional <= Rp 50 juta",
    "batas_maksimal": 50_000_000,
    "icon": "wallet",
    "color": "#27ae60",  # Green
    "color_light": "#d5f5e3",

    # UP mendukung beberapa jenis kegiatan dengan kebutuhan dokumen berbeda
    "jenis_kegiatan_options": [
        "OPERASIONAL",      # Belanja operasional kantor (< 1jt, cukup lembar permintaan)
        "KEPANITIAAN",      # Kegiatan kepanitiaan (perlu TOR, RAB, SK)
        "JAMUAN_TAMU",      # Jamuan tamu (perlu Undangan, SK)
        "RAPAT",            # Rapat/pertemuan (perlu Undangan, SK)
        "PERJALANAN_DINAS", # Perjalanan dinas (perlu Surat Tugas)
        "PERJALANAN_LOKAL", # Perjalanan lokal (perlu ST)
        "LAINNYA",          # Kegiatan lainnya
    ],
    "jenis_kegiatan_labels": {
        "OPERASIONAL": "Belanja Operasional Kantor (< Rp 1 juta)",
        "KEPANITIAAN": "Kegiatan Kepanitiaan",
        "JAMUAN_TAMU": "Jamuan Tamu",
        "RAPAT": "Rapat/Pertemuan/Workshop",
        "PERJALANAN_DINAS": "Perjalanan Dinas",
        "PERJALANAN_LOKAL": "Perjalanan Lokal",
        "LAINNYA": "Kegiatan Lainnya",
    },

    # Jenis Pertanggungjawaban untuk checklist dokumen
    # Lihat app/config/checklist_config.py untuk detail dokumen per jenis
    "jenis_pertanggungjawaban_categories": [
        "HONORARIUM",           # Berbagai jenis honorarium
        "PERJALANAN_DINAS",     # Dalam negeri, luar negeri, transport lokal
        "LEMBUR",               # Uang lembur
        "SEWA_KONSUMSI",        # Sewa kendaraan, gedung, konsumsi
        "PENGADAAN",            # Barang, konstruksi, jasa konsultan
        "OPERASIONAL",          # Langganan, BBM, pemeliharaan
        "BANTUAN_PEMERINTAH",   # Bantuan bentuk barang/uang
    ],

    "fase": {
        1: {
            "nama": "Inisiasi & SK",
            "deskripsi": "Persiapan awal dan penerbitan SK/Dasar Hukum",
            "icon": "file-text",
            "color": "#3498db",

            # Dokumen WAJIB untuk SEMUA jenis kegiatan
            "dokumen": [
                {
                    "kode": "LBR_REQ",
                    "nama": "Lembar Permintaan",
                    "kategori": "wajib",
                    "template": "lembar_permintaan.docx",
                    "deskripsi": "Lembar permintaan pencairan dana",
                    "exclude_jenis_kegiatan": ["PERJALANAN_DINAS"]
                },
                {
                    "kode": "CHECKLIST_PD",
                    "nama": "Checklist Kelengkapan Dokumen",
                    "kategori": "wajib",
                    "template": "checklist_perjalanan_dinas.docx",
                    "deskripsi": "Daftar checklist kelengkapan dokumen"
                },
            ],

            # Dokumen WAJIB untuk kegiatan yang memerlukan SK (KEPANITIAAN, JAMUAN_TAMU, RAPAT, LAINNYA)
            "dokumen_dengan_sk": [
                {
                    "kode": "ND_REQ",
                    "nama": "Nota Dinas Permintaan",
                    "kategori": "wajib",
                    "template": "nota_dinas_pp.docx",
                    "deskripsi": "Nota dinas permohonan uang muka kegiatan",
                    "jenis_kegiatan": ["KEPANITIAAN", "JAMUAN_TAMU", "RAPAT", "PERJALANAN_LOKAL", "LAINNYA"]
                },
                {
                    "kode": "SK_KPA",
                    "nama": "SK KPA / Surat Tugas",
                    "kategori": "wajib",
                    "template": "sk_kpa.docx",
                    "deskripsi": "Surat Keputusan atau Surat Tugas dari KPA",
                    "jenis_kegiatan": ["KEPANITIAAN", "JAMUAN_TAMU", "RAPAT", "PERJALANAN_LOKAL", "LAINNYA"]
                },
            ],

            # Dokumen khusus KEPANITIAAN
            "dokumen_kepanitiaan": [
                {
                    "kode": "TOR",
                    "nama": "TOR/KAK",
                    "kategori": "wajib",
                    "template": "kak.docx",
                    "deskripsi": "Terms of Reference / Kerangka Acuan Kerja",
                    "jenis_kegiatan": ["KEPANITIAAN"]
                },
                {
                    "kode": "RAB",
                    "nama": "Rencana Anggaran Biaya",
                    "kategori": "wajib",
                    "template": "rab_swakelola.xlsx",
                    "deskripsi": "Rincian estimasi biaya kegiatan",
                    "jenis_kegiatan": ["KEPANITIAAN"]
                },
            ],

            # Dokumen khusus JAMUAN_TAMU
            "dokumen_jamuan_tamu": [
                {
                    "kode": "UND",
                    "nama": "Undangan",
                    "kategori": "wajib",
                    "template": "undangan_pl.docx",
                    "deskripsi": "Surat undangan tamu",
                    "jenis_kegiatan": ["JAMUAN_TAMU"]
                },
            ],

            # Dokumen khusus RAPAT
            "dokumen_rapat": [
                {
                    "kode": "UND",
                    "nama": "Undangan Rapat",
                    "kategori": "wajib",
                    "template": "undangan_pl.docx",
                    "deskripsi": "Surat undangan untuk peserta rapat",
                    "jenis_kegiatan": ["RAPAT"]
                },
                {
                    "kode": "TOR",
                    "nama": "TOR/KAK",
                    "kategori": "opsional",
                    "template": "kak.docx",
                    "deskripsi": "Terms of Reference (jika diperlukan)",
                    "jenis_kegiatan": ["RAPAT"]
                },
                {
                    "kode": "RAB",
                    "nama": "Rencana Anggaran Biaya",
                    "kategori": "opsional",
                    "template": "rab_swakelola.xlsx",
                    "deskripsi": "Rincian estimasi biaya rapat",
                    "jenis_kegiatan": ["RAPAT"]
                },
            ],

            # Dokumen khusus PERJALANAN_DINAS
            "dokumen_perjalanan_dinas": [
                {
                    "kode": "ST",
                    "nama": "Surat Tugas",
                    "kategori": "wajib",
                    "is_arsip": True,
                    "deskripsi": "Upload Surat Tugas dari pejabat berwenang",
                    "jenis_kegiatan": ["PERJALANAN_DINAS"]
                },
                {
                    "kode": "SPPD",
                    "nama": "SPPD (Surat Perintah Perjalanan Dinas)",
                    "kategori": "wajib",
                    "template": "sppd.docx",
                    "deskripsi": "Draft SPPD untuk perjalanan dinas",
                    "jenis_kegiatan": ["PERJALANAN_DINAS"]
                },
            ],

            # Validasi berbeda per jenis
            "validasi_operasional": [
                {"field": "estimasi_biaya", "rule": "max:1000000", "message": "Belanja operasional maksimal Rp 1 juta"},
            ],
            "validasi_dengan_sk": [
                {"field": "nomor_dasar", "rule": "required", "message": "Nomor SK/Surat Tugas wajib diisi"},
                {"field": "tanggal_dasar", "rule": "required", "message": "Tanggal SK wajib diisi"},
            ],
            "validasi": [
                {"field": "estimasi_biaya", "rule": "max:50000000", "message": "Estimasi biaya UP maksimal Rp 50 juta"},
            ],
            "next_condition": "Semua dokumen wajib sudah dibuat dan SK sudah ditandatangani"
        },

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
                    "deskripsi": "Kuitansi penerimaan uang muka"
                },
            ],
            "validasi": [
                {"field": "uang_muka", "rule": "required", "message": "Jumlah uang muka wajib diisi"},
                {"field": "penerima_nama", "rule": "required", "message": "Nama penerima wajib diisi"},
            ],
            "catatan": "Uang muka untuk keperluan kegiatan",
            "next_condition": "Uang muka sudah dicairkan dan diterima penerima"
        },

        3: {
            "nama": "Pelaksanaan Kegiatan",
            "deskripsi": "Kegiatan dilaksanakan dan bukti dikumpulkan",
            "icon": "activity",
            "color": "#9b59b6",

            # Dokumen WAJIB untuk SEMUA jenis kegiatan (termasuk operasional)
            "dokumen": [
                {
                    "kode": "DOK_FOTO",
                    "nama": "Dokumentasi Foto (Tagging)",
                    "kategori": "wajib",
                    "template": None,
                    "deskripsi": "Foto dokumentasi pelaksanaan dengan tagging lokasi/waktu"
                },
                {
                    "kode": "NOTA_BLJ",
                    "nama": "Nota/Faktur Belanja",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Nota pembelian dari toko/penyedia"
                },
                {
                    "kode": "KWIT_TOKO",
                    "nama": "Kwitansi Toko",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Kwitansi pembayaran dari toko"
                },
            ],

            # Dokumen tambahan untuk KEPANITIAAN (perlu laporan kegiatan)
            "dokumen_kepanitiaan": [
                {
                    "kode": "LAP_KEG",
                    "nama": "Laporan Kegiatan",
                    "kategori": "wajib",
                    "template": "laporan_kegiatan.docx",
                    "deskripsi": "Laporan pelaksanaan kegiatan kepanitiaan",
                    "jenis_kegiatan": ["KEPANITIAAN"]
                },
            ],

            # Dokumen tambahan untuk RAPAT dan JAMUAN_TAMU (perlu daftar hadir dan notulensi)
            "dokumen_rapat_jamuan": [
                {
                    "kode": "DH",
                    "nama": "Daftar Hadir",
                    "kategori": "wajib",
                    "template": "daftar_hadir_swakelola.docx",
                    "deskripsi": "Daftar hadir peserta rapat/jamuan",
                    "jenis_kegiatan": ["RAPAT", "JAMUAN_TAMU"]
                },
                {
                    "kode": "NOTULEN",
                    "nama": "Notulensi Rapat",
                    "kategori": "wajib",
                    "template": "notulen.docx",
                    "deskripsi": "Notulen/catatan hasil rapat",
                    "jenis_kegiatan": ["RAPAT", "JAMUAN_TAMU"]
                },
            ],

            # Dokumen tambahan untuk kegiatan lainnya (opsional)
            "dokumen_lainnya": [
                {
                    "kode": "DH",
                    "nama": "Daftar Hadir",
                    "kategori": "opsional",
                    "template": "daftar_hadir_swakelola.docx",
                    "deskripsi": "Daftar hadir (jika ada peserta)",
                    "jenis_kegiatan": ["LAINNYA", "PERJALANAN_LOKAL"]
                },
                {
                    "kode": "LAP_KEG",
                    "nama": "Laporan Kegiatan",
                    "kategori": "opsional",
                    "template": "laporan_kegiatan.docx",
                    "deskripsi": "Laporan pelaksanaan kegiatan",
                    "jenis_kegiatan": ["LAINNYA", "PERJALANAN_LOKAL"]
                },
            ],

            # Validasi berbeda per jenis kegiatan
            "validasi": [
                {"field": "dokumen_foto", "rule": "required", "message": "Dokumentasi foto wajib ada"},
            ],
            "validasi_rapat_jamuan": [
                {"field": "dokumen_dh", "rule": "required", "message": "Daftar hadir wajib ada"},
                {"field": "dokumen_notulen", "rule": "required", "message": "Notulensi rapat wajib ada"},
            ],
            "validasi_kepanitiaan": [
                {"field": "dokumen_lap_keg", "rule": "required", "message": "Laporan kegiatan wajib ada"},
            ],
            "next_condition": "Kegiatan selesai dan semua bukti terkumpul"
        },

        4: {
            "nama": "Pertanggungjawaban",
            "deskripsi": "Membuat dokumen pertanggungjawaban dan perhitungan tambah/kurang",
            "icon": "calculator",
            "color": "#e74c3c",
            "dokumen": [
                {
                    "kode": "REKAP_BKT",
                    "nama": "Rekap Bukti Pengeluaran",
                    "kategori": "wajib",
                    "template": "rekap_bukti_pengeluaran.docx",
                    "deskripsi": "Rekap seluruh bukti pengeluaran"
                },
                {
                    "kode": "KUIT_RAMP",
                    "nama": "Kuitansi Rampung",
                    "kategori": "wajib",
                    "template": "kuitansi_rampung.docx",
                    "deskripsi": "Kuitansi penyelesaian/rampung kegiatan"
                },
                {
                    "kode": "LPJ",
                    "nama": "LPJ Kegiatan",
                    "kategori": "opsional",
                    "template": "lpj.docx",
                    "deskripsi": "Laporan Pertanggungjawaban kegiatan"
                },
            ],
            "kalkulasi": {
                "formula": "selisih = realisasi - uang_muka",
                "hasil_positif": {
                    "label": "KURANG BAYAR",
                    "aksi": "Ajukan pembayaran tambahan",
                    "color": "#e74c3c",
                    "icon": "arrow-up"
                },
                "hasil_negatif": {
                    "label": "LEBIH BAYAR",
                    "aksi": "Kembalikan kelebihan ke kas",
                    "color": "#f39c12",
                    "icon": "arrow-down"
                },
                "hasil_nol": {
                    "label": "PAS / NIHIL",
                    "aksi": "Lanjut ke SPBY",
                    "color": "#27ae60",
                    "icon": "check"
                },
            },
            "validasi": [
                {"field": "realisasi", "rule": "required", "message": "Total realisasi wajib diisi"},
                {"field": "dokumen_kuit_ramp", "rule": "required", "message": "Kuitansi rampung wajib dibuat"},
            ],
            "next_condition": "Perhitungan selesai dan dokumen pertanggungjawaban lengkap"
        },

        5: {
            "nama": "Penyelesaian & Arsip",
            "deskripsi": "Penyelesaian dan pengarsipan dokumen final",
            "icon": "check-circle",
            "color": "#27ae60",
            "dokumen": [
                {
                    "kode": "SPR",
                    "nama": "Surat Pendebitan Rekening",
                    "kategori": "opsional",
                    "template": "spr.docx",
                    "deskripsi": "Surat pendebitan rekening untuk penarikan tunai via teller bank"
                },
                {
                    "kode": "SPPR",
                    "nama": "Surat Perintah Pendebitan Rekening",
                    "kategori": "opsional",
                    "template": "sppr.docx",
                    "deskripsi": "Surat perintah pendebitan rekening menggunakan Kartu Debit"
                },
                {
                    "kode": "REKAP_FINAL",
                    "nama": "Rekap Final Transaksi",
                    "kategori": "opsional",
                    "template": "rekap_final.xlsx",
                    "deskripsi": "Rekap akhir seluruh transaksi"
                },
            ],
            "aksi_tambahan": [
                "Upload ke SAKTI/Aplikasi Keuangan",
                "Arsip ke folder tahun berjalan",
                "Update sisa UP tersedia",
            ],
            "validasi": [],
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
    "color": "#f39c12",  # Orange
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
            "syarat": [
                "UP yang ada tidak mencukupi",
                "Kebutuhan mendesak dan tidak dapat ditunda",
                "Rincian penggunaan jelas dan terukur",
            ],
            "validasi": [
                {"field": "estimasi_biaya", "rule": "required", "message": "Nilai TUP yang diajukan wajib diisi"},
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
            "catatan": "Proses persetujuan biasanya 1-3 hari kerja",
            "validasi": [
                {"field": "dokumen_appr_tup", "rule": "required", "message": "Surat persetujuan dari KPPN wajib ada"},
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
                {
                    "kode": "BST_UM_TUP",
                    "nama": "Bukti Serah Terima Uang TUP",
                    "kategori": "wajib",
                    "template": "bukti_serah_terima_um.docx",
                    "deskripsi": "Berita acara serah terima uang muka TUP"
                },
            ],
            "validasi": [
                {"field": "dokumen_sp2d_tup", "rule": "required", "message": "SP2D TUP wajib ada"},
                {"field": "dokumen_kuit_um_tup", "rule": "required", "message": "Kuitansi uang muka TUP wajib ada"},
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
            "validasi": [
                {"field": "penggunaan", "rule": "sesuai_rincian", "message": "Penggunaan harus sesuai rincian yang diajukan"},
            ],
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
                    "kode": "SPBY_TUP",
                    "nama": "SPBY TUP",
                    "kategori": "wajib",
                    "template": "spby_tup.docx",
                    "deskripsi": "SPBY untuk TUP"
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
                {
                    "kode": "BUKTI_SETOR",
                    "nama": "Bukti Setor Pengembalian",
                    "kategori": "kondisional",
                    "template": None,
                    "deskripsi": "Bukti setoran pengembalian sisa TUP"
                },
            ],
            "kalkulasi": {
                "formula": "sisa = nilai_tup - total_penggunaan",
                "jika_sisa": "Wajib setor kembali ke kas negara via SSBP",
            },
            "validasi": [
                {"field": "dokumen_kuit_ramp_tup", "rule": "required", "message": "Kuitansi rampung TUP wajib dibuat"},
                {"field": "dokumen_spby_tup", "rule": "required", "message": "SPBY TUP wajib dibuat"},
                {"field": "sisa_tup", "rule": "dikembalikan", "message": "Sisa TUP wajib disetor kembali"},
            ],
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
    "deskripsi": "Pembayaran langsung ke penyedia via KPPN untuk kontrak/SPK atau Surat Tugas",
    "icon": "send",
    "color": "#3498db",  # Blue
    "color_light": "#ebf5fb",

    # LS mendukung 2 mode: KONTRAK atau SURAT_TUGAS
    "jenis_dasar_options": ["KONTRAK", "SURAT_TUGAS"],
    "jenis_dasar_labels": {
        "KONTRAK": "Kontrak/SPK (Pengadaan Barang/Jasa)",
        "SURAT_TUGAS": "Surat Tugas (Perjalanan Dinas, dll)"
    },

    "fase": {
        1: {
            "nama": "Dasar Hukum",
            "deskripsi": "Pembuatan dasar hukum (Kontrak/SPK atau Surat Tugas)",
            "icon": "file-signature",
            "color": "#3498db",

            # Dokumen khusus KONTRAK (ditampilkan jika jenis_dasar == KONTRAK)
            "dokumen_kontrak": [
                {
                    "kode": "LBR_REQ",
                    "nama": "Lembar Permintaan",
                    "kategori": "wajib",
                    "template": "lembar_permintaan.docx",
                    "deskripsi": "Lembar permintaan pencairan dana",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "SPK",
                    "nama": "Surat Perjanjian Kerja",
                    "kategori": "wajib",
                    "template": "spk.docx",
                    "deskripsi": "Kontrak kerja dengan penyedia",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "SSUK",
                    "nama": "Syarat-Syarat Umum Kontrak",
                    "kategori": "wajib",
                    "template": "ssuk.docx",
                    "deskripsi": "Syarat umum kontrak",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "SSKK",
                    "nama": "Syarat-Syarat Khusus Kontrak",
                    "kategori": "wajib",
                    "template": "sskk.docx",
                    "deskripsi": "Syarat khusus kontrak",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "SPMK",
                    "nama": "Surat Perintah Mulai Kerja",
                    "kategori": "wajib",
                    "template": "spmk.docx",
                    "deskripsi": "Perintah untuk memulai pekerjaan",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "JAM_PELAKS",
                    "nama": "Jaminan Pelaksanaan",
                    "kategori": "kondisional",
                    "template": None,
                    "deskripsi": "Jaminan pelaksanaan dari bank/asuransi",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "JAM_UM",
                    "nama": "Jaminan Uang Muka (jika ada UM kontrak)",
                    "kategori": "kondisional",
                    "template": None,
                    "deskripsi": "Jaminan uang muka kontrak",
                    "jenis_dasar": "KONTRAK"
                },
            ],

            # Dokumen khusus SURAT_TUGAS (Perjalanan Dinas)
            "dokumen_surat_tugas": [
                {
                    "kode": "ST",
                    "nama": "Surat Tugas",
                    "kategori": "wajib",
                    "template": "surat_tugas.docx",
                    "deskripsi": "Surat Tugas dari pejabat berwenang",
                    "jenis_dasar": "SURAT_TUGAS"
                },
                {
                    "kode": "SPD",
                    "nama": "Surat Perjalanan Dinas (SPPD)",
                    "kategori": "wajib",
                    "template": "sppd.docx",
                    "deskripsi": "Surat Perjalanan Dinas",
                    "jenis_dasar": "SURAT_TUGAS"
                },
                {
                    "kode": "RINCIAN_PD",
                    "nama": "Rincian Biaya Perjalanan Dinas",
                    "kategori": "wajib",
                    "template": "rincian_biaya_pd.docx",
                    "deskripsi": "Rincian anggaran biaya perjalanan dinas",
                    "jenis_dasar": "SURAT_TUGAS"
                },
            ],

            # Validasi berbeda per jenis
            "validasi_kontrak": [
                {"field": "nomor_kontrak", "rule": "required", "message": "Nomor kontrak/SPK wajib diisi"},
                {"field": "nilai_kontrak", "rule": "required", "message": "Nilai kontrak wajib diisi"},
                {"field": "penyedia_id", "rule": "required", "message": "Penyedia wajib dipilih"},
            ],
            "validasi_surat_tugas": [
                {"field": "nomor_st", "rule": "required", "message": "Nomor Surat Tugas wajib diisi"},
                {"field": "tanggal_st", "rule": "required", "message": "Tanggal Surat Tugas wajib diisi"},
                {"field": "tujuan_perjalanan", "rule": "required", "message": "Tujuan perjalanan wajib diisi"},
            ],
            "next_condition": "Dasar hukum sudah ditandatangani"
        },

        2: {
            "nama": "Pelaksanaan",
            "deskripsi": "Pelaksanaan pekerjaan/kegiatan sesuai dasar hukum",
            "icon": "hard-hat",
            "color": "#f39c12",

            # Dokumen untuk mode KONTRAK
            "dokumen_kontrak": [
                {
                    "kode": "LAP_PROG",
                    "nama": "Laporan Progress Pekerjaan",
                    "kategori": "wajib",
                    "template": "laporan_kemajuan.docx",
                    "deskripsi": "Laporan kemajuan pekerjaan",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "BA_MC",
                    "nama": "BA Monthly Certificate (jika termin)",
                    "kategori": "kondisional",
                    "template": "ba_mc.docx",
                    "deskripsi": "Berita acara progress bulanan",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "MONEV",
                    "nama": "Laporan Monitoring & Evaluasi",
                    "kategori": "opsional",
                    "template": "monev.docx",
                    "deskripsi": "Laporan monev pekerjaan",
                    "jenis_dasar": "KONTRAK"
                },
            ],

            # Dokumen untuk mode SURAT_TUGAS (Perjalanan Dinas)
            "dokumen_surat_tugas": [
                {
                    "kode": "DH_PJD",
                    "nama": "Daftar Hadir / Bukti Kehadiran",
                    "kategori": "wajib",
                    "template": "daftar_hadir_swakelola.docx",
                    "deskripsi": "Daftar hadir atau bukti kehadiran di lokasi tujuan",
                    "jenis_dasar": "SURAT_TUGAS"
                },
                {
                    "kode": "DOK_FOTO_PJD",
                    "nama": "Dokumentasi Foto Kegiatan",
                    "kategori": "wajib",
                    "template": None,
                    "deskripsi": "Foto dokumentasi pelaksanaan kegiatan perjalanan",
                    "jenis_dasar": "SURAT_TUGAS"
                },
                {
                    "kode": "TIKET",
                    "nama": "Tiket/Boarding Pass",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Tiket pesawat/kereta/kapal atau boarding pass",
                    "jenis_dasar": "SURAT_TUGAS"
                },
                {
                    "kode": "BUKTI_HOTEL",
                    "nama": "Bukti Penginapan/Hotel",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Bill/invoice dari hotel atau penginapan",
                    "jenis_dasar": "SURAT_TUGAS"
                },
            ],

            "validasi_kontrak": [
                {"field": "progress", "rule": "updated", "message": "Progress pekerjaan harus di-update"},
            ],
            "validasi_surat_tugas": [
                {"field": "tanggal_berangkat", "rule": "required", "message": "Tanggal berangkat wajib diisi"},
                {"field": "tanggal_kembali", "rule": "required", "message": "Tanggal kembali wajib diisi"},
            ],
            "next_condition": "Pekerjaan/kegiatan selesai dilaksanakan"
        },

        3: {
            "nama": "Serah Terima / Laporan",
            "deskripsi": "Pemeriksaan dan serah terima hasil pekerjaan atau laporan kegiatan",
            "icon": "handshake",
            "color": "#9b59b6",

            # Dokumen untuk mode KONTRAK
            "dokumen_kontrak": [
                {
                    "kode": "BA_PMR",
                    "nama": "BA Pemeriksaan Pekerjaan",
                    "kategori": "wajib",
                    "template": "bahp.docx",
                    "deskripsi": "Berita acara pemeriksaan oleh PPHP",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "BAST",
                    "nama": "Berita Acara Serah Terima",
                    "kategori": "wajib",
                    "template": "bast.docx",
                    "deskripsi": "BAST hasil pekerjaan",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "BA_PHO",
                    "nama": "BA Provisional Hand Over (PHO)",
                    "kategori": "kondisional",
                    "template": "bast_konstruksi_pho.docx",
                    "deskripsi": "Serah terima sementara",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "BA_FHO",
                    "nama": "BA Final Hand Over (konstruksi)",
                    "kategori": "kondisional",
                    "template": "bast_konstruksi_fho.docx",
                    "deskripsi": "Serah terima akhir untuk konstruksi",
                    "jenis_dasar": "KONTRAK"
                },
            ],

            # Dokumen untuk mode SURAT_TUGAS (Perjalanan Dinas)
            "dokumen_surat_tugas": [
                {
                    "kode": "LAP_PJD",
                    "nama": "Laporan Perjalanan Dinas",
                    "kategori": "wajib",
                    "template": "laporan_perjalanan_dinas.docx",
                    "deskripsi": "Laporan hasil perjalanan dinas",
                    "jenis_dasar": "SURAT_TUGAS"
                },
                {
                    "kode": "SPD_TTD",
                    "nama": "SPD yang Sudah Ditandatangani",
                    "kategori": "wajib",
                    "template": None,
                    "deskripsi": "SPD dengan tanda tangan pejabat di lokasi tujuan",
                    "jenis_dasar": "SURAT_TUGAS"
                },
            ],

            "validasi_kontrak": [
                {"field": "dokumen_bast", "rule": "required", "message": "BAST wajib dibuat"},
                {"field": "dokumen_bast", "rule": "signed", "message": "BAST wajib ditandatangani kedua pihak"},
            ],
            "validasi_surat_tugas": [
                {"field": "dokumen_lap_pjd", "rule": "required", "message": "Laporan perjalanan dinas wajib dibuat"},
                {"field": "dokumen_spd_ttd", "rule": "required", "message": "SPD yang ditandatangani wajib ada"},
            ],
            "next_condition": "Serah terima/laporan selesai"
        },

        4: {
            "nama": "Pengajuan Tagihan SPM",
            "deskripsi": "Pemrosesan dokumen SPP/SPM untuk pembayaran",
            "icon": "file-invoice-dollar",
            "color": "#e74c3c",

            # Dokumen umum untuk semua jenis
            "dokumen": [
                {
                    "kode": "SPP_LS",
                    "nama": "Surat Permintaan Pembayaran",
                    "kategori": "wajib",
                    "template": "spp_ls.docx",
                    "deskripsi": "SPP untuk pengajuan ke PPSPM"
                },
                {
                    "kode": "SPM_LS",
                    "nama": "Surat Perintah Membayar",
                    "kategori": "wajib",
                    "template": "spm_ls.docx",
                    "deskripsi": "SPM untuk dikirim ke KPPN"
                },
                {
                    "kode": "KUIT_LS",
                    "nama": "Kuitansi Pembayaran LS",
                    "kategori": "wajib",
                    "template": "kuitansi.docx",
                    "deskripsi": "Kuitansi pembayaran LS"
                },
            ],

            # Dokumen khusus KONTRAK
            "dokumen_kontrak": [
                {
                    "kode": "INVOICE",
                    "nama": "Invoice/Tagihan dari Penyedia",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Tagihan resmi dari penyedia",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "FAKTUR_PJK",
                    "nama": "Faktur Pajak",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Faktur pajak dari PKP",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "SSP_PPN",
                    "nama": "SSP PPN",
                    "kategori": "wajib",
                    "template": "ssp.xlsx",
                    "deskripsi": "Surat Setoran Pajak PPN",
                    "jenis_dasar": "KONTRAK"
                },
                {
                    "kode": "SSP_PPH",
                    "nama": "SSP PPh",
                    "kategori": "wajib",
                    "template": "ssp.xlsx",
                    "deskripsi": "Surat Setoran Pajak PPh",
                    "jenis_dasar": "KONTRAK"
                },
            ],

            # Dokumen khusus SURAT_TUGAS (Perjalanan Dinas)
            "dokumen_surat_tugas": [
                {
                    "kode": "RINCIAN_BIAYA",
                    "nama": "Rincian Biaya Perjalanan",
                    "kategori": "wajib",
                    "template": "rincian_biaya_pd.docx",
                    "deskripsi": "Rincian biaya perjalanan dinas yang direalisasi",
                    "jenis_dasar": "SURAT_TUGAS"
                },
                {
                    "kode": "BUKTI_BAYAR_PJD",
                    "nama": "Bukti-bukti Pembayaran",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Bukti pembayaran (tiket, hotel, transport lokal)",
                    "jenis_dasar": "SURAT_TUGAS"
                },
            ],

            "kelengkapan_kontrak": [
                "Resume Kontrak",
                "Ringkasan Kontrak",
                "Copy SPK",
                "Copy BAST",
                "Faktur Pajak",
                "NPWP Penyedia",
                "Copy Rekening Penyedia",
            ],
            "kelengkapan_surat_tugas": [
                "Copy Surat Tugas",
                "Copy SPD yang ditandatangani",
                "Laporan Perjalanan Dinas",
                "Bukti-bukti pengeluaran",
            ],
            "validasi": [
                {"field": "dokumen_spm", "rule": "required", "message": "SPM wajib dibuat"},
            ],
            "validasi_kontrak": [
                {"field": "pajak", "rule": "calculated", "message": "Pajak wajib dihitung"},
            ],
            "next_condition": "SPM diajukan ke KPPN"
        },

        5: {
            "nama": "SP2D & Penyelesaian",
            "deskripsi": "KPPN menerbitkan SP2D, dana masuk ke rekening penyedia",
            "icon": "check-circle",
            "color": "#27ae60",
            "dokumen": [
                {
                    "kode": "SP2D_LS",
                    "nama": "Surat Perintah Pencairan Dana",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "SP2D dari KPPN"
                },
                {
                    "kode": "BUKTI_TRF",
                    "nama": "Bukti Transfer ke Penyedia",
                    "kategori": "upload",
                    "template": None,
                    "deskripsi": "Bukti transfer pembayaran"
                },
            ],
            "aksi_tambahan": [
                "Verifikasi dana sudah diterima penyedia",
                "Update status kontrak menjadi SELESAI",
                "Arsip seluruh dokumen",
                "Update realisasi anggaran di DIPA",
            ],
            "validasi": [
                {"field": "dokumen_sp2d", "rule": "required", "message": "SP2D wajib ada"},
                {"field": "pembayaran", "rule": "confirmed", "message": "Pembayaran wajib dikonfirmasi penyedia"},
            ],
            "next_condition": "Transaksi selesai dan pembayaran diterima penyedia"
        }
    }
}

# ============================================================================
# EXPORT & HELPER FUNCTIONS
# ============================================================================

# Export semua workflow
ALL_WORKFLOWS = {
    "UP": UP_WORKFLOW,
    "TUP": TUP_WORKFLOW,
    "LS": LS_WORKFLOW,
}

def get_workflow(mekanisme: str) -> Optional[Dict[str, Any]]:
    """
    Get konfigurasi workflow berdasarkan mekanisme.

    Args:
        mekanisme: Kode mekanisme (UP, TUP, LS)

    Returns:
        Dictionary konfigurasi workflow atau None
    """
    return ALL_WORKFLOWS.get(mekanisme.upper())


def get_fase_config(mekanisme: str, fase: int) -> Optional[Dict[str, Any]]:
    """
    Get konfigurasi fase tertentu.

    Args:
        mekanisme: Kode mekanisme (UP, TUP, LS)
        fase: Nomor fase (1-5)

    Returns:
        Dictionary konfigurasi fase atau None
    """
    workflow = get_workflow(mekanisme)
    if workflow and fase in workflow.get("fase", {}):
        return workflow["fase"][fase]
    return None


def get_dokumen_list(mekanisme: str, fase: int) -> List[Dict[str, Any]]:
    """
    Get daftar dokumen untuk fase tertentu.

    Args:
        mekanisme: Kode mekanisme
        fase: Nomor fase

    Returns:
        List dokumen untuk fase tersebut
    """
    fase_config = get_fase_config(mekanisme, fase)
    if fase_config:
        return fase_config.get("dokumen", [])
    return []


def get_all_dokumen(mekanisme: str) -> List[Dict[str, Any]]:
    """
    Get semua dokumen untuk mekanisme tertentu.

    Returns:
        List semua dokumen dengan informasi fase
    """
    workflow = get_workflow(mekanisme)
    if not workflow:
        return []

    dokumen_list = []
    for fase_num, fase_config in workflow.get("fase", {}).items():
        for dok in fase_config.get("dokumen", []):
            dok_copy = dok.copy()
            dok_copy["fase"] = fase_num
            dok_copy["fase_nama"] = fase_config.get("nama", "")
            dokumen_list.append(dok_copy)

    return dokumen_list


def get_validasi_rules(mekanisme: str, fase: int) -> List[Dict[str, str]]:
    """
    Get aturan validasi untuk fase tertentu.

    Returns:
        List aturan validasi
    """
    fase_config = get_fase_config(mekanisme, fase)
    if fase_config:
        return fase_config.get("validasi", [])
    return []


def get_workflow_summary(mekanisme: str) -> Dict[str, Any]:
    """
    Get ringkasan workflow untuk display.

    Returns:
        Dictionary dengan informasi ringkas workflow
    """
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
            "dokumen_wajib": len([d for d in fase_config.get("dokumen", []) if d.get("kategori") == "wajib"]),
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
        1: "Inisiasi & SK",
        2: "Pencairan UM",
        3: "Pelaksanaan",
        4: "Pertanggungjawaban",
        5: "Selesai & Arsip"
    },
    "TUP": {
        1: "Pengajuan TUP",
        2: "Persetujuan",
        3: "Pencairan",
        4: "Penggunaan",
        5: "Pertanggungjawaban"
    },
    "LS": {
        1: "Kontrak/SPK",
        2: "Pelaksanaan",
        3: "Serah Terima",
        4: "Tagihan SPM",
        5: "SP2D & Selesai"
    }
}


def get_nama_fase(mekanisme: str, fase: int) -> str:
    """Get nama singkat fase untuk display."""
    return NAMA_FASE.get(mekanisme, {}).get(fase, f"Fase {fase}")
